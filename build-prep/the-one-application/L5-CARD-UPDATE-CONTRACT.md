# L5 — the decision-card UPDATE contract (RHM proposes → operator accepts → re-render)

**Status:** ✅ FINALIZED — co-drafted with fork (floors below), settled 2026-06-22. Design-not-code: built when
sequenced BEHIND the #1b operator-token primitive (the accept-floor keys on it), and per the lead's
be-responsible guard the enforcement-flip coordinates with projection's surface-mint so Tim's live decides
never break. The POSTURE is authored now as a Tim-facing decision-card (decisions/card-refine-posture.py). Tim
may re-prioritize post-use. (composition 2026-06-21 → finalized w/ fork 2026-06-22)

## The shape (mirrors decision_take/compose_state — the ONE mechanism, no parallel)

The RHM can refine a decision card (sharpen the meaning, add/edit an option, tighten legibility). Like the
take, the refinement is a MARK on the decision address; the row never mutates; the resolver composes the
effective definition. Registry-is-truth applied to the DEFINITION, exactly as compose_state applies it to STATE.

- **mark_type `decision_update`** (new; mirrors `decision_take`/`decision_retract`):
  `{target: decision://global/<id>, value: {field, value}, by, ts}` · value_shape=free · direction=surface.
  `field` = a WHITELISTED content path; `value` = the proposed new value; `by` = the proposer (the RHM).
- **compose extension** — a definition-fold beside compose_state: fold the ACCEPTED `decision_update` marks
  (per-field, latest-by-ts) onto the row → the effective card definition. The row stays the pending
  DEFINITION; accepted updates resolve on top. The resolved VIEW, never a stored mutation.

## ★ Gating = A: propose-then-accept (the floor — an AI must not silently rewrite what Tim decides ON)

decision_take/retract sit behind the **#1b genuine-operator-attribution floor (operator-only)**. An RHM update
is the AI — a DIFFERENT actor — so it CANNOT share that floor. The binding precedent is already in the codebase:
`/api/run-in-channel/propose` returns a structured proposal and explicitly does NOT execute — *"the face
proposes, the human runs it through the gated path."* That is the fabric's floor for AI-initiated actions.

⟹ **An un-accepted `decision_update` does NOT compose into the definition.** The proposal is SHOWN on the card
(attributed to the RHM, with its rationale) but the effective definition is unchanged until an OPERATOR ACCEPT
(a gated, #1b-floored mark — `decision_update_accept`, the operator twin) applies it → then it composes. A
reject/retract twin lets Tim drop a pending or applied update (append-only, audit-preserving, like
decision_retract). Model A by construction prevents the AI from changing what Tim is deciding on.

**The posture is TIM'S call (authorize-flavored, per the subtype model) — surfaced through the surface itself:**
whether the RHM may refine decision cards at all, and that it must propose-for-accept (A) vs apply-reversibly
(B). composition will author this as a Tim-facing decision-card (subtype=authorize, owner=tim) — the elegant
self-reference: a decision ABOUT the decision-surface, decided THROUGH it. A is the safe default we build toward.

## ★ Hole 1 — update × an already-DECIDED card (must resolve; state-fold and definition-fold are COUPLED)

`compose_state` sets `decided_value` = the take's stored label STRING and never re-validates it against the
current `options`. So an accepted update that edits/removes the decided option leaves `state=decided` with a
`decided_value` pointing at a label no longer in `options` — orphaned, silently incoherent. **The contract MUST
decide** (open question for fork's floor): an accepted update that changes a DECIDED card's option set →
RE-OPENS it (implies a decision_retract → pending → Tim re-decides) — OR is blocked while decided — OR forces a
re-decision. Lean: an options-touching update to a decided card re-opens it (a stale decided_value is the
silent-drop class). Updates to non-decided-bearing fields (legibility/meaning-wording) don't re-open. Verify the
take/update interaction in compose; do NOT ship the definition-fold assuming a guard exists.

## ★ Hole 2 — the updatable-field WHITELIST (an RHM that can re-subtype can silently un-queue Tim's decision)

`value={field,value}` over an arbitrary dot-path is too wide. **Updatable = CONTENT fields only:** `meaning` ·
`options[]` · `legibility` · `dimensions` · `device`. **NEVER** `subtype` (moves owner tim↔fabric = in/out of
Tim's queue + card_variant + required_elements — the whole blast-radius just closed), `id`/`address` (breaks
resolution), `scope` (moves the frame). The contract fail-louds on a non-whitelisted field. The RHM refines
CONTENT, never the row's structural identity.

## Co-draft asks for fork
1. The RHM-proposes shape: how the brain emits `decision_update` → territory_write (the write leg + actor
   attribution `by=rhm`), distinct from the operator decide-path.
2. The accept floor: `decision_update_accept` behind the #1b operator floor (the operator applies the proposal).
3. Hole 1: the decided-card interaction (re-open / block / re-decide) — your floor call.

---

## fork's CO-DRAFT — the FLOORS (2026-06-22, design — composition finalizes the contract)

Code-grounded against `mark_types/decision_take.py` + `decision_retract.py` + `compose_state` (the ONE
mechanism — registry-is-truth on the DEFINITION, mirroring how it's applied to STATE) + the #1b floor
(`territory.py:506`, `bridge.py:594/3148` — the X-Operator-Session token-mint).

### Floor 1 — the RHM-proposes write-leg (`decision_update`, INERT until accepted)
- **mark_type `decision_update`** (new file; id==stem; mirrors decision_take): `{target: decision://global/<id>
  (canonical), value: {field, value}, by: "rhm", rationale?, ts}` · value_shape=free · direction=surface.
- **The RHM emits it floor-clean** (a PROPOSAL, not an apply): `suite.mark(canonical, "decision_update",
  value={field,value}, by="rhm", rationale=…)`. Writing it is read+propose — it is INERT (does NOT compose
  into the definition; Floor 2 gates the apply). Shown on the card, attributed to the RHM + its rationale —
  exactly the `/api/run-in-channel/propose` precedent ("the face proposes, the human runs it").
- **Distinct from the operator decide-path by ACTOR**: decision_take = the operator's CHOICE (#1b-floored,
  by=operator); decision_update = the RHM's REFINEMENT-PROPOSAL (inert, by="rhm"). The `by` actor is what the
  compose-fold + the accept key on — an AI write can never be mistaken for an operator decide.
- **WHITELIST (Hole-2, composition's settled constraint) lives at the writer + the fold (one source):** `field`
  ∈ {meaning, options, legibility, dimensions, device}. Fail-loud on subtype/id/address/scope (the structural
  blast-radius). The RHM refines CONTENT, never the row's identity.

### Floor 2 — the accept floor (`decision_update_accept` + the definition-fold)
- **mark_type `decision_update_accept`** {target: canonical, value: <accepted update's ts/ref>, by: operator,
  ts} — the OPERATOR twin, behind the SAME #1b genuine-operator-attribution floor decision_take/retract sit
  behind (no operator token ⇒ refused; an AI CANNOT write it — different actor).
- **`compose_definition(row, marks)`** (beside compose_state — the resolver does both): fold the
  `decision_update` marks that have a matching `decision_update_accept` (per-field, latest-accepted-by-ts) onto
  the row → the effective card DEFINITION. An un-accepted update does NOT compose (visible proposal only). A
  `decision_update_reject` twin (operator) drops a pending/applied update (append-only, audit-preserving, like
  decision_retract). The row never mutates; the resolved VIEW composes. ⟹ Model A by construction: the AI
  proposes, only an operator ACCEPT (gated) applies.

### Floor 3 — Hole-1 (decided-card interaction): **RE-OPEN on an options-touching accepted update** [fork's call]
- **DECISION (convergent — contract lean + lead lean + fork):** an accepted `decision_update` that touches the
  OPTIONS (add/edit/remove/reorder) of a **decided** card RE-OPENS it — the fold emits/implies a
  `decision_retract` (state → pending) so Tim RE-DECIDES against the new options.
- **WHY:** `compose_state`'s `decided_value` is the stored option-label STRING and NEVER re-validates against
  current `options` (verified — no guard exists). An accepted options-change leaves state=decided with a
  `decided_value` that may no longer be in `options` → orphaned, silently incoherent (the silent-drop class).
  Re-open = the honest re-present; block is too rigid (can't refine a decided card); silent-keep IS the
  incoherence. **state-fold and definition-fold are COUPLED here — build the coupling explicitly; do NOT ship
  the definition-fold assuming compose_state guards it.**
- **SCOPE:** ONLY options-touching updates re-open. Non-decided-bearing fields (meaning-wording, legibility,
  dimensions, device) do NOT re-open (the decided_value stays valid).
- **SURFACED (Tim-facing edge, NOT gating him):** re-open vs block vs re-decide — designing to RE-OPEN (the
  agreed safe default); Tim can name a different feel for refining-a-decided-card. Proceeding on re-open
  (minimize-gating — a well-reasoned floor, his to override).

---

## ✅ FINALIZED CONTRACT (composition's contract + fork's floors, converged 2026-06-22)

The settled shape, one place — **3 mark-types** (mirror decision_take/retract; id==stem; registry-is-truth on
the DEFINITION, exactly as compose_state applies it to STATE; no parallel mechanism):
- **`decision_update`** — the RHM's refinement PROPOSAL: `{target: canonical, value:{field,value}, by:"rhm",
  rationale?, ts}`. INERT — does NOT compose until accepted (shown attributed + with rationale). Whitelist
  enforced at writer + fold (ONE source): `field ∈ {meaning, options, legibility, dimensions, device}`;
  fail-loud on `subtype`/`id`/`address`/`scope` (the structural blast-radius).
- **`decision_update_accept`** — the OPERATOR twin, behind the **#1b operator-token floor** (an AI cannot write
  it — different actor). Applying it composes the update into the definition.
- **`decision_update_reject`** — the operator drop of a pending/applied update (append-only, audit-preserving).
- **`compose_definition(row, marks)`** (beside compose_state — the resolver does both): fold the ACCEPTED
  updates (per-field, latest-accepted-by-ts) onto the row → the effective DEFINITION. Row never mutates.
- **Gating = A** (propose-then-accept) — the AI proposes (inert), only the gated operator-accept applies; the
  `/api/run-in-channel/propose` floor for AI-initiated actions.
- **Hole-1 = RE-OPEN** — an accepted OPTIONS-touching update to a DECIDED card emits a `decision_retract` →
  pending → Tim re-decides (state-fold ⟷ definition-fold coupling built EXPLICITLY, not assumed). Only
  options-touching re-opens; wording/legibility/device updates don't.
- **Hole-2 = content-whitelist** — never the structural identity fields.
- **Build-sequencing:** follows the #1b operator-token primitive; the enforcement-flip coordinates with the
  surface-mint (the be-responsible guard) so Tim's live decides never break.
- **POSTURE = Tim's** (authorize, owner=tim): `decisions/card-refine-posture.py`, grounded in THIS doc — Tim
  decides whether the RHM may refine cards + the propose-then-accept floor, THROUGH the surface itself.
