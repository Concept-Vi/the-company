<!-- generated: INITIAL SKELETON, hand-derived 1:1 from the per-op `tasks:` declarations in
     resources/*.md by the F1 contract lane (2026-06-12). The generator (tools/) is NOT YET
     BUILT — when it lands it overwrites this file in place and hand-edits fail its diff.
     Until then: if a row here disagrees with an op's tasks: block, the OP'S FENCE WINS. -->

# TASKS — intent → (op, params)

Cross-resource tasks: see `journeys/` (currently: [[message-and-read-reply]]).
Statuses ride the ops (CONTRACT-FORMAT §4.2); rows whose op is `planned` say so.

## Find & inspect sessions
| intent / alias | op | params |
|---|---|---|
| list every Claude Code session on this machine | [[session#op: session.list]] | |
| find a session by title or directory | [[session#op: session.list]] | q= / cwd= |
| which sessions are alive right now | [[session#op: session.list]] | state=supervised-live |
| show the fleet · session catalog *(aliases)* | [[session#op: session.list]] | |
| inspect one session in full | [[session#op: session.get]] | |
| is this session alive, and what has it been mailed | [[session#op: session.get]] | |
| describe a session *(alias)* | [[session#op: session.get]] | |

## Spawn & control sessions
| intent / alias | op | params |
|---|---|---|
| spawn a supervised Claude Code session | [[session#op: session.create]] | |
| resume an old session under supervision | [[session#op: session.create]] | resume=<id> |
| fork a session into a sandbox copy | [[session#op: session.create]] | resume=<id>, fork=true |
| launch a session *(alias)* | [[session#op: session.create]] | |
| push a turn directly into a supervised session | [[session#op: session.inject]] | |
| type into a running session *(alias)* | [[session#op: session.inject]] | |
| stop a session's in-flight turn without killing it | [[session#op: session.interrupt]] | |
| cancel a running turn *(alias)* | [[session#op: session.interrupt]] | |
| tear down a supervised session · free a fabric slot | [[session#op: session.stop]] | |
| kill a session *(alias)* | [[session#op: session.stop]] | |

## Message sessions (the routed verbs — parameter-level rows, never buried)
| intent / alias | op | params |
|---|---|---|
| send a message to another session | [[session#op: session.post]] | verb=auto (default) |
| resume a closed session and ask it something | [[session#op: session.post]] | verb=wake |
| ask N forked copies of a session in parallel | [[session#op: session.post]] | verb=consult, copies=N |
| leave a message a running unsupervised session picks up next turn | [[session#op: session.post]] | verb=auto → queue |
| notify a session · fan out a question · consult a session without disturbing it *(aliases)* | [[session#op: session.post]] | |
| read a session's inbox · check my mail *(alias)* | [[session-message#op: session-message.list]] | |
| collect the replies to a question I fanned out · did anyone answer *(alias)* | [[session-message#op: session-message.list]] | thread=<from post> |
| check for queued messages at my turn start | [[session-message#op: session-message.list]] | verb=queue |

## Observe the fabric
| intent / alias | op | params |
|---|---|---|
| what happened in the fabric since my cursor · poll fabric events *(alias)* | [[events#op: events.list]] | since= |
| did my message cause a turn | [[events#op: events.list]] | since=, session= (join intent_id) |
| stream fabric events live · subscribe to the event stream *(alias)* | [[events#op: events.watch]] | |
| watch what a session is doing right now · tail a session *(alias)* | [[session#op: session.watch]] | |

## Memory & configuration
| intent / alias | op | params |
|---|---|---|
| refresh the session-transcript corpus now · turn the exporter on | [[transcript#op: transcript.export]] | |
| export my sessions to markdown *(alias)* | [[transcript#op: transcript.export]] | |
| what did a past session decide about X · search my session history *(alias)* | [[transcript#op: transcript.search]] | **PLANNED** — until live: session.list q= (titles) + direct file reads over ~/corpora/claude-sessions/ |
| find the session that edited a given file · recall a past conversation *(alias)* | [[transcript#op: transcript.search]] | **PLANNED** (same interim paths) |
| what is the fabric's concurrency cap · check the cap before fanning out *(alias)* | [[fabric-config#op: fabric-config.get]] | |
| is the session supervisor up · fabric health *(alias)* | [[fabric-config#op: fabric-config.get]] | |

## Context management & checkpoints (F2 — in-process Claude Code features, NOT yet fabric)
> Every row here is **PLANNED**: these are interactive-TUI / Agent-SDK capabilities the Company
> supervisor does not yet bridge (it spawns headless `claude -p`). The op entries carry the
> grounded behavior + the named gap. A fabric-only consumer reaching for these has found a
> recorded boundary, not a dead end.

| intent / alias | op | params |
|---|---|---|
| how full is the context window · what is eating my tokens *(alias)* | [[context-window#op: context-window.get]] | **PLANNED** — in-process /context + statusline feed; no fabric endpoint |
| compact the conversation to free context · run compaction now *(alias)* | [[context-window#op: context-window.compact]] | focus=<instruction> · **PLANNED** — /compact (TUI) or SDK prompt; auto-compaction is on by default |
| clear context and start fresh between tasks · wipe the context *(alias)* | [[context-window#op: context-window.clear]] | **PLANNED** — /clear (parks the old session, resumable); /btw for an aside that never enters history |
| ask a quick aside without growing context | [[context-window#op: context-window.clear]] | mode=btw · **PLANNED** |
| show the points I can rewind this session to · show the rewind menu *(alias)* | [[checkpoint#op: checkpoint.list]] | **PLANNED** — /rewind menu (TUI) / accumulate SDK UserMessage.uuid |
| rewind this session to an earlier prompt · go back to before that broke *(alias)* | [[checkpoint#op: checkpoint.restore]] | scope=code\|conversation\|both · **PLANNED** — /rewind restore actions / SDK rewind_files (files-only) |
| undo Claude's file edits back to a point · undo the last changes *(alias)* | [[checkpoint#op: checkpoint.restore]] | scope=code · **PLANNED** |
| compress one side of a chosen point · targeted compact at a checkpoint *(alias)* | [[checkpoint#op: checkpoint.summarize]] | direction=from-here\|up-to-here · **PLANNED** — /rewind "Summarize from/up to here" |

## Permissions (F3 — CC-07)
| intent / alias | op | params |
|---|---|---|
| what permission mode will a spawned session run under · is the fabric read-only *(alias)* | [[permission#op: permission.get]] | |
| can fabric sessions edit files or only plan | [[permission#op: permission.get]] | |
| spawn a session that can edit files without prompting | [[permission#op: permission.act]] | mode=acceptEdits **PLANNED** |
| lock a session to a fixed tool surface | [[permission#op: permission.act]] | mode=dontAsk, allow=[…] **PLANNED** |
| change permission mode mid-session · raise a session's permissions *(alias)* | [[permission#op: permission.act]] | act=set-mode **PLANNED** |

## Models & reasoning (F3 — CC-10)
| intent / alias | op | params |
|---|---|---|
| what models can a session run · available models *(alias)* | [[model#op: model.list]] | **PLANNED** (interim: the alias table in [[model#Representation]]) |
| spawn a session on a specific model · switch model *(alias)* | [[model#op: model.act]] | model=opus|sonnet|haiku|fable|opusplan **PLANNED** |
| run a cheaper faster model for a simple task | [[model#op: model.act]] | model=haiku **PLANNED** |
| make a session reason harder · select reasoning effort *(alias)* | [[model#op: model.act]] | effort=xhigh **PLANNED** |
| use opus for planning then sonnet for execution | [[model#op: model.act]] | model=opusplan **PLANNED** |
| set a fallback model if the primary is overloaded | [[model#op: model.act]] | fallback=[sonnet,haiku] **PLANNED** |
| use the 1 million token context *(alias)* | [[model#op: model.act]] | model=opus[1m] **PLANNED** |

## Subagents & teams (F3 — CC-09; the LIVE path is the fabric fan)
| intent / alias | op | params |
|---|---|---|
| fan out parallel workers · ask N copies of a session in parallel *(the LIVE path)* | [[session#op: session.post]] | verb=consult, copies=N |
| collect a fan's replies | [[session-message#op: session-message.list]] | thread=<from post> |
| list live parallel workers · show running teammates *(alias)* | [[session#op: session.list]] | state=supervised-live |
| create an agent team to work in parallel · run a parallel code review | [[agent-team#op: agent-team.act]] | act=create-team **PLANNED** (native teams) |
| spawn a teammate from a subagent definition · delegate to a subagent *(alias)* | [[agent-team#op: agent-team.act]] | act=spawn-teammate, agent_type=… **PLANNED** |
| require a teammate to plan before changing code | [[agent-team#op: agent-team.act]] | plan_approval=true **PLANNED** |
| message a teammate · shut down a teammate *(alias)* | [[agent-team#op: agent-team.act]] | act=message-teammate / shutdown-teammate **PLANNED** |
| list agent teams · available agent types *(alias)* | [[agent-team#op: agent-team.list]] | **PLANNED** (interim: [[session#op: session.list]]) |

## Headless / SDK control (F3 — CC-18)
| intent / alias | op | params |
|---|---|---|
| read a headless session's output stream as JSON · tail a headless session *(alias)* | [[headless-control#op: headless-control.watch]] | (= [[session#op: session.watch]], headless lens) |
| what model and tools did a session resolve at init | [[headless-control#op: headless-control.watch]] | (system/init fields — fold gap noted) |
| push a turn into a programmatic session · send stream-json input *(alias)* | [[headless-control#op: headless-control.act]] | act=turn (= [[session#op: session.inject]]) |
| interrupt a headless session's current turn | [[headless-control#op: headless-control.act]] | act=interrupt (= [[session#op: session.interrupt]]) |
| ask a headless session for structured JSON output | [[headless-control#op: headless-control.act]] | act=set-output, output_format=json **PLANNED** |

## Not exposed locally (honest rows — reach for these and you found a recorded boundary)
| intent | status |
|---|---|
| get one mail message by id | NOT EXPOSED — read the thread/inbox ([[session-message#op: session-message.list]] thread=/since=); a by-id get lands with the planned msg:// scheme (§9.7) |
| rename/retitle a session record | NOT EXPOSED — titles are importer-derived (fallback chain); no update op exists yet |
| change the fabric's cap/timeout/permission via an API | NOT EXPOSED BY DESIGN — operator env + service restart; raising the cap is a recorded decision ([[fabric-config#Caller]]) |
| reach the supervisor from off this machine | NOT EXPOSED BY DESIGN — 127.0.0.1 only, no env to widen (exposure law B3) |
| read/compact/clear a session's context window through an API | NOT EXPOSED — in-process only (/context, /compact, /clear). The supervisor could inject /compact as a turn but no contracted op means it; observation rides the SDK compact_boundary marker / OTEL claude_code.compaction event ([[context-window#Caller]]) |
| rewind code or conversation to a checkpoint through an API | NOT EXPOSED — checkpoints are session-local, operated via the /rewind TUI menu or the Agent SDK rewind_files (which restores FILES ONLY). The supervisor never enables file-checkpointing on its headless sessions ([[checkpoint#Caller]]). For "preserve original, try another way" the fabric path is fork: [[session#op: session.create]] fork=true |

## Knowledge: search the corpora (F6 — building, proven by use)
| intent / alias | op | params |
|---|---|---|
| how does Claude Code do X · look it up in the docs *(alias)* | [[knowledge-corpus#op: knowledge-corpus.search]] | vault=claude-code-atlas |
| what does the Anthropic API doc say about Y | [[knowledge-corpus#op: knowledge-corpus.search]] | vault=claude-platform-docs |
| ask the company codebase a question · ask the codebase *(alias)* | [[knowledge-corpus#op: knowledge-corpus.search]] | backend=company, space=repo |
| look up a Claude Code term or best practice | [[knowledge-corpus#op: knowledge-corpus.search]] | vault=claude-code-atlas |
| what knowledge corpora can I search · list the vaults *(alias)* | [[knowledge-corpus#op: knowledge-corpus.list]] | |
| which memory holds this (knowledge vs history vs instructions) | [[which-corpus]] (journey) | route first |

## Memory: CLAUDE.md & auto-memory (F6 — planned, data model contracted)
| intent / alias | op | params |
|---|---|---|
| what CLAUDE.md and memory files are loaded · what is Claude remembering *(alias)* | [[claude-memory#op: claude-memory.list]] | **PLANNED** — interim: built-in `/memory` + read the scope paths |
| add a convention to CLAUDE.md · edit a memory file *(alias)* | [[claude-memory#op: claude-memory.update]] | **PLANNED** — interim: edit the scope-path file directly |
| remember that X · save this preference *(alias)* | [[claude-memory#op: claude-memory.act]] | act=remember **PLANNED** |
| forget the stale note · stop remembering this *(alias)* | [[claude-memory#op: claude-memory.act]] | act=forget **PLANNED** |

## Cost & usage telemetry (F6 — planned, data model contracted, gap code-cited)
| intent / alias | op | params |
|---|---|---|
| what has this session cost · spend so far *(alias)* | [[cost-usage#op: cost-usage.get]] | **PLANNED** — interim: built-in `/usage` / `/cost` (local estimate) |
| show usage by model/skill/plugin · usage breakdown *(alias)* | [[cost-usage#op: cost-usage.get]] | **PLANNED** — OTel metrics / `/usage` attribution / org Usage & Cost API |
| cap this headless run's spend · set a spend limit *(alias)* | [[cost-usage#op: cost-usage.act]] | act=cap-budget, max_budget_usd=N **PLANNED** |

## Not exposed locally (F6 honest rows)
| intent | status |
|---|---|
| get authoritative org billing from the company | NOT A COMPANY FACE — EXTERNAL Anthropic Usage & Cost API (Admin key); local /usage is an ESTIMATE this-machine-only ([[cost-usage#Errors]]) |
| programmatically list loaded memory via a company API | NOT EXPOSED YET — Claude Code's `/memory` is interactive, not machine-readable; company list op is an F10.1 gap-adoption candidate ([[claude-memory#op: claude-memory.list]]) |
| read per-turn cost from the fabric event stream | NOT EXPOSED YET — the supervisor DISCARDS the result event's cost/usage fields (code-cited gap, [[cost-usage#Representation]]); adoption = stamp ModelUsage onto agent_sessions.turn |
| semantically search past-session transcripts | PLANNED (F1's [[transcript#op: transcript.search]]) — the claude-sessions vault is not yet registered; this is a DIFFERENT corpus from the knowledge vaults ([[which-corpus]]) |
| set a per-session permission mode / allow-deny rules | NOT EXPOSED YET (planned) — the fabric pins COMPANY_FABRIC_PERMISSION (default plan) + --allowedTools mcp__company on every spawn; per-session is [[permission#op: permission.act]] (spawn-param gap named). Operator path: COMPANY_FABRIC_PERMISSION=<mode> + restart |
| select a session's model / effort / thinking | NOT EXPOSED YET (planned) — the spawn passes no --model/--effort ([[model#op: model.act]]). Operator path: ANTHROPIC_MODEL on the service + restart; OBSERVE the resolved model via [[headless-control#op: headless-control.watch]] system/init |
| create or control a NATIVE Claude Code agent team | NOT EXPOSED BY DESIGN (no API) — native teams are driven inside a lead session, gated by CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1. The LIVE parallel path is the fabric fan ([[session#op: session.post]] verb=consult) |
| run a native single-session subagent (Task/Agent tool) from a fabric session | NOT EXPOSED — fabric sessions run --allowedTools mcp__company, so the native Agent tool is outside their allow surface ([[permission]]); use the consult fan instead |
| choose a headless run's output-format / structured-output schema / token streaming | NOT EXPOSED YET (planned) — the supervisor hardcodes --output-format stream-json --verbose and requests no --include-partial-messages/--json-schema ([[headless-control#op: headless-control.act]]). Operator path: run claude -p --output-format json --json-schema directly, outside the fabric |
| read api-retry progress / token-level deltas of a fabric session | NOT EXPOSED — the supervisor's reader ignores system/api_retry and the spawn omits --include-partial-messages; the folded `text` frame is per-block, not per-token ([[headless-control#Representation]]) |
