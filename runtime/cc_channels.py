"""runtime/cc_channels.py — the channel TRANSPORT layer (cross-session messaging into LIVE sessions).

ONE channel concept, TWO layers — this module is the TRANSPORT half:
  • STRUCTURE (what a channel IS — name/purpose/roster/mode/shared/lifecycle): runtime/session_channels.py
    (the ONE named-channel store, channels.jsonl), reached via the `channels`/`channel_act` MCP tools.
  • TRANSPORT (reach a live member NOW — discover/push/reply-back): THIS module, the `cc_channel` MCP tool.
This module does NOT hold a named-channel store (a second store lived here until 2026-06-29; it was folded
into session_channels and retired — see the retirement note further down). It is the live-injection router.

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
import threading
import time
import urllib.error
import urllib.request
import uuid

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAN_DIR = os.path.join(REPO, ".data", "channels")
MAIL_LOG = os.path.join(CHAN_DIR, "_mail.jsonl")        # durable record of every channel message/reply
THREADS = os.path.join(CHAN_DIR, "_threads.json")       # thread_id -> {originator_handle, topic, members}
# NOTE: the named-channel STORE (formerly .data/channels/_channels/) was folded into session_channels
# (channels.jsonl) and RETIRED 2026-06-29 — this module is TRANSPORT only. See the retirement note below.

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


def _proc_state(pid: int):
    """The process state char from /proc/<pid>/stat, or None if the pid is dead. 'R'/'S'/'D' = live,
    'T'/'t' = STOPPED (suspended — Ctrl-Z / SIGSTOP; cannot consume an injected message), 'Z' = zombie."""
    try:
        with open(f"/proc/{int(pid)}/stat") as f:
            data = f.read()
        # state is the field right after the (comm) paren group — comm may contain spaces/parens
        return data[data.rindex(")") + 2]
    except (OSError, ValueError, TypeError):
        return None


def _channel_presence(reg: dict) -> str:
    """TRUE reachability of a channel-transport member: 'live' | 'suspended' | 'dead'. Presence means the
    message can actually be DELIVERED — which needs BOTH the node channel-server (reg['pid']) alive AND the
    Claude session it feeds (reg['claude_pid']) alive-and-not-stopped. The old test checked only reg['pid']
    (the node helper) and treated os.kill(pid,0) as alive, so an ORPHANED server (Claude gone) or a SUSPENDED
    session (state T) both falsely read as live and then timed out on send. claude_pid is honoured when
    present; older regs without it fall back to the node-pid test (unchanged)."""
    if not _alive(reg.get("pid", -1)):
        return "dead"                                    # node channel-server gone
    cpid = reg.get("claude_pid")
    if cpid in (None, "", -1):
        return "live"                                    # older reg: no claude_pid recorded → node-pid test only
    st = _proc_state(cpid)
    if st is None:
        return "dead"                                    # the Claude session is gone → this server is orphaned
    if st in ("T", "t"):
        return "suspended"                               # session paused (Ctrl-Z) — can't consume, but may resume
    return "live"


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
        # channel transport (default): reachable = node-server alive AND Claude session alive-and-not-stopped
        if "port" not in reg:
            continue
        presence = _channel_presence(reg)
        if presence == "dead":
            try: os.unlink(p)          # node server gone OR Claude session gone (orphaned) → prune the reg
            except OSError: pass
            continue
        if presence == "suspended":
            continue                   # paused session — NOT reachable (excluded from live), but KEEP the reg
        out.append(reg)                #   (it re-appears when resumed; pruning would strip a resumable session)
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
# The watcher arms a fold ONLY for the turn THIS dispatch started: each dispatch mints a fresh NONCE,
# tags `source = channel-fabric:<nonce>`, and stores {thread, nonce} as the member's pending fold. A
# `done` is folded only when preceded, IN THE LIVE STREAM, by an `injected` whose source nonce matches
# the CURRENT pending nonce. Why the nonce (not a bare constant source):
#   /watch REPLAYS s.events on connect (session_supervisor L1485). Two stale-done hazards exist —
#     (a) a FOREIGN turn (e.g. cc_clone.msg_clone, source "http"): its replayed injected has a non-
#         channel-fabric source → never arms → discarded.
#     (b) a PRIOR OWN turn of ours sitting in the replay (a watcher RECONNECT after a non-`closed`
#         stream blip): its replayed injected carries an OLD nonce ≠ the current pending nonce → never
#         arms → discarded; so the CURRENT turn's real reply is never dropped by a stale own-done.
# Both stale-done classes are correctly DISCARDED — no mis-route, no silent dropped reply.
CHANNEL_FABRIC_SOURCE = "channel-fabric"   # the source PREFIX (the nonce is appended per dispatch)


def _fabric_source(nonce: str) -> str:
    return f"{CHANNEL_FABRIC_SOURCE}:{nonce}"


_watchers: dict = {}                      # handle -> {"supervisor_session", "base"}
_pending_fold: dict = {}                  # handle -> {"thread", "nonce"} the in-flight turn answers
_watch_lock = threading.Lock()


def _push_supervised(reg: dict, content: str, *, meta: dict, base_timeout: float = 10) -> dict:
    """Dispatch to a supervised member: ensure its reply-watcher is running, mint this turn's fold
    nonce + record {thread, nonce} as the member's pending fold, then POST /inject tagged with the
    nonced source. The watcher folds back ONLY the done whose preceding injected carries THIS nonce —
    so neither a foreign turn nor a replayed prior-own turn can mis-route or drop a reply."""
    handle = reg.get("handle")
    base = supervisor_base(reg)
    session = reg.get("supervisor_session")
    if not session:
        raise ChannelError(f"supervised member {handle!r} has no supervisor_session — cannot /inject "
                           f"(the fork's clone-registration must carry it; see the seam schema).")
    thread = (meta or {}).get("thread")
    nonce = uuid.uuid4().hex                       # this dispatch's fold nonce (distinguishes THIS turn
                                                  # from a prior own turn sitting in the /watch replay)
    # ensure the reply watcher FIRST (a lazy ensure: a watcher connecting now replays s.events, but the
    # nonce gate discards every replayed injected/done — only THIS dispatch's nonce arms the fold)
    _ensure_supervised_watcher(handle, base, session)
    with _watch_lock:
        _pending_fold[handle] = {"thread": thread, "nonce": nonce}   # THIS turn's reply routing
    body = json.dumps({"session": session, "message": content,
                       "source": _fabric_source(nonce)}).encode()
    req = urllib.request.Request(base + "/inject", data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=base_timeout) as resp:
            ok = resp.status == 200
    except (urllib.error.URLError, OSError) as e:
        with _watch_lock:
            cur = _pending_fold.get(handle)
            if cur and cur.get("nonce") == nonce:   # only clear OUR pending (not a racing later dispatch)
                _pending_fold.pop(handle, None)
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
    armed_nonce = None     # set to a fold nonce by an `injected` whose source nonce matches the member's
                           # CURRENT pending nonce — only THEN is the next done ours to fold. A `done`
                           # not preceded by a matching-nonce injected (foreign turn, OR a replayed
                           # own turn carrying an old nonce) is DISCARDED — no mis-route, no dropped reply.
    try:
        for raw in resp:
            try:
                ev = json.loads(raw)
            except ValueError:
                continue
            etype = ev.get("type")
            if etype == "injected":
                src = ev.get("source") or ""
                if not src.startswith(CHANNEL_FABRIC_SOURCE + ":"):
                    continue            # foreign inject (non-fabric source) — ignore
                ev_nonce = src.split(":", 1)[1]
                with _watch_lock:
                    cur = _pending_fold.get(handle)
                # arm ONLY if this injected's nonce is the member's current pending nonce (a replayed
                # OLD own-turn injected carries a stale nonce ≠ current → never arms)
                armed_nonce = ev_nonce if (cur and cur.get("nonce") == ev_nonce) else None
            elif etype == "done":
                if armed_nonce is None:
                    continue            # a replayed/foreign/stale done — discard (never mis-route)
                with _watch_lock:
                    cur = _pending_fold.get(handle)
                    if cur and cur.get("nonce") == armed_nonce:
                        _pending_fold.pop(handle, None)
                        thread = cur.get("thread")
                    else:
                        thread = None   # pending changed out from under us — don't route a stale done
                armed_nonce = None
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
            # NOTE: do NOT clear _pending_fold here. A re-dispatch after a stream blip overwrites the
            # single per-handle slot with a fresh nonce (correct single-slot semantics); clearing it
            # in this finally could delete a live pending a concurrent re-dispatch just set. An orphan
            # pending (watcher died, no re-dispatch) is harmless — nothing arms it without a live
            # matching-nonce injected.


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


# ---- the named-channel REGISTRY: RETIRED 2026-06-29 (folded into session_channels) ----
# This module is the channel TRANSPORT layer (live-injection: live_sessions/find/push/send/broadcast/
# mail + the two transports). It NO LONGER holds a named-channel store.
#
# Until 2026-06-29 cc_channels ALSO carried a SECOND named-channel store (create_channel/list_channels/
# add_member/remove_member/archive_channel/channel_members/is_shared, backed by .data/channels/_channels/
# <id>.json). That duplicated the channel STRUCTURE that session_channels owns (channels.jsonl). The two
# stores were ONE channel concept split in two; the cc store was folded into session_channels — the ONE
# named-channel store — and these functions retired. The 15 _channels/*.json records were migrated into
# channels.jsonl (explicit slug-ids + a shared flag). One channel concept now reads cleanly:
#   • STRUCTURE (what a channel IS — name/purpose/roster/mode/shared/lifecycle): session_channels.py,
#     reached via the `channels`/`channel_act` MCP tools.
#   • TRANSPORT (reach a live member NOW — push/find/reply-back): cc_channels.py (here), `cc_channel` tool.
#
# Consumers were repointed to session_channels:
#   • runtime/channel_boundary_run.py — is_shared/channel_members/create_channel/set_shared (the shared edge)
#   • runtime/cc_attachments.py       — channel existence check
# Use runtime.session_channels.{create_channel, channel_members, is_shared, set_shared, add_member,
# remove_member, archive_channel, fold_channels, get_channel} (each takes a `store` as its first arg).
