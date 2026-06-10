#!/usr/bin/env python3
"""rg10_rejury.py — the PANEL RE-JURY of the jury-flagged registry entries (Tim's standing approval,
2026-06-10: refinement passes run autonomously; his gate receives the smallest refined set — "I was
not happy with being given 222 things").

Per class='jury' entry in .build/rg10/reconciled.json: rebuild its REAL element (cluster_members →
candidates order — the context law; a fit-lens without the element rightly dissents) → run_panel
(registration_confirm: grounding · voice · element-fit, quorum 2/3, temperature-0 lenses) →
  · verdict True  → class 'confirmed' (the floor already passed for every jury-class entry —
                    jury-class ⟺ floor-clean + old-jury-no-quorum; the panel supersedes the old
                    same-role draw-jury, whose no-quorum was variance, not judgment)
  · verdict False → class 'panel' — STAYS flagged, now with NAMED seat dissents (the review object)
Entry-idempotent (entries already carrying `panel` skip) → bounded batches compose; fail-loud per
entry. PROPOSES classes only — reconciled.json updates in place; the registry write stays behind
Tim's approve."""
import json
import os
import sys
import time

os.chdir("/home/tim/company")
sys.path.insert(0, "/home/tim/company")
sys.path.insert(0, "/home/tim/company/build-prep/cognition-self-improvement")
REC = ".build/rg10/reconciled.json"
ART_DIR = "build-prep/cognition-self-improvement"


def run_batch(time_budget_s: int = 600) -> dict:
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    from runtime.verdict_panels import PanelRegistry
    from runtime import cognition as C
    from registry_generation_run import _unit_of

    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    panel = PanelRegistry().discover().get("registration_confirm")
    rec = json.load(open(REC, encoding="utf-8"))
    cands = json.load(open("design/_system/candidates.json", encoding="utf-8"))["candidates"]
    arts: dict = {}

    def element_of(e):
        mockup = (e.get("sources") or [None])[0]
        if not mockup:
            return None
        if mockup not in arts:
            fp = os.path.join(ART_DIR, f"rg10-batch-{mockup.replace('.html', '')}.json")
            arts[mockup] = json.load(open(fp, encoding="utf-8")) if os.path.exists(fp) else None
        art = arts[mockup]
        if not art:
            return None
        src = next((x for g in ("confirmed", "flagged") for x in art[g]
                    if x["dossier"].get("address") == e["address"]), None)
        members = (src or {}).get("cluster_members") or []
        sel = [c for c in cands if c.get("mockup_file") == mockup]
        rep = members[0] if members else None
        return _unit_of(sel[rep]) if isinstance(rep, int) and rep < len(sel) else None

    todo = [e for e in rec["entries"] if e["class"] == "jury" and "panel" not in e]
    t0, done, failed = time.time(), 0, []
    for e in todo:
        if time.time() - t0 > time_budget_s:
            break
        el = element_of(e)
        if el is None:                                       # no rebuildable element — recorded, never silent
            e["panel"] = {"error": "element unrebuildable (artifact/cluster gap)", "verdict": None}
            failed.append(e["address"])
            continue
        try:
            out = C.run_panel(panel, {"utterance": json.dumps(e["dossier"]), "element": el},
                              s.store, turn_id=f"rejury-{e['address'][-16:]}",
                              resolve_role=lambda rid: s.role_registry.get(rid))
        except Exception as ex:
            e["panel"] = {"error": f"{type(ex).__name__}: {ex}"[:200], "verdict": None}
            failed.append(e["address"])
            continue
        e["panel"] = {"verdict": out["verdict"], "grounded_seats": out["grounded_seats"],
                      "quorum": out["quorum"], "seats": out["seats"]}
        e["class"] = "confirmed" if out["verdict"] else "panel"
        done += 1
        if done % 10 == 0:
            json.dump(rec, open(REC, "w"), indent=1)
            print(f"  …{done} judged", flush=True)

    counts: dict = {}
    for e in rec["entries"]:
        counts[e["class"]] = counts.get(e["class"], 0) + 1
    rec["counts"] = counts
    json.dump(rec, open(REC, "w"), indent=1)
    remaining = sum(1 for e in rec["entries"] if e["class"] == "jury" and "panel" not in e)
    return {"judged_this_batch": done, "failed": failed, "remaining": remaining, "counts": counts}


if __name__ == "__main__":
    print(json.dumps(run_batch(int(sys.argv[1]) if len(sys.argv) > 1 else 600), indent=1, default=str))
