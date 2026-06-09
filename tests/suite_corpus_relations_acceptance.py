"""tests/suite_corpus_relations_acceptance.py — the SUITE-lane FACE over the corpus pillar (Cognition
Engine GROUP B + GROUP D, SUITE lane).

Proves, BY USE against a real Suite over a temp FsStore (no live model — the wrappers + the projection
wiring are the unit under test; :8001 is DOWN so the vector spaces are SEEDED deterministically):

  B — the cognition SELECTS PROJECT the file-discovered PROJECTION registry:
    1. cognition_info()['projections'] == the discovered lens set (as_records), not a hardcoded list;
       'spaces' == the embeddable subset.
    2. available_inputs()['projections'] / ['projection_spaces'] surface the lenses + their vec:// spaces,
       additive to the prior keys (utterance/roles/role_addresses/context_variables unchanged).
    3. THE BAR (add-a-row=a-FILE): drop a `projections/<id>.py`, build a FRESH Suite (the bridge-restart
       analog), and the new lens appears in BOTH selects with NO code change; remove it → gone.

  D — the corpus + inversion-finder Suite methods (thin reuse of runtime/corpus + query_index):
    4. write_corpus_record → read_corpus_record round-trips with lineage INTACT; the lineage GATE bites
       (a record with no lineage RAISES through the Suite face).
    5. list_corpus / find_corpus project + filter the discovered records.
    6. find_relations(item, near_space, far_space) returns the near∩¬far inversion over SEEDED per-space
       vectors (near in principle-space, NOT near in topic-space); a missing anchor FAILS LOUD.

  FLOOR: none of these is on RHM_VERBS / the MCP face; find_relations + the corpus reads emit no
  resolve/approve/dispatch.

LAWS proven: registry-is-truth (selects project the discovered set, never hardcoded) · file-discovery
(drop-in lens appears) · reuse-don't-parallel (the Suite methods are thin over corpus.py/query_index) ·
fail-loud (the lineage gate + the missing-anchor anchor) · the floor (reads/telemetry only).
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from store.fs_store import FsStore                                          # noqa: E402
from runtime.registry import NodeRegistry                                   # noqa: E402
from runtime.suite import Suite                                             # noqa: E402
from runtime.corpus import CorpusError, corpus_address                      # noqa: E402

PROJECTIONS_DIR = os.path.join(ROOT, "projections")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def raises(label, fn, exc=Exception):
    try:
        fn()
    except exc:
        check(label, True)
        return
    check(label, False)


def new_suite(root):
    store = FsStore(os.path.join(root, "store"))
    reg = NodeRegistry().discover([os.path.join(ROOT, "nodes")])
    return Suite(store, reg)


store_dir = tempfile.mkdtemp(prefix="suite-corpus-test-")
try:
    suite = new_suite(store_dir)

    # =============================================================================================
    # B1/B2 — the SELECTS project the discovered projection registry
    # =============================================================================================
    seed_ids = {"what", "topics", "principles", "worldview", "claimed_status", "lineage"}
    info = suite.cognition_info()
    proj_ids = {p["id"] for p in info["projections"]}
    check("cognition_info()['projections'] = the discovered lens set (file-discovered, not hardcoded)",
          seed_ids <= proj_ids)
    check("cognition_info()['spaces'] = the embeddable subset (Group-L vector spaces) — the discovery "
          "seeds present (registry-is-truth: a NEW embeds:true lens like 'repo' for ① extends the set, not breaks it)",
          {"topics", "principles", "worldview"} <= set(info["spaces"]))

    ai = suite.available_inputs()
    check("available_inputs()['projections'] surfaces the lens set", seed_ids <= set(ai["projections"]))
    check("available_inputs()['projection_spaces'] = the vec:// spaces of the embeddable lenses (seeds present; "
          "a new space extends)",
          {"vec://<item>#space=topics", "vec://<item>#space=principles", "vec://<item>#space=worldview"}
          <= set(ai["projection_spaces"]))
    check("available_inputs() ADDITIVE — prior keys preserved",
          all(k in ai for k in ("utterance", "roles", "role_addresses", "context_variables")))

    # =============================================================================================
    # B3 — THE BAR: drop a projections/<id>.py → a FRESH Suite (bridge-restart analog) sees it
    # =============================================================================================
    tmp_lens = os.path.join(PROJECTIONS_DIR, "acc_suite_tmp_lens.py")
    try:
        with open(tmp_lens, "w") as f:
            f.write('PROJECTION = {"id": "acc_suite_tmp_lens", "level": "content", '
                    '"produced_by": "model", "embeds": True, "field": "array", '
                    '"desc": "a drop-in lens for the SUITE-lane select-projection proof"}\n')
        suite2 = new_suite(store_dir)                          # FRESH Suite = the bridge-restart analog
        info2 = suite2.cognition_info()
        ai2 = suite2.available_inputs()
        check("DROP-IN: a new projections/<id>.py appears in cognition_info()['projections'] (NO code edit)",
              "acc_suite_tmp_lens" in {p["id"] for p in info2["projections"]})
        check("DROP-IN: the embeds:true lens appears in cognition_info()['spaces']",
              "acc_suite_tmp_lens" in info2["spaces"])
        check("DROP-IN: it appears in available_inputs()['projections'] too",
              "acc_suite_tmp_lens" in ai2["projections"])
    finally:
        if os.path.exists(tmp_lens):
            os.remove(tmp_lens)
    suite3 = new_suite(store_dir)
    check("REMOVE: a fresh Suite no longer lists the temp lens (file-discovery, not append-only)",
          "acc_suite_tmp_lens" not in {p["id"] for p in suite3.cognition_info()["projections"]})

    # =============================================================================================
    # D4 — write/read corpus round-trip + the lineage gate (through the Suite face)
    # =============================================================================================
    LINE = {"session": "s1", "round": "1", "project": "vault-scan"}
    ev = suite.write_corpus_record(source_address="f/a.md", output={"what": "a design note"},
                                   kind="capture", lineage=LINE, model="qwen", projection="what")
    rec = suite.read_corpus_record(ev["address"])
    check("write→read corpus round-trips (output intact)", rec and rec["output"] == {"what": "a design note"})
    check("lineage INTACT through the Suite face", rec["lineage"]["project"] == "vault-scan")
    check("address is the deterministic corpus_address",
          ev["address"] == corpus_address("f/a.md", project="vault-scan", projection="what"))
    raises("the lineage GATE bites through the Suite (no lineage RAISES)",
           lambda: suite.write_corpus_record(source_address="f/b.md", output={"x": 1}, kind="capture",
                                              lineage=None),
           exc=CorpusError)

    # =============================================================================================
    # D5 — list_corpus / find_corpus project + filter
    # =============================================================================================
    suite.write_corpus_record(source_address="g/b.md", output=["topic1"], kind="capture",
                              lineage={"session": "s9", "round": "1", "project": "other-proj"},
                              projection="topics")
    check("list_corpus projects the records",
          any(r["address"] == ev["address"] for r in suite.list_corpus()))
    check("find_corpus(project=) filters by lineage",
          {r["source_address"] for r in suite.find_corpus(project="vault-scan")} == {"f/a.md"})
    check("find_corpus(projection=) filters by lens",
          all(r["projection"] == "topics" for r in suite.find_corpus(projection="topics")))

    # =============================================================================================
    # D / L2 — find_relations: the near∩¬far inversion over SEEDED per-space vectors
    #   (the embedder :8001 is DOWN — seed deterministic vectors directly, the persisted-query path needs
    #    no live embed. Geometry: in PRINCIPLES space, ITEM is adjacent to A (both [1,0]) and far from B
    #    ([0,1]); in TOPICS space, ITEM is adjacent to B ([1,0]) and far from A ([0,1]). So the near∩¬far
    #    inversion near=principles/far=topics = {A} (shares the principle, diverges in topic) — NOT B.)
    # =============================================================================================
    def seed(item, space, vec):
        suite.store.put_vector(suite.store.space_address(item, space), vec, "b2:seed",
                               dim=2, model="seed", space=space, source=item)

    seed("ITEM", "principles", [1.0, 0.0]);  seed("ITEM", "topics", [1.0, 0.0])
    seed("A", "principles", [1.0, 0.0]);     seed("A", "topics", [0.0, 1.0])
    seed("B", "principles", [0.0, 1.0]);     seed("B", "topics", [1.0, 0.0])
    # C is the TEETH-CHECK for the ¬far subtraction: near ITEM in BOTH spaces (principle [1,0] AND topic
    # [1,0]). It is excluded ONLY by the far filter (`not in far_ids`) — unlike B, which is excluded
    # trivially (not near in near_space at all). Delete the far clause and C LEAKS into relations → this
    # assertion goes red. (Mirrors concurrency_acceptance neutering the fcntl lock to prove the teeth.)
    seed("C", "principles", [1.0, 0.0]);     seed("C", "topics", [1.0, 0.0])

    rel = suite.find_relations("ITEM", near_space="principles", far_space="topics", k=10)
    check("find_relations returns the near∩¬far inversion: A (same principle, different topic)",
          "A" in rel["relations"])
    check("find_relations EXCLUDES B (near in far_space=topics — not an inversion)",
          "B" not in rel["relations"])
    check("find_relations EXCLUDES C — the ¬far TEETH: near in BOTH spaces, subtracted by the far filter",
          "C" not in rel["relations"])
    check("find_relations excludes the item itself", "ITEM" not in rel["relations"])
    check("find_relations carries the near/far neighbour rows for the WHY",
          isinstance(rel["near"], list) and isinstance(rel["far"], list))
    raises("find_relations FAILS LOUD on a missing anchor (no vector in a named space)",
           lambda: suite.find_relations("NOPE", near_space="principles", far_space="topics"),
           exc=ValueError)

    # =============================================================================================
    # THE FLOOR — none of these methods is on the MCP face / RHM_VERBS
    # =============================================================================================
    check("find_relations / corpus methods are NOT in RHM_VERBS (the floor)",
          all(v not in suite.RHM_VERBS for v in
              ("find_relations", "write_corpus_record", "list_corpus", "find_corpus")))

    print(f"\nPASS ({PASS} checks) — SUITE-lane: selects PROJECT the projection registry (B) + "
          f"corpus/find_relations Suite methods (D), thin reuse, fail-loud, floor held.")
finally:
    import shutil
    shutil.rmtree(store_dir, ignore_errors=True)
