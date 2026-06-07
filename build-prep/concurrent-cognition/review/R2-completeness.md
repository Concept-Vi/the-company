# R2 — Completeness Critique (post-fold)

*Round-2 read-only pass. The question is NOT "is the architecture right" — R1 settled that (sound; spine real; `claude -p` floor holds; reuse spine present). The question is: **after the R1 fold edited the triad in place, what is STILL missing, unverified, contradictory, or unscoped?** I read the three triad docs, `DECISIONS.md`, `R1-FOLD.md`, all five `R1-*.md`, both landscapes, and the repo governance (`AGENTS.md`/`MAP.md`/`STATE.md`). Findings are file:line-anchored to the triad as it stands 2026-06-07. Severity-ordered. Verdict at the end is NOT binary — it says which gate each gap blocks.*

> **One-line verdict:** the fold corrected the *headers and the criteria* but **left several fold-decisions unpropagated into the document bodies a build agent actually reads** — three live "32" assertions and four live `swarm://` resolutions survive, one of which blocks the G0 spike itself. The architecture is build-ready; the *text* is not yet spike-clean. Fix the cheap text reconciliation and the spike (G0) is buildable; fan-out past G0 is blocked on net-new HOW + named drift homes (below).

---

## TIER 0 — Contradictions that SURVIVED the fold (build agent reads bodies, not headers)

The fold (`R1-FOLD.md` F1, F3) made two decisions and wrote them into every doc's **header banner**: *"`run://` throughout (never `swarm://`)"* and *"the budget reads `max_num_seqs`(=16)+KV, never 32."* But the **body text** of all three docs still contradicts those banners. A sub-agent build loop follows the criterion body and the Guide step, not the header caveat — so these are live defects, not cosmetics. This is the single most important R2 finding: **the fold half-landed.**

### T0.1 — `swarm://` survives as a *resolvable address* in four body locations (contradicts the banner, C1.3, G7, DECISIONS, and `address.py`)
- **Criteria C4.2** (line 62): *"later parts resolve **`swarm://`** addresses written by concurrent roles (injection = address-resolution via the existing `_chat_context` path)."* — This is the *exact* sentence R1-FOLD F3 + R1-consistency X1 + R1-seams Seam 2 + R1-flow Flow 1 all flagged as **mechanically wrong twice over**: (a) `swarm` is not in `contracts/address.py` SCHEMES (`run/cas/blob/vec/ui/code`) so it resolves to `None`; (b) the existing `_chat_context`/`_resolve_context_at` path reads operator-notebook strata, not fresh role refs. C1.3 (line 38) was correctly edited to `run://` + "net-new ref-read"; **C4.2 was not.** The two criteria now contradict each other inside the same document.
- **Guide G0 step 3** (line 20): the spike *"resolves its **`swarm://`** address into Part 2."* — see T0.2; this one gates the gate.
- **Guide G5** (line 60): rollups consolidate *"the swarm's own run-records (**`swarm://`** persisted, G-dev-call)."*
- **Synthesis line 15 + line 43**: *"the **`swarm://`** resolution"* and *"`swarm://` lifecycle (persist+GC)"* as a live carried dev-call.
- **Consequence:** a build agent implementing C4.2/G0 either (a) fails to resolve a `swarm://` string, or (b) mints a `swarm` scheme — a `contracts/address.py` edit = **rule-7 CONFIRM** and the precise opposite of the fold's decision and DECISIONS' carried call. *Fix: replace every live/resolvable `swarm://` with `run://<turn>/<role>`; the literature reference (Synthesis line 24, Blackboard) and the dev-call *name* may stay as prose, but every "resolve/persist/written-to a `swarm://` address" must become `run://`.*

### T0.2 — `swarm://` blocks the SPIKE, not just fan-out (the gate is not clean-buildable as written)
Guide G0 is the GATE the whole build is staked on (Criteria line 19–30). Its step 3 tells the agent to resolve a `swarm://` address. Since `swarm` is an unregistered scheme, **the very first buildable artefact contains an unbuildable instruction.** The fold's own header says `run://` — but G0's body was not updated. *This means even G0 fails the "ready to build" bar until the one-word edit lands in C4.2 + Guide G0 step 3 + Guide G5.*

### T0.3 — Three live "32" assertions survive (F1 was *the central failure*; this is the same defect class as T0.1, ranked at least equal)
The fold reframed "32" in the banners, C0.5, C1.2, and the parallelism note — but **left it asserted as fact in three body sentences**, two of which sit directly above their own correction:
- **Synthesis line 39**: *"the swarm's **32-concurrency** lives on this one resident model"* — directly contradicts **line 40 immediately below it** (`max_num_seqs=16`, "real swarm ceiling … well below 16 at usable per-role context"). A self-contradicting adjacent pair.
- **Guide line 14** (governing principle 4): *"one 4B with a KV pool for the main context + **32 short role contexts**."* — states the disproven number as the design's resource premise.
- **Synthesis line 17**: *"a ThreadPoolExecutor of **~32 requests**."*
- **Consequence:** F1 was named "the central failure" by the adversarial review. Leaving "32" live in the design-premise sentences a build agent reads to size the executor re-introduces exactly the failure the fold existed to kill. *Fix: these three must read `max_num_seqs−R` / "the measured ceiling (C0.5)" / "well below 16 at usable context," matching their own banners.*

---

## TIER 1 — Fold-demands NOT reflected in the Criteria (the fold asked; the truth-table didn't fold it in)

### T1.1 — Self-description / drift homes are named for NO net-new registry (R1-FOLD F9 "smaller, real" + R1-consistency G-A)
F9 closes with: *"Self-description/drift homes must be named for every net-new registry (roles, MODEL_CAPABILITIES, edge-kinds)."* R1-consistency G-A widens this to **roles · MODEL_CAPABILITIES · edge-kinds · rule-engine · thought-shapes · activation-contexts · `cognition.*` events** and ties it to a hard law: `tests/drift_acceptance.py` **fails loud** if a registered capability isn't reflected in `MAP.md`'s `<!--REGISTRY:START-->` block (verified present, MAP.md:71, listing node-types/RHM-verbs/modes) via `Suite.refresh_self_description()`/`capabilities()`. **The Criteria never fold this in.** C2.1 says roles "self-register + is queryable" but not that they join `capabilities()`/the MAP registry; G8 never says `MODEL_CAPABILITIES` wires into `capabilities()`; edge-kinds/rules/thought-shapes/activation-contexts have no stated drift home at all. Under law-8 (registry-is-truth, the path-of-least-resistance law that binds the self-coding brain) a capability the authoring prompt can't see invites confabulation. **This is a fold-demand-not-reflected gap with no verification path** — there is no criterion that would go red if a new registry is invisible to drift. *Fix: add to each net-new-registry criterion (C2.1, C8.1, C1.3, C3.x, C4.1, C5.5) "…and joins `capabilities()` + the MAP `REGISTRY` block; `drift_acceptance` asserts it."*

### T1.2 — C4.2 was not reclassified net-new even though F3 reclassified injection
F3 moved injection from reuse→net-new and corrected C1.3. But **C4.2 still describes injection as "address-resolution via the existing `_chat_context` path"** (line 62) — the old reuse framing the fold explicitly retired. Same root as T0.1; flagged separately because it is a *classification* error (reuse vs net-new), not only a scheme typo: a build agent reading C4.2 will look for free reuse and find none.

### T1.3 — `cognition.*` still called an "emit-contract"; not reclassified, no drift home (R1-consistency G-B)
Guide G7 (line 72) still names *"a `cognition.*` **emit-contract**."* R1-consistency G-B established `cognition.*` is **NOT a pinned contract** — event kinds live as runtime string literals (`suite.py:4321` `_emit("decision.intent")`), there is no event-kind shape in `contracts/*.py`, so there is no rule-7 CONFIRM for the event *names*. The fold left the "emit-contract" wording uncorrected. The risk cuts both ways: an agent reading "contract" may **over-gate** it (treat as a CONFIRM) OR **under-document** it (skip the STATE/MAP self-description note an operator-facing SSE surface needs). And — see T1.1 — `cognition.*` needs a named self-description home (runtime-emit + drift/STATE note) like every other net-new surface. *Fix: reclassify Guide G7's "emit-contract" to "runtime emit-strings + self-description (STATE/MAP note), NOT a `contracts/` contract"; add `cognition.*` to the drift-home list.*

### T1.4 — Edge-`kind` CONFIRM gate is in C1.3 but the vault-spec update is half-stated
C1.3 correctly flags "CONFIRM-level contract edit (bump `schema_ver`; default-kind for existing edges; vault-spec update)." But R1-consistency X2 found `Edge` has **no `schema_ver` field to bump** (the version markers live on `Provenance`/`NodeType`, not `Edge`) — so "bump `schema_ver`" is not literally executable on `Edge`. Minor, but the criterion instructs an impossible mechanic. *Fix: C1.3 should say "kind defaults to `data-wire` so existing edges stay valid (Edge has no version marker to bump); update the `build-prep/contracts/` vault spec."*

---

## TIER 2 — Under-specified net-new subsystems (named, no real HOW)

These are net-new per the fold, but the Guide gives them one clause each — not enough HOW for a build agent. Each is a FUNCTION criterion that could pass shallowly.

### T2.1 — G5's three activation triggers: one clause each for three net-new subsystems (F7 + Flow 2)
F7 + Flow 2 establish there is **zero activation substrate** (no `.timer` units, no tick, `background` is a directive string). The fold reclassified G5 as "three net-new subsystems." But Guide G5 (lines 58–61) gives them ~one sentence: *"a scheduler/timer for rollups · an event-hook for sense · an idle-loop for background."* Missing HOW for each: the host mechanism (systemd `.timer`? in-process loop? — `ops/systemd/` has zero timers today), the **`TurnContext`-without-an-utterance** construction (Flow 2: a background trigger needs an activation object that today only exists per-user-turn), and the budget-gate wiring (C1.2's semaphore, itself unbuilt). C5.2–C5.4 are FUNCTION criteria with no Guide HOW deep enough to build against. *This is the largest under-scoped area; correctly sequenced after per-turn (C5.1), but the HOW is a stub.*

### T2.2 — `THOUGHT_SHAPES` schema is named but never specified
Guide G4 (line 52) names "a `THOUGHT_SHAPES` registry (per-mode part templates); `shape_for(mode)`" and C4.1 says "a config table." **Neither specifies the schema** of a thought-shape: what fields a shape declares (part count? per-part grain? which roles each part depends on? the dep-graph between parts? tools-on-final flag?). C4.1's "part grain follows the mode" is the only concrete field. A registry with an unspecified record schema cannot be built to a verifiable bar. *Fix: specify the thought-shape record (the same way C2.1 specifies the role record's 9 fields).*

### T2.3 — Typed-lane / channel destination: no seam cited (R1-consistency G-C)
C3.2 lists five destinations; four have reuse anchors (inject→resolve, chain→role, address→store, surface→`surface_review`/inbox). The fifth — **typed-lane/channel** — has no cited seam in either Criteria or Guide. G-C flags it may touch a contract (CONFIRM) or be net-new infra. It is a bare destination kind with no HOW and no classification. *Fix: name the channel seam or flag it a sub-decision; do not leave it as a word in a list.*

### T2.4 — The jury verdict/quorum evaluator is ~90% unbuilt and under-specified (Flow 3)
C2.4/C1.5 make jury "first-class," and C1.5 correctly leads with the per-draw cache-key (not blanket VOLATILE — F9 fixed this). But Flow 3 showed the volatile fix is *~10%* of the jury flow: the missing 90% is **(a) `draws:N` fan-out issuance, (b) N distinct addressed slots (`run://<turn>/<role>#<draw>` — a sub-address grammar that doesn't exist), (c) varied sampling per draw, (d) the verdict/quorum/vote evaluator.** The Guide (G2/G3) mentions "a verdict rule (quorum/vote)" but specifies neither the draw-addressing grammar nor where the verdict aggregator lives (a rule? a role? `cognition/rules.py`?). C2.4 is verifiable (C1.5's 3-distinct-generations test) but the *aggregation half* has no HOW. *Fix: specify the draw sub-address + name the verdict evaluator's home.*

---

## TIER 3 — Verification-path gaps (a criterion that can pass without proving its intent)

### T3.1 — C0.2 replay-determinism vs C1.5 varied-draws: the test is ambiguous (Flow 1 + Flow 3)
C0.2 wants "re-run identical inputs → identical routing." C1.5 wants varied (temp>0) draws. **These coexist only if C0.2's test freezes the role output and re-runs ONLY the rule** — because rule-determinism is a *rule-layer* property (deterministic GIVEN a role's output), NOT an end-to-end-turn property (the role generation is non-deterministic by design). C0.2's current wording ("re-running identical inputs routes identically") reads as an end-to-end turn replay, which would be **non-deterministic and fail** for any temp>0 role. As written, a build agent could implement a literal turn-replay test that contradicts the jury requirement. *Fix: C0.2 must say "freeze the resolved role outputs; re-run only the rule evaluator → identical routing trace." (F5's "post-barrier, pure function of resolved values" is the right discipline; the C0.2 test wording must match it.)*

### T3.2 — "Where does the swarm run" fork is undecided and governs C1.5's reachability (Flow 3)
Flow 3 surfaced a load-bearing ambiguity the fold did not close: **does the swarm run THROUGH the scheduler (memo-gated, so C1.5's per-draw cache-key bites) or via a direct `run_role()` that bypasses the scheduler AND its memo gate entirely?** Guide G0 step 1 sketches a "minimal `run_role`" (bypasses scheduler → the whole VOLATILE/per-draw discussion is moot for the swarm); Guide G1.5 cites `scheduler.py:96`'s memo gate (assumes the swarm rides the scheduler). C1.5's verification ("ordinary `llm` nodes still memoize") only makes sense on the scheduler path. **This fork is unresolved and silently changes whether C1.5 even applies to the swarm.** *Fix: decide and state — likely `_run_swarm` calls `run_role` directly (off-scheduler, off-MCP per F2/C9.2), in which case C1.5's per-draw key is an APP-graph-jury concern and the swarm gets variation another way (distinct draw-id in the request, not the memo sig).*

### T3.3 — C5.x background/sense have FUNCTION bars but no measurable budget-floor proof
C5.2–C5.4 say background/sense/rollup "fire under a mode's budget" and "don't exceed the floor." But the budget semaphore (C1.2) is unbuilt and there is no criterion that **adversarially proves a background swarm cannot starve the live floor** (the sacred reservation). C9.3 covers fail-loud generally; no criterion targets "a background cast tried to take the reserved R slots and was refused." *Fix: add an adversarial sub-clause to C5.5 (mirroring C9.1's posture-escalation adversarial check).*

---

## TIER 4 — DECISIONS → Criteria coverage (the positive completeness check, on record)

I checked all six binding decisions the task named are reflected in the Criteria. **All six are present** — recording the absence-check positively so it is on the record, not assumed:

| DECISION | Criteria reflection | Status |
|---|---|---|
| Jury/quorum first-class (B4-Q2) | C2.4 + C1.5 | ✅ present (HOW gap: T2.4) |
| All four activation-contexts (B3-Q2) | G5 / C5.1–C5.5 | ✅ present (HOW gap: T2.1) |
| All five destinations (B3-Q4) | C3.2 | ✅ present (seam gap: T2.3) |
| Live view in first build (B4-Q3) | G7 / C7.1–C7.2 | ✅ present |
| Mode-dependent grain (B1-Q1) | C4.1 | ✅ present (schema gap: T2.2) |
| Cloud decoupled (B2-Q3) | C8.3 | ✅ present |
| Roles-can-act governed (B3-Q3) | C9.1 | ✅ present (deterministic-router proof in C9.1 adversarial) |
| `claude -p` floor lead-only | C9.2 (invariant + test) | ✅ present + correctly hardened (F6) |

No DECISION is missing from the Criteria. The gaps are all in HOW/verification depth, not in coverage.

---

## TIER 5 — Smaller / carried (real, low blast-radius)

- **Synthesis line 20 stale line refs** (`suite.py:1322,1461,1943`) survive in the body despite the banner's "locate by symbol; drifted ~+14." Harmless to a symbol-seeking agent, but the Synthesis body still prints the wrong numbers. (R1-reference Tier-2, R1-flow headline.)
- **G6 transitive gating not stated in the Criteria.** R1-seams Seam 7 + Flow 1 established G6 (voice parts) inverts `_voice_stream`'s think→speak structure and is **transitively gated on the Seam-4 shared-core refactor**. The Guide G6 mentions PRESERVE targets but neither doc states "G6 cannot start until C4's `chat_parts` generator exists." The priority order (Criteria line 110) implies it (G6 after G4) but doesn't name the *generator* dependency. Minor sequencing clarity gap.
- **VRAM co-residence accounting** (R1-consistency G-D): the swarm-KV-pool ⨯ resident-4-bit-voice co-residence (the card is already ~0.6 GB over at the marquee config per `ops/AGENTS.md`) is folded into C0.5/C1.2 as "measure," but no criterion states the *voice constitution's* "never load TTS without VRAM headroom" Never-rule applies to the swarm pool. C0.5 measures; it doesn't assert the headroom guard. Low risk (G0 measurement will surface it) but unstated as a guard.
- **`json_object` ≠ `json_schema`** correctly folded (C1.4, F9) — no gap; noted as resolved.
- **`chat_parts` "additive" → "refactor"** correctly folded — Guide line 52 now reads *"a hot-path REFACTOR, not additive (R1-FOLD F4)… extract `chat()`'s body into a shared core."* The old "additive beside `chat()`" framing the fold retired does NOT survive anywhere in the triad (grep-confirmed). Positive check on record; no gap.

---

## Ready-to-build? — the non-binary verdict

**Architecture: sound.** R1 affirmed it; nothing in R2 relitigates it. The spine, the reuse ledger (post-shrink), the `claude -p` floor, and the law-alignment hold.

**G0 spike — NOT clean-buildable as written; cheap to fix.** Blocked only by the **text reconciliation** (T0.1/T0.2 `swarm://`→`run://` in C4.2 + Guide G0 step 3 + Guide G5; T0.3 the three live "32" sentences; T3.1 the C0.2 replay wording; T3.2 the through-scheduler-or-not fork — the last because G0 step 1's `run_role` sketch assumes an answer). These are edits to prose a build agent reads, not new design. **Do these and G0 is buildable.**

**Fan-out past G0 — BLOCKED on net-new HOW + drift homes.** Even with G0 green, the following must land before the corresponding group is buildable to a verifiable bar:
- **Drift homes named** for every net-new registry (T1.1) — else `drift_acceptance` has nothing to assert and law-8 is unguarded. *Blocks G2, G3, G8, C1.3.*
- **THOUGHT_SHAPES schema specified** (T2.2). *Blocks G4.*
- **Jury draw-addressing + verdict evaluator home** (T2.4). *Blocks C2.4's aggregation half.*
- **G5's three triggers given real HOW** (TurnContext-without-utterance, host mechanism, budget gate) (T2.1). *Blocks G5 — correctly sequenced last, but the HOW is currently a stub.*
- **Typed-lane seam named or flagged a sub-decision** (T2.3). *Blocks the fifth destination in C3.2.*

**Build sequence — still right.** The serial-spine (G0→G4 on `suite.py`/`bridge.py`/`scheduler.py`) + 3 disjoint lanes (json_schema transport · `llm` per-draw · canvas-FE — confirmed file-disjoint by R1-seams) + spike-gate **survives the reuse→net-new shrink.** The new net-new mass the fold added (G5's three triggers, the jury aggregator, the activation substrate) lands *inside the serial spine* or *after per-turn works* (C5.x is correctly sequenced last) — NOT as new parallel lanes — so the 3-lane structure is unaffected. The net effect of the fold is: **the spine got longer and the G0 gate matters more** (it is now a measurement gate, not just a feel gate — C0.5). The ordering claim holds; do not re-cut the lanes.

**The meta-finding:** R1's fold was a *correction layer*; it edited the headers and the criteria but **did not fully propagate two of its own headline decisions (F1 "32", F3 `swarm://`) into the document bodies** — and F9's drift-home demand never reached the Criteria at all. The build agent reads bodies and criteria, not the header caveats. **Before the spike: a propagation pass that makes the bodies say what the banners already say**, plus the five HOW/schema specifications above before their groups fan out. That is the gap between "the fold happened" and "the truth-table is true."
