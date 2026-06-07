---
type: design
module: build-prep/concurrent-cognition
aliases: ["Role Registry — design", "Concurrent Cognition 01"]
tags: [company, design, roles, judge, collective-cognition, concurrent-cognition]
status: draft
relates-to: ["[[runtime — constitution]]", "[[fabric — constitution]]", "[[Company Map]]"]
---

# Role Registry — generalising the finished-thought judge into many concurrent small-model roles

**What this is.** A read-only map of the EXISTING role/judge machinery in `~/company`, then an on-paper
design (NOT built) for generalising it into a **Role Registry**: a registry of named, concurrently-running
small-model FUNCTIONS — each a `{id, prompt template, input addresses, output JSON schema, trigger
condition, model binding, mode-dependence, output destination, render hint}` — completing the growth path
the code already DECLARES (`suite.py:913-958`). Framed as **additive to `ROLE_REGISTRY`** (one source,
schema-additive — AGENTS.md rules 2+3), never a parallel registry.

> [!important] Epistemic status
> Every "EXISTS today" claim below carries a `file:line`. Every "net-new" is design, marked as such.
> Mapping is **Observed** (read from code). The design is **Inferred** proposal — not verified by execution.
> **Exception:** Part D's `ops/cli/gpu.py` / `services.json` / `set_ref` / `surface_review` claims rest on
> `STATE.md` + `MAP.md` PROSE, not a direct read of those files — legitimate for a paper design (the
> scheduler is explicitly deferred as net-new), but lower-confidence than the `suite.py`/`fabric` file:line
> claims. Reading `gpu.py` would strengthen D; the task does not require it.

---

## Part A — the existing machinery (Observed, with file:line evidence)

### A1. The role concept already exists — `ROLE_REGISTRY` (`runtime/suite.py:929-958`)
A **role** is defined in code as *"a named model-FUNCTION of the collective cognition: a specific job done
by a model that is NOT the conversational brain"* (`suite.py:914-916`). The brain (`rhm_config.model`) is
its own slot; roles are the AUXILIARY model-functions. `judge` is the first and only registered role today
(`suite.py:917`).

The `judge` role row (`suite.py:930-957`) already declares MOST of the target schema as fields:

| Target field | Field in `ROLE_REGISTRY['judge']` | Line | Wired today? |
|---|---|---|---|
| id | the dict key `"judge"` | 930 | yes |
| label / description | `label`, `description` | 931-933 | yes (status read) |
| trigger condition | `trigger` (descriptive string) | 934 | **DECLARED-ONLY** — see A6 |
| model binding | `default_model`, `default_base_url`, `recommended_model`, `recommended_base_url`, `env_model`, `env_url` | 935-944, 955 | yes (`resolve_role`) |
| knobs (max_tokens/temp) | `knobs`, `env_knobs` | 954, 956 | yes |
| thinking flag | `thinking` | 945 | yes (resolved) |
| output schema | `output` (a prose string `"one word: FINISHED | MORE"`) | 946 | **descriptive only — NOT enforced** |
| tools | `tools` (`[]`) | 947 | declared, not yet bound |
| input addresses (context) | `context` (prose: `"the utterance text only"`) | 948 | **descriptive only** |

The code's own comment (`suite.py:921-928`) names this exact generalisation as the intended growth path:
*"Each role DECLARES its full contract — Tim's 'triggers, configs like outputs/tools, contexts, and
whatever else' … WIRED-NOW fields … DECLARED-design fields (captured + designable, the growth path — NOT a
faked general engine): `trigger` is descriptive today … a general event→role trigger engine, and per-role
arbitrary tool-binding, come as their consuming code is built."* **This design IS that consuming code.**

### A2. Binding & resolution — `resolve_role` (`suite.py:3172-3196`)
A role resolves to the EFFECTIVE `{role, model, base_url, knobs, thinking, output, tools, context}` actually
used when it fires. Precedence (`suite.py:3184-3192`): **config binding > env override > declared default**,
and a `None` `default_model` falls back to the RHM brain (`cfg["model"]`, line 3185). Fail-loud on an
unknown role (`suite.py:3179-3180`, rule 8). Knobs merge declared-defaults ← env ← binding
(`suite.py:3188-3192`). So **swapping a role's model is a config change, never a code change** (3176-3177).

### A3. The `roles` config slot — bindings live in ONE dict (`suite.py:1162-1166`, `1217-1242`)
`rhm_config()["roles"]` is `{role_id: {model?, base_url?, knobs?, ...}}` (`suite.py:1166`). Stored as ONE
dict *"so adding a role never touches the config whitelist"* (1164). `set_rhm_config` validates each role-id
against `ROLE_REGISTRY` (fail-loud on unknown, `suite.py:1222-1224`) and **deep-merges three levels**
(siblings, per-role keys, the `knobs` sub-dict) so a partial update never wipes a sibling role or another
knob (`suite.py:1227-1242`). `roles()` (`suite.py:3158-3170`) is the registry-as-status read the config lab
renders: per role it returns the declared contract + current binding + `effective` resolution.

### A4. The MODEL_KNOBS catalog (`suite.py:997-1011`) + `knobs_for` (`suite.py:3198-3221`)
A declarative catalog of per-request knobs (temperature/max_tokens/top_p/tools/thinking/structured_output),
emitted in the **node config_schema shape** (`{type,label,default,min?,max?,options?}`) so the UI renders
model-knobs with the SAME `NodeConfigForm` it renders node config (3199-3205). The `structured_output` knob
(`suite.py:1008-1010`) already declares options `["none","json","json_schema"]` — **but it is `applies:
"declared"` (not wired into the transport); see C2.** `tools` capability is PROBED live (3216).

### A5. The judge itself — `is_finished_thought` (`suite.py:3252-3294`) + the endpoint
- Resolves the `judge` role: `r = self.resolve_role("judge")` (`suite.py:3275`).
- Builds a FIXED two-message prompt — `sys_p` hardcoded (`suite.py:3277-3279`) + the utterance
  (`suite.py:3280-3281`). **The prompt template lives in the consuming code, not in the registry.**
- Calls `client.complete(transport.openai_transport(base_url=r["base_url"], …), msgs, model=r["model"],
  max_tokens=r["knobs"].get("max_tokens", 2048), temperature=…)` (`suite.py:3283-3286`).
- **Output handling is substring-match, NOT schema-validated:** `verdict = "FINISHED" if "finish" in
  (out or "").strip().lower() else "MORE"` (`suite.py:3288`). It does NOT pass `schema=` to `complete()`
  (so `complete()`'s validate/retry path at `client.py:75-87` is unused here).
- Emits a G7 run-record (`emit_run_record("judge", ms, model=…, verdict=…)`, `suite.py:3292`).
- Fail-loud: transport/empty errors PROPAGATE (`FabricError`); the explicit fallback is the manual
  push-to-talk toggle SURFACED to the operator, never a silent silence-timer degrade (3266-3269).

**Endpoint** (`runtime/bridge.py:834-836`): `POST /api/voice/finished-thought {text}` →
`SUITE.is_finished_thought(b.get("text",""))` → JSON. The trigger is the **voice circuit** calling this on a
VAD pause during always-listen (`suite.py:934`; `voice/stt.py:222`). There is **no role scheduler** — the
judge is a synchronous bridge call. (Co-residence note in D2 below.)

### A6. Trigger today is descriptive; the in-repo trigger PATTERN is `VerbSpec.predicate`
The judge's `trigger` field (`suite.py:934`) is a prose string — the actual trigger is the hardcoded
endpoint call. The repo's working "fire-when-condition-holds" PATTERN lives in **`RHM_VERB_SPECS`**
(`suite.py:2012-2037`): each `VerbSpec` carries a **mode-set** + a `predicate(ctx)` lambda
(e.g. `lambda ctx: ctx.get("graph_nonempty", False)`, `suite.py:2014`). `available_verbs(mode, ctx)`
(`suite.py:2113-2120`) returns verbs whose spec lists the current mode AND whose predicate holds against the
live `_affordance_context` (`suite.py:2090-2111`, all derived from existing `state()`/`now()`/focus reads).
**This is the reusable pattern for a role's `mode-dependence` + `trigger condition`.**

### A7. The address → resolve → inject path (Observed) — and the judge BYPASSES it
> [!warning] Critical nuance
> **The judge does NOT resolve context.** Its declared context is *"the utterance text only (no system
> grounding)"* (`suite.py:948`), and `is_finished_thought` builds a fixed prompt that never touches the
> addressing path. Giving a role `input addresses` = wiring it INTO machinery the judge currently bypasses.

The address→resolve→inject path lives in the RHM `chat()` lineage:
1. `chat()` (`suite.py:3333`) builds the system prompt then appends `self._chat_context(graph_id, focus)`
   (`suite.py:3409`).
2. `_chat_context` (`suite.py:1322-1462`) assembles compact LIVE ground truth — graph/nodes/models/modes/
   verbs/inbox/panels/recent-events (`suite.py:1385-1404`) — plus, from the operator's `focus.selected`:
   - a `ui://` address → an "OPERATOR IS INDICATING" block via `_describe_ui_address` (`suite.py:1417-1435`,
     `1464-1498`), which also SETS the backend-held locus `self._current_locus = indicated[-1]`
     (`suite.py:1435`).
   - a canvas node-id → the co-presence block (`suite.py:1436-1445`).
3. `current_locus()` (`suite.py:1500-1512`) is the read seam for "where the operator IS".
4. `_resolve_context_at(self.current_locus(), graph_id=…, intent=…)` (called `suite.py:1461`) is the
   **address-keyed resolution** (R2, `suite.py:1514+`): gathers info attached to the locus + its ancestors
   (`_r2_ancestors`, `suite.py:1629`) — I6 annotations, I7 chats, addressed events, X6 `run://` versions —
   scored by `_r2_score` (`suite.py:1595-1627`): recency (`R2_LAMBDA`) · proximity (`address_tree_distance`,
   `suite.py:1574-1593`) · pin · X13 semantic-relevance-to-intent, **bounded by `R2_BUDGET=4000` chars**
   (`suite.py:1569`) so it cannot flood the window.

**So the addressing substrate for a role's `input addresses` ALREADY EXISTS** — `_resolve_context_at` (read
side) + the addressed store / event log (write side). It is just not yet exposed as a per-role declarable
field.

### A8. Output destination + render hint — the in-repo precedents
- **Output destination today:** the judge's output is the HTTP response (`bridge.py:836`) + a run-record
  event (`suite.py:3292`). The general write-side primitives that exist: the **addressed content store**
  (`set_ref`/content-addressed), the **append-only event log** (`_emit`/`_emit_durable`,
  `emit_run_record` `suite.py:296-306`), the **surfaced/inbox** (`surface_review` → a `build_result_review`
  item, per the wire). A role's `output destination` would name one of these — reuse, not net-new mechanism.
- **Render hint today:** none per-role. The precedent is the **node config_schema / MODEL_KNOBS emit-shape**
  (`{type,label,…}`, A4) the UI already renders generically, and the S1 UI registry's `represents`/`title`
  rows (`suite.py:1491-1497`).

### A9. Structured output — the enforcement gap (load-bearing finding)
- The transports emit ONLY `response_format: {type: "json_object"}` (plain JSON mode) — and only when
  `opts["schema"]` is set or `opts["json"]` is truthy (`fabric/transport.py:37-38` for `openai_transport`;
  `:67-68` for `openai_tools_transport`). **Neither emits `json_schema`.**
- `client.complete` (`fabric/client.py:54-89`) DOES accept a Pydantic `schema=` and runs parse(+repair)→
  validate→**retry** (`client.py:75-87`). This validate/retry loop EXISTS and is reusable.
- **But the judge uses neither** — it substring-matches `"finish"` (`suite.py:3288`) and passes no schema.
- The benchmark sheet confirms the day-one local 4B (`cyankiwi/Qwen3.5-4B-AWQ-4bit`, the judge's
  `recommended_model` at `suite.py:940`) does **`response_format: {type: json_schema, json_schema: {...}}`
  reliably**: *"All 3 prompts produced valid, schema-conforming JSON … Reliable for production. Use
  `response_format: json_schema` for any structured output task"* (`~/vllm-tests/BENCHMARK_FACTSHEET.md:83-96`).

**Conclusion:** enforcing per-role structured JSON is **net-new in the transport** (add a `json_schema`
branch), **reuse in the client** (existing validate/retry). The judge is a MIGRATION TARGET for this, not
the template for it.

---

## Part B — the design: a generalised Role Registry (Inferred / proposed, NOT built)

### B0. Stance — additive to `ROLE_REGISTRY`, completing the declared growth path
We do NOT create a new registry. We **widen the existing `ROLE_REGISTRY` rows** to carry the full schema,
build the **consuming machinery** the comment at `suite.py:921-928` says comes "as its consuming code is
built", and **migrate `judge`** onto it as the first proof. One source (rule 3); schema-additive (rule 2 —
every new field optional, behaviour byte-for-byte for `judge` until its row opts in).

### B1. Why a ROLE and not just a node-type (resolve the convergence head-on)
The target schema (`trigger / input addresses / output destination`) maps almost exactly onto the repo's
reactive **node-type** primitive (PORTS, fires when input addresses resolve, run→output address — see the
scheduler in `runtime/AGENTS.md`). State the distinction explicitly:

- A **node-type** is an OPERATOR-COMPOSED unit on a canvas graph — placed, wired, run by the scheduler as
  part of a graph the operator authored.
- A **role** is an AUXILIARY model-function of the *collective cognition itself* (`suite.py:914-916`) — it
  is part of the system's standing apparatus (like the judge on the voice hot-path), NOT a graph the
  operator drew. It fires on SYSTEM events (a VAD pause, an inbox arrival, a turn), not on graph-address
  resolution.

So a role REUSES the addressing/scheduling CONCEPTS (address→resolve→inject; fire-when-condition-holds) but
is a distinct registry because its lifecycle is the cognition's, not a graph's. This mirrors how the RHM
verbs (`RHM_VERB_SPECS`) are a separate registry from node-types for the same reason.

### B2. Proposed role schema (each field: reuse anchor or net-new)
```python
ROLE_REGISTRY = {
  "<role_id>": {
    # --- IDENTITY (exists) ---
    "label": str, "description": str,            # suite.py:931-933 — reuse

    # --- PROMPT TEMPLATE (net-new field; LIFTED from consuming code) ---
    # The system prompt + the user-message template with {placeholders} filled from resolved
    # input-addresses. Today this lives as `sys_p` inside is_finished_thought (suite.py:3277-3281).
    "prompt": {"system": str, "user_template": str},   # NET-NEW field, reuse f-string fill

    # --- INPUT ADDRESSES (net-new field; reuse the resolve path) ---
    # An ordered list of context sources. "$utterance" / "$intent" = call-arg passthrough (judge today);
    # a ui:// / run:// / store address → resolved via _resolve_context_at (suite.py:1461) bounded by a
    # per-role budget. Empty list = no system grounding (judge's "utterance text only", suite.py:948).
    "input_addresses": [str],                    # NET-NEW field; reuse _resolve_context_at

    # --- OUTPUT JSON SCHEMA (net-new field; reuse client validate/retry + NEW transport branch) ---
    # A JSON schema (or a Pydantic model name) the model MUST conform to. Enforced via
    # response_format:{type:json_schema} (NET-NEW in transport) + complete()'s validate/retry (EXISTS).
    # judge's "output": "one word: FINISHED|MORE" (suite.py:946) becomes {verdict: enum[FINISHED,MORE]}.
    "output_schema": dict | None,                # NET-NEW field; reuse client.py:75-87 + transport branch

    # --- TRIGGER CONDITION + MODE-DEPENDENCE (net-new field; reuse the VerbSpec pattern) ---
    # modes: the presence-mode set this role is active in (suite.py:2119 pattern).
    # trigger: a named system EVENT-kind + an optional predicate(ctx) lambda (suite.py:2014 pattern).
    "modes": tuple,                              # NET-NEW field; reuse available_verbs() mode-set
    "trigger": {"event": str, "predicate": "lambda ctx: ..."},  # NET-NEW; reuse VerbSpec.predicate

    # --- MODEL BINDING + KNOBS (exists) ---
    "default_model": str | None, "default_base_url": str | None,   # suite.py:935-939 — reuse
    "recommended_model": str, "recommended_base_url": str,         # suite.py:940-944 — reuse
    "thinking": bool, "knobs": dict,                               # suite.py:945,954 — reuse
    "env_model": str, "env_url": str, "env_knobs": dict,           # suite.py:955-956 — reuse

    # --- OUTPUT DESTINATION (net-new field; reuse the write primitives) ---
    # WHERE the validated JSON goes: "response" (HTTP, judge today) | "event":<kind> (emit/emit_durable)
    # | "store":<address-template> (set_ref) | "surface":<lane> (surface_review). One of the EXISTING
    # write seams (suite.py:296-306, set_ref, surface_review) — never a parallel sink.
    "output_destination": dict,                  # NET-NEW field; reuse existing write seams

    # --- RENDER HINT (net-new field; reuse node config_schema emit-shape) ---
    # How the surface should present this role's output (a chip / a card / a status pill / silent).
    "render": dict | None,                       # NET-NEW field; reuse the {type,label,...} emit-shape
  },
}
```

### B3. The role-RUN function (net-new; generalises `is_finished_thought`)
A single generic `run_role(role_id, **call_args) -> dict` that:
1. `spec = ROLE_REGISTRY[role_id]`; `r = resolve_role(role_id)` (**reuse** `suite.py:3172`).
2. Resolve `input_addresses`: `$`-args from `call_args`; addresses via `_resolve_context_at`
   (**reuse** `suite.py:1461`) under a per-role budget (reuse the `R2_BUDGET` pattern, `suite.py:1569`).
3. Fill the prompt template (**net-new**, trivial f-string fill of `spec["prompt"]`).
4. Call `client.complete(transport.openai_transport(...), msgs, model=r["model"], schema=<from
   output_schema>, **r["knobs"])` — passing `schema=` so the **EXISTING** validate/retry runs
   (**reuse** `client.py:75-87`); the transport emits `response_format:{type:json_schema}` (**net-new**, C2).
5. Route the validated dict to `output_destination` (**reuse** the write seam).
6. `emit_run_record(role_id, ms, model=…, **conditions)` (**reuse** `suite.py:296`).

`is_finished_thought` becomes a thin wrapper: `return run_role("judge", utterance=text)`, with the `judge`
row gaining `output_schema={verdict: enum}`, `prompt`, `input_addresses=["$utterance"]`,
`output_destination={"kind":"response"}`.

> [!note] Migration caveat — strict schema removes a deliberate leniency
> Today the judge substring-matches `"finish"` *anywhere* precisely because that is *"robust to a little
> thinking"* (`suite.py:3264`). A strict `output_schema={verdict: enum[FINISHED,MORE]}` enforced via
> `json_schema` is **behaviour-equivalent for a no-think model (the recommended 4B)** but **STRICTER for the
> thinking-model brain-fallback** the judge defaults to (`default_model=None` → the reasoning brain,
> `suite.py:935,949-953`): a reasoner emitting reasoning tokens before the verdict would fail a strict
> schema. So migrating `judge` to a strict schema must either keep the no-think model bound OR keep the
> lenient substring path as the fallback decoder for thinking models — do not silently trade away the
> deliberate robustness.

### B4. The trigger ENGINE (net-new; the "concurrent" half)
Today there is no role scheduler — the judge is a synchronous bridge call (A5). A general engine:
- A role with `trigger.event = "<kind>"` is invoked when an event of that kind is appended to the log AND
  its `predicate(_affordance_context())` holds AND the current `mode ∈ spec["modes"]` (**reuse** the exact
  `available_verbs` gate, `suite.py:2113-2120`).
- Synchronous endpoint triggers (the judge's `POST /api/voice/finished-thought`) stay as-is — a role can be
  BOTH endpoint-invokable and event-triggered. The engine is additive.

---

## Part C — structured-JSON enforcement (the load-bearing build)

### C1. Reuse: `complete()` already validates + retries (`fabric/client.py:75-87`)
Pass `schema=<PydanticModel>` and `complete()` parses(+repairs)→validates→retries on mismatch. No change
needed to use it; the judge just never did.

### C2. Net-new: a `json_schema` branch in the transport
`openai_transport` / `openai_tools_transport` (`transport.py:37-38`, `:67-68`) emit only
`{type:"json_object"}`. Add (schema-additive): when `opts["json_schema"]` is present, emit
`response_format = {"type":"json_schema", "json_schema": {"name": <role_id>, "schema": <dict>}}`. Proven
reliable on the day-one local 4B per `~/vllm-tests/BENCHMARK_FACTSHEET.md:83-96`. Keep the
`{type:json_object}` path for endpoints that don't support `json_schema` (fail-loud, never silent — rule 4):
probe-or-declare per model (the `structured_output` `MODEL_KNOBS` row already declares the
`none/json/json_schema` axis, `suite.py:1008-1010`).

### C3. Net-new wiring already half-declared
The `structured_output` knob (`suite.py:1008-1010`, options `none/json/json_schema`, `applies:"declared"`)
is the registry slot for this — it exists but is inert. C2 makes it live.

---

## Part D — the constraint that makes-or-breaks "concurrent": VRAM

> [!warning] The hard part is not the schema — it is N small models resident at once on a 16GB card.
The declarative registry is the easy half. **"Concurrent cognition" = concurrent RESIDENCY**, gated by the
VRAM resource-manager and the co-residence rule.

### D1. The single budget authority — `ops/cli/gpu.py`
Per `STATE.md` + `MAP.md`: `ops/cli/gpu.py` is the single VRAM budget/teardown authority (shared with
`voice/lifecycle.py`); it REFUSES a start that would blow card capacity, shows what's holding VRAM + what to
evict, and tears down orphan-safe via the unit cgroup. **Any role that binds a NON-brain model (e.g. the
judge's recommended resident 4B) must be a registered service in `ops/services.json` with a measured VRAM
cost, loaded through the resource-manager — never spun up ad hoc.** A role's `recommended_model` is a
PREFERENCE; binding it live requires the model resident, which the resource-manager owns (the judge row
already says exactly this, `suite.py:936-944`).

### D2. Co-residence is non-negotiable (`runtime/bridge.py:807-824`)
The finished-thought judge + the brain must run RESIDENT together (`bridge.py:807` — "non-negotiable"); the
brain's context is sized to a stored `coresident_brain_ctx` and shrunk+restarted BEFORE loading a voice
(`bridge.py:819-824`). **N concurrent roles multiply this constraint:** each resident role-model competes
for the same 16GB. The design MUST treat resident-role-set as a budgeted resource:
- **Tier the roles by residency:** (a) **brain-shared** roles (`default_model=None` → reuse the resident
  brain, zero extra VRAM — the judge's safe default, `suite.py:935`); (b) **co-resident small models**
  (a fast 4B held alongside the brain — VRAM-budgeted, resource-manager-owned); (c) **on-demand** roles
  (loaded on trigger, evicted after — accept the load latency where the hot-path doesn't forbid it).
- The role row should carry a residency tier (net-new field, deferrable) so the resource-manager can
  decide what stays warm. The **measured** `emit_run_record` rollups (`run_stats`, `suite.py:308`) +
  `services.json` VRAM/wake data are the inputs (introspective-data-building — the judge already emits its
  ms+model+verdict, `suite.py:3292`).

### D3. No role scheduler exists yet
There is no concurrent role runner today (A5/B4). Building one means an event-driven dispatch loop that
respects D1+D2 — fire a role only if its model is resident OR can be loaded within the role's latency
budget, else surface (fail-loud, never silent-skip — rule 4). This is the genuinely net-new system; the
registry schema is the declarative input to it.

---

## Part E — reuse-vs-net-new summary table

| Schema field | Reuse anchor (file:line) | Net-new |
|---|---|---|
| id | `ROLE_REGISTRY` dict key (`suite.py:930`) | — |
| prompt template | f-string fill; lives in code today (`suite.py:3277-3281`) | **field** (lift into registry) |
| input addresses | `_resolve_context_at`/R2 read path (`suite.py:1461`, `1514+`) | **field** + per-role budget |
| output JSON schema | `complete()` validate/retry (`client.py:75-87`); `structured_output` knob (`suite.py:1008`) | **field** + **transport `json_schema` branch (C2)** |
| trigger condition | `VerbSpec.predicate` + `_affordance_context` (`suite.py:2014`, `2090`) | **field** + **trigger ENGINE (B4)** |
| model binding | `resolve_role` precedence (`suite.py:3172-3196`), `roles` slot (`suite.py:1166`) | — (fully exists) |
| knobs | `knobs` resolution (`suite.py:3188-3192`), `MODEL_KNOBS` (`suite.py:997`) | — |
| mode-dependence | `available_verbs(mode,ctx)` mode-set (`suite.py:2113-2120`) | **field** (`modes` tuple) |
| output destination | `emit_run_record`/`_emit_durable` (`suite.py:296`), `set_ref`, `surface_review` | **field** (names a seam) |
| render hint | node config_schema emit-shape (`suite.py:997-1011`); S1 `represents` (`suite.py:1491`) | **field** |
| role RUN function | `is_finished_thought` (`suite.py:3252`) as the migration template | **generic `run_role` (B3)** |
| **concurrent residency** | `ops/cli/gpu.py` budget authority; co-residence (`bridge.py:807`); `run_stats` (`suite.py:308`) | **residency tier + role scheduler (D2/D3)** |

**Net-new is concentrated in three places:** (1) the transport `json_schema` branch (small, proven by the
benchmark), (2) the generic `run_role` + the role rows' new declarative fields (additive to `ROLE_REGISTRY`),
(3) the **trigger/residency scheduler** — the genuinely new system, and the one the "concurrent" vision
lives or dies on (VRAM-bounded on the 16GB card).

---

## Open questions to put to the operator (not to decide silently)
- **A** (depth): trace the voice circuit end-to-end (`voice/stt.py` → `/api/voice/finished-thought` →
  judge) to confirm the exact trigger cadence + how many judge calls per spoken turn — this sizes the
  hot-path latency budget that decides which roles can be on-demand vs must be resident.
- **B** (mapping): inventory the candidate roles beyond `judge` (e.g. an intent-classifier, a
  context-relevance ranker, a turn-grader, a safety/abstain gate) and which residency tier each wants —
  this is what turns "many concurrent roles" from one example into the actual set.
- **C** (artifact): draft the concrete additive `ROLE_REGISTRY` field-set + the `run_role` signature + the
  transport `json_schema` patch as a build-ready spec (tentative; for correction), so the registry half can
  be built independently of the harder scheduler half.
- **D** (the crux): design the VRAM-bounded role scheduler against `ops/cli/gpu.py` + the co-residence rule
  first — because it is the constraint everything else composes against, and the schema is its input.
