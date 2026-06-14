"""runtime/context_ops.py — live context-window READ + COMPACT over the session-supervisor (S-R10.1).

The in-process TUI context controls (/context, /compact) are NOT exposed as fabric ops — but BOTH
are reachable headless by INJECTING the slash command into a supervised-live session and capturing
what it emits (the supervisor's reader declares every emit). Lead-VERIFIED 2026-06-14:
  - `/context`  → a `system/local_command_output` declared event carrying the usage breakdown
                  (proven in ops/fabric_live_probe_r1.py leg 2).
  - `/compact`  → a `system/compact_boundary` declared event; the session re-inits with the summary
                  and memory survives (post-compact recall confirmed).
The always-live continuous gauge (usage between turns, no inject) stays in-process; fork-on-compaction
(R3.4) covers the preserve-before-compact need. These are the on-demand snapshot + compact ops.

Operates on an EXISTING supervised-live session (a session id). FAIL LOUD if the supervisor is
unreachable. Thin orchestration over proven capabilities — no new transport code.
"""
from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request

DEFAULT_SUPERVISOR = os.environ.get("COMPANY_SUPERVISOR_BASE", "http://127.0.0.1:8771")


class ContextOpError(RuntimeError):
    """A context op could not run — raised TEACHING-loud (never a silent no-op)."""


def _req(base, method, path, body=None, timeout=30):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(base + path, data=data, method=method,
                               headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def _inject_and_capture(base, session, message, want_keys, timeout):
    """Inject `message` into a live session and capture (declared events whose render_key is in
    want_keys) + the turn's `done`. BULLETPROOF against the /watch backlog replay (which trips a
    naive reader on a prior turn's stale done): every event is stored with its ARRIVAL TIME, and we
    scan ONLY events that arrived AFTER our /inject call returned. Quiet-drain first so the inject
    itself is not lost in a flood, then arrival-time filtering isolates exactly our turn."""
    events, lock, stop = [], threading.Lock(), threading.Event()

    def run():
        try:
            req = urllib.request.Request(f"{base}/watch?session={session}")
            with urllib.request.urlopen(req, timeout=timeout + 10) as resp:
                for raw in resp:
                    if stop.is_set():
                        return
                    try:
                        ev = json.loads(raw)
                    except ValueError:
                        continue
                    with lock:
                        events.append((time.time(), ev))     # (arrival_time, event)
        except Exception:
            return

    t = threading.Thread(target=run, daemon=True)
    t.start()
    # quiet-drain the backlog so our inject is not lost mid-flood (mark by time, not index)
    quiet, t0, last_len, last_change = 0.6, time.time(), -1, time.time()
    while time.time() - last_change < quiet and time.time() - t0 < 10:
        with lock:
            cur = len(events)
        if cur != last_len:
            last_len, last_change = cur, time.time()
        time.sleep(0.1)
    code, r = _req(base, "POST", "/inject", {"session": session, "message": message})
    inject_t = time.time()                               # arrival cutoff: only events AFTER this
    if code != 200:
        stop.set()
        raise ContextOpError(f"inject refused ({code}) for session {session}: {r}")
    t1, matched, done = time.time(), [], None
    while time.time() - t1 < timeout:
        with lock:
            fresh = [e for (ta, e) in events if ta >= inject_t]   # ONLY our turn's events
        matched = [e for e in fresh if e.get("type") == "declared" and e.get("render_key") in want_keys]
        done = next((e for e in fresh if e.get("type") == "done"), None)
        if done:
            break
        time.sleep(0.25)
    stop.set()
    return matched, done


def _ensure_supervisor(base):
    try:
        _req(base, "GET", "/health", timeout=5)
    except Exception as e:
        raise ContextOpError(
            f"session-supervisor unreachable at {base} ({e}). Start it: `company up session-supervisor`.")


def read_context(session, *, base=DEFAULT_SUPERVISOR, timeout=120.0) -> dict:
    """Inject `/context` and capture the usage breakdown (a `system/local_command_output` emit).
    Returns {session, raw, observed}. `raw` is the verbatim local-command output (the usage table)."""
    _ensure_supervisor(base)
    matched, done = _inject_and_capture(
        base, session, "/context",
        {"system/local_command_output", "system/local_command"}, timeout)
    raw = ""
    if matched:
        f = matched[-1].get("fields") or {}
        raw = f.get("stdout") or f.get("output") or f.get("content") or json.dumps(f)[:2000]
    elif done and done.get("result"):
        raw = done["result"]
    return {"session": session, "op": "read", "observed": bool(matched or (done and done.get("result"))),
            "raw": raw[:4000]}


def compact_session(session, *, base=DEFAULT_SUPERVISOR, focus="", timeout=240.0) -> dict:
    """Inject `/compact` (optionally `/compact <focus>`) and wait for the `system/compact_boundary`
    completion marker. Returns {session, compacted, boundary_seen}. Memory survives (the session
    re-inits with the summary) — lead-verified 2026-06-14."""
    _ensure_supervisor(base)
    msg = f"/compact {focus}".strip()
    matched, done = _inject_and_capture(base, session, msg, {"system/compact_boundary"}, timeout)
    boundary = bool(matched)
    return {"session": session, "op": "compact", "boundary_seen": boundary,
            "compacted": boundary, "turn_done": done is not None}


if __name__ == "__main__":
    import sys
    op, sess = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("read", "")
    fn = {"read": read_context, "compact": compact_session}[op]
    print(json.dumps(fn(sess), indent=2))
