# MODEL-HANDOFF NOTES — things the deterministic layer can't (or shouldn't) do

*Running ledger of facts/fields that need a MODEL (the Opus interpretive layer) or would be materially better with one. Compiled while building the deterministic extractors (`ops/ledger_build.py`). The deterministic layer extracts only what is CERTAIN from a file; everything here is deferred to the model layer or a future better parser. Append as found.*

## A. The interpretive fields (model layer by design — never deterministic)
- `what_it_does`, symbol `description`/`does` — behaviour-in-meaning, not structure.
- `observations`, `standouts`, `conventions` (followed/broken), `concerns`, `notes`, `questions`, `purpose_vs_actual`.
- `apparent_themes`, `intention_signals`, `novelty` — the Tim-pattern / original-intent capture.
- `summary_for_embedding`, `intention_for_embedding` — the embedding text.
- These are the whole point of the Opus pass; listed here for completeness.

## B. Things the deterministic layer does PARTIALLY — a model would deepen
- **`stores_touched`** — deterministic catches obvious file-path/leaf writes, but "this function persists X to store Y" often hides behind a helper (`_atomic_write_fsync`, `capture_corpus`, `set_ref`). A model reading the body infers the real persistence target. *(Deterministic: shallow. Model: better.)*
- **`inputs`/`outputs` (semantic)** — deterministic gets imports/calls/returns; the *meaning* of what flows in/out (e.g. "consumes a board item, emits a decision event") is a model read.
- **TS/TSX symbol fidelity** — extracted by regex now (no tree-sitter/typescript in venv). Generics, overloads, destructured params, arrow-vs-function, JSX-component detection are best-effort. **Better deterministic option exists: a node + typescript AST bridge (node v25 is installed)** — that's a deterministic upgrade, NOT a model job. Model only needed for component *purpose*. → candidate: build a `node` TS-AST extractor later.
- **Registry-row TRUE classification** — deterministic detects module-level UPPERCASE dict assignments (`module_dicts`); deciding "this dict IS a registry row of kind X" vs "an uppercase constant" is partly a query (file under a registry dir + dict name matches) and partly a model read for edge cases.
- **Edge `to_resolved`** — resolution to the real node is deterministic (codeedges precedence) for Python; cross-language and dynamic dispatch (getattr, string-keyed handlers) need a model or are inherently unresolvable. Mark unresolved honestly.

## C. Things ONLY a model can do (cross-file / semantic — by design these are QUERIES or model passes, not extraction)
- **Duplication / "same job done twice"** — structural candidates come from queries (same write-target, near-identical signatures), but confirming two things are *semantically the same job* (the three comment stores; the two channel systems) is a model judgment over the candidates.
- **Clusters by meaning** (vs by edge-density) — edge-density clusters are a query; meaning-clusters need embeddings + a model.
- **Dead vs dormant** — no-edges-in is a query signal, but "dead" vs "intentionally-undriven / needs-tim" is a model read of the in-file markers + context.
- **State (working/partial/stub/scaffold)** — deterministic captures literal markers (TODO, "skeleton", `__main__`); the verdict is a model read.

## D. Data/prose files
- **Markdown** — deterministic gets structure (frontmatter, headings, links, wikilinks → the docs/AGENTS web). What a doc *says/means* is the model layer (and Tim's steer: agents don't re-read prose; the structure-graph is the deterministic value).
- **JSONL data leaves / large generated JSON** — recorded as data (shape + size), not deep-parsed. A model would only matter if we wanted their semantic content (usually not — they're data).

## E. Exclusions recorded (so coverage stays honest)
- This effort's own discovery scratch (`build-prep/the-one-system/discovery/pass1|pass2|_bundles*`) is excluded from the ledger denominator with reason `discovery-scratch` — it's self-referential artifact, not a built thing. Recorded, never silently dropped.
