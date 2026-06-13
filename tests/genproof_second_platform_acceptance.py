"""tests/genproof_second_platform_acceptance.py — C-GENPROOF (THE LIFT GATE) acceptance.
Mirror-Registry System, LANE-INTROSPECTION-CORE / LANE-REGISTRIES.

THE GENERALIZATION-PROOF — the lift's final proof. This suite proves a SECOND platform registers,
discovers, classifies, and projects through the EXISTING four-verb engine + the EXISTING cli-help
adapter with ZERO edits to introspection/engine.py / rules.py / discover.py / adapters/. It is the
single criterion that proves the two-level separation is real: a KNOWN type is almost-free (just a
data row); a NOVEL type fails LOUD naming the missing adapter, never hand-papered, never a silent
empty registry.

VERIFY-BY-USE. The WORKS case spawns the REAL `gh` binary (subprocess, NO claude, NO model load) and
runs the live DISCOVER→CLASSIFY→PROJECT circuit. Run: `python3 tests/genproof_second_platform_acceptance.py`.
Build Plan §C-GENPROOF; Spec §7 / §8.3 boundary; F-FIX-6 / F-FIX-10.

Covers:
  (a) WORKS  — gh-cli registers via the REAL PlatformRegistry file discovery; the engine DISCOVERS +
       CLASSIFIES + PROJECTS it live through DISCOVERERS["cli-help"] (CliHelpDiscoverer) UNCHANGED →
       a non-zero flag count, real R5/R3 postures, R3 consent on the declared axes. ZERO engine edits.
  (b) UNBUILT-TYPE — a platform declaring discovery_sources[].type="rest-openapi" (a VALID Literal
       whose adapter is UNBUILT) passes model_validate, then FAILS LOUD at discover() naming the
       missing RestOpenApiDiscoverer + the built set — the §8.3 gap-surface, not a crash.
  (c) LEAK-GREP — introspection/{engine,rules,discover}.py + adapters/ carry ZERO platform-name
       literals (claude/dangerously/--mcp-config/stream-json) — the engine stayed platform-agnostic
       THROUGH a second platform.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import shutil
from contracts.platform_entry import PlatformEntry
from introspection.platforms import platform_registry, PLATFORMS_DIR
from introspection.registry import CapabilityRegistry
from introspection.discover import discover as run_discover, MissingAdapterError

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not cond else ""))


# ── (a) WORKS CASE — second known-type platform, almost free, ZERO engine edits ─────────────────
print("\n[(a) WORKS] gh-cli registers + DISCOVER→CLASSIFY→PROJECT via the EXISTING cli-help adapter")
GH = shutil.which("gh")
reg = platform_registry()        # REAL file discovery over platforms/*.py
ok("(a) gh-cli self-registered via PlatformRegistry file discovery (a NEW data row, no engine edit)",
   "gh-cli" in reg, detail=f"discovered ids={reg.ids()}")
ok("(a) instance #1 (claude-code) still registers alongside it (two rows, one engine)",
   "claude-code" in reg, detail=str(reg.ids()))

if GH and "gh-cli" in reg:
    gh = reg["gh-cli"]
    ok("(a) gh-cli declares a 'cli-help' discovery source (the KNOWN type → existing adapter)",
       any(s.type == "cli-help" for s in gh.discovery_sources),
       detail=str([s.type for s in gh.discovery_sources]))
    # LIVE DISCOVER+CLASSIFY through the unchanged engine (spawns `gh pr create --help`)
    cap = CapabilityRegistry().discover(gh)
    snap = cap.snapshot()
    flags = cap.by_kind("flag")
    ok("(a) NON-ZERO capability count came through the existing machinery (the headline)",
       snap["total"] > 0 and len(flags) >= 10,
       detail=f"total={snap['total']} flags={len(flags)} counts={snap['counts']}")
    ok("(a) every discovered row is a CapabilityEntry flag tagged with the platform id + help-parse",
       all(e.kind == "flag" and e.platform_id == "gh-cli" and e.source == "help-parse" for e in flags),
       detail=str([(e.source, e.platform_id) for e in flags[:3]]))
    # CLASSIFY produced REAL postures (not a pass-through): R5 SAFE majority + R3 CONSENT on the axes
    postures = snap["postures"]
    ok("(a) CLASSIFY stamped real postures — R5 SAFE majority over the discovered flags",
       postures.get("safe", 0) > 0, detail=str(postures))
    consent = {e.name: e.axis for e in flags if e.posture == "consent"}
    ok("(a) R3 CONSENT fired on the declared capability axes (--repo→repo-target, --web→browser)",
       consent.get("--repo") == "repo-target" and consent.get("--web") == "browser",
       detail=str(consent))
    # Prove the adapter that produced them is the UNCHANGED cli-help adapter (no gh-specific branch).
    from introspection.adapters import DISCOVERERS
    ok("(a) the rows came through DISCOVERERS['cli-help'] == CliHelpDiscoverer (unchanged closed set)",
       DISCOVERERS["cli-help"].__name__ == "CliHelpDiscoverer" and set(DISCOVERERS) == {"cli-help", "stream-init"},
       detail=str({k: v.__name__ for k, v in DISCOVERERS.items()}))
else:
    ok("(a) gh binary present on PATH for the live proof", bool(GH),
       detail="gh not on PATH — cannot run the live WORKS case (LEAD-verify on a host with gh)")


# ── (b) UNBUILT-TYPE CASE — valid Literal, unbuilt adapter → FAIL LOUD (gap-surface, not crash) ──
print("\n[(b) UNBUILT-TYPE] rest-openapi (valid Literal, no adapter) → discover() FAILS LOUD")
decl = {
    "id": "unbuilt-probe",
    "invocation_kind": "rest",     # also unbuilt — exercises the invoker gap-surface too
    "executable_locator": {"name": "https://api.example.com", "which_fallback": False},
    "discovery_sources": [{"type": "rest-openapi", "command": ["{binary}/openapi.json"]}],
    "signal_sets": {"transport_invariants": ["--x"], "hazard_scope": "flag_name_only"},
}
p = PlatformEntry.model_validate(decl)
ok("(b) a VALID-but-unbuilt DiscoverySourceType ('rest-openapi') passes model_validate (it IS a Literal)",
   p.id == "unbuilt-probe")
try:
    run_discover(p, executable="https://api.example.com", version="1")
    ok("(b) discover() FAILS LOUD on the unbuilt adapter", False)
except MissingAdapterError as e:
    msg = str(e)
    ok("(b) discover() raised MissingAdapterError naming the missing RestOpenApiDiscoverer + built set",
       "RestOpenApiDiscoverer" in msg and "cli-help" in msg, detail=msg[:200])


# ── (c) LEAK-GREP — engine stayed platform-agnostic THROUGH a second platform ────────────────────
print("\n[(c) LEAK-GREP] ZERO platform-name literals in introspection engine/rules/discover/adapters")
BANNED = ["claude", "dangerously", "--mcp-config", "stream-json"]
LEVEL1 = [
    os.path.join(ROOT, "introspection", "engine.py"),
    os.path.join(ROOT, "introspection", "rules.py"),
    os.path.join(ROOT, "introspection", "discover.py"),
] + [
    os.path.join(ROOT, "introspection", "adapters", f)
    for f in os.listdir(os.path.join(ROOT, "introspection", "adapters")) if f.endswith(".py")
]
leak_hits = []
for path in LEVEL1:
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            low = line.lower()
            for tok in BANNED:
                if tok in low:
                    leak_hits.append(f"{os.path.relpath(path, ROOT)}:{n}: {tok!r}")
ok(f"(c) ZERO platform-name literals across {len(LEVEL1)} Level-1 files (hit count = 0)",
   not leak_hits, detail="LEAKS: " + "; ".join(leak_hits))
print(f"      leak hit count: {len(leak_hits)}")


print(f"\n{'='*64}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — C-GENPROOF: a 2nd known-type platform is almost-free; a novel type fails loud.")
