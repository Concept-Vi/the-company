"""mcp_face/tools/channels.py — the CROSS-SESSION FABRIC's structure face (Session Fabric R2.2–R2.5).

Channels · gatherings · connection edges · coordination — the structure AROUND sessions, exposed
to agents the same way the mailbox is (the sessions/session_post CQRS precedent, MCP-DESIGN-
PRINCIPLE law):

    channels(op=list|describe|history|edges, …)      → the ONE consolidated READ (pure, never writes)
    channel_act(action=create|gather|add|remove|status|post|mode|promote|disperse|archive, …)
                                                     → the ONE consequential WRITE (store appends)

A new need is a new `op`/`action`, never a new flat tool. Mechanism lives in
runtime/session_channels.py (the organ); this face is thin — it binds the suite's registry lookup
(liveness routing, member validation) and translates teaching errors outward.

ONE channel concept, two layers: these tools are the STRUCTURE layer (what a channel IS — name,
roster, mode, lifecycle; the ONE named-channel store, channels.jsonl). The TRANSPORT layer (reach a
live member NOW — push/find/reply-back) is the separate `cc_channel` tool over runtime/cc_channels.py.
There is no second channel store: cc_channels' former named-store was folded here and retired (2026-06-29).

THE FLOOR (synthesis §6.3): nothing here spawns/resumes a session. channel_act appends to the
channels leaf and (for action='post') fans intents onto the EXISTING mail leaf — the supervisor
service alone acts on deliver-class intents; queue-class are pulled by their targets. A channel
post can NEVER wake/spawn (the organ's routing law).

NAMING (criteria ruling N2): store leaf `agent_sessions/channels.jsonl` · addresses `channel://…`.
Exports OPS + ACTIONS (CONTRACT-FORMAT §9.2 — the closed machine inventories; drift teeth in
tests/agent_sessions_channels_acceptance.py).
"""
from typing import Literal
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from contracts.tools import ToolAnnotations as CompanyToolAnnotations
from mcp.types import ToolAnnotations as SDKToolAnnotations

from runtime import session_channels as sc

OPS = ("list", "describe", "history", "edges")
ACTIONS = ("create", "gather", "add", "remove", "status", "post", "mode",
           "promote", "disperse", "archive", "react", "unreact")


def _to_sdk_annotations(ann: CompanyToolAnnotations, title: str,
                        posture: str = "") -> SDKToolAnnotations:
    # `posture` (optional): the REMOTE-GATEWAY security tag remote.py:_tool_posture reads. posture="safe"
    # exposes a READ tool to the authenticated non-operator (client) tier. Rides verbatim (extra='allow').
    # Omitted ⇒ operator-only (fail-closed) — the write tool (channel_act) stays untagged.
    extra = {"posture": posture} if posture else {}
    return SDKToolAnnotations(
        title=title, readOnlyHint=ann.readonly, destructiveHint=ann.destructive,
        idempotentHint=ann.idempotent, openWorldHint=False, **extra)


def _registry(suite):
    """The per-session lookup bound for routing/validation — suite.get_agent_session when the
    registry lane is loaded; None (honest queue-everything, validate-nothing is NOT acceptable
    for membership, so membership ops fail teaching-loud instead) when absent."""
    return getattr(suite, "get_agent_session", None)


def _need_registry(suite, doing: str):
    reg = _registry(suite)
    if not callable(reg):
        raise ValueError(
            f"{doing} needs the agent-session registry fold (Suite.get_agent_session — Session "
            f"Fabric guide §B), which is not present in this running Suite. Restart the MCP "
            f"server against current main. (Membership must validate against the real fleet — "
            f"a roster of fabricated ids is worse than a refusal.)")
    return reg


def _members_arg(members) -> list[dict]:
    """Accept ["sid", …] or [{"session": sid, "participation": …}, …] — normalised for the organ."""
    out = []
    for m in (members or []):
        if isinstance(m, str):
            out.append({"session": m, "participation": "awake"})
        elif isinstance(m, dict) and m.get("session"):
            out.append({"session": m["session"],
                        "participation": m.get("participation", "awake")})
        else:
            raise ValueError(
                f"channel_act: bad member entry {m!r} — pass a session id string or "
                f"{{session, participation?}} (participation ∈ {list(sc.PARTICIPATION)}).")
    return out


def register(mcp, suite):
    # ── the consolidated READ ─────────────────────────────────────────────────────────────────
    # READ-ONLY across every op (list/describe/history/edges — "PURE READ; writes are channel_act").
    # posture="safe" exposes it to the client tier; the write tool channel_act stays untagged (operator-only).
    @mcp.tool(annotations=_to_sdk_annotations(
        CompanyToolAnnotations(readonly=True, destructive=False, idempotent=True),
        "Session fabric — channels/gatherings/edges (read)", posture="safe"))
    def channels(op: Literal["list", "describe", "history", "edges"], channel: str = "",
                 session: str = "", kind: str = "", status: str = "", q: str = "",
                 since: int = -1, limit: int = 50, probe_supervisor: bool = True) -> dict:
        """READ the cross-session fabric's STRUCTURE — channels (persistent named groups),
        gatherings (momentary grabs), and connection edges (who talked to whom). PURE READ (CQRS:
        writes are channel_act). Pick `op`:

          op="list"     — every channel + gathering: {id, kind, name, purpose, mode, coordinator,
                          status, member_count, posts, created, last_activity}. Filters: `kind`
                          (channel|gathering), `status` (active|archived|dispersed|promoted),
                          `q` (substring over name/purpose/id).
          op="describe" — ONE channel in full (`channel` required): row + members with their
                          PROJECTED statuses (declared awake/listening ∪ derived busy/closed —
                          composed from this registry + the agent-session registry + a live
                          supervisor probe; `status_source` says which sources answered, a down
                          supervisor is reported, never hidden). `probe_supervisor=False` skips
                          the live probe.
          op="history"  — the channel's EXCHANGE (`channel` required): each post (body resolved)
                          + the mail its thread gathered (replies, a conducted coordinator's
                          traffic). `since` = channel-event seq cursor. This is "what did they
                          work out?" answered from the channel's own exchange.
          op="edges"    — `session`'s CONNECTION HISTORY (required): every peer it has talked to
                          (direction-aware counts, verbs, channel attribution, recent threads) +
                          a ready-to-run follow-up handle (session_post args joining your latest
                          shared thread). Folded from the durable mail leaf — the talk itself is
                          the record.

        Empty results are HONEST (no channels / no history / no edges — never fabricated)."""
        if op not in OPS:
            raise ValueError(
                f"channels: unknown op={op!r}. Valid: {list(OPS)} — list=the registry · "
                f"describe=one channel + member statuses · history=the exchange · edges=a "
                f"session's connection history. To WRITE, use channel_act (CQRS).")
        store = suite.store
        if op == "list":
            rows = list(sc.fold_channels(store).values())
            if kind:
                if kind not in sc.KINDS:
                    raise ValueError(f"channels: unknown kind {kind!r} — {list(sc.KINDS)}.")
                rows = [r for r in rows if r["kind"] == kind]
            if status:
                if status not in sc.ROW_STATUS:
                    raise ValueError(f"channels: unknown status {status!r} — {list(sc.ROW_STATUS)}.")
                rows = [r for r in rows if r["status"] == status]
            if q:
                needle = q.lower()
                rows = [r for r in rows if needle in " ".join(
                    str(r.get(k) or "") for k in ("name", "purpose", "id")).lower()]
            rows.sort(key=lambda r: r.get("last_activity") or "", reverse=True)
            return {"op": op, "total": len(rows),
                    "channels": [{"id": f"channel://{r['id']}", "kind": r["kind"],
                                  "name": r["name"], "purpose": r["purpose"], "mode": r["mode"],
                                  "coordinator": r.get("coordinator"), "status": r["status"],
                                  "member_count": len(r["members"]), "posts": r.get("posts", 0),
                                  "promoted_to": r.get("promoted_to"), "origin": r.get("origin"),
                                  "created": r["created"], "last_activity": r["last_activity"]}
                                 for r in rows[:limit]]}
        if op == "describe":
            if not channel.strip():
                raise ValueError("channels: op='describe' needs `channel` (channel://<id> or the "
                                 "bare id — op='list' shows what exists).")
            row = sc.get_channel(store, channel)
            statuses = sc.member_statuses(store, channel, registry=_registry(suite),
                                          probe_supervisor=probe_supervisor)
            return {"op": op, "channel": f"channel://{row['id']}",
                    "record": {k: row.get(k) for k in
                               ("id", "kind", "name", "purpose", "mode", "coordinator", "status",
                                "origin", "promoted_to", "created", "last_activity", "posts")},
                    "members": statuses["members"], "supervisor": statuses["supervisor"],
                    "status_source": statuses["status_source"],
                    "next": "channels(op='history', channel=…) reads the exchange; "
                            "channel_act(action='post', …) messages it."}
        if op == "history":
            if not channel.strip():
                raise ValueError("channels: op='history' needs `channel`.")
            return {"op": op, **sc.channel_history(store, channel, since=since, limit=limit)}
        # op == "edges"
        if not session.strip():
            raise ValueError("channels: op='edges' needs `session` — whose connection history? "
                             "(a session id or session://<id>; sessions(op='list') shows the fleet).")
        return {"op": op, **sc.edges_for(store, session, limit=limit)}

    # ── the consequential WRITE ───────────────────────────────────────────────────────────────
    @mcp.tool(annotations=_to_sdk_annotations(
        CompanyToolAnnotations(readonly=False, destructive=False, idempotent=False),
        "Session fabric — act on channels/gatherings (write)"))
    def channel_act(action: Literal["create", "gather", "add", "remove", "status", "post",
                                    "mode", "promote", "disperse", "archive", "react", "unreact"],
                    channel: str = "", name: str = "", purpose: str = "",
                    members: list = None, session: str = "", participation: str = "awake",
                    message: str = "", from_session: str = "", thread: str = "",
                    mode: str = "", coordinator: str = "", parent: str = "",
                    kind: str = "live-session", label: str = "",
                    reply_to: int = None, emoji: str = "") -> dict:
        """ACT on the cross-session fabric's structure (the one WRITE — CQRS twin of `channels`).
        Everything is a durable store append; NOTHING here spawns or wakes a session (a channel
        post routes deliver-class intents to the supervisor for live members and queue-class for
        the rest — never wake/consult; those are session_post's deliberate, targeted acts).

          action="create"   — mint a persistent CHANNEL: `name` (required), `purpose`, `members`
                              (session ids or {session, participation}), `mode`
                              (direct|conducted; conducted needs `coordinator` ∈ members),
                              `parent` (channel://… — a sub-channel, the recursion).
          action="gather"   — grab a GATHERING for right-now (same args as create; momentary:
                              disperse it when done, or promote it if it proves durable).
          action="add"      — add a member (`channel`, `session`, `participation`, `kind`,
                              `label`). `kind` ∈ human|live-session|model — HOW the member is
                              present (a person on a face · a Claude Code session reached via
                              inject · an AI brain that is a first-class member, e.g. the operator
                              model). `label` is an optional display identity. A human/model member
                              is NOT validated against the agent-session registry (only a session is).
          action="remove"   — remove a member (`channel`, `session`).
          action="status"   — declare a member's posture (`channel`, `session`,
                              `participation` ∈ awake|listening). busy/closed are DERIVED —
                              read them via channels(op='describe').
          action="post"     — MESSAGE the channel (`channel`, `message`, `from_session`).
                              direct → fans to every member (live→supervisor inject ·
                              rest→next-turn inbox pickup); conducted → ONE context-laden intent
                              to the coordinator, who works the members on the returned thread.
                              `thread` joins an existing conversation; `reply_to` (a prior post's
                              seq) makes this a single-level THREAD reply (inherits the parent's
                              conversation, collapses reply-of-reply to root — OWUI-style).
          action="react"    — add a REACTION (`channel`, `message`=the post seq or a face's msg
                              ref, `from_session`=who reacted, `emoji`). A channel primitive: the
                              fold exposes reactions per message (channels(op='history')).
          action="unreact"  — remove a reaction (same args; set semantics — removing an absent one
                              is a no-op, never an error).
          action="mode"     — set coordination (`channel`, `mode`; conducted needs `coordinator`).
          action="promote"  — gathering → durable channel (provenance stamped both ways).
          action="disperse" — let a gathering go (terminal; history stays readable).
          action="archive"  — close a channel (terminal; history stays readable).

        VERIFY consequences, don't assume: a post returns its fan (per-member verb + mail seq) —
        replies land under the returned `thread` (sessions(op='inbox', thread=…)); the channel's
        own record of the exchange is channels(op='history')."""
        if action not in ACTIONS:
            raise ValueError(
                f"channel_act: unknown action={action!r}. Valid: {list(ACTIONS)} — create/gather "
                f"mint · add/remove/status work the roster · post messages · mode sets "
                f"coordination · promote/disperse/archive are lifecycle.")
        store = suite.store
        if action in ("create", "gather"):
            reg = _need_registry(suite, f"channel_act(action='{action}')")
            row = sc.create_channel(
                store, name=name, purpose=purpose, members=_members_arg(members),
                mode=mode or "direct", coordinator=coordinator or None,
                kind=("channel" if action == "create" else "gathering"),
                origin=({"parent": parent} if parent.strip() else None), registry=reg)
            return {"action": action, "channel": f"channel://{row['id']}", "kind": row["kind"],
                    "name": row["name"], "mode": row["mode"], "coordinator": row.get("coordinator"),
                    "members": sorted(row["members"]),
                    "next": "channel_act(action='post', channel=…, message=…, from_session=…) "
                            "messages it; channels(op='describe') shows member statuses."}
        if not channel.strip():
            raise ValueError(f"channel_act: action='{action}' needs `channel` "
                             f"(channels(op='list') shows what exists).")
        if action == "add":
            # registry is needed to validate a live-session member; a human/model member is not a
            # session, so the lookup is skipped inside add_member (kind-gated). Still bind it when present.
            reg = _registry(suite) if kind != "live-session" else _need_registry(suite, "channel_act(action='add')")
            row = sc.add_member(store, channel, session, participation=participation,
                                kind=kind, label=label or None, registry=reg)
        elif action in ("react", "unreact"):
            if not from_session.strip():
                raise ValueError(f"channel_act: action='{action}' needs `from_session` — who "
                                 f"reacted (the reacting member's handle/session).")
            fn = sc.react if action == "react" else sc.unreact
            fn(store, channel, message, from_session, emoji)
            return {"action": action, "channel": f"channel://{sc._chan_bare(channel)}",
                    **sc.reactions_for(store, channel, message)}
        elif action == "remove":
            row = sc.remove_member(store, channel, session)
        elif action == "status":
            row = sc.set_member_status(store, channel, session, participation)
        elif action == "post":
            return {"action": action,
                    **sc.post_to_channel(store, channel, message, from_session,
                                         registry=_registry(suite),
                                         thread=thread or None, reply_to=reply_to)}
        elif action == "mode":
            row = sc.set_mode(store, channel, mode, coordinator=coordinator or None)
        elif action == "promote":
            reg = _need_registry(suite, "channel_act(action='promote')")
            row = sc.promote_gathering(store, channel, name=name or None,
                                       purpose=purpose or None, mode=mode or None,
                                       coordinator=coordinator or None, registry=reg)
            return {"action": action, "channel": f"channel://{row['id']}",
                    "origin": row.get("origin"), "members": sorted(row["members"]),
                    "note": "the gathering is now status='promoted' with promoted_to → this "
                            "channel; its history remains readable."}
        elif action == "disperse":
            row = sc.disperse_gathering(store, channel)
        else:  # archive
            row = sc.archive_channel(store, channel)
        return {"action": action, "channel": f"channel://{row['id']}", "status": row["status"],
                "mode": row["mode"], "coordinator": row.get("coordinator"),
                "members": sorted(row["members"])}

    return channels, channel_act
