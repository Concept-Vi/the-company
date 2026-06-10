#!/usr/bin/env python3
"""rg10_reconcile.py — GC5: the CROSS-MOCKUP reconcile pass (Tim's question-3 finding, 2026-06-10:
the per-mockup runs deduped only WITHIN each mockup — 551 proposals are really 463 distinct addresses;
57 addresses were proposed by up to 6 mockups independently, with possibly-disagreeing fields).

Pure deterministic reconcile (NO model): group the 23 batch artifacts' proposals by address →
  · 1 proposal            → its own class (confirmed | floor | jury)
  · N agreeing proposals  → MERGE to one representative (prefer a confirmed one), sources recorded
  · N DISAGREEING (on maps_to_feature or grounding — the truth-bearing fields) → class 'conflict':
    ALL variants kept for Tim (the disagreement is itself the signal — six screens describing one
    element differently is exactly what his eyes are for)
Classes drive the TRIAGE-BY-CONDITION review (never a 463-item list): confirmed → block-approvable;
floor → the GC4 re-ask's input; jury → needs-eyes; conflict → needs-decision.

Output: .build/rg10/reconciled.json. Then RE-SURFACE: a new aggregate card with the TRUE numbers,
superseding s94/s96 (their status moves to 'requeue' — a STATUS-lane write, never the operator's
resolved field; THE FLOOR: only Tim resolves)."""
import json
import os
import sys
import glob

os.chdir("/home/tim/company")
sys.path.insert(0, "/home/tim/company")
ART_DIR = "build-prep/cognition-self-improvement"
OUT = ".build/rg10/reconciled.json"
SUPERSEDES = ("s94-review", "s96-review")


def classify_one(p: dict) -> str:
    """One proposal's class from its confirm result: confirmed | floor (deterministic fabrication) |
    jury (soft no-quorum only)."""
    if p["confirm"]["confirmed"]:
        return "confirmed"
    reasons = p["confirm"].get("reasons") or []
    if any(r.startswith("refcheck") for r in reasons):
        return "floor"
    return "jury"


def reconcile() -> dict:
    by_addr: dict = {}
    for fp in sorted(glob.glob(os.path.join(ART_DIR, "rg10-batch-*.json"))):
        d = json.load(open(fp, encoding="utf-8"))
        for grp in ("confirmed", "flagged"):
            for e in d[grp]:
                addr = e["dossier"].get("address")
                if not addr:
                    continue
                by_addr.setdefault(addr, []).append(
                    {"mockup": e["mockup"], "dossier": e["dossier"], "confirm": e["confirm"]})

    entries, counts = [], {"confirmed": 0, "floor": 0, "jury": 0, "conflict": 0}
    for addr in sorted(by_addr):
        props = by_addr[addr]
        if len(props) == 1:
            cls = classify_one(props[0])
            entries.append({"address": addr, "class": cls, "dossier": props[0]["dossier"],
                            "confirm": props[0]["confirm"], "sources": [props[0]["mockup"]]})
        else:
            # the truth-bearing fields must AGREE for a silent merge; anything else is Tim's signal
            feats = {p["dossier"].get("maps_to_feature") for p in props}
            grounds = {p["dossier"].get("grounding") for p in props}
            if len(feats) == 1 and len(grounds) == 1:
                rep = next((p for p in props if p["confirm"]["confirmed"]), props[0])
                cls = classify_one(rep)
                entries.append({"address": addr, "class": cls, "dossier": rep["dossier"],
                                "confirm": rep["confirm"],
                                "sources": sorted({p["mockup"] for p in props}),
                                "merged_from": len(props)})
            else:
                counts["conflict"] += 1
                entries.append({"address": addr, "class": "conflict",
                                "variants": [{"mockup": p["mockup"],
                                              "maps_to_feature": p["dossier"].get("maps_to_feature"),
                                              "grounding": p["dossier"].get("grounding"),
                                              "represents": p["dossier"].get("represents"),
                                              "dossier": p["dossier"]} for p in props],
                                "sources": sorted({p["mockup"] for p in props})})
                continue
        counts[entries[-1]["class"]] += 1

    out = {"entries": entries, "counts": counts,
           "raw_proposals": sum(len(v) for v in by_addr.values()),
           "distinct_addresses": len(by_addr)}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1)
    return out


def resurface(rec: dict) -> dict:
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    # dup guard: one live reconciled card
    for it in s.inbox.list():
        p = it.get("payload") or {}
        if p.get("kind") == "registry_proposal_batch" and p.get("scope") == "reconciled" \
                and it.get("resolved") is None:
            raise RuntimeError(f"an unresolved reconciled card already exists ({it.get('id')}) — fail loud.")
    c = rec["counts"]
    item = {
        "title": f"RG10 reconciled — {c['confirmed']} confirmed entries ready for your APPROVE "
                 f"({c['jury']} need your eyes · {c['conflict']} need a decision · {c['floor']} fabrication-caught)",
        "kind": "registry_proposal_batch",
        "scope": "reconciled",
        "supersedes": list(SUPERSEDES),
        "summary": (
            f"The cross-mockup reconcile ran (your question caught it: the first count was inflated — "
            f"{rec['raw_proposals']} raw proposals are {rec['distinct_addresses']} distinct addresses; "
            f"57 elements like the toolbar were proposed by up to 6 screens independently and are now "
            f"merged). TRIAGE BY CONDITION, not by item: "
            f"· {c['confirmed']} CONFIRMED (passed the no-fiction floor + the jury — block-approvable) "
            f"· {c['jury']} the jury couldn't agree match their element (your eyes) "
            f"· {c['conflict']} screens DISAGREE about what the element is (your decision) "
            f"· {c['floor']} caught naming things that don't exist (a re-ask pass can fix most). "
            f"Approving the confirmed block authorizes the write-back that grows the address registry."),
        "counts": c,
        "artifact": OUT,
    }
    surfaced = s.surface_review(item, origin="responsive")
    retired = []
    for sid in SUPERSEDES:
        try:
            s.inbox.set_status(sid, "requeue")    # STATUS lane only — resolved stays untouched (the floor)
            retired.append(sid)
        except (KeyError, ValueError) as e:
            retired.append(f"{sid}: NOT retired ({e})")
    return {"surfaced": surfaced, "retired": retired, "counts": c}


if __name__ == "__main__":
    rec = reconcile()
    print(json.dumps({"counts": rec["counts"], "raw": rec["raw_proposals"],
                      "distinct": rec["distinct_addresses"]}, indent=1))
    print(json.dumps(resurface(rec), indent=1, default=str))
