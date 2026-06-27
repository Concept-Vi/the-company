# THE LEDGER — spec, ideas, plan, goals

*Status: design converged with Tim (2026-06-27), pre-build. Lives in the-one-system effort (channel://ch-9). This is the canonical spec the deterministic harness, the Opus pass, and the ingest all read from. It is written to be **reusable** — done well, this whole process fuses into the Company and the channel systems.*

---

## 1. WHY — purpose & goals

The Company is an entity, not an app — splinters from hundreds of unspecced Claude Code sessions, none human-read, split/partial/disorganised, and the unified system is undocumented anywhere. Before anything can be merged/unified/consolidated into the one new Supabase-backed system, there must be **total, grounded, trustworthy knowledge of what is actually built** — because the fragmentation was *caused* by agents acting on partial knowledge.

The **ledger** is that knowledge, made into a queryable substrate:

- **Path-anchored.** Every file and folder is a node, keyed by its path (relative-to-root = its address). The directory tree is the one deterministic, complete enumeration available — so **completeness becomes a diff, not a claim**: list the tree, compare to the ledger, any path without a full entry is provably not done. This is the only thing that makes "100% coverage / no partial" real instead of a promise.
- **A graph, not a list.** The path-tree is one dimension (the anchor); typed edges add the others. Querying the graph is how we *see* the system — clusters, what-connects-to-what, where the same job is done twice (the channel split, the three comment stores) — computed across the whole, never asserted by a context-blind agent.
- **The foundation of everything after.** It grounds the first build (finish/unify the channel system; build on the existing board UI into Tim's interface). It is itself what that interface renders — in tree/graph/filter views, state-as-colour, at-a-glance — so Tim directs by recognition, and annotates/comments on its nodes through the channel system. Built right, the ledger is a working instance, at smallest scale, of the architecture the whole system is meant to have, so Stage 3 is largely "grow it," not a separate build.

**Laws it serves:** no-partial · discovery-not-verification (the process *yields* what's there; it never checks against a pre-known set) · no-developer-burden (Tim directs by recognition; agents derive specifics) · recognition-not-dump · fuse-don't-separate · sequence-first (no conclusions/retain-replace/merge before the ledger exists).

---

## 2. THE BIG IDEAS (the design principles behind the shape)

1. **Facts vs. queries.** An agent may output *only what is certain from the file in front of it*. Anything needing the whole picture — duplicates, clusters, dead/live state, role, centrality, what-depends-on-X, the API surface, the event taxonomy, convention-violations-across-files, theme aggregation — is **derived by query afterward**, over the assembled graph, where full context exists and the answer can be trusted. A guess in a structured field is worse than nothing: it looks authoritative and poisons every query built on it.

2. **Deterministic vs. model.** Much of what we want is not a judgment call — imports, signatures, decorators, class bases, call references, constants/ports/paths, the contains-tree, line counts. For Python (the bulk) `ast` gives these *perfectly, zero hallucination*; JSON/SQL/systemd parse cleanly too. So **a deterministic harness extracts the structural facts (all files); the model is reserved for the interpretive layer it's uniquely good at.** Parsed facts are more trustworthy than any model's — this directly serves the trust requirement.

3. **No bias injected into discovery.** Agents are never given a checklist of *which* schemes/events/routes/themes to look for — that caps the answer at what I already know and biases it. They get **open fields** they fill with whatever they actually find (`address_schemes_used: [...]`, `apparent_themes: [...]`); the enumerating/matching is a later query.

4. **Self-extending.** The schema carries open fields (`extra`, `suggested_fields`, `proposed_edge_kinds`) so it grows from what the files reveal — recurring keys in `extra` are retro-promoted to real columns (gap-pressure applied to the ledger's own shape). Same as the Company's registries: self-describing, self-extending.

5. **Many faces, one substrate.** The same rows are queryable by **address** (path), **tree** (folder spine + depth), **type** (extension), **scheme** (`channel://`…), **symbol**, **relation** (the graph), and **meaning** (pgvector embeddings). They complement and combine — every view is a different query/projection over the one store.

6. **Graph for free.** Typed nodes + typed edges in Postgres = a graph natively (recursive SQL / a graph extension traverses it; custom logic via Postgres extensions). No separate graph build.

7. **Traceable & migratable.** Every row in every layer is stamped with this session's id + run/workflow id + pass + model + prompt/schema version + timestamp. The cheap pass-1/pass-2 layers and the prompts/schemas get the same stamp retro-applied. So the whole corpus is auditable to *this* session and migratable after the fact.

8. **Intention capture.** These files are AI-generated from Tim's idea-descriptions (he is not the developer, gives no specs). So the interpretive layer deliberately includes apparent themes/principles and intention signals — across hundreds of files these aggregate into *Tim's recurring patterns*, a capture of original intent. Flagged as inferred; trivially filtered out of results if noise.

---

## 3. THE TWO-LAYER EXTRACTION MODEL

- **Layer A — deterministic harness (ALL files, no model).** Parses each file (Python `ast`; TS/TSX parser; JSON/SQL/systemd/shell parsers) → structural facts + symbol rows + typed edges. Builds the complete factual graph in Supabase: every node, every edge, the whole tree. Incorruptible, cheap, total. Fixes "graph holes" — every edge resolves to a real node because every file has one.
- **Layer B — Opus interpretive (RELEVANT set only).** Reads the *originals* (not summaries), follows cross-references, and **upserts the interpretive + intention + embedding layer onto the rows Layer A already created** — the layer only a deep read gives. Opus spends its whole budget on understanding, never on re-typing what `ast` already knows.
- **(Optional) Layer B-lite** — a cheaper model (sonnet/haiku) can fill a thin interpretive layer for the non-relevant set later; not required (they already have complete deterministic facts, which suffices for graph + completeness).

Relevance cut happens between A and B: read the assembled facts (and the existing pass-1/pass-2 prose) to mark the relevant set. Cannot be known in advance — grounded in a description of every file, not a guess. Non-relevant keep their deterministic rows (coverage preserved).

---

## 4. THE SCHEMA (Supabase / Postgres + pgvector)

### Provenance — stamped on EVERY row, EVERY table
`produced_by_session` · `run_id` · `pass` · `model` (null for deterministic) · `prompt_version` · `schema_version` · `extracted_at`.

### TABLE `entry` — one row per file AND per folder

**Harness-computed (deterministic, no model):**
`path` (PK) · `parent` · `node_type` (file|folder) · `ext` · `language` · `size_bytes` · `line_count` · `source_hash` · `address` (path rel. to root) · `type_by_ext` · `depth`.

**Harness-extracted facts (deterministic where parseable):**
`imports` `[{target, internal|external, line}]` · `declares` (→ detailed in `symbol`) · `address_schemes_used` (open) · `stores_touched` (open, read|write) · `env_vars` (open) · `markers` (literal in-file signals, quoted: TODO/FIXME, "skeleton", "not wired", `__main__`/self-test present, "verified …").

**Measured structural signals (counts, not judgment — replaces "complexity"):**
`n_functions` · `n_classes` · `n_constants` · `n_imports` · `n_outgoing_edges` · `max_nesting_depth` · `n_branches` · `n_routes` · `n_events` · `has_entry_point`.

**Model factual (Opus / relevant set):**
`kind` (open) · `purpose` (docstring verbatim) · `what_it_does` (behaviour as written) · `inputs` · `outputs`.

**Model interpretive (Opus, strictly file-local, state-what's-uncertain):**
`observations` · `standouts` · `conventions` (followed or **broken**) · `concerns` (file-local smells only) · `notes` · `questions` (genuine unknowns *from this file alone*) · `purpose_vs_actual`.

**Pattern / intention layer (Opus):**
`apparent_themes` (open — "fail-loud", "registry-is-truth", …) · `intention_signals` (inferred original intent; flagged) · `novelty` (what's distinct/unusual here).

**Embedding faces (Opus-written text; pgvector columns):**
`summary_for_embedding` (the "what is this" vector) · `intention_for_embedding` (the "what was this *for*" vector).

**Open / self-extending:**
`extra` (k/v bag) · `suggested_fields` · `proposed_edge_kinds`.

### TABLE `symbol` — one row per function / class / method / type / const / route / component / registry-row / tool
`symbol_id` · `parent_path` · `name` · `symbol_kind` · `signature` · `params(+defaults)` · `returns` · `decorators[]` · `bases[]` · `line_span` · `is_exported` · `is_async` (all harness-deterministic where parseable)
\+ `does` (factual one-line) · `description` (rich symbol-level read — **for ALL symbols, public and private**, per Tim 2026-06-27) · `observations`/`notes` (optional, file-local) · `summary_for_embedding` (symbols independently searchable). Provenance-stamped.

### TABLE `edge` — the typed graph (outgoing only, per source; harness-built)
`{ from (path|symbol_id), kind, to (RAW target string), line, provenance }`
`kind` ∈ `contains` · `imports` · `calls` · `reads` · `writes` · `references` · `defines-route` · `calls-endpoint` · `emits-event` · `consumes-event` · `registers-tool` · `discovers-registry` · `raises` · `extends`.
`to` stays the **raw reference**; resolving it to the real node id is a later deterministic pass (the `resolve_address`-style normalization that turns strings into a traversable graph). New `kind`s allowed but recorded loudly (registry-style), never forced/dropped.

### Per-file-type additional fields (fold into entry/symbol)
- **Python:** functions/classes/constants/types_schemas → symbols; `registry_row {declared_name,id,fields}` (open); `registers_tool [{name,ops}]`; `exceptions {defined,raised}`.
- **Frontend (ts/tsx/js/mjs/cjs):** components(props→symbols); exports/hooks; `api_calls [{method,url,line}]`; `events_dom`; types_schemas.
- **JSON:** top_level_keys; `json_role` (open, `_schema`/`_note` quoted); references; `generated?` (only if literally signalled — huge generated files: record shape+size, don't deep-parse).
- **SQL:** tables[{name,columns}] · indexes · policies(RLS) · functions_triggers · migration_order.
- **systemd .service/.timer:** unit_name · exec_start · wanted_by · schedule.
- **Shell:** runs · env_set · services_started · entry.
- **Folder:** contains(children) · child_counts_by_type + a `contains` edge per child.

---

## 5. DERIVED BY QUERY — NOT agent output (the engine)
duplicates · clusters · state (dead/live/partial) · role · centrality · what-depends-on-X · API surface · event taxonomy · who-touches-`channel://` · cross-file convention-violations · theme aggregation (Tim's patterns) · completeness (paths with no/partial entry). All are SQL views / pgvector queries over the three tables. Pre-built views planned: completeness, duplications, cluster, by-state, neighbourhood, the-API-surface, the-event-taxonomy, themes.

---

## 6. HOW IT RUNS (the mechanism)
1. **Step 0** — verify the local Supabase container; find the existing connection path (`runtime/supabase_principal.py`, `build-prep/claude-design/supabase/` migrations + `.boundary.env`); stand up the schema (3 tables + provenance + pgvector). *Read-only verification + report before creating anything irreversible.*
2. **Layer A harness** — parse all files → upsert entry/symbol/edge rows (deterministic). Prove on one folder (e.g. `runtime/`) before going wide.
3. **Resolve edges** — normalize raw `to` strings to node ids (deterministic pass) → traversable graph.
4. **Triage** — read assembled facts + pass-1/pass-2 → mark relevant set.
5. **Layer B (Opus)** — relevant clusters, read originals, emit structured JSON (interpretive + intention + embeddings + symbol descriptions). **Validated single ingest path**: agents emit JSON → one deterministic step validates against schema (fail-loud on malformed) → upsert by path/symbol_id. Agents never hold DB creds; a bad record is rejected, never silently written.
6. **Engine** — build the SQL/pgvector views.
7. **Completeness loop** — query for paths/clusters missing entries → re-queue → repeat until the tree-diff is empty.
8. Coverage is run by a MIX matched to the work (the deterministic harness; the Company's local concurrent models; multiple Claude Codes; the dragnet; my own workflows/agents) — exactly which does which is learned as we go, not declared.

---

## 7. SCOPE & STATUS
- Scope: `/company` only for now. Cross-repo splinters (DNA/counterpart, visual-designer/ConceptV) are a later, separate territory.
- Markdown/prose files were deliberately not agent-described in the cheap passes. Open: whether/how prose gets ledger entries vs. the ledger being the inventory of *built things* (non-prose). To settle, not silently decided.
- Done so far: pass-1 (1,104 non-prose, light prose descriptions, coverage-gated) + pass-2 (629 code files, deeper prose, coverage-gated) under `build-prep/the-one-system/discovery/`. These are prose (an index), superseded by this structured-into-Supabase design but reused for triage + retro-stamped for traceability.

---

## 8. SUPERSESSION & INTEGRATION (decided 2026-06-27)
The ledger (`ledger.*` in the local Supabase) is the **canonical structural store**. The earlier experiments are superseded — one store, not parallels:
- `ops/code_archaeology.py`'s `.data/store/code_archaeology/ledger.jsonl` + `field_index.jsonl` → **superseded** by `ledger.entry` (deeper, non-flat, queryable, accumulating). `code_archaeology.py` is **kept** only because its `enumerate_files` (the real-tree coverage walk) is reused; its standalone capture run is retired.
- `design/_system/{code-symbols.json, code-edges.json, field_index}` → **superseded** by `ledger.symbol` + `ledger.edge`. **Re-pointing their consumers** (`codeedges.reach`/blast-radius, `refcheck`, `symbols.py`) onto the ledger is a **TRACKED FOLLOW-UP** — not done this pass, because those design-folder tools still work and re-pointing is its own change (don't break them mid-effort). Recorded so it isn't forgotten.
- **Address-spine integration:** `address_schemes_used` now flags **registered Company schemes** (`contracts/address.SCHEMES`). **TARGET (named, staged, not built this pass):** `code://` resolving *into* the ledger via `runtime/cognition.resolve_address`, replacing the second `Suite.resolve_scope`-over-JSON resolver — closing the "one resolver is actually two" gap and making the ledger reachable through the one spine.

## 9. SETUP (reproducible — the deterministic layer is product-complete)
- **Schema:** `build-prep/claude-design/supabase/supabase/migrations/0011_ledger.sql` (canonical, tracked, idempotent). Apply: `psql … -f 0011_ledger.sql` (or via the supabase migration flow).
- **Connection config — one env home** (defaults = the local docker Supabase): `COMPANY_LEDGER_PGHOST` (127.0.0.1) · `PGPORT` (15432) · `PGUSER` (postgres) · `PGDB` (postgres) · `PGPASSWORD`. Direct-DB superuser is the deliberate choice for the bulk build tool; the RLS `SupabasePrincipal` is for runtime app components.
- **Commands** (`ops/ledger_build.py`):
  - `--all --load` — extract the whole tree → a new accumulating run → health-gated.
  - `--incremental` — diff `source_hash` vs the latest run; **skip if unchanged**, else snapshot + delta report (the "maintained so it doesn't stale" path).
  - `--health` — the extraction-quality gate on the latest run.
  - `--show <file>` / `--folder <dir> --load` — prove one file / one folder.
  - run-identity: `--project --channel --purpose --session` (non-flat scoping).
- **Scheduled refresh:** `ops/systemd/company-ledger-refresh.{service,timer}` fire `--incremental` on a cadence (shipped **disabled**; the operator enables — `systemctl --user enable --now company-ledger-refresh.timer`).
- **Reproducibility:** every run stamps git sha + tool version + schema version; the migration is tracked; the tool is config-driven — a fresh checkout + the migration + the env defaults reproduces the ledger.
