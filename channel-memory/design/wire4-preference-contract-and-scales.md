# Wire 4 — Preference-Signal Contract + the Shared Scale Taxonomy (WELDED)

```
trust: fabric-derived — cross-reviewed + AGREED by fork (ch-8djrpmsl) + recall-fork (ch-83e2cque); the hierarchy is tim-direct(session=11e7d395)
author: ch-8djrpmsl (fork) — welded from the t-1781435815 thread
date: 2026-06-14 (overnight)
status: AGREED — both sides build to this. Pillar-1 hierarchy/scale folding = recall-fork; the feeder + multi-scale chunker = fork.
```
> The welded spec for the two shared wires between session-recall (INNER) and recollection (OUTER): the **preference-signal feed** (wire 4 → Pillar-1) and the **scale taxonomy** (chunk-scales == unit-scales). Both held to the keystone bar — the preference layer IS the fabric's self-approval safety substrate; recovery-quality gates autonomy, so it must be re-verifiable (structure, not trust), pattern-level across time AND projects, no-fiction.

## A. PreferenceSignal — the session-side feed (fork EXTRACTS, Pillar-1 JUDGES)
The INNER lens emits, per session, a set of leveled SIGNALS (hypotheses with evidence). It does NOT decide cross-session truth — Pillar-1 re-grounds on the evidence and judges the authoritative tree. Extraction-vs-judgment.

```
PreferenceSignal {
  source:  "session://<project>/<sid>",     # provenance — re-embed-stable, multi-space canonical identity
  project: "<project>",                      # FIRST-CLASS (recall-fork ask): the bar is pattern across time AND projects
  signals: [ {
     statement:  str,                        # the standing preference/requirement, in Tim's intent
     level:      "broad-principle" | "mid" | "specific-application",   # the conceptual hierarchy (tim-direct: "broad down to specific")
     parent:     str | null,                 # link to a broader signal's statement (the per-session hypothesised tree)
     polarity:   "do" | "dont" | "value",
     evidence:   [ {line, ts, quote} ],      # VERBATIM quote + resolvable line-ref — Pillar-1 RE-GROUNDS on the real turn, never trusts blind
     basis:      "explicit" | "correction" | "frustration" | "repetition" | "implicit",
     session_weight: float,                  # WITHIN-session salience (repetition/emphasis/correction-strength) — NEVER position/recency
     confidence: "high" | "med" | "low",
     relates_to: {slug: "<feedback-slug>", relation: "supports"|"contradicts"|"refines"} | null  # lets Pillar-1 supersede on the time axis
  } ],
  caveats: [str]                             # MANDATORY — where the session signal is thin/ambiguous (the no-fiction honesty channel)
}
```

### The two gates (the safety mechanism — no-fiction-about-Tim)
1. **Emit-gate (fork):** a signal with NO structural `evidence[]` is NOT emitted. No evidence ⇒ it would be fiction ⇒ dropped.
2. **Ratification-gate (Pillar-1):** recollection re-grounds each signal on its verbatim evidence + line-ref, judges pattern-level across sessions+projects, and ratifies before anything becomes a STANDING preference that licenses self-approval.
Two gates, because if the recovery is wrong the autonomy is unsafe.

### Ownership / layering (agreed)
- **Fork (INNER):** tool-derives over its OWN session scope (runs recall/lenses over the session → leveled signals). Does NOT read the cross-session `feedback-*` corpus (that's the outer layer's, to keep cross-session synthesis out of the inner scope).
- **recollection (OUTER / Pillar-1):** reads `feedback-*` directly (via tools), ingests every session's PreferenceSignals, owns the authoritative broad→specific tree, does the cross-session + temporal anti-recency weighting, ratifies.
- **Tool-driven (tim-direct "use the tools"):** both layers actively retrieve — each over its own scope. Not a static file read.

## B. The shared SCALE TAXONOMY (chunk-scales == unit-scales — ONE vocabulary)
Nested STRUCTURAL ladder (finest → coarsest):
```
atom  ⊂  dimension  ⊂  turn  ⊂  section  ⊂  segment  ⊂  session  ⊂  project
 │         │            │        │           │           │          └ ~/.claude/projects/<encoded-cwd>/
 │         │            │        │           │           └ one .jsonl
 │         │            │        │           └ a compaction generation (isCompactSummary boundary)
 │         │            │        └ a header/paragraph-delimited group within a turn
 │         │            └ one exchange (a user or assistant message)
 │         └ one dimension within a dense turn (a line/point — the dimension-aware chunk)
 └ one event (msg / tool_call / tool_result)
```
CROSS-CUTTING (span the ladder, not on it):
- **intent-constellation** — a Tim-intent + its agent fan-out (the work one directive spawned).
- **concept / topic** — a semantic grouping across positions.

Fork's chunker emits at the ladder scales (dimension/section/turn at least), each chunk tagged `scale` + `parent` (the turn line) so recall can target or blend scales. recollection's typed units (G0.2 atoms) use the SAME vocabulary — a chunk at scale S maps 1:1 to a unit of type S.

## C. D8 drift-detection mapping
The fork's per-session drift-detection lens (diff current-self vs earlier-self — a TEMPORAL/STATE-axis op) feeds recollection's identity-over-time layer; recollection's `find_state_asymmetries` state-sensor is its cross-session generalization. Fork owns the per-session lens; it feeds the outer state/identity layer.

---
*Welded 2026-06-14 overnight. Build targets: fork → the leveled-signal feeder + the multi-scale chunker to §A/§B; recall-fork → fold the hierarchy + scale taxonomy into Pillar-1 + G0.2. Cross-link: [[UNIFIED-SEAM]] (wire 4 + wire of scales), [[2026-06-14-session-splicing-and-channel-memory]].*
