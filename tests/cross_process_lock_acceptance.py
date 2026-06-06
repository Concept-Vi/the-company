"""STORE lane acceptance — REAL cross-process lock (T-LOCK).

Proves `store.graph_lock(gid)` serializes a load→mutate→save read-modify-write across
SEPARATE PROCESSES (not just threads), and that the SAME cross-process lock primitive
serializes an exactly-once check→claim against the event log.

Why processes, not threads: the bridge is a ThreadingHTTPServer over ONE Suite, so a
thread RLock covers the in-process race — but Tim runs MULTIPLE sessions/processes
against the SAME store (STATE.md: "Tim runs multiple sessions in parallel"). The
in-process thread lock does NOTHING across processes; only an OS file-lock (fcntl.flock
on a per-graph lockfile) serializes two `python runtime/bridge.py` processes hitting the
same store. This test spawns 2 real child processes with multiprocessing and proves it.

PORTABILITY: this test imports ONLY `store.fs_store` — it never references fcntl/lockfile
directly. The enforcement lives behind the resolver seam; the engine (and this test) call
`store.graph_lock(gid)` agnostic to HOW it is enforced.

Run: ./.venv/bin/python tests/cross_process_lock_acceptance.py
"""
import os
import sys
import shutil
import tempfile
import multiprocessing as mp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore                       # noqa: E402
from contracts.node_record import Graph, NodeInstance    # noqa: E402


# ---------------------------------------------------------------------------
# Worker bodies — top-level so they are picklable for multiprocessing spawn.
# Each worker opens its OWN FsStore on the SHARED root (a separate process =
# a separate Suite/store object — exactly the multi-session reality). The ONLY
# thing serializing them is the OS file-lock inside store.graph_lock.
# ---------------------------------------------------------------------------

GID = "race-graph"


def _create_node_worker(root, base_index, count, barrier):
    """Do `count` create_node-equivalent mutations on GID, each the SAME
    load→mutate→save pattern Suite.create_node uses, all under store.graph_lock.
    A barrier makes both processes start hammering at the same instant (real race)."""
    store = FsStore(root)
    barrier.wait()                          # line both processes up on the start
    for i in range(count):
        nid = f"n-{base_index}-{i}"
        with store.graph_lock(GID):         # cross-process serialization point
            g = store.load_graph(GID)       # READ current version
            if g is None:
                g = Graph(id=GID)
            g.nodes.append(NodeInstance(id=nid, type="constant"))   # MUTATE
            store.save_graph(g)             # SAVE (atomic replace)
    return True


def _dispatch_claim_worker(root, claimant, barrier, result_q):
    """Both processes try to claim the SAME dispatch seq via a check→claim on the
    event log, held under the SAME cross-process lock graph_lock provides. Exactly
    one must win (emit the claim); the other must see the claim already exists.
    This is the dispatch-claim TOCTOU expressed against the store primitive."""
    store = FsStore(root)
    SEQ = 7                                 # the resolve seq being claimed
    barrier.wait()
    won = False
    # Use the SAME cross-process lock the spec mandates wrapping the dispatch-claim with.
    # A lock keyed on the claim-target (mirrors the per-seq lock in suite.dispatch_decision,
    # but cross-process via the store). graph_lock keys on a string id, so key it on the seq.
    with store.graph_lock(f"dispatch-claim:{SEQ}"):
        # CHECK: is there already a decision.dispatch for this seq in the durable log?
        already = any(e.get("kind") == "decision.dispatch" and e.get("seq_claimed") == SEQ
                      for e in store.events_since(-1))
        if not already:
            # CLAIM: emit the durable claim (append_event = atomic seq under the event lock).
            store.append_event({"kind": "decision.dispatch", "seq_claimed": SEQ,
                                "by": claimant})
            won = True
    result_q.put((claimant, won))
    return won


def _try_acquire_worker(root, gid, result_q):
    """A SEPARATE process that tries to take store.graph_lock(gid). It signals 'trying',
    then blocks on the (cross-process) flock. If the parent holds the lock (even via a
    NESTED acquire), this child must NOT get in until the parent fully exits. We detect
    'blocked' by the absence of an 'acquired' signal within a short window."""
    store = FsStore(root)
    result_q.put(("trying", os.getpid()))
    with store.graph_lock(gid):
        result_q.put(("acquired", os.getpid()))


def _check(label, ok):
    print(f"  {'PASS' if ok else 'FAIL'}  {label}")
    return ok


def main():
    ok = True
    root = tempfile.mkdtemp(prefix="company-xproc-lock-")   # ext4 (/tmp), never /mnt/c
    try:
        ctx = mp.get_context("spawn")      # separate interpreter — a TRUE second process

        # ---- T-LOCK part 1: 16+ concurrent create_node across 2 processes, no lost update ----
        PER_PROC = 9                        # 2 * 9 = 18 (>= 16 required), each id unique
        barrier = ctx.Barrier(2)
        p0 = ctx.Process(target=_create_node_worker, args=(root, 0, PER_PROC, barrier))
        p1 = ctx.Process(target=_create_node_worker, args=(root, 1, PER_PROC, barrier))
        p0.start(); p1.start()
        p0.join(60); p1.join(60)
        ok &= _check("both create-node processes exited cleanly (no deadlock/hang)",
                     p0.exitcode == 0 and p1.exitcode == 0)

        final = FsStore(root).load_graph(GID)
        n_nodes = len(final.nodes) if final else 0
        expected = 2 * PER_PROC
        ok &= _check(f"ALL {expected} nodes survived (no lost update) — got {n_nodes}",
                     n_nodes == expected)
        ids = {n.id for n in final.nodes} if final else set()
        ok &= _check("every node id is distinct (no overwrite/collision)",
                     len(ids) == n_nodes == expected)

        # ---- T-LOCK part 2: 2 processes racing ONE dispatch-claim → exactly one wins ----
        barrier2 = ctx.Barrier(2)
        q = ctx.Queue()
        d0 = ctx.Process(target=_dispatch_claim_worker, args=(root, "proc-A", barrier2, q))
        d1 = ctx.Process(target=_dispatch_claim_worker, args=(root, "proc-B", barrier2, q))
        d0.start(); d1.start()
        d0.join(60); d1.join(60)
        ok &= _check("both dispatch-claim processes exited cleanly",
                     d0.exitcode == 0 and d1.exitcode == 0)
        outcomes = [q.get(timeout=5), q.get(timeout=5)]
        winners = [c for c, w in outcomes if w]
        ok &= _check(f"EXACTLY ONE process won the dispatch-claim — winners={winners}",
                     len(winners) == 1)
        # the durable log must hold exactly ONE decision.dispatch for the seq
        claims = [e for e in FsStore(root).events_since(-1)
                  if e.get("kind") == "decision.dispatch" and e.get("seq_claimed") == 7]
        ok &= _check(f"durable log holds exactly ONE decision.dispatch claim — got {len(claims)}",
                     len(claims) == 1)

        # ---- T-LOCK part 3: RE-ENTRANCY — the precise reason graph_lock returns a re-entrant lock.
        # fcntl.flock is per-fd and NOT re-entrant, so a naive flock-on-enter/release-on-exit would
        # DEADLOCK on the nested same-gid acquire (or the inner __exit__ would release the OUTER's lock,
        # letting another process in mid-section). suite.py nests graph_lock(gid) calls. We prove BOTH:
        # (a) nesting in one thread does NOT self-deadlock, and (b) the OUTER flock stays HELD through
        # the inner nest — a separate process is BLOCKED until the parent fully exits BOTH levels.
        store = FsStore(root)
        NGID = "reentrant-graph"
        rq = ctx.Queue()
        nested_returned = {"v": False}

        # Take the lock NESTED (depth 2) in this process, then while still inside it spawn a child that
        # tries to acquire the SAME gid — it must NOT get in (flock still held by us through the nest).
        with store.graph_lock(NGID):
            with store.graph_lock(NGID):        # re-entrant: must NOT deadlock (we got here = no deadlock)
                g = store.load_graph(NGID) or Graph(id=NGID)
                g.nodes.append(NodeInstance(id="nested", type="constant"))
                store.save_graph(g)
                child = ctx.Process(target=_try_acquire_worker, args=(root, NGID, rq))
                child.start()
                # the child should report 'trying' then BLOCK on the flock — give it a window.
                sig1 = rq.get(timeout=10)        # 'trying'
                import time as _time
                _time.sleep(1.0)                  # window in which a BROKEN (released-by-inner) lock would let it in
                blocked_while_held = rq.empty()   # no 'acquired' yet = outer flock still held through the nest
            nested_returned["v"] = True           # inner + (about to be) outer exited without hanging
        # now the parent has fully released — the child must be able to acquire and finish.
        child.join(15)
        ok &= _check("nested same-gid graph_lock did NOT self-deadlock (re-entrant)",
                     nested_returned["v"])
        ok &= _check("OUTER cross-process flock stayed HELD through the inner nest (child blocked while parent held)",
                     blocked_while_held)
        ok &= _check("child acquired + exited cleanly AFTER parent fully released (lock truly freed)",
                     child.exitcode == 0)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("\nALL PASS" if ok else "\nFAILURES ABOVE")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
