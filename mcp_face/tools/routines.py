"""mcp_face/tools/routines.py — the ROUTINES tool (Session Fabric S-R9.1, the in-Company /fire arm).

One consolidated parameterised tool (`routines`) over the file-discovered routine registry
(runtime/routines.py) + the fire mechanism (runtime/routine_runner.py). File-drop contract: this
module is discovered by mcp_face/server.py's pkgutil loop and called as `.register(mcp, SUITE)` with
no server.py edit (mirrors introspection.py / sessions.py).

MCP DESIGN PRINCIPLE (mcp_face/AGENTS.md): one parameterised tool with an `op` selector — NEVER a
flat tool per operation. A new need is a new `op`.

## Ops
  op="list"  — every registered routine (id + label + cadence + prompt preview). The registry is
               fresh-discovered each call (a routines/<id>.py drop is picked up without restart).
  op="get"   — one routine's full record. Required: `id`.
  op="fire"  — FIRE a routine NOW through the session-supervisor (spawn → inject the prompt →
               capture the result → teardown). Required: `id`. Returns the run record
               {routine_id, claude_session_id, result, is_error, ...}. This spawns a REAL claude
               session — it is the consequential verb of this tool.
"""
from __future__ import annotations

from typing import Literal

OPS = ("list", "get", "fire")


def register(mcp, suite):
    """Register the `routines` tool. Called by mcp_face/server.py's pkgutil discovery loop —
    no server.py edit required (the file-drop contract)."""

    @mcp.tool()
    def routines(op: Literal["list", "get", "fire"], id: str = "") -> dict:
        """SCHEDULE/FIRE Claude-Code ROUTINES — named, repeatable tasks the Company drives through
        the session-supervisor (spawn a real session, inject the routine's prompt, capture the
        result). The local-driven equivalent of a cloud routine (reached by DRIVING A REAL SESSION,
        not by reproducing Anthropic's off-machine scheduler). Pick `op`:

          op="list" — every registered routine (drop a routines/<id>.py file to add one).
          op="get"  — one routine's full record (required: id).
          op="fire" — fire a routine NOW: spawn → inject → capture → teardown (required: id).
                      Returns the run record. Spawns a REAL session — the consequential verb.
        """
        from runtime.routines import routine_registry
        reg = routine_registry()

        if op == "list":
            return {"op": "list", "total": len(reg.ids()),
                    "routines": [{"id": r.id, "label": r.spec.get("label"),
                                  "cadence": r.cadence, "repeats": r.repeats,
                                  "prompt_preview": (r.prompt[:120] + ("…" if len(r.prompt) > 120 else ""))}
                                 for r in (reg[i] for i in reg.ids())]}

        if op == "get":
            if not id:
                raise ValueError("routines(op='get') requires `id` (routines(op='list') shows them).")
            if id not in reg:
                raise ValueError(f"no routine {id!r} — registered: {reg.ids()}. "
                                 f"Add routines/{id}.py (a ROUTINE dict). Fail loud.")
            return {"op": "get", "routine": reg[id].record()}

        if op == "fire":
            if not id:
                raise ValueError("routines(op='fire') requires `id` (routines(op='list') shows them).")
            if id not in reg:
                raise ValueError(f"no routine {id!r} — registered: {reg.ids()}. Fail loud.")
            from runtime.routine_runner import fire, RoutineFireError
            try:
                run = fire(reg[id])
            except RoutineFireError as e:
                # surface the teaching error as a structured result (no silent failure)
                return {"op": "fire", "id": id, "fired": False, "error": str(e)}
            return {"op": "fire", "id": id, "fired": True, "run": run}

        raise ValueError(f"routines: unknown op {op!r} — one of {OPS}.")
