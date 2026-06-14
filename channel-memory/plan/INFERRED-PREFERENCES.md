# Inferred-Preference Proposals — answers to the open questions, FOR TIM TO REACT TO

```
trust: fabric-derived — these are PROPOSED answers inferred from Tim's stated preferences + session signals, NOT his direct words. He reacts.
author: ch-8djrpmsl / 11e7d395 (fork)
date: 2026-06-14
method: get-a-feel-for-Tim — primary source the cross-session preference-memory (feedback-* corpus, anti-recency by construction), supplemented by this session's Tim-turns. (Dogfooding the very capability being designed.)
```
> Tim's instruction: "look through the session history not just for decisions but get a feel for me, suggest what I'd probably like / would appreciate, bring it back, I'll respond." Each proposal carries the EVIDENCE it's grounded in + a confidence + a one-line react prompt. **Tim: skim the react lines; agree / adjust / reject any.**

---

### The get-a-feel profile (what the substrate says you value — the lens we're building, run on you)
Distilled from the `feedback-*` memory corpus + this session. The standing constants (high-confidence, repeatedly signalled): **reasoning visible in the message** ([[reasoning-in-messages]]) · **whole slates, no deferral, no MVP-filtering** ([[deliver-whole-slates]], [[no-deferral]], [[no-mvp-prioritization]]) · **record/expand, never summarize-down** ([[record-expansively]], [[maximal-capture]]) · **fail loud, no silent fallback** ([[no-silent-failures]]) · **evidence over speculation; structure/execution over text-trust** (the triply-confirmed law today) · **render for cognition — navigable visual/spatial, not text-walls** ([[render-for-cognition]]) · **make each thing actually work, don't substitute** ([[make-each-thing-work]]) · **registries-with-types, dataflow + structured-output by default, not agent-architecture** ([[the-heart]], [[not-agent-architecture-by-default]]) · **the Company's own corpus+embedding memory, not external memory** ([[no-episodic-memory]]) · **recency bias frustrates you** (stated today) — so anti-recency is a first-class requirement, not a nicety.

---

## Q1 — Synthesis panel: FIXED facet-schema or DYNAMIC?
**PROPOSED: FIXED facet-schema, as an extensible REGISTRY of facet-types** (chosen / alternatives / reason / constraints / owner / …; add a row to extend).
- **Evidence:** [[the-heart]] (fractal registries + typed edges) · [[extraction-vs-judgment]] (small models EXTRACT to a known shape; the centre judges) · [[not-agent-architecture-by-default]] + [[reference-vllm-structured-output]] (enforced json_schema, dataflow not agent) · "make it projectable" (a fixed schema projects cleanly).
- **Why fixed over dynamic:** dynamic facets push judgment INTO the small models (asking them what to extract) — exactly what you said they're bad at. Fixed roles keep them as pure structured extractors; the registry stays extensible so it's not rigid.
- **Confidence: HIGH.** *React: fixed-extensible-registry ✓ / want dynamic / mix?*

## Q2 — Chunking strategy
**PROPOSED: DIMENSION-AWARE — split on your message's own structure (paragraphs, the line-by-line dimension shifts), each dimension a retrievable facet, parent-message handle preserved.**
- **Evidence:** CLAUDE.md "Dense Messages — process LINE BY LINE, each line implies connections" · [[dense-transmission-protocol]] · your words today ("my messages are very long and very dense and multidimensional").
- **Confidence: HIGH.** *React: dimension-aware ✓ / different cut?*

## Q3 — "Get a feel for me": what's the source?
**PROPOSED: PRIMARY = the cross-session preference-memory (`feedback-*` corpus) — it's distilled across many sessions, so it's anti-recency BY CONSTRUCTION; SUPPLEMENT = session-recall filtered to your turns, importance-weighted.**
- **Evidence:** today's single-session recall was polluted by recent fabric chatter (proof recency/noise hurts) · [[no-episodic-memory]] (the Company's own corpus+embedding memory is the substrate) · your recency-bias frustration.
- **Implication:** the anti-recency requirements/preferences lens (Group 3.7) reads the standing memory FIRST, then layers session signal. The profile becomes the channel-load payload (Group 5.3).
- **Confidence: HIGH.** *React: memory-primary + session-supplement ✓ / weight differently?*

## Q4 — Attaching sessions + docs to channels: the mechanism
**PROPOSED: a per-channel context-MANIFEST (a registry entry listing attached sources: sessions [indexed or spun-up] + documentation + the preference profile); an agent loads it ON JOIN as rules/context — riding the existing `~/.vi/rules` auto-load + the source registry, NOT a parallel system.**
- **Evidence:** [[the-heart]] + [[session-fabric-registry-frame]] (the fabric IS registries) · `~/.vi/CLAUDE.md`/`rules/*.md` already auto-load to every session (the load-on-join precedent) · loop-prep principle 2 / [[flag-hardcoding]] (don't build parallel systems).
- **Confidence: MEDIUM** (joint with the lead — channels are their lane). *React: manifest-rides-registry+rules ✓ / different shape?*

## Q5 — Multi-project / multi-session addressing
**PROPOSED: registry-based addressing — each (project, session) is an addressed entry in the fractal registry; the concrete scheme deferred to the LEAD (their lane; you flagged you mentioned it to them). GATES indexing more sessions.**
- **Evidence:** [[the-heart]], [[session-fabric-registry-frame]] · your explicit "work it out with the lead before indexing more."
- **Confidence: LOW** (lead owns the scheme). *React: registry-addressed, lead-led ✓?*

## Q6 — Choosing spin-up points
**PROPOSED: rank candidate fork-points by an EVIDENCED context-state score (decision-density, where a distinct expertise crystallized, hot-open-threads, novelty-vs-the-compaction-summary) — a navigable ranked surface, not my hand-picked six.**
- **Evidence:** [[render-for-cognition]] (your perception is the compute — give you a surface to see) · [[patterned-visibility]] · [[gap-pressure]].
- **Confidence: MEDIUM.** *React: evidenced ranked surface ✓ / which signals matter most to you?*

## Q7 — The decisions-lens generic-pinpoint gap
**PROPOSED: solve it via the synthesis panel (Q1/Group 4) — retrieve the decision REGION (which works) then extract+judge the brief — NOT by forcing one chunk to rank #1 (which fights the embedding).**
- **Evidence:** [[make-each-thing-work]] · extraction-vs-judgment · today's finding (the reason-turn L4335 is diluted across 5 topics; retrieval surfaces the region, synthesis distills it).
- **Confidence: HIGH.** *React: synthesize-the-region ✓?*

---

## Already locked by your direct words (not inferred — listed so the plan is complete)
- Retrieve-then-synthesize is **additive**; raw search+rerank **stays** a capability. (Your words.)
- Small models: **concurrency + assignment + structured output + chaining only — never judgment/reasoning**; the smart model judges. (Your words = [[extraction-vs-judgment]].)
- **Coordinate the multi-project model with the lead BEFORE indexing more sessions.** (Your words.)
- Bridge-free: Company-served endpoints, **no overlord venv bridge**. (Your earlier direction.)

*Tim — react to the Q lines (agree/adjust/reject); anything you change, we update the plan and proceed. Anything you don't touch, we build to the proposal.*
