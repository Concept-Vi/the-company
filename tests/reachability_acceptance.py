"""tests/reachability_acceptance.py — THE REACHABILITY GATE.

Every `/api` route must reach a caller (a front-end reference in canvas/app/src, or a test) OR be a
CATALOGUED orphan in the declared registry (design/_system/orphan-routes.json, via Suite._orphan_routes()). This catches the disconnection class the all-green gate cannot:
a route that WORKS but nothing calls it — built-but-unwired. It has no failing test, so it is invisible to
suite_health; it just sits there. (The X16 seam was a cousin; the latent gold — /api/knobs, /api/run-stats
— and the 12 cognition authoring endpoints are live instances of exactly this.)

A NEW orphan — a built route with no caller that is NOT in the catalogue — FAILS this gate: a fresh
disconnection, caught the moment it appears, instead of accumulating silently across sessions. The
catalogue (design/_system/orphan-routes.json — a DECLARED registry, not a hardcoded dict) doubles as the connect-it BACKLOG, tagged:
  to_build_ui  — needs a screen (a Claude Design target; the authoring UI)
  to_wire      — built, should have an FE caller (the latent gold + addressed surfaces)
  voice_owned  — the concurrent voice session's lane (theirs to wire)
  backend_only — legitimately no FE (an agent/operator/internal entry point)

Extraction is AST-grounded (a route literal in a real self.path ==/in routing decision, not one mentioned
in a comment/docstring) and the consumer check is call-marker-based on the comment-stripped corpus (a real
fetch/EventSource/HTTP call, not a mention/existence-assertion/prose-in-a-string) — both in
runtime/coherence_detect.py. This fixed the measured false-WIRE bug (a dead route reading as wired because
its name appeared in a comment/label). A route consumed ONLY via a computed/template path can still read as
an orphan (the safe direction) — if so, add it to design/_system/orphan-routes.json, or (better) wire a real caller.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
reg = NodeRegistry(); reg.discover([NODES])
store = FsStore(os.path.join(tempfile.mkdtemp(prefix="reach-gate-"), "store"))
suite = Suite(store, reg, nodes_dir=NODES)

rep = suite.reachability()
c = rep["counts"]
print(f"reachability — {c['routes']} /api routes :: {c['wired']} wired · {c['orphan']} catalogued-orphan "
      f"· {c['new']} NEW-orphan · {c['stale']} stale")
for tag, routes in rep["backlog"].items():
    if routes:
        print(f"  [{tag}] {len(routes)}: {', '.join(r.split('/api/', 1)[1] for r in routes)}")
for r in rep["new_orphans"]:
    print(f"  ⚠ NEW ORPHAN (built, no caller, not catalogued): {r}")
for r in rep["stale"]:
    print(f"  · stale catalogue entry (now wired or removed — prune from design/_system/orphan-routes.json): {r}")

assert rep["all_accounted"], (
    f"NEW UNWIRED ROUTES: {rep['new_orphans']} — built /api routes with NO front-end or test caller, not "
    f"in the catalogue. Either wire them to a caller, or add them to design/_system/orphan-routes.json with "
    f"a tag (to_build_ui / to_wire / voice_owned / backend_only) so the disconnection is TRACKED, not silent.")

print(f"\nREACHABILITY GREEN — every /api route reaches a caller or is a catalogued orphan "
      f"({c['wired']} wired, {c['orphan']} catalogued, 0 new disconnections).")
