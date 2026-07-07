"""mcp_face/tools/embeddings.py — EMBEDDINGS AS AN OPERABLE SURFACE (potentials-loop E1; file-drop tool).

The operator (and any agent) sees/configures/runs the embedding substrate through ONE tool — the same
shared functions the `company embed` CLI verb renders (runtime/embeddings_surface.py; one function,
two faces). Nothing here is a second dialect: routing IS fabric/embed_routing, building IS
ops/build_embeddings, pyramids ARE runtime/scale — this face only calls them.
"""
from __future__ import annotations

from typing import Literal

OPS = ("spaces", "route", "build", "pyramid")


def register(mcp, suite):
    @mcp.tool()
    def embeddings(op: Literal["spaces", "route", "build", "pyramid"],
                   space: str = "", force: bool = False) -> dict:
        """The embedding substrate, operable: see every space, read the lens routing, (re)build a
        space, rebuild its scale-pyramid rungs. Pick `op`:

          op="spaces"  — THE STATUS VIEW: every real space (units · dims · lenses/emb_layers ·
                         pyramid rungs · last-embed ts · rebuild-fingerprint freshness).
          op="route"   — the ONE lens table (space → nomic/pplx → endpoint/model/dim) + honestly HOW
                         to change it (edit fabric/embed_routing.py _NOMIC_SPACES — it is code).
          op="build"   — (re)build ONE registered space (`space`; optional `force` re-embed, ollama-kind
                         only). Incremental by content_hash — expect mostly skips on an unchanged corpus;
                         over-window items are FLAGGED for chunking, never silently truncated. Also
                         schedulable as the `build_space` jobs handler (jobs op='define').
          op="pyramid" — rebuild `space`'s scale-pyramid rungs (runtime.scale.rebuild_scale_pyramids;
                         `skipped_whole_space: true` = the fingerprint says nothing changed — fresh,
                         not failed).

        Unregistered/unknown spaces get a TEACHING refusal (what's valid + closest match).
        """
        from runtime import embeddings_surface as E
        if op == "spaces":
            return {"op": "spaces", **E.spaces_status()}
        if op == "route":
            return {"op": "route", **E.route_table()}
        if op == "build":
            if not space:
                raise ValueError(f"embeddings(op='build') requires `space` — buildable: "
                                 f"{E.spaces_status()['buildable']}")
            return {"op": "build", **E.build_space(space=space, force=force)}
        if op == "pyramid":
            return {"op": "pyramid", **E.pyramid_space(space=space)}
        raise ValueError(f"embeddings: unknown op {op!r} — one of {OPS}.")
