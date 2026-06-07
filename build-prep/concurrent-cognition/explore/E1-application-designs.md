---
type: design
module: build-prep/concurrent-cognition/explore
series: concurrent-cognition-explore
seq: "E1"
aliases: ["Concurrent Cognition — Application Designs", "E1 — The Four Worked Examples", "K/I/M/B as buildable shapes"]
tags: [company, design, concurrent-cognition, collective-cognition, application-space, worked-examples, thought-shapes]
status: open
relates-to: ["[[Concurrent Cognition — Broader Applications]]", "[[Concurrent Cognition — Research Landscape (aggregated)]]", "[[Staged Response Queue]]", "[[Graph Substrate Reuse]]", "[[Concurrent Cognition — Completion Criteria]]", "[[DECISIONS]]", "[[project-collective-cognition]]", "[[feedback-altitude-transformation-layer]]"]
---

# E1 — The Four Worked Examples (widening "limitless applications" into buildable shapes)

> **Status: open / generative / designed (not built).** This is the *extension* chapter. Where B3 mapped fifteen applications at paragraph altitude, E1 takes the **four targets Tim locked as the post-voice roadmap** (DECISIONS Batch-2 Q4: *codebase-map-reduce · altitude-translation · typed-triage · background cognition*) and designs each as a **concrete worked example a builder could spike from this doc alone**: real role IDs, the thought-shape as JSON, routing rules in the Batch-5 grammar (predicates over resolved values, never prose), real `run://<turn>/<role>` addresses, real destination kinds.
>
> **Epistemic tags (repo rule, doc 06's model):** **Observed** = read in `~/company` code or this series' threads (re-cited as anchors, not re-derived). **Designed** = an intended application, not built. **Open** = decide with Tim. This doc is forward-looking → almost everything is **Designed/Open**; the *reuse anchors* are Observed.

---

## 0 · The frame — these four are NOT four copies of the voice stream

The single most important generative finding, stated first because it reframes the whole roadmap:

**The voice reply (target A, the seed) is a *linear part-grain stream* — one brain, sequential parts, each enriched by the prior. The four post-voice targets each exercise a DIFFERENT staged-output shape.** Naming those shapes *is* the extension — it is what tells the THOUGHT_SHAPES registry (doc 04) what archetypes it must carry beyond `acknowledge_retrieve_synthesise_offer` and `direct`.

```
   shape archetype        what staging means here              the four
   ───────────────        ───────────────────────              ────────
   LINEAR-STREAM          sequential parts, each enriched       A (voice — the seed)
   REDUCE-TREE            fan-out chunks → join → 1 grounded    K (codebase map-reduce)
   JURY-SELECT            N varied candidates → score → winner  I (altitude translation)
   SCATTER-ROUTE          N independent classifications, NO     M (typed-triage)
                          reduce — each routes to its own lane
   SCATTER-WRITE          N independent consolidations → sinks  B (background cognition)
```

Only **I (jury-select)** resembles the voice stream (it has a scoring/selection reduce). **K** reduces via `join`. **M and B have no reduce at all** — they fan out and route/write, never converging to one answer. This is the generative core: *the same six-piece primitive produces four structurally distinct cognition shapes*, and the THOUGHT_SHAPES registry must be expressive enough to declare all four. (Observed substrate for the shapes: doc 04 `THOUGHT_SHAPES` part-schema; doc 02 `join.py`/`gate.py`/`pair.py` for the reduce/branch primitives.)

Each target below also **forces a specific reshape** from B3 §4 (R1–R4) into the *build* — the connective tissue B3 left open:

| Target | Shape | Forces | Because |
|---|---|---|---|
| **K** codebase map-reduce | reduce-tree | `join` fan-in + (optional) **R1** jury | cross-chunk contradiction needs N varied draws |
| **I** altitude translation | jury-select | **R1** (candidate jury) + **I's learned-presentation scoring** | "pick the best presentation" needs >1 candidate |
| **M** typed-triage | scatter-route | **R3** typed-lane/channel sink | significance is *declared*; the role only classifies |
| **B** background cognition | scatter-write | **R4** activation-context budget + **R3** propose/surface sink | runs on idle VRAM, not a presence mode; never auto-writes |

---

## TARGET K · Codebase Map-Reduce — the *reduce-tree* shape

> **The field:** answer a question over a corpus too big for one context window (the self-hosting first-use reads the whole repo into one 600k-char read and fails loud past it — Observed, STATE.md / B3 §K). **The shape:** fan out N per-chunk reader-roles concurrently → fan-in (`join`) → one grounded answer. This is the highest reuse×unlock target (B3 §3.1): the node-graph *is* map-reduce.

### K.1 · The role-cast (IDs + what each reads/emits)

| role-id | reads (input_addresses) | emits (output_schema, abbreviated) | model-binding |
|---|---|---|---|
| `chunk_reader` *(fan-out, N instances)* | `$chunk` (one file/region, passthrough) + `$question` | `{file, summary, relevant_spans:[{lines, why}], answers_question:bool, confidence:enum[high,med,low]}` | resident 4B (fast, cheap, N-wide) |
| `cross_file_linker` | `run://<turn>/chunk_reader/*` (all chunk outputs, via `join`) | `{links:[{from_file, to_file, relation:enum[calls,imports,defines,contradicts,duplicates]}]}` | resident 4B |
| `contradiction_checker` *(R1 jury, draws:3)* | `join(chunk_reader/*)` | `{contradictions:[{claim_a, claim_b, files, severity}]}` + jury spread | resident 4B, 3 varied draws |
| `answer_grounder` *(the reduce head)* | `join(chunk_reader/*)` + `cross_file_linker` + `contradiction_checker` + `$question` | `{answer:str, cites:[{file, lines}], gaps:[str], confidence:enum}` | brain (the strong synthesiser) |

**What each instance of `chunk_reader` is:** the *same role row*, fired N times with a different `$chunk` arg. Each is independent → embarrassingly parallel → the vLLM batch absorbs them. Observed reuse: `nodes/ask.py` is already "a role over context" (two ports: `question`, `context`); `chunk_reader` is `ask` + a chunk-summariser system prompt + the structured `output_schema`.

### K.2 · The thought-shape (declarative, doc-04 grammar)

```python
THOUGHT_SHAPES["map_reduce_answer"] = {
    "label": "Map-reduce over a corpus → grounded answer",
    "archetype": "reduce-tree",                       # NET-NEW archetype tag (doc 04 had only linear)
    "modes": ("focus", "walkthrough"),                # a deliberate research turn, not chat
    "fanout": {"role": "chunk_reader", "over": "$chunks"},  # NET-NEW: a role fired once per element
    "parts": [
        {"id": "acknowledge", "deps": [], "intent": "One line: 'Reading <N> files…'", "may_act": False},
        {"id": "answer",
         "deps": ["join:chunk_reader/*", "role:cross_file_linker",
                  "role:contradiction_checker", "role:answer_grounder"],
         "intent": "Deliver the grounded answer with citations; name gaps honestly.",
         "may_act": True},                            # may call e.g. open-file / annotate verbs
        {"id": "offer", "deps": [], "offer": True,
         "intent": "Offer a follow-up: 'open <file>' / 'show the contradiction' as a suggest-proposal."},
    ],
}
```

The **`fanout`** field is the genuine net-new the reduce-tree needs (doc 04's part-schema names only fixed `deps`; a map-reduce part depends on *a variable-width set* `chunk_reader/*`). The `join:` dep-prefix is the fan-in primitive (`nodes/join.py`, Observed). A part with a `join:<role>/*` dep fires only when *all* fan-out instances resolve — the reduce barrier.

### K.3 · The routing rules (Batch-5 grammar: predicates over resolved values)

```
# R-K1 — escalate a chunk that needs a deeper read to the strong brain (chain a dependent role)
WHEN resolved("chunk_reader/<i>").confidence == "low"
     AND resolved("chunk_reader/<i>").answers_question == true
THEN chain role:deep_reader(chunk = chunk_of(<i>), model = "brain")   # composition: a 2nd-pass role

# R-K2 — surface a real contradiction even if the answer didn't need it (typed-lane destination)
WHEN any(resolved("contradiction_checker").contradictions, c => c.severity == "high")
THEN route → surface:lane="code-health"   # R3 typed-lane sink; the answer turn AND a standing record

# R-K3 — fail loud on a pruned chunk (no silent gap)
WHEN missing("chunk_reader/<i>")
THEN on_missing = "fail"   # a dropped chunk is a hole in the answer → never implicit-truthy (C9.3)
```

Note R-K1 is the Batch-5 discipline in action: "read this chunk again, deeper" is *heavier than a predicate*, so the rule does not embed it — it **chains an upstream role** (`deep_reader`), composition not code-in-a-rule.

### K.4 · Mode / activation-context

**Per-turn, in `focus` or `walkthrough`.** Map-reduce is a deliberate research turn (operator asks a question of the codebase), so it lives in the per-turn activation-context with a generous budget (`focus` here means deep-work-on-one-thing, not the terse chat brevity — the budget is `max_concurrent_roles` high because the fan-out *is* the point). **Variation (B/§K.5 below):** the same cast runs as a *background rollup* on a schedule with no operator turn — a standing code-health monitor.

### K.5 · Destinations + what a single model couldn't

**Destinations:** `answer_grounder` → `inject-into-reply` (the answer part). `contradiction_checker` → `surface:lane="code-health"` (R3 typed-lane). `cross_file_linker` → `land-at-address` `run://<turn>/links` (renderable as edges in the cognition view, G7).

**What concurrency+composition BUY (B3 §0 gate, applied sharply):**
1. **Bounded large-corpus reasoning.** A single 600k read fails loud at the ceiling (Observed). Map-reduce makes the corpus size irrelevant to the context window — N chunks read *in parallel*, reduced once. A *serial* map-reduce would work but take N× the wall-clock; concurrency is what makes it usable.
2. **Cross-chunk contradiction detection a single read structurally cannot do well.** A 600k single-context read *blurs* contradictions (attention dilutes across the window — the lost-in-the-middle failure). N focused chunk-reads each emit a sharp structured claim; the `contradiction_checker` *jury* (R1, 3 varied draws) then finds disagreements *between* chunks — a comparison a single blurred read cannot make. **This is the non-obvious unlock**: map-reduce isn't just "fits the window," it's *sharper per-chunk reasoning* → better cross-chunk synthesis.

**The non-obvious use it opens:** run the *same cast* on a schedule (K as a B-style rollup) → a **standing code-health monitor**: every night, fan-out over changed files, contradiction-check, and the high-severity contradictions land in `code-health` lane. The self-hosting repo *watches its own coherence*. (This is K∘B∘F composed — the application-space graph from B3 §5 made literal.)

---

## TARGET I · Altitude Translation — the *jury-select* shape (both directions)

> **The field:** the two-way transformation layer between Tim's altitude and the technical depths (feedback-altitude-transformation-layer — "big missing angle, high value"). **Up:** technical reality → Tim's words/shape. **Down:** Tim's intent → record-edits. **The shape:** generate N candidate renderings *concurrently*, score each against *learned presentation-preferences*, render the winner. This is the target that **requires R1** (you cannot pick the best presentation from one candidate).

### I.1 · The role-cast — UP-translation (technical → Tim)

| role-id | reads | emits | binding |
|---|---|---|---|
| `summarise_for_tim` | `$technical_payload` (the raw result/diff/state) + `ui://model-of-tim/digest` | `{plain_summary:str, omitted:[str], altitude:enum[surface,runtime,fabric]}` | brain |
| `pick_the_shape` *(R1 jury, draws:4)* | `$technical_payload` + `$summary` | `{shape:enum[tread-marks,table,canvas-overlay,prose,A/B/C/D-options], rationale:str}` | resident 4B, 4 varied draws → a *distribution of candidate shapes* |
| `draft_options` | `$summary` + `pick_the_shape` (winning shape) | `{options:[{label, body, recommendation:bool, why}]}` | brain |
| `score_presentation` *(the select head)* | `join:pick_the_shape/*` (all 4 jury draws) + `ui://presentation-prefs` (the LEARNED prefs) | `{chosen_shape, score, runner_up, why_chosen}` | resident 4B |

### I.2 · The role-cast — DOWN-translation (Tim → record-edits), the symmetric jury

| role-id | reads | emits | binding |
|---|---|---|---|
| `parse_intent` | `$tim_utterance` + `ui://current-locus` (where Tim IS — Observed `current_locus()`, doc 01 A7) | `{intent:enum[edit,create,run,ask,decide], target_address:str, fields:{}}` | resident 4B |
| `draft_edit` *(R1 jury, draws:3)* | `parse_intent` + `$locus_record` | 3 candidate `{address, field, new_value, reversible:bool}` edits | resident 4B, 3 draws |
| `verdict_edit` *(select head)* | `join:draft_edit/*` (the 3 candidates) | `{chosen_edit, agreement:float, ask_tim:bool}` | resident 4B |

**The jury IS the design here (R1):** for DOWN-translation, the *agreement* across draws is the trust signal. 3 draws agree → high confidence → propose the edit. 3 draws diverge → `ask_tim:true` → **surface a fork instead of guessing** (B3 §G: "variance is signal; disagreement = ask Tim"). This is exactly the per-draw-variation primitive R1 names — without it, a jury of identical prompts silently collapses to one cached answer (Observed gotcha, doc 02 §5d; `llm` not VOLATILE).

### I.3 · The thought-shape (UP-translation)

```python
THOUGHT_SHAPES["altitude_up_translate"] = {
    "label": "Translate a technical payload to Tim's altitude",
    "archetype": "jury-select",
    "modes": ("listening", "walkthrough"),
    "parts": [
        {"id": "acknowledge", "deps": [], "intent": "One beat: 'Here's what happened, in plain terms…'"},
        {"id": "render",
         "deps": ["role:summarise_for_tim", "role:score_presentation", "role:draft_options"],
         "intent": "Present at the CHOSEN shape (score_presentation.chosen_shape) — "
                   "if A/B/C/D, render the option-set; if tread-marks, render the temporal form.",
         "may_act": False, "render_from": "score_presentation.chosen_shape"},  # NET-NEW: render-hint is data-driven
    ],
}
```

The `render_from` field is the generative net-new: the *winning jury candidate selects the render form*. The cognition view (G7) and the canvas (reflects-never-owns) read `score_presentation.chosen_shape` and project the matching shape — the presentation form itself is an addressed, resolved value, not a hardcoded template (rule 3, one source).

### I.4 · The routing rules

```
# R-I1 — when the jury disagrees on shape, fall back to the safe default AND record the disagreement
WHEN resolved("score_presentation").score < PREF_THRESHOLD
THEN render_from = "prose"                              # safe default
     AND route → land-at-address: run://<turn>/presentation-uncertainty   # feeds the learning loop

# R-I2 — DOWN-translate: propose only on agreement; surface a fork on spread (R1 = the whole point)
WHEN resolved("verdict_edit").ask_tim == true
THEN route → surface:lane="decisions"  options=[draft_edit/0, draft_edit/1, draft_edit/2]
WHEN resolved("verdict_edit").agreement >= AGREEMENT_FLOOR
     AND resolved("verdict_edit").chosen_edit.reversible == true
THEN route → inject-into-reply (propose the edit as a suggest/proposal — operator one-click approves)
```

R-I2 encodes Tim's "offer multiple next-step options, never binary" instruction structurally: a disagreeing jury *becomes* the A/B/C/D option-set surfaced to decisions — the variance is the option-set. And it holds the governance floor: a non-reversible edit is *never* auto-proposed (C9.1 posture; reflects-never-owns — the role proposes, the operator resolves).

### I.5 · Mode / activation-context, destinations, what a single model couldn't

**Activation-context:** per-turn (it's the up/down translation of *every* operator interaction — the layer the whole system speaks through). Budget keyed on presence-mode (R4): `walkthrough` allows the full 4-draw jury; `listening` may run a 2-draw jury for speed.

**Destinations:** UP → `inject-into-reply` (the rendered part) + `land-at-address` (presentation-uncertainty → the learning loop). DOWN → `surface:lane="decisions"` (on disagreement) or `inject-into-reply` as a proposal (on agreement). **The learning loop** (the destination that makes I *learn*): `ui://presentation-prefs` is updated by a background-rollup role (B) reading which rendered shapes Tim *acted on vs reshaped* — closing F's introspective loop into I. Presentation-prefs is a *learned* address, the same prediction machinery as the twin (B3 §I).

**What concurrency+composition BUY:**
1. **You cannot pick the best presentation from one candidate.** Up-translation is a generative judgement with *many valid renderings*; "score the best" *requires* a candidate-set. One model call gives one rendering with no basis for "is this the right shape for Tim?" The jury *manufactures the choice set* that scoring needs. This is the textbook concurrency-for-quality use.
2. **Disagreement-as-signal is structurally impossible single-shot.** A single DOWN-translation guess either edits or doesn't — it has no way to express "this is a genuine fork." The jury's *spread* is the only place "ask Tim vs act" can come from. Without R1, the system either over-acts (guesses wrong, erodes trust) or under-acts (asks everything, annoying). The jury is what makes governed autonomy *calibrated*.

**The non-obvious use it opens:** the *same jury-select machinery* is the engine for **every "the system chooses how to behave" decision** — which persona/voice to use, whether to interrupt, how terse to be. Altitude translation generalises to a **behaviour-selection organ**: N candidate behaviours, scored against learned prefs, the winner enacted. I is not a feature, it's the system's *taste*.

---

## TARGET M · Typed-Triage Classification — the *scatter-route* shape

> **The field:** the collective-cognition triage law — significance is **DECLARED** in a typed event-registry (condition · lane · channel · urgency); the AI only *classifies* against it, never decides "is this important?" (Observed, project-collective-cognition; B3 §M). **The shape:** one classifier-role *per declared event-type*, fired concurrently against an arriving event — **no reduce**, each routes to its own lane. This is the **outbound reach organ** (the system contacts Tim) and it **requires R3** (the typed-lane/channel sink).

### M.1 · The role-cast — one classifier-role PER declared type (the registry generates the cast)

The cast is **not hand-written** — it is *generated from the typed-event-registry* (rule 8: author from the registry, never invent). For each declared event-type, a `classify_<type>` role:

| role-id (generated) | reads | emits | routes per its declared rule |
|---|---|---|---|
| `classify_decision_needed` | `$event` + `ui://model-of-tim/digest` | `{matches:bool, urgency:enum[now,soon,whenever], why}` | → `surface:lane="decisions"` channel=push if urgency=now |
| `classify_build_failed` | `$event` + `run://<event>/diff` | `{matches:bool, severity:enum, blocking:bool}` | → `surface:lane="errors"` channel=push if blocking |
| `classify_memory_worthy` | `$event` | `{matches:bool, salience:float, suggested_tags:[]}` | → `store:address="memory/inbox"` (inject-quietly, no ping) |
| `classify_stale_index` | `$event` | `{matches:bool, age_days:int}` | → `land-at-address run://rollup/stale` (background, silent) |
| `classify_reach_out` | `$event` + `ui://presence` | `{matches:bool, contact_now:bool, channel:enum[push,sms,voice]}` | → `surface:channel=<channel>` (the OUTBOUND flip) |

Every arriving event hits *all* classifiers **concurrently**. Each emits independently. There is **no `join`, no synthesis** — this is the scatter-route shape's signature: the fan-out *is* the whole computation, and each output routes to its own destination.

### M.2 · The thought-shape — scatter-route has no parts, only routes

```python
THOUGHT_SHAPES["scatter_route_triage"] = {
    "label": "Classify an arriving event against every declared type, route each result",
    "archetype": "scatter-route",
    "activation": "sense",                            # NOT a presence-mode turn — an event trigger (R4)
    "fanout": {"role": "classify_*", "over": "$event"},  # ALL classifier-roles fire on the one event
    "reduce": None,                                   # the signature of scatter-route: NO reduce
    "routes": "per-role declared-rule",               # each role's own routing rule fires independently
}
```

There are no `parts` because triage produces no *reply* — it produces *routings*. This is the structural proof that M is not a voice-stream variant: the staged-output shape here is "N independent classifications, each to its own sink," fundamentally unlike a linear stream.

### M.3 · The routing rules — declared significance, the role only classifies (Batch-5 grammar)

```
# R-M1 — the urgency gate IS the declared significance (NOT a model judging "is this important?")
WHEN resolved("classify_decision_needed").matches == true
     AND resolved("classify_decision_needed").urgency == "now"
THEN route → surface:lane="decisions" channel="push"

# R-M2 — quiet injection: memory-worthy but never pings (kills "annoying" structurally)
WHEN resolved("classify_memory_worthy").matches == true
     AND resolved("classify_memory_worthy").salience >= SALIENCE_FLOOR
THEN route → store:address="memory/inbox"   # land it; do NOT contact Tim

# R-M3 — the OUTBOUND reach, governed: only a declared-fireable type may reach out
WHEN resolved("classify_reach_out").contact_now == true
     AND resolved("classify_reach_out").channel ∈ DECLARED_CHANNELS   # can ONLY fire what's declared
THEN route → surface:channel=resolved("classify_reach_out").channel
```

**The "kills annoying" mechanism made structural (B3 §M):** the system can *only* contact Tim through a channel that is *declared fireable in the typed registry*. There is no path for a role to invent an interruption. Significance is the registry's, classification is the role's, the contact is gated by a declared channel — three separations that make over-contact *impossible by construction*, not by good behaviour. This is R3's typed-lane/channel sink doing exactly what B3 said it must.

### M.4 · Mode / activation-context

**Sense-triggered activation-context (R4), not a presence mode.** M fires on *event arrival* (an inbox item, a build event, a state change), not on an operator turn. This is precisely why R4 matters: M's budget has no home in the eight presence-modes — it lives in the *sense* activation-context with its own cheap-and-fast budget (a classifier-sweep must be light; it runs on *every* event). The mode still *modulates* it (in `off`/`focus`, the reach-out classifier is suppressed — don't interrupt deep work), but the *activation* is the event, not the turn.

### M.5 · Destinations + what a single model couldn't

**Destinations (all of R3's kinds, exercised):** `surface:lane` (decisions/errors), `surface:channel` (the outbound push/sms/voice — the reach organ), `store:address` (quiet memory inject), `land-at-address` (silent rollup feed). M is the application that *exercises every destination kind*, which is why B3-R3 surfaced it as the load-bearing one.

**What concurrency+composition BUY:**
1. **Classify against many types at once, as events arrive.** A *serial* classifier would check types one at a time → latency scales with the type-count → events queue up. Concurrency makes triage *O(1) in wall-clock* regardless of how many declared types exist — and the type-registry *grows*, so this matters more over time.
2. **The fan-out-without-reduce is the unlock a single model structurally lacks.** A single "is this important and what should I do?" call *conflates* significance-judgement with action-choice — exactly the conflation the triage law forbids. The scatter shape *separates* them: each classifier judges *one* declared dimension, routes *independently*; significance stays declared. A single model can't be made to *not* conflate — the architecture has to enforce it. **M is the case where the shape itself is the governance.**

**The non-obvious use it opens:** the same scatter-route engine is the **universal inbound router** for the whole Company — every channel-event, every decision, every error, every external webhook hits the classifier-sweep and lands in its declared lane. M generalises from "triage" to **the system's entire afferent nervous system** (the *senses* feed it via J; it feeds the *reach* outbound). It is the cognition-meets-reach organ B3 named — and it's the same six pieces.

---

## TARGET B · Background Cognition — the *scatter-write* shape

> **The field:** the swarm when no one is talking — consolidation/learning that runs on idle VRAM (collective-cognition activation-spectrum §2.5; B3 §B). **The shape:** N independent consolidation roles fan out over the day's substrate → each *writes* to a sink — **no reduce, and crucially no reply** (it's not a turn). **Requires R4** (it's an activation-context, not a presence mode) **and R3** (the propose/surface sink — it never auto-writes; reflects-never-owns).

### B.1 · The role-cast — consolidation roles, each writing knowledge

| role-id | reads (over the day's substrate) | emits | sink (destination) |
|---|---|---|---|
| `thread_summariser` | `run://events/since/<last_rollup>` (threads touched) | `{thread_id, summary, key_decisions:[], open_loops:[]}` | `store:address="rollup/thread/<id>"` (write — own telemetry) |
| `gold_extractor` | the day's chat turns | `{turn_id, gold_grade:enum, why, twin_worthy:bool}` | `surface:lane="twin-corpus"` (PROPOSE — never auto-writes the twin) |
| `skill_registrar` | recurring resolutions in events | `{pattern, occurrences:int, propose_faculty:bool}` | `surface:lane="faculties"` (PROPOSE a new automaticity) |
| `stale_index_detector` | index timestamps vs source mtimes | `{index, stale:bool, age_days}` | `land-at-address run://rollup/stale` + `surface` if blocking |
| `pref_learner` *(closes I's loop)* | `run://*/presentation-uncertainty` + which shapes Tim acted on | `{shape, acted:bool, reshaped:bool}` → updated weights | `store:address="ui://presentation-prefs"` (the learned address I reads) |
| `cost_correlator` *(F overlap)* | `run_stats` op-records | `{condition, p95_ms, anomaly:bool}` | `store:address="rollup/gotchas"` |

Each role is independent (no role reads another's output) → pure scatter → the whole day's consolidation finishes in the wall-clock of *one* pass. This is B3's "consolidation is embarrassingly parallel" made into a concrete cast.

### B.2 · The thought-shape — scatter-write: fan out, write, no reply

```python
THOUGHT_SHAPES["scatter_write_consolidate"] = {
    "label": "Idle-time consolidation over the day's substrate",
    "archetype": "scatter-write",
    "activation": "background",                       # R4: an activation-context, NOT a presence mode
    "trigger": {"event": "rollup.tick", "predicate": "lambda ctx: ctx['idle'] and ctx['model_resident']"},
    "fanout": {"roles": ["thread_summariser", "gold_extractor", "skill_registrar",
                         "stale_index_detector", "pref_learner", "cost_correlator"], "over": "$substrate_slice"},
    "reduce": None, "parts": None,                    # no reply — it WRITES, it doesn't answer
    "budget": "activation:background",                # R4: the background budget, generous (idle VRAM)
}
```

`parts: None` *and* `reduce: None` is the scatter-write signature — distinct from M's scatter-route (M *routes* classifications to lanes/channels; B *writes* consolidations to stores/proposals). Both lack a reduce; they differ in destination-kind (route-to-lane vs write-to-store/propose).

### B.3 · The routing rules — propose, never auto-write (reflects-never-owns)

```
# R-B1 — gold-grade turns are PROPOSED to the twin corpus, never written (R3 propose/surface sink)
WHEN resolved("gold_extractor").twin_worthy == true
     AND resolved("gold_extractor").gold_grade == "high"
THEN route → surface:lane="twin-corpus"   # a PROPOSAL the operator reviews — the twin is sacred, never auto-fed

# R-B2 — a recurring resolution becomes a PROPOSED faculty (automaticity), operator approves
WHEN resolved("skill_registrar").occurrences >= FACULTY_FLOOR
     AND resolved("skill_registrar").propose_faculty == true
THEN route → surface:lane="faculties"

# R-B3 — own-telemetry writes ARE allowed direct (the swarm's own run-records, introspective-data law)
WHEN resolved("thread_summariser").thread_id != null
THEN route → store:address="rollup/thread/<id>"   # writing the system's OWN record is not owning Tim's truth
```

The R3 distinction made sharp: **writing the system's own telemetry/rollup is a direct `store` write; writing anything that becomes the operator's truth (the twin corpus, a faculty, a memory) is a `surface` PROPOSAL.** B is the application that forces the propose/surface sink to be a *distinct destination kind* from write — exactly B3-R3's finding.

> **The propose path is not the *only* path (locked: DECISIONS Batch-3 Q3).** Reflects-never-owns governs *operator-truth* sinks (twin/faculty/memory → always propose). But in *permitted* modes (e.g. `decide-for-me`), a role MAY act on reversible/AUTO-class verbs through the existing governance posture — so a low-risk reversible consolidation could route `inject`/act directly, not only `surface`. The bright line is **risk-class + posture (governed), never "roles can't act"**; the floor that never moves is autonomous build-dispatch / `claude -p` (lead-only, C9.2). So: operator-truth → propose; reversible/AUTO in a permitted mode → may act; build-dispatch → never.

### B.4 · Mode / activation-context

**Background activation-context (R4), the canonical case.** B is *why* R4 exists: it is not a presence mode (no one is present), it's a *scheduled/idle* activation with its own budget. The budget is *generous* — idle VRAM is wasted attention (B3 §B), so background can run the full 6-role cast wide and even (Batch-2 Q3) run roles on the *cloud* brain in the background (the resident swarm ⟂ cloud-background, DECISIONS Batch-2). The trigger is `rollup.tick` + an idle+resident predicate (C5.4); fail-loud + offer-to-load if the model isn't up (C8.4).

### B.5 · Destinations + what a single model couldn't

**Destinations:** `store:address` (own rollups — direct), `surface:lane` (twin-corpus / faculties — proposals), `land-at-address` (stale-index feed). B writes *across all six introspective streams* (cognition · decisions · surface-usage · errors · twin · cost — B3 §F), one role per stream.

**What concurrency+composition BUY:**
1. **The consolidation keeps up with a compounding corpus only if parallel.** As the substrate grows, a serial nightly pass falls behind (the day's events outpace one-at-a-time analysis). N concurrent consolidations finish in one pass's time — the system's *learning rate keeps pace with its usage rate*. This is the compounding-value claim B3 §5 makes: F closes the loop, and B is where it runs.
2. **The system thinks when attention is idle — a thing a single on-demand model never does.** A single model only runs when called. The *scatter-write on a schedule* is what turns "idle VRAM" into "sleep" — the system consolidates, learns presentation-prefs (closing I's loop), proposes faculties (growing M's classifiers and the role-cast itself). **B is the application that makes the whole mechanism's value compound while no one is using it** — the single most under-appreciated reuse (B3 §3.5).

**The non-obvious use it opens:** B is the *generator of the other three targets' inputs* — `pref_learner` feeds I's `presentation-prefs`; `skill_registrar` proposes new M classifiers; `gold_extractor` feeds the twin that I/M both read; K-as-rollup is itself a B-scheduled cast. **Background cognition is the recursion's heartbeat**: it's where use→record→knowledge→better-use (the introspective-data law) actually *runs*. The four targets aren't four features — B is the one that makes the other three *improve themselves over time*.

---

## 5 · The four as one organ (the relational read)

These four are not four builds — they are **the same six-piece primitive pointed at four fields, exercising four shapes, forcing four reshapes**, and they *compose into each other*:

```
   M (scatter-route) ── senses/events in ──┐
   the afferent nerve                      ▼
                              B (scatter-write) ── runs on idle VRAM ──┐
                              the heartbeat                            │ feeds
                                   │ proposes new M-classifiers,       │ presentation-prefs,
                                   │ twin-corpus, faculties            │ twin, gotchas
                                   ▼                                   ▼
   K (reduce-tree) ── grounded answers ──▶ I (jury-select) ── chooses how to show Tim
   the deep read         feed the answer    the taste/behaviour-selection organ
                                   │                                   │
                                   └──── everything emits run-records ─┘
                                         ──▶ B's cost_correlator/F rollup ──▶ knowledge ──▶ all four get smarter
```

Read relationally (Tim's law):
- **M is the afferent nerve** (events → classified → routed), **B is the heartbeat** (idle consolidation that grows the others), **K is the deep read** (corpus → grounded answer), **I is the taste** (how any of it reaches Tim).
- **The shapes are the generative yield:** linear-stream (A) · reduce-tree (K) · jury-select (I) · scatter-route (M) · scatter-write (B) — *five archetypes the THOUGHT_SHAPES registry must carry*, named here so the registry is built once for all of them, not retrofitted per target.
- **Each forces its reshape into the build:** K→`join`+fanout · I→R1 jury+learned-scoring · M→R3 typed-channel · B→R4 activation-context+R3 propose-sink. Building the four *is* building R1–R4 into the substrate — the reshapes are not optional folds, they are *load-bearing for these targets*.
- **F (rollup) closes the loop through B:** every target self-instruments, B's consolidation turns that into knowledge, which improves every target. The "limitless" is concrete: the mechanism is field-agnostic, adding a field is adding role-rows (one source), and B means each new field makes the others smarter.

**The sequencing finding (a recommendation, not a decision):** build the *archetypes* in this order, because each is a strictly larger demand on the substrate:
1. **K first** (reduce-tree) — highest reuse (the node-graph IS map-reduce), serves self-hosting, proves `join`/fanout + R1-optional. The natural second proving target after voice (B3 §3.1).
2. **M next** (scatter-route) — proves R3's typed-channel sink + the sense activation-context; unlocks the reach organ; no reduce to get right.
3. **B next** (scatter-write) — proves R4's activation-budget + the propose/surface sink; depends on M's classifiers existing to propose more of them; turns idle VRAM into compounding value.
4. **I last** (jury-select) — needs R1, and is *fully realized* once *B's `pref_learner` feeds `presentation-prefs`*; it **bootstraps with default prefs** and improves as B runs (not a hard block — it degrades gracefully to the safe-default shape, R-I1). It is the hardest (taste is the hardest thing to verify — `needs-tim` heavy) and the most valuable (it's what makes the system operable by Tim *specifically*).

---

## 6 · Open questions to put to Tim (don't decide silently)

- **The five archetypes (the core finding):** confirm THOUGHT_SHAPES carries `reduce-tree · jury-select · scatter-route · scatter-write` alongside `linear-stream` — built once, up front — vs growing them per-target. (Building once is the rule-3 / "full substrate now" instinct, DECISIONS Q3.)
- **The `fanout` field:** a part depending on a *variable-width* role-set (`chunk_reader/*`, `classify_*`) is net-new beyond doc 04's fixed `deps`. Add `fanout` + the `join:<role>/*` barrier-dep to the part-schema now (K and M both need it), or design per-target?
- **Sequencing:** K → M → B → I as above (each a larger substrate demand, I depends on B's learned prefs), or a different order? (K is the strongest second-target candidate independent of order.)
- **The propose-vs-write line (R3, sharpened by B):** confirm the rule — *own telemetry/rollup = direct `store` write; anything that becomes the operator's truth (twin/faculty/memory) = `surface` proposal, reflects-never-owns*. Is that the bright line for every target?
- **M as the universal inbound router:** is the typed-triage scatter meant to be the system's *entire* afferent nerve (every event-kind, every channel), or scoped to a specific event-set first?
- **I as the behaviour-selection organ:** does the jury-select generalise past presentation to *all* "how should the system behave" choices (persona, interrupt, terseness), or stay scoped to up/down translation?
- **B's cloud-background:** confirm background roles may run on the cloud brain (DECISIONS Batch-2 Q3) while the resident swarm serves live turns — and what the cost-governance on that is.

---

## 7 · Sources

- **This series (Observed by read):** `00-LANDSCAPE.md`, `01-role-registry.md` (the role schema + `run_role` + the `run://` addressing + destinations + render-hint), `02-graph-substrate-reuse.md` (`join`/`gate`/`pair`, the memo/VOLATILE gotcha that R1 fixes, the `running` node-state), `04-staged-response-queue.md` (the `THOUGHT_SHAPES` registry + part-schema + `deps`/`intent`/`may_act`/`offer` + MODE_BUDGETS), `broader/B3-broader-applications.md` (the 15-use map; K=§K, I=§I, M=§M, B=§B; the R1–R4 reshapes; the §0 quality gate applied per-target above), `broader/00-BROADER-LANDSCAPE.md` (the deltas).
- **Locked decisions (DECISIONS.md):** L1 registry-driven · L2 rule-based-routing (the Batch-5 grammar all rules above use: predicates over resolved values, composition for anything heavier) · Batch-2 Q4 (the four targets) · Batch-3 Q4 (the five destinations) · Batch-4 (jury first-class = R1; live view in first build) · Batch-5 (rich predicates + composition, restricted AST, `on_missing` fail-loud).
- **Company goals (memory, point-in-time):** project-collective-cognition (activation-contexts; budget=attention; the triage law M implements; the senses feeding M), feedback-altitude-transformation-layer (the off-list I, "big missing angle"), project-introspective-data-building (the write-half B runs; F closing the loop), feedback-autonomous-spawn-lead-only (the floor: a role classifies/proposes, never dispatches — holds across all four).
- **Governing rules:** rule 3 (one source — add a role-row/shape-row, not a system), rule 4 (fail loud — every `on_missing`/down-model above), rule 8 (author from the registry — M's cast is *generated* from the typed registry), rule 9 (navigable visual surface — the cognition view renders all four shapes). All four targets inherit them.
