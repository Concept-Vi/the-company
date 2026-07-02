"""cascades/board.py — derive the BOARD face (A's notice_board_sync cascade, priority 20).

The one place A's hollow rows carried REAL intention was the notice_board_types status_values. From
faces.board (status_values / renderer / icon / color) derive the board-type projection. NOT written into the
engine's item_types/ (that is L6-BOARD's territory — file-disjoint); recorded as a derived projection row.
The type's declared `states` (law 11) are the authoritative lifecycle; faces.board.status_values mirror them
for the board renderer."""

CASCADE = {
    "id": "board",
    "target": "notice_board_types",
    "priority": 20,
    "requires": ["board"],
    "desc": "the board-type face (status_values/renderer/icon/color) derived from faces.board",
}


def handle(type_row: dict, ctx: dict) -> dict:
    face = (type_row.get("faces") or {}).get("board") or {}
    # status_values default to the type's declared law-11 states (single source), else the face's own
    states = list(type_row.get("states") or [])
    status_values = list(face.get("status_values") or states)
    return {
        "type": type_row["id"],
        "label": type_row.get("label"),
        "status_values": status_values,
        "renderer": face.get("renderer"),
        "icon": face.get("icon"),
        "color": face.get("color"),
        "initial": type_row.get("initial"),
    }
