"""runtime/capability_handlers/automation.py — the ⑤ AUTOMATION handler family (Capability Fabric §3.2/§4).

The DRY layer for ⑤'s four resources. PURE functions over `Suite` — no socket, no MCP decorator, no
`claude -p`, no model load (the lead-only law: a worker NEVER fires claude / loads a model — this code
builds the intent/job/argv and routes it; a sanctioned SERVICE acts). EACH handler's RAIL was declared
in capability_handlers/__init__.py (registry-is-truth); this module WIRES the real fn onto the
pre-declared slot via register_handler — `building`, honest-pending until the rail's executor
round-trips by use.

THE FOUR RESOURCES + their rails (arch §4 ⑤ table, every fact grounded in the Claude-Code Atlas
2026-06-12 — never invented):

  auto.routines  (CC-21) → list/get = direct-read (cloud routines are Anthropic-resident — a thin host
                  `claude schedule list` read); act{run-now,pause,one-off,cancel-session-task} = R3
                  (the native scheduling CLI / CronDelete — a thin bridge, the config_writer service is
                  the sanctioned shelling process). Atlas scheduled-tasks.md: the session-scoped cron
                  tools are CronCreate/CronList/CronDelete (8-char ids, ≤50/session; Esc clears a
                  pending /loop; CLAUDE_CODE_DISABLE_CRON=1 disables). Cloud routines = /schedule,
                  Anthropic-managed, min 1h interval.

  auto.workflows (CC-22) → list/get = direct-read; act{set-goal,goal-status,clear-goal} = R1 (a
                  per-session goal STEER routed via the supervisor mailbox deliver/inject — /goal is a
                  session-scoped prompt-based Stop hook, Atlas goal.md: each turn the condition+convo
                  are sent to a fresh evaluator model, default small-fast; needs hooks enabled);
                  act{loop} = R2 (an interval keep-going = a SCHEDULED wire job — /loop is cron-backed,
                  session-scoped, Atlas scheduled-tasks.md). MULTI-session parallel is NOT here — it is
                  ALREADY-LIVE as session.post(verb=consult) (the consult-fan); this handler LINKS to
                  it, never rebuilds it.

  auto.cost      (CC-20) → direct-read: a FOLD over the `usage` block the supervisor ALREADY stamps onto
                  agent_sessions.turn (session_supervisor._extract_usage — verified built, §1.5; NOT
                  net-new). costUSD is a CLIENT-SIDE ESTIMATE, never the authoritative bill.

  auto.auth      (CC-24.1, reopened) → direct-read: the credential METHOD, REDACTED (host_reads row
                  `claude auth status` → JSON; the secret NEVER transits). The host ACTS
                  (relogin/logout/setup-token = CC-24.2/.3/.4) are OUT — absence-of-row IS the boundary
                  (§1.8/§5.2 C3). The act here is the REOPENED read Tim pulled back in.

THE FLOOR (the rail split is the security boundary):
  · direct-read (auth/cost/routines-read/workflows-read) — DECLARATIVE-DIRECT: shells nothing dangerous,
    writes nothing, spawns nothing; safe on every face incl. a cold external agent. Auth output is
    REDACTED at the source (the secret never transits — §5.2 C3).
  · R3 (routines act) — the handler builds the intent; the config_writer SERVICE (sanctioned, consent-
    gated) shells the native scheduling CLI. This handler returns the proposed argv/intent + the
    consent path; it NEVER shells.
  · R1 (workflows goal) — the handler builds a per-session deliver intent (a /goal-prefixed turn); the
    SUPERVISOR injects it. Handler returns a receipt + the watch cursor.
  · R2 (workflows loop) — the handler builds a wire-job intent behind /api/resolve (operator-only); the
    wire (implement.py) launches it. Handler returns a job receipt + the watch cursor.

ASYNC HONESTY (arch §3.3/§8): R1/R2/R3 acts return a RECEIPT (the intent/job + a watch cursor / consent
path), NEVER a pretended typed result on the call. The consequence rides the rail's own executor; the
corpus flips building→live only when that executor round-trips BY USE (live-verify pending lead — a
real /goal turn, a real /loop job, a real schedule/CronDelete fire, a real `claude auth status`).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from runtime import capability_handlers as ch
from runtime.capability_handlers.reduction import host_reads as HR

# the closed op vocabulary per resource (the uniform-verb law — CONVENTIONS §). `act` carries an
# internal `act:` discriminator (the named acts registered in CONVENTIONS' F1/F2 + the reopened CC-24).
ROUTINES_OPS = ("list", "get", "act")
WORKFLOWS_OPS = ("list", "get", "act")
COST_OPS = ("read",)
AUTH_OPS = ("get",)

# the named acts per resource (CONVENTIONS named-act registry — closed; V2 closure). Each maps to a rail.
ROUTINES_ACTS = ("run-now", "pause", "one-off", "cancel-session-task")
WORKFLOWS_ACTS = ("set-goal", "goal-status", "clear-goal", "loop")

# which workflows act rides which rail (arch §4 ⑤ table — goal=R1, loop=R2). Closed map; an act not here
# is refused-loud (never a silent default rail).
WORKFLOWS_ACT_RAIL = {
    "set-goal": "R1", "goal-status": "R1", "clear-goal": "R1", "loop": "R2",
}

# the native /goal command form each goal act maps to (Atlas goal.md — grounded, never invented):
#   set-goal <condition> · goal-status = `/goal` alone · clear-goal = `/goal clear`
_GOAL_COMMAND = {
    "set-goal": "/goal {arg}",
    "goal-status": "/goal",
    "clear-goal": "/goal clear",
}

# the native scheduling CLI each routines act maps to (Atlas scheduled-tasks.md — cloud /schedule for
# cloud-routine lifecycle; CronDelete for a session-scoped task). argv-array head, value-free; the
# config_writer renders the value slots. These are PROPOSED argv, never shelled here.
_ROUTINE_CLI = {
    "run-now": ("claude", ["schedule", "run"]),     # cloud routine: run now (Atlas /schedule run)
    "pause": ("claude", ["schedule", "pause"]),      # cloud routine: pause/resume the schedule
    "one-off": ("claude", ["schedule", "create"]),   # a single non-repeating fire (auto-disables to Ran)
    "cancel-session-task": ("CronDelete", []),        # session-scoped task by 8-char id (native tool)
}


def _validate_op(resource: str, op: str, valid: tuple) -> None:
    if op not in valid:
        raise ValueError(
            f"{resource}: unknown op={op!r}. Valid: {list(valid)} (the uniform-verb law — a new need is "
            f"a new op, never an ad-hoc verb). To act, op='act' with act=<one of the named acts>.")


def _bare_session(ref: str) -> str:
    """Normalize a session reference (bare id OR session://<id>) to the bare id — matches the
    mcp_face.sessions `_sid` convention so the R1 deliver intent addresses the supervisor's registry
    by the SAME id form the session fabric uses (never a session://-prefixed mismatch)."""
    ref = (ref or "").strip()
    return ref[len("session://"):] if ref.startswith("session://") else ref


def _redact(obj, fields: tuple):
    """Strip the secret-bearing fields from a read's output (the secret NEVER transits — §5.2 C3).
    Recursive over dicts/lists; a matched key's value becomes '[REDACTED]'. Never raises — redaction is
    a floor, not an option."""
    if isinstance(obj, dict):
        return {k: ("[REDACTED]" if k in fields else _redact(v, fields)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact(x, fields) for x in obj]
    return obj


# ─────────────────────────── auto.routines (CC-21) ───────────────────────────

def routines(suite, op: str, act: str = "", routine_id: str = "", cron: str = "",
             prompt: str = "", task_id: str = "", consent: bool = False, **_p) -> dict:
    """⑤ routines — list/get the cloud-routine + session-task surface (direct-read), or act on one
    (run-now/pause/one-off = R3 cloud-schedule CLI; cancel-session-task = R3 native CronDelete). The
    handler NEVER shells: list/get returns the read row (the host read the config_writer/native surface
    serves); act returns the PROPOSED argv + the R3 routing + consent path (the config_writer service
    shells it, consent-gated). Cloud routines are Anthropic-resident — this is a thin bridge, not a
    company datastore (host_reads CC-21 row)."""
    _validate_op("auto.routines", op, ROUTINES_OPS)
    if op in ("list", "get"):
        row = HR.read_for("auto.routines")          # the direct-read row (claude schedule list)
        return {
            "resource": "auto.routines", "op": op, "rail": "direct-read",
            "read": {"source": row["source"], "argv": row["argv"], "schema": row["schema"]},
            "routine": routine_id or None,
            "teach": row["teach"],
            "note": ("list/get is a THIN host read of cloud routines (Anthropic-resident) via the native "
                     "schedule surface — not a company datastore; an empty result is honest (no routines), "
                     "never fabricated. live-verify pending (lead): a real `claude schedule list`."),
        }
    # op == "act"
    if act not in ROUTINES_ACTS:
        raise ValueError(
            f"auto.routines act: unknown act={act!r}. Named acts (CONVENTIONS routines registry): "
            f"{list(ROUTINES_ACTS)} — run-now/pause/one-off steer a CLOUD routine (native `claude "
            f"schedule …`); cancel-session-task cancels a session-scoped task by its 8-char id (native "
            f"CronDelete). All ride R3 (the config_writer service shells them — consent-gated).")
    tool, sub = _ROUTINE_CLI[act]
    if act == "cancel-session-task" and not (task_id or "").strip():
        raise ValueError(
            "auto.routines act='cancel-session-task' needs `task_id` — the 8-char id of the session-"
            "scoped scheduled task (CronList shows them; Atlas scheduled-tasks.md). Esc clears a pending "
            "/loop wakeup; this cancels a named task. Fail loud, never a no-op.")
    # build the PROPOSED intent (argv head + the value the config_writer fills). NEVER shelled here.
    proposed = {"tool": tool, "argv_head": [tool, *sub]}
    if act == "cancel-session-task":
        proposed["task_id"] = task_id.strip()
    if act in ("run-now", "pause") and (routine_id or "").strip():
        proposed["routine"] = routine_id.strip()
    if act == "one-off":
        if (cron or "").strip():
            proposed["cron"] = cron.strip()
        if (prompt or "").strip():
            proposed["prompt"] = prompt.strip()
    return {
        "resource": "auto.routines", "op": "act", "act": act, "rail": "R3",
        "status": "intent-built",
        "executor": ("config-writer service (sanctioned R3 shelling) — POST /cli, consent-gated"
                     if tool == "claude" else
                     "the native CronDelete tool (session-scoped scheduler) — operator/agent vantage"),
        "proposed": proposed,
        "consent": ("ride consent=true on the consequential R3 call, or a standing grant "
                    "(config_writer /consent class=cli-write) — consent-not-lockdown, git-revert backstop")
                   if not consent else "consented",
        "watch": "re-read via op='list' (a cancelled task disappears; a run-now/one-off appears) — "
                 "the consequence is observed on the schedule surface, never returned here.",
        "note": "live-verify pending (lead): a REAL `claude schedule …` / CronDelete fire (the handler "
                "NEVER shells — it builds the intent; the R3 service / native tool acts).",
    }


# ─────────────────────────── auto.workflows (CC-22) ───────────────────────────

def workflows(suite, op: str, act: str = "", session: str = "", condition: str = "",
              interval: str = "", prompt: str = "", from_session: str = "", **_p) -> dict:
    """⑤ workflows — the native keep-going modes as a company face. list/get = direct-read (the mode
    catalog). act{set-goal,goal-status,clear-goal} = R1 (a per-session /goal STEER routed via the
    supervisor mailbox deliver/inject — the handler builds the deliver intent, the supervisor injects;
    receipt+watch). act{loop} = R2 (an interval keep-going = a scheduled wire job behind /api/resolve —
    the handler builds the job intent, the wire launches; job receipt+watch). MULTI-session parallel is
    NOT here — it is session.post(verb=consult) (ALREADY LIVE); this links to it, never rebuilds it."""
    _validate_op("auto.workflows", op, WORKFLOWS_OPS)
    if op in ("list", "get"):
        return {
            "resource": "auto.workflows", "op": op, "rail": "direct-read",
            "modes": {
                "goal": {"acts": ["set-goal", "goal-status", "clear-goal"], "rail": "R1",
                         "native": "/goal <condition>",
                         "what": "keep working toward a verifiable end state without per-step prompting; "
                                 "a fresh evaluator model checks the condition after each turn (needs "
                                 "hooks enabled). Atlas goal.md."},
                "loop": {"acts": ["loop"], "rail": "R2",
                         "native": "/loop <interval> <prompt>",
                         "what": "interval keep-going (cron-backed, session-scoped, runs until Esc/7-day "
                                 "expiry). Atlas scheduled-tasks.md."},
                "parallel": {"acts": [], "rail": "n/a",
                             "what": "the LIVE multi-session primitive is NOT here — it is "
                                     "session.post(verb=consult) (the consult-fan, ALREADY LIVE). "
                                     "Use the `sessions`/`session_post` tools; workflows links, never rebuilds."},
            },
            "session": session or None,
            "note": "the chooser between three keep-going meanings: goal=until-condition (R1), "
                    "loop=on-interval (R2), parallel=fan (consult, live). live-verify pending (lead) "
                    "for the goal/loop executors.",
        }
    # op == "act"
    if act not in WORKFLOWS_ACTS:
        raise ValueError(
            f"auto.workflows act: unknown act={act!r}. Named acts (CONVENTIONS workflows registry): "
            f"{list(WORKFLOWS_ACTS)} — set-goal/goal-status/clear-goal steer one session's /goal (R1); "
            f"loop starts an interval keep-going (R2). MULTI-session is session_post(verb=consult), not here.")
    rail = WORKFLOWS_ACT_RAIL[act]

    if rail == "R1":
        # a per-session goal STEER → a supervisor deliver/inject intent (a /goal-prefixed turn). The
        # handler builds the intent (the EXACT native /goal command, grounded in Atlas goal.md); the
        # SUPERVISOR injects it (the floor — this handler never injects). Receipt + watch cursor.
        if not (session or "").strip():
            raise ValueError(
                f"auto.workflows act={act!r} (R1) needs `session` — /goal is SESSION-SCOPED (it steers ONE "
                f"live session's keep-going). Pass the target session id (session://<id>); "
                f"sessions(op='list') shows the fleet. Fail loud, never a fabric-wide goal.")
        if act == "set-goal" and not (condition or "").strip():
            raise ValueError(
                "auto.workflows act='set-goal' needs `condition` — the verifiable end state the evaluator "
                "checks after each turn (Atlas goal.md: e.g. 'all tests in test/auth pass and lint is "
                "clean'). An empty goal is nothing to work toward. Fail loud.")
        command = _GOAL_COMMAND[act].format(arg=(condition or "").strip())
        sid = _bare_session(session)
        return {
            "resource": "auto.workflows", "op": "act", "act": act, "rail": "R1",
            "status": "intent-built",
            "executor": "the session supervisor (sole injector) — POST /inject, or session_post(verb="
                        "deliver) → the supervisor injects this turn into the live session",
            "intent": {"session": sid, "verb": "deliver",
                       "message": command,
                       "from_session": (from_session or "").strip() or None},
            "native_command": command,
            "requires": "hooks enabled in the target session (the /goal evaluator is a prompt-based Stop "
                        "hook — Atlas goal.md). A session without hooks cannot evaluate the goal.",
            "watch": f"sessions(op='watch', session='{sid}') — the goal evaluator's turns ride "
                     f"agent_sessions.turn after this is injected; goal-status surfaces the evaluator's reason.",
            "note": "live-verify pending (lead): a REAL /goal turn injected into a live session (the "
                    "handler NEVER injects — it builds the deliver intent; the supervisor acts).",
        }

    # rail == "R2" — loop: an interval keep-going = a SCHEDULED wire job behind /api/resolve (operator-
    # only). The handler builds the job intent (the native /loop command); the wire (implement.py)
    # launches the headless run. Job receipt + watch.
    if not (interval or "").strip():
        raise ValueError(
            "auto.workflows act='loop' needs `interval` — /loop is cron-backed (Atlas scheduled-tasks.md: "
            "s/m/h/d units; seconds round up to the minute). e.g. '5m'. Fail loud, never an unbounded loop "
            "without a cadence.")
    command = f"/loop {interval.strip()}" + (f" {prompt.strip()}" if (prompt or "").strip() else "")
    return {
        "resource": "auto.workflows", "op": "act", "act": "loop", "rail": "R2",
        "status": "job-built",
        "executor": "the headless wire (implement.py) behind /api/resolve (operator-only) — a scheduled "
                    "claude -p keep-going job; NOT the supervisor mailbox (a separate rail, §1.1).",
        "job": {"kind": "wire-loop", "native_command": command,
                "interval": interval.strip(), "prompt": (prompt or "").strip() or "(maintenance prompt)"},
        "operator_gate": "the consequential launch rides /api/resolve (operator vantage) — a cold agent "
                         "may PROPOSE the job, the operator confirms (consent-not-lockdown).",
        "watch": "the job's consequence rides the existing wire dispatch events (the /api/resolve seam); "
                 "re-read via op='list'.",
        "note": "live-verify pending (lead): a REAL /loop wire job (the handler NEVER launches claude -p — "
                "it builds the job intent; the wire acts behind the operator gate).",
    }


# ─────────────────────────── auto.cost (CC-20) ───────────────────────────

def cost(suite, op: str = "read", session: str = "", since: int = -1, limit: int = 200, **_p) -> dict:
    """⑤ cost/usage — a direct-read FOLD over the `usage` block the supervisor ALREADY stamps onto
    agent_sessions.turn (session_supervisor._extract_usage — §1.5, NOT net-new). Reads the events store
    (no spawn, no shell), sums tokens + cost across turns, optionally for one session. costUSD is a
    CLIENT-SIDE ESTIMATE (cost-usage.md), never the authoritative bill — surfaced honestly."""
    _validate_op("auto.cost", op, COST_OPS)
    sid = session.strip()
    if sid.startswith("session://"):
        sid = sid[len("session://"):]
    # read the turn events — the fold source. Honest absence (no turns / supervisor down → zeros).
    try:
        events = suite.store.events_since(since)
    except Exception as e:                                   # fail loud, never a fabricated total
        raise RuntimeError(f"auto.cost: could not read the events store for the usage fold ({e}) — "
                           f"the cost read folds agent_sessions.turn `usage`; if the store is "
                           f"unreachable that is a real breakage, not a zero total.") from e
    turns = [e for e in events if e.get("kind") == "agent_sessions.turn"
             and isinstance(e.get("usage"), dict)
             and (not sid or e.get("session") == sid)]
    if limit and len(turns) > limit:
        turns = turns[-limit:]
    total = {"input_tokens": 0, "output_tokens": 0,
             "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0, "cost_usd": 0.0}
    by_model: dict = {}
    counted = 0
    for t in turns:
        u = t["usage"]
        counted += 1
        for k in ("input_tokens", "output_tokens",
                  "cache_read_input_tokens", "cache_creation_input_tokens"):
            v = u.get(k)
            if isinstance(v, (int, float)):
                total[k] += v
        c = u.get("cost_usd")
        if isinstance(c, (int, float)):
            total["cost_usd"] += c
        m = u.get("model")
        if m:
            by_model.setdefault(m, 0)
            by_model[m] += 1
    return {
        "resource": "auto.cost", "op": "read", "rail": "direct-read",
        "session": ("session://" + sid) if sid else None,
        "turns_counted": counted, "total": total, "by_model_turn_count": by_model,
        "source": "agent_sessions.turn `usage` fold (session_supervisor._extract_usage — already stamped)",
        "estimate": "costUSD is a CLIENT-SIDE ESTIMATE (cost-usage.md), NOT the authoritative bill.",
        "note": ("an empty/zero fold is HONEST (no turns with usage yet, or the supervisor hasn't run) — "
                 "never a fabricated total. Verified-by-use the moment a turn with usage exists."),
    }


# ─────────────────────────── auto.auth (CC-24.1, reopened) ───────────────────────────

def auth(suite, op: str = "get", **_p) -> dict:
    """⑤ auth — the REOPENED credential-method READ (CC-24.1; Tim pulled it back in). direct-read: the
    credential METHOD, REDACTED (host_reads row `claude auth status` → JSON; the secret NEVER transits —
    §5.2 C3). The host ACTS (relogin/logout/setup-token = CC-24.2/.3/.4) are OUT — absence-of-row IS the
    boundary, NOT a redacted endpoint that returns a secret (§1.8). The handler returns the read row + the
    redaction contract; the config_writer/host surface runs the read (no secret ever reaches a wire)."""
    _validate_op("auto.auth", op, AUTH_OPS)
    row = HR.read_for("auto.auth")
    redact = HR.redaction_for("auto.auth")
    return {
        "resource": "auto.auth", "op": "get", "rail": "direct-read",
        "read": {"source": row["source"], "argv": row["argv"], "schema": row["schema"]},
        "redaction": {"fields_stripped": list(redact),
                      "contract": "these fields are stripped at the source — the secret NEVER transits "
                                  "the primitive (§5.2 C3). _redact() is the floor applied to the read "
                                  "output before it leaves the handler."},
        "boundary": "relogin/logout/setup-token (CC-24.2/.3/.4) are HOST acts — NO op, NO endpoint. "
                    "Absence-of-row IS the boundary; there is NO redacted path that returns a secret.",
        "teach": row["teach"],
        "note": "live-verify pending (lead): a REAL `claude auth status` (method only, redacted). The "
                "handler NEVER returns a secret — redaction is enforced on the read output, not hoped for.",
        "_redact": "use automation._redact(output, fields_stripped) on the raw `claude auth status` JSON",
    }


# ─────────────────────────── wire the family onto the pre-declared HANDLERS slots ───────────────────

ch.register_handler("auto.routines", routines)
ch.register_handler("auto.workflows", workflows)
ch.register_handler("auto.cost", cost)
ch.register_handler("auto.auth", auth)
