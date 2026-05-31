"""C5 (Part 2) — `compile`: workflow → execution.

The C3 "two-graph split" in code. The WORKFLOW face (`Graph` of `NodeInstance`s
with pixels/wires) becomes the EXECUTION face (`ExecNode`s with addresses). The
runtime recompiles each run, so the editable face and the runnable face never
drift. See build-prep/contracts/C5.

Generic over node-type (rule 3 / the runtime constitution): compile gains
nothing per node-type — a new node-type needs no change here.

Addresses use the LOGICAL run-address form `run://<graph.id>/<node>`. This is
deliberately the exact form `scheduler.run()` builds for `logical_of` — the
execution face and the scheduler's resolution agree by construction. (It is the
node-level logical pointer; the `@branch` / `#run=` segments from C1's full
grammar are not part of this seam.)
"""
from __future__ import annotations

from contracts.node_record import Graph, ExecNode


def _addr(graph_id: str, node_id: str, branch: str = "main") -> str:
    """The logical run-address of a node's output.

    `run://<graph.id>/<node>` on the default branch; `…@<branch>` otherwise.
    Main stays branchless so existing addresses/tests are unchanged (schema-additive).
    """
    return f"run://{graph_id}/{node_id}" if branch == "main" else f"run://{graph_id}/{node_id}@{branch}"


def compile(graph: Graph, branch: str = "main") -> list[ExecNode]:
    """Compile a workflow `Graph` into a list of `ExecNode`s.

    For each node: drop position/size/render_state/layer (stripped by
    construction — `ExecNode` has no such fields), carry `config`, and set
    `outputs[port] = run://<graph.id>/<node.id>` per the node's declared output
    ports (its `outputs` keys) if any, else a single default port `"out"`.

    For each edge: turn the wire into an ADDRESS reference — the target node's
    `inputs[to_port]` points at the source node's logical address.

    Fail loud (rule 4): an edge referencing a node not in the graph raises.
    """
    node_ids = {n.id for n in graph.nodes}

    execs: list[ExecNode] = []
    by_id: dict[str, ExecNode] = {}
    for inst in graph.nodes:
        # Declared output ports if available, else a default "out".
        out_ports = list(inst.outputs.keys()) or ["out"]
        addr = _addr(graph.id, inst.id, branch)
        exec_node = ExecNode(
            id=inst.id,
            type=inst.type,
            config=inst.config,
            inputs={},
            outputs={port: addr for port in out_ports},
        )
        execs.append(exec_node)
        by_id[inst.id] = exec_node

    for edge in graph.edges:
        if edge.from_node not in node_ids:
            raise ValueError(
                f"compile: edge from unknown node {edge.from_node!r} "
                f"(graph {graph.id!r}) — dangling wire"
            )
        if edge.to_node not in node_ids:
            raise ValueError(
                f"compile: edge to unknown node {edge.to_node!r} "
                f"(graph {graph.id!r}) — dangling wire"
            )
        # The wire becomes an address reference: the target reads from the
        # source node's logical output address.
        by_id[edge.to_node].inputs[edge.to_port] = _addr(graph.id, edge.from_node, branch)

    return execs


if __name__ == "__main__":
    # Self-check (C5): a 2-node graph, constant -> uppercase, one edge.
    import json

    from contracts.node_record import Graph, NodeInstance, Edge
    from contracts.node_type import NodeType, Ports
    from contracts.object_info import build_object_info

    GID = "demo"
    g = Graph(
        id=GID,
        nodes=[
            NodeInstance(id="src", type="constant", config={"value": "hello"}),
            NodeInstance(id="up", type="uppercase"),
        ],
        edges=[Edge(from_node="src", from_port="value", to_node="up", to_port="text")],
    )

    execs = compile(g)
    assert len(execs) == 2, f"expected 2 ExecNodes, got {len(execs)}"

    up = next(e for e in execs if e.id == "up")
    src = next(e for e in execs if e.id == "src")

    expected_in = f"run://{GID}/src"
    assert up.inputs["text"] == expected_in, (
        f"uppercase input should reference {expected_in!r}, got {up.inputs!r}"
    )

    # config carried through
    assert src.config == {"value": "hello"}, f"config not carried: {src.config!r}"

    # outputs default to "out" -> the node's own logical address
    assert src.outputs == {"out": f"run://{GID}/src"}, f"bad outputs: {src.outputs!r}"
    assert up.outputs == {"out": f"run://{GID}/up"}, f"bad outputs: {up.outputs!r}"

    # build_object_info over one NodeType -> JSON-serializable dict
    nt = NodeType(
        name="uppercase",
        category="text",
        kind="process",
        ports=Ports(inputs={"text": "Text"}, outputs={"text": "Text"}),
        config_schema={"casing": {"type": "string"}},
        output_schema={"type": "Text"},
        actions=["run"],
        version=1,
    )
    info = build_object_info({"uppercase": nt})
    serialized = json.dumps(info)  # proves JSON-serializable (not just isinstance dict)
    assert "uppercase" in info, "object_info missing the entry"
    entry = info["uppercase"]
    assert entry["title"] == "Uppercase", f"bad title: {entry['title']!r}"
    assert entry["ports"] == {"inputs": {"text": "Text"}, "outputs": {"text": "Text"}}, (
        f"ports not serialized to plain dict: {entry['ports']!r}"
    )
    assert entry["version"] == 1

    print("SELF-CHECK PASS")
    print("  compile -> 2 ExecNodes; uppercase.inputs['text'] =", up.inputs["text"])
    print("  src.config =", src.config, "; src.outputs =", src.outputs)
    print("  object_info(uppercase).keys =", sorted(entry.keys()))
    print("  json length =", len(serialized))
