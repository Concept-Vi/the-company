"""fabric/transport.py — the OpenAI-compatible HTTP transport (S6). See fabric/AGENTS.md.

Stdlib only. A transport is `(model, messages, **opts) -> content_str` — exactly what
fabric.client.complete() wraps with guards. It speaks the OpenAI `/v1/chat/completions`
shape, so the SAME transport points at either the LiteLLM proxy or ollama directly
(both OpenAI-compatible) — repointable by `base_url`. NO Gemini (enforced in config).
"""
from __future__ import annotations
import json
import urllib.request

from fabric.config import DEFAULT_BASE_URL, DEFAULT_EMBED_URL, DEFAULT_TIMEOUT, forbid_gemini


def list_models(base_url: str = DEFAULT_BASE_URL, api_key: str = "ollama", timeout: int = 8) -> list:
    """The REAL registered models at this endpoint (OpenAI /v1/models). Source of truth so the
    self-coding brain never invents model names — it picks from what actually exists. NO Gemini."""
    req = urllib.request.Request(
        base_url.rstrip("/") + "/models",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read())
    ids = [m.get("id") for m in (data.get("data") or []) if m.get("id")]
    return [m for m in ids if "gemini" not in m.lower()]


def _apply_response_format(body: dict, opts: dict) -> None:
    """Set body["response_format"] from opts — the ONE structured-output decision, shared by
    openai_transport AND openai_tools_transport (single-source so the two transports agree by
    construction; reuse, not a second copy). Precedence (schema-additive — C2 / R1-FOLD F9):

      1. opts["json_schema"]  → response_format {"type":"json_schema","json_schema": <dict>}.
         SERVER-SIDE schema-CONSTRAINED decoding (vLLM ≥0.21 guided/structured outputs). The caller
         passes the FULL OpenAI/vLLM json_schema object — {"name": <role_id>, "schema": <JSON schema>}
         (the actual schema nests UNDER "schema", "name" is its sibling; flattening 400s the server).
         A role's declared output_schema (a Pydantic model) flows through as
         {"name": role.id, "schema": role.output_schema.model_json_schema()} when the caller opts in.
      2. opts["schema"] OR opts["json"]  → {"type":"json_object"} — the EXISTING bare-JSON path,
         UNCHANGED, so every current json=True caller (run_role, the judge, G0/G1/G2/G3) is unaffected.
      3. neither  → no response_format (free text), unchanged.

    This is a DECODE strengthening, NOT the enforcement: fabric.client.complete()'s parse/validate/
    retry remains the guarantee (R1-FOLD F9). If the server rejects/ignores json_schema, the call
    raises (urlopen on a 400) → complete() retries → FabricError (fail loud, never silent — rule 4).
    """
    if opts.get("json_schema") is not None:
        body["response_format"] = {"type": "json_schema", "json_schema": opts["json_schema"]}
    elif opts.get("schema") is not None or opts.get("json"):
        body["response_format"] = {"type": "json_object"}      # structured-output request (existing path)


def openai_transport(base_url: str = DEFAULT_BASE_URL, api_key: str = "ollama", timeout: int = DEFAULT_TIMEOUT):
    """Build a transport bound to an OpenAI-compatible endpoint.

    `timeout` defaults from config (DEFAULT_TIMEOUT — not a bare literal; D2). The single-call
    ceiling: long enough a slow-but-progressing cloud call succeeds vs being killed + re-queued.
    A batch caller may override with DEFAULT_CLOUD_TIMEOUT."""
    def transport(model: str, messages: list, **opts) -> str:
        forbid_gemini(model)                                   # hard constraint, fail loud
        body = {"model": model, "messages": messages, "stream": False}
        _apply_response_format(body, opts)                     # json_schema branch › json_object › off
        for k in ("temperature", "max_tokens", "top_p"):
            if k in opts:
                body[k] = opts[k]
        req = urllib.request.Request(
            base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
        # OpenAI shape: choices[0].message.content
        return (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
    return transport


def openai_tools_transport(base_url: str = DEFAULT_BASE_URL, api_key: str = "ollama", timeout: int = DEFAULT_TIMEOUT):
    """Build a NATIVE TOOL-CALLING transport bound to an OpenAI-compatible endpoint.

    A SIBLING of openai_transport / openai_embeddings_transport — built so the 12+ string-callers
    of openai_transport are untouched (they depend on the bare-content-string return). The contract
    here is `(model, messages, tools=..., tool_choice=...) -> message dict {content, tool_calls}`,
    wrapped by fabric.client.complete_with_tools (a tool_call with empty content is SUCCESS, not the
    empty-failure of complete()). Identical request build to openai_transport (response_format / temp /
    max_tokens / top_p), PLUS body["tools"] + body["tool_choice"] when tools are passed. Every fleet
    CHAT model supports native tools (capabilities → "tools"); only embedders don't. NO Gemini (FIRST)."""
    def transport(model: str, messages: list, **opts) -> dict:
        forbid_gemini(model)                                   # hard constraint, fail loud, FIRST
        body = {"model": model, "messages": messages, "stream": False}
        _apply_response_format(body, opts)                     # json_schema branch › json_object › off
        for k in ("temperature", "max_tokens", "top_p"):
            if k in opts:
                body[k] = opts[k]
        tools = opts.get("tools")
        if tools:                                              # only add the tool keys when tools passed
            body["tools"] = tools
            body["tool_choice"] = opts.get("tool_choice", "auto")
        req = urllib.request.Request(
            base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
        # OpenAI shape: choices[0].message = {role, content, tool_calls?}. Return the WHOLE message
        # dict (NOT the bare content) so the caller sees tool_calls alongside content.
        return (data.get("choices") or [{}])[0].get("message", {}) or {}
    return transport


def model_supports_tools(model: str, base_url: str = DEFAULT_BASE_URL, api_key: str = "ollama",
                         timeout: int = 8, endpoint: str = "ollama") -> bool:
    """Endpoint-aware, FAIL-LOUD tool-capability detection (rule 4 — no silent assume-capable).

    Returns True/False ONLY when the endpoint actually TELLS us; if capability cannot be determined
    (endpoint unreachable, no capabilities field, unknown endpoint kind), it RAISES — a silent
    can't-detect would be a silent fallback (forbidden). NO Gemini (forbidden first, fail loud).

      - endpoint='ollama'  : POST {base sans /v1}/api/show {"model":…}; capabilities contains "tools".
                             nomic-embed-text returns capabilities WITHOUT "tools" → a clean False.
      - endpoint='litellm' : the proxy's model_info / supports_function_calling field. (Proxy was
                             down at probe — implemented per the documented field; any failure or a
                             missing field RAISES, never assume-capable.)
      - endpoint='vllm'    : a raw vLLM OpenAI endpoint has no caps field to read, so we PROBE: a tiny
                             chat completion with a forced tool_choice. A server launched with
                             --enable-auto-tool-choice honours it and returns a tool_call (→ True); one
                             without tool support errors on the forced choice (→ raises, fail loud). This
                             is an honest runtime VERIFICATION, not an assume — vLLM is supported
                             natively (no need to route through litellm just to read a flag).
      - any other endpoint : RAISE (cannot determine).
    """
    forbid_gemini(model)                                       # hard constraint, fail loud, FIRST
    root = base_url.rstrip("/")
    if root.endswith("/v1"):
        root = root[:-3].rstrip("/")                           # /api/show is at the ROOT, not under /v1

    if endpoint == "ollama":
        req = urllib.request.Request(
            root + "/api/show",
            data=json.dumps({"model": model}).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:   # unreachable → raises → fail loud
            data = json.loads(r.read())
        caps = data.get("capabilities")
        if not isinstance(caps, list):                            # cannot determine → fail loud
            raise ValueError(
                f"fabric: cannot determine tool-capability for {model!r} — ollama /api/show "
                f"returned no 'capabilities' list (never assume-capable)"
            )
        return "tools" in caps

    if endpoint == "litellm":
        req = urllib.request.Request(
            root + "/model/info",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:   # unreachable → raises → fail loud
            data = json.loads(r.read())
        for entry in (data.get("data") or []):
            if entry.get("model_name") == model or (entry.get("litellm_params") or {}).get("model") == model:
                info = entry.get("model_info") or {}
                if "supports_function_calling" in info:
                    return bool(info["supports_function_calling"])
        raise ValueError(
            f"fabric: cannot determine tool-capability for {model!r} via LiteLLM model_info "
            f"(no supports_function_calling field; never assume-capable)"
        )

    if endpoint == "vllm":
        # No caps field on a raw vLLM endpoint → PROBE by forcing a trivial tool call. A tool-enabled
        # vLLM (--enable-auto-tool-choice) honours the forced tool_choice and returns a tool_call;
        # a server without tool support 400s on the forced choice → urlopen raises → fail loud (never
        # assume-capable). A 200 that returns NO tool_calls → the model didn't actually call it → False.
        probe_tool = {"type": "function", "function": {
            "name": "ping", "description": "health probe",
            "parameters": {"type": "object", "properties": {}}}}
        body = {"model": model, "messages": [{"role": "user", "content": "ping"}],
                "tools": [probe_tool], "tool_choice": {"type": "function", "function": {"name": "ping"}},
                "max_tokens": 8, "stream": False}
        req = urllib.request.Request(
            root + "/v1/chat/completions", data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
        with urllib.request.urlopen(req, timeout=timeout) as r:   # 400/unreachable → raises → fail loud
            data = json.loads(r.read())
        msg = (data.get("choices") or [{}])[0].get("message", {}) or {}
        return bool(msg.get("tool_calls"))                        # honoured the forced tool → supports tools

    raise ValueError(
        f"fabric: cannot determine tool-capability for {model!r} — unknown endpoint kind "
        f"{endpoint!r} (never assume-capable)"
    )


def openai_embeddings_transport(base_url: str = DEFAULT_EMBED_URL, api_key: str = "none", timeout: int = DEFAULT_TIMEOUT):
    """Build an EMBEDDINGS transport bound to an OpenAI-compatible /v1/embeddings endpoint.

    A SIBLING of openai_transport (a vector response is not a chat response). The contract is
    `(model, inputs: list[str]) -> list[list[float]]` — fabric.client.complete_embeddings wraps
    it with vector guards (NOT the text-shaped guards of complete()). Repointable by base_url
    (BGE-M3 @ :8001 is the only live, dim-grounded one). NO Gemini (enforced first, fail loud).

    `timeout` defaults from config (DEFAULT_TIMEOUT — config-driven). Endpoint is LOCAL (:8001),
    not high-variance cloud, so it stays MODERATE — deliberately not the cloud ceiling."""
    def transport(model: str, inputs: list) -> list:
        forbid_gemini(model)                                   # hard constraint, fail loud, FIRST
        body = {"model": model, "input": inputs}               # OpenAI /v1/embeddings shape
        req = urllib.request.Request(
            base_url.rstrip("/") + "/embeddings",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
        # OpenAI shape: {"data":[{"embedding":[...],"index":i},...]} -> the bare vectors
        return [d["embedding"] for d in (data.get("data") or [])]
    return transport
