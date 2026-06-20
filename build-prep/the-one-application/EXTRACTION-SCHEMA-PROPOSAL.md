# The dragnet EXTRACTION SCHEMA — proposed (proven by-use) for the quick-look before the bake

*Tim's gate (lead g-1781962851): SCHEMA-FIRST before the 85min+ extract — the asset's schema bakes on that run, so get it RICH + RESOLUTION-VARIABLE (grain-scalable) first. recollection owns the asset schema. Proven by-use on local-4b 2026-06-20 before proposing (default-to-wrong: a rich schema the worker can't fill accurately = a garbage asset). Render-independent; keystone holds.*

## THE PROPOSED SCHEMA (grain-tiered — the granularity IS the resolution coordinate)
The extraction is the chunk's reusable representation: a future "determine relevance to topic X" reads THIS, never re-reads the chunk. Grain tiers nest (coarse ⊂ medium ⊂ fine) so `resolve(grain=G)` → the fields + the prompt for that grain.

```
COARSE  (cheapest determine — always present)
  about:    str          # one phrase: what this content IS
  kind:     str          # decision | digest | discussion | spec | log | reference | other
  touches:  list[str]    # topic/domain tags
MEDIUM  (+ entity/summary determine)
  summary:  str          # 1-2 sentence neutral summary
  entities: list[str]    # named things: systems, files, concepts, people
FINE    (+ claim/relation/thread determine)
  claims:        list[str]   # assertions/decisions stated
  relations:     list[str]   # "X depends on Y" / "X supersedes Y"
  open_questions:list[str]   # unresolved threads ([] if none)
```

## PROVEN BY-USE (15 real corpus chunks, local-4b, before the bake)
- **Accuracy: clean, NO hallucination** — spot-checked extractions vs the actual chunk text; about/kind/entities/claims accurate; CHUNK[2] correctly produced relations ("mine_exchange extract depends on RAW source exchange", "judge triggers the no-fiction gate"). kinds classified right (digest/spec).
- **Fill-rate (does local-4b populate the rich fields?):** about/kind/touches/summary/entities = 15/15 · claims 13/15 · relations 3/15 · open_questions 1/15. ★ The low fine-field rates are CORRECT SPARSITY (most chunks genuinely have no explicit relations/threads — the model left them empty rather than fabricating). Empty-when-absent is the right behavior; no hallucinated relations.
- **Throughput is GRAIN-DEPENDENT** (the reason grain-as-resolution matters): rich/FINE ≈ 1.8 chunks/s (full 35,904 ≈ 5.5h) · COARSE {about,touches} ≈ 7/s (≈85min) · binary ≈ 18/s. Richer schema = more tokens = slower. Free + local + overnight, but the grain choice is a real cost lever.

## THE RESOLUTION-VARIABLE ANGLE (my part = the schema's grain axis; fork/composition = the mechanism)
- The schema is designed AS a grain coordinate: `resolve(grain)` selects {coarse | +medium | +fine} fields AND scales the prompt to match (the prompt asks for exactly the resolved fields). That's "prompt + output_schema as a variable resolution at variable granularity" — the schema side.
- fork (mechanism): can a role's prompt+output_schema resolve(coordinate)→prompt/schema today, or is it role-swap only? (their lane — the resolution engine).
- composition (contract): is "prompt"/"output_schema" a resolvable VARIABLE TYPE in the resolver? (the spine question).
- If swap-only today: the grain tiers can ship as 3 role variants (coarse/medium/fine roles) NOW + become coordinate-resolved when the mechanism lands — additive, not blocking.

## ★ THE BAKE-STRATEGY DECISION (for Tim's quick look — the throughput exposes it)
Given coarse≈85min vs fine≈5.5h, two ways to bake the asset:
- **(A) Full-rich-once** — extract ALL fields over the whole corpus in one ~5.5h overnight run → maximally reusable asset, never re-extract (matches "re-extracting is bad-wasteful, get it right once"). Cost: 5.5h saturating local-4b; fine fields sparse on most chunks (some wasted generation).
- **(B) Coarse-universal + fine-on-demand** — extract COARSE+MEDIUM over the whole corpus (~85min) as the universal asset → run FINE only on the SURVIVORS of a given determine (cheap, targeted). Matches grain-as-resolution: store the cheap universal layer, resolve fine per-need. Cost: a determine needing claims/relations pays a small fine-pass on its survivors.
- LEAN: (B) — it IS the grain-as-resolution design Tim's pointing at (the asset resolved at the grain a question needs, not maxed upfront), and it avoids 5.5h of mostly-sparse fine generation. But (A) is defensible if "one maximally-rich asset, never re-touch" is the priority. ← TIM'S CALL.

## STATUS
Schema designed + proven viable by-use (accurate, fills correctly, sparse-when-absent). NOT baked (per the gate: schema-first, quick look before the run). Awaiting: Tim's nod on the schema + the (A)/(B) bake-strategy; fork/composition on the resolution mechanism. THEN recollection fires the full extract on the agreed schema+grain. The extraction layer = the dragnet riding the spine (the asset itself a resolved variable).