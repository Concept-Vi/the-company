#!/usr/bin/env python3
"""g13_cluster.py — ③/G13: the FAILURE-PATTERN CLUSTER over the FULL mined history corpus — the
mining program's payoff. Deterministic tally → embed the DISTINCT pattern_tags (the resident
embed-bge, the canonical fabric seam) → greedy cosine cluster → named pattern groups weighted by
how often they recur — the system's first complete self-study of how-I-work-with-Tim.

Output: .build/g13/clusters.json (the data) — the REPORT (G13-PATTERN-REPORT.md) is written by the
lead from this data (the memory cross-reference is judgment work, not script work).
THE FLOOR: read + embed + cluster — proposes/reports only."""
import json
import math
import os
import sys
from collections import Counter

os.chdir("/home/tim/company")
sys.path.insert(0, "/home/tim/company")
OUT = ".build/g13/clusters.json"
THRESHOLD = 0.78          # short kebab tags — spot-checked below; conservative (under-merge > over-merge)


def cos(a, b):
    d = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(x * x for x in b))
    return d / (na * nb) if na and nb else 0.0


def main() -> dict:
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    from fabric import client, transport
    from fabric.config import DEFAULT_EMBED_MODEL

    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    recs = s.find_corpus(projection="history")
    tags, fields = Counter(), Counter()
    examples: dict = {}
    for r in recs:
        out = (s.store.get_content(r["cas"]) or {}).get("output") or {}
        t = (out.get("pattern_tag") or "").strip().lower()
        if t:
            tags[t] += 1
            if t not in examples and (out.get("tim_correction") or out.get("my_error")):
                examples[t] = {"src": r.get("source_address"),
                               "correction": out.get("tim_correction", "")[:160],
                               "error": out.get("my_error", "")[:160]}
        for f in ("tim_correction", "my_error", "frustration", "bug_fix", "needs_tim"):
            if out.get(f):
                fields[f] += 1

    distinct = list(tags)
    t = transport.openai_embeddings_transport()
    vecs = client.complete_embeddings(t, distinct, model=DEFAULT_EMBED_MODEL)
    by_tag = dict(zip(distinct, vecs))

    # greedy weight-ordered clustering: heaviest tag seeds a cluster; others join at >= THRESHOLD
    order = [tg for tg, _n in tags.most_common()]
    clusters: list = []
    for tg in order:
        v = by_tag[tg]
        placed = False
        for c in clusters:
            if cos(v, c["seed_vec"]) >= THRESHOLD:
                c["members"].append(tg); c["weight"] += tags[tg]
                placed = True
                break
        if not placed:
            clusters.append({"name": tg, "seed_vec": v, "members": [tg], "weight": tags[tg]})
    for c in clusters:
        del c["seed_vec"]
        c["example"] = next((examples[m] for m in c["members"] if m in examples), None)
    clusters.sort(key=lambda c: -c["weight"])

    out = {"extracts": len(recs), "tagged": sum(tags.values()), "distinct_tags": len(distinct),
           "clusters": len(clusters), "threshold": THRESHOLD,
           "signal_fields": dict(fields),
           "top": clusters[:30]}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1)
    return {k: out[k] for k in ("extracts", "tagged", "distinct_tags", "clusters", "signal_fields")} | \
           {"top10": [{"name": c["name"], "weight": c["weight"], "n_tags": len(c["members"])}
                      for c in clusters[:10]]}


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
