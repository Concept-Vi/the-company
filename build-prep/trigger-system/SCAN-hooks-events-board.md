# SCAN — HOOKS / EVENTS / BOARD surface (for the reusable trigger system)

Read-only scan of `/home/tim/company`, 2026-06-17. Every claim below is **Observed** (read
directly in code/files) unless tagged **Verified** (confirmed by running an inspection) or
**Inferred** (pattern-matched, not executed). No code was modified.

The headline, up front:

> **"Hook" and "trigger" are DISTINCT in this codebase, and the gap Tim is pointing at is real.**
> A **hook** is a *fixed interception point* (the Claude Code harness fires it; today there is exactly
> ONE: `SessionStart`). A **trigger** — a declared `event → action` rule that a dispatcher reads and
> fires — **does not exist as a live general mechanism.** The word `trigger` appears all over the code
> but only ever as a *descriptive field* or a *label for what caused a run* — nothing ever reads a field
> named `trigger` to decide what to do. **Board-file fires nothing. The semantic-fill-in hook was
> intended (it's named in a code comment) but does not exist.**

---

## 1. HOOKS — what exists, where it's wired, how it fires

### The ONE real hook
- **Wiring:** `/home/tim/company/.claude/settings.json:5-16` — a single `SessionStart` hook of
  `type: "command"` running `bash /home/tim/company/ops/hooks/cc_registry_freshness_check.sh`.
- **What it does:** `/home/tim/company/ops/hooks/cc_registry_freshness_check.sh:1-69` — at the start of
  every session, compares `claude --version` against `store/claude-code.version_stamp` and, if stale,
  prints a WARNING to stdout (Claude Code injects it as `additionalContext`). **Non-blocking** (exits 0
  always). It NEVER writes the stamp, NEVER spawns a claude subprocess, and — importantly for facet 4 —
  **NEVER sets `COMPANY_SESSION_ID` and NEVER fills any channel registry entry.**
- **Its own self-description** (`...check.sh:22-24`) confirms it is the *first and only* file in
  `ops/hooks/`: *"this is the FIRST file in ops/hooks/ — a NEW pattern (F-FIX-13). No existing
  ops/hooks/ template exists; the wiring model is .claude/settings.json SessionStart."*

That is the complete hook inventory. There is **no** `PreToolUse`, `PostToolUse`, `UserPromptSubmit`,
or `Stop` hook configured anywhere.

### So: is a "hook" the same as a "trigger" here?
**No — they are different categories, and the code itself draws the line.**

| | **Hook** (in this repo) | **Trigger** (the thing Tim wants to build) |
|---|---|---|
| Who owns it | the **Claude Code harness** (fixed lifecycle points: SessionStart, …) | the **application** (a declared rule) |
| Form | a `command:` entry in `.claude/settings.json` → runs a shell script | *would be* a registry row: `when EVENT → do ACTION` |
| Extensible by | adding a harness lifecycle entry | *would be* "add a row, not code" |
| Live count today | **1** (registry-freshness) | **0** as a general engine |

The clean primitive for the build pack:
**HOOK = a fixed interception point the runtime offers. TRIGGER = a declared `event→action` rule the
runtime reads and fires.** Today the only "fire" points are: (1) the SessionStart hook, (2) time-scheduled
routines, (3) intra-turn rule activation, (4) the supervisor's mailbox-intent loop — see §2/§5. None of
these is a general declarative `on-event → run-action` trigger.

---

## 2. EVENT / WATCH / NOTIFY — does anything fire on a state change?

### Does `cc_board.file_item()` notify / enqueue / emit anything? — NO.
- **Observed:** `/home/tim/company/runtime/cc_board.py:201-241` — `file_item()` validates type/source/edge
  against their registries (fail-loud), mints an id, builds the record dict, calls `_write(...)`
  (`cc_board.py:194-197` → atomic file write), and **returns the record**. There is no callback, no queue
  push, no event emit, no notify, no supervisor ping — nothing.
- The grep for `notify|emit|enqueue|publish|subscribe|watcher` matched `cc_board.py` on **exactly one
  line — a docstring** (`cc_board.py:32`: *"…the `source` field this module emits"*). That is prose, not
  a mechanism. **Filing a board item is a pure write; it triggers nothing.**

### Does the supervisor watch the board (or any registry dir)?  — NO (it polls a mailbox FILE).
- **Observed:** `runtime/session_supervisor.py` runs two daemon polling loops (started ~line 1693):
  - `watchdog_loop` (`session_supervisor.py:1197-1215`) — every `WATCHDOG_POLL_S` (0.5s) closes timed-out
    sessions. Time-based, not change-based.
  - `mailbox_loop` (`session_supervisor.py:1263-1270`) — every `MAIL_POLL_S` (0.5s) reads the durable
    **mailbox file** (`_mail_pass`, `session_supervisor.py:1272-1304`) for *intent records*
    (`wake` / `consult` / `deliver`) and dispatches them: `wake` → `inject` into a live session or
    `spawn` a resume (`:1388-1400`); `consult` → `spawn` fork copies (`:1401-1417`).
- **It does NOT `listdir`/`scandir`/`stat`-watch `channel-memory/noticeboard/`** or any registry dir, and
  there is no inotify. The "events" it reacts to are *append-only mailbox intent records written by the
  channel/clone code*, not filesystem changes and not board items.

### Is there a pub/sub / event bus anywhere? — Only a per-session HTTP push stream, not a global bus.
- **Observed:** the supervisor exposes a `/watch` ndjson endpoint (`session_supervisor.py:1527-1570`):
  a client subscribes, gets event replay + live push via a per-session `Queue` and a `subscribers` list,
  fanned by `_fan` (~`:1007`). This is *per-session conversation events* pushed to watchers — **not** a
  system-wide `event → action` bus that other code can subscribe to in order to react to state changes.

**Net (facet 2): nothing in the runtime fires on board state-change.** A trigger system would be NEW
infrastructure (the board has the addresses + edges to make it cheap — see §3 — but no emit/watch wire
exists today).

---

## 3. The BOARD — typed links, and how a triggered CC would ATTACH its output as a reply

### The board's typed-edge layer (this is the seam a trigger system would build on)
- **Records** live id-keyed flat at `channel-memory/noticeboard/<id>.md` (md + YAML frontmatter); canonical
  address `board://<id>` (`cc_board.py:56, 17, 224-239`).
- **`links`** are TYPED EDGES `[{kind, target}]`, `kind` validated fail-loud against the
  `board_edges/` registry (`cc_board.py:157-170`).
- **Registered edge kinds today** (`/home/tim/company/board_edges/`):
  - `authored_by` — item → `session://<id>` (provenance) — `board_edges/authored_by.py`
  - `attached_to` — item → channel/Space — `board_edges/attached_to.py:1-8` (`directed:True`,
    item→channel; mirrors the channel-layer attachments manifest)
  - `sourced_from` — item → source-type row — `board_edges/sourced_from.py`
  - `promoted_from` — the only **item → item** edge (promotion lineage) — `board_edges/promoted_from.py`
- **There is NO `reply` / `in_reply_to` / `responds_to` edge kind.** A "reply" semantic is a one-line
  **row-add**: drop `board_edges/responds_to.py` (an item→item directed edge) and `reset_registries()`
  makes it live — no code change (the design's whole point, `cc_board.py:18-21, 96-103`).
- **Query surface exists** for the reverse direction (the trigger's "what links to me"): `relations(addr,
  direction="in"|"out"|"both")` and `reverse_traverse(target_addr, kind)` (`cc_board.py:318-410`) already
  find every item that links to a given `board://<id>`. So once an output is attached, *finding* the reply
  is a solved read.

### How an auto-launched CC attaches its output to the triggering item (the mechanism that would close the loop)
The triggering item has a stable address `board://<id>`. The launched CC files its result as a NEW board
item whose `links` point back at the trigger:
```
cc_board.file_item(
    item_type="...", title="...", body="<the CC's output>",
    author_session="session://<the-CC's-own-id>",
    links=[{"kind": "responds_to", "target": "board://<triggering-id>"}],  # ← needs the new edge row
)
```
- `file_item` accepts `author_session`, `channel`, `thread`, and `links` (`cc_board.py:201-203`), so the
  reply carries provenance + the back-edge in one write.
- **Verified (read):** `relations("board://<triggering-id>", direction="in")` would then surface that
  reply — the inbound-edge read already works (`cc_board.py:380-410`).
- **Gap:** (a) the reply edge-kind row doesn't exist yet (trivial row-add); (b) nothing *fires* the launch
  in the first place (§2) — `file_item` emits nothing and the supervisor doesn't watch the board.

---

## 4. The CHANNEL-REGISTRY semantic-info gap + COMPANY_SESSION_ID  ← the load-bearing finding

**Two distinct registries — do not blur them:**

### (i) The CHANNEL registration — a Node `.mjs` server, `.data/channels/` (this is "the channel system")
- **Observed:** `/home/tim/company/channels/company_channel.mjs` boots on session start and writes a
  registry entry. The entry schema (`company_channel.mjs:28-32`, `regEntry()`):
  `{handle, session_id, cwd, description, model, profile, pid, port, started}`.
  **A `description` field AND a `profile` ({model, role, focus, expertise}) DO exist** — the gap is NOT a
  missing field.
- **The gap is that they are seeded EMPTY and only an AGENT can fill them — no hook does:**
  - `company_channel.mjs:18`: `SESSION_ID = process.env.COMPANY_SESSION_ID || ''`
  - `company_channel.mjs:21`: `DESCRIPTION = process.env.COMPANY_CHANNEL_DESC || ''`
  - The **general** channel MCP config — `/home/tim/company/channels/channel.mcp.json:1-9` — sets in
    `env` ONLY `COMPANY_ROOT`. It does **NOT** set `COMPANY_CHANNEL_DESC` and does **NOT** set
    `COMPANY_SESSION_ID`. So a normal session that loads this MCP server registers with
    **`session_id=''` and `description=''`** — exactly Tim's "auto-registers WITHOUT semantic info."
  - The only way the description/profile get filled is the agent VOLUNTARILY calling the
    `announce` tool (`company_channel.mjs:95-98`, sets `DESCRIPTION`) or the `profile` tool
    (`:100-110`, merges `{model, role, focus, expertise}`). These are prompted only by the **prose** MCP
    server-instruction (`company_channel.mjs:54`: *"Once, near the start, call `profile`…"*) — i.e. an
    instruction to the model, **NOT a hook that auto-fires.**
- **Verified (live inspection of `.data/channels/*.json`):** existing members DO have rich descriptions
  and profiles (e.g. `ch-2mnxl9j0.json` has a full `profile`; `ch-ovxwz8k8.json` likewise). So the
  fill-in *path works* — but it worked because those agents *chose* to call `announce`/`profile`. The
  fill is **agent-discretion, not guaranteed.** Nothing enforces or auto-triggers it → the "intended hook"
  is exactly what's missing.
- **The exception that proves the rule:** the **operator-launched interactive clone** path —
  `cc_clone.operator_launch_cmd()` (`runtime/cc_clone.py:104-112`) — DOES pre-seed both:
  `COMPANY_SESSION_ID={new_sid}` and `COMPANY_CHANNEL_DESC={json.dumps(description)}`. That's why that one
  launch path registers WITH semantic info. The *general* startup (`channel.mcp.json`) does not.

### (ii) The agent_sessions registry — the Python supervisor's durable layer (contrast, NOT the answer to (c))
- **Observed:** the supervisor's `agent_sessions.registered` event (`session_supervisor.py:1055-1058`)
  carries only `session / claude_session_id / cwd / name` (+ a templated summary string). The folded
  registry row (`runtime/suite.py:930-936`) has `id, name, cwd, state, last_activity, title, title_source,
  started, summarizer` — **no `description`/`purpose`/`focus`/semantic field at all.** Different layer from
  the channel registry; mentioned here only so the two aren't confused.

### COMPANY_SESSION_ID — where it is (and isn't) injected
- **Read by:** `runtime/session_scan.py:62` — `sid = session_id or os.environ.get("COMPANY_SESSION_ID")`
  (so `resolve_own_session` can identify "self" unambiguously in a multi-transcript project dir).
- **Injected ONLY in two narrow cases:**
  1. Supervisor **resume (non-fork) spawn**: `session_supervisor.py:844`
     `child_env["COMPANY_SESSION_ID"] = resume` (guarded `if resume and not fork`).
  2. Operator clone launch: `cc_clone.py:108` (the `env=` prefix).
- **NOT injected for a fresh/fork session, and NOT in the general `channel.mcp.json`.** The code comment
  at `session_supervisor.py:837-841` is the smoking gun for "a hook was intended":
  > *"fork/fresh spawns mint a NEW id unknown here (claude-assigned at launch) → **left to the
  > SessionStart hook**; NEVER inject a wrong id."*
  But the only SessionStart hook that exists is the registry-freshness check (§1), which does **not** set
  `COMPANY_SESSION_ID`. **So the deferral-to-a-hook is written into the code, and the hook that was
  supposed to do it does not exist.** That is precisely the gap Tim describes — both for the self-id and
  (by the same missing mechanism) for the semantic fill-in.

---

## 5. The complete inventory of "firing" mechanisms today (for the build pack)

| Mechanism | Live? | Kind | Evidence |
|---|---|---|---|
| `SessionStart` hook (registry freshness) | **LIVE** | harness lifecycle hook | `.claude/settings.json:5-16`; `ops/hooks/cc_registry_freshness_check.sh` |
| Per-turn chat/voice (the spine) | **LIVE** | turn | `runtime/activation.py:67` ("per-turn … ALREADY LIVE") |
| Scheduled routines | live-if-armed | **time/cron only** | `runtime/routines.py:33-51` (`cadence`); `runtime/routine_schedule.py:12-14` (OnCalendar / every:N). **No event-based routine kind.** |
| Intra-turn rule activation | **LIVE** | condition→action (deterministic) | `runtime/rules.py` — fires on a `when` AST over resolved role outputs; `destination="chain"` routes to next role. NOT external-event-driven. |
| Supervisor mailbox loop (wake/consult/deliver) | **LIVE** | intent-record poll | `session_supervisor.py:1263-1304, 1388-1417` — polls a mailbox FILE, not the board. |
| Activation substrate (background/sense/rollup) | **BUILT-NOT-ARMED** | declared contexts; nearest to a trigger | `activation.py:64-106` registry has `"trigger"` + `"trigger_driver"` LABELS; loop is opt-in (`activation_driver.py:84-95`, env `COMPANY_ACTIVATION_LOOP`, default OFF); the event SOURCE is NEEDS-TIM (`activation.py:467`). |
| A general `event → action` trigger registry / event bus | **DOES NOT EXIST** | — | no field named `trigger` is ever read to dispatch; `trigger` is descriptive everywhere (`routines.py:50`, `roles.py:26-27` self-confesses "descriptive today … a general event→role trigger engine is downstream"). |

---

## VERDICTS

**(a) trigger vs hook — DISTINCT.**
A **hook** = a fixed interception point owned by the Claude Code harness; the repo has exactly one
(`SessionStart` → `cc_registry_freshness_check.sh`). A **trigger** = a declared `event→action` rule a
dispatcher reads and fires — **this does not exist as a live general mechanism.** The token `trigger`
occurs widely but is *always* a descriptive field or a "what-caused-this-run" label; no code ever reads a
field named `trigger` to decide what to do (`roles.py:26-27` literally says the trigger field is
"descriptive today" and the real engine is "downstream"). The clean primitive for the build:
**HOOK = interception point; TRIGGER = declared event→action row.**

**(b) does board-file currently trigger anything — NO.**
`cc_board.file_item()` (`cc_board.py:201-241`) validates, writes, and returns — it emits/notifies/enqueues
nothing (its lone "emit" is a docstring word, `:32`). The supervisor polls a durable **mailbox file**, not
the noticeboard directory, and has no inotify/scandir watch (`session_supervisor.py:1263-1304`). Filing a
board item is an inert write. The board does, however, already carry the **typed-edge + address +
inbound-query** machinery (`board://<id>`, `links`, `relations(…, "in")`) that a trigger system would
attach onto — including the attach-a-reply mechanism (`file_item(..., links=[{kind, target:"board://…"}])`,
once a `responds_to` edge row is added).

**(c) channel-registry semantic-info + COMPANY_SESSION_ID — gap CONFIRMED, intended-but-absent hook.**
The channel registry (`company_channel.mjs`, `.data/channels/`) DOES have `description` + `profile`
fields, but the **general** startup wiring (`channels/channel.mcp.json`) seeds them EMPTY — it passes only
`COMPANY_ROOT`, neither `COMPANY_CHANNEL_DESC` nor `COMPANY_SESSION_ID`. So a normal session auto-registers
with `session_id=''` and `description=''`. They get filled ONLY if the agent voluntarily calls
`announce`/`profile` (prompted by prose instruction, `company_channel.mjs:54` — not a hook). Live
`.data/channels/*.json` shows the fill *does* happen when agents comply — but it's discretionary, not
enforced/auto-fired. `COMPANY_SESSION_ID` is injected only on supervisor resume-spawn
(`session_supervisor.py:844`) and operator clone launch (`cc_clone.py:108`); for fresh/general sessions the
code comment `session_supervisor.py:837-841` explicitly **defers self-id to "the SessionStart hook"** — but
the only SessionStart hook that exists (registry-freshness) does not set it. **The fill-in hook Tim
remembers was intended (named in code) and does not exist** — that single missing hook is the root of both
the empty `COMPANY_SESSION_ID` and the empty semantic description at registration.
