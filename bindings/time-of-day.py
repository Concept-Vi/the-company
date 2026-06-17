# A lens that binds the radius to the DAY cycle by default (the cycle frame as a declared binding).
BINDING = {
    "id": "time-of-day",
    "label": "Day cycle — activity around the clock",
    # human meaning (registry-true, declared-first; TENTATIVE draft — Tim/DNA ratify; never machine names)
    "meta": {
        "name": "Day cycle",
        "is": "Everything that's happening, arranged around a day (or week) cycle.",
        "fills": "The same events, placed around a clock-like cycle so you can see the rhythm of the day or week.",
        "why": "To see when in the day or week things tend to happen.",
    },
    "angle_from": "kind",
    "radius_from": "time",  # the FE cycle-frame switch overrides to day/week; this is the opening hint
    "order_by": "count",
}
