"""C5 (Part 1) — `/object_info` serialization: node-types → frontend.

The frontend is a GENERIC renderer (ComfyUI's proven pattern): it holds no
per-node-type code. It asks the runtime for the whole type library, serialized,
and from that builds the palette, every render-mode, and every inspector.

This module SERIALIZES the C2 type library (`contracts.node_type.NodeType`).
It is generated FROM the registry — never hand-written. Add a node-type → it
registers → `/object_info` gains an entry → the frontend re-merges → the new
type appears live, no frontend code written. See build-prep/contracts/C5.

Schema-additive: new serialized fields carry defaults; an older frontend ignores
fields it doesn't know, so backend and frontend evolve at different speeds.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from contracts.node_type import NodeType, Ports

# Bumped when the SERIALIZATION shape changes (additively). Lets the frontend
# reason about which serialized fields it can expect. Distinct from a single
# node-type's own `version`.
SCHEMA_VER = 1


class ObjectInfoEntry(BaseModel):
    """One serialized node-type — exactly the C2 fields the frontend needs.

    The node-type's `name` is the DICT KEY in the `/object_info` map, so it is
    not repeated as a field here (matches the C5 spec's `{ "<name>": {...} }`).
    """

    title: str
    category: str
    kind: str
    ports: Ports
    config_schema: dict = Field(default_factory=dict)
    output_schema: dict = Field(default_factory=dict)
    render_set: list[str] = Field(default_factory=list)
    inspector_schema: dict = Field(default_factory=dict)
    actions: list[str] = Field(default_factory=list)
    version: int = 1

    @classmethod
    def from_node_type(cls, nt: NodeType) -> "ObjectInfoEntry":
        return cls(
            title=nt.title,
            category=nt.category,
            kind=nt.kind,
            ports=nt.ports,
            config_schema=nt.config_schema,
            output_schema=nt.output_schema,
            render_set=list(nt.render_set),
            inspector_schema=nt.inspector_schema,
            actions=list(nt.actions),
            version=nt.version,
        )


def build_object_info(node_types: dict[str, NodeType]) -> dict:
    """Serialize the C2 type library for the frontend.

    Returns a plain JSON-serializable dict: ``{ "<name>": { ...C2 fields... } }``.
    Generated from the registry — the single source (rule 3): UI, runtime, and
    tools all project from the same `NodeType`.

    Fail loud (rule 4): a malformed registry (non-`NodeType` value, or a key
    that disagrees with the type's own `name`) raises rather than emitting a
    silently-wrong palette.
    """
    out: dict = {}
    for key, nt in node_types.items():
        if not isinstance(nt, NodeType):
            raise TypeError(
                f"/object_info: registry entry {key!r} is {type(nt).__name__}, "
                f"expected NodeType"
            )
        if nt.name and nt.name != key:
            raise ValueError(
                f"/object_info: registry key {key!r} disagrees with "
                f"NodeType.name {nt.name!r} — one source (rule 3) violated"
            )
        out[key] = ObjectInfoEntry.from_node_type(nt).model_dump(mode="json")
    return out
