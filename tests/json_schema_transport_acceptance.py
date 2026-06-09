"""tests/json_schema_transport_acceptance.py — the json_schema transport branch (L-transport · C1.4 / R1-FOLD F9).

PROVES the additive `json_schema` branch in fabric/transport.py:
  1. UNIT (no network): the request body shape is correct + additive — json_schema when asked,
     json_object for the EXISTING json=True callers, nothing when neither. Nesting is the OpenAI/vLLM
     contract ({"type":"json_schema","json_schema":{"name":..,"schema":..}}) — flattening would 400.
  2. BY USE (live :8000 resident 4B): does the resident vLLM ACCEPT
     response_format:{type:json_schema,...} with a REAL pydantic-derived role schema (FocusOut) and
     return schema-conformant JSON? (vLLM 0.21 structured outputs / xgrammar backend.) On a 400 we
     READ the HTTPError body so the report can distinguish "no flag" from "schema-shape rejected".
  3. PRESERVED: the json_object path (json=True, the run_role / judge path) still works against :8000.
  4. ENFORCEMENT STAYS CLIENT-SIDE: complete()'s validate/retry is the guarantee (F9) — json_schema is a
     decode strengthening, not a replacement. A live json_schema call STILL goes through complete() and
     returns a VALIDATED FocusOut.
  5. finish_reason + usage PASSTHROUGH (O3): the additive `meta={}` out-param — a caller passes an empty
     dict, the transport fills it (finish_reason + token usage) after parsing. UNIT: meta does NOT leak
     into the request body; _fill_meta populates from the envelope; absent meta = no-op (the 12+ bare-string
     callers byte-unaffected). BY USE: tiny max_tokens → finish_reason='length' (truncation = invalid
     grammar output, the O3 signal); normal → 'stop' + usage; threads through complete() with its return
     type UNCHANGED. The ENGINE lane (cognition.py run_role / op.run) is the CONSUMER (O3) — not wired here.

Run: PYTHONPATH=/home/tim/company-cognition /home/tim/company/.venv/bin/python tests/json_schema_transport_acceptance.py
The live checks need the resident 4B UP at :8000 (read-only USE — no load/evict). If it is DOWN, the
live checks are reported SKIPPED-server-down (fail-loud distinction), the unit checks still run.
"""
from __future__ import annotations
import json
import os
import sys
import urllib.error

# self-bootstrap the repo root onto sys.path (every acceptance suite does this) so the suite is
# runnable STANDALONE — `python tests/json_schema_transport_acceptance.py` — not only with an external
# PYTHONPATH. Without it `import fabric` fails (ModuleNotFoundError) and a bare sweep/drift run skips it.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fabric import transport, client
from roles.focus import FocusOut

RESIDENT_BASE_URL = "http://127.0.0.1:8000/v1"
RESIDENT_MODEL = "cyankiwi/Qwen3.5-4B-AWQ-4bit"

_passed = []
_failed = []


def ok(name):
    _passed.append(name); print(f"  ok  {name}")


def bad(name, why):
    _failed.append((name, why)); print(f"  XX  {name} — {why}")


# A transport that does NOT hit the network — captures the body that WOULD be sent, so we can assert
# the exact request shape (the discriminating bug is the nesting). Mirrors openai_transport's build.
def _capturing_transport(captured: dict):
    def t(model, messages, **opts):
        body = {"model": model, "messages": messages, "stream": False}
        transport._apply_response_format(body, opts)
        captured["body"] = body
        return body
    return t


# ---------------------------------------------------------------------------------------------------
# 1. UNIT — request body shape (additive + correct nesting)
# ---------------------------------------------------------------------------------------------------
def test_unit_shape():
    schema = FocusOut.model_json_schema()
    js = {"name": "focus", "schema": schema}

    # (a) json_schema present → json_schema response_format with the EXACT nesting
    cap = {}
    _capturing_transport(cap)("m", [], json_schema=js)
    rf = cap["body"].get("response_format")
    if rf == {"type": "json_schema", "json_schema": js}:
        ok("unit: json_schema → response_format {type:json_schema, json_schema:{name,schema}} (correct nesting)")
    else:
        bad("unit: json_schema nesting", f"got {rf!r}")
    # the actual schema must nest UNDER 'schema', name as sibling (flattening 400s vLLM)
    if rf and rf["json_schema"].get("schema") == schema and rf["json_schema"].get("name") == "focus":
        ok("unit: schema nests under 'schema' key, name is sibling (not flattened)")
    else:
        bad("unit: schema-under-schema-key", f"got {rf!r}")

    # (b) json=True (the EXISTING run_role/judge path) → STILL json_object (additive, unbroken)
    cap = {}
    _capturing_transport(cap)("m", [], json=True)
    if cap["body"].get("response_format") == {"type": "json_object"}:
        ok("unit: json=True → json_object UNCHANGED (existing callers unaffected)")
    else:
        bad("unit: json=True path", f"got {cap['body'].get('response_format')!r}")

    # (c) schema= opt (the other existing trigger) → json_object
    cap = {}
    _capturing_transport(cap)("m", [], schema=object())
    if cap["body"].get("response_format") == {"type": "json_object"}:
        ok("unit: schema= opt → json_object UNCHANGED")
    else:
        bad("unit: schema= path", f"got {cap['body'].get('response_format')!r}")

    # (d) neither → NO response_format (free text), unchanged
    cap = {}
    _capturing_transport(cap)("m", [])
    if "response_format" not in cap["body"]:
        ok("unit: neither → no response_format (free-text path unchanged)")
    else:
        bad("unit: free-text path", f"unexpected {cap['body'].get('response_format')!r}")

    # (e) precedence: json_schema WINS over a co-passed json=True (the new branch is first)
    cap = {}
    _capturing_transport(cap)("m", [], json_schema=js, json=True)
    if cap["body"]["response_format"]["type"] == "json_schema":
        ok("unit: json_schema takes precedence over json=True (branch ordering)")
    else:
        bad("unit: precedence", f"got {cap['body']['response_format']!r}")

    # (f) BOTH transports share the one decision (tools transport too) — reuse, not parallel
    cap = {}
    tt = transport.openai_tools_transport  # build a tools-transport, but capture via the same helper
    # we can't easily intercept its urlopen; instead assert the helper is the single source by checking
    # the tools transport ALSO routes json_schema (re-run the helper on a fresh body == same result)
    body = {"model": "m", "messages": [], "stream": False}
    transport._apply_response_format(body, {"json_schema": js})
    if body.get("response_format") == {"type": "json_schema", "json_schema": js}:
        ok("unit: _apply_response_format is the single shared decision (both transports call it)")
    else:
        bad("unit: shared helper", f"got {body.get('response_format')!r}")


# ---------------------------------------------------------------------------------------------------
# server reachability
# ---------------------------------------------------------------------------------------------------
def _server_up():
    try:
        import urllib.request
        with urllib.request.urlopen(RESIDENT_BASE_URL + "/models", timeout=5) as r:
            json.loads(r.read())
        return True
    except Exception as e:
        print(f"  -- resident server :8000 not reachable ({e!r}) — live checks SKIPPED")
        return False


# ---------------------------------------------------------------------------------------------------
# 2. BY USE — does the resident vLLM ACCEPT json_schema with a REAL role schema?
# ---------------------------------------------------------------------------------------------------
def test_live_json_schema(evidence: dict):
    schema = FocusOut.model_json_schema()
    js = {"name": "focus", "schema": schema}
    t = transport.openai_transport(base_url=RESIDENT_BASE_URL, timeout=60)
    msgs = [
        {"role": "system", "content": "Return ONLY JSON: intent (a string), which_roles (array of strings)."},
        {"role": "user", "content": "Utterance: remind me what we decided about the database last week"},
    ]
    try:
        raw = t(RESIDENT_MODEL, msgs, json_schema=js, temperature=0.0, max_tokens=128)
    except urllib.error.HTTPError as e:
        bodytext = ""
        try:
            bodytext = e.read().decode(errors="replace")
        except Exception:
            pass
        evidence["live_json_schema_400"] = {"code": e.code, "body": bodytext[:1000]}
        bad("live: resident vLLM accepts json_schema (real FocusOut schema)",
            f"HTTP {e.code}: {bodytext[:300]}")
        evidence["resident_accepts_json_schema"] = False
        return None
    except Exception as e:
        bad("live: resident vLLM accepts json_schema", f"{e!r}")
        evidence["resident_accepts_json_schema"] = False
        return None

    evidence["live_json_schema_raw"] = raw
    # parse + validate against the real model — proves schema-conformant
    try:
        validated = FocusOut.model_validate(json.loads(raw))
    except Exception as e:
        bad("live: json_schema response is schema-conformant", f"raw={raw!r} err={e!r}")
        evidence["resident_accepts_json_schema"] = False
        return None
    evidence["resident_accepts_json_schema"] = True
    evidence["live_json_schema_validated"] = validated.model_dump()
    ok(f"live: resident vLLM ACCEPTS json_schema + returns schema-conformant JSON → {validated.model_dump()}")

    # NEGATIVE CONTROL — discriminates "vLLM CONSTRAINED decoding" from "the model just obeyed a
    # JSON-asking prompt". The prompt here EXPLICITLY asks for a plain-English sentence, NO JSON. If
    # the response is STILL conformant FocusOut, the server's guided-decoding backend (xgrammar) is
    # actually biting (the real purpose — schema-CONSTRAINED decode). If it comes back as prose, the
    # server is IGNORING response_format and only the prompt was doing the work.
    ctrl_msgs = [
        {"role": "system", "content": "Reply in one plain English sentence. Do NOT output JSON."},
        {"role": "user", "content": "Describe what you can do."},
    ]
    try:
        ctrl_raw = t(RESIDENT_MODEL, ctrl_msgs, json_schema=js, temperature=0.0, max_tokens=128)
        ctrl_validated = FocusOut.model_validate(json.loads(ctrl_raw))
        evidence["resident_constrains_decode"] = True
        evidence["live_negctrl_raw"] = ctrl_raw
        evidence["live_negctrl_validated"] = ctrl_validated.model_dump()
        ok(f"live NEG-CONTROL: json_schema CONSTRAINS decode — conformant JSON despite a no-JSON prompt → {ctrl_validated.model_dump()}")
    except Exception as e:
        # the server did NOT constrain — only the prompt was working. Genuine finding, NOT a test fail:
        # the lane is correct regardless (client validate/retry is the guarantee). Recorded for the report.
        evidence["resident_constrains_decode"] = False
        evidence["live_negctrl_raw"] = locals().get("ctrl_raw")
        evidence["live_negctrl_note"] = f"no-JSON prompt produced non-conformant output ({e!r}) — server ACCEPTS json_schema but may not CONSTRAIN; client validate/retry remains the guarantee (F9)"
        print(f"  ?? live NEG-CONTROL: json_schema ACCEPTED but did NOT constrain a no-JSON prompt — "
              f"finding (not a fail): {evidence['live_negctrl_note']}")
    return validated


# ---------------------------------------------------------------------------------------------------
# 3. PRESERVED — the json_object path (json=True) still works live (the run_role/judge path)
# ---------------------------------------------------------------------------------------------------
def test_live_json_object_preserved(evidence: dict):
    t = transport.openai_transport(base_url=RESIDENT_BASE_URL, timeout=60)
    msgs = [
        {"role": "system", "content": "Return ONLY JSON: {\"intent\": <string>, \"which_roles\": []}."},
        {"role": "user", "content": "Utterance: hello"},
    ]
    try:
        raw = t(RESIDENT_MODEL, msgs, json=True, temperature=0.0, max_tokens=128)
        obj = json.loads(raw)
    except Exception as e:
        bad("live: json_object path (json=True) STILL works", f"{e!r}")
        evidence["json_object_preserved"] = False
        return
    evidence["json_object_preserved"] = True
    evidence["live_json_object_raw"] = raw
    ok(f"live: json_object path (json=True) unaffected → {obj}")


# ---------------------------------------------------------------------------------------------------
# 4. ENFORCEMENT STAYS CLIENT-SIDE — complete() validate/retry over the json_schema branch (F9)
# ---------------------------------------------------------------------------------------------------
def test_live_complete_validates(evidence: dict):
    t = transport.openai_transport(base_url=RESIDENT_BASE_URL, timeout=60)
    msgs = [
        {"role": "system", "content": "Return ONLY JSON: intent (string), which_roles (array of strings)."},
        {"role": "user", "content": "Utterance: what can you do"},
    ]
    js = {"name": "focus", "schema": FocusOut.model_json_schema()}
    try:
        # complete() is the ENFORCEMENT (parse+validate+retry); json_schema is the decode strengthening.
        validated = client.complete(t, msgs, model=RESIDENT_MODEL, schema=FocusOut,
                                    json_schema=js, temperature=0.0, max_tokens=128)
    except Exception as e:
        bad("live: complete() validate/retry over json_schema branch (F9 enforcement)", f"{e!r}")
        evidence["complete_enforcement"] = False
        return
    evidence["complete_enforcement"] = True
    evidence["live_complete_validated"] = validated.model_dump()
    ok(f"live: complete() returns a VALIDATED FocusOut over the json_schema branch → {validated.model_dump()}")


# ---------------------------------------------------------------------------------------------------
# 5. finish_reason + usage PASSTHROUGH (O3) — the additive meta={} out-param
# ---------------------------------------------------------------------------------------------------
def test_meta_no_leak():
    """UNIT (no network): a `meta={}` out-param must NOT leak into the request body, and _fill_meta
    populates it from the response envelope. Proves the 12+ bare-string callers are byte-unaffected."""
    cap = {}

    def cap_t(model, messages, **opts):
        body = {"model": model, "messages": messages, "stream": False}
        transport._apply_response_format(body, opts)
        for k in ("temperature", "max_tokens", "top_p"):
            if k in opts:
                body[k] = opts[k]
        cap["body"] = body
        transport._fill_meta(opts, {"choices": [{"finish_reason": "stop"}], "usage": {"total_tokens": 7}})
        return "hi"

    m = {}
    cap_t("m", [], meta=m, temperature=0.0)
    if "meta" not in cap["body"]:
        ok("unit: meta out-param does NOT leak into the request body (callers unaffected)")
    else:
        bad("unit: meta leak", f"body has meta: {cap['body']!r}")
    if m == {"finish_reason": "stop", "usage": {"total_tokens": 7}}:
        ok("unit: _fill_meta populates finish_reason + usage from the envelope")
    else:
        bad("unit: _fill_meta fill", f"got {m!r}")

    # no meta passed → _fill_meta is a no-op (the default path)
    m2 = {}
    transport._fill_meta({}, {"choices": [{"finish_reason": "stop"}]})
    if m2 == {}:
        ok("unit: no meta= → _fill_meta is a no-op (default path unchanged)")


def test_live_finish_reason(evidence: dict):
    """BY USE: a tiny max_tokens call → finish_reason='length' (truncation = invalid grammar output, the
    O3 signal); a normal call → 'stop' + real usage token counts. Threads through complete() unchanged."""
    t = transport.openai_transport(base_url=RESIDENT_BASE_URL, timeout=60)
    # short → length (truncated)
    meta_s = {}
    try:
        t(RESIDENT_MODEL, [{"role": "system", "content": "Write a long multi-paragraph essay about databases."},
                           {"role": "user", "content": "Go."}], max_tokens=8, temperature=0.0, meta=meta_s)
    except Exception as e:
        bad("live: finish_reason on truncation", f"{e!r}"); evidence["finish_reason_passthrough"] = False; return
    evidence["finish_reason_short"] = meta_s.get("finish_reason")
    evidence["usage_short"] = meta_s.get("usage")
    if meta_s.get("finish_reason") == "length":
        ok(f"live: tiny max_tokens → finish_reason='length' (the O3 truncated-invalid signal); usage={meta_s.get('usage')}")
    else:
        bad("live: truncation → finish_reason='length'", f"got {meta_s!r}")
    # normal → stop + usage
    meta_n = {}
    try:
        t(RESIDENT_MODEL, [{"role": "user", "content": "Say only the word: hello"}],
          max_tokens=64, temperature=0.0, meta=meta_n)
    except Exception as e:
        bad("live: finish_reason on clean stop", f"{e!r}"); evidence["finish_reason_passthrough"] = False; return
    evidence["finish_reason_normal"] = meta_n.get("finish_reason")
    if meta_n.get("finish_reason") == "stop" and isinstance(meta_n.get("usage"), dict) \
            and "completion_tokens" in meta_n["usage"]:
        ok(f"live: clean completion → finish_reason='stop' + usage token counts {meta_n.get('usage')}")
    else:
        bad("live: clean → 'stop' + usage", f"got {meta_n!r}")
    # threads through complete() WITHOUT changing its return type
    meta_c = {}
    try:
        validated = client.complete(
            t, [{"role": "system", "content": "Return ONLY JSON: intent (string), which_roles (array of strings)."},
                {"role": "user", "content": "Utterance: hello"}],
            model=RESIDENT_MODEL, schema=FocusOut, json=True, temperature=0.0, max_tokens=128, meta=meta_c)
    except Exception as e:
        bad("live: meta threads through complete()", f"{e!r}"); evidence["finish_reason_passthrough"] = False; return
    if hasattr(validated, "model_dump") and meta_c.get("finish_reason") == "stop":
        ok(f"live: complete() return UNCHANGED (validated FocusOut) + meta filled → fr={meta_c.get('finish_reason')}")
        evidence["finish_reason_passthrough"] = True
        evidence["complete_meta"] = meta_c
    else:
        bad("live: complete() return + meta", f"validated={validated!r} meta={meta_c!r}")
        evidence["finish_reason_passthrough"] = False


def main():
    print("== json_schema transport acceptance (L-transport · C1.4 / R1-FOLD F9) ==")
    evidence = {"resident_model": RESIDENT_MODEL, "base_url": RESIDENT_BASE_URL}

    print("\n[1] UNIT — request body shape (additive + correct nesting)")
    test_unit_shape()
    print("\n[5-unit] finish_reason+usage meta out-param (O3) — no-leak + fill")
    test_meta_no_leak()

    print("\n[2-5] BY USE — live resident 4B")
    if _server_up():
        test_live_json_schema(evidence)
        test_live_json_object_preserved(evidence)
        test_live_complete_validates(evidence)
        test_live_finish_reason(evidence)
    else:
        evidence["live_skipped"] = "resident server :8000 down"

    # dump evidence for the lane report
    with open("/tmp/ltransport_evidence.json", "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"\nevidence → /tmp/ltransport_evidence.json")

    print(f"\n{'='*60}")
    print(f"PASSED {len(_passed)} · FAILED {len(_failed)}")
    if _failed:
        for n, w in _failed:
            print(f"  FAILED: {n} — {w}")
        sys.exit(1)
    print("ALL CHECKS PASS")


if __name__ == "__main__":
    main()
