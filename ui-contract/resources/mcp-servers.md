---
type: contract-entry
resource: mcp-servers
summary: The MCP server connections a Claude Code session loads — add/remove/list/get a stdio/http/sse/ws server, its scope (local/project/user) and config file, its transport+auth (OAuth 2.0, headers, headersHelper), and its live connection status; the company manages its OWN MCP face but exposes no API to manage a session's MCP server set, so this resource contracts the native `claude mcp` surface with the bridge gap named.
schemes: []
status: building
relates-to: ["[[hooks]]", "[[extensions]]", "[[permission]]", "[[session]]"]
---

# Resource: mcp-servers

## Identity
**An MCP server is identified by its NAME within a scope (local/project/user) — there is no `mcp://` fabric scheme; a server is an entry in a config file (`~/.claude.json` for local+user, `.mcp.json` for project, or a plugin's `.mcp.json`/`plugin.json`), and the company exposes no endpoint to add, remove, or list a session's MCP servers.**
Claude Code connects to external tools via MCP servers, documented at https://code.claude.com/docs/en/mcp (reference) and https://code.claude.com/docs/en/mcp-quickstart. This resource contracts the DATA MODEL a UI manager renders — the server config schema, the three scopes, the four transports, the OAuth/auth model, the connection status — NOT a new addressable object. Every op is `planned` against the company: `mcp_face/server.py` (Observed 2026-06-12) IS the company's own MCP server (FastMCP "company"), but the company has no face to manage which MCP servers a SESSION loads. Native management is the `claude mcp` CLI subcommands + the `/mcp` interactive panel. NOTE: the bridge's `/api/cognition/create_skill` route (`runtime/bridge.py:1962`) creates a COMPOSITION skill in the substrate brain — it is NOT MCP-server management and is unrelated to this resource.

## Representation
**An MCP server config carries a transport `type` (stdio / http / streamable-http / sse / ws), the connection details for that transport (command+args+env for stdio; url+headers for remote), an optional `oauth` block, a `timeout`, and (as a runtime fact, not config) a connection STATUS and tool count.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/mcp-server.config",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": { "enum": ["stdio", "http", "streamable-http", "sse", "ws"],
      "description": "transport. `streamable-http` is an ALIAS for `http` (the MCP spec name). SSE is DEPRECATED. WS supports neither OAuth nor the --transport flag — header auth only. Source https://code.claude.com/docs/en/mcp#installing-mcp-servers" },
    "command": { "type": "string", "description": "stdio: executable; supports ${VAR} / ${VAR:-default} expansion. Claude Code sets CLAUDE_PROJECT_DIR in the spawned server env" },
    "args": { "type": "array", "items": { "type": "string" }, "description": "stdio: argument vector; everything after `--` on the CLI is passed untouched" },
    "env": { "type": "object", "description": "stdio: env vars passed to the server; supports ${VAR} expansion" },
    "url": { "type": "string", "description": "http/sse/ws: server URL; supports ${VAR} expansion" },
    "headers": { "type": "object", "description": "http/sse/ws: static request headers (e.g. Authorization: Bearer …); supports ${VAR} expansion" },
    "headersHelper": { "type": "string", "description": "http/ws: command run at connect time whose stdout JSON merges into headers (for non-OAuth auth: Kerberos, short-lived tokens, SSO). 10s timeout, no caching, runs fresh each connect. Project/local scope requires workspace trust" },
    "oauth": { "type": "object", "description": "http/sse: OAuth 2.0. Fields: clientId, callbackPort, scopes (space-separated string), authServerMetadataUrl (https only, v2.1.64+). Source https://code.claude.com/docs/en/mcp#authenticate-with-remote-mcp-servers" },
    "timeout": { "type": "integer", "description": "per-server per-tool-call wall-clock limit in MILLISECONDS; values <1000 ignored; overrides MCP_TOOL_TIMEOUT env for this server" } },
  "additionalProperties": true }
```
| field | type | volatile? | changed-by | address? -> resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| type / transport | enum | no | — | — | NOT a company lever. Native: `claude mcp add --transport <t> <name> <url|-- cmd>` |
| scope | enum (local/project/user) | no | — | — | local default (`~/.claude.json`, current project only) · project (`.mcp.json`, team-shared, needs approval) · user (`~/.claude.json`, all projects). Set with `--scope` |
| oauth/auth | object | yes (token refresh) | the `/mcp` auth flow | — | OAuth tokens stored in keychain (macOS) / credentials file; auto-refreshed; "Clear authentication" in /mcp revokes. NOT a company lever |
| status | enum | yes | the connection lifecycle | — | runtime fact: connected / pending / failed / `⏸ Pending approval` (project servers) / `✗ Rejected`. Observable in `/mcp` + `claude mcp get`; auto-reconnect with exponential backoff (HTTP/SSE: 5 attempts; stdio not reconnected). NOT surfaced by a company face |
| tool count | integer | yes | server's tools/list | — | shown in `/mcp` next to each server; flags servers advertising tools capability but exposing none |

## State model
**State model: stateless (the CONFIG); the CONNECTION has a runtime status that is not a contracted machine.** The config record has no lifecycle — it is declarative data in a config file. The live CONNECTION moves through connecting -> connected / pending-approval / failed / rejected at runtime, with automatic reconnection (HTTP/SSE exponential backoff, up to 5 attempts; initial-connect retry up to 3 on transient errors as of v2.1.121). The company contracts neither the config write nor the connection status today.

## Caller
**Managing MCP servers is the operator running `claude mcp …` subcommands or the `/mcp` panel in an interactive session; there is no company API caller and no HTTP consumer identity, because the company exposes no MCP-server-management face.** Project-scoped servers from `.mcp.json` require per-operator APPROVAL before use (security: a shared config could point Claude at a malicious server) — `claude mcp reset-project-choices` resets those choices. Enterprise admins deploy servers via managed configuration. A UI manager must surface the approval state, never auto-approve.

## Operations

## op: mcp-servers.list
**`mcp-servers.list` is the PLANNED roster read: every configured MCP server with its scope, transport, connection status, and tool count — the data behind `claude mcp list` and the `/mcp` panel, which the company does not surface through any face.** <!-- lint-ok: "/mcp panel" is the native Claude Code interactive surface name, F4 carve-out (CONVENTIONS) -->
```contract:op
op: mcp-servers.list
resource: mcp-servers
kind: list
status: building
direction: outbound
atlas: [CC-11.1, CC-11.5]
tasks:
  - phrase: "list the MCP servers a session has"
  - phrase: "which MCP servers are connected"
  - alias: "show my MCP connections"
  - alias: "check MCP server status"
bindings:
  - { kind: mcp, tool: config_mcp_servers, op: "op='list'", server: company, exposure: "exposure.json#mcp.company", status: building, note: "BUILT (Capability Fabric ③): the MCP face runs `claude mcp list` via the R3 config_writer. The handler runtime/capability_handlers/config_authoring.py:mcp_servers backs both faces (DRY). live-verify pending (lead): a REAL .claude write / native claude-CLI round-trip." }
  - { kind: cli, command: "claude mcp list", transport: claude-cli, exposure: "n/a — claude CLI", status: planned, note: "NATIVE: `claude mcp list` (CLI) + `/mcp` (claude-tui) (interactive panel: tool count, status, auth state). No company endpoint mirrors it. https://code.claude.com/docs/en/mcp#managing-your-servers" }
liveness: snapshot
live-twin: "the live connection status changes underneath; /mcp re-reads it. No company stream"
emits: []
verification:
  list: {state: unverified, note: "no company face; native claude mcp list / /mcp are CLI+TUI, not contracted endpoints"}
```
Pending project-scoped servers appear as `⏸ Pending approval`; rejected as `✗ Rejected`. The reserved name `workspace` is skipped at load with a warning.
```contract:example
captured: synthetic            # status=planned -> synthetic legal AND loud (V11)
binding: cli
request: |
  claude mcp list
response: |
  github      http   https://api.githubcopilot.com/mcp/   ✓ connected (41 tools)
  airtable    stdio  npx -y airtable-mcp-server            ✓ connected (12 tools)
  paypal      http   https://mcp.paypal.com/mcp            ⏸ Pending approval
```
Adjacent: [[mcp-servers#op: mcp-servers.get]] (one server's detail), [[mcp-servers#op: mcp-servers.act]] (add/remove/auth), [[hooks]] (mcp_tool hooks call a connected server).

## op: mcp-servers.get
**`mcp-servers.get` is the PLANNED single-server detail read: transport, scope, full config, OAuth-configured flag, and connection state for one named server — the data behind `claude mcp get <name>`, not surfaced by the company.**
```contract:op
op: mcp-servers.get
resource: mcp-servers
kind: get
status: building
direction: outbound
atlas: [CC-11.1]
tasks:
  - phrase: "show the config for the github MCP server"
  - phrase: "is OAuth configured for this MCP server"
  - alias: "inspect an MCP server"
bindings:
  - { kind: mcp, tool: config_mcp_servers, op: "op='get'", server: company, exposure: "exposure.json#mcp.company", status: building, note: "BUILT (Capability Fabric ③): the MCP face runs `claude mcp get` via the R3 config_writer. The handler runtime/capability_handlers/config_authoring.py:mcp_servers backs both faces (DRY). live-verify pending (lead): a REAL .claude write / native claude-CLI round-trip." }
  - { kind: cli, command: "claude mcp get <name>", transport: claude-cli, exposure: "n/a — claude CLI", status: planned, note: "NATIVE: `claude mcp get <name>` — shows pending as ⏸ Pending approval, rejected as ✗ Rejected, and whether OAuth credentials are configured. https://code.claude.com/docs/en/mcp#managing-your-servers" }
liveness: snapshot
live-twin: "none — static between config edits + connection state changes"
emits: []
verification:
  get: {state: unverified, note: "no company face — planned"}
```
Adjacent: [[mcp-servers#op: mcp-servers.list]] (the roster), [[mcp-servers#op: mcp-servers.act]] (mutate).

## op: mcp-servers.act
**`mcp-servers.act` is the PLANNED MCP-server manager: add (any transport + scope), remove, add-from-JSON, import-from-Claude-Desktop, authenticate (OAuth via /mcp), and reset-project-choices — the writes the native model does via `claude mcp` subcommands, named here so a UI manager builds toward the real seam (a server-config writer + auth bridge the company has not built).**
```contract:op
op: mcp-servers.act
resource: mcp-servers
kind: act
status: building
direction: outbound
atlas: [CC-11.2, CC-11.3, CC-11.4]
tasks:
  - phrase: "add an http MCP server to my project"
    params: {act: add, transport: http, scope: project}
  - phrase: "connect a local stdio MCP server"
    params: {act: add, transport: stdio, scope: local}
  - phrase: "authenticate an MCP server with OAuth"
    params: {act: authenticate}
  - phrase: "remove an MCP server"
    params: {act: remove}
  - phrase: "import MCP servers from Claude Desktop"
    params: {act: import-desktop}
  - alias: "claude mcp add"
  - alias: "connect a tool to Claude"
  - alias: "log in to a remote MCP server"
caller: required
bindings:
  - { kind: mcp, tool: config_mcp_servers, op: "op='act' (add/add-json/remove/reset-project-choices)", server: company, exposure: "exposure.json#mcp.company", status: building, note: "BUILT (Capability Fabric ③): the MCP face runs `claude mcp …` (argv-array, exec-tier consent) via the R3 config_writer. The handler runtime/capability_handlers/config_authoring.py:mcp_servers backs both faces (DRY). live-verify pending (lead): a REAL .claude write / native claude-CLI round-trip." }
  - { kind: cli, command: "claude mcp add [--transport t] [--scope s] [--header H] [--env K=V] <name> <url | -- cmd args>", transport: claude-cli, exposure: "n/a — claude CLI", status: planned, note: "NATIVE writer: claude mcp add / add-json / add-from-claude-desktop / remove / reset-project-choices. Auth via /mcp (interactive). https://code.claude.com/docs/en/mcp#installing-mcp-servers" }
  - { kind: http, method: POST, path: "/mcp-servers  (Wire-phase-owned, pending — MCP face built)", transport: bridge-http, exposure: "exposure.json#bridge-http", status: planned, note: "GAP: BRIDGE_ROUTES (runtime/bridge.py:45) has zero MCP-server-management routes. A manager must write ~/.claude.json (local/user) or .mcp.json (project) AND drive the OAuth flow. The bridge arm is Wire-phase-owned (pending); the MCP face is live now." }
liveness: none
emits: []
consequences:
  - when: "server added (planned)"
    expect: []
    evidence: "[[mcp-servers#op: mcp-servers.list]] / `claude mcp get <name>` shows the new server; on next session start (or /mcp connect) its tools appear. No fabric event"
  - when: "remote server added requiring auth (planned)"
    expect: []
    evidence: "the server is flagged needs-auth in /mcp on 401/403; OAuth completes in the browser; status flips to connected — a runtime+browser flow, not a fabric event"
  - when: "project server added (planned)"
    expect: []
    evidence: "appears as ⏸ Pending approval until the operator approves in an interactive session; absence-shaped until approved (named read: mcp-servers.list)"
correlate: [session]
verification:
  add:          {state: unverified, note: "no settings-writer endpoint — planned"}
  remove:       {state: unverified, note: "no settings-writer endpoint — planned"}
  authenticate: {state: unverified, note: "no OAuth bridge — planned"}
```
### Description (purpose-free)
The native model's server-management writes, none yet bridged. ADD: `claude mcp add --transport http <name> <url>` (remote, recommended), `--transport sse` (deprecated), `--transport stdio <name> -- <cmd> [args]` (local; the `--` separates Claude's flags from the server command), or `add-json <name> '<json>'` (full config incl WebSocket `type:ws`). SCOPE via `--scope local|project|user` (local default). HEADERS via `--header`, env via `--env`. AUTHENTICATE remote servers: `/mcp` opens the browser OAuth flow (Claude Code flags a server needing auth on 401/403, or a WWW-Authenticate header). Fixed callback port `--callback-port`; pre-configured creds `--client-id`/`--client-secret`; scope-pinning via `oauth.scopes`. IMPORT: `claude mcp add-from-claude-desktop` (macOS/WSL). REMOVE: `claude mcp remove <name>`. RESET project approvals: `claude mcp reset-project-choices`. A company manager would render the config schema, validate transport+scope, write the right file, and drive auth. Until that bridge exists, `planned`.
### Request (PLANNED shape)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/mcp-servers.act.request",
  "type": "object",
  "required": ["act"],
  "properties": {
    "act":   { "enum": ["add", "add-json", "remove", "authenticate", "import-desktop", "reset-project-choices"] },
    "name":  { "type": "string", "description": "server name within its scope" },
    "scope": { "enum": ["local", "project", "user"], "default": "local" },
    "transport": { "enum": ["http", "sse", "stdio", "ws", "streamable-http"] },
    "config": { "$ref": "ui-contract/mcp-server.config" } },
  "additionalProperties": false }
```
### Interaction semantics
Native rules a manager MUST respect (sourced to the MCP reference):
- **Scope precedence (no merging):** when one server name is defined in multiple places, Claude Code uses the highest-precedence source ENTIRELY — local > project > user > plugin-provided > claude.ai connectors. Plugins/connectors match by ENDPOINT (URL/command), the three scopes match by NAME.
- **Project servers need approval.** `.mcp.json` servers prompt for per-operator approval before use; this is a security boundary, not a bug.
- **OAuth specifics:** flags apply to HTTP/SSE only (no effect on stdio). Tokens in keychain/credentials file, not config. `oauth.scopes` pins the requested scope subset; `offline_access` auto-appended if advertised. Re-auth on 403 insufficient_scope.
- **`headersHelper` runs arbitrary shell** — at project/local scope it only runs after workspace trust.
- **Env expansion in `.mcp.json`** (`${VAR}`, `${VAR:-default}`) lets teams share config; a missing required var with no default fails config parse.
### Errors
```contract:error
code: mcp-servers.unsupported-transport | http: 400 | retryable: false
when: transport not in {stdio, http, streamable-http, sse, ws} or a transport-flag mismatch (e.g. ws with --transport, which it doesn't accept)
teach: "Transports: http (recommended), sse (deprecated), stdio (local), ws (add-json only — no --transport, header auth only). See [[mcp-servers#Representation]]; source https://code.claude.com/docs/en/mcp."
```
```contract:error
code: mcp-servers.auth-required | http: 401 | retryable: true
when: a remote server returns 401/403 and needs OAuth (or a static Authorization header was rejected)
teach: "Run /mcp in an interactive session and complete the browser login. If you set headers.Authorization and it's rejected, Claude Code reports the connection failed instead of falling back to OAuth — fix the token or remove the header. Source https://code.claude.com/docs/en/mcp#authenticate-with-remote-mcp-servers."
```
```contract:error
code: mcp-servers.not-exposed | http: 501 | retryable: false
when: any call against mcp-servers.act today
teach: "MCP-server management is PLANNED — the company has no config-writer or auth bridge. Native path: `claude mcp add/remove/list/get` + `/mcp` for OAuth (https://code.claude.com/docs/en/mcp#managing-your-servers). The bridge gap is named in this op's bindings. (Note: the company's OWN MCP face is mcp_face/server.py — that is the company tool surface, NOT a session's manageable server set.)"
```
Adjacent: [[mcp-servers#op: mcp-servers.list]] (verify the add), [[mcp-servers#op: mcp-servers.get]] (inspect auth state), [[hooks]] (mcp_tool hooks need a connected server), [[extensions]] (plugins bundle MCP servers via .mcp.json/plugin.json — managed through plugin install, not /mcp).

## Errors
**Resource-level error vocabulary: `mcp-servers.unsupported-transport` (transport guard), `mcp-servers.auth-required` (the OAuth-needed signal), and `mcp-servers.not-exposed` (the honest 501 every write returns until the config-writer + auth bridge is built).** Each teaches the native recovery. No error claims an MCP-management capability the company does not have.

## Links
**No address-typed fields: an MCP server config references no fabric addresses.** Server NAMES are scope-local identifiers, not a fabric scheme; `command`/`url`/`headersHelper` are filesystem paths and URLs. None resolve to a corpus entry, by design. (The company's own MCP face is the company tool surface in TRANSPORTS.md, distinct from a managed server.)
