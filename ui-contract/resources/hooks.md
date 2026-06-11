---
type: contract-entry
resource: hooks
summary: The lifecycle automation surface — user-defined command/HTTP/MCP-tool/prompt/agent handlers that fire at Claude Code lifecycle points (PreToolUse, SessionStart, Stop, …), gated by matchers and `if` rules, declared in settings JSON / plugin hooks.json / skill+agent frontmatter; the company exposes NO hook editor today, so this resource contracts the native surface a UI editor renders, with the bridge gap named.
schemes: []
status: building
relates-to: ["[[permission]]", "[[extensions]]", "[[mcp-servers]]", "[[output-style]]"]
---

# Resource: hooks

## Identity
**A hook is identified by the tuple (settings-source, hook-event, matcher-group-index, handler-index) — there is no `hook://` scheme and no addressable hook record; a hook is an entry inside a JSON settings file (or a plugin `hooks.json`, or skill/agent frontmatter), and the company exposes no endpoint that reads or writes it today.**
Claude Code hooks are user-defined shell commands, HTTP endpoints, MCP tool calls, LLM prompts, or subagents that execute automatically at lifecycle points, documented at https://code.claude.com/docs/en/hooks (reference) and https://code.claude.com/docs/en/hooks-guide (quickstart). This resource contracts the DATA MODEL a UI editor renders — the events catalog, the matcher grammar, the handler schema, the JSON input/output contract — NOT a new addressable object. Every op here is `planned`: the company's MCP face (`mcp_face/server.py`, Observed 2026-06-12) is a composition-substrate brain and exposes nothing about Claude Code hooks; the bridge `BRIDGE_ROUTES` (`runtime/bridge.py:45`) carries no hook route. The native write path is "edit the settings JSON" + the read path is the `/hooks` read-only menu.

## Representation
**A hook configuration is a tree: `hooks` → one key per lifecycle EVENT → an array of MATCHER GROUPS → each group's inner `hooks` array of HANDLERS; a handler is one of five types (command / http / mcp_tool / prompt / agent) carrying type-specific fields plus the common `if` / `timeout` / `statusMessage` / `once` fields.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/hooks.config",
  "type": "object",
  "properties": {
    "hooks": {
      "type": "object",
      "description": "keys are hook EVENT names (closed set, see hooks.event-catalog). Source: https://code.claude.com/docs/en/hooks#hook-events",
      "additionalProperties": {
        "type": "array",
        "description": "matcher groups for this event",
        "items": {
          "type": "object",
          "properties": {
            "matcher": { "type": "string",
              "description": "filter; evaluation depends on chars: `*`/``/omitted = match-all; only letters/digits/_/| = exact or |-list; any other char = JS regex. Each event matches a DIFFERENT field — tool events match tool_name, SessionStart matches start-reason, etc. (https://code.claude.com/docs/en/hooks#matcher-patterns)" },
            "hooks": { "type": "array", "items": { "$ref": "#/$defs/handler" } } },
          "required": ["hooks"] } } },
    "disableAllHooks": { "type": "boolean", "default": false,
      "description": "temporarily disable ALL hooks without removing them; respects the managed-settings hierarchy (only managed-level disableAllHooks disables managed hooks)" } },
  "$defs": {
    "handler": {
      "type": "object",
      "required": ["type"],
      "properties": {
        "type": { "enum": ["command", "http", "mcp_tool", "prompt", "agent"] },
        "if": { "type": "string", "description": "permission-rule syntax e.g. Bash(git *), Edit(*.ts); ONE rule only, no &&/||; evaluated ONLY on tool events; on other events a handler with `if` never runs (https://code.claude.com/docs/en/hooks#common-fields)" },
        "timeout": { "type": "integer", "description": "seconds before cancel. Defaults: 600 command/http/mcp_tool, 30 prompt, 60 agent; UserPromptSubmit lowers cmd default to 30, MessageDisplay to 10" },
        "statusMessage": { "type": "string", "description": "custom spinner message while the hook runs" },
        "once": { "type": "boolean", "description": "run once per session then remove; ONLY honored in SKILL frontmatter hooks, ignored in settings files + agent frontmatter" },
        "command": { "type": "string", "description": "command hooks: shell command, or (with args) the executable to spawn directly" },
        "args": { "type": "array", "items": { "type": "string" }, "description": "command hooks: when present, exec form — command resolved as executable + spawned with no shell" },
        "async": { "type": "boolean", "description": "command hooks: run in background without blocking" },
        "asyncRewake": { "type": "boolean", "description": "command hooks: background + wake Claude on exit 2; implies async" },
        "shell": { "enum": ["bash", "powershell"], "description": "command hooks: shell for this hook (ignored when args set)" },
        "url": { "type": "string", "description": "http hooks: POST target; JSON input sent as body, response body uses the same JSON output format" },
        "headers": { "type": "object", "description": "http hooks: extra headers; values interpolate $VAR only if listed in allowedEnvVars" },
        "allowedEnvVars": { "type": "array", "items": { "type": "string" }, "description": "http hooks: env vars permitted in header interpolation; unlisted refs become empty strings" },
        "server": { "type": "string", "description": "mcp_tool hooks: a CONNECTED MCP server name (never triggers OAuth/connection)" },
        "tool": { "type": "string", "description": "mcp_tool hooks: tool to call on that server" },
        "input": { "type": "object", "description": "mcp_tool hooks: args; string values support ${path} substitution from the hook JSON input e.g. ${tool_input.file_path}" },
        "prompt": { "type": "string", "description": "prompt/agent hooks: prompt text; $ARGUMENTS = the hook input JSON" },
        "model": { "type": "string", "description": "prompt/agent hooks: model for evaluation; defaults to a fast model" } } } } }
```
| field | type | volatile? | changed-by | address? -> resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| hooks.<event> | array | yes (planned: file edit / `/hooks` is READ-only) | NO company event — the file watcher in Claude Code picks up direct edits; there is no fabric event for a hook change | — | NOT exposed by the company. Native: edit `~/.claude/settings.json`, `.claude/settings.json[.local]`, plugin `hooks/hooks.json`, or skill/agent frontmatter |
| handler.type | enum | no | — | — | five values; the `/hooks` menu labels each `[type]` + a source (User/Project/Local/Plugin/Session/Built-in) |
| disableAllHooks | boolean | yes | — | — | a settings field; managed-hierarchy-aware. NOT a company lever |

## State model
**State model: stateless.** A hook configuration has no lifecycle of its own — it is declarative data in a settings file. The session it governs has the lifecycle ([[session#State model]]); hooks are configuration the session reads. The hook handler's RUNTIME (it fires, returns a decision, can block) is per-tool-call behavior, not a state machine over the hook record.

## Caller
**Reading hooks is the operator inspecting settings files or running `/hooks` inside an interactive session (read-only); WRITING hooks is the operator editing the JSON or frontmatter — there is no company API caller for either, and no consumer-over-HTTP identity, because the company exposes no hook face.**
When the bridge gap is closed (see Operations), a hook editor would be the operator's act against scope-validated settings files (the same scope hierarchy as [[output-style]] and CLAUDE.md). Enterprise managed policy can set `allowManagedHooksOnly` to block user/project/plugin hooks (managed-marketplace plugin hooks exempt) — a posture a UI must surface, never silently override.

## Operations

## op: hooks.get
**`hooks.get` is the PLANNED read of a session's effective hook configuration — every event with its matcher groups and handlers, each tagged with its SOURCE (User/Project/Local/Plugin/Session/Built-in) — the data behind Claude Code's read-only `/hooks` menu, which the company does not yet surface through any face.**
```contract:op
op: hooks.get
resource: hooks
kind: get
status: building
direction: outbound
atlas: [CC-12.1, CC-12.5]
tasks:
  - phrase: "show me what hooks are configured"
  - phrase: "which settings file did this hook come from"
  - alias: "list my hooks"
  - alias: "inspect the hooks menu"
bindings:
  - { kind: mcp, tool: config_hooks, op: "op='list'|'get'", server: company, exposure: "exposure.json#mcp.company", status: building, note: "BUILT (Capability Fabric ③): the MCP face reads settings hook blocks via the R3 config_writer. The handler runtime/capability_handlers/config_authoring.py:hooks backs both faces (DRY). live-verify pending (lead): a REAL .claude write / native claude-CLI round-trip." }
  - { kind: tui, command: "claude (interactive) then /hooks", transport: claude-tui, exposure: "n/a — interactive", status: planned, note: "NATIVE only: /hooks opens a read-only browser (event -> matcher -> handler detail + source). No company endpoint reads it. https://code.claude.com/docs/en/hooks#the-hooks-menu" }
liveness: snapshot
live-twin: "none — static between settings-file edits (the file watcher reloads on edit)"
emits: []
verification:
  read: {state: unverified, note: "no company face; native /hooks is interactive-TUI only, not a contracted endpoint"}
```
The `/hooks` menu is READ-ONLY by Claude Code's own design: "to add, modify, or remove hooks, edit the settings JSON directly or ask Claude to make the change" (https://code.claude.com/docs/en/hooks#the-hooks-menu). A company hook editor would need to (1) read the merged config across the scope hierarchy and (2) write the chosen scope's file — neither exists in `runtime/bridge.py` today.
```contract:example
captured: synthetic            # status=planned -> synthetic legal AND loud; no company hook face exists (V11)
binding: cli
request: |
  /hooks
response: |
  (read-only TUI) PreToolUse (2)
    └ Bash -> [command] User  ~/.claude/settings.json  block-rm.sh
    └ Edit|Write -> [command] Project  .claude/hooks/lint.sh
  PostToolUse (1)
    └ Write|Edit -> [mcp_tool] Plugin  my_server.security_scan
```
Adjacent: [[hooks#op: hooks.act]] (the planned writer), [[hooks#op: hooks.event-catalog]] (the closed event set), [[extensions#op: extensions.get]] (plugins that ship hooks), [[permission]] (PreToolUse hooks decide tool approval).

## op: hooks.act
**`hooks.act` is the PLANNED hook editor: add / update / remove a hook handler in a chosen settings scope, or flip `disableAllHooks` — the write the native model only does via direct file edit, named here so a UI editor builds toward the real seam (a scope-validated settings writer the company has not built).**
```contract:op
op: hooks.act
resource: hooks
kind: act
status: building
direction: outbound
atlas: [CC-12.2, CC-12.3, CC-12.4]
tasks:
  - phrase: "add a hook that runs a linter after every edit"
    params: {act: add-hook, event: PostToolUse, matcher: "Edit|Write"}
  - phrase: "block rm -rf with a pre-tool hook"
    params: {act: add-hook, event: PreToolUse, matcher: "Bash"}
  - phrase: "turn off all my hooks temporarily"
    params: {act: set-flag, disableAllHooks: true}
  - alias: "edit a hook"
  - alias: "remove a hook"
  - alias: "automate an action on a lifecycle event"
caller: required
bindings:
  - { kind: mcp, tool: config_hooks, op: "op='act' (add-hook/update-hook/remove-hook/set-flag)", server: company, exposure: "exposure.json#mcp.company", status: building, note: "BUILT (Capability Fabric ③): the MCP face routes the hook write to the R3 config_writer (consent-gated — a hook command is exec). The handler runtime/capability_handlers/config_authoring.py:hooks backs both faces (DRY). live-verify pending (lead): a REAL .claude write / native claude-CLI round-trip." }
  - { kind: http, method: POST, path: "/hooks  (Wire-phase-owned, pending — MCP face built)", transport: bridge-http, exposure: "exposure.json#bridge-http", status: planned, note: "GAP: BRIDGE_ROUTES (runtime/bridge.py:45) has zero hook routes. A hook editor must read the merged scope hierarchy AND write one scope's JSON file with validation. The bridge arm is Wire-phase-owned (pending); the MCP face is live now." }
liveness: none
emits: []
consequences:
  - when: "hook added/edited/removed in a settings file (planned)"
    expect: []
    evidence: "[[hooks#op: hooks.get]] (the /hooks menu) re-reads the file via Claude Code's file watcher and shows the new state — there is NO fabric event for a hook change; the proof is the re-read config + the hook firing on its next lifecycle event"
  - when: "disableAllHooks flipped (planned)"
    expect: []
    evidence: "behavioural: hooks stop firing on their events; observable only by the absence of hook effects, never a fabric event"
correlate: [session]
verification:
  add-hook:  {state: unverified, note: "no settings-writer endpoint — planned"}
  set-flag:  {state: unverified, note: "no settings-writer endpoint — planned"}
```
### Description (purpose-free)
Three planned writes the native model supports only by direct file edit. (1) Add a handler under an event's matcher group in a chosen scope (`~/.claude/settings.json` = all projects; `.claude/settings.json` = this project, committable; `.claude/settings.local.json` = this project, gitignored; managed policy = org-wide). (2) Update or remove an existing handler. (3) Flip `disableAllHooks`. The native model exposes NO programmatic writer — hooks are edited in JSON, then Claude Code's file watcher reloads them (https://code.claude.com/docs/en/hooks#disable-or-remove-hooks). A company editor would render the Representation tree, validate against the event catalog + matcher grammar + handler schema, and write the chosen scope's file. Until that bridge route exists, this op is `planned`.
### Request (PLANNED shape)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/hooks.act.request",
  "type": "object",
  "required": ["act", "scope"],
  "properties": {
    "act":   { "enum": ["add-hook", "update-hook", "remove-hook", "set-flag"] },
    "scope": { "enum": ["user", "project", "local", "managed"], "description": "which settings file to write (https://code.claude.com/docs/en/hooks#hook-locations)" },
    "event": { "type": "string", "description": "for add/update/remove: a member of the event catalog (https://code.claude.com/docs/en/hooks#hook-events)" },
    "matcher": { "type": "string", "description": "matcher-group filter (see Representation grammar)" },
    "handler": { "$ref": "ui-contract/hooks.config#/$defs/handler" },
    "disableAllHooks": { "type": "boolean", "description": "for act=set-flag" } },
  "additionalProperties": false }
```
### Interaction semantics
Native rules a hook editor MUST respect (sourced to the hooks reference):
- **Exit codes are the command-hook decision channel.** Exit 0 = success (stdout parsed for JSON output; only UserPromptSubmit/UserPromptExpansion/SessionStart inject stdout as context). Exit 2 = blocking error (stderr fed to Claude; effect is per-event — PreToolUse blocks the call, UserPromptSubmit erases the prompt). Any other exit code = NON-blocking error for most events (exit 1 does NOT block — use exit 2 to enforce policy). The one exception: WorktreeCreate aborts on any non-zero exit.
- **Not every event can block.** Post* events (PostToolUse, PostToolUseFailure) cannot block — the tool already ran; they only show stderr to Claude. The blockable set: PreToolUse, PermissionRequest, UserPromptSubmit, UserPromptExpansion, Stop, SubagentStop, TeammateIdle, TaskCreated, TaskCompleted, ConfigChange (except policy_settings), PostToolBatch, PreCompact, Elicitation, ElicitationResult, WorktreeCreate.
- **`if` is best-effort, not enforcement.** The `if` filter fails OPEN when a Bash command can't be parsed; use the [[permission]] system for hard allow/deny, not a hook.
- **MCP tool hooks need a connected server.** SessionStart/Setup usually fire before MCP servers connect, so those hooks should expect a "not connected" error on first run.
- **Hooks run without a controlling terminal** (macOS/Linux, v2.1.139+): return `systemMessage` (to the user) or `terminalSequence` (notification/bell) in JSON output; a hook cannot write to /dev/tty.
### Errors
```contract:error
code: hooks.unknown-event | http: 400 | retryable: false
when: event not in the closed catalog (typo, or an event this Claude Code version doesn't support)
teach: "Events are the closed set in [[hooks#op: hooks.event-catalog]] (source https://code.claude.com/docs/en/hooks#hook-events). Check spelling; some events require a recent Claude Code version."
```
```contract:error
code: hooks.not-exposed | http: 501 | retryable: false
when: any call against hooks.act today
teach: "Hook editing is PLANNED — the company has no settings-writer. Native path: edit the settings JSON (~/.claude/settings.json for all projects, .claude/settings.json[.local] per project) then Claude Code's file watcher reloads it; inspect via /hooks (https://code.claude.com/docs/en/hooks). The bridge gap is named in this op's bindings."
```
Adjacent: [[hooks#op: hooks.get]] (the read), [[hooks#op: hooks.event-catalog]] (legal events), [[mcp-servers]] (mcp_tool handlers reference a connected server), [[extensions]] (plugins bundle hooks via hooks.json).

## op: hooks.event-catalog
**`hooks.event-catalog` is the closed reference set of every lifecycle event a hook can target, each with its cadence, what its matcher filters, and whether exit-2 can block — the data a UI populates an event picker from; this is documentation-as-data, sourced verbatim to the hooks reference, not a company endpoint.**
```contract:op
op: hooks.event-catalog
resource: hooks
kind: get
status: planned
direction: outbound
atlas: [CC-12.1]
tasks:
  - phrase: "what lifecycle events can a hook fire on"
  - phrase: "which hook events can block an action"
  - alias: "list hook events"
bindings:
  - { kind: cli, command: "(reference only — the catalog is documentation at https://code.claude.com/docs/en/hooks#hook-events)", transport: claude-cli, exposure: "n/a — claude CLI", status: planned, note: "no enumerable company registry; the canonical list is the hooks reference page" }
liveness: snapshot
live-twin: "none — static reference (grows across Claude Code versions)"
emits: []
verification:
  catalog: {state: probe-verified, run: "doc-mirror read", date: 2026-06-12, note: "transcribed verbatim from claude-code-atlas hooks.md (fetched 2026-06-10), source https://code.claude.com/docs/en/hooks#hook-events — a documentation fact, not a company runtime fact"}
```
The catalog, grouped by cadence (https://code.claude.com/docs/en/hooks#hook-lifecycle):
- **Once per session:** `SessionStart` (matcher: startup/resume/clear/compact; only this event's hook gets a `model` field), `Setup` (--init-only / --init / --maintenance; matcher init/maintenance), `SessionEnd` (matcher clear/resume/logout/prompt_input_exit/bypass_permissions_disabled/other).
- **Once per turn:** `UserPromptSubmit` (no matcher; blockable), `UserPromptExpansion` (matcher: command name; blockable), `Stop` (no matcher; blockable — prevents Claude stopping), `StopFailure` (matcher: error type rate_limit/overloaded/…; output ignored).
- **Per tool call (agentic loop):** `PreToolUse` (matcher tool_name; blocks the call), `PostToolUse` (cannot block), `PostToolUseFailure` (cannot block), `PostToolBatch` (no matcher; blocks before next model call), `PermissionRequest` (blockable = deny), `PermissionDenied` (matcher tool_name; use JSON `retry:true` to let the model retry).
- **Subagents/tasks:** `SubagentStart` / `SubagentStop` (matcher agent type), `TaskCreated` / `TaskCompleted` (blockable), `TeammateIdle` (blockable — keeps a teammate working).
- **Async/standalone:** `Notification` (matcher notification type), `MessageDisplay` (display-only, 10s timeout), `InstructionsLoaded` (CLAUDE.md/rules loaded; matcher load-reason), `ConfigChange` (matcher config source; blockable except policy_settings), `CwdChanged` (no matcher), `FileChanged` (matcher = literal filenames to watch), `WorktreeCreate` (blockable, any non-zero exit aborts), `WorktreeRemove`, `PreCompact` / `PostCompact` (matcher manual/auto; PreCompact blockable), `Elicitation` / `ElicitationResult` (matcher MCP server name; blockable).
Adjacent: [[hooks#op: hooks.act]] (target an event), [[hooks#op: hooks.get]] (see configured events).

## Errors
**Resource-level error vocabulary: `hooks.unknown-event` (event not in the closed catalog) and `hooks.not-exposed` (the honest 501 every write returns until the settings-writer seam is built).** Both teach the native recovery: edit the settings JSON and inspect via `/hooks`. No error claims a hook-management capability the company does not have.

## Links
**No address-typed fields: a hook configuration references no fabric addresses.** `mcp_tool` handlers name a connected MCP server by string (resolves conceptually to [[mcp-servers]] but the server NAME is not a fabric scheme); matchers are tool-name patterns (Claude Code permission-rule / regex syntax), not corpus addresses; `command`/`url` are filesystem paths and URLs. None resolve to a corpus entry, by design.
