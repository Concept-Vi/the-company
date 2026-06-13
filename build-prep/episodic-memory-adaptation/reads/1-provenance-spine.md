# THE PROVENANCE SPINE — Read 1 (memory-merge fleet)

> **What this read establishes.** There is a single, latent, *already-built* graph that connects **every generated artefact in every system Tim runs** back to the moment it was created **in conversation** — through the tool-call that wrote it, the exchange it sat inside, the session, the wall-clock timestamp, and the other parallel sessions running at that same moment. That graph is not "designed" yet as a joined product, but **both halves of it physically exist on disk today and the join runs live** (verified, queries below). This document is the spine all other reads hang from.
>
> **Evidence discipline.** Every statement below is tagged **Observed** (read in code / queried against the live DB), **Verified** (I ran it and saw the result), or **Inferred** (pattern-match, NOT yet executed — flagged loud). No "probably/likely" stands unqualified.

---

## 0. THE LENS (Tim's intentional architecture — the frame this read serves)

There is a **clean split** between two classes of data across all of Tim's systems:

1. **THE CONVERSATION STORE** — the raw Claude Code transcripts (`*.jsonl` under `~/.claude/projects/...`), indexed into the episodic-memory SQLite DB. This is **the ONLY primary source**. Nothing in it was *authored* by Claude as a deliverable — it is **the record of what happened**: Tim's exact words, the assistant's exact replies, and (critically) **every tool call that was fired**, with its inputs.

2. **ALL OTHER CONTENT, in every system** — every corpus record, every Obsidian note, every Supabase row, every code file, every design doc, every `build-prep/` artefact. **None of it was hand-written or reviewed or read by Tim.** Every one is a **generated output** — and every generated output was produced *by a tool call inside an exchange inside a session at a timestamp*.

The consequence Tim is pointing at: **the conversation store is not just searchable memory. It is the genesis-ledger.** Because the tool-call inputs contain the **addresses of the artefacts** (the file paths written/edited), there is a latent **provenance graph**:

```
generated artefact (a file, anywhere)
      ▲
      │  its path appears in
      │
   tool_call  (Write / Edit / MultiEdit / NotebookEdit …)
      ▲
      │  belongs to (FK exchange_id)
      │
   exchange   (one Tim-message + assistant reply)
      ▲
      │  carries
      │
   session_id · timestamp · cwd · git_branch · project
      ▲
      │  co-occurs in time with
      │
   N OTHER parallel sessions  (Tim was doing many things at once)
```

This read documents: **(A)** the full conversation-store schema, **(B)** the `tool_calls → artefact-address` mechanism with live example rows, **(C)** the Company-side anchoring (`source_address` / `ts_source`) that *already* puts generated corpus records on the same `exchange://` coordinate system, and **(D)** the synthesized design for **THE JOIN** — re-anchoring all generated content to its transcript genesis — plus what is **dormant/unbuilt**.

---

## A. THE CONVERSATION STORE — FULL SCHEMA (every table, every column, annotated)

**Source of truth (two, and they agree):**
- Schema-definition code: `/home/tim/.claude/plugins/cache/superpowers-marketplace/episodic-memory/1.0.15/src/db.ts` — **Observed** (read lines 8–130).
- Live database: `/home/tim/.config/superpowers/conversation-index/db.sqlite` — **Verified** (`.schema` + `.tables` run readonly).

**Live tables (Verified — `.tables`):**
```
exchanges                      tool_calls                     vec_exchanges
vec_exchanges_chunks           vec_exchanges_info             vec_exchanges_rowids
vec_exchanges_vector_chunks00
```
(The `vec_exchanges*` set are the internal shadow tables of the `sqlite-vec` virtual table; only `vec_exchanges` is the logical one.)

**Live row counts (Verified):**
- `exchanges`: **75,397 rows** (the inventory's ~75,374 figure — grows continuously; latest exchange timestamp `2026-06-11T12:10:05Z`).
- `tool_calls`: **6,719,356 rows** (inventory said ~6,713,952 — same order, grows live).

### A.1 — Table `exchanges` (the unit of conversation: one Tim-turn + reply)

This is the central table. **18 columns.** (Tim's "~16–19 columns" claim — **Verified: exactly 18 on `exchanges`**; the `tool_calls` table is the one holding tool calls and has **7** — see A.2. The 16–19 intuition maps to `exchanges`.)

| # | Column | Type | Annotation (Observed from db.ts + live `.schema`) |
|---|--------|------|---------------------------------------------------|
| 1 | `id` | TEXT **PK** | The exchange's unique id (a UUID-shaped key). The hub every tool_call FKs to. |
| 2 | `project` | TEXT NOT NULL | The project slug, e.g. `-home-tim` (derived from the transcript dir). **96 distinct** (Verified). |
| 3 | `timestamp` | TEXT NOT NULL | ISO-8601 of the exchange (e.g. `2026-05-31T06:41:56.461Z`). **The wall-clock anchor.** Indexed DESC. |
| 4 | `user_message` | TEXT NOT NULL | **Tim's exact words** for this turn (primary source). |
| 5 | `assistant_message` | TEXT NOT NULL | The assistant's exact reply text. |
| 6 | `archive_path` | TEXT NOT NULL | Absolute path to the source `*.jsonl` transcript file on disk. **The link back to the raw record.** |
| 7 | `line_start` | INTEGER NOT NULL | First line in the `.jsonl` this exchange spans. |
| 8 | `line_end` | INTEGER NOT NULL | Last line — together with `line_start`, the exact byte-region of the raw transcript. |
| 9 | `embedding` | BLOB | A 384-dim float vector stored inline (also mirrored into `vec_exchanges`). Enables semantic recall. |
| 10 | `last_indexed` | INTEGER | `Date.now()` epoch ms of last index — the incremental-reindex watermark. |
| 11 | `parent_uuid` | TEXT | The parent message UUID from the transcript — lets you reconstruct the message tree / threading. |
| 12 | `is_sidechain` | BOOLEAN DEFAULT 0 | **1 = this exchange happened inside a sub-agent / Task sidechain**, not the main thread. (Distinguishes Tim-facing turns from agent-internal ones.) Indexed. |
| 13 | `session_id` | TEXT | **The session this exchange belongs to.** The grouping key for "one continuous Claude Code run." Indexed. **7,351 distinct sessions** (Verified). |
| 14 | `cwd` | TEXT | Working directory at the time (e.g. `/home/tim/company`, `/home/tim/vllm-tests`). **292 distinct** (Verified) — a coarse "what was I working on" facet. |
| 15 | `git_branch` | TEXT | Git branch at the time (e.g. `HEAD`, `operable-surface`). Indexed. Another genesis-context facet. |
| 16 | `claude_version` | TEXT | The Claude Code version that produced the exchange. |
| 17 | `thinking_level` | TEXT | Extended-thinking level for the turn (migration-added). |
| 18 | `thinking_disabled` | BOOLEAN | Whether thinking was off. |
| (19) | `thinking_triggers` | TEXT | Trigger metadata for thinking (migration-added). |

> **On Tim's "~16–19 columns" — Verified resolution:** the original `CREATE TABLE` (db.ts lines 57–79) defines columns 1–18 *plus* `thinking_triggers` listed last in the live schema, giving the **18–19** count depending on whether you count `embedding`. The migration block (db.ts lines 12–23) shows columns 10–19 were **added over time** (`ALTER TABLE … ADD COLUMN`), which is exactly why the count is "around" a number rather than fixed — the schema is **additive/evolving**. This matters for the merge: **a future Claude Code version may add more columns**; any join must tolerate schema drift.

**Indexes on `exchanges` (Observed, db.ts 107–121 / Verified `.schema`):**
`idx_timestamp(timestamp DESC)`, `idx_session_id`, `idx_project`, `idx_sidechain`, `idx_git_branch`. (Note: **no index on `archive_path`** and **no index on `cwd`** — relevant for join-performance planning.)

### A.2 — Table `tool_calls` (THE column-set that holds the artefact addresses)

**7 columns.** This is the table Tim is pointing at — "ONE [column] holds the TOOL CALLS, and tool-call inputs contain THE ADDRESSES OF ARTEFACTS." Precisely: the table holds one row per tool call, and the **`tool_input` column** (a JSON string) contains the artefact address.

| # | Column | Type | Annotation (Observed db.ts 82–93 / Verified `.schema`) |
|---|--------|------|--------------------------------------------------------|
| 1 | `id` | TEXT **PK** | The tool_call's unique id (the transcript's `tool_use` block id). |
| 2 | `exchange_id` | TEXT NOT NULL **FK→exchanges.id** | **The spine joint.** Every tool call points back to the exchange it fired in. Indexed (`idx_tool_exchange`). |
| 3 | `tool_name` | TEXT NOT NULL | `Write`, `Edit`, `Bash`, `Read`, `Agent`, `mcp__…`, etc. Indexed (`idx_tool_name`). |
| 4 | **`tool_input`** | TEXT | **★ THE ARTEFACT-ADDRESS FIELD.** A JSON string of the tool's parameters. For `Write`/`Edit`/`MultiEdit`/`NotebookEdit` it contains **`"file_path": "<absolute path of the artefact>"`** — the address of the thing that was written/edited. |
| 5 | `tool_result` | TEXT | The tool's return value. **★ DORMANT: 100% NULL** (see A.4). |
| 6 | `is_error` | BOOLEAN DEFAULT 0 | Whether the tool call errored. |
| 7 | `timestamp` | TEXT NOT NULL | ISO-8601 of the tool call itself (finer-grained than the exchange ts — e.g. `2025-12-20T20:49:23.573Z`). |

**FK:** `FOREIGN KEY (exchange_id) REFERENCES exchanges(id)` (Observed db.ts 91).

### A.3 — `tool_name` distribution (Verified — top 25 of 6.7M rows)

This is the *shape of the work*: it tells you which tool-kinds produce artefacts (the address-bearing ones) vs which are reads/coordination.

```
Bash                              2,272,348      Glob                                 38,016
Read                                941,973      mcp__chrome-devtools__take_snapshot  37,653
Edit                                859,307      Task                                 37,014
Write                               303,169      mcp__obsidian__patch_note            35,565
Grep                                274,933      TodoWrite                            34,140
TaskUpdate                          253,491      mcp__langflow-builder__configure     32,924
Agent                               235,155      mcp__langflow-control-plane__author  30,052
TaskCreate                          152,377      mcp__langflow-builder__connect       28,135
mcp__supabase__execute_sql          139,757      mcp__langflow-builder__add_node      23,675
SendMessage                         112,476      mcp__voicemode__converse             23,451
ToolSearch                          102,401
mcp__chrome-devtools__evaluate_script 65,121
mcp__chrome-devtools__take_screenshot 60,522
mcp__chrome-devtools__click          41,840
mcp__chrome-devtools__navigate_page  40,497
```

**The artefact-writing tools** (the ones whose `tool_input.file_path` is a filesystem artefact address):
- `Edit`: **859,307** rows · of which **859,297 carry `"file_path"`** (Verified) — 99.999%.
- `Write`: **303,169** rows · of which **303,080 carry `"file_path"`** (Verified) — 99.97%.
- `NotebookEdit`: present (uses `notebook_path`).
- `MultiEdit`: **1** row in this DB (legacy; uses `file_path` + `edits[]`).

> **Other systems also leave addressed write-traces in `tool_input`** (Inferred from tool_name list, not yet field-parsed): `mcp__supabase__execute_sql` (139,757 — the SQL/migration text → Supabase rows), `mcp__obsidian__patch_note` (35,565 — the note path → Obsidian vault), `mcp__langflow-*` (the flow id → Langflow graphs). **So the "artefact address" generalizes beyond filesystem paths** to per-system identifiers carried in each MCP tool's input JSON. *I have not yet parsed those input shapes — flagged for a follow-up read.*

### A.4 — ★ DORMANT: `tool_result` is 100% NULL (Verified — confirms the inventory)

```
SELECT COUNT(*), SUM(tool_result IS NULL), SUM(tool_result IS NOT NULL) FROM tool_calls;
→ 6,719,356 total | 6,719,356 NULL | 0 non-null      (Verified)
```

**Every one of the 6.7M tool_result cells is NULL.** The episodic-memory indexer (`src/db.ts` line 195, `toolCall.toolResult || null`) is *structured* to capture results, but the upstream parser is **not populating them** — so the entire "what did the tool return / what was the artefact's content at write-time" axis is **captured-as-schema but empty-in-fact**. This is the single biggest dormant capability in the conversation store: the *inputs* (addresses) are rich; the *outputs* (the written content, command stdout, query results) are blank.

### A.5 — ★ Verified: the artefact→genesis JOIN runs TODAY on live data

The whole spine reduces to one SQL join. I ran it readonly:

```sql
SELECT tc.tool_name, tc.timestamp AS tool_ts, e.session_id,
       e.timestamp AS exch_ts, e.cwd, e.git_branch, e.project,
       substr(e.user_message,1,90) AS user_msg
FROM tool_calls tc
JOIN exchanges e ON e.id = tc.exchange_id
WHERE tc.tool_name='Write'
  AND tc.tool_input LIKE '%/home/tim/company/%'
LIMIT 3;
```
**Verified output (real rows):**
```
Write | 2026-05-31T06:39:31Z | 7c2c1b74-…-2ca | 2026-05-31T06:41:56Z | /home/tim/vllm-tests | HEAD | -home-tim | "Go for it"
Write | 2026-05-31T07:17:03Z | 7c2c1b74-…-2ca | 2026-05-31T07:22:39Z | /home/tim/vllm-tests | HEAD | -home-tim | "1"
Write | 2026-05-31T07:17:28Z | 7c2c1b74-…-2ca | 2026-05-31T07:22:39Z | /home/tim/vllm-tests | HEAD | -home-tim | "1"
```

So for **any artefact path**, this returns: **which tool wrote it → at what tool-time → in which session → in which exchange (with Tim's exact prompt) → in which cwd / branch / project.** That is the entire spine, and it is **queryable now**.

And the concrete example rows of the address field itself (Verified):
```
Edit  {"file_path":"/mnt/c/00_ConceptV/06_Project_Vi/repos/Supabase/supabase/files/content_display.html", "old_string":"…case 'faq':…", "new_string":"…"}   ts=2025-12-20T20:49:23Z
Edit  {"file_path":"…/content_display.html", "old_string":"…case 'card'…", …}                                                                                 ts=2025-12-20T21:03:46Z
Edit  {"file_path":"…/content_display.html", "old_string":"…BLOCK RENDERER…", …}                                                                              ts=2025-12-20T21:09:37Z
```
**The artefact's address is `JSON_EXTRACT(tool_input, '$.file_path')`.** Three consecutive edits to the *same* file, minutes apart, in one session — i.e. the spine also reconstructs the *edit history* of a single artefact across its life.

### A.6 — ★ Verified: the PARALLEL-ACTIVITY dimension is real and large

Tim's claim — "Tim was doing multiple different things across parallel sessions at that time" — is **Verified, and the magnitude is striking**:

```sql
SELECT substr(timestamp,1,15) AS window, COUNT(DISTINCT session_id) AS concurrent
FROM exchanges GROUP BY window ORDER BY concurrent DESC LIMIT 5;
→ 2026-04-10T09:51 | 263 concurrent sessions
  2026-04-10T10:06 | 258
  2026-04-10T10:17 | 208
  2026-04-04T04:01 | 197
  2026-04-04T04:11 | 175
```
At peak, **263 distinct sessions** were active within a single ~10-minute window. Span of the whole store: `2025-11-10T01:17:50Z → 2026-06-11T12:10:05Z` (Verified), across **7,351 sessions · 96 projects · 292 cwds**. So "when in time" is not a thin facet — it is a **dense, multi-stream timeline**. An artefact's genesis-moment is surrounded by a knowable *constellation* of other concurrent work (other sessions whose `timestamp` overlaps), which is itself recoverable: `SELECT DISTINCT session_id FROM exchanges WHERE timestamp BETWEEN <t-Δ> AND <t+Δ>`.

### A.7 — The vector tables (`vec_exchanges*`)

`CREATE VIRTUAL TABLE vec_exchanges USING vec0(id TEXT PRIMARY KEY, embedding FLOAT[384])` (Observed db.ts 97–101). Backed by `sqlite-vec`'s shadow tables (`_info`, `_chunks`, `_rowids`, `_vector_chunks00`). Embedding dim **384** (a MiniLM-class local model — Inferred from the dim; not the Company's jina-v4). This means **the conversation store is already semantically searchable on its own** — independent of the Company corpus. Two embedding spaces exist (this 384-dim store-side index, and the Company's history-space embeddings); a merge must decide whether they stay separate or reconcile (open — flagged for the merge-design read).

---

## B. THE COMPANY SIDE — generated records ARE ALREADY anchored to `exchange://` + time

The second half of the spine: on the Company side, **generated corpus records already carry their genesis address and genesis time.** The anchoring is not aspirational — it is enforced and populated.

### B.1 — `source_address` = `exchange://<session_id>/<i>` (Observed + Verified)

The miner that turns transcripts into durable memory writes each record keyed by its source exchange. From `/home/tim/company/build-prep/cognition-self-improvement/g23_mine.py` (Observed):

```python
records = [{"source_address": f"exchange://{sid}/{new[j][0]}",
            "output": dict(out, ts_source=new[j][1].get("ts")),
            "projection": "history"}
           for j, out in sorted(resolved.items()) if isinstance(out, dict)]
```

- `sid` = the **session_id** (same id space as `exchanges.session_id`).
- `new[j][0]` = the **positional index `i`** of the exchange *within that transcript*, assigned by the deterministic walk in `transcript_extract.py` (Observed: `extract_exchanges` enumerates exchange units in file order; index `i` is the durable per-exchange key, see g23 docstring "index i is a durable per-exchange key for a SETTLED file").
- So **`exchange://<sid>/<i>` is the Company's address for one conversation exchange** — the *same coordinate* the episodic store keys by (session + position).

> **⚠️ Join-key caveat (Observed, important):** the episodic-memory DB keys exchanges by an opaque `id` (UUID) and stores `session_id`, but does **NOT** store the positional index `i`. The Company keys by `(session_id, i)` where `i` is *its own* deterministic enumeration. These two enumerations are **not guaranteed identical** unless both walk the transcript with the same exchange-boundary rule. `transcript_extract.py` has a specific boundary rule (Observed: a `tool_result` rides as `type='user'` but must NOT start a new exchange — lines in `_is_tool_result_record`). Whether episodic-memory's indexer uses the *same* boundary rule is **UNVERIFIED** — this is a **concrete reconciliation risk for the merge** (the same exchange could get index 39 on one side and 41 on the other). Flagged loud.

### B.2 — `ts_source` = the ORIGINAL exchange timestamp (Observed + Verified live)

The miner stamps each record with the **source exchange's own timestamp**, not the capture time:

```python
"output": dict(out, ts_source=new[j][1].get("ts"))   # g23_mine.py (Observed)
```

Why it matters (Observed, from `flows/ts_backfill.py` docstring): *"capture-ts can't partition by period (the whole corpus was captured in two days)."* The capture happened in a burst; `ts_source` re-attaches each record to **when it was actually discussed** — the forager's time-period facet.

**Verified live (queried the running corpus):**
- `history` records total: **1,464**; with `exchange://` source_address: **1,459**.
- Of the first 400 inspected, **400/400 carry `ts_source`** (e.g. `2026-05-31T13:28:03Z`). The `ts_backfill` flow has clearly run — the research's original "only 173/1,420 carry ts_source" gap is **largely closed** (Observed: `ts_backfill.py` exists precisely to re-stamp the rest, deterministically, no model, latest-seq-wins supersession).
- The record `output` shape is the mined-exchange schema (Verified keys): `{bug_fix, decision, frustration, my_error, needs_tim, pattern_tag, rationale, tim_correction}` + `ts_source`.

### B.3 — The corpus record contract: lineage is a FAIL-LOUD GATE (Observed)

From `/home/tim/company/runtime/corpus.py` (Observed, the headline of the module):

- **Required fields** (line 69): `REQUIRED_RECORD_FIELDS = ("source_address", "output", "kind", "lineage")`.
- **Lineage axes** (line 73): `LINEAGE_FIELDS = ("session", "round", "project")` — **all three REQUIRED at write**, refused fail-loud if missing (`_validate_lineage`, lines 97–119). Rationale (Observed docstring PART 4.7): *"A record written WITHOUT lineage can never be corroborated cross-session — so retrofitting lineage after a capture run is a full re-capture."*
- **Deterministic address** (line 84): `corpus_address()` → `run://corpus/<project>/<source_address>[/<projection>]` — resume-safe, idempotent (write-once cas + deterministic pointer).
- **Three distinct lineage axes — DO NOT conflate** (Observed, lines 17–24):
  1. **corpus lineage** (`session/round/project`) — the *capture* provenance (which run produced the record).
  2. **store provenance-lineage** (`store.lineage()`) — the *inputs an artefact was made from* (a different axis).
  3. **decision-lineage** (`decision_view`) — the event-trajectory of a decision.

> **Key distinction for the merge:** the Company's `source_address`/`ts_source` answers *"which conversation exchange + when did this generated record come from."* That is **exactly the same question** the episodic store's `tool_calls → exchanges` join answers for *filesystem artefacts*. **The two halves are the same spine, approached from opposite ends** — Company records point *down* to their genesis exchange; the episodic store points *up* from a written file to its genesis exchange. They meet at the exchange.

### B.4 — Read-side: how the Company reads anchored records (Observed)

- `find_corpus(projection='history')` / `find_corpus(source_address=…)` in `runtime/corpus.py` (lines 230–242) — a read-time projection over the event log filtered to `kind=='corpus.record'`, narrowable by `source_address`. So **given an `exchange://<sid>/<i>`, the Company can already fetch every generated record minted from that exchange** (Verified the API exists and the data is present).
- `flows/ts_backfill.py` (Observed) round-trips the address: it parses `exchange://<sid>/<i>` back into `(sid, i)`, re-walks the transcript, and re-stamps — proving the address is a **two-way** key (record ⇄ source exchange).
- **No code in `~/company` currently reads the episodic-memory `db.sqlite` directly** (Verified grep: the only `tool_calls` hits in company are *test fixtures* for the RHM model-tool-call parser and `ops/cli/capabilities.py` checking an LLM response — **none touch the conversation-index DB**). **The cross-system join does not exist in code yet.** The Company mines transcripts *itself* (via `transcript_extract.py` walking the `.jsonl` files), entirely independent of the episodic DB.

---

## C. THE JOIN — synthesized design (re-anchoring all generated content to its transcript genesis)

This is the merge's center of gravity. Both halves exist; **the join between them is unbuilt.** Here is the design, grounded in the verified facts above.

### C.1 — The unifying coordinate

Everything keys to **the exchange**, addressed two compatible ways:
- Episodic store: `exchanges.id` (UUID) + `(session_id, timestamp, archive_path, line_start..end)`.
- Company corpus: `exchange://<session_id>/<i>`.

The bridge key is **`session_id`** (shared, identical id space — Verified both use the transcript's session UUID) plus a **position/time reconciliation** between the episodic `id`/`timestamp` and the Company `i`/`ts_source`.

### C.2 — The full re-anchoring chain (the product)

For **any generated artefact, in any system**, the join answers *"where did this come from?"*:

```
ARTEFACT (a file path, a Supabase row, an Obsidian note, a corpus record)
  │
  ├─ if it's a FILESYSTEM file:
  │     find the tool_call:  SELECT * FROM tool_calls
  │                          WHERE JSON_EXTRACT(tool_input,'$.file_path') = :path
  │                          ORDER BY timestamp           ← whole edit-history of the file
  │     → exchange_id → JOIN exchanges → session_id, timestamp, cwd, git_branch,
  │                                       user_message (Tim's exact ask), assistant_message
  │     → the parallel constellation:  SELECT DISTINCT session_id FROM exchanges
  │                                     WHERE timestamp BETWEEN t-Δ AND t+Δ
  │
  ├─ if it's a CORPUS record (Company):
  │     it ALREADY carries source_address = exchange://<sid>/<i> + ts_source
  │     → resolve <sid> to episodic exchanges (session_id match)
  │     → reconcile <i> ↔ episodic exchange via timestamp/position
  │     → now it ALSO inherits the tool_calls of that exchange (what else was written then)
  │
  └─ if it's a Supabase row / Obsidian note / Langflow graph:
        its write rode an MCP tool_call (mcp__supabase__execute_sql / mcp__obsidian__patch_note / …)
        → parse that tool's input JSON for the row/note/graph identifier  (UNBUILT per-tool parser)
        → exchange_id → exchanges → same genesis chain as above
```

The result is a **bidirectional index**: *artefact → genesis exchange* AND *exchange → all artefacts it produced*. An exchange becomes a hub showing: Tim's exact words, the reply, **and every file/row/note that turn created**, plus the surrounding parallel work.

### C.3 — Minimal buildable shape (Inferred design — not yet built)

1. **A read-only attach.** The join needs no migration: `sqlite3` can `ATTACH` the conversation-index DB read-only, or a Python reader can query it. The Company's `find_corpus` already returns `source_address`; a new bridge module would resolve those to episodic exchange rows. *(Inferred: feasible with zero writes to either store; I have not built or run it.)*
2. **A `file_path → tool_call` reverse index.** `JSON_EXTRACT(tool_input,'$.file_path')` is not indexed; with 1.16M Write+Edit rows a generated-column index (`ALTER TABLE tool_calls ADD COLUMN fp TEXT GENERATED ALWAYS AS (json_extract(tool_input,'$.file_path')) VIRTUAL; CREATE INDEX …`) would make artefact-lookup O(log n). *(Inferred — would be a write to the episodic DB, so likely belongs in a Company-side mirror, not the upstream DB which gets overwritten on plugin update.)*
3. **The `(session_id, i)` ↔ episodic-`id` reconciliation table.** The one genuinely hard piece (see B.1 caveat): align the Company's positional `i` with the episodic store's exchange enumeration. Cleanest path (Inferred): re-walk each transcript *once* with `transcript_extract.py`'s boundary rule, and for each `i` record `(line_start, line_end, ts)`; match to episodic `exchanges` rows by `session_id + line overlap` (the episodic store HAS `line_start/line_end` — column 7/8). **This makes the line-region the true bridge** and sidesteps any boundary-rule mismatch. *(Inferred — not built; I verified the columns exist on both sides to support it.)*

### C.4 — Why this is the spine, not just a feature

- **Every generated record in every system is re-groundable to primary source.** The merge isn't "better search" — it's *provenance for the entire generated corpus*. A claim in a build-prep doc, a row in Supabase, a note in the vault: all become traceable to *the conversation turn that authored them, what Tim actually said, and when*.
- **It re-anchors content to TIME and to PARALLEL CONTEXT.** Because of A.6, an artefact isn't just "made on date X" — it sits in a knowable web of *what else Tim was doing in those minutes*. That is the substrate for "what was the bigger picture when this was written."
- **It closes the loop the Company already half-drew.** `corpus.py`'s lineage gate exists *because* cross-session corroboration needs genesis. The episodic store *is* the cross-session genesis ledger. They were built to meet; the meeting is the merge.

---

## D. WHAT IS DORMANT / UNBUILT (fail-loud honest status)

| Item | Status | Evidence |
|------|--------|----------|
| `tool_result` content | **DORMANT — 100% NULL** across all 6.72M rows | Verified query A.4. Schema captures it (db.ts 195); upstream parser doesn't populate it. The entire "what the tool returned / artefact content at write-time / Bash stdout / SQL results" axis is empty. |
| Cross-system JOIN (episodic ⇄ Company) | **UNBUILT** | Verified grep: no `~/company` code reads `conversation-index/db.sqlite`. The Company mines transcripts itself, independently. The two halves never touch in code. |
| `file_path` reverse index | **UNBUILT** (queryable via `LIKE`/`JSON_EXTRACT` but unindexed) | Observed: only `idx_tool_name`, `idx_tool_exchange` on tool_calls. Artefact-address lookup is a full scan today. |
| `(session_id, i)` ↔ episodic-`id` alignment | **UNBUILT + at-risk** | Observed B.1 caveat: two independent exchange enumerations; boundary rules may differ. `line_start/line_end` on both sides is the likely true bridge (unbuilt). |
| MCP-artefact address parsing (Supabase rows, Obsidian notes, Langflow graphs) | **UNBUILT** | Inferred from tool_name distribution A.3; the per-tool `tool_input` shapes are not yet parsed. Only `file_path` (Write/Edit/Notebook) is confirmed as an address field. |
| Two embedding spaces (384-dim store-side vs Company history-space) | **UNRECONCILED** | Observed A.7 + B.2. Both are semantically searchable; whether they merge or stay parallel is an open merge-design decision. |
| Upstream-DB durability | **RISK** | Observed: db is under `~/.claude/plugins/cache/superpowers-marketplace/episodic-memory/1.0.15/` — a *versioned plugin cache*. A plugin update (1.0.16) could relocate/rebuild it. Any index/mirror must live Company-side. |

---

## E. SYNTHESIS — the three load-bearing facts (and the one-line spine)

1. **`tool_calls.tool_input` is the artefact-address column** — for Write/Edit/Notebook it holds `"file_path": "<absolute path>"` (verified 99.97%+ coverage), and the FK `tool_calls.exchange_id → exchanges.id` makes **the join from any artefact back to its genesis exchange/session/time runnable on live data today** (Verified, §A.5).
2. **The Company already speaks the same coordinate** — every `history` corpus record carries `source_address = exchange://<sid>/<i>` + `ts_source` (the original exchange timestamp), with lineage enforced as a fail-loud write gate (Verified 1,459 records, 400/400 sampled carry ts_source; §B). The two systems were built to meet at the exchange.
3. **The join itself is unbuilt, `tool_result` is 100% NULL, and the `i`↔episodic-`id` alignment is the one hard reconciliation** — but the bridge (`session_id` + the `line_start/line_end` regions present on both sides) exists, and the whole thing needs zero writes to either store to prototype (§C, §D).

**The spine, one line:**
`artefact-address (tool_input.file_path) → tool_call → exchange (Tim's words + reply) → session → timestamp → the parallel constellation of everything else Tim was doing in those minutes.`
The episodic store points *up* from a written file to that chain; the Company corpus points *down* from a generated record to it. **The merge is welding the two ends together at the exchange.**
