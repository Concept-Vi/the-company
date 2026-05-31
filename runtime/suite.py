"""runtime/suite.py — the shared brain (the composition suite's core operations).

ONE brain, two faces: the UI bridge and the MCP server both call this. Graphs live in
the addressed store (S3 graphs registry), so the faces operate the SAME substrate even in
separate processes. Operations are the C7 generic verbs — generic over node-type
(they consult the registry), never one-per-type.
"""
from __future__ import annotations

from contracts.node_record import NodeInstance, Edge, Graph
from runtime import scheduler
from runtime.registry import NodeRegistry
from store.fs_store import FsStore

CONTENT_KINDS = ("constant", "document", "code", "file", "image", "source", "portal")


class Suite:
    def __init__(self, store: FsStore, registry: NodeRegistry):
        self.store = store
        self.registry = registry

    # --- introspection (reads) ---
    def list_types(self) -> list[str]:
        return sorted(self.registry.types)

    def object_info(self) -> dict:
        return self.registry.object_info()

    def list_by_type(self, output_type: str) -> list[str]:
        return self.registry.produces(output_type)

    def list_graphs(self) -> list[str]:
        return self.store.list_graphs()

    # --- graph building (generic over node-type) ---
    def _load(self, graph_id: str) -> Graph:
        return self.store.load_graph(graph_id) or Graph(id=graph_id)

    def create_node(self, graph_id: str, type: str, config: dict | None = None,
                    node_id: str | None = None) -> str:
        if type not in self.registry:
            raise KeyError(f"unknown node-type {type!r} (have: {self.list_types()})")
        g = self._load(graph_id)
        nid = node_id or f"{type}-{len(g.nodes) + 1}"
        g.nodes.append(NodeInstance(id=nid, type=type, config=config or {}))
        self.store.save_graph(g)
        return nid

    def connect(self, graph_id: str, from_node: str, from_port: str,
                to_node: str, to_port: str) -> None:
        g = self._load(graph_id)
        g.edges.append(Edge(from_node=from_node, from_port=from_port,
                            to_node=to_node, to_port=to_port))
        self.store.save_graph(g)

    def set_config(self, graph_id: str, node_id: str, config: dict) -> None:
        g = self._load(graph_id)
        for n in g.nodes:
            if n.id == node_id:
                n.config.update(config)
                self.store.save_graph(g)
                return
        raise KeyError(f"no node {node_id!r} in graph {graph_id!r}")

    def save_graph(self, graph: Graph) -> None:
        self.store.save_graph(graph)

    # --- run + read ---
    def run(self, graph_id: str, branch: str = "main", pause=None, force=None) -> dict:
        return scheduler.run(self._load(graph_id), self.store, self.registry,
                             branch=branch, pause=pause, force=force)

    def state(self, graph_id: str, result: dict | None = None, branch: str = "main") -> dict:
        g = self._load(graph_id)
        nodes = []
        for n in g.nodes:
            logical = f"run://{g.id}/{n.id}" if branch == "main" else f"run://{g.id}/{n.id}@{branch}"
            cas = self.store.head(logical)
            status = "idle"
            if result:
                status = ("ran" if n.id in result["ran"]
                          else "cached" if n.id in result["skipped"] else "idle")
            nodes.append({
                "id": n.id, "type": n.type, "config": n.config,
                "kind": "content" if n.type in CONTENT_KINDS else "process",
                "status": status, "address": logical, "content_hash": cas,
                "output": self.store.get_content(cas) if cas else None,
            })
        return {"id": g.id, "nodes": nodes,
                "edges": [{"from": e.from_node, "to": e.to_node} for e in g.edges]}

    def results(self, graph_id: str) -> dict:
        st = self.state(graph_id)
        return {n["id"]: n["output"] for n in st["nodes"]}
