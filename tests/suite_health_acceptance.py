"""tests/suite_health_acceptance.py — THE STANDING ALL-GREEN GATE.

Runs EVERY acceptance suite STANDALONE and requires green (needs-live-dep = a documented skip, not a
red). This is the catch the 2026-06-08 cross-session unification proved MISSING: three reds slipped the
gate layer entirely —
  • conv_reach_acceptance     — RED on main, undetected (no gate ran it; the wire only runs build-AFFECTED
                                suites, and no build touched it).
  • event_address_acceptance  — RED on main, undetected (same reason) — two coa emits lost their address=.
  • json_schema_transport_acceptance — FALSE-GREEN by invocation: passed with an external PYTHONPATH,
                                failed standalone (ModuleNotFoundError) — nothing ran suites bare to catch it.

WHY the existing gates missed them:
  • drift_acceptance checks every suite is LISTED in STATE — NOT that it PASSES.
  • _affected_suites / _run_suites (the wire's definition-of-done) runs only the suites a BUILD touches —
    a red in an untouched suite accumulates silently.
  • nothing ran suites STANDALONE, so an invocation-dependent false-green was invisible.

This gate closes all three holes at once: Suite.suite_health() discovers every *_acceptance suite, runs
each as a fail-loud STANDALONE subprocess, and classifies green / needs-live-dep / red. It FAILS LOUD if
any suite is really red. It EXCLUDES itself (recursion guard).

SLOW — it spawns every suite — so it is a PRE-MERGE / PRE-DEPLOY / periodic standing gate, NOT a per-build
one. Run it before a merge lands or a deploy goes live; that is exactly when the silent-red class bites.
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
store = FsStore(os.path.join(tempfile.mkdtemp(prefix="suitehealth-"), "store"))
suite = Suite(store, reg, nodes_dir=NODES)

report = suite.suite_health()
c = report["counts"]
print(f"suite_health — {c['total']} suites :: {c['green']} green · {c['needs_dep']} needs-live-dep · {c['red']} RED")
for sname in report["needs_dep"]:
    print(f"  ~ needs-live-dep (documented skip, not a code red): {sname}")
for sname, detail in report["red"]:
    print(f"  ✗ RED: {sname} :: {detail[:180]}")

assert report["all_green"], (
    f"SUITE HEALTH RED: {[r[0] for r in report['red']]} — a suite is failing that the per-build gate "
    f"never runs. Fix it, or (if it needs a live model) make its skip detectable so it lands in "
    f"needs-live-dep, not red. This is the silent-red class the gate exists to catch.")

print(f"\nALL SUITES GREEN — the standing all-green gate holds "
      f"({c['green']} green, {c['needs_dep']} dep-gated skips, 0 red).")
