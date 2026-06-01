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
        mode = self.get_mode()
        return {
            "graph": st["id"],
            "nodes_total": len(nodes),
            "nodes_resolved": len(resolved),
            "surfaced_pending": len(pending),
            "presence": "off" if mode == "off" else presence,
            "mode": mode,
            "last_event": recent[0] if recent else None,
        }

    # --- modes / the presence dial: the mode IS a node (context-05, D1-D3) ---
    MODES = ("listening", "text-only", "background", "focus",
             "walkthrough", "watch-and-react", "decide-for-me", "off")
    DEFAULT_MODE = "listening"
    SYSTEM_GRAPH = "system"
    MODE_NODE = "rhm"
    MODE_DIRECTIVES = {
        "listening": "Conversational and present; respond fully.",
        "text-only": "Respond in text, concisely, only to what is addressed.",
        "background": "Be minimal — surface only what genuinely needs the operator; otherwise a one-line acknowledgement.",
        "focus": "The operator is in deep work. Be extremely brief (one or two lines); do not elaborate unless asked.",
        "walkthrough": "Actively guide: narrate what you are doing and direct the operator's attention step by step.",
        "watch-and-react": "Observe; comment only when relevant, and briefly.",
        "decide-for-me": "Act on what you confidently can — prefer taking a governed action (propose a node, run the graph) over asking. You still cannot self-approve; proposals are surfaced for approval.",
        "off": "",
    }

    def _rhm_cfg(self) -> dict:
        """The RHM's config node (system graph) — holds mode + model + base_url + persona."""
        g = self.store.load_graph(self.SYSTEM_GRAPH)
        if g:
            for n in g.nodes:
                if n.id == self.MODE_NODE:
                    return dict(n.config)
        return {}

    def _ensure_rhm_node(self) -> None:
        g = self.store.load_graph(self.SYSTEM_GRAPH)
        if not g or not any(n.id == self.MODE_NODE for n in g.nodes):
            self.create_node(self.SYSTEM_GRAPH, "rhm_mode",
                             config={"mode": self.DEFAULT_MODE}, node_id=self.MODE_NODE)

    def get_mode(self) -> str:
        return self._rhm_cfg().get("mode", self.DEFAULT_MODE)

    def set_mode(self, mode: str) -> str:
        if mode not in self.MODES:
            raise ValueError(f"unknown mode {mode!r} — one of {self.MODES}")
        self._ensure_rhm_node()
        self.set_config(self.SYSTEM_GRAPH, self.MODE_NODE, {"mode": mode})   # editing a parameter (same verb)
        self._emit("mode", f"presence → {mode}")
        return mode

    def _mode_directive(self, mode: str) -> str:
        return self.MODE_DIRECTIVES.get(mode, "")

    # --- RHM configs (E1-E2): model/provider + persona, all configurable + persistent ---
    def rhm_config(self) -> dict:
        from fabric import config as fcfg
        c = self._rhm_cfg()
        return {"mode": c.get("mode", self.DEFAULT_MODE),
                "model": c.get("model") or fcfg.DEFAULT_BRAIN,
                "base_url": c.get("base_url") or fcfg.DEFAULT_BASE_URL,
                "persona": c.get("persona", "")}

    def set_rhm_config(self, updates: dict) -> dict:
        allowed = {k: v for k, v in (updates or {}).items()
                   if k in ("model", "base_url", "persona", "mode")}
        if "mode" in allowed and allowed["mode"] not in self.MODES:
            raise ValueError(f"unknown mode {allowed['mode']!r}")
        if not allowed:
            return self.rhm_config()
        self._ensure_rhm_node()
        self.set_config(self.SYSTEM_GRAPH, self.MODE_NODE, allowed)
        self._emit("config", "RHM config → " + ", ".join(f"{k}={v}" for k, v in allowed.items()))
        return self.rhm_config()

    # --- the twin (B1, B3): the explicit model-of-Tim + provenance grading ---
    @staticmethod
    def _provenance_grade(role: str) -> str:
        """Tim's own words are GOLD (the only thing that trains the twin); the twin's output is
        WORKING-grade inference and must never masquerade as ground truth (prevents model-collapse)."""
        return "gold" if role == "user" else "working"

    def _model_of_tim_digest(self, max_chars: int = 2600) -> str:
        """A COMPACT extract of the EXPLICIT model of Tim (principle headers + their statements) for
        the twin's context. The full text is drillable via the model_of_tim node. '' if unavailable."""
        import os
        from nodes import model_of_tim as mot
        path = os.environ.get("COMPANY_MODEL_OF_TIM", mot.DEFAULT_PATH)
        try:
            text = open(path, encoding="utf-8").read()
        except Exception:
            return ""
        lines, out = text.splitlines(), []
        for i, ln in enumerate(lines):
            s = ln.strip()
            if s.startswith("## "):                                   # a principle/law title
                out.append("• " + s[3:].strip())
            elif s.startswith("**") and "**" in s[2:]:                # its bold one-line statement
                out.append("  " + s.strip("*").split("**")[0].strip())
        digest = "\n".join(out)
        return digest[:max_chars]

    def training_signal(self) -> list:
        """Only GOLD turns (Tim's actual words) train the twin — never the twin's own echoes."""
        return [t for t in self.store.chat_history(999) if t.get("grade") == "gold"]

    # --- the right-hand-man: the coherent voice of the Company about ITSELF (I2) ---
    def _chat_context(self, graph_id: str, focus: dict | None = None) -> str:
        """Compact GROUND TRUTH — live system state, not the codebase (context-05 rung 1).
        With `focus` (the operator's current canvas selection), the RHM gains CO-PRESENCE:
        the focused nodes' full detail (output/config) — the shared perceptual field where
        'context is a consequence of what I'm doing' (two planes, one state)."""
        nowv = self.now(graph_id)
        st = self.state(graph_id)
        by = {n["id"]: n for n in st["nodes"]}
        nodes = "; ".join(
            f"{n['id']}({n['type']}, {'resolved' if n['content_hash'] else 'unresolved'})"
            for n in st["nodes"]) or "(none)"
        evs = "; ".join(f"{e['kind']}: {e['summary']}" for e in self.store.recent_events(6)) or "(none)"
        ctx = (
            "LIVE SYSTEM STATE (ground truth — answer only from this):\n"
            f"- graph: {nowv['graph']} · {nowv['nodes_total']} nodes, {nowv['nodes_resolved']} resolved"
            f" · {nowv['surfaced_pending']} awaiting approval · presence: {nowv['presence']}\n"
            f"- nodes: {nodes}\n"
            f"- available node-types: {', '.join(self.list_types())}\n"
            f"- recent activity: {evs}\n"
        )
        selected = [s for s in (focus or {}).get("selected", []) if s in by]
        if selected:
            lines = []
            for nid in selected:
                n = by[nid]
                out = n.get("output")
                detail = (str(out)[:280] if out is not None else "(unresolved)")
                cfg = n.get("config") or {}
                lines.append(f"  · {nid} ({n['type']}, {n['status']}) — config={cfg} — output: {detail}")
            ctx += ("\nOPERATOR'S CURRENT FOCUS (co-presence — they have these selected on the canvas RIGHT "
                    "NOW; you may reference their full detail, including values):\n" + "\n".join(lines) + "\n")
        return ctx

    # The RHM signals intent with a trailing `ACTION:` line; the dispatcher enforces a
    # WHITELIST so the conversational surface can never reach apply/delete/file-write (E6).
    RHM_VERBS = ("run", "propose", "build")

    @staticmethod
    def _parse_rhm_action(reply: str):
        """Split a reply into (shown_text, action|None). Action lines:
        `ACTION: run` · `ACTION: propose <name> :: <spec>` · `ACTION: build <json pipeline>`."""
        import json as _j
        lines = reply.rstrip().splitlines()
        if not lines:
            return reply, None
        last = lines[-1].strip()
        if not last.upper().startswith("ACTION:"):
            return reply, None
        body = last[len("ACTION:"):].strip()
        shown = "\n".join(lines[:-1]).rstrip()
        verb, _, rest = body.partition(" ")
        verb = verb.lower()
        if verb == "propose":
            name, _, spec = rest.partition("::")
            return shown, {"verb": "propose", "name": name.strip(), "spec": spec.strip()}
        if verb == "build":
            try:
                steps = _j.loads(rest)
            except Exception:
                steps = None
            return shown, {"verb": "build", "steps": steps}
        return shown, {"verb": verb}

    def _dispatch_rhm_action(self, action: dict, graph_id: str) -> dict:
        """Execute ONLY whitelisted verbs. Anything else is refused with no effect — this is the
        no-bypass guarantee: the RHM cannot apply/delete/write, only propose (surfaces) or run (AUTO)."""
        verb = (action or {}).get("verb")
        if verb == "run":
            r = self.run(graph_id)
            return {"did": "run", "ran": sorted(r["ran"]), "cached": sorted(r["skipped"])}
        if verb == "propose":
            name, spec = action.get("name"), action.get("spec")
            if name and spec:
                p = self.propose_node(name, spec)        # surfaces for OPERATOR approval (CONFIRM)
                return {"did": "propose", "surfaced": p["id"], "name": name}
            return {"did": "none", "refused": "propose needs '<name> :: <spec>'"}
        if verb == "build":
            # symmetric agency / NL→graph: compose a pipeline on the canvas. Only create_node +
            # connect (AUTO, reversible — exactly what the operator can do), never apply/delete.
            steps = action.get("steps")
            if not isinstance(steps, list):
                return {"did": "none", "refused": "build needs a JSON list of steps"}
            local, made, edges = {}, [], []
            try:
                for step in steps:
                    if "type" in step:
                        nid = self.create_node(graph_id, step["type"], config=step.get("config", {}))
                        local[step.get("as", nid)] = nid
                        made.append(nid)
                    elif "wire" in step:
                        lhs, _, rhs = step["wire"].partition("->")
                        fa, _, fp = lhs.strip().partition("."); ta, _, tp = rhs.strip().partition(".")
                        self.connect(graph_id, local.get(fa, fa), fp, local.get(ta, ta), tp)
                        edges.append(step["wire"])
            except Exception as e:                        # bad type/port → fail the build loudly, no half-claim
                return {"did": "build", "error": f"{type(e).__name__}: {e}", "nodes": made, "edges": edges}
            return {"did": "build", "nodes": made, "edges": edges}
        return {"did": "none",
                "refused": f"verb {verb!r} is not permitted from the RHM — only {self.RHM_VERBS} "
                           "(apply/delete/file-write are operator-gated)"}

    def chat(self, message: str, graph_id: str, focus: dict | None = None) -> dict:
        """Grounded conversation with the operator. Answers from compact ground truth; never
        confabulates system facts. Suggests actions but performs none that skip the surfaced
        gate (E6 invariant) — proposing/running route through the normal verbs."""
        mode = self.get_mode()
        if mode == "off":                                     # the dial disables the RHM entirely
            self.store.append_chat({"role": "user", "text": message, "grade": "gold"})
            off = "The right-hand-man is off. Switch a mode on the presence dial to wake me."
            self.store.append_chat({"role": "assistant", "text": off, "grade": "working"})
            self._emit("chat", f"you: {message[:40]} (RHM off)")
            return {"reply": off, "action": None, "mode": mode, "history": self.store.chat_history(40)}
        from fabric import client, transport
        cfg = self.rhm_config()
        persona = cfg["persona"]
        sys_p = (
            "You are the right-hand-man — the coherent voice of the Company, speaking to its operator "
            "about the system ITSELF. Answer ONLY from the LIVE SYSTEM STATE below; it is ground truth. "
            "If something is not in that state, say you cannot see it — NEVER invent counts, names, or "
            "facts. Be concise and concrete.\n\n"
            + (f"VOICE / PERSONA (hold this consistently): {persona}\n\n" if persona else "")
            + ("THE EXPLICIT MODEL OF TIM (the principles the Company holds itself to — reason from these "
               "for judgment/value questions, but mark such answers as YOUR inference (working-grade), "
               "never as Tim's actual words; when genuinely uncertain, say so and defer to Tim):\n"
               f"{self._model_of_tim_digest()}\n\n" if self._model_of_tim_digest() else "")
            + f"CURRENT MODE — {mode}: {self._mode_directive(mode)}\n\n"
            "You can ACT on the system, but only through governed verbs. When the operator asks you to do "
            "something you're capable of, append EXACTLY ONE final line:\n"
            "  ACTION: run                         (recompute the current graph)\n"
            "  ACTION: propose <name> :: <spec>    (draft a NEW node-type for the operator to approve)\n"
            "  ACTION: build <json>                (compose a pipeline on the canvas from EXISTING types)\n"
            "build's <json> is a list of steps, each either a node "
            '{"as":"a","type":"<existing type>","config":{...}} or a wire {"wire":"a.port -> b.port"} '
            "(reference nodes by their 'as' name). Use build to turn a described pipeline into real nodes "
            "wired on the canvas. Use the available node-types listed in the state; if a needed type does "
            "not exist, propose it first.\n"
            "Proposing only DRAFTS a node-type (operator must approve before it goes live). build only adds/"
            "wires nodes (reversible, like the operator does). You CANNOT apply, delete, or write files "
            "yourself. Never append an ACTION line unless asked to act."
        )
        msgs = [{"role": "system", "content": sys_p + "\n\n" + self._chat_context(graph_id, focus)}]
        for t in self.store.chat_history(20):
            msgs.append({"role": t["role"], "content": t["text"]})
        msgs.append({"role": "user", "content": message})
        raw = client.complete(transport.openai_transport(base_url=cfg["base_url"]),
                              msgs, model=cfg["model"])      # model + provider are configurable (E1)
        reply, action = self._parse_rhm_action(raw)
        outcome = self._dispatch_rhm_action(action, graph_id) if action else None
        # provenance grading (B3): Tim's words are gold (train the twin); the twin's are working
        self.store.append_chat({"role": "user", "text": message, "grade": self._provenance_grade("user")})
        self.store.append_chat({"role": "assistant", "text": reply, "action": outcome,
                                "grade": self._provenance_grade("assistant")})
        self._emit("chat", f"you: {message[:48]}")
        return {"reply": reply, "action": outcome, "mode": mode,
                "model": cfg["model"], "history": self.store.chat_history(40)}

    def chat_history(self, limit: int = 40) -> list:
        return self.store.chat_history(limit)

    # --- the inbox: chief-of-staff triage (F1-F2) + the decision-compiler UP (C2-C3) ---
    def inbox_lanes(self) -> dict:
        """Three lanes (context-05): live escalations (pending, need the operator), resolved-for-you
        (already handled — audit), and batched walkthroughs (pending grouped by theme)."""
        items = self.inbox.list()
        escalations = [d for d in items if d.get("resolved") is None]
        resolved = [d for d in items if d.get("resolved") is not None]
        batched: dict = {}
        for d in escalations:
            batched.setdefault(d["action"], []).append(d["id"])
        return {
            "live_escalations": escalations,                       # the irreducible — brought as COA
            "resolved_for_you": resolved,                          # logged for audit; needn't be worked
            "batched": {k: v for k, v in batched.items() if len(v) > 1},  # themes to handle in one sitting
            "counts": {"escalations": len(escalations), "resolved": len(resolved)},
        }

    def coa(self, surfaced_id: str) -> dict:
        """Decision-compiler UP: translate a raw technical decision into a Commander-altitude
        value-choice — what it means, 2-3 options with trade-offs, + a recommendation. The raw
        payload stays DRILLABLE (F2); the operator decides on value, never the raw fork (C2)."""
        d = self.inbox.get(surfaced_id)
        if not d:
            raise KeyError(f"no surfaced decision {surfaced_id!r}")
        from fabric import client, transport
        cfg = self.rhm_config()
        sys_p = (
            "You are the right-hand-man's decision-compiler. Translate a raw technical decision into a "
            "COMMANDER-ALTITUDE value choice for the operator: (1) what it means for the system in plain "
            "terms, (2) 2-3 options with their trade-offs, (3) a clear RECOMMENDATION with a one-line why. "
            "Never make raw code the choice — the operator decides on value, not implementation. Be concise.")
        user = f"Decision class: {d['action']}. Default if ignored: {d.get('default')}. Payload: {d['payload']}"
        framing = client.complete(transport.openai_transport(base_url=cfg["base_url"]),
                                  [{"role": "system", "content": sys_p},
                                   {"role": "user", "content": user}], model=cfg["model"])
        return {"id": surfaced_id, "class": d["action"], "framing": framing, "raw": d["payload"]}

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
