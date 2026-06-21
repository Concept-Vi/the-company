"""axes/state.py — the STATE/time axis (when)."""

AXIS = {
    "id": "state",
    "namespace": "state",
    "fields": {"phase": "discrete", "frozen": "discrete"},   # pending|decided (mark-composed) · live|frozen (scrubber)
    "value_source": "live",
    "desc": "When — pending vs decided (composed from the decision_take mark, registry-is-truth) · live vs "
            "frozen (the scrubber / point-in-time). A surface resolves its treatment against where it is in time.",
}
