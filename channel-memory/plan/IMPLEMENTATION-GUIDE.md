# Implementation Guide — HOW to build each group

```
trust: fabric-derived
author: ch-8djrpmsl / 11e7d395 (fork) — joint groups with lead ch-al7jdfdr
date: 2026-06-14
```
> loop-prep Document 2. Tense is explicit: "IS" = exists, "WILL BE" = planned. References COMPLETION-CRITERIA.md (what) + RESEARCH-SYNTHESIS.md (what exists) + INFERRED-PREFERENCES.md (the proposed design choices). Build only after Tim reacts to the inferred answers; until then these are specced to the proposals.

## Group 1 — Dimension-aware chunking
**Principle:** Tim's messages carry multiple dimensions in one turn; a fixed char window blurs/splits them. Split on the message's OWN structure so each dimension embeds as its own vector and stays retrievable. WHY not fixed-window: today's 700-char split already proved the dilution failure (the 5-topic decision turn L4335 sank to rank #51 averaged; sub-chunking lifted its reason-segment to #1).
**Sequence:** read turn → detect structure (double-newline paragraphs; then sentence/line boundaries; for Tim-turns, the line-by-line dimension shifts) → emit sub-chunks at structure boundaries (with a min/max size guard + small overlap) → each carries parent {line, ts, attr} (Group 1.2).
**Do/Don't:** DON'T cut mid-sentence (loses the dimension's meaning). DON'T drop the parent handle (a hit must surface the whole message). DO keep it deterministic (same input → same chunks → cache-stable index).
**Files:** MODIFY `runtime/session_recall.py` `session_chunks()`/`_split()` (ADD structure-detection; KEEP the served-embed path). REFERENCE the scan rows for attribution.

## Group 2 — Recall substrate
**Principle:** bridge-free, Company-served, fail-loud (Round 2). **IS:** embed :8007, rerank :8008, both served.
**2.4 Freshness (the build):** before recall, compare source `.jsonl` mtime/size against the index's recorded source stamp; if newer ⇒ rebuild (or warn + degrade, declared). **Do/Don't:** DON'T serve a stale index silently on a live session (the advisor's flag) — that re-introduces a silent-wrong. DO stamp the index with source size+mtime at build (session_scan already records source_bytes/mtime — reuse).
**Files:** MODIFY `runtime/session_recall.py` (ADD freshness check in `recall()`/`build_recall_index`).

## Group 3 — Lenses (esp. the new ones)
**3.7 requirements/preferences (ANTI-RECENCY) — the keystone.**
**Principle:** the source of truth for "how Tim works" is the cross-session `feedback-*` memory corpus (distilled, anti-recency by construction — INFERRED-PREFERENCES Q3), NOT one session's recency-skewed recall. The lens READS the memory corpus first, then layers session-specific signal (Tim-turns, his corrections/frustrations), weighted by importance/repetition.
**Sequence:** load feedback-* corpus (the standing profile) → extract session-specific Tim-signals (directives + corrections via open_loops cues, Tim-turns only — EXCLUDE channel chatter, which polluted the naive recall) → merge, weight by repetition/emphasis not recency → emit a profile.
**Do/Don't:** DON'T rank by recency. DON'T let fabric/channel chatter into the profile (proven pollution). DO cite the memory entry each signal came from.
**Files:** NEW `runtime/session_lens.py` `preferences()` (or a `runtime/tim_profile.py`); REUSE the feedback-* reader. The output is the Group-5.3 channel-load payload.
**3.8 spin-up-choosing:** score each fork-point candidate (channel-memory/map/fork-points.md) by decision-density (decision-cue counts in its segment), expertise-crystallization (topic concentration), hot-open-threads (open_loops near it), novelty-vs-compaction-summary. Emit a ranked surface. **Files:** NEW lens reusing session_scan segments + session_lens.

## Group 4 — Retrieve-then-synthesize panel  [build ON the existing cognition engine — do NOT parallel]
**Principle (Tim's law):** small models = concurrency + assignment + STRUCTURED OUTPUT + chaining; NEVER judgment/reasoning. The smart model judges. The panel is almost certainly ROLES in the existing `runtime/cognition.py` / role-cascade engine ([[company-compositional-architecture]]) — RESEARCH-SYNTHESIS Round 4 (explore first).
**Sequence:** `decision_brief(topic)` → (a) retrieve region (Groups 2/3, search+rerank — kept separate, 4.1) → (b) fan concurrent small-model EXTRACTORS, one per FIXED facet (chosen/alternatives/reason/constraints/owner — the registry, INFERRED-PREFERENCES Q1), each with an enforced json_schema ([[reference-vllm-structured-output]]: response_format json_schema, NOT json_object) → (c) chain the structured facets into ONE smart-model judge that assembles the brief with line citations.
**Do/Don't:** DON'T ask a small model "what did we decide?" (judgment — it'll reason badly). DO ask it "extract the {facet} as this schema" (extraction). DON'T build a parallel extractor framework — use the existing roles/cascades. DON'T replace search (additive, 4.1).
**Files:** REFERENCE `runtime/cognition.py` + the role/cascade MCP (run_role/run_cascade/save_cascade) — explore, then ADD the facet-roles + the brief cascade. NEW thin `runtime/session_brief.py` orchestrating retrieve→cascade.

## Group 5 — Channel-context  [JOINT with lead]
**Principle:** a channel IS a context scope (The Heart: registries with attached context). A member loads the channel's manifest on join the way `~/.vi/rules/*.md` auto-loads (the precedent). Don't parallel the registry/rules system (INFERRED-PREFERENCES Q4).
**Sequence (proposed, pending lead):** channel registry entry gains an `attached` manifest {sessions[], docs[], preference_profile} → on member join, the manifest loads as rules/context → member can recall against attached sources live (Groups 3/4).
**Files:** [P] lead-owned (`runtime/cc_channels.py` + the registry + the ~/.vi/rules loader). Fork provides the recall/preference payload.

## Group 6 — Multi-project / multi-session  [JOINT with lead; GATES indexing]
**Principle:** registry-based addressing of (project, session) (INFERRED-PREFERENCES Q5). **HARD GATE:** settle the scheme with the lead BEFORE indexing more than the current sessions.
**Files:** [P] lead-led. Fork's session_scan/recall already key on a single transcript path; the multi-session index location/naming is the open piece.

## Group 7 — Projection
**Principle (FORM):** the data (scan rows, lens outputs, lineage, briefs) is registered as a SOURCE; the Company UI PROJECTS it (vision §1.9) — no bespoke UI. **WILL BE** rendered as a navigable visual/spatial surface (timeline, density, dense-message profile) on Tim's pointer to the UI-building sessions (§1.10).
**Files:** the data shapes exist (scans/, map/); registration + projection [TIM-GATED/FAR].

## Group 8 — Spin-up / fork-fleet
**Principle:** mapped (map/fork-points.md); a uuid-cut probe proves mid-conversation resume before any fleet; launch is [TIM-GATED].

## What every change preserves
The recall stack (scan/recall/lens) is bridge-free + served — additive modules; changes to chunking/freshness MUST keep: the served-embed path, the served-rerank path, the structural scan attribution, the existing lens APIs, and the non-destructive source guarantee. session_search.py deprecation must not break any OTHER consumer (check before re-pointing — lead's task).
