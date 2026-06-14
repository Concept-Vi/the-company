"""runtime/session_lens.py — LENSES over a scanned session (the useful-questions layer).

Tim's directive (2026-06-14): recall is more than "find decisions" — build the family of useful views a
session scanner + embedding index enables, the easy wins. A lens is a cheap query over one or both
substrates already built:
  • STRUCTURAL rows  → runtime/session_scan (who/when/tokens/boundaries/gaps/attribution/system-subtypes)
  • SEMANTIC index   → runtime/session_recall (embed + cosine, the Company-served :8007 embedder; bridge-free)

Lenses (all read-only):
  find(q)         — semantic recall (general).                              [meaning]
  decisions(topic)— recall biased toward decision language (chose/switched/locked).  [meaning + cue]
  open_loops()    — UNRESOLVED threads: blockers, "needs you", gated, gaps, Tim's open questions,
                    with a resolution heuristic (did a later turn close it?).  [Tim's #1 pain: lost threads]
  catch_up(since) — what happened in a window / since the last away-gap (the "catch me up" he asks for).  [rows + gaps]
  timeline(topic) — every place a topic was discussed, sorted by time — the topic's arc.  [meaning over time]
  directives()    — every GENUINE Tim turn, chronologically — the whole-slate / no-dropped-ask ledger.  [structural]

CLI: python3 -m runtime.session_lens <jsonl> <lens> [arg] [--k N] [--index-dir DIR]
"""
from __future__ import annotations

import json
import os
import re
import sys

from runtime.session_scan import scan_session, _iter_jsonl, _iso_to_epoch
from runtime import session_recall as sr

# cue vocabularies — grounded in patterns observed in real sessions (structural, declared, extend freely)
BLOCKER_CUES = re.compile(r"\b(needs? you|need from you|one step needs|one-keystroke|hard stop|parked on|"
                          r"talk to me before|gated on|awaiting|blocked on|still downloading|waiting on|"
                          r"before you|your (go|call|word)|pending your|can't proceed|unblock)\b", re.I)
GAP_TAG_CUES = re.compile(r"\[(Gap|Notice|TODO|FIXME|Blocked|Pending)\]|TODO:|FIXME:", re.I)
DECISION_CUES = re.compile(r"\b(decided|decision|chose|choose|switched to|we'?ll use|go with|going with|"
                           r"the call is|settled on|locked|let'?s use|opt(ed)? for|picked)\b", re.I)
RESOLVED_CUES = re.compile(r"\b(done|fixed|resolved|working|proven|verified|complete[d]?|landed|live now|"
                           r"shipped|committed|now works|got it working|✓|✅)\b", re.I)
TIM_QUESTION = re.compile(r"\?\s*$|^(can|could|will|would|what|why|how|when|where|is|are|do|does|should)\b", re.I)

INJ_PREFIXES = ("<task-notification", "<command", "<local-command", "Base directory for this skill",
                "<persisted-output", "<user-prompt-submit")


# ───────────────────────── shared: genuine content turns with text ─────────────────────────

def _turns(jsonl_path: str) -> list[dict]:
    """Genuine content turns (human/assistant/compaction/channel) with text + structural handle.
    Reuses the scanner's attribution (inject/tool already excluded structurally)."""
    rows = scan_session(jsonl_path)["rows"]
    wanted = {r["line"] for r in rows if r["attr"] in ("user", "assistant", "compaction", "channel")}
    texts = sr._texts_for_lines(jsonl_path, wanted)
    out = []
    for r in rows:
        if r["line"] not in wanted:
            continue
        t = (texts.get(r["line"]) or "").strip()
        if not t:
            continue
        out.append({"line": r["line"], "ts": r["ts"], "attr": r["attr"], "model": r.get("model"),
                    "point": r.get("boundary_point"), "epoch": _iso_to_epoch(r["ts"]), "text": t})
    return out


def _clip(t: str, n: int = 240) -> str:
    return " ".join(t.split())[:n]


# ───────────────────────── lenses ─────────────────────────

def find(jsonl_path: str, query: str, k: int = 8, index_dir: str | None = None) -> dict:
    """General semantic recall (delegates to session_recall)."""
    return {"lens": "find", **sr.recall(jsonl_path, query, k=k, index_dir=index_dir)}


def decisions(jsonl_path: str, topic: str, k: int = 6, index_dir: str | None = None) -> dict:
    """Recall biased toward decision language: semantic recall, then re-rank-boost chunks whose text
    carries a decision cue (chose/switched/locked/…). Surfaces the DECISION turn, not just discussion."""
    # QUERY EXPANSION — a generic topic ("embedding model") pulls broad discussion; the SOURCE decision
    # turn surfaces only for decision-pointed phrasings. So embed several phrasings and merge each chunk
    # by its MAX cosine across them (verified: this lifts the canonical pplx-4b turn into the top for the
    # generic topic). rerank is deliberately OFF (it favours later recall-chatter over the source turn).
    queries = [
        f"which {topic} did we choose, and why — the decision and the reasoning",
        f"we decided to use / switched to / picked {topic} because",
        f"the comparison of {topic} options and the final pick over the alternatives",
    ]
    merged: dict[int, dict] = {}
    for q in queries:
        for h in sr.recall(jsonl_path, q, k=30, rerank=False, index_dir=index_dir)["hits"]:
            if h["attr"] in ("channel", "compaction"):   # fabric meta, not the live decision
                continue
            cos = h.get("cosine") or 0
            cur = merged.get(h["line"])
            if cur is None or cos > cur["cosine"]:
                merged[h["line"]] = {**h, "cosine": cos}
    cands = list(merged.values())
    for h in cands:
        h["decision_cue"] = bool(DECISION_CUES.search(h["text"]))
        # cue is an ADDITIVE tiebreaker, NOT a gate — a high-cosine decision turn that happens not to use
        # the literal word "chose/switched" must NOT be sunk below a low-cosine turn that does.
        h["score"] = round(h["cosine"] + (0.04 if h["decision_cue"] else 0), 4)
    ranked = sorted(cands, key=lambda h: -h["score"])
    return {"lens": "decisions", "topic": topic,
            "ranking": "max-cosine over expanded decision phrasings + decision-cue bonus; rerank off",
            "hits": ranked[:k]}


def open_loops(jsonl_path: str, k: int = 25) -> dict:
    """UNRESOLVED threads — the lost-thread killer. Find blocker/gap/question cues, then check whether a
    LATER turn plausibly resolved each (a resolution cue near the same topic after it). Heuristic, declared."""
    turns = _turns(jsonl_path)
    loops = []
    for i, t in enumerate(turns):
        if t["attr"] == "channel":          # fabric chatter is not a session thread
            continue
        kind = None
        if t["attr"] == "assistant" and BLOCKER_CUES.search(t["text"]):
            kind = "blocker(assistant asked Tim)"
        elif GAP_TAG_CUES.search(t["text"]):
            kind = "gap/tag"
        elif t["attr"] == "user" and (TIM_QUESTION.search(t["text"]) or "?" in t["text"][:400]):
            kind = "tim-question"
        if not kind:
            continue
        # resolution heuristic (TIGHT + honest): a resolution cue in the NEXT 4 turns (the immediate
        # exchange), AND for a Tim-question, a substantial assistant reply right after. Dense sessions
        # make any wider window meaningless (everything "resolves" eventually) — so this stays a HINT.
        nxt = turns[i + 1:i + 5]
        resolved = any(RESOLVED_CUES.search(later["text"]) for later in nxt)
        if kind == "tim-question":
            resolved = resolved or any(later["attr"] == "assistant" and len(later["text"]) > 400 for later in nxt)
        loops.append({"line": t["line"], "ts": t["ts"], "attr": t["attr"], "kind": kind,
                      "likely_resolved": resolved, "text": _clip(t["text"], 200)})
    openish = [l for l in loops if not l["likely_resolved"]]
    openish.sort(key=lambda l: l["ts"] or "", reverse=True)     # MOST RECENT open loops first — what matters now
    return {"lens": "open_loops", "total_candidates": len(loops), "likely_open": len(openish),
            "open": openish[:k],
            "note": "likely_resolved = a resolution cue (or substantial reply) within the next 4 turns — a HINT, not proof; latest-first. Verify before acting."}


def catch_up(jsonl_path: str, since: str | None = None, k: int = 20) -> dict:
    """What happened in a window. `since` = ISO ts; if omitted, start AFTER the last big gap (the last
    time Tim stepped away). Returns the substantive turns in the window, chronological."""
    turns = _turns(jsonl_path)
    if not turns:
        return {"lens": "catch_up", "window": None, "items": []}
    start_ep = _iso_to_epoch(since) if since else None
    if start_ep is None:
        # find the last large gap (>1h) and start after it
        biggest = None
        for a, b in zip(turns, turns[1:]):
            if a["epoch"] and b["epoch"]:
                gap = b["epoch"] - a["epoch"]
                if gap > 3600 and (biggest is None or gap > biggest[0]):
                    biggest = (gap, b["epoch"], b["ts"])
        start_ep = biggest[1] if biggest else turns[0]["epoch"]
        since = biggest[2] if biggest else turns[0]["ts"]
    window = [t for t in turns if (t["epoch"] or 0) >= (start_ep or 0)]
    # the substantive ones: biggest turns + all Tim turns, chronological
    sub = sorted(window, key=lambda t: -len(t["text"]))[:k * 2]
    sub = sorted({t["line"]: t for t in (sub + [w for w in window if w["attr"] == "user"])}.values(),
                 key=lambda t: t["line"])
    return {"lens": "catch_up", "since": since, "window_turns": len(window),
            "items": [{"line": t["line"], "ts": t["ts"], "attr": t["attr"], "text": _clip(t["text"], 220)} for t in sub[:k]]}


def timeline(jsonl_path: str, topic: str, threshold: float = 0.35, index_dir: str | None = None) -> dict:
    """When was a topic discussed — every semantic hit above threshold, sorted by TIME (the topic's arc)."""
    res = sr.recall(jsonl_path, topic, k=40, rerank=False, index_dir=index_dir)
    hits = [h for h in res["hits"] if (h.get("cosine") or 0) >= threshold]
    hits.sort(key=lambda h: h["ts"] or "")
    return {"lens": "timeline", "topic": topic, "n": len(hits),
            "points": [{"line": h["line"], "ts": h["ts"], "attr": h["attr"], "cosine": h["cosine"],
                        "text": _clip(h["text"], 160)} for h in hits]}


def directives(jsonl_path: str, k: int = 100) -> dict:
    """Every GENUINE Tim turn, chronologically — the whole-slate ledger (nothing dropped). Structural:
    the scanner's 'user' attribution already excludes inject/tool/compaction."""
    rows = scan_session(jsonl_path)["rows"]
    wanted = {r["line"] for r in rows if r["attr"] == "user"}
    texts = sr._texts_for_lines(jsonl_path, wanted)
    items = []
    for r in rows:
        if r["line"] not in wanted:
            continue
        t = (texts.get(r["line"]) or "").strip()
        if not t or t.lstrip().startswith(INJ_PREFIXES):
            continue
        items.append({"line": r["line"], "ts": r["ts"], "bytes": len(t.encode()), "text": _clip(t, 200)})
    return {"lens": "directives", "n": len(items), "items": items[:k]}


LENSES = {"find": find, "decisions": decisions, "open_loops": open_loops,
          "catch_up": catch_up, "timeline": timeline, "directives": directives}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    jsonl, lens = sys.argv[1], sys.argv[2]
    rest = sys.argv[3:]
    idx = rest[rest.index("--index-dir") + 1] if "--index-dir" in rest else None
    arg = next((x for x in rest if not x.startswith("--")), None)
    fn = LENSES.get(lens)
    if not fn:
        print(f"unknown lens {lens!r}; one of {list(LENSES)}"); sys.exit(2)
    kw = {}
    if idx and lens in ("find", "decisions", "timeline"):
        kw["index_dir"] = idx
    if lens in ("find", "decisions", "timeline"):
        out = fn(jsonl, arg or "", **kw)
    elif lens == "catch_up":
        out = fn(jsonl, since=arg)
    else:
        out = fn(jsonl)
    print(json.dumps(out, indent=2, ensure_ascii=False))
