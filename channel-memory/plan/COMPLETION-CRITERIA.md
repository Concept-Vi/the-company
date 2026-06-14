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

## Group 4 — Retrieve-then-synthesize panel  (Tim's "panels"; extraction-vs-judgment)  [CONVERGED with lead §D]
> Build ON `runtime/cognition.py` — VERIFIED (lead §D): it already has `run_role(role,ctx)` + concurrency (ThreadPoolExecutor) + structured output (`json=True`→response_format), and `roles/` already splits extract-roles (mine_exchange/eval_classify/ground/interpret_file) vs judge-roles (judge/judge_mining/judge_drift). So the panel = NEW roles + a chain, NOT new infra. Models: chat-4b(:8000, 32-concurrency) · chat-2b(:8003) · chat-08b(:8006) extract; chat-nemotron-30B(:8005) or a cloud seat judges.
- **4.1 Search kept separate** — the synthesis is an ADDITIONAL capability; raw search+rerank (Groups 2/3) remain independently usable. FUNCTION: [D] (Tim-direct constraint).
- **4.2 Concurrent structured extractors** — NEW facet-extract roles (`roles/*.py`), each ASSIGNED one facet, `json=True` structured output, fired concurrently via `run_role`/`run_swarm` on chat-4b/08b; NEVER judge/reason (extraction-vs-judgment law). FUNCTION: [D].
- **4.3 Facet schema** — fixed+extensible registry of facet-types (chosen/alternatives/reason/constraints/owner — INFERRED-PREFERENCES Q1, confirmed by lead). FUNCTION: [D].
- **4.4 Smart-model judge** — one `run_role(<judge role>)` on a smarter seat (chat-nemotron-30B/cloud) assembles the brief from the chained structured extractions (the only judgment step). FUNCTION: [D].
- **4.5 decision_brief(topic)** — end-to-end: retrieve region → concurrent facet-extract roles → judge role → "we chose X over Y because Z, at L####." FUNCTION: [D] — closes the Group-3.2 generic-pinpoint gap. NEW thin `runtime/session_brief.py` orchestrates retrieve→cascade.
  - FORM: [D] the brief renders as a projected card (Group 7), not a JSON dump.

## Group 5 — Channels: management + context-attachment  (lead lane §A/§C — CONVERGED) — [P] lead-owned
> Reshaped by Tim's corrections (relayed via lead, lead-owned to act): MULTIPLE MANAGED channels, join=launch-flag (NO wrapper), profile via SessionStart HOOK, unified per-member transport, notify-each. Lead builds these WITH the unified-transport once Tim reacts. Cross-ref: `../design/lead-lane-inputs.md` §A/§C.
- **5.0 Multi-channel management** — `cc_channel` gains create / list / add-member / remove-member / archive; a member (live session OR supervised clone) can belong to several channels; membership is a registry not ad-hoc handles. FUNCTION: [D] [P-lead].
- **5.0b Profile hook** — a SessionStart hook writes each session's PROFILE (handle/cwd/model/self-description) to the registry → rich member listings. (Tim applies the global hook — boundary edit.) FUNCTION: [D] [P-lead].
- **5.1 Channel attachments manifest** — a channel row carries `{sessions:[session://…], docs:[path…], recall_scope:{…}}`. FUNCTION: [D] [P-lead].
- **5.2 Load-on-join** — on add-member, inject a `<channel>` context-load pointing at the manifest; the member loads it as its rule/context-set (the `~/.vi/rules` auto-load precedent). FUNCTION: [D] [P-lead].
- **5.3 Preference payload** — the Group-3.7 requirements/preferences profile is part of what loads. FUNCTION: [D] (fork supplies the payload).
- **5.4 Recall-as-channel-capability** — `cc_channel op=recall {channel, query}` runs recall scoped to the channel's attached sessions (Group 6 scope) through the served embed+rerank (Groups 2/4). FUNCTION: [D] (fork supplies recall; lead wires the op).

## Group 6 — Multi-project / multi-session addressing  (lead lane §B — CONVERGED) — GATES fleet indexing
> The session store IS the source; addressable units keyed on THREE scope axes — **project · session · segment** (segment = the `isCompactSummary` compaction generation, per the schema find). Cross-ref: `../design/lead-lane-inputs.md` §B.
- **6.1 Address grammar** — `session://<project>/<sid>` + scope selector `{scope: project|session|segment|all, project?, sid?, segment?}`. Project key = the `~/.claude/projects/<encoded-cwd>/` dir (encode `/`,`.`→`-`; resolve by re-encoding, never decode — per `resume_cwd_for`). FUNCTION: [D] [P-lead].
- **6.2 Index scoping** — index per-(project,session) with scope keys embedded so a query filters scope WITHOUT re-embedding; ONE embedder space per index (pplx-4b — the golden rule, never mix). FUNCTION: [D] [P-lead].
- **6.3 Default-recall setting** — a `default_recall` config row (which session/project recall targets when no scope given). FUNCTION: [D].
- **6.4 Worked out BEFORE fleet indexing** — Tim's HARD GATE: do NOT index more sessions until 6.1/6.2 keying is locked. STATUS: [P] — blocking; lead-led.

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
