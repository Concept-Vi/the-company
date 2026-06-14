#!/usr/bin/env bash
# ops/serve_rerank.sh — launch the Company rerank endpoint in ~/vllm-env (torch+transformers already
# present), CPU-PINNED (no GPU touch — keeps the @xsession loadout intact). Mirrors serve_pplx_embed.sh.
set -euo pipefail
OPS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export CUDA_VISIBLE_DEVICES=""          # force CPU — 0 VRAM, no contention with the GPU loadout
export COMPANY_RERANK_PORT="${COMPANY_RERANK_PORT:-8008}"
cd "$HOME/vllm-env" && exec ./bin/python "$OPS/serve_rerank.py"
