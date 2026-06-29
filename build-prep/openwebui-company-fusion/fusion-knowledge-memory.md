---
type: proposal
title: KNOWLEDGE + MEMORY Fusion — One Substrate, Best Parts Built INTO the Company
area: openwebui-company-fusion
register: prescriptive
status: unconfirmed
posture: both sides incomplete + unreviewed; no source of truth; no horizon; best parts fused INTO the company centre; no duplicates
verified_live: 2026-06-28
aliases: ["fusion-knowledge-memory", "knowledge-memory-fusion"]
tags: [fusion, rag, corpus, recollection, dragnet, embeddings]
sources:
  - "[[area-B-runtime-fabric]]"
  - "[[area-F-nodes-projections-contracts]]"
  - "[[area-I-memory-tests]]"
  - "[[owui-side-map]]"
---

# KNOWLEDGE + MEMORY Fusion

> The question is not "company corpus OR OpenWebUI RAG." Tim's standing laws already
> decide it: **Unions, not bridges** (the patchwork IS the problem, 2026-06-17);
> **Islands join the mainland** (good parts built INTO the centre; the island drops its
> parallel scaffolding); **Resolution-first / compositional**; **Both-plus-others** (the
> binary is usually false framing). So this is a UNION onto ONE substrate, not two piles
> wired together. Everything below is grounded in that, with live verification noted.

---

## 1. BEST PARTS (what each side UNIQUELY brings)

The honest delta — not "they overlap," but what each has that the other does **not**.
The company already has embedding **and** rerank **and** a persisted space-keyed vector
index. So OWUI's contribution is narrower than "its whole RAG factory."

### Company — the durable substrate (verified live 2026-06-28)
- **Projection lenses / embeddable spaces.** 9 live spaces (`cognition_info().spaces`
  verified: `code_archaeology · common_knowledge · extractions · history · operators ·
  principles · repo · topics · worldview`). These are MEANING-TYPED views — the same
  content embedded through different lenses (what / topics / principles / worldview /
  history). OWUI's "collections" are flat folders by comparison
  ([[area-F-nodes-projections-contracts]] §II; `projections/`).
- **Corpus with lineage + digests.** Every record carries required session/round/project
  lineage (fail-loud at write), is an OPEN schema-additive dict, and stores a DIGEST not
  raw text (corpus.py:72; `_validate_lineage`). The source is addressed, not duplicated.
- **Recollection** — episodic memory: sqlite + sqlite-vec index over Claude/Codex
  exchanges, embedding-versioned, reentrancy-guarded ([[area-I-memory-tests]] §1;
  `recollection/src/db.ts`, `embedding-migration.ts`).
- **The inversion-finder (`find_relations`)** — the cross-space query OWUI has NO analogue
  for: "same principle, different subject" = near in `principles`, far in `topics`
  (near∩¬far over the space-keyed index). This is a RELATIONAL primitive, not retrieval
  (verified: tool live; `runtime/corpus_neighbours.py`, Suite.find_relations).
- **Rerank already in hand** — jina-v3 cross-encoder @ :8008 (`corpus rerank=True`,
  `ops/rerank.py`), calibrated floor `_CTX_FLOOR=-0.13` (decision_memory.py:55).
- **Forms → effort-band routing** — shape-recognised capture depth (log/registry/decision/
  prose → legibility/deep), so the corpus does NOT burn full describe-depth on bookkeeping
  ([[area-F-nodes-projections-contracts]] §V).

### OpenWebUI — the genuine net-new (the narrow delta worth absorbing)
Verified against [[owui-side-map]] §5 against what the company already runs:
- **Hybrid BM25 + vector FUSION (the merge, not the lexical leg).** `query_*_with_hybrid_search`
  + `HYBRID_BM25_WEIGHT` + `merge_and_sort_query_results` (owui §5; `retrieval/utils.py:341,613,475`).
  CORRECTION (verified live): the company is NOT cosine-only — `session_search.py` already has a
  declared **`lexical` mode** ("term search over the SAME index's chunk text... zero models, zero
  GPU, always available") alongside `semantic`. What the company lacks is the **fusion stage** that
  COMBINES cosine + lexical scores into one ranking (BM25 weighting + merge). So the gap is narrower:
  fuse two retrieval legs the company largely already has, not build keyword search from scratch.
- **The document loader matrix.** docling / tika / datalab-marker / Azure-DI / mineru /
  paddleocr_vl + per-extension LangChain + youtube/web/tavily loaders
  (`retrieval/loaders/main.py:228`). The company's dragnet ingests repo files + images;
  it has no PDF/docx/OCR ingestion path. **Real gap.**
- **Agentic retrieval via native function-calling.** `query_knowledge_files` /
  `view_knowledge_file` built-in tools let the model ITERATIVELY retrieve mid-turn
  (owui §5; `middleware.py:220,308`), vs the company's single-shot retrieve node.
- **Documents/Knowledge/Collections UI + the `#`-invocation** — a real management surface
  (create/reindex/sync/folders) that the company's corpus has no front-end for.

(NOT worth harvesting: OWUI's 14 vector-DB backends — the company already has one working
persisted index; inheriting a backend-zoo violates "no duplicates." Its embedding services
are weaker than the company's pplx/bge/jina stack. Skip both.)

---

## 2. THE FUSED MODEL — one knowledge substrate

**Decided by standing rules, not a live menu.** The "should OWUI point at the corpus, OR
build OWUI's plumbing into the company, OR expose the corpus to OWUI?" is a false trilemma
("Both-plus-others"). The answer is **all three legs of ONE union**, with the company
corpus as the single substrate:

### Leg A — the company corpus is THE knowledge store (no second pile)
There is ONE knowledge substrate: the company corpus + its 9 spaces + the space-keyed
vector index. OWUI's `Knowledge`/`Collection`/`KnowledgeDirectory` tables are NOT adopted as
a parallel store — that would be the bridge anti-pattern (two stores kept in sync). A
"collection" in the fused model is a PROJECTION/space filter (or a `project` facet) over the
one corpus, not a new table. **Islands-join-mainland: OWUI drops its store, rides the spine.**

### Leg B — OWUI's strong plumbing is built INTO the company (absorbed, not bridged)
The narrow delta from §1 is built as company-native capability on the durable substrate:
- **Hybrid FUSION stage** → the company already has both legs (cosine over the space-index;
  lexical term-search in `session_search.py`). Build the FUSION: a BM25-weighted
  `merge_and_sort` over cosine + lexical candidates, exposed as `corpus(op='query', mode='hybrid')`.
  Reuse the existing rerank stage (jina-v3 @ :8008) as the precision pass over the fused
  candidates — the company already has the reranker OWUI bolts on. Net-new is the merge math +
  lifting lexical from the session index onto the corpus spaces, NOT keyword search itself.
- **Loader matrix** → the dragnet (`cc_dragnet.py`) gains kind-pluggable loaders (it is
  already "kind-pluggable" per its design) for PDF/docx/OCR, lifting OWUI's loader choices
  as a new `source_type` per format. The output still flows through capture → digest →
  embed-to-spaces. One ingestion path, more formats.
- **Agentic retrieval** → expose the corpus query as a model-callable tool (Leg C) and let
  the RHM/role iterate, replacing OWUI's single built-in with the company's `find_relations`
  + spaced query as the agentic toolset.

### Leg C — the corpus is a TOOL the RHM / OWUI front-end calls (the union seam)
The company ALREADY exposes the corpus over MCP (`mcp__company__corpus`,
`mcp__company__find_relations`) — verified live this session. OWUI's Tools subsystem can
call MCP servers in-interface (owui §1.5; `utils/tools.py:321-427`, MCP resolved into
`tools_dict`). So the union seam is: **register the company corpus MCP tools as OWUI Tools**
→ OWUI's chat/channels/agentic-retrieval all retrieve from the ONE corpus through the
company's own verbs (spaced query, rerank, inversion-finder). No data copied into OWUI; OWUI
becomes a FACE on the corpus, the corpus stays the substrate. This is the union, not a bridge:
OWUI does not hold a mirror — it dereferences live (the same discipline as the `portal` node,
[[area-F-nodes-projections-contracts]] §I, RESOLVE='reference').

**Net shape:** ONE corpus (durable, lineage-gated, 9 spaces) · the fusion + loaders absorbed
INTO it as company-native legs · reachable as MCP tools that OWUI (and any face) calls live.

**CORRECTION — recollection is a THIRD pile to ABSORB, not already-merged.** Verified live:
`projections/history.py` states the `history` space is "durable cross-session memory **on the
corpus, NOT episodic-memory**." Recollection (`~/.recollection` sqlite + sqlite-vec, Transformers.js
embeddings, [[area-I-memory-tests]] §1) is a SEPARATE episodic index from the corpus `history`
space. So the union has THREE indices to collapse, not two: (a) the durable corpus + 9 spaces,
(b) recollection's sqlite-vec, (c) the interim claude-sessions Chroma. "One substrate" is the
TARGET, not today's reality. The fold: recollection's mined exchange-extracts feed the corpus
`history` space (same shape — "one mined exchange-extract per unit: decisions/corrections/
failures/patterns") through capture→embed-to-spaces, then recollection's parallel sqlite-vec is
retired. This is the islands-join-mainland act applied to memory; until it is wired, recollection
remains a genuine second episodic pile (named honestly here, per "no duplicates").

---

## 3. COMPANY-INTERNAL ISSUES (verified live — most memory-flagged bugs are STALE)

The four dragnet bugs come from MEMORY dated 2026-06-22; it is now 2026-06-28 with active
building. Live check resolves most of them:

| Issue (from memory) | Live status 2026-06-28 | Resolution |
|---|---|---|
| **Floor 0.5 miscalibrated-high** | **STALE / already fixed.** `_CTX_FLOOR=-0.13` live at `decision_memory.py:55`; recalibrated by-use against the live jina-v3 reranker (the -0.5 was a guess on the pre-reboot reranker; area-B:283 documents the fix). | None needed. Keep the by-use calibration discipline; re-verify the floor whenever the reranker model changes (it is reranker-scale-specific). |
| **Freshness: no auto-reindex** | **STALE / fixed + WIRED.** `freshness.py:reconcile_space()` does the COMPLETE loop (add-missing · re-embed-changed via content_hash diff · retract-orphaned via `store.remove_vector`, 2026-06-27) AND it is SCHEDULED: `runtime/bridge.py:507-538`'s `_freshness_loop` daemon mtime-polls the 'extractions' assets and calls it on change (corrected 2026-06-29 — the prior "zero callers" was a grep miss of the `reconcile_extractions` wrapper). | Mechanism + auto-schedule both done. Added 2026-06-29: `ingest(op='reindex', space=…)` — the EXPLICIT on-demand twin for any space (the daemon covers only 'extractions' on mtime). |
| **Rollup can't scale 52k → minibatch-kmeans** | **Plausibly open**, but lives in the rollup-consolidation path (`activation.py:consolidate_rollup`, the C5.4 introspective-data-building of run-records), NOT the durable corpus. Not re-verified to failure this session. | When the rollup distribution exceeds in-memory clustering, swap the consolidation's clustering for minibatch-kmeans (incremental). Scoped to `consolidate_rollup`; the corpus/recall path is unaffected. Treat as a rollup-lane perf task, not a substrate blocker. |
| **35904 = stale chroma** | **Interim-path, not durable.** Chroma references are in the **throwaway** claude-sessions reindex path (`ops/claude_sessions_reindex.py`, the substrate-claude-sessions index @ `~/.cache/company/substrate-claude-sessions`) which services.json + memory both label "INTERIM/throwaway — Tim is building the real memory system elsewhere." | Do NOT invest in repairing interim Chroma. The fused substrate (Leg A) IS the real memory system; the interim claude-sessions index is SUBSUMED by routing transcript search through the corpus `history` space (recollection already indexes exchanges). Retire the Chroma interim once corpus-history search covers transcripts. |
| **Embedding port collision 8004** | **NOT a bug.** `embed-jina-v5` and `embed-qwen3` deliberately SHARE :8004 as mutually-exclusive hot-swap siblings (gpu.py:66-67 documents the same-port swap pattern explicitly; STARTUP.md:40: `swap` refuses them because they set their model differently). Only ONE binds at a time. | None. The collision reading was the critical-comparison failure mode — corrected. (The operative embedder is `embed-pplx` @ :8007; bge @ :8001 is the legacy layer.) |
| **Corpora split-brain** | **Real — and bigger than memory says: THREE indices, verified.** (a) corpora index env-var split (writer ignores `EPISODIC_MEMORY_CONFIG_DIR`, [[area-I-memory-tests]] §migration); (b) the durable corpus (9 spaces) vs (c) the interim claude-sessions Chroma index vs **(d) recollection's own sqlite-vec** (`~/.recollection`, disjoint from corpus `history` — verified via history.py). | (a) Fix the env-var so writer + reader agree; force one reindex (migration-pending). (b/c/d) The fusion collapses all three: ONE substrate (Leg A) is the target; fold recollection's exchange-extracts into corpus `history` (§2 correction) and retire both the interim Chroma and recollection's parallel sqlite-vec. The split-brain IS the patchwork the union eliminates — but it is a 3-way fold, not 2-way. |

**Key reframe:** the memory's bug-list is largely a snapshot of 2026-06-22; the durable
substrate (corpus + space-index + `find_relations` + freshness reconcile + calibrated floor)
is in better shape than the memory implies. The remaining genuine work is (1) the corpora
env-var split, (2) the rollup-clustering scale task, and (3) retiring the interim Chroma by
folding transcripts into corpus `history`. (Item formerly "(2) scheduling reconcile_space" is
DONE — it was already scheduled via bridge.py's freshness daemon, and an explicit on-demand
`ingest(op='reindex')` op was added 2026-06-29. The hybrid-fusion delta is also now BUILT —
`runtime/corpus_fusion.py`, exposed as `corpus(op='query', mode='hybrid')`: RRF over a vector +
a lexical leg over the same corpus space.)

---

## 4. BROKEN / HALF-BUILT SEAMS

- **`reconcile_space` IS scheduled — the "ZERO callers" claim was STALE (corrected 2026-06-29).**
  Re-grep finds a LIVE caller: `runtime/bridge.py:507-538` runs a `_freshness_loop` daemon thread that
  mtime-polls the 'extractions' asset files and calls `freshness.reconcile_extractions()` (→
  `reconcile_space`) on change, emitting a durable event. So the auto-reindex is BUILT AND WIRED for the
  'extractions' recall space. The earlier grep missed `bridge.py` (it greps `reconcile_extractions`, the
  convenience wrapper, not `reconcile_space` directly). RESIDUAL (the genuine gap, now closed 2026-06-29):
  there was no EXPLICIT/on-demand reconcile for an ARBITRARY space — added as `ingest(op='reindex', space=…)`
  (`mcp_face/tools/ingest.py`), the on-demand twin of the auto daemon (any space; conservative
  `retract_extra=False` default for a possibly-partial corpus view).
- **Recollection is a separate episodic index (verified).** `~/.recollection` sqlite-vec is
  disjoint from the corpus `history` space (history.py: "on the corpus, NOT episodic-memory").
  A live second episodic pile until folded into `history` (§2 correction).
- **Company lexical search lives on the INTERIM substrate index, not the corpus spaces.** The
  `session_search.py` `lexical` mode searches the claude-sessions substrate.db chunk text — the
  throwaway index, not the durable corpus. Lifting it onto the corpus spaces is part of the
  hybrid-fusion build (§2 Leg B).
- **Default/unspaced vector index is empty (verified live).** `corpus(op='query')` with no
  space returns `[]` — durable records ONLY live in the 9 named spaces. Any face that queries
  the corpus MUST pass a `space`; an unspaced query silently returns nothing. This is a
  legibility trap for the OWUI seam (Leg C) — the MCP tool must default to a sensible space
  or fail loud, never return a confusing empty.
- **Interim claude-sessions index is parallel scaffolding** (Chroma @ substrate-claude-sessions,
  the reindex timer beat). It is the very "island parallel scaffolding" the union should drop —
  subsumed by corpus `history`. Until retired, it is a live second-pile (the split-brain).
- **Hybrid FUSION leg — BUILT 2026-06-29** (`runtime/corpus_fusion.py`, exposed as
  `corpus(op='query', mode='hybrid')`). It is LATE-FUSION RRF over a vector leg (`suite.query_corpus`,
  meaning) + a lexical leg lifted onto the corpus-space digests (the term-count algorithm from
  `session_search._search_lexical`, now over `corpus.find_corpus(projection=space)` rows resolved via their
  CAS — ONE scan, no inverted index). Fuses by RANK (never score — the projection-discipline law
  corpus_rerank.py:19-20), degrades HONESTLY to lexical-only when the embedder is down (legs_used says so),
  ids are bare so they fuse with the vector leg + remain rerank-able. Rerank composes on top of the fused
  list. Residual future work: a real inverted index (the lexical leg currently reads every digest in the
  space, bounded by LEX_SCAN_CAP) + a true BM25 weighting (RRF needs only ranks, so term-count suffices now).
- **No document loader matrix yet** — dragnet ingests repo files + images only; PDF/docx/OCR
  is net-new (Leg B). Lift OWUI's loader CHOICES, not its code (its loaders are LangChain
  wrappers — reusable as a reference, integrated through the dragnet's kind-pluggable path).
- **Corpora env-var split-brain** (writer ignores `EPISODIC_MEMORY_CONFIG_DIR`) — a known
  migration-pending repair; the reader/writer disagree on the index dir.
- **OWUI's own three mid-migration seams** (chat_message⟷chat-JSON, access_grant⟷access_control,
  knowledge-files-in-meta vs join table — owui §6/§7/§10) — DO NOT inherit. The company has one
  resolution model; absorbing OWUI's half-finished normalization would import duplication. Take
  the retrieval plumbing (BM25/loaders), leave the storage seams.

---

## 5. VERIFICATION DONE

**Verified live (this session, 2026-06-28):**
- Corpus is LIVE; default index empty; durable records in 9 spaces — `mcp__company__corpus(op=query)`
  returned the empty-default + spaces note (Observed, executed).
- The 9 embeddable spaces — `cognition_info(section='spaces')` returned exactly:
  code_archaeology, common_knowledge, extractions, history, operators, principles, repo,
  topics, worldview (Observed, executed). Confirms map's "spaces ⊂ projections."
- `find_relations` + `corpus` MCP tools are LIVE and callable (schemas fetched + corpus called).
- **8004 is a swap-sibling, NOT a collision** — read services.json:446 (embed-jina-v5) +
  :567 (embed-qwen3) both :8004; gpu.py:66-67 + STARTUP.md:40 document the deliberate
  same-port hot-swap pattern (Observed, file:line).
- **Floor already recalibrated** — `decision_memory.py:55` `_CTX_FLOOR=-0.13` (Observed, grep).
- **Freshness auto-reindex BUILT** — `freshness.py:reconcile_space()` does add/re-embed/retract
  with `store.remove_vector` (2026-06-27) (Observed, read file head).
- **35904/Chroma is interim-path** — chroma refs only in `ops/claude_sessions_reindex.py` +
  the throwaway substrate-claude-sessions path (Observed, grep + services.json notes).
- OWUI RAG delta — read [[owui-side-map]] §5 in full: 14 backends, hybrid+rerank, loader
  matrix, agentic retrieval, knowledge UI (Observed, source map cites file:line).
- **Company HAS a lexical search mode** — `session_search.py` declares a `lexical` mode (term
  search over substrate.db chunk text, zero-GPU) alongside `semantic` (Observed, read file head).
  Corrects an earlier "cosine-only" assumption.
- **Recollection is DISJOINT from corpus `history`** — `projections/history.py` states verbatim
  "on the corpus, NOT episodic-memory"; recollection is its own sqlite-vec store (Observed,
  read projection + area-I §1). Two separate episodic indices.
- **`reconcile_space` IS scheduled (corrected 2026-06-29)** — `runtime/bridge.py:507-538`'s
  `_freshness_loop` daemon calls `reconcile_extractions`→`reconcile_space` on an mtime-gated poll of the
  'extractions' assets (Observed, read bridge.py). The earlier "ZERO callers" grep matched only the literal
  `reconcile_space` token and missed the `reconcile_extractions` wrapper the daemon actually calls. The auto
  loop is BUILT AND WIRED; the only real residual (an on-demand any-space op) is now `ingest(op='reindex')`.
- The rollup 52k-scale issue is "plausibly open" — NOT re-verified to failure; the term
  minibatch-kmeans is absent from current activation.py (the bug may predate or be unrelated).
- OWUI Tools→MCP wiring works as the union seam — INFERRED from owui §1.5 file:line; the
  actual registration of company MCP tools INTO an OWUI instance is NOT yet executed/tested.

**Not done:** did not stand up an OWUI instance; did not execute a hybrid-search build; did not
re-run the rollup at scale. These are build/verify steps for the implementation loop, not this
proposal.

---

## NEXT STEPS (options)

- **A — Depth:** trace the `reconcile_space` callers + the rollup `consolidate_rollup`
  clustering to confirm/deny the two remaining "plausibly open" issues with execution evidence
  before any build (closes the inferred gaps in §5).
- **B — Map:** draw the one-substrate union as a relational diagram (corpus core → spaces →
  BM25/loader legs absorbed → MCP-tool seam → OWUI face) so the union vs bridge distinction is
  visible at a glance, for Tim's eye.
- **C — Artifact:** draft the build-prep completion-criteria for the fusion's largest net-new
  item — the **hybrid BM25 leg** on `corpus(op='query', mode='hybrid')` reusing the existing
  rerank — since that is the real gap and everything else is wiring or absorption. (Recommended:
  it materializes the one genuinely new capability; the rest is union-discipline, not new code.)
