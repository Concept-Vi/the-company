"""RED→GREEN for codeedges.py — the STRUCTURAL code-dependency graph (X10): symbol→symbol
calls/imports, the relational layer the reverse-index (symbols.py) does NOT have. Run:
    python3 test_codeedges.py
Real behaviour on small INLINE fixtures (no ~/company access, no mocks): given a fake
source tree where symbol A calls symbol B, the parser must emit B in A.depends_on AND
A in B.depended_by — keyed by the SAME code://<file-stem>/<symbol> ids symbols.py uses
(one coordinate system, no parallel). The transitive reach is BOUNDED at a named DEPTH
(a chain longer than DEPTH does not leak edges beyond the cap — asserted, with the cap
noted). An unparseable source file is recorded as a stale/resolves:false entry, never a
silent skip or a crash (fail-loud-legible). The existing code-symbols.json / symbols.py
is a SIBLING and stays UNTOUCHED (X10 does not modify it — that is X11)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import codeedges  # RED until codeedges.py exists
import symbols    # the sibling must remain importable + unchanged in shape

# --- a fake source TREE: {repo-relative-path: source-text} -----------------------------
# A chain a -> b -> c -> d -> e (5 deep) inside one module, so DEPTH-bounded reach is testable.
CHAIN_PY = """\
def a():
    return b()

def b():
    return c()

def c():
    return d()

def d():
    return e()

def e():
    return 1
"""

# cross-file: suite.Suite.run() calls a helper imported from scheduler, and a method on self.
SUITE_PY = """\
from scheduler import tick

class Suite:
    def run(self):
        tick()
        return self.resolve()

    def resolve(self):
        return 2
"""

SCHED_PY = """\
def tick():
    return 0
"""

# an unparseable file (syntax error) — must become a stale entry, never crash the build.
BROKEN_PY = """\
def busted(:
    this is not python
"""

FAKE_TREE = {
    "chain.py": CHAIN_PY,
    "runtime/suite.py": SUITE_PY,
    "scheduler.py": SCHED_PY,
    "broken.py": BROKEN_PY,
}


def fake_read(repo_path):
    """Stand-in for reading a file under ~/company READ-ONLY: returns the source text or None.
    Keyed by repo-relative path exactly as the on-disk walker would yield it."""
    return FAKE_TREE.get(repo_path)


def run():
    # ---- 1) the build over the fake tree -----------------------------------------------
    files = sorted(FAKE_TREE.keys())
    doc = codeedges.build_graph(files, read=fake_read)
    edges = doc["edges"]

    # ---- 2) DIRECT call edge: a -> b (same file) ---------------------------------------
    # a() calls b(); both defined in chain.py → ids code://chain/a, code://chain/b.
    a, b = "code://chain/a", "code://chain/b"
    assert b in edges[a]["depends_on"], f"a calls b -> b in a.depends_on: {edges.get(a)}"
    assert a in edges[b]["depended_by"], f"inverse: a in b.depended_by: {edges.get(b)}"

    # ---- 3) CROSS-FILE import edge: suite.run -> scheduler.tick ------------------------
    # Suite.run calls tick(), imported `from scheduler import tick` → code://scheduler/tick.
    run_id, tick_id = "code://suite/run", "code://scheduler/tick"
    assert tick_id in edges[run_id]["depends_on"], \
        f"imported call resolves cross-file: {edges.get(run_id)}"
    assert run_id in edges[tick_id]["depended_by"], f"inverse cross-file: {edges.get(tick_id)}"

    # ---- 3b) SAME-FILE method edge: suite.run -> suite.resolve (self.resolve()) --------
    resolve_id = "code://suite/resolve"
    assert resolve_id in edges[run_id]["depends_on"], \
        f"self.resolve() resolves to the same-file method: {edges.get(run_id)}"

    # ---- 4) BOUNDED transitive reach at DEPTH ------------------------------------------
    # The chain a->b->c->d->e is 4 hops. reach() from `a` capped at DEPTH must NOT include
    # nodes beyond DEPTH hops — that is the explosion guard (a transitive graph can blow up).
    assert codeedges.DEPTH in (2, 3), f"DEPTH is the named 2-3 cap, got {codeedges.DEPTH}"
    r = codeedges.reach(a, edges, depth=2)
    assert b in r and "code://chain/c" in r, f"2 hops reach b and c: {r}"
    assert "code://chain/d" not in r and "code://chain/e" not in r, \
        f"reach is CAPPED at depth 2 — d (3 hops) + e (4 hops) excluded: {r}"
    # explicit cap signal: a reach that hits the bound is reported as capped, not silently cut.
    capped = codeedges.reach_report(a, edges, depth=2)
    assert capped["capped"] is True, f"hitting the bound is reported (no silent truncation): {capped}"
    assert "code://chain/d" not in capped["reached"], capped

    # depth-1 reach is just the direct neighbour.
    r1 = codeedges.reach(a, edges, depth=1)
    assert r1 == {b}, f"depth 1 = direct deps only: {r1}"

    # ---- 5) UNPARSEABLE file → stale entry, NOT a crash / silent skip ------------------
    # broken.py raised SyntaxError; it must surface as a stale entry with resolves:false.
    assert any(s["file"] == "broken.py" and s["resolves"] is False for s in doc["stale"]), \
        f"unparseable file recorded as stale (fail-loud), not dropped: {doc['stale']}"
    # and a crashy build is a test failure by construction — reaching here means it did not crash.

    # ---- 6) the SIBLING (symbols.py / code-symbols.json) is untouched ------------------
    # codeedges reuses symbols' id scheme but must NOT redefine or mutate it.
    assert symbols.symbol_id("runtime/suite.py", "run") == "code://suite/run", \
        "codeedges keys off the SAME symbol_id scheme as symbols.py (no parallel coordinate)"
    assert codeedges.symbol_id is symbols.symbol_id, \
        "codeedges reuses symbols.symbol_id (one coordinate system, not a copy)"

    # ---- 7) the emitted doc shape (mirrors code-symbols.json honesty fields) ------------
    assert "_what" in doc and "code://" in doc["_what"], "carries the code:// branch note"
    assert "summary" in doc and doc["summary"]["depth"] == codeedges.DEPTH, doc["summary"]
    assert "stale" in doc, "honest about what didn't resolve (stale[])"
    # every edge entry carries the honesty field.
    for sid, e in edges.items():
        assert "resolves" in e and "depends_on" in e and "depended_by" in e, f"{sid}: {e}"

    print("PASS test_codeedges (direct call edge + inverse + cross-file import + same-file "
          "method + DEPTH-bounded reach [capped, reported] + unparseable->stale + sibling "
          "symbols.py untouched + emitted doc shape)")


run()
