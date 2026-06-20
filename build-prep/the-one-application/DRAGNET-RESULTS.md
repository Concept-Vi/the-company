# Dragnet recall — RESULTS (the overnight bake + first determines)

*The #65 full-coverage dragnet, run overnight 2026-06-21 per Tim's mandate. Two extraction-layer assets built (extract-once/determine-many), both determines proven useful by-use. The recall substrate now has a meaning-extracted layer over the session history AND Tim's Visual-DNA vault.*

## THE ASSETS (.data/store/extractions/)
- **extractions-full.jsonl — SESSION HISTORY: 18,857 records** (1 coarse-fail, honest). 6,991 coarse + 11,866 fine. Tim's 9-project filter (exact-segment, verified clean). Kinds: discussion 7,625 · log 5,258 · spec 4,087 · digest 853 · decision 158. Per-project: -home-tim 16,680 · vi-visual-dev 1,229 · company-interactive 653 · company 214 · others.
- **extractions-visual-dna.jsonl — VISUAL-DNA VAULT: 10,568 records** (0 failed, clean). 2,897 coarse + 7,671 fine. Kinds: spec 5,841 · discussion 1,797 · log 1,322 · reference 1,228. The design-DNA theory — new ground for DNA's form strand.

## THE RECIPE (proven end-to-end)
Stepped adaptive cascade (Tim's design): COARSE {about,kind,touches} every chunk → STEP-GATE from each coarse output (kind∈{decision,spec,discussion}→fine; log/reference/other→stop) → FINE {summary,entities,claims,relations,open_questions} on gated. Stored superset; grain=depth-reached (down-projection serves any grain). Worker EXTRACTS (neutral, no relevance prior — can't miss); central DETERMINE reads the cheap extractions per-topic; REDUCE synthesizes. Local chat-4b, ~3 chunks/s effective.

## THE CRASH-AND-RECOVERY (honest gap-surface)
Session bake CRASHED at 10,998/18,858 — run_items mis-classified ~6 chunks whose TEXT starts with a scheme example (run://… / cas://… doc lines) as ADDRESSES → fatal resolve fail. default-to-wrong caught it (the watcher said "exited"; the log showed the RuntimeError, NOT a clean finish). Fixed (`_safe_item` leading-space guard, 6aeb8ef) + resumed crash-safe (the batched-append re-skipped the 10,998 — zero lost work). The crash-safe/resumable design earned its keep.

## FIRST DETERMINE — SESSION HISTORY (the self-referential proof)
Determine over the cheap stored extractions (NOT raw chunks — the generalizability win) recovered real design depth: "laws-as-substrate + verb-whitelist (run/propose/build/consult/show/panel/extend), the resolve→work→persist→trigger engine, graph-IS-the-plan, three-layer fabric, signature caching, vLLM concurrency." + 6 key-decisions + 3 open-threads. HONEST: the filter was broad (caught all architecture depth, not only the narrow structured-outputs/feeding thread) — proves the mechanism; a narrower determine is a follow-on.

## DETERMINE — VISUAL-DNA (for DNA's form strand) ★ CONFIRMS TIM'S META-PATTERN
Determine recovered the design-DNA core: "a scalable multi-scale architecture, all input modules write to a central DNA source, resolves visual variables (shapes/colors/spacing) through a typed token graph rather than fixed rules, single source of truth, DAG-node hashing for token propagation." Shape/line: shapes multi-use+context-dependent (circles/diamonds/parallelograms/hexagons/pills), line+spacing via token scales, color via unified theme→CSS-vars, tokens as DAG-node hashes.
★ CONTEXT-RESOLUTION EVIDENCE — the vault INDEPENDENTLY confirms the meta-pattern the lead told DNA to build to (Tim's design language IS his resolver philosophy; his line=context-dependent, opacity=multi-use decisions): "shapes adapt to platform/system context", "visual variables resolve differently by scale + architectural layer", "same DNA principles applied differently per context", "a system is WRONG if it treats variables as fixed rather than context-resolved." DNA's form strand should draw on this — it's grounded validation, not invention.

## NARROW SELF-REF DETERMINE (the exact structured-outputs/allocation/feeding thread) — done, with a RELIABILITY FINDING
Ran the tighter determine (3,346 candidate extractions vs the broad pass). It surfaced REAL themes that ARE in the history: kind-tag routing ([spec]/[discussion]→buckets), the LOCAL-extraction / CLOUD-judgment allocation split (matches [[extraction-vs-judgment]] + fork's PARAM-MAP), schema-constrained vs open prompts, batching for context-window cost.
★ BUT critical-comparison (default-to-wrong) on the determine's OWN output: the single-REDUCE CONFABULATES — it smooths scattered extractions into a coherent-sounding "design" with invented specifics ("corporate organ metaphors", "architectural manifestos") that overstate what was actually discussed as one thread. So this determine is a useful MAP TO THE SOURCE extractions, NOT verbatim recall — don't treat the synthesis as ground truth.
★ THE RELIABILITY FIX (the determine-as-tool's next step): the REDUCE needs NO-FICTION CLAIM-GROUNDING — cite the source extraction (and its chunk) per claim, validate each against the raw source (the SAME no-fiction-judge pattern the corpus mining already uses — the mine_exchange judge that validates an extract against its raw exchange). Without it, the reduce produces plausible-but-confabulated design. So: determine = the cheap candidate-filter (reliable, reads real extractions) + a GROUNDED reduce (cite-per-claim) — not a free-synthesis reduce. This is the gap to close before the determine becomes a trusted tool/skill.

## ★ GROUNDED DETERMINE — BUILT + PROVEN (the reliability fix; ops/dragnet_determine.py, ef74471)
The no-fiction reduce is done (lead-endorsed, 4c57c01). Instead of free-synthesis (which confabulated), the model
CLUSTERS the real extraction claims BY INDEX (groups + theme-labels only, never generates claim text) → every
output claim is a VERBATIM real extraction with its chunk_id provenance. A no-fiction check verifies every
returned index is valid. PROVEN by-use (structured-outputs topic): NO-FICTION=True, 6 coherent themes (MCP
capabilities · API endpoints · exclusions · architecture principles · safety · operational), 48/50 real claims
grouped + chunk-traced. ★ Confabulation is now STRUCTURALLY impossible — the model can't invent claim text, only
group existing-by-number. So the determine is a TRUSTED tool: reliable candidate-filter + no-fiction grounded cluster.

## DETERMINE-AS-MCP-TOOL — DONE (d873572): corpus(op='determine', text, asset) → grounded chunk-traced themes, no_fiction by construction. runtime/recall_determine.py = the engine (CLI + face share). The operable recall-before-build surface.

## PRECISION FINDING + FIX (proven): the determine's candidate-FILTER is keyword-based → topically BLUNT
The no-fiction GROUNDING is solved; the candidate-FILTER isn't. On "visual variables resolve by context" the keyword filter surfaced ROOT-STRUCTURE claims (homonym/word-match ≠ concept-match). ★ PROVEN FIX (by-use, no commitment): a SEMANTIC filter (embed topic + extraction texts, rank by cosine) surfaces the RIGHT claims — "blocks resolve values by walking up their CONTEXT chain" (0.410), "architecture-canonical applies at pixel/component/view SCALES" (0.401), "identical primitives distinguished only by [context]" (0.391) — i.e. it hard-grounds Tim's context-resolution design-law, where keyword couldn't.

## NEXT (proven + scoped): EMBED THE EXTRACTION LAYER
Register an embeddable space + embed the 29,425 extractions (embed_corpus_to_spaces) → (a) the determine candidate-filter becomes SEMANTIC (precise, fixes the bluntness + unlocks the Visual-DNA verbatim hard-grounding) AND (b) the dragnet asset folds into the existing corpus(op='query') path (one recall surface). A ~29k embed on :8007 (announce/sequence like the bake). Render-independent.
- The determine stage wants to become a tool/skill (`gap-surface` + `theorem-mine` / a determine verb over the extraction layer) + wired so the RHM/face queries the asset.
- The extraction layer is the reusable asset for ANY future question (extract-once/query-many) — both session + visual-dna now queryable by determine.
