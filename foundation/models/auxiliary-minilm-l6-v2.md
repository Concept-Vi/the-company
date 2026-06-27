---
type: model
id: sentence-transformers/all-MiniLM-L6-v2
filename: auxiliary-minilm-l6-v2
status: auxiliary
runtime: not-yet-served
date_added: present-before-substrate-setup
tags: [foundation, models, embedding, auxiliary, small]
---

# all-MiniLM-L6-v2 (auxiliary)

> [[_models-index|← Models hub]] · auxiliary; not a primary endpoint

## At a glance

| Field | Value |
|---|---|
| HF id | `sentence-transformers/all-MiniLM-L6-v2` |
| Disk | 888 MB |
| Architecture | 6-layer MiniLM, sentence-transformer trained |
| Embedding dim | 384 |
| Status | present on disk; used by tooling (sentence-transformers default) rather than as a primary endpoint |

## Source

Present in the HF cache prior to the deliberate model-pulls of 2026-05-26. Likely downloaded by `sentence-transformers` library auto-load when other tooling used the default embedder.

## Fits these needs

- **Tooling default**, not a Tim-need. Lives here so its presence is documented; not part of the deliberate embedding slate.

## Open at this entry

- Whether to keep on disk (it's 888 MB — non-trivial but small)
- Which tools auto-load it; pinning explicit embedder choices on those tools would let this be cleaned up

## Connects to

- [[_models-index]] — hub
