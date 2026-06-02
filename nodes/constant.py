"""constant — a content node-type (skeleton).

Emits its configured value. Deterministic, no AI. See nodes/AGENTS.md.
A real C2 declaration (ports/render_set/inspector) arrives with stage E4.
"""
VERSION = "1"
PORTS_IN: dict = {}
PORTS_OUT = {"value": "Any"}

# The single editable field run() reads: the value this node emits.
CONFIG = {
    "value": {"type": "text", "label": "Value", "default": None},
}


def run(inputs: dict, config: dict):
    return config.get("value")
