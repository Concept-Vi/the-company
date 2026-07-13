"""mcp_face/bridge_write_manifest.py — the DECLARED consequential-write boundary for the bridge (:8770).

B4 leg 2, co-designed (lead↔fabric, board://item-33970ac8). The SIBLING of remote_safe_manifest.py —
ONE auth doctrine across both public fronts:
  • remote front (:8772): the SAFE set is declared; everything else is operator-only.  (FL1, shipped)
  • bridge front (:8770): the FREE set is declared; everything else is CONSEQUENTIAL → the operator
    token is required.  (this file)

WHY "declare the FREE set", not "list the writes": FAIL-CLOSED BY CONSTRUCTION. There are ~87 POST
routes and the set grows; enumerating writes means a new write route ships UNGATED until someone
remembers to list it (the silent-boundary-rewrite hazard, again). Declaring the small, stable READ/
COMPUTE set instead means a new route is consequential — gated — the instant it exists; opening it is
the deliberate act of adding it here (the manifest edit IS the decision record). Same law as FL1, dual.

WHAT COUNTS AS FREE: a POST route is free ONLY if it neither mutates durable state nor acts on the
world — pure resolve/translate/query/compute, or a lenient client-trace write whose loss changes
nothing. A route that writes the board/store, posts to a channel, spawns/runs, changes config, or
resolves an operator decision is CONSEQUENTIAL by construction — never listed here.

ENFORCEMENT (the lead wires this in bridge.py; fabric reviews against this declaration):
  a consequential POST with no valid X-Operator-Session → TEACH-AND-REFUSE (403 + a body naming the
  route, that it is consequential, and how to mint the token) — the TeachingRefusal shape, NEVER a
  bare 401 and NEVER a silent no-op. Reads in the FREE set run without a token (Tim's own console must
  stay frictionless for the read path). Gated by COMPANY_OPERATOR_TOKEN_ENFORCE — this file is the set
  the flag enforces over.

SEED STATUS (2026-07-13): the FREE list below is fabric's first cut from a route enumeration; entries
marked ⚠ are fabric-uncertain and need the lead's confirmation (they know these routes' bodies). The
acceptance test asserts the doctrine (every non-free POST route is gated) — so a mis-seed fails LOUD
toward safety (a real read wrongly gated is a visible 403, never an ungated write).
"""

# POST routes that run WITHOUT the operator token — pure read/compute + lenient traces. Sorted; one per
# line so a diff reads as a boundary decision. Everything NOT here is consequential (token required).
BRIDGE_FREE_POST = frozenset({
    "/api/resolve",              # pure layout resolver (resolve(invariant,coordinate)->slot); no gate by its own header
    "/api/query",                # ledger.query read
    "/api/coa",                  # course-of-action compute (read)
    "/api/voice/log",            # lenient client-side voice trace (loss changes nothing)
    # ⚠ fabric-uncertain — lead confirm these are pure read/compute before leaving free:
    "/api/cognition/preview_turn",   # ⚠ name says preview (no commit) — confirm it writes nothing
    "/api/cognition/role/dry_run",   # ⚠ dry_run — confirm no persist
    "/api/cognition/rule/dry_run",   # ⚠ dry_run — confirm no persist
    "/api/cognition/rule/validate",  # ⚠ validate — confirm no persist
    "/api/decision/explain",         # ⚠ explain — confirm read-only (vs decision/* writes)
    "/api/intent-at",                # ⚠ confirm read (a lookup) vs a build-intent write
})
# NOTE (why up-translate / address-help / stale-at are NOT here though they're reads): they are GET
# routes on the read-only GET face, not POST — this manifest governs the POST face only (the test
# caught them named here as rot, 2026-07-13). They're free by being GET, which needs no declaration.

# The read-only GET face is free by nature (do_GET carries no consequential writes — audit line
# bridge.py:149 "NO consequential surface-write, no gate"). This manifest governs the POST face only;
# the test asserts that scope explicitly so no one assumes it covers GET.
