"""mark_types/strain.py — SEED mark-type: strain (the structure↔meaning DIVERGENCE; SEED §111).

The disposition a strain pass writes when a unit's SQUARE position (where it's filed — repo-tree
distance from the centre) and its CIRCLE position (where it MEANS to be — semantic distance) DISAGREE.
0 = coincident = coherent (filed where it means, one read); high = strain = resistance. A `score`-shaped
value (the 0..1 magnitude |r_struct - r_semantic|). Direction `surface` — strain SURFACES a divergence to
attend to (render, NEVER auto-correct; operator-overridable, the gate-inbox / drift signal — Group 7).
The instrument computes it live per-point in semantic mode; this row lets it be MARKED + surfaced as a
finding. See runtime/mark_types.py + mark_types/AGENTS.md. Its `id` MUST equal the file stem (`strain`).
"""

MARK_TYPE = {
    "id": "strain",
    "value_shape": "score",
    "direction": "surface",
    "desc": "structure↔meaning divergence: |where it's FILED - where it MEANS to be| (SEED §111). 0 = "
            "coherent; high = strain — surface it, never auto-correct (operator-overridable).",
}
