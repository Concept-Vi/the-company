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
# is ollama :11434 (chat). BGE-M3 @ :8001 is the only LIVE, dim-grounded embedder (1024-dim dense).
# Other embedders' dims are NOT doc-grounded — resolve at runtime, never hardcode them here.
DEFAULT_EMBED_URL = os.environ.get("COMPANY_EMBED_URL", "http://localhost:8001/v1")
DEFAULT_EMBED_MODEL = os.environ.get("COMPANY_EMBED_MODEL", "BAAI/bge-m3")

# Timeouts (D2 configurable; was an orphaned literal in transport.py). Levers SPLIT, not co-bumped
# (worst-case wall-clock = retries × timeout): a longer TIMEOUT fixes slow-but-succeeding cloud calls;
# jittered RETRY (client.py) fixes transient hard failures. CLOUD ceiling is for batch/cloud-brain nodes.
DEFAULT_TIMEOUT = int(os.environ.get("COMPANY_FABRIC_TIMEOUT", "180"))
DEFAULT_CLOUD_TIMEOUT = int(os.environ.get("COMPANY_CLOUD_TIMEOUT", "300"))

# Embedder dim contract (rule 4): BGE-M3 = 1024-dim. Config-driven, not a node literal — a
# wrong-length vector FAILS LOUD, never flows through as a bad cosine.
DEFAULT_EMBED_DIM = int(os.environ.get("COMPANY_EMBED_DIM", "1024"))

FORBIDDEN = ("gemini",)   # hard constraint


def forbid_gemini(model: str) -> None:
    low = (model or "").lower()
    if any(f in low for f in FORBIDDEN):
        raise ValueError(f"fabric: model {model!r} is forbidden (NO Gemini, ever)")
