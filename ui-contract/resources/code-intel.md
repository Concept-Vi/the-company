---
type: contract-entry
resource: code-intel
summary: Claude Code's LSP-backed code intelligence — go-to-definition, find-references, hover types, document/workspace symbols, implementations, call hierarchy, and automatic post-edit diagnostics, all from a language server installed via a code-intelligence plugin. A native in-session capability inside the sessions the company spawns; NO company endpoint exposes it — contracted as the native surface with the bridge gap named.
schemes: []
status: building
relates-to: ["[[session]]", "[[headless-control]]", "[[knowledge-corpus]]"]
---

# Resource: code-intel
## Identity
**Code intelligence is keyed by the SESSION whose language server it belongs to (`session://<id>`)
and the workspace that session runs in — there is no `code-intel://` scheme and no standalone
record.** It is Claude Code's built-in LSP tool: once a code-intelligence plugin is installed and
its language-server binary is on PATH, the tool gives the session real-time type info, symbol
navigation, and automatic diagnostics after edits (source `tools-reference.md#lsp-tool-behavior`,
`discover-plugins.md#code-intelligence`, `plugins-reference.md#lsp-servers`, vault
`claude-code-atlas`). This resource contracts the levers over that machinery. HONEST STATUS: it is
`planned` against the company — the LSP tool runs INSIDE a spawned session's own context (it is a
tool the model calls, not a service with an endpoint), and the company exposes NO face to invoke it,
read its diagnostics, or configure it from outside. A consumer reaching for symbol navigation
through a company API is reaching for an unbuilt bridge; the gap is named per op.

## Representation
**Code intelligence is the LSP capability set a session HAS (active iff a code-intelligence plugin +
its server binary are present) plus the automatic diagnostics the language server pushes into the
session's context after each edit — a per-session capability, not an addressable object.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/code-intel.capability",
  "type": "object",
  "description": "the native LSP tool's capability surface (source tools-reference.md#lsp-tool-behavior). These are the tool's modes; the company exposes none of them through an endpoint",
  "properties": {
    "active": { "type": "boolean", "description": "false until a code-intelligence plugin is installed for the language AND the server binary is on PATH" },
    "navigation": { "type": "array", "items": { "enum": ["definition", "references", "hover-type", "document-symbols", "workspace-symbol-search", "implementations", "call-hierarchy"] },
                    "description": "the seven navigation operations the LSP tool can call directly" },
    "diagnostics": { "type": "boolean", "description": "automatic: after each file edit the server reports type errors/warnings into the session's context (default true; .lsp.json diagnostics:false keeps navigation but suppresses auto-injection)" },
    "server": { "type": "object", "description": "the .lsp.json / plugin.json lspServers config: command, args, extensionToLanguage, transport(stdio|socket), env, initializationOptions, startupTimeout, maxRestarts" } } }
```
| field | type | volatile? | changed-by | address? → resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| active | bool | yes (plugin install) | the session's plugin/binary state | — | per-session, INTERNAL to the spawned session; the company cannot read it (no endpoint). The native default tool surface a fabric session gets is `--allowedTools mcp__company` ([[permission]]) — native LSP is NOT in that allow set unless the spawn changes (planned) |
| navigation | array | no (capability) | — | — | the 7 ops the model calls in-session; NOT individually invokable from outside |
| diagnostics | bool | no | `.lsp.json` config | — | auto-injected after edits when a plugin is active; Ctrl+O shows them inline (interactive only) — invisible to a company consumer |
| server config | object | yes | plugin author / repo enabledPlugins | — | the official marketplace ships clangd/csharp/gopls/jdtls/kotlin/lua/php/pyright/rust-analyzer/swift/typescript LSP plugins; binary installed separately. The company spawns sessions but does NOT preinstall or configure code-intelligence plugins |

## State model
**State model: stateless (a per-session capability).** Code intelligence has no lifecycle of its
own — it activates when a plugin+binary are present and reports diagnostics as the session edits.
The language server process has a lifecycle (startup with `startupTimeout`, `maxRestarts` on crash)
but that is internal to the session's own runtime; the company observes none of it.

## Caller
**Inside a session the CALLER is the model itself (the LSP tool is one of the model's tools); from
OUTSIDE there is no caller because there is no company endpoint to call.** A consumer cannot today
ask the company "find references to symbol X in session Y" — the capability lives in-session. The
nearest real seam is the headless control protocol ([[headless-control]]): if a future company face
read a session's native tool surface (`system/init` tools) or threaded LSP-plugin config into the
spawn, this would become observable/configurable — both are `planned`.

## Operations

## op: code-intel.act
**`code-intel.act` is the PLANNED symbol-navigation + diagnostics bridge: invoke the LSP tool's
operations (definition / references / hover / symbols / implementations / call-hierarchy) and read
post-edit diagnostics for a session — the native capability the company does not yet expose, named
here so a UI builds toward the real seam (a session-scoped LSP face) rather than a fiction.**
```contract:op
op: code-intel.act
resource: code-intel
kind: act
status: building
direction: outbound
atlas: [CC-16.1, CC-16.2, CC-16.3]
tasks:
  - phrase: "jump to where this symbol is defined"
    params: {act: definition}
  - phrase: "find all references to a function across the workspace"
    params: {act: references}
  - phrase: "what type does this expression have"
    params: {act: hover}
  - phrase: "list the type errors after the last edit"
    params: {act: diagnostics}
  - alias: "go to definition"
  - alias: "find references"
  - alias: "symbol search"
  - alias: "call hierarchy"
bindings:
  - { kind: mcp, tool: dev_code_intel, op-param: "op=act", server: company, exposure: "exposure.json#mcp-company", status: building, note: "L-④-dev: RAIL R1-prime — the handler builds a bridge-session spawn INTENT; the SUPERVISOR (spawn_bridge_session, operator_consent-gated) runs the in-session LSP; result rides back as PROSE on the turn stream — liveness:stream, NO typed return_shape (§1.1). live-verify pending (lead): a REAL prose round-trip is the lead's slice, NEVER green-painted" }
  - { kind: http, method: "POST (PLANNED: a session-scoped LSP face)", path: "/api/code-intel  (does not exist)", transport: bridge-http, exposure: "exposure.json#bridge-http", status: planned, note: "GAP: no company endpoint invokes the LSP tool or reads its diagnostics. The capability runs inside the spawned session's own context. Verified: no language-server/LSP/definition-finding face in runtime/ mcp_face/ ops/ (grep 2026-06-12). Wiring path = either (a) thread an LSP-plugin config into the spawn ([[headless-control]] --bare/plugin config) and read diagnostics off the stream, or (b) run a company-side language server" }
liveness: none
emits: []
consequences:
  - when: "a navigation call (planned)"
    expect: []
    bound: "n/a — not built"
    evidence: "no company-visible outcome; in a native session the model receives the LSP result directly. The company sees only the FOLDED text/tool frames ([[headless-control#op: headless-control.watch]]), which do NOT carry structured LSP results today"
  - when: "post-edit diagnostics (planned)"
    expect: []
    bound: "n/a — not built"
    evidence: "natively auto-injected into the session's context after an edit; a company consumer cannot read them — the spawned session's diagnostics never reach a company face"
correlate: [session]
verification:
  navigation:  {state: unverified, note: "no company LSP face — planned; the native tool runs in-session only"}
  diagnostics: {state: unverified, note: "post-edit diagnostics are in-session context, never surfaced through the company — planned"}
```
### Description (purpose-free)
The native LSP tool, contracted as a planned company bridge. Inside a session with a
code-intelligence plugin active, the model can jump to a symbol's definition, find all references,
get type info at a position, list a file's symbols, search a symbol by name across the workspace,
find implementations of an interface, and trace call hierarchies — more precise than grep, fewer
file reads (source `tools-reference.md`, `discover-plugins.md`, `large-codebases.md`,
`costs.md#install-code-intelligence-plugins`). Separately, after every edit the language server
auto-reports type errors and warnings into the session's context so the model fixes mistakes
in-turn. NONE of this is reachable through a company endpoint — the company spawns sessions but does
not invoke their LSP tool from outside, read their diagnostics, or preinstall code-intelligence
plugins. This op names that gap and the two real wiring paths (spawn-config a plugin + read the
stream, or run a company-side server).
### Request (PLANNED shape — the contract the seam should fulfil)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/code-intel.act.request",
  "type": "object",
  "required": ["session", "act"],
  "properties": {
    "session": { "type": "string", "description": "session://<id> whose workspace + language server to query" },
    "act":     { "enum": ["definition", "references", "hover", "document-symbols", "workspace-symbol", "implementations", "call-hierarchy", "diagnostics"] },
    "file":    { "type": "string", "description": "workspace-relative path (for position-scoped acts)" },
    "position": { "type": "object", "properties": { "line": {"type":"integer"}, "character": {"type":"integer"} } },
    "symbol":  { "type": "string", "description": "for workspace-symbol search" } },
  "additionalProperties": false }
```
### Interaction semantics
Native rules a consumer MUST respect when this op lands (sourced to the docs):
- **Inactive until installed.** The LSP tool is inert until a code-intelligence plugin for the
  language is installed AND its server binary is on PATH (`Executable not found in $PATH` in the
  `/plugin` Errors tab otherwise). The company's spawned sessions do not preinstall these.
- **Diagnostics are automatic, not requested.** They push into context after each edit; the
  `diagnostics:false` `.lsp.json` flag keeps navigation but suppresses auto-injection.
- **Availability varies by language/environment.** Navigation precision depends on the language
  server; the official marketplace covers the 11 languages listed in Representation.
### Errors
```contract:error
code: code-intel.not-exposed | http: 501 | retryable: false
when: any call against this op today
teach: "Symbol navigation + diagnostics are PLANNED — they run inside a spawned session's LSP tool, with no company endpoint. To use code intelligence today, an operator installs a code-intelligence plugin (e.g. /plugin install typescript-lsp@claude-plugins-official) + the language-server binary IN the working session via [[extensions#op: extensions.act]]. The bridge gap is named in this op's bindings."
```
```contract:error
code: code-intel.server-inactive | http: 409 | retryable: false
when: (when built) a navigation call against a session whose language server is not active
teach: "Install the language's code-intelligence plugin and its server binary (see https://code.claude.com/docs/en/discover-plugins code-intelligence: pyright/gopls/rust-analyzer/typescript-language-server/...). Until active, the LSP tool is inert and only grep-based search is available."
```
```contract:example
captured: synthetic            # status=planned → synthetic legal AND loud; no company LSP endpoint exists (V11)
binding: http
request: |
  POST /api/code-intel HTTP/1.1   (PLANNED — endpoint does not exist)
  {"session":"as-91cf4502","act":"references","file":"src/auth.ts","position":{"line":42,"character":9}}
response: |
  HTTP/1.1 501 Not Implemented
  {"error":"Code intelligence is planned; the LSP tool runs inside the session, not via a company endpoint. Install a code-intelligence plugin + server binary in the working session. See discover-plugins.md#code-intelligence."}
```
Adjacent: [[session#op: session.get]] (the session whose workspace this navigates),
[[headless-control#op: headless-control.watch]] (the stream a future face would read diagnostics
off), [[knowledge-corpus#op: knowledge-corpus.search]] (the docs on LSP plugins).

## Errors
**Resource-level error vocabulary: `code-intel.not-exposed` (the honest 501 for any call today —
the capability is in-session, no company endpoint) and `code-intel.server-inactive` (the
plugin/binary-missing refusal a built face would return).** Both teach the live recovery — install
the code-intelligence plugin + language-server binary in the working session — and name the bridge
gap. No error claims a navigation face the company has not built.

## Links
**No address-typed fields: code intelligence references the `session://` it belongs to (dereferences
to [[session]]) and workspace-relative file paths (filesystem paths, not corpus addresses).** Symbol
results (definitions/references) are file+position locations, not fabric records — they never resolve
to a corpus entry, by design, since the whole capability is a planned in-session tool.
