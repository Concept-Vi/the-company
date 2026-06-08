"""runtime/governance.py — the act-unwatched policy + surfaced-decision gate (S7/D4/D7).

Per-action-class posture on the axes reversibility · cost · externality:
  reversible+cheap+internal -> AUTO; meaningful-but-recoverable -> SURFACE (default+deadline);
  irreversible/expensive/external -> CONFIRM. Some classes are locked-to-CONFIRM forever
  (Tim: real source data, external publishing). See decisions/D4 + D7.
"""
from __future__ import annotations

AUTO, SURFACE, CONFIRM = "auto", "surface", "confirm"

POLICY = {
    # AUTO — cheap, reversible, internal
    "inspect": AUTO, "compose": AUTO, "configure": AUTO, "run": AUTO, "write_own_layer": AUTO,
    # AUTO — the decision→implementation wire (Group W). AUTO here means auto-DISPATCH on the
    # operator's approve (no second gate BEFORE building) — it does NOT mean auto-CLOSE without review.
    # A DECLARED-SCOPE, reversible (git-committed, build-gated, scope-diffed) build is the ONE class the
    # wire may auto-dispatch: the operator's approve of the declared-scope build-intent IS the
    # authorization, so the dispatch proceeds without a second gate. The pre-dispatch gate keys on
    # posture==AUTO, so ONLY this class auto-runs; ANY CONFIRM/SURFACE/LOCKED declared class surfaces
    # for the operator instead (never auto-acts — a CONFIRM class like 'destructive' that is absent from
    # LOCKED can no longer slip through a LOCKED-membership check). After the build, EVERY implemented
    # result is SURFACED FOR REVIEW (a `decision.surfaced_for_review` event + a review inbox item) —
    # AI-operated is NOT review-free; `implemented` means "done AND surfaced for review", never a silent
    # terminal. The CLOSE routes through guard("code_build") (CONFIRM), so an unverified build can never
    # reach `implemented`, and the review item is ALWAYS surfaced in the same guarded close.
    "decision_build": AUTO,
    # SURFACE — meaningful but recoverable (proceeds on default + deadline)
    "promote": SURFACE, "spend": SURFACE,
    # CONFIRM — irreversible / expensive / external
    "destructive": CONFIRM, "code_build": CONFIRM, "register_type": CONFIRM,
    "external": CONFIRM, "source_data": CONFIRM, "frozen_contract": CONFIRM,
    # CONFIRM — UI self-mod + the review queue. They already routed to CONFIRM via the
    # unknown-class default (posture() → CONFIRM); declaring them here changes NO behavior,
    # it makes the intent explicit + single-source (G1). `review` = a surfaced item the
    # operator walks/decides; only Tim resolves it (no-bypass), so CONFIRM is its posture.
    "ui_panel": CONFIRM, "ui_extension": CONFIRM, "review": CONFIRM,
    # CONFIRM — AUTHORING (Concurrent Cognition C7.4/C7.5). `role_build` = an operator-authored
    # cognition ROLE (a roles/<id>.py file) written through the surface. It mirrors code_build/
    # ui_extension exactly: propose-not-apply, surfaced for the operator, applied ONLY on
    # `resolved=='approve'` (authorization READ from the inbox, never a caller flag). Declared here
    # so apply_role's guard("role_build", ...) is single-source + so it routes to apply_role (NOT the
    # generic apply_node) via apply_surfaced's distinct action branch — a role is NOT a node-type. The
    # role module is GATED (imported in a temp dir) before any write, so a bad approve can never brick
    # RoleRegistry.discover (the whole cognition layer). `role_delete` is its removal sibling.
    "role_build": CONFIRM, "role_delete": CONFIRM,
}
# never graduate to AUTO, no matter the earned trust (D4/D7 forever-confirm)
LOCKED = {"source_data", "external", "frozen_contract"}


class GovernanceError(RuntimeError):
    """Raised when a CONFIRM action is attempted without confirmation (fail loud)."""


def posture(action_class: str) -> str:
    return POLICY.get(action_class, CONFIRM)        # unknown class -> safest


def guard(action_class: str, do, *, confirmed: bool = False, inbox=None, payload: dict | None = None):
    """Run `do()` per policy. AUTO: run. SURFACE: run, record a surfaced note (default = proceed).
    CONFIRM: run only if `confirmed`; else surface a gate and raise (fail loud)."""
    p = posture(action_class)
    if p == AUTO:
        return do()
    if p == SURFACE:
        if inbox is not None:
            inbox.surface(action_class, payload or {}, default="proceed", resolved="proceed")
        return do()
    # CONFIRM
    if confirmed:
        return do()
    if inbox is not None:
        inbox.surface(action_class, payload or {}, default="reject", resolved=None)
    raise GovernanceError(f"action '{action_class}' requires confirmation (CONFIRM); surfaced for the operator")


class Inbox:
    """Surfaced decisions live in the store, so both faces (UI + MCP) see the same inbox."""
    def __init__(self, store):
        self.store = store
        self._n = 0

    def _next_index(self) -> int:
        """Next id index, computed from PERSISTED decisions (not just an in-memory counter) so a
        process restart can never reuse an id and overwrite an unresolved decision (gate integrity)."""
        import re
        mx = self._n
        for d in self.store.list_surfaced():
            m = re.match(r"s(\d+)-", d.get("id", ""))
            if m:
                mx = max(mx, int(m.group(1)))
        return mx + 1

    def surface(self, action_class: str, payload: dict, default: str, resolved=None,
                status: str | None = None, origin: str | None = None) -> str:
        self._n = self._next_index()
        sid = f"s{self._n}-{action_class}"
        rec = {"id": sid, "action": action_class, "payload": payload,
               "default": default, "resolved": resolved}
        # T3-HYGIENE (tag-at-source): the OPERATOR inbox was ~90% test/adversarial pollution because
        # test- and red-team-created surfaced items were indistinguishable from real ones, and the FE
        # filter pattern-matched titles (brittle, missed most). The DURABLE fix is a tag set AT CREATION:
        # when a run sets COMPANY_TEST_RUN, every item this surfaces carries `test_origin=True`, so the
        # inbox lanes / FE filter exclude it by a real field instead of a fragile title regex. A real
        # operator run never sets the flag, so real items are never tagged. Additive + optional: an
        # untagged item reads exactly as before. (Cross-lane: the TESTS lane / adversarial harness sets
        # COMPANY_TEST_RUN; the FE filters on `test_origin`; the verifier drives a clean operator run.)
        import os as _os
        if _os.environ.get("COMPANY_TEST_RUN"):
            rec["test_origin"] = True
        # SEPARATE lifecycle field (A): inbox→presented→responded→resolved|requeue. NEVER
        # overload `resolved` (inbox_lanes/now/is_approved key on `resolved is None`); the
        # status tracks the walk WITHOUT touching the live/escalation predicate. Additive +
        # optional, so every existing surfaced item (no status) reads exactly as before.
        if status is not None:
            rec["status"] = status
        if origin is not None:                       # responsive (came from a build need) | generative (an idea)
            rec["origin"] = origin
        self.store.save_surfaced(rec)
        return sid

    # --- the review queue (A): a review item is the SAME inbox, a new decision class ---
    # `implemented` (W4) is the code-written terminal of the decision→implementation wire: it lives
    # on the SEPARATE `status` lane (NOT the operator `resolved` field), so a build can close without
    # breaking operator-only resolve. set_status RAISES on an unknown value, so it MUST be listed here
    # before the wire can write it. The wire only writes it through a guard()ed close on the
    # verification verdict — an unverified build that reaches the close raises (W4).
    REVIEW_STATUSES = ("inbox", "presented", "responded", "resolved", "requeue", "implemented")

    def surface_review(self, item: dict, origin: str = "responsive") -> str:
        """Surface a `review` decision into the SAME inbox/surfaced store (no parallel queue).
        Carries a SEPARATE `status` (starts `inbox`) + `origin` (responsive|generative). `resolved`
        stays None so it lands in `live_escalations` until Tim resolves it — only `resolve_surfaced`
        ever writes `resolved`, so a presented/responded item is still a live escalation (A)."""
        if origin not in ("responsive", "generative"):
            raise ValueError(f"unknown review origin {origin!r} — responsive|generative")
        return self.surface("review", dict(item), default="reject",
                            resolved=None, status="inbox", origin=origin)

    def set_status(self, sid: str, status: str) -> None:
        """Advance a surfaced item's lifecycle status WITHOUT touching `resolved` (A). Fail loud
        on an unknown status or a missing item — never silently no-op."""
        if status not in self.REVIEW_STATUSES:
            raise ValueError(f"unknown review status {status!r} — one of {self.REVIEW_STATUSES}")
        # T1-RACE: serialize the whole get→mutate→save against every other surfaced writer (the
        # Suite's resolve/build_result writes, Inbox.resolve) so a status advance can't lose-update a
        # concurrently-written field (e.g. `resolved`). The store-level lock is the one both reach.
        with self.store.surfaced_lock():
            d = self.store.get_surfaced(sid)
            if not d:
                raise KeyError(sid)
            d["status"] = status
            self.store.save_surfaced(d)

    def list(self) -> list:
        return self.store.list_surfaced()

    def get(self, sid: str) -> dict | None:
        return self.store.get_surfaced(sid)

    def resolve(self, sid: str, choice: str, reason: str = "") -> None:
        """OPERATOR-only: approve/reject a surfaced decision. (Must NOT be reachable by the
        agent it gates — kept off the MCP face; only the UI/operator channel calls this.)
        `reason` captures the WHY — the trajectory that generalises, not just the endpoint (I1)."""
        # T1-RACE: serialize the whole get→mutate→save (resolved is the operator-only field; a
        # concurrent set_status must not lose-update it, nor it the status). Store-level lock.
        with self.store.surfaced_lock():
            d = self.store.get_surfaced(sid)
            if not d:
                raise KeyError(sid)
            d["resolved"] = choice
            if reason:
                d["reason"] = reason
            self.store.save_surfaced(d)

    def is_approved(self, sid: str) -> bool:
        d = self.store.get_surfaced(sid)
        return bool(d and d.get("resolved") == "approve")
