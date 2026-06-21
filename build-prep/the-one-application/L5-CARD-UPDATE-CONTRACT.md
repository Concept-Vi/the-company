# L5 — the decision-card UPDATE contract (RHM proposes → operator accepts → re-render)

**Status:** DESIGN PROPOSAL for co-draft with fork (the RHM-proposes shape + the #1b floor). NOT built — the
loop is fabric-complete + Tim may re-prioritize post-use; this is the contract, not code. (composition 2026-06-21)

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
