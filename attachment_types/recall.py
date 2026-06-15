"""recall — a recall scope bound to a channel (the §3 manifest `recall_scope`; the 5th-wire seam)."""
ATTACHMENT_TYPE = {
    "id": "recall",
    "label": "Recall scope",
    "target_kind": "scope",         # target = a recall-scope selector (project/session/segment), not an address
    "multi": False,
    "desc": "the channel-scoped recall selector — cc_channel op=recall runs over this scope (5th wire).",
}
