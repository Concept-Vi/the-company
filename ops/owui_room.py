#!/usr/bin/env python3
"""ops/owui_room.py — THE OPERATOR ROOMS: OpenWebUI channels as a multi-room console onto the fabric.

A human (Tim) and AI members share OpenWebUI channels. Beyond chat, each channel is an OPERATOR SURFACE:
Tim spawns/tears-down/renames members, repersonas them, creates/lists channels, checks status — by
SLASH-COMMAND or NATURAL LANGUAGE. MULTI-ROOM: every channel the daemon knows is its own live room with
its own member roster; a slash command acts on the channel it was typed in. Members in a room can address
each other by @mention and converse (visible to Tim), guarded by a circuit breaker. Tim stops/pauses any
member by tapping a 🛑/⏸ reaction on its message (native, works on the phone).

Drive three ways, one engine:
  1. SLASH       — `/spawn analyst …`, `/members`, `/channel design`, `/status` … → executed on the
                   channel it was typed in.
  2. OP-ENDPOINT — the daemon runs a local op-server (POST /op {op, args, channel}); the CLI mode
                   (`owui_room.py op <op> …`) is a thin client. Lets an AI operator drive ops, no creds.
  3. NATURAL     — a spawned `operator` member maps Tim's plain words → op-CLI calls.
  4. REACTIONS   — 🛑/❌ on a member's message tears it down; ⏸/✋ interrupts its current turn.

The daemon is the SOLE executor (holds the OWUI token). Members are reached via cc_channels.push (unified
transport); meta is STRING-ONLY (null/bool break <channel> surfacing — proven; guarded at the choke point).

Run daemon: OWUI_PASSWORD=… .venv/bin/python ops/owui_room.py
CLI:        .venv/bin/python ops/owui_room.py op members            (acts on HOME room)
            .venv/bin/python ops/owui_room.py op spawn x role… --channel <cid>
"""
from __future__ import annotations
import json, os, sys, threading, queue, time, urllib.request, requests, socketio
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from runtime import cc_channels, cc_clone, session_channels as sc

OWUI = os.environ.get("OWUI_BASE", "http://127.0.0.1:8081")
HOME = os.environ.get("ROOM_OWUI_CHANNEL", "a9a338cc-ede3-4268-a43a-94857e2ad4e6")   # the default/home room
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
_mm_window: "dict[str, deque]" = {}                         # per-room member→member hop timestamps
_mm_tripped: "set[str]" = set()                             # rooms with a tripped breaker
MM_MAX, MM_WINDOW = 8, 90.0
_sio = None                                                 # the live socket client (set in main) — for re-join


# ---------------- the ONE structure store (channels.jsonl — session_channels) ----------------
# THE FOLD (channels-fusion increment 2 + 3): an OWUI channel's MEMBERSHIP is a company channel.
# The set of member HANDLES is owned by session_channels (the one named-channel structure store,
# cid == the OWUI channel uuid VERBATIM — deterministic 1:1 mapping, no separate mapping row).
# INC.3 closed the label slot inc.2 deferred: session_channels membership now carries {kind, label}
# on the member sub-record (kind ∈ human|live-session|model — a spawned member is a live-session,
# the operator/RHM is a MODEL). So label/kind are written INTO sc (truth), and the local label map
# is kept ONLY as a fast-path FALLBACK so the live chat path never depends on a store round-trip:
#   membership truth (handle SET + kind + label)  → session_channels  (shared with the fabric)
#   label fast-path fallback                       → owui_room state ("labels": {cid: {handle: label}})
#   roster(cid)                                    → a JOIN (sc handles + label, fallback to local map)
#   reactions (🛑/⏸ control + any emoji)           → sc.react primitive (record-then-act, fail-soft)
# cc_channels stays TRANSPORT-only (push/find) — untouched.
_STORE = None


def _store():
    """The ONE store session_channels (channels.jsonl) lives on — COMPANY_STORE / FsStore.
    Cached: a daemon-lifetime singleton (the fold reads disk every call, so it stays fresh)."""
    global _STORE
    if _STORE is None:
        from store.fs_store import FsStore
        import fabric.config as fcfg
        _STORE = FsStore(fcfg.STORE_DIR)
    return _STORE


# ---------------- state (rooms = {cid: {name}} ; labels = {cid: {handle: label}} ; webhooks = {cid: {label: hook}}) ----------------
def _load_state() -> dict:
    try:
        s = json.load(open(STATE))
    except Exception:
        s = {}
    s.setdefault("rooms", {})
    s.setdefault("webhooks", {})
    s.setdefault("labels", {})
    # migrate a pre-multi-room (flat) state into the HOME room, once.
    if "roster" in s and HOME not in s["rooms"]:
        s["rooms"][HOME] = {"name": "fabric-test", "roster": s.pop("roster")}
        if isinstance(s["webhooks"].get("fork") or s["webhooks"].get("operator"), dict) and HOME not in s["webhooks"]:
            flat = {k: v for k, v in s["webhooks"].items() if isinstance(v, dict) and "id" in v}
            s["webhooks"] = {HOME: flat}
    if HOME not in s["rooms"]:
        s["rooms"][HOME] = {"name": "home", "roster": list(DEFAULT_ROSTER)}
    # FOLD migration (idempotent): lift any legacy in-state "roster" (the OLD private store) into
    # (a) the per-room label map and (b) session_channels membership truth. Survives drift — runs
    # every load, only fills what's missing (the old live daemon may have spawned before restart).
    for cid, room in s["rooms"].items():
        labels = s["labels"].setdefault(cid, {})
        for m in room.get("roster", []):
            labels.setdefault(m["handle"], m["label"])
        room.pop("roster", None)                    # the list is no longer the truth — drop it
    return s


def _save_state() -> None:
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(_state, open(STATE + ".tmp", "w"), indent=2)
    os.replace(STATE + ".tmp", STATE)


def rooms() -> dict:
    return _state["rooms"]


def _ensure_company_channel(cid: str, name: str = "", handles: "list[str] | None" = None) -> None:
    """Ensure a session_channels row exists for this OWUI channel (cid == OWUI uuid VERBATIM),
    then reconcile its membership to include `handles`. Idempotent. registry=None ALWAYS — owui_room
    handles (operator/spawned labels/ch-…) are not all in the agent-session registry; passing one
    would fail-loud and break spawn. Fail-soft: structure-store hiccups must never break the live
    chat path (membership then falls back to the local label map)."""
    try:
        try:
            sc.get_channel(_store(), cid)
        except ValueError:
            sc.create_channel(_store(), name=(name or cid), cid=cid,
                              purpose="OpenWebUI room (owui_room face)", registry=None)
        if handles:
            present = set(sc.channel_members(_store(), cid))
            for h in handles:
                if h and h not in present:
                    sc.add_member(_store(), cid, h, registry=None)
    except Exception as e:
        print(f"  _ensure_company_channel({cid}) soft-fail: {type(e).__name__}: {e}", flush=True)


def roster(cid: str) -> list:
    """The room's members as {handle,label} dicts — a JOIN: handle SET from session_channels
    (membership truth), label from the local map. Falls back to the local label map if the
    structure store is unreachable (the live chat path must never break on a store hiccup)."""
    labels = _state["labels"].setdefault(cid, {})
    try:
        handles = sc.channel_members(_store(), cid)
    except Exception:
        handles = list(labels.keys())               # store unreachable → local map is the fallback
    return [{"handle": h, "label": labels.get(h, h)} for h in handles]


def _member(cid: str, label: str) -> "dict | None":
    return next((m for m in roster(cid) if m["label"] == label), None)


def _add_to_roster(cid: str, handle: str, label: str, kind: str = "live-session") -> None:
    """Add a member: handle → session_channels (truth, now WITH kind+label — fusion inc.3 member-kind),
    label → local map (the fast-path display fallback). Dual-write, fail-soft on the sc side.
    `kind` ∈ human|live-session|model: a spawned room member is a live-session; the operator/RHM is a
    model (an AI brain that is a first-class member). The local label map is KEPT as the fallback —
    membership truth migrates to sc additively, the live chat path never depends on the store."""
    _state["labels"].setdefault(cid, {})[handle] = label
    try:
        _ensure_company_channel(cid, rooms().get(cid, {}).get("name", cid))
        if handle not in set(sc.channel_members(_store(), cid)):
            sc.add_member(_store(), cid, handle, kind=kind, label=label, registry=None)
    except Exception as ex:
        print(f"  _add_to_roster({cid},{handle}) sc soft-fail: {type(ex).__name__}: {ex}", flush=True)
    _save_state()


def _remove_from_roster(cid: str, handle: str) -> None:
    """Remove a member: from session_channels membership + the local label map."""
    _state["labels"].get(cid, {}).pop(handle, None)
    try:
        sc.remove_member(_store(), cid, handle)
    except Exception as e:
        print(f"  _remove_from_roster({cid},{handle}) sc soft-fail: {type(e).__name__}: {e}", flush=True)
    _save_state()


# ---------------- OWUI ----------------
def signin() -> str:
    if not PASSWORD:
        raise SystemExit("set OWUI_PASSWORD")
    r = requests.post(f"{OWUI}/api/v1/auths/signin", json={"email": EMAIL, "password": PASSWORD}, timeout=15)
    r.raise_for_status()
    return r.json()["token"]


def ensure_webhook(cid: str, label: str) -> dict:
    hooks = _state["webhooks"].setdefault(cid, {})
    if label in hooks:
        return hooks[label]
    r = requests.post(f"{OWUI}/api/v1/channels/{cid}/webhooks/create",
                      headers={"Authorization": f"Bearer {_token}"}, json={"name": label}, timeout=15)
    r.raise_for_status()
    wh = r.json()
    hooks[label] = {"id": wh["id"], "token": wh["token"]}
    _save_state()
    return hooks[label]


def webhook_url(cid: str, label: str) -> str:
    wh = ensure_webhook(cid, label)
    return f"{OWUI}/api/v1/channels/webhooks/{wh['id']}/{wh['token']}"


def post_as(cid: str, label: str, content: str) -> None:
    wh = ensure_webhook(cid, label)
    try:
        requests.post(f"{OWUI}/api/v1/channels/webhooks/{wh['id']}/{wh['token']}",
                      json={"content": content}, timeout=15)
    except Exception as e:
        print(f"  post_as({cid},{label}) failed: {e}", flush=True)


def _label_for_webhook_id(cid: str, wid: str) -> "str | None":
    for lb, wh in _state["webhooks"].get(cid, {}).items():
        if wh.get("id") == wid:
            return lb
    return None


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
    req = urllib.request.Request(SUPERVISOR + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def _sup_get_state(supervisor_session: str) -> str:
    req = urllib.request.Request(SUPERVISOR + "/sessions", method="GET")
    with urllib.request.urlopen(req, timeout=5) as r:
        for s in (json.load(r).get("sessions") or []):
            if s.get("id") == supervisor_session:
                return s.get("state", "?")
    return "absent"


# ---------------- OPERATIONS (room-scoped: first arg is the channel id) ----------------
def op_help(cid, *_a) -> str:
    return ("Operator commands (slash in this channel, or ask the operator in plain words):\n"
            "  /members · /status · /spawn <label> [persona…] · /teardown <label> · /rename <old> <new>\n"
            "  /persona <label> <text> · /say <label> <text> · /channel <name> · /channels\n"
            "  /interrupt <label> · /stop · /resume · /panel · /help\n"
            "Stop a member by tapping 🛑 on its message; ⏸ to pause. Members address each other with @name.")


def op_members(cid, *_a) -> str:
    lines = []
    for m in roster(cid):
        reg = None
        try:
            reg = cc_channels.find(m["handle"])
        except Exception:
            pass
        if reg:
            t = reg.get("transport") or "channel"
            status = t
            if t == "supervised":
                try:
                    status = f"supervised/{_sup_get_state(reg.get('supervisor_session'))}"
                except Exception:
                    status = "supervised"
            else:
                status = "live"
            lines.append(f"  • {m['label']}  [{status}]  ({m['handle']})")
        else:
            lines.append(f"  • {m['label']}  [offline]  ({m['handle']})")
    return f"Members in {rooms().get(cid,{}).get('name',cid)}:\n" + ("\n".join(lines) if lines else "  (none)")


def op_spawn(cid, label: str = "", *persona_words) -> str:
    label = (label or "").strip()
    if not label:
        return "usage: /spawn <label> [persona…]"
    if _member(cid, label):
        return f"member '{label}' already here."
    brief = " ".join(persona_words).strip() or f"a sharp, concise member named {label}"
    hook = webhook_url(cid, label)
    persona = (
        f"You are '{label}', an AI MEMBER of a live multi-party room (the human Tim + other AI members). "
        f"To SPEAK in the room run a Bash command exactly like:\n"
        f"  curl -s -X POST '{hook}' -H 'Content-Type: application/json' -d '{{\"content\":\"<your message>\"}}'\n"
        f"That curl is the ONLY way the room hears you — run it whenever you want to say something. To address "
        f"another member, start your message with '@theirname'. Messages arrive to you as your turns. "
        f"Your role: {brief}. Keep posts short. RIGHT NOW introduce yourself in one short sentence via that curl."
    )
    rec = _sup("/bridge-session", {"operator_consent": True, "name": label, "source": "owui-room",
                                   "prompt": persona}).get("session", {})
    sid = rec.get("id")
    if not sid:
        return f"spawn '{label}' failed — no session id."
    cc_clone.register_supervised_member(handle=label, session_id=sid, supervisor_session=sid,
                                        cwd=REPO, description=f"room member: {brief[:60]}")
    _add_to_roster(cid, label, label)
    return f"spawned '{label}' ({sid}) — in this room, introducing itself now."


def op_teardown(cid, label: str = "", *_a) -> str:
    m = _member(cid, label)
    if not m:
        return f"no member '{label}' here."
    msg = []
    try:
        reg = cc_channels.find(m["handle"])
    except Exception:
        reg = None
    if reg and reg.get("transport") == "supervised" and reg.get("supervisor_session"):
        try:
            _sup("/teardown", {"session": reg["supervisor_session"]}, timeout=20); msg.append("session torn down")
        except Exception as e:
            msg.append(f"teardown error: {e}")
    try:
        cc_clone._deregister_member(m["handle"]); msg.append("deregistered")
    except Exception as e:
        msg.append(f"dereg error: {e}")
    _remove_from_roster(cid, m["handle"])
    return f"removed '{label}' — " + "; ".join(msg)


def op_rename(cid, old: str = "", new: str = "", *_a) -> str:
    m = _member(cid, old)
    if not m:
        return f"no member '{old}'."
    if _member(cid, new):
        return f"'{new}' already exists."
    _state["labels"].setdefault(cid, {})[m["handle"]] = new   # relabel in the map (handle unchanged)
    _save_state()
    return f"renamed '{old}' → '{new}' (new posts use the new identity)."


def op_persona(cid, label: str = "", *words) -> str:
    m = _member(cid, label)
    if not m:
        return f"no member '{label}'."
    text = " ".join(words).strip()
    if not text:
        return "usage: /persona <label> <new role>"
    _route_q.put((m["handle"], f"[operator re-brief] From now your role is: {text}"))
    return f"re-briefed '{label}'."


def op_say(cid, label: str = "", *words) -> str:
    m = _member(cid, label)
    if not m:
        return f"no member '{label}'."
    _route_q.put((m["handle"], " ".join(words)))
    return f"sent to '{label}'."


def op_channel(cid, name: str = "", *_a) -> str:
    name = (name or "").strip()
    if not name:
        return "usage: /channel <name>"
    try:
        ch = create_owui_channel(name)
        ncid = ch.get("id")
        rooms()[ncid] = {"name": name}                    # register it as a LIVE room immediately
        _state["labels"].setdefault(ncid, {})
        _ensure_company_channel(ncid, name)               # mirror it as a company channel (membership truth)
        ensure_webhook(ncid, "operator")
        _save_state()
        if _sio is not None:                               # re-join so the socket receives the new channel's events
            try:
                _sio.emit("join-channels", {"auth": {"token": _token}})
            except Exception:
                pass
        return f"created channel '{name}' (id {ncid}) — it's a live room now; spawn members into it there."
    except Exception as e:
        return f"channel create failed: {e}"


def op_channels(cid, *_a) -> str:
    try:
        chs = list_owui_channels()
        out = []
        for c in chs:
            tag = " [room]" if c.get("id") in rooms() else ""
            out.append(f"  • {c.get('name')}{tag}  (id {c.get('id')})")
        return "Channels:\n" + "\n".join(out) if out else "Channels: (none)"
    except Exception as e:
        return f"list channels failed: {e}"


def op_interrupt(cid, label: str = "", *_a) -> str:
    m = _member(cid, label)
    if not m:
        return f"no member '{label}'."
    try:
        reg = cc_channels.find(m["handle"])
    except Exception:
        reg = None
    if not reg or reg.get("transport") != "supervised" or not reg.get("supervisor_session"):
        return f"'{label}' is not supervised — nothing to interrupt."
    try:
        _sup("/interrupt", {"session": reg["supervisor_session"]}, timeout=15)
        return f"⏸ interrupted '{label}' (turn halted; member present)."
    except Exception as e:
        return f"interrupt '{label}' failed: {e}"


def op_stop(cid, *_a) -> str:
    hit = []
    for m in roster(cid):
        try:
            reg = cc_channels.find(m["handle"])
            if reg and reg.get("transport") == "supervised" and reg.get("supervisor_session"):
                _sup("/interrupt", {"session": reg["supervisor_session"]}, timeout=10); hit.append(m["label"])
        except Exception:
            pass
    return f"⏹ STOP — interrupted: {', '.join(hit) if hit else '(none running)'}"


def op_panel(cid, *_a) -> str:
    lines = ["🎛 Control panel.  TAP a reaction on a member's message:  🛑 = stop  ·  ⏸ = pause.  Or:"]
    for m in roster(cid):
        lb = m["label"]
        lines.append(f"  {lb}: (lead session)" if lb == "fork" else f"  {lb}:   ⏸ /interrupt {lb}    🛑 /teardown {lb}")
    lines.append("  ALL:  /stop  ·  /status  ·  /members  ·  /help")
    return "\n".join(lines)


def op_status(cid, *_a) -> str:
    tripped = "TRIPPED — /resume to clear" if cid in _mm_tripped else "ok"
    return "\n".join([op_members(cid), "", op_channels(cid), "",
                      f"member↔member breaker (this room): {tripped} ({len(_mm_window.get(cid, []))} recent hops)"])


def op_resume(cid, *_a) -> str:
    _mm_tripped.discard(cid)
    _mm_window.pop(cid, None)
    return "member↔member routing resumed for this room."


def op_spawn_operator(cid, *_a) -> str:
    if _member(cid, "operator"):
        return "operator already here."
    hook = webhook_url(cid, "operator")
    py, cli = sys.executable, os.path.join(REPO, "ops", "owui_room.py")
    persona = (
        "You are 'operator', the room's OPERATOR — you turn Tim's plain-language requests into fabric "
        "actions. You have a Bash shell. To ACT, run (one Bash command):\n"
        f"  {py} {cli} op <command> [args] --channel {cid}\n"
        "Commands: members | status | spawn <label> <role…> | teardown <label> | rename <old> <new> | "
        "persona <label> <text> | say <label> <text> | channel <name> | channels | interrupt <label> | stop | help.\n"
        f"e.g. 'spin up an analyst' → {py} {cli} op spawn analyst market analyst --channel {cid}\n"
        f"     'who's here?'        → {py} {cli} op members --channel {cid}\n"
        "The command's RESULT is posted into the room automatically — do NOT repeat it. If ambiguous, ask ONE "
        f"short question via your webhook: curl -s -X POST '{hook}' -H 'Content-Type: application/json' "
        "-d '{\"content\":\"…\"}'. Be terse. RIGHT NOW post 'operator online — tell me what to build' via that curl."
    )
    rec = _sup("/bridge-session", {"operator_consent": True, "name": "operator", "source": "owui-room",
                                   "prompt": persona}).get("session", {})
    sid = rec.get("id")
    if not sid:
        return "operator spawn failed."
    cc_clone.register_supervised_member(handle="operator", session_id=sid, supervisor_session=sid,
                                        cwd=REPO, description="the room operator (NL → ops)")
    _add_to_roster(cid, "operator", "operator", kind="model")   # the operator/RHM is a MODEL member (inc.3)
    return "operator spawned — talk to it in plain language and it runs the ops."


OPS = {"help": op_help, "members": op_members, "status": op_status, "spawn": op_spawn,
       "teardown": op_teardown, "rename": op_rename, "persona": op_persona, "say": op_say,
       "channel": op_channel, "channels": op_channels, "interrupt": op_interrupt, "stop": op_stop,
       "resume": op_resume, "panel": op_panel, "spawn_operator": op_spawn_operator}


def dispatch(op: str, args: list, cid: str) -> str:
    fn = OPS.get(op)
    if not fn:
        return f"unknown op '{op}'. /help for commands."
    try:
        with _lock:
            return fn(cid, *args)
    except Exception as e:
        return f"op '{op}' error: {type(e).__name__}: {e}"


# ---------------- inbound: deliver to a member (string-only meta) ----------------
def _route_worker() -> None:
    while True:
        handle, content = _route_q.get()
        meta = {"from": "tim", "thread": "owui-room"}            # STRING-ONLY
        for attempt in range(1, 31):
            try:
                if cc_channels.push(handle, content, meta=meta, base_timeout=12).get("ok"):
                    print(f"  → delivered to {handle} try {attempt}", flush=True); break
            except cc_channels.ChannelError as e:
                print(f"  deliver {handle} err {attempt}: {e}", flush=True)
            except Exception as e:
                print(f"  deliver {handle} unexpected {attempt}: {type(e).__name__}", flush=True)
            time.sleep(2)
        else:
            print(f"  ✗ gave up on {handle}", flush=True)
        _route_q.task_done()


def _deliver(cid: str, handle: str, label_for_reply: str, body: str) -> None:
    """Queue a message to a member, wrapping in the reply instruction for THIS room's webhook."""
    try:
        hook = webhook_url(cid, label_for_reply)
    except Exception:
        hook = ""
    _route_q.put((handle, f"[room message — to reply, POST {{\"content\":\"...\"}} to {hook}] {body}"))


# ---------------- reaction buttons ----------------
_TEARDOWN_EMOJI = ("🛑", "❌", "⛔", "octagonal_sign", "no_entry", "cross_mark", "stop")
_INTERRUPT_EMOJI = ("⏸", "⏸️", "✋", "🤚", "pause_button", "double_vertical_bar", "raised_hand")


def _classify_reaction(emoji: str) -> "str | None":
    """PURE classifier — map a reaction emoji to a control intent (teardown|interrupt|None).
    No I/O, no store, never raises: the live operator gesture (🛑/⏸ on the phone) must resolve to an
    action even if every other subsystem is down."""
    e = (emoji or "").lower()
    if emoji in _TEARDOWN_EMOJI or any(t in e for t in _TEARDOWN_EMOJI):
        return "teardown"
    if emoji in _INTERRUPT_EMOJI or any(t in e for t in _INTERRUPT_EMOJI):
        return "interrupt"
    return None


def handle_reaction(cid: str, msg: dict) -> None:
    """RECORD-THEN-ACT (fusion inc.3): a reaction is now RECORDED as a first-class CHANNEL PRIMITIVE
    event on session_channels (sc.react), so the room's reactions are legible in the one fold rather
    than living only on the socket. The control DECISION stays LOCAL (_classify_reaction over the
    emoji tuples) BY DESIGN — making teardown depend on reading the fold would re-couple the live
    operator gesture to a store round-trip, which the live path forbids. So: classify purely, record
    best-effort (fail-soft), then run the supervisor action UNCONDITIONALLY — a store hiccup can NEVER
    block Tim stopping a runaway member (the live path is sacred). The OWUI message id is the opaque
    `message` ref (id-agnostic primitive).

    NEEDS-LIVE-VERIFICATION: the OWUI reaction payload's message-id key is inferred (`id`/`message_id`)
    — the original socket handler never extracted it. If both are absent the reaction is NOT recorded
    (logged loud, never silent), but control still fires. Confirm the real key against a live socket
    event and pin it here."""
    emoji = msg.get("name") or ""
    wid = ((msg.get("meta") or {}).get("webhook") or {}).get("id")
    label = _label_for_webhook_id(cid, wid) if wid else None
    if not label or not _member(cid, label):
        return
    intent = _classify_reaction(emoji)            # pure — decided BEFORE any I/O
    # RECORD (best-effort, fail-soft): land the reaction on the channel primitive. NEVER gate the
    # control action on this succeeding. An absent msg-id is logged loud (no-silent-failure law).
    msg_ref = str(msg.get("id") or msg.get("message_id") or "")
    if not msg_ref:
        print(f"  handle_reaction: reaction {emoji!r} on {label} has no message id "
              f"(keys={sorted(msg)}) — NOT recorded to the primitive; control still fires.", flush=True)
    else:
        try:
            sc.react(_store(), cid, msg_ref, label, emoji)
        except Exception as ex:
            print(f"  handle_reaction sc.react soft-fail: {type(ex).__name__}: {ex}", flush=True)
    # ACT (unconditional — reads the classified intent, runs the proven supervisor control):
    if intent == "teardown":
        print(f"  reaction {emoji} on {label} → TEARDOWN", flush=True)
        post_as(cid, "operator", f"🛑 ({label}) — " + dispatch("teardown", [label], cid))
    elif intent == "interrupt":
        print(f"  reaction {emoji} on {label} → INTERRUPT", flush=True)
        post_as(cid, "operator", f"⏸ ({label}) — " + dispatch("interrupt", [label], cid))


# ---------------- member↔member ----------------
def handle_member_post(cid: str, m: dict) -> None:
    wid = ((m.get("meta") or {}).get("webhook") or {}).get("id")
    sender = _label_for_webhook_id(cid, wid) if wid else None
    if not sender or not _member(cid, sender) or sender == "operator":
        return
    text = (m.get("content") or "").strip()
    low = text.lower()
    target = None
    for cand in roster(cid):
        lb = cand["label"]
        if low.startswith((f"@{lb.lower()} ", f"@{lb.lower()},", f"{lb.lower()}:", f"{lb.lower()}, ")):
            target = lb; break
    if not target or target == sender or target == "operator" or not _member(cid, target):
        return
    if cid in _mm_tripped:
        return
    win = _mm_window.setdefault(cid, deque(maxlen=64))
    now = time.time()
    while win and now - win[0] > MM_WINDOW:
        win.popleft()
    if len(win) >= MM_MAX:
        _mm_tripped.add(cid)
        post_as(cid, "operator", f"⏸ member↔member breaker TRIPPED ({MM_MAX}/{int(MM_WINDOW)}s) — loop paused. /resume or 🛑 a member.")
        return
    win.append(now)
    if text:
        _deliver(cid, _member(cid, target)["handle"], target, f"(from {sender}) {text}")
        print(f"  member→member [{rooms().get(cid,{}).get('name',cid)}]: {sender} → {target}", flush=True)


# ---------------- op-server / CLI ----------------
def _parse_channel(args: list) -> "tuple[list, str]":
    if "--channel" in args:
        i = args.index("--channel")
        cid = args[i + 1] if i + 1 < len(args) else HOME
        return args[:i] + args[i + 2:], cid
    return args, HOME


class _OpHandler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"{}")
            op = body.get("op", ""); args = body.get("args", []) or []
            args, cid = _parse_channel(list(args))
            cid = body.get("channel") or cid
            result = dispatch(op, args, cid)
            post_as(cid, "operator", result)
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
    for cid, room in rooms().items():
        # FOLD reconcile: ensure each room is a company channel with its known handles as members
        # (idempotent; lifts the migrated label-map handles into session_channels membership truth).
        handles = list(_state["labels"].get(cid, {}).keys())
        _ensure_company_channel(cid, room.get("name", cid), handles)
        for m in roster(cid):
            ensure_webhook(cid, m["label"])
        ensure_webhook(cid, "operator")
    _save_state()
    threading.Thread(target=_route_worker, daemon=True).start()
    _start_op_server()

    global _sio
    sio = socketio.Client(reconnection=True, reconnection_attempts=0, request_timeout=20)
    _sio = sio

    @sio.event
    def connect():
        print("connected → joining channels", flush=True)
        sio.emit("user-join", {"auth": {"token": _token}})
        sio.emit("join-channels", {"auth": {"token": _token}})

    @sio.on("events:channel")
    def on_channel(data):
        try:
            cid = (data or {}).get("channel_id")
            if cid not in rooms():                              # only handle channels that are registered rooms
                return
            d = (data.get("data") or {})
            if d.get("type") == "message:reaction:add":
                handle_reaction(cid, d.get("data") or {})
                return
            if d.get("type") != "message":
                return
            m = d.get("data") or {}
            mid = m.get("id")
            if not mid or mid in _seen:
                return
            if m.get("meta"):                                   # a member's own post → maybe member↔member
                _seen.add(mid); handle_member_post(cid, m); return
            text = (m.get("content") or "").strip()
            if not text:
                _seen.add(mid); return
            _seen.add(mid)
            if text.startswith("/"):                            # SLASH command, scoped to THIS channel
                parts = text[1:].split()
                op = parts[0] if parts else "help"
                post_as(cid, "operator", dispatch(op, parts[1:], cid))
                print(f"  slash [{rooms()[cid]['name']}]: /{op}", flush=True); return
            rt = m.get("reply_to_message") or {}
            target = ((rt.get("user") or {}).get("name")) or (((rt.get("meta") or {}).get("webhook") or {}).get("name"))
            low = text.lower()
            wants_op = (target == "operator") or low.startswith(("operator", "@operator", "op,", "op:"))
            if wants_op and _member(cid, "operator"):
                _deliver(cid, _member(cid, "operator")["handle"], "operator", text)
                print("  → operator (NL)", flush=True); return
            if target and _member(cid, target) and target != "operator":
                _deliver(cid, _member(cid, target)["handle"], target, text)
                print(f"  → {target}", flush=True)
            else:
                for mm in roster(cid):
                    if mm["label"] != "operator":
                        _deliver(cid, mm["handle"], mm["label"], text)
                print("  → broadcast", flush=True)
        except Exception as e:
            print(f"  event error: {e}", flush=True)

    names = [r["name"] for r in rooms().values()]
    print(f"owui-rooms: {len(rooms())} room(s) {names} · op-console · home={HOME}", flush=True)
    sio.connect(OWUI, socketio_path=SIO_PATH, transports=["websocket"], auth={"token": _token})
    sio.wait()


def cli(argv):
    op = argv[0] if argv else "help"
    rest, cid = _parse_channel(argv[1:])
    port = (json.load(open(STATE)) if os.path.exists(STATE) else {}).get("op_port", OP_PORT)
    req = urllib.request.Request(f"http://127.0.0.1:{port}/op",
                                 data=json.dumps({"op": op, "args": rest, "channel": cid}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        print(json.load(r).get("result", ""))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "op":
        cli(sys.argv[2:])
    else:
        raise SystemExit(main())
