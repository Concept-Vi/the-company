"""mcp_face/tools/ — the FILE-DISCOVERED MCP tool modules (MCP-DESIGN-PRINCIPLE).

Each `mcp_face/tools/<resource>.py` exposes `register(mcp, suite)` and defines ONE consolidated,
parameterised tool for that resource (op/by/kind selector — NOT flat-per-operation). server.py
discovers + registers them all via pkgutil (mirrors the file-discovered registries roles/·projections/·
nodes/ — add a resource = add a file, no edit to server.py). The standing law:
build-prep/cognition-self-improvement/MCP-DESIGN-PRINCIPLE.md.
"""
