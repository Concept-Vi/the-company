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
import time
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAN_DIR = os.path.join(REPO, ".data", "channels")
MAIL_LOG = os.path.join(CHAN_DIR, "_mail.jsonl")        # durable record of every channel message/reply
THREADS = os.path.join(CHAN_DIR, "_threads.json")       # thread_id -> {originator_handle, topic, members}


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


def live_sessions() -> list:
    """Every live channel-session: [{handle, session_id, cwd, description, pid, port, started}],
    newest first. Prunes registrations whose process has died (stale files removed)."""
    out = []
    if not os.path.isdir(CHAN_DIR):
        return out
    for fn in os.listdir(CHAN_DIR):
        if not fn.endswith(".json") or fn.startswith("_"):
            continue
        p = os.path.join(CHAN_DIR, fn)
        reg = _read_reg(p)
        if not reg or "port" not in reg:
            continue
        if not _alive(reg.get("pid", -1)):
            try: os.unlink(p)          # prune the dead registration
            except OSError: pass
            continue
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
    """Inject `content` into a live channel-session's conversation (POST to its port). `meta` keys
    become <channel ...> attributes (identifiers only). Returns {ok, handle, status}."""
    reg = handle_or_reg if isinstance(handle_or_reg, dict) else find(handle_or_reg)
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
    return {"ok": ok, "handle": reg.get("handle"), "cwd": reg.get("cwd"), "port": port}


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
