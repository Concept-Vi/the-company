"""mcp_face/tools/automation.py — the ⑤ AUTOMATION agent face (Capability Fabric §3.3).

The MCP face for ⑤'s four resources. RESOURCE-KEYED (matches the CONVENTIONS named-act grain — A2/E1),
glob-auto-registered by mcp_face/server.py's pkgutil discovery (ZERO server.py edit — §1.3). Each tool
is THIN: validate op ∈ OPS → delegate to the SAME runtime.capability_handlers handler the bridge route
calls (DRY: one handler, two faces — drift-tested byte-identical by tests/capability_handlers_acceptance.py).
The face NEVER executes a rail (the floor — sessions.py:332 precedent: the face APPENDS/READS, a SERVICE
acts). It imports nothing that spawns/shells.

THE FOUR TOOLS (every fact grounded in the Claude-Code Atlas 2026-06-12):
  routines(op=list|get|act, …)   — CC-21 · cloud routines + session-tasks (direct-read / R3)
  workflows(op=list|get|act, …)  — CC-22 · /goal (R1) + /loop (R2); multi-session is session_post(consult)
  cost(op=read, …)               — CC-20 · the usage fold over agent_sessions.turn (direct-read)
  auth(op=get)                   — CC-24.1 reopened · credential method, REDACTED (direct-read)

CONSOLIDATED-OP LAW: a new need is a new `op`/`act`, never a new flat tool. Each tool exports a closed
`OPS` constant — the contract corpus's machine inventory (CONTRACT-FORMAT §9.2: extract_reality.py fails
loud on a tool module without one). The module-level OPS dict aggregates them for the foundation/DRY test.
"""
from typing import Literal
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from contracts.tools import ToolAnnotations as CompanyToolAnnotations   # the honest contracts model
from mcp.types import ToolAnnotations as SDKToolAnnotations             # the SDK's hint carrier
from runtime import capability_handlers as ch

# the per-tool closed op sets — mirror the handler-family ROUTINES_OPS/… (single source: the handler).
# Imported so the face and the handler can NEVER drift on the op vocabulary.
from runtime.capability_handlers.automation import (
    ROUTINES_OPS, WORKFLOWS_OPS, COST_OPS, AUTH_OPS,
    ROUTINES_ACTS, WORKFLOWS_ACTS, AUTH_ACTS,
)

# EXPORTED closed op inventory for this consolidated module (CONTRACT-FORMAT §9.2). One entry per
# resource-tool; the DRY test joins these against the bridge arms + the HANDLERS keys.
OPS = {
    "auto.routines": ROUTINES_OPS,
    "auto.workflows": WORKFLOWS_OPS,
    "auto.cost": COST_OPS,
    "auto.auth": AUTH_OPS,
}


def _to_sdk_annotations(ann: CompanyToolAnnotations, title: str) -> SDKToolAnnotations:
    """contracts.ToolAnnotations → SDK hints (the sessions.py wiring). The contracts model's own gate
    (readonly∧destructive raises) bites BEFORE registration — an incoherent annotation never reaches a
    client. readonly mirrors the HANDLERS readonly flag (registry-is-truth)."""
    return SDKToolAnnotations(
        title=title, readOnlyHint=ann.readonly, destructiveHint=ann.destructive,
        idempotentHint=ann.idempotent, openWorldHint=False)


def _ro(key: str) -> bool:
    """The readonly flag for a handler key — from the HANDLERS registry, never hand-typed (the rail/
    readonly coherence is the registry's, §3.2)."""
    return ch.HANDLERS[key].readonly


def register(mcp, suite):
    # ensure THIS family's fns are wired onto HANDLERS before we delegate (idempotent — re-import is a
    # Python no-op). We import OUR handler module directly, NOT ch.load_all() — load_all pulls all three
    # family modules (config_authoring/dev_bridges/automation) and would couple this file-disjoint lane
    # to the sibling lanes' files before they land. Each face wires its own family; the DRY test (which
    # DOES want the full registry) calls load_all once all three exist.
    from runtime.capability_handlers import automation as _automation  # noqa: F401 (wires on import)

    # ── auto.routines (CC-21) ───────────────────────────────────────────────────────────────────────
    @mcp.tool(annotations=_to_sdk_annotations(
        CompanyToolAnnotations(readonly=_ro("auto.routines"), destructive=False, idempotent=False),
        "Automation — routines (cloud routines + session tasks)"))
    def routines(op: Literal["list", "get", "act"], act: str = "", routine_id: str = "",
                 cron: str = "", prompt: str = "", task_id: str = "", consent: bool = False) -> dict:
        """⑤ ROUTINES — the scheduled-work surface (CC-21). Pick `op`:

          op="list"/"get" — the cloud-routine + session-task surface (DIRECT-READ): cloud routines are
                             Anthropic-resident, read via the native `claude schedule list`; an empty
                             result is honest (no routines), never fabricated. `routine_id` narrows get.
          op="act"        — steer one routine/task. `act` ∈ {run-now, pause, one-off, cancel-session-task}:
                             run-now/pause/one-off steer a CLOUD routine (native `claude schedule …`);
                             cancel-session-task cancels a SESSION-scoped task by its 8-char `task_id`
                             (native CronDelete; Esc clears a pending /loop). ALL ride R3 (the config-
                             writer service shells them, consent-gated) — this face NEVER shells: it
                             returns the PROPOSED argv + the R3 routing + the consent path.
                             `cron`/`prompt` parameterise a one-off; `routine_id` names the cloud routine.

        Cloud routines run on Anthropic infra (min 1h interval, no local files); session tasks are local
        and session-scoped (≤50/session). The consequence is observed by re-reading op='list', never
        returned on an act (async honesty — §3.3)."""
        return ch.HANDLERS["auto.routines"].fn(
            suite, op, act=act, routine_id=routine_id, cron=cron, prompt=prompt,
            task_id=task_id, consent=consent)

    # ── auto.workflows (CC-22) ────────────────────────────────────────────────────────────────────────
    @mcp.tool(annotations=_to_sdk_annotations(
        CompanyToolAnnotations(readonly=_ro("auto.workflows"), destructive=False, idempotent=False),
        "Automation — workflows (/goal keep-going · /loop)"))
    def workflows(op: Literal["list", "get", "act"], act: str = "", session: str = "",
                  condition: str = "", interval: str = "", prompt: str = "",
                  from_session: str = "") -> dict:
        """⑤ WORKFLOWS — the native keep-going modes as a company face (CC-22). Pick `op`:

          op="list"/"get" — the mode catalog (DIRECT-READ): goal (until-condition, R1), loop (on-
                             interval, R2), and a POINTER to the LIVE multi-session primitive
                             session_post(verb=consult) — the consult-fan, which is NOT here (workflows
                             links to it, never rebuilds it). `session` narrows the view.
          op="act"        — `act` ∈ {set-goal, goal-status, clear-goal, loop}:
                             • set-goal/goal-status/clear-goal (R1) steer ONE session's /goal — needs
                               `session` (session-scoped) and, for set-goal, a `condition` (the verifiable
                               end state a fresh evaluator checks each turn; needs hooks enabled). The
                               handler builds a supervisor DELIVER intent (a /goal-prefixed turn); the
                               SUPERVISOR injects it — this face NEVER injects. Receipt + watch cursor.
                             • loop (R2) starts an interval keep-going — needs `interval` (e.g. '5m';
                               cron-backed), optional `prompt`. Builds a wire-JOB intent behind /api/
                               resolve (operator-only); the wire launches the headless run. Job receipt +
                               watch. NOT the supervisor mailbox (a separate rail, §1.1).

        MULTI-session parallel is session_post(verb=consult) (ALREADY LIVE) — not a workflows act. Every
        act returns an intent/job receipt, never a pretended result (async honesty — §3.3)."""
        return ch.HANDLERS["auto.workflows"].fn(
            suite, op, act=act, session=session, condition=condition, interval=interval,
            prompt=prompt, from_session=from_session)

    # ── auto.cost (CC-20) ─────────────────────────────────────────────────────────────────────────────
    @mcp.tool(annotations=_to_sdk_annotations(
        CompanyToolAnnotations(readonly=_ro("auto.cost"), destructive=False, idempotent=True),
        "Automation — cost/usage (fold over agent_sessions.turn)"))
    def cost(op: Literal["read"] = "read", session: str = "", since: int = -1, limit: int = 200) -> dict:
        """⑤ COST/USAGE (CC-20) — a DIRECT-READ fold over the `usage` block the supervisor ALREADY stamps
        onto agent_sessions.turn (session_supervisor._extract_usage). Sums input/output/cache tokens +
        cost across turns, optionally for one `session` (id or session://<id>), from event-seq `since`
        (-1 = all), capped at `limit` most-recent turns. costUSD is a CLIENT-SIDE ESTIMATE, NOT the bill.
        An empty/zero fold is HONEST (no turns with usage yet / supervisor hasn't run), never fabricated.
        Read-only; shells nothing, spawns nothing."""
        return ch.HANDLERS["auto.cost"].fn(suite, op, session=session, since=since, limit=limit)

    # ── auto.auth (CC-24, reopened) ───────────────────────────────────────────────────────────────────
    @mcp.tool(annotations=_to_sdk_annotations(
        CompanyToolAnnotations(readonly=_ro("auto.auth"), destructive=False, idempotent=False),
        "Automation — auth (credential method READ, redacted · reopened host-config acts)"))
    def auth(op: Literal["get", "act"] = "get", act: str = "", consent: bool = False) -> dict:
        """⑤ AUTH (CC-24, reopened by Tim's sole-operator steer). Pick `op`:

          op="get"  (CC-24.1) — DIRECT-READ the credential METHOD, REDACTED. `claude auth status` (JSON);
                     the secret NEVER transits — redaction is enforced on the read output (the strip-
                     fields are listed in the response). Returns the method (subscription / console-api /
                     token) + account label, never the token/api_key/oauth secret.
          op="act"  (CC-24.2/.3/.4, REOPENED) — a host-config credential STEER on rail R3, consent-gated,
                     NEVER locked out (consent-not-lockdown; git-revert / re-login is the backstop):
                     • relogin    — `claude auth login` (re-authenticate / switch account)
                     • logout     — `claude auth logout` (clear / switch the credential; reversed by relogin)
                     • setup-token— `claude setup-token` (mint a one-year inference-only token — PRINTS the
                                    secret to the operator terminal; this face NEVER returns the token)
                     This face NEVER shells: it returns the PROPOSED argv + the R3 routing + the consent
                     path; the config_writer service shells it. `consent=true` rides the consequential call.

        The credential acts are NOT absence-of-row boundaries (the arch's original ruling) — Tim reopened
        them as buildable consent-gated capabilities. Every act returns an intent receipt + watch (re-read
        op='get'), never a pretended result; setup-token's printed secret is surfaced to the operator
        terminal ONLY (§5.2 C3 honoured by NOT returning it)."""
        return ch.HANDLERS["auto.auth"].fn(suite, op, act=act, consent=consent)

    return routines, workflows, cost, auth
