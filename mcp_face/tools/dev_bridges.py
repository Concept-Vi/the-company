"""mcp_face/tools/dev_bridges.py — the ④ DEV-BRIDGES agent face (Capability Fabric §3.3, lane L-④-dev).

RESOURCE-KEYED tools (matches the CONVENTIONS named-act grain — A2/E1), glob-auto-registered by
mcp_face/server.py (pkgutil — ZERO edit to server.py, §1.3). Each tool is THIN: validate op ∈ OPS,
then DELEGATE to the SAME handler the bridge route calls — `runtime.capability_handlers.HANDLERS[key].fn`
(DRY: one handler, two faces, drift-tested byte-identical, §3.3). The face NEVER reimplements the
handler and NEVER spawns/shells (the floor — §1.2).

FIVE resource tools, one per ④ resource (the §4 mapping):
  dev_git()          → dev.git          (R3 structured git/gh — sha/exit)
  dev_code_intel()   → dev.code_intel   (R1-prime in-session LSP — prose result, NO return_shape)
  dev_computer_use() → dev.computer_use (R1-prime web/browser/computer — browser/computer host-bounded)
  dev_code_review()  → dev.code_review  (R2 headless claude -p review — wire job + watch cursor)
  dev_ci()           → dev.ci           (R3 ci scaffold file write + reads)

Each exports an `OPS` constant (CONTRACT-FORMAT §9.2: every consolidated MCP tool module exports OPS;
extract_reality.py fails loud on a tool module without one). The uniform op set is list/get/act — a new
need is a new ACT on the resource (act=…), never a new flat tool. ToolAnnotations come from the HANDLERS
`readonly` flag (the honest contracts model: readonly∧destructive refused at construction); ④ writes are
NOT readonly (every dev handler is a write rail).

SOLE-OPERATOR FLOOR (Tim's steer): the dangerous ④ capabilities are ENABLED — git/gh writes, in-session
bash via R1-prime, computer-use (where the host allows), CI-file writes. The gate is a CONSENT BEAT
(consent= passed through to the sanctioned actor) + git-revert backstop, NEVER a multi-user auth wall.
A cold MCP agent reaches the READ surface and may build a write intent/job, but the consequential act is
operator-confirmed (the consent beat lives in the actor — config_writer / spawn_bridge_session /
/api/resolve). NOTHING here is green-painted: R1-prime/R2 ops return an intent/job receipt + a watch
cursor; the rail's own executor round-trip is the build lead's `live-verify pending` slice.
"""
from typing import Literal
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from contracts.tools import ToolAnnotations as CompanyToolAnnotations   # the honest contracts model
from mcp.types import ToolAnnotations as SDKToolAnnotations             # the SDK's hint carrier
from runtime import capability_handlers as ch

# the uniform op set for EVERY ④ resource tool (CONTRACT-FORMAT §9.2 — the machine inventory). A new
# need is a new ACT (act=…) on one of these ops, never a new flat tool (the sessions.py law).
OPS = ("list", "get", "act")


def _to_sdk_annotations(ann: CompanyToolAnnotations, title: str) -> SDKToolAnnotations:
    """contracts.ToolAnnotations → SDK hints (the sessions.py F10.1 precedent). The contracts model's own
    gate (readonly∧destructive raises) bites BEFORE registration, so an incoherent annotation can never
    reach a client."""
    return SDKToolAnnotations(
        title=title, readOnlyHint=ann.readonly, destructiveHint=ann.destructive,
        idempotentHint=ann.idempotent, openWorldHint=False)


def _annotations_for(key: str, title: str) -> SDKToolAnnotations:
    """Derive the tool annotations from the HANDLERS slot (registry-is-truth — the readonly flag is the
    handler's, not re-asserted here). Every ④ handler is a WRITE rail → readonly=False, destructive=False
    (writes are consequential but not data-destroying; git-revert is the backstop)."""
    h = ch.get(key)
    return _to_sdk_annotations(
        CompanyToolAnnotations(readonly=h.readonly, destructive=False, idempotent=False), title)


def _call(key: str, op: str, suite, **params) -> dict:
    """The DRY delegation — the MCP op and the bridge route call THIS, identically (§3.3). load_all()
    guarantees the dev family is wired before dispatch (idempotent re-import). The handler validates op
    + act and fails LOUD; the face adds nothing but the op multiplex + annotations."""
    ch.load_all()
    return ch.get(key).fn(suite, op, **params)


def register(mcp, suite):
    # ── dev.git (CC-06) — R3 structured git/gh ───────────────────────────────────────────────────────
    @mcp.tool(annotations=_annotations_for("dev.git", "Dev bridges — git (structured status/log/commit/pr/worktree)"))
    def dev_git(op: Literal["list", "get", "act"], act: str = "", cwd: str = "",
                args: list | None = None, consent: bool = False, run: bool = True) -> dict:
        """dev.git (CC-06) — STRUCTURED git/gh in a repo cwd (RAIL R3, the config_writer service; sha/exit,
        NOT R1-prime prose). Reads are ungated; writes ride the config_writer git-write CONSENT beat
        (sole-operator consent-not-lockdown — a write without `consent` returns a pending-proposal, never
        a denial). `op`:
          list → the available read acts (status/log/worktrees) + write acts.
          get  → a git READ: `act` ∈ {status, log, worktrees}; `args` are extra argv (e.g. log range).
          act  → a git WRITE: `act` ∈ {commit, open-pr, rebase, worktree-create, worktree-remove};
                 `args` are extra argv (e.g. ["-m","msg"] for commit). `cwd` = the repo (defaults to the
                 company repo). `run=False` returns the argv without executing (preview / injection-proof).
        The structured-sha path: commit returns the resulting HEAD sha. This face NEVER shells git — the
        sanctioned R3 service does (the floor)."""
        return _call("dev.git", op, suite, act=act, cwd=cwd, args=args, consent=consent, run=run)

    # ── dev.code_intel (CC-16) — R1-prime in-session LSP ───────────────────────────────────────────────
    @mcp.tool(annotations=_annotations_for("dev.code_intel", "Dev bridges — code intelligence (in-session LSP)"))
    def dev_code_intel(op: Literal["list", "get", "act"], act: str = "", target: str = "",
                       params: dict | None = None, consent: bool = False) -> dict:
        """dev.code_intel (CC-16) — native LSP navigation IN-SESSION (RAIL R1-prime). A supervised session
        is mcp__company-only (no LSP), so this needs the WIDER bridge-session spawn; the result is
        assistant PROSE on the turn stream — liveness:stream, NO typed return_shape (§1.1, honest — the
        grounded-chain law forbids binding to model narration as data). `op`:
          list → the LSP acts (definition/references/hover/document-symbols/workspace-symbol/
                 implementations/call-hierarchy/diagnostics) + the rail truth.
          get  → the surface for one `act` (its caveats + the tools the R1-prime spawn must grant).
          act  → build the bridge-session spawn INTENT for `act` over `target` (a symbol/file/position);
                 returns a receipt + watch cursor. The SUPERVISOR (sole launcher, operator_consent-gated)
                 runs it; watch agent_sessions.turn for the prose result.
        `consent` rides to the spawn-consent beat (no consent → pending-proposal). This face NEVER spawns.
        live-verify pending (lead): a REAL prose round-trip is the build lead's slice."""
        return _call("dev.code_intel", op, suite, act=act, target=target, params=params, consent=consent)

    # ── dev.computer_use (CC-17) — R1-prime web/browser/computer ───────────────────────────────────────
    @mcp.tool(annotations=_annotations_for("dev.computer_use", "Dev bridges — computer use (in-session web/browser/computer)"))
    def dev_computer_use(op: Literal["list", "get", "act"], act: str = "", target: str = "",
                         params: dict | None = None, consent: bool = False) -> dict:
        """dev.computer_use (CC-17) — in-session web/browser/computer access (RAIL R1-prime). web-fetch/
        web-search are -p-grantable session tools (WebFetch/WebSearch); browser (Claude-in-Chrome, beta)
        and computer (macOS+interactive) are HOST/RAIL boundaries that REFUSE-LOUD on this headless WSL
        `-p` rail — never green-painted (§5.4). `op`:
          list → the acts + each act's caveats (beta/not_wsl) so the boundary is visible before you try.
          get  → the surface for one `act`.
          act  → act ∈ {web-fetch, web-search}: build the R1-prime spawn intent (prose result + watch
                 cursor); act ∈ {browser, computer}: REFUSED LOUD (host/rail boundary, stays needs-tim).
        `target` = the URL/query/instruction. `consent` rides to the spawn beat. Result is prose —
        liveness:stream, NO return_shape. This face NEVER spawns (the floor)."""
        return _call("dev.computer_use", op, suite, act=act, target=target, params=params, consent=consent)

    # ── dev.code_review (CC-19) — R2 headless wire job ─────────────────────────────────────────────────
    @mcp.tool(annotations=_annotations_for("dev.code_review", "Dev bridges — code review (headless claude -p job)"))
    def dev_code_review(op: Literal["list", "get", "act"], act: str = "", target: str = "",
                        cwd: str = "", consent: bool = False) -> dict:
        """dev.code_review (CC-19) — AI code review via a HEADLESS `claude -p` job (RAIL R2, the wire —
        NOT the supervisor mailbox; only deliver/wake/consult ride R1). This face writes a WIRE-JOB INTENT
        and returns a job-id + watch cursor; the operator-only /api/resolve seam + the wire-loop dispatch
        the review. `op`:
          list → the review acts (review-local / security-review-local / review-pr) + the rail.
          get  → the pending/recent review jobs this resource surfaced (a fold over its own intents).
          act  → act ∈ {review-local, security-review-local, review-pr}: append a wire-job intent over
                 `target` (a branch / PR number-url / empty=working tree) and return {job, watch}. The
                 review FINDINGS ride the wire's dispatch events — watch events after the returned seq;
                 completion is the declared terminal event, never a response body (§8 async proof shape).
        `cwd` = the repo. This face NEVER spawns `claude -p` and NEVER calls implement.launch (the floor).
        live-verify pending (lead): a REAL review round-trip + its consequence events are the lead's slice."""
        return _call("dev.code_review", op, suite, act=act, target=target, cwd=cwd, consent=consent)

    # ── dev.ci (CC-30) — R3 ci scaffold file write + reads ─────────────────────────────────────────────
    @mcp.tool(annotations=_annotations_for("dev.ci", "Dev bridges — CI/CD (scaffold workflow file + reads)"))
    def dev_ci(op: Literal["list", "get", "act"], act: str = "", name: str = "", body: str = "",
               cwd: str = "", consent: bool = False, run: bool = True) -> dict:
        """dev.ci (CC-30) — CI/CD scaffolding as a config-file write (the §4 unification: the SAME R3
        primitive as a .claude write; the file just lands at .github/workflows/<name>.yml). `op`:
          list → the ci surface: the scaffold act (outbound write) + the inbound boundary (mention/event
                 have NO company op — the CI provider drives @claude; absence-of-op IS the boundary).
          get  → read an existing .github/workflows/<name>.yml (honest absence when it does not exist).
          act  → act=scaffold: WRITE a workflow YAML (`name` + `body`) under .github/workflows/ in `cwd`
                 via the R3 service. Consent-gated (a workflow file can drive `claude -p` runs); a write
                 without `consent` returns a pending-proposal (consent-not-lockdown). `run=False` previews.
        This face NEVER writes the file — the sanctioned R3 service does. NOTE (honest): the R3 actor's
        generic .github/workflows write arm (POST /ci-scaffold) is a NEEDED foundation arm reported to
        the Wire; until it lands, scaffold fails LOUD (no silent no-op) — honest `building`."""
        return _call("dev.ci", op, suite, act=act, name=name, body=body, cwd=cwd,
                     consent=consent, run=run)

    return dev_git, dev_code_intel, dev_computer_use, dev_code_review, dev_ci
