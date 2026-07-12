"""bridge_routes_acceptance — the TEETH that make BRIDGE_ROUTES the SINGLE SOURCE of the bridge route
table (registry-is-truth, AGENTS.md rules 3+8 + the api_verbs B-fix).

WHY this test exists: `Suite.capabilities()['api_verbs']` is now PROJECTED from `bridge.BRIDGE_ROUTES`
(the /api/* subset) instead of a hardcoded literal. But a hand-written BRIDGE_ROUTES that drifts from the
ACTUAL dispatch chain (`path == "…"` / `self.path == "…"` in do_GET/do_POST) would just be a THIRD copy of
the route literals — moving the hardcode, not de-hardcoding it. So this test greps the dispatcher's own
route literals out of bridge.py's source and asserts the set EQUALS BRIDGE_ROUTES, BOTH DIRECTIONS:
  • a route DISPATCHED but NOT in BRIDGE_ROUTES → fail loud (it would be invisible to capabilities()).
  • a route in BRIDGE_ROUTES but NOT dispatched → fail loud (a phantom verb advertised to the agent).
With this test, adding/removing a route in the dispatcher FORCES the matching BRIDGE_ROUTES edit, so the
registry stays truth. Run: ./.venv/bin/python tests/bridge_routes_acceptance.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime import bridge

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  {detail}")


def dispatched_routes() -> set:
    """Grep the route-string literals out of bridge.py's source — every `path == "…"` and
    `self.path == "…"` and `.startswith("…")` (the /mockups/ prefix is dispatched via startswith)."""
    src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runtime", "bridge.py")
    text = open(src, encoding="utf-8").read()
    # only scan the dispatcher body (after the do_GET def) so the BRIDGE_ROUTES literal itself isn't matched
    cut = text.index("def do_GET")
    body = text[cut:]
    routes = set()
    # path == "/…"  /  self.path == "/…"  /  self.path.split("?")[0] == "/…" (the query-string form —
    # /api/claude/turn dispatches through it; the extractor missing it made a real route look phantom)
    for m in re.finditer(r'(?:self\.)?path(?:\.split\("\?"\)\[0\])?\s*==\s*"(/[^"]*)"', body):
        routes.add(m.group(1))
    # (self.)path.startswith("/…")  — the prefix routes (e.g. /mockups/)
    for m in re.finditer(r'(?:self\.)?path\.startswith\(\s*"(/[^"]*)"', body):
        routes.add(m.group(1))
    # (self.)path in ("/…", "/…")  — the tuple-membership form (the supervisor quartet dispatches
    # through it; the extractor missing it made those four REAL routes look phantom — found 2026-07-13
    # while adding /app, fixed as the class: every dispatch form the file actually uses is extracted)
    for m in re.finditer(r'(?:self\.)?path\s+in\s+\(([^)]*)\)', body):
        for s in re.finditer(r'"(/[^"]*)"', m.group(1)):
            routes.add(s.group(1))
    return routes


print("=== bridge_routes_acceptance — BRIDGE_ROUTES is the SINGLE SOURCE (drift teeth) ===")

declared = set(bridge.BRIDGE_ROUTES)
dispatched = dispatched_routes()

check("BRIDGE_ROUTES is a non-empty tuple", isinstance(bridge.BRIDGE_ROUTES, tuple) and len(declared) > 0)
check("BRIDGE_ROUTES has no duplicates", len(declared) == len(bridge.BRIDGE_ROUTES),
      f"{len(bridge.BRIDGE_ROUTES)} entries, {len(declared)} unique")

dispatched_not_declared = dispatched - declared
declared_not_dispatched = declared - dispatched
check("every DISPATCHED route is in BRIDGE_ROUTES (no invisible route)",
      not dispatched_not_declared, f"missing from BRIDGE_ROUTES: {sorted(dispatched_not_declared)}")
check("every BRIDGE_ROUTES entry is actually DISPATCHED (no phantom verb)",
      not declared_not_dispatched, f"in BRIDGE_ROUTES but not dispatched: {sorted(declared_not_dispatched)}")

# api_verbs PROJECTION: the /api/ subset of BRIDGE_ROUTES, by the intrinsic path-prefix (no hand-class).
from store.fs_store import FsStore
from runtime.registry import NodeRegistry
import tempfile

tmp = tempfile.mkdtemp(prefix="bridge_routes_")
store = FsStore(os.path.join(tmp, "store"))
reg = NodeRegistry()
suite = bridge.Suite(store, reg)
cap = suite.capabilities()
api_verbs = cap["api_verbs"]

expected_api = sorted(r for r in declared if r.startswith("/api/"))
check("api_verbs == the /api/ projection of BRIDGE_ROUTES (registry-is-truth)",
      sorted(api_verbs) == expected_api,
      f"\n    api_verbs={sorted(api_verbs)}\n    expected={expected_api}")
check("api_verbs is NON-empty + every entry starts with /api/",
      api_verbs and all(v.startswith("/api/") for v in api_verbs))
check("the standing assertion holds: /api/cognition_info is an api verb",
      "/api/cognition_info" in api_verbs)
# the de-hardcode landmark: adding a route to BRIDGE_ROUTES would change api_verbs (proven structurally —
# api_verbs is literally derived, so this is a tautology we assert to lock the derivation in place).
check("api_verbs is DERIVED from BRIDGE_ROUTES, not a literal (the de-hardcode)",
      set(api_verbs) == {r for r in bridge.BRIDGE_ROUTES if r.startswith("/api/")})

print(f"\n{'PASS' if FAIL == 0 else 'FAIL'} — {PASS} passed, {FAIL} failed")
sys.exit(0 if FAIL == 0 else 1)
