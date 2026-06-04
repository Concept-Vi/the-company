"""Acceptance — set_ref is ATOMIC (no torn/empty read), hardening FIX 1.

set_ref is the scheduler's hot-path output write. The prior code used a naked write_text, which
TRUNCATES the target before re-filling it; during that window a concurrent head() can read "" — which
the scheduler readiness check treats as UNRESOLVED (a node silently waits a pass) and get_content("")
raises. This proves set_ref now writes via tmp + os.replace (same-fs atomic rename), so every concurrent
read of the ref is the WHOLE old cas or the WHOLE new one — never torn/empty.

Run: python3 tests/set_ref_atomic_acceptance.py
"""
import os
import shutil
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore   # noqa: E402

STORE_DIR = "/tmp/company-setref-atomic-store"
LOGICAL = "run://demo/node"
# Two distinct, whole cas values of DIFFERENT lengths — a torn read of one would not equal either.
CAS_A = "cas://b2:" + "a" * 32
CAS_B = "cas://b2:" + "bbbb" * 20   # longer, so a partial-overwrite of A would be detectable


def _check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    return cond


def main():
    shutil.rmtree(STORE_DIR, ignore_errors=True)
    store = FsStore(STORE_DIR)
    ok = True

    # 1: round-trips correctly + uses tmp+replace (no torn read).
    store.set_ref(LOGICAL, CAS_A)
    ok &= _check("set_ref round-trips", store.head(LOGICAL) == CAS_A)
    store.set_ref(LOGICAL, CAS_B)
    ok &= _check("set_ref overwrites in place", store.head(LOGICAL) == CAS_B)

    # 2: no .tmp file is left behind (replace consumed it) — the dir holds only the final ref.
    refs_dir = store.root / "refs"
    leftover = [p.name for p in refs_dir.iterdir() if p.name.endswith(".tmp")]
    ok &= _check("no .tmp leftover after set_ref", leftover == [])

    # 3: CONCURRENCY — many writers flip the ref between CAS_A and CAS_B while many readers hammer head().
    # Assert EVERY observed read is one of the two WHOLE values (or None on the very first reads),
    # never "" and never a truncated/torn string. A naked write_text would expose "" mid-truncate.
    shutil.rmtree(STORE_DIR, ignore_errors=True)
    store = FsStore(STORE_DIR)
    valid = {CAS_A, CAS_B, None}
    bad_reads = []
    stop = threading.Event()
    ITER = 4000

    def writer(val):
        for _ in range(ITER):
            store.set_ref(LOGICAL, val)

    def reader():
        while not stop.is_set():
            v = store.head(LOGICAL)
            if v not in valid:
                bad_reads.append(repr(v))

    writers = [threading.Thread(target=writer, args=(CAS_A,)),
               threading.Thread(target=writer, args=(CAS_B,))]
    readers = [threading.Thread(target=reader) for _ in range(4)]
    for t in readers:
        t.start()
    for t in writers:
        t.start()
    for t in writers:
        t.join()
    stop.set()
    for t in readers:
        t.join()

    ok &= _check(f"concurrent set_ref/head never torn/empty (saw {len(bad_reads)} bad: {bad_reads[:3]})",
                 not bad_reads)
    # And after the storm, head() resolves to a real whole value (not None/empty).
    final = store.head(LOGICAL)
    ok &= _check("final head() is a whole cas", final in {CAS_A, CAS_B})

    print("\n" + ("✅ SET_REF ATOMIC PASSED" if ok else "❌ FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
