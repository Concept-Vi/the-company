"""tests/detectors_acceptance.py — the structural coherence detectors (round-1 layer).

Three detectors in runtime/coherence_detect.py, surfaced honestly by trust tier:

  GATE (trustworthy, hard-assert):
    · registry-vs-live — node-type files discoverable on disk (nodes/*.py with run()) vs the LIVE registry
      (capabilities().node_types). A pure set-difference of two declared sets — no model, no heuristic — so
      it can fail the build. Drift here is real.

  REPORT (CANDIDATE-only — positive-only, NEVER a gate):
    · capability-with-no-consumer — public Suite methods reached from no face/test/wire (AST call-graph).
    · hardcoding-candidates — big UPPER-name literals in runtime/*.py that MAY belong in a registry.
  These have false positives BY CONSTRUCTION (dynamic dispatch is invisible to AST; a big literal can be a
  legitimate grammar/constant — the run flags MODE_REGISTRY, which IS the registry). So they PROPOSE for a
  human/stronger-model to adjudicate; they print every run but do NOT fail the suite. Asserting their content
  would be exactly the over-claim the positive-only discipline forbids.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime import coherence_detect as cd

NODES = os.path.join(ROOT, "nodes")
reg = NodeRegistry(); reg.discover([NODES])
suite = Suite(FsStore(os.path.join(tempfile.mkdtemp(prefix="detectors-"), "store")), reg, nodes_dir=NODES)

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

# ── GATE: registry-vs-live (trustworthy) ─────────────────────────────────────────────────────────────
live = set(suite.capabilities().get("node_types", []))
rvl = cd.registry_vs_live(ROOT, live)
print(f"[gate] registry-vs-live: {len(rvl['on_disk'])} on disk · {len(rvl['live'])} live")
check(f"every node-type file on disk is LIVE in the registry (disk-not-live: {rvl['disk_not_live']})",
      not rvl["disk_not_live"])
check(f"every live node-type has a file on disk (live-not-disk: {rvl['live_not_disk']})",
      not rvl["live_not_disk"])

# ── REPORT: capability-with-no-consumer (candidate-only) ─────────────────────────────────────────────
cnc = cd.capability_no_consumer(ROOT)
print(f"\n[report · candidate] capability-with-no-consumer ({len(cnc)} — public Suite methods reached from "
      f"no face/test/wire; CANDIDATES, may be live via dynamic dispatch — adjudicate, don't auto-act):")
for m in cnc:
    print(f"    ~ {m}")
check("capability-no-consumer detector runs + returns a list (candidate report, not a gate)",
      isinstance(cnc, list))

# ── REPORT: hardcoding-candidates (candidate-only) ───────────────────────────────────────────────────
hc = cd.hardcoding_candidates(ROOT)
print(f"\n[report · candidate] hardcoding-candidates ({len(hc)} — big UPPER literals in runtime/*.py that "
      f"MAY belong in a registry; CANDIDATES — a grammar/the-registry-itself is a legit false positive):")
for d in hc[:15]:
    print(f"    ~ {d['file']}:{d['line']}  {d['name']} ({d['kind']}, {d['n']})")
check("hardcoding-candidates detector runs + returns a list (candidate report, not a gate)",
      isinstance(hc, list))

print(f"\nALL {PASS} CHECKS PASS — registry-vs-live GATE green; the two candidate detectors run + report "
      f"(positive-only, adjudicated by a human/stronger model, never auto-acted).")
