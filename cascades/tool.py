"""cascades/tool.py — derive the MCP TOOL face (A's mcp_tools cascade, priority 10).

From faces.tool.verbs, derive the per-type tool surface (create_<t>/list_<t>/get_<t>/update_<t>). A's cloud
cascade wrote these into mcp_tool_registry (30 rows = 15 types × {create,list}); ④ DERIVES the same surface
as a projection artifact (never migrated — regenerated). The engine's real tool face stays the generic
create(kind=…) verb; this records WHAT tool surface the type declares (registry-is-truth for authoring)."""

CASCADE = {
    "id": "tool",
    "target": "mcp_tool_registry",
    "priority": 10,
    "requires": ["tool"],
    "desc": "the per-type MCP tool surface (create_/list_/get_/update_) derived from faces.tool",
}


def handle(type_row: dict, ctx: dict) -> dict:
    tid = type_row["id"]
    face = (type_row.get("faces") or {}).get("tool") or {}
    verbs = list(face.get("verbs") or ["create", "list", "get", "update"])
    return {
        "type": tid,
        "verbs": verbs,
        "tools": [f"{v}_{tid}" for v in verbs],            # create_task, list_tasks would be A's naming
        "source_type": "universal_type",                   # A's provenance marker, preserved
    }
