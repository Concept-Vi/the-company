"""mcp_face/tools/keeper.py — the KEEPER tool: the tending AI answers about its project (④ L7-KEEPER).

The MCP-face projection of Suite.keeper_answer — the SAME ONE function the /api/keeper bridge route calls
(organ-studies/KEEPER.md §4.5: "one function keeper_answer(address, question, token) — the chat surface
and the agent tool both call it"; law 9: the MCP face and the HTTP face cannot diverge). File-drop contract
(pkgutil auto-register, no server.py edit).

The keeper is a COMPOSITION anchored at project://<key>: a member edge (L1) + cast_for_mode('keeper') +
config rungs resolved through the ONE ladder + a persona record. It composes territory over the address
(the project's LIVE ledger/status/members), resolves its config, fires the cast, and returns a grounded
answer + the enriched envelope (coordinate + territory + trail).
"""
from __future__ import annotations


def register(mcp, suite):
    @mcp.tool()
    def keeper(address: str, question: str, user_id: str = "", fire: bool = True) -> dict:
        """Ask the KEEPER of a project about its project. The keeper answers grounded in the project's
        OWN live ledger/status/members — never invention; it flags what it cannot ground.

          address   — the project container: project://<key> (e.g. project://counterpart-design).
          question  — the operator's question about the project.
          user_id   — optional principal address of the asker (rides the coordinate/token).
          fire      — True (default): fire the keeper cast and return a real answer. False: return the
                      DETERMINISTIC envelope only (coordinate + territory + resolved config + trail; no
                      model call) — the half the MCP + HTTP faces agree on byte-for-byte.

        Returns {answer, envelope, cast}: `envelope` carries the coordinate (the anchor + surface token,
        accreted), the composed territory (the live project legs, never accreted), the resolved config +
        governed-verb whitelist, and the trail (who accreted what, per stage)."""
        if not (address and question):
            raise ValueError("keeper(address, question): both are required "
                             "(e.g. address='project://counterpart-design', question='what does it hold?').")
        token = {"user_id": user_id} if user_id else None
        return suite.keeper_answer(address, question, token, fire=fire)
