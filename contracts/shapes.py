"""Compat shim — shapes moved to typed contracts in E1.

Kept so existing imports (`from contracts.shapes import NodeInstance, Edge, Graph`)
keep working — schema-additive, never break what exists. Prefer importing from
contracts.node_record directly in new code.
"""
from contracts.node_record import NodeInstance, Edge, Graph, ExecNode  # noqa: F401
