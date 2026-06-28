#!/usr/bin/env python3
"""ops/fabric_openai_adapter.py — exposes the company's RIGHT HAND MAN as an OpenAI model for OpenWebUI.

Registered in OpenWebUI as a Connection, it makes the RHM appear as a model named 'operator' that you can
chat — and therefore VOICE-CHAT with OpenWebUI's native call UI (mic in, spoken out). It is NOT a parallel
brain: every turn routes to the company's real RHM via the bridge's /api/chat (SUITE.chat), so

  • the operator's BRAIN is the RHM's brain — whatever model the company loadout selects (rhm_config.model),
    changeable in the company (or /api/rhm-config); the operator follows it with no change here (loadout-linked).
  • the operator's CAPABILITIES are the RHM's governed verbs (run/propose/build/consult/show/configure/
    load_voice/…) — it observes the fabric (sessions/channels) and acts within its governance.

This replaced the earlier ad-hoc 'operator' (a separate cloud-LLM NL→ops island) — one operator now, = the RHM.
"""
from __future__ import annotations
import json, os, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BRIDGE = os.environ.get("COMPANY_BRIDGE", "http://127.0.0.1:8770")
RHM_CHAT = BRIDGE + "/api/chat"
PORT = int(os.environ.get("FABRIC_ADAPTER_PORT", "4300"))
GRAPH = os.environ.get("RHM_GRAPH", "codebase")
MODEL_ID = "operator"                                          # how the RHM appears in OpenWebUI's model picker


def rhm_reply(messages: list) -> str:
    """Route the conversation to the real RHM (the company brain). Returns its reply text."""
    user = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "user"), "")
    body = json.dumps({"message": user, "graph_id": GRAPH}).encode()
    req = urllib.request.Request(RHM_CHAT, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.load(r)
    return d.get("reply") or d.get("text") or d.get("answer") or "(no reply from the RHM)"


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/").endswith("/models"):
            self._send(200, json.dumps({"object": "list", "data": [
                {"id": MODEL_ID, "object": "model", "created": 0, "owned_by": "company-rhm"}]}).encode())
        else:
            self._send(200, b'{"ok":true}')

    def do_POST(self):
        if not self.path.endswith("/chat/completions"):
            self._send(404, b'{"error":"not found"}'); return
        n = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(n) or b"{}")
        model = req.get("model", MODEL_ID)
        stream = bool(req.get("stream"))
        try:
            reply = rhm_reply(req.get("messages", []))
        except Exception as e:
            reply = f"(could not reach the RHM: {type(e).__name__}: {e})"
        cid = "chatcmpl-rhm"
        if stream:
            self.send_response(200); self.send_header("Content-Type", "text/event-stream"); self.end_headers()
            def chunk(delta, finish=None):
                o = {"id": cid, "object": "chat.completion.chunk", "model": model,
                     "choices": [{"index": 0, "delta": delta, "finish_reason": finish}]}
                self.wfile.write(f"data: {json.dumps(o)}\n\n".encode()); self.wfile.flush()
            chunk({"role": "assistant"}); chunk({"content": reply}); chunk({}, "stop")
            self.wfile.write(b"data: [DONE]\n\n"); self.wfile.flush()
        else:
            o = {"id": cid, "object": "chat.completion", "model": model,
                 "choices": [{"index": 0, "message": {"role": "assistant", "content": reply}, "finish_reason": "stop"}]}
            self._send(200, json.dumps(o).encode())


if __name__ == "__main__":
    print(f"fabric-openai-adapter (operator = RHM) on :{PORT} → {RHM_CHAT}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
