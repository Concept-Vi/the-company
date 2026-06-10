"""flows/registry_generation.py — the GROUNDED registry-filling chain (the GC2 pattern's proven
instance), as a registered flow row. ONE call runs bounded per-mockup batches of the FULL chain —
GROUND (screen_reader) → MAP (register_element with the designed context package: exemplars + closed
vocabularies + the mockup ground + parent dossier) → REDUCE (cluster dedup) → CONFIRM (deterministic
refcheck floor + accuracy jury) — resume-safe state in .build/rg10/. PROPOSES per-mockup artifacts;
the reconcile/surface/approve stages stay the operator-gated path. NEVER invents an ungrounded MAP —
that is this row's reason to exist (the GC1 law: the grounded chain is the one easy call)."""
import sys

FLOW = {
    "id": "registry_generation",
    "label": "Registry generation (grounded mockup→dossier chain, bounded batches)",
    "description": (
        "Runs the proven registry-filling production line over the design mockups: each candidate "
        "element is described BY a small model WITH its full grounding package (page summary, parent "
        "entry, real exemplar entries, the closed feature/capability vocabularies), deduped, then "
        "gated by the deterministic no-fiction floor + an accuracy jury. Resume-safe per mockup; "
        "artifacts land in build-prep/cognition-self-improvement/rg10-batch-*.json; the operator's "
        "APPROVE gate stays downstream (this flow only proposes)."),
    "params": {
        "time_budget_s": {"desc": "wall-clock bound for this batch (per-mockup increments compose)",
                          "default": 420},
    },
    "proposes_only": True,
}


def run(time_budget_s: int = 420) -> dict:
    sys.path.insert(0, "/home/tim/company/build-prep/cognition-self-improvement")
    from rg10_run import run_batch
    return run_batch(int(time_budget_s))
