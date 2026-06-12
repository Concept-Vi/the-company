---
type: contract-entry
resource: extensibility-patterns
summary: The meta-resource for customizing Claude Code — the chooser across the customization mechanisms (skills · custom commands · hooks · MCP servers · output styles · subagents · CLAUDE.md · plugins-as-package · settings precedence), the shared path placeholders (${CLAUDE_PROJECT_DIR}/${CLAUDE_PLUGIN_ROOT}/${CLAUDE_PLUGIN_DATA}), and the scope/precedence laws that govern them all; the company exposes no customization face, so this entry is documentation-as-data a UI uses to route an intent to the right mechanism.
schemes: []
status: planned
relates-to: ["[[hooks]]", "[[mcp-servers]]", "[[extensions]]", "[[output-style]]", "[[permission]]", "[[claude-memory]]"]
---

# Resource: extensibility-patterns

> **Refocus (Session Fabric R1.4, 2026-06-13):** the company command-wrapper endpoints this entry once cited (the ③④⑤ MCP tools + `/api/config|dev|auto` bridge arms + the R3 config_writer rail) were REMOVED — they duplicated what a real Claude Code session does natively. The capability is reached by DRIVING A REAL SESSION (the supervisor's spawn/inject + R1-prime profile); this entry remains as the NATIVE data-model declaration a UI renders. Ops whose only real endpoint was the wrapper are back to `planned` — honestly.

## Identity
**There is no addressable record and no scheme: extensibility-patterns is the CHOOSER resource — the relational map of which Claude Code customization mechanism fits a given intent, the placeholders and precedence laws shared across them, and the cross-references to each mechanism's own entry.** It exists because the named ambiguity "I want to customize Claude Code's behavior" routes to at least eight distinct mechanisms with overlapping reach, and a UI (or an agent) must pick the right one. Sourced to the customization comparison tables across https://code.claude.com/docs/en/output-styles#comparisons-to-related-features, https://code.claude.com/docs/en/skills, https://code.claude.com/docs/en/plugins#when-to-use-plugins-vs-standalone-configuration, and https://code.claude.com/docs/en/hooks. Every op is `planned` against the company: there is no company face for any of these mechanisms (the per-mechanism entries name each bridge gap); this entry adds no new capability — it routes among the ones the others contract.

## Representation
**An extensibility decision has three axes: WHAT you're changing (behavior/voice, gated actions, external tools, presentation, persistent facts), HOW it activates (always / on-demand / on-event / per-task), and WHERE it's scoped (user / project / local / plugin / enterprise) — the chooser maps an intent across these axes to one mechanism.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/extensibility.mechanism",
  "type": "object",
  "description": "one row of the chooser. Source: the customization comparison tables in the Claude Code docs.",
  "properties": {
    "mechanism": { "enum": ["output-style", "claude-md", "append-system-prompt", "subagent", "skill", "custom-command", "hook", "mcp-server", "plugin", "settings"] },
    "changes": { "type": "string", "description": "WHAT it affects" },
    "activation": { "enum": ["always", "on-invoke", "on-relevant", "on-event", "per-task", "at-launch"] },
    "entry": { "type": "string", "description": "the corpus entry that contracts it" } } }
```
The chooser (the relational map — read it as a routing table, not a list):
| Intent | Mechanism | Why this one, not its neighbours | Entry |
|---|---|---|---|
| Different role/tone/format EVERY turn | output style | modifies the system prompt directly (Proactive/Explanatory/Learning or custom) | [[output-style]] |
| Claude should always KNOW project conventions/facts | CLAUDE.md / memory | adds a user message after the system prompt — facts, not a procedure | [[claude-memory]] |
| A one-off system-prompt addition for a single run | `--append-system-prompt` | appends without removing the default prompt; not persisted | [[output-style]] (compared there) |
| A separately-scoped helper with its own prompt/model/tools | subagent | runs a subagent; the section of work is isolated | [[extensions]] (agents are a plugin/`.claude/agents/` component) |
| A reusable WORKFLOW / multi-step procedure / checklist | skill (SKILL.md) | loads task instructions on demand; cheap until used; can be `/invoked` or auto | [[extensions]] |
| The same as a skill but with a short `/name` and no namespace | custom command (`.claude/commands/*.md`) | legacy flat form, merged into skills; identical behavior, fewer features | [[extensions]] |
| Run code automatically AT a lifecycle point (block/log/format) | hook | fires on PreToolUse/PostToolUse/Stop/…; deterministic enforcement | [[hooks]] |
| HARD allow/deny of a tool (enforcement, not best-effort) | permission rules | the permission system enforces; a hook `if` fails open | [[permission]] |
| Give Claude access to an external tool/DB/API | MCP server | connects a stdio/http/sse/ws server's tools | [[mcp-servers]] |
| PACKAGE + share/version any of the above across projects/teams | plugin | bundles skills/agents/hooks/MCP/LSP/monitors/output-styles + a manifest | [[extensions]] |
| A persistent bottom bar of session data | status line | a shell script fed JSON session data | [[output-style]] |
| Tune a configuration value (cap/timeout/model/permission default) | settings | the settings.json hierarchy | [[fabric-config]] / [[permission]] / [[model]] |

| field | type | volatile? | changed-by | address? -> resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| chooser map | reference data | no | doc updates | — | documentation-as-data; NOT a company endpoint. The company exposes no mechanism-routing face |
| path placeholders | reference data | no | — | — | shared across hooks + MCP stdio + plugins (see State model). NOT a company lever |

## State model
**State model: stateless.** A chooser is reference data — no lifecycle. The shared LAWS it carries (below) are invariants across the mechanisms, not states.

The shared path placeholders (https://code.claude.com/docs/en/hooks#reference-scripts-by-path) — a UI authoring ANY script-bearing mechanism (hook command, plugin script, stdio MCP server) must offer these:
- `${CLAUDE_PROJECT_DIR}` — the project root. Set in hook env AND in stdio-MCP-server env AND plugin LSP server env. In project/user `.mcp.json` it needs a default (`${CLAUDE_PROJECT_DIR:-.}`); plugin configs substitute it directly.
- `${CLAUDE_PLUGIN_ROOT}` — the plugin's install dir; changes on each plugin update.
- `${CLAUDE_PLUGIN_DATA}` — the plugin's persistent data dir; survives plugin updates (use for dependencies/state).
- `${user_config.*}` — plugin hooks only; user-configuration values.
Exec form (args set) substitutes placeholders as plain strings with no shell tokenization (prefer for paths with spaces); shell form needs double-quoting.

The shared SCOPE + PRECEDENCE laws (a UI must surface the effective source, never silently merge):
- Settings/skills scope ladder: enterprise (managed) > user (`~/.claude/`) > project (`.claude/`) > local (`.claude/settings.local.json`, gitignored). Skill/command name collisions resolve enterprise>personal>project; a skill beats a same-named command; plugin skills are namespaced so cannot collide.
- MCP server scope precedence (no merging — highest source used ENTIRELY): local > project > user > plugin-provided > claude.ai connectors.
- `--add-dir` loads `.claude/skills/` from the added dir (the one config exception) but NOT subagents/commands/output-styles; the `permissions.additionalDirectories` SETTING grants file access only.
- WORKSPACE TRUST gates project-skill `allowed-tools`, skills-dir-plugins, and project/local `headersHelper` — a UI must require trust acceptance, never auto-trust.
- Enterprise managed settings can force-enable/disable plugins (`enabledPlugins`) and block user/project/plugin hooks (`allowManagedHooksOnly`, managed-marketplace exempt) — `--plugin-dir` cannot override forced plugins.

## Caller
**The chooser is consumed by whoever is deciding how to customize — an operator or an agent reasoning about mechanism selection; there is no company API caller and no consumer identity, because this entry routes among native mechanisms the company does not yet bridge.** Each chosen mechanism's own entry carries its real caller model and bridge gap.

## Operations

## op: extensibility-patterns.get
**`extensibility-patterns.get` is the PLANNED chooser lookup: given an intent, return the fitting mechanism(s) + the entry that contracts each + the placeholders/precedence laws that apply — documentation-as-data a UI uses to route, sourced to the Claude Code customization comparison tables, not a company endpoint.**
```contract:op
op: extensibility-patterns.get
resource: extensibility-patterns
kind: get
status: planned
direction: outbound
atlas: [CC-27.1, CC-27.2]
tasks:
  - phrase: "should I use a hook or a skill for this"
  - phrase: "what's the difference between an output style and CLAUDE.md"
  - phrase: "how do I share my customizations with my team"
  - phrase: "which path placeholder do I use in a plugin script"
  - alias: "how do I customize Claude Code"
  - alias: "pick the right extension mechanism"
  - alias: "settings precedence rules"
bindings:
  - { kind: cli, command: "(reference — the chooser is documentation across the output-styles/skills/plugins/hooks docs; the company exposes no routing endpoint)", transport: claude-cli, exposure: "n/a — claude CLI", status: planned, note: "no enumerable company registry; canonical source = the customization comparison tables. https://code.claude.com/docs/en/output-styles#comparisons-to-related-features" }
liveness: snapshot
live-twin: "none — static reference (grows as Claude Code adds mechanisms)"
emits: []
verification:
  chooser: {state: probe-verified, run: "doc-mirror read", date: 2026-06-12, note: "the chooser map + placeholders + precedence laws transcribed from claude-code-atlas output-styles.md/skills.md/plugins.md/hooks.md (fetched 2026-06-10) — documentation facts, not company runtime facts"}
```
The standing-distinction prose (the disambiguation that lives BETWEEN the mechanisms, V19-class): a hook ENFORCES at an event and a skill GUIDES on a task — if behavior must be deterministic use a hook (or, for hard tool gating, [[permission]] rules, since a hook `if` fails open); a skill is a reusable workflow that loads on demand. An output style changes the VOICE every turn; CLAUDE.md teaches FACTS; `--append-system-prompt` is a one-off. A subagent isolates a TASK with its own prompt/model/tools; a skill with `context: fork` runs in a forked subagent context. MCP gives Claude external TOOLS; the others shape Claude's own behavior. A plugin is the PACKAGE that ships any combination of the above for sharing/versioning — choose standalone `.claude/` for personal/experimental work (short `/name`), a plugin for team distribution (namespaced `/plugin:name`).
Adjacent: [[hooks]], [[mcp-servers]], [[extensions]] (skills/commands/plugins/agents), [[output-style]] (styles + status line), [[permission]] (hard enforcement), [[claude-memory]] (CLAUDE.md facts), [[fabric-config]] (settings values).

## Errors
**Resource-level error vocabulary: none beyond the chooser being reference data.** This entry exposes no write; it routes to other entries, each of which carries its own `*.not-exposed` 501 honesty for the company gap. A consumer that wants to ACT picks a mechanism and follows that entry's ops. No error here claims a capability the company does not have.

## Links
**No address-typed fields: the chooser references CORPUS ENTRIES by wikilink (the mechanisms it routes to), never fabric addresses.** The path placeholders (`${CLAUDE_PROJECT_DIR}` etc.) are environment-variable names substituted at runtime, and the scope/precedence laws are configuration discipline — none resolve to a fabric scheme. The wikilinks in this entry ARE its hypermedia: they take a consumer from "which mechanism" to the entry that contracts it.
