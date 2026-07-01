# Extractor + resolver rebuild — reusable on any codebase (2026-07-01)

*Resolving every gap validated in DETERMINISTIC-PASS-GAP-ANALYSIS.md. Hard constraint (Tim): this must be **codebase-agnostic** — parameterized root/project (already `--root`/`--project`), a **portable in-process parser** (tree-sitter, pip dep — NOT the repo's node_modules), no hardcoded paths/vocab. Branch: `fix/extractor-resolver-reusable`.*

## The fixes (completion criteria — each verified by re-extract + `ops/verify_extraction/verify.py`, then proven on a 2nd repo)

- **F1 · R3 — size guard is extractor-aware.** The 800KB byte-cap protected the *regex* path from backtracking; parse-based extractors don't need it. Each EXTRACTOR declares `parse_safe`; parse-safe skips the byte cap (keeps the minified-single-line guard, since minified bundles are generated artifacts). ✅ target: `suite.py` (945KB) deep-parses.
- **F2 · R1+R2 — real-parser frontend extractor (`ops/ts_extract.py`, tree-sitter).** Replaces `ts-regex-v1`. Walks the AST for JS/JSX/TS/TSX: functions (incl nested/arrow/object-method), components, classes, methods, interfaces, types, enums, **constants** (R2), exports, imports (with relative flag), **calls** (currently absent for TS!), calls-endpoint, events. Same return-dict contract as `extract_ts`. ✅ target: jsx/js misses → ~0 in verify.py.
- **F3 · R2 — python vocabulary.** `extract_python` also captures module-level constants (UPPER / registry-dict rows) + exports as symbols/nodes. ✅ target: py constant flags resolved.
- **F4 · R4 — complete + fix the resolver (`resolve_edges`).** Add branches for `references`, `calls-endpoint` (→ route-table handler map), `emits-event` (+ a new `subscribes-event` edge kind → emitter↔listener). Make `calls` resolution **import/scope-aware** (use the file's import table, not bare-name global-uniqueness). Add **JS/TS module resolution** (relative/path imports → file). **Classify** unresolved far-ends `builtin|stdlib|external` so "unresolved" ≠ "broken". ✅ target: resolution rates up; references/endpoints/events > 0.
- **F5 · reusability — audit + prove.** No hardcoded `company`/paths beyond params; parser dependency graceful (absent → fail-loud shallow record, never silent). Run the whole pipeline on a **second repo** end-to-end.

## Division of labor (the standing principle, applied)
Completeness/structure/resolution = **deterministic code** (this rebuild). The **model** is reserved for no-oracle judgment (description accuracy, contract blind-spots), asked **pointed/bounded/fed** questions — never open-exhaustive-over-large (the dragnet's failure). The 4B coverage-audit is replaced for completeness by `verify.py`.

## Verify loop
`python ops/ledger_build.py --root <repo> --all [--load]` → `python ops/verify_extraction/verify.py` → confirm misses↓ & resolution↑ → repeat until converged. Add an acceptance test.
