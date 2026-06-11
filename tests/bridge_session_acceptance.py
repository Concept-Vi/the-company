"""tests/bridge_session_acceptance.py — RAIL R1-prime SERVICE-LEVEL proof (Capability Fabric ④,
L-FOUND-R1prime). Boots the REAL session_supervisor service against an ISOLATED tmp store with a
STUB claude binary (COMPANY_CLAUDE_BIN — NO real claude is ever spawned, the lane law) and exercises
the `POST /bridge-session` route end-to-end over HTTP:

  1. consent-not-lockdown: a bridge-session WITHOUT operator_consent is REFUSED with HTTP 403
     (forbidden-until-consent, distinct from cap=429 / state=409), and the refusal TEACHES (names the
     consent flag + that git-revert backstops, never an auth wall).
  2. WITH operator_consent=true the spawn is accepted (200), the session record marks
     profile="bridge-session", and the durable agent_sessions.spawned event STAMPS the security
     decision: profile + operator_consent + the WIDER allowed_tools string (Bash present, not the
     mcp__company-only floor) — the Introspective-Data-Building run-record (§5.6).
  3. a host/rail-boundary capability (computer) is REFUSED-LOUD over HTTP too (the boundary holds at
     the service edge, not just in the unit builder) — macOS+interactive-only, never bindable on -p.
  4. the wider session reaches idle (the stub's init parsed, stream held open) — the profile is a
     real spawn posture, not just a cmd string.

This is SERVICE-LEVEL (HTTP) proof with a stub binary. 🟡 live-verify pending (lead): a REAL wider
session round-trip (a bridge-session committing via Bash-git / an LSP nav returning prose) needs a
real claude spawn — the build lead's slice, NEVER claimed live here.

Run: ./.venv/bin/python tests/bridge_session_acceptance.py    (exit 0 = pass)
"""
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, ".venv", "bin", "python")
PORT = 8783                      # a TEST port — never the live 8771, never the other suite's 8779
BASE = f"http://127.0.0.1:{PORT}"

PASS = 0
FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  XX  {label}  {detail}")


def req(method, path, body=None, timeout=10):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def _try_health():
    try:
        c, _ = req("GET", "/health", timeout=2)
        return c == 200
    except Exception:
        return False


def wait_for(fn, timeout, what):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if fn():
            return True
        time.sleep(0.1)
    raise AssertionError(f"BLOCKED: timed out waiting for {what}")


STUB = r'''#!/usr/bin/env python3
import json, sys, uuid, os
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
    if ev.get("type") != "user":
        continue
    blocks = (ev.get("message") or {}).get("content") or []
    text = " ".join(b.get("text", "") for b in blocks if isinstance(b, dict))
    print(json.dumps({"type": "assistant", "message": {"content": [
        {"type": "text", "text": "echo: " + text}]}}), flush=True)
    print(json.dumps({"type": "result", "result": "echo: " + text,
                      "session_id": sid, "num_turns": 1, "is_error": False}), flush=True)
'''


def _events(store_dir):
    p = os.path.join(store_dir, "events.jsonl")
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def main():
    tmp = tempfile.mkdtemp(prefix="bridge-session-accept-")
    store_dir = os.path.join(tmp, "store")
    stub = os.path.join(tmp, "stub-claude")
    with open(stub, "w") as f:
        f.write(STUB)
    os.chmod(stub, 0o755)
    env = dict(os.environ,
               COMPANY_STORE=store_dir,
               COMPANY_CLAUDE_BIN=stub,
               COMPANY_FABRIC_CONCURRENCY="3",
               COMPANY_FABRIC_TURN_TIMEOUT_S="10",
               COMPANY_FABRIC_INIT_WAIT_S="5")
    sup = subprocess.Popen([PY, os.path.join(ROOT, "runtime", "session_supervisor.py"), str(PORT)],
                           env=env, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True)
    try:
        wait_for(_try_health, 15, "/health")

        # 1 — consent-not-lockdown: no operator_consent → 403, teaching.
        code, r = req("POST", "/bridge-session", {"name": "br-no-consent"})
        check("bridge-session WITHOUT operator_consent is REFUSED 403 (forbidden-until-consent)",
              code == 403, f"code={code} body={r}")
        err = (r.get("error") or "")
        check("the 403 refusal TEACHES (names operator_consent + that it is a gate, not a lockout)",
              "operator_consent" in err and "consent-gated" in err, f"err={err[:200]}")

        # 2 — WITH consent → 200, profile marked, spawn event stamps the security decision.
        code, r = req("POST", "/bridge-session",
                      {"operator_consent": True, "cwd": tmp, "name": "br-yes"})
        check("bridge-session WITH operator_consent is accepted (200)", code == 200 and r.get("ok"),
              f"code={code} body={r}")
        rec = r.get("session") or {}
        check("the session record marks profile='bridge-session'", rec.get("profile") == "bridge-session",
              f"rec={rec}")
        check("the response is liveness:stream with a watch cursor + no-return_shape note",
              r.get("liveness") == "stream" and "watch" in r and "return_shape" in (r.get("note") or ""))

        wait_for(lambda: any(e.get("kind") == "agent_sessions.spawned"
                             and e.get("profile") == "bridge-session" for e in _events(store_dir)),
                 10, "the bridge-session spawned event")
        evs = [e for e in _events(store_dir)
               if e.get("kind") == "agent_sessions.spawned" and e.get("profile") == "bridge-session"]
        check("durable agent_sessions.spawned stamps profile + operator_consent (the run-record §5.6)",
              bool(evs) and evs[-1].get("operator_consent") is True, f"evs={evs}")
        allow = evs[-1].get("allowed_tools", "") if evs else ""
        check("the spawn event records the WIDER allowlist (Bash present, NOT the mcp__company-only floor)",
              "Bash" in allow and "mcp__company" in allow and allow != "mcp__company", f"allow={allow!r}")

        # the wider session reaches idle (real spawn posture, stub init parsed)
        wait_for(lambda: any(s.get("profile") == "bridge-session" and s.get("state") == "idle"
                             for s in (req("GET", "/sessions")[1].get("sessions") or [])),
                 10, "the bridge-session reaching idle")
        sess = [s for s in (req("GET", "/sessions")[1].get("sessions") or [])
                if s.get("profile") == "bridge-session"]
        check("the wider session reached idle (init parsed, stream held — a real spawn posture)",
              bool(sess) and sess[-1].get("state") == "idle", f"sess={sess}")

        # 3 — host/rail boundary refused-loud over HTTP too (computer can never bind a -p/Linux rail)
        code, r = req("POST", "/bridge-session",
                      {"operator_consent": True, "capabilities": ["computer"], "name": "br-computer"})
        check("capabilities=['computer'] is REFUSED-LOUD over HTTP (macOS+interactive-only host boundary)",
              code in (403, 409) and "macOS" in (r.get("error") or ""), f"code={code} body={r}")

    finally:
        try:
            sup.send_signal(signal.SIGTERM)
            sup.wait(timeout=10)
        except Exception:
            sup.kill()

    print(f"\n{'PASS' if FAIL == 0 else 'FAIL'} — {PASS} ok, {FAIL} failed "
          f"(R1-prime bridge-session SERVICE-LEVEL, stub binary; real wider round-trip is the lead's).")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
