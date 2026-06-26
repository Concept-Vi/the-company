# recollection — COMPLETION CRITERIA

> The truth-table the build loop runs against. Each item is a **verifiable statement about the system**, checked by USE — not by code-reading, not by "the file exists." Grouped by component; priority order at the bottom (dependency-first). HOW for each item: `IMPLEMENTATION_GUIDE.md` §. Evidence: `RESEARCH_SYNTHESIS.md`. Open calls: `OPEN-DECISIONS.md` — **an item blocked on an unanswered decision stays ☐ and the build leaves the seam; it is not green-painted.**

## Verification rules (read before checking anything)
- **Status:** ☐ unverified · ✅ verified-by-use · 🟡 code-complete-untested · 🔴 known-broken. NEVER ✅ from code-reading.
- **FUNCTION bar:** the behaviour is demonstrated by a real run — an actual capture pass, an actual recall/gather/judge call returning real results, an actual distill producing real records, an actual MCP call from a Claude Code agent. No stub, no mock, no "looks right."
- **FORM bar (adapted for a memory system — its product face is agent-facing + any operator surface):**
  (1) **Agent ergonomics** — recall returns a navigable, grounded result (handles + typed verdicts carrying their *why*), NOT a raw text-flood; the grounded path is the *easy* path (grounded-chain law); parametric/axis-addressed, not blunt.
  (2) **Registry-visible / no-hardcoding** — adding a unit-type / lens / judge-type / tool / source is demonstrably a *registry row*, not a code edit (show it by adding one).
  (3) **Operator surfaces** (any viewer / health-map / ratification surface) built on the Company/design-system components + tokens, navigable-visual not text-wall, responsive — judged by a design-critic, not self-graded.
- A line is green only when BOTH faces are verified. Function-only is half-done.
- **Standing "no-fiction-about-Tim" gate:** any criterion that writes a principle/identity record is also verified for *no fabrication* (extracts only what's in the source; abstains when uncertain).

---

## G0 · Base & data model  (Guide §1)
- **G0.1 Rename & isolation** — FUNCTION: recollection installs as its own plugin, data dir `~/.recollection`, survives a (simulated) plugin-cache update without losing the corpus ☐ · FORM: paths/manifests registry/env-driven, no hardcoded cache path ☐
- **G0.2 Schema** — FUNCTION: atoms/units/links/fingerprints/verdicts/candidates tables exist and a real row of each can be written+read; lineage (session/round/project) fail-loud rejects a record missing it ☐ · FORM: portable-by-field (explicit space/source/dim/model/lineage cols), additive migration leaves existing exchanges/tool_calls intact ☐
- **G0.3 Address grammar** — FUNCTION: a unit resolves by `exchange://<sid>/<i>` and by containment (atom∈session∈project from cwd) on real data ☐ · FORM: address is an interface with one pluggable resolver (seam left for D-1) ☐

## G1 · Capture  (Guide §2)
- **G1.1 Total Claude-Code capture incl. sidechains** — FUNCTION: a backfill run ingests real sessions INCLUDING `agent-*.jsonl` sidechains; count of captured sidechain exchanges > 0 and matches the archive ☐ · FORM: source is a registry entry; adding a source = a row ☐
- **G1.2 Backfill from existing archive** — FUNCTION: the ~13,270-conv existing archive is ingested (verified by count) as the head-start ☐ · FORM: incremental/resumable (high-water-mark), re-run adds nothing duplicate ☐
- **G1.3 Live capture** — FUNCTION: a new exchange in an active session appears in recollection within the session (verified by a recall of something just said) ☐ · FORM: one unified path, not a 4th parallel lane ☐

## G2 · Distill  (Guide §3)
- **G2.1 L1 summaries complete** — FUNCTION: every captured conversation has a summary (count = conversations), produced by the LOCAL resident-4B (no cloud call) ☐ · FORM: layer is registry-typed; no SessionStart recursion ☐
- **G2.2 L2 structured extraction** — FUNCTION: a real exchange yields typed records (a decision, a principle, a what-built) findable as *meaning*, linked to source ☐ · FORM: record-types are registry rows (add one, it works); no-fiction verified on a sample ☐
- **G2.3 L3 rollups** — FUNCTION: a concept touched across ≥2 projects rolls up into a settled-view that pools them; a project rolls up into an arc ☐ · FORM: rollup levels registry-defined ☐
- **G2.4 Principle ratification gate** — FUNCTION: a candidate principle lands in staging and is committed ONLY via the propose→refine→commit flow with the powerful-judge slot (D-2); non-principle records self-assemble without it ☐ · FORM: the ratification surface (if UI) on design-system; no-fiction enforced ☐
- **G2.5 Interactive distill** — FUNCTION: in directed/co mode, distillation happens in-conversation (a candidate surfaces during a real exchange) ☐ · FORM: mode-gated via the modes registry ☐

## G3 · Embed / lenses  (Guide §4)
- **G3.1 Fabric multi-lens (no hardcode)** — FUNCTION: units get fingerprints from ≥2 lenses via fabric `:8001`; a unit has multiple `(unit,space)` rows ☐ · FORM: NO hardcoded model/dim anywhere; bge-m3 is just one registry row, swappable; demonstrated by swapping a lens via registry ☐
- **G3.2 Steerable multi-space** — FUNCTION: the same unit is findable by different question-shapes (by-concept vs by-decision return different rankings) ☐ · FORM: steering vocab MINED from corpus, not dev-default literals ☐
- **G3.3 Code lens** — FUNCTION: "find code that does X" returns the right code unit; nomic-code runs with `--pooling last`+query-prefix (no silent fail) ☐ · FORM: ColGrep multi-vector lives in its OWN index, not the single-column store ☐
- **G3.4 Re-embed migration** — FUNCTION: the legacy 384-dim space is migrated/retired; corpus & query use the same model per space (no mismatch) ☐ · FORM: version-stamped ☐

## G4 · Link / provenance  (Guide §5)
- **G4.1 Mechanical crossings** — FUNCTION: from a real file path, the live join returns the exchange/session/ts that wrote it (artefact↔conversation), on real data ☐ · FORM: grade=mechanical, asserted as fact ☐
- **G4.2 Semantic links** — FUNCTION: a cross-project concept link connects the same concept in ≥2 projects; "what projects include X" resolves via links ☐ · FORM: grade=semantic + confidence; high-stakes routed through the judge; never masquerades as certain ☐
- **G4.3 Lazy tool_results** — FUNCTION: a tool_result is NOT in the distilled memory but is fetchable on demand via its key ☐ · FORM: keyed to the crossing ☐
- **G4.4 Link, not embed** — FUNCTION: a generated record points to its causal conversation by live link (drift checkable against source); no embedded quote-copy ☐ · FORM: one source, everything points to it ☐

## G5 · Gather  (Guide §6)
- **G5.1 Decompose + classify** — FUNCTION: a dense multi-thread message is split to threads, each classified+routed, on a real input ☐ · FORM: classification obeys the Classification Law (1 axis/2 extremes/3–5/chains); types are registry rows ☐
- **G5.2 Two modes** — FUNCTION: top-k returns a precise hit; gather-all-and-aggregate returns a pooled arc for a much-discussed concept ☐ · FORM: agreement-across-lenses surfaces as signal (RRF) ☐
- **G5.3 Questionless-sweep lane** — FUNCTION: a sweep emits findings unasked (e.g. an orphan/duplicate inventory, or a merge-as-join MATCHED/build/debt list across two projects) ☐ · FORM: map(all)→reduce(cluster/join), not query-time gather ☐

## G6 · Judge  (Guide §7)
- **G6.1 Proofreader + set-reader** — FUNCTION: a noisy top-50 is re-ordered so the right answer surfaces; duplicates fold; a conflict is flagged ☐ · FORM: proofreader on CPU (~free), always-on ☐
- **G6.2 Jury, routed** — FUNCTION: on an ambiguous/high-stakes recall the jury fires and rules current-vs-superseded (time-axis) and answers-vs-mentions; on a clean recall it does NOT fire ☐ · FORM: routing rule-driven on question AND result (registry); judgment-types are registry rows (add one) ☐
- **G6.3 Typed self-explaining verdicts** — FUNCTION: a returned result carries multiple typed verdicts (relevance/currency/confidence) the agent can reason from ☐ · FORM: never bare scores; basis attached ☐

## G7 · Recall surfaces  (Guide §8)
- **G7.1 Axis-addressed MCP tools** — FUNCTION: a Claude Code agent (me/other) calls `whats_my_position_on`/`the_arc_of`/`what_projects_include`/`what_touched` over the MCP and gets correct grounded results ☐ · FORM: parametric core, registry-driven (add a tool = a row), `return_format` override, **handles-first not text-flood**; `search`+`read` names preserved ☐
- **G7.2 Skill** — FUNCTION: recollection's skill performs the common "recall what's relevant" flow end-to-end ☐ · FORM: wraps the tools so the agent doesn't hand-orchestrate ☐
- **G7.3 Sub-agent (deep arm)** — FUNCTION: the sub-agent runs gather→judge→follow-up→assemble for a deep pool/arc job without burning the caller's context ☐ · FORM: returns a curated arc + verdicts, not a dump ☐

## G8 · Proactive injection — LAYER 2  (Guide §8d)
- **G8.1 Floor at session start** — FUNCTION: a fresh session's agent already holds Tim's active principles + this project's standing state, injected by a SessionStart hook, WITHOUT being asked ☐ · FORM: same gather→judge machine; conservative (no speculative dump) ☐
- **G8.2 In-session injection** — FUNCTION: a dense/conceptual moment triggers relevant context injection on the moment (UserPromptSubmit hook) ☐ · FORM: mode-gated; learns from `tim_correction` ☐

## G9 · Health  (Guide §9)
- **G9.1 Temperature scan** — FUNCTION: a real per-unit resistance score + a heat-map of misfiled/drifted units is produced on the live corpus ☐ · FORM: any surface on design-system ☐
- **G9.2 Annealing dream-phase** — FUNCTION: a deep-pass re-places drifted units / folds duplicates and lowers measured corpus temperature (before/after) ☐ · FORM: registry-driven schedule ☐

## G10 · Bootstrap & the north star (the proofs that matter most)
- **G10.1 Build-uses-itself** — FUNCTION: once A is online, a build step recovers a real prior decision BY QUERYING recollection (the subagents-through-memory directive, served by recollection) ☐
- **G10.2 Pillar 1 — switch-flip test** — FUNCTION: an agent loaded with recollection's floor answers a "what does Tim mean by X / what's his position on Y" correctly WITHOUT re-explanation, where a cold agent fails ☐ · FORM: grounded (carries provenance) ☐
- **G10.3 Pillar 2 — omniscience test** — FUNCTION: "what was built in project Z and when / what projects include X / merge these two" returns correct cross-project, time-anchored answers from real history ☐
- **G10.4 No-fiction proof** — FUNCTION: an adversarial check finds zero fabricated principle/identity records on a sample ☐

---

## G11 · Law-floors & negative tests (Wave-3 — laws need teeth, not adjectives)
Laws asserted in prose pass nothing; each needs a NEGATIVE test that fails loud.
- **G11.1 Classification Law floor** — FUNCTION: a classification-type declared with >5 bins (or no two-extreme axis) is REJECTED at registry-time, not silently accepted ☐
- **G11.2 Directional-edge floor** — FUNCTION: an edge-type declared without a direction+inverse is REJECTED ☐
- **G11.3 No-fiction ABSTENTION path** — FUNCTION: on a source with no principle present, extraction returns empty/abstains (NOT a fabricated principle); verified adversarially, not just on the positive corpus ☐
- **G11.4 Worker-can't-judge membrane** — FUNCTION: a fan-out worker cannot emit a verdict/decision (only observations); attempting it is structurally impossible/rejected ☐
- **G11.5 Per-step context-package** — FUNCTION: each distill/classify/judge step ships its context-package + deterministic-floor + gate (grounded-chain), verified on a real step ☐
- **G11.6 Grounded-is-easiest** — FUNCTION: the easiest tool/path an agent reaches for returns the GROUNDED result; the raw ungrounded flood requires an explicit override (D-11) ☐

## Wave-3 STRENGTHENED criteria (tighten weak items the design audit flagged)
- **G4.2★ (tightens G4.2) — cross-project edge graph AT SCALE** — FUNCTION: the cross-project concept-edge graph is POPULATED across the real corpus (not one hand-made edge); "what projects include X" resolves from the populated graph for multiple real X; the `find_relations` edge layer actually emits edges at scale ☐ · FORM: edges typed+graded; the questionless-sweep lane (G5.3) is named as the omniscience organ, not query-time gather ☐
- **G5.2★ (tightens G5.2) — pooled recall completeness** — FUNCTION: a gather-all result carries a coverage/confidence verdict AND is checked against a known ground-set (it must NOT silently miss half the occurrences) ☐ · FORM: no-silent-failure applied to recall — incompleteness is surfaced, never hidden ☐
- **G10.2★ (tightens G10.2) — Pillar-1 PANEL switch-flip** — FUNCTION: a floored agent clears a PANEL of "things Tim shouldn't have to re-explain" (drawn from real `tim_correction` records) where a cold agent fails — a population property, not one lucky principle ☐ · FORM: each answer grounded (carries provenance) ☐
- **G10.5 (new, was missing — B5) — fresh agent drives a real task unaided** — FUNCTION: a fresh agent, floored by recollection, completes a real Tim-task correctly WITHOUT re-explanation that a cold agent would have needed ☐
- **G4.3★ (tightens G4.3) — tool_result round-trip** — FUNCTION: "fetch what came back" actually RETRIEVES the result (re-read from source JSONL via show.ts), not just returns a key to a never-fetched NULL ☐

## Priority order (dependency-first — informs the loop; Tim sets actual build-order)
1. **G0** (base/schema) → **G1** (capture incl. sidechains + backfill) → **G3.1** (one fabric lens). *Foundation; ends with G10.1 bootstrap online.*
2. **G2** (distill L1→L2→L3 + ratification) + **G4** (links) + **G3.2–3.4** (lenses + steering). *Understanding.*
3. **G5** (gather + sweep) + **G6** (judge) + **G7** (tools/skill/sub-agent). *First usable recall; verify G10.2/G10.3.*
4. **G8** (proactive layer-2) + remaining **G7** + **G9** (health). *Delivery + lifecycle.*
Cross-cutting throughout: registry-visible/no-hardcoding (every group's FORM), no-fiction (every principle write), verify-by-use (every ✅).
