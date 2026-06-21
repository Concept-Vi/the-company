# schemas/vi-vision/v1/ — the company's CANONICAL decision-surface + render-type contracts

The in-tree canonical home for the FACE-2 / decision-surface + archetype contracts (islands-join:
migrated from the vi-visual-dev factory island where they were authored → the company centre, the
canonical source of truth; fork's `runtime/decision_registry.py` references these as its "in-tree mirror").

**The contracts here:**
- `decision.schema.json` — a DECISION (id, address, meaning, options[], explanation_source, scope, channel,
  legibility, dimensions/device [data-bound device], steps/flow keys, card_kinds via the archetype). state is
  NOT authored — composed from a `decision_take` mark (registry-is-truth). Addressed `decision://<frame>/<id>`.
- `option.schema.json` — a decision's choice (label, description→prose, implication→chip, recommended, dimensions).
- `decision-card.schema.json` — the FIRST archetype instance (render_kind, slot_map, card_kinds present/explain/
  choose, take, the data-bound device + decoration-ban, the composed co-visible view + 390 gate).
- `legibility.schema.json` — the meaning-fields {name, is, fills?, why?} (the operator-legibility law; name+is required).
- `archetype.schema.json` — the general RENDER-TYPE (archetype_of, render_kind, slot_map, take, language) — the
  layer the decision-card (+ future tool-card/graph/selector) resolve through.

**Consumption (registry-is-truth):** fork's decision_registry validates/references decision+option+legibility
here; DNA's renderer reads the archetype/card_kinds; the resolver-contract (build-prep/the-one-application/
RESOLVER-CONTRACT.md) composes them. recommended_label is a DERIVED field on the resolved record (fork 0273792),
not authored here.

**Migration note (islands-join, in progress):** these are now CANONICAL in the company. The vi-visual-dev copies
(schemas/vi-vision/v1/) are the deprecated ISLAND mirror — to be removed/pointed once fork's decision_registry is
wired to THIS in-company copy (so there's never a zero-source moment). The FACTORY-composition schemas
(atom/molecule/organism/template/pack/mode/variant/slot/tokens/animation/icon/layout/behavior) stay in
vi-visual-dev — they are the factory's own, not company-face contracts.
