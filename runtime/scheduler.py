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

    execs = _compile(graph, branch=branch, node_types=node_types)   # compile is in the run path
    by_id = {e.id: e for e in execs}
    # Per-port output addresses (B5): the FULL {port: address} map per node, not
    # collapsed to one. A single-output node carries {"out": <bare addr>}; a
    # multi-output node carries {port: <addr>#<port>} — each a distinct store key,
    # so a branch not taken is simply an address never written.
    out_ports = {e.id: dict(e.outputs) for e in execs}

    ran, skipped, processed = set(), set(), set()
    # PER-NODE ERROR ISOLATION: one node's run() raising must NOT abort the whole run (the other ready
    # nodes still resolve). `failed` is a {nid: "ErrType: message"} map — a DICT (not a list) so the WHY
    # is carried legibly (fail-loud, rule 4), and drop-in with how ran/skipped/stuck are consumed (`in`,
    # len, sorted all work over keys). A failed node writes NO output ref (its downstream inputs never
    # resolve → that downstream stays unresolved → classified stuck below, which is correct). The result
    # SURFACES `failed` so the caller (Suite.run / state) can report it — containment, not swallowing.
    failed: dict = {}
    progress = True
    while len(processed) < len(execs) and progress:
        progress = False
        for nid, ex in by_id.items():
            if nid in processed or nid in pause:
                continue
            # Reference-resolved node-types (e.g. portal) are NOT computed and NOT fired —
            # their output is a live window onto another address, read at view-time
            # (Suite.state). Mark processed so the run terminates; write no ref of our own.
            if getattr(node_types[ex.type], "RESOLVE", "compute") == "reference":
                processed.add(nid)
                progress = True
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
            ports = out_ports[nid]
            multi = len(ports) > 1

            # VOLATILE nodes read EXTERNAL state (filesystem, network) — their output is NOT a pure
            # function of (type, version, config, inputs), so the memo gate would wrongly cache a
            # stale first-run output forever (red-team F1). Never memo-skip them; always re-run.
            # The memo cas is the RAW run() return (a single-key/multi-key dict for a multi-output
            # node, a bare value for a single-output node); a hit re-expands it per-port below, so
            # selective emission is preserved across cache hits.
            volatile = getattr(mod, "VOLATILE", False)
            cached = store.memo_get(sig)
            if nid not in force and not volatile and cached and store.exists(cached):   # MEMO GATE
                cas = cached
                result = store.get_content(cas)
                agent = f"{ex.type}@memo"
                skipped.add(nid)
            else:
                try:
                    result = mod.run(inputs, ex.config)
                except Exception as e:
                    # CONTAINMENT (not swallowing): mark THIS node failed with its error captured, write
                    # NO output ref (skip put_content/memo_set/the per-port write block via `continue`),
                    # and CONTINUE resolving the other ready nodes — one bad node must not abort the run.
                    # `processed.add(nid)` keeps it OUT of `unreached` so the stuck/pruned logic below never
                    # misclassifies it as stuck (it appears ONLY in `failed`). Its downstream stays
                    # unresolved (inputs never resolve) — correct. NO failure is cached (memo_set skipped),
                    # so a re-run retries it. We do NOT emit here — the scheduler stays pure; surfacing the
                    # failure is the Suite's job (it reads result["failed"]). Fail-loud, rule 4.
                    failed[nid] = f"{type(e).__name__}: {e}"
                    processed.add(nid)
                    progress = True
                    continue
                cas = store.put_content(result)
                store.memo_set(sig, cas)
                agent = f"{ex.type}@deterministic"
                ran.add(nid)

            # Map the run() return onto per-port WRITES. A multi-output node returns a
            # {port: value} dict and we write set_ref ONLY for the ports present (selective
            # emission — a gate that returns {"pass": v} leaves "fail" unwritten, pruning that
            # branch). A single-output node returns a bare value -> the lone "out" port
            # (back-compat: a non-dict return is the one declared port). Fail loud on an
            # unknown port (rule 4): the scheduler stays generic, the node owns its ports.
            if multi:
                if not isinstance(result, dict):
                    raise ValueError(
                        f"scheduler: multi-output node {nid!r} ({ex.type!r}) must return a "
                        f"{{port: value}} dict, got {type(result).__name__}"
                    )
                emit = result
                unknown = set(emit) - set(ports)
                if unknown:
                    raise ValueError(
                        f"scheduler: node {nid!r} ({ex.type!r}) emitted unknown port(s) "
                        f"{sorted(unknown)} — declared ports are {sorted(ports)}"
                    )
            else:
                emit = {"out": result}

            for port, value in emit.items():
                oaddr = ports[port]
                pcas = store.put_content(value) if multi else cas   # single: value IS the memo cas
                store.set_ref(oaddr, pcas)
                store.write_provenance(Provenance(   # every write records lineage (store invariant)
                    address=oaddr, content_hash=pcas, type=ex.type,
                    produced_by=oaddr, inputs=in_addrs, agent=agent))

            processed.add(nid)
            progress = True

    # Distinguish a PRUNED branch from a genuinely STUCK node. A node never reached
    # is "stuck" UNLESS one of its inputs points at a port-address a multi-output node
    # that DID run deliberately left unwritten (a gate's not-taken branch) — or it is
    # downstream of such a node (transitive). That is pruning, not a failure: the branch
    # was correctly never taken. Gate on owner-ran + multi-output (NOT mere "processed",
    # so a reference-resolved portal that writes nothing is not mistaken for a prune).
    # Addresses a multi-output node that COMPLETED (ran OR memo-skipped) OWNS but never
    # wrote = deliberately-pruned ports. `ran | skipped` is essential: on resume / a second
    # pass the gate is a memo HIT (in `skipped`, not `ran`), yet its not-taken branch is
    # still deliberately unwritten and must stay pruned, not flip to stuck. Reference-resolved
    # portals enter `processed` WITHOUT `ran`/`skipped`, so they're never mistaken for prunes.
    pruned_addrs = {a for nid in (ran | skipped) for a in out_ports[nid].values()
                    if len(out_ports[nid]) > 1 and not store.head(a)}
    unreached = [nid for nid in by_id if nid not in processed and nid not in pause]
    pruned, stuck = [], []
    changed = True
    while changed:                                   # transitive closure over the not-taken branch
        changed = False
        for nid in unreached:
            if nid in pruned:
                continue
            in_addrs = list(by_id[nid].inputs.values())
            # downstream of a pruned address, OR of another pruned node's (unwritten) ports
            feeds_pruned = {a for pid in pruned for a in out_ports[pid].values()}
            if any(a in pruned_addrs or a in feeds_pruned for a in in_addrs):
                pruned.append(nid)
                changed = True
    stuck = [nid for nid in unreached if nid not in pruned]
    return {"ran": ran, "skipped": skipped, "stuck": stuck, "pruned": pruned,
            "failed": failed, "held": sorted(pause), "compiled": len(execs)}
