"""mcp_face/tools/decisions.py — the operator's DECISIONS-WAITING verb (the brain's canonical source).

THE COHERENCE FIX (2026-06-19, projection's integration cold-stranger FLAG C — the trust-breaker): asked
"what decisions are waiting for me?", the RHM brain was reaching `list_surfaced` (the surfaced-ACTION /
build-approval inbox — review/role_build/code_build items, s-coded ids) because that verb's docstring said
"Decisions". So the V enumerated a DIFFERENT set than the operator's decision-cards inbox renders (the
/api/decisions canonical set) — two contradictory "your decisions", and it leaked the s-code ids (FLAG B).
ROOT (verified by use): the canonical decision registry had NO MCP verb, so the brain couldn't reach it.

THIS verb is that source — the SAME `decision_inbox(decision_registry(), store)` the inbox pill renders
(/api/decisions), so the V answers COHERENTLY with what the operator sees, by construction. OPERATOR-LAW:
returns the pending decisions by human NAME + the recommended option only — NEVER an id/address/code (the
brain can't leak what it isn't given; same pattern as the pointables catalog). registry-is-truth + GPU-free
(decision_inbox uses the fast mark-composed state — no recall/embed)."""


def register(mcp, suite):
    @mcp.tool()
    def decisions() -> dict:
        """The decisions WAITING for the operator — the SAME canonical set shown in their 'decisions waiting'
        inbox. Use THIS whenever they ask what decisions are open / waiting / pending for them. Do NOT use
        list_surfaced for this (that is the separate surfaced-action / build-approval inbox — different items)
        nor session_recall (that is PAST decisions from memory) — those will CONTRADICT what they see. Returns
        the pending decisions by human NAME (+ the recommended option, if any) — never an id or code. Name them
        plainly; offer to walk them through one. Returns {waiting, decisions:[{name, recommended}],
        already_decided}."""
        from runtime.cognition import decision_registry
        from runtime.decision_registry import decision_inbox
        rows = decision_inbox(decision_registry(), getattr(suite, "store", None))
        pending = [{"name": r.get("name"), "recommended": r.get("recommended_label")}
                   for r in rows if isinstance(r, dict) and r.get("state") == "pending"]
        decided = sum(1 for r in rows if isinstance(r, dict) and r.get("state") != "pending")
        return {"waiting": len(pending), "decisions": pending, "already_decided": decided}
