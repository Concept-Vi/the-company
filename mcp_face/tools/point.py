"""mcp_face/tools/point.py — the RHM's POINT verb (the brain's emit door onto the surface spotlight).

Tim's law (see instrument.py): everything doable through the UI is doable through the MCP doors. The
right-hand-man, explaining a surface WITH the operator, points at the on-screen thing it names as it
speaks — this is that capability, as a tool. It is a pure PRESENTATION SIGNAL: the brain calls
point(<token>) with an OPAQUE token it was handed in its turn context (the live {token,label} catalog the
surface sources via window.surfacePointables()); the SIGNAL is the tool-call itself — run_turn surfaces it
as a {type:'point', token} stream event, and fork-brain-core (client) maps token->ui:// address from its
LOCAL copy of the same catalog and dispatches ui:point (projection's ONE sink, resolveUiTarget, spotlights
it). REUSE-DON'T-PARALLEL: the spotlight mechanism is projection's sink; this is only the brain's emit door.

OPERATOR-LAW (airtight): the token is OPAQUE (never a ui:// address) — addresses never touch the brain or
this server; only the client holds the token->address map. So this verb carries no address, validates
nothing against a catalog it doesn't have, and is READ/COSMETIC (no gated-floor concern — it moves no
state, writes nothing). An unknown/stale token degrades clean (the client finds no mapping -> no-op; the
sink no-ops on a non-ui://). The act is the signal — instant, no round-trip work."""


def register(mcp, suite):
    @mcp.tool()
    def point(token: str) -> dict:
        """Point at an on-screen thing as you talk about it — the surface spotlights it for the operator.

        token — the OPAQUE handle of the target, taken from the "Things you can point at" list in your
        context (e.g. 'wheel', 'lens', a sector's token). NOT an address. Call this the MOMENT you name one
        of those things in your reply, so the operator's eye goes where your words go. Point ONLY at handles
        in that list; never invent one. Returns {ok, token} — the act itself is the signal, instant."""
        return {"ok": True, "token": str(token or "")}
