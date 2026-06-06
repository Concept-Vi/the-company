"""tests/addr_chat_acceptance.py — I7: chat-thread at an address (the `chat://` content branch).

§21.1 names FOUR things you attach by clicking: comments / communications / commands / **chats**.
The criteria covered annotation (I6), command (I2/I3) — `chat://` (a chat thread attached to an
element) was the dropped 4th (fidelity ISSUE-1). I7 rides the EXISTING open `append_chat` path
(`rec = {"ts", **turn}`, fs_store.py:357) stamped with one additive `address` field — NOT a separate
chat store (a parallel store would violate one-source; the existing `chat.jsonl` open-record handles
it additively). This proves it end-to-end at the Suite level (`Suite.attach_chat` / `Suite.chats_at`,
the logic the thin bridge routes wrap — reachability is grepped separately, the established split):

  1. ATTACH → RETRIEVE-BY-ADDRESS round-trip: a turn posted at `ui://…` is retrievable by that same
     address; turns at OTHER addresses (and unaddressed ordinary chat) don't leak into the answer
     (the address IS the key — ISOLATION).
  2. MALFORMED address is REJECTED (fail loud) on BOTH write and read — the S0 grammar gate; the
     store never persists a junk key, and a read on a bad address never silently returns [].
  3. ONE-SOURCE (the INVERSE of I6): the addressed turn lands in chat.jsonl — the SAME lane as the
     ordinary RHM conversation — and creates NO separate file. (I6 asserted the opposite; this is
     what proves I7 rode the open append_chat path, not a parallel store.)
  4. PRESERVE — training_signal's gold/operator/echo-guard filter (suite.py:856-866) is UNCHANGED:
     an addressed OPERATOR turn flows through it untouched (it IS in the stream, with its address
     intact), while an addressed TWIN turn is filtered out exactly as before. The address rides free.
  5. PERSISTENCE SURVIVES A RELOAD: a SECOND Suite built over the SAME store root reads the first
     Suite's addressed turns — proving on-disk persistence, not an in-memory cache.
  6. FAIL LOUD on empty text (no silent no-op — AGENTS.md rule 4).

COMPANY_TEST_RUN is set for inbox-hygiene parity with the sibling suites.
"""
import os, sys, json, tempfile, shutil

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


store_dir = tempfile.mkdtemp(prefix="addr-chat-test-")
try:
    root = os.path.join(store_dir, "store")
    store = FsStore(root)
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    check("Suite.attach_chat exists (the address-keyed chat-attach entry)",
          hasattr(suite, "attach_chat") and callable(suite.attach_chat))
    check("Suite.chats_at exists (the address-keyed chat retrieval)",
          hasattr(suite, "chats_at") and callable(suite.chats_at))

    # =====================================================================================
    # 1. ATTACH → RETRIEVE-BY-ADDRESS round-trip + ISOLATION.
    # =====================================================================================
    A1 = "ui://inbox/coa"
    A2 = "ui://chrome/inbox"
    rec = suite.attach_chat(A1, "what does this lane decide?")
    check("attach_chat returns a persisted turn stamped with the address",
          rec.get("address") == A1 and rec.get("text") == "what does this lane decide?")
    check("the turn is stamped with a ts (feeds R2's recency/decay)", bool(rec.get("ts")))
    check("the turn carries a role (an ordinary chat turn that ALSO carries an address)",
          rec.get("role") == "user")
    check("the turn carries source + grade (the echo-guard tags — store constitution 'Never')",
          rec.get("source") == "operator" and rec.get("grade") == "gold")

    got = suite.chats_at(A1)
    check("retrieve-by-address returns the turn posted at that address",
          len(got) == 1 and got[0]["text"] == "what does this lane decide?")

    # a SECOND turn at the SAME address accrues a THREAD (append-only)
    suite.attach_chat(A1, "second turn at the same locus")
    got = suite.chats_at(A1)
    check("a second turn at the same address accrues a thread (append-only)",
          len(got) == 2 and got[0]["text"] == "what does this lane decide?"
          and got[1]["text"] == "second turn at the same locus")

    # an address with NO turns returns [] (a clean, non-leaking read)
    check("an address with no attached chat returns []", suite.chats_at(A2) == [])

    # a turn at A2 does NOT leak into A1's thread; ordinary (unaddressed) chat doesn't either
    suite.attach_chat(A2, "turn at a different locus")
    suite.store.append_chat({"role": "user", "text": "ordinary unaddressed chat",
                             "grade": "gold", "source": "operator"})
    check("a turn at a DIFFERENT address does not leak into the first address's thread (ISOLATION)",
          len(suite.chats_at(A1)) == 2 and len(suite.chats_at(A2)) == 1)
    check("ordinary unaddressed chat is NOT returned for an address (ISOLATION)",
          all(t["text"] != "ordinary unaddressed chat" for t in suite.chats_at(A1)))

    # the live grammar form parses too (a /@state suffix)
    A3 = "ui://canvas/node-7/@selected"
    suite.attach_chat(A3, "stateful locus")
    check("an address carrying a /@state suffix is a valid locus (S0 grammar)",
          len(suite.chats_at(A3)) == 1)

    # =====================================================================================
    # 2. MALFORMED address REJECTED (fail loud) on BOTH write and read — the S0 gate.
    # =====================================================================================
    expect_raises("a malformed (non-ui://) address is REJECTED on attach_chat (S0 gate)",
                  lambda: suite.attach_chat("inbox/coa", "x"))
    expect_raises("a code:// address is REJECTED on attach_chat (only ui:// loci)",
                  lambda: suite.attach_chat("code://runtime/suite.py", "x"))
    expect_raises("a bare ui:// with no segments is REJECTED on attach_chat",
                  lambda: suite.attach_chat("ui://", "x"))
    expect_raises("a malformed address is REJECTED on chats_at too (never silent [])",
                  lambda: suite.chats_at("not-an-address"))

    # =====================================================================================
    # 6. FAIL LOUD on empty text (no silent no-op).
    # =====================================================================================
    expect_raises("empty text is REJECTED (fail loud — no silent no-op)",
                  lambda: suite.attach_chat(A1, ""))
    expect_raises("whitespace-only text is REJECTED (fail loud)",
                  lambda: suite.attach_chat(A1, "   "))
    check("the failed empty-text writes did NOT grow the thread",
          len(suite.chats_at(A1)) == 2)

    # =====================================================================================
    # 3. ONE-SOURCE (the INVERSE of I6): rode chat.jsonl, NO separate file.
    # =====================================================================================
    check("the addressed turns landed in chat.jsonl (the SAME lane as ordinary RHM chat)",
          os.path.exists(os.path.join(root, "chat.jsonl")))
    check("attach_chat created NO separate addressed-chat file (one-source — rode append_chat)",
          not os.path.exists(os.path.join(root, "addr_chat.jsonl"))
          and not os.path.exists(os.path.join(root, "chats.jsonl")))
    # the addressed turns ARE first-class members of chat_history (not a side channel)
    hist = suite.chat_history(200)
    check("addressed turns appear in chat_history (first-class stream members, one-source)",
          any(t.get("address") == A1 for t in hist))

    # =====================================================================================
    # 4. PRESERVE — training_signal's gold/operator/echo-guard filter is UNCHANGED.
    #    An addressed OPERATOR turn flows through untouched (address intact); an addressed
    #    TWIN turn is filtered out exactly as before. Distinct texts so the echo-guard
    #    (twin-text match) doesn't confound the source/grade filter.
    # =====================================================================================
    AP = "ui://chrome/chat"
    suite.attach_chat(AP, "operator-gold addressed turn for training", role="user")
    suite.attach_chat(AP, "twin-working addressed turn never trains", role="assistant")
    sig = suite.training_signal()
    sig_texts = {t.get("text") for t in sig}
    check("an addressed OPERATOR-gold turn IS in training_signal (flows through unchanged)",
          "operator-gold addressed turn for training" in sig_texts)
    check("the addressed operator turn keeps its address inside training_signal (rides free)",
          any(t.get("address") == AP and t.get("text") == "operator-gold addressed turn for training"
              for t in sig))
    check("an addressed TWIN turn is FILTERED OUT of training_signal (echo-guard preserved)",
          "twin-working addressed turn never trains" not in sig_texts)
    check("every training_signal turn is operator-gold (the filter is byte-for-byte the same)",
          all(t.get("grade") == "gold" and t.get("source", "operator") != "twin" for t in sig))

    # =====================================================================================
    # 5. PERSISTENCE SURVIVES A RELOAD: a SECOND Suite over the SAME root reads the writes.
    # =====================================================================================
    store2 = FsStore(root)                       # fresh store object, SAME on-disk root
    reg2 = NodeRegistry(); reg2.discover([NODES])
    suite2 = Suite(store2, reg2, nodes_dir=NODES)
    reloaded = suite2.chats_at(A1)
    check("a SECOND Suite over the same store root reads the prior Suite's addressed chat (on-disk)",
          len(reloaded) == 2 and reloaded[0]["text"] == "what does this lane decide?")
    check("the reloaded thread carries the address key + ts (intact across reload)",
          reloaded[0]["address"] == A1 and bool(reloaded[0]["ts"]))

    print(f"\nALL {PASS} CHECKS PASS — I7 chat-at-an-address: attach→retrieve-by-address round-trip "
          "+ isolation, malformed rejected (write+read), rode the open append_chat (one-source, no "
          "separate file), training_signal filter preserved (operator-gold rides / twin filtered), "
          "persists across reload")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
