"""C7 — the MCP tool surface (the agent face). See build-prep/contracts/C7.

The load-bearing property: the tools are a SMALL FIXED SET of GENERIC verbs over
the single type source — NOT one tool per node-type. Adding a node-type adds ZERO
tools; the verbs consult the registries (C2/C3) to act on any type. The agent uses
introspection verbs to LEARN a type, then the generic verbs to USE it — the same
surface the canvas drives (symmetric agency).

This module defines the TYPED SCHEMAS for the verbs: a Pydantic params model and a
Pydantic result model per verb, plus a `TOOLS` registry mapping verb-name ->
ToolSpec (params model, result model, summary, honest annotations). It is the
contract, not a running server — the FastMCP server (mcp/server.py) projects from
this and calls the same internal API the canvas's actions call.

Schema-additive: new optional params carry defaults; growth happens in types/
compositions, not here. The verb set is the fixed kernel.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# Build against the spine — import, do not redefine (C3).
from contracts.node_record import Edge, NodeInstance
from contracts.node_type import NodeType

# The spine's executable shapes do not carry a `schema_ver` field
# (node_record has none; node_type uses `version: int`). Rather than pollute every
# param model with a field the spine doesn't use, the tool surface is versioned once
# here. Bump additively when verbs/params change.
SCHEMA_VER = 1


# ─────────────────────────────────────────────────────────────────────────────
# introspection — how the agent LEARNS what exists (reads the registries)
# ─────────────────────────────────────────────────────────────────────────────
class GetTypeGraphParams(BaseModel):
    """No params — return the whole type-graph (C2 registry + extends relations)."""


class GetTypeGraphResult(BaseModel):
    types: list[NodeType] = Field(default_factory=list)
    # type-name -> parent type-name (the `extends` relation, S4)
    edges: dict[str, str] = Field(default_factory=dict)


class ListByTypeParams(BaseModel):
    type: str                                      # a NodeType.name (C2)


class ListByTypeResult(BaseModel):
    type: str
    nodes: list[NodeInstance] = Field(default_factory=list)


class ObjectInfoParams(BaseModel):
    # Optional target: a node id OR a type name. Omitted = describe everything.
    target: str | None = None


class ObjectInfoResult(BaseModel):
    # The /object_info projection (C5) — generic blob; shape depends on target.
    info: dict[str, Any] = Field(default_factory=dict)


class SearchParams(BaseModel):
    query: str


class SearchHit(BaseModel):
    kind: str                                      # "type" | "node" | "source" | ...
    id: str
    summary: str = ""


class SearchResult(BaseModel):
    query: str
    hits: list[SearchHit] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# sources
# ─────────────────────────────────────────────────────────────────────────────
class SourceRef(BaseModel):
    id: str
    spec: dict = Field(default_factory=dict)
    state: str = "registered"


class ListSourcesParams(BaseModel):
    """No params."""


class ListSourcesResult(BaseModel):
    sources: list[SourceRef] = Field(default_factory=list)


class RegisterSourceParams(BaseModel):
    spec: dict


class RegisterSourceResult(BaseModel):
    source: SourceRef


class SurveySourceParams(BaseModel):
    id: str


class SurveySourceResult(BaseModel):
    id: str
    survey: dict = Field(default_factory=dict)     # what the source contains


# ─────────────────────────────────────────────────────────────────────────────
# graphs / compositions
# ─────────────────────────────────────────────────────────────────────────────
class ListGraphsParams(BaseModel):
    """No params."""


class GraphRef(BaseModel):
    id: str
    title: str = ""
    node_count: int = 0


class ListGraphsResult(BaseModel):
    graphs: list[GraphRef] = Field(default_factory=list)


class CreateNodeParams(BaseModel):
    graph: str
    type: str                                      # generic — any NodeType.name (C2)
    config: dict = Field(default_factory=dict)


class CreateNodeResult(BaseModel):
    node: NodeInstance


class ConnectParams(BaseModel):
    graph: str
    edge: Edge


class ConnectResult(BaseModel):
    graph: str
    edge: Edge


class SetConfigParams(BaseModel):
    node: str
    config: dict


class SetConfigResult(BaseModel):
    node: NodeInstance


class DeleteNodeParams(BaseModel):
    node: str


class DeleteNodeResult(BaseModel):
    node: str
    deleted: bool = True


class ValidateGraphParams(BaseModel):
    id: str


class ValidationIssue(BaseModel):
    node: str | None = None
    edge: Edge | None = None
    message: str


class ValidateGraphResult(BaseModel):
    id: str
    ok: bool
    issues: list[ValidationIssue] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# runs — the live controls (D1)
# ─────────────────────────────────────────────────────────────────────────────
class RunRef(BaseModel):
    id: str
    graph: str
    status: str = "running"


class RunGraphParams(BaseModel):
    graph: str


class RunGraphResult(BaseModel):
    run: RunRef


class WatchRunParams(BaseModel):
    id: str


class WatchRunResult(BaseModel):
    id: str
    status: str
    # node id -> status (live snapshot the agent watches)
    nodes: dict[str, str] = Field(default_factory=dict)


class PauseRunParams(BaseModel):
    id: str


class PauseRunResult(BaseModel):
    id: str
    status: str = "paused"


class RetryParams(BaseModel):
    id: str
    node: str | None = None                        # None = retry the failed frontier


class RetryResult(BaseModel):
    run: RunRef


class BranchRunParams(BaseModel):
    id: str
    changes: dict = Field(default_factory=dict)    # config overrides for the branch


class BranchRunResult(BaseModel):
    run: RunRef
    branched_from: str


class ReprioritiseParams(BaseModel):
    id: str
    level: int


class ReprioritiseResult(BaseModel):
    id: str
    level: int


# ─────────────────────────────────────────────────────────────────────────────
# results
# ─────────────────────────────────────────────────────────────────────────────
class GetResultsParams(BaseModel):
    run: str


class GetResultsResult(BaseModel):
    run: str
    # node id -> output port -> resolved address (C1)
    outputs: dict[str, dict[str, str]] = Field(default_factory=dict)


class GetTraceParams(BaseModel):
    run: str


class TraceStep(BaseModel):
    node: str
    status: str
    detail: dict = Field(default_factory=dict)


class GetTraceResult(BaseModel):
    run: str
    steps: list[TraceStep] = Field(default_factory=list)


class FeedbackParams(BaseModel):
    run: str
    correction: str


class FeedbackResult(BaseModel):
    run: str
    accepted: bool = True


# ─────────────────────────────────────────────────────────────────────────────
# surfaced decisions — non-blocking (D4/D7)
# ─────────────────────────────────────────────────────────────────────────────
class SurfacedItem(BaseModel):
    id: str
    prompt: str
    choices: list[str] = Field(default_factory=list)


class ListSurfacedParams(BaseModel):
    """No params."""


class ListSurfacedResult(BaseModel):
    items: list[SurfacedItem] = Field(default_factory=list)


class ResolveSurfacedParams(BaseModel):
    id: str
    choice: str


class ResolveSurfacedResult(BaseModel):
    id: str
    resolved: bool = True
    choice: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# The registry — verb-name -> ToolSpec
# ─────────────────────────────────────────────────────────────────────────────
class ToolAnnotations(BaseModel):
    """Honest safety hints — feed governance (S7/D4). Mark destructive ones truly.

    Invariant: a verb is never both readonly and destructive (a read changes nothing).
    """
    readonly: bool = False
    destructive: bool = False
    idempotent: bool = False

    def model_post_init(self, __ctx) -> None:
        if self.readonly and self.destructive:
            # Fail loud — an incoherent annotation would mislead governance.
            raise ValueError("annotation cannot be both readonly and destructive")


class ToolSpec(BaseModel):
    # params/result are classes, not instances — allow arbitrary types.
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    params_model: type[BaseModel]
    result_model: type[BaseModel]
    summary: str
    annotations: ToolAnnotations

    def model_post_init(self, __ctx) -> None:
        # Fail loud on a misregistered tool rather than at call time.
        if not issubclass(self.params_model, BaseModel):
            raise TypeError(f"{self.name}: params_model must be a BaseModel subclass")
        if not issubclass(self.result_model, BaseModel):
            raise TypeError(f"{self.name}: result_model must be a BaseModel subclass")


def _spec(name, params, result, summary, *, readonly=False,
          destructive=False, idempotent=False) -> ToolSpec:
    return ToolSpec(
        name=name,
        params_model=params,
        result_model=result,
        summary=summary,
        annotations=ToolAnnotations(
            readonly=readonly, destructive=destructive, idempotent=idempotent),
    )


TOOLS: dict[str, ToolSpec] = {
    # introspection — pure reads
    "GetTypeGraph": _spec(
        "GetTypeGraph", GetTypeGraphParams, GetTypeGraphResult,
        "Return the type-graph: all node-types and their extends relations (C2/S4).",
        readonly=True, idempotent=True),
    "ListByType": _spec(
        "ListByType", ListByTypeParams, ListByTypeResult,
        "List node instances of a given type across the system.",
        readonly=True, idempotent=True),
    "ObjectInfo": _spec(
        "ObjectInfo", ObjectInfoParams, ObjectInfoResult,
        "The /object_info projection (C5) for a node or type — the UI's own view.",
        readonly=True, idempotent=True),
    "Search": _spec(
        "Search", SearchParams, SearchResult,
        "Free-text search across types, nodes, sources and runs.",
        readonly=True, idempotent=True),

    # sources
    "ListSources": _spec(
        "ListSources", ListSourcesParams, ListSourcesResult,
        "List registered sources and their state.",
        readonly=True, idempotent=True),
    "RegisterSource": _spec(
        "RegisterSource", RegisterSourceParams, RegisterSourceResult,
        "Register a new source from a spec. Additive — does not touch existing data."),
    "SurveySource": _spec(
        "SurveySource", SurveySourceParams, SurveySourceResult,
        "Survey what a registered source contains (read-only inspection).",
        readonly=True, idempotent=True),

    # graphs / compositions
    "ListGraphs": _spec(
        "ListGraphs", ListGraphsParams, ListGraphsResult,
        "List graphs (compositions) and a summary of each.",
        readonly=True, idempotent=True),
    "CreateNode": _spec(
        "CreateNode", CreateNodeParams, CreateNodeResult,
        "Create a node of ANY type in a graph (generic — consults the C2 registry)."),
    "Connect": _spec(
        "Connect", ConnectParams, ConnectResult,
        "Connect two nodes by an edge (port -> port)."),
    "SetConfig": _spec(
        "SetConfig", SetConfigParams, SetConfigResult,
        "Set a node's config (generic over type — the inspector's edit).",
        idempotent=True),
    "DeleteNode": _spec(
        "DeleteNode", DeleteNodeParams, DeleteNodeResult,
        "Delete a node from its graph. DESTRUCTIVE — removes the record.",
        destructive=True, idempotent=True),
    "ValidateGraph": _spec(
        "ValidateGraph", ValidateGraphParams, ValidateGraphResult,
        "Validate a graph against the type contracts; report issues.",
        readonly=True, idempotent=True),

    # runs — live controls (D1)
    "RunGraph": _spec(
        "RunGraph", RunGraphParams, RunGraphResult,
        "Run a graph; returns a run handle to watch/control."),
    "WatchRun": _spec(
        "WatchRun", WatchRunParams, WatchRunResult,
        "Snapshot a run's live status (per-node).",
        readonly=True, idempotent=True),
    "PauseRun": _spec(
        "PauseRun", PauseRunParams, PauseRunResult,
        "Pause a running graph.",
        idempotent=True),
    "Retry": _spec(
        "Retry", RetryParams, RetryResult,
        "Retry a run, or a single node within it."),
    "BranchRun": _spec(
        "BranchRun", BranchRunParams, BranchRunResult,
        "Fork a run with config changes — explore an alternative without losing the original."),
    "Reprioritise": _spec(
        "Reprioritise", ReprioritiseParams, ReprioritiseResult,
        "Change a run's scheduling priority.",
        idempotent=True),

    # results
    "GetResults": _spec(
        "GetResults", GetResultsParams, GetResultsResult,
        "Get a run's output addresses (per node, per port).",
        readonly=True, idempotent=True),
    "GetTrace": _spec(
        "GetTrace", GetTraceParams, GetTraceResult,
        "Get a run's execution trace (per-step detail).",
        readonly=True, idempotent=True),
    "Feedback": _spec(
        "Feedback", FeedbackParams, FeedbackResult,
        "Submit a correction against a run (steers re-runs / learning)."),

    # surfaced decisions — non-blocking (D4/D7)
    "ListSurfaced": _spec(
        "ListSurfaced", ListSurfacedParams, ListSurfacedResult,
        "List decisions the system surfaced for a human/agent choice.",
        readonly=True, idempotent=True),
    "ResolveSurfaced": _spec(
        "ResolveSurfaced", ResolveSurfacedParams, ResolveSurfacedResult,
        "Resolve a surfaced decision by choosing an option.",
        idempotent=True),
}


# ─────────────────────────────────────────────────────────────────────────────
# Public verb names alias their params model — so an agent (and the self-check)
# refers to a verb by its name, e.g. `CreateNode(graph=..., type=...)`. The result
# type lives on the ToolSpec (`TOOLS["CreateNode"].result_model`).
# ─────────────────────────────────────────────────────────────────────────────
CreateNode = CreateNodeParams
Connect = ConnectParams
SetConfig = SetConfigParams
DeleteNode = DeleteNodeParams
ValidateGraph = ValidateGraphParams
ListByType = ListByTypeParams
ObjectInfo = ObjectInfoParams
Search = SearchParams
GetTypeGraph = GetTypeGraphParams
ListSources = ListSourcesParams
RegisterSource = RegisterSourceParams
SurveySource = SurveySourceParams
ListGraphs = ListGraphsParams
RunGraph = RunGraphParams
WatchRun = WatchRunParams
PauseRun = PauseRunParams
Retry = RetryParams
BranchRun = BranchRunParams
Reprioritise = ReprioritiseParams
GetResults = GetResultsParams
GetTrace = GetTraceParams
Feedback = FeedbackParams
ListSurfaced = ListSurfacedParams
ResolveSurfaced = ResolveSurfacedParams


# ─────────────────────────────────────────────────────────────────────────────
# self-check — verbs are a generic kernel; annotations are honest; schemas typed.
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # 1) A generic verb instantiates and validates for ANY type.
    cn = CreateNode(graph="demo", type="extract")
    assert isinstance(cn, CreateNodeParams)
    assert cn.config == {}                          # default carried (schema-additive)
    CreateNodeParams.model_validate(cn.model_dump())  # round-trips
    print(f"[ok] CreateNode(graph='demo', type='extract') validates -> {cn.model_dump()}")

    # 2) Every registered tool has typed params + result models and honest annotations.
    for name, spec in TOOLS.items():
        assert spec.name == name, f"{name}: registry key != spec.name ({spec.name})"
        assert isinstance(spec.params_model, type) and issubclass(spec.params_model, BaseModel), \
            f"{name}: params_model is not a BaseModel subclass"
        assert isinstance(spec.result_model, type) and issubclass(spec.result_model, BaseModel), \
            f"{name}: result_model is not a BaseModel subclass"
        a = spec.annotations
        # honest = coherent: never both readonly and destructive.
        assert not (a.readonly and a.destructive), f"{name}: readonly AND destructive"
    print(f"[ok] {len(TOOLS)} verbs: each has BaseModel params_model + result_model")

    # 3) Annotation honesty is specific, not vacuous.
    assert TOOLS["DeleteNode"].annotations.destructive is True, "DeleteNode must be destructive"
    assert TOOLS["DeleteNode"].annotations.readonly is False
    for read_verb in ("GetTypeGraph", "ListByType", "ObjectInfo", "Search",
                      "ListSources", "SurveySource", "ListGraphs", "ValidateGraph",
                      "WatchRun", "GetResults", "GetTrace", "ListSurfaced"):
        assert TOOLS[read_verb].annotations.readonly is True, f"{read_verb} should be readonly"
        assert TOOLS[read_verb].annotations.destructive is False
    print("[ok] DeleteNode destructive; reads readonly — annotations honest")

    # 4) NO per-node-type tool. The kernel is generic; type is a PARAMETER, not a verb.
    #    Representative type names from the spec must never appear as (part of) a verb.
    forbidden_types = ("extract", "document", "annotation", "summarize")
    for verb in TOOLS:
        low = verb.lower()
        for t in forbidden_types:
            assert t not in low, f"per-type tool leaked: '{verb}' contains type '{t}'"
    # Proof that type is a parameter: CreateNode exposes `type` as a plain str field.
    type_field = CreateNodeParams.model_fields["type"]
    assert type_field.annotation is str, "CreateNode.type must be a generic str parameter"
    # And a fresh, never-before-seen type works with the SAME verb — zero new tools.
    CreateNode(graph="demo", type="a_type_invented_tomorrow")
    print(f"[ok] no per-node-type tool; type is a generic str param "
          f"(verified types {forbidden_types} absent from {len(TOOLS)} verbs)")

    print(f"\nALL CHECKS PASSED — C7 tool surface v{SCHEMA_VER}: "
          f"{len(TOOLS)} generic verbs.")
