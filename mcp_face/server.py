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
             ensure: bool = False, ensure_evict: bool = False) -> dict:
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

    GENERATE runs PERSIST: the validated output is written to run://<turn>/<role> (the SAME put_content→
    set_ref primitives run_items uses) so the run can be inspected back by address (inspect_address) and
    fed as an input downstream. Returns {role, op, output, address, turn_id}.

    FLOOR: this produces a run:// output (computation) — it emits NO resolve/approve/dispatch."""
    r = _resolve_role(role)
    turn_id = "mcp-" + _time.strftime("%Y%m%d-%H%M%S") + f"-{int(_time.monotonic()*1000) % 100000}"
    # resolve any address-valued declared inputs through the engine resolver (input-address intent).
    ctx = {"utterance": utterance}
    for name, val in dict(inputs).items():
        if isinstance(val, str) and "://" in val:
            ctx[name] = _cog.resolve_address(SUITE.store, val, turn_id=turn_id)
        else:
            ctx[name] = val
    kw = {"max_tokens": max_tokens, "temperature": temperature, "store": SUITE.store,
          "ensure": ensure, "ensure_evict": ensure_evict}
    if model:
        kw["model"] = model
    _t0 = _time.monotonic()
    out = _cog.run_role(r, ctx, **kw)
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
    SUITE.emit_run_record("cognition.run_role", _ms,
                          run_op=getattr(r, "op", "generate"), turn_id=turn_id,
                          role=r.id, addresses=[address])
    return {"role": r.id, "op": getattr(r, "op", "generate"), "output": out,
            "address": address, "turn_id": turn_id}


@mcp.tool()
def run_items(role: str, items: list, max_tokens: int = 256, temperature: float = 0.0) -> dict:
    """CONFIGURE + RUN the MAP — fan ONE role over N input-UNITS (1 role × N units). REUSES
    runtime.cognition.run_items (the axis-inversion engine — never a parallel fan). Each unit is either
    a LITERAL value OR an ADDRESS (run://…, cas://… — resolved via resolve_address). Outputs land at
    run://<turn>/<role>/<i> (inspectable/feedable). Returns {role, turn_id, n_units, addresses, resolved,
    finish_order, skipped, wall_s}. A DRIVER: emits NO resolve/approve/dispatch (the floor)."""
    r = _resolve_role(role)
    turn_id = "mcp-items-" + _time.strftime("%Y%m%d-%H%M%S") + f"-{int(_time.monotonic()*1000) % 100000}"
    res = _cog.run_items(r, list(items), SUITE.store, turn_id=turn_id, emit=_cog_emit,
                         max_tokens=max_tokens, temperature=temperature)
    return {"role": r.id, "turn_id": turn_id, "n_units": len(items),
            "addresses": res.addresses, "resolved": res.resolved,
            "finish_order": res.finish_order, "skipped": res.skipped, "wall_s": res.wall_s}


# the closed, NAMED reduce-rule registry (registry-is-truth): a deterministic L2 join the agent selects
# BY NAME over the MCP/JSON boundary (a Python callable cannot cross MCP). Each is a PURE function over
# the N read-back values. An unknown name FAILS LOUD (never a fabricated rule). This is the rule-mode
# analogue of the role/cluster modes — additive; add a named rule here when a new deterministic join is needed.
_REDUCE_RULES = {
    "count":  lambda values: {"count": len(values)},
    "concat": lambda values: {"concat": [v for v in values]},
    "first":  lambda values: {"first": (values[0] if values else None)},
}


@mcp.tool()
def run_reduce(addresses: list, mode: str, role: str = "", reduce_rule: str = "",
               cluster_threshold: float = 0.85, max_tokens: int = 512) -> dict:
    """CONFIGURE + RUN the cross-unit JOIN — REDUCE a set of map-output run:// addresses into ONE output.
    REUSES runtime.cognition.run_reduce (the net-new JOIN engine — never a parallel reducer).

      mode="role"    → synthesize join (op=generate). Pass `role` = a reduce-role id (e.g. 'reduce_synth').
      mode="rule"    → deterministic L2 join (no model). Pass `reduce_rule` = a NAMED built-in
                       (one of: count · concat · first) — a callable can't cross MCP, so select by name.
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
        if reduce_rule not in _REDUCE_RULES:
            raise ValueError(f"run_reduce(mode='rule'): unknown reduce_rule {reduce_rule!r} — named "
                             f"built-ins are {sorted(_REDUCE_RULES)} (fail loud, never a fabricated rule).")
        kw["reduce_rule"] = _REDUCE_RULES[reduce_rule]
    res = _cog.run_reduce(list(addresses), SUITE.store, **kw)
    return {"turn_id": turn_id, "mode": mode, "joined": res.joined, "inputs": res.inputs,
            "skipped": res.skipped, "wall_s": res.wall_s, "detail": res.detail}


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


if __name__ == "__main__":
    mcp.run(transport="stdio")
