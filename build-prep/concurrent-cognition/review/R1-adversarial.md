# R1 — Adversarial Review (attempt to DISPROVE the plan)

*Read-only. The job was to break the load-bearing claims of the Concurrent Cognition triad against the real code in `~/company-cognition` (branch `concurrent-cognition`). Default skeptical. For each attack: does it land, and what is the consequence. Evidence is `file:line` from the worktree as of 2026-06-07. Statements are marked **Observed** (read from the file), **Inferred** (pattern-matched, not executed), or **Verified** (executed — none here; this is read-only).*

---

## Verdict in one line

The two architectural claims (substrate reuse · the `claude -p` floor) **largely survive**. The **resource claim does NOT**: the plan's "~32 concurrent role-runs PLUS the main stream on the resident 4B" is contradicted by the live config and the KV math — it fails on the very config that the marquee proving target (voice) requires. The store-race claim is **mostly defused** by the wave-barrier design (so I downgrade it), but two real lower-severity hazards remain. Rule determinism is **stated as a goal but not enforced**, and "full declared logic" (Q4) is the hole.

---

## ATTACK 1 — "the resident 4B serves ~32 concurrent role-runs + the main stream within its KV pool at real context" — **LANDS HARD (the central failure)**

This is C1.2 ("30+ concurrent role-runs complete; the main stream never blocks"), the `concurrency_knee ~32` premise (G8/C8.1), and the §C.3 slot-budget design in `03-concurrency-and-injection.md`. It rests on `BENCHMARK_FACTSHEET.md` "concurrency 32 → 2,241 tok/s." Two independent blades both cut it:

**Blade 1 — the server admission cap is 16, not 32 (Observed).**
`ops/services.json:60` — the live `chat-4b` config has **`max_num_seqs: 16`**. This is vLLM's hard cap on concurrently-*scheduled* sequences. No matter how many client threads fire, only 16 decode at once; the 17th+ sit in vLLM's WAITING queue. So "30+ concurrent role-runs complete" (C1.2) and "concurrency-knee ~32" (C8.1, the value the swarm `Semaphore` is sized from) are **false against the live registry.** The plan says "knee from the registry, not hardcoded 32" — but the registry value (`max_num_seqs`) is **16**, and nothing in the plan reconciles the swarm's `knee−R` math with it.

**Blade 2 — the KV pool holds ~one 64K context, total, shared (Observed math from the registry profile).**
`ops/services.json:58,59,76,77` give the live numbers: `gpu_util: 0.49` (the **voice-co-residence** util, `HANDOFF-2026-06-07…:30`), `max_model_len: 65536`, `fixed_mb: 5838`, `kv_kb_per_token: 31.7`.
- Pool = 0.49 × 16 GB − 5838 MB ≈ 7840 − 5838 = **~2002 MB of KV**.
- ~2002 MB ÷ 31.7 KB/tok ≈ **~64,700 tokens of total KV budget** — i.e. the whole pool is **one full 64K window.**
- 32 sequences sharing ~64.7K tokens = **~2K tokens each** before vLLM preempts/recomputes. 16 sequences = ~4K each.

This is empirically confirmed by the factsheet's own note (`BENCHMARK_FACTSHEET.md:13`): **"Long context: 32K context max, drops concurrency to 7-8x."** The 2,241-tok/s c=32 number was measured at **4K context** (`BENCHMARK_FACTSHEET.md:11`, TL;DR) — short role contexts, on a server whose `gpu_util` the factsheet **does not record** (so it was almost certainly a standalone higher-util server, not the 0.49 co-resident config; **the plan must not cite it as evidence for the co-resident swarm** — mark its util Unverified).

**The two blades interlock so there is no escape (Inferred from the two Observed facts):**
- *Keep the cap at 16* → only 16 run; "30+ concurrent" is impossible.
- *Raise the cap to 32* → the ~64.7K KV pool gives ~2K tokens/seq → preemption/recompute thrash; latency collapses (the factsheet's "7-8x at 32K" is the warning shot).
- The main conversational reply ALSO lives on this same `:8000` 4B (the plan moves it there, `03 §B`), and its sequential parts carry a growing context — so the main stream is one of the heaviest KV consumers, competing with the swarm for the same ~64.7K.

**Sharpest consequence — the conflict peaks exactly when the demo runs.** `gpu_util: 0.49` is the value chosen *so the 4B co-resides with 4-bit AWQ Orpheus* (`HANDOFF-2026-06-07…:30,93`), and **voice is proving target #1** (G6, DECISIONS Batch 2/4). So during the marquee voice scenario, the swarm, the staged main stream, the judge, AND Orpheus all contend for the same 16 GB. Off-voice you could raise util to ~0.8 (~225K KV tokens — comfortable), but then `max_num_seqs:16` still binds unless ALSO raised, and a ~13 GB 4B can't co-reside with a TTS engine (`HANDOFF.md:138`).

**The reservation logic reserves against the wrong number (Observed design flaw in `03 §C.3`).** The plan sizes a global `Semaphore(32)` at the "knee" and reserves R *there*. But a free client **permit** ≠ a free server **decode slot**. With the real server cap at 16, the main part acquires its permit instantly, then sits in vLLM's WAITING queue *behind in-flight role decodes* — **the exact turn-stall C1.2 / C0.4 promise to prevent.** Layer-1 "temporal separation" (swarm fires *between* parts) carries the weight in the common case, but C1.2 explicitly claims the main stream never blocks *during* a swarm wave, and the budget math (sized to 32) does not deliver that on a 16-seq server.

**The cloud-main escape doesn't save it either (Inferred; closes the obvious rebuttal).** DECISIONS Batch 2 Q3 makes cloud the main brain a *supported* mode — a defender will say "put the main stream on cloud, free the whole ~64.7K pool for the swarm, contention gone." It doesn't rescue C1.2: the swarm *alone* on the full pool still caps at ~16 roles@4K / ~32@2K-with-thrash, so "30+ concurrent role-runs at real context" remains false; and cloud-main *worsens* Attack 6 — every part becomes a cloud round-trip with **no 4B prefix-cache reuse** (`BENCHMARK_FACTSHEET.md:81` is a *resident-4B* measurement), so the inter-part stall grows. The finding survives from either brain config.

**What the plan must change:** the knee is `max_num_seqs` (16 today), not 32; the budget math, the swarm cap, and the semaphore must read THAT; the KV-per-context budget must be a first-class constraint (roles must run at short context, and the part count × context must fit ~64.7K with the swarm); and G0's spike must measure **concurrent role-runs + a staged main reply at realistic context on the co-resident 0.49 config**, not borrow the 4K/unknown-util c=32 number. The spike-gate (G0) is the right place to catch this — but only if it tests the real config, which the current C0.* wording does not require.

---

## ATTACK 2 — "the node mechanism is reused near-wholesale; the dual-use app+cognition split doesn't fracture it" — **MOSTLY HOLDS; one real friction**

The substrate claims check out against the code: the scheduler is the right readiness shape and **strictly serial** (`scheduler.py:59-61` single `for nid, ex in by_id.items()` inside `while … and progress`; **Observed**, no threadpool/async). Role=node, chain=edges, the store's per-port addressing, per-node error isolation (`scheduler.py:104-116`), selective-emit/gate (`gate.py:38-40`), and the generic canvas all exist as `02-graph-substrate-reuse.md` claims. The "concurrent executor IS the scheduler" leg is correctly flagged as the one that needs the net-new parallel build.

**The friction the plan under-states:** the parallel dispatch is built INTO `scheduler.py` (`Implementation Guide` G1.1), which is the **shared** lower layer used by the app surface (`Suite.run`) — but the design wants the *cognition* driver (`_run_swarm`) to be the concurrent one (ephemeral, off-MCP). Two readings of "where parallelism lives" coexist in the triad: G4 says the staged-part runner may be "a small in-turn runner … not necessarily the full `runtime/` scheduler (open)", while G1.1 says modify `scheduler.py` itself. If parallelism lands in the shared scheduler, every app-surface `Suite.run` becomes concurrent too — a behaviour change to the governed app face that the "two thin drivers, one substrate" framing says it's avoiding. **This is not a fracture, but it is an unresolved seam**: decide whether concurrency is a property of the shared executor (blast-radius into the app face) or of the cognition driver only. The plan should name it, not leave G1.1 and G4 pointing at different runners.

---

## ATTACK 3 — "parallel dispatch is safe on the single-writer store" — **DOWNGRADED: no corruption race, but two real lower-severity hazards**

I tried hard to find a corruption/lost-update race and it **does not land at the headline severity**, because of the plan's own mitigations (wave-synchronous dispatch + a per-wave barrier + each node writing to a **distinct** per-port address). The store's hot write is atomic: `set_ref` is tmp+`os.replace`+fsync with a unique per-write tmp name (`fs_store.py:215-227`; **Observed**), `put_content` is write-once (`fs_store.py:196-198`), and the T-RACE/T-SEQ locks exist. Concurrent writes to *different* addresses don't collide. **I will not manufacture a race the barrier prevents.** What is genuinely true, at lower severity:

1. **`memo_set` and `write_provenance` are naked `write_text` — non-atomic (Observed, `fs_store.py:310, 283`).** Unlike `set_ref`, they have no tmp+replace. Under concurrent in-process callers a reader can see a torn memo/provenance file. Consequence is low in the wave model (distinct sigs/addresses, and memo is a cache that re-computes on miss) — but it is an *Inferred* latent torn-read that the plan's "store writes serialize safely" (C1.1) glosses. It is **not** serialized; it is *atomic-per-address for `set_ref` only*. Worth a one-line fix (route both through `_atomic_write_fsync`) before parallel dispatch, and worth the cheap concurrent-in-process test `02 §Provenance` flagged as "not yet verified."

2. **`append_event` is one RLock + an `os.fsync` PER write (Observed, `fs_store.py:433-454`).** The live cognition view (G7) wants `cognition.*` fire/injection events per role. A 32-role wave emitting events serializes through one process-wide lock with a disk sync each — a real **latency/contention cost on the hot path** that the plan never budgets. At ~30 events/turn × fsync, this competes with the very turn-latency budget C0.4/C1.2 are protecting. The event log is also explicitly **not cross-process seq-unique** (`fs_store.py:425-432`) — a second session/process could duplicate a seq, which the wire's seq-bind relies on; the swarm increases event volume and thus the odds this latent gap bites.

Net: "safe" is true for *correctness under the barrier*; "free" is not — the event-emit path is a real serialization cost the plan should measure in G0.

---

## ATTACK 4 — "a role can NEVER reach autonomous dispatch / `claude -p`" (C9.2) — **HOLDS, but on ONE unforgeable-event invariant the plan must encode**

I traced the dispatch chain (**Observed**):
- `claude -p` is spawned only by `runtime/implement.py` (`:30, :318-337` real `subprocess.run`).
- The only auto-dispatch trigger is `drive_dispatchable` → `dispatch_decision`, gated by `_is_dispatchable` (`implement.py:409-423`): the event must be `kind == "resolve"` **AND** `choice == "approve"` AND a build-intent AND `posture(class) == AUTO`.
- `decision_build` IS posture AUTO (`governance.py:27`) — so an *approved* build-intent auto-dispatches with no second gate. The floor therefore rests entirely on: **a role cannot produce a `resolve`/`approve` event.**
- `resolve_surfaced` (the method that emits the `resolve` event, `suite.py:5957, 6016`) is documented **"OPERATOR-only (UI channel) — NOT exposed on the MCP face, so the agent can't self-approve."** (**Observed**.) Roles run inside `_run_swarm`, which the plan keeps off the MCP face. A role's "surface-to-inbox/decisions" destination (C3.2) calls `surface`/`surface_review`, which write `resolved=None` (`governance.py:65`, `suite.py:4274`) — it creates an item awaiting the operator, it does **not** resolve it.

**The emitter set is CLOSED (Observed — the airtight check).** A grep of every `_emit`/`append_event` of a `resolve` event across `runtime/suite.py`, `runtime/governance.py`, `mcp_face/*.py` returns **exactly one** site: `suite.py:6016`, inside `resolve_surfaced` (operator-only, off-MCP). `Inbox.resolve` (`governance.py:153`) sets the `resolved` field but **emits no event** (no `_emit`/`append_event` in its body) and its docstring states it "must NOT be reachable by the agent it gates — kept off the MCP face." `mcp_face/server.py:158` confirms "resolve_surfaced (operator approval) is deliberately NOT exposed on this face." So the *sole* trigger event for `claude -p` dispatch has *one* emitter, and it is operator-only / off-MCP. **The floor is structurally closed today**, not merely sampled.

**So the floor is real** — surfacing ≠ resolving, resolve is operator-only, and the emitter set is closed. **But the plan states it as a structural given; it is actually a build-time invariant that the NEW rule-engine code must not violate.** The precise dependency to encode (and adversarially test, as C9.2 says):
- the rule-engine "surface" destination MUST route through `inbox.surface`/`surface_review` (resolved=None) and MUST NEVER emit a synthetic `kind=resolve, choice=approve` event;
- the cognition driver MUST stay off the MCP face (no role-callable verb reaches `resolve_surfaced`);
- a role's governed AUTO actions (C9.1, "reversible/AUTO via existing POLICY like `decide-for-me`") must be checked: none of the AUTO classes (`inspect/compose/configure/run/write_own_layer`, `governance.py:14`) writes a `resolve` verdict, so they can't indirectly approve a build — **confirmed for the current POLICY**, but this becomes false the instant a future role-reachable AUTO verb emits a resolve event. The adversarial test must assert *no role path emits a `resolve`/`approve` event*, not merely "_run_swarm is off-MCP."

Verdict: floor holds today; the plan should restate C9.2 as the unforgeable-`resolve`-event invariant + a regression test, not as a property that falls out for free.

---

## ATTACK 5 — "rules are deterministic, no model inside a rule, survives FULL DECLARED LOGIC" — **PARTIALLY LANDS: the constraint is asserted, not enforced**

The precedent (`gate.py:26-40`, **Observed**) is a clean pure function of resolved inputs — no time, no random, no order-dependence. C3.1/Q4, however, license "an arbitrary declared expression" ("power over simplicity"). The non-determinism doesn't sneak in through a model call (that's well-fenced — a model only runs inside a role); it sneaks in through **what the rule body is allowed to reference**:

- **Evaluation timing / wave-completion order.** Under parallel dispatch, roles in a wave finish in nondeterministic order. If a "full logic" rule can fire on *partial* results, or read *which* sibling completed first, or branch on a count-so-far, then "re-run the same inputs → identical routing" (C0.2) breaks — the routing depends on a race, not on the resolved VALUES. C0.2 only holds if rules are evaluated **post-barrier, as pure functions of fully-resolved address values** (the gate's discipline). The plan states this as a *constraint to hold* (DECISIONS Q4: "declarative-by-inspection · deterministic · renderable · no hidden model judgment") but **specifies no enforcement** — no whitelist of referenceable inputs, no ban on `now()`/random/order, no "rules see only resolved values" rule in the evaluator design (`cognition/rules.py` is NEW, unbuilt).
- **`now()` / time / randomness** in a "full expression" would directly defeat replay-identity.

Consequence: C0.2 (the spike's determinism check) can pass on a *trivial* rule and still be false for the "full declared logic" the system is actually for. **The gap is the missing enforcement layer**: the rule evaluator must be constrained (referenceable inputs = resolved address values only; no time/random/order/partial-result access; evaluated after the wave barrier) and C0.2 must test a rule that *could* be non-deterministic, not a one-liner. Until that's specified, "deterministic" is a hope, not a property.

---

## ATTACK 6 — "the staged stream feels like one rather than stalling between parts" — **PARTLY LANDS (a `needs-tim`, but with an unbudgeted stall source)**

The plan honestly flags the *feel* as `needs-tim` (C4.4, C6). Two things the plan under-acknowledges as *mechanical* (not just subjective) stall sources:

1. **The inter-part gap is the swarm's wall-clock.** Part N+1 cannot start until the roles it depends on finish AND their addresses resolve. A role decodes at ~100 tok/s (`BENCHMARK_FACTSHEET.md:64`); even a short role at, say, 150 tokens ≈ 1.5s, plus TTFT, plus the JSON-validate/retry loop (`client.py:75-87`, up to 4 retries on malformed output, `03 §E.5`) — a single retrying role can add seconds. So the "between parts" window is **bounded below by the slowest dep role + any retry**, and the operator hears/sees silence across it. The "feels like one" claim depends on that window being short, which the 16-seq/KV-contended reality (Attack 1) makes *worse* under load, not better.
2. **Conditional staging is the real mitigation and the plan knows it** (C4.3, B1's "conditional staging proven mandatory") — a brevity bypass skips the whole machine for one-liners. Good. But for the multi-part case it's *for*, the stall is real and its magnitude is governed by Attack 1's resource reality. The voice path (G6) overlaps synth-of-N with gen-of-N+1, which hides *some* of it — but only if Part N's audio is long enough to cover Part N+1's swarm+gen, which is not guaranteed for terse modes.

Verdict: not a disproof (it's correctly a `needs-tim`), but the plan treats the gap as purely a feel question when it has a hard mechanical floor (slowest dep role + retries) that worsens under the Attack-1 resource pressure. G0 should *measure* the inter-part wall-clock, not just judge the feel.

---

## Secondary findings (smaller, real)

- **`json_object` ≠ `json_schema` (Observed, `transport.py:37`).** The transport sets `response_format: {type: json_object}` — guarantees *valid JSON*, not *schema-conformance*. The factsheet §5 tested the stricter `json_schema` mode. So C1.4's "output_schema enforced" relies on `complete()`'s client-side validate/retry (`client.py:75-87`), not server-side constrained decoding. That's fine, but the "one transport branch away" framing (Research Synthesis) overstates it: getting true server-side schema-constrained output (the factsheet's tested mode) is a real transport change, and the retry-loop is the actual enforcement (adds latency per malformed draw — see Attack 6).
- **`llm.py` is NOT VOLATILE (Observed; no `VOLATILE` attr, vs `model_of_tim.py:11` which sets it).** Confirms C1.5's premise: identical role+config draws collapse at the memo gate (`scheduler.py:96`). The fix (volatile or per-draw id) is correctly net-new. No issue with the claim — just confirming the gap is real and the jury/quorum feature (C2.4) genuinely depends on it.
- **Line-number drift.** Plan cites `chat()` at `suite.py:3333` (real: **3347**), `_chat_context` at `1322` (real: **1336**), `_resolve_context_at` at `1943` (real: **1957**). Not fatal — the symbols exist — but the build follows these citations. Recommend: **verify seams by symbol, not line number.**

---

## Priority of what the plan must fix (highest first)

1. **Attack 1 (resource).** The knee is `max_num_seqs` (16), not 32; KV holds ~one 64K context total; the budget/semaphore must read the real registry values; G0 must measure on the **co-resident 0.49 config at realistic context**, concurrently with a staged main reply. Reframe "32-way swarm" — the real ceiling on the voice config is far below 32 at usable context.
2. **Attack 5 (rule determinism).** Specify and enforce the rule evaluator's referenceable-input whitelist (resolved values only, post-barrier, no time/random/order/partial); make C0.2 test a non-trivial rule.
3. **Attack 4 (`claude -p` floor).** Restate C9.2 as the unforgeable-`resolve`-event invariant + a regression test asserting no role path emits `resolve`/`approve`.
4. **Attack 3 (store).** Atomic-ize `memo_set`/`write_provenance`; budget the per-event fsync cost of `cognition.*`; run the cheap concurrent-in-process store test.
5. **Attack 2 (executor location)** + **Attack 6 (inter-part stall)** — name the shared-vs-driver concurrency seam; measure the inter-part wall-clock in G0.

*Nothing here kills the architecture. The substrate-reuse thesis and the safety floor stand. The build is gated correctly on G0 — but G0 as currently worded would pass without testing the one thing most likely to break it (concurrency × real context × co-residence). Fix the G0 wording and the resource math, enforce rule purity, and the rest is sound.*
