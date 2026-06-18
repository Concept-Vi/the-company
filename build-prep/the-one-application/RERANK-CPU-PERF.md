> ⬆ SUPERSEDED-FOR-TRACKING (2026-06-18): the TRACKING handle is now **board://item-a3844c46** + the
> authored card **decision://global/rerank-loadout** (decisions/rerank-loadout.py) — Tim decides it on the
> surface. This doc remains the detailed MEASUREMENT/analysis the board item + card draw on (not the tracker).
> The data-shape side-finding moved to its own gap-note: GAP-corpus-output-nonstring.md.

# corpus_rerank is slow because jina-v3 runs on CPU (~1s/candidate) — root cause + options

*recollection's follow-up to the 2026-06-18 decision-surface regression. The lead parked "corpus_rerank pathologically slow" as a non-blocking follow-up (it's now OFF the decision hot-path — see 7e0ebbc). This note gives the ROOT CAUSE + the options, measured by use. Not a code bug → no unilateral fix; the real lever is a Tim loadout decision.*

## Measured (warm cache, 24-hit cross-space pool from a decision query)
- **Stage A — digest-fetch** (`_digest_text` = `corpus.find_corpus` + `read_record`, ×24): **1.16s** (0.043s each). Minor.
- **Stage B — the :8008 cross-encoder POST** (jina-v3, CPU): **10.9s then 11.8s** for **11 candidates** (~4.3k chars total, avg 392 chars/passage). **~1s per candidate passage, consistent across calls.**

So the cost is ~entirely Stage B, and it's **per-passage forward-pass time on CPU**, not a warmup/model-reload bug (call#1 ≈ call#2) and not passage-length-bound (passages are already short, ~392 chars). 11 cands → ~11s; 24 → ~24s. recall ran it TWICE (cross-space + inside prior_decisions) → the ~30s that, stacked with the (now-fixed) uncached index reads, produced the >15s decision hang.

## Why CPU: by design
`ops/serve_rerank.sh` pins `CUDA_VISIBLE_DEVICES=""` — jina-reranker-v3 is served CPU-only on :8008 deliberately (0 VRAM, no contention with the GPU loadout — Tim's 2026-06-14 direction: served endpoints, no overlord bridge). So the slowness is the cost of that choice, not a regression.

## Options (the real lever is a loadout decision — NOT mine to make unilaterally)
1. **Keep rerank OFF latency-bounded paths (done for decisions).** Cosine grounding is the live path; rerank is a precision refinement reserved for unbounded/background paths. Zero cost, zero new load. ← current state.
2. **Move jina-v3 to GPU.** ~10-50× faster (sub-second), restores rerank as a live-usable precision pass everywhere. COST: VRAM + a loadout change (consult-before-model-loads — Tim's call). The clean win IF the VRAM fits the loadout.
3. **A lighter CPU cross-encoder** (e.g. a small bge/MiniLM reranker) as a fast-tier, jina-v3 reserved for high-stakes. COST: quality tradeoff; and "make each thing work" says don't just swap jina away — so this is a fast-TIER beside it, not a replacement.
4. **Smaller candidate sets / background rerank** for the paths that still want jina (e.g. consult): rerank top-6 not top-24, or compute it async and cache.

## Also affected (flagged): the CC consult path
`query_and_rerank` / the consult/R2 retrieve use rerank too → consult queries that rerank pay ~10s on CPU. Same root cause; same options. Worth Tim/lead deciding option 1-vs-2 once, company-wide.

## Side finding for the corpus-face owner (data shape)
13 of 24 pooled candidates had a **non-string `output`** (a list) → `_digest_text` returns the list → `rerank_hits` skips them (`isinstance(text, str)` guard; skip_missing drops them, same-space would fail-loud). So cross-space rerank silently reranks only the with-text minority. Not wrong (honest skip), but means many records carry an `output` shape the digest-reader can't turn into rerank text — the corpus capture/digest path may want to normalise `output` to a string/summary at write time.
