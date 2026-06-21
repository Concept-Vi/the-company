"""axes/viewer.py — the VIEWER/principal axis (who). The control-density / expertise seam — knobs resolve
against it (novice→plain, pilot→full knob-row), NOT a hardcoded advanced panel."""

AXIS = {
    "id": "viewer",
    "namespace": "viewer",
    "fields": {"expertise": "discrete"},   # novice | pilot — a render-family/density pick
    "value_source": "pending",             # no operator-mode/settings state exists yet — slot wired, value pending
    "desc": "Who's viewing — Tim · the RHM · a client (each translated-for). The control-density axis: expert "
            "knobs resolve against expertise (novice→plain · pilot→full), not a hardcoded panel. Value-source "
            "PENDING (no operator-mode state built); the axis is wired so it resolves the moment a source exists.",
}
