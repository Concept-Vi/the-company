"""uppercase — a process node-type (skeleton).

Transforms input text to upper-case. Deterministic, no AI. Demonstrates a
dependent node that only fires once its input address resolves. See nodes/AGENTS.md.
"""
VERSION = "1"
PORTS_IN = {"text": "Text"}
PORTS_OUT = {"text": "Text"}

CONFIG: dict = {}   # no editable fields — pure transform, reads no config keys


def run(inputs: dict, config: dict):
    return str(inputs.get("text", "")).upper()
