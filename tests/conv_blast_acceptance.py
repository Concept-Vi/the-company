"""tests/conv_blast_acceptance.py — X9 · blast_radius(address), Seam 2 (the nearly-free one).

The `referenced_by[]` data in design/_system/code-symbols.json already encodes "which
addresses/features touch the same code symbol" — a CO-REFERENCE blast radius — but NOTHING reads
it (zero runtime consumers). X9 is the FREE half: a `blast_radius(addr)` method beside
`resolve_scope` that INVERTS that already-loaded reverse index into the sibling set, with NO new
substrate (the structural symbol→symbol graph is X10, a separate net-new unit — NOT this).

Sequence (Implementation Guide X9): addr → its `code://` symbols (the SAME forward step
`resolve_scope` does — X9 REUSES it, so the S0 grammar gate + the stale short-circuit + the
canonical symbol set all come for free, one source) → for each symbol read its `referenced_by[]`
from the already-loaded index, MINUS the address itself = the sibling addresses/features that share
that code → return the co-reference neighbours.

This suite proves:
  1. CO-REFERENCE + SELF-EXCLUSION (the load-bearing assertion): given a controlled
     code-symbols.json where address A and address B BOTH reference symbol S, blast_radius(A)
     returns B (the sibling that shares the code) and does NOT return A itself ("minus self").
  2. HONEST EMPTY (not an error): an address whose symbol nothing else references → empty
     co-reference set, with a legible note — never a silent wrong answer, never a raise.
  3. FAIL-LOUD S0 GATE: a malformed ui:// address raises (reuses parse_ui_address via
     resolve_scope) — AND resolve_scope still works byte-for-byte unchanged (preserve).
  4. STALE = fail-loud-legible: an unreadable/absent corpus index → empty neighbours + a stale
     note (mirrors resolve_scope), never a fabricated answer.
  5. NEIGHBOURS INCLUDE FEATURES, not just ui:// (the index's referenced_by carries feature-ids
     like ENG-*/WIRE-*; the spec says "addresses/features").
  6. ROBUSTNESS: blast_radius never crashes across EVERY real corpus address.
  7. The `shared_only` knob (X17 configurable-ready) is a thin param with a sane default — present
     and callable, default-off behaviour is what every other check pins.
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

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
reg = NodeRegistry(); reg.discover([NODES])


def fresh_suite():
    store = FsStore(os.path.join(tempfile.mkdtemp(prefix="blast-"), "store"))
    return Suite(store, reg, nodes_dir=NODES)


# ── A controlled corpus fixture: shadow _corpus_dir so BOTH resolve_scope and blast_radius read
#    our hand-built code-symbols.json. A is the clicked address; B is the co-reference sibling
#    (shares symbol S with A); C-only shares nothing else; ENG-feat is a non-ui feature referrer. ──
def with_fixture(symbols: dict):
    """Build a temp design/_system/code-symbols.json and return a suite pointed at it."""
    tmpsys = tempfile.mkdtemp(prefix="blast-corpus-")
    with open(os.path.join(tmpsys, "code-symbols.json"), "w", encoding="utf-8") as f:
        json.dump({"symbols": symbols,
                   "shared": [sid for sid, e in symbols.items()
                              if len(e.get("referenced_by") or []) >= 2]}, f)
    s = fresh_suite()
    s._corpus_dir = lambda: tmpsys           # instance attr shadows the bound method (read-redirect)
    return s


A = "ui://inbox/coa"
B = "ui://inbox/build-review"
C = "ui://toolbar/run"
FIXTURE = {
    # S is referenced by A, B, and a non-ui feature → A's blast radius = {B, ENG-feat}, never A.
    "code://shared/S": {"file": "runtime/suite.py", "symbol": "S", "kind": "def",
                        "resolves": True, "referenced_by": [A, B, "ENG-feat"]},
    # T is referenced ONLY by C → C's blast radius is empty (honest, not an error).
    "code://lonely/T": {"file": "runtime/scheduler.py", "symbol": "T", "kind": "def",
                        "resolves": True, "referenced_by": [C]},
}

# ── 1. CO-REFERENCE + SELF-EXCLUSION (the load-bearing assertion) ─────────────
s = with_fixture(FIXTURE)
br = s.blast_radius(A)
check(f"blast_radius({A}) resolves the shared symbol S (forward step, same as resolve_scope) "
      f"→ symbols {br['symbols']}", br["symbols"] == ["code://shared/S"])
check(f"co-reference sibling {B} IS in the blast radius (shares symbol S) — neighbours "
      f"{br['neighbours']}", B in br["neighbours"])
check("SELF-EXCLUSION: the clicked address A is NOT in its own blast radius ('minus self')",
      A not in br["neighbours"])
check("not stale (fixture corpus read OK)", br["stale"] is False)

# ── 5. NEIGHBOURS INCLUDE FEATURES, not just ui:// addresses ──────────────────
check(f"a non-ui FEATURE referrer (ENG-feat) is a co-reference neighbour — neighbours "
      f"{br['neighbours']}", "ENG-feat" in br["neighbours"])

# ── 2. HONEST EMPTY (an address whose symbol nothing else references) ─────────
empty = s.blast_radius(C)
check(f"blast_radius({C}) resolves symbol T → symbols {empty['symbols']}",
      empty["symbols"] == ["code://lonely/T"])
check("symbol referenced by nothing else → EMPTY co-reference set (honest, not an error)",
      empty["neighbours"] == [])
check("the empty (has-symbols-but-no-co-referrers) case carries a legible note",
      bool(empty["note"]))
check("empty case did NOT raise (returned a result)", empty["address"] == C)

# ── the OTHER empty case: an address with NO referencing symbol at all ────────
none = s.blast_radius("ui://nonexistent/thing")
check("address with no referencing symbol → empty neighbours, no raise",
      none["neighbours"] == [] and none["symbols"] == [])
check("the no-symbol empty case carries its own legible note", bool(none["note"]))

# ── 7. the shared_only knob (X17 configurable-ready) — present, sane default ──
br_shared = s.blast_radius(A, shared_only=True)
check("blast_radius accepts a shared_only knob (X17-ready) and still returns B "
      "(neighbour-bearing symbols are shared by construction)", B in br_shared["neighbours"])

# ── 3. FAIL-LOUD S0 GATE + resolve_scope PRESERVED byte-for-byte ──────────────
raised = False
try:
    s.blast_radius("not-a-ui-address")
except (ValueError, TypeError):
    raised = True
check("malformed ui:// address raises (S0 grammar gate via parse_ui_address)", raised)

# resolve_scope must STILL work on the same fixture (preserve — X9 is a NEW sibling, not an edit)
rs = s.resolve_scope(A)
check("resolve_scope STILL resolves A's symbol unchanged (preserved)",
      rs["symbols"] == ["code://shared/S"] and rs["scope"] == ["runtime/suite.py"])
rs_bad = False
try:
    s.resolve_scope("not-a-ui-address")
except (ValueError, TypeError):
    rs_bad = True
check("resolve_scope STILL fails loud on a malformed address (preserved)", rs_bad)

# ── 4. STALE = fail-loud-legible (mirrors resolve_scope) ──────────────────────
stale_suite = fresh_suite()
stale_suite._corpus_dir = lambda: tempfile.mkdtemp(prefix="blast-empty-")  # no code-symbols.json
st = stale_suite.blast_radius(A)
check("absent/unreadable corpus index → stale=True (fail-loud-legible)", st["stale"] is True)
check("stale case → empty neighbours (never a fabricated answer)", st["neighbours"] == [])
check("stale case carries a regenerate note", "regenerate" in st["note"].lower())

# ── 6. ROBUSTNESS — never crashes across EVERY real corpus address ────────────
real = fresh_suite()
with open(os.path.join(ROOT, "design", "_system", "addresses.json"), encoding="utf-8") as f:
    all_addrs = json.load(f)["addresses"]
crashed = []
for a in all_addrs:
    try:
        out = real.blast_radius(a)
        assert isinstance(out["neighbours"], list) and isinstance(out["symbols"], list)
    except Exception as e:  # noqa: BLE001 — the point is to prove it never throws
        crashed.append((a, repr(e)))
check(f"blast_radius never crashes on ANY of the {len(all_addrs)} real corpus addresses "
      f"(crashed: {crashed[:2]})", not crashed)
# and on the real corpus the clicked address is never its own neighbour
self_in = [a for a in all_addrs if a in (real.blast_radius(a)["neighbours"])]
check(f"on the real corpus NO address is ever its own neighbour (self-exclusion holds; "
      f"offenders: {self_in[:2]})", not self_in)

print(f"\nCONV BLAST ACCEPTANCE — {PASS} checks passed. "
      f"blast_radius inverts code-symbols.json's referenced_by (the SAME index resolve_scope loads, "
      f"reusing its forward step) into the co-reference sibling set MINUS self; honest-empty + "
      f"fail-loud (S0 + stale); features included; resolve_scope preserved; no new substrate.")
