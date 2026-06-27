#!/usr/bin/env python3
"""ops/owui_to_fork_listen.py — PUSH connector: wake THIS fork session on Tim's OpenWebUI channel messages.

Replaces the polling probe (owui_to_fork_watch.py) with an event SUBSCRIBER. OpenWebUI emits every channel
message over socket.io as `events:channel` (type `message`) to room `channel:{id}` — carrying the FULL message
(parent_id, reply_to_id, reply_to_message, meta, user). We join the room and react on the event. Proven from
source: open_webui/routers/channels.py:1060 (emit), socket/main.py:413 (join-channels), :236 (socketio_path).

Why this is strictly better than the poll:
  - NO POLLING — reacts the instant a message lands (Tim's directive 2026-06-27).
  - THREAD DEAD-ZONE GONE — the REST messages endpoint filters parent_id=None (models/messages.py:292), so the
    poll never saw thread replies / replies-to-a-reply. The socket emits ALL messages to the room → we see them.
  - RESTART-SWALLOW GONE — a live stream has no cursor/seed; nothing to mis-mark "seen" on restart.

Filter: act only on Tim-authored messages (meta is None). My own replies + mirrored members post via webhooks
(meta set) → never echoed. Reply/thread aware: a quote-reply or thread reply carries the member Tim is answering.

Tied to this session's company-channel inject port — restart with the new FORK_PORT if the session changes.
"""
from __future__ import annotations
import os, time, queue, threading, requests, socketio

OWUI = os.environ.get("OWUI_BASE", "http://127.0.0.1:8081")
CH = os.environ.get("OWUI_CHANNEL", "a9a338cc-ede3-4268-a43a-94857e2ad4e6")
EMAIL = os.environ.get("OWUI_EMAIL", "v.i@conceptv.com.au")
PASSWORD = os.environ.get("OWUI_PASSWORD", "")
FORK_PORT = os.environ.get("FORK_PORT", "41939")          # this session's company-channel inject port
SIO_PATH = "/ws/socket.io"                                # open_webui/socket/main.py:236

_seen: set[str] = set()                                   # in-session de-dup (socket won't replay, but be safe)
_deliver_q: "queue.Queue[tuple[str, dict]]" = queue.Queue()  # decouple delivery from the socket thread

# Why a queue + worker (proven 2026-06-27): the channel server (company_channel.mjs:151) does
# `await mcp.notification()` BEFORE replying 200, so the inject POST BLOCKS until the notification drains
# into the live conversation. While THIS session is busy, that can take seconds → an 8s read-timeout →
# the message is LOST ("none work" while I was building). Worse, doing that blocking POST inside the
# socketio event handler froze the client → missed pings → disconnect/flap. So: the handler ENQUEUES
# (instant, socket stays alive) and a worker DELIVERS with retry until it lands (survives my busy spells).


def signin() -> str:
    if not PASSWORD:
        raise SystemExit("set OWUI_PASSWORD")
    r = requests.post(f"{OWUI}/api/v1/auths/signin", json={"email": EMAIL, "password": PASSWORD}, timeout=15)
    r.raise_for_status()
    return r.json()["token"]


def _deliver_worker() -> None:
    """Drain the queue, delivering each message to the fork port with retry until it lands. Runs on its
    OWN thread so a slow/blocking inject never freezes the socket client. A message that arrives while
    the session is busy is retried until the session is idle enough to accept it (instead of being lost)."""
    while True:
        content, meta = _deliver_q.get()
        for attempt in range(1, 41):                      # ~retry for a few minutes, then give up loudly
            try:
                r = requests.post(f"http://127.0.0.1:{FORK_PORT}/",
                                  json={"content": content, "meta": meta}, timeout=10)
                if r.status_code == 200:
                    print(f"  ✓ delivered (try {attempt}): {content[:60]!r}", flush=True)
                    break
                print(f"  deliver non-200 ({r.status_code}) try {attempt} — retrying", flush=True)
            except Exception as e:
                print(f"  deliver timeout/err try {attempt} ({type(e).__name__}) — retrying (session busy?)", flush=True)
            time.sleep(2)
        else:
            print(f"  ✗ GAVE UP after 40 tries — message dropped: {content[:80]!r}", flush=True)
        _deliver_q.task_done()


def handle_message(msg: dict) -> None:
    """A new channel message arrived (full dict from the socket). Inject Tim's into the fork session."""
    mid = msg.get("id")
    if not mid or mid in _seen:
        return
    if msg.get("meta"):                                   # webhook-origin (my reply / a mirrored member) — skip
        _seen.add(mid); return
    text = (msg.get("content") or "").strip()
    if not text:
        _seen.add(mid); return
    # who is Tim answering? (quote-reply OR thread reply both carry this)
    rt = msg.get("reply_to_message") or {}
    target = ((rt.get("user") or {}).get("name")) or (((rt.get("meta") or {}).get("webhook") or {}).get("name"))
    threaded = bool(msg.get("parent_id"))
    bits = []
    if target:
        bits.append(f"replying to {target}")
    if threaded:
        bits.append("in a thread")
    ctx = f" ({', '.join(bits)})" if bits else ""
    content = f"[Tim, in the OpenWebUI channel{ctx} — reply to him by posting to the fork webhook] {text}"
    _seen.add(mid)                                        # mark before enqueue — the worker owns delivery+retry
    # CRITICAL (proven 2026-06-27): the <channel> notification does NOT surface if meta carries a null or
    # boolean value (controlled test: rich payload with reply_target:null + threaded:false stayed silent;
    # the same message with simple string-only meta surfaced). So emit STRING-ONLY meta, omit when absent;
    # the reply/thread context already rides in the content wrapper above (ctx), so nothing is lost.
    meta = {"from": "tim", "thread": "owui-channel", "owui_msg_id": str(mid)}
    if target:
        meta["reply_target"] = str(target)
    if threaded:
        meta["threaded"] = "true"                         # string, not bool — never a JSON bool/null in meta
    _deliver_q.put((content, meta))
    print(f"  → queued{ctx}: {text[:60]!r}", flush=True)


def main():
    token = signin()
    threading.Thread(target=_deliver_worker, daemon=True).start()   # delivery off the socket thread
    sio = socketio.Client(reconnection=True, reconnection_attempts=0, request_timeout=20)

    @sio.event
    def connect():
        print("connected → joining channels", flush=True)
        sio.emit("user-join", {"auth": {"token": token}})
        sio.emit("join-channels", {"auth": {"token": token}})

    @sio.event
    def disconnect():
        print("disconnected (will auto-reconnect)", flush=True)

    @sio.on("events:channel")
    def on_channel(data):
        try:
            if (data or {}).get("channel_id") != CH:
                return
            d = (data.get("data") or {})
            if d.get("type") != "message":                # ignore message:update / message:reply / reactions
                return
            handle_message(d.get("data") or {})
        except Exception as e:
            print(f"  event error: {e}", flush=True)

    print(f"fork-listen: owui[{CH}] events:channel → inject :{FORK_PORT}  (push, no poll)", flush=True)
    # OWUI's socket server is websocket-ONLY by default (socket/main.py:71, ENABLE_WEBSOCKET_SUPPORT=True).
    # Offering polling too makes the client flap (connect→'packet queue empty'→disconnect loop) → missed
    # messages. Pin to websocket + pass auth at connect (connect handler reads auth, main.py:342).
    sio.connect(OWUI, socketio_path=SIO_PATH, transports=["websocket"], auth={"token": token})
    sio.wait()


if __name__ == "__main__":
    raise SystemExit(main())
