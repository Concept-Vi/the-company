"""tests/conv_index_staleness_acceptance.py — X12 · the READ-ONLY index STALENESS check (Convergence).

WHAT THIS PROVES (the gap STATE.md:47 + the embedder-regen follow-up name): build_index is incremental,
but there was NO way to ASK whether the persisted vector index is stale relative to the current corpus
WITHOUT a full rebuild — so semantic retrieval (query_index / consult / R2 semantic ranking) could
silently run over a stale index as the corpus grows. `vector_index.index_staleness(store, corpus)` closes
that: it compares each corpus item's content_hash (REUSING this module's content_hash()) against the
persisted index, READ-ONLY — NO embedding, NO network, NO :8001 dependency — and returns
{"fresh", "missing", "changed", "extra", "counts"} where fresh = (no missing AND no changed AND no extra).

HERMETIC (no :8001, no real embedder): the index is SEEDED via build_index with a deterministic stub
embed_fn (the same hermetic seam conv_index_acceptance / conv_semantic_rank use) over real code:// + ui://
addresses. Seeding through build_index (not hand-written put_vector) means the persisted content_hash is
computed by the SAME path index_staleness checks against — so "identical corpus → fresh" holds by
construction, not by a hand-copied hash that could silently drift.

THE PROOFS (by use, mirroring conv_index_acceptance's check(...) + final ALL-N-CHECKS line):
  1. identical corpus            → fresh=True, missing/changed/extra all empty.
  2. ADD a corpus item           → it appears in `missing`, fresh=False (the new item was never embedded).
  3. CHANGE an item's text       → it appears in `changed`, fresh=False (content_hash differs).
  4. DROP a corpus item          → the dropped indexed address appears in `extra`, fresh=False.
  +  malformed corpus item       → FAILS LOUD (ValueError), never a silent skip (rule 4).
  +  counts                      → the counts block agrees with the lists.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from store.fs_store import FsStore
from store import vector_index

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# ---------------------------------------------------------------------------------------------------
# Deterministic embed stub (no live model). A tiny 3-dim axis: each known text maps to a fixed vector.
# UP returns a vector per input (never raises). Used ONLY to seed the index — index_staleness itself
# never embeds, so the vectors' values don't matter to it; only the persisted content_hash does.
# ---------------------------------------------------------------------------------------------------
_DIM = 3
_VECS = {
    "the conversational chat reply organ":       [1.0, 0.0, 0.0],
    "the voice synthesis text-to-speech engine": [0.9, 0.1, 0.0],
    "the finance ledger and invoice accounting": [0.0, 0.0, 1.0],
}


def _stub_embed_up(transport, inputs, model, dim=None, **kw):
    return [_VECS.get(s, [0.0, 0.0, 1.0]) for s in inputs]


# The seed corpus — real code:// + ui:// addresses (the SAME grammar the index is keyed by).
CORPUS = [
    {"address": "code://suite/chat",   "text": "the conversational chat reply organ"},
    {"address": "code://voice/tts",    "text": "the voice synthesis text-to-speech engine"},
    {"address": "ui://finance/ledger", "text": "the finance ledger and invoice accounting"},
]


store_dir = tempfile.mkdtemp(prefix="conv-index-staleness-test-")
try:
    # Seed the index via build_index with the stub (so the persisted content_hash matches by construction).
    s = FsStore(os.path.join(store_dir, "s"))
    res = vector_index.build_index(s, CORPUS, embed_fn=_stub_embed_up, dim=_DIM, model="stub", base_url="stub://")
    check("seed: build_index embedded all 3 fixture items (no degrade)",
          res.get("embedded") == 3 and not res.get("degraded"))
    check("seed: the index is keyed by all 3 corpus addresses",
          set(vector_index.index_addresses(s)) ==
          {"code://suite/chat", "code://voice/tts", "ui://finance/ledger"})

    # =================================================================================================
    # PROOF 1 — IDENTICAL corpus → fresh=True, all three lists empty.
    # =================================================================================================
    st = vector_index.index_staleness(s, CORPUS)
    check("identical corpus → fresh=True", st["fresh"] is True)
    check("identical corpus → missing/changed/extra ALL empty",
          st["missing"] == [] and st["changed"] == [] and st["extra"] == [])
    check("identical corpus → counts agree (corpus=3, indexed=3, zeros)",
          st["counts"] == {"corpus": 3, "indexed": 3, "missing": 0, "changed": 0, "extra": 0})
    check("model= is accepted (signature symmetry) and does NOT change a content-hash-fresh verdict",
          vector_index.index_staleness(s, CORPUS, model="some-other-model")["fresh"] is True)

    # =================================================================================================
    # PROOF 2 — ADD a corpus item → it appears in `missing`, fresh=False (never embedded).
    # =================================================================================================
    added = [dict(c) for c in CORPUS] + [{"address": "code://finance/invoice",
                                          "text": "the new invoice composition node"}]
    st = vector_index.index_staleness(s, added)
    check("added item → fresh=False", st["fresh"] is False)
    check("added item → it appears in `missing` (in corpus, NOT in index)",
          st["missing"] == ["code://finance/invoice"])
    check("added item → NOT in changed/extra (it is purely new)",
          st["changed"] == [] and st["extra"] == [])
    check("added item → counts: corpus=4, indexed=3, missing=1",
          st["counts"]["corpus"] == 4 and st["counts"]["indexed"] == 3 and st["counts"]["missing"] == 1)

    # =================================================================================================
    # PROOF 3 — CHANGE an item's text → it appears in `changed`, fresh=False (content_hash differs).
    # =================================================================================================
    changed_corpus = [dict(c) for c in CORPUS]
    changed_corpus[0]["text"] = "the conversational chat reply organ — now reworded and updated"
    st = vector_index.index_staleness(s, changed_corpus)
    check("changed item → fresh=False", st["fresh"] is False)
    check("changed item → it appears in `changed` (stored content_hash differs from corpus)",
          st["changed"] == ["code://suite/chat"])
    check("changed item → NOT in missing/extra (the address is still present both sides)",
          st["missing"] == [] and st["extra"] == [])

    # =================================================================================================
    # PROOF 4 — DROP a corpus item → the dropped INDEXED address appears in `extra`, fresh=False.
    # =================================================================================================
    dropped = [c for c in CORPUS if c["address"] != "ui://finance/ledger"]
    st = vector_index.index_staleness(s, dropped)
    check("dropped item → fresh=False", st["fresh"] is False)
    check("dropped item → the orphaned INDEXED address appears in `extra` (indexed, no longer in corpus)",
          st["extra"] == ["ui://finance/ledger"])
    check("dropped item → NOT in missing/changed (the remaining two still match)",
          st["missing"] == [] and st["changed"] == [])
    check("dropped item → counts: corpus=2, indexed=3, extra=1",
          st["counts"]["corpus"] == 2 and st["counts"]["indexed"] == 3 and st["counts"]["extra"] == 1)

    # =================================================================================================
    # FAIL-LOUD — a malformed corpus item (missing address/text) RAISES, never a silent skip (rule 4).
    # =================================================================================================
    raised_addr = False
    try:
        vector_index.index_staleness(s, [{"text": "no address here"}])
    except ValueError:
        raised_addr = True
    check("malformed corpus item (no `address`) RAISES (fail-loud, never a silent skip)", raised_addr)

    raised_text = False
    try:
        vector_index.index_staleness(s, [{"address": "code://x/y"}])
    except ValueError:
        raised_text = True
    check("malformed corpus item (no `text`) RAISES (fail-loud, never a silent skip)", raised_text)

    # =================================================================================================
    # READ-ONLY — the check did NOT mutate the index (no embedding, no writes).
    # =================================================================================================
    check("READ-ONLY: the index is unchanged after all checks (no writes, no re-embed)",
          set(vector_index.index_addresses(s)) ==
          {"code://suite/chat", "code://voice/tts", "ui://finance/ledger"})

    print(f"\nALL {PASS} CHECKS PASS — X12 read-only index staleness "
          f"(identical→fresh · add→missing · change→changed · drop→extra · fail-loud · read-only)")
except AssertionError as e:
    print(e)
    sys.exit(1)
finally:
    import shutil
    shutil.rmtree(store_dir, ignore_errors=True)
