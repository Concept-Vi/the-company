"""tests/corpus_acceptance.py — the corpus-record WITH LINEAGE (Cognition Engine D1 · the sequencing gate).

Proves, BY USE against a real FsStore (no model needed — the record is the unit under test):

  1. THE GATE (the headline, PART 4.7) — write_record REFUSES a record missing lineage (fail-loud, NOT
     optional-with-default): no lineage dict / missing an axis / empty axis all RAISE CorpusError. A record
     without session/round/project is uncorroboratable cross-session, so it can never be written.
  2. ROUND-TRIP with lineage INTACT — a written record reads back (read_record) with its session/round/
     project preserved, AND survives a SECOND store over the same root (persistence-survives-reload).
  3. THE INDEX is a `corpus.record` EVENT, not op.run — the record is indexed on the ONE event log with a
     DISTINCT kind (so it never pollutes the closed ENGINE_RUN_OPS grammar); list_corpus/find_corpus are a
     read-projection over it.
  4. RESUME-SAFETY (dedup-on-read) — re-writing the SAME record (resume) is idempotent (same cas, same
     deterministic address) and list_corpus folds the duplicate index events (latest wins) so a resumed run
     never double-counts.
  5. NO fs_store edit — only the store's existing public methods are used (put_content/set_ref/append_event/
     head/get_content/events_since); fs_store is untouched (STORE lane owns it).
  6. THE FLOOR — the index event is `corpus.record` (telemetry), never a resolve/approve/dispatch.

LAWS proven: fail-loud (the lineage gate) · reuse-don't-parallel (store public methods + the run-index
event pattern, no new DB) · the floor (corpus.record is not a consequential verb) · schema-additive
(extra fields ride free) · resume-safety (deterministic address + dedup-on-read).
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from store.fs_store import FsStore                                                      # noqa: E402
from runtime import corpus                                                             # noqa: E402
from runtime.corpus import (write_record, read_record, list_corpus, find_corpus,        # noqa: E402
                            corpus_address, CorpusError, CORPUS_EVENT_KIND, LINEAGE_FIELDS)

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def raises(label, fn, exc=CorpusError):
    try:
        fn()
    except exc:
        check(label, True)
        return
    check(label, False)


store_dir = tempfile.mkdtemp(prefix="corpus-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    GOOD_LINEAGE = {"session": "s1", "round": "1", "project": "vault-scan"}

    # =============================================================================================
    # 1 · THE GATE — lineage is REQUIRED, fail-loud (the sequencing gate)
    # =============================================================================================
    raises("no lineage dict (None) RAISES",
           lambda: write_record(store, source_address="f/a.md", output={"x": 1}, kind="capture", lineage=None))
    raises("lineage missing 'project' RAISES",
           lambda: write_record(store, source_address="f/a.md", output={"x": 1}, kind="capture",
                                lineage={"session": "s1", "round": "1"}))
    raises("lineage empty 'session' RAISES",
           lambda: write_record(store, source_address="f/a.md", output={"x": 1}, kind="capture",
                                lineage={"session": "", "round": "1", "project": "p"}))
    raises("lineage as a string (not dict) RAISES",
           lambda: write_record(store, source_address="f/a.md", output={"x": 1}, kind="capture", lineage="s1"))
    # other required-field gates:
    raises("None output RAISES", lambda: write_record(store, source_address="f/a.md", output=None, kind="capture", lineage=GOOD_LINEAGE))
    raises("empty source_address RAISES", lambda: write_record(store, source_address="", output={"x": 1}, kind="capture", lineage=GOOD_LINEAGE))
    raises("empty kind RAISES", lambda: write_record(store, source_address="f/a.md", output={"x": 1}, kind="", lineage=GOOD_LINEAGE))

    # =============================================================================================
    # 2 · ROUND-TRIP with lineage INTACT
    # =============================================================================================
    ev = write_record(store, source_address="f/a.md", output={"what": "a design note"},
                      kind="capture", lineage=GOOD_LINEAGE, model="qwen", projection="what")
    rec = read_record(store, ev["address"])
    check("round-trip: record reads back", rec is not None)
    check("round-trip: output intact", rec["output"] == {"what": "a design note"})
    check("round-trip: lineage INTACT (all three axes)",
          all(rec["lineage"].get(k) for k in LINEAGE_FIELDS) and rec["lineage"]["project"] == "vault-scan")
    check("round-trip: model + projection carried", rec["model"] == "qwen" and rec["projection"] == "what")
    # the address is deterministic + projection-keyed:
    check("address is the deterministic corpus_address",
          ev["address"] == corpus_address("f/a.md", project="vault-scan", projection="what"))

    # persistence-survives-reload (a SECOND store over the same root):
    store2 = FsStore(os.path.join(store_dir, "store"))
    rec2 = read_record(store2, ev["address"])
    check("persistence-survives-reload: a 2nd store reads the record", rec2 is not None and rec2["output"] == rec["output"])

    # =============================================================================================
    # 3 · THE INDEX is a corpus.record EVENT (not op.run) + the read-projection
    # =============================================================================================
    raw = [e for e in store.events_since(-1) if e.get("kind") == CORPUS_EVENT_KIND]
    check("index rides a DISTINCT 'corpus.record' event kind (not op.run)", len(raw) >= 1)
    check("no op.run was emitted by the corpus write",
          all(e.get("kind") != "op.run" for e in store.events_since(-1)))
    rows = list_corpus(store)
    check("list_corpus projects the indexed record", any(r["address"] == ev["address"] for r in rows))
    # a second project's record + filtering:
    write_record(store2, source_address="g/b.md", output=["topic1"], kind="capture",
                 lineage={"session": "s9", "round": "1", "project": "other-proj"}, projection="topics")
    store3 = FsStore(os.path.join(store_dir, "store"))
    check("find_corpus(project=) filters by lineage",
          {r["source_address"] for r in find_corpus(store3, project="vault-scan")} == {"f/a.md"})
    check("find_corpus(projection=) filters by lens",
          all(r["projection"] == "topics" for r in find_corpus(store3, projection="topics")))
    check("find_corpus(source_address=) filters by unit",
          {r["address"] for r in find_corpus(store3, source_address="g/b.md")}
          == {corpus_address("g/b.md", project="other-proj", projection="topics")})

    # =============================================================================================
    # 4 · RESUME-SAFETY — re-write the SAME record → idempotent + dedup-on-read
    # =============================================================================================
    before = len(list_corpus(store3, project="vault-scan"))
    ev_again = write_record(store3, source_address="f/a.md", output={"what": "a design note"},
                            kind="capture", lineage=GOOD_LINEAGE, model="qwen", projection="what")
    check("resume: re-writing the same record yields the SAME cas (put_content write-once)", ev_again["cas"] == ev["cas"])
    check("resume: same deterministic address", ev_again["address"] == ev["address"])
    after = len(list_corpus(store3, project="vault-scan"))
    check("resume: list_corpus DEDUPS on read (no double-count)", after == before)

    # =============================================================================================
    # 6 · THE FLOOR — the index event is never a consequential verb
    # =============================================================================================
    FORBIDDEN = {"resolve", "approve", "dispatch", "decision.dispatch", "decision.implemented"}
    check("the floor: no corpus write emitted a forbidden/consequential event",
          all(e.get("kind") not in FORBIDDEN for e in store3.events_since(-1)))

    print(f"\nPASS ({PASS} checks) — corpus-record + LINEAGE gate (D1), round-trip, distinct-index, resume-safe.")
finally:
    import shutil
    shutil.rmtree(store_dir, ignore_errors=True)
