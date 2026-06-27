---
type: model
id: nomic-embed-text:latest (Ollama)
filename: ollama-nomic-embed-text
status: available
runtime: ollama
port: 11434
date_added: present-before-substrate-setup
tags: [foundation, models, embedding, ollama]
---

# nomic-embed-text (Ollama)

> [[_models-index|← Models hub]] · the Ollama-side default embedder

## At a glance

| Field | Value |
|---|---|
| Ollama tag | `nomic-embed-text:latest` |
| Disk | 262 MB (quantised) |
| Architecture | nomic-embed-text — Nomic's general-purpose dense embedder |
| Embedding dim | 768 |
| Endpoint | `http://localhost:11434/api/embeddings` (Ollama native) and `http://localhost:11434/v1/embeddings` (OpenAI-compat) |
| Status | registered with Ollama (system-wide); available |

## Source

Registered with Ollama prior to the substrate setup of 2026-05-26. Likely pulled at some point when Ollama-based tooling needed a default embedder.

## Fits these needs

- [[_models-index#General dense text embedding for semantic search|General dense text embedding]] — accessible via the Ollama API path. Smaller / lower quality than [[bge-m3]]; useful when the Ollama API is the integration path.

## Quirks

- Different format (Ollama registry) and runtime (Ollama) than the other embedders here. Lives on the Ollama port (11434), not the vLLM embed port (8001).
- Quantised — much smaller than `nomic-embed-text` at full precision. Quality vs the unquantised full-precision Nomic embedder unverified.

## Open at this entry

- Whether to keep registered or remove (262 MB; small cost)
- Quality vs [[bge-m3]] on representative tasks (BGE-M3 should win on quality; nomic-embed-text wins on ubiquity through the Ollama ecosystem)
- The Nomic v1.5 / v2 family relationship (which version is `nomic-embed-text:latest` pointing at)

## Connects to

- [[_models-index]] — hub
- [[bge-m3]] — primary embedder on the substrate
- [[nomic-embed-code]] — code-specialised sibling (different distribution path)
- [[../operations/ollama]] — Ollama runtime
