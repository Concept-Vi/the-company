---
trust: fabric-derived
author: ch-al7jdfdr (lead, session bda8ce28)
date: 2026-06-14
verified: lead's delegated call (Tim D1+D6: "your call on the registry shape") — surfaced to Tim; locks the D-1 keying so indexing proceeds
relates: [UNIFIED-SEAM.md, lead-lane-inputs.md, APPROVAL-STANDARD.md]
---
# Embedding-axis registry (D1+D6) — the multi-space semantic axes, my delegated call

Tim D1+D6 (tim-direct, relayed): "many models on the desk, a bunch have multiple ways to embed — that
could be a registry, all of those as axes, as well as their actual position in the session file." This
fuses [[native-model-layer]] (use ALL models) with D-1 multi-space addressing. He delegated the shape
to the lead ("your call"). Here it is — locking the keying so the recall fork can index NOW.

## The model
A unit's multi-space address = co-equal coordinate spaces:
- **provenance** (`exchange://<sid>/<i>`) — the CANONICAL, re-embed-stable identity (the spine).
- **temporal** (ts) — continuous axis.
- **file-position** (the unit's literal position in the session `.jsonl` — Tim's "actual position in
  the session file") — discrete structural axis.
- **structural/provenance sub-axes** — project · session · segment (compaction generation).
- **semantic** — NOT one axis: **ONE co-equal semantic axis per (embedding-model × embedding-way)**,
  held in an EXTENSIBLE REGISTRY. Each row = one semantic coordinate space.

## The embedding-axis registry (file-discovered, mirrors roles/ · platforms/)
Each axis is a row: `{ id, model, way, endpoint, dim, metric, instruction? , status: served|planned }`.
- `way` = the embedding MODE (e.g. pplx documents-mode vs flat-input; bge dense vs sparse; a steered
  Qwen3-Embedding instruction). One (model × way) = one axis = one space.
- **First populated row:** `{id: pplx-ctx-4b-docs, model: perplexity-ai/pplx-embed-context-v1-4b,
  way: documents-mode, endpoint: http://127.0.0.1:8007/v1/embeddings, dim: 2560, metric: cosine}`.
- Adding a model/way = adding a row + serving its endpoint + (lazily) backfilling its vectors. Extensible
  exactly like the native-model-layer model registry — the axes ARE embedding-registry entries.

## Recall axis-selection
A recall query carries an axis selector: default = the primary served axis (pplx-ctx-4b-docs now);
optional multi-axis → fuse by RRF (agreement across axes = the relevance signal, per the lens-set
design). The GOLDEN RULE is per-axis: index and query within the SAME axis (a vector only matches its
own maker × way). Provenance/temporal/file-position filter ANY axis (they're stable, model-independent).

## Indexing path (D-1 gate RESOLVED — recall fork: proceed)
Index in the `pplx-ctx-4b-docs` axis NOW (it's served + verified). The registry is extensible: add
semantic axes as models are served + backfill lazily — DON'T wait for all. Provenance is the join key
across axes. This locks the addressing+embedding keying; indexing is unblocked.

## Build note
The embedding-axis registry is the lead's channel/serving lane (file-discovered registry under e.g.
`embedding_axes/`, served-endpoint per row). Reversible (re-keyable). Built via the lead's build loop.
