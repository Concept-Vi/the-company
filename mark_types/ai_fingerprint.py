"""mark_types/ai_fingerprint.py — SEED mark-type: ai-fingerprint (the SUBTRACT/inversion direction).

The disposition a fingerprint-pass writes when a unit matches the coined-vocab projection against the
AI-tics registry: generic+recurring = a tic to SUBTRACT (denoising = surfacing, OPPOSITE direction).
Direction `subtract` (the inversion) — this is the seed that EXERCISES the surface-vs-subtract split.
A `label`-shaped value (which tic matched). See runtime/mark_types.py + mark_types/AGENTS.md. Its `id`
MUST equal the file stem (`ai_fingerprint`).
"""

MARK_TYPE = {
    "id": "ai_fingerprint",
    "value_shape": "label",
    "direction": "subtract",
    "desc": "a matched AI-tic (generic+recurring) to subtract — denoising is surfacing, opposite direction",
}
