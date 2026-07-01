---
type: analysis
register: descriptive
status: unconfirmed
coverage: {files_read: 14, files_total: "~30 in scope", last_read: 2026-07-01}
tags: [glyphic-language, live-instrument, corpus, ingest, embed, address-scheme, modes, run_role, bridge-api]
aliases: ["AREA-26 — Company Subsystems the Glyphgraph Relies On"]
---

# AREA-26 — Company Subsystems the Conversational Glyphgraph Relies On

**LENS:** Nothing here is canonical. This is a DESCRIPTIVE map of what the live machinery
*is* and *does*, read in full where the wave demanded depth. Every load-bearing claim is
tagged **Observed (file:line)** or **Inferred**. READ-ONLY pass — `~/company` was not modified
(this findings file is the assigned deliverable, written under the analysis tree, not in the
engine).

This area goes DEEPER than earlier waves on the live machinery and fully maps the
**corpus / ingest / embed / index apparatus** — the answer to "how does Tim's external source
corpus get mined IN." It covers four requested faces:
- **(a)** the corpus/ingest/embed/index apparatus (the headline)
- **(b)** the address-scheme registry + how a new scheme is added additively
- **(c)** modes / run_role / run_swarm / run_items / run_reduce, deeper
- **(d)** the bridge HTTP/SSE API surface a browser consumes

---

## 0. The one-line shape (the relational spine)

> **Walk → Digest → Type → Corpus-Record (cas:// + run:// + event) → Embed-to-Space (vec://) → Query (vector ∥ lexical → RRF fuse → rerank) → Resolve-by-address (one resolver) → serve over the bridge (JSON + SSE).**

Everything below is a leg of that one circuit. The key architectural property to carry into a
glyphgraph design: **there is ONE addressed state and ONE resolver.** Every kind of thing — a
code symbol, a UI element, a session, a board item, a decision, an extraction, a corpus record —
is a row reachable by a typed `scheme://` address, and `resolve_address` is the single seam that
turns any address into content.

---

## (a) THE CORPUS / INGEST / EMBED / INDEX APPARATUS — how a source corpus is mined in

This is the critical area: how external content is ingested, chunked, tagged, embedded, addressed,
and made queryable. The pipeline is **a projection over the existing addressed store, NOT a new DB**
(Observed: `runtime/corpus.py:4-7`, the module docstring — "a PROJECTION over the store, NOT a new DB").

> **EVIDENCE NOTE:** the `runtime/corpus.py`, `contracts/address.py`, `store/vector_index.py`,
> `runtime/cognition.py` (resolve/embed/run_* regions), `runtime/corpus_fusion.py`,
> `runtime/freshness.py`, `runtime/modes_registry.py`, `runtime/relation_types.py`, `fabric/config.py`,
> and the registry dirs were read first-hand (Observed = verified). The `runtime/suite.py` and
> `runtime/bridge.py` line refs were located by Explore sub-agents and then **spot-confirmed
> first-hand** by grep: `ingest_paths@11138`, `capture_corpus@11243`, `query_corpus@11506`,
> `"kind": "capture"@11227`, and the bridge spine `do_GET@1444`/`do_POST@2527`/`BRIDGE_ROUTES@45` all
> matched. The remaining suite/bridge route line numbers are second-hand-but-corroborated.

### A0. TWO ingest DOORS (the fork that answers "how does an EXTERNAL corpus enter?")

There are **two distinct ingest paths**, and which one an external source corpus uses matters:

1. **`ingest_paths` → a projection SPACE** (this section, A1–A6). The general file/dir door: walk →
   `repo_digest` role → `corpus.record` → embed into the chosen `projection` space (default `repo`).
   `Suite.capture_corpus_lenses` (Observed: suite.py:11330) is a sibling that ingests under MULTIPLE
   lenses at once (suite.py:11474 also writes `kind:"capture"`). This is the door for code/doc dirs.
2. **The DRAGNET extract-bake → the `extractions` space** (Observed: `runtime/freshness.py:78-95`
   `extractions_corpus`/`reconcile_extractions`; the `extraction://` resolver, cognition.py:1376-1397).
   The `extractions` space is the **main recall corpus**; it is populated by a separate bake
   (`ops/embed_extractions.build_records`) producing the rich superset records (about/kind/touches/
   summary/entities/claims/relations), and it is the DEFAULT space for `ingest op=reindex`. **Inferred:**
   an external NON-repo document corpus that needs entity/claim/relation extraction plausibly enters
   through this dragnet extract-bake, not through `ingest_paths` (whose digest is a single summary blob).
   The two doors share the SAME vector substrate + the SAME `freshness.reconcile_space` loop.

### A1. The ingest entry point — `Suite.ingest_paths`

**Observed:** `runtime/suite.py:11137`
```python
def ingest_paths(self, *, roots: list | None = None, paths: list | None = None,
                 project: str = "company", session: str = "ingest", round: str = "1",
                 projection: str = "repo", max_files: int = 50, force: bool = False) -> dict
```

**Steps, in order (Observed, suite.py line refs from the ingest-pipeline survey):**

| # | Line | Step | Calls | Produces |
|---|------|------|-------|----------|
| 0 | 11164–11185 | **WALK** the dirs (or load explicit `paths`) | `corpus.walk_files(roots)` | `[{path, text, hash}]` |
| 1 | 11193–11199 | **HASH** each file (full content, not the slice) | `vector_index.content_hash()` | blake2b per file |
| 2 | 11201–11209 | **SKIP-IF-FRESH** (incremental; bypassed by `force=True`) | `list_corpus(project)` + hash compare | stale-only file set |
| 3 | 11218 | **DIGEST-FAN** — map the `repo_digest` role over file units, CONCURRENTLY | `cognition.run_items(rd, units, store, …)` | `{i: digest}` + `failed` |
| 4 | 11225–11227 | **BUILD RECORDS** — assemble corpus records | python dict | `[{source_address, output, kind, projection, source_hash}]` |
| 5 | 11229 | **CAPTURE + EMBED** | `self.capture_corpus(records, …)` | corpus records + vectors |
| 6 | 11236–11240 | **RETURN** addressed URIs + stats | — | `{walked, skipped_existing, digested, captured, failed, remaining, addresses, corpus_total}` |

### A2. The deterministic WALK (Observed: `runtime/corpus.py:258-286`, `walk_files`)

- Produces `[{path, text}]`, **sorted = resume-stable**.
- Skips junk dirs (`WALK_SKIP_DIRS = {__pycache__, .git, node_modules, .venv, .data, dist, build}`,
  corpus.py:249) AND **any hidden `.`-prefixed dir as a CLASS** (corpus.py:273-274 — a hardening
  after `walk(["."])` once returned 13,663 files including venvs).
- `WALK_EXTS = (.py, .md, .ts, .tsx, .js, .jsx, .mjs)` (corpus.py:254 — broadened 2026-06-16 so a
  TS codebase like recollection's 140 `.ts` files is comprehensible; callers can pass a narrower `exts=`).
- `WALK_MAX_CHARS = 6000` (corpus.py:255) — **the per-file slice fed to the digest role is the HEAD,
  not the whole file.** Paths are `os.path.normpath`'d (one-file-one-id law, N5 — `./AGENTS.md` and
  `AGENTS.md` must mint the SAME `code://` id, else the repo double-ingests).

**Glyphgraph implication:** to mine an EXTERNAL source corpus in, you point `ingest_paths` at its
`roots=`/`paths=` and choose a `projection` (the space it lands in). The walk is generic over any
dir; the only assumptions are the extension set and the 6000-char head slice. A large or non-code
corpus would want a different chunker (see A5 — chunking is currently file-head-only).

### A3. How a raw file becomes a TYPED corpus unit (the "tagging / type-registry" leg)

**Observed: `runtime/suite.py:11225-11227`** — the type is set HERE:
```python
records.append({"source_address": f"code://{f['path']}", "output": dig,
                "kind": "capture", "projection": projection,
                "source_hash": f["hash"]})
```
- **`source_address`** = `code://<normalized-path>` — the retrieval KEY (the address the record is
  keyed by). Inferred: for a non-code corpus this would still be `code://<path>`; the scheme is the
  address label, not a content-type claim.
- **`kind`** = the literal `"capture"` for an ingest digest. The `kind` axis is OPEN: corpus.py
  documents `'capture'/'reduce'/'lift'` as record kinds (corpus.py:149).
- **`projection`** = the LENS (the vector space the digest embeds into) — defaults to `"repo"`.
- **TYPING LIMIT (honest caveat — not fully traced):** the corpus *digest* record's type is JUST the
  `kind` string (`"capture"`) plus the `projection` lens. The other type registries are a DIFFERENT
  axis and were confirmed first-hand to NOT govern corpus digests: `contracts/node_type.py` (Observed:
  process/content/presentation GRAPH-node kinds, C2) types canvas nodes; `item_types/` (Observed:
  artefact/block/document/idea/issue/message/note/request/signal/tip) types BOARD items;
  `source_types/` (Observed: `claude_code.py`) types provenance sources. The RICH per-unit typing
  (entities/claims/relations) is the DRAGNET extraction superset reached via `extraction://`
  (cognition.py:1376-1397) — see A0 door 2 and A8 — **not** the plain digest. How a `code://` corpus
  unit would carry a `node_type`/`item_type` was not traced; **Inferred** it does not — the digest's
  only type surface is `kind`+`projection`. (Flagged honestly: the task's "type-registry integration"
  sub-point is resolved as "the digest is lightly typed; rich typing is the dragnet's job," not deeper.)

**The digest model run (Observed):** the digest is produced by the **`repo_digest` role**
(`roles/repo_digest`, discovered via `role_registry.get("repo_digest")`, suite.py:11160). Each unit's
input is `"FILE <path>:\n\n<first-6000-chars>"` (suite.py:11217). The fan is `cognition.run_items`
(1 role × N units, concurrent) — so the digest is a real per-file model pass, not a mechanical slice.

### A4. CAPTURE + persist + EMBED — `capture_corpus` (Observed: `runtime/suite.py:11242-11320`)

1. **Lineage gate** (suite.py:11282): `session/round/project` are REQUIRED; missing → RAISES.
   This is the **sequencing gate** (corpus.py:8-15, 97-119, `_validate_lineage`): a record without
   `session/round/project` is uncorroboratable cross-session, so it is refused at write — never a
   silent default. **This matters for a glyphgraph:** every captured unit carries WHICH run/round/project
   minted it, from the start.
2. **`corpus.write_record`** FIRST (suite.py:11292 → corpus.py:122): persists the record to
   **`cas://`** (write-once immutable, resume-safe — same record → same hash), sets a deterministic
   **`run://corpus/<project>/<source_address>[/<projection>]`** pointer (corpus.py:84-94,
   `corpus_address`), and emits a durable **`corpus.record`** event on the one event log (corpus.py:76,
   178-193). The log IS the index — `list_corpus`/`find_corpus` are read-time projections over
   `events_since(-1)` filtered to `kind=="corpus.record"`, dedup-on-read by address (corpus.py:208-242).
3. **`cognition.embed_corpus_to_spaces`** SECOND (suite.py:11318 → cognition.py:667).

### A5. The EMBED orchestration (Observed: `runtime/cognition.py:667-732`, `embed_corpus_to_spaces`)

- Takes `records = [{source_address, text, projection}]`; groups by projection; one
  `vector_index.build_index(store, [...], space=projection)` call per space.
- **REFUSES** a record whose `projection` is not in `projection_registry.embeddable()`
  (cognition.py:713-718) — registry-is-truth, fail-loud, never a silent drop. Only a lens declared
  `embeds: True` (GROUP L) may become a space.
- Returns `{spaces: {<proj>: {embedded, skipped, degraded}}, records: N, degraded: bool}`.

### A6. The persisted vector index (Observed: `store/vector_index.py`, read IN FULL)

This is the heart of "made queryable." Three functions:

- **`build_index(store, corpus, *, space=None, emb="__default__", …)`** (vector_index.py:64-140):
  - **CONTENT-HASH INCREMENTAL**: re-embeds an address ONLY when NEW or its blake2b `content_hash`
    CHANGED (lines 100-109). An all-unchanged rebuild embeds NOTHING and touches the endpoint ZERO
    times (lines 111-114) — so no spurious "embedder down" warning.
  - **EMBED PATH (reuse, no parallel)**: `fabric.transport.openai_embeddings_transport` +
    `fabric.client.complete_embeddings` (lines 56-61, 116-120) — the EXACT path `nodes/embed.py` uses.
    `dim=` enforced at the fabric → a wrong-length vector FAILS LOUD, never a silent bad cosine.
  - **SPACE-KEYED** (lines 74-80): `space=None` = the default/unspaced index keyed by the bare item
    address (back-compat). A named `space="<projection>"` is keyed by the composed address
    **`vec://<item>#space=<proj>[#emb=<layer>]`** (`store.space_address`). The SAME item embedded at a
    different lens is an independent entry — so an item is cross-space distinguishable by its different
    neighbours (this is the substrate for "a glyph means a FIELD, not a single thing").
  - **DEGRADE-WITH-WARNING** (lines 82-85, 121-133): embedder unreachable → NO vectors written, a LOUD
    durable `warning` event, `degraded: True`, no crash. NEVER a fabricated/zero vector.
  - Persists via `store.put_vector(key, vec, content_hash, dim, model, space, source, emb)`.

- **`query_index(store, query_vector, *, k=5, space=None, emb, with_note, records)`**
  (vector_index.py:143-218):
  - **Fast path** (lines 170-190): a cached per-space numpy matrix → cosine via ONE matmul
    (`store.space_matrix`), ranking-identical to the reuse path. Falls back to `nodes/retrieve` on any
    edge (dim-mismatch / zero-vector) — fail-loud preserved.
  - **Reuse path** (lines 191-195): `store.index_corpus(space=, emb=)` → `nodes.retrieve.run(...)`
    (the cosine is NOT reimplemented; its `_cosine` raises on a dim mismatch).
  - **SPACE filter** (lines 148-154): `space=None` ranks the default index (a spaced entry never leaks
    in); `space="<proj>"` restricts the k-NN to that ONE space; `FsStore.ALL_SPACES` ranks every entry.
  - **HONEST EMPTY + WEAK-MATCH note** (lines 196-218): an empty index returns `{ranked: [], note: …}`
    so callers distinguish "index empty (embedder was down)" from "populated, no match." A top-1 cosine
    `< 0.33` is flagged "★ WEAK top match … likely off-topic" — cosine always returns top-k, so it
    SURFACES low confidence rather than filtering (rerank is the decisive gate, line 211-217).

- **`index_staleness(store, corpus, *, space, emb)`** (vector_index.py:221-283): READ-ONLY — embeds
  nothing, touches no network. Compares content_hashes → `{fresh, missing, changed, extra, counts}`.
  The interrogation primitive the freshness loop reads.

### A7. The freshness / auto-reindex loop (Observed: `runtime/freshness.py`, read IN FULL)

The gap it closes (freshness.py:1-7): the bridge's vector-cache daemon only WARMED existing vectors;
nothing auto-reindexed when source content changed.

- **`reconcile_space(store, space, corpus, *, retract_extra=True)`** (freshness.py:22-75): the COMPLETE
  loop — `index_staleness` (read-only) → embed missing+changed via `embed_corpus_to_spaces` (O(changed),
  not O(corpus)) → RETRACT orphaned index keys via `store.remove_vectors` → re-check staleness. Honest
  report `{space, fresh_before, embedded, retracted, degraded, fresh_after, counts}`. A degraded build
  (embedder down) writes 0 and SAYS SO (line 61-65), never a phantom write.
- **`reconcile_extractions(store, emb="pplx")`** (freshness.py:90-95): the high-value default — reconcile
  the `extractions` space against its live asset files (`ops.embed_extractions.build_records`).
- **Inferred (from memory + the survey):** the bridge runs an auto-freshness daemon (`bridge.py`
  `_freshness_loop` / `_warm_vector_cache`) that mtime-polls and calls `reconcile_extractions`.

### A8. The QUERY / consult / hybrid retrieval side (the read-back half)

- **`Suite.query_corpus(text, *, space=None, k=8)`** (Observed: suite.py:11505-11521): embed the query
  (`_embed_consult_query` → `complete_embeddings`; embedder down → honest empty) → `query_index(space=,
  with_note=True)`. Returns `{query, space, ranked: [{address, score}], note?}`.
- **`consult()`** (suite.py:5297+): system Q&A — semantic retrieve, then a PRECISION rerank stage
  `corpus_rerank.rerank_hits()` (jina-v3 @ :8008), degrade-honest; keyword fallback if semantic empty;
  then an LLM answer with citations.
- **`corpus_rerank`** (`runtime/corpus_rerank.py`): the cross-encoder precision stage over the top-k.
  Law it carries (quoted in corpus_fusion.py:12-14): *"when fusion comes, it is LATE FUSION ONLY (RRF /
  score-blend over ranked LISTS) — bge-1024 and pplx-2560 are different models/dims; NEVER
  concat/avg/cosine across them."*
- **`corpus_fusion.query_hybrid(suite, text, *, space, k)`** (Observed: `runtime/corpus_fusion.py`,
  read IN FULL):
  - **VECTOR leg** = `suite.query_corpus` (meaning; needs embedder up).
  - **LEXICAL leg** = `lexical_leg(store, text, space)` (corpus_fusion.py:75-116): ONE event-log scan
    of the space's digests (`corpus.find_corpus(projection=space)`), resolving each row's digest text
    from the `cas` it already carries, scored by a term-count algorithm lifted from `session_search`.
    Capped at `LEX_SCAN_CAP=5000`. **The id is the BARE `source_address`** — the SAME shape the vector
    leg returns, so RRF fuses on a COMMON key (the fusion-correctness pivot, corpus_fusion.py:82-86).
  - **FUSE** = `rrf_fuse` (corpus_fusion.py:119-146): Reciprocal-Rank Fusion — `Σ_leg weight/(rrf_k +
    rank)`, `DEFAULT_RRF_K=60`. Uses RANK only, never raw scores (sidesteps the bge-1024 vs pplx-2560
    scale mismatch). An item ranked decently in BOTH legs beats a #1 in only one (consensus wins).
  - **DEGRADE-HONEST** (corpus_fusion.py:31-33, 158-191): embedder down → vector leg empty → fusion runs
    lexical-only and `legs_used=['lexical']` SAYS SO. Never a silent lexical-only-as-hybrid.
  - **Inferred (per memory note):** hybrid fusion is PURE-MATH verified; end-to-end is held pending the
    embedder. The math layer is real and self-testable (corpus_fusion.py:195-212 `__main__` self-test).
- **`corpus_neighbours.neighbours()`** (`runtime/corpus_neighbours.py`): recall-under-a-unit — the
  relational node-field that DNA's "constellation" data reads (the glyphgraph's neighbour edges).
- **`find_relations`** (cognition.py, GROUP L2 — "the inversion-finder"): `query_index(near) ∩
  ¬query_index(far)`, labelled with a declared **relation-type** (see (c)/§relation_types). This is the
  cross-level TYPED-EDGE machinery a glyphgraph would draw from.

### A9. The embedder model + dims + endpoint (Observed: `fabric/config.py:39-66`)

**The live embedder is NOT bge-m3/1024 (an earlier-wave assumption) — it is:**
```python
DEFAULT_EMBED_URL   = COMPANY_EMBED_URL   or "http://localhost:8007/v1"   # :8007, not :8001
DEFAULT_EMBED_MODEL = COMPANY_EMBED_MODEL or "perplexity-ai/pplx-embed-context-v1-4b"
DEFAULT_EMBED_DIM   = COMPANY_EMBED_DIM   or 2560
DEFAULT_EMB_LAYER   = COMPANY_EMB_LAYER   or "pplx"
EMB_LAYER_DEFAULT   = "__default__"   # sentinel: caller omitted emb -> use DEFAULT_EMB_LAYER
```
`resolve_emb_layer(emb)` (config.py:59-66): `__default__` → `pplx` (the write+read layer); an explicit
`None`/`'bge'` → the bare/legacy layer. **The `emb` (embedder LAYER) is a real axis** — the index can
hold the SAME item under multiple embedders (`…#space=<proj>#emb=<layer>`), and read-layer must match
write-layer or every item reads as missing (vector_index.py:266-270). (Code comments still mention
`:8001`/`bge-1024` as historical/multi-layer context; the live default per config.py is pplx-2560 @ :8007.)

### A10. The embeddable SPACES (the corpus lenses) — registry-is-truth

**Observed: `projections/` dir** + `embeds` flags. The projection registry
(`runtime/projections.py`, `ProjectionRegistry.embeddable()` at line 244 → `embeds==True`):

| projection file | `embeds` | role |
|---|---|---|
| `repo.py` | True | the codebase exocortex space (ingest default) |
| `extractions.py` | True | the dragnet extraction space (main recall corpus) |
| `history.py` | True | cross-session discussion records |
| `worldview.py` | True | meaning-level worldview space |
| `operators.py` | True | (operators lens) |
| `common_knowledge.py` | (True per note) | comprehended content (recollection chroma parallel) |
| `principles.py` / `topics.py` | (spaces) | principle / topic spaces |
| `lineage.py` | False | provenance lens — does NOT embed |
| `what.py` | False | does NOT embed |
| `claimed_status.py`, `code_archaeology.py` | — | other lenses |

**Add a corpus space = drop a `projections/<id>.py` declaring `embeds: True`** (no code edit). This is
how a new external-corpus lens is introduced.

---

## (b) THE ADDRESS-SCHEME REGISTRY + adding a new scheme additively

### B1. The registry (Observed: `contracts/address.py:145`)
```python
SCHEMES = ("run", "cas", "blob", "vec", "ui", "code", "skill", "context", "guide",
           "session", "cap", "board", "clone", "mind", "exchange", "file", "project",
           "vi-vision", "decision", "image", "extraction")
```
`scheme(addr)` (address.py:164-168) returns the matching scheme prefix or None. The grammar is documented
exhaustively in the module docstring (address.py:1-141) — each scheme has a note explaining its resolver
home and that adding it was "purely additive, no `schema_ver` change."

### B2. The resolver — ONE seam (Observed: `runtime/cognition.py:1129-1415`, `resolve_address`, read IN FULL)

`resolve_address(store, addr, *, turn_id, on_missing)` is the EXTENSIBLE SEAM. Path:
1. **Materialize** `<turn>` template → `turn_id` first (raises if a `<turn>` template has no turn_id).
2. **Dispatch by `scheme(addr)`** to the per-scheme resolver:
   - `run://` → `resolve_run_ref` (head→get_content)
   - `cas://` → `store.get_content`
   - `blob://` → `store.get_blob` (binary)
   - `image://` → `cc_images.get_image`
   - `skill://`/`context://`/`guide://` → the file-discovered `SkillRegistry`/`ContextRegistry`/`GuideRegistry.read(id)`
   - `session://` → `store.load_agent_session` (+ `session://<sid>/step/<tool_use_id>` resolves a tool-call STEP from the transcript)
   - `cap://` → the cached `capability_registry()` singleton
   - `board://` → `cc_board.get_item`; `clone://` → `cc_clone.get_by_address`; `mind://` → `minds.resolve_mind`
   - `vi-vision://` → `vi_vision.resolve_vi_vision`
   - `decision://` → `decision_registry` row COMPOSED with its resolved take-state (from marks)
   - `extraction://` → `recall_determine.read_extraction` (the dragnet read leg)
3. A **registered scheme with no resolver yet** (`vec`, `ui`, `code`, `exchange`, `file`, `project`) →
   **RAISES fail-loud** ("not content-resolvable yet … add a `<scheme>://` resolver branch here").
4. An **unregistered scheme** (`foo://`) → RAISES. A **bare name** (no `://`) → `BARE_NAME` sentinel
   (the caller reads it from ctx).

### B3. The additive recipe (the exact "how to add a scheme")

From the resolver code + the docstring notes, adding a new scheme is THREE additive moves, none breaking:
1. **Append the scheme string to `SCHEMES`** (contracts/address.py:145) — purely additive, no `schema_ver`.
2. **(Optional) declare a `parse_<x>_address` grammar** in `contracts/address.py` (the "one grammar home"
   pattern — `parse_session_address`, `parse_clone_address`, `parse_decision_address`, `parse_cap_address`,
   `parse_image_address` all live there, declared once, shared by resolver + writers).
3. **Add ONE `if sch == "<x>":` dispatch branch** in `resolve_address` (cognition.py) — typically a LAZY
   import of the scheme's registry module + a fail-loud-on-unknown read (mirrors `board://`/`clone://`).

There is also a **register-but-defer** intermediate state: a scheme can be in `SCHEMES` (grammar-legal)
while its resolver lives in another lane and still RAISES at `resolve_address` (e.g. `exchange://`,
`file://`, `project://` — recollection's lane owns them). The seam is "declared, not faked."

There is a **general cross-scheme version axis** too: `<addr>@v<n>` (`split_version`/`versioned_address`,
address.py:402-424) — ordinal content versions on ANY addressed content.

**Glyphgraph implication:** a "glyphic address" is exactly this — a new `scheme://` row + a resolver
branch. If the glyphgraph needs its own node identity (e.g. a glyph node), it joins the ONE addressed
state additively, the same way `decision://` and `extraction://` did.

---

## (c) MODES / run_role / run_swarm / run_items / run_reduce — deeper

### C1. The presence-MODE registry (Observed: `runtime/modes_registry.py`, read IN FULL + `modes/`)

- Modes were the LAST hardcoded dict (`MODE_REGISTRY={…}` in suite.py); now an OPEN, file-discovered
  registry — one `modes/<id>.py` declaring a module-level `MODE` dict (modes_registry.py:1-21).
- **`discover_modes(dirs)`** (modes_registry.py:61-86): `os.listdir`→importlib, fail-loud on
  malformed/duplicate, sorted by `(order, id)` (modes are ORDER-BEARING). `order` is stripped from the
  returned decl (byte-for-byte the literal entry).
- **Schema** (modes_registry.py:30-32): REQUIRED = `label, directive, resolution, consent, grain, shape,
  stage, live, reserve_r, per_role_ctx, main_ctx_tokens, brain_config`; OPTIONAL = `subtypes,
  loadout_class, voice`.
- **The modes** (Observed `modes/` dir): `listening`, `text-only`, `background`, `focus`, `walkthrough`,
  `watch-and-react`, `decide-for-me`, `off`. Example (`modes/listening.py`): `directive: 'Conversational
  and present; respond fully'`, `consent: 'offer'`, `grain: 'beat'`, `shape: 'linear-stream'`,
  `brain_config: 'voice-64k'`, `loadout_class: 'interaction'`, `voice: 'on'`.
- A mode carries the **RESOLUTION** (how deep to answer), **CONSENT** (offer/auto), **GRAIN/SHAPE**
  (beat / linear-stream), and the **BRAIN loadout** — i.e. the presence mode is the dial that shapes how
  the conversational surface behaves. **Add/edit a mode = drop/edit a file, no code edit.**

### C2. `run_role` — fire ONE request, the two axes (Observed: `runtime/cognition.py:313-427`)

- Returns the role's VALIDATED JSON output DIRECTLY (the `{output, address}` nesting exists ONLY on the
  MCP face — cognition.py:319-326; "false 0-findings twice" warning).
- **THE TWO AXES:**
  - **INPUT axis** — `role.input_addresses` (declared). Default (`["utterance"]`) is byte-identical:
    `ctx["utterance"]` framed as `"Utterance: …"`. Other declared inputs resolve per-name via
    `resolve_address` (a `run://` name needs `store=`) and compose as labelled lines.
  - **OP axis** — `role.op`: default `"generate"` (complete + output_schema + json); **`"embed"`**
    (cognition.py:408-427) → `complete_embeddings` against the LOCAL embedder
    (`DEFAULT_EMBED_URL`/`DEFAULT_EMBED_MODEL`/`DEFAULT_EMBED_DIM`), returns `{vector, dim, model}`.
- **Resident-brain sentinel** (cognition.py:401-406): `RESIDENT_BASE_URL`/`RESIDENT_MODEL` resolve to the
  ACTIVELY-loaded brain via `active_brain()` — the whole cognition layer follows the live loadout (the
  SAME brain the RHM uses, never a dead pinned port). An explicitly-passed base_url/model is verbatim.
- **#50 ensure-resident** (opt-in `ensure=`): a deliberate caller can make the embedder resident via the
  gated capability before an embed-op; default keeps fail-loud-when-down.
- **Generation policy ladder** (opt-in `policy=`): a rep-penalty escalation regime from the
  `generation_policies/` registry (flagged: the transport passthrough of `repetition_penalty` is a
  cross-lane follow-up, not yet wired to vLLM — cognition.py:365-372).
- **Resolved-slots** (`prompt_slot`/`schema_slot`, cognition.py:439-462): one role's prompt+schema can
  RESOLVE per turn `coordinate` (grain·viewer·mode·subtype·register) instead of being static.

### C3. `run_swarm` — N roles, concurrent wave (Observed: `runtime/cognition.py:1442-…`)
```python
def run_swarm(roles, ctx, store, *, turn_id, budget=None, emit=None,
              base_url=RESIDENT_BASE_URL, model=RESIDENT_MODEL, max_tokens=256) -> WaveResult
```
Dispatches a WAVE of independent role-runs CONCURRENTLY (C1.1), bounded by the registry SLOT budget
(C1.2). Each role writes its validated JSON to its own `run://<turn>/<role>` address; JOIN at a barrier;
read back via the canonical resolver. `WaveResult` (cognition.py:1429-1439) carries `resolved` (role_id →
value), `addresses`, `runs` (per-role RoleRun records), `finish_order` (nondeterministic), `wall_s`,
`sum_role_s`. The determinism discipline: downstream rules read only FULLY-resolved address values from a
declared whitelist, so finish-order never changes the result (cognition.py:735-786, the injection rule).

### C4. `run_items` — 1 role × N units (the MAP) (Observed: `runtime/cognition.py:1590-…`)
The axis-inversion of run_swarm. Each unit is EITHER an address (`run://`/`cas://`, resolved) OR a literal,
placed at `ctx["utterance"]`; fired concurrently (same pool + VramGate + barrier); written to
`run://<turn>/<role>/<i>`. **F2 PER-UNIT RESILIENCE** (cognition.py:1621-1635): a resolution failure under
`on_missing="raise"` fails the whole fan (address contract); a processing failure (resolved but run_role
raised) goes to `.failed` and the GOOD units STILL return — the batch is not all-or-nothing. This is the
DIGEST-FAN ingest uses (A1 step 3).

### C5. `run_reduce` — N→1 JOIN (Observed: `runtime/cognition.py:2389-…`)
Reads N map-output `run://` addresses back, applies ONE declared `mode`:
- **`mode="role"`** — a reduce/synthesize role (op=generate) composes the N outputs into one input.
- **`mode="rule"`** — a deterministic PURE callable (vote/merge/select), no model, replay-identical.
- **`mode="cluster"`** — embed each unit's text (op=embed) + GROUP by cosine-nearness (reuse
  `nodes/retrieve._cosine`) → clusters of near-duplicates (the "which of these are the same" join);
  `embed_fn` injectable for embedder-down. Deterministic given vectors.

**The map/reduce/swarm trio is the dataflow backbone** — note the floor: these are DRIVERS, they emit no
resolve/approve/dispatch (the operator-only floor). A glyphgraph that wants to compute over many nodes
composes these, it does not build a parallel engine.

### C6. The relation-type registry (Observed: `runtime/relation_types.py`, read IN FULL + `relation_types/`)
A file-discovered registry of TYPED, DIRECTIONAL edge kinds between corpus units — the vocabulary
`find_relations` labels its discovered edges with. **The dir** (Observed): `contradicts`, `depends_on`,
`fragment_of`, `precedes`, `principle_beneath`, `sibling`. Schema (relation_types.py:62-63): REQUIRED
`id` (==filename) + `directed` (bool — one end or both); OPTIONAL `inverse`, `near`/`far` (the spaces the
inversion-finder set-operates over), `label`, `desc`. **Add an edge kind = drop a
`relation_types/<id>.py`.** This is the typed-edge vocabulary a glyphgraph's relationships would draw from
(edges are NOT verbs — they are declared relation-types with direction + the spaces they're computed over).

---

## (d) THE BRIDGE HTTP / SSE API SURFACE a browser consumes (Observed: `runtime/bridge.py`)

A thin synchronous JSON layer over the shared `Suite`. **Dispatch (Observed):** exact-string match on
`urlparse(self.path).path` in `do_GET` (bridge.py:1444) and `do_POST` (bridge.py:2527) — no router
framework; a single-source `BRIDGE_ROUTES` tuple (bridge.py:45-140) is drift-checked by
`tests/bridge_routes_acceptance.py`. `/api/image/` is the one prefix route.

### D1. Streaming / SSE (what a live glyphgraph subscribes to)
| Method | Path | Handler | file:line |
|---|---|---|---|
| GET | `/api/stream` | `_stream(q)` — SSE, tails the shared `events.jsonl`; cursor via `?since=` / `Last-Event-ID`; ~15s heartbeat; `text/event-stream` | bridge.py:1449-1451 |
| POST | `/api/chat/stream` | `_chat_stream` — text-only turn, NDJSON `{type:part}`/`{done}`/`{error}` | bridge.py:2946-2950 (impl 2153-2256) |
| POST | `/api/voice/stream` | `_voice_stream` — streaming voice turn, sentence-by-sentence NDJSON | bridge.py:2943-2945 |
| POST | `/api/voice/turn` | single live turn (hear→think→speak), non-streaming | bridge.py:2870-2888 |

### D2. Corpus / ingest / recall / embed / cognition
| Method | Path | Purpose | file:line |
|---|---|---|---|
| POST | `/api/cognition/corpus` | D1 CAPTURE — persist + embed-on-write | bridge.py:854-887 |
| GET | `/api/cognition/corpus` | D5 — discovered corpus records (list/read) | bridge.py:2055 |
| POST | `/api/cognition/embed` | fire an embed-op role → `{vector, dim, model}` | bridge.py:844-853 |
| GET | `/api/corpus-query` | S7 — the forager's semantic+heads search door | bridge.py:1775 |
| GET | `/api/cognition/neighbours` | neighbour node-field (DNA constellation data) | bridge.py:2070 |
| GET | `/api/cognition/find_relations` | L2 inversion-finder (near ∩ ¬far) | bridge.py:2046-2054 |
| GET | `/api/session-recall` | per-session recall lens | bridge.py:1668 |
| GET | `/api/transcript-search` | semantic search over recollection backend | bridge.py:1646 |
| GET | `/api/layers` / `/api/layer-dims` | the embedder-layer self-description (MRL ladder) | bridge.py:1730/1732 |

(Note: the OPERATOR-facing corpus/ingest entry the survey found is the MCP face —
`mcp_face/tools/corpus.py` `corpus(op=query|list|find|read|neighbours|determine)` and
`mcp_face/tools/ingest.py` `ingest(op=ingest|reindex)`. The bridge routes above are the BROWSER face.)

### D3. Resolve / address / inspect (the one-resolver door, browser-facing)
| Method | Path | Purpose | file:line |
|---|---|---|---|
| POST | `/api/resolve` | THE RESOLVER door (4th-primitive seam) — pure computation | bridge.py:252-430 |
| GET | `/api/scope` | S3 — `ui://→code://→scope[]` (address→code join) | bridge.py:1847 |
| GET | `/api/context` | R2 — addressed-context inspector | bridge.py:1892 |
| GET | `/api/territory` / `/api/territory/label` | structured territory read / human aim-label (NEVER the raw address — operator law) | bridge.py:1866/1859 |
| GET | `/api/address-history` | everything that happened AT a `ui://` address | bridge.py:1939 |
| GET | `/api/address-help` | composed affordance bundle for one address | bridge.py:1849 |

### D4. Cognition / chat / conversation (what the conversational surface posts to)
| Method | Path | Purpose | file:line |
|---|---|---|---|
| POST | `/api/chat` | the right-hand-man — grounded conversation (sync) | bridge.py:475-480 |
| GET | `/api/chat` / `/api/conversations` / `/api/conversation` | read chat / list threads / reopen one | bridge.py:1799/1801/1803 |
| POST | `/api/conversation/new` | start a fresh conversation (becomes current) | bridge.py:497-499 |
| POST | `/api/cognition/run_role` | fire ONE role → `run://` output | bridge.py:825-831 |
| POST | `/api/cognition/run_items` | the MAP — fan a role over N units | bridge.py:832-836 |
| POST | `/api/cognition/run_reduce` | the JOIN — reduce N addresses → one | bridge.py:837-843 |
| POST | `/api/cognition/preview_turn` | preview a staged turn (read-only) | bridge.py:814-824 |
| GET | `/api/cognition/inputs` | the addresses a role/rule can read (authoring) | bridge.py:2029 |
| GET | `/api/graph` / `/api/graphs` | the addressed graph(s) (C4) | bridge.py:1534/1536 |
| POST | `/api/node` / `/api/connect` / `/api/delete-node` / `/api/move` / `/api/set` | mutate the addressed graph | bridge.py:442/448/453/436/431 |
| GET | `/api/tools` · POST `/api/tools/invoke` | the interactive MCP tool list + generic invoke door | bridge.py:2090/957 |

(Fuller route inventory — decisions, RHM/voice/model config, fabric/channels/sessions, review/journey,
inbox, introspection — exists in bridge.py and was catalogued; the above are the routes a conversational
glyphgraph most directly consumes.)

---

## SUMMARY (3 lines)
- **Corpus mining-in is a projection over the ONE addressed store, not a new DB:** `ingest_paths` →
  walk (corpus.py, 6000-char head slice) → `repo_digest` role fan (run_items) → typed `corpus.record`
  (cas:// + run:// + event, lineage-gated) → `embed_corpus_to_spaces` → `vector_index.build_index`
  (incremental, space-keyed `vec://<item>#space=<proj>#emb=<layer>`, pplx-2560 @ :8007); query is
  vector ∥ lexical → RRF fuse → jina rerank, with an `index_staleness`/`freshness.reconcile_space`
  auto-reindex loop.
- **One scheme registry + one resolver:** `contracts/address.py:SCHEMES` (21 schemes) + the single
  `cognition.resolve_address` dispatch; adding a scheme is the additive 3-move recipe (append to SCHEMES,
  optionally declare `parse_<x>_address`, add one lazy-import resolver branch) — exactly how a glyph
  identity would join the addressed state. Modes, projections (spaces), and relation-types are all
  file-discovered registries (drop a file, no code edit). run_role/run_swarm/run_items/run_reduce are the
  concurrent map/reduce dataflow backbone (drivers, not agents).
- **Path:** `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-26-company-subsystems-corpus.md`
