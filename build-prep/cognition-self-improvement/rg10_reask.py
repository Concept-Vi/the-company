#!/usr/bin/env python3
"""rg10_reask.py — GC4: the FLOOR-TRIGGERED RE-ASK (Tim greenlit 2026-06-10: "yeah it needs that
improvement"). The deterministic floor's rejection reason is perfect feedback — feed it back for ONE
bounded re-fire, then re-gate. Fixable fabrications become confirmed entries; stubborn ones stay
flagged. The floor remains the gate (a re-asked dossier passes ONLY by passing the same floor + jury).

Per class='floor' entry in .build/rg10/reconciled.json:
  · rebuild the ORIGINAL element unit (artifact cluster_members[0] → candidates.json order per mockup —
    the same [c for c in cands if mockup_file==m] ordering the run used)
  · re-fire register_element with the SAME grounding ctx (exemplars+inventory+that mockup's ground)
    PLUS the floor's named reasons as an explicit correction
  · re-floor (check_dossier) + re-jury (run_jury confirm_registration) + confirm_status → new class
  · update reconciled.json IN PLACE (no-versioning law) — prior dossier kept under `prior_dossier`,
    `reasked: true` stamped (maximal capture; the history is visible)
Then ONE live card: retire s97 (STATUS lane) → surface the final reconciled card with true counts.
THE FLOOR: proposes only; the operator's resolved field is never touched."""
import json
import os
import sys

os.chdir("/home/tim/company")
sys.path.insert(0, "/home/tim/company")
sys.path.insert(0, "/home/tim/company/build-prep/cognition-self-improvement")
sys.path.insert(0, "/home/tim/company/design/_system")
REC = ".build/rg10/reconciled.json"
ART_DIR = "build-prep/cognition-self-improvement"


def main() -> dict:
    from registry_generation_run import _load_suite, _grounding_payload, _unit_of, EXEMPLAR_KEYS
    from runtime import cognition as C
    from runtime.roles import RoleRegistry, Role
    import importlib.util
    import refcheck

    rec = json.load(open(REC, encoding="utf-8"))
    floor_entries = [e for e in rec["entries"] if e["class"] == "floor"]
    if not floor_entries:
        return {"reasked": 0, "note": "no floor-class entries — nothing to re-ask"}

    suite = _load_suite()
    rr = RoleRegistry().discover(["roles"])
    reg, conf = rr.get("register_element"), rr.get("confirm_registration")
    spec2 = dict(reg.spec); spec2["input_addresses"] = ("utterance", "ground", "exemplars", "inventory")
    reg_v = Role(id=reg.id, spec=spec2, prompt_template=reg.prompt_template, output_schema=reg.output_schema,
                 mode_scope=reg.mode_scope, draws=reg.draws, op=reg.op)
    cspec = importlib.util.spec_from_file_location("confirm_reg_mod", "roles/confirm_registration.py")
    cm = importlib.util.module_from_spec(cspec); cspec.loader.exec_module(cm)
    exemplars, inventory, fids = _grounding_payload(EXEMPLAR_KEYS)
    cands = json.load(open("design/_system/candidates.json", encoding="utf-8"))["candidates"]

    # rebuild each floor entry's original unit + its mockup ground, grouped by mockup (shared ctx per group)
    by_mockup: dict = {}
    skipped = []
    for e in floor_entries:
        mockup = (e.get("sources") or [None])[0]
        art_fp = os.path.join(ART_DIR, f"rg10-batch-{mockup.replace('.html', '')}.json") if mockup else None
        if not (art_fp and os.path.exists(art_fp)):
            skipped.append({"address": e["address"], "why": f"no artifact for {mockup!r}"}); continue
        art = json.load(open(art_fp, encoding="utf-8"))
        src = next((x for grp in ("flagged", "confirmed") for x in art[grp]
                    if x["dossier"].get("address") == e["address"]), None)
        members = (src or {}).get("cluster_members") or []
        sel = [c for c in cands if c.get("mockup_file") == mockup]
        rep = members[0] if members else None
        if rep is None or not isinstance(rep, int) or rep >= len(sel):
            skipped.append({"address": e["address"], "why": f"cluster rep {rep!r} unresolvable"}); continue
        floor_reasons = [r for r in e["confirm"].get("reasons", []) if r.startswith("refcheck")]
        correction = ("\nCORRECTION (a previous attempt FAILED the deterministic fact-check):\n"
                      + "\n".join(f"  - {r}" for r in floor_reasons)
                      + "\nFix EXACTLY this: maps_to_feature must be COPIED VERBATIM from the allowed list, "
                        "or be the literal word 'proposed'. capabilities must use ONLY the allowed words.")
        by_mockup.setdefault(mockup, []).append(
            {"entry": e, "unit": _unit_of(sel[rep]) + correction, "ground": json.dumps(art.get("ground") or {})})

    moved = {"confirmed": 0, "jury": 0, "floor": 0}
    for mockup, rows in by_mockup.items():
        res = C.run_items(reg_v, [r["unit"] for r in rows], suite.store, turn_id=f"reask-{mockup[:10]}",
                          ctx={"ground": rows[0]["ground"], "exemplars": exemplars, "inventory": inventory},
                          max_tokens=400)
        resolved = res.resolved if isinstance(res.resolved, dict) else {}
        for i, row in enumerate(rows):
            e = row["entry"]
            new_d = resolved.get(i)
            if not isinstance(new_d, dict):                  # re-ask itself failed → stays floor, loudly
                e.setdefault("reask_failed", str((dict(res.failed) or {}).get(i, "no output"))[:200])
                moved["floor"] += 1
                continue
            jres = C.run_jury(conf, {"utterance": json.dumps(new_d), "element": row["unit"]},
                              suite.store, turn_id=f"reask-confirm-{e['address'][-20:]}")
            cs = cm.confirm_status(new_d, jres.verdict, feature_ids=fids)
            e["prior_dossier"], e["dossier"], e["reasked"] = e["dossier"], new_d, True
            e["confirm"] = {"status": cs["status"], "confirmed": cs["confirmed"],
                            "jury": cs["jury"], "reasons": cs["reasons"]}
            if cs["confirmed"]:
                e["class"] = "confirmed"
            elif any(r.startswith("refcheck") for r in cs["reasons"]):
                e["class"] = "floor"
            else:
                e["class"] = "jury"
            moved[e["class"]] += 1

    # recount + persist IN PLACE
    counts = {"confirmed": 0, "floor": 0, "jury": 0, "conflict": 0}
    for e in rec["entries"]:
        counts[e["class"]] += 1
    rec["counts"] = counts
    json.dump(rec, open(REC, "w"), indent=1)
    return {"reasked": sum(len(v) for v in by_mockup.values()), "moved_to": moved,
            "skipped": skipped, "new_counts": counts}


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
