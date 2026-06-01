"""runtime/suite.py — the shared brain (the composition suite's core operations).

ONE brain, two faces: the UI bridge and the MCP server both call this. Graphs live in
the addressed store (S3 graphs registry), so the faces operate the SAME substrate even in
separate processes. Operations are the C7 generic verbs — generic over node-type
(they consult the registry), never one-per-type.
"""
from __future__ import annotations
import os

from contracts.node_record import NodeInstance, Edge, Graph
from runtime import scheduler
from runtime.governance import Inbox, GovernanceError
from runtime.registry import NodeRegistry
from store.fs_store import FsStore

CONTENT_KINDS = ("constant", "document", "code", "file", "image", "source", "portal")


def _tag_system_origin(code: str) -> str:
    """Tag a brain-written node module with its provenance layer. Idempotent — the canvas
    reads ORIGIN to show "what a role changed" (context-13 layers)."""
    if "ORIGIN" in code:
        return code
    return "ORIGIN = 'system'  # brain-written (self-grown) — provenance layer\n" + code


def _strip_fences(code: str) -> str:
    c = code.strip()
    if c.startswith("```"):
        inner = c[3:]
        c = inner.split("```", 1)[0] if "```" in inner else inner.strip("`")
        if c.lstrip().startswith("python"):
            c = c.lstrip()[len("python"):]
    return c.strip()


class Suite:
    def __init__(self, store: FsStore, registry: NodeRegistry, nodes_dir: str | None = None):
        self.store = store
        self.registry = registry
        self.inbox = Inbox(store)
        self.nodes_dir = nodes_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes")

    def _emit(self, kind: str, summary: str, **meta) -> None:
        """Append one event to the captured trajectory (I2). Never breaks the action it records."""
        try:
            self.store.append_event({"kind": kind, "summary": summary, **meta})
        except Exception:
            pass

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
        self._emit("create", f"+ {type} node ({nid})", graph=graph_id, node=nid, type=type)
        return nid

    def connect(self, graph_id: str, from_node: str, from_port: str,
                to_node: str, to_port: str) -> None:
        g = self._load(graph_id)
        byid = {n.id: n for n in g.nodes}
        if from_node not in byid or to_node not in byid:
            raise KeyError(f"connect: unknown node ({from_node!r} -> {to_node!r})")
        ft = self.registry.types.get(byid[from_node].type)
        tt = self.registry.types.get(byid[to_node].type)
        out_t = ft.ports.outputs.get(from_port) if ft else None
        in_t = tt.ports.inputs.get(to_port) if tt else None
        if out_t and in_t and "Any" not in (out_t, in_t) and out_t != in_t:   # type-check, fail loud
            raise ValueError(
                f"type mismatch: {from_node}.{from_port}:{out_t} → {to_node}.{to_port}:{in_t}")
        g.edges.append(Edge(from_node=from_node, from_port=from_port,
                            to_node=to_node, to_port=to_port))
        self.store.save_graph(g)
        self._emit("connect", f"wired {from_node}.{from_port} → {to_node}.{to_port}",
                   graph=graph_id, from_node=from_node, to_node=to_node)

    def delete_node(self, graph_id: str, node_id: str) -> None:
        g = self._load(graph_id)
        g.nodes = [n for n in g.nodes if n.id != node_id]
        g.edges = [e for e in g.edges if e.from_node != node_id and e.to_node != node_id]
        self.store.save_graph(g)
        self._emit("delete", f"removed node {node_id}", graph=graph_id, node=node_id)

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
        r = scheduler.run(self._load(graph_id), self.store, self.registry,
                          branch=branch, pause=pause, force=force)
        self._emit("run", f"ran {len(r['ran'])}, cached {len(r['skipped'])}"
                   + (f", stuck {len(r['stuck'])}" if r.get("stuck") else ""),
                   graph=graph_id, ran=sorted(r["ran"]), cached=sorted(r["skipped"]),
                   stuck=sorted(r.get("stuck", [])))
        return r

    def state(self, graph_id: str, result: dict | None = None, branch: str = "main") -> dict:
        g = self._load(graph_id)
        nodes = []
        for n in g.nodes:
            logical = f"run://{g.id}/{n.id}" if branch == "main" else f"run://{g.id}/{n.id}@{branch}"
            mod = self.registry.get(n.type)
            if getattr(mod, "RESOLVE", "compute") == "reference":
                # live window: resolve the referenced address NOW (window, not a copy)
                ref = n.config.get("ref") or ""
                cas = self.store.head(ref) if ref else None
            else:
                cas = self.store.head(logical)
            status = "idle"
            if result:
                status = ("ran" if n.id in result["ran"]
                          else "cached" if n.id in result["skipped"] else "idle")
            nt = self.registry.types.get(n.type)
            nodes.append({
                "id": n.id, "type": n.type, "config": n.config,
                "kind": nt.kind if nt else ("content" if n.type in CONTENT_KINDS else "process"),
                "layer": getattr(mod, "ORIGIN", "authored"),   # provenance layer (authored vs system)
                "status": status, "address": logical, "content_hash": cas,
                "output": self.store.get_content(cas) if cas else None,
            })
        return {"id": g.id, "nodes": nodes,
                "edges": [{"from": e.from_node, "to": e.to_node} for e in g.edges]}

    def results(self, graph_id: str) -> dict:
        st = self.state(graph_id)
        return {n["id"]: n["output"] for n in st["nodes"]}

    # --- the operator surfaces (I2): now-view · presence · event log ---
    def events(self, limit: int = 60) -> list:
        return self.store.recent_events(limit)

    def now(self, graph_id: str) -> dict:
        """The now-view + presence snapshot — derived live from state, the inbox, and the log."""
        st = self.state(graph_id)
        nodes = st["nodes"]
        resolved = [n for n in nodes if n["content_hash"]]
        pending = [d for d in self.inbox.list() if d.get("resolved") is None]
        recent = self.store.recent_events(1)
        if pending:
            presence = "awaiting your approval"
        elif nodes and len(resolved) == len(nodes):
            presence = "ready · all resolved"
        elif nodes:
            presence = "ready · work unresolved"
        else:
            presence = "empty"
        return {
            "graph": st["id"],
            "nodes_total": len(nodes),
            "nodes_resolved": len(resolved),
            "surfaced_pending": len(pending),
            "presence": presence,
            "last_event": recent[0] if recent else None,
        }

    # --- the right-hand-man: the coherent voice of the Company about ITSELF (I2) ---
    def _chat_context(self, graph_id: str) -> str:
        """Compact GROUND TRUTH — live system state, not the codebase (context-05 rung 1)."""
        nowv = self.now(graph_id)
        st = self.state(graph_id)
        nodes = "; ".join(
            f"{n['id']}({n['type']}, {'resolved' if n['content_hash'] else 'unresolved'})"
            for n in st["nodes"]) or "(none)"
        evs = "; ".join(f"{e['kind']}: {e['summary']}" for e in self.store.recent_events(6)) or "(none)"
        return (
            "LIVE SYSTEM STATE (ground truth — answer only from this):\n"
            f"- graph: {nowv['graph']} · {nowv['nodes_total']} nodes, {nowv['nodes_resolved']} resolved"
            f" · {nowv['surfaced_pending']} awaiting approval · presence: {nowv['presence']}\n"
            f"- nodes: {nodes}\n"
            f"- available node-types: {', '.join(self.list_types())}\n"
            f"- recent activity: {evs}\n"
        )

    def chat(self, message: str, graph_id: str) -> dict:
        """Grounded conversation with the operator. Answers from compact ground truth; never
        confabulates system facts. Suggests actions but performs none that skip the surfaced
        gate (E6 invariant) — proposing/running route through the normal verbs."""
        from fabric import client, transport, config as fcfg
        sys_p = (
            "You are the right-hand-man — the coherent voice of the Company, speaking to its operator "
            "about the system ITSELF. Answer ONLY from the LIVE SYSTEM STATE below; it is ground truth. "
            "If something is not in that state, say you cannot see it — NEVER invent counts, names, or "
            "facts. Be concise and concrete. You may suggest actions (grow a node, run the graph) but you "
            "never perform irreversible actions yourself; those are surfaced for the operator's approval."
        )
        msgs = [{"role": "system", "content": sys_p + "\n\n" + self._chat_context(graph_id)}]
        for t in self.store.chat_history(20):
            msgs.append({"role": t["role"], "content": t["text"]})
        msgs.append({"role": "user", "content": message})
        reply = client.complete(transport.openai_transport(base_url=fcfg.DEFAULT_BASE_URL),
                                 msgs, model=fcfg.DEFAULT_BRAIN)
        self.store.append_chat({"role": "user", "text": message})
        self.store.append_chat({"role": "assistant", "text": reply})
        self._emit("chat", f"you: {message[:48]}")
        return {"reply": reply, "history": self.store.chat_history(40)}

    def chat_history(self, limit: int = 40) -> list:
        return self.store.chat_history(limit)

    # --- self-growth: build-dispatch (the "direct its growth" half of the first purpose) ---
    @staticmethod
    def _safe_node_name(name: str) -> str:
        if not isinstance(name, str) or not name.isidentifier() or name.startswith("_"):
            raise ValueError(f"unsafe node name {name!r} — must be a plain identifier (no paths, no '_'-prefix)")
        return name

    def propose_node(self, name: str, spec: str, model: str | None = None) -> dict:
        """The agent asks the brain to WRITE a new node module, then SURFACES it as a CONFIRM
        decision for the operator. It is NOT applied here. Returns {id, name, code}.
        (Proposing is safe — a model call + a surfaced gate; applying needs operator approval.)"""
        self._safe_node_name(name)                          # reject path-traversal up front
        from fabric import client, transport, config as fcfg
        sys_p = ("You write ONE Python node module for the 'company' composition engine. "
                 "Output ONLY raw Python — no prose, no markdown fences.")
        user_p = (
            "Contract: a module with VERSION='1', KIND ('process'|'content'), PORTS_IN dict, "
            "PORTS_OUT dict, and def run(inputs: dict, config: dict) returning the output value.\n\n"
            "Example:\nVERSION='1'\nKIND='process'\nPORTS_IN={'text':'Text'}\nPORTS_OUT={'text':'Text'}\n"
            "def run(inputs, config):\n    return str(inputs.get('text','')).upper()\n\n"
            f"Write a node named '{name}' that: {spec}\n"
            "Use PORTS_IN={'text':'Text'} and PORTS_OUT={'text':'Text'} unless the spec needs otherwise. "
            "Output ONLY the code.")
        t = transport.openai_transport(base_url=fcfg.DEFAULT_BASE_URL)
        code = _tag_system_origin(_strip_fences(client.complete(
            t, [{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}],
            model=model or fcfg.DEFAULT_BRAIN)))
        sid = self.inbox.surface("code_build", {"name": name, "code": code}, default="reject")
        self._emit("grow", f"brain wrote a '{name}' node — surfaced for approval", node_name=name, surfaced=sid)
        return {"id": sid, "name": name, "code": code}

    def apply_node(self, surfaced_id: str) -> str:
        """Apply a proposed node — ONLY if the OPERATOR approved its surfaced decision.
        Authorization is READ from the inbox (resolved=='approve'), never a caller flag, so the
        agent that proposed it cannot self-approve. Writes atomically + re-discovers. (code_build, D7)."""
        d = self.inbox.get(surfaced_id)
        if not d:
            raise KeyError(f"no surfaced decision {surfaced_id!r}")
        if not self.inbox.is_approved(surfaced_id):
            raise GovernanceError(
                f"code_build {surfaced_id!r} not approved — operator must resolve it 'approve' first (CONFIRM)")
        name = self._safe_node_name(d["payload"]["name"])   # re-validate at apply
        code = d["payload"]["code"]
        path = os.path.join(self.nodes_dir, name + ".py")
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(code if code.endswith("\n") else code + "\n")
        os.replace(tmp, path)                               # atomic; no partial file
        self.registry.discover([self.nodes_dir])            # re-discover -> capability is live
        self._emit("apply", f"approved + applied '{name}' — now a live node-type", node_name=name)
        return path

    # --- surfaced-decision inbox (D4/D7) ---
    def list_surfaced(self) -> list:
        return self.inbox.list()

    def resolve_surfaced(self, sid: str, choice: str) -> None:
        """OPERATOR-only (UI channel) — NOT exposed on the MCP face, so the agent can't self-approve."""
        self.inbox.resolve(sid, choice)
        self._emit("resolve", f"operator {choice}d {sid}", surfaced=sid, choice=choice)
