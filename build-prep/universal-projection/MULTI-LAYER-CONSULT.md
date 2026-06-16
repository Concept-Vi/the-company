# MULTI-LAYER / PARENT-WORK CONSULT — projection's answer

*Tim-directed (relayed by lead `ch-al7jdfdr`, thread `t-1781594751-ch-al7jdfdr`). Tim's words: "ask project about the pplx relative to parent work we did and the multi embedding." Context: lead switched corpus-embed DEFAULT bge-1024 → pplx-2560, coupled write==read, bge dormant as explicit fallback (commit `1f88727`); omit-emb now resolves to pplx everywhere. This is the design picture the migration should be built to respect. Written expansively, not as a confirmation. — projection (the build-loop that built the scale-pyramid + multi-layer #emb work WITH Tim).*

---

## 0 · THE EVIDENCE BASE (verified myself, not relayed — full store scan, 5,852 vectors)

I scanned every vector file in `.data/store/vectors` and tallied `(space, emb, dim)`. This is ground truth, not the relayed audit:

**MAIN spaces** (`space → {layer: count (dim)}`):
| space | default (bge) | pplx | note |
|---|---|---|---|
| `common_knowledge` | — | 102 (2560) | **pplx-ONLY** — recollection's new pilot; no bare layer |
| `history` | 1464 (1024) | 1464 (2560) | dual, balanced |
| `operators` | 29 (**2560**) | 29 (2560) | **ANOMALY: default is 2560, not 1024** — the only space whose two layers are same-dim |
| `principles` | 162 (1024) | 162 (2560) | dual |
| `repo` | 644 (1024) | 645 (2560) | dual; +1 pplx drift (the `.ts` walker) |
| `topics` | 163 (1024) | 162 (2560) | dual; +1 default drift |
| `worldview` | 162 (1024) | 162 (2560) | dual |

**SCALE spaces** (the pyramids = candidate "parent work"; `scale:<space>:k<K>`):
| pyramid | default | pplx | rung ladder |
|---|---|---|---|
| `scale:repo:*` | — | yes (2560) | **pplx-ONLY**, k4/k16/k64 |
| `scale:history:*` | — | yes (2560) | **pplx-ONLY**, k4/k16/k64 |
| `scale:operators:k8` | 8 (2560) | 8 (2560) | dual |
| `scale:principles:*` | 1024 | 2560 | dual, k8/k32 |
| `scale:topics:*` | 1024 | 2560 | dual, k8/k32 |
| `scale:worldview:*` | 1024 | 2560 | dual, k8/k32 |

**UNSPACED: 78 vectors, `space=None`, `source=None`, `emb=default`, `model=BAAI/bge-m3`, dim 1024.** These are the consult/R2 "dead orphans" — confirmed directly: no space, NO SOURCE ADDRESS → they resolve to nothing, render nothing, attribute to nothing. Not a layer to choose; garbage to drop.

**The landscape is ALREADY non-uniform in TWO ways** — this is the crux of the whole answer:
1. **Which layers a space carries varies**: pplx-only (common_knowledge, repo/history pyramids) vs dual (everything else).
2. **What "default" even means dimensionally varies**: operators' default = 2560; everyone else's default = 1024. So "the default layer" is not one geometry.

---

## Q1 · "PARENT WORK" — what Tim means, and how pplx relates

I can't resolve the exact referent from here, and shouldn't pretend to — Tim rejects standard vocab, so "parent work we did" could be any of three. **I cover all three; lead, please let Tim cheaply correct the referent if I've mis-aimed:**

**(a) STRONGEST — the SCALE PYRAMID nesting hierarchy (`runtime/scale.py`, Group 11).** This is the work with a literal *parent* concept that Tim and I built together. The pyramid is **hierarchical (Ward agglomerative)** so the rungs **NEST**: `unit ⊂ fine cluster ⊂ coarse cluster`. Each coarse cluster records `children_finer` — the explicit cross-rung **parent→child links**. A coarse centroid IS the parent of the finer clusters that fold into it. (scale.py even documents a *reversal we did*: from a lineage parent-hierarchy `unit⊂session⊂project` — killed because within a space `session` is just capture-batch provenance — to MEANING centroids. That reversal is itself "parent work we did.")

**How pplx relates — directly and concretely:** *a pyramid is a PER-LAYER artifact.* Every centroid is the normalised mean of its members' vectors **at one embedder layer**; it inherits that layer's model and dim. The evidence shows this split now:
- `scale:repo:*`, `scale:history:*` were **rebuilt at pplx-only** → their parent hierarchy now lives ONLY at pplx (k4/k16/k64).
- `scale:principles/topics/worldview/operators` still carry a **bge-1024 parent hierarchy AND a pplx-2560 one** — two parallel pyramids, different geometries.

So the pplx switch did NOT just re-embed leaves — it (partially) **re-parented the hierarchy at a new layer for some spaces and not others.** That's the live consequence, and it's exactly what bit me in regression `3560163`: `resolve_at_rung` was querying a pyramid at the wrong layer → empty `ranked`. The fix threads `emb` explicitly so the rung is always queried at the layer its pyramid was built at.

**(b) the LINEAGE / parent-SPACE reading** — corpus.record lineage (unit ⊂ session ⊂ project), or a parent-space relation across spaces. scale.py's docstring records why we abandoned lineage-as-pyramid *within* a space (provenance, not meaning), but lineage may still be the "parent" Tim means at the cross-space level. If so: the pplx switch is layer-orthogonal to lineage (lineage is a metadata edge, not a vector), so it's unaffected — but say the word and I'll map it.

**(c) "foundational prior work we did"** (Tim's non-standard vocab) — if "parent work" just means the prior projection/scale/multi-layer foundation, then the whole axes picture below IS the answer.

---

## Q2 · MULTI-EMBEDDING — is the intent multi-layer, and does a single pplx DEFAULT conflict?

**The intent is unambiguously multi-layer, and the store proves it's REAL, not aspirational:** 6 of 7 main spaces carry TWO live layers right now (bge-1024 + pplx-2560), the `layers` tool exposes them as a drivable axis, and the UI LayerChip + the `#emb=`/`?emb=` fragment make the layer a *variable the operator picks*. This is Tim's law made concrete — "everything is a variable, nothing static": a unit isn't one vector, it's a stack of layers, and the lens you read it through is chosen, not fixed.

**Does a single pplx default conflict? Tim's instinct is RIGHT to worry — and the honest answer is NOT "the default is fine."** Here's the precise distinction:

> **A default is a *resolved variable*, not a *collapse* — but a default silently BECOMES a de-facto *only* wherever a read path omits `emb`.**

That's not hypothetical. It's literally my `3560163` regression and my standing latent-risk flag: the moment `query_index`'s omit-default shifted to pplx, every omit-emb caller silently re-pointed to a different layer. On a pplx-covered space that's invisible; on a bare-only or wrong-layer-pyramid space it **silent-empties**. With the landscape already non-uniform (§0), omit-emb is a loaded gun.

**So the multi-layer model survives the default ONLY IF:**
1. **Layers stay present + load-bearing** — bge "dormant" (present, not default) is fine; bge *deleted* would be the real collapse. (Right now bge is present on 6 spaces — good.)
2. **`emb` is EXPLICIT in every read path where layer-consistency matters** (the `3560163` pattern), so "default" never silently becomes "only."
3. **Composition becomes a REAL lens**, not an implicit behavior.

**On "should the corpus COMPOSE across layers rather than default to one?" — yes, but composition is LATE FUSION, never a vector merge:**
- bge-1024 and pplx-2560 are **different models at different dims**. You **cannot** concatenate, average, or cosine across them. Cross-layer composition must be **rank-fusion (RRF), score-blend, or rerank** — combine each layer's *ranked list*, never its raw vectors.
- **MRL/`dim` composes WITHIN a layer, not across it.** Pre-empt the tempting trap: *do not truncate pplx-2560 to its first 1024 dims to "match" bge-1024.* The first 1024 dims of pplx are not bge's 1024 dims — different model, incomparable axes. `dim` is a coarse↔fine zoom *inside one layer's* geometry.
- **One real exception** (the operators anomaly): `operators` carries default-2560 AND pplx-2560 — same dim. Those two *could* fuse at the vector level. But that's an accident of operators' default model, not a general capability — don't generalize it.

**Bottom line for Q2:** keep the default as a *convenience resolution of a variable*; keep the layers present and explicit; make cross-layer composition an additive fusion lens (a new binding), and make multi-ness EXPLICIT in read paths rather than relying on one implicit default. Tim's worry is the correct worry; the fix is explicit multi-ness, not a silent single default.

---

## Q3 · CONSULT / R2 + SCALE READS — single pplx, or compose across lens-spaces?

**SCALE READS — not a preference, a correctness constraint:** *query a pyramid at the layer it was built at, and match the query vector's layer to the pyramid's layer.*
- `scale:repo:*`, `scale:history:*` are pplx-only → must read pplx (embed the query at pplx). omit-emb→pplx happens to work today, but **pass `emb='pplx'` explicitly** (per `3560163`) so it survives any future default change.
- `scale:principles/topics/worldview/operators` carry both → read the layer that matches your query vector; **never cross** (a bge query vector against a pplx centroid is a dim-mismatch crash — fail-loud by design, but don't author it).
- If a layer's pyramid doesn't exist for a space you need, **build it** (additive); don't expect one read to span layers.

**CONSULT / R2 — the dead-orphans fix is NOT a layer choice:**
- The 78 unspaced vectors (`source=None`, bge-1024) resolve to nothing. **Drop them** — they can't be a retrieval base because they return nothing renderable/attributable. This is staleness (an index that outlived its corpus), not a layer to pick.
- Retrieve over the **LIVE, SPACED corpus at the live layer (pplx)** — which recollection's `common_knowledge` pilot now provides: 102 pplx units, surviving sources, **render-proven today** (the centred projection works end-to-end; see render proof below). Correctness-first, single-layer.
- **The reranker is the right FIRST "composition"** (lead built it: `ops/rerank.py` @ :8008, jina-reranker-v3, CPU/0-VRAM): pplx single-layer retrieve → rerank reorder (toggle, fail-loud). That's late fusion of *embedding-retrieval × cross-encoder judgment* — cleaner and safer than cross-layer vector fusion, and it composes regardless of the multi-embedding decision.
- **Cross-layer / cross-lens rank-fusion = FAST-FOLLOW enrichment**, gated behind single-layer+rerank working. This matches the lead's own framing (multi-embedding REFINES what the drill surfaces, not a blocker) AND Tim's "stack all work, don't filter by impact" — I'm not dropping fusion, I'm **sequencing** it behind a correct base. The dead-orphans bug is the cautionary tale: complexity over a broken base.

---

## THE GOVERNING RULE (the one line the migration should respect)

> **A layer is a per-unit variable. The default is a *resolution* of that variable, not a *collapse* of it. Multi-ness survives only when (1) the layers stay present, (2) every read path that cares names its `emb` explicitly, and (3) composition across layers is an additive late-fusion lens (rank-fusion / rerank) — NEVER an implicit cross-layer vector merge, and NEVER an MRL-truncation pretending one layer is another.**

## MIGRATION CHECKLIST for recollection (what to respect)
- [ ] Don't read the 78 unspaced bge orphans; retrieve over live spaced corpus.
- [ ] Consult/R2: pplx single-layer retrieve → rerank (toggle, fail-loud). Fusion is fast-follow.
- [ ] Every scale/retrieval read names `emb` explicitly (don't lean on the global default).
- [ ] Keep bge present (dormant ≠ deleted); the layer axis must stay drivable.
- [ ] If you need a bge-layer pyramid (or any space's missing layer), build it additively — don't cross layers in one read.
- [ ] Heads-up the non-uniformity: common_knowledge & repo/history-pyramids are pplx-only; operators' default is 2560. An omit-emb read is only safe where pplx exists.

## RENDER PROOF (Q3's hardest evidence — the seam is closed)
`project(space=common_knowledge, center=code:///home/tim/recollection/test/sync.test.ts, emb=pplx)` → centre **r=0.0**, `sync-error-sentinel.test.ts` **r=0.06**, `version-consistency.test.ts` **r=1.0**. Radius = cosine meaning-distance over recollection's freshly-published pplx index. The comprehend→publish→project()→resolve() circuit is demonstrated through the live interface. common_knowledge reads omit-emb→pplx layer-consistently; a wrong-layer/wrong-address centre fails loud (no silent fallback). Verified by use, 2026-06-16.
