"""tests/capture_lenses_acceptance.py — THE MULTI-LENS CAPTURE LANE + space-aware index_staleness
(Universal Projection Group 8 — EMBEDDING SUBSTRATE LIVE).

WHAT THIS PROVES:
The embeddable lenses topics/principles/worldview were DECLARED spaces with NO producer until
`Suite.capture_corpus_lenses` was built (the capture-schema builder projections.py:5 / suite.py:292
NAMED but never built). This guards the DETERMINISTIC contract of that lane + the `space=` extension
of `vector_index.index_staleness` that confirms a per-projection space is fresh.

HERMETIC: the embed transport is a deterministic stub (no live :8001) — the same seam conv_index uses.
The MODEL fan (run_items @ chat-4b) is NOT exercised here (it needs a live model); it is verified BY USE
in the Group-8 beat (162 files captured into each of topics/principles/worldview, 0 failures, real
BGE-M3 vectors, meaningful render-not-judge content, queryable, all spaces index_staleness fresh=True).
This suite guards the parts that MUST hold regardless of the model: lens validation (fail-loud),
per-space staleness, cross-space no-leak, and the computation-floor.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from store.fs_store import FsStore
from store import vector_index as vx
from runtime.suite import Suite
from runtime.registry import NodeRegistry

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


_DIM = 3


def _stub(transport, inputs, model, dim=None, **kw):
    # a deterministic non-zero embed (the content of the vector is irrelevant to a content_hash verdict)
    return [[1.0, 0.0, 0.0] for _ in inputs]


# ── SECTION 1 — index_staleness(space=) over a per-projection space (the new param) ────────────────────
s = FsStore(tempfile.mkdtemp())
# build TWO topics-space entries + ONE default-space entry (the no-leak guard depends on both existing)
vx.build_index(s, [{"address": "code://a.py", "text": "ta"},
                   {"address": "code://b.py", "text": "tb"}],
               embed_fn=_stub, dim=_DIM, model="stub", base_url="stub://", space="topics")
vx.build_index(s, [{"address": "code://d.py", "text": "td"}],
               embed_fn=_stub, dim=_DIM, model="stub", base_url="stub://")          # DEFAULT space

CORPUS_T = [{"address": "code://a.py", "text": "ta"}, {"address": "code://b.py", "text": "tb"}]

st = vx.index_staleness(s, CORPUS_T, space="topics")
check("space='topics': an identical corpus is FRESH", st["fresh"] is True)
check("space='topics': counts corpus==indexed==2",
      st["counts"]["corpus"] == 2 and st["counts"]["indexed"] == 2)

# CROSS-SPACE NO-LEAK: the default-space entry (d.py) must NOT show as 'extra' in the topics verdict
check("space='topics': the DEFAULT-space entry does NOT leak in as extra", "code://d.py" not in str(st["extra"]))
check("space='topics': extra is empty (only the 2 topics entries are seen)", st["extra"] == [])

# DROP b from the corpus → b is an ORPHAN in the index → 'extra' (indexed, no longer in corpus)
st_drop = vx.index_staleness(s, [{"address": "code://a.py", "text": "ta"}], space="topics")
check("space='topics': dropping b → NOT fresh", st_drop["fresh"] is False)
check("space='topics': dropped b is reported in 'extra' (the spaced key)",
      any("b.py" in e and "#space=topics" in e for e in st_drop["extra"]))

# ADD c (never embedded) → c is 'missing'
st_add = vx.index_staleness(s, CORPUS_T + [{"address": "code://c.py", "text": "tc"}], space="topics")
check("space='topics': a never-embedded item is reported 'missing' (bare address)",
      st_add["missing"] == ["code://c.py"])

# CHANGE a's text → content_hash differs from the stored one → 'changed' (no rebuild; the point of staleness)
st_chg = vx.index_staleness(s, [{"address": "code://a.py", "text": "ta-CHANGED"},
                                {"address": "code://b.py", "text": "tb"}], space="topics")
check("space='topics': a changed-text item is reported 'changed'", st_chg["changed"] == ["code://a.py"])

# THE OTHER DIRECTION of no-leak: the DEFAULT verdict must not see the topics entries as extra
st_def = vx.index_staleness(s, [{"address": "code://d.py", "text": "td"}], space=None)
check("space=None: the DEFAULT verdict is fresh + does NOT see the topics entries as extra",
      st_def["fresh"] is True and st_def["extra"] == [])

# REGRESSION — space=None is byte-identical to the pre-space behaviour (the bare default set)
check("space=None: default-space counts see ONLY the 1 default entry (no spaced leak)",
      st_def["counts"]["indexed"] == 1)


# ── SECTION 2 — capture_corpus_lenses lens validation (FAIL-LOUD, no model needed) ─────────────────────
suite = Suite(FsStore(tempfile.mkdtemp()), NodeRegistry().discover([os.path.join(ROOT, "nodes")]))


def _raises(fn):
    try:
        fn(); return False
    except Exception:
        return True


check("capture_corpus_lenses: empty `lenses` RAISES (no default — fail loud, never guess)",
      _raises(lambda: suite.capture_corpus_lenses(lenses=[], paths=["AGENTS.md"])))
check("capture_corpus_lenses: a NON-registry lens RAISES (registry-is-truth)",
      _raises(lambda: suite.capture_corpus_lenses(lenses=["nonexistent_lens"], paths=["AGENTS.md"])))
check("capture_corpus_lenses: a CODE-produced lens ('lineage') RAISES (not a capture-role lens)",
      _raises(lambda: suite.capture_corpus_lenses(lenses=["lineage"], paths=["AGENTS.md"])))
check("capture_corpus_lenses: a model-but-NON-embeddable lens ('claimed_status') RAISES (not a space)",
      _raises(lambda: suite.capture_corpus_lenses(lenses=["claimed_status"], paths=["AGENTS.md"])))
# the registry HAS the embeddable model lenses the lane is FOR (so validation passes for them — the
# RAISE above is a real gate, not a registry that simply lacks every lens)
_emb_model = {p.id for p in suite.projection_registry.embeddable()} & {p.id for p in suite.projection_registry.model_projections()}
check("capture_corpus_lenses: topics/principles/worldview ARE valid embeddable model lenses",
      {"topics", "principles", "worldview"} <= _emb_model)


# ── SECTION 3 — the computation FLOOR (the lane is a pure read+embed, never a dispatcher) ──────────────
# Scan the CODE, not the docstring prose (the docstring NAMES the floor — 'launches no claude -p' — which a
# naive string scan would false-trip on). Strip the docstring, then look for real EXECUTION primitives.
import inspect, ast
src = inspect.getsource(Suite.capture_corpus_lenses)
_fn = ast.parse(src.strip()).body[0]
if ast.get_docstring(_fn) is not None:           # drop the docstring node, keep the executable body
    _fn.body = _fn.body[1:]
code = ast.unparse(_fn)
check("capture_corpus_lenses spawns NO subprocess / claude (the autonomous-spawn-lead-only floor)",
      "subprocess" not in code and "Popen" not in code and "os.system" not in code and "claude" not in code)
check("capture_corpus_lenses makes NO drive/dispatch/approve call (the operator-only floor)",
      "drive_dispatch" not in code and ".approve(" not in code and "resolve_decision" not in code
      and "route_run_output" not in code)
check("capture_corpus_lenses REUSES the proven seams (run_items + capture_corpus + walk_files)",
      "run_items" in code and "capture_corpus" in code and "walk_files" in code)


print(f"\nPASS ({PASS} checks) — multi-lens capture lane: lens validation fail-loud, per-space "
      f"index_staleness (fresh/missing/changed/extra + cross-space no-leak), space=None regression, "
      f"the computation floor. (Live model fan = verified by use in the Group-8 beat.)")
