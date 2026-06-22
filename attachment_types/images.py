"""images — images (image://<id>) attached to a channel: the hierarchical place to put images IN a channel."""
ATTACHMENT_TYPE = {
    "id": "images",
    "label": "Images",
    "target_kind": "address",       # target = image://<id> (opaque; resolve by stripping scheme → cc_images.get_image)
    "multi": True,
    "desc": "an image (image://<id>) bound to a channel — the channel's images. The manifest projects "
            "channel → [images], so a channel becomes the addressed/hierarchical home for its visual artifacts "
            "(store, generate-into, read, comment, cross-reference).",
}
