#!/usr/bin/env bash
# serve_pplx_embed.sh — start the pplx-embed-context-v1-4b transformers server.
#
# CUSTOM (non-vLLM) embedder, mirroring the serve_jina_v4.sh precedent: vLLM 0.21
# lacks this model's arch (PPLXQwen3Model / bidirectional_pplx_qwen3, remote-code),
# so it runs via raw transformers behind FastAPI (ops/serve_pplx_embed.py).
#
# venv: reuses ~/vllm-env (already carries torch 2.11+cu130, transformers 5.9.0,
# fastapi, uvicorn, huggingface_hub — all the custom modeling.py needs). Kept lean
# for this throwaway interim rather than building a redundant multi-GB venv.
set -euo pipefail
OPS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$HOME/vllm-env/bin/activate"

# CUDA toolchain (shared cu13 stack, same as serve_jina_v4.sh / serve_model.sh).
export CUDA_HOME="$HOME/vllm-env/lib/python3.12/site-packages/nvidia/cu13"
export PATH="$CUDA_HOME/bin:$PATH"

export PPLX_EMBED_MODEL="${PPLX_EMBED_MODEL:-perplexity-ai/pplx-embed-context-v1-4b}"
export PPLX_EMBED_PORT="${PPLX_EMBED_PORT:-8007}"
export PPLX_EMBED_DTYPE="${PPLX_EMBED_DTYPE:-bfloat16}"

echo "[serve_pplx_embed] PID=$$ model=$PPLX_EMBED_MODEL port=$PPLX_EMBED_PORT dtype=$PPLX_EMBED_DTYPE"
exec python "$OPS/serve_pplx_embed.py"
