"""STORE lane acceptance — DURABILITY / fsync (T-FSYNC).

Proves the three HOT durable writes are flushed to disk with `os.fsync` (not left in the
OS page cache, where a power-loss / crash loses the most recent acknowledged writes), and
that each round-trips intact.

The three hot writes (the durable spine the rest of the system rides on):
  1. event-log append (`append_event`)  — the exactly-once dispatch claim + the SSE trajectory
  2. ref pointer       (`set_ref`)       — every node fire's output address
  3. graph save        (`save_graph`)     — the canvas substrate, shared across faces

Plus the directory entry is fsync'd after the atomic rename in set_ref/save_graph, so the
rename itself is durable (a renamed-but-not-dir-fsync'd file can vanish on crash on some fs).

Read paths are untouched — fsync is cheap on the write side and absent on reads.

We assert fsync is INVOKED by wrapping `os.fsync` with a counter (the durability contract is
"the bytes were forced to stable storage", and the observable proof of that is the fsync
syscall on the right fds), AND that the data round-trips (correctness preserved).

Run: ./.venv/bin/python tests/durability_acceptance.py
"""
import os
import sys
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore   # noqa: E402


def _check(label, ok):
    print(f"  {'PASS' if ok else 'FAIL'}  {label}")
    return ok


def main():
    ok = True
    root = tempfile.mkdtemp(prefix="company-durability-")   # ext4 (/tmp), never /mnt/c
    try:
        store = FsStore(root)

        # Instrument os.fsync to count calls during each hot write (the observable proof the
        # bytes were forced to stable storage). We wrap the real syscall, so durability is REAL
        # (the fd is genuinely fsync'd) AND counted.
        real_fsync = os.fsync
        calls = {"n": 0}

        def counting_fsync(fd):
            calls["n"] += 1
            return real_fsync(fd)

        os.fsync = counting_fsync
        try:
            # 1 — event-log append
            calls["n"] = 0
            rec = store.append_event({"kind": "test.event", "summary": "durable?"})
            ok &= _check("append_event invokes os.fsync (>=1)", calls["n"] >= 1)
            back = store.events_since(-1)
            ok &= _check("event round-trips intact",
                         any(e.get("summary") == "durable?" and e.get("seq") == rec["seq"]
                             for e in back))

            # 2 — set_ref (atomic replace + dir fsync). Expect fsync on the file fd AND the dir fd.
            calls["n"] = 0
            cas = store.put_content({"hello": "world"})
            store.set_ref("run://demo/out", cas)
            ok &= _check("set_ref invokes os.fsync on file + dir (>=2)", calls["n"] >= 2)
            ok &= _check("ref round-trips intact",
                         store.head("run://demo/out") == cas and
                         store.get_content(cas) == {"hello": "world"})

            # 3 — save_graph (atomic replace + dir fsync). Expect fsync on the file fd AND the dir fd.
            from contracts.node_record import Graph, NodeInstance
            calls["n"] = 0
            g = Graph(id="dg", nodes=[NodeInstance(id="a", type="constant")])
            store.save_graph(g)
            ok &= _check("save_graph invokes os.fsync on file + dir (>=2)", calls["n"] >= 2)
            g2 = store.load_graph("dg")
            ok &= _check("graph round-trips intact",
                         g2 is not None and len(g2.nodes) == 1 and g2.nodes[0].id == "a")
        finally:
            os.fsync = real_fsync

        # 4 — read paths are NOT fsync'd (cheap reads, durability only on writes). Re-instrument and
        # confirm a pure read sequence triggers zero fsyncs.
        calls["n"] = 0
        os.fsync = counting_fsync
        try:
            _ = store.head("run://demo/out")
            _ = store.load_graph("dg")
            _ = store.recent_events(10)
            _ = store.get_content(cas)
        finally:
            os.fsync = real_fsync
        ok &= _check("read paths invoke NO fsync (durability is write-only)", calls["n"] == 0)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("\nALL PASS" if ok else "\nFAILURES ABOVE")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
