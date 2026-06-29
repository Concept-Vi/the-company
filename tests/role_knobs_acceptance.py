"""tests/role_knobs_acceptance.py — PER-ROLE SAMPLING reaches the model (run_role applies role.knobs).

run_role previously forwarded ONLY the temperature/max_tokens kwargs, so a role's DECLARED knobs
(top_p/top_k/min_p/presence_penalty/… in roles/<id>.py `spec["knobs"]`) were a SILENT NO-OP — a thinking
role wanting the Qwen3.5 thinking sampling (temp 1.0 / top_p 0.95 / top_k 20) ran on default sampling. This
closes that gap. Proven by capturing the REAL request body run_role issues (monkeypatch urllib.request.urlopen
inside fabric.transport — the SHIPPED transport builds + "sends" the body), so green = the real path forwards.

Checks:
  1. a role declaring spec.knobs {temp 1.0, top_p 0.95, top_k 20} → ALL reach the request body;
  2. BYTE-IDENTICAL: a role with NO knobs + no explicit temperature → temperature 0.0, NO top_p/top_k key;
  3. PRECEDENCE: an explicitly-passed temperature kwarg WINS over the role's knob (jury varied-draws safe);
  4. max_tokens from role.knobs applies when the caller passes none;
  5. O2 ladder path: the role's other samplers (top_p) ride alongside the ladder's repetition_penalty, and
     the ladder still OWNS repetition_penalty (the role's is not double-passed)."""
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


def _role(spec_extra=None):
    spec = {"id": "ktest"}
    if spec_extra:
        spec.update(spec_extra)
    return Role(id="ktest", prompt_template='Reply ONLY JSON {"text":"ok"}', output_schema=_Out, spec=spec)


def _capture_run_role(role, **run_kwargs):
    """Run run_role with urlopen patched inside fabric.transport; return the request body dict the SHIPPED
    transport would send (network-free — a canned conformant envelope so the call completes cleanly)."""
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
        cap["body"] = json.loads(req.data.decode())
        return _R()

    urllib.request.urlopen = fake
    try:
        cognition.run_role(role, {"utterance": "hi"}, **run_kwargs)
    finally:
        urllib.request.urlopen = real
    return cap["body"]


# 1. role.knobs reach the body
b = _capture_run_role(_role({"knobs": {"temperature": 1.0, "top_p": 0.95, "top_k": 20}}))
check("role.knobs temperature 1.0 reaches the request body", b.get("temperature") == 1.0)
check("role.knobs top_p 0.95 reaches the request body", b.get("top_p") == 0.95)
check("role.knobs top_k 20 reaches the request body", b.get("top_k") == 20)

# 2. byte-identical: no knobs, no explicit temperature → temp 0.0, NO top_p/top_k
bn = _capture_run_role(_role())
check("no-knobs role → temperature falls back to 0.0 (byte-identical)", bn.get("temperature") == 0.0)
check("no-knobs role → NO top_p key in the body (additive, nothing leaked)", "top_p" not in bn)
check("no-knobs role → NO top_k key in the body", "top_k" not in bn)
check("no-knobs role → max_tokens falls back to 256", bn.get("max_tokens") == 256)

# 3. precedence: an explicit temperature kwarg WINS over the role's knob (jury varied-draws safe)
bp = _capture_run_role(_role({"knobs": {"temperature": 1.0}}), temperature=0.3)
check("explicit temperature kwarg (0.3) WINS over role.knobs temperature (1.0)", bp.get("temperature") == 0.3)

# 4. max_tokens from role.knobs applies when the caller passes none
bm = _capture_run_role(_role({"knobs": {"max_tokens": 4096}}))
check("role.knobs max_tokens 4096 applies when no explicit kwarg", bm.get("max_tokens") == 4096)

# 5. O2 ladder path: the role's other samplers ride alongside the ladder's repetition_penalty
reg = cognition.generation_policy_registry()
rung = reg.policy_for("prose_default").default_rep_penalty
bl = _capture_run_role(_role({"knobs": {"top_p": 0.9, "repetition_penalty": 1.9}}), policy="prose_default")
check("O2 path: the role's top_p 0.9 rides alongside the ladder", bl.get("top_p") == 0.9)
check("O2 path: the LADDER owns repetition_penalty (the rung, not the role's 1.9)",
      bl.get("repetition_penalty") == rung)

print(f"\n{'='*56}\nPASSED {PASS} · FAILED {len(FAIL)}")
if FAIL:
    for f in FAIL:
        print(f"  FAILED: {f}")
    sys.exit(1)
print("ALL CHECKS PASS — per-role sampling reaches the model")
