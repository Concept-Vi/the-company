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

srv.shutdown()
print(f"\n{'='*56}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL: print("FAILED:", ", ".join(FAIL)); sys.exit(1)
print("ALL GREEN — cc_channels router: presence-prune, find/fail-loud, thread+mail, reply push-back.")
