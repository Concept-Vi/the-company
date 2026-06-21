"""axes/resolution.py — the RESOLUTION/detail axis (how close — the grain)."""

AXIS = {
    "id": "resolution",
    "namespace": "resolution",
    "fields": {"grain": "discrete"},   # coarse | medium | fine — the MRL grain / levels-of-detail
    "value_source": "live",
    "desc": "How close — coarse · medium · fine (the same thing zoomed; the MRL grain). ★ READ-SIDE: a "
            "subset projection of the stored superset (extract-once / determine-many — never re-extract); the "
            "dragnet grain axis (recollection's determine projects fields by this). Also the multi-scale embeddings.",
}
