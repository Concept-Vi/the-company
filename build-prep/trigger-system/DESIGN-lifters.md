---
type: design
module: lifters
topic: deterministic-extraction-layer
status: draft
relates-to: ["[[lifters — constitution]]", "[[projections — constitution]]", "runtime/lifters.py", "runtime/corpus.py", "runtime/suite.py"]
written: 2026-06-17
epistemic-note: design draft, written with deliberate tentativeness — assumptions + source refs inline; correct directly. Nothing here is built; this is the design only.
---

# DESIGN — the deterministic-extraction layer (the "lifters")

**One line:** a lifter captures the structural facts of a file *by code, not by asking the model* —
so a corpus record = **deterministic structure (lifter)** + **open-ended description (model digest)**,
and the reliability principle holds: *never ask the model to enumerate what code can extract exactly.*

> Tim's flag carried through this design: **do not limit to imports/exports** — that was one example
> of a whole category (every enumerable structural fact, per file type). The registry is designed
> OPEN so the set grows by dropping a file, never by editing a list.

---

## 0. What exists today, and the one thing that is missing (Observed)

The lifter **mechanism** is built and tested; the lifter **wire into capture is not connected.** Both
facts are load-bearing for this design, so they are stated as Observed evidence:

- **The registry mechanism is built** — `runtime/lifters.py:131` `LifterRegistry` (file-discovered,
  mirrors `ProjectionRegistry`/`RoleRegistry`/`NodeRegistry`), with `for_projection(pid)`
  (`runtime/lifters.py:167`) and `as_records()` (`:175`). Three seed lifters exist:
  `lifters/frontmatter.py`, `lifters/links.py`, `lifters/blocks.py`.
- **It is discovered and surfaced** — `runtime/suite.py:332` discovers it; `:5998` passes it to
  `build_cognition_info`. So the operator can SEE the lifter set; nothing CONSUMES it to produce a record.
- **No capture path calls any lifter.** Grepped repo-wide: the ONLY `.extract(` / `for_projection`
  callers are `tests/lifters_acceptance.py`. `ingest_paths` (`runtime/suite.py:10474`) writes
  `output=dig` (the model digest) and never attaches lifter output. `capture_corpus`
  (`:10575`) and `capture_corpus_lenses` (`:10662`) likewise never call a lifter.
  **→ This design's primary job is to CONNECT a currently-dead lane** (the wire is structurally
  present; it carries nothing).
- **Selection axis mismatch (Observed).** The current row keys a lifter to a *projection id*
  (`produces` → `for_projection`). But the seed lifters (frontmatter/links/blocks) have **no matching
  `produced_by:"code"` projection**, and the existing code-projections (`projections/lineage.py`,
  `operators.py`, `common_knowledge.py`) have **no matching lifter**. The two registries are wired by a
  key that nothing currently lines up on. The task asks for selection **by file type** — a *different
  axis*. This design adds that axis (it does not remove `produces`); see §2.

---

## 1. The BROADENED deterministic-extraction set, per file type

The principle that decides what belongs here: **a fact is a lifter's job iff code can enumerate it
exactly and a parse is a READ** (the floor C9.2 — no resolve/dispatch). The set below is examples to
seed the registry, **not a closed list** — each row is a `lifters/<id>.py` file; more drop in freely.

Each entry names: the lifter id · the file types it selects · the structural facts it extracts ·
REUSE-vs-BUILD for its parser.

### Python (`.py`) — parser: `ast` (stdlib) · **REUSE**
`ast` is already the in-repo standard (`runtime/coherence_detect.py:35,127,154` walk the tree for
routes / node-types / call-edges — the proven pattern to mirror, not fork).

- **`py_symbols`** — top-level **defs, classes, and their methods** (name + lineno + arg names);
  module-level **assignments to UPPER_CASE names** (the registry/constant vocabulary — same shape
  `coherence_detect.hardcoding_candidates` already finds, `:384`). *This is "exports" generalized:
  the file's public surface.*
- **`py_imports`** — `import x` / `from a.b import c` → the module's **dependency edges** (the import
  graph is a relation source — see §1-relations).
- **`py_decorators`** — decorators on each def/class (`@dataclass`, `@property`, a framework route
  decorator). A structural signal the model would only approximate.
- **`py_docstrings`** — the module + each top-level def/class **docstring first line** (verbatim, not
  a paraphrase). *Reliability point: the model paraphrases; the lifter quotes exactly.*
- **`py_callgraph`** (flagged heavier) — intra-file call edges (`self.<m>(` / `name(`), the exact walk
  `coherence_detect.capability_no_consumer` already does (`:164`). Worth its own lifter because it is
  the spine of dead-code / reachability reads.

### TypeScript / TSX / JS / JSX / MJS (`.ts .tsx .js .jsx .mjs`) — **NO parser in repo → BUILD** (see §5)
WALK_EXTS was broadened to these on 2026-06-16 (`runtime/corpus.py:250`) precisely so a TS codebase is
comprehensible — but the digest is model-only; nothing extracts TS structure today.

- **`ts_imports`** — `import … from "x"` / `require("x")` / dynamic `import("x")` → dependency edges.
- **`ts_exports`** — `export const/function/class/default …`, `export { a, b }` → the module surface.
- **`ts_components`** — exported React components (a `PascalCase` function/const returning JSX, or a
  `*.tsx` default export) — the UI surface Tim's front-end work keeps asking "where is X" of.
  *First pass via regex (§5); flagged for a tree-sitter upgrade.*

### Markdown (`.md`) — parser: regex + the existing seed lifters · **REUSE**
The three seeds already cover the within-file structure. The BROADENING Tim flagged is the
**cross-file relation** layer (§1-relations).

- **`frontmatter`** — leading YAML block as a dict (`lifters/frontmatter.py`, exists). PyYAML if
  present, else a line parser (already fail-soft, `frontmatter.py:25`).
- **`blocks`** — heading structure `[{level, heading}]` (`lifters/blocks.py`, exists).
- **`links`** — outbound `[[wikilinks]]` + `[md](targets)` (`lifters/links.py`, exists). **Left
  UNCHANGED** — it returns `list[str]` and `tests/lifters_acceptance.py:85` asserts that exact shape
  (`["Alpha", "http://x"]`). Do NOT widen its return type in place (a silent type-contract change in a
  typed-dataflow repo).
- **`link_context`** (new SIBLING — not a change to `links`) — per link `[{target, anchor, sentence}]`
  (anchor text + surrounding sentence) so the relation rollup (§1-relations) has a *description*, not
  just a target id. A separate lifter keeps `links`' contract + its test green. Single-file signature.
- **`md_tags`** (new) — `#tag` inline tags + frontmatter `tags:` — the file's own classification.

### JSON / YAML (`.json .yaml .yml`) — parser: `json` / PyYAML (stdlib + already-optional) · **REUSE**
- **`json_shape`** — top-level **keys** + the **type** of each value (`str|int|list|dict|bool|null`) +
  list lengths. The *shape*, not the data — what a config/manifest declares. (PyYAML is already an
  optional dep, `frontmatter.py:25`; degrade-to-line-parse if absent, same as frontmatter.)

### SQL and others — **note (flagged, not built first pass)**
- **`sql_objects`** (note) — `CREATE TABLE/VIEW/FUNCTION` names + column names via regex; a real SQL
  parser is a later upgrade. **`.toml`**, **`.html`** (id/class/route attrs), **`.css`** (selectors)
  are all natural future lifter files. The point of the registry shape (§2) is that **each is a
  drop-in file, never a code edit** — so this list is open by construction.

### The cross-file RELATION layer Tim flagged — "links → RELATIONS + descriptions from referencing files"
This **breaks the single-file `extract(text, *, meta)` signature** (it is about who points AT a file),
so it is split into two correctly-separated mechanisms — **not** crammed into a lifter:

1. **Per-file lifters (`links` + the new `link_context`)** — *outbound* edges (`links`, unchanged
   `list[str]`) + per-link description (`link_context`: `[{target, anchor, sentence}]`). Both fit the
   single-unit signature. The dependency lifters emit, per edge, a candidate **typed relation** using
   the existing `relation_types` registry (`relation_types/depends_on.py` etc. — declared
   `{id, directed, inverse, label}` rows; `py_imports`/`ts_imports` map naturally to `depends_on`).
2. **Corpus-level INVERSION (read-time projection, NOT a lifter)** — *inbound*: "who links to file B,
   and how do they DESCRIBE B." This is a **fold over all the link-lifts**, mirroring
   `corpus.list_corpus` (read-time projection over the event log, `runtime/corpus.py:208`) and
   `find_relations` (the near/far inversion, `runtime/suite.py:10854`) — **reuse that pattern, do not
   fork a parallel store.** For a target address B: scan every record's stored `structure.link_context`,
   collect the `(source, description)` pairs whose target is B → B's *accumulated inbound descriptions*
   (this is Tim's address-accumulation idea: a record accrues how others refer to it). Lives next to
   `find_relations` as a sibling read method (e.g. `inbound_links(address)`), not in `lifters.py`
   (the floor: a lifter is single-unit; a corpus-wide fold is a read-time projection).

   *Assumption to confirm:* the inbound-description rollup is a READ over stored link-lifts, so it
   needs §3's attach to have run first (the `link_context` must be ON the records). If it is attached as
   `structure.link_context`, the fold is a pure read — no re-parse, no model.

---

## 2. Selection by file type + composition onto one record + the registry shape

### The selection axis (the conceptual shift — BOTH axes, not either/or)
The current registry selects by **projection id** (`produces` → `for_projection`). The task needs
selection by **file type**. These are *different axes*; the design **adds the file-type axis and keeps
`produces`**, decoupling the two:

- **Most structural lifters attach structure and feed NO projection** (`py_symbols`, `ts_imports`,
  `json_shape` describe a file's structure; they are not vector spaces). For these, `produces` is
  absent and they are selected purely by file type.
- **`produces`/`for_projection` survives only for the embedding code-lenses** — the
  `produced_by:"code"` projections that ARE spaces (`operators`, `common_knowledge`; `lineage` is
  code+non-embed). A lifter feeding one of those still declares `produces`.

This is the genuine broadening: a lifter is *primarily* "extract this file type's structure," and only
*secondarily* (when it feeds an embeddable code-lens) routed by projection id.

### The extended LIFTER row (mirror the existing mechanism — one-time schema edit, then file-drop)
Extend `LIFTER_FIELDS` (`runtime/lifters.py:69`) and `_build_lifter` (`:100`) with a **declarative
selector** (DATA-first — registry-is-truth):

```
LIFTER = {
  "id":         "py_symbols",          # required; == filename (unchanged)
  "extract":    _extract,              # required; (text, *, meta=None) -> value (unchanged)
  "extensions": [".py"],               # NEW — primary selector (DATA: a list of extensions)
  "match":      None,                  # NEW optional — a DECLARATIVE regex/shebang STRING for
                                       #   shape-sniffing (e.g. r"^#!/usr/bin/env python" for an
                                       #   extension-less script). A STRING, NOT a callable — so it
                                       #   stays DATA the operator can read AND it serializes through
                                       #   as_records() (a callable would break JSON — see below).
  "produces":   None,                  # optional, now usually absent (decoupled — see above)
  "desc":       "top-level defs/classes/UPPER_CASE constants (the file's public surface)",
}
```

- `extensions` is the normal selector (a `.py` file → every lifter whose `extensions` contains `.py`).
- `match` is the escape hatch for shape (a shebang, a fenced marker) — a **declarative regex STRING**
  applied to the path/head-of-text, kept rare so selection stays DATA you can read. **It MUST be a
  string, not a callable:** `as_records()` (`runtime/lifters.py:175`) only qualname-ifies `extract`; a
  callable `match` would ride into the dict raw and fail JSON serialization in `build_cognition_info`
  (and trip the `isinstance(r["extract"], str)` sibling check, `tests/lifters_acceptance.py:90`). A
  regex string serializes cleanly and needs no `as_records` change.
- **Selection semantics — absent `extensions` = NEVER selected** (the safe reading: a lifter opts IN to
  file types explicitly; no silent match-everything). This means the three SEED lifters
  (frontmatter/links/blocks), which have neither field today, must be **migrated**: add
  `"extensions": [".md"]` to each (see §6). Without it they would silently extract nothing.
- Adding `extensions`/`match` is a **one-time mechanism change** to the validator; **adding a lifter
  stays a file-drop** (no hardcoding — the no-hardcoding law holds: the registry path is the rule).

### A new pure read on the registry (mirror `for_projection`)
Add `applicable(path, text=None) -> list[Lifter]` to `LifterRegistry` (sibling of `for_projection`,
`runtime/lifters.py:167`): returns, in sorted id order, every lifter whose `extensions` matches the
path's suffix OR whose `match(path, text)` returns True. Pure read — the floor holds.

### Composition: multiple lifters onto ONE file's record
`applicable(".py")` returns e.g. `[py_callgraph, py_decorators, py_docstrings, py_imports, py_symbols]`
(sorted). The capture path runs each and composes their outputs into a **single keyed dict**:

```
structure = { lifter.id: lifter.extract(text, meta=meta) for lifter in reg.applicable(path, text) }
#   e.g. {"py_imports": [...], "py_symbols": [...], "py_docstrings": [...], ...}
```

Composition is the dict merge keyed by lifter id — collision-free by construction (id == filename ==
unique key). No ordering dependence (each lifter reads the same `text` independently — the floor).

---

## 3. How lifted structure ATTACHES to the corpus record (alongside the model digest)

**Face value, low-friction, no `corpus.py` change** (confirmed against the code):

- The corpus record is an **open/additive dict** — `write_record` spreads `**extra`
  (`runtime/corpus.py:172`); `capture_corpus` already forwards arbitrary `**extra`
  (`runtime/suite.py:10623`). So a `structure` field rides free, no schema edit.
- **The wire is one block in `ingest_paths`** (`runtime/suite.py:10554`), where each record dict is
  built. Add the lifter pass there:

```
# CURRENT (runtime/suite.py:10558) — model digest only:
records.append({"source_address": f"code://{f['path']}", "output": dig,
                "kind": "capture", "projection": projection, "source_hash": f["hash"]})

# DESIGNED — model digest + deterministic structure (one record = both halves):
structure = {lf.id: lf.extract(f["text"], meta={"path": f["path"]})
             for lf in self.lifter_registry.applicable(f["path"], f["text"])}
records.append({"source_address": f"code://{f['path']}", "output": dig,
                "kind": "capture", "projection": projection, "source_hash": f["hash"],
                "structure": structure})        # rides free via capture_corpus **extra → write_record
```

- **Attach to the per-FILE record only.** Structure is a property of the file, not of a lens. The
  per-file "repo" capture (`ingest_paths`) is the right home. **Do NOT** duplicate structure across the
  per-lens space-records that `capture_corpus_lenses` writes (`runtime/suite.py:10662`) — those are
  per-(file,lens) and would replicate the same structure N times. (If a future caller wants structure
  on a lens record too, it reads it from the file record by `source_address` — one source of truth.)
- **The resulting record shape:**
  ```
  { source_address: "code://runtime/suite.py",
    output: "<model digest: what_it_is / role / notable>",   # MODEL side (open-ended)
    structure: { py_imports:[...], py_symbols:[...], ... },   # LIFTER side (deterministic)
    kind: "capture", projection: "repo", lineage:{...}, source_hash:"…" }
  ```
- **Embedding is unchanged.** Only `output` feeds the vector space (`_embed_text(output)`,
  `runtime/suite.py:10635`). `structure` is durable + queryable on the record (the `find_corpus`
  projection, `corpus.py:230`), not embedded — it is exact facts, not a meaning space. (A future
  code-lens that DOES embed, e.g. `operators`, routes via `produces` → its own embed path; orthogonal.)

**Resume-safety holds:** `structure` is deterministic over the same `text`, so a re-capture produces the
same record content → same cas (the `put_content` write-once / idempotent-resume guarantee,
`corpus.py:174`). Lifters do not break the determinism the resume model depends on.

---

## 4. MODEL-side vs LIFTER-side — the reliability split

**The reliability principle (the whole point):** *never ask the model to enumerate what code can
extract exactly.* The model is for judgement and open-ended description; the lifter is for exact,
enumerable, verifiable facts. The split:

| | LIFTER side (deterministic, `produced_by:"code"`) | MODEL side (open-ended, `produced_by:"model"`) |
|---|---|---|
| **What** | Everything enumerable / structural / exact | Everything interpretive / synthetic |
| **Examples** | imports, exports/defs/classes, decorators, docstring text (verbatim), headings, frontmatter, wikilinks + targets, JSON keys/shape, tags, call edges | `what_it_is` (≤15-word statement, `projections/what.py`), `role` in the system (`projections/repo.py`), `notable`, `topics` (`topics.py`), `principles` (`principles.py`), `claimed_status` (`claimed_status.py`) |
| **Failure mode it removes** | model miscounts / omits / hallucinates a symbol or link | — (judgement genuinely needs a model) |
| **Cost / reliability** | free, instant, 100% reproducible, git-diffable | a model call; approximate; not reproducible |
| **In the record** | `structure: {…}` (this design) | `output: "<digest>"` (today) |

**The boundary test:** if two careful readers would always produce the *same* answer → lifter. If the
answer is a *description / judgement* → model. "List the imports" is a lifter (one right answer); "what
is this file for" is the model (the digest). The current `repo_digest` role (`roles/repo_digest.py`,
`digest`+`kind` fields) is correctly model-side — it describes; it does not enumerate.

A subtle one worth stating: `kind`-of-file ("test", "config", "role") sits on the boundary — the lifter
can give the *extension + structural signals* (has `def test_`, declares `LIFTER`/`PROJECTION`), the
model gives the *interpretation*. Prefer the lifter for the signal, let the model name it.

---

## 5. Parsers — available vs needed (REUSE-vs-BUILD)

| File type | Parser | Status | Decision |
|---|---|---|---|
| Python `.py` | `ast` (stdlib) | **In repo** (`coherence_detect.py:35,127,154,164`) | **REUSE** — mirror the existing AST walks |
| Markdown `.md` | regex + seed lifters | **In repo** (`lifters/*.py`) | **REUSE** — extend `links` for per-link context |
| JSON `.json` | `json` (stdlib) | available | **REUSE** |
| YAML `.yaml/.yml` | PyYAML | already-optional (`frontmatter.py:25`) | **REUSE** — degrade-to-line-parse if absent (existing pattern) |
| **TS/TSX/JS/JSX/MJS** | — | **NONE in repo** (verified: no tree-sitter, esprima, acorn, babel, pyjsparser) | **BUILD** — see options below |
| SQL / TOML / HTML / CSS | — | none | note — future drop-in lifter files (regex first) |

### The TS/JS call (the explicit ask — not punted)
No JS/TS parser exists anywhere in the repo (`grep` over the tree returns nothing for tree-sitter /
esprima / acorn / babel / pyjsparser). Options, REUSE-vs-BUILD, with a recommendation:

1. **Regex extractors now (BUILD, zero-dep) — RECOMMENDED first pass.** ES `import`/`export`/component
   syntax is line-regular and the common forms are matchable deterministically (the `links` and route
   regexes already in `coherence_detect`/`links.py` are the precedent). Floor-respecting, no new
   dependency, ships immediately for the TS pain point (WALK_EXTS, `corpus.py:250`).
   *Epistemic label (per the Observed/Inferred/Verified rule):* regex coverage is **Inferred-complete
   for common forms**, NOT a Verified-complete parse — it will miss exotic syntax (re-exports through
   barrels, computed names). Acceptable because a missed symbol is the SAFE direction (under-extraction
   surfaces; it never fabricates a symbol that isn't there).
2. **`tree-sitter` + `tree-sitter-typescript` (BUILD via an existing resource) — the flagged robust
   upgrade.** A real grammar, not hand-rolled regex; one pip dependency; gives an exact AST like `ast`
   does for Python. Recommended as the *upgrade path* once the regex pass proves the wire — it raises TS
   to parity with the Python lifters. (This is "use existing resources, not hand-built" — the grammar
   already exists; we'd consume it.)
3. **node/`tsc` subprocess (REJECT).** The most accurate, but needs a Node toolchain present, is heavy
   per-file, and a subprocess on the parse path strains the floor (a parse should be a pure in-process
   READ). Note and reject.

**Recommendation:** ship `ts_imports`/`ts_exports`/`ts_components` as **regex lifters now** (option 1),
**flag tree-sitter as the upgrade** (option 2) in `lifters/AGENTS.md`. Both are file-drop lifters — the
upgrade replaces the `extract` body of an existing `lifters/<id>.py`, no registry change.

---

## 6. Mechanics — what a build pass must touch (so it stays a registry, not a hardcode)

- **Schema (one-time):** add `extensions` + `match` to `LIFTER_FIELDS` (`runtime/lifters.py:69`) and
  validate in `_build_lifter` (`:100`: `extensions` a list-of-str if present; `match` a regex STRING if
  present — NOT a callable); add `applicable()` read (`:167` sibling) with the absent-extensions =
  never-selected semantics. Update the `Lifter` dataclass accessors (`:79`). **No `as_records()` change
  needed** because `match` is a string (a callable would have required qualname-ifying it too).
- **Seed migration (required, else they go silent):** add `"extensions": [".md"]` to
  `lifters/frontmatter.py`, `lifters/links.py`, `lifters/blocks.py` — they have no selector today, so
  under the new model they would never be selected.
- **Wire (one block):** the `structure = {…}` attach in `ingest_paths` (`runtime/suite.py:10558`).
  No `corpus.py` edit (rides `**extra`). No `capture_corpus` edit (forwards `**extra`).
- **Corpus-level read (one method):** `inbound_links(address)` as a `find_relations` sibling
  (`runtime/suite.py:10854`) — a read-time fold over stored `structure.link_context`, mirroring
  `list_corpus`.
- **New lifter files (file-drop, the open set):** `lifters/py_symbols.py`, `py_imports.py`,
  `py_decorators.py`, `py_docstrings.py`, `py_callgraph.py`, `ts_imports.py`, `ts_exports.py`,
  `ts_components.py`, `json_shape.py`, `md_tags.py`, `link_context.py` (the inbound-description sibling).
  Each self-registers. `links.py` is migrated (selector) but its return contract is unchanged.
- **Drift home + tests (fail-loud guard):** every new lifter MUST be reflected in `lifters/AGENTS.md`
  and any new field exercised in `tests/lifters_acceptance.py` — the suite asserts each discovered
  lifter is in the drift home (`tests/lifters_acceptance.py:95`) and that the extractors WORK on real
  values (`:81`). The existing `links == ["Alpha", "http://x"]` assertion (`:85`) stays GREEN because
  `links`' shape is unchanged. Add: a DROP-IN test for `extensions`/`applicable` selection (mirroring
  `:50`), and an assertion that a string `match` survives `as_records()` JSON serialization.

**Laws honoured:** no-hardcoding (lifters file-discovered; selection is DATA `extensions`) ·
reuse-don't-parallel (the ONE registry mechanism; `ast` reuse; the `list_corpus`/`find_relations` fold
for inbound links — no new store) · fail-loud (malformed lifter / unknown projection RAISES) · the floor
(every `extract` is a pure in-process READ; the corpus-wide rollup is a read-time projection, never a
dispatch) · schema-additive (`structure` rides the open record free).

---

## 7. Open questions / assumptions to correct (epistemic humility)

1. **Inbound-link descriptions** assume link structure is attached as `structure.links` first (§1-rel,
   §3) so the rollup is a pure read. If the relation layer should instead emit into the
   `relation_types`/vector substrate (so `find_relations` ranges over it), that is a bigger wire — worth
   a direction check. (Both are reuse of existing mechanisms; the question is which substrate.)
2. **`produces` decoupling** (§2): this design makes `produces` usually-absent and selection
   file-type-first. If the intent is the *opposite* — keep every lifter tied to a `produced_by:"code"`
   projection (one lens per lifter) — then each new lifter also needs a `projections/<id>.py`. The
   file-type-first reading is recommended (it's what "don't limit to imports/exports" implies — most
   structural facts aren't embeddable spaces), but it's the main interpretive fork.
3. **TS via regex vs tree-sitter** (§5): recommended regex-now / tree-sitter-upgrade, but if TS
   correctness is load-bearing immediately, start at tree-sitter (one dependency) and skip the regex
   stage.
