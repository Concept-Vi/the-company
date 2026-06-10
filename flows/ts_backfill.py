"""flows/ts_backfill.py — the TIME-FACET BACKFILL (forager C2): deterministically re-stamp
ts_source onto history records that lack it.

The forager research found only 173/1,420 history records carry ts_source (the source exchange's
ORIGINAL timestamp) — capture-ts can't partition by period (the whole corpus was captured in two
days). The fix is PURE DETERMINISM (no model): re-walk each transcript with the SAME
extract_exchanges the miner used, look up each existing exchange://<sid>/<i> record, and re-capture
it with ts_source added (append-only; latest-seq-wins supersedes — nothing is lost, nothing is
re-mined). Embeds ride the normal capture path (the local embedder, not API quota)."""
import json
import os
import sys

FLOW = {
    "id": "ts_backfill",
    "label": "Backfill ts_source onto history records (the forager's time facet)",
    "description": (
        "Deterministically re-stamps the ORIGINAL exchange timestamp onto history records that lack "
        "it: re-walks each transcript with the miner's own extract_exchanges, matches existing "
        "exchange:// records, re-captures them with ts_source added (latest-seq-wins supersession — "
        "no re-mining, no model). Idempotent: records already carrying ts_source are skipped."),
    "params": {
        "budget": {"desc": "max records to re-stamp this run (bounded batches compose)", "default": 600},
    },
    # proposes_only is the FLOOR contract (no resolve/approve/dispatch) — corpus capture is a
    # declarative data write, the same class as transcript_mine's captures. True is honest.
    "proposes_only": True,
}


def run(budget: int = 600) -> dict:
    sys.path.insert(0, "/home/tim/company")
    sys.path.insert(0, "/home/tim/company/build-prep/cognition-self-improvement")
    os.chdir("/home/tim/company")
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    from transcript_extract import extract_exchanges

    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    rows = [r for r in s.list_corpus(project="company")
            if (r.get("source_address") or "").startswith("exchange://")]
    # newest-seq-wins per address; collect the ones MISSING ts_source
    latest: dict = {}
    for r in rows:
        sa = r["source_address"]
        if sa not in latest or (r.get("seq") or 0) > (latest[sa].get("seq") or 0):
            latest[sa] = r
    missing = {}
    for sa, r in latest.items():
        content = (s.store.get_content(r["cas"]) or {}).get("output") or {}
        if content and not content.get("ts_source"):
            missing[sa] = content
    if not missing:
        return {"restamped": 0, "note": "nothing missing — backfill complete"}

    # group by session id → one transcript walk each (deterministic source of truth)
    by_sid: dict = {}
    for sa in missing:
        sid, idx = sa[len("exchange://"):].rsplit("/", 1)
        by_sid.setdefault(sid, []).append((int(idx), sa))
    tdir = "/home/tim/.claude/projects/-home-tim"
    restamped, no_file, no_idx = 0, [], 0
    for sid, items in sorted(by_sid.items()):
        path = os.path.join(tdir, f"{sid}.jsonl")
        if not os.path.isfile(path):
            no_file.append(sid)                              # fail-LOUD in the report, never silent
            continue
        ex = extract_exchanges(path)
        recs = []
        for idx, sa in sorted(items):
            if idx >= len(ex) or not ex[idx].get("ts"):
                no_idx += 1
                continue
            recs.append({"source_address": sa,
                         "output": dict(missing[sa], ts_source=ex[idx]["ts"]),
                         "projection": "history"})
            if restamped + len(recs) >= budget:
                break
        if recs:
            s.capture_corpus(recs, project="company", session="ts-backfill", round="1")
            restamped += len(recs)
        if restamped >= budget:
            break
    return {"restamped": restamped, "still_missing": len(missing) - restamped,
            "transcripts_gone": no_file[:5], "unmatched_indices": no_idx,
            "note": "re-run to continue (bounded batches compose; idempotent)"}
