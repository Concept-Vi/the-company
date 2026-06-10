"""dials/stability.py — how much the surface may move on its own (Track-1 round 3)."""
DIAL = {
    "id": "stability",
    "label": "Stability (how much the surface rearranges itself)",
    "governs": ("the resolved interface's freedom to move things: the spatial frame is the UI's "
                "IDENTITY (places Tim knows stay put), content is its MEMORY (resolves with "
                "where/when/who) — this dial sets how far beyond content-resolution the composer "
                "may go. CONSUMERS (named honestly): the RHM surface-composer + the resolved-UI "
                "layer when built; nothing reads this yet — the dial is their configuration seam."),
    "positions": [
        {"name": "museum", "meaning": "nothing moves without Tim's hand — resolution changes emphasis only"},
        {"name": "workshop", "meaning": "places stay stable, contents flow with context — rearrangement is proposed, never silent"},
        {"name": "stage", "meaning": "the composer may re-set the scene per moment — the surface tells each moment's story"},
    ],
    "default": "workshop",
}
