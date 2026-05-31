"""C2 — the node-type contract (Pydantic). See build-prep/contracts/C2.

The single definition of what a node IS — UI, runtime, and tools all project from it.
Three kinds via this one shape: process · content · presentation.
"""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

RenderMode = Literal["collapsed", "expanded", "full", "workshop"]
Kind = Literal["process", "content", "presentation"]


class Ports(BaseModel):
    inputs: dict[str, str] = Field(default_factory=dict)    # port name -> port-type name
    outputs: dict[str, str] = Field(default_factory=dict)


class NodeType(BaseModel):
    name: str                                    # unique id, e.g. "extract"
    title: str = ""
    category: str = ""                           # palette grouping
    kind: Kind = "process"
    extends: str | None = None                   # type-graph relation (S4)
    ports: Ports = Field(default_factory=Ports)
    config_schema: dict = Field(default_factory=dict)     # inspector's editable fields
    output_schema: dict = Field(default_factory=dict)     # the structured thing it produces
    render_set: list[RenderMode] = Field(
        default_factory=lambda: ["collapsed", "expanded", "full", "workshop"])
    inspector_schema: dict = Field(default_factory=dict)
    actions: list[str] = Field(default_factory=lambda: ["run"])
    layout_hints: dict = Field(default_factory=dict)
    version: int = 1

    def model_post_init(self, __ctx) -> None:
        if not self.title:
            object.__setattr__(self, "title", self.name.title())
