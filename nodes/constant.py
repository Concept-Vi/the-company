"""constant — a content node-type (skeleton).

Emits its configured value. Deterministic, no AI. See nodes/AGENTS.md.
A real C2 declaration (ports/render_set/inspector) arrives with stage E4.
"""
VERSION = "1"
PORTS_IN: dict = {}
PORTS_OUT = {"value": "Any"}


def run(inputs: dict, config: dict):
    return config.get("value")
