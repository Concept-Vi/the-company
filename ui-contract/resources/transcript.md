---
type: contract-entry
resource: transcript
summary: The filtered, redacted markdown memory of one past session — a regenerable projection of its jsonl, exported on a 20-minute timer under the quiesce law, destined for the claude-sessions search vault.
schemes: []
status: building
relates-to: ["[[session]]", "[[events]]"]
---

# Resource: transcript

## Identity
**A transcript is identified by its session uuid, materialized at
`~/corpora/claude-sessions/<project>/<session-uuid>.md` — a derived render the source jsonl
always outranks; no address scheme is claimed (plain files, plainly readable).**
The corpus is real and on disk (1,040 markdown files measured 2026-06-12); the SEARCH surface
over it is the planned half (vault registration is an explicitly-held later step).

## Representation
**One markdown file per session: an envelope frontmatter, `## Turn N — Tim/Claude` body
sections of kept conversation, and `## Subagent:` rollups — everything secret-bearing is
structurally stripped, then regex-redacted, with measured ~3% size retention.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/transcript.frontmatter",
  "type": "object",
  "required": ["type", "session_id", "title", "title_source"],
  "properties": {
    "type":         { "const": "session-transcript" },
    "session_id":   { "type": "string" },
    "project":      { "type": "string" },
    "cwd":          { "type": "string" },
    "git_branch":   { "type": "string" },
    "title":        { "type": "string" },
    "title_source": { "enum": ["ai-title", "custom-title", "last-prompt", "first-user-turn", "untitled"] },
    "started":      { "type": "string" },
    "last_event":   { "type": "string" },
    "cc_version":   { "type": "string" },
    "turns":        { "type": "integer" },
    "subagents":    { "type": "integer" },
    "source_bytes": { "type": "integer" },
    "exported_at":  { "type": "string", "format": "date-time" } } }
```
| property | reality (full backfill, measured via the registered systemd unit, 2026-06-11/12) |
|---|---|
| coverage | 1,040 md from 1,065 mains (the gap = empty sessions + quiesce-live ones — re-caught next cycle) |
| size | 1.44 GB jsonl → 44 MB md (≈3.0%; the filter law holding) |
| filter law | KEEP user+assistant text, ai-title, one-line tool traces (`> tools: Bash(git push …)`); STRIP tool_result bodies + top-level toolUseResult (where secrets land), tool_use bodies, attachments/bookkeeping, system-reminder/Caveat/command/interrupt/isMeta texts, thinking (flag, default off); REDACT sk-/JWT/xox/AKIA/gh*/hf_/AIza/private-key/assignment → `[redacted:<kind>]` |
| leak audit | full-corpus structural greps = zero hits; 2 live hf-tokens + 1 assignment caught and redacted on real data |
| freshness | only sessions quiesced >15 min export; write-only-if-different (idempotent re-runs) |
| source safety | READ-ONLY on ~/.claude — proven byte-identical source after a run |

## State model
**State model: stateless.** (A transcript is a projection: regenerated in place when its
source grows, never versioned, never hand-edited.)

## Caller
**No identity: transcripts are local files any local consumer may read; the export job runs
as the operator's user timer.**

## Operations

## op: transcript.export
**`transcript.export` fires the jsonl→markdown export job — normally a 20-minute systemd
timer you ARM rather than an act you call per-transcript; one invocation sweeps every
quiesced session idempotently.**
```contract:op
op: transcript.export
resource: transcript
kind: act
status: building
direction: outbound
atlas: [CC-23.1]
tasks:
  - phrase: "refresh the session-transcript corpus now"
  - phrase: "turn the transcript exporter on"
  - alias: "export my sessions to markdown"
bindings:
  - { kind: cli, command: "company up agent-sessions-exporter   (arms the 20-min timer; one-shot: systemctl --user start company-agent-sessions-exporter.service)", transport: cli-local, exposure: "exposure.json#cli-local" }
liveness: none
emits: []                       # deliberately NO fabric events — the importer/exporter never write events (single-writer law)
consequences:
  - when: "a sweep completes"
    expect: []
    evidence: "filesystem snapshot: new/updated md under ~/corpora/claude-sessions/ + the run summary on the unit's journal (counts, bytes, redactions, residue — fail-loud exit 1 on any per-file error)"
correlate: []
verification:
  full-backfill: {state: probe-verified, run: "fired through systemd 2026-06-11 — 1,035 md / 1,065 mains, 1.44GB→44MB, 0 errors; corpus re-measured 1,040 on 2026-06-12", date: 2026-06-12}
```
Adjacent: [[transcript#op: transcript.search]] is what the corpus is FOR;
[[session#op: session.get]] for the live registry view of the same session.

## op: transcript.search
**`transcript.search` is the content-recall read over every session that ever ran — PLANNED:
the corpus exists, the `claude-sessions` substrate vault it searches through is not yet
registered, and the merged endpoint (registry names/recency + transcript content, one read,
two backends) is not yet built.**
```contract:op
op: transcript.search
resource: transcript
kind: search
status: planned
direction: outbound
atlas: [CC-08.6, CC-23.1]
tasks:
  - phrase: "what did a past session decide about X"
  - phrase: "find the session that edited a given file"
  - alias: "search my session history"
  - alias: "recall a past conversation"
bindings:
  - { kind: http, method: GET, path: "/api/agent_sessions/search?q=", transport: bridge-http, exposure: "exposure.json#bridge-http", status: planned, note: "the merged-search contract: one endpoint, registry + vault backends, merged results" }
liveness: snapshot
live-twin: "none — static (a search over history)"
emits: []
verification:
  probe-set: {state: unverified, note: "the F1.4 bar is the PINNED 5-probe set (frozen in the guide BEFORE export, authored from memory never from the corpus) — 4/5 must hit once the vault is registered; a miss is a gap-pressure drop, not a probe rewrite"}
```
Until this flips, the honest paths are: registry title/name search via
[[session#op: session.list]] `q=`, and direct filesystem reads/greps over
`~/corpora/claude-sessions/` (granted — they are plain markdown).
Adjacent: [[session#op: session.list]] (the registry half of the merge).

## Errors
**This resource fails loud at the job boundary, not per-read: any per-file export error is
collected, printed, and exits non-zero on the unit's journal; unknown residue line-types are
counted and reported (residue-as-data), never silently swallowed.**

## Links
**`session_id` in every frontmatter dereferences to [[session]] (`session://<id>` accepted by
session.get/post/watch); `project`/`cwd` join the registry record's same-named envelope
fields — the transcript and the registry row are two projections of one session.**
