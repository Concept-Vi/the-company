---
type: contract-coverage
build: capability-fabric
captured: 2026-06-12
status: HAND-DERIVED coverage pass (F9.3) — tools/coverage.py NOT yet built; this is the
  machine-checkable MAP, computed by reading every resources/*.md frontmatter+atlas tag against
  atlas/FEATURE-ATLAS.md. Layer-1 (CONTRACTED) only; Layer-2 (DEMONSTRATED — task verdicts /
  load.jsonl) is empty because no driving harness has run (no op is `live`).
source-of-truth: atlas/FEATURE-ATLAS.md (35 classes CC-01…CC-35; affordances CC-nn.m) ↔
  resources/*.md per-op `atlas:`+`status:` ↔ atlas/OUT-OF-SCOPE.md ↔ atlas/INVENTORY-EXCLUSIONS.md
honesty: per CONTRACT-FORMAT §4.2 — `building` = code exists behind a cited real endpoint (NOT
  flipped `live`); `planned` = data model contracted, company backend named-as-gap. NOTHING here
  is `live`. Coverage grain is the AFFORDANCE; the class roll-up is reported alongside.
---

# COVERAGE — the 35 Feature-Atlas classes ↔ resource entries ↔ status (F9.3)

The F9.3 bar: **every Feature-Atlas class mapped to the resource entries that cover it, with an
honest status, and every gap named — never silent.** This map is the gap-pressure instrument for
the build: it tells the next lanes exactly what is starved (no entry at all), what is contracted
but backend-less (the F2–F8→backend gap list), and confirms there are no silent holes.

## Headline counts (class grain — the F9.3 unit)

| bucket | count | classes |
|---|---|---|
| **COVERED** (≥1 affordance reached by a `building` op — real cited endpoint) | **8** | CC-05, CC-07, CC-08, CC-09, CC-18, CC-23, CC-25, CC-35 |
| **PLANNED-ONLY** (mapped, but EVERY covering op is `planned` — no real endpoint yet) | **2** | CC-10, CC-20 |
| **UNMAPPED** (no affordance seeded, no op — starvation) | **25** | CC-01·02·03·04·06·11·12·13·14·15·16·17·19·21·22·24·26·27·28·29·30·31·32·33·34 |
| total | **35** | — |

Affordance grain (the finer instrument): **48 affordances defined in FEATURE-ATLAS, 48 reached by
≥1 op (zero unmapped affordances), 0 affordances out-of-scope** (OUT-OF-SCOPE.md is empty of true
exclusions — every touched affordance is `building` or `planned`, both IN scope). Of the 48
affordances: **21 reached by a `building` op**, **27 reached only by `planned` ops**.

> The asymmetry that matters: at AFFORDANCE grain nothing the lanes TOUCHED is unmapped — the holes
> are entire CLASSES no lane has opened yet (25/35). This is the gap-pressure starvation read.

---

## Layer 1 — CONTRACTED (the claims): every defined affordance → covering op(s) → status

Statuses are the op's own frontmatter `status:` (verified by grep 2026-06-12). A class is COVERED
iff ≥1 of its affordances is reached by a `building`/`live` op.

### CC-05 · Context Management & Window Optimization — **COVERED** (mixed)
| affordance | op(s) | entry | status |
|---|---|---|---|
| CC-05.1 carry prior context into a continued conversation | session.create · session.post | session.md | **building** |
| CC-05.2 targeted compaction (one side of a point) | checkpoint.summarize | checkpoint.md | planned |
| CC-05.3 read live context-window usage/breakdown | context-window.get | context-window.md | planned |
| CC-05.4 whole-conversation compaction (manual+auto) | context-window.compact | context-window.md | planned |
| CC-05.5 reset/clear context between tasks | context-window.clear | context-window.md | planned |
_Gap: 05.2–05.5 are in-process TUI/SDK features the supervisor does not bridge; only 05.1 (resume/fork) rides a real endpoint._

### CC-07 · Permissions & Approval Modes — **COVERED**
| affordance | op(s) | entry | status |
|---|---|---|---|
| CC-07.1 read the permission posture a session runs under | permission.get | permission.md | **building** |
| CC-07.2 spawn under a chosen permission mode | permission.act | permission.md | planned |
| CC-07.3 constrain tool surface (allow/deny/ask) | permission.act | permission.md | planned |
| CC-07.4 change a live session's mode mid-session | permission.act | permission.md | planned |
_Gap: only the fabric-wide posture READ is real (= fabric-config.get lens); spawn() carries no permission param (runtime/session_supervisor.py:254)._

### CC-08 · Checkpoints & Session Management — **COVERED**
| affordance | op(s) | entry | status |
|---|---|---|---|
| CC-08.1 list/browse every session this machine has run | session.list | session.md | **building** |
| CC-08.2 inspect one session's full record | session.get | session.md | **building** |
| CC-08.3 resume a closed session with context intact | session.create · session.post(wake) | session.md | **building** |
| CC-08.4 fork a session without touching the original | session.create(fork) · session.post(consult) | session.md | **building** |
| CC-08.5 watch one live session's activity | session.watch · events.watch | session.md · events.md | **building** |
| CC-08.6 search the content of past sessions | transcript.search | transcript.md | planned |
| CC-08.7 list a session's within-session restore points | checkpoint.list | checkpoint.md | planned |
| CC-08.8 rewind code/conversation to a restore point | checkpoint.restore | checkpoint.md | planned |
| CC-08.9 restore FILES ONLY (SDK rewind_files) | checkpoint.restore | checkpoint.md | planned |
_Gap: native session-fork (08.4) is the one realized native-lifecycle capability; in-session checkpointing (08.7–08.9) and transcript search (08.6) are unbridged._

### CC-09 · Subagents & Agent Teams — **COVERED**
| affordance | op(s) | entry | status |
|---|---|---|---|
| CC-09.1 send a message/question to another session | session.post | session.md | **building** |
| CC-09.2 fan one question to N forked consultants | session.post(consult) | session.md | **building** |
| CC-09.3 read a session's inbox | session-message.list | session-message.md | **building** |
| CC-09.4 aggregate a fan's replies under one thread | session-message.list(thread=) | session-message.md | **building** |
| CC-09.5 define/spawn a subagent | agent-team.list · agent-team.act | agent-team.md | planned |
| CC-09.6 create a native agent TEAM | agent-team.list · agent-team.act | agent-team.md | planned |
| CC-09.7 assign tasks / require plan-approval | agent-team.act | agent-team.md | planned |
| CC-09.8 message a teammate / shut one down | agent-team.act | agent-team.md | planned |
_Gap: the fabric consult-fan (09.1–09.4) is the LIVE parallel-worker path; NATIVE subagents/teams (09.5–09.8) have no company control surface._

### CC-10 · Model Selection & Reasoning — **PLANNED-ONLY** (warn)
| affordance | op(s) | entry | status |
|---|---|---|---|
| CC-10.1 list available models/aliases | model.list | model.md | planned |
| CC-10.2 select the model a session runs | model.act | model.md | planned |
| CC-10.3 set reasoning effort level | model.act | model.md | planned |
| CC-10.4 toggle extended thinking | model.act | model.md | planned |
| CC-10.5 set a fallback model chain | model.act | model.md | planned |
_Whole class backend-less: spawn() passes no --model/--effort/--fallback-model (runtime/session_supervisor.py:261-265). A UI can RENDER the model contract; no company endpoint sets it._

### CC-18 · Headless & Programmatic Use — **COVERED**
| affordance | op(s) | entry | status |
|---|---|---|---|
| CC-18.1 spawn a supervised headless session | session.create | session.md | **building** |
| CC-18.2 inject a turn programmatically | session.inject · headless-control.act | session.md · headless-control.md | **building** |
| CC-18.3 interrupt an in-flight turn | session.interrupt · headless-control.act | session.md · headless-control.md | **building** (interrupt unproven vs real turn — honest) |
| CC-18.4 tear down a session (no orphans) | session.stop | session.md | **building** |
| CC-18.5 observe the machine-readable fleet event flow | events.list · events.watch · session.watch | events.md · session.md | **building** |
| CC-18.6 read a session's stream-json output fold | headless-control.watch | headless-control.md | **building** |
| CC-18.7 choose output-format / structured-output / partial streaming | headless-control.act | headless-control.md | planned |
_Gap inside a COVERED class: 18.7 (output-format/json-schema/--include-partial-messages) is hardcoded in the supervisor spawn — named on headless-control.act bindings._

### CC-20 · Cost Management & Usage Tracking — **PLANNED-ONLY** (warn)
| affordance | op(s) | entry | status |
|---|---|---|---|
| CC-20.1 read what a session/turn has cost | cost-usage.get | cost-usage.md | planned |
| CC-20.2 usage broken down by model/skill/plugin/subagent | cost-usage.get | cost-usage.md | planned |
| CC-20.3 cap a headless run's spend (--max-budget-usd) | cost-usage.act | cost-usage.md | planned |
_Whole class backend-less but CODE-CITED adoption path: the supervisor consumes the result event's cost/usage and DISCARDS it (runtime/session_supervisor.py _turn_done, ~L369/380/384). Stamp ModelUsage onto agent_sessions.turn -> CC-20.1/.2 become `building` reads over [[events]] with zero new transport._

### CC-23 · CLAUDE.md, Memory & Persistent Context — **COVERED**
| affordance | op(s) | entry | status |
|---|---|---|---|
| CC-23.1 durable filtered memory of every past session | transcript.export · transcript.search | transcript.md | **building** (export) / planned (search) |
| CC-23.2 semantically search the embedded knowledge corpora | knowledge-corpus.list · knowledge-corpus.search | knowledge-corpus.md | **building** (verified-by-use) |
| CC-23.3 list loaded CLAUDE.md/memory files | claude-memory.list | claude-memory.md | planned |
| CC-23.4 edit a memory/instruction file | claude-memory.update | claude-memory.md | planned |
| CC-23.5 remember/forget a learning | claude-memory.act | claude-memory.md | planned |
_Gap: corpus search + transcript export are real; the CLAUDE.md/auto-memory data model (23.3–23.5) has no company endpoint (grep-verified empty)._

### CC-25 · Configuration & Settings System — **COVERED**
| affordance | op(s) | entry | status |
|---|---|---|---|
| CC-25.1 read the fabric's live operating config (cap/timeout/permission/bind) | fabric-config.get | fabric-config.md | **building** |
_Note: only the FABRIC's own posture is contracted; the broad Claude Code settings system (settings.json, env, /config) is unmapped — see Silent-gap watch._

### CC-35 · Glossary & Best Practices — **COVERED**
| affordance | op(s) | entry | status |
|---|---|---|---|
| CC-35.1 look up a Claude Code term/best-practice from the docs mirror | knowledge-corpus.search | knowledge-corpus.md | **building** (verified-by-use, domain=claude-code-atlas) |

---

## The two flagged lists (F9.3 deliverables)

### A) STARVATION — 25 classes with NO entry at all (gap-pressure read)
No lane has opened these. They are the entire-class holes; nothing is silently missing — every one
is named here. (These are the future-lane backlog at CLASS grain.)

| class | what it is | nearest existing lane / note |
|---|---|---|
| CC-01 | CLI & Session Entry Points | partially adjacent to session.create CLI binding; the CLI surface itself uncontracted |
| CC-02 | Interactive Surfaces (Terminal/Desktop/Web/IDE) | the disposable harness UI is explicitly out (feedback-company-ui-disposable); a real surface contract is future |
| CC-03 | Slash Commands & Built-In Skills | /memory·/usage·/cost noted as built-ins in INVENTORY-EXCLUSIONS; no class entry |
| CC-04 | Keyboard Shortcuts & Keybindings | interactive-only; no fabric face |
| CC-06 | Git Integration & Worktrees | agent-team `isolation: worktree` is mentioned in a schema, not contracted as a class |
| CC-11 | MCP Integration | the fabric IS driven through MCP, but MCP-as-a-managed-capability is uncontracted |
| CC-12 | Hooks & Automation | PreCompact / InstructionsLoaded / PreToolUse cited in prose; no hook resource |
| CC-13 | Plugins, Skills & Extension Packaging | the F4 lane (claude-memory report names it); not landed |
| CC-14 | Voice & Audio I/O | duplex/binary-stream liveness pre-exists in the FORMAT for it; no entry |
| CC-15 | Remote Control & Mobile Access | Tailscale/PWA exists in the Company but uncontracted here |
| CC-16 | Code Intelligence (LSP) & Symbol Navigation | none |
| CC-17 | Computer Use & Web Access | duplex liveness pre-exists; no entry |
| CC-19 | AI-Driven Code Review & Analysis | none |
| CC-21 | Scheduled Tasks, Routines & Automation | none |
| CC-22 | Dynamic Workflows & Task Coordination | none |
| CC-24 | Authentication & Account Management | the `authed` exposure value pre-exists for it; no entry |
| CC-26 | Terminal Configuration & Output Styling | statusline cited in context-window prose; no entry |
| CC-27 | Extensibility & Customization Patterns | none |
| CC-28 | Enterprise & Admin Features | Usage&Cost/Analytics admin APIs noted (INVENTORY-EXCLUSIONS); no class entry |
| CC-29 | Cloud Provider Integrations (Bedrock/Vertex/Foundry) | model.md notes provider-agnosticism; no entry |
| CC-30 | CI/CD Integrations | none |
| CC-31 | Large Codebase Support & Dev Containers | none |
| CC-32 | Data Privacy, Security & Compliance | transcript redaction touches it; no class entry |
| CC-33 | Diagnostics, Debugging & Troubleshooting | errors.md cited throughout; no class entry |
| CC-34 | Installation, Updates & Platform Support | none |

### B) BACKEND-GAP — classes/affordances contracted but with NO real endpoint (the F2–F8->backend list)
The build list for a future backend lane. Two whole PLANNED-ONLY classes, plus planned affordances
inside COVERED classes. Each carries the named gap and (where found) the code-cited adoption path.

| class | affordances `planned` | the named backend gap | adoption path |
|---|---|---|---|
| **CC-10** (planned-only) | 10.1–10.5 | spawn() passes no --model/--effort/--fallback-model | add model block to /spawn body -> flags |
| **CC-20** (planned-only) | 20.1–20.3 | supervisor DISCARDS result-event cost/usage (code-cited) | stamp ModelUsage onto agent_sessions.turn |
| CC-05 | 05.2,05.3,05.4,05.5 | in-process TUI/SDK only; supervisor doesn't bridge context-window | SDK/telemetry-shaped face (CC-18-adjacent) |
| CC-07 | 07.2,07.3,07.4 | spawn() carries no permission param | permission block on /spawn + mid-session control_request |
| CC-08 | 08.6,08.7,08.8,08.9 | transcript vault unregistered; checkpointing not enabled on spawns | register claude-sessions vault; SDK checkpoint face |
| CC-09 | 09.5,09.6,09.7,09.8 | no native subagent/team control surface (driven inside a lead) | /teams + /team supervisor endpoints |
| CC-18 | 18.7 | supervisor hardcodes --output-format stream-json, no --json-schema/partial | output controls on /spawn body |
| CC-23 | 23.1(search),23.3,23.4,23.5 | no CLAUDE.md/auto-memory company endpoint (grep-verified empty) | scope-validated memory walk + guarded write |

### C) SILENT-GAP WATCH — places coverage could be quietly overstated, checked and cleared
- **OUT-OF-SCOPE.md is empty of true exclusions.** Confirmed not a hidden hole: every touched
  affordance is `building` or `planned` (both in scope); no affordance is silently dropped. CLEAR.
- **INVENTORY-EXCLUSIONS.md endpoint exclusions are all justified**: the external Anthropic
  admin/analytics API, the built-in `/memory`·/`usage`·/`cost` slash commands, and the substrate-mcp
  tools (inventoried against the external server, not the company `OPS` join). None is a company
  route counted as a gap; none is a company route silently skipped. CLEAR.
- **CC-25 scope creep risk**: `fabric-config.get` covers ONLY the fabric's own posture, NOT the
  full Claude Code settings system. CC-25 is reported COVERED on that narrow basis — flagged here so
  a reader does not read "CC-25 covered" as "all of settings contracted". The broad settings surface
  is effectively unmapped within a nominally-covered class. NAMED, not silent.
- **Multi-affordance ops**: session.post carries 5 affordance tags (CC-09.1/.2, CC-08.3/.4, CC-05.1);
  this map credits each affordance to the op individually, NOT a smear (per CONTRACT-FORMAT §7 Layer-2
  rule). Layer-2 demonstrated credit will come only from blind-author task verdicts, none of which
  exist yet — so NO affordance here is marked demonstrated. NO green-paint.

---

## Layer 2 — DEMONSTRATED (proof): EMPTY by honest construction
No op in this corpus is `live`; the corpus-only driving harness (tools/coverage.py, the battery,
load.jsonl, drops.jsonl) has not been built or run. Therefore:
- demonstrated affordances: **0 / 48** (no task verdicts exist).
- starvation-by-load (zero-load entries): **uncomputable** — load.jsonl does not exist yet.
This is the expected state at this build stage (CONTRACT-FORMAT §7.5 / README honest-status): the
CONTRACTED layer is the truth surface; DEMONSTRATED waits on the harness. Stated, never decorated.

## Regeneration note
This file is HAND-DERIVED (tools/coverage.py per CONTRACT-FORMAT §1/§7 is not yet built). When that
generator lands it overwrites coverage/coverage.json + renders this map; until then this is the
loud, honest manual coverage pass. Recompute by re-reading every `resources/*.md` `atlas:`+`status:`
against `atlas/FEATURE-ATLAS.md` — every status here was grep-verified 2026-06-12.
