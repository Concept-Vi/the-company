"""C8 — bridge message models (Pydantic). See build-prep/contracts/C8.

The TYPED MESSAGE MODELS for the canvas <-> runtime bridge. NOT the transport
(a minimal http bridge already lives at runtime/bridge.py). Two channels:

  STATE channel  — the live shared document pushed to the canvas:
                   GraphState { nodes: [NodeState], edges }.
  ACTION channel — request/response of the C7 verbs:
                   ActionRequest -> ActionResponse (errors fail LOUD).

One source: status reuses C3's `Status` (imported, not redefined). NodeState /
GraphState are deliberately a flat *projection* for the canvas — distinct from
C3's NodeInstance / Graph, not a duplicate of them.

Schema-additive: add optional fields + bump schema_ver; never break an existing one.
"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field

from contracts.node_record import Status   # one source — C3 owns the status set


# ── ACTION channel — request/response of the C7 verbs ────────────────────────
class ActionRequest(BaseModel):
    id: str                                          # correlates request <-> response
    verb: str                                        # a C7 verb: run · pause · retry · …
    params: dict = Field(default_factory=dict)
    schema_ver: int = 1


class ActionResponse(BaseModel):
    id: str                                          # echoes the request id
    ok: bool                                         # True = success, False = failure
    result: Any | None = None                        # present on success
    error: str | None = None                         # present on failure — fail LOUD, never silent
    schema_ver: int = 1


# ── STATE channel — the live shared document pushed to the canvas ────────────
class NodeState(BaseModel):                          # flat projection of a node for the canvas
    id: str
    type: str                                        # -> NodeType.name (C2)
    status: Status                                   # C3's status set (imported, not redefined)
    address: str | None = None                       # run:// pointer for this node (C1)
    content_hash: str | None = None                  # cas:// — integrity + dedup (C1)
    output: Any | None = None                        # partial / final output value
    config: dict = Field(default_factory=dict)
    schema_ver: int = 1


class GraphState(BaseModel):                         # what the state channel pushes to the canvas
    id: str
    nodes: list[NodeState] = Field(default_factory=list)
    edges: list[dict] = Field(default_factory=list)
    schema_ver: int = 1


# ── helpers — build a loud, well-formed response ─────────────────────────────
def ok(id: str, result: Any) -> ActionResponse:
    """Success response for request `id` carrying `result`."""
    return ActionResponse(id=id, ok=True, result=result, error=None)


def err(id: str, message: str) -> ActionResponse:
    """Failure response for request `id` — surfaces `message` (no silent failures)."""
    return ActionResponse(id=id, ok=False, result=None, error=message)


if __name__ == "__main__":
    # ── ACTION request round-trip ──
    req = ActionRequest(id="1", verb="run", params={"graph": "demo"})
    req2 = ActionRequest.model_validate_json(req.model_dump_json())
    assert req2.id == "1"
    assert req2.verb == "run"
    assert req2.params == {"graph": "demo"}

    # ── err response round-trip (failure must survive the wire) ──
    e = err("1", "boom")
    e2 = ActionResponse.model_validate_json(e.model_dump_json())
    assert e2.id == "1"
    assert e2.ok is False
    assert e2.error == "boom"
    assert e2.result is None

    # ── ok response round-trip ──
    o = ok("1", {"run": "run://demo/n1@main#run=42"})
    o2 = ActionResponse.model_validate_json(o.model_dump_json())
    assert o2.id == "1"
    assert o2.ok is True
    assert o2.error is None
    assert o2.result == {"run": "run://demo/n1@main#run=42"}

    # ── STATE channel: GraphState with one NodeState ──
    gs = GraphState(
        id="demo",
        nodes=[
            NodeState(
                id="n1",
                type="prompt",
                status="ran",
                address="run://demo/n1@main#run=42",
                content_hash="cas://sha256:abc",
                output={"text": "hello"},
                config={"model": "qwen"},
            )
        ],
        edges=[{"from_node": "n1", "from_port": "out", "to_node": "n2", "to_port": "in"}],
    )
    gs2 = GraphState.model_validate_json(gs.model_dump_json())
    assert gs2.id == "demo"
    assert len(gs2.nodes) == 1
    assert gs2.nodes[0].id == "n1"
    assert gs2.nodes[0].status == "ran"
    assert gs2.nodes[0].address == "run://demo/n1@main#run=42"
    assert gs2.nodes[0].output == {"text": "hello"}
    assert gs2.edges[0]["to_node"] == "n2"

    print("OK — bridge_msgs self-check passed (ActionRequest, ok/err, GraphState round-trips)")
