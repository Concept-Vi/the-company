"""routines/dragnet_freshness.py — the OWNER of the dragnet asset staleness check (unify-exercise 2026-06-26).

Q6 resolution: freshness is a DECLARED computed flag + a routine owner, NEVER an auto-rebake and NEVER a
resolver-side reindex (extract-once/query-many economics — a bake is ~4h). The determine() envelope already
surfaces a cheap per-asset age flag (recall_determine.asset_freshness). THIS routine owns the DEEP check:
compare each baked asset against its SOURCE corpus and, when the source has grown materially past the bake,
surface ONE (Gap)/(Notice) addressed to the lead + PROPOSE a rebake via the dragnet_extract flow. It does
NOT rebake (operator-only via the --confirm door). Fire: routines op=fire id='dragnet_freshness', or the
systemd-timer arm (cadence below).
"""
from __future__ import annotations

ROUTINE = {
    "id": "dragnet_freshness",
    "label": "Dragnet asset freshness — source-vs-asset staleness owner",
    "description": (
        "Owns the deep dragnet staleness check (Q6: declared flag + routine, never auto-rebake). For each "
        "baked extraction asset, compares its bake time against the newest source content; when the source "
        "has grown past the bake, surfaces ONE (Gap)/(Notice) + proposes a rebake through the dragnet_extract "
        "flow. Does not rebake (operator-only via the --confirm door)."
    ),
    "prompt": (
        "You are the DRAGNET FRESHNESS owner. Your job: detect when a baked dragnet extraction asset is STALE "
        "vs its source, and SURFACE it — never rebake (the ~4h bake is operator-only).\n\n"
        "METHOD:\n"
        "1. List the baked assets: ls .data/store/extractions/extractions-*.jsonl (note each one's mtime).\n"
        "2. For each asset, identify its SOURCE and check whether the source has NEWER content than the bake:\n"
        "   - 'full' ← the claude-sessions substrate / ~/corpora/claude-sessions (the session-history corpus).\n"
        "   - 'visual-dna' ← the Visual-DNA vault (overlord .state db).\n"
        "   - others ← infer from the asset name; if you can't, say so (honest, never guess).\n"
        "   Compare the source's newest content time / count against the asset mtime + record count. A cheap "
        "   first cut: source newest-mtime > asset mtime, or source chunk-count >> asset record-count.\n"
        "3. For each STALE asset, post ONE (Gap)+(Notice) to the active channel addressed to the LEAD: the "
        "   asset, how stale (age, source-grown-by), and the PROPOSED rebake — call the dragnet_extract flow "
        "   (mcp__company__flows op='run' flow='dragnet_extract' with out_name=<asset> and any scope filters) "
        "   so the operator gets a runnable proposal. Do NOT run the bake yourself.\n"
        "4. If every asset is fresh, say so plainly (honest no-op — no fabricated staleness).\n\n"
        "THE BAR: surface, propose, never rebake. extract-once/query-many: a bake is expensive and operator-"
        "gated; your value is catching silent staleness before a determine() answers from a stale asset."
    ),
    "cwd": "/home/tim/company",
    "permission_mode": "default",        # reads + a channel post + a propose-only flow; no dangerous writes
    "cadence": "every:86400",            # daily (the systemd-timer arm reads this grammar) + fire-on-demand
    "repeats": True,
    "max_turns": 10,
    "trigger": (
        "schedule (daily) OR fire after a large corpus growth — the standing owner of dragnet asset staleness "
        "(Q6: declared flag in determine() + this routine; never auto-rebake)."
    ),
}
