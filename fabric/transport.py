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


def openai_transport(base_url: str = DEFAULT_BASE_URL, api_key: str = "ollama", timeout: int = DEFAULT_TIMEOUT):
    """Build a transport bound to an OpenAI-compatible endpoint.

    `timeout` defaults from config (DEFAULT_TIMEOUT — not a bare literal; D2). The single-call
    ceiling: long enough a slow-but-progressing cloud call succeeds vs being killed + re-queued.
    A batch caller may override with DEFAULT_CLOUD_TIMEOUT."""
    def transport(model: str, messages: list, **opts) -> str:
        forbid_gemini(model)                                   # hard constraint, fail loud
        body = {"model": model, "messages": messages, "stream": False}
        if opts.get("schema") is not None or opts.get("json"):
            body["response_format"] = {"type": "json_object"}  # structured-output request
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
