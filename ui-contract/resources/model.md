---
type: contract-entry
resource: model
summary: Which Claude model a session runs and how hard it reasons — the alias/name, the effort level, the thinking toggle, and the fallback chain; the company spawns every session on the account default with no model lever yet, so this resource is the native contract with the spawn-param gap named.
schemes: []
status: building
relates-to: ["[[session]]", "[[permission]]", "[[agent-team]]", "[[headless-control]]", "[[fabric-config]]"]
---

# Resource: model


## Identity
**A model selection is identified by an alias or a full model NAME, not a fabric address — there is
no `model://` scheme; a selection is a launch attribute of a [[session]] (or of a subagent /
teammate), resolved by Claude Code's own precedence order.** The selectable values are the closed
alias set plus any full model id the provider accepts (source of truth:
https://code.claude.com/docs/en/model-config.md). The company does not own a model registry of its
own here — it inherits Claude Code's. Bare names and aliases are both accepted by the native
`--model` flag; this resource contracts the consumer-facing levers, all of them `planned` against
the company spawn until it carries a model param.

## Representation
**A model selection is the tuple (model alias-or-name, effort level, thinking on/off, fallback
chain) — Claude Code resolves the effective model through a documented precedence order; the
company supplies NONE of these today, so every fabric session runs the account-default model at its
default effort.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/model.selection",
  "type": "object",
  "properties": {
    "model": { "type": "string",
               "description": "an alias (default|best|fable|sonnet|opus|haiku|sonnet[1m]|opus[1m]|opusplan) OR a full name (e.g. claude-opus-4-8, claude-sonnet-4-6) OR claude-...[1m] for the 1M window. https://code.claude.com/docs/en/model-config.md#model-aliases" },
    "effort": { "enum": ["low", "medium", "high", "xhigh", "max", "ultracode", "auto"],
                "description": "adaptive-reasoning level; available levels depend on the model (Fable5/Opus4.8/4.7 support xhigh; Opus4.6/Sonnet4.6 cap at high+max). ultracode is a Claude Code setting (xhigh + dynamic-workflow orchestration), session-only. https://code.claude.com/docs/en/model-config.md#adjust-effort-level" },
    "thinking": { "type": ["boolean", "null"],
                  "description": "extended thinking on/off; on adaptive-reasoning models effort is the primary control. MAX_THINKING_TOKENS=0 disables (except Fable5, which cannot turn thinking off). null = inherit" },
    "fallback": { "type": "array", "items": { "type": "string" }, "maxItems": 3,
                  "description": "ordered fallback models tried on overload/unavailable/non-retryable server errors (NOT auth/billing/rate-limit). Capped at 3 after dedup; the switch lasts the current turn only. --fallback-model / fallbackModel setting" } } }
```
| field | type | volatile? | changed-by | address? -> resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| model | string | yes (planned: per-spawn / native /model mid-session / ANTHROPIC_MODEL env) | NO company control — the supervisor spawn (`runtime/session_supervisor.py:261-265`) passes NO `--model`; the session uses the account default | — | NOT SET by the fabric on any spawn. Effective model = the host account's default (Max/API -> Opus 4.8; Pro/Team -> Sonnet 4.6). Per-session selection = NOT BUILT |
| effort | enum | yes (planned) | NO company control — no `--effort` passed | — | NOT SET; defaults to the model's default (high on Fable5/Opus4.8/Opus4.6/Sonnet4.6, xhigh on Opus4.7) |
| thinking | bool | yes (planned) | — | — | NOT SET; default per model/account |
| fallback | array | n/a (planned) | — | — | NOT SET; no `--fallback-model` passed |

Subagent/teammate model: the env var `CLAUDE_CODE_SUBAGENT_MODEL` overrides ALL subagent and
agent-team teammate models and the per-invocation/frontmatter `model` (set to `inherit` to disable);
the company sets none of these (see [[agent-team]]). Resolution precedence for a subagent's model:
1) `CLAUDE_CODE_SUBAGENT_MODEL` env, 2) per-invocation `model` param, 3) the subagent definition's
`model` frontmatter, 4) the main conversation's model.

## State model
**State model: stateless.** A model selection has no lifecycle — it is a launch attribute resolved
per turn against Claude Code's precedence order. The session it parameterises owns the lifecycle
([[session#State model]]). NOTE: a session resumed via `--resume`/`--continue` KEEPS the model it was
saved with regardless of the current setting (a saved-transcript invariant, not a transition).

## Caller
**Reading the effective model of a running session is observable on the per-session stream
(`system/init` carries `model`); SELECTING a model is whoever spawns the session (planned spawn
param) or, natively, the interactive operator via `/model` — never an ambient company default.** The
company is provider-agnostic about WHICH model resolves: it inherits the host's account tier and any
`ANTHROPIC_DEFAULT_*_MODEL` / `availableModels` the operator configured outside the fabric.

## Operations

## op: model.list
**`model.list` is the available-models read: the alias set plus whatever the host account/provider
exposes — PLANNED as a company face because the supervisor surfaces no model catalog today; a
consumer needing the live list reads the per-session `system/init` or falls back to the documented
alias table.**
```contract:op
op: model.list
resource: model
kind: list
status: planned
direction: outbound
atlas: [CC-10.1]
tasks:
  - phrase: "what models can a session run"
  - phrase: "list the model aliases"
  - alias: "available models"
  - alias: "which models does my account have"
bindings:
  - { kind: http, method: GET, path: "/models  (PLANNED: a supervisor catalog endpoint)", transport: supervisor-http, exposure: "exposure.json#supervisor-http", status: planned, note: "GAP: no model catalog endpoint exists. The native equivalents are the /model picker (interactive only) and the SDK supportedModels()/ModelInfo type — neither is exposed through a company face. Interim: the alias table in [[model#Representation]] is the static list" }
liveness: snapshot
live-twin: "[[headless-control#op: headless-control.watch]] system/init `model` for the ONE model a given session actually resolved"
emits: []
verification:
  catalog-read: {state: unverified, note: "no catalog endpoint — planned"}
```
The closed alias set a consumer can rely on without any live read (per
https://code.claude.com/docs/en/model-config.md#model-aliases): `default` (clears override ->
account default), `best` (Fable5 where available else latest Opus), `fable` (Claude Fable 5),
`sonnet`, `opus`, `haiku`, `sonnet[1m]`/`opus[1m]` (1M context), `opusplan` (Opus in plan mode ->
Sonnet in execution). Aliases track the recommended version and move over time; pin with a full
name or `ANTHROPIC_DEFAULT_*_MODEL`. Enterprise `availableModels` can restrict the picker.
Adjacent: [[model#op: model.act]] (select one), [[headless-control#op: headless-control.watch]]
(the resolved model of a live session).

## op: model.act
**`model.act` is the PLANNED model/reasoning steer: choose the model, effort level, thinking toggle
and fallback chain for a session at spawn, and (native-SDK) switch model or effort mid-session — the
native levers `--model`/`--effort`/`--fallback-model`/`/model`/`/effort` that the company spawn does
NOT yet carry, named here so a UI builds the real seam.**
```contract:op
op: model.act
resource: model
kind: act
status: building
direction: outbound
atlas: [CC-10.2, CC-10.3, CC-10.4, CC-10.5]
tasks:
  - phrase: "spawn a session on a specific model"
    params: {model: opus}
  - phrase: "run a cheaper faster model for a simple task"
    params: {model: haiku}
  - phrase: "make a session reason harder"
    params: {effort: xhigh}
  - phrase: "use opus for planning then sonnet for execution"
    params: {model: opusplan}
  - phrase: "set a fallback model if the primary is overloaded"
    params: {fallback: ["sonnet", "haiku"]}
  - alias: "switch model"
  - alias: "select reasoning effort"
  - alias: "turn on extended thinking"
  - alias: "use the 1 million token context"
bindings:
  - { kind: http, method: POST, path: "/spawn  (model/effort/fallback on the body → --model/--effort/--fallback-model)", transport: supervisor-http, exposure: "exposure.json#supervisor-http", status: building, note: "BUILT (runtime/session_supervisor.py _build_spawn_cmd + /spawn body, 2026-06-12): body fields model/effort/fallback thread to --model/--effort/--fallback-model (each grounded in the Atlas cli-reference). thinking is NOT a CLI flag (MAX_THINKING_TOKENS env / per-model) so it stays unbuilt here. CLAUDE_CODE_SUBAGENT_MODEL would govern any fan-spawned consults. live-verify pending (lead): a real spawn must confirm the chosen model actually ran (read system/init `model`) — built+unit-tested on the cmd-builder, NOT flipped live" }
  - { kind: http, method: POST, path: "/model  (PLANNED: mid-session set-model control_request, the /model analogue)", transport: supervisor-http, exposure: "exposure.json#supervisor-http", status: planned, note: "GAP: no control surface for mid-session model switch. A resumed session keeps its saved model regardless — the native invariant constrains what this op can promise" }
liveness: none
emits: []
consequences:
  - when: "model set at spawn (planned)"
    expect: [agent_sessions.spawned]
    bound: "the spawn's own bound ([[session#op: session.create]]); the chosen model is observable only on the session's system/init `model` field — NOT a distinct fabric event"
    evidence: "[[headless-control#op: headless-control.watch]] system/init `model` — the named read for this absence-of-dedicated-event outcome"
  - when: "content-flagged fallback fires (Fable5 safety classifier, native automatic)"
    expect: []
    bound: "unbounded-with-evidence: the turn re-runs on the default Opus; the switch shows as a transcript notice, observable as a model change on the next system message"
    evidence: "the per-session stream's text/result frames carry the fallback notice; in non-interactive mode a flagged request ENDS the turn with a refusal instead (is_error result) — the corpus contracts that this is expected routing, not a fault"
correlate: [session]
verification:
  model-at-spawn: {state: probe-verified, run: "session_supervisor_params_acceptance (cmd-builder: model→--model, fallback→--fallback-model)", date: 2026-06-12, note: "BUILT: the /spawn body threads model/effort/fallback to the flags; unit-proven on the built cmd. live-verify pending (lead): a REAL spawn must confirm the model took (system/init `model`) — NOT flipped live"}
  effort-at-spawn: {state: probe-verified, run: "session_supervisor_params_acceptance (cmd-builder: effort→--effort)", date: 2026-06-12, note: "BUILT: effort threads to --effort (Atlas-verified flag). live-verify pending (lead): a real spawn must confirm the effort took"}
  set-mid-session: {state: unverified, note: "STILL planned — the mid-session /model control surface is not built; the resumed-session-keeps-model invariant also limits it"}
```
### Description (purpose-free)
The native model/reasoning surface, all `planned` at the company layer. At spawn (planned): choose
`model` (alias or name), `effort`, `thinking`, and a `fallback` chain — the native flags `--model`,
`--effort`, `--fallback-model`, `MAX_THINKING_TOKENS`. Mid-session (planned, native `/model` /
`/effort`): switch model or effort on a live session — with the hard constraint that a resumed
session keeps its saved model. The one native behaviour that operates WITHOUT any company wiring is
automatic content-based fallback FROM Fable 5: requests flagged by its cybersecurity/biology
classifiers re-run on the default Opus (a notice in the transcript), and in non-interactive mode a
flagged request ends the turn with a refusal — relevant because fabric sessions ARE non-interactive
(`-p`), so a consumer must treat such a refusal as expected routing, not a contract failure.
### Request (PLANNED shape)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/model.act.request",
  "type": "object",
  "required": ["session", "act"],
  "properties": {
    "session":  { "type": "string", "description": "session://<id> spawned or steered" },
    "act":      { "enum": ["set-at-spawn", "set-model", "set-effort"] },
    "model":    { "type": "string", "description": "alias or full name; see [[model#op: model.list]]" },
    "effort":   { "enum": ["low", "medium", "high", "xhigh", "max", "ultracode", "auto"] },
    "thinking": { "type": ["boolean", "null"] },
    "fallback": { "type": "array", "items": { "type": "string" }, "maxItems": 3 } },
  "additionalProperties": false }
```
### Interaction semantics
Native rules a consumer respects when this lands (sourced to model-config.md):
- **Effort floors to the model.** Setting a level above the active model's support runs at the
  highest supported level at or below it (e.g. `xhigh` runs as `high` on Opus 4.6). `max` and
  `ultracode` are session-only.
- **Resumed sessions keep their model.** `--resume`/`--continue` ignore the current model setting;
  this op cannot change a resumed session's model unless the saved model was retired.
- **`opusplan`** uses Opus during plan mode then Sonnet for execution; its plan-mode Opus phase stays
  at the 200K window (the 1M upgrade does not apply to `opusplan`).
- **Fallback excludes** auth/billing/rate-limit/request-size/transport errors — those follow normal
  retry, never a model switch. The chain caps at 3.
- **`ultrathink`** keyword in a prompt requests deeper reasoning for one turn without changing the
  session effort; other "think harder" phrases are ordinary text (lint-ok: ultrathink is a Claude
  Code reserved keyword, not a UI directive).
### Errors
```contract:error
code: model.unsupported-effort | http: 400 | retryable: false
when: effort value not in the closed enum
teach: "Effort levels are low/medium/high/xhigh/max/ultracode/auto, and the model floors unsupported ones down. See [[model#Representation]] and https://code.claude.com/docs/en/model-config.md#adjust-effort-level."
```
```contract:error
code: model.not-exposed | http: 501 | retryable: false
when: a MID-SESSION model switch is requested (act: set-model on a live session)
teach: "Spawn-time model/effort/fallback selection is now BUILT (the /spawn body threads --model/--effort/--fallback-model). The MID-SESSION switch (/model analogue) is still PLANNED — no control surface writes it, and a resumed session keeps its saved model regardless. OBSERVE a live session's resolved model via [[headless-control#op: headless-control.watch]] system/init."
```
```contract:example
captured: synthetic            # status=building, live-verify pending (lead): the spawn ACCEPTS the params (cmd-builder unit-proven); a REAL spawn confirming the model TOOK is the lead's live-verify, so this stays synthetic-and-loud, NOT a captured-live exchange (V11)
binding: http
request: |
  POST /spawn HTTP/1.1
  {"cwd": "/home/tim/scratch", "name": "deep-1", "model": "opus", "effort": "xhigh", "fallback": ["sonnet", "haiku"]}
response: |
  HTTP/1.1 200 OK
  {"ok": true, "session": {"id": "as-1a2b3c4d", "name": "deep-1", "state": "starting"}}
  # built: the body threads --model opus --effort xhigh --fallback-model sonnet,haiku onto the spawn cmd.
  # live-verify pending (lead): confirm the resolved model via the session's system/init `model` field.
```
Adjacent: [[model#op: model.list]] (the values), [[session#op: session.create]] (the spawn this
extends), [[agent-team]] (CLAUDE_CODE_SUBAGENT_MODEL governs teammate models),
[[headless-control#op: headless-control.watch]] (the resolved-model observation).

## Errors
**Resource-level error vocabulary: `model.unsupported-effort` (closed-enum guard) and
`model.not-exposed` (the honest 501 the MID-SESSION switch returns — spawn-time selection is now BUILT).**
Both teach the in-corpus recovery (the system/init observation; for mid-session, the resumed-keeps-model
invariant). No error asserts a selection capability the supervisor lacks; the spawn-time params are
built+unit-proven with a live-verify-pending (lead) note, never claimed proven against a real turn.

## Links
**No address-typed fields: a selection references the `session://` it parameterises (dereferences to
[[session]]) and nothing else.** Model aliases and names are Claude Code identifiers
(https://code.claude.com/docs/en/model-config.md), not fabric addresses — they never resolve to a
corpus entry, by design.
