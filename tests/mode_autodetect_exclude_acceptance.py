"""tests/mode_autodetect_exclude_acceptance.py — WS5 acceptance: the auto-detect EXCLUDE-LIST.

The auto-detector (detect_mode_candidate → propose_mode → autodetect_mode, all already built) honours an
off/suggest/auto toggle. WS5 adds an EXCLUDE-LIST: mode ids the detector must NEVER suggest OR switch to
(gates BOTH suggest+auto — the conservative scope). MANUAL set_mode is NEVER gated — an excluded mode can
always be chosen by hand. Default is empty (nothing excluded; backward-compatible). The list is
runtime-settable + persisted (set_rhm_config, validated against MODES, fail loud).

Run: `python3 tests/mode_autodetect_exclude_acceptance.py`  (exit 0 = all green).

Covers:
  T1  default exclude-list is empty → auto-detect behaves exactly as pre-WS5.
  T2  an excluded candidate is GATED under toggle='auto' (action 'excluded', NOT switched) AND under
        'suggest' (not suggested) — both, the conservative scope.
  T3  MANUAL set_mode to an excluded mode STILL works (the list only constrains auto-detect).
  T4  set_rhm_config persists the list + FAILS LOUD on an unknown mode id.
  T5  capabilities() exposes MODE_AUTODETECT_EXCLUDE (the surface can render + set it).
  T6  the list SURVIVES a reload (a fresh Suite on the same store re-resolves it — X17 persistence).
"""
import os
import sys
import tempfile
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "ops", "cli"))

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not cond else ""))


os.environ["COMPANY_CAP_LOAD_FROM_LEDGER"] = "0"
os.environ.pop("COMPANY_MODE_AUTODETECT_EXCLUDE", None)

from runtime.suite import Suite
from runtime.registry import NodeRegistry
from store.fs_store import FsStore

NODES = os.path.join(ROOT, "nodes")
store_dir = tempfile.mkdtemp(prefix="mode-exclude-test-")
exit_code = 1
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # ── T1 — default empty ───────────────────────────────────────────────────────────────────────────
    print("\n[T1] default exclude-list is empty (backward-compatible)")
    ok("T1a MODE_AUTODETECT_EXCLUDE empty by default", suite.MODE_AUTODETECT_EXCLUDE == frozenset(),
       f"got {set(suite.MODE_AUTODETECT_EXCLUDE)}")
    suite.set_rhm_config({"MODE_AUTODETECT": "auto"})
    r = suite.autodetect_mode("focus")     # not excluded → auto switches
    ok("T1b non-excluded candidate auto-switches", r["action"] == "switched" and suite.get_mode() == "focus", f"{r}")

    # ── T2 — excluded candidate gated under BOTH auto and suggest ─────────────────────────────────────
    print("\n[T2] an excluded candidate is gated under auto AND suggest (conservative scope)")
    suite.set_mode("listening")            # known starting point
    suite.set_rhm_config({"MODE_AUTODETECT_EXCLUDE": "background", "MODE_AUTODETECT": "auto"})
    r_auto = suite.autodetect_mode("background")
    ok("T2a excluded under 'auto' → action 'excluded', NOT switched",
       r_auto["action"] == "excluded" and suite.get_mode() == "listening", f"{r_auto} mode={suite.get_mode()}")
    suite.set_rhm_config({"MODE_AUTODETECT": "suggest"})
    r_sug = suite.autodetect_mode("background")
    ok("T2b excluded under 'suggest' → action 'excluded', not suggested", r_sug["action"] == "excluded", f"{r_sug}")
    # a NON-excluded candidate still flows under suggest
    r_ok = suite.autodetect_mode("focus")
    ok("T2c non-excluded candidate still suggested", r_ok["action"] == "suggested", f"{r_ok}")

    # ── T3 — manual set_mode to an excluded mode still works ──────────────────────────────────────────
    print("\n[T3] MANUAL set_mode to an excluded mode is NEVER gated")
    suite.set_mode("background")
    ok("T3a manual set_mode('background') works despite exclusion", suite.get_mode() == "background")

    # ── T4 — set_rhm_config validates + persists ──────────────────────────────────────────────────────
    print("\n[T4] set_rhm_config persists the list + fails loud on an unknown mode")
    suite.set_rhm_config({"MODE_AUTODETECT_EXCLUDE": "focus, off"})
    ok("T4a comma-list parsed to a frozenset", suite.MODE_AUTODETECT_EXCLUDE == frozenset({"focus", "off"}),
       f"got {set(suite.MODE_AUTODETECT_EXCLUDE)}")
    try:
        suite.set_rhm_config({"MODE_AUTODETECT_EXCLUDE": "not-a-mode"})
        ok("T4b unknown mode RAISES", False, "did not raise")
    except ValueError as e:
        ok("T4b unknown mode RAISES", "unknown mode" in str(e), f"msg={str(e)[:120]!r}")

    # ── T5 — capabilities exposure ────────────────────────────────────────────────────────────────────
    print("\n[T5] capabilities() exposes the exclude-list")
    cc = suite.capabilities().get("composition_config", {})
    ok("T5a MODE_AUTODETECT_EXCLUDE present in composition_config",
       "MODE_AUTODETECT_EXCLUDE" in cc and sorted(cc["MODE_AUTODETECT_EXCLUDE"]) == ["focus", "off"], f"{cc.get('MODE_AUTODETECT_EXCLUDE')}")

    # ── T6 — survives a reload ────────────────────────────────────────────────────────────────────────
    print("\n[T6] the list survives a reload (fresh Suite, same store)")
    suite2 = Suite(FsStore(os.path.join(store_dir, "store")), reg, nodes_dir=NODES)
    ok("T6a fresh Suite re-resolves the persisted exclude-list",
       suite2.MODE_AUTODETECT_EXCLUDE == frozenset({"focus", "off"}), f"got {set(suite2.MODE_AUTODETECT_EXCLUDE)}")

    print(f"\n[RESULT] {len(PASS)} pass / {len(FAIL)} fail")
    exit_code = 1 if FAIL else 0
    if FAIL:
        print("FAILED: " + ", ".join(FAIL))
finally:
    shutil.rmtree(store_dir, ignore_errors=True)

sys.exit(exit_code)
