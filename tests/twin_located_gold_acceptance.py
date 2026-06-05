"""tests/twin_located_gold_acceptance.py — L4: the twin's LOCATED gold label (§21.7#7).

§21.7#7: an addressed comment (an I6 annotation attached at a `ui://` address, via the I5
per-click classifier) IS the twin's *located* gold label. The pipe already exists end-to-end:
`append_chat` is an open record (`rec = {"ts", **turn}`, fs_store.py:357) and `training_signal`
returns the WHOLE turn dict (gold + operator-sourced + echo-guarded, suite.py:868-878) — so an
`address` field rides through both untouched (seams-rhm Seam 5, CONFIRM). L4 is near-free: it adds
ONE additive `append_chat` call at the I6 comment-ingest entry point. No new training pipeline.

THE DECISION (stated, and proven by the tests): the default lean — making `annotate()` ITSELF also
emit the gold turn — is IMPOSSIBLE: `annotation_acceptance.py:131-132` asserts `chat_history(200)==[]`
AFTER `suite.annotate(...)` (I6's SEPARATION preserve — annotate writes its OWN annotations.jsonl,
never chat.jsonl), and that test is a hard preserve, not editable. So L4 keeps `annotate()`
byte-for-byte PURE and emits the located-gold turn one layer UP, in the I5 router's ANNOTATE branch
(`Suite.route_click`, suite.py:1938-1991) — the REAL clicked-comment path (the per-click annotate
classifier). A clicked comment IS the twin's located gold by provenance; the leaf `annotate()` (and
the direct `/api/annotate` read/write API) stay a pure annotation branch (documented boundary).

This proves it end-to-end at the Suite level (`Suite.route_click` — the I5 entry the thin bridge
click-route wraps; reachability is grepped separately, the established split):

  1. A `ui://` click with text (NO verb) → route_click ANNOTATES → ALSO emits a gold/operator chat
     turn carrying that address (the located gold label). The annotation branch (I6) is unchanged.
  2. That located-gold turn appears in `training_signal` — grade gold, source operator, the address
     PRESENT and intact, the text intact (it rides the existing pipe, echo-guarded, automatic).
  3. PRESERVE — `training_signal`'s gold/operator/echo-guard filter is UNCHANGED (byte-for-byte):
     a twin/assistant addressed turn does NOT become gold (the echo-guard + source filter still
     fire); every returned turn is operator-gold. The address rides free; the filter is untouched.
  4. I6 SEPARATION still holds: `annotate()` called DIRECTLY still writes NO chat history (the leaf
     is pure) — only the I5 router emits the located gold. (Guards the chosen placement.)
  5. A non-operator comment can NOT launder into gold: a route with source!="operator" emits a
     working/twin turn (role-tied via _provenance_*), so it never trains the twin (F4 guard).

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


store_dir = tempfile.mkdtemp(prefix="twin-located-gold-test-")
try:
    root = os.path.join(store_dir, "store")
    store = FsStore(root)
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    g = suite.list_graphs()[0] if suite.list_graphs() else "default"

    check("Suite.ingest_comment exists (the WIRED comment-ingest entry — what /api/annotate calls)",
          hasattr(suite, "ingest_comment") and callable(suite.ingest_comment))
    check("Suite.route_click exists (the I5 per-click classifier — composes ingest_comment)",
          hasattr(suite, "route_click") and callable(suite.route_click))

    # =====================================================================================
    # 1. The WIRED entry: ingest_comment (what POST /api/annotate calls in production) records the
    #    I6 comment AND emits the located gold turn. (Drive the REAL production path, not just the
    #    router — the located-gold MUST fire on the path a real operator's click takes.)
    # =====================================================================================
    A1 = "ui://inbox/coa"
    rec = suite.ingest_comment(A1, "this lane decides too aggressively")
    check("ingest_comment records the I6 annotation (the comment is attached at the address)",
          rec.get("text") == "this lane decides too aggressively" and rec.get("address") == A1)
    check("ingest_comment leaves the I6 annotation thread intact (the comment is retrievable)",
          len(suite.annotations_at(A1)) == 1)

    # the located gold label: a gold/operator chat turn carrying that SAME address now exists
    hist = suite.chat_history(200)
    located = [t for t in hist if t.get("address") == A1
               and t.get("text") == "this lane decides too aggressively"]
    check("an addressed comment emitted a chat turn at that ui:// address (the located label)",
          len(located) == 1)
    check("that turn is GOLD + OPERATOR-sourced (operator comment = gold by provenance)",
          located[0].get("grade") == "gold" and located[0].get("source") == "operator")
    check("that turn is a 'user' role turn (an ordinary chat turn that ALSO carries an address)",
          located[0].get("role") == "user")

    # =====================================================================================
    # 2. It appears in training_signal as a LOCATED gold label (the address rides through).
    # =====================================================================================
    sig = suite.training_signal()
    located_sig = [t for t in sig if t.get("address") == A1
                   and t.get("text") == "this lane decides too aggressively"]
    check("the addressed comment appears in training_signal (rides the existing pipe, automatic)",
          len(located_sig) == 1)
    check("inside training_signal it is grade=gold, source=operator (a located gold LABEL)",
          located_sig[0].get("grade") == "gold" and located_sig[0].get("source") == "operator")
    check("the ADDRESS is present + intact inside training_signal (located, not just gold)",
          located_sig[0].get("address") == A1)

    # =====================================================================================
    # 1b. The I5 classifier (route_click) COMPOSES ingest_comment — so a ui:// click with no verb
    #     ALSO produces located gold (the MCP/classifier path, same single-source entry).
    # =====================================================================================
    AR = "ui://canvas/node-7/@selected"
    out = suite.route_click(AR, g, text="routed clicked comment is located gold too")
    check("a ui:// click (no verb) ROUTED to ANNOTATE (face=='annotate')", out.get("face") == "annotate")
    sig_r = suite.training_signal()
    check("the I5-routed clicked comment is a located gold label too (route_click composes ingest)",
          any(t.get("address") == AR and t.get("grade") == "gold" and t.get("source") == "operator"
              and t.get("text") == "routed clicked comment is located gold too" for t in sig_r))

    # =====================================================================================
    # 1c. REACHABILITY: the WIRED production entry — POST /api/annotate in bridge.py calls
    #     ingest_comment (NOT the pure annotate leaf), so a real operator's click fires located gold.
    # =====================================================================================
    bridge_src = open(os.path.join(ROOT, "runtime", "bridge.py"), encoding="utf-8").read()
    # SAME-HANDLER check (not a loose anywhere-in-file match): slice the /api/annotate block (from its
    # marker to the next `elif self.path` route) and assert ingest_comment is dispatched INSIDE it AND
    # the pure annotate() leaf is NOT (so a regression to SUITE.annotate would FAIL this — it bites).
    assert '"/api/annotate"' in bridge_src, "FAIL: /api/annotate route missing from bridge.py"
    blk = bridge_src.split('"/api/annotate"', 1)[1].split("elif self.path", 1)[0]
    check("POST /api/annotate dispatches SUITE.ingest_comment INSIDE its handler (located-gold REACHABLE)",
          "SUITE.ingest_comment(" in blk)
    check("POST /api/annotate does NOT call the pure annotate() leaf (no regression to unreachable path)",
          "SUITE.annotate(" not in blk)

    # =====================================================================================
    # 3. PRESERVE — training_signal's gold/operator/echo-guard filter is UNCHANGED.
    #    A twin/assistant addressed turn does NOT become gold (the filter still fires).
    # =====================================================================================
    AP = "ui://chrome/chat"
    # an operator located comment via the wired entry (gold) vs a twin addressed turn (must be filtered).
    suite.ingest_comment(AP, "operator located gold for training")
    suite.store.append_chat({"role": "assistant", "text": "twin addressed turn never trains",
                             "address": AP, "source": "twin",
                             "grade": suite._provenance_grade("assistant")})
    sig2 = suite.training_signal()
    sig2_texts = {t.get("text") for t in sig2}
    check("the operator located-gold turn IS in training_signal (flows through unchanged)",
          "operator located gold for training" in sig2_texts)
    check("an addressed TWIN turn is FILTERED OUT of training_signal (echo-guard/source preserved)",
          "twin addressed turn never trains" not in sig2_texts)
    check("EVERY training_signal turn is operator-gold (the filter is byte-for-byte the same)",
          all(t.get("grade") == "gold" and t.get("source", "operator") != "twin" for t in sig2))

    # =====================================================================================
    # 4. I6 SEPARATION still holds — annotate() called DIRECTLY writes NO chat (the leaf is pure).
    #    This guards the CHOSEN placement (the located-gold lives in ingest_comment, NOT in the
    #    annotate leaf): annotation_acceptance's chat_history()==[] preserve survives because the
    #    leaf annotate() never emits chat — only ingest_comment (the wired entry) does.
    # =====================================================================================
    store_b = FsStore(os.path.join(store_dir, "store-b"))
    suite_b = Suite(store_b, reg, nodes_dir=NODES)
    suite_b.annotate("ui://inbox/coa", "a direct annotate — leaf is pure, no chat")
    check("annotate() called DIRECTLY writes NO chat history (I6 SEPARATION preserve intact)",
          suite_b.chat_history(200) == [])
    check("annotate() DIRECTLY still records the annotation (the leaf branch is unchanged)",
          len(suite_b.annotations_at("ui://inbox/coa")) == 1)

    # =====================================================================================
    # 5. A non-operator comment can NOT launder into gold (F4 guard — role-tied provenance).
    # =====================================================================================
    AN = "ui://chrome/inbox"
    suite_b.ingest_comment(AN, "a non-operator comment must not train", source="twin")
    hist_b = suite_b.chat_history(200)
    laundered = [t for t in hist_b if t.get("address") == AN]
    check("a source='twin' route emitted a turn (it is recorded)", len(laundered) == 1)
    check("that non-operator turn is NOT gold/operator (cannot launder into training signal)",
          laundered[0].get("grade") != "gold" or laundered[0].get("source") == "twin")
    sig_b = suite_b.training_signal()
    check("the non-operator comment is ABSENT from training_signal (F4 — never trains the twin)",
          all(t.get("text") != "a non-operator comment must not train" for t in sig_b))

    print(f"\nALL {PASS} CHECKS PASS — L4 twin located-gold: a ui:// clicked comment via the WIRED "
          "entry (ingest_comment — what POST /api/annotate calls; the I5 router composes it too) "
          "becomes a gold/operator chat turn carrying its address → a LOCATED gold label in "
          "training_signal (rides the existing append_chat→training_signal pipe, address intact); "
          "training_signal's gold/operator/echo-guard filter byte-for-byte preserved (twin turn "
          "filtered, no launder); annotate() leaf stays pure (I6 SEPARATION intact); located-gold "
          "REACHABLE in production (bridge /api/annotate → ingest_comment)")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
