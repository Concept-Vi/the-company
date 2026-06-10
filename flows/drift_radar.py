"""flows/drift_radar.py — ② the drift-radar as a registered flow row. ONE call sweeps the FULL repo
space for built-twice/overlap (all-pairs cosine → near-clusters → judge_drift confirm → marks,
direction=surface) + doc-vs-code drift candidates (deterministic centroid check). Conservative by
design (the judge's false-positive guard; 'distinct' drops a cluster). PROPOSES marks + findings only
— never auto-fixes. Re-run after repo_ingest refreshes the space."""
import sys

FLOW = {
    "id": "drift_radar",
    "label": "Drift radar (built-twice / overlap / doc-drift sweep over the repo space)",
    "description": (
        "Sweeps the embedded repo corpus for semantic duplication: near-pairs cluster, judge_drift "
        "confirms genuinely-duplicated vs legitimately-distinct (conservative), confirmed clusters "
        "become reviewable marks (built_twice/overlap, surface-direction); AGENTS.md constitutions "
        "far from their module's centroid are flagged as doc-drift candidates. Findings land in "
        ".build/drift/findings.json; DRIFT-RADAR-REPORT.md is the judgment layer. Requires the repo "
        "space to be ingested (run the repo_ingest flow first)."),
    "params": {},
    "proposes_only": True,
}


def run() -> dict:
    sys.path.insert(0, "/home/tim/company/build-prep/cognition-self-improvement")
    from drift_radar import main
    out = main()
    if not out.get("near_pairs") and not out.get("doc_drift_candidates"):
        # zero-is-suspicious (the first sweep's lesson: an empty-set sweep reported clean zeros).
        raise RuntimeError(
            "drift_radar: ZERO near-pairs AND zero doc candidates over the repo space — either the "
            "space is empty/unreadable (run repo_ingest, check vec:// keys) or thresholds are wrong. "
            "A silent 'all clean' is not a believable radar result. Fail loud.")
    return out