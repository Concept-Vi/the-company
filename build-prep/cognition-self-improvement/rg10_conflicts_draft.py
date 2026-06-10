#!/usr/bin/env python3
"""rg10_conflicts_draft.py — DRAFT resolutions for the 33 cross-screen conflicts (Decision 2,
option 1 prepared ahead per refine-before-gating). DETERMINISTIC judgment — each pick carries its
named heuristic; Tim scans and vetoes. PROPOSES an artifact only (.build/rg10/conflict-drafts.json).

Heuristics, in precedence order (each resolution names which one decided it):
  H1 DEDICATED-SCREEN — the variant from the element's own screen wins (the inspector screen's
     reading of the inspector outranks a passing appearance elsewhere). Match: an address segment
     appears in the mockup filename.
  H2 FEATURE-REALITY — a variant naming a REAL inventory feature beats 'proposed'; a 'built' claim
     REQUIRES the feature to be real (else demoted).
  H3 RICHNESS — the variant with the fullest at-altitude prose (howto lengths) wins.
Ties after H1–H3 → the first confirmed-class variant, else the first (named as H4 ORDER)."""
import json
import os
import sys

os.chdir("/home/tim/company")
OUT = ".build/rg10/conflict-drafts.json"


def main() -> dict:
    rec = json.load(open(".build/rg10/reconciled.json", encoding="utf-8"))
    reg = json.load(open("design/register.json", encoding="utf-8"))
    real_ids = {f["id"] for f in reg["features"]}
    conflicts = [e for e in rec["entries"] if e["class"] == "conflict"]

    drafts = []
    for e in conflicts:
        addr_segs = [s for s in e["address"].replace("ui://", "").split("/") if s]
        variants = e["variants"]

        def h1(v):
            stem = v["mockup"].lower()
            return any(seg.lower() in stem for seg in addr_segs)

        def h2(v):
            mtf = v.get("maps_to_feature") or ""
            real = mtf in real_ids
            built_ok = v.get("grounding") != "built" or real
            return (real, built_ok)

        def rich(v):
            d = v.get("dossier") or {}
            h = d.get("howto") or {}
            return len(str(h.get("what", ""))) + len(str(h.get("what_you_can_do", "")))

        pick, why = None, ""
        dedicated = [v for v in variants if h1(v)]
        if len(dedicated) == 1:
            pick, why = dedicated[0], "H1 dedicated-screen: its own screen's reading wins"
        if pick is None:
            real_vs = [v for v in variants if h2(v) == (True, True)]
            if len(real_vs) == 1:
                pick, why = real_vs[0], "H2 feature-reality: the only variant naming a real, honestly-claimed feature"
            elif dedicated and len({v["maps_to_feature"] for v in dedicated}) == 1:
                pick, why = dedicated[0], "H1+H2: dedicated-screen variants agree among themselves"
        if pick is None:
            ranked = sorted(variants, key=rich, reverse=True)
            if rich(ranked[0]) > rich(ranked[1]) * 1.5 if len(ranked) > 1 else False:
                pick, why = ranked[0], "H3 richness: clearly fullest at-altitude description"
        if pick is None:
            pick, why = variants[0], "H4 order: no heuristic separates them — flagged for your eyes especially"

        # demote a 'built' claim whose feature isn't real (never silently keep a false built)
        grounding = pick.get("grounding")
        if grounding == "built" and (pick.get("maps_to_feature") or "") not in real_ids:
            grounding = "proposed"
        drafts.append({
            "address": e["address"], "heuristic": why,
            "picked": {"mockup": pick["mockup"], "maps_to_feature": pick.get("maps_to_feature"),
                       "grounding": grounding, "represents": pick.get("represents")},
            "rejected": [{"mockup": v["mockup"], "maps_to_feature": v.get("maps_to_feature"),
                          "represents": v.get("represents")} for v in variants if v is not pick],
            "needs_eyes": why.startswith("H4"),
        })

    out = {"drafts": drafts,
           "summary": {"total": len(drafts),
                       "by_heuristic": {},
                       "needs_eyes": sum(1 for d in drafts if d["needs_eyes"])}}
    for d in drafts:
        k = d["heuristic"].split(":")[0]
        out["summary"]["by_heuristic"][k] = out["summary"]["by_heuristic"].get(k, 0) + 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1)
    return out["summary"]


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
