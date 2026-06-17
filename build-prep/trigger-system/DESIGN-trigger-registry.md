# DESIGN — the reusable TRIGGER REGISTRY + CC-LAUNCH NODE

> A read-only design (no code written). Built on the three prior scans in this dir
> (`SCAN-registries-graph-routing.md`, `SCAN-cc-launch-node.md`, `SCAN-hooks-events-board.md`) and a
> deep read of the cited files. Evidence-classed per Tim's bar: **Observed** = read directly (file:line),
> **Inferred** = pattern-matched (labelled), **Verified** = confirmed by running an inspection. Every
> piece tagged **REUSE** (import + call, never clone) / **CLONE** (copy the *shape* of a template) /
> **BUILD** (net-new). Open questions are flagged for Tim, never resolved unilaterally.

---

## 0 · THE ONE-SCREEN ANSWER (the relational circuit)

A trigger is one unbroken circuit — and every link in it already exists except the *binding* and the
*driver*:

```
  EVENT  ───emit──▶  EVENT-LOG  ───driver reads (cursor)──▶  TRIGGER REGISTRY  ──when?──▶  ACTION
  (board.filed,      (the ONE          (BUILT-NOT-ARMED,        trigger/<id>.py        ┌─ rules.route (5 DEST_KINDS)
   turn.done,         append-only       mirrors                 {watch, when,          │   surface/address/lane/inject/chain
   sense, timer)      log)              activation_driver)       action, output} )      └─ CC-LAUNCH NODE  ← the launch
        │                  │                    │                      │                    (scheduler/supervisor layer,
   event taxonomy     events_since()       for_event(kind)       RULE_OPS `when`            NOT a rule verb — see §F)
   (HALF #1: a gap)   (REUSE)              + priority            (REUSE rules.py)                │
                                                                                          output-target:
                                                                                       file_item(links=[responds_to])
                                                                                          back to the trigger
```

**THE FLOOR, STATED FIRST (the keystone — §F).** A trigger that "launches a Claude Code session" does
NOT violate the unforgeable floor, because the launch does **not** live in the rule layer. There are
**TWO distinct dispatch surfaces** and the design keeps them separate:

1. **Rule-routing** — `rules.route()` over the FIVE `DESTINATION_KINDS`. A rule/trigger may NEVER emit
   `resolve`/`approve`/`dispatch` (`FORBIDDEN_DESTINATION_VERBS`, `runtime/rules.py:130`). Cheap trigger
   actions (surface / address / lane / inject / chain-a-role) ride this. **We add NO 6th destination.**
2. **CC-launch** — running a *node/graph* through the scheduler → session-supervisor, the SAME mechanism
   `run_graph` already uses. Autonomous `claude -p` launch is the **legitimate purpose** of the
   routine/supervisor layer (`routine_runner.fire()` "spawns a REAL session — the consequential verb",
   `mcp_face/tools/routines.py:17`), bounded by `COMPANY_FABRIC_CONCURRENCY=3`
   (`session_supervisor.py:600-610`) + consent posture + explicit arming.

A trigger's `action` therefore picks ONE of those two surfaces. The CC-launch is reached as **"run this
node/graph"** (an `address`/run-graph action), never as a rule forging a verb (the SCAN §7(b) trap is
explicitly avoided). And the **trigger DRIVER is BUILT-NOT-ARMED** — it mirrors `activation_driver`'s
dormant posture (`runtime/activation.py:330-348`, env-gated, no always-on daemon stood up).

**Single biggest REUSE win:** `runtime/rules.py` — `RULE_OPS` (the `when` predicate language) **+**
`DESTINATION_KINDS` + `route()`. That is the two HARD halves at once (the predicate AND the routing
connection Tim named), proven reused by `mode_detection_rules` and `activation.fire_activation`.

**Single biggest NEW piece:** the **trigger DRIVER** (`runtime/trigger_driver.py`, §5) — the thing that
reads events off the log and fires matching rows. The registry, the CC-launch node, and the MCP tool are
mostly clone-and-wire of existing shapes (`mode_detection_rules`, `nodes/ask.py`, `routines.py`); the
driver is genuinely net-new. (First-classing the event-kind taxonomy is the key open *decision* — Tim's
call, §2.2 / open question A — not a co-equal new piece.)

---

## FACET 1 — THE CC-LAUNCH NODE (`nodes/cc_launch.py`)

**Tim's frame:** *"launching the CC is basically input variable → output variable for Claude Code."* As a
composable graph unit: inputs `{prompt, startup-flags, model/provider, context-address}` → output a
**STRUCTURED result written to an address**.

### 1.1 What this IS — a `nodes/` dataflow module (CLONE the contract, REUSE the engine)

A node module self-registers by file-drop (`runtime/registry.py:55-90`; `nodes/AGENTS.md:14-19` — "adding
a node = dropping a file"). Its contract (Observed from `nodes/ask.py` + `registry.py:75-90`):

```python
# nodes/cc_launch.py  (BUILD — the module itself)
KIND = "process"; VERSION = "1"
VOLATILE = True                       # ★ MANDATORY — a CC launch reads MUTABLE truth (live repo/model);
                                      #   without it the scheduler memo-gate serves the first result forever
                                      #   (nodes/AGENTS.md:15; scheduler.py VOLATILE bypass).
PORTS_IN  = {"prompt": "Text", "context": "Text"}        # context = the context-address resolved to prose
PORTS_OUT = {"result": "Text", "structured": "Json"}     # TWO outputs: prose result + the typed value
CONFIG = {                            # the inspector's editable fields (the non-wired inputs)
    "model":        {"type": "enum",   "label": "Model",      "options_from": "chat_models"},
    "provider":     {"type": "enum",   "label": "Provider",   "default": "anthropic"},  # 'ollama' = launcher path
    "permission_mode": {"type": "enum","label": "Permission", "default": "plan"},
    "json_schema":  {"type": "string", "label": "Output schema (--json-schema)", "default": ""},
    "flags":        {"type": "json",   "label": "Extra start-flags", "default": {}},
    "keep_session": {"type": "bool",   "label": "Keep session (multi-turn)", "default": False},
}
OUTPUT_SCHEMA = {...}                  # declares "the structured thing it produces" → NodeType.output_schema

def run(inputs, config):
    # fire the supervisor circuit (the proven routine_runner.fire PATTERN, on raw /spawn) →
    # return {"result": <prose>, "structured": <result.structured_output>}
```

- **"Written to an address" is FREE** — the scheduler writes each `PORTS_OUT` port to its run:// address
  (`runtime/scheduler.py:48`; SCAN-cc-launch §4). The node's `run()` only returns `{port: value}`.
- **One-shot vs session** — `keep_session=False` = pure input-var→output-var (`/spawn` → watch `done` →
  `/teardown`, `routine_runner.fire` with `keep=False`). `keep_session=True` threads `session_id` as node
  state for multi-turn (`/inject` further turns, `msg_clone` pattern). Same engine. (SCAN-cc-launch §
  "One-shot vs session".)

### 1.2 The launch engine — REUSE the supervisor `/spawn` → `/watch done` cycle

`run()` builds on the **single best existing primitive**: the session-supervisor's
`/spawn(prompt, model, provider, flags)` → `/watch` `done` cycle (`session_supervisor.py:804-891` +
`:1086-1110`) — the only launch surface carrying ALL the named inputs in one POST. **Prefer the
`routine_runner.fire()` PATTERN over the inputs-bottleneck of `fire()` itself**: SCAN-cc-launch §6 found
`build_spawn_body` (`routine_runner.py:37-50`) only threads `{cwd, prompt, permission_mode, name, model}`
— it **drops `provider`, `flags`, `effort`, `fallback`**, so it cannot pass `provider='ollama'` OR
`flags={"json_schema": …}`. The raw `/spawn` route DOES read `provider`+`flags` off the body
(`session_supervisor.py:1591-1602` per scan). So `cc_launch.run()` copies the spawn→inject→watch→teardown
orchestration (~30 lines) onto raw `/spawn`, building the FULL body. (BUILD, reusing the engine.)

- **Input side of structured output — REUSE.** `--json-schema` is a declared flag:
  `SPAWN_FLAG_ASSEMBLY["json_schema"]` (`session_supervisor.py:278-279`), teach-string *"schema-validated
  structured output (result.structured_output)"*. A CC launch CAN be told to emit schema-valid JSON.
- **provider='ollama' — REUSE.** The launcher path runs `ollama launch claude --model <tag> -- -p …`
  (`session_supervisor.py:651-655`), with the PATH fix at `:853-854`. (Tim 2026-06-16: launch command, not
  env overlay.)
- **Concurrency constraint (compose-time).** A graph firing >3 cc_launch nodes in parallel hits
  `TeachingRefusal` (429) at the cap (`session_supervisor.py:600-610`, default 3). Note this in the node's
  drift-home so a fan-out graph designer knows the bound.

### 1.3 ★ CLOSE THE STRUCTURED-OUTPUT CAPTURE GAP (the one real BUILD inside an otherwise-reuse path)

**Verified field name (it is `structured_output`, snake_case — load-bearing, was flagged for
verification):** the repo's own Claude-Code result-event field-map confirms it —
`runtime/render_declarations.json:394`:
`"field_map": {... "structured_output": "structured_output", ... "model_usage": "modelUsage"}` — i.e. the
wire field IS `structured_output` (snake), whereas `model_usage` is renamed from wire `modelUsage`. Also
`ui-contract/resources/headless-control.md:162,177` ("result carries `structured_output`"). So
`result.structured_output` is the right field; `structuredOutput` is NOT it.

**The gap (Observed):** `_turn_done` builds the fanned `done` event from `ev.get("result")` + usage ONLY
(`session_supervisor.py:1086-1097`) — it does **NOT** read `ev["structured_output"]`. A CC launched with
`--json-schema` *produces* structured output and the supervisor *drops* it.

**THE FIX (BUILD — minimal, additive):**
1. `_turn_done` (`session_supervisor.py:1095-1097`) — add `"structured_output": ev.get("structured_output")`
   to the fanned `{type:"done", …}` dict (None when no schema was used → byte-identical for non-schema
   spawns).
2. The capture readers that lift `done` — extend each to surface it:
   - `cc_clone.msg_clone` (`cc_clone.py:330-339`) — return `{reply, structured}`.
   - `routine_runner._capture_done` / `fire` (`routine_runner.py:81-91, 115`) — add `structured_output` to
     the run record.
3. `cc_launch.run()` returns `{"result": result_text, "structured": done.get("structured_output")}`.

### 1.4 End-to-end structured chain (the circuit, facet 1)

```
inputs{prompt,context} + config{model,provider,flags{json_schema}}
   → POST /spawn (full body, raw route)               [REUSE supervisor]
   → /watch until type=="done"                         [REUSE]
   → done now carries result.structured_output         [BUILD: _turn_done +2 readers]
   → run() returns {result: <prose>, structured: <typed>}
   → scheduler writes PORTS_OUT["result"]→addr, PORTS_OUT["structured"]→addr   [REUSE scheduler]
   → both addresses resolve downstream (a trigger's output-target reads `structured`)
```

| Piece | file:line | Verdict |
|---|---|---|
| `/spawn` w/ prompt+model+provider+flags | `session_supervisor.py:804-891`, `_build_spawn_cmd:612-695` | **REUSE** |
| `--json-schema` flag (input side) | `session_supervisor.py:278-279` | **REUSE** |
| `/watch`→`done` capture | `session_supervisor.py:1028-1110`; `cc_clone.py:303-339` | **REUSE** |
| Node contract (ports/config/output_schema/run, VOLATILE) | `registry.py:75-90`; `nodes/ask.py`; `nodes/AGENTS.md:15` | **REUSE** (slot) |
| Scheduler writes output→address (reactive) | `scheduler.py:37-48` | **REUSE** |
| `structured_output` CAPTURE (lift in `_turn_done` + readers) | `:1086-1097`; `cc_clone.py:331`; `routine_runner.py:115` | **BUILD** |
| `nodes/cc_launch.py` (the module) | — | **BUILD** |

---

## FACET 2 — THE TRIGGER REGISTRY (`runtime/triggers.py` + `trigger/<id>.py`)

A trigger is a declared event→action row: **registry-is-truth, file-discovered, add-a-row-not-code** —
the ONE registry mechanism (`runtime/mode_detection_rules.py` is the strongest structural TEMPLATE:
file-discovered + RULE_OPS-`when` + explicit `priority` + fail-loud `_build` + `as_records`).

### 2.1 The TRIGGER row shape (CLONE mode_detection_rules.py; pure data → no callable)

```python
# trigger/<id>.py   — a registry ROW (id == filename, addressable by file)
TRIGGER = {
    "id":       "<id>",
    "watch":    {"event": "<event-kind>",          # WHICH events wake this trigger (the taxonomy — §2.2)
                 "address_pattern": "board://*"},   # OPTIONAL: filter by the event's address shape
    "when":     {<RULE_OPS data-AST>},              # the predicate over the event snapshot (REUSE rules.py)
    "action":   {"surface"|"address"|"lane"|"inject"|"chain"|"run_node"|"run_graph": <params>},
                                                    #   cheap kinds → rules.route; run_node/run_graph → §F layer 2
    "output_target": {"kind": "reply"|"attach",     # reply = land at run:// ; attach = file back onto the trigger
                      "edge": "responds_to"},       #   (facet 3 — a board edge back to the triggering item)
    "scope":    {"level": "global"|"project"|"user", "ref": "<id?>"},   # ★ scoping (open question C)
    "priority": 100,                                # lower fires first (first-match-wins, ordered walk)
    "why":      "one-line legible rationale",
}
```

- **`when` REUSES `rules.RULE_OPS`** — the ONE predicate language (`runtime/rules.py:65`), validated by
  `validate_ast` and evaluated by `evaluate` (pure, IO-free, never eval/exec). This is exactly what
  `mode_detection_rules` already does (`mode_detection_rules.py:90,114`). A trigger's `when` is this exact
  AST — **no second predicate language.**
- **`action`** maps to a destination. **Cheap kinds** (`surface`/`address`/`lane`/`inject`/`chain`) →
  `rules.route()` over `DESTINATION_KINDS` (`runtime/rules.py:114-126, 491`). **`run_node`/`run_graph`** →
  the scheduler/supervisor layer (§F). The row carries no python function → **pure data** → Tier-B-eligible
  (§2.3).
- **Validation** (`_build_trigger`, fail-loud, CLONE the `_build_rule` discipline): `id==filename`;
  `when` ∈ grammar (`rules.validate_ast`); `watch.event` ∈ the event taxonomy (§2.2); a cheap-kind action's
  destination ∈ `DESTINATION_KINDS` and ∉ `FORBIDDEN_DESTINATION_VERBS`; `run_node`/`run_graph` action
  names a registered node/graph.

### 2.2 The EVENT-KIND taxonomy — the true registry-is-truth gap (OPEN QUESTION A — Tim's call)

Today event-kinds live ONLY inside the in-module `ACTIVATION_CONTEXTS` dict (`activation.py:64-106`:
`turn`/`idle-loop`/`event-hook`/`timer`) — **not file-discovered, not MCP-exposed**. For a trigger's
`watch.event` to be registry-is-truth, the taxonomy must be first-class. Three candidate framings (do NOT
resolve unilaterally — SCAN §7(a)):

- **(A1) lift to a file-discovered `event_kinds/` registry** — the purest registry-is-truth answer
  (add-a-kind = a FILE); most net-new.
- **(A2) validate `trigger.watch.event` against `ACTIVATION_CONTEXTS` in-place** — smallest change; keeps
  the taxonomy in one module but not yet file-droppable.
- **(A3) "a trigger IS a new activation-context"** — fold triggers INTO the activation substrate rather
  than beside it.
- **Recommendation (tentative):** A1 for fidelity to registry-is-truth, but flagged for Tim because it is
  the largest of the three and reshapes how `activation.py` reads its own taxonomy.

### 2.3 Wiring + MCP authoring (REUSE the registry machinery)

- **TIER-A discover** (`Suite.__init__`): one discover line beside `mode_detection_rule_registry`
  (`suite.py:308-310`) → `self.trigger_registry = TriggerRegistry().discover([self.triggers_dir])`. (BUILD,
  one line.)
- **TIER-B `create(kind='trigger')` — CONDITIONAL (OPEN QUESTION B).** A trigger row is pure data, so it
  *looks* Tier-B-eligible (`suite.py:348-359` pure-data rule + `create.py:28-34` derives the `kind` enum
  from `dir(suite)`). **BUT** the scan found a counter-precedent: `mode_detection_rules` is ALSO pure-data
  yet is NOT in `_CORPUS_REGISTRIES` (`suite.py:360-371`) — it's Tier-A discover-only. **Resolve WHY MDR
  was kept off the create-path before promising `create(kind='trigger')` for free.** Lead facet 4 (the
  dedicated `triggers` MCP tool) regardless; treat `create_trigger` as a *conditional add* gated on that
  resolution. (Observed counter-precedent; Inferred eligibility.)

---

## FACET 3 — HOOK = the firing mechanism a trigger rides (board-file → trigger, the first use)

**HOOK ≠ TRIGGER (the code draws the line — SCAN-hooks verdict a).** A **hook** is a fixed interception
point the runtime offers (today exactly one: the `SessionStart` registry-freshness shell hook,
`.claude/settings.json:5-16`). A **trigger** is a declared `event→action` row a dispatcher reads and
fires. A hook is the *firing edge* a trigger rides; the trigger is the *rule*. For the board-file first
use, the "hook" is a minimal **emit on `file_item` + a driver that watches the event log**.

### 3.1 The gap (Observed) — `file_item` emits nothing

`cc_board.file_item()` validates → `_write` → returns the record; **no callback, no queue, no emit, no
notify** (`cc_board.py:201-241`; its lone "emit" is a docstring word at `:32`). The supervisor polls a
mailbox FILE, not the noticeboard dir (`session_supervisor.py:1263-1304`). **Filing a board item is an
inert write.**

### 3.2 The minimal emit — DO NOT bolt a pub/sub bus onto cc_board (advisor keystone 3)

`cc_board.py` is pure functions with **no suite/emit handle**. So the emit lives at the **suite/MCP
boundary**, OR `file_item` takes an optional `emit` callback the way `rules.route(emit=…)` already does
(`runtime/rules.py:491-493`). Either way it rides the **ONE append-only event log** — no parallel channel:

```python
# at the suite/MCP boundary (the mcp_face cc_board tool calls suite, which has _emit):
record = cc_board.file_item(...)
suite._emit("board.filed", f"{record['type']} · {record['title']}",
            address=record["address"], item_type=record["type"], source=record["source"])  # BUILD (1 emit)
```

This mirrors how `activation.py`'s casts emit `cognition.wave` and the `RollupDriver` reads them back by a
held `since` cursor (`activation.py:271, 510-529`). **`board.filed` then rides the event log, and the
trigger driver reads it via the same cursor pattern** — closing facet 3 with NO new infra.

### 3.3 The `responds_to` edge — a ROW-ADD (the attach-output mechanism)

The board already has the typed-edge layer the attach-a-reply needs (`cc_board.py:157-170, 318-410`).
There is **no `reply`/`responds_to` edge today** — adding one is a one-line **row-add**: drop
`board_edges/responds_to.py` (an item→item directed edge, mirroring `promoted_from.py`) and
`reset_registries()` makes it live (`cc_board.py:96-103`). (BUILD, one ROW — no code.)

The launched CC files its result back onto the trigger with the edge:

```python
cc_board.file_item(item_type="...", title="...", body="<the CC's structured/prose output>",
    author_session="session://<the-CC's-own-id>",
    links=[{"kind": "responds_to", "target": "board://<triggering-id>"}])   # ← the new edge row
```

**Verified (read):** `relations("board://<triggering-id>", direction="in")` already surfaces that reply —
the inbound-edge read works today (`cc_board.py:380-410`). So once attached, *finding* the reply is a
solved read.

### 3.4 The board→trigger circuit (facet 3 end-to-end)

```
file_item(item_type="request", …)                         [REUSE cc_board]
  → suite._emit("board.filed", address="board://<id>", item_type="request")   [BUILD: 1 emit]
  → trigger_driver reads "board.filed" off the event log (cursor)             [BUILD: driver — §4 / §5]
  → registry.for_event("board.filed") in priority order → each `when` over the event snapshot
  → a fired trigger whose action is run_node(cc_launch) → §F layer-2 launch (a real CC session)
  → the CC files its findings back: file_item(links=[{responds_to → board://<id>}])  [BUILD: 1 edge row]
  → relations(board://<id>, "in") surfaces the reply                          [REUSE — works today]
```

**★ THE SELF-TRIGGER LOOP (must guard — folded from Q-D).** Note the circuit: the reply
`file_item(...)` **re-emits `board.filed`** → the driver reads it → `for_event("board.filed")` returns the
SAME trigger → it fires again → a runaway CC-spawn loop, bounded only by the concurrency cap throwing 429s.
**The in-repo fix pattern is already proven:** `OPERATOR_ACTIVITY_KINDS` deliberately EXCLUDES
self-generated kinds so "the system reacting to its OWN background activity must NOT reset the idle clock"
(`activation.py:359-364`). The trigger driver needs the same guard — the emit (or the `when`) must
distinguish operator/agent-originated items from trigger-AUTHORED replies. Two grounded options: (a)
exclude items that carry a `responds_to` edge (they ARE replies — a structural test in `when`); (b) stamp
the emit with an origin marker the way `surface_review` stamps `origin="responsive"`
(`rules.py:570` → `suite.surface_review(item, origin="responsive")`) and have the driver skip
trigger-authored origins. **Recommendation:** (a) is structural and needs no new field; (b) is the more
general guard if any non-board action also re-emits. This is the difference between a sound design and a
latent landmine — a builder must wire it.

---

## FACET 4 — How agents SET UP triggers (`mcp_face/tools/triggers.py`)

A consolidated `triggers` MCP tool, **dropped beside `flows.py`/`node.py`/`routines.py`** — auto-registered
by `server.py`'s pkgutil discovery (`register(mcp, suite)`, no `server.py` edit; mirrors
`routines.py:27-29`). ONE parameterised tool, an `op` selector (the MCP-DESIGN-PRINCIPLE: "a new need is a
new `op`, never a new flat tool"):

```python
# mcp_face/tools/triggers.py   (BUILD — CLONE routines.py / flows.py shape)
def register(mcp, suite):
    @mcp.tool()
    def triggers(op: Literal["list","get","run","add","arm"], id: str = "", spec: dict | None = None) -> dict:
        # op="list"  — every registered trigger (id + watch.event + when_text + action + scope)
        # op="get"   — one trigger's full row (required: id)
        # op="run"   — MANUALLY fire a trigger NOW against a supplied/synthetic event (proves the path
        #              without arming the always-on driver — mirrors routines op=fire + sense_tick's
        #              synthetic-event proof). The consequential verb iff the action is a CC-launch.
        # op="add"   — author a NEW trigger row (gated by §2.3-B; until resolved, author as a committed
        #              trigger/<id>.py, like flows). 
        # op="arm"   — (needs-tim) flip the driver's env gate for an event source. Refuses-loud unless
        #              operator-authorized — the BUILT-NOT-ARMED floor (§F).
```

- `op="run"` is the by-USE proof — feeding a synthetic event fires the matching rows, exactly as
  `activation.sense_tick(raw_event)` proves the sense path without a live OS hook (`activation.py:458-487`).
- The tool's ACTIONS resolve through the SAME routing the graph engine uses (`rules.route` for cheap kinds;
  scheduler `run` for `run_node`/`run_graph`) — so it "lives in the graph/MCP layer, connected to routing"
  as the task specifies. (SCAN §2.4.)

---

## §F — THE FLOOR RECONCILIATION (the keystone, expanded)

| Surface | Mechanism | Floor status |
|---|---|---|
| **Layer 1 — rule-routing** | `rules.route()` over 5 `DESTINATION_KINDS` (`rules.py:491`) | A trigger may NEVER emit `resolve`/`approve`/`dispatch` (`FORBIDDEN_DESTINATION_VERBS`, `rules.py:130`). Holds **by construction** — there is no op/destination by which a rule launches a `claude -p`. |
| **Layer 2 — CC-launch** | run a node/graph → scheduler → session-supervisor `/spawn` | Autonomous launch is the *legitimate purpose* of this layer (`routine_runner` "the consequential verb"). Bounded by `COMPANY_FABRIC_CONCURRENCY=3`, plan-mode floor spawn (`--allowedTools mcp__company`), and the **BUILT-NOT-ARMED driver**. Wider tools ride the consent/`bridge-session` path (`session_supervisor.py:895-989`). |

**Three load-bearing rules this design holds to:**
1. **No 6th destination.** We do NOT add `dispatch` to `rules.route`. A CC-launch is a *node the trigger
   runs*, not a rule verb (avoids SCAN §7(b) trap).
2. **Driver is BUILT-NOT-ARMED.** `trigger_driver` mirrors `activation_driver`'s dormant posture
   (`activation.py:330-348` — env-gated `COMPANY_ACTIVATION_LOOP`, "do NOT stand up an always-on
   GPU-consuming daemon — that is the operator's call"). The mechanism is proven by USE (`op="run"` /
   synthetic event); the always-on event SOURCES stay needs-tim. This satisfies the standing
   *Autonomous-Spawn-Lead-Only* / *No-Autonomous-Self-Modifying-Build* rules: a build-worker must never arm
   the driver.
3. **cc_launch defaults to the floor spawn** — plan permission + `mcp__company` only; a consent-posture
   flag refuses-loud on a plain spawn and teaches the bridge path (`session_supervisor.py:816-817`).

---

## §5 — THE TRIGGER DRIVER (`runtime/trigger_driver.py`) — the biggest NEW piece

CLONE the `activation` driver shape: a **tickable decision layer, NOT a daemon** (`activation.py:330-348`).

```python
# runtime/trigger_driver.py   (BUILD)
@dataclass
class TriggerDriver:
    suite: Any
    since: int = -1                              # held event-log cursor (mirrors RollupDriver.since, activation.py:504)
    def tick(self):                              # the always-on caller would invoke this on a cadence (needs-tim)
        new = [e for e in self.suite.events_since(self.since) if e.get("kind") in self._watched_kinds()]
        for ev in new:
            for trig in self.suite.trigger_registry.for_event(ev["kind"]):    # priority order, first-match-wins
                snap = self._event_snapshot(ev)                               # the dict `when` reads
                if trig.matches(snap):                                        # rules.evaluate (REUSE)
                    self._act(trig, ev)          # cheap → rules.route ; run_node/graph → scheduler (§F)
        self.since = self._head_seq()
```

- **REUSE** `events_since` + the cursor pattern (the EXACT shape `RollupDriver.tick` uses,
  `activation.py:506-529`), `rules.evaluate` for `matches`, `rules.route` for cheap actions, the scheduler
  `run` for CC-launch.
- **needs-tim** the always-on caller (a tick loop) + `op="arm"` for each event source. The tick itself is
  pure-ish and provable by feeding one synthetic event.

---

## §6 — REUSE vs CLONE vs BUILD (the consolidated ledger)

| Item | Source (Observed) | Verdict |
|---|---|---|
| `rules.RULE_OPS` + `validate_ast` + `evaluate` (the `when`) | `rules.py:65` | **REUSE** ★ biggest win |
| `rules.DESTINATION_KINDS` + `route()` + `FORBIDDEN_*` (cheap actions + the floor) | `rules.py:114,130,491` | **REUSE** |
| `mode_detection_rules.py` (file-disc + when + priority + `_build` + `as_records`) | whole file | **CLONE** (template) |
| `activation_driver` / `RollupDriver` dormant-posture + cursor | `activation.py:330-348, 504-529` | **CLONE** (posture) |
| supervisor `/spawn`→`/watch done` (all CC-launch inputs in one POST) | `session_supervisor.py:804-891,1086-1110` | **REUSE** |
| `routine_runner.fire` orchestration PATTERN (spawn→inject→watch→teardown) | `routine_runner.py:94-130` | **REUSE** (pattern) |
| node contract + scheduler output→address + VOLATILE | `registry.py:75-90`; `scheduler.py:48`; `nodes/AGENTS.md:15` | **REUSE** (slot) |
| cc_board typed edges + `relations(…, "in")` (attach + find reply) | `cc_board.py:157-170, 380-410` | **REUSE** |
| `_CORPUS_REGISTRIES` + `create.py` kind-derive (free MCP author) | `suite.py:360`; `create.py:28-34` | **REUSE** (conditional — §2.3-B) |
| `mcp_face/tools/{routines,flows,node}.py` (the tool template) | `mcp_face/tools/` | **CLONE** (template) |
| **`structured_output` capture** (`_turn_done` + msg_clone + routine readers) | `:1086-1097`; `cc_clone.py:331`; `routine_runner.py:115` | **BUILD** |
| **`nodes/cc_launch.py`** | — | **BUILD** |
| **`runtime/triggers.py` + `TriggerRegistry` + `trigger/` dir** | — | **BUILD** (clone) |
| **event-kind taxonomy first-class** (`event_kinds/` or validate-against) | `activation.py:64-106` | **BUILD** (the registry-is-truth gap — open Q-A *decision*) |
| **`runtime/trigger_driver.py`** | — | **BUILD** ★ THE single biggest new piece |
| **`board.filed` emit** (suite/MCP boundary, NOT in cc_board) | `cc_board.py` + `suite._emit` | **BUILD** (1 emit) |
| **`board_edges/responds_to.py`** | mirror `promoted_from.py` | **BUILD** (1 ROW) |
| **`mcp_face/tools/triggers.py`** | — | **BUILD** (clone) |
| `trigger/AGENTS.md` drift-home + acceptance test | mirror `mode_detection_rules/AGENTS.md` | **BUILD** |

---

## §7 — OPEN QUESTIONS FOR TIM (do not resolve unilaterally)

- **A · event-kind taxonomy** — file-discovered `event_kinds/` (purest) vs validate against
  `ACTIVATION_CONTEXTS` in-place vs "a trigger is a new activation-context"? (§2.2; tentative: A1.)
- **B · `create(kind='trigger')` for free** — resolve WHY `mode_detection_rules` (also pure-data) was kept
  off `_CORPUS_REGISTRIES` before promising the create-path; the dedicated `triggers` MCP tool ships
  regardless. (§2.3.)
- **C · scope shape** — the task says "scoped global/project/user *like the forms design*." The `forms/`
  registry here has NO such scope field (`forms.py:61`); the project/shared/global precedent lives
  elsewhere (episodic-adaptation scope-isolation; `mode_scope` on roles). So `scope:{level, ref}` is
  proposed as a declared trigger field — **confirm which "forms design" Tim means** (likely the Vi-Chat
  forms/wizard scoping, not this registry).
- **D · single-fire vs re-fire + dedup, AND the self-trigger loop guard (§3.4 ★)** — should a trigger that
  matched an event fire once per event, and how is "already handled" recorded? The acute case is the
  self-trigger loop (a `responds_to` reply re-emits `board.filed`); the grounded fix is the
  `OPERATOR_ACTIVITY_KINDS` self-exclusion pattern (`activation.py:359-364`) — exclude `responds_to`-edged
  items, or stamp emits with an origin like `surface_review`'s `origin="responsive"`. Mirrors
  `routine.repeats` / `run_goal_loop` bounding but for event-driven firing.
