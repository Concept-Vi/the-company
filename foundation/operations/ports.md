---
type: operations
title: Ports — canonical service map
date_started: 2026-05-27
tags: [foundation, operations, ports]
---

# Ports

> [[_operations-index|← Operations hub]]

## Canonical map

| Port | Service | Runtime | What lives here |
|---|---|---|---|
| 8000 | `vllm-chat` | vLLM | [[../models/qwen3_5-4b-awq]] (default chat) |
| 8001 | `vllm-embed` | vLLM | [[../models/bge-m3]] (default embed) |
| 8002 | `vllm-jina-v4` | jina-v4-env | [[../models/jina-embeddings-v4]] (multimodal embed) |
| 8003 | (reserved) | — | future chat / text-only sibling — see [[../models/qwen3_5-2b]] |
| 8004 | (reserved) | — | future swap-only chat — see [[../models/nemotron-3-nano-30b-a3b-awq]] |
| 8005 | (reserved) | — | future swap-only chat |
| 8080 | `open-webui` | Docker | Open WebUI; connects to 8000/8001 |
| 11434 | `ollama` | Ollama (system) | All Ollama-registered models + cloud routes |

## Endpoint patterns

All chat/embed services expose **OpenAI-compatible** APIs at `/v1/*`:

- `GET /v1/models` — list available models on this port
- `POST /v1/chat/completions` — chat (works on 8000, 8002 returns embeddings only)
- `POST /v1/embeddings` — embedding (works on 8001, 8002, 11434)

Ollama also exposes its **native** API at `/api/*` on 11434 alongside `/v1/*`.

Open WebUI on 8080 is a web UI, not an API.

## Cross-host reachability

All services bind to `0.0.0.0` (not `127.0.0.1`), making them reachable from:
- WSL-side `localhost`
- Windows-side `localhost` (via WSL2's port forwarding)
- Docker containers via host networking

This is the right default for substrate use from inside Open WebUI containers and from Windows-side tools. **Not** the right configuration if the host is ever exposed to the network beyond this machine — no auth is configured anywhere.

## Why these specific ports

- 8000-series for OpenAI-compat services (industry convention)
- 8080 for web UI (industry convention)
- 11434 is Ollama's default (not chosen by us)

## Open at this topic

- Reverse proxy / unified port — currently each service has its own port; a future router (LiteLLM, custom proxy) would consolidate to one
- HTTPS — currently HTTP only; if substrate is exposed beyond localhost, TLS + auth become required
- IPv6 binding — currently IPv4 only

## Connects to

- [[_operations-index]] — hub
- [[runtimes]] — what binds these ports
- [[systemd-services]] — what manages the listeners
