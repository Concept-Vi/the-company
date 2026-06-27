---
type: terrain-entry
name: jina-v4-env
register: descriptive
aliases: ["jina-v4-env"]
path: /home/tim/jina-v4-env
relation: external
kind: engine
status: unconfirmed
created: 2026-05-26
last_active: 2026-05-26
size: 5.0G
coverage: { files_read: 2, files_total: 2, last_read: 2026-06-26 }
git_remote: none
ports: [8002]
models: [jina-embeddings-v4]
service_units: [vllm-jina-v4]
launched_by: serve_jina_v4.sh (which `source`s this venv) ← vllm-jina-v4.service
launched-by: ["[[company-systemd]]"]
part-of: ["[[company]]"]
depends-on: ["[[vllm-env]]"]
relates-to: ["[[vllm-tests]]"]
secrets: false
move_intent: none
tags: [embedding, model]
---

# jina-v4-env

## What it is
A 5.0G dedicated venv for the jina-embeddings-v4 multimodal embedding server. It is held separate from the main `vllm-env` because it pins an older transformers (`transformers<5.0`) for jina-v4 compatibility (per the launcher comment).

## How it works — TWO-HOP wire, launcher lives in vllm-tests
1. `vllm-jina-v4.service` → `ExecStart=/home/tim/vllm-tests/serve_jina_v4.sh` (note: launcher is in `~/vllm-tests`, NOT `~/company/ops`).
2. **`serve_jina_v4.sh` activates this venv** (the proof): `source "$HOME/jina-v4-env/bin/activate"`, then `exec python "$HOME/vllm-tests/serve_jina_v4.py"`. It borrows `CUDA_HOME` from the main vllm-env's cu13 toolchain (`export CUDA_HOME="$HOME/vllm-env/lib/python3.12/site-packages/nvidia/cu13"`).

Serves on port 8002.

## What it connects to
- `[[vllm-tests]]` — both the shell launcher and the `serve_jina_v4.py` server live there.
- `[[vllm-env]]` — borrows its bundled cu13 CUDA toolchain.
- `[[company]]` / `[[company-systemd]]` — wired in by the `vllm-jina-v4` unit on the Company target.

## When / where
`/home/tim/jina-v4-env`, 5.0G; unit `vllm-jina-v4.service` mtime 2026-05-26. Venv files not enumerated.

## Notes / evidence
- Read: `vllm-jina-v4.service`, `serve_jina_v4.sh` (verbatim activate + exec lines).
- **Correction to the starting fact:** the launcher is `/home/tim/vllm-tests/serve_jina_v4.sh` (in vllm-tests), not in `company/ops` like the other vLLM models — a two-hop wire through vllm-tests.
