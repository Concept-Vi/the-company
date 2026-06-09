"""tests/conv_index_space_acceptance.py — SPACE-KEYED vectors + per-space query (cognition-engine GROUP L).

WHAT THIS PROVES (the STORE lane of the cognition-engine build, L1/L2):
A single SOURCE item is a POINT in MANY PROJECTION SPACES (principle / topic / vocab / ...) — its
principle-embedding and its topic-embedding are DIFFERENT vectors of the SAME item. The store can hold
both, keyed THROUGH the C1 address grammar (`vec://<item>#space=<proj>`, NOT an address hack), and a
query can rank WITHIN one space (k-NN in principle-space ≠ in topic-space → the same item is
cross-space DISTINGUISHABLE by its different neighbours).

DONE-RIGHT / PORTABLE (store constitution + C4 Resolver Protocol — Supabase-later implements the SAME):
the space + source ride as EXPLICIT FIELDS on the open record, so the per-space filter is a clean field
match (a SQL `WHERE space = X`), and the composed `vec://...#space=` address keeps the per-(item,space)
key unique + portable. Field and address agree by construction.

NO-REGRESSION (the critical guard): no-space query/index_addresses see EXACTLY the default-space entries
— a spaced entry NEVER leaks into the default corpus (or retrieval is polluted + two differing-dim
projections crash retrieve._cosine). Old single-space (unspaced) vectors still resolve and round-trip.

HERMETIC: the embed transport is a deterministic stub (no live :8001) — the exact seam conv_index uses.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from store.fs_store import FsStore
from store import vector_index as vx

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


_DIM = 3

# The same THREE source items, embedded at TWO different LENSES (projection spaces). In PRINCIPLE-space,
# alpha and beta are near (both [1,0,0]-ish), gamma orthogonal. In TOPIC-space the geometry is DIFFERENT:
# alpha and gamma are near, beta orthogonal. Same items, different neighbours per space = the whole point.
_PRINCIPLE = {
    "alpha source text (principle lens)": [1.0, 0.0, 0.0],
    "beta source text (principle lens)":  [0.9, 0.1, 0.0],   # near alpha in principle-space
    "gamma source text (principle lens)": [0.0, 0.0, 1.0],   # orthogonal in principle-space
}
_TOPIC = {
    "alpha source text (topic lens)": [1.0, 0.0, 0.0],
    "beta source text (topic lens)":  [0.0, 1.0, 0.0],       # orthogonal in topic-space
    "gamma source text (topic lens)": [0.9, 0.0, 0.1],       # near alpha in topic-space
}


def _stub(table):
    def _embed(transport, inputs, model, dim=None, **kw):
        return [table.get(s, [0.0, 0.0, 1.0]) for s in inputs]
    return _embed


# corpus addresses (the SOURCE items) — bare item addresses; the space rides separately.
ITEMS = ["code://x/alpha", "code://x/beta", "code://x/gamma"]
PRINCIPLE_CORPUS = [
    {"address": "code://x/alpha", "text": "alpha source text (principle lens)"},
    {"address": "code://x/beta",  "text": "beta source text (principle lens)"},
    {"address": "code://x/gamma", "text": "gamma source text (principle lens)"},
]
TOPIC_CORPUS = [
    {"address": "code://x/alpha", "text": "alpha source text (topic lens)"},
    {"address": "code://x/beta",  "text": "beta source text (topic lens)"},
    {"address": "code://x/gamma", "text": "gamma source text (topic lens)"},
]


store_dir = tempfile.mkdtemp(prefix="conv-index-space-test-")
try:
    s = FsStore(os.path.join(store_dir, "s"))

    # =============================================================================================
    # PART 0 — the address grammar: space_address composes THROUGH C1 (not a hack), default = bare.
    # =============================================================================================
    check("space_address(item, None) == the BARE item address (the default/unspaced key, back-compat)",
          s.space_address("code://x/alpha", None) == "code://x/alpha")
    check("space_address(item, 'principle') composes the C1 vec://#space= grammar shape",
          s.space_address("code://x/alpha", "principle") == "vec://code://x/alpha#space=principle")

    # =============================================================================================
    # PART 1 — store the SAME items in TWO spaces (a point in many spaces).
    # =============================================================================================
    rp = vx.build_index(s, PRINCIPLE_CORPUS, embed_fn=_stub(_PRINCIPLE), dim=_DIM, model="stub",
                        base_url="stub://", space="principle")
    rt = vx.build_index(s, TOPIC_CORPUS, embed_fn=_stub(_TOPIC), dim=_DIM, model="stub",
                        base_url="stub://", space="topic")
    check("both space-builds embedded all 3 items (no degrade)",
          rp.get("embedded") == 3 and rt.get("embedded") == 3
          and not rp.get("degraded") and not rt.get("degraded"))

    # the per-(item,space) entries are stored under composed vec://#space= keys (explicit fields carried)
    rec_p = s.get_vector("vec://code://x/alpha#space=principle")
    rec_t = s.get_vector("vec://code://x/alpha#space=topic")
    check("a spaced entry carries explicit `space` + `source` FIELDS (the portable per-space filter key)",
          rec_p["space"] == "principle" and rec_p["source"] == "code://x/alpha"
          and rec_t["space"] == "topic" and rec_t["source"] == "code://x/alpha")
    # alpha is the shared query anchor (== [1,0,0] in both spaces by design); beta is what differs per lens.
    rec_pb = s.get_vector("vec://code://x/beta#space=principle")
    rec_tb = s.get_vector("vec://code://x/beta#space=topic")
    check("the SAME item (beta) has DIFFERENT vectors in the two spaces (a point in many spaces)",
          rec_pb["vector"] == _PRINCIPLE["beta source text (principle lens)"]
          and rec_tb["vector"] == _TOPIC["beta source text (topic lens)"]
          and rec_pb["vector"] != rec_tb["vector"])

    # =============================================================================================
    # PART 2 — per-space query: k-NN WITHIN one space, returns the SOURCE item, cross-space distinct.
    # =============================================================================================
    # query near alpha (vector [1,0,0]) — the NEIGHBOURS differ by space.
    q = [1.0, 0.0, 0.0]
    ranked_p = vx.query_index(s, q, k=3, space="principle")
    ranked_t = vx.query_index(s, q, k=3, space="topic")
    check("query(space=principle) returns the SOURCE items (not the internal vec://#space= keys)",
          all(r["id"] in ITEMS for r in ranked_p) and ranked_p[0]["id"] == "code://x/alpha")
    check("query(space=topic) also returns SOURCE items, alpha nearest",
          all(r["id"] in ITEMS for r in ranked_t) and ranked_t[0]["id"] == "code://x/alpha")
    # CROSS-SPACE DISTINGUISHABLE: in principle-space beta is alpha's near neighbour; in topic-space gamma is.
    order_p = [r["id"] for r in ranked_p]
    order_t = [r["id"] for r in ranked_t]
    check("principle-space: beta is alpha's near neighbour (gamma orthogonal)",
          order_p == ["code://x/alpha", "code://x/beta", "code://x/gamma"])
    check("topic-space: gamma is alpha's near neighbour (beta orthogonal) — DIFFERENT geometry, same item",
          order_t == ["code://x/alpha", "code://x/gamma", "code://x/beta"])
    check("the rankings DIFFER across spaces (cross-space distinguishable — the L2 point)",
          order_p != order_t)

    # index_addresses per space enumerates that space only
    check("index_addresses(space=principle) lists exactly the 3 composed principle keys",
          set(vx.index_addresses(s, space="principle"))
          == {s.space_address(i, "principle") for i in ITEMS})
    check("index_addresses(space=topic) lists exactly the 3 composed topic keys",
          set(vx.index_addresses(s, space="topic"))
          == {s.space_address(i, "topic") for i in ITEMS})

    # =============================================================================================
    # PART 3 — NO-REGRESSION: an unspaced (default) index over the SAME store is isolated from spaces.
    # =============================================================================================
    DEFAULT_CORPUS = [{"address": i, "text": f"{i} default-space text"} for i in ITEMS]
    rd = vx.build_index(s, DEFAULT_CORPUS, embed_fn=_stub({}), dim=_DIM, model="stub", base_url="stub://")
    check("a default-space build over the same store embeds its 3 items (independent of the spaces)",
          rd.get("embedded") == 3)
    # the default index_addresses sees ONLY the bare (unspaced) addresses — NO spaced keys leak in
    check("no-space index_addresses == the bare default entries ONLY (spaced keys do NOT leak in)",
          set(vx.index_addresses(s)) == set(ITEMS))
    # a no-space query ranks ONLY the default corpus (the regression guard the live consult/R2 callers need)
    nd = vx.query_index(s, q, k=10, space=None)
    check("no-space query ranks ONLY default-space entries (3, not 9 — spaced entries excluded)",
          len(nd) == 3 and all(r["id"] in ITEMS for r in nd))
    # ALL_SPACES sees everything (3 default + 3 principle + 3 topic = 9)
    check("ALL_SPACES enumerates every entry (3 default + 3 principle + 3 topic = 9)",
          len(vx.index_addresses(s, space=FsStore.ALL_SPACES)) == 9)

    # =============================================================================================
    # PART 4 — incremental diff keys on the SPACED address (changing one space never false-skips it).
    # =============================================================================================
    calls = {"n": 0}

    def _counting(table):
        def _e(transport, inputs, model, dim=None, **kw):
            calls["n"] += len(inputs)
            return [table.get(t, [0.0, 0.0, 1.0]) for t in inputs]
        return _e

    si = FsStore(os.path.join(store_dir, "si"))
    vx.build_index(si, PRINCIPLE_CORPUS, embed_fn=_counting(_PRINCIPLE), dim=_DIM, model="stub", base_url="stub://", space="principle")
    after_principle = calls["n"]
    check("first principle build embeds all 3", after_principle == 3)
    # building the SAME items in TOPIC space must NOT be skipped as 'already embedded' — different key
    rt2 = vx.build_index(si, TOPIC_CORPUS, embed_fn=_counting(_TOPIC), dim=_DIM, model="stub", base_url="stub://", space="topic")
    check("the SAME items in a DIFFERENT space all re-embed (diff keys on the spaced address, not the bare one)",
          calls["n"] == after_principle + 3 and rt2.get("embedded") == 3 and rt2.get("skipped") == 0)
    # rebuild principle UNCHANGED → skip (incremental still works per-space)
    rp2 = vx.build_index(si, PRINCIPLE_CORPUS, embed_fn=_counting(_PRINCIPLE), dim=_DIM, model="stub", base_url="stub://", space="principle")
    check("rebuilding an UNCHANGED space re-embeds nothing (per-space incremental intact)",
          rp2.get("embedded") == 0 and rp2.get("skipped") == 3)

    # =============================================================================================
    # PART 5 — persistence-survives-reload (ext4); old unspaced vectors still resolve (round-trip).
    # =============================================================================================
    s2 = FsStore(os.path.join(store_dir, "s"))
    check("a second store over the same root sees the per-space entries (survives reload)",
          set(vx.index_addresses(s2, space="principle"))
          == {s.space_address(i, "principle") for i in ITEMS})
    check("a second store still sees the default/unspaced entries by their bare address (round-trip)",
          set(vx.index_addresses(s2)) == set(ITEMS)
          and s2.get_vector("code://x/alpha")["space"] is None)

    # =============================================================================================
    # PART 6 — FAIL LOUD: a spaced put_vector WITHOUT a source raises (no silent wrong round-trip).
    # =============================================================================================
    raised = False
    try:
        s.put_vector("vec://code://x/alpha#space=z", [1.0, 0.0, 0.0], "b2:x", dim=_DIM, model="stub", space="z")
    except ValueError:
        raised = True
    check("a spaced put_vector with NO source RAISES (fail-loud — never a silent wrong round-trip)", raised)

    print(f"\nPASS — {PASS} checks green (space-keyed vectors: grammar + multi-space store + per-space k-NN "
          f"+ cross-space-distinct + no-regression + per-space incremental + reload)")
finally:
    import shutil
    shutil.rmtree(store_dir, ignore_errors=True)
