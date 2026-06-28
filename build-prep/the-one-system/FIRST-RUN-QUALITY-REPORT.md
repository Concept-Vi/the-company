# First-Run Quality Report — the interpretive ledger sweep

*Written 2026-06-29, the first time the full interpretive sweep has ever run. Governing principle (advisor-sharpened): **fix the GENERATOR, not the generated.** Tim will re-run, so a prompt/schema/extraction/pipeline fix is durable; hand-patching individual outputs is wasted if a re-run regenerates them. Every finding below is judged by one lens: **does the Stage-1 interface (which renders this ledger) need it?***

## The headline
- **4,614 files** carry a full interpretive layer: claude-ds 295/295, counterpart-design 859/859, company 3,460/3,461 (the 1 is mid-flight rename drift — honest, not a defect).
- **Three models** produced it, all attributed with timestamps (provenance is GOOD): **kimi-k2.7-code:cloud 3,437 (74%)** · codex 618 · opus 559.
- **8,073 symbols** in the latest run; **6,322 (78%) carry per-symbol descriptions.**
- Field fill rates (of 4,614): what_it_does 100% · observations 100% · novelty 100% · summary_for_embedding 100% · purpose_vs_actual 100% · concerns 91% · proposed_edge_kinds 86% · suggested_fields 86% · **inputs 0% · outputs 0%.**

## Findings (generator-level, prioritized by Stage-1 need)

### F1 — `proposed_edge_kinds` are discovered but never promoted to edges  ★ HIGH (interface-critical)
The interpretive layer found rich SEMANTIC relationships the deterministic layer can't — `is_sub_type_of`, `quotes`, `deferred-to`, `springboards_to`, `curates-into`, `generates_code`, `operator-cycle-precedes`, `coordinates_transition_with`, `grades_provenance`… **They sit dead in a column.** The edge graph the interface renders contains only the mechanical edges (calls 28,789 · contains 5,647 · imports 4,662 · references 3,229 · capability-of 487 · …). *Evidence:* `ledger.edge` has zero rows of any proposed kind. *Why it matters:* Stage 1 renders the graph; this is a whole dormant layer of meaning. *Fix:* a harvest step that promotes proposed_edge_kinds into real (typed, provenance-stamped, lower-confidence) edges — with endpoint resolution and a review gate so they don't pollute the deterministic edges.

### F2 — JS/TS symbol-level interpretation is weak  ★ HIGH
The 22% of symbols with NO description are ~95% JavaScript/TypeScript: **1,370 JS + 287 TS + 82 Python.** *Why:* JS/TS symbols are extracted by regex (not AST like Python), so the `code_id`s the model is asked to describe likely don't match cleanly, and the per-symbol descriptions don't map back. *Why it matters:* the interface needs symbol granularity for the design-side (JSX/TSX) files too, not just Python. *Fix:* a real JS/TS symbol extractor (tree-sitter or equivalent) so code_ids are stable and describable.

### F3 — truncated descriptions aren't flagged  ★ LOW (downgraded — see audit: content is honest, only the metadata is missing)
**436 files (~9%)** exceed the 48,000-char cap (company 275 · counterpart 121 · claude-ds 40) and were interpreted on a PREFIX only. The prompt mentions truncation in the text, but **no ledger column records which descriptions are partial** — a consumer can't tell a full read from a half read. *Fix:* (a) persist a `truncated` boolean + the char-window used; (b) consider raising the cap or chunking for the long files (kimi/opus context allows more than 48k).

### F4 — `inputs` / `outputs` columns are dead (0%)  ★ LOW (decide: drop or fill)
The schema has `inputs`/`outputs` columns; the v2 prompt never asks for them, so nothing fills them. *Decision needed:* either DROP the columns (honest schema) or ADD them to the prompt — but ONLY if the interface needs "what this file consumes / produces." Note the tradeoff: the prompt already asks for 17 fields; more fields spread the model's attention and can degrade EVERY field. Empty ≠ defect.

### F5 — `suggested_fields` (schema-evolution feedback) unharvested  ★ LOW
86% of files proposed a "field that wants to exist." This is the model telling us how the schema should grow — valuable meta-feedback, currently dormant. *Fix:* aggregate + rank suggested_fields into a schema-evolution review list (feeds the schema before a re-run).

### F6 — incremental refresh ORPHANS the interpretive layer  ★ HIGH (blocks safe re-run/drift)
*(Already recorded in SCOPE.md.)* `ledger_build --incremental` writes a fresh structural snapshot with `what_it_does=NULL` for every file — running it would discard this entire sweep. **Drift reconciliation is currently unsafe.** *Fix:* `load_run` must carry forward interpretation for files whose `source_hash` is unchanged, re-interpreting only changed/new files. This is also what makes a cheap re-run possible.

## Accuracy audit (the verdict on whether the descriptions are TRUE)  ✅ PASSED
*Stratified sample of 34 (kimi 20, opus 7, codex 7; 5 truncated; py/md/jsx/ts/tsx/sql/css/html/svg/json), each read against the real file on disk by four independent auditor agents.*

**Result: 34/34 FAITHFUL. Zero hallucinated, zero embellished, zero inaccurate, zero truncation-corrupted.**
The interpretive layer is **trustworthy** — and crucially, **kimi (74% of all output) is as disciplined as opus.** Auditor observations:
- **kimi** — accurate on both extremes (4-line frontmatter stubs ↔ 660-line landscape docs); on truncated files it explicitly scoped its claims to "not visible in this excerpt" rather than over-claiming about unseen content (verified: a 1.37MB bundle and a 73KB doc both held up — every spot-checked claim was inside the model's actual window, not extrapolated from the header).
- **codex** — restrained, evidence-anchored; used `novelty: n/a` for trivial files instead of inventing significance.
- **opus** — caught fine detail a casual reader misses (dead code never called, `count(*)`-recount perf footguns, single-source-of-truth violations) and correctly labelled Inferred vs Observed.

**Implication for the truncation finding (F3):** descriptions of truncated files are *honest*, not wrong — so F3 drops from "accuracy risk" to "metadata gap" (flag the partial-read, but the content is sound).

## The one decision for Tim (recognition-level, not a dev question)
**Re-run vs. preserve.** The fixes above improve the GENERATOR. Do we:
- **(A)** apply the high-value generator fixes (F1, F2, F6) and **re-run the sweep** to get a richer ledger (semantic edges promoted, JS/TS symbols described, truncation handled) — cleanest, but spends another sweep; OR
- **(B)** keep this populated ledger as-is for Stage 1 now, and apply fixes incrementally as the interface surfaces what it actually needs; OR
- **(C)** a hybrid — harvest F1 (semantic edges) and F5 onto the EXISTING ledger without a re-run (these are additive, no regeneration), defer F2/F3 to the next natural re-run.

*(C looks strongest: it banks the interface-critical graph enrichment now without spending a sweep, and lets real interface needs drive the rest.)*

## Generator-fix worklist (recurse until empty)
- [ ] F1 — proposed_edge_kinds → edge harvester (typed, provenance-stamped, gated)
- [ ] F2 — JS/TS AST symbol extractor (tree-sitter)
- [ ] F6 — incremental carry-forward of interpretation (unblocks safe re-run + drift)
- [ ] F3 — persist truncation flag + window; raise/chunk the cap
- [ ] F5 — suggested_fields aggregation → schema-evolution review
- [ ] F4 — decide drop-vs-fill inputs/outputs
