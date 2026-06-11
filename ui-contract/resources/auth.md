---
type: contract-entry
resource: auth
summary: How a Claude Code session authenticates with Anthropic — the credential precedence chain (cloud-provider > AUTH_TOKEN > API_KEY > apiKeyHelper > OAuth token > subscription login), where credentials are stored, /login /logout and claude setup-token; the company inherits the service account's host credentials and threads NO per-session auth, so this resource contracts the native auth model with the per-session-identity gap named and surfaces nothing secret.
schemes: []
status: building
relates-to: ["[[settings]]", "[[session]]", "[[platform]]", "[[cost-usage]]", "[[diagnostics]]"]
---

# Resource: auth

## Identity
**An authentication state is identified by the HOST ACCOUNT/credential it resolves to, not a fabric
address — there is no `auth://` scheme; a session's auth is whichever credential Claude Code selects
from a closed precedence chain at startup, and the company NEVER threads or exposes a credential — a
spawned fabric session simply inherits the service account's host login.** The credential precedence
order (source of truth https://code.claude.com/docs/en/authentication.md#authentication-precedence,
highest first): (1) cloud-provider credentials when `CLAUDE_CODE_USE_BEDROCK`/`_VERTEX`/`_FOUNDRY` is
set — see [[platform#op: platform.cloud-provider]]; (2) `ANTHROPIC_AUTH_TOKEN` (Bearer, for LLM
gateways); (3) `ANTHROPIC_API_KEY` (X-Api-Key, Console direct); (4) `apiKeyHelper` script output;
(5) `CLAUDE_CODE_OAUTH_TOKEN` (long-lived, from `claude setup-token`, CI use); (6) subscription OAuth
from `/login` (the default for Pro/Max/Team/Enterprise). This resource contracts the model a UI
renders to show WHICH method is active and HOW to switch — the redacted status READ and the operator's
own credential ACTS (relogin/logout/setup-token) are `building` company ops (Tim's sole-operator
reopening, consent-gated); proxying a DIFFERENT user's credential stays out of scope (usage policy).

## Representation
**An authentication state is the tuple (active method, account/subscription identity, storage
location) that Claude Code resolves once per session start; the company surfaces NONE of it — secrets
are never read, and a fabric session's identity is exactly the service account that runs the
supervisor.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/auth.state",
  "type": "object",
  "description": "the NON-SECRET shape a UI would render to show auth status (never the credential itself). Source: https://code.claude.com/docs/en/authentication.md",
  "properties": {
    "method": { "enum": ["cloud-provider", "auth-token", "api-key", "api-key-helper", "oauth-token", "subscription-oauth"],
                "description": "which precedence-chain entry resolved" },
    "account_kind": { "enum": ["pro", "max", "team", "enterprise", "console", "bedrock", "vertex", "foundry", "unknown"],
                "description": "subscription/plan or cloud provider; what /status displays" },
    "storage": { "enum": ["macos-keychain", "credentials-json", "env-only", "none"],
                "description": "macOS: encrypted Keychain. Linux: ~/.claude/.credentials.json mode 0600 (or under CLAUDE_CONFIG_DIR). Windows: %USERPROFILE%\\.claude\\.credentials.json. env-only when an API key/token is supplied purely by environment" } },
  "additionalProperties": false }
```
| field | type | volatile? | changed-by | address? -> resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| method / account / storage | (the auth state) | yes (operator runs /login, /logout, sets/unsets an env credential — host actions) | NO company event; auth resolution happens inside `claude` at startup, invisible to the supervisor | — | NOT exposed. The company reads NO credential and surfaces NO auth status. A spawned session AUTHENTICATES AS the service account (whatever credential the host the supervisor runs under resolves). There is no per-session identity, no credential threading, no /status proxy |
| per-session identity | — | n/a | — | — | NOT BUILT. The supervisor spawn (`runtime/session_supervisor.py:259-265`) threads no auth flag/env; all fabric sessions share one host identity. Distinct CALLER identity (who is asking the supervisor) is a transport concern (free-text `source`, NOT authenticated) — see [[session#Caller]] and TRANSPORTS.md |

Native credential-management facts a UI must respect (source authentication.md#credential-management):
`apiKeyHelper` is called after 5 min or on HTTP 401 (`CLAUDE_CODE_API_KEY_HELPER_TTL_MS` tunes it; a
helper taking >10s shows a prompt-bar warning); `apiKeyHelper`/`ANTHROPIC_API_KEY`/`ANTHROPIC_AUTH_TOKEN`
apply to TERMINAL CLI sessions only — Desktop and cloud sessions use OAuth exclusively. A subscription
user with `ANTHROPIC_API_KEY` set has the API key take precedence once approved (a common failure when
the key's org is disabled — `unset ANTHROPIC_API_KEY` to fall back; confirm with `/status`).

## State model
**State model: stateless.** An authentication state has no lifecycle of its own — Claude Code resolves
it once at session start from the precedence chain. The reopened acts (`claude auth login`/`logout`,
`claude setup-token`) MUTATE the host credential store via the config_writer R3 service (consent-gated),
and the next session start re-resolves. The session it authenticates owns the lifecycle
([[session#State model]]).

## Caller
**The company never authenticates a consumer to Anthropic and never reads a credential; a fabric
session's Anthropic identity is the SERVICE ACCOUNT's host login, and the CALLER identity (who is
talking to the supervisor) is the transport's anonymous-local / free-text `source` model, NOT a
credentialed identity.** This is the deliberate boundary: per-consumer Anthropic identity would mean
the company storing or proxying Anthropic credentials, which it does not do and which the usage policy
restricts (https://code.claude.com/docs/en/legal-and-compliance.md#authentication-and-credential-use:
third parties may not route requests through Free/Pro/Max plan credentials on behalf of users). See
[[platform#op: platform.privacy]] for what the company does and does not store.

## Operations

## op: auth.get
**`auth.get` is the BUILT auth-status read: which credential method and account a session is running
under, REDACTED — the company surfaces the METHOD (subscription / console-api / token) + account label
via `claude auth status`, and the secret NEVER transits (the read output is _redact-stripped). The
bridge HTTP arm is still planned (the Wire handoff); the MCP face op is reachable today.**
```contract:op
op: auth.get
resource: auth
kind: get
status: building
direction: outbound
atlas: [CC-24.1]
tasks:
  - phrase: "what account is the fabric authenticated as"
  - phrase: "which credential method is active"
  - phrase: "is the fabric on a subscription or an API key"
  - alias: "auth status"
  - alias: "who am I logged in as"
bindings:
  - { kind: mcp, tool: auth, op-param: "op=get", server: company, exposure: "exposure.json#mcp-company", status: building, note: "BUILT (2026-06-12; mcp_face/tools/automation.py auth() → runtime/capability_handlers/automation.py:auth, direct-read host_reads CC-24.1). Returns the credential METHOD + account label REDACTED (the secret never transits — _redact strips token/api_key/oauth/CLAUDE_CODE_OAUTH_TOKEN). live-verify pending (lead): a REAL `claude auth status`. The host ACTS (relogin/logout/setup-token) stay OUT — absence-of-row IS the boundary." }
  - { kind: http, method: GET, path: "/auth  (PLANNED: a non-secret auth-status endpoint)", transport: supervisor-http, exposure: "exposure.json#supervisor-http", status: planned, note: "GAP: no auth-status endpoint exists; the supervisor reads no credential and tracks no account. The native equivalent is the interactive /status 'auth method' line (human-only) and `claude auth status` (CLI, host). Neither is a company route. Wiring would mean the supervisor reporting the service account's resolved method WITHOUT the secret" }
liveness: snapshot
live-twin: "none — auth state changes only when the operator re-logins the host account + restarts the service"
emits: []
verification:
  auth-status-read: {state: unverified, note: "no auth-status endpoint — planned"}
```
The honest interim path: the OPERATOR checks the host with the interactive `/status` (shows the active
auth method + account) or `claude auth status` (CLI) — both run against the service account's
terminal, NOT a company route. These built-in surfaces are inventoried in INVENTORY-EXCLUSIONS.md
(Claude Code's own commands, not `company …` routes). A consumer cannot read auth state through the
company today.
```contract:example
captured: synthetic            # status=planned -> synthetic legal AND loud; no auth-status endpoint exists (V11)
binding: http
request: |
  GET /auth HTTP/1.1   (PLANNED endpoint)
response: |
  HTTP/1.1 501 Not Implemented
  {"error": "Auth status is planned; the company reads no credential and exposes no /status proxy. On the host, the operator runs the interactive /status or `claude auth status`. The fabric session authenticates as the service account."}
```
Adjacent: [[platform#op: platform.cloud-provider]] (the highest-precedence credential class),
[[platform#op: platform.privacy]] (what is/isn't stored), [[settings#op: settings.get]] (the
apiKeyHelper setting key), [[auth#op: auth.act]] (the planned switch).

## op: auth.act
**`auth.act` is the REOPENED credential steer: relogin (`claude auth login`), logout (`claude auth
logout`), or mint a long-lived token (`claude setup-token`) — under Tim's sole-operator steer these
are BUILDABLE consent-gated R3 host-config ops (NOT a multi-user boundary), built on the company face
as `auto.auth` op="act"; the config_writer R3 service shells the native CLI (the floor — the face
never shells), and setup-token's printed token is surfaced to the consenting operator terminal ONLY,
never folded into a wire result (the redaction floor).**
```contract:op
op: auth.act
resource: auth
kind: act
status: building
direction: outbound
atlas: [CC-24.2, CC-24.3, CC-24.4]
tasks:
  - phrase: "switch the Claude account"
    params: {act: relogin}
  - phrase: "log out of the current account"
    params: {act: logout}
  - phrase: "create a long-lived token for CI"
    params: {act: setup-token}
  - alias: "re-authenticate"
  - alias: "change accounts"
  - alias: "generate an auth token"
bindings:
  - { kind: mcp, tool: auth, op-param: "op=act, act=relogin|logout|setup-token", server: company, exposure: "exposure.json#mcp-company", status: building, note: "BUILT (2026-06-12; mcp_face/tools/automation.py auth(op=act) -> runtime/capability_handlers/automation.py:auth, rail R3). REOPENED by Tim's sole-operator steer (consent-not-lockdown): the handler builds the argv via the auto.auth:<act> cli_allowlist row (relogin=`claude auth login` exec, logout=`claude auth logout` write, setup-token=`claude setup-token` exec+returns_secret); the config_writer R3 service shells it, consent-gated. setup-token's printed token is surfaced to the consenting operator terminal ONLY and NEVER folded into the result (redaction floor). live-verify pending (lead): a REAL `claude auth login`/`logout`/`setup-token` round-trip." }
  - { kind: http, method: POST, path: "/api/auto/auth  (PLANNED bridge arm — Wire handoff)", transport: bridge-http, exposure: "exposure.json#bridge-http", status: planned, note: "GAP: the bridge /api/auto/auth arm is not built (the L-Wire lane owns bridge.py per the no-edit-bridge rule). The MCP face op IS reachable today; the operator-vantage HTTP arm rides /api/resolve's consent precedent when the Wire lands it" }
liveness: none
emits: []
consequences:
  - when: "the consented R3 act runs (relogin/logout/setup-token via the config_writer service)"
    expect: []
    bound: "takes effect on the NEXT session start, not mid-session — a running fabric session keeps its resolved credential until restart"
    evidence: "no company event; the new credential posture is observable by re-reading [[auth#op: auth.get]] (`claude auth status`, method only, redacted) and by the next spawn's success/failure — an absence-shaped outcome (CONTRACT-FORMAT section 6 V9)"
correlate: [session]
verification:
  relogin:     {state: unverified, note: "building — `claude auth login` argv built on R3; live-verify pending (lead): a REAL re-auth round-trip"}
  logout:      {state: unverified, note: "building — `claude auth logout` argv built on R3 (reversed by relogin); live-verify pending (lead)"}
  setup-token: {state: unverified, note: "building — `claude setup-token` argv built on R3 (returns_secret: token to operator terminal only, never returned); live-verify pending (lead)"}
```
### Description (purpose-free)
The native account-management surface, REOPENED as consent-gated R3 company acts (Tim's sole-operator
steer — the operator is the only user and is trusted, so these are enabled, not locked out). relogin
runs `claude auth login` (OAuth, paste-code fallback in WSL/SSH/containers — reads the code from stdin)
and switches the active subscription/Console account; logout runs `claude auth logout` and clears the
stored credential (reversed by relogin — the git-revert-equivalent backstop). `claude setup-token`
walks an OAuth authorization and PRINTS a one-year token to set as `CLAUDE_CODE_OAUTH_TOKEN` (it saves
nothing; copy it) — inference-scoped, requires a Pro/Max/Team/Enterprise plan, and CANNOT establish
Remote Control sessions; `--bare` mode does not read it (use `ANTHROPIC_API_KEY`/`apiKeyHelper` there).
An env credential (`ANTHROPIC_API_KEY`/`ANTHROPIC_AUTH_TOKEN`) supplied to the service process changes
the resolved method per the precedence chain. The company face builds the argv and the config_writer
R3 service shells it; setup-token's printed token reaches the consenting operator terminal ONLY, never
a wire result. Source: https://code.claude.com/docs/en/authentication.md.
### Interaction semantics
- **Credential change is next-start, not mid-session** — a live fabric session keeps its resolved auth
  until the supervisor restarts the subprocess.
- **API key over subscription gotcha** — if the service account has both an active subscription and
  `ANTHROPIC_API_KEY` set, the key wins once approved; an expired key's org causes auth failure. The
  recovery (`unset ANTHROPIC_API_KEY` + restart) is operator-only.
- **Consent-not-lockdown** — the operator's OWN credential acts (relogin/logout/setup-token) are
  ENABLED, consent-gated; a cold MCP agent may PROPOSE but the consequential R3 act rides the
  operator-consent seam (the same vantage precedent as /api/resolve). Per-CONSUMER Anthropic identity
  (storing/proxying a DIFFERENT user's credential) remains out of scope by the usage policy — the
  reopening is the SOLE operator steering their own host credential, never multi-user credential proxy.
### Errors
```contract:error
code: auth.consent-required | http: 409 | retryable: true
when: a credential-changing act (relogin/logout/setup-token) is called WITHOUT operator consent (consent-not-lockdown — the act is ENABLED but the consequential R3 run needs a consent signal)
teach: "This act changes the host credential, so it needs an operator consent signal — it is NOT locked out (consent-not-lockdown). Re-call with consent=true (or hold a standing config_writer consent grant), then the config_writer R3 service runs `claude auth login`/`logout`/`setup-token`. Re-login reverses a logout; git-revert-equivalent is the backstop. Named at [[auth#op: auth.act]] and https://code.claude.com/docs/en/authentication.md. NOTE: proxying a DIFFERENT user's credential stays out of scope (usage policy) — this is the SOLE operator steering their own credential."
```
```contract:error
code: auth.failed | http: 401 | retryable: false
when: a spawned session's underlying claude process fails to authenticate (expired/invalid host credential)
teach: "The service account's credential is invalid or expired. Common cause: an ANTHROPIC_API_KEY whose org is disabled taking precedence over a valid subscription — `unset ANTHROPIC_API_KEY` and restart, or re-run /login on the host. Confirm with the host /status. This surfaces as a spawn/turn failure on [[session#op: session.watch]], not a company auth op."
```
```contract:example
captured: synthetic            # status=building -> synthetic legal AND loud; replaced by captured evidence at flip-to-live (V11)
binding: mcp
request: auth(op="act", act="setup-token", consent=True)
response: { "resource": "auto.auth", "op": "act", "act": "setup-token", "rail": "R3",
            "status": "intent-built",
            "executor": "the config-writer service (sanctioned R3 shelling) — POST /cli, consent-gated",
            "proposed": { "tool": "claude", "argv": ["claude", "setup-token"], "tier": "exec" },
            "consent": "consented",
            "returns_secret": true,
            "secret_handling": "the printed token reaches the consenting operator terminal ONLY; this handler returns NO token field (redaction floor, the secret never transits the wire)",
            "watch": "re-read auth(op=get) — the credential method reflects the new posture",
            "note": "live-verify pending (lead): a REAL `claude setup-token` round-trip" }
# NOTE: no token field appears in the result — the secret never transits the wire (the floor by NOT returning it).
```
Adjacent: [[auth#op: auth.get]] (the redacted status read — re-read it to observe the new posture),
[[platform#op: platform.cloud-provider]] (provider credentials, the highest-precedence method),
[[platform#op: platform.privacy]] (the credential-storage + data boundary), [[session#op:
session.create]] (where an auth failure surfaces).

## Errors
**Resource-level error vocabulary: `auth.consent-required` (the 409 a credential-change act returns
without an operator consent signal — consent-not-lockdown, the act is ENABLED but the consequential R3
run needs consent) and `auth.failed` (the 401 a spawn/turn shows when the service account's host
credential is invalid, with the API-key-precedence gotcha and its recovery).** Both teach the in-corpus
recovery. The read (`auth.get`) surfaces only the credential METHOD, redacted — never a secret; the
acts steer the SOLE operator's own credential, never a different user's (the usage-policy boundary held).

## Links
**No address-typed fields: an auth state references the `session://` it authenticates (dereferences to
[[session]]) and points at [[platform]] (cloud-provider credentials + the privacy/storage boundary),
[[settings]] (the apiKeyHelper key), and [[cost-usage]] (the account whose spend is tracked).**
Credential method names, account kinds, and env-var names are Claude Code/Anthropic identifiers
(https://code.claude.com/docs/en/authentication.md), not fabric addresses — and credentials themselves
are NEVER surfaced as values, by design.
