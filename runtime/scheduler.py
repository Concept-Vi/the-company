"""The reactive scheduler + memo gate (S1). See runtime/AGENTS.md.

A node runs the instant its input ADDRESSES resolve in the store; its output
persists to an address; that resolves downstream. Readiness is read from the
STORE (not an in-memory map), so resume-across-process falls out for free.
The memo gate makes "re-run only what changed" and "resume" the same mechanism.
NOT a control flow — a resolver.

Run path: compile the workflow -> ExecNodes (C5), then resolve-and-fire over them.
Live controls are addressing operations:
  - branch : write to run://…@<branch>  (timelines coexist; main is branchless)
  - pause  : hold a set of node-ids (don't dispatch; downstream stays unresolved)
  - force  : bypass the memo gate for a set of node-ids (retry)

A node is READY only when every input port its type DECLARES (PORTS_IN) is both
wired and resolved — a half-wired node waits (it does not fire on empty input).
"""
from __future__ import annotations
import hashlib
import json

from contracts.address import Provenance
from runtime.compile import compile as _compile


def _memo_sig(ex, version, input_map: dict) -> str:
    # input_map is PORT -> content-hash, so swapping which value feeds which port
    # changes the signature (a port-agnostic hash would mis-cache non-commutative nodes).
    payload = json.dumps(
        {"type": ex.type, "version": version,
         "config": ex.config, "inputs": input_map},
        sort_keys=True,
    ).encode()
    return "sig:" + hashlib.blake2b(payload, digest_size=16).hexdigest()


def run(graph, store, node_types, branch: str = "main",
        pause=None, force=None) -> dict:
    pause = set(pause or [])
    force = set(force or [])

    execs = _compile(graph, branch=branch)            # compile is in the run path
    by_id = {e.id: e for e in execs}
    out_addr = {e.id: (e.outputs.get("out") or next(iter(e.outputs.values())))
                for e in execs}

    ran, skipped, processed = set(), set(), set()
    progress = True
    while len(processed) < len(execs) and progress:
        progress = False
        for nid, ex in by_id.items():
            if nid in processed or nid in pause:
                continue
            # READY only when every DECLARED input port is wired AND resolved.
            declared = set(getattr(node_types[ex.type], "PORTS_IN", {}).keys())
            if not declared <= set(ex.inputs.keys()):     # a required port is unwired -> wait
                continue
            if not all(store.head(a) for a in ex.inputs.values()):
                continue

            in_addrs = list(ex.inputs.values())
            input_map = {port: store.head(a) for port, a in ex.inputs.items()}   # port -> cas
            inputs = {port: store.get_content(cas) for port, cas in input_map.items()}
            mod = node_types[ex.type]
            version = getattr(mod, "VERSION", "1")
            sig = _memo_sig(ex, version, input_map)
            oaddr = out_addr[nid]

            cached = store.memo_get(sig)
            if nid not in force and cached and store.exists(cached):       # MEMO GATE
                cas = cached
                agent = f"{ex.type}@memo"
                skipped.add(nid)
            else:
                cas = store.put_content(mod.run(inputs, ex.config))
                store.memo_set(sig, cas)
                agent = f"{ex.type}@deterministic"
                ran.add(nid)
            store.set_ref(oaddr, cas)
            store.write_provenance(Provenance(          # every write records lineage (store invariant)
                address=oaddr, content_hash=cas, type=ex.type,
                produced_by=oaddr, inputs=in_addrs, agent=agent))

            processed.add(nid)
            progress = True

    stuck = [nid for nid in by_id if nid not in processed and nid not in pause]
    return {"ran": ran, "skipped": skipped, "stuck": stuck,
            "held": sorted(pause), "compiled": len(execs)}
