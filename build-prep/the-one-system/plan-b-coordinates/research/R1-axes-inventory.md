# Plan B research · R1 — the complete axes inventory (live-DB verified, 2026-07-02)

*Every axis of the coordinate space: where it lives, size, queryability, gaps, join keys. Produced by a
research agent (all counts executed live); report verbatim below. Companion: R2-query-patterns.md.*

RESEARCH COMPLETE — all counts run live against Supabase :15432 on 2026-07-02. Everything below is **Observed** (executed queries / read files) unless tagged *Inferred*.

# THE COMPLETE AXES INVENTORY — multi-axis coordinate query over the unified ledger

**Substrate:** schema `ledger` = 6 tables (`run`, `entry`, `edge`, `embedding`, `symbol`, `coverage_findings`) + 5 views (`latest_run`, `entry_latest`, `edge_latest`, `symbol_latest`, `coverage`). 18 runs. **Zero Postgres functions/RPCs exist in the ledger schema** — the "one query function" does not exist yet in any form.

**The one structural disease that cuts across every axis:** the `*_latest` views pick ONE run per `(project, purpose)` (`latest_run` = `DISTINCT ON ... ORDER BY started_at DESC`). Every fresh deterministic snapshot creates a NEW run, so anything enriched into an older run — interpretations, `generated-by` edges, git `file_meta` — is **stranded invisible** below the latest views.

---

## Axis 1 — GRAPH (`ledger.edge` / `edge_latest`)

- **Lives:** `ledger.edge` (720,461 rows all-runs) → `ledger.edge_latest` (74,230 rows). Columns: `from_ref, kind, to_raw, to_resolved, line, extra, run_id, extracted_at`.
- **Kinds in edge_latest (with resolution rates):** calls 49,468 (29.6%), contains 13,855 (92.5%), imports 5,450 (25.4%), references 3,398 (0.1%!), capability-of 487 (100%), **powered-by 359 (100%)**, subscribes-event 313 (16.6%), extends 219 (1.4%), serves-endpoint 186 (0%), **binds-ui 172 (100%)**, emits-event 156 (0%), calls-endpoint 155 (60%), on-axis 10, uses-capability 2.
- **CRITICAL:** `generated-by` (1,403 rows) is **NOT in edge_latest at all** — it lives only in superseded run `c7522773` (Jul 1 13:53); the latest company run is `390286ec` (Jul 2 05:39). Same fate for 30 more organic kinds in the raw table (in_channel 1,109, authored_by 540, relates-to 438, launched-by, indexed-by, …).
- **Key form:** `from_ref`/`to_resolved` are addresses (`code://company/<path>`, `code://…::<symbol>`, `ui://…`, `cap://…`). `to_raw` is the unresolved token.
- **Queryable today:** kind-filtered traversal, indexed on from/to. **Missing:** an FK/join to `entry` is by address-string only (no entry_id on edges); resolution rates for calls/imports/references are the known weak extractor; ui→code join = powered-by 359 + binds-ui 172 + 553 references touching ui:// (the ② dependency).
- **Join path:** `edge.from_ref / to_resolved = entry.address = embedding.source_address` — the address string IS the join key everywhere.

## Axis 2 — VECTORS (`ledger.embedding`)

- **Lives:** one table, 76,196 rows; per-dim halfvec columns `vec_3584 / vec_2560 / vec_1024` + `vec_any` (157 test rows); unique key `(source_address, space, emb_layer)`.
- **Real spaces × layers:** extractions/pplx/2560 = 51,600 (`extraction://full/<n>`); exchange/pplx = 6,983 (`exchange://<sid>/<i>`); symbol/nomic-code/3584 = 6,201 (`code://…::<sym>`); code_archaeology/pplx = 2,900; history/pplx+bge = 1,464×2 (`exchange://` + `deferred://` + `memory://` sources); desc/pplx = 1,043; code/nomic = 1,042; docs/pplx = 679; repo/pplx+bge = 648×2; topics ×2 = ~163.
- **Scale rungs present:** `scale:extractions:k512/k128/k32/k8`, `scale:repo:k64/k16/k4`, `scale:history:k64/k16/k4`, `scale:principles:k32/k8`, `scale:worldview:k32/k8`, `scale:topics:k32/k8`, `scale:operators:k8` (source form `cluster://<space>/k<K>/<label>`).
- **Test pollution:** 140 rows across ~40 `__root_*` namespaces + junk rows (model='seed'/'stub'/'synthetic', dims 2/3/4/12) sitting in production spaces (`topics`, `principles`, `topic`, `principle`, `__default__`).
- **HNSW:** 3 partial indexes present (`embedding_h1024/h2560/h3584`, halfvec_cosine_ops, default m/ef — not tuned). No index on `vec_any`.
- **MIGRATION HOLE:** FsStore disk (`.data/store/vectors`, 1.7GB) still holds unit spaces **absent from Supabase**: `common_knowledge` (112 — the `corpus(op='neighbours')` DEFAULT space!), `worldview` (324), `principles` (324), `operators` (58) — while their *pyramid rungs* DID migrate. Since `_vector_records` is retired (fs_store.py:1102, ① cutover done) and `space_matrix` now reads pg (fs_store.py:1145), those spaces are now unqueryable-by-vector.
- **Join path:** `embedding.source_address = entry.address = edge.from_ref` — but see the divergences in Axis 8.

## Axis 3 — DIRECTORY/PATHS (`ledger.entry`)

- **Lives:** `entry` 164,937 all-runs → `entry_latest` 20,602 (file 18,655 · folder 1,301 · capability 487 · ui 156 · platform 3), across 4 projects (company 18,038, counterpart-design 1,743, platforms 490, claude-ds 331).
- **Key form:** `path` (relative, e.g. `docs/MOTION.md`), `parent` (relative path of folder, NOT an address), `depth` 0–15, `address` = `code://<project>/<path>`. Unique `(run_id, path)`; trigram index on path.
- **Containment IS traversable** two ways: recursive CTE on `entry.parent` (folder nodes exist), or `contains` edges (13,855, 92.5% resolved). *Inferred:* the two are redundant encodings of the same tree; I did not verify they agree row-for-row.
- **Missing:** `parent` is a bare path while everything else is an address (a form seam at every join); capability/ui/platform nodes have `parent=NULL` (not in the tree).
- **Stale view:** `entry_latest` was created before columns `contribution, summary_for_embedding, intention_for_embedding, interp_model, interp_at, interp_prompt_version, file_meta` were added — **the view does not expose them**.

## Axis 4 — SCALE (`scale:*` spaces + `runtime/scale.py`)

- **Lives:** centroids as ordinary rows in `ledger.embedding` (space=`scale:<space>:k<K>`, source=`cluster://<space>/k<K>/<label>`); the **membership/nesting structure lives ONLY on disk** — `.data/store/scale/<space>#emb=<emb>.json` sidecars (fs_store.py:436–452): extractions, history, repo, topics, principles, worldview, operators (each `#emb=pplx`, some bare).
- **CONFIRMED: no pyramids over code / symbol / docs / desc** — neither `scale:code:*`/`scale:symbol:*`/`scale:docs:*`/`scale:desc:*` spaces in embedding nor sidecar files. The four code-side lenses have no zoom axis (upgrade 3, still to build).
- **How a rung links to members:** ONLY via the JSON sidecar (`clusters[].members` = list of unit source_addresses, `exemplar`, `children_finer` cross-rung links) — **not queryable in SQL at all**. `runtime/scale.py:build_scale_pyramid[_kmeans]` (Ward ≤4,000 units, MiniBatchKMeans+Ward above), `resolve_at_rung` (scale.py:468) just queries the `scale:` space.
- **Missing for composition:** membership as rows (e.g. `on-axis`-style edges `cluster://… contains-member <source_address>`); pyramids for the code-side spaces.

## Axis 5 — TIME

- **What exists:** `entry.extracted_at`, `edge.extracted_at`, `symbol.extracted_at` (all = run write-time, range Jun 27 → Jul 2); `embedding.ts` (embed time); `run.started_at/ended_at` (18 runs = coarse history; 9 company one-system-ledger snapshots).
- **Git-derived change times:** `entry.file_meta` (`created_at`, `last_modified_at`, `change_count`, `temporal_source:"git"`) exists in only 3 SUPERSEDED runs (3f923cdb: 3,388; 215304eb: 857; e50f4c5e: 295) — **the latest company run has 0**. So the only real "when did this file change" axis is currently invisible.
- **History/time-series:** run-scoped full snapshots ARE a history (entry keyed `(run_id, path)` + `source_hash` lets you diff runs by path), but nothing relates runs over time — no run-lineage, no change/delta table, no "changed after T" query possible except `source_hash` diff between two run_ids.

## Axis 6 — TRANSCRIPT PROVENANCE

- **In Supabase:** 1,403 `generated-by` edges (`code://company/<path>` → `exchange://<sid>/<line>`), covering **459 distinct files = 2.5% of the 18,655 latest files** — and all invisible via edge_latest (stranded run). Plus the exchange embeddings (6,983, space='exchange').
- **In sqlite only** (`/home/tim/company/.recollection/conversation-index/db.sqlite`, 220MB): **exchanges 8,224** (full user+assistant text, archive_path, line ranges, session_id — 1,254 distinct sessions, model/branch/cwd metadata), **links 23,608** (contains 8,239 / precedes 6,560 / produced_by 4,790 / references 4,019 — all mechanical), **fingerprints 8,222**, tool_calls 52,694, units 4; plus sqlite-vec virtual tables (vec0 module unavailable to plain sqlite3 CLI).
- **Join key:** `fingerprints.source` = `exchange://<session_id>/<line_start>` = `ledger.embedding.source_address` (space='exchange') = `generated-by.to_raw`. Internal sqlite key: `exchanges.id` (md5-like) = `fingerprints.unit_id` = `links.from_id/to_id`. So Supabase↔sqlite joins on the exchange:// string; sqlite-internal graph joins on the hash id. **The exchange:// addresses have no `entry` rows** — exchanges are not first-class nodes, so `generated-by.to_resolved` is NULL for all 1,403 (nothing to resolve against).
- Migration script: `ops/migrate_recollection_to_supabase.py` (fingerprints→embedding only; 6,983 landed of 8,222 — *Inferred:* remainder skipped for null blobs/conflicts, not verified).

## Axis 7 — RECALL/RECOLLECTION AS AXES

- **Per-session recall sidecars** (`runtime/session_recall.py`): 13 indexes, 809MB at `/home/tim/company/.data/recall-index/<sid>.recall.jsonl` — raw pplx-2560 vectors per dimension/section/turn chunk with line/ts/scale handles + freshness meta. **Entirely outside Supabase**; its own chunk grain (finer than exchange); key = session jsonl path + line, trivially convertible to `exchange://<sid>/<line>`.
- **exchange space** in ledger.embedding (6,983) = the recollection fingerprints, migrated — one embedding per whole exchange.
- **Duplicated vs distinct:** the SAME transcripts exist at 3 grains in 3 places: (a) exchange space in Supabase (whole-exchange, pplx), (b) `history` corpus space in Supabase (1,464 curated exchange:// units, pplx+bge — a lens over a subset), (c) recall sidecars on disk (sub-turn chunks, pplx). The raw text lives only in sqlite + `~/.claude/projects` archives. Corpus spaces (`extractions` 51,600, `history`, `repo`, `topics`…) already join the coordinate space by source_address; recall sidecars and the sqlite links graph do not.

## Axis 8 — ADDRESSES/REGISTRIES

- **`contracts/address.py:145` SCHEMES (21):** `run, cas, blob, vec, ui, code, skill, context, guide, session, cap, board, clone, mind, exchange, file, project, vi-vision, decision, image, extraction` — plus declared sub-grammars (`session://<sid>/step/<tuid>`, `run://<turn>/<member>[/<i>]`).
- **In the ledger:** entry.address = `code://<project>/<path>` (files/folders), `cap://<platform>/<kind>/<name>` (487), `ui://<region>/<element>` (156). Symbols: `code://<project>/<path>::<symbol>` (symbol.code_id, 12,681 latest).
- **Where forms STILL diverge (observed in data):**
  1. `repo` space: `code:///home/tim/company/<path>` — **absolute-path form, no project segment** (won't join entry.address).
  2. `topics` space: bare tokens (`C`) and project-less forms (`code://fabric/client.py`).
  3. `history` space uses `deferred://` and `memory://` — **schemes not in SCHEMES** (fail-loud resolver would reject them).
  4. Sidecar `design/_system/code-symbols.json` (26KB): lossy `code://<stem>/<symbol>` still powering live `resolve_scope` (the ② split); `design/_system/addresses.json` (354KB) ui:// registry only partially in ledger (156 ui entries).
  5. `entry.parent` = bare path, not an address.
  6. clone-session exchanges: `exchange://clone://<sid>/uuid:<u>/0` — nested scheme the `exchange://<sid>/<i>` grammar doesn't parse.
- **Dangling rate:** desc/code/docs/code_archaeology embeddings matching a latest entry address: 4,805/5,664 (85%; 859 dangling).

---

# (a) AXES × READINESS MATRIX

| axis | lives where | size | queryable today | missing for composition | join key |
|---|---|---|---|---|---|
| 1 Graph | ledger.edge(_latest) | 720k raw / 74k latest | kind-filtered traversal, indexed | generated-by + 30 kinds stranded below _latest; calls 29.6% / references 0.1% resolved | address string (from_ref/to_resolved) |
| 2 Vectors | ledger.embedding | 76,196; 10 real spaces × 3 layers | per-space HNSW cosine (SQL only — no RPC) | common_knowledge/worldview/principles/operators units NOT migrated; 140+ test rows polluting; no shared search fn | source_address |
| 3 Paths | ledger.entry(_latest) | 20,602 latest (1,301 folders) | parent-CTE or contains-edges; trigram path search | parent is bare path not address; view missing 7 new columns | address ↔ path |
| 4 Scale | scale:* in embedding + `.data/store/scale/*.json` | 15 rung-spaces, ~930 centroids | rung-space cosine only | membership/nesting NOT in SQL (JSON sidecar only); NO pyramids for code/symbol/docs/desc | cluster:// ↔ members only via sidecar |
| 5 Time | extracted_at / ts / run.started_at; file_meta (git) | 18 runs | write-time filters only | git change-times only in 3 superseded runs; no run-lineage/delta; "changed after T" impossible | run_id + address |
| 6 Provenance | edge kind=generated-by + .recollection sqlite | 1,403 edges (459 files, 2.5%) / sqlite: 8,224 exch, 23,608 links | raw-table query only (not in _latest) | exchanges not entry rows (to_resolved NULL); links graph + full text sqlite-only; 97.5% files uncovered | exchange://<sid>/<line> |
| 7 Recall | .data/recall-index (13 idx, 809MB) + exchange/history spaces | 8,222 fingerprints migrated → 6,983 | exchange-space cosine in SQL | session sidecar vectors + sqlite tool_calls/links outside pg; 3 grains unreconciled | exchange:// (sidecar: sid+line) |
| 8 Addresses | contracts/address.py + entry.address/code_id | 21 schemes | scheme() parse; address = the universal key | repo/topics malformed forms; deferred:///memory:// unregistered; code-symbols.json lossy sidecar live; parent not an address | the address string itself |

# (b) SHORTEST list of schema additions/joins for ONE composable query

1. **Fix supersession — make enrichment survive runs.** Either carry-forward on ingest (copy interp/file_meta/agent-pass edges into each new run keyed by `source_hash`) or redefine `*_latest` as layered: deterministic-latest ⊕ newest interpretation ⊕ agent-pass edges (a `unit_latest` view coalescing across runs by address). Without this, axes 5 & 6 and the desc lens are structurally invisible. **This single fix un-strands 3 axes.**
2. **One `unit` view + the address as the declared PK:** `entry.address`, `symbol.code_id`, `embedding.source_address`, `edge.from_ref/to_resolved` already share the grammar — add btree indexes on `entry(address)` and normalize the 3 divergent producers (repo absolute-paths, topics bare tokens, register `deferred`/`memory` or re-address them).
3. **`ledger.cluster_member` table** (cluster_address, member_address, k, space, exemplar bool, parent_cluster) — load from the 7 JSON sidecars; scale axis becomes a JOIN. Then build the code/symbol/docs/desc pyramids with the existing `build_scale_pyramid_kmeans`.
4. **`ledger.exchange` table** (address, session_id, line_start/end, ts, project, model, text or archive_path) — migrated from sqlite `exchanges`; gives `generated-by.to_resolved` a target, gives TIME to provenance, and gives semantic hits their text.
5. **One Postgres function** `ledger_query(query_vec, space, emb, k, path_prefix, kinds[], scale_k, after_ts, session)` — semantic CTE (HNSW on the right vec_ column) ∘ join unit ∘ edge-expand ∘ path LIKE ∘ time filter ∘ generated-by join — exposed via PostgREST/RPC to both MCP and UI. No new tech needed; every leg is a join once 1–4 land.
6. (Hygiene) delete/void the `__root_*` + seed/stub rows; add missing unit-space migrations (common_knowledge, worldview, principles, operators).

# (c) NOT yet in Supabase (migrate or federate)

- **Recollection sqlite graph + text** (220MB): exchanges full text (8,224), links (23,608), tool_calls (52,694) — only fingerprints were migrated. The provenance axis's substance.
- **Scale pyramid STRUCTURE** — 7 sidecar JSONs in `.data/store/scale/` (membership/nesting/exemplars).
- **Session recall sidecars** — 809MB, 13 sessions, sub-turn grain vectors (`.data/recall-index/`).
- **4 unit vector spaces** stranded on disk post-cutover: common_knowledge (112), worldview (324), principles (324), operators (58).
- **ui:// registry** `design/_system/addresses.json` (354KB; only 156 ui nodes landed) + the lossy `code-symbols.json` still powering live resolve_scope (② scope).
- **Git change-history** (the real time axis) — derivable from the repo, currently captured only as file_meta in dead runs.
- Extraction raw records (`.data/store/extractions/`, 76MB — the text behind `extraction://full/<n>`) and the rest of FsStore (~objects/events/chat/graphs/sessions) — the north-star's deliberate "later".
