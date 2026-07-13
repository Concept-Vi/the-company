"""inbox_sources/board_requests.py — open REQUEST-type board items (an ask still awaiting pick-up).

Rides `runtime.cc_board.list_items(type="request", state="open")` — the SAME noticeboard read `/api/board`
projects (no parallel board read). `why` is the request's own body head (the ask, in its own words) so
the card never invents a summary the item didn't state.

Same honest-limitation note as `obligations`: the only WRITE door here is `/api/board/comment` (a real,
visible comment as `operator://tim`) — it does not transition the item's state (open → picked-up/…), which
is a lane's job, not a card-button's. Labelled "Comment", not "Pick up" / "Close"."""


def fetch() -> list:
    from runtime import cc_board

    out = []
    for it in cc_board.list_items(type="request", state="open"):
        body = (it.get("body") or "").strip()
        why = body[:200] if body else "an open request awaiting pick-up"
        out.append({
            **it,
            "title": it.get("title") or it.get("id"),
            "why": why,
            "created": it.get("created") or "",
        })
    return out


INBOX_SOURCE = {
    "id": "board_requests",
    "label": "Request",
    "fetch": "inbox_sources.board_requests:fetch",
    "card_shape": {
        "id_field": "id", "address_field": "address", "title_field": "title",
        "why_field": "why", "created_field": "created",
    },
    "verbs": [
        {"id": "comment", "label": "Comment", "door": "/api/board/comment"},
    ],
}
