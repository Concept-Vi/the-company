"""runtime/bridge.py — the UI face (C8, skeleton form). Thin HTTP over the shared Suite.

Serves the operator console + state/action. Same brain (runtime.suite.Suite) and same
substrate (the store at fcfg.STORE_DIR) as the MCP face — so the agent and the UI operate
ONE system. Stdlib http only. See contracts/C8.

Run: python3 runtime/bridge.py [port]   then open http://localhost:8770
"""
from __future__ import annotations
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contracts.node_record import NodeInstance, Edge, Graph
from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from fabric import config as fcfg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANVAS = os.path.join(ROOT, "canvas", "index.html")
SUITE = Suite(FsStore(fcfg.STORE_DIR),
              NodeRegistry().discover([os.path.join(ROOT, "nodes")]))
DEMO = "codebase"


def seed_demo():
    """First-run graph = the FIRST PURPOSE: the system answering about its own codebase."""
    if DEMO not in SUITE.list_graphs():
        SUITE.save_graph(Graph(id=DEMO, nodes=[
            NodeInstance(id="question", type="constant",
                         config={"value": "What does the scheduler's memo gate do, and which file is it in?"}),
            NodeInstance(id="code", type="codebase", config={}),
            NodeInstance(id="answer", type="ask", config={"model": "deepseek-v4-pro:cloud"}),
        ], edges=[
            Edge(from_node="question", from_port="value", to_node="answer", to_port="question"),
            Edge(from_node="code", from_port="context", to_node="answer", to_port="context"),
        ]))


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(CANVAS, "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        elif self.path == "/api/graph":
            self._send(200, json.dumps(SUITE.state(DEMO)))
        elif self.path == "/api/object_info":
            self._send(200, json.dumps(SUITE.object_info()))
        else:
            self._send(404, "{}")

    def do_POST(self):
        if self.path == "/api/run":
            result = SUITE.run(DEMO)
            self._send(200, json.dumps(SUITE.state(DEMO, result)))
        elif self.path == "/api/set":
            ln = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(ln) or "{}")
            SUITE.set_config(DEMO, body.get("node"), body.get("config", {}))
            self._send(200, json.dumps(SUITE.state(DEMO)))
        else:
            self._send(404, "{}")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    seed_demo()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8770
    print(f"[bridge] UI face over the shared Suite at http://localhost:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
