#!/usr/bin/env python3
"""rg10_surface.py — RG8: surface the FULL RG10 run as ONE aggregate review item at the operator's
APPROVE gate. Runs only when every mockup is done (or left LOUD in state.failed after MAX_ATTEMPTS —
those ride the payload as needs-attention, never silently dropped).

The card is built for SCANNING (render-for-the-operator): totals → per-mockup counts → each mockup's
compact confirmed rows (address ← feature, grounding) → the artifact path carrying the FULL dossiers
(howto prose, flagged set, jury reasons). Approving is what authorizes RG9's write-back — nothing here
writes addresses.json or the mockups (THE FLOOR: this surfaces, only the operator approves).

Duplicate-guarded: an unresolved full-run registry_proposal_batch already in the inbox → refuses
(fail-loud message, no second card).
"""
import json
import os
import sys

os.chdir("/home/tim/company")
sys.path.insert(0, "/home/tim/company")
STATE = ".build/rg10/state.json"
ART_DIR = "build-prep/cognition-self-improvement"


def main() -> dict:
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore

    state = json.load(open(STATE, encoding="utf-8"))
    cands = json.load(open("design/_system/candidates.json", encoding="utf-8"))["candidates"]
    mockups = sorted({c["mockup_file"] for c in cands})
    not_done = [m for m in mockups if m not in state["done"] and m not in state.get("failed", {})]
    if not_done:
        raise RuntimeError(f"RG10 is not finished — {len(not_done)} mockups neither done nor failed-loud "
                           f"(e.g. {not_done[:3]}). Run rg10_run.py to completion first. Fail loud.")

    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    # duplicate guard — one live full-run card, never two (inbox.list is the real listing API)
    for it in s.inbox.list():
        p = it.get("payload") or {}
        if (p.get("kind") == "registry_proposal_batch" and p.get("scope") == "full-run"
                and it.get("resolved") is None):
            raise RuntimeError(f"an unresolved full-run RG10 card already exists ({it.get('id')}) — "
                               f"refusing a duplicate (fail loud).")

    per_mockup, confirmed_rows, total_ok, total_flag = [], {}, 0, 0
    for m in mockups:
        if m not in state["done"]:
            continue
        v = state["done"][m]
        stem = m.replace(".html", "")
        art = os.path.join(ART_DIR, f"rg10-batch-{stem}.json")
        per_mockup.append({"mockup": m, "candidates": v["candidates"], "clusters": v["clusters"],
                           "confirmed": v["confirmed"], "flagged": v["flagged"], "artifact": art})
        total_ok += v["confirmed"]; total_flag += v["flagged"]
        d = json.load(open(art, encoding="utf-8"))
        confirmed_rows[m] = [{"address": e["dossier"].get("address"),
                              "maps_to_feature": e["dossier"].get("maps_to_feature"),
                              "grounding": e["dossier"].get("grounding")}
                             for e in d.get("confirmed", [])]

    item = {
        "title": f"RG10 full run — {total_ok} confirmed registry dossiers across {len(per_mockup)} mockups "
                 f"await your APPROVE ({total_flag} flagged for scrutiny, never dropped)",
        "kind": "registry_proposal_batch",
        "scope": "full-run",
        "summary": (
            f"The registry-generation chain (GROUND → MAP → cluster-dedup → jury+refcheck CONFIRM) ran over "
            f"every design mockup: {sum(p['candidates'] for p in per_mockup)} candidate elements → "
            f"{sum(p['clusters'] for p in per_mockup)} unique → {total_ok} CONFIRMED (grounded + the "
            f"deterministic no-fiction floor passed) and {total_flag} FLAGGED for your scrutiny. Approving "
            f"authorizes the write-back (RG9) that grows the address registry — every confirmed mockup "
            f"element then explains itself at your altitude, like the 82 existing entries. Each mockup's "
            f"artifact carries the full dossiers (the plain-language what/can-do/how-to-change prose) and "
            f"the flagged set with the jury's reasons."),
        "per_mockup": per_mockup,
        "confirmed_total": total_ok,
        "flagged_total": total_flag,
        "confirmed_by_mockup": confirmed_rows,
        "failed_loud": state.get("failed", {}),
    }
    out = s.surface_review(item, origin="responsive")
    return {"surfaced": out, "confirmed_total": total_ok, "flagged_total": total_flag,
            "mockups": len(per_mockup), "failed_loud": list(state.get("failed", {}))}


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
