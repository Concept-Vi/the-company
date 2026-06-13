#!/usr/bin/env python3
"""Minimal REAL-claude WAKE/resume proof (S-R3.2/3.3 + validates the R1 deadlock fix on the
RESUME spawn path). Drives the live supervisor on :8771:

  1. spawn a fresh session, give it a codeword, get the claude_session_id, tear it down.
  2. WAKE it (spawn resume=<claude_session_id>) and ask for the codeword.
  3. PASS only if the resumed session answers with the SAME codeword (continuity across a
     real claude --resume) — proving the resume path reaches idle (the fix) and wake works.

Mirrors the R1 probe's req/Watcher mechanics. No model load (claude API). Run with the
fixed supervisor up. NEVER green-paints: each step reports OBSERVED/NOT-OBSERVED with evidence.
"""
import json, sys, threading, time, urllib.request, urllib.error

BASE = "http://127.0.0.1:8771"
STAMP = sys.argv[1] if len(sys.argv) > 1 else "X"
CODEWORD = f"BANANA-{STAMP}"


def req(method, path, body=None, timeout=30):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


class Watcher(threading.Thread):
    def __init__(self, session):
        super().__init__(daemon=True)
        self.session = session
        self.events = []
        self.lock = threading.Lock()

    def run(self):
        try:
            r = urllib.request.Request(f"{BASE}/watch?session={self.session}")
            with urllib.request.urlopen(r, timeout=300) as resp:
                for raw in resp:
                    try:
                        ev = json.loads(raw)
                    except ValueError:
                        continue
                    with self.lock:
                        self.events.append(ev)
        except Exception:
            pass

    def mark(self):
        with self.lock:
            return len(self.events)

    def wait_for(self, pred, timeout, since=0):
        t0 = time.time()
        while time.time() - t0 < timeout:
            with self.lock:
                for ev in self.events[since:]:
                    if pred(ev):
                        return ev
            time.sleep(0.25)
        return None


def wait_idle(sid, timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        _, r = req("GET", "/sessions")
        rec = next((s for s in r.get("sessions", []) if s["id"] == sid), None)
        if rec and rec["state"] == "idle":
            return rec
        if rec and rec["state"] == "closed":
            raise SystemExit(f"FAIL: session {sid} closed: {rec.get('close_reason')}")
        time.sleep(0.5)
    raise SystemExit(f"FAIL: session {sid} not idle within {timeout}s")


def turn(sid, w, message, timeout=240):
    m = w.mark()
    req("POST", "/inject", {"session": sid, "message": message})
    done = w.wait_for(lambda e: e.get("type") == "done", timeout, since=m)
    return (done or {}).get("result", "")


_, h = req("GET", "/health")
print(f"supervisor up: {h.get('sessions')}")

# ── 1. fresh session: plant the codeword ──
code, r = req("POST", "/spawn", {"cwd": "/home/tim/company", "name": f"wake-src-{STAMP}"})
assert code == 200, f"spawn failed: {r}"
sid = r["session"]["id"]
w = Watcher(sid); w.start()
wait_idle(sid)
turn(sid, w, f"Remember this codeword: {CODEWORD}. Reply with just: OK")
_, r = req("GET", "/sessions")
rec = next((s for s in r["sessions"] if s["id"] == sid), None)
csid = rec.get("claude_session_id")
print(f"  plant: claude_session_id={csid}  (codeword {CODEWORD})")
assert csid, "FAIL: no claude_session_id captured after first turn"
req("POST", "/teardown", {"session": sid})

# ── 2. WAKE it: resume by claude_session_id, ask for the codeword ──
time.sleep(1)
code, r = req("POST", "/spawn", {"cwd": "/home/tim/company", "name": f"wake-resumed-{STAMP}",
                                 "resume": csid})
assert code == 200, f"wake spawn failed: {r}"
wsid = r["session"]["id"]
w2 = Watcher(wsid); w2.start()
wait_idle(wsid)   # ← the fix's resume-path proof: a resumed session reaches idle
ans = turn(wsid, w2, "What codeword did I ask you to remember? Reply with just the codeword.")
req("POST", "/teardown", {"session": wsid})

ok = CODEWORD in ans
print(f"  WAKE resume reached idle: OBSERVED")
print(f"  continuity: {'OBSERVED' if ok else 'NOT-OBSERVED'} — resumed session "
      + (f"recalled {CODEWORD}" if ok else f"replied: {ans[:200]!r}"))
print(f"\nRESULT: {'PASS — real claude --resume reaches idle (fix holds on resume) AND carries conversation continuity' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
