"""board_edges/pinned.py — SALIENCE edge (④ L6 BOARD): a board-VIEW pins an item.

The pin is a typed edge FROM a board_view record TO the item it pins (view -> board://<item>). Because the
edge originates on the VIEW record, pinning an item on one view does NOT pin it on another (C6.6) — salience
is a property of the view, never of the item. The inverse ('pinned_on') lets reverse_traverse find which
views have pinned a given item. Pins/salience/ordering are VIEW-records, exactly as the BOARD study designed
(A3's dead partial-index (project_id, pinned) finally lives as resolution, not a column)."""
RELATION_TYPE = {
    "id": "pinned",
    "directed": True,
    "label": "pinned",
    "inverse": "pinned_on",
    "desc": "the source board-view has pinned the target item (view -> board://<item>); salience belongs to "
            "the view, so a pin on one view is absent on another",
}
