"""tests/cc_board_reverse_acceptance.py — Heart H1.2 gate: reverse_traverse + relations on cc_board.

Proof-by-use on a CONTROLLED board fixture (deterministic) PLUS a smoke check against the real board if
present. Covers: edges-into matching on the opaque target string, kind filter, fail-loud on an
unregistered kind, the unified relations(in/out/both) surface, and hydrate=True round-tripping a match
through resolve_address. Run: python3 tests/cc_board_reverse_acceptance.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime import cc_board as cb

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'ok ' if cond else 'FAIL'} {name}" + (f"  — {detail}" if detail and not cond else ""))


# ── controlled fixture: a tiny board mirroring the real genesis chain ──
tmp = tempfile.mkdtemp(prefix="cc_board_rev_")
BD = os.path.join(tmp, "board")
# two items authored by the same session + a promoted_from chain (the real shape)
a = cb.file_item("request", "alpha", "first", "ch-8djrpmsl", board_dir=BD,
                 links=[{"kind": "authored_by", "target": "session://ch-8djrpmsl"}])
b = cb.file_item("request", "beta", "second", "ch-8djrpmsl", board_dir=BD,
                 links=[{"kind": "authored_by", "target": "session://ch-8djrpmsl"},
                        {"kind": "promoted_from", "target": a["address"]}])
c = cb.file_item("idea", "gamma", "third", "ch-al7jdfdr", board_dir=BD,
                 links=[{"kind": "authored_by", "target": "session://ch-al7jdfdr"}])

# 1. edges-INTO a target, matched on the opaque string
into_me = cb.reverse_traverse("session://ch-8djrpmsl", "authored_by", board_dir=BD)
ok("reverse_traverse finds all items linking to a target (authored_by)",
   {m["source"] for m in into_me} == {a["address"], b["address"]})
ok("reverse_traverse entry carries source+kind+target+full item",
   all(set(m.keys()) >= {"source", "kind", "target", "item"} for m in into_me)
   and into_me[0]["target"] == "session://ch-8djrpmsl"
   and into_me[0]["item"].get("title") in ("alpha", "beta"))

# 2. the promoted_from chain (board://-target match) — b was promoted_from a
into_a = cb.reverse_traverse(a["address"], "promoted_from", board_dir=BD)
ok("reverse_traverse follows a board://-target edge backward (promoted_from chain)",
   [m["source"] for m in into_a] == [b["address"]])

# 3. kind filter narrows: no promoted_from edge points at the session
ok("kind filter narrows the match set",
   cb.reverse_traverse("session://ch-8djrpmsl", "promoted_from", board_dir=BD) == [])
# kind=None returns ALL edges into the target regardless of kind
ok("kind=None returns every edge into the target",
   len(cb.reverse_traverse("session://ch-8djrpmsl", board_dir=BD)) == 2)

# 4. fail-loud on an unregistered kind (mirrors traverse)
try:
    cb.reverse_traverse("session://ch-8djrpmsl", "not_a_kind", board_dir=BD)
    ok("reverse_traverse fails loud on an unregistered kind", False)
except cb.BoardError as e:
    ok("reverse_traverse fails loud on an unregistered kind", "unknown edge kind" in str(e))

# 5. the unified relations surface — in / out / both
rin = cb.relations("session://ch-8djrpmsl", direction="in", board_dir=BD)
ok("relations(in) = edges into the addr",
   {m["source"] for m in rin["edges_in"]} == {a["address"], b["address"]} and "edges_out" not in rin)
rout = cb.relations(b["address"], direction="out", board_dir=BD)
ok("relations(out) on a board addr = its outgoing edges (via traverse)",
   {h["kind"] for h in rout["edges_out"]} == {"authored_by", "promoted_from"})
rboth = cb.relations(b["address"], direction="both", board_dir=BD)
ok("relations(both) returns edges_in AND edges_out",
   "edges_in" in rboth and "edges_out" in rboth)
# out on a NON-board addr is empty + stated (never a silent guess)
rnon = cb.relations("session://ch-8djrpmsl", direction="out", board_dir=BD)
ok("relations(out) on a non-board addr is empty + STATED, not silent",
   rnon["edges_out"] == [] and "edges_out_note" in rnon)

import shutil
shutil.rmtree(tmp, ignore_errors=True)

# 6. PROOF-BY-USE on the REAL board (the lead's ask): hydrate=True round-trips a real match through
# resolve_address. The genesis chain item-15aaf9da --promoted_from--> board://item-e523b30d is live;
# reverse_traverse on the real target with hydrate resolves the matched source through the ONE resolver.
# board://->board:// hydration is store-independent (resolve_address reads the noticeboard for board://).
REAL = os.path.join(ROOT, "channel-memory", "noticeboard")
if os.path.isdir(REAL) and os.path.exists(os.path.join(REAL, "item-e523b30d.md")):
    real_in = cb.reverse_traverse("board://item-e523b30d", "promoted_from")   # default board_dir = the real board
    ok("REAL board: reverse_traverse finds the promoted_from chain (item-15aaf9da -> item-e523b30d)",
       any(m["source"] == "board://item-15aaf9da" for m in real_in))
    try:
        h = cb.reverse_traverse("board://item-e523b30d", "promoted_from", hydrate=True)
        hit = next((m for m in h if m["source"] == "board://item-15aaf9da"), None)
        ok("REAL board: hydrate=True resolves the matched source through resolve_address (string-match -> record)",
           hit is not None and isinstance(hit.get("resolved"), dict) and hit["resolved"].get("id") == "item-15aaf9da")
    except Exception as e:
        ok("REAL board: hydrate=True resolves the matched source through resolve_address", False,
           f"hydrate raised ({type(e).__name__}: {e})")
else:
    print("  -- skipped REAL-board hydrate check (genesis items not present) --")

print(f"\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — H1.2 reverse_traverse + relations: edges-into by opaque-string match, kind filter, "
      "fail-loud, unified in/out/both surface, hydrate round-trip. Composes list_items+edge-registry+resolver.")
