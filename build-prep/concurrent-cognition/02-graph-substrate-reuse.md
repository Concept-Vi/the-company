# 02 — Graph Substrate Reuse: can the node-graph runtime BE the concurrent-cognition layer?

**Thesis under test:** the Company's existing node-graph runtime can largely BE the substrate
for a concurrent-cognition layer — a *role* is a node, a *chain* is edges, the concurrent
executor is the scheduler, the view is the canvas.

**Verdict in one line:** Three of the four legs hold near-wholesale (role=node, chain=edges,
view=canvas). The fourth — "the concurrent executor IS the scheduler" — is the one that does
NOT hold as-is: the scheduler has the right *shape* (readiness-driven dispatch) but is **strictly
serial**. Making the dispatch parallel is THE net-new build. Everything else is reuse, plus a
request-concurrency budget, an injection/resolve edge type, and one memo consideration.

This is file-line evidence as of the repo state on 2026-06-07. READ-ONLY research; no code changed.

---

## 1. How a node declares config + ports + compute (role = node)

A node-type is a single Python module under `nodes/` — module-level constants + a `run()`. No base
class, no registration call. The registry discovers it from the file (`runtime/registry.py:35-46`,
`discover()` walks the dir, `register_module` reads the attrs).

`nodes/llm.py` is the canonical AI node and the template for a "role" node:

- **Ports (the wiring contract):** `PORTS_IN = {"prompt": "Text"}` (`llm.py:10`),
  `PORTS_OUT = {"text": "Text"}` (`llm.py:11`). Port dicts are `{name: type-string}`. The registry
  turns these into a `NodeType.ports` (`registry.py:60-61`); the canvas draws nubs straight from them
  (`NodeShape.tsx:53-55`).
- **Config (the editable slots):** `CONFIG = {...}` (`llm.py:15-25`) declares each editable field
  (`model`, `system`, `temperature`, `max_tokens`, `top_p`, `retries`, `timeout`). The `model` field
  is an enum whose options come from the live registry — `"options_from": "chat_models"`
  (`llm.py:16`) — so a role's model is a registry-sourced slot, never a hardcoded string (path-of-least
  -resistance law, AGENTS.md rule 8). `registry.py:62` copies `CONFIG` verbatim into
  `NodeType.config_schema`.
- **Compute:** `def run(inputs: dict, config: dict)` (`llm.py:28-39`). `inputs` is `{port: value}`
  resolved from the store; `config` is the node instance's settings. Returns a bare value (single
  output) or a `{port: value}` dict (multi-output).
- **How an LLM node calls a model:** `run()` builds OpenAI-shape messages from `config["system"]` +
  `inputs["prompt"]` (`llm.py:33-34`), builds a transport bound to `base_url`
  (`transport.openai_transport`, `llm.py:36` → `transport.py:28-51`), and calls
  `client.complete(t, messages, model=...)` (`llm.py:38-39`). `fabric/client.py:54-89` is the guarded
  wrapper: retry/backoff + non-empty + JSON-repair + schema-validate, fail-loud (`FabricError`). The
  transport itself is a **blocking `urllib.request.urlopen`** (`transport.py:47`) — this matters for
  concurrency (§5).

`nodes/ask.py` is the same shape with two input ports (`question`, `context`) and a grounding system
prompt (`ask.py:10-13`) — already a two-input "role over context" node. `model_of_tim.py` is a
zero-input content node that reads a file and is `VOLATILE=True` (`model_of_tim.py:11`) so the memo
gate never freezes it.

**Reusability:** a concurrent-cognition "role" is `llm.py`/`ask.py` with a role-specific `system`
prompt + a `model` slot. **No node-type machinery is net-new.** The author-from-registry law already
makes "model = a slot resolved from the live registry" the default.

---

## 2. Ports / edges / per-port addresses (chain = edges)

### Compile: workflow → execution (`runtime/compile.py`)

- Each node gets per-port output **addresses**. Single-output → the bare node address under the key
  `"out"`: `{"out": "run://<graph>/<node>"}` (`compile.py:78-82`). Multi-output (≥2 declared ports) →
  a per-port fragment address each: `{port: "run://<graph>/<node>#<port>"}` (`compile.py:76-77`). Each
  port is a **distinct store key**.
- Each edge becomes an **address reference**: `by_id[edge.to_node].inputs[edge.to_port] =
  src_addr` where `src_addr` is read off the source node's computed `outputs` by `from_port`
  (`compile.py:104-111`). Compile and the scheduler agree by construction (the comment at
  `compile.py:104-108`).
- An edge to/from an unknown node raises (`compile.py:94-103`) — fail loud.

### The edge/port representation

A `Graph` is `nodes: [NodeInstance]` + `edges: [Edge]` (`contracts/node_record.py`; an `Edge` carries
`from_node/from_port/to_node/to_port`, used at `compile.py:93-111`). `ExecNode` carries
`inputs: {port: address}` + `outputs: {port: address}` (`compile.py:83-89`). The canvas commits a wire
through `/api/connect` (the backend type-checks + owns the edge — `NodeShape.tsx:94`,
`onPointerUp` → `CONNECT`).

**Reusability:** a "chain" of roles is exactly edges between nodes. **Output→address→next-node-input is
the existing edge mechanism, not net-new** (this corrects an over-claim — basic chaining is wholly
reusable; only *dynamic/selective* injection is net-new, see §6). Fan-in (a role consuming several
upstream roles) is `nodes/join.py` (concatenate all inputs, `join.py:16-18`) or `nodes/pair.py`
(ordered fan-in, `pair.py:14-15`).

---

## 3. The scheduler: ready-node dispatch — and the serial truth (executor)

`runtime/scheduler.py:37-184` is `run(graph, store, node_types, ...)`.

**The readiness primitive (the right shape):**
- Compile the graph (`scheduler.py:42`), then loop until all nodes processed (`scheduler.py:59`).
- A node is READY only when **every declared input port is wired AND resolved in the store**
  (`scheduler.py:72-77`: `declared <= set(ex.inputs)` and `all(store.head(a) for a in ex.inputs.values())`).
  A half-wired node simply waits — readiness, not run-order.
- Inputs are read by content-hash per port (`scheduler.py:79-81`), the node runs (`scheduler.py:103`),
  the result is content-addressed (`put_content`, `scheduler.py:117`) and written per-port via
  `set_ref` (`scheduler.py:144-150`), recording provenance on every write (`scheduler.py:148-150`).

**The serial truth (why leg 4 of the thesis fails as-is):**
- The dispatch is a single Python `for nid, ex in by_id.items()` loop (`scheduler.py:60`) inside a
  `while ... and progress` loop (`scheduler.py:59`). **Each ready node runs to completion
  (`mod.run(...)`, `scheduler.py:103`) before the next is considered.** There is no thread pool, no
  `asyncio`, no parallel fan-out. Confirmed: `grep ThreadPool|concurrent|asyncio|gather|max_workers`
  over `runtime/` returns nothing in the scheduler.
- So 32 ready "role" nodes today run **one after another, in dict-iteration order** — N serial blocking
  HTTP calls to the model, not N concurrent ones.

**Selective emit + the `gate` node (branching = absence-of-write):**
- A multi-output node returns a `{port: value}` dict; the scheduler writes `set_ref` ONLY for the ports
  present (`scheduler.py:128-150`). An unknown port fails loud (`scheduler.py:135-140`).
- `nodes/gate.py` emits a single-key dict — `{"pass": value}` or `{"fail": value}` (`gate.py:38-40`).
  The untaken port's address is never written, so its downstream never resolves — pruned, not stuck
  (`scheduler.py:155-182` distinguishes pruned vs stuck via transitive closure over not-taken branches).

**Per-node error isolation (a concurrent-cognition asset):**
- A node's `run()` raising is CONTAINED into `result["failed"][nid] = "ErrType: msg"` and the run
  continues for the other ready nodes (`scheduler.py:102-116`). One role crashing does not abort the
  cohort. The Suite surfaces it loud as a `warning` event (`suite.py:771-780`).

**Resume / re-run / branch as addressing ops:** readiness is read from the STORE, not an in-memory map
(`scheduler.py` docstring, lines 4-16), so resume-across-process is free; `pause`/`force`/`branch` are
addressing operations (hold a node, bypass memo, write to `@branch`).

---

## 4. Run / address / store: `Suite.run` and where results live

`Suite.run(graph_id, ...)` (`runtime/suite.py:760-782`) calls `scheduler.run(...)` (`suite.py:762`),
emits a run event with `ran/cached/stuck/failed` counts (`suite.py:765-770`), and emits a distinct
`warning` event if anything failed (`suite.py:775-780`). It is `guard("run", ...)`-wrapped (AUTO posture
— `suite.py:782`).

Results are **content-addressed + per-port-addressed**: a node's output lives at
`run://<graph>/<node>` (single) or `run://<graph>/<node>#<port>` (multi). `Suite.state`
(`suite.py:784-848+`) reads each node's status from the store (cas present → `cached`; in `failed` →
`failed`; in `stuck` → `stuck`; else `idle`) so status survives reload.

The node-type registry is `NodeRegistry` (`runtime/registry.py:30-86`): dict-like
(`reg[name] -> module`), discovered from files, queryable type-graph (`produces`/`consumes`,
`registry.py:67-71`), serves `/object_info` (`registry.py:74-75`).

**Reusability:** addressing, storage, provenance, status derivation, error surfacing — all reusable
as-is for a cohort of role nodes. Each role's output is already a stable address the next role can read.

---

## 5. The concurrency reality: one resident model, 32 roles, request budgeting

This is the heart of the assessment. Two budgetings exist that must NOT be conflated:

### (a) GPU-*load* budgeting — ALREADY EXISTS (`ops/cli/gpu.py`)
The ONE VRAM resource manager decides which models are *resident* on the card: `check_fit`
(`gpu.py:113`), `plan_eviction` (`gpu.py:176`), `budget_vram` (`gpu.py:32`), `read_gpu` (`gpu.py:68`).
`company up` refuses a start that would blow the card and shows what's holding it (`gpu.py` docstring,
POLICY 2026-06-06). **"One resident model" leans on this — it is built and proven.** Once a model is
loaded, its VRAM is fixed; the resource manager is not in the per-request path.

### (b) Concurrent-*request* bounding to that one endpoint — the NET-NEW
- `fabric/vram.py` has a `VramGate` (a `threading.Semaphore`, `vram.py:13-24`) **intended** for this,
  but it is **NOT wired in**: nothing in `scheduler.py` or `fabric/client.py` acquires `.slot()` around
  `mod.run`. Its own docstring calls it "an unmet runtime guarantee before model-nodes land"
  (`vram.py:1-6`), and its default `limit=1` would serialize anyway (`vram.py:14`).
- Because the runtime is single-resident-model, the right primitive for concurrent cognition is a
  **request-concurrency semaphore sized to the inference server's batch capacity** (a resident vLLM with
  continuous batching has up-to-32 as a sweet spot), NOT a VRAM-fit calc per call (VRAM is fixed once
  loaded). `VramGate` is the right *kind* of object; it needs (i) wiring into the dispatch path and
  (ii) a limit sized to the endpoint rather than 1.

### (c) The parallel-dispatch seam — the real build
- The seam is the scheduler's dispatch loop (`scheduler.py:60-153`): fire **all currently-ready
  nodes in a pass concurrently** instead of one-at-a-time. The transport is blocking `urllib`
  (`transport.py:47`), and the bridge is already a `ThreadingHTTPServer` (per STATE.md / `suite.py:188`
  comment), so **threads are the idiomatic fit here** (a thread pool over the ready set), not async.
- **Store-write safety under concurrent dispatch:** the store already serializes the hot writes the
  T1-RACE work added — a per-graph mutation lock + atomic `set_ref`/`save_*` with `fsync` (STATE.md
  "Concurrency (T1-RACE)"; `suite.py:671-672`). A concurrency check (`tests/concurrency_acceptance.py`)
  proves cross-process write safety with REAL subprocesses. **Open verification (cheap to confirm,
  worth a test):** that `put_content`/`memo_set`/`memo_get` are safe under concurrent in-process
  callers — if so, parallel dispatch is cheap and needs no store rewrite.

### (d) The memo / sampling gotcha (a genuine concurrent-cognition concern)
`nodes/llm.py` is **NOT `VOLATILE`**. The memo gate (`scheduler.py:96`) reuses a cached result for an
identical `(type, version, config, inputs)` signature (`_memo_sig`, `scheduler.py:26-34`).
- 32 **distinct-role** prompts → 32 distinct sigs → all run. Fine.
- 32 **same-role same-config** draws (sampling diversity / a jury of identical prompts for variance)
  → collapse to ONE cached result. A "draw N samples from one role" pattern must either vary the
  config/input per draw, set `force`, or use a sampling-aware node — otherwise the cohort silently
  returns one answer N times.

---

## 6. The injection / resolve edge type (C6) — parallel primitive, not the same wire

The task asks whether an "injection/resolve edge type" exists. It does — as a **parallel application of
the same readiness primitive**, in `runtime/context_variables.py` (C6), but it is **RHM-turn-scoped,
not a node-graph edge**:

- C6 is the resolution engine "pointed at context-variables instead of node-inputs"
  (`context_variables.py:1-13`): `runtime: a node runs when its INPUT addresses resolve` ‖
  `RHM: a turn runs when its CONTEXT variables resolve`.
- A `ContextVariable` is `name + cost + resolve(ctx)` (`context_variables.py:49-59`), held in a
  universal `REGISTRY` of variable TYPES (`context_variables.py:62-80`) — register once, every
  turn/provider gains it (Tim's universal-variable-registry principle). `resolve_context(ctx, names)`
  fails loud on an unknown name (`context_variables.py:83-95`).
- Concrete resolvers read the substrate: `Selection`, `RunState`, `Trajectory`, `RecallSlice`, the
  `trial_*` set (`context_variables.py:103-265`). The RHM assembles its per-turn context via
  `_chat_context` → `_resolve_context_at` (`suite.py:1322`, `suite.py:1461`, `suite.py:1943`).

**What this gives vs what's net-new:** the *resolve primitive* (a named thing that reads the substrate
and injects content, budgeted by cost, fail-loud) **exists and is reusable**. What is **net-new** is
making it an **edge in the node graph** — a "resolve/injection edge" where role-B's `context` input
isn't a static wire to role-A's output, but a *resolve* that dynamically selects which upstream role
outputs (by address) to inject into B's context at fire time (e.g. "inject the top-k most relevant
sibling-role outputs"). Today, injection-into-context is C6 (RHM-turn) and chaining-into-input is a
static edge (compile); the concurrent-cognition layer wants C6's *dynamic resolve* available as a
*graph edge*. The pieces (registry, resolve protocol, address reads, cost budget) are all present to
build it on; it is not a wire that exists yet.

---

## 7. The view (canvas) — render = node/edge/registry, generic (view = canvas)

The canvas renders **generically from the registry**, so a new role node-type appears with zero
per-type frontend code:

- One generic `NodeShape` (`canvas/app/src/NodeShape.tsx:30-184`). Ports/nubs come from the registry:
  `getOINFO()[p.nodeType]?.ports` (`NodeShape.tsx:53-55`, `175-176`). Status is driven **by sight** from
  the served `capabilities().node_states` registry (color token + dot/ring shape), not a hardcoded
  ternary (`NodeShape.tsx:56-87`) — so a new status (e.g. a "running" role) paints from a registered
  render token (rule 3).
- Edges are a reactive screen-space overlay anchored on the exact source/target port
  (`NodeShape.tsx:243-278`, `Edges`), port-y from `portTop` mirroring the shape.
- `loadGraph`/`refresh` (`NodeShape.tsx:194-238`) update-or-create-or-prune shapes from the backend
  graph; backend `n.position` is the single source of layout truth.
- The registry feeds the canvas via `/api/object_info` (`bridge.py:153-154` → `SUITE.object_info()`),
  and the element-level UI registry via `/api/ui_info` (`bridge.py:199-200`). `App.tsx` mounts the
  `NodeShapeUtil` + `Edges` (`App.tsx:26-27`, `127`, `242`).

**Reusability:** a cohort of role nodes + their chains renders as-is. The one missing render concept for
concurrent cognition is a **live "running" / in-flight status** for a node mid-call — there is a
registered `node_states` set and a `failed` state, but no `running` state surfaced during a node's run
(the scheduler is serial + synchronous today, so "running" was never needed). Parallel dispatch makes a
`running` state meaningful; adding it is a registry entry + a render token (`NodeShape.tsx:56-87`
already keys off the registry), not bespoke code.

---

## 8. Reuse-vs-net-new table

| Concurrent-cognition need | Substrate today (file:line) | Reusable as-is? | Net-new work |
|---|---|---|---|
| **Role = node** (config + ports + model-call compute) | `nodes/llm.py:10-39`, `nodes/ask.py`; registry discovers from file `registry.py:35-46` | ✅ wholesale | A role is `llm`/`ask` + a role `system` prompt + a `model` slot. None. |
| **Model = registry-sourced slot** | `llm.py:16` `"options_from":"chat_models"`; author-from-registry law (AGENTS.md rule 8) | ✅ wholesale | None. |
| **Chain = edges; output→address→next input** | per-port addresses `compile.py:76-82`; edge→address ref `compile.py:104-111`; fan-in `join.py`/`pair.py` | ✅ wholesale (basic chaining) | None for static chaining. |
| **Ready-node dispatch (readiness primitive)** | `scheduler.py:59-77` (every declared input wired+resolved) | ✅ right shape | None — the shape is correct. |
| **Concurrent execution of the ready set** | `scheduler.py:60-153` — **strictly serial** `for`-loop, one `mod.run` to completion at a time | ❌ **THE net-new** | Fire all currently-ready nodes in a pass **in parallel** (thread pool — transport is blocking `urllib`, bridge is already threaded). Verify `put_content`/`memo_*` concurrent-safe (store hot-writes already locked, T1-RACE). |
| **One resident model (GPU-load budget)** | `ops/cli/gpu.py:32,68,113,176` — refuse/evict/fit | ✅ built + proven | None for residency. |
| **Bounding concurrent requests to that one endpoint** | `fabric/vram.py:13-24` `VramGate` exists but **unwired**, `limit=1` | ⚠️ primitive exists, not wired | Wire a request-semaphore into the dispatch path, size it to the server's batch capacity (not a per-call VRAM calc). |
| **Selective emit / branching among roles** | `scheduler.py:128-150`; `gate.py:38-40` (single-key emit) | ✅ wholesale | None. |
| **Per-role error isolation** | `scheduler.py:102-116` (contained `failed` map); surfaced `suite.py:771-780` | ✅ wholesale | None — one role crashing won't abort the cohort. |
| **Output→address→next-node CONTEXT (static)** | edges `compile.py:104-111` | ✅ wholesale | None. |
| **Injection / resolve EDGE (dynamic context selection)** | C6 resolve primitive `context_variables.py:49-95` — but RHM-turn-scoped, not a graph edge | ⚠️ primitive exists, wrong scope | Make C6's dynamic `resolve` available as a **graph edge type** (role-B's context = a resolve over selected upstream addresses), not a static wire. |
| **Same-role multi-draw (sampling diversity)** | memo gate `scheduler.py:96`; `llm.py` is NOT `VOLATILE` | ⚠️ gotcha | Identical config+input collapse to one cached result. Vary per-draw, `force`, or a sampling-aware node. |
| **View = canvas (generic render)** | `NodeShape.tsx:30-184` (ports/status from registry); `Edges` 243-278; `/api/object_info` `bridge.py:153-154` | ✅ wholesale | A `running` node-state (registry entry + render token) for in-flight roles — meaningful only once dispatch is parallel. |
| **Resume / branch / re-run** | store-derived readiness (`scheduler.py` 4-16); `pause`/`force`/`@branch` | ✅ wholesale | None. |

---

## 9. Assessment summary (the concrete verdict)

**Reusable near-wholesale (the substrate IS the layer):** node = role, edge = chain, per-port
content-addressed outputs + provenance, selective-emit branching (`gate`), fan-in (`join`/`pair`),
per-node error isolation, store-derived resume, generic registry-driven canvas render, and the
GPU-*load* resource manager that makes "one resident model" real. A cohort of role nodes wired into
chains, authored from the model registry, **runs and renders today** — serially.

**Net-new, in priority order:**
1. **Parallel dispatch** — the one real build. Turn the scheduler's serial ready-set loop
   (`scheduler.py:60-153`) into a concurrent fan-out (thread pool; transport is blocking `urllib`, the
   bridge is already threaded). This is what makes "32 concurrent roles against one resident model"
   true. Cheap if `put_content`/`memo_*` are confirmed concurrent-safe (store hot-writes already locked).
2. **Request-concurrency budget** — wire `fabric/vram.py:VramGate` (or its equivalent) into the dispatch
   path with a limit sized to the inference server's batch capacity. (Distinct from the existing
   GPU-load budget.)
3. **Injection/resolve edge type** — promote C6's dynamic `resolve` (`context_variables.py`) from an
   RHM-turn primitive to a node-graph edge so a role's context can be a *dynamic selection* over
   sibling-role output addresses, not only a static wire.
4. **Memo/sampling consideration** — handle same-role multi-draw so identical prompts don't collapse to
   one cached answer (`scheduler.py:96`; `llm.py` not `VOLATILE`).
5. **`running` node-state** — a registered state + render token for in-flight roles (only meaningful
   once dispatch is parallel).

**The thesis stands with one correction:** role=node, chain=edges, view=canvas hold near-wholesale; but
"the concurrent executor IS the scheduler" is the leg that needs work — the scheduler is the right
readiness *shape* but serial. The substrate is overwhelmingly reusable; the executor is the build.

---

## Provenance

All claims are **Observed** (read directly from the files cited) unless marked otherwise. Two claims are
**Inferred** and flagged inline: (a) that `put_content`/`memo_*` are concurrent-safe is *not yet
verified* — recommended as a check before parallel dispatch; (b) that threads (not async) are the
idiomatic fit is inferred from the blocking `urllib` transport (`transport.py:47`) + the already-threaded
bridge. The serial nature of the scheduler is **Observed** (no concurrency primitives in `scheduler.py`;
single `for`-loop dispatch). No code was executed for this research.
