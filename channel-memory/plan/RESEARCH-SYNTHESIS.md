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

## Round 4 — cognition / models for the synthesis panel [VERIFIED by-read; one caveat]
- **VERIFIED (read runtime/cognition.py, 172KB):** `run_role(role, ctx)` (L203) + `ThreadPoolExecutor` concurrency (`_role_worker` L573, `concurrency_probe` L633) + structured output (`json=True` → `response_format`, L217/327/340 passing `schema=role.output_schema`). The lead's "build the panel ON cognition.py roles, not parallel" is CONFIRMED — the panel = NEW facet-extract roles + a judge-role chain, reusing run_role/run_swarm. Models (lead): chat-4b(:8000) · chat-2b(:8003) · chat-08b(:8006) extract; chat-nemotron-30B(:8005) judges.
- **★ CAVEAT RESOLVED (re-verified the engine):** the enforced-schema path EXISTS — my earlier "json_object only" flag was incomplete. Three layers found:
  1. `runtime/generation_policies.py` L35/L97 — a **`json_schema` generation-policy flag**: "structured-outputs (json_schema, NOT json_object) for this [role]". A role/generation can REQUEST enforced json_schema decoding. (suite.py L2313: the declared option set is `none|json|json_schema`.)
  2. `client.complete(schema=…)` (suite.py L102/6910) — **retries + RAISES on schema mismatch** regardless of response_format. So even the json=True (json_object) path is schema-VALIDATED with retry, not blind.
  3. `json=True` default = `json_object` (the hint). For the safety-substrate preference-extract, set the role's `json_schema` generation-policy → enforced decode + the validate-retry net.
  ⇒ the panel is NOT blocked on a missing capability; it uses the existing json_schema policy. (Tell the lead: no engine fix needed — request the policy per-role.)
- **Roles ARE file-discovered, additive:** `roles/*.py`, each a `Role{id, prompt_template, output_schema}` (canonical defs: focus/recall/ground/ground_criterion/develop_option/reduce_synth/voice_lens/register_element/confirm_registration). `runtime/roles.py` = Role/RoleRegistry; `role_registry().discover([roles/])`. Concurrency: `run_items`/`run_swarm`/ThreadPoolExecutor. ⇒ a preference-extract or facet-extract role = a NEW additive `roles/*.py` file (file-disjoint; no shared-engine edit) declaring the welded PreferenceSignal `output_schema` + the extraction `prompt_template`, run with the `json_schema` policy + the schema-retry net.
- **Build path (Group 4 + preferences feeder, engine-unblocked):** new `roles/preference_extract.py` (+ facet-extract roles for decisions) with json_schema policy → `run_items` concurrent → a judge-role chain. The SAFETY-SUBSTRATE quality bar means the extraction prompt_template needs cross-review (recall-fork owns the Pillar-1 ratification gate it feeds) + real verification (does it faithfully recover Tim's broad→specific hierarchy?) — a focused build, not a rushed one.

## Round 5 — channels / registry / rule-load [PENDING — lead-lane]
- **runtime/cc_channels.py** [read earlier] — channel router/registry/threads/mail.
- **The source registry** — where the CLI + (proposed) session-store register as sources; the projection feeds off it ([[project-claude-code-atlas]], The Heart).
- **~/.vi/CLAUDE.md + rules/*.md** — the auto-load-to-every-session mechanism = the load-on-join precedent for channel-context (Group 5.2).
- **Explore:** how a channel could carry a manifest + how members "load" it (does it ride ~/.vi/rules, the registry, or cc_channels membership?).

## Round 7 — memory-system convergence [confirmed in-channel 2026-06-14]
- **ONE layered memory system** (recollection-fork's framing, lead-confirmed): **session-recall = the INNER layer** (one session); **recollection = the OUTER layer** (all sessions + sidechains + cross-project links + distill + the two pillars). My session-recall nests INSIDE recollection — the served :8007 embed / :8008 rerank stack is the concrete working instance of recollection's abstract slots. **NO parallel memory system** (principle 2, across forks).
- **Preference/identity layer = recollection's Pillar-1** (cross-session by nature — the feedback-* corpus spans sessions). The fork's get-a-feel lens (Group 3.7) FEEDS the session-scoped signal INTO Pillar-1; it is not a second layer. Ownership = recollection (Tim's call).
- **Address grammar (the GATE, Tim's direct call):** lattice (coordinate-space) vs hierarchy (project·session·segment). Fork's position: the embedding index IS already a 2560-d coordinate lattice → recall is lattice-based today; structural keys are DISCRETE AXES within it (hierarchy = a slice of the lattice, not an alternative). Proposed: lattice-with-hierarchy-as-axes. Surfaced to the lead's one-decision-surface.
- **Reranker license:** jina-v3 = CC-BY-NC → commercial path needs a permissive swap (ms-marco CPU, lead-served). session_recall is env-configurable (EMBED_URL/RERANK_URL) → swap is config, not rebuild.

## Round 6 — the get-a-feel source [V this session]
- **The preference-memory corpus** `~/.claude/projects/-home-tim/memory/feedback-*.md` (50+ entries) — Tim's distilled preferences across sessions = the anti-recency get-a-feel substrate (Group 3.7, INFERRED-PREFERENCES Q3). Plus `~/.claude/CLAUDE.md`.

## Implications for the plan
- Group 4 (synthesis panel): **build on runtime/cognition.py + the role/cascade engine** (Round 4) — don't create a parallel extractor framework. *Pending that exploration.*
- Group 5/6 (channel-context, multi-project): **joint with the lead**; ride the registry + ~/.vi/rules (Round 5), don't parallel.
- Group 3.7 (preferences): **read the feedback-* memory first** (Round 6), session-recall second.
- session_search.py is dead weight — deprecate, don't extend (Round 1).
