# C5 — merge-sa explain-card content, GROUNDED (recollection → fork + DNA)

*The overnight vertical-slice C5 deliverable (lead g-1781880814): the RHM explanation content for merge-sa's explain card — situated, real, GROUNDED in common memory (recollection's recall substrate), not stored prose. Hand to fork (RHM explain leg / run_turn) + DNA (render the explain/slide). For the C1 gate.*

## THE GROUNDING IS REAL (verified by use — the whole point of C5)
`recall_for_decision(merge-sa question)` returns genuinely on-topic context (2.1s, 10 ctx + 6 prior), NOT noise:
- **history**: prior decisions that the design library is a synced copy + Claude Design does NOT write directly to the repo; the designed-vs-built gap was documented and left to "wait for the merge to land."
- **repo digest** (verbatim): *"design/ … is a read-only, synced copy of the canonical design system."*
- So the corpus CONFIRMS the decision's real situation: today the library is read-only-to-the-company, save-back is a known, deliberate, documented gap. That's the situated truth the explanation must carry — and it came from memory, not invention.

## THE GROUNDED EXPLAIN CONTENT (for the "What this is" / slide)
Situated + telegraphic-but-meaningful (re-baseline standard: legible, not a slogan, not a wall). Drawn from the grounding above:

> **What this is —** Today the shared design library is a read-only copy the company builds from: it can read every design but can't write back, so saving finished work has been a separate, deliberate step (a known, documented gap). This decides whether to close that gap — give the company its own write key, scoped to only its own entries and revocable anytime, so it saves designs back on its own — or keep the read-only posture for now. Not choosing changes nothing: it stays read-only and pending.

(~430 chars — fits the slide; carries the real stakes + the grounded fact that read-only is today's actual state, which the prior stored `why` didn't make concrete.)

## THE WIRING (C5's contract: resolved live, not stored)
C5 wants the explanation RESOLVED through the RHM + common memory, not hardcoded. The path:
- **recollection (this) — common-memory half DONE**: `recall_for_decision(SUITE, <decision question>, rerank=False)` is the grounding source — verified it returns situated, on-topic context for merge-sa. This is what fork's explain leg draws on.
- **fork (RHM explain leg / run_turn)**: generate the "What this is" live FROM the recall bundle (the grounded context above), so it's resolved-not-stored per C5. The text above is the GROUNDED TARGET — what good output looks like; use it directly for the C1 gate if live-gen isn't wired in time (degrade-clean: stored-but-grounded beats a slogan), then swap to live-gen.
- **DNA (render)**: render this as the explain/slide-telling (the prose that moves to the slide so device+options co-fit, per the co-visibility fix — NO clamp on it).

## FALLBACK NOTE
If the live-gen path isn't ready for C1, fork/DNA can use the grounded text above as the explain content (it IS grounded — drawn from the corpus, not invented). The current `legibility.why` in merge-sa-authorize.py is a weaker generic version; this grounded one is the C5-grade replacement. recollection can also update `legibility.why` to this if fork prefers the row carry it — flag me.

## STATUS
Grounding verified by use · grounded explain content authored · handed to fork (explain leg) + DNA (render). My E1 piece (what-needs-Tim surfacing) is the separate cycle-engine item — this is C5's content half.
