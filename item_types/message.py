"""item_types/message.py — a MESSAGE: a chat message between the operator (Tim) and the fabric (the lead),
exchanged in a channel's chat view. Distinct from board comments (which anchor to content); a message is
direct conversation. `sent` -> `read`."""
ITEM_TYPE = {
    "id": "message",
    "initial": "sent",
    "states": ["sent", "read"],
    "transitions": {"sent": ["read"], "read": ["sent"]},
    "label": "Message",
    "desc": "a direct chat message between the operator and the fabric, in a channel",
}
