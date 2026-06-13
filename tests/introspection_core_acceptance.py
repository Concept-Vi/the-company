"""tests/introspection_core_acceptance.py — LANE-INTROSPECTION-CORE acceptance (Mirror-Registry System).

VERIFY-BY-USE, no live claude (LEAD-only items — CliHelp/StreamInit against the real binary — are
queued for the lead; this suite uses a STUB PlatformEntry + stub adapter so the engine + rules + the
LEAK GATE are unit-verified without a spawn). Run: `python3 tests/introspection_core_acceptance.py`.

Covers:
  THE GATE (F-FIX-10, MANDATORY) — introspection/{engine,rules}.py + adapters/ carry ZERO platform-name
    literals ([claude, claude-code, dangerously, --mcp-config, stream-json]). Any hit = the lift is
    broken → FAIL. (C-CORE-6; re-run as a gate in LANE-REFRESH.)
  C-CORE-3  CliHelpDiscoverer parse of a 5-row help → engine floor_guard(30) RAISES (fail-loud partial).
  C-CORE-4  derive_transport_invariants() over a stub _build_spawn_cmd head ∪ body_key_overrides returns
            a set INCLUDING every unconditional-head flag — NO hand-list.
  C-CORE-5  the 5 rules over a known flag set: hazard→R2, transport→R1, axis→R3, plain→R5, novel→R4.
  GENPROOF-converse  a platform selecting an UNBUILT discoverer (rest-openapi) FAILS LOUD naming the
            missing class — never a silent empty registry.
  ENGINE    discover→classify→project→refresh over a stub PlatformEntry + stub discoverer (fixture rows),
            no live spawn: postures stamped, projection counts, refresh diff + empty-diff guard.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from contracts.capability_entry import CapabilityEntry
from contracts.platform_entry import (
    PlatformEntry, ExecutableLocator, DiscoverySource, SignalSets,
    ConsumerReservedInvariants, VersionSource,
)
from introspection import rules
from introspection import engine
from introspection.adapters.cli_help import CliHelpDiscoverer
from introspection.discover import discover as run_discover, MissingAdapterError, select_discoverer

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not cond else ""))


# ── THE GATE (F-FIX-10) — ZERO platform-name literals in Level-1 code ───────────────────────────
print("\n[GATE] F-FIX-10 platform-name leak grep (engine + rules + adapters)")
BANNED = ["claude", "claude-code", "dangerously", "--mcp-config", "stream-json"]
LEVEL1_FILES = [
    os.path.join(ROOT, "introspection", "engine.py"),
    os.path.join(ROOT, "introspection", "rules.py"),
    os.path.join(ROOT, "introspection", "discover.py"),  # also Level-1; the gate covers it too
] + [
    os.path.join(ROOT, "introspection", "adapters", f)
    for f in os.listdir(os.path.join(ROOT, "introspection", "adapters"))
    if f.endswith(".py")
]
leak_hits = []
for path in LEVEL1_FILES:
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            low = line.lower()
            for tok in BANNED:
                if tok in low:
                    leak_hits.append(f"{os.path.relpath(path, ROOT)}:{n}: {tok!r} in {line.strip()[:80]!r}")
ok("GATE: ZERO platform-name literals in engine/rules/adapters", not leak_hits,
   detail=("LEAK HITS:\n    " + "\n    ".join(leak_hits)) if leak_hits else "")
for h in leak_hits:
    print(f"      LEAK: {h}")


# ── C-CORE-4 — derive_transport_invariants is REAL code, no hand-list ───────────────────────────
print("\n[C-CORE-4] derive_transport_invariants() from a stub spawn head ∪ body_key_overrides")
# Stub head_builder: a generic command list (NO claude/stream-json literals here — this is the TEST,
# Level-2; in production the platform row binds the real _build_spawn_cmd thunk). We model the SHAPE
# of the supervisor head (unconditional flags) using neutral tokens so the test itself proves the
# derivation logic, and a separate LEAD check binds the real thunk.
def stub_head_builder():
    return ["/bin/tool", "-p", "--input-format", "X", "--output-format", "Y", "--verbose",
            "--permission-mode", "Z", "--cfg", "C", "--strict-cfg", "--allow", "A"]

body_overrides = {
    "model":  {"flag": "--model",  "kind": "value"},
    "resume": {"flag": "--resume", "kind": "value"},
}
derived = rules.derive_transport_invariants(stub_head_builder, body_overrides)
head_flags = [t for t in stub_head_builder() if t.startswith("-")]
ok("C-CORE-4: every unconditional-head flag is in the derived set",
   all(f in derived for f in head_flags), detail=f"head={head_flags} derived={derived}")
ok("C-CORE-4: body_key_overrides flags joined the set",
   "--model" in derived and "--resume" in derived, detail=str(derived))
ok("C-CORE-4: result is a derivation (sorted set), not the literal input list",
   derived == sorted(set(derived)))


# ── C-CORE-5 — the five rules over a known flag set ─────────────────────────────────────────────
print("\n[C-CORE-5] the 5 closed rules R1>R2>R3>R5>R4")
ss = SignalSets(
    transport_invariants=["--input-format", "-p", "--verbose"],   # R1 input (derived in prod)
    hazard_name_vocabulary=["dangerously", "skip", "bypass", "unsafe"],
    hazard_scope="flag_name_only",
    capability_axes={"mcp": ["--cfg-server"], "tools": ["--allow-tools"]},
)
ok("C-CORE-5: R1 LOCKED — a transport invariant",
   rules.classify("-p", ss) == ("locked", "R1", ""))
ok("C-CORE-5: R2 HAZARD — hazard word in the flag NAME",
   rules.classify("--dangerously-skip-permissions", ss) == ("hazard", "R2", ""))
ok("C-CORE-5: R3 CONSENT — flag in a capability axis (axis recorded)",
   rules.classify("--cfg-server", ss) == ("consent", "R3", "mcp"))
ok("C-CORE-5: R5 SAFE — the expose default",
   rules.classify("--some-feature", ss) == ("safe", "R5", ""))
ok("C-CORE-5: R4 UNMATCHED — a novel flag fails closed (never silent)",
   rules.classify_with_novelty("--brand-new-flag", ss, is_novel=True) == ("unmatched", "R4", ""))
# R2 scope guard: description text must NEVER be scanned — the rule asserts hazard_scope.
bad_ss = SignalSets(hazard_name_vocabulary=["skip"], hazard_scope="description")
try:
    rules.r2_hazard("--anything", bad_ss)
    ok("C-CORE-5: R2 scope guard raises on non-flag_name_only", False)
except ValueError:
    ok("C-CORE-5: R2 scope guard raises on non-flag_name_only", True)
# R4 priority: a novel flag that ALSO matches R1 keeps the higher posture.
ok("C-CORE-5: R4 lowest priority — novel+transport stays LOCKED",
   rules.classify_with_novelty("-p", ss, is_novel=True) == ("locked", "R1", ""))


# ── C-CORE-3 — CliHelp parse + engine floor_guard RAISES on a truncated help ────────────────────
print("\n[C-CORE-3] floor_guard fail-loud on a sub-floor parse")
TINY_HELP = """Usage: tool [options]

Options:
  -d, --debug            enable debug output
  --model <name>         pick a model
  --verbose              chatter
  --output <file>        write here
  -h, --help             show help
"""
parsed = CliHelpDiscoverer().parse(TINY_HELP, "option-row", platform_id="stub", version="9.9")
ok("C-CORE-3: CliHelp parses option rows (id=flag/--name, name keeps '--')",
   any(e.id == "flag/--debug" and e.name == "--debug" for e in parsed),
   detail=str([e.id for e in parsed]))


# A stub discoverer/platform to drive the engine floor + classify + project + refresh with NO spawn.
class StubDiscoverer:
    source_type = "cli-help"
    def __init__(self, entries):
        self._entries = entries
    def discover(self, executable, src):
        return "raw"
    def parse(self, raw, parse_rule="option-row", *, platform_id="", version=""):
        return list(self._entries)


def make_platform(disc_type="cli-help", floor=30):
    return PlatformEntry(
        id="stub-platform",
        executable_locator=ExecutableLocator(name="tool", which_fallback=False,
                                             known_paths=["/bin/tool"]),
        invocation_kind="subprocess",
        discovery_sources=[DiscoverySource(type=disc_type, command=["{binary}", "--help"],
                                           floor_guard=floor)],
        version_source=VersionSource(command=["{binary}", "--version"]),
        signal_sets=ss,
        consumer_reserved_invariants=ConsumerReservedInvariants(body_key_overrides=body_overrides),
    )

# floor_guard: 5 parsed rows < floor 30 → RAISE (via a stubbed discover_fn that returns the tiny set)
def floor_discover(platform, *, executable=None, version=None):
    # mimic discover.py's floor check using the engine path
    return parsed
plat = make_platform(floor=30)
try:
    # use the real discover() but inject the stub discoverer by monkeypatching the DISCOVERERS lookup
    # — simpler: call run_discover with a platform whose source floor is 30 and a stub via select.
    # We exercise the ENGINE floor by replicating discover()'s contract through a stub discover_fn
    # that returns the 5 rows, then asserting classify_platform surfaces them — but the floor lives
    # in discover(). So call run_discover with a stub discoverer patched in:
    import introspection.discover as disc_mod
    orig = disc_mod.DISCOVERERS.copy()
    disc_mod.DISCOVERERS["cli-help"] = lambda: StubDiscoverer(parsed)
    try:
        run_discover(plat, executable="/bin/tool", version="9.9")
        ok("C-CORE-3: engine floor_guard RAISES on sub-floor parse", False)
    except RuntimeError as e:
        ok("C-CORE-3: engine floor_guard RAISES on sub-floor parse", "floor_guard" in str(e))
    finally:
        disc_mod.DISCOVERERS.clear(); disc_mod.DISCOVERERS.update(orig)
except Exception as e:
    ok("C-CORE-3: engine floor_guard RAISES on sub-floor parse", False, detail=repr(e))


# ── GENPROOF-converse — an UNBUILT discoverer fails loud naming the missing class ───────────────
print("\n[GENPROOF-converse] unbuilt adapter FAILS LOUD (never silent empty registry)")
try:
    select_discoverer("rest-openapi", "novel-platform")
    ok("GENPROOF-converse: unbuilt 'rest-openapi' fails loud", False)
except MissingAdapterError as e:
    ok("GENPROOF-converse: unbuilt 'rest-openapi' fails loud naming RestOpenApiDiscoverer",
       "RestOpenApiDiscoverer" in str(e), detail=str(e))


# ── ENGINE — discover→classify→project→refresh over a stub (no live spawn) ──────────────────────
print("\n[ENGINE] discover→classify→project→refresh (stub PlatformEntry + stub discoverer)")
fixture_rows = [
    CapabilityEntry(id="flag/-p", kind="flag", name="-p"),                       # → R1 locked
    CapabilityEntry(id="flag/--dangerously-skip", kind="flag", name="--dangerously-skip"),  # → R2 hazard
    CapabilityEntry(id="flag/--cfg-server", kind="flag", name="--cfg-server"),   # → R3 consent (mcp)
    CapabilityEntry(id="flag/--some-feature", kind="flag", name="--some-feature"),  # → R5 safe
    CapabilityEntry(id="tool/Bash", kind="tool", name="Bash"),                   # non-flag, untouched
]
def stub_discover(platform, *, executable=None, version=None):
    return list(fixture_rows)

plat2 = make_platform(floor=0)  # floor 0 so the 5-row fixture passes
classified = engine.classify_platform(plat2, executable="/bin/tool", version="9.9",
                                       discover_fn=stub_discover)
by_id = {e.id: e for e in classified}
ok("ENGINE: -p classified R1 locked", by_id["flag/-p"].posture == "locked"
   and by_id["flag/-p"].posture_rule == "R1")
ok("ENGINE: --dangerously-skip classified R2 hazard", by_id["flag/--dangerously-skip"].posture == "hazard")
ok("ENGINE: --cfg-server classified R3 consent on axis 'mcp'",
   by_id["flag/--cfg-server"].posture == "consent" and by_id["flag/--cfg-server"].axis == "mcp")
ok("ENGINE: --some-feature classified R5 safe", by_id["flag/--some-feature"].posture == "safe")
ok("ENGINE: non-flag tool/Bash left at default posture (not flag-classified)",
   by_id["tool/Bash"].posture == "unmatched" and by_id["tool/Bash"].posture_rule == "")

proj = engine.project(classified)
ok("ENGINE: projection counts by kind", proj["counts"].get("flag") == 4 and proj["counts"].get("tool") == 1)
ok("ENGINE: projection postures tally", proj["postures"].get("locked") == 1
   and proj["postures"].get("hazard") == 1 and proj["postures"].get("consent") == 1)
ok("ENGINE: projection total + entries shape", proj["total"] == 5 and len(proj["entries"]) == 5)

# REFRESH: prior = the fixture minus the new flag; current adds one → added=[new]; novel→R4 surfaced.
prior = [e for e in classified if e.id != "flag/--brand-new"]
def stub_discover_with_new(platform, *, executable=None, version=None):
    return list(fixture_rows) + [CapabilityEntry(id="flag/--brand-new", kind="flag", name="--brand-new")]
payload = engine.refresh(plat2, prior, version_from="9.9", version_to="9.10",
                         discover_fn=stub_discover_with_new, executable="/bin/tool", version="9.10")
ok("REFRESH: added id surfaced in the batch payload", payload["added"] == ["flag/--brand-new"],
   detail=str(payload["added"]))
ok("REFRESH: the novel flag is UNMATCHED (R4, fail-closed) in unclassified",
   "flag/--brand-new" in payload["unclassified"], detail=str(payload["unclassified"]))
ok("REFRESH: payload shape (F-FIX-4: added/changed/unclassified/vanished/version_from/to)",
   set(payload) >= {"added", "changed", "unclassified", "vanished", "version_from", "version_to"})

# empty-diff-on-version-bump guard (C-REF-3 portion proven at the engine level)
def stub_discover_same(platform, *, executable=None, version=None):
    return list(prior)
try:
    engine.refresh(plat2, prior, version_from="9.9", version_to="9.10",
                   discover_fn=stub_discover_same, executable="/bin/tool", version="9.10")
    ok("REFRESH: version-bump + empty-diff RAISES (broken-read guard)", False)
except RuntimeError as e:
    ok("REFRESH: version-bump + empty-diff RAISES (broken-read guard)", "EMPTY" in str(e).upper())
# same-version no-op: empty diff allowed when version unchanged
same = engine.refresh(plat2, prior, version_from="9.9", version_to="9.9",
                      discover_fn=stub_discover_same, executable="/bin/tool", version="9.9")
ok("REFRESH: same-version empty-diff is a clean no-op (no raise)",
   not (same["added"] or same["changed"] or same["vanished"]))

# empty R1 input guard: a platform with no thunk + empty cached invariants RAISES (never silent demote)
plat_empty = make_platform(floor=0)
plat_empty = plat_empty.model_copy(update={
    "signal_sets": ss.model_copy(update={"transport_invariants": []})})
try:
    engine.classify_platform(plat_empty, executable="/bin/tool", version="9.9", discover_fn=stub_discover)
    ok("ENGINE: empty R1 set RAISES (never silent locked→safe demote)", False)
except RuntimeError as e:
    ok("ENGINE: empty R1 set RAISES (never silent locked→safe demote)", "R1" in str(e))


print(f"\n{'='*64}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN (no-live-claude unit verification; LEAD live items queued)")
