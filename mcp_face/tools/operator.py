"""mcp_face/tools/operator.py — the OPERATOR-MEMORY tool.

ONE resource (the system's memory of working with Tim), an `op` selector. Registry-is-truth
(file-discovered, rediscovered per call). READ-ONLY on this face — new rows arrive via the mining's
proposals + Tim's confirmation, never via a tool write. THE FLOOR: pure reads.
"""
from typing import Literal

from mcp.types import ToolAnnotations    # posture="safe" → remote.py:_tool_posture reads it (registry-native)



def register(mcp, suite):
    # READ-ONLY on this face — operator-memory reads only (rules/describe/proposed); no write op. Client-safe.
    @mcp.tool(annotations=ToolAnnotations(posture="safe"))
    def operator(op: Literal["rules", "describe", "proposed"], rule: str = "") -> dict:
        """READ THE SYSTEM'S MEMORY OF ITS OPERATOR (Tim) — the confirmed rules for working with him,
        each carrying his verbatim words as evidence. IF YOU ARE ABOUT TO INTERACT WITH TIM, SURFACE
        SOMETHING TO HIM, OR PREPARE ANYTHING HE WILL SEE: read op='rules' FIRST and follow them —
        they are his own corrections, made standing.

        Pick `op`:
          · 'rules'    — every CONFIRMED row, concise: id + the rule sentence + when it applies.
          · 'describe' — ONE row in full (rule= required): the rule, why, his verbatim evidence,
                         scope, and how it was confirmed.
          · 'proposed' — rows the mining has proposed that AWAIT Tim's confirmation (visible,
                         second-class — do not treat as standing).

        The registry grows by the propose→confirm circuit (the transcript mining proposes; Tim
        confirms) — there is no write op here. A row without his verbatim evidence cannot exist
        (enforced at discovery)."""
        from runtime.operator_memory import OperatorMemoryRegistry
        reg = OperatorMemoryRegistry().discover()
        if op == "rules":
            return {"rules": [{"id": r["id"], "rule": r["rule"],
                               "when": (r.get("scope") or {}).get("when", "always")}
                              for r in reg.rows(status="confirmed")],
                    "note": "confirmed rows only — op='describe' for evidence; op='proposed' for pending"}
        if op == "describe":
            if not rule:
                raise ValueError("operator(op='describe') needs rule= — one of: " + ", ".join(sorted(reg)))
            return {"memory": reg.get(rule)}
        if op == "proposed":
            return {"proposed": reg.rows(status="proposed"),
                    "note": "awaiting Tim's confirmation — visible, not standing"}
        raise ValueError(f"unknown op {op!r} — operator ops are rules | describe | proposed.")
