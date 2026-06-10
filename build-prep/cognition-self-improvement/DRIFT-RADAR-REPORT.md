# ② Drift-Radar Report (canonical, update-in-place; data: `.build/drift/findings.json`)

**This pass: 2026-06-10, the first FULL-REPO sweep (unblocked by ① — 586 embedded file-digests).**
Pipeline: all-pairs cosine (1,626 near-pairs ≥0.82) → union-find clusters → judge_drift CONFIRM on the
21 largest → 8 confirmed (marked, direction=surface) · 13 judged DISTINCT (the false-positive guard
doing its job — near-but-legitimate siblings rejected). Channel B (doc-vs-code): 1 candidate.

## Confirmed unification candidates (marked; the operator/lead decides — never auto-fixed)

1. **The three build-methodology docs** (`docs/methodology/{company,rhm,wire}-build.md`, cos .86) —
   the same cron-loop/lanes/verify-by-use protocol written three times. Real; a one-source
   methodology page with per-build deltas would hold it.
2. **live-resolution-surface pair** (cos .94 — the repo's nearest pair): `live-intent-resolution-surface.md`
   vs `project-base-live-intent-resolution.md` — one is the draft/base of the other (this is the folder
   Tim renamed; the formatting cleanup there is already a pending needs-tim).
3. **MERGE-COORDINATION.md vs coordination/WORK-SPLIT.md** (cos .86) — two coordination protocols for
   the same parallel-session problem; known accumulation, real consolidation target.
4. **guided-review-surface ANCHOR vs main doc** (cos .86) and **the two coordination BRIEFs** (cos .84)
   — partially BY-DESIGN layering (an ANCHOR is an intentional summary); judge can't see intent. See
   "limitations" — candidates, not verdicts.
5. **tests/interactive_consent vs tests/propose_affordance** (cos .85) — two acceptance suites proving
   the same non-executing-suggest mechanism; plausible real overlap in test coverage.
6. **tests/speakable_acceptance.py vs voice/speakable.py** (built-twice, cos .84) — **judged
   borderline-FP by the lead**: a test mirroring its module's vocabulary is the test DOING ITS JOB.
   Kept in the data (the mark is reviewable), noted as a known radar limitation.
7. **concurrent-cognition 00-LANDSCAPE vs 03-concurrency** (cos .83) — design-doc series overlap;
   the series structure is intentional, the specific duplicated content may still merit a tighten.

## Doc-vs-code drift (channel B, deterministic)

- **ai_tics/AGENTS.md** sits at 0.436 similarity to its own module's files (7 files) — the lowest in
  the repo and below the 0.45 line. The constitution there is the stalest-reading; worth a refresh
  pass when ai_tics is next touched.

## Honest limitations (next-pass upgrades, logged)

- **Intent-blindness**: ANCHOR/summary docs and test↔module mirrors read as overlap; the judge sees
  digests, not purpose-relations. Fix direction: feed the judge the pair's RELATION (same-dir?
  test-of? anchor-of?) as declared context — the GC2 context-package law applied to the radar itself.
- **Digest ceiling**: judgments ride 6k-char digests, not full files — fine for radar, not for verdicts.
- The first run swept an EMPTY set and reported clean zeros (the vec:// key-wrap; caught by
  zero-is-suspicious). The radar now hard-fails nothing silently — but a `space_size` sanity assert
  belongs in the flow row.
