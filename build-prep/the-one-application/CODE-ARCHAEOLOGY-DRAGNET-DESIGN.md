# Code-Archaeology Dragnet — Design (reusable build-prep PRIMITIVE)

**Spec:** `board://item-d1a7bf75` (+ this doc is the amended, engine-grounded design). **Status:** PRE-POSITIONED;
RUN gated on Tim's scope-confirm (via ChatGPT) + the lead's chat-4b contention clearance. **Lane:** fork. **Seam:**
SIBLING `ops/code_archaeology.py` reusing `cog.run_items` (lead-settled — isolate from the live corpus bake;
generalize-`run_extract` is recollection's post-bake consolidation). **Law:** descriptive-only; coverage is the
proof; decisions only AFTER full coverage.

---

## WHY (the elevation — Tim via ChatGPT)

This is NOT a provider-registry one-off. It is a **reusable build-prep PRIMITIVE** that fixes the session's recurring
failure: *agents sample → search a few likely places → get confident → build from partial info* (bit the keystone 5×).
The dragnet is the antidote: a **coverage-complete, queryable map you run/refresh BEFORE a significant build, then
synthesize from.** Search-confidence ≠ coverage. So the deliverable is a PRIMITIVE + a TEMPLATE/GATE, proven first on
the company repo.

**★ DISCIPLINE GUARD (the primitive must not itself be an over-build-from-partial-info — the irony):** DESIGN the
general/cross-project seams right (addressing, space, registry-discoverability), but PROVE on THIS ONE repo first
(coverage-complete on `company` = the proof). Do NOT speculatively build the cross-project-comparison machinery before
a 2nd repo exists — **design the seam, prove on one, extend when the 2nd arrives.** Verify-by-use applies to the
primitive too.

## 0. DENOMINATOR (measured — company repo)

`git ls-files` (1526) + `--others --exclude-standard` (125) = 1,651 files in the GIT view. **683 `.py` (41%)** · 576
`.md` · 133 `.json` · 126 JS/TS · rest tiny. Most files small → ONE unit each.

**★ COVERAGE-CORRECTNESS (DNA's catch, 2026-06-22 — the denominator is the REAL FILESYSTEM TREE, not the git view):**
git-ls-files SILENTLY OMITS git-ignored dirs — and those can hold the REAL foundation. Proven on the counterpart/design
instance: `reference/` (104MB / 760 files — the actual ConceptV design-system CSS: colors_and_type.css, deck.css,
workshop.css, _ds_manifest, SKILL.md) + `source/` (237MB / 174 files — brand assets + deep conceptual docs) are
git-ignored → a git-ls-files denominator reports "643 tracked files" and DROPS the entire design system. That is
EXACTLY the "structure exists but agents don't find it → re-derive shallow" failure this primitive exists to KILL — so a
git/registry-filtered denominator reintroduces the very blind spot. ⟹ enumeration walks the **real filesystem tree**
(git-ignored content dirs INCLUDED; the substrate scan's `SKIP_TOP`/registry-skip OVERRIDDEN), with an explicit
include-list for the git-ignored dirs that carry real content (design `source/`+`reference/`), and excludes only true
junk (binaries/caches/node_modules) with a loud per-exclusion reason. The git view is a HINT, never the coverage bar.

## 1. Engine reuse (scouted, evidence-grounded)

**SHARED ENGINE = `cog.run_items(role, items, store, *, turn_id, max_tokens)` → `ItemsResult{.resolved{i:dict}, .failed}`**
— the 32-concurrent runner, source-agnostic, per-unit fail-soft. Reused directly; `run_extract`'s coarse→gate→fine→merge
is the PATTERN mirrored in the sibling. chat-4b @ :8000, think=false (the contention the lead coordinates).

## 2. ★ PARSER-FIRST (quality refinement of the spec — fork's technical call)

Structural facts (`top_symbols, imports, declares`) are EXACT from a parser and **hallucination-prone from an LLM** —
and phase-2 synthesis maps the registry/provider landscape FROM them, so an invented import silently corrupts the map.
"As GOOD as the system allows" ⟹ deterministic-first IS the mandate. Split by source:

| field | source |
|---|---|
| `rel_path, language, kind, loc, fingerprint(sha256)` | deterministic (fs + ext + heuristic) |
| `top_symbols, imports, declares[registry-rows]` | **PARSER** — Python `ast` (683 files, exact); regex for JS/TS·sh·sql; keys for JSON; none for md; byte-chunk+LLM fallback for the tail (logged) |
| `what_it_is` (coarse), `per_symbol.describes` + `registry_touchpoints` prose (fine) | **LLM** (run_items) |

**Resolves the granularity mismatch (engine is chunk-native, spec is file-native):** parser gives whole-file structure
(no chunk→file merge of symbols/imports); the LLM unit is the FILE (`what_it_is`) or the SYMBOL (fine `describes`),
never a byte window — the natural code chunk is a symbol/definition, feeding `per_symbol` directly, no mid-function
truncation. One file → one record + one ledger row.

## 3. ADDRESSING — reusable across repos + runs (VERIFIED grammar; #1 hardening)

`code://` exists (`contracts/address.py:144` SCHEMES). The grammar supports multi-segment + fragments (mirror
`decision://<frame>/<id>` + `run://…@<branch>#run=<id>`). **Form (general, collision-free):**
- FILE record: **`code://<project>/<rel_path>`** (project-first → no cross-repo collision; `rel_path` carries the
  extension, e.g. `code://company/runtime/suite.py`).
- SYMBOL: **`code://<project>/<stem>/<symbol>`** (nests under the file; coexists with the LEGACY
  `code://<file-stem>/<symbol>` ui→code→scope resolver).
- RUN/VERSION key: **`#run=<run-id>`** fragment (mirrors `run_address`'s `#run=`) so re-runs/versions don't collide.
- **BUILD:** add `parse_code_address` + `code_address` canonicalizer to `contracts/address.py` (decision:// precedent),
  declared ONCE. `store.space_address(addr, space)` already namespaces by `#space=` (collision-free across spaces —
  no store change). ⚠ DISAMBIGUATION (flag recollection/lead, confirm ONE scheme): `code://suite/review_verdicts`
  (legacy stem/symbol) vs `code://company/suite/review_verdicts` (project/stem/symbol) differ only by whether segment-1
  is a project or a stem — an extension/heuristic CANNOT tell reliably. Use an EXPLICIT marker (a frame like
  decision://'s, or the `#run=` presence), NOT a heuristic — settle the marker with recollection before building the parser.

## 4. SPACE — must be REGISTERED, not assumed (VERIFIED; #2 hardening)

A space is a `ProjectionRegistry` entry with `embeds:True` (`runtime/projections.py:244`); `embed_corpus_to_spaces`
**FAILS LOUD** on an unregistered space (`runtime/cognition.py:522`). Precedent: `projections/repo.py` was created for
exactly this. **BUILD:** create `projections/code_archaeology.py` `PROJECTION={id, level:content, produced_by:code,
embeds:True, field:text, desc}` + a row in `projections/AGENTS.md` (drift-home) + rediscover → then
`corpus op=query space=code_archaeology` works (verify by-use, not assumed). Records embed via the normal
capture→`embed_corpus_to_spaces` lane (default `emb=pplx`, both write+query layers match).

## 5. FIELD-QUERYABILITY — must be BUILT (VERIFIED; #3 hardening — the registry-discoverability spine)

Semantic search ≠ "all files writing FsStore" / "all files declaring a role" / "all failed files". Observed (subagent
code-read, to re-confirm BY-USE at build): NO existing surface (find_corpus scans 4 fixed fields; list_by_type is the
node-type graph; inspect_address is per-address; FsStore is content-addressed, not relational) answers field-queries —
the structured data sits in cas:// blobs, address-only. **BUILD a structured index that reuses the marks-layer PATTERN
(append-only jsonl + read-time linear scan) in a DEDICATED SIBLING store under the `code_archaeology` namespace with
its OWN read surface — NOT the shared `marks.jsonl`/`mark_types/` registry.** ⚠ This is the right reading of
reuse-don't-parallel here: `imports`/`writes`/`declares` are NOT cognition mark-types (adding them to `mark_types/`
pollutes the vocabulary + fails `mark_types_acceptance`; writing them unregistered violates registry-is-truth), AND at
1,651 files × dozens-to-hundreds of field-records each that store would add 100k+ lines that EVERY `marks_by_type` call
(decisions/findings/cognition) then linear-scans. So: the PATTERN, in a separate namespaced file + read surface:
- During extraction, emit typed field-records per file: `{target: code://<project>/<rel_path>, field, value}` for the
  queryable fields — `imports`, `writes`, `reads`, `calls`, `declares` (registry-row), `registry_touchpoint`, `kind`,
  `language`, ledger `state`. A read surface `code_archaeology(by=field, value=…)` linear-scans the index.
- **★ REGISTRY/TYPE DISCOVERABILITY FIRST-CLASS (the elevation's core):** the parser's `declares[]` detects when a file
  IS a registry-row (a `ROLE`/`PROJECTION`/`MARK_TYPE`/`NODE_TYPE`/`DECISION` dict, a flow, a panel, a provider/model
  entry, an MCP tool, an address scheme) → indexed so "all roles" / "all MCP tools" / "all projections" / "every
  registry + its rows" / "all address schemes" are first-class queries. This is the fix for *structure-exists-but-
  agents-don't-find-it*. (The repo's registries are file-discovered dirs — `roles/`, `projections/`, `mark_types/`,
  node-types, `decisions/`, flows, panels — so a file's dir + its declared sentinel IS its registry membership.)

## 6. The cascade (`ops/code_archaeology.py`)

1. `enumerate()` — walk the REAL FILESYSTEM TREE (NOT git-ls-files-only — §0 coverage-correctness): the git view UNION an explicit include-list of git-ignored content dirs (design source/+reference/), SKIP_TOP/registry-skip overridden = the DENOMINATOR; classify readable/binary/excluded (loud per-exclusion reason; exclude only true junk — binaries/caches/node_modules).
2. STAGE 0 — PARSER (deterministic, per file): language·kind·loc·fingerprint + top_symbols·imports·declares (§2). The structural data lands in the M1 record; the field-INDEX write over it (§5) is M2 (decoupled — does not gate the coverage proof).
3. STAGE 1 — LLM COARSE (run_items, per file): `what_it_is`. chat-4b, think=false. Merged onto the skeleton.
4. STEP-GATE: code-bearing (parsed symbols / kind∈{module,script}) → FINE; config/doc/data/asset → coarse-only.
5. STAGE 2 — LLM FINE (run_items, per SYMBOL of gated files): `describes` + reads/writes/calls + registry_touchpoints. Records at `code://<project>/<stem>/<symbol>`.
6. MERGE → store: one record per file at `code://<project>/<rel_path>` (structured) + embed into `code_archaeology` space (§4) + the field-index (§5).
7. LEDGER (`code://<project>/_ledger`, first-class): per-file {rel_path, state, reason, chunks, record_address, fingerprint, ts}. FAIL-LOUD: denominator == Σ(states); unaccounted file → loud Notice + gap-note. coverage% = done/(denominator − excluded).
8. INCREMENTAL: sha256 in the ledger → re-describe only changed/new; deleted marked (X12-FAST signature).
9. READ SURFACE: `corpus op=query space=code_archaeology` (semantic) · `inspect_address code://<project>/<path>` (one) · the field-index read (§5, structured) · the ledger (coverage).
10. SYNTHESIS (phase 2, gated on FULL coverage): a DETERMINE pass reads the records → maps registry/provider/capability landscape → THEN extend/redesign/home. The TEMPLATE/GATE: *before a significant build, run/refresh the relevant map → synthesize from it.*

## 7. MILESTONES (the discipline guard applied to the primitive's OWN build)

The lead's "prove on company first" = a sequenced first milestone. Decouple the COVERAGE PROOF from the reusable-
primitive elaborations so a bug in the latter can't block the former (the irony-guard: the primitive must not itself
over-reach before its core is proven).

- **M1 — COVERAGE PROOF (the milestone the lead asked for):** enumerate → addressing (`parse_code_address`+canonicalizer,
  §3) → registered space (`projections/code_archaeology.py`, §4) → STAGE-0 parser + cascade + merge → per-file record at
  `code://<project>/<rel_path>` → **ledger at 100%** (§6.7, fail-loud denominator==Σstates). These are PREREQUISITES
  (can't store/embed without addressing+space). Done ⟺ the company repo is coverage-complete + every record readable by
  address + semantically queryable. This is the proof; it does NOT depend on the field-index.
- **M2 — REUSABLE-PRIMITIVE LAYER (fast-follow, decoupled):** the structured field-index (§5, sibling store) + the
  registry/type-discoverability read surface. The parser already produces the structural data in M1; M2 is the INDEX +
  READ over it. A bug here cannot block M1's coverage proof. Verify by-use (write a field-record → query it back).
- **M3 — CROSS-PROJECT (designed-not-built):** comparison machinery. The seam = `<project>` is already the address/space
  key, so a 2nd repo slots in without rework; the comparison reads are DEFERRED until a 2nd repo exists. NO speculative build.

## 8. To flag / open gates
- **Lead/recollection:** the PARSER-FIRST refinement (§2, fork's call, FYI); the `code://` legacy-vs-archaeology disambiguation (§3, confirm ONE scheme); the field-index-via-marks-pattern (§5) as the structured surface.
- **Manifest hygiene (#4):** keep `board://item-d1a7bf75` + this doc attached to the channel as the build proceeds (not optional).
- Tim: scope-confirm of the elevated spec. Lead: chat-4b contention sequencing. Design advisor-checked before build; build held for the go.
