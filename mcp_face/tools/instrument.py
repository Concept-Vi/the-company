"""mcp_face/tools/instrument.py — THE INSTRUMENT'S TOOL FACE (the MCP door onto the radial projection).

The instrument is ONE engine, TWO faces: the visual surface (surface/app, over the bridge's /api/projection)
AND these MCP tools. Tim's law (2026-06-15): *everything that can be done through the UI must be done through
the MCP doors* — the design of the interface is half the job, and the tool face is the other half of THAT.
This is the door. It calls the SAME resolver the surface does (Suite.project → bridge.build_projection), so
the agent sees byte-identically what the operator sees — every lens, every layer (?emb=), every resolution
(?dim=), the time scrubber (?at=), the relative centre (?center=), the scale rung (?rung=). No parallel
projector (reuse-don't-parallel). Registry-true + parametric: a new binding/space/embedder layer becomes
drivable here with ZERO edit to this file (it just reads the discovered registries + the store's self-scan).
"""


def register(mcp, suite):
    @mcp.tool()
    def project(binding: str = "", space: str = "", emb: str = "", dim: int = 0, rung: str = "",
                center: str = "", at: str = "", types_space: str = "", pole_a: str = "", pole_b: str = "",
                limit: int = 150) -> dict:
        """THE INSTRUMENT — the radial universal projection, as a tool. The agent's twin of the operator's
        wheel: resolve a `binding` (a lens) into points on the seed's circle-in-square, the SAME engine the
        visual surface uses. Run with binding='' to get the available bindings echoed back (registry-true —
        every response also carries the full `bindings` list).

        THE DRIVABLE AXES (each one the MCP twin of a UI control):
          binding   — THE LENS. e.g. 'semantic' (meaning radius = cosine from a centre) · 'by_separator'
                      (signed lean between two poles) · 'by_nucleation' (where new types are born — the
                      keystone) · 'raw' / the Group-10 angle-by-registry/graph lenses (kinds, connections…).
          space     — the item store the lens ranges over (repo · history · principles · worldview · topics ·
                      operators). For nucleation, `types_space` is the registry-of-types the items are typed
                      against (e.g. types_space='operators' & space='repo' → candidate operators).
          emb       — THE EMBEDDER LAYER (the multi-layer model): '' = default (BGE); 'pplx' = the pplx layer.
                      Call the `layers` tool to see what each space carries. A mismatched-dim pair fails loud.
          dim       — THE MRL RESOLUTION: truncate every read vector to its first N dims before the cosine — a
                      continuous coarse↔fine MEANING zoom (orthogonal to `rung`). 0 = full dim.
          rung      — THE SCALE RUNG: '' / 'unit' = the items themselves; a coarse k (e.g. '8','32') = the
                      pyramid's theme/cluster centroids at that rung (zoom out from units to themes).
          center    — THE RELATIVE CENTRE: an address the whole space re-projects around (radius = distance
                      from it). Attention IS origin-selection.
          at        — THE TIME SCRUBBER: an ISO instant to move the temporal centre into the past (project
                      only events ≤ at).
          pole_a / pole_b — THE TWO GRAVITIES for the separator: any two addresses carrying vectors in the
                      lens (a corpus item, a cluster:// theme, or a planted anchor://).
          limit     — max points (default 150 — context-friendly; drive it up for a fuller field).

        RETURNS the projection body: the `binding` echo (incl. the active `emb` + MRL `res`), `bindings` (the
        full lens list — discovery), `sectors`, `points` (each with r/theta/kind/summary/address/source + the
        lens's per-point signal: fit/born for nucleation, lean/pull_a/pull_b for the separator), `scale` (the
        rung ladder when a pyramid exists), and the lens's REPORT — `nucleation_report` / `separation_report`,
        the witness that the field actually resolved (a normalized gradient over noise can never read as done).
        FAILS LOUD on an unknown binding, a centre/pole with no vector in the lens, or a layer-dim mismatch."""
        if not binding:
            _st, body = suite.project({"binding": "raw", "limit": "1"})   # 'raw' is always present — harvest the list
            return {"error": "project needs a `binding` (a lens). Pick one of the ids below — registry-true.",
                    "bindings": body.get("bindings", []),
                    "note": "drive emb (layer) · dim (MRL resolution) · rung (scale) · center · at · pole_a/pole_b — "
                            "the same axes as the UI controls. Use the `layers` tool to see each space's embedders."}
        q = {"binding": binding, "limit": str(limit)}
        for k, v in (("space", space), ("emb", emb), ("rung", rung), ("center", center),
                     ("at", at), ("types_space", types_space), ("pole_a", pole_a), ("pole_b", pole_b)):
            if v:
                q[k] = v
        if dim:
            q["dim"] = str(dim)
        _st, body = suite.project(q)
        if _st != 200:                                  # carry the status so a fail-loud body is unmistakable
            body = {**body, "_status": _st}
        return body

    @mcp.tool()
    def layers() -> dict:
        """THE MULTI-LAYER MODEL'S SELF-DESCRIPTION — which embedder LAYERS each space carries:
        {space: [embedder-layer, …]} (e.g. {'repo': ['default','pplx'], 'operators': ['default','pplx'], …}).
        The SAME data the UI's layer picker reads (/api/layers). Use it to choose `emb` for the `project` tool.
        'default' = the base BGE layer; a named layer (e.g. 'pplx') is an additive embedding over the same
        items. Registry-true: the store scans itself — a newly-embedded layer appears here with no code edit."""
        return suite.layers()
