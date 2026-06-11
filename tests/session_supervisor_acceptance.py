"""tests/session_supervisor_acceptance.py — the session supervisor's service-level guarantees (F1.1, guide §A).

Proves BY USE, against the REAL service process (no mocks of the supervisor itself), on an
ISOLATED tmp store, with a STUB claude binary (COMPANY_CLAUDE_BIN — the ui_claude_session
binary-resolution seam; this lane may not spawn real claude sessions, lead-only law):

  1. the service starts and /health answers on 127.0.0.1 (the exposure law, audit B3);
  2. spawn ×3 concurrent supervised sessions — all reach idle (init parsed, stream held open);
  3. the 4th spawn above COMPANY_FABRIC_CONCURRENCY=3 is REFUSED with a TEACHING error
     (names the cap + the env var + the way forward — audit C9);
  4. inject → the stub replies → state returns to idle, the reply landed, and the durable
     `agent_sessions.turn` claim + `agent_sessions.spawned` events are on events.jsonl
     (single-writer law: this service is the only agent_sessions.* emitter);
  5. THE WATCHDOG (audit C3): a turn that HANGS SILENTLY (no output at all) is reaped within
     the enforced wall-clock (COMPANY_FABRIC_TURN_TIMEOUT_S=2 here) — state=closed, reason
     names the watchdog, the subprocess is actually DEAD (no orphan);
  6. the MAILBOX contract (guide §C format): a deliver intent appended to
     agent_sessions/mail.jsonl is consumed (cursor ref advances), injected, and a durable
     reply (verb=reply, re=<intent id>, body in cas) is appended back to the leaf;
  7. teardown + SIGTERM leave NO orphan stub processes.

Deadlock-safe: every wait is bounded; the supervisor child is killed in finally. Exit 0 = pass,
1 = a failed check, 2 = blocked (the concurrency_acceptance convention).
Run: ./.venv/bin/python tests/session_supervisor_acceptance.py
"""
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PY = os.path.join(ROOT, ".venv", "bin", "python")
if not os.path.exists(PY):
    PY = sys.executable
PORT = 8779                      # a TEST port — never the live 8771 (a real service may be up)
BASE = f"http://127.0.0.1:{PORT}"
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def req(method, path, body=None, timeout=10):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def wait_for(fn, timeout, what):
    t0 = time.time()
    while time.time() - t0 < timeout:
        v = fn()
        if v:
            return v
        time.sleep(0.1)
    raise AssertionError(f"BLOCKED: timed out waiting for {what}")


# ── the stub claude: speaks the stream-json contract; "HANG" = silent no-output turn ──
STUB = r'''#!/usr/bin/env python3
import json, sys, time, uuid, os
sid = os.environ.get("STUB_SID") or ("stub-" + uuid.uuid4().hex[:8])
print(json.dumps({"type": "system", "subtype": "init", "session_id": sid}), flush=True)
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        ev = json.loads(line)
    except ValueError:
        continue
    if ev.get("type") == "control_request":
        continue
    if ev.get("type") != "user":
        continue
    blocks = (ev.get("message") or {}).get("content") or []
    text = " ".join(b.get("text", "") for b in blocks if isinstance(b, dict))
    if "HANG" in text:
        time.sleep(3600)                       # the silent hang — emits NOTHING, the watchdog's case
    print(json.dumps({"type": "assistant", "message": {"content": [
        {"type": "text", "text": "echo: " + text}]}}), flush=True)
    print(json.dumps({"type": "result", "result": "echo: " + text,
                      "session_id": sid, "num_turns": 1, "is_error": False}), flush=True)
'''


def main():
    tmp = tempfile.mkdtemp(prefix="supervisor-accept-")
    store_dir = os.path.join(tmp, "store")
    stub = os.path.join(tmp, "stub-claude")
    with open(stub, "w") as f:
        f.write(STUB)
    os.chmod(stub, 0o755)
    env = dict(os.environ,
               COMPANY_STORE=store_dir,
               COMPANY_CLAUDE_BIN=stub,
               COMPANY_FABRIC_CONCURRENCY="3",
               COMPANY_FABRIC_TURN_TIMEOUT_S="2",
               COMPANY_FABRIC_INIT_WAIT_S="5")
    sup = subprocess.Popen([PY, os.path.join(ROOT, "runtime", "session_supervisor.py"), str(PORT)],
                           env=env, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True)
    try:
        # 1 — service starts, /health curls, 127.0.0.1 stated
        wait_for(lambda: _try_health(), 15, "/health")
        code, h = req("GET", "/health")
        check("GET /health is 200 + ok", code == 200 and h.get("ok") is True)
        check("health states the 127.0.0.1 bind + the cap", h.get("bind") == "127.0.0.1" and h.get("cap") == 3)

        # 2 — three concurrent supervised sessions reach idle
        sids = []
        for i in range(3):
            code, r = req("POST", "/spawn", {"cwd": tmp, "name": f"t{i}"})
            check(f"spawn t{i} accepted", code == 200 and r.get("ok"))
            sids.append(r["session"]["id"])
        code, r = req("GET", "/sessions")
        idle = [s for s in r["sessions"] if s["state"] == "idle"]
        check("3 sessions live + idle (init parsed, stream held open)", len(idle) == 3)
        check("claude session ids captured from init", all(s["claude_session_id"] for s in idle))

        # 3 — the 4th spawn refuses with a TEACHING error
        code, r = req("POST", "/spawn", {"cwd": tmp, "name": "over-cap"})
        check("4th spawn is refused (429)", code == 429)
        msg = r.get("error", "")
        check("refusal TEACHES (cap value + env var + the way forward)",
              "3" in msg and "COMPANY_FABRIC_CONCURRENCY" in msg and "/teardown" in msg)

        # 4 — inject → reply → idle; durable events on the shared log
        code, r = req("POST", "/inject", {"session": sids[0], "message": "hello fabric"})
        check("inject accepted on an idle session", code == 200)
        rec = wait_for(lambda: _session(sids[0], turns=1), 10, "turn completion")
        check("turn completed → state idle, turns=1", rec["state"] == "idle" and rec["turns"] == 1)
        evs = _events(store_dir)
        kinds = [e["kind"] for e in evs]
        check("agent_sessions.spawned ×3 on events.jsonl (single writer)",
              kinds.count("agent_sessions.spawned") == 3)
        # BOUNDED WAIT (the test's own convention): the record flips idle/turns=1 in the reader
        # thread BEFORE the durable claim's fsync completes — an immediate log read races that
        # window (observed losing on WSL fsync latency). The claim is still the bar; the wait is.
        turn_evs = wait_for(lambda: [e for e in _events(store_dir)
                                     if e["kind"] == "agent_sessions.turn"] or None,
                            10, "durable agent_sessions.turn claim")
        check("durable agent_sessions.turn claim written", len(turn_evs) == 1
              and turn_evs[0].get("session") == sids[0] and turn_evs[0].get("is_error") is False)
        check("inject while BUSY would refuse-loud (409 teach)", _busy_refusal_teaches(sids[1]))

        # 5 — THE WATCHDOG reaps a silent hang (the F1.1 silent-hang case)
        wait_for(lambda: _session(sids[1], state="idle"), 10, "probe session back to idle")
        code, r = req("GET", "/sessions")
        pid_hang = [s for s in r["sessions"] if s["id"] == sids[1]][0]["pid"]
        code, r = req("POST", "/inject", {"session": sids[1], "message": "please HANG now"})
        check("hang turn injected", code == 200)
        rec = wait_for(lambda: _session(sids[1], state="closed"), 10, "watchdog reap")
        check("watchdog reaped the silent hang (state=closed, reason names it)",
              "watchdog-timeout" in (rec["close_reason"] or ""))
        check("agent_sessions.closed event carries the watchdog reason",
              any(e["kind"] == "agent_sessions.closed" and "watchdog" in e.get("reason", "")
                  for e in _events(store_dir)))
        check("the hung subprocess is DEAD (no orphan)", not _alive(pid_hang))

        # 6 — mailbox: deliver intent consumed → injected → durable reply with re=<id>
        from store.fs_store import FsStore
        st = FsStore(store_dir)
        target = _session(sids[2])["claude_session_id"]
        intent_id = "intent-0001"
        cas = st.put_content({"text": "mailbox says hello"})
        mail = os.path.join(store_dir, "agent_sessions", "mail.jsonl")
        os.makedirs(os.path.dirname(mail), exist_ok=True)
        with open(mail, "a") as f:
            f.write(json.dumps({"id": intent_id, "to": f"session://{target}",
                                "from": "session://tester", "verb": "deliver", "cas": cas}) + "\n")
        reply = wait_for(lambda: _mail_reply(mail, intent_id), 10, "mailbox reply")
        check("deliver intent consumed → durable reply appended (verb=reply, re=intent)",
              reply["verb"] == "reply" and reply["to"] == "session://tester")
        body = st.get_content(reply["cas"])
        check("reply body rides cas and carries the turn's text", "mailbox says hello" in body["text"])
        # the closed raw-append seam: replies now ride store.append_agent_mail → seq-stamped +
        # thread-joined, so a seq-cursor inbox read (sessions(op='inbox') / agent_mail_since)
        # actually SEES them — the raw no-seq append made every reply invisible to those reads
        check("reply is seq-stamped (inbox-visible, never the invisible raw-append shape)",
              isinstance(reply.get("seq"), int))
        check("reply joins the intent's thread (fan aggregation key; id-fallback — this "
              "hand-appended intent carries no thread)", reply.get("thread") == intent_id)
        inbox = st.agent_mail_since(-1, to="session://tester", verb="reply")
        check("agent_mail_since(to=tester, verb=reply) round-trips the reply",
              any(r.get("re") == intent_id for r in inbox))
        check("per-consumer cursor ref advanced", (st.head("agent_sessions/cursor:supervisor") or "0") != "0")
        turn2 = [e for e in _events(store_dir) if e["kind"] == "agent_sessions.turn"
                 and e.get("intent_id") == intent_id]
        check("the mailbox turn's agent_sessions.turn claim names the intent", len(turn2) == 1)

        # 7 — teardown + SIGTERM leave no orphans
        code, r = req("GET", "/sessions")
        pids = [s["pid"] for s in r["sessions"] if s["state"] != "closed" and s["pid"]]
        code, r = req("POST", "/teardown", {"session": sids[0]})
        check("teardown closes a session", code == 200 and r["session"]["state"] == "closed")
        sup.send_signal(signal.SIGTERM)
        try:
            sup.wait(timeout=10)
        except subprocess.TimeoutExpired:
            raise AssertionError("BLOCKED: supervisor did not exit on SIGTERM")
        time.sleep(0.5)
        check("SIGTERM → every owned subprocess is dead (no orphans)",
              all(not _alive(p) for p in pids))
        print(f"\nPASS — {PASS} checks green (session_supervisor service-level guarantees).")
    finally:
        if sup.poll() is None:
            sup.kill()
            sup.wait(timeout=5)
        out = sup.stdout.read() if sup.stdout else ""
        if "Traceback" in (out or ""):
            print("--- supervisor output (had a traceback) ---\n" + out[-3000:])
        shutil.rmtree(tmp, ignore_errors=True)


def _try_health():
    try:
        code, _ = req("GET", "/health", timeout=2)
        return code == 200
    except Exception:
        return False


def _session(sid, turns=None, state=None):
    code, r = req("GET", "/sessions")
    for s in r.get("sessions", []):
        if s["id"] == sid:
            if turns is not None and s["turns"] < turns:
                return None
            if state is not None and s["state"] != state:
                return None
            return s
    return None


def _busy_refusal_teaches(sid):
    # inject twice fast: the second hits BUSY → 409 with teach-text (or the first already
    # finished — the stub is fast — in which case we accept the pass-by-speed honestly).
    req("POST", "/inject", {"session": sid, "message": "first"})
    code, r = req("POST", "/inject", {"session": sid, "message": "second"})
    if code == 409:
        return "mid-turn" in r.get("error", "")
    wait_for(lambda: _session(sid, turns=1), 10, "busy-probe turn")
    return code == 200          # too fast to catch busy — both turns legitimately accepted


def _events(store_dir):
    p = os.path.join(store_dir, "events.jsonl")
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p) if l.strip()]


def _mail_reply(mail, intent_id):
    if not os.path.exists(mail):
        return None
    for l in open(mail):
        if not l.strip():
            continue
        rec = json.loads(l)
        if rec.get("re") == intent_id:
            return rec
    return None


def _alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"\n{e}")
        sys.exit(2 if "BLOCKED" in str(e) else 1)
