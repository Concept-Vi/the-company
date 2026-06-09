"""tests/relation_types_acceptance.py — relation-types as a FILE-DISCOVERED registry (Cognition Engine NEWMOD · L3/P1).

The adversary-verified BAR (PART 4.3): **add-a-row = a FILE, no code edit**. Proves BY MECHANISM:
  1. DISCOVER like projections — `RelationTypeRegistry` mirrors `ProjectionRegistry`.
  2. DYNAMIC (the BAR) — drop a NEW file → discovered; remove → un-registers.
  3. FAIL LOUD — a malformed relation-type RAISES (bad id / id≠filename / missing/non-bool directed / unknown field).
  4. THE CONSUMER READS — directed() / symmetric() / as_records(); the directed-vs-symmetric split is
     exercised by real seeds (sibling=symmetric, the others=directed); the inverse field is carried.
  5. DRIFT HOME — every discovered relation-type is reflected in relation_types/AGENTS.md.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from runtime.relation_types import (RelationTypeRegistry, RelationType,  # noqa: E402
                                    _build_relation_type, RELATION_TYPE_FIELDS, REQUIRED_FIELDS)

RT_DIR = os.path.join(ROOT, "relation_types")
SEED_IDS = {"principle_beneath", "fragment_of", "contradicts", "sibling"}
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# 1 · DISCOVER
reg = RelationTypeRegistry().discover([RT_DIR])
check("registry discovers the seed relation-types (file-discovered, not a dict)", SEED_IDS <= set(reg))
check("dict-like: reg['sibling'] is a RelationType", isinstance(reg["sibling"], RelationType))
check("dict-like: 'contradicts' in reg; .get default", "contradicts" in reg and reg.get("nope", "X") == "X")
check("'principle_beneath' is directed; label carries the hyphenated name",
      reg["principle_beneath"].directed is True and reg["principle_beneath"].label == "principle-beneath")
check("'fragment_of' carries an inverse (has_fragment)", reg["fragment_of"].inverse == "has_fragment")
check("'sibling' is SYMMETRIC (directed=False — the symmetric seed)", reg["sibling"].directed is False)
check("'contradicts' names near+far spaces", reg["contradicts"].near == "principles" and reg["contradicts"].far == "principles")

# 2 · DYNAMIC
tmp_path = os.path.join(RT_DIR, "acc_tmp_rel.py")
try:
    with open(tmp_path, "w") as f:
        f.write('RELATION_TYPE = {"id": "acc_tmp_rel", "directed": True, "near": "topics"}\n')
    reg2 = RelationTypeRegistry().discover([RT_DIR])
    check("DROP-IN: a new relation_types/<id>.py is discovered with NO code change (the BAR)", "acc_tmp_rel" in reg2)
finally:
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
reg3 = RelationTypeRegistry().rediscover([RT_DIR])
check("REMOVE: the temp relation-type un-registers on rediscover", "acc_tmp_rel" not in reg3)
check("non-RELATION_TYPE skip: only declaring files register", set(reg3) == set(reg))


# 3 · FAIL LOUD
def raises(label, fn):
    try:
        fn()
    except (ValueError, TypeError):
        check(label, True)
        return
    check(label, False)


raises("bad id (empty) RAISES", lambda: _build_relation_type("x", {"id": "", "directed": True}))
raises("id != filename RAISES", lambda: _build_relation_type("x", {"id": "y", "directed": True}))
raises("missing directed RAISES", lambda: _build_relation_type("x", {"id": "x"}))
raises("non-bool directed RAISES", lambda: _build_relation_type("x", {"id": "x", "directed": "yes"}))
raises("unknown field RAISES", lambda: _build_relation_type("x", {"id": "x", "directed": True, "bogus": 1}))
raises("non-dict decl RAISES", lambda: _build_relation_type("x", ["nope"]))
good = _build_relation_type("ok", {"id": "ok", "directed": False})
check("a minimal well-formed relation-type builds", good.id == "ok")

# 4 · CONSUMER READS
dir_ids = {r.id for r in reg.directed()}
sym_ids = {r.id for r in reg.symmetric()}
check("directed() = the directed seeds", dir_ids == {"principle_beneath", "fragment_of", "contradicts"})
check("symmetric() = the symmetric seed (sibling)", sym_ids == {"sibling"})
recs = reg.as_records()
check("as_records() = one dict per relation-type, verbatim spec", len(recs) == len(reg) and all("id" in r for r in recs))

# 5 · DRIFT HOME
agents_md = open(os.path.join(RT_DIR, "AGENTS.md")).read()
for rid in reg:
    check(f"drift: '{rid}' is reflected in relation_types/AGENTS.md", f"`{rid}`" in agents_md)
check("the registry is NAMED in its drift home", "RelationTypeRegistry" in agents_md)

print(f"\nPASS ({PASS} checks) — relation_types is a file-discovered registry (L3/P1), drift-home reflected.")
