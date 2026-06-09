#!/usr/bin/env python3
"""tests/route_run_output_acceptance.py — E4 (SUITE-2 lane): run-output DESTINATION.

E4 = chain save/re-run + output-destination. The SAVE + RE-RUN half is the SAVED CASCADE (save_cascade/
run_cascade, GROUP N — proven by cascade_acceptance 25/25). This is the REMAINING bit: route a DIRECT run's
output to a named destination/lane WITHOUT a saved cascade.

REUSE-don't-parallel (the lane law): `route_run_output` READS the output via `resolve_address` (the canonical
resolver) and performs the effect via `rules.route` over `DESTINATION_KINDS` — NO second router.

THE FLOOR (C9.2): the routable kinds are the FIVE non-consequential DESTINATION_KINDS; NONE is
resolve/approve/dispatch (the build-dispatch floor is unforgeable). Proven here.

PROOFS:
  1. address — route a discovered run output to a durable run:// landing (re-resolvable).
  2. lane    — route to a named typed lane (a cognition.lane event on the ONE log).
  3. surface — route to the inbox (an `ask`, resolved=None — NEVER a resolve).
  4. fail-loud — unknown destination + unresolvable address both raise (never a silent no-op).
  5. the FLOOR — resolve/approve/dispatch are NOT routable.
"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore
from runtime.suite import Suite
from runtime.registry import NodeRegistry
from runtime import rules as _rules

PASS = 0
def check(label, cond):
    global PASS
    print(f"  {'ok ' if cond else 'XX '} {label}")
    if not cond:
        raise SystemExit(f"FAIL: {label}")
    PASS += 1


with tempfile.TemporaryDirectory() as root:
    store = FsStore(root)
    reg = NodeRegistry().discover([os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes")])
    suite = Suite(store, reg)

    # seed a "discovered" run output at a run:// address (as run_role/run_items would).
    src = "run://turn-x/ground"
    store.set_ref(src, store.put_content("the ground role concluded: in-scope, note=foo"))

    print("[1] address — route the output to a durable run:// landing (re-resolvable)")
    out = suite.route_run_output(src, "address", turn_id="t1")
    check("1 route(address) acted", out.get("acted") and out.get("destination") == "address")
    landed = out.get("address")
    from runtime import cognition as _cog
    check("1 the landed address re-resolves to the routed output",
          "in-scope" in str(_cog.resolve_address(store, landed, turn_id="t1")))

    print("\n[2] lane — route to a named typed lane (cognition.lane on the ONE log)")
    out2 = suite.route_run_output(src, "lane", turn_id="t2", params={"lane": "digest-lane"})
    check("2 route(lane) acted on the named lane", out2.get("acted") and out2.get("lane") == "digest-lane")
    lane_evs = [e for e in store.events_since(-1) if e.get("kind") == "cognition.lane"]
    check("2 a cognition.lane event landed on the event log", any(e.get("lane") == "digest-lane" for e in lane_evs))

    print("\n[3] surface — route to the inbox (an `ask`, NEVER a resolve)")
    out3 = suite.route_run_output(src, "surface", turn_id="t3", params={"title": "routed output for review"})
    check("3 route(surface) surfaced a review item", out3.get("acted") and out3.get("surfaced"))
    # the surfaced item is an `ask` (resolved=None) — never a resolve event (the floor).
    asks = [e for e in store.events_since(-1) if e.get("kind") == "ask"]
    resolves = [e for e in store.events_since(-1) if e.get("kind") == "resolve"]
    check("3 surfacing emitted an `ask`, NOT a resolve (the floor holds)", asks and not resolves)

    print("\n[4] fail-loud — unknown destination + unresolvable address")
    raised = False
    try:
        suite.route_run_output(src, "not-a-destination")
    except ValueError:
        raised = True
    check("4 an unknown destination FAILS LOUD (never a silent no-op)", raised)
    raised2 = False
    try:
        suite.route_run_output("run://never-set/role", "address")
    except Exception:
        raised2 = True
    check("4 an unresolvable address FAILS LOUD (never route an empty output)", raised2)

    print("\n[5] the FLOOR — resolve/approve/dispatch are NOT routable")
    for forbidden in ("resolve", "approve", "dispatch"):
        r = False
        try:
            suite.route_run_output(src, forbidden)
        except ValueError:
            r = True
        check(f"5 destination {forbidden!r} is REFUSED (the build-dispatch floor is unforgeable)", r)
    check("5 DESTINATION_KINDS contains none of resolve/approve/dispatch",
          not ({"resolve", "approve", "dispatch"} & set(_rules.DESTINATION_KINDS)))

print(f"\nALL {PASS} CHECKS PASS — E4 run-output DESTINATION: route a discovered run output to "
      f"address/lane/surface via rules.route over DESTINATION_KINDS (reuse, no parallel router); fail-loud "
      f"on unknown/unresolvable; the resolve/approve/dispatch floor is unforgeable. (Save+re-run = the cascade.)")
