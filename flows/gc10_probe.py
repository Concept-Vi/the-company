"""flows/gc10_probe.py — PROPOSED flow (GC10 gated authoring: an agent proposed it; the operator approved the SOURCE; landed via apply_flow — the propose→accept→Real lifecycle for the system's own toolset)."""

FLOW = {
    "id": 'gc10_probe',
    "label": 'GC10 probe',
    "description": 'a trivial proposed flow (probe)',
    "params": {'x': {'desc': 'echo value', 'default': 1}},
    "proposes_only": True,
}


def run(x=1) -> dict:
    return {"echo": x, "probe": True}
