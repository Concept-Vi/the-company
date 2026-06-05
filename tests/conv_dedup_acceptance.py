"""tests/conv_dedup_acceptance.py — Convergence X8 · dedup the R2 gather (kill the double-count).

THE DEFECT (Research Synthesis, Round 4 — Observed, file:line):
  A single clicked comment flows through `ingest_comment` and lands as THREE strata at the SAME address:
    1. an ANNOTATION on its annotations.jsonl branch  — full text (suite.py:2063 → annotate:2029)
    2. the located-gold CHAT turn (append_chat)        — full text (suite.py:2065)
    3. ONE addressed EVENT echo (`_emit("annotation",…)` suite.py:2032) whose summary is the text
       TRUNCATED to 40 chars (`rec['text'][:40]`)
  So `_r2_gather` returns it 2–3× and it consumes 2–3× the bounded R2 window — a double-count, NOT three
  distinct notebook items. (`append_chat` is called DIRECTLY, not via attach_chat, precisely so a SECOND
  event isn't emitted — suite.py:2060-61 — so the comment yields exactly one event echo.)

THE FIX: `_r2_gather` collapses same-comment items to ONE before the cap, by an `(address, underlying-
text)` identity that is ROBUST to the 40-char truncation:
  • annotation ↔ chat: exact (address, full text) → one survivor (the full-text item).
  • the event echo: dropped iff its (truncated) text is a PREFIX of a kept annotation/chat full-text at
    the same address — so the narration echo is killed WITHOUT flat-keying on a 40-char prefix (which
    would wrongly merge two distinct comments sharing a 40-char opening).

PROOF MODEL (the truncation trap deliberately defused):
  • THE COMMENT IS LONGER THAN 40 CHARS — so the event text is a strict prefix of the full text, and a
    naive full-text key would MISS the event (leaving 2×). We assert it collapses to exactly ONE and the
    survivor carries text PAST position 40 (proving the full-text item won, not the truncated echo).
  • TWO GENUINELY-DISTINCT comments at the same address are BOTH kept (never over-collapsed) — incl. the
    adversarial case of two comments that share a long (>40-char) common prefix but differ later.
  • PRESERVE — the cap + the recency·proximity·pin ranking are unchanged: dedup only frees budget. A
    non-comment event (no comment-echo shape) is never dropped.

Run: /home/tim/company/.venv/bin/python tests/conv_dedup_acceptance.py
"""
import os
import sys
import tempfile
import shutil
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


NODES = os.path.join(ROOT, "nodes")
LOCUS = "ui://chrome/inbox"
PARENT = "ui://chrome"

store_dir = tempfile.mkdtemp(prefix="conv-dedup-")
try:
    reg = NodeRegistry(); reg.discover([NODES])

    # ════════════════════════════════════════════════════════════════════════════════════════════
    # PART 1 — ONE clicked comment (annotation+chat+event) counts ONCE in the gather (the core fix)
    # ════════════════════════════════════════════════════════════════════════════════════════════
    s1 = Suite(FsStore(os.path.join(store_dir, "s1")), reg, nodes_dir=NODES)
    # LONGER THAN 40 CHARS — defuses the truncation trap: the event echo is a strict prefix, so a naive
    # full-text key would miss it. The 40th char boundary falls mid-text; we assert the survivor goes past it.
    COMMENT = "this inbox card is misaligned and the spacing is wrong, please fix the padding too"
    assert len(COMMENT) > 40, "fixture must exceed 40 chars to exercise the event-echo truncation path"
    s1.ingest_comment(LOCUS, COMMENT, source="operator")

    items = s1._r2_gather(LOCUS)
    # how many gathered items carry this comment's text (in any of its three wrapped forms)?
    def carries(it):
        t = it.get("text", "") or ""
        return COMMENT in t or COMMENT[:40] in t
    matches = [it for it in items if carries(it)]
    check("X8: ONE clicked comment appears exactly ONCE in the gather (was 2-3×: annotation+chat+event)",
          len(matches) == 1)
    survivor = matches[0]
    check("X8: the survivor is the FULL-TEXT item, not the 40-char-truncated event echo",
          COMMENT in (survivor.get("text", "") or ""))
    check("X8: the survivor carries text PAST position 40 (proves the full item won, not the truncation)",
          COMMENT[40:60] in (survivor.get("text", "") or ""))
    check("X8: the survivor is NOT the event echo (it is the annotation/chat stratum, full content)",
          survivor.get("kind") in ("annotation", "chat"))

    # ════════════════════════════════════════════════════════════════════════════════════════════
    # PART 2 — TWO GENUINELY-DISTINCT comments are BOTH kept (never over-collapse distinct items)
    # ════════════════════════════════════════════════════════════════════════════════════════════
    s2 = Suite(FsStore(os.path.join(store_dir, "s2")), reg, nodes_dir=NODES)
    C_A = "the run button colour is too aggressive, soften it"
    C_B = "the inbox list needs more vertical breathing room"
    s2.ingest_comment(LOCUS, C_A, source="operator")
    s2.ingest_comment(LOCUS, C_B, source="operator")
    items2 = s2._r2_gather(LOCUS)
    has_a = sum(1 for it in items2 if C_A in (it.get("text", "") or ""))
    has_b = sum(1 for it in items2 if C_B in (it.get("text", "") or ""))
    check("X8: two distinct comments are BOTH present (distinct items never dropped)", has_a >= 1 and has_b >= 1)
    check("X8: each distinct comment still counts exactly ONCE (each deduped independently)",
          has_a == 1 and has_b == 1)

    # ADVERSARIAL: two comments that share a >40-char common prefix but DIFFER later — must stay distinct
    # (proves the dedup keys on the FULL text for annotation/chat, not a 40-char prefix).
    s3 = Suite(FsStore(os.path.join(store_dir, "s3")), reg, nodes_dir=NODES)
    PRE = "the settings panel header alignment is off by a few pixels "   # >40 chars shared
    assert len(PRE) > 40
    P_A = PRE + "on desktop at 1440 width"
    P_B = PRE + "on mobile at 390 width"
    s3.ingest_comment(LOCUS, P_A, source="operator")
    s3.ingest_comment(LOCUS, P_B, source="operator")
    items3 = s3._r2_gather(LOCUS)
    cnt_a = sum(1 for it in items3 if P_A in (it.get("text", "") or ""))
    cnt_b = sum(1 for it in items3 if P_B in (it.get("text", "") or ""))
    check("X8 adversarial: two comments sharing a >40-char prefix stay DISTINCT (full-text key, not prefix)",
          cnt_a == 1 and cnt_b == 1)

    # ════════════════════════════════════════════════════════════════════════════════════════════
    # PART 3 — PRESERVE: the cap holds + ranking unchanged + a non-comment event is never dropped
    # ════════════════════════════════════════════════════════════════════════════════════════════
    s4 = Suite(FsStore(os.path.join(store_dir, "s4")), reg, nodes_dir=NODES)
    now = datetime.now(timezone.utc)
    # attach MANY distinct annotations directly (each unique text) — the cap proof from addr_context
    N = 40
    store4 = s4.store
    for i in range(N):
        ts = now - timedelta(seconds=(N - i) * 10)
        store4.append_annotation({"kind": "annotation", "address": LOCUS,
                                  "text": f"ITEM-{i:03d} " + ("x" * 100), "ts": ts.isoformat(),
                                  "source": "operator"})
    items4 = s4._r2_gather(LOCUS)
    check("PRESERVE: distinct annotations are NOT deduped away (all N survive the gather)",
          sum(1 for it in items4 if it.get("kind") == "annotation"
              and it.get("text", "").startswith("[comment @")) >= N)
    capped = s4._r2_score_and_cap(items4, LOCUS, now)
    capped_text = "\n".join(it.get("text", "") for it in capped)
    check("PRESERVE: the budget cap still holds (≤ R2_BUDGET chars) after dedup", len(capped_text) <= s4.R2_BUDGET)
    check("PRESERVE: the cap still DROPS items (cap unchanged by dedup)", len(capped) < N)
    check("PRESERVE: the highest-scored (most-recent) item still survives (ITEM-039)",
          any("ITEM-039" in it.get("text", "") for it in capped))
    check("PRESERVE: the lowest-scored (oldest) item is still DROPPED (ITEM-000 absent)",
          not any("ITEM-000" in it.get("text", "") for it in capped))

    # a NON-comment addressed event (e.g. a chat attach echo) is NOT a comment echo → never dropped
    s5 = Suite(FsStore(os.path.join(store_dir, "s5")), reg, nodes_dir=NODES)
    s5.attach_chat(LOCUS, "why is this build stuck", role="user")   # emits its own addressed event
    items5 = s5._r2_gather(LOCUS)
    ev_present = any(it.get("kind") == "event" for it in items5)
    check("PRESERVE: a non-comment addressed event survives the dedup (conservative — only echoes dropped)",
          ev_present)

    # END-TO-END through the production R2 entry: the deduped slice still resolves cleanly (no crash)
    s1.annotate(PARENT, "a parent-address note for proximity")
    ctx = s1._resolve_context_at(LOCUS)
    check("PRESERVE: _resolve_context_at still produces the locus block after dedup (no crash)",
          "CONTEXT RESOLVED AT YOUR LOCUS" in ctx and COMMENT in ctx)
    # and the deduped comment appears ONCE in the resolved block, not twice
    check("X8 end-to-end: the comment appears ONCE in the resolved R2 block (not double-counted)",
          ctx.count(COMMENT) == 1)

    print(f"\nCONV DEDUP ACCEPTANCE (X8) — {PASS} checks passed. A single clicked comment "
          f"(annotation+chat+event) counts ONCE in the R2 gather; the survivor is the full-text item "
          f"(not the 40-char-truncated event echo); two genuinely-distinct comments (incl. a >40-char "
          f"shared prefix) are both kept; the budget cap + recency·proximity·pin ranking + a non-comment "
          f"event are all preserved.")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
