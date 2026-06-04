"""mcp_face/server.py — the agent face (C7). FastMCP exposing the generic verbs over the
shared Suite. Same brain + same substrate as the UI bridge (runtime.suite.Suite). See mcp_face/AGENTS.md.

(Dir is `mcp_face`, not `mcp`, to avoid colliding with the installed `mcp` SDK package.)
Verbs are GENERIC over node-type — adding a node-type adds zero tools.
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP          # the SDK (site-packages)
from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from fabric import config as fcfg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUITE = Suite(FsStore(fcfg.STORE_DIR),
              NodeRegistry().discover([os.path.join(ROOT, "nodes")]))

mcp = FastMCP("company")


@mcp.tool()
def list_types() -> list:
    """List every registered node-type (process · content · presentation)."""
    return SUITE.list_types()


@mcp.tool()
def object_info() -> dict:
    """The full node-type library (ports · render-set · config) for rendering/composition."""
    return SUITE.object_info()


@mcp.tool()
def list_by_type(output_type: str) -> list:
    """Type-graph query: which node-types PRODUCE a given port-type."""
    return SUITE.list_by_type(output_type)


@mcp.tool()
def list_graphs() -> list:
    """List all graphs (canvases) in the substrate."""
    return SUITE.list_graphs()


@mcp.tool()
def create_node(graph: str, type: str, config: dict = {}, node_id: str = "") -> str:
    """Add a node of `type` to `graph` (GENERIC — works for any registered type). Returns its id."""
    return SUITE.create_node(graph, type, dict(config), node_id or None)


@mcp.tool()
def connect(graph: str, from_node: str, from_port: str, to_node: str, to_port: str) -> str:
    """Wire from_node.from_port -> to_node.to_port in `graph`."""
    SUITE.connect(graph, from_node, from_port, to_node, to_port)
    return "ok"


@mcp.tool()
def delete_node(graph: str, node: str) -> str:
    """Remove `node` from `graph` along with any edges touching it."""
    SUITE.delete_node(graph, node)
    return "ok"


@mcp.tool()
def set_config(graph: str, node: str, config: dict) -> str:
    """Update a node's config in `graph`."""
    SUITE.set_config(graph, node, dict(config))
    return "ok"


@mcp.tool()
def run_graph(graph: str, branch: str = "main") -> dict:
    """Run `graph`; returns which nodes ran vs were cached (memo)."""
    r = SUITE.run(graph, branch=branch)
    return {"ran": sorted(r["ran"]), "cached": sorted(r["skipped"]), "stuck": r["stuck"]}


@mcp.tool()
def get_state(graph: str) -> dict:
    """Current state of `graph`: nodes, statuses, outputs, addresses."""
    return SUITE.state(graph)


@mcp.tool()
def get_results(graph: str) -> dict:
    """The output of each node in `graph`."""
    return SUITE.results(graph)


# --- self-growth: build-dispatch + the surfaced-decision inbox (D7/D4) ---
@mcp.tool()
def propose_node(name: str, spec: str) -> dict:
    """Build-dispatch: ask the brain to WRITE a new node-type module. Returns {name, code}.
    Proposing is safe; APPLYING is CONFIRM-gated (see apply_node)."""
    return SUITE.propose_node(name, spec)


@mcp.tool()
def apply_node(surfaced_id: str) -> str:
    """Apply a proposed node by its surfaced id — succeeds ONLY if the OPERATOR has approved it
    (resolved=='approve'). The agent cannot self-approve (approval is not on this face)."""
    return SUITE.apply_node(surfaced_id)


@mcp.tool()
def list_surfaced() -> list:
    """Decisions the system surfaced for the operator (each carries a default + resolution)."""
    return SUITE.list_surfaced()


@mcp.tool()
def self_change_log(limit: int = 50) -> list:
    """The self-modification AUDIT LEDGER — the [self-apply] commit history newest-first, each entry
    with sha · subject · timestamp · changed_files (which files it touched) · is_revert (a revert is
    surfaced distinctly, never mistaken for a change). For one-click rollback + audit of the system's
    own self-edits; revert is operator-only (off this face)."""
    return SUITE.self_change_log(limit)


@mcp.tool()
def get_events(limit: int = 60) -> list:
    """The captured trajectory — recent actions (run · create · connect · grow · approve), newest-first."""
    return SUITE.events(limit)


@mcp.tool()
def now(graph: str) -> dict:
    """The now-view + presence snapshot for `graph` — node counts, pending approvals, presence, last event."""
    return SUITE.now(graph)


@mcp.tool()
def chat(message: str, graph: str) -> dict:
    """Converse with the right-hand-man — the coherent voice of the Company about itself. Answers
    from live ground truth; suggests actions but performs none that skip the surfaced gate."""
    return SUITE.chat(message, graph)


@mcp.tool()
def inbox() -> dict:
    """The chief-of-staff inbox triaged into lanes: live escalations, resolved-for-you, batched."""
    return SUITE.inbox_lanes()


@mcp.tool()
def capabilities() -> dict:
    """The source of truth for WHAT EXISTS — real models, node-types, RHM verbs, panels, api verbs.
    Author from these; never invent. If you need something not here, ask the operator (don't fabricate)."""
    return SUITE.capabilities()


# NOTE: resolve_surfaced (operator approval) is deliberately NOT exposed on this face — only the
# UI/operator channel may approve a CONFIRM, so the proposing agent cannot self-approve its code-build.


if __name__ == "__main__":
    mcp.run(transport="stdio")
