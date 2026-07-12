"""sessions — the `company session` type-view (Session Fabric F1.1 launcher).

The operator face of the SESSION SUPERVISOR service (runtime/session_supervisor.py,
127.0.0.1:8771): spawn a supervised Claude Code session, list the fleet, send a turn,
tear one down. ONE spawn path — this CLI and the bridge both POST the same /spawn; the
console never launches claude itself (the supervisor is the only launcher, the fabric's
single-owner law).

stdlib-only (the console constitution): urllib against the supervisor's HTTP API. The
supervisor down is a LOUD, teaching failure — never a silent no-op.

  company session                          list the supervised fleet
  company session new [--cwd D] [--resume ID] [--name L] [--prompt "..."]   spawn
  company session send <id> <message...>   inject a turn (id = supervisor id or claude session id)
  company session stop <id>                teardown one session
  company session cap                      show the live-session cap (COMPANY_FABRIC_CONCURRENCY) + live count
  company session fleet                    list the point-in-time CLONE fleet (handle · cut · era)
"""
import json
import os
import sys
import urllib.error
import urllib.request

# P1 config fix: was a bare literal with NO env override (the only unconfigurable supervisor address
# besides the bridge proxy). Env-first now; the default literal stays local because this CLI is
# deliberately dependency-light (no runtime imports).
SUPERVISOR = os.environ.get("COMPANY_SUPERVISOR_BASE", "http://127.0.0.1:8771")


def _call(method, path, body=None, timeout=30):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(SUPERVISOR + path, data=data, method=method,
                               headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except ValueError:
            return e.code, {"error": f"HTTP {e.code}"}
    except (urllib.error.URLError, OSError):
        sys.exit("  ✖ the session supervisor is not up (127.0.0.1:8771).\n"
                 "    Start it first: company up session-supervisor")


def _row(s):
    sid = s.get("claude_session_id") or s["id"]
    return (f"  {s['id']:<12} {s['state']:<9} {s.get('name', ''):<22} turns={s['turns']:<3} "
            f"cwd={s['cwd']}  session={sid}")


def run(args):
    """Dispatch `company session ...` (args = everything after `session`)."""
    sub = args[0] if args else "list"
    if sub in ("list", "ls"):
        _, r = _call("GET", "/sessions")
        rows = r.get("sessions", [])
        if not rows:
            print("  no supervised sessions. Spawn one: company session new [--cwd DIR] "
                  "[--resume ID] [--name LABEL]")
            return
        for s in rows:
            print(_row(s))
        return
    if sub == "new":
        body, it = {}, iter(args[1:])
        for a in it:
            if a == "--cwd":
                body["cwd"] = next(it, None)
            elif a == "--resume":
                body["resume"] = next(it, None)
            elif a == "--name":
                body["name"] = next(it, None)
            elif a == "--prompt":
                body["prompt"] = next(it, None)
            elif a == "--fork":
                body["fork"] = True
            else:
                sys.exit(f"  unknown flag {a!r}. usage: company session new [--cwd DIR] "
                         f"[--resume ID] [--fork] [--name LABEL] [--prompt \"...\"]")
        body["source"] = "cli"
        code, r = _call("POST", "/spawn", body, timeout=60)
        if code != 200:
            sys.exit(f"  ✖ {r.get('error', 'spawn failed')}")
        print("  ✓ spawned:")
        print(_row(r["session"]))
        return
    if sub == "send":
        if len(args) < 3:
            sys.exit("usage: company session send <id> <message...>")
        code, r = _call("POST", "/inject",
                        {"session": args[1], "message": " ".join(args[2:]), "source": "cli"},
                        timeout=60)
        if code != 200:
            sys.exit(f"  ✖ {r.get('error', 'inject failed')}")
        print(f"  ✓ injected into {args[1]} — watch: curl -N "
              f"'{SUPERVISOR}/watch?session={args[1]}'")
        return
    if sub == "stop":
        if len(args) < 2:
            sys.exit("usage: company session stop <id>")
        code, r = _call("POST", "/teardown", {"session": args[1]})
        if code != 200:
            sys.exit(f"  ✖ {r.get('error', 'teardown failed')}")
        print(f"  ✓ closed {args[1]}")
        return
    if sub == "cap":
        _, h = _call("GET", "/health")
        s = h.get("sessions", {})
        print(f"  live-session cap (COMPANY_FABRIC_CONCURRENCY): {h.get('cap')}")
        print(f"  live now: {s.get('total', 0)}  ·  turn-timeout: {h.get('turn_timeout_s')}s  ·  "
              f"permission: {h.get('permission')}")
        if len(args) >= 2:
            print(f"\n  note: the supervisor reads COMPANY_FABRIC_CONCURRENCY at START, so setting the cap "
                  f"to {args[1]!r} needs a managed supervisor restart. That restart command is built + "
                  f"verified separately (it briefly restarts the fleet's owner) — not folded into this "
                  f"read-only view.")
        return
    if sub == "fleet":
        _, r = _call("GET", "/sessions")
        clones = [s for s in r.get("sessions", []) if str(s.get("name", "")).startswith("clone-")]
        if not clones:
            print("  no point-in-time clones live. Spawn one via the cc_clone tool (op='clone').")
            return
        print(f"  {len(clones)} clone(s) live (name encodes the cut point):")
        for s in clones:
            print(_row(s))
        return
    sys.exit(f"unknown session subcommand {sub!r}. Try: company session [list|new|send|stop|cap|fleet]")
