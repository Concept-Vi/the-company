# Research Synthesis — what EXISTS (the evidence base)

```
trust: fabric-derived
author: ch-8djrpmsl / 11e7d395 (fork)
date: 2026-06-14
verified: rounds 1-3 by-execution/read this session; rounds 4-5 PENDING (lead-lane exploration)
```
> loop-prep Document 3 — what we HAVE, so the Criteria/Guide aren't aspirational. Changes flow: new findings → here → Guide → Criteria. Don't build parallel systems (principle 2): every "build" must first check this for an existing equivalent.

## Round 1 — recall substrate (this repo) [V/read this session]
- **runtime/session_scan.py** [V built] — structural scan → projectable rows (attribution incl. inject/tool/compaction filter, per-turn tokens, boundaries, system-subtypes, dense profile, gaps). Reuses `build_timeline`.
- **runtime/session_recall.py** [V built] — embed (:8007 documents-mode) + cosine + served rerank (:8008) + sub-chunking. Build-once index.
- **runtime/session_lens.py** [V built] — find/decisions/open_loops/catch_up/timeline/directives.
- **runtime/session_search.py** [B broken / deprecated] — existing semantic session search; its semantic mode bridges to the OVERLORD venv (chromadb) via `ops/wire_substrate_claude_sessions.py`, which fails (`substrate_mcp.embeddings` deleted). Tim is DROPPING the overlord bridge → this path is deprecated; the lead re-points it at session_recall. **DO NOT build on it.**
- **runtime/corpus.py, runtime/operator_memory.py** [exists, unread] — existing memory/corpus primitives. *Explore before adding any memory store (principle 2).*

## Round 2 — serving surfaces [V verified live this session]
- **:8007 embed-pplx** — Company service (`ops/serve_pplx_embed.py`, /usr/bin/python3.12). pplx-embed-context-v1-4b, documents-mode → 2560-d int8 cosine. The decision-grounded embedder ([[embedding-model-decision]]).
- **:8008 rerank-jina** — the LEAD's service (services.json / @xsession, commit ba87f61). jina-v3 listwise, CPU-pinned (0 VRAM). Contract: POST /rerank {query, candidates, top_n} → ranking[{item, rerank_score, orig_rank}].
- **ops/rerank.py** [exists] — the jina-v3 reranker library (now served via :8008).
- **substrate index** `~/.cache/company/substrate-claude-sessions/substrate.db` — 1050 files / 35512 chunks / 21626 embedded (60.9%) — built via the now-broken overlord path. Possibly reusable once the lead restores `embeddings.py`, but our path doesn't need it.

## Round 3 — session store [V documented this session]
- The `.jsonl` grammar, boundary detection (structural, `compact_boundary`/`isCompactSummary`), forkedFrom provenance, build_timeline/resolve_cut/materialize_at_point → **channel-memory/schema/session-store-grammar.md**. Lineage/distances → **channel-memory/map/**.

## Round 4 — cognition / models for the synthesis panel [PENDING — explore next; lead-lane for loadout]
- **LEAD signal needed:** what local small models are loadable/appropriate for concurrent structured-output EXTRACTION (their model-loadout lane).
- **Strong hint of an existing engine NOT to parallel:** `runtime/cognition.py` exists (referenced L632/L867 this session — `cognition.py:326`, `response_format json_object`), and [[company-compositional-architecture]] describes the Company AS a typed compositional dataflow of code + AI nodes wired by structured-output contracts, with roles/cascades. **The Group-4 panel (extractors → judge) is almost certainly ROLES in this existing engine — build the panel ON it, not parallel.** MUST explore: runtime/cognition.py, the role/cascade/run_role/run_cascade MCP surface, structured-output contracts. [[reference-vllm-structured-output]]: use response_format json_schema (enforced), not json_object.

## Round 5 — channels / registry / rule-load [PENDING — lead-lane]
- **runtime/cc_channels.py** [read earlier] — channel router/registry/threads/mail.
- **The source registry** — where the CLI + (proposed) session-store register as sources; the projection feeds off it ([[project-claude-code-atlas]], The Heart).
- **~/.vi/CLAUDE.md + rules/*.md** — the auto-load-to-every-session mechanism = the load-on-join precedent for channel-context (Group 5.2).
- **Explore:** how a channel could carry a manifest + how members "load" it (does it ride ~/.vi/rules, the registry, or cc_channels membership?).

## Round 6 — the get-a-feel source [V this session]
- **The preference-memory corpus** `~/.claude/projects/-home-tim/memory/feedback-*.md` (50+ entries) — Tim's distilled preferences across sessions = the anti-recency get-a-feel substrate (Group 3.7, INFERRED-PREFERENCES Q3). Plus `~/.claude/CLAUDE.md`.

## Implications for the plan
- Group 4 (synthesis panel): **build on runtime/cognition.py + the role/cascade engine** (Round 4) — don't create a parallel extractor framework. *Pending that exploration.*
- Group 5/6 (channel-context, multi-project): **joint with the lead**; ride the registry + ~/.vi/rules (Round 5), don't parallel.
- Group 3.7 (preferences): **read the feedback-* memory first** (Round 6), session-recall second.
- session_search.py is dead weight — deprecate, don't extend (Round 1).
