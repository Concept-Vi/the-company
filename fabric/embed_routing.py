"""fabric/embed_routing.py — the ONE embedder-routing table (P2.2, the-one-system wirings).

WHICH embedder turns a text query into a vector for a given SPACE. One table, every face uses it —
the /api/query bridge route AND the `coordinate` MCP tool (never a second dialect): the space's stored
vectors fix the lens; a query embedded under any other lens is a cross-dim/cross-space lie.

  code · symbol · scale:code:* · scale:symbol:*   → nomic-embed-code (ollama :11434, 3584-dim,
                                                    options.num_ctx set — the silent-truncation guard)
  everything else                                 → the fabric default (pplx-2560 @ :8007)

Additive: a NEW space with a new lens = one ROUTES entry (or rely on the default). Fail-loud: routing
never guesses a model that isn't resident — errors carry the endpoint + the fix.
"""
from __future__ import annotations

# space (or its scale:<space>: prefix) → the lens family
_NOMIC_SPACES = {"code", "symbol"}


def lens_for_space(space: str | None) -> str:
    """'nomic' | 'pplx' — which lens family embeds queries against this space."""
    if not space:
        return "pplx"
    base = space.split(":", 2)[1] if space.startswith("scale:") else space
    return "nomic" if base in _NOMIC_SPACES else "pplx"


def embed_query(text: str, *, space: str | None = None) -> list:
    """text → the query vector under the RIGHT lens for `space`. Raises loud (endpoint + fix) on an
    unreachable embedder — never a fabricated/zero vector, never the wrong lens."""
    lens = lens_for_space(space)
    if lens == "nomic":
        import json
        import urllib.request
        body = json.dumps({"model": "nomic-embed-code", "input": text,
                           "options": {"num_ctx": 32768}}).encode()
        req = urllib.request.Request("http://127.0.0.1:11434/api/embed", data=body,
                                     headers={"Content-Type": "application/json"})
        try:
            return json.loads(urllib.request.urlopen(req, timeout=90).read())["embeddings"][0]
        except Exception as e:
            raise RuntimeError(
                f"embed_routing: nomic lens unreachable for space {space!r} (ollama :11434 — "
                f"{type(e).__name__}: {e}). Fix: `company up ollama` / check `company gpu`.") from e
    from fabric import client, transport, config as fcfg
    try:
        t = transport.openai_embeddings_transport(base_url=fcfg.DEFAULT_EMBED_URL)
        return client.complete_embeddings(t, [text], model=fcfg.DEFAULT_EMBED_MODEL,
                                          dim=fcfg.DEFAULT_EMBED_DIM)[0]
    except Exception as e:
        raise RuntimeError(
            f"embed_routing: pplx lens unreachable for space {space!r} ({fcfg.DEFAULT_EMBED_URL} — "
            f"{type(e).__name__}: {e}). Fix: `company up embed-pplx` / check `company gpu`.") from e
