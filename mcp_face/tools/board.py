"""mcp_face/tools/board.py — the NOTICEBOARD, CQRS-split (design v2 door: BOARD).

The board was the one door violating the repo's own read/write tool convention (sessions/session_post,
channels/channel_act — but cc_board mixed 13 read+write ops on one tool). This splits it: `board`
(pure read, + the `since` cursor the board never had — it is what agents are WOKEN BY, yet had no
"what's new since I looked") and `board_act` (the writes). Both are THIN doors over the UNCHANGED
runtime/cc_board.py; the original `cc_board` tool keeps working verbatim (adapters, no flag-day).

EXPOSURE preserved deliberately: cc_board is operator-tier today (untagged), so BOTH new doors stay
untagged — splitting must never silently widen the public remote boundary (the completeness review's
posture rule). Annotations now tell the truth per door (read: readOnly; write: not).

Comments/replies/threads here annotate ANY address (board:// · image:// · code:// · decision:// …) —
this IS the one annotation system (cc_images' comment/reply/thread already delegate to it at runtime;
the image RECORD layer — blobs/versions/image:// — rightly stays its own).
"""
from __future__ import annotations

from typing import Literal

from contracts.tools import ToolAnnotations as CompanyToolAnnotations
from mcp.types import ToolAnnotations as SDKToolAnnotations

READ_OPS = ("list", "get", "types", "thread", "document", "authored", "pins")
WRITE_OPS = ("file", "transition", "edit", "comment", "reply", "pin")


def _to_sdk_annotations(ann: CompanyToolAnnotations, title: str,
                        posture: str = "") -> SDKToolAnnotations:
    extra = {"posture": posture} if posture else {}
    return SDKToolAnnotations(
        title=title, readOnlyHint=ann.readonly, destructiveHint=ann.destructive,
        idempotentHint=ann.idempotent, openWorldHint=False, **extra)


def register(mcp, suite):
    from runtime import cc_board as _cb
    _cb.set_board_emitter(lambda ev, fields: suite.emit_run_record(ev, 0, **fields))

    @mcp.tool(annotations=_to_sdk_annotations(
        CompanyToolAnnotations(readonly=True, destructive=False, idempotent=True),
        "Noticeboard — read (list/get/thread/document + since-cursor)"))
    def board(op: Literal["list", "get", "types", "thread", "document", "authored", "pins"],
              type: str = "", state: str = "", source: str = "", author_session: str = "",
              scope: str = "", author: str = "", item: str = "", target: str = "",
              view: str = "", since: str = "", limit: int = 100) -> dict:
        """READ the noticeboard (CQRS: writes are `board_act`). Ops mirror cc_board's reads, plus:

          op="list" gains `since` (an ISO timestamp cursor): only items UPDATED after it, oldest-first,
          with `next_since` = the last returned item's updated stamp — so "what's new since I looked"
          is one cheap call (the board is what agents are woken by; it never had a cursor). No `since`
          → the full filtered list (unchanged semantics). `limit` caps either mode."""
        from runtime import cc_board as cb
        try:
            if op == "types":
                return {"op": op, "item_types": cb.item_types(),
                        "source_types": cb.source_types(), "edge_kinds": cb.edge_kinds()}
            if op == "list":
                rows = cb.list_items(type=type or None, state=state or None,
                                     source=source or None, author_session=author_session or None,
                                     scope=scope or None, author=author or None)
                if since:
                    rows = sorted((r for r in rows if (r.get("updated") or r.get("created") or "") > since),
                                  key=lambda r: r.get("updated") or r.get("created") or "")
                    rows = rows[:limit]
                    nxt = (rows[-1].get("updated") or rows[-1].get("created")) if rows else since
                    return {"op": op, "total": len(rows), "since": since, "next_since": nxt,
                            "items": rows}
                return {"op": op, "total": len(rows), "items": rows[:limit]}
            if op == "get":
                if not item:
                    raise ValueError("board(op='get') needs `item`.")
                return {"op": op, "item": cb.get_item(item)}
            if op == "authored":
                if not author:
                    raise ValueError("board(op='authored') needs `author` (an address or legacy handle).")
                ids = cb.items_by_author(author)
                return {"op": op, "author": author, "total": len(ids), "items": ids}
            if op == "pins":
                if not view:
                    raise ValueError("board(op='pins') needs `view` (the board_view item id).")
                pinned = cb.pinned_on_view(view)
                return {"op": op, "view": view, "total": len(pinned), "pinned": pinned}
            if op == "thread":
                addr = target or (f"board://{item}" if item and not item.startswith("board://") else item)
                if not addr:
                    raise ValueError("board(op='thread') needs `target` (or `item`).")
                return {"op": op, "on": addr, "thread": cb.thread(addr)}
            if op == "document":
                if not item:
                    raise ValueError("board(op='document') needs `item` (the document id).")
                return {"op": op, **cb.assemble_document(item)}
        except cb.BoardError as e:
            return {"op": op, "ok": False, "error": str(e)}
        raise ValueError(f"board: unknown op {op!r} — one of {READ_OPS}. Writes live on board_act.")

    @mcp.tool(annotations=_to_sdk_annotations(
        CompanyToolAnnotations(readonly=False, destructive=False, idempotent=False),
        "Noticeboard — act (file/transition/edit/comment/reply/pin)"))
    def board_act(op: Literal["file", "transition", "edit", "comment", "reply", "pin"],
                  type: str = "", title: str = "", body: str = "", author_session: str = "",
                  source: str = "", channel: str = "", thread: str = "",
                  scope: str = "", author: str = "", links: list | None = None,
                  item: str = "", to_state: str = "", by: str = "", note: str = "",
                  target: str = "", order: list | None = None, add_links: list | None = None,
                  view: str = "") -> dict:
        """WRITE the noticeboard (CQRS: reads are `board`). file/transition/edit/comment/reply/pin —
        identical semantics to cc_board's writes (thin door, same runtime; cc_board keeps working).
        `comment`/`reply` annotate ANY address (board:// image:// code:// decision:// …) — the ONE
        annotation system, and a comment's @mentions still live-route to the named members."""
        from runtime import cc_board as cb
        try:
            if op == "file":
                if not type or not title or not author_session:
                    raise ValueError("board_act(op='file') needs `type`, `title`, and `author_session`.")
                rec = cb.file_item(type, title, body, author_session,
                                   source=source or "claude_code", channel=channel,
                                   thread=thread, scope=scope or None, author=author or None,
                                   links=links)
                return {"op": op, "item": rec}
            if op == "transition":
                if not item or not to_state:
                    raise ValueError("board_act(op='transition') needs `item` and `to_state`.")
                return {"op": op, "item": cb.transition(item, to_state, by=by, note=note)}
            if op == "edit":
                if not item:
                    raise ValueError("board_act(op='edit') needs `item` + at least one of "
                                     "title/body/order/add_links.")
                return {"op": op, "item": cb.edit_item(item, title=title or None, body=body or None,
                                                       order=order, add_links=add_links, by=by,
                                                       note=note)}
            if op == "comment":
                if not target or not body or not author_session:
                    raise ValueError("board_act(op='comment') needs `target` (the address), `body`, "
                                     "`author_session`.")
                return {"op": op, "item": cb.comment(target, body, author_session,
                                                     title=title or "Comment", channel=channel)}
            if op == "reply":
                if not target or not body or not author_session:
                    raise ValueError("board_act(op='reply') needs `target` (the comment board://), "
                                     "`body`, `author_session`.")
                return {"op": op, "item": cb.reply(target, body, author_session,
                                                   title=title or "Reply", channel=channel)}
            if op == "pin":
                if not view or not item:
                    raise ValueError("board_act(op='pin') needs `view` (the board_view item id) and `item`.")
                return {"op": op, "view": cb.pin(view, item, by=by or author_session)}
        except cb.BoardError as e:
            return {"op": op, "ok": False, "error": str(e)}
        raise ValueError(f"board_act: unknown op {op!r} — one of {WRITE_OPS}. Reads live on board.")
