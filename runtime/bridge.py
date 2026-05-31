"""The bridge (C8, skeleton form) — the runtime hosts the canvas's connection.

Stdlib http.server only (zero install). Minimal version of the two channels:
action (POST /api/run) + state (GET /api/graph). Full pycrdt/Yjs sync is the
I1 hardening; the runtime is authoritative either way. See contracts/C8.

Run: python3 runtime/bridge.py   then open http://localhost:8770
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contracts.shapes import NodeInstance, Edge, Graph   # noqa: E402
from store.fs_store import FsStore                        # noqa: E402
from runtime import scheduler                             # noqa: E402
from runtime.registry import NodeRegistry                 # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANVAS = os.path.join(ROOT, "canvas", "index.html")
REGISTRY = NodeRegistry().discover([os.path.join(ROOT, "nodes")])   # node-types DISCOVERED (E4)
CONTENT_KINDS = ("constant", "document", "code", "file", "image", "source")

STORE = FsStore("/tmp/company-bridge-store")
GRAPH = Graph(
    id="demo",
    nodes=[
        NodeInstance(id="prompt", type="constant",
                     config={"value": "In one sentence, what is a composition engine?"}),
        NodeInstance(id="brain", type="llm",
                     config={"model": "deepseek-v4-pro:cloud",
                             "system": "Answer in one concise sentence."}),
    ],
    edges=[Edge(from_node="prompt", from_port="value", to_node="brain", to_port="prompt")],
)


def graph_state(result=None):
    nodes = []
    for n in GRAPH.nodes:
        logical = f"run://{GRAPH.id}/{n.id}"
        cas = STORE.head(logical)
        status = "idle"
        if result:
            status = "ran" if n.id in result["ran"] else ("cached" if n.id in result["skipped"] else "idle")
        nodes.append({
            "id": n.id, "type": n.type, "config": n.config,
            "kind": "content" if n.type in CONTENT_KINDS else "process",
            "status": status,
            "address": logical,
            "content_hash": cas,
            "output": STORE.get_content(cas) if cas else None,
        })
    edges = [{"from": e.from_node, "to": e.to_node} for e in GRAPH.edges]
    return {"id": GRAPH.id, "nodes": nodes, "edges": edges}


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
            self._send(200, json.dumps(graph_state()))
        elif self.path == "/api/object_info":
            self._send(200, json.dumps(REGISTRY.object_info()))   # served from the live registry (C5/E4)
        else:
            self._send(404, "{}")

    def do_POST(self):
        if self.path == "/api/run":
            result = scheduler.run(GRAPH, STORE, REGISTRY)
            self._send(200, json.dumps(graph_state(result)))
        elif self.path == "/api/set":         # change a node's config (proves change-propagation)
            ln = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(ln) or "{}")
            for n in GRAPH.nodes:
                if n.id == body.get("node"):
                    n.config.update(body.get("config", {}))
            self._send(200, json.dumps(graph_state()))
        else:
            self._send(404, "{}")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8770
    print(f"[bridge] runtime hosting canvas at http://localhost:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
