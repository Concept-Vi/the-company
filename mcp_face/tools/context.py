"""mcp_face/tools/context.py — the CONTEXT tool: live context-window read + compact (S-R10.1).

One consolidated `context` op-tool over runtime/context_ops.py. File-drop contract (pkgutil
auto-register, no server.py edit). MCP-DESIGN-PRINCIPLE: one parameterised tool, op selector.

## Ops (operate on a supervised-live session id)
  op="read"    — inject `/context` and return the usage breakdown (the on-demand context snapshot).
  op="compact" — inject `/compact` (optional `focus`) and wait for the compact_boundary marker;
                 the session re-inits with the summary, memory preserved. The consequential verb.
"""
from __future__ import annotations

from typing import Literal

OPS = ("read", "compact")


def register(mcp, suite):
    @mcp.tool()
    def context(op: Literal["read", "compact"], session: str = "", focus: str = "") -> dict:
        """LIVE CONTEXT-WINDOW ops on a supervised-live session (drives the in-session slash commands
        headlessly via the supervisor). Pick `op`:

          op="read"    — inject `/context`, return the usage breakdown (on-demand snapshot).
          op="compact" — inject `/compact` (optional `focus`), wait for the compact_boundary; the
                         session continues with a summary (memory preserved). Consequential verb.

        Required: `session` (the supervised-live session id; sessions(op='list') shows the fleet).
        """
        if not session:
            raise ValueError("context(...) requires `session` — the supervised-live session id "
                             "(sessions(op='list') shows the fleet).")
        from runtime.context_ops import read_context, compact_session, ContextOpError
        try:
            if op == "read":
                return read_context(session)
            if op == "compact":
                return compact_session(session, focus=focus)
        except ContextOpError as e:
            return {"op": op, "session": session, "ok": False, "error": str(e)}
        raise ValueError(f"context: unknown op {op!r} — one of {OPS}.")
