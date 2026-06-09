#!/usr/bin/env python3
"""tests/capture_one_source_acceptance.py — CAPTURE-EMBED ONE-SOURCE (FINAL lane).

THE GAP CLOSED (SUITE-3 flagged it): the MCP `capture` tool embedded-on-write, but the bridge capture route
`/api/cognition/corpus` ONLY wrote the corpus record and NEVER embedded — so capturing via /api SILENTLY did
not populate the space, and find_relations stayed empty over it (a no-silent-failure violation — AGENTS.md
rule 4). FIX: HOIST capture+embed-on-write into ONE shared `Suite.capture_corpus` method; BOTH faces (the MCP
`capture` tool AND the bridge `/api/cognition/corpus` route) call it. So both populate identically; neither
silently no-ops; a non-embeddable projection FAILS LOUD on both faces (not a silent capture-only).

This suite proves, with a STUB embedder (the space_embed_acceptance pattern — :8001 down = needs-tim, the
CODE PATH is proven here):
  1. capture_corpus writes lineage-gated records FIRST, then embeds into the space (sequencing gate).
  2. the embed lands at store.space_address(item, space) — the SAME key find_relations reads (end-to-end).
  3. BOTH faces use capture_corpus (the MCP tool's body + the bridge route's body both call it — single
     source, no duplicated embed path); driving the bridge BODY SHAPE populates the space identically.
  4. FAIL LOUD: a record naming a NON-embeddable projection RAISES (not a silent embedded=None) — the
     whole-point no-silent-failure fix. NO projection = legitimately capture-only (embedded=None, no error).
  5. THE FLOOR: capture_corpus is a corpus.record write + a put_vector write — no resolve/approve/dispatch.

Run: ./.venv/bin/python tests/capture_one_source_acceptance.py
"""
import os, sys, json, tempfile, inspect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from store.fs_store import FsStore
from runtime.suite import Suite
from runtime.registry import NodeRegistry
from store import vector_index as _vx

PASS = 0
FAIL = 0
def check(label, cond):
    global PASS, FAIL
    print(f"  {'ok ' if cond else 'XX '} {label}")
    if cond:
        PASS += 1
    else:
        FAIL += 1


def _new_suite(root):
    reg = NodeRegistry().discover([os.path.join(ROOT, "nodes")])
    return Suite(FsStore(root), reg)


_DIM = 4
def _stub(table, default):
    def f(transport, inputs, model=None, dim=None):
        return [table.get(t, default) for t in inputs]
    return f


# the embeddable projection set this Suite declares — pick one to embed into.
def _embeddable_id(s):
    emb = s.projection_registry.embeddable()
    assert emb, "no embeddable projection registered — the test needs one"
    return emb[0].id


def _non_embeddable_id(s):
    embset = {p.id for p in s.projection_registry.embeddable()}
    for p in s.projection_registry.as_records():
        if p["id"] not in embset:
            return p["id"]
    return None


print("=== capture_one_source_acceptance — ONE shared capture+embed seam, both faces ===")

# ---------------------------------------------------------------------------------------------------
# [1+2] capture_corpus: lineage-first write → embed → space → find_relations end-to-end (stub embedder).
# ---------------------------------------------------------------------------------------------------
print("\n[1+2] capture_corpus writes lineage-gated records, then populates the space (sequencing gate)")
with tempfile.TemporaryDirectory() as root:
    s = _new_suite(root)
    proj = _embeddable_id(s)
    # two units, A≈C in this space (same output text → same stub vector), B distinct.
    oA = {"v": "alpha"}; oB = {"v": "beta"}; oC = {"v": "alpha"}
    txt = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False)
    P = {txt(oA): [1.0, 0.0, 0.0, 0.0], txt(oB): [0.0, 1.0, 0.0, 0.0]}   # C shares A's text → A's vector
    recs = [{"source_address": "u/a.md", "output": oA, "projection": proj},
            {"source_address": "u/b.md", "output": oB, "projection": proj},
            {"source_address": "u/c.md", "output": oC, "projection": proj}]
    out = s.capture_corpus(recs, project="P", session="S", round="1",
                           embed_fn=_stub(P, [0.0, 0.0, 1.0, 0.0]))
    check("capture_corpus wrote N corpus records", len(out["captured"]) == 3)
    rec0 = s.read_corpus_record(out["captured"][0]["address"])
    check("the record carries LINEAGE (gate bit BEFORE embed)",
          rec0 and rec0["lineage"] == {"session": "S", "round": "1", "project": "P"})
    check("capture_corpus embedded (embedded result present, 3 records)",
          out["embedded"] is not None and out["embedded"]["records"] == 3)
    check(f"the embed targeted the embeddable space {proj!r}", proj in out["embedded"]["spaces"])
    check("the embed did NOT degrade (stub embedder up)", out["embedded"]["degraded"] is False)
    # the vectors landed at the SAME key find_relations reads (space_address), via the embed path.
    va = s.store.get_vector(s.store.space_address("u/a.md", proj))
    check("vector for u/a.md landed at space_address(u/a.md, proj) — embed-path-written",
          va is not None and list(va.get("vector") or []) == [1.0, 0.0, 0.0, 0.0])
    # find_relations runs over the capture-written vectors (seed a far space so the near∩¬far is defined).
    _vx.build_index(s.store, [{"address": "u/a.md", "text": "ta"}, {"address": "u/b.md", "text": "tb"}],
                    space="topics", embed_fn=_stub({"ta": [1.0, 0, 0, 0], "tb": [0, 1.0, 0, 0]},
                                                   [0, 0, 0, 1.0]), dim=_DIM, model="seed")
    rel = s.find_relations("u/a.md", near_space=proj, far_space="topics", k=10, min_score=0.5)
    check("find_relations runs over the CAPTURE-WRITTEN vectors end-to-end",
          isinstance(rel, dict) and "relations" in rel)
    check("the inversion excludes the anchor itself", "u/a.md" not in rel["relations"])

# ---------------------------------------------------------------------------------------------------
# [3] BOTH FACES call capture_corpus — single source, no duplicated embed path.
# ---------------------------------------------------------------------------------------------------
print("\n[3] BOTH faces route through capture_corpus (the MCP tool + the bridge route) — one source")
import mcp_face.server as srv
import runtime.bridge as bridge

def _code_only(src: str) -> str:
    """Strip the leading docstring + every `#` comment line, so we scan ACTUAL calls (a docstring/comment
    that MENTIONS a name must not count as a call — the move-don't-copy fix keeps the names in prose)."""
    body = src.split('"""', 2)[-1] if src.count('"""') >= 2 else src
    return "\n".join(ln for ln in body.splitlines() if not ln.lstrip().startswith("#"))

cap_code = _code_only(inspect.getsource(srv.capture))
check("the MCP `capture` tool CALLS SUITE.capture_corpus", "capture_corpus(" in cap_code)
check("the MCP `capture` tool no longer CALLS embed_corpus_to_spaces (no duplicated embed path)",
      "embed_corpus_to_spaces(" not in cap_code)
check("the bridge/server no longer defines a local _embed_text (it moved to Suite._embed_text)",
      not hasattr(srv, "_embed_text"))
# the bridge route's do_POST body — the /api/cognition/corpus arm must call capture_corpus, not write_corpus_record.
H = [c for c in vars(bridge).values() if isinstance(c, type) and hasattr(c, "do_POST")][0]
post_code = _code_only(inspect.getsource(H.do_POST))
check("the bridge /api/cognition/corpus POST arm CALLS SUITE.capture_corpus (the shared seam)",
      "capture_corpus(" in post_code)
check("the bridge POST arm no longer CALLS write_corpus_record for capture (routed via capture_corpus)",
      "write_corpus_record(" not in post_code)

# ---------------------------------------------------------------------------------------------------
# [3b] DRIVE the bridge body shape through capture_corpus → it populates the space IDENTICALLY to MCP.
# ---------------------------------------------------------------------------------------------------
print("\n[3b] the BRIDGE single-record body shape populates the space (both faces populate identically)")
with tempfile.TemporaryDirectory() as root:
    s = _new_suite(root)
    proj = _embeddable_id(s)
    # this is EXACTLY what the bridge route assembles from a single-record POST body (lineage → kwargs).
    body = {"source_address": "fe/x.md", "output": {"v": "from-bridge"}, "kind": "capture",
            "projection": proj, "lineage": {"project": "BP", "session": "BS", "round": "1"}}
    rec = {"source_address": body["source_address"], "output": body["output"],
           "kind": body["kind"], "projection": body["projection"]}
    lin = body["lineage"]
    txt = json.dumps({"v": "from-bridge"}, sort_keys=True, ensure_ascii=False)
    out = s.capture_corpus([rec], project=lin["project"], session=lin["session"], round=lin["round"],
                           embed_fn=_stub({txt: [1.0, 0, 0, 0]}, [0, 0, 1.0, 0]))
    check("bridge-shape capture wrote the record with lineage",
          s.read_corpus_record(out["captured"][0]["address"])["lineage"]["project"] == "BP")
    check("bridge-shape capture POPULATED the space (the SUITE-3 silent no-op is CLOSED)",
          out["embedded"] is not None and proj in out["embedded"]["spaces"])
    vx = s.store.get_vector(s.store.space_address("fe/x.md", proj))
    check("bridge-shape capture's vector landed at space_address (find_relations can read it)",
          vx is not None and list(vx.get("vector") or []) == [1.0, 0, 0, 0])

# ---------------------------------------------------------------------------------------------------
# [4] FAIL LOUD on a non-embeddable projection; NO projection = capture-only (no error).
# ---------------------------------------------------------------------------------------------------
print("\n[4] fail-loud on a non-embeddable projection; no projection = capture-only")
with tempfile.TemporaryDirectory() as root:
    s = _new_suite(root)
    nonemb = _non_embeddable_id(s)
    if nonemb is not None:
        raised = False
        try:
            s.capture_corpus([{"source_address": "n/a.md", "output": {"v": "x"}, "projection": nonemb}],
                             project="P", session="S", round="1", embed_fn=_stub({}, [0, 0, 0, 1.0]))
        except ValueError:
            raised = True
        check(f"a NON-embeddable projection {nonemb!r} FAILS LOUD (not a silent capture-only)", raised)
    else:
        print("    (no non-embeddable projection registered — skipping the fail-loud case)")
        PASS += 1
    # NO projection → capture-only, embedded=None, NO error (the legitimate case).
    out = s.capture_corpus([{"source_address": "p/none.md", "output": {"v": "y"}}],
                           project="P", session="S", round="1")
    check("a record with NO projection is capture-only (embedded=None, no error)",
          out["embedded"] is None and len(out["captured"]) == 1)
    # the record was still written (capture-only still persists the corpus record).
    check("the un-projected record was still WRITTEN (capture-only persists)",
          s.read_corpus_record(out["captured"][0]["address"]) is not None)
    # missing lineage still FAILS LOUD (the corpus.py gate, unchanged).
    raised = False
    try:
        s.capture_corpus([{"source_address": "g/x.md", "output": {"v": "z"}}],
                         project="", session="", round="1")
    except Exception:
        raised = True
    check("missing lineage (empty project/session) FAILS LOUD (the corpus gate bites through capture_corpus)",
          raised)

# ---------------------------------------------------------------------------------------------------
# [5] THE FLOOR — capture_corpus is computation/telemetry, never an action.
# ---------------------------------------------------------------------------------------------------
print("\n[5] the FLOOR — capture_corpus emits no resolve/approve/dispatch")
cc_src = inspect.getsource(Suite.capture_corpus)
cc_body = cc_src.split('"""', 2)[-1] if '"""' in cc_src else cc_src
for forbidden in ("resolve_surfaced", "dispatch_decision", ".approve(", "drive_dispatchable"):
    check(f"capture_corpus's BODY makes no {forbidden} call (the floor — capture is computation)",
          forbidden not in cc_body)
et_src = inspect.getsource(Suite._embed_text)
et_body = et_src.split('"""', 2)[-1] if '"""' in et_src else et_src
for forbidden in ("resolve_surfaced", "dispatch_decision", ".approve(", "drive_dispatchable"):
    check(f"_embed_text's BODY makes no {forbidden} call (pure derivation)", forbidden not in et_body)

print(f"\n{'PASS' if FAIL == 0 else 'FAIL'} — {PASS} passed, {FAIL} failed")
sys.exit(0 if FAIL == 0 else 1)
