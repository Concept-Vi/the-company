#!/usr/bin/env python3
"""ops/dragnet_determine.py — thin CLI over runtime.recall_determine (the grounded determine engine).

The determine logic lives in runtime/recall_determine.py (the engine layer — ONE implementation the CLI
AND the MCP face's corpus(op='determine') both call). This is the command-line entry: ask the dragnet
extraction layer a topic → GROUNDED themes of real, chunk-traced claims (no-fiction by construction).

  python3 ops/dragnet_determine.py --topic "structured outputs / allocation / feeding" [--asset full|visual-dna]
"""
from __future__ import annotations
import argparse, json, os, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True, help="natural-language topic to determine")
    ap.add_argument("--asset", default="full", help="extraction asset: full (session history) | visual-dna")
    ap.add_argument("--max-claims", type=int, default=60)
    a = ap.parse_args()
    from runtime import recall_determine as rd
    t = time.time()
    res = rd.determine(a.topic, asset=a.asset, max_claims=a.max_claims)
    print(json.dumps(res, indent=2)[:3000])
    print(f"\nno_fiction={res.get('no_fiction')} | {time.time()-t:.1f}s")


if __name__ == "__main__":
    main()
