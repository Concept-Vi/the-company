"""tests/clone_address_grammar_acceptance.py — clone:// joins the ONE addressed state (A+B unify).

The clone-fleet (Tim's "a") becomes first-class addressed rows in the one resolver (the Heart, "b").
clone:// = fleet/PROVENANCE identity: clone://<source-sid>/<cut> where cut = the clone record's `at`
field verbatim (compact:N | uuid:<uuid> | ts:<iso> — a path-segment colon is address-safe). Provenance,
NOT the ephemeral handle — a re-spawn of the same era resolves the SAME address (re-embed-stable, the
board:// identity principle). clone:// ≠ mind:// (separate axis — board://item-3c324c27).

Proves (falsify-first floor — the grammar fn import RAISES before the build):
  • parse_clone_address (contracts.address — declared grammar, beside parse_session_address) parses the
    legal form + FAILS LOUD on malformed (never a silent-pass).
  • ★ EQUIVALENCE: parse_clone_address(clone_address(rec)) round-trips fork's cc_clone.clone_address over
    REAL era-clone records — the two shapes provably AGREE at the seam (the is_step_address≡STEP_ADDR_RE
    pattern; cacc9e8b's bar-7 two-owner-boundary check, applied to clone://).
  • ★ resolve_address(store, clone://<real>) → the clone record + persisted reflection THROUGH the ONE
    resolver (cognition.py) — clone:// resolves like board://·session://·cap://; fail-loud on unknown.

    .venv/bin/python tests/clone_address_grammar_acceptance.py
"""
import glob
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from contracts.address import parse_clone_address          # noqa: E402  (RED before build)
from runtime.cc_clone import clone_address, CLONES_DIR     # noqa: E402  (fork's landed provider, 0bdeac3)
from runtime.cognition import resolve_address              # noqa: E402
from store.fs_store import FsStore                         # noqa: E402

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


# ── the legal form parses (cut = `at` verbatim, colon kept) ──────────────────────────────────────────
check("1 clone://<sid>/compact:1 → {source_sid, cut}",
      parse_clone_address("clone://bda8ce28/compact:1") == {"source_sid": "bda8ce28", "cut": "compact:1"})
check("2 clone://<sid>/uuid:<uuid> → cut keeps the colon token",
      parse_clone_address("clone://abc/uuid:11111111-2222") == {"source_sid": "abc", "cut": "uuid:11111111-2222"})

# ── FAIL LOUD on malformed (never silent-pass) ───────────────────────────────────────────────────────
check("3 clone://<sid> (no cut) RAISES",
      raises(lambda: parse_clone_address("clone://bda8ce28"), ValueError))
check("4 clone:// (empty) RAISES",
      raises(lambda: parse_clone_address("clone://"), ValueError))
check("5 a non-clone address RAISES (this grammar is clone://-scoped)",
      raises(lambda: parse_clone_address("board://item-x"), ValueError))

# ── ★ EQUIVALENCE with fork's clone_address over REAL era-clone records (the seam agrees) ─────────────
recs = []
for p in sorted(glob.glob(os.path.join(CLONES_DIR, "*.json"))):
    try:
        import json
        with open(p, encoding="utf-8") as f:
            r = json.load(f)
        if r.get("source_sid") and r.get("at"):
            recs.append(r)
    except Exception:
        continue
check("6 real era-clone records present (.data/clones/*.json with source_sid+at)", bool(recs),
      f"found {len(recs)}")
if recs:
    mism = [r.get("handle") for r in recs
            if parse_clone_address(clone_address(r)) != {"source_sid": r["source_sid"], "cut": r["at"]}]
    check("7 ★ parse_clone_address(clone_address(rec)) == {source_sid, cut:at} for ALL real clones (seam agrees)",
          not mism, f"mismatches: {mism}")

# ── ★ resolve through the ONE resolver (clone:// joins board://·session://·cap://) ───────────────────
store = FsStore(os.path.join(REPO, ".data", "store"))
if recs:
    addr = clone_address(recs[0])
    r_clone = resolve_address(store, addr)
    check("8 ★ resolve_address(clone://<real>) → the clone record (+reflection) THROUGH the one resolver",
          isinstance(r_clone, dict) and r_clone.get("source_sid") == recs[0]["source_sid"],
          f"addr={addr}")
check("9 resolve_address(clone://bogus/x) RAISES (fail-loud, never silent-empty)",
      raises(lambda: resolve_address(store, "clone://bogus-sid-zzz/compact:0"), ValueError))

print(f"\n{'=' * 60}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — clone:// joins the ONE addressed state: parse_clone_address (declared grammar) agrees\n"
      "with cc_clone.clone_address over REAL era-clones (the seam meets), and resolve_address resolves\n"
      "clone://<source-sid>/<cut> → the clone record + persisted reflection through the one resolver,\n"
      "fail-loud on unknown. The clone-fleet (a) is now first-class addressed rows in the Heart (b).")
