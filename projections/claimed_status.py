"""projections/claimed_status.py — the SEED `claimed_status` lens (Cognition Engine K1 · render-not-judge).

The clearest render-NOT-judge lens (K3): render the file's OWN CLAIMED state — what it SAYS it is
(decided/draft/aspirational/stub/unknown) — and do NOT judge whether the claim is true. Judgement of
truth is a LATER reduce pass; the capture lens is a describer. An `epistemic`-level enum; does not embed
(a categorical, not a space).

See runtime/projections.py + projections/AGENTS.md. Its `id` MUST equal the file stem (`claimed_status`).
"""

PROJECTION = {
    "id": "claimed_status",
    "level": "epistemic",
    "produced_by": "model",
    "embeds": False,
    "field": "enum",
    "enum": ["decided", "draft", "aspirational", "stub", "unknown"],
    "desc": "the file's OWN claimed state (render its claim; do NOT judge whether the claim is true — K3)",
    "stage": "legibility",
}
