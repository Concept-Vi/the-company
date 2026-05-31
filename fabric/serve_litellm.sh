#!/usr/bin/env bash
# Start the LiteLLM proxy (the company's unified model endpoint) on :4100.
# Runs from the isolated 3.12 venv so it never touches the 3.14 runtime. See fabric/AGENTS.md.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
exec "$HERE/../.litellm-venv/bin/litellm" \
  --config "$HERE/litellm.config.yaml" \
  --host 127.0.0.1 --port 4100
