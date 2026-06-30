# Authoring Surface — FE Handoff (Concurrent Cognition C7.4/C7.5)

**Read this first.** You are the front-end session for the **cognition AUTHORING surface** — the operator
creating/managing **roles, rules, modes/casts, structured outputs** on the canvas, composably. A separate
session (this one) built the **entire authoring BACKEND** so your job is to build the UX, not the plumbing:
every write path, validate, test, and select-query is a clean `/api` endpoint, tested and live. This doc
maps every endpoint, every data shape, the UX surfaces to extend, the laws to honour, and what already
exists to reuse.

> **Status of the backend:** built + verified by use against the resident 4B on the worktree bridge `:8772`
> (branch `concurrent-cognition`, NOT merged). `tests/authoring_acceptance.py` (42 checks) is green. The
> create→approve→live loop, the gate, validate (good+bad), the dry-runs, the selects, and delete were all
> proven through the real operator endpoints. The backend is `runtime/authoring.py` + the authoring methods
> in `runtime/suite.py` (search "AUTHORING BACKEND") + the endpoints in `runtime/bridge.py`.

---

## A · The conceptual model — authoring cognition IS composing a node graph

The cognition layer is a **dual-use substrate**: the SAME mechanism the app uses for node-graphs is what
the operator uses to compose cognition. The mental model the surface should make visible:

```
  utterance ─▶ [role] ─emits structured output▶ run://<turn>/<role>
                  │                                    │
                  └─ rule reads resolved values ──▶ DESTINATION (inject·chain·address·surface·lane)
                                                       │
                            the reply assembles as staged PARTS, enriched by what resolved
```

- A **ROLE** is a small model-function: it reads the utterance (and other roles' outputs) and emits a
  **structured output** (a Pydantic schema). A role is a file in `roles/<id>.py`. Authoring a role = defining
  its prompt + its output FIELDS + which casts (modes) it's in + what it requires of a model.
- A **RULE** is a **declared, deterministic** routing decision (a data-AST, never code): it reads resolved
  role outputs and routes a value to one of **5 destinations**. The rule grammar is **closed and renderable**
  (it draws as a short edge-badge).
- A **MODE** picks the **cast** (which roles fire) + the staging grain. (Modes/casts are existing registries
  surfaced in `/api/cognition_info`; this handoff focuses on roles+rules authoring.)

**This is the existing object_info/ui_info pattern** (`06-rendering.md §B.3`): the backend serializes the
cognition registries through `build_cognition_info` (the sibling of `build_object_info`), and the FE is a
**generic renderer** — *"drop a role/rule → it appears live, no FE code."* Your authoring forms are the
existing **NodeConfigForm / Inspector** pattern applied to roles+rules instead of node-types.

---

## B · Every endpoint (request → response JSON)

### B.1 · READ (what already exists — the view side, L-fe/L-fe-be)

| Endpoint | Request | Response (shape) |
|---|---|---|
| `GET /api/cognition_info` | — | the full cognition registry projection (roles, rules, edge_kinds, thought_shapes, activation_contexts, **rule_ops**, **destination_kinds**, casts, node_states). See §C.1. The single read-truth for the authoring surface. |
| `GET /api/stream` (SSE) | — | the live event stream. `cognition.*` lifecycle events fire as a staged turn runs (see §C.5). The FE already has a `cognition.*` dispatch branch (`useAppController.ts:227 foldCognition`). |

### B.2 · WRITE — roles (propose-not-apply; apply rides the EXISTING operator endpoints)

| Endpoint | Request body | Response |
|---|---|---|
| `POST /api/cognition/role/propose` | `{"spec": <RoleFieldSpec>, "model"?: str}` — author a NEW role. `spec` is the field-set (§C.2). OR a brain-draft: `{"spec": {"id"?, "brief": "<NL description>"}}`. | `{"id": "s<N>-role_build", "role_id": str, "source": "<rendered .py source>"}` OR `{"needs": str, "id": "<question sid>"}` if the brain hit unregistered ground. **Surfaces for approval — NOT applied.** |
| `POST /api/cognition/role/edit` | `{"role_id": str, "spec": <RoleFieldSpec>, "model"?: str}` | `{"id": str, "role_id": str, "source": str, "edit": true}` OR `{"protected": true, "needs": str, "id": str}` if the role is protected. **Surfaces a replacement.** |
| `POST /api/cognition/role/delete` | `{"role_id": str}` | `{"id": str, "role_id": str, "delete": true}` OR `{"protected": true, "needs": str, "id": str}`. **Surfaces a removal.** |
| `POST /api/resolve` *(EXISTING, operator-only)* | `{"id": "<sid>", "choice": "approve"\|"reject", "reason"?: str}` | `{"ok": true, "verdict": {...}, "surfaced": [...]}` — the operator APPROVES the surfaced role here. |
| `POST /api/apply` *(EXISTING)* | `{"id": "<sid>"}` | `{"ok": bool, "path": str, "kind": "role_build"\|"role_delete", "error": str\|null, "types": [...]}` — applies the approved role (writes the file, git-commits, the role goes LIVE in `/api/cognition_info`). Routes by action class to the role write-path (never mis-writes to `nodes/`). |

**THE LOOP (proven by use):** `role/propose` → (operator) `/api/resolve` approve → `/api/apply` → the role
appears in `/api/cognition_info` and in `casts[<mode>]`. Before approve it is NOT live; an apply WITHOUT an
operator approve is REFUSED (HTTP 400, `GovernanceError`).

### B.3 · WRITE — rules (validate/dry-run are pure; attach/detach surface like an edit)

| Endpoint | Request body | Response |
|---|---|---|
| `POST /api/cognition/rule/validate` | `{"ast": <RuleAST>, "destination"?: str}` | `{"ok": bool, "errors": [str], "references": [str], "destination": str\|null, "destination_ok": bool\|null, "renderable": bool, "when_text": str\|null, "depth": int\|null}`. **Live validation for the rule-builder.** |
| `POST /api/cognition/rule/dry_run` | `{"ast": <RuleAST>, "sample_resolved": {role: {field: val}}, "destination"?: str (default "inject"), "params"?: {}, "on_missing"?: "raise"\|"skip"}` | `{"ok": bool, "decision": {rule, fire, destination, value, params, reason}, "when_text": str}` OR `{"ok": false, "error": str}`. **"With these inputs → this routes."** |
| `POST /api/cognition/rule/attach` | `{"role_id": str, "rule": <RuleDecl>}` | same as `role/edit` (surfaces a `role_build` with the rule added). |
| `POST /api/cognition/rule/detach` | `{"role_id": str, "rule_id": str}` | same as `role/edit` (surfaces a `role_build` with the rule removed). |

### B.4 · TEST / preview (fire the resident swarm; non-mutating to conversation state)

> **Note:** `preview_turn` does NOT touch chat history/thread/training-signal, but it IS a real staged turn —
> it emits the `cognition.*` events to the event log and writes role outputs to `run://<turn>/<role>` CAS
> (turn-scoped, exactly like a live turn). So a preview is **observable on the live `/api/stream` SSE + the
> cognition view** (it lights the river/dots). That's intended (it's what `cognition_events` reflects), just
> not zero-side-effect on the stream. `dry_run_role` is fully isolated (one role, no turn, no events).

| Endpoint | Request body | Response |
|---|---|---|
| `POST /api/cognition/role/dry_run` | `{"role_id": str}` OR `{"fields": <RoleFieldSpec>}` + `{"utterance": str, "model"?, "base_url"?}` | `{"role_id": str, "output": {<the validated structured output>}}`. **Test a role (registered OR a never-saved draft) in isolation.** No file written. |
| `POST /api/cognition/preview_turn` | `{"utterance": str, "mode"?: str, "graph_id"?: str}` | `{"utterance": str, "mode": str, "parts": [{part, text, final, staged}], "cognition_events": [<cognition.* events>], "n_parts": int}`. **Preview a full staged turn** (mode set + restored; the cast that fired + the injections + the parts). **NON-MUTATING:** it fires a REAL staged turn (`chat_parts(persist=False)`) but does NOT append to the live chat history / thread / training_signal — safe to call repeatedly while authoring. (Verified live: chat-history delta = 0.) |

### B.5 · SELECT (populate every dropdown from truth — never hardcode)

| Endpoint | Request | Response |
|---|---|---|
| `GET /api/cognition/models_for_role?requires=chat,json` | query: `requires` (comma-sep capability tags) | `{"requires": [str], "models": [str], "providers": {provider_id: {model, base_url, provides:[str]}}}`. **The model-select** — only models whose `provides ⊇ requires`. |
| `GET /api/cognition/inputs` | — | `{"utterance": "utterance", "roles": [str], "role_addresses": ["run://<turn>/<role>"], "context_variables": [str]}`. **The input-wiring select** (what a role/rule can read). |
| `GET /api/cognition/field_types` | — | `{"<type>": {"kind": str, "gloss": str, "annotation"?: str, "params"?: [str]}}` for the **live closed set** (read it from the endpoint — single-sourced from `runtime/authoring.py:FIELD_TYPES` + aliases; the flat scalars PLUS the richer kinds `enum`/`object`/`list[object]`, never a frozen subset). **The schema-editor's field-type dropdown.** |

**Verified live response examples** (curled against `:8772`):

```jsonc
// GET /api/cognition/field_types
{"str":{"annotation":"str","gloss":"a text field"}, "int":{...}, "float":{...}, "bool":{...},
 "list[str]":{"annotation":"list[str]","gloss":"a list of strings"}, "list[int]":{...}}

// GET /api/cognition/inputs
{"utterance":"utterance",
 "roles":["check","connect","focus","ground","recall","verify_jury","voice"],
 "role_addresses":["run://<turn>/check", ...],
 "context_variables":["recall_slice","rules","run_state","selection","trajectory","trial_*"]}

// GET /api/cognition/models_for_role?requires=chat,json
{"requires":["chat","json"], "models":["cyankiwi/Qwen3.5-4B-AWQ-4bit","deepseek-v4-pro:cloud"],
 "providers":{"resident:chat-4b":{"model":"cyankiwi/Qwen3.5-4B-AWQ-4bit",
              "base_url":"http://127.0.0.1:8000/v1","provides":["chat","json","tools","fast","no-think"]}}}

// POST /api/cognition/rule/validate {"ast":{"op":"and","args":[{"op":"field","path":"recall.relevant"},
//                                          {"op":"field","path":"ground.in_scope"}]},"destination":"inject"}
{"ok":true,"errors":[],"references":["ground","recall"],"destination":"inject","destination_ok":true,
 "renderable":true,"when_text":"(recall.relevant AND ground.in_scope)","depth":2}

// POST /api/cognition/rule/validate {... "destination":"resolve"}  ← the floor
{"ok":false,"errors":["destination 'resolve' must be one of ['address','chain','inject','lane','surface']
 and NEVER one of ('resolve','approve','dispatch') (the claude -p floor is lead-only)."],
 "destination_ok":false, ...}

// POST /api/cognition/rule/dry_run {"ast":{"op":"field","path":"recall.relevant"},
//                                   "sample_resolved":{"recall":{"relevant":true}},"destination":"inject"}
{"ok":true,"decision":{"rule":"dry-run","fire":true,"destination":"inject","value":true,"params":{},
 "reason":"dry-run: recall.relevant → FIRE"},"when_text":"recall.relevant"}

// POST /api/cognition/role/dry_run {"fields":{"id":"probe_role","prompt_template":"...","output_fields":[
//                                  {"name":"tone","type":"str"}]},"utterance":"I love this!"}
{"role_id":"probe_role","output":{"tone":"positive"}}

// POST /api/cognition/role/propose {"spec":{"id":"authtest_role","prompt_template":"...","output_fields":[
//                                  {"name":"intent","type":"str"}],"mode_scope":["listening"],"requires":["chat","json"]}}
{"id":"s90-role_build","role_id":"authtest_role","source":"\"\"\"roles/authtest_role.py ...\nclass AuthtestRoleOut(BaseModel):\n    intent: str = ''\n\nROLE = {...}\n"}
```

---

## C · The data shapes

### C.1 · `/api/cognition_info` (the read-truth — `contracts/cognition_info.py:146 build_cognition_info`)

```jsonc
{
  "schema_ver": int,
  "roles": { "<id>": {                  // contracts/cognition_info.py:100 _serialize_role
      "id", "label", "description",
      "can_fire": bool,                 // has prompt_template + output_schema (a fire-able role)
      "is_jury": bool, "draws": int,    // a jury = N varied draws + a verdict
      "mode_scope": [str],              // the casts this role is part of
      "requires": [str],                // the capability query (role.requires ⊆ model.provides)
      "trigger", "render_hint",
      "rules": [ <RuleDecl or descriptive rule> ]   // the role's declared routing rules (DATA)
  }},
  "rules":      { "<id>": {id, label, when, when_text, destination, params, inputs, on_missing, depth} },
  "edge_kinds": { "<kind>": "<gloss>" },            // the C1.3 edge vocabulary (chain/inject labels)
  "thought_shapes": { "<archetype>": {...} },       // the ~5 reply shapes
  "activation_contexts": { "<ctx>": {...} },        // when a cast fires (per-turn/background/sense/rollup)
  "rule_ops":   { "<op>": "<gloss>" },              // THE CLOSED RULE GRAMMAR (the badge legend)
  "destination_kinds": { "<dest>": "<gloss>" },     // THE 5 ROUTING DESTINATIONS (the floor)
  "casts":      { "<mode>": [role_id] },            // which roles fire in which mode
  "node_states": [ {id, label, means, applies_to, derived_when} ]  // the status-dot vocabulary
}
```

### C.2 · `RoleFieldSpec` — what `role/propose`/`role/edit`/`role/dry_run` take (the AUTHORING shape)

```jsonc
{
  "id": "my_role",                      // REQUIRED — plain lower identifier (becomes the file name + ROLE id)
  "label": "My Role",                   // operator-facing
  "description": "what it does",
  "prompt_template": "You are ...",     // the system prompt (present ⇒ the role can FIRE)
  "output_fields": [                    // C7.5 — the STRUCTURED OUTPUT, defined as fields (→ a BaseModel)
    {"name": "relevant", "type": "bool", "description": "is it relevant"},
    {"name": "snippet",  "type": "str"}
  ],
  "input_addresses": ["utterance"],     // declared inputs (DATA; from GET /api/cognition/inputs)
  "mode_scope": ["listening"],          // the casts this role is in (modes from cognition_info.casts)
  "trigger": "per-turn",                // descriptive
  "requires": ["chat", "json"],         // the capability query (drives GET /api/cognition/models_for_role)
  "rules": [ <RuleDecl>, ... ]          // declared routing rules attached to this role (validated)
}
```
- `type` ∈ the **closed field-type set** — read it LIVE from `GET /api/cognition/field_types` (single-sourced
  from `runtime/authoring.py:FIELD_TYPES` + aliases; the flat scalars PLUS the richer kinds `enum`/`object`/`list[object]`,
  never a frozen subset here). An unknown type fails loud at propose. A role with no `output_fields` gets a minimal `{ok: bool}` schema.
- The backend renders this to a real `roles/<id>.py` module (`render_role_source`, `runtime/authoring.py`) and
  **gates it by importing it in a temp dir before any write** — a malformed role NEVER reaches the live tree.

### C.3 · `RuleAST` — the rule condition grammar (`runtime/rules.py` `RULE_OPS`, closed)

A rule's condition is a **data-AST** (a dict tree), never a string/code. The ops (all in `cognition_info.rule_ops`):

```jsonc
// leaves
{"op": "field", "path": "recall.relevant"}     // dot-path read of a resolved role output
{"op": "lit",   "value": 0.5}                   // a static literal (scalar or list of scalars)
// boolean       {"op":"and"|"or", "args":[...]}      {"op":"not","args":[X]}
// comparison    {"op":"eq"|"ne"|"lt"|"le"|"gt"|"ge", "args":[A, B]}
// arithmetic    {"op":"add"|"sub"|"mul", "args":[A, B]}
// membership    {"op":"in", "args":[X, LIST]}        {"op":"contains", "args":[CONTAINER, X]}
```
**There is NO `now`/`random`/`call`/IO op — they cannot be expressed** (determinism is structural). The AST
is **depth-capped** (`MAX_RULE_DEPTH`) so it stays a legible edge-badge; heavier logic decomposes into an
upstream role (the rule-vs-role classifier). `validate_rule` returns `references` (the role-ids the rule
reads — the first path segments), `when_text` (the rendered badge string), `depth`, and `renderable`.

### C.4 · `RuleDecl` — a full declared rule (for `rule/attach`, and `role.rules[]`)

```jsonc
{
  "id": "recall-injects",
  "label": "recall.relevant AND ground.in_scope",
  "when": <RuleAST>,                               // the condition
  "destination": "inject",                          // one of the 5 DESTINATION_KINDS (below) — NEVER resolve/approve/dispatch
  "params": {"value_path": "recall.snippet"},       // destination-specific (e.g. the routed value; chain_role for chain)
  "on_missing": "raise"                             // "raise" (fail loud) | "skip" (declared no-op on a pruned input)
}
```

### C.5 · The 5 `destination_kinds` (the routing destinations — `runtime/rules.py` `DESTINATION_KINDS`)

| kind | what it does | params |
|---|---|---|
| `inject` | inject the routed value into a later reply part (lands at `run://<turn>/inject/<rule>`) | `value_path` |
| `chain` | trigger a dependent role (the model runs in the ROLE, never the rule) | `chain_role` |
| `address` | land the value at a `run://` address for later (durable, no reply impact) | — |
| `surface` | surface to the inbox/decisions for the operator (an `ask`, `resolved=None`) — **NEVER a resolve** | — |
| `lane` | write to a named typed lane/channel (a `cognition.lane` event on the one log) | — |

**CRITICAL LAW (the floor):** a destination is **NEVER** `resolve`/`approve`/`dispatch` (`FORBIDDEN_DESTINATION_VERBS`).
The rule-builder UI must offer ONLY these 5 (read them from `cognition_info.destination_kinds`), and a rule
that tries a forbidden destination fails loud at validate.

### C.6 · The `cognition.*` lifecycle events (`contracts/cognition_info.py:52 COGNITION_EVENT_KINDS`)

Each event record carries `kind` (NOT `op`), `seq`, `ts`, `summary`, `address`, + payload:

```
cognition.turn.start  {turn_id, mode, shape, grain, cast[], address=ui://cognition/<turn>}
cognition.role.fire   {turn_id, role, model, address=run://<turn>/<role>}    // the dot goes 'firing'
cognition.role.ran    {turn_id, role, ok, ms, error?, address=run://<turn>/<role>}
cognition.inject      {turn_id, rule, source, role, into, chars, address=run://<turn>/<source>}
cognition.part        {turn_id, part, final, staged, address=ui://cognition/<turn>}
cognition.turn.done   {turn_id, total_ms, n_parts, n_roles, address=ui://cognition/<turn>}
cognition.wave        // the per-wave rollup (run_swarm telemetry; preserved, additive)
```
`preview_turn` returns these in `cognition_events` for a draft config; the live view already folds them
(`useAppController.ts:227`).

---

## D · The UX needed, mapped to the existing app surfaces

| Authoring affordance | Build by extending | Backend it drives |
|---|---|---|
| **Role palette** — the list of cognition roles (like the node palette), with a "+ new role" affordance, the facet (can_fire/jury/cast) by sight | `canvas/app/src/regions/Palette.tsx` (the node palette) + `regions/CognitionView.tsx` (the live role nodes) | reads `GET /api/cognition_info.roles`; "+ new" opens the role form (→ `role/propose`) |
| **Role config form** — edit a role's prompt, label, mode_scope, requires; the schema editor (below) | `regions/Inspector.tsx` + `components/NodeConfigForm.tsx` (the node config form — the SAME pattern, `06 §C` row "Config") | `role/propose` (new) / `role/edit` (existing) → surfaces; `models_for_role` populates the model picker from `requires`; `inputs` populates the read-wiring |
| **Schema editor** — define `output_fields` (name + type dropdown + description); add/remove rows | net-new sub-form inside the role config form | `field_types` populates the type dropdown; the fields go into `RoleFieldSpec.output_fields` |
| **Rule-builder** — an expression composer for the `when` AST (a small block/condition builder), the destination picker (the 5 kinds), live validation + the badge preview | **net-new** — an edge-badge expression composer. The closest existing analog is the Inspector config form; the AST is a small recursive block UI | `rule/validate` (live, on every edit — show errors + `when_text` + `references`); `rule/dry_run` (a "test with sample values" panel); `rule/attach`/`rule/detach` to save onto a role |
| **Create-from-canvas** (the propose→approve flow) | the existing inbox/surfaced flow — `regions/Inbox.tsx` + `ProposeAffordance.tsx` + the `/api/resolve` + `/api/apply` buttons | `role/propose` surfaces → the inbox shows it (a `role_build` item carrying `source`) → operator approves (`/api/resolve`) → `/api/apply` makes it live |
| **Test / preview affordance** — "test this role" (fire it on a sample utterance) and "preview a turn" (run a full staged turn for a draft config) | net-new test panel; the preview reuses the live `CognitionView` rendering for the returned events | `role/dry_run` (one role, draft or saved); `preview_turn` (full staged turn → parts + `cognition_events`) |
| **Scan directories → live structured output** (C7.5) | net-new; pairs a directory picker with the schema editor → roles that scan + emit structured output stream into the view | the structured-output half is `output_fields` → `role/propose`; the live-stream is the existing `cognition.*` SSE + `CognitionView`. *(The directory-scan source node is a downstream pairing — flag for the build; the structured-output authoring + live-stream rendering it depends on are DONE.)* |

**What exists to reuse (don't rebuild):**
- `regions/CognitionView.tsx` (214 lines) — the **live cognition VIEW** L-fe built (Pulse→River→Nodes). It
  already renders roles, the cast, injections, and the staged parts from `/api/cognition_info` +
  the `cognition.*` SSE. Your authoring forms extend it (add/edit), they don't replace it.
- `components/NodeConfigForm.tsx` — the config-form pattern (fields from a schema). The role config form is
  this pattern over a role's fields. (`06-rendering.md:118` names this reuse explicitly.)
- `regions/Palette.tsx`, `regions/Inspector.tsx` — the palette + inspector to extend for roles.
- `useAppController.ts:227 foldCognition` + the `cognition.*` SSE branch — the live event fold (mirrors the
  `decision.*` branch). `api.ts:154 cognitionInfo()` — the read fetch.
- `registryStore.ts` — the reflects-never-owns read-truth store (the `COGNITION_INFO` field).
- The inbox/surfaced flow (`regions/Inbox.tsx`, `/api/resolve`, `/api/apply`) — the propose→approve→apply UX.

**Net-new FE:** the rule-builder (the AST expression composer + the destination picker + live validate/dry-run),
the schema editor sub-form, the role "+ new"/edit form, the test/preview panel.

---

## E · The laws the UI MUST honour

1. **reflects-never-owns.** The canvas drives via addresses + endpoints; the BACKEND writes the role/rule
   files. The FE never writes a role file directly — it calls `role/propose` etc. (`AGENTS.md` rule 3 — one source).
2. **propose-not-apply.** Every write SURFACES for the operator (it returns a surfaced `id`); nothing is live
   until the operator approves (`/api/resolve`) and applies (`/api/apply`). The UI must show the surfaced
   item + its rendered `source` for review, and route approve→apply. **Never auto-apply.**
3. **The rule grammar is closed + renderable.** Offer ONLY the ops in `cognition_info.rule_ops` and the
   destinations in `cognition_info.destination_kinds` — never a free-text expression, never a 6th destination.
   Respect the depth cap (`validate_rule.renderable`: if false, the rule is too deep to draw — surface that).
4. **The claude-p / dispatch floor is LEAD-ONLY (C9.2).** A rule's destination is NEVER
   `resolve`/`approve`/`dispatch`. The rule-builder must not offer them; `validate_rule` refuses them
   (`destination_ok: false`). Authoring **surfaces**; the operator approves.
5. **run:// addressing.** A rule reads role outputs at `run://<turn>/<role>` (the `inputs`/`role_addresses`
   from `GET /api/cognition/inputs`). Never invent another scheme.
6. **Author from the registry, never invent** (`AGENTS.md` rule 8). Every dropdown (field types, models,
   inputs, modes, destinations, ops) comes from an endpoint, never a hardcoded FE list. A NEW model/role/
   field-type added to the backend appears in the dropdown automatically.
7. **Fail loud.** A malformed role/rule fails loud at validate/propose (HTTP 400 with the reason) — surface
   the error, never silently swallow or fabricate a success.
8. **Protected roles.** `role/edit`/`role/delete` on a runtime-imported role returns `{protected: true,
   needs: ...}` — show this as "needs Tim / can't edit from here", not an error.

---

## F · Where everything lives (backend, for cross-reference)

- **Pure renderer + gate:** `runtime/authoring.py` — `render_role_source` (fields→`.py`), `FIELD_TYPES`
  (the closed type registry), `gate_role_source`/`load_role_from_source` (validate-in-a-temp-dir).
- **The governed write-path:** `runtime/suite.py` — search **"AUTHORING BACKEND"**: `propose_role`,
  `apply_role`, `edit_role`, `delete_role`/`apply_role_delete`, `validate_rule`, `dry_run_rule`,
  `attach_rule`/`detach_rule`, `dry_run_role`, `preview_turn`, `models_for_role`, `available_inputs`,
  `field_types`. `PROTECTED_ROLES` is the runtime-imported set. `apply_surfaced` routes `role_build`/
  `role_delete` to the role write-path.
- **Governance:** `runtime/governance.py` — `role_build`/`role_delete` action classes (CONFIRM).
- **Endpoints:** `runtime/bridge.py` — `POST /api/cognition/{role/propose,role/edit,role/delete,role/dry_run,
  rule/validate,rule/dry_run,rule/attach,rule/detach,preview_turn}` + `GET /api/cognition/{models_for_role,
  inputs,field_types}`. Apply rides existing `/api/resolve` + `/api/apply`.
- **The view backend (read):** `contracts/cognition_info.py` (`build_cognition_info`, `_serialize_role`,
  `COGNITION_EVENT_KINDS`), `Suite.cognition_info()`, `GET /api/cognition_info`, the `cognition.*` SSE.
- **The rule engine (reused):** `runtime/rules.py` — `RULE_OPS`, `DESTINATION_KINDS`,
  `FORBIDDEN_DESTINATION_VERBS`, `validate_ast`, `evaluate`, `Rule`, `build_rule`, `route`.
- **The role registry:** `runtime/roles.py` (`RoleRegistry.discover` — file-discovered), `roles/*.py`.
- **The capability query (the model-select):** `ops/cli/capabilities.py` — `suitable_models`/`provides_for`/
  `role_can_bind`.
- **Tests (the by-use proofs):** `tests/authoring_acceptance.py`, `tests/cognition_governance_acceptance.py`
  (the floor), `tests/cognition_info_acceptance.py`, `tests/rules_acceptance.py`, `tests/roles_acceptance.py`.

> **To run the surface against the backend:** start the bridge `runtime/bridge.py <port>` (the worktree's
> verify bridge is `:8772`); the vite dev server proxies `/api` to it. The resident 4B at `:8000` is the
> model the swarm/dry-runs fire against (read-only).
