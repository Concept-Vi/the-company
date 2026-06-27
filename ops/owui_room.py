#!/usr/bin/env python3
"""ops/owui_room.py — THE ROOM: an OpenWebUI channel as the human window onto a fabric room of AI members.

Generalizes the proven single-fork wire (ops/owui_to_fork_listen.py) to N members. Built ENTIRELY on
pieces proven this session (2026-06-27):

  IDENTITY / DISPLAY (member → human): each room member self-registers its OWN OpenWebUI webhook
      (name = the member's friendly label). When a member speaks, it posts to its webhook and appears
      in the OWUI channel AS ITSELF. (Same mechanism the fork already uses to reply.)

  ADDRESS (human → member): the room SUBSCRIBES to the OWUI channel over socket.io (events:channel —
      push, no poll). Every message Tim types is routed to a member via cc_channels.push (the unified
      per-member transport: a live Claude session gets a <channel> inject on its port; a supervised
      session gets a supervisor /inject). A REPLY to member X's message → routed to X; a plain message
      → broadcast to every room member. The member replies on its own webhook, closing the loop.

INVARIANT (the bug that cost a session to find): the <channel> notification only SURFACES if meta is
string-only — a null or boolean value silently blocks it. So this module emits STRING-ONLY meta, and
the choke point (channels/company_channel.mjs) now also coerces. Belt and suspenders.

ROSTER: a member is one {handle, label} — handle is its cc_channels registration (live_sessions()),
label is how it appears to Tim. The roster is the room's membership (so unrelated live sessions are
NOT pulled in). Adding a member = adding a roster row. Config via ROOM_ROSTER env (json) or the default.

Run (from repo root): OWUI_PASSWORD=... ROOM_ROSTER='[{"handle":"ch-82ro8r4o","label":"fork"}]' \
    .venv/bin/python ops/owui_room.py
"""
from __future__ import annotations
import json, os, sys, threading, queue, time, requests, socketio

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from runtime import cc_channels                                    # the unified per-member delivery

OWUI = os.environ.get("OWUI_BASE", "http://127.0.0.1:8081")
OWUI_CHANNEL = os.environ.get("ROOM_OWUI_CHANNEL", "a9a338cc-ede3-4268-a43a-94857e2ad4e6")
EMAIL = os.environ.get("OWUI_EMAIL", "v.i@conceptv.com.au")
PASSWORD = os.environ.get("OWUI_PASSWORD", "")
SIO_PATH = "/ws/socket.io"
STATE = os.environ.get("ROOM_STATE", os.path.join(REPO, ".data", "owui_room_state.json"))
# The room roster: each member is {handle, label}. handle = cc_channels registration; label = OWUI identity.
ROSTER = json.loads(os.environ.get("ROOM_ROSTER", '[{"handle":"ch-82ro8r4o","label":"fork"}]'))

_seen: set[str] = set()
_route_q: "queue.Queue[tuple[str, str]]" = queue.Queue()           # (member_handle, content) — off the socket thread


# ---- state: the per-member webhook map (label -> {id, token}); survives restarts ----
def _load_state() -> dict:
    try:
        return json.load(open(STATE))
    except Exception:
        return {}


def _save_state(s: dict) -> None:
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(s, open(STATE + ".tmp", "w"), indent=2)
    os.replace(STATE + ".tmp", STATE)


def signin() -> str:
    if not PASSWORD:
        raise SystemExit("set OWUI_PASSWORD")
    r = requests.post(f"{OWUI}/api/v1/auths/signin", json={"email": EMAIL, "password": PASSWORD}, timeout=15)
    r.raise_for_status()
    return r.json()["token"]


def ensure_member_webhook(token: str, label: str, state: dict) -> dict:
    """Self-registration: a room member's OWN OpenWebUI webhook (identity = label). Created once, cached."""
    hooks = state.setdefault("webhooks", {})
    if label in hooks:
        return hooks[label]
    r = requests.post(f"{OWUI}/api/v1/channels/{OWUI_CHANNEL}/webhooks/create",
                      headers={"Authorization": f"Bearer {token}"}, json={"name": label}, timeout=15)
    r.raise_for_status()
    wh = r.json()
    hooks[label] = {"id": wh["id"], "token": wh["token"]}
    _save_state(state)
    print(f"  registered webhook for member '{label}'", flush=True)
    return hooks[label]


def label_for_handle(handle: str) -> str:
    for m in ROSTER:
        if m["handle"] == handle:
            return m["label"]
    return handle


def handle_for_label(label: str) -> "str | None":
    for m in ROSTER:
        if m["label"] == label:
            return m["handle"]
    return None


# ---- ADDRESS: deliver Tim's message into a member's live session (string-only meta) ----
def _route_worker() -> None:
    while True:
        handle, content = _route_q.get()
        label = label_for_handle(handle)
        wh = _state.get("webhooks", {}).get(label, {})
        # tell the member who's speaking + exactly how to reply (its own webhook) — the member posts there.
        wrapped = (f"[Tim, in the OpenWebUI room — reply to him by POSTing {{\"content\":\"...\"}} to "
                   f"http://127.0.0.1:8081/api/v1/channels/webhooks/{wh.get('id')}/{wh.get('token')}] {content}")
        meta = {"from": "tim", "thread": "owui-room", "to": label}     # STRING-ONLY — never null/bool
        for attempt in range(1, 31):
            try:
                res = cc_channels.push(handle, wrapped, meta=meta, base_timeout=12)
                if res.get("ok"):
                    print(f"  → delivered to {label} ({handle}) try {attempt}", flush=True)
                    break
                print(f"  deliver to {label} not ok try {attempt} — retry", flush=True)
            except cc_channels.ChannelError as e:
                print(f"  deliver to {label} err try {attempt}: {e} — retry (member may be offline)", flush=True)
            except Exception as e:
                print(f"  deliver to {label} unexpected try {attempt}: {type(e).__name__} — retry", flush=True)
            time.sleep(2)
        else:
            print(f"  ✗ GAVE UP delivering to {label}: {content[:60]!r}", flush=True)
        _route_q.task_done()


def route_message(text: str, target_label: "str | None") -> None:
    """Route a Tim message: to the addressed member if a reply, else broadcast to all roster members."""
    if target_label:
        h = handle_for_label(target_label)
        if h:
            _route_q.put((h, text)); return
        # reply was to a non-member (e.g. another human msg) — fall through to broadcast
    for m in ROSTER:
        _route_q.put((m["handle"], text))


_state: dict = {}


def main():
    global _state
    token = signin()
    _state = _load_state()
    for m in ROSTER:                                               # self-register every member up front
        ensure_member_webhook(token, m["label"], _state)
    threading.Thread(target=_route_worker, daemon=True).start()

    sio = socketio.Client(reconnection=True, reconnection_attempts=0, request_timeout=20)

    @sio.event
    def connect():
        print("connected → joining channels", flush=True)
        sio.emit("user-join", {"auth": {"token": token}})
        sio.emit("join-channels", {"auth": {"token": token}})

    @sio.on("events:channel")
    def on_channel(data):
        try:
            if (data or {}).get("channel_id") != OWUI_CHANNEL:
                return
            d = (data.get("data") or {})
            if d.get("type") != "message":
                return
            m = d.get("data") or {}
            mid = m.get("id")
            if not mid or mid in _seen:
                return
            if m.get("meta"):                                      # webhook-origin (a member's own post) — skip
                _seen.add(mid); return
            text = (m.get("content") or "").strip()
            if not text:
                _seen.add(mid); return
            _seen.add(mid)
            rt = m.get("reply_to_message") or {}
            target = ((rt.get("user") or {}).get("name")) or (((rt.get("meta") or {}).get("webhook") or {}).get("name"))
            route_message(text, target)
            print(f"  routed Tim msg ({'->'+target if target else 'broadcast'}): {text[:50]!r}", flush=True)
        except Exception as e:
            print(f"  event error: {e}", flush=True)

    print(f"owui-room: channel[{OWUI_CHANNEL}] · members={[m['label'] for m in ROSTER]} · push-deliver", flush=True)
    sio.connect(OWUI, socketio_path=SIO_PATH, transports=["websocket"], auth={"token": token})
    sio.wait()


if __name__ == "__main__":
    raise SystemExit(main())
