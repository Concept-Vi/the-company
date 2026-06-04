"""tests/gate_acceptance.py — the gate node's per-port selective branching actually routes (T2-EMBED-GATE).

`nodes/gate.py` is the branching primitive (B5): it routes `value` to exactly ONE of `pass`/`fail`
on the truthiness of `verdict`, emitting a SINGLE-key dict. The scheduler (runtime/scheduler.py) writes
`set_ref` ONLY for the emitted port, so the untaken branch's address is never written — downstream of it
is PRUNED (deliberately not taken), distinct from STUCK (a genuine wait). The branching MECHANISM is
exercised in scheduler tests, but no committed suite instantiates `type="gate"` end-to-end. This proves it
by USE: a real graph with a gate + a downstream node on EACH branch, run through the Suite/scheduler, and
asserts that ONLY the selected branch's downstream fires while the other is pruned-not-stuck — under BOTH
verdict polarities, so routing demonstrably depends on the verdict.

Run: ./.venv/bin/python tests/gate_acceptance.py
"""
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
PASS = 0
ok = True


def check(label, cond):
    global PASS, ok
    ok &= bool(cond)
    if cond:
        PASS += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def build_branching_graph(suite, gid, verdict_value):
    """value(constant) → gate.value ; verdict(constant) → gate.verdict ;
    gate.pass → onpass(uppercase).text ; gate.fail → onfail(uppercase).text.
    Only the branch matching verdict's truthiness should fire."""
    suite.create_node(gid, "constant", config={"value": "payload"}, node_id="value")
    suite.create_node(gid, "constant", config={"value": verdict_value}, node_id="verdict")
    suite.create_node(gid, "gate", node_id="g")
    suite.create_node(gid, "uppercase", node_id="onpass")
    suite.create_node(gid, "uppercase", node_id="onfail")
    suite.connect(gid, "value", "value", "g", "value")
    suite.connect(gid, "verdict", "value", "g", "verdict")
    suite.connect(gid, "g", "pass", "onpass", "text")
    suite.connect(gid, "g", "fail", "onfail", "text")


def main():
    # gate must be a registered node-type at all (it's in the live registry per MAP.md)
    store_dir = tempfile.mkdtemp(prefix="gate-acc-")
    try:
        store = FsStore(os.path.join(store_dir, "store"))
        reg = NodeRegistry(); reg.discover([NODES])
        suite = Suite(store, reg, nodes_dir=NODES)

        check("gate is a registered node-type", "gate" in reg)
        check("gate declares pass + fail output ports",
              set(reg.types["gate"].ports.outputs) == {"pass", "fail"})

        # === TRUTHY verdict → pass branch fires, fail branch is PRUNED (not stuck) ===
        gid_t = "gate-truthy"
        build_branching_graph(suite, gid_t, "yes")     # non-empty string → truthy
        r_t = suite.run(gid_t)
        ran_t = set(r_t["ran"]) | set(r_t["skipped"])
        check("[truthy] the gate itself ran", "g" in ran_t)
        check("[truthy] the PASS-branch downstream fired", "onpass" in ran_t)
        check("[truthy] the FAIL-branch downstream did NOT fire", "onfail" not in ran_t)
        check("[truthy] the untaken FAIL branch is PRUNED (deliberately not taken)",
              "onfail" in r_t.get("pruned", []))
        check("[truthy] the untaken FAIL branch is NOT reported stuck",
              "onfail" not in r_t.get("stuck", []))
        # the value actually carried through the taken branch (real routing, not just readiness)
        pass_out = store.get_content(store.head(f"run://{gid_t}/onpass")) if store.head(f"run://{gid_t}/onpass") else None
        check("[truthy] the PASS-branch downstream consumed the routed value (PAYLOAD)",
              pass_out == "PAYLOAD")
        check("[truthy] the FAIL-branch address was never written (selective emission)",
              store.head(f"run://{gid_t}/onfail") is None)

        # === FALSY verdict → fail branch fires, pass branch is PRUNED (separate graph id; no memo bleed) ===
        gid_f = "gate-falsy"
        build_branching_graph(suite, gid_f, "")        # empty string → falsy
        r_f = suite.run(gid_f)
        ran_f = set(r_f["ran"]) | set(r_f["skipped"])
        check("[falsy] the gate itself ran", "g" in ran_f)
        check("[falsy] the FAIL-branch downstream fired", "onfail" in ran_f)
        check("[falsy] the PASS-branch downstream did NOT fire", "onpass" not in ran_f)
        check("[falsy] the untaken PASS branch is PRUNED",
              "onpass" in r_f.get("pruned", []))
        check("[falsy] the untaken PASS branch is NOT reported stuck",
              "onpass" not in r_f.get("stuck", []))
        fail_out = store.get_content(store.head(f"run://{gid_f}/onfail")) if store.head(f"run://{gid_f}/onfail") else None
        check("[falsy] the FAIL-branch downstream consumed the routed value (PAYLOAD)",
              fail_out == "PAYLOAD")
        check("[falsy] the PASS-branch address was never written (selective emission)",
              store.head(f"run://{gid_f}/onpass") is None)

        # === the discriminator: the SAME topology routed OPPOSITELY purely on the verdict ===
        check("routing depends on the verdict (truthy→pass, falsy→fail — opposite outcomes, same graph shape)",
              ("onpass" in ran_t and "onfail" not in ran_t)
              and ("onfail" in ran_f and "onpass" not in ran_f))

        print("\n" + (f"ALL {PASS} CHECKS PASS — gate selective branching routes by verdict, untaken branch pruned-not-stuck"
                      if ok else "GATE ACCEPTANCE FAILED"))
        return 0 if ok else 1
    finally:
        shutil.rmtree(store_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
