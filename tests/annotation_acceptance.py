"""tests/annotation_acceptance.py — I6: annotation-at-an-address (the `annotation://` content branch).

NET-NEW: nothing today attaches a comment BY a `ui://` ADDRESS. `/api/resolve`'s comment *choice*
annotates an existing surfaced item by `id` (suite.py:3045) — NOT an arbitrary address. I6 adds a
SEPARATE address-keyed branch. This proves it end-to-end at the Suite level (`Suite.annotate` /
`Suite.annotations_at`, the logic the thin /api/annotate + /api/annotations bridge routes wrap —
reachability is grepped separately, the established split):

  1. ATTACH → RETRIEVE-BY-ADDRESS round-trip: a comment posted at `ui://…` is retrievable by that
     same address; comments at OTHER addresses don't leak into the answer (the address IS the key).
  2. MALFORMED address is REJECTED (fail loud) on BOTH write and read — the S0 grammar gate; the
     store never persists a junk key, and a read on a bad address never silently returns [].
  3. PERSISTENCE SURVIVES A RELOAD: a SECOND Suite built over the SAME store root reads the first
     Suite's annotations — proving on-disk persistence, not an in-memory cache.
  4. SEPARATION: annotate writes its OWN annotations.jsonl, NOT chat.jsonl (I2/I7's lane) and NOT
     the surfaced inbox (I2 act path) — I6 is a parallel branch, the I2/I7 paths stay untouched.
  5. FAIL LOUD on empty text (no silent no-op — AGENTS.md rule 4).

COMPANY_TEST_RUN is set for inbox-hygiene parity with the sibling suites.
"""
import os, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def expect_raises(label, fn):
    global PASS
    try:
        fn()
    except Exception:
        PASS += 1
        print(f"  ok  {label}")
        return
    assert False, f"FAIL (did not raise): {label}"


store_dir = tempfile.mkdtemp(prefix="annotation-test-")
try:
    root = os.path.join(store_dir, "store")
    store = FsStore(root)
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    check("Suite.annotate exists (the address-keyed annotation entry)",
          hasattr(suite, "annotate") and callable(suite.annotate))
    check("Suite.annotations_at exists (the address-keyed retrieval)",
          hasattr(suite, "annotations_at") and callable(suite.annotations_at))

    # =====================================================================================
    # 1. ATTACH → RETRIEVE-BY-ADDRESS round-trip.
    # =====================================================================================
    A1 = "ui://inbox/coa"
    A2 = "ui://chrome/inbox"
    rec = suite.annotate(A1, "this lane is too loud")
    check("annotate returns a persisted record stamped with the address",
          rec.get("address") == A1 and rec.get("text") == "this lane is too loud")
    check("the record is stamped with a ts (feeds R2's recency/decay)", bool(rec.get("ts")))
    check("the record is marked kind=annotation (the annotation:// branch)",
          rec.get("kind") == "annotation")

    got = suite.annotations_at(A1)
    check("retrieve-by-address returns the comment posted at that address",
          len(got) == 1 and got[0]["text"] == "this lane is too loud")

    # a SECOND comment at the SAME address accrues a THREAD (append-only, not last-writer-wins)
    suite.annotate(A1, "second thought")
    got = suite.annotations_at(A1)
    check("a second comment at the same address accrues a thread (append-only)",
          len(got) == 2 and got[0]["text"] == "this lane is too loud" and got[1]["text"] == "second thought")

    # an address with NO comments returns [] (a clean, non-leaking read)
    check("an address with no annotations returns []", suite.annotations_at(A2) == [])

    # a comment at A2 does NOT leak into A1's thread (the address IS the key)
    suite.annotate(A2, "comment elsewhere")
    check("a comment at a DIFFERENT address does not leak into the first address's thread",
          len(suite.annotations_at(A1)) == 2 and len(suite.annotations_at(A2)) == 1)

    # the live grammar form parses too (kind-form ui://chrome/<id> + a /@state suffix)
    A3 = "ui://canvas/node-7/@selected"
    suite.annotate(A3, "stateful locus")
    check("an address carrying a /@state suffix is a valid locus (S0 grammar)",
          len(suite.annotations_at(A3)) == 1)

    # =====================================================================================
    # 2. MALFORMED address REJECTED (fail loud) on BOTH write and read — the S0 gate.
    # =====================================================================================
    expect_raises("a malformed (non-ui://) address is REJECTED on annotate (S0 gate)",
                  lambda: suite.annotate("inbox/coa", "x"))
    expect_raises("a code:// address is REJECTED on annotate (only ui:// loci)",
                  lambda: suite.annotate("code://runtime/suite.py", "x"))
    expect_raises("a bare ui:// with no segments is REJECTED on annotate",
                  lambda: suite.annotate("ui://", "x"))
    expect_raises("a malformed address is REJECTED on annotations_at too (never silent [])",
                  lambda: suite.annotations_at("not-an-address"))

    # the rejected writes persisted NOTHING (the store never got a junk key)
    check("a rejected write persisted nothing (store never saw the junk key)",
          suite.store.annotations_for("inbox/coa") == []
          and suite.store.annotations_for("code://runtime/suite.py") == [])

    # =====================================================================================
    # 5. FAIL LOUD on empty text (no silent no-op).
    # =====================================================================================
    expect_raises("empty text is REJECTED (fail loud — no silent no-op)",
                  lambda: suite.annotate(A1, ""))
    expect_raises("whitespace-only text is REJECTED (fail loud)",
                  lambda: suite.annotate(A1, "   "))
    check("the failed empty-text writes did NOT grow the thread",
          len(suite.annotations_at(A1)) == 2)

    # =====================================================================================
    # 4. SEPARATION: I6 is a parallel branch — chat.jsonl (I2/I7) + the inbox (I2 act) untouched.
    # =====================================================================================
    check("annotate wrote NO chat history (chat.jsonl is I2/I7's lane, not I6's)",
          suite.chat_history(200) == [])
    check("annotate surfaced NO inbox item (the I2 act path is untouched)",
          suite.list_surfaced() == [])
    check("annotations.jsonl exists on disk (its OWN file, separate from chat.jsonl)",
          os.path.exists(os.path.join(root, "annotations.jsonl")))

    # =====================================================================================
    # 3. PERSISTENCE SURVIVES A RELOAD: a SECOND Suite over the SAME root reads the writes.
    # =====================================================================================
    store2 = FsStore(root)                       # fresh store object, SAME on-disk root
    reg2 = NodeRegistry(); reg2.discover([NODES])
    suite2 = Suite(store2, reg2, nodes_dir=NODES)
    reloaded = suite2.annotations_at(A1)
    check("a SECOND Suite over the same store root reads the prior Suite's annotations (on-disk)",
          len(reloaded) == 2 and reloaded[0]["text"] == "this lane is too loud")
    check("the reloaded thread carries the address key + ts (intact across reload)",
          reloaded[0]["address"] == A1 and bool(reloaded[0]["ts"]))

    print(f"\nALL {PASS} CHECKS PASS — I6 annotation-at-an-address: attach→retrieve-by-address "
          "round-trip, malformed rejected (write+read), persists across reload, I2/I7 paths untouched")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
