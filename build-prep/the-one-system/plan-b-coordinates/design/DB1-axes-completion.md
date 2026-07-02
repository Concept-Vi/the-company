# Plan B design · take — the AXES-COMPLETION / DATA lens (2026-07-02)

*What must land, migrate, normalize, or be built BENEATH the coordinate query (companion to the query-lens
takes). Report verbatim below.*

All four anchors read, and I verified the load-bearing facts live (sqlite schemas, text volumes, sidecar shapes, the FsStore space census). Here is the design.

---

# PLAN B — DATA / AXES-COMPLETION LENS
*Design of everything that must land, migrate, normalize, or be built beneath the coordinate query. All counts Observed (executed 2026-07-02) unless tagged Inferred. No code here — specs and migration sketches.*

## Ground truth added by this lens (beyond R1/R2)

| fact | value | how observed |
|---|---|---|
| exchanges full text | 8,224 rows, **69MB** total; only 15 rows >100KB (2.4MB combined) | sqlite SUM(LENGTH) |
| tool_calls | 52,694 rows, **52MB** (input+result); schema: `id, exchange_id, tool_name, tool_input(JSON), tool_result, is_error, timestamp`; file_path only via `json_extract(tool_input,'$.file_path')` (an expression index exists) | .schema + queries |
| write-tool calls with file_path | **9,561** (Edit 6,997 · Write 2,564 · MultiEdit/NotebookEdit remainder) in the 1,254 indexed sessions | sqlite query |
| session archives on disk | **~10,411 jsonl files across 72 project dirs** in `~/.claude/projects` — the indexed 1,254 is **12%** of sessions | find/wc |
| recall sidecar record | per-line JSON: `{line, ts, attr, scale:"dimension", parent, text, vec[2560 floats as text]}`; meta: one session = **5,209 chunks**, keyed to source jsonl bytes/mtime (it is a **freshness-keyed cache**) | head of sidecar + meta |
| FsStore stranded spaces | `common_knowledge` 112 · `worldview` 324 · `principles` 324 · `operators` 58 = **818 files**, uniform shape `{address, vector, content_hash, dim, model, space, source, ts}` | ls + json read |
| scale sidecars | 12 files / 7 spaces (5 have stale non-`#emb` twins); extractions sidecar 8.9MB | ls -la |
| `common_knowledge` is live-load-bearing | it is the default space of `corpus(op='neighbours')` (`runtime/corpus_neighbours.py:87`, `mcp_face` docs) — post-① it is **unqueryable now** | grep |

---

## 1 · TRANSCRIPT PROVENANCE — completing the root axis

**The structural decision first (coordinates everything below): provenance is WORLD-FACT, not run-artifact.** The file_meta and generated-by strandings both happened because append-only truths were written into run-scoped rows and died at the next snapshot. So the provenance tables below are **run-exempt / append-only** — they never live under `*_latest` supersession. (Interface point with the SQL lens: their `unit_latest`/layered-view design must treat these tables as a persistent layer, coalesced by address, not picked by run.)

**1a. `ledger.exchange` — a dedicated table, not entry rows.** `entry` is snapshot-grain (a run's view of a file tree); exchanges are append-only conversation events. Forcing them into entry would either strand them (run-scoped) or corrupt entry's contract (mixed regimes). Dedicated table:

- Columns (from the verified sqlite schema): `address` PK (`exchange://<sid>/<line_start>`), `session_id`, `line_start/line_end`, `ts`, `project`, `cwd`, `git_branch`, `model`, `harness`, `is_sidechain`, `parent_uuid`, `cloned_from` (see §5.4), `archive_path`, **`user_text` + `assistant_text` IN Postgres**, plus `sqlite_id` (the md5 key, for reconciliation).
- **Text-in-pg verdict: yes, full text.** 69MB is trivial; pg TOASTs the 15 oversized rows automatically. `archive_path + line range` stays as the *re-derivation pointer and the sub-turn-grain handle* (§2), not as the read path — semantic hits must return their text without a filesystem hop, or the axis isn't composable.
- This gives `generated-by.to_resolved` a real target (today NULL ×1,403 — nothing to resolve against), gives provenance a time column, and makes `exchange://` first-class in the unit union.

**1b. `ledger.exchange_link` (23,608 links) + `ledger.tool_call` (52,694).** Links (`contains/precedes/produced_by/references`, all mechanical) become rows keyed by exchange address — either a dedicated table or `ledger.edge` rows in the persistent layer; my verdict: **into `ledger.edge`** with `exchange-` kinds, so graph traversal composes across code and conversation in one CTE — *provided* the persistent-layer view exists (SQL-lens interface; if their layering can't land in wave 1, a dedicated table is the fallback that avoids blocking). `tool_call` migrates whole (52MB): `exchange_address, tool_name, tool_input jsonb, tool_result, is_error, ts`, with a **stored generated column** `file_path = tool_input->>'file_path'` (pg-native equivalent of the sqlite expression index) + btree on it. Total pg growth for all of 1a+1b: **~130MB**. Fingerprint gap: 8,222 → 6,983 migrated; the migration re-run must **account for every skipped row** (null blob → re-embed queue; conflict → report), not leave 1,239 unexplained (fail-loud law).

**1c. generated-by beyond 2.5% — the full pipeline.** Current: 1,403 edges, 459 files (from the 1,254 indexed sessions). Verified headroom: 9,561 write-tool calls in 12% of sessions → **Inferred: order 50–80k write events across all ~10,411 sessions** (not verified; distribution across projects unknown).

- **Backfill (deterministic code, no model — per the standing law):** walk every session jsonl directly (do NOT wait for full recollection indexing of 10k sessions), extract `tool_use` blocks of the four write tools, emit `(file_path, exchange://<sid>/<line>, ts, tool)`. Normalize `file_path` → `code://<project>/<relpath>` via a **project-roots table** (cwd + registered roots + `.claude/worktrees/*` mapped to their repo). Write generated-by edges into the persistent layer; write **stub `ledger.exchange` rows** (address, sid, line, ts, archive_path; text NULL) for un-indexed sessions so `to_resolved` always lands — text backfills when/if recollection indexes that session.
- **Accounting is part of the output:** unmapped-root paths, renamed/deleted files, non-file writes → a counted discard report, and coverage reported as *measured %* of latest files, per project. 100% is unreachable (files created by `bash >`—redirects, pre-archive files, git operations) — say so in the number, never pad it.
- **Ongoing:** a Plan A job, change-triggered on `~/.claude/projects` mtimes, appends incrementally (high-water mark per session file). generated-by becomes each file's **authorship timeline** — which is also a TIME-axis input (§4).

## 2 · RECALL SIDECARS — the grain taxonomy, then the verdict

**The 3-grains problem dissolves into three orthogonal dimensions** — the "duplication" is a labeling failure, not a data failure:

| dimension | values | what it is |
|---|---|---|
| **GRAIN** (containment rungs of the one transcript axis) | g0 `session://<sid>` ⊃ g1 `exchange://<sid>/<line>` ⊃ g2 `exchange://<sid>/<line>#chunk=<n>` | the scale ladder of the provenance axis — exactly analogous to file↕symbol↕rung on the code axis |
| **LENS** | pplx-2560, bge-1024, … | which embedder looked at it |
| **SELECTION** | all · curated corpus | which subset a space carries |

So: `exchange` space = g1 × pplx × all; `history` space = g1 × {pplx,bge} × **curated** (a lens+selection, NOT a grain — stop treating it as a third copy); recall sidecars = g2 × pplx × 13 sessions. Registered this way, the three are layers of one axis and the query's `scale` stage applies to transcripts the same as to code.

**Verdict on the 809MB: LEAVE-WITH-POINTER, federate by contract, promote by job.** Reasons: (a) the meta file proves it's a **freshness-keyed cache** of a live jsonl (source_bytes/mtime) — migrating a cache manufactures staleness in pg; (b) 13/~10k sessions is arbitrary coverage, not an axis; (c) the bulk is JSON-text float bloat — the true payload is ~40k chunks × 2560 halfvec ≈ **~205MB** if ever promoted (Inferred from one meta's 5,209 chunks; not summed across all 13). Design: register g2 in the grain taxonomy with a **federation contract** — the query's transcript axis resolves g1 in pg; a g2 request routes to `session_recall` iff a sidecar exists, else fail-loud with the build command ("g2 index not built for <sid>; build: session_recall --index <sid>"). A Plan A **promotion job** can deliberately land chosen sessions' g2 into pg (`space='exchange:chunk'`) later. This is booked as conscious debt (risk 3).

## 3 · SCALE — membership into SQL, four new pyramids

**3a. `ledger.cluster_member`** (`cluster_address, member_address, space, k, emb, is_exemplar, parent_cluster_address`) loaded from the 7 canonical `#emb=pplx` sidecars (ignore the 5 stale bare twins). Row estimate: memberships = units × rungs → extractions 51,600×4 ≈ 206k; history ~4.4k; repo ~2k; topics/principles/worldview ~650 each; operators 58 → **≈ 215k rows total**. Load must reconcile counts per (space, rung) against the sidecar and raise on mismatch. After load the sidecars are **deprecated-in-place** (kept on disk, readers switched — the file analogue of Tim's comment-out rule); `build_scale_pyramid*` gains a row-writing output so no new sidecars are ever written.

**3b. The four missing pyramids.** Ladder rule (make it a Plan A job *parameter*, not a constant): ~4× fan-out per rung, finest rung averaging ~20–25 members, floor k≈4–8.

| space | N | emb / vec column | ladder | method |
|---|---|---|---|---|
| symbol | 6,201 | nomic-code / vec_3584 | **k256 / k64 / k16 / k4** | >4,000 → MiniBatchKMeans+Ward (existing path) |
| desc | 1,043 | pplx / vec_2560 | **k64 / k16 / k4** | Ward (exact) |
| code | 1,042 | nomic-code / vec_3584 | **k64 / k16 / k4** | Ward |
| docs | 679 | pplx / vec_2560 | **k32 / k8** | Ward |

Centroids land as ordinary embedding rows (`scale:<space>:k<K>`, in the *correct* dim column — note two of these are 3584, the first non-pplx rungs); membership lands as cluster_member rows in the same transaction.

**3c. Rebuild trigger (Plan A hook).** Each rung stores its `member_set_hash` (hash of sorted member addresses+source_hashes) at build. The pyramid job registers a change-trigger: heartbeat's re-embed stage completes → compare live member set hash vs stored → rebuild if drift > threshold (e.g. 5% or 25 units, parameters-as-data). Pyramids sit **last** in the heartbeat chain (change → extract → re-embed → joins → descriptions → **pyramids**). Staleness is thereby computable and loud, never inferred.

## 4 · TIME — the axis that must survive supersession

**Why file_meta died: it was enrichment written into run-scoped entry rows.** The redesign moves time facts to where they're keyed by their own truth, not by a run:

**4a. `ledger.file_change`** — append-only, keyed `(project, commit_sha, path)`: `address, committed_at, change_kind (A/M/D/R + rename_to), insertions, deletions, session_hint` (parsed from Co-Authored-By / commit-trailer when present — joins TIME to PROVENANCE). Loader = deterministic `git log --name-status` walk, **incremental by last-loaded sha per project** (a Plan A job; the backfill is the first run of the same job, not a separate script). Supersession-proof *by construction*: no run_id anywhere. `created_at / last_modified_at / change_count` become a **view** aggregating file_change — never stored per-run again. "Changed after T" = one indexed predicate. D/R rows double as **tombstones** for dangling-edge and provenance hygiene (risk 1's mitigation).

**4b. Run lineage.** `run_lineage` view: per `(project, purpose)`, runs ordered by `started_at` with `prev_run_id`. `run_delta` view: FULL OUTER JOIN of entry rows (run vs prev) on path, comparing `source_hash` → added/changed/removed. **Views first** (18 runs — cheap); materialize per-run at ingest only if measured slow. This also *is* the heartbeat's incremental contract (what changed since the last snapshot) — Plan A consumes it, don't build it twice.

**4c. Composition payoff:** `exchange.ts` (§1a) + `generated-by` + `file_change` closes the loop: "what did last Tuesday's conversation change, and what has changed since" becomes joins, not archaeology.

## 5 · ADDRESS normalization — per-case verdicts

**Principle: fix at source + one audited migration of stored rows; the resolver stays strict.** Normalize-at-query is rejected across the board — it's a permanent silent-fix layer masking divergence (anti-fail-loud). And the one systemic change worth more than every migration: **producer-side validation** — every writer to entry/edge/embedding parses the address through `contracts/address.py` before write and raises on failure. Divergence then cannot recur.

| # | case | verdict |
|---|---|---|
| 1 | `repo` space absolute paths (`code:///home/tim/company/…`, 1,296 rows incl. bge) | fix producer (repo-corpus ingest, `mcp_face/tools/ingest.py`) + deterministic prefix-rewrite migration → `code://company/<path>`; paths outside registered roots → loud list, decide individually |
| 2 | `topics` bare tokens + project-less forms (329 rows, mixed with legit `anchor://`) | one-shot audited migration: rewrite resolvable (`code://fabric/…` → `code://company/fabric/…`), quarantine-or-delete irresolvable, with a per-row accounting report — small enough to be exhaustive |
| 3 | `deferred://` + `memory://` unregistered | **register in SCHEMES** (address.py documents SCHEMES as purely additive) — they're real schemes of the memory system; no data rewrite |
| 4 | clone-nested `exchange://clone://<sid>/uuid:<u>/0` | **flatten the address, move lineage into data**: canonical `exchange://<clone_session_id>/<i>` + a `cloned_from` column on ledger.exchange. Nesting in an address string is grammar debt; lineage is a relation. Migrate the few stored rows |
| 5 | `entry.parent` bare path | fix at source (ingest writes `parent_address`) + backfill migration; deprecate bare `parent` in the view (SQL-lens call on column retirement) |
| 6 | lossy `code://<stem>/<symbol>` sidecar | ② scope — nothing to migrate; the canonical symbol addresses already exist (12,681 latest); never import the lossy forms |

## 6 · The 4 stranded unit spaces — the ①-cutover debt (URGENT)

**This is live breakage, not debt**: `common_knowledge` is the *default space* of `corpus(op='neighbours')`, and post-① those 818 vectors are unreachable (FsStore read retired, rows never copied — their *rungs* migrated, their *units* didn't). Fix: re-run `ops/migrate_vectors_to_supabase.py --space` for `common_knowledge (112) / worldview (324) / principles (324) / operators (58)`. The file shape maps 1:1 (`source→source_address, space, model→emb_layer, dim→vec_<dim>, ts`). **Reconciliation is mandatory**: per (space × emb), disk count == pg count or raise — this exact class of hole (rungs in, units out) is what un-reconciled migration produces.

## 7 · HYGIENE — purge + tripwire

- **Purge:** (a) DELETE `space LIKE '__root_%'` (140 rows — the namespace already isolates new test writes, so deletion is clean); (b) legacy junk in production spaces: `model IN ('seed','stub','synthetic') OR dim NOT IN (1024,2560,3584)` → **archive the rows to a purge-log first, then delete** (record-or-raise, never silently drop); (c) fold/purge the singular ghost spaces (`topic`, `principle`, `__default__`) in the same audit.
- **Prevent re-pollution:** (a) a CHECK/trigger on `ledger.embedding`: dim must be a registered layer and model a registered embedder **unless** space starts `__root_` (the sanctioned sandbox); (b) a post-suite tripwire test that scans production spaces for test-signature rows and fails red — enforcement, not convention.

## 8 · ORDER — the waves

| wave | contents | why here |
|---|---|---|
| **0 — unbreak live** (hours) | §6 stranded spaces · §7 purge+tripwire | restores the live vector path; cleans the stats every later wave measures against. Zero design dependencies |
| **1 — the join fabric** | supersession fix / persistent-provenance layer (SQL-lens interface — un-strands generated-by, 30 organic kinds, and hosts everything in §1/§4) · §5 address migrations + producer validation | **this is what the query function blocks on** — without it, 3 axes are invisible and joins mis-key |
| **2 — new tables** (3 parallel lanes) | `exchange`+`exchange_link`+`tool_call` (§1a-b) ∥ `cluster_member` load (§3a) ∥ `file_change` loader (§4a) | independent lanes; each is an additive CTE stage — the query function can ship after wave 1 and gain axes as these land |
| **3 — derivations** | generated-by full backfill (§1c) ∥ 4 pyramids (§3b) ∥ lineage/delta views (§4b) | each depends only on its wave-2 lane |
| **4 — ongoing (Plan A hooks)** | pyramid rebuild triggers (§3c) · incremental recollection sync · incremental git loader · g2 federation contract + promotion job (§2) | the maintenance regime; jobs, not scripts |

## The 3 biggest risks of THIS design — honestly

1. **Two temporal regimes in one ledger.** The persistent/append-only layer (exchange, file_change, generated-by) versus run-scoped snapshots is my central move, and it's a per-table classification *I* made. If the SQL lens's layered views don't encode the boundary exactly, we recreate the stranding one level up — or its inverse, **ghost data that never expires** (generated-by pointing at files deleted three snapshots ago, presented as current). Mitigation is file_change tombstones, but that's a join discipline every consumer must apply, and disciplines erode.
2. **The backfill coverage number can rot silently.** cwd-relative → `code://<project>/<path>` mapping across 72 project dirs, worktrees, renames, deletions: my "loud discard accounting" prevents *silent* loss, but if the roots table is thin the pipeline can loudly discard the majority and still be called done. The 50–80k estimate is Inferred from a 12% sample; and a real fraction of the 18,655 files may be unreachable by any archive. The deliverable must be a **measured coverage % with the discard ledger attached**, and I may be over-promising the ceiling.
3. **The federated g2 grain breaks the one-function purity.** Leaving recall sidecars outside pg makes transcripts the only axis whose finest grain needs an escape hatch out of SQL. If the query lens builds a pure `ledger.query(spec)` PL/pgSQL function (R2's verdict), g2 either drops out of the composable space (axis incompleteness) or forces a second query path (exactly the sprawl this system exists to kill). The promotion job is the repayment plan — but it's deferred debt I am choosing to book, and I've said so rather than hidden it.

**Interface points for the SQL/query lens** (so the seams are explicit): the layered `unit_latest` semantics for the persistent layer (wave 1); whether exchange_link lands in `ledger.edge` or a dedicated table; the unit-union view (`entry ∪ exchange ∪ …`) that gives `to_resolved` its targets; column retirement for `entry.parent`.
