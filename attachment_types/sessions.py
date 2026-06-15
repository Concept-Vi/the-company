"""sessions — sessions attached to a channel for context (the §3 manifest `sessions` bucket)."""
ATTACHMENT_TYPE = {
    "id": "sessions",
    "label": "Sessions",
    "target_kind": "address",       # target = session://<id>
    "multi": True,
    "desc": "a session (session://<id>) attached to a channel as context / a recall source.",
}
