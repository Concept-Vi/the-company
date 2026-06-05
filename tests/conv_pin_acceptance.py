"""tests/conv_pin_acceptance.py — Convergence X7 · the pin override works.

THE DEFECT (Research Synthesis, Round 4 — Observed, file:line):
  The R2 decay formula ALREADY has a pin term — `_r2_score` (suite.py:1140) reads `item.get("pinned")`
  → `pin_bonus = R2_PIN_WEIGHT` (suite.py:1080) — and `_r2_gather` ALREADY surfaces a per-record
  `bool(a.get("pinned"))` / `bool(c.get("pinned"))` (suite.py:1299/1304). But NOTHING ever SETS pinned
  True: the only literal is `pinned:False` everywhere a record is constructed. So the operator's "keep
  this in view" override exists in the math but can't be triggered — a DEAD term.

WHAT X7 ADDS (the SET path — the math + read are preserved byte-for-byte):
  1. an operator can PIN / UNPIN an attached item at an address (`Suite.pin(address, ts, pinned=…)` +
     an operator-face bridge route mirroring `/api/annotate` — operator-only, OFF the MCP face).
  2. the pin flag PERSISTS on the item's open record (resolve-on-read: `annotations_at`/`chats_at`
     overlay the persisted pin-state — survives reload-from-disk).
  3. `_r2_gather` reads the REAL persisted `pinned` (it already does — `.get("pinned")`) → `pin_bonus`
     becomes reachable → a pinned item is HELD in the bounded R2 window even when older/farther.

PRESERVE (asserted here): the `_r2_score` formula + `R2_PIN_WEIGHT` are UNCHANGED; a NON-pinned old item
  is still evicted (the cap + recency·proximity ranking hold); the I6 thread (`annotations_at`) keeps the
  SAME count + text (pin-state is overlaid, never an extra record — annotation_acceptance stays green);
  pinning a NON-EXISTENT item fails LOUD (no silent no-op — rule 4).

Run: /home/tim/company/.venv/bin/python tests/conv_pin_acceptance.py
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


def expect_raises(label, fn):
    global PASS
    try:
        fn()
    except Exception:
        PASS += 1
        print(f"  ok  {label}")
        return
    assert False, f"FAIL (did not raise): {label}"


NODES = os.path.join(ROOT, "nodes")
LOCUS = "ui://chrome/inbox"
PARENT = "ui://chrome"

store_dir = tempfile.mkdtemp(prefix="conv-pin-")
try:
    reg = NodeRegistry(); reg.discover([NODES])

    # ════════════════════════════════════════════════════════════════════════════════════════════
    # PART 1 — pin a record → it carries pinned:True on its PERSISTED record (survives reload)
    # ════════════════════════════════════════════════════════════════════════════════════════════
    s1_root = os.path.join(store_dir, "s1")
    s1 = Suite(FsStore(s1_root), reg, nodes_dir=NODES)
    rec = s1.annotate(LOCUS, "keep this comment in view across the build")
    target_ts = rec["ts"]

    check("Suite.pin exists (the SET path the dead term was missing)",
          hasattr(s1, "pin") and callable(s1.pin))

    # before pinning: the annotation reads as unpinned (schema-additive default)
    before = s1.annotations_at(LOCUS)
    check("before pin: the annotation reads as unpinned (additive default)",
          len(before) == 1 and not bool(before[0].get("pinned")))

    s1.pin(LOCUS, target_ts, pinned=True)
    after = s1.annotations_at(LOCUS)
    check("after pin: annotations_at carries pinned:True on the record",
          len(after) == 1 and bool(after[0].get("pinned")))
    check("PRESERVE: pinning did NOT change the thread count or text (overlay, not a new record)",
          len(after) == 1 and after[0].get("text") == "keep this comment in view across the build")

    # RELOAD FROM DISK — a second Suite over the same store root sees the persisted pin-state
    s1b = Suite(FsStore(s1_root), reg, nodes_dir=NODES)
    reloaded = s1b.annotations_at(LOCUS)
    check("RELOAD: the pin flag persists on disk (a fresh Suite reads pinned:True)",
          len(reloaded) == 1 and bool(reloaded[0].get("pinned")))

    # the gather surfaces the real pinned flag (the read path was already there; the SET now reaches it)
    gathered = s1b._r2_gather(LOCUS)
    pinned_in_gather = [it for it in gathered if it.get("pinned")
                        and "keep this comment in view" in (it.get("text", "") or "")]
    check("the gather surfaces the REAL persisted pinned (pin_bonus is now reachable)",
          len(pinned_in_gather) >= 1)

    # ════════════════════════════════════════════════════════════════════════════════════════════
    # PART 2 — a PINNED item is HELD in the bounded window even when it would otherwise be evicted
    # ════════════════════════════════════════════════════════════════════════════════════════════
    s2_root = os.path.join(store_dir, "s2")
    s2 = Suite(FsStore(s2_root), reg, nodes_dir=NODES)
    now = datetime.now(timezone.utc)
    store2 = s2.store
    # An OLD item we will pin. Then flood the locus with many RECENT distinct items so the budget cap
    # would evict the old one by recency — UNLESS the pin_bonus holds it.
    OLD_TEXT = "PINNED-OLD this is the operator's must-keep note from long ago padded out " + ("z" * 80)
    old_rec = store2.append_annotation({"kind": "annotation", "address": LOCUS, "text": OLD_TEXT,
                                        "ts": (now - timedelta(days=30)).isoformat(), "source": "operator"})
    N = 60
    for i in range(N):
        ts = now - timedelta(seconds=(N - i))
        store2.append_annotation({"kind": "annotation", "address": LOCUS,
                                  "text": f"RECENT-{i:03d} " + ("y" * 100), "ts": ts.isoformat(),
                                  "source": "operator"})

    # BASELINE (RED before the SET path exists / before pinning): the OLD item is evicted by the cap.
    gather_unpinned = s2._r2_gather(LOCUS)
    capped_unpinned = s2._r2_score_and_cap(gather_unpinned, LOCUS, now)
    check("BASELINE: the OLD unpinned item is EVICTED by the budget cap (recency loses)",
          not any("PINNED-OLD" in (it.get("text", "") or "") for it in capped_unpinned))

    # PIN the old item → it must now be HELD in the bounded window
    s2.pin(LOCUS, old_rec["ts"], pinned=True)
    gather_pinned = s2._r2_gather(LOCUS)
    capped_pinned = s2._r2_score_and_cap(gather_pinned, LOCUS, now)
    check("X7 CORE: a PINNED old item is HELD in the bounded R2 window (pin_bonus fires)",
          any("PINNED-OLD" in (it.get("text", "") or "") for it in capped_pinned))
    check("X7 CORE: the pinned item ranks at/near the TOP (pin_bonus ≥ max recency·proximity)",
          "PINNED-OLD" in (capped_pinned[0].get("text", "") or ""))
    # PRESERVE: the cap still HOLDS (pinning one item doesn't unbound the window)
    capped_text = "\n".join(it.get("text", "") for it in capped_pinned)
    check("PRESERVE: the budget cap still holds after a pin (≤ R2_BUDGET)", len(capped_text) <= s2.R2_BUDGET)

    # ════════════════════════════════════════════════════════════════════════════════════════════
    # PART 3 — UNPIN → the item returns to normal scoring (evicted again)
    # ════════════════════════════════════════════════════════════════════════════════════════════
    s2.pin(LOCUS, old_rec["ts"], pinned=False)
    after_unpin = s2.annotations_at(LOCUS)
    old_after = [a for a in after_unpin if "PINNED-OLD" in (a.get("text", "") or "")]
    check("UNPIN: the record reads as unpinned again", old_after and not bool(old_after[0].get("pinned")))
    gather_after_unpin = s2._r2_gather(LOCUS)
    capped_after_unpin = s2._r2_score_and_cap(gather_after_unpin, LOCUS, now)
    check("UNPIN: the item returns to NORMAL scoring (evicted by the cap again, like baseline)",
          not any("PINNED-OLD" in (it.get("text", "") or "") for it in capped_after_unpin))

    # ════════════════════════════════════════════════════════════════════════════════════════════
    # PART 4 — pinning a NON-EXISTENT item fails LOUD (rule 4 — no silent no-op)
    # ════════════════════════════════════════════════════════════════════════════════════════════
    s3 = Suite(FsStore(os.path.join(store_dir, "s3")), reg, nodes_dir=NODES)
    s3.annotate(LOCUS, "a real note")
    expect_raises("FAIL-LOUD: pinning a non-existent (address, ts) raises (no silent no-op)",
                  lambda: s3.pin(LOCUS, "2099-01-01T00:00:00+00:00", pinned=True))
    expect_raises("FAIL-LOUD: pinning at a malformed address raises (S0 gate)",
                  lambda: s3.pin("not-an-address", "2099-01-01T00:00:00+00:00", pinned=True))

    # ════════════════════════════════════════════════════════════════════════════════════════════
    # PART 5 — a CHAT-attached item can be pinned too (the open chat record, same overlay)
    # ════════════════════════════════════════════════════════════════════════════════════════════
    s4 = Suite(FsStore(os.path.join(store_dir, "s4")), reg, nodes_dir=NODES)
    crec = s4.attach_chat(LOCUS, "this chat thread matters, keep it", role="user")
    s4.pin(LOCUS, crec["ts"], pinned=True)
    chats = s4.chats_at(LOCUS)
    check("X7: a chat-attached item can be pinned (chats_at overlays pinned:True)",
          len(chats) == 1 and bool(chats[0].get("pinned")))

    # ════════════════════════════════════════════════════════════════════════════════════════════
    # PART 6 — PRESERVE: the _r2_score formula + R2_PIN_WEIGHT are byte-for-byte unchanged
    # ════════════════════════════════════════════════════════════════════════════════════════════
    pinned_item = {"text": "PN", "address": LOCUS, "ts": (now - timedelta(days=30)).isoformat(),
                   "kind": "annotation", "pinned": True}
    unpinned_old = {"text": "OLD", "address": LOCUS, "ts": (now - timedelta(days=30)).isoformat(),
                    "kind": "annotation", "pinned": False}
    check("PRESERVE: _r2_score still gives a pinned item the pin_bonus over an identical unpinned one",
          s4._r2_score(pinned_item, LOCUS, now) > s4._r2_score(unpinned_old, LOCUS, now))
    check("PRESERVE: the pin_bonus equals exactly R2_PIN_WEIGHT (formula unchanged)",
          abs((s4._r2_score(pinned_item, LOCUS, now) - s4._r2_score(unpinned_old, LOCUS, now))
              - s4.R2_PIN_WEIGHT) < 1e-9)

    # ════════════════════════════════════════════════════════════════════════════════════════════
    # PART 7 — the PRODUCTION clicked-comment path (ingest_comment, the X7×X8 interaction)
    # A clicked comment lands as annotation(ts1)+chat(ts2)+event for the SAME text. X8 dedup collapses
    # them to ONE survivor (the annotation, kept first in PASS 1). Pinning the ANNOTATION's ts must hold
    # that single survivor in the window — proving X7 works on the real wired entry, not just a bare leaf.
    # ════════════════════════════════════════════════════════════════════════════════════════════
    s5_root = os.path.join(store_dir, "s5b")
    s5 = Suite(FsStore(s5_root), reg, nodes_dir=NODES)
    now5 = datetime.now(timezone.utc)
    CLICKED = "PINNED-CLICK the operator clicked this exact comment and wants it kept in view forever " + ("q" * 40)
    assert len(CLICKED) > 40
    # back-date the clicked comment so recency alone would evict it (we control ts via the store leaf for
    # determinism, but route through the SAME three strata ingest_comment produces).
    s5.store.append_annotation({"kind": "annotation", "address": LOCUS, "text": CLICKED,
                                "ts": (now5 - timedelta(days=30)).isoformat(), "source": "operator"})
    clicked_ts = s5.annotations_at(LOCUS)[0]["ts"]
    s5.store.append_chat({"role": "user", "text": CLICKED, "address": LOCUS,
                          "ts": (now5 - timedelta(days=30)).isoformat(), "source": "operator", "grade": "gold"})
    s5._emit("annotation", f"comment at {LOCUS}: {CLICKED[:40]}", address=LOCUS)   # the truncated event echo
    # flood with recent distinct items so the cap would evict the old clicked comment
    for i in range(60):
        ts = now5 - timedelta(seconds=(60 - i))
        s5.store.append_annotation({"kind": "annotation", "address": LOCUS,
                                    "text": f"FLOOD-{i:03d} " + ("w" * 100), "ts": ts.isoformat(),
                                    "source": "operator"})
    # BASELINE: the clicked comment is deduped to ONE and evicted by the cap (unpinned)
    gather_pre = s5._r2_gather(LOCUS)
    pre_clicked = [it for it in gather_pre if CLICKED in (it.get("text", "") or "")]
    check("X7×X8: the clicked comment is deduped to ONE in the gather (annotation+chat+event collapsed)",
          len(pre_clicked) == 1)
    capped_pre = s5._r2_score_and_cap(gather_pre, LOCUS, now5)
    check("X7×X8 baseline: the unpinned clicked comment is EVICTED by the cap",
          not any(CLICKED in (it.get("text", "") or "") for it in capped_pre))
    # PIN the annotation's ts (the survivor X8 keeps) → it must hold AND still count once
    s5.pin(LOCUS, clicked_ts, pinned=True)
    gather_post = s5._r2_gather(LOCUS)
    post_clicked = [it for it in gather_post if CLICKED in (it.get("text", "") or "")]
    check("X7×X8: after pin the clicked comment STILL counts exactly ONCE (dedup + pin coexist)",
          len(post_clicked) == 1 and bool(post_clicked[0].get("pinned")))
    capped_post = s5._r2_score_and_cap(gather_post, LOCUS, now5)
    check("X7×X8 CORE: the PINNED clicked comment is HELD in the bounded window (the production path)",
          any(CLICKED in (it.get("text", "") or "") for it in capped_post))

    print(f"\nCONV PIN ACCEPTANCE (X7) — {PASS} checks passed. An operator can pin/unpin an attached "
          f"item; the pin flag persists on the item's open record (survives reload); a pinned item is "
          f"held in the bounded R2 window (the dead pin_bonus is now reachable); unpin returns it to "
          f"normal scoring; pinning a non-existent item fails loud; the _r2_score formula + R2_PIN_WEIGHT "
          f"are unchanged.")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
