"""axes/mode.py — the MODE axis (how it behaves)."""

AXIS = {
    "id": "mode",
    "namespace": "mode",
    "fields": {"current": "discrete"},   # pilot | inspect | dev | autopilot — a behaviour/render-family pick
    "value_source": "live",
    "desc": "How it behaves — pilot · inspect · dev · autopilot (the stability dial). The mode-selector + the "
            "mode→colour cascade resolve against it (drive a mode → re-resolve).",
}
