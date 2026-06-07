# B2 — The Node Mechanism Build-Out (dual-use substrate: app surface + concurrent cognition)

*Read-only research, 2026-06-07, worktree `~/company-cognition`. All file:line is **Observed** unless marked Inferred.*

**Premise (Tim):** the composition node-graph was the first AI attempt, so it needs to be **built significantly** into a properly **registry-driven** substrate — and the **same node mechanism** serves BOTH the operable composition surface (the app) AND the concurrent-cognition layer (roles=nodes, chains=edges). The mechanism is **dual-use**, and that dual-use is the design constraint, not a footnote.

**What this doc is (and is NOT).** The *current-state reuse map* — role=node, chain=edges, serial scheduler, the reuse-vs-net-new table — is already delivered with file:line in [`00-LANDSCAPE.md`](../00-LANDSCAPE.md) and especially [`02-graph-substrate-reuse.md`](../02-graph-substrate-reuse.md). **This doc does not re-derive that.** It does three things 02 does not: (A) maps the mechanism specifically through the lens of *"what stops it being fully registry-driven,"* (B) designs the **build-out** the dual-use substrate needs, prioritized, and (C) makes the **shared-vs-divergent seam analysis** the centerpiece. Where 02 has the evidence, this references it rather than repeating it.

---

## Part A — The current node mechanism, mapped honestly (the registry-driven lens)

A compressed map (full file:line in 02 §1–§7). The point here is to surface, at each layer, **what is declared-as-data (registry-driven) vs hardcoded**, because "fully registry-driven" is the build premise.

| Layer | Where | Registry-driven today? | The gap |
|---|---|---|---|
| **node-type declaration** | a `nodes/*.py` module: `VERSION · KIND · PORTS_IN · PORTS_OUT · CONFIG · run()` (`nodes/llm.py:9-39`) | ✅ **Yes** — file-per-type, module-level constants. The strongest part. | — |
| **registration** | `NodeRegistry.discover()` walks the dir, `register_module` reads attrs (`registry.py:35-64`); live re-discover into the running system (`suite.py:4531-4540`, `rediscover`) | ✅ **Yes** — drop a file, it self-registers; a removed file un-registers via `rediscover`. | `register_module` **does not read `OUTPUT_SCHEMA` or `VOLATILE` or `RESOLVE`** into the `NodeType` descriptor — `output_schema` is hardcoded `{}` at `registry.py:57-64`. Capabilities are read ad-hoc off the module at run-time (`getattr(mod, "VOLATILE", …)`, `scheduler.py:94`), not declared in the type-graph. |
| **config / ports** | `CONFIG` dict → `config_schema` verbatim (`registry.py:62`); `PORTS_IN/OUT` → `Ports{name: type-string}` (`registry.py:60-61`); enum options sourced from the live registry via `"options_from": "chat_models"` (`llm.py:16`) | ◑ **Partly** — config + port *names* are data; **port TYPES are free strings** (`"Text"`, `"Any"`) with no type registry. | `connect`'s type-check is a string-equality with an `"Any"` bypass (`suite.py:712-716`) — there is **no port-type registry**, no subtype/coercion graph. `CONTENT_KINDS` is a **hardcoded tuple** (`registry.py:15`) that decides `kind` when a module omits `KIND`. |
| **edge model** | `Edge{from_node, from_port, to_node, to_port}` (`node_record.py:35-40`) | ❌ **No edge types at all.** | An edge is a bare wire. **There is no `kind` on an edge.** Branching is a *node* (`gate`), fan-in is a *node* (`join`/`pair`). See Part C. |
| **compile** | `compile()` (`compile.py:47-113`) — workflow→exec, per-port addresses, edge→address-ref | ✅ **Generic** — gains nothing per node-type (`compile.py:8-10`). Single-out → `{"out": run://g/n}`; multi-out → `{port: …#port}`. | — (the generic-over-type property is exactly right; keep it). |
| **scheduler** | `run()` (`scheduler.py:37-184`) — readiness over the store, memo gate, per-port selective-emit, per-node error isolation | ◑ **Right shape, serial** — single `for nid,ex in by_id.items()` loop (`scheduler.py:60`); each `mod.run` runs to completion before the next (`scheduler.py:103`). Zero async/threadpool. | **THE net-new** (02 §3, §9). Plus: `RESOLVE`/`VOLATILE` are read by `getattr` off the module (`scheduler.py:67,94`), not from the type descriptor. |
| **run / address** | `Suite.run` (`suite.py:774-797`) `guard("run")`-wrapped, emits run event with `ran/cached/stuck/failed` | ✅ | Run is **graph-scoped + governed** — fine for the app; the cognition layer needs an *internal, off-MCP, intra-turn* sibling (Part D). |
| **results addressed/stored** | `set_ref(logical, cas)` atomic+fsync+version-history (`fs_store.py:215-243`); `put_content` write-once (`fs_store.py:184-198`); provenance on every write (`scheduler.py:148-150`) | ✅ **Strong** — content-addressed, per-port, provenance, version trail. | `memo_set` is a **naked non-atomic `write_text`** (`fs_store.py:309-310`) — see concurrency note in Part B. |
| **state derivation** | `Suite.state` (`suite.py:798-879`) reads status from the store: `idle/ran/cached/stuck/failed/live/empty`, survives reload | ✅ | **No `running`/in-flight state** — never needed because dispatch is synchronous. The cognition layer needs it (Part B.5). |
| **NODE_STATES registry** | `Suite.NODE_STATES` tuple (`suite.py:146-179`) — id·label·means·`applies_to`·`derived_when`·`render` token; exposed via `capabilities().node_states` (`suite.py:489`) | ✅ **Exemplary** — the FE paints status by sight from this registry, not a hardcoded ternary (02 §7). This is the *pattern* the rest of the system should follow. | — (use this as the template for the role/edge registries). |
| **rendering** | generic `NodeShape` reads ports/status from `/object_info` + `node_states` (02 §7); SSE `/api/stream` dispatch-by-kind (`decision.*` is the extension-point precedent) | ✅ **Generic** — a new node-type renders with zero per-type FE code. | No `cognition.*` SSE branch; no live "running" paint (depends on Part B.5). |
| **the "role" concept** | `ROLE_REGISTRY` (`suite.py:943-972`) + `resolve_role` (`suite.py:3186-3210`) | ❌ **Hardcoded dict, ONE role (judge), inside suite.py.** | **The single biggest registry-driven gap for cognition.** It is NOT file-discovered like node-types; it does not declare ports/prompt-template/output-schema/trigger as a uniform shape. See Part C, the master fork. |

**The honest one-line state:** the *node-type* half is genuinely registry-driven and excellent (file-per-type, self-registering, generic compile/render, a model registry feeding config enums). The *non-registry-driven* surfaces are: **(1)** edges have no type system, **(2)** ports have no type registry (string-equality + `Any` bypass), **(3)** `output_schema` is declared-but-unenforced and not even read into the descriptor, **(4)** the *role* concept is a one-entry hardcoded dict, and **(5)** the executor is serial. The first-attempt roughness is concentrated exactly where the cognition layer needs the most: roles, edges, concurrency.

---

## Part B — The build-out (prioritized)

Ordered by *what unblocks the most*, with each item marked **[SHARED]** (both uses benefit), **[COGNITION]** (cognition-led, app benefits later), or **[APP]** (surface hardening). Contract-touching items are flagged **CONFIRM** (rule 7 — they widen the system).

### B1. Parallel dispatch — wave-synchronous *(SHARED, top priority)*
**Evidence:** `scheduler.py:60` is a strictly serial `for`-loop; 32 ready role-nodes run one-after-another (02 §3). The bridge is already a `ThreadingHTTPServer` and the transport is blocking `urllib` (02 §5c), so **threads, not async**, are the idiomatic fit.

**Design — wave-synchronous (a refinement over 02's "fire ready nodes concurrently"):**
1. Compute the ready set for this pass (the existing readiness predicate, `scheduler.py:72-77`).
2. `ThreadPoolExecutor` the wave — each worker runs ONE `mod.run(inputs, config)` and returns `(nid, result | exception)`. **Workers do not touch the `ran/skipped/failed` sets or the store-ref-writes.**
3. Join the wave.
4. **Apply results serially on the main thread** — `put_content` → `memo_set` → per-port `set_ref` → provenance → mutate `ran/skipped/failed`. This keeps set-mutation single-threaded and confines store-write concurrency to the parallel read-only `run()` calls.
5. Recompute ready set; repeat until `processed == execs` and no progress.

**Why wave-synchronous beats free-for-all:** it reuses the existing `while progress` loop almost verbatim, makes the `ran/skipped/failed/stuck/pruned` bookkeeping (`scheduler.py:50-184`) correct-by-construction (single-threaded), and isolates the only genuinely-concurrent surface to the `run()` calls themselves — which for `llm` are pure HTTP. The per-node error-isolation already in place (`scheduler.py:102-116`) carries through: a worker exception becomes `failed[nid]` on apply.

**Store-safety — *intra-run* vs *cross-run* (this resolves the open verification 02 §5c flagged):**

*Intra-run:* wave-synchronous **serializes all store writes by design (step 4, a feature).** Within one run, `put_content`/`memo_set`/`set_ref` are never concurrent — only the read-only `run()` calls parallelize. This is precisely *why* wave-sync is the right executor: it confines concurrency to pure HTTP and keeps every store mutation single-threaded. So no intra-run store hardening is needed.

*Cross-run (the real concurrency, because all runs share ONE store + ONE resident model):* the cognition swarm running while the operator runs a graph, or two graphs overlapping on the threaded bridge, DO write the store concurrently. There:
- `put_content` is **write-once + content-addressed** (`fs_store.py:184-198`) — concurrent callers writing the *same* cas race on `p.write_bytes`, but the bytes are identical and the path is the hash, so the result is correct. **TOCTOU note:** the `if not p.exists()` (`fs_store.py:196`) is not atomic, but safe *only because content is deterministic* — two writers of the same hash write the same bytes. Mark this assumption explicitly; it breaks the instant a non-deterministic cas is introduced.
- `memo_set` is a **naked `write_text`** (`fs_store.py:309-310`) — NOT atomic, unlike `set_ref` (`fs_store.py:215-227`). **Right-sized:** because the cached value is a deterministic cas string, a torn *cross-run* read causes at worst a *redundant re-run*, never corruption — and it is **moot for the swarm** because the swarm marks `llm` VOLATILE (B7, memo bypassed entirely). **Fix is cheap:** mirror `set_ref`'s tmp+`os.replace`+fsync. Low priority, not load-bearing.
- `set_ref` is already atomic+fsync+unique-tmp-per-write (`fs_store.py:215-227`) — safe across runs. ✅
- The graph mutation lock (`store.graph_lock`, `fs_store.py:144-164`) wraps load→mutate→save on both faces (`suite.py:688` etc.) — orthogonal to the run path; unaffected.

**Conclusion:** parallel dispatch needs the executor change + a request semaphore (B2); the store is essentially ready for intra-run parallelism (wave-sync serializes its writes), and cross-run safety needs only one cheap atomicity fix. This is the make-or-break each research agent named.

### B2. Request-concurrency budget *(SHARED, top priority — pairs with B1)*
**Evidence:** `fabric/vram.py:VramGate` is a `threading.Semaphore` *intended* for this but **unwired** with `limit=1` (02 §5b). GPU-*load* budgeting already exists and is separate (`ops/cli/gpu.py` — refuse/evict/fit; once a model is resident its VRAM is fixed, not per-request).

**Design:** a global `Semaphore(N)` sized to the resident inference server's batch capacity (vLLM continuous-batching knee ≈ 32), acquired around each `run()` in the wave. **Reserve R slots** for the main stream + judge so the swarm (cap `N−R`) never starves them — a config slot (the landscape's open fork: R=4, swarm≤28). This is **distinct from VRAM-fit** (VRAM is fixed once loaded; this bounds in-flight requests). Wire it into the dispatch path (B1 step 2), not into `fabric/client.py` (keep the transport dumb). **Cross-run note:** the semaphore and the resident model are shared by the operator's `Suite.run` AND the cognition turn, so an operator graph-run also draws from `N` — the `N−R` reserve must account for a concurrent operator run consuming slots, not only main-stream + judge + swarm; the budget is a *global* bound on the shared endpoint, not a per-driver one.

### B3. The general Role Registry — *the master registry-driven gap (COGNITION, CONFIRM)*
**Evidence:** `ROLE_REGISTRY` (`suite.py:943-972`) is a hardcoded dict with **one** role (judge), living in `suite.py`, NOT file-discovered. Its own comment names this generalization as the intended path. `resolve_role` (`suite.py:3186-3210`) already resolves model+base_url+knobs+thinking+output+tools+context with config-binding > env > default precedence — **good machinery, no registry behind it.**

**THE master fork (surface to Tim, options not binary):** *what IS a role?*
- **Option A — role = node-type (file-per-role, the `nodes/` pattern).** A role is a `nodes/roles/<name>.py` declaring `PROMPT_TEMPLATE · INPUT_ADDRESSES · OUTPUT_SCHEMA · TRIGGER · MODEL_BINDING · MODE_DEPENDENCE · RENDER_HINT` + a generic `run_role`. **Pro:** maximal reuse of discovery/registry/render; a role IS a node so chains/canvas/provenance come free; the dual-use is *literal* (the same registry holds both). **Con:** roles carry cognition-specific fields a plain node doesn't; risks bloating the node contract.
- **Option B — role = a data registry (file-discovered dict rows, like `NODE_STATES`/`STT_PROVIDERS`).** Roles are declarative rows the `resolve_role` machinery already reads, moved out of `suite.py` into a discovered source. **Pro:** keeps the node contract clean; roles can declare cognition-only fields freely. **Con:** a second registry to render/maintain; the "role=node" literalness is looser.
- **Option C — role = an `llm`/`ask` node *instance* + a thin role descriptor.** The compute is the existing `llm` node; the role registry only adds prompt-template + output-schema + trigger + binding on top. **Pro:** smallest net-new; rides `llm.py` verbatim. **Con:** the role's identity is split across two places.

**Recommendation (tentative):** **Option A or C**, leaning C for the proving spike → A as the layer matures — because the landscape's stated path is "generalise the judge into a 2-role registry feeding ONE injected second part" (00 §6), which is cheapest as C. But this **touches the node/role contract**, so it is **CONFIRM-level** — present these three as the fork, don't pick silently. Pair this decision with the executor fork (B8): together they determine *how much is actually shared*.

Whichever option: the role registry must be **declared data**, not a hardcoded dict in `suite.py`, and `resolve_role`'s existing precedence logic is the reusable core.

### B4. `run_role(role_id, ctx)` + `_run_swarm(roles, budget)` *(COGNITION)*
A sibling of the judge's call path (`is_finished_thought` already calls `resolve_role("judge")`), generalized: `run_role` resolves the role, builds messages from its prompt-template + resolved input addresses, calls guarded `fabric.client.complete` with the role's knobs + (B6) `json_schema`, writes the structured result to the role's output address. `_run_swarm` fires N roles through the B1 executor under the B2 budget. **OFF the MCP face** (internal cognition, not an operator verb — Part D divergence).

### B5. The `running` / in-flight node-state *(SHARED, but COGNITION-led)*
**Evidence:** `NODE_STATES` (`suite.py:146-179`) has no `running` — dispatch was synchronous, so it was never needed (02 §7). `node_record.py:10` *Status* literal already lists `"running"` but nothing emits it.

**Design:** add one row to `NODE_STATES` (`running`, `applies_to=("compute",)`, render token + pulse) — the FE already paints by sight from the registry (02 §7), so this is **a registry entry + a render token, not bespoke code.** Emit it when the B1 wave dispatches a node and clear it on apply. Cognition needs it most (live swarm); the app benefits (long-running LLM/codebase nodes show progress instead of looking frozen).

### B6. `json_schema` in the transport *(SHARED)*
**Evidence:** transport does `json_object` today (`02 §5`, `transport.py:37`). The resident 4B does strict schemas reliably (benchmark §5). One branch; retry already exists in `client.complete` (`fabric/client.py`). Roles need structured JSON outputs that resolve cleanly into the next part's context. **The app benefits too** — any structured-output node (extract/classify/judge) gets schema-enforced returns.

### B7. Mark `llm` (and role nodes) VOLATILE for distinct draws *(COGNITION)*
**Evidence:** `llm` is NOT VOLATILE (`02 §5d`), so 32 same-role same-config draws collapse to ONE memo-cached result (`scheduler.py:96`). A swarm doing sampling diversity needs distinct draws. **Design:** the role-node sets `VOLATILE=True` (the documented escape, `nodes/AGENTS.md:15`), OR vary per-draw input/seed, OR a sampling-aware node. **Divergence flag:** the *app* wants `llm` memoised (don't re-hit the model on an unchanged graph); the *cognition* swarm wants it volatile. So this is **per-use, not a global flip** — the role node is volatile; the app's plain `llm` node stays memoised (Part D).

### B8. The injection / resolve edge type — *the genuine net-new edge (COGNITION, CONFIRM)*
**Evidence:** the C6 resolve primitive exists (`context_variables.py:49-95` — `name + cost + resolve(ctx)`, universal registry, fail-loud, budgeted) but is **RHM-turn-scoped, not a graph edge** (02 §6). A `ContextVariable` reads the substrate and injects content; what's net-new is making that a **graph edge** where role-B's `context` input is a *dynamic resolve* over selected upstream role addresses (e.g. "inject the top-k most relevant sibling outputs"), not a static wire. See Part C for the edge-contract decision this forces.

### B9. The staged-response queue *(COGNITION)*
`THOUGHT_SHAPES` registry + a part schema + an intra-turn runner speaking the same "fires-when-deps-resolve" language + `chat_parts()` + `shape_for(mode)` (focus/background → never stage). Each completed PART is the TTS streaming unit (05 voice-coupling). This is the cognition-specific layer ON the shared substrate — covered in depth by 04; noted here as the consumer of B1–B8.

### B10. App-surface hardening (the first-attempt-rough bits) *(APP)*
Where the app surface is thin and needs hardening **independent of cognition**:
- **Port-type registry** *(CONFIRM)* — port types are free strings with an `Any` bypass (`suite.py:712-716`); `connect`'s type-check is string-equality. A real surface wants a **declared port-type registry** with subtype/coercion rules so the canvas can prevent + explain invalid wires, and the palette can suggest compatible targets. Today `produces`/`consumes` (`registry.py:67-71`) do exact-string matching only.
- **`output_schema` enforcement** — it is **declared-but-decorative**: `register_module` never reads a module's `OUTPUT_SCHEMA` (always `{}`, `registry.py:57-64`), and the scheduler never validates a node's return against it. It only flows to the FE via `object_info` (`object_info.py:39,53`). Either **enforce it** (validate `run()`'s return, fail loud — rule 4) or **remove the dead field**. A declared-but-unused contract field is exactly the rot rule-9 warns about.
- **`CONTENT_KINDS` hardcoded** (`registry.py:15`) — kind-inference falls back to a hardcoded tuple. A node should declare its `KIND` (most do); the fallback list is a latent drift source. Low priority.
- **`memo_set` atomicity** (B1) — the one store fix; mirror `set_ref`.
- **Live `running` paint** (B5) — long app nodes look frozen today.

---

## Part C — Edge types: confront that there are *none* today

**The honest finding:** the `Edge` contract (`node_record.py:35-40`) is `from_node · from_port · to_node · to_port` — **no `kind` field, no resolve field.** Today's "edge types" are not edge types at all; they are **node concerns**:

| The task's "edge type" | Where it actually lives today | Net-new? |
|---|---|---|
| **data wire** | the plain `Edge` → address-ref in compile (`compile.py:104-111`) | ✅ exists, wholesale |
| **gate / branch** | the `gate` **node** (selective single-key emit; untaken port never written → pruned) (`gate.py:26-40`, `scheduler.py:128-150`) | ✅ exists as a node, not an edge |
| **fan-in** | the `join` / `pair` **nodes** (`join.py:16-18`, `pair.py`) | ✅ exists as a node, not an edge |
| **injection / resolve edge** | the C6 resolve primitive, but RHM-turn-scoped (`context_variables.py:49-95`) — NOT a graph edge | ❌ **the one genuinely net-new edge** |

**The design fork (CONFIRM — it touches the C3 contract):**
- **Option A — keep edges plain; keep semantics in nodes.** Branching/fan-in stay nodes; the injection/resolve "edge" becomes a *node* too (a `resolve` node whose config is a selection query over sibling addresses, emitting the chosen context). **Pro:** zero contract change (schema-stable, rule 2 happy); the scheduler stays a pure resolver; consistent with how gate/join already work. **Con:** dynamic injection as a node is slightly indirect vs a first-class edge; the canvas shows a node where the mental model is "a smart wire."
- **Option B — add an optional `kind` (and `resolve`) field to `Edge`.** `Edge.kind: Literal["wire","resolve"] = "wire"` + an optional resolve spec, schema-additive (rule 2 — bump `schema_ver`, existing graphs keep working). Compile gains a branch: a `resolve` edge compiles to a *dynamic* input address (resolved at fire-time over a `swarm://`/`run://` address set) instead of a static one. **Pro:** injection is first-class; "a smart wire" matches the mental model; the canvas can render resolve-edges distinctly. **Con:** the scheduler's readiness predicate (`scheduler.py:72-77`) must learn dynamic inputs (an input whose address set isn't known until fire-time) — a real change to the readiness invariant, the riskiest part.

**Recommendation (tentative):** **Option A for the proving spike** (a `resolve`/`inject` node — no contract change, ships fastest, proves the end-to-end mechanism per 00 §6's spike plan), **revisit Option B** once the dynamic-selection pattern is proven and the readiness-invariant change is understood. Present both; the contract-touching one is CONFIRM-level.

Either way, the **C6 resolve machinery is the reusable core** (`context_variables.py` — registry, cost budget, fail-loud); what's net-new is its *scope* (graph/part-context vs RHM-turn), not its mechanism.

---

## Part D — Shared-vs-divergent seam analysis (the centerpiece)

The premise is dual-use. The value is in being **precise about where the app and cognition SHARE the substrate vs DIVERGE** — sharing the wrong thing couples them; diverging on the wrong thing duplicates. Mapped axis by axis, with the file:line that pins each.

### What they SHARE (one substrate, no fork)
| Shared mechanism | The single implementation | Why it's safe to share |
|---|---|---|
| **node-type declaration + discovery** | `nodes/*.py` + `NodeRegistry` (`registry.py:35-64`) | a role is a node-type; both author from the same file-per-type pattern. |
| **compile (workflow→exec, per-port addresses)** | `compile.py:47-113` | generic over type by design (`compile.py:8-10`) — gains nothing per use. |
| **the readiness primitive** | `scheduler.py:72-77` | "fires-when-inputs-resolve" is identical intra-turn and on-canvas (00 §1). |
| **content-addressed store + provenance + version trail** | `fs_store.py:184-243` | both want addressed, provenanced, replayable outputs. |
| **parallel dispatch + request budget (B1/B2)** | the new wave executor + semaphore | the app benefits from parallelism on big graphs; cognition requires it. **Build once, both use.** |
| **per-node error isolation** | `scheduler.py:102-116` | one role/node crashing must not abort the cohort/graph — same need. |
| **generic registry-driven render** | `NodeShape` + `node_states` + `object_info` (02 §7) | a new role node-type and a new app node-type both render with zero per-type FE. |
| **the model registry feeding config enums** | `"options_from":"chat_models"` (`llm.py:16`); author-from-registry law (AGENTS rule 8) | both pick models from the live registry, never hardcoded. |
| **the resolve machinery (C6 core)** | `context_variables.py:49-95` | the injection primitive is the same; only its scope diverges (below). |

### Where they DIVERGE (must NOT share — the seam lines)
| Axis | **App surface** | **Concurrent cognition** | The seam (how they split cleanly) |
|---|---|---|---|
| **Persistence** | durable operator graphs in the store, survive reload, version-tracked (`save_graph`, `fs_store.py`) | **ephemeral per-turn** — a swarm's role outputs live for one turn (the `swarm://<turn>/<role>` namespace, 00 §1) | a **namespace + GC policy** decision (00 §5 open fork: persist for introspective-data vs reap per turn). Share the store; diverge on retention. |
| **Trigger** | operator action (`Suite.run`, guard-wrapped, `suite.py:774`) | **intra-turn, automatic** — a part fires when its inputs resolve, no operator (00 §1) | the cognition layer gets an **internal `_run_swarm`/intra-turn runner**, NOT `Suite.run`. Same readiness shape, different entry. |
| **Governance** | `guard("run")`-wrapped, AUTO/SURFACE/CONFIRM posture (`suite.py:782`); dispatch off the agent face | **OFF the MCP face** — internal cognition is not an operator verb (00 §3, B4) | `_run_swarm` is a Suite-internal method, never a registered verb. The RHM *reads its own* cognition via addressed data, never *invokes* the swarm as a tool. |
| **Addressing namespace** | `run://<graph>/<node>` (`compile.py:22-28`) | `swarm://<turn>/<role>` **or** reuse `run://<turn>/<role>` (00 §5 open fork) | reuse `run://` = no new contract (default); mint `cog://`/`swarm://` = CONFIRM-level contract-widening (rule 8, mirrors the `ui://`/`code://` precedent at `address.py:32`). Recommend reuse for the spike. |
| **Memo default** | `llm` **memoised** — don't re-hit the model on an unchanged graph (`scheduler.py:96`) | role nodes **VOLATILE** — distinct draws for sampling diversity (B7) | **per-node-instance, not global.** The app's plain `llm` stays memoised; the role node sets `VOLATILE=True`. The scheduler already reads VOLATILE per-node (`scheduler.py:94`) — the divergence is *data*, not a code fork. |
| **`running` state** | nice-to-have (long nodes look frozen) | **essential** — the live swarm frame is the whole point (06 rendering) | one shared `NODE_STATES` row (B5); cognition lights it via `cognition.*` SSE, the app via the existing run path. |
| **Render surface** | the operator canvas (tldraw), reflects-never-owns | a **per-turn cognition frame** — own surface vs canvas overlay (00 §5 open fork); possibly 5 visually-distinct layers | share the generic `NodeShape`/`Edges`/registry-render machinery; diverge on the *surface* (a `CognitionView` + `cognition.*` SSE branch mirroring `decision.*`, 00 §3.10). |
| **Edge dynamism** | static wires (operator draws them) | dynamic resolve-edges/nodes (select context at fire-time, B8/Part C) | share the C6 resolve core; the app uses static edges, cognition adds the dynamic resolve (a node or an edge-kind per Part C). |

### The two top-level forks that decide *how much* is shared
1. **Executor (00 §5 open fork):** reuse `runtime/scheduler.run` verbatim for the swarm vs a lightweight in-turn runner. **Recommendation (tentative):** a **thin in-turn runner that speaks the same readiness language** but is ephemeral, off-MCP, and writes to the turn namespace — because `Suite.run` is graph-scoped + guard-wrapped + emits operator run-events, none of which fit an intra-turn swarm. The *readiness algorithm* is shared (extract it so both call it); the *driver* diverges. This makes B1's wave executor a shared lower layer with two drivers on top.
2. **Role identity (B3):** node-type vs data-registry vs llm-instance+descriptor. This decides whether the role registry literally IS the node registry (maximal share) or a sibling (clean separation).

**The clean architecture this points to:** a **shared lower substrate** (node-type registry · compile · readiness algorithm · wave executor + request budget · content-addressed store · generic render machinery) with **two thin drivers on top** — the app's `Suite.run` (durable, governed, operator-triggered) and cognition's `_run_swarm`/intra-turn runner (ephemeral, off-MCP, auto-triggered) — diverging only on persistence, trigger, governance, namespace, memo-per-node, and render-surface. Sharing the substrate is right; sharing the *driver* would couple operator governance to internal cognition, which is exactly wrong.

---

## Part E — Prioritized build-out list (one place)

1. **B1 Parallel dispatch (wave-synchronous)** — SHARED, top. The one make-or-break.
2. **B2 Request-concurrency semaphore** (`N−R` reserve) — SHARED, pairs with B1.
3. **B3 General Role Registry** (resolve the master fork: node-type / data / instance) — COGNITION, **CONFIRM**.
4. **B4 `run_role` + `_run_swarm`** (off-MCP) — COGNITION.
5. **B6 `json_schema` transport branch** — SHARED.
6. **B5 `running` node-state** (registry row + render token) — SHARED.
7. **B8 / Part C injection-resolve** (node first, edge-kind later) — COGNITION, edge-kind is **CONFIRM**.
8. **B7 VOLATILE role nodes** (per-node, not global) — COGNITION.
9. **B9 Staged-response queue** — COGNITION (consumes 1–8; detail in 04).
10. **B10 App hardening:** port-type registry (**CONFIRM**) · `output_schema` enforce-or-remove · `memo_set` atomicity · `CONTENT_KINDS` declared-not-hardcoded — APP.

**Proving spike (recommended, per 00 §6):** B1 + B2 + B6 + a 2-role registry (B3 Option C) + ONE resolve-into-second-part (B8 as a node) → prove parallel dispatch + json_schema + injection + a 2-part staged reply end-to-end **before** fanning out to the full swarm + rendering. This validates the shared substrate and the seam split on the smallest surface.

---

## Provenance
All file:line claims **Observed** by reading the cited files (`scheduler.py`, `compile.py`, `registry.py`, `suite.py`, `fs_store.py`, `node_type.py`, `node_record.py`, `address.py`, `gate.py`, `join.py`, `llm.py`, the `nodes/` constitution) at the 2026-06-07 worktree state. **Inferred** (flagged inline): threads-not-async is the fit (from blocking `urllib` + threaded bridge); the wave-synchronous store-safety argument (rests on `put_content` determinism + `set_ref` atomicity, both Observed, but not executed under concurrency). The reuse-vs-net-new current-state map is in `02-graph-substrate-reuse.md`; this doc references rather than re-derives it. No code was executed or changed (read-only).
