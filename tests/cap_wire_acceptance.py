"""tests/cap_wire_acceptance.py — LANE-CAP-WIRE acceptance (Mirror-Registry System, Stage 2).

The #1 unblock: makes the Mirror-Registry have PRODUCTION EFFECT. Verifies the cap:// address scheme
resolves end-to-end through the REAL resolve_address dispatcher (runtime/cognition.py) against a
CapabilityRegistry that Suite.__init__ installed via the cached module-level singleton
(introspection.registry — F-FIX-1 / PG-D2).

VERIFY-BY-USE, NO live claude. The registry is populated through a STUB discover_fn (no `claude`
subprocess, no `system/init` spawn) — the live-binary-populated path (CapabilityRegistry.discover()
spawns the binary) is 🟡 LEAD-verify queued (C-WIRE-1/2/3 in the build plan). Every cap:// fact below
is unit-verified against the real dispatch path; nothing is monkeypatched in cognition.py itself.

Run: `python3 tests/cap_wire_acceptance.py`  (exit 0 = all green; non-zero = a FAIL line printed).

Covers:
  T1 IMPORT-CLEAN (PG-D6)  `import runtime.suite` then `import runtime.cognition` succeeds with NO
        import cycle and NO binary spawn at import time. introspection never imports runtime/, so
        runtime→introspection is the only edge; the supervisor head-builder platforms/claude_code.py
        registers does NOT import Suite. (The cap:// resolver's introspection import is LAZY, inside
        the branch — proven by a fresh interpreter import in T1b.)
  T2 WIRED-AT-INIT  a freshly-constructed Suite installs `capability_registry` (the singleton accessor
        returns the SAME object) and resolves the 'claude-code' PlatformEntry — WITHOUT spawning the
        binary (default COMPANY_CAP_DISCOVER_AT_INIT unset → empty registry, discovered=False).
  T3 EMPTY-IS-FAILLOUD  before any discovery, cap://flag/--debug RAISES "unknown capability" through
        resolve_address — registry-is-truth: empty surface fails loud, NEVER fabricates a row.
  T4 RESOLVE-STUB-ENTRY  after stub-populating via suite.discover_capabilities(discover_fn=stub),
        cognition.resolve_address(store, "cap://flag/--debug") returns the CapabilityEntry END-TO-END
        through the real dispatcher (reached via the singleton, not the store — the P7 decision).
  T5 UNKNOWN-FAILS-LOUD  cap://flag/--nonexistent RAISES the registry-is-truth fail-loud message
        (parity with session:// for an unknown id) — never a silent None/empty.
  T6 INTROSPECTION-KEY  capabilities()['introspection'] reflects the populated registry (discovered=True,
        counts_by_kind, total) — the projection face reads the SAME one registry.
"""
import os
import sys
import tempfile
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not cond else ""))


# ── T1 — IMPORT-CLEAN (PG-D6: no cycle, no spawn-at-import) ─────────────────────────────────────
print("\n[T1] import-clean (PG-D6 circularity + no binary spawn at import)")
try:
    import runtime.suite as _suite_mod          # noqa: F401
    import runtime.cognition as cognition
    from runtime.suite import Suite
    ok("T1 import runtime.suite + runtime.cognition (no cycle)", True)
except Exception as e:                            # pragma: no cover — a cycle/spawn would land here
    ok("T1 import runtime.suite + runtime.cognition (no cycle)", False, f"{type(e).__name__}: {e}")
    print("\n[RESULT] FAIL — import broke; cannot continue.")
    sys.exit(1)

# T1b — a FRESH interpreter imports the chain (proves no module-load side-effect spawns a process,
# and that the cap:// branch's introspection import is lazy — importing cognition must NOT import
# introspection.registry at module load).
_probe = (
    "import sys; sys.path.insert(0, %r);"
    "import runtime.cognition;"
    "assert 'introspection.registry' not in sys.modules, "
    "'cognition module-load must NOT import introspection.registry (cap:// import is lazy)';"
    "import contracts.address as a; assert 'cap' in a.SCHEMES;"
    "print('OK')" % ROOT
)
_r = subprocess.run([sys.executable, "-c", _probe], capture_output=True, text=True, timeout=60)
ok("T1b fresh-import: cap:// import is lazy (introspection not loaded by importing cognition)",
   _r.returncode == 0 and _r.stdout.strip() == "OK",
   f"rc={_r.returncode} out={_r.stdout.strip()!r} err={_r.stderr.strip()[-300:]!r}")

from contracts.capability_entry import CapabilityEntry
from introspection.registry import capability_registry, set_capability_registry, CapabilityRegistry

# ── build a Suite against a temp store (no live discovery — default env) ─────────────────────────
from store.fs_store import FsStore
from runtime.registry import NodeRegistry

NODES = os.path.join(ROOT, "nodes")
store_dir = tempfile.mkdtemp(prefix="cap-wire-test-")
exit_code = 1
try:
    # Ensure the opt-in init discovery is OFF (the default) so Suite construction does NOT spawn claude.
    os.environ.pop("COMPANY_CAP_DISCOVER_AT_INIT", None)
    # Isolate the cap-wire MECHANISM under test: turn OFF the ledger-backed auto-load (2026-06-28 — the
    # operational default that populates cap:// from the ledger spawn-free) so T2-T6 verify the
    # discover()/stub + fail-loud path against a controlled fixture set, not the live ledger's contents.
    # The ledger-backed operational path is verified separately (by real resolve_address use).
    os.environ["COMPANY_CAP_LOAD_FROM_LEDGER"] = "0"
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # ── T2 — WIRED-AT-INIT ───────────────────────────────────────────────────────────────────────
    print("\n[T2] capability_registry installed at Suite init (no spawn)")
    ok("T2a suite.capability_registry is a CapabilityRegistry",
       isinstance(getattr(suite, "capability_registry", None), CapabilityRegistry))
    ok("T2b singleton accessor returns the SAME object Suite installed",
       capability_registry() is suite.capability_registry)
    ok("T2c 'claude-code' PlatformEntry resolved (instance #1 registered)",
       getattr(suite, "capability_platform", None) is not None
       and suite.capability_platform.id == "claude-code")
    ok("T2d default: NO discovery at init → empty registry (no binary spawn)",
       len(suite.capability_registry) == 0)

    # ── T3 — EMPTY-IS-FAILLOUD ─────────────────────────────────────────────────────────────────────
    print("\n[T3] empty registry → cap:// fails loud (registry-is-truth, never fabricate)")
    try:
        cognition.resolve_address(suite.store, "cap://flag/--debug")
        ok("T3 cap://flag/--debug RAISES on an un-discovered registry", False,
           "returned a value instead of raising")
    except ValueError as e:
        ok("T3 cap://flag/--debug RAISES on an un-discovered registry",
           "unknown capability" in str(e), f"msg={str(e)[:120]!r}")

    # ── stub-populate the registry (NO live spawn) ─────────────────────────────────────────────────
    fixture_rows = [
        CapabilityEntry(id="flag/--debug", kind="flag", name="--debug"),
        CapabilityEntry(id="flag/-p", kind="flag", name="-p"),
        CapabilityEntry(id="flag/--dangerously-skip-permissions", kind="flag",
                        name="--dangerously-skip-permissions"),
        CapabilityEntry(id="flag/--some-feature", kind="flag", name="--some-feature"),
        CapabilityEntry(id="tool/Bash", kind="tool", name="Bash"),
    ]

    def stub_discover(platform, *, executable=None, version=None):
        # mirrors the live discover_fn contract (introspection.discover.discover signature) — returns
        # fixture rows, spawns NOTHING. The engine's classify runs over the REAL claude-code platform's
        # signal_sets (so postures are real), but the rows are injected, not parsed from the binary.
        return list(fixture_rows)

    suite.discover_capabilities(discover_fn=stub_discover, executable="/usr/bin/claude", version="0.0.0-test")

    # ── T4 — RESOLVE-STUB-ENTRY (end-to-end through the real dispatcher) ───────────────────────────
    print("\n[T4] cap:// resolves end-to-end through resolve_address (reached via the singleton)")
    resolved = cognition.resolve_address(suite.store, "cap://flag/--debug")
    ok("T4a resolve_address('cap://flag/--debug') returns a CapabilityEntry",
       isinstance(resolved, CapabilityEntry) and resolved.id == "flag/--debug",
       f"got {type(resolved).__name__}={getattr(resolved, 'id', None)!r}")
    resolved_tool = cognition.resolve_address(suite.store, "cap://tool/Bash")
    ok("T4b resolve_address('cap://tool/Bash') returns the tool leaf (kind-agnostic id)",
       isinstance(resolved_tool, CapabilityEntry) and resolved_tool.id == "tool/Bash")

    # ── T5 — UNKNOWN-FAILS-LOUD ────────────────────────────────────────────────────────────────────
    print("\n[T5] unknown cap:// fails loud (parity with session://)")
    try:
        cognition.resolve_address(suite.store, "cap://flag/--nonexistent")
        ok("T5 cap://flag/--nonexistent RAISES (never a silent None)", False, "returned instead of raising")
    except ValueError as e:
        ok("T5 cap://flag/--nonexistent RAISES (never a silent None)",
           "unknown capability" in str(e) and "--nonexistent" in str(e), f"msg={str(e)[:140]!r}")

    # ── T6 — INTROSPECTION-KEY (the projection face reads the SAME registry) ───────────────────────
    print("\n[T6] capabilities()['introspection'] reflects the populated registry")
    intro = suite.capabilities().get("introspection", {})
    ok("T6a introspection.discovered is True after populate", intro.get("discovered") is True, f"intro={intro}")
    ok("T6b introspection.total == 5 fixture rows", intro.get("total") == 5, f"total={intro.get('total')}")
    ok("T6c counts_by_kind has flag+tool", intro.get("counts_by_kind", {}).get("flag") == 4
       and intro.get("counts_by_kind", {}).get("tool") == 1, f"counts={intro.get('counts_by_kind')}")
    ok("T6d platform_id == claude-code", intro.get("platform_id") == "claude-code", f"intro={intro}")

    print(f"\n[RESULT] {len(PASS)} pass / {len(FAIL)} fail")
    if FAIL:
        print("FAILED: " + ", ".join(FAIL))
        exit_code = 1
    else:
        exit_code = 0
finally:
    shutil.rmtree(store_dir, ignore_errors=True)

sys.exit(exit_code)
