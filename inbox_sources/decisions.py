"""inbox_sources/decisions.py — open DECISIONS awaiting the operator's call.

Rides the SAME decision feed `/api/decisions` projects (`runtime.decision_registry.decision_inbox`, folded
through `runtime.cognition.decision_registry()` + `DecisionSubtypeRegistry`, EXACTLY the bridge's own
construction at that route) — no parallel decision read. Filters to `state == "pending"` ("open decisions"
per the I1 spec; a "decided" row no longer needs Tim). `why` derives from `recommended_label` (present on
every row — `compose_state`'s static derivation), never invented.

The verb is a VIEW/drill-through, not a resolve: taking a decision (`decision_take`) is a heavier,
territory-gated write (`/api/territory/write`, element_id-addressed, operator-session-enforced — see
`runtime/bridge.py`'s `/api/territory/write` block) that does not fit a bare "verb button" with no free-
text/element context. `/api/decision` (POST {id} -> `SUITE.decision_view`) is the real, always-working
door this card can safely ride in v1 — Tim drills to the decision's full framing from the card; the actual
take still happens through the decision's own surface. Honest, not a shortcut pretending to resolve."""


def fetch() -> list:
    import os
    from fabric import config as fcfg
    from runtime.suite import Suite
    from store.fs_store import FsStore
    from runtime.registry import NodeRegistry
    from runtime.cognition import decision_registry as _dreg_factory
    from runtime.decision_registry import decision_inbox as _decision_inbox
    from runtime.decision_subtypes import DecisionSubtypeRegistry as _DSTReg

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    suite = Suite(FsStore(fcfg.STORE_DIR), NodeRegistry().discover([os.path.join(root, "nodes")]))
    subreg = _DSTReg().discover([os.path.join(root, "decision_subtypes")])
    rows = _decision_inbox(_dreg_factory(), suite.store, subtype_registry=subreg)

    out = []
    for r in rows:
        if r.get("state") != "pending":            # "open decisions" only — decided rows don't need Tim
            continue
        rec = r.get("recommended_label")
        why = (f"Awaiting your decision — recommended: {rec}" if rec
               else "Awaiting your decision (no recommendation yet)")
        out.append({
            **r,
            "title": r.get("name") or r.get("id"),
            "why": why,
            "created": "",             # decision rows carry no created ts (registry-is-truth: none exists)
        })
    return out


INBOX_SOURCE = {
    "id": "decisions",
    "label": "Decision",
    "fetch": "inbox_sources.decisions:fetch",
    "card_shape": {
        "id_field": "id", "address_field": "address", "title_field": "title",
        "why_field": "why", "created_field": "created",
    },
    "verbs": [
        {"id": "view", "label": "View decision", "door": "/api/decision"},
    ],
}
