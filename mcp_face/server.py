"""mcp_face/server.py — the agent face (C7). FastMCP exposing the generic verbs over the
shared Suite. Same brain + same substrate as the UI bridge (runtime.suite.Suite). See mcp_face/AGENTS.md.

(Dir is `mcp_face`, not `mcp`, to avoid colliding with the installed `mcp` SDK package.)
Verbs are GENERIC over node-type — adding a node-type adds zero tools.
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP          # the SDK (site-packages)
from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from fabric import config as fcfg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUITE = Suite(FsStore(fcfg.STORE_DIR),
              NodeRegistry().discover([os.path.join(ROOT, "nodes")]))

mcp = FastMCP("company")

# --- MODULAR TOOLS (file-discovered — MCP-DESIGN-PRINCIPLE) ---------------------------------------
# Consolidated, parameterised tools live in mcp_face/tools/<resource>.py, each exposing
# register(mcp, suite). Discovered + registered here via pkgutil — mirrors the file-discovered
# registries (roles/·projections/·nodes/): add a resource = add a file, no edit here. Each replaces a
# flat-per-op cluster (the law: a new need is a new `op`, never a new flat tool). Standing law:
# build-prep/cognition-self-improvement/MCP-DESIGN-PRINCIPLE.md.
import importlib as _importlib, pkgutil as _pkgutil
from mcp_face import tools as _tools_pkg
for _m in _pkgutil.iter_modules(_tools_pkg.__path__):
    _importlib.import_module(f"mcp_face.tools.{_m.name}").register(mcp, SUITE)


@mcp.tool()
def list_types() -> list:
    """List every registered node-type (process · content · presentation)."""
    return SUITE.list_types()


@mcp.tool()
def object_info() -> dict:
    """The full node-type library (ports · render-set · config) for rendering/composition."""
    return SUITE.object_info()


@mcp.tool()
def list_by_type(output_type: str) -> list:
    """Type-graph query: which node-types PRODUCE a given port-type."""
    return SUITE.list_by_type(output_type)


@mcp.tool()
def list_graphs() -> list:
    """List all graphs (canvases) in the substrate."""
    return SUITE.list_graphs()


@mcp.tool()
def create_node(graph: str, type: str, config: dict = {}, node_id: str = "") -> str:
    """Add a node of `type` to `graph` (GENERIC — works for any registered type). Returns its id."""
    return SUITE.create_node(graph, type, dict(config), node_id or None)


@mcp.tool()
def connect(graph: str, from_node: str, from_port: str, to_node: str, to_port: str) -> str:
    """Wire from_node.from_port -> to_node.to_port in `graph`."""
    SUITE.connect(graph, from_node, from_port, to_node, to_port)
    return "ok"


@mcp.tool()
def delete_node(graph: str, node: str) -> str:
    """Remove `node` from `graph` along with any edges touching it."""
    SUITE.delete_node(graph, node)
    return "ok"


@mcp.tool()
def set_config(graph: str, node: str, config: dict) -> str:
    """Update a node's config in `graph`."""
    SUITE.set_config(graph, node, dict(config))
    return "ok"


@mcp.tool()
def run_graph(graph: str, branch: str = "main") -> dict:
    """Run `graph`; returns which nodes ran vs were cached (memo)."""
    r = SUITE.run(graph, branch=branch)
    return {"ran": sorted(r["ran"]), "cached": sorted(r["skipped"]), "stuck": r["stuck"]}


@mcp.tool()
def get_state(graph: str) -> dict:
    """Current state of `graph`: nodes, statuses, outputs, addresses."""
    return SUITE.state(graph)


@mcp.tool()
def get_results(graph: str) -> dict:
    """The output of each node in `graph`."""
    return SUITE.results(graph)


# --- self-growth: build-dispatch + the surfaced-decision inbox (D7/D4) ---
@mcp.tool()
def propose_node(name: str, spec: str) -> dict:
    """Build-dispatch: ask the brain to WRITE a new node-type module. Returns {name, code}.
    Proposing is safe; APPLYING is CONFIRM-gated (see apply_node)."""
    return SUITE.propose_node(name, spec)


@mcp.tool()
def apply_node(surfaced_id: str) -> str:
    """Apply a proposed node by its surfaced id — succeeds ONLY if the OPERATOR has approved it
    (resolved=='approve'). The agent cannot self-approve (approval is not on this face)."""
    return SUITE.apply_node(surfaced_id)


@mcp.tool()
def list_surfaced() -> list:
    """Decisions the system surfaced for the operator (each carries a default + resolution)."""
    return SUITE.list_surfaced()


@mcp.tool()
def self_change_log(limit: int = 50) -> list:
    """The self-modification AUDIT LEDGER — the [self-apply] commit history newest-first, each entry
    with sha · subject · timestamp · changed_files (which files it touched) · is_revert (a revert is
    surfaced distinctly, never mistaken for a change). For one-click rollback + audit of the system's
    own self-edits; revert is operator-only (off this face)."""
    return SUITE.self_change_log(limit)


@mcp.tool()
def get_events(limit: int = 60) -> list:
    """The captured trajectory — recent actions (run · create · connect · grow · approve), newest-first."""
    return SUITE.events(limit)


@mcp.tool()
def now(graph: str) -> dict:
    """The now-view + presence snapshot for `graph` — node counts, pending approvals, presence, last event."""
    return SUITE.now(graph)


@mcp.tool()
def chat(message: str, graph: str) -> dict:
    """Converse with the right-hand-man — the coherent voice of the Company about itself. Answers
    from live ground truth; suggests actions but performs none that skip the surfaced gate."""
    return SUITE.chat(message, graph)


@mcp.tool()
def inbox() -> dict:
    """The chief-of-staff inbox triaged into lanes: live escalations, resolved-for-you, batched."""
    return SUITE.inbox_lanes()


@mcp.tool()
def capabilities() -> dict:
    """The source of truth for WHAT EXISTS — real models, node-types, RHM verbs, panels, api verbs.
    Author from these; never invent. If you need something not here, ask the operator (don't fabricate)."""
    return SUITE.capabilities()


# =================================================================================================
# THE COGNITION ENGINE FACE (#53) — the AGENT-face equal of the human FE / `/api/cognition/*` surface.
#
# These tools let an AGENT configure · run · inspect · CREATE cognition roles/chains/runs through the
# MCP, exactly as the operator does through the FE. EVERY tool REUSES the SAME engine the `/api/cognition/*`
# endpoints + the swarm use: the existing `Suite.*` methods (cognition_info/models_for_role/…/preview_turn/
# propose_role/…) OR the `runtime/cognition.py` engine functions (run_role/run_items/run_reduce/
# resolve_address). NO parallel engine, NO re-implementation.
#
# THE FLOOR (C9.2, reframed by #58 — Tim's correction): the propose→surface→operator-approval gate on
# AUTHORING (creating a role/skill/context) was the AI's DEFAULT, not Tim's constraint. So the agent
# CREATES roles/skills/contexts DIRECTLY + LIVE here (`create_role`/`create_skill`/`create_context` →
# the direct Suite methods), no operator approval. What STILL holds: (1) the CORRECTNESS gate — a
# malformed entry is REFUSED fail-loud (validate-in-tempdir), never written; (2) the BUILD-DISPATCH
# floor — NO tool here emits `dispatch_decision` or launches `claude -p` (the wire's autonomous
# repo-mutation stays operator-gated, OFF this face, UNCHANGED). `propose_role`/`edit_role`/`delete_role`
# STAY available (surfacing remains an option). Running a role/chain produces run:// outputs
# (computation, not governance). resolve_surfaced is NOT exposed as a tool here — not exposed on this
# face (operator-only, on /api/resolve). No tool below calls resolve_surfaced/dispatch_decision/launches claude -p.
# =================================================================================================
from runtime import cognition as _cog          # the ONE engine (run_role/run_items/run_reduce/resolve_address)
import time as _time


def _cog_emit(kind: str, payload: dict) -> None:
    """The (kind, payload-dict) emit sink the engine fns expect, adapted onto the Suite's lenient
    telemetry _emit (one event log — reflects-never-owns narration; never a safety claim)."""
    summary = payload.get("summary") or f"{kind} ({payload.get('turn_id', '')})"
    SUITE._emit(kind, summary, **{k: v for k, v in payload.items() if k != "summary"})


# NOTE: the embed-text derivation that used to live HERE (`_embed_text`) MOVED to `Suite._embed_text`
# (runtime/suite.py) when the capture+embed-on-write was hoisted into the shared `Suite.capture_corpus`
# seam (CAPTURE-EMBED ONE-SOURCE). It travels WITH the seam BOTH faces call — move-don't-copy, so the
# bridge's /api/cognition/corpus route gets the SAME embed-text derivation, never a divergent or absent one.


def _resolve_role(role_id_or_fields):
    """Resolve a role from an id (str — looked up in the LIVE registry, registry-is-truth) OR a draft
    field-set (dict — rendered + loaded from a temp module, the SAME authoring path dry_run_role uses).
    Reuse-don't-parallel: no second role notion. Fail loud on an unknown id / unfireable role."""
    from runtime import authoring as _auth
    if isinstance(role_id_or_fields, str):
        rid = _auth._safe_role_id(role_id_or_fields)
        if rid not in SUITE.role_registry:
            raise ValueError(f"unknown role {rid!r} — registered roles: {sorted(SUITE.role_registry)} "
                             f"(see cognition_info()/models_for_role — author from the registry, never invent).")
        return SUITE.role_registry[rid]
    if isinstance(role_id_or_fields, dict):
        rid = _auth._safe_role_id(role_id_or_fields.get("id"))
        source = _auth.render_role_source(role_id_or_fields)
        return _auth.load_role_from_source(rid, source)        # the SAME RoleRegistry discovery (no fork)
    raise TypeError("role must be a registered role id (str) or a draft field-set (dict)")


# --- INSPECT (read-only) -------------------------------------------------------------------------
@mcp.tool()
def cognition_info() -> dict:
    """INSPECT the cognition registries — the agent's 'what can I compose with': the file-discovered
    roles (+ each role's rules/render-hint/facet/op/input_addresses), the declared rules, the
    THOUGHT_SHAPES · ACTIVATION_CONTEXTS · RULE_OPS · DESTINATION_KINDS · the cast-per-mode, and the
    cognition event-contract. REUSES Suite.cognition_info() (the SAME projection /api/cognition_info
    serves — registry-is-truth, generated from the live registries)."""
    return SUITE.cognition_info()


@mcp.tool()
def models_for_role(requires: str = "") -> dict:
    """INSPECT (the MODEL select): the model-ids whose `provides` ⊇ `requires` (comma-separated caps,
    e.g. 'embed' or 'chat'), plus the live providers the swarm binds against. REUSES
    Suite.models_for_role (the /api/cognition/models_for_role path). What models fit a role."""
    return SUITE.models_for_role(requires)


@mcp.tool()
def cognition_inputs() -> dict:
    """INSPECT (the INPUT-WIRING select): the addresses a role/rule can READ — the utterance, the
    roles' run://<turn>/<role> outputs, the context variables. REUSES Suite.available_inputs
    (the /api/cognition/inputs path). What addresses are readable as inputs."""
    return SUITE.available_inputs()


@mcp.tool()
def field_types() -> dict:
    """INSPECT (the OUTPUT-FIELD-TYPE select): the closed output_schema field-type registry
    (str·int·float·bool·list[str]·list[int]). REUSES Suite.field_types (the /api/cognition/field_types
    path). What types a proposed role's output fields may be."""
    return SUITE.field_types()


@mcp.tool()
def list_skills_contexts() -> dict:
    """INSPECT the skill:// + context:// registries — the addressable, file-discovered units a role's
    input can be set to (a skill = reusable instructions, a context = a reusable blob). REUSES
    runtime.cognition.skill_registry()/context_registry() (the SAME registries resolve_address reads via
    skill://<id> / context://<id>). Read-only. Returns {skills:[{id,label,description}], contexts:[…]}.

    CREATE: skills/contexts are now authored DIRECTLY + LIVE via create_skill/create_context (#56/#58 —
    the skill-writing-skill, no operator approval; correctness-gated). This is READ; CREATE is those tools."""
    sk = _cog.skill_registry()
    cx = _cog.context_registry()
    def _rows(reg):
        return [{"id": eid, "label": reg[eid].label, "description": reg[eid].description} for eid in reg]
    return {"skills": _rows(sk), "contexts": _rows(cx)}


@mcp.tool()
def list_runs(op: str = "", run_op: str = "", limit: int = 50) -> dict:
    """DISCOVER past engine runs — the agent-face RUN INDEX (#54 storage-discovery). Lists past
    run_role / run_items / run_reduce runs + their run:// output addresses, NEWEST-FIRST, so an agent can
    feed a discovered output as an INPUT (run_role inputs=/run_items items=, resolved via inspect_address/
    resolve_address) or re-run it — instead of only reading a run whose address it already KNOWS. REUSES
    Suite.list_runs (a READ-TIME projection over the op.run event log — the log IS the index, no parallel
    store). `op` filters to one engine run-op (cognition.run_role|run_items|run_reduce); `run_op` filters by
    the operation (generate|embed|role|rule|cluster). Read-only. Returns {runs:[{address, op, run_op,
    turn_id, role, duration_ms, seq, ts}], total_records}."""
    return SUITE.list_runs(op=(op or None), run_op=(run_op or None), limit=limit)


@mcp.tool()
def find_runs(role: str = "", op: str = "", run_op: str = "", limit: int = 50) -> dict:
    """DISCOVER past engine runs FILTERED by role (and/or op/run_op) — the query face of the run index
    (#54). REUSES Suite.find_runs (thin reuse of list_runs). E.g. find_runs(role='ground') → the past runs
    of the 'ground' role + their run:// addresses. Read-only. Returns the same {runs, total_records} shape."""
    return SUITE.find_runs(role=(role or None), op=(op or None), run_op=(run_op or None), limit=limit)


@mcp.tool()
def inspect_address(address: str, turn_id: str = "") -> dict:
    """INSPECT a RUN OUTPUT (or any addressed content) by address — reads a PAST run's output back.
    REUSES runtime.cognition.resolve_address (the engine's canonical read path): run:// (an upstream
    role/unit output) · cas:// (a content blob) · skill:// (a skill's instructions) · context:// (a
    context blob). A <turn> template materializes against `turn_id`. Fail loud on an unresolvable/
    unknown address (never a silent empty). Read-only."""
    val = _cog.resolve_address(SUITE.store, address, turn_id=(turn_id or None))
    if val is _cog.BARE_NAME:
        raise ValueError(f"inspect_address: {address!r} is a bare name (a ctx key), not an address — "
                         f"pass a run://, cas://, skill:// or context:// address.")
    return {"address": address, "value": val}


# --- CONFIGURE + RUN -----------------------------------------------------------------------------
@mcp.tool()
def run_role(role: str, utterance: str = "", op: str = "generate", model: str = "",
             inputs: dict = {}, max_tokens: int = 256, temperature: float = 0.0,
             ensure: bool = False, ensure_evict: bool = False, policy: str = "") -> dict:
    """CONFIGURE + RUN ONE role (the agent fires a role and gets its validated output).
    REUSES runtime.cognition.run_role (the SAME fire path run_swarm/dry_run_role use — never a parallel
    engine). `role` is a registered role id (or pass a draft field-set is via propose_role first).

      op="generate" (default) → the role's structured-JSON output (validated against its output_schema).
      op="embed"              → a dense vector {vector, dim, model} via the local embedder. **EMBED via
                                MCP (headline):** if the embedder isn't resident, `ensure=True` requests
                                the GATED #50 actuator (capabilities.ensure_resident) to load it;
                                `ensure_evict=True` additionally authorizes largest-first eviction. With
                                ensure=False (default) a down embedder FAILS LOUD (never a silent degrade).

    `inputs` (optional): extra named inputs the role declares (input_addresses). An address-VALUED input
    (run://…, cas://…, skill://…, context://…) is RESOLVED via the engine's resolve_address before the
    run (the input-address intent); a literal value is used as-is. `model` overrides the role's model.

    `policy` (optional, O2): a GENERATION_POLICY id (from the generation_policies registry — see
    available via cognition_inputs / create_generation_policy). When set, run_role reads that regime's
    repetition_penalty LADDER (DATA, NOTHING static): start at the ladder default, escalate on
    finish_reason=length, fail-loud `degenerate-loop` when the ladder exhausts. Default "" → byte-identical
    to before (no ladder). DELEGATE: runtime.cognition.run_role's `policy=` axis.

    GENERATE runs PERSIST: the validated output is written to run://<turn>/<role> (the SAME put_content→
    set_ref primitives run_items uses) so the run can be inspected back by address (inspect_address) and
    fed as an input downstream. Returns {role, op, output, address, turn_id}.

    FLOOR: this produces a run:// output (computation) — it emits NO resolve/approve/dispatch."""
    r = _resolve_role(role)
    return _fire_role_and_persist(
        r, utterance, inputs, model, max_tokens, temperature, ensure, ensure_evict, policy,
        turn_prefix="mcp")


def _fire_role_and_persist(r, utterance: str, inputs: dict, model: str, max_tokens: int,
                           temperature: float, ensure: bool, ensure_evict: bool, policy: str,
                           *, turn_prefix: str) -> dict:
    """The SHARED single-role fire-and-persist tail of run_role / run_draft (REUSE — never copy-paste a
    second wrapper body, so the two stay byte-identical in behaviour). Given an ALREADY-RESOLVED `Role`
    (`_resolve_role` of an id for run_role, of a draft dict for run_draft — the engine path is the same
    `_cog.run_role` either way), it: mints a turn_id, resolves address-valued declared inputs, FIRES the
    role, PERSISTS the output to run://<turn>/<role>, emits ONE op.run index record, and returns the
    agent-facing shape. The draft case differs ONLY in how `r` was built (a tempdir module that is
    rmtree'd — NEVER written to roles/); from here the two are identical. FLOOR: a run:// output
    (computation) — emits NO resolve/approve/dispatch."""
    turn_id = turn_prefix + "-" + _time.strftime("%Y%m%d-%H%M%S") + f"-{int(_time.monotonic()*1000) % 100000}"
    # resolve any address-valued declared inputs through the engine resolver (input-address intent).
    ctx = {"utterance": utterance}
    for name, val in dict(inputs or {}).items():
        if isinstance(val, str) and "://" in val:
            ctx[name] = _cog.resolve_address(SUITE.store, val, turn_id=turn_id)
        else:
            ctx[name] = val
    kw = {"max_tokens": max_tokens, "temperature": temperature, "store": SUITE.store,
          "ensure": ensure, "ensure_evict": ensure_evict}
    if model:
        kw["model"] = model
    if policy:
        kw["policy"] = policy          # O2 — the rep_penalty ladder regime (registry-is-truth)
    # O3 — read the completion's finish_reason (+ usage) back via run_role's `meta` OUT-PARAM (ENGINE-2's
    # flagged hand-off: the value is AVAILABLE at the run_role seam, persisting it into the agent-facing
    # op.run record is THIS MCP wrapper's emit). meta={} = an empty out-dict the transport's _fill_meta
    # populates; the run_role RETURN shape (model_dump()) is UNCHANGED — finish_reason never folds into it.
    # An EMBED op or any path that doesn't fill meta leaves it {} → finish_reason stays None (honest absent,
    # never fabricated).
    meta: dict = {}
    _t0 = _time.monotonic()
    out = _cog.run_role(r, ctx, meta=meta, **kw)
    _ms = int((_time.monotonic() - _t0) * 1000)
    # PERSIST the output to run://<turn>/<role> so it is inspectable/feedable (reuse the store primitives).
    address = f"run://{turn_id}/{r.id}"
    cas = SUITE.store.put_content(out)
    SUITE.store.set_ref(address, cas)
    # #54 STORAGE-DISCOVERY — the op.run RUN INDEX. Engine run_role has NO emit + does NOT persist (the
    # CALLER assigns the run:// address — and it's reused INTERNALLY per-cast-role by run_swarm / per-draw
    # by run_jury / by chat_parts), so the op.run emit lives HERE, colocated with the discoverable persist —
    # exactly one record per agent-facing run, NEVER flooding the index with internal cast/draw fires.
    # Reuses Suite.emit_run_record (the introspective-data op.run path; run_stats rolls duration_ms up).
    # Additive + behaviour-preserving (the output persists to run:// exactly as before); a run record
    # NARRATES backend truth — NO resolve/approve/dispatch (the operator-only floor).
    # O3 — finish_reason (+ usage if present) ride ONTO the op.run record (introspective-data-building: the
    # run self-instruments — so find_runs surfaces WHY a run stopped: 'stop' vs 'length' vs tool-call).
    _conds = dict(run_op=getattr(r, "op", "generate"), turn_id=turn_id,
                  role=r.id, addresses=[address])
    if meta.get("finish_reason") is not None:
        _conds["finish_reason"] = meta["finish_reason"]
    if meta.get("usage") is not None:
        _conds["usage"] = meta["usage"]
    SUITE.emit_run_record("cognition.run_role", _ms, **_conds)
    return {"role": r.id, "op": getattr(r, "op", "generate"), "output": out,
            "address": address, "turn_id": turn_id,
            "finish_reason": meta.get("finish_reason")}


@mcp.tool()
def run_draft(draft_role: dict, utterance: str = "", model: str = "",
              inputs: dict = {}, max_tokens: int = 256, temperature: float = 0.0,
              ensure: bool = False, ensure_evict: bool = False, policy: str = "") -> dict:
    """CONFIGURE + RUN a ONE-OFF DRAFT role (the G1 ephemeral-run path) — fire an INLINE role spec ONCE
    over a single utterance WITHOUT registering or committing it. The motivating gap (SYSTEM-GAPS G1): a
    bounded one-off classify/extract forces `create_role` (which COMMITS a throwaway role → registry
    pollution + a `.git/index.lock` race) or dropping below the MCP. `run_draft` closes it.

    `draft_role` is a DRAFT FIELD-SPEC (a dict, the SAME shape `create_role`/`propose_role`/`dry_run_role`
    consume — NOT a registered id): `{id (plain lower identifier), prompt_template, output_fields:
    [{name, type, description?}], op?, input_addresses?, requires?, ...}`. It is rendered → loaded from a
    TEMP module → discovered (the SAME RoleRegistry the live roles use, via `_resolve_role`'s dict branch
    → `authoring.load_role_from_source`, which `shutil.rmtree`s the tempdir in a `finally`). **The draft
    role is NEVER written to roles/ and NEVER committed** — a malformed spec FAILS LOUD (the correctness
    gate) before any fire.

    Everything else is byte-identical to `run_role` (REUSES `_fire_role_and_persist` — the SAME engine
    path `_cog.run_role`, the SAME persist to run://<turn>/<role>, the SAME op.run index record). The
    output is inspectable/feedable downstream by address. Returns {role, op, output, address, turn_id,
    finish_reason}.

    FLOOR: this is a run:// output (COMPUTATION, not authoring-apply) — it emits NO resolve/approve/
    dispatch and writes/commits NO role file. The single-fire analogue of run_draft_items (the MAP)."""
    r = _resolve_role(draft_role)        # the dict branch: render → tempdir-load → discover → (rmtree); no commit
    return _fire_role_and_persist(
        r, utterance, inputs, model, max_tokens, temperature, ensure, ensure_evict, policy,
        turn_prefix="mcp-draft")


@mcp.tool()
def run_items(role: str, items: list, max_tokens: int = 256, temperature: float = 0.0) -> dict:
    """CONFIGURE + RUN the MAP — fan ONE role over N input-UNITS (1 role × N units). REUSES
    runtime.cognition.run_items (the axis-inversion engine — never a parallel fan). Each unit is either
    a LITERAL value OR an ADDRESS (run://…, cas://… — resolved via resolve_address). Outputs land at
    run://<turn>/<role>/<i> (inspectable/feedable). Returns {role, turn_id, n_units, addresses, resolved,
    finish_order, skipped, wall_s}. A DRIVER: emits NO resolve/approve/dispatch (the floor)."""
    r = _resolve_role(role)
    return _run_items_and_shape(r, items, max_tokens, temperature, turn_prefix="mcp-items")


def _run_items_and_shape(r, items: list, max_tokens: int, temperature: float,
                         *, turn_prefix: str) -> dict:
    """The SHARED MAP fan-and-shape tail of run_items / run_draft_items (REUSE — one fan body, so the
    registered-id and draft-spec paths stay byte-identical). Given an ALREADY-RESOLVED fireable `Role`
    (`_resolve_role` of an id for run_items, of a draft dict for run_draft_items), it fans the role over
    the N units via `_cog.run_items` (the axis-inversion engine — never a parallel fan) and returns the
    agent-facing ItemsResult shape. FLOOR: a DRIVER — emits NO resolve/approve/dispatch."""
    turn_id = turn_prefix + "-" + _time.strftime("%Y%m%d-%H%M%S") + f"-{int(_time.monotonic()*1000) % 100000}"
    res = _cog.run_items(r, list(items), SUITE.store, turn_id=turn_id, emit=_cog_emit,
                         max_tokens=max_tokens, temperature=temperature)
    return {"role": r.id, "turn_id": turn_id, "n_units": len(items),
            "addresses": res.addresses, "resolved": res.resolved,
            "finish_order": res.finish_order, "skipped": res.skipped, "wall_s": res.wall_s}


@mcp.tool()
def run_draft_items(draft_role: dict, items: list, max_tokens: int = 256,
                    temperature: float = 0.0) -> dict:
    """CONFIGURE + RUN the DRAFT MAP (the G1 ephemeral-fan path + ⑪ grunt-offload's missing primitive) —
    fan a ONE-OFF INLINE role spec over N input-UNITS WITHOUT registering or committing the role. This is
    THE primitive a bounded one-off classify needs: "classify these 39 candidates once" → one
    `run_draft_items` call, NOT a `create_role` that pollutes the registry (+ a `.git/index.lock` race).

    `draft_role` is a DRAFT FIELD-SPEC (a dict, the SAME shape `create_role`/`dry_run_role` consume — NOT
    a registered id): `{id, prompt_template, output_fields:[{name, type, description?}], op?,
    input_addresses?, requires?, ...}`. It is rendered → loaded from a TEMP module → discovered (the SAME
    RoleRegistry the live roles use, via `_resolve_role`'s dict branch → `authoring.load_role_from_source`,
    which `shutil.rmtree`s the tempdir in a `finally`). **The draft role is NEVER written to roles/ and
    NEVER committed** — a malformed spec FAILS LOUD (the correctness gate) before any fire.

    `items` = the N input-units (each a LITERAL value OR an ADDRESS run://…/cas://… resolved via
    resolve_address) — identical to `run_items`. REUSES `_cog.run_items` (the axis-inversion engine) +
    `_run_items_and_shape` (the SAME fan body run_items uses). Outputs land at run://<turn>/<role>/<i>
    (inspectable/feedable). Returns {role, turn_id, n_units, addresses, resolved, finish_order, skipped,
    wall_s}.

    FLOOR: a DRIVER — this is run:// COMPUTATION (not an authoring-apply): it emits NO resolve/approve/
    dispatch and writes/commits NO role file. The N-unit MAP analogue of run_draft."""
    r = _resolve_role(draft_role)        # the dict branch: render → tempdir-load → discover → (rmtree); no commit
    return _run_items_and_shape(r, items, max_tokens, temperature, turn_prefix="mcp-draft-items")


# the closed, NAMED reduce-rule registry (registry-is-truth): a deterministic L2 join the agent selects
# BY NAME over the MCP/JSON boundary (a Python callable cannot cross MCP). Each is a PURE function over
# the N read-back values. An unknown name FAILS LOUD (never a fabricated rule). This is the rule-mode
# analogue of the role/cluster modes — additive; add a named rule here when a new deterministic join is needed.
#
# SINGLE SOURCE (G11 unification): the named reduce-rules live ONCE in the engine —
# runtime/cognition.py:REDUCE_RULES — and BOTH faces reference it (here for the run_reduce MCP tool;
# runtime/suite.py's run_cascade caller passes the SAME cognition.REDUCE_RULES). So a rule added in the
# engine is visible to run_reduce AND run_cascade — the parallel-literal built-twice (this dict vs suite's
# old _CASCADE_REDUCE_RULES, which had drifted: missing verdict-tally + a different concat) is GONE.
# The names still DERIVE from `sorted(_REDUCE_RULES)` (reduce_rule_names + the run_reduce description + the
# fail-loud error) — no second list. Serving the names at /api is the BRIDGE lane (flagged).
_REDUCE_RULES = _cog.REDUCE_RULES


@mcp.tool()
def run_reduce(addresses: list, mode: str, role: str = "", reduce_rule: str = "",
               cluster_threshold: float = 0.85, max_tokens: int = 512) -> dict:
    """CONFIGURE + RUN the cross-unit JOIN — REDUCE a set of map-output run:// addresses into ONE output.
    REUSES runtime.cognition.run_reduce (the net-new JOIN engine — never a parallel reducer).

      mode="role"    → synthesize join (op=generate). Pass `role` = a reduce-role id (e.g. 'reduce_synth').
      mode="rule"    → deterministic L2 join (no model). Pass `reduce_rule` = a NAMED built-in. The
                       available names are listed by `reduce_rule_names()` (and in the fail-loud error on
                       an unknown name) — both DERIVE from the single-source _REDUCE_RULES dict (no
                       hardcoded second list). A callable can't cross MCP, so select by name.
      mode="cluster" → embed-cluster join (the 'which of these are the same' discovery primitive) — needs
                       the local embedder resident.

    Returns {turn_id, mode, joined, inputs, skipped, wall_s, detail}. A DRIVER: the model runs only in a
    reduce-role; rule/cluster are pure L2. Emits NO resolve/approve/dispatch (the floor)."""
    turn_id = "mcp-reduce-" + _time.strftime("%Y%m%d-%H%M%S") + f"-{int(_time.monotonic()*1000) % 100000}"
    kw = {"turn_id": turn_id, "mode": mode, "emit": _cog_emit, "max_tokens": max_tokens,
          "cluster_threshold": cluster_threshold}
    if mode == "role":
        if not role:
            raise ValueError("run_reduce(mode='role'): pass a reduce-role id (e.g. 'reduce_synth').")
        kw["role"] = _resolve_role(role)
    elif mode == "rule":
        rule = _cog.resolve_reduce_rule(reduce_rule)        # single-source: static + tally-by:<field> (M1)
        if rule is None:
            raise ValueError(f"run_reduce(mode='rule'): unknown reduce_rule {reduce_rule!r} — named "
                             f"built-ins are {sorted(_REDUCE_RULES)}, plus the PARAMETERISED "
                             f"'tally-by:<field>' (group-by-count over <field>, e.g. 'tally-by:label'). "
                             f"Fail loud, never a fabricated rule.")
        kw["reduce_rule"] = rule
    res = _cog.run_reduce(list(addresses), SUITE.store, **kw)
    return {"turn_id": turn_id, "mode": mode, "joined": res.joined, "inputs": res.inputs,
            "skipped": res.skipped, "wall_s": res.wall_s, "detail": res.detail}


@mcp.tool()
def reduce_rule_names() -> dict:
    """INSPECT the named deterministic reduce-rules `run_reduce(mode='rule')` accepts — PROJECTED from the
    single-source _REDUCE_RULES dict (the B-fix: derive, never a hardcoded second list; PART 4.4). A
    reduce-rule is a PURE function over the N read-back values, selected BY NAME over the MCP boundary (a
    callable can't cross MCP). Read-only. Returns {names:[…], parameterised:[…]} — `names` are the static
    rules (adding one is a row in _REDUCE_RULES, appears here with no other edit); `parameterised` are the
    name:arg patterns (tally-by:<field> = group-by-count over <field>, e.g. 'tally-by:label')."""
    return {"names": sorted(_REDUCE_RULES),
            "parameterised": ["tally-by:<field> — group-by-count over <field> (e.g. 'tally-by:label' → {counts:{value:n}})"]}


# --- SAVED CASCADES (GROUP N · save a proven pipeline → re-run it; AK4 frozen recipes) ----------------
@mcp.tool()
def save_cascade(decl: dict) -> dict:
    """SAVE a proven multi-step pipeline as a re-runnable CASCADE (GROUP N · N1 · AK4 — a frozen recipe an
    agent reuses without re-deriving). A cascade = a declared chain validated through the EXISTING one door
    (coherence_actions.build_action — REUSED, NOT a 2nd validator) + persisted (survives reload). REUSES
    Suite.save_cascade.

    `decl` = {name(str), steps:[{...}], output_schema?(dict)}. EACH STEP:
      · op        — the OPERATION (REQUIRED, validated): generate|embed|reduce (+similarity/retrieve/detect,
                    which have no engine primitive yet → out-of-lane, flagged needs-tim/N2).
      · role      — the role id to fire (REQUIRED at run time; resolved from the live role registry).
      · model     — OPTIONAL per-step model. MUST be a member of the LIVE model registry (chat ∪ embed) or
                    build_action FAILS LOUD (registry-is-truth, no hardcoded literal). OMIT it → the
                    resident default brain (recommended; NO cloud router here — N2, needs-tim).
      · kind      — OPTIONAL primitive selector: role(run_role · 1→1) | items(run_items · MAP 1→N) |
                    reduce(run_reduce · JOIN N→1). DEFAULT: op=reduce→reduce; a `fan:true`/`items:[…]` step
                    →items; else role.
      · reduce_mode/reduce_rule/cluster_threshold — for a reduce step (mode role|rule|cluster; rule selects
                    a NAMED reduce-rule via reduce_rule_names()).

    THE SEAM (output→input): step 0 reads run_cascade(inputs); step N reads step N-1's output address(es).
    A `role` step consumes ONE value, `items` a LIST, `reduce` a LIST→ONE (the runner persists the reduce's
    joined output to a run:// address so it is feedable+discoverable). Returns build_action's shape
    {ok, action} or {ok:False, error} — fail-loud, NEVER written on an invalid decl. THE FLOOR: a cascade
    is run:// computation — running it emits NO resolve/approve/dispatch, launches NO claude -p."""
    return SUITE.save_cascade(dict(decl))


@mcp.tool()
def list_cascades() -> dict:
    """LIST the saved cascades (the discoverable re-runnable pipelines — AK4 · registry-is-truth). Each row
    is the full decl (name·steps·output_schema) so an agent reads the steps/ops/models BEFORE run_cascade.
    REUSES Suite.list_cascades. Read-only. Returns {cascades:[…]}."""
    return {"cascades": SUITE.list_cascades()}


@mcp.tool()
def run_cascade(name: str, inputs=None, max_tokens: int = 256) -> dict:
    """RUN a saved cascade END-TO-END (GROUP N · N3 — the largest net-new). Loads the saved decl (fail-loud
    if unknown — never a fabricated cascade), then fires the GROUP-N runner (cognition.run_cascade) which
    rides the EXISTING engine primitives (run_role/run_items/run_reduce — NO 2nd engine): each step's output
    threads → the next step's input via the run:// resolver, each step is PERSISTED + op.run-INDEXED (so
    find_runs/list_runs see every step), the final addressed output is returned. REUSES Suite.run_cascade.

    `name`   — a saved cascade name (see list_cascades / save_cascade).
    `inputs` — the FIRST step's argument. A run://·cas:// address is RESOLVED via the engine resolver; a
               literal is used as-is; None → the role's default framing. A missing/unresolvable step input
               FAILS LOUD (the engine raises — no silent skip).

    Returns {action, turn_id, steps:[{step, role, kind, op, addresses, address?}…], final_address,
    final_output, final_addresses}. THE FLOOR: run:// computation only — NO resolve/approve/dispatch, NO
    claude -p (a cascade step is a role-run, never a code-build)."""
    return SUITE.run_cascade(name, inputs, max_tokens=max_tokens)


@mcp.tool()
def preview_turn(utterance: str, mode: str = "") -> dict:
    """RUN a full STAGED turn (the cast fires, the declared rules route) — non-mutating (no chat history
    appended). REUSES Suite.preview_turn (the /api/cognition/preview_turn path — the SAME chat_parts
    staged-turn engine). Returns {utterance, mode, parts[], cognition_events[], n_parts}."""
    return SUITE.preview_turn(utterance, mode or None)


# --- CREATE (#58 DIRECT — the agent authors LIVE, no operator approval; correctness gate + build-dispatch floor kept) ---
@mcp.tool()
def create_role(spec: dict) -> dict:
    """CREATE a NEW role DIRECTLY — applies LIVE, NO operator approval (#58: authoring is the agent's,
    not gated). Renders the role module from the FULL schema, runs the CORRECTNESS gate (import in a
    temp dir — a malformed spec is REFUSED fail-loud, never written), writes + git-commits (revertible),
    re-discovers → the role is LIVE in cognition_info immediately. REUSES Suite.create_role (apply_role's
    render+gate+write path MINUS the approval check — never a parallel author path).

    `spec` exposes EVERY role field the agent can set: id · label · description · prompt_template ·
    output_fields ([{name,type,description}] → the structured output BaseModel) · op (generate|embed) ·
    thinking · tools · knobs (max_tokens/temperature/…) · model_binding/requires · input_addresses
    (incl skill://context://run://cas://) · mode_scope · rules · context · render_hint.

    Returns {role_id, path, live: True, source}. The build-dispatch floor is UNTOUCHED — this writes a
    roles/ file (authoring), it NEVER dispatches claude -p. (propose_role stays available for surfacing.)"""
    return SUITE.create_role(spec, model=spec.get("model"))


@mcp.tool()
def create_skill(spec: dict) -> dict:
    """CREATE a NEW skill DIRECTLY — applies LIVE, NO operator approval (#56 write-half, #58 direct: the
    skill-writing-skill). Renders `skills/<id>.py` (id + content + label/description), runs the
    CORRECTNESS gate, writes + git-commits, → LIVE (readable via skill://<id> + list_skills_contexts).
    REUSES Suite.create_skill. Returns {skill_id, path, live: True}."""
    return SUITE.create_skill(spec)


@mcp.tool()
def create_context(spec: dict) -> dict:
    """CREATE a NEW context DIRECTLY — applies LIVE, NO operator approval (#56 write-half, #58 direct).
    Renders `contexts/<id>.py` (id + content + label/description), runs the CORRECTNESS gate, writes +
    git-commits, → LIVE (readable via context://<id> + list_skills_contexts). REUSES Suite.create_context.
    Returns {context_id, path, live: True}."""
    return SUITE.create_context(spec)


# --- CREATE (PROPOSE — surfacing STAYS available for when an operator wants it; not the default path) ---
@mcp.tool()
def propose_role(spec: dict) -> dict:
    """CREATE a NEW role — PROPOSE (surfacing path, kept available alongside the direct create_role):
    renders + GATES the role module, then SURFACES it for the OPERATOR to approve (it is NOT applied
    here). REUSES Suite.propose_role (the /api/cognition/role/propose path). `spec` carries id +
    output_fields + prompt_template (or a natural-language `brief` the brain drafts from). Returns
    {id (surfaced id), role_id, source}. Use create_role for the direct, no-approval path (#58)."""
    return SUITE.propose_role(spec, model=spec.get("model"))


@mcp.tool()
def edit_role(role_id: str, spec: dict) -> dict:
    """CREATE/edit — re-PROPOSE an existing role (renders a replacement + SURFACES it for the operator).
    REUSES Suite.edit_role (the /api/cognition/role/edit path). PROTECTED roles refuse. Surfaces;
    never self-applies."""
    return SUITE.edit_role(role_id, spec, model=spec.get("model"))


@mcp.tool()
def delete_role(role_id: str) -> dict:
    """CREATE/remove — request a role's removal: SURFACES for the operator to approve. REUSES
    Suite.delete_role (the /api/cognition/role/delete path). PROTECTED roles refuse. Surfaces;
    never self-applies."""
    return SUITE.delete_role(role_id)


@mcp.tool()
def validate_rule(ast: dict, destination: str = "") -> dict:
    """INSPECT/validate a rule AST against the closed grammar (RULE_OPS) + the destination check.
    REUSES Suite.validate_rule (the /api/cognition/rule/validate path). Read-only — pure validation."""
    return SUITE.validate_rule(ast, destination=destination or None)


@mcp.tool()
def dry_run_rule(ast: dict, sample_resolved: dict = {}, destination: str = "inject",
                 params: dict = {}, on_missing: str = "raise") -> dict:
    """RUN a rule's routing DECISION over sample resolved values (no effect). REUSES Suite.dry_run_rule
    (the /api/cognition/rule/dry_run path). Read-only — the routing decision, never the effect."""
    return SUITE.dry_run_rule(ast, dict(sample_resolved), destination=destination,
                              params=(dict(params) or None), on_missing=on_missing)


@mcp.tool()
def attach_rule(role_id: str, rule: dict) -> dict:
    """CREATE — attach a declared rule onto a role: SURFACES for the operator (a constrained edit_role).
    REUSES Suite.attach_rule (the /api/cognition/rule/attach path). Surfaces; never self-applies."""
    return SUITE.attach_rule(role_id, rule)


# NOTE (the floor, reframed by #58): AUTHORING (create_role/create_skill/create_context) applies
# DIRECTLY here — Tim's call: the create-approval gate was the AI's default, not his constraint. What
# stays operator-only is the WIRE's autonomous repo-mutation: NO MCP tool emits dispatch_decision or
# launches `claude -p` (the build-dispatch floor), and resolve_surfaced (the build-dispatch trigger via
# an operator approve) stays OFF this face (on /api/resolve, operator-only). So an agent can author a
# role/skill/context, but it can NEVER trigger an autonomous code-build of the repo. The CORRECTNESS
# gate (validate-in-tempdir, fail-loud on malformed) is kept on every create — a bad entry never writes.


# =================================================================================================
# COGNITION ENGINE — THE CORPUS / DISCOVERY PILLAR (agent face · GROUP B/D · PART 3.6)
# -------------------------------------------------------------------------------------------------
# The 3-LAYER PIPELINE an agent drives over a corpus, every tool a THIN wrapper over the SAME engine
# the SUITE/ENGINE lanes built (reuse-don't-parallel — NO parallel engine):
#
#   LAYER 1 · CAPTURE  — `capture(role, units, project, session, round)` : fan ONE role over N corpus
#                        units (REUSE run_items, the axis-inversion engine) → write each per-unit output
#                        as a DURABLE corpus RECORD (REUSE Suite.write_corpus_record → runtime/corpus.py).
#                        The records are the place the engine's at-scale output LIVES + is reused (D1).
#   LAYER 2 · EMBED    — per-projection vectors are written by the ENGINE/BRIDGE capture+embed pass (not
#                        a tool here); the corpus records produced by LAYER 1 are what gets embedded.
#   LAYER 3 · RELATE / — `find_relations(item, near_space, far_space)` : the INVERSION-FINDER (REUSE
#             MARK       Suite.find_relations over the space-keyed vector index — same principle, different
#                        subject); `findings_for(address)` : read the marks/gold-profile a mark-pass left
#                        (REUSE the coherence finding store).
#
# READ-BACK the pillar: `list_corpus`/`find_corpus`/`read_corpus_record` project the corpus-record event
# log (REUSE the Suite corpus methods); `cognition_info().projections`/`.spaces` is the lens/space surface.
#
# THE FLOOR (C9.2): every tool below is a READ or a corpus.record-telemetry / put_content-store write —
# NONE emits resolve/approve/dispatch and NONE launches `claude -p`. `create_projection` is a DECLARATIVE
# create (a `projections/<id>.py` lens DATA file) → DIRECT, like create_role/create_skill (#58: authoring
# is the agent's, correctness-gated). NODE-TYPE / executable-code create stays GATED (off this face).
# NOT here yet (no dead tools): `run_cascade` (the cascade-RUNNER is unbuilt — PART 4.1, NET-NEW ENGINE
# lane); `mark` (marks-generalization is a later STORE pass — `findings_for` only READS the store, safe);
# `create_mark_type`/`create_lifter`/… (those registries are later NEWMOD passes). See the lane report.
# =================================================================================================

@mcp.tool()
def capture(role: str, units: list, project: str, session: str, round: str = "1",
            projection: str = "", record_kind: str = "capture",
            max_tokens: int = 512, temperature: float = 0.0) -> dict:
    """LAYER 1 of the corpus pipeline — CAPTURE: fan ONE describe-role over N corpus UNITS and PERSIST
    each per-unit output as a durable, addressed, queryable corpus RECORD. This is the place the engine's
    at-scale output LIVES (D1 — the scale test produced at scale then DISCARDED the output for want of a
    sink; this is that sink).

    MECHANISM (reuse-don't-parallel — NO parallel fan, NO parallel record gate):
      • REUSES runtime.cognition.run_items (the axis-inversion engine, 1 role × N units) to fan `role`
        over `units`. Each unit is a LITERAL value OR an ADDRESS (run://… cas://… — resolved by the
        engine's resolver). Per-unit OK outputs land at run://<turn>/<role>/<i> and are read BACK.
      • REUSES Suite.write_corpus_record (→ runtime/corpus.py) to persist ONE record per OK unit:
        durable cas:// content + a deterministic run://corpus/<project>/<unit>[/<projection>] pointer +
        a `corpus.record` index event. The source_address is the unit itself (a corpus address; a
        non-string literal unit is repr'd so it still has a retrieval key).

    LINEAGE IS A REQUIRED GATE (PART 4.7 — fail-loud, never defaulted): `project` · `session` · `round`
    are REQUIRED and ride INTO every record. A record without all three is UNCORROBORATABLE cross-session
    (M3 corroboration is cross-SESSION) and unplaceable by the inversion-finder (L2) — so it is REFUSED at
    write (CorpusError). Supply them; this is not optional metadata.

    `role` is a registered describe-role id (see cognition_info().roles) OR a draft field-set (dict path
    via _resolve_role). The capture-schema-FROM-projections builder (output_schema = the model
    projections) is the SUITE/ENGINE lane's concern; this tool writes ONE record per unit of whatever the
    role outputs. To tag a record to a specific lens, pass `projection` (a lens id — see
    cognition_info().projections); absent → one un-projected record per unit.

    POPULATES THE QUERYABLE SPACE (CAPTURE-EMBED ONE-SOURCE): the write+embed-on-write is HOISTED into the
    SHARED Suite.capture_corpus — the ONE seam this tool AND the bridge `/api/cognition/corpus` route both
    call (one source, NOT a duplicated bridge embed path). When `projection` names an EMBEDDABLE lens
    (embeds==True → a vector space), capture_corpus embeds the captured outputs into that space AFTER the
    lineage-gated records are written (the sequencing gate: lineage rides IN the record before the first
    embed). So a real capture run AUTO-POPULATES the space find_relations reads. A NON-embeddable projection
    FAILS LOUD (you asked for a space you can't have — no silent capture-only); NO projection → capture-only
    (records written, embedded=None, no error). A DOWN embedder → the sanctioned LOUD degrade-with-warning
    (degraded=True, no vectors, no crash); re-run when up populates the space. THIS tool owns only the FAN
    (run_items over units); capture_corpus owns the write+embed both faces share.

    Returns {project, session, round, role, turn_id, n_units, captured:[{i, source_address, address, cas,
    seq, projection}], embedded, skipped, failed, wall_s}. `captured` are the persisted records (inspect via
    read_corpus_record/inspect_address; feed downstream via list_corpus/find_corpus). `embedded` is the
    per-space embed result {spaces, records, degraded} when the projection is embeddable, else None.
    `skipped`/`failed` carry units that did not produce a record (F2 per-unit resilience — a poison unit
    never silently vanishes).

    DELEGATE: run_items (cognition.py — the FAN) + Suite.capture_corpus (the shared write+embed seam →
    corpus.py + store/vector_index.build_index). FLOOR: a corpus.record telemetry write + a store put_vector
    WRITE — emits NO resolve/approve/dispatch."""
    r = _resolve_role(role)
    units = list(units)
    turn_id = "mcp-capture-" + _time.strftime("%Y%m%d-%H%M%S") + f"-{int(_time.monotonic()*1000) % 100000}"
    res = _cog.run_items(r, units, SUITE.store, turn_id=turn_id, emit=_cog_emit,
                         max_tokens=max_tokens, temperature=temperature)
    # CAPTURE-EMBED ONE-SOURCE (this lane): the FAN (run_items above) is the MCP face's own concern — but the
    # write+embed-on-write is HOISTED into the shared Suite.capture_corpus, the ONE seam this tool AND the
    # bridge's POST /api/cognition/corpus route both call (neither silently no-ops; both populate the space
    # identically). This tool builds the per-unit records (source_address + the OK output + the lens) and
    # hands them off; capture_corpus owns the lineage-gated write_corpus_record loop, the _embed_text
    # derivation, and the embed_corpus_to_spaces populate (registry-is-truth embeddable decision + fail-loud
    # on a non-embeddable projection). NO duplicated embed path here anymore (the run-glue-mirror anti-pattern
    # SUITE-3 flagged is exactly what this closes).
    proj = projection or None
    capture_records = []
    for i, output in sorted(res.resolved.items()):
        unit = units[i]
        # The source-address retrieval key: a string unit IS its address; a literal is repr'd so it still
        # has a stable key (the record's source_address is required + a string — corpus.py gate).
        source_address = unit if isinstance(unit, str) else repr(unit)
        capture_records.append({"source_address": source_address, "output": output, "kind": record_kind,
                                "projection": proj, "model": getattr(r, "model", None)})
    out = SUITE.capture_corpus(capture_records, project=project, session=session, round=round)
    # capture_corpus returns {captured, embedded, n_records}; the i-key on each captured row is the index
    # within capture_records, which (sorted by run-item index) preserves the per-unit mapping. Carry the
    # tool's own run-shape fields (turn_id/n_units/skipped/failed/wall_s) — the FAN telemetry capture_corpus
    # does not own (it is face-agnostic write+embed; the fan is the MCP face's).
    return {"project": project, "session": session, "round": round, "role": r.id, "turn_id": turn_id,
            "n_units": len(units), "captured": out["captured"], "embedded": out["embedded"],
            "skipped": res.skipped, "failed": res.failed, "wall_s": res.wall_s}


# --- READ-BACK the corpus → CONSOLIDATED into mcp_face/tools/corpus.py (MCP-DESIGN-PRINCIPLE) -----
# list_corpus · find_corpus · read_corpus_record + the previously-unexposed query() are now ONE
# parameterised tool: corpus(op=list|find|read|query, detail=concise|detailed, limit=...). The flat
# trio is removed (a new need = a new `op`, never a new flat tool). See mcp_face/tools/corpus.py.


# --- LAYER 3: the inversion-finder + the marks/gold read ------------------------------------------
@mcp.tool()
def find_relations(item: str, near_space: str, far_space: str, k: int = 10, min_score: float = 0.5) -> dict:
    """LAYER 3 — THE INVERSION-FINDER: the cross-space relation query "same principle, different subject."
    Over the SPACE-KEYED persisted vector index, returns the items NEAR `item` in `near_space` but NOT
    near it in `far_space` (a near∩¬far set difference) — e.g. units sharing a PRINCIPLE
    (near_space='principles') yet diverging in TOPIC (far_space='topics'), the inversion the discovery
    loop surfaces. The space ids are the EMBEDDABLE projections — see cognition_info().spaces (the live
    set; never invent one). REUSES Suite.find_relations (no cosine reimplemented — the k-NN is
    query_index, the threshold turns 'ranked' into 'is-a-neighbour').

    `min_score` (default 0.5): a NEIGHBOUR is an item whose cosine ≥ this (query_index ranks EVERY indexed
    item incl. score≈0, so mere presence in the far ranked list ≠ a far-neighbour — without the threshold
    far would contain everything and the difference would always be empty). A per-projection cluster
    threshold becomes registry-projected once the relation/generation-policy registries land; a tunable
    PARAM until then. `k` caps the per-space k-NN.

    FAIL LOUD: if `item` has no persisted vector in EITHER named space, this RAISES (the inversion is
    undefined without both anchors — never a silent empty that reads as 'no relations'). The vectors come
    from the capture+embed pass (the embedder must have been up at build) — a missing anchor means run the
    capture+embed for `item` in both spaces first.

    Returns {item, near_space, far_space, min_score, relations:[ids], near:[{id,score}], far:[{id,score}]}.
    `relations` is the inversion result; near/far carry the THRESHOLDED neighbour rows so the surface can
    render the WHY. DELEGATE: Suite.find_relations (→ store/vector_index.query_index space-filter).
    Read-only; no model call."""
    return SUITE.find_relations(item, near_space=near_space, far_space=far_space, k=k, min_score=min_score)


@mcp.tool()
def findings_for(address: str) -> dict:
    """READ the MARKS / gold-likelihood PROFILE at a corpus address — every finding a mark-pass left on
    `address`, oldest-first (the detection thread). A mark = a finding record; the gold-likelihood profile
    is findings_for(item) composed with its evidence — a READ, never a stored score (Tim sees-WHY and can
    overrule; positive-only — frequency only promotes). REUSES the coherence finding store
    (Suite.store.findings_for over the append-only findings.jsonl — the SAME store coherence writes; the
    address IS the key). An address with no findings returns an HONEST empty list (not yet marked), never
    a fabricated mark. Read-only.

    Returns {address, total, findings:[{kind, address, state, source, evidence, ts, …}]}. NOTE: writing
    marks (`mark`) is a later STORE pass (marks-generalization — a claim/span target + mark_type
    retrieval); this tool is the READ side, available now. DELEGATE: Suite.store.findings_for
    (store/fs_store.py)."""
    rows = SUITE.store.findings_for(address)
    return {"address": address, "total": len(rows), "findings": rows}


# --- CREATE (declarative-direct — a projection LENS, like create_role/create_skill; #58) ----------
@mcp.tool()
def create_projection(spec: dict) -> dict:
    """CREATE a NEW projection LENS DIRECTLY — applies LIVE, NO operator approval (#58: declarative
    authoring is the agent's, correctness-gated). A PROJECTION is a declared LENS over a corpus unit (one
    named way to DESCRIBE it — what it IS, its topics, the principles it expresses, its claimed status).
    Dropping a lens makes it appear EVERYWHERE with zero code change: the capture-schema (if
    produced_by='model'), the vector spaces find_relations ranges over (if embeds=true), and
    cognition_info().projections/.spaces — the PART 4.3 "add-a-row = a FILE" registry bar.

    `spec` is the projection ROW (see runtime/projections.py · projections/AGENTS.md):
      • id          (required) — the lens name; MUST be a valid identifier (it becomes projections/<id>.py).
      • level       (required) — the abstraction band (open vocab: structural·content·relational·meaning·
                                 epistemic·generative·texture·functional — a new band is just a new value).
      • produced_by (required) — 'model' (a capture-role DESCRIBES it — the LLM path, included in the
                                 capture-schema) | 'code' (a lifter EXTRACTOR produces it — a later pass).
      • embeds      (required) — bool; does this lens become a vector SPACE (Group L) find_relations uses.
      • field       (optional) — the output field shape ('string'·'array'·'enum').
      • enum        (optional) — for field='enum', the allowed values.
      • desc        (optional) — the render-NOT-judge instruction the capture prompt uses (K3: DESCRIBE
                                 what the unit claims; do NOT judge whether it is true — that is a later reduce).
      • stage       (optional) — effort band ('legibility' cheap broad · 'deep' heavier).

    MECHANISM (reuse-don't-parallel): renders `PROJECTION = {...}` source → runs the registry's OWN
    correctness GATE (import-in-tempdir via ProjectionRegistry — a malformed lens RAISES, never written,
    mirroring create_role/create_skill's gate-in-tempdir) → writes projections/<id>.py atomically →
    git-commits via the shared Suite._commit_or_rollback (path-scoped — only the one file; revertible) →
    rediscovers the live registry. RENDER-NOT-JUDGE is enforced by the schema (a lens DESCRIBES via desc).

    Returns {projection_id, path, live: True, spec}. `live` proves it appears in cognition_info()
    immediately. The build-dispatch floor is UNTOUCHED — this writes a projections/ DATA file (declarative
    authoring), it NEVER dispatches claude -p; node-type / executable-code create stays GATED, off this face.

    SEAM (BAR2, cross-lane — flagged, not made): the long-term home is render_projection_source in
    runtime/authoring.py + a Suite.create_projection method (mirroring create_skill/create_context). This
    in-server author path is the in-lane reuse-don't-parallel move (the SAME registry gate + the SAME
    Suite._commit_or_rollback) until that lands — the SUITE lane's own augment-in-lane/flag-the-seam
    precedent. DELEGATE: runtime.projections (the gate) + Suite._commit_or_rollback + Suite.projection_registry."""
    import os as _os
    import tempfile as _tempfile
    import pprint as _pprint
    from runtime import projections as _proj

    if not isinstance(spec, dict):
        raise TypeError(f"create_projection needs a dict spec (the lens ROW), got {type(spec).__name__}")
    pid = spec.get("id")
    if not pid or not isinstance(pid, str) or not pid.isidentifier():
        raise ValueError(
            f"create_projection: `id` must be a valid python identifier (it becomes projections/<id>.py — "
            f"addressable by file, like a role/skill). Got {pid!r} — fail loud, never an unnamed/illegal lens.")
    if pid in SUITE.projection_registry:
        raise ValueError(
            f"projection {pid!r} already exists — create_projection is for a NEW lens. Fail loud "
            f"(registry-is-truth; existing: {sorted(SUITE.projection_registry)}).")
    # RENDER the lens module source: `PROJECTION = {...}` (the declared row verbatim). Trivial PYTHON-literal
    # serialization (pprint.pformat — NOT json.dumps, which would emit `true`/`null` that aren't Python) —
    # NOT a parallel engine (no logic, no behaviour — DATA). The dict round-trips: pformat of a dict of
    # str/bool/list/None reads back as the same Python value, which the gate then re-validates.
    row = {k: v for k, v in spec.items() if k in _proj.PROJECTION_FIELDS}
    row["id"] = pid
    source = (f'"""projections/{pid}.py — an agent-authored projection LENS (create_projection, #58 direct).\n'
              f'A declared lens over a corpus unit. See runtime/projections.py + projections/AGENTS.md.\n'
              f'Its `id` MUST equal the file stem ({pid!r})."""\n\n'
              f"PROJECTION = {_pprint.pformat(row, indent=4, sort_dicts=True)}\n")
    # THE CORRECTNESS GATE — import-in-tempdir via the registry's OWN discovery path. A malformed lens
    # (bad id / missing required / unknown field / bad type) RAISES in _build_projection here, BEFORE any
    # write to the live projections/ dir (which a bad module would NOT brick — discovery is per-file — but
    # a bad lens must never go live). Mirrors create_role/create_skill's gate-in-tempdir (reuse the gate).
    with _tempfile.TemporaryDirectory() as _td:
        with open(_os.path.join(_td, f"{pid}.py"), "w", encoding="utf-8") as _f:
            _f.write(source)
        gated = _proj.ProjectionRegistry().discover([_td])      # RAISES on a malformed lens (the gate)
        if pid not in gated:
            raise RuntimeError(
                f"create_projection: rendered module for {pid!r} did not discover as a PROJECTION — "
                f"refused to write it (fail loud; a non-discovering lens is a bug in the render).")
    # WRITE atomically into the LIVE projections/ dir, then git-commit (path-scoped, revertible) via the
    # shared Suite path — reuse, NOT a parallel write/commit.
    path = _os.path.join(SUITE.projections_dir, f"{pid}.py")
    _os.makedirs(SUITE.projections_dir, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as _f:
        _f.write(source)
    _os.replace(tmp, path)                                      # atomic; no partial file
    sha = SUITE._commit_or_rollback(path, f"create projection lens '{pid}' (direct)")
    SUITE.projection_registry.rediscover([SUITE.projections_dir])   # go LIVE in this process
    SUITE._emit("apply", f"created projection lens '{pid}' DIRECTLY — now a live lens · {sha[:8]}",
                node_name=pid, commit=sha)
    return {"projection_id": pid, "path": path, "live": pid in SUITE.projection_registry, "spec": row}


# --- CREATE the 4 PURE-DATA file-discovered registries (declarative-direct, like create_projection; #58) ---
# These are THIN DELEGATORS to Suite.create_<kind> (the shared _write_registry_file helper — the proper
# long-term home create_projection's BAR2 seam wished for: ONE author path over the _CORPUS_REGISTRIES
# table, never N copy-pasted bodies). Each: render `<CONST> = {...}` → the registry's OWN gate-in-tempdir
# (a malformed spec RAISES, never written) → atomic write → git-commit → rediscover → LIVE. DATA registries
# → DECLARATIVE-DIRECT (no approval); node-type / executable-code create stays GATED, off this face. FLOOR:
# writes a DATA file, NEVER dispatches claude -p / emits resolve/approve/dispatch.
#   SCOPED TO 4: mark_type · generation_policy · relation_type · ai_tic. The other two discovered registries
#   (lifter/form) carry a CALLABLE (extract/match) in their row — executable code that pprint can't serialize
#   and MCP-JSON can't carry — so a data-create would always fail-loud at the gate. They need a CODE-render+
#   gate authoring contract (create_role-style), net-new + unspecified → FLAGGED for the operator, NOT built
#   here (they stay fully listable via cognition_inputs + governed by the floor; only data-create excludes them).
@mcp.tool()
def create_mark_type(spec: dict) -> dict:
    """CREATE a NEW MARK_TYPE DIRECTLY — applies LIVE, NO approval (#58). A MARK_TYPE is the type
    VOCABULARY a mark carries (the `mark(...)` tool's mark_type must be registered): e.g. gold_likelihood
    / ai_fingerprint / contradiction. `spec` is the row (see runtime/mark_types.py · mark_types/AGENTS.md):
    id (required, becomes mark_types/<id>.py) · value_shape · direction ('surface'|'subtract') · desc.
    Malformed → REFUSED fail-loud (the registry gate). Returns {id, kind, path, live, spec}. DELEGATE:
    Suite.create_mark_type → _write_registry_file → runtime.mark_types (the gate)."""
    return SUITE.create_mark_type(spec)


@mcp.tool()
def create_generation_policy(spec: dict) -> dict:
    """CREATE a NEW GENERATION_POLICY DIRECTLY — applies LIVE, NO approval (#58). A GENERATION_POLICY is
    the per-content GENERATION REGIME run_role reads (run_role(policy=<id>)) — the repetition_penalty
    LADDER as DATA (NOTHING static): default → escalate-on-finish=length → fail-loud degenerate-loop. `spec`
    (see runtime/generation_policies.py · generation_policies/AGENTS.md): id (required) · rep_penalty_ladder
    (required, ASCENDING non-empty list of floats) · diff_against_source (required bool) · json_schema? ·
    temperature? · budget? · desc?. Malformed → REFUSED fail-loud (empty/non-ascending ladder, bad type).
    Returns {id, kind, path, live, spec}. DELEGATE: Suite.create_generation_policy → _write_registry_file."""
    return SUITE.create_generation_policy(spec)


@mcp.tool()
def create_relation_type(spec: dict) -> dict:
    """CREATE a NEW RELATION_TYPE DIRECTLY — applies LIVE, NO approval (#58). A RELATION_TYPE is a typed/
    directional corpus relation (the L3 vocabulary): principle_beneath / fragment_of / contradicts /
    sibling. `spec` (see runtime/relation_types.py · relation_types/AGENTS.md): id (required) · directed
    (required bool) · inverse? · near? · far? · label? · desc?. Malformed → REFUSED fail-loud. Returns
    {id, kind, path, live, spec}. DELEGATE: Suite.create_relation_type → _write_registry_file."""
    return SUITE.create_relation_type(spec)


@mcp.tool()
def create_ai_tic(spec: dict) -> dict:
    """CREATE a NEW AI_TIC DIRECTLY — applies LIVE, NO approval (#58). An AI_TIC is a fingerprint MARKER
    (the M4 vocabulary — generic-AI tells to surface/subtract): framework_imposition / versioning /
    false_finality / silent_fallback / agent_arch / closure_form / mvp. `spec` (see runtime/ai_tics.py ·
    ai_tics/AGENTS.md): id (required) · markers (required) · label · desc. Malformed → REFUSED fail-loud.
    Returns {id, kind, path, live, spec}. DELEGATE: Suite.create_ai_tic → _write_registry_file."""
    return SUITE.create_ai_tic(spec)


# --- MARK — append a typed mark on a claim/span (the marks layer; reuses STORE-2 + the mark_types gate) ---
@mcp.tool()
def mark(target: str, mark_type: str, value: object = None, confidence: float = None,
         source_pass: str = "", evidence: str = "") -> dict:
    """APPEND a MARK on a claim/span `target`, of a REGISTERED `mark_type` (the marks layer, M1). A mark
    targets a CLAIM or SPAN (the `target` string — e.g. a corpus address, a claim id, a span ref) and
    carries a mark_type from the mark_types registry (the type VOCABULARY — create one via
    create_mark_type). The Suite GATES the mark_type fail-loud (an unknown type is REFUSED — registry-is-
    truth, never a fabricated mark_type). Optional fields ride the open record: value · confidence ·
    source_pass (which mark-pass left it) · evidence (the WHY — Tim sees-why, overrules; positive-only).

    Round-trips by BOTH keys: read back via marks_for(target) / marks_by_type(mark_type) (the
    inspect_address / list-by-type seams). Append-only (a target accrues a mark THREAD; re-marking
    re-appends). REUSES STORE-2's append_mark (the dumb marks.jsonl leaf — distinct from findings.jsonl, so
    coherence's orphan rollup is unpolluted); the Suite is the only gate. FLOOR: a mark is a store append
    (telemetry-class), NEVER a resolve/approve/dispatch. Returns the persisted mark record. DELEGATE:
    Suite.mark → Suite.store.append_mark + the mark_types registry gate."""
    fields = {}
    if value is not None:
        fields["value"] = value
    if confidence is not None:
        fields["confidence"] = confidence
    if source_pass:
        fields["source_pass"] = source_pass
    if evidence:
        fields["evidence"] = evidence
    return SUITE.mark(target, mark_type, **fields)


@mcp.tool()
def marks_for(target: str) -> dict:
    """READ every MARK on a claim/span `target`, oldest-first (the mark thread there — the M2 gold-
    likelihood PROFILE is marks_for(target) composed with evidence, a READ not a stored score). An
    unmarked target → an HONEST empty list. REUSES Suite.marks_for (store.marks_for over marks.jsonl;
    persistence-survives-reload). Read-only. Returns {target, total, marks:[…]}. DELEGATE: Suite.marks_for.
    (DISTINCT from findings_for, which reads the legacy coherence findings.jsonl by address — marks carry a
    claim/span target + a registered mark_type, the marks-generalization's two retrieval keys.)"""
    ms = SUITE.marks_for(target)
    return {"target": target, "total": len(ms), "marks": ms}


@mcp.tool()
def marks_by_type(mark_type: str) -> dict:
    """READ every MARK of `mark_type` across targets, oldest-first (the cross-target view of one mark kind
    — e.g. every ai_fingerprint mark, the M4 denoising surface). FAIL LOUD on an unknown mark_type
    (registry-is-truth — a typo'd type would silently look like 'no marks'). REUSES Suite.marks_by_type.
    Read-only. Returns {mark_type, total, marks:[…]}. DELEGATE: Suite.marks_by_type + the mark_types gate."""
    ms = SUITE.marks_by_type(mark_type)
    return {"mark_type": mark_type, "total": len(ms), "marks": ms}


if __name__ == "__main__":
    mcp.run(transport="stdio")
