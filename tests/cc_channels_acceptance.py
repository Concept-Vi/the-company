"""tests/cc_channels_acceptance.py — the cross-session CHANNEL router (runtime/cc_channels.py).
Proves presence-pruning, find-resolution (fail-loud on ambiguous/none), threading, the mail record,
and the reply-routing loop (push-back to the thread originator) — all WITHOUT launching a real claude
(fake registration files + a throwaway local HTTP server standing in for a channel port)."""
import json, os, sys, tempfile, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from runtime import cc_channels as cc

PASS, FAIL = [], []
def check(n, c, d=""):
    (PASS if c else FAIL).append(n); print(f"  {'PASS' if c else 'FAIL'}  {n}" + (f"  — {d}" if d and not c else ""))
def raises(fn, sub=""):
    try: fn(); return False
    except cc.ChannelError as e: return sub in str(e) if sub else True
    except Exception: return False

# --- a throwaway channel port: records what gets POSTed, so we can assert injection ---
class _Rx(BaseHTTPRequestHandler):
    received = []
    def log_message(self, *a): pass
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try: _Rx.received.append(json.loads(self.rfile.read(n) or b"{}"))
        except ValueError: pass
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
srv = ThreadingHTTPServer(("127.0.0.1", 0), _Rx)
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

tmp = tempfile.mkdtemp()
cc.CHAN_DIR = tmp
cc.MAIL_LOG = os.path.join(tmp, "_mail.jsonl")
cc.THREADS = os.path.join(tmp, "_threads.json")

def reg(handle, cwd, pid, port, desc=""):
    json.dump({"handle": handle, "session_id": "", "cwd": cwd, "description": desc, "pid": pid,
               "port": port, "started": "2026-06-14T00:00:00"}, open(os.path.join(tmp, handle + ".json"), "w"))

# --- presence + pruning ---
reg("ch-live", "/home/tim/a", os.getpid(), PORT, "the live one")   # alive (our pid)
reg("ch-dead", "/home/tim/b", 999999, 5, "the dead one")           # dead pid
live = cc.live_sessions()
ids = {r["handle"] for r in live}
check("1 live_sessions returns the alive session", "ch-live" in ids)
check("2 live_sessions PRUNES the dead session (real presence)", "ch-dead" not in ids)
check("3 the dead registration file was removed", not os.path.exists(os.path.join(tmp, "ch-dead.json")))

# --- find resolution + fail-loud ---
check("4 find by handle", cc.find("ch-live")["handle"] == "ch-live")
check("5 find by exact cwd", cc.find("/home/tim/a")["handle"] == "ch-live")
check("6 find by description substring", cc.find("live one")["handle"] == "ch-live")
check("7 find unknown FAILS LOUD", raises(lambda: cc.find("nope"), "matched"))
reg("ch-live2", "/home/tim/a", os.getpid(), PORT, "second in same cwd")
check("8 find ambiguous cwd FAILS LOUD (never message the wrong session)",
      raises(lambda: cc.find("/home/tim/a"), "matches"))
os.unlink(os.path.join(tmp, "ch-live2.json"))

# --- send: opens a thread, records to mail, pushes to the port ---
_Rx.received.clear()
res = cc.send("ch-live", "hello fabric", frm="tester", topic="t1")
time.sleep(0.3)
check("9 send returned ok + a thread id", res.get("ok") and res.get("thread"))
check("10 send PUSHED to the channel port (injection)", len(_Rx.received) == 1 and "hello fabric" in _Rx.received[0]["content"])
check("11 the push carried from+thread meta", _Rx.received[0]["meta"].get("from") == "tester")
check("12 send recorded the message in the mail log", any(m["kind"]=="message" and m["text"]=="hello fabric" for m in cc.mail(thread=res["thread"])))
check("13 the thread originator was recorded (tester)", cc.thread_info(res["thread"]).get("originator") == "tester")

# --- route_reply: records + pushes back to the originator's LIVE session ---
# Make the originator a LIVE session (ch-live, on our port) so the reply can push back to it.
res2 = cc.send("ch-live", "ping from a live originator", frm="ch-live", topic="t2")
time.sleep(0.2)
_Rx.received.clear()                                   # drop the send's push; we assert the REPLY push
rr = cc.route_reply("ch-other", res2["thread"], "reply text back")
time.sleep(0.3)
check("14 route_reply recorded the reply in the mail log", any(m["kind"]=="reply" and m["text"]=="reply text back" for m in cc.mail(thread=res2["thread"])))
check("15 route_reply PUSHED the reply back into the originator's live session (no polling)",
      rr.get("delivered") and len(_Rx.received) == 1 and "reply text back" in _Rx.received[0]["content"])
# originator = fabric (an agent, not a live session) → recorded, not pushed
cc.open_thread("t-fabric", "fabric", topic="x")
rr2 = cc.route_reply("ch-other", "t-fabric", "to the fabric")
check("16 a reply whose originator is the fabric is recorded, not pushed (agent reads the log)",
      rr2.get("recorded") and not rr2.get("delivered"))

# --- push to a dead port FAILS LOUD ---
reg("ch-deadport", "/home/tim/c", os.getpid(), 6, "dead port")
check("17 push to an unreachable port FAILS LOUD", raises(lambda: cc.send("ch-deadport", "x"), "failed"))


# ════════════════════════════════════════════════════════════════════════════════════════════════
# NAMED-CHANNEL REGISTRY (channels as named managed groups — create/list/add/remove/archive)
# ════════════════════════════════════════════════════════════════════════════════════════════════
cc.CHANNELS_DIR = os.path.join(tmp, "_channels")        # point the registry at the throwaway tmp dir

c1 = cc.create_channel("Build Coordination", purpose="overnight build", coordinator="ch-live")
check("18 create_channel returns a record with id+name+empty roster",
      c1["id"] == "build-coordination" and c1["name"] == "Build Coordination" and c1["members"] == []
      and c1["status"] == "active")
check("19 create_channel persisted the record to _channels/<id>.json",
      os.path.exists(os.path.join(cc.CHANNELS_DIR, "build-coordination.json")))
check("20 create_channel DUP-name FAILS LOUD (no silent overwrite)",
      raises(lambda: cc.create_channel("Build Coordination"), "already exists"))

cc.create_channel("Memory Lane", purpose="recall work")
chans = cc.list_channels()
check("21 list_channels returns both active channels",
      {c["id"] for c in chans} == {"build-coordination", "memory-lane"})

cc.add_member("Build Coordination", "ch-live")
cc.add_member("build-coordination", "ch-other")          # add by id too (slug-stable)
check("22 add_member roster reflects both members",
      cc.channel_members("Build Coordination") == ["ch-live", "ch-other"])
check("23 add_member DUPLICATE member FAILS LOUD (no silent no-op)",
      raises(lambda: cc.add_member("Build Coordination", "ch-live"), "already a member"))
check("24 add_member to a MISSING channel FAILS LOUD",
      raises(lambda: cc.add_member("no-such-channel", "ch-live"), "no channel"))

# member-in-multiple-channels: ch-live joins a second channel
cc.add_member("Memory Lane", "ch-live")
check("25 a member can be in SEVERAL channels at once",
      "ch-live" in cc.channel_members("Build Coordination") and "ch-live" in cc.channel_members("Memory Lane"))

cc.remove_member("Build Coordination", "ch-other")
check("26 remove_member drops the member from the roster",
      cc.channel_members("Build Coordination") == ["ch-live"])
check("27 remove_member of a NON-member FAILS LOUD",
      raises(lambda: cc.remove_member("Build Coordination", "ch-other"), "not a member"))

cc.archive_channel("Memory Lane")
check("28 archive_channel flips status (NOT a delete — record survives)",
      cc.list_channels(include_archived=True)[0].get("status") == "archived" or
      any(c["id"] == "memory-lane" and c["status"] == "archived"
          for c in cc.list_channels(include_archived=True)))
check("29 archived channels are EXCLUDED from list_channels by default",
      "memory-lane" not in {c["id"] for c in cc.list_channels()})
check("30 archived channels are INCLUDED with include_archived=True",
      "memory-lane" in {c["id"] for c in cc.list_channels(include_archived=True)})
check("31 add_member to an ARCHIVED channel FAILS LOUD",
      raises(lambda: cc.add_member("Memory Lane", "ch-x"), "archived"))
check("32 channel_members on a MISSING channel FAILS LOUD",
      raises(lambda: cc.channel_members("ghost"), "no channel"))


# ════════════════════════════════════════════════════════════════════════════════════════════════
# UNIFIED PER-MEMBER TRANSPORT DISPATCH (transport: channel | supervised)
# ════════════════════════════════════════════════════════════════════════════════════════════════

# --- back-compat: a portful / no-transport registration is a "channel" member ---
check("33 a portful no-transport reg defaults to transport 'channel'",
      cc._transport_of({"handle": "x", "port": 5}) == "channel")
check("34 an explicit transport='channel' reg is a channel member",
      cc._transport_of({"handle": "x", "transport": "channel"}) == "channel")
check("35 an explicit transport='supervised' reg is a supervised member",
      cc._transport_of({"handle": "x", "transport": "supervised"}) == "supervised")
_Rx.received.clear()
res_bc = cc.send("ch-live", "back-compat channel dispatch", frm="tester")
time.sleep(0.2)
check("36 transport back-compat: a channel member still dispatches over HTTP to its port",
      len(_Rx.received) == 1 and "back-compat channel dispatch" in _Rx.received[0]["content"]
      and res_bc.get("transport") == "channel")


# --- a FAITHFUL MOCK SUPERVISOR standing in for session_supervisor ---
# Mirrors the real surface on the axes that matter for the reply-fold:
#   /sessions : {sessions:[{id, state}]}                       (live_sessions presence probe)
#   /watch    : REPLAYS s.events on connect (real L1485), THEN streams live events (real fans on close)
#   /inject   : threads body `source` into an `injected{source}` event (real L1606→L1091) THEN a `done`
# The replay is what makes the stale-done mis-route path testable: a session a PRIOR path drove carries
# a stale done in its replay, and the faithful mock replays it on every /watch connect.
import queue as _queue
class _MockSupervisor(BaseHTTPRequestHandler):
    states = {}           # session_id -> "idle"|"busy"|"closed"
    history = {}          # session_id -> list[event]   (REPLAYED on /watch connect, like real s.events)
    watch_q = {}          # session_id -> Queue[event]  (LIVE events streamed after replay)
    injects = []          # every /inject body received (assert the dispatch shape)
    def log_message(self, *a): pass
    def _json(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        from urllib.parse import urlparse as _up, parse_qs as _pq
        u = _up(self.path)
        if u.path == "/sessions":
            recs = [{"id": sid, "state": st} for sid, st in _MockSupervisor.states.items()]
            self._json(200, {"sessions": recs}); return
        if u.path == "/watch":
            sid = (_pq(u.query).get("session") or [""])[0]
            q = _MockSupervisor.watch_q.setdefault(sid, _queue.Queue())
            self.send_response(200); self.send_header("Content-Type", "application/x-ndjson")
            self.send_header("Connection", "close"); self.end_headers()
            try:
                # REPLAY history first (mirrors the real supervisor's list(s.events) on connect)
                for ev in list(_MockSupervisor.history.get(sid, [])):
                    self.wfile.write((json.dumps(ev) + "\n").encode()); self.wfile.flush()
                # then live events
                while True:
                    ev = q.get(timeout=10)
                    self.wfile.write((json.dumps(ev) + "\n").encode()); self.wfile.flush()
                    if ev.get("type") == "closed":
                        break
            except (_queue.Empty, BrokenPipeError, ConnectionResetError):
                pass
            return
        self._json(404, {"error": "unknown"})
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try: body = json.loads(self.rfile.read(n) or b"{}")
        except ValueError: body = {}
        u = self.path.split("?")[0]
        if u == "/inject":
            _MockSupervisor.injects.append(body)
            sid = body.get("session")
            q = _MockSupervisor.watch_q.setdefault(sid, _queue.Queue())
            # the real turn order: fan `injected{source}` (L1091), then the turn's `done` (L1039)
            q.put({"type": "injected", "source": body.get("source") or "http",
                   "chars": len(body.get("message") or "")})
            q.put({"type": "done", "result": f"SUPERVISED REPLY to: {body.get('message')}",
                   "is_error": False})
            self._json(200, {"ok": True}); return
        self._json(404, {"error": "unknown"})

msup = ThreadingHTTPServer(("127.0.0.1", 0), _MockSupervisor)
SUP_PORT = msup.server_address[1]
SUP_BASE = f"http://127.0.0.1:{SUP_PORT}"
threading.Thread(target=msup.serve_forever, daemon=True).start()

def sup_reg(handle, supervisor_session, cwd="/home/tim/sup", desc="", base=SUP_BASE):
    json.dump({"handle": handle, "session_id": "s-" + handle, "transport": "supervised",
               "supervisor_session": supervisor_session, "supervisor_base": base,
               "cwd": cwd, "description": desc, "started": "2026-06-14T00:00:00"},
              open(os.path.join(tmp, handle + ".json"), "w"))

# register a live supervised member (the supervisor reports its session idle)
_MockSupervisor.states["sv-1"] = "idle"
sup_reg("ch-sup", "sv-1", desc="the supervised clone")

# --- live_sessions is transport-aware: supervised members appear when the supervisor says non-closed ---
live2 = cc.live_sessions()
check("37 live_sessions includes a supervised member the supervisor reports live",
      any(r["handle"] == "ch-sup" for r in live2))

# --- supervised dispatch: send to the supervised member → POST /inject + reply folded back ---
# The ASKER is a live channel member (ch-live on our _Rx PORT) so the folded reply can push back to it.
_Rx.received.clear()
_MockSupervisor.injects.clear()
res_sup = cc.send("ch-sup", "hello supervised", frm="ch-live", topic="t-sup")
# wait for: the /inject to land AND the watcher to fold the done back to ch-live's port
for _ in range(60):
    if _MockSupervisor.injects and _Rx.received:
        break
    time.sleep(0.1)
check("38 supervised dispatch POSTed to the supervisor /inject (correct session + message)",
      len(_MockSupervisor.injects) == 1 and _MockSupervisor.injects[0]["session"] == "sv-1"
      and _MockSupervisor.injects[0]["message"] == "hello supervised")
check("39 supervised send reported transport='supervised'", res_sup.get("transport") == "supervised")
check("40 the supervised reply was folded into the mail log (route_reply)",
      any(m["kind"] == "reply" and "SUPERVISED REPLY" in m.get("text", "")
          for m in cc.mail(thread=res_sup["thread"])))
check("41 the supervised reply was PUSHED BACK into the asker's live session (no polling)",
      any("SUPERVISED REPLY to: hello supervised" in (r.get("content") or "") for r in _Rx.received))

# --- STALE-REPLAY mis-route guard (the faithful-mock path): a session a PRIOR path drove carries a
#     stale `done` in its /watch replay. A fresh watcher must DISCARD it (only fold a done preceded by
#     OUR injected{source:channel-fabric} marker), never mis-route the stale result to a pending thread.
# Register a NEW supervised member whose supervisor history already holds a stale (foreign) turn.
_MockSupervisor.states["sv-stale"] = "idle"
_MockSupervisor.history["sv-stale"] = [
    {"type": "injected", "source": "http", "chars": 3},                 # a PRIOR path's inject (msg_clone)
    {"type": "done", "result": "STALE FOREIGN REPLY", "is_error": False},  # its stale done, replayed
]
sup_reg("ch-stale", "sv-stale", desc="supervised w/ stale replay history")
_Rx.received.clear()
_MockSupervisor.injects.clear()
# dispatch via the channel layer: watcher connects → REPLAYS the stale done first, then our turn runs.
res_stale = cc.send("ch-stale", "fresh question", frm="ch-live", topic="t-stale")
for _ in range(60):
    if _MockSupervisor.injects and any("fresh question" in (r.get("content") or "") for r in _Rx.received):
        break
    time.sleep(0.1)
mailed_stale = cc.mail(thread=res_stale["thread"])
check("42 stale replayed done is DISCARDED — never folded to the pending thread (no mis-route)",
      not any("STALE FOREIGN REPLY" in m.get("text", "") for m in mailed_stale)
      and not any("STALE FOREIGN REPLY" in (r.get("content") or "") for r in _Rx.received))
check("43 the FRESH supervised reply still folds correctly past the stale replay",
      any(m["kind"] == "reply" and "SUPERVISED REPLY to: fresh question" in m.get("text", "")
          for m in mailed_stale)
      and any("SUPERVISED REPLY to: fresh question" in (r.get("content") or "") for r in _Rx.received))

# --- STALE-OWN-NONCE reconnect guard (the watcher-reconnect path): a member's history holds a PRIOR
#     OWN fabric turn (injected{source: channel-fabric:OLDNONCE} + its done). On a watcher reconnect a
#     fresh dispatch mints a NEW nonce; the replayed old-nonce injected must NOT arm (nonce mismatch),
#     so the prior-own done is DISCARDED and the CURRENT turn's real reply is never dropped/mis-routed.
_MockSupervisor.states["sv-own"] = "idle"
_MockSupervisor.history["sv-own"] = [
    {"type": "injected", "source": cc.CHANNEL_FABRIC_SOURCE + ":OLDNONCEdeadbeef", "chars": 5},
    {"type": "done", "result": "STALE OWN REPLY (old nonce)", "is_error": False},
]
sup_reg("ch-own", "sv-own", desc="supervised w/ a prior OWN fabric turn in replay")
_Rx.received.clear()
_MockSupervisor.injects.clear()
res_own = cc.send("ch-own", "current question", frm="ch-live", topic="t-own")
for _ in range(60):
    if _MockSupervisor.injects and any("current question" in (r.get("content") or "") for r in _Rx.received):
        break
    time.sleep(0.1)
mailed_own = cc.mail(thread=res_own["thread"])
check("44 a replayed PRIOR-OWN done (old nonce) is DISCARDED — current turn's reply not dropped/mis-routed",
      not any("STALE OWN REPLY" in m.get("text", "") for m in mailed_own)
      and not any("STALE OWN REPLY" in (r.get("content") or "") for r in _Rx.received))
check("45 the CURRENT supervised reply folds correctly past the prior-own replay",
      any(m["kind"] == "reply" and "SUPERVISED REPLY to: current question" in m.get("text", "")
          for m in mailed_own)
      and any("SUPERVISED REPLY to: current question" in (r.get("content") or "") for r in _Rx.received))

# --- mixed-member broadcast: one broadcast fans across a channel member AND a supervised member ---
_Rx.received.clear()
_MockSupervisor.injects.clear()
res_mix = cc.send("ch-live", "X", frm="fabric")          # warm; then broadcast
bres = []
import time as _t2
gthread = f"g-mix-{int(_t2.time())}"
for tgt in ("ch-live", "ch-sup"):
    bres.append(cc.send(tgt, "mixed fanout", frm="fabric", thread=gthread))
time.sleep(0.4)
check("46 mixed broadcast: channel member got the HTTP push",
      any("mixed fanout" in (r.get("content") or "") for r in _Rx.received))
check("47 mixed broadcast: supervised member got a /inject under the same thread",
      any(i["message"] == "mixed fanout" for i in _MockSupervisor.injects))

# --- supervised PRUNE: supervisor reports the session closed → the reg is pruned ---
_MockSupervisor.states["sv-1"] = "closed"
live3 = cc.live_sessions()
check("48 live_sessions PRUNES a supervised member the supervisor reports CLOSED",
      not any(r["handle"] == "ch-sup" for r in live3))
check("49 the closed supervised registration file was removed",
      not os.path.exists(os.path.join(tmp, "ch-sup.json")))

# --- supervised TRANSIENT outage: an UNREACHABLE supervisor must NOT delete the fork-owned reg ---
sup_reg("ch-sup2", "sv-2", base="http://127.0.0.1:9")    # port 9 = discard, unreachable
live4 = cc.live_sessions()
check("50 unreachable supervisor: the supervised reg is KEPT (transient), never deleted",
      os.path.exists(os.path.join(tmp, "ch-sup2.json")))
check("51 a supervised member under an unreachable supervisor still LISTS (presence held, not destroyed)",
      any(r["handle"] == "ch-sup2" for r in cc.live_sessions()))

# --- supervisor_base fallback: a supervised reg missing the field uses COMPANY_SUPERVISOR_BASE ---
check("52 supervisor_base falls back to the process default when the reg omits it",
      cc.supervisor_base({"handle": "z", "supervisor_session": "s"}) == cc.DEFAULT_SUPERVISOR_BASE.rstrip("/"))

# --- WATCHER RESTART after exit (regression for the silent-drop bug found in lead cross-review) ---
# A supervised member's reply-watcher exits (a /watch stream blip / supervisor recycle — the SESSION
# stays live). A LATER dispatch to the SAME handle MUST start a FRESH watcher and fold the new reply.
# The pre-fix code left the handle in _watchers after the first exit (the finally never popped it) →
# _ensure_supervised_watcher returned without re-tailing → every later reply for that handle was
# SILENTLY DROPPED. This case FAILS against that bug and PASSES with the lifecycle fix.
_MockSupervisor.states["sv-restart"] = "idle"
sup_reg("ch-restart", "sv-restart", desc="watcher exits, then a redispatch must re-tail")
_Rx.received.clear(); _MockSupervisor.injects.clear()
cc.send("ch-restart", "first turn", frm="ch-live", topic="t-r1")     # dispatch 1 → watcher 1 folds reply 1
for _ in range(60):
    if any("SUPERVISED REPLY to: first turn" in (r.get("content") or "") for r in _Rx.received): break
    time.sleep(0.1)
check("53 supervised reply folded on the FIRST dispatch (watcher 1 ran)",
      any("SUPERVISED REPLY to: first turn" in (r.get("content") or "") for r in _Rx.received))
# end watcher 1: a `closed` watch event ends its stream (states stays idle = a stream blip, NOT a close)
_MockSupervisor.watch_q.setdefault("sv-restart", _queue.Queue()).put({"type": "closed"})
for _ in range(60):                                   # wait for watcher 1 to reap itself out of _watchers
    w = cc._watchers.get("ch-restart")
    if not (w and w.get("thread") and w["thread"].is_alive()): break
    time.sleep(0.1)
_Rx.received.clear(); _MockSupervisor.injects.clear()
cc.send("ch-restart", "second turn", frm="ch-live", topic="t-r2")    # dispatch 2 → the bug drops this
for _ in range(60):
    if any("SUPERVISED REPLY to: second turn" in (r.get("content") or "") for r in _Rx.received): break
    time.sleep(0.1)
check("54 a FRESH watcher started on the SECOND dispatch + folded its reply (no silent drop after exit)",
      any("SUPERVISED REPLY to: second turn" in (r.get("content") or "") for r in _Rx.received))

msup.shutdown()
srv.shutdown()
print(f"\n{'='*56}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL: print("FAILED:", ", ".join(FAIL)); sys.exit(1)
print("ALL GREEN — cc_channels: presence-prune, find/fail-loud, thread+mail, reply push-back, "
      "named-channel registry (CRUD + multi-channel membership), unified transport "
      "(channel↔HTTP · supervised↔supervisor /inject+/watch reply-fold · safe prune).")
