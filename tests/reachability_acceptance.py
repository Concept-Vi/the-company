"""tests/reachability_acceptance.py — THE REACHABILITY GATE.

Every `/api` route must reach a caller (a front-end reference in canvas/app/src, or a test) OR be a
CATALOGUED orphan in Suite._ORPHAN_ROUTES. This catches the disconnection class the all-green gate cannot:
a route that WORKS but nothing calls it — built-but-unwired. It has no failing test, so it is invisible to
suite_health; it just sits there. (The X16 seam was a cousin; the latent gold — /api/knobs, /api/run-stats
— and the 12 cognition authoring endpoints are live instances of exactly this.)

A NEW orphan — a built route with no caller that is NOT in the catalogue — FAILS this gate: a fresh
disconnection, caught the moment it appears, instead of accumulating silently across sessions. The
catalogue (_ORPHAN_ROUTES) doubles as the connect-it BACKLOG, tagged:
  to_build_ui  — needs a screen (a Claude Design target; the authoring UI)
  to_wire      — built, should have an FE caller (the latent gold + addressed surfaces)
  voice_owned  — the concurrent voice session's lane (theirs to wire)
  backend_only — legitimately no FE (an agent/operator/internal entry point)

Heuristic: it matches the route's literal string. A route called ONLY via a computed/template path reads
as an orphan — if that happens, add it to _ORPHAN_ROUTES with a note, or (better) reference its literal.
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
    print(f"  · stale catalogue entry (now wired or removed — prune from _ORPHAN_ROUTES): {r}")

assert rep["all_accounted"], (
    f"NEW UNWIRED ROUTES: {rep['new_orphans']} — built /api routes with NO front-end or test caller, not "
    f"in the catalogue. Either wire them to a caller, or add them to Suite._ORPHAN_ROUTES with a tag "
    f"(to_build_ui / to_wire / voice_owned / backend_only) so the disconnection is TRACKED, not silent.")

print(f"\nREACHABILITY GREEN — every /api route reaches a caller or is a catalogued orphan "
      f"({c['wired']} wired, {c['orphan']} catalogued, 0 new disconnections).")
