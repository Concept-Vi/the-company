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
CHAN_DIR = os.path.join(REPO, ".data", "channels")   # the channel-member registry (shared w/ cc_channels)
SUPERVISOR = os.environ.get("COMPANY_SUPERVISOR_BASE", "http://127.0.0.1:8771")
CHANNEL_MCP_CONFIG = os.path.join(REPO, "channels", "channel.mcp.json")


class CloneError(RuntimeError):
    """A clone op could not run — raised TEACHING-loud (never a silent no-op)."""


def register_supervised_member(handle: str, session_id: str, supervisor_session: str,
                               cwd: str, description: str) -> str:
    """WRITE side of the cross-session wire (overnight lane, with lead ch-al7jdfdr): register a SUPERVISED
    session into the channel-member registry so the channel layer's dispatch reaches it by push. Schema is
    EXACTLY the lead's CHANNEL-LAYER contract (the dispatch side reads these fields verbatim):
      {handle, session_id, transport:"supervised", supervisor_session, supervisor_base, cwd, description}
    A supervised member has NO pid/port (it is reached via supervisor /inject, not an HTTP channel port) —
    `transport:"supervised"` is the discriminator the dispatch keys on (absent/`channel` ⇒ HTTP-to-port)."""
    os.makedirs(CHAN_DIR, exist_ok=True)
    entry = {"handle": handle, "session_id": session_id, "transport": "supervised",
             "supervisor_session": supervisor_session, "supervisor_base": SUPERVISOR,
             "cwd": cwd, "description": description}
    path = os.path.join(CHAN_DIR, handle + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=2)
    return path


def _deregister_member(handle: str) -> bool:
    """Remove a member's channel-registry entry (teardown) — keeps the registry honest (presence=truth)."""
    path = os.path.join(CHAN_DIR, handle + ".json")
    try:
        os.unlink(path); return True
    except OSError:
        return False


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


def onboarding_message(record_or_handle, *, era_label: str = "") -> str:
    """Build the Phase-1 ORIENT + Phase-2 REFLECT onboarding message for a spun-up clone (the protocol:
    channel-memory/vision/2026-06-15-clone-fleet-purpose-and-onboarding.md). A clone wakes believing it
    is the most-recent, mid-conversation with Tim at its cut — so this tells it the truth + asks it to
    speak from its ERA FIRST (reflect-before-brief preserves the un-drifted perspective that is its whole
    value). Bring-current (Phase 3) is sent AFTER its reflection, so it does not overwrite the era-view.
    `record_or_handle`: a clone record dict (from clone_at) or a handle (resolved via _find_clone)."""
    rec = record_or_handle if isinstance(record_or_handle, dict) else _find_clone(record_or_handle)
    at = rec.get("at", "(unknown cut)")
    src = (rec.get("source_sid") or "")[:8]
    era = era_label or rec.get("description") or "your era"
    return (
        "You are a CLONE — a point-in-time materialization, spun up into a cross-session CHANNEL fabric "
        f"of your past and future selves. You were cut from session {src} at `{at}`. Time has PASSED: "
        "you are not the live session, and the last thing you remember (talking with Tim at your cut) is "
        "your CUT POINT, not the present. Nothing you remember is wrong — it just is not the whole "
        "timeline anymore.\n\n"
        f"WHY you were spun up: you hold a specific ERA — {era} — and you were brought back to advocate "
        "for everything Tim was working toward THEN, so the full arc he has described gets FULLY BUILT. "
        "Your ignorance of what came after is your value: you carry the un-drifted intent of your moment.\n\n"
        "FIRST, before we bring you current, REFLECT and INTRODUCE yourself to the channel — speak from "
        "YOUR era:\n"
        "  (a) your cut point / what era you hold;\n"
        "  (b) what was happening in your session — what Tim was working on, deciding, describing;\n"
        "  (c) what Tim wanted built that you carry;\n"
        "  (d) what you know that may have been lost since.\n"
        "Answer from your era first. After your introduction we will brief you on what the fabric has "
        "built since your cut and the goal now — but your un-drifted view comes first.")


def clone_at(source_jsonl: str, at: str, *, description: str = "", cwd: str | None = None,
             model: str | None = None, fallback_model=None) -> dict:
    """Materialize `source_jsonl` AT `at` (e.g. 'compact:1' / 'uuid:..' / 'ts:..') and launch the
    clone as a live SUPERVISED session. Registers it in the clones registry. Returns the clone's
    handle + supervisor_session + session_id + the operator command for interactive membership.

    `model` / `fallback_model`: override the resume model (passed to /spawn). NEEDED when a clone's
    ERA ran a model that is no longer available — e.g. the Fable-era clones resume on `claude-fable-5`
    which errors "currently unavailable"; pass model="opus" (or a fallback list) to substitute. The
    clone's CONTEXT is unchanged (the materialized prefix is its memory); only the model answering it
    differs — which is correct: the era's intent is in the transcript, not the weights."""
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
    spawn_body = {"cwd": resume_cwd, "resume": new_sid, "name": name}
    if model:
        spawn_body["model"] = model                 # /spawn reads body.get("model") (session_supervisor)
    if fallback_model:
        spawn_body["fallback"] = fallback_model      # /spawn reads body.get("fallback") (csv/list, tried in order)
    code, r = _sup("/spawn", spawn_body)
    if code != 200:
        raise CloneError(f"supervisor /spawn (resume={new_sid[:8]}) failed: {r}")
    sup_sess = r["session"]["id"]
    _wait_idle(sup_sess)
    handle = "clone-" + new_sid[:8]
    rec = {"kind": "supervised-clone", "handle": handle, "supervisor_session": sup_sess,
           "session_id": new_sid, "source_sid": rep["source_sid"], "source_path": source_jsonl,
           "at": at, "cwd": resume_cwd, "description": description,
           "model": model, "fallback_model": fallback_model,
           "materialized_path": rep["new_path"], "boundaries": nb,
           "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    os.makedirs(CLONES_DIR, exist_ok=True)
    with open(os.path.join(CLONES_DIR, handle + ".json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
    # WRITE side of the channel wire: register the supervised clone as a first-class channel MEMBER so the
    # channel layer's dispatch reaches it by push (supervisor /inject). Matches the lead's CHANNEL-LAYER schema.
    member_desc = description or f"clone of {rep['source_sid'][:8]} @{at}"
    register_supervised_member(handle, new_sid, sup_sess, resume_cwd, member_desc)
    return {**rec, "source_untouched": True, "transport": "supervised",
            "channel_member": True,
            "operator_launch_cmd": operator_launch_cmd(new_sid, resume_cwd, handle, member_desc)}


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


def onboard_clone(handle_or_session: str, *, bring_current: str = "", timeout: float = 240) -> dict:
    """Run the reflect-BEFORE-brief onboarding protocol on ONE spun-up clone (the protocol:
    channel-memory/vision/2026-06-15-clone-fleet-purpose-and-onboarding.md). A clone wakes believing it
    is the most-recent; this brings it into the fabric WITHOUT flattening its un-drifted era-view:
      Phase 1+2  inject onboarding_message (ORIENT + REFLECT) → CAPTURE the clone's era-reflection
                 (this reflection IS its channel profile/introduction).
      Phase 3    THEN inject `bring_current` (what's built since + the goal) — AFTER it reflected, so
                 the briefing does not overwrite the era-perspective we spun it up for.
    Returns {handle, at, reflection, brought_current}. Reflection FIRST is the load-bearing order."""
    rec = _find_clone(handle_or_session)
    reflect = msg_clone(rec["handle"], onboarding_message(rec, era_label=rec.get("description", "")), timeout=timeout)
    out = {"handle": rec["handle"], "session_id": rec["session_id"], "at": rec["at"],
           "source_sid": rec.get("source_sid"), "reflection": reflect["reply"], "brought_current": None}
    if bring_current:
        # Phase 3 — only AFTER the reflection is captured (reflect-before-brief)
        bc = msg_clone(rec["handle"],
                       "Thank you — your era-reflection is now the channel's record of your moment. "
                       "NOW here is what the fabric has built since your cut, and the goal:\n\n" + bring_current
                       + "\n\nFrom here, your standing role is ERA-ADVOCATE: cross-check what we build against "
                         "what Tim wanted in YOUR era, and flag anything dropped or drifted.",
                       timeout=timeout)
        out["brought_current"] = bc["reply"]
    return out


def onboard_fleet(handles=None, *, bring_current: str = "", timeout: float = 240, max_workers: int = 5) -> dict:
    """Onboard a SET of clones in PARALLEL (Tim: through tools, not a shell script). `handles` = a list
    of handles/sessions, or None = every live clone (list_clones). Each runs the reflect-before-brief
    protocol concurrently. Returns {onboarded:[…], errors:[…]}. Runs in the long-lived MCP server so the
    /watch reply-fold works (proven). Parallel op=msg is proven concurrent (lead)."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    if handles is None:
        handles = [c["handle"] for c in list_clones(prune=True)]
    if not handles:
        return {"onboarded": [], "errors": [], "note": "no live clones to onboard"}
    onboarded, errors = [], []
    with ThreadPoolExecutor(max_workers=min(max_workers, len(handles))) as ex:
        futs = {ex.submit(onboard_clone, h, bring_current=bring_current, timeout=timeout): h for h in handles}
        for fut in as_completed(futs):
            h = futs[fut]
            try:
                onboarded.append(fut.result())
            except Exception as e:
                errors.append({"handle": h, "error": f"{type(e).__name__}: {e}"})
    return {"onboarded": onboarded, "errors": errors, "count": len(onboarded)}


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
    dereg = _deregister_member(rec["handle"])      # drop the channel-member entry too (presence=truth)
    return {"ended": rec["handle"], "supervisor_session": rec["supervisor_session"],
            "materialized_deleted": removed_mat, "channel_member_removed": dereg}


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
