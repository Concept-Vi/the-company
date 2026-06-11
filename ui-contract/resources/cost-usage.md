---
type: contract-entry
resource: cost-usage
summary: The cost/usage telemetry data model a UI renders — per-turn token+cost from the Claude Code result message, the OpenTelemetry metric set, the /cost & /usage views, the on-disk stats-cache, the headless --max-budget-usd cap, and the org Usage & Cost API. Today the data flows through the supervisor and is DISCARDED; the surface is planned, the gap code-cited.
schemes: []
status: planned
relates-to: ["[[events]]", "[[session]]", "[[fabric-config]]", "[[knowledge-corpus]]"]
---

# Resource: cost-usage

## Identity
**Cost/usage has no id of its own — it is telemetry ATTRIBUTED to other resources: per a
session/turn (the result message), per a model, per a skill/plugin/subagent (the OTel
attributes), per an org/workspace (the Usage & Cost API). A UI keys it by the resource it
attaches to; this entry contracts the SHAPE of that telemetry.**
This resource is `planned`. The DATA is real and partly already flowing through the company
(see Representation's code-cite), but NO company endpoint surfaces, persists, or aggregates
cost/usage today (verified — `grep -rilE '/cost|cost\.usage|token\.usage|stats-cache' runtime/
mcp_face/ ops/` returns nothing in `~/company`). Every fact below is grounded in the Claude
Code Atlas + docs mirror — search via [[knowledge-corpus#op: knowledge-corpus.search]]
(`vault: claude-code-atlas`). Primary cites: `Docs/claude-code/costs.md`,
`Docs/claude-code/monitoring-usage.md`, `Docs/claude-code/analytics.md`,
`Docs/claude-code/agent-sdk/typescript.md`, `manage-claude/usage-cost-api.md`,
`Config & UI Data Model.md`.

## Representation
**Cost/usage exists at four grains, each its own machine shape: (1) PER-TURN — the result
message's token counts + a client-side cost estimate; (2) METRIC — the OpenTelemetry counter
set; (3) ON-DISK — the local stats cache `/usage` reads its historical totals from; (4) ORG —
the Anthropic Usage & Cost API. A UI renders different views off different grains.**

### (1) Per-turn — the result message `ModelUsage` shape (on the wire NOW)
Returned in the Agent SDK / `claude -p --output-format stream-json` result message. `costUSD`
is a CLIENT-SIDE ESTIMATE (see Errors). (Source:
`Docs/claude-code/agent-sdk/typescript.md#modelusage`.)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/cost-usage.model-usage",
  "type": "object",
  "properties": {
    "inputTokens":              { "type": "integer" },
    "outputTokens":             { "type": "integer" },
    "cacheReadInputTokens":     { "type": "integer", "description": "prompt-cache hits — cheaper than full input" },
    "cacheCreationInputTokens": { "type": "integer" },
    "webSearchRequests":        { "type": "integer" },
    "costUSD":                  { "type": "number", "description": "CLIENT-SIDE ESTIMATE from token counts × pricing — NOT the authoritative bill" },
    "contextWindow":            { "type": "integer" },
    "maxOutputTokens":          { "type": "integer" } } }
```
**CODE-CITED GAP (the headline honesty of this entry):** the company session supervisor
(`runtime/session_supervisor.py`) runs each turn under `--input-format stream-json
--output-format stream-json` and consumes the result event `ev` in `_turn_done` (line ~369),
but extracts ONLY `num_turns` and `is_error` into the `agent_sessions.turn` event (line ~380,
~384). `total_cost_usd` / `usage` / token counts carried by that same result event are NOT
read and NOT persisted — the cost data flows through the fabric and is discarded. This is the
exact adoption path: have the supervisor's emit helper stamp the `ModelUsage` fields onto the
`agent_sessions.turn` event ([[events]]); cost/usage then becomes a `building` read over the
event stream with zero new transport. (F10.1 gap-adoption candidate — see verification.)

### (2) Metric — the OpenTelemetry counter set (opt-in, all providers)
Exported when OTel is enabled. (Source: `Docs/claude-code/monitoring-usage.md`.)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/cost-usage.otel-metrics",
  "type": "object",
  "properties": {
    "claude_code.token.usage":        { "type": "object", "description": "break down by type(input/output), user, team, model, skill.name, plugin.name, agent.name" },
    "claude_code.cost.usage":         { "type": "object", "description": "approximate spend; carries the model attribute (only token.usage + cost.usage carry model)" },
    "claude_code.session.count":      { "type": "object" },
    "claude_code.lines_of_code.count":{ "type": "object" },
    "claude_code.commit.count":       { "type": "object" },
    "claude_code.pull_request.count": { "type": "object" } } }
```
Note: per-model breakdowns of lines/commits can only be APPROXIMATED by joining against the
token/cost metrics on `session.id` (activity counters never carry the model attribute).

### (3) On-disk — the local stats cache + the /usage view
`~/.claude/stats-cache.json` holds the historical totals `/usage` renders (deleting it loses
those totals — `Docs/claude-code/claude-directory.md`). The OTel traces live under
`~/.claude/debug/` (`Config & UI Data Model.md`). The `/usage` Session block (intended for API
users) renders, computed LOCALLY from this machine's session history:
```text
Total cost:            $0.55
Total duration (API):  6m 19.7s
Total duration (wall): 6h 33m 10.2s
Total code changes:    0 lines added, 0 lines removed
```
On Pro/Max/Team/Enterprise, `/usage` also shows plan-limit usage bars + an attribution
breakdown (recent usage as % across skills, subagents, plugins, individual MCP servers), with
`d`/`w` toggling 24h/7d. Figures are approximate, local-only — usage from other devices or
claude.ai is NOT included. (Source: `Docs/claude-code/costs.md#using-the-usage-command`.)
| reality (Tim's install, 2026-06-12) | value |
|---|---|
| `~/.claude/stats-cache.json` | present, 15,077 bytes — the historical-totals source `/usage` reads |
| supervisor cost capture | NONE — result-event cost/usage fields discarded (code-cite above), so the fabric has no cost history of its own yet |

### (4) Org — the Usage & Cost API + Analytics
For org-wide attribution: the Usage & Cost API (`/v1/organizations/usage_report/messages`,
Admin key, paginated, data within ~5 min) and the Claude Code Analytics API (per-user
estimated cost + productivity, the dashboard at claude.ai/analytics/claude-code, Anthropic
plans only). (Source: `manage-claude/usage-cost-api.md`, `Docs/claude-code/analytics.md`,
`admin-setup.md`.)

## State model
**State model: stateless.** (Telemetry accumulates but a read of it transitions nothing. The
one stateful adjacent behavior is the headless budget cap — see the `act` op — which causes a
SESSION state change, contracted on [[session]], not here.)

## Caller
**Read identity differs by grain: per-turn + /usage + stats-cache are LOCAL to this machine
(no auth, this device only); OTel export is configured per the OTel collector; the Usage &
Cost / Analytics APIs require an Anthropic ADMIN key and return ORG-scoped data. A UI must not
present local /usage estimates as authoritative org billing — they are different callers over
different data.**

## Operations

## op: cost-usage.get
**`cost-usage.get` is the cost/usage read — per-turn token+cost, the session running total, the
historical stats — the data a UI renders as a spend panel; planned as a company op, today read
only via Claude Code's own /usage (local) or the org Usage & Cost API.**
```contract:op
op: cost-usage.get
resource: cost-usage
kind: get
status: planned
direction: outbound
atlas: [CC-20.1, CC-20.2]
tasks:
  - phrase: "what has this session cost"
  - phrase: "show my token usage by model"
  - phrase: "how much of my plan have I used this week"
  - alias: "show the cost"
  - alias: "usage breakdown"
  - alias: "spend so far"
bindings:
  - { kind: cli, command: "claude /usage   (local session totals + plan bars + attribution; /cost shows the session cost breakdown)", transport: cli-local, exposure: "exposure.json#cli-local", status: planned, note: "BUILT-IN slash commands, not a company route; local-only, this-machine estimates" }
  - { kind: http, method: GET, path: "/v1/organizations/usage_report/messages", transport: anthropic-admin-api, exposure: "exposure.json#anthropic-admin-api", status: planned, note: "ORG grain; EXTERNAL Anthropic API, Admin key — see [[cost-usage#INVENTORY note]]; the company does not proxy it today" }
liveness: snapshot
live-twin: "none — accumulating totals, read point-in-time; the live per-turn signal would be [[events#op: events.watch]] IF the supervisor stamped cost onto turn events (see Representation gap)"
emits: []
verification:
  no-company-endpoint: {state: unverified, note: "GAP (code-cited): supervisor discards result-event cost/usage; no company read exists. ADOPTION PATH: stamp ModelUsage onto agent_sessions.turn → cost-usage.get becomes a building read over [[events]]. F10.1 candidate. Interim: /usage (local) + the Usage & Cost API (org)"}
```
Interim honest paths: `claude /usage` and `/cost` for this machine's local estimates; the org
Usage & Cost API for authoritative-ish attribution; `~/.claude/stats-cache.json` is directly
readable for historical totals. None is a company fabric endpoint yet.
Adjacent: [[cost-usage#op: cost-usage.act]] (the budget cap), [[events]] (where per-turn cost
WOULD ride once captured), [[session#op: session.get]] (the session a turn's cost attaches to).

## op: cost-usage.act
**`cost-usage.act` is the cost-control verb — `cap-budget`, the headless `--max-budget-usd`
spend ceiling that STOPS a session when exceeded — the one cost affordance that causes an
effect rather than just reporting; planned as a company parameter on session spawn.**
```contract:op
op: cost-usage.act
resource: cost-usage
kind: act
status: planned
direction: outbound
atlas: [CC-20.3]
tasks:
  - phrase: "cap this headless run at five dollars"
    params: {act: cap-budget, max_budget_usd: 5}
  - alias: "set a spend limit"
  - alias: "stop if it costs too much"
named-acts: [cap-budget]
bindings:
  - { kind: cli, command: "claude -p --max-budget-usd <amount>   (headless only; stops the session when the budget is exceeded)", transport: cli-local, exposure: "exposure.json#cli-local", status: planned, note: "a Claude Code HEADLESS flag; the company supervisor spawns headless sessions (runtime/session_supervisor.py) so it COULD pass --max-budget-usd through on session.create — that wiring is the planned company affordance" }
liveness: none
emits: []
consequences:
  - when: "the running budget exceeds max_budget_usd"
    expect: []
    evidence: "the session STOPS (a session-state change — observed on [[events]] as the close event if the supervisor passes the flag through and reaps the stopped child); the cap prevents surprise large bills"
correlate: []
verification:
  no-company-endpoint: {state: unverified, note: "GAP (named): --max-budget-usd is a Claude Code flag, not yet threaded through the company session.create. Adoption: add max_budget_usd to the spawn params on [[session#op: session.create]]. F10.1 candidate"}
```
Adjacent cost-OPTIMIZATION levers (config, not ops — a UI surfaces them but they live in other
lanes): fast mode (reduced token cost), prompt caching (cheaper repeated input), model
selection (cheaper models for simple tasks — F3 model lane), `/compact` + effort level
(fewer tokens — F2 context lane), moving instructions out of CLAUDE.md into on-demand skills
([[claude-memory]]). (Source: `Docs/claude-code/costs.md`.)
Adjacent: [[cost-usage#op: cost-usage.get]] (read the spend), [[session#op: session.create]]
(where the cap would be a spawn parameter).

## Errors
**The defining error is EPISTEMIC, not transport: every local cost figure is a client-side
ESTIMATE computed from token counts × pricing — it is NOT the authoritative bill, and a UI
that presents it as billing is wrong by construction. The authoritative source is the API
provider (Claude Console / Bedrock / Vertex). A second honest condition: local /usage and
stats-cache cover THIS machine only — usage from other devices or claude.ai is absent, not
zero.**
```contract:error
code: cost-usage.estimate-not-bill | retryable: false
when: a consumer treats a local costUSD / /usage / cost.usage figure as authoritative billing
teach: "These are approximations (the docs state it on every surface: ModelUsage.costUSD, /usage Session block, the OTel cost.usage metric). For actual costs use the Usage page in the Claude Console / your provider's billing. Render local figures LABELLED as estimates."
```
```contract:error
code: cost-usage.this-machine-only | retryable: false
when: a consumer reads local /usage / stats-cache as the operator's TOTAL usage across devices
teach: "Local cost/usage is computed from THIS machine's session history; other devices and claude.ai are not included. For cross-device/org totals use the Usage & Cost API (Admin key) or the Analytics dashboard."
```

## Links
**No address scheme — cost/usage attaches to other resources by attribute. The relations a UI
renders: per-turn ModelUsage → the [[session]] turn it measures (would ride [[events]]
`agent_sessions.turn` once captured — the named gap); OTel `skill.name`/`plugin.name`/
`agent.name` attributes → the extension resources (F4 lane) and subagent/team resources (F3
lane) they attribute spend to; `--max-budget-usd` → a spawn parameter on [[session#op:
session.create]]. The cost data MODEL lives here; the resources it measures live across the
fabric.**

## INVENTORY note
The `anthropic-admin-api` transport in `cost-usage.get`'s binding is an EXTERNAL Anthropic
endpoint, not a company-owned face — it is recorded in TRANSPORTS.md as an external transport
the company may proxy later; until a company route proxies it, that binding is `planned` and
its endpoint belongs in INVENTORY-EXCLUSIONS.md as "external, not a company face" rather than a
phantom company route. (Stated here so V21/V22 have a truthful target, never a silent skip.)
