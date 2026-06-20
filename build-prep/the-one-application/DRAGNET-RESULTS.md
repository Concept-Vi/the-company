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

## NEXT
- Narrower self-ref determine on the exact structured-outputs/allocation/feeding thread (quick).
- The determine stage wants to become a tool/skill (`gap-surface` + `theorem-mine` / a determine verb over the extraction layer) + wired so the RHM/face queries the asset.
- The extraction layer is the reusable asset for ANY future question (extract-once/query-many) — both session + visual-dna now queryable by determine.
