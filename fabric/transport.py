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


# The vLLM/OpenAI SAMPLING family — the ALLOWLIST of opts keys that are forwarded VERBATIM into the
# request body. ONE source, iterated by BOTH chat transports (reuse — never two divergent inline tuples).
# An ALLOWLIST, deliberately (not a denylist): so `meta`/`tools`/`tool_choice`/`json_schema`/`schema`/`json`
# (the OUT-PARAMS + the structured-output triggers, handled by _apply_response_format / _fill_meta) can NEVER
# leak into the body. A key ABSENT from opts is not added → the call is BYTE-IDENTICAL to before for any
# caller not passing it (the behaviour-preserving guarantee). It is an ORDERED TUPLE, not a set, ON PURPOSE:
# _apply_sampling inserts keys in THIS order, and json.dumps serializes in dict-insertion order — so with the
# original three FIRST, a call passing none of the new keys produces byte-for-byte the SAME request as the
# pre-change inline `(temperature, max_tokens, top_p)` loop (a hash-ordered set would reorder the bytes for
# any ≥2-key call — same keys/values, but not byte-identical). This is the seam the generation-policy
# rep_penalty LADDER's `repetition_penalty` rides through to vLLM (it is a valid vLLM sampling param); the
# rest of the family (frequency/presence_penalty, top_k, min_p, stop, seed, n) ride the SAME seam, so a
# policy declaring any of them reaches the model with no further transport edit (registry-driven, general —
# not a single hardcoded key). vLLM accepts these as top-level request fields (OpenAI-compatible + its
# documented sampling extensions); an endpoint that doesn't recognise one ignores it (forward-compatible).
_SAMPLING_KEYS = (
    "temperature", "max_tokens", "top_p",                  # the original three, FIRST + IN ORDER (byte-identical)
    "repetition_penalty",                                  # the O2 generation-policy ladder rung → vLLM
    "frequency_penalty", "presence_penalty",               # OpenAI sampling penalties
    "top_k", "min_p",                                      # vLLM sampling extensions
    "stop", "seed", "n",                                   # stop sequences · determinism seed · draw count
)


def _apply_sampling(body: dict, opts: dict) -> None:
    """Forward every PRESENT sampling-family key from opts into the request body, VERBATIM — the ONE
    sampling passthrough shared by openai_transport AND openai_tools_transport (reuse, single-source so the
    two agree by construction). Allowlist-gated (`_SAMPLING_KEYS`): an out-param (`meta`) or a structured-
    output trigger (`json_schema`/`schema`/`json`) is NOT in the set, so it can never reach the body. A key
    absent from opts is not added → the request is byte-identical to before for any caller not passing it."""
    for k in _SAMPLING_KEYS:
        if k in opts:
            body[k] = opts[k]


def _apply_response_format(body: dict, opts: dict) -> None:
    """Set body["response_format"] from opts — the ONE structured-output decision, shared by
    openai_transport AND openai_tools_transport (single-source so the two transports agree by
    construction; reuse, not a second copy). Precedence (schema-additive — C2 / R1-FOLD F9):

      1. opts["json_schema"]  → response_format {"type":"json_schema","json_schema": <dict>}.
         SERVER-SIDE schema-CONSTRAINED decoding (vLLM ≥0.21 guided/structured outputs). The caller
         passes the FULL OpenAI/vLLM json_schema object — {"name": <role_id>, "schema": <JSON schema>}
         (the actual schema nests UNDER "schema", "name" is its sibling; flattening 400s the server).
         WIRED (G24): fabric.client.complete() now DERIVES this opt from its `schema=` Pydantic class
         ({"name": <class name>, "schema": schema.model_json_schema()}) unless the caller passed
         `json_schema` explicitly (even None — the opt-out) — so EVERY schema= caller (run_role's
         role.output_schema, coa's CoaFraming) gets the guided decode, and a role fire cannot emit
         schema-invalid JSON at the decoder. Client-side validate/retry stays the guarantee (F9).
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


def _apply_thinking(body: dict, opts: dict) -> None:
    """Set body["chat_template_kwargs"]["enable_thinking"] from opts["think"] — the vLLM stack's
    USE-CONTRACT for the `reasoning` capability (the capability-type's vLLM use_ref). Shared by BOTH
    openai_transport AND openai_tools_transport, so the text path (run_role) and the tools path
    (chat_parts) honor reasoning identically — patching only one would silently skip the RHM chat path.
    The vLLM /v1 path carries thinking in chat_template_kwargs (the model's OWN official template gates on
    enable_thinking — verified byte-identical to Qwen/Qwen3.5-4B); ollama_native_transport carries it as
    body.think instead (that stack's own contract). ONE opt key — `think` — across BOTH stacks (NOT a second
    name like `thinking`: ollama_native_transport already reads opts["think"] and cognition already emits it,
    so a divergent key would silently bypass one path). Each stack TRANSLATES the one `think` bool to its own
    mechanism: vLLM → chat_template_kwargs.enable_thinking (here); ollama → body.think. Absent opts["think"]
    → no key added (byte-identical for any caller not requesting it). The DECISION to think (per role/mode,
    ONLY iff the model declares the `reasoning` capability) is the resolver's use-gate UPSTREAM; the transport
    only forwards. vLLM 0.21 returns the split reasoning in message.`reasoning` (NOT reasoning_content); a
    thinking turn that returns no reasoning is drift → the caller loud-fails, never falls back."""
    if opts.get("think") is not None:
        body.setdefault("chat_template_kwargs", {})["enable_thinking"] = bool(opts["think"])


def _fill_meta(opts: dict, data: dict) -> None:
    """ADDITIVE finish_reason + token-count passthrough (O3). If the caller passed a `meta={}` dict in
    opts, fill it IN PLACE from the response envelope — WITHOUT touching the transport's return type, so
    every one of the 12+ bare-content-string callers is byte-unaffected (the out-param is invisible to
    them: they pass no `meta`, so this is a no-op). `meta` rides `**opts` straight through
    fabric.client.complete() (which forwards `**opts` to the transport) and NEVER enters the request body
    (the body only reads response_format + the allowlisted `_SAMPLING_KEYS` family via _apply_sampling —
    `meta` is NOT in that allowlist, so a stray `meta` key can't pollute the request), never `meta`.

    Why the TRANSPORT fills it (not the client): the transport is the ONLY layer that sees the raw OpenAI
    envelope (`choices[0].finish_reason`, `usage`). `complete()` re-runs the transport per retry attempt and
    overwrites `meta` each time, so it naturally lands on the SUCCESSFUL attempt's values (fail-loud chain
    unchanged — meta is decoration, never the guarantee).

      - finish_reason: choices[0].finish_reason — 'stop' (clean) | 'length' (TRUNCATED → grammar/JSON
        output is INVALID; the O3 signal the engine persists) | 'tool_calls' | 'content_filter' | None.
      - usage: the token counts (prompt_tokens / completion_tokens / total_tokens) when the server reports
        them (vLLM does); None-safe (an endpoint that omits usage → usage stays absent, never a crash).
    """
    meta = opts.get("meta")
    if meta is None:
        return                                                 # no out-param requested → no-op (default)
    choices = data.get("choices") or [{}]
    meta["finish_reason"] = choices[0].get("finish_reason")    # may be None — passed through honestly
    usage = data.get("usage")
    if isinstance(usage, dict):
        meta["usage"] = usage                                  # {prompt_tokens, completion_tokens, total_tokens}


def openai_transport(base_url: str = DEFAULT_BASE_URL, api_key: str = "ollama", timeout: int = DEFAULT_TIMEOUT):
    """Build a transport bound to an OpenAI-compatible endpoint.

    `timeout` defaults from config (DEFAULT_TIMEOUT — not a bare literal; D2). The single-call
    ceiling: long enough a slow-but-progressing cloud call succeeds vs being killed + re-queued.
    A batch caller may override with DEFAULT_CLOUD_TIMEOUT."""
    def transport(model: str, messages: list, **opts) -> str:
        forbid_gemini(model)                                   # hard constraint, fail loud
        body = {"model": model, "messages": messages, "stream": False}
        _apply_response_format(body, opts)                     # json_schema branch › json_object › off
        _apply_sampling(body, opts)                            # the sampling family (temp/max_tokens/top_p/repetition_penalty/…), allowlist-gated
        _apply_thinking(body, opts)                            # the reasoning capability's vLLM use-contract (chat_template_kwargs.enable_thinking)
        req = urllib.request.Request(
            base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
        _fill_meta(opts, data)                                 # ADDITIVE finish_reason+usage out-param (O3); no-op without meta=
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
        _apply_sampling(body, opts)                            # the sampling family (temp/max_tokens/top_p/repetition_penalty/…), allowlist-gated
        _apply_thinking(body, opts)                            # the reasoning capability's vLLM use-contract (chat_template_kwargs.enable_thinking)
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
        _fill_meta(opts, data)                                 # ADDITIVE finish_reason+usage out-param (O3); no-op without meta=
        # OpenAI shape: choices[0].message = {role, content, tool_calls?}. Return the WHOLE message
        # dict (NOT the bare content) so the caller sees tool_calls alongside content.
        return (data.get("choices") or [{}])[0].get("message", {}) or {}
    return transport


def ollama_native_transport(base_url: str = DEFAULT_BASE_URL, api_key: str = "ollama", timeout: int = DEFAULT_TIMEOUT):
    """NATIVE ollama /api/chat transport — the ONE path that honours THINK-CONTROL. The OpenAI /v1 path
    SILENTLY IGNORES `think` (verified: a reasoning model still reasoned, content empty); ollama's native
    `/api/chat` honours `"think": false` → the hidden reasoning trace is suppressed (VERIFIED by-use: 1304→43
    output-tokens on kimi-k2.6:cloud, a 30× collapse). A SIBLING of openai_transport — the /v1 string-callers
    are untouched; this is used by run_role ONLY when a `think` value is set on an ollama-served model.

    `base_url` is the OpenAI base (…/v1) → the native endpoint is <host>/api/chat. ollama sampling rides
    `options` (`num_predict` = max_tokens). `format` (ollama structured output) is set from json_schema/schema
    when present — BUT cloud reasoning models honour it INCONSISTENTLY (verified — may return prose), so the
    caller's schema validate/retry (client.complete) stays the guarantee, and clean structured EXTRACTION
    belongs on a LOCAL vLLM model via /v1, not this path. Contract: (model, messages, **opts) -> content_str.
    NO Gemini (FIRST)."""
    def transport(model: str, messages: list, **opts) -> str:
        forbid_gemini(model)                                   # hard constraint, fail loud, FIRST
        host = base_url.rstrip("/")
        if host.endswith("/v1"):
            host = host[:-3].rstrip("/")                       # …/v1 → the native host root
        body = {"model": model, "messages": messages, "stream": False}
        if "think" in opts:
            body["think"] = bool(opts["think"])                # the whole point — /v1 can't carry this
        options = {}
        if opts.get("temperature") is not None:
            options["temperature"] = opts["temperature"]
        if opts.get("max_tokens") is not None:                 # None = NO budget (cloud runs to completion,
            options["num_predict"] = opts["max_tokens"]        # Tim 2026-07-07) — never send num_predict=None
        if options:
            body["options"] = options
        # structured output (best-effort; cloud-inconsistent — validate/retry is the guarantee, not this)
        if opts.get("json_schema") is not None:
            js = opts["json_schema"]
            body["format"] = js.get("schema", js) if isinstance(js, dict) else js
        elif opts.get("schema") is not None or opts.get("json"):
            body["format"] = "json"
        req = urllib.request.Request(
            host + "/api/chat",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
        # native shape: {message:{role,content,thinking?}, eval_count, prompt_eval_count, done_reason}
        meta = opts.get("meta")
        if meta is not None:                                   # O3 out-param, native field names mapped
            meta["finish_reason"] = data.get("done_reason")
            ec, pc = data.get("eval_count"), data.get("prompt_eval_count")
            if ec is not None:
                meta["usage"] = {"completion_tokens": ec, "prompt_tokens": pc,
                                 "total_tokens": (ec or 0) + (pc or 0)}
        return (data.get("message") or {}).get("content", "")
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
      - endpoint='vllm'    : a raw vLLM OpenAI endpoint has no caps field to read AND the forced
                             tool_choice probe is RETIRED (capability-resolution deliverable c, Tim
                             2026-06-29). The forced probe was the SAME brittle mechanism that mislabelled
                             the 4B as "can't tool-call": a forced tool_choice + --reasoning-parser
                             false-negatives (vLLM #19051/#39056), and "disabling thinking to make the
                             probe pass" papers over a mechanism that shouldn't exist. DECLARATION IS
                             TRUTH — a vLLM model's tool capability is DECLARED in the catalog
                             (model_capabilities.json / the family). _model_supports_tools reads that
                             declaration FIRST; this helper is reached for a vLLM endpoint ONLY when the
                             model is UNDECLARED, and an undeclared vLLM model FAILS LOUD here (raise —
                             "declare this model"), it is NEVER coerced through a forced choice. No probe,
                             no silent assume, no thinking-disable.
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
        # FORCED-CHOICE PROBE RETIRED (deliverable c — Tim 2026-06-29: declaration is truth; the forced
        # tool_choice probe is the brittle mechanism that mislabelled the 4B and conflicts with the
        # reasoning-parser, vLLM #19051/#39056). _model_supports_tools reads the DECLARATION first and only
        # delegates here for a vLLM model that is UNDECLARED in the catalog. An undeclared vLLM model is not
        # coerced through a forced choice — it FAILS LOUD so the operator DECLARES it (the no-silent-assume
        # law). This dissolves the false-incapable class by construction: a declared model can never be
        # demoted by a flaky probe, and an undeclared one surfaces as a missing declaration, never a
        # mislabel. (Tools still flow on the REAL chat path with tool_choice="auto", where thinking + tools
        # coexist naturally — that path needs no probe.)
        raise ValueError(
            f"fabric: cannot determine tool-capability for {model!r} on a raw vLLM endpoint — the forced "
            f"tool_choice probe is RETIRED (deliverable c). DECLARATION IS TRUTH: declare this model's tool "
            f"capability in ops/model_capabilities.json (or via its family), then it resolves without any "
            f"probe. FAIL LOUD, never assume-capable, never force a tool_choice (it false-negatives under "
            f"--reasoning-parser).")

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
