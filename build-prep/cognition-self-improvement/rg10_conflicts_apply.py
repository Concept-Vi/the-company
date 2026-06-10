#!/usr/bin/env python3
"""rg10_conflicts_apply.py — apply the conflict resolutions (Decision 2, Tim's delegation 2026-06-10:
"you're going to need to investigate and you will be a better judge" + his MULTI-JOB insight:
"elements that do multiple jobs depending on what else is happening — will have to be accounted for").

The 21 heuristic-clean drafts apply as drafted. The 12 needs-eyes carry the LEAD'S INVESTIGATED
JUDGMENT (the table below — each with its why; the investigation dossier at
.build/rg10/conflict-investigation.json). TWO are genuine MULTI-JOB elements (Tim's insight) — they
keep a PRIMARY role + an additive `roles` field naming each contextual face (schema-additive;
consumers reading known fields are untouched). Resolved entries write back through the same gated
path as Decision 1. Conflicts among CURATED entries are NOT here (their own pass)."""
import json
import os
import sys

os.chdir("/home/tim/company")
sys.path.insert(0, "/home/tim/company")
sys.path.insert(0, "/home/tim/company/design/_system")

# the lead's judgments for the 12 H4 conflicts — {address: (winning maps_to_feature, grounding,
# multi_roles or None, why)}
JUDGMENTS = {
    "ui://activity/audit": ("EVT-log", "proposed", None,
                            "the element IS the log view; ENG-resolve is the mechanism behind it"),
    "ui://canvas/portal": ("NODE-portal", "built", None,
                           "NODE-portal is real and nodes/portal.py exists — the draft's 'proposed' pick lost to reality"),
    "ui://canvas/process": ("NODE-kinds", "proposed", None, "variants agree on the feature — not a real conflict"),
    "ui://chat/process-11": ("ENG-volatile", "uncertain", None,
                             "the twin screen depicts a volatile process node; low confidence — uncertain tag kept"),
    "ui://chat/utterance": ("proposed", "proposed", None,
                            "RHM-utterance is NOT a real inventory id — joins the proposed-features pile; "
                            "two foreign variants were mis-collapsed into this address (noted)"),
    "ui://chat/walk": ("WALK-present", "built", ["WALK-present", "WALK-session"],
                       "MULTI-JOB (Tim's insight): presents the current step AND fronts the whole session"),
    "ui://inbox/build-review/lifecycle-states": ("WIRE-states", "built", None,
                                                 "the element is the states display; WIRE-review is its container"),
    "ui://inbox/idea": ("INB-idea", "built", None, "INB-idea is real (idea_capture exists)"),
    "ui://rail/palette/node-kinds": ("NODE-kinds", "proposed", None, "variants agree — not a real conflict"),
    "ui://tabbar/inbox": ("INB-surface", "built", None, "the tab opens the SURFACE; lanes live inside it"),
    "ui://toolbar/layers": ("CAN-layers", "built", ["CAN-layers", "NODE-layer", "SM-revert"],
                            "MULTI-JOB poster child: canvas layers + node layering + self-mod revert by screen"),
    "ui://toolbar/wire": ("WIRE-intent", "built", None, "all six variants agree — not a real conflict"),
}


def main() -> dict:
    import registry_writeback as wb
    rec = json.load(open(".build/rg10/reconciled.json", encoding="utf-8"))
    drafts = {d["address"]: d for d in json.load(open(".build/rg10/conflict-drafts.json"))["drafts"]}
    cands = json.load(open("design/_system/candidates.json", encoding="utf-8"))["candidates"]

    entries, resolved = [], 0
    for e in [x for x in rec["entries"] if x["class"] == "conflict"]:
        addr = e["address"]
        d = drafts.get(addr)
        if addr in JUDGMENTS:
            feat, ground, roles, why = JUDGMENTS[addr]
        else:
            feat = d["picked"]["maps_to_feature"]; ground = d["picked"]["grounding"]
            roles, why = None, d["heuristic"]
        # the winning variant's FULL dossier (richest matching the picked feature, else first)
        variants = e["variants"]
        win = next((v for v in variants if v.get("maps_to_feature") == feat), variants[0])
        dossier = dict(win.get("dossier") or {})
        dossier["maps_to_feature"] = feat if feat == "proposed" or feat else "proposed"
        dossier["grounding"] = ground
        if roles:
            dossier["roles"] = roles                       # additive: the contextual faces (Tim's multi-job)
        mockup = win["mockup"]
        sel = [c for c in cands if c.get("mockup_file") == mockup]
        # locate the candidate by address via the batch artifact
        art_fp = f"build-prep/cognition-self-improvement/rg10-batch-{mockup.replace('.html','')}.json"
        art = json.load(open(art_fp, encoding="utf-8")) if os.path.exists(art_fp) else {}
        src = next((x for g in ("confirmed", "flagged") for x in art.get(g, [])
                    if x["dossier"].get("address") == addr), None)
        rep = ((src or {}).get("cluster_members") or [None])[0]
        cand = sel[rep] if isinstance(rep, int) and rep < len(sel) else None
        entries.append({"address": addr, "represents": dossier.get("represents"),
                        "howto": dossier.get("howto"), "capabilities": dossier.get("capabilities"),
                        "maps_to_feature": dossier.get("maps_to_feature"),
                        "mockup_file": mockup, "outerHTML": (cand or {}).get("outerHTML", ""),
                        "run": "rg10-conflict-resolution", "model": "lead-investigated"})
        if roles:
            entries[-1]["roles"] = roles
        e["class"] = "confirmed"
        e["resolution"] = {"picked_feature": feat, "grounding": ground, "roles": roles, "why": why}
        resolved += 1

    # curated-overlap partition (same as Decision 1's): an entry whose address is already registered
    # with DIFFERENT content is a proposal to CHANGE curated truth — held for its own pass, never
    # folded in (the writeback would refuse the whole batch otherwise).
    registry = json.load(open("design/_system/addresses.json", encoding="utf-8"))["addresses"]
    safe, curated_held = [], []
    for en in entries:
        _addr, record = wb._dossier_to_entry(en)
        ex = registry.get(_addr)
        if ex is None or all(ex.get(k) == record.get(k)
                             for k in ("region", "represents", "howto", "capabilities", "maps_to_feature")):
            safe.append(en)
        else:
            curated_held.append(_addr)
    report = wb.registry_writeback(safe, write=True, skip_already_stamped=True)
    counts = {}
    for x in rec["entries"]:
        counts[x["class"]] = counts.get(x["class"], 0) + 1
    rec["counts"] = counts
    json.dump(rec, open(".build/rg10/reconciled.json", "w"), indent=1)
    return {"resolved": resolved,
            "added": sum(1 for m in report["merged"] if m["status"] == "added"),
            "stamp_skipped": len(report.get("stamp_skipped", [])),
            "curated_held": curated_held,
            "multi_job": [a for a, j in JUDGMENTS.items() if j[2]],
            "counts": counts}


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
