"""tests/messaging_weld_acceptance.py — the messaging-unification WELD (map board://item-0139fbc1).

PROVES BY USE (isolated tmp store + a mock .mjs port; never ~/company/.data) that a DURABLE channel
post routes each member by PRESENCE, not by supervisor-ownership — the exact "it shouldn't matter if
the supervisor owns them" fix:

  1. a member reachable RIGHT NOW via its own live .mjs port is LIVE-PUSHED here-and-now (the mock
     endpoint receives the message + meta), and the fan reports transport='channel', delivered=True.
  2. a member with NO live transport queues (transport='queue', delivered=False) — no phantom-OK.
  3. a supervised-live member keeps the proven path: verb='deliver' (the supervisor injects the mail
     intent), transport='supervised' — and is NOT double-pushed via .mjs.

Exit 0 = PASS · 1 = FAIL.
"""
import json
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore            # noqa: E402
from runtime import session_channels as sc    # noqa: E402
from runtime import identity                  # noqa: E402

FAIL = []


def check(name, cond):
    print(("  ok  " if cond else "  XX  ") + name)
    if not cond:
        FAIL.append(name)


def main():
    got = []

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            got.append(json.loads(self.rfile.read(n) or b"{}"))
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok")

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), H)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    tmp = tempfile.mkdtemp(prefix="mu-weld-")
    s = FsStore(tmp)
    states = {"mA": "unsupervised-live", "mB": "unsupervised-live", "mC": "supervised-live"}
    reg = lambda sid: {"id": sid, "state": states.get(sid, "unsupervised-live"), "cwd": None}
    ch = sc.create_channel(s, name="weld work", members=["mA", "mB", "mC"], registry=reg)

    def fake_resolve(target, **kw):
        if target == "mA":
            return {"uuid": "mA", "handle": "ch-mA", "transports": ["channel"], "state": "unsupervised-live",
                    "reg": {"handle": "ch-mA", "port": port, "transport": "channel", "cwd": None}}
        return None
    identity.resolve = fake_resolve

    out = sc.post_to_channel(s, ch["id"], "WELD PROBE", "session://sender", registry=reg)
    fan = {f["session"]: f for f in out["fan"]}
    a, b, c = fan.get("session://mA", {}), fan.get("session://mB", {}), fan.get("session://mC", {})

    check("mA live-pushed via .mjs (transport=channel)", a.get("transport") == "channel")
    check("mA delivered=True (confirmed HTTP 200)", a.get("delivered") is True)
    check("mock .mjs received exactly one POST", len(got) == 1)
    check("the POST carried the message body", bool(got) and got[0].get("content") == "WELD PROBE")
    check("the POST meta names the sender + channel",
          bool(got) and got[0].get("meta", {}).get("from") == "session://sender"
          and got[0].get("meta", {}).get("channel") == "weld work")
    check("mB unreachable -> transport=queue", b.get("transport") == "queue")
    check("mB delivered=False (no phantom-OK)", b.get("delivered") is False)
    check("mC supervised-live -> verb=deliver (supervisor injects)", c.get("verb") == "deliver")
    check("mC transport=supervised", c.get("transport") == "supervised")
    check("supervised member NOT double-pushed via .mjs", len(got) == 1)

    if FAIL:
        print(f"\nFAIL — {len(FAIL)} failed")
        sys.exit(1)
    print("\nmessaging_weld_acceptance: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
