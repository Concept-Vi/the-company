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
                    "stt": voice_stt.available(),
                    "stt_default": voice_stt.DEFAULT_PROVIDER,
                    "tts_up": engines[0]["up"],            # back-compat: the default (kokoro) up?
                    "engines": engines,                    # lane B: per-engine availability + voices
                    "voice_enabled": SUITE.voice_enabled()}))  # lane H: the per-mode voice toggle state
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
                engine = payload.get("engine")            # None/kokoro → default; unknown → fail loud
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
            elif self.path == "/api/review/start":         # B: start a review session (NOT graph-scoped — makes its own)
                b = self._body()
                self._send(200, json.dumps(SUITE.start_session(
                    b["item_ids"], mode=b.get("mode", "walkthrough"))))
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
