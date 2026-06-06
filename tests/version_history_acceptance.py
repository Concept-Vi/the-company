"""Acceptance — L6 · live-history / versions at an address (§21.7#6).

A portal shows the CURRENT ref live (head(ref)), but set_ref OVERWRITES and there was NO
ref→version-history index — though the old versions' CAS bytes SURVIVE (put_content is
write-once, never deletes). L6 adds the index + the read path:

  1. on each set_ref, APPEND (ts, cas) to a per-ref version-history index (the cas bytes
     already survive — the index just MAPS a ref to its prior cas hashes; no bytes copied).
  2. ref_history(ref) returns the ordered (ts, cas) trail; the LIVE head(ref) is unchanged.
  3. a prior version's bytes are STILL fetchable by its cas via the existing content store.

PRESERVES (HARD): set_ref's current-ref overwrite + atomic os.replace; head(ref) live resolve;
put_content write-once CAS; lineage() (provenance, not temporal) untouched.

DECISION (stated in the report): versioning is ALL refs (every set_ref appends — cheap, just
(ts,cas)); NO write cap (append-only, lock-free like append_annotation), the READ is bounded
(ref_history(ref, limit=...)). Consecutive identical cas entries are legitimate (history records
WRITES, not distinct values).

Run: /home/tim/company/.venv/bin/python tests/version_history_acceptance.py
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore   # noqa: E402

STORE_DIR = "/tmp/company-version-history-store"
LOGICAL = "run://demo/node"
OTHER = "run://demo/other"


def _check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    return cond


def main():
    shutil.rmtree(STORE_DIR, ignore_errors=True)
    store = FsStore(STORE_DIR)
    ok = True

    # ----- set value A, then value B at the SAME address -----
    cas_a = store.put_content({"v": "A"})
    cas_b = store.put_content({"v": "B"})
    store.set_ref(LOGICAL, cas_a)
    store.set_ref(LOGICAL, cas_b)

    # 1: ref_history returns BOTH (ts, cas_a) and (ts, cas_b) IN ORDER (oldest-first).
    hist = store.ref_history(LOGICAL)
    ok &= _check("ref_history returns 2 entries", len(hist) == 2)
    if len(hist) == 2:
        ok &= _check("entry 0 is cas_A", hist[0].get("cas") == cas_a)
        ok &= _check("entry 1 is cas_B (chronological)", hist[1].get("cas") == cas_b)
        ok &= _check("each entry carries a ts", all(e.get("ts") for e in hist))

    # 2: head(ref) STILL returns B — current-value-live PRESERVED (overwrite path intact).
    ok &= _check("head(ref) still returns the current value B", store.head(LOGICAL) == cas_b)

    # 3: a PRIOR version's bytes are still fetchable by its cas (CAS survival — the whole point).
    ok &= _check("prior version cas_A still fetchable from the content store",
                 store.get_content(cas_a) == {"v": "A"})
    ok &= _check("current version cas_B fetchable too", store.get_content(cas_b) == {"v": "B"})

    # 4: the atomic OVERWRITE of the live ref still works — head is always the LAST write, no torn read.
    cas_c = store.put_content({"v": "C"})
    store.set_ref(LOGICAL, cas_c)
    ok &= _check("head(ref) is the last write (C) after a 3rd set_ref", store.head(LOGICAL) == cas_c)
    ok &= _check("ref_history now has 3 entries, C last",
                 len(store.ref_history(LOGICAL)) == 3
                 and store.ref_history(LOGICAL)[-1].get("cas") == cas_c)
    # no .tmp leftover (the atomic replace consumed it — the preserve)
    leftover = [p.name for p in (store.root / "refs").iterdir() if p.name.endswith(".tmp")]
    ok &= _check("no .tmp leftover (atomic replace preserved)", leftover == [])

    # 5: a ref with NO history returns an HONEST EMPTY (not a crash, not a silent wrong value).
    empty = store.ref_history(OTHER)
    ok &= _check("a ref never written → ref_history returns [] (honest empty, no crash)", empty == [])

    # 6: ISOLATION — OTHER's history does not bleed into LOGICAL's (per-ref index).
    cas_o = store.put_content({"v": "O"})
    store.set_ref(OTHER, cas_o)
    ok &= _check("OTHER's history is its own single entry",
                 [e.get("cas") for e in store.ref_history(OTHER)] == [cas_o])
    ok &= _check("LOGICAL's history unaffected by OTHER's write",
                 len(store.ref_history(LOGICAL)) == 3)

    # 7: bounded READ — ref_history(ref, limit=N) returns the last N (newest), order preserved.
    last2 = store.ref_history(LOGICAL, limit=2)
    ok &= _check("ref_history(limit=2) returns the last 2 entries",
                 [e.get("cas") for e in last2] == [cas_b, cas_c])

    # 8: persistence-survives-reload — a SECOND store over the same root sees the prior store's index.
    store2 = FsStore(STORE_DIR)
    ok &= _check("a second store over the same root reads the persisted history",
                 len(store2.ref_history(LOGICAL)) == 3)

    # 9: consecutive IDENTICAL cas is a legitimate version entry (history records WRITES, not values).
    store.set_ref(LOGICAL, cas_c)   # re-write the same value
    ok &= _check("re-writing the same cas appends another history entry (records writes)",
                 len(store.ref_history(LOGICAL)) == 4)
    ok &= _check("head still resolves to that value", store.head(LOGICAL) == cas_c)

    # 10: CONCURRENCY — the version-index append runs INSIDE set_ref (the scheduler's hot path). Fire many
    # concurrent set_refs at ONE address and assert EVERY history line parses + the count is EXACT (no torn
    # append swallowed/duplicated a line, no append raised into the caller). This is the one NEW behaviour on
    # the preserve-critical hot path — proven by execution, not inferred from the append_annotation analogy.
    import threading
    shutil.rmtree(STORE_DIR, ignore_errors=True)
    store = FsStore(STORE_DIR)
    N_THREADS, M_WRITES = 8, 500
    cas_x = store.put_content({"v": "X"})

    def storm():
        for _ in range(M_WRITES):
            store.set_ref(LOGICAL, cas_x)

    threads = [threading.Thread(target=storm) for _ in range(N_THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # ref_history parses the WHOLE file — a torn line would raise here (json.loads). Count must be exact.
    full = store.ref_history(LOGICAL)
    ok &= _check(f"concurrent set_ref → every history line parses + count exact "
                 f"(got {len(full)}, want {N_THREADS * M_WRITES})",
                 len(full) == N_THREADS * M_WRITES)
    ok &= _check("head still resolves after the storm (set_ref preserved)", store.head(LOGICAL) == cas_x)

    print("\n" + ("✅ VERSION HISTORY PASSED" if ok else "❌ FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
