"""runtime/suite.py — the shared brain (the composition suite's core operations).

ONE brain, two faces: the UI bridge and the MCP server both call this. Graphs live in
the addressed store (S3 graphs registry), so the faces operate the SAME substrate even in
separate processes. Operations are the C7 generic verbs — generic over node-type
(they consult the registry), never one-per-type.
"""
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Callable

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


@dataclass(frozen=True)
class VerbSpec:
    """ONE source for a single RHM verb (replaces the 3 parallel tables RHM_VERBS / RHM_VERB_DESC /
    RHM_VERB_CLASS — which could drift). Each verb carries: its operator-facing gloss (desc), its
    GOVERNANCE action-class (the deterministic decide-for-me router input), the set of presence MODES
    in which it is OFFERED (mode-primary), and a PREDICATE over the live affordance context that
    further refines whether it makes sense RIGHT NOW (context-refines). The three legacy dicts are
    DERIVED from the registry below so there is no second copy to fall out of sync.

    The `modes`/`predicate` pair governs only what is OFFERED to the model (the tools array +
    the rendered verb list). The ONE whitelist that ENFORCES safety still lives in
    `_dispatch_rhm_action` (it keys on RHM_VERBS), so even a verb the model emits unprompted —
    or a forbidden verb — is refused there: narrowing the offer never weakens the gate (E6)."""
    desc: str                       # one-line operator-facing gloss (the old RHM_VERB_DESC value)
    action_class: str               # governance action-class (the old RHM_VERB_CLASS value)
    modes: frozenset                # the presence modes in which this verb is OFFERED
    predicate: Callable             # ctx(dict) -> bool — does this verb make sense in the current context


class Suite:
    # The STATE-TYPE REGISTRY (Possibility Space Block 19) — node "state" is a REGISTERED, single-source
    # set, NOT a hardcoded enum. `state()` reads its status-id strings from HERE (one source), and
    # `capabilities().node_states` exposes the set so the surface renders the vocabulary from the
    # registry (registry-is-truth) instead of hardcoding it. Each entry:
    #   id          — the status string `state()` reports for a node
    #   label       — short human label for the surface
    #   means       — what the status means (the surface shows this; descriptive, not executable)
    #   applies_to  — which RESOLVE-MODE this status can apply to ('compute' = executing nodes;
    #                 'reference' = reference-resolved nodes i.e. portals). This SCOPES the vocabulary:
    #                 executing nodes keep idle/ran/cached/stuck; reference nodes get live/empty.
    #   derived_when— the condition under which `state()` derives this status (descriptive metadata for
    #                 the surface; the derivation logic lives in `state()`, this is not an interpreter).
    # Step A: the four EXISTING statuses are lifted here UNCHANGED (compute-scoped) — their derivation in
    # state() is byte-for-byte as before, proven by the existing suites staying green.
    # Step B: two ADDITIVE states for reference-resolved nodes (portals): `live` (ref resolves to content)
    # and `empty` (ref is None/dangling/unresolved) — so a portal stops mis-reporting idle/cached on
    # reload. Executing nodes are UNAFFECTED (scoped by applies_to).
    NODE_STATES = (
        {"id": "idle", "label": "Idle", "applies_to": ("compute",),
         "means": "has never produced a result and holds none",
         "derived_when": "no fresh run result and the node's output address does not resolve"},
        {"id": "ran", "label": "Ran", "applies_to": ("compute",),
         "means": "fired on the most recent run and produced a fresh result",
         "derived_when": "the node id is in the run result's `ran` set"},
        {"id": "cached", "label": "Cached", "applies_to": ("compute",),
         "means": "output already existed, so the memo gate skipped re-running it (the GPU/clock guard)",
         "derived_when": "the node id is in the run result's `skipped` set, OR (on reload) its output "
                         "address resolves to a stored result"},
        {"id": "stuck", "label": "Stuck", "applies_to": ("compute",),
         "means": "could not fire because a required input never resolved (not a pruned branch)",
         "derived_when": "the node id is in the run result's `stuck` set, OR (on reload) the most recent "
                         "run event for the graph listed it stuck and it still holds no result"},
        {"id": "failed", "label": "Failed", "applies_to": ("compute",),
         "means": "fired but RAISED — it threw an error during run (the scheduler contained it; downstream "
                  "stays unresolved). Distinct from stuck (an input never arrived) — here the node ran and "
                  "errored. The error message is carried on the node where the shape allows.",
         "derived_when": "the node id is a key in the run result's `failed` map (scheduler containment)"},
        {"id": "live", "label": "Live", "applies_to": ("reference",),
         "means": "a live window onto its reference address, currently resolving to content",
         "derived_when": "RESOLVE='reference' and head(config.ref) resolves to a stored content hash"},
        {"id": "empty", "label": "Empty", "applies_to": ("reference",),
         "means": "a live window whose reference is unset, dangling, or not yet resolvable",
         "derived_when": "RESOLVE='reference' and config.ref is empty/None or head(ref) does not resolve"},
    )

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

    def emit_run_record(self, op: str, duration_ms: int, **conditions) -> None:
        """G7 / Introspective Data Building (Tim's law) — FIRST INSTANCE, the voice/model layer learning
        by use. A typed run-record: an operation + HOW LONG IT TOOK + the CONDITIONS it happened under,
        into the EXISTING event log (kind='op.run') — NOT a new analytics store. A datum without its
        conditions is noise, so callers pass model/ear/engine/mode/ok/etc. Lenient-emit (telemetry must
        never break the op it records; the raw record is cheap + append-only). Rollups (n·median·p95) are
        DERIVED off the hot path from these — never computed here. 'How long it TOOK' lands here; 'how
        long it TAKES' (the prior/estimate) lives in the declared specs (role knobs, services.json
        vram/wake) — the measured refines the estimate. Generalises Company-wide past voice (cognition,
        RHM verbs, surface, errors) — same emit→substrate→rollup loop, per-type."""
        self._emit("op.run", f"{op} · {duration_ms}ms", op=op, duration_ms=duration_ms, **conditions)

    def run_stats(self, op: str | None = None, since: int = -1) -> dict:
        """G7 ROLLUP — raw op.run run-records → DISTRIBUTIONS (n · median · p95 · min · max), grouped by
        (op, model/engine). The read-half of introspective-data-building: the trace becomes KNOWLEDGE.
        Read-time aggregation over the event log — NEVER on the hot path (callers hit this on demand /
        a cadence). Feeds the Manifest's measured cells + the resource manager's pre-warm decisions.
        `op` filters to one operation; `since` is an event seq (default -1 = all)."""
        import statistics
        evs = [e for e in self.events_since(since) if e.get("kind") == "op.run"]
        if op:
            evs = [e for e in evs if e.get("op") == op]

        def dist(vals):
            vals = sorted(v for v in vals if isinstance(v, (int, float)))
            if not vals:
                return None
            n = len(vals)
            return {"n": n, "median": round(statistics.median(vals), 1),
                    "p95": vals[min(n - 1, int(round(0.95 * (n - 1))))],
                    "min": vals[0], "max": vals[-1]}

        groups: dict = {}
        for e in evs:
            key = (e.get("op"), e.get("model") or e.get("engine") or "")
            groups.setdefault(key, []).append(e)
        out = []
        for (o, who), es in groups.items():
            rec = {"op": o, "who": who, "n": len(es), "duration_ms": dist([e.get("duration_ms") for e in es])}
            for f in ("stt_ms", "think_ms", "tts_ms", "queue_ms", "chunks", "chunks_done", "chunks_total"):  # extra timing/condition fields
                d = dist([e.get(f) for e in es if e.get(f) is not None])
                if d:
                    rec[f] = d
            out.append(rec)
        return {"ops": sorted(out, key=lambda r: -r["n"]), "total_records": len(evs)}

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
    _models_cache_at: float = 0.0                             # monotonic stamp of the last live fetch
    _models_cache_degraded: bool = False                      # the cached list is the fallback, not the live list
    MODELS_CACHE_TTL = 60.0                                    # seconds — a model that comes up later becomes
    #                                                            visible without a process restart (was: pinned
    #                                                            process-lifetime → the fleet went stale). A
    #                                                            DEGRADED cache (endpoint was down) is NOT held for
    #                                                            the TTL — it expires immediately so the next call
    #                                                            re-probes and the fleet recovers the moment the
    #                                                            endpoint returns. Manual refresh_models() forces it.

    def available_models(self, force_refresh: bool = False) -> list:
        """The REAL models registered at the fabric endpoint — so the brain picks from what exists
        instead of inventing names. Cached with a short TTL (MODELS_CACHE_TTL) so a model that comes up
        LATER is visible without a restart; a degraded (fallback) cache is never held — it re-probes next
        call so the fleet recovers the instant the endpoint returns. Falls back FAIL-LOUD-LEGIBLE to the
        configured brain if the endpoint is down (a warning event, never silent). force_refresh bypasses
        the cache (the manual-refresh path)."""
        import time as _t
        fresh = (self._models_cache is not None
                 and not self._models_cache_degraded                      # never serve a stale degraded list
                 and (_t.monotonic() - self._models_cache_at) < self.MODELS_CACHE_TTL)
        if fresh and not force_refresh:
            return self._models_cache
        from fabric import transport, config as fcfg
        degraded = False
        try:
            models = transport.list_models(fcfg.DEFAULT_BASE_URL)
        except Exception as e:
            models = None
            self._emit("warning", f"model registry unreachable ({type(e).__name__}) — "
                       f"falling back to [{fcfg.DEFAULT_BRAIN}]; the source-of-truth list is degraded")
        if not models:                                        # surface the degraded fallback, never silent (F6)
            if models is not None:
                self._emit("warning", "model registry returned empty — falling back to the default brain")
            models = [fcfg.DEFAULT_BRAIN]
            degraded = True
        self._models_cache = models
        self._models_cache_at = _t.monotonic()
        self._models_cache_degraded = degraded
        return self._models_cache

    def refresh_models(self) -> list:
        """Manual cache invalidation — re-probe the fabric endpoint NOW (no restart). The fleet stays
        current: a model brought up after process start becomes visible the moment this is called (or
        within MODELS_CACHE_TTL automatically). Returns the fresh list."""
        return self.available_models(force_refresh=True)

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
            # T3-MODE (COMPLETE): expose the mode DIRECTIVES (the prose behind each mode) from the one
            # source (MODE_DIRECTIVES) so the surface reads them instead of hand-copying. Backend half
            # (this line) + FE half (App.tsx deletes its MODE_DESC copy and reads capabilities().
            # mode_directives) are now BOTH merged — registry-is-truth, PoLR honoured. Additive map
            # {mode: directive}; an older FE that ignores it is unaffected.
            "mode_directives": dict(self.MODE_DIRECTIVES),
            "rhm_verbs": list(self.RHM_VERBS),
            # The STATE-TYPE REGISTRY exposed (registry-is-truth): WHAT node-states exist + their meaning
            # + which resolve-mode each applies to, so the surface renders the status vocabulary from
            # here instead of hardcoding idle/ran/cached/stuck/live/empty. Additive key; an older FE that
            # ignores it is unaffected (the four executing statuses derive exactly as before).
            "node_states": [dict(s, applies_to=list(s["applies_to"])) for s in self.NODE_STATES],
            "panels": [p.get("id") for p in self.list_panels()],
            # the STT (ear) registry — WHAT speech-to-text providers exist + are usable (the slot mirrors
            # the brain model). From voice/stt.py's source of truth (guarded — {} if voice is absent), so
            # the surface fills the ear dropdown from what's real, never a hand-typed list. The stt lane
            # may not have shipped its richer available_stt() yet → degrades to available() (rule 4: no
            # crash, no fabrication). Schema-additive key; an older surface ignoring it is unaffected.
            "stt": self.available_stt(),
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

    def _last_run_failed(self, graph_id: str) -> dict:
        """The `failed` {nid: "ErrType: msg"} map from the MOST RECENT `run` event for `graph_id` (the
        run emit records `failed=dict(failed)` with `graph=<id>`). Mirror of `_last_run_stuck` so a
        FAILED node survives a reload (status=`failed`, not re-defaulting to idle) — closing the same
        silent-regression shape on the no-fresh-result path (rule 4). Newest run wins; tolerant (a
        malformed/absent field reads as no-failures; never raises in a status read). A node that since
        resolved (its output address now holds content) is no longer reported failed (checked at the
        call site, after cas)."""
        for ev in self.store.recent_events(200):
            if ev.get("kind") == "run" and ev.get("graph") == graph_id:
                fl = ev.get("failed")
                return dict(fl) if isinstance(fl, dict) else {}
        return {}

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
            failed = r.get("failed") or {}
            self._emit("run", f"ran {len(r['ran'])}, cached {len(r['skipped'])}"
                       + (f", stuck {len(r['stuck'])}" if r.get("stuck") else "")
                       + (f", failed {len(failed)}" if failed else ""),
                       graph=graph_id, ran=sorted(r["ran"]), cached=sorted(r["skipped"]),
                       stuck=sorted(r.get("stuck", [])), failed=dict(failed))
            # FAIL LOUD at the surface (engine handoff, rule 4): the run COMPLETES (containment, no raise),
            # but a failed node must be SEEN — a node-error is not a silent no-op. A distinct `warning`
            # event (not just the count folded into the run line) so now()'s last_event surfaces it and the
            # operator/now-view can't miss it. Names the nodes + their errors.
            if failed:
                detail = "; ".join(f"{nid}: {err}" for nid, err in sorted(failed.items()))
                self._emit("warning", f"{len(failed)} node(s) FAILED this run — {detail}",
                           graph=graph_id, failed=dict(failed))
            return r
        return guard("run", do=_do)                                     # AUTO → identical; POLICY is the router

    def state(self, graph_id: str, result: dict | None = None, branch: str = "main") -> dict:
        g = self._load(graph_id)
        nodes = []
        for n in g.nodes:
            logical = f"run://{g.id}/{n.id}" if branch == "main" else f"run://{g.id}/{n.id}@{branch}"
            mod = self.registry.get(n.type)
            node_error = None                                  # the run error for a `failed` node (else None)
            if getattr(mod, "RESOLVE", "compute") == "reference":
                # REFERENCE-RESOLVED (portals): a live window onto another address, never computed and
                # never fired (the scheduler SKIPS it). Resolve config.ref NOW (window, not a copy) and
                # derive its state from the STATE-TYPE REGISTRY's reference-scoped vocabulary
                # (NODE_STATES, applies_to='reference') — `live` if the ref resolves to content, `empty`
                # otherwise. This is hoisted ABOVE the result/reload split on purpose: a portal never
                # legitimately gets a run-status (it has no run), so routing it through ONE branch makes
                # the fresh-result path and the reload path AGREE by construction — which is exactly why
                # the old idle↔cached flip-on-reload (idle on the result path, cached on reload) is gone.
                # Executing nodes (RESOLVE='compute') are UNAFFECTED — they fall through to the original
                # four-status derivation below, byte-for-byte (Step A, no behaviour change).
                ref = n.config.get("ref") or ""
                cas = self.store.head(ref) if ref else None
                status = "live" if cas else "empty"
            else:
                cas = self.store.head(logical)
                if result:
                    # T3-STATUS: `stuck` is a REAL backend node status (one source of truth), not a
                    # client-only overlay. The scheduler already reports which nodes could not fire because
                    # an input never resolved (scheduler result['stuck']); surface it here so the FE reads
                    # it from the backend instead of maintaining a parallel client-side `stuck` re-applied
                    # from events after every reload. Checked BEFORE ran/cached/idle so a stuck node is
                    # never mislabeled idle. (be-half → at most needs-tim until the FE drops its overlay.)
                    # FAILED (engine handoff): the scheduler now CONTAINS a node that RAISED into a
                    # result['failed'] {nid: "ErrType: msg"} map. Without consuming it, a failed node fell
                    # through to `idle` — a SILENT regression (the operator saw "nothing happened" for a
                    # node that actually errored, violating rule 4). Branch on `failed` BEFORE the idle
                    # fallthrough (the sets are disjoint) and carry the error message onto the node dict.
                    failed_map = result.get("failed") or {}
                    if n.id in failed_map:
                        status = "failed"
                        node_error = failed_map[n.id]
                    else:
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
                    elif n.id in self._last_run_failed(g.id):
                        # FAILED survives a reload too (rule 4): the most recent run recorded this node as
                        # failed and it still holds no result, so it is NOT idle. Mirror of the stuck path;
                        # checked before stuck/idle. Carry the persisted error message.
                        status = "failed"
                        node_error = self._last_run_failed(g.id).get(n.id)
                    elif n.id in self._last_run_stuck(g.id):
                        status = "stuck"
                    else:
                        status = "idle"
            nt = self.registry.types.get(n.type)
            node = {
                "id": n.id, "type": n.type, "config": n.config,
                "kind": nt.kind if nt else ("content" if n.type in CONTENT_KINDS else "process"),
                "layer": getattr(mod, "ORIGIN", "authored"),   # provenance layer (authored vs system)
                "status": status, "address": logical, "content_hash": cas,
                "output": self.store.get_content(cas) if cas else None,
                "position": n.position.model_dump(),           # C5: layout is backend-authoritative
                "size": n.size.model_dump(),
            }
            if node_error is not None:                         # carry the run error for a `failed` node (fail-loud)
                node["error"] = node_error
            nodes.append(node)
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

    # --- the MODEL-ROLE REGISTRY (registry-is-truth; mirrors STT_PROVIDERS / the node registry) -------
    # A ROLE is a named model-FUNCTION of the collective cognition: a specific job done by a model that
    # is NOT the conversational brain. The brain (rhm_config.model) is the primary/conscious role and
    # stays its OWN slot (widely read; the model-registry session owns it) — these are the AUXILIARY
    # roles. `judge` is the first (the voice circuit's finished-thought endpoint). Add a role TYPE here
    # (+ the code that consumes it) → it appears as a configurable slot in the UI automatically; you
    # never edit the config whitelist (bindings live in ONE `roles` dict).
    #
    # Each role DECLARES its full contract — Tim's "triggers, configs like outputs/tools, contexts, and
    # whatever else": the fields below are the role's self-description the config lab renders + binds.
    # WIRED-NOW fields (flow into the model call): default_model/base_url (None → the brain), knobs
    # (max_tokens/temperature/…), thinking, output, tools. DECLARED-design fields (captured + designable,
    # the growth path — NOT a faked general engine): `trigger` is descriptive today (judge's concrete
    # trigger is the voice circuit calling /api/voice/finished-thought); a general event→role trigger
    # engine, and per-role arbitrary tool-binding, come as their consuming code is built. `env_*` give
    # the resolution precedence: a config binding > env override > the declared default.
    ROLE_REGISTRY = {
        "judge": {
            "label": "Finished-thought judge",
            "description": "Decides whether a spoken utterance is a COMPLETE thought (fire the turn) or "
                           "mid-ramble (keep listening) — the voice circuit's semantic endpoint.",
            "trigger": "voice circuit: a VAD pause during always-listen (POST /api/voice/finished-thought)",
            "default_model": None,            # None → falls to the RHM brain (rhm_config.model) — always
                                              # available. The hard default stays safe; the data-driven
                                              # PREFERENCE is `recommended_*` below (binding it live needs
                                              # the 4B resident → the resource manager owns that).
            "default_base_url": None,         # None → the brain's base_url
            "recommended_model": "cyankiwi/Qwen3.5-4B-AWQ-4bit",      # MEASURED day-one pick (Tim 2026-06-05)
            "recommended_base_url": "http://localhost:8000/v1",
            "recommended_reason": ("local 4B no-think judged FINISHED in 463ms / a fragment in 49ms vs "
                                   "deepseek-cloud 2113–6500ms (measured) — a reasoning cloud model is the "
                                   "wrong tool on the always-listen hot path. Bind when the 4B is resident."),
            "thinking": False,                # WANTS a fast non-reasoning model (a reasoner stalls the hot path)
            "output": "one word: FINISHED | MORE",
            "tools": [],                      # no tools — a pure classifier
            "context": "the utterance text only (no system grounding)",
            "knobs": {"max_tokens": 256, "temperature": 0},
            "env_model": "COMPANY_JUDGE_MODEL", "env_url": "COMPANY_JUDGE_URL",
            "env_knobs": {"max_tokens": "COMPANY_JUDGE_MAX_TOKENS"},
        },
    }

    # --- the MODEL KNOB CATALOG (G8.1 — dynamic knob resolution; mirrors STT_PROVIDERS/ROLE_REGISTRY) --
    # "all the configurable knobs for whatever is loaded" (Tim): a declarative catalog of the per-request
    # knobs a chat model exposes. knobs_for(model) resolves it DYNAMICALLY — tool-capability is PROBED
    # live (the existing _model_supports_tools, endpoint-aware), the rest are DECLARED-by-capability
    # (thinking/structured-output can't be universally probed; marked source='declared'). Emitted in the
    # NODE CONFIG SHAPE ({type,label,default,min?,max?,options?}) so the UI renders model-knobs with the
    # SAME NodeConfigForm it renders node config — one resolution, two faces (the RHM tools + the UI).
    # Load-time knobs (gpu-util/ctx) are per-service launch DATA (services.json load.env, the A mechanism),
    # not per-request — kept separate. Adding a knob = a row here; no dispatch edit.
    MODEL_KNOBS = {
        "temperature":       {"type": "number", "label": "Temperature", "default": 0.7, "min": 0.0, "max": 2.0,
                              "applies": "always", "note": "sampling randomness"},
        "max_tokens":        {"type": "number", "label": "Max output tokens", "default": 1024, "min": 1, "max": 32768,
                              "applies": "always"},
        "top_p":             {"type": "number", "label": "Top-p", "default": 1.0, "min": 0.0, "max": 1.0,
                              "applies": "always"},
        "tools":             {"type": "boolean", "label": "Native tool-calling", "default": True,
                              "applies": "capability", "note": "PROBED live per the endpoint (vllm/ollama/litellm)"},
        "thinking":          {"type": "boolean", "label": "Reasoning / thinking", "default": False,
                              "applies": "declared", "note": "reasoning models (ollama think / a reasoning-parser)"},
        "structured_output": {"type": "choice", "label": "Structured output", "default": "none",
                              "options": ["none", "json", "json_schema"], "applies": "declared",
                              "note": "vLLM guided-decoding / ollama format=json"},
    }

    # --- VOICE PATHS (Tier 4 — the SWAPPABLE voice architecture; registry-is-truth) ------------------
    # Tim: "that [S2S] should be a swappable thing." Two ways the RHM can voice:
    #   pipeline — STT → brain → TTS (3 models, full control, BUILT, the default)
    #   s2s      — one fused audio→audio model (Qwen3-Omni/Moshi/GLM-Voice/mini-omni): sub-second,
    #              full-duplex, but the brain+voice are fused (less control). NO such model is on disk
    #              yet (only STT+TTS components + canary/granite which are speech→TEXT, not s2s) — so
    #              the s2s path is available:false until one is downloaded (mirrors a down-ear). The
    #              SWAPPABILITY is built now (a voice_path slot); the s2s runner is a fail-loud stub.
    VOICE_PATHS = {
        "pipeline": {"label": "Pipeline (STT → brain → TTS)", "built": True,
                     "note": "3 models, full per-stage control + config; the default. Tier 1 streaming."},
        "s2s":      {"label": "Speech-to-speech (one fused model)", "built": False,
                     "note": "sub-second + full-duplex; brain+voice fused. Needs an S2S model downloaded "
                             "(candidates: Qwen3-Omni, Moshi, GLM-Voice, mini-omni). No runner until then."},
    }
    # HF-cache name fragments that would indicate an s2s/omni model is present (probed by voice_paths()).
    _S2S_HINTS = ("omni", "moshi", "glm-voice", "glm4-voice", "mini-omni", "miniomni", "qwen2.5-omni",
                  "qwen3-omni", "ultravox", "llama-omni", "csm", "sesame")

    MODE_DIRECTIVES = {
        "listening": "Conversational and present; respond fully.",
        "text-only": "Respond in text, concisely, only to what is addressed.",
        "background": "Be minimal — surface only what genuinely needs the operator; otherwise a one-line acknowledgement.",
        "focus": "The operator is in deep work. Be extremely brief (one or two lines); do not elaborate unless asked.",
        "walkthrough": "Actively guide: narrate what you are doing and direct the operator's attention step by step.",
        "watch-and-react": "Observe; comment only when relevant, and briefly.",
        "decide-for-me": "Act on what the governance posture lets you act on (the AUTO/reversible classes — propose a node, run the graph) rather than asking; surface the rest for the operator. The routing is deterministic (the action's posture decides), not a judgement call. You still cannot self-approve; anything that needs approval is surfaced.",
        # D13: 'off' now carries a one-line DESCRIPTION (was an empty string — the only mode with none,
        # so the surface had nothing to render for it). chat() still short-circuits on mode=='off' BEFORE
        # any directive is used, so this is purely descriptive for the surface (capabilities().
        # mode_directives) — it does NOT re-enable the RHM. modes_acceptance asserts non-empty directives
        # only for m != 'off', so this is schema-additive there too.
        "off": "The right-hand-man is asleep — no conversation, no actions. Switch any other mode on the presence dial to wake it.",
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

    # --- the STT (ear) slot: a SWAPPABLE speech-to-text provider, mirroring the brain-model slot ---
    # The RHM's ear is a config slot just like its brain model — so the operator can swap providers
    # without code. The stt lane (voice/stt.py) is the source of truth for WHAT ears exist; this slot
    # records WHICH one is selected. Because the stt lane DEPENDS on this lane and may not have shipped
    # its richer registry (STT_PROVIDERS / available_stt()) yet, we GUARD the import and degrade
    # gracefully: prefer the new registry when present, else fall back to the current `available()` dict
    # + `DEFAULT_PROVIDER`. Never fabricate a provider id (rule 8) — the valid ids come from voice/stt.py.
    @staticmethod
    def _stt_module():
        """The voice STT module, or None if voice isn't importable here (a status read must never
        crash a turn). Namespace import (no voice/__init__.py) — mirrors bridge.py's usage."""
        try:
            from voice import stt as voice_stt
            return voice_stt
        except Exception:
            return None

    def available_stt(self) -> dict:
        """Which STT providers exist + are usable right now — the registry the UI/RHM reads (never
        guess). Prefers the stt lane's richer `available_stt()` (status read, never raises) when it has
        shipped; else the current `available()` {id: usable}. {} when voice isn't importable."""
        m = self._stt_module()
        if m is None:
            return {}
        fn = getattr(m, "available_stt", None) or getattr(m, "available", None)
        try:
            return fn() if fn else {}
        except Exception:
            return {}

    def _stt_provider_ids(self) -> list:
        """The valid STT provider IDS to validate a selection against — from voice/stt.py's source of
        truth (STT_PROVIDERS when present, else the keys of available()). Empty when voice is absent."""
        m = self._stt_module()
        if m is None:
            return []
        providers = getattr(m, "STT_PROVIDERS", None)
        if isinstance(providers, dict):
            return list(providers.keys())
        try:
            return list((getattr(m, "available", lambda: {})() or {}).keys())
        except Exception:
            return []

    def _stt_default(self) -> str:
        """The default ear id — the stt lane's STT_DEFAULT/DEFAULT_PROVIDER when present, else ''."""
        m = self._stt_module()
        if m is None:
            return ""
        return getattr(m, "STT_DEFAULT", None) or getattr(m, "DEFAULT_PROVIDER", "") or ""

    # --- RHM configs (E1-E2): model/provider + persona, all configurable + persistent ---
    def rhm_config(self) -> dict:
        from fabric import config as fcfg
        c = self._rhm_cfg()
        return {"mode": c.get("mode", self.DEFAULT_MODE),
                "model": c.get("model") or fcfg.DEFAULT_BRAIN,
                "base_url": c.get("base_url") or fcfg.DEFAULT_BASE_URL,
                "persona": c.get("persona", ""),
                # call-site timeout (D2): the interactive RHM model calls (chat reply, react) inherit
                # THIS, so the RHM never hangs minutes on a slow endpoint. Default DEFAULT_TIMEOUT (the
                # moderate 180s); configurable + persistent like the rest. Schema-additive (absent → default).
                # consult() + the self-coding calls deliberately use the longer DEFAULT_CLOUD_TIMEOUT
                # directly (they can wait) — see those call sites; this slot governs the INTERACTIVE calls.
                "timeout": int(c.get("timeout") or fcfg.DEFAULT_TIMEOUT),
                # voice-trial lane H: surface the per-mode voice toggle in the config the FE reads.
                # Default 'on' so a node with no field is voice-enabled (schema-additive).
                "voice_enabled": c.get("voice_enabled", "on"),
                # the STT (ear) slot — WHICH speech-to-text provider the RHM listens through. A config
                # slot mirroring `model` (the brain). Default = the stt lane's default ear when present
                # (else ''); the operator swaps providers without code. Schema-additive (absent → default).
                "stt": c.get("stt") or self._stt_default(),
                # the TTS slots (G4.2): an OPTIONAL active-engine + voice-arg OVERRIDE. Default '' →
                # the circuit uses the PERSONA's engine (personas.py) — so qwen3tts stays Sable's default,
                # nothing changes unless the operator explicitly picks an engine. Lets the config lab swap
                # the voice engine + voice-arg live without touching the persona. Schema-additive.
                "tts_engine": c.get("tts_engine", ""),
                "tts_voice": c.get("tts_voice", ""),
                # the VOICE PATH slot (Tier 4): 'pipeline' (default, built) or 's2s' (needs a model).
                "voice_path": c.get("voice_path", "pipeline"),
                # the ROLE BINDINGS — {role_id: {model?, base_url?, knobs?, ...}} per the ROLE_REGISTRY.
                # n model-FUNCTION roles (judge first; more to come) each bind a model + config from the
                # live registry. Stored as ONE dict so adding a role never touches the config whitelist.
                # Schema-additive (absent → {}); the brain stays its OWN slot (`model`) — NOT a role here.
                "roles": c.get("roles", {})}

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
                   if k in ("model", "base_url", "persona", "mode", "voice_enabled", "timeout", "stt",
                            "roles", "tts_engine", "tts_voice", "voice_path")}
        if "voice_path" in allowed:                           # the voice-path slot (registry-is-truth)
            vp = str(allowed["voice_path"]).strip()
            if vp not in self.VOICE_PATHS:
                raise ValueError(f"unknown voice_path {vp!r} — one of {sorted(self.VOICE_PATHS)}")
            allowed["voice_path"] = vp
        if "tts_engine" in allowed and str(allowed["tts_engine"]).strip():
            # validate against the engine port map (registry-is-truth; '' clears → persona default)
            from voice import loop as _vl
            eng = str(allowed["tts_engine"]).strip()
            if eng not in _vl.ENGINE_PORTS and eng != "kokoro":
                raise ValueError(f"unknown TTS engine {eng!r} — one of {['kokoro'] + sorted(_vl.ENGINE_PORTS)}")
            allowed["tts_engine"] = eng
        if "roles" in allowed:                                # the role-binding registry slot (n roles)
            incoming = allowed["roles"]
            if not isinstance(incoming, dict):
                raise ValueError("roles must be a dict {role_id: {model?, base_url?, knobs?, ...}}")
            for rid, binding in incoming.items():
                if rid not in self.ROLE_REGISTRY:             # registry-is-truth: fail loud on an unknown role
                    raise ValueError(f"unknown role {rid!r} — registered roles: {sorted(self.ROLE_REGISTRY)}. "
                                     f"Author from the registry, never invent (add a role TYPE in code first).")
                if not isinstance(binding, dict):
                    raise ValueError(f"role {rid!r} binding must be a dict (model?/base_url?/knobs?/…)")
            # MERGE with the existing bindings (set_config does a shallow top-level update, which would
            # REPLACE the whole roles dict — so we deep-merge here). THREE levels so a partial update is
            # non-destructive: (1) binding one role never wipes a SIBLING role; (2) within a role,
            # incoming keys override, others preserved; (3) the `knobs` SUB-dict deep-merges too, so
            # setting one knob (e.g. temperature) never resets another (e.g. max_tokens). Verified: a
            # partial knob update used to drop the other knob to its default — this keeps both.
            existing = dict(self.rhm_config().get("roles", {}))
            for rid, binding in incoming.items():
                merged = dict(existing.get(rid, {}))
                inc = dict(binding)
                if "knobs" in inc and isinstance(merged.get("knobs"), dict):
                    knobs = dict(merged["knobs"]); knobs.update(inc["knobs"] or {})
                    inc["knobs"] = knobs                      # deep-merge the knobs sub-dict
                merged.update(inc)
                existing[rid] = merged
            allowed["roles"] = existing
        if "mode" in allowed and allowed["mode"] not in self.MODES:
            raise ValueError(f"unknown mode {allowed['mode']!r}")
        if "stt" in allowed:                                  # the ear slot — validate against voice/stt.py's
            # source of truth (never fabricate a provider id, rule 8). When the stt lane's registry has
            # shipped we validate ∈ its ids; until then (registry absent → no ids) we accept any non-empty
            # str (TODO: tighten once voice/stt.py exports STT_PROVIDERS/available_stt — coordinated with
            # the stt lane, which depends on THIS slot existing; do not block on it).
            ids = self._stt_provider_ids()
            val = str(allowed["stt"]).strip()
            if not val:
                raise ValueError("stt provider must be a non-empty id")
            if ids and val not in ids:
                raise ValueError(f"unknown STT provider {val!r} — one of {ids}")
            allowed["stt"] = val
        if "voice_enabled" in allowed and str(allowed["voice_enabled"]).lower() not in ("on", "off"):
            raise ValueError(f"voice_enabled must be 'on' or 'off', got {allowed['voice_enabled']!r}")
        if "timeout" in allowed:                              # the interactive call-site timeout — positive int
            try:
                t = int(allowed["timeout"])
            except (TypeError, ValueError):
                raise ValueError(f"timeout must be a positive integer (seconds), got {allowed['timeout']!r}")
            if t <= 0:
                raise ValueError(f"timeout must be a positive integer (seconds), got {allowed['timeout']!r}")
            allowed["timeout"] = t
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

        # --- WHOLE-INTERFACE grounding (Tim: "everything it needs to be aware of in the whole
        # interface") — every value below comes from the LIVE registry/state, never fabricated. The
        # model reads are fail-loud-LEGIBLE (rule 4): a down endpoint renders a marker + emits a
        # warning, never a silent omission and never a crash (a raise here would break every turn).
        try:
            chat_models = self.available_models()             # chat — cached; warns on a down endpoint
        except Exception as e:                                 # defensive: never let grounding crash a turn
            self._emit("warning", f"chat model registry unreachable in RHM context ({type(e).__name__})")
            chat_models = None
        try:
            embed_models = self.models_at("embed")            # embed — its OWN endpoint; may be down
        except Exception as e:
            self._emit("warning", f"embed model registry unreachable in RHM context ({type(e).__name__})")
            embed_models = None
        chat_s = ", ".join(chat_models) if chat_models else "(endpoint unreachable)"
        embed_s = ", ".join(embed_models) if embed_models else "(endpoint unreachable)"

        mode = nowv["mode"]
        modes_s = ", ".join(self.MODES)
        # render ONLY the verbs AVAILABLE in this mode×context (mode-primary, context-refines), from
        # the SAME available_verbs() the tools array is built from — so the two channels (what the
        # prompt says it can do + what the native tools array offers) AGREE by construction. (Was: all
        # 7 unconditionally, which told the RHM it could `run` an empty graph or `build` in watch mode.)
        ctx = self._affordance_context(graph_id, focus)
        avail = self.available_verbs(mode, ctx)
        verbs_s = ("; ".join(f"{v} ({self.RHM_VERB_DESC.get(v, '')})" for v in avail)
                   if avail else "(none in this mode/context)")
        lanes = self.inbox_lanes()
        n_esc = lanes["counts"]["escalations"]
        # count AND what's awaiting — so the RHM can answer "what's awaiting", not just "how many".
        esc_titles = []
        for d in lanes["live_escalations"][:6]:
            pl = d.get("payload") or {}
            esc_titles.append(str(pl.get("title") or pl.get("name") or d.get("action") or d.get("id"))[:48])
        awaiting_s = ("; ".join(esc_titles) + ("…" if n_esc > 6 else "")) if esc_titles else "(nothing)"
        all_graphs = self.list_graphs()                       # keep COMPACT: count + the current graph
        others = [x for x in all_graphs if x != nowv["graph"]]
        graphs_s = (f"{len(all_graphs)} total — current: {nowv['graph']}"
                    + (f"; others incl. {', '.join(others[:5])}" + ("…" if len(others) > 5 else "") if others else ""))
        panels_s = ", ".join(p.get("id", "?") for p in self.list_panels()) or "(none)"
        # the valid ui:// show-targets, from the UI_REGISTRY (single-source; chrome refs as full ui:// refs).
        show_targets_s = ", ".join(
            ("ui://canvas/*" if kind == "canvas" else f"ui://{kind}/{ref}")
            for ref, kind, *_ in self.UI_REGISTRY) or "(none)"

        ctx = (
            "LIVE SYSTEM STATE (ground truth — answer only from this):\n"
            f"- graph: {nowv['graph']} · {nowv['nodes_total']} nodes, {nowv['nodes_resolved']} resolved"
            f", {len(self._last_run_stuck(nowv['graph']))} stuck"
            f" · {nowv['surfaced_pending']} awaiting approval · presence: {nowv['presence']}\n"
            f"- nodes: {nodes}\n"
            f"- available node-types: {', '.join(self.list_types())}\n"
            f"- chat models: {chat_s}\n"
            f"- embed models: {embed_s}\n"
            f"- presence modes: {modes_s} (current: {mode})\n"
            f"- RHM verbs you can perform: {verbs_s}\n"
            # show-targets vocabulary (grounding for the `show` verb): enumerate the valid ui:// chrome
            # refs from the UI_REGISTRY (single-source) + note node-ids are valid targets, so the RHM
            # GROUNDS `show` in real handles instead of guessing. A bare handle resolves leniently.
            f"- show targets (ui:// regions): {show_targets_s}; plus any node-id above is a valid show target\n"
            f"- inbox: {n_esc} item(s) awaiting you — {awaiting_s}\n"
            f"- graphs (multigraph): {graphs_s}\n"
            f"- panels: {panels_s}\n"
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

    # ════════════════════════════════════════════════════════════════════════════════════════════
    # THE SINGLE-SOURCE RHM VERB REGISTRY (replaces the old 3 parallel tables RHM_VERBS /
    # RHM_VERB_DESC / RHM_VERB_CLASS, which could drift). ONE VerbSpec per verb carries everything:
    # the gloss, the governance class, the modes it is OFFERED in (mode-primary), and a predicate over
    # the live affordance context (context-refines). The three legacy names are DERIVED below — there
    # is no second copy to fall out of sync (AGENTS.md rule 3, one-source).
    #
    # MODE SETS (per the Change-Maps §suite, mode-primary / context-refines):
    #   run    → {focus, background, listening, text-only, decide-for-me}
    #            pred = graph_nonempty (no point recomputing an empty graph)
    #            NOT walkthrough / watch-and-react: those are GUIDE / OBSERVE modes (show+consult only) —
    #            they do not RECOMPUTE the graph (spec-aligned). (whether walkthrough should offer run is
    #            a Tim mode-design call — flagged needs_tim; shipping the spec-aligned version now.)
    #   show   → all modes BUT 'off'
    #   consult→ {walkthrough, watch-and-react, listening, text-only, decide-for-me}
    #   build/propose/panel/extend → {listening, text-only, decide-for-me}
    #   off    → no verb is offered (the RHM is disabled; chat() short-circuits before this anyway)
    #   text-only MIRRORS listening for the ACTION set (its style differs via the mode directive, not
    #            the affordances) — so wherever 'listening' appears above, 'text-only' appears too.
    # The dict insertion ORDER (run, propose, build, consult, show, panel, extend) defines RHM_VERBS'
    # tuple order — kept identical to the prior literal so RHM_VERBS == the same 7-tuple (a contract
    # rhm_completion_acceptance asserts exactly).
    # ════════════════════════════════════════════════════════════════════════════════════════════
    _M_BUILDISH = frozenset({"listening", "text-only", "decide-for-me"})
    _M_RUN = frozenset({"focus", "background", "listening", "text-only", "decide-for-me"})
    _M_CONSULT = frozenset({"walkthrough", "watch-and-react", "listening", "text-only", "decide-for-me"})
    _M_ALL_BUT_OFF = frozenset(MODES) - {"off"}

    RHM_VERB_SPECS = {
        "run":     VerbSpec("recompute the current graph", "run",
                            _M_RUN, lambda ctx: ctx.get("graph_nonempty", False)),
        "propose": VerbSpec("draft a new node-type for approval", "register_type",
                            _M_BUILDISH, lambda ctx: True),
        "build":   VerbSpec("compose a pipeline on the canvas", "compose",
                            _M_BUILDISH, lambda ctx: True),
        "consult": VerbSpec("read the system's own code+design", "inspect",
                            _M_CONSULT, lambda ctx: True),
        "show":    VerbSpec("move the operator's view to node(s)/UI", "inspect",
                            _M_ALL_BUT_OFF, lambda ctx: True),
        "panel":   VerbSpec("add a declarative settings panel", "ui_panel",
                            _M_BUILDISH, lambda ctx: True),
        "extend":  VerbSpec("write a new UI component (build-gated)", "ui_extension",
                            _M_BUILDISH, lambda ctx: True),
        # G8.2 — config-as-tools: the RHM operates its OWN config by voice, not only the UI. All AUTO
        # (governance class 'configure') — operator-directed + reversible; the lifecycle fail-louds on
        # VRAM. configure sets any rhm_config slot (model/persona/mode/stt/tts_engine/voice_enabled/roles
        # — so "use the fast judge" or "switch to xtts" works); load/unload_voice drive the lifecycle.
        "configure":    VerbSpec("set RHM config (model/persona/mode/voice/ear/role bindings)", "configure",
                                 _M_BUILDISH, lambda ctx: True),
        "load_voice":   VerbSpec("load a voice service (STT ear / TTS engine) into VRAM", "configure",
                                 _M_BUILDISH, lambda ctx: True),
        "unload_voice": VerbSpec("unload a voice service to free VRAM", "configure",
                                 _M_BUILDISH, lambda ctx: True),
    }

    # --- the three legacy names, DERIVED from the one registry (no drift) ---
    # The dispatcher's WHITELIST: a verb the RHM may perform. apply/delete/file-write are NOT here, so
    # the conversational surface can never reach them (E6). Tuple in registry-insertion order.
    RHM_VERBS = tuple(RHM_VERB_SPECS)
    # one-line gloss per verb — so the grounding context can tell the RHM its OWN capabilities.
    RHM_VERB_DESC = {v: s.desc for v, s in RHM_VERB_SPECS.items()}
    # G3: each verb's GOVERNANCE action-class — the deterministic decide-for-me router input. AUTO
    # classes (run/compose/inspect) run; CONFIRM classes (register_type/ui_panel/ui_extension) surface.
    RHM_VERB_CLASS = {v: s.action_class for v, s in RHM_VERB_SPECS.items()}

    # the OpenAI-tool parameter schema per verb — built FROM the registry (single-source). The shapes
    # MIRROR exactly what _json_obj_to_action consumes (so a native tool_call round-trips to an action
    # dict with no shape drift): run{} · consult{query} · show{targets[]} · build{steps[]} ·
    # propose/panel/extend{name,spec}.
    _VERB_PARAMS = {
        "run":     {"type": "object", "properties": {}},
        "consult": {"type": "object",
                    "properties": {"query": {"type": "string",
                                             "description": "the question about this system's own design/code"}},
                    "required": ["query"]},
        "show":    {"type": "object",
                    "properties": {"targets": {"type": "array", "items": {"type": "string"},
                                               "description": "node-ids and/or ui:// regions to move the view to"}},
                    "required": ["targets"]},
        "build":   {"type": "object",
                    "properties": {"steps": {"type": "array", "items": {"type": "object"},
                                             "description": "pipeline steps: a node {as,type,config} or a wire {wire:'a.port -> b.port'}"}},
                    "required": ["steps"]},
        "propose": {"type": "object",
                    "properties": {"name": {"type": "string"}, "spec": {"type": "string"}},
                    "required": ["name", "spec"]},
        "panel":   {"type": "object",
                    "properties": {"name": {"type": "string"}, "spec": {"type": "string"}},
                    "required": ["name", "spec"]},
        "extend":  {"type": "object",
                    "properties": {"name": {"type": "string"}, "spec": {"type": "string"}},
                    "required": ["name", "spec"]},
        "configure":    {"type": "object",
                         "properties": {"updates": {"type": "object",
                             "description": "rhm_config slots to set: any of model, base_url, persona, mode, "
                                            "stt, tts_engine, tts_voice, voice_enabled, timeout, roles "
                                            "({role_id:{model,base_url,knobs}})"}},
                         "required": ["updates"]},
        "load_voice":   {"type": "object",
                         "properties": {"service": {"type": "string",
                             "description": "a loadable voice-service id (e.g. tts-qwen3tts, stt-parakeet)"}},
                         "required": ["service"]},
        "unload_voice": {"type": "object",
                         "properties": {"service": {"type": "string"}}, "required": ["service"]},
    }

    def _affordance_context(self, graph_id: str, focus: dict | None = None) -> dict:
        """The live AFFORDANCE CONTEXT a verb's predicate is evaluated against — all derived from
        EXISTING reads (state() / now() / the operator's focus), nothing fabricated:
          - graph_nonempty : the current graph has at least one node (a `run` makes sense)
          - inbox_pending  : there is at least one item awaiting the operator
          - node_selected  : the operator currently has a node selected on the canvas (co-presence)
        Tolerant: a read hiccup degrades a flag to False rather than crashing a turn (the affordance
        layer narrows the OFFER; the dispatcher's whitelist is the real gate, so a conservative-False
        here only offers fewer verbs, never weakens safety)."""
        try:
            st = self.state(graph_id)
            graph_nonempty = len(st.get("nodes", [])) > 0
        except Exception:
            graph_nonempty = False
        try:
            inbox_pending = any(d.get("resolved") is None for d in self.inbox.list())
        except Exception:
            inbox_pending = False
        node_selected = bool((focus or {}).get("selected"))
        return {"graph_nonempty": graph_nonempty,
                "inbox_pending": inbox_pending,
                "node_selected": node_selected}

    def available_verbs(self, mode: str, ctx: dict) -> list:
        """The verbs OFFERED right now = those whose spec lists this `mode` AND whose predicate holds
        for the live affordance context. Mode-primary, context-refines. Order follows the registry
        (run, propose, build, …) so the rendered list + the tools array are deterministic. This is the
        ONE source both channels (the rendered verb list in _chat_context and the _rhm_tools array)
        read, so the two never disagree about what the RHM may do."""
        return [v for v, s in self.RHM_VERB_SPECS.items()
                if mode in s.modes and s.predicate(ctx)]

    def _rhm_tools(self, mode: str, ctx: dict) -> list:
        """The OpenAI tools array for THIS turn — built FROM available_verbs() + the single-source
        RHM_VERB_DESC (description) + _VERB_PARAMS (schema). So the model is offered exactly the verbs
        that are mode-appropriate + context-sensible, each as a native function tool. Empty list when
        no verb is available (off, or an empty graph with only `run` eligible) — the caller then passes
        no tools (tool_choice auto over zero tools = a plain reply)."""
        tools = []
        for v in self.available_verbs(mode, ctx):
            tools.append({
                "type": "function",
                "function": {
                    "name": v,
                    "description": self.RHM_VERB_DESC.get(v, ""),
                    "parameters": self._VERB_PARAMS.get(v, {"type": "object", "properties": {}}),
                },
            })
        return tools

    # tool-capability gate: a short-TTL cache (mirrors available_models) so the RHM doesn't re-probe
    # /api/show on every turn, while a model brought up later still becomes usable without a restart.
    _tools_cap_cache: dict = {}                               # (model, base_url) -> (bool, monotonic_stamp)
    TOOLS_CAP_TTL = 60.0

    def _model_supports_tools(self, model: str, base_url: str | None = None) -> bool:
        """Endpoint-aware, FAIL-LOUD tool-capability gate (rule 4 — no silent assume-capable). Delegates
        to the fabric helper (transport.model_supports_tools), which RAISES if it cannot determine the
        answer (endpoint down / no capabilities field / unknown endpoint kind). Here we translate a
        cannot-determine RAISE into FALSE — the RHM treats 'can't prove it supports tools' as 'does NOT',
        the safe refusal (a non-tool model must never silently be called with tools). Cached short-TTL
        (TOOLS_CAP_TTL) keyed on (model, base_url); a model that comes up later becomes usable without a
        restart. A POSITIVE (True) result is cached; a False from an unreachable endpoint is NOT cached
        (so recovery is immediate, mirroring the degraded-models policy)."""
        import time as _t
        from fabric import config as fcfg, transport as ftrans
        base = base_url or fcfg.DEFAULT_BASE_URL
        key = (model, base)
        hit = self._tools_cap_cache.get(key)
        if hit is not None and (_t.monotonic() - hit[1]) < self.TOOLS_CAP_TTL:
            return hit[0]
        # Classify the endpoint so the tool-cap detector probes the RIGHT way (was: everything-not-4100
        # = ollama, which mis-routed a raw vLLM endpoint to ollama's /api/show → false refusal). ollama
        # is :11434; litellm proxy :4100; a raw vLLM OpenAI server (the local model workers, :8000+) is
        # its own kind (probed by a forced tool-call). Default base (config) stays ollama.
        from fabric import config as _fc
        if "4100" in base:
            endpoint = "litellm"
        elif "11434" in base or base.rstrip("/") == _fc.DEFAULT_BASE_URL.rstrip("/"):
            endpoint = "ollama"
        else:
            endpoint = "vllm"                                  # raw OpenAI-compatible vLLM (local workers)
        try:
            ok = bool(ftrans.model_supports_tools(model, base_url=base, endpoint=endpoint))
        except Exception:
            return False                                       # cannot determine → False (safe), NOT cached
        self._tools_cap_cache[key] = (ok, _t.monotonic())
        return ok

    # consult retrieval: the WHOLE repo (~400k chars ≈ 100k tokens) into one model call overflowed /
    # ran slow / "didn't return". So consult RETRIEVES a query-relevant slice instead of stuffing the
    # repo — keyword scan over the SAME file set the codebase node reads (single-source the corpus), no
    # embed-service dependency (retrieval-proper/embed is still future). Cap the fed source so it stays
    # bounded; cite which files were used; on no match fall back to a small curated set (never the whole
    # repo). The "answer strictly from source, cite the file, abstain if absent" contract is preserved.
    CONSULT_CAP = 40000                                       # max chars of source fed to the model (~10k tok)
    CONSULT_PER_FILE_CAP = 8000                               # max chars any ONE file contributes — so a single
    #                                                            huge file (suite.py ≈140k) can't monopolize the
    #                                                            budget and crowd out the actually-relevant smaller
    #                                                            file (scheduler.py). ~CAP/5 → ≥5 distinct files of
    #                                                            headroom. Big files get a relevance-WINDOWED slice
    #                                                            (around the first term hit — the brief's "sections"),
    #                                                            small files come in whole.
    CONSULT_CURATED = ("AGENTS.md", "MAP.md", "STATE.md")     # the orientation fallback when nothing matches
    _CONSULT_STOPWORDS = frozenset((
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being", "of", "to", "in", "on",
        "for", "and", "or", "but", "with", "as", "by", "at", "from", "how", "what", "why", "where",
        "when", "which", "who", "does", "do", "did", "this", "that", "these", "those", "it", "its",
        "system", "work", "works", "i", "you", "me", "my", "can", "could", "would", "should", "tell",
        "about", "explain", "describe", "show", "get", "use", "used", "have", "has", "into", "out"))

    @classmethod
    def _consult_terms(cls, query: str) -> list:
        """Salient lowercase terms from a query — words ≥3 chars, minus stopwords. The retrieval keys."""
        import re
        words = re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", (query or "").lower())
        seen, out = set(), []
        for w in words:
            if w in cls._CONSULT_STOPWORDS or w in seen:
                continue
            seen.add(w); out.append(w)
        return out

    def _retrieve_for_consult(self, query: str) -> tuple:
        """Keyword retrieval over the repo — returns (context, sources, file_list). Feeds ONLY the
        query-relevant files/sections (bounded by CONSULT_CAP), not the whole repo. file_list is a short
        repo orientation (every candidate file's relpath). sources is the files actually fed (for the
        citation + the test). On no keyword match, falls back to the curated orientation set — NEVER the
        whole repo. No embed-service dependency: a plain term scan (relevance = term-hit count)."""
        import os, glob
        from nodes import codebase as cb
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # ~/company (single-source w/ codebase node)
        files = []                                            # (relpath, text) for every candidate file
        for g in cb.DEFAULT_GLOBS:
            for p in sorted(glob.glob(os.path.join(root, g))):
                try:
                    text = open(p, encoding="utf-8").read()
                except Exception:
                    continue
                files.append((os.path.relpath(p, root), text))
        file_list = [rel for rel, _ in files]
        terms = self._consult_terms(query)
        scored = []
        for rel, text in files:
            low = text.lower(); rel_low = rel.lower()
            score = sum(low.count(t) + (3 if t in rel_low else 0) for t in terms)   # filename match weighted
            if score > 0:
                scored.append((score, rel, text))
        scored.sort(key=lambda x: (-x[0], x[1]))
        if not scored:                                        # no match → curated orientation set, never the whole repo
            picked = []                                       # read the curated files DIRECTLY (not all are in the
            for rel in self.CONSULT_CURATED:                  # codebase globs — STATE.md isn't — so don't depend on it)
                try:
                    picked.append((rel, open(os.path.join(root, rel), encoding="utf-8").read(), []))
                except Exception:
                    continue
        else:
            picked = [(rel, text, [t for t in terms if t in text.lower()]) for _, rel, text in scored]
        # Fill the budget ACROSS the top-ranked files (relevance order), capping each file's contribution
        # to CONSULT_PER_FILE_CAP so no single huge file monopolizes the budget. A small file comes in
        # whole; a big file gets a relevance-WINDOWED slice (centred on its first matching term — the
        # brief's "files/SECTIONS"), so the slice carries the relevant code, not the header/imports.
        parts, sources, total = [], [], 0
        for rel, text, hits in picked:
            if total >= self.CONSULT_CAP:
                break
            budget = min(self.CONSULT_PER_FILE_CAP, self.CONSULT_CAP - total)
            if len(text) <= budget:                           # small file → whole
                chunk = f"\n===== {rel} =====\n{text}\n"
            else:                                             # big file → windowed slice around the first hit
                low = text.lower()
                pos = min((low.find(t) for t in hits if low.find(t) >= 0), default=0)
                start = max(0, pos - 1000)
                excerpt = text[start:start + budget]
                tag = rel if start == 0 and len(excerpt) >= len(text) else f"{rel} (excerpt)"
                chunk = f"\n===== {tag} =====\n{excerpt}\n"
            if total + len(chunk) > self.CONSULT_CAP and parts:
                break                                         # keep the overall cap hard once we have something
            parts.append(chunk); sources.append(rel); total += len(chunk)
        context = "".join(parts)
        return context, sources, file_list

    def consult(self, query: str) -> dict:
        """The RHM reads the system's OWN code+design (the first-purpose Q&A, as a callable) and
        answers — so it knows how it is built. Grounded in a RETRIEVED, query-relevant slice (keyword
        scan, bounded by CONSULT_CAP — NOT the whole repo, which overflowed/stalled); cites the files
        used; abstains if the answer isn't there. A read (AUTO). Uses DEFAULT_CLOUD_TIMEOUT (a consult
        can wait)."""
        from fabric import client, transport, config as fcfg
        cfg = self.rhm_config()
        context, sources, file_list = self._retrieve_for_consult(query)
        orient = ", ".join(file_list)
        sys_p = ("You answer questions about THIS system's own design and code, STRICTLY from the SOURCE "
                 "below (a RETRIEVED slice of the repo selected for this question, not the whole repo). "
                 "Cite the relevant file(s). If the answer is not in the source provided, say so plainly "
                 "(it may live in a file that wasn't retrieved — name what you'd need). Concise.\n"
                 f"REPO FILE-LIST (for orientation — these files exist): {orient}")
        ans = client.complete(transport.openai_transport(base_url=cfg["base_url"], timeout=fcfg.DEFAULT_CLOUD_TIMEOUT),
                              [{"role": "system", "content": sys_p},
                               {"role": "user", "content": f"SOURCE:\n{context}\n\nQUESTION: {query}"}],
                              model=cfg["model"])
        return {"answer": ans, "sources": sources}

    # --- model-/provider-AGNOSTIC action mapping -------------------------------------------------
    # The requirement (Tim): the RHM must ACT regardless of which model/provider is selected, and a
    # NEW model must "just work". The RHM now acts through NATIVE TOOL-CALLING — chat() feeds each
    # tool_call's {name, arguments} through `_json_obj_to_action` (below) to the SAME dispatcher dict
    # the gate already takes. There is no prose-parsing step: the old `ACTION:`-line / `<invoke>` /
    # fenced-json / bare-json TEXT-shape parser cluster (_parse_rhm_action + _normalise_rhm_action +
    # _strip_provider_delims + _PROVIDER_DELIMS) has been RETIRED — chat() never used it once it moved
    # to native tools. The mapper is shape-recognition ONLY: it does NOT whitelist (that would be a
    # second whitelist that drifts from the dispatcher's — AGENTS.md rule 3). The ONE whitelist lives
    # in `_dispatch_rhm_action` (RHM_VERBS), so a forbidden verb mapped here is REFUSED there (the E6
    # no-bypass guarantee, proven end-to-end via chat() in rhm_action_parse_acceptance.py).

    @classmethod
    def _json_obj_to_action(cls, obj: dict, verb: str):
        """Normalise a JSON tool-call object → the dispatcher dict. The args may be a nested
        `arguments`/`args`/`input` dict (OpenAI/Anthropic style) OR fields on the object itself
        (the fenced `{"verb":..,"targets":..}` style). Either way it routes through the ONE
        normaliser, so the same intent yields the same action across shapes."""
        import json as _j
        verb = (verb or "").strip().lower()
        a = obj.get("arguments") or obj.get("args") or obj.get("input") or {}
        if isinstance(a, str):                                 # arguments serialised as a JSON string
            try:
                a = _j.loads(a)
            except Exception:
                a = {}
        merged = {**({k: v for k, v in obj.items() if k not in ("verb", "name", "tool")}), **(a if isinstance(a, dict) else {})}
        if verb == "build":
            steps = merged.get("steps") or merged.get("pipeline") or merged.get("json")
            return {"verb": "build", "steps": steps if isinstance(steps, list) else None}
        if verb == "consult":
            return {"verb": "consult", "query": str(merged.get("query") or merged.get("question") or "").strip()}
        if verb == "show":
            t = merged.get("targets") or merged.get("target") or []
            t = [t] if isinstance(t, str) else list(t or [])
            return {"verb": "show", "targets": [str(x) for x in t]}
        if verb in ("propose", "panel", "extend"):
            return {"verb": verb, "name": str(merged.get("name") or "").strip(),
                    "spec": str(merged.get("spec") or merged.get("description") or "").strip()}
        if verb == "run":
            return {"verb": "run"}
        return {"verb": verb}

    @staticmethod
    def _confirmation_for(outcome: dict) -> str:
        """Fold a dispatched verb's outcome dict → ONE concise operator-facing confirmation line, for
        EVERY verb (run/build/show/propose/panel/extend/consult/ask + refused). Before this, only
        consult/ask folded an outcome; run/build/show/propose/panel/extend executed but returned a BLANK
        reply — worst for native-tool-call models that emit no prose. The operator must ALWAYS see what
        happened (rule 4: no silent success). Returns '' only for a None/empty outcome (nothing dispatched).
        consult's full answer is folded by the caller (it carries the looked-up text); here we don't
        duplicate it — '' so the caller's answer-fold stands alone."""
        if not outcome:
            return ""
        did = outcome.get("did")
        if did == "run":
            return f"▶ ran: {len(outcome.get('ran', []))} ran, {len(outcome.get('cached', []))} cached"
        if did == "build":
            if outcome.get("error"):
                return (f"build failed: {outcome['error']}"
                        + (f" (made {len(outcome.get('nodes', []))} before failing)" if outcome.get("nodes") else ""))
            nodes, edges = outcome.get("nodes", []), outcome.get("edges", [])
            wired = (" (" + ", ".join(edges) + ")") if edges else ""
            return f"＋ built {len(nodes)} node(s){wired}"
        if did == "show":
            return "→ moved your view to " + ", ".join(outcome.get("targets", []))
        if did == "propose":
            return f"drafted node '{outcome.get('name')}' — awaiting your approval in the inbox"
        if did == "panel":
            return f"drafted panel '{outcome.get('name')}' — awaiting your approval in the inbox"
        if did == "extend":
            return f"authored UI component '{outcome.get('name')}' (build-gated) — awaiting your approval"
        if did == "consult":
            return ""                                         # the caller folds the full answer text
        if did == "ask":
            return ""                                         # the caller folds the ❓-needs line
        if did == "none":
            return "show refused: " + outcome["refused"] if "show" in str(outcome.get("refused", "")) \
                   else "couldn't do that: " + str(outcome.get("refused", "no effect"))
        return ""                                             # unknown did → nothing to confirm

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
            # LENIENT bare-target grounding: the RHM is told the vocabulary (in _chat_context) but a
            # native-tool-call model still often emits a bare handle ("inbox") rather than the full
            # ui://chrome/inbox. So a bare word that matches a UI_REGISTRY handle resolves to its FULL
            # ref USING THE REGISTRY ENTRY'S OWN KIND (not assumed) — never hardcoded. We refuse ONLY on
            # a genuine no-match (fail-loud preserved). Built from UI_REGISTRY so it can't drift.
            handle_map = {ref: kind for ref, kind, *_ in self.UI_REGISTRY}   # 'inbox'→'chrome', '*'→'canvas'
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
                elif t in handle_map:
                    # LENIENT: a bare UI handle ('inbox') → its full ref via the registry's own kind.
                    # 'canvas' kind is the whole-canvas '*' camera ref; chrome/etc become ui://<kind>/<ref>.
                    k = handle_map[t]
                    targets.append("ui://canvas/*" if (k == "canvas" or t == "*") else f"ui://{k}/{t}")
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
        if verb == "configure":                              # G8.2: the RHM sets its own config (AUTO)
            updates = action.get("updates") or {}
            if not isinstance(updates, dict) or not updates:
                return {"did": "none", "refused": "configure needs a non-empty 'updates' object"}
            cfg = self.set_rhm_config(updates)               # fail-loud on unknown slot/model/role/engine
            return {"did": "configure", "set": sorted(updates.keys()), "config": cfg}
        if verb in ("load_voice", "unload_voice"):           # G8.2: the RHM drives the voice lifecycle (AUTO)
            from voice import lifecycle as _vlc
            svc = action.get("service")
            if not svc:
                return {"did": "none", "refused": f"{verb} needs a 'service' id"}
            try:
                r = _vlc.load(svc) if verb == "load_voice" else _vlc.unload(svc)
            except Exception as e:                           # the lifecycle fail-loud (unknown/won't-fit) → structured, not a crash
                return {"did": verb, "error": f"{type(e).__name__}: {e}"}
            return {"did": verb, **r}
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

    def roles(self) -> dict:
        """The MODEL-ROLE registry as a STATUS read — the config lab's source (it NEVER hardcodes the
        role list). For each registered role: its declared contract (label/description/trigger/output/
        tools/context/thinking/knobs) + the current binding + the EFFECTIVE resolution (what would
        actually be used right now). Mirrors available_stt()'s registry-as-status shape."""
        bindings = self.rhm_config().get("roles", {})
        out = {}
        for rid, spec in self.ROLE_REGISTRY.items():
            out[rid] = {"id": rid, **{k: spec[k] for k in spec
                                      if k not in ("env_model", "env_url", "env_knobs")},
                        "binding": bindings.get(rid, {}),
                        "effective": self.resolve_role(rid)}
        return out

    def resolve_role(self, role_id: str) -> dict:
        """Resolve a role to the EFFECTIVE {model, base_url, knobs, thinking, output, tools, context}
        actually used when the role fires. Precedence (advisor-set): config BINDING > env override >
        declared default; a None default_model falls to the RHM brain (rhm_config.model). Fail loud on
        an unknown role (registry-is-truth). The role's consuming code (e.g. is_finished_thought) calls
        THIS — so swapping a role's model is a config change, never a code change."""
        import os
        if role_id not in self.ROLE_REGISTRY:
            raise ValueError(f"unknown role {role_id!r} — registered: {sorted(self.ROLE_REGISTRY)}")
        spec = self.ROLE_REGISTRY[role_id]
        cfg = self.rhm_config()
        binding = cfg.get("roles", {}).get(role_id, {})
        model = (binding.get("model") or os.environ.get(spec.get("env_model", ""))
                 or spec.get("default_model") or cfg["model"])               # None default → the brain
        base_url = (binding.get("base_url") or os.environ.get(spec.get("env_url", ""))
                    or spec.get("default_base_url") or cfg["base_url"])
        knobs = dict(spec.get("knobs", {}))                                  # declared defaults
        for k, env_name in (spec.get("env_knobs") or {}).items():           # env override
            if os.environ.get(env_name):
                knobs[k] = type(knobs.get(k, 0))(os.environ[env_name]) if isinstance(knobs.get(k), int) else os.environ[env_name]
        knobs.update(binding.get("knobs", {}))                              # binding wins
        return {"role": role_id, "model": model, "base_url": base_url, "knobs": knobs,
                "thinking": binding.get("thinking", spec.get("thinking")),
                "output": spec.get("output"), "tools": spec.get("tools", []),
                "context": spec.get("context")}

    def knobs_for(self, model: str | None = None, base_url: str | None = None) -> dict:
        """G8.1 — DYNAMIC knob resolution: the configurable per-request surface for a (loaded) model,
        in the node config_schema SHAPE so the UI renders it with NodeConfigForm + the RHM can read it
        as a tool. `always` knobs always apply; the `tools` knob is PROBED LIVE (endpoint-aware) — its
        default + availability reflect what the model actually supports right now; `declared` knobs
        (thinking/structured-output, not universally probeable) are offered with source='declared'.
        None model/base_url → the current brain. Reuses MODEL_KNOBS (registry-is-truth) — no hardcoding
        in the UI; adding a knob is a catalog row."""
        cfg = self.rhm_config()
        model = model or cfg["model"]
        base_url = base_url or cfg["base_url"]
        out = {}
        for kid, spec in self.MODEL_KNOBS.items():
            entry = {k: v for k, v in spec.items() if k != "applies"}
            applies = spec.get("applies")
            if applies == "always":
                entry.update(available=True, source="always")
            elif applies == "capability" and kid == "tools":
                ok = self._model_supports_tools(model, base_url)     # PROBED live (vllm/ollama/litellm)
                entry.update(default=ok, available=ok, source="probed")
            else:                                                    # declared (can't universally probe)
                entry.update(available=True, source="declared")
            out[kid] = entry
        return {"model": model, "base_url": base_url, "knobs": out}

    def _s2s_models(self) -> list:
        """Probe the HF cache for any downloaded s2s/omni model (the _S2S_HINTS). Returns matching dir
        names — empty = no s2s model present (so the s2s path stays available:false)."""
        import os
        hub = os.path.expanduser("~/.cache/huggingface/hub")
        try:
            return [d for d in os.listdir(hub) if any(h in d.lower() for h in self._S2S_HINTS)]
        except OSError:
            return []

    def voice_paths(self) -> dict:
        """Tier 4 — the swappable voice-path registry as a STATUS read (the config lab's source). Each
        path + whether it's AVAILABLE right now: pipeline always (built); s2s only if an S2S model is on
        disk (probed). `active` = the rhm_config.voice_path slot (default pipeline). Mirrors the
        available_stt()/roles() registry-as-status shape — the UI never hardcodes the path list."""
        s2s_models = self._s2s_models()
        active = self.rhm_config().get("voice_path", "pipeline")
        out = {}
        for pid, spec in self.VOICE_PATHS.items():
            avail = spec["built"] or (pid == "s2s" and bool(s2s_models))
            entry = {"id": pid, "label": spec["label"], "built": spec["built"], "available": avail,
                     "note": spec["note"], "active": pid == active}
            if pid == "s2s":
                entry["models"] = s2s_models
                entry["detail"] = (f"s2s model present: {s2s_models}" if s2s_models
                                   else "no S2S model on disk — download one (Qwen3-Omni/Moshi/GLM-Voice) to enable")
            out[pid] = entry
        return {"paths": out, "active": active}

    def is_finished_thought(self, text: str) -> dict:
        """The voice circuit's SEMANTIC endpoint judge (G1.3): given the utterance heard so far (after a
        VAD pause), is it a FINISHED THOUGHT — fire the turn — or is the operator mid-ramble — keep
        listening? This is the "not a dumb silence timer" lever: a pause alone does NOT end a turn; a
        MODEL judges completeness.

        JUDGE = the 'judge' ROLE in the ROLE_REGISTRY (resolve_role('judge')) — a separate, configurable,
        fast model, NOT the conversational brain. The judge is a utility classifier on the LIVE turn
        path, so a reasoning brain is the WRONG tool: measured 2026-06-05, deepseek-v4-pro (a reasoner)
        needs ~256 tokens to surface a 1-word answer and takes ~6.5s — unusable per pause. The role's
        model/knobs resolve binding > env (COMPANY_JUDGE_*) > declared default (default_model None → the
        brain, which WORKS but is slow until rebound to a fast no-think model). Verdict parses 'finish'
        anywhere (robust to a little thinking).

        Empty/blank text → trivially not finished (no model call). Returns {finished, verdict, text,
        judge_model}. Brain/transport errors PROPAGATE (FabricError) → fail loud; the circuit's explicit
        fallback is the manual push-to-talk toggle SURFACED to the operator, NEVER a silent degrade to a
        silence timer (the rejected design)."""
        from fabric import client, transport
        t = (text or "").strip()
        if not t:
            return {"finished": False, "verdict": "MORE", "text": t, "note": "empty — nothing to end"}
        import time
        r = self.resolve_role("judge")                        # the role registry resolves model+knobs
        cfg = self.rhm_config()
        sys_p = ("You judge ONLY whether a spoken utterance is a COMPLETE THOUGHT the listener should now "
                 "respond to, or whether the speaker is mid-sentence / mid-ramble and likely to continue. "
                 "Answer with EXACTLY one word: FINISHED or MORE. No punctuation, no explanation.")
        msgs = [{"role": "system", "content": sys_p},
                {"role": "user", "content": f'Utterance so far: "{t}"\nFINISHED or MORE?'}]
        t0 = time.monotonic()
        out = client.complete(
            transport.openai_transport(base_url=r["base_url"], timeout=cfg["timeout"]),
            msgs, model=r["model"], max_tokens=r["knobs"].get("max_tokens", 256),
            temperature=r["knobs"].get("temperature", 0))
        ms = int((time.monotonic() - t0) * 1000)
        verdict = "FINISHED" if "finish" in (out or "").strip().lower() else "MORE"
        # G7 run-record: the judge is on the LIVE turn path — how long it took, on which model, the
        # verdict (the condition that matters for tuning the always-listen feel). Rollups reveal whether
        # the bound judge model is fast enough live (the deepseek-6.5s lesson, measured per use).
        self.emit_run_record("judge", ms, model=r["model"], verdict=verdict)
        return {"finished": verdict == "FINISHED", "verdict": verdict, "text": t,
                "judge_model": r["model"], "ms": ms}

    def chat(self, message: str, graph_id: str, focus: dict | None = None) -> dict:
        """Grounded conversation with the operator via NATIVE TOOL-CALLING. Answers from compact
        ground truth; never confabulates system facts. It ACTS only through the governed verbs offered
        as native function-tools for this mode×context — and the dispatcher's whitelist still REFUSES
        anything off it (E6). The RHM model MUST support native tools: a non-tool model is refused
        FAIL-LOUD (no model call, no fallback, rule 4)."""
        mode = self.get_mode()
        if mode == "off":                                     # the dial disables the RHM entirely
            self.store.append_chat({"role": "user", "text": message, "grade": "gold", "source": "operator"})
            off = "The right-hand-man is off. Switch a mode on the presence dial to wake me."
            self.store.append_chat({"role": "assistant", "text": off, "grade": "working", "source": "twin"})
            self._emit("chat", f"you: {message[:40]} (RHM off)")
            return {"reply": off, "action": None, "mode": mode, "history": self.store.chat_history(40)}
        from fabric import client, transport
        from fabric.client import FabricError
        cfg = self.rhm_config()

        # CAPABILITY-GATE FIRST (before any model call): the RHM acts through NATIVE tools, so the
        # selected model MUST support tool-calling. A non-tool model (e.g. an embedder mis-selected, or
        # a chat model the endpoint reports without "tools") is a CONFIGURATION error — refuse it FAIL
        # LOUD: a legible turn + a warning event, and NO model call and NO fallback (rule 4 — never
        # silently degrade to a non-acting path). _model_supports_tools translates a cannot-determine
        # (endpoint down) into False, so an unreachable endpoint is ALSO a loud refusal, never an
        # assume-capable call.
        if not self._model_supports_tools(cfg["model"], cfg["base_url"]):
            self.store.append_chat({"role": "user", "text": message, "grade": "gold", "source": "operator"})
            refusal = (f"I can't act right now: the selected model '{cfg['model']}' does not report "
                       f"native tool-calling support (or its endpoint is unreachable), and I act ONLY "
                       f"through governed tools — I won't silently fall back to a non-acting path. "
                       f"Select a tool-capable chat model in the RHM config.")
            self.store.append_chat({"role": "assistant", "text": refusal, "grade": "working", "source": "twin"})
            self._emit("warning", f"RHM model '{cfg['model']}' is not tool-capable — refused (no model "
                       f"call, no fallback); select a tool-capable model")
            return {"reply": refusal, "action": None, "mode": mode,
                    "model": cfg["model"], "history": self.store.chat_history(40)}

        persona = cfg["persona"]
        # PERSONA / GROUND-TRUTH / MODE-DIRECTIVE HEAD (the ACTION:-prose block is GONE — the verbs are
        # now offered as native function-tools, so the model invokes them through the tool API, not by
        # emitting a hand-typed `ACTION:` line). The head still tells it WHO it is, to answer only from
        # ground truth, the persona, the model-of-Tim, and the current mode's behavioral directive.
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
            "You can ACT on the system, but ONLY by CALLING one of the governed tools provided to you "
            "(they are the verbs you are permitted in this mode/context). Call a tool ONLY when the "
            "operator actually asks you to act — otherwise just answer in text. Describing an action in "
            "prose does NOTHING; to act you must CALL the tool. You CANNOT apply, delete, or write files "
            "(those are operator-gated and are not offered as tools)."
        )

        # the affordance context for THIS turn → the native tools array (mode-primary, context-refines),
        # built from the ONE registry (same available_verbs the grounding context renders).
        actx = self._affordance_context(graph_id, focus)
        tools = self._rhm_tools(mode, actx)

        msgs = [{"role": "system", "content": sys_p + "\n\n" + self._chat_context(graph_id, focus)}]
        for t in self.store.chat_history(20):
            msgs.append({"role": t["role"], "content": t["text"]})
        msgs.append({"role": "user", "content": message})

        # NATIVE tool-calling: complete_with_tools returns the whole message dict {content, tool_calls}.
        # A tool_call with empty content is SUCCESS (the model chose to act, not to speak) — the fabric
        # guard knows this. A non-tool model never reaches here (gated above). FAIL LOUD on exhaustion:
        # complete_with_tools raises FabricError, which we let propagate (no fallback) after logging the
        # operator turn — the bridge surfaces the error rather than the system pretending success.
        msg = client.complete_with_tools(
            transport.openai_tools_transport(base_url=cfg["base_url"], timeout=cfg["timeout"]),
            msgs, model=cfg["model"], tools=tools, tool_choice="auto", timeout=cfg["timeout"])
        reply = msg.get("content") or ""                      # may be empty (the model called a tool)

        # LOOP over every tool_call the model emitted (a model may call >1). Each becomes an action via
        # the EXISTING _json_obj_to_action (it JSON-decodes the `arguments` string) → the EXISTING
        # _dispatch_rhm_action (the ONE whitelist — a forbidden verb is refused end-to-end, E6 holds).
        # In decide-for-me each call routes per its governance posture via autonomous_dispatch.
        # MODE-DISCIPLINE GATE (defense-in-depth ATOP the whitelist): the affordance set is a REAL gate
        # at dispatch, not merely a hint to the model. A forged/confused tool_call for a verb that is
        # whitelisted but NOT OFFERED in this mode×context (e.g. `build` in watch-and-react) must NOT
        # execute. We re-validate each call against the SAME available_verbs(mode, actx) that built the
        # tools array — so the OFFER and the DISPATCH agree by construction. A not-offered verb is
        # refused here (did=='none', a legible note folded into the reply) and never reaches the
        # dispatcher. This is purely additive: the dispatcher's whitelist still refuses non-RHM_VERBS
        # (E6), the catastrophic apply/delete/file-write wall is untouched, decide-for-me routing is
        # unchanged for OFFERED verbs, and a verb that IS offered dispatches exactly as before.
        offered = set(self.available_verbs(mode, actx))
        outcomes = []
        for tc in (msg.get("tool_calls") or []):
            fn = tc.get("function") or {}
            verb = fn.get("name")
            if not verb:
                continue
            if verb not in offered:
                # not offered in THIS mode → refuse without dispatching (mode-discipline gate). Legible
                # reason; same {did:none, refused} shape _confirmation_for folds into the reply.
                outcomes.append({"did": "none",
                                 "refused": f"{verb} not available in mode {mode}"})
                continue
            action = self._json_obj_to_action({"name": verb, "arguments": fn.get("arguments")}, verb)
            if mode == "decide-for-me":
                # G3 wiring: route the ACT-vs-SURFACE decision DETERMINISTICALLY by the verb's governance
                # action-class (no confidence) through autonomous_dispatch. The verb BODY performs it
                # either way — AUTO verbs run; CONFIRM verbs run their body whose action is to SURFACE a
                # consumable applyable draft. Outcome carries routed_posture for audit.
                cls = self.RHM_VERB_CLASS.get(verb, "register_type")   # unknown verb → safest (CONFIRM)
                outcome = self.autonomous_dispatch(
                    cls, do=lambda a=action: self._dispatch_rhm_action(a, graph_id), payload=action)
            else:
                outcome = self._dispatch_rhm_action(action, graph_id)
            outcomes.append(outcome)

        # ACTION-CONFIRMATION: fold a concise confirmation into `reply` for EVERY dispatched verb so the
        # operator ALWAYS sees what happened — CRITICAL with native tool-calls (the model often emits NO
        # prose, only the call → reply would otherwise be blank). consult/ask keep their richer folds
        # (the full answer / the needs-line); all others get _confirmation_for. A confirmation appends to
        # existing prose, or BECOMES the reply when there is none (handles empty-content + tool_call).
        for outcome in outcomes:
            if outcome and outcome.get("did") == "consult":   # fold the looked-up answer into the turn
                reply = (reply + "\n\n📖 " + outcome["answer"]).strip()
            elif outcome and outcome.get("did") == "ask":     # asked instead of fabricating (PoLR)
                reply = (reply + "\n\n❓ That needs something not in the registry, so I'm asking rather "
                         "than guessing: " + outcome["needs"] + " — surfaced for you in the inbox.").strip()
            else:
                confirm = self._confirmation_for(outcome)
                if confirm:
                    reply = (reply + "\n\n" + confirm).strip() if reply.strip() else confirm

        # the persisted/returned `action`: a LIST of outcomes (a turn may now carry several). Kept
        # backward-compatible for the single-action consumers (bridge/mcp passthrough): None when nothing
        # was dispatched, the single dict when exactly one (the prior shape), the list when several.
        if not outcomes:
            action_field = None
        elif len(outcomes) == 1:
            action_field = outcomes[0]
        else:
            action_field = outcomes
        # provenance grading (B3): Tim's words are gold (train the twin); the twin's are working
        self.store.append_chat({"role": "user", "text": message, "grade": self._provenance_grade("user"), "source": self._provenance_source("user")})
        self.store.append_chat({"role": "assistant", "text": reply, "action": action_field,
                                "grade": self._provenance_grade("assistant"), "source": self._provenance_source("assistant")})
        self._emit("chat", f"you: {message[:48]}")
        return {"reply": reply, "action": action_field, "mode": mode,
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
        out = client.complete(transport.openai_transport(base_url=cfg["base_url"], timeout=cfg["timeout"]),
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

        # 3 + 5 — EXACTLY-ONCE check→claim, ATOMIC under TWO nested locks. The bridge is a
        # ThreadingHTTPServer over one Suite; without a lock two concurrent fires both clear the check
        # before either claims → double-launch. The thread lock (_dispatch_lock) serializes in-PROCESS
        # threads; nested INSIDE it the store's cross-PROCESS graph_lock (keyed dispatch-claim:<seq>,
        # backed by fcntl.flock — the primitive the store lane built) serializes across SEPARATE
        # PROCESSES too (Tim runs multiple sessions). So the check→emit critical section is atomic
        # whether the race is two threads or two processes; the durable decision.dispatch event remains
        # the restart guarantee. Re-entrant, so a nested locked call on the same key won't self-deadlock.
        with self._dispatch_lock(derived_from), self.store.graph_lock(f"dispatch-claim:{derived_from}"):
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
        t = transport.openai_transport(base_url=fcfg.DEFAULT_BASE_URL, timeout=fcfg.DEFAULT_CLOUD_TIMEOUT)
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

    @staticmethod
    def _is_revert_subject(subject: str) -> bool:
        """A `git revert` of a self-apply produces subject `Revert "[self-apply] ..."` — which STILL
        contains `[self-apply]`, so `--grep=[self-apply]` matches the REVERT itself. So an undo is NOT
        a change: distinguish it by subject prefix. (Finding #2: prevents 'revert the revert' — and a
        revert's --invert-grep can't be expressed alongside the positive grep, so we tag in Python.)"""
        return (subject or "").startswith('Revert "[self-apply]')

    def _self_change_changed_files(self, sha: str) -> list[str]:
        """The files a self-apply commit touched — git ground truth (`git show --name-only`), so the
        record surfaces WHICH files it changed (Finding #4; mirrors the wire's `changed_files` manifest
        and the very call selfmod_acceptance asserts at HEAD). Tolerant: an unreadable commit reads as
        no files (a manifest read must never break the audit log it feeds)."""
        import subprocess
        try:
            out = subprocess.run(
                ["git", "-C", self._repo_root, "show", "--name-only", "--format=", sha],
                check=True, capture_output=True, text=True).stdout
        except Exception:
            return []
        return [ln.strip() for ln in out.splitlines() if ln.strip()]

    SELF_APPLY_PREFIX = "[self-apply]"

    def _self_change_records(self, limit: int = 50) -> list[dict]:
        """The shared reader behind the audit log + last_self_change (Finding #1/#2/#4). Reads the
        `[self-apply]` commits newest-first and tags each: {sha, subject, ts (committer ISO date),
        is_revert (Finding #2), changed_files (Finding #4)}. Reverts are INCLUDED but MARKED — the log
        shows the full undo history; `last_self_change` filters them out. Empty list on any git failure
        (a read, not a mutation — degrade to empty, never raise here).

        CLASSIFY BY SUBJECT, not by message body: `--grep` matches the whole message (subject AND
        body), but a genuine self-apply is SUBJECT-prefixed `[self-apply]` (exactly what
        `_git_self_commit` writes), and a revert is subject `Revert "[self-apply] ...`. A plain commit
        whose BODY merely MENTIONS the string (e.g. a feature/doc commit describing self-apply work) is
        NOT a self-change and must NOT pollute the ledger — it would make `last_self_change` point at a
        non-self-apply commit. So `--grep` stays as the cheap coarse net (it never drops a genuine or a
        revert — both contain the string), and we KEEP a record only if its SUBJECT is a genuine
        self-apply OR a revert-of-one; everything else (body-only mention) is dropped. To request more
        than `limit` genuine records, the coarse net is widened (×4 + 20) before the subject filter, so
        body-mentions interleaved in history don't starve the requested count."""
        import subprocess
        n = max(1, int(limit))
        try:
            out = subprocess.run(
                ["git", "-C", self._repo_root, "log", "--grep=[self-apply]", "--fixed-strings",
                 "-n", str(n * 4 + 20), "--format=%H%x00%cI%x00%s"],
                check=True, capture_output=True, text=True).stdout.strip()
        except Exception:
            return []
        records = []
        for line in out.splitlines():
            if not line:
                continue
            sha, _, rest = line.partition("\x00")
            ts, _, subject = rest.partition("\x00")
            is_revert = self._is_revert_subject(subject)
            is_genuine = (subject or "").startswith(self.SELF_APPLY_PREFIX)
            if not (is_genuine or is_revert):       # body-only mention → NOT a self-change, drop it
                continue
            records.append({
                "sha": sha, "subject": subject, "ts": ts,
                "is_revert": is_revert,
                "changed_files": self._self_change_changed_files(sha),
            })
            if len(records) >= n:
                break
        return records

    def self_change_log(self, limit: int = 50) -> list[dict]:
        """The multi-entry self-modification audit ledger (Finding #1): the `[self-apply]` commit
        history newest-first, each entry carrying sha · subject · timestamp · changed_files (Finding
        #4) · is_revert (Finding #2 — a revert is surfaced DISTINCTLY, not hidden and not mistaken for
        a change). Reachable through a real face (`GET /api/self-change-log`). Was: only the single
        latest (last_self_change) existed — no ledger."""
        return self._self_change_records(limit)

    @staticmethod
    def _reverted_target_sha(body: str) -> str | None:
        """The ORIGINAL commit a revert undid — `git revert --no-edit` writes `This reverts commit
        <40-hex-sha>.` in the commit BODY. So the revert names its target unambiguously by full sha
        (subject-matching would be fragile — two changes can share a subject). Returns the full sha, or
        None if the body has no such line. Read from the body, NOT the line-split %s parser of
        _self_change_records (which would corrupt on a multi-line body)."""
        import re
        m = re.search(r"This reverts commit ([0-9a-f]{40})", body or "")
        return m.group(1) if m else None

    def _reverted_shas(self, records: list) -> set:
        """The set of ORIGINAL-change shas that a revert (in `records`) has UNDONE — so a change that
        no longer STANDS (it was reverted) can be skipped. For each revert record, read its body once
        (`git show -s --format=%b`, surgical — NOT through the shared %s parser) and extract the target
        sha. D9: 'still-standing' means not only 'not itself a revert' but also 'not the target of a
        later revert'. Tolerant: an unreadable body contributes no sha (degrade, never raise in a read).
        Minimal-correct: we do NOT model revert-of-revert restoration (a once-reverted change stays
        skipped) — only build that if a test demands it (no gold-plating)."""
        import subprocess
        out = set()
        for rec in records:
            if not rec.get("is_revert"):
                continue
            try:
                body = subprocess.run(
                    ["git", "-C", self._repo_root, "show", "-s", "--format=%b", rec["sha"]],
                    check=True, capture_output=True, text=True).stdout
            except Exception:
                continue
            tgt = self._reverted_target_sha(body)
            if tgt:
                out.add(tgt)
        return out

    def last_self_change(self) -> dict | None:
        """The most recent STILL-STANDING self-applied CHANGE (for one-click rollback + audit). D9:
        a change still STANDS only if (a) it is not itself a revert (Finding #2 — a `git revert` of a
        self-apply still matches `--grep=[self-apply]`, so the naive `-1` returned the revert itself,
        and the UI offered to 'revert the revert'), AND (b) it has not since been UNDONE by a later
        revert. Without (b), `last_self_change` would still point at a change the operator already
        reverted — offering to roll back something that no longer exists in the working tree. So we read
        the tagged log, compute the set of shas reverted by any revert in it, and return the newest
        record that is neither a revert NOR in that reverted set. Keeps the {sha, subject} keys callers/
        the bridge read; ts + changed_files are additive."""
        records = self._self_change_records(50)
        reverted = self._reverted_shas(records)
        for rec in records:
            if not rec["is_revert"] and rec["sha"] not in reverted:
                return rec
        return None

    def revert_self_change(self, sha: str) -> dict:
        """RECOVERY: roll back a self-applied change via git (itself reversible). OPERATOR-only.
        Re-discovers so the capability change reflects immediately. The property that makes
        self-modification acceptable — a bad self-edit is bounded, never bricking.

        Finding #3 — CONFLICT-AWARE: reverting a NON-TIP commit can conflict (e.g. a later commit
        touched the same file). The old `check=True` raised mid-revert, leaving the repo in a dirty,
        half-reverted state. Now: run the revert WITHOUT check, and on a non-zero exit (conflict or
        other failure) `git revert --abort` to leave the repo CLEAN, then raise a LEGIBLE fail-loud
        error naming the sha — never a silent swallow, never a repo left mid-revert."""
        import subprocess
        proc = subprocess.run(["git", "-C", self._repo_root, "revert", "--no-edit", sha],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            # leave the repo CLEAN — abort the half-applied revert (best-effort; a fresh repo with
            # nothing to abort just no-ops). Then fail loud with a legible reason (no silent swallow).
            subprocess.run(["git", "-C", self._repo_root, "revert", "--abort"],
                           capture_output=True, text=True)
            detail = (proc.stderr.strip() or proc.stdout.strip())[:400]
            raise RuntimeError(
                f"revert of self-change {sha[:8]} FAILED (likely a conflict — a later commit touched "
                f"the same files, so this non-tip revert cannot apply cleanly). Aborted the revert; the "
                f"repo is left CLEAN at its prior HEAD (no mid-revert state). git said: {detail}")
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
        raw = client.complete(transport.openai_transport(base_url=fcfg.DEFAULT_BASE_URL, timeout=fcfg.DEFAULT_CLOUD_TIMEOUT),
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
            transport.openai_transport(base_url=fcfg.DEFAULT_BASE_URL, timeout=fcfg.DEFAULT_CLOUD_TIMEOUT),
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
        framed → resolved (with the why) — reconstructed in order. Auditable + replayable.
        Reads the WHOLE event tail (events_since(-1)) and filters on `surfaced`, mirroring
        session_view: an audit must NOT silently truncate (fail-loud). A long-lived decision whose
        lineage spans more than the old 999-event window is now returned WHOLE, not clipped."""
        d = self.inbox.get(sid)
        evs = sorted((e for e in self.store.events_since(-1) if e.get("surfaced") == sid),
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
