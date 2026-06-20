#!/usr/bin/env python3
"""ops/embed_extractions.py — embed the dragnet extraction layer into the 'extractions' vector space (#65).

Makes the extract-once asset SEMANTIC: each extraction's representative text (about + summary + claims) is
embedded into the registered 'extractions' space (projections/extractions.py) via the existing
embed_corpus_to_spaces → build_index path (reuse-don't-parallel; the SAME embed seam the corpus capture uses).
⟹ (a) the grounded determine's candidate-filter becomes SEMANTIC (concept-match, fixes the keyword bluntness);
(b) the extractions fold into corpus(op='query', space='extractions') (one recall surface).

source_address = extraction://<asset>/<chunk_id> (stable, distinct per extraction). Batched + resumable
(skip already-embedded source_addresses). Uses :8007 (the shared embedder) — announce/sequence like the bake.

  python3 ops/embed_extractions.py [--asset full|visual-dna|both] [--sample N] [--batch 500]
"""
from __future__ import annotations
import argparse, json, os, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
EXT_DIR = os.path.join(REPO, ".data", "store", "extractions")


def rep_text(r):
    """The representative text to embed: about + summary + top claims (the extraction's meaning)."""
    parts = [r.get("about", ""), r.get("summary", "")]
    parts += (r.get("claims") or [])[:3]
    parts += (r.get("relations") or [])[:2]
    return ". ".join(p for p in parts if p).strip()[:400]


def build_records(asset):
    path = os.path.join(EXT_DIR, f"extractions-{asset}.jsonl")
    if not os.path.exists(path):
        return []
    recs = []
    for line in open(path):
        try:
            r = json.loads(line)
        except Exception:
            continue
        t = rep_text(r)
        if t and len(t) > 20:
            recs.append({"source_address": f"extraction://{asset}/{r.get('chunk_id')}",
                         "text": t, "projection": "extractions"})
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asset", default="both", help="full | visual-dna | both")
    ap.add_argument("--sample", type=int, default=0, help="embed only N (proof) — does not skip-resume")
    ap.add_argument("--batch", type=int, default=500)
    a = ap.parse_args()
    assets = ["full", "visual-dna"] if a.asset == "both" else [a.asset]
    records = []
    for asset in assets:
        records += build_records(asset)
    print(f"built {len(records)} embed-records from {assets}", flush=True)
    if a.sample:
        records = records[:a.sample]
        print(f"SAMPLE: embedding only {len(records)}", flush=True)

    from store.fs_store import FsStore
    from fabric import config as fcfg
    from runtime import projections as P
    from runtime import cognition as cog
    store = FsStore(fcfg.STORE_DIR)
    proj_set = P.ProjectionRegistry().discover([os.path.join(REPO, "projections")]).embeddable()

    # RESUME: skip source_addresses already embedded in the 'extractions' space (unless --sample)
    if not a.sample:
        try:
            existing = {row.get("id") for row in store.index_corpus(space="extractions", emb="pplx")}
            before = len(records)
            records = [r for r in records if store.space_address(r["source_address"], "extractions") not in existing
                       and r["source_address"] not in existing]
            if before - len(records):
                print(f"RESUME: {before - len(records)} already embedded → skipping", flush=True)
        except Exception as e:
            print(f"(resume check skipped: {type(e).__name__})", flush=True)

    t0 = time.time()
    done = 0
    for i in range(0, len(records), a.batch):
        batch = records[i:i + a.batch]
        out = cog.embed_corpus_to_spaces(store, batch, proj_set, emb="pplx")
        done += len(batch)
        deg = out.get("degraded") if isinstance(out, dict) else None
        print(f"  batch {i}-{i+len(batch)}: embedded (degraded={deg}) | {done}/{len(records)} | "
              f"{(time.time()-t0)/60:.1f}min", flush=True)
        if deg:
            print("  ⚠ embedder degraded (:8007 down) — STOP, durable warning emitted; resume when up.", flush=True)
            break
    print(f"\nEMBED COMPLETE: {done} extractions → space 'extractions' ({(time.time()-t0)/60:.1f}min)", flush=True)


if __name__ == "__main__":
    main()
