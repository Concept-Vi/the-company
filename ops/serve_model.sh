#!/usr/bin/env bash
# serve_model.sh — the ONE registry-driven vLLM launcher.
#
#   serve_model.sh <service-key>
#
# Reads the service's `config` block from ops/services.json (via cli/serveconfig.py)
# and execs vLLM with those flags. So a model's settings (model id, port, gpu-util,
# context, …) are CONFIG in the registry — edit them with `company config` or by hand —
# never hardcoded here. One launcher for every config-driven model; add a model = add a
# registry entry, no new script.
#
# cu13/Ada gotcha (voice-stack session, 2026-06-06): FlashInfer can crash on this stack. If a
# config model hits it, set in its config.env: VLLM_USE_FLASHINFER_SAMPLER=0 (and for the
# attention path VLLM_ATTENTION_BACKEND=TRITON_ATTN, with `ninja` on PATH). See memory
# project-vllm-gpu-gotchas. nemotron + jina embedders already carry the sampler-off env.
set -euo pipefail
KEY="${1:?usage: serve_model.sh <service-key>}"
OPS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Universal infra env (all config-driven vLLM models share the vllm-env + cu13 toolchain).
export CUDA_HOME="$HOME/vllm-env/lib/python3.12/site-packages/nvidia/cu13"
export PATH="$CUDA_HOME/bin:$PATH"

# Per-service env from the registry's config.env (faithful to each model's old serve script).
while IFS= read -r line; do
  [ -n "$line" ] && export "$line"
done < <(python3 "$OPS/cli/serveconfig.py" "$KEY" --env)

source "$HOME/vllm-env/bin/activate"

mapfile -t ARGS < <(python3 "$OPS/cli/serveconfig.py" "$KEY")
echo "[serve_model] $KEY → vllm serve ${ARGS[*]}"
exec vllm serve "${ARGS[@]}"
