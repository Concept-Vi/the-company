# SCAN — the reusable "Claude Code launch NODE"

Read-only scan. Goal: find what to build a composable **CC-launch NODE** on — a unit whose
INPUT is `{prompt, startup-flags, model/provider, context-address}` and whose OUTPUT is a
`{structured result → written to an address}`. Tim's framing: *"launching the CC is basically
input variable + output variable for Claude Code."*

All paths absolute. Each piece tagged **REUSE** (exists, build on it) / **BUILD** (gap, must
write) / **REUSE+BUILD** (the seam where a real gap sits inside an otherwise-reusable thing).

---

## The two layers (do not collapse into one "primitive")

1. **Composition shell** — `nodes/*.py` + `NodeRegistry` + `scheduler.py`.
   Gives ports-in/ports-out AND address-in/address-out *for free*. This IS Tim's "input
   variable + output variable" as a wireable unit. **REUSE.**
2. **Launch+capture engine** — the session-supervisor's `/spawn`(prompt, model, provider,
   flags) → `/watch` `done` cycle. This is what actually runs a `claude -p` and returns its
   reply. **REUSE** (with one BUILD seam: structured-output capture).

The CC-launch NODE = a thin `nodes/` module whose `run()` calls the launch engine. There is
ALSO an existing intermediate that is 80% of the deliverable already: **`routine_runner.fire()`**
(a CC launch as a named, fireable, addressable unit) — see §6.

---

## §1 — SUPERVISOR: programmatic spawn with prompt / flags / model / provider  **REUSE**

`/home/tim/company/runtime/session_supervisor.py` — ONE long-running service (127.0.0.1:8771)
that owns N `claude -p` subprocesses under held-open `--input-format stream-json`. This is the
push tier; a held process accepts injected turns while idle with full memory + same session_id.

**The input-variable surface — `SessionSupervisor.spawn(...)`** (def `session_supervisor.py:804-891`):
- `prompt` rides the HTTP `/spawn` body and is auto-injected as the first turn
  (`bridge`/route at `session_supervisor.py:1603-1604`: `if body.get("prompt"): SUP.inject(...)`).
- `model`, `effort`, `fallback`, `permission_mode`, `settings`, `add_dir`, `output_format`,
  `include_partial`, `debug`, `safe_mode`, `bare` — all dedicated body keys, threaded through to
  the **pure command builder** `_build_spawn_cmd` (`session_supervisor.py:612-695`). Pure +
  unit-testable; byte-identical to today's cmd when nothing extra is passed.
- `provider='ollama'` — the **ollama path** (`session_supervisor.py:651-655`): runs
  `ollama launch claude --model <tag> -- -p …` instead of `claude -p` (NOT an env overlay — a
  logged-in Claude Code ignores ANTHROPIC_* env and rejects the model name; the launcher
  redirects correctly). `_provider_env` returns `{}` always (`:697-707`). PATH fix at `:853-854`.
  Context-size model pick for ollama lives in `runtime/cc_clone.py:193-215` (`pick_ollama_model_for_context`).
- `flags={…}` — the **registry-declared start-flag surface** (`SPAWN_FLAG_ASSEMBLY`,
  `session_supervisor.py:258-373`). ~50 declared `--flags`; posture (locked/consent/safe) is
  DERIVED from the Mirror-Registry, not hand-stored (`_registry_posture`, `:400-409`;
  `_apply_spawn_flags`, `:412-468`). A consent-posture flag (widens surface) refuses-loud on a
  plain `/spawn` and teaches the `/bridge-session` path.

**HTTP API** (`SUPERVISOR_ROUTES`, `:127-136`; handlers `do_GET`/`do_POST`, `:1510-1685`):
`GET /health · /sessions · /watch?session=<id>` ; `POST /spawn · /inject · /interrupt ·
/teardown · /bridge-session`.

**The output-variable surface — `/watch` → the `done` event:**
- `_reader` parses the stream for the life of the process (`:1028-1084`); on a `result` event
  it calls `_turn_done` (`:1086-1110`).
- `_turn_done` fans `{type:"done", result, claude_session_id, num_turns, is_error}` (`:1095-1097`)
  and stamps a durable `agent_sessions.turn` event WITH cost/usage (`_extract_usage`, `:515-553`).
- A `done` event's `result` is **prose** (`ev.get("result")` or joined assistant text, `:1088`).

**`/bridge-session`** (`spawn_bridge_session`, `:895-989`) = the consent-gated WIDER-allowlist
spawn (Bash/git/LSP/web + file writes). Needed only if the CC-launch node must EDIT/RUN, not just
read. Floor spawn is `--allowedTools mcp__company` only.

**Concurrency bound (composition constraint):** `COMPANY_FABRIC_CONCURRENCY` (default **3**),
`fabric_concurrency()` `:145-150`, enforced `_cap_check` `:600-610`. A graph firing >3 CC-launch
nodes in parallel hits `TeachingRefusal` (429). Per-turn wall-clock watchdog: `turn_timeout_s()`
default 900s, `:1197-1215`.

---

## §2 — cc_clone: the WORKING TEMPLATE for "launch → capture reply"  **REUSE (copy the pattern)**

`/home/tim/company/runtime/cc_clone.py` — the cleanest end-to-end example of *spawn a supervised
CC + capture its reply*. The CC-launch node should copy this minus the materialize-from-past step.

- `clone_at(...)` (`cc_clone.py:218-284`) — builds `spawn_body` (`:255-261`) with `model` /
  `fallback` / `provider`, POSTs `/spawn` (`:262`), `_wait_idle` (`:91-101`), registers the unit.
- **`msg_clone(handle, message)`** (`:303-339`) — THE reply-capture primitive: open `/watch`
  BEFORE `/inject` (so no events are missed, `:311-316`), inject the message, read the stream
  until `type=="done"`, return `{reply: ev["result"]}` (`:330-339`).
- `clone_address(rec)` (`:342-350`) → `clone://<source_sid>/<at>` + `get_by_address` (`:367-388`)
  — the provenance-stable addressing pattern (a CC-launch node's runs could be addressed the same).
- Already exposed as an MCP tool: `/home/tim/company/mcp_face/tools/cc_clone.py` (file-drop
  auto-register; ops clone/msg/onboard/list/end/prepare/resolve). Confirms "this kind of unit
  slots into the agent surface as a tool" — but it is NOT a graph node.

---

## §3 — STRUCTURED OUTPUT  **REUSE (input) + BUILD (capture seam)**

This is the central REUSE-vs-BUILD seam for the node's "output: structured result → address".

**Input side — the flag exists. REUSE.**
- `--json-schema` is a declared spawn flag: `SPAWN_FLAG_ASSEMBLY["json_schema"]`
  (`session_supervisor.py:278-279`), teach-string: *"schema-validated structured output
  (result.structured_output)"*. So a CC launch CAN be told to emit schema-validated JSON via
  `flags={"json_schema": "<schema-or-path>"}`.

**Capture side — THE GAP. BUILD.**
- `_turn_done` (`session_supervisor.py:1086-1097`) builds the `done` event from
  `ev.get("result")` + usage **ONLY**. It does **NOT** read the result event's
  `structured_output` field. So a CC launched with `--json-schema` *produces* structured output
  and the supervisor *drops* it.
- `msg_clone` (`cc_clone.py:331`) and `routine_runner._capture_done` (`routine_runner.py:81-83`,
  `fire` `:115`) likewise read only the prose `result`.
- **BUILD:** extend `_turn_done` to lift `result.structured_output` (label the exact field name
  Observed-from-teach-string as `structured_output`; confirm vs `structuredOutput` against the
  Claude Code Atlas before relying on it) into the fanned `done` event, and extend the capture
  readers (msg_clone / routine fire) to surface it. THEN the node can output a typed value.

**The OTHER structured-output system (in-engine model calls, NOT CC launches) — context only:**
- `runtime/cognition.py:217` `run_role` — `json=True` sets the transport
  `response_format:{type:"json_object"}`; `schema=` makes `client.complete()` parse+validate+retry
  client-side (`cognition.py:203-280`+). Verified the resident vLLM honours json_schema (memory:
  use `json_schema`, NOT `json_object` — `reference-vllm-structured-output`).
- `runtime/generation_policies.py:35,97-98` — a `json_schema` bool per generation regime (file-
  discovered registry; same drop-in mechanism as nodes/roles).
- `nodes/*` and `roles/*` carry `OUTPUT_SCHEMA` (a dict or a Pydantic model) → read into
  `NodeType.output_schema` (`registry.py:22-39, 88`). This is how a NODE declares "the structured
  thing it produces" — the CC-launch node should declare its `OUTPUT_SCHEMA` here.

---

## §4 — the compositional NODE / dataflow system  **REUSE (the slot to build into)**

`/home/tim/company/runtime/registry.py` — `NodeRegistry`. Node-types are DISCOVERED from files,
not hardcoded (`discover`/`rediscover`, `:55-73`). **Adding a node = dropping a file** in
`nodes/`; it self-registers, becomes queryable in the type-graph, appears in the palette via
`/object_info` — with NO change to runtime/UI/tools (`nodes/AGENTS.md:14-19`).

**A node module's contract** (`register_module`, `registry.py:75-90`; example `nodes/ask.py`):
- `run(inputs: dict, config: dict)` — the only required hook (`registry.py:63`).
- `PORTS_IN = {name: PortType}` / `PORTS_OUT = {name: PortType}` (e.g. `nodes/ask.py:10-11`).
- `CONFIG = {field: {type,label,default,…}}` — the inspector's editable fields (`ask.py:17-24`).
- `OUTPUT_SCHEMA` — dict or Pydantic model → `NodeType.output_schema` (`registry.py:22-39`).
- `KIND`, `VERSION`, and (live-state) **`VOLATILE=True`**.
- The C2 contract object: `/home/tim/company/contracts/node_type.py` (`NodeType`, `Ports`).

**The type-graph wiring by output→input contract** (`registry.py:93-97`):
`produces(port_type)` / `consumes(port_type)` — nodes compose because one's `PORTS_OUT` type
matches another's `PORTS_IN` type. THIS is where a CC-launch node + a trigger node register and
wire.

**Execution / addressing** — `/home/tim/company/runtime/scheduler.py`:
- Reactive resolver, NOT control flow (`scheduler.py:1-17`): a node fires the instant its input
  ADDRESSES resolve in the store; output persists to an address; that resolves downstream.
- `run()` `:37-` reads readiness from the STORE → resume-across-process is free.
- **"Written to an address" is the scheduler's job** — a node's `run()` just returns
  `{port: value}`; the scheduler writes each port to its address (`out_ports`, `:48`; per-port
  addresses B5). Multi-output (prose result + structured value) = two `PORTS_OUT` entries.
- READY = every DECLARED `PORTS_IN` port wired AND resolved (`:72-77`). VOLATILE nodes bypass the
  memo gate (`:88-`).

**MANDATORY for a CC-launch node:** set `VOLATILE=True` — a CC launch reads MUTABLE truth (live
repo, live model). Without it the memo gate serves the first result forever
(`nodes/AGENTS.md:15`).

---

## §5 — run_turn / the loadable-brain single-turn path  (minimal shape, NOT the base)

`/home/tim/company/runtime/ui_claude_session.py` — `run_turn(prompt, session_id?, context_block?)`
(`:79-131`). One subprocess per turn (`claude -p <prompt>` as argv, not stdin-injection),
`--resume` carries the conversation. Yields `init/text/tool/done/error` events; `done` =
`{result, session_id, num_turns, is_error}` (`:120-124`). Exposed at HTTP `/api/claude/turn`
(`bridge.py:1636-1710`, `_claude_stream`; context-address folded in via
`runtime/territory.py:territory_prose`, `bridge.py:1688-1689`).

**Why this is the minimal shape but NOT the build base:** `_turn_cmd` (`:64-76`) HARDCODES
`--permission-mode PANEL_PERMISSION` and `--mcp-config`/`--allowedTools`, and has **no**
`--model` / provider / startup-flags axis. It cannot carry the model/provider(ollama)/flags
inputs the task names. The supervisor's `spawn()` has all of them. Use `run_turn` to understand
the event shapes; build on the supervisor.

---

## §6 — ★ THE TRIGGER-SYSTEM half, and the closest existing primitive

The dir is `trigger-system`. The Company ALREADY has a "CC launch as a named, fireable,
addressable unit" + its trigger arms:

**`/home/tim/company/runtime/routines.py`** — file-discovered ROUTINE registry (`routines/*.py`,
same drop-in mechanism as nodes; `routines.py:1-17`). Each declares
`ROUTINE = {id, prompt, cwd, model, permission_mode, cadence, goal, done_when, repeats, max_turns}`
(`Routine` accessors `:54-110`). **That dict IS Tim's "input variable"** for a CC launch.

**`/home/tim/company/runtime/routine_runner.py`** — `fire(routine_id)` (`:94-130`):
`build_spawn_body` (prompt+model+permission_mode+cwd, `:37-50`) → POST `/spawn` (`:109`) →
`_capture_done` via `/watch` (`:64-91`) → POST `/teardown` → returns a durable RUN RECORD
`{routine_id, claude_session_id, result, is_error, ts, session}` (`:122-130`). **That record IS
the "output variable."** `run_goal_loop` (`:147-175`) = bounded fire→evaluate→re-fire.

**The trigger arms (the "trigger node" half):**
- **schedule arm** — `/home/tim/company/runtime/routine_schedule.py`: generates a per-routine
  systemd `.timer` from the routine's `cadence` (`render_units`/`generate_units`, `:54-91`).
- **manual arm** — the `routines` MCP tool `op=fire` (and the off-machine cron skill `/loop`,
  `/schedule`). The scheduler in §4 is the OTHER trigger style: REACTIVE (fires on
  address-resolution), not cron.

**What routine_runner is NOT (the gaps to a true compositional node):**
1. NOT a graph `nodes/` module — it has no `PORTS_IN/PORTS_OUT/OUTPUT_SCHEMA`, so it can't wire
   output→input with other nodes; it's an imperative `fire()` + a registry, not a dataflow node.
2. Captures only the prose `result` (`routine_runner.py:115`) — the §3 structured-output CAPTURE gap.
3. **`build_spawn_body` (`routine_runner.py:37-50`) only carries `{cwd, prompt, permission_mode,
   name, source}` + `model` — NO `provider`, NO `flags`, NO `effort`/`fallback`.** So calling
   `fire()` as-is CANNOT pass `provider='ollama'` OR `flags={"json_schema":…}`. This bites facet 3
   on the INPUT side too: `--json-schema` rides the `flags` key, and fire() drops it. The supervisor
   `spawn()`/`/spawn` route DO accept these (`session_supervisor.py:1591-1602` reads `provider`+`flags`
   off the body) — the gap is only in `build_spawn_body`'s narrow body.

So the CC-launch NODE has two viable shapes — **prefer (a)**:
  (a) **copy fire()'s PATTERN onto raw `/spawn`** (spawn→inject→watch-done→teardown), building the
      full body incl. `provider` + `flags` directly — reaches every input axis, reimplements ~30
      lines of orchestration.
  (b) **call `fire()`** AND first **BUILD: extend `build_spawn_body` to thread `provider`+`flags`+
      `effort`+`fallback`** — reuses the runner, smaller change, but touches the shared routine path.

Either way: a `nodes/cc_launch.py` module with `PORTS_IN={"prompt":"Text","context":"Text"}`,
`CONFIG={model, provider, permission_mode, flags, json_schema}`,
`PORTS_OUT={"result":"Text","structured":"Json"}`, `OUTPUT_SCHEMA=<the schema>`, `VOLATILE=True`,
`run()` → fire the supervisor circuit → return `{result, structured}`. A `nodes/cc_trigger.py`
(or reuse routines+scheduler) supplies the firing edge.

---

## One-shot vs session (the two variants of "input var → output var")

- **One-shot (ephemeral)** — Tim's pure "input var → output var": `/spawn`(prompt) → watch `done`
  → teardown (exactly `routine_runner.fire` with `keep=False`). Add `flags={"no_session_persistence":
  true}` for no transcript on disk (`SPAWN_FLAG_ASSEMBLY:286`).
- **Session (multi-turn)** — keep the session alive (`keep=True`), thread `session_id` as node
  state, `/inject` further turns (`msg_clone` / `run_turn` resume). Same engine.

---

## REUSE-vs-BUILD summary

| Piece | File:line | Verdict |
|---|---|---|
| Spawn w/ prompt+model+provider+flags | `session_supervisor.py:804-891`, `_build_spawn_cmd:612-695` | **REUSE** |
| `flags` registry (~50 `--flags`, incl `--json-schema`) | `session_supervisor.py:258-468` | **REUSE** |
| ollama provider path | `session_supervisor.py:651-655`; `cc_clone.py:193-215` | **REUSE** |
| `/watch` → `done` capture (prose result) | `session_supervisor.py:1028-1110`; `cc_clone.py:303-339` | **REUSE** |
| structured_output INPUT (`--json-schema`) | `session_supervisor.py:278` | **REUSE** |
| structured_output CAPTURE (lift `result.structured_output`) | `_turn_done:1086-1097`; `msg_clone:331`; `routine_runner.py:115` | **BUILD** |
| Node contract (ports/config/output_schema/run) | `registry.py:75-90`; `contracts/node_type.py`; `nodes/ask.py` | **REUSE** (slot) |
| Type-graph wiring (produces/consumes) | `registry.py:93-97` | **REUSE** |
| Scheduler writes output→address, reactive | `scheduler.py:37-` | **REUSE** |
| CC-launch-as-unit (prompt+model in, result out) | `routine_runner.py:94-130`; `routines.py` | **REUSE** (closest fit) |
| `build_spawn_body` provider/flags/effort/fallback passthrough | `routine_runner.py:37-50` | **BUILD** (or bypass via raw `/spawn`) |
| Trigger arms (systemd timer / MCP fire / reactive) | `routine_schedule.py`; `routines` tool; `scheduler.py` | **REUSE** |
| `nodes/cc_launch.py` (the node itself) | — | **BUILD** |
| `nodes/cc_trigger.py` (or routines+scheduler edge) | — | **BUILD** |

---

## THE single best existing primitive to build the CC-launch-node ON

**The session-supervisor `/spawn`(prompt, model, provider, flags) → `/watch` `done` cycle**
(`session_supervisor.py:804-891` + `:1086-1110`). It is the only launch surface carrying ALL the
named inputs (prompt, startup-flags, model, provider/ollama) in one POST and returning the captured
output. Build the node's `run()` on it via the proven wrapper pattern in **`routine_runner.fire()`**
(`routine_runner.py:94-130`) — which already does spawn→inject→watch-done→teardown and returns a
durable run record (it is the "CC launch = input var → output var" primitive, just not yet wrapped
as a `nodes/` dataflow module). The one real BUILD inside this otherwise-reuse path is lifting
`result.structured_output` in `_turn_done` so the node can emit a TYPED output, not just prose.
