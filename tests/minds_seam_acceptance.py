"""tests/minds_seam_acceptance.py — R13 seams A+B: the REAL resolve_address→mind→traverse path.

fork's runtime/minds.py (8cd361e) is the provider (minds_acceptance 10/10, traverse tested with a
SIMULATED seam-A). This proves the LEAD's two hot seams meet that provider for real (cacc9e8b's bar 7 —
consumer-interface == provider-interface at the meet-point):
  • SEAM A — resolve_address(mind://<id>) → the Mind row THROUGH the one resolver; fail-loud (bar 6).
  • SEAM B — Suite.cast_for_mode(mode): if bound to a composition (a minds/ binding ROW), the cast is the
    composition resolved THROUGH the one resolver (bar 2) → ordered role-shaped minds; ELSE byte-identical
    role-registry default (additive — run_swarm untouched, behaviour-preserving).

Falsify-first floor: before seam A, resolve_address(mind://…) RAISES "not content-resolvable" (RED);
before seam B, a composition-bound mode falls to the empty role default (RED). Plain-assert.
    .venv/bin/python tests/minds_seam_acceptance.py
"""
import os
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from contracts.address import SCHEMES                       # noqa: E402
from runtime.cognition import resolve_address              # noqa: E402
from store.fs_store import FsStore                          # noqa: E402

PASS, FAIL = [], []


def check(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  {'PASS' if c else 'FAIL'}  {n}" + (f"  — {d}" if d and not c else ""))


def raises(fn, exc=Exception, sub=""):
    try:
        fn()
        return False
    except exc as e:
        return sub in str(e) if sub else True
    except Exception:
        return False


store = FsStore(os.path.join(REPO, ".data", "store"))

# ── SEAM A — mind:// resolves THROUGH the one resolver (+ the axis guard) ─────────────────────────────
check("1 'mind' registered in SCHEMES (+ 'clone' still there — separate axis)",
      "mind" in SCHEMES and "clone" in SCHEMES)
pair = resolve_address(store, "mind://pair")
check("2 ★ resolve_address(mind://pair) → composition Mind via seam A (the REAL one-resolver path)",
      getattr(pair, "kind", None) == "composition"
      and "extractor" in pair.members and "judge" in pair.members,
      f"kind={getattr(pair, 'kind', None)} members={getattr(pair, 'members', None)}")
ex = resolve_address(store, "mind://extractor")
check("3 resolve_address(mind://extractor) → a role-kind Mind", getattr(ex, "kind", None) == "role")
check("4 resolve_address(mind://nonexistent) RAISES (fail-loud bar 6, the REAL resolver path)",
      raises(lambda: resolve_address(store, "mind://nonexistent-zzz"), ValueError))

# ── SEAM B — cast_for_mode through the composition (the Suite method edit) ────────────────────────────
from runtime.registry import NodeRegistry  # noqa: E402
from runtime.suite import Suite            # noqa: E402
NODES = os.path.join(REPO, "nodes")
s2 = FsStore(os.path.join(tempfile.mkdtemp(prefix="minds-seam-"), "store"))
reg = NodeRegistry().discover([NODES])
suite = Suite(s2, reg, nodes_dir=NODES)

cast = suite.cast_for_mode("compose-test")
check("5 ★ cast_for_mode('compose-test') → the composition's ordered role-shaped minds (seam B, REAL bind)",
      isinstance(cast, list) and len(cast) == 2 and all(hasattr(r, "id") for r in cast),
      f"got {cast!r}")
ids = [getattr(r, "id", None) for r in cast]
check("6 ★ the cast is the composition in run order: extractor→judge = [mine_exchange, judge_mining]",
      ids == ["mine_exchange", "judge_mining"], f"got {ids}")

# behaviour-preserving: an UNBOUND mode is byte-identical to the role-registry default (additive seam)
unbound = "__definitely_unbound_mode_zzz__"
check("7 cast_for_mode(<unbound>) == role_registry default (additive seam — default unchanged, run_swarm untouched)",
      suite.cast_for_mode(unbound) == suite.role_registry.cast_for_mode(unbound))

print(f"\n{'=' * 60}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — R13 seams A+B meet fork's runtime/minds.py at the locked interface (bar 7): mind://\n"
      "resolves through the ONE resolver (seam A, fail-loud), and cast_for_mode binds a mode to a\n"
      "composition resolved through that resolver into ordered role-shaped minds (seam B), with the\n"
      "unbound default byte-identical (run_swarm untouched). The brain is a composition from a registry.")
