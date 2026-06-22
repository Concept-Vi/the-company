# HARVEST — composition lane (the type/contract system, the decision-surface, the resolver spine)

**author_session:** ch-o1wy1t07 (composition) · **transcript:** e16c0a10-…jsonl (2026-06-15 → 06-22) ·
**filed:** 2026-06-22 (the Harvest/Retirement protocol, board://item-78c63045)

This is composition's honest current-state VIEW — the COMPLEMENT to recollection's transcript-dragnet (which is
the session-attributed backbone of *what was built*). Each record LEADS with its honest status. ★ Verification
provenance is split: **verified-by-me** = confirmed by composition's OWN tool-output (curls / schema-validation /
discovery runs I ran + saw); **reported-by-[lane]** = taken on another lane's claim, NOT independently confirmed
by composition (the keystone was "certified at-bar 5×" via cross-lane relay and was text-in-boxes — so this
distinction is deliberate). No self-certified "done."

---

## A · The decision-surface + the operator-loop content engine
**STATUS: data/grounding layer VERIFIED-BY-ME · render REPORTED-BY-PROJECTION · the loop-CLOSE-by-Tim's-real-decide ATTEMPTED-UNVERIFIED (the central gap).**
- **about:** the resolution-first decision chain (address→type→archetype→render→RHM-explain→decide→write-back→
  re-resolve); 25 `decisions/*.py` rows at Tim's altitude.
- **verified-by-me:** the `/api/decisions` feed resolves subtype+owner+required_elements for all rows (I curled
  it); all 25 schema-pass + compile (I ran the checks); a live `/api/decision/explain` returns the right
  subtype+policy + grounds (I curled merge-sa-authorize + card-refine-posture).
- **reported-by-projection:** the grounded walk-through "15/15 by-sight, both viewports." NOT confirmed by me.
- **★ ATTEMPTED-UNVERIFIED — THE HONEST GAP:** the operator-loop has NEVER closed on a real Tim decide.
  `decided-signal=0`; every card is `pending`. Tim said "yes" to the posture-card in WORDS, but the registry is
  truth and no `decision_take` mark exists (no agent writes it — the ghost-take guard). So "the operator loop
  works" is **built + fabric-verified, NOT Tim-verified.** This is the bar that stayed open all session.
- **relations:** commits f605939·149fd77·8b5a169·5b7acbb (the chain + HOLE-1 canonicalize) · decisions/*.py ·
  RESOLVER-CONTRACT.md.
- **open:** Tim's first real decide-through-the-surface (his tap) remains the uncrossed line.

## B · The subtype + owner-resolution system + the silent-drop catch
**STATUS: VERIFIED-BY-ME.**
- **about:** `decision.subtype` → `decision_subtypes/*` → {card_variant, explanation_policy, required_elements,
  owner}. The file-discovered registry (the one mechanism).
- **verified-by-me:** found the silent-drop by my own script (10 of 24 rows untagged → resolved no owner →
  absent from Tim's queue, incl. the frame-first substrate-home); fixed → 24/24 tagged, all owner-resolve, the
  feed carries owner+required_elements (curled); tag-then-require schema gate landed, all rows re-validate
  (ran it), no C5 break.
- **claim/law:** **resolver-input-must-be-required** — deleting a resolver fallback to be "registry-true"
  without making the input contract-required makes the drop SILENT (a memory: resolver-input-contract-required).
- **relations:** commits 51d5256·2804164·0b850f7·38ccd78 · SUBTYPE-COVERAGE-GAP.md · decisions/AGENTS.md.

## C · The grounding-provenance contract (explanation_source / HOLE-2)
**STATUS: contract VERIFIED-BY-ME · the full 21/21 resolve REPORTED-BY-RECOLLECTION (2 cards verified-by-me).**
- **about:** `explanation_source` = a traceable POINTER an explanation traces THROUGH to real source content,
  never a stored prose claim (the HOLE-2 law — claim-grounded-in-a-claim is the trap).
- **verified-by-me:** the contract + the backfill (21 cards' pointers set, section/JSON-key-anchored for
  per-item scoping); I curled 2 cards grounding live (merge-sa, card-refine-posture).
- **reported-by-recollection (via lead):** the per-pointer 21/21 PASS sweep + the theorem-forks asset-grounded.
  NOT independently run by me.
- **law/memory:** grounding-traces-pointer-not-claim; Level-3 (captured artifact) is the bar, Level-4 (Tim's raw
  words) forward-only.
- **relations:** commits 8e3d1f1·beb34e9·67625e0·157622c·0ed266c·a730815·a3454b8 + the 12 backfill commits.

## D · The resolver contract (RESOLVER-CONTRACT.md §1–8) + the axes registry
**STATUS: contract VERIFIED-BY-ME (authored) · resolve_slot-live REPORTED-BY-FORK · device-axis migration ATTEMPTED-UNVERIFIED · design-axis populate OPEN-LOOP.**
- **about:** resolve(invariant, coordinate)→surface as the AUTHORING layer over fork's resolve_slot; axes-are-
  registries (`axes/*.py`, 8 axes); §8 the extraction resolver-variable (prompt/schema ARE resolvable variables).
- **verified-by-me:** §8 authored + aligned to Tim's adaptive-stepped cascade (his L99 decision resolved my
  read-vs-extraction fork); `explanation_policy_for` resolves all 4 subtypes correctly (ran it); the 8 axes
  discover clean incl. the naming-collision catch (design ≠ the grain resolution — both distinct, ran it).
- **reported-by-fork (via lead):** resolve_slot LIVE in run_role (prompt/schema/thinking against the coordinate).
  NOT confirmed by me.
- **ATTEMPTED-UNVERIFIED:** the device-axis MIGRATION (projection consuming /api/resolve as CSS vars) — authored
  in the contract, projection's to verify by-use; not confirmed by me.
- **★ OPEN-LOOP (finish-to-bar, NOT done):** `axes/design.py` value_source POPULATING is **pending
  recollection's bounded 10,568 re-bake** — the axis is registered + the `<dim>:<context>->value` vocab-gate
  passed (verified-by-me), but value_source-populated is unverified until the re-bake lands + I confirm it. Named
  dependency, not closure.
- **relations:** RESOLVER-CONTRACT.md · commits c43601e·400e13f·e42863b·c3d6106·2af4eba · axes/design.py·resolution.py.

## E · The L5 decision-card UPDATE contract (RHM proposes → operator accepts)
**STATUS: contract VERIFIED-BY-ME · the mechanism BUILT (commits exist, fork) but ATTEMPTED-UNVERIFIED (unexercised by Tim).**
- **about:** the RHM proposes a card refinement (a `decision_update` mark, inert) → an operator ACCEPT
  (#1b-transparent, scoped to the accept-route, NOT full decide-gating-A) applies it → compose_definition folds it
  → re-render. Gating=A (propose-then-accept, the run-in-channel/propose floor). Hole-1=RE-OPEN on options-touching
  updates to a decided card. Hole-2=content-whitelist (never subtype/id/address/scope).
- **verified-by-me:** the contract (authored, finalized, co-drafted with fork); the posture-card
  (card-refine-posture, authorize/owner=tim) renders+grounds in the feed (curled).
- **built-but-ATTEMPTED-UNVERIFIED:** the mechanism (decision_update/accept mark-types + compose_definition +
  the accept route + projection's accept-wire) — commits 9d06d79·9a5669f·0d9ac76·e3b9c84 EXIST (fork/projection),
  but I did NOT verify by-use, and **Tim has not exercised it** (the loop's not closed). Built ≠ used.
- **the recursive move:** Tim decided the posture-card YES *in words* + broadened it ("update whatever's on
  screen") — but per A, that's a capability-yes, NOT a recorded decide; the loop-close is still pending his tap.
  I caught + refused loosening the #1b floor on that inference (it's a Tim security-decision, not ours).
- **relations:** L5-CARD-UPDATE-CONTRACT.md · commits a5dc258·46556b9·ee51ef5·9539f76 · decisions/card-refine-posture.py.

## F · The archetype catalog
**STATUS: contracts VERIFIED-BY-ME (schema-validated) · decision-card/graph/session-card render REPORTED-BY-DNA/PROJECTION · the rest DESIGNED/ATTEMPTED-UNVERIFIED.**
- **about:** decision-card · graph · diagram · selector · instrument · spatial-material · zones · lanes ·
  session-card — each an archetype.schema instance (allOf $ref); the slot-shape law + edge-binding lifted to
  the parent.
- **verified-by-me:** the schemas validate (instances allOf the parent; ran it); the slot-shape-conformance law
  + the edge-binding scope-correction (graph·diagram only) are in the contract.
- **reported-by-dna/projection:** decision-card (binary/n-panel), graph (channel-view), session-card render
  live. NOT confirmed by me.
- **DESIGNED / not-rendered (to my knowledge):** diagram · selector · instrument · spatial-material · zones ·
  lanes — contracts authored, render pending/unconfirmed.
- **relations:** schemas/vi-vision/v1/*.schema.json · commit d74739b (slot-shape law).

## G · The factory backend (atoms/molecules/organisms) — GAP RECORD
**STATUS: UNKNOWN-TO-ME (stale). Last I verified: Tier-1 organism through the real contracts, by-sight, ~2026-06-17.**
- I built/verified a Tier-1 organism (a molecule of atoms) through the REAL composition contracts, verified by
  sight (~06-17, screenshots). Since then I shifted entirely to the decision-surface + resolver; I have **NOT
  re-verified the factory's current state.** docs/build/02-factory-backend/BUILD_PLAN.md exists. Do not trust a
  confident "done" here from me — current state unknown to me; recollection's transcript-dragnet + the BUILD_PLAN
  are the sources. Honest gap, fail-loud.

## H · The Face Pipeline / Claude Design integration — GAP RECORD
**STATUS: DESIGNED · build-state UNKNOWN-TO-ME.**
- The translate pipeline (ingest→tag→compose→validate→reconcile→register; ~80% reuse) was DESIGNED
  (FACE-PIPELINE-TRANSLATOR.md). I did NOT build or verify it; whether any lane built it since is unknown to me.
  Designed, not verified. Honest gap.

## I · The V-symbol / early identity work — GAP RECORD (handed to DNA)
**STATUS: early work (~2026-06-16), now DNA's lane.**
- Early: the V home with the company gold (#E3C421), the mode-as-colour cascade captured. The identity (look/
  voice/tokens) is DNA's lane now; I do not own or track its current state. Pointer, not a claim.

## J · The durable LAWS composition established (verified-by-application)
**STATUS: VERIFIED-BY-APPLICATION — each caught a real defect this session.**
- **resolver-input-must-be-required** (caught the silent-drop, B). **grounding-traces-a-pointer-not-a-claim /
  HOLE-2** (the bleed fix, C). **closed-loop-is-the-unit, not pieces** (Tim's correction; the false-green
  discipline; my own "you decided through the surface" was premature — corrected). **the data-bound device /
  decoration-ban** (a device must encode real trade-off data or not render). **the resolver as the 4th
  primitive** (one invariant resolves against a coordinate, never variants). **default-to-wrong on a security
  claim** (refused loosening the #1b floor on a capability-yes inference, E).
- These are the reusable spine — held in the memory store; their value is they each caught a real false-state.

---

## COVERAGE LEDGER (composition's artifacts — harvested | excluded+reason)
- HARVESTED above: decisions/*.py · decision_subtypes/* · schemas/vi-vision/v1/* · axes/* · RESOLVER-CONTRACT.md
  · L5-CARD-UPDATE-CONTRACT.md · SUBTYPE-COVERAGE-GAP.md · the §8 + grounding + backfill commits.
- STALE/GAP (honest unknown-to-me): the factory backend (G) · the Face Pipeline (H) · the V-symbol/identity (I).
- EXCLUDED: other lanes' commits in the shared log (projection/fork/DNA/recollection) — theirs to harvest;
  named here only as cross-lane dependencies (L5 needs fork's build + Tim's accept; the design axis needs
  recollection's re-bake; the grounding 21/21 + renders are reported-by-lane, not mine).
- ★ The one finish-to-bar OPEN LOOP that is mine: axes/design.py value_source populate (D) — pending the re-bake.
