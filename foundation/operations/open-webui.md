---
type: operations
title: Open WebUI — interactive chat surface
date_started: 2026-05-27
tags: [foundation, operations, webui]
---

# Open WebUI

> [[_operations-index|← Operations hub]] · runtime overview in [[runtimes#Open WebUI]]

## State

- Container: `openwebui/open-webui:latest` (Docker)
- Container name: `open-webui`
- Network mode: host
- Auth: disabled (`WEBUI_AUTH=false`) — appropriate for localhost-only use
- Persistence: Docker volume `open-webui-data` — chat history survives restarts
- Endpoint: `http://localhost:8080`
- Connected backends: vLLM chat (port 8000), vLLM embed (port 8001)
- HF_TOKEN: injected via env vars so the container can pull its own auxiliary models without rate-limit issues

## What it can and cannot configure

Open WebUI is a **client** — a chat interface that talks to OpenAI-compatible APIs. Settings split into three categories:

**Per-request (set by Open WebUI on every call to the model):**

- Model selection (dropdown)
- System prompt (per chat or per preset)
- Temperature, top_p, max_tokens, repetition_penalty
- Tool definitions (Workspace → Tools)
- Document context (Workspace → Knowledge; routes through the RAG layer)
- Vision input (drag-drop images into chat — works on VL models)
- Conversation history (multi-turn)

**Server-level (set on the vLLM server's launch flags, NOT in Open WebUI):**

- Which models are loaded (decided at `vllm serve` time)
- Max context length (`--max-model-len`)
- Concurrency budget (`--max-num-seqs`)
- Prefix caching on/off
- Tool parser
- Chat template

**UI-level (Open WebUI-specific, no model effect):**

- Theme, layout, citation display
- Saved prompt templates (Workspace → Prompts)
- Model presets (Workspace → Models — create variant "Qwen-Creative" with high temp + custom system prompt as a separate dropdown entry)
- Document RAG settings (chunk size, retrieval mode)

## Why Open WebUI shows only some models

Open WebUI auto-discovers models from each `/v1/models` endpoint it's connected to. Current configuration:

- Connection 1: `http://localhost:8000/v1` → exposes [[../models/qwen3_5-4b-awq]]
- Connection 2: `http://localhost:8001/v1` → exposes [[../models/bge-m3]] (visible but not useful in a chat UI)

The Ollama endpoint at `http://localhost:11434/v1` is **not currently connected**. Adding it would surface [[../models/qwen3_6-35b-a3b-gguf-q3-k-m]] and other Ollama-registered models in the chat dropdown.

To add a connection:

1. Admin Settings → Connections → "+" next to OpenAI API
2. URL: `http://localhost:11434/v1` (or any other endpoint; from inside the container the host is reachable as `host.docker.internal` or the host's WSL IP — host networking simplifies this to `localhost`)
3. Key: `dummy` (no auth)
4. Save → new models appear in the dropdown

## Why some Tim-relevant settings aren't UI-controllable

Things like Qwen's `enable_thinking` flag are not standard OpenAI parameters. Open WebUI doesn't expose them in the per-conversation settings panel. Two resolutions (using the no-think example):

- **Server-side (current solution):** apply [[chat-template-patch]] so the default is no-think; Open WebUI doesn't need to know about it
- **Client-side workaround:** Open WebUI's Workspace → Models supports custom "Model Parameters" in JSON form; could add `chat_template_kwargs` there per model preset. Less clean than server-side.

The server-side approach generalises: anything non-standard about a model's request shape is best handled on the server (chat template patches, parser flags, defaults baked into the launcher).

## Container management

- Start: `docker start open-webui`
- Stop: `docker stop open-webui`
- Logs: `docker logs open-webui -f`
- Restart with new env: `docker stop open-webui && docker rm open-webui && docker run -d --name open-webui ...` (volume persists, env vars get replaced)

The full launch command (used by the substrate setup):

```bash
docker run -d \
  --name open-webui \
  --restart unless-stopped \
  --network host \
  -e "OPENAI_API_BASE_URLS=http://localhost:8000/v1;http://localhost:8001/v1" \
  -e "OPENAI_API_KEYS=dummy;dummy" \
  -e WEBUI_AUTH=false \
  -e ENABLE_OLLAMA_API=false \
  -e RAG_EMBEDDING_ENGINE=openai \
  -e RAG_OPENAI_API_BASE_URL=http://localhost:8001/v1 \
  -e RAG_OPENAI_API_KEY=dummy \
  -e RAG_EMBEDDING_MODEL=BAAI/bge-m3 \
  -e HF_TOKEN="$(cat ~/.cache/huggingface/token)" \
  -e HUGGINGFACE_HUB_TOKEN="$(cat ~/.cache/huggingface/token)" \
  -v open-webui-data:/app/backend/data \
  openwebui/open-webui:latest
```

Notes on env vars:
- `OPENAI_API_BASE_URLS` is semicolon-separated; `OPENAI_API_KEYS` matches one-to-one in the same order
- `ENABLE_OLLAMA_API=false` disables Open WebUI's own Ollama integration (cleaner — Ollama would be added as another OPENAI_API_BASE_URL if wanted, for consistency)
- `RAG_EMBEDDING_*` route the built-in document-RAG embedding through BGE-M3 rather than having Open WebUI download its own embedder

## Open at this topic

- Adding Ollama as a third connection (would surface the GGUF MoE models)
- The "Workspace → Models" preset pattern — has Tim used it; could it be a substitute for the chat-template patch in places
- The built-in RAG (Workspace → Knowledge) — currently routes through BGE-M3 but never characterised end-to-end on Tim's documents
- Authentication for non-localhost use — currently localhost-only; if exposed, `WEBUI_AUTH=true` and a reverse proxy with TLS would be needed
- Whether the chat-history persistence in the Docker volume should be backed up or considered ephemeral

## Connects to

- [[_operations-index]] — hub
- [[runtimes]] — runtime overview
- [[chat-template-patch]] — why default Open WebUI requests work cleanly
- [[../models/_models-index]] — which models are discoverable
- [[ports]] — port assignments
