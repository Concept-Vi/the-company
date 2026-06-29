---
type: proposal
title: CONVERSATIONS + SESSIONS Fusion — One Record of What Was Said
subject: fuse OpenWebUI chats (branching message DAG) with the company session/recall/store stack
register: prescriptive
status: unconfirmed
posture: both sides incomplete, unreviewed; no source of truth; no horizon; best parts fused INTO THE COMPANY; no duplicates
created: 2026-06-28
verified_live: true
relates-to: ["[[area-A-runtime-core]]", "[[area-I-memory-tests]]", "[[owui-side-map]]"]
---

# CONVERSATIONS + SESSIONS Fusion

> Read the maps as descriptive only. This proposal is grounded in **live verification** (real files,
> real DB rows, real bridge state) done 2026-06-28, not in the maps' prose. Where the maps and the
> live system disagree, the live system wins and the disagreement is flagged. Confident prose ≠ correct.

---

## 0. THE DISCRIMINATING FACT (verified) — there are THREE record-kinds, not two

The brief frames this as "two records of what was said." **Verified live, that framing is wrong, and
getting it right changes the whole seam.** The company does not hold one conversational record that
"disagrees" with OWUI's. It holds a **pointer + a metadata fold + a search index over a foreign file**:

| Record | What it physically is | Holds message CONTENT? | Evidence (verified) |
|---|---|---|---|
| **CC transcript** (`~/.claude/projects/<proj>/<uuid>.jsonl`) | The Claude Code agent's own append-only conversation log | **YES — the only place** | `agent_sessions/<uuid>.json` field `jsonl_path` points AT it |
| **company `agent_sessions/<uuid>.json`** | Per-session **metadata** (cwd, state, turns, title, `jsonl_path`, bytes/mtime) | **NO** | `.data/store/agent_sessions/0004d571….json` — read live; no message text, just a pointer + counts |
| **company `events.jsonl` `agent_sessions.turn`** | Lifecycle **events** (spawned/turn/idle/closed) | **NO** | `{"kind":"agent_sessions.turn","summary":"f1-test-2 · turn 1 done","duration_ms":4929…}` — a summary string, no content (verified, seq 5068) |
| **recollection index** (sqlite + sqlite-vec) | Semantic **search index** over the CC transcript archive | content is COPIED in (`user_message`/`assistant_message` columns) for search | `exchanges` table; verified both DBs below |
| **`session_recall`** | On-demand embed+rerank over ONE session | reads content **directly from the CC `.jsonl`** | `runtime/session_recall.py:161` `scan_session(jsonl_path)` — consumes the transcript, stores nothing of its own |
| **company `chat.jsonl` / `chat_threads/`** | A **thin operator-console chat log** (the studio twin) | YES but trivial | `.data/store/chat.jsonl` last row = `"▶ ran: 0 ran, 3 cached"` — this is NOT the conversational substrate; it is UI plumbing |
| **OWUI `Chat` table** | Human↔model web conversation, **full content + branching DAG** in one JSON blob | **YES — authoritative, with branching** | `models/chats.py:41,495` `history.messages{}`+`currentId` |

**Consequence for the seam (Section 2):** The "company store becomes truth, OWUI becomes a view"
option is **not currently possible** — because the company has **no message-content store with
parent/child structure at all**. Content of agent conversations lives in foreign CC `.jsonl` files;
content of operator chats is a degenerate twin log. So the fusion is not "pick which of two stores
wins." It is: **build the conversational-content record the company is currently missing, and make
OWUI's branching DAG the donor shape for it.** State this dependency openly rather than pretending a
store already holds it.

---

## 1. BEST PARTS

### Company side
- **The addressed store (FsStore)** — `.data/store/` — append-only leaves + read-time folds, graph-locked
  cross-process appends, fsync discipline. This is the right *substrate* for a unified record (one
  store, log-is-the-index). It is NOT currently used to hold conversation message content.
- **Sessions (supervisor-held)** — `session_supervisor.py` owns the live Claude-subprocess fleet,
  single-writer to `agent_sessions.*` events (audit C6), truthful state machine
  (starting→idle⇄busy→closed). Strong **lifecycle** model; weak **content** model (points out to CC `.jsonl`).
- **`session_recall`** (`runtime/session_recall.py`) — meaning-search over a session's turns
  (pplx-embed contextual + jina-v3 rerank, fail-loud, bridge-free). The strongest *retrieval* primitive;
  it is index-free at rest (rebuilds from the transcript), so it does not itself fix the "where does
  content live" gap — but it is exactly the recall lane the brain_router flags as unwired (`brain_router.py:244`).
- **The mail log + channel fabric** — `agent_sessions/mail.jsonl` (intents), `agent_sessions/channels.jsonl`
  (channel lifecycle), connection-edges as a read-time projection. This is the cross-session
  *coordination* spine, NOT a conversation record — important to keep distinct (see Section 4).
- **recollection** — the embedded episodic index over the CC/Codex transcript archive (semantic + text
  + multi-concept). The company's existing answer to "what was said across all sessions."

### OWUI side (donor)
- **Branching chat DAG** — `models/chats.py:495`: every message carries `parentId`+`childrenIds`,
  `history.currentId` = active leaf, siblings = branches. Regen/edit/branch are new DAG nodes. **The
  single cleanest conversation-shape in either system** and the thing the company entirely lacks.
- **Regen / edit / branch UX** — edit-a-message-and-re-run, regenerate, walk siblings — first-class.
- **Chat history UI** — list/search/pinned/archived/shared/folders/tags, `branchPointMessageId` on clone
  (`routers/chats.py:1211`). Product-grade conversation-management surface.
- **(Honest caveat)** OWUI itself is **mid-migration**: `Chat` JSON blob (truth today) vs normalized
  `ChatMessage` table (forward path, dual-write glue `models/chats.py:540-560`). Do **not** inherit
  the half-finished duplication — harvest the *shape* (the parent/child DAG), resolve it once.

---

## 2. THE FUSED MODEL — one record, the seam

### The decision (grounded in Section 0)
Neither "company-store-as-truth-with-OWUI-as-view" nor "keep-OWUI's-DB-and-sync" is right as stated:
- "Company store as truth" presumes a content store that **does not exist yet** (verified §0).
- "Keep OWUI's DB + sync" is **two-stores-that-disagree** — the exact patchwork Tim rejects
  (unions-not-bridges; islands-join-mainland). And the live bridge already proves the failure mode is
  near: there is a running OWUI↔company bridge today (`ops/owui_fabric_bridge.py`,
  `.data/owui_bridge_state.json` `fabric_last_seq:35`) — but it syncs **channels only, never chats**
  (verified: all four `ops/owui_*` scripts touch `/api/v1/channels/...`, zero touch `/api/v1/chats`).
  So conversations are still completely unfused; the temptation to "just add a chat sync to the bridge"
  is the patchwork to refuse.

**Proposed union: the company addressed store becomes the ONE record of conversation content, with a
typed branching message DAG built INTO it — donating OWUI's parentId/childrenIds/currentId shape — and
OWUI's chat UI becomes a VIEW that reads/writes that record through the company API.** No second store.

### The new store leaf (the thing the company is missing)
Add a conversation-content record to FsStore, modeled as the company already models everything else
(append-only leaf + read-time fold, the `agent_sessions/channels.jsonl` pattern):

```
.data/store/conversations/<conversation_id>.jsonl   # append-only message events, graph-locked + fsync
```
One message event (donor shape from OWUI, named in company grammar):
```
{ seq, ts, conversation_id, message_id, parent_id, role, content,
  model_id?, files?, sources?, attribution, current?, edited_of?, regen_of? }
```
- **Branching = parent_id + the fold computes children + a `current` leaf** — identical semantics to
  OWUI `history.messages{}`/`currentId`, but as company append-only events (no JSON-blob rewrite, no
  dual ChatMessage table — we resolve the migration OWUI never finished by *only* keeping the
  normalized form).
- **Edit / regen** = a new message event with `edited_of`/`regen_of` + a new branch under the same
  `parent_id`. The DAG records every variant; `current` selects the displayed leaf. This is OWUI's
  regen/edit/branch UX expressed natively.
- **Read-time fold** `fold_conversation(store, cid)` → the message tree + current path, exactly as
  `fold_channels` folds channels.

### How the three record-kinds collapse into one (the seam, concretely)
1. **Agent (Claude Code) conversations.** Today: content only in the CC `.jsonl`, company holds a
   pointer. **Fusion:** the supervisor's `_reader()` already parses every stdout stream-json event
   (`session_supervisor.py:_reader`). At each assistant/user turn it ALSO appends a message event to
   `conversations/<cid>.jsonl` (the supervisor stays the single writer — audit C6 preserved). The CC
   `.jsonl` becomes a *cache/source of the agent runtime*, not the company's record; the company record
   is the store leaf. `jsonl_path` stays as provenance, not as the truth.
2. **Operator / OWUI human chats.** Today: OWUI `Chat` table is truth; company `chat.jsonl` is a twin
   stub. **Fusion:** OWUI's chat frontend writes through to the company conversation API instead of its
   own DB — OWUI becomes a **view** (its branching UI drives company `parent_id` events). Where OWUI's
   compiled frontend cannot be rewired without a fork (owui-side-map §8: chat UI is fork-only), the
   minimal seam is a **company-owned chat surface** that reuses OWUI's branching *shape* and history
   *UX patterns*, with OWUI retained only as a model-gateway/console — not as a chat store.
3. **recall + recollection.** Once content lives in `conversations/*.jsonl`, **`session_recall` and
   recollection both index the company record** instead of (recall) re-reading foreign CC `.jsonl` and
   (recollection) indexing the archive copy. One content source → one thing to embed → the
   `brain_router` recall lane (`brain_router.py:244`, currently degrades recall→model) gets a real
   backend. Recollection's archive-of-everything role stays (historical CC/Codex transcripts predating
   the leaf), but new conversation is born in the store, not imported from a transcript.

### Why this is a union not a bridge
- One content store (FsStore `conversations/`), one branching model (OWUI's, built in), one recall
  target. OWUI contributes **shape + UX**, not a parallel database. The running channel-bridge stays
  doing its channel job (coordination), and is explicitly **not** extended to sync chats — chats join
  the mainland instead of being mirrored across it.

### The seam's hard dependency (stated, not assumed)
This requires FsStore to gain a conversation leaf + fold. That is new construction, not a re-point of
an existing store. The proposal's correctness rests on §0: the company genuinely has no
message-content+branching record today. If a later reader finds one, revisit — but it was verified absent.

### Increment status + the exact inc.2 wiring (insertion points confirmed by reading `_reader` line-by-line, 2026-06-29)

**Inc.1 (the store) — DONE + VERIFIED BY USE.** `runtime/conversations.py` exists (new_conversation /
append_message(parent_id) / select_branch / fold_conversation / get_conversation / list_conversations).
Branching DAG verified company-down against a stub store: root+chain, regen sibling survival under one
parent, default-current = last-appended, select override, append-after-select advancing current, deeper
current-walk, persistence re-read. **A real fold bug was found + fixed here** (commit `0393bd7`):
`current_leaf` took any prior `select` unconditionally, freezing the displayed leaf so a reply appended
after a branch-nav was invisible; now both a message-append and a valid select advance `current_leaf` in
file order (latest-action-wins). The store is correct + inert-but-usable; it is NOT yet written to live.

**Inc.2 (wire the supervisor reader) — PLAN, apply+verify when the company is up.** Touches the
load-bearing supervisor → do solo/careful, verify by use, never on inference. Confirmed insertion points
in `runtime/session_supervisor.py`:

- **cid (the conversation key)** = `s.claude_session_id` — durable, set at the `system/init` event
  (`_reader`, line 1044) which fires BEFORE the first `inject` (init moves `starting→idle`; inject refuses
  unless idle). Born on first append (new_conversation mints nothing on disk). Fallback to `s.id` only if
  `claude_session_id` is still None (defensive; shouldn't occur post-init).
- **DAG cursor** = a new `Supervised.last_message_id: str | None = None` field — the running parent_id.
  Each append sets it; the next append passes it as `parent_id`. This is the one piece of per-session
  state inc.2 adds.
- **User turn IN** — `inject()` (line 1121): after the stdin write SUCCEEDS (after line 1142), append
  `role="user", content=message, parent_id=s.last_message_id, attribution={"source": source}`; set
  `s.last_message_id` to the returned id. ALSO the spawn-with-initial-prompt path (the prompt passed at
  spawn, not via inject — locate in the spawn block ~838-866; if the initial prompt rides the subprocess
  args/first-stdin rather than `inject`, hook it at that send-site too, else turn-1's user message is lost).
- **Assistant turn DONE** — `_turn_done()` (line 1086): `result_text` (line 1088 = `ev.get("result") or
  "\n".join(s.turn_text)`) is the full reply. Append `role="assistant", content=result_text,
  parent_id=s.last_message_id, model_id=(usage or {}).get("model"), attribution={"is_error": ...,
  "duration_ms": dur_ms, "intent_id": ...}`; set `s.last_message_id`. Do this AFTER the existing
  `agent_sessions.turn` emit + mail reply (the conversation leaf is a secondary sink, never ahead of the
  primary contract).
- **FAIL-SOFT (the load-bearing safety law)** — every `append_message` call is wrapped so a conversation-
  store hiccup can NEVER raise into the reader/inject path and kill a session turn. Pattern: a private
  `self._record_message(s, role, content, **kw)` helper that try/excepts, logs a warning to stderr +
  `self._fan(s, {"type":"conv_record_failed", ...})` (non-durable), and swallows. The store is additive;
  the supervisor's existing behaviour must be byte-for-byte unaffected when the store is absent/erroring.
- **Single-writer (audit C6) preserved** — conversations.py writes ONLY its own `conversations/<cid>.jsonl`
  leaf (its own per-conversation lock); it emits NO `agent_sessions.*` on events.jsonl. The supervisor
  stays the single writer of events.jsonl. (Already true by the module's floor — restated so inc.2 doesn't
  break it by reflex.)

**Verify-by-use bar for inc.2 (when the company is up):** spawn a session → capture `claude_session_id`
→ inject a message → assert `conversations/<csid>.jsonl` has a `user` message → let the turn finish →
assert an `assistant` message appended with `parent_id` = the user message → multi-turn → assert the DAG
chain → **simulate a store write failure (e.g. unwritable dir) and confirm the session turn STILL
completes** (fail-soft proven, not assumed). Only then is inc.2 done.

**Inc.3 (re-point recall) — follow-on, after content is born live.** §3.4's one-line source swap:
`session_recall` (and recollection's new-content path) read `conversations/*.jsonl` instead of foreign CC
`.jsonl`. Gated on inc.2 producing real content, so there is something company-owned to index.

---

## 3. COMPANY-INTERNAL ISSUES (verified, with resolutions)

### 3.1 The recollection index is a genuine, LIVE split-brain — TWO databases, two schemas
The area-I map says the env split-brain "needs repair." **Verified live it is worse and different than
the map states — there are two physical DBs with divergent schemas, both live:**

| DB | Size | Rows | Schema |
|---|---|---|---|
| `~/.config/superpowers/conversation-index/db.sqlite` | **12.5 GB** | **86,241** exchanges | OLD (no `harness`/`model`/`embedding_version`) |
| `~/company/.recollection/conversation-index/db.sqlite` | 218 MB | 8,224 exchanges | NEW (+`harness`,`model`,`model_provider`,`embedding_version`, **+ dragnet tables** `atoms`/`units`/`links`/`verdicts`/`candidates` + a `vec_pplx-ctx-4b-docs` vector table) |

- The company-local DB's vec tables are **empty** (`vec_exchanges_chunks: 0 rows`) — it is freshly
  schema-migrated but **not re-embedded** (matches the map's "freshness / no-auto-reindex" bug and the
  Dragnet "35904=stale chroma" note).
- The 12.5GB DB is the one actually carrying embeddings (914 vec chunks, 86k rows) but on the OLD schema.
- **Both** have absolute `archive_path` columns (verified: `/home/tim/.config/superpowers/conversation-archive/…`
  and `/home/tim/recollection/test/fixtures/…`) — confirming the area-I "8218 absolute-path rows → SQL
  rewrite on relocation" issue, present in BOTH DBs.

**Resolution (NON-destructive ordering — caution):** First **determine the canonical-live DB** — the
12.5GB `~/.config/superpowers` DB is the one with actual embeddings (914 vec chunks, 86k rows), while
the schema-current company-local DB has **empty vec tables**, so a naive "keep the new, drop the old"
would delete the only populated index. I did **not** confirm which DB the live recollection MCP reads
this session (the running MCP procs found were unrelated langsmith servers; the recollection service's
`RECOLLECTION_CONFIG_DIR` / systemd ExecStart env must be read first). So: (1) read the live service's
config to find which DB is canonical; (2) converge on ONE — adopt the new schema, **migrate the 86k
embedded rows into it and re-embed only the delta**, THEN retire the other; (3) make `archive_path`
**store-relative**, resolved at read-time against a single configured root — so relocation never needs a
SQL rewrite. Migrate-then-retire, never retire-first. This is one-store discipline applied to the index, mirroring the
one-store discipline applied to content in Section 2.

### 3.2 The env split-brain is RESOLVED in code — the map is stale on this point
The map flags `EPISODIC_MEMORY_CONFIG_DIR` as ignored (a bug). **Verified live this is now intentional
and correct:** `recollection/src/paths.ts:100` documents it was *deliberately* dropped because it is a
shared-namespace var that "could resolve onto the live store (the exact B-5 comingling)"; precedence is
now `RECOLLECTION_CONFIG_DIR > TEST_CONFIG_DIR > ~/.recollection`, both recollection-private names.
**Resolution: none needed for the var; update the area-I map** (it asserts a bug that the code fixed).
The *real* remaining issue is 3.1 (two physical DBs), not the env var.

### 3.3 Two parallel "chat" notions inside the company
`chat.jsonl`/`chat_threads/` (studio operator twin) vs `agent_sessions` (the fleet) vs the proposed
`conversations/` leaf. The studio `chat.jsonl` is a degenerate UI log (verified: `"▶ ran: 0 ran…"`),
not a conversation record. **Resolution:** fold the studio chat onto the same `conversations/` leaf as a
conversation whose participant is the operator console — no third chat concept.

### 3.4 session_recall is index-free at rest, re-reads foreign files
`session_recall` reads CC `.jsonl` directly each call (`:161`). Fine while content lives there; under
Section 2 it must re-point at `conversations/<cid>.jsonl`. **Resolution:** one-line source swap once the
leaf exists; recall's embed/rerank logic is unchanged (it already chunks generic turn rows).

---

## 4. BROKEN / HALF-BUILT SEAMS

1. **The live OWUI bridge syncs channels but NOT chats** — `ops/owui_fabric_bridge.py`,
   `owui_room.py`, `owui_to_fork_*.py`; state in `.data/owui_*_state.json` (`fabric_last_seq:35`,
   live webhooks/rooms `fabric-test`/`war-room`). Conversations are therefore **completely unfused**.
   This is the gap this proposal fills — and the bridge must **not** be the place chats get bolted on
   (that would make two chat stores). Flag: the bridge is real, running, and channel-only.
2. **OWUI's own JSON→relational migration is unfinished** (`Chat` JSON `history` vs `ChatMessage` table,
   dual-write glue `models/chats.py:540-560`). Do not inherit it; Section 2 keeps only the normalized
   branching form.
3. **The recollection re-embed is not done** — company-local DB has the schema but empty vec tables
   (verified). Recall over the new schema returns nothing until re-embedded.
4. **brain_router recall lane is a declared hook, not wired** — `brain_router.py:244` routes recall
   questions to the model (itself), degrading; the real recall backend (Section 2 + 3.4) is the fill.
5. **`channel_boundary.py` Realtime subscriber is stubbed** (area-A:408) — separate from this fusion
   (it is the Supabase shared-channel path, not chats) but named here so it is not conflated.
6. **agent_sessions has no content, by design** — until Section 2's leaf exists, "recall what an agent
   said" depends on the foreign CC `.jsonl` surviving (`jsonl_path` + `jsonl_mtime` are cached; if the
   CC file is rotated/deleted, the company loses the content). This is a silent-data-loss seam today.

---

## 5. VERIFICATION DONE (live, 2026-06-28)

- **Read** all three required maps + confirmed sibling docs exist (`01-spine.md`, area-A..I).
- **agent_sessions record holds no content:** read `.data/store/agent_sessions/0004d571….json` — fields
  are metadata + `jsonl_path` pointer; `turns:2`, no message text. **(Observed.)**
- **turn events carry no content:** `grep agent_sessions.turn .data/store/events.jsonl` → seq 5068 =
  `summary:"f1-test-2 · turn 1 done"`, duration only. Counts: 136 turn, 67 spawned, 63 closed. **(Observed.)**
- **session_recall reads the CC transcript directly:** `runtime/session_recall.py:161` `scan_session(jsonl_path)`;
  module docstring confirms it loads no store of its own, embeds the transcript on demand. **(Observed.)**
- **company chat.jsonl is a UI twin, not a conversation store:** last row `"▶ ran: 0 ran, 3 cached"`. **(Observed.)**
- **OWUI bridge is live and channel-only:** read all four `.data/owui_*_state.json` (`fabric_last_seq:35`,
  webhooks, rooms); Explore agent confirmed `ops/owui_*` scripts use `/api/v1/channels/...` exclusively,
  zero `/api/v1/chats`. **(Observed + delegated-verified.)**
- **recollection split-brain (two DBs):** queried both sqlite files read-only — 12.5GB/86,241 rows
  (old schema, has embeddings) vs 218MB/8,224 rows (new schema + dragnet tables, **empty vec tables**).
  Both have absolute `archive_path`. **(Verified by SQL.)**
- **env split-brain is resolved in code:** read `recollection/src/paths.ts:90-130` — `EPISODIC_MEMORY_CONFIG_DIR`
  deliberately dropped; precedence `RECOLLECTION_CONFIG_DIR > TEST_CONFIG_DIR > ~/.recollection`. The
  area-I map is **stale** on this. **(Observed.)**

### §0 premise re-checked (advisor-prompted, the seam stands on this)
- **`.data/store/sessions/`** (69 files) holds **review/walkthrough mode-cursor** records
  (`{id,graph,mode:"walkthrough",items:[s5-review…],cursor,done}`), **NOT conversation content**. **(Verified.)**
- **`chat_threads/<id>.json`** is a thread **registry** (`{id,title,created,last_msg}`) — messages are
  NOT in it; and `chat.jsonl` rows carry **no thread/conversation id** (`ts,role,text,action,grade,source`),
  so the studio chat is an undifferentiated flat log not even joined to its own thread registry.
  This *strengthens* §0 and §3.3. **(Verified.)**
- **`.data/unify-exercise/`** (touched today) is a **retrieval/reranker A-B eval** workspace
  (recall *quality*) — relevant to §3.1, **not** a parallel conversation-store build. No collision with
  this proposal's seam. **(Verified by ls -R + reading the dir contents.)**
- **Conclusion: §0's "the company has no message-content + branching record" is confirmed** across
  `agent_sessions`, `events.jsonl`, `chat.jsonl`, `chat_threads`, and `sessions/`. The seam = build the
  leaf, not extend an existing one.

### NOT verified (honest gaps)
- I did not read `session_supervisor._reader()` line-by-line to confirm the exact insertion point for
  the proposed message-event append (Section 2 step 1) — first thing to confirm at build time.
- OWUI `Chat`/`ChatMessage` claims (branching truth, dual-write `:540-560`) are from owui-side-map
  (file:line cited there), **not** re-verified against the installed OWUI source this session.
- **Which recollection DB the live service reads** — not confirmed; gates the §3.1 retirement step
  (see the non-destructive ordering note there).
