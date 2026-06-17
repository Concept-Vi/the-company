"""tests/lifters_acceptance.py — lifters as a FILE-DISCOVERED registry (Cognition Engine NEWMOD · P1 · K2).

The adversary-verified BAR (PART 4.3): a registry is "registry-is-truth" only if **add-a-row = a FILE,
no code edit**. This suite proves, BY MECHANISM (no live model), that:

  1. DISCOVER like projections — `LifterRegistry` mirrors `ProjectionRegistry`/`RoleRegistry`:
     file-discovered from `lifters/`, dict-like, fail-loud on a malformed entry, a non-LIFTER/`_`-file
     skipped; the seeds are present with their declared shape.
  2. DYNAMIC (the BAR) — dropping a NEW `lifters/<id>.py` registers it (no code edit); REMOVING it
     un-registers on rediscover.
  3. FAIL LOUD — a malformed lifter (bad id / id≠filename / non-callable extract / unknown field) RAISES.
  4. THE EXTRACTORS WORK (the floor: a parse is a READ) — frontmatter/links/blocks extract real values.
  5. DRIFT HOME — every discovered lifter is reflected in lifters/AGENTS.md.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from runtime.lifter_registry import LifterRegistry, Lifter, _build_lifter, LIFTER_FIELDS  # noqa: E402

LIFTERS_DIR = os.path.join(ROOT, "lifters")
SEED_IDS = {"frontmatter", "links", "blocks"}
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# 1 · DISCOVER
reg = LifterRegistry().discover([LIFTERS_DIR])
check("registry discovers the seed lifters (file-discovered, not a dict)", SEED_IDS <= set(reg))
check("dict-like: reg['links'] is a Lifter", isinstance(reg["links"], Lifter))
check("dict-like: 'links' in reg; .get default", "links" in reg and reg.get("nope", "X") == "X")
check("a lifter carries a callable extract", callable(reg["frontmatter"].extract))
check("`produces` defaults to id", reg["links"].produces == "links")

# 2 · DYNAMIC
tmp_path = os.path.join(LIFTERS_DIR, "acc_tmp_lift.py")
try:
    with open(tmp_path, "w") as f:
        f.write('def _e(text, *, meta=None):\n    return len(text)\nLIFTER = {"id": "acc_tmp_lift", "extract": _e}\n')
    reg2 = LifterRegistry().discover([LIFTERS_DIR])
    check("DROP-IN: a new lifters/<id>.py is discovered with NO code change (the BAR)", "acc_tmp_lift" in reg2)
finally:
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
reg3 = LifterRegistry().rediscover([LIFTERS_DIR])
check("REMOVE: the temp lifter un-registers on rediscover", "acc_tmp_lift" not in reg3)
check("non-LIFTER skip: only LIFTER-declaring files register", set(reg3) == set(reg))


# 3 · FAIL LOUD
def raises(label, fn):
    try:
        fn()
    except (ValueError, TypeError):
        check(label, True)
        return
    check(label, False)


def _ok(text, *, meta=None):
    return text


raises("bad id (empty) RAISES", lambda: _build_lifter("x", {"id": "", "extract": _ok}))
raises("id != filename RAISES", lambda: _build_lifter("x", {"id": "y", "extract": _ok}))
raises("non-callable extract RAISES", lambda: _build_lifter("x", {"id": "x", "extract": "nope"}))
raises("unknown field RAISES", lambda: _build_lifter("x", {"id": "x", "extract": _ok, "bogus": 1}))
raises("non-dict decl RAISES", lambda: _build_lifter("x", ["nope"]))
good = _build_lifter("ok", {"id": "ok", "extract": _ok})
check("a minimal well-formed lifter builds", good.id == "ok")

# 4 · THE EXTRACTORS WORK (a parse is a READ — the floor)
fm = reg["frontmatter"].extract("---\ntype: note\ntags: a\n---\nbody\n")
check("frontmatter extractor returns the YAML block as a dict", isinstance(fm, dict) and fm.get("type") == "note")
links = reg["links"].extract("see [[Alpha]] and [b](http://x) and [[Alpha]] again")
check("links extractor returns deduped link targets", links == ["Alpha", "http://x"])
blocks = reg["blocks"].extract("# H1\ntext\n## H2\nmore\n")
check("blocks extractor returns the heading structure",
      blocks == [{"level": 1, "heading": "H1"}, {"level": 2, "heading": "H2"}])
recs = reg.as_records()
check("as_records() renders the callable as a qualname (serializable to a face)",
      all(isinstance(r["extract"], str) for r in recs) and len(recs) == len(reg))
check("for_projection routes by `produces`", reg.for_projection("links") is reg["links"])

# 5 · DRIFT HOME
agents_md = open(os.path.join(LIFTERS_DIR, "AGENTS.md")).read()
for lid in reg:
    check(f"drift: '{lid}' is reflected in lifters/AGENTS.md", f"`{lid}`" in agents_md)
check("the registry is NAMED in its drift home", "LifterRegistry" in agents_md)

print(f"\nPASS ({PASS} checks) — lifters is a file-discovered registry (P1/K2), drift-home reflected.")
