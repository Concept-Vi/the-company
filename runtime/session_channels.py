"""runtime/session_channels.py — the CROSS-SESSION FABRIC ORGANS (Session Fabric R2.2–R2.5).

The structure AROUND sessions — the genuinely-new layer the operational-requirements doc names
(never a wrapper for what a session does natively): CHANNELS (persistent work-centric groups,
R2.2) · GATHERINGS (momentary grabs, promotable, R2.3) · CONNECTION EDGES (durable who-talked-
to-whom recorded on the session, R2.4) · COORDINATION MODES (direct router vs conducted
coordinator, recursing, R2.5).

REGISTRY-SHAPED BY DESIGN (the R11/R12 heart frame): everything here is registry content —
  · the channel/gathering registry  = a fold over ONE append-only leaf
    (`<store>/agent_sessions/channels.jsonl` — the mail.jsonl twin: graph-locked cross-process-
    unique seq, fsync'd appends, log-IS-the-index; naming law N2 — inside `agent_sessions/`,
    never `fabric/`)
  · the closed vocabularies are module constants (CHANNEL_OPS / KINDS / MODES / PARTICIPATION /
    ROW_STATUS) — a new lifecycle event/kind/mode is a REGISTRY-VOCABULARY change here and
    nowhere else (registry-is-truth)
  · connection edges are a PROJECTION registry — folded at read time from the durable mail leaf
    (`agent_sessions/mail.jsonl`), the same log-owns-the-trajectory argument as the session
    registry fold. The mail log IS the durable record of "A talked to B"; the edge fold makes it
    legible per-session. These are exactly the rows a future heart ingests (couplings resolve
    against them).

THE ROUTING LAW (the genuinely-new mechanism, riding the EXISTING fabric — surface, don't
rebuild): a channel post does NOT invent a second message path. It FANS to per-member records on
the one mail leaf (store.append_agent_mail — the same intents the supervisor service already
pops). Per-member verb resolution mirrors the session_post router's own liveness rule:
    supervised-live member → "deliver"  (the supervisor injects it into the live conversation)
    anything else          → "queue"    (the member PULLS it via sessions(op='inbox') next turn)
A channel post NEVER wakes/spawns (verbs wake/consult are session_post's deliberate, targeted
acts — a broadcast that stampede-respawns N closed sessions would be a silent consequence, and
this module refuses to own one). Fan mail carries `channel` + the post's `thread`, so inboxes
show provenance and the edge fold attributes the connection via the channel.

CONDUCTED MODE (R2.5): mode="conducted" routes the WHOLE post to the COORDINATOR session only,
as ONE intent whose body is the channel context (purpose · roster with live states · the message
· how to work the members: session_post joined on this thread). The coordinator — a real session
— holds the channel's purpose and works the members; its session_posts ARE the conducted
exchange (threads + edges accrue on the same leaves). The primitive RECURSES: any member can
coordinate a sub-channel (`origin={"parent": "channel://…"}`) — the sub-commander shape.

THE FLOOR (synthesis §6.3 — same side as the MCP face): this module NEVER spawns `claude -p`,
never resumes a session, never imports the supervisor. Writes are store appends (registry-
filling class). It also emits NO `agent_sessions.*` events on events.jsonl — the single-writer
law (audit C6) stays intact: channel lifecycle lives on its OWN leaf; the supervisor remains the
only events.jsonl fabric writer.

SUPERVISOR LIVENESS REFINEMENT (honest, never silent): the registry's closed state vocabulary
has no "busy" — that is the live supervisor's per-turn state machine. `member_statuses` may
PROBE the supervisor's HTTP read face (127.0.0.1:8771/sessions, sub-second timeout) to refine
awake/listening into "busy" for mid-turn members; the result ALWAYS carries `status_source`
("registry" | "registry+supervisor") and a probe failure is REPORTED in the result
(supervisor:"down"), never swallowed into a pretend-fresh answer.

Consumers: mcp_face/tools/channels.py (the agent face — CQRS pair channels/channel_act) ·
tests/agent_sessions_channels_acceptance.py (the teeth). The fold deliberately lives HERE
(beside Suite, not in it) so the R2 lane stays file-disjoint from the R1/R3/R4 lanes working
suite.py/session_supervisor.py/sessions.py; lifting it onto Suite later is a clean move (one
import site), recorded as an open seam, not a hidden one.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

# ── the closed vocabularies (registry-is-truth: defined ONCE, here) ────────────────────────────
# Lifecycle events on the channels leaf. A new event kind is added HERE and folded in
# _apply_channel_event — nowhere else.
CHANNEL_OPS = (
    "channel.created",        # {channel, kind, name, purpose, mode, coordinator?, members[], origin?}
    "channel.member_added",   # {channel, session, participation}
    "channel.member_removed", # {channel, session}
    "channel.member_status",  # {channel, session, participation}
    "channel.posted",         # {channel, from, cas, thread, mode, fan:[{session, verb, mail_seq}], coordinator?}
    "channel.mode_set",       # {channel, mode, coordinator?}
    "channel.archived",       # {channel}
    "gathering.dispersed",    # {channel}   — terminal for kind=gathering
    "gathering.promoted",     # {channel, promoted_to}  — gathering → durable channel
)
KINDS = ("channel", "gathering")
MODES = ("direct", "conducted")                  # R2.5: router vs conductor
PARTICIPATION = ("awake", "listening")           # the DECLARED member posture (R2.2 vocabulary);
                                                 # busy/closed are DERIVED (registry + supervisor), never stored
ROW_STATUS = ("active", "archived", "dispersed", "promoted")   # the row lifecycle (kind-dependent terminals)

LEAF = "channels.jsonl"                          # beside mail.jsonl under <store>/agent_sessions/
LOCK_KEY = "agent_sessions:channels"             # the cross-process append lock (the mail-leaf twin)
SUPERVISOR_URL = "http://127.0.0.1:8771"         # the supervisor's READ face (ops/services.json row);
                                                 # probed read-only for busy-refinement, never commanded


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _addr(sid: str) -> str:
    sid = sid.strip()
    return sid if sid.startswith("session://") else f"session://{sid}"


def _bare(ref: str) -> str:
    ref = (ref or "").strip()
    return ref[len("session://"):] if ref.startswith("session://") else ref


def _chan_addr(cid: str) -> str:
    cid = cid.strip()
    return cid if cid.startswith("channel://") else f"channel://{cid}"


def _chan_bare(ref: str) -> str:
    ref = (ref or "").strip()
    return ref[len("channel://"):] if ref.startswith("channel://") else ref


def _leaf_path(store):
    return store.root / "agent_sessions" / LEAF


# ── the leaf (append + read — the append_agent_mail discipline, second instance) ───────────────
def append_channel_event(store, rec: dict) -> dict:
    """Persist ONE channel-lifecycle event to the append-only channels leaf. STRUCTURAL fail-loud:
    `kind` must be in the closed CHANNEL_OPS vocabulary and `channel` non-empty (an event that
    names no channel is unfoldable — a black hole, store rule 4). Owns `seq`/`ts` (never caller-
    overridable). Cross-process-unique monotonic seq under graph_lock (the append_event landmine,
    closed here exactly as for mail — every Claude Code session runs its own MCP-face process over
    this one store). Fsync'd before return: a channel you were told exists survives a crash."""
    kind = rec.get("kind")
    if kind not in CHANNEL_OPS:
        raise ValueError(
            f"append_channel_event: unknown kind {kind!r} — the closed lifecycle vocabulary is "
            f"{list(CHANNEL_OPS)} (registry-is-truth; a new lifecycle event is added to "
            f"runtime/session_channels.CHANNEL_OPS + its fold, never ad-hoc).")
    cid = rec.get("channel")
    if not isinstance(cid, str) or not cid.strip():
        raise ValueError(
            "append_channel_event: `channel` must be a non-empty channel id — an event that names "
            "no channel can never be folded. Fail loud, never write an unfoldable record.")
    d = store.root / "agent_sessions"
    d.mkdir(parents=True, exist_ok=True)
    path = d / LEAF
    with store.graph_lock(LOCK_KEY):
        seq = 0
        if path.exists():
            with path.open("rb") as f:
                try:
                    f.seek(-2, 2)
                    while f.read(1) != b"\n":
                        f.seek(-2, 1)
                except OSError:
                    f.seek(0)
                last = f.readline().decode().strip()
            if last:
                seq = json.loads(last).get("seq", -1) + 1
        out = {**rec, "seq": seq, "ts": _now()}
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(out) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return out


def channel_events_since(store, seq: int = -1, *, channel: str | None = None,
                         limit: int | None = None) -> list[dict]:
    """Channel events with seq STRICTLY greater than `seq`, OLDEST-first (the events_since
    semantics — a fresh consumer passes -1). `channel` filters one channel's lifecycle. Reads
    disk every call (a sibling process's appends are seen next call). Honest empty list."""
    path = _leaf_path(store)
    if not path.exists():
        return []
    cid = _chan_bare(channel) if channel else None
    out = []
    for l in path.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        rec = json.loads(l)
        if rec.get("seq", -1) <= seq:
            continue
        if cid is not None and rec.get("channel") != cid:
            continue
        out.append(rec)
        if limit is not None and len(out) >= limit:
            break
    return out


# ── the fold (log-IS-the-index — the _agent_session_fold pattern, applied to channels) ─────────
def fold_channels(store) -> dict[str, dict]:
    """Project the channel/gathering registry rows from the leaf. Read-time fold, no parallel
    store: a fresh process rebuilds everything from shared disk (persistence-survives-reload).
    Row shape: {id, kind, name, purpose, mode, coordinator, status, members:{sid→{participation,
    added}}, origin, created, last_activity, posts, seq}. The leaf is the small registry log
    (channel lifecycle, not message bodies) — a full re-read per call is the honest baseline;
    an incremental high-water fold is the documented next step if this leaf ever grows hot."""
    rows: dict[str, dict] = {}
    for e in channel_events_since(store, -1):
        _apply_channel_event(rows, e)
    return rows


def _apply_channel_event(rows: dict, e: dict) -> None:
    """Fold ONE event into the rows — the single source of the row-update rule."""
    cid = e.get("channel")
    k = e.get("kind")
    if k == "channel.created":
        rows[cid] = {
            "id": cid, "kind": e.get("channel_kind", "channel"), "name": e.get("name"),
            "purpose": e.get("purpose"), "mode": e.get("mode", "direct"),
            "coordinator": e.get("coordinator"), "status": "active",
            "members": {m["session"]: {"participation": m.get("participation", "awake"),
                                       "added": e.get("ts")}
                        for m in (e.get("members") or [])},
            "origin": e.get("origin"), "created": e.get("ts"),
            "last_activity": e.get("ts"), "posts": 0, "seq": e.get("seq"),
        }
        return
    row = rows.get(cid)
    if row is None:
        return                                   # an event for a channel whose create we haven't seen —
                                                 # surfaced by reads as fold_errors? kept simple: the leaf is
                                                 # single-file append-ordered, so this only happens on a
                                                 # hand-corrupted leaf; describe() fails loud on unknown ids.
    row["last_activity"] = e.get("ts")
    row["seq"] = e.get("seq")
    if k == "channel.member_added":
        row["members"][e["session"]] = {"participation": e.get("participation", "awake"),
                                        "added": e.get("ts")}
    elif k == "channel.member_removed":
        row["members"].pop(e.get("session"), None)
    elif k == "channel.member_status":
        m = row["members"].get(e.get("session"))
        if m is not None:
            m["participation"] = e.get("participation")
    elif k == "channel.posted":
        row["posts"] = row.get("posts", 0) + 1
    elif k == "channel.mode_set":
        row["mode"] = e.get("mode")
        if e.get("coordinator") is not None:
            row["coordinator"] = e.get("coordinator")
    elif k == "channel.archived":
        row["status"] = "archived"
    elif k == "gathering.dispersed":
        row["status"] = "dispersed"
    elif k == "gathering.promoted":
        row["status"] = "promoted"
        row["promoted_to"] = e.get("promoted_to")


def get_channel(store, cid: str) -> dict:
    """One channel row, fail-loud on unknown (never fabricate a channel)."""
    cid = _chan_bare(cid)
    row = fold_channels(store).get(cid)
    if row is None:
        raise ValueError(
            f"get_channel: unknown channel {cid!r} — not on the channels leaf. "
            f"list via fold_channels/channels(op='list'); create via create_channel/"
            f"channel_act(action='create'|'gather'). Fail loud, never fabricate.")
    return row


def _require_active(row: dict, doing: str) -> None:
    if row.get("status") != "active":
        raise ValueError(
            f"{doing}: channel://{row['id']} is {row['status']!r}, not active — "
            f"{'a dispersed gathering is gone (form a new one, or it was promoted: see promoted_to)' if row['status'] in ('dispersed', 'promoted') else 'an archived channel is read-only history'}. "
            f"Reads (describe/history/edges) still work; writes refuse loud.")


# ── R2.2 / R2.3 — create · gather · membership · status ────────────────────────────────────────
def create_channel(store, *, name: str, purpose: str = "", members: list[dict] | None = None,
                   mode: str = "direct", coordinator: str | None = None,
                   kind: str = "channel", origin: dict | None = None,
                   registry=None) -> dict:
    """Mint a channel (R2.2) or gathering (R2.3 — same primitive, kind discriminates: universal
    composition, one relational mechanism reused). `members` = [{session, participation?}…];
    each session is validated against the agent-session registry when a `registry` lookup is
    supplied (fail-loud on unknown ids — never a roster of fabrications); pass registry=None only
    where no registry exists (isolated tests). mode="conducted" requires a coordinator who IS a
    member (a conductor outside the room cannot hold its purpose). `origin` records provenance
    ({"parent": "channel://…"} for a sub-channel — the R2.5 recursion; {"promoted_from": …} is
    stamped by promote_gathering). Returns the folded row."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("create_channel: `name` must be non-empty — channels are work-centric "
                         "NAMED groups (the name is how the fleet view reads them).")
    if kind not in KINDS:
        raise ValueError(f"create_channel: kind must be one of {list(KINDS)}, got {kind!r}.")
    if mode not in MODES:
        raise ValueError(
            f"create_channel: unknown mode {mode!r} — the coordination vocabulary is {list(MODES)} "
            f"(direct = the fabric routes posts to every member · conducted = ONE coordinator "
            f"session receives posts and works the members).")
    norm: list[dict] = []
    seen = set()
    for m in (members or []):
        sid = _bare(m["session"] if isinstance(m, dict) else m)
        if not sid:
            raise ValueError("create_channel: a member entry has an empty session id.")
        part = (m.get("participation", "awake") if isinstance(m, dict) else "awake")
        if part not in PARTICIPATION:
            raise ValueError(
                f"create_channel: unknown participation {part!r} for {sid} — declared postures are "
                f"{list(PARTICIPATION)} (awake = full participant · listening = receives, not "
                f"worked). busy/closed are DERIVED states, never declared.")
        if registry is not None:
            registry(sid)                        # fail-loud teaching error on unknown (the registry's own)
        if sid not in seen:
            norm.append({"session": sid, "participation": part})
            seen.add(sid)
    coord = _bare(coordinator) if coordinator else None
    if mode == "conducted":
        if not coord:
            raise ValueError(
                "create_channel: mode='conducted' requires `coordinator` — the ONE session that "
                "receives the channel's posts and works the members (R2.5). Use mode='direct' for "
                "router fan-out.")
        if coord not in seen:
            raise ValueError(
                f"create_channel: coordinator {coord} is not a member — the conductor holds the "
                f"channel's purpose from INSIDE it. Add it to `members` too.")
    prefix = "ch" if kind == "channel" else "ga"
    # id mint rides the same lock as the append (seq-unique), via a created-event carrying members inline
    # (a gathering is GRABBED in one gesture — one event, not N+1).
    with store.graph_lock(LOCK_KEY + ":mint"):
        existing = fold_channels(store)
        n = sum(1 for r in existing.values() if r["kind"] == kind)
        cid = f"{prefix}-{n}"
        while cid in existing:                   # archive/promote never frees an id; scan past collisions
            n += 1
            cid = f"{prefix}-{n}"
        append_channel_event(store, {
            "kind": "channel.created", "channel": cid, "channel_kind": kind,
            "name": name.strip(), "purpose": purpose or "", "mode": mode,
            "coordinator": coord, "members": norm, "origin": origin})
    return get_channel(store, cid)


def add_member(store, cid: str, session: str, *, participation: str = "awake",
               registry=None) -> dict:
    """Fluid membership, the add half (R2.2). Validated against the agent-session registry when
    supplied. Adding an existing member is refused loud (use set_member_status to change posture
    — a silent re-add would silently reset their declared posture)."""
    if participation not in PARTICIPATION:
        raise ValueError(f"add_member: unknown participation {participation!r} — declared postures "
                         f"are {list(PARTICIPATION)}.")
    row = get_channel(store, cid)
    _require_active(row, "add_member")
    sid = _bare(session)
    if sid in row["members"]:
        raise ValueError(
            f"add_member: {_addr(sid)} is already a member of channel://{row['id']} — to change "
            f"its posture use set_member_status; membership is a set, not a multiset.")
    if registry is not None:
        registry(sid)
    append_channel_event(store, {"kind": "channel.member_added", "channel": row["id"],
                                 "session": sid, "participation": participation})
    return get_channel(store, cid)


def remove_member(store, cid: str, session: str) -> dict:
    """Fluid membership, the remove half. Removing a non-member is refused loud (the caller's
    model of the roster is wrong — teach, don't no-op silently). Removing the COORDINATOR of a
    conducted channel is refused (a conducted channel without its conductor is headless — set a
    new coordinator via set_mode first)."""
    row = get_channel(store, cid)
    _require_active(row, "remove_member")
    sid = _bare(session)
    if sid not in row["members"]:
        raise ValueError(
            f"remove_member: {_addr(sid)} is not a member of channel://{row['id']} — the roster is "
            f"{sorted(row['members'])}. Nothing was changed (no silent no-op).")
    if row.get("mode") == "conducted" and row.get("coordinator") == sid:
        raise ValueError(
            f"remove_member: {_addr(sid)} is the COORDINATOR of conducted channel://{row['id']} — "
            f"removing it would leave the channel headless. set_mode(mode='conducted', "
            f"coordinator=<other member>) or set_mode(mode='direct') first.")
    append_channel_event(store, {"kind": "channel.member_removed", "channel": row["id"],
                                 "session": sid})
    return get_channel(store, cid)


def set_member_status(store, cid: str, session: str, participation: str) -> dict:
    """Declare a member's posture (awake|listening) — the DECLARED half of R2.2's per-member
    status; the live half (busy/closed) is derived by member_statuses, never stored here."""
    if participation not in PARTICIPATION:
        raise ValueError(
            f"set_member_status: unknown participation {participation!r} — declared postures are "
            f"{list(PARTICIPATION)} (awake|listening). busy/closed are DERIVED (registry + "
            f"supervisor probe), not declarable: a stored liveness flag rots.")
    row = get_channel(store, cid)
    _require_active(row, "set_member_status")
    sid = _bare(session)
    if sid not in row["members"]:
        raise ValueError(f"set_member_status: {_addr(sid)} is not a member of channel://{row['id']} "
                         f"— add_member first.")
    append_channel_event(store, {"kind": "channel.member_status", "channel": row["id"],
                                 "session": sid, "participation": participation})
    return get_channel(store, cid)


def set_mode(store, cid: str, mode: str, *, coordinator: str | None = None) -> dict:
    """Flip the coordination mode (R2.5). conducted requires a member coordinator; direct clears
    the requirement (the coordinator field is kept as history unless overridden)."""
    if mode not in MODES:
        raise ValueError(f"set_mode: unknown mode {mode!r} — {list(MODES)}.")
    row = get_channel(store, cid)
    _require_active(row, "set_mode")
    coord = _bare(coordinator) if coordinator else None
    if mode == "conducted":
        coord = coord or row.get("coordinator")
        if not coord:
            raise ValueError("set_mode: conducted needs `coordinator` (a member session).")
        if coord not in row["members"]:
            raise ValueError(f"set_mode: coordinator {coord} is not a member of "
                             f"channel://{row['id']} — add_member first.")
    append_channel_event(store, {"kind": "channel.mode_set", "channel": row["id"],
                                 "mode": mode, "coordinator": coord})
    return get_channel(store, cid)


def archive_channel(store, cid: str) -> dict:
    """Archive a CHANNEL (read-only history). Gatherings don't archive — they disperse."""
    row = get_channel(store, cid)
    if row["kind"] != "channel":
        raise ValueError(f"archive_channel: channel://{row['id']} is a {row['kind']} — gatherings "
                         f"DISPERSE (disperse_gathering) or get PROMOTED; archive is the durable "
                         f"channel's terminal.")
    _require_active(row, "archive_channel")
    append_channel_event(store, {"kind": "channel.archived", "channel": row["id"]})
    return get_channel(store, cid)


def disperse_gathering(store, cid: str) -> dict:
    """R2.3 — let the momentary grab go. Terminal; history (events + mail) remains readable."""
    row = get_channel(store, cid)
    if row["kind"] != "gathering":
        raise ValueError(f"disperse_gathering: channel://{row['id']} is a {row['kind']} — durable "
                         f"channels ARCHIVE; disperse is the gathering's terminal.")
    _require_active(row, "disperse_gathering")
    append_channel_event(store, {"kind": "gathering.dispersed", "channel": row["id"]})
    return get_channel(store, cid)


def promote_gathering(store, cid: str, *, name: str | None = None, purpose: str | None = None,
                      mode: str | None = None, coordinator: str | None = None,
                      registry=None) -> dict:
    """R2.3 — the gathering proved durable: promote it to a CHANNEL. Members + posture carry
    over; provenance is stamped both ways (the channel's origin.promoted_from, the gathering's
    promoted_to) so the channel's history is answerable back through its gathering prelude.
    The gathering becomes terminal status='promoted'."""
    row = get_channel(store, cid)
    if row["kind"] != "gathering":
        raise ValueError(f"promote_gathering: channel://{row['id']} is already a {row['kind']} — "
                         f"only gatherings promote.")
    _require_active(row, "promote_gathering")
    members = [{"session": s, "participation": m["participation"]}
               for s, m in row["members"].items()]
    chan = create_channel(
        store, name=name or row.get("name") or row["id"], purpose=purpose or row.get("purpose") or "",
        members=members, mode=mode or row.get("mode") or "direct",
        coordinator=coordinator or row.get("coordinator"), kind="channel",
        origin={"promoted_from": _chan_addr(row["id"])}, registry=registry)
    append_channel_event(store, {"kind": "gathering.promoted", "channel": row["id"],
                                 "promoted_to": _chan_addr(chan["id"])})
    return get_channel(store, chan["id"])


# ── the post router (R2.2 message-the-channel · R2.5 direct vs conducted) ──────────────────────
def post_to_channel(store, cid: str, message: str, from_: str, *,
                    registry=None, thread: str | None = None) -> dict:
    """Message the channel — the ONE write that makes a channel a live thing rather than a list.

    direct (the ROUTER): fan to every member except the sender, one mail intent each on the
    existing leaf — supervised-live members get verb='deliver' (the supervisor injects); everyone
    else verb='queue' (next-turn pull). NEVER wake/consult (no broadcast may stampede-spawn).
    conducted (the CONDUCTOR): ONE intent to the coordinator carrying the channel context —
    purpose, roster with live states, the message, and how to work the members (session_post on
    this same thread). The coordinator session does the routing-with-judgment; that is the point.

    `registry` = the per-session lookup (suite.get_agent_session) used for liveness routing; when
    None (no registry in scope), every fan record is honestly verb='queue'. All fan mail carries
    `channel` + one shared `thread` (minted here if not joining an existing one) — provenance for
    inboxes, attribution for the edge fold, aggregation for replies. Returns the posted event +
    the fan (per-member verb + mail seq) so the caller can verify consequences, not assume them."""
    if not isinstance(message, str) or not message.strip():
        raise ValueError("post_to_channel: `message` is empty — nothing to route.")
    if not isinstance(from_, str) or not from_.strip():
        raise ValueError("post_to_channel: `from_` is required — the reply path (your "
                         "session://<id>; a stable label is accepted but not reply-addressable).")
    row = get_channel(store, cid)
    _require_active(row, "post_to_channel")
    sender = _bare(from_)
    mode = row.get("mode", "direct")
    if mode == "conducted":
        targets = [row["coordinator"]]
        if not targets[0]:
            raise ValueError(f"post_to_channel: conducted channel://{row['id']} has no coordinator "
                             f"— set_mode first (the fold should have prevented this; the leaf may "
                             f"be hand-edited).")
    else:
        targets = [s for s in row["members"] if s != sender]
        if not targets:
            raise ValueError(
                f"post_to_channel: channel://{row['id']} has no members besides the sender — a fan "
                f"to nobody is a dead letter. add_member first (the roster is {sorted(row['members'])}).")

    def _state(sid: str) -> str | None:
        if registry is None:
            return None
        try:
            return (registry(sid) or {}).get("state")
        except ValueError:
            return None                          # not in the registry — honestly unknown → queue

    # ONE shared thread per post, PRE-minted (append_agent_mail honours caller threads) so every
    # fan record — and the conducted body's own work-instructions — carry the same aggregation key
    # from birth. Joining an existing conversation = pass `thread`.
    import uuid as _uuid
    mail_thread = (thread.strip() if isinstance(thread, str) and thread.strip()
                   else f"chan-{row['id']}-{_uuid.uuid4().hex[:8]}")
    fan = []
    for sid in targets:
        st = _state(sid)
        if mode == "conducted":
            body = {
                "channel": _chan_addr(row["id"]), "name": row.get("name"),
                "purpose": row.get("purpose"), "mode": "conducted", "you_are": "coordinator",
                "from": from_.strip(), "message": message, "thread": mail_thread,
                "members": [{"session": _addr(s), "participation": m["participation"],
                             "live_state": _state(s)}
                            for s, m in row["members"].items() if s != sid],
                "how_to_work_the_channel": (
                    f"You coordinate this channel (Session Fabric R2.5). Work the members toward "
                    f"the purpose: message a member with the company MCP's session_post(to=<member>, "
                    f"message=…, from_session='session://<your id>', thread='{mail_thread}') — keep "
                    f"this thread so the exchange aggregates; read replies via sessions(op='inbox', "
                    f"session='session://<your id>', thread='{mail_thread}'). Members marked "
                    f"listening receive but are not worked. Report the outcome back to "
                    f"{from_.strip()} on the same thread."),
            }
        else:
            body = {"channel": _chan_addr(row["id"]), "name": row.get("name"),
                    "from": from_.strip(), "message": message, "thread": mail_thread,
                    "participation": row["members"].get(sid, {}).get("participation")}
        verb = "deliver" if st == "supervised-live" else "queue"
        cas = store.put_content(body)
        out = store.append_agent_mail({
            "to": _addr(sid), "from": from_.strip(), "verb": verb, "cas": cas,
            "thread": mail_thread, "channel": _chan_addr(row["id"]), "channel_post": True,
            "state_at_post": st, "source": "session_channels.post_to_channel"})
        fan.append({"session": _addr(sid), "verb": verb, "mail_seq": out["seq"]})
    ev = append_channel_event(store, {
        "kind": "channel.posted", "channel": row["id"], "from": from_.strip(),
        "cas": store.put_content(message), "thread": mail_thread, "mode": mode,
        "coordinator": row.get("coordinator") if mode == "conducted" else None, "fan": fan})
    return {"posted": ev["seq"], "channel": _chan_addr(row["id"]), "mode": mode,
            "thread": mail_thread, "fan": fan,
            "what_happens": ("the coordinator session receives the channel context + your message "
                             "as one intent and works the members (watch the thread)"
                             if mode == "conducted" else
                             "each live member gets a supervisor inject; others pick it up via "
                             "sessions(op='inbox') at their next turn"),
            "replies": f"agent_mail_since(thread='{mail_thread}') / sessions(op='inbox', thread=…)"}


# ── R2.2 — per-member status (declared ∪ derived, honest about its sources) ────────────────────
def member_statuses(store, cid: str, *, registry=None, probe_supervisor: bool = True) -> dict:
    """Project every member's STATUS — the R2.2 vocabulary (awake/listening/busy/closed) composed
    honestly from its three sources, never a stored flag that rots:
      declared  (this registry)  : awake | listening — the member's posture in THIS channel
      registry  (agent sessions) : supervised-live | unsupervised-live | closed — fleet liveness
      supervisor (live probe)    : busy | idle — the per-turn state machine, only the live
                                   service knows it; probed read-only (GET /sessions, sub-second)
    Composition rule: closed (registry) wins → 'closed'; a busy probe refines a live member →
    'busy'; otherwise the declared posture stands. Every result carries `status_source` and a
    failed/disabled probe is REPORTED (`supervisor: "down"|"off"`) — degraded vocabulary is
    stated, never silently green."""
    row = get_channel(store, cid)
    sup_states: dict[str, str] = {}
    sup = "off"
    if probe_supervisor:
        sup = "down"
        try:
            import urllib.request
            with urllib.request.urlopen(SUPERVISOR_URL + "/sessions", timeout=0.8) as r:
                payload = json.loads(r.read().decode())
            for s in payload.get("sessions", []):
                key = s.get("claude_session_id") or s.get("id")
                if key:
                    sup_states[key] = s.get("state")
            sup = "up"
        except Exception:
            pass                                  # reported below as supervisor:"down" — loud in-band
    members = []
    for sid, m in row["members"].items():
        live = None
        if registry is not None:
            try:
                live = (registry(sid) or {}).get("state")
            except ValueError:
                live = None                       # unregistered — honestly unknown
        if live == "closed":
            status = "closed"
        elif sup_states.get(sid) == "busy":
            status = "busy"
        else:
            status = m["participation"]
        members.append({"session": _addr(sid), "declared": m["participation"],
                        "live_state": live, "supervisor_state": sup_states.get(sid),
                        "status": status})
    return {"channel": _chan_addr(row["id"]), "members": members,
            "supervisor": sup,
            "status_source": "declared+registry" + ("+supervisor" if sup == "up" else ""),
            "vocabulary": {"declared": list(PARTICIPATION), "derived": ["busy", "closed"]}}


# ── R2.2 — the channel's exchange (history: posts + the replies their threads gathered) ────────
def channel_history(store, cid: str, *, since: int = -1, limit: int = 50) -> dict:
    """The channel's own exchange, oldest-first: every channel.posted event (body resolved) joined
    with the mail its thread gathered (replies/errors/the conducted coordinator's traffic). This
    is the readable artifact seed (R12.1: 'what did they work out?' is answerable from the
    channel's own exchange). `since` = channel-event seq cursor; honest empty when nothing."""
    row = get_channel(store, cid)                 # fail-loud on unknown
    posts = [e for e in channel_events_since(store, since, channel=row["id"])
             if e.get("kind") == "channel.posted"][:limit]
    out = []
    for p in posts:
        body = store.get_content(p["cas"]) if p.get("cas") else None
        thread_mail = [
            {"seq": r["seq"], "from": r.get("from"), "to": r.get("to"), "verb": r.get("verb"),
             "ts": r.get("ts"), "channel_post": bool(r.get("channel_post"))}
            for r in store.agent_mail_since(-1, thread=p.get("thread"))]
        out.append({"seq": p["seq"], "ts": p.get("ts"), "from": p.get("from"),
                    "mode": p.get("mode"), "message": body, "thread": p.get("thread"),
                    "fan": p.get("fan"), "thread_traffic": thread_mail})
    return {"channel": _chan_addr(row["id"]), "name": row.get("name"), "posts": out,
            "next_since": (posts[-1]["seq"] if posts else since),
            "note": "thread_traffic is the LIVE join over the mail leaf — a conducted exchange "
                    "grows it as the coordinator works the members."}


# ── R2.4 — connection history: the edge fold (durable, recorded BY the talk itself) ────────────
def edges_for(store, session: str, *, limit: int = 100) -> dict:
    """Who has this session talked to? A read-time PROJECTION over the durable mail leaf — the
    talk IS the record (every session_post/reply/channel-fan landed there fsync'd), so edges are
    durable without a second write path (log-IS-the-index, the registry fold's own argument).
    Direction-aware (sent/received), verb-counted, channel-attributed (fan mail carries
    `channel`), and each edge carries the FOLLOW-UP HANDLE (R2.4's point: see who A talked to,
    then follow up to B from it): ready-to-pass session_post args joining the latest shared
    thread. Peers that are labels (a `from` like 'lead-x1' — accepted by the mail law as a reply
    path but not a session) are kept, marked addressable:false — honest edges, not dropped ones."""
    me = _addr(_bare(session))
    edges: dict[str, dict] = {}
    for r in store.agent_mail_since(-1):
        frm, to = r.get("from"), r.get("to")
        if me not in (frm, to):
            continue
        peer = to if frm == me else frm
        if not isinstance(peer, str) or not peer.strip() or peer == me:
            continue
        e = edges.get(peer)
        if e is None:
            e = edges[peer] = {"peer": peer,
                               "addressable": peer.startswith("session://"),
                               "first_ts": r.get("ts"), "last_ts": r.get("ts"),
                               "count": 0, "sent": 0, "received": 0, "verbs": {},
                               "threads": [], "via": {"direct": 0, "channels": {}}}
        e["count"] += 1
        e["last_ts"] = r.get("ts")
        e["sent" if frm == me else "received"] += 1
        v = r.get("verb") or "?"
        e["verbs"][v] = e["verbs"].get(v, 0) + 1
        t = r.get("thread")
        if t and t not in e["threads"]:
            e["threads"].append(t)
        ch = r.get("channel")
        if ch:
            e["via"]["channels"][ch] = e["via"]["channels"].get(ch, 0) + 1
        else:
            e["via"]["direct"] += 1
    rows = sorted(edges.values(), key=lambda e: e.get("last_ts") or "", reverse=True)[:limit]
    for e in rows:
        e["threads"] = e["threads"][-5:]
        if e["addressable"]:
            e["followup"] = {"tool": "session_post",
                             "args": {"to": e["peer"], "from_session": me,
                                      "thread": e["threads"][-1] if e["threads"] else None},
                             "note": "verb='auto' routes by the peer's live state; the thread "
                                     "joins your existing conversation with them."}
    return {"session": me, "edges": rows, "total": len(edges),
            "source": "agent_sessions/mail.jsonl (the durable talk itself — no second write path)"}
