"""C3 — the node record (Pydantic): instance on a canvas, both faces. See build-prep/contracts/C3.

NodeInstance/Edge/Graph = the WORKFLOW face (what you see/edit).
ExecNode = the EXECUTION face (compiled, what the runtime runs — no pixels).

Schema-additive (AGENTS.md rule 2): add optional fields + bump SCHEMA_VER; never break an
existing one. SCHEMA_VER bumped to 2 by Concurrent Cognition G1 (C1.3) — `Edge.kind` is a
NEW OPTIONAL field defaulting to "data", so every existing graph (edges with no `kind`)
deserializes UNCHANGED (a data-wire). The edge-kind vocabulary is a single-source registry
(EDGE_KINDS below) — its drift home is contracts/node_record.py itself + the contracts
constitution; tests/edge_kinds_acceptance.py asserts it stays reflected.
"""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

# C3 schema version. v1 = the original {from_node,from_port,to_node,to_port} edge; v2 adds the
# optional declared Edge.kind (default "data") — additive, old graphs load unchanged.
SCHEMA_VER = 2

Status = Literal["idle", "ready", "running", "ran", "cached", "done", "failed", "surfaced"]

# --- the edge-kind registry (single source, C1.3 / R2-FOLD H5) ---------------------------------
# An edge is NOT a bare wire — it carries a declared `kind`. Today's graphs are all "data" wires
# (and default to it). The cognition layer adds the "injection" kind (a part reads a role's
# resolved run:// output into its context — the net-new ref-read of C1.3/C4.2). `gate` and
# `fan_in` are declared here so the vocabulary is registered ONCE (rule 8 — never invent a kind
# off-registry); their behaviour stays NODE-driven (the scheduler's gate/join nodes — R1-FOLD:
# "DON'T turn gate/join into edges"), the kind is the renderable/declarative label.
EDGE_KINDS: dict[str, str] = {
    "data":      "a data-wire — the source port's content feeds the destination port (the default).",
    "injection": "a cognition ref-read — a reply part reads a role's resolved run://<turn>/<role> "
                 "output into its context (C1.3/C4.2; net-new, addressed by run:// only).",
    "gate":      "a conditional wire downstream of a gate/branch node (behaviour lives in the node).",
    "fan_in":    "a join/aggregation wire into a fan-in node (behaviour lives in the join node).",
}
EDGE_KIND_DEFAULT = "data"

EdgeKind = Literal["data", "injection", "gate", "fan_in"]


class XY(BaseModel):
    x: float = 0
    y: float = 0


class WH(BaseModel):
    w: float = 268
    h: float = 120


class NodeInstance(BaseModel):           # workflow face
    id: str
    type: str                            # -> NodeType.name (C2)
    config: dict = Field(default_factory=dict)
    position: XY = Field(default_factory=XY)
    size: WH = Field(default_factory=WH)
    render_state: str = "collapsed"
    layer: str = "main"
    status: Status = "idle"
    outputs: dict[str, str] = Field(default_factory=dict)   # port -> address (filled by runtime)


class Edge(BaseModel):
    from_node: str
    from_port: str
    to_node: str
    to_port: str
    # C1.3 (schema-additive, v2): the declared edge KIND. Optional with a default of "data", so
    # every pre-v2 graph (edges with no `kind`) loads as a data-wire UNCHANGED. Validated against
    # EDGE_KINDS by callers that care (the cognition layer); the contract keeps it a plain str-typed
    # literal so an unknown value is a load-time pydantic error, never a silent mystery kind.
    kind: EdgeKind = EDGE_KIND_DEFAULT


class Graph(BaseModel):
    id: str
    nodes: list[NodeInstance] = Field(default_factory=list)
    edges: list[Edge] = Field(default_factory=list)


class ExecNode(BaseModel):               # execution face (compiled)
    id: str
    type: str
    inputs: dict[str, str] = Field(default_factory=dict)    # port -> resolved address
    config: dict = Field(default_factory=dict)
    outputs: dict[str, str] = Field(default_factory=dict)
