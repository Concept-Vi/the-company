"""tests/territory_acceptance.py — the address→territory composer's OPERATOR-LAW + DEGRADE contract (fork).

Locks the invariants verified by-use during the operator-surface/RHM sprint (2026-06-17) — the regression
guard for the leak projection caught live (the brain narrated a raw address / system-readout jargon because
territory_prose dumped the raw address_help dict). These are DATA-INDEPENDENT invariants (degrade cases +
non-address + the never-raises contract), so the suite is deterministic on a fresh temp store — no reliance
on specific live corpus rows.

  OPERATOR-LAW (feedback-translate-everything-human-meaning): the operator NEVER sees code/files/machine
    names. So territory_label NEVER returns the raw address (degrades to a human scheme-noun), and
    territory_prose leaks no scheme:// string into any operator-VISIBLE line (the raw address survives ONLY
    in the explicitly-labeled "[internal handle …]" line, which is FOR the brain, never shown to Tim).
  DEGRADE CONTRACT (TERRITORY_FOR_DESIGN.md, advisor-hardened): territory_for RAISES only on a non-address;
    territory_prose NEVER raises (context-gathering must never kill a brain turn); a nonexistent record /
    non-resolvable scheme degrades to a noted-absent leg, not a crash.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime.territory import territory_for, territory_prose, territory_label

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


store = FsStore(os.path.join(tempfile.mkdtemp(prefix="territory-"), "store"))
reg = NodeRegistry(); reg.discover([os.path.join(ROOT, "nodes")])
su = Suite(store, reg, nodes_dir=os.path.join(ROOT, "nodes"))

# Addresses that have NO data in this fresh store — they exercise the DEGRADE paths (the bug-prone ones).
DEGRADE_ADDRS = [
    "ui://instrument/surface",          # unregistered ui:// — address_help echoes "(unregistered)" (the leak source)
    "session://bogus-nonexistent",      # resolvable scheme, nonexistent record → resolve_address raises → noted-absent
    "vec://some-source#emb=x",          # non-resolvable scheme → identity noted-absent
    "board://item-does-not-exist",      # resolvable scheme, missing record
    "vi-vision://global/organism/x",    # the factory scheme, register-but-defer / no transport
]


def _human_lines(prose):
    # everything the operator sees — i.e. NOT the explicitly-labeled internal-handle line (which is for the brain).
    return [ln for ln in prose.split("\n") if not ln.startswith("[internal handle")]


print("[OL] OPERATOR-LAW — territory_label NEVER leaks a raw address / machine name")
for a in DEGRADE_ADDRS:
    lbl = territory_label(a, suite=su)
    check(f"territory_label({a}) is human, not the address (no '://', not ==/contains the addr)",
          isinstance(lbl, str) and "://" not in lbl and a not in lbl and lbl != a)
check("territory_label(non-address) → safe generic 'this' (never the raw input)",
      territory_label("not-an-address", suite=su) == "this")

print("\n[OL] OPERATOR-LAW — territory_prose leaks no scheme:// into any operator-visible line")
for a in DEGRADE_ADDRS:
    prose = territory_prose(a, suite=su)
    check(f"territory_prose({a}) human lines carry no '://' (raw addr only in the labeled internal-handle line)",
          all("://" not in ln for ln in _human_lines(prose)))
    check(f"territory_prose({a}) carries no system-readout jargon (no 'blast'/'unregistered')",
          "blast" not in prose.lower() and "unregistered" not in prose.lower())

print("\n[DG] DEGRADE CONTRACT — territory_for raises ONLY on a non-address; territory_prose NEVER raises")
# (1) non-address → territory_for RAISES (fail-loud-legible)
raised = False
try:
    territory_for("not-an-address", suite=su)
except ValueError:
    raised = True
check("territory_for(non-address) RAISES ValueError (fail-loud-legible)", raised)
# (2) territory_prose NEVER raises — not on a non-address, not on a bogus record, not on None-ish
for a in (["not-an-address", "", "session://bogus"] + DEGRADE_ADDRS):
    ok = True
    try:
        out = territory_prose(a, suite=su)
        ok = isinstance(out, str)
    except Exception:
        ok = False
    check(f"territory_prose({a!r}) returns a string, never raises", ok)
# (3) a nonexistent record degrades to a PARTIAL territory (noted-absent), not a crash
terr = territory_for("session://bogus-nonexistent", suite=su)
check("territory_for(nonexistent record) returns a dict with notes (degrade-clean, not void)",
      isinstance(terr, dict) and isinstance(terr.get("notes"), list))
check("territory_for(nonexistent record) identity leg noted-absent (legs_present.identity False)",
      terr.get("legs_present", {}).get("identity") is False)

# ── the vi-vision LIBRARY leg (the credential-free brain's compose-palette) — stubbed catalog, no live read ──
import runtime.vi_vision as _vv
_VVADDR = "vi-vision://project/p1/organism/component.organism.brand-icon"
_orig_catalog = _vv.vi_vision_catalog
try:
    _vv.vi_vision_catalog = lambda frame="global", **kw: [
        {"component_id": f"component.c{i}", "type": t, "name": n, "tags": [], "desc": ""}
        for i, (n, t) in enumerate([("Brand Icon", "organism"), ("Chip", "molecule"), ("Button", "atom")])]
    tv = territory_for(_VVADDR, suite=su)
    check("vi-vision library leg present (the compose-palette, only for vi-vision://)",
          tv.get("legs_present", {}).get("library") is True and tv["library"]["total"] == 3)
    pv = territory_prose(_VVADDR, suite=su)
    pv_human = "\n".join(ln for ln in pv.split("\n") if not ln.startswith("[internal handle"))
    check("prose renders the palette as HUMAN name+type (Chip (molecule)), never the raw component_id",
          "Chip (molecule)" in pv and "component.c" not in pv_human)
    check("vi-vision prose human lines carry no '://' (operator-law)", "://" not in pv_human)
    # degrade: a catalog transport error → library noted-absent, prose still a string (never raises)
    def _boom(frame="global", **kw):
        raise _vv.ViVisionTransportError("store down")
    _vv.vi_vision_catalog = _boom
    td = territory_for(_VVADDR, suite=su)
    check("catalog error → library leg noted-absent (degrade-clean, not a crash)",
          td.get("library") is None and any("library leg unresolved" in n for n in td["notes"]))
    check("territory_prose(vi-vision) returns a string even when the catalog errors (never raises)",
          isinstance(territory_prose(_VVADDR, suite=su), str))
    check("the library leg is vi-vision-ONLY (a board:// territory has no library leg)",
          territory_for("board://item-x", suite=su).get("legs_present", {}).get("library") is not True)
finally:
    _vv.vi_vision_catalog = _orig_catalog

print(f"\nALL {PASS} CHECKS PASS — territory composer holds the operator-law (no raw-address/jargon leak) "
      f"+ the degrade contract (territory_for raises only on non-address; territory_prose never raises) "
      f"+ the vi-vision compose-palette leg (human name+type, capped, degrade-clean, vi-vision-only).")
