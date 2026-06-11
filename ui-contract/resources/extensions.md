---
type: contract-entry
resource: extensions
summary: The packaged-capability surface — skills (SKILL.md), custom slash commands (now merged into skills), and plugins (a .claude-plugin/plugin.json bundling skills/agents/hooks/MCP-servers/LSP/monitors/output-styles), plus marketplaces, install/enable, and the `/reload-plugins` lifecycle; the company exposes no skill/plugin manager, so this resource contracts the native surface a UI editor+installer renders, with the bridge gap named.
schemes: []
status: building
relates-to: ["[[hooks]]", "[[mcp-servers]]", "[[output-style]]", "[[extensibility-patterns]]", "[[session]]"]
---

# Resource: extensions

## Identity
**An extension is identified by its INVOCATION NAME and LOCATION — a skill by `/<name>` (plugin skills namespaced `/<plugin>:<name>`) sourced from a `SKILL.md` directory (or a `.claude/commands/*.md` file), a plugin by `<plugin-name>` (+ optional `@<marketplace>`) sourced from a `.claude-plugin/plugin.json` manifest — there is no `skill://` or `plugin://` fabric scheme, and the company exposes no endpoint to author, install, enable, or list them.**
Claude Code skills (https://code.claude.com/docs/en/skills), custom commands (merged into skills — same page), and plugins (https://code.claude.com/docs/en/plugins create · https://code.claude.com/docs/en/plugins-reference spec · https://code.claude.com/docs/en/discover-plugins install · https://code.claude.com/docs/en/plugin-marketplaces). This resource contracts the DATA MODEL a UI authoring tool + installer renders. Every op is `planned` against the company: the bridge's `/api/cognition/create_skill` (`runtime/bridge.py:1962`, Observed 2026-06-12) creates a COMPOSITION skill in the substrate brain — NOT a Claude Code Agent Skill (`SKILL.md`) — and no bridge route authors, installs, or enables a Claude Code extension. Native paths are file authoring + the `/plugin`, `/skills`/`/help`, and `--plugin-dir`/`--plugin-url` surfaces.

## Representation
**A skill is a `SKILL.md`: YAML frontmatter (only `description` recommended) + markdown instructions, optionally with supporting files. A plugin is a directory with a `.claude-plugin/plugin.json` manifest + component directories at the ROOT (skills/, commands/, agents/, hooks/, .mcp.json, .lsp.json, monitors/, output-styles/, bin/, settings.json).**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/skill.frontmatter",
  "type": "object",
  "description": "SKILL.md YAML frontmatter. Source https://code.claude.com/docs/en/skills#frontmatter-reference. All optional; description recommended.",
  "properties": {
    "name": { "type": "string", "description": "display label in skill listings; defaults to directory name. Does NOT change the typed command except for a plugin-ROOT SKILL.md" },
    "description": { "type": "string", "description": "what it does + when to use; Claude uses it to auto-invoke. description+when_to_use truncated at 1536 chars in the listing" },
    "when_to_use": { "type": "string", "description": "trigger phrases/examples; appended to description, counts toward the 1536 cap" },
    "argument-hint": { "type": "string", "description": "autocomplete hint e.g. [issue-number]" },
    "arguments": { "description": "named positional args for $name substitution; space-separated string or YAML list" },
    "disable-model-invocation": { "type": "boolean", "default": false, "description": "true = only YOU invoke (manual /name); also blocks subagent preload" },
    "user-invocable": { "type": "boolean", "default": true, "description": "false = only Claude invokes (hidden from / menu)" },
    "allowed-tools": { "description": "tools usable without prompting while active (project skills need workspace trust)" },
    "disallowed-tools": { "description": "tools removed from the pool while active; clears on next message" },
    "model": { "type": "string", "description": "model while active (this turn only); accepts /model values or `inherit`" },
    "effort": { "enum": ["low", "medium", "high", "xhigh", "max"], "description": "effort while active" },
    "context": { "enum": ["fork"], "description": "fork = run in a forked subagent context" },
    "agent": { "type": "string", "description": "subagent type when context:fork" },
    "hooks": { "type": "object", "description": "hooks scoped to this skill's lifecycle — see [[hooks]] (skill-frontmatter hooks honor `once`)" },
    "paths": { "description": "glob patterns limiting auto-activation to matching files (path-specific-rule format)" },
    "shell": { "enum": ["bash", "powershell"], "description": "shell for !`cmd` injection blocks (powershell needs CLAUDE_CODE_USE_POWERSHELL_TOOL=1)" } } }
```
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/plugin.manifest",
  "type": "object",
  "description": ".claude-plugin/plugin.json. Source https://code.claude.com/docs/en/plugins-reference#plugin-manifest-schema",
  "required": ["name"],
  "properties": {
    "name": { "type": "string", "description": "unique id AND skill namespace — skills become /<name>:<skill>" },
    "description": { "type": "string", "description": "shown in the plugin manager" },
    "version": { "type": "string", "description": "optional; if set, users update only on a bump; if omitted + git-distributed, the commit SHA is the version (every commit = new version)" },
    "author": { "type": "object" },
    "mcpServers": { "type": "object", "description": "inline MCP servers (alternative to a root .mcp.json) — see [[mcp-servers]]" } },
  "additionalProperties": true }
```
| field | type | volatile? | changed-by | address? -> resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| skill body | markdown | yes (planned: file edit; live-change-detection reloads SKILL.md text within the session) | NO company event — Claude Code watches skill dirs; plugin component changes need /reload-plugins | — | NOT a company lever. Native: author SKILL.md at ~/.claude/skills/<n>/ (personal), .claude/skills/<n>/ (project), <plugin>/skills/<n>/ (plugin); or .claude/commands/*.md (legacy, still works) |
| plugin enabled | boolean | yes | /plugin install/enable, --plugin-dir, managed enabledPlugins | — | install via /plugin from a marketplace; or --plugin-dir ./p (.zip ok v2.1.128+); or --plugin-url <zip>. /reload-plugins to (de)activate mid-session. NOT a company lever |
| command name | string | no | the skill's LOCATION (dir name; file basename for commands/; plugin namespace) | — | dir-name -> /name; .claude/commands/x.md -> /x; plugin skill -> /plugin:skill; plugin-root SKILL.md -> frontmatter name (the one case name sets the command) |

## State model
**State model: stateless (the DEFINITION); a plugin has an enabled/disabled runtime flag that is not a contracted machine.** A skill/command definition is declarative files. A plugin is enabled or disabled at runtime (per session / per settings); `/reload-plugins` reconnects its skills, agents, hooks, MCP servers, LSP servers. Live-change-detection reloads SKILL.md TEXT within a session (a new top-level skills dir needs a restart; plugin component dirs need /reload-plugins). The company contracts neither authoring nor the enable flag today.

## Caller
**Authoring extensions is the operator writing files; installing/enabling plugins is the operator via `/plugin` or `--plugin-dir`/`--plugin-url`; there is no company API caller and no HTTP consumer identity, because the company exposes no extension face.** Project skills' `allowed-tools` and skills-dir-plugins require accepting the WORKSPACE TRUST dialog before they grant tool access or load — a skill can grant itself broad tool access, so a UI must surface trust state, never auto-trust. Enterprise managed settings can force-enable/disable plugins (`enabledPlugins`) which `--plugin-dir` cannot override.

## Operations

## op: extensions.list
**`extensions.list` is the PLANNED inventory read: every available skill/command (name, source level, who-can-invoke) and every installed plugin (name, marketplace, enabled state, components) — the data behind `/help`, `/skills`, `/agents`, and `/plugin`, which the company does not surface through any face.**
```contract:op
op: extensions.list
resource: extensions
kind: list
status: building
direction: outbound
atlas: [CC-03.1, CC-13.1]
tasks:
  - phrase: "list my skills and slash commands"
  - phrase: "what plugins are installed"
  - phrase: "which marketplaces are added"
  - alias: "show available commands"
  - alias: "browse my extensions"
bindings:
  - { kind: mcp, tool: config_extensions, op: "op='list'", server: company, exposure: "exposure.json#mcp.company", status: building, note: "BUILT (Capability Fabric ③): the MCP face reads SKILL.md / plugin state via the R3 config_writer. The handler runtime/capability_handlers/config_authoring.py:extensions backs both faces (DRY). live-verify pending (lead): a REAL .claude write / native claude-CLI round-trip." }
  - { kind: tui, command: "claude (interactive) then /help (commands+skills) · /plugin (plugins+marketplaces) · /agents (agents)", transport: claude-tui, exposure: "n/a — interactive", status: planned, note: "NATIVE only. Bundled skills (/code-review /debug /loop /batch /claude-api /run /verify) listed in /help marked Skill. No company endpoint mirrors it. https://code.claude.com/docs/en/skills#bundled-skills" }
liveness: snapshot
live-twin: "live-change-detection updates skills within a session; no company stream"
emits: []
verification:
  list: {state: unverified, note: "no company face; native /help, /plugin, /skills, /agents are interactive-TUI — not contracted endpoints"}
```
Skill command-name resolution (https://code.claude.com/docs/en/skills#how-a-skill-gets-its-command-name): directory name for `~/.claude/skills/<n>/` and `.claude/skills/<n>/`; file basename for `.claude/commands/x.md`; plugin namespace for `<plugin>/skills/<n>/` -> `/<plugin>:<n>`; frontmatter `name` for a plugin-ROOT `SKILL.md`. Override precedence when names collide: enterprise > personal > project; a skill beats a same-named command.
Adjacent: [[extensions#op: extensions.act]] (author/install/enable), [[hooks]] (plugins ship hooks), [[mcp-servers]] (plugins ship MCP servers), [[output-style]] (plugins ship output styles).

## op: extensions.get
**`extensions.get` is the PLANNED single-extension detail read: a skill's frontmatter + body + supporting files, or a plugin's manifest + bundled components — the data a UI editor opens for editing, not surfaced by the company.**
```contract:op
op: extensions.get
resource: extensions
kind: get
status: building
direction: outbound
atlas: [CC-03.1, CC-13.1]
tasks:
  - phrase: "show the SKILL.md for my deploy skill"
  - phrase: "what does this plugin bundle"
  - alias: "open a skill for editing"
  - alias: "inspect a plugin's components"
bindings:
  - { kind: mcp, tool: config_extensions, op: "op='get'", server: company, exposure: "exposure.json#mcp.company", status: building, note: "BUILT (Capability Fabric ③): the MCP face reads a SKILL.md via the R3 config_writer. The handler runtime/capability_handlers/config_authoring.py:extensions backs both faces (DRY). live-verify pending (lead): a REAL .claude write / native claude-CLI round-trip." }
  - { kind: cli, command: "(read the SKILL.md / plugin.json file directly; or /plugin in claude-tui for the manager view)", transport: claude-cli, exposure: "n/a — claude CLI", status: planned, note: "NATIVE: a skill/plugin is files on disk; the company exposes no structured reader. https://code.claude.com/docs/en/plugins-reference" }
liveness: snapshot
live-twin: "none — static between file edits"
emits: []
verification:
  get: {state: unverified, note: "no company face — planned"}
```
Adjacent: [[extensions#op: extensions.list]] (the inventory), [[extensions#op: extensions.act]] (write/install).

## op: extensions.act
**`extensions.act` is the PLANNED authoring + plugin manager: create/edit a skill (SKILL.md + supporting files), scaffold/package a plugin, add a marketplace, install/uninstall/enable/disable a plugin, and `/reload-plugins` — the operations the native model does via file authoring + the `/plugin` CLI, named here so a UI builds toward the real seam (an authoring + install bridge the company has not built).**
```contract:op
op: extensions.act
resource: extensions
kind: act
status: building
direction: outbound
atlas: [CC-03.2, CC-03.3, CC-13.2, CC-13.3, CC-13.4, CC-13.5]
tasks:
  - phrase: "create a skill that summarizes my git diff"
    params: {act: create-skill, scope: personal}
  - phrase: "make a slash command for deploying"
    params: {act: create-skill}
  - phrase: "scaffold a new plugin"
    params: {act: scaffold-plugin}
  - phrase: "add a plugin marketplace"
    params: {act: add-marketplace}
  - phrase: "install a plugin from a marketplace"
    params: {act: install-plugin}
  - phrase: "reload my plugins without restarting"
    params: {act: reload-plugins}
  - alias: "package my skills as a plugin"
  - alias: "/plugin install"
  - alias: "enable a plugin"
caller: required
bindings:
  - { kind: mcp, tool: config_extensions, op: "op='act' (create/update-skill + install/update/uninstall/validate-plugin + add-marketplace)", server: company, exposure: "exposure.json#mcp.company", status: building, note: "BUILT (Capability Fabric ③): the MCP face authors a SKILL.md or runs `claude plugin …` (exec-tier consent for install) via the R3 config_writer; delete-skill is a named building gap. The handler runtime/capability_handlers/config_authoring.py:extensions backs both faces (DRY). live-verify pending (lead): a REAL .claude write / native claude-CLI round-trip." }
  - { kind: cli, command: "author SKILL.md/plugin.json files · `claude plugin init <n>` (scaffold) · `claude plugin validate` · /plugin marketplace add <repo> · /plugin install <name>@<marketplace> · /reload-plugins · --plugin-dir/--plugin-url (test)", transport: claude-cli, exposure: "n/a — claude CLI", status: planned, note: "NATIVE writer surface (claude CLI + /plugin claude-tui). https://code.claude.com/docs/en/skills + https://code.claude.com/docs/en/plugins + https://code.claude.com/docs/en/discover-plugins" }
  - { kind: http, method: POST, path: "/extensions  (Wire-phase-owned, pending — MCP face built)", transport: bridge-http, exposure: "exposure.json#bridge-http", status: planned, note: "GAP: BRIDGE_ROUTES (runtime/bridge.py:45) has NO Claude-Code skill/plugin authoring or install route. (/api/cognition/create_skill is a COMPOSITION skill, unrelated.) A manager must write skill/plugin files, drive /plugin install, and reload. The bridge arm is Wire-phase-owned (pending); the MCP face is live now." }
liveness: none
emits: []
consequences:
  - when: "skill authored/edited (planned)"
    expect: []
    evidence: "[[extensions#op: extensions.list]] (/help) shows /<name>; live-change-detection reloads SKILL.md text within the session (new top-level dir needs restart). No fabric event"
  - when: "plugin installed/enabled (planned)"
    expect: []
    evidence: "/plugin shows it enabled; /reload-plugins activates its skills/agents/hooks/MCP/LSP without restart. No fabric event"
  - when: "marketplace added (planned)"
    expect: []
    evidence: "/plugin lists its plugins as installable; absence-shaped until added (named read: extensions.list via /plugin)"
correlate: [session]
verification:
  create-skill:    {state: unverified, note: "no authoring endpoint — planned"}
  install-plugin:  {state: unverified, note: "no install bridge — planned"}
  reload-plugins:  {state: unverified, note: "no company face — planned"}
```
### Description (purpose-free)
The native model's authoring + management operations, none bridged. SKILL: create `~/.claude/skills/<n>/SKILL.md` (personal, all projects), `.claude/skills/<n>/SKILL.md` (project), or `.claude/commands/x.md` (legacy flat command — both make `/x`); add supporting files (reference docs/templates/scripts) referenced from SKILL.md; control invocation with `disable-model-invocation`/`user-invocable`; pass args via `$ARGUMENTS`/`$N`/`$name`; inject live context with `` !`cmd` `` blocks. PLUGIN: `claude plugin init <n>` scaffolds a manifest + starter skill (loads as `<n>@skills-dir`); a manifest is `.claude-plugin/plugin.json` with component dirs at the ROOT (NOT inside .claude-plugin/); bundle skills/agents/hooks(hooks.json)/MCP(.mcp.json)/LSP(.lsp.json)/monitors(monitors.json)/output-styles/bin/settings.json. DISTRIBUTE: add a marketplace `/plugin marketplace add <github-repo>`; install `/plugin install <name>@<marketplace>`; the official `claude-plugins-official` (auto-available) + `claude-community` marketplaces exist; validate with `claude plugin validate` before submitting. TEST: `--plugin-dir ./p` (or .zip / --plugin-url). RELOAD: `/reload-plugins`. A company manager would render the schemas, write files, drive install, validate trust. Until that bridge exists, `planned`.
### Request (PLANNED shape)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/extensions.act.request",
  "type": "object",
  "required": ["act"],
  "properties": {
    "act": { "enum": ["create-skill", "update-skill", "delete-skill", "scaffold-plugin", "package-plugin", "add-marketplace", "install-plugin", "uninstall-plugin", "enable-plugin", "disable-plugin", "reload-plugins"] },
    "scope": { "enum": ["personal", "project", "enterprise", "plugin"], "description": "skill location" },
    "name": { "type": "string" },
    "marketplace": { "type": "string", "description": "github repo or marketplace id for install/add-marketplace" },
    "skill": { "$ref": "ui-contract/skill.frontmatter" },
    "manifest": { "$ref": "ui-contract/plugin.manifest" } },
  "additionalProperties": false }
```
### Interaction semantics
Native rules a manager MUST respect (sourced to the skills + plugins references):
- **Skill content lifecycle:** an invoked skill's rendered SKILL.md enters the conversation as ONE message and STAYS the whole session (Claude does not re-read it). Auto-compaction re-attaches the most recent invocation of each skill (first 5000 tokens each, 25000 combined budget, most-recent-first). Keep the body concise — every line is a recurring token cost.
- **Plugin layout is strict:** only `plugin.json` goes inside `.claude-plugin/`; commands/agents/skills/hooks live at the plugin ROOT. A single-skill plugin may place SKILL.md at the root (name from frontmatter).
- **Versioning:** explicit `version` = users update only on bump; omitted + git = commit SHA, every commit is a new version.
- **Trust:** project `.claude/skills/` `allowed-tools` and skills-dir-plugins need workspace trust; review project skills before trusting a repo.
- **Additional dirs:** `--add-dir`/`/add-dir` DO load `.claude/skills/` from the added dir (the one config exception), but NOT subagents/commands/output-styles, and the `permissions.additionalDirectories` SETTING grants file access only (no skill loading).
- **Default-settings plugins** ship a root `settings.json` (only `agent` + `subagentStatusLine` keys honored) that can make a plugin's custom agent the main thread when enabled.
### Errors
```contract:error
code: extensions.name-collision | http: 409 | retryable: false
when: a created skill/command name collides illegally, or a plugin name duplicates a forced managed plugin
teach: "Skill precedence: enterprise>personal>project; skill beats same-named command; plugin skills are namespaced /<plugin>:<skill> so cannot collide. Managed force-enabled plugins can't be overridden by --plugin-dir. See [[extensions#op: extensions.list]] for resolution."
```
```contract:error
code: extensions.untrusted | http: 403 | retryable: true
when: a project skill's allowed-tools or a skills-dir-plugin tries to load before workspace trust is accepted
teach: "Accept the workspace trust dialog for this folder first — a skill can grant itself broad tool access, so review project skills before trusting the repo. Source https://code.claude.com/docs/en/skills#pre-approve-tools-for-a-skill."
```
```contract:error
code: extensions.not-exposed | http: 501 | retryable: false
when: any call against extensions.act today
teach: "Skill/plugin authoring + management is PLANNED — the company has no authoring or install bridge (its /api/cognition/create_skill is a COMPOSITION skill, unrelated). Native path: author SKILL.md / plugin.json files + use /plugin, claude plugin init/validate, --plugin-dir, /reload-plugins (https://code.claude.com/docs/en/plugins). The bridge gap is named in this op's bindings."
```
Adjacent: [[extensions#op: extensions.list]] (verify), [[extensions#op: extensions.get]] (open for edit), [[hooks]] · [[mcp-servers]] · [[output-style]] (plugin component types), [[extensibility-patterns]] (which mechanism to choose).

## Errors
**Resource-level error vocabulary: `extensions.name-collision` (precedence/namespace guard), `extensions.untrusted` (the workspace-trust gate), and `extensions.not-exposed` (the honest 501 every write returns until the authoring + install bridge is built).** Each teaches the native recovery. No error claims an extension-management capability the company does not have.

## Links
**No address-typed fields: a skill/plugin references no fabric addresses.** Skill names are location-derived identifiers; `allowed-tools`/`disallowed-tools` are tool-NAME patterns; plugin component dirs are filesystem paths; marketplace ids are github repos. The `arguments`/`$ARGUMENTS` substitutions are runtime user input, not fabric schemes. None resolve to a corpus entry, by design.
