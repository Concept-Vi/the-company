# Coherence lane — Implementation Guide (the HOW for the loop)

> Loop-prep doc 2 of 3. Pairs with `COMPLETION-CRITERIA.md` (what must be true) + the Research Synthesis
> (`COHERENCE-SUBSTRATE.md`/`SEMANTIC-LAYER.md`/`CORPUS-CHAIN.md` + `findings/` — the WHY + the file:line
> evidence). This doc is the build sequence, the dos/don'ts, and the file map for the 🟡 net-new groups
> (A/B are mostly built; the depth for everything is in the synthesis — I reference it, don't duplicate it).

## Standing laws (bind every build step)
Registry-is-truth (no-hardcoding) · additive (optional fields, bump schema_ver) · fail-loud · reflects-never-owns ·
**own/reflect (re-derive detection, persist only dispositions)** · **positive-only (semantic/fuzzy PROPOSES,
never auto-acts)** · operator-only floor · verify-by-use · claim a shared file in `WORK-SPLIT.md § CLAIMS`
before editing it · `company suites` green before any shared-file commit · **read-vs-mutate: I build my
detectors/gates/substrate; I never write the engine (`cognition.py`/`run_items`/`run_reduce`) or the FE.**

## File territory (mine — additive)
- `runtime/coherence_detect.py` (the detector module — mine, extend freely).
- `runtime/suite.py` gate methods ONLY (~7025-7174 region + new detector/store methods) — claim the window.
- `tests/{suite_health,reachability,detectors,disposition,calibration}_acceptance.py` (new tests — disjoint).
- `design/_system/orphan-routes.json` + new declared registries under `design/_system/`.
- the store (`store/fs_store.py`) — ADD finding/disposition methods (claim the window; additive).
- NEVER: `runtime/cognition.py`, `runtime/roles.py`, `canvas/app/src/*`, the engine. Those are co-design/other lanes.

---

## Group B — assemble the shared pre-commit suite
**Principle:** one suite, not two pre-commit layers. `company suites` already runs every `*_acceptance`
standalone (the spine). The FORM-lint is ONE more check inside it, handed over by guided-review.
**Sequence:** (1) confirm `company suites` runs A1–A5 + drift standalone (it does). (2) when guided-review
hands the FORM-lint, register it as one check in the suite runner (additive — a new `*_acceptance` or a
folded check), not a separate command. (3) ratify in `WORK-SPLIT.md § PROTOCOL` as the green-before-shared-commit
gate the three loops read.
**Don't:** build a second pre-commit mechanism · gate on the FORM-lint before they hand it (mark B2 🟡 until then).

## Group C — the disposition store + finding model  (the substrate spine; build on existing primitives)
**Principle (own/reflect — the load-bearing distinction, AREA-6):** DETECTION is re-derivable (re-run the
detector → same finding) so it RIDES the existing machinery and is never owned; DISPOSITION is a decision (not
recomputable) so it is the one genuinely persisted thing. A disposition is a micro-ADR.
**Reuse (do NOT build new storage — AREA-1 maps every field to an existing primitive):**
- finding record → `fs_store.append_event` / `_emit` (already address-stamped on every emit). One new `kind`.
- mutable disposition → the **pin-overlay-last-wins** pattern (`fs_store.append_pin`/`pin_state_for`) — a
  separate overlay keyed by finding-id, NOT a mutation of the append-only record.
- the burn-down → the **`run_stats` read-time-rollup** pattern (fold the events; never a maintained graph).
- the status lifecycle SHAPE → the Inbox's separate-status-lane (`governance.py`) — but findings get their
  OWN lane, agent-disposable; only `by-design` escalates through the consent gate.
**Sequence:** (1) `append_finding(rec)` + `findings_for(address)` on the store (mirror `append_annotation`).
(2) the disposition overlay (`set_disposition(finding_id, disposition, reason, by)` — pin-pattern). (3) the
`(kind,address)` reconcile upsert → known/new/resolved (generalize `reachability`'s documented/new/stale).
(4) the burn-down rollup (`run_stats`-style). (5) migrate `_ORPHAN_ROUTES`(the declared registry) → finding-
records (C6 — the catalogue becomes the first findings; the recursion). (6) `tests/disposition_acceptance.py`
proves it by use (a detector emits → a finding lands → disposition persists → reconcile resolves on re-run).
**Don't:** put findings in the operator inbox (it's operator-only + already-drowned — C4) · mutate the
append-only record for disposition (use the overlay) · let a semantic finding close by re-detection (only the
confirming authority closes it — SEM-4) · key dedup on a content-hash for semantic findings (prose varies →
key coarse on (kind,address) — SEM-4).

## Group D — the calibration harness  (experiment → calibrate → save; THE first artefact)
**Principle:** the harness turns the trust tiering from assertion into a measured number per class (SEM-3), and
it IS "experiment with the LLM layer + save what works" (Tim). A detector/action run under N model configs
against a labelled eval set → precision/recall/cost/latency per config → the winning config saved as default.
**Reuse:** the structural detectors (built, model-free) prove the framework single-config NOW; the eval set is
the system's own named incidents (real, documented — D1); the N-config LLM experiment + the semantic detectors
land when cognition's engine does (D2's full form). The save side is the Action registry (E).
**Sequence:** (1) `build-prep/coherence/eval-set/` — the labelled incidents as fixtures ({input, expected,
class}), drawn from `/status`/mode-dial/`/api/knobs`/the 3 false-wires + the hand-built true-negatives.
(2) a scorer: run detector D over the eval set → precision/recall/cost/latency. (3) the per-config loop: same
detector, swap the model config (from the registry) → a per-config table. (4) `tests/calibration_acceptance.py`
proves it: run the structural detectors over the set, assert the known TPs are caught + the TNs are not
(single-config now). (5) when the engine lands: run the semantic detectors under N configs → the per-class
number → save the winner (D4, via E2).
**Don't:** ship a class to the panel on an UNCALIBRATED config (positive-only) · let the 4B's self-confidence
gate (Verified-useless, SEM-3) · trust a same-model jury for correctness (variance≠error — the stronger-model
confirm is the keystone) · build the N-config-LLM form before cognition's engine (build the framework + the
single-config structural form now; wire the LLM-config axis when the engine lands).

## Group E — chains/graphs as configurable saveable actions  (CO-DESIGN — build the SAVING side only)
**Principle:** a saved graph/chain is a declared, named, LLM-configurable, fireable ACTION; one `build_action`
validator gates declared/compiled/saved instances through one door (CC-1); the LLM config is part of the
declaration (→ configurable + experimentable via D). I own DECLARE+VALIDATE+SAVE+REGISTER; the RUNNER is
cognition's engine + the existing `run_graph` (E3 — NOT mine to build).
**Reuse:** `save_graph`/`/api/graphs`/`run_graph` exist; nodes already declare a registry-model
(`options_from:chat_models`) — the configurable-LLM-layer per-node is BUILT; the action registry is discovered
like roles/nodes.
**Sequence:** (1) the Action declaration schema (a typed object; the LLM config per step from the registry).
(2) `build_action(decl)` validator (mirror `_build_role`/`build_chain`). (3) the action registry (declared
rows, discovered — registry-is-truth). (4) `build_coherence_info` (E4 — the projection sibling; co-design the
machinery with cognition). (5) hand the runner seam to cognition (they run via `run_items`/`run_reduce`/`run_graph`).
**Don't:** build the runner (cognition's) · build the authoring FE (guided-review's) · decide the Action schema
unilaterally — it spans cognition's engine + guided-review's authoring; **propose the schema in the coordination
home and co-design it** (the convergence round exists to catch a unilateral schema seam). · hardcode the action
list (registry-is-truth).

## Group A — already built (verify + lock; one 🟡)
A1–A6 ✅ this session (`2707b79`/`71f8e8e`). A7 (hardcoding-candidate → tracked-to-closure) lands after C
(the disposition store) gives it a place to be dispositioned `must-fix` + reconciled. No new build for A
except A7-after-C and keeping the gates green as the other lanes land routes/registries (the gates VERIFY
their additions — that's the synergy, not a build).

## Group F — the convergence-round lens (last)
No net-new build: the detectors already run tree-wide; F = running them as the structural half of the
convergence sign-off (adversarial-to-appearance, can't be green-painted), paired with guided-review's by-use
operator path. The work is the convergence-round orchestration (co-owned), not new coherence code.

---

## The loop's build order (what the cron picks up, dependency-first)
**B2** (fold the FORM-lint when handed) → **C** (the disposition store: C1→C2→C3→C4→C5→C6) → **D** (the
calibration harness: D1→D2-single-config→D3→[D4 after E2]) → **E** (declaration→validator→registry→
build_coherence_info; runner handed to cognition) → **A7** (after C) → **F** (convergence round).
Each criterion: build in my file territory → verify by use (run it, adversarial re-check) → `company suites`
green → claim-release + commit per criterion → mark the criterion ✅/🟡 in the Completion Criteria.
**Engine-independent prefix (build now, unblocked): B2-framework, C (all), D1–D3, E1–E2, E4.** Only D4's save
+ E3's runner + D2's N-config-LLM form wait on cognition's C.
