"""tests/marks_acceptance.py — the marks store (cognition-engine GROUP M) = the finding store, GENERALIZED.

By USE, pure store primitives (no model, no engine — store constitution: turns an address into bytes and
back, never calls a model). Proves the marks-generalization the Implementation Guide §4.2 specs (which
supersedes M1's "same shape" over-claim): a MARK extends the coherence finding record along two axes the
finding shape can't carry —

  1. TARGET, not just an address — a CLAIM target or a SPAN target (a sub-region), as well as a plain address;
  2. mark_type + the mark payload — retrievable BY mark_type (the finding's address-only key can't do this).

Verified by use:
  · write a mark on a CLAIM target (with a mark_type id) → retrievable BY target AND BY mark_type;
  · write a mark on a SPAN target → retrievable;
  · persistence-survives-reload (a 2nd Suite/store over the same root sees the marks);
  · PRESERVED — an OLD finding (written pre-generalization, into findings.jsonl) STILL READS, byte-for-byte,
    through findings_for/all_findings, and a mark NEVER leaks into the finding corpus (so the live
    coherence_detect.burn_down orphan count is unpolluted — the regression the same-file layout would cause);
  · STRUCTURAL fail-loud — a mark with a missing/empty target or mark_type is REFUSED (an unfindable mark is a
    silent black hole; store rule 4).

The store does NOT define or validate the claim/span/address grammar (that is the C1 contract + the Suite's
S0 gate — a SEPARATE lane), and does NOT import the mark-types registry (mark_type is an opaque string id from
a SEPARATE lane). The target/mark_type strings below are ILLUSTRATIVE.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

root = os.path.join(tempfile.mkdtemp(prefix="marks-"), "store")
store = FsStore(root)

# ── PRESERVATION SETUP · an OLD finding, written the pre-generalization way (into findings.jsonl) ─────────
# This record exists BEFORE marks were a thing. The whole point of the sibling-leaf layout is that it keeps
# reading exactly as before. We capture the finding corpus state now and re-assert it is UNCHANGED after marks.
old_finding = store.append_finding({"kind": "unwired-route", "address": "code://bridge/api_knobs",
                                    "state": "built-no-caller", "evidence": "no caller", "source": "structural"})
check("an old finding writes + reads at its address (the pre-generalization path is intact)",
      len(store.findings_for("code://bridge/api_knobs")) == 1)
findings_before = store.all_findings()
check("finding corpus has exactly the 1 old finding before any mark", len(findings_before) == 1)

# ── AXIS 1 · a mark on a CLAIM target (a claim handle, not a plain address) ───────────────────────────────
# Illustrative claim handle — the store treats it as an OPAQUE string (does NOT parse `claim://...#...`).
CLAIM = "claim://design/principles.md#3"
m_claim = store.append_mark({"target": CLAIM, "mark_type": "principle-beneath",
                             "value": "this paragraph is an instance of the addressing principle",
                             "confidence": 0.82, "source_pass": "project:principle", "evidence": "para 3"})
check("append_mark returns the record with a ts stamped", "ts" in m_claim and m_claim["target"] == CLAIM)

# retrievable BY TARGET
by_target = store.marks_for(CLAIM)
check("marks_for(claim) returns the mark at its claim target",
      len(by_target) == 1 and by_target[0]["mark_type"] == "principle-beneath"
      and by_target[0]["confidence"] == 0.82)
check("a different target has no marks", store.marks_for("claim://other/thing#1") == [])

# retrievable BY mark_type (the second axis — the finding store's address-only key can't do this)
by_type = store.marks_by_type("principle-beneath")
check("marks_by_type(mark_type) returns the mark by its type", len(by_type) == 1 and by_type[0]["target"] == CLAIM)
check("an absent mark_type has no marks", store.marks_by_type("nonexistent-type") == [])

# ── AXIS 1b · a SPAN target (a sub-region handle) — also retrievable ──────────────────────────────────────
SPAN = "span://code/fs_store.py#534-548"
store.append_mark({"target": SPAN, "mark_type": "ai-fingerprint",
                   "value": "closure-form phrasing", "confidence": 0.6, "source_pass": "invert:fingerprint",
                   "evidence": "the doc-comment shape"})
check("a SPAN-target mark is retrievable by its span target", len(store.marks_for(SPAN)) == 1)
check("the span mark is retrievable by its mark_type", len(store.marks_by_type("ai-fingerprint")) == 1)
check("by-type does NOT cross types (principle-beneath still returns only its 1 mark)",
      len(store.marks_by_type("principle-beneath")) == 1)

# ── append-only THREAD · a mark-pass re-run re-appends (own/reflect, mirrors findings) ────────────────────
store.append_mark({"target": CLAIM, "mark_type": "principle-beneath", "value": "re-marked this pass",
                   "confidence": 0.9, "source_pass": "project:principle"})
check("re-running a mark-pass re-appends on the target (append-only thread — 2 now)",
      len(store.marks_for(CLAIM)) == 2)
check("by-type also sees both principle-beneath marks", len(store.marks_by_type("principle-beneath")) == 2)
check("all_marks() returns every mark record across targets/types (3 total)", len(store.all_marks()) == 3)

# ── by-type's PURPOSE · CROSS-TARGET aggregation (what marks_by_type does that marks_for can't) ───────────
# A principle-beneath mark on a DIFFERENT target. marks_by_type must aggregate ACROSS targets — that is the
# whole reason it exists beside marks_for (which is single-target). Asserts the cross-target fold, not just
# the by-type filter.
OTHER_CLAIM = "claim://design/AGENTS.md#1"
store.append_mark({"target": OTHER_CLAIM, "mark_type": "principle-beneath",
                   "value": "a different item, same mark type", "confidence": 0.7, "source_pass": "project:principle"})
across = store.marks_by_type("principle-beneath")
check("marks_by_type AGGREGATES ACROSS targets (3 principle-beneath marks now, on 2 distinct targets)",
      len(across) == 3 and len({m["target"] for m in across}) == 2)
check("marks_for stays SINGLE-target (the original claim still has only its 2)", len(store.marks_for(CLAIM)) == 2)
check("all_marks() now 4 across all targets/types", len(store.all_marks()) == 4)

# ── PERSISTENCE survives reload · a SECOND store over the same root sees the marks ────────────────────────
store2 = FsStore(root)
check("persistence survives reload — 2nd store sees the claim mark by target", len(store2.marks_for(CLAIM)) == 2)
check("persistence survives reload — 2nd store sees by mark_type", len(store2.marks_by_type("ai-fingerprint")) == 1)
check("persistence survives reload — 2nd store sees all 4 marks", len(store2.all_marks()) == 4)

# ── PRESERVED · the OLD finding STILL reads, byte-for-byte; marks NEVER leak into the finding corpus ──────
# This is the load-bearing preservation guarantee: the sibling-leaf layout means findings.jsonl is byte-for-
# byte untouched, so coherence_detect.burn_down (which counts all_findings) is unpolluted by the 3 marks.
check("the old finding STILL reads at its address after 3 marks (preserved)",
      len(store.findings_for("code://bridge/api_knobs")) == 1)
findings_after = store.all_findings()
check("the finding corpus is UNCHANGED by marks (still exactly the 1 finding — no mark leaked in)",
      len(findings_after) == 1 and findings_after == findings_before)
# inverse: no finding leaked into the marks corpus either
check("no finding leaked into the marks corpus (the leaves are disjoint)",
      all(r.get("kind") != "unwired-route" for r in store.all_marks()))

# ── STRUCTURAL fail-loud · an unfindable mark (missing/empty key) is REFUSED ──────────────────────────────
def refused(label, fn):
    try:
        fn()
        check(label + " (should have raised)", False)
    except ValueError:
        check(label, True)

refused("a mark with NO target is refused (fail-loud — unfindable)",
        lambda: store.append_mark({"mark_type": "principle-beneath", "value": "x"}))
refused("a mark with an EMPTY target is refused",
        lambda: store.append_mark({"target": "   ", "mark_type": "principle-beneath"}))
refused("a mark with NO mark_type is refused (fail-loud — no second key)",
        lambda: store.append_mark({"target": CLAIM, "value": "x"}))
refused("a mark with an EMPTY mark_type is refused",
        lambda: store.append_mark({"target": CLAIM, "mark_type": ""}))
# a refused write left NOTHING behind (fail-loud, not partial)
check("a refused mark wrote nothing (still 4 marks)", len(store.all_marks()) == 4)

print(f"\nALL {PASS} CHECKS PASS — marks store = the finding store GENERALIZED (claim/span target + mark_type "
      f"retrieval), on a sibling leaf. Old findings preserved byte-for-byte (burn-down unpolluted); marks "
      f"retrievable by target AND by mark_type; persistence survives reload; structural fail-loud. The "
      f"suite-side API + the `mark` MCP tool + the mark-types registry are SEPARATE next passes (other lanes).")
