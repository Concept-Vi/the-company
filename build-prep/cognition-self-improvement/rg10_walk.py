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
    by_cls = {k: [e for e in rec["entries"] if e["class"] == k]
              for k in ("confirmed", "conflict", "floor", "jury")}
    # dup guard — one live triage walk's blocks (an unresolved block with our marker → refuse)
    for it in s.inbox.list():
        p = it.get("payload") or {}
        if p.get("kind") == "registry_triage_block" and it.get("resolved") is None:
            raise RuntimeError(f"a live triage block already exists ({it.get('id')}) — fail loud, no duplicate walk.")

    blocks = [
        {"block": "confirmed", "title": f"Approve {len(by_cls['confirmed'])} confirmed registry entries as a block?",
         "decision": ("ONE decision: these passed BOTH gates (the deterministic no-fiction floor AND the "
                      "accuracy jury). Approving writes them into the address registry — each element then "
                      "explains itself at your altitude. Reject sends the batch back with your reason."),
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
        {"block": "floor", "title": f"{len(by_cls['floor'])} likely INVENTORY GAPS — concepts the feature list doesn't name",
         "decision": ("The model insists these elements represent features that don't exist in the inventory "
                      "(e.g. NODE-model, RHM-identity) — even after correction. That reads as the INVENTORY "
                      "being incomplete, not the model lying. Reviewing these may grow the feature inventory "
                      "itself; each entry shows the name the model keeps reaching for."),
         "count": len(by_cls["floor"]),
         "gaps": [{"address": e["address"], "insisted_feature": e["dossier"].get("maps_to_feature"),
                   "represents": e["dossier"].get("represents")} for e in by_cls["floor"]]},
        {"block": "jury", "title": f"{len(by_cls['jury'])} entries the accuracy jury couldn't agree on — re-jury with a diverse panel first?",
         "decision": ("The jury today is 3 draws of ONE model — it measures self-consistency, not independent "
                      "judgement, so this pile is mostly variance. Before spending your eyes on 222 items: "
                      "approve a re-jury with DIVERSE panel seats (distinct lenses), which should shrink this "
                      "to a short genuinely-doubtful list. Or walk a sample now to calibrate."),
         "count": len(by_cls["jury"]), "sample": _sample(by_cls["jury"], 6)},
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
