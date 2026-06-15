"""tests/cc_board_acceptance.py — the Company NOTICEBOARD / board acceptance suite.

Falsify-first floor for the inward-facing half (Tim 2026-06-15): a session FILES a typed item →
it is STORED as a registry-backed, addressable record → the lead LISTS + picks it up + TRANSITIONS
it along the item-type's DECLARED lifecycle. Proves the load-bearing decisions locked with the fabric:

  • type & state & source & edge-kind are REGISTRY REFERENCES, validated fail-loud — never inline enums.
  • lifecycle (legal state transitions) lives ON the item-type registry row (per-type, not one global enum).
  • storage is id-keyed FLAT (channel-memory/noticeboard/<id>.md) — type is frontmatter, never the path.
  • canonical address is board://<id> — FLAT, because type can CHANGE (idea→request) and identity holds
    nothing mutable.
  • links are TYPED EDGES [{kind,target}] — kind validated against the relation/edge registry (the Heart's
    cross-registry edge layer, exercised here for the first time); a new edge-kind is a row-add, no code.

Plain-assert harness (mirrors tests/cc_channels_acceptance.py). Run:
    .venv/bin/python tests/cc_board_acceptance.py
Exit 0 = all green, 1 = a FAIL.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runtime import cc_board as cb  # noqa: E402

PASS, FAIL = [], []


def check(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  {'PASS' if c else 'FAIL'}  {n}" + (f"  — {d}" if d and not c else ""))


def raises(fn, sub=""):
    try:
        fn()
        return False
    except cb.BoardError as e:
        return sub in str(e) if sub else True
    except Exception:
        return False


tmp = tempfile.mkdtemp(prefix="company-board-")

# ── REGISTRIES are file-discovered + fail-loud (not inline enums) ──────────────────────────
types = set(cb.item_types())
check("1 item-type registry holds all five story-types",
      {"request", "issue", "tip", "guide", "idea"} <= types, f"got {sorted(types)}")
check("2 edge-kind registry holds the four cross-registry edges",
      {"authored_by", "attached_to", "sourced_from", "promoted_from"} <= set(cb.edge_kinds()),
      f"got {sorted(cb.edge_kinds())}")
check("3 source-type registry holds claude_code", "claude_code" in set(cb.source_types()))
check("4 lifecycle lives ON the item-type row (per-type, not global)",
      cb.legal_transitions("request", "open") and cb.legal_transitions("issue", "open")
      and cb.legal_transitions("request", "open") != cb.legal_transitions("issue", "open"),
      "request and issue must declare DIFFERENT lifecycles")

# ── FILE an item (a session files a request) ──────────────────────────────────────────────
it = cb.file_item("request", "Add a `company board cap` view",
                  "The CLI should show board counts by state.",
                  author_session="clone-test", source="claude_code",
                  links=[{"kind": "authored_by", "target": "session://clone-test"}],
                  board_dir=tmp)
iid = it["id"]
check("5 file_item returns an id", bool(iid))
check("6 canonical address is FLAT board://<id> (nothing mutable in identity)",
      it["address"] == f"board://{iid}", it.get("address"))
check("7 initial state is the item-type's REGISTRY-declared initial",
      it["state"] == cb.initial_state("request"), f"state={it.get('state')}")
check("8 the item file is id-keyed FLAT (type is frontmatter, NOT the path)",
      os.path.exists(os.path.join(tmp, f"{iid}.md"))
      and not os.path.exists(os.path.join(tmp, "request")),
      "no per-type subdir")
check("9 the typed edge is stored", it["links"] == [{"kind": "authored_by", "target": "session://clone-test"}])
check("10 history records the open (from None → initial, by author)",
      it["history"] and it["history"][0]["to"] == it["state"] and it["history"][0]["from"] is None)

# ── LIST + pick up (the lead reads the board) ─────────────────────────────────────────────
rows = cb.list_items(board_dir=tmp)
check("11 list_items finds the filed item", any(r["id"] == iid for r in rows))
check("12 list filters by type", all(r["type"] == "request" for r in cb.list_items(type="request", board_dir=tmp))
      and any(r["id"] == iid for r in cb.list_items(type="request", board_dir=tmp)))
check("13 list filters by state (open)", any(r["id"] == iid for r in cb.list_items(state="open", board_dir=tmp)))
got = cb.get_item(iid, board_dir=tmp)
check("14 get_item round-trips the body", got["body"] == "The CLI should show board counts by state.")
check("15 get_item round-trips the typed edge",
      got["links"] == [{"kind": "authored_by", "target": "session://clone-test"}])

# ── TRANSITION along the DECLARED lifecycle (registry-driven, not a hardcoded op) ─────────
moved = cb.transition(iid, "picked-up", by="ch-lead", note="lead picks it up", board_dir=tmp)
check("16 transition moves the state along the declared lifecycle", moved["state"] == "picked-up")
check("17 transition appends history (from open → picked-up, by lead)",
      moved["history"][-1]["from"] == "open" and moved["history"][-1]["to"] == "picked-up"
      and moved["history"][-1]["by"] == "ch-lead")
check("18 the transition persisted to disk",
      cb.get_item(iid, board_dir=tmp)["state"] == "picked-up")
check("19 'updated' advanced past 'created'", cb.get_item(iid, board_dir=tmp)["updated"] >= got["created"])

# ── FAIL LOUD: every registry reference is validated (never a silent bad value) ───────────
check("20 file with an UNREGISTERED type fails loud",
      raises(lambda: cb.file_item("bug", "x", "y", author_session="s", board_dir=tmp), "type"))
check("21 file with an UNREGISTERED source fails loud",
      raises(lambda: cb.file_item("request", "x", "y", author_session="s", source="jira", board_dir=tmp), "source"))
check("22 file with an UNREGISTERED edge-kind fails loud",
      raises(lambda: cb.file_item("request", "x", "y", author_session="s",
                                  links=[{"kind": "blocks", "target": "board://z"}], board_dir=tmp), "kind"))
check("23 an ILLEGAL transition fails loud (registry-declared lifecycle is the only truth)",
      raises(lambda: cb.transition(iid, "resolved", by="x", board_dir=tmp), "transition"))
check("24 get/transition on a MISSING item fails loud",
      raises(lambda: cb.get_item("item-deadbeef", board_dir=tmp)))

# ── the H1 proof clone-cacc9e8b will confirm: a NEW edge-kind is a ROW-ADD, no code change ─
edge_dir = cb.BOARD_EDGES_DIR
extra = os.path.join(edge_dir, "blocks.py")
added = False
try:
    with open(extra, "w", encoding="utf-8") as f:
        f.write('RELATION_TYPE = {"id": "blocks", "directed": True, "label": "blocks",\n'
                '                 "desc": "this item blocks another (item → board://<id>)."}\n')
    added = True
    cb.reset_registries()  # rediscover — proves the registry re-reads the directory
    check("25 a brand-new edge-kind (blocks.py) is live by ROW-ADD — the registry is real, not an enum",
          "blocks" in set(cb.edge_kinds()))
    ok = cb.file_item("issue", "x", "y", author_session="s",
                      links=[{"kind": "blocks", "target": "board://q"}], board_dir=tmp)
    check("26 the new edge-kind validates on a real item (cross-registry edge, born typed)",
          ok["links"][0]["kind"] == "blocks")
finally:
    if added and os.path.exists(extra):
        os.remove(extra)
    cb.reset_registries()

print(f"\n{'='*60}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — cc_board: registry-typed items (type/state/source/edge as rows), per-type\n"
      "lifecycle, flat board://<id> identity, typed cross-registry edges, fail-loud on every ref,\n"
      "new-edge-kind-by-row-add. The inward-facing half's request loop, proven by use.")
