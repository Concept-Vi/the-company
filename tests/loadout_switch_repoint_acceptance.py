#!/usr/bin/env python3
"""Acceptance — the ATOMIC loadout switch repoints (and verifies + reverts) the RHM brain.

The gap this closes (loadout-resolution design, part 3): apply_loadout used to evict+start a loadout's
services but NEVER repoint the RHM brain → the RHM stayed pointed at the just-evicted brain = a broken brain.
These checks prove the wire (suite._repoint_rhm_for_loadout, called from apply_loadout):
  • finds the loadout's OWN brain (registry group:brain ∩ the loadout's services — not brain_keys[0]);
  • repoints the RHM to that brain's model + local endpoint, after a live verify probe;
  • reverts to the prior brain (and fails loud) when the new brain does not answer;
  • no-ops on a tool-only loadout; fails loud on an ambiguous (>1 brain) loadout.

The REAL services registry is used (registry.load()) so the model-ids/ports are ground truth; the live
inference probe + ensure_resident are mocked (hermetic — never touches the running :8001/:8002 or VRAM)."""

import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "ops", "cli"))

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
import registry as svc_registry      # the ops/cli SERVICES registry (services.json) — ground truth
import capabilities as caps          # the module _repoint_rhm_for_loadout imports as _cap (same cached object)

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


store_dir = tempfile.mkdtemp(prefix="loadout-repoint-test-")
reg = svc_registry.load()
svcs = reg["services"]
combos = svc_registry.combos(reg)

# Ground-truth the registry rows the checks assert against (registry-is-truth; if these move, the test
# should move with them, never the other way).
FP8_4B = svcs["chat-4b-fp8"]["config"]["model"]      # RedHatAI/Qwen3.5-4B-FP8-dynamic
FP8_9B = svcs["chat-9b-fp8"]["config"]["model"]      # RedHatAI/Qwen3.5-9B-FP8-dynamic
EP_4B = "http://127.0.0.1:8001/v1"
EP_9B = "http://127.0.0.1:8002/v1"

# concrete service lists (resolve the combos so the test rides the SAME resolver the system does)
INTERACTION_FP8 = list(combos["interaction-fp8"]["services"])   # has chat-4b-fp8, embed, ear, voice
QUALITY_9B = list(combos["quality-9b"]["services"])             # [chat-9b-fp8] solo

# ---- mock seams: the live probe + the loader (hermetic — no real service start, no VRAM) --------------
_orig_probe = caps._probe_tools
_orig_ensure = caps.ensure_resident
_probe_returns = {"v": True}                       # flip per-test: True/False = alive, None = dead
caps._probe_tools = lambda *a, **k: _probe_returns["v"]
caps.ensure_resident = lambda *a, **k: {"resident": True, "action": "noop(mock)"}

try:
    store = FsStore(os.path.join(store_dir, "store"))
    nreg = NodeRegistry(); nreg.discover([NODES])
    suite = Suite(store, nreg, nodes_dir=NODES)

    # ---- 1. the brain-in-loadout join: the loadout's OWN brain, not the registry's first brain ---------
    b = suite._brain_in_loadout(INTERACTION_FP8, reg)
    check("interaction-fp8's brain resolves to exactly [chat-4b-fp8]", b == ["chat-4b-fp8"])
    check("quality-9b's brain resolves to exactly [chat-9b-fp8]",
          suite._brain_in_loadout(QUALITY_9B, reg) == ["chat-9b-fp8"])
    check("a tool-only service list resolves to NO brain",
          suite._brain_in_loadout(["embed-pplx", "tts-kokoro"], reg) == [])

    # ---- 2. repoint to the loadout's brain (interaction-fp8 → the FP8-4B @ :8001) -----------------------
    _probe_returns["v"] = True
    suite.set_rhm_config({"model": "sentinel/prior", "base_url": "http://127.0.0.1:9999/v1"})
    rep = suite._repoint_rhm_for_loadout(INTERACTION_FP8, reg,
                                         prior={"model": "sentinel/prior", "base_url": "http://127.0.0.1:9999/v1"})
    check("interaction-fp8 repoint reports the FP8-4B", rep.get("repointed") and rep.get("model") == FP8_4B)
    check("interaction-fp8 repoint uses the :8001 endpoint", rep.get("base_url") == EP_4B)
    check("RHM config now POINTS at the FP8-4B (the live config moved)",
          suite.rhm_config().get("model") == FP8_4B and suite.rhm_config().get("base_url") == EP_4B)

    # ---- 3. repoint to a DIFFERENT brain (quality-9b → the FP8-9B @ :8002) ------------------------------
    _probe_returns["v"] = True
    rep9 = suite._repoint_rhm_for_loadout(QUALITY_9B, reg, prior={"model": FP8_4B, "base_url": EP_4B})
    check("quality-9b repoint reports the FP8-9B @ :8002",
          rep9.get("model") == FP8_9B and rep9.get("base_url") == EP_9B)
    check("RHM config now POINTS at the FP8-9B (switch followed the loadout)",
          suite.rhm_config().get("model") == FP8_9B)

    # ---- 4. tool-only loadout → no repoint, pointer unchanged ------------------------------------------
    before = suite.rhm_config().get("model")
    rep0 = suite._repoint_rhm_for_loadout(["embed-pplx", "tts-kokoro"], reg)
    check("tool-only loadout does NOT repoint", rep0.get("repointed") is False)
    check("tool-only loadout leaves the RHM pointer UNCHANGED", suite.rhm_config().get("model") == before)

    # ---- 5. verify-by-use FAILS → revert to prior + fail loud (no silent broken brain) -----------------
    # Put the RHM on the 9B, then attempt a switch to the 4B whose probe comes back DEAD; expect a loud
    # raise AND the pointer reverted to the prior 9B (the revert anchor), never left on the dead 4B.
    suite.set_rhm_config({"model": FP8_9B, "base_url": EP_9B})
    _probe_returns["v"] = None                      # the NEW brain does not answer
    raised = False
    try:
        suite._repoint_rhm_for_loadout(INTERACTION_FP8, reg, prior={"model": FP8_9B, "base_url": EP_9B})
    except caps.EnsureResidentError:
        raised = True
    check("a dead new brain FAILS LOUD (EnsureResidentError)", raised)
    check("after a failed switch the RHM is REVERTED to the prior brain (not left on the dead one)",
          suite.rhm_config().get("model") == FP8_9B)

    # ---- 6. an ambiguous loadout (>1 brain) fails loud -------------------------------------------------
    _probe_returns["v"] = True
    amb = False
    try:
        suite._repoint_rhm_for_loadout(["chat-4b-fp8", "chat-9b-fp8"], reg)
    except ValueError:
        amb = True
    check("a loadout naming >1 brain fails loud (ambiguous)", amb)

    print(f"\nPASS — {PASS}/{PASS} loadout-switch repoint checks")
finally:
    caps._probe_tools = _orig_probe
    caps.ensure_resident = _orig_ensure
    import shutil
    shutil.rmtree(store_dir, ignore_errors=True)
