"""mcp_face/tools/cc_gate.py — per-step GATE / ABORT / REWIND through the MCP (agent surface over
runtime/cc_gate.py). File-drop tool (pkgutil auto-register on the next MCP server start). Heart R15.

An OBSERVER on the native mechanism (NOT a hot-path edit, NOT a parallel render): the PAUSE rides the
native blocks_execution declaration; ABORT = supervisor /interrupt+/teardown (no-orphan); REWIND =
materialize_at_point (native fork transform). The step is an OPAQUE address (session://<sid>/step/<id>),
stored verbatim; `session` is the separate abort/rewind handle.

## Ops
  op="gate"   — register a gate on a declared step. Req: `step_address` (opaque), `session`. Opt `note`,`by`.
  op="resume" — record a gated step resumed (native continuation). Req: `gate` (id or step_address).
  op="abort"  — interrupt + teardown the session (no-orphan). Req: `gate`.
  op="rewind" — materialize the session's transcript at `at` (native fork). Req: `gate`, `source`, `at`.
  op="list"   — gate records; optional `state` / `session` filter.
  op="get"    — one gate (`gate` = id or step_address).
"""
from __future__ import annotations

from typing import Literal

OPS = ("gate", "resume", "abort", "rewind", "list", "get")


def register(mcp, suite):
    @mcp.tool()
    def cc_gate(op: Literal["gate", "resume", "abort", "rewind", "list", "get"],
                step_address: str = "", session: str = "", gate: str = "", source: str = "",
                at: str = "", state: str = "", by: str = "", note: str = "") -> dict:
        """Per-step GATE/ABORT/REWIND, observer on the native mechanism (Heart R15). Pick `op`:

          op="gate"   — `step_address` (opaque session://<sid>/step/<id>) + `session` -> a gate (state=gated).
          op="resume" — `gate` (id/step_address) -> recorded resumed (native continuation).
          op="abort"  — `gate` -> supervisor /interrupt + /teardown (no-orphan).
          op="rewind" — `gate` + `source` (.jsonl) + `at` ('compact:N'|'uuid:..'|'ts:..') -> native materialize.
          op="list"   — gate records; optional `state`/`session`.
          op="get"    — one gate (`gate` = id or step_address).
        """
        from runtime import cc_gate as cg
        try:
            if op == "gate":
                if not step_address or not session:
                    raise ValueError("cc_gate(op='gate') needs `step_address` (opaque) and `session`.")
                return {"op": "gate", **cg.gate(step_address, session, note=note, by=by)}
            if op == "resume":
                if not gate:
                    raise ValueError("cc_gate(op='resume') needs `gate` (id or step_address).")
                return {"op": "resume", **cg.resume(gate, by=by, note=note)}
            if op == "abort":
                if not gate:
                    raise ValueError("cc_gate(op='abort') needs `gate` (id or step_address).")
                return {"op": "abort", **cg.abort(gate, by=by, note=note)}
            if op == "rewind":
                if not gate or not source or not at:
                    raise ValueError("cc_gate(op='rewind') needs `gate`, `source` (.jsonl), and `at`.")
                return {"op": "rewind", **cg.rewind(gate, source, at, by=by, note=note)}
            if op == "list":
                return {"op": "list", "gates": cg.list_gates(state=state or None, session=session or None)}
            if op == "get":
                if not gate:
                    raise ValueError("cc_gate(op='get') needs `gate` (id or step_address).")
                return {"op": "get", **cg.get_gate(gate)}
        except cg.GateError as e:
            return {"op": op, "ok": False, "error": str(e)}
        raise ValueError(f"cc_gate: unknown op {op!r} — one of {OPS}.")
