# decision_subtypes/ — the decision-subtype registry (the decision FORMED right for the operator)

The file-discovered vocabulary of decision KINDS. Each `<id>.py` declares a `DECISION_SUBTYPE` that maps a
decision to its **card_variant** (DNA renders — the elements/layout) + **explanation_policy** (fork's
generation_policies — the RHM's explain regime) + **required_elements** (the gate). One knob (decision.subtype)
→ both halves resolve, so each decision-kind is formed with the right card + the right explanation.

- **DERIVED, never invented** (Tim's law): the vocabulary clusters out of the real DECISION-GATHER. Seeded
  2026-06-21 from the first gather (16+ decisions): `authorize` (approve/hold, security) · `trade-off`
  (multi-option direction) · `theorem-fork` (a conceptual fork in Tim's math) · `cross-lane` (a fabric
  technical choice). REFINE as the set grows — a decision of a new shape (ranking · allocation · workflow ·
  single-confirm, DNA's unbuilt variant candidates) adds a ROW, never a code edit.
- **Mechanism:** `runtime/decision_subtypes.py` (mirrors axis_registry / stack_item_types — the one mechanism).
- **Row:** `id` (==filename) · `card_variant` (required — DNA's variant vocabulary: binary · n-panel · …) ·
  `explanation_policy` (required — a generation_policies id, fork) · `required_elements`? (the card must carry
  these — drives the decoration-ban) · `desc`?.
- **Resolves:** decision.subtype → this row → card_variant [DNA] · explanation_policy [fork run_role] ·
  required_elements [the gate]. card_variant + explanation_policy are meet-at-the-contract (DNA's render vocab,
  fork's policy ids). The floor: reading a subtype is a READ.
