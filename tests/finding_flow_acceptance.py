"""tests/finding_flow_acceptance.py — the substrate flows END-TO-END on REAL data (C6).

Wires the trustworthy structural detector (reachability) to WRITE findings into the store, seeding each
catalogued orphan's disposition from the declared orphan-routes catalogue (the _ORPHAN_ROUTES→finding-records
migration). Then the burn_down rollup reflects the REAL backlog, not fixtures: detector → finding-store →
disposition overlay → burn_down. Proves:
  · every real orphan route lands as a finding;
  · a catalogued orphan's disposition is seeded from its tag (to_wire/to_build_ui → open-finish; voice_owned/
    backend_only → accepted) — the real backlog as the burn-down model;
  · re-detection does NOT inflate the model (own/reflect: dedup on read);
  · an operator disposition is NOT clobbered by the catalogue default on re-detection (the decision persists).
Only the trustworthy/exact detector writes burn-down findings; the candidate detectors stay report-only
(positive-only — they don't inflate the must-fix count).
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime import coherence_detect as cd

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

# expected, computed from the live detector + catalogue (robust — no hardcoded counts)
routes, wired = cd.route_reachability(ROOT)
orphans = [r for r in routes if not wired.get(r)]
catalogue = json.load(open(os.path.join(ROOT, "design", "_system", "orphan-routes.json")))["routes"]
ACCEPTED_TAGS = {"voice_owned", "backend_only", "by-design"}
exp_accepted = sum(1 for r in orphans if r in catalogue and catalogue[r]["tag"] in ACCEPTED_TAGS)
exp_open = len(orphans) - exp_accepted   # to_wire/to_build_ui + any uncatalogued NEW orphan

root = os.path.join(tempfile.mkdtemp(prefix="flow-"), "store")
store = FsStore(root)

res = cd.record_structural_findings(store, ROOT)
check(f"recorded one finding per real orphan route ({len(orphans)})", res["recorded"] == len(orphans))

roll = cd.burn_down(store)
check(f"burn_down total == distinct orphans ({len(orphans)})", roll["total"] == len(orphans))
check(f"open == the finish-backlog ({exp_open}: to_wire/to_build_ui + new)", roll["open"] == exp_open)
check(f"accepted == the dispositioned-accepted ({exp_accepted}: voice_owned/backend_only)", roll["accepted"] == exp_accepted)
check("open + accepted + closed == total (every finding classified, none lost)",
      roll["open"] + roll["accepted"] + roll["closed"] == roll["total"])

# a known voice route is seeded voice_owned → accepted (the catalogue tag became the disposition)
if "/api/voice/load" in orphans:
    d = store.disposition_for("unwired-route", "/api/voice/load")
    check("a catalogued voice orphan is seeded voice_owned (catalogue→disposition migration)",
          d and d["disposition"] == "voice_owned" and d["by"] == "catalogue")

# own/reflect: re-detection does NOT inflate; and an OPERATOR disposition survives the catalogue re-seed
store.append_disposition("unwired-route", "/api/knobs", "resolved", reason="wired it", by="tim")
cd.record_structural_findings(store, ROOT)   # re-run — re-detects, re-seeds catalogue defaults
roll2 = cd.burn_down(store)
check("re-detection does NOT inflate the model (still N distinct)", roll2["total"] == len(orphans))
if "/api/knobs" in orphans:
    d2 = store.disposition_for("unwired-route", "/api/knobs")
    check("the OPERATOR disposition survives re-detection (not clobbered by the catalogue default)",
          d2["disposition"] == "resolved" and d2["by"] == "tim")

print(f"\nALL {PASS} CHECKS PASS — the substrate flows end-to-end on REAL data: reachability → finding-store "
      f"→ disposition overlay (catalogue-seeded) → burn_down. The real orphan backlog IS the burn-down model.")
