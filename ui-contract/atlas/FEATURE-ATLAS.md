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

## Affordances seeded by F7 (Reach — classes 14, 15, 16, 17, 19)

### CC-14 · Voice & Audio Input/Output
- CC-14.1 — speak a turn: record audio in, get the transcribed prompt + a reply ([[voice#op: voice.watch]])
- CC-14.2 — switch the speech circuit: pick the TTS engine / voice / persona ([[voice#op: voice.act]] act=switch)
- CC-14.3 — stream the spoken reply sentence-by-sentence (first audio while the brain still thinks; [[voice#op: voice.watch]])
- CC-14.4 — list the available ears (STT) + engines (TTS) + personas, with up/loadable state ([[voice#op: voice.list]])
- CC-14.5 — load/unload a GPU ear or TTS engine, VRAM-budgeted, and toggle voice on/off ([[voice#op: voice.act]])
- CC-14.6 — push-to-talk vs auto-listen (VAD + finished-thought) modes (native CC-14; feel is device-only/unflipped)

### CC-15 · Remote Control & Mobile Access
- CC-15.1 — reach the Company from another device (the REAL path: tailnet HTTPS PWA; [[remote#op: remote.get]])
- CC-15.2 — make a session controllable from the phone via native Remote Control (`--remote-control`; [[remote#op: remote.act]])
- CC-15.3 — serve the surface over HTTPS for the mobile browser mic (secure-context; [[remote#op: remote.get]])
- CC-15.4 — launch a session from a web/deep link (`claude://`; [[remote#op: remote.act]])

### CC-16 · Code Intelligence (LSP) & Symbol Navigation
- CC-16.1 — navigate symbols: go-to-definition / find-references / hover-type / workspace-symbol / implementations / call-hierarchy ([[code-intel#op: code-intel.act]])
- CC-16.2 — read automatic post-edit diagnostics (type errors/warnings) ([[code-intel#op: code-intel.act]] act=diagnostics)
- CC-16.3 — configure/activate a language server via a code-intelligence plugin (.lsp.json / lspServers) ([[code-intel#op: code-intel.act]])

### CC-17 · Computer Use & Web Access
- CC-17.1 — web access: WebFetch (lossy URL→extraction) + WebSearch ([[computer-use#op: computer-use.act]] act=web-fetch/web-search)
- CC-17.2 — browser automation: open tabs, click, type, read console (Claude-in-Chrome; beta, not WSL; [[computer-use#op: computer-use.act]] act=browser)
- CC-17.3 — computer use: screenshot + mouse/keyboard GUI control (API beta; [[computer-use#op: computer-use.act]] act=computer)

### CC-19 · AI-Driven Code Review & Analysis
- CC-19.1 — review a diff locally (`/code-review`, `/security-review`) ([[code-review#op: code-review.act]] act=review-local/security-review-local)
- CC-19.2 — managed PR review: a fleet posts severity-tagged inline comments (GitHub Code Review; [[code-review#op: code-review.act]] act=review-pr)
- CC-19.3 — self-hosted CI review via `claude -p` (GitHub Actions / GitLab) ([[code-review#op: code-review.act]] act=review-pr)

> F7 honesty (status split, CONTRACT-FORMAT §4.2): CC-14 is `building` and REAL — the Company runs a
> complete local voice stack (swappable STT-ear registry + 6 TTS engines + 5-persona cast) and a
> proven end-to-end voice circuit (`/api/voice/turn`, `/api/voice/stream`); the device-only FEEL
> (auto-listen VAD, on-device iOS playback, always-on activation) is unflipped/needs-tim, named never
> green-painted (CC-14.6). CC-15 is `building` for the REAL path — the bridge+canvas served over
> Tailscale HTTPS to Tim's iPhone PWA (verified on-device, `project-mobile-access-tailscale`);
> native Remote Control + Deep Links (CC-15.2/.4) are `planned` (Anthropic-hosted, un-bridged — the
> Company's mobile story is the tailnet, deliberately not the relay). CC-16/17/19 are ALL `planned`:
> they are native in-session / in-browser / hosted capabilities the Company exposes NO endpoint for —
> code intelligence runs inside a session's LSP tool, web/computer reach isn't even granted to a
> default fabric session (`--allowedTools mcp__company`), Chrome is NOT-WSL (the host), and code
> review's surfaces are TUI/Anthropic-hosted/CI (the CI `claude -p` path is buildable on the fabric
> but un-packaged). Each `planned` op names its bridge gap + the real wiring seam. Grounded in:
> Feature Atlas.md (classes 14/15/16/17/19), voice-dictation.md, remote-control.md, deep-links.md,
> glossary.md, tools-reference.md, discover-plugins.md, plugins-reference.md, large-codebases.md,
> costs.md, chrome.md, computer-use-tool.md, web-fetch-tool.md, code-review.md, github-actions.md,
> gitlab-ci-cd.md, Custom Apps Integration.md (vaults claude-code-atlas + claude-platform-docs,
> searched 2026-06-12) + the company ground truth: ops/services.json (voice + tailscale + pipeliner
> rows), runtime/bridge.py (voice routes :864-:1290), voice/lifecycle.py, voice/personas.py,
> project-voice-stack + project-mobile-access-tailscale (verified 2026-06-12).

## Affordances seeded by F5 (Automation — classes 6, 21, 22, 30)

### CC-06 · Git Integration & Worktrees
- CC-06.1 — automatic git context + commit/branch/PR/rebase/stash via the session's Bash tool ([[git#op: git.act]] — under [[permission]])
- CC-06.2 — resume a session linked to a PR (`--from-pr <number|url>`) ([[git#op: git.act]])
- CC-06.3 — create/enter an isolated git worktree for parallel work (`--worktree`/`-w`, the EnterWorktree tool, `git worktree`) ([[git#op: git.worktree]])
- CC-06.4 — isolate subagents in their own worktrees (`isolation: worktree`); base branch via `worktree.baseRef`; non-git VCS via WorktreeCreate/Remove hooks ([[git#op: git.worktree]])

### CC-21 · Scheduled Tasks, Routines & Automation
- CC-21.1 — list a consumer's cloud routines / a session's scheduled tasks ([[routines#op: routines.list]] — `/schedule list`, claude.ai/code/routines, CronList)
- CC-21.2 — create a recurring/one-off scheduled run (cloud routine schedule trigger, or session-scoped CronCreate/`/loop`) ([[routines#op: routines.create]])
- CC-21.3 — trigger a routine on demand via a bearer-token HTTP `/fire` endpoint, or on GitHub repo events (cloud routine API/GitHub triggers) ([[routines#op: routines.create]])
- CC-21.4 — run-now / pause / one-off / rotate-token / cancel an existing routine or task ([[routines#op: routines.act]] — claude.ai/code/routines controls, CronDelete, Esc)

### CC-22 · Dynamic Workflows & Task Coordination
- CC-22.1 — keep one session working toward a verifiable condition without per-step prompting (`/goal`, evaluator-gated) ([[workflows#op: workflows.act]])
- CC-22.2 — keep one session working on an interval / via a Stop hook (`/loop`, settings Stop hook) ([[workflows#op: workflows.act]]; `/loop` cron mechanics in [[routines]])
- CC-22.3 — push external events INTO a running session and react two-way (channels: Telegram/Discord/iMessage/fakechat plugins via `--channels`) ([[workflows#op: workflows.watch]])
- (the LIVE Company parallel-coordination primitive — fan one question to N forked consultants — is NOT a CC-22 affordance here; it is CC-09.2 realized at [[session#op: session.post]] verb=consult, `building`)

### CC-30 · CI/CD Integrations (GitHub Actions, GitLab, Automation)
- CC-30.1 — scaffold a GitHub Actions integration (anthropics/claude-code-action@v1 via `/install-github-app`; @claude-mention auto-detection vs prompt-mode; `schedule:`/event triggers) ([[ci#op: ci.create]])
- CC-30.2 — invoke an installed CI integration (a `@claude` comment, or a CI event matching the workflow trigger) ([[ci#op: ci.act]])
- CC-30.3 — scaffold a GitLab CI/CD integration (a `.gitlab-ci.yml` `claude -p` job with mcp__gitlab + a masked ANTHROPIC_API_KEY); cloud-provider auth (Claude API key / Bedrock-OIDC / Vertex-WIF) for both ([[ci#op: ci.create]])

> F5 honesty note (status split, CONTRACT-FORMAT §4.2): EVERY affordance above is `planned` —
> there is NO company face for git, worktrees, routines, in-session keep-going, channels, or
> CI/CD (verified 2026-06-12: no git/worktree/cron/schedule/routine/github-actions/gitlab noun
> in `ops/cli/`, `runtime/`, or `mcp_face/`; the only git/worktree references in `runtime/` are
> the Company's OWN recursive self-build self-commit, runtime/suite.py:8430-8644, which is the
> system building itself, NOT a consumer git service). These resources contract the NATIVE Claude
> Code surfaces (CLI flags, slash commands, the EnterWorktree tool, cloud routines, channel
> plugins, the GitHub Action / GitLab job) so a UI can present and reason about them, and route
> the genuinely LIVE adjacent capabilities to F1 where they exist: the consult-fan
> ([[session#op: session.post]] verb=consult, `building`) for parallel coordination, and the spawn
> `cwd`/`fork` params ([[session#op: session.create]]) for running a supervised session in a chosen
> working tree. Cloud routines (CC-21) are entirely Anthropic-cloud-resident (claude.ai account,
> per-routine bearer-token `/fire` under the experimental-cc-routine-2026-04-01 beta header, the
> Claude GitHub App) — an external surface, never a local file. Grounded in: routines.md,
> scheduled-tasks.md, desktop-scheduled-tasks.md, goal.md, channels.md, worktrees.md,
> how-claude-code-works.md, github-actions.md, gitlab-ci-cd.md (vault claude-code-atlas) +
> managed-agents/scheduled-deployments.md (vault claude-platform-docs), all fetched/searched
> 2026-06-12; company code grepped live 2026-06-12.

## Affordances seeded by F4 (Extension fabric — classes 3, 11, 12, 13, 26, 27)

### CC-03 · Slash Commands & Built-In Skills
- CC-03.1 — list available slash commands / skills (built-in, bundled, custom, plugin-namespaced)
- CC-03.2 — create a custom slash command / skill (SKILL.md or .claude/commands/*.md, with invocation control + arguments)
- CC-03.3 — invoke a skill with arguments ($ARGUMENTS / $N / $name substitution)

### CC-11 · MCP (Model Context Protocol) Integration
- CC-11.1 — list/inspect configured MCP servers + their connection status and tool count (claude mcp list/get, /mcp)
- CC-11.2 — add an MCP server (stdio/http/sse/ws) at a chosen scope (local/project/user)
- CC-11.3 — remove / import (from Claude Desktop) / reset-project-approval an MCP server
- CC-11.4 — authenticate a remote MCP server (OAuth 2.0 via /mcp; headers; headersHelper; scope pinning)
- CC-11.5 — read live MCP connection state (pending-approval / connected / failed / rejected; auto-reconnect)

### CC-12 · Hooks & Automation
- CC-12.1 — choose a lifecycle event to automate (the closed hook-event catalog + matcher grammar + blockability)
- CC-12.2 — add a hook handler (command/http/mcp_tool/prompt/agent) under an event's matcher group at a chosen scope
- CC-12.3 — update / remove a hook handler
- CC-12.4 — disable all hooks temporarily (disableAllHooks; managed-hierarchy-aware)
- CC-12.5 — inspect configured hooks + their source (the read-only /hooks menu)

### CC-13 · Plugins, Skills, & Extension Packaging
- CC-13.1 — list installed plugins + added marketplaces + their bundled components
- CC-13.2 — scaffold / author a plugin (.claude-plugin/plugin.json manifest + skills/agents/hooks/MCP/LSP/monitors/output-styles)
- CC-13.3 — add a plugin marketplace (github repo; official/community catalogs)
- CC-13.4 — install / uninstall / enable / disable a plugin; test with --plugin-dir/--plugin-url; /reload-plugins
- CC-13.5 — package existing standalone .claude/ configuration into a shareable, versioned plugin

### CC-26 · Terminal Configuration & Output Styling
- CC-26.1 — read the active output style + available styles (/config Output-style picker; outputStyle setting)
- CC-26.2 — set / create an output style (built-in Default/Proactive/Explanatory/Learning or a custom Markdown file)
- CC-26.3 — read the status-line config + its JSON data model (model/context/cost/git/rate-limit fields)
- CC-26.4 — set / generate / remove a status line (a shell script fed JSON session data; /statusline + statusLine setting)

### CC-27 · Extensibility & Customization Patterns
- CC-27.1 — route an intent to the right customization mechanism (the chooser: skill vs hook vs MCP vs output-style vs CLAUDE.md vs subagent vs plugin)
- CC-27.2 — apply the shared placeholders + scope/precedence laws (${CLAUDE_PROJECT_DIR}/${CLAUDE_PLUGIN_ROOT}/${CLAUDE_PLUGIN_DATA}; settings + skill + MCP precedence; workspace trust; managed force-enable)

> F4 honesty note (status split, CONTRACT-FORMAT §4.2): EVERY F4 affordance is `planned` against
> the Company. These are NATIVE Claude Code extension-fabric surfaces (hooks, MCP-server management,
> skills/commands/plugins, output styles + status line, the customization chooser) that the Company
> does NOT yet bridge — the entries contract the native data model a UI editor/installer renders and
> name the bridge gap per op. CODE-CITED gaps (Observed 2026-06-12): the Company MCP face
> `mcp_face/server.py` is a composition-substrate brain (FastMCP "company") and exposes NOTHING about
> Claude Code hooks/skills/plugins/MCP-server-management; `BRIDGE_ROUTES` (runtime/bridge.py:45)
> carries no hook/mcp-add/plugin-install/output-style/statusLine route. Two NEAR-MISSES that are
> deliberately NOT claimed: `/api/cognition/create_skill` (runtime/bridge.py:1962) creates a
> COMPOSITION skill in the substrate, NOT a Claude Code Agent Skill (SKILL.md); `/api/presentation-pref`
> is the Company UI's own altitude presentation preference, NOT Claude Code's outputStyle/statusLine.
> Native surfaces are carried on two NON-fabric transports declared in TRANSPORTS.md: `claude-cli`
> (the `claude` binary's mcp/plugin subcommands + launch flags) and `claude-tui` (the interactive
> /hooks /mcp /plugin /config /statusline menus); both fail V21 for want of a machine-readable Company
> inventory, so all F4 bindings are `planned` and carry `exposure: "n/a — …"`, never a registry key.
> Grounded in: hooks.md, mcp.md, skills.md, plugins.md, plugins-reference.md, output-styles.md,
> statusline.md, discover-plugins.md, plugin-marketplaces.md (vault claude-code-atlas, fetched
> 2026-06-10), all searched/read 2026-06-12; mcp_face/server.py + runtime/bridge.py read live 2026-06-12.

## Affordances seeded by F8 (Platform & admin)

### CC-01 · CLI & Session Entry Points
- CC-01.1 — the inventory of CLI entry points/flags that start or modify a session ([[surfaces#op: surfaces.list]] — the company drives exactly one: `claude -p`)

### CC-02 · Interactive Surfaces (Terminal, Desktop, Web, IDE)
- CC-02.1 — the inventory of interactive client kinds (terminal TUI, Desktop, Web, VS Code, JetBrains, Chrome) ([[surfaces#op: surfaces.list]] — all host-only; the fabric drives none)

### CC-04 · Keyboard Shortcuts & Keybindings
- CC-04.1 — the keybindings.json data model: contexts × namespaced actions, keystroke syntax, unbind/reserved rules ([[surfaces#op: surfaces.get-keybindings]] — host-only TUI config)

### CC-24 · Authentication & Account Management
- CC-24.1 — read which credential method/account a session is authenticated under ([[auth#op: auth.get]])
- CC-24.2 — switch the active account / re-authenticate (/login, /logout) ([[auth#op: auth.act]])
- CC-24.3 — supply or change a key/token credential (env / apiKeyHelper) ([[auth#op: auth.act]])
- CC-24.4 — mint a long-lived CI token (`claude setup-token` -> CLAUDE_CODE_OAUTH_TOKEN) ([[auth#op: auth.act]])

### CC-25 · Configuration & Settings System
- CC-25.2 — thread a chosen settings file / inline JSON into a session at spawn (`--settings`) ([[settings#op: settings.act]])
- CC-25.3 — grant a session additional directories / set per-session env (`--add-dir`, env) ([[settings#op: settings.act]])
> (CC-25.1 — read the fabric's live operating configuration — was seeded by F1; F8 re-owns the read as [[settings#op: settings.get]], the settings/config lens on the same GET /health.)

### CC-28 · Enterprise & Admin Features
- CC-28.1 — central org configuration: managed policy (server/MDM/file), admin console, managed MCP, org analytics ([[platform#op: platform.enterprise]] — org-only; the fabric is a policy subject)

### CC-29 · Cloud Provider Integrations (Bedrock, Vertex, Foundry)
- CC-29.1 — route inference through a cloud provider (CLAUDE_CODE_USE_BEDROCK/_VERTEX/_FOUNDRY) ([[platform#op: platform.cloud-provider]] — host env, inherited by the fabric)

### CC-31 · Large Codebase Support & Dev Containers
- CC-31.1 — set up Claude Code for a monorepo/large codebase (nested CLAUDE.md, sparse worktrees, per-package skills, dev containers) ([[platform#op: platform.privacy]] description — host/project setup; LSP/code-intel is CC-16, a separate lane)

### CC-32 · Data Privacy, Security & Compliance
- CC-32.1 — the data posture: what is logged/retained, telemetry opt-in, provider-default behaviors, credential storage, and the company's OWN local-persistence boundary ([[platform#op: platform.privacy]])

### CC-33 · Diagnostics, Debugging & Troubleshooting
- CC-33.1 — read fabric health (supervisor up?, session counts, operating slice) ([[diagnostics#op: diagnostics.get]])
- CC-33.2 — observe per-session failures (spawn-fail, turn-error, turn-timeout) + resolved tool surface ([[diagnostics#op: diagnostics.watch]])
- CC-33.3 — run a per-session health check (/doctor) ([[diagnostics#op: diagnostics.act]])
- CC-33.4 — thread debug categories / safe-mode for troubleshooting (`--debug`, `--safe-mode`, `--bare`) ([[diagnostics#op: diagnostics.act]])

### CC-34 · Installation, Updates & Platform Support
- CC-34.1 — install/update the Claude Code binary; platform support; updater health ([[platform#op: platform.install]] — host-only; the fabric drives an already-installed binary)

### CC-35 · Glossary & Best Practices
> (CC-35.1 — look up a Claude Code term/best-practice from the docs mirror — was seeded by F6; F8 re-owns it as the platform/glossary lens [[platform#op: platform.glossary]] over the SAME knowledge-corpus search.)

> F8 honesty note (status split, CONTRACT-FORMAT §4.2): the F8 classes split sharply by whether a
> capability is a FABRIC concern or a HOST/ORG concern.
> - `building` (a real, proven-by-use company READ exists): CC-25.1 ([[settings#op: settings.get]]),
>   CC-33.1 ([[diagnostics#op: diagnostics.get]]), CC-33.2 ([[diagnostics#op: diagnostics.watch]]) —
>   all three are the settings/diagnostics LENSES on the F1/F3 `GET /health` + supervisor watch
>   stream, proven by `session_supervisor_acceptance`; and CC-35.1 ([[platform#op: platform.glossary]])
>   — the F6 knowledge-corpus search, proven by use 2026-06-12.
> - `planned` (a company endpoint is namable but unbuilt; the spawn-param/control gap is CODE-CITED):
>   CC-24.1 (auth status read), CC-25.2/.3 (settings/add-dir/env at spawn — `runtime/session_supervisor.py:259-265`
>   threads a FIXED flag set), CC-33.3/.4 (per-session /doctor + --debug — spawn threads `--verbose`
>   only, no `--debug`/`--safe-mode`). These are F10.1 gap-adoption candidates.
> - OUT-OF-LOCAL-SCOPE (a HOST or ORG concern by design, not omission — routed to OUT-OF-SCOPE.md /
>   INVENTORY-EXCLUSIONS.md with reasons): CC-01.1/CC-02.1/CC-04.1 (surfaces — the company drives one
>   headless entry; interactive clients + keybindings are human-only), CC-24.2/.3/.4 (credential change
>   = host act + usage-policy boundary), CC-28.1 (managed policy = org admin; fabric inherits it
>   unoverridably), CC-29.1 (provider selection = host env; inherited transparently), CC-31.1 (host/
>   project setup), CC-32.1 (org data agreement + host telemetry; the company's local-persistence
>   boundary is STATED), CC-34.1 (install/update = host operator). Each is named, never silent (N5/C8).
> Grounded in: settings.md, authentication.md, cli-reference.md, keybindings.md, troubleshooting.md,
> setup.md, quickstart.md, admin-setup.md, server-managed-settings.md, managed-mcp.md, data-usage.md,
> large-codebases.md, legal-and-compliance.md, monitoring-usage.md, glossary.md, platforms.md (vault
> claude-code-atlas), all searched/read 2026-06-12; supervisor spawn + GET /health verified against
> runtime/session_supervisor.py:254-265,478,697-705 (2026-06-12).
