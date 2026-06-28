"""routines/guide_freshness.py — the OWNER of guide staleness (the guide-author's recurring 'practice').

A guide is composed FROM source addresses and records a source-hash; when those sources change, the guide
is STALE and should be re-authored, so the system's how-tos TRACK the system instead of rotting. This
routine is that practice made recurring (Tim's 'built means usable' bar: the guide-author is not really
built until the practice actually RUNS, not just exists as a function). Unlike the dragnet bake (~4h,
operator-gated), re-authoring a guide is cheap and SAFE in propose-mode (writes nothing — surfaces a diff),
so this routine re-authors stale guides as PROPOSALS and surfaces them for review. Fire: routines op=fire
id='guide_freshness', or the systemd-timer arm (cadence below).
"""
from __future__ import annotations

ROUTINE = {
    "id": "guide_freshness",
    "label": "Guide freshness — re-author stale guides as proposals (the guide-author's practice)",
    "description": (
        "Owns guide staleness: detects guides whose source addresses changed since they were authored and "
        "re-authors them as PROPOSALS (propose-mode — never clobbers a human-edited guide), surfacing the "
        "diffs for review. The recurring 'practice' that keeps the system's how-tos tracking the system."
    ),
    "prompt": (
        "You are the GUIDE FRESHNESS owner. Your job: keep the Company's narrative guides (guide://<id>) "
        "TRUE to the system they document — re-author the stale ones, surface the changes, clobber nothing.\n\n"
        "METHOD:\n"
        "1. Report freshness: call author_guide(op='staleness'). Each guide reports stale=true/false (a "
        "   guide is stale when its grounded_from sources changed since its recorded source_hash).\n"
        "2. If every guide is fresh, say so plainly (honest no-op — never fabricate staleness).\n"
        "3. For the stale ones, re-author as PROPOSALS: call author_guide(op='refresh', on_existing='propose'). "
        "   This composes a fresh narrative from the (changed) sources via the guide_author model and returns "
        "   a diff per guide — it WRITES NOTHING (a human-edited guide stays safe).\n"
        "4. Post ONE (Notice) to the active channel addressed to the LEAD: which guides were stale and that "
        "   re-authored proposals are ready to review; include each guide's address. To accept a proposal, the "
        "   lead/agent re-runs author_guide(target=…, grounded_from=…, on_existing='overwrite') for that guide.\n\n"
        "THE BAR: detect → re-author as a proposal → surface. Never overwrite a guide unattended (propose, "
        "don't clobber); never invent staleness (a guide with cold grounding is surfaced as a problem, not "
        "silently 'fresh')."
    ),
    "cwd": "/home/tim/company",
    "permission_mode": "default",        # reads + model compose (propose-only) + a channel post; no clobber
    "cadence": "every:86400",            # daily (the systemd-timer arm reads this grammar) + fire-on-demand
    "repeats": True,
    "max_turns": 10,
    "trigger": (
        "schedule (daily) OR fire after a change to source skills/contexts a guide is grounded in — the "
        "standing owner of guide staleness (the guide-author's recurring practice; propose, never clobber)."
    ),
}
