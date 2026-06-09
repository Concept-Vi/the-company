"""mcp_face/tools/create.py — the CREATE tool (consolidated 8→1; MCP-DESIGN-PRINCIPLE).

ONE declarative-authoring tool with a `kind` selector — replaces the flat create_role / create_skill /
create_context / create_projection / create_mark_type / create_generation_policy / create_relation_type /
create_ai_tic. The kinds DERIVE registry-is-truth from the Suite's create_<kind> methods (MINUS 'node',
which is a GRAPH instance, not a declarative registry — it lives in node(op=create)). Declarative-DIRECT
(the entry applies live, correctness-gated in a tempdir) — NEVER resolve/approve/dispatch/claude-p (the
FLOOR; executable-code/node-types stay GATED off this face). Reuse-don't-parallel: dispatches to the
existing Suite.create_<kind> (each a render→gate→write→commit→rediscover via the shared helper). The
drift-home reflection is surfaced in the response (M4 — self-teaching, not a silent gap).
"""

# kind → the drift-home a fresh entry of that kind should be reflected in (M4 self-teaching response).
_DRIFT_HOME = {
    "role": "roles/AGENTS.md", "skill": "skills/AGENTS.md", "context": "contexts/AGENTS.md",
    "projection": "projections/AGENTS.md", "mark_type": "mark_types/AGENTS.md",
    "generation_policy": "generation_policies/AGENTS.md", "relation_type": "relation_types/AGENTS.md",
    "ai_tic": "ai_tics/AGENTS.md",
}


def register(mcp, suite):
    def _kinds():
        # registry-is-truth: the declarative kinds = Suite.create_<kind> MINUS 'node' (graph, not a registry).
        return sorted(k[len("create_"):] for k in dir(suite)
                      if k.startswith("create_") and callable(getattr(suite, k)) and k != "create_node")

    @mcp.tool()
    def create(kind: str, spec: dict, model: str = "") -> dict:
        """Author a NEW declarative registry entry — DIRECT, live, correctness-gated (no operator approval:
        declarative authoring is the agent's). ONE tool for every file-discovered registry; pick `kind`:
          role · skill · context · projection · mark_type · generation_policy · relation_type · ai_tic
        (the live set is registry-is-truth — see the error/cognition_info if unsure). `spec` is the entry
        ROW (its `id` MUST be a valid identifier — it becomes <kind>/<id>.py; the row's fields are the
        registry's own — see cognition_info / field_types). `model` applies only to kind='role' (its bound
        model). Each kind renders→gates-in-tempdir→writes→commits→rediscovers (a malformed spec FAILS LOUD,
        never written). Returns {kind, id, path, live, spec, reflect_in} — `reflect_in` names the drift-home
        doc to reflect the new entry in (keeps tests/<kind>_acceptance green). FLOOR: declarative DATA only —
        never resolve/approve/dispatch; a node-type / executable-code create stays GATED, off this tool
        (graph nodes are node(op=create))."""
        kinds = _kinds()
        if kind not in kinds:
            return {"error": f"create: unknown kind {kind!r}. Valid (registry-is-truth): {kinds}. "
                    "(A graph node is node(op='create'), not a declarative create.)"}
        if not isinstance(spec, dict) or not spec.get("id"):
            return {"error": f"create(kind={kind!r}) needs a `spec` dict with an `id` (a valid identifier — "
                    f"it becomes {kind}/<id>.py). See cognition_info / field_types for the {kind}'s fields."}
        fn = getattr(suite, f"create_{kind}")
        result = fn(spec, model=model or None) if kind == "role" else fn(spec)
        out = dict(result) if isinstance(result, dict) else {"result": result}
        out["kind"] = kind
        out["reflect_in"] = _DRIFT_HOME.get(kind, f"{kind}/AGENTS.md")
        return out
    return create
