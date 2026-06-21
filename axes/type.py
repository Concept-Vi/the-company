"""axes/type.py — the TYPE axis (what it IS — the archetype)."""

AXIS = {
    "id": "type",
    "namespace": "type",
    "fields": {"kind": "discrete"},   # decision-card | graph | selector | instrument | diagram | spatial-material
    "value_source": "live",
    "desc": "What it IS — the archetype/render_kind (the CATALOG: decision-card·graph·selector·instrument·"
            "diagram·spatial-material). The 'content compositionality' axis; render_kind selects the renderer. "
            "(Per Tim's law type is 'n' not a ranked axis — the kind the surface resolves its archetype from.)",
}
