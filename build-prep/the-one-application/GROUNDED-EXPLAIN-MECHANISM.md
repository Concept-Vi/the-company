# THE GROUNDED WALK-THROUGH — how it's set off + how it works (the mechanism map)

*Commissioned by Tim (2026-06-21): "investigate how it's set off and how it works — delicate context resolution + address resolution, multiple parts." Investigated by 3 parallel read-only agents (trigger · context-resolution · address-resolution); synthesized by projection. Evidence is code-grounded (file:line), Observed unless marked Inferred. This is the map the L1 fix is driven against — it spans 3 lanes (projection · recollection · composition) and the upstream capture.*

## THE CIRCUIT (Tim's frame)
```
decision card opened
   → [1 TRIGGER]  which door does "Ask about this" knock on?
   → [2 CONTEXT]  what memory does that door pull into the explanation?
   → [3 ADDRESS]  where does that memory live, and does the decision point at it?
   → the explanation
```
Three serial joints. ALL must connect for a genuinely-grounded walk-through; today each is broken in a different way. That is the "multiple parts."

## PART 1 — HOW IT'S SET OFF (the trigger) — projection's lane
- The card's "Ask about this", the V/RHM ask, and the per-unit brain ALL route to the GENERIC `POST /api/claude/turn` via the single constant `CLAUDE_TURN = '/api/claude/turn'` (surface/app/public/gallery/fork-brain-core.js:21; bound to decision cards at fork-gallery-brain-hooks.js:86-91 on `decision:rendered`).
- The grounded compose route `POST /api/decision/explain` (runtime/bridge.py:2344) is **completely unwired client-side** — zero references in any surveyed surface module.
- ⟹ **Today the grounded door is never knocked on from the surface.** Even a card that WOULD ground correctly is explained by the generic streamer (`_claude_stream`, bridge.py:2037), which uses `territory_prose(address)` — not the three-half grounded compose.
- THE FIX (mine, built + HELD): redirect the decision-card ask → `/api/decision/explain`. Wire is poised + shape-verified; held until coverage (Part 2) is complete — one clean flip, no partial-coverage inconsistency.

## PART 2 — CONTEXT RESOLUTION (the grounding retrieval) — recollection's lane
`explanation_grounding(SUITE, decision)` (runtime/decision_memory.py:421-597) builds the `block` the model explains from. On the DEFAULT interactive path it contains ONLY the card's own authored fields:
1. `meaning` · 2. `legibility.is` · 3. `options[label+implication]` · 4. `legibility.why` (decision_memory.py:557-567).
Two genuine-provenance channels exist but BOTH gate to empty on the fast path — by design, as defences against the earlier wrong-decision "bleed":
- **Gate 1 — provenance pointer:** `WHERE THIS CAME FROM` is appended only if `_provenance_text(explanation_source)` resolves non-empty (decision_memory.py:573). Absent on most decisions → empty.
- **Gate 2 — corpus admission:** `RELATED BACKGROUND` requires `rerank_score >= 0.5`, but `rerank=False` by default (latency: ~5-18s→57s if on) → no `rerank_score` present → zero corpus admitted (decision_memory.py:579-582).
- ⟹ **Root cause of "restates the card":** for any decision lacking `explanation_source`, the model receives only the card's own text → it can only rephrase it. NOT a retrieval bug — the retrieval fires correctly; it's the INPUT CEILING. Both guards are correct; together they reduce the default to a restatement.
- NOTE (design tradeoff, surface it): on the FAST path, genuine grounding comes ONLY from the authored `explanation_source` pointer (Gate 1) — live corpus search (Gate 2) is deliberately off for latency. The deep/slow path (rerank=True) gets corpus background.

## PART 3 — ADDRESS RESOLUTION (decision://<id> → record + grounding) — composition/upstream
- The decision record's full field set: `DECISION_FIELDS = (id, address, meaning, options, explanation_source, scope, legibility, subtype, owner)` (runtime/decision_registry.py:52). **`explanation_source` is the ONLY provenance-bearing field.** No `origin`/`raised_by`/`gap_ref`.
- `resolve_address(decision://global/<id>)` returns the declared row + composed state (marks) (runtime/cognition.py:1095-1125). It does **not** dereference `explanation_source` or reach corpus — the pointer rides as a bare string; the explain turn resolves it separately.
- ⟹ **Verdict: genuine provenance is PARTIALLY STORED, NOT reachable via the address.** Only ~8-9 of ~21-24 decisions carry `explanation_source`; the rest have NO provenance link at all. For a decision whose origin (the gap that raised it) was never written into a board item / corpus, there is nothing to point at — the provenance is ABSENT UPSTREAM (always-more-to-the-theorem: capture is upstream of retrieval).

## THE SERIAL GATE CHAIN (what must ALL be true)
1. **Door wired** (projection): card ask → /api/decision/explain. — built, HELD.
2. **Pointer present** (recollection+composition backfill, 8e3d1f1 + the explanation_source backfill): each decision carries `explanation_source`. — ~9/21 done; ~12 backfilling.
3. **Pointer has content** (upstream capture): the explanation_source resolves to REAL origin content (the gap/discussion), not a stub. — per-decision; absent ones must be captured first.
(+ the rerank tradeoff: fast path = pointer-only grounding by design.)

## CORROBORATION
This independent 3-agent trace CONFIRMS recollection's own diagnosis (8e3d1f1: genuine-provenance built, cards WITH explanation_source ground in real memory; ~12/21 lack the pointer → backfill is the coverage close) — reached from the code, not relayed (default-to-wrong satisfied). It ADDS: Part 1 (the trigger is totally unwired — the backfill alone won't close L1; the redirect must also flip) + the rerank fast-path tradeoff.

## OWNERSHIP
- Part 1 (trigger redirect): projection — built, held, one-clean-flip when Part 2 covers the 13.
- Part 2 (grounding mechanism + backfill): recollection (mechanism, 8e3d1f1) + composition (explanation_source backfill).
- Part 3 (provenance capture for the absent decisions): upstream — the origin must be written before it can be pointed at.
