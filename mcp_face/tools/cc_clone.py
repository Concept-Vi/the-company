"""mcp_face/tools/cc_clone.py — point-in-time CLONE -> fabric, through the MCP (agent surface over
runtime/cc_clone.py). File-drop tool (pkgutil auto-register on the next MCP server start).

Clone any session AS IT WAS at a past moment and talk to that past-point context. The clone launches
as a live SUPERVISED session (headless, supervisor-controlled) and is DM'd via supervisor-inject —
the SAFE autonomous path. (Channels fire only in interactive sessions; an agent auto-launching an
interactive channel-clone is correctly blocked by the safety classifier — use op="prepare" to get the
OPERATOR command for that.)

## Ops
  op="clone"   — materialize `source` @ `at` + launch a live supervised clone. Required: `source`
                 (transcript .jsonl path), `at` ('compact:N' | 'uuid:<id>' | 'ts:<iso>'). Optional
                 `description`, `cwd`. Returns handle + session_id + the operator launch command.
  op="msg"     — DM a clone, get its past-point reply. Required: `clone` (handle/session), `message`.
  op="list"    — every live supervised clone (auto-prunes closed ones).
  op="end"     — teardown a clone + delete its materialized prefix (source untouched). Req: `clone`.
  op="prepare" — OPERATOR-interactive path: materialize @ `at` + emit the exact command for Tim to
                 launch the clone as an interactive CHANNEL member. Required: `source`, `at`.
"""
from __future__ import annotations

from typing import Literal

OPS = ("clone", "msg", "list", "end", "prepare")


def register(mcp, suite):
    @mcp.tool()
    def cc_clone(op: Literal["clone", "msg", "list", "end", "prepare"],
                 source: str = "", at: str = "", clone: str = "", message: str = "",
                 description: str = "", cwd: str = "", timeout: float = 180) -> dict:
        """Clone a Claude Code session AS IT WAS at a past moment and talk to that past context.

          op="clone"   — `source` (.jsonl) + `at` ('compact:N'|'uuid:..'|'ts:..') -> live supervised clone.
          op="msg"     — `clone` (handle) + `message` -> the clone's reply from its past-point context.
          op="list"    — live clones.
          op="end"     — `clone` -> teardown + delete materialized prefix (source untouched).
          op="prepare" — `source` + `at` -> the OPERATOR command to launch it as an interactive
                         channel member (agents cannot auto-launch interactive channel agents).
        """
        from runtime import cc_clone as cc
        try:
            if op == "clone":
                if not source or not at:
                    raise ValueError("cc_clone(op='clone') needs `source` (.jsonl path) and `at` "
                                     "('compact:N' | 'uuid:<id>' | 'ts:<iso>').")
                return {"op": "clone", **cc.clone_at(source, at, description=description, cwd=cwd or None)}
            if op == "msg":
                if not clone or not message:
                    raise ValueError("cc_clone(op='msg') needs `clone` (handle/session) and `message`.")
                return {"op": "msg", **cc.msg_clone(clone, message, timeout=timeout)}
            if op == "list":
                return {"op": "list", "clones": cc.list_clones()}
            if op == "end":
                if not clone:
                    raise ValueError("cc_clone(op='end') needs `clone` (handle/session).")
                return {"op": "end", **cc.end_clone(clone)}
            if op == "prepare":
                if not source or not at:
                    raise ValueError("cc_clone(op='prepare') needs `source` (.jsonl path) and `at`.")
                return {"op": "prepare", **cc.prepare_at(source, at, description=description, cwd=cwd or None)}
        except cc.CloneError as e:
            return {"op": op, "ok": False, "error": str(e)}
        raise ValueError(f"cc_clone: unknown op {op!r} — one of {OPS}.")
