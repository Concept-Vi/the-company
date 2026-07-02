# The two next builds — parametric jobs + the coordinate query (Tim's direction, 2026-07-02)

*Folding the post-①②③ upgrade list into two properly-researched builds. Tim: "each will require its own
research and multi-perspective design plan — doing it right is cheaper than doing it cheaply." Nothing
built until each plan's research + design waves land and Tim recognizes the design.*

## PLAN A — the PARAMETRIC JOB SYSTEM (absorbs upgrades 1 + 5 + 6)
**Tim's frame (in substance):** the heartbeat is not a cron script — it is the first instance of a
general system of **parametric jobs agents can trigger through the MCP tools**. An **auto-run system with
configurable triggers** (change-triggers give the heartbeat; other triggers give conditional processing).
Uses beyond the heartbeat: **one-offs, targeted processing, conditional processing, generative processing,
traversal**, and more. **Every part configurable and data-driven** — prompts, allocations, parameters,
settings, outputs — melded into the systems (not a new silo).
- The heartbeat (upgrade 1: change → incremental extract → re-embed changed → joins re-derive →
  descriptions re-carry) becomes simply: a registered job graph + a change-trigger.
- Upgrade 5 (suite.py decomposition via mapped hints) and 6 (symbol descriptions, B-pass judgment tail,
  bad-json self-retry) become jobs on this system, not bespoke efforts.

**What exists to unify (the five job-shaped mechanisms, each partial):**
| mechanism | what it has | what it lacks |
|---|---|---|
| flows/ (registry rows + run(**params), MCP-invocable) | declared params, propose-only floor, discovery | no triggers, no chaining, code-authored only |
| routines/ (declared owners + prompt, timer-fired) | schedule/cadence, prompt-driven agent work | no params-as-data, no conditions, no composition |
| cascades (save_cascade — declarative chains AS DATA) | data-authored chaining | no triggers, thin vocabulary |
| graphs (run_graph over node graphs) | graph execution | not wired to triggers/params surface |
| activation (background_tick/sense_tick/rules) | the always-on caller, event-sensing, rules | rules aren't a general trigger registry |
**The design question:** one coherent system where a JOB = a data row (what to run: flow/cascade/graph/
role/agent-prompt · with what params · under what trigger: change/schedule/event/condition/manual ·
allocations/model/budget · outputs/addresses), registered + discovered + triggered through the same
MCP/UI faces. The trigger registry is the auto-run system; the heartbeat is row #1.

## PLAN B — the COORDINATE QUERY, FULL (absorbs upgrades 2 + 3)
**Tim's correction:** do 2 *fully and properly* — ALL the axes he named, not just the four I listed:
graph · vectors (multi-embedder lenses) · directory/paths · **scale** (file↕symbol↕rungs — fold upgrade 3
in: build the pyramid over code/symbol/docs/desc as part of this) · **time** · **transcript provenance**
(every unit's generating exchange) · address systems/registries · **and the recall + recollection
systems** (the session/memory axes join the same coordinate space — the transcripts are the root).
One function: a multi-axis coordinate query over the unified store, projected to BOTH MCP and UI (it is
also ③'s world-map engine — the design wave consumes it).

## PROCESS (both plans, per the north-star + Tim's "right not cheap")
1. **Research wave** (multi-agent, parallel): the existing-substrate deep-read + the external
   best-known-ways read (job/trigger/DAG systems for A; hybrid multi-axis query patterns over
   pg/pgvector for B). Counts + file:line evidence; no design yet.
2. **Multi-perspective design wave**: independent design takes over the research (≥3 perspectives each),
   judged + synthesized into ONE design.
3. **Tim recognition checkpoint** (rendered/recognizable artifacts, not spec reviews).
4. loop-prep triad → build loop (FUNCTION+FORM bars, acceptance gates).

## Sequencing
- Research waves for A and B launch NOW (parallel; read-only).
- ③'s mapping-wave synthesis + design wave continue independently; B's coordinate query and ③'s design
  wave meet at the world-map engine (B feeds ③).
- The 2 pre-existing red test classes (conv_index key-form drift, capture_lenses) get triaged inside A's
  heartbeat scope (they're staleness/key-form issues the heartbeat's contract must define anyway).
