# The POTENTIALS loop — "all of those options and potentials" (Tim's go, 2026-07-08)

*Tim: "would it be crazy if I said I wanted all of those options and potentials? Because I really do."
Every criterion verified BY USE; commit per criterion to main; coordinate with ④ (window prep gains each
landing) + Glyphic. No front-end (the window stays ④'s deferred frontier); the loop switch stays as Tim
set it (armed). New standing triggers born PROPOSED except where Tim's blanket "I really do" covers the
maintenance class (arm with the operator stamp + say so).*

## Q · THE QUERY'S NEW REACHES (ledger.query v4 — one file, one function, both faces)
- [x] Q1 TIME-TRAVEL: spec key `at` ("<timestamp>"|"run:<uuid>") — resolves the run AS OF that moment
      (started_at <= at, per project) instead of latest. VERIFIED: the same filter query at two `at`
      values returns the tree as it was then (counts differ, plan echoes the resolved run).
- [x] Q2 CROSS-PROJECT: `project` accepts "*" or a list — the candidate/filter/count stages union across
      each project's own latest (or `at`-resolved) run. VERIFIED: one query returns company + claude-ds
      results, project attributed per result.
- [x] Q3 PROVENANCE-BY-DEFAULT: `origin: true` spec key — every result carries its latest generated-by
      exchange (address + ts + a text snippet when indexed). VERIFIED on a known-provenance file.
- [x] Q4 the golden gate grows to cover Q1-Q3 (+ refusal shapes); re-run GREEN.

## S · SAVED QUERIES (questions as addressable, watchable things)
- [x] S1 a saved-query REGISTRY (ActionRegistry rows: id, label, spec, created_by) + `coordinate` tool ops
      save/list/run-by-id; VERIFIED round-trip.
- [x] S2 the `watch_query` jobs HANDLER: run a saved query, fingerprint its result-set (addresses), diff vs
      the last fingerprint (state json), and on CHANGE file a board note naming what appeared/vanished.
      VERIFIED: a watched query + a planted change → the note appears; no change → silent.
- [x] S3 a real standing watch registered as a job (schedule trigger; born proposed → armed under Tim's
      blanket with the stamp). VERIFIED via jobs status + a tick.

## M · MODEL RUNS AS JOBS (the run-kinds Tim named)
- [x] M1 run-kind `role`: {role, op?, model?, inputs-from-params} through the EXISTING run_role path
      (registry-validated at define; budget honored). VERIFIED: a job fires a real role run end-to-end.
- [x] M2 run-kind `flow`: {flow, params} through the flows registry (proposes_only floor intact).
      VERIFIED with a real flow.
- [x] M3 the worked GENERATIVE example: "re-describe changed files" as ONE registered job — selector
      (changed_since watermark) → describe role over each → durability sync — runnable manually, armable.
      VERIFIED on a real changed-file set.

## C · CONDITIONAL TRIGGERS (when-X-do-Y as data)
- [x] C1 trigger kind `condition`: config = {sql: "<a SELECT returning one number>", op: ">"|">="|…,
      value: N, cursor?: bool} — evaluated on the tick as a cheap predicate (never a resident poller);
      fires when true; watermark/cursor semantics so one event fires once. Guardrails: read-only SQL
      (regex-refuse non-SELECT), timeout, teaching refusals. VERIFIED: a condition on a real count fires
      once when crossed, then stays quiet.

## E · EMBEDDINGS AS AN OPERABLE SURFACE
- [x] E1 the `embeddings` MCP tool: op=spaces (each space: units, dims, lenses, pyramid rungs, freshness) ·
      op=route (the lens table) · op=build (run a space's builder via the jobs/handler path — proposes/
      fires bounded) · op=pyramid (rebuild rungs for a space). VERIFIED by use on a small space.
- [x] E2 `company embed` CLI verb — the same status + build faces in the terminal. VERIFIED.
- [x] E3 embed-build registered as jobs handlers (build_space, already-have rebuild_scale_pyramids) so
      every embed operation is schedulable/watchable like everything else.

## P · PARITY + FACES + CLOSE
- [x] P1 `company timeline <file>` — the authorship timeline in the terminal (generated-by + file_meta +
      conversation snippets where indexed). VERIFIED on runtime/jobs.py.
- [x] P2 parity sweep recorded: a table (capability × MCP × CLI × HTTP) in docs; gaps named honestly.
- [x] P3 golden gates re-run (ledger_query + jobs-touching suites) GREEN; STATUS.md + board note; ④+glyph
      pinged with the new spec keys + tool ops; working tree clean.

## Order: Q1→Q4 (one file) → S1→S3 → M1→M3 → C1 → E1→E3 → P1→P3.
## Mechanics: verify-by-use per criterion; ScheduleWakeup self-paced; agents for parallelizable lanes
## (E is file-disjoint from Q/S/M — a briefed agent can build E while I do Q/S/M); fail-loud everywhere.
