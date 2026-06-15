"""tests/minds_acceptance.py — R13 composable-mind (runtime/minds.py, the fork's disjoint build).

Verifies the buildable bars: registry discover + resolve + fail-loud (bar 6); traverse → ordered
role-shaped minds (the cast_for_mode shape: Role objects .id/.can_fire/.is_jury) resolved THROUGH
resolve_address (bar 2 — its LOGIC + cast-shape; the REAL resolve_address mind:// branch is the lead's
seam A, so we simulate that one branch here and the live end-to-end is the meet-point cacc9e8b verifies on
landing); recompose = a ROW edit, ZERO code (bar 1); binding_for_mode. Run: python3 tests/minds_acceptance.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import runtime.minds as minds
import runtime.cognition as cognition

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'ok ' if cond else 'FAIL'} {name}" + (f"  — {detail}" if detail and not cond else ""))


# ── registry: discover the 4 first-unit rows + resolve (by id and mind://) ──
reg = minds.mind_registry()
ok("registry discovers the first-unit rows (extractor, judge, pair, binding)",
   {"extractor", "judge", "pair", "bind_compose_test"}.issubset(set(reg)))
ok("resolve(id) and resolve(mind://id) both return the row",
   reg.resolve("pair").kind == "composition" and reg.resolve("mind://pair").id == "pair")
ok("pair is a composition of [extractor, judge] with the extractor→judge order-edge",
   reg.resolve("pair").members == ["extractor", "judge"]
   and reg.resolve("pair").order[0]["from"] == "extractor" and reg.resolve("pair").order[0]["to"] == "judge")

# ── bar 6: fail-loud on an unknown mind (the blob/vec guard) ──
try:
    reg.resolve("mind://nonexistent")
    ok("bar 6: resolve fails loud on an unknown mind", False)
except minds.MindError as e:
    ok("bar 6: resolve fails loud on an unknown mind", "unknown mind" in str(e))

# ── bar 2: traverse → ordered ROLE-SHAPED minds, resolved THROUGH resolve_address ──
# The REAL mind:// branch in resolve_address is the lead's seam A (not landed during the fork's build), so
# we SIMULATE that ONE branch (route mind://→registry.resolve) to verify traverse's composition logic +
# the cast-shape. The live end-to-end (real resolve_address) is the meet-point cacc9e8b verifies on landing.
_orig_resolve = cognition.resolve_address
def _resolve_with_mind(store, addr, **k):
    if isinstance(addr, str) and addr.startswith("mind://"):
        return minds.mind_registry().resolve(addr)          # the seam-A branch, simulated
    return _orig_resolve(store, addr, **k)
cognition.resolve_address = _resolve_with_mind
try:
    cast = minds.traverse(reg.resolve("pair"), store=None)
    ok("bar 2: traverse returns the ordered cast (extractor→judge), RESOLVED minds not strings",
       [getattr(m, "id", None) for m in cast] == ["mine_exchange", "judge_mining"])
    ok("bar 2: traverse output is the EXACT cast_for_mode shape (Role objects: .id/.can_fire/.is_jury)",
       all(hasattr(m, "id") and hasattr(m, "can_fire") and hasattr(m, "is_jury") for m in cast))
    ok("traverse resolves the role-mind to its real roles/ Role (mine_exchange fires)",
       cast[0].id == "mine_exchange" and cast[0].can_fire)
finally:
    cognition.resolve_address = _orig_resolve

# ── binding_for_mode (mode→composition as a row) ──
ok("binding_for_mode(compose-test) → pair (the mode→composition row)",
   minds.binding_for_mode("compose-test") == "pair")
ok("binding_for_mode(unknown-mode) → None (never a default-fire)",
   minds.binding_for_mode("no-such-mode") is None)

# ── bar 1: recompose = a ROW edit, ZERO code (a fresh row file becomes live on rediscover) ──
tmp = tempfile.mkdtemp(prefix="minds_recompose_")
open(os.path.join(tmp, "extractor.py"), "w").write("MIND = {'id':'extractor','kind':'role','role':'mine_exchange'}")
open(os.path.join(tmp, "judge.py"), "w").write("MIND = {'id':'judge','kind':'role','role':'judge_mining'}")
open(os.path.join(tmp, "pair.py"), "w").write(
    "MIND = {'id':'pair','kind':'composition','members':['extractor','judge'],'order':[{'from':'extractor','to':'judge','kind':'feeds'}]}")
r2 = minds.MindRegistry().discover([tmp])
before = list(r2.resolve("pair").members)
# add a third member by EDITING the row file (no code) — recompose
open(os.path.join(tmp, "ground.py"), "w").write("MIND = {'id':'ground','kind':'role','role':'ground'}")
open(os.path.join(tmp, "pair.py"), "w").write(
    "MIND = {'id':'pair','kind':'composition','members':['extractor','judge','ground'],'order':[{'from':'extractor','to':'judge','kind':'feeds'}]}")
r3 = minds.MindRegistry().discover([tmp])
ok("bar 1: recompose = a ROW edit (members extractor,judge → +ground), ZERO code",
   before == ["extractor", "judge"] and r3.resolve("pair").members == ["extractor", "judge", "ground"])

import shutil
shutil.rmtree(tmp, ignore_errors=True)

print(f"\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — R13 composable-mind: registry discover/resolve/fail-loud, traverse→ordered cast (Role "
      "shape, through-resolver logic), binding_for_mode, recompose-by-row (zero code). The 4 locked "
      "signatures hold; live end-to-end (real resolve_address mind:// + run_swarm) is the meet-point with the lead's seams A/B.")
