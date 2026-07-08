# THE USE — what all of this is FOR, and how agents actually use it (Tim, 2026-07-08 — BINDING)

*Tim's articulation, processed and recorded. This sits above NORTH-STAR.md: the north star says what the
ledger IS (a coordinate space); THIS says what the whole apparatus is FOR. Every future build decision
answers to this frame.*

## The corpus's unique nature (why nothing standard applies)
This repo/estate is **entirely the output of AI generation with zero human code interaction, ever** — all
of it produced through Claude Code conversations with Tim (no dev background, no specs, no plans; he
directs by description and recognition). Consequences:
- **"Nothing works."** The code was never the authority and never the goal-state — it is the RESIDUE of a
  long generative process: drifted, spiraling, partial outputs accumulated over a common time axis.
- **There is no place where intent lives.** No spec, no requirements, no design doc of record. Intent
  exists ONLY smeared across time in the jsonl transcripts — through session compactions, drift,
  re-approaches, distractions and returns. **The transcripts are the primary text; the code is a lossy
  projection of them.**
- **The system must be fully SELF-RELATIVE.** No external instruction, direction, or context exists. An
  arriving agent knows nothing and can be handed nothing from outside — the system must explain itself
  FROM itself. Therefore: nothing hardcoded, nothing predetermined, every surface self-describing,
  every miss a teaching, every capability discoverable from inside.

## The pipeline everything serves (the real use)
```
DECONSTRUCTED RESIDUE (repo + docs + transcripts, sprawled over time)
   → INGEST into the coordinate space (supabase: entries/edges/vectors/exchanges/tool_calls/time/addresses)  ✅ built
   → IMAGE WHAT IS (structure + behavior + descriptions + provenance, composable per scope)                 ✅ axes built; the composed PRINT not yet
   → RECOVER WHAT WAS INTENDED (mine the transcripts: directives, arcs, re-approaches, the threads of
     one intention across many sessions — the INTENT AXIS)                                                  ❌ THE MISSING LAYER
   → MEASURE THE DRIFT (what-is vs what-was-intended, per thread/region — embeddings make this computable)  ❌ follows intent
   → REGENERATE by the collective (4B extract · cloud models judge/compose · Claude Code builds), through
     RESOLUTION: the intended system expressed as declarations that resolve into the thing                  ❌ the far shore
```
The models in play: the local 4B + ollama-cloud (mass extraction — the dragnet pattern, proven at 51k),
Claude Code sessions (judgment, composition, building), the embedders (the meaning substrate). The jobs/
trigger/circuit system is the collective's coordination fabric.

## THE INTENT AXIS (the named missing layer)
Everything provenance currently answers is "which conversation produced this file." It does NOT answer
"what was being ATTEMPTED." Required:
- **Intent extraction** (extraction-vs-judgment law: small models extract, a strong judge weaves): walk
  the exchanges (they're in the store with their words + the precedes/contains graph + embeddings) and
  extract intent-statements — Tim's directives, stated goals, corrections, recognitions ("yes, that").
- **Thread weaving**: the SAME intention re-approached across sessions/compactions clusters by meaning
  across time → INTENT THREADS: addressable rows (thread://… or intent:// — grammar TBD with the
  registry) carrying {the arc: first articulation → re-approaches → drift points → last state}, joined to
  provenance (which files each thread actually produced) and to time.
- **Drift measurement**: per thread/region, the computable gap between the thread's intent-embedding and
  the produced artifacts' description-embeddings. Drift is a NUMBER + evidence, never a vibe.
- **A named first target**: the VARIABLE-RESOLUTION / CONTEXT-TEMPLATE / COMPUTATION design Tim says is
  spread through the transcripts — "the other part." It is not merely content to recover; it is THE
  REGENERATION MECHANISM (resolution-first: declare typed rows + schemas that RESOLVE into the thing).
  The first intent-mining campaign targets it specifically.

## THE PRINT (the composed image — "full system-wide prints")
A PRINT = one generated artifact composing EVERY axis for a scope (a folder, a project, the estate):
what it is (structure/graph) · what it does (descriptions) · where it came from (provenance + the
conversations' words) · what it was becoming (the intent threads) · how far it drifted (the measure) ·
its state in time. The parts all exist as axes; the print is a job/cascade that walks a scope and
composes them. Prints are what the collective regenerates FROM — and what Tim recognizes against.

## How an agent actually uses this (the cold-arrival story, self-relative)
1. **Orient**: the substrate onboarding (run_start('substrate-onboarding')) + guide_search — the system
   introduces itself; response-rules inject guidance conditioned on what you touch.
2. **Ask**: the coordinate query — any question across meaning/words/graph/place/time/origin/scale;
   the plan-echo tells you honestly what ran; refusals teach the vocabulary.
3. **Understand a region**: (today) query + timeline + origin; (soon) request its PRINT.
4. **Recover intent**: (the missing rung) ask the intent axis what a region was becoming.
5. **Contribute**: register work as jobs (data rows, floor-governed); leave guides + response-rules
   behind for the next agent — the substrate accretes its own pedagogy.
6. **Regenerate**: express the recovered intent as resolvable declarations; the collective materializes.

## Laws this adds (binding on everything)
- **The transcripts are the primary text.** Any understanding pipeline that reads only code/docs is
  reading the residue and will inherit the drift.
- **Self-relative or nothing**: no capability may assume outside knowledge; every surface teaches;
  arrival-from-zero is the design case.
- **Intent is recovered, never invented.** An intent thread cites its exchanges verbatim (the words are
  in the store); a thread without citations is fiction and fails loud.
- **Prints compose axes; they never summarize from thin air.** Every leg of a print names its source
  counts (the plan-echo discipline, lifted to the artifact level).
