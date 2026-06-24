"""board_edges/attachment.py — an ATTACHMENT edge: this item carries an attached artifact (an image/file).

A comment links `attachment` → image://<channel>/<path> (the stored image/file). Lets a comment carry images
the operator attached on the phone; the review surface renders them inline under the comment, and an agent
receiving the comment gets the attachment address in the envelope."""
RELATION_TYPE = {
    "id": "attachment",
    "directed": True,
    "label": "attachment",
    "inverse": "attached_to",
    "desc": "the source item (e.g. a comment) has an attached artifact at the target address (image://, blob://)",
}
