---
type: contract-entry
resource: checkpoint
summary: A within-session restore point Claude Code snapshots before every prompt — the granular rewind/restore/targeted-summarize layer beneath a session, native to the interactive TUI and the Agent SDK, NOT yet reachable through any Company fabric endpoint.
schemes: []
status: planned
relates-to: ["[[session]]", "[[context-window]]", "[[transcript]]"]
---

# Resource: checkpoint

## Identity
**A checkpoint is identified by the uuid of the user message it precedes — Claude Code creates
one before each prompt you send, and that message uuid IS the restore point; there is no fabric
address scheme, because no Company endpoint mints, lists, or dereferences checkpoints today.**
The restore-point id is the user-message uuid surfaced in a session's stream (the Agent SDK
exposes it on `UserMessage.uuid`, which requires the `replay-user-messages` extra arg — source:
https://code.claude.com/docs/en/agent-sdk/file-checkpointing.md). In the interactive TUI there is
no externalized id at all: you pick a checkpoint by selecting a prompt in the `/rewind` menu, not
by naming an id. This corpus claims no `checkpoint://` scheme: F2 contracts the capability as it
is grounded in Claude Code (cited throughout), and marks loudly that the fabric does not surface
it (§ Caller; every op `planned`).

## Representation
**A checkpoint captures the on-disk state of the files Claude edited THROUGH its file-editing
tools (Write / Edit / NotebookEdit) before a given prompt — file content only, session-local,
auto-cleaned with the session after ~30 days (configurable); it is "local undo", explicitly NOT
version control.** (Source: https://code.claude.com/docs/en/checkpointing.md.)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/checkpoint.record",
  "type": "object",
  "description": "The shape a fabric checkpoint-list endpoint WOULD return if built (planned). Grounded in the SDK's per-user-message restore points; no live endpoint emits this today.",
  "required": ["id"],
  "properties": {
    "id":          { "type": "string", "description": "the user-message uuid that is the restore point (SDK: UserMessage.uuid)" },
    "session_id":  { "type": "string", "description": "the owning session (checkpoints are session-local; tied to the session that created them)" },
    "prompt_text": { "type": ["string", "null"], "description": "the prompt sent at this point — what the TUI rewind menu lists per row" },
    "ts":          { "type": ["string", "null"], "format": "date-time" },
    "tracked_files": { "type": ["array", "null"], "items": { "type": "string" },
                       "description": "files snapshotted before this point (Write/Edit/NotebookEdit only — NEVER bash-touched, external, or other-session edits)" } } }
```
| field | type | volatile? | changed-by | address? -> resource | reality (Observed in docs, NOT measured against a live fabric endpoint) |
|---|---|---|---|---|---|
| id | string | no | — | — | the user-message uuid; surfaced by the SDK only when `replay-user-messages` is set, never by a Company endpoint today |
| session_id | string | no | — | session:// -> [[session]] (the owning session) | a checkpoint cannot outlive or cross its session — session-local by design |
| tracked_files | array | YES | each Write/Edit/NotebookEdit in the turn | — | file edits ONLY through those three tools are tracked; bash `rm`/`mv`/`cp`, external edits, and concurrent-session edits are NOT (a documented blind spot, not a fabric bug) |

**Field-reality honesty:** every row above is `Observed` from the Claude Code docs (cited), NOT
`Verified` against a running Company endpoint — because none exists. A fabric checkpoint resource
is `planned`; until built, the only real surfaces are the interactive TUI menu and the SDK calls
below, neither of which the Company backend wraps.

## State model
**State model: stateless.** A checkpoint is an immutable snapshot keyed to a message; it is never
mutated, only created (at prompt time) and consumed (by a restore). Restoring does not delete a
checkpoint — the original messages are preserved in the session transcript even after a summarize
or restore (source: checkpointing.md, "the original messages are preserved in the session
transcript").

## Caller
**No fabric caller exists: checkpoints are operated either by the human at the interactive TUI
(`/rewind`, or `Esc Esc` on an empty prompt) or by an Agent-SDK program holding the session
(`enable_file_checkpointing` + `rewind_files(uuid)`); the Company supervisor spawns headless
`claude -p` sessions and does NOT enable checkpointing, capture restore uuids, or call rewind.**
This is the central honesty of this entry. The supervisor transport ([[TRANSPORTS]]
`supervisor-http`) drives sessions through stream-json but exposes no checkpoint affordance — so
every op below is `planned` with the gap named, never `building`. Wiring it would be an
Agent-SDK-shaped capability owned by the headless/SDK lane (Atlas CC-18); F2 contracts WHAT it is
and records that the bridge is absent.

## Operations

## op: checkpoint.list
**`checkpoint.list` is the planned read of one session's restore points — the prompts you could
rewind to — with no Company endpoint today: the interactive equivalent is opening the `/rewind`
menu (it lists every prompt sent during the session), and the programmatic equivalent is
accumulating `UserMessage.uuid`s from the SDK response stream yourself.**
```contract:op
op: checkpoint.list
resource: checkpoint
kind: list
status: planned
direction: outbound
atlas: [CC-08.7]
tasks:
  - phrase: "show the points I can rewind this session to"
  - phrase: "list the restore points in a session"
  - alias: "what can I undo to"
  - alias: "show the rewind menu"
bindings:
  - { kind: tui, surface: "/rewind  (or Esc Esc on empty prompt) -> the menu lists each prompt sent this session", exposure: "n/a — interactive, not a Company endpoint", status: planned, note: "double-Esc with text in the box CLEARS the text instead (saved to input history); the menu opens only on an empty prompt" }
  - { kind: sdk, call: "accumulate UserMessage.uuid from the response stream (requires extraArgs {replay-user-messages: null})", exposure: "n/a — Agent SDK in-process, no fabric transport", status: planned, note: "the SDK has no list-checkpoints call; you build the list by capturing uuids as messages arrive" }
liveness: snapshot
live-twin: "none — static (the menu reflects the session's prompts as of when you open it)"
emits: []
verification:
  fabric-endpoint: {state: unverified, note: "NO Company endpoint exists — this is the named gap (§ Caller). Grounded only in checkpointing.md + agent-sdk/file-checkpointing.md."}
```
There is deliberately no request/response schema pinned to a live wire here: a `planned` op with
no binding has no captured reality to schema against (the §6 V11 rule — synthetics are marked, a
`planned` op carries no green-painted shapes). The Representation fence above is the shape a
future fabric endpoint WOULD serve.
Adjacent: [[checkpoint#op: checkpoint.restore]] (act on a listed point);
[[session#op: session.list]] (the fabric DOES list sessions — checkpoints live one level inside).

## op: checkpoint.restore
**`checkpoint.restore` is the planned rewind act — revert code, conversation, or both to a chosen
restore point — exposed today ONLY in-process: the TUI `/rewind` menu's three restore actions, or
the SDK's `rewind_files(uuid)` (which restores FILES on disk and explicitly does NOT rewind the
conversation, a difference the TUI does not have).**
```contract:op
op: checkpoint.restore
resource: checkpoint
kind: act
status: planned
direction: outbound
atlas: [CC-08.8, CC-08.9]
tasks:
  - phrase: "rewind this session to an earlier prompt"
  - phrase: "undo Claude's file edits back to a point"
    params: {scope: code}
  - phrase: "rewind the conversation but keep my current files"
    params: {scope: conversation}
  - phrase: "revert both code and conversation to a point"
    params: {scope: both}
  - alias: "undo the last changes"
  - alias: "go back to before that broke"
bindings:
  - { kind: tui, surface: "/rewind -> select a prompt -> 'Restore code and conversation' | 'Restore conversation' | 'Restore code'", exposure: "n/a — interactive", status: planned }
  - { kind: sdk, call: "rewind_files(checkpoint_id) / rewindFiles(checkpointId) after resuming the session with an empty prompt", exposure: "n/a — Agent SDK in-process", status: planned, note: "SDK restores FILES ONLY; conversation/context stay intact — NOT equivalent to the TUI's 'Restore conversation'/'both'. Requires enable_file_checkpointing on BOTH the original run and the resume." }
liveness: none
emits: []
consequences:
  - when: "scope=code (TUI 'Restore code', or SDK rewind_files)"
    expect: []
    evidence: "filesystem snapshot: files edited via Write/Edit/NotebookEdit since the point are reverted; created files are deleted; bash-touched/external/other-session edits are UNCHANGED (the documented blind spot). No fabric event is emitted — there is no fabric path."
  - when: "scope=conversation or both (TUI only)"
    expect: []
    evidence: "the session's live context is rewound to that message; the original prompt of the selected message is restored into the input field for re-send/edit. Observable only in the interactive session, not on any fabric stream."
correlate: []
verification:
  tui-restore:  {state: unverified, note: "interactive; documented behavior (checkpointing.md). No automated probe — there is no programmatic TUI driver in scope."}
  sdk-rewind:   {state: unverified, note: "rewind_files documented + example in agent-sdk/file-checkpointing.md; NOT run through any Company harness — the supervisor never enables checkpointing."}
  fabric-endpoint: {state: unverified, note: "NO Company endpoint — the named gap."}
```
### Errors
**Restore has no fabric error envelope because it has no fabric face; the in-process failure modes
are documented limits, not error codes.** The corpus records them as the honest boundaries a UI
must teach AROUND, not as catchable codes:
```contract:error
code: checkpoint.untracked-change-lost | http: n/a (no fabric face) | retryable: false
when: a UI offers "undo" expecting checkpoints to cover bash/external/directory changes
teach: "Checkpoints track ONLY Write/Edit/NotebookEdit file CONTENT, same session, local files. Bash commands (rm/mv/cp), directory create/move/delete, external edits, and other sessions' edits are NOT reverted. For anything beyond session-local file content the recovery path is git — checkpoints complement but do not replace version control. (Source: checkpointing.md Limitations.)"
```
### Interaction semantics
- **Preconditions:** a session with at least one prior prompt (so at least one restore point
  exists). The SDK path additionally requires `enable_file_checkpointing=true` set at run time AND
  on the resuming connection, plus `replay-user-messages` to have captured the uuid.
- **Effects:** scope=code reverts tracked file content; scope=conversation rewinds the live
  context to the selected message (TUI); scope=both does both. Created files are deleted on a code
  revert; modified files are restored to their content at the point.
- **Durability/irreversibility:** the original messages survive in the transcript regardless, so a
  restore is not a destructive delete of history — but file-content reverts ARE applied to disk
  immediately. There is no "redo".
- **Concurrency:** checkpoints are session-local; a concurrent session editing the SAME files is
  the one external-change case that CAN bleed in (documented).
### Live-ness
`liveness: none` — restore is an immediate in-process action; there is no stream and no fabric
cursor because there is no fabric path. A UI driving this today drives the TUI or the SDK
directly, not the Company backend.
Adjacent: [[checkpoint#op: checkpoint.list]] (pick the point first); for branching off instead of
rewinding-in-place, see [[session#op: session.create]] fork=true (the fabric DOES expose fork —
checkpointing.md itself points to fork as the "preserve the original, try a different approach"
alternative); for compressing context without reverting, see
[[context-window#op: context-window.compact]].

## op: checkpoint.summarize
**`checkpoint.summarize` is the planned targeted-compaction act — compress the conversation on ONE
side of a chosen point ("Summarize from here" / "Summarize up to here") to free context window
space WITHOUT touching files — exposed today only in the TUI `/rewind` menu; it is `/compact` made
selective, and it has no fabric endpoint.**
```contract:op
op: checkpoint.summarize
resource: checkpoint
kind: act
status: planned
direction: outbound
atlas: [CC-05.2]
tasks:
  - phrase: "compress the conversation from this point forward to free space"
    params: {direction: from-here}
  - phrase: "summarize the early setup but keep recent work in full"
    params: {direction: up-to-here}
  - alias: "shrink part of the conversation"
  - alias: "targeted compact at a checkpoint"
bindings:
  - { kind: tui, surface: "/rewind -> select a prompt -> 'Summarize from here' | 'Summarize up to here' (optional focus instructions accepted)", exposure: "n/a — interactive", status: planned }
liveness: none
emits: []
consequences:
  - when: "'Summarize from here' chosen"
    expect: []
    evidence: "the selected message + everything after it are replaced with an AI summary; earlier messages stay intact; the selected message's original prompt is restored into the input field. Files on disk UNCHANGED. Observable only in-session."
  - when: "'Summarize up to here' chosen"
    expect: []
    evidence: "messages BEFORE the selected one are replaced with a summary; the selected message and everything after stay intact; you remain at the end of the conversation, input empty. Files UNCHANGED."
correlate: []
verification:
  tui-summarize: {state: unverified, note: "documented in checkpointing.md Restore-vs-summarize; no programmatic driver, no fabric endpoint."}
```
The relationship a UI must understand: `checkpoint.summarize` is to
[[context-window#op: context-window.compact]] what a scalpel is to a sweep — same compression
mechanism, but you choose WHICH side of a point to compress, and the original messages are still
kept in the transcript for Claude to reference. Use it to discard a side-discussion while keeping
early context, or to compress setup while keeping recent work.
Adjacent: [[context-window#op: context-window.compact]] (whole-conversation compaction);
[[checkpoint#op: checkpoint.restore]] (the reverting siblings in the same `/rewind` menu).

## Errors
**This resource has no fabric error vocabulary — it has no fabric face.** Its only failure modes
are the documented LIMITS recorded under [[checkpoint#op: checkpoint.restore]]
(untracked-change classes: `checkpoint.untracked-change-lost`) and the SDK precondition that
`enable_file_checkpointing` must be set on both the original and resuming connections. When a
Company checkpoint endpoint is built (Atlas CC-18, SDK-shaped), it will adopt the uniform envelope
([[CONVENTIONS]]); that is a future obligation, recorded here, not a present capability.

## Links
**The only live cross-resource address this entry carries is `session_id` -> [[session]]
(`session://`, accepted by session.get/watch): a checkpoint is always one level inside exactly one
session.** Checkpoint ids themselves are user-message uuids, NOT a dereferenceable fabric scheme —
no `checkpoint://` is claimed, because no accepting op exists (the §6 V7 dereferenceability law
forbids claiming a dead-end scheme). The transcript that preserves the underlying messages after a
restore/summarize is [[transcript]] (the durable, exported memory of the same session).
