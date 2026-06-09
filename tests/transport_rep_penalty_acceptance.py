"""tests/transport_rep_penalty_acceptance.py — the sampling-family passthrough (FABRIC-2 · completes O2's
model EFFECT).

WIRING built the generation-policy rep_penalty LADDER in run_role(policy=) — it computes the right
`repetition_penalty` from the registry rung. But fabric/transport.py only forwarded temperature/max_tokens/
top_p, so the computed `repetition_penalty` never reached vLLM. This lane added a SINGLE-SOURCE sampling
passthrough (`_apply_sampling` over the `_SAMPLING_KEYS` allowlist) called by BOTH chat transports, so the
ladder's value now reaches the model.

PROVES, by exercising the REAL transport (NOT a reimplementation — monkeypatches urllib.request.urlopen
INSIDE fabric.transport to capture the EXACT bytes that openai_transport / openai_tools_transport would
send), so a green here is proof the SHIPPED transport forwards the key, not proof that a test copy does:

  1. NEGATIVE CONTROL / forward proof: `repetition_penalty` passed → it lands in the request body, on BOTH
     openai_transport AND openai_tools_transport (the two paths the brief names).
  2. BYTE-IDENTICAL: a call WITHOUT repetition_penalty produces a body with NO repetition_penalty key (the
     behaviour-preserving guarantee — additive, absent → unchanged). The original three (temperature/
     max_tokens/top_p) still forward exactly as before.
  3. ALLOWLIST, not denylist: the out-params + structured-output triggers (`meta`/`tools`/`json_schema`/
     `schema`/`json`) NEVER appear as body keys via the sampling path (they are handled by
     _apply_response_format / _fill_meta / the tools branch, and are NOT in _SAMPLING_KEYS). This protects
     the meta-no-leak guarantee _fill_meta documents.
  4. THE WHOLE FAMILY rides the one seam: a policy declaring frequency_penalty/presence_penalty/top_k/min_p/
     stop/seed/n reaches the body too (registry-driven/general, not a single hardcoded key).
  5. BY USE (live :8000 resident 4B, read-only — no load/evict): a REAL request carrying
     repetition_penalty returns HTTP 200 with content (vLLM ACCEPTS it as a valid sampling param).
  6. END-TO-END (the point of this lane): run_role(policy='prose_default') — the ladder path — now drives a
     real call whose request body carries the registry rung as repetition_penalty (the ladder→model effect,
     previously gated on this passthrough). Proven via the same urlopen capture.

Run: /home/tim/company/.venv/bin/python tests/transport_rep_penalty_acceptance.py
The live checks need the resident 4B UP at :8000 (read-only USE). DOWN → reported SKIPPED (fail-loud
distinction), the capture checks (the real proof of the passthrough) still run.
"""
from __future__ import annotations
import io
import json
import os
import sys
import urllib.request

# self-bootstrap the repo root onto sys.path (every acceptance suite does this) so it runs standalone.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fabric import transport

RESIDENT_BASE_URL = "http://127.0.0.1:8000/v1"
RESIDENT_MODEL = "cyankiwi/Qwen3.5-4B-AWQ-4bit"

_passed = []
_failed = []


def ok(name):
    _passed.append(name); print(f"  ok  {name}")


def bad(name, why):
    _failed.append((name, why)); print(f"  XX  {name} — {why}")


# ---------------------------------------------------------------------------------------------------
# The real-transport body capturer. We monkeypatch urllib.request.urlopen INSIDE fabric.transport so
# the REAL openai_transport / openai_tools_transport build + "send" their body; we capture req.data
# (the exact JSON bytes that would hit the wire) and return a canned OpenAI envelope so the transport
# parses cleanly. This proves the SHIPPED transport forwards the key — not a reimplementation.
# ---------------------------------------------------------------------------------------------------
class _FakeResp:
    def __init__(self, payload: bytes):
        self._b = payload
    def read(self):
        return self._b
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False


def _capture(make_transport, *call_args, envelope=None, **call_kwargs):
    """Build a transport via `make_transport`, call it with the given args, return the sent body dict
    AND the raw sent bytes. Patches transport.urllib.request.urlopen so NO network happens — both are
    captured from req.data (raw bytes for the byte-identity proof; parsed dict for the shape proofs)."""
    captured = {}
    canned = json.dumps(envelope or {
        "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "hi"}}],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    }).encode()

    real_urlopen = urllib.request.urlopen

    def fake_urlopen(req, timeout=None):
        captured["raw"] = req.data
        captured["body"] = json.loads(req.data.decode())
        captured["url"] = req.full_url
        return _FakeResp(canned)

    urllib.request.urlopen = fake_urlopen
    try:
        t = make_transport()
        t(*call_args, **call_kwargs)
    finally:
        urllib.request.urlopen = real_urlopen
    return captured


# ---------------------------------------------------------------------------------------------------
# 1+2. NEGATIVE CONTROL (the param lands) + BYTE-IDENTICAL (absent → unchanged) — BOTH transports
# ---------------------------------------------------------------------------------------------------
def test_passthrough_both_paths():
    msgs = [{"role": "user", "content": "hi"}]

    # openai_transport — WITH repetition_penalty → it reaches the body
    body = _capture(lambda: transport.openai_transport(base_url=RESIDENT_BASE_URL),
                    RESIDENT_MODEL, msgs, repetition_penalty=1.2, temperature=0.0, max_tokens=8)["body"]
    if body.get("repetition_penalty") == 1.2:
        ok("openai_transport: repetition_penalty=1.2 LANDS in the sent request body (reaches vLLM)")
    else:
        bad("openai_transport: repetition_penalty forwarded", f"body={body!r}")
    # the original three still forward (unchanged)
    if body.get("temperature") == 0.0 and body.get("max_tokens") == 8:
        ok("openai_transport: temperature/max_tokens still forward (the original three unchanged)")
    else:
        bad("openai_transport: original keys", f"body={body!r}")

    # openai_tools_transport — WITH repetition_penalty → it reaches the body (the SECOND path)
    body_t = _capture(lambda: transport.openai_tools_transport(base_url=RESIDENT_BASE_URL),
                      RESIDENT_MODEL, msgs, repetition_penalty=1.15, temperature=0.0, max_tokens=8,
                      envelope={"choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "hi"}}]})["body"]
    if body_t.get("repetition_penalty") == 1.15:
        ok("openai_tools_transport: repetition_penalty=1.15 LANDS in the sent request body (the 2nd path)")
    else:
        bad("openai_tools_transport: repetition_penalty forwarded", f"body={body_t!r}")

    # BYTE-IDENTICAL — a call WITHOUT repetition_penalty produces NO such key (behaviour-preserving)
    cap_n = _capture(lambda: transport.openai_transport(base_url=RESIDENT_BASE_URL),
                     RESIDENT_MODEL, msgs, temperature=0.0, max_tokens=8)
    body_n = cap_n["body"]
    if "repetition_penalty" not in body_n:
        ok("byte-identical: a call WITHOUT repetition_penalty has NO repetition_penalty body key (additive)")
    else:
        bad("byte-identical: absent → unchanged", f"unexpected key in {body_n!r}")
    # the absent-rep_penalty body must be EXACTLY the pre-change shape (model/messages/stream + the 2 sampling keys)
    expected = {"model": RESIDENT_MODEL, "messages": msgs, "stream": False, "temperature": 0.0, "max_tokens": 8}
    if body_n == expected:
        ok("byte-identical: the no-rep_penalty body is EXACTLY the pre-change shape (nothing extra leaked)")
    else:
        bad("byte-identical: exact body", f"got {body_n!r} vs {expected!r}")
    # TRUE BYTE-IDENTITY (not dict-equality, which is order-insensitive): the RAW sent bytes must equal
    # the bytes the PRE-CHANGE inline `(temperature, max_tokens, top_p)` loop produced — same dict built
    # in the SAME key-insertion order. This is why _SAMPLING_KEYS is an ORDERED tuple with the three FIRST
    # (a hash-ordered frozenset would serialize these in a different order → same dict, different bytes).
    # the EXACT pre-change body: base keys, then the old loop's (temperature, max_tokens, top_p) order —
    # only temperature + max_tokens were passed, so top_p is omitted (as the old `if k in opts` did).
    pre_change = {"model": RESIDENT_MODEL, "messages": msgs, "stream": False,
                  "temperature": 0.0, "max_tokens": 8}
    pre_bytes = json.dumps(pre_change).encode()
    if cap_n["raw"] == pre_bytes:
        ok("byte-identical: the RAW sent bytes EQUAL the pre-change inline-loop bytes (key order preserved — "
           "literal byte-identity, not just dict-equality)")
    else:
        bad("byte-identical: raw bytes equal pre-change", f"got {cap_n['raw']!r} vs {pre_bytes!r}")

    # tools path WITHOUT repetition_penalty → also absent (additive on both paths)
    body_tn = _capture(lambda: transport.openai_tools_transport(base_url=RESIDENT_BASE_URL),
                       RESIDENT_MODEL, msgs, temperature=0.0, max_tokens=8,
                       envelope={"choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "hi"}}]})["body"]
    if "repetition_penalty" not in body_tn:
        ok("byte-identical: tools path WITHOUT repetition_penalty has no such key either")
    else:
        bad("byte-identical: tools absent", f"unexpected key in {body_tn!r}")


# ---------------------------------------------------------------------------------------------------
# 3. ALLOWLIST, not denylist — out-params + structured-output triggers must NOT leak into the body
# ---------------------------------------------------------------------------------------------------
def test_allowlist_no_leak():
    msgs = [{"role": "user", "content": "hi"}]
    meta = {}
    js = {"name": "x", "schema": {"type": "object", "properties": {}}}
    body = _capture(lambda: transport.openai_transport(base_url=RESIDENT_BASE_URL),
                    RESIDENT_MODEL, msgs, repetition_penalty=1.1, temperature=0.0,
                    meta=meta, json_schema=js, schema=object(), json=True)["body"]
    leaked = [k for k in ("meta", "json_schema", "schema", "json", "tools", "tool_choice") if k in body]
    if not leaked:
        ok("allowlist: meta/json_schema/schema/json/tools NEVER leak into the body via the sampling path")
    else:
        bad("allowlist: out-param leak", f"leaked {leaked} in {body!r}")
    # json_schema is still honored by _apply_response_format (it routes to response_format, not a body key)
    if body.get("response_format", {}).get("type") == "json_schema":
        ok("allowlist: json_schema still routes to response_format (handled by _apply_response_format, not leaked)")
    else:
        bad("allowlist: json_schema routing intact", f"response_format={body.get('response_format')!r}")
    # and meta was still filled (the O3 out-param works alongside the sampling passthrough)
    if meta.get("finish_reason") == "stop":
        ok("allowlist: meta out-param still filled (O3 unaffected by the sampling passthrough)")
    else:
        bad("allowlist: meta still filled", f"meta={meta!r}")


# ---------------------------------------------------------------------------------------------------
# 4. THE WHOLE FAMILY rides the one seam (registry-driven/general, not a single hardcoded key)
# ---------------------------------------------------------------------------------------------------
def test_family_rides_seam():
    msgs = [{"role": "user", "content": "hi"}]
    fam = {"frequency_penalty": 0.2, "presence_penalty": 0.1, "top_k": 40,
           "min_p": 0.05, "seed": 7, "n": 1, "stop": ["\n\n"]}
    body = _capture(lambda: transport.openai_transport(base_url=RESIDENT_BASE_URL),
                    RESIDENT_MODEL, msgs, **fam)["body"]
    missing = [k for k in fam if body.get(k) != fam[k]]
    if not missing:
        ok(f"family: the whole sampling family rides the SAME seam ({sorted(fam)}) — general, not one key")
    else:
        bad("family: whole family forwards", f"missing/wrong {missing} in {body!r}")
    # _SAMPLING_KEYS is the single source both transports iterate; an ORDERED tuple with the original
    # three FIRST (so a no-new-key call serializes byte-identically — see the byte-identity check below)
    sk = transport._SAMPLING_KEYS
    if "repetition_penalty" in sk and {"temperature", "max_tokens", "top_p"} <= set(sk) \
            and tuple(sk[:3]) == ("temperature", "max_tokens", "top_p"):
        ok("family: _SAMPLING_KEYS is the single-source allowlist, ordered, original three FIRST "
           "(repetition_penalty + the family follow)")
    else:
        bad("family: single-source ordered allowlist", f"_SAMPLING_KEYS={sk!r}")


# ---------------------------------------------------------------------------------------------------
# server reachability
# ---------------------------------------------------------------------------------------------------
def _server_up():
    try:
        with urllib.request.urlopen(RESIDENT_BASE_URL + "/models", timeout=5) as r:
            json.loads(r.read())
        return True
    except Exception as e:
        print(f"  -- resident server :8000 not reachable ({e!r}) — live checks SKIPPED")
        return False


# ---------------------------------------------------------------------------------------------------
# 5. BY USE — the resident vLLM ACCEPTS repetition_penalty (200 + content)
# ---------------------------------------------------------------------------------------------------
def test_live_accepts(evidence: dict):
    t = transport.openai_transport(base_url=RESIDENT_BASE_URL, timeout=60)
    try:
        content = t(RESIDENT_MODEL, [{"role": "user", "content": "Say only the word: hello"}],
                    repetition_penalty=1.15, temperature=0.0, max_tokens=16)
    except Exception as e:
        bad("live: resident vLLM ACCEPTS repetition_penalty (valid sampling param)", f"{e!r}")
        evidence["resident_accepts_rep_penalty"] = False
        return
    evidence["resident_accepts_rep_penalty"] = True
    evidence["live_rep_penalty_content"] = content
    if isinstance(content, str) and content.strip():
        ok(f"live: resident vLLM ACCEPTS repetition_penalty=1.15 → 200 + content {content.strip()!r}")
    else:
        bad("live: rep_penalty request returned content", f"content={content!r}")


# ---------------------------------------------------------------------------------------------------
# 6. END-TO-END — run_role(policy=) ladder now drives a real call carrying the registry rung
# ---------------------------------------------------------------------------------------------------
def test_end_to_end_ladder(evidence: dict):
    """The point of the lane: the ladder VALUE now reaches the model. We capture the body of the real
    request run_role's ladder path issues and confirm repetition_penalty == the registry rung."""
    from runtime import cognition
    from runtime.roles import Role
    from pydantic import BaseModel

    class _Out(BaseModel):
        text: str = "ok"

    role = Role(id="e2etest", prompt_template="Reply ONLY JSON: {\"text\": \"ok\"}", output_schema=_Out,
                spec={"id": "e2etest", "prompt_template": "x", "output_schema": _Out})
    reg = cognition.generation_policy_registry()
    rung = reg.policy_for("prose_default").default_rep_penalty   # the registry default rung
    evidence["ladder_rung"] = rung

    captured = {}
    real_urlopen = urllib.request.urlopen

    def fake_urlopen(req, timeout=None):
        captured["body"] = json.loads(req.data.decode())
        # a clean (finish_reason=stop) conformant envelope so the ladder accepts the first draw
        return _FakeResp(json.dumps({
            "choices": [{"finish_reason": "stop",
                         "message": {"role": "assistant", "content": "{\"text\": \"ok\"}"}}],
            "usage": {"total_tokens": 3},
        }).encode())

    urllib.request.urlopen = fake_urlopen
    try:
        out = cognition.run_role(role, {"utterance": "hi"}, policy="prose_default")
    except Exception as e:
        bad("end-to-end: run_role(policy=) ladder drives a real call", f"{e!r}")
        evidence["end_to_end"] = False
        return
    finally:
        urllib.request.urlopen = real_urlopen

    body = captured.get("body", {})
    evidence["end_to_end_body_rep_penalty"] = body.get("repetition_penalty")
    if body.get("repetition_penalty") == rung:
        ok(f"end-to-end: run_role(policy='prose_default') ladder rung ({rung}) REACHES the request body "
           f"(ladder→model effect now closed — was gated on this passthrough)")
        evidence["end_to_end"] = True
    else:
        bad("end-to-end: ladder rung reaches the body", f"body.repetition_penalty={body.get('repetition_penalty')!r} expected {rung}")
        evidence["end_to_end"] = False
    if isinstance(out, dict) and out.get("text") == "ok":
        ok("end-to-end: run_role still returns the validated dict (ladder path intact)")
    else:
        bad("end-to-end: run_role return", f"out={out!r}")


def main():
    print("== transport repetition_penalty / sampling-family passthrough (FABRIC-2 · completes O2) ==")
    evidence = {"resident_model": RESIDENT_MODEL, "base_url": RESIDENT_BASE_URL}

    print("\n[1+2] NEGATIVE CONTROL (param lands) + BYTE-IDENTICAL (absent → unchanged) — both transports")
    test_passthrough_both_paths()
    print("\n[3] ALLOWLIST not denylist — out-params / structured-output triggers do NOT leak")
    test_allowlist_no_leak()
    print("\n[4] the WHOLE sampling family rides the one seam (general, not a single hardcoded key)")
    test_family_rides_seam()

    print("\n[5-6] BY USE — live resident 4B + end-to-end ladder")
    if _server_up():
        test_live_accepts(evidence)
    else:
        evidence["live_skipped"] = "resident server :8000 down"
    # the end-to-end ladder body-capture is network-free (fake urlopen) — runs regardless of the server
    test_end_to_end_ladder(evidence)

    with open("/tmp/transport_rep_penalty_evidence.json", "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"\nevidence → /tmp/transport_rep_penalty_evidence.json")

    print(f"\n{'='*60}")
    print(f"PASSED {len(_passed)} · FAILED {len(_failed)}")
    if _failed:
        for n, w in _failed:
            print(f"  FAILED: {n} — {w}")
        sys.exit(1)
    print("ALL CHECKS PASS")


if __name__ == "__main__":
    main()
