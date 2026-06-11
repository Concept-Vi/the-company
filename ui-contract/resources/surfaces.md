---
type: contract-entry
resource: surfaces
summary: The ways a human or program enters Claude Code — the CLI entry points and flags (claude, -p, -c, -r, --fork-session …), the interactive surfaces (terminal TUI, Desktop, Web, VS Code, JetBrains, Chrome), and the keybindings model (keybindings.json contexts + actions); the company drives EXACTLY ONE entry point (headless claude -p, via the supervisor) and the human interactive surfaces are out of fabric scope, so this resource maps the surface inventory and routes the one programmatic entry to F1.
schemes: []
status: building
relates-to: ["[[session]]", "[[headless-control]]", "[[settings]]", "[[diagnostics]]", "[[platform]]"]
---

# Resource: surfaces

## Identity
**A surface is identified by its KIND (a closed enum of entry points / interactive clients), not a
fabric address — there is no `surface://` scheme; the company is itself a consumer of exactly ONE
surface (the headless `claude -p` CLI entry, driven by the supervisor subprocess), and the
human-facing interactive surfaces (terminal TUI, Desktop, Web, IDE extensions) are NOT fabric
endpoints.** The surface inventory (source of truth https://code.claude.com/docs/en/cli-reference.md,
https://code.claude.com/docs/en/platforms.md, https://code.claude.com/docs/en/keybindings.md):
CLI entry points (`claude`, `-p`, `-c`/`--continue`, `-r`/`--resume`, `--fork-session`,
`--from-pr`, plus subcommands `claude auth|doctor|install|mcp|plugin|update|setup-token|agents`);
interactive clients (terminal TUI, native Desktop macOS/Windows/Linux, Web app, VS Code extension,
JetBrains IDEs, Chrome extension beta); and the keybindings layer (`~/.claude/keybindings.json`,
contexts × actions). This resource documents the surface map so a UI knows which entry the company
drives and which surfaces are human-only.

## Representation
**A surface record is the tuple (kind, programmatic?, the company's relationship to it) — the company
drives the headless CLI entry and inherits the host's interactive surfaces only as the human's own
tools; nothing here is a company-owned object.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/surfaces.surface",
  "type": "object",
  "properties": {
    "kind": { "enum": ["cli-headless", "cli-interactive", "desktop", "web", "vscode", "jetbrains", "chrome"],
              "description": "the entry-point / client kind. cli-headless (claude -p) is the ONLY one the company drives" },
    "programmatic": { "type": "boolean", "description": "true = machine-drivable (cli-headless); false = human-interactive (the rest)" },
    "company_relationship": { "enum": ["driven", "host-only"],
              "description": "driven = the supervisor spawns it (cli-headless only); host-only = the human's surface, the company neither drives nor exposes it" } },
  "additionalProperties": false }
```
| field | type | volatile? | changed-by | address? -> resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| cli-headless | the driven surface | n/a | the supervisor builds the `claude -p` invocation (`runtime/session_supervisor.py:259-265`) | -> [[session]], [[headless-control]] | DRIVEN. The supervisor spawns `claude -p --input-format stream-json --output-format stream-json --verbose --permission-mode … --mcp-config … --strict-mcp-config --allowedTools mcp__company` (+resume/fork). This is the company's whole entry-point relationship to Claude Code |
| --resume / --fork-session / --continue | CLI flags | n/a | threaded by `spawn(resume=…, fork=…)` | -> [[session#op: session.create]] | THREADED (the F1 building slice): resume + fork are wired; --continue's "most recent" is a host convenience the supervisor does not need (it addresses sessions explicitly) |
| --from-pr, claude agents, the ~80 other flags | CLI flags/subcommands | n/a | NOT threaded | — | NOT threaded. The supervisor's invocation is fixed; flags beyond resume/fork/permission-mode/mcp/allowedTools are not wired (model/effort -> [[model]], settings/add-dir -> [[settings]], debug -> [[diagnostics]], output-format/json-schema -> [[headless-control]]) |
| cli-interactive / desktop / web / vscode / jetbrains / chrome | host-only surfaces | n/a | the human launches them | — | HOST-ONLY. None is a fabric endpoint. The supervisor spawns headless `-p`, which has NO interactive TUI — the company cannot drive a human surface. These surfaces' affordances (slash commands, /config editor, diff view, panels) are CC-02/CC-03/CC-26-class, out of F8 scope |
| keybindings | ~/.claude/keybindings.json | yes (hot-reloaded; no restart) | the human edits the file or runs /keybindings | -> see [[surfaces#op: surfaces.get-keybindings]] | HOST-ONLY data model. Bindings apply to the interactive TUI/Desktop the company does not drive; documented here as a settings-sibling data shape, NOT a fabric capability |

## State model
**State model: stateless.** A surface has no lifecycle in the company — it is an entry point or a
client kind, not a stateful object. The SESSION a surface launches owns the lifecycle
([[session#State model]]). Keybindings are a config file, recomputed on edit (hot-reload), with no
state machine.

## Caller
**The company is the caller of exactly one surface: the supervisor process invokes the headless CLI
entry as a subprocess; every human-interactive surface has the HUMAN as its caller and no fabric
caller at all.** There is no company op that opens a Desktop window, a Web session, or an IDE panel —
those are launched by the person at their machine. The supervisor's relationship is strictly: build a
`claude -p` argv, spawn it, talk stream-json over its stdio (see [[headless-control]] and
[[session#Caller]]).

## Operations

## op: surfaces.list
**`surfaces.list` is the surface-inventory read: the closed set of Claude Code entry points and
interactive clients with the company's relationship to each — PLANNED as a company face because there
is no surface-catalog endpoint; the inventory is the static [[surfaces#Representation]] table, and the
ONE surface the company drives is already addressed through [[session]].**
```contract:op
op: surfaces.list
resource: surfaces
kind: list
status: planned
direction: outbound
atlas: [CC-01.1, CC-02.1]
tasks:
  - phrase: "what entry points can start a Claude Code session"
  - phrase: "which surfaces can the company drive"
  - phrase: "list the Claude Code interactive clients"
  - alias: "entry points"
  - alias: "how do you start claude code"
  - alias: "available surfaces"
bindings:
  - { kind: http, method: GET, path: "/surfaces  (PLANNED: there is no surface-catalog endpoint)", transport: supervisor-http, exposure: "exposure.json#supervisor-http", status: planned, note: "GAP + scope: no catalog endpoint exists and most surfaces are human-only, so a live endpoint would only ever report cli-headless=driven and the rest=host-only. The static [[surfaces#Representation]] table is the inventory; the one driven surface is operated via [[session#op: session.create]]" }
liveness: snapshot
live-twin: "none — the surface set is a static enum; the driven surface's live sessions are listed by [[session#op: session.list]]"
emits: []
verification:
  surface-catalog-read: {state: unverified, note: "no catalog endpoint; inventory is static — planned"}
```
The complete CLI entry-point set (Observed from cli-reference.md, v2.1.170): `claude` (interactive),
`claude -p`/`--print` (headless — the company's surface), `-c`/`--continue` (most-recent in cwd),
`-r`/`--resume [id]` (specific, picker if no id), `--fork-session` (resume under a new id),
`--from-pr [n]` (PR-linked), and subcommands `auth · doctor · install · mcp · plugin · update ·
upgrade · setup-token · agents · project · auto-mode · ultrareview`. The interactive client set:
terminal TUI, Desktop (macOS/Windows/Linux), Web, VS Code extension, JetBrains IDEs, Chrome extension
(beta). Only `claude -p` is machine-drivable and only it the company drives. CLI subcommands map to
other resources: `auth`->[[auth]], `doctor`->[[diagnostics]], `install`/`update`->[[platform]],
`mcp`/`plugin`-> (MCP/plugins lanes).
```contract:example
captured: synthetic            # status=planned -> synthetic legal AND loud; no catalog endpoint (V11)
binding: http
request: |
  GET /surfaces HTTP/1.1   (PLANNED endpoint)
response: |
  HTTP/1.1 501 Not Implemented
  {"error": "No surface catalog endpoint; the surface set is the static Representation enum. The only company-driven surface is cli-headless (claude -p) — operate it via POST /spawn. The interactive clients (Desktop/Web/IDE/TUI) are host-only and not fabric endpoints."}
```
Adjacent: [[session#op: session.create]] (driving the one company surface), [[headless-control]]
(the stream-json protocol over it), [[surfaces#op: surfaces.get-keybindings]] (the keybindings model),
[[platform#op: platform.install]] (where surfaces come from).

## op: surfaces.get-keybindings
**`surfaces.get-keybindings` is the keybindings data-model read: the `~/.claude/keybindings.json`
shape — a `bindings` array of {context, keystroke->action} blocks over a closed context set and
namespaced actions — documented here as a settings-sibling so a UI can render/validate shortcut config,
PLANNED at the company layer because keybindings govern the interactive TUI the fabric does not drive.**
```contract:op
op: surfaces.get-keybindings
resource: surfaces
kind: get
status: building
direction: outbound
atlas: [CC-04.1]
tasks:
  - phrase: "what keyboard shortcuts does Claude Code use"
  - phrase: "the keybindings.json schema"
  - phrase: "how to rebind a shortcut"
    params: {note: "set keystroke->action, or action->null to unbind"}
  - alias: "keyboard shortcuts"
  - alias: "customize keybindings"
  - alias: "rebind keys"
bindings:
  - { kind: mcp, tool: config_keybindings, op: "op='list'|'get' (read) + op='act' (set-binding) — REOPENED CC-04", server: company, exposure: "exposure.json#mcp.company", status: building, note: "BUILT (Capability Fabric ③): the MCP face reads/writes ~/.claude/keybindings.json via the R3 config_writer (reopened CC-04; non-executable, reversible). The handler runtime/capability_handlers/config_authoring.py:keybindings backs both faces (DRY). live-verify pending (lead): a REAL .claude write / native claude-CLI round-trip." }
  - { kind: cli, command: "/keybindings   (HOST interactive command — opens ~/.claude/keybindings.json; NOT a company route)", transport: cli-local, exposure: "n/a — Claude Code built-in", status: planned, note: "GAP + scope: keybindings apply to the interactive TUI/Desktop the company does not drive (the supervisor spawns headless -p with no TUI). Documented as a data model for a config UI; there is no company endpoint and one would be inert against a headless session. Requires Claude Code v2.1.18+" }
liveness: snapshot
live-twin: "none — keybindings.json hot-reloads on edit; no live stream"
emits: []
verification:
  keybindings-model: {state: unverified, note: "host-only interactive config; no company op — planned"}
```
The keybindings model (source https://code.claude.com/docs/en/keybindings.md): a file with a
`bindings` array; each block is `{context, bindings: {keystroke: action | null}}`. Contexts are a
closed set — `Global, Chat, Autocomplete, Settings, Confirmation, Tabs, Help, Transcript,
HistorySearch, Task, ThemePicker, Attachments, Footer, MessageSelector, DiffDialog, ModelPicker,
Select, Plugin, Scroll, Doctor`. Actions follow `namespace:action` (e.g. `chat:submit`,
`app:toggleTodos`, `doctor:fix`). Keystroke syntax: `+`-joined modifiers (`ctrl/control`,
`shift`, `alt|opt|option|meta`, `cmd|command|super|win`), space-separated chords (`ctrl+k ctrl+s`),
a bare uppercase letter implies Shift, `null` unbinds. Reserved (un-rebindable): `Ctrl+C` (interrupt),
`Ctrl+D` (exit), `Ctrl+M` (= Enter), Caps Lock. `/doctor` lists keybinding validation warnings (parse
errors, invalid contexts, reserved/multiplexer conflicts, duplicates) — see [[diagnostics]].
```contract:example
captured: synthetic            # status=planned -> synthetic legal AND loud; host-only config model (V11)
binding: cli
request: |
  # HOST interactive session (not a company route):
  /keybindings        # opens ~/.claude/keybindings.json
response: |
  {
    "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
    "bindings": [
      { "context": "Chat",
        "bindings": { "ctrl+e": "chat:externalEditor", "ctrl+u": null } }
    ]
  }
```
Adjacent: [[settings#Representation]] (keybindings as a settings sibling), [[diagnostics#op:
diagnostics.act]] (/doctor validates keybindings), [[surfaces#op: surfaces.list]] (the surface this
config belongs to).

## Errors
**Resource-level error vocabulary: `surfaces.not-exposed` (the honest 501 for any surface-catalog or
keybindings call — the surface set is a static enum and these surfaces are human-only / inert against
the headless entry the company drives).** It teaches the in-corpus recovery: read the static inventory,
drive the one company surface via [[session]], and treat interactive-client config as a host concern.
```contract:error
code: surfaces.not-exposed | http: 501 | retryable: false
when: any call to enumerate surfaces or read/set keybindings against the company
teach: "Surfaces are a static enum, not a live catalog; the only company-driven surface is cli-headless (claude -p), operated via [[session#op: session.create]]. Keybindings (and the other interactive clients) are HOST concerns — the supervisor drives a headless session with no TUI, so keybinding config is inert against it. Read the static models in [[surfaces#Representation]]."
```

## Links
**No address-typed fields: a surface references the `session://` it launches (dereferences to
[[session]] via [[session#op: session.create]]) and points at the resources that own the levers each
CLI subcommand maps to — [[auth]] (claude auth), [[diagnostics]] (claude doctor / --debug),
[[platform]] (claude install/update), [[headless-control]] (the stream-json protocol over -p),
[[settings]] (keybindings + --settings).** CLI flag names, client kinds, keybinding contexts and
action names are Claude Code identifiers (https://code.claude.com/docs/en/cli-reference.md,
keybindings.md), not fabric addresses — they never resolve to a corpus entry, by design.
