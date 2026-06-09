"""tests/generation_policy_ladder_acceptance.py — Cognition Engine O2 (the rep_penalty LADDER wired into
run_role, NOTHING static).

Proves, by USE (a fake transport-level `client.complete` that RECORDS opts + drives finish_reason):

  O2.1  run_role(policy=None) is BYTE-IDENTICAL to before — no repetition_penalty, no meta read, ONE call.
  O2.2  run_role(policy=<id>) reads the rep_penalty value FROM THE REGISTRY LADDER (registry-is-truth —
        the value is the policy's default rung, NEVER a code constant). [the "observe the param" verify]
  O2.3  finish_reason=="length" ESCALATES to the next ladder rung (the degenerate-loop signal climbs).
  O2.4  EXHAUSTING the ladder (every rung returns finish=length) FAILS LOUD with `degenerate-loop`
        (never a silent give-up — the regime's own contract).
  O2.5  an UNKNOWN policy id FAILS LOUD (registry-is-truth — a regime that is not a discovered file
        does not exist).

KNOWN/FLAGGED (asserted as a NOTE, not green): the real `fabric/transport.py` does NOT yet forward
`repetition_penalty` into the request body (it copies only temperature/max_tokens/top_p), so the penalty
does not reach vLLM until that one-line passthrough lands (the coordinate-with-owner follow-up). This
test proves the LADDER LOGIC + the registry-sourced VALUE + the escalation + the fail-loud exhaustion —
all real and verifiable here; the param's EFFECT on the model is gated on the transport edit.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from runtime import cognition
from runtime.roles import Role
from pydantic import BaseModel

PASS = 0
ok = True


def check(label, cond):
    global PASS, ok
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        ok = False
        print(f"  FAIL  {label}")


# A trivial fireable role (a prompt + a one-field schema) — the SAME shape run_swarm/dry_run_role fire.
class _Out(BaseModel):
    text: str = "ok"


ROLE = Role(id="laddertest", prompt_template="echo", output_schema=_Out,
            spec={"id": "laddertest", "prompt_template": "echo", "output_schema": _Out})

# The seeded capture_default policy: ladder [1.1, 1.2], so default=1.1, next(1.1)=1.2, next(1.2)=None.
POLICY = "capture_default"
_reg = cognition.generation_policy_registry()
assert POLICY in _reg, f"seed policy {POLICY!r} missing — registered: {sorted(_reg)}"
LADDER = _reg.policy_for(POLICY).rep_penalty_ladder
print(f"\n[setup] policy {POLICY!r} ladder = {LADDER} (from the file-discovered registry, not a constant)")


# --- a fake client.complete: mimics the real signature (transport, messages, model, schema, **opts),
# RECORDS the repetition_penalty + meta it was handed, and drives finish_reason via the `meta` out-param. ---
_orig_complete = cognition.client.complete


def _fake_factory(finish_seq):
    """Build a fake complete() that returns finish_reason from `finish_seq` per call (then 'stop')."""
    calls = []

    def _fake(transport, messages, model, schema=None, **opts):
        i = len(calls)
        fr = finish_seq[i] if i < len(finish_seq) else "stop"
        meta = opts.get("meta")
        if meta is not None:
            meta["finish_reason"] = fr          # the O3 out-param the transport would fill
        calls.append({"rep_penalty": opts.get("repetition_penalty"),
                      "temperature": opts.get("temperature"),
                      "had_meta": meta is not None})
        return schema(text="ok") if schema is not None else "ok"

    _fake.calls = calls
    return _fake


# ── O2.1 — policy=None is byte-identical (no rep_penalty, no meta) ────────────────────────────────
print("\n[O2.1] policy=None → byte-identical (no repetition_penalty, no meta read, ONE call)")
fake = _fake_factory([])
cognition.client.complete = fake
try:
    out = cognition.run_role(ROLE, {"utterance": "hi"})           # NO policy
finally:
    cognition.client.complete = _orig_complete
check("O2.1 policy=None made exactly ONE complete() call", len(fake.calls) == 1)
check("O2.1 policy=None passed NO repetition_penalty (byte-identical default path)",
      fake.calls[0]["rep_penalty"] is None)
check("O2.1 policy=None passed NO meta out-param (no finish_reason read on the default path)",
      fake.calls[0]["had_meta"] is False)
check("O2.1 policy=None returns the validated dict", isinstance(out, dict) and out.get("text") == "ok")

# ── O2.2 — policy=<id> uses the rep_penalty FROM THE REGISTRY LADDER (clean finish, one call) ──────
print("\n[O2.2] policy set → repetition_penalty == the registry ladder default (registry-is-truth)")
fake = _fake_factory(["stop"])
cognition.client.complete = fake
try:
    out = cognition.run_role(ROLE, {"utterance": "hi"}, policy=POLICY)
finally:
    cognition.client.complete = _orig_complete
check("O2.2 a clean finish made ONE call", len(fake.calls) == 1)
check(f"O2.2 the repetition_penalty == the ladder DEFAULT ({LADDER[0]}) — FROM THE REGISTRY, not a constant",
      fake.calls[0]["rep_penalty"] == LADDER[0])
check("O2.2 the call carried a meta out-param (finish_reason is read to drive escalation)",
      fake.calls[0]["had_meta"] is True)

# ── O2.3 — finish=length ESCALATES to the next ladder rung ────────────────────────────────────────
print("\n[O2.3] finish_reason='length' escalates to the NEXT ladder rung")
fake = _fake_factory(["length", "stop"])   # first call truncates → escalate → second is clean
cognition.client.complete = fake
try:
    out = cognition.run_role(ROLE, {"utterance": "hi"}, policy=POLICY)
finally:
    cognition.client.complete = _orig_complete
check("O2.3 finish=length drove a SECOND call (escalation, not a give-up)", len(fake.calls) == 2)
check(f"O2.3 call-1 used the default rung ({LADDER[0]})", fake.calls[0]["rep_penalty"] == LADDER[0])
check(f"O2.3 call-2 CLIMBED to the next rung ({LADDER[1]}) — the ladder escalated on finish=length",
      fake.calls[1]["rep_penalty"] == LADDER[1])
check("O2.3 the clean second draw is returned", isinstance(out, dict) and out.get("text") == "ok")

# ── O2.4 — exhausting the ladder FAILS LOUD (degenerate-loop) ─────────────────────────────────────
print("\n[O2.4] every rung finish=length → ladder EXHAUSTED → fail-loud degenerate-loop")
fake = _fake_factory(["length"] * 10)       # every draw truncates → never clean → exhaust
cognition.client.complete = fake
raised_msg = None
try:
    cognition.run_role(ROLE, {"utterance": "hi"}, policy=POLICY)
except Exception as e:
    raised_msg = str(e)
finally:
    cognition.client.complete = _orig_complete
check("O2.4 an exhausted ladder RAISED (never a silent give-up)", raised_msg is not None)
check("O2.4 the error is a degenerate-loop fail-loud (names the pathology)",
      raised_msg is not None and "degenerate-loop" in raised_msg)
check(f"O2.4 it climbed the WHOLE ladder before raising ({len(LADDER)} rungs tried)",
      len(fake.calls) == len(LADDER))
check("O2.4 the rungs tried are EXACTLY the ladder (registry-driven escalation, in order)",
      [c["rep_penalty"] for c in fake.calls] == list(LADDER))

# ── O2.5 — an unknown policy id FAILS LOUD (registry-is-truth) ────────────────────────────────────
print("\n[O2.5] an unknown policy id → fail loud (registry-is-truth)")
raised = False
try:
    cognition.run_role(ROLE, {"utterance": "hi"}, policy="not_a_real_policy")
except Exception as e:
    raised = "unknown generation-policy" in str(e) or "not_a_real_policy" in str(e)
check("O2.5 run_role(policy=<unknown>) RAISES (a regime that is not a discovered file does not exist)",
      raised)

# ── TRANSPORT PASSTHROUGH NOW CLOSED (FABRIC-2): the rep_penalty value REACHES vLLM ───────────────
# WAS: a NOTE asserting the transport copied ONLY temperature/max_tokens/top_p (the gap WIRING flagged).
# The FABRIC-2 lane added a single-source sampling passthrough (`_apply_sampling` over `_SAMPLING_KEYS`)
# called by BOTH chat transports, so the ladder rung now lands in the request body. We prove it
# BEHAVIOURALLY against the REAL transport (capture the bytes it would send) — NOT by string-matching its
# source (which a single-sourced helper would defeat). The ladder→model EFFECT is now end-to-end.
print("\n[TRANSPORT] the rep_penalty ladder VALUE now reaches vLLM — the passthrough closed (FABRIC-2).")
import json as _json
import urllib.request as _urlreq


class _FakeR:
    def __init__(self, b): self._b = b
    def read(self): return self._b
    def __enter__(self): return self
    def __exit__(self, *a): return False


_cap = {}
_real_uo = _urlreq.urlopen


def _fake_uo(req, timeout=None):
    _cap["body"] = _json.loads(req.data.decode())
    return _FakeR(_json.dumps({"choices": [{"finish_reason": "stop",
                  "message": {"role": "assistant", "content": "hi"}}]}).encode())


_urlreq.urlopen = _fake_uo
try:
    _t = cognition.transport.openai_transport()
    _t("m", [{"role": "user", "content": "hi"}], repetition_penalty=1.2, temperature=0.0, max_tokens=8)
finally:
    _urlreq.urlopen = _real_uo
check("TRANSPORT confirmed: the live openai_transport now FORWARDS repetition_penalty into the request "
      "body (the ladder→model effect is end-to-end; was the flagged cross-lane gap, now closed)",
      _cap.get("body", {}).get("repetition_penalty") == 1.2)

_cap2 = {}
_urlreq.urlopen = lambda req, timeout=None: (_cap2.__setitem__("body", _json.loads(req.data.decode())),
    _FakeR(_json.dumps({"choices": [{"finish_reason": "stop",
        "message": {"role": "assistant", "content": "hi"}}]}).encode()))[1]
try:
    cognition.transport.openai_transport()("m", [{"role": "user", "content": "hi"}], temperature=0.0, max_tokens=8)
finally:
    _urlreq.urlopen = _real_uo
check("TRANSPORT byte-identical: a call WITHOUT repetition_penalty leaves it OUT of the body (additive — "
      "absent → unchanged; the passthrough is behaviour-preserving)",
      "repetition_penalty" not in _cap2.get("body", {}))

print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {PASS} checks passed — O2: run_role reads the "
      "rep_penalty LADDER from the file-discovered generation-policy registry (NOTHING static); escalates "
      "on finish=length; fails loud degenerate-loop on exhaustion; unknown policy fails loud. The transport "
      "passthrough is the flagged cross-lane follow-up.")
sys.exit(0 if ok else 1)
