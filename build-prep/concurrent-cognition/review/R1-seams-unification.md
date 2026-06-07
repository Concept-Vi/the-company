# R1 — Seams & Unification Review

*Plan-review round 1, read-only. How the Concurrent Cognition plan's proposed pieces actually JOIN the existing `~/company-cognition` code. Every claim below is traced to file:line in the worktree as it stands on `concurrent-cognition` (2026-06-07). Where the plan's reuse claim is mechanically wrong, it is marked **WRONG**; where it's harder than implied, **HARDER**; where clean, **CLEAN**. The plan's own line refs are mostly slightly off (the code has grown) but point at the right region — noted only where it changes the work.*

> Evidence classification (per CLAUDE.md): **Observed** = read directly in code. **Inferred** = pattern-matched, labelled, not execution-verified. No claim below was execution-verified (this is a read-only review) — so functional claims about the *built* code are Observed-structural; claims about how the *proposed* code would behave are Inferred.

---

## Seam 1 — Parallel wave executor meets the single-writer store

**Plan claim (C1.1, Guide G1):** "dispatch the ready-set via a `ThreadPoolExecutor` firing the existing blocking transport … Keep a barrier per wave; serialize store writes (the store is the single-writer truth)."

**What the code actually is (`runtime/scheduler.py:37-184`, Observed):**

The scheduler is not just "strictly serial" — its `run()` is **serial by construction in a way that resists a dispatch-line swap.** One `while … progress:` loop wraps a single `for nid, ex in by_id.items()` pass that **interleaves** readiness-check (`73-77`) → memo gate (`96`) → `mod.run()` dispatch (`103`) → per-port store writes (`144-150`) → bookkeeping (`ran/skipped/processed/failed/progress`, plain `set`/`dict`, mutated mid-loop). The post-loop prune/`stuck` classification (`155-182`) then reads `ran | skipped` after the loop completes.

So C1.1 is a **loop restructure, not a dispatch-line wrap.** You cannot drop a `ThreadPoolExecutor` around line 103. The honest shape is: (1) compute the ready-set from store state, (2) parallel-dispatch that set, (3) **join barrier**, (4) do the per-port writes + bookkeeping for the wave, (5) recompute the next ready-set. The prune/stuck closure stays after the final barrier. The plan's "wave-synchronous … keep a barrier per wave" language is right; the Guide's "dispatch … via a ThreadPoolExecutor firing the existing blocking transport" undersells that the surrounding loop, the `ran/skipped/processed` mutation, and the readiness recompute all move.

**Does "serialize store writes" actually hold? — mostly YES, but not for the reason the plan gives (Observed, `store/fs_store.py`):**

- `set_ref` (`215-243`) is **already atomic + concurrency-safe by construction**: tmp + `os.replace`, with a unique tmp name *per write* (pid+thread). Two parallel nodes write **distinct** addresses (each node owns `run://<g>/<nid>`), so they never contend. You do **not** need a wave barrier to make `set_ref` safe — it is safe today.
- `put_content` (`184-198`) is write-once + content-addressed; two threads writing identical content write identical bytes to the same path (idempotent), different content → different paths. Safe.
- `_append_ref_version` (`245-258`) is lock-free `O_APPEND` of a sub-PIPE_BUF line — documented atomic, storm-tested.
- **`memo_set` (`309-310`) is the one soft spot: a bare `write_text`, NOT atomic, NOT fsync'd.** Two threads computing the same sig (only happens for a jury role with identical config+input — which C1.5 explicitly makes volatile/varied, so they *won't* share a sig) would write the same cas → benign. Different sigs → different files. **Inferred:** safe in practice, but it is the only non-atomic hot write and deserves a one-line note if a wave can ever produce a sig collision.

**Net:** the plan's framing "store writes serialize safely [because of the barrier]" is imprecise. The store is safe because **each node writes a private address**, not because of any serialization. The barrier is needed for the *scheduler's own bookkeeping sets and the readiness recompute*, not for store-write safety.

**Deadlock / race risk (the task asked; the plan does not address):**

**Verified no store lock is held across a fan-out join (Observed):** `scheduler.run()` takes **no** `graph_lock` and no `surfaced_lock` — it calls `store.set_ref/put_content/memo_set` directly (`117-150`), none of which acquire `graph_lock`. The Suite acquires `graph_lock` *around* a run at the suite/bridge layer, but the scheduler body holds nothing across its loop. So a worker thread calling `set_ref` cannot deadlock against a coordinator holding `graph_lock` — the lock isn't held during dispatch. **This is the key safety fact and it holds.**

The one real concurrency hazard the plan must respect: **`graph_lock`/`_event_lock`/`surfaced_lock` are `threading.RLock` (`fs_store.py:49,134,135`) — re-entrant *per owning thread only.*** If the parallel rewrite ever has worker threads acquire a lock the coordinator already holds (e.g. each role-run appends an event under a coordinator-held event lock), that is **not** re-entrant across threads and will block. The swarm being **off the MCP face** (`_run_swarm`, per the plan) is what keeps it out of the `graph_lock`/`surfaced_lock` paths — that boundary is load-bearing for deadlock-freedom, not just for governance. **State it as a build constraint:** workers may only touch the store through `set_ref`/`put_content`/`memo_set` (lock-free, private-address) and through `append_event` (which takes its own short-lived `_event_lock`) — never inside a coordinator-held lock scope. → ties directly into **Seam 5**.

**`fabric/vram.py:VramGate` (Observed):** exists, `limit=1`, a `contextmanager slot()` wrapping a `threading.Semaphore`. It is a real, working bound — but it is a **single flat semaphore**, not the "global `Semaphore(knee)` + swarm sub-pool of `knee−R`" two-tier structure C1.2 wants. The two-tier reservation (R slots fenced for the main stream/judge) is **net-new** — and `VramGate` is currently **unwired** (no caller acquires `slot()`). C1.2 is genuinely net-new wiring, not a config tweak.

---

## Seam 2 — The injection edge: promoting C6's resolve from RHM-turn scope to a graph edge

**This is the seam where the plan is INTERNALLY INCONSISTENT, and the inconsistency hides a mechanical error.**

The plan names two *different* mechanisms as "the injection path," in two different documents:

- **Guide principle 3 (correct live path):** "the next part's prompt *resolves* that address through the existing `_chat_context → _resolve_context_at` path (`suite.py:1322,1461,1943`)." This is the **real** path used by `chat()`.
- **Guide G1.3 + Synthesis (the dead path):** "the injection/resolve edge wraps C6's `context_variables.py:49-95` promoted from RHM-turn scope to a graph-edge."

**`runtime/context_variables.py` (the C6 module) is NOT wired into the live runtime (Observed).** The only importers in the whole repo are itself and `tests/e1_acceptance.py` (`grep`-verified across `runtime/`, `mcp_face/`). `chat()`/`_chat_context` never import it; they use `_resolve_context_at`. So "promote `context_variables.py:49-95`" promotes a module that isn't in the live circuit. **Present it precisely: the plan is internally inconsistent — the correct path is named in principle 3, a dead module in G1.3.** Build against `_resolve_context_at`, not `context_variables.py`.

**Worse — the *correct* path doesn't do what the plan needs either (WRONG, Observed, `_r2_gather` at `suite.py:1778-1817`):**

`_resolve_context_at` → `_r2_gather` resolves a locus by gathering **operator-attached notebook strata** at the address and its ancestors: annotations (`annotations_at`), chats (`chats_at`), and addressed *events* (`_r2_events_at`), then dedups/scores/caps them into a prose block. It does **not** do `store.head(addr) → get_content(cas)` on a freshly-written output ref.

A role writing its JSON to `swarm://<turn>/<role>` (the plan's mechanism, C4.2) would be **invisible** to `_resolve_context_at` — that path doesn't read raw refs, it reads the comment/chat/event notebook. So "injection = address-resolution via the existing `_chat_context` path" (C4.2) is **mechanically wrong as written.** Injecting a role's output requires a **new resolution branch** that reads the ref's content (`store.head` → `get_content` → format into the part's prompt). That is net-new code, small but real, and it is the actual heart of C0.1's injection — not a reuse.

**On the edge itself (`contracts/node_record.py:35-39`, Observed):** `Edge = {from_node, from_port, to_node, to_port}` — no `kind`. Adding `kind: str = "data"` is trivially schema-additive (satisfies AGENTS rule 2). **But the field add is the easy 5%.** `runtime/compile.py:93-111` treats *every* edge identically (wire → address ref). For an injection/gate/fan-in edge to behave differently from a data-wire, **compile and/or the scheduler must branch on `kind`** — that behavior is net-new. C1.3's "register edge-kinds in the registry" + "the injection edge resolves an address into a downstream node's context" is a compile+scheduler change, not a contract-field change.

---

## Seam 3 — File-discovered role registry replacing the hardcoded ROLE_REGISTRY

**Plan claim (C2.1, Guide G2):** generalise `ROLE_REGISTRY` (`suite.py:929`, "a hardcoded one-entry dict") into file-discovered registry data, mirroring node-type self-registration.

**CLEAN — this is the best-matched seam.** (Observed.)

- `ROLE_REGISTRY` is real, at `suite.py:943` (plan said 929 — off by the model-knob block that grew above it). It is exactly one entry (`judge`), a `dict` keyed by role-id, each value a declared contract (label/trigger/default_model/recommended_model/knobs/output/tools/context/env_*).
- **Its readership is small and fully enumerated (grep-verified):** config-binding validation (`1176`, `1236-1237`), the `roles()` status read (`3172-3184`), `resolve_role()` (`3186-3210`), and `is_finished_thought()` (`3289`). That is the *entire* breakage surface. Nothing in `mcp_face/`, `canvas/`, `ops/`, or `tests/` reads `ROLE_REGISTRY` directly (only `suite.py`).
- The replacement must preserve **the `resolve_role()` contract** (`3186-3210`): precedence config-binding > env > declared-default, `None` default_model → the brain (`cfg["model"]`), fail-loud on unknown role. `is_finished_thought` and `roles()` both go through `resolve_role`, so if `resolve_role` keeps reading from a discovered registry instead of the dict, **those two callers don't change.** Clean swap point.
- The self-registration model to mirror is `runtime/registry.py:35-64` (`NodeRegistry.discover` → `register_module`): scan a dir, skip `_`-prefixed, require a `run` attr, build a typed descriptor. A `roles/` discoverer is a clean sibling.

**One nuance the plan blurs:** G2 says "mirror how node-types self-register (`registry.py`)." A role is **not** a node-type — it has no `run`/`PORTS`/`KIND`. So this is a *new sibling registry class* (a `RoleRegistry`), not a reuse of `NodeRegistry`. The pattern transfers; the class does not. Minor, but worth not conflating in the build.

**C2.2 (judge as role #0):** trivially satisfied — `judge` already IS the sole registry entry; file-discovery just moves it to `roles/judge.py`. The behaviour-unchanged bar holds as long as `resolve_role("judge")` returns the same effective dict.

---

## Seam 4 — chat_parts() sitting beside chat() without forking the brain

**Plan claim (C4.2, Guide G4):** "`chat_parts()` beside `chat()` (`chat():3333` is the single-shot path — preserve it; additive)."

**HARDER than "additive" — this seam forces a hot-path refactor, with regression risk. (Observed, `chat()` at `suite.py:3347`.)**

`chat()` is the RHM hot path and does several things a parts-loop must each handle *exactly once per turn*, not once per part:

1. **Capability-gate** (`3371-3381`): refuses fail-loud if the selected model isn't tool-capable. Re-running this per part = N model-capability probes per turn.
2. **History append** (`append_chat` of the user turn + assistant reply): one user turn, one assistant reply per turn. A naive parts-loop would append N assistant turns.
3. **One `chat` event** (`_emit("chat", …)`, `3358`/`3379`): the FE chat refresh keys on it. The plan itself says "one chat-event regardless of N parts" (G6) — a loop over `chat()` violates that.
4. **Tool-offering** (`_rhm_tools(mode, ctx)`): the plan wants **tools on the final part only** (C4.5). `chat()` always offers tools.

So `chat_parts()` can be **neither** a loop over `chat()` (re-runs the gate, emits N events, appends N turns — wrong) **nor** a copy of `chat()`'s body (forks the brain — the explicit thing the task says not to do). The real shape is **factoring `chat()`'s body into a shared core** (`_chat_once(ctx, offer_tools: bool) → reply`) that both `chat()` and `chat_parts()` call, with the gate/history/event/tool-offering decisions lifted to the *caller*. That **modifies the hot path** — and the hot path is gated by the `rhm_*` acceptance suites (`rhm_acceptance`, `rhm_action_acceptance`, `rhm_completion_acceptance`, `rhm_grounding_acceptance`). The change is not "additive beside `chat()`"; it is "refactor `chat()` so a second caller can reuse its core." Doable, but it carries the highest regression blast radius in the build (consistent with the plan's own "serial spine on suite.py" note — just name the *reason* it's risky: shared-core extraction, not addition).

---

## Seam 5 — cognition.* events riding the existing SSE

**Plan claim (G7):** drive the live thought-graph from `cognition.*` SSE events, reuse the `decision.*` render pattern.

**The transport is CLEAN; the volume/serialization is a real, unmentioned risk. (Observed.)**

- **CLEAN:** `/api/stream` (`bridge.py:324-355`) tails the **shared `events.jsonl`** and pushes *every* event by seq, regardless of `op`/`kind`. So `cognition.*` events ride it automatically once written via `_emit`/`append_event` — no transport change. The FE branch slots in exactly like `decision.*`: `useAppController.ts:390` already does `k.startsWith('decision.')`; a sibling `k.startsWith('cognition.')` is the same one-line extension point the plan names.

- **HARDER (the Seam-1 connection the plan misses):** every `cognition.*` event goes through `append_event`, which per STATE.md (T1-SEQ) holds `_event_lock` **and** is **fsync'd before atomic rename** (`fs_store.py:414-433`, the durable governance-grade path). That log was designed for **low-frequency, durability-critical events** (the wire's exactly-once `decision.dispatch` claim depends on its atomicity). Now point a **32-way swarm** at it firing per-role-fire/injection events: (a) all 32 worker threads **serialize on the single `_event_lock`**, and (b) each event pays an `fsync`. That is both a **throughput bottleneck on the hot turn path** and a **flood through a log whose other writers need it slow and durable.** This is the direct consequence of Seam 1's "workers append events" — the parallel executor's telemetry contends on the one serialized, fsync'd log.

  **Mitigations to consider in the build (flagged, not prescribed):** a separate non-fsync'd cognition-event lane (the introspective `swarm://` run-records the dev-calls already lean toward persisting), or batched/coalesced emission, or emit cognition frames to a lighter channel and reserve `events.jsonl` for the durable governance events. Either way: **do not naively route 32-way per-fire telemetry through `append_event` as-is.**

- **FE render cost (HARDER):** the `decision.*` branch (`useAppController.ts:396`) responds to each event with a **coarse refetch** (`api.inbox()`, `api.now()`, `api.lastChange()`, `api.panels()`). Copying that pattern for a rapid `cognition.*` stream = a full multi-endpoint refetch per role-fire — a render storm. G7's live thought-graph needs a **fine-grained, event-payload-driven** node-state update (read the role status off the event itself), not the decision branch's refetch-everything reflex. The *pattern* (a `startsWith` branch) reuses; the *handler body* should not.

---

## Seam 6 — Roles binding models through the capability-registry JOIN to gpu.py

**Plan claim (C2.5/C8.2, Synthesis B4):** a role binds a model-id → reads `MODEL_CAPABILITIES` → if locally served, looks up the backing service for VRAM via `gpu.py`; "`_local_brain_key` already does the match," "`concurrency_knee` becomes data."

**Mostly NET-NEW; the synthesis OVERSTATES what exists. (Observed / grep-verified.)**

- **`MODEL_CAPABILITIES` does not exist** anywhere (repo-wide grep, `--include=*.py`, empty) — fully net-new (the plan does mark it net-new in the ledger; just don't let B4's prose imply a JOIN substrate is already there).
- **`concurrency_knee` does not exist** anywhere in the repo (repo-wide grep, empty). C1.2/C8.1 treat it as "a registry value, not hardcoded 32," but there is **no such field today.** The closest existing analog is `services.json` `chat-4b.config.max_num_seqs` (the vLLM batch param) — a candidate source, but the mapping `max_num_seqs → concurrency_knee` is a design decision the build must make, not a value to read.
- **`_local_brain_key` EXISTS but is narrower than the synthesis implies** (repo-wide grep: `runtime/bridge.py:75-83`, called at `:843` — *not* in `suite.py`/`gpu.py` where I first looked). It *does* do a model-id → service-key match — but **scoped to the single active brain**: `next(k for k,s in reg["services"] if s.group=="brain" and s.config.model == rc["model"])`, returning `None` for a cloud/ollama brain. So the synthesis's "`_local_brain_key` already does the match" is **partially right (mechanism present), over-stated (scope wrong)**: it resolves *the one active brain* to its service, not *any role's model-id* to its backing service. The general model-id → service-key resolver the JOIN needs (so a role bound to a non-brain local model can be VRAM-sized) is a **generalisation of this 9-line function**, not net-new-from-zero. Good news — the *pattern* (scan `services` for `config.model == X`) is proven and reusable; the build widens its scope past `group=="brain"`.
- **What IS real and reusable (CLEAN):** `ops/cli/gpu.py:32` `budget_vram(reg, key)` is the VRAM authority — it takes a **service key** (e.g. `"chat-4b"`), not a model-id. `fit_report` (`:129`) exists. So the JOIN is buildable: `_local_brain_key`'s match-pattern generalised → a service key → `budget_vram`. "Reuse `gpu.py`" is correct; "the join already works" overstates a single-brain helper into a general resolver.
- `resident_capable` (Synthesis: "DERIVED from the join, never declared") does not exist (repo-wide grep, empty) — net-new, consistent with the above.

**Net:** Seam 6 is the seam where the plan's *synthesis* most over-claims existing scaffolding. The VRAM authority (`gpu.py`) is real and should not be duplicated (correct). Everything between a role's `requires` and that authority — capabilities table, model-id→service-key bridge, knee-as-data, resident_capable — is net-new.

---

## Seam 7 — Voice coupling: parts as the TTS streaming unit (brain ↔ TTS overlap)

**Plan claim (C6.1/G6):** "synth part N while the brain generates part N+1 (overlap brain↔TTS) … the PART becomes the synth unit with near-zero change to `speak()`."

**HARDER than "near-zero change." (Observed, `bridge.py:_voice_stream` 357-487.)**

`speak()` itself is indeed reusable near-unchanged — that half of the claim holds. But the **current voice circuit has zero brain↔TTS overlap**, and getting it requires restructuring `_voice_stream`, not just swapping the synth unit:

- Line **435**: `thought = SUITE.chat(transcript, gid)` — the brain produces the **ENTIRE reply in one blocking call** *before any TTS happens.*
- Lines **449-460**: the reply is then `re.split` into **sentences** and each sentence is synth+streamed. So today's overlap is **synth ↔ playback only** (the FE plays chunk N while the bridge synths chunk N+1) — exactly what the synthesis's own R1 note says ("the only overlap is synth↔playback").

To get the plan's **brain ↔ TTS** overlap (C6.1: "audio of Part 1 plays before Part 2 is generated"), the single blocking `SUITE.chat()` at line 435 must become an **iterator/generator of parts** (`chat_parts()`), and the loop at 449 must consume *parts as they are produced by the brain* rather than *sentences of an already-finished reply.* That is a real control-flow change to `_voice_stream`, and it depends entirely on Seam 4 (`chat_parts` existing as a generator) — which itself depends on the Seam-4 shared-core refactor. So G6 is **transitively gated on the hardest seam (4)**, and the "near-zero change to `speak()`" framing, while literally true of `speak()`, hides that `_voice_stream`'s think→speak structure inverts.

- **What IS preserved cleanly (Observed):** the FE in-order playback (`playCursorRef`, `useAppController.ts:1198`), the per-turn durable record (`emit_run_record("voice.stream", …)`, `470`), client-disconnect cancellation (`client_gone()`, `391-404`), trial recording (`trial_record_turn`, `441-442`). These ride along — the change is *where the reply text comes from*, not the surrounding plumbing. The plan's preservation list (G6) is accurate.

---

## Cross-cutting

- **Plan line refs drift** (code has grown): ROLE_REGISTRY 929→**943**; chat 3333→**3347**; the `_chat_context/_resolve_context_at` cluster is at **1336/1957** not 1322/1461/1943. Region-correct, line-stale. Low-impact (an implementer greps), noted for accuracy.
- **The serial-spine ordering (G0→G4 on `suite.py`/`bridge.py`/`scheduler.py`) is the right read** — Seams 1, 4, 7 all converge on those three files and chain (7 depends on 4 depends on the chat-core refactor; 1 is the executor under all of it). The "3 disjoint parallel lanes" (json_schema transport, llm-volatile, canvas FE) are genuinely independent and confirmed file-disjoint: `transport.py` (one branch at `:37` already does `json_object` — extend to `json_schema`), `nodes/llm.py` (add `VOLATILE`/draw-id), `canvas/app/` (the `cognition.*` FE). These three can run parallel to the spine.
- **The off-MCP boundary for `_run_swarm` is doing double duty** — the plan frames it as a governance floor (C9.2, roles can't reach `claude -p`). It is **also** the deadlock-safety floor (Seam 1): keeping the swarm out of the `graph_lock`/`surfaced_lock` paths is what makes the parallel executor safe against the per-thread RLocks. Worth stating that one boundary carries both guarantees.

## The honest seam scorecard
| Seam | Plan's framing | Real shape |
|---|---|---|
| 1 Parallel executor | barrier + serialize store writes | **loop restructure**; store already safe via private addresses; deadlock-safe *iff* swarm stays off lock paths; VramGate unwired + single-tier |
| 2 Injection edge | promote C6 `context_variables`; reuse `_resolve_context_at` | **internally inconsistent + WRONG**: C6 module dead; `_resolve_context_at` reads notebook strata, not raw refs — injection needs a net-new ref-read branch; edge `kind` add is easy, per-kind *behavior* is net-new compile/scheduler |
| 3 Role registry | file-discover, mirror node registry | **CLEAN**; small enumerated readership; swap at `resolve_role`; it's a *sibling* registry, not `NodeRegistry` reuse |
| 4 chat_parts beside chat | additive | **HARDER**: forces shared-core refactor of the hot path; rhm_* regression risk; not additive |
| 5 cognition.* on SSE | reuse decision.* pattern | transport **CLEAN**; **but** 32-way telemetry floods the serialized fsync'd `append_event`; FE needs payload-driven update, not decision-branch refetch |
| 6 Model JOIN to gpu.py | `_local_brain_key` already matches; knee is data | **mostly net-new, partly seeded**: `_local_brain_key` (bridge.py:75) DOES match model-id→service but only for the single `group=="brain"` model — generalise it; `concurrency_knee`/`MODEL_CAPABILITIES`/`resident_capable` absent repo-wide; `budget_vram` real but service-keyed |
| 7 Voice parts | near-zero change to speak() | `speak()` yes; **but** brain↔TTS overlap inverts `_voice_stream`'s think→speak structure; transitively gated on Seam 4 |
