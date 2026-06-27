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
# 8-bit by default (2026-06-28, Tim): clean swap to bitsandbytes 8-bit weights — saves ~2.9GB,
# verified vector-compatible with the bf16-embedded corpus (cosine 0.996, top-k overlap ~0.97 →
# NO re-embed). Still overridable: PPLX_EMBED_8BIT=0 restores the bf16 path byte-identically.
export PPLX_EMBED_8BIT="${PPLX_EMBED_8BIT:-1}"
# Memory-envelope bound (2026-06-15, lead) — pairs with the model_max_length + batch caps in
# serve_pplx_embed.py so this 4B embedder co-resides with chat-4b on the 16G card.
# expandable_segments lets the CUDA caching allocator GIVE BACK reserved segments after a spike
# (so a long-input forward's high-water doesn't permanently pin VRAM) and cuts the fragmentation
# that was turning the spike into a hard 15.5G reservation. MAX_TOKENS hard-caps each input's
# token length (the truncation target); BATCH bounds docs-per-forward.
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
export PPLX_EMBED_MAX_TOKENS="${PPLX_EMBED_MAX_TOKENS:-8192}"
export PPLX_EMBED_BATCH="${PPLX_EMBED_BATCH:-8}"

echo "[serve_pplx_embed] PID=$$ model=$PPLX_EMBED_MODEL port=$PPLX_EMBED_PORT dtype=$PPLX_EMBED_DTYPE 8bit=$PPLX_EMBED_8BIT alloc=$PYTORCH_CUDA_ALLOC_CONF max_tok=$PPLX_EMBED_MAX_TOKENS batch=$PPLX_EMBED_BATCH"
exec python "$OPS/serve_pplx_embed.py"

# PPLX_REMOTE_PATCH (2026-06-12, lead): the model's remote modeling.py targets an OLDER transformers —
# it calls create_causal_mask(input_embeds=…, cache_position=…) but transformers 5.9.0 renamed
# input_embeds→inputs_embeds and removed cache_position. Re-apply the fix on every start (idempotent),
# covering both the snapshot source and any already-extracted modules copy, so a re-download can't re-break it.
for mp in $(find "$HOME/.cache/huggingface/hub/models--perplexity-ai--pplx-embed-context-v1-4b/snapshots" -name modeling.py 2>/dev/null) \
          $(find "$HOME/.cache/huggingface/modules/transformers_modules" -path "*pplx*" -name modeling.py 2>/dev/null); do
  sed -i 's/input_embeds=inputs_embeds,/inputs_embeds=inputs_embeds,/' "$mp" 2>/dev/null
  sed -i '/cache_position=dummy_cache_position,/d' "$mp" 2>/dev/null
done
