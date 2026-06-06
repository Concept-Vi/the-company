"""tests/addr_context_acceptance.py — R2 · address-keyed context resolution (the keystone).

WHAT R2 IS (Implementation Guide R2 + seams-rhm.md Seam 4 + §21.4#3/§21.10):
today retrieval is KEYWORD-keyed — `_consult_terms` extracts salient terms, `_retrieve_for_consult`
scans the repo by term-hit count, bounded only by `CONSULT_CAP=40000` (the consult context-flood is
the RHM's worst wound, §21.4#3). R2 makes THE ADDRESS THE OPERATOR IS AT (R1's `current_locus()`) the
retrieval key:

  1. GATHER info attached to the locus (I6 annotations via `annotations_at`, I7 chats via `chats_at`,
     addressed events) — AND its ancestors in the address tree, so proximity is a LIVE dimension
     (a locus-exact item outranks a parent-address item), not a dead term.
  2. RE-KEY consult keyword→address: at a locus the address→relevant-slice map is primary; the keyword
     scan REMAINS as a fallback (no locus / no addressed match).
  3. BOUND it with a relevance/recency decay so it CANNOT flood the window (THE critical requirement —
     without decay, auto-resolve recreates the 396k-char stuffing R2 exists to kill). Per item:
       recency  = exp(-LAMBDA * (now - ts))                  # newer = heavier
       proximity = address_tree_distance(locus, it.address)  # closer in the tree = heavier
       pin_bonus = PIN_WEIGHT if it.pinned else 0.0
       score = recency * (1/(1 + PROXIMITY_WEIGHT*proximity)) + pin_bonus
     sort desc; budget_cap(items, BUDGET) — cap the window, NEVER stuff.
  4. INJECT the resolved, bounded slice into `_chat_context` at the locus.

THE CAP IS THE KEYSTONE: "bounded" (≤ total) alone false-passes — the absence of the lowest-scored
item is what PROVES the cap holds. This test attaches MANY items (more than the budget) and asserts the
injected block is ≤ BUDGET AND the lowest-scored item is ABSENT AND the highest-scored win.

PRESERVE (HARD CONSTRAINTS):
  - `_chat_context`'s other injected blocks (models/modes/verbs/inbox/graphs/panels) stay present.
  - the I1 INDICATING block + R1 locus set-point stay intact.
  - the keyword consult fallback (`_retrieve_for_consult`) still serves with no locus / no match.

These all run WITHOUT a live model — `_chat_context`, `_retrieve_for_consult`, and the pure decay
helpers are deterministic; only `chat()`/`consult()` hit fabric, which we never call here.

COMPANY_TEST_RUN is set for inbox-hygiene parity with the sibling suites.
"""
import os, sys, tempfile, shutil, math
from datetime import datetime, timezone, timedelta

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


# Real registered element/region addresses (S1 UI_REGISTRY). The locus + an ancestor of it, so we can
# prove proximity end-to-end (a locus-exact item outranks a parent-address item).
LOCUS = "ui://chrome/inbox"           # the operator's locus
PARENT = "ui://chrome"                # an ancestor in the address tree (distance 1 from LOCUS)

store_dir = tempfile.mkdtemp(prefix="addr-context-test-")
try:
    root = os.path.join(store_dir, "store")
    store = FsStore(root)
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    g = "addrctx"
    suite.create_node(g, "constant", config={"value": "hello"}, node_id="c")
    suite.create_node(g, "uppercase", node_id="u")
    suite.connect(g, "c", "value", "u", "text")

    # ============================================================================================
    # PART 1 — the pure decay helpers (deterministic; the cap proof lives here too)
    # ============================================================================================
    check("address_tree_distance exists", hasattr(suite, "address_tree_distance"))
    check("exact match → distance 0", suite.address_tree_distance(LOCUS, LOCUS) == 0)
    check("parent → distance 1", suite.address_tree_distance(LOCUS, PARENT) == 1)
    check("sibling → distance 2",
          suite.address_tree_distance("ui://chrome/inbox", "ui://chrome/activity") == 2)
    check("deeper child → distance 1",
          suite.address_tree_distance("ui://chrome", "ui://chrome/inbox") == 1)

    # the weights/budget are NAMED config constants (D2-configurable), not bare literals
    for const in ("R2_LAMBDA", "R2_PROXIMITY_WEIGHT", "R2_PIN_WEIGHT", "R2_BUDGET"):
        check(f"weight/budget constant {const} is a named class constant", hasattr(suite, const))

    # --- the scoring + cap, on SYNTHETIC items (proves all four dimensions deterministically) ---
    now = datetime.now(timezone.utc)
    def iso(dt): return dt.isoformat()
    # recency: a recent item outscores an old one (same address, unpinned)
    recent = {"text": "R", "address": LOCUS, "ts": iso(now - timedelta(seconds=1)), "kind": "annotation"}
    old = {"text": "O", "address": LOCUS, "ts": iso(now - timedelta(days=30)), "kind": "annotation"}
    s_recent = suite._r2_score(recent, LOCUS, now)
    s_old = suite._r2_score(old, LOCUS, now)
    check("recency: a recent item scores higher than an old one", s_recent > s_old)
    # proximity: a locus-exact item outscores a parent-address item (same ts, unpinned)
    exact = {"text": "E", "address": LOCUS, "ts": iso(now), "kind": "annotation"}
    parent = {"text": "P", "address": PARENT, "ts": iso(now), "kind": "annotation"}
    check("proximity: a locus-exact item scores higher than a parent-address item",
          suite._r2_score(exact, LOCUS, now) > suite._r2_score(parent, LOCUS, now))
    # pin: a pinned item outscores an identical unpinned one
    pinned = {"text": "PN", "address": LOCUS, "ts": iso(now - timedelta(days=30)),
              "kind": "annotation", "pinned": True}
    check("pin: a pinned item scores higher than the same unpinned (old) item",
          suite._r2_score(pinned, LOCUS, now) > suite._r2_score(old, LOCUS, now))

    # ============================================================================================
    # PART 2 — the CAP holds (the keystone): MORE items than the budget → bounded + lowest dropped
    # ============================================================================================
    # Attach MANY annotations at the locus. Each ~120 chars; with a small budget only a few survive.
    N = 40
    for i in range(N):
        # stagger ts so there is a strict score order; item 0 is the OLDEST (lowest score, must drop)
        ts = now - timedelta(seconds=(N - i) * 10)
        store.append_annotation({"kind": "annotation", "address": LOCUS,
                                 "text": f"ITEM-{i:03d} " + ("x" * 100), "ts": ts.isoformat(),
                                 "source": "operator"})
    items = suite._r2_gather(LOCUS)
    check("gather returns all attached items before the cap", len(items) >= N)
    capped = suite._r2_score_and_cap(items, LOCUS, now)
    capped_text = "\n".join(it.get("text", "") for it in capped)
    check("CAP: the resolved slice is bounded (≤ R2_BUDGET chars)", len(capped_text) <= suite.R2_BUDGET)
    check("CAP: not all items survive (the cap actually drops items)", len(capped) < N)
    check("CAP: the highest-scored (most-recent) item survives (ITEM-039)",
          any("ITEM-039" in it.get("text", "") for it in capped))
    check("CAP: the lowest-scored (oldest) item is DROPPED (ITEM-000 absent) — proves the cap holds",
          not any("ITEM-000" in it.get("text", "") for it in capped))

    # ============================================================================================
    # PART 3 — END-TO-END: at a locus, the addressed annotations + chats resolve INTO _chat_context
    # ============================================================================================
    # fresh store so the flood items don't dominate the budget here
    store2 = FsStore(os.path.join(store_dir, "store2"))
    suite2 = Suite(store2, reg, nodes_dir=NODES)
    suite2.create_node(g, "constant", config={"value": "hi"}, node_id="c")
    ann = suite2.annotate(LOCUS, "REVIEW-NOTE the inbox card is misaligned")
    cht = suite2.attach_chat(LOCUS, "CHAT-NOTE why is this build stuck", role="user")
    # an annotation at a SIBLING address must NOT leak into the locus resolution (address is the key)
    suite2.annotate("ui://chrome/activity", "SIBLING-NOTE should not appear at the inbox locus")

    # set the locus (R1 set-point) by indicating it, then resolve context
    suite2._chat_context(g, focus={"selected": [LOCUS]})
    check("R1 locus is set after indicating", suite2.current_locus() == LOCUS)
    ctx = suite2._chat_context(g, focus={"selected": [LOCUS]})
    # the R2 block is the slice headed "CONTEXT RESOLVED AT YOUR LOCUS" — isolate it so we assert on the
    # ADDRESS-KEYED resolution itself, not the pre-existing global "recent activity" narration block
    # (which carries the S2 event echoes of EVERY addressed write, sibling included — that block is not
    # R2 and is out of R2's scope to change).
    R2_HEAD = "CONTEXT RESOLVED AT YOUR LOCUS"
    check("E2E: the R2 address-keyed resolution block is present at a locus", R2_HEAD in ctx)
    r2_block = ctx[ctx.index(R2_HEAD):]
    check("E2E: the addressed ANNOTATION at the locus resolves into the R2 block",
          "REVIEW-NOTE" in r2_block)
    check("E2E: the addressed CHAT at the locus resolves into the R2 block",
          "CHAT-NOTE" in r2_block)
    check("E2E: a SIBLING-address annotation does NOT leak into the R2 locus resolution",
          "SIBLING-NOTE" not in r2_block)

    # --- PROXIMITY IS LIVE IN PRODUCTION (not just in the pure _r2_score unit test): the ancestor walk
    #     means an item attached to a PARENT address is ALSO gathered at the locus, and a locus-EXACT
    #     item ranks above it. This proves Decision A end-to-end through the real _r2_gather path (the
    #     unit test scores hand-built items and bypasses gather). Precondition: the parent address must
    #     parse the S0 grammar (else the ancestor walk silently skips it and proximity is dead). ---
    from contracts.ui_info import parse_ui_address
    parse_ui_address(PARENT)                          # raises here if a single-segment ui:// is illegal
    sp = FsStore(os.path.join(store_dir, "store3"))
    suite3 = Suite(sp, reg, nodes_dir=NODES)
    suite3.annotate(PARENT, "PARENT-NOTE attached one level up the tree")
    suite3.annotate(LOCUS, "EXACT-NOTE attached at the locus itself")
    gathered = suite3._r2_gather(LOCUS)
    g_addrs = {it["address"] for it in gathered if it["kind"] == "annotation"}
    check("PROXIMITY-LIVE: the ancestor walk gathers the PARENT-address item at the locus",
          PARENT in g_addrs and LOCUS in g_addrs)
    g_now = datetime.now(timezone.utc)
    ex_item = [it for it in gathered if "EXACT-NOTE" in it["text"]][0]
    pa_item = [it for it in gathered if "PARENT-NOTE" in it["text"]][0]
    check("PROXIMITY-LIVE: the locus-EXACT item ranks above the PARENT-address item (gather path)",
          suite3._r2_score(ex_item, LOCUS, g_now) > suite3._r2_score(pa_item, LOCUS, g_now))

    # ============================================================================================
    # PART 4 — PRESERVE: the other _chat_context blocks + I1 INDICATING + R1 locus stay intact
    # ============================================================================================
    check("PRESERVE: presence-modes block still present", "presence modes:" in ctx)
    check("PRESERVE: RHM verbs block still present", "RHM verbs you can perform:" in ctx)
    check("PRESERVE: chat models block still present", "chat models:" in ctx)
    check("PRESERVE: inbox block still present", "inbox:" in ctx)
    check("PRESERVE: graphs (multigraph) block still present", "graphs (multigraph):" in ctx)
    check("PRESERVE: the I1 INDICATING block still present at a ui:// locus",
          "INDICATING" in ctx.upper())
    # a canvas node-id focus still injects the co-presence block (unchanged)
    ctx_n = suite2._chat_context(g, focus={"selected": ["c"]})
    check("PRESERVE: a node-id focus STILL injects the co-presence block",
          "OPERATOR'S CURRENT FOCUS" in ctx_n)

    # ============================================================================================
    # PART 5 — FALLBACK: no locus / no addressed match → the keyword consult path still serves
    # ============================================================================================
    # _retrieve_for_consult returns a tuple (no model) — the keyword fallback, unchanged by R2.
    context, sources, file_list = suite2._retrieve_for_consult("how does the memo gate work")
    check("FALLBACK: keyword consult still returns context for a real query", len(context) > 0)
    check("FALLBACK: keyword consult still cites sources", len(sources) > 0)
    # a locus with NO attached info → R2 gather is empty → no R2 block, no crash, context still built
    suite2._current_locus = None
    ctx_no_locus = suite2._chat_context(g, focus=None)
    check("FALLBACK: no locus → context still built (no crash), other blocks intact",
          "presence modes:" in ctx_no_locus)

    print(f"\nALL {PASS} CHECKS PASS — R2 keys retrieval by the operator's locus, the relevance/recency "
          f"decay CAPS the window (lowest-scored dropped), the addressed gather resolves at the locus, "
          f"and the other _chat_context blocks + I1 INDICATING + the keyword fallback are preserved.")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
