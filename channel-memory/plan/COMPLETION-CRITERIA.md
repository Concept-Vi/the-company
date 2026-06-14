# Completion Criteria — Session Recall, Lenses, Synthesis & Channel-Context

```
trust: fabric-derived (the plan); answers to open questions are INFERRED-from-Tim proposals (see INFERRED-PREFERENCES.md) for his reaction
author: ch-8djrpmsl / 11e7d395 (fork) — with lead ch-al7jdfdr on the joint lanes
date: 2026-06-14
verified: criteria status marked per-item (Verified / Designed / Broken); FORM faces pending the projection surface
```
> The check-back artifact Tim asked for: "a full design and plan for everything, so you can check back against it when you complete things and make sure you get everything." Covers his whole vision ([[2026-06-14-session-splicing-and-channel-memory]]) + today's threads. Per loop-prep. Companion docs: IMPLEMENTATION-GUIDE.md (how), RESEARCH-SYNTHESIS.md (what exists), INFERRED-PREFERENCES.md (proposed answers to open questions — Tim reacts to that one).

## Verification rules (BOTH bars, or it is not done)
- **FUNCTION** — the behaviour is real and verified BY USE (run it, see the result), no stub, no silent fallback. Code-reading is not verification.
- **FORM** — for any operator-facing surface: the data is rendered as a **projection of addressed state** in the Company UI (The Heart), built on the design system, a *navigable visual/spatial surface* (Tim recognises by sight, not by reading a text-wall), responsive, coherent. Form is half of done; a recall result that is correct but only a JSON dump is FUNCTION-only = NOT done for any surface criterion.
- Status tags: **[V]erified** (by use) · **[D]esigned** (specced, not built/verified) · **[B]roken** (exists, wrong) · **[P]ending-joint** (needs the lead/recollection fork).

---

## Group 1 — Dimension-aware chunking  (FOUNDATION — everything rests on it)
- **1.1 Structure-aware split** — long turns split on their OWN structure (paragraphs, line-by-line dimension shifts), NOT a fixed char window, so a multi-dimensional message (esp. Tim's) keeps each dimension as a retrievable unit.
  - FUNCTION: [D] a dense N-dimension message indexes as ~N facets, each retrievable; a query matching one dimension surfaces it. (Today: fixed 700-char overlap split [V] — works, but not dimension-aware.)
  - FORM: n/a (substrate) — but its OUTPUT feeds projectable rows (Group 7).
- **1.2 Parent-handle preserved** — every sub-chunk carries its parent message's line/ts/attribution; a hit on one dimension can surface the whole message. FUNCTION: [V] (sub-chunks carry line/ts/attr today).
- **1.3 Tim-message priority** — Tim's turns get the most careful dimension-aware treatment (his are longest/densest/multidimensional — his words). FUNCTION: [D].

## Group 2 — Recall substrate  (FOUNDATION)
- **2.1 Embed bridge-free** — chunks embed via the Company-served :8007 (pplx-4b, documents-mode, 2560-d cosine); NO overlord venv bridge. FUNCTION: [V].
- **2.2 Rerank served** — rerank via the Company-served :8008 (jina-v3, CPU); kept as its OWN capability (raw search+rerank stays available, per Tim). FUNCTION: [V] (pool=12 tuned for CPU).
- **2.3 Fail-loud** — embedder/reranker down ⇒ teaching error + declared degradation in the envelope; never silent empty / silent fallback. FUNCTION: [V].
- **2.4 Freshness guard** — a build-once index on a LIVE (growing) session is stale; recall must detect staleness (source mtime/size vs index) and rebuild or warn. FUNCTION: [D] (today: build-once, stale-on-live — the advisor's flag). Fine for stable past sessions; REQUIRED before live-session recall.

## Group 3 — Lenses  (the family of useful views; reuse the substrate)
- **3.1 find(q)** — general semantic recall. FUNCTION: [V].
- **3.2 decisions(topic)** — surfaces the decision; choice + reason recoverable for pointed queries. FUNCTION: [V] for pointed queries (choice→L4257, reason→L4296); [D] one-call pinpoint of the reason-turn for a GENERIC topic — needs Group 4 (synthesize over the region). Honest limit, characterized.
- **3.3 open_loops()** — unresolved threads (blockers/gaps/Tim-questions), latest-first, resolution-hint. FUNCTION: [V] (12 of 117 on the lead session).
- **3.4 catch_up(since)** — what happened since the last away-gap. FUNCTION: [V].
- **3.5 timeline(topic)** — a topic's arc over the session, by time. FUNCTION: [V].
- **3.6 directives()** — every genuine Tim ask, chronological (whole-slate ledger). FUNCTION: [V] (144 turns).
- **3.7 requirements/preferences (ANTI-RECENCY)** — extract Tim's standing requirements + preferences + IMPLICIT signals across the WHOLE session, weighted by importance/repetition NOT recency; PRIMARY source = the cross-session preference-memory (`feedback-*`), session-recall as supplement. FUNCTION: [D] — the keystone new lens; also the payload for Group 5.
- **3.8 spin-up-choosing** — rank §1.5 fork-points by context-state (decision-density, expertise-crystallization, hot-open-threads, novelty-vs-compaction-summary) → an evidenced fork-point surface. FUNCTION: [D].

## Group 4 — Retrieve-then-synthesize panel  (Tim's "panels"; extraction-vs-judgment)
- **4.1 Search kept separate** — the synthesis is an ADDITIONAL capability; raw search+rerank (Groups 2/3) remain independently usable. FUNCTION: [D] (constraint).
- **4.2 Concurrent structured extractors** — small models, each ASSIGNED one facet, emit STRUCTURED OUTPUT, run concurrently; small models NEVER asked to judge/reason (extraction-vs-judgment law). FUNCTION: [D] [P] (model loadout = lead's lane).
- **4.3 Facet schema** — the facets are a registry of facet-types (proposed FIXED+extensible — see INFERRED-PREFERENCES Q1). FUNCTION: [D].
- **4.4 Smart-model judge** — a single capable model assembles the brief from the chained structured extractions (the only judgment step). FUNCTION: [D].
- **4.5 decision_brief(topic)** — end-to-end: retrieve region → extract facets → judge → "we chose X over Y because Z, at L####." FUNCTION: [D] — closes the Group-3.2 generic-pinpoint gap.
  - FORM: [D] the brief renders as a projected card (Group 7), not a JSON dump.

## Group 5 — Channel-context  (attach sessions + docs to channels; load as rules) — [P] joint with lead
- **5.1 Channel context-manifest** — a channel carries a manifest of attached sources (sessions — indexed or spun-up — + documentation). FUNCTION: [D] [P].
- **5.2 Load-on-join** — an agent that becomes a channel member loads the manifest as rules/context (like `~/.vi/rules/*.md` auto-load). FUNCTION: [D] [P].
- **5.3 Preference payload** — the Group-3.7 requirements/preferences profile is part of what loads (so members inherit "how Tim works" + the channel's standing context). FUNCTION: [D].
- **5.4 On-demand recall in-channel** — members can recall against the channel's attached sources (Groups 3/4) live. FUNCTION: [D].

## Group 6 — Multi-project / multi-session model  — [P] joint with lead; GATES fleet indexing
- **6.1 Addressing scheme** — sessions across projects (`~/.claude/projects/<enc-cwd>/<sid>`) addressable in one scheme (registry-based, The Heart). FUNCTION: [D] [P].
- **6.2 Index scoping** — indexing handles many sessions × many projects without collision; index location/naming scheme settled. FUNCTION: [D] [P].
- **6.3 Worked out BEFORE fleet indexing** — Tim's hard gate: do NOT index more sessions until 6.1/6.2 are settled with the lead. STATUS: [P] — blocking.

## Group 7 — Projection  (the data → Company UI; FORM-bearing) — from vision §1.9
- **7.1 Scan/recall as projectable data** — scan rows + lens outputs + the lineage map are DATA (rows/json), registered as a SOURCE, so the UI projects them — not bespoke UI code. FUNCTION: [V] (data shape exists); registration [TIM-GATED].
- **7.2 The projection renders** — the analytics (lineage, scan profile, lenses, briefs) appear in the Company UI as a projection of addressed state.
  - FUNCTION: [D] [FAR] — needs Tim to point to the UI-building sessions (vision §1.10).
  - FORM: [D] navigable visual/spatial surface (timeline, density, the dense-message profile), design-system-built, not a text-wall.

## Group 8 — Spin-up / fork-fleet  — [TIM-GATED] (from vision §1.5)
- **8.1 Fork-points mapped** — candidate points with cut/position/context + readiness. FUNCTION: [V] (channel-memory/map/fork-points.md).
- **8.2 uuid-cut probe** — prove a mid-conversation (non-boundary) cut resumes cleanly (one probe clone). FUNCTION: [D] (reversible; not yet run).
- **8.3 Fleet launch** — launch chosen points into the channel. STATUS: [TIM-GATED] (his go + perms).

---

## Priority order (dependency-first)
1. **Group 6** (multi-project model) — [P] gates indexing; settle with lead FIRST.
2. **Group 1** (dimension-aware chunking) — everything's quality rests on it.
3. **Group 2/3** (substrate + lenses) — mostly [V]; add 2.4 freshness + 3.7 preferences + 3.8 spin-up.
4. **Group 4** (synthesis panel) — needs lead's model loadout; closes the decisions gap.
5. **Group 5** (channel-context) — [P] joint; the integration target.
6. **Group 7** (projection) — [FAR]; needs Tim's UI-session pointer.
7. **Group 8** (fork-fleet) — [TIM-GATED].

## Check-back protocol
When any item is completed, verify BOTH faces by use, flip [D]→[V] here with the evidence (line/command/screenshot), and confirm nothing in its group's "what's preserved" list regressed. Nothing is done until its FORM face is also green (for surface items). This file is the single source of "what must be true" — re-read it before claiming any part done.
