"""runtime/session_supervisor.py — the SESSION SUPERVISOR service (Session Fabric F1.1, guide §A).

The fabric's engine spine: ONE long-running service that OWNS N concurrent Claude Code
subprocesses — spawn (new | --resume | --resume --fork-session) · inject (a user turn pushed
into a live session) · interrupt · teardown — and fans each session's events to subscribers
as ndjson. It is the push tier the T2 harness proved (~/xsession-tests/RESULTS.md): a claude
process held open under `--input-format stream-json` accepts injected turns while idle, with
full memory and the same session_id.

THE LAWS THIS SERVICE CARRIES (each cites its ruling):
  · EXPOSURE (audit B3): binds 127.0.0.1 ONLY. There is deliberately no env var to widen the
    bind — any wider exposure (tailnet/authed) is an explicit recorded decision + a code change
    here, never a quiet env flip.
  · SINGLE WRITER (audit C6 / synthesis §3 landmine): this service is the ONLY process that
    emits `agent_sessions.*` events onto the shared events.jsonl — the bridge and the MCP face
    route fabric intents here via the mailbox and emit nothing fabric-shaped themselves. One
    writer → the in-process seq lock suffices → no cross-process duplicate-seq hazard.
  · ONE OWNER PER SESSION (T1): the supervisor is the only process that resumes a session it
    has live — concurrent resume elsewhere talks to a disk-loaded copy, never the live mind.
  · ENFORCED WALL-CLOCK (audit C3): a per-turn watchdog REAPS a session whose turn exceeds
    COMPANY_FABRIC_TURN_TIMEOUT_S (default 900 — implement.py DEFAULT_TIMEOUT_S precedent,
    the constant that actually enforces; ui_claude_session.TURN_TIMEOUT_S was a dead constant
    and this module does not repeat that mistake). A silently-hung no-output subprocess is
    reaped, never blocks forever.
  · CONCURRENCY CAP (audit C9): COMPANY_FABRIC_CONCURRENCY (call-time env read, default 3 —
    the implement.py CONCURRENCY_CAP precedent) caps live sessions AND consult fan copies;
    above it the service refuses LOUD with a teaching error that names the cap, the env var,
    what is live, and how to free a slot.
  · PERMISSION POSTURE: COMPANY_FABRIC_PERMISSION (call-time read, default "plan" — read-only;
    the COMPANY_WIRE_PERMISSION / COMPANY_PANEL_PERMISSION twin). acceptEdits is opt-in only.
  · THE FLOOR: this is a SERVICE (an operator-sanctioned process like the bridge), NOT the MCP
    face. mcp_face NEVER imports this module; the face writes *intents* to the mailbox and this
    service is the only thing that launches/resumes claude processes (synthesis §6.3 split).
  · NO ORPHANS: every owned subprocess is terminated on teardown/SIGTERM/exit (atexit +
    signal handlers); under systemd the cgroup is the second net.

TRANSPORT (NET-NEW, T2-proven — audit N4 honesty): held-open stdin + `--input-format
stream-json` + `--output-format stream-json`. `ui_claude_session.run_turn` is NOT reused for
the loop (it has no stdin-injection mode — one subprocess per turn, prompt as argv); what IS
reused from it: binary resolution (_find_claude), the strict company MCP config, and the
stream-event parsing shapes. Per-turn `--resume` re-spawn remains the documented fallback if
the held-open loop misbehaves under real load.

MAILBOX (coordinate-by-contract, guide §C — this module CONSUMES the leaf, it does not build
§C's tools): intents ride `<store>/agent_sessions/mail.jsonl`, one json object per line:
  {id, to: "session://<id>", from, verb: deliver|wake|consult, cas, [copies]}
Body text lives in cas (store.get_content) — messages stay small (<4KB single O_APPEND write,
the fs_store ref-history atomicity argument). Consumption is a per-consumer CURSOR (a ref —
`agent_sessions/cursor:supervisor` — holding the consumed byte offset; synthesis §2.3's
cheaper-than-RMW design). Replies/acks are appended to the SAME leaf via the store's own
`append_agent_mail` (verb: reply | error, `re` = the intent id, `thread` = the intent's thread
— seq-stamped + inbox-visible; the first commit's raw-append seam is closed), and the completed turn is claimed
durably as an `agent_sessions.turn` event (the _emit_durable class — its loss would change
behavior). F1 SIMPLIFICATION (stated, not hidden): intents are consumed strictly in order; an
intent whose target is mid-turn HOLDS the cursor (head-of-line blocking, retried next poll) so
a crash never skips an unhandled intent. A per-target queue is a later refinement.

VERBS = ROUTING DECISIONS (guide prime principle 2):
  DELIVER → inject into a session this supervisor holds live.
  WAKE    → spawn a supervisor-owned process on a non-live session id (`--resume`), then inject.
  CONSULT → spawn on a FORKED copy (`--resume --fork-session`, T4-proven non-destructive),
            N-fan ≤ cap, never touches the original.

HTTP API (127.0.0.1:<port>, default 8771 — the services.json row cites this same number):
  GET  /health                 → {ok, service, sessions, cap, turn_timeout_s, bind}
  GET  /sessions               → every owned session's record (state machine:
                                 starting → idle ⇄ busy → closed)
  GET  /watch?session=<id>     → ndjson stream of that session's events (replay + live)
  POST /spawn                  {cwd?, resume?, fork?, name?, prompt?, source?}
  POST /inject                 {session, message, source?}
  POST /interrupt              {session}   (control_request on stdin — see _interrupt note)
  POST /teardown               {session}

Run: .venv/bin/python runtime/session_supervisor.py [port]   ·   service: company up session-supervisor
Proven by: tests/session_supervisor_acceptance.py (stub-binary service-level checks; real-claude
end-to-end verification is the build lead's, per the lane split)."""
from __future__ import annotations

import atexit
import json
import os
import signal
import subprocess
import sys
import threading
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore
from fabric import config as fcfg
from runtime import ui_claude_session as _panel   # reuse: _find_claude + _MCP_CONFIG (one source
                                                  # of the binary + the strict company-MCP config).
                                                  # This import is service→runtime, NOT the MCP face —
                                                  # the panel module's floor note covers it explicitly.

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PORT = 8771                    # next free beside the bridge's 8770 (audit N7 — the ONE number
                                       # services.json + the unit + the contract entries all cite)

# THE INVENTORY SOURCE for the supervisor-http transport (CONTRACT-FORMAT §9.3 / V21: a transport
# without a machine-readable registry fails contract validation — the BRIDGE_ROUTES law applied here,
# (method, path) structured from birth per §9.1). tests/supervisor_routes_acceptance.py is the drift
# teeth: this tuple and the do_GET/do_POST dispatch literals must match, BOTH directions.
SUPERVISOR_ROUTES = (
    ("GET", "/health"),
    ("GET", "/sessions"),
    ("GET", "/watch"),
    ("POST", "/spawn"),
    ("POST", "/inject"),
    ("POST", "/interrupt"),
    ("POST", "/teardown"),
)
MAIL_LEAF = "agent_sessions"           # naming law: agent_sessions everywhere (never fabric/, never sessions/)
CURSOR_REF = "agent_sessions/cursor:supervisor"   # per-consumer mailbox cursor (a ref, §2.3 pattern)
INIT_WAIT_S = float(os.environ.get("COMPANY_FABRIC_INIT_WAIT_S", "15"))  # spawn blocks briefly for init
MAIL_POLL_S = 0.5
WATCHDOG_POLL_S = 0.5


def fabric_concurrency() -> int:
    """The live concurrency cap — CALL-TIME env read (the implement.py permission_mode() pattern:
    a deliberately-set env flips the posture without a restart; tests monkeypatch it). Default 3
    (the COMPANY_WIRE_CONCURRENCY precedent). Registry-served default is the F-tier follow-up —
    the env var stays the override either way."""
    return int(os.environ.get("COMPANY_FABRIC_CONCURRENCY", "3"))


def fabric_permission() -> str:
    """Live permission posture for supervised sessions (call-time read; default plan = read-only)."""
    return os.environ.get("COMPANY_FABRIC_PERMISSION", "plan")


def turn_timeout_s() -> float:
    """The ENFORCED per-turn wall-clock ceiling (audit C3). Call-time read so the acceptance test
    runs the reap in seconds; default 900 = implement.py DEFAULT_TIMEOUT_S, the precedent that
    actually enforces (never the dead-constant pattern)."""
    return float(os.environ.get("COMPANY_FABRIC_TURN_TIMEOUT_S", "900"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TeachingRefusal(Exception):
    """A refusal that TEACHES (audit C9): the message names the limit, the live state, and the
    way forward. Mapped to HTTP 429/409 — never a bare error."""


class Supervised:
    """One owned claude subprocess + its supervisor-side state. The state machine is
    starting → idle ⇄ busy → closed (truthful transitions — F1.2's bar; `closed` is terminal)."""

    def __init__(self, *, name: str | None, cwd: str, resume: str | None, fork: bool, source: str):
        self.id = "as-" + uuid.uuid4().hex[:8]      # local handle until init names the claude session id
        self.claude_session_id: str | None = resume if (resume and not fork) else None
        self.name = name or self.id
        self.cwd = cwd
        self.resume = resume
        self.fork = fork
        self.source = source
        self.state = "starting"
        self.created = time.time()
        self.created_iso = _now()
        self.last_activity = time.time()
        self.turn_started: float | None = None
        self.turn_source: str | None = None
        self.turn_intent: dict | None = None        # the mailbox intent this turn answers (for the reply)
        self.turn_text: list[str] = []              # assistant text of the in-flight turn (reply body)
        self.stderr_tail: list[str] = []            # last ~50 stderr lines (drained for life; close diagnostic)
        self.turns = 0
        self.proc: subprocess.Popen | None = None
        self.stdin_lock = threading.Lock()
        self.events: deque = deque(maxlen=500)
        self.subscribers: list = []                 # queue.Queue per /watch client
        self.ev_seq = 0
        self.close_reason: str | None = None

    def record(self) -> dict:
        return {
            "id": self.id, "claude_session_id": self.claude_session_id, "name": self.name,
            "cwd": self.cwd, "state": self.state, "resume": self.resume, "fork": self.fork,
            "created": self.created_iso, "last_activity": datetime.fromtimestamp(
                self.last_activity, timezone.utc).isoformat(),
            "turns": self.turns, "pid": self.proc.pid if self.proc else None,
            "close_reason": self.close_reason,
        }

    def matches(self, key: str) -> bool:
        return key in (self.id, self.claude_session_id)


class SessionSupervisor:
    """Owns the fleet. All mutations to the fleet dict happen under self.lock; per-session
    stdin writes under the session's stdin_lock; events.jsonl writes ride FsStore's own lock
    (single process → the in-process seq lock is sufficient, by construction)."""

    def __init__(self, store: FsStore):
        self.store = store
        self.sessions: dict[str, Supervised] = {}
        self.lock = threading.RLock()
        self.mail_path = store.root / MAIL_LEAF / "mail.jsonl"
        self._stop = threading.Event()

    # ---------- events (single writer — agent_sessions.* originate ONLY here) ----------

    def emit(self, kind: str, summary: str, *, durable: bool, **meta) -> None:
        """`durable=True` = a claim whose loss changes behavior (spawned/turn/closed): the
        failure is printed LOUDLY and RE-RAISED (the _emit_durable posture — never swallow a
        claim write). Callers that must outlive a bad write (the watchdog loop — killing it
        over one write would silently unguard every other session) wrap their call sites.
        `durable=False` = narration (idle): logged-and-continue, the _emit posture."""
        try:
            self.store.append_event({"kind": kind, "summary": summary, **meta})
        except Exception as e:
            print(f"[session-supervisor] EVENT WRITE FAILED kind={kind}: {e}", file=sys.stderr, flush=True)
            if durable:
                raise

    # ---------- fan ----------

    def _fan(self, s: Supervised, ev: dict) -> None:
        s.ev_seq += 1
        ev = {"seq": s.ev_seq, "ts": _now(), "session": s.id, **ev}
        s.events.append(ev)
        for q in list(s.subscribers):
            try:
                q.put_nowait(ev)
            except Exception:
                pass

    # ---------- spawn ----------

    def _live(self) -> list[Supervised]:
        return [s for s in self.sessions.values() if s.state != "closed"]

    def _cap_check(self, adding: int) -> None:
        cap = fabric_concurrency()
        live = self._live()
        if len(live) + adding > cap:
            names = ", ".join(f"{s.name}({s.state})" for s in live) or "none"
            raise TeachingRefusal(
                f"REFUSED — this would put {len(live) + adding} sessions live, over the cap of {cap} "
                f"(COMPANY_FABRIC_CONCURRENCY, call-time env). Live now: {names}. "
                f"Free a slot first (POST /teardown {{\"session\": \"<id>\"}}) or raise the cap "
                f"deliberately by restarting the service with COMPANY_FABRIC_CONCURRENCY=<n>. "
                f"CONSULT fans count against the same cap (copies ≤ cap).")

    def spawn(self, *, cwd: str | None = None, resume: str | None = None, fork: bool = False,
              name: str | None = None, source: str = "http", wait_init: bool = True) -> Supervised:
        with self.lock:
            self._cap_check(1)
            s = Supervised(name=name, cwd=cwd or REPO_ROOT, resume=resume, fork=fork, source=source)
            self.sessions[s.id] = s
        claude_bin = _panel._find_claude()           # call-time (env-overridable — the stub harness path)
        cmd = [claude_bin, "-p",
               "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
               "--permission-mode", fabric_permission(),
               "--mcp-config", _panel._MCP_CONFIG, "--strict-mcp-config",
               "--allowedTools", "mcp__company"]
        if resume:
            cmd += ["--resume", resume]
        if fork:
            if not resume:
                raise TeachingRefusal("REFUSED — fork=true requires resume=<session id>: a CONSULT is "
                                      "a fork OF an existing session (--resume <id> --fork-session). "
                                      "For a fresh session, spawn without fork.")
            cmd += ["--fork-session"]
        s.proc = subprocess.Popen(cmd, cwd=s.cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, bufsize=1)
        threading.Thread(target=self._reader, args=(s,), daemon=True,
                         name=f"reader-{s.id}").start()
        # DRAIN stderr for the LIFE of the process. The OS pipe buffer (~64KB) MUST be emptied or a
        # chatty child blocks writing to it and dies — observed as rc=1 on RESUME spawns only: a
        # resume fires the SessionStart:resume hook AND replays the full conversation, overflowing
        # what a fresh spawn never reaches (a fresh session's thin stderr masked this in the lane's
        # stub-binary acceptance test, which never resumed a real claude). The drain IS the fix; the
        # retained tail is kept only for the close diagnostic.
        threading.Thread(target=self._drain_stderr, args=(s,), daemon=True,
                         name=f"stderr-{s.id}").start()
        self.emit("agent_sessions.spawned",
                  f"{s.name} · {'fork of ' + resume if fork else ('resume ' + resume if resume else 'new')}",
                  durable=True, session=s.id, name=s.name, cwd=s.cwd, resume=resume, fork=fork,
                  source=source, pid=s.proc.pid)
        if wait_init:
            deadline = time.time() + INIT_WAIT_S
            while time.time() < deadline and s.state == "starting" and s.proc.poll() is None:
                time.sleep(0.05)
        return s

    # ---------- the per-session stderr drain (the rc=1-on-resume fix) ----------

    def _drain_stderr(self, s: Supervised) -> None:
        """Empty the child's stderr pipe for the life of the process so it can never block on a full
        buffer. Keeps only the last 50 lines for the close diagnostic — the point is the DRAIN, not
        capture."""
        try:
            for line in s.proc.stderr:
                s.stderr_tail.append(line.rstrip("\n"))
                if len(s.stderr_tail) > 50:
                    del s.stderr_tail[0]
        except Exception:
            pass

    # ---------- the per-session stdout reader ----------

    def _reader(self, s: Supervised) -> None:
        """Parses the claude stream (the run_turn event shapes) for the LIFE of the process —
        not one turn. EOF = the process ended → closed."""
        try:
            for line in s.proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue                          # non-JSON chatter — the result event is the contract
                et = ev.get("type")
                if et == "system" and ev.get("subtype") == "init":
                    s.claude_session_id = ev.get("session_id") or s.claude_session_id
                    if s.state == "starting":
                        s.state = "idle"
                    s.last_activity = time.time()
                    self._fan(s, {"type": "init", "claude_session_id": s.claude_session_id})
                elif et == "assistant":
                    for block in (ev.get("message") or {}).get("content") or []:
                        if block.get("type") == "text" and block.get("text"):
                            s.turn_text.append(block["text"])
                            self._fan(s, {"type": "text", "text": block["text"]})
                        elif block.get("type") == "tool_use":
                            inp = block.get("input") or {}
                            detail = (inp.get("file_path") or inp.get("path") or inp.get("pattern")
                                      or inp.get("command") or inp.get("description") or "")
                            self._fan(s, {"type": "tool", "name": block.get("name", "?"),
                                          "detail": str(detail)[:160]})
                elif et == "result":
                    self._turn_done(s, ev)
        except Exception as e:
            print(f"[session-supervisor] reader {s.id} died: {e}", file=sys.stderr, flush=True)
        finally:
            rc = s.proc.poll()
            if s.state != "closed":
                try:
                    # Non-zero exits carry the drained stderr tail so the cause is never a mystery
                    # (the rc=1 hunt is exactly why this is here — fail loud WITH evidence).
                    tail = (" :: " + " | ".join(s.stderr_tail[-5:])) if (rc and s.stderr_tail) else ""
                    self._close(s, reason=f"exited rc={rc}{tail}", kill=False)
                except Exception as e:
                    print(f"[session-supervisor] close event write failed for {s.id}: {e}",
                          file=sys.stderr, flush=True)

    def _turn_done(self, s: Supervised, ev: dict) -> None:
        dur_ms = int((time.time() - s.turn_started) * 1000) if s.turn_started else None
        result_text = (ev.get("result") or "") or "\n".join(s.turn_text)
        s.turns += 1
        s.state = "idle"
        s.last_activity = time.time()
        intent = s.turn_intent
        s.turn_started, s.turn_intent = None, None
        s.turn_text = []
        self._fan(s, {"type": "done", "result": result_text[:4000],
                      "claude_session_id": ev.get("session_id") or s.claude_session_id,
                      "num_turns": ev.get("num_turns"), "is_error": bool(ev.get("is_error"))})
        # DELIVER ack/reply is a CLAIM (durable class): the turn event + the mailbox reply.
        self.emit("agent_sessions.turn", f"{s.name} · turn {s.turns} done",
                  durable=True, session=s.id, claude_session_id=s.claude_session_id,
                  name=s.name, duration_ms=dur_ms, is_error=bool(ev.get("is_error")),
                  source=s.turn_source, intent_id=(intent or {}).get("id"))
        if intent:
            self._mail_reply(s, intent, result_text, is_error=bool(ev.get("is_error")))
        self.emit("agent_sessions.idle", f"{s.name} idle", durable=False,
                  session=s.id, claude_session_id=s.claude_session_id, name=s.name)

    # ---------- inject / interrupt / teardown ----------

    def find(self, key: str) -> Supervised | None:
        with self.lock:
            for s in self.sessions.values():
                if s.matches(key):
                    return s
        return None

    def inject(self, s: Supervised, message: str, *, source: str = "http",
               intent: dict | None = None) -> None:
        if s.state == "closed":
            raise TeachingRefusal(f"REFUSED — session {s.id} ({s.name}) is closed "
                                  f"({s.close_reason}). WAKE it instead: spawn with "
                                  f"resume=\"{s.claude_session_id or s.id}\".")
        if s.state == "busy":
            raise TeachingRefusal(f"REFUSED — session {s.id} ({s.name}) is mid-turn. Wait for idle "
                                  f"(GET /sessions), POST /interrupt to stop the turn, or queue via "
                                  f"the mailbox (the supervisor retries deliver intents until idle).")
        line = json.dumps({"type": "user",
                           "message": {"role": "user",
                                       "content": [{"type": "text", "text": message}]}})
        with s.stdin_lock:
            s.state = "busy"
            s.turn_started = time.time()
            s.turn_source = source
            s.turn_intent = intent
            s.turn_text = []
            try:
                s.proc.stdin.write(line + "\n")
                s.proc.stdin.flush()
            except Exception as e:
                s.state = "closed"
                s.close_reason = f"stdin write failed: {e}"
                raise
        self._fan(s, {"type": "injected", "source": source, "chars": len(message)})

    def interrupt(self, s: Supervised) -> None:
        """Write a control_request interrupt onto the same stdin stream (the SDK transport's
        control wrapper shape — {type: control_request, request_id, request:{subtype: interrupt}}).
        HONEST STATUS: built-untested against a real claude turn (this lane runs only stub
        subprocesses); the watchdog remains the enforcement backstop either way."""
        if s.state != "busy":
            raise TeachingRefusal(f"REFUSED — session {s.id} ({s.name}) is {s.state}, not mid-turn; "
                                  f"there is nothing to interrupt.")
        line = json.dumps({"type": "control_request", "request_id": uuid.uuid4().hex,
                           "request": {"subtype": "interrupt"}})
        with s.stdin_lock:
            s.proc.stdin.write(line + "\n")
            s.proc.stdin.flush()
        self._fan(s, {"type": "interrupt_sent"})

    def _close(self, s: Supervised, *, reason: str, kill: bool) -> None:
        s.state = "closed"
        s.close_reason = reason
        if kill and s.proc and s.proc.poll() is None:
            try:
                s.proc.stdin.close()
            except Exception:
                pass
            s.proc.terminate()
            try:
                s.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                s.proc.kill()
        self._fan(s, {"type": "closed", "reason": reason})
        self.emit("agent_sessions.closed", f"{s.name} · {reason}", durable=True,
                  session=s.id, claude_session_id=s.claude_session_id, name=s.name, reason=reason)

    def teardown(self, s: Supervised) -> None:
        if s.state == "closed":
            return
        self._close(s, reason="teardown", kill=True)

    def teardown_all(self) -> None:
        with self.lock:
            live = self._live()
        for s in live:
            try:
                self.teardown(s)
            except Exception as e:
                print(f"[session-supervisor] teardown {s.id} failed: {e}", file=sys.stderr, flush=True)

    # ---------- the watchdog (the ENFORCED per-turn wall-clock — audit C3) ----------

    def watchdog_loop(self) -> None:
        while not self._stop.is_set():
            limit = turn_timeout_s()
            now = time.time()
            for s in list(self.sessions.values()):
                try:
                    if s.state == "busy" and s.turn_started and now - s.turn_started > limit:
                        self._close(s, reason=f"watchdog-timeout after {int(now - s.turn_started)}s "
                                              f"(COMPANY_FABRIC_TURN_TIMEOUT_S={int(limit)})", kill=True)
                    elif s.state == "starting" and now - s.created > limit:
                        # the silent-hang spawn: no init ever arrived — same enforcement
                        self._close(s, reason=f"watchdog-timeout: no init after {int(now - s.created)}s",
                                    kill=True)
                except Exception as e:
                    # the reap HAPPENED (kill precedes the event write in _close); a failed event
                    # write is loud, and the watchdog survives to guard the rest of the fleet.
                    print(f"[session-supervisor] watchdog event write failed for {s.id}: {e}",
                          file=sys.stderr, flush=True)
            self._stop.wait(WATCHDOG_POLL_S)

    # ---------- the mailbox consumer (guide §C contract — consume-only here) ----------

    def _cursor(self) -> int:
        v = self.store.head(CURSOR_REF)
        if v is None:
            # First boot: start at the CURRENT end of the leaf — never replay history written
            # before this supervisor existed (stated F1 choice; the importer/backfill is §B's).
            return self.mail_path.stat().st_size if self.mail_path.exists() else 0
        return int(v)

    def _reply_thread(self, intent: dict) -> str:
        """The reply's aggregation key: the intent's own thread (store-minted on every session_post),
        falling back to the intent id for hand-appended intents that bypassed append_agent_mail —
        a consult fan's N replies all join the ONE intent's thread either way."""
        t = intent.get("thread")
        return t if (isinstance(t, str) and t.strip()) else str(intent.get("id") or "")

    def _mail_reply(self, s: Supervised, intent: dict, text: str, *, is_error: bool) -> None:
        """Append the durable reply via the store's OWN mailbox API (the seam the first commit
        flagged, now closed: append_agent_mail stamps cross-process-unique `seq` + defaults `thread`,
        so replies are VISIBLE to sessions(op='inbox') reads and aggregate under the intent's thread
        — the raw no-seq append made them invisible to every seq-cursor read)."""
        cas = self.store.put_content({"text": text, "session": s.claude_session_id or s.id})
        self.store.append_agent_mail({
            "to": intent.get("from"), "from": f"session://{s.claude_session_id or s.id}",
            "verb": "error" if is_error else "reply", "re": intent.get("id"),
            "thread": self._reply_thread(intent), "cas": cas})

    def _mail_error(self, intent: dict, why: str) -> None:
        print(f"[session-supervisor] intent {intent.get('id')} refused: {why}", file=sys.stderr, flush=True)
        cas = self.store.put_content({"text": why})
        self.store.append_agent_mail({
            "to": intent.get("from"), "from": "session://supervisor",
            "verb": "error", "re": intent.get("id"),
            "thread": self._reply_thread(intent), "cas": cas})

    def _intent_body(self, rec: dict) -> str:
        if rec.get("cas"):
            body = self.store.get_content(rec["cas"])
            if isinstance(body, dict):
                return str(body.get("text") or body)
            return str(body)
        if rec.get("message"):
            return str(rec["message"])
        raise ValueError("intent carries neither cas nor message")

    def mailbox_loop(self) -> None:
        offset = self._cursor()
        while not self._stop.is_set():
            try:
                offset = self._mail_pass(offset)
            except Exception as e:
                print(f"[session-supervisor] mailbox pass failed: {e}", file=sys.stderr, flush=True)
            self._stop.wait(MAIL_POLL_S)

    def _mail_pass(self, offset: int) -> int:
        if not self.mail_path.exists():
            return offset
        with self.mail_path.open("r", encoding="utf-8") as f:
            f.seek(offset)
            while True:
                pos = f.tell()
                line = f.readline()
                if not line:
                    break
                if not line.endswith("\n"):
                    break                              # torn tail of a concurrent append — retry next poll
                rec_offset_after = f.tell()
                line = line.strip()
                if not line:
                    offset = rec_offset_after
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    print(f"[session-supervisor] unparseable mail line at {pos} — skipped LOUDLY",
                          file=sys.stderr, flush=True)
                    offset = rec_offset_after
                    continue
                if rec.get("verb") not in ("deliver", "wake", "consult"):
                    offset = rec_offset_after          # replies/acks/foreign verbs — not ours to act on
                    continue
                handled = self._handle_intent(rec)
                if not handled:
                    break                              # head-of-line hold (target busy) — cursor stays put
                offset = rec_offset_after
                self.store.set_ref(CURSOR_REF, str(offset))
        return offset

    def _handle_intent(self, rec: dict) -> bool:
        """True = consumed (acted or terminally refused-loud); False = hold the cursor and retry
        (the one non-terminal case: deliver to a session that is mid-turn)."""
        target = (rec.get("to") or "").removeprefix("session://")
        verb = rec.get("verb")
        frm = rec.get("from")
        if not (isinstance(frm, str) and frm.strip()):
            # No reply path: neither the answer nor a refusal is mailable (append_agent_mail
            # refuses a from-less record by the store's own law). Consume it LOUDLY — holding
            # the cursor here would deadlock the whole mailbox behind one unroutable line.
            print(f"[session-supervisor] intent {rec.get('id')} has no `from` — unroutable, "
                  f"consumed without action (the reply path is mandatory)", file=sys.stderr, flush=True)
            return True
        try:
            body = self._intent_body(rec)
        except Exception as e:
            self._mail_error(rec, f"unreadable intent body: {e}")
            return True
        try:
            if verb == "deliver":
                s = self.find(target)
                if s is None or s.state == "closed":
                    self._mail_error(rec, f"deliver target session://{target} is not live under this "
                                          f"supervisor — route as wake (it will be resumed) or consult.")
                    return True
                if s.state == "busy":
                    return False                       # retried next poll — durable, in order
                self.inject(s, body, source=rec.get("from") or "mailbox", intent=rec)
                return True
            if verb == "wake":
                live = self.find(target)
                if live and live.state == "busy":
                    return False                       # already live + mid-turn → hold, deliver next poll
                if live and live.state in ("idle", "starting"):
                    # already supervised-live → a wake degrades to deliver (truthful routing)
                    self.inject(live, body, source=rec.get("from") or "mailbox", intent=rec)
                    return True
                s = self.spawn(resume=target, source=f"mailbox:{rec.get('from')}",
                               name=rec.get("name") or f"wake-{target[:8]}")
                self.inject(s, body, source=rec.get("from") or "mailbox", intent=rec)
                return True
            if verb == "consult":
                copies = int(rec.get("copies") or 1)
                cap = fabric_concurrency()
                if copies > cap:
                    self._mail_error(rec, f"consult copies={copies} exceeds the concurrency cap {cap} "
                                          f"(COMPANY_FABRIC_CONCURRENCY) — fan ≤ cap, or raise the cap "
                                          f"deliberately on the service.")
                    return True
                with self.lock:
                    self._cap_check(copies)
                for i in range(copies):
                    s = self.spawn(resume=target, fork=True, source=f"mailbox:{rec.get('from')}",
                                   name=(rec.get("name") or f"consult-{target[:8]}") + f"-{i + 1}")
                    self.inject(s, body, source=rec.get("from") or "mailbox", intent=rec)
                return True
        except TeachingRefusal as e:
            self._mail_error(rec, str(e))
            return True
        except Exception as e:
            self._mail_error(rec, f"{verb} failed: {e}")
            return True
        return True


# ───────────────────────────── HTTP face ─────────────────────────────

SUP: SessionSupervisor | None = None


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):                 # journald gets our own lines; not every GET
        pass

    def _send(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/health":
            with SUP.lock:
                by_state: dict = {}
                for s in SUP.sessions.values():
                    by_state[s.state] = by_state.get(s.state, 0) + 1
            self._send(200, {"ok": True, "service": "session-supervisor", "bind": "127.0.0.1",
                             "sessions": {"total": len(SUP.sessions), "by_state": by_state},
                             "cap": fabric_concurrency(), "turn_timeout_s": turn_timeout_s(),
                             "permission": fabric_permission()})
            return
        if u.path == "/sessions":
            with SUP.lock:
                recs = [s.record() for s in SUP.sessions.values()]
            self._send(200, {"sessions": recs})
            return
        if u.path == "/watch":
            self._watch(parse_qs(u.query))
            return
        self._send(404, {"error": f"unknown path {u.path} — GET /health · /sessions · "
                                  f"/watch?session=<id>; POST /spawn · /inject · /interrupt · /teardown"})

    def _watch(self, q: dict) -> None:
        key = (q.get("session") or [""])[0]
        s = SUP.find(key)
        if s is None:
            self._send(404, {"error": f"unknown session {key!r} — GET /sessions for the live set"})
            return
        import queue as _q
        sub: _q.Queue = _q.Queue()
        replay = list(s.events)
        s.subscribers.append(sub)
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            for ev in replay:
                self.wfile.write((json.dumps(ev) + "\n").encode())
            self.wfile.flush()
            while True:
                try:
                    ev = sub.get(timeout=15)
                except _q.Empty:
                    if s.state == "closed":
                        break
                    self.wfile.write(b'{"type":"keepalive"}\n')
                    self.wfile.flush()
                    continue
                self.wfile.write((json.dumps(ev) + "\n").encode())
                self.wfile.flush()
                if ev.get("type") == "closed":
                    break
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            try:
                s.subscribers.remove(sub)
            except ValueError:
                pass

    def do_POST(self):
        self.close_connection = True                   # the bridge's POST socket-reuse lesson
        u = urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length) or b"{}") if length else {}
        except ValueError:
            self._send(400, {"error": "body must be JSON"})
            return
        try:
            if u.path == "/spawn":
                s = SUP.spawn(cwd=body.get("cwd"), resume=body.get("resume"),
                              fork=bool(body.get("fork")), name=body.get("name"),
                              source=body.get("source") or "http")
                if body.get("prompt"):
                    SUP.inject(s, str(body["prompt"]), source=body.get("source") or "http")
                self._send(200, {"ok": True, "session": s.record()})
                return
            if u.path in ("/inject", "/interrupt", "/teardown"):
                s = SUP.find(str(body.get("session") or ""))
                if s is None:
                    self._send(404, {"error": f"unknown session {body.get('session')!r} — "
                                              f"GET /sessions for the live set"})
                    return
                if u.path == "/inject":
                    if not body.get("message"):
                        self._send(400, {"error": "inject needs {session, message}"})
                        return
                    SUP.inject(s, str(body["message"]), source=body.get("source") or "http")
                    self._send(200, {"ok": True, "session": s.record()})
                elif u.path == "/interrupt":
                    SUP.interrupt(s)
                    self._send(200, {"ok": True, "session": s.record()})
                else:
                    SUP.teardown(s)
                    self._send(200, {"ok": True, "session": s.record()})
                return
        except TeachingRefusal as e:
            self._send(429 if "cap" in str(e) else 409, {"error": str(e)})
            return
        except Exception as e:
            self._send(500, {"error": f"INTERNAL: {e}"})
            return
        self._send(404, {"error": f"unknown path {u.path}"})


def main() -> None:
    global SUP
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    store = FsStore(fcfg.STORE_DIR)
    SUP = SessionSupervisor(store)
    threading.Thread(target=SUP.watchdog_loop, daemon=True, name="watchdog").start()
    threading.Thread(target=SUP.mailbox_loop, daemon=True, name="mailbox").start()

    def _bye(*_a):
        SUP._stop.set()
        SUP.teardown_all()                             # no orphans — the lane's hard guarantee
        os._exit(0)

    signal.signal(signal.SIGTERM, _bye)
    signal.signal(signal.SIGINT, _bye)
    atexit.register(SUP.teardown_all)
    print(f"[session-supervisor] owning sessions at http://127.0.0.1:{port} "
          f"(cap={fabric_concurrency()} · turn_timeout={int(turn_timeout_s())}s · "
          f"permission={fabric_permission()} · store={fcfg.STORE_DIR})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()


if __name__ == "__main__":
    main()
