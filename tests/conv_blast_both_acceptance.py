"""tests/conv_blast_both_acceptance.py — X14 · blast_radius spans BOTH edge kinds.

X9 gave the CO-REFERENCE blast radius (addresses/features sharing a `code://` symbol — from
code-symbols.json's `referenced_by[]`). X14 WIDENS `blast_radius` to ALSO return, DISTINGUISHED
by kind:
  • structural_dependents[]   — the symbols that DEPEND ON the resolved symbol (X10's
                                `depended_by`, bounded by X10's reach query) = dependents-to-VERIFY.
  • structural_dependencies[] — the symbols the resolved symbol DEPENDS ON (X10's `depends_on`,
                                bounded) = dependencies-to-RESPECT.
  • semantic_neighbours[]     — the conceptually-related symbols (X11's `semantically_nearest[]`).
  • co_reference[]            — the X9 set, PRESERVED (== the legacy `neighbours` field).

REUSE, not reimplement (rule 3 + the unit brief):
  - addr→symbols   : `resolve_scope` (the SAME forward step X9 reuses).
  - structural reach: X10's `codeedges.reach_report` (bounded at DEPTH 2–3; capped reported) —
                      dependents come from the SAME bounded walk over a TRANSPOSED edge view
                      (depends_on↔depended_by swapped), so the BFS algorithm is X10's, not a
                      new graph computation.
  - semantic       : X11's `semantically_nearest[]` read straight off the same code-symbols.json.

GRACEFUL-EMPTY + fail-loud-legible (rule 4):
  - code-edges.json absent  → structural_* empty + a note (no crash, no fabricated edges).
  - semantically_nearest[] absent (the embedder :8001 was down at regen — its CURRENT real state)
                            → semantic_neighbours empty + a note (no crash, no fabrication).

PRESERVE: X9's co-reference result is unchanged — `tests/conv_blast_acceptance.py` still GREEN,
and here the legacy `neighbours` key + the new `co_reference` key carry the SAME set.

This suite proves (against hand-built fixtures so the assertions are controlled):
  1. STRUCTURAL: a symbol S that is depended-on-by D and depends-on P → blast_radius(addr→S)
     returns D in structural_dependents AND P in structural_dependencies, each DISTINCT from
     co_reference.
  2. SEMANTIC: a populated `semantically_nearest[]` → those ids appear in semantic_neighbours,
     distinct from the structural + co-reference sets.
  3. BOUNDED: the structural reach uses X10's DEPTH cap; a chain longer than DEPTH is reported
     `*_capped` (no silent truncation), and symbols past the bound are NOT leaked.
  4. PRESERVE: X9's co-reference result is unchanged (co_reference == legacy neighbours == the
     X9 sibling set, minus self).
  5. GRACEFUL: absent code-edges.json → structural_* empty + note; absent semantically_nearest →
     semantic empty + note; never a crash.
  6. ROBUSTNESS: blast_radius never crashes across EVERY real corpus address with the REAL
     code-edges.json + code-symbols.json (the live data — semantic currently empty by design).
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
    store = FsStore(os.path.join(tempfile.mkdtemp(prefix="blast2-"), "store"))
    return Suite(store, reg, nodes_dir=NODES)


def with_corpus(symbols: dict, edges: dict | None = None):
    """Build a temp design/_system with a controlled code-symbols.json (+ optional code-edges.json)
    and return a suite pointed at it. `edges` None ⇒ NO code-edges.json file (graceful-absent test)."""
    tmpsys = tempfile.mkdtemp(prefix="blast2-corpus-")
    with open(os.path.join(tmpsys, "code-symbols.json"), "w", encoding="utf-8") as f:
        json.dump({"symbols": symbols,
                   "shared": [sid for sid, e in symbols.items()
                              if len(e.get("referenced_by") or []) >= 2]}, f)
    if edges is not None:
        with open(os.path.join(tmpsys, "code-edges.json"), "w", encoding="utf-8") as f:
            json.dump({"edges": edges, "stale": [], "shared": []}, f)
    s = fresh_suite()
    s._corpus_dir = lambda: tmpsys
    return s


# Addresses. A clicks symbol S. B co-references S (the X9 sibling). D depends on S (structural
# dependent of S). P is depended-on-by S (a structural dependency of S). Q is two hops out from S
# (depth>1) for the bound test.
A = "ui://inbox/coa"
B = "ui://inbox/build-review"
S = "code://shared/S"
D = "code://dependent/D"
P = "code://dependency/P"
Q = "code://far/Q"
N1 = "code://near/N1"
N2 = "code://near/N2"

SYMBOLS = {
    # S — clicked via A; co-referenced by B (X9). Carries a populated semantically_nearest[] (X11).
    S: {"file": "runtime/suite.py", "symbol": "S", "kind": "def", "resolves": True,
        "referenced_by": [A, B], "semantically_nearest": [{"id": N1, "score": 0.91},
                                                           {"id": N2, "score": 0.83}]},
}

# Structural edge fixture (X10 shape): D --depends_on--> S --depends_on--> P --depends_on--> Q.
# So from S: dependencies = {P} at hop1, {Q} at hop2; dependents = {D}. With DEPTH=2 the reach of
# dependencies should include P and Q but NOT anything past Q (and capped only if there is more).
EDGES = {
    S: {"depends_on": [P], "depended_by": [D], "resolves": True},
    D: {"depends_on": [S], "depended_by": [], "resolves": True},
    P: {"depends_on": [Q], "depended_by": [S], "resolves": True},
    Q: {"depends_on": [], "depended_by": [P], "resolves": True},
}

# ── 1. STRUCTURAL: dependents (D) + dependencies (P) distinguished from co_reference ──────────
s = with_corpus(SYMBOLS, EDGES)
br = s.blast_radius(A)
check(f"blast_radius({A}) resolves symbol S → symbols {br['symbols']}", br["symbols"] == [S])
check(f"co_reference still carries the X9 sibling B — co_reference {br['co_reference']}",
      B in br["co_reference"])
check(f"structural_dependents carries D (a symbol that DEPENDS ON S) — {br['structural_dependents']}",
      D in br["structural_dependents"])
check(f"structural_dependencies carries P (a symbol S DEPENDS ON) — {br['structural_dependencies']}",
      P in br["structural_dependencies"])
check("the kinds are DISTINGUISHED: D is a dependent, not a co_reference",
      D not in br["co_reference"])
check("the kinds are DISTINGUISHED: P is a dependency, not a co_reference",
      P not in br["co_reference"])
check("structural_dependents and structural_dependencies are separate fields",
      D not in br["structural_dependencies"] and P not in br["structural_dependents"])

# ── 2. SEMANTIC: semantically_nearest[] surfaces in semantic_neighbours, distinguished ────────
check(f"semantic_neighbours carries the X11 nearest N1/N2 — {br['semantic_neighbours']}",
      N1 in br["semantic_neighbours"] and N2 in br["semantic_neighbours"])
check("semantic neighbours are DISTINGUISHED from structural + co_reference",
      N1 not in br["structural_dependents"] and N1 not in br["co_reference"])

# ── 3. BOUNDED: the structural reach respects X10's DEPTH cap (no silent truncation) ──────────
import importlib.util
_ce = os.path.join(ROOT, "design", "_system", "codeedges.py")
spec = importlib.util.spec_from_file_location("codeedges_probe", _ce,
                                              submodule_search_locations=[os.path.dirname(_ce)])
sys.path.insert(0, os.path.dirname(_ce))
ce = importlib.util.module_from_spec(spec); spec.loader.exec_module(ce)
DEPTH = ce.DEPTH
check(f"the structural reach reports its DEPTH (== X10's CODEEDGES_DEPTH={DEPTH})",
      br.get("structural_depth") == DEPTH)
# With DEPTH=2, dependencies of S reach P (hop1) + Q (hop2); Q has no further deps → not capped.
check(f"with DEPTH={DEPTH}, dependencies reach P and Q (within bound) — {br['structural_dependencies']}",
      P in br["structural_dependencies"] and Q in br["structural_dependencies"])
check("the reach exposes a capped flag (legible bound, no silent truncation)",
      "structural_dependencies_capped" in br and "structural_dependents_capped" in br)

# A deeper chain to PROVE the cap actually bounds + reports capped=True.
P2, P3 = "code://dependency/P2", "code://dependency/P3"
DEEP_SYM = {S: {"file": "runtime/suite.py", "symbol": "S", "kind": "def", "resolves": True,
                "referenced_by": [A]}}
# S->P->Q->P2->P3 : a chain of length 4. DEPTH=2 reaches P,Q only; P2/P3 are past the bound.
DEEP_EDGES = {
    S: {"depends_on": [P], "depended_by": [], "resolves": True},
    P: {"depends_on": [Q], "depended_by": [S], "resolves": True},
    Q: {"depends_on": [P2], "depended_by": [P], "resolves": True},
    P2: {"depends_on": [P3], "depended_by": [Q], "resolves": True},
    P3: {"depends_on": [], "depended_by": [P2], "resolves": True},
}
sd = with_corpus(DEEP_SYM, DEEP_EDGES)
brd = sd.blast_radius(A)
check(f"BOUND HOLDS: with DEPTH={DEPTH}, P2/P3 (hops 3-4) are NOT leaked into dependencies — "
      f"{brd['structural_dependencies']}",
      P2 not in brd["structural_dependencies"] and P3 not in brd["structural_dependencies"])
check("BOUND REPORTED: dependencies_capped=True when the graph continues past DEPTH "
      "(no silent truncation)", brd["structural_dependencies_capped"] is True)

# ── 4. PRESERVE: X9's co-reference result is unchanged (co_reference == legacy neighbours) ─────
check("legacy `neighbours` key STILL present (X9 callers/test unbroken)", "neighbours" in br)
check("co_reference == legacy neighbours (the SAME X9 sibling set)",
      sorted(br["co_reference"]) == sorted(br["neighbours"]))
check("SELF-EXCLUSION preserved: A is not in its own co_reference", A not in br["co_reference"])

# ── 5a. GRACEFUL: code-edges.json ABSENT → structural empty + note, no crash ──────────────────
s_noedges = with_corpus(SYMBOLS, edges=None)   # NO code-edges.json written
brn = s_noedges.blast_radius(A)
check("absent code-edges.json → structural_dependents empty (no crash, no fabrication)",
      brn["structural_dependents"] == [])
check("absent code-edges.json → structural_dependencies empty",
      brn["structural_dependencies"] == [])
check("absent code-edges.json → a legible structural note", bool(brn.get("structural_note")))
check("absent code-edges.json does NOT break the co_reference layer (B still present)",
      B in brn["co_reference"])
check("absent code-edges.json does NOT break the semantic layer (N1 still present)",
      N1 in brn["semantic_neighbours"])

# ── 5b. GRACEFUL: semantically_nearest[] ABSENT (embedder down) → semantic empty + note ───────
SYM_NO_SEM = {S: {"file": "runtime/suite.py", "symbol": "S", "kind": "def", "resolves": True,
                  "referenced_by": [A, B]}}   # NO semantically_nearest (the real :8001-down state)
s_nosem = with_corpus(SYM_NO_SEM, EDGES)
brm = s_nosem.blast_radius(A)
check("absent semantically_nearest[] → semantic_neighbours empty (no crash, no fabrication)",
      brm["semantic_neighbours"] == [])
check("absent semantically_nearest[] → a legible semantic note (the :8001-down honesty)",
      bool(brm.get("semantic_note")))
check("absent semantic does NOT break structural (D still a dependent)",
      D in brm["structural_dependents"])

# ── 6. ROBUSTNESS — never crashes across EVERY real corpus address with the LIVE corpus ───────
real = fresh_suite()   # uses the REAL design/_system (code-edges.json present, semantic empty)
with open(os.path.join(ROOT, "design", "_system", "addresses.json"), encoding="utf-8") as f:
    all_addrs = json.load(f)["addresses"]
crashed = []
for a in all_addrs:
    try:
        out = real.blast_radius(a)
        for k in ("co_reference", "neighbours", "structural_dependents",
                  "structural_dependencies", "semantic_neighbours"):
            assert isinstance(out[k], list), f"{k} not a list for {a}"
    except Exception as e:  # noqa: BLE001
        crashed.append((a, repr(e)))
check(f"blast_radius never crashes on ANY of the {len(all_addrs)} real corpus addresses "
      f"(crashed: {crashed[:2]})", not crashed)
# the live corpus has code-edges.json present (so structural reads) but semantic empty by design
live = real.blast_radius(A)
check("LIVE corpus: semantic_neighbours empty (embedder :8001 was down at regen) + an honest note",
      live["semantic_neighbours"] == [] and bool(live.get("semantic_note")))

print(f"\nCONV BLAST BOTH ACCEPTANCE (X14) — {PASS} checks passed. "
      f"blast_radius now spans co_reference (X9, preserved) + structural_dependents/dependencies "
      f"(X10, bounded by reach_report at DEPTH, capped reported) + semantic_neighbours (X11), all "
      f"distinguished by kind; graceful-empty + fail-loud-legible when code-edges.json or "
      f"semantically_nearest[] is absent; no new substrate, no reimplemented graph walk.")
