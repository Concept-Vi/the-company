"""runtime/cc_clone.py — point-in-time CLONE -> fabric (the clone->channel extension, SAFE path).

Materialize a source session AT A PAST POINT (runtime/session_pointintime), launch the clone as a
LIVE SUPERVISED session (the supervisor's proven spawn-resume, headless -p), register it in the
fabric clones registry so it is discoverable, and DM it via the supervisor's /inject (capturing the
clone's reply from THAT past-point context).

WHY supervised+inject and NOT an interactive channel member:
  Channels fire only in INTERACTIVE sessions. An AGENT programmatically launching a no-human
  interactive `claude --dangerously-load-development-channels` is (correctly) BLOCKED by the safety
  classifier as an unsafe autonomous agent that auto-ingests untrusted channel pushes. So the
  AUTONOMOUS clone is supervised+inject (operator-controlled supervisor, agent-initiated turns);
  the INTERACTIVE-channel-member clone is OPERATOR-launched — operator_launch_cmd() emits the exact
  ready-to-run command for Tim.

Proven parts only: materialize_at_point (source byte-untouched), supervisor /spawn resume (R3.4),
/inject + /watch (R1/wake). NEW FILE — no edits to cc_channels.py or session_supervisor.py.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import uuid as _uuid

from runtime.session_pointintime import materialize_at_point, resume_cwd_for, build_timeline

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLONES_DIR = os.path.join(REPO, ".data", "clones")
SUPERVISOR = os.environ.get("COMPANY_SUPERVISOR_BASE", "http://127.0.0.1:8771")
CHANNEL_MCP_CONFIG = os.path.join(REPO, "channels", "channel.mcp.json")


class CloneError(RuntimeError):
    """A clone op could not run — raised TEACHING-loud (never a silent no-op)."""


def _sup(path: str, body=None, method: str = "POST", timeout: float = 30):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(SUPERVISOR + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")
    except (urllib.error.URLError, OSError) as e:
        raise CloneError(f"supervisor at {SUPERVISOR} unreachable ({e}). Start it: company up "
                         f"session-supervisor")


def _alive_supervised(supervisor_session: str) -> bool:
    try:
        _, r = _sup("/sessions", method="GET")
    except CloneError:
        return False
    rec = next((s for s in r.get("sessions", []) if s["id"] == supervisor_session), None)
    return bool(rec and rec.get("state") != "closed")


def _wait_idle(supervisor_session: str, timeout: float = 120) -> dict:
    t0 = time.time()
    while time.time() - t0 < timeout:
        _, r = _sup("/sessions", method="GET")
        rec = next((s for s in r.get("sessions", []) if s["id"] == supervisor_session), None)
        if rec and rec["state"] == "idle":
            return rec
        if rec and rec["state"] == "closed":
            raise CloneError(f"clone {supervisor_session} closed during launch: {rec.get('close_reason')}")
        time.sleep(0.5)
    raise CloneError(f"clone {supervisor_session} not idle within {timeout}s")


def operator_launch_cmd(new_sid: str, cwd: str, handle: str, description: str) -> str:
    """The EXACT command Tim runs to launch this clone as a full INTERACTIVE channel member
    (operator-gated — an agent cannot auto-launch it). Resumes the materialized point-in-time
    prefix WITH the channel so it auto-registers and joins group chats / is DM-able by channel."""
    env = (f"COMPANY_CHANNEL_HANDLE={handle} COMPANY_SESSION_ID={new_sid} "
           f"COMPANY_ROOT={REPO} COMPANY_CHANNEL_DESC={json.dumps(description)}")
    return (f"cd {cwd} && {env} claude --resume {new_sid} "
            f"--mcp-config {CHANNEL_MCP_CONFIG} "
            f"--dangerously-load-development-channels server:company-channel")


def clone_at(source_jsonl: str, at: str, *, description: str = "", cwd: str | None = None) -> dict:
    """Materialize `source_jsonl` AT `at` (e.g. 'compact:1' / 'uuid:..' / 'ts:..') and launch the
    clone as a live SUPERVISED session. Registers it in the clones registry. Returns the clone's
    handle + supervisor_session + session_id + the operator command for interactive membership."""
    if not os.path.exists(source_jsonl):
        raise CloneError(f"source transcript not found: {source_jsonl}")
    tl = build_timeline(source_jsonl)
    nb = len(tl.get("boundaries") or [])
    new_sid = str(_uuid.uuid4())
    resume_cwd = resume_cwd_for(source_jsonl, cwd or os.path.basename(os.path.dirname(source_jsonl)).replace("-", "/"))
    rep = materialize_at_point(source_jsonl, at, dest_dir=os.path.dirname(source_jsonl), new_sid=new_sid)
    if not rep.get("source_untouched"):
        raise CloneError(f"source changed during materialization of {source_jsonl} — aborting (non-destructive law).")
    name = f"clone-{at.replace(':', '')}-{new_sid[:8]}"
    code, r = _sup("/spawn", {"cwd": resume_cwd, "resume": new_sid, "name": name})
    if code != 200:
        raise CloneError(f"supervisor /spawn (resume={new_sid[:8]}) failed: {r}")
    sup_sess = r["session"]["id"]
    _wait_idle(sup_sess)
    handle = "clone-" + new_sid[:8]
    rec = {"kind": "supervised-clone", "handle": handle, "supervisor_session": sup_sess,
           "session_id": new_sid, "source_sid": rep["source_sid"], "source_path": source_jsonl,
           "at": at, "cwd": resume_cwd, "description": description,
           "materialized_path": rep["new_path"], "boundaries": nb,
           "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    os.makedirs(CLONES_DIR, exist_ok=True)
    with open(os.path.join(CLONES_DIR, handle + ".json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
    return {**rec, "source_untouched": True,
            "operator_launch_cmd": operator_launch_cmd(new_sid, resume_cwd, handle, description
                                                        or f"clone of {rep['source_sid'][:8]} @{at}")}


def _find_clone(handle_or_session: str) -> dict:
    if not os.path.isdir(CLONES_DIR):
        raise CloneError("no clones registered — clone_at() first.")
    for fn in os.listdir(CLONES_DIR):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(CLONES_DIR, fn), encoding="utf-8") as f:
                rec = json.load(f)
        except (OSError, ValueError):
            continue
        if handle_or_session in (rec.get("handle"), rec.get("supervisor_session"), rec.get("session_id")):
            return rec
    raise CloneError(f"no clone matches {handle_or_session!r}. list_clones() shows them.")


def msg_clone(handle_or_session: str, message: str, *, timeout: float = 180) -> dict:
    """DM a supervised clone: inject `message` and return its reply (from the clone's past-point
    context). Uses the supervisor /inject + /watch (proven). Fail-loud if the clone is gone."""
    rec = _find_clone(handle_or_session)
    sup = rec["supervisor_session"]
    if not _alive_supervised(sup):
        raise CloneError(f"clone {rec['handle']} ({sup}) is no longer live — re-clone with clone_at().")
    # open the watch stream BEFORE injecting so the turn's events are not missed
    wreq = urllib.request.Request(f"{SUPERVISOR}/watch?session={sup}")
    try:
        wresp = urllib.request.urlopen(wreq, timeout=timeout + 10)
    except (urllib.error.URLError, OSError) as e:
        raise CloneError(f"watch open failed for {sup}: {e}")
    code, _ = _sup("/inject", {"session": sup, "message": message})
    if code != 200:
        try: wresp.close()
        except Exception: pass
        raise CloneError(f"/inject to clone {rec['handle']} failed (HTTP {code}).")
    reply, t0 = "", time.time()
    try:
        for raw in wresp:
            if time.time() - t0 > timeout:
                break
            try:
                ev = json.loads(raw)
            except ValueError:
                continue
            if ev.get("type") == "done":
                reply = ev.get("result", "") or ""
                break
    finally:
        try: wresp.close()
        except Exception: pass
    if not reply:
        raise CloneError(f"clone {rec['handle']} produced no reply within {timeout}s (turn may still be running).")
    return {"handle": rec["handle"], "session_id": rec["session_id"], "at": rec["at"],
            "source_sid": rec["source_sid"], "reply": reply}


def list_clones(*, prune: bool = True) -> list:
    """Every registered supervised clone; prunes ones whose supervisor session has closed."""
    out = []
    if not os.path.isdir(CLONES_DIR):
        return out
    for fn in sorted(os.listdir(CLONES_DIR)):
        if not fn.endswith(".json"):
            continue
        p = os.path.join(CLONES_DIR, fn)
        try:
            with open(p, encoding="utf-8") as f:
                rec = json.load(f)
        except (OSError, ValueError):
            continue
        if prune and not _alive_supervised(rec.get("supervisor_session", "")):
            try: os.unlink(p)
            except OSError: pass
            continue
        out.append(rec)
    return out


def end_clone(handle_or_session: str, *, delete_materialized: bool = True) -> dict:
    """Teardown a clone's supervised session, drop its registry entry, and (default) delete the
    materialized prefix file so ~/.claude/projects is not polluted. Non-destructive to the source."""
    rec = _find_clone(handle_or_session)
    _sup("/teardown", {"session": rec["supervisor_session"]})
    removed_mat = False
    if delete_materialized:
        mp = rec.get("materialized_path")
        if mp and os.path.exists(mp):
            try: os.unlink(mp); removed_mat = True
            except OSError: pass
    regp = os.path.join(CLONES_DIR, rec["handle"] + ".json")
    try: os.unlink(regp)
    except OSError: pass
    return {"ended": rec["handle"], "supervisor_session": rec["supervisor_session"],
            "materialized_deleted": removed_mat}


def prepare_at(source_jsonl: str, at: str, *, description: str = "", cwd: str | None = None) -> dict:
    """OPERATOR-INTERACTIVE path: materialize `source_jsonl` @ `at` into a FRESH prefix and return the
    exact command for Tim to launch it as an INTERACTIVE channel member (auto-launch by an agent is
    correctly blocked by the safety classifier). Does NOT spawn anything — just prepares + emits the
    command. Distinct new_sid from any supervised clone so the two never collide on one resume id."""
    if not os.path.exists(source_jsonl):
        raise CloneError(f"source transcript not found: {source_jsonl}")
    new_sid = str(_uuid.uuid4())
    resume_cwd = resume_cwd_for(source_jsonl, cwd or os.path.basename(os.path.dirname(source_jsonl)).replace("-", "/"))
    rep = materialize_at_point(source_jsonl, at, dest_dir=os.path.dirname(source_jsonl), new_sid=new_sid)
    if not rep.get("source_untouched"):
        raise CloneError(f"source changed during materialization of {source_jsonl} — aborting.")
    handle = "clone-" + new_sid[:8]
    desc = description or f"interactive clone of {rep['source_sid'][:8]} @{at}"
    return {"prepared": True, "handle": handle, "session_id": new_sid, "at": at,
            "source_sid": rep["source_sid"], "cwd": resume_cwd, "source_untouched": True,
            "materialized_path": rep["new_path"],
            "operator_launch_cmd": operator_launch_cmd(new_sid, resume_cwd, handle, desc),
            "note": "Run operator_launch_cmd in a terminal to launch this clone as an INTERACTIVE "
                    "channel member (joins group chats, DM-able by channel). An agent cannot "
                    "auto-launch it (safety boundary). Delete materialized_path if you don't launch it."}
