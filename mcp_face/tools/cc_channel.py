"""mcp_face/tools/cc_channel.py — cross-session messaging into LIVE Claude Code sessions, through the
MCP (the agent-facing surface over runtime/cc_channels.py). File-drop tool (pkgutil auto-register).

This is the Claude Code CHANNEL transport (live injection into hand-launched sessions) — distinct
from the fabric's own `channels`/gatherings (group membership). Design (Tim 2026-06-14): discover
live sessions; 1:1 send+receive (reply pushed back, no polling); group = broadcast over members.

## Ops
  op="list"      — every LIVE channel-session: handle, cwd, description, started (discovery).
  op="send"      — push a message INTO a live session's conversation. Required: `to` (handle/cwd),
                   `message`. Optional: `thread` (continue one), `topic`. Opens a thread so the
                   reply is pushed back to you. Returns the thread id.
  op="broadcast" — group chat: send to MANY live sessions at once under ONE shared thread.
                   Required: `to` (comma-separated handles/cwds) + `message`. Optional `topic`.
  op="mail"      — read the channel mail log (messages + replies), optionally one `thread`.

The CHANNEL REGISTRY (named managed groups — create/manage members; a member may be in several
channels at once; a member is reached by its transport at push time, NOT here):
  op="create_channel" — create a named channel. Required: `name`. Optional: `purpose`, `coordinator`.
  op="list_channels"  — list named channels (archived excluded unless `include_archived`).
  op="add_member"     — add a member `handle` to a `channel`.
  op="remove_member"  — remove a member `handle` from a `channel`.
  op="archive_channel"— archive a `channel` (status flip, not a delete; roster survives).
"""
from __future__ import annotations

from typing import Literal

OPS = ("list", "send", "broadcast", "mail",
       "create_channel", "list_channels", "add_member", "remove_member", "archive_channel")


def register(mcp, suite):
    @mcp.tool()
    def cc_channel(op: Literal["list", "send", "broadcast", "mail",
                               "create_channel", "list_channels", "add_member", "remove_member",
                               "archive_channel"],
                   to: str = "", message: str = "", thread: str = "", topic: str = "",
                   frm: str = "fabric", limit: int = 50,
                   channel: str = "", name: str = "", handle: str = "",
                   purpose: str = "", coordinator: str = "",
                   include_archived: bool = False) -> dict:
        """Message LIVE Claude Code sessions across the fabric (inject into their running
        conversation; replies push back to you — no polling) AND manage named channels. Pick `op`:

          op="list"      — discover live channel-sessions (handle · cwd · description).
          op="send"      — push `message` into the session `to` (handle/cwd); returns the thread.
          op="broadcast" — send `message` to many sessions (`to` = comma-separated) under one thread.
          op="mail"      — read the message/reply log (optionally one `thread`).

          op="create_channel"  — create a named channel (`name`; optional `purpose`, `coordinator`).
          op="list_channels"   — list named channels (`include_archived` to include archived).
          op="add_member"      — add member `handle` to `channel`.
          op="remove_member"   — remove member `handle` from `channel`.
          op="archive_channel" — archive `channel` (status flip, not a delete).

        A session becomes reachable by launching it with the channel
        (--mcp-config .../channels/channel.mcp.json --dangerously-load-development-channels
        server:company-channel). Live-only: a closed session is reached via session_post wake/consult.
        """
        from runtime import cc_channels as cc
        try:
            if op == "create_channel":
                if not name:
                    raise ValueError("cc_channel(op='create_channel') needs `name`.")
                return {"op": "create_channel", "channel": cc.create_channel(name, purpose, coordinator)}
            if op == "list_channels":
                chans = cc.list_channels(include_archived=include_archived)
                return {"op": "list_channels", "total": len(chans), "channels": chans}
            if op == "add_member":
                if not channel or not handle:
                    raise ValueError("cc_channel(op='add_member') needs `channel` and `handle`.")
                return {"op": "add_member", "channel": cc.add_member(channel, handle)}
            if op == "remove_member":
                if not channel or not handle:
                    raise ValueError("cc_channel(op='remove_member') needs `channel` and `handle`.")
                return {"op": "remove_member", "channel": cc.remove_member(channel, handle)}
            if op == "archive_channel":
                if not channel:
                    raise ValueError("cc_channel(op='archive_channel') needs `channel`.")
                return {"op": "archive_channel", "channel": cc.archive_channel(channel)}
            if op == "list":
                live = cc.live_sessions()
                return {"op": "list", "total": len(live),
                        "sessions": [{"handle": r["handle"], "cwd": r.get("cwd"),
                                      "description": r.get("description") or "(no description yet)",
                                      "session_id": r.get("session_id") or "", "started": r.get("started")}
                                     for r in live]}
            if op == "send":
                if not to or not message:
                    raise ValueError("cc_channel(op='send') needs `to` (handle/cwd) and `message`.")
                return {"op": "send", **cc.send(to, message, frm=frm, thread=thread, topic=topic)}
            if op == "broadcast":
                if not to or not message:
                    raise ValueError("cc_channel(op='broadcast') needs `to` (comma-separated) and `message`.")
                targets = [t.strip() for t in to.split(",") if t.strip()]
                import time as _t
                grp = thread or f"g-{int(_t.time())}"
                results = []
                for t in targets:
                    try:
                        results.append(cc.send(t, message, frm=frm, thread=grp, topic=topic))
                    except cc.ChannelError as e:
                        results.append({"to": t, "ok": False, "error": str(e)})
                return {"op": "broadcast", "thread": grp, "targets": len(targets), "results": results}
            if op == "mail":
                return {"op": "mail", "thread": thread or "(all)", "messages": cc.mail(thread=thread, limit=limit)}
        except cc.ChannelError as e:
            return {"op": op, "ok": False, "error": str(e)}
        raise ValueError(f"cc_channel: unknown op {op!r} — one of {OPS}.")
