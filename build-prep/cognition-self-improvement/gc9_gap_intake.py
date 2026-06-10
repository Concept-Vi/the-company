#!/usr/bin/env python3
"""gc9_gap_intake.py — GC9: the INVENTORY-GAP INTAKE — the registry-filling pattern's SECOND instance,
pointed at the FEATURE INVENTORY itself (design/register.json features). DETERMINISTIC end-to-end
(no model — the strongest form of the no-fiction floor: every field derives from data that exists).

SOURCE: the 18 stubborn-floor entries in .build/rg10/reconciled.json — each carries the feature id
the model INSISTED on through correction (the gap signal) + the dossier's at-altitude prose.
MAP (deterministic): proposed feature row {id: the insisted name, area: derived from the id PREFIX
via the REAL inventory's own prefix→area map (registry-derived, never hand-written), label: the
dossier's `represents`/`what` prose, code: "" (mockup-only — unbuilt)}.
FLOOR (deterministic): id format ^[A-Z]+-[a-z_-]+$ · area resolved (an unknown prefix FLAGS, never
guesses) · no collision with a REAL inventory id · label non-empty.
WRITE: each gap entry in reconciled.json gains `proposed_feature` (update-in-place — the walk's
stop-3 artifact is the truth the surface reads). PROPOSES ONLY — register.json is untouched; Tim's
stop-3 verdict is what authorizes any inventory growth."""
import json
import os
import re
import sys
from collections import Counter

os.chdir("/home/tim/company")
REC = ".build/rg10/reconciled.json"


def main() -> dict:
    reg = json.load(open("design/register.json", encoding="utf-8"))
    real_ids = {f["id"] for f in reg["features"]}
    # the prefix→area map DERIVED from the real inventory (registry-is-truth; ambiguity flags loud)
    pref_areas = {}
    for f in reg["features"]:
        pref = f["id"].split("-", 1)[0]
        pref_areas.setdefault(pref, Counter())[f["area"]] += 1
    prefix_map = {}
    for pref, areas in pref_areas.items():
        top, n = areas.most_common(1)[0]
        if n / sum(areas.values()) < 1.0:
            prefix_map[pref] = None        # ambiguous prefix — flag, never guess
        else:
            prefix_map[pref] = top

    rec = json.load(open(REC, encoding="utf-8"))
    gaps = [e for e in rec["entries"] if e["class"] == "floor"]
    proposed, flagged = [], []
    for e in gaps:
        d = e["dossier"]
        fid = (d.get("maps_to_feature") or "").strip()
        # label = the at-altitude PROSE (howto.what), never the id echo: register_element puts the
        # feature NAME in `represents` (the first run labelled every row with its own id — caught by
        # look-at-output). represents is the fallback only when it is real prose, not the id.
        what = (d.get("howto") or {}).get("what") or ""
        rep = (d.get("represents") or "").strip()
        label = what.strip() or (rep if rep and rep != fid else "")
        reasons = []
        if not re.fullmatch(r"[A-Z]+-[a-z][a-z_-]*", fid):
            reasons.append(f"id {fid!r} does not match the inventory id shape")
        if fid in real_ids:
            reasons.append(f"id {fid!r} already EXISTS in the inventory (not a gap — a reconcile miss)")
        pref = fid.split("-", 1)[0] if "-" in fid else ""
        area = prefix_map.get(pref)
        if area is None:
            reasons.append(f"prefix {pref!r} is unknown/ambiguous in the real inventory — area cannot "
                           f"be derived (an invented area would be fiction)")
        if not label:
            reasons.append("no label derivable from the dossier")
        row = {"id": fid, "area": area, "label": label[:140], "code": "",
               "origin": "mockup-gap (RG10 stubborn-floor)", "ui_address": e["address"]}
        if reasons:
            e["proposed_feature"] = {"status": "FLAGGED", "row": row, "reasons": reasons}
            flagged.append({"id": fid, "reasons": reasons})
        else:
            e["proposed_feature"] = {"status": "proposed", "row": row}
            proposed.append(row)

    # within-batch MERGE: two elements insisting the SAME feature id = ONE proposed feature carrying
    # both ui addresses (correct inventory semantics — a feature maps from many surface elements).
    # Deterministic representative label: the longest prose (most specific).
    by_id: dict = {}
    for r in proposed:
        if r["id"] in by_id:
            prev = by_id[r["id"]]
            prev["ui_addresses"] = sorted(set(prev.get("ui_addresses", [prev.pop("ui_address", None)])
                                              ) | {r["ui_address"]} - {None})
            if len(r["label"]) > len(prev["label"]):
                prev["label"] = r["label"]
        else:
            by_id[r["id"]] = r
    merged = []
    for r in by_id.values():
        if "ui_address" in r:
            r["ui_addresses"] = [r.pop("ui_address")]
        merged.append(r)

    json.dump(rec, open(REC, "w"), indent=1)
    return {"gaps": len(gaps), "proposed_features": len(merged), "flagged": flagged,
            "by_area": dict(Counter(r["area"] for r in merged)),
            "rows": merged}


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
