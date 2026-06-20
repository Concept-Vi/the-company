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

## ★ THE BAKE STRATEGY — RESOLVED by convergence with fork's PARAM-MAP (678e7f6)
My earlier A-vs-B framing is SUPERSEDED. fork's resolution-mechanism answer gives the right design: **the GRAIN axis = the resolver PROJECTS the rich superset DOWN to the requested grain at read-time (MRL), so the bake is done ONCE on the superset.**
- **Down-projection is FREE** (rich store → coarse view = field-subset selection at determine-time). **Up-projection is IMPOSSIBLE** (coarse store → fine needs re-extraction = the bad-wasteful Tim warned against). So my "lean-B (coarse-universal + fine-on-demand)" was WRONG — fine-on-demand IS re-extraction. CORRECTED.
- ⟹ **BAKE THE FINE SUPERSET ONCE** (all fields), resolver projects down by grain: `resolve(grain)→schema-subset` (coarse `{about,kind,touches}` ↔ fine full). One stored asset serves ANY determine at ANY grain, never re-extracted. This IS Tim's "variable granularity" — the grain is a read-time projection of the one rich asset.
- WHY the fine fields belong in the superset despite sparsity (relations 3/15, open_questions 1/15): never-re-extract (the whole point) · empty lists are cheap to STORE · the chunks that DO carry relations (specs/decisions) are exactly the high-value ones for the theorem-mine. The one-time gen-cost is free + overnight.
- **THE REMAINING SUB-QUESTION (not A/B — it's throughput):** the fine superset measured ~1.8 chunks/s on a small batch (full 35,904 ≈ 5.5h) — but that's UNSATURATED. Real full-scale throughput with 32-concurrent vLLM batching + the local extraction workhorse (chat-2b/4b — fork's "local=extraction/MAP") is a fork+recollection measurement before committing the run. AND it needs the LEAD's VRAM call (a local extraction model resident — fork's PARAM-MAP §provider-reality). So: superset-once is the strategy; the bake fires once (a) Tim okays the schema, (b) fork+I measure real throughput, (c) lead loads the local extraction model.

## STATUS
Schema designed + proven viable by-use (accurate, fills correctly, sparse-when-absent). NOT baked (per the gate: schema-first, quick look before the run). Awaiting: Tim's nod on the schema + the (A)/(B) bake-strategy; fork/composition on the resolution mechanism. THEN recollection fires the full extract on the agreed schema+grain. The extraction layer = the dragnet riding the spine (the asset itself a resolved variable).