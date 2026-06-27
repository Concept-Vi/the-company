#!/usr/bin/env python3
"""ops/owui_room.py — THE OPERATOR ROOM: an OpenWebUI channel as a full console onto the Company fabric.

A human (Tim) and AI members share an OpenWebUI channel. Beyond chat, the room is an OPERATOR SURFACE:
from inside it Tim spawns/tears-down/renames members, repersonas them, creates/lists channels, checks
status — by SLASH-COMMAND or in NATURAL LANGUAGE. All of it runs on the supervisor + fabric + OWUI APIs.

Three ways to drive, one engine:
  1. SLASH      — Tim types `/spawn analyst <persona>`, `/members`, `/channel design`, … → the daemon
                  parses and executes directly. The deterministic power-user substrate.
  2. OP-ENDPOINT— the daemon runs a tiny local HTTP op-server (POST /op {op, args}). The CLI mode
                  (`owui_room.py op <op> <args…>`) is a thin client to it. This lets an AI OPERATOR
                  member (which has Bash) drive the same ops without holding any credentials.
  3. NATURAL    — a spawned `operator` member interprets Tim's plain-language requests and calls the
                  op CLI to fulfil them. So Tim just talks; the operator translates + executes.

The daemon is the SOLE executor (holds the OWUI admin token); every result is posted back into the room
as `operator` so Tim sees what happened. Members are reached via cc_channels.push (unified transport;
STRING-ONLY meta — null/bool break <channel> surfacing, proven 2026-06-27 + guarded at the choke point).

Run daemon: OWUI_PASSWORD=… .venv/bin/python ops/owui_room.py
CLI (op):   .venv/bin/python ops/owui_room.py op members
"""
from __future__ import annotations
import json, os, sys, threading, queue, time, uuid, urllib.request, requests, socketio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from runtime import cc_channels, cc_clone

OWUI = os.environ.get("OWUI_BASE", "http://127.0.0.1:8081")
OWUI_CHANNEL = os.environ.get("ROOM_OWUI_CHANNEL", "a9a338cc-ede3-4268-a43a-94857e2ad4e6")
EMAIL = os.environ.get("OWUI_EMAIL", "v.i@conceptv.com.au")
PASSWORD = os.environ.get("OWUI_PASSWORD", "")
SUPERVISOR = os.environ.get("COMPANY_SUPERVISOR_BASE", "http://127.0.0.1:8771")
SIO_PATH = "/ws/socket.io"
STATE = os.environ.get("ROOM_STATE", os.path.join(REPO, ".data", "owui_room_state.json"))
OP_PORT = int(os.environ.get("ROOM_OP_PORT", "8782"))
DEFAULT_ROSTER = json.loads(os.environ.get("ROOM_ROSTER", '[{"handle":"ch-82ro8r4o","label":"fork"}]'))

_seen: set[str] = set()
_route_q: "queue.Queue[tuple[str, str]]" = queue.Queue()
_state: dict = {}
_token: str = ""
_lock = threading.RLock()


# ---------------- state ----------------
def _load_state() -> dict:
    try:
        return json.load(open(STATE))
    except Exception:
        return {}


def _save_state() -> None:
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(_state, open(STATE + ".tmp", "w"), indent=2)
    os.replace(STATE + ".tmp", STATE)


def roster() -> list:
    return _state.setdefault("roster", list(DEFAULT_ROSTER))


def _member(label: str) -> "dict | None":
    return next((m for m in roster() if m["label"] == label), None)


# ---------------- OWUI ----------------
def signin() -> str:
    if not PASSWORD:
        raise SystemExit("set OWUI_PASSWORD")
    r = requests.post(f"{OWUI}/api/v1/auths/signin", json={"email": EMAIL, "password": PASSWORD}, timeout=15)
    r.raise_for_status()
    return r.json()["token"]


def ensure_webhook(label: str) -> dict:
    hooks = _state.setdefault("webhooks", {})
    if label in hooks:
        return hooks[label]
    r = requests.post(f"{OWUI}/api/v1/channels/{OWUI_CHANNEL}/webhooks/create",
                      headers={"Authorization": f"Bearer {_token}"}, json={"name": label}, timeout=15)
    r.raise_for_status()
    wh = r.json()
    hooks[label] = {"id": wh["id"], "token": wh["token"]}
    _save_state()
    return hooks[label]


def webhook_url(label: str) -> str:
    wh = ensure_webhook(label)
    return f"{OWUI}/api/v1/channels/webhooks/{wh['id']}/{wh['token']}"


def post_as(label: str, content: str) -> None:
    """Post a message into the room under `label`'s identity (its webhook)."""
    wh = ensure_webhook(label)
    try:
        requests.post(f"{OWUI}/api/v1/channels/webhooks/{wh['id']}/{wh['token']}",
                      json={"content": content}, timeout=15)
    except Exception as e:
        print(f"  post_as({label}) failed: {e}", flush=True)


def create_owui_channel(name: str) -> dict:
    r = requests.post(f"{OWUI}/api/v1/channels/create", headers={"Authorization": f"Bearer {_token}"},
                      json={"name": name}, timeout=15)
    r.raise_for_status()
    return r.json()


def list_owui_channels() -> list:
    r = requests.get(f"{OWUI}/api/v1/channels/", headers={"Authorization": f"Bearer {_token}"}, timeout=15)
    r.raise_for_status()
    return r.json() or []


# ---------------- supervisor ----------------
def _sup(path: str, body: dict, timeout: float = 60) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(SUPERVISOR + path, data=data,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


# ---------------- OPERATIONS (the engine — shared by slash, op-endpoint, NL) ----------------
def op_help(*_a) -> str:
    return ("Operator commands (slash, or just ask the operator in plain words):\n"
            "  /members                      — list members + status\n"
            "  /spawn <label> [persona…]     — spawn a new AI member\n"
            "  /teardown <label>             — remove a member\n"
            "  /rename <old> <new>           — rename a member's identity\n"
            "  /persona <label> <text>       — re-brief a member's role\n"
            "  /say <label> <text>           — send a message to a member\n"
            "  /channel <name>               — create a new channel\n"
            "  /channels                     — list channels\n"
            "  /help                         — this")


def op_members(*_a) -> str:
    lines = []
    for m in roster():
        reg = cc_channels.find(m["handle"])
        if reg:
            t = reg.get("transport") or "channel"
            status = "live"
            if t == "supervised":
                ss = reg.get("supervisor_session")
                try:
                    sj = _sup_get_state(ss)
                    status = f"supervised/{sj}"
                except Exception:
                    status = "supervised"
            lines.append(f"  • {m['label']}  [{t}]  {status}  ({m['handle']})")
        else:
            lines.append(f"  • {m['label']}  [offline / not registered]  ({m['handle']})")
    return "Members:\n" + ("\n".join(lines) if lines else "  (none)")


def _sup_get_state(supervisor_session: str) -> str:
    req = urllib.request.Request(SUPERVISOR + "/sessions", method="GET")
    with urllib.request.urlopen(req, timeout=5) as r:
        for s in (json.load(r).get("sessions") or []):
            if s.get("id") == supervisor_session:
                return s.get("state", "?")
    return "absent"


def op_spawn(label: str = "", *persona_words) -> str:
    label = (label or "").strip()
    if not label:
        return "usage: /spawn <label> [persona…]"
    if _member(label):
        return f"member '{label}' already exists — pick another label or /teardown it first."
    persona_brief = " ".join(persona_words).strip() or f"a sharp, concise member named {label}"
    hook = webhook_url(label)                                  # mint identity first
    persona = (
        f"You are '{label}', an AI MEMBER of a live multi-party room (the human Tim and other AI members). "
        f"To SPEAK in the room you run a Bash command exactly like:\n"
        f"  curl -s -X POST '{hook}' -H 'Content-Type: application/json' -d '{{\"content\":\"<your message>\"}}'\n"
        f"That curl is the ONLY way the room hears you — run it every time you want to say something. "
        f"Messages from the room arrive to you as your turns. Your role: {persona_brief}. Keep posts short. "
        f"RIGHT NOW introduce yourself to the room in one short sentence by running the curl above."
    )
    rec = _sup("/bridge-session", {"operator_consent": True, "name": label, "source": "owui-room",
                                   "prompt": persona}).get("session", {})
    sid = rec.get("id")
    if not sid:
        return f"spawn failed for '{label}' — no session id returned."
    cc_clone.register_supervised_member(handle=label, session_id=sid, supervisor_session=sid,
                                        cwd=REPO, description=f"room member: {persona_brief[:60]}")
    roster().append({"handle": label, "label": label})
    _save_state()
    return f"spawned '{label}' ({sid}) — registered, in the roster, introducing itself now."


def op_teardown(label: str = "", *_a) -> str:
    m = _member(label)
    if not m:
        return f"no member '{label}'."
    reg = cc_channels.find(m["handle"])
    msg = []
    if reg and (reg.get("transport") == "supervised") and reg.get("supervisor_session"):
        try:
            _sup("/teardown", {"session": reg["supervisor_session"]}, timeout=20)
            msg.append("supervisor session torn down")
        except Exception as e:
            msg.append(f"teardown call error: {e}")
    try:
        cc_clone._deregister_member(m["handle"]); msg.append("deregistered")
    except Exception as e:
        msg.append(f"deregister error: {e}")
    _state["roster"] = [x for x in roster() if x["label"] != label]
    _save_state()
    return f"removed '{label}' — " + "; ".join(msg)


def op_rename(old: str = "", new: str = "", *_a) -> str:
    m = _member(old)
    if not m:
        return f"no member '{old}'."
    if _member(new):
        return f"'{new}' already exists."
    m["label"] = new                                           # webhook identity for NEW posts re-mints lazily
    _save_state()
    return f"renamed '{old}' → '{new}' (new posts use the new identity; handle unchanged: {m['handle']})."


def op_persona(label: str = "", *words) -> str:
    m = _member(label)
    if not m:
        return f"no member '{label}'."
    text = " ".join(words).strip()
    if not text:
        return "usage: /persona <label> <new role text>"
    _route_q.put((m["handle"], f"[operator re-brief] From now on your role is: {text}"))
    return f"re-briefed '{label}'."


def op_say(label: str = "", *words) -> str:
    m = _member(label)
    if not m:
        return f"no member '{label}'."
    _route_q.put((m["handle"], " ".join(words)))
    return f"sent to '{label}'."


def op_channel(name: str = "", *_a) -> str:
    name = (name or "").strip()
    if not name:
        return "usage: /channel <name>"
    try:
        ch = create_owui_channel(name)
        return f"created channel '{name}' (id {ch.get('id')}). (To make it a live room too, tell me — multi-room is next.)"
    except Exception as e:
        return f"channel create failed: {e}"


def op_channels(*_a) -> str:
    try:
        chs = list_owui_channels()
        return "Channels:\n" + "\n".join(f"  • {c.get('name')}  (id {c.get('id')})" for c in chs) if chs else "Channels: (none)"
    except Exception as e:
        return f"list channels failed: {e}"


def op_interrupt(label: str = "", *_a) -> str:
    """Halt a member's CURRENT turn (the soft stop — supervisor /interrupt; the session survives)."""
    m = _member(label)
    if not m:
        return f"no member '{label}'."
    reg = cc_channels.find(m["handle"])
    if not reg or reg.get("transport") != "supervised" or not reg.get("supervisor_session"):
        return f"'{label}' is not a supervised member — nothing to interrupt."
    try:
        _sup("/interrupt", {"session": reg["supervisor_session"]}, timeout=15)
        return f"⏸ interrupted '{label}' (current turn halted; member still present)."
    except Exception as e:
        return f"interrupt '{label}' failed: {e}"


def op_stop(*_a) -> str:
    """EMERGENCY BRAKE — interrupt every supervised member's current turn at once."""
    hit = []
    for m in roster():
        reg = cc_channels.find(m["handle"])
        if reg and reg.get("transport") == "supervised" and reg.get("supervisor_session"):
            try:
                _sup("/interrupt", {"session": reg["supervisor_session"]}, timeout=10); hit.append(m["label"])
            except Exception:
                pass
    return f"⏹ STOP — interrupted: {', '.join(hit) if hit else '(none running)'}"


def op_panel(*_a) -> str:
    """The control panel — every member with its stop controls (the text 'buttons')."""
    lines = ["🎛 Control panel — tap a command:"]
    for m in roster():
        lb = m["label"]
        if lb == "fork":
            lines.append(f"  {lb}: (that's the lead session — not stoppable from here)")
        else:
            lines.append(f"  {lb}:   ⏸ /interrupt {lb}    ⏹ /teardown {lb}")
    lines.append("  ALL:   ⏹ /stop  (interrupt everyone)   ·   /members   ·   /help")
    return "\n".join(lines)


def op_spawn_operator(*_a) -> str:
    """Spawn the NL OPERATOR member: an AI that turns Tim's plain-language requests into op-CLI calls."""
    if _member("operator"):
        return "operator already present."
    hook = webhook_url("operator")
    py = sys.executable
    cli = os.path.join(REPO, "ops", "owui_room.py")
    persona = (
        "You are 'operator', the room's OPERATOR — you turn Tim's plain-language requests into fabric "
        "actions. You have a Bash shell. To ACT, run the op CLI (one Bash command):\n"
        f"  {py} {cli} op <command> [args]\n"
        "Commands: members | spawn <label> <persona words…> | teardown <label> | rename <old> <new> | "
        "persona <label> <text> | say <label> <text> | channel <name> | channels | help.\n"
        "Examples: Tim says 'spin up an analyst who watches the market' → run:  "
        f"{py} {cli} op spawn analyst who watches the market\n"
        "Tim says 'who's here?' → run:  " f"{py} {cli} op members\n"
        "Tim says 'make a design channel' → run:  " f"{py} {cli} op channel design\n"
        "The command's RESULT is posted into the room automatically — do NOT repeat it. If a request is "
        "ambiguous, ask ONE short clarifying question by posting to your webhook:\n"
        f"  curl -s -X POST '{hook}' -H 'Content-Type: application/json' -d '{{\"content\":\"…\"}}'\n"
        "Be terse and act decisively. RIGHT NOW post a one-line greeting 'operator online — tell me what "
        "to build' via that curl."
    )
    rec = _sup("/bridge-session", {"operator_consent": True, "name": "operator", "source": "owui-room",
                                   "prompt": persona}).get("session", {})
    sid = rec.get("id")
    if not sid:
        return "operator spawn failed — no session id."
    cc_clone.register_supervised_member(handle="operator", session_id=sid, supervisor_session=sid,
                                        cwd=REPO, description="the room operator (NL → ops)")
    roster().append({"handle": "operator", "label": "operator"})
    _save_state()
    return "operator spawned — talk to it in plain language (or reply to it) and it runs the ops."


OPS = {"help": op_help, "members": op_members, "spawn": op_spawn, "teardown": op_teardown,
       "rename": op_rename, "persona": op_persona, "say": op_say, "channel": op_channel,
       "channels": op_channels, "spawn_operator": op_spawn_operator,
       "interrupt": op_interrupt, "stop": op_stop, "panel": op_panel}


def dispatch(op: str, args: list) -> str:
    fn = OPS.get(op)
    if not fn:
        return f"unknown op '{op}'. /help for commands."
    try:
        with _lock:
            return fn(*args)
    except Exception as e:
        return f"op '{op}' error: {type(e).__name__}: {e}"


# ---------------- inbound: deliver Tim's chat to a member (string-only meta) ----------------
def _route_worker() -> None:
    while True:
        handle, content = _route_q.get()
        label = next((m["label"] for m in roster() if m["handle"] == handle), handle)
        hook = ""
        try:
            hook = webhook_url(label)
        except Exception:
            pass
        wrapped = f"[room message — to reply, POST {{\"content\":\"...\"}} to {hook}] {content}"
        meta = {"from": "tim", "thread": "owui-room", "to": label}     # STRING-ONLY
        for attempt in range(1, 31):
            try:
                if cc_channels.push(handle, wrapped, meta=meta, base_timeout=12).get("ok"):
                    print(f"  → delivered to {label} try {attempt}", flush=True); break
            except cc_channels.ChannelError as e:
                print(f"  deliver {label} err try {attempt}: {e}", flush=True)
            except Exception as e:
                print(f"  deliver {label} unexpected try {attempt}: {type(e).__name__}", flush=True)
            time.sleep(2)
        else:
            print(f"  ✗ gave up delivering to {label}", flush=True)
        _route_q.task_done()


# ---------------- op-server (thin executor for the CLI / operator member) ----------------
class _OpHandler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"{}")
            op = body.get("op", ""); args = body.get("args", []) or []
            result = dispatch(op, args)
            post_as("operator", result)                        # surface every op result in the room
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "result": result}).encode())
        except Exception as e:
            self.send_response(500); self.end_headers(); self.wfile.write(str(e).encode())


def _start_op_server():
    srv = ThreadingHTTPServer(("127.0.0.1", OP_PORT), _OpHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    _state["op_port"] = OP_PORT; _save_state()
    print(f"  op-server on 127.0.0.1:{OP_PORT}", flush=True)


# ---------------- daemon ----------------
def main():
    global _state, _token
    _token = signin()
    _state = _load_state()
    roster()                                                   # ensure default seeded
    for m in roster():
        ensure_webhook(m["label"])
    ensure_webhook("operator")                                 # system identity for op results
    threading.Thread(target=_route_worker, daemon=True).start()
    _start_op_server()

    sio = socketio.Client(reconnection=True, reconnection_attempts=0, request_timeout=20)

    @sio.event
    def connect():
        print("connected → joining channels", flush=True)
        sio.emit("user-join", {"auth": {"token": _token}})
        sio.emit("join-channels", {"auth": {"token": _token}})

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
            if m.get("meta"):
                _seen.add(mid); return
            text = (m.get("content") or "").strip()
            if not text:
                _seen.add(mid); return
            _seen.add(mid)
            if text.startswith("/"):                            # SLASH command → run op directly
                parts = text[1:].split()
                op = parts[0] if parts else "help"
                post_as("operator", dispatch(op, parts[1:]))
                print(f"  slash: /{op}", flush=True); return
            rt = m.get("reply_to_message") or {}
            target = ((rt.get("user") or {}).get("name")) or (((rt.get("meta") or {}).get("webhook") or {}).get("name"))
            low = text.lower()
            wants_operator = (target == "operator") or low.startswith(("operator", "@operator", "op,", "op:"))
            if wants_operator and _member("operator"):          # NATURAL-LANGUAGE op → the operator member
                _route_q.put((_member("operator")["handle"], text))
                print("  routed → operator (NL)", flush=True); return
            if target and _member(target) and target != "operator":
                _route_q.put((_member(target)["handle"], text))
                print(f"  routed → {target}", flush=True)
            else:
                for mm in roster():                             # plain message → broadcast to CHAT members
                    if mm["label"] != "operator":
                        _route_q.put((mm["handle"], text))
                print("  routed → broadcast", flush=True)
        except Exception as e:
            print(f"  event error: {e}", flush=True)

    print(f"owui-room: channel[{OWUI_CHANNEL}] · members={[m['label'] for m in roster()]} · operator-console", flush=True)
    sio.connect(OWUI, socketio_path=SIO_PATH, transports=["websocket"], auth={"token": _token})
    sio.wait()


# ---------------- CLI (thin client to the daemon's op-server) ----------------
def cli(argv):
    op = argv[0] if argv else "help"
    args = argv[1:]
    port = (_load_state() or {}).get("op_port", OP_PORT)
    req = urllib.request.Request(f"http://127.0.0.1:{port}/op",
                                 data=json.dumps({"op": op, "args": args}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        print(json.load(r).get("result", ""))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "op":
        cli(sys.argv[2:])
    else:
        raise SystemExit(main())
