"""runtime/capability_handlers/dev_bridges.py — ④ DEV-BRIDGES handlers (Capability Fabric §4, lane L-④-dev).

THE SPINE (§3.2): pure functions over `Suite`. NO socket, NO MCP decorator, NO `claude -p`, NO direct
spawn. Each handler BUILDS the intent/job/argv for its rail and routes it to the SANCTIONED actor; it
never executes the dangerous rail itself (the floor — §1.2: the face APPENDS, a service ACTS). Wired
onto the pre-declared HANDLERS slots on import (register_handler swaps stub→real, flips .built True).

THE FOUR RAILS ④ SPANS (the decisive finding — rails exist, NOT one; §1.1):
  · dev.git          → R3   : structured git/gh via the config_writer service (argv-array, sha/exit).
  · dev.ci           → R3   : ci list/get (direct read) + scaffold (.github/workflows/*.yml file write).
  · dev.code_intel   → R1-prime : in-session LSP — a bridge-session spawn INTENT; PROSE result, NO return_shape.
  · dev.computer_use → R1-prime : in-session web/browser/computer — same spawn intent; browser/computer
                                   are host/rail boundaries REFUSED-LOUD on this headless WSL `-p` rail (§5.4).
  · dev.code_review  → R2   : headless `claude -p` review behind /api/resolve — a WIRE-JOB intent + job-id.

THE HANDLER SIGNATURE is `fn(suite, op, **params) -> dict`. `op ∈ {list, get, act}` (the uniform verbs;
the consolidated tool's op multiplex). `act=` carries the named act (the F1/F7 named-act registry values).

────────────────────────────────────────────────────────────────────────────────────────────
SOLE-OPERATOR FLOOR (Tim's explicit steer — overrides any inherited multi-user caution)
────────────────────────────────────────────────────────────────────────────────────────────
Tim is the ONLY user and is TRUSTED. The dangerous ④ capabilities — native git/gh writes, plugin-grade
in-session Bash via the R1-prime spawn, computer-use, CI-file writes — are ENABLED, never locked out,
never behind a multi-user auth wall. The gate is a CONSENT BEAT + git-revert backstop, NOT a denial:
  · A handler that ROUTES to a write/exec rail passes `consent` through to the actor (config_writer's
    consent-not-lockdown beat for R3; spawn_bridge_session's operator_consent for R1-prime; the
    operator-only /api/resolve seam for R2). WITHOUT a consent signal the actor returns a PENDING
    PROPOSAL (a cold agent may propose; the consequential act is operator-confirmed) — never a slammed door.
  · Reads (git status/log/worktrees, ci list/get) are DECLARATIVE-DIRECT — ungated, always run.
The handler's job is to BUILD the request faithfully and route it; the CONSENT enforcement lives in the
sanctioned actor (so the floor is a property of the rails, not a policy a handler must remember — §5).

THE FLOOR THIS LANE NEVER CROSSES (lead-only law): nothing here fires `claude -p`, spawns a real
bridge-session, runs a real `claude mcp`/`git commit`, or loads a model. The handlers BUILD the
intent/argv/job; the REAL round-trips (an R1-prime LSP nav returning prose, an R2 review job's
consequence events, a real `git commit` sha) are the build lead's **live-verify pending (lead)** slice —
unit-tested here against STUBS, NEVER green-painted to live.

INTROSPECTIVE-DATA + FAIL-LOUD (§5.6): unknown op/act, a missing required param, a host-boundary
capability, or a service refusal → a TEACHING ValueError (no silent no-op, no fabricated success).
The structured {code,teach,retryable} envelope is NOT yet on the wire (CONVENTIONS admits this) —
teach-TEXT today, the envelope a named follow-up.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

from runtime.capability_handlers import register_handler
from runtime.capability_handlers.reduction import cli_allowlist as CL
from runtime.capability_handlers.reduction import session_capabilities as SC

# The R3 config_writer service (the structured git/gh + CI-file-write actor). 127.0.0.1:8772 — the ONE
# number ops/services.json + config_writer.CONFIG_WRITER_ROUTES cite. Call-time env read (the
# implement.py permission_mode precedent) so a deliberately-set port is honoured without a restart.
def _config_writer_base() -> str:
    port = os.environ.get("COMPANY_CONFIG_WRITER_PORT", "8772")
    return f"http://127.0.0.1:{port}"


_OPS = ("list", "get", "act")
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_op(handler: str, op: str) -> None:
    if op not in _OPS:
        raise ValueError(
            f"{handler}: unknown op={op!r}. Valid: {list(_OPS)} — list/get are reads, act carries a "
            f"named act (act=…). A new need is a new act on this resource, never a new flat handler.")


# ─────────────────────────── the R3 config_writer client (git/gh + ci file write) ───────────────────
# The handler is the CALLER of the sanctioned service; it never shells git itself. `_post` is the only
# place this lane touches the actor — fail-loud on a down service (no silent empty, no fabricated sha).

def _cw_post(path: str, body: dict) -> dict:
    """POST to the config_writer service. FAILS LOUD (teaching) when the service is down — the structured
    git/gh + CI-file-write rail runs ONLY through it (the floor). A `run=False` body is the unit-test
    path the actor itself honours (argv without executing); we never inject that — the caller decides."""
    url = _config_writer_base() + path
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=310) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        # the service returns teaching text on 400/409 — surface it, never swallow it.
        detail = ""
        try:
            detail = json.loads(e.read() or b"{}").get("error", "")
        except Exception:
            pass
        raise ValueError(
            f"config_writer refused {path} ({e.code}): {detail or e.reason} — the R3 git/ci rail runs "
            f"only through the config_writer service; fail loud, never a fabricated success.")
    except urllib.error.URLError as e:
        raise ValueError(
            f"the R3 config_writer service is not reachable at {url} ({e.reason}). The structured "
            f"git/gh + CI-scaffold rail runs ONLY through it (the floor — this handler never shells "
            f"git itself). Start it: `company up config-writer`. Fail loud, never a silent no-op.")


# ─────────────────────────── dev.git (CC-06) — R3 structured git/gh ───────────────────
# Reads (status/log/worktrees) are DECLARATIVE-DIRECT; writes (commit/open-pr/worktree-*) ride the R3
# config_writer consent beat. STRUCTURED result (sha/exit) — NOT R1-prime prose (§4 git row; one rail
# per op, the |-ambiguity Critique B flagged is resolved by routing commit through R3 plain-git).

# the act → cli_allowlist key map (the named acts of git, F1 registry). worktree.{create,remove} fold
# onto the worktree-add/remove allowlist rows; status/log/worktrees are the reads.
_GIT_READ_ACTS = {"status": "dev.git:status", "log": "dev.git:log", "worktrees": "dev.git:worktrees"}
_GIT_WRITE_ACTS = {
    "commit": "dev.git:commit",
    "open-pr": "dev.git:open-pr",
    "rebase": "dev.git:commit",            # rebase rides the same plain-git argv shape via `args`
    "worktree-create": "dev.git:worktree-add",
    "worktree-remove": "dev.git:worktree-remove",
}


def git(suite, op, *, act: str = "", cwd: str = "", args=None, consent: bool = False,
        run: bool = True, **_ignore) -> dict:
    """dev.git (CC-06) — R3 STRUCTURED git/gh in a repo cwd (sha/exit), the structured-sha path (NOT the
    R1-prime prose path). Reads ungated; writes ride the config_writer git-write consent beat.

      op=list  → the read acts available (status/log/worktrees) + the write acts (the discoverable surface).
      op=get   → a git READ: act ∈ {status, log, worktrees}; status/worktrees are porcelain, log takes `args`.
      op=act   → a git WRITE: act ∈ {commit, open-pr, rebase, worktree-create, worktree-remove}; runs
                 `git`/`gh` argv-array in `cwd` via the R3 service (consent-gated, fail-loud on nonzero exit).

    `cwd` is the repo (defaults to the company repo root). `args` is the extra argv list (e.g. the commit
    message: ["-m", "msg"]). `consent` rides through to the config_writer consent beat (sole-operator:
    a write WITHOUT consent gets a pending-proposal receipt, never a denial). `run=False` returns the
    argv without executing (the unit-test / preview path — argv-array injection-resistance is provable
    without a real commit)."""
    _require_op("dev.git", op)
    repo = cwd.strip() or _REPO_ROOT
    if op == "list":
        return {"op": "list", "resource": "dev.git", "rail": "R3",
                "reads": sorted(_GIT_READ_ACTS), "writes": sorted(_GIT_WRITE_ACTS),
                "note": "reads are direct (ungated); writes ride the config_writer git-write consent "
                        "beat (sole-operator consent-not-lockdown). Structured sha/exit, not prose."}
    if op == "get":
        if act not in _GIT_READ_ACTS:
            raise ValueError(
                f"dev.git op=get: act={act!r} is not a git READ. Reads: {sorted(_GIT_READ_ACTS)} "
                f"(status/log/worktrees). For commit/pr/worktree changes use op=act.")
        body = {"act": _GIT_READ_ACTS[act], "cwd": repo, "run": run}
        if args is not None:
            body["args"] = list(args)
        out = _cw_post("/git", body)
        # spread the actor echo FIRST, then the handler's authoritative face keys — so the friendly
        # `act` (status/log/worktrees) wins over the actor's echoed cli_allowlist key (dev.git:status).
        return {**out, "op": "get", "resource": "dev.git", "rail": "R3", "act": act}
    # op == act — a git WRITE
    if act not in _GIT_WRITE_ACTS:
        raise ValueError(
            f"dev.git op=act: act={act!r} is not a git WRITE. Writes: {sorted(_GIT_WRITE_ACTS)} "
            f"(commit/open-pr/rebase/worktree-create/worktree-remove). For status/log/worktrees use op=get.")
    body = {"act": _GIT_WRITE_ACTS[act], "cwd": repo, "consent": bool(consent), "run": run}
    if args is not None:
        body["args"] = list(args)
    out = _cw_post("/git", body)
    return {**out, "op": "act", "resource": "dev.git", "rail": "R3", "act": act}


# ─────────────────────────── dev.ci (CC-30) — R3 ci file write + reads ───────────────────
# CI scaffolding IS a config-file write (the unification, §4 + Proposal B's insight) — same R3 primitive
# as a .claude write, but the target is .github/workflows/*.yml. There is NO separate "CI scaffolder".
# The inbound CI acts (mention/event) have NO company face — the CI provider drives @claude; absence-of-
# op IS the boundary (§4 — contracted, not exposed).

_CI_WF_DIR = os.path.join(".github", "workflows")


def _safe_ci_name(name) -> str:
    """A workflow file `name` must be a bare id (the config_writer _safe_name pattern, re-derived for the
    .github/workflows root — anti-traversal). `..`, slashes, a leading dot are refused HERE."""
    import re
    if not isinstance(name, str) or "/" in name or "\\" in name or ".." in name \
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
        raise ValueError(
            f"dev.ci: workflow name {name!r} must be a BARE id (letters/digits then [._-], no slashes, "
            f"no '..', no leading dot) — a path component would let the write escape .github/workflows/ "
            f"(traversal). Fail loud.")
    return name


def ci(suite, op, *, act: str = "", name: str = "", body: str = "", cwd: str = "",
       consent: bool = False, run: bool = True, **_ignore) -> dict:
    """dev.ci (CC-30) — CI/CD scaffolding as a config-file write (the §4 unification: same R3 primitive
    as a .claude write; the file just lands at .github/workflows/<name>.yml).

      op=list  → the ci surface: the scaffold act (outbound write) + the inbound boundary (mention/event
                 have NO company op — the CI provider drives @claude; absence-of-op IS the boundary).
      op=get   → read an existing workflow file at .github/workflows/<name>.yml (direct read via the
                 config_writer /read — honest absence when it does not exist).
      op=act   → act=scaffold: WRITE a workflow YAML file (`name` + `body`) under .github/workflows/ in
                 `cwd` via the R3 service. Consent-gated (a workflow file can drive `claude -p` runs);
                 sole-operator consent-not-lockdown (no consent → pending-proposal, never a denial).

    `run=False` returns the planned write (the unit-test / preview path) without touching disk."""
    _require_op("dev.ci", op)
    repo = cwd.strip() or _REPO_ROOT
    if op == "list":
        return {"op": "list", "resource": "dev.ci", "rail": "R3",
                "writes": ["scaffold"],
                "inbound_boundary": ["mention", "event"],
                "note": "scaffold WRITES .github/workflows/<name>.yml (an R3 file write — same primitive "
                        "as a .claude write). mention/event are direction:inbound — the CI provider "
                        "drives @claude; the company exposes NO op for them (absence IS the boundary)."}
    if op == "get":
        nm = _safe_ci_name(name)
        path = os.path.join(repo, _CI_WF_DIR, nm + ".yml")
        exists = os.path.isfile(path)
        out = {"op": "get", "resource": "dev.ci", "rail": "direct-read", "act": "read",
               "name": nm, "path": path, "exists": exists}
        if exists:
            out["content"] = open(path, encoding="utf-8").read()
        else:
            out["content"] = None
            out["note"] = "no such workflow file yet — scaffold creates it (honest absence, not a default)."
        return out
    # op == act — scaffold a workflow file
    if act != "scaffold":
        raise ValueError(
            f"dev.ci op=act: act={act!r} unknown — the only outbound act is 'scaffold' (write a "
            f"workflow YAML). mention/event are inbound (CI-provider-driven, no company op).")
    nm = _safe_ci_name(name)
    if not isinstance(body, str) or not body.strip():
        raise ValueError(
            "dev.ci scaffold needs a non-empty `body` — the workflow YAML to write to "
            ".github/workflows/<name>.yml (e.g. an `on:`/`jobs:` block that invokes the claude action).")
    rel = os.path.join(_CI_WF_DIR, nm + ".yml")
    cw_body = {"act": "dev.ci:scaffold", "rel_path": rel, "cwd": repo, "body": body,
               "consent": bool(consent), "run": run}
    # NEEDED-ARM (reported to Wire/foundation): the R3 config_writer's `/write` is keyed to `.claude`
    # config_targets ONLY (scope-validated against the .claude roots) — it has NO generic repo-relative
    # file-write for the .github/workflows root. CI scaffold is "the same R3 primitive as a config-file
    # write" (§4) but on a DIFFERENT root, so it requires a NEW config_writer arm: POST /ci-scaffold
    # {act:"dev.ci:scaffold", rel_path, cwd, body, consent, run} that applies the realpath+commonpath
    # containment wall for <cwd>/.github/workflows/ (the second wall on top of _safe_ci_name here),
    # the config-write consent beat (a workflow YAML can drive `claude -p` runs -> dangerous), atomic+
    # backup write, and re-read verification. This handler BUILDS the request faithfully and fails LOUD
    # (no silent no-op) until that arm lands — honest `building`, never green-painted. live-verify
    # pending (lead): a REAL workflow-file write proven by re-read is the lead's slice once the arm exists.
    out = _cw_post("/ci-scaffold", cw_body)
    return {**out, "op": "act", "resource": "dev.ci", "rail": "R3", "act": "scaffold", "name": nm,
            "rel_path": rel}


# ─────────────────────────── dev.code_intel (CC-16) — R1-prime in-session LSP ───────────────────
# The structural truth (§1.1): a supervised session is --allowedTools mcp__company — NO LSP. So code-intel
# needs the WIDER R1-prime bridge-session spawn, and the reply rides back as PROSE on the turn stream:
# liveness:stream, NO typed return_shape (the grounded-chain law forbids binding a UI to model narration
# as data). The handler builds a bridge-session SPAWN INTENT receipt; the SUPERVISOR (sole launcher,
# spawn_bridge_session, operator_consent-gated) acts. The handler NEVER spawns.

def _r1prime_intent(suite, key: str, *, act: str, target: str, params: dict,
                    consent: bool) -> dict:
    """Build the R1-prime bridge-session spawn INTENT for an in-session capability act (code-intel /
    computer-use). REFUSES-LOUD a host/rail-boundary act (browser/computer on this headless WSL `-p`
    rail) BEFORE proposing a spawn — the boundary is explicit, never an intent that can never bind (§5.4).
    Returns a receipt naming the consent gate + the watch cursor (the prose result rides the turn stream).
    The handler does NOT call spawn_bridge_session — that is the supervisor's (the floor); this APPENDS
    the intent + names the consequence path."""
    row = SC.capability_for(key)                    # raises KeyError on unknown key (registry-is-truth)
    caveats = SC.act_caveats(key, act)              # raises ValueError on an act the capability doesn't model
    if caveats["not_wsl"]:
        raise ValueError(
            f"{key} act={act!r}: this is a HOST/RAIL BOUNDARY — {row['teach']} It cannot bind to this "
            f"headless `-p`/WSL2 rail (beta={caveats['beta']}, not_wsl=True). Refused LOUD, never "
            f"green-painted: it stays needs-tim/planned (§5.4). web-fetch/web-search ARE grantable here.")
    # the wider tools this capability needs beyond mcp__company (the requires_tool_grant surface, §5.4).
    grant = SC.requires_tool_grant(key)
    capability = "lsp" if key == "dev.code_intel" else "web"   # the bridge-session capability name (§ supervisor map)
    # write the durable intent (the store append — the session_post precedent; a service acts on it).
    instruction = _compose_in_session_instruction(key, act, target, params)
    cas = suite.store.put_content(instruction)
    watch_since = _event_tail_seq(suite)
    rec = {"kind": "dev_bridge.intent", "capability": key, "act": act, "rail": "R1-prime",
           "bridge_capability": capability, "requires_tool_grant": list(grant),
           "target": target, "cas": cas, "operator_consent": bool(consent),
           "liveness": "stream", "return_shape": None, "ts": _now(),
           "summary": f"{key}:{act} in-session (R1-prime bridge-session) — prose result on the turn stream"}
    posted = suite.store.append_event(rec)
    return {"op": "act", "resource": key, "rail": "R1-prime", "act": act, "target": target,
            "intent_seq": posted["seq"], "intent": cas, "bridge_capability": capability,
            "requires_tool_grant": list(grant), "liveness": "stream", "return_shape": None,
            "operator_consent": bool(consent),
            "watch": {"stream": "events", "since": watch_since},
            "consequence": ("the SUPERVISOR (sole launcher) spawns the R1-prime bridge-session "
                            "(spawn_bridge_session, operator_consent-gated) and runs the in-session "
                            "act; the result rides back as PROSE on the turn stream — watch "
                            "agent_sessions.turn after this seq. NO typed return_shape (the prose IS "
                            "the carrier; the grounded-chain law forbids binding to narration as data)."),
            "consent_note": ("sole-operator consent-not-lockdown: a wider in-session spawn is "
                             "consent-gated, NEVER locked — pass consent=true (the operator-vantage "
                             "beat). Without it the supervisor returns a pending-proposal, not a denial."),
            "live_verify": "live-verify pending (lead): a REAL bridge-session prose round-trip is the "
                           "build lead's slice — this handler builds the intent, never spawns."}


def _compose_in_session_instruction(key: str, act: str, target: str, params: dict) -> str:
    """The natural-language instruction the bridge-session runs (the in-session capability has no typed
    API — it is the model driving the native LSP/web tool). Plain, grounded; the supervisor injects it."""
    if key == "dev.code_intel":
        extra = f" with {params}" if params else ""
        return (f"Use the LSP code-intelligence tool to perform `{act}` for: {target}{extra}. "
                f"Report the result (symbols / locations / diagnostics) as prose.")
    extra = f" {params}" if params else ""
    return (f"Use the {act} capability for: {target}{extra}. Report what you find as prose.")


def _event_tail_seq(suite) -> int:
    """The current event-log tail seq (the watch cursor's `since` — consequences appear AFTER it)."""
    try:
        evs = suite.store.events_since(-1)
        return evs[-1].get("seq", -1) if evs else -1
    except Exception:
        return -1


def code_intel(suite, op, *, act: str = "", target: str = "", params=None,
               consent: bool = False, **_ignore) -> dict:
    """dev.code_intel (CC-16) — in-session LSP navigation (R1-prime). The native LSP tool runs IN-SESSION
    (a supervised session is mcp__company-only, so this needs the WIDER bridge-session spawn); the result
    is assistant PROSE on the turn stream — liveness:stream, NO typed return_shape (§1.1, honest).

      op=list  → the LSP acts (definition/references/hover/document-symbols/workspace-symbol/
                 implementations/call-hierarchy/diagnostics) + the rail truth (R1-prime, prose result).
      op=get   → same surface as list for a chosen act (the per-act caveats + the tool grant it needs).
      op=act   → build the R1-prime bridge-session spawn INTENT for `act` over `target` (a symbol / file /
                 position). Returns a receipt + watch cursor; the SUPERVISOR runs it (consent-gated).

    `target` is what to navigate (a symbol name, file path, or position). `consent` rides to the
    spawn-consent beat (sole-operator: no consent → pending-proposal). This handler NEVER spawns."""
    _require_op("dev.code_intel", op)
    row = SC.capability_for("dev.code_intel")
    acts = sorted(row["acts"])
    if op in ("list", "get"):
        surface = {"op": op, "resource": "dev.code_intel", "rail": "R1-prime", "acts": acts,
                   "liveness": "stream", "return_shape": None,
                   "requires_tool_grant": list(SC.requires_tool_grant("dev.code_intel")),
                   "note": row["teach"]}
        if op == "get" and act:
            if act not in row["acts"]:
                raise ValueError(f"dev.code_intel: act={act!r} unknown — acts: {acts}.")
            surface["act"] = act
            surface["caveats"] = SC.act_caveats("dev.code_intel", act)
        return surface
    # op == act
    if act not in row["acts"]:
        raise ValueError(
            f"dev.code_intel op=act: act={act!r} unknown — LSP acts: {acts}. Each runs the native LSP "
            f"tool in-session (R1-prime); the result is prose on the turn stream.")
    if not isinstance(target, str) or not target.strip():
        raise ValueError(
            f"dev.code_intel {act}: `target` is required — what to navigate (a symbol name, a file path, "
            f"or a position). The in-session LSP tool needs something to look up.")
    return _r1prime_intent(suite, "dev.code_intel", act=act, target=target.strip(),
                           params=dict(params or {}), consent=consent)


# ─────────────────────────── dev.computer_use (CC-17) — R1-prime in-session web/browser/computer ──────
# web-fetch/web-search are -p-grantable session tools (WebFetch/WebSearch) → R1-prime bridge-session.
# browser (Claude-in-Chrome) is beta + NOT-WSL; computer is macOS+interactive-only → host/rail BOUNDARIES
# refused-loud on this rail (§5.4). The handler surfaces the boundary, never silently fails or green-paints.

def computer_use(suite, op, *, act: str = "", target: str = "", params=None,
                 consent: bool = False, **_ignore) -> dict:
    """dev.computer_use (CC-17) — in-session web/browser/computer access (R1-prime). web-fetch/web-search
    are -p-grantable session tools; browser (Claude-in-Chrome, beta) and computer (macOS+interactive) are
    HOST/RAIL boundaries that REFUSE-LOUD on this headless WSL `-p` rail (§5.4) — never green-painted.

      op=list  → the acts (web-fetch/web-search grantable here; browser/computer host-bounded) + each
                 act's caveats (beta/not_wsl), so the boundary is visible BEFORE you try.
      op=get   → the surface for a chosen act incl. its caveats.
      op=act   → act ∈ {web-fetch, web-search}: build the R1-prime spawn intent (prose result, watch
                 cursor). act ∈ {browser, computer}: REFUSED LOUD (host/rail boundary — stays needs-tim).

    Result rides as PROSE — liveness:stream, NO return_shape. `consent` rides to the spawn beat."""
    _require_op("dev.computer_use", op)
    row = SC.capability_for("dev.computer_use")
    acts = sorted(row["acts"])
    if op in ("list", "get"):
        surface = {"op": op, "resource": "dev.computer_use", "rail": "R1-prime", "acts": acts,
                   "liveness": "stream", "return_shape": None,
                   "requires_tool_grant": list(SC.requires_tool_grant("dev.computer_use")),
                   "caveats": {a: SC.act_caveats("dev.computer_use", a) for a in row["acts"]},
                   "note": row["teach"]}
        if op == "get" and act:
            if act not in row["acts"]:
                raise ValueError(f"dev.computer_use: act={act!r} unknown — acts: {acts}.")
            surface["act"] = act
        return surface
    # op == act
    if act not in row["acts"]:
        raise ValueError(
            f"dev.computer_use op=act: act={act!r} unknown — acts: {acts}. web-fetch/web-search are "
            f"grantable on this rail; browser/computer are host/rail boundaries.")
    if not isinstance(target, str) or not target.strip():
        raise ValueError(
            f"dev.computer_use {act}: `target` is required — the URL / query / instruction to act on.")
    # _r1prime_intent applies the not_wsl boundary refusal (browser/computer) — loud, before any intent.
    return _r1prime_intent(suite, "dev.computer_use", act=act, target=target.strip(),
                           params=dict(params or {}), consent=consent)


# ─────────────────────────── dev.code_review (CC-19) — R2 headless wire job ───────────────────
# Code-review's act runs a headless `claude -p` review (the Atlas path: `/code-review` local diff review;
# `claude -p "Start a security review"`; managed GitHub Code Review for PRs). This is RAIL R2 (the wire,
# implement.py), NOT the supervisor mailbox (Critique C: only deliver/wake/consult ride R1). The handler
# WRITES A WIRE-JOB INTENT (the session_post precedent — a durable store append) and returns a job-id +
# watch cursor; the operator-only /api/resolve seam + the wire-loop dispatch it. The handler NEVER spawns
# `claude -p` and NEVER calls implement.launch (the floor — §3.1).

_REVIEW_ACTS = {
    "review-local": "Review the working-tree diff for correctness bugs and quality issues (the "
                    "/code-review path); report findings.",
    "security-review-local": "Perform a security review of the working-tree diff (the /security-review "
                             "path); report vulnerabilities.",
    "review-pr": "Review the pull request for logic errors, security issues, and regressions (the "
                 "managed GitHub Code Review path); report findings.",
}


def code_review(suite, op, *, act: str = "", target: str = "", cwd: str = "",
                consent: bool = False, **_ignore) -> dict:
    """dev.code_review (CC-19) — AI-driven code review via a HEADLESS `claude -p` job (RAIL R2, the wire).
    NOT the supervisor mailbox (only deliver/wake/consult ride R1). The handler writes a WIRE-JOB INTENT
    and returns a job-id + watch cursor; the operator-only /api/resolve seam + the wire-loop dispatch the
    `claude -p` review. The handler NEVER spawns and NEVER calls implement.launch (the floor).

      op=list  → the review acts (review-local / security-review-local / review-pr) + the rail (R2).
      op=get   → the pending/recent review jobs this handler has surfaced (a fold over its own intent
                 events — honest empty when none).
      op=act   → act ∈ {review-local, security-review-local, review-pr}: append a wire-job intent
                 (the instruction + target) and return {job, watch}. The CONSEQUENCE rides the wire's
                 dispatch events (events.watch) — completion = the review job's terminal event, never
                 a response body (the async-write proof shape, §3.3/§8).

    `target` is the diff/PR scope (a branch, a PR number/url, or empty = the working tree). `consent`
    rides through — the actual dispatch stays on the operator-only /api/resolve seam (the R2 gate)."""
    _require_op("dev.code_review", op)
    if op == "list":
        return {"op": "list", "resource": "dev.code_review", "rail": "R2", "acts": sorted(_REVIEW_ACTS),
                "note": "each act is a headless `claude -p` review JOB on the wire (implement.py), "
                        "dispatched behind the operator-only /api/resolve seam — NOT the supervisor "
                        "mailbox. op=act returns a job-id + watch cursor; the result rides dispatch events."}
    if op == "get":
        evs = [e for e in suite.store.events_since(-1) if e.get("kind") == "code_review.job"]
        jobs = [{"job": e.get("job"), "act": e.get("act"), "target": e.get("target"),
                 "seq": e.get("seq"), "ts": e.get("ts"), "status": e.get("status", "surfaced")}
                for e in evs]
        return {"op": "get", "resource": "dev.code_review", "rail": "R2", "total": len(jobs),
                "jobs": jobs,
                "note": "review jobs this handler surfaced (a fold over its own code_review.job intents). "
                        "Empty is honest — no review requested yet."}
    # op == act — append a wire-job intent
    if act not in _REVIEW_ACTS:
        raise ValueError(
            f"dev.code_review op=act: act={act!r} unknown — review acts: {sorted(_REVIEW_ACTS)}. Each "
            f"is a headless `claude -p` review job on the R2 wire.")
    repo = cwd.strip() or _REPO_ROOT
    scope = target.strip() or "the working-tree diff"
    instruction = f"{_REVIEW_ACTS[act]} Scope: {scope}. Repo: {repo}."
    cas = suite.store.put_content(instruction)
    watch_since = _event_tail_seq(suite)
    job_id = "crev-" + cas[:12]
    rec = {"kind": "code_review.job", "job": job_id, "act": act, "rail": "R2", "target": scope,
           "cwd": repo, "cas": cas, "operator_consent": bool(consent), "status": "surfaced",
           "ts": _now(),
           "summary": f"code-review job {job_id}: {act} over {scope} (R2 headless wire job)"}
    posted = suite.store.append_event(rec)
    return {"op": "act", "resource": "dev.code_review", "rail": "R2", "act": act, "target": scope,
            "job": job_id, "job_seq": posted["seq"], "instruction": cas,
            "watch": {"stream": "events", "since": watch_since},
            "consequence": ("the wire (implement.py) dispatches this as a headless `claude -p` review "
                            "behind the operator-only /api/resolve seam; the review FINDINGS ride the "
                            "dispatch events — watch events.watch after this seq for the job's terminal "
                            "event. Completion is the declared event, never a response body (§8)."),
            "consent_note": ("R2 dispatch stays on the operator-only /api/resolve gate (the wire's "
                             "existing floor); this op only SURFACES the job intent (consent-not-lockdown)."),
            "live_verify": "live-verify pending (lead): a REAL `claude -p` review round-trip + its "
                           "consequence events are the build lead's slice — this handler builds the job."}


# ─────────────────────────── wire the handlers onto the pre-declared HANDLERS slots ───────────────────
# register_handler swaps each stub → the real fn + flips .built True. A lane WIRES a declared handler;
# it never invents a key (the §3.2 law — fails loud on an undeclared key).
register_handler("dev.git", git)
register_handler("dev.ci", ci)
register_handler("dev.code_intel", code_intel)
register_handler("dev.computer_use", computer_use)
register_handler("dev.code_review", code_review)
