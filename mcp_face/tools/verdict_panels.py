"""mcp_face/tools/verdict_panels.py — the VERDICT-PANEL tool (GC7 on the face).

ONE resource (the verdict-panel registry — diverse lens-juries), an `op` selector (the
MCP-DESIGN-PRINCIPLE shape). Registry-is-truth: the runnable set IS verdict_panels/<id>.py
(file-discovered, rediscovered per call). THE FLOOR: a panel JUDGES — its verdict flags/confirms for
the operator's review; running one emits NO resolve/approve/dispatch.
"""


def register(mcp, suite):
    @mcp.tool()
    def panel(op: str, panel: str = "", utterance: str = "", element: str = "") -> dict:
        """JUDGE something through a DIVERSE PANEL — N different lens-roles, one fire each, a
        deterministic quorum (the perspective-diverse jury: where run_role draws measure one judge's
        self-consistency, a panel's seats catch DIFFERENT failure modes — grounding vs voice vs
        claims-fit). Pick `op`:

          · 'list'     — every registered panel: id + label + seats + quorum.
          · 'describe' — ONE panel's full row (panel= required).
          · 'run'      — fire it (panel= required): `utterance` (required) is the PRIMARY input every
                         seat reads (e.g. a dossier JSON); `element` (optional) is the extra context a
                         seat may declare (e.g. the element snippet a claims-fit lens compares against
                         — a seat judging fit WITHOUT the real element will rightly dissent; supply it).
                         Returns {verdict, seats:[{seat, grounded, reason}], grounded_seats, quorum} —
                         every dissent NAMED, a failed seat recorded as a dissent (never a silent pass).

        THE FLOOR: judges only — the verdict informs the operator's review; nothing here resolves or
        approves. A new panel is a committed verdict_panels/<id>.py (see verdict_panels/AGENTS.md);
        new SEATS are roles — author one via create(kind='role') with a bool `grounded` output field."""
        from runtime.verdict_panels import PanelRegistry
        from runtime import cognition as C
        reg = PanelRegistry().discover()
        if op == "list":
            return {"panels": [{"id": r["id"], "label": r["label"], "seats": r["seats"],
                                "quorum": r["quorum"]} for r in reg.rows()]}
        if op == "describe":
            if not panel:
                raise ValueError("panel(op='describe') needs panel= — one of: " + ", ".join(sorted(reg)))
            return {"panel": reg.get(panel)}
        if op == "run":
            if not panel:
                raise ValueError("panel(op='run') needs panel= — one of: " + ", ".join(sorted(reg)))
            if not utterance:
                raise ValueError("panel(op='run') needs utterance= — the thing being judged (every seat "
                                 "reads it; e.g. the dossier JSON).")
            ctx = {"utterance": utterance}
            if element:
                ctx["element"] = element
            row = reg.get(panel)
            return C.run_panel(row, ctx, suite.store, turn_id=f"mcp-panel-{row['id']}",
                               resolve_role=lambda rid: suite.role_registry.get(rid))
        raise ValueError(f"unknown op {op!r} — panel ops are list | describe | run (fail loud).")
