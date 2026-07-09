"""mcp_face/tools/send.py — the ONE presence-aware send (the unified fabric front door).

Tim's intent, made a tool: "there was never meant to be two ... the system should recognise who's who,
and route. It shouldn't matter if the supervisor owns them or not." ONE call, `send(to, message)`:
  • `to` is recognised as a SESSION (durable uuid | ch-handle | as-id | agent-id | cwd | session://X —
    all resolve to the same actor even after its handle churns) or a CHANNEL (channel://<name-or-id>).
  • it resolves WHO they are (runtime.identity), routes to the transport that actually reaches them
    RIGHT NOW (the owning supervisor's inject OR the session's own live .mjs port — whichever works),
    falls back to the durable mailbox, and NEVER silently drops.
  • it returns a RECEIPT you can trust — the true transport + delivered-live-vs-queued, per target.

The two live transports are folded UNDER this one layer (runtime.router); it is not a third path. The
existing cc_channel / channel_act / session_post tools keep working — they already route through the
same welded functions (channel_act(post) → session_channels.post_to_channel, now presence-aware).
File-drop tool (pkgutil auto-register).
"""
from __future__ import annotations


def register(mcp, suite):
    def _resolve_channel(store, ref: str):
        """Return a channel id if `ref` names a channel (channel://<id|name>, or a bare id/name that
        exists as an active channel), else None → it is a session target. Name resolution is WIN C
        (address a channel by its NAME, not only its id — the read path already did, the write path
        didn't). An explicit channel://<x> that resolves to nothing FAILS LOUD (never silently retried
        as a session)."""
        from runtime import session_channels as _sc
        explicit = ref.startswith("channel://")
        bare = ref[len("channel://"):] if explicit else ref
        try:
            row = _sc.get_channel(store, bare)                     # by id
            if row:
                return row["id"]
        except Exception:
            pass
        try:                                                       # by name (WIN C)
            for cid, row in (_sc.fold_channels(store) or {}).items():
                if row.get("name") == bare and row.get("status") in (None, "active", "promoted"):
                    return cid
        except Exception:
            pass
        if explicit:
            raise ValueError(f"send: channel://{bare} not found — channels(op='list') shows the roster.")
        return None

    @mcp.tool()
    def send(to: str, message: str, thread: str = "", frm: str = "fabric") -> dict:
        """Send `message` to ONE target and get a TRUTHFUL receipt. `to` is either:
          • a SESSION — a durable uuid, a ch-handle, an as-id, an agent-id, a cwd, or session://<id>
            (all resolve to the same actor even after its ephemeral handle churns), OR
          • a CHANNEL — channel://<name-or-id> (fans to every member by their best path).
        Routes to the best LIVE transport (the owning supervisor's inject, or the session's own live
        .mjs port), else queues to the durable mailbox — it NEVER silently drops and NEVER reports a
        delivery it cannot confirm. `frm` = your session://<id> so a reply can route home; `thread`
        continues a conversation. Returns {kind:'session'|'channel', ...} naming the true transport(s)
        and whether each target got it LIVE or was queued for next-turn pull."""
        from runtime import router as _router
        from runtime import session_channels as _sc

        store = suite.store
        reg = getattr(suite, "get_agent_session", None)
        if not isinstance(to, str) or not to.strip():
            raise ValueError("send: `to` is required — a session (uuid/handle/agent-id/cwd/session://X) "
                             "or a channel (channel://<name-or-id>).")
        if not isinstance(message, str) or not message.strip():
            raise ValueError("send: `message` is empty — nothing to send.")
        target = to.strip()
        frm = (frm or "fabric").strip()

        cid = _resolve_channel(store, target)
        if cid is not None:
            res = _sc.post_to_channel(store, cid, message, frm, registry=reg, thread=thread or None)
            fan = res.get("fan", [])
            live = sum(1 for f in fan if f.get("delivered"))
            return {"kind": "channel", "channel": res.get("channel"), "members": len(fan),
                    "delivered_live": live, "queued": len(fan) - live, "thread": res.get("thread"),
                    "fan": fan, "what_happens": res.get("what_happens")}

        receipt = _router.route(target, message, frm=frm, thread=thread or None,
                                store=store, registry=reg)
        return {"kind": "session", **receipt}
