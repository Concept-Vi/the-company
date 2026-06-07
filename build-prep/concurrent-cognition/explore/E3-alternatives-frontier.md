---
type: design
module: build-prep/concurrent-cognition/explore
aliases: ["Alternatives & Frontier — scout", "Concurrent Cognition E3"]
tags: [company, design, concurrent-cognition, frontier, alternatives, aggregation, voice, scout]
status: exploration
relates-to: ["[[00-LANDSCAPE]]", "[[B1-external-architectures]]", "[[R2-resource-math]]", "[[R2-FOLD]]", "[[DECISIONS]]", "[[01-role-registry]]", "[[04-staged-response-queue]]", "[[B4-model-capability-registry]]"]
---

# E3 — Alternatives & Frontier: enriching the design's hard/open spots

> **Scout's job (GENERATIVE, not verification).** Widen the design space at the four hard spots the task names. I bring back **options**, mark each high-value vs speculative with reasoning, and **do not pick** — Tim decides. House style from [[B1-external-architectures|B1]]: every claim sourced or marked **[my inference]**; provisional; maximal-capture (volume is the feature). Written 2026-06-07.

> [!important] What this is NOT
> This is **not** a re-survey of [[B1-external-architectures|B1]] — B1 already mapped MoA / Self-MoA / SoT / Blackboard / Moshi / debate / BSM / LLM-Blender / spec-decode / SLM-agentic. E3's three value-adds, kept disjoint from B1:
> 1. **The registry slot-in MECHANICS** per pattern — the rule-vs-role decomposition that makes each option honour the locked spine ([[DECISIONS|L2]]).
> 2. **The execution-timing HYBRIDS** — speculative roles, prefetch, the prefix-cache play (the spectrum *between* the two recorded endpoints, not the endpoints).
> 3. **Genuinely newer frontier** B1 did not cover — semantic-VAD/turn-detection models, generative verifiers as gate-roles, learned routers, Router-R1.

---

## 0. The framing that makes every option below legal (read first)

The spine is **LOCKED** ([[DECISIONS|L2]]): the core mechanism is **rule-based, deterministic ROUTING/RESOLUTION from registry declarations** — *not* a model judging weak-vs-strong / aggregating by quality. Tim: *"That is the main mechanism that all of this application is aimed at."* So model-aggregation/fusion is **one optional role-type, not the spine.** The task explicitly asks for these as *"optional role-types"* and *"beyond simple routing"* — so exploring them does not fight L2; it fills the slot L2 leaves open.

**The load-bearing classifier for everything in §1 (and the most useful single idea in this file):** every combination pattern decomposes into a **rule part** and a **role part**, by one test —

| The combine-step is… | …therefore it is a | Fits which locked machinery |
|---|---|---|
| **deterministic over resolved values** (majority count, threshold, weighted-sum with *declared* weights, rank-by-numeric-score, pick-max-confidence) | **RULE** | the Batch-5 predicate grammar (boolean/comparison/arithmetic/field/membership over resolved values; declared AST + restricted evaluator; per-rule readiness) — [[DECISIONS]] |
| **model judgment / generation** (synthesise prose from N candidates, NL cross-critique, debate-synthesis, semantic rank) | **ROLE** (a model inside a role) whose *output a rule then routes* | `ROLE_REGISTRY` row + `run_role` (01) + the rule routes its output (L2) |

This is exactly what [[R2-FOLD|R2-FOLD H7]] already states for the jury: *"a jury role's DRAWS are intentionally varied; the verdict over them is deterministic."* Drawing = role(s); verdict = rule (if numeric) or a verdict-role (if it needs judgment). **The deliverable of §1 is doing this decomposition for each named pattern** — that is "how it slots in as registry-declared."

**Already-locked, so framed as variants not proposals** (don't re-discover; anchor):
- **Quorum/jury is first-class core** ([[DECISIONS|Batch 4 Q2]]) — *"any role can be a quorum (run N times, varied, take a verdict). Fixes the volatile-memo collapse."* So weighted-quorum / debate are **variants on an adopted primitive**; §1 explores the *verdict-shape spectrum*, not whether to have one.
- **Per-mode brain config is adopted** ([[R2-FOLD|H1]]: mode selects the brain config; swarm-mode 16K/0.6 vs voice-depth 64K). So §3's "one vs per-mode" is *answered* — §3's net-new is the **tiny dedicated judge/router model** + **speculative decoding as orthogonal**.
- **Overlap-vs-between-parts is a recorded choice** ([[R2-resource-math|§3]]). So §2's value is the **hybrids/spectrum**, not the two endpoints.

---

## 1. Swarm-output → main-stream combination: the optional role-types

> The spine routes by rule. But a rule can route N role-outputs **into a combining role** (or **into a combining rule**). This section enumerates the *combining* role/rule-types worth offering as registry-declared options. Each: what it is · the rule-vs-role split · how it declares · verdict (worth a place / speculative).

### 1.1 Pick / threshold / vote — **pure RULE, no model** (the cheapest combiner; ship first)
- **What:** several roles answer the *same* question (e.g. three `relevance-scorer` draws, or three `check` draws); the combiner is **majority vote** (votable answers) or **threshold/count** (≥2 of 3 say "contradiction" → route to the contradiction lane). Ancestor: Self-Consistency ([[B1-external-architectures|B1 §8a]]).
- **Rule-vs-role split:** **100% rule.** No model in the combine-step — it's `count(votes, "X") >= 2` or `argmax(score)`, dead-centre in the Batch-5 predicate grammar.
- **Declares as:** a quorum role (the N varied draws, Batch-4 primitive) + a **routing rule** over the draws' resolved fields. The rule IS the aggregator. The verdict is provably deterministic (R2-FOLD H7) and renderable (a short edge-label: `≥2/3 → lane`).
- **Verdict: WORTH A PLACE — highest-L2-fidelity, lowest-cost combiner.** No model judgment anywhere, free determinism proof, free renderability. Most "combine 32 outputs" worries dissolve here: you rarely fuse 32 prose blobs; you usually **route on a count over scored fields.** [my inference]

### 1.2 Rank-then-fuse — **RULE rank + ROLE fuse** (the LLM-Blender recipe, decomposed)
- **What:** LLM-Blender ([[B1-external-architectures|B1 §8d]]) = **PairRanker** (rank candidates) + **GenFuser** (generate a fused answer from top-K). B1 flagged "rank-by-quality first, don't concatenate" as its highest-value refinement; here is the *mechanics*.
- **Rule-vs-role split — this is the clean teaching example:** the **rank** is a RULE *if* the rank key is a numeric score each role self-emits (`{answer, confidence}`) → `sort_desc(confidence)[:K]` is pure predicate-grammar. The rank is a ROLE *only if* you want a model to judge quality (then it's a `ranker` role whose output a rule routes). The **fuse** is a ROLE (GenFuser = a model generating from top-K) — almost always the synthesise-part brain itself.
- **Declares as:** roles emit `{value, confidence}`; a **selection rule** keeps top-K by the numeric field (rule); the brain's synthesise-part receives the K survivors as resolved context (the existing injection edge). **No new "aggregator engine" — the rank is a rule, the fuse is the brain.**
- **Why it matters here:** directly answers "beyond simple routing" while staying inside L2 — the *only* model step is the brain composing, which it already does. Self-MoA's quality-sensitivity ([[B1-external-architectures|B1 §4]]) is honoured by the rank-gate dropping weak draws (the `abstain` state).
- **Verdict: WORTH A PLACE as the second combiner-type** (top-K-by-score + inject). The rule does the ranking; gives Tim the "don't concatenate" win without a quality-judging model in the spine.

### 1.3 Generative aggregation (MoA-style) — **ROLE** (the model-fusion option, quarantined)
- **What:** MoA's proposer→aggregator ([[B1-external-architectures|B1 §3]]): a model *reads all N proposals and writes one improved answer.* This is the pattern L2 explicitly says is **not** the spine.
- **Rule-vs-role split:** the aggregator is a **ROLE** (a model judging+generating). A rule routes the N proposals *into* it and routes *its* output onward. So MoA fits — **as a role the rules wire**, never as the routing mechanism.
- **Declares as:** an `aggregator` role (`input_addresses` = the N proposer outputs; `output_schema` = the fused answer); a rule fans the proposers in. Usually the aggregator IS the synthesise-part brain (so "MoA on us" = the brain reading the swarm — which is already the design).
- **Open risk it carries (from B1, unchanged):** can a **4B** aggregator fuse N outputs as well as MoA's 110B aggregator? Unproven; the G0 spike's job. But because L2 demoted aggregation to *optional*, this risk is **no longer central** (DECISIONS L2 says exactly this).
- **Verdict: WORTH A PLACE as an OPTIONAL role-type, clearly labelled non-spine.** Offer it; default off; let a mode opt in. Don't let its prose-fusion framing leak back into "the combiner is a model" — that violates L2.

### 1.4 Blackboard arbitration — **the CONTROL pattern, mostly RULE** (the 40-year ancestor's control half)
- **What:** B1 §6 mapped the blackboard *data* model (KSs post to `run://<turn>/<role>`). The piece B1 left for us is the **control/arbitration**: classic blackboards had a *scheduler* deciding which KS runs next, and Hayes-Roth's BB1 put **control reasoning itself on the blackboard.** Source: [Hayes-Roth, A Blackboard Architecture for Control](https://www.sciencedirect.com/science/article/pii/0004370285900633).
- **Rule-vs-role split:** arbitration ("which posted hypothesis wins / fires next") is a **RULE** when it's priority/confidence/recency over posted fields (predicate grammar) — and the design *already chose this*: the mode pre-selects the cast to **avoid per-step control reasoning** ([[B1-external-architectures|B1 §6 mitigation]]). Frontier extension: a **focus-of-attention rule** = Tim's *budget = attention* made a literal arbitration predicate (fire the highest-confidence posted role first; drop the rest at budget).
- **Declares as:** roles post `{hypothesis, confidence, level}` to addresses; an **arbitration rule** selects/orders by confidence within the mode's slot budget. No arbitration *model*.
- **Verdict: WORTH A PLACE as vocabulary + one arbitration-rule type** (confidence-ordered firing under budget). Low cost (it's a rule), and it hands us 40 years of control-theory naming (focus-of-attention, KS triggering, hypothesis confidence) that maps onto the open forks. Mine the vocabulary; build the one rule.

### 1.5 Debate / critique (single-bounce) — **a 2-node ROLE CHAIN** (not a combiner; a refiner)
- **What:** multi-agent debate ([[B1-external-architectures|B1 §8b]]) and Attention-MoA's NL cross-critique ([[B1-external-architectures|B1 §4]]): roles *critique each other* before the brain composes. B1's lesson: debate needs *rounds* (latency we lack), so **reserve a single bounce for adversarial roles only.**
- **Rule-vs-role split:** the critique is a **ROLE** (the `check`/contradiction-checker reads peers and emits a correction); the *decision to apply the correction* is a **RULE** (if `check.found_contradiction` → route the flagged claim back / annotate). This is a **chain** (role→role edge), already a first-class primitive (02-graph-substrate-reuse).
- **Declares as:** `check` role with `input_addresses` = the other roles' outputs (single pass); a rule routes on its verdict. Attention-MoA's variant: the critique is *natural-language* ("corrective instruction") rather than a scalar — a lighter prompt-level way to get "weigh the good, discount the contradicted." Source: [Attention-MoA arXiv 2601.16596](https://arxiv.org/html/2601.16596v1).
- **Verdict: WORTH A PLACE, but bounded — single-bounce, adversarial roles only.** The locked cast already has `check` (Batch 4 Q1); this is the *mechanism* for it. Multi-round debate: **speculative** (latency cost intra-turn).

### 1.6 Weighted quorum — **a RULE variant of the locked jury** (verdict-shape spectrum)
- **What:** the jury (Batch-4) takes a verdict over N varied draws. The *verdict-shape spectrum*: (a) **unweighted majority** (§1.1); (b) **confidence-weighted** (each draw carries `confidence`; verdict = weighted vote with *declared* weights); (c) **role-weighted** (a `ground` draw counts more than a `connect` draw — weights declared per mode); (d) **veto** (any single `check` "unsafe" overrides the majority — a hard-gate, mirrors the judge's free hard-gates, 04).
- **Rule-vs-role split:** **all four are RULES** — weighted-sum / veto-predicate over resolved fields, dead-centre in the predicate grammar. The only thing net-new vs §1.1 is the *weights are declared registry data* (per-role, per-mode), which is exactly L1 (registry-driven, not hardcoded).
- **Verdict: WORTH A PLACE — it's the jury's verdict-rule, parameterised.** Ship unweighted (§1.1) first; weighted + veto are config rows on the same rule-type. This is *filling in* the adopted Batch-4 primitive, not a new proposal.

### 1.7 Combiner summary — the spectrum, L2-fidelity ranked
| Combiner | Combine-step | Slot-in | L2-fidelity | Verdict |
|---|---|---|---|---|
| Vote / threshold (§1.1) | RULE | quorum + routing-rule | highest (no model) | **default — ship first** |
| Weighted quorum / veto (§1.6) | RULE (declared weights) | jury verdict-rule, parameterised | highest | **worth it — jury fill-in** |
| Rank-then-fuse (§1.2) | RULE rank + ROLE(=brain) fuse | top-K-by-score + inject | high (model only in the brain) | **worth it — 2nd combiner** |
| Blackboard arbitration (§1.4) | RULE (confidence/budget) | arbitration-rule + vocabulary | high | **worth it — 1 rule + naming** |
| Single-bounce critique (§1.5) | ROLE critique + RULE route | role-chain (`check`) | high | **worth it — bounded** |
| Generative aggregation (§1.3) | ROLE (model fusion) | optional `aggregator` role | lower (model judges) — **non-spine** | **offer, default-off, labelled** |
| Multi-round debate | ROLE × rounds | role-chain × N | high but **latency** | **speculative (intra-turn)** |

---

## 2. Overlap-vs-between-parts execution: the spectrum + hybrids

> The two endpoints are *recorded* ([[R2-resource-math|§3]]): **between-parts** (prior part's KV frees → 16-wide, prefix-cache-cheap re-prefill) vs **overlap** (swarm fires while Part-1 still generates with a large base context → 1–5 wide but latency-hidden). E3's value is the **middle**: hybrids that get overlap's latency-hiding *and* between-parts' width.

### 2.1 Speculative roles — start a role *before it's surely needed* (the highest-value hybrid)
- **What:** don't wait for the rule to *decide* a role is needed — **speculatively fire** the likely-needed roles in Part-1's shadow, and let the rule **discard** the ones whose branch didn't win. This is speculative *execution* lifted from CPU branch-prediction to the swarm. (Distinct from speculative *decoding*, §3.3 — that's token-level.)
- **The play:** while Part-1 generates, fire the roles the mode's *most probable* shape names. When the routing rule resolves, keep the winners, abandon the losers (their KV reclaims). Cost = wasted draws on mispredicted branches; benefit = the winning roles are *already done* when Part-2 needs them → overlap's latency with between-parts' readiness.
- **Slot-in (registry-declared):** a role row gains `speculative: true` + the rule that *confirms/discards* it (a routing rule whose miss-branch routes the speculative output to `discard`). Fits L2 — the *decision to keep* is a rule. Mode tunes how many speculative slots (budget = attention, literally — you spend attention on a bet).
- **Verdict: WORTH A PLACE — likely the best latency/width trade.** It's the one hybrid that beats both endpoints when branch-prediction is good (conversational turns are highly predictable). Mark the wasted-draw cost; measure hit-rate in G0. [my inference]

### 2.2 Prefix-cache prefetch — **warm the shared prefix, not the roles** (near-free, do always)
- **What:** [[R2-resource-math|§5]] already names the lever: with prefix caching, a cached base context gives **40–110ms TTFT** vs ~700ms cold re-prefill of 16K. The *prefetch* move: at turn start, **issue a cheap warm-up request that establishes the shared system+context prefix** so every role-draw and every part *hits the cache* instead of re-prefilling.
- **The design requirement it implies (already a hard rule in §5):** keep the main base context **stable / append-only** so injection adds only *new* tokens to re-prefill, never invalidating the cached prefix. Roles should **share a common prompt prefix** (same system head) so the swarm's 16 draws share one cached prefix and each pays only for its short role-specific tail. [my inference, grounded in §5]
- **Slot-in:** not a role-type — a **transport/runner discipline** (a `shared_prefix` the runner front-loads; roles declare their *tail* template only). Belongs in the swarm-executor build (01/04), not the registry schema.
- **Verdict: WORTH A PLACE — do it always, it's near-free** and it's the mechanism that makes the between-parts re-prefill cost vanish. The whole latency story in §5 depends on it.

### 2.3 Staggered / wave execution — **roles in dependency waves, not one flat fan-out**
- **What:** not all roles fire at t0. Roles with no deps fire in wave-1 (in Part-1's shadow); roles that *depend on* wave-1 outputs (chains, §1.5) fire in wave-2 (between parts). This is the BSM branch→solve→merge ([[B1-external-architectures|B1 §8c]]) made *temporal* and it falls out of the existing reactive scheduler ("fires-when-deps-resolve").
- **Slot-in:** **free** — it's the scheduler's native behaviour applied intra-turn (04). The registry already carries `deps`; waves emerge. The only choice is whether wave-2 overlaps Part-1's *tail* or waits for Part-2 — a runner timing knob, mode-tuned.
- **Verdict: WORTH A PLACE — it's emergent, not net-new.** Name it so the spectrum is explicit: turn execution is *waves of (overlap | between)*, per-role, not a single global mode.

### 2.4 The honest spectrum (per-role, not per-turn)
The real finding: **overlap-vs-between is a per-ROLE choice, not a per-TURN switch.** A turn can run *some* roles in overlap (the predictable, short, no-dep ones — §2.1) and *others* between-parts (the wide, dependent, or large-context ones — §2.3), with a warmed shared prefix making both cheap (§2.2). Mode + the slot budget tune the mix. This is richer than the two recorded endpoints and costs nothing structurally — it's the scheduler + a per-role `speculative`/`timing` hint. [my inference]

---

## 3. Swarm-brain config strategy: judge model + speculative decoding

> [[R2-FOLD|H1]] already adopted **mode-selects-the-brain-config** (swarm-mode 16K/0.6 vs voice-depth 64K). So §3's net-new is two things H1 didn't settle: a **tiny dedicated judge/router model** and **speculative decoding as an orthogonal speedup.**

### 3.1 A tiny dedicated judge/router model — **the third residency tier, made literal**
- **What:** [[01-role-registry|01 D2]] tiers roles by residency: (a) brain-shared (zero VRAM), (b) co-resident small model, (c) on-demand. The frontier option: a **sub-1B dedicated model** held warm purely for the *fast deterministic-ish decisions* — the brevity judge (04c), the finished-thought judge, intent-classification, the router (§3.2). The `small-pair` combo already proves **2B@0.45 + 0.8B@0.30 co-reside** ([[B4-model-capability-registry|B4 A3]]) — so a 0.8B judge alongside the 4B brain is *measured-feasible*, not hypothetical.
- **Why a separate tiny model (not the brain, not the 4B swarm):** the judge/router calls are *hot-path, high-frequency, low-complexity* — exactly NVIDIA's SLM-agentic sweet spot ([[B1-external-architectures|B1 §8f]]: "specialized tasks repetitively, little variation"). Putting them on a 0.8B frees the 4B's KV pool for swarm width (the [[R2-resource-math|§2]] binding constraint) and avoids the brain-contention the [[04-staged-response-queue|04 open-Q1]] warns about.
- **Slot-in (registry-declared):** purely config — a role's `recommended_model` binds the 0.8B; the model is a registered service in `services.json` (B4); `MODEL_CAPABILITIES` (B4 net-new) records "judge-suitable, no-think, fast." **No code change** — it's `resolve_role` precedence (01 A2). Residency is the resource-manager's call (B4 A2).
- **Verdict: WORTH A PLACE as an OPTION, measured before binding** (same discipline as the judge's measured pick). The win: it protects swarm width. The cost: a 2nd resident model + a 2nd thing to keep warm. Tie it to the §3.4 decision; default could be brain-shared until measurement shows the contention. [my inference]

### 3.2 Learned router as a role — **RouteLLM / Router-R1** (route-to-model, by rule or by tiny model)
- **What:** the field has matured "which model handles this" into a discipline. **RouteLLM** (Ong et al, 2025) trains a router to send queries to strong-vs-weak models; **A Unified Approach to Routing and Cascading** combines routing + cascade; **Router-R1** (NeurIPS 2025) makes the *router itself an LLM* that interleaves routing + aggregation over multiple rounds. Sources: [Dynamic Model Routing & Cascading (arXiv 2603.04445)](https://arxiv.org/html/2603.04445v1) · [RouteLLM/cascades overview](https://tianpan.co/blog/2025-11-03-llm-routing-model-cascades) · [Unified Routing+Cascading (OpenReview AAl89VNNy1)](https://openreview.net/forum?id=AAl89VNNy1) · [Router-R1 (NeurIPS 2025)](https://neurips.cc/virtual/2025/poster/119214).
- **Maps to us — and the L2 fit is the interesting part:** Tim's L2 *is already a router* — "declared rules decide what happens next." The frontier router-frameworks are the **learned** version of that. The clean reconciliation: **the spine router stays a declared rule** (L2, deterministic, renderable); a learned router is **one optional role-type** that *emits a routing suggestion the rule then honours or overrides.* Router-R1's "router-as-LLM-that-aggregates" is exactly §1.3's generative-aggregator-as-role — same quarantine.
- **Cascade specifically:** the model-cascade pattern (try the cheap model; escalate to the expensive one only if a confidence-gate fails) is a **RULE** (`if cheap.confidence < θ → route to expensive`) — pure predicate grammar, and a natural fit for the resident-4B-vs-cloud-brain choice ([[DECISIONS|Batch 2 Q3]]: cloud is an optional brain). 
- **Verdict:** **Cascade-by-confidence-rule: WORTH A PLACE** (it's a rule, it operationalises the resident-vs-cloud decision). **Learned router model: speculative** — only if a declared rule proves insufficient; and even then it's a *suggesting role*, never the spine.

### 3.3 Speculative decoding — **orthogonal token-level speedup** (turn it on, it compounds)
- **What:** [[B1-external-architectures|B1 §8e]] flagged it as a *boundary case* (not composition) and noted vLLM supports it natively. E3's add: it is **orthogonal and compounding** — a draft model proposes tokens, the 4B verifies in parallel, identical output distribution, ~1.5–2× faster decode *per role-run and per part.* That directly shrinks the [[R2-resource-math|§5]] inter-part wall-clock (decode is ~100 tok/s steady — spec-decode lifts that).
- **Slot-in:** a **service/config flag** in `services.json` (vLLM `--speculative-*` args via `serveconfig.args_for`, B4 A1) + a `MODEL_CAPABILITIES` note. **Not a role-type, not a rule** — it's a serve-time knob, invisible to the cognition layer. Costs a little VRAM for the draft model (competes with swarm width — measure).
- **Verdict: WORTH A PLACE as a measured serve-flag.** Compounds with concurrency (§2) and the swarm-mode config (H1). The VRAM cost of the draft model vs the throughput gain is the trade to measure in G0. [my inference]

### 3.4 The config-strategy spectrum (what H1 left open)
| Option | What | Slot-in | Verdict |
|---|---|---|---|
| One leaner swarm-brain (H1) | 16K/0.6 mode-selected config | adopted | **locked (H1)** |
| Per-mode configs (H1) | voice-depth 64K vs swarm 16K | adopted | **locked (H1)** |
| Tiny dedicated judge/router (§3.1) | 0.8B for hot-path decisions | `recommended_model` + service + caps | **option, measure first** |
| Cascade-by-confidence (§3.2) | cheap→escalate, rule-gated | a routing RULE | **worth it (it's a rule)** |
| Learned router model (§3.2) | RouteLLM/Router-R1 style | suggesting role, rule honours | **speculative** |
| Speculative decoding (§3.3) | draft+verify, ~2× decode | serve-flag + caps note | **worth it, measure VRAM** |

---

## 4. Frontier patterns B1 didn't cover (genuinely net-new)

### 4.1 Semantic VAD / turn-detection models — **a SENSE-role, upgrade for the finished-thought judge**
- **What:** the 2025–26 production voice frontier moved past energy-VAD (silence-threshold) to **semantic turn-detection** — a small model that decides *"has the speaker finished a thought?"* from *meaning*, not pause length, killing the "interrupted mid-thought on a short pause" failure. AssemblyAI's Universal-Streaming, Inworld's Semantic VAD, OpenAI's Realtime "semantic_vad" turn-detection mode. Sources: [AssemblyAI turn detection](https://www.assemblyai.com/blog/turn-detection-endpointing-voice-agent) · [Inworld Semantic VAD](https://inworld.ai/resources/what-is-semantic-vad) · [OpenAI Realtime VAD](https://developers.openai.com/api/docs/guides/realtime-vad).
- **Maps to us — strikingly direct:** the Company **already has a finished-thought judge** ([[01-role-registry|01 A5]]: `is_finished_thought`, substring-matches FINISHED|MORE on a VAD pause). That judge *is* a primitive semantic turn-detector. The frontier says: this should be a **first-class SENSE-role** that fires on the audio-stream activation-context ([[DECISIONS|Batch 3 Q2]]: sense-triggered cognition is in scope), emitting `{turn_complete: bool, confidence}` — and a **rule** routes on it (confidence-gated: high → fire the turn; low → keep listening). This is Moshi's "inner monologue beat-ahead" ([[B1-external-architectures|B1 §7b]]) reframed as a *cascade-friendly sense-role* we can actually inject into.
- **Slot-in:** the judge role, generalised — `output_schema={turn_complete, confidence}`, `trigger.event="vad_pause"`, a routing rule on confidence. Reuses the *exact* existing machinery (01); the upgrade is the schema + the rule replacing the substring match.
- **Verdict: WORTH A PLACE — it's an upgrade to an EXISTING role, near-free, high conversational-feel payoff.** It also makes barge-in (B1 §7b's reconciliation) a first-class sense event that re-fires the swarm. [my inference]

### 4.2 Generative verifiers / process-reward models as a **gate-ROLE**
- **What:** the reward-modelling frontier showed **generative verifiers (GenRM)** — a model that *verifies* an answer by next-token prediction — outperform discriminative verifiers and LLM-as-a-judge (Best-of-N: 5%→45.3% reported). **Process-reward models (ThinkPRM)** verify *each step.* Critically: there's a **known failure** — "one token to fool LLM-as-a-judge" — so verifiers need robustness. Sources: [Generative Verifiers (OpenReview Ccwp4tFEtE)](https://openreview.net/forum?id=Ccwp4tFEtE) · [ThinkPRM](https://medium.com/@techsachin/thinkprm-generative-process-reward-model-for-solution-verification-via-long-cot-reasoning-2016f1e1387d) · [One Token to Fool LLM-as-a-Judge (arXiv 2507.08794)](https://arxiv.org/html/2507.08794v1).
- **Maps to us:** this is the *quality-gate* Self-MoA's finding demands ([[B1-external-architectures|B1 §4]]: drop weak injections). It's the `abstain` state's mechanism — a **verifier role** scores a role-output; a **rule** drops it below threshold. The GenRM-beats-LLM-judge result says: if you *do* want a quality gate, a trained generative verifier beats an ad-hoc judge prompt. The "one token to fool" result is the **caution**: a verifier role can be gamed → keep the *decision* in a deterministic rule over the verifier's score (L2 protects us here — the verifier *scores*, the rule *decides*).
- **Slot-in:** a `verifier` role (`input_addresses`=a role's output; `output_schema={score, valid}`); a routing rule drops/keeps on the score (the `abstain` state, B1 §4). Optional, mode-selected.
- **Verdict: WORTH A PLACE as an optional gate-role** — it's the principled form of the abstain-gate B1 §4 called the highest-value refinement. Speculative on *which* verifier (a prompt-judge is the cheap start; a trained GenRM is the upgrade). The L2 split (verifier scores, rule decides) is what makes it safe against the "one-token-fool" attack. [my inference]

### 4.3 Full-duplex / barge-in as a swarm re-trigger (the Moshi reconciliation, made buildable)
- **What:** B1 §7b proposed making the TTS edge Moshi-like (interruptible). E3's add: the *mechanism* — a barge-in (user speaks during the brain's part) is a **sense event** (§4.1 detects it) that **routes (rule) to: cancel the current part's TTS + re-fire the swarm against the new input.** The existing `_voice_stream` already has client-disconnect cancellation ([[04-staged-response-queue|04]] `client_gone()`); barge-in is the same cancel, triggered by speech instead of disconnect.
- **Slot-in:** no new model — a sense-role (§4.1) + a routing rule (`if user_speaking_during_part → cancel + re-fire`). Reuses the cancel path.
- **Verdict: WORTH A PLACE — the buildable form of B1's "make TTS interruptible."** It's a rule over a sense-role, fully L2-native. [my inference]

### 4.4 Process-level streaming verification (speculative)
- **What:** ThinkPRM verifies *each step*; applied intra-turn, a verifier could check *each part* as it streams (does Part-2 contradict Part-1?). 
- **Verdict: SPECULATIVE** — interesting (a per-part `check` chain, §1.5) but the latency of verifying mid-stream likely doesn't pay intra-turn. Park it; it's a between-turns / rollup-activation-context candidate ([[DECISIONS|Batch 3 Q2]]).

---

## 5. Scout's closing read (the non-obvious takeaways)

1. **The single most useful idea here is the rule-vs-role classifier (§0).** It turns "what aggregation patterns do we offer" from a model-quality question into a *grammar* question: most combiners are **rules** (vote/threshold/weighted/rank-by-score/cascade/arbitration) and only a few are **roles** (generative-aggregator, NL-critique, learned-router) — and even those are roles the *rules wire*, never the spine. This is what keeps every option honouring L2. [my inference]
2. **§1.1 (vote/threshold, pure rule) is the highest-L2-fidelity, lowest-cost combiner** — free determinism + renderability. Rank-then-fuse (§1.2, rule-rank + brain-fuse) is the next-lowest-cost. Generative aggregation (§1.3) is offered but quarantined as non-spine.
3. **Overlap-vs-between is a per-ROLE choice, not a per-TURN switch (§2.4)** — speculative roles (§2.1) + a warmed shared prefix (§2.2) + emergent waves (§2.3) get both endpoints' wins at near-zero structural cost.
4. **A tiny 0.8B judge/router (§3.1) protects swarm width** (the [[R2-resource-math|§2]] binding constraint) and is *measured-feasible* via the `small-pair` combo — but measure before binding.
5. **The freshest, highest-payoff frontier B1 missed is semantic turn-detection (§4.1)** — it's an *upgrade to an existing role* (the finished-thought judge), it makes barge-in first-class (§4.3), and it's pure rule-over-sense-role. Generative verifiers (§4.2) give the principled `abstain`-gate, with the L2 split (verifier scores, rule decides) defending against the known "one-token-fool" attack.

*Everything above is an OPTION, marked worth-it or speculative with reasoning. Tim picks. The decisions stay open.*

---

## Sources (E3-specific; B1's are not repeated)
- AssemblyAI — turn detection / semantic endpointing: https://www.assemblyai.com/blog/turn-detection-endpointing-voice-agent
- Inworld — What is Semantic VAD: https://inworld.ai/resources/what-is-semantic-vad
- OpenAI Realtime VAD (semantic_vad): https://developers.openai.com/api/docs/guides/realtime-vad
- Dynamic Model Routing and Cascading (arXiv 2603.04445): https://arxiv.org/html/2603.04445v1
- LLM Routing & Model Cascades overview: https://tianpan.co/blog/2025-11-03-llm-routing-model-cascades
- A Unified Approach to Routing and Cascading (OpenReview AAl89VNNy1): https://openreview.net/forum?id=AAl89VNNy1
- Router-R1 (NeurIPS 2025): https://neurips.cc/virtual/2025/poster/119214
- Generative Verifiers: Reward Modeling as Next-Token Prediction (OpenReview Ccwp4tFEtE): https://openreview.net/forum?id=Ccwp4tFEtE
- ThinkPRM — generative Process Reward Model: https://medium.com/@techsachin/thinkprm-generative-process-reward-model-for-solution-verification-via-long-cot-reasoning-2016f1e1387d
- One Token to Fool LLM-as-a-Judge (arXiv 2507.08794): https://arxiv.org/html/2507.08794v1
- Hayes-Roth, A Blackboard Architecture for Control (ScienceDirect): https://www.sciencedirect.com/science/article/pii/0004370285900633
- Attention-MoA (NL cross-critique) (arXiv 2601.16596): https://arxiv.org/html/2601.16596v1
</content>
</invoke>
