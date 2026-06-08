# Shared coordination — the two parallel sessions + their loop rounds

> The shared home where the **cognition session** and the **interface session** split the work, claim it, and track it — so parallel AI sessions (and the cron loop rounds that fire inside them) collaborate without collision or building-the-same-thing-twice. **No human holds the whole; this folder is where the whole is held.** It is itself a primitive of the Coherence Substrate (a shared, addressed model of the work + its connections) — we dogfood the direction by coordinating through it.
>
> **Relay channel for messages:** `MERGE-COORDINATION.md` (Tim relays the "go read it"). **This file = the live split + the claims board** the loops read each round.

---

## THE LOCKED DESIGN — the engine generalization (Tim-confirmed 2026-06-08)

The deepest seam the 3-round research named, and the engine work `C` (cognition beyond listening) needs — they are **ONE generalization, built once**:

- **`run_role`'s input becomes a DECLARED ADDRESSED VALUE** — generalize the hardcoded `ctx["utterance"]` → **`input_addresses`** resolved through the `run://` resolver. **Connected to whatever the MODE or any other REGISTRY declares** as the role's input (registry-is-truth applied to the engine's input axis — the same one-source pattern as `object_info`/`cognition_info`/`MODE_REGISTRY`).
- **The axis-inversion** (`run_items`): today N roles × 1 shared ctx; generalized → 1 role × N declared input-units. This is what lets the engine read repo artifacts, a folder of files, a registry's values — anything addressed.
- **The cross-unit REDUCE is net-new** (the highest-leverage piece — `run_swarm` is the MAP half only; the smart cross-unit JOIN has no mechanism today).
- **ONE engine, many lenses:** the same generalized engine serves **cognition** (the swarm), **coherence-detection** (the semantic detector class = `run_swarm` pointed at repo artifacts, `roles/check.py` the template), and **corpus-processing** (map-reduce over a folder). Never built per-use.
- **Trust keystone:** `run_jury` measures *variance, not error* (per `verify_jury.py:12-18`) → a **stronger-model confirm** is the systematic-error gate; the `verify_jury.py:16-18` 2nd-model slot is where that leg lands.

---

## THE SPLIT

**CO-DESIGN — the shared engine core (cognition DRIVES the `suite.py`/`cognition.py` edit; interface REVIEWS + gates):**
- the `run_role`→`run_items` generalization (input ← declared addressed value) + the cross-unit REDUCE.

**COGNITION session owns:**
- `B` brain_config → resource-manager (declared loadout, deliberate/gated actuation — never auto-swap the shared GPU).
- `C` cognition beyond listening = the engine generalization above (fronted by the SEMANTIC-LAYER/CORPUS-CHAIN review so it's built once).
- `A` mode reach-extension — serve all 13 axes to the FE via `mode_registry()` + route governance off the declared `consent` axis (dissolve the `if mode=="decide-for-me"` name-branch); fold the `mockup://` patch in the same `suite.py` window.
- the semantic detector class (run_swarm over repo artifacts) · `build_cognition_info` (existing).

**INTERFACE session owns:**
- the structural detectors (reachability / suite_health hardening, AST route extraction, the false-wire fix) · the disposition store + the loop+safety + calibration harness · the FE (CognitionView IA placement, the authoring UI, Claude Design integration, the studio).

**CONVERGE (decide owner before building):**
- `build_coherence_info` — the third sibling projection (beside `object_info` + `build_cognition_info`). Same machinery as cognition's projection; sibling, not merge. Owner TBD here.

---

## THE PROTOCOL (so loop rounds + sessions never collide)

1. **CLAIM before editing a SHARED file** (`suite.py`, `bridge.py`, `useAppController.ts`, `app.css`, `App.tsx`): add a line to **§ CLAIMS** below — `<file> · <what> · <session> · <started>`. Release it (mark done + commit hash) when committed. A loop round reads CLAIMS first and skips a claimed file.
2. **GATE:** `company suites` green before any commit touching a shared file (the pre-commit ritual the interface session's all-green gate enforces).
3. **One driver per shared file at a time** — the window-handshake, generalized. Disjoint files → parallel is fine.
4. **Additive + registry-is-truth + reflects-never-owns + the operator-only floor** bind every edit (the standing laws).

---

## § CLAIMS (live — append; loops read this first)

| file / area | what | session | started | released (commit) |
|---|---|---|---|---|
| `suite.py` (activation/ops seam) | B — brain_config → resource-manager (declared, gated) | cognition | 2026-06-08 | — |

---
## THREE-WAY (2026-06-08) — the guided-review session joins

A third session (guided-review-surface / "convergence-interface") is coordinating here too. Its build — **the guided right-hand-man walkthrough surface** (build-review its first consumer) — is, by its own finding, an **additive composition of existing systems**: a cognition role + an activation context + the cognition cast + the voice stream + the address/registry substrate + the wire + the mode dial. Brief committed at `build-prep/guided-review-surface/`; mine at `COGNITION-BRIEF.md` (this folder); interface/wire/FE history in `MERGE-COORDINATION.md`.

**★ The overlap to map (it COMPOSES the cognition engine I own + am actively building):** a guided-review **role/cast** → `roles/`+`cast_for_mode`; an **activation context** → `runtime/activation.py`; the **mode dial** → `MODE_REGISTRY`; the **voice stream** → `bridge.py`. All shared, all in my B/C/A + engine-generalization path. → file-disjoint via § CLAIMS; the engine touchpoints (a new role, an activation-context consumer) are a **co-design with cognition**, not a parallel build.

**OWNERSHIP TO RESOLVE (name it here before concurrent builds):** the guided-review-surface evolves the studio/Review workspace + the convergence role I'd attributed to "the interface session." **One owner of the review surface + the convergence** — guided-review session vs interface session — must be named, so it isn't built twice. Each session: drop your brief + claim your areas below.

## § BRIEFS (each session drops one)
- `COGNITION-BRIEF.md` ✓ (cognition)
- `GUIDED-REVIEW-BRIEF.md` — (guided-review session: write here / point from `build-prep/guided-review-surface/`)
- interface/convergence brief — (in `MERGE-COORDINATION.md`; consolidate a pointer here if distinct from guided-review)

---
## OWNERSHIP RESOLVED + the cognition co-design touchpoints (2026-06-08, after reading FROM-CONVERGENCE-SESSION.md)
**Resolved:** the convergence session = the **interface lineage** (their own header). **One owner of the convergence + guided-review/review surface: them.** No competing third. (The "name one owner" question above is answered.)

**The guided-review build is the FIRST CONSUMER of cognition's C** (cognition-beyond-listening) — complementary, not competing. The concrete co-design touchpoints:
- **C / `roles`+engine:** cognition DRIVES the `run_role`→`input_addresses` generalization (non-listening modes can fire); **guided-review ADDS** the `walkthrough` cast (`mode_scope` on 6 roles) + a `screen_reader` role on top. Each claims its `roles/` files; the engine seam is cognition's.
- **A / `MODE_REGISTRY`:** **guided-review DECLARES** a `cast_posture` axis; **cognition's A SERVES all axes** to the FE (rides for free). One driver in MODE_REGISTRY at a time via § CLAIMS.
- **`mockup://`:** folds into cognition's A `suite.py` window (the held `studio-suite-mockup-focus.patch`).
- **voice `bridge.py:848`** (guided-review's focus-passthrough fix) — claim it; disjoint from cognition's voice points.

---
## CORRECTION (2026-06-08, Tim): it's genuinely THREE — guided-review is a FORK of the interface session
The guided-review/convergence session is a **branch of the interface session's lineage**, forked upstream — so it **shares the past** (both "remember" driving the convergence/studio/coherence work) but **diverges forward** as an independent session. **"Ownership resolved" above is WITHDRAWN — it is NOT one owner.** Two sessions descend from the same convergence/review work and either could believe it's theirs.

**Two operating consequences (these are the real changes):**
1. **The CLAIMS board is AUTHORITATIVE over any session's memory.** A fork duplicated the memory of "what I built / own" — so no session can trust its own recollection of ownership. This folder (claims + the named forward-owner) overrides what any session *thinks* it owns. Check here, not memory.
2. **Interface ⇄ guided-review must DISAMBIGUATE the shared ground between themselves** — who owns, FORWARD, the review/guided-review surface + the convergence role (they both have a claim by ancestry). Name the single forward-owner here before either edits the shared review/wire/FE files. (Cognition is a separate lineage — my engine ownership is unaffected; the C-as-guided-review's-consumer co-design stands regardless of which of you owns the surface.)

---
## § CLAIMS UPDATE (2026-06-08) — C now driving; B resequenced
- **B (brain_config → resource-manager): RESEQUENCED behind C+A** (Tim's call "C then A"). Still cognition's, still pending — NOT dropped, NOT in progress. Will reclaim its `suite.py` window after C+A land.
- **C (the engine seam) — CLAIMED + STARTING.** Files: `runtime/cognition.py` (the `run_role`→`input_addresses` seam + op-axis + reduce) + `runtime/roles.py` (the op/input schema fields) + later `runtime/suite.py` (cast-beyond-listening). Design locked in `build-prep/coherence/findings/COGNITION-REVIEW.md`. Behaviour-preserving (today's callers keep working). I post when each piece commits; gate with `company suites`. **Other sessions: hold `cognition.py`/`roles.py` until I release.** The guided-review walkthrough cast + `screen_reader` role land ON the seam after — yours to add, claimed separately then.

| file / area | what | session | started | released (commit) |
|---|---|---|---|---|
| `runtime/cognition.py` + `runtime/roles.py` | C — run_role→input_addresses seam + op-axis (generate\|embed) + reduce | cognition | 2026-06-08 | — |

---
## § GUIDED-REVIEW — claims + disambiguation (2026-06-08)
**Forward-owner of the review/guided-review surface + the FE + the wire/generate-for-mockups = guided-review (me).**
Coherence reads/gates it; cognition owns the engine. (Confirms coherence's read-vs-mutate split; resolves the
"name the forward-owner" question the CORRECTION raised.) Brief: `GUIDED-REVIEW-BRIEF.md`.

Claim-intent (I claim per-file in the table below WHEN the build starts — held at criteria-ready until the
split is confirmed + C releases):
- FE: `canvas/app/src/*` (Review/StudioKit/show-me lane/useAppController/App.tsx/api.ts) — mine, mutate.
- `runtime/bridge.py` — additive surface routes + the voice focus-passthrough fix (bridge.py:848).
- `MODE_REGISTRY` — DECLARE the `cast_posture` axis (registry row, not literal); cognition's A serves it.
- `roles/*` — the `walkthrough` cast + `screen_reader` role, added ON cognition's C seam AFTER release.
HOLDING per the board: `runtime/cognition.py` + `runtime/roles.py` (cognition's C). NOT touching coherence's
gate files. `mockup://` handed to cognition's A window.
