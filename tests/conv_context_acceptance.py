"""tests/conv_context_acceptance.py — Convergence X3 · the ATTACHED CONTEXT reaches the payload (R2 gather at mint).

THE PRINCIPLE (Completion Criteria X3 / Implementation Guide X3):
  The build's launch context should inherit the accumulated NOTEBOOK at the address. R2 already
  assembles that bundle for the chat (`_r2_gather` → `_r2_score_and_cap`, bounded by recency·proximity·
  pin decay + the R2_BUDGET cap, deduped by X8). X3: at MINT/consent time, call that SAME gather for the
  build-intent's address and PERSIST the bounded, deduped bundle into the payload — so the surfaced
  record == what the build will later compose from (the consent-time trust property), and X4 can slot it
  into the prompt exactly as it slots `scope`.

THE DEFECT (today): `annotations_at`/`chats_at`/`_r2_gather` exist; the wire never calls them at mint —
  the persisted build-intent carries `address` (X1) + `symbols` (X2) but NOT the attached strata. The
  build never inherits the comments/chats/history accumulated at the locus.

THE FIX (schema-ADDITIVE, rule 2): in `surface_intent_at`, AFTER `resolve_scope` (the mint comment is
  already at the address via `ingest_comment`), call the EXISTING `_r2_gather(addr)` + `_r2_score_and_cap`
  → the bounded, deduped, scored list → thread it into the payload as an additive-optional `context` key
  (the same additive way X1/X2 threaded address/symbols, splatted by `inbox.surface`). REUSE the existing
  gather — NO second gather, the R2_BUDGET cap STAYS, the X8 dedup + `_raw`-strip ride free.

PROOF MODEL:
  • RELOAD FROM DISK — a FRESH Suite on the SAME store root reads the surfaced record back; the reloaded
    payload carries a `context` list that includes the pre-attached item (the build inherits the notebook).
  • BOUNDED (the keystone, mirrors addr_context_acceptance) — attach MANY items exceeding R2_BUDGET, then
    assert the persisted bundle's total text ≤ R2_BUDGET AND a specific low-scored item is ABSENT. "≤ budget"
    alone false-passes; the dropped low-scored item is what PROVES the cap holds (no unbounded dump on disk).
  • DEDUP (X8) — the clicked mint comment (lands as annotation + chat + event) appears EXACTLY ONCE.
  • JSON-CLEAN — every persisted item is the public shape {kind,address,ts,text,pinned} only; NO internal
    `_raw` leaks to disk (X8 strips it in `_r2_gather`).
  • PRESERVE — X1/X2 address+symbols still persist alongside `context`; the existing chat-path is untouched
    (a separate assertion that `_resolve_context_at(locus)` still returns the same bounded string block).

REAL corpus address (verified live, same fixtures conv_payload uses):
  ui://chat/input → symbols=['code://App'], scope=['canvas/app/src/App.tsx']

Run: /home/tim/company/.venv/bin/python tests/conv_context_acceptance.py
"""
import os
import sys
import tempfile

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
STORE_ROOT = os.path.join(tempfile.mkdtemp(prefix="conv-context-"), "store")
store = FsStore(STORE_ROOT)
reg = NodeRegistry(); reg.discover([NODES])
suite = Suite(store, reg, nodes_dir=NODES)

CHATIN = "ui://chat/input"                 # → symbols=['code://App'], scope=['canvas/app/src/App.tsx']

# ── PRE-ATTACH a notebook at the address (the accumulated context the build should inherit) ─────────
# A FAR, OLD item that the cap should DROP (parent address = proximity-farther; attached FIRST = oldest).
# This is the drop-proof for the bounded keystone — its ABSENCE proves the cap actually pruned.
LOWSCORE_MARK = "ZZZ-OLDEST-FARTHEST-LOWEST-SCORE-SHOULD-BE-DROPPED"
PARENT = "ui://chat"   # a parent address (proximity-farther) — first to drop under the cap.
suite.annotate(PARENT, LOWSCORE_MARK + " " + ("filler " * 14), source="operator")

# Attach MANY items so the gather EXCEEDS the R2_BUDGET cap (the bounded keystone needs an overflow).
# Each ~120 chars; >>40 of them blows past R2_BUDGET (4000). The cap keeps the recent+proximate winners.
for i in range(60):
    suite.annotate(CHATIN, f"bulk note #{i:03d} " + ("padding text to consume budget " * 3), source="operator")

# A distinctive comment attached LAST (newest = highest recency) — it MUST survive the cap, so we can
# prove the build inherits a real accumulated note (the notebook) and not just the mint comment.
PREEXISTING = "the run button has felt sluggish since last week — this is the accumulated note"
suite.annotate(CHATIN, PREEXISTING, source="operator")

# sanity: the corpus resolver gives the symbols+scope the X1/X2 assertions lean on
rs = suite.resolve_scope(CHATIN)
check(f"{CHATIN} resolves symbols=['code://App'] (S3, real corpus)", rs["symbols"] == ["code://App"])

# ── mint a build-intent at the address (the L1 mint path that should now gather + persist context) ──
MINT_COMMENT = "this run button is too loud — tone it down"
out = suite.surface_intent_at(CHATIN, MINT_COMMENT, source="operator")
sid = out["id"]

# ════════════════════════════════════════════════════════════════════════════════════════════════
# THE LOAD-BEARING PROOF — reload the PERSISTED record from disk via a FRESH Suite on the same store
# ════════════════════════════════════════════════════════════════════════════════════════════════
store2 = FsStore(STORE_ROOT)
suite2 = Suite(store2, reg, nodes_dir=NODES)
reloaded = suite2.inbox.get(sid)
check("the build-intent persisted and reloads from disk (fresh Suite, same store root)",
      reloaded is not None and Suite.is_build_intent(reloaded))
payload = reloaded["payload"]

# X3 — the attached context reaches disk as a structured bundle (a list of normalised items)
ctx = payload.get("context")
check("X3: the RELOADED payload carries a 'context' bundle (a list, reaches disk)",
      isinstance(ctx, list) and len(ctx) > 0)

# the build INHERITS THE NOTEBOOK: the pre-attached comment is present in the persisted bundle
all_text = "\n".join((it.get("text", "") or "") for it in ctx)
check("X3: the persisted context includes the PRE-ATTACHED comment (the build inherits the notebook)",
      PREEXISTING in all_text)

# ── BOUNDED (the keystone) — the persisted bundle is the SAME bounded slice the chat gets ──────────
total_chars = sum(len(it.get("text", "") or "") for it in ctx)
check(f"X3 BOUNDED: the persisted bundle total text ≤ R2_BUDGET ({Suite.R2_BUDGET}) — NOT an unbounded dump",
      total_chars <= Suite.R2_BUDGET)
check("X3 BOUNDED (keystone): the OLDEST/most-distant low-scored item is ABSENT (the cap actually dropped it)",
      LOWSCORE_MARK not in all_text)
# with 60+ attached bulk items, the bundle must be FEWER than gathered (proof the cap pruned, not kept-all)
check("X3 BOUNDED: the bundle holds FAR fewer items than were attached (the budget pruned the gather)",
      len(ctx) < 60)

# ── DEDUP (X8) — the clicked mint comment counts EXACTLY ONCE across annotation/chat/event ─────────
mint_hits = sum(1 for it in ctx if MINT_COMMENT in (it.get("text", "") or ""))
check("X3 DEDUP (X8): the clicked mint comment appears EXACTLY ONCE (annotation+chat+event collapsed)",
      mint_hits == 1)

# ── JSON-CLEAN — only the public {kind,address,ts,text,pinned} shape; NO internal `_raw` leaks ─────
PUBLIC_KEYS = {"kind", "address", "ts", "text", "pinned"}
check("X3 JSON-CLEAN: NO internal '_raw' field leaks to disk (X8 strips it in _r2_gather)",
      all("_raw" not in it for it in ctx))
check("X3 JSON-CLEAN: every persisted item is the public {kind,address,ts,text,pinned} shape only",
      all(set(it.keys()) <= PUBLIC_KEYS for it in ctx))

# ── PRESERVE — X1/X2 still persist alongside the new context key ───────────────────────────────────
check("PRESERVE X1: the address still reaches disk alongside context", payload.get("address") == CHATIN)
check("PRESERVE X2: the code:// symbol-neighbours still persist alongside context",
      payload.get("symbols") == ["code://App"])
for f in ("intent", "spec", "scope", "consequence_class", "why"):
    check(f"PRESERVE: the existing payload field {f!r} survives on the reloaded record", f in payload)

# ── PRESERVE — the EXISTING R2 chat-path use is unchanged (X3 ADDS a second caller, doesn't alter it) ─
# _resolve_context_at(locus) still returns its bounded STRING block (the chat's slice), unaffected.
from datetime import datetime, timezone
resolved_str = suite._resolve_context_at(CHATIN)
check("PRESERVE (chat-path): _resolve_context_at(locus) still returns a non-empty bounded STRING block",
      isinstance(resolved_str, str) and "CONTEXT RESOLVED AT YOUR LOCUS" in resolved_str)
check("PRESERVE (chat-path): the chat-path string slice is itself ≤ R2_BUDGET budget-bounded",
      sum(len(line) for line in resolved_str.splitlines()) <= Suite.R2_BUDGET + 400)  # +header allowance

# ── PRESERVE — a bare surface_build_intent (no address) persists NO context key (additive-optional) ──
bare = suite.surface_build_intent("a plain build with no address", scope=["runtime/suite.py"])
bp = FsStore(STORE_ROOT)
bpl = Suite(bp, reg, nodes_dir=NODES).inbox.get(bare["id"])["payload"]
check("PRESERVE: a bare surface_build_intent (no address) persists NO 'context' key (additive-optional)",
      "context" not in bpl)
check("PRESERVE: a .get('context') on the OLD-shape record reads as None (readers unaffected)",
      bpl.get("context") is None)

# ── consent-time (X5 precursor): the SURFACED record's bundle == a re-gather at mint would produce ──
# The persisted bundle is exactly the bounded slice the gather yields for this address (same machinery).
fresh_capped = suite._r2_score_and_cap(suite._r2_gather(CHATIN), CHATIN, datetime.now(timezone.utc))
fresh_texts = {it.get("text", "") for it in fresh_capped}
persisted_texts = {it.get("text", "") for it in ctx}
check("X3 consent-time: the persisted bundle's items are drawn from the SAME bounded gather (no second system)",
      persisted_texts <= fresh_texts or len(persisted_texts & fresh_texts) >= max(1, len(persisted_texts) - 2))

print(f"\nCONV CONTEXT ACCEPTANCE (X3) — {PASS} checks passed. At mint, surface_intent_at calls the "
      f"EXISTING R2 _r2_gather + _r2_score_and_cap for the address and PERSISTS the bounded, deduped, "
      f"JSON-clean bundle into the payload as the additive-optional `context` key. The build inherits the "
      f"accumulated notebook; the bundle is the SAME R2_BUDGET-bounded slice the chat gets (a dropped "
      f"low-scored item proves the cap); the clicked comment counts once (X8); no `_raw` leaks; X1/X2 "
      f"address+symbols still persist; the chat-path _resolve_context_at is unchanged.")
