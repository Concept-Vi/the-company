# A lens that binds the radius to the DAY cycle by default (the cycle frame as a declared binding).
BINDING = {
    "id": "time-of-day",
    "label": "Day cycle (raw kinds)",
    "angle_from": "kind",
    "radius_from": "time",  # the FE cycle-frame switch overrides to day/week; this is the opening hint
    "order_by": "count",
}
