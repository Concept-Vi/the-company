"""tests/messaging_send_acceptance.py — the ONE unified send() tool (mcp_face/tools/send.py).

PROVES BY USE (isolated tmp store + a mock .mjs port + a stub MCP; never ~/company/.data) that
send(to, message) is the single presence-aware front door:
  1. a CHANNEL target resolved BY NAME (channel://<name>, WIN C) fans to members and LIVE-PUSHES the
     reachable ones (the mock endpoint receives the message); the receipt names delivered_live vs queued.
  2. a SESSION target that is unknown/unreachable FAILS LOUD (transport='none', verb='unreachable',
     delivered=False) — never a phantom OK, never a silent drop.
  3. an empty target raises (teaching).

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
from mcp_face.tools import send as send_mod    # noqa: E402

FAIL = []


def check(name, cond):
    print(("  ok  " if cond else "  XX  ") + name)
    if not cond:
        FAIL.append(name)


class _StubMCP:
    def __init__(self):
        self.tools = {}

    def tool(self):
        def deco(fn):
            self.tools[fn.__name__] = fn
            return fn
        return deco


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

    tmp = tempfile.mkdtemp(prefix="mu-send-")
    store = FsStore(tmp)
    known = {"mA", "mB"}

    def reg(sid):
        if sid in known:
            return {"id": sid, "state": "unsupervised-live", "cwd": None}
        raise ValueError(f"unknown session {sid}")     # mirrors suite.get_agent_session's fail-loud

    sc.create_channel(store, name="unify demo", members=["mA", "mB"], registry=reg)

    # r1 (channel) fans via cc_channels.live_sessions(); r2 (session) routes via identity.resolve.
    mA_reg = {"handle": "ch-mA", "session_id": "mA", "port": port, "cwd": None}
    identity.cc.live_sessions = lambda: [mA_reg]                 # mA is the live .mjs channel member
    identity.resolve = lambda target, **kw: None                # router path: unknown target -> unreachable

    class FakeSuite:
        def __init__(self, s):
            self.store = s

        def get_agent_session(self, sid):
            return reg(sid)

    mcp = _StubMCP()
    send_mod.register(mcp, FakeSuite(store))
    send = mcp.tools["send"]

    r1 = send(to="channel://unify demo", message="hi channel", frm="session://sender")
    check("channel resolved BY NAME (WIN C)", r1.get("kind") == "channel")
    check("delivered_live>=1 (reachable member live-pushed)", r1.get("delivered_live", 0) >= 1)
    check("the mock .mjs actually received the push", any(g.get("content") == "hi channel" for g in got))
    check("queued names the unreachable member", r1.get("queued", 0) >= 1)

    r2 = send(to="session://nope-xyz", message="hi", frm="session://sender")
    check("session target routes through the router", r2.get("kind") == "session")
    check("unknown target FAILS LOUD (delivered False)", r2.get("delivered") is False)
    check("unknown -> transport none / verb unreachable (no phantom)",
          r2.get("transport") == "none" and r2.get("verb") == "unreachable")

    try:
        send(to="", message="x")
        check("empty `to` raises", False)
    except ValueError:
        check("empty `to` raises", True)

    if FAIL:
        print(f"\nFAIL — {len(FAIL)} failed")
        sys.exit(1)
    print("\nmessaging_send_acceptance: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
