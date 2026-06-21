ITEM_TYPE = {
    "id": "signal",
    "label": "signal",
    "desc": "A fabric SIGNAL a lane consumes to ACT — the shared-tree, floor-clean half of the operator "
            "cycle's resume wire. The first instance: a decision.decided signal (the operator decided an "
            "addressed decision; work GATED on it can RESUME with the chosen option). Posted here so lanes "
            "SEE the decide without polling the event log (cross-session-via-shared-tree) — distinct from the "
            "gated live-MCP channel post (autonomous-spawn-lead-only: the brain records here, the lane/operator "
            "fires the actual resume). Links attached_to the decision:// address (the accumulation-point the "
            "decided VALUE lives on — any resolve reads it; the signal is the additional 'it changed' relation).",
    "initial": "raised",
    "states": ["raised", "consumed", "superseded"],
    "transitions": {
        "raised": ["consumed", "superseded"],      # a lane picked it up + resumed | a later decide/retract replaced it
        "consumed": ["superseded"],                # resumed, then a re-decide supersedes the prior signal
        "superseded": ["raised"],                  # a still-later decide re-raises (mirrors decision_take re-decide)
    },
}
