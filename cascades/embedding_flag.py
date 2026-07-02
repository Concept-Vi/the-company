"""cascades/embedding_flag.py — A's embedding_flag cascade (priority 70), target=notice_board_items.

CLOUD-ONLY: the target system (notice_board_items) lives on the cloud/read side, NOT in ④'s scope. Declared here so the
fan-out is HONEST about the hole (generate_all returns skipped:reason) rather than silently omitting it —
the run-all-report-holes loop A never had. Regenerated on the cloud side; ④ derives only the in-scope faces.
No live handler (never invoked — generate_all short-circuits on cloud_only)."""

CASCADE = {
    "id": "embedding_flag",
    "target": "notice_board_items",
    "priority": 70,
    "cloud_only": True,
    "desc": "per-type embedding policy flag (cloud embedding pipeline)",
}


def handle(type_row: dict, ctx: dict) -> dict:  # never called (cloud_only short-circuits) — fail loud if it is
    raise NotImplementedError("embedding_flag is cloud_only — its target notice_board_items is not present in ④; nothing to derive here.")
