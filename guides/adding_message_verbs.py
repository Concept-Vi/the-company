"""guides/adding_message_verbs.py — how to add a typed-message VERB (Tim: 'guides on how to add new
verbs, in the channel system'). The guide IS a registry row — the knowledge lives in the fabric."""

GUIDE = {
    "id": "adding_message_verbs",
    "label": "Adding a message verb",
    "description": "How to add a new typed-message kind (a verb with an obligation) to the board's "
                   "message registry — a row-add, zero code.",
    "target": "file://runtime/message_types.py",
    "grounded_from": [
        "file://runtime/message_types.py",
        "file://message_types/review_request.py",   # the worked example (a verdict-obligation verb)
        "file://runtime/cc_board.py",
    ],
    "source_hash": "live",
    "content": """# Adding a message verb (a typed kind with an obligation)

A verb = message_types/<id>.py declaring MESSAGE_TYPE = {id, obligation, label, desc}.
- id MUST equal the filename. obligation ∈ reply | verdict | ack | none — what the addressed member
  owes, and what the nag hook holds them to until it lands on the board.
- Drop the file → the registry discovers it (no code change). Malformed rows FAIL LOUD at discovery.
- Use it: cc_board.comment(target, body, author, message_type='<id>') — @mentions in the body are
  routed with your kind; the obligation pends against each mentioned member until their reply.
- If the obligation semantics you need don't exist (beyond reply/verdict/ack/none), that's a
  runtime/message_types.py OBLIGATIONS extension + a matching close-condition in
  cc_board.pending_obligations — a small code change; flag it on the board first.

Worked example — message_types/review_request.py:
    MESSAGE_TYPE = {"id": "review_request", "obligation": "verdict",
                    "label": "Review request",
                    "desc": "Asks for a review; obligation: an explicit verdict + why."}
""",
}
