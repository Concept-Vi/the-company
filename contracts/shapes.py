"""Skeleton shapes (C1/C3, dataclass form).

Stdlib dataclasses for the walking skeleton; these become the Pydantic-validated
contracts in stage E1/E4. See contracts/AGENTS.md (schema-additive; the spine).
"""
from dataclasses import dataclass, field


@dataclass
class NodeInstance:           # C3, face 1 (execution-relevant subset)
    id: str
    type: str                 # -> a registered node-type (C2)
    config: dict = field(default_factory=dict)


@dataclass
class Edge:                   # a wire = a binding between two ports
    from_node: str
    from_port: str
    to_node: str
    to_port: str


@dataclass
class Graph:
    id: str
    nodes: list               # list[NodeInstance]
    edges: list               # list[Edge]
