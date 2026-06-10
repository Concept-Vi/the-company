#!/usr/bin/env python3
"""g23_mine.py — G23 rolling batches: the ③ transcript-miner at full scale, as a PERSISTENT incremental
driver (mirrors rg10_run.py's shape — bounded batches compose toward all ~465 transcripts).

Per transcript: extract_exchanges (deterministic, transcript_extract.py — no model) → run_items
(mine_exchange × N exchange-units, the resident 4B) → capture_corpus(projection='history') — persisted
+ embedded-on-write into space='history' (⑨ durable memory on the CORPUS, not episodic-memory).

INCREMENTAL BY SOURCE-SESSION: the skip-list is read from the corpus itself (find_corpus(projection=
'history') → source_address 'exchange://<sid>/<i>'), never a parallel state file — the substrate is the
truth. .build/g23/state.json carries only the round counter + loud per-file failures.

ORDERING: richest-first (size desc within the 30KB–20MB band — the batch-1 lesson: smallest-first mined
thin sessions). ACTIVE sessions (mtime < 1h) are skipped this pass (a partial file would mint a partial
mining for its sid and the skip-list would then never revisit it) — they ripen for a later batch.

FAIL-LOUD: res.failed per file is recorded in state (never swallowed); a file whose fan ALL-fails is a
recorded failure, not a mined session. THE FLOOR: extraction + run:// computation + corpus writes only —
no resolve/approve/dispatch, no claude -p.
"""
import json
import os
import sys
import time

os.chdir("/home/tim/company")
sys.path.insert(0, "/home/tim/company")
sys.path.insert(0, "/home/tim/company/build-prep/cognition-self-improvement")
TDIR = "/home/tim/.claude/projects/-home-tim"
STATE_DIR = ".build/g23"
STATE = os.path.join(STATE_DIR, "state.json")
ACTIVE_S = 3600                 # mtime younger than this = an active session; ripens for a later batch
MIN_EXCHANGES = 3               # fewer = no dialogue worth mining
MAX_NEW_PER_FILE = 60           # model-work bound per file per batch; deep files deepen across batches


def _load(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return default


def run_batch(time_budget_s: int = 420, max_files: int = 25,
              min_kb: int = 30, max_mb: int = 20) -> dict:
    """The size band is parameterised: the default 30KB–20MB band covers the bulk; the >20MB tail
    (the long foundational sessions — found to be 6 files, likely the richest dialogue) is mined by
    an explicit max_mb raise. The per-file 40-exchange cap bounds the model work either way; the
    1h-mtime ripening guard still excludes a session being written right now."""
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    from runtime import cognition as C
    from transcript_extract import extract_exchanges

    os.makedirs(STATE_DIR, exist_ok=True)
    state = _load(STATE, {"round": 2, "failed": {}, "skipped_thin": []})
    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    mine_role = s.role_registry["mine_exchange"]

    # the skip-list IS the corpus, PER EXCHANGE (substrate-is-truth, no parallel mined-list file).
    # exchange://<sid>/<i> record addresses make the driver idempotent at exchange granularity — a
    # session truncated by an earlier per-file cap DEEPENS on later batches (its unmined tail is
    # mined), instead of being stranded behind a session-level skip (the batch-6 lesson: all three
    # foundational sessions hit the 40-cap with hundreds of exchanges beyond it).
    mined_idx: dict = {}
    for r in s.find_corpus(projection="history"):
        sa = r.get("source_address") or ""
        if sa.startswith("exchange://"):
            sid_, _, idx_ = sa.split("://")[1].partition("/")
            try:
                mined_idx.setdefault(sid_, set()).add(int(idx_))
            except ValueError:
                pass                                        # a non-positional historical address — ignore

    # richest-first candidates in the band; active + known-thin + failed-twice skipped
    now = time.time()
    rows = []
    for fn in os.listdir(TDIR):
        if not fn.endswith(".jsonl"):
            continue
        sid = fn[:-6]
        p = os.path.join(TDIR, fn)
        st = os.stat(p)
        if (sid in state["skipped_thin"] or st.st_size < min_kb * 1024
                or st.st_size > max_mb * 1024 * 1024 or now - st.st_mtime < ACTIVE_S
                or state["failed"].get(sid, {}).get("attempts", 0) >= 2):
            continue
        rows.append((st.st_size, p, sid))
    rows.sort(reverse=True)

    state["round"] += 1
    rnd = f"batch-{state['round']}"
    t0, done = time.time(), []
    fully_mined = 0
    for _sz, path, sid in rows[:max_files]:
        if time.time() - t0 > time_budget_s:
            break
        # extraction is deterministic + file-order-stable, so index i is a durable per-exchange key for
        # a SETTLED file (the 1h ripening guard keeps still-growing files out). Extract DEEP (cap 500 —
        # parse is cheap); bound the MODEL work by mining at most MAX_NEW_PER_FILE new units per batch.
        exchanges = extract_exchanges(path, max_exchanges=500)
        if len(exchanges) < MIN_EXCHANGES:
            state["skipped_thin"].append(sid)               # recorded, never re-walked
            json.dump(state, open(STATE, "w"), indent=1)
            continue
        have = mined_idx.get(sid, set())
        new = [(i, e) for i, e in enumerate(exchanges) if i not in have][:MAX_NEW_PER_FILE]
        if not new:
            fully_mined += 1                                # complete — nothing stranded, nothing to do
            continue
        units = [{"session_id": e["session"], "ts": e["ts"],
                  "tim_message": e["tim"], "my_response": e["reply"]} for _i, e in new]
        try:
            res = C.run_items(mine_role, units, s.store, turn_id=f"g23-{sid[:8]}-r{state['round']}",
                              max_tokens=300)
        except Exception as e:
            prior = state["failed"].get(sid, {"attempts": 0})
            state["failed"][sid] = {"attempts": prior["attempts"] + 1, "error": f"{type(e).__name__}: {e}"[:300]}
            json.dump(state, open(STATE, "w"), indent=1)
            continue
        resolved = res.resolved if isinstance(res.resolved, dict) else {}
        if not resolved:                                     # ALL units failed — loud, never marked mined
            prior = state["failed"].get(sid, {"attempts": 0})
            state["failed"][sid] = {"attempts": prior["attempts"] + 1,
                                    "error": f"0/{len(units)} extracts — failed: {str(res.failed)[:200]}"}
            json.dump(state, open(STATE, "w"), indent=1)
            continue
        # records carry the ORIGINAL exchange index (new[j][0]), not the unit position j — the durable key.
        # ts_source = the exchange's ORIGINAL timestamp (the forager's time-period facet; the research
        # found only 173/1420 records carry it — this stops the gap growing; backfill re-stamps the rest).
        records = [{"source_address": f"exchange://{sid}/{new[j][0]}",
                    "output": dict(out, ts_source=new[j][1].get("ts")), "projection": "history"}
                   for j, out in sorted(resolved.items()) if isinstance(out, dict)]
        cap = s.capture_corpus(records, project="company", session="g23-mine", round=rnd)
        state["failed"].pop(sid, None)
        json.dump(state, open(STATE, "w"), indent=1)
        done.append({"session": sid, "new_units": len(units), "captured": cap["n_records"],
                     "deepened": bool(have), "remaining_in_file": max(0, len(exchanges) - len(have) - len(new)),
                     "unit_failures": len(getattr(res, "failed", []) or [])})
    total = len(s.find_corpus(projection="history"))
    return {"round": rnd, "mined_this_batch": done, "failed": state["failed"],
            "history_extracts_total": total, "fully_mined_in_band": fully_mined,
            "candidates_in_band": len(rows)}


if __name__ == "__main__":
    _budget = int(sys.argv[1]) if len(sys.argv) > 1 else 420
    _max_mb = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    print(json.dumps(run_batch(_budget, max_mb=_max_mb), indent=1, default=str))
