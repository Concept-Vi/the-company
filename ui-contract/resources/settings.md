---
type: contract-entry
resource: settings
summary: Claude Code's configuration data model — the settings.json key set, the scope hierarchy (managed > CLI flags > local > project > user) and merge rules, environment variables, and the /config editor; the company spawns every session with a FIXED minimal flag set and threads NO settings, so this resource contracts the native config model with the per-session config gap named, and surfaces the fabric's effective operating config (cap, timeout, permission, bind) as the one live read.
schemes: []
status: building
relates-to: ["[[fabric-config]]", "[[session]]", "[[permission]]", "[[model]]", "[[auth]]", "[[surfaces]]", "[[diagnostics]]"]
---

# Resource: settings

## Identity
**A settings configuration is identified by its SCOPE, not a fabric address — there is no
`settings://` scheme; a resolved configuration is the merge of up to five scope layers Claude Code
reads at session start, and the company exposes only the fabric's already-resolved operating slice
(via [[fabric-config]]), never a per-scope editor.** The scope set is a closed, ordered hierarchy
(source of truth https://code.claude.com/docs/en/settings.md): managed policy (highest) → CLI flags →
local (`.claude/settings.local.json`) → project (`.claude/settings.json`) → user
(`~/.claude/settings.json`) → built-in defaults (lowest). "Other configuration" (OAuth session,
user/local MCP servers, per-project trust/allowed-tools, caches) lives in `~/.claude.json`, NOT in a
settings.json. This resource contracts the model a UI renders to show or edit configuration; every
write lever is `planned` at the company layer because the supervisor spawn carries a fixed flag set
and threads no settings file (gap cited per op).

## Representation
**A resolved settings object is the deep-merge of the loaded scope layers — scalar values from the
higher-precedence scope win, arrays concatenate-and-dedupe (with `fallbackModel` the one exception:
the highest-precedence scope supplies the whole chain), and managed policy cannot be overridden by
any user/project/local key; the company's fabric session is spawned with NONE of these files
threaded, so its effective config is only the small operating slice [[fabric-config]] reads.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/settings.resolved",
  "type": "object",
  "description": "the consumer-relevant subset of the settings.json key space (NOT exhaustive — the full key list is in the docs; these are the keys a fabric/control UI most needs). Source: https://code.claude.com/docs/en/settings.md#available-settings",
  "properties": {
    "model":        { "type": "string", "description": "default model alias or full name — see [[model]]" },
    "effortLevel":  { "type": "string", "description": "default reasoning effort — see [[model#Representation]]" },
    "permissions":  { "type": "object",
                      "description": "defaultMode + allow/deny/ask/additionalDirectories — the rule surface owned by [[permission]]",
                      "properties": {
                        "defaultMode": { "type": "string" },
                        "allow": { "type": "array", "items": { "type": "string" } },
                        "deny":  { "type": "array", "items": { "type": "string" } },
                        "ask":   { "type": "array", "items": { "type": "string" } },
                        "additionalDirectories": { "type": "array", "items": { "type": "string" } } } },
    "env":          { "type": "object", "additionalProperties": { "type": "string" },
                      "description": "environment variables injected into every session/tool shell (e.g. CLAUDE_CODE_ENABLE_TELEMETRY) — see [[diagnostics]], [[platform]]" },
    "hooks":        { "type": "object", "description": "lifecycle event handlers (out of F8 scope — a hooks lane owns this)" },
    "enabledPlugins": { "type": "array", "items": { "type": "string" } },
    "mcpServers":   { "type": "object", "description": "MCP server configs (user/local copies live in ~/.claude.json, project in .mcp.json) — an MCP lane owns this" },
    "keybindings":  { "type": "object", "description": "custom shortcuts — the schema is in [[surfaces#op: surfaces.get-keybindings]]" },
    "apiKeyHelper": { "type": "string", "description": "credential script path — see [[auth#Representation]]" },
    "fallbackModel": { "type": "string", "description": "the one array-style key whose highest scope wins whole, not merged" },
    "companyAnnouncements": { "type": "array", "items": { "type": "string" },
                      "description": "admin banner lines, managed-settings-class — see [[platform#op: platform.enterprise]]" },
    "autoCompactEnabled": { "type": "boolean" },
    "outputStyle":  { "type": "string", "description": "terminal output styling (class CC-26, out of F8 scope)" } } }
```
| field | type | volatile? | changed-by | address? -> resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| the resolved object | object | yes (operator edits a settings.json + the session re-reads — see "When edits take effect" below) | NO company event — a settings file edit is a host filesystem change Claude Code re-reads; the fabric session is spawned without any settings file threaded | — | NOT threaded by the fabric. The supervisor spawn (`runtime/session_supervisor.py:259-265`) passes a FIXED flag set (`-p`, stream-json I/O, `--verbose`, `--permission-mode`, `--mcp-config`, `--strict-mcp-config`, `--allowedTools mcp__company`) and NO `--settings` — so spawned sessions inherit only the host's `~/.claude/settings.json` (the service account's), never a per-session config |
| permissions.defaultMode | string | n/a for fabric | pinned by `--permission-mode fabric_permission()` (`:263`) | -> [[permission]] | = `COMPANY_FABRIC_PERMISSION` (default `plan`); read via [[fabric-config#op: fabric-config.get]] `.permission` |
| model / effortLevel | string | n/a for fabric | NOT passed (no `--model`/`--effort`) | -> [[model]] | NOT SET by the fabric; the account default resolves — see [[model#Representation]] |
| the fabric operating slice (cap, turn_timeout_s, bind, permission) | object | yes | operator env (`COMPANY_FABRIC_*`) + service restart | -> [[fabric-config]] | LIVE-READABLE via `GET /health` — this is the one configuration a consumer can actually read from the company today (`:702-705`) |

**When edits take effect** (native rule a UI must respect, source settings.md#when-edits-take-effect):
most settings.json changes apply at the next session start, not mid-session; some (theme, keybindings)
hot-reload. For the fabric this is moot — sessions are headless `claude -p` with no settings file
threaded, so an edit to any settings.json is invisible to a running fabric session.

## State model
**State model: stateless.** A settings configuration has no lifecycle of its own — it is a resolved
read of files on disk, recomputed when a session (re)starts. The session it parameterises owns the
lifecycle ([[session#State model]]); a configuration is a launch-time input, not a stateful object.

## Caller
**Reading the fabric's effective operating config is anonymous-local via [[fabric-config]]; EDITING
any settings.json scope is an operator act on the host filesystem (deliberately not a company op),
and when a per-session config surface lands the setter is whoever spawns the session, carrying
selected keys as spawn params — never an ambient default.** No company consumer can today change
another session's configuration; the only company-visible config knobs are the fabric env vars
(`COMPANY_FABRIC_PERMISSION`, `COMPANY_FABRIC_CONCURRENCY`, the turn timeout) flipped by the operator
+ a restart, exactly the B3-class discipline as the bind in [[fabric-config#Caller]].

## Operations

## op: settings.get
**`settings.get` is the resolved-config read: the effective configuration a session is running
under — at the company layer this resolves ONLY to the fabric's operating slice (cap, timeout,
permission, bind) via the supervisor health read, because the full per-scope settings.json contents
are never threaded into a fabric session and have no company endpoint.**
```contract:op
op: settings.get
resource: settings
kind: get
status: building
direction: outbound
atlas: [CC-25.1]
tasks:
  - phrase: "read the fabric's live operating configuration"
  - phrase: "what concurrency cap and turn timeout is the fabric running under"
  - phrase: "what configuration does a spawned session inherit"
  - alias: "show settings"
  - alias: "current config"
  - alias: "fabric config"
bindings:
  - { kind: http, method: GET, path: /health, transport: supervisor-http, exposure: "exposure.json#supervisor-http", note: "the SAME read as [[fabric-config#op: fabric-config.get]] and [[permission#op: permission.get]] — three retrieval lenses, one wire read. Returns cap, turn_timeout_s, permission, bind; NOT the host settings.json contents" }
  - { kind: cli, command: "company status   (the session-supervisor row reflects the operating slice; the full read rides the health endpoint)", transport: cli-local, exposure: "exposure.json#cli-local" }
liveness: snapshot
live-twin: "none — static between operator COMPANY_FABRIC_* env changes + service restart"
emits: []
verification:
  fabric-slice-read: {state: probe-verified, run: "session_supervisor_acceptance (health asserts cap/turn_timeout_s/permission/bind)", date: 2026-06-12, note: "this op is the settings/config lens on the SAME GET /health field set [[fabric-config]] proves; the host settings.json contents are NOT exposed and that gap is named below"}
```
This op deliberately overlaps [[fabric-config#op: fabric-config.get]] and [[permission#op:
permission.get]] — same `GET /health` wire read, three retrieval lenses (a consumer asking
"settings" finds it here, "fabric config" there, "permission posture" in [[permission]]). The FULL
settings.json key space (the [[settings#Representation]] schema) is NOT readable through any company
endpoint: the fabric threads no settings file, and there is no native "dump resolved settings" API —
the interactive `/status` "Setting sources" line and the `/config` editor are human-only surfaces
(declared in [[surfaces]], not company routes). A consumer needing a key the fabric does not surface
reads the static defaults documented at https://code.claude.com/docs/en/settings.md.
```contract:example
captured: synthetic            # status=building — replaced by captured evidence at flip-to-live (V11)
binding: http
request: |
  GET /health HTTP/1.1
response: |
  HTTP/1.1 200 OK
  {"ok": true, "service": "session-supervisor", "bind": "127.0.0.1",
   "sessions": {"total": 1, "by_state": {"idle": 1}},
   "cap": 3, "turn_timeout_s": 900.0, "permission": "plan"}
```
Adjacent: [[fabric-config#op: fabric-config.get]] (same read, fabric lens), [[permission#op:
permission.get]] (same read, posture lens), [[settings#op: settings.act]] (the planned per-session
config setter), [[surfaces#op: surfaces.get-keybindings]] (keybindings, a settings sibling).

## op: settings.act
**`settings.act` is the PLANNED per-session configuration steer: thread a chosen settings file or
inline JSON, env vars, and additional directories into a session at spawn — the native `--settings`,
`--add-dir`, and `env`-key levers the company spawn does NOT yet carry, named here so a UI builds the
real seam instead of a fiction.**
```contract:op
op: settings.act
resource: settings
kind: act
status: planned
direction: outbound
atlas: [CC-25.2, CC-25.3]
tasks:
  - phrase: "spawn a session with a specific settings file"
    params: {act: set-at-spawn, settings: "<path-or-json>"}
  - phrase: "give a session access to extra directories"
    params: {act: add-dirs}
  - phrase: "set an environment variable for a session"
    params: {act: set-env}
  - alias: "load custom settings"
  - alias: "configure a session"
  - alias: "grant additional directory access"
bindings:
  - { kind: http, method: POST, path: "/spawn  (PLANNED extension: a settings/env/add_dirs block on the body)", transport: supervisor-http, exposure: "exposure.json#supervisor-http", status: planned, note: "GAP: spawn() (runtime/session_supervisor.py:254) accepts cwd/resume/fork/name/source ONLY — NO --settings, --add-dir, or env override. Every spawn inherits the SERVICE ACCOUNT's ~/.claude/settings.json. Wiring = a settings block -> --settings <json>, an add_dirs array -> repeated --add-dir, an env map -> per-process environment. The native flags are documented at https://code.claude.com/docs/en/cli-reference.md" }
liveness: none
emits: []
consequences:
  - when: "settings/env/dirs set at spawn (planned)"
    expect: [agent_sessions.spawned]
    bound: "the spawn's own bound ([[session#op: session.create]]); applied config is observable only via the session's behaviour (e.g. the resolved tool surface on system/init, or a tool reaching an added directory) — NOT a distinct fabric event"
    evidence: "[[diagnostics#op: diagnostics.watch]] system/init for the resolved tool surface; for added directories, the named read is the next tool call succeeding against a path outside cwd on [[session#op: session.watch]] — an absence-of-dedicated-event outcome (CONTRACT-FORMAT section 6 V9)"
correlate: [session]
verification:
  settings-at-spawn: {state: unverified, note: "the spawn param does not exist — planned"}
  add-dirs-at-spawn: {state: unverified, note: "no --add-dir threaded — planned"}
  env-at-spawn:      {state: unverified, note: "no per-session env override — planned"}
```
### Description (purpose-free)
Three planned spawn-time configuration levers the native CLI supports and the company does not yet
thread. (1) `--settings <file-or-json>` loads a settings object that merges into the scope hierarchy
at the CLI-flags layer (above local/project/user, below managed policy). (2) `--add-dir
<directories>` (repeatable) grants tool access to directories outside the session cwd — the
`additionalDirectories` permission key as a flag. (3) per-session environment variables (the `env`
settings key, or the spawning process's environment) parameterise tools and telemetry. All three ride
parameters the supervisor's `spawn()` could carry; none is wired today, so this op is `planned`, its
examples synthetic-and-loud, its verification rows honestly unverified. Source:
https://code.claude.com/docs/en/cli-reference.md, https://code.claude.com/docs/en/settings.md.
### Request (PLANNED shape — the contract the seam should fulfil)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/settings.act.request",
  "type": "object",
  "required": ["session", "act"],
  "properties": {
    "session":  { "type": "string", "description": "session://<id> being spawned" },
    "act":      { "enum": ["set-at-spawn", "add-dirs", "set-env"] },
    "settings": { "type": ["object", "string"], "description": "an inline settings object or a path; merges at the CLI-flags scope layer" },
    "add_dirs": { "type": "array", "items": { "type": "string" }, "description": "extra directories the session's tools may read/write" },
    "env":      { "type": "object", "additionalProperties": { "type": "string" } } },
  "additionalProperties": false }
```
### Interaction semantics
Native rules a consumer respects when this lands (sourced to settings.md):
- **Scope precedence is fixed.** A `--settings` object sits at the CLI-flags layer: it overrides
  local/project/user but is itself overridden by managed policy. A UI cannot promise a `--settings`
  value will win if a managed-settings policy pins the same key.
- **Arrays merge, scalars override** across scopes; `fallbackModel` is the one whole-chain exception.
- **`additionalDirectories` is a permission widening** — it interacts with [[permission]]'s rule
  surface; an `--add-dir` does not bypass `deny` rules.
- **Managed policy is unoverridable** and may itself disable the very keys a consumer tries to set
  (e.g. an org can forbid custom MCP servers) — see [[platform#op: platform.enterprise]].
### Errors
```contract:error
code: settings.invalid-json | http: 400 | retryable: false
when: a `--settings` inline object or file fails JSON parse / schema validation
teach: "Settings must be valid JSON matching the settings.json schema (https://json.schemastore.org/claude-code-settings.json). On the host, Claude Code shows a setup-issues notice and [[diagnostics#op: diagnostics.act]] (/doctor) lists the offending file. The fabric pre-validates before threading."
```
```contract:error
code: settings.not-exposed | http: 501 | retryable: false
when: any per-session settings/env/dir call against the fabric today
teach: "Per-session configuration is PLANNED — the fabric spawns with a fixed flag set and threads no --settings/--add-dir/env. To change configuration today, an operator edits the service account's ~/.claude/settings.json (or the COMPANY_FABRIC_* env) and restarts the service; READ the live operating slice via [[settings#op: settings.get]]. The spawn-param gap is named in this op's bindings."
```
```contract:example
captured: synthetic            # status=planned -> synthetic legal AND loud; no spawn settings param exists (V11)
binding: http
request: |
  POST /spawn HTTP/1.1   (PLANNED body extension)
  {"cwd": "/home/tim/scratch", "name": "wide-1",
   "add_dirs": ["/home/tim/shared"], "env": {"CLAUDE_CODE_ENABLE_TELEMETRY": "1"}}
response: |
  HTTP/1.1 501 Not Implemented
  {"error": "Per-session configuration is planned; the fabric spawns with a fixed flag set (no --settings/--add-dir/env). Edit the service account ~/.claude/settings.json or COMPANY_FABRIC_* env and restart to change config globally; read the live operating slice via GET /health."}
```
Adjacent: [[settings#op: settings.get]] (the live read that DOES work), [[session#op: session.create]]
(the spawn this would extend), [[permission#op: permission.act]] (the rule-surface sibling lever),
[[platform#op: platform.enterprise]] (managed policy, which outranks any of these).

## Errors
**Resource-level error vocabulary: `settings.invalid-json` (the parse/validation guard, the same
condition `/doctor` reports on the host) and `settings.not-exposed` (the honest 501 every per-session
config setter returns until the spawn-param seam is built).** Both teach the in-corpus recovery — read
the live operating slice, or have the operator edit the service settings/env + restart. No error
asserts a configuration capability the supervisor lacks.

## Links
**No address-typed fields: a settings configuration references the `session://` it parameterises
(dereferences to [[session]]) and points at sibling resources that own slices of the config model —
[[permission]] (the rule surface), [[model]] (model/effort keys), [[auth]] (apiKeyHelper), [[surfaces]]
(keybindings), [[diagnostics]] (env/telemetry keys), [[platform]] (managed policy).** Settings KEYS
(model, env, hooks, …) and scope file paths are Claude Code identifiers
(https://code.claude.com/docs/en/settings.md), not fabric addresses — they never resolve to a corpus
entry, by design.
