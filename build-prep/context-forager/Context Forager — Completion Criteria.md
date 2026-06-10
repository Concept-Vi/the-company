# Context Forager — Completion Criteria

**Verification rules: every criterion is two-faced — FUNCTION verified by USE in the real browser
(:5173 → bridge :8831), FORM verified by the design rubric (corpus tokens + kit vocabulary, no
literals; no overlap with existing surfaces; navigable-by-sight; 390px state stated honestly).
Never green from code-reading; embedder-down and empty-result paths must be LOUD. The vision bar:
Tim sculpts a context set by recognition and hands it to the builder — his method at scale.**

## Group A · search → circles
- **A1 search lands on canvas** · FUNCTION: type a query (space picker: history/repo), hits render
  as circle nodes ('f-' ids, Circle2d) with score-tinted ring + a recognizable label; canvas pans to
  them ☐ / FORM: tokens only; circles read by shape at zoom (semantic zoom: label→detail) ☐
- **A2 coexistence** · FUNCTION: forager circles and graph NodeShapes coexist — graph loadGraph
  prune NEVER deletes 'f-' shapes; forager clear never touches 'n-' ☐ / FORM: visually distinct
  vocabularies (circle vs card) ☐
- **A3 honest empties** · FUNCTION: embedder down → a loud note on the surface (the backend's honest
  note rendered, not an empty silence); zero hits → "nothing returned" state ☐ / FORM: kit notice ☐

## Group B · sculpt
- **B1 whittle** · FUNCTION: delete/dismiss circles (selection delete); the set is the canvas ☐ /
  FORM: removal feels like sculpting (no confirm-dialog friction) ☐
- **B2 grow** · FUNCTION: successive searches ADD (dedupe by address — re-hit pulses, never dupes) ☐
- **B3 expand** · FUNCTION: click a circle → River detail in place (what it is: record kind, session,
  ts_source when present, content head); full-screen open for the whole record ☐ / FORM: altitude
  grammar (Pulse=circle, River=card, Nodes=full) ☐
- **B4 connections** · FUNCTION: edges between circles sharing session/source-prefix (lineage) ☐ /
  FORM: edge weight legible, never hairball (cap + fade) ☐

## Group C · facets
- **C1 chips v1** · FUNCTION: filter the visible set by space · kind · session · pattern-tag-cluster
  (chips derive from the REAL index fields — registry-is-truth, no hardcoded vocab) ☐
- **C2 time facet** · FUNCTION: the ts_source backfill flow runs (deterministic transcript re-walk →
  re-stamp; flows/ row, proposes_only) → a time-period chip works on backfilled data ☐
- **C3 growth path stated** · topics/principles chips appear ONLY when their capture runs populate
  the spaces (no fake chips; the empty state names the flow that would fill it) ☐

## Group D · the handoff (the point of it all)
- **D1 select-multiple → builder** · FUNCTION: tldraw multi-select circles → "give to builder" →
  the panel's NEXT turn carries the selection-set block (bounded: per-item head + total cap; replace
  semantics across turns); the builder demonstrably answers FROM the set ☐ / FORM: the set chip in
  the panel shows N selected (the .rhm-indicating vocabulary) ☐
- **D2 the demo scenario** · FUNCTION (the bar Tim set): search a thing he half-made → circles →
  whittle → select 3 → ask the builder to use them → it cites them back correctly ☐

## Product face (standing)
- **PF1** all surfaces on tokens/kit; no overlaps with chat/builder/cognition overlays ☐
- **PF2** mobile: stated honestly (hidden <699px v1 like its siblings, named as gap) ☐

Priority: A1→A2→D1 (the spine) → B1-B3 → C1 → A3/B4 → C2 → D2 → C3.
