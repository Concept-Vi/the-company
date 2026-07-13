"""inbox_sources/obligations.py — Tim's PENDING TYPED MESSAGES (mentions he owes a reply/verdict/ack).

Rides `runtime.cc_board.pending_obligations("tim")` VERBATIM — the PULL half of the typed-message loop
(no parallel obligations read; see that function's own docstring for the fold: every comment addressed to
`tim` whose message-kind carries an unmet obligation, `_obligation` stamped on each returned row).

★ HONEST LIMITATION (documented, not hidden — the I1 spec's "honest split" law): the only WRITE door the
operator surface exposes onto a board item today is `/api/board/comment` (files a `commented_on` board
comment as `operator://tim`). Actually CLEARING an obligation requires a `reply_to`-edged reply
(`cc_board.reply_to_mention` / the MCP `reply` tool) — a mechanism the bridge does not expose to the
operator surface (agent/session-only). So this card's verb is honestly labelled **"Comment"**, not
"Resolve"/"Reply" — posting it puts Tim's words on the board (visible to every session reading the
thread) but does **not** clear `_obligation`; the item will keep surfacing here until a real `reply_to`
lands (by an agent, or by a future bridge door). Never overclaimed as resolution."""


def fetch() -> list:
    from runtime import cc_board

    out = []
    for it in cc_board.pending_obligations("tim"):
        obligation = it.get("_obligation") or "reply"
        by = it.get("author_session") or "someone"
        title = it.get("title") or it.get("id")
        why = f"{obligation} owed — from {by}"
        out.append({
            **it,
            "title": title,
            "why": why,
            "created": it.get("created") or "",
        })
    return out


INBOX_SOURCE = {
    "id": "obligations",
    "label": "Obligation",
    "fetch": "inbox_sources.obligations:fetch",
    "card_shape": {
        "id_field": "id", "address_field": "address", "title_field": "title",
        "why_field": "why", "created_field": "created",
    },
    "verbs": [
        {"id": "comment", "label": "Comment", "door": "/api/board/comment"},
    ],
}
