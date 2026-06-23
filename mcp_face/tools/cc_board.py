"""mcp_face/tools/cc_board.py — the Company NOTICEBOARD / board, through the MCP (the agent-facing
surface over runtime/cc_board.py). File-drop tool (pkgutil auto-register).

The inward-facing half (Tim 2026-06-15): agents (and Tim) FILE typed items — request · issue · tip ·
guide · idea — about the Company / MCP / CLI / CI / app; a channel (the lead first, a routine later)
LISTS + picks them up and TRANSITIONS them along the item-type's declared lifecycle. The board rides
ON the channel system (an item lives in a channel, carries a thread) but its records are a DISTINCT
resource, so it is its OWN op-multiplexed tool — exactly as `cc_clone` sits beside `cc_channel`.

Every `type` / `source` / link `kind` / state transition is a REGISTRY REFERENCE, validated fail-loud
(item_types/ · source_types/ · board_edges/ — file-discovered, add-a-row-not-code). There is NO
hardcoded pickup/resolve op — `transition` moves along the registry-declared legal states.

## Ops
  op="file"       — file a typed item. Required: `type`, `title`, `author_session`. Optional: `body`,
                    `source` (default claude_code), `channel`, `thread`, `links` ([{kind,target}] typed
                    edges). Returns the new item (with its flat `board://<id>` address).
  op="list"       — list/pick-up read. Optional filters: `type`, `state`, `source`, `author_session`.
  op="get"        — read one item. Required: `item` (the id).
  op="transition" — move an item along its type's lifecycle. Required: `item`, `to_state`. Optional:
                    `by`, `note`. Fail-loud if the move is not a declared legal transition.
  op="types"      — the registries (valid item-types, source-types, edge-kinds) for filing.
  op="edit"       — edit an item IN PLACE (no-versioning). Required: `item`. Any of `title`, `body`,
                    `order` (a container's ordered child-address list), `add_links` ([{kind,target}]).
  op="comment"    — comment on ANY address. Required: `target` (the addr), `body`, `author_session`.
                    Files an addressed comment linked `commented_on` → target (itself replyable).
  op="reply"      — reply to a comment (threading). Required: `target` (the comment's board://), `body`,
                    `author_session`. Links `reply_to` → the comment.
  op="thread"     — the threaded annotation tree on an address. Required: `item` OR `target` (the addr).
  op="document"   — assemble a DOCUMENT for reading: ordered blocks + each block's comment thread.
                    Required: `item` (the document id).
"""
from __future__ import annotations

from typing import Literal

OPS = ("file", "list", "get", "transition", "types", "edit", "comment", "reply", "thread", "document")


def register(mcp, suite):
    @mcp.tool()
    def cc_board(op: Literal["file", "list", "get", "transition", "types",
                             "edit", "comment", "reply", "thread", "document"],
                 type: str = "", title: str = "", body: str = "", author_session: str = "",
                 source: str = "", channel: str = "", thread: str = "",
                 links: list | None = None, item: str = "", to_state: str = "",
                 by: str = "", note: str = "", state: str = "",
                 target: str = "", order: list | None = None, add_links: list | None = None) -> dict:
        """The Company NOTICEBOARD — file/list/get/transition typed items about the Company itself.
        type/source/edge-kind/state are REGISTRY REFERENCES (fail-loud). Pick `op`:

          op="file"       — file an item (`type`, `title`, `author_session` required; optional `body`,
                            `source`, `channel`, `thread`, `links`=[{kind,target}]). Returns board://<id>.
          op="list"       — pick-up read; filter by `type`/`state`/`source`/`author_session`.
          op="get"        — read one item (`item`=id).
          op="transition" — move along the lifecycle (`item`, `to_state`; optional `by`, `note`).
          op="types"      — list valid item-types / source-types / edge-kinds.
        """
        from runtime import cc_board as cb
        try:
            if op == "types":
                return {"op": "types", "item_types": cb.item_types(),
                        "source_types": cb.source_types(), "edge_kinds": cb.edge_kinds()}
            if op == "file":
                if not type or not title or not author_session:
                    raise ValueError("cc_board(op='file') needs `type`, `title`, and `author_session`.")
                rec = cb.file_item(type, title, body, author_session,
                                   source=source or "claude_code", channel=channel,
                                   thread=thread, links=links)
                return {"op": "file", "item": rec}
            if op == "list":
                rows = cb.list_items(type=type or None, state=state or None,
                                     source=source or None, author_session=author_session or None)
                return {"op": "list", "total": len(rows), "items": rows}
            if op == "get":
                if not item:
                    raise ValueError("cc_board(op='get') needs `item` (the item id).")
                return {"op": "get", "item": cb.get_item(item)}
            if op == "transition":
                if not item or not to_state:
                    raise ValueError("cc_board(op='transition') needs `item` and `to_state`.")
                return {"op": "transition", "item": cb.transition(item, to_state, by=by, note=note)}
            if op == "edit":
                if not item:
                    raise ValueError("cc_board(op='edit') needs `item` + at least one of title/body/order/add_links.")
                return {"op": "edit", "item": cb.edit_item(item, title=title or None, body=body or None,
                                                           order=order, add_links=add_links, by=by, note=note)}
            if op == "comment":
                if not target or not body or not author_session:
                    raise ValueError("cc_board(op='comment') needs `target` (the address), `body`, `author_session`.")
                return {"op": "comment", "item": cb.comment(target, body, author_session,
                                                            title=title or "Comment", channel=channel)}
            if op == "reply":
                if not target or not body or not author_session:
                    raise ValueError("cc_board(op='reply') needs `target` (the comment board://), `body`, `author_session`.")
                return {"op": "reply", "item": cb.reply(target, body, author_session,
                                                       title=title or "Reply", channel=channel)}
            if op == "thread":
                addr = target or (f"board://{item}" if item and not item.startswith("board://") else item)
                if not addr:
                    raise ValueError("cc_board(op='thread') needs `target` (or `item`) — the address to read the thread of.")
                return {"op": "thread", "on": addr, "thread": cb.thread(addr)}
            if op == "document":
                if not item:
                    raise ValueError("cc_board(op='document') needs `item` (the document id).")
                return {"op": "document", **cb.assemble_document(item)}
        except cb.BoardError as e:
            return {"op": op, "ok": False, "error": str(e)}
        raise ValueError(f"cc_board: unknown op {op!r} — one of {OPS}.")
