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
    "channel.member_added",   # {channel, session, participation, member_kind?, label?}
    "channel.member_removed", # {channel, session}
    "channel.member_status",  # {channel, session, participation}
    "channel.posted",         # {channel, from, cas, thread, mode, fan:[{session, verb, mail_seq}], coordinator?, reply_to?}
    "channel.mode_set",       # {channel, mode, coordinator?}
    "channel.shared_set",     # {channel, shared}  — the shared-edge flag (publish-to-Supabase gate)
    "channel.reaction_added", # {channel, message, member, emoji}  — a reaction event on a message (fusion inc.3)
    "channel.reaction_removed", # {channel, message, member, emoji}  — un-react (set semantics)
    "channel.archived",       # {channel}
    "gathering.dispersed",    # {channel}   — terminal for kind=gathering
    "gathering.promoted",     # {channel, promoted_to}  — gathering → durable channel
)
KINDS = ("channel", "gathering")
MODES = ("direct", "conducted")                  # R2.5: router vs conductor
PARTICIPATION = ("awake", "listening")           # the DECLARED member posture (R2.2 vocabulary);
                                                 # busy/closed are DERIVED (registry + supervisor), never stored
# MEMBER_KINDS (fusion inc.3 — the "label slot" inc.2 deferred): a member is no longer assumed to be
# a live agent session. A room member can be a HUMAN (the operator on the OWUI face), a LIVE-SESSION
# (a Claude Code session reached via cc_channels inject — the original assumption), or a MODEL (an AI
# brain that is a first-class room member, e.g. the OWUI operator/RHM model). kind discriminates HOW a
# member is present; it is a member SUB-RECORD field (+ an optional display `label`), never a new row.
MEMBER_KINDS = ("human", "live-session", "model")
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
                                       "kind": m.get("kind", "live-session"),
                                       "label": m.get("label"),
                                       "added": e.get("ts")}
                        for m in (e.get("members") or [])},
            "origin": e.get("origin"), "created": e.get("ts"),
            "last_activity": e.get("ts"), "posts": 0, "seq": e.get("seq"),
            "shared": bool(e.get("shared")),   # the shared-edge flag (default INTERNAL; publish-gate)
            "reactions": {},   # {message_ref → {emoji → [member, …]}} — folded from reaction events (inc.3)
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
                                        "kind": e.get("member_kind", "live-session"),
                                        "label": e.get("label"),
                                        "added": e.get("ts")}
    elif k == "channel.member_removed":
        row["members"].pop(e.get("session"), None)
    elif k == "channel.member_status":
        m = row["members"].get(e.get("session"))
        if m is not None:
            m["participation"] = e.get("participation")
    elif k == "channel.posted":
        row["posts"] = row.get("posts", 0) + 1
    elif k == "channel.reaction_added":
        # SET semantics: a (message, emoji, member) is present at most once (re-react is idempotent).
        reacts = row.setdefault("reactions", {})
        msg = str(e.get("message"))
        per_emoji = reacts.setdefault(msg, {}).setdefault(e.get("emoji"), [])
        if e.get("member") not in per_emoji:
            per_emoji.append(e.get("member"))
    elif k == "channel.reaction_removed":
        reacts = row.setdefault("reactions", {})
        msg = str(e.get("message"))
        per_emoji = reacts.get(msg, {}).get(e.get("emoji"))
        if per_emoji and e.get("member") in per_emoji:
            per_emoji.remove(e.get("member"))
            if not per_emoji:                    # last reactor of this emoji left → drop the emoji bucket
                reacts[msg].pop(e.get("emoji"), None)
                if not reacts[msg]:              # no emojis left on the message → drop the message bucket
                    reacts.pop(msg, None)
    elif k == "channel.mode_set":
        row["mode"] = e.get("mode")
        if e.get("coordinator") is not None:
            row["coordinator"] = e.get("coordinator")
    elif k == "channel.shared_set":
        row["shared"] = bool(e.get("shared"))
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
                   cid: str | None = None, shared: bool = False,
                   registry=None) -> dict:
    """Mint a channel (R2.2) or gathering (R2.3 — same primitive, kind discriminates: universal
    composition, one relational mechanism reused). `members` = [{session, participation?}…];
    each session is validated against the agent-session registry when a `registry` lookup is
    supplied (fail-loud on unknown ids — never a roster of fabrications); pass registry=None only
    where no registry exists (isolated tests). mode="conducted" requires a coordinator who IS a
    member (a conductor outside the room cannot hold its purpose). `origin` records provenance
    ({"parent": "channel://…"} for a sub-channel — the R2.5 recursion; {"promoted_from": …} is
    stamped by promote_gathering).

    `cid` (optional explicit id): when None, the id is MINTED sequentially (ch-N / ga-N — the
    fabric's own channels). When supplied (a slug, e.g. "design"/"fabric"), it is used VERBATIM —
    this is the named-channel surface (formerly cc_channels' second store, now folded here): a
    stable human slug, dup-detected fail-loud (an existing id refuses, no silent overwrite). Ids are
    thus heterogeneous BY HISTORY — minted ch-N alongside migrated/named slugs; get_channel resolves
    both (one store, mixed-id). `shared` (default False = INTERNAL): the shared-edge flag — only a
    shared=True channel publishes posts OUT to the Supabase channel_boundary (the single-source gate).
    Returns the folded row."""
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
        mkind = (m.get("kind", "live-session") if isinstance(m, dict) else "live-session")
        if mkind not in MEMBER_KINDS:
            raise ValueError(
                f"create_channel: unknown member kind {mkind!r} for {sid} — a member is one of "
                f"{list(MEMBER_KINDS)} (human = a person on a face · live-session = a Claude Code "
                f"session reached via inject · model = an AI brain that is a first-class member).")
        mlabel = (m.get("label") if isinstance(m, dict) else None)
        # registry validation is for LIVE-SESSION members only — a human/model member is not an
        # agent session and must NOT be looked up (it would fail-loud on an id that isn't a session).
        if registry is not None and mkind == "live-session":
            registry(sid)                        # fail-loud teaching error on unknown (the registry's own)
        if sid not in seen:
            norm.append({"session": sid, "participation": part, "kind": mkind, "label": mlabel})
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
    want = _chan_bare(cid) if cid else None      # an explicit id (a named-channel slug), used verbatim
    if want is not None and not want:
        raise ValueError("create_channel: explicit `cid` is empty after normalization — give a real "
                         "slug (e.g. 'design') or pass cid=None to mint a sequential id.")
    # id mint rides the same lock as the append (seq-unique), via a created-event carrying members inline
    # (a gathering is GRABBED in one gesture — one event, not N+1). An explicit id is dup-detected
    # fail-loud under the SAME lock (no silent overwrite — the named-channel store's contract).
    with store.graph_lock(LOCK_KEY + ":mint"):
        existing = fold_channels(store)
        if want is not None:
            if want in existing:
                raise ValueError(
                    f"create_channel: channel {want!r} already exists — it is on the channels leaf "
                    f"(channels(op='list') / fold_channels shows it). Pick a different id, or "
                    f"add_member/set_shared on the existing one. Fail loud, never silent overwrite.")
            new_cid = want
        else:
            n = sum(1 for r in existing.values() if r["kind"] == kind)
            new_cid = f"{prefix}-{n}"
            while new_cid in existing:           # archive/promote never frees an id; scan past collisions
                n += 1
                new_cid = f"{prefix}-{n}"
        append_channel_event(store, {
            "kind": "channel.created", "channel": new_cid, "channel_kind": kind,
            "name": name.strip(), "purpose": purpose or "", "mode": mode,
            "coordinator": coord, "members": norm, "origin": origin,
            "shared": bool(shared)})
    row = get_channel(store, new_cid)
    # THE DOOR (Tim 2026-06-29): the creator receives the channel-create CARD at the mechanical moment
    # itself — resolved live (never baked), telling them to seed the channel's own door rows. Fail-soft:
    # the card is knowledge, not the op; its failure must never fail the create.
    try:
        from runtime.door import compose_card
        from runtime.session_scan import resolve_self_member
        row["card"] = compose_card(resolve_self_member() or {}, moment="channel-create",
                                   channel=row.get("name") or new_cid)
    except Exception:  # noqa: BLE001
        pass
    return row


def add_member(store, cid: str, session: str, *, participation: str = "awake",
               kind: str = "live-session", label: str | None = None,
               registry=None) -> dict:
    """Fluid membership, the add half (R2.2). `kind` (MEMBER_KINDS, inc.3): human | live-session |
    model — HOW the member is present (a person on a face · a session reached via inject · an AI
    brain). `label` is an optional display identity (the inc.2-deferred label slot). Validated
    against the agent-session registry when supplied AND kind == 'live-session' (only a session is a
    registry id; a human/model member is not). Adding an existing member is refused loud (use
    set_member_status to change posture — a silent re-add would silently reset their declared
    posture/kind)."""
    if participation not in PARTICIPATION:
        raise ValueError(f"add_member: unknown participation {participation!r} — declared postures "
                         f"are {list(PARTICIPATION)}.")
    if kind not in MEMBER_KINDS:
        raise ValueError(f"add_member: unknown member kind {kind!r} — a member is one of "
                         f"{list(MEMBER_KINDS)} (human · live-session · model).")
    row = get_channel(store, cid)
    _require_active(row, "add_member")
    sid = _bare(session)
    if sid in row["members"]:
        raise ValueError(
            f"add_member: {_addr(sid)} is already a member of channel://{row['id']} — to change "
            f"its posture use set_member_status; membership is a set, not a multiset.")
    if registry is not None and kind == "live-session":
        registry(sid)
    append_channel_event(store, {"kind": "channel.member_added", "channel": row["id"],
                                 "session": sid, "participation": participation,
                                 "member_kind": kind, "label": label})
    row2 = get_channel(store, cid)
    # THE DOOR: the joiner's channel-join CARD rides the op result (the mechanical moment). The card is
    # for the JOINED member (their identity when resolvable via the sid), scoped to this channel —
    # default rows + the channel's own modification rows. Fail-soft: knowledge never fails the op.
    try:
        from runtime.door import compose_card
        row2["card"] = compose_card({"handle": sid, "name": (label or "")}, moment="channel-join",
                                    channel=row2.get("name") or cid)
    except Exception:  # noqa: BLE001
        pass
    return row2


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


# ── reactions as a CHANNEL PRIMITIVE (fusion inc.3) ─────────────────────────────────────────────
# A reaction is a {message, member, emoji} EVENT on the channel — first-class, not an ad-hoc handler
# in the owui_room daemon. `message` is an OPAQUE STRING ref into whatever id-space the caller owns:
# session_channels callers pass str(post_seq) (the channel.posted seq); the owui_room face passes the
# OWUI message id. The primitive is id-agnostic — it never resolves the ref, so two faces' id-spaces
# coexist on one store. The fold (row["reactions"]) projects {message → {emoji → [member, …]}} with SET
# semantics. owui_room's 🛑/⏸ reaction-CONTROL records here, then acts (record-then-act, never gate-act).
def react(store, cid: str, message: str, member: str, emoji: str) -> dict:
    """Add a reaction (one member, one emoji, on one message ref). Idempotent (set semantics — a
    repeat re-react is a no-op in the fold). Fail-loud on an inactive channel or empty inputs; the
    message ref is NOT validated (id-agnostic by design — see the block comment). Returns the row."""
    if not isinstance(message, str) or not message.strip():
        raise ValueError("react: `message` must be a non-empty message ref (the post seq, or the "
                         "face's own message id) — a reaction with no target is unfoldable.")
    if not isinstance(member, str) or not member.strip():
        raise ValueError("react: `member` is required — who reacted (a handle/session/label).")
    if not isinstance(emoji, str) or not emoji.strip():
        raise ValueError("react: `emoji` is required — the reaction (an emoji char or shortcode).")
    row = get_channel(store, cid)
    _require_active(row, "react")
    append_channel_event(store, {"kind": "channel.reaction_added", "channel": row["id"],
                                 "message": message.strip(), "member": member.strip(),
                                 "emoji": emoji.strip()})
    return get_channel(store, cid)


def unreact(store, cid: str, message: str, member: str, emoji: str) -> dict:
    """Remove a reaction (the un-react half — set semantics, removing an absent reaction is a fold
    no-op, never an error: the caller's intent ['this member is no longer reacting'] is satisfied
    either way). Fail-loud only on an inactive channel or empty inputs."""
    if not (isinstance(message, str) and message.strip() and isinstance(member, str)
            and member.strip() and isinstance(emoji, str) and emoji.strip()):
        raise ValueError("unreact: `message`, `member`, `emoji` are all required.")
    row = get_channel(store, cid)
    _require_active(row, "unreact")
    append_channel_event(store, {"kind": "channel.reaction_removed", "channel": row["id"],
                                 "message": message.strip(), "member": member.strip(),
                                 "emoji": emoji.strip()})
    return get_channel(store, cid)


def reactions_for(store, cid: str, message: str | None = None) -> dict:
    """The folded reactions view: {message_ref → {emoji → [member, …]}} for the whole channel, or
    {emoji → [member, …]} for one `message`. Fail-loud on an unknown channel; honest empty dict
    when nothing has been reacted to."""
    row = get_channel(store, cid)
    reacts = row.get("reactions") or {}
    if message is not None:
        return {"channel": _chan_addr(row["id"]), "message": str(message),
                "reactions": reacts.get(str(message), {})}
    return {"channel": _chan_addr(row["id"]), "reactions": reacts}


# ── the shared-edge flag + the named-channel roster read (the cc_channels-store fold-in) ─────────
# These complete the one-store fold: cc_channels' named-store is_shared/channel_members are now thin
# delegations to THESE (one channel concept — structure here, transport in cc_channels).
def is_shared(store, cid: str) -> bool:
    """True iff `cid` is a SHARED channel (publish-eligible: its posts route OUT to the Supabase
    channel_boundary). Fail-CLOSED: an absent channel ⇒ False (INTERNAL — never publishes out). The
    publish hook's gate (channel_boundary_run.post_to_channel routes outward ONLY when this is True)."""
    try:
        return bool(get_channel(store, cid).get("shared"))
    except ValueError:
        return False                             # absent ⇒ internal (fail-closed), never raise the gate


def set_shared(store, cid: str, shared: bool = True) -> dict:
    """Set the shared-edge flag on an existing channel (idempotent re-set is allowed — a flag, not a
    member). Used by ensure_design_channel's upgrade branch (an INTERNAL channel promoted to SHARED)."""
    row = get_channel(store, cid)
    _require_active(row, "set_shared")
    append_channel_event(store, {"kind": "channel.shared_set", "channel": row["id"],
                                 "shared": bool(shared)})
    return get_channel(store, cid)


def channel_members(store, cid: str) -> list[str]:
    """The member handles of a channel as a FLAT LIST (the named-channel roster — membership facts,
    NOT liveness; resolve liveness via cc_channels.find/live_sessions). Fail-loud on an unknown
    channel. This is the read channel_boundary_run.members_of rides: sc stores members as a
    {sid→{participation}} dict; this returns sorted(keys) — the handle list its inject loop fans over."""
    return sorted(get_channel(store, cid).get("members", {}).keys())


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
def _post_event(store, cid: str, seq: int) -> dict | None:
    """The channel.posted event with this seq on `cid`, or None (id-agnostic lookup for reply_to
    root-resolution). Used to collapse reply-of-reply to the root (single-level threads, OWUI-style)."""
    for e in channel_events_since(store, -1, channel=cid):
        if e.get("kind") == "channel.posted" and e.get("seq") == seq:
            return e
    return None


def _publish_shared_best_effort(store, cid: str, frm: str, message: str, thread: str) -> "dict | None":
    """Complete the channel_boundary orphan: if channel `cid` is `shared`, publish THIS post outward to
    Supabase channel_posts (so an external face — Claude-Design — sees the same channel, single-source).
    NEVER raises and NEVER blocks the internal fan. Returns None for a non-shared channel.

    DORMANT-SAFE: only attempts the outbound write when the boundary principal's creds are already in the
    process env (COMPANY_CHANNEL_*). It deliberately does NOT auto-load .boundary.env — so a test/local
    post to a shared channel never makes a surprise outbound write. A serving process activates the
    publish by loading .boundary.env at startup (the receive half — the Realtime subscriber — is a
    separate service to register). Any missing-cred/offline/FK failure → {ok:False,...}, fan unaffected."""
    import os
    try:
        if not is_shared(store, cid):
            return None
    except Exception:
        return None
    if not os.environ.get("COMPANY_CHANNEL_SA_EMAIL"):
        return {"ok": False, "dormant": True,
                "reason": "shared channel, but boundary creds (COMPANY_CHANNEL_*) are not loaded in this "
                          "process — load .boundary.env at service startup to enable outward publish."}
    try:
        from runtime.channel_boundary import build_post_row, publish_shared_post
        from runtime.supabase_principal import SupabasePrincipal
        principal = SupabasePrincipal("COMPANY_CHANNEL")
        row = build_post_row(cid, frm, message, thread=thread, sender_kind="session")
        return publish_shared_post(row, principal=principal)
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def post_to_channel(store, cid: str, message: str, from_: str, *,
                    registry=None, thread: str | None = None,
                    reply_to: int | None = None) -> dict:
    """Message the channel — the ONE write that makes a channel a live thing rather than a list.

    THREADS (fusion inc.3, OWUI-style single-level): `reply_to` = the seq of the post being replied
    to (a channel.posted seq, from a prior post's `posted` return). A reply is a normal post that ALSO
    carries `reply_to` (the hierarchy axis — OWUI's parent_id) AND joins the parent's aggregation
    `thread` (the conversation axis — OWUI's reply_to_id continuity) automatically. Single-level: a
    reply to a reply collapses to the thread ROOT (no nesting — fusion §2 accepts this for v1). The
    fold's channel_history exposes a post's replies via reply_to; reactions key on the same seq.

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

    # THREADS (inc.3): a reply (reply_to set) inherits the PARENT's aggregation thread so the reply
    # lands in the same conversation. Single-level — if the parent is ITSELF a reply, collapse to the
    # root (the parent's reply_to), so no nesting accrues. reply_to is validated to be a real post on
    # THIS channel (fail-loud — a reply to a phantom post is a dangling hierarchy edge).
    root_reply_to = None
    if reply_to is not None:
        parent = _post_event(store, row["id"], int(reply_to))
        if parent is None:
            raise ValueError(
                f"post_to_channel: reply_to={reply_to} is not a post on channel://{row['id']} — "
                f"reply to a real post seq (channels(op='history') lists them). No dangling replies.")
        # single-level collapse: the hierarchy parent is the parent's OWN root if it had one, else the parent
        root_reply_to = parent.get("reply_to") if parent.get("reply_to") is not None else int(reply_to)
        if thread is None:                       # inherit the parent's conversation key (unless caller forced one)
            thread = parent.get("thread")

    # ONE shared thread per post, PRE-minted (append_agent_mail honours caller threads) so every
    # fan record — and the conducted body's own work-instructions — carry the same aggregation key
    # from birth. Joining an existing conversation = pass `thread`.
    import uuid as _uuid
    mail_thread = (thread.strip() if isinstance(thread, str) and thread.strip()
                   else f"chan-{row['id']}-{_uuid.uuid4().hex[:8]}")
    # the weld: index the LIVE .mjs channel members ONCE per post — FAST (pid-pruned regs + fast uuid
    # rungs only; NO supervisor probe, NO transcript scan on this hot path). A member reachable via its
    # own .mjs port is then live-pushed in the loop below. reconcile_registry() backfills empty regs so
    # they appear here by durable uuid; a single-target send() uses the deeper resolve. (Lazy import —
    # no top-level cycle: identity/cc_channels never import this module.)
    from runtime import identity as _identity
    from runtime import cc_channels as _cc
    _identity.maybe_reconcile()          # throttled self-heal: backfill empty regs so members resolve by uuid
    _chan_index = {}
    try:
        for _reg in _cc.live_sessions():
            if _cc._transport_of(_reg) != "channel":
                continue
            _u, _ = _identity.recover_uuid(_reg)          # deep=False (fast rungs only)
            for _k in (_u, _reg.get("handle")):
                if _k:
                    _chan_index.setdefault(_k, _reg)
    except Exception:
        _chan_index = {}
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
        # ── THE WELD (map G7): route each member by PRESENCE, not by supervisor-ownership. A
        # supervised-live member keeps its deliver-intent (the supervisor injects it — unchanged,
        # proven path). A member reachable RIGHT NOW via its own live .mjs port is LIVE-PUSHED here
        # and now (the transport a durable post never chose before — the exact "it shouldn't matter
        # if the supervisor owns them" fix). Everyone else queues. The mail record is written
        # REGARDLESS as the durable/inbox backstop (the .mjs push carries no ACK — a queued copy is
        # the honest backstop, map G14). The fan carries the TRUE transport + a delivered flag per
        # member — no phantom-OK (map G15/G16).
        transport, delivered = None, None
        if st == "supervised-live":
            verb, transport, delivered = "deliver", "supervised", True   # supervisor injects the intent
        else:
            verb = "queue"                                               # durable/inbox copy; supervisor skips queue
            _reg = _chan_index.get(sid)                                  # a live .mjs member (by uuid or handle)?
            if _reg is not None:
                try:
                    r = _cc.push(_reg, message, meta={"from": from_.strip(),
                                 "thread": mail_thread, "channel": row.get("name") or ""})
                    delivered = bool(r.get("ok"))
                except _cc.ChannelError:
                    delivered = False
                transport = "channel" if delivered else "queue"
            else:
                transport, delivered = "queue", False
        cas = store.put_content(body)
        out = store.append_agent_mail({
            "to": _addr(sid), "from": from_.strip(), "verb": verb, "cas": cas,
            "thread": mail_thread, "channel": _chan_addr(row["id"]), "channel_post": True,
            "transport": transport, "delivered": delivered,
            "state_at_post": st, "source": "session_channels.post_to_channel"})
        fan.append({"session": _addr(sid), "verb": verb, "transport": transport,
                    "delivered": delivered, "mail_seq": out["seq"]})
    ev = append_channel_event(store, {
        "kind": "channel.posted", "channel": row["id"], "from": from_.strip(),
        "cas": store.put_content(message), "thread": mail_thread, "mode": mode,
        "coordinator": row.get("coordinator") if mode == "conducted" else None, "fan": fan,
        "reply_to": root_reply_to})
    # shared channel → ALSO publish outward (completes the channel_boundary orphan; fail-soft, dormant
    # without boundary creds — never breaks the internal fan). None for a non-shared channel.
    shared_publish = _publish_shared_best_effort(store, row["id"], from_.strip(), message, mail_thread)
    return {"posted": ev["seq"], "channel": _chan_addr(row["id"]), "mode": mode,
            "thread": mail_thread, "fan": fan, "reply_to": root_reply_to,
            "shared_publish": shared_publish,
            "what_happens": ("the coordinator session receives the channel context + your message "
                             "as one intent and works the members (watch the thread)"
                             if mode == "conducted" else
                             "every reachable member is LIVE-injected now — supervised via the "
                             "supervisor, hand-started via its own .mjs port; the rest are queued for "
                             "next-turn pull. The fan names the true transport + delivered per member "
                             "(no phantom-OK)."),
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
        mkind = m.get("kind", "live-session")
        live = None
        # registry/supervisor liveness is a LIVE-SESSION property only — a human/model member is not
        # an agent session, so its derived state is never "closed/busy"; its declared posture stands.
        if mkind == "live-session":
            if registry is not None:
                try:
                    live = (registry(sid) or {}).get("state")
                except ValueError:
                    live = None                   # unregistered — honestly unknown
            if live == "closed":
                status = "closed"
            elif sup_states.get(sid) == "busy":
                status = "busy"
            else:
                status = m["participation"]
        else:
            status = m["participation"]
        members.append({"session": _addr(sid), "kind": mkind, "label": m.get("label"),
                        "declared": m["participation"],
                        "live_state": live, "supervisor_state": sup_states.get(sid),
                        "status": status})
    return {"channel": _chan_addr(row["id"]), "members": members,
            "supervisor": sup,
            "status_source": "declared+registry" + ("+supervisor" if sup == "up" else ""),
            "vocabulary": {"declared": list(PARTICIPATION), "derived": ["busy", "closed"],
                           "member_kinds": list(MEMBER_KINDS)}}


# ── R2.2 — the channel's exchange (history: posts + the replies their threads gathered) ────────
def channel_history(store, cid: str, *, since: int = -1, limit: int = 50) -> dict:
    """The channel's own exchange, oldest-first: every channel.posted event (body resolved) joined
    with the mail its thread gathered (replies/errors/the conducted coordinator's traffic). This
    is the readable artifact seed (R12.1: 'what did they work out?' is answerable from the
    channel's own exchange). `since` = channel-event seq cursor; honest empty when nothing.

    THREADS + REACTIONS (inc.3): each post carries `reply_to` (the parent post seq it replies to,
    None for a root post) and `replies` (the seqs of posts that reply TO it — the single-level
    thread view) and `reactions` ({emoji → [member, …]} keyed on the post seq). A reader rebuilds
    the OWUI-style threaded room from this one fold."""
    row = get_channel(store, cid)                 # fail-loud on unknown
    all_posts = [e for e in channel_events_since(store, -1, channel=row["id"])
                 if e.get("kind") == "channel.posted"]
    # map parent-seq → [child-seq, …] across ALL posts (so the replies view is complete even when
    # the window starts after the parent), and pull the folded reactions for keying per post.
    replies_of: dict[int, list[int]] = {}
    for e in all_posts:
        rt = e.get("reply_to")
        if rt is not None:
            replies_of.setdefault(int(rt), []).append(e.get("seq"))
    reacts = row.get("reactions") or {}
    posts = [e for e in all_posts if e.get("seq", -1) > since][:limit]
    out = []
    for p in posts:
        body = store.get_content(p["cas"]) if p.get("cas") else None
        thread_mail = [
            {"seq": r["seq"], "from": r.get("from"), "to": r.get("to"), "verb": r.get("verb"),
             "ts": r.get("ts"), "channel_post": bool(r.get("channel_post"))}
            for r in store.agent_mail_since(-1, thread=p.get("thread"))]
        out.append({"seq": p["seq"], "ts": p.get("ts"), "from": p.get("from"),
                    "mode": p.get("mode"), "message": body, "thread": p.get("thread"),
                    "fan": p.get("fan"), "thread_traffic": thread_mail,
                    "reply_to": p.get("reply_to"),
                    "replies": replies_of.get(p.get("seq"), []),
                    "reactions": reacts.get(str(p.get("seq")), {})})
    return {"channel": _chan_addr(row["id"]), "name": row.get("name"), "posts": out,
            "next_since": (posts[-1]["seq"] if posts else since),
            "note": "thread_traffic is the LIVE join over the mail leaf — a conducted exchange "
                    "grows it as the coordinator works the members. reply_to/replies are the "
                    "single-level thread tree; reactions are keyed on the post seq."}


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


def channels_for_self(store) -> dict:
    """P2 (operator-surface) — the SELF→CHANNEL-MEMBERSHIP join (Tim: search/inbox default to the
    caller's own channel). Resolves WHO I AM (the fabric registration, via the claude-ancestor PID —
    session_scan.resolve_self_member) and folds WHICH channels carry me as a member (this module's ONE
    membership store — the fold rows' members are keyed by sid). Returns
        {handle, name, session_id, channels: [{id, name, kind, mode, participation}, ...]}
    channels=[] honestly when the session is registered but joined nowhere. FAIL-LOUD when self does not
    resolve (register first: cc_channels.register_self) — a scoping default must never guess who's asking."""
    from runtime.session_scan import resolve_self_member   # lazy — session_scan imports nothing from here
    me = resolve_self_member()
    if not me or not me.get("handle"):
        raise ValueError(
            "channels_for_self: SELF does not resolve — this session has no fabric registration. "
            "Join first: cc_channels.register_self(). Fail loud (a scope default never guesses the caller).")
    sid = me.get("session_id") or ""
    out = []
    if sid:
        for cid, row in fold_channels(store).items():
            m = (row.get("members") or {}).get(sid)
            if m is not None and row.get("status") != "archived":
                out.append({"id": cid, "name": row.get("name", ""), "kind": row.get("kind", "channel"),
                            "mode": row.get("mode", ""), "participation": (m or {}).get("participation", "")})
    return {"handle": me["handle"], "name": me.get("name", ""), "session_id": sid,
            "channels": sorted(out, key=lambda r: r["id"])}
