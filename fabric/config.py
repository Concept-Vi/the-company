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

FORBIDDEN = ("gemini",)   # hard constraint


def forbid_gemini(model: str) -> None:
    low = (model or "").lower()
    if any(f in low for f in FORBIDDEN):
        raise ValueError(f"fabric: model {model!r} is forbidden (NO Gemini, ever)")
