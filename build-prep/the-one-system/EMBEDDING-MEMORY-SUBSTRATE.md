# Embedding + memory substrate — the connection map (2026-07-02)

*Tim: "it's connecting more than building — look into recall and recollection, change source address, add what you find to scope." This is the map of what ALREADY exists in the embedding/memory space, the seams to unify, and the addressing reconciliation. recall ≠ recollection (distinct systems). Supabase is the intended shared backend; vectors currently live in FsStore.*

## The pieces that already exist (connect, don't rebuild)

| system | what it is | store | embed | addressing |
|---|---|---|---|---|
| **recall** (`runtime/session_recall.py`, `session_scan.py`, `session_lens.py`; MCP `session_recall`) | INNER, single-session: chunks ONE `.jsonl` transcript, semantic search + drift | per-session **sidecar files** (`<stem>.recall.jsonl` + `.meta.json` next to the transcript) | :8007 pplx + :8008 jina rerank | line/ts/attr within a jsonl |
| **recollection** (`~/recollection`, episodic-memory v1.4.2 fork) | OUTER, cross-session/cross-project memory | *(agent surveying — its own index/DB; .recollection 1.2G)* | :8007 pplx (consumed) | `board://` / `clone://` / `session://` units |
| **corpus / extractions** (`ops/embed_extractions.py`, `runtime/freshness.py`; MCP `corpus`) | the embedded exocortex — session-history + repo, queryable by space | **FsStore** `vectors/` (space-keyed) | pplx (2560) + bge (1024) | `extraction://…`, `code://<path>` (repo space) |
| **scale pyramid** (`runtime/scale.py`; `/api/scale/build`) | MULTI-SCALE up: agglomerative dendrogram → nested rungs (`unit ⊂ fine ⊂ coarse`); "zoom changes which rung resolves" | FsStore (`scale:<space>:k<N>`) | reuses a space's vectors | centroid per cluster |
| **my new code/symbol spaces** (`ops/build_embeddings.py`) | MULTI-SCALE down: file-level + symbol-level code | **FsStore** `vectors/` | nomic-embed-code (3584, via ollama, num_ctx=32768) code; pplx docs | `code://<project>/<path>[::<symbol>]` |

**The substrate is largely built:** multi-model (pplx/bge/nomic), multi-space (extractions/history/repo/topics/code_archaeology/code/symbol), multi-scale (leaf ↕ pyramid rungs), plus a projection engine (`projection.py`: θ=kind, r=time). My work ADDS the code-specialised + symbol-scale leaves and CONNECTS to the rest.

## THE reconciliation: code:// is fragmented THREE ways (the "change source address" work)
1. **Ledger + my spaces:** `code://<project>/<path>::<symbol>` (e.g. `code://company/runtime/suite.py::Suite.foo`)
2. **Corpus S3 surface / `resolve_scope`:** `code://<file-stem>/<symbol>` (e.g. `code://suite/review_verdicts`)
3. **Corpus `repo` space rows:** `code://<path>` (e.g. `code://tests/disposition_acceptance.py`)

These must converge to ONE canonical `code://` so the semantic axis (embeddings), the graph axis (ledger edges), the corpus/recall, and the S3 surface all address the SAME node. **Decision needed (intersects the fabric coordination + Supabase migration):** which form is canonical? Leaning the ledger's `code://<project>/<path>::<symbol>` (it's the most complete — carries project + full path + symbol, and the contract `parse_cap_address`/address grammar already lives there), migrating the corpus/repo + resolve_scope to it. But this is a system-wide change touching the S3 surface, so it must be decided WITH the Glyphic session (coordinating now) since Supabase is the shared store.

## Supabase migration (the shared-backend unification)
Vectors currently persist in FsStore `vectors/` (space-keyed JSON files). Target: Supabase (pgvector). Open schema questions being coordinated with `ch-518m76r0` (Glyphic):
- multi-DIM storage (nomic 3584 vs pplx 2560 vs bge 1024) — pgvector is fixed-dim per column → likely one table per (space,model) or a dim-tagged design.
- columns: canonical source-address, space (scale), emb-layer (model), content_hash (incremental), + the pyramid rungs.

## Added to scope (Tim: "add things you find")
- recall (single-session sidecar) · recollection (cross-session, ~/recollection) · corpus/extractions (FsStore spaces) · scale pyramid (`runtime/scale.py`) · the projection engine · the 3-way code:// address fragmentation · the FsStore→Supabase migration.
- Axis inventory (Tim's list): semantic (embeddings) · graph (edges) · type-registry · file/folder · time · **jsonl-provenance** (the session-turn that generated each node — recall/recollection are this axis) · recall/recollection memory. These compose over one node.

## THE BIGGER FRAME (found via the recollection survey + build-prep/episodic-memory-adaptation/MERGE-INTENTION.md)
My embedding work is ONE part of an already-designed **memory unification**, not a standalone system. The vision (Tim's, documented): **the conversation transcripts (.jsonl) are THE ROOT** — the sole primary-source spine — and *everything generated* (all code, all files = the ledger) re-anchors to its transcript genesis. The connector already exists and is VERIFIED on live data:
- **The provenance join runs now:** `tool_calls.tool_input → file_path` (99.99% of Write/Edit rows) completes `artefact → tool_call → exchange://<sid>/<i> → session → timestamp → parallel-activity`. Live: 75,397 exchanges / 6.72M tool-calls / 7,351 sessions / 96 projects.
- **The grammar is ALREADY ONE:** `contracts/address.py` holds `code:// cap:// exchange:// board:// clone:// session:// vec:// file:// project://` in one SCHEMES registry, one `resolve_address` seam. Not a merge — recollection is already a citizen.
- **Three memory systems to fuse into one store:** ① episodic-memory capture (75k exchanges, sqlite-vec, MiniLM, sidecar) · ② Company corpus (addressed/governed understanding, `exchange://`, but starved: 2,111 records) · ③ consolidation (Chroma). MERGE-INTENTION says: *"almost the entire merge is wiring + volume + activation of pieces that already exist — with exactly ONE genuinely large net-new build (the storage backend)."* That backend = Supabase (Tim's intent).

**So my code/symbol/doc embeddings are the "generated-artefact / what-exists" side; recall+recollection+corpus+the provenance spine are the "genesis / why-and-when" side. Unification = connect the two over the shared grammar, on one Supabase store.** The crossings/provenance builders are BUILT + TESTED but NEVER RUN (`links=0`) — the highest-value connect is nearly free: run them + join to the ledger's code nodes.

## The code:// format reconciliation (precise now)
Not a grammar merge — the grammar is one. It's a FORMAT divergence WITHIN `code://`: the contract declares `code://<file-stem>/<symbol>` (the S3 surface / `resolve_scope` form), but the ledger + my spaces use `code://<project>/<path>::<symbol>`. And the provenance spine addresses artefacts as `file://<abs-path>`. To make a code node, its embedding, its graph edges, AND its generating exchange all address the SAME thing, these need one canonical join (likely: ledger's `code://<project>/<path>` canonical + a `file://`↔`code://` path map for provenance). System-wide (touches S3) → decide with Glyphic + Tim.

## Open / next
- [ ] recollection deep survey (agent) — its store, addressing, Supabase touch, jsonl-provenance link.
- [ ] canonical code:// decision (with Glyphic + Tim) → migrate corpus/repo + resolve_scope.
- [ ] Supabase vector schema (with Glyphic).
- [ ] build the docs space (pplx) — pending.
- [ ] chunk the 4 giant files (suite/bridge/cognition/useAppController) — symbol-scale already covers their functions.
