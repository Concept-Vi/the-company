# Deterministic-pass gap analysis — what to fix before the rerun (2026-07-01)

*Task 1 of Tim's three (fix+rerun deterministic → embeddings → UI). Built by querying the dragnet (`ledger.coverage_findings`) AND validating every claim against ground truth. Tim's charge: broad coverage, reason, push back, self-correct — no one else checks this. So this doc is explicit about what is **verified-real** vs **dragnet-noise** vs **my-own-artifact**, because the raw dragnet says "97% of files broken" and that number is misleading.*

## The dragnet, characterised honestly
`ledger.coverage_findings` = the local-4B objective-verifier pass over the deterministic extractor, per code file (1,304 rows, run 2026-06-30). It is **raw and first-run**, and it must be read critically:
- **50 rows are stale `oversize` skip-records** — files it never actually audited (pre-fix guard). True audited set ≈ 1,254.
- **It over-flags Python.** Headline "96% of .py flagged / 1,032 missing functions" is **largely 4B noise** (see G-NOISE-1). Its `name` fields are frequently empty — flags are coarse.
- **It is a trustworthy signal for JS/JSX** (its flags there are corroborated 3 independent ways) and a **noisy signal for Python** (contradicted by ground truth). Reliability is language-dependent — do not drive the rerun off its raw counts.

## VERIFIED-REAL gaps (fix these)

**R1 — JS/JSX/TS/TSX symbol extraction is weak/blind.** Dragnet flags functions (639 jsx, 363 js, 291 ts, 256 tsx) + components (193+162 jsx). Corroborated independently: company `.jsx` has **0 stored symbols, 0 interpretive descriptions, 97/97 graph-orphans, 0 reachability**. The regex frontend extractors miss components-referenced-in-JSX, `window.*` assigns, hooks, arrow-fn components. → **Replace regex JS/TS extraction with a real parser (AST via a JS/TS grammar), not regex.** Highest-leverage: the frontends are both the merge target and the blind spot.

**R2 — the symbol vocabulary is too narrow (all languages).** The extractor's symbol kinds are only function/method/class/type/component. It captures **no constants (1,848 py flagged), no module-constants (308), no imports-as-nodes (~940), no exports (~430), no interfaces/variables**. These dragnet flags are *correct* — the extractor never tried. → **Widen the vocabulary**: constants, exports, interfaces, and imports as first-class symbol/edge targets (imports-as-nodes also helps R4).

**R3 — the size-guard void at the kernel.** `runtime/suite.py` is **945KB / 12,776 lines**, over the `_MAX_TEXT_DEEP=800,000` guard, so the latest run stored **0 symbols, 0 edges** for the single most-imported file (154×). The kernel is a hole; the RHM chat path dies there. → **Chunk-parse oversized files** (don't skip) or raise+stream the guard. Non-negotiable: the center must be in the map. (Also a smell worth surfacing to Tim separately: a 12.7k-line kernel is itself an architecture problem.)

**R4 — the half-edge / resolution gap (NOT measured by the dragnet — my finding).** The extractor records what a file *reaches toward* but rarely resolves the far end: **calls 27.5% land, imports 20%, references 1.1%, calls-endpoint 0%, emits-event 0%** (subscribers have no edge kind at all), uses-capability 2 of 487. Six separate symptoms, one cause: **no resolution pass.** → Add: call→def / import→module / reference→target resolution *with far-end classification* (internal | stdlib | external | builtin, so builtins aren't false "broken wiring"); an **endpoint→handler resolver** (heals the frontend↔backend seam); a **`subscribes-event` edge kind** + subscriber resolution; and run the AST capability-deep-link across all code (not just the codex producer).

**R5 — staleness (architectural, not a bug).** All 10 deterministic runs are **June-27**; today is July-1. Confirmed live: `cognition.py` ledger=50 fns vs real=51 (the `active_brain`/`_chat_brain_cfg` work postdates extraction); **63 new code files never indexed**; the dragnet is equally stale. → The rerun fixes the snapshot, but structurally the ledger must become **incremental/live** (source_hash-driven refresh), or it will re-stale immediately. This is the deepest one — a static self-model cannot coordinate live building.

## Dragnet validity map (VERIFIED at full population, 3 instruments: grep → AST → git-historical)

**The principle:** the dragnet's flag-validity is *inversely proportional to how well the deterministic extractor works for that language.* Good extraction (py) → the 4B **over-flags** (invents discrepancies against correct data). Blind extraction (jsx) → the 4B is **accurate** (everything really is missing). Calibrate trust per-language.

| language | extractor stored | dragnet flags | validity of the flags |
|---|---|---|---|
| **py functions/classes** | complete (715/738 exact; real=ledger at extraction) | ~1,200 | **INVALID** — 0 real extractor misses. The 450 def-deltas = suite.py void (393, R3) + staleness (57, R5). Verified: at the June-27 commit every file's AST == ledger. |
| **py const/import/export** | not captured (vocab) | ~1,900 | **VALID** — real R2 vocab gap. |
| **jsx (all)** | **0 symbols, all 97 files empty** | 1,641 | **100% VALID** — total blindness; everything flagged is genuinely missing. |
| **js** | 246 sym, 65/86 files empty | 1,063 | **mostly VALID** (75% of files captured nothing). |
| **ts / tsx** | 657 / 315 sym (partial) | 960 / 659 | **MIXED / UNRESOLVED** — partial capture, so flags blend real-miss + vocab-kinds + possible-noise. **Cannot split without a TS AST parser** (a tool we don't have — see R4/needed-tooling). Do NOT assume these counts are all real. |

Consequence for the rerun: **do not drive py function/class fixes off the dragnet** (0 real bugs there — you'd chase ghosts and risk breaking correct extraction). DO trust the jsx/js flags. Treat ts/tsx as unknown until a real parser adjudicates.

## NOT real — ruled out by ground truth (do not chase)

**G-NOISE-1 — "1,032 missing py functions" is dragnet noise (VERIFIED full-population).** At the June-27 extraction commit, every py file's AST FunctionDef count == ledger function+method count (715/738 exact today; the 23 deltas are 20 staleness + suite.py void + 1 new file — **0 genuine extractor misses**). `fs_store.py` 89==89 with only 2 top-level defs proves nested defs ARE captured. Python function/class extraction is **sound** — leave it alone.

**G-ARTIFACT-1 — "281 phantom files" is a comparison artifact.** They exist on disk under `design/claude-ds/` and `recollection/` — separate git repos not listed by company `git ls-files`. NOT deletion-drift. (Retracted mid-analysis.)

## VERIFIED via the durable verifier (`ops/verify_extraction/`, 2026-07-01)
Real parse-tree ground truth (python `ast` for .py, the TypeScript compiler API via `ts_symbols.js` for the rest), set-diffed against `ledger.symbol`. Reproduces the adjudication and is **repeatable** (`python ops/verify_extraction/verify.py [--list-misses]`):

| ext | files | complete | files-with-miss | real misses | void (0-captured) | what the misses ARE |
|---|---|---|---|---|---|---|
| .py | 738 | 716 | 22 | 447 | 1 | **0 extractor bugs** — 393 = suite.py void, ~54 = staleness (proven via git-historical AST) |
| .tsx | 80 | 77 | 3 | 10 | 0 | extractor is **good**; dragnet's tsx flags ~97% noise/vocab |
| .ts | 138 | 116 | 22 | 28 | 15 | extractor **good**; 15 files got nothing (worth a look) |
| .js | 86 | 46 | 40 | 801 | 38 | **genuinely broken** — dragnet flags VALID |
| .jsx | 97 | 1 | 96 | 888 | 96 | **blind** — dragnet flags VALID |

**Corrected R1 scope:** the frontend extractor problem is **JS + JSX specifically** (~1,689 real misses), NOT TS/TSX (38 — those work). Earlier "the frontends are blind" was over-broad twice; the canvas TypeScript app is captured, the surface `.js` gallery and `.jsx` are the hole.

**Reliability caveat of the tool:** `verify.py` compares current disk vs the (stale) ledger, so its raw "misses" conflate extractor-bug + staleness + void. To auto-separate them it needs a `--at-commit` mode (compare against the extraction-era file); until then, the py "0 bugs" split was done by hand (git-historical). Miss counts are a conservative FLOOR (leaf-name matching + undercounted exotic component patterns).

## Needed tooling (functions we don't have, that this validation required)
- **A real JS/TS AST parser** — to (a) fix R1 extraction and (b) *adjudicate the ts/tsx dragnet flags*, which are currently unknowable. Without it, ~1,600 ts/tsx flags stay uncategorised.
- **A staleness/liveness check** (`is_current(entry)` vs disk) — this analysis had to hand-roll git-historical AST to separate staleness from bugs; the ledger can't tell you what's stale.

## Still under-covered (honest gaps in THIS analysis)
- Extraction quality of non-code files (.md/.html/.css/.json) not assessed — out of the "code" focus, but the ledger indexes them.
- Whether `design/claude-ds` is double-indexed (project=company AND project=claude-ds) — a possible exclude-prefix failure, noted not verified.
- The dragnet's own Python over-flagging cause (audit-prompt? schema?) — worth understanding before re-running the dragnet post-fix.

## Rerun sequence (proposed)
1. Fix R2 (vocabulary) + R3 (chunk-parse) — cheap, high-coverage.
2. Fix R1 (real JS/TS parser) — the big one; unblocks the frontend merge.
3. Add R4 (resolution pass) — turns half-edges into a real graph.
4. Re-run deterministic over the current tree (fixes R5's snapshot); re-run the dragnet to confirm convergence — and this time **trust the language-specific reliability** (believe its JS/JSX flags, verify its py flags).
5. Make it incremental (R5 architectural) so it stops re-staling.
