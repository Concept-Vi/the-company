"""mcp_face/tools/cc_images.py — IMAGES through the MCP (agent surface over runtime/cc_images.py + the
board/attachment machinery). File-drop tool (auto-registers on the next MCP server start).

The hierarchical/addressed home for images in the fabric: STORE/generate-into, READ, COMMENT, LINK/reference
— all reusing existing seams (the blob store, image:// records, cc_attachments for channel binding, cc_board
typed edges for comments + cross-references). Lets an external reviewer (e.g. ChatGPT comparing generated
outputs against source material) add images, attach them to a channel, comment on them, and link each
output to its source.

## Ops
  op="add"      — STORE an image (or a GENERATED one). `data_b64` (base64 bytes) OR `path` (read a file) +
                  `mime` (optional, sniffed/verified) + `name`/`alt`/`w`/`h`. Optional `channel` →
                  also attaches it (channel → [images]). `author_session` REQUIRED (provenance). Returns the
                  image record (address image://<id>) + a `serve_url`.
  op="get"      — read one image record (`image`=image://<id> or the bare id) + its serve_url + its comments.
  op="list"     — image records, newest-first; optional `channel` filter.
  op="comment"  — add a comment/feedback to an image (or any address). Required: `image` (target), `body`,
                  `author_session`. Files a board item linked `commented_on` → the target.
  op="link"     — cross-reference two artifacts (e.g. a generated output ↔ its source). Required: `image`
                  (from), `target` (to). Files/uses a `references` edge between them.
  op="comments" — gather every comment ON an image (the review read): reverse `commented_on` edge.
"""
from __future__ import annotations

import base64
from typing import Literal

OPS = ("add", "get", "list", "comment", "link", "comments")


def register(mcp, suite):
    @mcp.tool()
    def cc_images(op: Literal["add", "get", "list", "comment", "link", "comments"],
                  image: str = "", target: str = "", channel: str = "", data_b64: str = "",
                  path: str = "", mime: str = "", name: str = "", alt: str = "", body: str = "",
                  author_session: str = "", w: int = 0, h: int = 0) -> dict:
        """Images as first-class addressed fabric artifacts — store/generate-into, read, comment, cross-reference.
        See the module docstring for ops. Reuses the blob store + image:// records + cc_board edges +
        cc_attachments (no parallel machinery). image:// resolves through the ONE resolve_address seam."""
        from runtime import cc_images as ci
        from runtime import cc_board as cb
        from runtime import cc_attachments as ca
        store = suite.store

        def _serve(addr_or_id: str) -> str:
            iid = addr_or_id.split("://")[-1]
            return f"/api/image/{iid}"

        if op == "add":
            if not author_session:
                raise ValueError("cc_images(op='add') needs `author_session` (provenance).")
            if data_b64:
                data = base64.b64decode(data_b64)
            elif path:
                with open(path, "rb") as f:
                    data = f.read()
            else:
                raise ValueError("cc_images(op='add') needs `data_b64` (base64 bytes) or `path` (a file to read).")
            rec = ci.save_image(store, data, mime=mime, name=name, channel=channel,
                                author_session=author_session, alt=alt, w=w, h=h)
            attached = False
            if channel:
                ca.attach(channel, "images", rec["address"])     # the hierarchical channel→[images] bind
                attached = True
            return {"op": "add", "image": rec, "serve_url": _serve(rec["address"]),
                    "attached_to_channel": channel if attached else ""}

        if op == "get":
            if not image:
                raise ValueError("cc_images(op='get') needs `image` (image://<id> or the id).")
            rec = ci.get_image(image)
            comments = [e["item"] for e in cb.reverse_traverse(rec["address"], "commented_on")]
            return {"op": "get", "image": rec, "serve_url": _serve(rec["address"]), "comments": comments}

        if op == "list":
            return {"op": "list", "images": ci.list_images(channel=channel or None)}

        if op == "comment":
            if not image or not body or not author_session:
                raise ValueError("cc_images(op='comment') needs `image` (target), `body`, `author_session`.")
            item = cb.file_item("tip", (name or "Comment"), body, author_session,
                                channel=channel, links=[{"kind": "commented_on", "target": image}])
            return {"op": "comment", "comment": item, "on": image}

        if op == "link":
            if not image or not target:
                raise ValueError("cc_images(op='link') needs `image` (from) and `target` (to).")
            item = cb.file_item("tip", (name or "Reference"), (body or f"{image} ⟷ {target}"),
                                author_session or "ch-3mpkjg3r", channel=channel,
                                links=[{"kind": "references", "target": image},
                                       {"kind": "references", "target": target}])
            return {"op": "link", "link": item, "from": image, "to": target}

        if op == "comments":
            if not image:
                raise ValueError("cc_images(op='comments') needs `image` (the target address/id).")
            iid = image if image.startswith("image://") else f"image://{image.split('://')[-1]}"
            return {"op": "comments", "on": iid,
                    "comments": [e["item"] for e in cb.reverse_traverse(iid, "commented_on")]}

        raise ValueError(f"cc_images: unknown op {op!r} — one of {OPS}.")
