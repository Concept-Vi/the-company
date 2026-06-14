#!/usr/bin/env python3
"""ops/serve_rerank.py — the Company RERANK endpoint (jina-reranker-v3 listwise, CPU, 0 VRAM).
Surfaces ops/rerank.py:Reranker as an HTTP service (mirrors the embed/tts serving pattern) so the
cross-session recall scanner can POST query+candidates → reranked order WITHOUT an in-process torch
dep and WITHOUT a bridge to the overlord venv (Tim's direction 2026-06-14: no overlord bridge; served
endpoints / company-installed). Runs from ~/vllm-env (already carries torch+transformers — no new
install). CPU-pinned (CUDA_VISIBLE_DEVICES="" in the launcher) so it never touches the GPU loadout.

Contract:
  GET  /health           -> {status:"ok", backend, device, loaded}
  POST /rerank           -> body {query, candidates|texts: [str|{...}], top_n?} ->
                            {backend, count, ranking:[{item,text,rerank_score,orig_rank,rank}, ...]}
"""
from __future__ import annotations
import json, os, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
from ops.rerank import Reranker  # noqa: E402

PORT = int(os.environ.get("COMPANY_RERANK_PORT", "8008"))
BACKEND = os.environ.get("COMPANY_RERANK_BACKEND", "jina-v3")
_RR = None  # loaded once


def _reranker():
    global _RR
    if _RR is None:
        _RR = Reranker(backend=BACKEND, device="cpu").load()
    return _RR


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def do_GET(self):
        if self.path in ("/", "/health"):
            body = {"status": "ok", "backend": BACKEND, "device": "cpu", "loaded": _RR is not None}
            self._send(200, body)
        else:
            self._send(404, {"error": "GET /health | POST /rerank"})

    def do_POST(self):
        if self.path != "/rerank":
            self._send(404, {"error": "POST /rerank"})
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            b = json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            self._send(400, {"error": "body must be JSON"})
            return
        query = (b.get("query") or "").strip()
        candidates = b.get("candidates") or b.get("texts") or []
        top_n = b.get("top_n")
        if not query or not candidates:
            self._send(400, {"error": "need {query, candidates:[...]}"})
            return
        try:
            ranking = _reranker().rerank(query, candidates, top_n=top_n)
            self._send(200, {"backend": BACKEND, "count": len(ranking), "ranking": ranking})
        except Exception as e:
            self._send(500, {"error": f"{type(e).__name__}: {e}"})

    def _send(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    _reranker()  # load at startup so /health reflects readiness + first query isn't cold
    sys.stderr.write(f"[serve_rerank] {BACKEND} on 127.0.0.1:{PORT} (CPU)\n")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
