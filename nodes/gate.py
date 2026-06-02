"""gate — a value-conditional routing process node-type (B5 / branching).

The branching primitive. It routes its `value` to exactly ONE of two output
ports — `pass` or `fail` — depending on `verdict`. The taken port is the only
one written; the untaken port's address is simply never set. Downstream of the
untaken port therefore never resolves — identical, mechanically, to a half-wired
node that waits. This is branching as ABSENCE-OF-WRITE, not a conditional in the
scheduler loop: the scheduler stays a resolver, never control-flow.

Selective emission is the one contract this relies on: a multi-output node's
`run()` returns a `{port: value}` dict, and the scheduler writes `set_ref` ONLY
for the ports present in that dict (see runtime/scheduler.py). A `gate` emits a
single-key dict, so exactly one branch is taken.

NOT VOLATILE — `run()` is a pure function of (value, verdict); the memo gate may
cache it like any deterministic node. See nodes/AGENTS.md.
"""
VERSION = "1"
KIND = "process"
PORTS_IN = {"value": "Any", "verdict": "Any"}
PORTS_OUT = {"pass": "Any", "fail": "Any"}

CONFIG: dict = {}   # no editable fields — routing is driven by the `verdict` input


def run(inputs: dict, config: dict):
    """Route `value` to `pass` when `verdict` is truthy, else to `fail`.

    Returns a SINGLE-key dict — the taken port only (selective emission). The
    untaken port is absent, so the scheduler never writes its address and the
    branch downstream of it is pruned (never resolves), not stuck.

    `verdict` is truthy-tested (Python truthiness): any non-empty / non-zero /
    non-None value passes; None / "" / 0 / [] / {} / False fail.
    """
    value = inputs.get("value")
    verdict = inputs.get("verdict")
    if verdict:
        return {"pass": value}
    return {"fail": value}
