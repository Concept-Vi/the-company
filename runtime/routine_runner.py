"""runtime/routine_runner.py — FIRE a routine through the session-supervisor (Session Fabric S-R9.1).

THE FIRE MECHANISM. `fire(routine_id)` drives the proven supervisor circuit:
  POST /spawn {cwd, prompt, model, permission_mode, name:"routine:<id>", source:"routine"}
       → the supervisor spawns a real `claude -p` and auto-injects the routine's prompt
         (session_supervisor.py /spawn route: `if body.get("prompt"): SUP.inject(...)`)
  watch /watch?session=<id> → capture the turn's `done` event (result + claude_session_id)
  POST /teardown {session}  → close the one-off (unless the routine repeats / keep=True)
and returns a durable RUN RECORD {routine_id, claude_session_id, result, is_error, ts, session,...}.

This is the LOCAL-DRIVEN routine: the supervisor already captures per-turn cost/usage in _turn_done,
so a routine run is a thin orchestration over capabilities that are PROVEN live (R1.1). No new
spawn/transport code — registry + this runner + a trigger arm (systemd .timer / the `routines` MCP
tool op=fire). FAIL LOUD if the supervisor is unreachable (no silent no-op).

Lead-only at fire time (it spawns a real claude session). The schedule arm (systemd) and the
op=fire tool both call fire(); a unit test exercises the /spawn BODY construction against a stub.
"""
from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request

from runtime.routines import routine_registry, Routine

DEFAULT_SUPERVISOR = os.environ.get("COMPANY_SUPERVISOR_BASE", "http://127.0.0.1:8771")


class RoutineFireError(RuntimeError):
    """A routine could not be fired — raised TEACHING-loud (never a silent no-op)."""


def build_spawn_body(routine: Routine, *, source: str = "routine") -> dict:
    """The /spawn request body for a routine fire (pure — unit-testable WITHOUT a real spawn).
    Omits None fields so the supervisor reproduces its defaults; the prompt rides in the body so
    the /spawn route auto-injects it as the first turn."""
    body: dict = {
        "cwd": routine.cwd,
        "prompt": routine.prompt,
        "permission_mode": routine.permission_mode,
        "name": f"routine:{routine.id}",
        "source": source,
    }
    if routine.model:
        body["model"] = routine.model
    return body


def _req(base: str, method: str, path: str, body: "dict | None" = None, timeout: float = 30):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(base + path, data=data, method=method,
                               headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def _capture_done(base: str, session: str, timeout: float):
    """Open the session's /watch stream and return its first `done` event (the turn result),
    or None on timeout. A thin reader (the supervisor _turn_done fans {type:done, result, ...})."""
    out = {"done": None}
    stop = threading.Event()

    def run():
        try:
            req = urllib.request.Request(f"{base}/watch?session={session}")
            with urllib.request.urlopen(req, timeout=timeout + 5) as resp:
                for raw in resp:
                    if stop.is_set():
                        return
                    try:
                        ev = json.loads(raw)
                    except ValueError:
                        continue
                    if ev.get("type") == "done":
                        out["done"] = ev
                        return
        except Exception:
            return

    t = threading.Thread(target=run, daemon=True)
    t.start()
    t.join(timeout)
    stop.set()
    return out["done"]


def fire(routine_or_id, *, base: str = DEFAULT_SUPERVISOR, keep: bool = False,
         turn_timeout: float = 300.0, source: str = "routine") -> dict:
    """Fire a routine: spawn → inject (via the /spawn prompt body) → capture the result → teardown.
    Returns the run record. Raises RoutineFireError (teaching) if the supervisor is unreachable or
    the spawn is refused. `keep=True` leaves the session alive (e.g. a repeats/goal-loop routine)."""
    routine = routine_or_id if isinstance(routine_or_id, Routine) else routine_registry()[routine_or_id]

    # supervisor reachable? fail loud, never a silent no-op (no-silent-failures law)
    try:
        _req(base, "GET", "/health", timeout=5)
    except Exception as e:
        raise RoutineFireError(
            f"routine {routine.id!r}: session-supervisor unreachable at {base} ({e}). "
            f"Start it first: `company up session-supervisor`. A routine cannot fire without it.")

    code, r = _req(base, "POST", "/spawn", build_spawn_body(routine, source=source))
    if code != 200:
        raise RoutineFireError(f"routine {routine.id!r}: spawn refused ({code}): {r}")
    session = r["session"]["id"]

    done = _capture_done(base, session, turn_timeout)
    result_text = (done or {}).get("result", "")
    claude_sid = (done or {}).get("claude_session_id")
    is_error = bool((done or {}).get("is_error")) or done is None

    if not keep:
        _req(base, "POST", "/teardown", {"session": session})

    return {
        "routine_id": routine.id,
        "session": session,
        "claude_session_id": claude_sid,
        "result": result_text,
        "is_error": is_error,
        "observed_done": done is not None,
        "source": source,
    }


if __name__ == "__main__":
    import sys
    rid = sys.argv[1] if len(sys.argv) > 1 else "self_status"
    rec = fire(rid, keep="--keep" in sys.argv)
    print(json.dumps(rec, indent=2))
