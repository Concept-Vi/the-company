"""mcp_face/tools/flows.py — the FLOWS tool (GC1: the grounded chains, one call away).

ONE resource (the FLOW registry — committed production lines), an `op` selector (the
MCP-DESIGN-PRINCIPLE shape — never a new flat tool per flow). Registry-is-truth: the runnable set IS
flows/<id>.py (file-discovered, rediscovered per call — a new committed row appears without restart).
THE FLOOR: flows are repo-AUTHORED + MCP-INVOKED; every row declares proposes_only=True (enforced at
discovery); running one emits NO resolve/approve/dispatch and launches NO claude -p.
"""
from typing import Literal



def register(mcp, suite):
    @mcp.tool()
    def flows(op: Literal["list", "describe", "run", "propose"], flow: str = "", params: dict | None = None, spec: dict | None = None) -> dict:
        """RUN A PROVEN PRODUCTION LINE (a 'flow') — the registered multi-step chains, ONE call each.

        WHY THIS EXISTS: chains like the registry-filling line need a designed CONTEXT PACKAGE per
        model step + a deterministic fact-check floor; rebuilding them by hand from the primitives
        loses that grounding (proven empirically). The registered flow IS the grounded version —
        use it instead of recomposing run_role/run_items yourself.

        Pick `op`:
          · 'list'     — every registered flow: id + label + one-line description + declared params.
          · 'describe' — ONE flow's full row (flow= required): the chain's stages, params with
                         defaults and descriptions, where its outputs land.
          · 'propose'  — PROPOSE a NEW flow (spec= {id, label, description, params, body}; `body`
                         is the run() code). GATED: a body touching operator verbs or process
                         launches refuses immediately; a clean proposal SURFACES for the operator's
                         approval of the source — it lands only on his approve (you cannot apply it).
          · 'run'      — invoke it (flow= required; params= optional dict matching the DECLARED
                         params — unknown names refuse loud with the declared set named). Flows are
                         BOUNDED (time-budget params) and resume-safe where stateful; the return is
                         the flow's own batch summary dict.

        THE FLOOR: every flow proposes only — artifacts, corpus records, review items for the
        operator's gate. Nothing a flow does resolves/approves/dispatches; operator approvals stay
        the operator's. A NEW flow is authored as a committed flows/<id>.py (see flows/AGENTS.md),
        never through this tool — declarative chains go through save_cascade instead."""
        from runtime.flows import FlowRegistry
        reg = FlowRegistry().discover()
        if op == "list":
            rows = [{"id": r["id"], "label": r["label"], "description": r["description"],
                     "params": r["params"]} for r in reg.rows()]
            out = {"flows": rows}
            if not rows:
                # Q6 — an empty list must never read as 'no chains exist': the OTHER chain registry
                # (saved cascades) may be populated; point there instead of misleading a cold agent.
                out["note"] = ("no flows registered in THIS environment — but saved CASCADES (the "
                               "declared data-chains) may exist: list_cascades / run_cascade, or "
                               "capabilities(section='chains') for both registries together.")
            return out
        if op == "describe":
            if not flow:
                raise ValueError("flows(op='describe') needs flow= — one of: " + ", ".join(sorted(reg)))
            return {"flow": reg.get(flow).spec}
        if op == "propose":
            if not isinstance(spec, dict):
                raise ValueError("flows(op='propose') needs spec= {id, label, description, params, body} "
                                 "— body is the run() code (str). The operator approves the source.")
            return suite.propose_flow(spec)
        if op == "run":
            if not flow:
                raise ValueError("flows(op='run') needs flow= — one of: " + ", ".join(sorted(reg)))
            return {"flow": flow, "result": reg.get(flow).run(**(params or {}))}
        raise ValueError(f"unknown op {op!r} — flows ops are list | describe | run | propose (fail loud).")
