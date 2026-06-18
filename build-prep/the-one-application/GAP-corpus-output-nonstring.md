# GAP (grounding-quality): many corpus records carry a non-string `output` → the precision re-sort silently skips them

*recollection's side-finding from the 2026-06-18 rerank investigation, tracked as a SEPARATE sub-item (the lead's #3) — distinct from the rerank-loadout decision (board://item-a3844c46 / decision://global/rerank-loadout). Non-blocking. Corpus-face owner: recollection.*

## What
Measured on a 24-hit cross-space decision pool: **13 of 24 candidates had a non-string `output`** (a list, not a string/dict). `runtime/corpus_rerank.py:_digest_text` returns that non-string; `rerank_hits` then guards with `isinstance(text, str)` and SKIPS it (with `skip_missing=True` it's dropped; same-space callers fail-loud). So **even with the sharper re-sort ON, only the with-text minority (11/24) ever got re-sorted** — the rest fell through to rough-similarity order regardless.

## Why it matters (grounding quality, independent of the on/off loadout decision)
This is NOT the same as the loadout decision (that's whether/where the sharper step runs at all). This is: the sharper step can't even SEE half the candidates, because their stored `output` isn't text it can read. So grounding precision is silently capped at the with-text subset — a quiet quality ceiling, invisible today.

## Root (where to fix — corpus capture/digest path, not the rerank stage)
The fix belongs at WRITE time, not read time: the corpus capture/digest path should normalise each record's `output` to a readable string/summary when it persists (so `_digest_text` always returns usable text), OR `_digest_text` should learn to render a list-`output` into text (join / summarise) rather than returning the raw list. Prefer normalise-at-write (single source of truth; every reader benefits) — confirm with the corpus-capture owner.

## Status
- Tracked here + noted in board://item-a3844c46 (as a sub-item). Non-blocking; no live decision-surface impact while the sharper sort is OFF (decisions ground by rough similarity over ALL candidates either way).
- Becomes load-bearing the moment the sharper sort is restored (any rerank-loadout option except "leave it off") — fold this fix in WITH that, so the restored precision actually sees the full candidate set.

## UPDATE 2026-06-18 — READ-SIDE handled (write-side now optional)
The grounding-legibility half is CLOSED from the read side (5d9e645 + follow-up): `recall_for_decision`'s
`_clean_meaning` now renders BOTH digest shapes — a structured dict (labelled non-empty fields) AND a
**list of insight strings** (joined). Verified: context-item text coverage went 5/10 → **10/10** on the
decision probe, hot-path budget held (~1.9s). So the RHM/territory_prose now get legible meaning for the
full candidate set today, regardless of the stored `output` shape.
What REMAINS (downgraded to consistency-nicety, NOT a grounding-blocker): the corpus-WRITE/digest pass
still emits heterogeneous `output` shapes (dict vs list vs string). Normalising to ONE canonical shape at
write time would (a) simplify every reader (not just this one), (b) help the RERANK path (which still
json.dumps a non-string output as the cross-encoder input). Worth doing in a coordinated cognition/digest-
schema pass; no longer urgent for decision grounding.
