"""tests/active_brain_resolution_acceptance.py — the resident-brain SENTINEL resolves to the ACTIVE loaded brain.

THE GAP (found live): cognition.RESIDENT_BASE_URL/RESIDENT_MODEL hardcoded :8000/AWQ, but the FP8 loadout
serves the brain on :8001 (AWQ :8000 down). So bare run_role / the swarm defaulted to a DEAD port. THE
ARCHITECTURE (Tim): "whatever the active loaded brain is should work for whatever uses it." RESIDENT_* is now
a SENTINEL — run_role resolves it at call-time to active_brain() (the RUNNING local brain service), so the
whole cognition layer follows the live loadout, the SAME brain the RHM uses.

Checks (run_role's request captured via the SHIPPED transport — urlopen patched inside fabric.transport):
  1. run_role with the SENTINEL default → the request hits active_brain()'s base_url + model;
  2. an EXPLICIT base_url/model (a role binding, a cloud model) is used VERBATIM (NOT resolved);
  3. an explicit model + sentinel base → base resolves to active, model kept (the mixed case from the live MCP);
  4. active_brain() live → returns a (model, base_url/v1) pair (smoke: the resolver reads the registry, never raises)."""
from __future__ import annotations
import json, os, sys, urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runtime import cognition
from runtime.roles import Role
from pydantic import BaseModel

PASS = 0
FAIL = []


def check(label, cond):
    global PASS
    if cond:
        PASS += 1; print(f"  ok  {label}")
    else:
        FAIL.append(label); print(f"  XX  {label}")


class _Out(BaseModel):
    text: str = "ok"


def _role():
    return Role(id="abr", prompt_template='Reply ONLY JSON {"text":"ok"}', output_schema=_Out, spec={"id": "abr"})


def _capture(**run_kwargs):
    cap = {}
    real = urllib.request.urlopen

    class _R:
        def read(self):
            return json.dumps({"choices": [{"finish_reason": "stop", "message": {"content": '{"text":"ok"}'}}],
                               "usage": {"total_tokens": 3}}).encode()
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def fake(req, timeout=None):
        cap["url"] = req.full_url
        cap["model"] = json.loads(req.data.decode()).get("model")
        return _R()

    urllib.request.urlopen = fake
    try:
        cognition.run_role(_role(), {"utterance": "hi"}, **run_kwargs)
    finally:
        urllib.request.urlopen = real
    return cap


# mock active_brain to a KNOWN pair so the resolution is hermetic (independent of what's live).
_orig_active = cognition.active_brain
cognition.active_brain = lambda: ("test/active-model", "http://127.0.0.1:9991/v1")
try:
    # 1. sentinel default → resolves to active_brain()
    c1 = _capture()
    check("sentinel-default run_role resolves base_url → active_brain (:9991)", ":9991" in c1["url"])
    check("sentinel-default run_role resolves model → active_brain (test/active-model)",
          c1["model"] == "test/active-model")

    # 2. explicit base_url + model (a binding / cloud) → used VERBATIM, NOT resolved
    c2 = _capture(base_url="http://127.0.0.1:11434/v1", model="kimi-k2.6:cloud")
    check("explicit base_url is used verbatim (NOT resolved to active)", ":11434" in c2["url"])
    check("explicit model is used verbatim (NOT resolved to active)", c2["model"] == "kimi-k2.6:cloud")

    # 3. explicit model + SENTINEL base (the live-MCP mixed case) → base resolves, model kept
    c3 = _capture(model="some/explicit-model")
    check("mixed: sentinel base resolves to active (:9991)", ":9991" in c3["url"])
    check("mixed: explicit model is kept (not overwritten by active)", c3["model"] == "some/explicit-model")
finally:
    cognition.active_brain = _orig_active

# 4. active_brain() live smoke — reads the registry, returns a (model, base/v1) pair, never raises
m, b = cognition.active_brain()
check("active_brain() returns a non-empty model + a /v1 base_url (live, no raise)",
      isinstance(m, str) and m and isinstance(b, str) and b.endswith("/v1"))

print(f"\n{'='*56}\nPASSED {PASS} · FAILED {len(FAIL)}")
if FAIL:
    for f in FAIL:
        print(f"  FAILED: {f}")
    sys.exit(1)
print("ALL CHECKS PASS — the resident-brain sentinel follows the active loaded brain")
