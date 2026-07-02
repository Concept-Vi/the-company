# Plan B design take · SQL-ARCHITECT — `ledger.query(spec jsonb)` and the schema that makes the axes composable

*One of three independent design perspectives over R1-axes-inventory + R2-query-patterns. Grounded in:
the live DDL (`0011_ledger.sql`, `0012_ledger_interpretive.sql`), the supersession incident (commit
`18a3a875` — R1's disease bit our own work live), NORTH-STAR standing directives. Register: prescriptive
PROPOSAL — nothing here is built; DDL is sketch-grade, meant to be judged against the other two takes.*

---

## 0. Posture

The database is the one place both faces (MCP + UI) already share. So the design puts **the entire
capability in the schema**: one PL/pgSQL function `ledger.query(spec jsonb)` compiled from a fixed CTE
skeleton (R2's verdict, adopted), sitting on a schema that is first REPAIRED (supersession), then
EXTENDED (membership, exchanges, indexes, lexical), then CLEANED (hygiene + address normalization).
The function is the artifact; everything else exists so its stages are all plain indexed joins.

---

## 1. THE SUPERSESSION FIX — enrichment moves OUT of run-scoped rows

### The disease, restated precisely
`latest_run` picks one run per `(project, purpose)`; `entry/edge/symbol` rows are keyed by `run_id`.
Interpretations, `file_meta`, and every agent-pass edge kind (`generated-by` + 30 others) were written
INTO rows of whatever run was current — so each fresh deterministic snapshot orphans them below the
`*_latest` views. This is not a view bug; it is a **key error**: an interpretation's identity is
*(which unit, which content-version)* = `(address, source_hash)` — not *(which snapshot run)*. Evidence
it's structural, not incidental: 18a3a875 had to carry 4,199 descriptions + 1,403 edges forward BY HAND
one day after R1 named the disease.

### The two candidate fixes, weighed

**(A) Layered view** — keep writing enrichment onto run rows; define `unit_latest` as
deterministic-latest ⊕ LATERAL "newest non-null interp across all runs where (path, source_hash)
matches" ⊕ agent-pass edges surfaced regardless of run.
- *For:* zero writer changes; purely additive.
- *Against:* the coalesce is a per-row lateral over a 164k-row (and growing ~18k/run) table — every
  query pays for the disease forever; every future enrichment column must be hand-threaded into the
  view; the wrong key stays load-bearing, so the next enrichment kind strands again by default. It
  institutionalizes carry-forward as the permanent read path.

**(B) Side tables keyed by content identity** — enrichment never lives in run-scoped rows, so runs
*cannot* strand it, by construction.
- *For:* correct key; queries become one indexed join; carry-forward scripts are deleted, not
  institutionalized; new enrichment kinds inherit immunity.
- *Against:* writers must be repointed (the interp job, the symbol-description writer, the
  `build_embeddings.py` carry logic) — a coordinated write-path cutover.

**PICK: (B), with (A)'s view as the read face.** The view (`unit_latest`) still exists, but it is a
cheap two-way join, not a cross-run archaeology. This matches the north-star ("current schema is
scaffolding, not spec") and the ①/② precedent: repoint at the single correct source, comment out the
old path, loud breadcrumbs.

### The DDL (sketch)

```sql
-- 0013_ledger_supersession.sql
create table ledger.interpretation (
  address        text not null,          -- code://<proj>/<path>  OR  code://…::<symbol> (one table for both)
  source_hash    text not null,          -- file's hash; for symbols: PARENT FILE's hash at interp time
  project        text not null,
  what_it_does   text,  purpose_doc  text,  contribution text,
  summary_for_embedding text,  intention_for_embedding text,
  observations   jsonb,  extra jsonb,
  interp_model   text,  interp_prompt_version text,  produced_by_session text,
  interp_at      timestamptz not null default now(),
  primary key (address, source_hash)
);
create index interp_addr_idx on ledger.interpretation (address);

create table ledger.file_meta (           -- the git time axis; key = path identity, NOT content or run
  project text not null, path text not null,
  address text not null,
  git_created_at timestamptz, git_last_modified_at timestamptz, change_count int,
  temporal_source text not null default 'git', as_of timestamptz not null default now(),
  primary key (project, path)
);
create index file_meta_addr_idx on ledger.file_meta (address);
create index file_meta_mtime_idx on ledger.file_meta (git_last_modified_at);

create table ledger.assertion (           -- agent/organic edges: run-independent claims
  assertion_id uuid primary key default gen_random_uuid(),
  from_address text not null,  kind text not null,
  to_address   text,           to_raw text not null,
  extra jsonb, produced_by_session text, model text,
  asserted_at timestamptz not null default now(),
  unique (from_address, kind, to_raw)
);
create index assertion_from_idx on ledger.assertion (kind, from_address);
create index assertion_to_idx   on ledger.assertion (kind, to_address);
```

**The distinction that decides which table an edge goes in:** deterministic *structural* edges
(calls/imports/contains/references/…) describe a snapshot → stay run-scoped in `ledger.edge`.
*Assertions* (generated-by, authored_by, in_channel, relates-to, launched-by, exchange links, …) are
claims about the world that a re-extraction does not re-derive and does not invalidate — provenance is
append-only history, it does not go stale the way a description does. Note the asymmetry with
`interpretation`: descriptions key on `source_hash` (a changed file makes its description stale and it
must fall away); assertions do not (a file's generating exchange stays true forever).

### The views

```sql
create or replace view ledger.unit_latest as     -- THE query surface for entries
  select e.entry_id, e.run_id, e.project, e.path, e.node_type, e.parent, e.depth, e.ext, e.language,
         e.size_bytes, e.line_count, e.source_hash, e.address, e.coverage_state, e.kind,
         i.what_it_does, i.purpose_doc, i.contribution, i.summary_for_embedding,
         i.intention_for_embedding, i.interp_model, i.interp_at,
         fm.git_created_at, fm.git_last_modified_at, fm.change_count
  from ledger.entry e
  join ledger.latest_run r using (run_id)
  left join ledger.interpretation i on i.address = e.address and i.source_hash = e.source_hash
  left join ledger.file_meta fm     on fm.project = e.project and fm.path = e.path;

create or replace view ledger.symbol_unit_latest as
  select s.*, i.what_it_does as description_i, i.summary_for_embedding, i.interp_at
  from ledger.symbol s join ledger.latest_run r using (run_id)
  join ledger.entry pe on pe.run_id = s.run_id and pe.path = s.parent_path
  left join ledger.interpretation i on i.address = s.code_id and i.source_hash = pe.source_hash;

create or replace view ledger.edge_unified as    -- structural latest ∪ live assertions
  select from_ref as from_address, kind, to_raw, to_resolved as to_address,
         line, extra, run_id, extracted_at as at, 'structural' as layer
  from ledger.edge_latest
  union all
  select from_address, kind, to_raw, to_address, null, extra, null, asserted_at, 'assertion'
  from ledger.assertion;
```

Note `ledger.embedding` needs nothing here — it is already keyed `(source_address, space, emb_layer)`,
i.e. already content-addressed, already immune. The disease was only ever in the run-scoped tables.

### Migration + cutover discipline
1. Backfill `interpretation`: `INSERT … SELECT DISTINCT ON (address, source_hash) …` from ALL runs of
   `ledger.entry` where interp fields are non-null, `ORDER BY address, source_hash, interp_at DESC NULLS LAST,
   extracted_at DESC` (same for symbol rows via `code_id`). Backfill `file_meta` from the 3 superseded
   runs holding git times (3f923cdb / 215304eb / e50f4c5e), newest per path. Backfill `assertion` from
   the raw `edge` table for the organic-kind list, newest per `(from_ref, kind, to_raw)`.
2. Repoint writers (interp job → `interpretation`; git-meta pass → `file_meta`; agent passes →
   `assertion`). The 18a3a875 carry-forward code in `ops/build_embeddings.py` is retired (commented,
   per the no-fallback=comment-out rule).
3. **Guard trigger** on `ledger.entry` post-cutover: any INSERT/UPDATE setting the deprecated interp
   columns RAISEs — `'ledger.entry.<col> is retired; write ledger.interpretation (address, source_hash);
   see 0013_ledger_supersession.sql'`. Two homes diverging silently is exactly the failure class the
   fail-loud law exists for. Columns are NOT dropped (recoverable, legible).
4. `unit_latest` reads interpretation ONLY (no `coalesce(i.x, e.x)` transition crutch — a coalesce
   would mask writer drift, violating fail-loud).

---

## 2. SCHEMA ADDITIONS — R1's shortest list, specced

```sql
-- 0014_ledger_coordinates.sql
-- (a) address as a first-class join key (R1 item 2)
create index entry_addr_idx      on ledger.entry (run_id, address);
create index entry_addr_all_idx  on ledger.entry (address);

-- (b) scale membership as rows (R1 item 3) — from the 7 sidecars + future code-side pyramids
create table ledger.cluster_member (
  space           text not null,          -- 'extractions', 'history', … later 'code','symbol','docs','desc'
  emb             text not null,          -- 'pplx' …
  k               int  not null,          -- the rung
  cluster_address text not null,          -- cluster://<space>/k<K>/<label>
  member_address  text not null,          -- unit source_address
  is_exemplar     boolean not null default false,
  parent_cluster  text,                   -- cluster:// at the coarser rung (children_finer inverted)
  built_at        timestamptz not null default now(),
  primary key (cluster_address, member_address)
);
create index cm_member_idx on ledger.cluster_member (member_address);
create index cm_space_idx  on ledger.cluster_member (space, emb, k);
-- loader: ops/load_cluster_members.py over .data/store/scale/<space>#emb=<emb>.json ;
-- runtime/scale.py:build_scale_pyramid[_kmeans] gains a "also emit rows" step so future pyramids
-- (code/symbol/docs/desc — upgrade 3) land here at build time, sidecars retired to comment.

-- (c) exchanges as first-class nodes (R1 item 4) — from .recollection sqlite
create table ledger.exchange (
  address       text primary key,          -- exchange://<sid>/<line_start> (canonical grammar)
  session_id    text not null, line_start int not null, line_end int,
  ts            timestamptz,
  project text, model text, branch text, cwd text,
  text_user     text,                      -- FULL TEXT COMES (see decision below)
  text_assistant text,
  archive_path  text not null,             -- authoritative pointer for everything beyond (tool calls stay federated)
  fts tsvector generated always as
      (to_tsvector('english', coalesce(text_user,'') || ' ' || coalesce(text_assistant,''))) stored
);
create index exchange_fts_idx on ledger.exchange using gin (fts);
create index exchange_sid_idx on ledger.exchange (session_id, line_start);
create index exchange_ts_idx  on ledger.exchange (ts);

-- (d) composite edge indexes for typed traversal (R2's verified gap)
create index edge_run_kind_from_idx on ledger.edge (run_id, kind, from_ref);
create index edge_run_kind_to_idx   on ledger.edge (run_id, kind, to_resolved) include (from_ref);

-- (e) lexical over the interpreted text (tsvector lives on the SIDE TABLE now — consequence of §1)
alter table ledger.interpretation add column fts tsvector generated always as
  (to_tsvector('english', coalesce(what_it_does,'')||' '||coalesce(purpose_doc,'')||' '||coalesce(contribution,''))) stored;
create index interp_fts_idx  on ledger.interpretation using gin (fts);
create index symbol_name_trgm on ledger.symbol using gin (name gin_trgm_ops);  -- identifiers: trgm > ts

-- (f) axis catalog — the enum whitelists the function validates against (data-driven, not hardcoded)
create table ledger.axis_catalog (category text not null, value text not null, meta jsonb,
                                  primary key (category, value));
-- refreshed at ingest + by 0014: categories = edge_kind, assertion_kind, space, emb_layer, scale_rung.
create index embedding_space_idx on ledger.embedding (space, emb_layer);

-- (g) hygiene (R1 item 6) — DELETE with counted report in the migration log
delete from ledger.embedding where model in ('seed','stub','synthetic');
delete from ledger.embedding where space like '\_\_root\_%' escape '\';
-- + ops/migrate_missing_spaces.py: common_knowledge(112)/worldview(324)/principles(324)/operators(58)
--   from FsStore disk → ledger.embedding (they are UNQUERYABLE since the ① cutover — live breakage).
```

**Exchange full-text decision, weighed:** pointers-only keeps pg lean but makes the provenance axis
mute — every hit needs a sqlite/archive round-trip from a *Postgres function that cannot make one*, and
lexical search over conversations becomes impossible in the one query. Full text of user+assistant for
8,224 exchanges is tens of MB — trivial. **Text comes in; tool_calls (52,694) and sub-turn recall
sidecars stay federated behind `archive_path`/session-id** (they have their own grain and their own
consumer; forcing them in now is scope creep — noted as a later wave). The sqlite `links` graph
(precedes/produced_by/contains/references, 23,608 mechanical rows) loads into `ledger.assertion`
verbatim (they are run-independent claims between exchange:// addresses — exactly what the table is
for). Then backfill `generated-by.to_resolved = to_raw` wherever an exchange row now exists.

**Address normalization — data-side, not query-side.** The divergences R1 found (`repo` space's
`code:///home/tim/company/<path>` absolute form; `topics`' bare tokens; unregistered `deferred://`
`memory://`) get a one-time normalization pass (`ops/normalize_addresses.py`: rewrite `repo` rows to
`code://company/<path>`; re-address or quarantine `topics` malformed rows; register `deferred`/`memory`
in `contracts/address.py` SCHEMES). Per-query rewriting inside the function would institutionalize the
divergence and tax every join. Inside `ledger.query`, a small `ledger._canon_address(text)` helper only
(i) canonicalizes trivia (trailing slash), (ii) **refuses** unknown schemes / project-less forms with a
breadcrumb: expected grammar + the 21 known schemes + nearest-match suggestions from a trgm lookup over
`entry.address`. Refuse-with-breadcrumb, never silent-guess — an agent can act on a breadcrumb; a wrong
silent match poisons results invisibly.

---

## 3. THE SPEC VOCABULARY (v1) — R2's draft refined against R1's reality

```jsonc
{
  "v": 1,                                       // spec_version — unknown value RAISES with migration pointer
  "run": "latest",                              // "latest" | uuid | {"project":"company","purpose":"one-system-ledger","at":"<ts>"}
                                                //   "latest" = latest DETERMINISTIC snapshot per (project,purpose).
                                                //   Post-§1 this is honest: interpretation/file_meta/assertions join by
                                                //   address regardless of run — "latest" no longer hides enrichment.
                                                //   "at" = time-travel: latest run with started_at <= at.
  "filter": {                                   // structured pre-filter → the candidates CTE (btree/trgm only)
    "path":  { "under": "canvas/app/", "glob": "*.ts", "not_under": ["node_modules/"] },
    "entry": { "node_type": ["file","symbol"], "language": ["typescript"], "coverage_state": null },
    "time":  { "changed_after": "2026-06-01T00:00:00Z",   // ← file_meta.git_last_modified_at (real axis, per §1)
               "extracted_after": null, "interp_after": null },
    "prov":  { "generated_in_session": null,    // via assertion kind=generated-by → exchange.session_id
               "model": null, "pass": null }
  },
  "scale": {                                    // Axis 4 — needs cluster_member (§2b)
    "space": "extractions", "emb": "pplx",
    "rung": "k128",
    "route": { "top": 5 },                      // coarse routing: top-P centroids (P generous — boundary recall)
    "within": null,                             // "cluster://extractions/k32/<label>" — zoom INTO one cluster's subtree
    "drill": true                               // true → results are MEMBERS; false → results are the CENTROIDS (map view)
  },
  "graph": {                                    // Axis 1 — over edge_unified (structural ∪ assertions)
    "anchor": { "address": "code://company/mcp_face/suite.py" },   // or {"from_results": true}
    "kinds": ["calls"], "direction": "in",      // in | out | both
    "depth": 2,                                 // default 2, hard max 4
    "mode": "restrict"                          // restrict | expand | rank (§6)
  },
  "semantic": {                                 // Axis 2
    "space": "extractions", "emb": "pplx", "layer": "summary",
    "text": "how noticeboard items are ingested",   // server-side embed via the embedder RPC/service, or "vector": [...]
    "k": 50, "min_sim": null
  },
  "lexical": { "text": "run_cascade", "mode": ["trgm","fts"],
               "fields": ["path","symbol_name","what_it_does","exchange_text"] },
  "fuse": { "method": "rrf", "rrf_k": 60,
            "weights": { "semantic": 1.0, "lexical": 0.7, "graph": 0.0 } },
  "page": { "limit": 20, "cursor": null },      // keyset (score DESC, address) — opaque base64(jsonb); NEVER offset
  "return": {
    "fields": ["path","what_it_does","kind"],   // whitelisted column map — %I only
    "edges": false,                             // attach 1-hop edge_unified neighborhoods per hit
    "provenance": false,                        // attach the generating exchange (assertion generated-by → ledger.exchange)
    "score_breakdown": true                     // per-row: each axis's rank + fused score
  }
}
```

**Return shape** (every response, no exceptions):
```jsonc
{ "rows": [ { "address": "...", "fields": {...}, "score": 0.031,
              "breakdown": {"semantic": 3, "lexical": 12, "graph": null},
              "via": null } ],                  // or {"graph_path": [...]} for mode=expand attachments
  "meta": { "run_id": "390286ec…", "spec_v": 1,
            "plan": { "stages": ["candidates","scale","semantic","lexical","fuse","page"],
                      "semantic_branch": "exact|hnsw_iterative", "candidates_n": 412,
                      "frontier_capped": false, "scan_tuples_hit": false },
            "cursor": "…" } }
```
The `meta.plan` echo is the fail-loud guarantee R2 asked for: under-recall is never silent — the caller
always sees which branch ran, how big the candidate set was, and whether any safety valve tripped.

**Every axis is optional; absent axes collapse to pass-through.** At least one of
{semantic, lexical, filter, graph.anchor, scale} must be present or the function raises ("empty spec").
Unknown top-level keys, unknown enum values, malformed addresses: RAISE, naming the axis, the offending
value, the valid vocabulary, and the fix (§4 error style).

---

## 4. THE FUNCTION — `ledger.query(spec jsonb)`, PL/pgSQL, dynamic-SQL compilation

Lives in the DB per R2's verdict (adopted: one-definition literal via PostgREST `.rpc` + supabase-py;
transactional `SET LOCAL`; bounded variability). `VOLATILE`, `SECURITY INVOKER`, `EXECUTE` granted to
the service roles. Helpers: `ledger._canon_address(text)`, `ledger._validate_spec(jsonb)` (returns a
typed record of validated params), `ledger._embed(text, space, emb)` (delegates to the embedder RPC —
or the caller passes `vector`; the function never silently embeds with the wrong lens: space→emb
compatibility is checked against `axis_catalog`).

### Stage pipeline (pseudo-steps — the compilation order)

```
0  VALIDATE      _validate_spec: v==1; unknown keys RAISE; enums vs axis_catalog; addresses via _canon_address;
                 depth<=4; limit<=200; decode cursor. Whitelist-or-raise on EVERYTHING interpolated.
1  RESOLVE RUN   run:="latest" → SELECT run_id FROM ledger.latest_run WHERE project=$p AND purpose=$q
                 ("at" variant adds started_at<=at ORDER BY started_at DESC LIMIT 1). No row → RAISE
                 breadcrumb ("no complete run for (company, one-system-ledger); runs present: …").
2  GUCS          SET LOCAL hnsw.ef_search=…, hnsw.iterative_scan=relaxed_order,
                 hnsw.max_scan_tuples=60000, work_mem bump — only if the hnsw branch may run.
3  COMPILE       assemble the fixed skeleton with format(%I/%L) — only stages present in the spec:

   WITH candidates AS NOT MATERIALIZED (            -- filter axes over unit_latest, run_id threaded
        SELECT address, entry_id, path, source_hash FROM ledger.unit_latest
        WHERE run_id=$run [AND path LIKE …] [AND node_type=ANY(…)] [AND git_last_modified_at>…]
        [AND address IN (SELECT member_address FROM ledger.cluster_member WHERE …)]   -- scale w/o routing
   ),
   scale_route AS (…),                              -- §5: exact cosine over the rung space → top-P clusters
   graph_r AS (…),                                  -- §6: recursive CTE (mode=restrict) → semi-join candidates
   sem AS (…),                                      -- §4a: the selectivity branch
   lex AS (…),                                      -- trgm(path,symbol.name) rank-list ∪ fts(interpretation.fts,
                                                    --   exchange.fts) rank-list, each LIMIT 2k
   fused AS (SELECT COALESCE(s.addr,l.addr,g.addr) addr,
                    Σ wᵢ/(60+rankᵢ) score, jsonb breakdown
             FROM sem s FULL OUTER JOIN lex l USING(addr) FULL OUTER JOIN graph_rank g USING(addr)),
   paged AS (SELECT * FROM fused WHERE (score,addr) < ($cursor_score,$cursor_addr)   -- keyset
             ORDER BY score DESC, addr LIMIT $limit)
   SELECT hydrate…                                  -- join unit_latest fields; return.edges → 1-hop
                                                    -- edge_unified; return.provenance → generated-by → exchange
4  EXECUTE       one EXECUTE of the assembled statement into the result jsonb.
5  META          attach run_id, plan (branch taken, candidates_n, caps), next cursor. RETURN jsonb.
```

### 4a. The selectivity branch (the R2 trap-1 answer, made explicit)
Before the semantic stage compiles, run `SELECT count(*) FROM (SELECT 1 FROM candidates LIMIT 8001) t`
(the LIMIT-bounded count — never a full count on a pathological filter):
- **n ≤ 8,000 → EXACT**: `ORDER BY e.vec_<dim> <=> $q` over `embedding JOIN candidates ON
  source_address=address AND space=… AND emb_layer=…` — perfect recall, ms-cheap, no GUCs.
- **n > 8,000 (or no filter) → HNSW ITERATIVE**: index scan on the right partial index with the SET
  LOCAL GUCs from stage 2, filter as semi-join, outer re-sort (relaxed_order reorders slightly).
- The branch taken is echoed in `meta.plan.semantic_branch`; if `max_scan_tuples` trips,
  `scan_tuples_hit: true` — never a silently short result.
- `scale:*` rung spaces (4–512 rows) are ALWAYS exact by construction (§5) — they never touch HNSW.

### Error/raise style (uniform, fail-loud, breadcrumbed)
```
RAISE EXCEPTION USING
  MESSAGE = format('ledger.query[graph.kinds]: unknown edge kind %L', bad),
  DETAIL  = format('known kinds: %s (ledger.axis_catalog category=edge_kind)', known_list),
  HINT    = 'if this kind was just introduced at ingest, refresh the catalog: ops/refresh_axis_catalog.py';
```
Every raise names **the axis path in the spec** (`graph.kinds`, `semantic.space`, `filter.path.under`),
the offending value, the valid vocabulary, and the fix command. Address failures add the old-vs-new
breadcrumb per the north-star law ("expected code://<project>/<path>; got absolute-path form;
previously the repo space used code:///home/…; normalized by ops/normalize_addresses.py").

---

## 5. SCALE / RUNG COMPOSITION — zoom as spec, world-map for free

Once `cluster_member` exists (§2b), coarse-to-fine compiles to three plain stages:

1. **Route** (if `scale.route`): exact cosine over `space='scale:<space>:<rung>'` (tiny — always exact)
   → top-P `cluster://` addresses. P defaults to 5 (boundary-recall caveat from R2 §6: generous P,
   fine stage is cheap).
2. **Restrict**: `cluster_member` join turns the routed clusters into a `member_address` pre-filter on
   `candidates` — the scale axis becomes a structured filter like any other.
3. **Fine**: the semantic stage then runs over members — typically the exact branch (top-5 clusters at
   k128 over 51k ≈ ~2,000 candidates).

**Zoom semantics (the ③ world-map contract):**
- `{"rung":"k32", "drill":false}` + no semantic → **the map**: rows ARE the centroids (address =
  `cluster://…`, fields = exemplar + member count + label). This is the query the projection engine /
  LatticeView calls to render a level.
- `{"within":"cluster://extractions/k32/<label>", "rung":"k128", "drill":false}` → **one zoom step**:
  the finer rung's clusters inside one coarse cluster (via `parent_cluster` nesting).
- Same spec with `"drill":true` (+ optional semantic text) → **leaf resolve**: actual units inside the
  viewport cluster, semantically ranked. UI zoom interaction ↔ spec mutation, 1:1 — no UI-side logic.
- Code-side pyramids (code/symbol/docs/desc — upgrade 3) require zero function changes: build the rungs
  with `build_scale_pyramid_kmeans` + emit `cluster_member` rows; the new spaces appear in
  `axis_catalog` and the same spec vocabulary addresses them.

---

## 6. THE GRAPH STAGE — one recursive CTE, three roles

Compiled shape (over `edge_unified`, direction decides which column anchors):

```sql
WITH RECURSIVE g AS (
  SELECT to_address AS addr, 1 AS hop, ARRAY[$anchor, to_address] AS seen
  FROM ledger.edge_unified
  WHERE from_address = $anchor AND kind = ANY($kinds)
    AND (run_id = $run OR layer = 'assertion')          -- run-scope structural; assertions are run-free
  UNION ALL
  SELECT e.to_address, g.hop+1, g.seen || e.to_address
  FROM g JOIN ledger.edge_unified e ON e.from_address = g.addr
  WHERE g.hop < $depth AND e.kind = ANY($kinds)
    AND (e.run_id = $run OR e.layer = 'assertion')
    AND e.to_address <> ALL(g.seen)                     -- cycle guard: visited-array (portable; also
)                                                        --   gives the path back for return.via)
SELECT DISTINCT ON (addr) addr, hop FROM g ORDER BY addr, hop LIMIT $frontier_cap;  -- frontier discipline
```
Guards: depth default 2 / hard max 4; visited-array cycle guard (chosen over the `CYCLE` clause — R2
never verified `server_version`, and the array doubles as the returnable path); frontier cap default
2,000 reachable nodes with `meta.plan.frontier_capped=true` when it trips (a raised flag, not a silent
truncation). The recursive arm hits the new `(run_id, kind, from_ref)` / `(run_id, kind, to_resolved)`
composites — without them this stage is the 30-second query (493k `calls` rows corpus-wide).

**When graph is which signal:**
- **RESTRICT** (compiled BEFORE semantic; reachable-set ∩ candidates): "semantic search *within* what
  calls suite.py" — the anchor defines the sub-world. Use when the anchor is trusted and the question
  is scoped.
- **EXPAND** (compiled AFTER fuse; 1..depth neighborhood of the result page, attached with
  `via.graph_path`, unscored): "show me the hits *plus their structure*" — the UI neighborhood view.
  Never changes ranking; purely additive hydration.
- **RANK** (a third RRF list: rank = hop distance from anchor, closer = better, weight from
  `fuse.weights.graph`): "prefer things near X but don't exclude the rest" — soft locality. Use when
  the anchor is a hint, not a boundary.

---

## 7. PERFORMANCE — golden specs + the R2 traps, answered

**Golden-spec suite** (stored as fixtures; run by `ops/verify_ledger_query.py` after every migration
touching the function — each asserts (a) the `meta.plan` echo, (b) EXPLAIN properties, (c) row bounds):

| # | spec (canonical) | expected plan assertions |
|---|---|---|
| G1 | pure semantic, extractions, no filter | `hnsw_iterative` branch; index scan on `embedding_h2560` |
| G2 | semantic + `path.under: canvas/app/` | `exact` branch; candidates_n < 8k; NO hnsw scan |
| G3 | hybrid: semantic + lexical `run_cascade` | RRF join present; trgm GIN + fts GIN both used |
| G4 | graph-restrict: calls→suite.py depth 2 + semantic | recursive arm uses `edge_run_kind_*` (no seq scan on edge); cycle terminates |
| G5 | world-map: `scale k32, drill:false` | exact over rung space ONLY; no entry/edge touch; rows=centroids |
| G6 | coarse-to-fine: route top5 k128 + drill + text | cluster_member join; fine stage exact |
| G7 | pointing-loop (worked ex. D below) | assertion + exchange joins; provenance attached |
| G8 | time: `changed_after` June 15 + semantic | file_meta join; exact branch |

**The three R2 traps, addressed in-design:** (1) post-filter starvation → the explicit selectivity
branch + always-exact rung spaces + `meta.plan` echo; (2) recursive blow-up → composite indexes +
run-scope in the recursive arm + depth/cycle/frontier guards with raised flags; (3) cross-run leakage &
CTE materialization → run resolved ONCE at stage 1 and threaded as a literal into every structural
predicate; `candidates` is the only entry point to entry data; all CTEs `NOT MATERIALIZED` (except the
tiny routed-cluster list, deliberately materialized); keyset-only paging (offset over relaxed_order is
non-deterministic — refused in vocabulary, not just discouraged).

Deliberately deferred (with triggers to revisit): partial HNSW per big space (`extractions`) — add when
G1 latency shows filter starvation despite iterative scan; closure/reachability tables — only if
unbounded-depth becomes a real workload; pgroonga/rum — only if `ts_rank` proves too weak on G3-class
relevance checks.

---

## 8. VERSIONING / MIGRATION — where it lives, how it evolves

**Files (the canonical migration home, `build-prep/claude-design/supabase/supabase/migrations/`):**
- `0013_ledger_supersession.sql` — §1: interpretation, file_meta, assertion (+backfills, guard trigger,
  unit_latest / symbol_unit_latest / edge_unified, entry_latest recreated to expose current columns).
- `0014_ledger_coordinates.sql` — §2: cluster_member, exchange, composite/addr/space indexes, fts
  columns+GINs, axis_catalog (+seed), hygiene deletes (counted). **Also canonicalizes `ledger.embedding`
  DDL** — the live table (76k rows) has NO tracked migration today; 0014 writes its
  `create table if not exists` so the schema's one home is complete.
- `0015_ledger_query.sql` — the function + helpers (`_validate_spec`, `_canon_address`, `_embed`,
  `_rrf`). `CREATE OR REPLACE`. First and only spec version: `v:1`.

**Ops loaders (not SQL):** `load_cluster_members.py` (7 sidecars→rows), `load_exchanges.py`
(sqlite→exchange + links→assertion + to_resolved backfill), `migrate_missing_spaces.py` (4 stranded
unit spaces), `normalize_addresses.py` (repo/topics forms), `refresh_axis_catalog.py`,
`verify_ledger_query.py` (golden suite).

**Evolution contract:** the spec carries `"v"`; the function supports exactly the current version and
RAISEs on others, naming the migration that changed it ("spec v1 retired by 0021_ledger_query_v2.sql;
vocabulary diff: …"). Additive vocabulary (new optional keys) does NOT bump v — unknown-key raising
means old servers loudly reject new specs, which is the correct failure direction. Function-body changes
ship as a new migration file re-`CREATE OR REPLACE`-ing (never edited in place), golden suite re-run in
the same migration's verify step. MCP tool + UI both call `.rpc('query', {spec})` in schema `ledger` —
neither carries any query logic; the one-definition property stays literal.

**Build sequence (dependency-ordered):**
1. 0013 supersession (unblocks time + provenance + desc axes — everything else reads through unit_latest)
2. writer repoint + guard trigger live (the disease is now impossible, not patched)
3. 0014 schema + the four ops loaders + hygiene + normalization
4. 0015 function v1: stages candidates/semantic/lexical/fuse/page first (G1–G3 green)
5. graph + scale stages (G4–G6 green)
6. provenance hydration + pointing-loop (G7–G8 green)
7. MCP tool wrapper + UI `.rpc` cutover (thin; the ③ design wave consumes G5/G6 as the world-map engine)

---

## 9. FOUR WORKED SPECS

**A — the world-map zoom (③'s engine).** *"Render the extraction world at coarse grain; then zoom into
the ingest cluster."* Map frame:
```jsonc
{ "v":1, "run":"latest",
  "scale": { "space":"extractions", "emb":"pplx", "rung":"k32", "drill": false },
  "return": { "fields":["path","what_it_does"], "score_breakdown": false }, "page": {"limit": 32} }
```
→ 32 rows, addresses `cluster://extractions/k32/*`, exemplar + member-count fields; no HNSW, no entry
scan. Zoom step: add `"within":"cluster://extractions/k32/ingest-flows", "rung":"k128"` — the finer
clusters inside that region. Leaf resolve: same + `"drill":true, "semantic":{"text":"noticeboard
ingestion", "space":"extractions", "k":20}`.

**B — hybrid identifier hunt.** *"Where is run_cascade handled, semantically and literally?"*
```jsonc
{ "v":1, "run":"latest",
  "semantic": { "space":"extractions","emb":"pplx","text":"how a saved cascade is executed","k":50 },
  "lexical":  { "text":"run_cascade", "mode":["trgm","fts"], "fields":["path","symbol_name","what_it_does"] },
  "fuse": { "method":"rrf", "weights":{"semantic":1.0,"lexical":0.9} },
  "page": {"limit":15}, "return": {"fields":["path","what_it_does"],"score_breakdown":true} }
```
→ trgm wins the exact identifier, vectors win the paraphrase; breakdown shows which.

**C — graph-restricted semantic with time.** *"Among things that call into suite.py (≤2 hops), what
touching channel routing changed since mid-June?"*
```jsonc
{ "v":1, "run":"latest",
  "graph": { "anchor":{"address":"code://company/mcp_face/suite.py"}, "kinds":["calls"],
             "direction":"in", "depth":2, "mode":"restrict" },
  "filter": { "time": {"changed_after":"2026-06-15T00:00:00Z"} },
  "semantic": { "space":"extractions","emb":"pplx","text":"channel routing and reply delivery","k":30 },
  "page": {"limit":10} }
```
→ recursive CTE on composites → reachable set ∩ file_meta-time filter → exact semantic (small set).

**D — the pointing loop (provenance round-trip).** *"I'm pointing at this UI element — what code powers
it, and what conversation created that code?"*
```jsonc
{ "v":1, "run":"latest",
  "graph": { "anchor":{"address":"ui://canvas/lattice-view"},
             "kinds":["powered-by","binds-ui","references"], "direction":"out", "depth":1,
             "mode":"restrict" },
  "return": { "fields":["path","what_it_does"], "edges": true, "provenance": true },
  "page": {"limit":10} }
```
→ ui→code via the ② join (powered-by 359 / binds-ui 172, both 100% resolved); per hit, hydration
follows `assertion kind=generated-by` → `ledger.exchange` and returns session_id, ts, and the exchange
text — the click-a-thing→see-its-conversation slice, one spec.

---

## 10. THE THREE BIGGEST RISKS OF THIS DESIGN (honest)

1. **The §1 write-path cutover is a coordinated multi-writer change, and partial adoption is the
   dangerous state.** If any writer (interp job, symbol pass, a forgotten script) keeps writing entry
   columns after unit_latest reads only `interpretation`, its output vanishes — the same *symptom* as
   the disease this fixes. The guard trigger is my mitigation, but it only covers writes I anticipated
   (entry's interp columns); a NEW enrichment writer targeting the wrong home isn't caught by a trigger
   that doesn't know it. Residual risk: process, not schema — the cutover needs a verified sweep of all
   writers (grep for the column names across ops/ + runtime/) before the trigger ships.
2. **A few hundred lines of dynamic PL/pgSQL is the least-reviewable artifact in the repo, maintained
   by agents.** format()-assembled SQL is hard to read, plan variance across branches is real, and one
   interpolation that isn't %I/%L is an injection or a corruption. Whitelist-everything + golden EXPLAIN
   suite is strong mitigation, but the honest statement is: this concentrates the system's most complex
   logic in its least-debuggable language, betting that the one-definition property (which is real and
   valuable) is worth it. If the function's vocabulary starts growing past the 8 axes, that bet flips —
   the extraction moment R2 named ("second consumer needs the compiler elsewhere") must actually be
   honored, and agents historically extend in place.
3. **RRF fuses ranked lists over DIFFERENT unit populations, and the incoherence is semantic, not
   visible in any EXPLAIN.** Lexical hits exchanges and symbols; semantic hits extraction units; graph
   ranks files — all addresses, so the join works, but a file and its own symbols and its extraction
   units can occupy 3 result slots for one underlying thing, and cross-grain scores aren't calibrated.
   Golden specs catch plans, not relevance. Mitigation is partial: `score_breakdown` makes it
   *inspectable*, and a `return.collapse:"file"` roll-up is sketched-but-not-designed here. If the other
   two takes have a stronger identity/grain story (e.g. a unit-identity table mapping symbol→file→
   extraction), theirs should win on this point.
