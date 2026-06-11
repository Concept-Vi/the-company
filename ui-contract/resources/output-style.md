---
type: contract-entry
resource: output-style
summary: "The terminal presentation surface — the output STYLE (a system-prompt modifier setting Claude's role/tone/format: built-in Default/Proactive/Explanatory/Learning or a custom Markdown file) and the STATUS LINE (a shell script fed JSON session data that renders a persistent bottom bar); the company exposes neither, so this resource contracts the native surface a UI editor renders, with the bridge gap named."
schemes: []
status: planned
relates-to: ["[[extensions]]", "[[context-window]]", "[[cost-usage]]", "[[model]]"]
---

# Resource: output-style

## Identity
**The output style is identified by the `outputStyle` settings field (a name: a built-in or a custom file's name); the status line is identified by the `statusLine` settings object — both are session-presentation attributes read from settings files, not addressable records, and the company exposes no endpoint to read or set either.**
Claude Code output styles (https://code.claude.com/docs/en/output-styles) change HOW Claude responds (system-prompt role/tone/format), not what it knows; status lines (https://code.claude.com/docs/en/statusline) render a customizable bottom bar from a shell script fed JSON session data. This resource contracts the DATA MODEL a UI editor renders — the style enum + custom-style frontmatter, the statusLine config + the full JSON field set the script receives. Every op is `planned` against the company: no bridge route (`runtime/bridge.py:45`, Observed 2026-06-12) reads or writes `outputStyle` or `statusLine`. Native paths are `/config` (output style picker), the `outputStyle` settings field, the `/statusline` command, and the `statusLine` settings object. NOTE: the company's bridge HAS an `/api/presentation-pref` route, but that is the COMPANY UI's own up-translate presentation preference (altitude layer), NOT Claude Code's outputStyle/statusLine — unrelated.

## Representation
**An output style is a NAME (built-in: Default / Proactive / Explanatory / Learning; or a custom style from a Markdown file with frontmatter name/description/keep-coding-instructions/force-for-plugin). A status line is a `statusLine` object: type=command, a command (script path or inline shell), and optional padding / refreshInterval / hideVimModeIndicator.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/output-style.config",
  "type": "object",
  "properties": {
    "outputStyle": { "type": "string",
      "description": "the active style name. Built-ins: Default (the SWE system prompt), Proactive (execute-immediately, action over planning — stronger than auto mode, no permission-mode change), Explanatory (educational Insights while coding), Learning (collaborative; adds TODO(human) markers). Or a custom style's name. Saved by /config to .claude/settings.local.json. Read once at session start — takes effect after /clear or a new session. Source https://code.claude.com/docs/en/output-styles" },
    "statusLine": { "type": "object",
      "properties": {
        "type": { "const": "command", "description": "runs a shell command/script" },
        "command": { "type": "string", "description": "script path (e.g. ~/.claude/statusline.sh) or inline shell; receives JSON session data on stdin, prints the bar to stdout" },
        "padding": { "type": "integer", "default": 0, "description": "extra horizontal spacing (chars); relative indentation" },
        "refreshInterval": { "type": "integer", "description": "re-run every N seconds (min 1) IN ADDITION to event-driven updates; for clocks or idle-period freshness" },
        "hideVimModeIndicator": { "type": "boolean", "description": "suppress built-in -- INSERT -- when your script renders vim.mode itself" } },
      "required": ["type", "command"] } } }
```
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/output-style.custom-file",
  "type": "object",
  "description": "Custom output-style Markdown file frontmatter. Body = instructions appended to the system prompt. Source https://code.claude.com/docs/en/output-styles#frontmatter",
  "properties": {
    "name": { "type": "string", "description": "style name if not the file name" },
    "description": { "type": "string", "description": "shown in the /config picker" },
    "keep-coding-instructions": { "type": "boolean", "default": false, "description": "true = keep Claude Code's built-in SWE instructions (changing voice but still coding); false = drop them (non-SWE assistant)" },
    "force-for-plugin": { "type": "boolean", "default": false, "description": "plugin styles only: apply automatically whenever the plugin is enabled, overriding the user's outputStyle (first-loaded wins on conflict)" } } }
```
| field | type | volatile? | changed-by | address? -> resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| outputStyle | string | yes (planned: /config or settings edit; takes effect after /clear or new session) | NO company event — read once at session start (system prompt) | — | NOT a company lever. Native: /config -> Output style (saves to .claude/settings.local.json), or edit `outputStyle`. The standalone /output-style command was removed v2.1.91 |
| custom style files | markdown | yes | file edit | — | live at ~/.claude/output-styles (user), .claude/output-styles (project), or managed-settings dir; plugins ship them in output-styles/ |
| statusLine.command | string | yes | settings edit / /statusline | — | NOT a company lever. Native: /statusline (NL -> Claude generates a script in ~/.claude/ + updates settings) or manual statusLine config |
| status line OUTPUT | text | yes (every assistant message / /compact / mode change / vim toggle; 300ms debounce) | the script run | — | runs LOCALLY, no API tokens; output is colors (ANSI)/multi-line/OSC-8 links; sized via $COLUMNS/$LINES env (v2.1.153+). NOT surfaced by a company face |

## State model
**State model: stateless.** Both are session-presentation attributes read from settings — no lifecycle of their own. The output style is fixed at session start (changes need /clear or a new session — prompt-cache reason); the status line script re-runs on events (new assistant message, /compact finish, permission-mode change, vim toggle; debounced 300ms; in-flight run cancelled if a new update triggers; refreshInterval adds a timer). The company contracts neither read nor write today.

## Caller
**Setting the output style or status line is the operator via `/config` / `/statusline` in an interactive session or by editing settings files; there is no company API caller and no HTTP consumer identity, because the company exposes no presentation face.** The status line SCRIPT runs as the operator's local process with Claude Code's environment ($CLAUDE_CODE_REMOTE="true" in remote web envs); it cannot read the terminal directly (Claude Code captures stdout) — it reads $COLUMNS/$LINES instead. A UI editor would write the chosen scope's settings file (user/project/local), same scope discipline as [[extensions]] and CLAUDE.md.

## Operations

## op: output-style.get
**`output-style.get` is the PLANNED read of a session's presentation config — the active output-style name (+ available styles) and the statusLine object — the data behind the `/config` Output-style picker and the `statusLine` setting, which the company does not surface through any face.**
```contract:op
op: output-style.get
resource: output-style
kind: get
status: planned
direction: outbound
atlas: [CC-26.1, CC-26.3]
tasks:
  - phrase: "what output style is active"
  - phrase: "show my status line config"
  - alias: "list output styles"
  - alias: "is the learning style on"
bindings:
  - { kind: tui, command: "claude (interactive) /config -> Output style (picker) · read the statusLine field in settings.json", transport: claude-tui, exposure: "n/a — interactive", status: planned, note: "NATIVE: /config shows + picks the style; statusLine is a settings field. The status line's CURRENT data is also visible on the bar itself. No company endpoint. https://code.claude.com/docs/en/output-styles#change-your-output-style" }
liveness: snapshot
live-twin: "the status-line OUTPUT is event-driven-live on the bar; the CONFIG is static between edits"
emits: []
verification:
  read: {state: unverified, note: "no company face; native /config + the statusLine setting are TUI/file — not contracted endpoints"}
```
The status line's JSON input (the field set a script reads, also useful as a presentation data model — https://code.claude.com/docs/en/statusline#available-data) includes: `model.id`/`model.display_name`, `cwd`/`workspace.current_dir`/`workspace.project_dir`/`workspace.added_dirs`/`workspace.git_worktree`/`workspace.repo.*`, `cost.total_cost_usd`/`cost.total_duration_ms`/`cost.total_lines_added`/`removed`, `context_window.total_input_tokens`/`output_tokens`/`context_window_size`/`used_percentage`/`remaining_percentage`/`current_usage`, `exceeds_200k_tokens`, `effort.level`, `thinking.enabled`, `rate_limits.five_hour`/`seven_day.used_percentage`/`resets_at`, `session_id`/`session_name`/`transcript_path`/`version`, `output_style.name`, `vim.mode`, `agent.name`, `pr.number`/`pr.url`/`pr.review_state`, `worktree.*`. (This overlaps [[context-window]] and [[cost-usage]] — the status line is one CONSUMER of those same readings.)
Adjacent: [[output-style#op: output-style.act]] (set), [[context-window]] (the context fields the bar shows), [[cost-usage]] (the cost fields), [[model]] (the model field).

## op: output-style.act
**`output-style.act` is the PLANNED presentation setter: choose/create an output style and configure/generate/remove the status line — the writes the native model does via `/config`, `/statusline`, and settings edits, named here so a UI builds toward the real seam (a presentation-config writer the company has not built).**
```contract:op
op: output-style.act
resource: output-style
kind: act
status: planned
direction: outbound
atlas: [CC-26.2, CC-26.4]
tasks:
  - phrase: "switch to the explanatory output style"
    params: {act: set-style, outputStyle: Explanatory}
  - phrase: "make a custom output style that leads with a diagram"
    params: {act: create-style}
  - phrase: "set a status line showing model and context percent"
    params: {act: set-statusline}
  - phrase: "remove my status line"
    params: {act: clear-statusline}
  - alias: "change how Claude talks"
  - alias: "customize the status bar"
caller: required
bindings:
  - { kind: tui, command: "/config (style picker) · edit outputStyle field · /statusline <NL description|delete> · edit statusLine object", transport: claude-tui, exposure: "n/a — interactive", status: planned, note: "NATIVE writer surface. /statusline accepts NL and Claude generates the script + updates settings. https://code.claude.com/docs/en/statusline#use-the-statusline-command" }
  - { kind: http, method: POST, path: "/output-style  (PLANNED — no such bridge route)", transport: bridge-http, exposure: "exposure.json#bridge-http", status: planned, note: "GAP: BRIDGE_ROUTES (runtime/bridge.py:45) has no outputStyle/statusLine route. (/api/presentation-pref is the COMPANY UI's altitude preference, unrelated.) A writer must edit the scope's settings file + (for custom styles) author the Markdown file. Unbuilt." }
liveness: none
emits: []
consequences:
  - when: "output style set (planned)"
    expect: []
    evidence: "the system prompt changes — but only AFTER /clear or a new session (read-once-at-start; prompt-cache reason). [[output-style#op: output-style.get]] reflects the saved name. No fabric event"
  - when: "status line set/generated (planned)"
    expect: []
    evidence: "the bar renders on the next assistant message / event (settings reload automatically, change appears on next interaction). No fabric event"
correlate: [session]
verification:
  set-style:      {state: unverified, note: "no settings-writer endpoint — planned"}
  set-statusline: {state: unverified, note: "no settings-writer endpoint — planned"}
```
### Description (purpose-free)
The native model's presentation writes, none bridged. OUTPUT STYLE: pick a built-in via `/config` -> Output style, or set the `outputStyle` settings field directly (`{"outputStyle": "Explanatory"}`); CREATE a custom style as a Markdown file (frontmatter name/description/keep-coding-instructions/force-for-plugin, body = instructions appended to the system prompt) at `~/.claude/output-styles`, `.claude/output-styles`, or the managed dir; a change takes effect after `/clear` or a new session because the system prompt is read once at start. STATUS LINE: `/statusline <natural-language description>` has Claude generate a script in `~/.claude/` and wire the `statusLine` setting; or configure manually (type=command, command=script-path-or-inline, optional padding/refreshInterval/hideVimModeIndicator); the script reads the JSON session data on stdin and prints colors/multi-line/OSC-8 links; remove via `/statusline delete`/`clear` or deleting the field. A company writer would render the enum + frontmatter + statusLine schema and write the right scope file. Until that bridge exists, `planned`.
### Request (PLANNED shape)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/output-style.act.request",
  "type": "object",
  "required": ["act"],
  "properties": {
    "act": { "enum": ["set-style", "create-style", "delete-style", "set-statusline", "clear-statusline"] },
    "scope": { "enum": ["user", "project", "local"], "description": "which settings/style-file location" },
    "outputStyle": { "type": "string", "description": "for set-style: a built-in or custom style name" },
    "customStyle": { "$ref": "ui-contract/output-style.custom-file" },
    "statusLine": { "$ref": "ui-contract/output-style.config#/properties/statusLine" } },
  "additionalProperties": false }
```
### Interaction semantics
Native rules a presentation editor MUST respect (sourced to the references):
- **Output style change is NOT immediate.** The system prompt is read once at session start; a style change applies after `/clear` or a new session, and it invalidates the prompt cache.
- **Custom styles drop the SWE instructions by default.** Without `keep-coding-instructions: true`, Claude Code's built-in software-engineering guidance is removed — correct for a non-SWE assistant, wrong if you still want it coding.
- **Output style vs neighbours:** output style MODIFIES the system prompt (every turn); CLAUDE.md adds a user message after it; `--append-system-prompt` is a one-off append; agents run a separately-scoped subagent; skills load task instructions on demand. A UI should not conflate them.
- **Status line is local + cosmetic:** runs locally (no API tokens), hides during autocomplete/help/permission prompts, and triggers can go quiet during idle (use `refreshInterval`). It cannot read the terminal directly — use `$COLUMNS`/`$LINES`.
### Errors
```contract:error
code: output-style.unknown-style | http: 400 | retryable: false
when: outputStyle names neither a built-in (Default/Proactive/Explanatory/Learning) nor a discoverable custom style file
teach: "Built-ins: Default, Proactive, Explanatory, Learning. Custom styles must live in ~/.claude/output-styles, .claude/output-styles, or the managed dir. See [[output-style#Representation]]; source https://code.claude.com/docs/en/output-styles#built-in-output-styles."
```
```contract:error
code: output-style.not-exposed | http: 501 | retryable: false
when: any call against output-style.act today
teach: "Output-style + status-line setting is PLANNED — the company has no presentation-config writer (/api/presentation-pref is the company UI's own altitude preference, unrelated). Native path: /config + outputStyle field for style; /statusline + statusLine object for the bar (https://code.claude.com/docs/en/output-styles). The bridge gap is named in this op's bindings."
```
Adjacent: [[output-style#op: output-style.get]] (the read), [[extensions]] (plugins ship output styles in output-styles/), [[context-window]] · [[cost-usage]] (the readings a status line displays).

## Errors
**Resource-level error vocabulary: `output-style.unknown-style` (the style-name guard) and `output-style.not-exposed` (the honest 501 every write returns until the presentation-config writer is built).** Both teach the native recovery: use /config / /statusline or edit the settings field. No error claims a presentation-management capability the company does not have.

## Links
**No address-typed fields: output style and status line reference no fabric addresses.** Style names are settings strings / file names; the statusLine `command` is a filesystem path or inline shell; the status line's JSON input fields are runtime READINGS (model/cost/context/git) the script consumes, not fabric schemes. None resolve to a corpus entry, by design. (The company UI's own /api/presentation-pref altitude preference is a distinct, company-internal surface.)
