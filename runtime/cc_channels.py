"""runtime/cc_channels.py — the Claude Code CHANNEL fabric core (cross-session messaging into LIVE
sessions). This is the registry + router behind the MCP tools; it is NOT the fabric's own
`channels`/gatherings concept (that's group membership) — this is the live-injection TRANSPORT.

A session launched with the channel (channels/company_channel.mjs via --dangerously-load-development-
channels) registers a file under .data/channels/<handle>.json: {handle, session_id, cwd, description,
pid, port, started}. This module:
  - live_sessions()        — every channel-session whose process is alive (presence + identity)
  - push(handle, content)  — inject a message into that session's live conversation (POST to its port)
  - record + route replies — the thread index maps a thread -> its originator so a reply is pushed
                             BACK into the asker's live session (no polling), and every message/reply
                             is appended to the channel mail log (the durable record).
The DESIGN (Tim, 2026-06-14): identity = cwd + self-announced description; replies go through the
mailbox AND are pushed into the right session (recipient never chooses to look); group = a fabric
channel whose members are live channel-sessions.
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAN_DIR = os.path.join(REPO, ".data", "channels")
MAIL_LOG = os.path.join(CHAN_DIR, "_mail.jsonl")        # durable record of every channel message/reply
THREADS = os.path.join(CHAN_DIR, "_threads.json")       # thread_id -> {originator_handle, topic, members}
CHANNELS_DIR = os.path.join(CHAN_DIR, "_channels")      # named-channel records: <channel-id>.json

# The supervisor base a supervised member is reached through when its registration omits the field
# (back-compat / fork-reg-missing-field). Mirrors cc_clone.SUPERVISOR — the one default both halves cite.
DEFAULT_SUPERVISOR_BASE = os.environ.get("COMPANY_SUPERVISOR_BASE", "http://127.0.0.1:8771")


class ChannelError(RuntimeError):
    """A channel op could not run — raised TEACHING-loud (never a silent no-op)."""


def _alive(pid: int) -> bool:
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError, TypeError):
        return False


def _read_reg(path: str):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _transport_of(reg: dict) -> str:
    """A member's transport (the unified per-member dispatch axis). BACK-COMPAT: a registration with
    no explicit `transport` (the original portful channel-session shape, or any reg carrying a `port`)
    is a "channel" member — the HTTP-POST-to-port transport that shipped first."""
    t = reg.get("transport")
    if t in ("channel", "supervised"):
        return t
    return "channel"


def supervisor_base(reg: dict) -> str:
    """The supervisor a supervised member is reached through: the reg's `supervisor_base`, else the
    process-wide default (COMPANY_SUPERVISOR_BASE / 127.0.0.1:8771 — the one the fork's cc_clone cites).
    Fail-loud only if neither resolves (a supervised reg must always reach SOME supervisor)."""
    base = (reg.get("supervisor_base") or DEFAULT_SUPERVISOR_BASE or "").rstrip("/")
    if not base:
        raise ChannelError(
            f"supervised member {reg.get('handle')!r} has no supervisor_base and "
            f"COMPANY_SUPERVISOR_BASE is unset — cannot reach its supervisor /inject.")
    return base


def _sup_sessions(base: str, *, timeout: float = 5) -> "tuple[bool, list]":
    """GET <base>/sessions. Returns (reachable, records). reachable=False means the supervisor could
    not be contacted (a TRANSIENT — e.g. mid-restart); the caller MUST NOT treat that as 'closed'
    (never delete a fork-owned supervised registration over a transient outage)."""
    req = urllib.request.Request(base.rstrip("/") + "/sessions", method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read() or b"{}")
        return True, data.get("sessions", []) or []
    except (urllib.error.URLError, OSError, ValueError):
        return False, []


def live_sessions() -> list:
    """Every live channel MEMBER (per-transport presence), newest first. A member is one registration
    file under CHAN_DIR. Transport-aware:
      - "channel"    (default / portful reg): alive = its pid is alive AND it has a port. A dead pid is
                     PRUNED (the file is removed — the original behaviour).
      - "supervised" (a clone/fork-owned reg): alive = the supervisor's /sessions shows its
                     supervisor_session in a non-closed state. PRUNED only when the supervisor is
                     REACHABLE and reports the session closed/absent — NEVER over a transient
                     unreachable supervisor (that would destroy a registration the fork owns).
    The _channels/ subdir (named-channel records) is skipped — it is `_`-prefixed."""
    out = []
    if not os.path.isdir(CHAN_DIR):
        return out
    # Group supervised members by supervisor_base so we GET /sessions ONCE per distinct supervisor.
    sup_regs: dict = {}        # base -> list[(path, reg)]
    sup_cache: dict = {}       # base -> (reachable, {non-closed supervisor_session ids})
    for fn in os.listdir(CHAN_DIR):
        if not fn.endswith(".json") or fn.startswith("_"):
            continue
        p = os.path.join(CHAN_DIR, fn)
        reg = _read_reg(p)
        if not reg:
            continue
        transport = _transport_of(reg)
        if transport == "supervised":
            try:
                base = supervisor_base(reg)
            except ChannelError:
                continue          # un-routable supervised reg — neither dispatch nor list it
            sup_regs.setdefault(base, []).append((p, reg))
            continue
        # channel transport (default): pid-alive + has a port (the original presence test)
        if "port" not in reg:
            continue
        if not _alive(reg.get("pid", -1)):
            try: os.unlink(p)          # prune the dead channel registration
            except OSError: pass
            continue
        out.append(reg)
    # supervised members: one /sessions probe per distinct supervisor base
    for base, items in sup_regs.items():
        if base not in sup_cache:
            reachable, recs = _sup_sessions(base)
            live_ids = {r.get("id") for r in recs if r.get("state") != "closed"}
            sup_cache[base] = (reachable, live_ids)
        reachable, live_ids = sup_cache[base]
        for p, reg in items:
            ss = reg.get("supervisor_session")
            if reachable and ss not in live_ids:
                try: os.unlink(p)      # supervisor REACHABLE + session closed/absent → prune
                except OSError: pass
                continue
            # reachable+live, OR unreachable (transient — keep, never destroy a fork-owned reg)
            out.append(reg)
    out.sort(key=lambda r: r.get("started", ""), reverse=True)
    return out


def find(target: str):
    """Resolve a target (handle, exact cwd, or substring of cwd/description) to ONE live session.
    Raises if none / ambiguous (fail loud — never push to the wrong session)."""
    live = live_sessions()
    if not live:
        raise ChannelError("no live channel-sessions — launch one with the channel "
                           "(--mcp-config .../channel.mcp.json --dangerously-load-development-channels "
                           "server:company-channel). cc_channels.live_sessions() lists them.")
    exact = [r for r in live if r.get("handle") == target or r.get("cwd") == target
             or r.get("session_id") == target]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        raise ChannelError(f"target {target!r} matches {len(exact)} live sessions — disambiguate by handle.")
    sub = [r for r in live if target and (target in (r.get("cwd") or "") or target in (r.get("description") or ""))]
    if len(sub) == 1:
        return sub[0]
    raise ChannelError(f"target {target!r} matched {len(sub)} live sessions (need exactly 1). "
                       f"Live: {[(r['handle'], r.get('cwd')) for r in live]}")


def push(handle_or_reg, content: str, *, meta: "dict | None" = None, base_timeout: float = 10) -> dict:
    """Inject `content` into a live channel MEMBER, dispatching on its TRANSPORT (the unified
    per-member transport — Tim-approved "notify-each"):
      - "channel"    — HTTP POST to the live session's local port (the original transport).
      - "supervised" — POST {session, message} to the member's supervisor /inject. Because a
                       supervised session runs the floor allowlist (mcp__company-only) it has no
                       channel `reply` tool of its own; so on FIRST dispatch we lazily start a
                       per-member /watch tail (the watcher IS the supervised member's missing reply
                       tool) that folds the supervisor's done-event into route_reply.
    `meta` keys become <channel ...> attributes. Returns {ok, handle, transport, ...}."""
    reg = handle_or_reg if isinstance(handle_or_reg, dict) else find(handle_or_reg)
    transport = _transport_of(reg)
    if transport == "supervised":
        return _push_supervised(reg, content, meta=meta or {}, base_timeout=base_timeout)
    port = reg["port"]
    body = json.dumps({"content": content, "meta": meta or {}}).encode()
    req = urllib.request.Request(f"http://127.0.0.1:{port}", data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=base_timeout) as resp:
            ok = resp.status == 200
    except (urllib.error.URLError, OSError) as e:
        raise ChannelError(f"push to {reg.get('handle')} (port {port}) failed: {e}. The session may "
                           f"have closed — live_sessions() reflects current presence.")
    return {"ok": ok, "handle": reg.get("handle"), "cwd": reg.get("cwd"), "port": port,
            "transport": "channel"}


# ---- supervised transport: dispatch via supervisor /inject + an async reply watcher (seam option B) ----
# A supervised member can't call a channel `reply` tool (it runs the mcp__company-only floor), so a
# daemon /watch tail per live supervised member folds its turn's done-event back into route_reply —
# synthesising the reply the member would otherwise have sent. The supervisor SERIALISES turns
# (idle⇄busy; /inject refused while busy), so per member a single pending-thread slot is exact: each
# done corresponds 1:1 to the most recent dispatch.
# The source tag the supervised /inject carries (the supervisor threads body `source` into inject(),
# which fans an `injected` event carrying it — session_supervisor do_POST /inject L1606 → inject L1091).
# The watcher uses this marker to ARM a fold ONLY for a turn THIS layer dispatched: a `done` is folded
# only when preceded, IN THE LIVE STREAM, by an `injected{source: CHANNEL_FABRIC_SOURCE}`. This makes
# the replayed-history case safe: /watch replays s.events on connect (session_supervisor L1485), so a
# supervised session a prior path (e.g. cc_clone.msg_clone) already drove carries a stale `done` in its
# replay — but that stale done is preceded only by a replayed injected with a DIFFERENT source (or
# none), never our marker, so it is correctly DISCARDED (never mis-routed to a pending thread).
CHANNEL_FABRIC_SOURCE = "channel-fabric"
_watchers: dict = {}                      # handle -> {"supervisor_session", "base"}
_pending_thread: dict = {}                # handle -> the channel thread the in-flight turn answers
_watch_lock = threading.Lock()


def _push_supervised(reg: dict, content: str, *, meta: dict, base_timeout: float = 10) -> dict:
    """Dispatch to a supervised member: ensure its reply-watcher is running (lazily, BEFORE injecting,
    so no prior replayed done is mis-routed), record which thread this turn answers, then POST
    /inject. The watcher pushes the member's reply back into the asker's session via route_reply."""
    handle = reg.get("handle")
    base = supervisor_base(reg)
    session = reg.get("supervisor_session")
    if not session:
        raise ChannelError(f"supervised member {handle!r} has no supervisor_session — cannot /inject "
                           f"(the fork's clone-registration must carry it; see the seam schema).")
    thread = (meta or {}).get("thread")
    # ensure the reply watcher FIRST (a lazy ensure on first dispatch: no prior done exists yet, so
    # the replay of s.events can't mis-route a stale done; serialisation gives 1:1 done↔pending after)
    _ensure_supervised_watcher(handle, base, session)
    with _watch_lock:
        _pending_thread[handle] = thread          # which channel thread THIS turn's reply routes to
    body = json.dumps({"session": session, "message": content,
                       "source": CHANNEL_FABRIC_SOURCE}).encode()
    req = urllib.request.Request(base + "/inject", data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=base_timeout) as resp:
            ok = resp.status == 200
    except (urllib.error.URLError, OSError) as e:
        with _watch_lock:
            _pending_thread.pop(handle, None)
        raise ChannelError(f"supervised inject to {handle!r} (session {session} @ {base}) failed: {e}. "
                           f"The supervisor may be down or the session closed — live_sessions() "
                           f"reflects current presence.")
    return {"ok": ok, "handle": handle, "cwd": reg.get("cwd"), "transport": "supervised",
            "supervisor_session": session, "supervisor_base": base, "thread": thread}


def _ensure_supervised_watcher(handle: str, base: str, session: str) -> None:
    """Start (once) a daemon /watch tail for a supervised member. Reaps itself when the supervisor
    fans the session's `closed` event or the watch stream ends, and deregisters so a later dispatch
    re-ensures a fresh watcher."""
    with _watch_lock:
        if handle in _watchers:
            return
        _watchers[handle] = {"base": base, "supervisor_session": session}
    t = threading.Thread(target=_supervised_watch_loop, args=(handle, base, session),
                         daemon=True, name=f"sup-watch-{handle}")
    t.start()


def _supervised_watch_loop(handle: str, base: str, session: str) -> None:
    """Tail <base>/watch?session=<id>; on each `done` event fold the member's reply into route_reply
    (using the thread recorded at dispatch). Exits on the supervisor's `closed` event or stream end —
    reaped + deregistered so the member can be re-watched on a future dispatch."""
    url = f"{base}/watch?session={session}"
    try:
        req = urllib.request.Request(url, method="GET")
        resp = urllib.request.urlopen(req, timeout=None)
    except (urllib.error.URLError, OSError):
        with _watch_lock:
            _watchers.pop(handle, None)
        return
    armed = False          # a fold is ARMED only by an `injected` marked with OUR source (this turn is
                           # ours). A `done` not preceded by our marker (a replayed-history done, or a
                           # turn another path drove) is DISCARDED — never folded to a pending thread.
    try:
        for raw in resp:
            try:
                ev = json.loads(raw)
            except ValueError:
                continue
            etype = ev.get("type")
            if etype == "injected" and ev.get("source") == CHANNEL_FABRIC_SOURCE:
                armed = True            # THIS layer's dispatch — the next done is ours to fold
            elif etype == "done":
                if not armed:
                    continue            # a replayed/foreign done — discard (never mis-route)
                armed = False
                with _watch_lock:
                    thread = _pending_thread.pop(handle, None)
                result = ev.get("result", "") or ""
                if thread and result:
                    try:
                        route_reply(handle, thread, result)
                    except ChannelError:
                        pass            # the asker may have closed; the reply is already in the mail log
            elif etype == "closed":
                break
    except (urllib.error.URLError, OSError, ValueError):
        pass
    finally:
        try: resp.close()
        except Exception: pass
        with _watch_lock:
            _watchers.pop(handle, None)
            _pending_thread.pop(handle, None)


# ---- the durable record + thread routing (the mailbox layer) ----
def _append_mail(rec: dict) -> None:
    os.makedirs(CHAN_DIR, exist_ok=True)
    rec = {"ts": rec.get("ts") or time.strftime("%Y-%m-%dT%H:%M:%S"), **rec}
    with open(MAIL_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def _load_threads() -> dict:
    return _read_reg(THREADS) or {}


def _save_threads(t: dict) -> None:
    os.makedirs(CHAN_DIR, exist_ok=True)
    tmp = THREADS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(t, f, indent=2)
    os.replace(tmp, THREADS)


def open_thread(thread: str, originator_handle: str, *, topic: str = "", members: "list | None" = None) -> None:
    """Record who started a thread (so replies route back) + optional group members."""
    t = _load_threads()
    t[thread] = {"originator": originator_handle, "topic": topic, "members": members or [], "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    _save_threads(t)


def thread_info(thread: str) -> dict:
    return _load_threads().get(thread, {})


def send(to: str, content: str, *, frm: str = "fabric", thread: str = "", topic: str = "") -> dict:
    """Send a message into a live session: record it + push it in. Opens the thread (origin=frm) so a
    reply routes back. Returns the push result + the thread id."""
    reg = find(to)
    thread = thread or f"t-{int(time.time())}-{reg['handle']}"
    open_thread(thread, frm, topic=topic)
    _append_mail({"kind": "message", "frm": frm, "to": reg["handle"], "to_cwd": reg.get("cwd"),
                  "thread": thread, "text": content})
    res = push(reg, content, meta={"from": frm, "thread": thread})
    res["thread"] = thread
    return res


def route_reply(from_handle: str, thread: str, text: str) -> dict:
    """A channel-session replied (its reply tool calls back here). Record it, then PUSH it back into
    the thread's originator's live session (no polling). If the originator is the fabric/an agent
    (not a live channel-session), it's recorded for the agent to read. Returns what happened."""
    _append_mail({"kind": "reply", "frm": from_handle, "thread": thread, "text": text})
    info = thread_info(thread)
    origin = info.get("originator")
    if not origin or origin == "fabric":
        return {"recorded": True, "delivered": False, "reason": "originator is the fabric/agent — read via mail log", "thread": thread}
    # push the reply back into the originator's live session
    try:
        push(origin, f"(reply from {from_handle}): {text}", meta={"from": from_handle, "thread": thread})
        return {"recorded": True, "delivered": True, "to": origin, "thread": thread}
    except ChannelError as e:
        return {"recorded": True, "delivered": False, "reason": str(e), "thread": thread}


def mail(thread: str = "", limit: int = 50) -> list:
    """Read the channel mail log (optionally one thread), newest last."""
    if not os.path.exists(MAIL_LOG):
        return []
    rows = []
    for line in open(MAIL_LOG, encoding="utf-8"):
        try: r = json.loads(line)
        except ValueError: continue
        if thread and r.get("thread") != thread:
            continue
        rows.append(r)
    return rows[-limit:]


# ---- the named-channel REGISTRY (channels as named managed groups) ----
# A CHANNEL is a named, managed group: a member-set (handles) + a purpose + a coordinator. It is a
# REGISTRY (create · list · add-member · remove-member · archive), distinct from the MEMBER
# registrations above: a member reg (CHAN_DIR/<handle>.json) carries liveness+transport; a channel
# record (CHANNELS_DIR/<channel-id>.json) carries membership. The two namespaces join on the handle —
# channel_members() reads the membership list; liveness for any member comes from find()/live_sessions().
# A member may belong to several channels at once. Fail-loud + teaching on every error (no silent no-op).

def _channel_id(name: str) -> str:
    """Slugify a channel name to its id (the record filename stem). A stable slug makes dup-name
    detection a file-exists check and keeps ids fs-safe."""
    slug = re.sub(r"[^a-z0-9]+", "-", (name or "").strip().lower()).strip("-")
    if not slug:
        raise ChannelError(f"channel name {name!r} has no usable characters — give it a real name "
                           f"(letters/digits), e.g. 'build-coordination'.")
    return slug


def _channel_path(channel: str) -> str:
    return os.path.join(CHANNELS_DIR, _channel_id(channel) + ".json")


def _read_channel(channel: str) -> "dict | None":
    return _read_reg(_channel_path(channel))


def _write_channel(rec: dict) -> None:
    os.makedirs(CHANNELS_DIR, exist_ok=True)
    p = os.path.join(CHANNELS_DIR, rec["id"] + ".json")
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
    os.replace(tmp, p)


def create_channel(name: str, purpose: str = "", coordinator: str = "") -> dict:
    """Create a named channel (a managed group). Fails loud if a channel with this name already
    exists (no silent overwrite). `coordinator` is an optional member handle that owns the channel."""
    if not (name or "").strip():
        raise ChannelError("create_channel needs a non-empty `name`.")
    cid = _channel_id(name)
    if os.path.exists(_channel_path(name)):
        raise ChannelError(f"channel {name!r} (id {cid!r}) already exists — list_channels() shows it. "
                           f"Pick a different name, or add_member/remove_member on the existing one.")
    rec = {"id": cid, "name": name.strip(), "purpose": purpose or "", "coordinator": coordinator or "",
           "members": [], "status": "active", "created": time.strftime("%Y-%m-%dT%H:%M:%S")}
    _write_channel(rec)
    return rec


def list_channels(*, include_archived: bool = False) -> list:
    """Every channel record, newest first. Archived channels are EXCLUDED by default (set
    include_archived=True to see them)."""
    out = []
    if not os.path.isdir(CHANNELS_DIR):
        return out
    for fn in sorted(os.listdir(CHANNELS_DIR)):
        if not fn.endswith(".json"):
            continue
        rec = _read_reg(os.path.join(CHANNELS_DIR, fn))
        if not rec:
            continue
        if rec.get("status") == "archived" and not include_archived:
            continue
        out.append(rec)
    out.sort(key=lambda r: r.get("created", ""), reverse=True)
    return out


def add_member(channel: str, handle: str) -> dict:
    """Add a member handle to a channel. Fails loud if the channel is missing or archived, or if the
    handle is already a member (no silent no-op). Does NOT require the member to be live — membership
    is a registry fact; liveness is resolved at push time via find()/live_sessions()."""
    rec = _read_channel(channel)
    if rec is None:
        raise ChannelError(f"no channel {channel!r} — create_channel({channel!r}, ...) first, or "
                           f"list_channels() to see the named channels.")
    if rec.get("status") == "archived":
        raise ChannelError(f"channel {rec['name']!r} is archived — cannot add members to an archived "
                           f"channel. Create a fresh channel for new coordination.")
    if not (handle or "").strip():
        raise ChannelError("add_member needs a non-empty `handle`.")
    handle = handle.strip()
    if handle in rec["members"]:
        raise ChannelError(f"{handle!r} is already a member of {rec['name']!r} — channel_members "
                           f"({channel!r}) shows the roster.")
    rec["members"].append(handle)
    _write_channel(rec)
    return rec


def remove_member(channel: str, handle: str) -> dict:
    """Remove a member handle from a channel. Fails loud if the channel is missing or the handle is
    not a member (no silent no-op)."""
    rec = _read_channel(channel)
    if rec is None:
        raise ChannelError(f"no channel {channel!r} — list_channels() shows the named channels.")
    if handle not in rec["members"]:
        raise ChannelError(f"{handle!r} is not a member of {rec['name']!r} — channel_members"
                           f"({channel!r}) shows the current roster.")
    rec["members"].remove(handle)
    _write_channel(rec)
    return rec


def archive_channel(channel: str) -> dict:
    """Archive a channel: mark it archived (status field — NOT a delete; the record + roster survive
    for the record). Fails loud if the channel is missing or already archived."""
    rec = _read_channel(channel)
    if rec is None:
        raise ChannelError(f"no channel {channel!r} — list_channels() shows the named channels.")
    if rec.get("status") == "archived":
        raise ChannelError(f"channel {rec['name']!r} is already archived.")
    rec["status"] = "archived"
    rec["archived"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    _write_channel(rec)
    return rec


def channel_members(channel: str) -> list:
    """The member handles of a channel (the roster — membership facts, NOT liveness). Fails loud if
    the channel is missing. Resolve liveness per handle via find()/live_sessions()."""
    rec = _read_channel(channel)
    if rec is None:
        raise ChannelError(f"no channel {channel!r} — list_channels() shows the named channels.")
    return list(rec.get("members", []))
