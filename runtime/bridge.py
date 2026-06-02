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
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contracts.node_record import NodeInstance, Edge, Graph
from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from fabric import config as fcfg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANVAS = os.path.join(ROOT, "canvas", "index.html")
TTS_URL = os.environ.get("COMPANY_TTS_URL", "http://127.0.0.1:4123")   # local Kokoro service
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
    protocol_version = "HTTP/1.1"   # keep-alive so /api/stream (SSE) can hold the socket open

    def _send(self, code, body, ctype="application/json"):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _body(self):
        ln = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(ln) or "{}")

    def _qs(self, parsed):
        """A flat {key: value} from the query string (first value per key)."""
        return {k: v[0] for k, v in parse_qs(parsed.query).items()}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path                                 # path WITHOUT the query (exact matches hold)
        q = self._qs(parsed)
        gid = q.get("graph_id", DEMO)                      # graph-scoped reads default to DEMO (C4)
        if path == "/api/stream":                          # SSE — own handler, NEVER _send (G)
            self._stream(q)
            return
        try:
            if path in ("/", "/index.html"):
                with open(CANVAS, "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            elif path == "/api/graph":
                self._send(200, json.dumps(SUITE.state(gid)))
            elif path == "/api/graphs":                    # C4: list every graph in the substrate
                self._send(200, json.dumps(SUITE.list_graphs()))
            elif path == "/api/object_info":
                self._send(200, json.dumps(SUITE.object_info()))
            elif path == "/api/types":
                self._send(200, json.dumps(sorted(SUITE.list_types())))
            elif path == "/api/models":                    # B: per-kind/per-endpoint live model list
                self._send(200, json.dumps(SUITE.models_at(
                    kind=q.get("kind", "chat"), base_url=q.get("base_url"))))
            elif path == "/api/surfaced":
                self._send(200, json.dumps(SUITE.list_surfaced()))
            elif path == "/api/events":
                self._send(200, json.dumps(SUITE.events(60)))
            elif path == "/api/now":
                self._send(200, json.dumps(SUITE.now(gid)))
            elif path == "/api/chat":
                self._send(200, json.dumps(SUITE.chat_history(40)))
            elif path == "/api/rhm-config":
                self._send(200, json.dumps(SUITE.rhm_config()))
            elif path == "/api/inbox":
                self._send(200, json.dumps(SUITE.inbox_lanes()))
            elif path == "/api/last-change":
                self._send(200, json.dumps(SUITE.last_self_change() or {}))
            elif path == "/api/panels":
                self._send(200, json.dumps(SUITE.list_panels()))
            elif path == "/api/capabilities":
                self._send(200, json.dumps(SUITE.capabilities()))
            elif path == "/api/voice":                     # voice status: STT providers + TTS up?
                from voice import stt as voice_stt
                tts_up = False
                try:
                    import urllib.request as _u
                    _u.urlopen(TTS_URL + "/health", timeout=2); tts_up = True
                except Exception:
                    pass
                self._send(200, json.dumps({"stt": voice_stt.available(),
                                            "stt_default": voice_stt.DEFAULT_PROVIDER, "tts_up": tts_up}))
            else:
                self._send(404, "{}")
        except Exception as e:                             # fail loud to the UI (parity with do_POST)
            self._send(400, json.dumps({"error": f"{type(e).__name__}: {e}"}))

    def _stream(self, q):
        """GET /api/stream — Server-Sent Events (G). Tails the SHARED events.jsonl (so it captures
        BOTH faces, not an in-memory queue), pushing each new event as `id: <seq>\\ndata: <json>\\n\\n`.
        Cursor = ?since= or the Last-Event-ID reconnect header (default -1 = from the start). Heartbeat
        every ~15s so idle proxies don't drop the socket. NOT routed through _send (which sets
        Content-Length + closes). Fail loud: only client-disconnect is swallowed, never a real error."""
        since = q.get("since")
        if since is None:
            since = self.headers.get("Last-Event-ID", "-1")   # gapless reconnect
        try:
            cursor = int(since)
        except (TypeError, ValueError):
            cursor = -1
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        last_beat = time.monotonic()
        try:
            while True:
                for ev in SUITE.events_since(cursor):
                    self.wfile.write(
                        f"id: {ev['seq']}\ndata: {json.dumps(ev)}\n\n".encode())
                    self.wfile.flush()
                    cursor = ev["seq"]
                if time.monotonic() - last_beat >= 15:
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
                    last_beat = time.monotonic()
                time.sleep(0.4)
        except (BrokenPipeError, ConnectionResetError):
            return                                          # client closed — done, not an error

    def do_POST(self):
        # HTTP/1.1 keeps sockets alive (needed for the GET /api/stream SSE). But a POST handler that
        # doesn't drain its request body (e.g. /api/react, the 404 branch) would leave bytes that the
        # next request on a reused connection mis-parses → garbled 400s in a browser (which pools
        # connections; curl uses a fresh socket per call, so it's invisible there). Force-close POST
        # sockets — GET (incl. the stream) still keeps alive.
        self.close_connection = True
        try:
            if self.path == "/api/stt":                   # raw audio bytes in → transcript out
                from voice import stt as voice_stt
                ln = int(self.headers.get("Content-Length", 0))
                audio = self.rfile.read(ln)
                self._send(200, json.dumps(voice_stt.transcribe(audio)))
                return
            if self.path == "/api/tts":                   # text in → wav out (proxied to Kokoro)
                import urllib.request as _u
                body = self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}"
                req = _u.Request(TTS_URL + "/tts", data=body,
                                 headers={"Content-Type": "application/json"})
                with _u.urlopen(req, timeout=60) as r:
                    self._send(200, r.read(), "audio/wav")
                return
            if self.path == "/api/run":
                b = self._body()
                gid = b.get("graph_id", DEMO)
                result = SUITE.run(gid, force=b.get("force"))   # D4: force re-run bypasses the memo gate
                self._send(200, json.dumps(SUITE.state(gid, result)))
            elif self.path == "/api/set":
                b = self._body()
                gid = b.get("graph_id", DEMO)
                SUITE.set_config(gid, b.get("node"), b.get("config", {}))
                self._send(200, json.dumps(SUITE.state(gid)))
            elif self.path == "/api/move":              # C5: drag-end → write the sibling position/size
                b = self._body()
                gid = b.get("graph_id", DEMO)
                SUITE.set_position(gid, b["node"], b["x"], b["y"], b.get("w"), b.get("h"))
                self._send(200, json.dumps(SUITE.state(gid)))
            # --- on-canvas composition ---
            elif self.path == "/api/node":              # add a node from the palette
                b = self._body()
                gid = b.get("graph_id", DEMO)
                nid = SUITE.create_node(gid, b["type"], b.get("config", {}),
                                        position=b.get("position"))
                self._send(200, json.dumps({"id": nid, "state": SUITE.state(gid)}))
            elif self.path == "/api/connect":           # wire two nodes (type-checked)
                b = self._body()
                gid = b.get("graph_id", DEMO)
                SUITE.connect(gid, b["from_node"], b["from_port"], b["to_node"], b["to_port"])
                self._send(200, json.dumps(SUITE.state(gid)))
            elif self.path == "/api/delete-node":
                b = self._body()
                gid = b.get("graph_id", DEMO)
                SUITE.delete_node(gid, b["node"])
                self._send(200, json.dumps(SUITE.state(gid)))
            elif self.path == "/api/chat":                # right-hand-man — grounded conversation
                b = self._body()
                gid = b.get("graph_id", DEMO)
                self._send(200, json.dumps(SUITE.chat(b["message"], gid, focus=b.get("focus"))))
            elif self.path == "/api/mode":                # the presence dial — set the RHM mode
                b = self._body()
                SUITE.set_mode(b["mode"])
                self._send(200, json.dumps(SUITE.now(DEMO)))
            elif self.path == "/api/rhm-config":          # configure model/provider + persona
                b = self._body()
                self._send(200, json.dumps(SUITE.set_rhm_config(b)))
            elif self.path == "/api/coa":                 # decision-compiler UP — value-framing
                b = self._body()
                self._send(200, json.dumps(SUITE.coa(b["id"])))
            elif self.path == "/api/surface-output":      # F2: route a node's result to the inbox/COA
                b = self._body()
                gid = b.get("graph_id", DEMO)
                self._send(200, json.dumps(SUITE.surface_output(gid, b["node"])))
            elif self.path == "/api/react":               # watch-and-react ambient comment
                self._send(200, json.dumps(SUITE.react(DEMO)))
            elif self.path == "/api/revert":              # OPERATOR-only rollback of a self-change
                b = self._body()
                self._send(200, json.dumps(SUITE.revert_self_change(b["sha"])))
            # --- build-dispatch (self-growth), operable from the operator's UI ---
            elif self.path == "/api/propose":          # agent/operator dispatches a build
                b = self._body()
                self._send(200, json.dumps(SUITE.propose_node(b["name"], b["spec"])))
            elif self.path == "/api/resolve":           # OPERATOR approves/rejects (UI channel)
                b = self._body()
                SUITE.resolve_surfaced(b["id"], b["choice"], b.get("reason", ""))
                self._send(200, json.dumps({"ok": True, "surfaced": SUITE.list_surfaced()}))
            elif self.path == "/api/decision":           # a decision as a view over the log (audit)
                b = self._body()
                self._send(200, json.dumps(SUITE.decision_view(b["id"])))
            elif self.path == "/api/apply":             # apply (only succeeds if operator approved)
                b = self._body()
                r = SUITE.apply_surfaced(b["id"])       # dispatches by class; build-gate may reject
                self._send(200, json.dumps({"ok": not r.get("rejected"), "path": r.get("applied"),
                                            "kind": r["kind"], "error": r.get("error"),
                                            "types": sorted(SUITE.list_types())}))
            else:
                self._send(404, "{}")
        except Exception as e:                          # fail loud to the UI
            self._send(400, json.dumps({"error": f"{type(e).__name__}: {e}"}))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    seed_demo()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8770
    print(f"[bridge] UI face over the shared Suite at http://localhost:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
