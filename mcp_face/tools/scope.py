"""mcp_face/tools/scope.py — the POINTING MECHANISM's agent face (② of NORTH-STAR; file-drop tool).

"What code powers this UI element?" — the question the surface could always answer and agents never could
(the join had a UI face and NO MCP face until 2026-07-02). Now both faces call the ONE shared function
(runtime/scope.py), backed by the ledger's DERIVED ui://→code join (recomputed every deterministic build:
binds-ui → calls-endpoint → serves-endpoint → powered-by; plus the legacy hand-seed fold).

## Ops
  op="resolve" — ui:// address → {symbols, scope(files), stale, note}. Empty scope = DENY-ALL (an
                 unjoined element never authorizes work). Malformed address raises (S0 grammar).
  op="symbol"  — code:// id → its record {file, kind, referenced_by(ui://)}. Accepts BOTH the canonical
                 code://<project>/<path>::<symbol> AND the legacy lossy code://<stem>/<symbol> (aliased
                 through the ledger where unambiguous; ambiguity is refused, never guessed).
"""
from __future__ import annotations

from typing import Literal

OPS = ("resolve", "symbol")


def register(mcp, suite):
    @mcp.tool()
    def scope(op: Literal["resolve", "symbol"], address: str = "") -> dict:
        """The pointing mechanism: connect what you can SEE (a ui:// element) to the code behind it —
        the same shared, ledger-derived function the UI surface uses (one function, two faces).

          op="resolve" — `address`=ui://<region>/<element> → the code symbols + file scope powering it.
                         Empty scope = DENY-ALL. The join is DERIVED (re-run ledger_build to refresh).
          op="symbol"  — `address`=code:// id (canonical or legacy) → {file, kind, referenced_by}.
        """
        from runtime import scope as s
        if not address:
            raise ValueError(f"scope(op={op!r}) requires `address`.")
        if op == "resolve":
            return {"op": "resolve", **s.resolve_scope(address)}
        if op == "symbol":
            return {"op": "symbol", **s.symbol_record(address)}
        raise ValueError(f"scope: unknown op {op!r} — one of {OPS}.")
