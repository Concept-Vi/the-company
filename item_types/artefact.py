"""item_types/artefact.py — an ARTEFACT: a self-contained rich HTML page hosted in the surface.

Unlike a `document` (ordered markdown blocks), an artefact is a single self-contained HTML page (its own
styles/scripts inline) — a designed page, a visual map, a tool. The surface serves its body verbatim into a
sandboxed iframe and wraps it with the channel chrome + a comment rail + the chat, so it is commentable and
discussable like any board item. Lives in a channel like everything else; the upward-engine technical
reference is the first one. Body = the full HTML; `links` may carry attachments. Commentable at the
artefact level (and at free-typed quote granularity)."""
ITEM_TYPE = {
    "id": "artefact",
    "initial": "active",
    "states": ["draft", "active", "archived"],
    "transitions": {"draft": ["active", "archived"], "active": ["archived", "draft"], "archived": ["active"]},
    "label": "Artefact",
    "desc": "a self-contained rich HTML page hosted in the surface — commentable, discussable, per channel",
}
