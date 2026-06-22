"""axes/resolution.py — the RESOLUTION/detail axis (how close — the grain)."""

AXIS = {
    "id": "resolution",
    "namespace": "resolution",
    "fields": {"grain": "discrete"},   # coarse | medium | fine — the MRL grain / levels-of-detail
    "value_source": "live",
    "desc": "How close — coarse · medium · fine (the same thing zoomed; the MRL grain). ★ ONE axis, BOTH facets "
            "(resolved 2026-06-22, Tim's STEPPED cascade): (a) EXTRACTION-TIME forward-stepping — coarse on all → "
            "step deeper IN-PASS per chunk by its OWN coarse output's kind (decision/spec/discussion→fine; "
            "log→stop), FORWARD-ONLY, never re-extract, no up-projection; (b) READ-TIME multi-scale ROLLUP — a "
            "subset projection of the stored superset (determine-many). The dragnet grain axis (recollection's "
            "4207e75) + the multi-scale embeddings = ONE axis, not two. never-re-extract holds throughout.",
}
