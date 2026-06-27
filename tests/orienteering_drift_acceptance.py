"""tests/orienteering_drift_acceptance.py — the terrain ledger self-maintains.

The drift gate for `orienteering/` (the terrain ledger), declared INTO the coherence substrate. Rides
`company suites` (suite_health auto-discovers `tests/*_acceptance.py`). EXACT, gate-able:
every ledger entry's `path:` must exist on disk — so the ledger can't silently rot when a thing moves
(the foundation-move was the worked example). The orbit-coverage candidate is positive-only — it runs
and reports, but NEVER fails the gate (is-it-company is a judgment for Tim, never auto-decided).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime.orienteering_drift import (path_existence, orbit_coverage, orienteering_signoff,
                                        scan, format_scan, entry_paths)

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# the EXACT, gate-able check: every entry path the ledger claims must exist on disk
missing = path_existence(ROOT)
check(f"every ledger entry path exists on disk ({len(entry_paths(ROOT))} entries; missing: {[m['slug'] for m in missing]})",
      not missing)

signoff = orienteering_signoff(ROOT)
check(f"orienteering drift signoff PASSES ({signoff['reasons']})", signoff["pass"])

# the dispositions registry must load (fail-loud if missing — never treat the whole orbit as uncatalogued)
cov = orbit_coverage(ROOT)
check("orbit-coverage candidate check runs (positive-only — never auto-fails the gate)",
      isinstance(cov["uncatalogued"], list) and isinstance(cov["stale"], list))

# the finding flows end-to-end through the substrate's burn_down (own/reflect, re-derived)
result = scan(ROOT)
check(f"scan folds through the coherence burn_down model (open={result['burn_down']['open']})",
      "burn_down" in result and "open" in result["burn_down"])

# the read renders (FORM bar — a navigable surface, not a dict dump)
rendered = format_scan(result)
check("format_scan renders the read", isinstance(rendered, str) and "ORIENTEERING DRIFT" in rendered)

print(f"\n--- orienteering drift read ---\n{rendered}")
print(f"\nALL {PASS} CHECKS PASS — ledger path-existence gate + positive-only orbit-coverage, in the coherence substrate")
