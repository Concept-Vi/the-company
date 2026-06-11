---
type: contract-entry
resource: platform
summary: The host-and-org layer Claude Code runs within — installation/updates/platform support, enterprise admin (managed policy), cloud-provider routing (Bedrock/Vertex/Foundry), large-codebase setup, data privacy/security, and the glossary; nearly all of this governs the HOST install and the Anthropic ORG, not the fabric, so this resource maps each class to its native model and marks it building/planned/out-of-local-scope WITH a reason — the company drives one installed claude binary and never administers the org.
schemes: []
status: planned
relates-to: ["[[auth]]", "[[settings]]", "[[diagnostics]]", "[[surfaces]]", "[[session]]", "[[cost-usage]]", "[[knowledge-corpus]]"]
---

# Resource: platform

## Identity
**A platform concern is identified by its CLASS (install/update, enterprise admin, cloud provider,
large-codebase setup, privacy/security, glossary), not a fabric address — there is no `platform://`
scheme; every one of these governs the HOST machine Claude Code is installed on or the Anthropic
ORGANIZATION the account belongs to, NOT the company fabric, which simply drives one already-installed
`claude` binary as a subprocess.** This resource is the honest map of Feature-Atlas classes CC-28/29/
31/32/34/35: each is grounded in its native doc and marked `building` (a real company read exists),
`planned` (a company endpoint is namable but unbuilt), or — for most — declared out-of-LOCAL-scope
with a reason and routed to OUT-OF-SCOPE.md / INVENTORY-EXCLUSIONS.md, because administering an org or
installing software is not something the fabric does or should do. No silent gaps (audit N5/C8).

## Representation
**A platform concern's shape is its native data model (install method, managed-policy object,
provider env set, retention posture, term definition); the company holds NO platform object of its own
— the only platform fact it surfaces is the version/binary it drives and the operating env it was
started with.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/platform.fact",
  "type": "object",
  "description": "the small slice of platform reality the company can actually see — the rest is host/org native models documented per op",
  "properties": {
    "claude_version": { "type": "string", "description": "the version of the claude binary the supervisor spawns; readable on a session's system/init, NOT a company field today" },
    "claude_bin":     { "type": "string", "description": "the resolved binary path (env-overridable for the stub harness) — `_panel._find_claude()`, runtime/session_supervisor.py:259" },
    "fabric_env":     { "type": "object",
      "description": "the COMPANY_FABRIC_* operating env the service was started with — the company's only self-administered config (cap/permission/timeout)",
      "properties": {
        "COMPANY_FABRIC_CONCURRENCY": { "type": "integer" },
        "COMPANY_FABRIC_PERMISSION":  { "type": "string" } } } },
  "additionalProperties": false }
```
| class | native model | company relationship | reality (2026-06-12) |
|---|---|---|---|
| CC-34 install/update | `curl …/install.sh`, homebrew, winget, npm, apt/dnf/apk; background auto-update on native installs; `claude install [version]`, `claude update`, `claude doctor` | HOST-only | OUT-OF-LOCAL-SCOPE. The company drives an already-installed binary (`_find_claude()`); it never installs/updates Claude Code. The version is observable on a session's system/init only |
| CC-28 enterprise/admin | managed-settings (server/MDM/file), `managed-settings.json`, drop-in `managed-settings.d/`, admin console, usage analytics, managed MCP | ORG-only | OUT-OF-LOCAL-SCOPE. Managed policy is delivered by an org admin and OUTRANKS every settings scope (see [[settings#Caller]]); the company is a policy SUBJECT, not an administrator |
| CC-29 cloud providers | `CLAUDE_CODE_USE_BEDROCK`/`_VERTEX`/`_FOUNDRY` + provider creds; highest auth precedence | HOST env | OUT-OF-LOCAL-SCOPE as a company op, but INHERITED: if the service account's env sets a provider, the fabric's sessions route there transparently. Provider selection is a host/[[auth]] concern |
| CC-31 large-codebase | nested CLAUDE.md, sparse worktrees, code intelligence (LSP), per-package skills, dev containers | HOST/project | OUT-OF-LOCAL-SCOPE. These configure how a human's `claude` works in a big repo; the fabric spawns with an explicit `cwd` and inherits the project's CLAUDE.md, but owns none of these setup levers (LSP/code-intel is class CC-16, a separate lane) |
| CC-32 privacy/security | data-usage policy, telemetry (no code/paths), retention, provider-default behaviors, credential storage | ORG/policy | OUT-OF-LOCAL-SCOPE as a company op + a STATED BOUNDARY: the company stores no Anthropic credential and proxies no inference; what the supervisor persists locally is named below |
| CC-35 glossary | the canonical Claude Code term list | reference | BUILDING via the knowledge corpus — a glossary lookup is a [[knowledge-corpus]] search (domain=claude-code-atlas), the one platform class with a real company read |

## State model
**State model: stateless.** A platform concern is a host/org configuration or a reference fact, not a
stateful company object. The supervisor has an up/down liveness ([[diagnostics]]) and sessions have
lifecycles ([[session#State model]]); platform concerns parameterise the environment those run in, with
no machine of their own.

## Caller
**The company administers NONE of these: install/update is the host operator at the machine; managed
policy is the org admin in the Claude admin console; cloud-provider and privacy posture are set by the
service account's environment and the org's data agreements; the glossary is anonymous reference.**
The company's only self-administered platform surface is the `COMPANY_FABRIC_*` env it is started with
(operator-set + restart, the B3-class discipline) and the binary it resolves to spawn. There is no
company op that installs software, edits managed policy, switches a cloud provider, or changes a
retention setting.

## Operations

## op: platform.glossary
**`platform.glossary` is the term-lookup read: a Claude Code term or best-practice resolved from the
embedded docs mirror — the ONE platform class with a real, proven company read, realized as a knowledge
corpus search over the claude-code-atlas vault.**
```contract:op
op: platform.glossary
resource: platform
kind: search
status: building
direction: outbound
atlas: [CC-35.1]
tasks:
  - phrase: "what does a Claude Code term mean"
  - phrase: "look up agent teams / compaction / permission mode in the glossary"
  - phrase: "Claude Code best practice for X"
  - alias: "define a Claude Code term"
  - alias: "glossary lookup"
  - alias: "what is X in Claude Code"
bindings:
  - { kind: mcp, tool: knowledge_search, server: substrate-mcp, exposure: "n/a — process-local (external MCP)", note: "REUSES the F6 knowledge-corpus search face — a glossary lookup is search_semantic over vault=claude-code-atlas (the docs mirror includes glossary.md). This is NOT a company-owned face; it is the external substrate-mcp server, inventoried in INVENTORY-EXCLUSIONS.md. See [[knowledge-corpus#op: knowledge-corpus.search]] for the real op; this is the platform/glossary lens on it" }
liveness: snapshot
live-twin: "none — the docs mirror is a static reference corpus, re-fetched/re-indexed out of band"
emits: []
verification:
  glossary-search: {state: probe-verified, run: "substrate search over claude-code-atlas (glossary.md chunks returned live)", date: 2026-06-12, note: "the same proven-by-use F6 search face [[knowledge-corpus]] cites; verified 2026-06-12. Platform/glossary is a retrieval LENS, not a new endpoint"}
```
This op deliberately overlaps [[knowledge-corpus#op: knowledge-corpus.search]] — a glossary lookup IS a
semantic search over the claude-code-atlas vault, whose docs mirror carries `glossary.md` (terms like
agent-teams, compaction, permission-mode, settings-layers, project-trust). A consumer asking "what does
X mean in Claude Code" finds it here; one asking "search the knowledge corpus" finds it there; both
resolve to the same substrate search. The canonical op, its real binding, and its honest field-reality
live in [[knowledge-corpus]]; this section is the platform-class entry point so CC-35 is reachable from
navigation, never a silent gap.
```contract:example
captured: synthetic            # status=building — replaced by captured evidence at flip-to-live (V11)
binding: mcp
request: knowledge_search(query="permission mode meaning", vault="claude-code-atlas")
response: { "results": [ { "address": "filesystem://claude-code-atlas/Docs/claude-code/glossary.md#permission-mode",
            "text": "A named approval posture (default/acceptEdits/plan/dontAsk/bypassPermissions/auto) that governs how tool calls are gated…" } ] }
```
Adjacent: [[knowledge-corpus#op: knowledge-corpus.search]] (the canonical search op), [[permission]] /
[[model]] / [[settings]] (the resources whose terms a glossary lookup explains), [[platform#op:
platform.cloud-provider]] (a sibling platform class).

## op: platform.install
**`platform.install` is the install/update class — OUT-OF-LOCAL-SCOPE: managing the Claude Code binary
(install method, version, auto-update) is a HOST operator concern; the company drives an already-present
binary and never installs or updates it, so this op exists only to make CC-34 reachable from navigation
and route it honestly to its native path.**
```contract:op
op: platform.install
resource: platform
kind: act
status: planned
direction: outbound
atlas: [CC-34.1]
tasks:
  - phrase: "how is Claude Code installed and updated"
  - phrase: "what platforms does Claude Code support"
  - phrase: "what version of claude is the fabric running"
    params: {note: "observable on a session system/init, not a company field"}
  - alias: "install claude code"
  - alias: "update claude code"
  - alias: "claude version"
bindings:
  - { kind: cli, command: "claude install [version] / claude update / claude doctor   (HOST commands; NOT company routes)", transport: cli-local, exposure: "n/a — Claude Code built-in", status: planned, note: "SCOPE: the company drives the binary at `_find_claude()` (runtime/session_supervisor.py:259, env-overridable) but never installs/updates it. Native installs auto-update in the background; homebrew/winget/npm need manual upgrade. Listed planned-and-routed so CC-34 is navigable; the actual install/update path is the host operator's" }
liveness: none
emits: []
verification:
  install-update: {state: unverified, note: "host operator concern; no company op by design — planned/out-of-local-scope"}
```
The install/update model (source https://code.claude.com/docs/en/setup.md, quickstart.md): native
installer (`curl -fsSL https://claude.ai/install.sh | bash`, or the Windows `.ps1`/`.cmd`) auto-updates
in the background; Homebrew (`claude-code` stable vs `claude-code@latest`), WinGet, and npm
(`@anthropic-ai/claude-code`, Node 18+) do NOT auto-update (manual `brew upgrade`/`winget upgrade`);
Linux package managers (apt/dnf/apk) are supported. `claude install [version]` installs a native build
(stable/latest/specific); `claude update`/`claude upgrade` check and install; `claude doctor` reports
updater health (see [[diagnostics]]). Platforms: macOS, Windows (PowerShell/CMD, Git-for-Windows
recommended for Bash), Linux, WSL. None of this is a company capability — the company spawns whatever
`claude` the host resolved.
```contract:example
captured: synthetic            # status=planned/out-of-local-scope -> synthetic legal AND loud (V11)
binding: cli
request: |
  # HOST terminal (not a company route):
  claude update
response: |
  # checks + installs in the background; the company has no equivalent op.
  # The driven binary's version surfaces on a fabric session's system/init.
```
Adjacent: [[diagnostics#op: diagnostics.act]] (claude doctor reports updater health), [[surfaces#op:
surfaces.list]] (the CLI subcommands), [[platform#op: platform.enterprise]] (org-managed version pins).

## op: platform.enterprise
**`platform.enterprise` is the enterprise-admin class — OUT-OF-LOCAL-SCOPE: managed policy, org
analytics, and managed MCP are delivered by an ORG ADMIN and the company is a policy SUBJECT, not an
administrator; this op makes CC-28 navigable and names the one way org policy reaches the fabric
(it inherits managed settings, unoverridably).**
```contract:op
op: platform.enterprise
resource: platform
kind: act
status: planned
direction: outbound
atlas: [CC-28.1]
tasks:
  - phrase: "how do organizations centrally configure Claude Code"
  - phrase: "what are managed settings and do they override the fabric"
  - phrase: "enterprise admin controls"
  - alias: "managed policy"
  - alias: "org settings"
  - alias: "admin console"
bindings:
  - { kind: http, method: GET, path: "(none — org admin console / MDM / managed-settings.json on the host)", transport: supervisor-http, exposure: "n/a — org/admin surface", status: planned, note: "SCOPE: managed settings are delivered server-side (Claude admin console), via MDM (macOS plist / Windows registry HKLM/HKCU), or file-based (/etc/claude-code/managed-settings.json on Linux/WSL, + managed-settings.d/ drop-ins). They OUTRANK all other scopes and cannot be overridden. The fabric INHERITS whatever the host has; the company administers none of it" }
liveness: none
emits: []
verification:
  managed-policy: {state: unverified, note: "org admin concern; no company op by design — planned/out-of-local-scope"}
```
The enterprise model (source https://code.claude.com/docs/en/admin-setup.md, server-managed-settings.md,
managed-mcp.md): managed settings use the same JSON format as settings.json but cannot be overridden by
user/project/local scopes (top of the precedence chain — see [[settings#Identity]]); delivery is
server-managed (admin console), MDM/OS-policy (macOS `com.anthropic.claudecode` plist; Windows
`HKLM\SOFTWARE\Policies\ClaudeCode`), or file-based (`/etc/claude-code/managed-settings.json` +
`managed-settings.d/` systemd-style drop-ins merged in numeric order). Admins can restrict MCP
(`managed-mcp.json`), plugin marketplaces (`strictKnownMarketplaces`), and set `companyAnnouncements`.
The fabric is subject to all of it through the host install; the company never edits it.
```contract:example
captured: synthetic            # status=planned/out-of-local-scope -> synthetic legal AND loud (V11)
binding: http
request: |
  # there is no company route — managed policy lives on the host/org:
  #   /etc/claude-code/managed-settings.json  (file-based, Linux/WSL)
response: |
  # the fabric inherits managed policy unoverridably; the company administers none of it.
```
Adjacent: [[settings#Identity]] (the scope hierarchy managed policy tops), [[settings#op: settings.act]]
(per-session config, which managed policy outranks), [[platform#op: platform.privacy]] (org data
posture), [[cost-usage]] (org usage analytics).

## op: platform.cloud-provider
**`platform.cloud-provider` is the cloud-routing class — OUT-OF-LOCAL-SCOPE as a company op but
INHERITED: if the service account's env sets `CLAUDE_CODE_USE_BEDROCK`/`_VERTEX`/`_FOUNDRY`, the
fabric's headless sessions route inference through that provider transparently; the company neither
selects nor switches the provider.**
```contract:op
op: platform.cloud-provider
resource: platform
kind: act
status: planned
direction: outbound
atlas: [CC-29.1]
tasks:
  - phrase: "can the fabric route through Bedrock or Vertex"
  - phrase: "how does Claude Code use a cloud provider for inference"
  - phrase: "keep inference on our own cloud"
  - alias: "Bedrock"
  - alias: "Vertex AI"
  - alias: "Microsoft Foundry"
bindings:
  - { kind: http, method: POST, path: "(none — host env CLAUDE_CODE_USE_BEDROCK/_VERTEX/_FOUNDRY + provider creds)", transport: supervisor-http, exposure: "n/a — host env / external provider", status: planned, note: "SCOPE: provider selection is the HIGHEST auth-precedence method (see [[auth#Identity]]). It is set by the service account's environment + provider credentials (AWS/GCP/Azure), not a company op. The fabric INHERITS it: a provider-configured host means provider-routed sessions, transparently. The provider endpoints themselves are EXTERNAL (Anthropic/AWS/GCP/Azure), inventoried in INVENTORY-EXCLUSIONS.md, never company routes" }
liveness: none
emits: []
verification:
  provider-routing: {state: unverified, note: "host env concern; no company op — planned/out-of-local-scope. Provider-inherited routing is UNVERIFIED end-to-end (no provider configured on this host)"}
```
The provider model (source https://code.claude.com/docs/en/authentication.md#cloud-provider-authentication,
third-party-integrations): set `CLAUDE_CODE_USE_BEDROCK=1` (+ AWS creds), `CLAUDE_CODE_USE_VERTEX=1`
(+ GCP creds), or `CLAUDE_CODE_USE_FOUNDRY=1` (+ Azure creds) in the environment before running
`claude` — no browser login needed; this is the top of the credential precedence chain ([[auth]]).
Organizations use it to keep inference on their own cloud. The company does not set or switch it; a
fabric session simply uses whatever the service account's env resolves. The provider APIs are external,
not proxied by the company.
```contract:example
captured: synthetic            # status=planned/out-of-local-scope -> synthetic legal AND loud (V11)
binding: http
request: |
  # HOST env (set before the supervisor starts; not a company route):
  export CLAUDE_CODE_USE_VERTEX=1
response: |
  # fabric sessions then route inference through Vertex transparently; the company selects nothing.
```
Adjacent: [[auth#Identity]] (provider creds = highest precedence), [[auth#op: auth.act]] (the credential
class), [[platform#op: platform.privacy]] (provider-default data behaviors differ), [[model]] (which
models a provider exposes).

## op: platform.privacy
**`platform.privacy` is the privacy/security/large-codebase class — OUT-OF-LOCAL-SCOPE as a company op
AND a stated BOUNDARY: data retention, telemetry, and provider-default behaviors are org/policy
concerns the company does not administer; what the company DOES persist locally is named here for
honesty, so the data boundary is explicit, never silent.**
```contract:op
op: platform.privacy
resource: platform
kind: get
status: planned
direction: outbound
atlas: [CC-32.1, CC-31.1]
tasks:
  - phrase: "what data does Claude Code collect"
  - phrase: "data retention and telemetry posture"
  - phrase: "what does the company store locally"
  - phrase: "set up a large codebase or monorepo"
  - alias: "data privacy"
  - alias: "zero data retention"
  - alias: "monorepo setup"
bindings:
  - { kind: http, method: GET, path: "(none — org data agreement + host telemetry config)", transport: supervisor-http, exposure: "n/a — org/policy + host", status: planned, note: "SCOPE + BOUNDARY: data-usage/retention is governed by the Anthropic data policy and the org's agreement, configured (telemetry) by the host's env (CLAUDE_CODE_ENABLE_TELEMETRY + OTel exporters) — not a company op. The company's OWN local persistence is stated in the prose below so the boundary is explicit" }
liveness: none
emits: []
verification:
  privacy-posture: {state: unverified, note: "org/policy + host concern; no company op — planned/out-of-local-scope. The company-local persistence claim below is code-grounded, not a privacy API"}
```
### Description (purpose-free)
Two adjacent host/org classes, neither a company op. PRIVACY/SECURITY (CC-32): Claude Code logs
operational metrics (latency, reliability, usage) that exclude code and file paths; data-retention and
training behaviors differ by API provider (Claude API vs Bedrock vs Vertex — see data-usage.md) and by
the org's agreement (zero-data-retention is an org/contract option); OTel telemetry is opt-in per host
(`CLAUDE_CODE_ENABLE_TELEMETRY=1` + exporters, see [[diagnostics]], monitoring-usage.md). Credentials
are stored in the OS keychain (macOS) or `~/.claude/.credentials.json` mode 0600 (Linux) — see [[auth]].
The COMPANY'S OWN data boundary (stated for honesty): the supervisor persists session records and mail
to its local store (`fcfg.STORE_DIR`, the `agent_sessions` jsonl), binds 127.0.0.1 only, stores NO
Anthropic credential, and proxies NO inference. LARGE-CODEBASE (CC-31): nested CLAUDE.md, sparse
worktrees, code intelligence (LSP, class CC-16), per-package skills, and dev containers configure how a
human's `claude` works in a big repo (large-codebases.md); the fabric spawns with an explicit `cwd` and
inherits the project's CLAUDE.md but owns none of these setup levers. Source:
https://code.claude.com/docs/en/data-usage.md, large-codebases.md, legal-and-compliance.md.
### Errors
```contract:error
code: platform.out-of-local-scope | http: 501 | retryable: false
when: any install / enterprise-admin / cloud-provider-switch / privacy-config call against the company
teach: "This is a HOST or ORG concern, not a company capability — the fabric drives one installed binary and never installs software, edits managed policy, switches providers, or sets retention. The recovery is the native path: claude install/update (host), the admin console / managed-settings.json (org), CLAUDE_CODE_USE_* env (host), the org data agreement. The company's own local persistence is stated in [[platform#op: platform.privacy]]. The one BUILT platform read is the glossary via [[knowledge-corpus]]."
```
```contract:example
captured: synthetic            # status=planned/out-of-local-scope -> synthetic legal AND loud (V11)
binding: http
request: |
  # there is no company route — privacy/retention is org policy + host telemetry config:
  #   CLAUDE_CODE_ENABLE_TELEMETRY=1   (host opt-in)
response: |
  # the company stores session records + mail locally (STORE_DIR), binds 127.0.0.1, stores no credential, proxies no inference.
```
Adjacent: [[auth]] (credential storage), [[diagnostics]] (telemetry/OTel), [[settings]] (the env key
surface), [[knowledge-corpus]] (the one built platform read — glossary/docs), [[session]] (the local
records the company does persist).

## Errors
**Resource-level error vocabulary: `platform.out-of-local-scope` (the honest 501 every install /
enterprise-admin / cloud-provider / privacy-config call returns — these govern the host and org, not
the fabric, by design not omission).** It teaches the native recovery path per class and points at the
ONE built platform read (the glossary via [[knowledge-corpus]]). No error implies the company can
install software, administer the org, or change a data posture.

## Links
**No address-typed fields: platform concerns reference the `session://` they parameterise (dereferences
to [[session]]) and point at the resources that own their adjacent slices — [[auth]] (cloud-provider
creds + storage), [[settings]] (managed policy + env keys), [[diagnostics]] (telemetry + install
health), [[surfaces]] (the install/update CLI subcommands), [[knowledge-corpus]] (the glossary/docs
search), [[cost-usage]] (org usage analytics).** Install methods, provider env-var names, managed-policy
paths, retention terms, and glossary terms are Claude Code/Anthropic identifiers
(https://code.claude.com/docs/en/setup.md, admin-setup.md, authentication.md, data-usage.md,
glossary.md), not fabric addresses — they never resolve to a corpus entry, by design.
