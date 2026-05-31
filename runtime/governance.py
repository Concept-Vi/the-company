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
    # SURFACE — meaningful but recoverable (proceeds on default + deadline)
    "promote": SURFACE, "spend": SURFACE,
    # CONFIRM — irreversible / expensive / external
    "destructive": CONFIRM, "code_build": CONFIRM, "register_type": CONFIRM,
    "external": CONFIRM, "source_data": CONFIRM, "frozen_contract": CONFIRM,
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

    def surface(self, action_class: str, payload: dict, default: str, resolved=None) -> str:
        self._n += 1
        sid = f"s{self._n}-{action_class}"
        self.store.save_surfaced({"id": sid, "action": action_class, "payload": payload,
                                  "default": default, "resolved": resolved})
        return sid

    def list(self) -> list:
        return self.store.list_surfaced()

    def get(self, sid: str) -> dict | None:
        return self.store.get_surfaced(sid)

    def resolve(self, sid: str, choice: str) -> None:
        """OPERATOR-only: approve/reject a surfaced decision. (Must NOT be reachable by the
        agent it gates — kept off the MCP face; only the UI/operator channel calls this.)"""
        d = self.store.get_surfaced(sid)
        if not d:
            raise KeyError(sid)
        d["resolved"] = choice
        self.store.save_surfaced(d)

    def is_approved(self, sid: str) -> bool:
        d = self.store.get_surfaced(sid)
        return bool(d and d.get("resolved") == "approve")
