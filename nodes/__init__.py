# Makes `nodes` an importable package so the projection can read nodes/_meta.py (the node-type legibility
# registry). The node MODULES themselves are still discovered by file-path (runtime/registry.py:discover),
# never via `import nodes.<x>` — this __init__ only enables `from nodes._meta import NODE_TYPE_META`.
# discover() skips any file starting with "_" (registry.py:60), so this file and _meta.py are never loaded
# as node-types.
