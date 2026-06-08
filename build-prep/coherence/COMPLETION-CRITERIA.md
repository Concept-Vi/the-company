# Coherence lane — Completion Criteria (the truth-table the loop builds against)

> The grounded loop-prep for the COHERENCE lane (loop-prep doc 1 of 3). Doc 3 (Research Synthesis) already
> exists: `COHERENCE-SUBSTRATE.md` + `SEMANTIC-LAYER.md` + `CORPUS-CHAIN.md` + `findings/` (18 companions).
> Doc 2 = `IMPLEMENTATION-GUIDE.md`. This doc = what must be TRUE for the coherence lane to be done.
>
> **Re-scoped to the three-way split (read-vs-mutate):** this lane builds the **structural detectors · gates ·
> disposition-store · calibration-harness · the shared pre-commit suite · `build_coherence_info`**. It does
> NOT build the engine (`run_items`/`run_reduce`/`cognition.py` — cognition's C) or the surface/FE
> (guided-review's). My detectors READ the engine/registry/routes/FE; they never mutate them. Chains-as-actions
> (Group E) is a CO-DESIGN: I own the *declaration + validator + registry* (the saving side); the *runner* is
> cognition's engine + the existing `run_graph`.

## Verification protocol (how a line earns ✅ — read before checking anything)
- **By USE, never code-reading.** A gate is ✅ only when run (its acceptance suite green) + an adversarial
  re-check (a separate pass that tries to DISPROVE "done") survives. A harness/store is ✅ only when run
  against real data and the output inspected.
- **Honest current-state, three states:** **✅ Verified** (run + confirmed this session/by the loop) ·
  **🟡 Designed** (specced + grounded in the research, code not built or not by-use-verified) ·
  **🔴 Broken** (code exists, wrong result). Never ✅ on code-reading or a green label alone.
- **The two faces, scoped honestly.** Most of this lane is FUNCTION (substrate — no operator surface; the FE
  is guided-review's). Its FORM-equivalent is the **CLI faces** (`company suites` / `company coherence` / the
  calibration report): legible, navigable, scannable output — NOT a text-wall, NOT a raw dict dump. Where a
  line has no surface, it carries FUNCTION only and says so; I do NOT invent a Form face that isn't mine.
- **The laws bind every line:** registry-is-truth (no-hardcoding — `~/.vi/rules/no-hardcoding.md`) · additive ·
  fail-loud (no silent fallback) · reflects-never-owns · own/reflect (re-derive detection, own dispositions) ·
  positive-only (a fuzzy/semantic finding PROPOSES, never auto-acts) · the operator-only floor.
- **No green-paint:** anything not headlessly confirmable → 🟡 needs-tim with a note, never ✅.

---

## Group A — The structural detectors + gates  (mostly built this session — verify + lock)
- **A1 · reachability gate, AST-grounded** — every `/api` route reaches a real caller (a `fetch`/`EventSource`/
  HTTP call on the comment-stripped corpus) or is a catalogued orphan; NO false-wire (a dead route reading as
  wired). FUNCTION: ✅ Verified (`2707b79` — 116 routes, 79 wired, 37 catalogued, 0 new; fixed 4 measured
  false-wires incl. the comment that gamed the substring heuristic). FORM(CLI): ✅ the gate prints a scannable
  by-tag backlog, not a dict.
- **A2 · all-green gate (`suite_health` / `company suites`)** — every `*_acceptance` suite passes standalone;
  live-dep skips classified via the registry, not silently. FUNCTION: ✅ Verified (114 green, 4 dep-skips, 0
  red). FORM(CLI): ✅ green/needs-dep/red classification, scannable.
- **A3 · registry-vs-live gate** — node-type files on disk (stem + `run()`) == live `capabilities().node_types`;
  drift fails the build. FUNCTION: ✅ Verified (`71f8e8e` — 16==16). 
- **A4 · candidate detectors are REPORT-only** (capability-no-consumer, hardcoding-candidates) — they run +
  surface candidates, NEVER fail the suite (positive-only; a grammar/the-registry-itself is a legit false
  positive). FUNCTION: ✅ Verified (`71f8e8e` — 4 + 18 candidates surfaced, suite green).
- **A5 · drift gate** — self-description (MAP/STATE) matches the live registry. FUNCTION: ✅ Verified (green).
- **A6 · the orphan catalogue is a DECLARED registry** (not a hardcoded dict) — `design/_system/orphan-routes.json`
  read via `_orphan_routes()`. FUNCTION: ✅ Verified (`2707b79`; no-hardcoding dogfooded).
- **A7 (🟡) · the hardcoding detector escalates from candidate → law** — once the disposition store exists (C),
  a hardcoding candidate dispositioned `must-fix` is tracked to closure (not just printed). FUNCTION: 🟡 Designed.

## Group B — The shared pre-commit suite  (I own assembling it; unblocks all three loops)
- **B1 · one entry runs ALL coherence gates standalone** (`company suites` is the spine: A1–A5 + drift).
  FUNCTION: ✅ Verified (exists). 
- **B2 (🟡) · guided-review's FORM-lint folded in as ONE check** — not a parallel pre-commit layer; their
  FORM-lint is a check inside the one suite. FUNCTION: 🟡 Designed (awaiting their FORM-check handoff — they
  said they'll hand it over). When landed: the one suite gates structure + form together.
- **B3 (🟡) · the suite is the ratified pre-commit gate the three loops read** — green-before-any-shared-commit,
  per `WORK-SPLIT.md § PROTOCOL`. FUNCTION: 🟡 Designed (ratify in the protocol; the gate exists, the
  three-way binding is the pending agreement).

## Group C — The disposition store + finding model  (net-new — the substrate spine)
- **C1 (🟡) · a persisted, ADDRESSED finding record** — `{kind, address(ui://|code://), state, evidence,
  source:structural|semantic, since}` on the append-only event log (rides `append_event`/`_emit`, per AREA-1).
  FUNCTION: 🟡 Designed.
- **C2 (🟡) · the disposition is OWNED, mutable, separate from detection** (own/reflect) — finish/defer/
  by-design + reason, on a last-wins overlay (the pin-overlay pattern, AREA-1), NOT in the append-only record;
  detection re-derived, disposition kept. FUNCTION: 🟡 Designed.
- **C3 (🟡) · the reconcile is `(kind, address)` upsert → known/new/resolved** (generalizing reachability's
  documented/new/stale, AREA-2); net-burn-down computable; a finding closes only when its detector agrees
  (structural) or the confirming authority agrees (semantic — never by a swarm re-read, SEM-4). FUNCTION: 🟡.
- **C4 (🟡) · findings are NOT operator-inbox items** — own agent-disposable lane; only `by-design` escalates
  through the consent gate (AREA-1: the inbox is operator-only + already-drowned). FUNCTION: 🟡 Designed.
- **C5 (🟡) · the burn-down rollup** — read-time fold (the `run_stats` pattern), open-by-kind/owner/over-time.
  FUNCTION: 🟡 Designed. FORM(CLI): `company coherence` shows the burn-down scannably.
- **C6 (🟡) · `_ORPHAN_ROUTES`→registry is step 1; the catalogue becomes finding-records** — the orphan
  catalogue migrates into the finding store (the first real findings; the recursion). FUNCTION: 🟡 (A6 was the
  declared-registry step; this is the store step).

## Group D — The calibration harness  (the "first real artefact" — experiment + save)
- **D1 (🟡) · a labelled eval set from the system's OWN named incidents** — `/status` half-migration (TP for
  half-migration), mode-dial-built-twice (TP for concept-coherence), `/api/knobs` (TP for intent-drift), the 3
  measured false-wires (structural truths to check agreement), + deliberate true-negatives (clean migration /
  rename / additive). FUNCTION: 🟡 Designed (the incidents are real + documented; the set is the build).
- **D2 (🟡) · run an action/detector under N model configs against the eval set** — swap the worker/synth model
  (from the registry); the experiment axis. FUNCTION: 🟡 Designed (the structural detectors prove the framework
  single-config now; the N-config LLM experiment lands when cognition's engine + the semantic detectors land).
- **D3 (🟡) · measure precision/recall/cost/latency PER config** — turns the S1/S2/S3 trust tiering (SEM-3)
  from assertion into a number-per-class. FUNCTION: 🟡 Designed. FORM(CLI): a scannable per-config table.
- **D4 (🟡) · the winning config is SAVED as the action's default** (experiment → calibrate → save) — the
  closed loop Tim named; positive-only (a class ships to the panel only if its calibrated precision clears the
  threshold). FUNCTION: 🟡 Designed (the save side is mine; depends on the Action registry, E).

## Group E — Chains/graphs as configurable saveable actions  (CO-DESIGN — my declaration half)
- **E1 (🟡) · the Action declaration schema + ONE `build_action` validator** — a saved graph/chain promoted to
  a declared, named, configurable action `{steps, per-step model from the registry, inputs(addressed),
  output_schema}`; one validator gates declared/compiled/saved instances (CC-1). FUNCTION: 🟡 Designed. LAW:
  registry-is-truth (the action registry, discovered like roles/nodes — not a hardcoded list).
- **E2 (🟡) · the action registry (the SAVING side)** — saved actions are declared rows, reusable/fireable;
  the LLM config is part of the declaration (→ configurable + experimentable via D). FUNCTION: 🟡 Designed.
- **E3 (co-design, NOT mine to build) · the runner** — `run_graph` (exists) + cognition's `run_items`/
  `run_reduce` (their C, in flight) execute an action. I declare + validate + save; they run. Marked here so
  the seam is explicit; built in cognition's lane.
- **E4 (🟡) · `build_coherence_info`** — the third sibling projection (beside `object_info` +
  `build_cognition_info`); the coherence model's read-face; reflects-never-owns. FUNCTION: 🟡 Designed (mine;
  co-design the projection machinery with cognition).
- **E5 (🟡) · END-STATE: actions COMPOSE + RUN across MODELS *and* EMBEDDINGS** (Tim, explicit) — a saved
  action can be composed from steps that each declare a model OR an embedding op (embed/similarity/retrieve),
  run end-to-end, and be re-run under a different model/embedding config (the experiment axis, D2). This is the
  whole point landing: chains-as-actions that actually exercise the LLM layer + the embedding layer, swappably.
  FUNCTION: 🟡 Designed. **CO-DESIGN + DEPENDENCY:** I own compose+declare+save+calibrate; the RUN half needs
  cognition's engine (`run_items`/`run_reduce` + the **embed op**, C 2-3/4) AND the model/embedding
  **launch/select/evict** capability (cognition's B + the resident-model capability — load BGE-M3 @ :8001 on
  demand, not a hand-evict). My calibration (D) is what proves a composed model+embedding action is trustworthy
  per config. Until the engine + on-demand-embed land, E5 builds on the existing `run_graph` + embed nodes
  single-config; the full swappable model+embedding form lands when they do.

## Group F — The substrate as the shared honesty instrument  (the convergence-round lens)
- **F1 (🟡) · the detectors run cross-fork over the merged whole** — one-seam / unconsumed-output / law-break
  as gates over all three lanes' work (not goodwill); my lens in the convergence round. FUNCTION: 🟡 Designed
  (realized in the convergence round; the detectors already run tree-wide).
- **F2 (🟡) · the structural half of the convergence sign-off** — the gate battery green over the integrated
  whole (adversarial-to-appearance, can't be green-painted); paired with guided-review's by-use operator path.
  FUNCTION: 🟡 Designed (the convergence round).

---

## Priority order (dependency-first)
1. **A** — verify + lock the built detectors/gates (mostly ✅; close A7 after C). *Foundation, done.*
2. **B** — the shared pre-commit suite (B1 ✅; fold B2 when guided-review hands the FORM-lint). *Unblocks all three loops — highest shared leverage.*
3. **C** — the disposition store + finding model. *The substrate spine; everything downstream writes into it.*
4. **D** — the calibration harness. *Makes detectors/actions trustworthy; the experiment→save loop; needs C for D4's save.*
5. **E** — chains-as-actions (declaration/registry/build_coherence_info; runner is cognition's). *Gated on cognition's engine for the runner half; the declaration half is buildable alongside.*
6. **F** — the convergence-round lens. *Last; the whole-system honesty pass.*

**Engine-independence note:** A→B→C→D are buildable WITHOUT cognition's engine (structural + substrate + the harness framework on existing `run_graph`/structural detectors). Only E's runner + D's N-config-LLM experiment depend on cognition's C. So the loop is NOT blocked on cognition for the bulk of the lane.

## Definition of done (the whole lane)
Every line ✅ or 🟡-needs-tim-with-a-note (none 🔴/unbuilt-silently); the shared pre-commit suite assembled +
ratified; the disposition store live with the detectors writing into it + the burn-down readable; the
calibration harness producing a per-class number on the real incidents; the Action declaration/registry built
(runner co-designed); **actions that compose + run across models AND embeddings, swappable per config (E5)**;
`build_coherence_info` projecting; and the substrate proven as the convergence-round's structural honesty half.
Verified by use, no green-paint, the laws held.
