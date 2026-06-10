#!/usr/bin/env python3
"""memory_proposals.py — the MINING→PROPOSED-ROW circuit (GC15's grow-half: the ③ pattern-cluster's
consumer). Reads the self-study clusters (.build/g13/clusters.json — weighted correction-patterns
mined from the full conversation record) → checks each strong cluster against the EXISTING
operator-memory rows by meaning (the embedder) → a strong, UNCOVERED pattern becomes a
status='proposed' row that AWAITS TIM'S CONFIRMATION (the lifecycle: mining proposes, Tim confirms;
a proposed row is visible but never standing).

CONSERVATIVE BY DESIGN (a spammed registry is worse than a slow one):
  · only clusters with weight >= MIN_WEIGHT and a REAL example correction qualify (evidence-required
    propagates: no quotable moment, no proposal);
  · a cluster whose meaning is already covered (max cosine vs existing rules >= COVERED_T) is skipped
    (reported — the mining VALIDATING existing memory is the expected, honest dominant outcome);
  · at most MAX_PROPOSALS new rows per run.
THE FLOOR: writes status='proposed' DATA rows only (the same declarative class as the gap intake's
register.json rows); confirmation is Tim's alone."""
import json
import os
import re
import sys

os.chdir("/home/tim/company")
sys.path.insert(0, "/home/tim/company")
MIN_WEIGHT = 8
COVERED_T = 0.62
MAX_PROPOSALS = 3


def main() -> dict:
    from runtime.operator_memory import OperatorMemoryRegistry
    from fabric import client, transport
    from fabric.config import DEFAULT_EMBED_MODEL
    import math

    clusters = json.load(open(".build/g13/clusters.json", encoding="utf-8"))["top"]
    reg = OperatorMemoryRegistry().discover()
    existing = [f"{r['rule']} {r['why']}" for r in reg.rows()]
    existing_ids = set(reg)

    strong = [c for c in clusters if c["weight"] >= MIN_WEIGHT and c.get("example")
              and (c["example"].get("correction") or c["example"].get("error"))]
    if not strong:
        return {"proposed": [], "note": "no strong evidenced clusters above the bar"}

    t = transport.openai_embeddings_transport()
    texts = [f"{c['name']}: {(c['example'] or {}).get('correction', '')}" for c in strong] + existing
    vecs = client.complete_embeddings(t, texts, model=DEFAULT_EMBED_MODEL)
    cvecs, evecs = vecs[:len(strong)], vecs[len(strong):]

    def cos(a, b):
        d = sum(x * y for x, y in zip(a, b))
        return d / (math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(x*x for x in b)) or 1)

    proposed, covered = [], []
    for c, cv in zip(strong, cvecs):
        best = max((cos(cv, ev) for ev in evecs), default=0.0)
        if best >= COVERED_T:
            covered.append({"cluster": c["name"], "weight": c["weight"], "covered_at": round(best, 2)})
            continue
        rid = re.sub(r"[^a-z0-9_]", "_", c["name"].replace("-", "_"))[:40]
        if rid in existing_ids or os.path.exists(f"operator_memory/{rid}.py"):
            continue
        ex = c["example"]
        row = {
            "id": rid,
            "rule": f"(MINED, awaiting Tim's confirmation) recurring pattern '{c['name']}' "
                    f"({c['weight']} occurrences across the record) — draft rule pending his words.",
            "why": f"the mining found this correction-pattern recurring {c['weight']} times with no "
                   f"existing memory row covering it (best similarity {best:.2f}).",
            "evidence": [{"quote": ex.get("correction") or ex.get("error"),
                          "source": ex.get("src", "mined exchange")}],
            "scope": {"when": "proposed — Tim defines the scope at confirmation"},
            "status": "proposed",
        }
        src = ('"""operator_memory/%s.py — MINED proposal (GC15 grow-circuit; awaits Tim\'s '
               'confirmation — not standing)."""\nMEMORY = %r\n' % (rid, row))
        with open(f"operator_memory/{rid}.py", "w", encoding="utf-8") as f:
            f.write(src)
        proposed.append({"id": rid, "cluster": c["name"], "weight": c["weight"], "best_existing_sim": round(best, 2)})
        if len(proposed) >= MAX_PROPOSALS:
            break

    OperatorMemoryRegistry().discover()                      # fail-loud gate: a malformed write refuses here
    return {"proposed": proposed, "covered_validated": covered,
            "note": "covered = the mining VALIDATING existing memory (the expected dominant outcome)"}


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
