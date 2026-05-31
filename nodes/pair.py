"""pair — a NON-commutative fan-in process node-type (skeleton).

Emits "<a>><b>" — order matters. Exists so the test suite exercises port→input
binding in the memo signature (a commutative node like `join` would hide that bug).
See nodes/AGENTS.md.
"""
VERSION = "1"
PORTS_IN = {"a": "Any", "b": "Any"}
PORTS_OUT = {"pair": "Text"}


def run(inputs: dict, config: dict):
    return f"{inputs.get('a')}>{inputs.get('b')}"
