---
type: contract-entry
resource: context-window
summary: One session's live token budget and the compaction machinery that keeps it under the model limit — /context to read it, /compact and auto-compaction and microcompaction to shrink it, /clear to reset it, /btw to ask without growing it. In-process to each Claude Code session; no Company fabric endpoint reads or drives it today.
schemes: []
status: planned
relates-to: ["[[session]]", "[[checkpoint]]", "[[transcript]]", "[[fabric-config]]"]
---

# Resource: context-window

## Identity
**A context-window belongs to exactly one session and is identified by that session's id — there
is one independent window per session (and a separate one per subagent); there is no fabric
address scheme, because no Company endpoint reads a window's usage or drives its compaction
today.** (Source: https://code.claude.com/docs/en/context-window.md ; per-session window:
glossary.md "session".) A UI that wants live usage reads it from the statusline data feed inside
the interactive process (`context_window.used_percentage` / `current_usage`, source:
statusline.md), or from the SDK stream's `compact_boundary` messages — NOT from the Company
backend. This corpus claims no `context://` scheme; F2 contracts the capability and names the gap.

## Representation
**A context-window's observable shape is a usage breakdown by category (system prompt, tools,
memory files, messages) plus a used/remaining token budget — surfaced live in-process by
`/context` and the statusline feed; the fabric does not aggregate it.** (Source: errors.md
prompt-is-too-long; statusline.md available-data; context-window.md check-your-own-session.)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/context-window.usage",
  "type": "object",
  "description": "The usage shape a fabric context endpoint WOULD serve if built (planned). Grounded in the statusline `context_window` fields and the /context breakdown; no live Company endpoint emits this.",
  "required": ["session_id"],
  "properties": {
    "session_id":           { "type": "string" },
    "used_percentage":      { "type": ["number", "null"], "description": "statusline context_window.used_percentage — 0..100" },
    "remaining_percentage": { "type": ["number", "null"], "description": "statusline pre-calculated remaining" },
    "current_usage":        { "type": ["object", "null"], "description": "token counts from the last API call (statusline context_window.current_usage)" },
    "exceeds_200k_tokens":  { "type": ["boolean", "null"], "description": "fixed-threshold flag from the most recent API response, regardless of the model's actual window size" },
    "breakdown":            { "type": ["object", "null"],
                              "description": "what /context shows: per-category token spend — system prompt, tools, memory (CLAUDE.md/auto-memory), messages",
                              "properties": {
                                "system_prompt": { "type": "integer" },
                                "tools":         { "type": "integer" },
                                "memory":        { "type": "integer" },
                                "messages":      { "type": "integer" } } } } }
```
| field | type | volatile? | changed-by | address? -> resource | reality (Observed in docs, NOT measured against a live fabric endpoint) |
|---|---|---|---|---|---|
| used_percentage | number | YES | every turn (more context = higher); a compaction drops it | — | the statusline carries it live in-process; a fabric endpoint serving it does not exist |
| breakdown | object | YES | adding tools/memory/messages; `/clear` zeroes messages; compaction collapses messages+tool outputs into a summary | — | `/context` renders this live with optimization suggestions; not aggregated by the fabric |
| exceeds_200k_tokens | bool | YES | the most recent API response | — | a fixed 200k threshold flag, NOT the model's true window size — stated so a UI does not misread it as the limit |

**Field-reality honesty:** Observed from docs (cited), not Verified against a Company endpoint —
none exists. MCP tool definitions are deferred-by-default and load on demand via tool search, so
only tool NAMES consume the window until a tool is used (source: how-claude-code-works.md
when-context-fills-up) — a UI showing "tools" spend should expect it to grow as tools are invoked.

## State model
**State model: stateless.** The window is a continuously-recomputed measure, not a thing with
states; the only state-shaped event in its lifecycle is a compaction BOUNDARY (the SDK marks it
with a `compact_boundary` system message; the conversation before/after that boundary is the only
"transition"). Compaction is recorded as a boundary, never as a window state machine.

## Caller
**No fabric caller exists: the context-window is read and driven only from inside a session —
the human via slash commands (`/context`, `/compact`, `/clear`, `/btw`) at the interactive TUI, or
an Agent-SDK program (which can SEND `/compact` as a prompt string and OBSERVE `compact_boundary`
messages, and set a `BetaTokenTaskBudget` when calling the Messages API directly).** The Company
supervisor spawns headless `claude -p` sessions and exposes no context endpoint: it could in
principle inject `/compact` as a turn (it has [[session#op: session.inject]]), but no contracted
op means "compact this session", and nothing aggregates `/context` usage to a fabric read. Auto-
compaction runs transparently inside each session regardless of any caller (source: glossary.md
compaction; agent-loop.md automatic-compaction). Every op below is therefore `planned`.

## Operations

## op: context-window.get
**`context-window.get` is the planned live-usage read — the `/context` breakdown (system prompt /
tools / memory / messages) plus used/remaining budget — which has no Company endpoint today: the
real surfaces are the in-process `/context` command and the statusline `context_window` data
feed.**
```contract:op
op: context-window.get
resource: context-window
kind: get
status: planned
direction: outbound
atlas: [CC-05.3]
tasks:
  - phrase: "how full is the context window"
  - phrase: "what is consuming my context tokens"
  - phrase: "show the context breakdown by category"
  - alias: "context usage"
  - alias: "am I about to run out of context"
bindings:
  - { kind: tui, surface: "/context  (live breakdown by category + optimization suggestions); /memory shows which CLAUDE.md/auto-memory files loaded", exposure: "n/a — interactive", status: planned }
  - { kind: sdk, call: "statusline JSON: context_window.used_percentage / remaining_percentage / current_usage / exceeds_200k_tokens", exposure: "n/a — in-process statusline feed", status: planned, note: "statusline scripts read this from stdin; it is not a Company endpoint" }
liveness: snapshot
live-twin: "none for a fabric read (no endpoint). In-process the statusline reflects it continuously; a UI can poll /context."
emits: []
verification:
  fabric-endpoint: {state: unverified, note: "NO Company endpoint. Grounded in context-window.md, statusline.md available-data, errors.md prompt-is-too-long."}
```
A `planned` op with no binding carries no green-painted request/response wire (§6 V11); the
Representation fence is the shape a future endpoint would serve. The interim honest path for a
fabric-only consumer: there is none for live per-session usage — it is genuinely in-process. The
nearest fabric-visible signal is a session's growth via [[session#op: session.get]] (turns,
jsonl_bytes), which is a coarse proxy, NOT the token breakdown.
Adjacent: [[context-window#op: context-window.compact]] (act on a full window);
[[fabric-config#op: fabric-config.get]] (fabric-wide limits, a different layer entirely).

## op: context-window.compact
**`context-window.compact` is the planned whole-conversation compaction act — summarize history
to free tokens, optionally with a focus instruction — exposed today as the in-process `/compact`
command (and as an SDK prompt input); auto-compaction performs the same collapse automatically as
the window fills, and is on by default.**
```contract:op
op: context-window.compact
resource: context-window
kind: act
status: planned
direction: outbound
atlas: [CC-05.4]
tasks:
  - phrase: "compact the conversation to free up context"
  - phrase: "summarize the history but keep the API changes"
    params: {focus: "the API changes"}
  - alias: "free up context space"
  - alias: "run compaction now"
bindings:
  - { kind: tui, surface: "/compact   (optionally /compact <focus instructions>, e.g. /compact Focus on code samples and API usage)", exposure: "n/a — interactive", status: planned }
  - { kind: sdk, call: "send '/compact' (optionally with focus) as a prompt string — an SDK input, not a CLI-only shortcut", exposure: "n/a — Agent SDK in-process", status: planned, note: "the PreCompact hook can run before compaction (trigger=manual|auto); the SDK emits a compact_boundary system message when it completes" }
liveness: none
emits: []
consequences:
  - when: "manual /compact (trigger=manual)"
    expect: []
    evidence: "the SDK stream carries a system message subtype=compact_boundary with compact_metadata {trigger: 'manual', pre_tokens}. Conversation + tool outputs are replaced with an AI summary; CLAUDE.md/auto-memory are re-read from disk and re-injected (they SURVIVE); subdirectory CLAUDE.md does NOT reload until a matching file is read. Telemetry path: a claude_code.compaction OTEL event fires with trigger/success/duration_ms/pre_tokens/post_tokens (monitoring-usage.md) — observable only where telemetry is wired (cross-lane, not a fabric endpoint here)."
  - when: "auto-compaction (trigger=auto, fires as the window approaches the limit)"
    expect: []
    evidence: "older tool outputs are cleared FIRST, then the conversation is summarized (the microcompaction-then-summarize order, source: glossary.md compaction). Same compact_boundary boundary marker, trigger='auto'. Disabled only via DISABLE_AUTO_COMPACT env var (errors.md)."
correlate: []
verification:
  tui-compact:  {state: unverified, note: "documented; no programmatic driver in scope."}
  sdk-compact:  {state: unverified, note: "compact_boundary message + PreCompact hook documented (agent-loop.md, typescript SDK SDKCompactBoundaryMessage); NOT run through any Company harness."}
  auto-compact: {state: unverified, note: "on by default, in-process; observable via compact_boundary / OTEL only."}
```
### Errors
```contract:error
code: context-window.compaction-thrashing | http: n/a (no fabric face) | retryable: false
when: a single file or tool output is so large that context refills immediately after each summary
teach: "Claude Code stops auto-compacting after a few attempts and shows a thrashing error rather than looping. Recovery: /clear to reset, or remove the oversized input (a giant file read / tool output), then continue. See troubleshooting 'Auto-compaction stops with a thrashing error'. This is the documented degenerate case, not a fabric error."
```
```contract:error
code: context-window.prompt-too-long | http: n/a (no fabric face) | retryable: false
when: the conversation plus attached files exceeds the model's window even after compaction
teach: "Run /compact (or /clear), run /context to see what is consuming the window, disable unused MCP servers with /mcp disable <name> to drop their tool definitions, and trim large CLAUDE.md or move instructions into path-scoped rules. Re-enable auto-compact if DISABLE_AUTO_COMPACT was set. (Source: errors.md prompt-is-too-long.)"
```
### Interaction semantics
- **What survives compaction (load-bearing for a UI's expectations):** project-root CLAUDE.md and
  auto-memory are re-loaded from disk and re-injected; user/assistant messages and tool outputs are
  REPLACED with the summary; subdirectory CLAUDE.md does NOT reload until a matching file is read.
  Instructions given only in conversation MAY be lost — persistent rules belong in CLAUDE.md.
- **Microcompaction:** the auto path clears older tool OUTPUTS first (cheap, lossless-ish) before
  summarizing the conversation (lossy) — the two-stage order is the "microcompaction then
  summarization" the Atlas names; `/compact` applies both.
- **Idempotency / control:** a manual `/compact` may reuse a background-prepared summary
  (`precompute_reuse: hit`) or recompute (`miss_*`) — a perf detail, not a behavior change.
### Live-ness
`liveness: none` — compaction is an in-process action; its completion is the `compact_boundary`
stream marker / OTEL event, not a fabric cursor. A fabric-only UI cannot today observe a session
compacting; that observation is the named gap.
Adjacent: [[checkpoint#op: checkpoint.summarize]] (TARGETED compaction at a chosen point — same
mechanism, one side of a message); [[context-window#op: context-window.clear]] (reset instead of
summarize).

## op: context-window.clear
**`context-window.clear` is the planned context-reset act — `/clear` starts a fresh conversation,
zeroing the window between unrelated tasks WITHOUT compacting (the previous session stays stored
and is resumable); `/btw` is its lightweight cousin, answering an aside in a dismissible overlay
that never enters history.**
```contract:op
op: context-window.clear
resource: context-window
kind: act
status: planned
direction: outbound
atlas: [CC-05.5]
tasks:
  - phrase: "clear the context and start fresh for a new task"
  - phrase: "reset the conversation between tasks"
  - phrase: "ask a quick aside without growing context"
    params: {mode: btw}
  - alias: "wipe the context"
  - alias: "start a clean slate"
bindings:
  - { kind: tui, surface: "/clear  (resets the window entirely; /rename before clearing makes the old session easy to /resume later). /btw <question> answers in a dismissible overlay, never entering history", exposure: "n/a — interactive", status: planned, note: "/clear starts a NEW session; the previous one stays stored under ~/.claude/projects/ and is resumable (glossary.md session)" }
liveness: none
emits: []
consequences:
  - when: "/clear"
    expect: []
    evidence: "the window is reset to empty (CLAUDE.md/memory reload fresh); a new session begins; the prior session persists on disk and is reachable via [[session#op: session.list]] + resume ([[session#op: session.create]] resume=). Files on disk are UNCHANGED. Observable only in-session for the reset itself; the new session DOES appear in the fabric registry once it registers."
  - when: "/btw <question>"
    expect: []
    evidence: "the answer appears in a dismissible overlay and never enters conversation history — the window does NOT grow. Purely in-process; nothing reaches the fabric."
correlate: []
verification:
  tui-clear: {state: unverified, note: "documented (best-practices.md manage-context-aggressively, costs.md); no programmatic driver."}
```
The relationship a UI must teach: `/clear` DISCARDS (fresh window, old session parked) while
`/compact` PRESERVES-AS-SUMMARY (same session, compressed). Clear between UNRELATED tasks; compact
within a long RELATED one. `/rename` before `/clear` so the parked session is findable.
Adjacent: [[context-window#op: context-window.compact]] (compress instead of discard);
[[session#op: session.create]] resume= (return to a parked session); [[session]] (the parked
session as a fabric resource).

## Errors
**This resource has no fabric error vocabulary — it has no fabric face.** Its real failure modes
are the documented in-process cases recorded on [[context-window#op: context-window.compact]]:
`context-window.compaction-thrashing` (oversized input loops) and `context-window.prompt-too-long`
(window exceeded). When a Company context endpoint is built (Atlas CC-18/CC-05, SDK- or
telemetry-shaped), it adopts the uniform envelope ([[CONVENTIONS]]) — a future obligation recorded
here, not a present capability.

## Links
**The only live cross-resource address is `session_id` -> [[session]] (`session://`, accepted by
session.get/watch): a context-window is exactly one session's window.** No `context://` scheme is
claimed — no accepting op exists, and the §6 V7 dereferenceability law forbids a dead-end scheme.
A `/clear` mints a NEW session that becomes a fabric [[session]] when it registers; the parked
prior session remains a [[session]] resumable via [[session#op: session.create]]. The durable
record of what was in a window before a compaction/clear lives in [[transcript]] (the exported
memory) and, for the original pre-summary messages, the session's own jsonl that the transcript
projects from.
