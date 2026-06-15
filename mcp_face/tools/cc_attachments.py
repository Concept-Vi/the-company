"""mcp_face/tools/cc_attachments.py — CHANNEL-ATTACHMENT bindings through the MCP (agent surface over
runtime/cc_attachments.py). File-drop tool (pkgutil auto-register on the next MCP server start).

Bind a target (a board item board://<id>, a session session://<id>, a doc path, a recall scope, the
cloning capability) to a channel. The set of attachment KINDS is a registry (attachment_types/); the
BINDINGS are file-discovered rows; the §3 manifest is a PROJECTION of the rows. (board://item-e523b30d.)

## Ops
  op="attach"   — bind a target to a channel. Required: `channel`, `attachment_type` (registry ref),
                  `target` (opaque ref). Optional `require_channel` (default true). Returns the binding.
  op="detach"   — remove a binding. Required: `attachment` (binding id).
  op="list"     — binding rows; optional `channel` / `attachment_type` filter.
  op="manifest" — a channel's attachments manifest (projection of rows grouped by type). Req: `channel`.
  op="types"    — the registered attachment kinds.
"""
from __future__ import annotations

from typing import Literal

OPS = ("attach", "detach", "list", "manifest", "types")


def register(mcp, suite):
    @mcp.tool()
    def cc_attachments(op: Literal["attach", "detach", "list", "manifest", "types"],
                       channel: str = "", attachment_type: str = "", target: str = "",
                       attachment: str = "", require_channel: bool = True) -> dict:
        """Bind things to a channel (sessions/docs/recall/cloning/board-items) as a registry of bindings;
        the manifest is a projection of the rows. Pick `op`:

          op="attach"   — `channel` + `attachment_type` + `target` -> a binding row (target stored opaque).
          op="detach"   — `attachment` (binding id) -> removed (presence=truth).
          op="list"     — binding rows; optional `channel` / `attachment_type`.
          op="manifest" — `channel` -> {attachments: {<type>: [target,…]}, count} (projection of rows).
          op="types"    — the registered attachment kinds (add an attachment_types/<id>.py to extend).
        """
        from runtime import cc_attachments as ca
        try:
            if op == "attach":
                if not channel or not attachment_type or not target:
                    raise ValueError("cc_attachments(op='attach') needs `channel`, `attachment_type`, `target`.")
                return {"op": "attach", **ca.attach(channel, attachment_type, target,
                                                    require_channel=require_channel)}
            if op == "detach":
                if not attachment:
                    raise ValueError("cc_attachments(op='detach') needs `attachment` (binding id).")
                return {"op": "detach", **ca.detach(attachment)}
            if op == "list":
                return {"op": "list", "attachments": ca.list_attachments(
                    channel=channel or None, attachment_type=attachment_type or None)}
            if op == "manifest":
                if not channel:
                    raise ValueError("cc_attachments(op='manifest') needs `channel`.")
                return {"op": "manifest", **ca.manifest(channel)}
            if op == "types":
                return {"op": "types", "attachment_types": ca.attachment_types()}
        except ca.AttachmentError as e:
            return {"op": op, "ok": False, "error": str(e)}
        raise ValueError(f"cc_attachments: unknown op {op!r} — one of {OPS}.")
