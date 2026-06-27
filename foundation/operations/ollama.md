---
type: operations
title: Ollama — registration, Modelfile, cloud routes
date_started: 2026-05-27
tags: [foundation, operations, ollama]
---

# Ollama

> [[_operations-index|← Operations hub]] · runtime overview in [[runtimes#Ollama]]

## State

- Binary: `/usr/local/bin/ollama` v0.17.4
- Service: system systemd unit `ollama.service` (not user-level — runs as the `ollama` user system-wide)
- Endpoint: `http://localhost:11434` — both `/api/*` (Ollama native) and `/v1/*` (OpenAI-compat) are live
- Storage: `~/.ollama/models/` (local model registry, separate from the HF cache)

## Currently registered models

Local GGUF (visible in `ollama list` with non-zero size):

| Ollama tag | Source | File | Size |
|---|---|---|---|
| `qwen3.6-35b-a3b-q3km:latest` | [[../models/qwen3_6-35b-a3b-gguf-q3-k-m]] | `Qwen3.6-35B-A3B-UD-Q3_K_M.gguf` | ~16 GB |
| `qwen3.6-27b-q3km:latest` | [[../models/qwen3_6-27b-gguf-q3-k-m]] | `Qwen3.6-27B-Q3_K_M.gguf` | ~13 GB |
| `nomic-embed-text:latest` | upstream Nomic | (Ollama-managed) | 262 MB |

Cloud routes (zero local size; route to Ollama Cloud, incur per-token cost):

`gemma4:31b-cloud`, `nemotron-3-super:cloud`, `deepseek-v4-flash:cloud`, `deepseek-v4-pro:cloud`, `kimi-k2.5:cloud`, `kimi-k2.6:cloud`, `glm-5:cloud`, `glm-5.1:cloud`, `gemini-3-flash-preview:cloud`, `qwen3.5:397b-cloud`.

## Registering a GGUF file with Ollama

The HF-cache GGUF files are not in Ollama's registry until registered. Pattern:

1. Find the GGUF file in the HF cache. Files live at:
   `~/.cache/huggingface/hub/models--<org>--<repo>/snapshots/<sha>/<file>.gguf`
2. Write a Modelfile (minimal form):
   ```
   FROM /home/tim/.cache/huggingface/hub/.../Qwen3.6-35B-A3B-UD-Q3_K_M.gguf
   ```
3. Register:
   ```
   ollama create <tag> -f /tmp/Modelfile
   ```
   where `<tag>` is the name that will appear in `ollama list` (e.g. `qwen3.6-35b-a3b-q3km`).
4. Verify: `ollama list` shows the new tag with the correct size; `curl http://localhost:11434/v1/models | jq` shows it via OpenAI-compat.

Ollama re-copies the file into its own registry by default, doubling disk use. To avoid this, the Modelfile can point at the HF-cache path and Ollama will reference it without copying — but symlinks in the HF cache mean Ollama may follow the link to the blob anyway. **Disk-usage check** after registration: `du -sh ~/.ollama/models/` — confirm no significant size increase if relying on the no-copy path.

## Modelfile directives

For richer registrations:

```
FROM /path/to/file.gguf
TEMPLATE """..."""            # override the chat template
SYSTEM """..."""              # default system prompt
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 32768       # context length
PARAMETER num_gpu 99          # GPU layer count (99 = all)
```

For Qwen3.5/3.6 GGUF served via Ollama: the model's chat template is bundled inside the GGUF metadata; Ollama uses it by default. To override (e.g. to apply the no-think pattern as a TEMPLATE directive), Ollama-side templating uses a different syntax than vLLM's jinja — not yet implemented on this substrate.

## Endpoints

| Path | Use |
|---|---|
| `GET /api/tags` | List registered models (Ollama format) |
| `POST /api/chat` | Chat (Ollama format) |
| `POST /api/generate` | Completion (Ollama format) |
| `POST /api/embeddings` | Embedding (Ollama format) |
| `GET /v1/models` | List models (OpenAI-compat) |
| `POST /v1/chat/completions` | Chat (OpenAI-compat) |
| `POST /v1/embeddings` | Embedding (OpenAI-compat) |

For tools that expect OpenAI APIs (Open WebUI, LangChain `ChatOpenAI`, openai Python SDK), use `/v1/*`. For Ollama-specific tools, `/api/*`.

## Cloud routes

Cloud-routed models look like local models from the API surface but actually call out to Ollama Cloud. The substrate has not characterised them for cost / latency / rate-limit behaviour. They expand the available capability ceiling significantly (e.g. `qwen3.5:397b-cloud` is far beyond anything that could run locally) but each call costs.

To disable a cloud route: `ollama rm <tag>`. To list only local: `ollama list | awk '$3 != ""'`.

## Operational lifecycle

- `ollama.service` is system-managed, not under user systemd. Restart: `sudo systemctl restart ollama` (not `systemctl --user`).
- The service survives WSL reboots because it's a system service. No `enable-linger` needed for Ollama (unlike the user-level vLLM services).
- `~/.ollama/` holds model registry and runtime state. Persisted across reboots.
- Concurrent requests are queued. For high-throughput batched serving, use [[runtimes#vLLM]] instead.

## Open at this topic

- A documented Modelfile pattern for applying chat-template overrides (the equivalent of [[chat-template-patch]] for Ollama-served Qwen variants)
- Tool calling reliability through Ollama for the registered Qwen3.6 variants — untested
- Cloud-route cost / latency / rate-limit characterisation
- Disk-usage growth pattern as more GGUF models register (does Ollama copy or symlink?)
- Whether to register [[../models/qwen3_6-35b-a3b-gguf-iq3-s]] and [[../models/gemma-4-26b-a4b-gguf-q3-k-m]] — currently downloaded but not registered
- Integration with Open WebUI — adding Ollama as a third connection to surface its models in the chat dropdown

## Connects to

- [[_operations-index]] — hub
- [[runtimes]] — Ollama runtime overview
- [[../models/qwen3_6-35b-a3b-gguf-q3-k-m]], [[../models/qwen3_6-27b-gguf-q3-k-m]], [[../models/ollama-nomic-embed-text]] — registered models
- [[../models/qwen3_6-35b-a3b-gguf-iq3-s]], [[../models/gemma-4-26b-a4b-gguf-q3-k-m]] — pending registration
