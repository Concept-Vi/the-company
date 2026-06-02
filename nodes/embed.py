"""embed — text → Vector, via the guarded embeddings fabric (E1–E5). See nodes/AGENTS.md.

A process node: one Text input → one Vector output (a list[float]). Calls the embeddings
endpoint through fabric.client.complete_embeddings (the vector-guarded SIBLING of complete()
— a vector response is not a chat response). The embedding endpoint is its OWN base_url
(BGE-M3 @ :8001, 1024-dim — the only live, dim-grounded embedder); model/endpoint are
swappable config slots, resolved from the live registry (`options_from`), never invented.

NOT VOLATILE: a pure transform of its input text — the same text always embeds the same way,
so the memo gate may reuse the cached vector. ('Vector' is a new port-type string; the connect
type-check passes Vector↔Vector and rejects Vector↔Text, which is correct.)
"""
# Module-level: CONFIG defaults reference these constants (CONFIG is evaluated at import).
# fabric.config imports only `os`, so this is safe during node discovery. One source — never
# hardcode the model literal here (that would duplicate the constant + violate one-source).
from fabric.config import DEFAULT_EMBED_URL, DEFAULT_EMBED_MODEL

VERSION = "1"
KIND = "process"
PORTS_IN = {"text": "Text"}
PORTS_OUT = {"vector": "Vector"}

# Nested field-descriptor CONFIG (Implementation-Guide Section A: {key:{type,label,default,options_from?}}).
# The descriptor drives the inspector; run()'s .get(..., default) fallbacks make a bare node
# (config == {}) run today. `embed_models` resolves at runtime against the embedding endpoint's
# live list (Lane B) — the registry is the source of truth; the dropdown is never hand-typed.
CONFIG = {
    "model":    {"type": "enum",   "label": "Embedding model", "default": DEFAULT_EMBED_MODEL,
                 "options_from": "embed_models"},
    "base_url": {"type": "string", "label": "Endpoint", "default": DEFAULT_EMBED_URL},
    "retries":  {"type": "number", "label": "Retries", "default": 3, "min": 0, "max": 10},
}


def run(inputs: dict, config: dict):
    from fabric import client, transport, config as fcfg
    model = config.get("model", fcfg.DEFAULT_EMBED_MODEL)
    base_url = config.get("base_url", fcfg.DEFAULT_EMBED_URL)
    retries = config.get("retries", 3)
    t = transport.openai_embeddings_transport(base_url=base_url)
    # complete_embeddings returns one vector per input; we send a single text → take [0].
    # A JSON-serializable list[float] (the Vector). Fail-loud is inside complete_embeddings.
    return client.complete_embeddings(t, [str(inputs.get("text", ""))], model=model, retries=retries)[0]
