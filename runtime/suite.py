"""runtime/suite.py — the shared brain (the composition suite's core operations).

ONE brain, two faces: the UI bridge and the MCP server both call this. Graphs live in
the addressed store (S3 graphs registry), so the faces operate the SAME substrate even in
separate processes. Operations are the C7 generic verbs — generic over node-type
(they consult the registry), never one-per-type.
"""
from __future__ import annotations
import os

from contracts.node_record import NodeInstance, Edge, Graph, XY, WH
from runtime import scheduler
from runtime.governance import Inbox, GovernanceError, guard, posture, AUTO
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
        self.panels_dir = os.path.join(os.path.dirname(self.nodes_dir), "panels")  # UI extension point
        # The bridge is a ThreadingHTTPServer → concurrent POST /api/review/next run in separate threads of
        # ONE process over this one Suite. The session-cursor advance is a read-modify-write (load→run→save)
        # with no lock → concurrent calls dropped advances (lost update). A per-session in-process lock
        # serializes that critical section. Guarded so a CAS re-read still protects across processes/restart.
        import threading as _t
        self._session_locks_guard = _t.Lock()
        self._session_locks: dict = {}
        # WIRE exactly-once: the dispatch CHECK (read the event log for a prior decision.dispatch) →
        # CLAIM (emit decision.dispatch) is a read-modify-write critical section. The bridge is a
        # ThreadingHTTPServer over ONE Suite, so two concurrent dispatch_decision calls on the same
        # approved seq would BOTH clear the check before either claims → double-launch. A per-seq
        # in-process lock serializes that section (mirrors the per-session lock pattern above); the
        # durable decision.dispatch event remains the cross-process/restart guarantee.
        self._dispatch_locks_guard = _t.Lock()
        self._dispatch_locks: dict = {}

    def _session_lock(self, session_id: str):
        """One reentrant-safe lock per session, created on demand (threadsafe)."""
        import threading as _t
        with self._session_locks_guard:
            lk = self._session_locks.get(session_id)
            if lk is None:
                lk = _t.Lock()
                self._session_locks[session_id] = lk
            return lk

    def _dispatch_lock(self, derived_from: int):
        """One lock per resolve `seq`, created on demand (threadsafe) — serializes the
        exactly-once CHECK→CLAIM critical section in dispatch_decision so a true race
        (two threads, one Suite) cannot double-launch the same approved decision."""
        import threading as _t
        with self._dispatch_locks_guard:
            lk = self._dispatch_locks.get(derived_from)
            if lk is None:
                lk = _t.Lock()
                self._dispatch_locks[derived_from] = lk
            return lk

    def _emit(self, kind: str, summary: str, **meta) -> None:
        """Append one TELEMETRY event to the captured trajectory (I2). Lenient by design: a telemetry
        emit must never break the action it records, so a store hiccup is swallowed here. This is the
        RIGHT posture for narration/visibility events — but it is the WRONG posture for a DURABLE CLAIM
        whose absence changes behavior (e.g. the exactly-once decision.dispatch claim): for those use
        _emit_durable, which fails loud (T1-EMIT). Never route a safety-critical claim through _emit."""
        try:
            self.store.append_event({"kind": kind, "summary": summary, **meta})
        except Exception:
            pass

    def _emit_durable(self, kind: str, summary: str, **meta) -> dict:
        """Append a DURABLE CLAIM event — FAIL LOUD (T1-EMIT). Unlike _emit (lenient telemetry), this
        does NOT swallow a failure: it returns the written record, and lets any append_event exception
        PROPAGATE. The exactly-once dispatch guarantee rides on the `decision.dispatch` claim being
        actually written — if that write silently failed (the old try/except: pass), _already_dispatched
        would return False on a retry → DOUBLE-LAUNCH of a real `claude -p` build. So the claim write
        must raise on failure (the caller is inside the dispatch lock, BEFORE launch — a raise here means
        nothing launches, exactly the safe outcome). Direct enforcement of rule 4 (fail loud) on the
        safety-critical path. Use ONLY for writes whose loss changes behavior; narration stays on _emit."""
        return self.store.append_event({"kind": kind, "summary": summary, **meta})

    # --- the capability registry: the source of truth the brain authors FROM (never invents) ---
    _models_cache: list | None = None

    def available_models(self) -> list:
        """The REAL models registered at the fabric endpoint — so the brain picks from what exists
        instead of inventing names. Cached; falls back to the configured brain if the endpoint is down."""
        if self._models_cache is None:
            from fabric import transport, config as fcfg
            try:
                models = transport.list_models(fcfg.DEFAULT_BASE_URL)
            except Exception as e:
                models = None
                self._emit("warning", f"model registry unreachable ({type(e).__name__}) — "
                           f"falling back to [{fcfg.DEFAULT_BRAIN}]; the source-of-truth list is degraded")
            if not models:                                    # surface the degraded fallback, never silent (F6)
                if models is not None:
                    self._emit("warning", "model registry returned empty — falling back to the default brain")
                models = [fcfg.DEFAULT_BRAIN]
            self._models_cache = models
        return self._models_cache

    def models_at(self, kind: str = "chat", base_url: str | None = None) -> list:
        """List the REAL models registered at a GIVEN endpoint (B) — so the UI can fill chat-model
        AND embed-model dropdowns from what is ACTUALLY running, not a hand-typed list. BYPASSES the
        chat-only available_models() cache (which only ever hits DEFAULT_BASE_URL → would fill an
        embed dropdown with chat models, the B3 bug). forbid_gemini is preserved (transport.list_models
        filters it). Fail loud: if the embed endpoint isn't configured by the fabric, raise rather than
        silently fall back to the chat endpoint (a silent fallback is the exact rot the laws forbid)."""
        from fabric import transport, config as fcfg
        if base_url is None:
            if kind == "embed":
                base_url = getattr(fcfg, "DEFAULT_EMBED_URL", None)
                if not base_url:
                    raise RuntimeError(
                        "no embedding endpoint configured (fabric.config.DEFAULT_EMBED_URL absent) — "
                        "cannot list embed models without inventing a fallback (fail loud, no silent "
                        "fallback to the chat endpoint). Configure the embed endpoint first.")
            else:
                base_url = fcfg.DEFAULT_BASE_URL
        return transport.list_models(base_url)               # live, uncached; Gemini filtered in transport

    def capabilities(self) -> dict:
        """One snapshot of WHAT EXISTS — fed into every authoring prompt + every registered select,
        so the correct values are the easy path and nothing is guessed. The reflective fold."""
        return {
            "node_types": sorted(self.registry.types),
            "models": self.available_models(),
            "modes": list(self.MODES),
            # T3-MODE (backend half): expose the mode DIRECTIVES (the prose behind each mode) so the FE
            # reads them from the registry instead of hand-copying MODE_DIRECTIVES into a parallel
            # MODE_DESC (the PoLR violation: registry is the one source of truth). The FE deletes its
            # copy and reads capabilities().mode_directives. (be-half → at most needs-tim until the FE
            # consumes it.) Additive map {mode: directive}; an older FE that ignores it is unaffected.
            "mode_directives": dict(self.MODE_DIRECTIVES),
            "rhm_verbs": list(self.RHM_VERBS),
            "panels": [p.get("id") for p in self.list_panels()],
            "panel_field_targets": list(self.PANEL_TARGETS),
            "api_verbs": ["/api/run", "/api/now", "/api/chat", "/api/graph", "/api/graphs",
                          "/api/types", "/api/object_info", "/api/events", "/api/inbox",
                          "/api/panels", "/api/models", "/api/stream", "/api/move",
                          "/api/ui_info", "/api/surface-review", "/api/capture-idea",
                          "/api/build-intent",
                          "/api/review/start", "/api/review/current", "/api/review/next",
                          "/api/review/status"],
        }

    def _authoring_preamble(self) -> str:
        """Put the registry on the brain's easy path so the correct values are effortless and nothing
        is invented — and make ASKING the easy path when something needed isn't registered."""
        cap = self.capabilities()
        return ("REGISTERED VALUES — author using ONLY these; do NOT invent anything not listed:\n"
                f"- models: {cap['models']}\n- modes: {cap['modes']}\n- node-types: {cap['node_types']}\n"
                f"- api verbs (for fetch): {cap['api_verbs']}\n"
                "If doing this correctly REQUIRES a value or capability NOT in these lists, do NOT make one "
                "up — output EXACTLY one line and nothing else: NEEDS: <what you need, and why>.")

    @staticmethod
    def _slug(name: str) -> str:
        """Normalize the brain's natural name ('Model Selector' → 'model_selector') so the correct
        path is easy. But a PATH-like name (/, .., \\) is a traversal attempt, not a name — reject it
        rather than silently sanitizing an attack into a node. (_safe_node_name guards again after.)"""
        import re
        if name and ("/" in name or "\\" in name or ".." in name):
            raise ValueError(f"unsafe name {name!r} — looks like a path, not a name")
        s = re.sub(r"[^a-z0-9]+", "_", (name or "").lower()).strip("_")
        if not s or s[0].isdigit():
            s = "x_" + s
        return s

    @staticmethod
    def _needs(text: str):
        t = (text or "").strip()
        return t[len("NEEDS:"):].strip() if t.upper().startswith("NEEDS:") else None

    def _ask_operator(self, question: str, context: str = "") -> str:
        """The brain hit unregistered ground → ASK the operator (surfaced question) instead of
        fabricating. Confabulation is as bad as failing (Tim) — this makes asking the easy path."""
        sid = self.inbox.surface("question", {"question": question, "context": context}, default="reject")
        self._emit("ask", f"the system needs input: {question[:60]}", surfaced=sid)
        return sid

    def _acceptance_suites(self) -> list:
        import glob
        return sorted(os.path.basename(p)[:-3]
                      for p in glob.glob(os.path.join(self._repo_root, "tests", "*.py")))

    def _write_doc_block(self, filename: str, marker: str, body: str) -> None:
        """Replace the <!--MARKER:START-->…<!--MARKER:END--> block of a self-description file
        with freshly-generated content. The factual parts of the docs thus maintain themselves."""
        import re
        path = os.path.join(self._repo_root, filename)
        if not os.path.exists(path):
            return
        full = f"<!--{marker}:START-->{body}<!--{marker}:END-->"
        text = open(path, encoding="utf-8").read()
        new = re.sub(rf"<!--{marker}:START-->.*?<!--{marker}:END-->", lambda _m: full, text, flags=re.S)
        if new != text:
            open(path, "w", encoding="utf-8").write(new)

    def refresh_self_description(self) -> None:
        """The reflective fold: regenerate the auto-maintained factual blocks of the orientation files
        — MAP.md (the live registry) + STATE.md (the acceptance-suite index) — from the system itself,
        so the self-description stays current as the app grows (Tim's 'maintains'). Called on every
        apply/revert. The PROSE is integration-maintained; doc_drift fails loud if anything falls behind."""
        cap = self.capabilities()
        self._write_doc_block("MAP.md", "REGISTRY",
            " (auto-maintained by Suite.refresh_self_description on every apply — do not hand-edit)\n"
            f"- **node-types** ({len(cap['node_types'])}): {', '.join(cap['node_types'])}\n"
            f"- **RHM verbs**: {', '.join(cap['rhm_verbs'])}\n"
            f"- **modes**: {', '.join(cap['modes'])}\n"
            f"- **panels**: {', '.join(cap['panels']) or '(none)'}\n"
            f"- **models** (from the fabric registry): {', '.join(cap['models'])}\n")
        suites = self._acceptance_suites()
        self._write_doc_block("STATE.md", "SUITES",
            " (auto-maintained by Suite.refresh_self_description — do not hand-edit)\n"
            f"- {len(suites)} acceptance suites: {', '.join(suites)}\n")

    # back-compat alias (older callers / external agents may know this name)
    refresh_map = refresh_self_description

    def _doc_block(self, filename: str, marker: str) -> str:
        """The text INSIDE a file's <!--MARKER--> block (lowercased) — so drift is checked against the
        maintained registry block, NOT the whole prose file (red-team F3: prose substrings → false negatives)."""
        import re
        path = os.path.join(self._repo_root, filename)
        if not os.path.exists(path):
            return ""
        m = re.search(rf"<!--{marker}:START-->(.*?)<!--{marker}:END-->",
                      open(path, encoding="utf-8").read(), re.S)
        return (m.group(1) if m else "").lower()

    def doc_drift(self) -> dict:
        """What the system has that the SELF-DESCRIPTION files don't yet reflect — so they can't
        silently rot (Tim: 'updates to the system → updates to whatever relevant files like this').
        Checked INSIDE the maintained blocks (not whole-file substrings), covering every capability
        category (node-types, verbs, modes, panels) + the suite index. A failing check is the enforcement."""
        reg = self._doc_block("MAP.md", "REGISTRY")
        suites_block = self._doc_block("STATE.md", "SUITES")
        cap = self.capabilities()
        return {
            "map_node_types": [t for t in cap["node_types"] if t.lower() not in reg],
            "map_rhm_verbs": [v for v in cap["rhm_verbs"] if v.lower() not in reg],
            "map_modes": [m for m in cap["modes"] if m.lower() not in reg],
            "map_panels": [p for p in cap["panels"] if p.lower() not in reg],
            "state_missing_suites": [s for s in self._acceptance_suites() if s.lower() not in suites_block],
        }

    map_drift = doc_drift  # back-compat alias

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

    def _last_run_stuck(self, graph_id: str) -> list:
        """T3-STATUS — the `stuck` node-ids from the MOST RECENT `run` event for `graph_id` (the run
        emit records `stuck=[...]` with `graph=<id>`). Backend-authoritative source for the persisted
        (no-fresh-result) status path, so `stuck` survives a reload without a client-side overlay. Reads
        events newest-first; the first matching run event wins. Empty when the graph never ran / no
        stuck nodes. Tolerant: a malformed/absent field reads as no-stuck (never raises in a status read)."""
        for ev in self.store.recent_events(200):
            if ev.get("kind") == "run" and ev.get("graph") == graph_id:
                st = ev.get("stuck")
                return list(st) if isinstance(st, list) else []
        return []

    @staticmethod
    def _schema_defaults(schema: dict) -> dict:
        """Flatten a node-type's nested config_schema {key:{...,default}} → {key:default} (A).
        Guarded so it survives a still-flat CONFIG ({key:value}, mid-migration) and skips entries
        with no/None default — so a freshly-added node is seeded with its type's defaults (not blank
        and inert) WITHOUT clobbering a run()-fallback (None default) or fabricating keys."""
        out = {}
        for k, v in (schema or {}).items():
            if isinstance(v, dict) and "default" in v and v["default"] is not None:
                out[k] = v["default"]
        return out

    def create_node(self, graph_id: str, type: str, config: dict | None = None,
                    node_id: str | None = None, position: dict | None = None) -> str:
        if type not in self.registry:
            raise KeyError(f"unknown node-type {type!r} (have: {self.list_types()})")
        def _do():                                                       # G1: AUTO → guard runs it straight through
            # T1-RACE: hold the per-graph lock around the WHOLE load→mutate→save so a concurrent
            # mutation on the same graph (another create/move/connect on the threading server, or the
            # MCP face racing a UI move) can't load the same version and last-writer-wins (lost update).
            with self.store.graph_lock(graph_id):
                g = self._load(graph_id)
                nid = node_id or f"{type}-{len(g.nodes) + 1}"
                nt = self.registry.types.get(type)
                seeded = self._schema_defaults(nt.config_schema if nt else {})   # type defaults first…
                seeded.update(config or {})                                      # …caller config WINS (merge)
                pos = XY(**position) if position else XY()                       # optional initial placement (C5)
                g.nodes.append(NodeInstance(id=nid, type=type, config=seeded, position=pos))
                self.store.save_graph(g)
                self._emit("create", f"+ {type} node ({nid})", graph=graph_id, node=nid, type=type)
                return nid
        return guard("compose", do=_do)                                  # AUTO → identical behavior; POLICY is the router

    def connect(self, graph_id: str, from_node: str, from_port: str,
                to_node: str, to_port: str) -> None:
        # T1-RACE: per-graph lock around the whole load→mutate→save (lost-update across both faces).
        with self.store.graph_lock(graph_id):
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
        # T1-RACE: per-graph lock around the whole load→mutate→save (lost-update across both faces).
        with self.store.graph_lock(graph_id):
            g = self._load(graph_id)
            g.nodes = [n for n in g.nodes if n.id != node_id]
            g.edges = [e for e in g.edges if e.from_node != node_id and e.to_node != node_id]
            self.store.save_graph(g)
            self._emit("delete", f"removed node {node_id}", graph=graph_id, node=node_id)

    def set_config(self, graph_id: str, node_id: str, config: dict) -> None:
        def _do():                                                       # G1: AUTO → guard runs it straight through
            # T1-RACE: per-graph lock around the whole load→mutate→save (lost-update across both faces).
            with self.store.graph_lock(graph_id):
                g = self._load(graph_id)
                for n in g.nodes:
                    if n.id == node_id:
                        n.config.update(config)
                        self.store.save_graph(g)
                        return
                raise KeyError(f"no node {node_id!r} in graph {graph_id!r}")
        return guard("configure", do=_do)                               # AUTO → identical; POLICY is the router

    def set_position(self, graph_id: str, node_id: str, x: float, y: float,
                     w: float | None = None, h: float | None = None) -> None:
        """Write a node's SIBLING position (and optional size) — NOT its config (C5). The canvas
        reflects, never owns: a drag-end round-trips here so the backend stays the source of truth
        for layout. A clone of set_config but targeting position/size, the NodeInstance fields that
        already round-trip to disk. Raises KeyError if the node is absent (fail loud)."""
        # T1-RACE: per-graph lock around the whole load→mutate→save. /api/move is the highest-frequency
        # mutation path; without the lock two concurrent moves on DISTINCT nodes both load version V →
        # last-writer-wins → the other node's move silently lost (the exact bug T1-RACE names).
        with self.store.graph_lock(graph_id):
            g = self._load(graph_id)
            for n in g.nodes:
                if n.id == node_id:
                    n.position = XY(x=x, y=y)
                    if w is not None and h is not None:
                        n.size = WH(w=w, h=h)
                    self.store.save_graph(g)
                    self._emit("move", f"moved {node_id} → ({x:.0f},{y:.0f})",
                               graph=graph_id, node=node_id)
                    return
            raise KeyError(f"no node {node_id!r} in graph {graph_id!r}")

    def save_graph(self, graph: Graph) -> None:
        self.store.save_graph(graph)

    # --- run + read ---
    def run(self, graph_id: str, branch: str = "main", pause=None, force=None) -> dict:
        def _do():                                                       # G1: AUTO → guard runs it straight through
            r = scheduler.run(self._load(graph_id), self.store, self.registry,
                              branch=branch, pause=pause, force=force)
            self._emit("run", f"ran {len(r['ran'])}, cached {len(r['skipped'])}"
                       + (f", stuck {len(r['stuck'])}" if r.get("stuck") else ""),
                       graph=graph_id, ran=sorted(r["ran"]), cached=sorted(r["skipped"]),
                       stuck=sorted(r.get("stuck", [])))
            return r
        return guard("run", do=_do)                                     # AUTO → identical; POLICY is the router

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
            if result:
                # T3-STATUS: `stuck` is a REAL backend node status (one source of truth), not a
                # client-only overlay. The scheduler already reports which nodes could not fire because
                # an input never resolved (scheduler result['stuck']); surface it here so the FE reads
                # it from the backend instead of maintaining a parallel client-side `stuck` re-applied
                # from events after every reload. Checked BEFORE ran/cached/idle so a stuck node is
                # never mislabeled idle. (be-half → at most needs-tim until the FE drops its overlay.)
                status = ("stuck" if n.id in result.get("stuck", [])
                          else "ran" if n.id in result["ran"]
                          else "cached" if n.id in result["skipped"] else "idle")
            else:
                # D5-be (persisted run-status, in-territory): with no fresh run result, DERIVE status
                # from the store — a node whose output address resolves has a cached result, so report
                # 'cached' instead of resetting to 'idle' on reload. Fail-loud-legible: the surface
                # never claims "nothing happened" for a node that actually holds a result. T3-STATUS:
                # `stuck` is run-relative (an input that never resolved on the LAST run), so without a
                # fresh result we derive from the most recent run event for THIS graph that listed the
                # node as stuck — keeping `stuck` backend-authoritative across a reload (what the FE used
                # to re-derive client-side). A node that since resolved (cas present) is never stuck.
                if cas:
                    status = "cached"
                elif n.id in self._last_run_stuck(g.id):
                    status = "stuck"
                else:
                    status = "idle"
            nt = self.registry.types.get(n.type)
            nodes.append({
                "id": n.id, "type": n.type, "config": n.config,
                "kind": nt.kind if nt else ("content" if n.type in CONTENT_KINDS else "process"),
                "layer": getattr(mod, "ORIGIN", "authored"),   # provenance layer (authored vs system)
                "status": status, "address": logical, "content_hash": cas,
                "output": self.store.get_content(cas) if cas else None,
                "position": n.position.model_dump(),           # C5: layout is backend-authoritative
                "size": n.size.model_dump(),
            })
        return {"id": g.id, "nodes": nodes,
                # C2/C3: carry per-port identity so the UI draws per-port wires + feeds multi-input
                # nodes correctly. {from,to} kept for back-compat; from_port/to_port are additive.
                "edges": [{"from": e.from_node, "to": e.to_node,
                           "from_port": e.from_port, "to_port": e.to_port} for e in g.edges]}

    def results(self, graph_id: str) -> dict:
        st = self.state(graph_id)
        return {n["id"]: n["output"] for n in st["nodes"]}

    # --- the operator surfaces (I2): now-view · presence · event log ---
    def events(self, limit: int = 60) -> list:
        return self.store.recent_events(limit)

    def events_since(self, seq: int) -> list:
        """Events with seq > given, oldest-first — the SSE cursor read (G). Thin pass-through to the
        store's file-tail (mirrors events()); captures BOTH faces since it tails the shared log."""
        return self.store.events_since(seq)

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
        "decide-for-me": "Act on what the governance posture lets you act on (the AUTO/reversible classes — propose a node, run the graph) rather than asking; surface the rest for the operator. The routing is deterministic (the action's posture decides), not a judgement call. You still cannot self-approve; anything that needs approval is surfaced.",
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
                "persona": c.get("persona", ""),
                # voice-trial lane H: surface the per-mode voice toggle in the config the FE reads.
                # Default 'on' so a node with no field is voice-enabled (schema-additive).
                "voice_enabled": c.get("voice_enabled", "on")}

    def voice_enabled(self) -> bool:
        """Lane H — is voice on for the current presence? Reads the rhm node's `voice_enabled`
        CONFIG (the per-mode voice toggle), defaulting to True when absent (schema-additive: an old
        node with no field is voice-on). The conversation loop / a voice-gated path consults THIS
        rather than assuming voice; 'off' here means the mode runs text-only even with engines up.
        Also gated by the presence dial: mode 'off' (the RHM disabled) is never voice-on."""
        if self.get_mode() == "off":
            return False
        return str(self._rhm_cfg().get("voice_enabled", "on")).lower() != "off"

    def set_rhm_config(self, updates: dict) -> dict:
        allowed = {k: v for k, v in (updates or {}).items()
                   if k in ("model", "base_url", "persona", "mode", "voice_enabled")}
        if "mode" in allowed and allowed["mode"] not in self.MODES:
            raise ValueError(f"unknown mode {allowed['mode']!r}")
        if "voice_enabled" in allowed and str(allowed["voice_enabled"]).lower() not in ("on", "off"):
            raise ValueError(f"voice_enabled must be 'on' or 'off', got {allowed['voice_enabled']!r}")
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

    @staticmethod
    def _provenance_source(role: str) -> str:
        """The SOURCE of a turn — operator (Tim) vs twin (the system). Grade alone is role-derived
        and launderable; the source travels with the turn so the twin's own output can never count
        as training signal even if its text is resubmitted as a 'user' turn (red-team F4)."""
        return "operator" if role == "user" else "twin"

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
        """Only operator-sourced GOLD turns train the twin — NEVER the twin's own output, even if it
        was laundered back in as a 'user' turn. Two guards (red-team F4): source must be 'operator'
        (not 'twin'), and the text must not echo any twin/assistant turn in history (echo-guard)."""
        history = self.store.chat_history(999)
        twin_texts = {(t.get("text") or "").strip()
                      for t in history if t.get("role") == "assistant" or t.get("source") == "twin"}
        return [t for t in history
                if t.get("grade") == "gold"
                and t.get("source", "operator") != "twin"
                and (t.get("text") or "").strip() not in twin_texts]

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
    RHM_VERBS = ("run", "propose", "build", "consult", "show", "panel", "extend")

    # G3: each RHM verb's GOVERNANCE action-class — the deterministic input to autonomous_dispatch in
    # decide-for-me mode. AUTO classes (run/compose/inspect) → the verb runs; CONFIRM classes
    # (register_type/ui_panel/ui_extension) → surfaced for the operator (the verb body is NOT run, so
    # there is exactly ONE surface, posture-routed). Classes are the SAME ones governance.POLICY routes;
    # no parallel mechanism. (Mirrors what the verb already does per-mode; in decide-for-me the routing
    # is made explicit + single-source through posture, with no confidence anywhere.)
    RHM_VERB_CLASS = {
        "run": "run", "build": "compose", "show": "inspect", "consult": "inspect",
        "propose": "register_type", "panel": "ui_panel", "extend": "ui_extension",
    }

    def consult(self, query: str) -> dict:
        """The RHM reads the system's OWN code+design (the first-purpose Q&A, as a callable) and
        answers — so it knows how it is built. Grounded in the source; cites the file; abstains if
        the answer isn't there. A read (AUTO)."""
        from nodes import codebase as cb
        from fabric import client, transport
        cfg = self.rhm_config()
        src = cb.run({}, {})                              # repo source; AGENTS.md points at the vault design
        sys_p = ("You answer questions about THIS system's own design and code, STRICTLY from the SOURCE "
                 "below. Cite the relevant file. If the answer is not in the source, say so plainly. Concise.")
        ans = client.complete(transport.openai_transport(base_url=cfg["base_url"]),
                              [{"role": "system", "content": sys_p},
                               {"role": "user", "content": f"SOURCE:\n{src[:380000]}\n\nQUESTION: {query}"}],
                              model=cfg["model"])
        return {"answer": ans}

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
        if verb == "consult":
            return shown, {"verb": "consult", "query": rest.strip()}
        if verb == "show":
            targets = [t for t in rest.replace(",", " ").split() if t]
            return shown, {"verb": "show", "targets": targets}
        if verb == "panel":
            name, _, spec = rest.partition("::")
            return shown, {"verb": "panel", "name": name.strip(), "spec": spec.strip()}
        if verb == "extend":
            name, _, spec = rest.partition("::")
            return shown, {"verb": "extend", "name": name.strip(), "spec": spec.strip()}
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
                if p.get("needs"):
                    return {"did": "ask", "surfaced": p["id"], "needs": p["needs"]}
                return {"did": "propose", "surfaced": p["id"], "name": name}
            return {"did": "none", "refused": "propose needs '<name> :: <spec>'"}
        if verb == "consult":
            q = action.get("query") or ""
            if not q:
                return {"did": "none", "refused": "consult needs a query"}
            return {"did": "consult", "answer": self.consult(q)["answer"]}
        if verb == "show":
            # attention-direction (magic-camera): a VIEW directive — moves the operator's view,
            # mutates NOTHING (view-only — preserved). Three target forms, all validated so we never
            # point at nothing; validated targets pass through UNCHANGED for the UI lane's resolver:
            #   • bare node-id            → live node on the canvas (existing behavior, kept)
            #   • ui://canvas/<id|*>      → camera path (a node-id, or '*' = the whole canvas)
            #   • ui://<chrome|field|panel|ext>/<ref> → a UI-component in the registry (build_ui_info)
            ids = {n.id for n in self._load(graph_id).nodes}
            reg = None                                          # the ui:// registry, lazily built once
            targets = []
            for t in action.get("targets", []):
                if t.startswith("ui://"):
                    kind, _, ref = t[len("ui://"):].partition("/")
                    if kind == "canvas":
                        # camera-resolved: a live node-id, or '*' = the whole canvas (registry entry)
                        if ref == "*" or ref in ids:
                            targets.append(t)
                    else:
                        # registry-resolved (chrome/field/panel/ext): the ref must be a known component.
                        # build_ui_info() is keyed by ref; kind is carried for the frontend's dispatch.
                        if reg is None:
                            reg = self.build_ui_info()
                        if ref in reg:
                            targets.append(t)
                elif t in ids:
                    targets.append(t)                           # bare node-id (kept)
            if not targets:
                return {"did": "none", "refused": "show: no matching target (node-id or ui:// component)"}
            return {"did": "show", "targets": targets}
        if verb == "panel":
            # update the interface through the interface: author a DECLARATIVE panel → surfaced
            # (CONFIRM, operator approves → git-committed). Not arbitrary code; not self-applied.
            name, spec = action.get("name"), action.get("spec")
            if name and spec:
                p = self.propose_panel(name, spec)
                if p.get("needs"):
                    return {"did": "ask", "surfaced": p["id"], "needs": p["needs"]}
                return {"did": "panel", "surfaced": p["id"], "name": name}
            return {"did": "none", "refused": "panel needs '<name> :: <spec>'"}
        if verb == "extend":
            name, spec = action.get("name"), action.get("spec")
            if name and spec:
                p = self.propose_extension(name, spec)       # arbitrary code → build-gate → operator approves
                if p.get("needs"):
                    return {"did": "ask", "surfaced": p["id"], "needs": p["needs"]}
                return {"did": "extend", "surfaced": p["id"], "name": name}
            return {"did": "none", "refused": "extend needs '<name> :: <spec>'"}
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

    # --- G3: the decide-for-me deterministic dispatcher (NO confidence — posture decides) ---
    def autonomous_dispatch(self, action_class: str, do, payload: dict | None = None) -> dict:
        """G3: route an intended action by GOVERNANCE POSTURE alone — the deterministic decide-for-me
        router. `posture(action_class)` (governance.py POLICY) is the ONLY input: there is no
        confidence value, no score, no judgement call. It routes the ACT-vs-SURFACE decision; the
        `do` callable performs it.

          posture == AUTO  → guard(action_class, do)  → ACT (reversible/cheap/internal; run it now)
          else (SURFACE/CONFIRM, incl. every unknown class → CONFIRM, and every LOCKED class which
                posture() can NEVER return AUTO for) → run `do()` — but for an action whose posture is
                CONFIRM, `do` is a GOVERNED verb body whose own action is to SURFACE a consumable draft
                for the operator (propose→code_build, panel→ui_panel, extend→ui_extension; each surfaces
                the GENERATED payload that apply_node/apply_panel/apply_extension consume on approve). So
                the surface is the verb's real, applyable draft — NOT a generic intent-record that
                nothing could later build (that would be silent success — AGENTS.md rule 4).

        WHY running `do()` on CONFIRM does NOT bypass governance: this router is only ever called with
        RHM verbs (run/propose/build/consult/show/panel/extend — the RHM_VERBS whitelist). NONE of them
        apply/delete/write; the CONFIRM ones SURFACE (never apply). apply still requires the operator's
        `is_approved`. So no-self-approve is preserved STRUCTURALLY by the whitelist: no raw-mutation verb
        can reach this path, so `do()` here can only ever surface or run a reversible AUTO op — never
        approve, apply, or mutate real source. A LOCKED class → posture() CONFIRM → the else branch,
        never AUTO (D4/D7 forever-confirm).

        Returns the verb's own outcome dict, tagged `routed_posture` (auto|surface|confirm) for audit."""
        p = posture(action_class)
        out = guard(action_class, do) if p == AUTO else do()
        out = dict(out) if isinstance(out, dict) else {"result": out}
        out["routed_posture"] = p                              # deterministic record: which posture routed it
        return out

    def chat(self, message: str, graph_id: str, focus: dict | None = None) -> dict:
        """Grounded conversation with the operator. Answers from compact ground truth; never
        confabulates system facts. Suggests actions but performs none that skip the surfaced
        gate (E6 invariant) — proposing/running route through the normal verbs."""
        mode = self.get_mode()
        if mode == "off":                                     # the dial disables the RHM entirely
            self.store.append_chat({"role": "user", "text": message, "grade": "gold", "source": "operator"})
            off = "The right-hand-man is off. Switch a mode on the presence dial to wake me."
            self.store.append_chat({"role": "assistant", "text": off, "grade": "working", "source": "twin"})
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
            "  ACTION: consult <question>          (read the system's OWN code+design and answer it)\n"
            "Use consult for any question about how THIS system is built/designed that isn't in the live "
            "state above (e.g. 'how does the memo gate work', 'what are the contracts'). "
            "  ACTION: show <target(s)>            (move the operator's view to node(s)/UI region — to SHOW them)\n"
            "  ACTION: panel <name> :: <spec>      (add a declarative settings/control PANEL)\n"
            "  ACTION: extend <name> :: <spec>     (write a NEW interface component in code — build-gated)\n"
            "Use panel when the operator asks to add a UI panel/settings to the application; you author a "
            "declarative panel (fields editing real config: mode/model/persona), surfaced for approval. "
            "Use show whenever the operator asks you to show/take them to/point at something. A target is "
            "either a node-id from the live state, or a UI region as ui://<kind>/<ref> from the UI registry "
            "(e.g. ui://chrome/inbox, ui://chrome/activity, ui://canvas/<node-id>). show only moves their "
            "view; it changes nothing. "
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
        if action and mode == "decide-for-me":
            # G3 wiring: in decide-for-me the ACT-vs-SURFACE decision is routed DETERMINISTICALLY by the
            # verb's governance action-class (no confidence) through autonomous_dispatch. The verb BODY
            # performs it either way — AUTO verbs run; CONFIRM verbs run their body whose action is to
            # SURFACE a consumable, applyable draft (propose→code_build, panel→ui_panel, extend→ui_extension).
            # So the outcome is the verb's own dict (did=run/propose/panel/extend/...), plus routed_posture.
            # Every OTHER mode keeps the exact per-verb dispatch below (untouched — mode-gated).
            cls = self.RHM_VERB_CLASS.get(action.get("verb"), "register_type")   # unknown verb → safest (CONFIRM)
            outcome = self.autonomous_dispatch(cls, do=lambda: self._dispatch_rhm_action(action, graph_id),
                                               payload=action)
        else:
            outcome = self._dispatch_rhm_action(action, graph_id) if action else None
        if outcome and outcome.get("did") == "consult":   # fold the looked-up answer into the turn
            reply = (reply + "\n\n📖 " + outcome["answer"]).strip()
        if outcome and outcome.get("did") == "ask":        # asked instead of fabricating (PoLR)
            reply = (reply + "\n\n❓ That needs something not in the registry, so I'm asking rather than "
                     "guessing: " + outcome["needs"] + " — surfaced for you in the inbox.").strip()
        # provenance grading (B3): Tim's words are gold (train the twin); the twin's are working
        self.store.append_chat({"role": "user", "text": message, "grade": self._provenance_grade("user"), "source": self._provenance_source("user")})
        self.store.append_chat({"role": "assistant", "text": reply, "action": outcome,
                                "grade": self._provenance_grade("assistant"), "source": self._provenance_source("assistant")})
        self._emit("chat", f"you: {message[:48]}")
        return {"reply": reply, "action": outcome, "mode": mode,
                "model": cfg["model"], "history": self.store.chat_history(40)}

    def chat_history(self, limit: int = 40) -> list:
        return self.store.chat_history(limit)

    def react(self, graph_id: str) -> dict:
        """watch-and-react mode: a brief AMBIENT comment on the latest activity — unprompted, but
        only in that mode (real mode-gated behavior) and only when something is worth remarking."""
        if self.get_mode() != "watch-and-react":
            return {"comment": ""}                         # mode-gated: silent otherwise
        recent = self.store.recent_events(1)
        if not recent:
            return {"comment": ""}
        from fabric import client, transport
        cfg = self.rhm_config()
        last = recent[0]
        sys_p = ("You are the right-hand-man in watch-and-react mode, watching over the operator's shoulder. "
                 "Given the latest activity, offer ONE short, useful observation or suggestion about it "
                 "(e.g. a node left unwired, an obvious next step, a result worth noting). Only if there is "
                 "truly nothing useful to say, reply with exactly: NOTHING. Keep it to one sentence.")
        user = f"Latest activity: {last['kind']} — {last['summary']}.\n{self._chat_context(graph_id)[:700]}"
        out = client.complete(transport.openai_transport(base_url=cfg["base_url"]),
                              [{"role": "system", "content": sys_p},
                               {"role": "user", "content": user}], model=cfg["model"]).strip()
        if not out or out.upper().startswith("NOTHING"):
            return {"comment": ""}
        self.store.append_chat({"role": "assistant", "text": out, "grade": "working", "ambient": True, "source": "twin"})
        self._emit("react", f"(watching) {out[:44]}")
        return {"comment": out}

    # ============================================================================================
    # The Voice Trial — recording (Group E) + debrief (Group F). REUSE-DON'T-PARALLEL: every
    # artifact rides an EXISTING seam — the append-only event log (durable claims via
    # _emit_durable), the content-addressed store (put_content/set_ref at trial://<session>/
    # transcript), the session store (save_session/load_session), the inbox (surface_review), and
    # the walkthrough organ (start_session/present_current/next/respond). No second event log, no
    # second store, no second brain. Each spoken session is recorded so the debrief can read it
    # back FAITHFULLY (no confabulation — the debrief item carries the REAL transcript).
    # ============================================================================================

    TRIAL_KINDS = ("trial.turn", "trial.feedback", "trial.reflection")

    @staticmethod
    def _trial_transcript_addr(session_id: str) -> str:
        """The CAS-pointer (run://-style mutable ref) for a trial session's full transcript — the
        address the debrief reads back. Namespaced trial:// so it can never collide with a node's
        run:// output address or a review session's go-gate addresses."""
        return f"trial://{session_id}/transcript"

    def _trial_turn_events(self, session_id: str) -> list:
        """Every recorded trial event (turn/feedback/reflection) for ONE session, OLDEST-first —
        the single source the transcript is DERIVED from (so events + CAS never disagree). Reads
        events_since(-1) (the whole file-tail) filtered to the trial kinds + this session id."""
        return [e for e in self.store.events_since(-1)
                if e.get("kind") in self.TRIAL_KINDS and e.get("trial_session") == session_id]

    def _rebuild_trial_transcript(self, session_id: str) -> dict:
        """Re-derive the FULL transcript for a session FROM its recorded events, write it to CAS,
        and (re)point the trial://<session>/transcript ref at the new content. Re-derived on every
        turn so the three artifacts (events · CAS transcript · session record) agree BY
        CONSTRUCTION — there is no parallel transcript write that could drift from the event log.
        Returns {address, cas, turns:[...]} (the materialised transcript)."""
        turns = []
        for ev in self._trial_turn_events(session_id):
            turns.append({"kind": ev.get("kind"), "seq": ev.get("seq"), "ts": ev.get("ts"),
                          "role": ev.get("role"), "character": ev.get("character"),
                          "text": ev.get("text", "")})
        transcript = {"session": session_id, "turns": turns, "n": len(turns)}
        cas = self.store.put_content(transcript)
        addr = self._trial_transcript_addr(session_id)
        self.store.set_ref(addr, cas)
        return {"address": addr, "cas": cas, "transcript": transcript}

    def _trial_session_record(self, session_id: str, character: str | None = None) -> dict:
        """Load this trial session's record, or seed a fresh one. The record carries the cast
        member and the running turn/feedback/reflection counts so the debrief can list sessions
        without re-scanning the whole event log. Namespaced id so it never collides with a review
        session record (_load_session expects review keys: graph/cursor/items)."""
        s = self.store.load_session(session_id)
        if not s:
            s = {"id": session_id, "kind": "trial", "character": character,
                 "turns": 0, "feedback": 0, "reflections": 0, "done": False}
        if character and not s.get("character"):
            s["character"] = character
        return s

    def trial_record_turn(self, session_id: str, role: str, text: str,
                          character: str | None = None) -> dict:
        """Record ONE spoken turn of a trial conversation (role='operator'|'character'). Emits a
        DURABLE trial.turn event (_emit_durable — the record IS the behavior here; a silently
        dropped turn would make the debrief misrepresent the session, so loss must FAIL LOUD, not
        be swallowed like lenient telemetry), re-materialises the CAS transcript from the events,
        and advances the trial session record. Fail loud on empty text (no silent no-op)."""
        sid = (session_id or "").strip()
        if not sid:
            raise ValueError("trial_record_turn needs a session id (fail loud)")
        if not (text or "").strip():
            raise ValueError("trial_record_turn needs non-empty text (fail loud)")
        self._emit_durable("trial.turn", f"[{character or role}] {text[:60]}",
                           trial_session=sid, role=role, character=character, text=text)
        s = self._trial_session_record(sid, character)
        s["turns"] = s.get("turns", 0) + 1
        self.store.save_session(s)
        built = self._rebuild_trial_transcript(sid)
        return {"session": sid, "role": role, "turns": s["turns"],
                "transcript_addr": built["address"], "transcript_cas": built["cas"]}

    def trial_record_feedback(self, session_id: str, text: str,
                              character: str | None = None) -> dict:
        """Record Tim's SPOKEN feedback during a trial session (his verdict-in-flight on a voice/
        character). DURABLE (_emit_durable) + folded into the same transcript so the debrief reads
        his feedback alongside the turns. Fail loud on empty text."""
        sid = (session_id or "").strip()
        if not sid:
            raise ValueError("trial_record_feedback needs a session id (fail loud)")
        if not (text or "").strip():
            raise ValueError("trial_record_feedback needs non-empty text (fail loud)")
        self._emit_durable("trial.feedback", f"feedback: {text[:60]}",
                           trial_session=sid, role="operator", character=character, text=text)
        s = self._trial_session_record(sid, character)
        s["feedback"] = s.get("feedback", 0) + 1
        self.store.save_session(s)
        built = self._rebuild_trial_transcript(sid)
        return {"session": sid, "feedback": s["feedback"], "transcript_addr": built["address"]}

    def trial_record_reflection(self, session_id: str, text: str,
                                character: str | None = None) -> dict:
        """Record the CHARACTER's own reflection-note on the exchange (the cast member's read of
        how it went). DURABLE + in the same transcript. Fail loud on empty text."""
        sid = (session_id or "").strip()
        if not sid:
            raise ValueError("trial_record_reflection needs a session id (fail loud)")
        if not (text or "").strip():
            raise ValueError("trial_record_reflection needs non-empty text (fail loud)")
        self._emit_durable("trial.reflection", f"[{character}] reflects: {text[:50]}",
                           trial_session=sid, role="character", character=character, text=text)
        s = self._trial_session_record(sid, character)
        s["reflections"] = s.get("reflections", 0) + 1
        self.store.save_session(s)
        built = self._rebuild_trial_transcript(sid)
        return {"session": sid, "reflections": s["reflections"], "transcript_addr": built["address"]}

    def trial_transcript(self, session_id: str) -> dict:
        """Read back a trial session's FULL transcript from CAS (the debrief's ground truth). Reads
        the trial://<session>/transcript ref → CAS content. Fail loud if the session was never
        recorded (no ref) — the debrief MUST NOT confabulate from an absent transcript."""
        addr = self._trial_transcript_addr(session_id)
        cas = self.store.head(addr)
        if not cas:
            raise KeyError(
                f"no recorded transcript for trial session {session_id!r} (no ref at {addr}) — "
                f"record turns first; the debrief reads only real transcripts (fail loud).")
        return self.store.get_content(cas)

    def trial_sessions(self) -> list:
        """Every recorded trial session record (the cast walked, with counts) — what the debrief
        loads as its review set. Reads the session store + filters to kind=='trial' so it never
        picks up a review session record."""
        out = []
        for sid in self.store.list_sessions():
            s = self.store.load_session(sid)
            if s and s.get("kind") == "trial":
                out.append(s)
        return out

    def start_debrief(self, session_ids: list, host_persona: str | None = None,
                      mode: str = "walkthrough") -> dict:
        """Group F — the trial DEBRIEF, built ON the walkthrough organ (specialise, don't rebuild).
        A debrief is a review session whose items are the recorded trial sessions; a host character
        walks Tim back through each, conversationally, and his verdicts are captured via the SAME
        resolve_surfaced path the walkthrough uses.

        CRITICAL (the parallel-path trap): start_session / present_current / respond all key on
        INBOX item ids (coa→inbox.get, resolve_surfaced→inbox.get raise KeyError on a non-surfaced
        id). So we CANNOT feed raw trial-session ids into start_session. We first SURFACE each trial
        session as a review item — carrying the REAL transcript pulled from CAS — and collect the
        returned surfaced ids; coa() dumps the whole payload into the framing prompt, so embedding
        the transcript is what lets the host read it back FAITHFULLY instead of confabulating from a
        bare character name. THEN we hand those surfaced ids to start_session.

        The debrief-host persona is set GLOBALLY via set_rhm_config (coa reads rhm_config().persona;
        there is no per-session persona slot) — deliberate for the trial: one host voice frames all
        five. Returns start_session's first presentation (the host's framing of the first session)."""
        ids = list(session_ids or [])
        if not ids:
            raise ValueError("start_debrief needs at least one trial session id (fail loud)")
        if host_persona:
            self.set_rhm_config({"persona": host_persona})   # the debrief-host voice (global, deliberate)
        surfaced = []
        for sid in ids:
            transcript = self.trial_transcript(sid)          # FAIL LOUD if a session was never recorded
            rec = self._trial_session_record(sid)
            item = {"title": f"debrief · {rec.get('character') or sid}",
                    "kind": "trial_debrief", "trial_session": sid,
                    "character": rec.get("character"),
                    "turns": rec.get("turns", 0), "feedback": rec.get("feedback", 0),
                    "reflections": rec.get("reflections", 0),
                    "transcript": transcript}              # the REAL transcript — coa frames from THIS
            r = self.surface_review(item, origin="generative")  # a debrief = Tim revisiting his own trial
            surfaced.append(r["id"])
        self._emit("trial.debrief.start",
                   f"debrief started — {len(surfaced)} trial session(s) to walk",
                   sessions=ids, surfaced=surfaced)
        return self.start_session(surfaced, mode=mode)

    # ============================================================================================

    # --- the inbox: chief-of-staff triage (F1-F2) + the decision-compiler UP (C2-C3) ---
    def inbox_lanes(self) -> dict:
        """Three lanes (context-05): live escalations (pending, need the operator), resolved-for-you
        (already handled — audit), and batched walkthroughs (pending grouped by theme).

        T3-HYGIENE (filter-at-source): items tagged `test_origin` at creation (a run under
        COMPANY_TEST_RUN) are EXCLUDED from the operator's lanes — that pollution is what buried the
        real items. The exclusion is NOT silent: `counts.test_origin_excluded` reports how many were
        filtered, so a test run can still see/verify them and nothing is hidden by sleight of hand
        (fail-loud-legible). A real operator run sets no flag → no items tagged → identical to before."""
        items = self.inbox.list()
        real = [d for d in items if not d.get("test_origin")]
        excluded = len(items) - len(real)
        escalations = [d for d in real if d.get("resolved") is None]
        resolved = [d for d in real if d.get("resolved") is not None]
        batched: dict = {}
        for d in escalations:
            batched.setdefault(d["action"], []).append(d["id"])
        return {
            "live_escalations": escalations,                       # the irreducible — brought as COA
            "resolved_for_you": resolved,                          # logged for audit; needn't be worked
            "batched": {k: v for k, v in batched.items() if len(v) > 1},  # themes to handle in one sitting
            "counts": {"escalations": len(escalations), "resolved": len(resolved),
                       "test_origin_excluded": excluded},
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

    def surface_output(self, graph_id: str, node_id: str) -> dict:
        """F2: route a node's RESULT to the decision surface. Composes the EXISTING surfaced/inbox
        path (no new mechanism): read the node's output from live state (the backend is truth — the
        client passes only {node, graph_id}, never the output itself; canvas reflects-never-owns),
        then surface it as a 'result' decision so it lands in `live_escalations` and is drillable via
        `coa` like any other surfaced item. Fail loud if the node is absent or has no output yet."""
        st = self.state(graph_id)
        node = next((n for n in st["nodes"] if n["id"] == node_id), None)
        if node is None:
            raise KeyError(f"no node {node_id!r} in graph {graph_id!r}")
        out = node.get("output")
        if out is None or str(out) == "":
            raise ValueError(f"node {node_id!r} has no output to surface yet — run it first (fail loud)")
        sid = self.inbox.surface("result",
                                 {"name": f"output · {node_id}", "node": node_id,
                                  "graph_id": graph_id, "output": str(out)},
                                 default="reject")
        # emit as 'ask' so the live SSE inbox-refresh path (App.tsx kinds: ask|reject|resolve|…) lights
        # up; the operator's button also poll()s for instant local feedback regardless of the stream.
        self._emit("ask", f"a result was surfaced for your decision: {node_id}", surfaced=sid)
        return {"id": sid, "node": node_id, "name": f"output · {node_id}"}

    # --- A: the review queue (one inbox, all sources; SEPARATE status lifecycle) ---
    def surface_review(self, item: dict, origin: str = "responsive") -> dict:
        """Surface a `review` decision into the SAME surfaced/inbox store (no parallel queue, A).
        `origin`: 'responsive' (a need raised by the build loop / a result) or 'generative' (an idea
        Tim threw in). The item carries a SEPARATE `status` (starts 'inbox') so the walk-lifecycle never
        overloads `resolved` — the predicate `resolved is None` keeps it a live escalation until Tim
        resolves it. Fail loud on a non-dict item. (E1's build loop calls this in place of WALKTHROUGH.md.)"""
        if not isinstance(item, dict):
            raise TypeError(f"surface_review needs a dict item, got {type(item).__name__}")
        sid = self.inbox.surface_review(item, origin=origin)
        # emit 'ask' so the SSE inbox-refresh lights up (same kind surface_output uses).
        self._emit("ask", f"a review item was surfaced ({origin}): {item.get('title', item.get('name', sid))}",
                   surfaced=sid, origin=origin)
        return {"id": sid, "origin": origin, "status": "inbox"}

    def idea_capture(self, text: str) -> dict:
        """A4 — capture a fleeting idea as a GENERATIVE review item (the idea-capture organ). It lands
        in the same queue; the operator triages it later. Fail loud on empty text (no silent no-op)."""
        t = (text or "").strip()
        if not t:
            raise ValueError("idea_capture needs non-empty text (fail loud)")
        return self.surface_review({"title": t[:80], "idea": t, "kind": "idea"}, origin="generative")

    # --- B: the walkthrough engine — a review session IS a Graph, run by the existing scheduler ---
    # No bespoke iterator + no scheduler change: a review-item = a STEP node whose readiness waits on a
    # human-writable `go` input (the scheduler already waits on an unwired/unresolved declared port,
    # scheduler.py:62-67). Each step has its OWN unresolved go-gate, so a fixpoint run() can't overrun
    # one step into the next (guide B). `next()` OPENS the current gate by writing the go-address.
    #
    # CARRIER node-type: any registered process node with a single declared input port works purely as a
    # resolution gate (the body is irrelevant — we read state, not the step's output). `uppercase` has
    # PORTS_IN={'text':'Text'}. Named once so swapping to a dedicated step/gate type later is one line.
    # CROSS-LANE SEAM (B-backend ↔ SCHED): SCHED owns nodes/gate.py + per-port emit for B5 BRANCHING;
    # this linear pacing deliberately does NOT depend on it (territory + don't couple to an unbuilt lane).
    STEP_CARRIER = "uppercase"
    GATE_CARRIER = "constant"     # the per-step go-SOURCE: a node whose output we write directly via next()

    @staticmethod
    def _session_graph_id(session_id: str) -> str:
        return f"review-{session_id}"

    def _go_addr(self, session_id: str, position: int) -> str:
        """The go-gate address for step `position` — the source node's logical output (compile.py form)."""
        return f"run://{self._session_graph_id(session_id)}/go{position}"

    def start_session(self, item_ids: list, mode: str = "walkthrough") -> dict:
        """Compile a review-session into a Graph the existing scheduler runs, operator-paced (B).
        For each item i: a go-SOURCE node `go{i}` (constant, unwired → never auto-fires → its address
        stays unresolved = the gate) wired into a STEP node `step{i}` (carrier) on its `text` port. The
        step thus waits until next() writes `go{i}`'s address. Persists the session record atomically
        (save_session) + the graph. The session is server-authoritative; the canvas reflects it."""
        items = list(item_ids or [])
        if not items:
            raise ValueError("start_session needs at least one item id (fail loud)")
        if mode not in self.MODES:
            raise ValueError(f"unknown session mode {mode!r} — one of {self.MODES}")
        import time as _t
        session_id = f"{int(_t.time())}-{len(items)}"
        gid = self._session_graph_id(session_id)
        nodes, edges = [], []
        for i, _item in enumerate(items):
            # go-SOURCE `go{i}` (constant, PORTS_IN={}) wired into STEP `step{i}` (carrier) on `text`.
            # The step waits until go{i}'s OUTPUT ADDRESS resolves (scheduler readiness, scheduler.py:62-67).
            nodes.append(NodeInstance(id=f"go{i}", type=self.GATE_CARRIER, config={"value": ""}))
            nodes.append(NodeInstance(id=f"step{i}", type=self.STEP_CARRIER, config={}))
            edges.append(Edge(from_node=f"go{i}", from_port="value", to_node=f"step{i}", to_port="text"))
        g = Graph(id=gid, nodes=nodes, edges=edges)
        self.store.save_graph(g)
        # THE GATE INVARIANT (load-bearing — do not break): a `constant` go-source has PORTS_IN={} so it
        # WOULD auto-fire on a plain run() and open EVERY gate at once. What actually holds the gates closed
        # is that next() runs the session graph with ALL `go*` nodes in `pause` (so none auto-fire), and
        # opens ONLY the current step's gate by WRITING that go-source's output address directly
        # (set_ref+put_content). => The session graph MUST NEVER be run un-paused over its go-sources; the
        # human-paced "go" signal is the hand-written address, not the source firing. (Removing the pause
        # silently breaks pacing — every step would fire on the first Next; no test would catch it.)
        session = {"id": session_id, "graph": gid, "mode": mode, "items": items,
                   "cursor": 0, "opened": [], "done": False}
        self.store.save_session(session)
        self._emit("review.start", f"review session {session_id} started — {len(items)} item(s), mode={mode}",
                   session=session_id, items=items, mode=mode)
        return self.present_current(session_id)

    def _load_session(self, session_id: str) -> dict:
        s = self.store.load_session(session_id)
        if not s:
            raise KeyError(f"no review session {session_id!r}")
        return s

    def _registry_ui_target(self, payload: dict) -> str:
        """T0-KEYSTONE (backend half) — derive a REGISTRY-VALID `ui://` target for a review item's
        payload, so the walkthrough's view-drive (FE `resolveUiTarget(session.raw.ui_target)`) actually
        moves the operator's view to the thing the step concerns. The FE validates the ref against the
        live UI registry (`/api/ui_info` → build_ui_info) and FAILS LOUD on an unknown ref — so this
        MUST emit a ref the registry knows. The registry (UI_REGISTRY) contains:
          • ui://canvas/<node-id>  (camera path — the FE only drives if that node is on the loaded graph)
          • ui://canvas/*          (the whole canvas)
          • ui://chrome/{toolbar,inspector,inbox,activity,chat,workshop}  (DOM-resolved chrome regions)
        Mapping (deterministic, never invents): if the payload references a specific NODE (a result
        surfaced from a node, or a build_result_review tied to a node) → ui://canvas/<node-id> (point at
        the node). Otherwise the item is about the review queue itself → ui://chrome/inbox (a node-less
        build/idea/review item — the safe, always-registered target). Registry-is-truth: every branch
        returns a ref present in UI_REGISTRY (no fabrication). This stamps INTO the payload (what `raw`
        carries) — the additive field the FE reads — WITHOUT removing the top-level ui://review/<id>."""
        p = payload or {}
        node = p.get("node")                               # surface_output result items carry the node id
        if isinstance(node, str) and node.strip():
            return f"ui://canvas/{node.strip()}"
        return "ui://chrome/inbox"                          # node-less items → the inbox chrome region

    def present_current(self, session_id: str) -> dict:
        """B: the node at the cursor — the next unresolved go-gate — with its `coa` framing + `ui://`
        target. Fail-safe: if `coa` errors (LLM down), present the RAW payload, NEVER block the walk (D)."""
        s = self._load_session(session_id)
        cur = s["cursor"]
        if s.get("done") or cur >= len(s["items"]):
            return {"session": session_id, "done": True, "cursor": cur, "total": len(s["items"])}
        item_id = s["items"][cur]
        framing, raw = None, None
        try:
            c = self.coa(item_id)                          # decision-compiler UP (D1, reuse)
            framing, raw = c.get("framing"), c.get("raw")
        except Exception as e:                             # FAIL-SAFE: raw payload, never block (guide D)
            d = self.inbox.get(item_id)
            raw = d.get("payload") if d else None
            framing = None
            self._emit("warning", f"coa failed for {item_id} ({type(e).__name__}) — presenting raw payload")
        # T0-KEYSTONE (backend half): STAMP a registry-valid `ui_target` INTO the payload the FE reads as
        # `session.raw.ui_target`. Before this fix nothing wrote a payload-level ui_target, so the FE's
        # per-step view-drive (resolveUiTarget(session.raw?.ui_target)) was ~always undefined → the
        # keystone "the RHM moves your view to the thing it asks about" silently no-op'd. We stamp it
        # onto the presented `raw` (additively — never removing the top-level ui://review/<id>). It is
        # NOT persisted back to the surfaced item (this is a presentation projection — reflects-never-
        # owns), only carried on the response the walkthrough card reads. (FE proof is a separate lane —
        # this is the backend half; at most needs-tim until the FE drive is verified by use.)
        if isinstance(raw, dict) and "ui_target" not in raw:
            raw = dict(raw)
            raw["ui_target"] = self._registry_ui_target(raw)
        # mark presented (lifecycle status only — never touches `resolved`, so it stays a live escalation).
        try:
            self.inbox.set_status(item_id, "presented")
        except (KeyError, ValueError):
            pass
        return {"session": session_id, "cursor": cur, "total": len(s["items"]),
                "item": item_id, "framing": framing, "raw": raw,
                "ui_target": f"ui://review/{item_id}",      # the step's present target (C1 addressing)
                "done": False}

    def respond(self, session_id: str, choice: str, reason: str = "") -> dict:
        """B→D: record the operator's verdict for the CURRENT step, tagged with the session + position
        (the reuse of resolve_surfaced — no parallel record path). Does NOT advance; `next()` does (B)."""
        s = self._load_session(session_id)
        cur = s["cursor"]
        if cur >= len(s["items"]):
            raise ValueError(f"session {session_id!r} has no current item to respond to (fail loud)")
        item_id = s["items"][cur]
        return self.resolve_surfaced(item_id, choice, reason, session_id=session_id, position=cur)

    def next(self, session_id: str) -> dict:
        """B: the Next page-turn. WRITES the current step's go-address (so the scheduler fires that step;
        the cascade stalls at the NEXT step's still-unresolved gate), advances the cursor, emits
        `review.advance`, returns the next presentation. Idempotent past the end (done).

        ATOMIC cursor advance (concurrency): the load→run→save is a read-modify-write; under the threading
        bridge two concurrent next() calls would both read cursor=N and one advance is LOST. We take the
        per-session lock AND re-load the session FRESH inside it (compare-and-set against the substrate),
        so each next() advances by exactly one distinct step — N concurrent calls = N distinct advances."""
        with self._session_lock(session_id):
            s = self._load_session(session_id)             # re-read INSIDE the lock — the authoritative cursor
            cur = s["cursor"]
            if cur >= len(s["items"]):
                if not s.get("done"):
                    s["done"] = True
                    self.store.save_session(s)
                return {"session": session_id, "done": True, "cursor": cur, "total": len(s["items"])}
            # OPEN this step's gate: write the go-source's logical output address directly (set_ref+
            # put_content — we don't FIRE the source, we resolve its address by hand; the human "go" signal).
            go = self._go_addr(session_id, cur)
            cas = self.store.put_content(f"go:{session_id}:{cur}")
            self.store.set_ref(go, cas)
            if cur not in s.setdefault("opened", []):
                s["opened"].append(cur)
            # run the session graph: only the now-opened step(s) become ready; later steps wait on gates.
            # Pause every go-source so a PORTS_IN={} constant can't auto-fire and open all gates at once.
            gid = s["graph"]
            g = self.store.load_graph(gid)
            pause = [n.id for n in g.nodes if n.id.startswith("go")] if g else []
            self.run(gid, pause=pause)                      # AUTO via guard; fires the opened step(s)
            s["cursor"] = cur + 1
            if s["cursor"] >= len(s["items"]):
                s["done"] = True
            self.store.save_session(s)                      # commit the advance BEFORE releasing the lock
            cursor_now, done_now, total = s["cursor"], s["done"], len(s["items"])
        self._emit("review.advance", f"review session {session_id} → step {cursor_now}",
                   session=session_id, cursor=cursor_now, total=total)
        if done_now:
            return {"session": session_id, "done": True, "cursor": cursor_now, "total": total}
        return self.present_current(session_id)

    def session_status(self, session_id: str) -> dict:
        """B: the session's live status — cursor, total, mode, which steps are opened, done."""
        s = self._load_session(session_id)
        return {"session": session_id, "cursor": s["cursor"], "total": len(s["items"]),
                "mode": s.get("mode"), "items": s["items"], "opened": s.get("opened", []),
                "done": bool(s.get("done"))}

    # --- E: the channel back — the system acts, provably from a recorded verdict (the derived-from gate) ---
    def review_verdicts(self, since: int = -1) -> list:
        """E: the recorded verdicts the build loop reads from the STORE (not from Claude Code). Reads
        events_since(cursor) filtered to kind=='resolve' & choice=='approve' (the resolve event carries
        seq·surfaced·choice·reason). Cross-session/crash-safe by construction (it tails the shared log)."""
        return [e for e in self.store.events_since(since)
                if e.get("kind") == "resolve" and e.get("choice") == "approve"]

    def commit_criterion(self, criterion_id: str, sid: str, derived_from: int) -> dict:
        """E: write a criterion as a GOVERNED action whose authorization is READ FROM THE SUBSTRATE —
        REQUIRES `derived_from` = a resolve event's unique `seq`, and verifies the THREE-PART BIND:
        that event is kind=resolve · choice=approve · surfaced==sid, else raise GovernanceError (mirrors
        apply_node→is_approved). Bound to the event `seq` (unique), NOT `sid` (repeats on re-resolve).
        Emits the write WITH `derived_from` for audit. (The loop that CALLS this is lane X.)"""
        if not isinstance(derived_from, int):
            raise GovernanceError(f"commit_criterion requires derived_from = a resolve event seq (int), "
                                  f"got {type(derived_from).__name__} — refused (no ungoverned criterion write)")
        ev = next((e for e in self.store.events_since(-1) if e.get("seq") == derived_from), None)
        if ev is None:
            raise GovernanceError(f"commit_criterion: no event with seq={derived_from} — cannot derive a "
                                  f"criterion from a verdict that doesn't exist (fail loud)")
        if not (ev.get("kind") == "resolve" and ev.get("choice") == "approve" and ev.get("surfaced") == sid):
            raise GovernanceError(
                f"commit_criterion: event seq={derived_from} does not satisfy the three-part bind "
                f"(kind=resolve·choice=approve·surfaced=={sid!r}) — got "
                f"kind={ev.get('kind')!r} choice={ev.get('choice')!r} surfaced={ev.get('surfaced')!r}. Refused.")
        self._emit("criterion.commit", f"criterion {criterion_id} committed (derived from verdict seq={derived_from})",
                   criterion=criterion_id, surfaced=sid, derived_from=derived_from)
        return {"criterion": criterion_id, "surfaced": sid, "derived_from": derived_from, "committed": True}

    def resolve_verdicts_since(self, since: int = -1) -> list:
        """E3: ALL resolve verdicts since the cursor — approve AND reject/needs-change/decide — so the
        build loop can route each. `review_verdicts` (above) is the APPROVE-only slice the commit path
        reads; this is its sibling that also surfaces the negative verdicts the REQUEUE path needs (they
        are invisible to review_verdicts by design). Same shared event log → same crash/cross-session
        safety. Each event carries seq·surfaced·choice·reason (suite.py resolve event)."""
        return [e for e in self.store.events_since(since) if e.get("kind") == "resolve"]

    def requeue_from_verdict(self, sid: str, derived_from: int, note: str = "") -> dict:
        """E3: turn a NEGATIVE verdict (reject / needs-change / actionable-WHY) into a NEW review item —
        the reuse-not-parallel requeue path (it surfaces through the SAME inbox via `surface_review`, no
        second queue). GOVERNED like commit_criterion: REQUIRES `derived_from` = the resolve event's
        unique `seq`, and verifies the bind (kind=resolve · surfaced==sid · choice != approve) so a
        requeue can only be derived from a real, non-approving verdict. The WHY (reason/note) rides along
        — the actionable signal that generalises (I1). The new item starts `inbox`/responsive (it came
        from a build need). Operator-only resolve is untouched: this WRITES a derived item, it never
        resolves anything."""
        if not isinstance(derived_from, int):
            raise GovernanceError(f"requeue_from_verdict requires derived_from = a resolve event seq (int), "
                                  f"got {type(derived_from).__name__} — refused (no ungoverned requeue)")
        ev = next((e for e in self.store.events_since(-1) if e.get("seq") == derived_from), None)
        if ev is None:
            raise GovernanceError(f"requeue_from_verdict: no event with seq={derived_from} — cannot requeue "
                                  f"from a verdict that doesn't exist (fail loud)")
        if not (ev.get("kind") == "resolve" and ev.get("surfaced") == sid and ev.get("choice") != "approve"):
            raise GovernanceError(
                f"requeue_from_verdict: event seq={derived_from} is not a non-approving resolve of {sid!r} "
                f"(kind=resolve · surfaced=={sid!r} · choice!=approve) — got kind={ev.get('kind')!r} "
                f"choice={ev.get('choice')!r} surfaced={ev.get('surfaced')!r}. Refused.")
        item = {"requeued_from": sid, "verdict": ev.get("choice"),
                "why": note or ev.get("reason", ""), "derived_from": derived_from}
        new_sid = self.inbox.surface_review(item, origin="responsive")
        self._emit("review.requeue",
                   f"requeued {sid} ({ev.get('choice')}) → {new_sid} (derived from verdict seq={derived_from})",
                   surfaced=new_sid, requeued_from=sid, derived_from=derived_from, verdict=ev.get("choice"))
        return {"requeued_from": sid, "new_item": new_sid, "verdict": ev.get("choice"),
                "derived_from": derived_from}

    # ============================================================================================
    # The Decision→Implementation Wire (Group W) — recorded decision → governed dispatch to Claude
    # Code → verify → result back → terminal status. No new gate, no confidence value, no second
    # queue: it REUSES the derived_from three-part bind (commit_criterion), the append-only event
    # log (exactly-once + visibility), POLICY (auto-vs-surface), and the separate `status` lane
    # (closes without writing the operator `resolved` field). Kept OFF the MCP face (not in
    # RHM_VERBS) — the RHM proposes/surfaces; it never dispatches a build of its own authority.
    # ============================================================================================

    def _verify_resolve_bind(self, sid: str, derived_from: int, *, require_approve: bool = True):
        """The shared three-part-bind verifier (factored from commit_criterion, suite.py:1114).
        REQUIRES `derived_from` = a resolve event's unique `seq`; verifies kind=resolve · surfaced==sid
        · (choice==approve when require_approve). Returns the bound event, or raises GovernanceError
        (fail loud). The bind is per-unique-seq (not per-sid), the anti-double-action guarantee."""
        # bool is a subclass of int (isinstance(True, int) is True) and True == 1, so a plain
        # isinstance check would let derived_from=True bind to seq 1 — a truthy caller FLAG
        # authorizing the first item's build. Reject bool explicitly: a seq is a genuine int.
        if type(derived_from) is not int:
            raise GovernanceError(
                f"dispatch requires derived_from = a resolve event seq (a genuine int, not bool), got "
                f"{type(derived_from).__name__} — refused (no ungoverned dispatch; authorization is the "
                f"substrate seq-bind, never a caller flag)")
        ev = next((e for e in self.store.events_since(-1) if e.get("seq") == derived_from), None)
        if ev is None:
            raise GovernanceError(
                f"dispatch: no event with seq={derived_from} — cannot derive a build from a verdict that "
                f"doesn't exist (fail loud)")
        ok = ev.get("kind") == "resolve" and ev.get("surfaced") == sid
        if require_approve:
            ok = ok and ev.get("choice") == "approve"
        if not ok:
            raise GovernanceError(
                f"dispatch: event seq={derived_from} does not satisfy the three-part bind "
                f"(kind=resolve·surfaced=={sid!r}" + ("·choice=approve" if require_approve else "") +
                f") — got kind={ev.get('kind')!r} choice={ev.get('choice')!r} "
                f"surfaced={ev.get('surfaced')!r}. Refused.")
        return ev

    def surface_build_intent(self, spec: str, scope: list[str] | None = None,
                             consequence_class: str = "decision_build", why: str = "") -> dict:
        """W4 PRODUCER: mint a build-intent item — a decision that, once the operator approves it,
        AUTHORIZES an autonomous build of a DECLARED scope. It is distinguished from a plain
        criterion/review by `intent="build"` (the discriminator §W2 — `action` is the governance
        class, so the intent rides the payload) and carries its declared `scope` (the paths it may
        touch) + `consequence_class` (the POLICY class the pre-dispatch gate keys on). The operator's
        `approve` is therefore approve OF THIS SCOPE (legible consent), not a bare agree.

        Surfaced through the SAME inbox (no parallel queue). `resolved` stays None → a live escalation
        until the operator resolves it via /api/resolve (operator-only preserved). Returns {id, ...}.

        Scope entries are normalized (blank entries dropped). An EMPTY declared scope is NOT a soft
        allow-all: the dispatch-time scope-diff treats empty scope as DENY-ALL (_in_any_scope returns
        False for every path), so a build with no declared scope can NEVER close `implemented` — every
        changed path reads as an overrun and surfaces back. This is the durable enforcement (the
        vacuous-enforcement hole closed at the gate that runs, not only at surface time)."""
        scope = [s for s in (scope or []) if isinstance(s, str) and s.strip()]
        payload = {"intent": "build", "spec": spec, "scope": scope,
                   "consequence_class": consequence_class, "why": why or spec}
        # action="review" so it walks the same review lifecycle/UI; the build-intent discriminator is
        # payload["intent"]=="build" (action is the governance class, which surface_review hardcodes).
        sid = self.inbox.surface("review", payload, default="reject", resolved=None,
                                 status="inbox", origin="responsive")
        self._emit("decision.intent",
                   f"build-intent surfaced ({consequence_class}, scope={scope or '∅'}) — awaiting operator approval",
                   surfaced=sid, intent="build", consequence_class=consequence_class, scope=scope)
        return {"id": sid, "intent": "build", "scope": scope, "consequence_class": consequence_class}

    @staticmethod
    def is_build_intent(decision: dict) -> bool:
        """The loop's discriminator (§W2): distinguish a 'go build this' decision from a 'mark a
        criterion done' approve. True only when the payload carries intent=='build'."""
        return bool(decision) and (decision.get("payload") or {}).get("intent") == "build"

    def _already_dispatched(self, derived_from: int) -> bool:
        """EXACTLY-ONCE (Round 2 Hole 1): the durable claim lives in the append-only crash-safe event
        log, NOT a cursor/lock. A prior `decision.dispatch` keyed on this resolve `seq` means this work
        already launched — refuse the second (checked BEFORE we emit our own claim, so emit-then-check
        can't find its own emission)."""
        return any(e.get("kind") == "decision.dispatch" and e.get("derived_from") == derived_from
                   for e in self.store.events_since(-1))

    # ============================================================================================
    # WIRE-HARDEN (H1–H8) — the wire's definition-of-done == the HUMAN BUILD LOOP's discipline.
    # ------------------------------------------------------------------------------------------
    # The wire is an autonomous build engine; its old "verified" was essentially "claude -p exited
    # and a file changed" — far weaker than the loop, which runs the suites + drift + a separate
    # review. That gap let the reverse incident through (a node-type built but the self-description
    # NOT refreshed → drift went red, silently). These helpers make the wire's verify REAL,
    # fail-loud, and surface-back-on-miss: the build re-discovers into the LIVE system (H3),
    # regenerates the factual self-description (H2), runs the affected acceptance suites + drift
    # (H1/H2), runs an adversarial CRITIC (H5), and refuses to auto-close anything that touches an
    # operator-facing surface (H4 — form can't be machine-verified until the design system exists).
    # ANY miss → fail loud → surface back, never a silent close (H6). All steps are INJECTABLE so
    # tests prove them deterministically without burning a real `claude -p` or a slow suite run.
    # ============================================================================================

    # the self-description files a build may always touch (H8) — H7 instructs the build to update them,
    # so they are upkeep, not out-of-scope wandering. The overrun check (H8) treats these as in-scope.
    _SELF_DESC_FILES = ("AGENTS.md", "MAP.md", "STATE.md")
    # operator-facing surface (H4): a build that changes anything under these CANNOT auto-close — its
    # FORM is unverifiable until the design system + design-critic/design-lint are wired. It surfaces.
    _SURFACE_PREFIXES = ("canvas/",)

    def _affected_suites(self, changed_files: list[str], scope: list[str]) -> list[str]:
        """H1 — which acceptance suites COULD this build break. The deterministic gate (no confidence):
        a change under `runtime/` or `store/` etc. can break the suites that exercise that module, and
        a node-type change can break node/registry/drift suites — so we always include `drift_acceptance`
        (H2) + the wire suites (this verify path itself), and add any suite whose name shares a module
        token with a changed/scoped path. The default verifier runs THESE (not all tests/*.py — several
        burn live models / are slow); the task allows 'at least the suites the change could affect + drift'.
        A node-type build (`nodes/`) → node/registry/drift/wire suites must stay green."""
        all_suites = set(self._acceptance_suites())
        affected = set()
        # ALWAYS: drift (the reverse incident) + the wire's own suites (this path must keep holding).
        for must in ("drift_acceptance", "wire_acceptance", "wire_loop_acceptance", "wire_adversarial"):
            if must in all_suites:
                affected.add(must)
        # module tokens touched by the change (changed paths + declared scope dirs).
        tokens = set()
        for p in list(changed_files or []) + list(scope or []):
            head = (p or "").strip().lstrip("./").split("/")[0]
            if head and head.endswith(".py"):           # a top-level file like 'MAP.md' has no module token
                continue
            if head:
                tokens.add(head.lower())
        # a node-type change can break the registry/drift/compose proofs — pull those in by token too.
        for s in all_suites:
            sl = s.lower()
            if any(tok and tok in sl for tok in tokens):
                affected.add(s)
            # a nodes/ change is a registry change — the registry/type suites guard it.
            if "nodes" in tokens and any(k in sl for k in ("registry", "e4", "compose", "walking", "polr")):
                affected.add(s)
        return sorted(affected)

    def _run_suites(self, suites: list[str], *, runner=None) -> tuple[bool, str]:
        """H1 — run the given acceptance suites as the loop does (`./.venv/bin/python tests/<s>.py`) and
        return (all_green, reason). FAIL LOUD: a non-zero exit = that suite broke → not green. `runner`
        is INJECTABLE (tests supply a deterministic pass/fail map so no slow/real suite is burned); the
        DEFAULT runner is the real subprocess so a live build is gated for real. A suite that ERRORS to
        run (missing interpreter, crash) is treated as RED (a build that breaks the harness is not done)."""
        if not suites:
            return True, "no affected suites to run"
        run = runner or self._default_suite_runner
        failed = []
        for s in suites:
            try:
                ok, detail = run(s)
            except Exception as e:                          # a runner crash is a RED suite, never a silent pass
                ok, detail = False, f"runner crashed on {s}: {type(e).__name__}: {e}"
            if not ok:
                failed.append(f"{s} ({detail})" if detail else s)
        if failed:
            return False, "acceptance suite(s) FAILED: " + "; ".join(failed)
        return True, f"all {len(suites)} affected suite(s) green: {', '.join(suites)}"

    def _default_suite_runner(self, suite: str) -> tuple[bool, str]:
        """The REAL suite runner (default): spawn the suite as the convergence record prescribes. A
        non-zero exit = RED (fail loud). Uses the repo's venv python if present, else the running one."""
        import subprocess, sys as _sys
        venv_py = os.path.join(self._repo_root, ".venv", "bin", "python")
        py = venv_py if os.path.exists(venv_py) else _sys.executable
        path = os.path.join(self._repo_root, "tests", suite + ".py")
        if not os.path.exists(path):
            return False, f"suite file missing: {path}"
        proc = subprocess.run([py, path], cwd=self._repo_root, capture_output=True, text=True,
                              timeout=600)
        if proc.returncode != 0:
            tail = (proc.stdout or "")[-400:] + (proc.stderr or "")[-400:]
            return False, f"exit={proc.returncode}; tail={tail!r}"
        return True, "exit=0"

    def _make_live_and_refresh(self) -> tuple[bool, str]:
        """H3 + H2a — re-discover into the RUNNING system so a new node-type is LIVE (in self.registry,
        not just on disk), THEN regenerate the factual self-description blocks FROM the now-current
        registry. This is the exact fix for the reverse incident: rediscover → refresh BEFORE the drift
        check, so MAP/STATE reflect the new capability and drift reads GREEN. Uses rediscover() (clear +
        discover) so a removed/renamed node un-registers too (the wire can do anything, unlike apply_node
        which only adds). FAIL LOUD: a syntactically broken node makes exec_module raise during
        rediscover — that is a legitimate verify MISS (the build broke the registry), returned as a
        reason, never crashing dispatch_decision."""
        try:
            self.registry.rediscover([self.nodes_dir])
        except Exception as e:
            return False, (f"re-discovery FAILED ({type(e).__name__}: {e}) — the build left the node "
                           f"registry un-loadable (a broken node-type). Not live; surfaced back.")
        try:
            self.refresh_self_description()                 # H2a: factual MAP/STATE blocks, from the live registry
        except Exception as e:
            return False, f"self-description refresh FAILED ({type(e).__name__}: {e}) — surfaced back."
        return True, "re-discovered into the live registry + refreshed the factual self-description"

    def _touches_surface(self, changed_files: list[str]) -> list[str]:
        """H4 — did the build change an operator-facing surface (anything under canvas/)? Such a change
        CANNOT auto-close: its FORM (design-system components + tokens, coherent layout — AGENTS.md
        rule 9) is the product bar, and there is NO design system wired to machine-check it yet. So a
        surface-touching build surfaces for review instead of closing. Returns the offending paths."""
        out = []
        for p in (changed_files or []):
            q = (p or "").strip().lstrip("./")
            if any(q == pre.rstrip("/") or q.startswith(pre) for pre in self._SURFACE_PREFIXES):
                out.append(p)
        return out

    def _design_critic(self, changed_files: list[str]) -> tuple[bool, str]:
        """H4 FORM slot (fail-safe seam) — where a design-critic AGENT + a design-lint will plug in
        once the design system exists. Until then FORM is UNVERIFIABLE for any operator-facing surface,
        so this returns (False, reason) for a surface-touching build → the build CANNOT claim 'done' and
        surfaces for review. A pure-backend build (no surface change) has no form to grade → (True, …),
        so it may proceed through H1/H2. This is the path-of-least-resistance default: the correct
        action (don't auto-close an unverifiable surface) is the easy one. NAMED hook, not a comment:
        replace the body with `design_critic_agent(changed_files)` + `design_lint(changed_files)` when
        the design system is wired (off-token / bespoke-element → fail loud, same shape as here)."""
        surface = self._touches_surface(changed_files)
        if surface:
            return (False, f"FORM unverifiable: this build changed operator-facing surface(s) {surface} "
                           f"but no design system / design-critic is wired yet — FORM is half of done "
                           f"(AGENTS.md rule 9), so it CANNOT auto-close. Surfaced for design review.")
        return True, "no operator-facing surface touched → no FORM gate (backend build may proceed)"

    def _critic_recheck(self, decision: dict, result: dict, *, critic=None) -> tuple[bool, str]:
        """H5 — an ADVERSARIAL re-check, SEPARATE from the builder's self-report (the builder defaults
        to function + grades itself generously — exactly why correctness gets its own adversary). A
        first-class part of the verify, not optional. The DEFAULT critic is deterministic + structural
        (no confidence value): a consequential build must actually have changed something and reported
        success; a launch that claims success with an empty change-set is a no-op masquerading as done.
        INJECTABLE so a stronger critic (or a test) can supply its own verdict."""
        run = critic or self._default_critic
        return run(decision, result)

    @staticmethod
    def _default_critic(decision: dict, result: dict) -> tuple[bool, str]:
        """The default adversarial critic (deterministic): re-derive the verdict from the result rather
        than trust the builder's narration. A 'success' with no change-set is not an implementation; a
        reported failure is a failure regardless of narration."""
        if not result.get("success"):
            return False, f"critic: builder reported failure (exit={result.get('exit_code')})"
        if not result.get("changed_files"):
            return False, "critic: success claimed with an EMPTY change-set — a no-op is not a build"
        return True, "critic: build is consequential (success + non-empty change-set)"

    def _wire_verify(self, decision: dict, result: dict, scope: list[str], *,
                     suite_runner=None, critic=None) -> tuple[bool, str]:
        """The wire's DEFINITION-OF-DONE — the loop's discipline, as ONE fail-loud gate (H1·H2b·H4·H5).
        Order matters (the reverse-incident fix): the build is ALREADY made LIVE + the factual
        self-description ALREADY refreshed (H3/H2a, hoisted to run unconditionally in dispatch_decision
        BEFORE any verifier — so a loop's injected scenario verifier can't lose the refresh). This gate
        then runs the affected suites + drift (H1/H2b) against the now-current state, the adversarial
        critic (H5), and the FORM gate (H4). ANY miss → (False, reason) → the caller surfaces back,
        never closes (H6). All steps injectable for deterministic tests. Returns (passed, reason)."""
        changed = result.get("changed_files", [])
        # NOTE: H3 + H2a (make-it-live + refresh-self-description) is hoisted OUT of here to run
        # UNCONDITIONALLY in dispatch_decision BEFORE the verifier branch — so even a loop that injects
        # its own scenario `verifier` (which bypasses this heavy default) cannot silently lose the
        # refresh (the exact reverse-incident class this lane kills). By the time _wire_verify runs, the
        # registry is already live + the self-description already refreshed. We re-assert it here ONLY
        # as a defensive no-op is unnecessary (it already ran); we go straight to the gates below.
        # H1 + H2b — the affected acceptance suites + drift must be GREEN (this is where the reverse
        # incident would now be CAUGHT: drift_acceptance is always in the affected set and runs AFTER
        # the refresh, so a build that didn't leave drift green does not close).
        suites = self._affected_suites(changed, scope)
        ok, why = self._run_suites(suites, runner=suite_runner)
        if not ok:
            return False, why
        # H5 — the adversarial critic, separate from the builder's self-report.
        ok, why = self._critic_recheck(decision, result, critic=critic)
        if not ok:
            return False, why
        # NOTE: H4 (the FORM gate — a surface-touching build cannot auto-close) is NOT here. It is a
        # STRUCTURAL gate, like the refresh + the scope-diff, so it runs UNCONDITIONALLY in
        # dispatch_decision — NOT only on this default path. Otherwise a loop that injects its own
        # scenario `verifier` (which bypasses this heavy default) could close a surface build with an
        # unverifiable FORM. The partition: structural gates (refresh · FORM · scope-diff) =
        # unconditional; verification-QUALITY (the affected suites + the critic) = replaceable by an
        # injected verifier. So _wire_verify proves only suites + critic.
        return True, ("wire verify PASSED: live+refreshed · affected suites + drift green · critic ok — "
                      + why)

    def dispatch_decision(self, sid: str, derived_from: int, *, launcher=None,
                          verifier=None, suite_runner=None, critic=None, repo: str | None = None) -> dict:
        """W2·W4·W1·W3·W5 — the governed dispatch verb. Run an implementation job ONLY when bound to
        a real operator approve via `derived_from` = the resolve event's unique `seq`, and ONLY once.

        Sequence (CHECK → CLAIM → GATE → LAUNCH → VERIFY → CLOSE-or-SURFACE):
          1. verify the three-part bind (kind=resolve·surfaced==sid·choice=approve) — else GovernanceError.
          2. require it IS a build-intent item (the discriminator) — else refuse.
          3. EXACTLY-ONCE: refuse if a `decision.dispatch` already exists for this `seq` (fail loud).
          4. W4 PRE-DISPATCH gate on the DECLARED consequence class, keyed on POLICY POSTURE: ONLY an
             AUTO-posture class auto-dispatches. CONFIRM/SURFACE/LOCKED all surface for the operator
             BEFORE building (refuse to auto-run a non-AUTO build). AUTO means auto-DISPATCH on the
             operator's approve (no second gate before building) — it does NOT mean auto-CLOSE without
             review. decision_build is the AUTO class; CONFIRM/SURFACE/LOCKED classes surface here.
          5. emit `decision.dispatch` (the durable exactly-once claim) BEFORE launching — so a crash
             after launch refuses re-launch on restart.
          6. launch (W1, runtime/implement.launch — injectable for tests).
          7. verify by USE (W3, injectable). On FAIL → surface_review directly with the reason; the
             item does NOT close (no `implemented`). Do NOT reuse requeue_from_verdict (it needs
             choice!=approve; a build follows an approve).
          8. W4 scope-diff: changed paths outside the declared scope → surface back, do NOT close.
          9. CLOSE + SURFACE-FOR-REVIEW (guarded): write status='implemented' AND surface a review item
             through guard("code_build",…, confirmed=verify_passed) — an unverified close RAISES
             (mirrors apply_node). `implemented` means "done AND surfaced for review", NEVER a silent
             terminal — AI-operated is NOT review-free. The review (a distinct `build_result_review`
             item, inert to the dispatcher) reuses the existing surface_review inbox + a
             `decision.surfaced_for_review` event; it is part of THIS single dispatch, not a second one.
             Code NEVER writes `resolved` (operator-only) — it writes the `status` lane + surfaces.
        """
        from runtime import implement as _impl
        repo = repo or self._repo_root
        d = self.inbox.get(sid)
        if not d:
            raise KeyError(f"no surfaced decision {sid!r}")

        # 1 + 2 — the bind, then the discriminator (a forged/mismatched/non-build item refuses).
        self._verify_resolve_bind(sid, derived_from, require_approve=True)
        if not self.is_build_intent(d):
            raise GovernanceError(
                f"dispatch_decision: {sid!r} is not a build-intent item (payload.intent != 'build') — "
                f"refusing to auto-build from a non-build approve (the discriminator §W2). Mint it via "
                f"surface_build_intent.")

        payload = d.get("payload") or {}
        declared = payload.get("consequence_class", "decision_build")
        scope = list(payload.get("scope") or [])

        # 4 — W4 PRE-DISPATCH gate on the DECLARED class (deterministic, no confidence, no LOCKED-set
        # special-case). ONLY an AUTO-posture declared class may auto-dispatch; CONFIRM/SURFACE/LOCKED
        # all surface for the operator (do NOT auto-run). This keys on POLICY posture, so a CONFIRM
        # class absent from the hardcoded LOCKED set (e.g. 'destructive') can no longer slip through.
        # (decision_build is SURFACE → surfaces by default = the safe default; an AUTO-classed build is
        # the only thing that auto-runs.)
        if posture(declared) != AUTO:
            raise GovernanceError(
                f"dispatch_decision: declared consequence class {declared!r} has posture "
                f"{posture(declared)!r} (not AUTO) — it does NOT auto-dispatch; it surfaces for the "
                f"operator (CONFIRM/SURFACE/LOCKED never auto-run; surfacing a result after the act is "
                f"too late). The operator launches a non-AUTO build; refused.")

        # 3 + 5 — EXACTLY-ONCE check→claim, ATOMIC under a per-seq lock. The bridge is a
        # ThreadingHTTPServer over one Suite; without the lock two concurrent fires both clear the
        # check before either claims → double-launch. The lock serializes check→emit; the durable
        # decision.dispatch event is the cross-process/restart guarantee.
        with self._dispatch_lock(derived_from):
            if self._already_dispatched(derived_from):
                raise GovernanceError(
                    f"dispatch_decision: a decision.dispatch already exists for resolve seq={derived_from} — "
                    f"this build already launched; refusing a second (exactly-once, fail loud).")
            # emit the durable exactly-once claim BEFORE launch (and inside the lock). T1-EMIT: this is
            # the SAFETY-CRITICAL claim the exactly-once guarantee rides on — it MUST fail loud. Routed
            # through _emit_durable (raises on an append failure) NOT _emit (which swallows). A swallowed
            # claim-write would let _already_dispatched return False on a retry → DOUBLE-LAUNCH of a real
            # `claude -p`. Because this raises BEFORE launch (below) + inside the lock, a failed claim
            # means NOTHING launches — the safe outcome — and the caller (drive_dispatchable) sees the
            # raise rather than a phantom success.
            self._emit_durable("decision.dispatch",
                               f"dispatching build for {sid} (class={declared}, scope={scope or '∅'}, "
                               f"derived from verdict seq={derived_from})",
                               surfaced=sid, derived_from=derived_from,
                               consequence_class=declared, scope=scope)
            self.inbox.set_status(sid, "presented")

        # 6 — launch (W1). Loud on a bad round-trip (LaunchError) — caller (W7/loop) re-queues loud.
        launch = launcher or _impl.launch
        try:
            result = launch(d, repo=repo)
        except _impl.LaunchError as e:
            # loud re-queue as a responsive review item — never a silent no-op (W7).
            req = dict(payload); req.update({"requeued_from": sid, "why": f"dispatch failed: {e}",
                                             "derived_from": derived_from, "intent": "build"})
            new_sid = self.inbox.surface_review(req, origin="responsive")
            self._emit("decision.verify",
                       f"dispatch for {sid} FAILED to launch → re-queued {new_sid} — {e}",
                       surfaced=new_sid, requeued_from=sid, derived_from=derived_from, verify_passed=False)
            return {"surfaced": sid, "dispatched": True, "launched": False, "verified": False,
                    "requeued": new_sid, "error": str(e)}

        # store the result summary on the item (W5) — visible after the fact. T1-RACE: re-read under the
        # surfaced lock and mutate the FRESH copy, so a concurrent set_status (presented→…) write can't
        # lose-update the build_result (or vice-versa). The lock is the store-level one both writers reach.
        with self.store.surfaced_lock():
            d = self.inbox.get(sid) or d
            d["build_result"] = {"success": result.get("success"), "summary": result.get("summary", "")[:2000],
                                 "changed_files": result.get("changed_files", []),
                                 "permission_mode": result.get("permission_mode")}
            self.store.save_surfaced(d)

        # 6b — WIRE-HARDEN H3 + H2a, UNCONDITIONAL (the reverse-incident fix): re-discover into the LIVE
        # system (a new node-type becomes live in self.registry, not just on disk) + regenerate the
        # factual self-description blocks (MAP/STATE) FROM the now-current registry — BEFORE any verify,
        # so the drift check reads the refreshed truth. Run here (not only inside _wire_verify) so even a
        # loop that injects its OWN scenario `verifier` (which bypasses the heavy default) can NEVER
        # silently lose the refresh — the exact class of bug (a node built but the self-description not
        # refreshed → drift red) this lane exists to kill. Spawns NOTHING (no fork-bomb risk) and is
        # idempotent on an unchanged registry (_write_doc_block no-ops when content matches). A broken
        # node makes rediscover raise → returned here as a MISS reason → surfaces back (a build that
        # breaks the registry is not done), never a silent close (H6).
        live_ok, live_reason = self._make_live_and_refresh()

        # 7 — VERIFY by use (W3 + WIRE-HARDEN H1·H2b·H5 — verification QUALITY). The wire's
        # definition-of-done is now the HUMAN BUILD LOOP's discipline: run the affected acceptance suites
        # + drift (against the now-refreshed state) + an adversarial critic. This is the DEFAULT verify.
        # An INJECTED `verifier` is the fast deterministic bypass the loop/tests use (a specific scenario
        # check) — it runs INSTEAD of the heavy default so existing suites stay fast + green, exactly as
        # before WIRE-HARDEN. Either way a miss surfaces back, never a silent close (H6). (The STRUCTURAL
        # gates — refresh, FORM, scope-diff — are UNCONDITIONAL, below + above; they are NOT replaceable
        # by an injected verifier, so a loop's scenario verifier can never close a surface build.)
        if not live_ok:
            verify_passed, verify_reason = False, live_reason     # broken-registry build → surface back
        elif verifier is not None:
            verify_passed, verify_reason = verifier(result)
        else:
            verify_passed, verify_reason = self._wire_verify(
                d, result, scope, suite_runner=suite_runner, critic=critic)

        if not verify_passed:
            # H6 — a verification miss (test fail / drift red / critic veto / broken registry / launch)
            # surfaces back as a RETRY-able build-intent (the operator may re-approve after a fix). Call
            # surface_review DIRECTLY (NOT requeue_from_verdict; a build follows an approve, no reject seq).
            fail_item = dict(payload)
            fail_item.update({"requeued_from": sid, "why": f"verification failed: {verify_reason}",
                              "derived_from": derived_from, "intent": "build",
                              "build_result": d.get("build_result")})
            new_sid = self.inbox.surface_review(fail_item, origin="responsive")
            self._emit("decision.verify",
                       f"build for {sid} did NOT verify ({verify_reason}) → re-queued {new_sid}; not closed",
                       surfaced=new_sid, requeued_from=sid, derived_from=derived_from,
                       verify_passed=False)
            return {"surfaced": sid, "dispatched": True, "launched": True, "verified": False,
                    "requeued": new_sid, "reason": verify_reason}

        # 7b — H4 FORM GATE (UNCONDITIONAL — a structural gate, like the scope-diff, NOT inside the
        # replaceable verifier). A build that touched an operator-facing surface (canvas/) CANNOT
        # auto-close: its FORM (design-system components+tokens, coherent layout — AGENTS.md rule 9) is
        # the product bar, and there is NO design system / design-critic wired to machine-check it yet.
        # So it surfaces for review REGARDLESS of how verify_passed was reached (incl. an injected
        # scenario verifier — the WIRE-LOOP path). The surfaced item is DELIBERATELY DISPATCHER-INERT
        # (a `build_form_review`, NOT a build-intent): re-approving it must NOT re-dispatch into a
        # can't-verify-form loop (it would satisfy _is_dispatchable under a NEW seq, and exactly-once is
        # keyed on the OLD seq). _design_critic is the NAMED hook where design_critic_agent + design_lint
        # plug in once the design system exists; until then it is fail-safe (surface, never close).
        form_ok, form_reason = self._design_critic(result.get("changed_files", []))
        if not form_ok:
            form_item = {"kind": "build_form_review", "review_of": sid, "derived_from": derived_from,
                         "why": f"not auto-closed: {form_reason}", "scope": scope,
                         "consequence_class": declared, "build_result": d.get("build_result"),
                         "changed_files": result.get("changed_files", [])}
            new_sid = self.inbox.surface_review(form_item, origin="responsive")
            self._emit("decision.verify",
                       f"build for {sid} touched an operator-facing surface → cannot auto-close (FORM "
                       f"unverifiable) → surfaced {new_sid} for design review; not closed",
                       surfaced=new_sid, review_of=sid, derived_from=derived_from, verify_passed=False)
            return {"surfaced": sid, "dispatched": True, "launched": True, "verified": True,
                    "closed": False, "requeued": new_sid, "reason": form_reason,
                    "form_unverifiable": True}

        # 8 — W4 SCOPE-DIFF (fail loud): changed paths outside the declared scope → surface back, no
        # close. Runs ALWAYS (no `if scope:` skip) — _within_scope treats an empty scope as DENY-ALL,
        # so a build with no/empty declared scope can NEVER close (vacuous-enforcement hole closed).
        # H8 — the self-description files (AGENTS.md / MAP.md / STATE.md) are ALWAYS allowed: H7 INSTRUCTS
        # the build to update them as part of the change, and the close itself regenerates the factual
        # blocks (the system's write, not the build's). So they are upkeep, NOT out-of-scope wandering —
        # the overrun check must not flag them, or every well-behaved build would surface as a false
        # overrun. (The regen's writes aren't in `changed_files` anyway — that was snapshotted inside
        # launch() before the close ran — but the BUILD's own H7 prose edits to these files ARE, and
        # those are legitimate.) The declared scope still binds every OTHER path.
        changed = result.get("changed_files", [])
        if True:
            overrun = [p for p in changed
                       if not self._is_self_description(p) and not self._in_any_scope(p, scope)]
            if overrun:
                over_item = dict(payload)
                over_item.update({"requeued_from": sid, "intent": "build", "derived_from": derived_from,
                                  "why": f"scope overrun: changed {overrun} outside declared scope {scope}",
                                  "overrun": overrun, "build_result": d.get("build_result")})
                new_sid = self.inbox.surface_review(over_item, origin="responsive")
                self._emit("decision.verify",
                           f"build for {sid} OVERRAN declared scope ({overrun}) → re-queued {new_sid}; not closed",
                           surfaced=new_sid, requeued_from=sid, derived_from=derived_from,
                           verify_passed=False, overrun=overrun)
                return {"surfaced": sid, "dispatched": True, "launched": True, "verified": True,
                        "closed": False, "requeued": new_sid, "overrun": overrun}

        # 9 — CLOSE + SURFACE-FOR-REVIEW (the conceptual correction). guarded on the verification
        # verdict (W4 Hole 4). guard("code_build", …, confirmed=verify_passed): code_build is
        # CONFIRM-posture, so an unverified close (confirmed False) RAISES instead of silently writing
        # `implemented` (mirrors apply_node). inbox=None so the blocked path just raises (it must NOT
        # re-surface). Code writes ONLY the `status` lane — never the operator `resolved` field.
        #
        # AI-operated is NOT review-free: `implemented` means "done AND surfaced for review", NEVER a
        # silent terminal. So the SAME guarded close ALSO surfaces a review item (via the existing
        # `surface_review` inbox + a `decision.surfaced_for_review` event) carrying the result summary,
        # the changed-files manifest (git ground truth = the diff), and `derived_from` — so the operator
        # SEES it in the RHM walkthrough. This is part of the ONE dispatch (the decision.dispatch claim
        # already made it exactly-once); surfacing the review is NOT a second dispatch.
        #
        # The review item is DELIBERATELY NOT a build-intent (no `intent="build"`). The failure/overrun
        # re-queue paths above keep `intent="build"` on purpose — they are RETRIES the operator may
        # re-approve. A SUCCESS review must not be re-approvable into a REBUILD: if it carried
        # intent="build"+decision_build(AUTO), the operator's "looks good" approve would satisfy
        # drive_dispatchable._is_dispatchable (approve + build-intent + posture==AUTO) under a NEW seq,
        # and exactly-once (keyed on the OLD seq) would not stop it. So the review payload is a distinct
        # `build_result_review` kind — inert to the dispatcher.
        review_holder = {}
        def _close():
            self.inbox.set_status(sid, "implemented")
            self._emit("decision.implemented",
                       f"build for {sid} verified + within scope → status=implemented "
                       f"(changed {len(changed)} files; derived from seq={derived_from})",
                       surfaced=sid, derived_from=derived_from, verify_passed=True, changed_files=changed)
            # surface the result for the MANDATORY review (reversible/AUTO builds are non-blocking —
            # the change is made + git-reversible — but the review is ALWAYS surfaced). Reuses the
            # existing surface_review inbox + event log; no parallel review system. surface_review
            # emits "ask" too, so the live SSE inbox-refresh lights up for the operator.
            br = d.get("build_result") or {}
            review_payload = {
                "kind": "build_result_review",          # NOT a build-intent → inert to the dispatcher
                "title": f"Review implemented build: {sid}",
                "review_of": sid,
                "derived_from": derived_from,
                "summary": br.get("summary", ""),
                "changed_files": changed,                # git ground truth = the diff manifest
                "consequence_class": declared,
                "scope": scope,
                "why": (f"a build for {sid} was implemented (verified + in scope) and is surfaced for "
                        f"MANDATORY review — AI-operated is NOT review-free. The change is "
                        f"git-reversible; review it in the RHM walkthrough."),
            }
            rev = self.surface_review(review_payload, origin="responsive")
            review_holder["id"] = rev["id"]
            self._emit("decision.surfaced_for_review",
                       f"build for {sid} surfaced for review → {rev['id']} "
                       f"(changed {len(changed)} files; review is mandatory, not silent close)",
                       surfaced=rev["id"], review_of=sid, derived_from=derived_from,
                       changed_files=changed)
            return True
        guard("code_build", do=_close, confirmed=verify_passed, inbox=None)
        return {"surfaced": sid, "dispatched": True, "launched": True, "verified": True,
                "closed": True, "status": "implemented", "changed_files": changed,
                "derived_from": derived_from, "review_surfaced": review_holder.get("id")}

    @classmethod
    def _is_self_description(cls, path: str) -> bool:
        """H8 — is this changed path a ROOT self-description file (AGENTS.md / MAP.md / STATE.md)? H7
        instructs the build to update the self-description as part of the change, and the close itself
        regenerates the factual blocks — so a change to one of these is the SYSTEM's upkeep, never an
        out-of-scope edit. The overrun check (H8) treats it as in-scope without it being declared.
        Matched at the REPO ROOT only (normalized): a module's own AGENTS.md (e.g. 'nodes/AGENTS.md')
        is covered by that module's declared scope dir, not by this blanket allow."""
        import os as _os
        p = _os.path.normpath((path or "").strip().lstrip("./"))
        return p in cls._SELF_DESC_FILES

    @staticmethod
    def _in_any_scope(path: str, scope: list[str]) -> bool:
        """A changed path is authorized iff it falls under AT LEAST ONE declared scope entry. An
        EMPTY scope is DENY-ALL (returns False for every path) — never allow-all — so a build with
        no declared scope can never pass the overrun check (closes the vacuous-enforcement hole)."""
        return any(Suite._within_scope(path, s) for s in (scope or []))

    @staticmethod
    def _within_scope(path: str, scope_entry: str) -> bool:
        """A changed path is in scope if it equals or is under a declared scope entry (a file or a
        dir prefix). Both sides are NORMALIZED with os.path.normpath, which collapses '..' — so a
        traversal path like 'runtime/../nodes/evil.py' resolves to 'nodes/evil.py' and CANNOT match
        'runtime/' (the guard can't be fooled by '..'). An absolute path (e.g. '/etc/passwd') never
        matches a repo-relative scope entry. 'runtime/' still covers 'runtime/implement.py'."""
        import os as _os
        p = _os.path.normpath(path.strip().lstrip("./"))
        s = _os.path.normpath(scope_entry.strip().lstrip("./").rstrip("/"))
        if not s or s == ".":
            return False                                     # empty/degenerate scope entry → deny
        return p == s or p.startswith(s + _os.sep)

    # --- C1: the UI-component registry serialization (sibling of object_info) ---
    # Seeds the known chrome regions (DOM-resolved via data-ui-ref handles the UI lane adds) + the node
    # canvas (camera-resolved). ref = the <ref> in ui://<kind>/<ref>; dom_handle = the data-ui-ref value.
    # (ref, kind, title, dom_handle|camera_ref, caps-dict). caps keys are the Capabilities fields.
    UI_REGISTRY = [
        ("toolbar",   "chrome", "Toolbar",      {"dom_handle": "toolbar"},
         {"pointable": True, "spotlit": True}),
        ("inspector", "chrome", "Inspector",    {"dom_handle": "inspector"},
         {"pointable": True, "spotlit": True, "openable": True}),
        ("inbox",     "chrome", "Inbox",        {"dom_handle": "inbox"},
         {"pointable": True, "spotlit": True, "openable": True}),
        ("activity",  "chrome", "Activity log", {"dom_handle": "activity"},
         {"pointable": True, "spotlit": True, "openable": True, "drivenReadOnly": True}),
        ("chat",      "chrome", "RHM chat",     {"dom_handle": "chat"},
         {"pointable": True, "spotlit": True, "openable": True}),
        ("workshop",  "chrome", "Workshop",     {"dom_handle": "workshop"},
         {"pointable": True, "spotlit": True, "openable": True}),
        # the node canvas itself (camera_ref="*" = the whole canvas; individual nodes are addressed live
        # as ui://canvas/<node-id> by show's canvas branch — reuse of the existing camera path).
        ("*", "canvas", "Node canvas", {"camera_ref": "*"},
         {"pointable": True, "spotlit": True, "presentable": True}),
    ]

    def build_ui_info(self) -> dict:
        """C1: serialize the UI-component registry for the frontend (a SIBLING of object_info — which is
        NodeType-hardwired, so this is its own build, not a reuse). Built against
        contracts.ui_info.UiComponentEntry/Capabilities + build_ui_info (the CONTRACTS lane provides them).
        FUNCTION-LOCAL import so suite.py loads even before that contract lands; fails loud only when
        ui_info is actually called. The UI lane adds the matching data-ui-ref handles to the DOM."""
        from contracts.ui_info import UiComponentEntry, Capabilities, build_ui_info as _build
        entries = []
        for ref, kind, title, handle, caps in self.UI_REGISTRY:
            entries.append(UiComponentEntry(ref=ref, kind=kind, title=title,
                                            capabilities=Capabilities(**caps), **handle))
        return _build(entries)

    def ui_info(self) -> dict:
        return self.build_ui_info()

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
        name = self._slug(name)                             # natural name -> safe identifier (PoLR)
        self._safe_node_name(name)                          # reject path-traversal after
        from fabric import client, transport, config as fcfg
        sys_p = ("You write ONE Python node module for the 'company' composition engine. "
                 "Output ONLY raw Python — no prose, no markdown fences.")
        user_p = (
            "Contract: a module with VERSION='1', KIND ('process'|'content'), PORTS_IN dict, "
            "PORTS_OUT dict, and def run(inputs: dict, config: dict) returning the output value.\n\n"
            "Example:\nVERSION='1'\nKIND='process'\nPORTS_IN={'text':'Text'}\nPORTS_OUT={'text':'Text'}\n"
            "def run(inputs, config):\n    return str(inputs.get('text','')).upper()\n\n"
            "LIVE-STATE RULE: the scheduler memo-caches a node's output by the hash of its inputs, so a "
            "node that READS MUTABLE TRUTH whose inputs don't change every run (the repo on disk, a model "
            "of someone, a clock, a corpus index, anything that drifts under a fixed address) MUST declare "
            "VOLATILE=True at module top-level, or it will serve a STALE frozen result forever. A pure "
            "transform of its inputs (uppercase, join, wordcount) must NOT set it. When unsure: does the "
            "same input ever need to produce a fresh output? If yes -> VOLATILE=True.\n\n"
            f"Write a node named '{name}' that: {spec}\n"
            "Use PORTS_IN={'text':'Text'} and PORTS_OUT={'text':'Text'} unless the spec needs otherwise. "
            "Output ONLY the code.")
        t = transport.openai_transport(base_url=fcfg.DEFAULT_BASE_URL)
        raw = _strip_fences(client.complete(
            t, [{"role": "system", "content": sys_p + "\n\n" + self._authoring_preamble()},
                {"role": "user", "content": user_p}], model=model or fcfg.DEFAULT_BRAIN))
        need = self._needs(raw)
        if need:
            return {"needs": need, "id": self._ask_operator(need, f"while building node '{name}': {spec}")}
        code = _tag_system_origin(raw)
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
        def _do():                                          # the consequential body — runs ONLY if approved
            name = self._safe_node_name(d["payload"]["name"])   # re-validate at apply
            code = d["payload"]["code"]
            path = os.path.join(self.nodes_dir, name + ".py")
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(code if code.endswith("\n") else code + "\n")
            os.replace(tmp, path)                           # atomic; no partial file
            sha = self._commit_or_rollback(path, f"add node-type '{name}'")  # fail loud if not git-revertible
            self.registry.discover([self.nodes_dir])        # committed -> NOW make it live
            self._emit("apply", f"approved + applied '{name}' — now a live node-type · {sha[:8]}",
                       node_name=name, commit=sha)
            self.refresh_map()
            return path
        # G1: POLICY is the single router. code_build → CONFIRM → runs only if the OPERATOR approved
        # the surfaced item (authorization READ from the substrate, never a caller flag). inbox=None so
        # the blocked path just raises GovernanceError — it must NOT re-surface (the item already exists).
        return guard("code_build", do=_do, confirmed=self.inbox.is_approved(surfaced_id))

    # --- self-modification safety net (slice 13): additive + git-reversible ---
    @property
    def _repo_root(self) -> str:
        return os.path.dirname(self.nodes_dir)

    def _git_self_commit(self, paths: list[str], msg: str) -> str | None:
        """Commit a self-authored change so it is ALWAYS one `git revert` away (the real safety
        net — not the operator gate). Path-scoped; tagged [self-apply]. None if commit fails."""
        import subprocess
        try:
            subprocess.run(["git", "-C", self._repo_root, "add", *paths], check=True, capture_output=True)
            subprocess.run(["git", "-C", self._repo_root, "commit", "-m", f"[self-apply] {msg}"],
                           check=True, capture_output=True)
            out = subprocess.run(["git", "-C", self._repo_root, "rev-parse", "HEAD"],
                                 check=True, capture_output=True, text=True)
            return out.stdout.strip()
        except Exception:
            return None

    def _commit_or_rollback(self, path: str, msg: str) -> str:
        """Commit a just-written self-change; if the commit FAILS, roll the file back and raise —
        never leave a live self-change without its revert safety net (red-team F2: fail loud, not
        silent success). Returns the sha on success."""
        sha = self._git_self_commit([path], msg)
        if not sha:
            try:
                os.remove(path)
            except OSError:
                pass
            raise RuntimeError(
                f"git commit failed for {os.path.basename(path)} — rolled back the write and refused "
                "to apply: a self-change must be git-revertible (the safety net), or it does not go live.")
        return sha

    def last_self_change(self) -> dict | None:
        """The most recent self-applied change (for one-click rollback + audit)."""
        import subprocess
        try:
            out = subprocess.run(["git", "-C", self._repo_root, "log", "--grep=[self-apply]",
                                  "--fixed-strings", "-1", "--format=%H%x00%s"],
                                 check=True, capture_output=True, text=True).stdout.strip()
        except Exception:
            return None
        if not out:
            return None
        sha, _, subject = out.partition("\x00")
        return {"sha": sha, "subject": subject}

    def revert_self_change(self, sha: str) -> dict:
        """RECOVERY: roll back a self-applied change via git (itself reversible). OPERATOR-only.
        Re-discovers so the capability change reflects immediately. The property that makes
        self-modification acceptable — a bad self-edit is bounded, never bricking."""
        import subprocess
        subprocess.run(["git", "-C", self._repo_root, "revert", "--no-edit", sha],
                       check=True, capture_output=True)
        self.registry.rediscover([self.nodes_dir])          # rebuild from FS so a removed file un-registers
        head = subprocess.run(["git", "-C", self._repo_root, "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        self._emit("revert", f"rolled back self-change {sha[:8]}", reverted=sha, commit=head)
        self.refresh_map()
        return {"reverted": sha, "head": head}

    # --- UI extension point (slice 14): brain-authored DECLARATIVE panels added through the UI ---
    # Bounded by construction: the brain authors a panel DEFINITION (a generic renderer displays it),
    # NOT arbitrary interface code. Additive + git-reversible. Fields edit only real config.
    PANEL_TARGETS = ("mode", "model", "persona")
    PANEL_FIELD_TYPES = ("select", "text")

    def _registered_options(self, target: str) -> list:
        """The authoritative options for a registered target — from the registry, never invented."""
        if target == "mode":
            return list(self.MODES)
        if target == "model":
            return self.available_models()
        return []                                            # persona = free text

    def list_panels(self) -> list:
        import json as _j
        if not os.path.isdir(self.panels_dir):
            return []
        out = []
        for fn in sorted(os.listdir(self.panels_dir)):
            if fn.endswith(".json"):
                try:
                    out.append(_j.loads(open(os.path.join(self.panels_dir, fn), encoding="utf-8").read()))
                except Exception as e:
                    # a malformed file doesn't break the list — but SURFACE it, never drop silently (F6)
                    self._emit("warning", f"panel file {fn} is malformed and was skipped: {e}")
        return out

    def propose_panel(self, name: str, spec: str, model: str | None = None) -> dict:
        """The brain AUTHORS a declarative panel definition (it chooses the fields + wiring), surfaced
        as a ui_panel CONFIRM. NOT arbitrary code — a definition a generic renderer displays."""
        name = self._slug(name)
        self._safe_node_name(name)
        import json as _j
        from fabric import client, transport, config as fcfg
        sys_p = ('You author ONE declarative UI panel definition for the operator interface. Output ONLY '
                 'JSON, no prose. Shape: {"title": str, "fields": [{"key": str, "label": str, '
                 '"type": "select"|"text", "target": "mode"|"model"|"persona", "options": [str] (select only)}]}. '
                 'Each field\'s target is the REAL config it edits: mode (presence mode), model (the RHM model), '
                 'persona (the RHM voice). Choose the fields that fit the request.')
        cap = self.capabilities()
        user = (f"Panel name: {name}. Request: {spec}.\nUse ONLY these REGISTERED values — do not invent any:\n"
                f"- modes (for target 'mode'): {cap['modes']}\n"
                f"- models (for target 'model'): {cap['models']}\n"
                "For select fields you may omit 'options' — the system fills them from the registry.")
        raw = client.complete(transport.openai_transport(base_url=fcfg.DEFAULT_BASE_URL),
                              [{"role": "system", "content": sys_p + "\n\n" + self._authoring_preamble()},
                               {"role": "user", "content": user}],
                              model=model or fcfg.DEFAULT_BRAIN)
        need = self._needs(raw)
        if need:
            return {"needs": need, "id": self._ask_operator(need, f"while building panel '{name}': {spec}")}
        try:
            deftn = _j.loads(_strip_fences(raw))
        except Exception as e:
            # don't surface a success-shaped empty panel (F6) — ASK, the model didn't produce a valid def
            q = f"the '{name}' panel definition didn't parse as JSON ({e}); the model output was malformed"
            return {"needs": q, "id": self._ask_operator(q, f"panel '{name}': {spec}")}
        sid = self.inbox.surface("ui_panel", {"name": name, "panel": deftn}, default="reject")
        self._emit("grow", f"brain authored a '{name}' UI panel — surfaced for approval",
                   node_name=name, surfaced=sid)
        return {"id": sid, "name": name, "panel": deftn}

    def apply_panel(self, surfaced_id: str) -> str:
        """Apply a proposed panel — only if OPERATOR-approved. VALIDATES the def to declarative
        fields with allowed types/targets (never arbitrary code), writes panels/<name>.json
        additively + git-commits (reversible)."""
        d = self.inbox.get(surfaced_id)
        if not d:
            raise KeyError(f"no surfaced decision {surfaced_id!r}")
        def _do():                                           # the consequential body — runs ONLY if approved
            name = self._safe_node_name(d["payload"]["name"])
            deftn = d["payload"]["panel"]
            fields, dropped = [], []
            for f in (deftn.get("fields") or []):
                if f.get("type") in self.PANEL_FIELD_TYPES and f.get("target") in self.PANEL_TARGETS:
                    # registered-target options come from the REGISTRY (authoritative) — never the brain's
                    # guess. So a 'model' picker always lists the REAL models, not invented names.
                    reg_opts = self._registered_options(f["target"])
                    opts = reg_opts if (f["type"] == "select" and reg_opts) \
                        else ([str(o) for o in f.get("options", [])] if f["type"] == "select" else [])
                    fields.append({"key": str(f.get("key", f.get("target"))), "label": str(f.get("label", "")),
                                   "type": f["type"], "target": f["target"], "options": opts})
                else:
                    dropped.append(f"{f.get('key', '?')}({f.get('type')}/{f.get('target')})")
            if dropped:                                      # surface dropped fields, never silent (F6)
                self._emit("warning", f"panel '{name}': dropped {len(dropped)} field(s) with unsupported "
                           f"type/target: {', '.join(dropped)}")
            clean = {"id": name, "title": str(deftn.get("title", name)), "fields": fields}
            import json as _j
            os.makedirs(self.panels_dir, exist_ok=True)
            path = os.path.join(self.panels_dir, name + ".json")
            tmp = path + ".tmp"
            open(tmp, "w", encoding="utf-8").write(_j.dumps(clean, indent=2))
            os.replace(tmp, path)
            sha = self._commit_or_rollback(path, f"add UI panel '{name}'")
            self._emit("apply", f"approved + applied '{name}' UI panel · {sha[:8]}", node_name=name, commit=sha)
            self.refresh_map()
            return path
        # G1: ui_panel → CONFIRM (now explicit in POLICY) → runs only if operator-approved. inbox=None
        # → the blocked path raises GovernanceError without re-surfacing (item already exists).
        return guard("ui_panel", do=_do, confirmed=self.inbox.is_approved(surfaced_id))

    def apply_surfaced(self, surfaced_id: str) -> dict:
        """Dispatch apply by the decision's class — ui_panel → panel, ui_extension → code-gated
        extension, else code_build → node-type."""
        d = self.inbox.get(surfaced_id)
        if not d:
            raise KeyError(f"no surfaced decision {surfaced_id!r}")
        if d.get("action") == "ui_panel":
            return {"applied": self.apply_panel(surfaced_id), "kind": "ui_panel"}
        if d.get("action") == "ui_extension":
            r = self.apply_extension(surfaced_id)
            r["kind"] = "ui_extension"
            return r
        return {"applied": self.apply_node(surfaced_id), "kind": "code_build"}

    # --- the self-coding subsystem (slice 15): arbitrary brain-authored extensions, BUILD-GATED ---
    # The object of safety is the LOOP, not the code: a broken change is caught by the build-gate
    # and NEVER goes live; runtime throws are contained by the error boundary; every promote is a
    # git commit (revert recovers). Operator-only. Reliability of the code is the MODEL's.
    def propose_extension(self, name: str, spec: str, model: str | None = None) -> dict:
        """The brain authors a real .tsx React component (arbitrary UI), surfaced as ui_extension
        CONFIRM (operator-only). Constrained: import only from 'react' (so the build-gate can keep
        unresolved-module breaks out); may call fetch('/api/...')."""
        name = self._slug(name)
        self._safe_node_name(name)
        from fabric import client, transport, config as fcfg
        sys_p = ("You write ONE React component (TSX) that extends the operator interface. Output ONLY the "
                 "code — no prose, no markdown fences. Contract: `export default function " + name +
                 "() { ... }`. You MAY `import { useState, useEffect } from 'react'` — but import from NO "
                 "other module. You MAY call fetch('/api/...') against the bridge to read or act on the "
                 "system.\n\n" + self._authoring_preamble())
        code = _strip_fences(client.complete(
            transport.openai_transport(base_url=fcfg.DEFAULT_BASE_URL),
            [{"role": "system", "content": sys_p}, {"role": "user", "content": f"Build: {spec}"}],
            model=model or fcfg.DEFAULT_BRAIN))
        need = self._needs(code)
        if need:                                              # asked instead of fabricating
            return {"needs": need, "id": self._ask_operator(need, f"while building extension '{name}': {spec}")}
        sid = self.inbox.surface("ui_extension", {"name": name, "code": code}, default="reject")
        self._emit("grow", f"brain authored a '{name}' UI extension — surfaced for approval",
                   node_name=name, surfaced=sid)
        return {"id": sid, "name": name, "code": code}

    def _gate_extension(self, code: str) -> str | None:
        """Build-gate: returns an error string if the candidate would break the build or do something
        forbidden, else None. AST-checked via canvas/app/syntax-gate.cjs (red-team B1): syntax +
        import-allowlist (react only) + no dynamic import() + no require() + no external-URL literals.
        Runs on a TEMP file OUTSIDE the live tree."""
        import subprocess
        import tempfile
        appdir = os.path.join(self._repo_root, "canvas", "app")
        fd, tmp = tempfile.mkstemp(suffix=".tsx")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(code)
            r = subprocess.run(["node", "syntax-gate.cjs", tmp], cwd=appdir,
                               capture_output=True, text=True, timeout=60)
            if r.returncode != 0:
                return "build-gate rejected: " + (r.stderr.strip() or r.stdout.strip())[:400]
        finally:
            os.unlink(tmp)
        return None

    def apply_extension(self, surfaced_id: str) -> dict:
        """Operator-approved. Build-GATE the candidate OUTSIDE the live tree; promote into
        src/extensions/ + git-commit ONLY on pass. A failed gate NEVER writes to the live tree."""
        d = self.inbox.get(surfaced_id)
        if not d:
            raise KeyError(f"no surfaced decision {surfaced_id!r}")
        def _do():                                            # the consequential body — runs ONLY if approved
            name = self._safe_node_name(d["payload"]["name"])
            code = d["payload"]["code"]
            err = self._gate_extension(code)                  # gate runs on a temp file, NOT in src
            if err:
                self._emit("reject", f"extension '{name}' REJECTED by build-gate (never went live)", node_name=name)
                return {"applied": None, "rejected": True, "error": err}
            extdir = os.path.join(self._repo_root, "canvas", "app", "src", "extensions")
            os.makedirs(extdir, exist_ok=True)
            path = os.path.join(extdir, name + ".tsx")
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(code if code.endswith("\n") else code + "\n")
            os.replace(tmp, path)                             # promote (gate passed) — now Vite loads it
            sha = self._commit_or_rollback(path, f"add extension '{name}'")   # fail loud if not git-revertible
            self._emit("apply", f"approved + applied '{name}' extension (gate passed) · {sha[:8]}",
                       node_name=name, commit=sha)
            self.refresh_map()
            return {"applied": path, "rejected": False, "commit": sha}
        # G1: ui_extension → CONFIRM (now explicit in POLICY) → runs only if operator-approved. inbox=None
        # → the blocked path raises GovernanceError without re-surfacing (item already exists).
        return guard("ui_extension", do=_do, confirmed=self.inbox.is_approved(surfaced_id))

    # --- surfaced-decision inbox (D4/D7) ---
    def list_surfaced(self) -> list:
        return self.inbox.list()

    # the operator's response vocabulary (D): approve/reject/decide RESOLVE; comment annotates without
    # resolving; skip defers — back to the inbox, NOT resolved (a skipped item still needs Tim).
    RESOLVING_VERBS = ("approve", "reject", "decide")

    def resolve_surfaced(self, sid: str, choice: str, reason: str = "",
                         session_id: str | None = None, position: int | None = None) -> dict:
        """OPERATOR-only (UI channel) — NOT exposed on the MCP face, so the agent can't self-approve.
        Captures the WHY (the generalising signal, I1) and — additively (D) — the session id + position
        the response came from, plus the comment/skip/decide vocabulary:
          • approve/reject/decide → RESOLVE (writes `resolved`; status → resolved).
          • comment → annotate only (records the reason; status → responded; NOT resolved).
          • skip → defer (status back to 'inbox'; NOT resolved — a skipped item still needs Tim).
        Returns the verbose verdict. Existing two-arg callers are unchanged (the new args default)."""
        d = self.inbox.get(sid)
        if not d:
            raise KeyError(f"no surfaced decision {sid!r}")
        # session-position tagging (record on the surfaced item + the resolve event for audit/replay).
        # T1-RACE: re-read under the surfaced lock and mutate the fresh copy so a concurrent set_status
        # write can't lose-update the session tag (and the tag can't clobber a status advance).
        if session_id is not None:
            with self.store.surfaced_lock():
                d = self.inbox.get(sid) or d
                d.setdefault("session_id", session_id)
                if position is not None:
                    d["position"] = position
                self.store.save_surfaced(d)

        if choice == "skip":
            self.inbox.set_status(sid, "inbox")            # defer — still a live escalation; NOT resolved
            self._emit("review.skip", f"operator skipped {sid}" + (f" — {reason}" if reason else ""),
                       surfaced=sid, choice="skip", reason=reason, session=session_id, position=position)
            return {"id": sid, "choice": "skip", "status": "inbox", "resolved": False}
        if choice == "comment":
            if reason:                                     # annotate the WHY without resolving
                d["reason"] = reason
                self.store.save_surfaced(d)
            self.inbox.set_status(sid, "responded")
            self._emit("review.comment", f"operator commented on {sid}" + (f" — {reason}" if reason else ""),
                       surfaced=sid, choice="comment", reason=reason, session=session_id, position=position)
            return {"id": sid, "choice": "comment", "status": "responded", "resolved": False}

        # approve / reject / decide (or any other verb) → RESOLVE (TERMINAL). resolve() writes `resolved` +
        # reason; mark the lifecycle status resolved (additive) and emit the resolve event (seq·surfaced·
        # choice·reason — the verdict E reads, suite.py resolve event).
        #
        # IDEMPOTENT-PER-ITEM (integrity, fail-loud): a recorded decision CANNOT be contradicted. Once an
        # item has a TERMINAL verdict (resolved == approve|reject|decide), a SECOND terminal resolve REFUSES
        # — else one item could be both committed-as-approved AND requeued-as-rejected (the three-part bind
        # is per-verdict-seq, so it can't catch the contradiction). skip→inbox and comment→responded never
        # write `resolved`, so they stay non-terminal + re-presentable; only these three are terminal.
        prior = d.get("resolved")
        if prior in self.RESOLVING_VERBS:
            raise GovernanceError(
                f"surfaced {sid!r} already has a terminal verdict ({prior!r}) — a recorded decision "
                f"cannot be contradicted; refusing the second {choice!r} (one item → one final verdict). "
                f"Re-open it with skip/comment first if it genuinely needs revisiting.")
        self.inbox.resolve(sid, choice, reason)
        try:
            self.inbox.set_status(sid, "resolved")
        except KeyError:
            pass
        self._emit("resolve", f"operator {choice}d {sid}" + (f" — {reason}" if reason else ""),
                   surfaced=sid, choice=choice, reason=reason, session=session_id, position=position)
        return {"id": sid, "choice": choice, "status": "resolved", "resolved": True}

    def decision_view(self, sid: str) -> dict:
        """A decision as a VIEW derived from the event log (I2): its full trajectory — proposed →
        framed → resolved (with the why) — reconstructed in order. Auditable + replayable."""
        d = self.inbox.get(sid)
        evs = sorted((e for e in self.store.recent_events(999) if e.get("surfaced") == sid),
                     key=lambda e: e.get("seq", 0))                # chronological path, not endpoint
        return {"id": sid, "decision": d, "trajectory": evs}

    def session_view(self, session_id: str) -> dict:
        """D: the full trajectory of a review SESSION — every event tagged with this session id, in
        order. Clones decision_view but WIDENS past the 999-event window: reads from the start via
        events_since(-1) (the file-tail) and filters on `session`, so a long walk is never truncated."""
        evs = [e for e in self.store.events_since(-1) if e.get("session") == session_id]
        evs.sort(key=lambda e: e.get("seq", 0))
        g = self.store.load_graph(self._session_graph_id(session_id))
        return {"session": session_id, "trajectory": evs,
                "graph": g.model_dump(mode="json") if g else None}

    def replay(self, limit: int = 200) -> list:
        """The whole captured path, oldest-first — the trajectory that trains the twin (I1)."""
        return list(reversed(self.store.recent_events(limit)))
