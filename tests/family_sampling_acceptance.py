"""tests/family_sampling_acceptance.py — PER-FAMILY default sampling (the USE-side capability spine).

A model FAMILY declares its recommended sampling (think/no-think profiles) ONCE in
family_capabilities.json; at call-time the chat path + run_role resolve model→family→profile and lay it as
the per-request BASE UNDER per-role knobs + per-call kwargs (override wins). This dissolves "every Qwen3.5
thinking role re-declares the same numbers (and they're wrong on a kimi role)" — each model gets ITS
family's sampling automatically. Tim's "Both": per-family defaults + per-role override.

Checks:
  1. resolver.family_sampling — qwen3.5 default vs thinking; unknown family → {}; a no-`sampling` family → {}.
  2. capabilities.sampling_profile_for — the local FP8 4B → qwen3.5 profile (think-aware); a cloud model → {}.
  3. run_role END-TO-END (real request body capture):
     - a 4B role, NO knobs, think=True → the THINKING profile reaches the body (temp 1.0/top_p 0.95/top_k 20);
     - a 4B role, NO knobs, think OFF → the family SAMPLERS reach the body BUT temperature STAYS 0.0
       (the deterministic-swarm guard — family default temp does NOT override the routing-stable default);
     - a role-declared knob WINS over the family base (top_p), family fills the rest (top_k);
     - an explicit temperature kwarg WINS over the family thinking temp;
     - a cloud/non-family model → NO family base (byte-identical: temp 0.0, no top_p)."""
from __future__ import annotations
import json, os, sys, urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ops", "cli"))

from runtime.capabilities import resolver
import capabilities as caps
from runtime import cognition
from runtime.roles import Role
from pydantic import BaseModel

FP8 = "RedHatAI/Qwen3.5-4B-FP8-dynamic"
PASS = 0
FAIL = []


def check(label, cond):
    global PASS
    if cond:
        PASS += 1; print(f"  ok  {label}")
    else:
        FAIL.append(label); print(f"  XX  {label}")


# 1. resolver.family_sampling
d = resolver.family_sampling("qwen3.5", thinking=False)
t = resolver.family_sampling("qwen3.5", thinking=True)
check("qwen3.5 default profile = 0.7/0.8/20", d.get("temperature") == 0.7 and d.get("top_p") == 0.8 and d.get("top_k") == 20)
check("qwen3.5 thinking profile = 1.0/0.95/20", t.get("temperature") == 1.0 and t.get("top_p") == 0.95 and t.get("top_k") == 20)
check("unknown family → {} (additive, no raise)", resolver.family_sampling("no-such") == {})
check("a family with no `sampling` → {} (nemotron)", resolver.family_sampling("nemotron") == {})

# 2. the model→family→profile join
check("the local FP8 4B resolves to the qwen3.5 thinking profile",
      caps.sampling_profile_for(FP8, thinking=True).get("temperature") == 1.0)
check("a cloud model (kimi) resolves to NO family profile ({})",
      caps.sampling_profile_for("kimi-k2.6:cloud", thinking=True) == {})


class _Out(BaseModel):
    text: str = "ok"


def _role(knobs=None):
    spec = {"id": "fstest"}
    if knobs is not None:
        spec["knobs"] = knobs
    return Role(id="fstest", prompt_template='Reply ONLY JSON {"text":"ok"}', output_schema=_Out, spec=spec)


def _body(role, **run_kwargs):
    cap = {}
    real = urllib.request.urlopen

    class _R:
        def read(self):
            return json.dumps({"choices": [{"finish_reason": "stop",
                               "message": {"role": "assistant", "content": '{"text":"ok"}'}}],
                               "usage": {"total_tokens": 3}}).encode()
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def fake(req, timeout=None):
        cap["body"] = json.loads(req.data.decode()); return _R()

    urllib.request.urlopen = fake
    try:
        cognition.run_role(role, {"utterance": "hi"}, model=FP8, **run_kwargs)
    finally:
        urllib.request.urlopen = real
    return cap["body"]


# 3a. 4B role, no knobs, think=True → THINKING profile reaches the body
bt = _body(_role(), think=True)
check("think=True 4B role (no knobs) → temperature 1.0 (family thinking profile)", bt.get("temperature") == 1.0)
check("think=True 4B role → top_p 0.95 + top_k 20 (family thinking samplers)",
      bt.get("top_p") == 0.95 and bt.get("top_k") == 20)

# 3b. 4B role, no knobs, think OFF → samplers apply BUT temperature STAYS 0.0 (determinism guard)
bn = _body(_role(), think=False)
check("think=False 4B role → temperature STAYS 0.0 (deterministic swarm preserved, NOT the family 0.7)",
      bn.get("temperature") == 0.0)
check("think=False 4B role → family samplers still ride (top_p 0.8 / top_k 20 — harmless at temp 0)",
      bn.get("top_p") == 0.8 and bn.get("top_k") == 20)

# 3c. role-declared knob WINS over the family base; family fills the rest
br = _body(_role({"top_p": 0.5}), think=True)
check("role-declared top_p 0.5 WINS over the family thinking top_p 0.95", br.get("top_p") == 0.5)
check("family still fills top_k 20 where the role is silent", br.get("top_k") == 20)

# 3d. explicit temperature kwarg WINS over the family thinking temp
be = _body(_role(), think=True, temperature=0.2)
check("explicit temperature kwarg 0.2 WINS over the family thinking temp 1.0", be.get("temperature") == 0.2)

# 3e. a cloud/non-family model → NO family base (byte-identical)
def _body_cloud(role, **kw):
    cap = {}
    real = urllib.request.urlopen
    class _R:
        def read(self): return json.dumps({"choices":[{"finish_reason":"stop","message":{"content":'{"text":"ok"}'}}],"usage":{"total_tokens":3}}).encode()
        def __enter__(self): return self
        def __exit__(self,*a): return False
    def fake(req, timeout=None):
        cap["body"] = json.loads(req.data.decode()); return _R()
    urllib.request.urlopen = fake
    try:
        cognition.run_role(role, {"utterance":"hi"}, model="some-cloud-model:cloud", base_url="http://127.0.0.1:11434/v1", **kw)
    finally:
        urllib.request.urlopen = real
    return cap["body"]

bc = _body_cloud(_role())
check("a non-family (cloud) model → temperature 0.0 (byte-identical, no family base)", bc.get("temperature") == 0.0)
check("a non-family (cloud) model → NO top_p key (byte-identical)", "top_p" not in bc)

print(f"\n{'='*56}\nPASSED {PASS} · FAILED {len(FAIL)}")
if FAIL:
    for f in FAIL:
        print(f"  FAILED: {f}")
    sys.exit(1)
print("ALL CHECKS PASS — per-family sampling base, per-role/per-call override")
