"""guides/the_door.py — the door's own guide (the self-reference Tim checked for: the card must teach
that the card is extensible — otherwise the mechanism itself is knowledge that 'doesn't exist')."""

GUIDE = {
    "id": "the_door",
    "label": "The door — cards at mechanical moments",
    "description": "How the join/create cards work and how to put your capability on them: door/<id>.py "
                   "rows with moment, scope (per-channel/per-project), audience, and until (temporal).",
    "target": "file://runtime/door.py",
    "grounded_from": [
        "file://runtime/door.py",
        "file://door/the_door.py",          # this very row — the worked self-example
        "file://ops/hooks/auto_register.py",
    ],
    "source_hash": "live",
    "content": """# The door — resolved cards at mechanical moments

THE LAW (Tim): anything not structurally delivered at a mechanical moment effectively DOES NOT EXIST.
The moments: register (SessionStart, automatic) · channel-join · channel-create · project-join/create.
At each moment the member receives a CARD — composed LIVE from the registries, never baked, so a card
can only ever show the CURRENT set (a registry edit IS a card edit; this is the anti-drift property).

PUT YOUR CAPABILITY ON THE CARD — drop door/<id>.py:
    DOOR = {"id": "<id>",                      # == filename
            "line": "one line at Tim's altitude",
            "depth": "guide://... | board://... | file://...",   # ONE level deeper
            "order": 50,                       # low sorts first
            "moment": "register|channel-join|channel-create|project-join|project-create|all",
            "scope": "global | channel:<name> | project:<id>",   # a channel card = global + its rows
            "audience": "lead,reviewer",       # optional — role/name-dependent lines
            "until": "2026-07-15"}             # optional — temporal/open items expire OUT live
Standing rows omit `until`. Conditional = scope+audience+until, resolved at compose time.

CHANNEL STEWARDS: on channel-create your card tells you to seed the channel's own rows
(scope 'channel:<name>') — joiners then get the default card PLUS your channel's modifications.
Write the guide the depth points to (guides/<id>.py) if it doesn't exist — knowledge lives in the
fabric, not in your session.
""",
}
