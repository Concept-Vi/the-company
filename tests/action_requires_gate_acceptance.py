#!/usr/bin/env python3
"""Acceptance — a unit of WORK (a cascade/action) can declare `requires` a loadout, and an action-level
RESOLVE-GATE surfaces a confirm + fails loud when that loadout isn't resident (never runs against the wrong
loadout). The work layer of the loadout-resolution spine, reusing the mode→loadout surface + the (now
RHM-repointing) apply_loadout door.

Checks:
  • build_action PRESERVES a valid `requires` (a loadout_class string) + REJECTS a non-string/empty one;
  • _gate_work_requires: no-requires → no-op; resident loadout → proceeds; MISSING services → surfaces a
    loadout_swap + raises GovernanceError; unknown combo → ValueError; dedups a pending swap;
  • run_cascade INVOKES the gate (a cascade requiring a missing loadout fails loud BEFORE any step runs).

_resolve_loadout is mocked so the gate's branching is tested hermetically (independent of what's live)."""

import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite, GovernanceError
from runtime import coherence_actions as ca

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# ---- 1. build_action: requires preserved / validated (pure, no Suite) --------------------------------
# a minimal VALID decl (op=generate, no roles= passed so the role-required check is skipped) so build_action
# reaches the requires handling.
_decl = {"name": "qstep", "steps": [{"op": "generate"}], "requires": "quality-9b"}
res = ca.build_action(_decl, models={"m"})
check("build_action PRESERVES a valid requires (loadout_class string)",
      res.get("ok") and res["action"].get("requires") == "quality-9b")

resb = ca.build_action({"name": "qstep", "steps": [{"op": "generate"}], "requires": 123}, models={"m"})
check("build_action REJECTS a non-string requires (fail loud)",
      (not resb.get("ok")) and "requires" in resb.get("error", "").lower())

rese = ca.build_action({"name": "qstep", "steps": [{"op": "generate"}], "requires": "   "}, models={"m"})
check("build_action REJECTS an empty/blank requires",
      (not rese.get("ok")) and "requires" in rese.get("error", "").lower())

# ---- 2. _gate_work_requires branches (Suite, _resolve_loadout mocked) ---------------------------------
store_dir = tempfile.mkdtemp(prefix="action-requires-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    nreg = NodeRegistry(); nreg.discover([NODES])
    suite = Suite(store, nreg, nodes_dir=NODES)

    # mock the loadout resolver: controllable (services, missing) per call, or raise for an unknown combo.
    _state = {"services": ["chat-9b-fp8"], "missing": ["chat-9b-fp8"], "raise": False}
    def _fake_resolve(lc):
        if _state["raise"]:
            raise ValueError(f"loadout {lc!r} names no combo (mock)")
        return list(_state["services"]), list(_state["missing"])
    suite._resolve_loadout = _fake_resolve

    # (a) no requires → no-op, nothing surfaced.
    n0 = len(suite.inbox.list())
    suite._gate_work_requires("cascade «x»", None)
    suite._gate_work_requires("cascade «x»", "")
    check("no-requires is a no-op (no raise, nothing surfaced)", len(suite.inbox.list()) == n0)

    # (b) required loadout fully resident (missing=[]) → proceeds, nothing surfaced.
    _state["missing"] = []
    suite._gate_work_requires("cascade «x»", "quality-9b")
    check("a resident required loadout proceeds (no raise, no surface)", len(suite.inbox.list()) == n0)

    # (c) missing services → surfaces a loadout_swap AND raises GovernanceError.
    _state["missing"] = ["chat-9b-fp8"]
    raised = False
    try:
        suite._gate_work_requires("cascade «needs9b»", "quality-9b")
    except GovernanceError:
        raised = True
    check("a missing required loadout FAILS LOUD (GovernanceError)", raised)
    swaps = [d for d in suite.inbox.list()
             if d.get("action") == "loadout_swap" and (d.get("payload") or {}).get("loadout_class") == "quality-9b"]
    check("a loadout_swap confirm was SURFACED for the missing loadout", len(swaps) == 1)
    check("the surfaced swap names the requiring work + the missing service",
          "needs9b" in (swaps[0]["payload"].get("requires_for") or "")
          and swaps[0]["payload"].get("missing") == ["chat-9b-fp8"])

    # (d) DEDUP — a second gate call for the same loadout still raises but does NOT double-surface.
    try:
        suite._gate_work_requires("cascade «needs9b-again»", "quality-9b")
    except GovernanceError:
        pass
    swaps2 = [d for d in suite.inbox.list()
              if d.get("action") == "loadout_swap" and (d.get("payload") or {}).get("loadout_class") == "quality-9b"]
    check("a pending swap is NOT re-surfaced (dedup) — still exactly one", len(swaps2) == 1)

    # (e) unknown combo → ValueError (registry-is-truth, fail loud).
    _state["raise"] = True
    verr = False
    try:
        suite._gate_work_requires("cascade «bad»", "no-such-loadout")
    except ValueError:
        verr = True
    check("an unknown required combo raises ValueError (fail loud)", verr)
    _state["raise"] = False

    # ---- 3. run_cascade INVOKES the gate (a missing-loadout cascade fails loud before any step) --------
    _state["missing"] = ["chat-9b-fp8"]
    suite.cascade_registry.get = lambda name: {"name": name, "steps": [{"op": "run", "role": "judge"}],
                                               "requires": "quality-9b"}   # stub a saved cascade with requires
    gated = False
    try:
        suite.run_cascade("anything")
    except GovernanceError:
        gated = True
    check("run_cascade fires the requires-gate (missing loadout → GovernanceError before any step)", gated)

    print(f"\nPASS — {PASS}/{PASS} action-requires gate checks")
finally:
    import shutil
    shutil.rmtree(store_dir, ignore_errors=True)
