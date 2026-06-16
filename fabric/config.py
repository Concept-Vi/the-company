"""fabric/config.py — fabric configuration (S6). See fabric/AGENTS.md.

Where the unified endpoint lives + the hard constraints. The LiteLLM proxy is the
intended endpoint (its own 3.12 venv); ollama's own OpenAI-compatible /v1 is the
direct fallback. Everything is configurable (D2). NO Gemini — enforced, fail loud.
"""
from __future__ import annotations
import os

# Shared addressed store (ext4, not /mnt/c). Both faces (UI bridge + MCP) use this one
# path, so they operate the SAME substrate — one brain, two faces.
STORE_DIR = os.environ.get("COMPANY_STORE", os.path.expanduser("~/company/.data/store"))

# The fabric calls ONE OpenAI-compatible endpoint. Point at the LiteLLM proxy when up,
# else ollama's own /v1 directly. Override via env.
LITELLM_PROXY = os.environ.get("COMPANY_LITELLM_URL", "http://localhost:4100/v1")
OLLAMA_DIRECT = os.environ.get("COMPANY_OLLAMA_URL", "http://localhost:11434/v1")
DEFAULT_BASE_URL = os.environ.get("COMPANY_FABRIC_URL", OLLAMA_DIRECT)

# The right-hand-man's default brain (D2): ollama-cloud, swappable.
DEFAULT_BRAIN = os.environ.get("COMPANY_BRAIN", "deepseek-v4-pro:cloud")

# Embeddings have their OWN endpoint — they are NOT in litellm.config.yaml and DEFAULT_BASE_URL
# is ollama :11434 (chat). OPERATIVE EMBEDDER (2026-06-16 switch, bge->pplx): pplx-embed-context-v1-4b
# @ :8007, 2560-dim INT8 — the LIVE GPU-served embedder. BGE-M3 @ :8001 is DORMANT (endpoint down; its
# 1024-dim vectors stay intact at the bare/None layer + vectors.bge-backup-20260615, reachable only if
# revived). Other embedders' dims are NOT doc-grounded — resolve at runtime, never hardcode them here.
DEFAULT_EMBED_URL = os.environ.get("COMPANY_EMBED_URL", "http://localhost:8007/v1")
DEFAULT_EMBED_MODEL = os.environ.get("COMPANY_EMBED_MODEL", "perplexity-ai/pplx-embed-context-v1-4b")

# Timeouts (D2 configurable; was an orphaned literal in transport.py). Levers SPLIT, not co-bumped
# (worst-case wall-clock = retries × timeout): a longer TIMEOUT fixes slow-but-succeeding cloud calls;
# jittered RETRY (client.py) fixes transient hard failures. CLOUD ceiling is for batch/cloud-brain nodes.
DEFAULT_TIMEOUT = int(os.environ.get("COMPANY_FABRIC_TIMEOUT", "180"))
DEFAULT_CLOUD_TIMEOUT = int(os.environ.get("COMPANY_CLOUD_TIMEOUT", "300"))

# Embedder dim contract (rule 4): pplx-embed-context-v1-4b = 2560-dim. Config-driven, not a node literal —
# a wrong-length vector FAILS LOUD at the fabric, never flows through as a bad cosine.
DEFAULT_EMBED_DIM = int(os.environ.get("COMPANY_EMBED_DIM", "2560"))

# OPERATIVE EMBEDDING LAYER (multi-layer #emb=<tag> model): the storage layer the corpus read/write paths
# resolve to when a caller does NOT pin one. 'pplx' = the live pplx-2560 layer is the default; the bge
# bare/None layer stays reachable EXPLICITLY (emb=None / 'bge'). ONE knob reverts the whole core.
DEFAULT_EMB_LAYER = os.environ.get("COMPANY_EMB_LAYER", "pplx")
EMB_LAYER_DEFAULT = "__default__"   # sentinel: caller omitted emb -> use DEFAULT_EMB_LAYER


def resolve_emb_layer(emb):
    """Resolve a caller's emb arg to a concrete storage-layer tag for store.space_address.
    - EMB_LAYER_DEFAULT (the param default -> caller did NOT pin a layer) -> DEFAULT_EMB_LAYER ('pplx').
    - None / '' / 'bge' / 'bare' -> None (the bare/legacy default-layer key — bge reachable explicitly).
    - any other string -> that explicit layer tag (e.g. 'pplx').
    Idempotent on an already-resolved value (resolve_emb_layer('pplx')=='pplx', resolve_emb_layer(None) is None)."""
    if emb == EMB_LAYER_DEFAULT:
        emb = DEFAULT_EMB_LAYER
    if emb in (None, "", "bge", "bare"):
        return None
    return emb

FORBIDDEN = ("gemini",)   # hard constraint


def forbid_gemini(model: str) -> None:
    low = (model or "").lower()
    if any(f in low for f in FORBIDDEN):
        raise ValueError(f"fabric: model {model!r} is forbidden (NO Gemini, ever)")
