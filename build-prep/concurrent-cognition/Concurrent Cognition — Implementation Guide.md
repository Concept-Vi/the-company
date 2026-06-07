# Concurrent Cognition — Implementation Guide

*Document 2 of the triad. HOW to make each Completion-Criteria group true, with the seams the research mapped. All paths are in the worktree `~/company-cognition`. Principle throughout: reuse the node-graph substrate; the cognition layer is a thin driver, not a parallel system.*

> **⚠ Hardened by Round-1 review — `review/R1-FOLD.md` is binding.** Corrections that change the HOW below: injection is a **net-new ref-read** (the existing resolve path reads operator-notebook strata, not fresh role refs) addressed via **`run://`** (never `swarm://`); **`chat_parts` is a hot-path refactor** (extract `chat()`'s body to a shared core), not additive; **parallelism lives in `_run_swarm`/the in-turn runner, NOT the shared `scheduler.py`**; the concurrency budget reads `max_num_seqs`(=16)+KV, never 32; `MODEL_CAPABILITIES` **extends the existing `MODEL_KNOBS`/`knobs_for()`**; the rule evaluator enforces determinism (post-barrier, resolved-values-only). **Locate by symbol** — line refs drifted ~+14; `node_record.py` is in `contracts/`.

---

## Governing principles (why the design is this shape)

1. **Role = node, chain = edge, view = canvas, the judge = role #0.** The node-graph engine already gives ports/config/registry/render; we extend it, never fork it. (`02-graph-substrate-reuse.md`.)
2. **Rule-based routing, not model judgment (L2).** A model only ever runs *inside a role*; a *rule* is declared, deterministic logic that routes a role's structured output. This is why the design is registry-driven and inspectable — and why "can a 4B aggregate 32" isn't central (aggregation is one optional role).
3. **Injection = a NET-NEW ref-read (corrected, R1-FOLD F3).** A role writes JSON to **`run://<turn>/<role>`**; the next part's prompt reads the resolved value there. This is a **new branch in part-context assembly** — the existing `_resolve_context_at`/`_r2_gather` resolves operator-notebook strata (annotations/chats/events), NOT freshly-written role refs, so it does NOT do this for free (and `context_variables.py` is test-only/dead — do not "promote" it). It is still the Company's address→resolve→inject *shape*; just build the role-ref read. No mid-generation injection; parts are sequential fresh requests.
4. **The swarm = concurrent requests to ONE resident model**, vLLM-batched — not N models. The resource question is "one 4B with a KV pool for the main context + 32 short role contexts," not "fit a fleet" (`03`).
5. **One shared substrate + two thin drivers** — app `Suite.run` (governed, persistent) and cognition `_run_swarm` (off-MCP, ephemeral); diverge on persistence/trigger/governance/namespace/render (`B2`).
6. **Mode is the dial** — gates whether to stage, picks the cast + the part-grain, sets the slot budget, and (generalised) selects the activation-context. Budget = attention, literal.

## G0 · Proving spike — DO THIS FIRST

**Sequence:** (1) add a minimal `run_role(role, ctx)` that fires one resident-4B request with a `json_schema` output; (2) declare 2 roles (`focus`, `recall`) as data; (3) a `chat_parts()` that emits Part 1 from base context, fires the auxiliary role concurrently (a thread), resolves its `swarm://` address into Part 2; (4) stream both as ndjson. **Verify by use** end-to-end + run twice for identical routing (C0.2). **Don't** build the full registry/executor yet — the spike proves the mechanism, not the substrate.
- NEW: `runtime/cognition.py` (the swarm helper, spike-minimal) · MODIFY: `runtime/suite.py` (a `chat_parts` path beside `chat`) · REFERENCE: `is_finished_thought` (the judge call pattern), `fabric/client.py:75-87` (validate/retry).
- **Gate:** spike green → proceed to G1. Spike weak (4B can't hold a coherent staged reply) → STOP, surface to Tim, redesign.

## G1 · Node-mechanism substrate (the make-or-break)

**Principle:** the scheduler has the right *readiness shape* but is strictly serial (`scheduler.py:60-153`). The single highest-risk change is parallel dispatch — do it wave-synchronous so store writes stay safe.
- **C1.1 concurrent dispatch in the DRIVER (corrected, R1-FOLD F2)** — put the `ThreadPoolExecutor` in `_run_swarm`/the in-turn part runner, NOT in the shared `runtime/scheduler.py` (modifying the shared scheduler would make every app `Suite.run` concurrent — a behaviour change to the governed app face the "two thin drivers" framing avoids). First **materialize a ready-set** (the scheduler is a re-scanning loop, no ready-set today). Fire the *existing* blocking transport (GIL releases on socket I/O; vLLM batches server-side). Barrier per wave; serialize store writes. DON'T introduce async/httpx; DON'T make the shared executor concurrent.
- **C1.2 slot budget** — wire `fabric/vram.py:VramGate` (exists, `limit=1`, unwired) into the dispatch path as a global `Semaphore(concurrency_knee)` + a swarm sub-pool of `knee − R`. `R` + `knee` are registry values (G8), never hardcoded 32.
- **C1.3 edge types** — MODIFY `node_record.py:35-40` (`Edge`): add a declared `kind`; register edge-kinds in the registry; the injection/resolve edge wraps C6's `context_variables.py:49-95` promoted from RHM-turn scope to a graph-edge. DON'T turn gate/join into edges — keep them as nodes; add the *injection* edge as the net-new kind.
- **C1.4 output_schema** — MODIFY `registry.py:57-64` (`register_module`) to read the declared `output_schema`; enforce via `complete()`'s existing validate/retry (`client.py:75-87`).
- **C1.5 volatile / per-draw** — MODIFY `nodes/llm.py`: mark VOLATILE (or a sampling-aware draw id) so identical config+input don't collapse at the memo gate (`scheduler.py:96`). A jury role passes `draws:N` → N varied requests.
- **DON'T** let app-use and cognition-use fork the substrate: one registry/compile/executor/store/render; two drivers (`Suite.run`, `_run_swarm`).

## G2 · Role registry

**Principle:** generalise `ROLE_REGISTRY` (`suite.py:929`, a hardcoded one-entry dict) into file-discovered registry data — mirror how node-types self-register (`registry.py`). The judge's comment already names this growth path.
- NEW: `roles/` dir, one file per role (self-registering), each declaring the role schema (Criteria C2.1). MODIFY `suite.py` `resolve_role`/`ROLE_REGISTRY` → read from the discovered registry. The `roles` rhm_config slot stays the per-binding override.
- The `listening` cast (C2.3): `focus` (selector — reads utterance, outputs which-roles + part-1 shape) · `recall` (utterance+memory → past context) · `ground` (live state → citable facts) · `connect` (topic+thread → a link) · `check` (forming answer vs ground → contradiction; chains AFTER part starts) · `voice` (persona+answer → tone). Each declares its input addresses + output schema + rule.
- Jury (C2.4): a role with `draws:N` + a verdict rule → uses C1.5.
- DON'T hand-write `recommended_model` prose — derive suitability from G8 (`role.requires ⊆ model.provides`).

## G3 · Rule engine

**Principle:** full declared logic, but a rule is DATA evaluated deterministically — never a model call. Mirror the `gate` node's predicate but richer.
- NEW: `cognition/rules.py` — a declared-rule evaluator (conditions over a role's output fields + chain triggers). REFERENCE `nodes/gate.py` (the selective-emit precedent). DON'T allow a rule to call a model (that's a role); DON'T allow non-deterministic constructs (keep replay-identical, C0.2).
- Destinations (C3.2): inject (write→address, resolved by a later part) · chain (fire a dependent role) · address (land for later) · surface (the inbox/decision path — reuse `surface_review`/the existing inbox) · typed-lane (a channel). Each is a declared destination kind.
- Gating (C3.4): a new rule/role commits like any change (review + `drift_acceptance`), no special approval.

## G4 · Staged-response queue

**Principle:** a part is a node, a role-output is an address, a part fires when its inputs resolve — the reactive scheduler relationship applied intra-turn (`04`). Cleanest as a small in-turn runner speaking the same "fires-when-deps-resolve" language (not necessarily the full `runtime/` scheduler — open, see `04`).
- MODIFY `suite.py`: this is a **hot-path REFACTOR, not additive (corrected, R1-FOLD F4)** — `chat_parts()` can't loop `chat()` (re-runs the capability-gate, emits N chat events) nor copy it (forks the brain), so **extract `chat()`'s body into a shared core** that both `chat()` (one part) and `chat_parts()` (N parts) call. This touches the `rhm_*`-gated hot path → gate the change on the `rhm_*` regression suites + a "what still works" enumeration. A `THOUGHT_SHAPES` registry (per-mode part templates); `shape_for(mode)`. Part 1 deps=[] (fires instant); later parts dep on **`run://`** role addresses (F3 read).
- Part grain (C4.1): a per-mode config table. Brevity bypass (C4.3): a cheap `brevity_judge` role; `focus`/`background` modes → never stage.
- Coherence (C4.4): each part's prompt prefills the prior parts + "continue naturally."
- DON'T stream brain tokens (out of scope; the PART is the unit). DON'T offer tools on intermediate parts (C4.5).

## G5 · Activation contexts

**Principle:** generalise "mode" from presence-modes to activation-contexts (`B3-R4`). Per-turn is the spine (G0–G4); the others are triggers that fire a cast without a user turn.
- Background: a scheduled/idle trigger fires a mode's background cast → destinations = surface/address (not a spoken reply). Sense: a screen/app/state-change event triggers a cast. Rollup: the introspective-data-building loop consolidates the swarm's own run-records (`swarm://` persisted, G-dev-call).
- Mode declares: the cast, the part-grain, the slot budget, and which activation-contexts are live. DON'T let a background/sense swarm exceed its mode's slot budget (the floor for the live stream is sacred).

## G6 · Voice coupling

**Principle:** the multi-part design IS the voice-streams-as-it-thinks mechanism (`05`). The unit of synth is a caller decision — a "part" becomes the unit with near-zero change to `speak()`.
- MODIFY `runtime/bridge.py` `/api/voice/stream` (~357-468): consume the sequence of parts from `chat_parts()` — synth + emit each part's chunk as it completes (overlap with the next part's generation). PRESERVE: in-order playback (`useAppController.ts` `playCursorRef`), iOS unlock (`primeAudio`), trial recording (once at turn end), one chat-event regardless of N parts, cancellation gated on part-gen too.
- `needs-tim`: the on-device feel + audio.

## G7 · Live cognition view (first build)

**Principle:** registry data → render rules → the canvas (reflects-never-owns), reusing the `decision.*` SSE pattern (`06`).
- NEW backend: a `cognition` registry serializer (a `build_object_info` sibling) + a `cognition.*` emit-contract (per-turn role-fires/injections, addressed to `ui://cognition/<turn>` + role instances at `run://<turn>/<role>` — reuse `run://`, don't mint `cog://`) + cognition node-states.
- NEW FE: a `CognitionView` region + a `RoleShape` (NodeShape sibling) + cognition `Edges` + a `cognition.*` branch in `openStream()` (mirror `decision.*` at `useAppController.ts:384`).
- FORM: design-system components + tokens; design-critic graded.

## G8 · Model + capability registry

**Principle:** three keyings kept distinct + JOINED (`B4`): intrinsic capability (by model-id, net-new) ⨝ service deployment (by service-key, `services.json`, exists) ⨝ telemetry (exists).
- EXTEND, don't duplicate (corrected, R1-FOLD F9): `suite.py` already has `MODEL_KNOBS` + `knobs_for()` (tagged "G8.1" in-code) with declared/probed provenance + a live tools-probe — grow THAT into the capability registry (tool-calling · json_schema · thinking · context-ceiling · **`max_num_seqs` + KV-derived concurrency** · speed), don't stand up a parallel `MODEL_CAPABILITIES` surface (L1 one-source). A role `requires` field; computed suitability replaces `recommended_model` prose.
- REUSE unchanged: `ops/cli/gpu.py` (VRAM authority — point at it, never copy), the co-residence work, `model_supports_tools`. The swarm `Semaphore` reads `concurrency_knee` from here. `resident_capable` is DERIVED from the join, never declared.

## G9 · Governance & safety

- C9.1: roles act through the EXISTING governance posture (`guard()`/POLICY) — in permitted modes the reversible/AUTO classes only; mirror `decide-for-me`. C9.2: `_run_swarm` is OFF the MCP face; no role path can reach build-dispatch/`claude -p` (lead-only — adversarially verify a role cannot escalate). C9.3: every failure mode is a loud legible surface.

---

## File territory (NEW / MODIFY / REUSE / REFERENCE)
- **NEW:** `runtime/cognition.py` (swarm helper) · `cognition/rules.py` (rule evaluator) · `roles/*` (file-discovered roles) · FE `regions/CognitionView.tsx` + `RoleShape`.
- **MODIFY:** `runtime/scheduler.py` (parallel wave) · `runtime/suite.py` (`chat_parts`, role registry, THOUGHT_SHAPES — the serial spine, highest blast radius) · `runtime/bridge.py` (`/api/voice/stream` parts, `/api/cognition*`, the `cognition.*` emit) · `node_record.py` (edge `kind`) · `registry.py` (output_schema) · `nodes/llm.py` (volatile) · `fabric/vram.py` (wire the gate) · `ops/services.json` + `ops/cli/*` (MODEL_CAPABILITIES) · `canvas/app/src/useAppController.ts` (cognition SSE branch).
- **REUSE:** `gpu.py`, `_chat_context`/`_resolve_context_at`, `complete()` validate/retry, `gate.py` (predicate precedent), the inbox/`surface_review`, the `decision.*` render pattern.
- **REFERENCE (don't change):** the judge as the role template; the node-type self-registration pattern; the `rhm_*` regression suites (the gate on `suite.py` edits).
