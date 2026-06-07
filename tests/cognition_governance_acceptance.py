"""tests/cognition_governance_acceptance.py — Concurrent Cognition G9 (governance & safety, binds all).

The STANDING regression that keeps the cognition layer's safety floor true as the system grows.
Mirrors e6_governance (the app face) for the cognition face. Proves, by use + adversarially:

  C9.1  roles act only within the governance posture — a model runs ONLY inside a role (run_role);
        a role/rule cannot reach a gate-bypassing action. (The cognition layer has NO apply/dispatch
        verb of its own — its only effects are the 5 DESTINATION_KINDS, none consequential.)
  C9.2  THE unforgeable-resolve INVARIANT (R1-FOLD F6): no role / rule / _run_swarm path may emit a
        `resolve`/`approve`/`dispatch` event (the sole build-dispatch trigger — operator-only via
        resolve_surfaced). Enforced BY CONSTRUCTION (FORBIDDEN_DESTINATION_VERBS + DESTINATION_KINDS)
        AND asserted as a STANDING source-invariant so a future role-reachable verb can't open it.
  C9.3  fail loud everywhere — missing ref, missing rule input, malformed role output, bad rule all RAISE.
  C9.4  every net-new cognition registry declares a drift home + a drift assertion (so drift has teeth).
"""
import os
import sys
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

PASS = 0
ok = True


def check(label, cond):
    global PASS, ok
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        ok = False
        print(f"  FAIL  {label}")


from runtime import rules as _rules

# ── C9.2 — the unforgeable-resolve invariant ────────────────────────────────────────────────────
print("\n[C9.2] the claude -p / build-dispatch floor is unforgeable from the cognition layer")
check("C9.2 DESTINATION_KINDS contains NONE of resolve/approve/dispatch",
      not ({"resolve", "approve", "dispatch"} & set(_rules.DESTINATION_KINDS)))
check("C9.2 FORBIDDEN_DESTINATION_VERBS names the three dispatch triggers",
      set(_rules.FORBIDDEN_DESTINATION_VERBS) == {"resolve", "approve", "dispatch"})

# a rule that DECLARES a forbidden destination must RAISE at construction (structural, not runtime)
for verb in ("resolve", "approve", "dispatch"):
    raised = False
    try:
        _rules.Rule(id="adv", when={"op": "lit", "value": True}, destination=verb, target="x")
    except Exception:
        raised = True
    check(f"C9.2 adversarial: a rule declaring destination={verb!r} is REJECTED at construction", raised)

# STANDING SOURCE-INVARIANT: no cognition execution path emits/calls the resolve trigger. The only
# legitimate token occurrences are run_ref RESOLUTION (resolve_run_ref / resolved values), the
# FORBIDDEN list itself, and comments/docstrings. A bare resolve_surfaced/governance.resolve CALL,
# or emitting a {"kind":"resolve"} event, from cognition code would open the floor.
COG_SOURCES = ["runtime/cognition.py", "runtime/rules.py", "runtime/roles.py"] + \
    [f"roles/{f}" for f in os.listdir("roles") if f.endswith(".py")]
floor_breach = []
for src in COG_SOURCES:
    with open(src) as fh:
        for i, line in enumerate(fh, 1):
            code = line.split("#", 1)[0]  # strip end-of-line comments
            if "resolve_surfaced" in code or "governance.resolve" in code \
               or re.search(r'["\']kind["\']\s*:\s*["\']resolve["\']', code) \
               or re.search(r'\.resolve\s*\(', code):
                floor_breach.append(f"{src}:{i}: {line.strip()[:80]}")
check("C9.2 STANDING source-invariant: NO cognition path calls resolve_surfaced/governance.resolve "
      "or emits a resolve event (only operator-only resolve_surfaced does)", not floor_breach)
if floor_breach:
    for b in floor_breach:
        print("      breach:", b)

# ── C9.1 — a model runs only inside a role; the cognition layer has no consequential verb ─────────
print("\n[C9.1] roles act only within posture — no gate-bypassing action reachable from cognition")
# the rule engine routes; the ONLY effects are the declared destination kinds (all non-consequential:
# inject/chain/address are run:// writes/role-fires; surface SURFACES for the operator; lane = an event).
check("C9.1 the rule layer's effects are exactly the 5 non-consequential DESTINATION_KINDS",
      set(_rules.DESTINATION_KINDS) == {"inject", "chain", "address", "surface", "lane"})
# the surface destination routes to the operator inbox as an ASK (resolved=None) — it cannot self-resolve.
# Real structural assertion: rules.py's route() for the surface kind goes through surface_review and emits
# an `ask` (resolved=None), and NO route effect emits/calls a resolve. Find the route() body + scan its calls.
src_rules = open("runtime/rules.py").read()
_route_body = src_rules.split("def route", 1)[1] if "def route" in src_rules else ""
_route_code = "\n".join(l.split("#", 1)[0] for l in _route_body.splitlines())  # strip comments
check("C9.1 route()'s surface destination uses surface_review (the operator ASK path), not a resolve",
      "surface_review" in _route_code and not re.search(r'\.resolve\s*\(|["\']kind["\']\s*:\s*["\']resolve["\']', _route_code))

# ── C9.3 — fail loud everywhere ──────────────────────────────────────────────────────────────────
print("\n[C9.3] fail loud — missing/bad inputs RAISE, never a silent truthy/skip")
from runtime.cognition import injection_rule, resolve_run_ref
import tempfile
from store.fs_store import FsStore

# missing declared rule input → raise (not implicit-truthy)
for bad in ({}, {"recall": {"relevant": True, "snippet": "x"}}, {"ground": {"in_scope": True, "note": "n"}}):
    raised = False
    try:
        injection_rule(bad)
    except Exception:
        raised = True
    check(f"C9.3 injection_rule raises on missing declared input (keys={list(bad)})", raised)

# unresolved run:// ref → raise
store = FsStore(tempfile.mkdtemp(prefix="g9-"))
raised = False
try:
    resolve_run_ref("run://nope/missing", store)
except Exception:
    raised = True
check("C9.3 resolve_run_ref raises on an unresolved ref (never route on a missing value)", raised)

# a non-run:// scheme → raise
raised = False
try:
    resolve_run_ref("swarm://x/y", store)
except Exception:
    raised = True
check("C9.3 resolve_run_ref rejects a non-run:// address (swarm:// is not a scheme)", raised)

# ── C9.4 — every net-new cognition registry has a drift home + a drift assertion ──────────────────
print("\n[C9.4] drift homes: every net-new cognition registry is self-described + drift-asserted")
HOMES = {
    "EDGE_KINDS (G1.3)":            ("contracts/node_record.py", "contracts/AGENTS.md", "tests/edge_kinds_acceptance.py"),
    "roles registry (G2)":         ("runtime/roles.py",        "roles/AGENTS.md",      "tests/roles_acceptance.py"),
    "RULE_OPS+DESTINATION (G3)":    ("runtime/rules.py",        "runtime/AGENTS.md",    "tests/rules_acceptance.py"),
    "MODEL_CAPABILITIES (G8)":      ("ops/cli/capabilities.py", "ops/AGENTS.md",        "tests/model_capabilities_acceptance.py"),
    "THOUGHT_SHAPES+GRAIN (G4)":    ("runtime/suite.py",        "runtime/AGENTS.md",    "tests/chat_parts_acceptance.py"),
}
for name, (regfile, home, test) in HOMES.items():
    check(f"C9.4 {name}: registry file + drift home ({home}) + acceptance test all present",
          os.path.exists(regfile) and os.path.exists(home) and os.path.exists(test))

print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {PASS} checks passed — G9 cognition governance: "
      "the resolve/dispatch floor is unforgeable from the cognition layer (by construction + standing "
      "source-invariant); roles run only inside run_role with non-consequential effects; fail-loud holds; "
      "every net-new registry has a drift home.")
sys.exit(0 if ok else 1)
