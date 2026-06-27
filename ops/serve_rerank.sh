#!/usr/bin/env bash
# ops/serve_rerank.sh — launch the Company rerank endpoint in ~/vllm-env (torch+transformers already
# present). GPU by default (2026-06-28, Tim): jina-v3 listwise rerank is attention-bound, so CPU was the
# bottleneck (~16s on realistic chunks); cuda is the real fix. Mirrors serve_pplx_embed.sh's toolchain.
# Override back to CPU with COMPANY_RERANK_DEVICE=cpu (then it sets CUDA_VISIBLE_DEVICES="" itself).
set -euo pipefail
OPS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export COMPANY_RERANK_PORT="${COMPANY_RERANK_PORT:-8008}"
export COMPANY_RERANK_DEVICE="${COMPANY_RERANK_DEVICE:-cuda}"
# CUDA toolchain (shared cu13 stack, same as serve_pplx_embed.sh / serve_model.sh) — only when on GPU.
if [ "$COMPANY_RERANK_DEVICE" = "cpu" ]; then
  export CUDA_VISIBLE_DEVICES=""
else
  export CUDA_HOME="$HOME/vllm-env/lib/python3.12/site-packages/nvidia/cu13"
  export PATH="$CUDA_HOME/bin:$PATH"
  export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
fi
echo "[serve_rerank] PID=$$ port=$COMPANY_RERANK_PORT device=$COMPANY_RERANK_DEVICE"
cd "$HOME/vllm-env" && exec ./bin/python "$OPS/serve_rerank.py"
