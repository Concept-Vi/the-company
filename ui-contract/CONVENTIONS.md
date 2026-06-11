---
type: contract-conventions
captured: 2026-06-12
status: living — updated in place (no-versioning law)
---

# CONVENTIONS — uniform vocabulary, envelopes, laws

## Uniform op verbs (closed — anything else is a resource or a named act)
**list · get · create · update · delete · act (named acts) · watch · search**

## Named-act registry (append-only — one line per act; lanes ADD lines, never rewrite)
- `post` — on `session`: append a durable routed message intent (deliver/wake/consult/auto/queue).
- `inject` — on `session`: direct synchronous push of one turn into a SUPERVISED session (no mailbox).
- `interrupt` — on `session`: stop the in-flight turn of a busy supervised session.
- `stop` — on `session`: tear down supervision of one session (subprocess killed; record stays, closed).
- `export` — on `transcript`: fire/arm the jsonl→markdown export job.

## The uniform error envelope (target shape) + per-face carriers — FIELD-REALITY HONESTY
Target (CONTRACT-FORMAT §9.5, a code-side obligation): every face emits
`{error: {code, message, teach, details?, retryable}}`.

**Reality as of 2026-06-12 — the envelope is NOT yet implemented on any face.** What each
face actually emits today (every refusal DOES carry teach-text; structured codes do not exist
in the wire shapes yet — error `code:` values in this corpus are contract-assigned names,
machine-emission pending):
| face | carrier today |
|---|---|
| supervisor-http | HTTP status (400/404/409/429/500) + JSON `{"error": "<teaching text>"}` |
| mcp-company | MCP tool error (raised ValueError → SDK error result), message IS the teaching text |
| cli-local | stderr teaching text + exit code 1 (supervisor-down teaches `company up session-supervisor`) |
| bridge-http | (no fabric routes yet — planned) |

HTTP status mapping used by the supervisor: 400 malformed body/missing field · 404 unknown
path/session · 409 state conflict (busy/closed/not-busy) · 429 over the concurrency cap ·
500 internal (fail-loud, never silent).

## Cursor / pagination law
Reads over ordered logs are seq-cursor shaped: pass `since` (exclusive; `-1` = everything),
results come OLDEST-first, `limit` keeps the FIRST N after the cursor (pagination never
skips), and the response's `next_since` (or the last row's `seq`) is your next call's
`since`. Two cursor disciplines exist and are both contracted: CLIENT-HELD (you keep
`next_since`; re-reading is safe, nothing is consumed destructively — the inbox read) and
DURABLE PER-CONSUMER REFS (`agent-mail-cursor://<consumer>` — monotonic, regression refused;
the supervisor's own mailbox cursor is a byte-offset ref `agent_sessions/cursor:supervisor`,
an internal detail stated for honesty, not a consumer surface).

## Address grammar
- `session://<id>` — LIVE scheme (in `contracts/address.py` SCHEMES): a Claude Code session.
  `<id>` is canonically the claude session uuid; the supervisor also accepts its own local
  handles (`as-<8 hex>`) minted before init names the uuid.
- `cas://<hash>` — content-addressed body store (mail bodies ride it; reads resolve it for you).
- PLANNED, not in code yet (CONTRACT-FORMAT §9.7 obligation): `msg://`, `thread://`,
  `consumer://`. Today mail ids are plain strings `mail-<seq>` and thread ids are plain
  strings (defaulting to the founding mail id) — they are NOT dereferenceable addresses, and
  no entry in this corpus claims them as schemes.

## Purpose-free vocabulary (V5 seed list — extendable, never shrinkable)
Banned in Description/Semantics prose: "the user wants", "the UI should", "button", "panel",
"screen", "click", "frontend", "page". `tasks:`/`alias:` fields are EXEMPT (the deliberate
retrieval bridge to consumer vocabulary). Escapes need an inline `lint-ok:` justification.

## Journey ambiguity classes (V19 — each MUST have a journey)
- "history vs live vs messages": a transcript is the past, a watch is the present, mail is
  addressed communication — `journeys/message-and-read-reply.md` carries the disambiguation.
- "session state management" (F2): rewind/restore REVERTS, targeted-summarize COMPRESSES one
  side, compact COMPRESSES the whole conversation, clear DISCARDS-and-parks, fork COPIES-and-
  preserves — five overlapping mechanisms, five distinct meanings. `journeys/manage-session-state.md`
  carries the chooser (intent -> mechanism) and the two deciding axes (touches-files? preserves-original?).
