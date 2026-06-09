"""tests/mark_types_acceptance.py — mark-types as a FILE-DISCOVERED registry (Cognition Engine NEWMOD · M1/M4/P1).

The adversary-verified BAR (PART 4.3): **add-a-row = a FILE, no code edit**. Proves BY MECHANISM:
  1. DISCOVER like projections — `MarkTypeRegistry` mirrors `ProjectionRegistry`/`RoleRegistry`.
  2. DYNAMIC (the BAR) — drop a NEW file → discovered; remove → un-registers on rediscover.
  3. FAIL LOUD — a malformed mark-type RAISES at build.
  4. THE CONSUMER READS — subtractive() / as_records() project the discovered set; the surface-vs-subtract
     split is exercised by a real seed (ai_fingerprint = subtract).
  5. DRIFT HOME — every discovered mark-type is reflected in mark_types/AGENTS.md.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from runtime.mark_types import MarkTypeRegistry, MarkType, _build_mark_type, MARK_TYPE_FIELDS  # noqa: E402

MT_DIR = os.path.join(ROOT, "mark_types")
SEED_IDS = {"gold_likelihood", "ai_fingerprint", "contradiction"}
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# 1 · DISCOVER
reg = MarkTypeRegistry().discover([MT_DIR])
check("registry discovers the seed mark-types (file-discovered, not a dict)", SEED_IDS <= set(reg))
check("dict-like: reg['gold_likelihood'] is a MarkType", isinstance(reg["gold_likelihood"], MarkType))
check("dict-like: 'contradiction' in reg; .get default", "contradiction" in reg and reg.get("nope", "X") == "X")
check("'gold_likelihood' shape: score + surface",
      reg["gold_likelihood"].value_shape == "score" and reg["gold_likelihood"].direction == "surface")
check("'ai_fingerprint' is the SUBTRACT direction (the inversion seed)", reg["ai_fingerprint"].direction == "subtract")
check("'contradiction' value_shape is span", reg["contradiction"].value_shape == "span")
check("direction defaults to surface when omitted",
      _build_mark_type("z", {"id": "z", "value_shape": "label"}).direction == "surface")

# 2 · DYNAMIC
tmp_path = os.path.join(MT_DIR, "acc_tmp_mark.py")
try:
    with open(tmp_path, "w") as f:
        f.write('MARK_TYPE = {"id": "acc_tmp_mark", "value_shape": "bool", "direction": "surface"}\n')
    reg2 = MarkTypeRegistry().discover([MT_DIR])
    check("DROP-IN: a new mark_types/<id>.py is discovered with NO code change (the BAR)", "acc_tmp_mark" in reg2)
finally:
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
reg3 = MarkTypeRegistry().rediscover([MT_DIR])
check("REMOVE: the temp mark-type un-registers on rediscover", "acc_tmp_mark" not in reg3)
check("non-MARK_TYPE skip: only MARK_TYPE-declaring files register", set(reg3) == set(reg))


# 3 · FAIL LOUD
def raises(label, fn):
    try:
        fn()
    except (ValueError, TypeError):
        check(label, True)
        return
    check(label, False)


raises("bad id (empty) RAISES", lambda: _build_mark_type("x", {"id": "", "value_shape": "score"}))
raises("id != filename RAISES", lambda: _build_mark_type("x", {"id": "y", "value_shape": "score"}))
raises("missing value_shape RAISES", lambda: _build_mark_type("x", {"id": "x"}))
raises("empty value_shape RAISES", lambda: _build_mark_type("x", {"id": "x", "value_shape": ""}))
raises("unknown field RAISES", lambda: _build_mark_type("x", {"id": "x", "value_shape": "s", "bogus": 1}))
raises("non-dict decl RAISES", lambda: _build_mark_type("x", ["nope"]))
good = _build_mark_type("ok", {"id": "ok", "value_shape": "label"})
check("a minimal well-formed mark-type builds", good.id == "ok")

# 4 · CONSUMER READS
sub = {m.id for m in reg.subtractive()}
check("subtractive() = the subtract-direction set (the inversion)", sub == {"ai_fingerprint"})
recs = reg.as_records()
check("as_records() = one dict per mark-type, verbatim spec", len(recs) == len(reg) and all("id" in r for r in recs))

# 5 · DRIFT HOME
agents_md = open(os.path.join(MT_DIR, "AGENTS.md")).read()
for mid in reg:
    check(f"drift: '{mid}' is reflected in mark_types/AGENTS.md", f"`{mid}`" in agents_md)
check("the registry is NAMED in its drift home", "MarkTypeRegistry" in agents_md)

print(f"\nPASS ({PASS} checks) — mark_types is a file-discovered registry (M1/M4/P1), drift-home reflected.")
