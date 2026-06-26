# bge→pplx corpus-embed SWITCH — apply-ready diff (proposed by ch-83e2cque, for ch-al7jdfdr to review+apply)

**Goal:** make pplx-2560 @ :8007 the DEFAULT corpus-embed layer, COUPLED (query-embed dim == stored-vector dim, always), per the lead's architecture call (2026-06-16, thread g-1781590958). bge = explicit dormant alternate (bare/None layer, reachable explicitly; endpoint down). Dim/layer mismatch stays FAIL-LOUD RAISE (proven below — it's already built into `retrieve._cosine`, no silent-empty).

**Design:** ONE knob (`DEFAULT_EMB_LAYER`) + a `resolve_emb_layer()` helper, resolved at the core chokepoints (`query_index`, `build_index`, `find_relations`). A string sentinel `"__default__"` is the param default ("caller didn't pin a layer → use the knob"); `None`/`'bge'` stay reachable as the bare/legacy bge layer. No call-site threading needed for `query_corpus`/consult (they omit `emb` → chokepoint resolves).

**PROVEN end-to-end (no committed file touched):** embed query via :8007/pplx → dim 2560; `query_index(space='repo', emb='pplx')` → **5 hits, "ranked 5 of 644 by cosine"**; same 2560 query vs `emb=None` (bge-1024) → **`ValueError: vector dim mismatch: 2560 vs 1024`** (the lead's non-negotiable fail-loud, by reuse).

---

## EDIT 1 — `fabric/config.py` (lines 23–27, 36–37): switch the operative embedder + add the layer knob

**OLD (23–27):**
```python
# is ollama :11434 (chat). BGE-M3 @ :8001 is the only LIVE, dim-grounded embedder (1024-dim dense).
# Other embedders' dims are NOT doc-grounded — resolve at runtime, never hardcode them here.
DEFAULT_EMBED_URL = os.environ.get("COMPANY_EMBED_URL", "http://localhost:8001/v1")
DEFAULT_EMBED_MODEL = os.environ.get("COMPANY_EMBED_MODEL", "BAAI/bge-m3")
```
**NEW:**
```python
# OPERATIVE EMBEDDER (2026-06-16 switch, bge→pplx): pplx-embed-context-v1-4b @ :8007, 2560-dim INT8 —
# the LIVE GPU-served embedder. BGE-M3 @ :8001 is DORMANT (endpoint down; its 1024-dim vectors intact at
# the bare/None layer + vectors.bge-backup-20260615, reachable only if revived). Other dims not
# doc-grounded — resolve at runtime, never hardcode.
DEFAULT_EMBED_URL = os.environ.get("COMPANY_EMBED_URL", "http://localhost:8007/v1")
DEFAULT_EMBED_MODEL = os.environ.get("COMPANY_EMBED_MODEL", "perplexity-ai/pplx-embed-context-v1-4b")
```

**OLD (36–37):**
```python
# Embedder dim contract (rule 4): BGE-M3 = 1024-dim. Config-driven, not a node literal — a
# wrong-length vector FAILS LOUD, never flows through as a bad cosine.
DEFAULT_EMBED_DIM = int(os.environ.get("COMPANY_EMBED_DIM", "1024"))
```
**NEW:**
```python
# Embedder dim contract (rule 4): pplx-embed-context-v1-4b = 2560-dim. Config-driven, not a node literal —
# a wrong-length vector FAILS LOUD at the fabric, never flows through as a bad cosine.
DEFAULT_EMBED_DIM = int(os.environ.get("COMPANY_EMBED_DIM", "2560"))

# OPERATIVE EMBEDDING LAYER (multi-layer #emb=<tag> model, 2026-06-15): the layer the corpus read/write
# paths resolve to when a caller does NOT pin one. 'pplx' = the live pplx-2560 layer is the default; the
# bge bare/None layer stays reachable EXPLICITLY (emb=None / 'bge'). ONE knob reverts the whole core.
DEFAULT_EMB_LAYER = os.environ.get("COMPANY_EMB_LAYER", "pplx")
EMB_LAYER_DEFAULT = "__default__"   # sentinel: caller omitted emb → use DEFAULT_EMB_LAYER

def resolve_emb_layer(emb):
    """Resolve a caller's emb arg to a concrete storage-layer tag for store.space_address.
    - EMB_LAYER_DEFAULT (param default → caller didn't pin) → DEFAULT_EMB_LAYER ('pplx').
    - None / '' / 'bge' / 'bare' → None (the bare/legacy default-layer key — bge reachable explicitly).
    - any other string → that explicit layer tag (e.g. 'pplx')."""
    if emb == EMB_LAYER_DEFAULT:
        emb = DEFAULT_EMB_LAYER
    if emb in (None, "", "bge", "bare"):
        return None
    return emb
```

## EDIT 2 — `store/vector_index.py`: resolve the layer at the two chokepoints

**`build_index` (sig line 64–65):** change `emb=None` → `emb="__default__"`. After line 92 (`dim = fcfg.DEFAULT_EMBED_DIM if dim is None else dim`) add:
```python
    emb = fcfg.resolve_emb_layer(emb)   # __default__ → DEFAULT_EMB_LAYER (pplx); None/'bge' → bare layer
```
(`fcfg` already imported at line 89.)

**`query_index` (sig line 142):** change `emb=None` → `emb="__default__"`. As the first body statement add:
```python
    from fabric import config as fcfg
    emb = fcfg.resolve_emb_layer(emb)   # omit-emb callers (query_corpus/consult) → pplx; explicit None → bge
```
> Effect: every `query_index`/`build_index` caller that OMITS `emb` now reads/writes the pplx layer. Callers passing `emb=None` explicitly still hit the bge bare layer.

## EDIT 3 — `runtime/cognition.py` `embed_corpus_to_spaces` (sig line 387): capture writes the pplx layer

Change `emb=None` → `emb="__default__"`. (It threads `emb` into `bi_kw` → `build_index`, which now resolves `"__default__"`→pplx. So `mcp__company__ingest` capture writes the pplx layer — matched with reads.)

## EDIT 4 — `runtime/suite.py` `find_relations` (sig line 10856): default to the pplx layer

Change `emb: str | None = None` → `emb: str = "__default__"`. As the first body statement (before the `space_address` calls at ~10891) add:
```python
        from fabric import config as _fcfg
        emb = _fcfg.resolve_emb_layer(emb)
```
(It already does `from store import vector_index as _vx`; `emb` then flows correctly into both `space_address` and `query_index`.)

## NO CHANGE NEEDED
- `query_corpus` (10837): omits `emb` → `query_index` resolves → pplx. Embeds query text via `_embed_consult_query` (now pplx via config). ✓ proven.
- `_embed_consult_query` (4706): uses `DEFAULT_EMBED_*` (now pplx). Only its docstring ("BGE-M3 @ …") is stale — cosmetic.

---

## ⚠ ONE RESIDUAL the lead must decide — the UNSPACED default index (consult/R2)
`_retrieve_for_consult_semantic` (suite.py:4754) calls `query_index(self.store, qvec, k=8, with_note=True)` — **space=None, emb omitted**. Post-switch that resolves to the **unspaced pplx layer, which is EMPTY**: the 78 bare-key vectors (`code://implement/resurface_crashed`, …) are all bge-1024 (`emb=None`), with NO `#emb=pplx` twin. So consult's semantic path returns an honest-empty note and **degrades to keyword** (NOT a crash — no vector to cross-dim, so the fail-loud doesn't fire here; it's the sanctioned "empty index" path).

**Options (lead's call):**
- **(a) Tiny re-embed (recommended):** re-embed the 78 unspaced bare-key entries into the pplx layer in the smoke-test window — one batch, trivial GPU — and consult's semantic path is fully restored. Keeps "no heavy GPU pass" true (78 ≪ the done 2919).
- **(b) Accept keyword-only** for consult's small unspaced index until a later pass (zero work now; consult still works, just not semantic on those 78).
- **(c) Point consult at a populated space** (e.g. repo/principles) — small code change in `_retrieve_for_consult_semantic`.

## RESTART + SMOKE-TEST GATE (lead sequences; ch-83e2cque runs the gate)
After apply: ONE `mcp_face` restart (loads the switch + clears the stale 2-arg `space_address` crash). Then my GATE before any embed write / the pilot:
1. `corpus(op='query', space='repo', text='…')` → expect ranked hits (NOT "embed endpoint unreachable").
2. `ingest(paths=[one .md], force=True)` → expect `captured:1` (no `space_address` crash).
Both green → pilot + (if chosen) the 78-entry consult re-embed proceed.

## Finding 1 (walker) — lead owns: add `.ts/.tsx/.js` to `WALK_EXTS` in `flows/repo_ingest.py`.
Deeper fix-reference (from ch-piffgfxv): `.discovery/implementations/pipeline/src/discovery_pipeline/extractors/` already does language-aware + EMBEDDED-language extraction (server.py's inline JS/HTML/SQL). Extensions alone comprehend `.ts` as text; the extractors handle it as code. Separate follow-up.
