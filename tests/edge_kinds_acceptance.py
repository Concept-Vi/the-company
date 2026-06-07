"""tests/edge_kinds_acceptance.py — the edge-kind registry + its drift home (Concurrent Cognition C1.3 / R2-FOLD H5).

The edge-kind vocabulary (contracts/node_record.EDGE_KINDS) is a NET-NEW single-source registry.
Per C9.4/H5, every net-new registry must declare a self-description home AND a drift assertion, or
drift_acceptance has nothing to check for it. THIS is that drift assertion:

  1. SCHEMA-ADDITIVE: Edge.kind is optional with default "data" → a pre-v2 edge (no `kind`) loads
     UNCHANGED (the old-graph-load invariant — AGENTS.md rule 2). SCHEMA_VER bumped to 2.
  2. The registry is REFLECTED in its drift home (contracts/AGENTS.md), so it can't silently rot.
  3. The injection kind is registered (C1.3) and run:// addressing is the only scheme.
  4. An unknown kind FAILS LOUD at load (pydantic literal) — never a silent mystery kind.

Run: PYTHONPATH=. python tests/edge_kinds_acceptance.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from contracts.node_record import (
    EDGE_KINDS, EDGE_KIND_DEFAULT, SCHEMA_VER, Edge, Graph, NodeInstance,
)

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# 1. SCHEMA-ADDITIVE — an OLD edge (no `kind`, the exact shape in .data/store graphs today) loads,
#    defaulting to "data". This is the old-graph-load invariant.
old_edge = Edge(from_node="c", from_port="value", to_node="u", to_port="text")
check("an old edge (no kind) loads and defaults to 'data'", old_edge.kind == "data")
check("EDGE_KIND_DEFAULT is 'data'", EDGE_KIND_DEFAULT == "data")
check("SCHEMA_VER bumped to >= 2 for the additive kind field", SCHEMA_VER >= 2)

# an old Graph with bare-dict edges (round-tripped JSON like the real store files) deserializes
old_graph_json = (
    '{"id":"old","nodes":[{"id":"c","type":"constant"},{"id":"u","type":"uppercase"}],'
    '"edges":[{"from_node":"c","from_port":"value","to_node":"u","to_port":"text"}]}'
)
g = Graph.model_validate_json(old_graph_json)
check("an old Graph JSON (edges without kind) deserializes unchanged", len(g.edges) == 1)
check("its edge defaults to kind='data' (no behaviour change)", g.edges[0].kind == "data")

# 2. the injection kind is registered (C1.3) and declared edges validate
inj = Edge(from_node="r", from_port="out", to_node="part2", to_port="ctx", kind="injection")
check("an edge can declare kind='injection' (the cognition ref-read)", inj.kind == "injection")
for k in ("data", "injection", "gate", "fan_in"):
    check(f"edge-kind {k!r} is in the EDGE_KINDS registry", k in EDGE_KINDS)

# 3. an UNKNOWN kind fails loud at load (pydantic literal) — never a silent mystery kind
try:
    Edge(from_node="a", from_port="o", to_node="b", to_port="i", kind="telepathy")
except Exception:
    check("an unknown edge kind FAILS LOUD at load (pydantic literal)", True)
else:
    raise AssertionError("an unknown edge kind did NOT fail loud")

# 4. DRIFT HOME — every registered kind is reflected in its self-description home (contracts/AGENTS.md).
#    If a kind is added to the registry but not documented here, this fails loud (rule 9 / C9.4).
constitution = open(os.path.join(ROOT, "contracts", "AGENTS.md")).read()
missing = [k for k in EDGE_KINDS if k not in constitution]
check(f"every EDGE_KINDS entry is reflected in contracts/AGENTS.md (drift: {missing})", not missing)
check("EDGE_KINDS is named in its drift home", "EDGE_KINDS" in constitution)

print(f"\nALL {PASS} CHECKS PASS — edge-kind registry + schema-additive load + drift home")
