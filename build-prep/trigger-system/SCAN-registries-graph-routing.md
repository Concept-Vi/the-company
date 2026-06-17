# SCAN — Registries · Graph-MCP · Routing (for a reusable TRIGGER/HOOK system)

> Read-only scan of `/home/tim/company`. No code modified. Evidence-classified per Tim's
> bar: **Observed** = read directly in the file (file:line cited). **Inferred** = pattern-match,
> labelled as such. A handful of graph line-refs from a sub-agent are marked **sub-agent-reported**
> where not personally opened.
>
> **The spine of this doc (the finding):** A trigger = `event-kind → when-predicate → action`.
> All three halves **already exist in the codebase, scattered across three modules.** What is
> MISSING is the *binding*: a single file-discovered, MCP-exposed registry that ties an
> event-kind to a `RULE_OPS` predicate to a `DESTINATION_KINDS` action. The trigger system is
> a **unification of existing parts**, not a net-new mechanism.

---

## 0. THE ONE-SCREEN ANSWER

```
A TRIGGER ROW (the thing that does not yet exist as one declared unit):

   ┌─────────────────────────────────────────────────────────────────────┐
   │ trigger/<id>.py  →  TRIGGER = {                                       │
   │     id:          "<id>"          # == filename (addressable by file)  │
   │     event:       "<event-kind>"  # ← taxonomy EXISTS: activation.py   │
   │     when:        {<RULE_OPS AST>} # ← predicate lang EXISTS: rules.py │
   │     destination: "<dest-kind>"   # ← routing EXISTS: rules.py route() │
   │     params/why/priority ...                                           │
   │ }                                                                     │
   └─────────────────────────────────────────────────────────────────────┘
        │                    │                         │
   event taxonomy       predicate AST            action/routing
   (HALF #1 exists)     (HALF #2 exists)         (HALF #3 exists)
   activation.py:64     rules.py:65 RULE_OPS     rules.py:114 DEST_KINDS
   ACTIVATION_CONTEXTS  + validate_ast/evaluate  + route() rules.py:491
        │                    │                         │
        └──── the BINDING registry that joins all three ────┘  ← MISSING
              (file-discovered + MCP-exposed via mcp_face/tools/triggers.py)
```

**THE single most important REUSE target (import + call, never clone):** `runtime/rules.py` —
`RULE_OPS` (the `when` predicate language) **+** `DESTINATION_KINDS` + `route()` (the routing
connection Tim named). It is the two HARD halves at once: the predicate and the routing.

**The structural TEMPLATE to clone (a different thing from "reuse"):**
`runtime/mode_detection_rules.py` — the file-discovery + RULE_OPS-`when` + priority + fail-loud
form. You copy its *shape*; you import + call `rules.py`.

---

## 1. REGISTRY SYSTEM — how "registry-is-truth" is declared

### 1.1 The ONE registry mechanism (file-discovered)
The repo has a **single, repeated registry mechanism**, stated explicitly as a law: a registry =
a `<name>/` dir of self-registering `<id>.py` files, each declaring a module-level CONST dict;
`os.listdir → importlib`; `id` must equal filename; fail-loud `_build_*` gate on malformed rows;
`rediscover()` for removal; dict-like access. **Add-a-row = drop a FILE, no code edit.**

- **Observed** — canonical statement of the law and the "mirrors roles/projections/NodeRegistry"
  note: `runtime/mode_detection_rules.py:10-40` and `:26-33`.
- **Observed** — the base node registry it all mirrors: `runtime/registry.py` (`NodeRegistry`).
- **Observed** — `RoleRegistry`/`ProjectionRegistry` are standalone copies of that pattern
  (`runtime/mode_detection_rules.py:26-33` names them as the precedent).

### 1.2 The registries that exist (the live `<name>/` dirs)
Repo-root sibling dirs of `nodes/`, each a file-discovered registry (Observed via `ls` + the
`runtime/*.py` registry modules):

```
roles/  projections/  nodes/  mode_detection_rules/  lifters/  mark_types/
generation_policies/  relation_types/  ai_tics/  forms/  minds/  routines/
skills/  contexts/  flows/  ...  (+ many domain dirs: marks, channels, board_edges, …)
```

### 1.3 Two declaration TIERS (this matters for the trigger registry)

**TIER A — discovered-and-wired (read at Suite construction).** `suite.py.__init__` discovers
each `<name>/` dir into a `*_registry` attribute. A NEW first-class discovered registry = **add
the discover line in `__init__`** (mirrors the block at `runtime/suite.py:318-344`).
- **Observed** — the 6 file-discovered corpus/cognition registries discovered together:
  `runtime/suite.py:318-344` (lifters/mark_types/generation_policies/relation_types/ai_tics/forms/minds).
- **Observed** — `mode_detection_rule_registry` discovered the same way:
  `runtime/suite.py:308-310` → `ModeDetectionRuleRegistry().discover([...])`.

**TIER B — `_CORPUS_REGISTRIES` table (the create-*-authorable, MCP-writable subset).** A
single-source table mapping `kind → (dir-attr, registry-attr, RegistryClass, MODULE_CONST)`.
The `create_*` MCP tools and the shared writer derive from this table — **one ROW per registry,
no per-registry branch.**
- **Observed** — the table: `runtime/suite.py:360-371` (`self._CORPUS_REGISTRIES = { ... }`).
- **Observed** — the shared writer `_write_registry_file(kind, spec)` that EVERY `create_*`
  routes through: `runtime/suite.py:9840-9931`. Mechanism = render `<CONST> = {...}` (pprint
  python literal) → **gate-in-tempdir via the registry's OWN `discover()`** (a malformed spec
  RAISES before any live write) → atomic write `<name>/<id>.py` → git-commit (revertible) →
  rediscover (go live in-process). Returns `{id, kind, path, live, spec}`.
- **Observed** — the per-kind thin wrappers: `runtime/suite.py:9933-9966`
  (`create_projection`/`create_mark_type`/.../`create_mind`), each one line:
  `return self._write_registry_file("<kind>", spec)`.
- **Observed (CRITICAL CONSTRAINT)** — Tier B is **scoped to PURE-DATA rows only**. A registry
  whose row carries a CALLABLE (lifter `extract`, form `match`) cannot round-trip pprint/MCP-JSON
  and is GATED off this path: `runtime/suite.py:348-359` + the callable-guard at `:9886-9891`.

### 1.4 How a NEW registry is added first-class (the recipe, Observed from the above)
1. `runtime/<name>.py` — copy `mode_detection_rules.py` shape: `<NAME>_FIELDS`, a `_build_<name>`
   fail-loud validator, a `<Name>Registry` class (`discover`/`rediscover`/dict-like).
2. `<name>/` dir at repo root with `<id>.py` rows + an `AGENTS.md` drift-home.
3. `runtime/suite.py.__init__` — one discover line (TIER A) like `:308-310`.
4. If MCP-writable: add ONE row to `_CORPUS_REGISTRIES` (`suite.py:360`) **iff the row is pure
   data** — then `create(kind='<name>')` works for free via `_write_registry_file`.
5. Reflect in the drift-home (`runtime/AGENTS.md`) — acceptance tests assert reflection.

**A trigger registry's row is PURE DATA** (event/when-AST/destination/params/priority — no
callable), so it is **Tier-B-ELIGIBLE** for `create()` authoring. **(Inferred** from the row shape
vs the pure-data rule at `suite.py:348-359` — a trigger row carries no python function.)
**CAVEAT (Observed counter-precedent):** `mode_detection_rules` is ALSO pure-data yet is **NOT** in
`_CORPUS_REGISTRIES` (it's Tier-A discover-only at `suite.py:308-310`). So pure-data is necessary
but not automatically sufficient — something kept MDR off the create-path. Resolve *why* before
promising "`create(kind='trigger')` for free."

---

## 2. GRAPH + MCP TOOLS — where Tim wants the trigger registry to live

### 2.1 The MCP tool surface
- **Observed** — server bootstrap: `mcp_face/server.py` constructs `FastMCP("company")` and
  **pkgutil-discovers** every `mcp_face/tools/<resource>.py`, calling its `register(mcp, SUITE)`.
  *Add a tool = add a file, no edit to server.py* (the same self-extending property as the
  registries). (server.py header, **sub-agent-reported** for the exact pkgutil lines ~25-36.)
- **Observed** — the direct graph tools in `server.py`:
  - `list_by_type(output_type)` → `SUITE.list_by_type(output_type)` — `mcp_face/server.py:50-52`.
  - `list_graphs()` → `SUITE.list_graphs()` — `mcp_face/server.py:56-58`.
  - `run_graph(graph, branch="main")` → `SUITE.run(graph, branch=branch)` — `mcp_face/server.py:78-81`.
- **Observed** — the existing tool modules (the peers a `triggers.py` would join):
  `mcp_face/tools/` = `create.py · node.py · flows.py · runs.py · rule.py · dials.py · corpus.py ·
  marks.py · channels.py · introspection.py · operator.py · sessions.py · routines.py · …`.

### 2.2 The graph/node engine behind the tools
- **Observed** — `SUITE.list_by_type(t)` is literally `return self.registry.produces(t)`:
  `runtime/suite.py:1711-1712` (the node TYPE-graph query — "which node types output port-type t").
- **Observed** — `SUITE.list_graphs()` at `runtime/suite.py:1714`.
- **Observed** — `SUITE.create_node(graph_id, type, config, ...)` at `runtime/suite.py:1759`
  (graph node create — note `node` is EXCLUDED from `_CORPUS_REGISTRIES`/`create(kind=)` because a
  graph is not a registry: `create.py:5` and `:32-34`).
- **Observed** — `SUITE.run(graph_id, branch, pause, force)` (the `run_graph` body) at
  `runtime/suite.py:1853`; the reactive engine is `runtime/scheduler.py` (a RESOLVER, not control
  flow — a node fires when its input ADDRESSES resolve in the store; header `scheduler.py:1-18`).
- **Inferred** — graphs persist as `<graph_id>.json` under the store root (`.data/store/graphs/`);
  **sub-agent-reported**, not personally opened.

### 2.3 The `create(kind=)` registry-is-truth derivation (the pattern a trigger tool would join)
- **Observed** — `mcp_face/tools/create.py:28-34`: the `kind` enum is DERIVED at registration from
  `dir(suite)` — every `create_<kind>` method (minus `create_node`) becomes a valid kind:
  ```python
  _kinds = tuple(sorted(n[len('create_'):] for n in dir(suite)
                        if n.startswith('create_') and n != 'create_node'))
  KindT = Literal.__getitem__(_kinds)
  ```
  So: add `Suite.create_trigger` (one line → `_write_registry_file("trigger", spec)`) and
  `create(kind='trigger', spec=...)` exists **with zero edits to create.py**.

### 2.4 WHERE the trigger registry should live (the placement answer)
The graph-MCP surface is the right home **because triggers are addressable-and-routable like
graphs/nodes**: a trigger tool (`mcp_face/tools/triggers.py`, `triggers(op=list|get|run|...)`)
sits beside `flows.py`/`node.py`/`routines.py`, and its rows resolve their ACTION through the same
routing layer the graph engine uses (§3). **(Inferred** placement from the consolidated-tool law:
`mcp_face/server.py` header — "a new need is a new `op`, never a new flat tool".)

---

## 3. ROUTING — where the trigger registry "connects with routing"

There are **THREE distinct routing layers**. A trigger touches the third (rules.route) directly;
the other two are what a trigger's fired ROLE/MODEL resolves through.

### 3.1 `rules.route()` + `DESTINATION_KINDS` — THE trigger→action seam (the one Tim means)
- **Observed** — `DESTINATION_KINDS` (the five destinations a rule/trigger may route an action to):
  `runtime/rules.py:114-126`:
  - `inject` — inject value into a later reply part.
  - `chain` — **"chain/trigger a dependent role"** (a thin executor fires `run_role`; the model
    runs in the ROLE, never the rule). **← this is literally event→action firing a role.**
  - `address` — land the value at a `run://` address (durable write).
  - `surface` — surface to the operator inbox via `Suite.surface_review` (an `ask`, never resolve).
  - `lane` — write to a named typed stream (`kind='cognition.lane'`).
- **Observed (THE FLOOR — binding law)** — `FORBIDDEN_DESTINATION_VERBS = ("resolve","approve",
  "dispatch")` at `runtime/rules.py:130`. A rule/trigger can NEVER forge an operator approve or a
  `claude -p` dispatch — the floor holds BY CONSTRUCTION. A trigger system MUST stay inside the
  five destinations.
- **Observed** — `route(decision, *, store, suite, turn_id, emit, chain_executor)` =
  `runtime/rules.py:491`; the dispatch body per destination spans `rules.py:~516-583`
  (**sub-agent-reported** line spans inside route; the function signature + DEST_KINDS are
  personally verified).
- **Observed** — `Rule.decide(resolved) -> {fire, value, destination, params}` at
  `runtime/rules.py:344`; `Rule` validates `destination ∈ DESTINATION_KINDS` and `when` ∈ grammar
  at construction: `runtime/rules.py:299-325`.

### 3.2 `RULE_OPS` — the ONE predicate language (the `when` half, REUSE never fork)
- **Observed** — `RULE_OPS` closed grammar at `runtime/rules.py:65`; `validate_ast` (fail-loud
  whitelist walk) and `evaluate` (pure, IO-free interpreter — NEVER eval/exec) are the same
  functions `mode_detection_rules` already reuses (`runtime/mode_detection_rules.py:90, 114,
  192-197`). A trigger's `when` is this exact AST.

### 3.3 `model_routing.resolve_model` — model selection for a fired action
- **Observed (sub-agent-reported line)** — `resolve_model(intent, *, suite=None) -> dict` at
  `runtime/model_routing.py:105`. Dispatches by `intent["kind"]`: `"clone"` (context-size pick),
  `"role"` (role→provider binding), `"capability"` (provider query). Returns
  `{model, base_url, provider, why, satisfied, ...}`.
- A trigger that fires a role/model resolves the concrete model through here. (The `chain`
  destination's `run_role` already does this internally.)

### 3.4 `cognition.resolve_address` + `capability_providers` — address/capability resolution
- **Observed (sub-agent-reported line)** — `resolve_address(store, addr, *, turn_id, on_missing)`
  at `runtime/cognition.py:842`, dispatching by scheme from `contracts/address.py` SCHEMES:
  `run:// cas:// skill:// context:// session:// cap:// board:// clone:// mind://` + bare-name
  sentinel. A trigger's action lands at / reads from `run://` addresses through this.
- **Observed** — `cap://` resolves via the cached `CapabilityRegistry` singleton; capability
  providers are queried via `Suite.capability_providers()` (scans `ops/services.json`,
  role.requires ⊆ provider.provides). Drift-home note: `runtime/AGENTS.md:378-386`.

### 3.5 The handoff (Inferred trace — how a trigger reaches routing)
```
event fires  →  trigger.when (RULE_OPS evaluate over a snapshot)  →  fire?
   → trigger.destination (DESTINATION_KINDS) → rules.route(decision, suite, store, ...)
      ├ chain   → run_role → resolve_model (3.3) → model in a ROLE
      ├ address → run:// write (resolve_address 3.4)
      ├ surface → suite.surface_review (operator ask)
      └ lane    → cognition.lane stream
```
This is exactly the path `activation.fire_activation` already walks (§4.2) — the trigger registry
generalises the EVENT half of it.

---

## 4. CRITICAL QUESTION — does a TRIGGER/HOOK registry ALREADY exist?

### ANSWER: **NO registry named "trigger" or "hook" exists. BUT event→action declaration
already exists, split across two places — and the unifying binding is what's MISSING.**

**Evidence it does NOT exist as a named unit (Observed):**
- No `trigger*/ hook*/ event*/ listen*/ subscri*/ watch*/ signal*` dir at repo root (`ls` →
  "NONE").
- No `class *Registry` matching Trigger/Hook/Event/Listener, and no `TRIGGER_REGISTRY`/
  `HOOK_REGISTRY` const anywhere in `*.py` (grep → empty).
- `ops/hooks/` is a single OPS shell script (`cc_registry_freshness_check.sh`) — **not** an
  application hook system.
- The one registry with "action" in its NAME (`coherence_actions.ActionRegistry`) was checked: it
  is action-COMPOSITION, **not** event-triggered (see candidate #5 below). No false negative from
  the naming filter.

**Evidence the THREE HALVES already exist (Observed):**

| Half | Exists as | Where | Form |
|---|---|---|---|
| #1 event-kind taxonomy | `ACTIVATION_CONTEXTS` | `runtime/activation.py:64-106` | **in-module dict, NOT file-discovered, NOT MCP-exposed** |
| #2 when-predicate | `RULE_OPS` + validate/evaluate | `runtime/rules.py:65` | the ONE predicate language (reuse) |
| #3 action/routing | `DESTINATION_KINDS` + `route()` | `runtime/rules.py:114, 491` | the routing connection Tim named |

**The closest existing event→action MECHANISMS (Observed), and why each is not THE registry:**

1. **`runtime/activation.py` — `ACTIVATION_CONTEXTS` + `fire_activation`** (the closest in SPIRIT).
   Each context DECLARES an explicit `trigger` kind: `turn` / `idle-loop` / `sense:event-hook` /
   `timer` (`activation.py:64-106`). `fire_activation(suite, context, sense_event=...)` fires a
   cast and routes outputs via `rules.route()` over surface/address/lane (`activation.py:141,
   218-220`). The **`sense` context IS an event-hook trigger** (`activation.py:86-95`).
   *Why not the registry:* it's an **in-module dict (not file-discovered)**, the **drivers are
   dormant/needs-tim** (`activation_driver.py` header), and it's **not MCP-exposed**. It is the
   event-KIND taxonomy half, not the binding.

2. **`runtime/mode_detection_rules.py` — `ModeDetectionRuleRegistry`** (the closest in STRUCTURE,
   the strongest template). A file-discovered registry of `when(RULE_OPS AST) → candidate`, ordered
   by explicit `priority`, first-match-wins, fail-loud `_build_rule`, `as_records()` projection
   (`mode_detection_rules.py:100-266`). This is **structurally already a trigger registry**
   (predicate→outcome), and it PROVES the "file-discovered + RULE_OPS `when` + priority" pattern is
   live (rows: `mode_detection_rules/{background,focus,listening}.py`).
   *Why not the registry:* its outcome is narrowly a **mode candidate fed to a toggle**, not a
   general `DESTINATION_KINDS` action; and its event is fixed to the `activity_signal()` snapshot.

3. **`runtime/routines.py` — `RoutineRegistry`** (a scheduler, not a general trigger).
   File-discovered registry of fireable `claude -p` tasks; its "TRIGGER LAYER" is explicitly TWO
   ARMS: a systemd `.timer` (cadence) + manual `/fire` (`routines.py:1-23, ROUTINE_FIELDS cadence/
   trigger`). MCP-exposed via `mcp_face/tools/routines.py` (`op=list|get|fire`).
   *Why not the registry:* its only "events" are **clock (cadence) + manual fire** — it is a
   *scheduler*, not a general event→action declaration.

4. **`runtime/rules.py` — G3 rule engine.** Already binds `when → destination` (`Rule` at
   `rules.py:299`). *Why not the registry:* a `Rule` rides INSIDE a fired role's output routing
   (per-turn / per-activation); there is **no top-level, file-discovered, event-keyed registry of
   standalone trigger rules** that a driver walks on arbitrary events.

5. **`runtime/coherence_actions.ActionRegistry` + `runtime/coherence_detect.py`** (checked
   explicitly — a near-miss by name). **Observed:** `coherence_actions.py:1-9` — an `ActionRegistry`
   (`coherence_actions.py:144`) of **saved chains/graphs promoted to fireable ACTIONS** (steps with
   `op`/`role`/`model`, validated through ONE `build_action` door `:23`, RUN by `run_cascade` /
   `run_graph`, persisted to `cascades.json` via `suite.cascade_registry` `suite.py:393`).
   `coherence_detect.py:1-13` is **model-free STATIC ANALYSIS** (AST route extraction / dead-code
   detection), a "detector" only in the static-analysis sense.
   *Why neither is THE registry:* `ActionRegistry` is action-**COMPOSITION** (declare→validate→save→
   replay) with **no `when`/`event` field** — it is the *action* shape, never event-TRIGGERED;
   `coherence_detect` declares no condition→action at all. They confirm the action-half exists as
   concrete declared/fireable units, but **nothing binds an EVENT or a `when` to them.**

**MISSING (the unification):** a **file-discovered, MCP-exposed `trigger/` registry** whose row
binds `event-kind (from #1) → when (RULE_OPS, #2) → destination/action (DESTINATION_KINDS, #3)`,
plus a thin DRIVER that, on a real event, walks the registry's rows for that event-kind and calls
`rules.route()`. The parts exist, scattered; the binding does not.

---

## 5. WHAT TO REUSE vs WHAT IS MISSING

### REUSE (do not fork — these are the load-bearing parts)
| Reuse | Source (Observed) | Role in the trigger system |
|---|---|---|
| **`runtime/mode_detection_rules.py` (whole file as TEMPLATE)** | `:100-266` | the exact file-discovered + RULE_OPS-`when` + priority + fail-loud `_build` + `as_records` shape to clone into `runtime/triggers.py` |
| **`rules.RULE_OPS` + `validate_ast` + `evaluate`** | `runtime/rules.py:65` etc. | the `when` predicate language (reuse, never a 2nd) |
| **`rules.DESTINATION_KINDS` + `route()` + FORBIDDEN_DESTINATION_VERBS** | `runtime/rules.py:114, 491, 130` | the action/routing connection + the floor a trigger MUST honour |
| **`activation.ACTIVATION_CONTEXTS`** | `runtime/activation.py:64-106` | the event-KIND taxonomy (turn/idle-loop/event-hook/timer) the trigger `event` field draws from |
| **`activation.fire_activation`** | `runtime/activation.py:141` | the PROVEN fire→run_swarm→route path a sense/background trigger already follows |
| **`_write_registry_file` + `_CORPUS_REGISTRIES`** | `runtime/suite.py:9840, 360` | free MCP authoring (`create(kind='trigger')`) IF the row stays pure-data |
| **`mcp_face/tools/routines.py` / `flows.py`** | `mcp_face/tools/` | the `register(mcp,suite)` + `triggers(op=…)` tool-module template |
| **`Suite.__init__` discover block** | `runtime/suite.py:308-344` | where to wire `trigger_registry` (Tier A) |

### MISSING (must be built)
1. **`runtime/triggers.py`** — `TriggerRegistry` (clone `mode_detection_rules.py`), with a row
   shape that adds an **`event`** field (the event-kind, validated ∈ a known event taxonomy) and a
   **`destination`** field (validated ∈ `DESTINATION_KINDS`, rejecting `FORBIDDEN_*`) on top of
   `when`/`priority`/`why`. (No callable in the row → pure data → Tier-B authorable.)
2. **An EVENT-KIND taxonomy that is itself a registry-or-declared-set** — today event-kinds live
   only inside the in-module `ACTIVATION_CONTEXTS` dict. The trigger system needs the event taxonomy
   to be first-class (either lift `ACTIVATION_CONTEXTS` to file-discovered, or have `triggers.py`
   validate `event` against it). **This is the true gap vs the registry-is-truth bar.**
3. **A trigger DRIVER** — the thing that, on a real event, looks up matching trigger rows
   (`registry.for_event(kind)` in `priority` order) and calls `rules.route()` per fired row. This
   mirrors `activation.fire_activation` but generalised over the event taxonomy (and shares its
   dormant/needs-tim posture for any always-on event source).
4. **`mcp_face/tools/triggers.py`** — `triggers(op=list|get|run|...)`, auto-registered by pkgutil.
5. **`Suite.create_trigger` one-liner** + a `_CORPUS_REGISTRIES["trigger"]` row → free MCP authoring.
6. **`trigger/AGENTS.md` drift-home** + an acceptance test asserting reflection (the registry law).

---

## 6. THE DIRECTORY GRAPH (where these live)

```
/home/tim/company
├── runtime/                         # the engine + every registry CLASS
│   ├── suite.py        :308-344  __init__ discover block (Tier A wiring)
│   │                   :360-371  _CORPUS_REGISTRIES table (Tier B, MCP-writable)
│   │                   :1711     list_by_type→registry.produces
│   │                   :1714     list_graphs · :1759 create_node · :1853 run (run_graph)
│   │                   :9840     _write_registry_file (the shared authoring writer)
│   ├── registry.py               NodeRegistry (the base mechanism everything mirrors)
│   ├── mode_detection_rules.py   ★ STRONGEST TEMPLATE (file-disc + RULE_OPS when + priority)
│   ├── rules.py        :65       RULE_OPS  · :114 DESTINATION_KINDS · :130 FORBIDDEN_*
│   │                   :299      Rule · :344 decide · :491 route()      ★ ROUTING SEAM
│   ├── activation.py   :64-106   ACTIVATION_CONTEXTS (event-kind taxonomy: turn/idle/sense/timer)
│   │                   :141      fire_activation (proven fire→route path)
│   ├── activation_driver.py      the dormant/needs-tim always-on caller (posture template)
│   ├── routines.py               RoutineRegistry (scheduler arm: cadence + /fire)
│   ├── model_routing.py :105     resolve_model (model selection)
│   ├── cognition.py    :842      resolve_address (scheme dispatch)
│   └── scheduler.py              the reactive graph engine (resolver)
├── mcp_face/
│   ├── server.py       :50 list_by_type · :56 list_graphs · :78 run_graph
│   │                   (pkgutil-discovers tools/, calls register(mcp,SUITE))
│   └── tools/          create.py:28-34 (kind=… registry-is-truth) · node.py · flows.py
│                       · routines.py · rule.py · …      ← add triggers.py HERE
├── contracts/
│   ├── address.py                SCHEMES (run:///cap:///mind://…) for resolve_address
│   └── node_record.py            Graph/NodeInstance/Edge schema (sub-agent-reported)
├── mode_detection_rules/         background.py focus.py listening.py + AGENTS.md   ← ROW dir to mimic
├── roles/ projections/ nodes/ lifters/ mark_types/ generation_policies/
│   relation_types/ ai_tics/ forms/ minds/ routines/ flows/ skills/ contexts/  (peer registry dirs)
└── build-prep/trigger-system/    ← THIS doc
        ▶ a NEW trigger/ dir would be a repo-root sibling of mode_detection_rules/
```

---

## 7. RECOMMENDED BUILD SHAPE (tentative — for correction)

`trigger = clone(mode_detection_rules.py) + event field + route() action`

1. `runtime/triggers.py` ← clone `mode_detection_rules.py`; row = `{id, event, when, destination,
   params, why, priority}`; reuse `rules.validate_ast` for `when`; validate `destination ∈
   DESTINATION_KINDS` & `∉ FORBIDDEN_*`; validate `event ∈` the event taxonomy.
2. Make event-kinds first-class (gap #2): either lift `ACTIVATION_CONTEXTS` to a file-discovered
   `event_kinds/` registry, or import + validate against it from `triggers.py`. **Decide with Tim.**
3. `runtime/trigger_driver.py` ← clone the `fire_activation`/`activation_driver` dormant-posture:
   `fire_triggers(suite, event_kind, event)` walks `registry.for_event(kind)` by priority, evaluates
   each `when` against the event snapshot, calls `rules.route()` for fired rows. Always-on event
   SOURCES stay needs-tim (mirror `activation_driver`'s `COMPANY_*` gate).
4. `runtime/suite.py` — discover `trigger_registry` (Tier A, beside `:308-310`) + add
   `_CORPUS_REGISTRIES["trigger"]` row + one-line `create_trigger`.
5. `mcp_face/tools/triggers.py` — `triggers(op=list|get|run)`, auto-registered.
6. `trigger/AGENTS.md` drift-home + `tests/triggers_acceptance.py`.

> Open questions for Tim (do not resolve unilaterally): (a) should the event taxonomy be lifted out
> of `ACTIVATION_CONTEXTS` into its own registry, or is a trigger just a NEW activation-context?
> (b) Should triggers route ONLY via `DESTINATION_KINDS` (the floor), or also be allowed to fire a
> graph (`run_graph`) — which would extend the destination set and needs the floor re-examined?
