"""docs — documentation files attached to a channel (the §3 manifest `docs` bucket)."""
ATTACHMENT_TYPE = {
    "id": "docs",
    "label": "Docs",
    "target_kind": "path",          # target = a filesystem path
    "multi": True,
    "desc": "a documentation file/path bound to a channel — loaded as context for members on join.",
}
