"""C3 — the node record (Pydantic): instance on a canvas, both faces. See build-prep/contracts/C3.

NodeInstance/Edge/Graph = the WORKFLOW face (what you see/edit).
ExecNode = the EXECUTION face (compiled, what the runtime runs — no pixels).
"""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

Status = Literal["idle", "ready", "running", "ran", "cached", "done", "failed", "surfaced"]


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
