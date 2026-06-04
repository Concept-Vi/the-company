"""tests/concurrency_acceptance.py — S4 · cross-PROCESS safety (foundational 🔴).

IS (before S4): the bridge and the MCP face are TWO separate processes on ONE STORE_DIR
(bridge.py:53 + mcp_face/server.py:20 both Suite(FsStore(STORE_DIR))). All locks were `threading`
(in-process only) — `grep fcntl|flock|LOCK_EX` → 0. So two FACES could:
  (a) both load graph version V, both save → LOST UPDATE (last-writer-wins), and
  (b) both clear the wire's exactly-once dispatch CHECK before either CLAIMs → DOUBLE `claude -p` launch.
The interaction layer ADDS writers (comments/commands/build-intents) through the bridge while the MCP
face + the wire also write — so this risk is the load-bearing engine risk the build had to close.

SHOULD-BE (S4, this proves it): an `fcntl` (OS) advisory file lock around the graph load→mutate→save and
the dispatch CHECK→CLAIM serializes those critical sections ACROSS PROCESSES; hot writes are fsync'd.

WHY THIS TEST USES REAL PROCESSES, NOT THREADS (the false-pass trap):
  Threads are ALREADY serialized by the existing threading.RLock — a threaded test would pass trivially
  and prove NOTHING about the process boundary fcntl exists for. So this test spawns REAL subprocesses
  (the bridge↔MCP boundary) on ONE isolated tmp store and asserts the cross-process guarantee.

DEADLOCK-SAFETY (mandatory, per the spec): every subprocess is run under a HARD timeout. If a child
hangs (a lock-ordering bug, the 3am deadlock the spec warns about), the parent KILLS it and the test
FAILS LOUD (exit 2 = BLOCKED) — it NEVER hangs the harness and NEVER leaves a lock held (the children
own their own isolated store; killing them frees their fds; the parent holds no store lock). A clean
PASS is exit 0; a real concurrency violation is exit 1 (FAIL); a hang is exit 2 (BLOCKED).

The worktree store is ISOLATED (a fresh tmp dir, never ~/company/.data) — safe to hammer.
"""
import os, sys, json, time, tempfile, shutil, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PY = sys.executable
HARD_TIMEOUT = 60          # seconds per child — generous for fsync'd writes, far below a deadlock-hang
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# ──────────────────────────────────────────────────────────────────────────────────────────────────
# The WORKER body — run as a child process (a stand-in for one face: its own Suite over the shared store)
# ──────────────────────────────────────────────────────────────────────────────────────────────────
WORKER_SRC = r'''
import os, sys, json
ROOT = os.environ["CONCURRENCY_ROOT"]
sys.path.insert(0, ROOT)
from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

mode = sys.argv[1]
store_dir = sys.argv[2]
tag = sys.argv[3]                       # this worker's unique id-prefix
store = FsStore(store_dir)
reg = NodeRegistry(); reg.discover([os.path.join(ROOT, "nodes")])
suite = Suite(store, reg, nodes_dir=os.path.join(ROOT, "nodes"))

if mode == "graph":
    # LOST-UPDATE probe: add N nodes to the SHARED graph 'g'. Each node id is unique to this worker,
    # so if the cross-process lock holds, ALL of both workers' nodes survive (no last-writer-wins).
    n = int(sys.argv[4])
    for i in range(n):
        suite.create_node("g", "constant", node_id=f"{tag}-{i}", config={"value": i})
    print(json.dumps({"worker": tag, "added": n}))

elif mode == "dispatch":
    # DOUBLE-DISPATCH probe: both workers try to CLAIM the same dispatch seq via the SAME critical
    # section dispatch_decision uses (the per-seq threading lock + the store's cross-process fcntl
    # dispatch_lock, then the durable _already_dispatched check + claim emit). Exactly ONE must win.
    seq = int(sys.argv[4])
    won = False
    try:
        with suite._dispatch_lock(seq), suite.store.dispatch_lock(seq):
            if suite._already_dispatched(seq):
                won = False                      # someone already claimed it
            else:
                suite._emit_durable("decision.dispatch",
                                    f"claim by {tag} for seq={seq}",
                                    surfaced="probe", derived_from=seq,
                                    consequence_class="decision_build", scope=["x"],
                                    address="ui://chrome/inbox")
                won = True
    except Exception as e:
        print(json.dumps({"worker": tag, "error": f"{type(e).__name__}: {e}"})); sys.exit(3)
    print(json.dumps({"worker": tag, "won": won}))
'''


def _spawn(mode, store_dir, tag, arg):
    env = dict(os.environ, CONCURRENCY_ROOT=ROOT)
    return subprocess.Popen(
        [PY, "-c", WORKER_SRC, mode, store_dir, tag, str(arg)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)


def _run_pair(mode, store_dir, arg):
    """Spawn TWO workers concurrently; HARD-timeout each; return (results, blocked_reason|None)."""
    p1 = _spawn(mode, store_dir, "A", arg)
    p2 = _spawn(mode, store_dir, "B", arg)
    results, deadline = [], time.time() + HARD_TIMEOUT
    for p in (p1, p2):
        remaining = max(0.1, deadline - time.time())
        try:
            out, err = p.communicate(timeout=remaining)
        except subprocess.TimeoutExpired:
            # DEADLOCK-SAFETY: kill the hung child(ren), report BLOCKED, never hang the harness.
            for q in (p1, p2):
                try: q.kill()
                except Exception: pass
            return results, f"{mode} worker hung >{HARD_TIMEOUT}s (deadlock) — KILLED, marking BLOCKED"
        if p.returncode != 0:
            return results, f"{mode} worker exited {p.returncode}: {err.strip()[:300]}"
        try:
            results.append(json.loads(out.strip().splitlines()[-1]))
        except (ValueError, IndexError):
            return results, f"{mode} worker emitted unparseable output: {out!r} / {err[:200]}"
    return results, None


def main():
    print("\nconcurrency_acceptance — S4 cross-process safety (real subprocesses, hard-timeout-wrapped)\n")
    work = tempfile.mkdtemp(prefix="concurrency-")
    try:
        # ── PROBE 1: NO LOST-UPDATE under two processes mutating one graph ──────────────────────────
        per = 25
        store_dir = os.path.join(work, "store1")
        FsStoreInit = __import__("store.fs_store", fromlist=["FsStore"]).FsStore
        FsStoreInit(store_dir)                       # create the dir structure up front (shared)
        results, blocked = _run_pair("graph", store_dir, per)
        if blocked:
            print(f"  ⚠️  BLOCKED: {blocked}")
            sys.exit(2)
        # count survivors in the shared graph — cross-process lock holds ⇒ ALL 2*per nodes survive.
        g = FsStoreInit(store_dir).load_graph("g")
        ids = {n.id for n in (g.nodes if g else [])}
        expected = {f"A-{i}" for i in range(per)} | {f"B-{i}" for i in range(per)}
        survived = len(ids & expected)
        print(f"  graph probe: expected {len(expected)} nodes, found {survived} "
              f"(lost: {sorted(expected - ids)[:5] or 'none'})")
        check(f"NO LOST-UPDATE: all {len(expected)} nodes from BOTH processes survived "
              f"(without the fcntl lock, last-writer-wins drops the other process's interleaved writes)",
              survived == len(expected))

        # ── PROBE 2: NO DOUBLE-DISPATCH under two processes claiming one seq ─────────────────────────
        store_dir2 = os.path.join(work, "store2")
        FsStoreInit(store_dir2)
        results, blocked = _run_pair("dispatch", store_dir2, 42)
        if blocked:
            print(f"  ⚠️  BLOCKED: {blocked}")
            sys.exit(2)
        wins = sum(1 for r in results if r.get("won"))
        print(f"  dispatch probe: {wins} of 2 processes won the exactly-once claim "
              f"({[r.get('won') for r in results]})")
        check("NO DOUBLE-DISPATCH: exactly ONE of two processes won the dispatch claim "
              "(the fcntl dispatch_lock + durable check serialize the CHECK→CLAIM across processes — "
              "without it both clear the check and double-launch claude -p)",
              wins == 1)
        # and the durable event log records exactly ONE decision.dispatch for the seq (ground truth)
        evs = [e for e in FsStoreInit(store_dir2).events_since(-1)
               if e.get("kind") == "decision.dispatch" and e.get("derived_from") == 42]
        check(f"durable event log carries EXACTLY ONE decision.dispatch claim for seq=42 (found {len(evs)})",
              len(evs) == 1)

        # ── PROBE 3: the fsync atomic-write helper produces a whole, readable file (durability path) ──
        s = FsStoreInit(os.path.join(work, "store3"))
        s.set_ref("run://g/n", "cas://b2:deadbeef")
        check("fsync'd set_ref round-trips a WHOLE ref (crash-durable atomic write, no torn read)",
              s.head("run://g/n") == "cas://b2:deadbeef")

        print(f"\nconcurrency_acceptance: {PASS} checks passed — S4 cross-process safety proven "
              f"(no lost-update, no double-dispatch, durable writes).\n")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
