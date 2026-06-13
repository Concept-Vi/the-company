# Read 3 — substrate-mcp: the metabolism layer to harvest

**Source:** `/home/tim/repos/obsidian-overlord/` — package `substrate_mcp` (`src/substrate_mcp/`).
**State dir:** `/home/tim/repos/obsidian-overlord/.state/` — `substrate.db` (SQLite, ~5.4 GB), `chroma/` (per-vault Chroma collections), `config.json`.
**Live config (verified):** provider `openai` (OpenAI-compatible, not Ollama despite the default), model `BAAI/bge-m3`, 10 vaults registered (`vi-context-design`, `_issues`, `visual-dna`, `visual-design-corpus`, `ulm-inventory`, `unification-vault`, `claude-code-atlas`, `claude-platform-docs`, `elevenlabs-mcp`, `relative-difference`), `chunk_target_tokens=600`, `chunk_overlap_tokens=64`.

**The lens (Tim's framing).** This system predates the Company. Its corpus (~114k chunks) is itself **generated** content (transcript-derived, nothing hand-authored, currently dormant). The corpus is not the asset — **the machinery is**. substrate-mcp already implements the lifecycle verbs the Company's other systems lack: re-embed-on-delta, embedding clustering, typed-relation graph walking, and — most novel — a **temporal state layer** that records when each unit's lifecycle value last changed and measures the *time-asymmetry between a thing and the things that point at it*. Per Tim's law (found-elsewhere ≠ replacement): this read tells us what to **rebuild into** the Company's substrate, not what to bolt on.

A structural fact worth stating up front, because it changes the porting cost dramatically: **SQLite is the ground truth; Chroma is one disposable projection.** The module docstring in `embeddings.py` says it directly — "The semantic face is one projection of the substrate, not its primary representation… The ground-truth for chunk text + structural relations stays in SQLite." Chroma stores only `{chunk_id → vector + a metadata copy}`. Every mechanism below except clustering reads from SQLite. That is the single most important harvest finding.

---

## Mechanism-by-mechanism

For each: **what it does · how (traced) · how coupled · harvest-worthiness.** Evidence is marked **Observed** (read directly in code) or **Inferred** (pattern-matched, not executed).

---

### 1. `consolidate` — the "sleep-time consolidation" — **OBSERVED, and it is NOT what the name implies**

**Tool:** `server.py:1042` `consolidate(vault=None, cross_vault=False)`. Body: `_consolidate` at `server.py:784`.

**What it actually does (Observed).** It does **two** things, and **only** two:
1. `db.resolve_wikilinks_for_vault(...)` — resolve every still-`unresolved` wikilink's `target_text` to a concrete `address_id` (`db.py:567`).
2. `db.recount_type_instances(...)` — recompute each type's `instance_count` from `type_assignments` (`db.py:346`).

It then resets the per-vault dirty counter (`_dirty[vname] = 0`).

**It does NOT** dedup, merge, prune, summarise, or re-embed. There is **no semantic consolidation** here — the name is aspirational. Re-embedding is a *separate* lifecycle handled inline by `_index_one_file` on content-hash delta (see Mechanism 7). This is the single biggest expectation-correction in this read: the verb the Company actually wants for "sleep-time consolidation" (dedup near-duplicate chunks, merge, prune stale) **does not exist in substrate-mcp** and would be net-new.

**How resolution works (Observed, traced — `db.py:722` `_resolve_target`).** For each unresolved link's `target_text`, try in order, returning at the first non-empty candidate set:
1. exact `rel_path` match (append `.md` if missing);
2. exact path-**suffix** match (`%/target.md`);
3. case-insensitive of (1)+(2);
4. **basename-only** match (last path segment, any directory) — Obsidian-style loose linking;
5. **title** match from frontmatter (last resort).
- Exactly one candidate → `resolution_state='resolved'`, set `resolved_address_id`.
- More than one → **ambiguous**; pick the shortest `rel_path` (most top-level) and mark `resolution_state='ambiguous'` (still wires an edge, but flagged).
- `cross_vault=True` adds step 6: a **stricter** resolver (`_resolve_target_strict`, `db.py:677` — only exact/suffix/case-insensitive, NO basename/title fallback) tried against *other* registered vaults in an optional priority order; matches get `resolved-cross-vault` / `ambiguous-cross-vault` states so callers can filter cross-boundary edges. The strictness exists because a bare `[[Note]]` should not silently bind to another vault's `templates/Note.md`.

**The "sleep" cadence (Observed).** `_index_one_file` calls `_bump_dirty` per write; once 5 writes accumulate (or the watcher batch finishes, `_reindex_paths:837`), a `_consolidate` pass fires automatically. So consolidation is the *debounced batch-reconciliation step* that turns freshly-written files' dangling link text into resolved graph edges. **That is the real verb: deferred edge-resolution + counter-recount, batched so it isn't O(vault) on every keystroke.**

**Coupling.** Pure SQLite. Zero Chroma. Trivially portable.

**Harvest-worthiness: HIGH — but reframe it.** The valuable pattern is **deferred, debounced reconciliation of unresolved references into resolved edges, with ambiguity preserved as a first-class state rather than dropped.** That is exactly the Company's registry-filling / grounded-chain need: references written by an agent (or by a conversation) are *intent to link*; resolution is a separate metabolic pass that either binds them or marks them ambiguous/unresolved (never silent-drops — aligns with Tim's no-silent-failures law). The Company should harvest the **pattern and the multi-strategy resolver ladder**, and then *additionally build* the genuinely-missing semantic-consolidation verb (dedup/merge/prune) that this system's name promises but does not deliver.

---

### 2. The temporal / state layer — `get_state_history`, `compare_state_observations`, `find_state_asymmetries` — **OBSERVED — the crown jewel**

This is the most novel machinery in the package and the strongest harvest candidate. It is small, pure-SQLite, and implements a primitive the Company does not currently have.

**What a "state observation" is (Observed).** Every vault has a discovered **state-axis** — a single frontmatter field that represents the unit's lifecycle dimension (e.g. `status`, `state`, `articulation-state`, `lifecycle`, `stage`, `phase`). It is auto-detected by the schema profiler (`schema_profiler.py:42` `STATE_AXIS_NAMES` regex + value-vocabulary candidacy at `:533`+; a field qualifies if ≥30% of its values are recognised state-tokens, it's enum-shaped not prose, well-covered, and low-cardinality). A "state observation" is one row in `state_history`: `(address_id, axis, value, observed_at)`.

**How state is tracked over time (Observed — `scanner.py:575` Pass 6, `db.py:1032` `record_state_transition_if_changed`).** On every scan, for each file, read the frontmatter value of the state-axis. Call `record_state_transition_if_changed`: it compares the new value to the **most recent** recorded value for that `(address_id, axis)`; **only if it differs** (or no prior row) does it append a new row. So `state_history` is an **append-only, change-only log of lifecycle transitions** — not a snapshot per scan. List-valued fields are skipped (a real state-axis is single-valued; multi-valued ⇒ misclassified, and the scanner emits a demotion warning, `scanner.py:622`).

**The mtime bootstrap (Observed — subtle and important).** On the *first* observation of a unit, `observed_at` is set to `min(file.mtime, now)` rather than `now` (`db.py:1059`). Rationale (verbatim in code): the state "has been at this value since at least the file's mtime, which is a real lower bound." This makes stagnation/age queries **meaningful from scan 1** instead of all units looking freshly-changed at first index. `backfill_state_history_from_mtime` (`db.py:1094`) retrofits existing installs. **This is a genuinely clever idea worth stealing wholesale: bootstrap temporal history from the filesystem's own mtime so the timeline isn't a lie on day one.**

**The three query tools (Observed):**
- **`get_state_history(address, axis=None, limit=50)`** (`server.py:1445`) — the transition log for one unit on one axis. Axis defaults to the vault's discovered state-axis.
- **`compare_state_observations(addresses[], axis=None)`** (`server.py:1483`) — "most primitive temporal-state query." For each address: `{state_value, observed_at, state_history_length}`. **No thresholds, no labels** — raw timestamps, caller compares however it wants. (This restraint is deliberate and recurs.)
- **`find_state_asymmetries(...)`** (`server.py:1539`) — **the novel one.** For every `(unit, referrer)` pair where the referrer links to the unit AND both have state-history on the axis, compute the **signed time-gap** `referrer_observed_at − unit_observed_at`:
  - **positive** → the referrer changed state *after* the thing it points at;
  - **negative** → the referrer changed *before* its target;
  - **zero** → co-observed (often both bootstrapped from the same scan).
  The SQL (`server.py:1606`) joins `wikilinks → addresses(referrer) → addresses(unit) → state_history(unit, MAX id) + state_history(referrer, MAX id)` on the axis, so it's comparing each side's *most recent* transition. Rich filter set (observed-before/after windows on either side, state-value whitelists, relation-kind filter, `min_abs_gap_seconds`) and eight sort modes (`abs_gap_desc` default, signed-gap, observed-asc/desc on either side). Returns raw pairs with `gap_seconds`.

**The discipline (Observed, repeated in docstrings):** *"No interpretation. Whether a gap is 'old' or 'stagnant' or 'fresh' is something the caller assigns. The substrate does not assume any rhythm of work, any threshold for staleness, or any meaning to the asymmetry."* The substrate is a **sensor**, not a judge.

**What an "asymmetry" *means* (Inferred — labelled).** I have not executed this against the live DB, but the design intent reads clearly: it surfaces **stale-reference and lag relationships**. Example: a foundational note that hasn't changed state in months, pointed at by twenty newer notes that have all moved to `settled` — a large positive gap on every edge says "the foundation is lagging its dependents," a possible signal the foundation needs revisiting. Or the inverse: a referrer that advanced to `done` while its prerequisite is still `proposed` (negative gap) — a possible ordering violation. The system deliberately does **not** decide which; it hands the gaps up. **Inferred: this is a structural gap-pressure / stagnation sensor expressed purely in time + graph, with zero semantic cost.** It maps tightly onto Tim's own "Gap Pressure (discovered law)" and "common memory + temporal resolution" notes — condition-addressed memory, time as an axis of context.

**Coupling.** 100% SQLite (`state_history`, `wikilinks`, `addresses`). Zero Chroma, zero filesystem at query time. The only inputs are: the discovered state-axis (schema profiler) and the wikilink edges (consolidate). Fully self-contained and portable.

**Harvest-worthiness: HIGHEST.** This is the mechanism the Company most lacks and most wants. Three reasons:
1. It's the operationalisation of **"temporal resolution" / common-memory-over-time** — condition-addressed, self-injecting memory needs exactly this substrate (when did this last change; what's stale relative to what points at it).
2. It is a **pure metabolism sensor** — generates signal from existing structure with no model calls, perfectly matching the "introspective data building" law (operation self-instruments → run-records → knowledge that improves the system).
3. The **mtime-bootstrap** and the **interpretation-free primitive** are both directly reusable design moves. The Company's addresses already have a state/status notion; adding an append-only change-log + the signed-gap query is a small, high-leverage build.

---

### 3. `cluster_by_embedding` — embedding clustering (maps to Company's flagged-but-unbuilt `pattern_cluster`) — **OBSERVED**

**Tool:** `server.py:3747` `cluster_by_embedding(vault, n_clusters=10, max_iter=30, sample_chunks_per_cluster=3, top_terms=10, top_files=10, seed=42)`.

**Algorithm (Observed, traced).** Hand-rolled **spherical k-means** in NumPy — no sklearn dependency:
1. Pull *all* embedded chunks for the vault from Chroma: `col.get(include=["embeddings","documents","metadatas"])` (`server.py:3791`).
2. `X = float32 array (n_chunks × dim)`; `k = max(2, min(n_clusters, n_chunks))`.
3. Seed `k` centroids from random chunk vectors (`random.Random(seed)` → reproducible).
4. Iterate up to `max_iter`: compute **cosine similarity** `sims = (X @ Cᵀ)/(‖X‖‖C‖)`, assign each chunk to `argmax`; recompute centroids as the mean of members; **empty clusters reseed** from a random point. Converged when labels stop changing (`np.array_equal`).
5. Per cluster, report: `n_chunks`, `n_files`, `top_files` (by chunk-count, address-keyed), `sample_chunks` (random, 280-char snippets), and `centroid_terms` — top frequency tokens after a built-in stopword filter (`_CLUSTER_STOPWORDS`, `server.py:3734`) and a `[A-Za-z][A-Za-z\-]{3,}` token regex. So clusters are **labelled by their salient words**, giving an interpretable theme without an LLM.

**Stated purpose (Observed docstring):** *"discover dense topical regions in a vault that aren't apparent from the folder structure or the wikilink graph… particularly useful as a first-orientation step on an unfamiliar vault."* Verb framing: `dividing` (partition the embedding face) + `interpreting` (centroid_terms surface themes).

**Coupling.** **Chroma-coupled** — this is the *one* read-path that genuinely needs the vector store, because it loads all vectors into memory. NumPy + stdlib only otherwise.

**Harvest-worthiness: MEDIUM-HIGH.** It is the concrete, dependency-light implementation of the Company's flagged-but-unbuilt `pattern_cluster`. The k-means itself is trivially portable to any vector source (pgvector, Qdrant, the Company's embedding substrate) — it only needs `(id, vector, document, address)` tuples; swap `col.get(...)` for the Company's bulk-vector read and it runs unchanged. The genuinely reusable assets are: (a) the **interpretation-via-centroid-terms** trick (cluster labels without a model), (b) reproducible seeding, (c) empty-cluster reseeding. **Caveat:** loading *all* vectors into memory doesn't scale to 114k×1024 forever; a production Company version should cap/sample or push the k-means into the store. Treat as a strong reference implementation, not a drop-in.

---

### 4. `traverse_links` / `get_neighborhood` — the graph layer — **OBSERVED**

**How edges are stored (Observed — `db.py:122` `wikilinks`).** Directed edges: `from_address_id → (target_text, target_anchor, alias, is_embed, resolved_address_id, resolution_state, kind)`. Edges are **born unresolved** (`target_text` only); `consolidate` fills `resolved_address_id`. `kind` distinguishes `wikilink` / typed frontmatter channels (`derives-from`, `depends_on`, `supersedes`, …) / `canvas_edge`. Indexed on `from`, `target_text`, `resolved`, and `(kind, from)` for kind-filtered traversal at scale. **An unresolved link is structural-state, not an error** (per the db.py docstring) — dangling references are kept and queryable.

**`traverse_links` (Observed — `server.py:3885`).** BFS over the typed-relation graph. `direction ∈ {out,in,both}`, `depth`, `kinds[]` filter (per-vault discoverable via `get_vault_schema` — *do not assume a kind exists everywhere*). Walk uses `db.wikilinks_from` / `db.wikilinks_to`. Hard safety caps: `max_nodes=50`, `max_edges=250`, with `truncated_at_max_nodes/_edges` flags (a popular foundation file at depth 2 could otherwise reach thousands). `canvas_edge` rows target chunk-anchor addresses and are surfaced separately; `edges_only=True` returns just shape (for later targeted enrichment). `enrich_nodes` attaches title/snippet/status/types per node so the graph isn't bare addresses.

**`get_neighborhood` (Observed — `server.py:2962`).** "An address and its immediate substrate context," same envelope shape for a **file** or a **chunk** address (`kind` tells you which). Returns: outgoing links + backlinks (capped), `siblings_by_type` (peers sharing a non-structural type), `chunks_summary`, optional body, and for canvas chunks the **spatial neighbours** within a pixel radius (`db.spatial_neighbours_in_canvas:877` — Euclidean over `extra_json.{x,y}`). Crucially it ships **`follow_ups`**: pre-computed next tool calls (e.g. "now `traverse_links` from here"), an affordance-surfacing pattern.

**Coupling.** Pure SQLite (+ the JSON `extra_json` for canvas geometry). No Chroma. Portable.

**Harvest-worthiness: MEDIUM.** The Company already has an address/relation graph, so this isn't net-new capability. What's worth harvesting as *design patterns*: (a) **edges born unresolved, resolution as a separate metabolic pass, dangling kept not dropped**; (b) **same envelope for file and chunk addresses**; (c) **bounded traversal with explicit truncation flags** (token-budget-safe MCP responses — directly relevant to Tim's MCP-is-top-priority law); (d) **`follow_ups` pre-computed next-calls** (agent-intuitive surface). Adopt the patterns; the Company's own graph stays the substrate.

---

### 5. `get_type_graph` — the autopoietic type registry (the 2,399-node graph) — **OBSERVED**

**How types are extracted (Observed — `parser.py:969` `extract_types`).** Per file, from frontmatter, register:
- `('markdown-file', 'structural')` always;
- axis types `body/…`, `layer/…`, `face/…`, `status/…` from top-level keys AND from a nested `substrate-position` dict — *only if the value is enum-shaped* (short, not prose; `_is_enum_shaped`);
- every `tags:` entry — a slash tag `domain/cognition` registers as name `domain/cognition` on axis `domain`; a bare tag registers on axis `tag`.

These become rows in `types` (`name UNIQUE, axis, instance_count, state ∈ {proto,working,settled}`) wired to files via the many-to-many `type_assignments`. "**Autopoietic**" = the type vocabulary is **discovered from the content as it's ingested**, not declared up front — every new tag/axis-value combination self-registers as a type. `get_type_graph` (`server.py:3683`) returns the registry paginated, filterable by axis, optionally scoped to a vault (where `instance_count` becomes the per-vault count).

**Coupling.** Pure SQLite. Portable.

**Harvest-worthiness: MEDIUM.** The Company already has a registry-is-truth / field-types architecture, so this overlaps. The harvest-worthy *idea* is **self-registering types discovered from content** (autopoietic vocabulary) with an instance-count and a `proto→working→settled` maturation state — a registry that **grows from observed usage** rather than being hand-declared. That maturation-state idea pairs naturally with the state/temporal layer (Mechanism 2). Adopt the autopoietic + maturation concept; the Company's existing registry is the home.

---

### 6. The chunker (`chunk_target_tokens=600`, `overlap=64`) — **OBSERVED**

**Three-pass chunking (Observed — `parser.py:211` `_chunk`):**
- **Pass 1 — block-id chunks.** Every `^block-id` anchor → a chunk for its enclosing paragraph (double-newline bounded). Anchor = the block-id. These mark regions as `covered`.
- **Pass 2 — heading-bounded sections** not already covered. If a section fits in `target_tokens` → one chunk (anchor = heading slug). Else → **paragraph windows** with overlap (anchor = `slug-pN`).
- **Pass 3 — no-heading fallback.** Paragraph windows over the whole body (anchor = `chunk-N`).
- Sort by `char_start`; dedup by `chunk_address` (block-id wins ties).

**Paragraph windowing (Observed — `parser.py:414` `_paragraph_windows`):** accumulate paragraphs until `target_chars` (≈ `target_tokens × 4`), then **walk back** to create `overlap_chars` overlap with the next window. `_split_oversized` (`parser.py:354`) force-splits degenerate giant blobs (one-line dumps) by lines → whitespace → raw chars so no chunk blows the cap.

**Token estimation (Observed — `parser.py:51` `estimate_tokens`):** **no tokenizer dependency.** Blends 4 chars/token (prose) down toward ~1.8 (dense punctuation/JSON/logs) by the ratio of structural (non-alnum, non-space) chars. Cheap and won't badly undershoot on logs/tool-dumps.

**Provenance / anchoring (Observed — this answers the prompt's explicit question).** Every chunk carries `chunk_address = filesystem://<vault>/<relpath>#<anchor>` where `<anchor>` is a `^block-id`, a heading slug, or `chunk-N`/`slug-pN`. Plus `char_start`/`char_end` (exact offsets into the source), `heading_path` (e.g. `#Part-I/§1-What-this-is`), and `content_hash`. So a chunk is **losslessly addressable back to a byte range in a named file under a named vault.** Re-embed gating uses `content_hash`: `_index_one_file` (`server.py:845`) skips unchanged files by `sha256`; `replace_chunks_for_address` re-derives chunks and the watcher only re-embeds deltas. **Provenance is strong and address-first** — exactly the Company's addressing philosophy.

**Coupling.** Pure Python/stdlib + SQLite. Chunk *text* and all anchors live in SQLite; Chroma only holds the vector + a metadata copy. Portable.

**Harvest-worthiness: MEDIUM-HIGH** *(as reference design).* The Company will chunk transcripts/notes; this is a battle-tested, dependency-free chunker with **first-class provenance** (vault/path/anchor/char-range/content-hash) and **structure-aware anchoring** (block-id > heading > paragraph). The tokenizer-free `estimate_tokens` heuristic is a nice cheap win. Harvest the **address scheme + content-hash delta-gating + structure-aware 3-pass** as the chunking pattern; the exact code is small enough to port directly.

---

### 7. Embedding integration + Chroma storage — **OBSERVED**

**Embedding (Observed — `embeddings.py`).** Two adapters behind `make_embedder`: `OllamaEmbedder` and `OpenAIEmbedder` (OpenAI-compatible `/v1/embeddings`, batches of 64, `trust_env=False` so localhost never gets proxied, **fail-loud** — "a down embedder must never silently degrade to empty vectors"). **Live config uses the OpenAI adapter against `BAAI/bge-m3`** (the prompt's "bge-m3 @ localhost:8001" — note the live `config.json` shows `openai_base_url: null`, so it falls to the adapter default `http://localhost:8001/v1`). This is the same OpenAI-compatible-vLLM shape the Company's own embed service speaks (the adapter comment literally says "e.g. the company embed-bge service").

**Chroma (Observed — `embeddings.py:165` `SubstrateChroma`).** `PersistentClient` at `.state/chroma/`, **one collection per vault** (`vault_<name>`, `hnsw:space=cosine`). `upsert_chunks` embeds in batches and stores `ids=[chunk_id], embeddings, documents=text, metadatas={address,rel_path,vault,anchor_kind,anchor,heading_path,title}`. `query` embeds the query text and returns `{chunk_id, text, metadata, distance}`. The metadata is a **denormalised copy of the address-graph** so retrieval-time filtering (`where=`) works without a SQLite join.

**Harvest-worthiness: LOW for the storage, HIGH for the adapter shape.** The Company already has its own embedding service + vector store, so Chroma itself is not wanted. The reusable bits: (a) the **OpenAI-compatible adapter against the same bge-m3 / vLLM endpoint** — the Company speaks this already, so the embedding *call path* is a near-match; (b) **fail-loud-not-silent-empty** discipline; (c) **denormalised retrieval-metadata** (address + anchors copied alongside the vector) so a hit is self-describing.

---

## Ranking by value-to-the-merge

1. **Temporal / state layer (`state_history` + `find_state_asymmetries` + mtime-bootstrap)** — HIGHEST. The capability the Company most lacks; pure-SQLite metabolism sensor; directly realises temporal-resolution / gap-pressure / introspective-data-building. Small build.
2. **`consolidate` reframed as deferred edge-resolution** — HIGH. The debounced reconcile-references-into-resolved-edges pattern + the multi-strategy resolver ladder + ambiguity-as-state. Realises grounded-chain / registry-filling. *Caveat: the actual semantic-consolidation verb (dedup/merge/prune) is NOT here — net-new.*
3. **`cluster_by_embedding` (`pattern_cluster`)** — MEDIUM-HIGH. Dependency-light k-means + label-by-centroid-terms; the concrete build for the Company's flagged-but-unbuilt clustering. Chroma-coupled but the algorithm is store-agnostic.
4. **Chunker provenance + structure-aware 3-pass + content-hash delta-gating** — MEDIUM-HIGH (reference design). Address-first chunks losslessly anchored to byte ranges; tokenizer-free estimate; re-embed-only-deltas.
5. **Type-graph (autopoietic + maturation state)** / **graph traversal (unresolved-edges-kept, bounded, follow_ups)** — MEDIUM (patterns, not capability — the Company has its own graph/registry).

---

## The Chroma coupling — what a port would require

**The coupling is shallow, and that's the headline.** SQLite is ground truth; Chroma is a rebuildable projection holding `{chunk_id → vector + denormalised metadata copy}`.

- **Mechanisms 1, 2, 4, 5(types), 6 read SQLite only.** Porting them to the Company means re-pointing at the Company's own store/schema — **no Chroma dependency at all.**
- **Only `cluster_by_embedding` (Mechanism 3) touches Chroma**, via one call: `col.get(include=["embeddings","documents","metadatas"])` to bulk-load all vectors. A port swaps that single read for the Company's bulk-vector read (pgvector / Qdrant / the Company embedding substrate) and the NumPy k-means runs unchanged. Caveat already noted: bulk-loading all vectors into memory needs a cap/sample at 114k+ scale.
- **The embedding *call path* is already a near-match** — substrate-mcp's `OpenAIEmbedder` hits the same OpenAI-compatible bge-m3/vLLM endpoint the Company already runs, so re-embedding into the Company's store reuses the same HTTP shape.
- **Net porting cost:** the state/temporal layer and consolidate-as-reconcile are *small, pure-SQL ports* (rebuild the `state_history` table + the change-only-append + the signed-gap query + the mtime bootstrap against the Company's address/relation tables). Clustering is a *moderate* port (one read-adapter swap + a scale cap). The chunker is a *direct code port* (stdlib only). **No part of this requires keeping Chroma**; the corpus would be re-embedded into the Company's own substrate (and per Tim's framing the existing 114k chunks are dormant generated content, so re-embedding fresh is acceptable, not a migration).

**Found-elsewhere ≠ replacement (Tim's law) applies cleanly:** these mechanisms *inform* the Company's metabolism layer. The strongest two (state/temporal + reconcile) are rebuilt natively against the Company's substrate; clustering and the chunker are ported as reference implementations; Chroma and the corpus are left behind.
