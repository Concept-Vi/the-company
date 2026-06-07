# Concurrent Cognition — Research Landscape (aggregated)

*Tim's idea, 2026-06-07. Six read-only research agents mapped the codebase; this aggregates their findings (01–06) into one picture: the architecture, what's reusable, what's net-new, the forks to decide with Tim, and the path to a build. The cascade of [[project-collective-cognition]] (looking=address→resolve→inject; budget=attention; the judge = the seed).*

---

## 1. The architecture (the spine)

```
  A TURN's reply is no longer ONE generation. It is a STAGED STREAM of PARTS,
  spoken by the resident 4B, each part fired when its inputs RESOLVE —
  fed, in the shadow of Part 1 being generated and SPOKEN, by a SWARM of ~32
  concurrent ROLE-runs whose structured JSON resolves into the NEXT part's context.

  part = node · role-output = address · part fires when its input addresses resolve
  (the Company's existing reactive scheduler relationship, applied INTRA-turn)
```

- **The swarm = ~32 concurrent REQUESTS to the ONE resident 4B** (not 32 models). vLLM batches server-side; the client fires ~32 threads at `:8000`. Resource cost = one 4B with a KV pool for the main context + 32 *short* role contexts — feasible at concurrency 32 (benchmark §1).
- **Injection = address→resolve→inject** (the judge's own primitive, currently bypassed): a role writes JSON to a `swarm://<turn>/<role>` address; the next part's prompt resolves it through the existing `_chat_context → _resolve_context_at` path (`suite.py:1322,1461,1943`).
- **Chains** = role→role edges (role B's input is a resolve over role A's output).
- **Mode = the one dial** — gates whether to stage at all, picks the thought-shape, selects the role set, AND sets the slot budget (budget = attention, literally).
- **The judge is role #0.** `ROLE_REGISTRY` (`suite.py:929`) already defines a role as "a named model-function of the collective cognition," and its comment names this exact generalisation as the intended growth path. This **completes declared work, additively** — not a parallel system.
- **Voice:** each completed PART is the TTS streaming unit → the voice streams as the brain produces parts (overlap brain↔TTS). This is the answer to "can the voice stream as the brain streams" — the multi-part design *is* the mechanism.
- **Rendering:** roles→nodes, chains→edges, injections→edges into the brain node; per-turn frame lit live by new `cognition.*` SSE events; the canvas (reflects-never-owns) renders it; the RHM reads its *own* cognition via the same addressed data.

## 2. Reuse spine — what's already there (near-wholesale)

| Capability | Exists as | Evidence |
|---|---|---|
| role = node (config + ports + run) | node-types declared from a file; `llm`/`ask` call the model through guarded fabric | `nodes/llm.py`, `ask.py` |
| chain = edges; per-port addressed outputs | edge→address wiring; selective-emit (`gate`), fan-in (`join`) | `compile.py:76-111`, `gate.py`, `join.py` |
| the reactive "fires-when-deps-resolve" relationship | the graph scheduler (readiness shape) | `scheduler.py:60-153` |
| role registry + model binding + knobs | `ROLE_REGISTRY`, `resolve_role`, the deep-merged `roles` config slot | `suite.py:929,3172` |
| injection (address→resolve→inject) | `_chat_context`→`_resolve_context_at`; C6 dynamic `resolve` | `suite.py:1322,1461`, `context_variables.py:49-95` |
| mode = the dial | `MODES`, `MODE_DIRECTIVES`, `_mode_directive` (brevity gradient) | `suite.py:907,1032` |
| structured-output validate/retry | `complete()` validate+retry | `client.py:75-87` |
| event stream → live UI | SSE `/api/stream` → `openStream` dispatch-by-kind; `decision.*` branch = the extension point | `useAppController.ts:355-403` |
| generic canvas render (reflects-never-owns) | `NodeShape` (ports/status from registry), `Edges`, `build_object_info`/`build_ui_info` | `NodeShape.tsx`, `bridge.py:153` |
| one resident model (the foundation) | the VRAM resource-manager | `ops/cli/gpu.py` |

## 3. Net-new — the build (priority-ordered, agents converge)

1. **Parallel dispatch.** The scheduler is **strictly serial** today (`scheduler.py:59-61`, single for-loop; zero async/threadpool in `runtime/`). Add a `ThreadPoolExecutor` firing the *existing* blocking transport from ~32 threads (GIL releases on socket I/O; vLLM batches server-side — no client batching).
2. **Request-concurrency budget.** Global `Semaphore(32)` (the vLLM knee) + a swarm pool capped at `32 − R` reserving R slots for the main stream + judge (never starves). `fabric/vram.py:VramGate` exists **unwired** (`limit=1`).
3. **`json_schema` in the transport.** It does `json_object` today (`transport.py:37`); the 4B does strict schemas reliably (benchmark §5). One branch; retry already exists.
4. **The general Role Registry.** Declarative fields — prompt template · input addresses · output JSON schema · trigger · model binding · mode-dependence · output destination · render hint — + a generic `run_role`. Judge is the seed; most fields have reuse anchors (§2).
5. **`_run_swarm(roles, budget)` helper** — a sibling of the judge call path, OFF the MCP face (internal cognition, not an operator verb).
6. **The staged-response queue.** `THOUGHT_SHAPES` registry + a part schema + an intra-turn runner speaking the same "fires-when-deps-resolve" language + `chat_parts()`; `shape_for(mode)` (focus/background → never stage).
7. **`brevity_judge`** — mirrors the judge; the short-response bypass, mode-biased, with free hard-gates.
8. **Injection edge** — promote C6's dynamic `resolve` from RHM-turn scope to a graph-edge / next-part-context resolution over `swarm://` addresses.
9. **`llm` node marked VOLATILE** — else identical role+config draws collapse to one memo-cached result (`scheduler.py:96`); the swarm needs distinct draws.
10. **Rendering** — cognition registry serializer (`build_object_info` sibling) + a `cognition.*` emit-contract (the render rules' hard dependency) + cognition node-states (`latent/firing/ran/injected/failed/abstained`) + FE `CognitionView`/`RoleShape`/cognition-`Edges` + the `cognition.*` SSE branch (mirrors `decision.*`).

## 4. The distinct pieces (Tim's "a few pieces + registries")

**Role Registry · Swarm Executor (dispatch + slot budget) · Injection (resolve edge) · Staged-Response Queue (shapes + intra-turn runner) · Selector/Brevity Judges · Cognition Rendering.** Six pieces, most riding existing substrate; the make-or-break each agent named is the **VRAM-bounded slot scheduler on the one resident model**.

## 5. Open forks — decide WITH Tim (not silently)

- **Part grain** — sentence / beat / paragraph? Mode-dependent?
- **The first role cast** beyond the judge — which concurrent "thoughts" fire every turn (memory-recall · screen-reader · relevance-scorer · contradiction-checker · tone-shaper · fact-grounder · …). This is the soul of the registry.
- **R (reserved slots) / swarm cap** — proposed R=4, swarm≤28 at a 32 semaphore. Snappier turns (larger R) vs richer per-gap cognition (smaller R)? Measured by use, a config slot.
- **Reuse `runtime/` scheduler verbatim vs a lightweight in-turn runner** — same relationship; cleanest is likely a small in-turn runner that speaks the same language.
- **Tools array across parts** — all parts carry the offered tools, or only the final part (intermediate parts pure generation)?
- **Residency policy** — swarm REQUIRES the 4B resident; if not loaded: fail loud + surface (judge's stance) vs auto-request a load via the manager.
- **`swarm://` namespace GC** — persist (introspective-data-building: the swarm's own run-records) vs reap per turn.
- **Address scheme** — reuse `run://<turn>/<role>` (default, no new contract) vs mint `cog://` (CONFIRM-level, rule-8 contract-widening).
- **Cloud-brain escape hatch** — keep an operator-selectable cloud brain (loses the cognition layer that turn)?
- **Render** — own surface vs canvas overlay; one role-node kind vs visually distinct conscious/auxiliary/faculty/sense layers (the spine's 5 layers).

## 6. Path

This landscape → **loop-prep triad** (Completion Criteria · Implementation Guide · Research Synthesis) → autonomous build loop. **Proving spike first** (recommended): generalise the judge into a 2-role registry feeding ONE injected second part — prove the end-to-end mechanism (parallel dispatch + json_schema + injection + a 2-part staged reply) before fanning out to the full swarm + rendering.

*Detail per thread: 01-role-registry · 02-graph-substrate-reuse · 03-concurrency-and-injection · 04-staged-response-queue · 05-voice-stream-coupling · 06-rendering.*
