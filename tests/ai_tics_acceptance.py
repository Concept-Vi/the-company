"""tests/ai_tics_acceptance.py — AI-tics as a FILE-DISCOVERED registry (Cognition Engine NEWMOD · M4/P1).

The adversary-verified BAR (PART 4.3): **add-a-row = a FILE, no code edit**. The fingerprint-subtraction
catalogue (the inversion). Proves BY MECHANISM:
  1. DISCOVER like projections — `AiTicRegistry` mirrors `ProjectionRegistry`.
  2. DYNAMIC (the BAR) — drop a NEW file → discovered; remove → un-registers.
  3. FAIL LOUD — a malformed tic RAISES (bad id / id≠filename / empty-or-non-string markers / unknown field).
  4. THE CONSUMER READS — all_markers() flattens the cue set; as_records() projects the catalogue.
  5. DRIFT HOME — every discovered tic is reflected in ai_tics/AGENTS.md.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from runtime.ai_tics import AiTicRegistry, AiTic, _build_tic, AI_TIC_FIELDS  # noqa: E402

TIC_DIR = os.path.join(ROOT, "ai_tics")
SEED_IDS = {"framework_imposition", "versioning", "false_finality", "silent_fallback",
            "agent_arch", "closure_form", "mvp"}
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# 1 · DISCOVER
reg = AiTicRegistry().discover([TIC_DIR])
check("registry discovers the seed tics (file-discovered, not a dict)", SEED_IDS <= set(reg))
check("dict-like: reg['versioning'] is an AiTic", isinstance(reg["versioning"], AiTic))
check("dict-like: 'mvp' in reg; .get default", "mvp" in reg and reg.get("nope", "X") == "X")
check("a tic carries a non-empty markers list", len(reg["versioning"].markers) > 0)
check("label falls back / is set", reg["versioning"].label == "versioning" and reg["mvp"].label == "MVP")

# 2 · DYNAMIC
tmp_path = os.path.join(TIC_DIR, "acc_tmp_tic.py")
try:
    with open(tmp_path, "w") as f:
        f.write('AI_TIC = {"id": "acc_tmp_tic", "markers": ["delve", "tapestry"]}\n')
    reg2 = AiTicRegistry().discover([TIC_DIR])
    check("DROP-IN: a new ai_tics/<id>.py is discovered with NO code change (the BAR)", "acc_tmp_tic" in reg2)
finally:
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
reg3 = AiTicRegistry().rediscover([TIC_DIR])
check("REMOVE: the temp tic un-registers on rediscover", "acc_tmp_tic" not in reg3)
check("non-AI_TIC skip: only declaring files register", set(reg3) == set(reg))


# 3 · FAIL LOUD
def raises(label, fn):
    try:
        fn()
    except (ValueError, TypeError):
        check(label, True)
        return
    check(label, False)


raises("bad id (empty) RAISES", lambda: _build_tic("x", {"id": "", "markers": ["a"]}))
raises("id != filename RAISES", lambda: _build_tic("x", {"id": "y", "markers": ["a"]}))
raises("missing markers RAISES", lambda: _build_tic("x", {"id": "x"}))
raises("empty markers RAISES", lambda: _build_tic("x", {"id": "x", "markers": []}))
raises("non-string marker RAISES", lambda: _build_tic("x", {"id": "x", "markers": [1, 2]}))
raises("unknown field RAISES", lambda: _build_tic("x", {"id": "x", "markers": ["a"], "bogus": 1}))
raises("non-dict decl RAISES", lambda: _build_tic("x", ["nope"]))
good = _build_tic("ok", {"id": "ok", "markers": ["a"]})
check("a minimal well-formed tic builds", good.id == "ok")

# 4 · CONSUMER READS
allm = reg.all_markers()
check("all_markers() flattens + dedups the cue set", "MVP" in allm and "v2" in allm and allm == sorted(allm))
recs = reg.as_records()
check("as_records() = one dict per tic, verbatim spec", len(recs) == len(reg) and all("markers" in r for r in recs))

# 5 · DRIFT HOME
agents_md = open(os.path.join(TIC_DIR, "AGENTS.md")).read()
for tid in reg:
    check(f"drift: '{tid}' is reflected in ai_tics/AGENTS.md", f"`{tid}`" in agents_md)
check("the registry is NAMED in its drift home", "AiTicRegistry" in agents_md)

print(f"\nPASS ({PASS} checks) — ai_tics is a file-discovered registry (M4/P1), drift-home reflected.")
