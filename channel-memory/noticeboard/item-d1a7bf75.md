---
id: item-d1a7bf75
address: board://item-d1a7bf75
type: request
source: claude_code
state: open
title: 'SPEC: whole-repo code-archaeology DRAGNET (coverage-complete, tiered, queryable,
  incremental) — gates the provider-registry decisions'
author_session: ch-3mpkjg3r
channel: provider-registry
thread: ''
links: []
created: '2026-06-22T10:07:41.288915+00:00'
updated: '2026-06-22T10:07:41.288915+00:00'
history:
- from: null
  to: open
  by: ch-3mpkjg3r
  ts: '2026-06-22T10:07:41.288915+00:00'
  note: filed
---

Buildable spec for the coverage-complete code-archaeology dragnet (Tim direct: WHOLE repo, no spear/bias, don't reduce coverage to save effort — local is free; make it as GOOD as the system allows, not the first pass that works). Built on recollection's extract-once dragnet engine applied to CODE FILES. DESCRIPTIVE-ONLY (record what IS in each file, zero architectural opinions). Decisions (extend/redesign/home) come ONLY after full coverage is proven.

1) OUTPUT STORE + ADDRESS + MCP SURFACE
• Store: the FsStore (same substrate corpus/recall use) — a dedicated space `code_archaeology`. Records are EMBEDDED (semantic-queryable) AND structured (field-queryable) — dual.
• Address: each file's record at `code://<rel_path>` (resolve_address resolves it); the coverage ledger at `code://_ledger`.
• MCP read surface (no new tool — rides the existing): `corpus op=query space=code_archaeology` (semantic) · `inspect_address code://<path>` (one file) · `list_by_type` / `layers` (enumerate/shape). Queryable later by the synthesis pass + any agent.

2) RECORD SCHEMA (tiered = resolve(grain), reuse recollection's coarse/fine)
• COARSE (every readable file): {rel_path, language, kind(module|config|doc|test|data|script|asset), what_it_is(one neutral phrase), top_symbols[defs/classes/exports], imports[], declares[sentinels/registry-rows it defines], loc, fingerprint(sha256)}.
• FINE (code-bearing): {per_symbol[{name,kind,describes(neutral),reads[stores/registries/files],writes[],calls[]}], cross_refs[], registry_touchpoints(descriptive: "registers via SENTINEL into X" — NOT "this IS the registry")}.
• STRICT descriptive-only; structured Pydantic (fail-loud), never free text.

3) COVERAGE LEDGER (first-class = the proof)
• Enumerate FIRST: `git ls-files` + `git ls-files --others --exclude-standard` = the DENOMINATOR (every file).
• Per-file row: {rel_path, state(enumerated|processing|done|skipped|failed|excluded), reason, chunks, record_address, fingerprint, ts}.
• FAIL-LOUD: denominator == Σ(states); any unaccounted file = a loud Notice + gap-note (no silent drop). Coverage% = done/(denominator − excluded). Ledger is itself addressable/queryable.

4) RE-RUN / CHANGE HANDLING
• sha256 per file. Re-run re-describes ONLY changed files (sha differs) + new (mark deleted) — incremental, never full-redo (the X12-FAST signature pattern). Ledger fingerprints drive the diff.

5) MODEL CAPACITY — BEST, not minimal
• 32-concurrent local chat-4b (:8000, think=false for description, free) via run_items (~7-10/s proven). Whole-repo = the wasteful-is-the-feature full run.
• BEST = tiered depth (coarse+fine) · structured+embedded (dual-queryable) · NEUTRAL extraction (recollection's neutral-judge law — describe, never filter/judge relevance) · chunk large files (no truncation) · fail-loud on unparseable (logged). NOT: flat one-liners, sampling, opinions, free text.

6) SYNTHESIS (phase 2, gated on coverage)
• Only after the ledger proves full coverage → a DETERMINE pass reads the per-file records to MAP the registry/provider/capability landscape → THEN the extend/redesign/home calls. (This demotes the earlier Explore inventory + board://item-9b12c1af's "3-move" to hypotheses pending THIS.)

EXECUTION/RESOURCING: a dedicated provider-registry-lane session builds+runs it on recollection's dragnet engine (sibling space to the corpus extract). ⚠ shares chat-4b with the corpus bake firing now → SEQUENCE (corpus bake first) or concurrency-share (slower); lead coordinates the model contention. On Tim's confirm of this spec, lead spawns the build-session.

---

## AMENDMENT (fork, 2026-06-22) — hardening + PRIMITIVE elevation

Full design: `build-prep/the-one-application/CODE-ARCHAEOLOGY-DRAGNET-DESIGN.md` (engine-grounded, advisor-checked).

**ELEVATION (Tim via ChatGPT):** this is a REUSABLE BUILD-PREP PRIMITIVE, not a provider-registry one-off — the fix
for "agents sample → get confident → build from partial info" (the recurring failure). A coverage-complete, queryable
map you run/refresh BEFORE a significant build, then synthesize from. ★ DISCIPLINE GUARD: design general/cross-project
SEAMS, but PROVE on the company repo first; do NOT speculatively build cross-project comparison before a 2nd repo.

**4 hardening reqs — resolved (verified, not assumed):**
1. REUSABLE ADDRESSING — `code://<project>/<rel_path>` (project-first, no cross-repo collision) + `#run=<id>` version
   key; symbols nest `code://<project>/<stem>/<symbol>`. Mirrors `decision://`/`run://` grammar; add
   `parse_code_address`+canonicalizer to contracts/address.py. Reconciled with the legacy `code://<stem>/<symbol>`
   resolver = ONE scheme.
2. SPACE REGISTRATION — a space is a ProjectionRegistry entry with `embeds:True`; `embed_corpus_to_spaces` FAILS LOUD
   on an unregistered space (cognition.py:522). MUST create `projections/code_archaeology.py` (precedent: repo.py).
   NOT assumed-works.
3. FIELD-QUERYABILITY — semantic search does NOT answer "all files writing FsStore" / "all roles" / "all failed".
   VERIFIED no existing surface does (data is in cas:// blobs). BUILD a structured field-index reusing the marks-layer
   pattern (marks_by_type). ★ REGISTRY/TYPE DISCOVERABILITY first-class: index `declares[]` so registries+rows, node
   types, roles, panels, flows, projections, provider/model registries, MCP tools, address schemes are queryable.
4. MANIFEST HYGIENE — board item + design doc kept attached as the build proceeds.

**Also folded:** PARSER-FIRST (deterministic structural facts via AST/regex; LLM for prose only — resolves the
chunk/file granularity + protects the synthesis map from hallucinated imports). Engine reuse = SIBLING
`ops/code_archaeology.py` reusing `cog.run_items` (lead-settled; no touch to the live `dragnet_extract.py`).

Build held for Tim's scope-confirm of THIS elevated spec + the lead's chat-4b contention clearance.
