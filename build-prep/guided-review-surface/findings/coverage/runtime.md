# Runtime Coverage Sweep — Guided-Review-Surface Relations

## Overview
The runtime modules form the **reactive execution spine** (scheduler + cognition + governance) that the guided-review-surface will plug into as a **right-hand-man walkthrough surface** — an operator-directed mode where screens/nodes are walked through, decisions marked, and autonomous builds triggered. This document maps every runtime module's relationship to the guided-review-surface build.

---

## Module Relations (by kind)

### USE — Faculties the Surface Composes Directly

#### scheduler.py (Lines 1–185)
- **What it does**: The reactive scheduler (S1) — nodes fire when their input addresses resolve in the store; outputs persist to addresses.
- **Guided-Review relation**: 
  - The surface's `mark` actions (marking nodes/edges/decisions) are **addressing operations** — writing tagged values to `run://` addresses that the scheduler reads during a walkthrough run.
  - Control verbs: `branch` (timelines for what-if scenarios), `pause` (hold nodes mid-walkthrough), `force` (re-run a node after review).
  - The `memo_gate` (reuse what hasn't changed) becomes transparent to the operator — "regenerate" vs "skip this part" is a UI choice, not a code concern.
- **Evidence**: Lines 37–54 define the `run()` interface: `pause=` and `force=` are already there; `branch=` coexists with main.
- **Integration**: `Suite.run()` calls `scheduler.run()` with `pause`/`force`/`branch` set from walkthrough state.
- **Unification**: The pause/force/branch controls are **already live primitives** — surface exposes them as "pause this", "regenerate", "what-if branch". No new scheduler concepts.

#### governance.py (Lines 1–281)
- **What it does**: The act-unwatched policy (S7) — AUTO / SURFACE / CONFIRM postures per action class. The `Inbox` gates all surfaced decisions.
- **Guided-Review relation**:
  - `SURFACE` actions (meaningful but recoverable) are the walkthrough's **natural class** — operator reviews, Tim decides.
  - `surface()` (lines 95–143) is where walkthrough decisions live — each marked node/decision is a surfaced item (sid).
  - `resolve()` (lines 184–197) is operator path to approve without `code_build` confirmation (walkthrough IS the review).
  - **T1-RACE fix** (lines 98–118): surfaced_lock serializes create→mint→save so concurrent marks don't lose-update ids.
- **Evidence**: Line 27: `"decision_build": AUTO`; Line 37: `"review": CONFIRM`; Lines 78–143: `Inbox` is SINGLE surfaced-item store.
- **Integration**: `Suite.surface_review()` for review items; walkthrough marks → `surface()` with action_class scoped to walkthrough.
- **Unification**: Walkthrough marks are already `surface()` calls under governance — no new governance class needed.

#### cognition.py (Lines 1–327)
- **What it does**: The concurrent cognition gate (G0–G2) — fires roles via `run_role()` / `run_swarm()`, validates JSON, reads rules.
- **Guided-Review relation**:
  - A walkthrough **IS a role's turn** — operator is the "utterance" (implicit: "review this graph / this section"). Marks are the walk's **output schema**.
  - `run_role()` (lines 93–142) is the ONE place a role fires; walkthrough-as-a-role fires the **same way**.
  - `run_swarm()` fires N roles concurrently; walkthrough firing multiple mark-collectors uses same pool.
  - **Output schema** (C1.4): Walkthrough mark's structured output (node id, decision type, reason) is Pydantic BaseModel, validated same way.
- **Evidence**: Lines 79–89: Role registry discovers roles/focus.py, roles/recall.py, roles/ground.py; roles/guided_review.py auto-registers.
- **Integration**: A walkthrough role is a role that fires synchronously with operator's voice/clicking as input.
- **Unification**: Guided-review IS a role in the registry — not a new execution model, a role fired in response to operator navigation.

#### activation.py (Lines 1–328)
- **What it does**: Concurrent Cognition G5 — activation contexts (background, sense, rollup) fire mode's cast under mode-allocated budget.
- **Guided-Review relation**:
  - Guided-walkthrough is **a new ACTIVATION CONTEXT** (alongside background/sense/rollup) — fires when operator clicks "walk through graph X".
  - `fire_activation()` (lines 141–244) is template: check context registered, get mode's allocation, fire cast, route to surface/address/lane (never resolve/approve/dispatch).
  - Walkthrough **destinations** are `["surface", "address"]` — marks land at `run://` addresses (scheduler reads) + surface (operator approval).
  - Walkthrough **reserve_r** (slot budget) is part of mode's allocation — doesn't starve per-turn live reply.
- **Evidence**: Lines 64–106: `ACTIVATION_CONTEXTS` registry declares 4 contexts; fifth `"guided-review"` belongs here.
- **Integration**: New `ACTIVATION_CONTEXTS["guided-review"]` entry + fire_activation call in bridge when operator initiates walkthrough.
- **Unification**: Guided-review is FIFTH activation context, completing non-turn landscape (idle, event, timer, operator-directed). No new primitives.

#### context_variables.py (Lines 1–324)
- **What it does**: C6 — RHM's context resolution engine. Variables declared, registered, resolved per turn.
- **Guided-Review relation**:
  - Walkthrough's **seeing half** (what operator sees at each step) is context-variable bundle — `selection` (highlighted node), `trajectory` (walk so far), `run_state` (which failed/stuck/ready).
  - New walkthrough variables can register into REGISTRY: `walkthrough_focus` (current section), `walkthrough_path` (walk so far), `walkthrough_changes` (what's changed).
  - `resolve_context()` (lines 83–95) is per-turn bundle builder; walkthrough calls with walkthrough variables to get RHM's view of "what to show operator next?"
- **Evidence**: Lines 103–183: Selection / RunState / Trajectory variables resolve from graph state.
- **Integration**: Walkthrough variables register in context_variables.py (NO new file). Called at module load alongside existing vars.
- **Unification**: Walkthrough's "what to show operator" is EXACTLY context-variable resolution — no new abstraction. Add variable classes + register.

#### rules.py (Lines 1–350+)
- **What it does**: Concurrent Cognition G3 — rule ENGINE. Rules are DECLARED DATA (AST, not code); evaluator over resolved values.
- **Guided-Review relation**:
  - Walkthrough **decisions are rules** — **declared, deterministic logic** over marked-up graph state. Routes to surface/address, never resolve/dispatch.
  - A walkthrough rule is AST-shaped (same RULE_OPS language): `{"op": "and", "args": [...]}`
  - `validate_ast()` (line 149+) is commit-time gate: bad rules fail loud.
  - `FORBIDDEN_DESTINATION_VERBS` (lines 128–130) — NO rule emits `resolve`/`approve`/`dispatch`. Walkthrough's marks are surfaced, not auto-approved.
- **Evidence**: Lines 65–88: `RULE_OPS` (closed grammar); Lines 114–126: `DESTINATION_KINDS` (five routes); Lines 128–130: No rule dispatches autonomously.
- **Integration**: Walkthrough rules registered in rule registry (Suite._rule_from_spec) like any role's declared rules.
- **Unification**: Walkthrough's decision logic IS the rule language — no new DSL. Role declares rules in AST shape; evaluator runs against graph state.

#### compile.py (Lines 1–150)
- **What it does**: C5 — workflow→execution compiler. Graph (workflow, pixels) becomes ExecNodes (addresses, inputs wired as refs).
- **Guided-Review relation**:
  - Walkthrough **run** is a compilation + scheduler run with walkthrough-driven pauses/marks.
  - When operator reviews graph, `compile()` called (like normal run). Graph becomes ExecNodes with address-wired inputs.
  - **Walkthrough mark** at node X is pause/force on ExecNode for X — scheduler won't advance until operator marks "ok" / "change" / "regenerate".
  - Multi-output nodes emit only ports written (selective emission = pruned branches). Walkthrough can visualize which ports written/pruned.
- **Evidence**: Lines 47–113: `compile()` turns Graph into ExecNodes; no specialization needed for walkthrough.
- **Integration**: Walkthrough uses compile() as-is (no changes).
- **Unification**: Compile is generic over node-type and walkthrough/normal runs — no walkthrough-awareness needed.

#### registry.py (Lines 1–112)
- **What it does**: C2/S4 — live node-type registry. Nodes DISCOVERED from files (not hardcoded); queryable + serves object_info to frontend.
- **Guided-Review relation**:
  - Walkthrough's **node palette** is registry's `types` dict — operator picks node types, walkthrough walks through usage.
  - `produces()` / `consumes()` (lines 93–97) help walkthrough suggest "which nodes follow this one?" (wiring question).
  - `object_info()` (lines 100–101) serves FE node-type schema. Walkthrough uses to show operator what each node does.
- **Evidence**: Lines 55–73: `discover()` discovers nodes; Lines 75–90: `register_module()` builds NodeType; Line 88: `output_schema` stored.
- **Integration**: Walkthrough reads registry (Suite.object_info / Suite.list_types).
- **Unification**: Registry is pure discovery/query engine — walkthrough doesn't modify it.

#### roles.py (Lines 1–80+)
- **What it does**: G2 — file-discovered ROLE registry. Roles declared in roles/*.py; schema is SUPERSET (covers judge's config-only role AND fire-able cast roles).
- **Guided-Review relation**:
  - Walkthrough's **walkthrough role** (`roles/guided_review.py`) registers like any other role. Walkthrough fires as a role (under cognition).
  - Walkthrough role's **output_schema** is structured walk (marked nodes, decisions, reasons). Validated same as recall/ground.
  - Walkthrough role's **rules** decide what surfaces/persists based on walk so far.
  - Role schema's `mode_scope` determines which modes walkthrough available in (e.g., `["command-center"]` or `["*"]`).
- **Evidence**: Lines 61–73: `ROLE_FIELDS` — schema; Lines 75–90: `Role` dataclass; Lines 1–50: "adding role = adding file".
- **Integration**: New `roles/guided_review.py` file that declares walkthrough role. Suite.role_registry() discovers automatically.
- **Unification**: **Walkthrough IS a role in registry** — not new execution model, a role fired in response to operator navigation.

#### authoring.py (Lines 1–120+)
- **What it does**: C7.4/C7.5 — authoring backend. Fields → source renderer (generates roles/*.py); gate validates module outside live tree.
- **Guided-Review relation**:
  - Walkthrough's **field-schema editor** rendered by authoring — when operator clicks "add mark type", authoring.render_role_source() generates the role.
  - Gate (lines 15–22) validates proposed role in temp dir — bad spec fails loud before reaching live tree.
  - `FIELD_TYPES` (lines 48–55) is closed registry of field types operator can use. Walkthrough mark's fields chosen from this set.
- **Evidence**: Lines 85–150: `render_role_source()` — ONE renderer; Lines 64–77: `_safe_role_id()` validates; Lines 44–55: `FIELD_TYPES`.
- **Integration**: Authoring used by Suite to render/validate roles. When operator designs walkthrough mark, Suite calls authoring.render_role_source().
- **Unification**: Authoring is pure renderer/validator — walkthrough uses to generate role schema when operator designs it.

#### implement.py (Lines 1–120)
- **What it does**: W1 — launch round-trip. Spawns `claude -p`, captures structured JSON result, never scraped text.
- **Guided-Review relation**:
  - Walkthrough's **"generate" button** calls implement.dispatch(). Launches claude -p with marked-up decisions as instruction.
  - `changed_delta()` (lines 111–126) is ground truth for what build actually changed (content-hash comparison, not model's self-report).
  - **Safety layer** (lines 34–72): `permission_mode()` returns "plan" (safe, read-only) by default; `wire_armed()` checks opt-in. Walkthrough respects same.
  - `LaunchError` (lines 75–77) fails loud on non-JSON / timeout / crash. Walkthrough build either succeeds with structured results or surfaces error loud.
- **Evidence**: Lines 34–54: Permission modes + arming gate; Lines 80–108: Git-based diff helpers; Lines 75–77: `LaunchError`.
- **Integration**: Suite.resolve_surfaced() (operator approves walkthrough build) calls implement.dispatch() with marked-up instruction.
- **Unification**: Implement is pure round-trip launcher — walkthrough uses to dispatch builds based on marked decisions.

---

### TOUCH — Shared Hot Files / Contracts the Build Changes

#### suite.py (Lines 1–9776) **[CRITICAL SEAM]**
- **What it does**: MAIN RUNTIME CLASS — ONE interface to whole system. Owns chat/cognition/governance/modes/rules/roles/graph ops. 9776 lines, interconnected.
- **Guided-Review relation**:
  - `chat()` / `chat_parts()` (lines 5223–5413) are existing operator paths. Walkthrough is **third path** (alongside chat and direct operations).
  - `surface_review()` (lines 9250+) is where walkthrough marks (decisions) live — surfaced items operator resolves.
  - `cast_for_mode()` (lines 4654–4658) returns roles for current mode. Walkthrough uses to know which roles active.
  - `activation_allocation()` (lines 1524–1536) declares which contexts live + budget. Walkthrough context registered here (mode-scoped).
  - `get_mode()` / `set_mode()` (lines 1610–1619) read/write presence dial. Walkthrough may operate in specific modes.
  - `shape_for()` / `grain_for()` / `mode_stages()` (lines 1569–1593) describe mode's staging. Walkthrough uses to understand mode's shape.
  - `run()` (calls scheduler.run() with pause/force/branch). Walkthrough calls with marked nodes as pause/force points.
  - `resolve_surfaced()` (operator-only: approve/reject). Walkthrough build (surfaced item) resolved here.
  - **CRITICAL SEAM**: `resolve_role()` reads role.spec for binding. Walkthrough role resolved here.
- **Evidence**: Lines 266–358: `__init__()`; Lines 5288–5412: `chat_parts()`; Lines 4654–4703: `cast_for_mode()` + `capability_providers()`.
- **Integration**: 
  - New methods (or orchestrated via existing): `fire_walkthrough()`, `mark_walkthrough_decision()`, `apply_walkthrough_build()`.
  - These are thin — orchestrate existing methods (fire_activation, surface_review, resolve_surfaced, implement.dispatch).
- **Unification**: 
  - **CRITICAL**: Walkthrough is NOT parallel path — it's **composition of existing methods**. Suite's CORE unchanged; walkthrough is **choreography** (like chat_parts is choreography of run_swarm + rules.route + context resolution).
  - No new Suite method REQUIRED; bridge orchestrates existing methods directly. But thin wrappers improve clarity (Suite's public API for guided-review).

#### bridge.py (Lines 1–1600) **[CRITICAL SEAM]**
- **What it does**: HTTP handler (H) — translates HTTP requests into Suite calls + streams responses. Operator's channel to runtime.
- **Guided-Review relation**:
  - New `/api/walkthrough` endpoints (POST): initiate, step, mark, generate.
  - `_voice_stream()` (lines 734–920) is existing chat streaming path. Walkthrough stream reuses SSE + ndjson pattern.
  - `emit()` (line 774+) is single emitter (ndjson line ordering safe). Walkthrough emissions (kind="walkthrough.*") go here.
  - Request parsing (lines 400–450 in GET, 923+ in POST) — walkthrough request carries graph_id, focus, mode, action.
  - Response streaming — walkthrough results streamed (each step as decided, not single final response).
- **Evidence**: Lines 734–920: `_voice_stream()` template; Lines 774–845: Single emit; Lines 400–450: GET parsing; Lines 923–1000+: POST routes.
- **Integration**:
  - New POST `/api/walkthrough/{action}` routes:
    - `POST /api/walkthrough/start` → Suite.fire_walkthrough() → emit walkthrough.start → stream steps.
    - `POST /api/walkthrough/mark` → Suite.mark_walkthrough_decision() → emit walkthrough.marked → stream next context.
    - `POST /api/walkthrough/generate` → Suite.apply_walkthrough_build() → stream build progress + results.
  - Each route is thin wrapper around Suite calls (request → Suite method → emit → respond).
- **Unification**: Walkthrough routes don't need new streaming logic — reuse `_emit()` + ndjson. Stateless HTTP model (no WebSocket).

---

### RELATE — Sequences / Addressed Substrate / Cognition Modes

#### The Sequences Primitive
Walkthrough IS a sequence — **deterministic path through decision tree**. Scheduler's sequences (resume, branch, pause) applied to walkthrough's path (operator-directed navigation). Walkthrough sets `pause` on unreviewed nodes; scheduler waits. When operator marks "ok", Suite calls `scheduler.run()` again with node removed from `pause` (sequence resumes).

**Observed** (suite.py line 37: `pause` param); **Inferred**: walkthrough uses pause/resume as navigation primitive.

#### Addressed Substrate
Every walkthrough mark is a **run:// address**:
- `run://walkthrough-{turn_id}/mark-{step}` — marked decision (JSON: node_id, decision, reason).
- Marks **persisted** (CAS-backed store) so walkthrough can be replayed, audited, resumed.
- Rules read marked addresses (evaluator gets resolved dict with every mark), so walkthrough's logic is **data-driven, not code-driven**.

**Observed** (scheduler.py line 76, store.head(addr)); **Inferred**: walkthrough marks are addresses. **Unification**: marks are NOT special — addressed data, same substrate scheduler uses.

#### Cognition Modes
Walkthrough is **mode-aware** — respects mode's allocation (C5.5), shape (C4.1), cast (C2.3). Walkthrough in "command-center" (high-authority, slow) routes differently than "listening" (fast, minimal marks).

**Observed** (suite.py line 1614: `set_mode()`; activation.py line 167: mode param); **Inferred**: walkthrough mode-scoped. **Unification**: walkthrough context's `destinations` and `reply` vary by mode (MODE_REGISTRY + ACTIVATION_ALLOCATION rows).

---

## Critical Unification: **WALKTHROUGH IS A ROLE UNDER A NON-TURN ACTIVATION CONTEXT**

The existing Company architecture ALREADY HAS the right layer:
1. **Role** (file-discovered, prompt+schema) — walkthrough is a role.
2. **Activation context** (non-turn trigger, mode-allocated budget, surface/address routes) — walkthrough is a context.
3. **Rules** (declared routing) — walkthrough decisions are rules.
4. **Addressed substrate** (run://) — marks are addresses.
5. **Governance** (SURFACE posture) — marks are surfaced decisions.

**NO new abstractions needed.** Guided-review-surface is a **COMPOSITION**:
- Suite.fire_activation(context="guided-review") fires walkthrough cast.
- Rules (G3) route operator marks to surface/address/lane.
- Operator's voice/clicking provides marks (utterance-like input to role).
- Suite.resolve_surfaced() approves marked-up build.
- Implement.dispatch() launches build.

**What the build adds:**
- `roles/guided_review.py` file (walkthrough role).
- Entry in activation.py's `ACTIVATION_CONTEXTS` (guided-review context).
- Bridge routes (/api/walkthrough/*) orchestrating Suite calls.
- UI (walkthrough canvas + mark tools) — OUTSIDE runtime.

**Runtime CORE remains UNCHANGED. Walkthrough IS the system, reused.**

---

## Module Status Summary

| Module | Relation | Status | Build Impact |
|--------|----------|--------|------|
| scheduler.py | USE (pause/force/branch) | ✅ Complete | Walkthrough uses as-is. |
| governance.py | USE (surface, Inbox, T1-RACE) | ✅ Complete | Marks are surfaced items; T1-RACE enables concurrent marks. |
| cognition.py | USE (role firing, schema validation) | ✅ Complete | Walkthrough fires as role; uses run_role/run_swarm. |
| activation.py | USE (non-turn context, routing) | 🟡 Complete, needs registry entry | Add "guided-review" context row. |
| context_variables.py | USE (resolution engine) | 🟡 Complete, add walkthrough vars | Register 3–4 new variables. |
| rules.py | USE (declared routing) | ✅ Complete | Walkthrough rules are AST-shaped; same evaluator. |
| compile.py | USE (graph→ExecNode) | ✅ Complete | Walkthrough calls compile(); no changes. |
| registry.py | USE (node-type discovery) | ✅ Complete | Walkthrough reads registry. |
| roles.py | USE (role discovery) | 🟡 Complete, add guided_review role | Write roles/guided_review.py. |
| authoring.py | USE (field→source renderer) | ✅ Complete | Walkthrough uses to generate/validate schemas. |
| implement.py | USE (dispatch launcher) | ✅ Complete | Walkthrough respects permission_mode() + wire_armed(). |
| suite.py | TOUCH (orchestration hub) | 🟡 Complete, add thin wrappers | fire_walkthrough() / mark_walkthrough_decision() / apply_walkthrough_build(). |
| bridge.py | TOUCH (HTTP handler) | 🟡 Complete, add routes | New /api/walkthrough/* POST routes. |

---

## Build Scope (Zero new primitives)

**Additive ONLY:**
1. **activation.py**: One row in ACTIVATION_CONTEXTS ("guided-review") + reflect in runtime/AGENTS.md.
2. **roles/guided_review.py**: New file (auto-discovered).
3. **context_variables.py**: Register 3–4 new variable types.
4. **suite.py**: Add 3 thin orchestration methods (optional).
5. **bridge.py**: New /api/walkthrough/* POST routes.

**Everything else: unchanged.** The system is already built for exactly this use case.
