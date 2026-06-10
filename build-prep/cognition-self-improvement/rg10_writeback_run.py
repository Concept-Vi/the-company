#!/usr/bin/env python3
"""rg10_writeback_run.py — RG9: the OPERATOR-APPROVED write-back. Tim approved Decision 1 in
conversation (2026-06-10, verbatim below) — this run records his verdict on s107-review and applies
the 385 confirmed entries through the EXISTING registry_writeback (merge → stamp → re-parse,
all-or-nothing, fail-loud; reuse-don't-parallel).

SAFETY PARTITION first: registry_writeback refuses a WHOLE batch on one curated-content collision —
so entries are pre-partitioned {new, identical(skip), conflicting}; only the safe set is submitted;
conflicting entries are REPORTED for the operator (a proposal to change a curated entry is its own
decision, never folded into a block-approve). Every write is git-committed — one revert undoes it."""
import json
import os
import sys

os.chdir("/home/tim/company")
sys.path.insert(0, "/home/tim/company")
sys.path.insert(0, "/home/tim/company/design/_system")
REC = ".build/rg10/reconciled.json"
ART_DIR = "build-prep/cognition-self-improvement"

TIM_VERDICT = ("approve — Tim, in conversation 2026-06-10: \"yes put them all in, the intent is for "
               "them to be very easy to update and add to anyway... that was a major point of all of "
               "this stuff so that the system would automatically show agents things that it needs\"")


def main() -> dict:
    import registry_writeback as wb
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore

    rec = json.load(open(REC, encoding="utf-8"))
    cands = json.load(open("design/_system/candidates.json", encoding="utf-8"))["candidates"]
    confirmed = [e for e in rec["entries"] if e["class"] == "confirmed"]
    arts: dict = {}

    def candidate_of(e):
        mockup = (e.get("sources") or [None])[0]
        if not mockup:
            return None, None
        if mockup not in arts:
            fp = os.path.join(ART_DIR, f"rg10-batch-{mockup.replace('.html', '')}.json")
            arts[mockup] = json.load(open(fp, encoding="utf-8")) if os.path.exists(fp) else None
        art = arts[mockup]
        src = next((x for g in ("confirmed", "flagged") for x in (art or {}).get(g, [])
                    if x["dossier"].get("address") == e["address"]), None)
        members = (src or {}).get("cluster_members") or []
        sel = [c for c in cands if c.get("mockup_file") == mockup]
        rep = members[0] if members else None
        return (sel[rep] if isinstance(rep, int) and rep < len(sel) else None), mockup

    # build writeback entries (the module CONTRACT shape)
    entries, unbuildable = [], []
    for e in confirmed:
        cand, mockup = candidate_of(e)
        if cand is None:
            unbuildable.append(e["address"])
            continue
        d = e["dossier"]
        entries.append({"address": e["address"], "represents": d.get("represents"),
                        "howto": d.get("howto"), "capabilities": d.get("capabilities"),
                        "maps_to_feature": d.get("maps_to_feature"),
                        "mockup_file": mockup, "outerHTML": cand.get("outerHTML", ""),
                        "run": f"rg10-refined", "model": "chat-4b (floor+prose+panel gated)"})

    # SAFETY PARTITION against the live registry
    registry = json.load(open("design/_system/addresses.json", encoding="utf-8"))["addresses"]
    safe, conflicting, identical = [], [], 0
    for en in entries:
        addr, record = wb._dossier_to_entry(en)
        existing = registry.get(addr)
        if existing is None:
            safe.append(en)
            continue
        cmp_keys = ("region", "represents", "howto", "capabilities", "maps_to_feature")
        if all(existing.get(k) == record.get(k) for k in cmp_keys):
            identical += 1
            safe.append(en)                                  # merge skips it (idempotent) — harmless
        else:
            conflicting.append({"address": addr,
                                "differs_on": [k for k in cmp_keys if existing.get(k) != record.get(k)]})

    report = wb.registry_writeback(safe, write=True, skip_already_stamped=True)
    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    s.inbox.resolve("s107-review", "approve", reason=TIM_VERDICT)

    return {"submitted": len(safe), "added": sum(1 for m in report["merged"] if m["status"] == "added"),
            "skipped_identical": sum(1 for m in report["merged"] if m["status"] == "skipped"),
            "stamped": len(report.get("stamped", [])),
            "curated_conflicts_held": conflicting, "element_unbuildable": unbuildable,
            "registry_total_after": len(report.get("registered_after", [])),
            "verdict_recorded": "s107-review approve"}


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
