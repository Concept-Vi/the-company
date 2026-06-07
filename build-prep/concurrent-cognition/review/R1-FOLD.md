# Round 1 Review — Consolidated Fold + Revised Positions

*Five read-only reviews (reference · seams · flow-trace · adversarial · consistency-laws) against the live worktree. Verdict: the **architecture is sound** (every net-new piece genuinely absent; the reuse spine genuinely present; the `claude -p` floor + substrate-reuse claims survive), but the triad **over-credited reuse** and had **one central failure (the resource ceiling)**. This doc is the authoritative correction layer; the triad docs are edited in place to match (no-versioning). Severity-ordered.*

---

## F1 · RESOURCE CEILING — the central failure (Adversarial Attack 1). FOLD: reframe everything that says "32."
- **Reality:** the resident 4B serves `max_num_seqs = 16` (serve config), and its KV pool is *shared with the main 64K context*. At high concurrency each sequence gets ~2K tokens → preemption/recompute thrash; the factsheet's "7–8× at 32K" is the warning. **You cannot run 32 concurrent role-runs at the 64K voice config.**
- **Revised position:** the swarm cap is **`min(max_num_seqs − R, KV-budget / per-role-context)`**, read from the registry — NOT a hardcoded/assumed 32. **Roles must be short-context** (small prompt + small JSON) so many fit; a long-context role costs a "seq slot" worth of KV. The realistic co-resident-with-voice ceiling is **well below 16** at usable context.
- **Criteria edits:** G0 gains **C0.5 — measure the real co-resident concurrency AND the inter-part wall-clock on the 0.49 voice config, with a staged reply running** (the spike must produce the real number, not assume one). C1.2 reworded: semaphore reads `max_num_seqs` + KV math, not 32. G8: `concurrency_knee` is `max_num_seqs`-bounded + KV-derived, not the throughput-benchmark 32.

## F2 · WHERE PARALLELISM LIVES — unresolved seam (Attack 2; Guide G1.1 vs G4 disagree). FOLD: decide.
- G1.1 said "modify `scheduler.py`" (the **shared** layer → would make every app `Suite.run` concurrent too — a behaviour change to the governed app face). G4 said "a small in-turn runner, not necessarily the scheduler."
- **Revised position:** parallelism lives in the **cognition driver** (`_run_swarm` / the in-turn part runner), **not** the shared `scheduler.py`. The app surface stays serial unless it opts in later. "Two thin drivers, one substrate" is preserved by keeping concurrency a property of the cognition driver. Guide G1.1 + G4 edited to point at the *same* runner.

## F3 · INJECTION IS NET-NEW, not reuse (Seams 2 + Flow 1 + Reference). FOLD: reclassify + correct the path.
- `_resolve_context_at`/`_r2_gather` (suite.py ~1778/1957) resolves the **operator notebook strata** (annotations/chats/events), NOT freshly-written role refs — a role's `run://<turn>/<role>` JSON would be **invisible** to it. And G1.3's "promote `context_variables.py`" names a module imported **only by a test** (dead in the live circuit).
- **Revised position:** injection is a **net-new ref-read branch** in the part-context assembly — the next part's prompt reads the resolved values at the role addresses written this turn. Guide principle 3 + G1.3 corrected; injection moves from "reuse" to "net-new" in the Synthesis ledger. **Address scheme = `run://` throughout** (drop every `swarm://` — not a registered scheme; `contracts/address.py` SCHEMES = run/cas/blob/vec/ui/code).

## F4 · chat_parts IS A HOT-PATH REFACTOR, not additive (Seams 4+7). FOLD: reclassify + gate.
- `chat_parts` can't loop `chat()` (re-runs the capability-gate, emits N chat events) nor copy it (forks the brain) → it **forces extracting `chat()`'s body into a shared core**, modifying the `rhm_*`-gated hot path. Voice (G6) inverts `_voice_stream`'s think→speak structure (bridge.py:435 blocks on the whole reply today) and is transitively gated on this.
- **Revised position:** G4 is a **refactor of the gated hot path** (extract a shared core; `chat()` and `chat_parts()` both call it), explicitly gated by the `rhm_*` regression suites + a "what still works" enumeration. Higher blast radius than "additive beside chat()" — sequenced as serial-spine, verified hard.

## F5 · RULE DETERMINISM — asserted, not enforced (Attack 5; the "full declared logic" hole). FOLD: specify enforcement.
- Under parallel dispatch, roles in a wave finish in **nondeterministic order**. If a full-logic rule can fire on partial results, read which-sibling-finished-first, or branch on a count-so-far, then C0.2 ("re-run → identical routing") breaks — routing would depend on a race, not on resolved values.
- **Revised position:** the rule evaluator (`cognition/rules.py`) evaluates **post-barrier, as a pure function of fully-resolved address values only**, against a **referenceable-input whitelist** (resolved role outputs only); **banned:** `now()`/random/wave-order/partial-results. Criteria C3.1 + C0.2 edited: C0.2 must test a **non-trivial** rule and prove replay-identical routing.

## F6 · THE `claude -p` FLOOR — holds, but must be encoded (Attack 4). FOLD: restate as an invariant + test.
- The floor holds today, but only because no current AUTO verb emits a `resolve` event; it becomes false the instant a future role-reachable AUTO verb does.
- **Revised position:** C9.2 restated as the **unforgeable-`resolve`-event invariant** — *no role path may emit a `resolve`/`approve` event* — plus a regression test asserting it (not "falls out because `_run_swarm` is off-MCP").

## F7 · ACTIVATION SUBSTRATE (G5) IS FULLY NET-NEW (Flow 2). FOLD: size it honestly.
- Repo sweep: the only backend `while True` is the SSE keepalive; **zero `.timer` units**; `background` is just a directive string. There is **no activation substrate** — background/sense/rollup are **three net-new subsystems**, not "generalise mode."
- **Revised position:** G5 reclassified net-new + sequenced *after* per-turn works; the Guide names the three triggers (a scheduler/timer for rollups, an event-hook for sense, an idle-loop for background) as net-new build, each under a mode's slot budget.

## F8 · TELEMETRY FLOOD + STORE ATOMICITY (Seam 1↔5 + Attack 3). FOLD: add a criterion.
- The store has no corruption race (wave-barrier + distinct per-port addresses + atomic `set_ref` defuse it). BUT the swarm's per-role `cognition.*` run-records would **flood the serialized, fsync'd `append_event`**; and `memo_set`/`write_provenance` aren't atomic-ized like `set_ref`.
- **Revised position:** new criterion — **swarm telemetry is batched/throttled** (one rollup event per turn, not one fsync per role-fire); atomic-ize `memo_set`/`write_provenance`. A cheap concurrent in-process store test in G1.

## F9 · Smaller, real (fold into wording)
- **`json_object` ≠ `json_schema`** (transport.py:37 sets `json_object`). True server-side schema-constrained output is a real transport change; the **client-side validate/retry (`client.py:75-87`) is the actual enforcement** (+ latency per malformed draw — feeds F1/inter-part stall). Synthesis "one branch away" softened.
- **`llm` per-draw cache-key, not blanket VOLATILE** (memoization is a real app feature; `model_of_tim.py:11` shows the VOLATILE pattern). C1.5 leads with the per-draw id.
- **Edge `kind` = a CONFIRM-level contract edit** (`contracts/node_record.py:35`, no `schema_ver`) — flag CONFIRM + vault-spec update + a default-kind for existing edges; not routine MODIFY.
- **`cognition.*` is runtime event-strings, not a `contracts/` contract** — needs runtime-emit + drift docs, not a CONFIRM.
- **G8 reconcile with existing `MODEL_KNOBS`/`knobs_for()`** (already tagged "G8.1" in-code) — extend, don't build a parallel capability surface (L1).
- **Scheduler has no materialized ready-set** (re-scanning loop) — C1.1 builds it before parallelizing.
- **Self-description/drift homes** must be named for every net-new registry (roles, MODEL_CAPABILITIES, edge-kinds).
- **Stale line refs (~+14):** ROLE_REGISTRY 943 (not 929), `_chat_context` 1336, `_resolve_context_at` 1957, `chat` 3347; **`node_record.py` is in `contracts/`, not `runtime/`.** → build agents locate-by-symbol, not by line.
- **VRAM/KV co-residence** of the swarm pool ⨯ the resident 4-bit voice must be accounted (the card is already ~0.6 GB over at the marquee config) — ties to F1.

## Net effect on the build
- The **reuse ledger shrinks**: injection, chat_parts (refactor), G5, the jury flow move to net-new. The architecture and the spine still hold.
- **G0 is now a measurement gate, not just a feel gate** — it must produce the real concurrency ceiling + inter-part wall-clock on the voice config before fan-out.
- Two design decisions are now made: **parallelism in the cognition driver** (F2), **`run://` addressing** (F3).
- Determinism (F5) and the `claude -p` floor (F6) become **enforced invariants with tests**, not assertions.
