#!/usr/bin/env python3
"""archaeology_mine.py — the MEMORY-ARCHAEOLOGY sweep driver (sibling of g23_mine.py, 2026-07-07).

Fans `mine_design_intent` (kimi-bound — the measured A/B: build-prep/memory-archaeology/
KIMI-VS-4B-MINE-SAMPLE.md) over a CURATED session list — the transcripts that designed the memory
systems (recall / reranker / recollection / embedder), ranked by mention-density in the design window
(scratchpad design-window-rank, 2026-07-07). Captures into projection='design_intent' (the archaeology
lens created the same day) keyed exchange://<sid>/<i> — SEPARATE from 'history' (mine_exchange's
self-improvement lens) so neither supersedes the other at the same addresses.

Differences from g23_mine (deliberate):
  * CURATED list, not richest-first discovery — this sweep is Tim's "kinda B": the memory-system
    design sessions first, for the agent's own deep understanding.
  * projection='design_intent', records carry design_weight for later filtering; connects_to are
    CANDIDATE-mentions (the A/B caveat: kimi decorates names with schemes — the cross-link pass
    must normalize + verify against the real code:// space before writing links).
  * model comes from the ROLE's declared binding via suite.resolve_role (the same resolution the
    MCP face now applies — the 2026-07-07 declared-binding fix), never a constant here.
  * max_tokens 900 (list-valued output — the 300 of the one-decision schema truncates it).

Idempotent at exchange granularity (the skip-list IS the corpus — find_corpus(projection=
'design_intent')); bounded by time budget + per-file cap; per-file failures recorded loud.
Run:  .venv/bin/python build-prep/memory-archaeology/archaeology_mine.py [budget_s] [max_new_per_file]
"""
import json
import os
import sys
import time

REPO = "/home/tim/company"
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "build-prep/cognition-self-improvement"))

STATE_DIR = os.path.join(REPO, "build-prep/memory-archaeology/.state")
STATE = os.path.join(STATE_DIR, "archaeology_mine.json")
ACTIVE_S = 3600          # 1h mtime ripening guard (a session being written right now is skipped)
MAX_TOKENS = None        # NO output budget — kimi is cloud (Tim 2026-07-08: no cloud budgets); a
#                          full-intent extract over a now-UNTRUNCATED exchange runs to completion.
MINE_VERSION = 2         # bumped 1→2 (2026-07-08): v1 mined TRUNCATED exchanges (extractor caps, now
#                          removed at source). The skip-list only skips records at the CURRENT version,
#                          so a bump RE-MINES every exchange on full text → supersedes the v1 records
#                          (latest-seq capture). Idempotent again thereafter.

# The CURATED sweep list (2026-07-07): the memory-system design sessions, mention-density ranked
# (design-window scan) + the two known design-rich corpus-era sessions. Order = mining order.
SESSIONS = [
    # sid, project-dir, why
    ("970bc7c0-53a6-4385-8d28-ee02848debdf", "-home-tim", "7764 hits/48MB — densest memory-system talk"),
    ("11e7d395-8bb9-463f-bcb3-06616da49ebb", "-home-tim", "1896 hits/71MB"),
    ("c9f6db2d-f432-4de8-8eea-14da5a511935", "-home-tim", "881 hits/29MB"),
    ("7a97439e-88f9-435a-a968-34f4043f72f5", "-home-tim-company", "853 hits/27MB — company-project side"),
    ("d5fc8ad1-1cab-461a-ab26-84ccda9ed11d", "-home-tim", "720 hits/13MB"),
    ("babe1fa7-ed90-42ce-b019-daf2601a4aa2", "-home-tim", "569 hits/22MB"),
    ("104a58a7-eaea-46fd-a187-9066d2dd7401", "-home-tim", "the address-system design session (A/B sample source)"),
    # the giants last (per-file cap still bounds them; they deepen batch over batch):
    ("bda8ce28-6dfb-4a76-b13a-bc016b8574ca", "-home-tim", "6829 hits/192MB"),
    ("aa38004f-5fd6-4c24-8463-f2953368ec0c", "-home-tim", "1726 hits/144MB"),
    ("cb334081-be01-4136-b81b-a8d93796089f", "-home-tim", "2110 hits/204MB"),
    ("f609942f-fc17-47f5-a739-966343e5a54c", "-home-tim", "4608 hits/404MB"),
]
TDIRS = "/home/tim/.claude/projects/{proj}/{sid}.jsonl"


def _load(path, default):
    try:
        return json.load(open(path))
    except (OSError, json.JSONDecodeError):
        return default


def run_batch(time_budget_s: int = 600, max_new_per_file: int = 30) -> dict:
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    from runtime import cognition as C
    from transcript_extract import extract_exchanges

    os.makedirs(STATE_DIR, exist_ok=True)
    state = _load(STATE, {"round": 0, "failed": {}})
    s = Suite(FsStore(os.path.join(REPO, ".data/store")), NodeRegistry().discover([os.path.join(REPO, "nodes")]),
              nodes_dir=os.path.join(REPO, "nodes"))
    role = s.role_registry["mine_design_intent"]
    # the ROLE's declared binding, resolved the one canonical way (config > env > declared > brain):
    binding = s.resolve_role("mine_design_intent")
    model, base_url = binding["model"], binding["base_url"]

    # skip-list IS the corpus, per exchange (substrate-is-truth; mirrors g23) — BUT version-gated:
    # only a record mined at the CURRENT MINE_VERSION counts as done, so a version bump re-mines
    # everything on full (now-untruncated) text and supersedes the old records. Reads CAS for the
    # version stamp (a few hundred records — cheap; fail-open so a stray shape never blocks re-mine).
    mined_idx: dict = {}
    for r in s.find_corpus(projection="design_intent"):
        sa = r.get("source_address") or ""
        if not sa.startswith("exchange://"):
            continue
        try:
            rec = s.store.get_content(r["cas"])
            if (rec.get("output") or {}).get("mine_version") != MINE_VERSION:
                continue                                    # older version → NOT done → re-mine
            sid_, _, idx_ = sa.split("://")[1].partition("/")
            mined_idx.setdefault(sid_, set()).add(int(idx_))
        except (ValueError, KeyError, AttributeError):
            pass

    state["round"] += 1
    rnd = f"arch-{state['round']}"
    now, t0, done = time.time(), time.time(), []
    for sid, proj, why in SESSIONS:
        if time.time() - t0 > time_budget_s:
            break
        path = TDIRS.format(proj=proj, sid=sid)
        if not os.path.exists(path):
            state["failed"][sid] = {"error": "transcript missing", "attempts": 99}
            continue
        if now - os.stat(path).st_mtime < ACTIVE_S:
            continue                                        # being written right now — next batch
        exchanges = extract_exchanges(path)             # LOSSLESS, ALL exchanges (no cap — resume bounds the batch)
        have = mined_idx.get(sid, set())
        new = [(i, e) for i, e in enumerate(exchanges) if i not in have][:max_new_per_file]
        if not new:
            continue
        units = [{"session_id": e["session"], "ts": e["ts"],
                  "tim_message": e["tim"], "my_response": e["reply"]} for _i, e in new]
        try:
            res = C.run_items(role, units, s.store, turn_id=f"{rnd}-{sid[:8]}",
                              model=model, base_url=base_url, max_tokens=MAX_TOKENS)
        except Exception as e:
            prior = state["failed"].get(sid, {"attempts": 0})
            state["failed"][sid] = {"attempts": prior["attempts"] + 1,
                                    "error": f"{type(e).__name__}: {e}"[:300]}
            json.dump(state, open(STATE, "w"), indent=1)
            continue
        resolved = res.resolved if isinstance(res.resolved, dict) else {}
        if not resolved:
            prior = state["failed"].get(sid, {"attempts": 0})
            state["failed"][sid] = {"attempts": prior["attempts"] + 1,
                                    "error": f"0/{len(units)} extracts — failed: {str(res.failed)[:200]}"}
            json.dump(state, open(STATE, "w"), indent=1)
            continue
        records = [{"source_address": f"exchange://{sid}/{new[j][0]}",
                    "output": dict(out, ts_source=new[j][1].get("ts"), mine_version=MINE_VERSION),
                    "projection": "design_intent"}
                   for j, out in sorted(resolved.items()) if isinstance(out, dict)]
        cap = s.capture_corpus(records, project="company", session="archaeology-mine", round=rnd)
        state["failed"].pop(sid, None)
        json.dump(state, open(STATE, "w"), indent=1)
        weights = [r["output"].get("design_weight") for r in records]
        done.append({"session": sid[:8], "why": why, "new_units": len(units),
                     "captured": cap["n_records"],
                     "substantial": weights.count("substantial"), "light": weights.count("light"),
                     "none": weights.count("none"),
                     "remaining_in_file": max(0, len(exchanges) - len(have) - len(new)),
                     "unit_failures": len(getattr(res, "failed", []) or [])})
    total = len(s.find_corpus(projection="design_intent"))
    out = {"round": rnd, "model": model, "mined_this_batch": done,
           "failed": state["failed"], "design_intent_total": total}
    json.dump(state, open(STATE, "w"), indent=1)
    return out


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    per_file = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    print(json.dumps(run_batch(budget, per_file), indent=1, default=str))
