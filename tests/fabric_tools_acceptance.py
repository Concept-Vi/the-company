"""tests/fabric_tools_acceptance.py — NATIVE TOOL-CALLING fabric path (the fabric lane).

Finding: every fleet CHAT model supports native tools (ollama /api/show → capabilities
contains "tools"); only embedders (nomic-embed-text) don't. complete() has 12+ string-callers,
so we ADD SIBLINGS — never modify complete()/openai_transport.

TDD, headless (transports/HTTP are INJECTED fakes — no live endpoint needed). Proven here:
  1. openai_tools_transport BUILDS tools+tool_choice into the request body AND returns the
     WHOLE choices[0].message dict ({content, tool_calls}), not a bare content string.
     forbid_gemini is enforced FIRST (fail loud).
  2. complete_with_tools returns the message dict; GUARD = valid iff tool_calls present OR
     non-empty content:
       - empty content + tool_calls  -> SUCCESS, ONE attempt, ZERO sleeps (NOT the :71 empty-fail)
       - non-empty content, no tools -> SUCCESS
       - empty content + no tool_calls -> retry, then FabricError (fail loud)
       - transport error -> retry, then FabricError
     tools/tool_choice are forwarded into the transport's **opts (the wiring round-trip).
  3. model_supports_tools (endpoint-aware, fail-loud):
       - ollama /api/show capabilities containing "tools"      -> True
       - ollama /api/show capabilities WITHOUT "tools" (nomic) -> False (a clean DETECTION)
       - truly UNDETECTABLE (unreachable / no capabilities / unknown endpoint) -> RAISE (fail loud,
         NEVER a silent assume-capable AND never a silent False)

Run: ./.venv/bin/python tests/fabric_tools_acceptance.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from fabric import client, transport
from fabric.client import FabricError

ok = True


def check(label, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def recording_sleep():
    """A fake sleep recording each delay (clock injection)."""
    calls = []
    return calls, (lambda s: calls.append(s))


def tools_transport_of(*responses):
    """A fake TOOLS transport: (model, messages, **opts) -> message dict (or raises).
    Records the opts it was called with so the wiring round-trip can be asserted."""
    it = iter(responses)
    seen = {"opts": None, "calls": 0}

    def t(model, messages, **opts):
        seen["opts"] = opts
        seen["calls"] += 1
        r = next(it)
        if isinstance(r, BaseException):
            raise r
        return r
    return t, seen


class FakeResp:
    """Context-manager stand-in for urllib's HTTP response."""
    def __init__(self, payload):
        self._b = json.dumps(payload).encode()

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def main():
    no_sleep = lambda s: None

    # === 1. openai_tools_transport: builds tools+tool_choice into body, returns the message dict ===
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["data"] = json.loads(req.data.decode())
        captured["url"] = req.full_url
        # OpenAI shape: choices[0].message carries content + tool_calls
        return FakeResp({"choices": [{"message": {"content": "",
                                                  "tool_calls": [{"id": "c1", "type": "function",
                                                                  "function": {"name": "run", "arguments": "{}"}}]}}]})

    orig_urlopen = transport.urllib.request.urlopen
    transport.urllib.request.urlopen = fake_urlopen
    try:
        tp = transport.openai_tools_transport(base_url="http://x/v1")
        tools = [{"type": "function", "function": {"name": "run", "parameters": {}}}]
        msg = tp("some-chat-model", [{"role": "user", "content": "go"}], tools=tools)
        check("tools transport returns the WHOLE message dict (content+tool_calls), not a bare string",
              isinstance(msg, dict) and "tool_calls" in msg and "content" in msg)
        check("tools transport put body['tools'] into the request",
              captured["data"].get("tools") == tools)
        check("tools transport put body['tool_choice']='auto' (default) into the request",
              captured["data"].get("tool_choice") == "auto")
        check("tools transport posts to /chat/completions",
              captured["url"].endswith("/chat/completions"))
        # explicit tool_choice override flows through
        tp("some-chat-model", [], tools=tools, tool_choice="required")
        check("tools transport honours an explicit tool_choice override",
              captured["data"].get("tool_choice") == "required")
        # NO tools passed -> no tools/tool_choice keys (sibling of openai_transport build)
        tp("some-chat-model", [{"role": "user", "content": "hi"}])
        check("tools transport omits tools/tool_choice when no tools passed",
              "tools" not in captured["data"] and "tool_choice" not in captured["data"])
    finally:
        transport.urllib.request.urlopen = orig_urlopen

    # forbid_gemini enforced FIRST (before any HTTP) — fail loud
    try:
        transport.openai_tools_transport()("gemini-pro", [], tools=[])
        check("tools transport forbids Gemini (fail loud, FIRST)", False)
    except ValueError:
        check("tools transport forbids Gemini (fail loud, FIRST)", True)

    # === 2. complete_with_tools guards ===
    tool_call_msg = {"content": "", "tool_calls": [{"id": "c1", "type": "function",
                     "function": {"name": "run", "arguments": "{}"}}]}

    # empty content + tool_calls = SUCCESS on the FIRST attempt, ZERO sleeps (NOT the :71 empty-fail)
    t1, seen1 = tools_transport_of(tool_call_msg)
    calls1, sleep1 = recording_sleep()
    r1 = client.complete_with_tools(t1, [], model="m", tools=[{"x": 1}], sleep=sleep1)
    check("empty-content + tool_calls is VALID — returns the message dict", r1 == tool_call_msg)
    check("empty-content + tool_calls makes exactly ONE attempt (no retry)", seen1["calls"] == 1)
    check("empty-content + tool_calls sleeps ZERO times (success, not the :71 empty-failure)",
          len(calls1) == 0)

    # tools/tool_choice are FORWARDED into the transport's **opts (the wiring round-trip)
    t2, seen2 = tools_transport_of(tool_call_msg)
    client.complete_with_tools(t2, [], model="m", tools=[{"y": 2}], tool_choice="required", sleep=no_sleep)
    check("complete_with_tools forwards tools= into the transport opts",
          seen2["opts"].get("tools") == [{"y": 2}])
    check("complete_with_tools forwards tool_choice= into the transport opts",
          seen2["opts"].get("tool_choice") == "required")

    # non-empty content, no tool_calls = SUCCESS
    t3, _ = tools_transport_of({"content": "a plain answer", "tool_calls": None})
    r3 = client.complete_with_tools(t3, [], model="m", tools=[], sleep=no_sleep)
    check("non-empty content + no tool_calls is VALID — returns the message dict",
          r3 == {"content": "a plain answer", "tool_calls": None})

    # empty content + NO tool_calls -> retry then FabricError (fail loud)
    t4, seen4 = tools_transport_of({"content": "", "tool_calls": None},
                                   {"content": "  ", "tool_calls": []},
                                   {"content": None, "tool_calls": None},
                                   {"content": "", "tool_calls": None})
    calls4, sleep4 = recording_sleep()
    try:
        client.complete_with_tools(t4, [], model="m", tools=[], retries=4, sleep=sleep4)
        check("empty + no tool_calls raises FabricError after retries (fail loud)", False)
    except FabricError:
        check("empty + no tool_calls raises FabricError after retries (fail loud)", True)
    check("empty + no tool_calls made 4 attempts", seen4["calls"] == 4)
    check("empty + no tool_calls slept exactly 3× (skips final-attempt sleep)", len(calls4) == 3)

    # transport error -> retry then SUCCEEDS (reuses the jittered backoff)
    t5, seen5 = tools_transport_of(RuntimeError("502"), tool_call_msg)
    calls5, sleep5 = recording_sleep()
    r5 = client.complete_with_tools(t5, [], model="m", tools=[], retries=4, sleep=sleep5)
    check("transient transport error retries then SUCCEEDS", r5 == tool_call_msg)
    check("transient error sleeps exactly ONCE (one failure → one backoff)", len(calls5) == 1)

    # transport error every time -> FabricError (fail loud)
    t6, _ = tools_transport_of(RuntimeError("x"), RuntimeError("x"), RuntimeError("x"))
    try:
        client.complete_with_tools(t6, [], model="m", tools=[], retries=3, sleep=no_sleep)
        check("always-erroring transport raises FabricError (fail loud)", False)
    except FabricError:
        check("always-erroring transport raises FabricError (fail loud)", True)

    # === 3. capability detection (endpoint-aware, fail-loud) ===
    # ollama /api/show: capabilities contains "tools" -> True; without -> clean False; undetectable -> raise.
    def fake_show(payload_or_exc):
        def f(req, timeout=None):
            if isinstance(payload_or_exc, BaseException):
                raise payload_or_exc
            captured["show_url"] = req.full_url
            captured["show_body"] = json.loads(req.data.decode()) if req.data else None
            return FakeResp(payload_or_exc)
        return f

    orig_urlopen = transport.urllib.request.urlopen
    try:
        # tools-capable model
        transport.urllib.request.urlopen = fake_show({"capabilities": ["completion", "tools"]})
        check("tools-capable model (capabilities has 'tools') -> True",
              transport.model_supports_tools("some-chat-model", base_url="http://localhost:11434/v1") is True)
        check("capability probe hits ollama /api/show (NOT under /v1)",
              captured["show_url"].endswith("/api/show") and "/v1" not in captured["show_url"])
        check("capability probe sends {'model': ...}",
              captured["show_body"].get("model") == "some-chat-model")

        # nomic-embed-text: capabilities present but NO 'tools' -> clean False (a real detection)
        transport.urllib.request.urlopen = fake_show({"capabilities": ["completion", "embedding"]})
        check("nomic-embed-text (capabilities without 'tools') -> False (clean detection)",
              transport.model_supports_tools("nomic-embed-text", base_url="http://localhost:11434/v1") is False)

        # UNDETECTABLE: endpoint unreachable -> RAISE (fail loud, never assume-capable, never silent False)
        transport.urllib.request.urlopen = fake_show(OSError("connection refused"))
        try:
            transport.model_supports_tools("x", base_url="http://localhost:11434/v1")
            check("unreachable endpoint RAISES (fail loud, not silent)", False)
        except Exception:
            check("unreachable endpoint RAISES (fail loud, not silent)", True)

        # UNDETECTABLE: response with NO capabilities field -> RAISE
        transport.urllib.request.urlopen = fake_show({"details": {}})
        try:
            transport.model_supports_tools("x", base_url="http://localhost:11434/v1")
            check("missing 'capabilities' field RAISES (cannot determine ⇒ fail loud)", False)
        except Exception:
            check("missing 'capabilities' field RAISES (cannot determine ⇒ fail loud)", True)

        # UNDETECTABLE: an unknown (non-ollama, non-litellm) endpoint kind -> RAISE
        try:
            transport.model_supports_tools("x", base_url="http://localhost:11434/v1", endpoint="mystery")
            check("unknown endpoint kind RAISES (cannot determine ⇒ fail loud)", False)
        except Exception:
            check("unknown endpoint kind RAISES (cannot determine ⇒ fail loud)", True)

        # forbid_gemini enforced in the probe too
        try:
            transport.model_supports_tools("gemini-pro", base_url="http://localhost:11434/v1")
            check("capability probe forbids Gemini (fail loud)", False)
        except ValueError:
            check("capability probe forbids Gemini (fail loud)", True)

        # LiteLLM endpoint: model_info.supports_function_calling -> True (fake-injected /model/info)
        transport.urllib.request.urlopen = fake_show(
            {"data": [{"model_name": "m", "model_info": {"supports_function_calling": True}}]})
        check("litellm endpoint: supports_function_calling=True -> True",
              transport.model_supports_tools("m", base_url="http://localhost:4100/v1",
                                              endpoint="litellm") is True)
        # explicit False from the proxy -> a clean False (a real detection)
        transport.urllib.request.urlopen = fake_show(
            {"data": [{"model_name": "m", "model_info": {"supports_function_calling": False}}]})
        check("litellm endpoint: supports_function_calling=False -> False (clean detection)",
              transport.model_supports_tools("m", base_url="http://localhost:4100/v1",
                                              endpoint="litellm") is False)
        # LiteLLM: the field is ABSENT -> RAISE (cannot determine ⇒ never assume-capable)
        transport.urllib.request.urlopen = fake_show(
            {"data": [{"model_name": "m", "model_info": {}}]})
        try:
            transport.model_supports_tools("m", base_url="http://localhost:4100/v1", endpoint="litellm")
            check("litellm endpoint: missing supports_function_calling RAISES (fail loud)", False)
        except Exception:
            check("litellm endpoint: missing supports_function_calling RAISES (fail loud)", True)
        # LiteLLM: model not listed at all -> RAISE
        transport.urllib.request.urlopen = fake_show({"data": []})
        try:
            transport.model_supports_tools("m", base_url="http://localhost:4100/v1", endpoint="litellm")
            check("litellm endpoint: model not listed RAISES (fail loud)", False)
        except Exception:
            check("litellm endpoint: model not listed RAISES (fail loud)", True)
    finally:
        transport.urllib.request.urlopen = orig_urlopen

    print("\n" + ("✅ FABRIC TOOLS ACCEPTANCE PASSED" if ok else "❌ FABRIC TOOLS ACCEPTANCE FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
