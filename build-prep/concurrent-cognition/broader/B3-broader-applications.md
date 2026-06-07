---
type: design
module: build-prep/concurrent-cognition/broader
series: concurrent-cognition-broader
seq: "B3"
aliases: ["Concurrent Cognition — Broader Applications", "B3 — Application Space", "Where else the mechanism unlocks"]
tags: [company, design, concurrent-cognition, collective-cognition, reuse, application-space, discovery-scout]
status: open
relates-to: ["[[Concurrent Cognition 01]]", "[[Concurrent Cognition — Research Landscape (aggregated)]]", "[[Collective Cognition — the context-resolution spine]]", "[[project-introspective-data-building]]", "[[feedback-altitude-transformation-layer]]", "[[Company Map]]"]
---

# B3 — Broader Applications of the Concurrent-Cognition Mechanism

> **Status: open / provisional / discovery-scout.** This is the *application-space* chapter of the concurrent-cognition work — a scout, not a build plan. It assumes the mechanism designed in `00-LANDSCAPE` + threads `01–06`, then asks Tim's question directly: *"the applications and potential uses of this are limitless… I can reuse this for other things as well."* Where ELSE in the Company (and beyond) does the **same mechanism** unlock something. The `broader/` directory held only this `B3-` when written (no B1/B2 present); this doc is self-contained and cross-links the threads it builds on.
>
> **Epistemic tags (repo rule, doc 06's model):** **Observed** = read in `~/company` code (01–06 already cite the file:lines; I re-cite the anchor, not re-derive it). **Designed** = an intended application, not built. **Open** = decide with Tim. This doc is forward-looking, so **almost every application is Designed/Open.** No application below "works" — none is built. The *reuse anchors* are Observed (they exist today); the *applications of them* are Designed.

---

## 0 · The mechanism, named once (so "reuse" means something exact)

Tim's "this" is not one feature. It is a **relational primitive** with six composable parts (the landscape's §4). Stating it precisely is the whole game, because an "application" is *this primitive pointed at a new field*:

```
  a RESIDENT model  ←  fired CONCURRENTLY (≤32, the vLLM knee)  as a SWARM of ROLES
        │                                                              │
        │  each role = {prompt · input-addresses · output JSON-schema · trigger · model-binding · destination · render-hint}
        │                                                              │
        ▼                                                              ▼
  outputs are STRUCTURED JSON that RESOLVE INTO ADDRESSES  ──────▶  fed forward into the
  (address→resolve→inject; chains = role→role edges)               NEXT stage / part / decision
        │                                                              │
        ▼                                                              ▼
  MODE = the one dial (gates whether to run · which role-set · the SLOT BUDGET = attention)
        │
        ▼
  RENDER RULES project roles→nodes, chains→edges, injections→edges, live via cognition.* SSE
```

The seven reusable invariants — the things that DON'T change across contexts (pattern-recognition law):

1. **Many small structured judgements run at once, cheaper than one big one** (concurrency on a resident model; the vLLM knee makes 32 ≈ free vs 1).
2. **Each judgement is a declared ROLE** — registry row, not bespoke code (one source; add a row, not a system).
3. **Outputs are addresses** — they resolve into the next thing via the *existing* `_resolve_context_at` path (no new injection machinery).
4. **Composition is edges** — role→role chains, fan-in (`join`), selective-emit (`gate`) — the node-graph substrate verbatim.
5. **A budget caps the spend** — MODE selects how much cognition a stage may cost (budget = attention).
6. **It self-instruments** — every role-fire emits a run-record with conditions (introspective-data-building, the write-half).
7. **It renders live** — the swarm is data, so render-rules project it to a navigable surface (rule 9).

> **An application is "real" only if concurrency + composition BUY something** (the quality gate, applied per row below). "Put an LLM here" is not an application of *this* — it's just an LLM call. The filter: does the field decompose into **many independent or chained sub-judgements** that a swarm resolves in parallel, where a single call would be slower, weaker, or coarser? If not, mark it **weak** or cut it.

---

## 1 · The application map

**Leverage = unlock-magnitude × reuse-fraction.** A pure-reuse application that unlocks a lot is the highest leverage (you get the unlock almost for free); a net-new-heavy application that unlocks a little is the lowest. The "reuse vs net-new" column and the leverage callout (§3) are therefore the *same* judgement, not two — the column feeds the callout.

| # | Application (field) | What a ROLE is here | What concurrency+composition UNLOCKS | Reuse vs net-new | Conc. gate |
|---|---|---|---|---|---|
| **A** | **Live voice reply** (the seed — threads 03/04/05) | enricher: retriever · fact-grounder · tone-shaper · relevance-scorer + the brevity-judge | Part 1 instant while the swarm resolves the substance behind it → brain↔TTS overlap, "speaks like a person" | mostly **reuse** (`resolve_role`, `_resolve_context_at`, voice ndjson); net-new = parallel dispatch + part-loop | strong |
| **B** | **Background cognition** (idle/scheduled cascade — collective-cognition §2.5) | consolidation roles: memory-summariser · gold-grade extractor · skill-registrar · stale-index detector | the system thinks WHEN ATTENTION IS IDLE ("sleep") — N consolidation passes over the day's substrate at once, no operator turn | **reuse** swarm + run-records; net-new = a scheduler trigger (time/volume) + the write-half sinks | strong |
| **C** | **The RHM's self-reflection** ("show me what I was thinking on turn N") | reader-roles over its OWN cognition trace: explain-this-turn · why-did-I-abstain · what-did-I-inject | the twin can INTROSPECT — read its own addressed thought-graph the same way it reads any context (one substrate) | **reuse** wholesale (cognition is addressed data; `_chat_context` resolves `ui://cognition/<turn>`) | medium |
| **D** | **Decision / build-intent wire** (Group W) | pre-dispatch swarm: scope-checker · consequence-classifier · risk-flagger · precedent-finder · standards-checker | a decision is APPRAISED FROM MANY ANGLES concurrently before it surfaces — richer than one classifier, each angle a declared role/lane | **reuse** the wire + governance + `output_destination`→surface; net-new = the appraisal role-set | strong |
| **E** | **The build loops themselves** (company-build / rhm-build / voice-build / mockup-build) | resident reviewer-roles: lane-readiness · file-disjointness · criterion-verifier · design-critic · adversary | the loops' *judgement* steps (which lane is buildable, did this pass) become a fast resident swarm instead of heavy `claude -p` subagents — **bounded by autonomous-spawn-lead-only (§4)** | partial reuse; net-new = role-set + the role-vs-subagent boundary decision | strong |
| **F** | **Introspective-data rollups** (the law itself) | analyst-roles over run-records: distribution-summariser · anomaly-spotter · condition-correlator · gotcha-writer | the rollup half ("raw→knowledge") is N concurrent analyses over the event substrate — the gotchas list / manifest write themselves | **reuse** events/CAS/run_stats; net-new = analyst role-set on the rollup (off hot path) | strong |
| **G** | **The model-of-Tim / twin prediction** (D8, cold-start today) | a JURY: N draws of "what would Tim decide / how would he want this shown" → aggregate/spread | prediction with a **confidence + spread**, not one guess — variance is signal; disagreement = "ask Tim" | reuse swarm; **net-new = the per-draw-variation primitive (§4 reshape!)** + the corpus | strong |
| **H** | **Memory consolidation** (write-half; overlaps B) | roles: dedup-cluster · merge-proposer · contradiction-finder · salience-scorer · forget-candidate | many memory operations run at once over the substrate; the network of memories re-organises (cf. substrate-mcp `consolidate`/`cluster_by_embedding`) | reuse swarm + addresses; net-new = consolidation sinks + clustering inputs | strong |
| **I** | **The operable surface / canvas** (render + altitude) | up-translation roles: summarise-for-Tim · pick-the-shape · draft-the-A/B/C/D options · choose-render-form | the **altitude transformation layer** (off the given list, §4) — N candidate up-translations scored by learned presentation-prefs, then the best rendered | reuse render-rules + SSE; net-new = translation role-set + the learned-presentation feedback | strong |
| **J** | **Multi-modal: screen/app awareness** (collective-cognition "senses") | sense-roles: screen-reader · element-locator · state-differ · what-changed-since · relevance-to-intent | the system SEES — many vision/diff passes over a screenshot/DOM at once feed the conscious field ("it already knew") | reuse swarm + injection; **net-new = a vision-capable resident model + capture** | strong (if vision resident) |
| **K** | **Document / codebase reasoning** (the first real use — self-hosting) | reader-roles over chunks: per-file summariser · cross-file linker · contradiction-checker · answer-grounder | map-reduce over a codebase: N files read concurrently → fan-in (`join`) → grounded answer; beats the 600k single-context read | **reuse** node-graph (`codebase`/`ask`/`join`) + swarm; net-new = the chunk-fanout role-set | strong |
| **L** | **Cognition-as-coordination recursion** (the system coordinates its OWN sub-builds) | coordinator-roles: next-buildable-lane · dependency-resolver · conflict-detector · merge-readiness | the swarm-that-thinks becomes the swarm-that-BUILDS-ITSELF — the recursion Tim named; **HARD-bounded by autonomous-spawn-lead-only (§4)** | reuse swarm + graph-coordination; net-new = the bounded action-edge + the lead/worker line | strong but BOUNDED |
| **M** | **Typed-triage classification** (collective-cognition law; off-list) | one classifier-role PER declared event-type, fired concurrently against an arriving event | every incoming event classified against the typed registry IN PARALLEL → remember / inject-quietly / escalate-now; kills "annoying" structurally | reuse swarm + `output_destination`→lanes; net-new = the per-type classifier rows | strong |
| **N** | **Plan-review / design-critic / adversarial-verify as resident swarms** (off-list) | critic-roles: correctness-adversary · reuse-simplifier · form-critic · contract-checker · red-teamer | the review *quorum* (today heavy `claude -p` agents) becomes a fast resident swarm — many adversaries at once, each a declared lens | partial reuse; net-new = critic role-set + the same lead/worker bound as E/L | strong |
| **O** | **Beyond the Company — the primitive as a product** (off-list, furthest) | any domain's decomposable judgement: triage, scoring, multi-perspective drafting, ensembling | the registry-driven concurrent-role substrate is **domain-agnostic** — it's a general "structured swarm over a resident model" engine others could point at their field | reuse the whole substrate; net-new = packaging + the domain's roles | varies |

---

## 2 · The applications in depth (the content lives here)

### A · Live voice reply — the seed, named so the others contrast against it
This is the application threads 03–05 already design, listed for completeness: enricher roles resolve behind an instant Part 1, structured outputs inject into later parts, mode gates the budget. Everything below **reuses the same six pieces** pointed at a different field. The point of B3 is that voice is **one instance of a general engine**, exactly as Tim said — and the engine's value is the sum of A–O, not A alone.

### B · Background cognition — the swarm when no one is talking
Collective-cognition's activation spectrum (§2.5) names **background/scheduled** firing: the cascade runs on time/volume/idle triggers, not only on an operator turn. This is the swarm's most under-appreciated reuse. While Tim sleeps, the resident model is idle — and idle VRAM is wasted attention. A background wave fires N consolidation roles over the day's event substrate: summarise the threads touched, extract gold-grade turns for the twin, register recurring resolutions as new faculties (automaticity), flag stale indices. **Concurrency buys the whole point**: consolidation is embarrassingly parallel (each summary/extract is independent), so 32 passes finish in the time of one. The write-half (introspective-data-building) is the destination — these roles WRITE knowledge, they don't answer a turn. *Net-new:* a scheduler trigger and the consolidation sinks; the swarm itself is reuse. This is the literal mechanism behind Tim's "sleep" frame.

### C · The RHM's self-reflection — it can read its own mind
Doc 06 establishes that the cognition layer is *addressed data on the event log* — `ui://cognition/<turn>` is a resolvable address. The non-obvious consequence: the RHM can **introspect** by running reader-roles over its own trace. "Why did you abstain on turn 412?" becomes a role whose `input_addresses` point at `cognition.turn.start{412}` and its role-fires; "what did you inject?" reads the `cognition.inject` events. This is *the same machinery* as reading any context — **pure reuse, zero net-new substrate** (only role rows). The unlock is large for the altitude/trust relationship: a system that can explain its own thinking in Tim's terms is the up-translation of cognition itself. Medium leverage only because the unlock, while real, is narrower than B/D/F.

### D · Decision / build-intent wire — appraise from many angles before surfacing
The wire (Group W) today classifies a build-intent by POLICY posture and binds `derived_from`. A swarm widens the *appraisal*: a scope-checker, a consequence-classifier, a risk-flagger, a precedent-finder ("have we built something like this?"), and a standards-checker all fire **concurrently** the instant an intent is minted, each writing structured JSON to its lane. The operator's surfaced review item then carries a *multi-angle appraisal*, not one classifier's verdict. **Concurrency buys breadth without latency** — five lenses in the time of one. Critically, `output_destination` already covers this: each role's output routes to the surfaced/inbox via `surface_review` (Observed reuse anchor, 01 §A8). *Net-new:* only the appraisal role-set. High leverage: big unlock (richer governance) on near-total reuse (the wire + governance + destinations all exist).

### E · The build loops themselves — judgement steps become a resident swarm
The autonomous build loops (`company-build`, `rhm-build`, `voice-build`, `mockup-build`, `remediation-build`) currently make their *judgements* — which lane is buildable, are lanes file-disjoint, did this criterion verify, does the FORM pass — by dispatching heavy `claude -p` subagents or by the lead reasoning inline. Many of those judgements are exactly the swarm's shape: fast, structured, parallel ("is lane X ready? → {ready: bool, blockers: []}"). Turning the *appraisal* half of the loops into a resident swarm makes them faster and cheaper. **But this is bounded** — see §4: a worker-role must NEVER fire `claude -p` / arm `acceptEdits`. The swarm may *appraise and propose*; only the lead, supervised, *acts*. So E is "the loops' thinking, not the loops' building." High leverage, hard line.

### F · Introspective-data rollups — the knowledge half writes itself
The introspective-data-building law has two halves: emit run-records (built, on the hot path) and **roll them up into knowledge** (off the hot path, mostly unbuilt). The rollup half is a swarm: N analyst-roles over the accumulated `op.run` records — a distribution-summariser, an anomaly-spotter ("p95 doubled when concurrency > 24"), a condition-correlator, a gotcha-writer that appends to the gotchas list. **Concurrency buys the multi-stream coverage** the law names (cognition · decisions · surface-usage · errors · twin · cost) — one analyst-role per stream, all firing on the rollup tick. *Net-new:* the analyst role-set; the substrate (events/CAS, `run_stats`) is reuse. This is the law eating its own tail in the best way — the system that measures itself gains roles that *read* the measurements and write the manifest.

### G · The twin / model-of-Tim — a jury, not a guess (and a reshape)
Prediction is where ensembling shines: don't ask the twin once "what would Tim decide?" — ask it **N times concurrently** and read the *distribution*. Consensus = high confidence; spread = "this is a genuine fork, ask Tim." Variance is signal, not noise. This is the highest-value use of concurrency-for-quality (vs concurrency-for-latency). **But it surfaces a reshape the current 6-piece design does NOT cover** — see §4, the sampling-diversity gotcha: identical role+config draws collapse to one memo-cached result (`llm` not VOLATILE, docs 02/05). A jury of identical prompts silently returns one answer N times. So G *requires* a per-draw-variation primitive the registry doesn't yet have. An application reshaping the core — exactly the unknown-unknown the scout exists to find.

### H · Memory consolidation — the network re-organises itself
Overlaps B (it's a background wave) but deserves its own row because the *operations* are distinct and the substrate-mcp already proves the primitives exist elsewhere (`consolidate`, `cluster_by_embedding`, `find_state_asymmetries` — found-elsewhere, INFORMS not replaces, per memory). Consolidation roles: dedup-cluster, merge-proposer, contradiction-finder, salience-scorer, forget-candidate. Each operates over a slice of the memory substrate; fan-in (`join`) assembles the re-organisation proposal, which **surfaces for review** (never auto-writes — reflects-never-owns). **Concurrency buys** parallel operation over a growing memory network that a serial pass couldn't keep up with as the corpus compounds.

### I · The operable surface / canvas — the altitude transformation layer (off-list, high value)
The given list omitted the **altitude transformation layer** (feedback memory, "big missing angle, high value") — yet it is a natural, almost archetypal swarm application. Up-translation (technical reality → Tim's altitude/words/shape) is a *generative judgement with many candidates*: summarise-for-Tim, pick-the-shape (tread-marks? table? canvas?), draft-the-A/B/C/D option-set, choose-the-render-form. Fire these **concurrently**, score each candidate against the *learned presentation-preferences* (the same prediction machinery), render the winner. Down-translation (Tim's intent → record-edits) is the symmetric swarm. **Concurrency buys** the candidate-set that scoring needs — you can't pick the best presentation from one. The unlock is the thing that makes the whole system *operable by Tim specifically*. High leverage; the reuse is the render-rules + SSE; net-new is the translation role-set + the presentation feedback loop. **Calibration note:** this being absent from the list is the signal that the list is a floor, not a ceiling.

### J · Multi-modal screen/app awareness — the senses
Collective-cognition names embeddings/vision as **senses**. A vision-capable resident model fired as a swarm over a screenshot/DOM: screen-reader, element-locator, state-differ ("what changed since last frame"), relevance-to-intent. Their structured outputs inject into the conscious field so the RHM perceives the screen *already-processed* ("it already knew" — aliveness). **Concurrency buys** the many simultaneous perceptual passes human vision does in parallel. *Net-new is heaviest here* — a vision model resident on the 16GB card (VRAM-arbitrated against the brain), plus screen capture. Strong gate IF a vision model can be resident; otherwise on-demand (accept the load latency). Furthest-reaching of the "in-Company" rows.

### K · Document / codebase reasoning — map-reduce as a swarm
The self-hosting first-use reads the whole repo into one 600k-char context (fails loud past it). A swarm replaces that with **map-reduce**: chunk the corpus, fire N per-chunk reader-roles concurrently (per-file summariser, cross-file linker, contradiction-checker), fan-in via `join` to a grounded answer. **Concurrency buys** the parallel read that makes large-corpus reasoning bounded and fast, and composition (`join`/`gate`) buys the reduce. This is **near-total reuse** — the node-graph substrate (`codebase`, `ask`, `join`, `gate`, per-port addresses) is exactly the map-reduce primitive (doc 02). The unlock is real (the retrieval/large-context gap STATE.md names). High leverage by the reuse×unlock product.

### L · Cognition-as-coordination recursion — the swarm builds itself (BOUNDED)
The recursion Tim named: the concurrent-role mechanism that *thinks* is the same shape that could *coordinate its own sub-builds* — coordinator-roles deciding the next buildable lane, resolving dependencies, detecting conflicts, judging merge-readiness. This is genuinely the deepest reuse (the system's cognition coordinating its own construction). **It is HARD-BOUNDED by the autonomous-spawn-lead-only constraint (§4):** a role is a worker; a worker must NEVER fire `claude -p` or arm `acceptEdits`. So the recursion is allowed to **think, appraise, and propose the coordination** — the *action* (the actual spawn) stays lead-only and supervised. Naming this boundary IS the finding: the recursion is safe and powerful for the *coordination judgement*, forbidden for the *autonomous action*. The role-vs-subagent line (§4) is the design decision this forces.

### M · Typed-triage classification — one classifier-role per event-type
The collective-cognition triage law: significance is DECLARED in a typed event-registry (condition·lane·channel·urgency); the AI only *classifies* against it, never decides "is this important?" The swarm is the natural engine: **one classifier-role per declared event-type**, fired concurrently against an arriving event, each emitting structured JSON routed to its lane (remember / inject-quietly / escalate-now) via `output_destination`. **Concurrency buys** classifying against many types at once as events arrive; **composition buys** the lane-routing. This structurally kills "annoying" (can only fire what's declared fireable) and is the cognition-meets-reach organ (the outbound flip — the RHM contacts Tim). Pure reuse of `output_destination` + the swarm; net-new is the per-type rows. High leverage.

### N · Plan-review / design-critic / adversarial-verify as resident swarms
The Company already does heavy review with `claude -p` subagents (plan-review, design-critic, the verification adversary). Many of those lenses are swarm-shaped: a correctness-adversary, a reuse-simplifier, a form-critic, a contract-checker, a red-teamer — each a declared role, all firing **concurrently** on a diff or a plan. **Concurrency buys** the quorum (many adversaries cheaper than many subagents); composition buys the fan-in to a verdict. Same lead/worker bound as E/L: the swarm *critiques and proposes*; it does not *act*. Note the kinship with G — a critic quorum is an ensemble, so it inherits the sampling-diversity reshape (§4) if the critics share a model+config.

### O · Beyond the Company — the primitive as a product
Furthest out, but Tim said "for other things as well." The substrate — registry-driven structured roles fired concurrently on a resident model, outputs-as-addresses, mode-as-budget, self-instrumenting, live-rendered — is **domain-agnostic**. Any field with decomposable structured judgement (triage, multi-criteria scoring, multi-perspective drafting, ensembled prediction) could point this engine at it. The reuse fraction is the entire substrate; the net-new is the domain's role-set + packaging. This is the "limitless" Tim named, made concrete: the limit isn't the mechanism, it's how many fields decompose into parallel structured roles. Leverage here is a *future* product judgement, flagged not scored.

---

## 3 · The highest-leverage reuses (leverage = unlock × reuse-fraction)

Called out because leverage is the criterion, not a vibe. These five score highest on *big unlock × high reuse* — the unlock comes almost for free:

1. **K · Document/codebase reasoning (map-reduce swarm).** Near-total reuse (the node-graph IS map-reduce — doc 02), closes the large-context/retrieval gap STATE.md names, and directly serves the self-hosting first-use. Highest reuse×unlock product; arguably the proving-spike's natural *second* target after voice.
2. **M · Typed-triage classification.** Pure reuse of `output_destination` + the swarm; unlock is the entire outbound/reach organ (the RHM contacts Tim) AND it structurally kills "annoying." The collective-cognition law was *waiting* for this engine.
3. **I · Altitude transformation layer.** The thing that makes the system operable by Tim *specifically* (named "big missing angle, high value"). Reuse = render-rules + SSE; unlock = the whole up/down-translation that spares Tim the depth. Off the given list — its absence is the signal.
4. **F · Introspective-data rollups.** The knowledge-half of a law that's already half-built; reuse = the event substrate + `run_stats`; unlock = the manifest/gotchas writing themselves across all six streams.
5. **B · Background cognition.** Turns idle VRAM (wasted attention) into the consolidation/learning that grows the twin. Reuse = the swarm; unlock = the write-half running as "sleep." The mechanism's value compounds *while no one is using it*.

Honourable mention: **D (decision-wire appraisal)** — high reuse, real unlock, just narrower in scope than the five above.

---

## 4 · The reshape-the-core findings (the unknown-unknowns — highest value)

These are applications that **change the core design**, not just consume it. Easiest to skip; most valuable to surface.

### R1 · Ensembling needs a per-draw-variation primitive the 6-piece design lacks
**Surfaced by G (twin jury), inherited by H/N (critic/consolidation quorums).** Docs 02 §5(d) and the landscape §3(9) flag it: `nodes/llm.py` is **not VOLATILE**, and the memo gate (`scheduler.py:96`) collapses identical `(type, version, config, inputs)` signatures to ONE cached result. So a "jury of N identical prompts for variance" **silently returns one answer N times** — the exact opposite of what an ensemble needs. The landscape already names the *node-graph* fix (mark `llm` VOLATILE, §3(9)), but the **role registry has no field for it** — a role fired N times for sampling-diversity needs a declared "draw N, vary the seed/temperature per draw, aggregate the spread" primitive. **This is a 7th piece** (an *ensemble/jury* mode of `run_role`) that several high-value applications (the twin's confidence, the critic quorum, grounding-confidence) all require. *Reshape: the registry's role-run needs an ensemble dimension, not just single-fire.*

### R2 · The role-vs-`claude -p`-subagent boundary, against a hard constraint
**Surfaced by E, L, N (the build/coordination/review applications).** The recursion is seductive: the swarm-that-thinks coordinating the swarm-that-builds. But the **autonomous-spawn-lead-only** memory is a hard line, written from a real 2026-06-05 incident: *a worker (any sub-agent) must NEVER fire `claude -p`, arm `acceptEdits`, or trigger an autonomous self-modifying build — that spawn is lead-only and supervised, only on explicit Tim authorization.* This **bounds the recursion precisely**: a concurrent-cognition role is a *worker*; therefore a role may **appraise, classify, critique, and propose** coordination/builds, but a role may **never dispatch one**. The action edge stays with the supervised lead. *Reshape: the role registry's `output_destination` must be able to write a SURFACED build-intent (reflects-never-owns) but must be structurally incapable of dispatch — the same off-the-MCP-face discipline the wire already uses for `dispatch_decision`. The design should make "a role cannot act autonomously" an enforced floor, not a convention.*

### R3 · `output_destination` is more load-bearing than thread 01 treats it
**Surfaced by D, F, H, M (decision-appraisal, rollups, consolidation, triage).** Thread 01 lists `output_destination` as a field naming one of four existing sinks (response · event · store · surface). But these applications write to *materially different* destinations with *different governance*: triage routes to typed lanes/channels (outbound reach); consolidation *surfaces a proposal* (never auto-writes, reflects-never-owns); rollups *write a living record* (the manifest/gotchas); the decision-appraisal *attaches to a surfaced review item*. The field exists, but whether its four kinds *cover* these — especially the reflects-never-owns "propose, don't write" sink and the typed-lane/channel routing — is **Open**, and an application (M's per-type channel routing) likely *widens* it. *Reshape: `output_destination` may need a "propose/surface for review" kind distinct from "write," and a "typed-lane/channel" kind — settle it against the triage + consolidation applications before it's hardcoded to four.*

### R4 · "Mode = the dial" generalises past presence-modes to per-application budgets
**Surfaced by B, F, I, J (background, rollups, altitude, senses).** Thread 04 binds the slot-budget to the *presence mode* (listening/walkthrough/focus…). But background cognition, rollups, and sense-perception are NOT presence modes — they're *activation contexts* (collective-cognition §2.5: per-turn · per-activity · background · trigger). Each needs its own budget (background can spend a lot of idle VRAM; a sense-pass must be cheap and fast). *Reshape: the "budget = attention" cap is keyed on the activation context, of which presence-mode is one kind — the budget registry should be indexed by activation-context, not only by the eight presence modes. Otherwise background/sense/rollup swarms have no budget home.*

> **Tags on §4:** all four are **Designed/Open** reshapes inferred from composing the applications against the threads' Observed gaps. I have not verified any against a built system — they are design tensions to resolve WITH Tim, surfaced by the scout precisely because each is invisible from inside any single application.

---

## 5 · The shape of the whole space (the relational read)

The applications are not a list — they're **the same circuit pointed at different fields**, and they *compose into each other*:

```
   senses (J) ──┐                          ┌──▶ outbound/reach (M triage)
                ▼                          │
   background (B) ──▶ consolidation (H) ──▶ twin/model-of-Tim (G jury)
                │                                    │
                ▼                                    ▼
   the live conscious turn (A voice) ◀── altitude up/down-translate (I)
                │                                    ▲
                ├──▶ self-reflection (C) ────────────┘
                │
                ├──▶ decision appraisal (D) ──▶ build loops (E) ──┐ bounded by R2
                │                                                  ▼
                └──▶ doc/code reasoning (K) ──▶ self-coordination (L) [lead acts]
                                                   │
   everything emits run-records ──▶ rollups (F) ──▶ knowledge ──▶ improves all of the above
                                                   (introspective-data write-half)
```

Read relationally (Tim's law): the swarm is **one organ** that the modes/activation-contexts point at different fields, and **F closes the loop** — every application self-instruments, the rollup swarm turns that into knowledge, which improves every application. That recursion (use → record → knowledge → better use) is the introspective-data law, and it makes the application space *grow its own value over time*. The "limitless" isn't hyperbole — it's that (a) the mechanism is field-agnostic, (b) adding a field is adding role-rows (one source), and (c) F means each new field makes the others smarter. **The mechanism is the Company's general cognition substrate; voice was the first place it showed.**

---

## 6 · Open questions to put to Tim (don't decide silently)

- **R1 (ensemble primitive):** add a "draw N / vary / aggregate-spread" dimension to `run_role` now (so the twin-jury, critic-quorum, grounding-confidence all land), or defer until an ensembling application is built? It's a 7th piece.
- **R2 (recursion boundary):** confirm the line — roles *propose* coordination/builds, the supervised lead *acts*. Should "a role cannot dispatch" be an enforced structural floor (like the wire's off-MCP-face discipline), and is that the same boundary for E/L/N?
- **R3 (`output_destination`):** does the field need a reflects-never-owns "propose/surface" kind and a typed-lane/channel kind, settled against triage (M) + consolidation (H) before it's fixed at four?
- **R4 (budget keying):** key the slot-budget on *activation-context* (per-turn / per-activity / background / trigger) rather than only the eight presence modes — so background/sense/rollup swarms have a budget home?
- **Sequencing the scout into a build:** which application is the *second* proving target after voice — **K (codebase map-reduce, highest reuse×unlock + serves self-hosting)**, **M (triage, the reach organ)**, or **F (rollups, the knowledge half)**? Each proves a different reuse face of the one engine.
- **The product question (O):** is "the concurrent-role substrate as a general engine" a future Company product direction, or is the scope deliberately the Company's own cognition only?

---

## 7 · Sources

- **This series (Observed by read):** `00-LANDSCAPE.md`, `01-role-registry.md`, `02-graph-substrate-reuse.md`, `03-concurrency-and-injection.md`, `04-staged-response-queue.md`, `05-voice-stream-coupling.md`, `06-rendering.md` — all the file:line reuse anchors cited above live in those threads (re-cited as anchors, not re-derived).
- **Repo orientation (Observed):** `~/company` `AGENTS.md` (rules 2/3/4/8/9/10), `MAP.md` (the live registry + the Suite/wire), `STATE.md` (what's built: RHM, wire, voice, ops/gpu, the retrieval/twin gaps).
- **Company goals (memory, point-in-time):** [[project-collective-cognition]] (layered cognition; activation spectrum; budget=attention; triage law; the senses), [[project-introspective-data-building]] (the self-instrumenting law; the rollup half; the six streams), [[feedback-altitude-transformation-layer]] (the two-way up/down translation; learned presentation — the off-list I), [[feedback-autonomous-spawn-lead-only]] (the hard recursion boundary — R2/L/E/N), [[feedback-render-for-cognition]], [[feedback-not-agent-architecture-by-default]], [[project-the-company]], [[project-company-one-entity]].
- **Governing rules:** rule 3 (one source — add a role-row, not a system), rule 4 (fail loud), rule 8 (author from the registry), rule 9 (navigable visual surface; FORM is half of done). All applications inherit them.
