---
type: contract-atlas
captured: 2026-06-12
status: class ids FROZEN (CC-01…CC-35); affordances grow append-only per lane
source: the 35 numbered classes verified verbatim against "Obsidian Builder/Spaces/Claude Code Atlas/Feature Atlas.md" (grep '^## [0-9]' = 35; the P0 audit's independent source)
---

# FEATURE-ATLAS — the 35 capability classes + affordances (coverage grain = the affordance)

Class ids are frozen. Affordance sub-ids (CC-nn.m) are appended by the lane that first
contracts them — append-only, never renumbered. F1 (Session Fabric) seeded the affordances
below; F2–F8 lanes append theirs under their classes.

| id | class |
|---|---|
| CC-01 | CLI & Session Entry Points |
| CC-02 | Interactive Surfaces (Terminal, Desktop, Web, IDE) |
| CC-03 | Slash Commands & Built-In Skills |
| CC-04 | Keyboard Shortcuts & Keybindings |
| CC-05 | Context Management & Window Optimization |
| CC-06 | Git Integration & Worktrees |
| CC-07 | Permissions & Approval Modes |
| CC-08 | Checkpoints & Session Management |
| CC-09 | Subagents & Agent Teams |
| CC-10 | Model Selection & Reasoning |
| CC-11 | MCP (Model Context Protocol) Integration |
| CC-12 | Hooks & Automation |
| CC-13 | Plugins, Skills, & Extension Packaging |
| CC-14 | Voice & Audio Input/Output |
| CC-15 | Remote Control & Mobile Access |
| CC-16 | Code Intelligence (LSP) & Symbol Navigation |
| CC-17 | Computer Use & Web Access |
| CC-18 | Headless & Programmatic Use (SDK & Automation) |
| CC-19 | AI-Driven Code Review & Analysis |
| CC-20 | Cost Management & Usage Tracking |
| CC-21 | Scheduled Tasks, Routines & Automation |
| CC-22 | Dynamic Workflows & Task Coordination |
| CC-23 | CLAUDE.md, Memory & Persistent Context |
| CC-24 | Authentication & Account Management |
| CC-25 | Configuration & Settings System |
| CC-26 | Terminal Configuration & Output Styling |
| CC-27 | Extensibility & Customization Patterns |
| CC-28 | Enterprise & Admin Features |
| CC-29 | Cloud Provider Integrations (Bedrock, Vertex, Foundry) |
| CC-30 | CI/CD Integrations (GitHub Actions, GitLab, Automation) |
| CC-31 | Large Codebase Support & Dev Containers |
| CC-32 | Data Privacy, Security & Compliance |
| CC-33 | Diagnostics, Debugging & Troubleshooting |
| CC-34 | Installation, Updates & Platform Support |
| CC-35 | Glossary & Best Practices |

## Affordances seeded by F1 (Session Fabric)

### CC-05 · Context Management & Window Optimization
- CC-05.1 — carry full prior context into a continued conversation (resume preserves memory)

### CC-08 · Checkpoints & Session Management
- CC-08.1 — list/browse the catalog of every session this machine has run
- CC-08.2 — inspect one session's full record (identity, envelope, liveness)
- CC-08.3 — resume a closed session with context intact (`--resume`)
- CC-08.4 — fork a session without touching the original (`--fork-session`)
- CC-08.5 — watch one live session's activity as it happens
- CC-08.6 — search the content of past sessions (transcript memory)

### CC-09 · Subagents & Agent Teams
- CC-09.1 — send a message/question to another session
- CC-09.2 — fan one question to N parallel forked consultants
- CC-09.3 — read a session's inbox (messages + replies addressed to it)
- CC-09.4 — aggregate a fan's replies under one thread

### CC-18 · Headless & Programmatic Use (SDK & Automation)
- CC-18.1 — spawn a supervised headless session programmatically
- CC-18.2 — inject a turn into a running session programmatically
- CC-18.3 — interrupt an in-flight turn
- CC-18.4 — tear down a session programmatically (no orphans)
- CC-18.5 — observe the machine-readable event flow of the fleet

### CC-23 · CLAUDE.md, Memory & Persistent Context
- CC-23.1 — durable, filtered, redacted memory of every past session (transcript corpus)

### CC-25 · Configuration & Settings System
- CC-25.1 — read the fabric's live operating configuration (cap, timeout, permission, bind)

## Affordances seeded by F2 (Sessions & lifecycle deep — context mgmt + checkpoints)

### CC-05 · Context Management & Window Optimization (deep)
- CC-05.2 — targeted compaction: compress ONE side of a chosen point ([[checkpoint#op: checkpoint.summarize]] — TUI /rewind "Summarize from/up to here")
- CC-05.3 — read live context-window usage + breakdown by category ([[context-window#op: context-window.get]] — /context, statusline feed)
- CC-05.4 — whole-conversation compaction, manual and automatic, with optional focus ([[context-window#op: context-window.compact]] — /compact, auto-compaction, microcompaction)
- CC-05.5 — reset context between tasks / ask without growing it ([[context-window#op: context-window.clear]] — /clear, /btw)

### CC-08 · Checkpoints & Session Management (deep)
- CC-08.7 — list a session's within-session restore points ([[checkpoint#op: checkpoint.list]] — /rewind menu / SDK UserMessage.uuid)
- CC-08.8 — rewind code and/or conversation to a restore point ([[checkpoint#op: checkpoint.restore]] — /rewind restore actions / SDK rewind_files)
- CC-08.9 — restore FILES ONLY to a point, conversation intact (the SDK rewind_files semantics; a sub-mode of [[checkpoint#op: checkpoint.restore]])

> F2 honesty: every CC-05.2–05.5 and CC-08.7–08.9 affordance is `planned` — these are
> in-process Claude Code features (interactive TUI + Agent SDK) the Company supervisor does NOT
> yet bridge. The fabric-fork affordance CC-08.4 (seeded by F1) is the one native-lifecycle
> capability that IS realized through a real endpoint ([[session#op: session.create]] fork=true);
> checkpointing.md itself names fork as the "preserve the original, try a different approach"
> alternative to in-place rewind. Grounded in: checkpointing.md, agent-sdk/file-checkpointing.md,
> context-window.md, sessions.md (branch-a-session), glossary.md, how-claude-code-works.md,
> monitoring-usage.md, statusline.md, errors.md (all in vault claude-code-atlas, fetched 2026-06-10).

## Affordances seeded by F6 (Knowledge & memory — classes 20, 23)

### CC-20 · Cost Management & Usage Tracking
- CC-20.1 — read what a session/turn has cost (per-turn token + estimated cost; the ModelUsage shape)
- CC-20.2 — read usage broken down by model / skill / plugin / subagent (OTel metrics, /usage attribution, org Usage & Cost API)
- CC-20.3 — cap a headless run's spend (`--max-budget-usd` — stops the session when exceeded)

### CC-23 · CLAUDE.md, Memory & Persistent Context
- CC-23.2 — semantically search the embedded knowledge corpora (Atlas + platform-docs + repo-exocortex)
- CC-23.3 — list the CLAUDE.md/memory files loaded in a session (the /memory inventory + scope hierarchy)
- CC-23.4 — edit a memory/instruction file (operator write to a scope-validated CLAUDE.md/rule/MEMORY.md)
- CC-23.5 — remember/forget a learning (Claude-driven auto-memory + add-to-CLAUDE.md acts)

### CC-35 · Glossary & Best Practices
- CC-35.1 — look up a Claude Code term/best-practice from the docs mirror (a knowledge-corpus search, domain=claude-code-atlas)

> F6 honesty note (status split, CONTRACT-FORMAT §4.2): CC-23.2 / CC-35.1 are `building` —
> realized through real, proven-by-use MCP search faces (substrate-mcp + the company corpus
> tool). CC-23.3/.4/.5 and ALL of CC-20 are `planned` — the DATA MODELS are contracted (so a UI
> can render them) but NO company endpoint exposes them yet. The CC-20 gap is CODE-CITED: the
> supervisor consumes the `claude -p` result event but discards its cost/usage fields
> (runtime/session_supervisor.py _turn_done) — an F10.1 gap-adoption candidate with a clean
> path (stamp ModelUsage onto agent_sessions.turn). CC-23.1 (transcript memory) was seeded by
> F1 and is NOT re-owned here. Grounded in: memory.md, glossary.md, costs.md, monitoring-usage.md,
> analytics.md, admin-setup.md, agent-sdk/typescript.md, claude-directory.md, Config & UI Data
> Model.md, Memory Systems.md (vault claude-code-atlas) + usage-cost-api.md, admin-api.md (vault
> claude-platform-docs), all searched 2026-06-12; substrate get_status/list_vaults run live 2026-06-12.

## Affordances seeded by F3 (Execution & control)

### CC-07 · Permissions & Approval Modes
- CC-07.1 — read the permission posture a session runs under (mode + tool surface)
- CC-07.2 — spawn a session under a chosen permission mode (default/acceptEdits/plan/dontAsk/bypassPermissions/auto)
- CC-07.3 — constrain a session's tool surface with allow/deny/ask rules
- CC-07.4 — change a live session's permission mode mid-session

### CC-09 · Subagents & Agent Teams
- CC-09.5 — define/spawn a subagent (system prompt + tool allowlist + model) that reports back
- CC-09.6 — create a native agent TEAM (lead + teammates with a shared task list and a mailbox)
- CC-09.7 — assign tasks to teammates / require plan-approval before they change code
- CC-09.8 — message a specific teammate directly and shut a teammate down

### CC-10 · Model Selection & Reasoning
- CC-10.1 — list the available models/aliases a session can run
- CC-10.2 — select the model a session runs (alias or full name; incl. opusplan, [1m])
- CC-10.3 — set a session's reasoning effort level (low…max / ultracode)
- CC-10.4 — toggle extended thinking for a session
- CC-10.5 — set a fallback model chain for overload/unavailability

### CC-18 · Headless & Programmatic Use (SDK & Automation)
- CC-18.6 — read a programmatic session's machine-readable output stream (stream-json fold)
- CC-18.7 — choose a headless run's output format / structured-output schema / partial streaming
