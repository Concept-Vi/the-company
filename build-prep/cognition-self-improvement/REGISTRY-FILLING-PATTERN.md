# The Registry-Filling Pattern (GC2) — a reusable production line for growing registries

**Status: TENTATIVE design capture — written 2026-06-10 from Tim's feedback on the RG10 run + the run's
own evidence. Tim has not reviewed this document. Assumptions are marked. This is the seed for the
design conversation, not a settled spec.**

Tim's framing (verbatim intent, 2026-06-10): *"That concept as a principle has a really high rate of
reusability — there will likely be a lot of registries that don't have all of the data entries they
need, or any other large work that follows rules, so getting it right and reusable is very high value.
And pretty much immediately useful to this actual project too."*

---

## What the pattern IS (one sentence)

A bounded chain that takes a large pile of raw units, has small models propose structured entries for
each — **with a designed context package, never bare** — mechanically rejects everything that violates
the closed world, and ends at the operator's approve gate; nothing writes itself.

## The stages, and what each one REQUIRES

```
SOURCE → GROUND → MAP → DEDUPE → FLOOR → JURY → SURFACE → [Tim APPROVES] → WRITE-BACK
```

1. **SOURCE** — a deterministic extractor produces the unit pile (no model). RG10's instance: the
   mockup-element candidates (940). The miner's instance: transcript exchanges. *The unit schema is
   frozen here; everything downstream depends on it.*

2. **GROUND** — the per-batch context is produced ONCE: a summary of the surrounding whole (the
   screen_reader pass), resolved once and shared, never re-derived per unit.

3. **MAP** — one role fires per unit, and the unit NEVER travels alone. The context package is part of
   the role's declared inputs (the law: a model-judgement step is only designed when its context
   package is designed with it). The package has four reusable slots:
   - **the unit itself** (the thing to describe)
   - **the parent/neighbour records** (already-approved entries the new one nests under)
   - **the ground** (the once-resolved whole-context from stage 2)
   - **exemplars + closed vocabularies** (real existing entries as the voice to match — a voice originally established BY an AI under Tim's direction; the finite
     lists of allowed values, with the copy-verbatim-or-say-proposed instruction)

4. **DEDUPE** — the embedder clusters the proposals; recurring sames collapse to one representative
   (RG10: 940 → ~550 unique).

5. **FLOOR** — the deterministic no-fiction gate, NO model: every claim against a closed world is
   mechanically checked (vocabulary membership, real-id membership, file/symbol resolution). **This is
   the guarantee.** Evidence from RG10: the 4B invented feature ids by analogy DESPITE the verbatim
   instruction in stage 3 — prompt context reduces fiction, only the floor stops it.

6. **JURY** — repeated model reads vote on soft accuracy. **Flag-never-drop**: no quorum → the entry is
   held for operator scrutiny, not deleted. The jury raises hands; it is never the gate.

7. **SURFACE** — one aggregate card at the operator's gate, built for scanning (totals → per-batch
   counts → compact rows → pointers to the full artifacts). Duplicate-guarded.

8. **WRITE-BACK** — runs only on the operator's approve. The chain PROPOSES; only Tim grows the truth.

## Why each piece is load-bearing (the failure each one prevents)

| Stage | Without it (observed, not hypothetical) |
|---|---|
| GROUND + context package | bare units → invention by design (Tim's prediction; also the literal first-draft failure at scale) |
| exemplars | the voice drifts from the 82 existing entries' altitude (themselves AI-written under Tim's direction when he first introduced the idea — the voice was never hand-authored) |
| closed vocabularies | free-text capability/feature fields → unjoinable data |
| FLOOR | invented-but-plausible ids pass the prompt instruction (RG10 caught real ones: INB-focus, NODE-act) |
| flag-never-drop | uncertain-but-real entries silently vanish |
| operator gate | the system writes its own self-knowledge — the one truth corrupts invisibly |
| fail-loud batch state | the all-940-fail scenario reports "done, 0 proposals" (the first-draft bug, verbatim) |

## The PARAMETERS (what changes per instance — the reuse axes)

An instance of the pattern is fully specified by:
- the **unit source** (which deterministic extractor, which pile)
- the **target registry** (which truth grows, what the entry schema is)
- the **grounding package** (which exemplars, which ground pass, which parent relation)
- the **closed vocabularies** (which finite lists the floor checks against)
- the **floor checks** (which mechanical verifications apply)
- the **surface shape** (what the operator's card shows)

Everything else — the chain skeleton, the dedupe, the jury, the gate, the resume-safe batch state —
is THE SAME every time and should exist ONCE.

## GC1 — the MCP consequence (Tim's multi-part point)

The chain proved that **agents default to the ungrounded design** (I did, with the grounded module in
my own session history). So per the path-of-least-resistance law: the pattern is not done until
invoking it through the company MCP is EASIER than rebuilding it. Today the proven chain lives in a
build-prep script the MCP face cannot see — that is the gap. Two candidate shapes (open, not decided):
- a **saved cascade** once the remaining engine seams close (the {mockup}-keyed ground chaining, the
  resolve-once shared ctx, the jury+refcheck composite step — the manual module IS their spec), or
- a **first-class flow tool** (a `flows`/`chains` resource on the face) that runs the chain with the
  six parameters above as its arguments.
ASSUMPTION to test: the saved-cascade shape is preferable because it keeps one execution engine
(reuse-don't-parallel); the flow tool is a fallback if the seams stay open long.

## GC3 — the extension Tim seeded: addresses as ACCUMULATION POINTS

Tim's idea (2026-06-10, his words condensed): with entries attached to things and the approval system
in place, he can talk to the right hand man about what he WANTS a thing to be — and that conversation
**adds new fields onto the SAME address**, through the SAME gate; any coding/knowledge agent reading
the address then sees the fields relevant to it.

What this does to the pattern: WRITE-BACK stops being a one-shot terminal stage and becomes the
**standard write-path for a growing record**. The address is the fixed coordinate; field families
accumulate (the production line wrote `what/can-do/how-to-change`; Tim's conversations add
intent/idea fields; future instruments add usage/telemetry fields); each consumer reads a projection.
This is the altitude-transformation layer made concrete: same address, different altitudes as
different fields.

Open design questions for the conversation with Tim:
- field-family naming + who may propose into which family (the RHM proposes intent fields; the line
  proposes description fields; both ride the one gate?)
- does an approved field-write version the record (history per address) or update in place
  (Tim's no-versioning law suggests in-place with the event log as the history)?
- which consumer sees which fields — a declared projection per consumer kind, or per-request?

## Standing instances (current + obvious next)

- **RG10 / ui-addresses** — the proven instance (231 confirmed / 320 flagged at the gate now).
- **The transcript miner** — already pattern-shaped (deterministic extract → grounded MAP → embed →
  flag-style honesty), missing only a floor + gate because its output is corpus memory, not registry
  truth. ASSUMPTION: memory-writes stay ungated (additive, queryable, low-blast-radius) — confirm.
- Next candidates visible from here: the feature inventory itself (58 entries, hand-grown), the
  capability vocabulary, mark_types/relation_types seeds, the model-capability registry — each is a
  registry that "doesn't have all the data entries it needs" (Tim's words).
