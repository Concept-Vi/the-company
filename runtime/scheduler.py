"""The reactive scheduler + memo gate (S1). See runtime/AGENTS.md.

A node runs the instant its input ADDRESSES resolve; its output persists to an
address; that resolves downstream. The memo gate makes "re-run only what changed"
and "resume after a crash" the SAME mechanism. NOT a control flow — a resolver.
"""
from __future__ import annotations
import hashlib
import json

from contracts.address import Provenance


def _memo_sig(node, version, input_hashes) -> str:
    payload = json.dumps(
        {"type": node.type, "version": version,
         "config": node.config, "inputs": sorted(input_hashes)},
        sort_keys=True,
    ).encode()
    return "sig:" + hashlib.blake2b(payload, digest_size=16).hexdigest()


def run(graph, store, node_types) -> dict:
    incoming = {n.id: [] for n in graph.nodes}
    for e in graph.edges:
        incoming[e.to_node].append(e)

    logical_of = {n.id: f"run://{graph.id}/{n.id}" for n in graph.nodes}
    done: dict = {}                      # node_id -> output cas://
    ran, skipped = set(), set()
    remaining = {n.id: n for n in graph.nodes}

    progress = True
    while remaining and progress:        # fire anything whose inputs have resolved
        progress = False
        for nid, node in list(remaining.items()):
            edges = incoming[nid]
            if not all(e.from_node in done for e in edges):
                continue                 # inputs not resolved yet

            inputs, input_hashes, input_addrs = {}, [], []
            for e in edges:
                src_cas = done[e.from_node]
                inputs[e.to_port] = store.get_content(src_cas)
                input_hashes.append(src_cas)
                input_addrs.append(logical_of[e.from_node])   # lineage = upstream addresses

            mod = node_types[node.type]
            version = getattr(mod, "VERSION", "1")
            sig = _memo_sig(node, version, input_hashes)
            logical = logical_of[nid]

            cached = store.memo_get(sig)
            if cached and store.exists(cached):           # MEMO GATE — answer already exists
                store.set_ref(logical, cached)
                done[nid] = cached
                skipped.add(nid)
            else:
                out = mod.run(inputs, node.config)
                cas = store.put_content(out)
                store.memo_set(sig, cas)
                store.set_ref(logical, cas)
                store.write_provenance(Provenance(
                    address=logical, content_hash=cas, type=node.type,
                    produced_by=logical, inputs=input_addrs,
                    agent=f"{node.type}@deterministic"))
                done[nid] = cas
                ran.add(nid)

            del remaining[nid]
            progress = True

    return {"done": done, "ran": ran, "skipped": skipped, "stuck": list(remaining)}
