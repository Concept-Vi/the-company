"""join — a fan-in process node-type (skeleton).

Concatenates all its inputs (ports sorted by name) with a separator. Deterministic.
Enables non-trivial graphs (fan-in) for the runtime. See nodes/AGENTS.md.
"""
VERSION = "1"
PORTS_IN = {"a": "Any", "b": "Any"}
PORTS_OUT = {"joined": "Text"}

# The single editable field run() reads: the separator between joined inputs.
CONFIG = {
    "sep": {"type": "string", "label": "Separator", "default": "|"},
}


def run(inputs: dict, config: dict):
    parts = [str(inputs[k]) for k in sorted(inputs)]
    return config.get("sep", "|").join(parts)
