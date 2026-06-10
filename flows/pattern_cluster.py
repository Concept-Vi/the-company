"""flows/pattern_cluster.py — the ③/G13 failure-pattern cluster as a registered flow row. ONE call
re-runs the self-study REDUCE over the FULL mined history space: deterministic tally of pattern_tags →
embed the distinct tags (the resident embedder) → conservative greedy cluster → named, weighted
pattern groups with their attached real corrections. Writes .build/g13/clusters.json; the canonical
report (G13-PATTERN-REPORT.md) is the lead's judgment layer over this data. PROPOSES data only."""
import sys

FLOW = {
    "id": "pattern_cluster",
    "label": "Failure-pattern cluster (the self-study REDUCE over mined history)",
    "description": (
        "Clusters every mined exchange-extract's pattern_tag across the full history space into named, "
        "weighted groups (embedder + conservative threshold), each carrying a real example correction. "
        "Re-run after new mining batches to refresh the self-study data; the report file updates in "
        "place from it. Read+compute only."),
    "params": {},
    "proposes_only": True,
}


def run() -> dict:
    sys.path.insert(0, "/home/tim/company/build-prep/cognition-self-improvement")
    from g13_cluster import main
    return main()
