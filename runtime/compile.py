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
    """The logical run-address of a node's output (the node-level base address).

    `run://<graph.id>/<node>` on the default branch; `…@<branch>` otherwise.
    Main stays branchless so existing addresses/tests are unchanged (schema-additive).
    """
    return f"run://{graph_id}/{node_id}" if branch == "main" else f"run://{graph_id}/{node_id}@{branch}"


def _declared_out_ports(inst, node_types) -> list[str]:
    """The output ports this node DECLARES.

    Source of truth = the node-type's `PORTS_OUT` (C2), the same registry the
    scheduler reads — NOT `inst.outputs`, which is empty at compile time on a
    freshly-built graph ("filled by runtime", C3). When `node_types` isn't
    supplied (the compile self-check), fall back to `inst.outputs.keys()` so the
    existing behaviour is byte-identical.
    """
    if node_types is not None and inst.type in node_types:
        ports = list(getattr(node_types[inst.type], "PORTS_OUT", {}).keys())
        if ports:
            return ports
    return list(inst.outputs.keys())


def compile(graph: Graph, branch: str = "main", node_types=None) -> list[ExecNode]:
    """Compile a workflow `Graph` into a list of `ExecNode`s.

    For each node: drop position/size/render_state/layer (stripped by
    construction — `ExecNode` has no such fields), carry `config`, and give each
    declared output port its OWN address:
      - a **single-output** node keeps the bare node-level form, under the
        uniform port key `"out"`: `outputs = {"out": run://<graph>/<node>}`
        (unchanged — the self-check + every single-output test still hold).
      - a **multi-output** node (>= 2 declared ports) gets a per-port fragment
        address each: `outputs = {p: run://<graph>/<node>#<p>}`. Each port is a
        DISTINCT store key, so writing one branch leaves the others unresolved
        (branch-not-taken = address simply never written). Schema-additive.

    For each edge: turn the wire into an ADDRESS reference — the target node's
    `inputs[to_port]` points at the SOURCE PORT's address (read straight off the
    source ExecNode's `outputs`, so compile and the scheduler agree by
    construction). `from_port` selects which port-address feeds downstream; the
    `"out"` fallback keeps single-output edges resolving to the bare address.

    Fail loud (rule 4): an edge referencing a node not in the graph raises.
    """
    node_ids = {n.id for n in graph.nodes}

    execs: list[ExecNode] = []
    by_id: dict[str, ExecNode] = {}
    for inst in graph.nodes:
        base = _addr(graph.id, inst.id, branch)
        declared = _declared_out_ports(inst, node_types)
        if len(declared) >= 2:
            # Multi-output: per-port fragment address, each a distinct store key.
            outputs = {port: f"{base}#{port}" for port in declared}
        else:
            # Single-output (incl. the default fallback): the bare node address
            # under the uniform "out" key — unchanged from the original form.
            outputs = {"out": base}
        exec_node = ExecNode(
            id=inst.id,
            type=inst.type,
            config=inst.config,
            inputs={},
            outputs=outputs,
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
        # The wire becomes an address reference, read straight off the source
        # ExecNode's computed outputs so compile and the scheduler agree by
        # construction. `from_port` selects the source port; single-output nodes
        # carry only "out", so the .get("out") fallback resolves them to the
        # bare node address (e.g. constant's "value" port -> run://demo/src).
        src_out = by_id[edge.from_node].outputs
        src_addr = src_out.get(edge.from_port) or src_out.get("out") or next(iter(src_out.values()))
        by_id[edge.to_node].inputs[edge.to_port] = src_addr

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
