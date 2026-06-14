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
"""
from __future__ import annotations

from typing import Literal

OPS = ("list", "send", "broadcast", "mail")


def register(mcp, suite):
    @mcp.tool()
    def cc_channel(op: Literal["list", "send", "broadcast", "mail"],
                   to: str = "", message: str = "", thread: str = "", topic: str = "",
                   frm: str = "fabric", limit: int = 50) -> dict:
        """Message LIVE Claude Code sessions across the fabric (inject into their running
        conversation; replies push back to you — no polling). Pick `op`:

          op="list"      — discover live channel-sessions (handle · cwd · description).
          op="send"      — push `message` into the session `to` (handle/cwd); returns the thread.
          op="broadcast" — send `message` to many sessions (`to` = comma-separated) under one thread.
          op="mail"      — read the message/reply log (optionally one `thread`).

        A session becomes reachable by launching it with the channel
        (--mcp-config .../channels/channel.mcp.json --dangerously-load-development-channels
        server:company-channel). Live-only: a closed session is reached via session_post wake/consult.
        """
        from runtime import cc_channels as cc
        try:
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
