#!/usr/bin/env python3
"""rg10_walk.py — GC6 (backend half): compose the s98 batch into a CLASS-GROUPED TRIAGE WALK —
"triage by condition, never a 463-item list" made real on the EXISTING walkthrough organ
(reuse-don't-parallel: surface_review for the per-class block items + start_session for the
operator-paced gated walk + present_current/coa for the live at-altitude framing — NO new stepper).

THE WALK (one step per DECISION-KIND, not per item):
  stop 1 · confirmed-block  — ONE decision: approve the 190 floor+jury-passed entries as a block
                              (his approve verdict on THIS item is what the RG9 write-back binds to).
  stop 2 · conflicts        — 33 elements different screens describe DIFFERENTLY (all variants in the
                              payload); his choice: walk them one-by-one (compose_conflict_walk — built,
                              fired only on his ask) or decide from the block view.
  stop 3 · inventory-gaps   — the 18 stubborn-floor entries (the model insists on a concept the feature
                              inventory doesn't name); reviewing may grow register.json, not addresses.
  stop 4 · jury-flagged     — the 222 no-quorum entries; the block proposes the GC7 panel re-jury
                              (diverse lenses) to shrink this before any one-by-one effort.

THE FLOOR: composes + surfaces + verifies PRESENTATION only — never resolves (only Tim's verdicts move
anything; the session cursor is left at stop 1 for him). FE/voice drive of the walk = needs-tim."""
import json
import os
import sys

os.chdir("/home/tim/company")
sys.path.insert(0, "/home/tim/company")
REC = ".build/rg10/reconciled.json"
PARENT = "s98-review"


def _suite():
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    return Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")


def _sample(entries, n=4):
    return [{"address": e["address"], "represents": e["dossier"].get("represents"),
             "maps_to_feature": e["dossier"].get("maps_to_feature")}
            for e in entries[:n]]


def compose_triage_walk() -> dict:
    s = _suite()
    rec = json.load(open(REC, encoding="utf-8"))
    # the REFINED classes (post-cascade, 2026-06-10: jury → panel → calibrated panel → deterministic
    # prose floor → re-describe; the standing refine-before-gating rule — Tim's gate gets the minimum)
    by_cls = {k: [e for e in rec["entries"] if e["class"] == k]
              for k in ("confirmed", "conflict", "floor", "panel")}
    # dup guard — one live triage walk's blocks. LIVE = unresolved AND not retired via the status
    # lane ('requeue' is how a superseded card is retired without touching the operator's resolved).
    for it in s.inbox.list():
        p = it.get("payload") or {}
        if (p.get("kind") == "registry_triage_block" and it.get("resolved") is None
                and it.get("status") not in ("requeue", "implemented")):
            raise RuntimeError(f"a live triage block already exists ({it.get('id')}) — fail loud, no duplicate walk.")

    features = [e["proposed_feature"]["row"] for e in by_cls["floor"]
                if (e.get("proposed_feature") or {}).get("status") == "proposed"]
    # one proposed feature can carry several elements (the GC9 merge) — dedupe by id for the block
    feat_by_id = {}
    for r in features:
        feat_by_id.setdefault(r["id"], r)
    blocks = [
        {"block": "confirmed", "title": f"Approve {len(by_cls['confirmed'])} refined registry entries as a block?",
         "decision": ("ONE decision: every entry here passed the deterministic no-fiction floor, the "
                      "deterministic prose check, AND a diverse review panel (grounding + element-fit "
                      "lenses) — many after autonomous correction rounds. Approving writes them into the "
                      "address registry: each element then explains itself at your altitude. Reject sends "
                      "the batch back with your reason."),
         "count": len(by_cls["confirmed"]), "sample": _sample(by_cls["confirmed"]),
         "addresses": [e["address"] for e in by_cls["confirmed"]]},
        {"block": "conflict", "title": f"{len(by_cls['conflict'])} elements your screens DESCRIBE DIFFERENTLY — walk them?",
         "decision": ("Different mockups gave the same element different truths (feature or built-status "
                      "disagree). The disagreement is the signal — these need your eyes one at a time. "
                      "Say the word and they become their own short walk; or decide from this block view."),
         "count": len(by_cls["conflict"]),
         "conflicts": [{"address": e["address"],
                        "variants": [{"mockup": v["mockup"], "maps_to_feature": v["maps_to_feature"],
                                      "grounding": v["grounding"], "represents": v["represents"]}
                                     for v in e.get("variants", [])]} for e in by_cls["conflict"]]},
        {"block": "features", "title": f"{len(feat_by_id)} PROPOSED FEATURES for the inventory (most flesh out the RHM)",
         "decision": ("These elements represent concepts the feature inventory doesn't name — the model "
                      "insisted on them through every correction, and each is now a concrete proposed "
                      "inventory row (name, area, plain-language label; fully derived from existing data — "
                      "nothing invented). Approving grows the feature inventory itself; 8 of these complete "
                      "the right-hand-man area's self-description."),
         "count": len(feat_by_id), "features": list(feat_by_id.values())},
        {"block": "residue", "title": f"{len(by_cls['panel'])} entries the panel still rejects after every refinement — the true residue",
         "decision": ("Every autonomous refinement is exhausted (diverse panel, calibration, deterministic "
                      "prose floor, corrected re-description) — these still fail, each with NAMED reasons "
                      "from the content lenses. Walk them individually, or reject the lot (their elements "
                      "stay candidates for a future pass)."),
         "count": len(by_cls["panel"]),
         "residue": [{"address": e["address"],
                      "dissents": [x.get("reason", "")[:120] for x in (e.get("panel", {}).get("seats") or [])
                                   if not x.get("grounded")]} for e in by_cls["panel"]]},
    ]
    ids = []
    for b in blocks:
        item = {"title": b["title"], "kind": "registry_triage_block", "parent": PARENT,
                "artifact": REC, **{k: v for k, v in b.items() if k != "title"}}
        out = s.surface_review(item, origin="responsive")
        ids.append(out["id"])
    # start_session RETURNS the stop-1 presentation directly (it ends `return self.present_current(...)`)
    pres = s.start_session(ids, mode="walkthrough")
    return {"session": pres.get("session"), "blocks": ids,
            "stop1_presents": bool(pres.get("framing") or pres.get("raw")),
            "stop1_framing_head": (pres.get("framing") or "")[:200],
            "total_stops": pres.get("total")}


def compose_conflict_walk() -> dict:
    """The drill-in Tim can ask for at stop 2: each conflict becomes ONE walk step (one decision each).
    NOT fired by default — his choice at the block; the composer exists so the ask is one call."""
    s = _suite()
    rec = json.load(open(REC, encoding="utf-8"))
    conflicts = [e for e in rec["entries"] if e["class"] == "conflict"]
    ids = []
    for e in conflicts:
        item = {"title": f"Which is true for {e['address']}?",
                "kind": "registry_conflict", "parent": PARENT, "address": e["address"],
                "variants": [{"mockup": v["mockup"], "maps_to_feature": v["maps_to_feature"],
                              "grounding": v["grounding"], "represents": v["represents"]}
                             for v in e.get("variants", [])]}
        ids.append(s.surface_review(item, origin="responsive")["id"])
    pres = s.start_session(ids, mode="walkthrough")
    return {"session": pres.get("session"), "items": len(ids)}


if __name__ == "__main__":
    fn = compose_conflict_walk if (len(sys.argv) > 1 and sys.argv[1] == "conflicts") else compose_triage_walk
    print(json.dumps(fn(), indent=1, default=str))
