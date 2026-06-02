"""reverse — a process node-type.

Reverses its text input (output = the input string, characters in reverse order).
Deterministic, no AI — a **pure transform of its input**, exactly like uppercase /
titlecase / wordcount, so it must NOT declare `VOLATILE` (the same input can never
need a fresh output, so the memo gate may safely serve a cached result). Drop it in;
it self-registers via auto-discovery (runtime/registry.py reads VERSION / KIND /
PORTS_IN / PORTS_OUT / CONFIG + run). See nodes/AGENTS.md.
"""
ORIGIN = 'system'  # grown via the decision→implementation wire (self-grown) — provenance layer
VERSION = "1"
KIND = "process"
PORTS_IN = {"text": "Text"}
PORTS_OUT = {"text": "Text"}

CONFIG: dict = {}   # no editable fields — pure transform, reads no config keys


def run(inputs: dict, config: dict):
    return str(inputs.get("text", ""))[::-1]
