# Ledger exploration — what the work yielded, and the shape of the mess (2026-07-01, overnight)

*Tim: "checking out the ledger, what all our hard work has yielded. The whole space is a mess — fragmented, duplicates, inconsistencies — 100% AI-generated over many sessions with no plan. This is hopefully how we see how to resolve everything." Built with the live embedder (embed-pplx) + the Company MCP/SQL surface. The ledger is the self-model; this is the first read of it AS a lens onto the sprawl.*

## The ledger at a glance
- **11,292 file entries · 8,073 symbols · 46,613 edges · 487 capabilities · 415 folders**, across 4 projects (company, platforms, counterpart-design, claude-ds).
- It is a **real, queryable self-model** — the audit + interpretive passes produced a navigable graph. That's the yield: we can now SEE the system as data, which is what makes the mess legible.

## Finding 1 — the self-model is ~88% NOISE (no ingest boundary)
Only **1,300 of 11,292 file entries (11.5%) are CODE.** The rest was ingested indiscriminately:

| bucket | files | what it is |
|---|---|---|
| recollection-archive | 3,536 | session **transcripts** — conversation data, not structure |
| build-prep (our scratch) | 2,598 | our OWN working-out / discovery artifacts |
| channel-memory (data) | 1,530 | channel attachments, noticeboard, images |
| **CODE** | **1,300** | the actual system |
| vendored/reference | 930 | design handoffs, `source/dump`, others' material |
| other | 712 | misc |
| markdown docs | 384 | the actual knowledge-vault docs |
| binary/image assets | 290 | png/jpg/svg/pdf |

**The root issue: the ledger has no boundary on what belongs in the self-model.** A self-model should hold the STRUCTURE (code + capabilities + the vault), not conversation archives, channel data, vendored handoffs, binary assets, or our own scratch. → *Resolution direction: a typed ingest boundary — the self-model indexes the system; transcripts/channel/assets are LINKED data, not entries.*

## Finding 2 — the extractor misses symbols in nearly every file
The coverage audit (1,304 code files, 100%) is brutal on the deterministic extractor:

| kind | files | pass | flagged | model-claimed missed symbols |
|---|---|---|---|---|
| py | 728 | 28 | **700 (96%)** | 4,243 |
| jsx | 210 | 0 | **210 (100%)** | 1,641 |
| js | 148 | 0 | **148 (100%)** | 1,063 |
| ts | 138 | 4 | 134 | 960 |
| tsx | 80 | 2 | 78 | 659 |

JS/JSX are **100% flagged** — the extractor is weakest on the front-end languages. (Counts are the audit model's claims — directional, with 4B noise — but the *pattern* is unambiguous: the deterministic extractor under-captures symbols everywhere.) → *Resolution: fix the per-language extractors (JS/JSX first); re-extract; re-audit; converge.*

## Finding 3 — the relationship graph is 66% dangling
Of **46,613 edges, 30,620 (66%) have an unresolved target** (`to_resolved` empty) — mostly `calls` (28,789 total) the extractor couldn't link to a definition. So the "wiring" is mostly broken links: the graph knows a call happened but not to what.

Edge kinds: calls 28,789 · contains 5,649 · imports 4,662 · references 3,274 · in_channel 1,109 · attached_to 680 · authored_by 540 · capability-of 487 · relates-to 438 · part_of 239 · calls-endpoint 210 · extends 200.

→ *Resolution: a symbol-resolution pass (link call/import targets to their definitions); the 66% dangling is the gap between "saw a reference" and "know what it points to."*

## Finding 4 — duplication: CODE is clean; "doc duplication" is mostly DATA-as-docs
Embedded every described code file (1,304) and doc (2,305) via the live embedder; cosine-clustered.

- **CODE is relatively clean:** at cos≥0.85, only **9 clusters / 32 files**, and 7 of 9 span projects — i.e. the only real code "duplication" is **vendored copies** (e.g. `Resizable.jsx`, `archetype.js` exist in both `claude-ds` and the `counterpart-design` handoff). The system's code is NOT massively duplicated at the file level.
- **DOCS look 35% duplicated (811 of 2,305 in 32 clusters) — but it's DATA, not docs:** the largest cluster is **716 near-identical `channel-memory/channel_attachments/att-*.md`** (one metadata stub per attachment — template instances), plus noticeboard/image metadata clusters. So the "doc duplication" is overwhelmingly **channel-memory DATA records ingested as markdown** — the same ingest-boundary problem as Finding 1, seen from the duplication angle.
- **Genuine conceptual duplication is smaller but real:** e.g. the *Live Intent Resolution Surface* spec written twice; the *Obsidian-as-host* exploration drafted 3×; one decision ("visual-fidelity") recorded as 12 near-identical noticeboard signals.

## Finding 5 — the orientation layer was rebuilt every session (no consolidation)
The navigational/self-description docs are heavily fragmented — each session minted its own:
- **20+ distinct `*-MAP.md`** (UNIFICATION-MAP, BUILD-ADDRESS-MAP, FILE-MAP, GROUNDED-MAP, INVENTORY-MAP, MODE-SYSTEM-MAP, UNION-MAP, UNION-SEAM-MAP, V-SURFACE-MAP, PARAM-MAP, SESSION_MAP, SUBSTRATE-HOME-CONVERGENCE-MAP, …), multiple `HANDOFF-*.md`, and `STATE.md`/`AUTONOMOUS-STATE.md`/`OVERNIGHT-STATE.md`.
- **58 `AGENTS.md` + 33 `README.md`** (AGENTS-per-folder is the vault convention, so that count is largely legitimate — but it means the constitution is spread across 58 files).
- **Cross-check via the Company's own recall:** querying the `repo` corpus "how does the system resolve which brain model to use" returns `cognition.py` (the real answer) then **8 `build-prep/*.md` scratch docs** — the noise-ingest actively *degrades the system's own retrieval* (it answers with planning docs, not code).

## What this means — the unification path the ledger reveals
The ledger did its job: it makes the sprawl legible, and the resolution is now concrete.

1. **A typed ingest boundary (highest leverage).** The self-model should index **structure** — code, capabilities, the real vault docs (~1,700 entries). **Data** (channel-memory, recollection transcripts), **scratch** (build-prep), **vendored** (reference/handoffs), and **binary assets** should be *linked*, not ingested as entries. This alone cuts the ledger from 11,292 → ~1,700 meaningful entries (−85% noise) and fixes corpus retrieval.
2. **Fix the per-language extractors** (JS/JSX first — 100% flagged), re-extract, let the coverage audit re-confirm convergence.
3. **A symbol-resolution pass** — link the 66% dangling `calls`/`imports` edges to their definitions so the relationship graph is real wiring, not broken references.
4. **Consolidate the orientation layer** — ONE live map (the vault `MAP.md`), `AGENTS.md`-per-folder as the constitution, and **archive** the 20+ session `*-MAP`/`HANDOFF`/`STATE` docs into a dated `archive/` (out of the live self-model).
5. **Re-index the corpus on the clean structure** — so "ask the codebase" returns code, not scratch.

**The throughline to the one-system mission:** the ledger is the seed, and it shows the unification is not "rewrite everything" — it's **draw the boundary** (structure vs data/scratch/vendored), **fix extraction + resolution** (so the structure graph is true), and **consolidate the orientation layer** (one map, not twenty). The fragmentation is real but bounded: ~1,300 code files that are individually distinct (low duplication) buried under ~10,000 entries of un-bounded ingest.

---
*Method note: built with the live pplx embedder (3,627 descriptions embedded), the ledger SQL surface, and the Company `corpus` MCP tool. Counts from the audit model's findings are directional (4B noise) but the structural facts (entry/edge/file counts, content buckets, dangling-edge ratio, cluster membership) are exact. Raw cluster dumps: `$CLAUDE_JOB_DIR/tmp/dupe_np.md`.*
