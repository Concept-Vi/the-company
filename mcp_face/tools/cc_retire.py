"""mcp_face/tools/cc_retire.py — RETIREMENT through the MCP (the reusable member/channel retire verb over
runtime/cc_retire.py). File-drop tool (auto-registers on the next MCP server start).

Make the wind-down HARVEST a repeatable verb: a member or a channel crystallizes its perspective/totality
into the ONE corpus (structured, attributed, linked, HONEST-state, coverage-checked) before it closes.

## Ops
  op="status"  — the coverage ledger for a channel's retirement: which members have crystallized a harvest,
                 which are missing (`channel` required). The fail-loud coverage proof before a close.
  op="member"  — MEMBER retire: crystallize a session's perspective. `session` + `claims`
                 (list of {text, status}; status ∈ verified|attempted-unverified|broken|abandoned — ENFORCED,
                 no self-certified 'done') + optional `summary`/`open_questions`/`dead_ends`. Ingests + links.
  op="channel" — CHANNEL retire: crystallize a channel's TOTALITY (members + harvests + attachments + board)
                 into one linked corpus record, coverage-checked. `channel` + `author_session` (+ optional
                 `summary`). `archive=true` (EXPLICIT) also archives the channel — default false (never auto).
"""
from __future__ import annotations

from typing import Literal

OPS = ("status", "member", "channel")


def register(mcp, suite):
    @mcp.tool()
    def cc_retire(op: Literal["status", "member", "channel"],
                  channel: str = "", session: str = "", author_session: str = "", summary: str = "",
                  claims: list | None = None, open_questions: list | None = None,
                  dead_ends: list | None = None, archive: bool = False) -> dict:
        """The reusable retirement verb — crystallize a member's perspective or a channel's totality into the
        corpus (honest-state-enforced, coverage-checked) before it winds down. See the module docstring."""
        from runtime import cc_retire as cr
        store = suite.store
        if op == "status":
            if not channel:
                raise ValueError("cc_retire(op='status') needs `channel`.")
            return {"op": "status", **cr.harvest_status(store, channel)}
        if op == "member":
            if not session or not claims:
                raise ValueError("cc_retire(op='member') needs `session` + `claims` (each {text, status}; "
                                 "status ∈ verified|attempted-unverified|broken|abandoned).")
            return {"op": "member", **cr.harvest_member(store, session, claims=claims, summary=summary,
                                                        open_questions=open_questions, dead_ends=dead_ends)}
        if op == "channel":
            if not channel or not author_session:
                raise ValueError("cc_retire(op='channel') needs `channel` + `author_session`.")
            return {"op": "channel", **cr.retire_channel(store, channel, author_session=author_session,
                                                        summary=summary, archive=archive)}
        raise ValueError(f"cc_retire: unknown op {op!r} — one of {OPS}.")
