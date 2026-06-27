# Wizard run-1 — Cascade Capture + Marks: Implementation Plan

**Goal:** Build the reframed per-file capture (2a) into a queryable SQLite substrate, on a registry-driven
code+AI pipeline wired as a flexible local→cloud→me cascade, then run the first three mark-passes as hypotheses —
all provenance-stamped, nothing lossy-by-single-pass, nothing auto-concluded.

**Architecture:** A tiered "query engine of a new kind" — **code (free, exact, registry-driven)** lifts structure;
**local 4B @ 32K (free, parallel)** does the per-file MAP; **cloud Kimi-K2.6 @ 256K (abundant, 6–10 parallel,
multi-turn, *different* reasoning)** does big-context REDUCE + a panel-lens with me; **me (free)** reasons/judges/
orchestrates; **Tim (scarce, special)** confirms meaning. Any tier can route to any other, multi-hop, with loops —
so single-pass lossiness is absorbed by the cascade being dynamic. Output is a queryable substrate (SQLite +
embeddings); **marks** are an open annotation layer proposed-with-evidence and confirmed by Tim, never silent.

**Tech stack:** Python (stdlib + numpy/sklearn), SQLite (JSON1), vLLM 4B @:8000 (32K), bge-m3 @:8001,
ollama `kimi-k2.6:cloud` @:11434. Workspace `~/wizard-run-1/` (ext4).

**Principles baked in:** registries not code-changes · code+AI both (free, use both) · principle/intent primary,
surface-claims unverified · semantic corroboration positive-only (rare≠wrong) · match-question-to-level
(map vs reduce) · provenance on everything · don't max the context window (judicious) · do-it-well-once.

---

## Component / file map (`~/wizard-run-1/`)
- `db.py` — SQLite schema + helpers (`files, links, blocks, marks, runs`). One writer.
- `registries/markdown_lifters.json` — declared code-lifters for markdown (extensible; add a row, not code).
- `lift.py` — registry-driven code extraction (frontmatter/wikilinks/fenced-blocks/tables + whatever the registry adds).
- `fleet.py` — the cascade call-layer: `local4b()`, `kimi()` (multi-turn capable), `embed()`; concurrency caps,
  retry, structured-output, **provenance stamping** (tier/model/pass). The reusable query-engine primitives.
- `forms.py` — the form-keyed AI capture schemas (prose-design / schema-contract / decision-card / math-proof /
  template / transcript / log-light), all sharing the reframed primary fields.
- `capture.py` — 2a orchestration: per file → lift (code) + form-keyed AI (4B, given frontmatter as context) →
  combine → write to db. Resume-safe, single-writer.
- `marks.py` — marks helpers + the three passes (A corroboration, B fingerprint, C idiosyncratic/generic), each
  emitting **proposed** marks + evidence for Tim to confirm.
- `query.py` — convenience queries/views over the db (gold / rare-flags / fingerprints / link-graph).

---

## Task 1 — SQLite substrate (`db.py`, `wizard.db`)
- [ ] Schema: `files(rel PK, form, frontmatter JSON, has_fm, principle, framing, reach, surface_claims JSON, form_specific JSON, substance, run_id)`; `links(src, dst)`; `blocks(rel, kind, content)`; `marks(id, target, mark_type, value, confidence, source_pass, source_tier, evidence JSON, status)`; `runs(run_id, kind, model, ts, params JSON)`.
- [ ] Helpers: `upsert_file`, `add_link`, `add_block`, `propose_mark`, `confirm_mark`, idempotent + single-writer.
- [ ] **Verify:** create db, round-trip a dummy record, query it back. (`python db.py --selftest`)

## Task 2 — Registry-driven code lifting (`registries/markdown_lifters.json`, `lift.py`)
- [ ] Registry rows (markdown): `frontmatter` (--- yaml ---), `wikilinks` (`[[…]]`), `fenced` (```lang→{kind,content}, detect json/sql/ts), `tables` (|…|). Each row: `{name, applies_to: md, method}`.
- [ ] `lift(path)` reads file-type → applies registry lifters → `{frontmatter (permissive, has_fm flag), links[], blocks[]}`. Never fail on missing/odd frontmatter.
- [ ] **Verify:** run on 10 varied reps (one with no frontmatter, one with json block, one with a table); inspect output is exact + complete. Confirm adding a new lifter row (e.g. `callouts`) works with **no code change**.

## Task 3 — The cascade call-layer (`fleet.py`) — [DONE; revise structured-output]
- [x] `local4b` @:8000(32K), `embed` @:8001, `kimi` @:11434 (`kimi-k2.6:cloud`, **reasoning model — needs token
  headroom + captures `reasoning` field**, cap 6–8 concurrent, judicious context — don't cram 256K), provenance.
- [ ] **REVISE: use enforced `response_format:{type:"json_schema",json_schema:{...}}`** (grammar-constrained to a
  real schema) **NOT `json_object`** (loose; freelances shape; can return empty-but-valid — likely a failure cause).
  Verified working on the 4B. `local4b` takes an optional JSON-Schema dict.

## Task 3b — Registries: forms + projections + prompts (`registries/`) — NEW
- [ ] `forms.json` — the form set (rethink: base + extensible), maps content-form → schema bucket. (Form = the
  file's *shape*, assigned by the 1.5 survey, routes the capture schema.)
- [ ] `projections.json` — the projection set (§5a of the methodology doc): each row `{name, level, produced_by
  (code|model+prompt), embeds?}`. Start with: format · temporal/lineage · topic · entities/coined-vocab · domain ·
  principle · reach · worldview · claimed-status · internal-contradiction · ai-fingerprint · completeness/part-whole
  · audience/use · open-questions · framing · investment. **No projection privileged (§5c).**
- [ ] `prompts.json` — capture/projection prompts, **versioned + reusable** (iterate-forever; the highest-leverage
  artifact). Each `{name, for_projection|for_form, text, version, notes}`.
- [ ] **Verify:** adding a form / projection / prompt row changes behaviour with no code change.

## Task 4 — Reframed capture (`forms.py`→`projections.py`, `capture.py`) — 2a, CORRECTED
- [ ] **Prompt reframe (§5/§5c):** the per-file pass **RENDERS, does not JUDGE** — strip "gold/untrustworthy/find-
  the-principle." Faithfully distil *what the file says/is* at each projection level; the gold/trust/relevance
  determination is a downstream REDUCE, not here. Capture stays multi-valued (lists, not single principle).
- [ ] **Projection-based capture:** run the registered projections (code ones via `lift`; model ones via `local4b`
  + enforced schema + the registry prompt, frontmatter as context). Substance-full / logs-light.
- [ ] **Chunk-not-truncate (§ silent-failure fix):** if a file exceeds the window → **error/branch → overlapping
  chunks → process each → record it was chunked** (never silent `read(110000)`).
- [ ] **Capture size + mtime + frontmatter-date** (code, exact) into `files` (+ schema migration).
- [ ] Write projections to db (extend schema: a `projections` table `{rel, projection, value JSON, produced_by}`
  OR columns — decide at build).
- [ ] **Verify (gate):** stratified sample → **show Tim the records** (multi-level projections, render-not-judge,
  multi-valued, chunked-where-needed, dates/size present) before the full run.

## Task 4b — Failure instrumentation + TRACE (before any retry-fix) — NEW, DISCIPLINE
- [ ] Add per-call logging: raw response, HTTP status, timing, concurrency-state, form, length → a `call_log`.
- [ ] Re-run the prose-design files (the form-concentrated failures) **with logging** → **catch a real failure in
  the act → trace WHY** (empty-200? timeout? schema-reject? length?). **Understand before any fix** (no band-aids).
- [ ] Report the root cause to Tim; only then decide if/what fix.

## Task 5 — Full capture run
- [ ] Run over all ~1,593 reps (substance-full, logs-light), 4B parallel, resume-safe, single-writer, enforced schema.
- [ ] **Verify:** counts by form/projection; error rate (should be ~0 after 3/4/4b); spot-check; db queryable.

## Task 6 — Multi-level embedding (`embed_projections.py`) — NEW, the unlock (§5d)
- [ ] Embed each embeddable projection (principle, vocabulary, worldview, topic, …) → per-projection vector sets
  (bge; restart bge @:8001, manage VRAM vs the 32K server). Store `vec://` refs.
- [ ] **Cross-level query tooling:** near-in-X / far-in-Y (the inversion-finder); per-space clustering; composed +
  **typed** relations (relation-type registry: principle-beneath/fragment-of/contradicts/sibling); prior-output-as-query.
- [ ] **Cross-session** corroboration uses the lineage projection (echoes count only across *different* sessions).
- [ ] **Verify:** the sequences↔wizard-style cross-conceptual link surfaces via near-principle/far-topic on a probe.

## Task 7 — Marks passes (`marks.py`) — A corroboration · B fingerprint · C idiosyncratic/generic
- [ ] **A:** semantic corroboration over principle-embeddings → `corroboration:N` (+ echoing rels) + `rare-flag`
  (low-N **never discounted**). **B:** AI-fingerprint (known tics + emergent generic clusters via vocabulary-space).
  **C:** idiosyncratic|generic + the **gold-likelihood profile** (corroboration × idiosyncrasy × not-tic ×
  not-contradicted), composed with evidence — a profile, not a black-box score.
- [ ] Marks are **proposed-with-evidence by any tier (provenance-stamped), confirmed by Tim — never silent, never
  privileged-routing (§5c).** Show Tim each pass's findings + reasoning → confirm → apply.

## Task 8 — LOOK + shape next (patterned visibility) — NOT pre-specced
- [ ] Query/view many ways (gold · fingerprints · rare-flags · cross-level links · link-graph seams · frontmatter
  + vocabulary clusters · part-whole fragments); **think findings out loud to Tim**; shape the next step (the
  Kimi-reduce sub-system reconstructions + the Kimi↔me panel) from what's visible. Do not pre-decide.

---

## Verification philosophy (adapted from TDD)
"Tests" here = **run-on-a-sample → inspect the real output → Tim reviews the findings.** Verify each component on a
small stratified sample before the full run; never trust a pass blind; the cascade + Tim's review are the gates.
**Understand failures (trace root cause) before any fix — no defensive band-aids.** Provenance on every
record/mark/call makes it traceable + re-runnable. Quality once > cheap many times. Prompts/schemas/registries
**iterate forever** — this is the pioneering pass; the learnings ARE the deliverable that better systems get built on.
