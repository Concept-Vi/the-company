---
type: design
module: build-prep/concurrent-cognition/explore
series: concurrent-cognition-explore
seq: "E4"
aliases: ["Concurrent Cognition — Unknowns & Futures", "E4 — The Scout for Unknown-Unknowns", "What the conception is missing + what it becomes at scale"]
tags: [company, design, concurrent-cognition, collective-cognition, unknown-unknowns, second-order, scout, futures, risk]
status: open
relates-to: ["[[Concurrent Cognition — Research Landscape (aggregated)]]", "[[B3 — Broader Applications of the Concurrent-Cognition Mechanism]]", "[[Concurrent Cognition — Completion Criteria]]", "[[DECISIONS]]", "[[R1-FOLD]]", "[[R2-FOLD]]", "[[project-collective-cognition]]", "[[project-introspective-data-building]]", "[[project-rhm-v1-state]]", "[[feedback-altitude-transformation-layer]]", "[[feedback-autonomous-spawn-lead-only]]", "[[feedback-render-for-cognition]]", "[[project-the-company]]", "[[project-company-one-entity]]"]
---

# E4 — The Scout for Unknown-Unknowns + Second-Order Futures

> **Status: open / provisional / discovery-scout.** This is the *exploration* layer, sibling to the codebase-reuse landscape (`../00-LANDSCAPE.md`), the broader landscape (`../broader/00-BROADER-LANDSCAPE.md`), and the two review rounds (`../review/R1-FOLD.md`, `R2-FOLD.md`). Those four bodies of work are excellent and *thorough on their own axes* — B3 mapped the application space; R1/R2 hardened the engineering (resources, determinism, the safety floor). **This doc is deliberately NOT a recap of any of them.** Its job is the thing each of those frames could not see from inside itself: what the conception is *missing*, what it *becomes* at scale, where it goes *wrong* at scale, and the single biggest latent opportunity nobody has named. The discriminator for every section is **novelty relative to B3 + R1/R2** — if it merely re-states the application map or the resource fold, it has failed.
>
> **Epistemic tags (repo rule, B3's model):** **Observed** = read in `~/company` code or the triad/review docs. **Designed** = an intended capability, not built. **Open** = decide with Tim. This doc is forward-looking, so **almost everything is Designed/Open** — I say so per claim, and I ground each future in a *specific mechanism property* (e.g. "because cognition is addressed data, X"), never free futurism.

---

## 0 · The frames each prior body could not see past (so "missing" means something exact)

The value of a scout is naming the *frame* a thorough analysis sat inside, then stepping out of it. Four frames produced the four blind spots this doc fills:

| Prior body | Its frame (what it did well) | What the frame structurally couldn't see |
|---|---|---|
| **B3 — applications** | "where ELSE does the mechanism unlock something" — one circuit pointed at 15 fields | The *recursion onto the cognition's own definition* (rollups tune telemetry, never the casts/rules/budgets that ARE the thinking); the *epistemic* properties of the swarm (it stayed on unlock-magnitude, never on correlated-error); the *identity/continuity* substrate under the roles |
| **R1/R2 — review** | break the load-bearing claims against the live code — resources, determinism, the `claude -p` floor | The *engineering* axis only. Nobody attacked the **epistemic** axis — whether 32 roles on one 4B are 32 *independent* judgements or 32 *correlated* ones. No review asked "is a jury of clones a jury?" |
| **The triad — build** | a buildable, spike-gated, verify-by-use plan | Turn-scoped + background-between-turns. No *live working-memory that persists as cognition across turns/sessions*. No story for what happens to identity when the resident model is swapped |
| **Collective-cognition note** | the layered-cognition spine (conscious=cloud, subconscious=local swarm, budget=attention) | *Where the twin lives in the layering* (role? layer? budget-allocator?); *automaticity* is gestured at ("recurring resolutions register as faculties") but nothing wires the loop that promotes them |

The five findings below each step out of one of these frames. They are ordered by what a scout owes Tim most: the sharpest unseen *risk* first, the biggest unnamed *opportunity* second, then the structural *absences*, then the remaining scale-failure modes.

---

## 1 · THE sharpest unknown-unknown — epistemic monoculture (the risk B3 AND the adversary both missed)

**Designed/Open. This is the highest-value finding in the doc.** Both prior frames missed it because each was looking elsewhere: B3 at unlock-magnitude, R1/R2 at engineering. Nobody attacked the *epistemic* axis.

**The fact, restated as a risk.** B1/Self-MoA was cited as **vindication** — one-model-many-draws beats mixing models on quality (`../broader/B1-external-architectures.md`; Synthesis line 24). That is true for *quality*. But the same fact, read at scale, is a **risk**: 32 roles fired on the ONE resident 4B are **32 correlated samples from one distribution**. They share the 4B's training, its blindspots, its systematic errors, its refusals, its hallucination tendencies. A jury of clones is not a jury. When the rule-based fan-in / verdict-evaluator (C1.5, C2.4, the L2 routing spine) reduces those correlated outputs to a route or a verdict, it **launders correlated error into apparent consensus** — "the swarm agreed," "the quorum was unanimous" — when the agreement is just the same model agreeing with itself five times.

**Why this is specifically dangerous HERE (grounded in the mechanism, not generic).**
- **Observed:** C2.4/C1.5 make a jury vary *seed/temperature per draw* (DECISIONS Batch 4 Q2; Criteria C1.5). That samples **decoding variance**, not **independent error**. Temperature spreads the same model's probability mass; it does not give you a second model's perspective. So the confidence-signal the twin-jury (B3-G) is supposed to produce — "consensus = high confidence, spread = ask Tim" — is **systematically overconfident**: the model can be confidently, consensually wrong, and the spread will be small precisely on the things it is uniformly biased about.
- **Observed tension with Self-MoA:** the obvious fix (mix in a second model for independence) is the exact move Self-MoA says *lowers* quality. So this is a genuine, unresolved **design tension**, not a solved problem: diversity-for-independence ⟂ Self-MoA's "don't mix models." The conception currently inherits Self-MoA's conclusion *as if it had no cost at the confidence layer*. It has a cost there.
- **Compounding at scale:** as the swarm's outputs feed rollups (B3-F) which feed the twin (B3-G) which seeds future casts (see §3), a 4B blindspot doesn't stay contained — it **propagates and amplifies through the introspective loop**. The system's self-knowledge becomes a high-resolution map of its own monoculture.

**What the conception should carry (Designed/Open — surface to Tim, don't silently add):**
1. **Disagreement is signal; engineered disagreement is better signal.** A jury whose draws differ only by temperature measures the wrong thing. Options to put to Tim: (a) accept the limit and *label* jury-confidence as "intra-model agreement, not independent corroboration" so it is never read as ground truth (the honest-coverage discipline from introspective-data-building, applied to cognition); (b) get independence cheaply WITHOUT a second base model — *prompt-induced* perspective diversity (a skeptic role, a steelman role, a contrarian role — distinct *prompts*, same model, so it is still "one model many roles" but the roles are engineered to disagree); (c) reserve a *different* model for the verdict/critic layer only (a cloud model judges the local swarm — uses the already-decoupled cloud-brain, DECISIONS Batch 2 Q3 — so the judge is not a clone of the judged).
2. **A monoculture-detector role** (Designed): a cheap analyst over a wave's outputs that flags "these N agreed because they are the same model, not because the answer is robust" — measurable as low output-entropy across draws that *should* have varied. This is the epistemic analog of the resource-measurement gate C0.5: measure the thing most likely to silently break.

**This is the doc's sharpest yield because it is invisible from every prior frame and it bites exactly where the Company stakes its credibility — the twin's predictive confidence and the swarm's "consensus."**

---

## 2 · The biggest latent opportunity nobody named — the cognition self-tuning loop

**Designed/Open. The biggest opportunity AND the deepest drift risk — that duality is the point.**

B3-F closes the introspective-rollup loop onto **telemetry and knowledge** (distributions, gotchas, the manifest). It is celebrated as the loop that "closes" — and it does, for *measurement*. But it **never closes the loop onto the registries that DEFINE the cognition** — the casts, the rules, the budgets, the thought-shapes. That is the deeper recursion, and naming it is the doc's biggest forward yield.

**The named recursion vs the unnamed one.**
- **Already designed (B5, L):** a Company that self-*builds its code* — the swarm coordinates its own construction (bounded by the `claude -p` floor). This is the recursion everyone has been pointing at.
- **Unnamed (this doc):** a Company that self-*tunes its own thinking*. The rollup swarm reads the swarm's own run-records and **proposes changes to the cognition registries**:
  - *retire a misfiring rule* — "rule R fired 200 times, its route was overridden by the operator 90% of the time → propose retiring/rewriting it";
  - *promote a recurring resolution to a faculty* — this is the **automaticity** the collective-cognition note gestures at ("recurring resolutions register as new faculties") but which *nothing in the triad wires*. The loop that detects "this resolve→work pattern recurred 40 times" and proposes registering it as a cheap declared faculty is the literal mechanism of a system getting *faster at thinking the things it thinks often* — the cognitive analog of a path worn into grass;
  - *reweight a cast* — "in `listening` mode the `check` role contributed to the final reply 3% of the time → propose dropping it from that cast / lowering its budget";
  - *re-bind a model* — "role X's outputs fail schema-validation 30% on the 4B → propose binding it to a model with `json_schema` provides" (rides the G8 capability join).

**Why this is grounded, not futurism (mechanism property):** *because the casts, rules, budgets, and shapes are all registry data (L1) and the swarm self-instruments (introspective-data law), the inputs a tuning-proposer needs already exist the moment the build ships.* The rollup swarm reading run-records is B3-F; pointing those analysts at the *cognition registries themselves* rather than at telemetry is a small extension of an already-planned piece. The opportunity is nearly free *given the mechanism* — that is exactly why it is the highest-leverage unnamed thing.

**The governance answer already exists by analogy (this is why it is safe to name as an opportunity, not just a hazard):** the self-coding subsystem (RHM v1) is **propose-not-apply, build-gated, surfaced for review, git-reversible** (`project-rhm-v1-state`). The cognition self-tuner inherits that exact discipline: a tuning-proposer is a *role* (a worker), so by the §1-of-B3-R2 floor it **can propose a registry change but can never apply one** — the change rides the normal review/commit path (DECISIONS Batch 4 Q4: rules ride the normal change discipline). So the safe form is: *the system proposes how to think better; Tim (or the supervised lead) approves the change to how it thinks.*

**The duality (the scout's honesty):** this is simultaneously the deepest *drift risk* in the whole conception. A system that edits the registries that define its own cognition, fed by rollups that are themselves products of that cognition, is a closed feedback loop that can **drift coherently** — optimize toward its own measurements, narrow its own cast toward what it already does well, prune the very roles (the contrarian, the checker) that would have caught the drift. The monoculture of §1 + the self-tuning of §2 *compose into each other*: a monocultural swarm that tunes itself toward its monoculture's strengths. **The mitigation is structural and already-Tim's-pattern:** propose-not-apply keeps a human in the loop on every change to *how it thinks*, exactly as the self-coding gate keeps one on every change to *what it runs*. The opportunity is real; the guardrail is the same guardrail Tim already built once.

---

## 3 · Structural absences in the design (prompt 2 — the safe, enumerable ground)

Three things the whole design simply does not contain. Each is Designed/Open; each is grounded in a specific gap between the triad and the collective-cognition note.

### 3a · Where the twin lives in the layering — the unanswered identity question
**Designed/Open.** The collective-cognition note says: conscious = cloud brain, subconscious = the local swarm, senses = embeddings, identity = *emergent* (grown by the write-half). B3-C and B3-G *touch* the twin (read its own trace; jury its predictions) but neither asks the structural question: **is the model-of-Tim a role, a layer, or the budget-allocator?** The triad never places it. This matters because the twin should be **bidirectionally coupled** to the cast, and neither direction is wired:
- *Twin → cast (seeding):* roles should reason "as-Tim-would-want" — the twin should bias what the `relevance-scorer` scores as relevant, what the `tone-shaper` shapes toward, what the altitude-translator (B3-I) translates *to*. Today roles get a static prompt; nothing injects the twin's learned preferences into the role prompts. *Mechanism property: because role prompts are registry templates and the twin is addressed data, the twin's preferences could resolve into role prompts the same way any context resolves — but this edge is not declared.*
- *Cast → twin (growing):* the swarm's run-records are exactly the gold-grade behavioural corpus the twin is starving for (`project-rhm-v1-state`: "the twin's predictive strength is cold-start, corpus-dependent"). **The swarm IS a corpus generator for the twin** — every routed decision, every operator-override of a route, is a labelled training signal. This is unnamed and high-value: the concurrent-cognition build, by running, *feeds the very corpus that the RHM's defining feature is blocked on.*
- *The placement question itself (Open):* my read is the twin is best modelled as a **cross-cutting bias-source that resolves into other roles' contexts** (a layer-property, not a role and not the allocator) — but this is precisely the kind of identity-architecture call to make WITH Tim, not silently. Flag it.

### 3b · No live working-memory — cognition is turn-scoped, not continuous
**Designed/Open.** "Budget = attention / working-memory" (collective-cognition, reframe 1) *implies a persistent working-set*. But the build is turn-scoped (per-turn cognition) + background-between-turns. There is **no live working-memory that persists AS COGNITION across turns and sessions** — distinct from *stored* memory (the substrate) and from *background consolidation* (B3-B). The gap, concretely: when turn N+1 fires its swarm, the roles start cold; the previous turn's resolved field is gone except as whatever got persisted to the store and re-resolved. A human in a conversation does not re-derive the whole context every sentence — there is a *held* working set that decays slowly. *Mechanism property: because `run://<turn>/<role>` is addressed and per-turn, there is no `working://session` address that holds a slowly-decaying cross-turn cognitive state.* The absence shows up as: the system feeling like it "forgets what it was just thinking about" between turns even within one conversation. Designed answer to put to Tim: a session-scoped working-memory address-space with a decay/eviction policy (the literal "awake subconscious / VRAM working-set = attention" idea, made into a data structure that lives between turns, not just between model-loads).

### 3c · Roles cannot propose new roles — no registry self-extension
**Designed/Open.** The casts are file-discovered registry data (C2.1) — adding a role is adding a file. But *who adds the file?* Today: Tim or the lead. There is no path for the cognition to **propose a new role** — the self-coding analog for the *cast* rather than for *code*. This is the natural completion of §2's self-tuning: not just "retire/reweight existing roles" but "this recurring gap (turns where no role covered X) suggests a new role with this prompt/schema." *Mechanism property: because a role is a declared file and the self-coding subsystem already proves "the brain authors a declarative panel def, generic renderer, git-reversible" (`project-rhm-v1-state`), a brain-authored role-file is the same shape — propose-not-apply, review, commit.* Absent today; a clean future once §2 exists. Bounded identically (a role proposes; the lead commits).

---

## 4 · Where it goes wrong at scale (prompt 3 — two failure modes the engineering review didn't reach)

R1/R2 covered the *engineering* scale-failures (KV thrash, fsync flood, determinism races, the dispatch floor) exhaustively. These two are different in kind — they are failures of *perception* and *continuity*, not of throughput.

### 4a · Opacity-by-volume — the render-for-cognition law breaks on throughput, not design
**Designed/Open.** G7 renders the per-turn thought-graph beautifully (roles as nodes, chains as edges, injections as edges). The design assumes the failure mode of opacity is *hiding* — and solves it by making cognition addressed, renderable data (rule 9). But at scale the opacity comes from **volume, not concealment.** Run the numbers the design implies: a 16-wide swarm (R2-FOLD H1) × multi-part replies × (per-turn + background + sense + rollup activation-contexts, G5) = potentially *hundreds of role-fires per minute*, all rendering. The `render-for-cognition` law (`feedback-render-for-cognition`: "his brain is the algorithm; offload compute to his perception") **assumes a rate his perception can absorb.** Nothing budgets the *rate* of cognition against the *bandwidth of a human watching it.* The failure: a perfectly transparent, fully-addressed, beautifully-rendered cognition surface that is *unwatchable* — transparent in principle, opaque in practice, because it scrolls faster than shape-perception works. *This is a genuine unknown-unknown: the design's own transparency mechanism (render everything) becomes the opacity mechanism at the design's own target width.* Designed answer to flag: rendering needs its OWN altitude-translation (B3-I applied reflexively to the cognition view) — *up-translate the swarm's activity to a rate and shape Tim can perceive*, drill-down on demand, not render-every-fire. The cognition view must itself be a cognition (a summarizing role over the swarm), or it drowns its own purpose.

### 4b · Model-swap = identity discontinuity (the continuity-across-substrate gap)
**Designed/Open.** Identity is "emergent" (collective-cognition) — grown by the write-half, carried by the twin. But the conscious/swarm cognition is **coupled to ONE swappable resident model.** The Company already swaps models freely (`company swap`, the native model layer). The unseen consequence: **upgrading or swapping the 4B silently rewrites the Company's cognitive signature.** The roles' behaviour, the swarm's blindspots (§1), the calibration of the jury-confidence, the *feel* of the voice — all shift the moment the resident model changes, because they are all properties of *that model*. There is **no continuity-across-substrate story.** The twin (model-of-Tim, separately held) gives continuity to *what the system knows about Tim*; nothing gives continuity to *how the Company itself thinks* across a model swap. At scale this is the "ship of Theseus" failure: the Company that was carefully tuned (§2) on model-A is a subtly different mind on model-B, and the introspective knowledge accumulated about model-A's behaviour (the conditions-stamped rollups) is partly invalidated — *but the rollups don't know that*, so old knowledge contaminates new behaviour. *Mechanism property: because every run-record stamps conditions including `stack-version`/model (introspective-data law), the substrate ALREADY HAS the signal to detect a swap and segment knowledge by cognitive-substrate-era — but nothing reads that signal as an identity-continuity boundary.* Designed answer to flag: a "cognitive-era" marker so rollups, jury-calibration, and tuning (§2) re-baseline on a model swap rather than silently carrying model-A's signature into model-B. Identity-continuity is a *first-class concern the moment the model layer is swappable* — and the model layer is *designed to be swappable.*

---

### 4c · Cost — the monotonically rising floor of cognition-about-cognition
**Designed/Open.** R1/R2 covered *per-turn* resource cost exhaustively (KV pool, `max_num_seqs`, fsync) — but that is the *snapshot* cost of one wave. They never modelled **sustained-operation cost**, which is genuinely unseen and is a different failure in kind. Three compounding bites:
- **The always-on floor.** Once background + sense + rollup + per-turn cognition all fire (G5, all four activation-contexts, DECISIONS Batch 3 Q2), the resident model is **never idle.** "Budget = attention" stops being a per-turn *cap* and becomes a **continuous compute/energy floor** — the card is doing cognition around the clock (background "sleep" consolidation, sense-passes on every screen change, scheduled rollups). R1/R2 modelled the busy-turn; nobody modelled the *never-idle steady state* and its power/thermal/wear cost on the one 16GB card the whole Company shares.
- **The cloud $/token bite.** The cloud-main option (DECISIONS Batch 2 Q3) makes every cloud-routed part a real **dollar cost per token**, and a mode can auto-route to cloud. Because the swarm-always-resident ⟂ separately-selectable-cloud-brain split means the *main stream* can be cloud while the swarm is local, cost scales with **conversation volume**, not just VRAM. Nothing in the conception budgets the $ envelope of a chatty day on a cloud main brain + a continuously-firing local swarm.
- **The compounding finding (the novel one):** *every mitigation this doc added is more cognition to pay for.* §1's monoculture-detector role, §2's self-tuning rollups, §4a's summarizing-cognition-over-the-cognition-view — each is *additional concurrent role-fires*. So **the introspective loop that makes the system smarter (§2) also makes it monotonically more expensive**: cognition-about-cognition has a rising cost floor, and the better it gets at watching itself, the more it costs to run. Nothing budgets the cost of the watching. *Mechanism property: because every role-fire is a `model.run` with usage+timing already captured (introspective-data law), the substrate ALREADY HAS the per-fire cost signal — but nothing aggregates it into a **cognition cost-budget** that the mode-dial spends against, the way the slot-budget caps concurrency.* The slot-budget caps *width*; nothing caps *spend-over-time*. Designed answer to flag: "budget = attention" needs a *second* axis — not just slots-now but **cost-over-time**, so a mode can declare "this much cognition per hour," and the self-tuning loop (§2) is itself subject to a cost cap (it cannot propose more cognition than the budget allows to pay for). Cost is what makes §2 *self-limiting* in a way drift alone does not — see §6.

## 5 · Second-order capabilities that emerge once the mechanism exists (prompt 1 — the generative read)

Grounding each in a mechanism property; flagging where it goes past B3's application map (which listed *fields*; these are *emergent properties of the substrate*, a different category).

- **The swarm reasoning over the codebase/memory/screen becomes one substrate, not three (Designed).** B3 lists K (codebase), H (memory), J (screen) as separate applications. The second-order capability is that *because all three are addressed data resolved by the same engine*, a single wave can fire roles that read code AND memory AND the screen **in one perceptual pass** and fan-in to a grounded judgement that no single-source reasoner could reach ("the screen shows X, the code says Y, you decided Z last week — these conflict"). The unlock is not three applications; it is **cross-source synthesis as a native operation.** Past B3's frame because B3 enumerated sources; this is the property of having them on one substrate.
- **Cognition becomes queryable as a first-class object (Designed).** Because `ui://cognition/<turn>` is addressed (B3-C), and rollups aggregate it (B3-F), the system can answer not just "why did you decide X" (B3-C) but **"how has my thinking CHANGED over time"** — query the cognition substrate the way you query any substrate. "Which roles have I stopped relying on? What do I now resolve automatically that I used to deliberate?" This is self-knowledge of *cognitive development*, not just of *decisions* — emergent once cognition is data + time + rollup.
- **Identity + memory as roles, not as special subsystems (Designed/Open, ties §3a).** Once the cast is rich, "remembering," "predicting-as-Tim," "perceiving the screen" are all *roles* — which means identity and memory stop being bolt-on subsystems and become **declared, inspectable, tunable, renderable** like everything else (the L1 dividend applied to the deepest layers). The second-order capability: you can *see and tune the Company's identity machinery the same way you see and tune a routing rule.* This is the collective-cognition note's "ONE console generalized per-type" reaching all the way down to identity.

---

## 6 · The relational read — how the unseen pieces compose (Tim's law)

The five findings are not a list; they **compose into one circuit**, and seeing the circuit is the point:

```
   §1 monoculture (correlated swarm)
        │  feeds correlated error into ↓
        ▼
   §2 self-tuning loop (rollups → propose cast/rule/budget changes)
        │  optimizes toward its own measurements →
        │  CAN narrow the cast toward its own monoculture (the drift)
        │  AND every mitigation it adds is more cognition to run →
        ▼
   §4c cost (every watcher-of-the-watcher is more spend)
        │  the rising cost floor is what makes §2 SELF-LIMITING →
        │  (drift narrows the cast; cost caps how much cognition can run at all)
        ▼
   §3a twin ↔ cast coupling (the swarm grows the corpus; the twin seeds the roles)
        │  identity emerges from this loop →
        ▼
   §4b model-swap discontinuity (the whole loop is coupled to ONE swappable model)
        │  a swap silently rebases the emergent identity →
        ▼
   §4a opacity-by-volume (the loop runs faster than Tim can perceive it)
        │  so the human-in-loop guardrail (propose-not-apply) →
        │  fails not because it's bypassed but because it's UNWATCHABLE at rate
        ▼
   ⇒ the guardrail that makes §2 safe (Tim approves how-it-thinks) DEPENDS on §4a
     being solved (Tim can actually perceive what he's approving).
```

**The relational finding (the thing no single section says):** the conception's safety rests on *propose-not-apply with a human in the loop* — and that guardrail is **only as good as Tim's ability to perceive what he is approving.** §4a (opacity-by-volume) is therefore not a separate rendering nicety; it is the **load-bearing dependency of the entire safety story** at scale. A monocultural (§1), self-tuning (§2), identity-coupled (§3a), substrate-fragile (§4b) cognition is *safe exactly to the degree it stays perceivable* (§4a). Render-for-cognition is not a FORM concern flanking the build — at scale it is the **keystone of governance.** That inversion — rendering as the keystone of safety, not the polish on top — is the deepest thing the prior frames could not see, because each treated rendering (G7), governance (G9), and the application space (B3) as separate groups. They are one circuit.

---

## 7 · What to put to Tim (don't decide silently — the scout's forks)

Ordered by leverage. All Designed/Open.

1. **Epistemic monoculture (§1) — the highest.** Confirm the jury/quorum confidence is *labelled* "intra-model agreement, not independent corroboration," AND choose the independence strategy: accept-and-label / prompt-induced perspective-diversity (skeptic/steelman/contrarian roles) / a different-model critic-verdict layer. This bites the twin's credibility directly.
2. **The cognition self-tuning loop (§2) — the biggest opportunity.** Is "the system proposes how to think better, Tim approves" an intended direction (propose-not-apply, like self-coding)? It is nearly free given the mechanism, and it is the truest form of "limitless." If yes, it also forces the automaticity/faculty-promotion loop the collective-cognition note has only gestured at.
3. **Where the twin lives (§3a).** A role, a layer, or the budget-allocator? My lean: a cross-cutting bias-source that resolves into role contexts. And: confirm the swarm's run-records are *intentionally* the corpus that grows the cold-start twin (this unblocks the RHM's defining feature as a byproduct of this build).
4. **Live working-memory (§3b).** Should cognition persist a slowly-decaying cross-turn/cross-session working-set (a `working://session` space), distinct from stored memory? "Budget = attention" implies it; the build lacks it.
5. **Opacity-by-volume / rendering as keystone (§4a + §6).** Confirm the cognition view must itself be a *summarizing cognition* (up-translated, drill-down-on-demand) rather than render-every-fire — because at the design's own target width, render-everything becomes unwatchable, and the safety guardrail depends on watchability.
6. **Cost as a second budget axis (§4c).** Should "budget = attention" gain a *cost-over-time* axis (cognition-spend per hour/mode), distinct from the slots-now cap — so the always-on steady state, the cloud-$ envelope, and the self-tuning loop's own rising cost are all bounded? Cost is what makes §2 self-limiting; nothing budgets it today.
7. **Cognitive-era continuity (§4b).** Should a model-swap re-baseline rollups/jury-calibration/tuning (a cognitive-era marker), so model-A's signature doesn't silently contaminate model-B?
8. **Roles proposing roles (§3c).** Defer until §2 exists, then the cast self-extends the way code self-codes.

---

## 8 · Sources

- **The conception (Observed by read):** `../00-LANDSCAPE.md`, `../broader/00-BROADER-LANDSCAPE.md`, `../broader/B3-broader-applications.md`, `../Concurrent Cognition — Completion Criteria.md`, `../Concurrent Cognition — Implementation Guide.md`, `../Concurrent Cognition — Research Synthesis.md`, `../DECISIONS.md`.
- **The reviews (Observed by read):** `../review/R1-FOLD.md`, `../review/R1-adversarial.md`, `../review/R2-FOLD.md` (the epistemic axis is the gap THESE leave — they cover engineering exhaustively).
- **Company goals (memory, point-in-time):** `[[project-collective-cognition]]` (the layered-cognition spine; budget=attention; automaticity gestured-at; identity emergent), `[[project-introspective-data-building]]` (the self-instrumenting law; the rollup loop §2 extends; conditions-stamping that §4b reuses), `[[project-rhm-v1-state]]` (the twin is cold-start/corpus-dependent — §3a unblocks it; the self-coding propose-not-apply gate §2/§3c inherit), `[[feedback-altitude-transformation-layer]]` (up/down-translation — §4a applies it reflexively to the cognition view), `[[feedback-render-for-cognition]]` (his-brain-is-the-algorithm — §4a/§6 find its throughput limit), `[[feedback-autonomous-spawn-lead-only]]` (the floor that bounds §2/§3c), `[[project-the-company]]`, `[[project-company-one-entity]]`.
- **Governing discipline inherited by every fork:** propose-not-apply / surfaced-for-review / git-reversible (the self-coding gate) · author-from-registry · fail-loud · render-as-navigable-surface (rule 9, which §6 elevates to the keystone of safety).
