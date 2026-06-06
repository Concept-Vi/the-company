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
TTS_URL = os.environ.get("COMPANY_TTS_URL", "http://127.0.0.1:4123")   # local Kokoro service (default engine)

# voice-trial lane B — multi-engine TTS routing. The voice-module builder writes each engine as an
# HTTP service mirroring tts_service.py's contract (POST /tts {text,voice?,speed?}->wav · GET
# /voices · GET /health) on its OWN port. This map is the ONE source of truth for the port routing
# (used by BOTH /api/tts routing AND /api/voice status). The DEFAULT engine "kokoro" routes to
# TTS_URL (so COMPANY_TTS_URL still overrides the default — we do NOT hardcode kokoro to 4123 here,
# which would silently break that override). An absent `engine` field → kokoro (unchanged
# behaviour). An UNKNOWN engine → fail loud (no silent fallback to kokoro).
ENGINE_PORTS = {"chatterbox": 4124, "orpheus": 4125, "cosyvoice": 4126,
                "xtts": 4127, "qwen3tts": 4128}


def _tts_base_url(engine: str | None) -> str:
    """The base URL for a TTS engine. kokoro / None → TTS_URL (env-overridable default). A mapped
    engine → its 127.0.0.1:<port>. An unknown engine → ValueError (fail loud, names the known set —
    NEVER a silent fallback to kokoro, which would mask a typo and ship the wrong voice)."""
    if not engine or engine == "kokoro":
        return TTS_URL
    if engine not in ENGINE_PORTS:
        raise ValueError(
            f"unknown TTS engine {engine!r} — known: {['kokoro'] + sorted(ENGINE_PORTS)}. "
            f"Refusing to fall back to kokoro silently (fail loud).")
    return f"http://127.0.0.1:{ENGINE_PORTS[engine]}"


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
            elif path == "/api/self-change-log":           # the self-modification AUDIT LEDGER (Finding #1)
                self._send(200, json.dumps(SUITE.self_change_log(int(q.get("limit", 50)))))
            elif path == "/api/panels":
                self._send(200, json.dumps(SUITE.list_panels()))
            elif path == "/api/capabilities":
                self._send(200, json.dumps(SUITE.capabilities()))
            elif path == "/api/ui_info":                   # C1: the UI-component registry (sibling of object_info)
                self._send(200, json.dumps(SUITE.ui_info()))
            elif path == "/api/scope":                     # S3: ui://→code://→scope[] (the address→code join)
                self._send(200, json.dumps(SUITE.resolve_scope(q["address"])))
            elif path == "/api/self-changes-at":           # L5: "what did the system change HERE?" (§21.7#5)
                # The address-keyed READ over the self-change audit log: filters self_change_log by the
                # S3 address→code scope join. Missing `address` → KeyError → 400 (fail loud, mirrors
                # /api/scope). Revert from here stays on the EXISTING operator-only /api/revert (no new
                # revert route, gate untouched). Carries stale/note straight through so the surface
                # distinguishes "corpus stale — regenerate" from "no changes here" (never a silent lie).
                self._send(200, json.dumps(SUITE.self_changes_at(q["address"])))
            elif path == "/api/annotations":               # I6: the comment THREAD attached to a ui:// address
                # The address-keyed READ side of /api/annotate (POST). Missing `address` → KeyError →
                # 400 (fail loud, mirrors /api/scope). Suite.annotations_at validates the address (S0)
                # and returns the thread oldest-first. This is what R2 will gather at the operator's locus.
                self._send(200, json.dumps(SUITE.annotations_at(q["address"])))
            elif path == "/api/chats":                     # I7: the chat THREAD attached to a ui:// address
                # The address-keyed READ side of /api/attach-chat (POST). Missing `address` → KeyError →
                # 400 (fail loud, mirrors /api/scope + /api/annotations). Suite.chats_at validates the
                # address (S0) and returns the thread oldest-first. DISTINCT from /api/chat (GET = the
                # whole RHM history; POST = the RHM conversation) — this reads ONLY the turns attached to
                # `address`. This is what R2 will gather at the operator's locus (address-keyed context).
                self._send(200, json.dumps(SUITE.chats_at(q["address"])))
            elif path == "/api/address-history":            # L3: everything that happened AT a ui:// address
                # §21.7#1: clicking an element shows its addressed history. The address-keyed READ over
                # the event tail. Missing `address` → KeyError → 400 (fail loud, mirrors /api/scope +
                # /api/annotations + /api/chats). Suite.address_view validates the address (S0 grammar
                # gate) and returns the trajectory chronological — the addressed analogue of decision_view
                # (it WIDENS the audit-view machinery to an address key; the sid path is untouched).
                self._send(200, json.dumps(SUITE.address_view(q["address"])))
            elif path == "/api/stale-at":                  # L10: "is the cached result at this node's address
                # stale vs its CURRENT inputs?" (§21.7#10). A COSTED DERIVATION, not a served field — the FE
                # CALLS it only for a cached node (it recompiles + resolves input-hashes + recomputes the
                # _memo_sig + memo_get-compares; seams-engine Seam 8a). The key is a run://<graph>/<node>
                # node-instance address (NOT ui:// — `cached` is served per run:// node). Missing `address`
                # → KeyError → 400 (fail loud, mirrors /api/scope + /api/address-history). A malformed /
                # non-run:// address RAISES in stale_at_address → 400 too — a junk query never reads as a
                # silent 'fresh'. The verdict carries stale/unknown/reason/volatile (rule 4: an unevaluable
                # node is 'unknown' with a reason, never a silent false). READ-ONLY: the memo gate is unmutated.
                self._send(200, json.dumps(SUITE.stale_at_address(q["address"])))
            elif path == "/api/ref-versions":               # L6: the PRIOR VERSIONS of an addressed output
                # §21.7#6: a portal shows the CURRENT ref live; this is the trail of values the address has
                # HELD over time (Suite.ref_versions → store.ref_history index, appended on each set_ref).
                # The key is a run://<graph>/<node> OUTPUT address (NOT ui:// — versions accrue where set_ref
                # wrote; a PORTAL never writes, so the FE queries the address its config.ref POINTS AT). The
                # cas bytes survive (put_content write-once), so each prior version is fetchable by its cas.
                # Missing `address` → KeyError → 400 (fail loud, mirrors /api/stale-at + /api/address-history);
                # a malformed / non-run:// address RAISES in ref_versions → 400 too (a junk query never reads
                # as a silent 'no versions'). An address with no history returns versions:[] (honest empty).
                self._send(200, json.dumps(SUITE.ref_versions(q["address"])))
            elif path == "/api/review/current":            # B: the node at the cursor + its framing + ui:// target
                self._send(200, json.dumps(SUITE.present_current(q["session"])))
            elif path == "/api/review/status":             # B: the session's live status
                self._send(200, json.dumps(SUITE.session_status(q["session"])))
            elif path == "/api/journey/replay":             # L9: the ordered ui:// addresses of a recorded
                # journey — the FE steps the view through them via the PRESERVED forward resolveUiTarget (the
                # reverse of present_current's drive; no second navigation mechanism). Missing `journey` →
                # KeyError → 400 (fail loud, mirrors /api/review/current).
                self._send(200, json.dumps(SUITE.replay_journey(q["journey"])))
            elif path == "/api/journeys":                   # L9: the recorded journeys (id · step-count · done),
                # newest-first — the picker the FE replays from.
                self._send(200, json.dumps(SUITE.list_journeys_meta()))
            elif path == "/api/voice":                     # voice status: STT providers + per-engine TTS
                from voice import stt as voice_stt
                import urllib.request as _u

                def _probe(name, base):
                    """STATUS probe (lane B): is this engine's service up, and what voices does it
                    report? A status read NEVER raises on a down engine (unlike /api/tts which fails
                    loud) — it reports up:false so the picker can grey it out. Liveness is checked via
                    `GET /voices` (which is IN the shared engine contract — POST /tts + GET /voices)
                    rather than /health (NOT in the contract — the five new engines need not implement
                    it; only Kokoro happens to). One call → up AND the voice list together; Kokoro has
                    /voices too, so this is uniform across every engine."""
                    info = {"engine": name, "url": base, "up": False, "voices": []}
                    try:
                        with _u.urlopen(base + "/voices", timeout=3) as r:
                            v = json.loads(r.read() or b"{}")
                        info["up"] = True
                        info["voices"] = v.get("voices", [])
                        if v.get("default"):
                            info["default"] = v["default"]
                    except Exception:
                        pass                                # unreachable / not-yet-serving → up:false
                    return info

                engines = [_probe("kokoro", TTS_URL)] + [
                    _probe(name, f"http://127.0.0.1:{port}")
                    for name, port in sorted(ENGINE_PORTS.items())]
                self._send(200, json.dumps({
                    "stt": voice_stt.available(),          # back-compat: id → bool (the old shape)
                    "stt_default": voice_stt.stt_default(),  # back-compat: the default ear id
                    "stt_registry": voice_stt.available_stt(),  # the RICH ear registry (label/kind/detail)
                    "stt_active": SUITE.rhm_config().get("stt") or voice_stt.active_ear(),  # selected ear
                    "tts_up": engines[0]["up"],            # back-compat: the default (kokoro) up?
                    "engines": engines,                    # lane B: per-engine availability + voices
                    "voice_enabled": SUITE.voice_enabled()}))  # lane H: the per-mode voice toggle state
            elif path == "/api/personas":                  # G2.4/G3: the 5-cast registry the picker reads
                from voice import personas as voice_personas   # stdlib-only data module (3.14-importable)
                self._send(200, json.dumps(voice_personas.list_personas()))
            elif path == "/api/trial/sessions":            # G4.6: the recorded trial sessions (the debrief's set)
                self._send(200, json.dumps(SUITE.trial_sessions()))
            elif path == "/api/trial/transcript":          # G4.6: a trial session's CAS transcript (fail loud if unrecorded)
                self._send(200, json.dumps(SUITE.trial_transcript(q["session"])))
            elif path in ("/api/voice/services", "/api/voice/ears"):  # G4.7: voice-service lifecycle (ears+engines: up/warming/down + VRAM)
                from voice import lifecycle as voice_lc       # /api/voice/ears kept as a back-compat alias
                for w in voice_lc.poll_wake():                # G7-loadcost: a service just became up → record its WAKE-TIME
                    SUITE.emit_run_record("voice.load", w["wake_ms"], service=w["service"], vram_used_mb=w.get("vram_used_mb"))
                self._send(200, json.dumps(voice_lc.status()))
            elif path == "/api/roles":                     # G4.2: the model-ROLE registry (judge + future) the config lab binds
                self._send(200, json.dumps(SUITE.roles()))
            elif path == "/api/run-stats":                 # G7 rollup: op.run run-records → distributions (learning by use)
                self._send(200, json.dumps(SUITE.run_stats(op=q.get("op"))))
            elif path == "/api/knobs":                     # G8.1: the dynamic configurable-knob surface for a (loaded) model
                self._send(200, json.dumps(SUITE.knobs_for(model=q.get("model"), base_url=q.get("base_url"))))
            elif path == "/api/voice/paths":               # Tier-4: the swappable voice-path registry (pipeline vs s2s)
                self._send(200, json.dumps(SUITE.voice_paths()))
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

    def _voice_stream(self):
        """Tier-1 STREAMING voice turn: hear → think → SPEAK SENTENCE-BY-SENTENCE. The win over
        /api/voice/turn: instead of synthesising the WHOLE reply before any audio (the ~28s-on-a-long-
        reply wall), we split the reply into sentences and stream each one's audio AS IT'S SYNTHESISED —
        so the first words play at ~(silence+STT+brain+TTS-of-one-short-sentence), and the rest flows
        behind. Response = newline-delimited JSON events the FE reads + plays incrementally:
          {type:transcript,text} · {type:chunk,idx,text,wav_b64,ms} (per sentence) · {type:done,total_ms,reply}
        Engine-agnostic (sentence-chunking works with the CURRENT qwen3tts — no engine change; each
        sentence is a short, fast synth). Brain-token streaming is a later refinement; chunking the TTS
        (the dominant cost) is most of the win. Fail-loud surfaces as a {type:error} event then closes."""
        import base64 as _b64, re as _re, time as _t
        from urllib.parse import urlparse as _up, parse_qs as _pq
        from voice import loop as voice_loop, stt as voice_stt, lifecycle as voice_lc, personas as voice_personas
        self.close_connection = True
        vq = {k: v[0] for k, v in _pq(_up(self.path).query).items()}
        persona = (vq.get("persona") or "").strip()
        gid = vq.get("graph_id", DEMO)
        audio = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()

        import select as _sel, socket as _sock
        gone = [False]                                        # Tier-2: client-disconnect flag (cancel a speculative turn)

        def emit(obj):
            try:
                self.wfile.write((json.dumps(obj) + "\n").encode()); self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                gone[0] = True                                # client hung up (e.g. resumed talking) — stop, don't raise

        def client_gone():
            """Tier-2: PROACTIVELY detect a client disconnect (a speculative turn cancelled on resume) so
            we stop BEFORE the next expensive synth — more reliable + prompt than waiting for a write to
            fail (TCP buffers the first post-close write). select+MSG_PEEK: socket readable AND 0 bytes
            peeked = EOF (closed). Readable-with-data is unexpected here (body's read) → treat as alive."""
            if gone[0]:
                return True
            try:
                r, _, _ = _sel.select([self.connection], [], [], 0)
                if r and self.connection.recv(1, _sock.MSG_PEEK) == b"":
                    gone[0] = True
            except Exception:
                pass
            return gone[0]
        try:
            if not persona:
                raise ValueError("/api/voice/stream needs ?persona=<id> (fail loud)")
            if SUITE.rhm_config().get("voice_path") == "s2s":
                emit({"type": "error", "error": "voice_path is 's2s' but no S2S runner/model exists yet — "
                      "this is the pipeline route. Set voice_path=pipeline or download an S2S model."}); return
            p = voice_personas.get_persona(persona)               # fail loud on unknown persona
            _rc = SUITE.rhm_config()
            eng_override = (_rc.get("tts_engine") or "").strip() or None   # G4.2 engine/voice override slots
            voice_override = (_rc.get("tts_voice") or "").strip() or None
            eng = eng_override or p["engine"]                     # override wins; else the persona's engine
            t0 = _t.monotonic()
            speak_reply = SUITE.voice_enabled()
            # boot-on-demand (only if we'll speak)
            if speak_reply:
                svc = voice_lc.engine_service_for(eng)
                if svc and not voice_lc.is_up(voice_lc._loadable()[svc]):
                    emit({"type": "error", "error": f"engine {eng} ({svc}) is down — load it "
                          f"(POST /api/voice/load) or use ?boot=1 on /api/voice/turn first"}); return
            ear = SUITE.rhm_config().get("stt") or voice_stt.active_ear()
            heard = voice_stt.transcribe(audio, provider=ear)
            transcript = (heard.get("text") or "").strip()
            stt_ms = int((_t.monotonic() - t0) * 1000)
            emit({"type": "transcript", "text": transcript, "ms": stt_ms})
            if not transcript:
                raise RuntimeError("empty transcript — STT heard nothing (fail loud)")
            thought = SUITE.chat(transcript, gid)                 # the ONE in-process brain (full reply)
            reply = (thought.get("reply") or "").strip()
            think_ms = int((_t.monotonic() - t0) * 1000) - stt_ms
            emit({"type": "reply", "text": reply, "ms": think_ms})
            if not speak_reply:
                emit({"type": "done", "total_ms": int((_t.monotonic() - t0) * 1000), "spoke": False, "reply": reply}); return
            # split into sentences → synth + stream each AS IT'S READY (the streaming win)
            sentences = [s.strip() for s in _re.split(r'(?<=[.!?])\s+', reply) if s.strip()] or [reply]
            voice_arg = voice_override or voice_loop._voice_arg_for(p)   # G4.2: honour the engine/voice override
            done_n = 0
            for idx, sent in enumerate(sentences):
                if client_gone():                             # Tier-2: client disconnected → STOP before the next synth (don't burn TTS)
                    break
                cs = _t.monotonic()
                wav = voice_loop.speak(sent, eng, voice=voice_arg)   # `eng` honours the override; short sentence → fast synth
                emit({"type": "chunk", "idx": idx, "text": sent,
                      "wav_b64": _b64.b64encode(wav).decode(),
                      "ms": int((_t.monotonic() - cs) * 1000)})
                done_n = idx + 1
            total = int((_t.monotonic() - t0) * 1000)
            if gone[0]:                                       # cancelled mid-stream — record it (server-side; the socket's dead)
                SUITE.emit_run_record("voice.stream.cancelled", total, stt_ms=stt_ms, think_ms=think_ms,
                                      chunks_done=done_n, chunks_total=len(sentences), persona=persona, engine=eng)
                return
            SUITE.emit_run_record("voice.stream", total, stt_ms=stt_ms, think_ms=think_ms,
                                  chunks=len(sentences), persona=persona, engine=eng, ear=ear)
            emit({"type": "done", "total_ms": total, "spoke": True, "chunks": len(sentences), "reply": reply})
        except Exception as e:                                     # fail loud as a stream event, then close
            try:
                emit({"type": "error", "error": f"{type(e).__name__}: {e}"})
            except Exception:
                pass

    def do_POST(self):
        # HTTP/1.1 keeps sockets alive (needed for the GET /api/stream SSE). But a POST handler that
        # doesn't drain its request body (e.g. /api/react, the 404 branch) would leave bytes that the
        # next request on a reused connection mis-parses → garbled 400s in a browser (which pools
        # connections; curl uses a fresh socket per call, so it's invisible there). Force-close POST
        # sockets — GET (incl. the stream) still keeps alive.
        self.close_connection = True
        try:
            if self.path == "/api/stt":                   # raw audio bytes in → transcript out
                # The ear is chosen by the SELECTED provider (rhm_config().stt — the config slot the
                # suite lane added, mirroring the brain-model slot), NOT a literal default. This closes
                # the bug where the bridge defaulted assemblyai while the loop defaulted local — ONE
                # source of selection now. A selected-but-down ear → transcribe() raises LOUD (fail
                # loud, no fallback); _send's except surfaces it to the UI.
                from voice import stt as voice_stt
                ln = int(self.headers.get("Content-Length", 0))
                audio = self.rfile.read(ln)
                ear = SUITE.rhm_config().get("stt") or voice_stt.active_ear()
                self._send(200, json.dumps(voice_stt.transcribe(audio, provider=ear)))
                return
            if self.path == "/api/voice/stt-partial":     # Tier-2: PARTIAL transcript of the audio-so-far (FE drives the window)
                from voice import stt as voice_stt
                import time as _t
                ln = int(self.headers.get("Content-Length", 0)); audio = self.rfile.read(ln)
                ear = SUITE.rhm_config().get("stt") or voice_stt.active_ear()
                t0 = _t.monotonic()
                r = voice_stt.transcribe_partial(audio, provider=ear)
                r["ms"] = int((_t.monotonic() - t0) * 1000)
                self._send(200, json.dumps(r))
                return
            if self.path == "/api/tts":                   # text in → wav out (routed by engine)
                # lane B: parse the body to read the optional `engine` field, route to that engine's
                # service (kokoro/absent → TTS_URL; others → ENGINE_PORTS), and forward ONLY the
                # downstream contract {text,voice?,speed?} (engine stripped — the engine's /tts must
                # not need to know its own name). Fail loud naming the engine+port if it's down (no
                # silent failure — AGENTS.md rule 4). DEFAULT (no engine) is byte-identical to before.
                import urllib.error as _ue
                import urllib.request as _u
                raw = self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}"
                payload = json.loads(raw or b"{}")
                engine = payload.get("engine")            # explicit engine wins; unknown → fail loud
                if not engine:
                    # No explicit engine → speak in the CONFIGURED voice (the tts_engine override, else the
                    # active persona's engine) — NOT a generic kokoro default. So EVERY voice-out (a text
                    # reply via speakReply, a voice reply, walkthrough narration) uses the chosen Company
                    # voice. Resolved the SAME way /api/voice/stream resolves it (one source — eng_override
                    # → persona.engine). Falls back to kokoro (TTS_URL) only when nothing is configured
                    # (no override AND no persona, or the persona declares no engine).
                    _rc = SUITE.rhm_config()
                    engine = (_rc.get("tts_engine") or "").strip() or None
                    if not engine and (_rc.get("persona") or "").strip():
                        from voice import personas as _vp
                        try:
                            engine = (_vp.get_persona(_rc["persona"].strip()) or {}).get("engine") or None
                        except Exception:
                            engine = None                 # unknown persona → kokoro fallback (never crash a reply)
                base = _tts_base_url(engine)              # raises ValueError on an unknown engine
                fwd = {k: v for k, v in payload.items() if k != "engine"}
                req = _u.Request(base + "/tts", data=json.dumps(fwd).encode(),
                                 headers={"Content-Type": "application/json"})
                try:
                    with _u.urlopen(req, timeout=60) as r:
                        self._send(200, r.read(), "audio/wav")
                except (_ue.URLError, ConnectionError, OSError) as e:
                    port = base.rsplit(":", 1)[-1]
                    raise RuntimeError(
                        f"{engine or 'kokoro'} TTS service at {base} (port {port}) unreachable: "
                        f"{type(e).__name__}: {e} — start the engine's service (fail loud).")
                return
            if self.path.split("?")[0] == "/api/voice/turn":   # G1.1: ONE live turn — hear→think→speak
                # The core circuit, reusing voice.loop.loop_turn (NOT a parallel hear/think/speak). We
                # inject the IN-PROCESS Suite.chat as the brain step (loop.py's designed injection point)
                # AND pass the selected ear explicitly → loop_turn makes NO HTTP call back to this bridge
                # (one in-process brain, one event log). Input: raw audio body + ?persona=<id>. Output:
                # JSON with the wav base64'd (a turn is hear→think→speak; the reply text + the spoken wav
                # travel together, so the UI shows the transcript/reply AND plays the audio from one call).
                # Fail loud: empty transcript, unknown persona, a down engine/ear all raise → 400.
                import base64 as _b64
                from urllib.parse import urlparse as _up, parse_qs as _pq
                from voice import loop as voice_loop, stt as voice_stt
                vq = {k: v[0] for k, v in _pq(_up(self.path).query).items()}
                persona = (vq.get("persona") or "").strip()
                if not persona:
                    raise ValueError("/api/voice/turn needs ?persona=<id> (fail loud)")
                gid = vq.get("graph_id", DEMO)
                audio = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                if not audio:
                    raise ValueError("/api/voice/turn got empty audio (fail loud)")
                if SUITE.rhm_config().get("voice_path") == "s2s":     # Tier-4: s2s path has no runner yet
                    raise RuntimeError("voice_path is 's2s' but no S2S runner/model exists yet — this is "
                                       "the PIPELINE route. Set voice_path=pipeline, or download an S2S "
                                       "model + build the s2s runner. Refusing to silently use the pipeline.")
                # G4.4 voice gate: the per-mode voice_enabled toggle. When voice is OFF (a text-only
                # presence), the turn is hear→think only — no speak, and NO engine boot for nothing.
                speak_reply = SUITE.voice_enabled()
                # BOOT-ON-DEMAND ("make it all live"): the persona needs its TTS engine up. Check BEFORE
                # the turn so we don't burn a brain call then fail at speak. Only when we WILL speak. If
                # down: ?boot=1 launches it (returns 'booting' — the UI shows warming + retries when up;
                # we do NOT block the request ~25s); else a legible refusal naming the load endpoint.
                from voice import lifecycle as voice_lc, personas as voice_personas
                _rc = SUITE.rhm_config()
                eng_override = (_rc.get("tts_engine") or "").strip() or None   # G4.2 engine override slot
                voice_override = (_rc.get("tts_voice") or "").strip() or None
                eng = eng_override or voice_personas.get_persona(persona)["engine"]   # override wins; else persona
                if speak_reply:
                    svc = voice_lc.engine_service_for(eng)
                    if svc and not voice_lc.is_up(voice_lc._loadable()[svc]):
                        if vq.get("boot") == "1":
                            booted = voice_lc.load(svc)           # warming; fail-loud if it won't fit
                            self._send(200, json.dumps({"booting": booted, "persona": persona, "engine": eng,
                                "note": f"engine {eng} is loading — retry the turn when status() shows it up"}))
                            return
                        raise RuntimeError(
                            f"persona {persona!r} needs TTS engine {eng!r} ({svc}) which is DOWN — load it "
                            f"first (POST /api/voice/load {{\"service\":\"{svc}\"}}) or call this with ?boot=1. "
                            f"Refusing a silent stall (fail loud).")
                ear = SUITE.rhm_config().get("stt") or voice_stt.active_ear()
                # G7 timing: split the turn into stt/think/tts using loop_turn's EXISTING callbacks as
                # markers (on_transcript fires after STT, on_reply after THINK) — no new plumbing.
                import time as _t
                marks = {}
                t0 = _t.monotonic()
                r = voice_loop.loop_turn(
                    audio, persona, graph_id=gid, stt_provider=ear, speak_reply=speak_reply,
                    think_fn=lambda txt: SUITE.chat(txt, gid),    # the ONE in-process brain
                    on_transcript=lambda _t_, _m=marks: _m.__setitem__("stt", int((_t.monotonic()-t0)*1000)),
                    on_reply=lambda _r_, _m=marks: _m.__setitem__("think_done", int((_t.monotonic()-t0)*1000)))
                total = int((_t.monotonic() - t0) * 1000)
                stt_ms = marks.get("stt")
                think_ms = (marks["think_done"] - stt_ms) if ("think_done" in marks and stt_ms is not None) else None
                tts_ms = (total - marks["think_done"]) if "think_done" in marks else None
                SUITE.emit_run_record("voice.turn", total, stt_ms=stt_ms, think_ms=think_ms,
                                      tts_ms=tts_ms, persona=persona, engine=r.get("engine"),
                                      ear=ear, spoke=r.get("spoke", True))
                wav = r.pop("wav", b"")
                r["wav_b64"] = _b64.b64encode(wav).decode()       # the spoken reply, travels with the text
                r["timing"] = {"total_ms": total, "stt_ms": stt_ms, "think_ms": think_ms, "tts_ms": tts_ms}
                self._send(200, json.dumps(r))
                return
            if self.path.split("?")[0] == "/api/voice/stream":   # G7/Tier-1: STREAMING turn — speak sentence-by-sentence
                self._voice_stream()
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
            elif self.path == "/api/surface-review":       # A: surface a review item into the one queue
                b = self._body()
                self._send(200, json.dumps(SUITE.surface_review(
                    b["item"], origin=b.get("origin", "responsive"))))
            elif self.path == "/api/capture-idea":         # A4: capture a fleeting idea (generative review item)
                b = self._body()
                self._send(200, json.dumps(SUITE.idea_capture(b["text"])))
            elif self.path == "/api/build-intent":          # T0-WIRE: the REAL production entry seam for the
                # decision→implementation wire. The operator (this is the OPERATOR face, not the agent
                # face) mints a build-intent — a declared-scope decision that, once they APPROVE it via
                # /api/resolve (operator-only), the WIRE-LOOP dispatches to `claude -p`. This route only
                # SURFACES the intent (resolved=None); it does NOT dispatch (dispatch is dispatch_decision,
                # off this face). So the wire's "off the agent face / operator-only approve" gates hold:
                # this is the missing FRONT DOOR (the closure + UI already existed but nothing in
                # production could populate the builds lane). Fail loud on a missing spec (no silent no-op).
                b = self._body()
                spec = b.get("spec")
                if not spec or not str(spec).strip():
                    raise ValueError("/api/build-intent needs a non-empty 'spec' (fail loud)")
                self._send(200, json.dumps(SUITE.surface_build_intent(
                    str(spec).strip(), scope=b.get("scope"),
                    consequence_class=b.get("consequence_class", "decision_build"),
                    why=b.get("why", ""))))
            elif self.path == "/api/intent-at":              # L1 (§21.4#2): a COMMENT-AT-AN-ADDRESS becomes a
                # build-intent that surfaces for approval AT that address. The addressed-feedback → wire
                # entry seam — mirrors /api/build-intent (OPERATOR face), but the scope is DERIVED from the
                # ui:// address via S3 (resolve_scope) instead of declared by the caller, and the comment is
                # RECORDED at the address via I6 (ingest_comment). It only SURFACES the intent (resolved=None);
                # approval stays on the EXISTING operator-only /api/resolve, and dispatch-on-approve is L2 (a
                # separate switch — this route NEVER dispatches). An orphan/stale address → EMPTY scope =
                # DENY-ALL (never fabricated). Fail loud on a missing address/text (S0 + I6 gates → 400).
                b = self._body()
                addr = b.get("address")
                if not addr or not str(addr).strip():
                    raise ValueError("/api/intent-at needs a non-empty 'address' (fail loud)")
                text = b.get("text") or b.get("comment")
                if not text or not str(text).strip():
                    raise ValueError("/api/intent-at needs a non-empty 'text' comment (fail loud)")
                self._send(200, json.dumps(SUITE.surface_intent_at(
                    str(addr).strip(), str(text).strip(), source=b.get("source", "operator"),
                    consequence_class=b.get("consequence_class", "decision_build"),
                    why=b.get("why", ""))))
            elif self.path == "/api/review/start":         # B: start a review session (NOT graph-scoped — makes its own)
                b = self._body()
                self._send(200, json.dumps(SUITE.start_session(
                    b["item_ids"], mode=b.get("mode", "walkthrough"))))
            elif self.path == "/api/walkthrough/start":     # C4: the mode-selection → ORGAN-start seam.
                # SELECTING the guided/walkthrough experience: this binds the cosmetic presence-dial
                # 'walkthrough' MODE to the real walkthrough ORGAN (start_walkthrough sets the dial AND
                # starts the organ over the pending items) — closing the naming trap (a dial mode that
                # only narrated vs. the screen-driving engine). Optional `item_ids` to pre-select a set;
                # absent → it walks every pending unresolved inbox item. FAIL LOUD (no silent no-op):
                # nothing pending → {organ_started:False, reason} (the dial is set, the surface is told).
                # The FE that CALLS this on dial-select + drives the per-step view is the FE show-me lane.
                b = self._body()
                self._send(200, json.dumps(SUITE.start_walkthrough(b.get("item_ids"))))
            elif self.path == "/api/guide/start":           # C1: the SYSTEM-INITIATED guided sequence ("show
                # me how" tour). start_guide composes the SAME walkthrough organ over ui:// ELEMENT addresses
                # (not inbox items): it sets the dial to 'walkthrough' AND starts a session whose steps each
                # narrate the element's corpus how-to (address_help) + spotlight the real element (G-43).
                # MODEL-FREE by construction (present_current's guide branch reads the corpus, never a model).
                # Optional `topic` to pick a sequence; absent → the default orientation tour. FAIL LOUD: no
                # registered addresses → {organ_started:False, reason} (the dial is set, the surface is told).
                b = self._body()
                self._send(200, json.dumps(SUITE.start_guide(b.get("topic"))))
            elif self.path == "/api/debrief/start":         # voice-trial lane F: walk Tim back through the
                # recorded trial sessions. start_debrief SURFACES each recorded session as a review item
                # (carrying its real CAS transcript) then drives the SAME walkthrough organ — so the
                # debrief is read/advanced via the EXISTING /api/review/{current,next,status} routes;
                # only this START is net-new. Verdicts are captured via /api/resolve (operator-only),
                # exactly like a review session. Fail loud on missing session_ids (no silent no-op).
                b = self._body()
                sids = b.get("session_ids")
                if not sids:
                    raise ValueError("/api/debrief/start needs a non-empty 'session_ids' list (fail loud)")
                self._send(200, json.dumps(SUITE.start_debrief(
                    sids, host_persona=b.get("host_persona"), mode=b.get("mode", "walkthrough"))))
            elif self.path == "/api/trial/turn":            # G4.6: record one spoken trial turn (durable event + CAS)
                b = self._body()
                self._send(200, json.dumps(SUITE.trial_record_turn(
                    b["session_id"], b.get("role", "operator"), b["text"], b.get("character"))))
            elif self.path == "/api/trial/feedback":        # G4.6: record Tim's spoken feedback during a trial
                b = self._body()
                self._send(200, json.dumps(SUITE.trial_record_feedback(
                    b["session_id"], b["text"], b.get("character"))))
            elif self.path == "/api/trial/reflection":      # G4.6: record the character's own reflection-note
                b = self._body()
                self._send(200, json.dumps(SUITE.trial_record_reflection(
                    b["session_id"], b["text"], b.get("character"))))
            elif self.path in ("/api/voice/load", "/api/voice/ear/load"):    # G4.7: load a voice service (ear OR engine; 'warming'; fail-loud if it won't fit)
                from voice import lifecycle as voice_lc
                b = self._body()
                self._send(200, json.dumps(voice_lc.load(b.get("service") or b["ear"])))
            elif self.path in ("/api/voice/unload", "/api/voice/ear/unload"):  # G4.7: unload a voice service → frees its VRAM
                from voice import lifecycle as voice_lc
                b = self._body()
                self._send(200, json.dumps(voice_lc.unload(b.get("service") or b["ear"])))
            elif self.path == "/api/voice/switch":  # Option A: pick a persona → set it AS active + auto-load its voice
                # "switch between them all" without manual VRAM juggling: set the active persona (brain
                # character + voice), then EVICT the previous voice engine and cold-load this persona's
                # engine (the card can't hold them all — accepted). Returns 'warming' → poll
                # /api/voice/services for 'up'. Fail loud on unknown persona, and (via the budget gate)
                # if the voice won't fit even after eviction (e.g. orpheus + a big brain).
                from voice import lifecycle as voice_lc, personas as voice_personas
                b = self._body()
                persona_id = (b.get("persona") or "").strip()
                if not persona_id:
                    raise ValueError("/api/voice/switch needs {persona} (fail loud)")
                p = voice_personas.get_persona(persona_id)        # fail loud on an unknown persona
                rc = SUITE.rhm_config()
                eng = (rc.get("tts_engine") or "").strip() or p["engine"]   # override wins, else persona's engine
                SUITE.set_rhm_config({"persona": persona_id})
                svc = voice_lc.engine_service_for(eng)
                if not svc:                                       # always-on engine (kokoro) — nothing to load
                    out = {"persona": persona_id, "engine": eng, "service": None, "state": "up",
                           "note": "always-on engine — no load step"}
                else:
                    out = {"persona": persona_id, "engine": eng, "service": svc, **voice_lc.switch_to(svc)}
                self._send(200, json.dumps(out))
            elif self.path == "/api/voice/finished-thought":  # G1.3: the semantic endpoint judge (brain-side)
                b = self._body()
                self._send(200, json.dumps(SUITE.is_finished_thought(b.get("text", ""))))
            elif self.path == "/api/review/next":          # B: Next — open the gate, fire the step, advance
                b = self._body()
                self._send(200, json.dumps(SUITE.next(b["session"])))
            elif self.path == "/api/journey/start":         # L9: open a journey-record (the REVERSE capture).
                # DISTINCT from /api/review/start (the review-session organ): a journey records NAVIGATION
                # (an ordered ui:// click-path), a session records a REVIEW (item-ids with a cursor). No body.
                self._send(200, json.dumps(SUITE.start_journey()))
            elif self.path == "/api/journey/step":          # L9: append one addressed step to an OPEN journey.
                # The address is S0-validated in the Suite (parse_ui_address raises → 400 here, fail loud,
                # mirrors /api/annotate). Appending to a finalized/absent journey raises → 400 (no silent no-op).
                b = self._body()
                self._send(200, json.dumps(SUITE.append_journey_step(b["journey"], b["address"])))
            elif self.path == "/api/journey/stop":          # L9: finalize a journey → it becomes replayable.
                b = self._body()
                self._send(200, json.dumps(SUITE.stop_journey(b["journey"])))
            elif self.path == "/api/react":               # watch-and-react ambient comment
                self._send(200, json.dumps(SUITE.react(DEMO)))
            elif self.path == "/api/revert":              # OPERATOR-only rollback of a self-change
                b = self._body()
                self._send(200, json.dumps(SUITE.revert_self_change(b["sha"])))
            # --- build-dispatch (self-growth), operable from the operator's UI ---
            elif self.path == "/api/propose":          # agent/operator dispatches a build
                b = self._body()
                self._send(200, json.dumps(SUITE.propose_node(b["name"], b["spec"])))
            elif self.path == "/api/act":               # I2: the click-emission seam — a DETERMINISTIC
                # human click ships a STRUCTURED {verb, address, args} that drives _dispatch_rhm_action
                # DIRECTLY (bypassing the unreliable model-prose parse) — the emission RELOCATION
                # (§21.4#1). OPERATOR face only (beside /api/resolve, NOT the MCP/agent face): a human
                # click is an operator act, where the no-self-approve gates already live (seams-rhm
                # headline). The 7-verb whitelist + no-self-apply ride along INSIDE the dispatcher; the
                # verb-class governance posture + the "did X" confirmation are re-folded by Suite.act.
                # Fail loud on a missing verb (no silent no-op).
                b = self._body()
                gid = b.get("graph_id", DEMO)
                verb = b.get("verb")
                if not verb or not str(verb).strip():
                    raise ValueError("/api/act needs a non-empty 'verb' (fail loud)")
                self._send(200, json.dumps(SUITE.act(
                    str(verb).strip(), gid, address=b.get("address"), args=b.get("args"))))
            elif self.path == "/api/annotate":          # I6: attach a comment/annotation to a ui:// ADDRESS
                # NET-NEW and SEPARATE from /api/resolve's comment choice (which annotates a surfaced
                # item by id, suite.py:3045) and from /api/act (I2): nothing else attaches BY ADDRESS.
                # OPERATOR face (beside the others). Suite.annotate validates the address against the S0
                # grammar (raises → 400 here) and persists keyed by address; retrieve via GET
                # /api/annotations?address=…. Feeds R2 (address-keyed context resolution). Fail loud on a
                # missing address (no silent no-op — AGENTS.md rule 4).
                b = self._body()
                addr = b.get("address")
                if not addr or not str(addr).strip():
                    raise ValueError("/api/annotate needs a non-empty 'address' (fail loud)")
                # L4: route through `ingest_comment` (NOT the pure `annotate` leaf) — a clicked comment
                # IS the twin's LOCATED gold label: it records the I6 annotation AND emits one additive
                # located-gold chat turn (operator=gold, address-stamped) that rides the existing
                # `append_chat → training_signal` pipe. This is the WIRED production entry the FE's
                # annotate-click hits; the same entry the I5 router composes (single-source). Returns the
                # annotation rec (unchanged response shape — retrieve the comment via GET /api/annotations).
                self._send(200, json.dumps(SUITE.ingest_comment(
                    str(addr).strip(), b.get("text", ""), source=b.get("source", "operator"))))
            elif self.path == "/api/pin":                # X7: pin/unpin an attached item at a ui:// ADDRESS
                # OPERATOR face (beside /api/annotate, /api/attach-chat) — the SET path for the dead pin
                # term: `pinned` is read in `_r2_score` but nothing set it. This records a pin/unpin of the
                # attached item at (address, target_ts) so the gather's existing read picks up the real flag
                # → a pinned item holds in the bounded R2 window. OPERATOR-ONLY, OFF the MCP face (not in
                # RHM_VERBS — no-bypass preserved). Suite.pin S0-validates the address (raises → 400) AND
                # fails loud if (address, target_ts) names no real attached item. Default pinned=True.
                b = self._body()
                addr = b.get("address")
                target_ts = b.get("target_ts")
                if not addr or not str(addr).strip():
                    raise ValueError("/api/pin needs a non-empty 'address' (fail loud)")
                if not target_ts or not str(target_ts).strip():
                    raise ValueError("/api/pin needs a non-empty 'target_ts' (the item's handle) (fail loud)")
                self._send(200, json.dumps(SUITE.pin(
                    str(addr).strip(), str(target_ts).strip(), pinned=bool(b.get("pinned", True)))))
            elif self.path == "/api/attach-chat":        # I7: attach a chat turn to a ui:// ADDRESS (the
                # dropped 4th attach-type, §21.1's chat:// branch). RIDES the open append_chat record with
                # one additive `address` field — NO separate chat store (one-source). DISTINCT from
                # /api/chat (the RHM conversation): this attaches a turn AT an address, retrieve via GET
                # /api/chats?address=…. Suite.attach_chat validates the address against the S0 grammar
                # (raises → 400 here) + tags source/grade (echo-guard) + flows through training_signal
                # unchanged. Feeds R2 (address-keyed context resolution). Fail loud on a missing address.
                b = self._body()
                addr = b.get("address")
                if not addr or not str(addr).strip():
                    raise ValueError("/api/attach-chat needs a non-empty 'address' (fail loud)")
                self._send(200, json.dumps(SUITE.attach_chat(
                    str(addr).strip(), b.get("text", ""),
                    role=b.get("role", "user"), source=b.get("source"))))
            elif self.path == "/api/approve-reach":      # X16: the operator authorizes HOW FAR a build's
                # edit propagates — the reach-approval. OPERATOR face (beside /api/resolve, /api/pin — NOT
                # the MCP/agent face). DEFAULT is the pointed address only (the build's declared scope is
                # unchanged); this widens it to include the files the APPROVED blast-radius members live in.
                # approve_reach validates each member against the PERSISTED blast_radius the operator saw
                # (consent-time) — a member NOT in that radius RAISES (→ 400), so this is never a
                # scope-injection path that defeats empty-scope=DENY-ALL. Operator-only, off the MCP face
                # (not in RHM_VERBS — no-bypass + the 7-verb whitelist + no-self-apply preserved). Fail loud
                # on a missing id / members (no silent no-op — AGENTS.md rule 4).
                b = self._body()
                if not b.get("id") or not str(b["id"]).strip():
                    raise ValueError("/api/approve-reach needs a non-empty 'id' (the build-intent) (fail loud)")
                members = b.get("members")
                if not members or not isinstance(members, list):
                    raise ValueError("/api/approve-reach needs a non-empty 'members' list (the approved "
                                     "blast-radius members) (fail loud)")
                self._send(200, json.dumps(SUITE.approve_reach(
                    str(b["id"]).strip(), [str(m) for m in members], reason=b.get("reason", ""))))
            elif self.path == "/api/resolve":           # OPERATOR approves/rejects/comments/skips (UI channel)
                b = self._body()
                # D: additive session tagging + the comment/skip/decide vocabulary; existing callers
                # (id+choice+reason) are unchanged. Operator-only — never on the MCP face (no-bypass).
                v = SUITE.resolve_surfaced(b["id"], b["choice"], b.get("reason", ""),
                                           session_id=b.get("session"), position=b.get("position"))
                self._send(200, json.dumps({"ok": True, "verdict": v, "surfaced": SUITE.list_surfaced()}))
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
