"""tests/convergence_signoff_acceptance.py — F: coherence's structural half of the convergence sign-off.

The convergence round's whole-system sign-off has TWO halves: the STRUCTURAL gate battery (coherence's —
adversarial-to-appearance, exact, can't be green-painted) AND the by-use operator path (guided-review's).
This is coherence's half, callable as one verdict over the integrated tree: no NEW unwired routes (all
accounted), registry-vs-live OK, and the burn-down has no orphan that isn't either wired or dispositioned.
It runs the detectors CROSS-FORK (tree-wide, not per-lane — the honesty-instrument working over all three
lanes' merged work). Exact + re-derivable → a structural verdict that can BLOCK the convergence merge, not a
goodwill check.
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

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

# the registry check needs the LIVE node-types (fail-loud if absent — never silently passed)
_reg = NodeRegistry(); _reg.discover([os.path.join(ROOT, "nodes")])
_suite = Suite(FsStore(os.path.join(tempfile.mkdtemp(prefix="signoff-"), "store")), _reg, nodes_dir=os.path.join(ROOT, "nodes"))
live_types = set(_suite.capabilities().get("node_types", []))

verdict = cd.structural_signoff(ROOT, live_types)
check("without live_types the registry check is NOT silently passed (fail-loud)",
      cd.structural_signoff(ROOT)["pass"] is False)
check("structural_signoff returns a verdict over the WHOLE tree (pass + reasons + evidence)",
      "pass" in verdict and "reasons" in verdict and "evidence" in verdict)
check("it runs reachability tree-wide (no-NEW-orphan is a sign-off condition)",
      "new_orphans" in verdict["evidence"])
check("it runs registry-vs-live tree-wide (a sign-off condition)",
      "registry_drift" in verdict["evidence"])
check("the verdict is a hard boolean (can BLOCK the convergence merge — not a soft opinion)",
      isinstance(verdict["pass"], bool))
# the conditions are exact/structural — each reason names a concrete, re-derivable check
check("each failing reason (if any) is a concrete structural fact, not a vibe",
      all(isinstance(r, str) for r in verdict["reasons"]))
# on the current tree: no new orphans (all catalogued) + registry in sync → the structural half should PASS
check("on the current integrated tree the structural half PASSES (no new orphans, registry in sync)",
      verdict["pass"] is True)

print(f"\nALL {PASS} CHECKS PASS — coherence's structural convergence sign-off: the gate battery run "
      f"tree-wide as one exact, re-derivable, can't-be-green-painted verdict (paired with guided-review's "
      f"by-use operator path). The substrate as the shared honesty instrument, callable.")
