# The Three-Body Memory Merge — Current State · Floor · Intention

> **What this doc is.** Tim's correction (2026-06-11) to the merge framing: *"all of them need big upgrades — put what each currently is, as well, below the floor to my intention."* So this is not "combine three strong things." All three current systems sit **below the floor** — beneath the minimum bar — measured against the intention. The relative strengths between them (capture vs structure vs lifecycle) are real but they are *sub-floor in absolute terms*. The merge target is the **intention**, far above, and every body needs a big upgrade to climb to it.
>
> **Reading convention.** For each body: **CURRENT** (grounded from live measurement 2026-06-11, marked Observed/Inferred) → **why it's sub-floor** → **FLOOR** (the minimum it must at least reach) → **INTENTION** (the ceiling — my best expansion of Tim's goal-function, written per *make-my-words-better* / *expand-don't-echo*; **marked tentative — Tim corrects these**).
>
> Companion docs in this folder: `INVENTORY.md` (episodic-memory traced), `UPSTREAM-DOCS.md` (its upstream), `LANDSCAPE.md` (18 comparable systems + design lessons), and `reads/` (code-grounded deep reads of the spine, store, substrate-mcp, conversation-intelligence, model layer).

---

## THE LENS (Tim, 2026-06-11) — read everything through this

Tim re-aimed the whole effort with five dense points. They change what the merge *is*:

1. **The clean split — conversation store vs all content.** There are two categories, not three systems: **the conversation store** (the raw Claude Code transcripts) is the **only primary source** — and **all content in every system** (the Company corpus's 2,111 records, substrate-mcp's ~114k vault chunks, conversation-intelligence, *everything*) is **generated output derived from the transcripts**. *Nothing anywhere was written, reviewed, or even read by Tim.* This was intentional. → Correction to the earlier framing: substrate-mcp's vaults are **not** a hand-curated "knowledge body"; they are generated projections of the conversation stream, same as the rest.

2. **The provenance spine — the tool-call→artefact-address join.** The conversation-store schema (~16–19 columns; the `tool_calls` table has **6.7M rows**) carries, in the tool-call inputs, **the addresses of the artefacts** (the file paths written/edited). So there is a latent **provenance graph**: every generated artefact in every system → the `tool_call` that wrote/edited it → the exchange → the session → the timestamp → the fact that Tim was running multiple different things across parallel sessions at that moment. The conversation store is therefore not just searchable memory — it is **the spine that re-anchors all generated content to its genesis-in-conversation, to when it was described and discussed, to its point in time.** *(Observed, partial: the Company corpus already anchors each generated record by `source_address: exchange://<sid>/<i>` + `ts_source` timestamp; episodic-memory already holds the 6.7M tool-call rows with artefact paths in their input JSON — but the cross-system join does not exist yet, and `tool_result` is unparsed.)*

3. **The dormancy frame — the inflection point.** None of the content anywhere is complete or finished. It is **unused dormant production material** — produced (generated from transcripts) but never activated. **What we are doing now is the inflection point** where dormant generated material becomes one living, used memory. *(This is `incomplete-work-in-scope` + `scaffolding-not-spec` at corpus scale: adopt and activate, never treat as the bar.)*

4. **The bigger model-layer intention.** Tim intends to do **a lot more with the Company's local-model systems**. Read and design assuming a *growing* model layer (embedding at scale, always-on mining, consolidation passes, on-device cognition over memory) — not today's usage.

5. **conversation-intelligence** — a half-built, never-used Supabase project (`~/repos/Supabase/`) with **unique designs worth harvesting for inspiration**. Plus a live third ingestion lane already exists: Tim's SessionEnd hook syncs the same transcripts to a Supabase `conversation-archives` bucket + `conversation-sync` edge function.

**What the lens does to the intention.** The merge's ceiling is no longer just "three faculties of memory." It is: **the conversation store as the sole primary-source spine and provenance graph → every dormant generated artefact across every system re-anchored to its transcript genesis (what was written, when, while discussing what, across which parallel sessions) → activated from dormant production material into one living, used, self-improving memory → driven by a growing local-model layer.** The transcripts are the root; everything else is a regenerable projection of them, and the inflection point is wiring the projections back to the root and turning them on.

---

## The altitude stack (the shape Tim asked for)

```
   ▲  INTENTION  — the Company's ONE living memory (goal-function / felt experience)
   │      total automatic recall + deep addressed understanding + living metabolism,
   │      over conversations AND knowledge, fabric-embedded, governed, self-injecting
   │      at Tim's altitude, growing itself. The entity that remembers its whole life
   │      and learns from it.
   │
   ├───────────────────  THE FLOOR  ───────────────────  (minimum acceptable bar)
   │      captured-into-the-Company · raw + distilled both running · addressed ·
   │      fabric-grade embeddings · consolidation alive · fed from ALL history
   │
   │   ░░ everything below here is CURRENT REALITY — all sub-floor ░░
   │
   │   ① episodic-memory   ██  total raw capture, but flat / dumb / isolated / unused
   │   ② Company corpus    ██  beautiful architecture, but starved / distill-only / batch
   │   ③ substrate-mcp     ██  right machinery, but wrong place / documents-only / island
   ▼
```

The gap between the grey band and the floor is the "big upgrade" each one needs. The gap between the floor and the intention is the goal-function — the part worth aiming the whole build at.

---

## ① episodic-memory — *the capture firehose*

**CURRENT (Observed, 2026-06-11).** Raw verbatim capture of every Claude Code conversation via a SessionStart hook: **75,374 exchanges across 13,270 conversations**, a 10.87 GB sqlite-vec index over a 13 GB archive in `~/.config/superpowers/`. Embedded per-exchange with a local 384-dim MiniLM (bge-small at v1.4.2). Two MCP tools (`search`, `read`); vector-KNN + SQL `LIKE`. No structure, no addressing, no understanding, no lifecycle. **Inferred:** it is not wired into the Company at all — it's a sidecar plugin Tim explicitly set aside as a *system* (`feedback-no-episodic-memory`).

**Why it's sub-floor.** It captures everything and comprehends nothing. A dead flat archive: it can find a similar exchange, but it cannot tell you the *decision* in it, relate it to another, resolve it by condition or time, or feed any of it into the Company. The richest record of the Company's entire life is sitting in a folder the Company can't see.

**FLOOR.** Its capture must feed the Company (not a sidecar store); exchanges must land as addressed records (`exchange://<sid>/<i>`), not flat rows; embeddings at fabric grade (`qwen3-embedding:4b` / `bge-m3`), not MiniLM.

**INTENTION (tentative — Tim corrects).** The Company's **total-recall sensory layer** — every word the entity has ever exchanged, captured automatically and continuously, lossless, as the raw ground-truth bedrock under everything else. Not a plugin you query; the Company's complete *episodic memory of its own life*, always-on. This is the "I remember everything that ever happened" floor of an entity with genuine continuity — the thing that makes *thousands-of-yous* (`project-company-one-entity`) resolve to one memory instead of a thousand amnesiac sessions. The upgrade is not better search; it is **promotion from archive to bedrock**.

---

## ② Company corpus — *the addressed, governed understanding layer*

**CURRENT (Observed, 2026-06-11).** The architecture is already right: `exchange://` + `memory://` + `deferred://` addresses, **projections** (per-consumer views, e.g. `history`), `space='history'`, embedding through the fabric (`qwen3-embedding:4b`, `bge-m3`), provenance, governance (`proposes_only`). A real conversation pipeline exists — **`flows/transcript_mine.py` (G23)** + `roles/mine_exchange.py` — but it is a **distiller**: it runs each exchange through the resident 4B and extracts `{decision, rationale, tim_correction, my_error, bug_fix, needs_tim, frustration, pattern_tag}`, idempotent on `exchange://<sid>/<i>` keys. **Observed:** only **2,111 total records**; the `exchange://` records visible are from essentially one session. The `pattern_cluster` reduce is a *flagged follow-on, not built*. No raw layer, no consolidation/forgetting, no temporal resolution actually running.

**Why it's sub-floor.** It's the cathedral with almost nothing in it. The mechanism for a great memory exists; the memory doesn't. It is **distill-only** (violates the landscape's #1 lesson — run raw *and* distilled), it is **starved** (fed bounded on-demand batches, not the firehose), and the lifecycle (cluster, consolidate, temporal self-injection) is mechanism-without-execution.

**FLOOR.** Fed continuously from ①'s firehose, not batches; a raw layer beneath the distilled layer; `pattern_cluster` actually running over real volume; the G23 extraction applied across *all* history, not a sample.

**INTENTION (tentative — Tim corrects).** The Company's **understanding layer** — where raw experience becomes structured, addressed, related, governed knowledge the entity reasons *from*. Every decision, rationale, correction, named frustration, and recurring pattern across Tim's entire history-of-working-through-agents, distilled and addressed and clustered into self-improving knowledge — the `introspective-data-building` law fully realized: *operation → record → substrate → rollup → knowledge that improves the operation*. Condition- and time-addressed memories (`memory://…`) that **self-inject when relevant** (`common-memory-temporal`, GC14). Per-consumer projections so the same junction shows each consumer the field it needs (`address-accumulation`). This is the Company **knowing itself and knowing Tim** — and the upgrade is **promotion from empty cathedral to living knowledge**.

---

## ③ substrate-mcp — *the lifecycle machinery (built in the wrong place)*

**CURRENT (Observed, 2026-06-11).** A v0.1.0 pre-Company document substrate at `~/repos/obsidian-overlord`. Indexes Tim's **knowledge vaults** — ~**114k chunks across 10 corpora** (visual-design DNA, universal-mechanics, claude-code-atlas, claude-platform-docs, unification-vault, …), bge-m3 @ `localhost:8001`, **Chroma** store, ~600-token overlapping chunks, a **2,399-node type-graph**. **Observed (tool surface):** it already exposes the lifecycle verbs the other two lack — `consolidate` (sleep-time consolidation), `cluster_by_embedding` (pattern clustering), `traverse_links` / `get_neighborhood` (graph multi-hop), `compare_state_observations` / `find_state_asymmetries` / `get_state_history` (a temporal/state layer). **Inferred:** these are real implementations, but I have read them by tool description, not yet at code level.

**Why it's sub-floor.** It built the right machinery in the wrong place. It is an **island**: separate from the Company, on a parallel Chroma store, **document-oriented not conversation-oriented**, predating the entity. The consolidation/clustering/graph/temporal capability — the exact things the landscape report named as the big gaps — exists but is disconnected from the memory that needs it, and the knowledge corpora it holds are walled off from the Company's common memory.

**FLOOR.** Its machinery (`consolidate`, `cluster_by_embedding`, graph traversal, state/temporal) harvested into the Company natively (per `feedback-not-a-replacement`: it *informs*, it is not a drop-in); its knowledge-vault corpora connected to the one common memory rather than a separate island.

**INTENTION (tentative — Tim corrects).** Its lifecycle machinery becomes the Company's **metabolism** — the consolidation, clustering, forgetting, graph-linking, and temporal-asymmetry processes that keep memory *alive* (the "dream phase"), running natively inside the Company over the merged conversation-plus-knowledge corpus. And its document corpora — Tim's design DNA, universal-mechanics, the Claude Code Atlas, his actual accumulated knowledge — **stop being a vault island and become part of the entity's memory of what Tim knows and has built**. The upgrade is **promotion from disconnected document-indexer to the Company's living metabolism + knowledge body**. (Open fork: harvest-and-retire ③ into ②, or keep ③ as a running organ — see Decisions.)

---

## The unified intention (the ceiling above all three)

**One living memory for the Company-as-entity.** Not three systems, not even one merged system — *the entity's memory*, with three faculties that are currently three sub-floor fragments:

- **Capture (from ①):** total, automatic, lossless recall of everything the Company has ever exchanged — its episodic bedrock.
- **Understanding (from ②):** that raw experience distilled, addressed, related, governed, projected per-consumer, self-injecting by condition and time — the entity reasoning from its own life.
- **Metabolism (from ③):** consolidation, clustering, forgetting, graph multi-hop, temporal asymmetry — the processes that keep the memory alive instead of monotonically growing — plus the entity's *knowledge body* (Tim's corpora) folded into the same memory.

Over **both** its conversations **and** its knowledge corpora, fabric-embedded, governed (proposes-only, provenance, revert), presented and resolved at **Tim's altitude** (`altitude-transformation-layer`), and **growing itself** (the self-build wire dispatches its own upgrades). This is the memory of an entity with continuity — the substrate under *one-entity*, *common-memory-temporal*, *introspective-data-building*, and *context-forager* all at once.

---

## The relational primitive that lets them compose

**The addressed, embedded record** — and for conversations specifically, the **`exchange://<sid>/<i>` junction**. It already exists in two of the three: episodic-memory keys exchanges by `session+index`; the Company keys them `exchange://<sid>/<i>`. **The same primitive on both ends.** The merge connects a pipe that is already the same shape — ①'s firehose fills the `exchange://` address space, ② distills and addresses it, ③ consolidates/clusters/relates it over time. One primitive, three faculties acting on it.

---

## The upgrade ledger (current → floor → intention, per faculty)

| Faculty | Current (sub-floor) | Floor | Intention |
|---|---|---|---|
| **Capture** ① | flat, MiniLM, isolated, unused | feeds Company, addressed, fabric-embedded | total-recall bedrock, always-on, lossless |
| **Understanding** ② | starved (2,111), distill-only, batch | raw+distilled, fed from all history, cluster running | self-improving addressed knowledge, self-injecting, per-consumer projections |
| **Metabolism** ③ | island, documents-only, Chroma, by-description | machinery harvested into Company, corpora joined | living dream-phase + knowledge-body inside the entity |
| **Embedding** | MiniLM 384 (①) / bge-m3 (③) / fabric (②) split across 3 stores | one fabric-grade embedder | model-layer-native, swappable, resource-managed |
| **Store** | sqlite-vec (①) / Company store (②) / Chroma (③) — **three stores** | one store of record | the Company store as the single addressed home (feasibility unknown — needs code read) |
| **Retrieval** | KNN+LIKE (①) / corpus query (②) / semantic+structural+graph (③) | hybrid + progressive-disclosure budgeting | altitude-resolved, self-injecting, grounded-chain-first |
| **Lifecycle** | none (①②) / built-but-islanded (③) | consolidation alive | full metabolism: consolidate, cluster, forget, relate, temporal |

---

## Open decisions (not assumed away)

- **D1 — Store of record.** Does the merged memory live in the Company `store/`? Is that sqlite-vec under the addresses, or something else? This decides "wire three things that already fit" vs "rebuild the storage layer." **Load-bearing, unverified — needs a `store/` code read.**
- **D2 — Fate of ③.** Harvest-and-retire substrate-mcp's machinery into the Company, or keep it running as a Company organ? Tim's call.
- **D3 — Raw volume.** episodic-memory holds 75k exchanges / 13 GB raw. Does *all* of it become Company bedrock, or is there a capture window / tiering? (No-MVP says all; storage reality may force tiering — surface, don't assume.)
- **D4 — Embedder unification.** One fabric embedder for everything means re-embedding ①'s 75k exchanges and ③'s 114k chunks at fabric grade — a real cost. Worth it for one vector space; needs sizing.
- **D5 — external reference.** `memoirs` (from `LANDSCAPE.md`) already does RRF-hybrid + HippoRAG graph + PII redaction + bi-temporal on the same sqlite-vec substrate, fully local — read it before building the retrieval/lifecycle pieces (`feedback-not-a-replacement`: informs, not drop-in).

---

*Status: tentative framing for Tim's correction. The CURRENT rows are grounded (live measurement). The FLOOR rows are my read of the minimum bar. The INTENTION rows are my expansion of Tim's goal-function — the part most in need of his steer.*

---

## SYNTHESIS — the merge, code-grounded (2026-06-11, five-reader fleet)

Five readers traced the code (`reads/1`–`5`). The headline: **almost the entire merge is wiring + volume + activation of pieces that already exist — with exactly ONE genuinely large net-new build (the storage backend) and a short, specific net-new list beyond it.** The systems were, in several places, *built to meet* — they just were never wired together and never run at scale.

### The root + spine is live-queryable TODAY (no build, no migration)
- **The provenance join runs now.** `tool_calls.tool_input → JSON_EXTRACT('$.file_path')` carries the artefact address on **99.99%** of Write/Edit rows; the `exchange_id` FK completes the chain *artefact → tool_call → exchange → session → timestamp → parallel-activity*. Verified on live data: 75,397 exchanges / 6.72M tool_calls / 7,351 sessions / 96 projects; **263 distinct sessions in one 10-minute window** (the parallel-activity dimension is measurable, not aspirational).
- **The two systems already share the coordinate.** episodic-memory points *up* from a file → exchange; the Company points *down* from a record (`source_address: exchange://<sid>/<i>` + `ts_source`, enforced by a fail-loud lineage gate in `runtime/corpus.py`). They meet *at the exchange*.
- **conversation-intelligence already prototyped the spine** — a 9,833-row artifact-provenance graph (conversation↔tool_call↔artifact + operation + time) and **turn-context embeddings** (24,847 built): the embedded unit is the turn-pair + a one-line tool-call summary, baking the `Intent → response → Execution` circuit into the vector. Three independent pieces converging on one join.

### D1 — the one big build: the store-of-record backend
**Verdict: ARCHITECTURE YES / CURRENT BACKEND NO.** The Company store today is a content-addressed **ext4 filesystem** (`/home/tim/company/.data/store/`) + filesystem vectors (bge-m3 / **1024-dim**, 2,186 live) — *not* SQLite, *not* pgvector. The long-designed **Postgres + pgvector resolver does not exist yet** (only `FilesystemResolver`). At 75k+ scale the filesystem read-paths full-scan flat dirs and re-parse whole `.jsonl` logs per query — the wrong shape. **But** the address grammar, open-record schema, projection/relation/mark registries, and the lineage gate all sit behind the **C4 Resolver Protocol** and carry over to SQL *unchanged* — every filter key already maps to a `WHERE`. So this is **an extension along an already-sealed seam (one new `*_resolver.py`), not a schema rebuild.** It is, however, the load-bearing prerequisite for everything at scale.

### The faculties — what's harvestable vs net-new
- **CAPTURE (①, episodic-memory):** the automatic firehose works and is current — but lives in a *versioned plugin cache*, so it must be **mirrored Company-side**. The raw `.jsonl` archive (13 GB, 29,678 files) is the recoverable source. **`tool_result` is 100% NULL** — the entire tool-output axis is empty; parsing it from the raw archive is **net-new** (small, recoverable — episodic has the JSONL, just never parsed results).
- **UNDERSTANDING (②, Company G23 miner):** live and correct — distills the 8-field schema per exchange, idempotent on `exchange://`, on the resident 4B. Run on only **2,111 records**; the `run_reduce(cluster)` reduce **never fired**. Work = *run it over all history at volume* (not new code).
- **METABOLISM (③, substrate-mcp):** ports **cheaply** (SQLite is ground truth; Chroma is a disposable projection only clustering touches). Harvest: the **temporal/state layer** (`state_history` append-only change-log + `find_state_asymmetries` signed-time-gap *pure sensor* = the gap-pressure substrate, zero model calls), `cluster_by_embedding` (NumPy spherical k-means w/ centroid-term labels = the unbuilt `pattern_cluster`), and the structure-aware chunker w/ first-class provenance. **Honesty flag:** substrate's `consolidate` is *aspirational* (resolves wikilinks + recounts types only) — **true dedup/merge/prune consolidation is net-new.**
- **MODEL LAYER (fabric):** one embedder already shared with substrate-mcp (`bge-m3` @ vLLM `:8001`, **1024-dim**); `qwen3-embedding-8B` cataloged (a registry swap). Constraint: **16 GB card** → a fabric-grade re-embed of 75k+ exchanges is an *evicting phase*, not co-resident. Three live dims (MiniLM **384** / bge-m3 **1024** / qwen3) don't interoperate → **a re-embed migration is required** (the 384 vectors are not reusable). Seam finding: the merge needs **volume, continuity, tier — not new architecture.**

### Decisions — resolved by the reads
- **D1 (store):** extend the Resolver Protocol with a **Postgres + pgvector backend**; one store-of-record, two namespaces (raw bedrock ‖ generated content). Schema carries over. *The one big build.*
- **D2 (fate of substrate-mcp):** **harvest the machinery, retire the Chroma island, re-embed fresh.** Don't keep it running. (Its corpus is dormant generated content — regenerable.)
- **D3 (raw volume):** all 75k exchanges become bedrock (no-MVP) — but **storage-backend-gated** and re-embed is an evicting phase, so this *sequences after D1*.
- **D4 (embedder):** unify on **bge-m3 / 1024-dim now** (already shared), `qwen3-8B` as a later registry swap; the re-embed migration is mandatory regardless.
- **D5 (memoirs):** still the external reference for **true consolidation + RRF-hybrid + PII** — exactly the net-new pieces substrate-mcp doesn't actually provide.

### New decisions the reads surfaced
- **N1 — the chunk/embed unit.** conversation-intelligence's **turn-context unit** (turn-pair + tool-call summary) is richer than episodic's raw exchange or the Company's bare exchange — it bakes Execution into the vector. *Lean: adopt it.*
- **N2 — the edge layer is unbuilt.** `find_relations` is registered-but-empty (relation *types* exist, no edges, no edge table). The graph faculty (relations between memories) must be **built**, not harvested.
- **N3 — `tool_result` parse.** Decide the parse pass that fills the empty output axis from the raw archive (it's where half the causal story lives — what came *back* from each action).

### The net-new list (everything else is unify + turn-on)
1. The **Postgres + pgvector resolver** (the one big build).
2. **`tool_result` parsing** (fill the empty axis from the raw `.jsonl`).
3. **True dedup/merge/prune consolidation** (substrate's is aspirational).
4. **`find_relations` edges** (the graph faculty).
5. The **cross-system join code** (the spine is queryable but nothing wires it).
6. The **re-embed migration** to one 1024-dim space.

Everything not on that list — capture, distillation, clustering, the temporal/state sensor, the embedder, the resident-swarm mining, the addressing/projection/lineage schema — **already exists** and needs unifying into the Company and running at volume. *This is the inflection point Tim named: the dormant material is mostly built; the merge turns it on, joined, on a backend that can hold it.*
