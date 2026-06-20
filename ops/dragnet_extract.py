#!/usr/bin/env python3
"""ops/dragnet_extract.py — the full-coverage dragnet's STEPPED extractor (the #65 extract-once asset builder).

Tim's design (2026-06-20/21): "coarse to fine, multi-layered and STEPPED based on EACH OUTPUT" — an ADAPTIVE
stepped cascade, not a blind fine-superset-everywhere:
  STAGE 1 (COARSE, every chunk):  {about, kind, touches}            — cheap, fast, small max_tokens.
  STEP-GATE (from the coarse OUTPUT, at extraction-time → never re-extract, no up-projection):
     kind ∈ {spec, decision, discussion} OR coarse signals claim-bearing  → continue to FINE.
     kind ∈ {log, reference, other} / chatter                              → STOP at coarse.
  STAGE 2 (FINE, gated chunks only): {summary, entities, claims, relations, open_questions} — larger budget.
The stored record is the rich SUPERSET shape (recollection's proven schema, 4207e75); what's STEPPED is the
DEPTH reached per chunk. Down-projection (resolve(grain)→subset) still serves any grain from the one asset.

SOURCE (Tim): the embedded transcript chunks in substrate.db (~/corpora/claude-sessions — the self-referential
history). OUTPUT: .data/store/extractions/ (corpus/recall reads it). FILTERABLE by project (rel_path substrings)
+ date (parsed from the chunk ANCHOR turn-date — NOT mtime, which is the EXPORT date 06-11/06-12, not the
conversation date; flagged finding 2026-06-21).

★ BUDGET (tool-atlas root-cause-2, verified): run_* default max_tokens=256 truncates a RICH extraction →
empty/invalid JSON. This sizes per stage (coarse 220, fine 600) + records finish_reason so truncation is VISIBLE.

GATES before the FULL 35,904-chunk fire (NONE fired by this script's --sample): throughput-measure at
32-concurrent scale (fork+recollection) · max_tokens sized (this script measures it) · Tim's filter list.
Use --sample N to PROVE + MEASURE + SIZE before the bake; the full run is --all (guarded, prints the gate
checklist + requires --confirm).
"""
from __future__ import annotations
import argparse, json, os, re, sqlite3, sys, time
from typing import List
from pydantic import BaseModel

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
SUBSTRATE_DB = os.path.expanduser("~/.cache/company/substrate-claude-sessions/substrate.db")
OUT_DIR = os.path.join(REPO, ".data", "store", "extractions")
_ANCHOR_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")          # turn-N-speaker-YYYY-MM-DD-HHMM → the conversation date


# ── the rich SUPERSET schema (the stored asset shape) — coarse ⊂ fine ──
class Coarse(BaseModel):
    about: str                  # one phrase: what this content IS
    kind: str                   # decision | spec | discussion | digest | log | reference | other
    touches: List[str]          # topic/domain tags

class Fine(BaseModel):
    summary: str                # 1-2 sentence neutral summary
    entities: List[str]         # named things: systems, files, concepts, people
    claims: List[str]           # assertions/decisions stated
    relations: List[str]        # "X depends on Y" / "X supersedes Y"
    open_questions: List[str]   # unresolved threads ([] if none)

_DEEPEN_KINDS = {"decision", "spec", "discussion"}            # the step-gate: these continue to fine


def _coarse_role():
    from runtime.roles import Role
    return Role(id="dragnet_coarse", spec={}, prompt_template=(
        "Read the content and describe it NEUTRALLY (only what it says — do not judge relevance).\n"
        "Content:\n{utterance}\n\n"
        "Return ONLY JSON: {\"about\": \"what this is in one phrase\", "
        "\"kind\": \"decision|spec|discussion|digest|log|reference|other\", "
        "\"touches\": [\"topic tags\"]}"
    ), output_schema=Coarse)


def _fine_role():
    from runtime.roles import Role
    return Role(id="dragnet_fine", spec={}, prompt_template=(
        "Extract a NEUTRAL deep representation of the content (describe only what it says).\n"
        "Content:\n{utterance}\n\n"
        "Return ONLY JSON: {\"summary\": \"1-2 sentence neutral summary\", "
        "\"entities\": [\"named systems/files/concepts/people\"], "
        "\"claims\": [\"assertions or decisions stated\"], "
        "\"relations\": [\"e.g. 'X depends on Y'\"], "
        "\"open_questions\": [\"unresolved threads, [] if none\"]}"
    ), output_schema=Fine)


def load_chunks(*, projects=None, since=None, until=None, limit=None, sample_step=None,
                db=SUBSTRATE_DB, vault=None):
    """Read chunks from a substrate.db (read-only), filtered. `db` = which substrate (claude-sessions OR the
    overlord .state for the visual-dna vault). `vault` = restrict to one substrate vault (e.g. 'visual-dna').
    project = leading-rel_path-segment EXACT match; date = parsed from the chunk ANCHOR (turn date), NOT mtime.
    Returns [{id, text, rel_path, anchor, date}]."""
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    q = ("SELECT ch.id, ch.text, a.rel_path, ch.anchor FROM chunks ch "
         "JOIN addresses a ON a.id = ch.address_id WHERE ch.text IS NOT NULL")
    params = ()
    if vault:
        q += " AND a.vault = ?"
        params = (vault,)
    rows = con.execute(q, params).fetchall()
    con.close()
    out = []
    for cid, text, rel_path, anchor in rows:
        if not text or len(text) < 40:
            continue
        # match the LEADING PATH SEGMENT (the project dir) EXACTLY against the include list — NOT
        # substring-anywhere (which would let "-home-tim" swallow every -home-tim-* dir incl. EXCLUDEs
        # like -home-tim-repos-project-vi / -home-tim-vi-chat). The lead's exact-match-not-substring flag.
        seg = (rel_path or "").split("/")[0]
        if projects and seg not in projects:
            continue
        d = None
        m = _ANCHOR_DATE.search(anchor or "")
        if m:
            d = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        if since and (d is None or d < since):
            continue
        if until and (d is None or d > until):
            continue
        out.append({"id": cid, "text": text[:600], "rel_path": rel_path, "anchor": anchor, "date": d})
    if sample_step and sample_step > 1:
        out = out[::sample_step]
    if limit:
        out = out[:limit]
    return out


def run_extract(chunks, *, store, coarse_max=220, fine_max=600, label="sample"):
    """The STEPPED cascade over `chunks`. Stage1 coarse all → gate → stage2 fine on gated. Returns
    (records, stats). records = the superset shape (coarse always; fine merged when the gate fired)."""
    from runtime import cognition as cog
    t0 = time.time()
    # STAGE 1 — coarse, every chunk
    c_res = cog.run_items(_coarse_role(), [c["text"] for c in chunks], store,
                           turn_id=f"dragnet-coarse-{label}", max_tokens=coarse_max)
    t_coarse = time.time() - t0
    coarse = {}
    for i, v in c_res.resolved.items():
        coarse[i] = v if isinstance(v, dict) else v.dict()
    # STEP-GATE — decide depth FROM the coarse output (extraction-time, forward only)
    gated = [i for i, cv in coarse.items()
             if (cv.get("kind") or "").strip().lower() in _DEEPEN_KINDS]
    # STAGE 2 — fine, gated chunks only
    t1 = time.time()
    fine = {}
    if gated:
        f_res = cog.run_items(_fine_role(), [chunks[i]["text"] for i in gated], store,
                              turn_id=f"dragnet-fine-{label}", max_tokens=fine_max)
        for pos, i in enumerate(gated):
            v = f_res.resolved.get(pos)
            if v is not None:
                fine[i] = v if isinstance(v, dict) else v.dict()
    t_fine = time.time() - t1
    # MERGE → the superset record per chunk
    records = []
    for i, ch in enumerate(chunks):
        cv = coarse.get(i)
        if cv is None:
            continue                                          # coarse failed for this chunk (counted below)
        rec = {"chunk_id": ch["id"], "rel_path": ch["rel_path"], "anchor": ch["anchor"], "date": ch["date"],
               "grain": "fine" if i in fine else "coarse", **cv}
        if i in fine:
            rec.update(fine[i])
        records.append(rec)
    stats = {"n": len(chunks), "coarse_ok": len(coarse), "coarse_failed": len(c_res.failed),
             "gated_to_fine": len(gated), "fine_ok": len(fine),
             "t_coarse_s": round(t_coarse, 1), "t_fine_s": round(t_fine, 1),
             "throughput_coarse_per_s": round(len(coarse) / t_coarse, 1) if t_coarse else 0,
             "total_s": round(time.time() - t0, 1)}
    return records, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=0, help="PROVE/MEASURE on N sampled chunks (does NOT bake the asset)")
    ap.add_argument("--sample-step", type=int, default=37, help="take every Nth chunk for a diverse sample")
    ap.add_argument("--all", action="store_true", help="the FULL bake (gated — needs --confirm + the checklist)")
    ap.add_argument("--confirm", action="store_true", help="actually fire the full bake")
    ap.add_argument("--projects", default="", help="comma-sep rel_path substrings to INCLUDE (Tim's filter)")
    ap.add_argument("--since", default=None, help="conversation date >= YYYY-MM-DD (from anchor, not mtime)")
    ap.add_argument("--until", default=None, help="conversation date <= YYYY-MM-DD")
    ap.add_argument("--coarse-max", type=int, default=220)
    ap.add_argument("--fine-max", type=int, default=600)
    ap.add_argument("--write", action="store_true", help="write records to .data/store/extractions/")
    ap.add_argument("--db", default=SUBSTRATE_DB, help="substrate db to read (default claude-sessions; for "
                    "visual-dna use the overlord .state db)")
    ap.add_argument("--vault", default=None, help="restrict to one substrate vault (e.g. visual-dna)")
    ap.add_argument("--out-name", default="full", help="output basename → extractions-<name>.jsonl")
    a = ap.parse_args()
    projects = [p.strip() for p in a.projects.split(",") if p.strip()] or None

    if a.all and not a.confirm:
        print("FULL BAKE is GATED. Before --all --confirm, these must be TRUE:\n"
              "  [ ] throughput measured at 32-concurrent scale (fork+recollection)\n"
              "  [ ] max_tokens sized (run --sample, check no finish=length truncation)\n"
              "  [ ] Tim's filter list set (--projects / --since / --until)\n"
              "Run --sample N first. Refusing to fire 35,904 chunks unconfirmed.")
        return 2

    n = a.sample if a.sample else (None if a.all else 50)
    chunks = load_chunks(projects=projects, since=a.since, until=a.until,
                         limit=(n if not a.all else None), sample_step=(a.sample_step if a.sample else None),
                         db=a.db, vault=a.vault)
    print(f"loaded {len(chunks)} chunks  (projects={projects} since={a.since} until={a.until})")
    if not chunks:
        print("no chunks after filter — check the filter (note: date is from anchor, not mtime).")
        return 1

    from store.fs_store import FsStore
    from fabric import config as fcfg
    store = FsStore(fcfg.STORE_DIR)

    # FULL bake: BATCHED + APPENDED incrementally (crash-safe — a ~2h run can't write only at the end;
    # a mid-run crash keeps every completed batch + lets us resume from the last chunk_id written).
    if a.all:
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, f"extractions-{a.out_name}.jsonl")
        done_ids = set()
        if os.path.exists(path):                              # RESUME: skip chunks already written
            for line in open(path):
                try: done_ids.add(json.loads(line)["chunk_id"])
                except Exception: pass
            if done_ids:
                print(f"RESUME: {len(done_ids)} chunks already extracted → skipping them")
        todo = [c for c in chunks if c["id"] not in done_ids]
        BATCH = 500
        agg = {"n": 0, "coarse_ok": 0, "coarse_failed": 0, "gated_to_fine": 0, "fine_ok": 0}
        t0 = time.time()
        with open(path, "a") as f:
            for bi in range(0, len(todo), BATCH):
                batch = todo[bi:bi + BATCH]
                recs, st = run_extract(batch, store=store, coarse_max=a.coarse_max, fine_max=a.fine_max,
                                       label=f"full-{bi}")
                for r in recs:
                    f.write(json.dumps(r) + "\n")
                f.flush()
                for k in agg: agg[k] += st.get(k, 0)
                el = time.time() - t0
                print(f"  batch {bi}-{bi+len(batch)}: +{len(recs)} recs (fine {st['fine_ok']}) | "
                      f"total {agg['coarse_ok']}/{len(todo)} | {el/60:.1f}min elapsed", flush=True)
        print(f"\nBAKE COMPLETE: {agg} → {path} ({(time.time()-t0)/60:.1f}min)")
        return 0

    # sample / --write path (proof)
    records, stats = run_extract(chunks, store=store, coarse_max=a.coarse_max, fine_max=a.fine_max,
                                 label="sample")
    print("STATS:", json.dumps(stats, indent=2))
    grains = {"coarse": sum(1 for r in records if r["grain"] == "coarse"),
              "fine": sum(1 for r in records if r["grain"] == "fine")}
    print("grain distribution:", grains, f"(gate kept {grains['fine']}/{len(records)} at fine)")
    if a.write:
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "extractions-sample.jsonl")
        with open(path, "w") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
        print(f"wrote {len(records)} records → {path}")
    else:
        print("(--write not set — proof/measure only, asset not written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
