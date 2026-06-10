#!/usr/bin/env python3
"""rg10_redescribe.py — the RE-DESCRIBE pass over the panel-flagged dossiers (the standing
refine-before-gating rule: exhaust buildable refinements before the gate). The GC4 mechanism aimed at
CONTENT defects: the 77 remaining flags all carry BOTH content lenses' named dissents (mis-described
elements — 'claims it pauses the tour; the text says it opens the workshop'). Feed those reasons back
to register_element with the full grounding package → a corrected dossier → re-floor (refcheck) +
re-prose (deterministic) + re-panel (confirm+fit seats) → confirmed only by passing EVERYTHING.
Entry-idempotent (redescribed flag); prior dossier kept. PROPOSES only."""
import json
import os
import sys
import time

os.chdir("/home/tim/company")
sys.path.insert(0, "/home/tim/company")
sys.path.insert(0, "/home/tim/company/build-prep/cognition-self-improvement")
sys.path.insert(0, "/home/tim/company/design/_system")
REC = ".build/rg10/reconciled.json"
ART_DIR = "build-prep/cognition-self-improvement"


def run_batch(time_budget_s: int = 1800) -> dict:
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    from runtime.roles import RoleRegistry, Role
    from runtime import cognition as C
    from registry_generation_run import _grounding_payload, _unit_of, EXEMPLAR_KEYS
    from prose_check import check_prose
    import refcheck

    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    rr = RoleRegistry().discover(["roles"])
    reg = rr.get("register_element")
    spec2 = dict(reg.spec); spec2["input_addresses"] = ("utterance", "ground", "exemplars", "inventory")
    reg_v = Role(id=reg.id, spec=spec2, prompt_template=reg.prompt_template, output_schema=reg.output_schema,
                 mode_scope=reg.mode_scope, draws=reg.draws, op=reg.op)
    exemplars, inventory, fids = _grounding_payload(EXEMPLAR_KEYS)
    rc_fids = fids
    cands = json.load(open("design/_system/candidates.json", encoding="utf-8"))["candidates"]
    rec = json.load(open(REC, encoding="utf-8"))
    arts: dict = {}

    def element_of(e):
        mockup = (e.get("sources") or [None])[0]
        if not mockup:
            return None, None
        if mockup not in arts:
            fp = os.path.join(ART_DIR, f"rg10-batch-{mockup.replace('.html', '')}.json")
            arts[mockup] = json.load(open(fp, encoding="utf-8")) if os.path.exists(fp) else None
        art = arts[mockup]
        if not art:
            return None, None
        src = next((x for g in ("confirmed", "flagged") for x in art[g]
                    if x["dossier"].get("address") == e["address"]), None)
        members = (src or {}).get("cluster_members") or []
        sel = [c for c in cands if c.get("mockup_file") == mockup]
        rep = members[0] if members else None
        unit = _unit_of(sel[rep]) if isinstance(rep, int) and rep < len(sel) else None
        return unit, json.dumps((art or {}).get("ground") or {})

    todo = [e for e in rec["entries"] if e["class"] == "panel" and not e.get("redescribed")]
    conf_seat = rr.get("confirm_registration")
    fit_seat = rr.get("element_fit_lens")
    t0, fixed, stayed, failed = time.time(), 0, 0, []
    for e in todo:
        if time.time() - t0 > time_budget_s:
            break
        unit, ground = element_of(e)
        if unit is None:
            e["redescribed"] = "element-unrebuildable"
            failed.append(e["address"])
            continue
        dissents = "\n".join(f"  - {x['seat']}: {x.get('reason','')}"
                             for x in e["panel"]["seats"] if not x["grounded"])
        correction = (f"\nCORRECTION (a previous description FAILED review — fix EXACTLY these):\n{dissents}\n"
                      f"Describe ONLY what the element actually shows. Do not invent interactions the "
                      f"element does not depict. Plain prose in what/what_you_can_do.")
        try:
            res = C.run_items(reg_v, [unit + correction], s.store, turn_id=f"redesc-{e['address'][-14:]}",
                              ctx={"ground": ground, "exemplars": exemplars, "inventory": inventory},
                              max_tokens=400)
            new_d = (res.resolved or {}).get(0)
            if not isinstance(new_d, dict):
                raise RuntimeError(f"no output: {str(res.failed)[:120]}")
            rc = refcheck.check_dossier(new_d, feature_ids=rc_fids)
            pc = check_prose(new_d)
            seats = []
            for seat_role, needs_el in ((conf_seat, True), (fit_seat, True)):
                out = C.run_role(seat_role, {"utterance": json.dumps(new_d), "element": unit},
                                 store=s.store, max_tokens=200)
                seats.append({"seat": seat_role.id, "grounded": bool(out.get("grounded")),
                              "reason": out.get("reason", "")})
            seats.append({"seat": "prose_floor (deterministic)", "grounded": pc["passed"],
                          "reason": "clean" if pc["passed"] else str(pc["hits"][:2])})
            ok = rc.get("passed") and pc["passed"] and sum(1 for x in seats if x["grounded"]) >= 2
            e["prior_dossier"], e["dossier"] = e.get("prior_dossier", e["dossier"]), new_d
            e["redescribed"] = True
            e["panel"] = {"verdict": bool(ok), "seats": seats, "quorum": 2,
                          "grounded_seats": sum(1 for x in seats if x["grounded"]),
                          "refloor": rc.get("passed")}
            if ok:
                e["class"] = "confirmed"; fixed += 1
            else:
                stayed += 1
        except Exception as ex:
            e["redescribed"] = f"error: {type(ex).__name__}: {ex}"[:160]
            failed.append(e["address"])
        if (fixed + stayed) % 10 == 0:
            json.dump(rec, open(REC, "w"), indent=1)
    counts = {}
    for e in rec["entries"]:
        counts[e["class"]] = counts.get(e["class"], 0) + 1
    rec["counts"] = counts
    json.dump(rec, open(REC, "w"), indent=1)
    return {"fixed": fixed, "stayed_flagged": stayed, "failed": failed,
            "remaining": sum(1 for e in rec["entries"] if e["class"] == "panel" and not e.get("redescribed")),
            "counts": counts}


if __name__ == "__main__":
    print(json.dumps(run_batch(int(sys.argv[1]) if len(sys.argv) > 1 else 1800), indent=1, default=str))
