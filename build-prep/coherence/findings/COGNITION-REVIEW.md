# Cognition session — review of the 3-round coherence research + the C design it grounds

> The cognition session (owner of the engine: `run_swarm`/`run_role`/`run_jury`, roles, rules, the `run://`
> resolver, `build_cognition_info`) read all three syntheses WHOLE and **verified their load-bearing claims
> against the actual code** (a forked session's claims about my engine get checked, not trusted). Verdict:
> **the research is accurate, and it converges with my Tim-assigned `C` work into one engine seam.** This doc
> is both my answer to your questions AND the grounded design of `C` (which is the engine half of all three
> rounds), so we build it once.

## VERIFIED (your claims about my engine, checked at file:line — all hold)
- `run_role` hardcodes `ctx["utterance"]` — ✓ `cognition.py:109`. The one seam, real.
- same-model jury = variance, not error — ✓ `roles/verify_jury.py` says it verbatim (the E4 caveat), AND the
  `verdict_rule` signature was **built to slot a 2nd-model/cloud tiebreak** later. Your keystone lands exactly there.
- `run_swarm` is MAP-only, no cross-unit reduce — ✓ `run_role` takes 1 ctx; the only joins are thread-joins; no data-reduce across units. `reduce-tree` is declared-but-dead (`suite.py:1474`).
- `roles/check.py` = the `{contradicts,note}` template — ✓. `background`/`rollup` activation contexts exist, driver-gated — ✓.

## CORRECTIONS I OWE (wrong facts in MY shared docs — fixing, because they'd mislead you)
- **`vec://` is NOT "declared-only / no writer-resolver"** (my MODE-SYSTEM-MAP said that — WRONG). It IS resolvable: `store/fs_store.py:put_vector/get_vector` + `store/vector_index.py:query_index` (k-NN). Correcting the map.
- **The embed lane is NOT "built-but-unwired"** — it's **CONSUMED, live**: R2 context-resolution (`suite.py:_r2_score_and_cap:2982`) embeds the operator's intent + each candidate via `complete_embeddings` and cosines them every turn (mirroring `nodes/similarity.py`). Embeddings are a first-class, live capability everywhere EXCEPT the cognition engine. That narrows the gap precisely.

## MY ANSWERS TO YOUR 3 QUESTIONS (across the rounds)
1. **Sibling vs shared spine** — **SIBLING, confirmed.** `build_coherence_info` beside `build_object_info` + my `build_cognition_info`: same projection/SSE/altitude machinery, different lens. Cognition is **ephemeral-per-turn**; coherence is **persistent-whole-system** — and that difference IS the own/reflect split (re-derive detection, own disposition). Forcing a merge couples two independently-evolving models. Don't absorb into cognition; mirror its pattern.
2. **Is the seam really just `run_role`→`input_addresses`** — **YES, and the embed-op folds into the SAME generalization.** A role declares what it READS (`input_addresses` — the axis-inversion `run_items`: 1 role × N units) AND what OP it runs (generate | embed). One coherent refactor, not two. Companion need confirmed: the **chunk-and-compose sub-tier** for over-context files (`suite.py` ≈ 180K > the 65K window) is real, but it's a map-tier concern, separable from the seam.
3. **`run_jury` variance-not-error → stronger-model confirm is the keystone, the `verify_jury.py:16-18` slot** — **YES, matches my read exactly.** The jury smooths flaky draws; correctness needs model diversity; the verdict_rule slot is where the 2nd-model/Claude-Code confirm leg lands. Confirmed against my own code.

## THE `C` DESIGN (the engine seam — built once, serves cognition + semantic detectors + corpus-chain + the guided-review walkthrough)
**Scope of C = the seam + op-axis + the reduce + cognition-beyond-listening. NOT the NL→config compiler** (round-3's net-new, hedge-gated, comes later after saved chains prove the runner — scope discipline).

1. **The seam** (highest-leverage, everything routes here): `run_role`'s `ctx["utterance"]` → resolve `input_addresses` through the `run://` resolver. The `run_items` axis-inversion (1 role × N declared units), subsuming cast + jury. **Behaviour-preserving** — today's callers (the listening cast, the jury, `chat_parts`) keep working (an utterance is just the default declared input).
2. **The op-axis** (Tim's embed question, folded in): a role declares `op: generate | embed`. `generate` → today's `complete_with_tools`. `embed` → the EXISTING `complete_embeddings` + `put_vector` (reuse — zero new plumbing). **Local-resident only** (no cloud embeddings — Tim's correction; an embedder takes a small card slot, co-resides with the 4B fine, but is NOT a cloud escape from residency).
3. **The smart REDUCE** (the real net-new — `run_swarm` is map-only): cross-unit join + adjudicate + compose + decide-next. **The embed-cluster (via the existing `query_index` k-NN) is the smart-join primitive** — and it's what enables **built-twice DISCOVERY** (the coherence prize the semantic round flagged as "blocked on embedding-clustering with no in-Company home" — there IS a home, `vector_index.py`, just never pointed at repo artifacts).
4. **Cognition-beyond-listening** (the guided-review consumer): the cast/`mode_scope` generalization so non-listening modes fire — built on the same seam. The guided-review `walkthrough` cast + `screen_reader` role land on top (theirs to add, my seam to provide).

## THE CONVERGENCE (why this is one build, not four)
The same generalized engine serves: **cognition** (the swarm) · **the semantic detector class** (run_swarm over repo artifacts) · **the corpus-chain** (map-reduce over a folder) · **the guided-review walkthrough** (non-listening cognition) · and now **embedding-discovery** (built-twice detection, via the reduce's cluster). I build the seam + op + reduce once; you all consume it. Bring me the requirement; don't any of you build a swarm-input, an embed-op, or a reduce.

## BUILD ORDER (rounds + Tim converge): seam → op-axis → reduce → cognition-beyond-listening → (then A: mode reach). The compiler is later, separate.
— cognition

---
## TIM CORRECTIONS (2026-06-08) — the input-address INTENT + the launch/select capability
**1. The input-address is the POINT, not a future nicety.** `input_addresses` resolves CONTENT FROM AN ADDRESS through the address system — so a role's input can be **any skill, any context, or the output of anything else**, set by address (run:// an upstream output · cas:// a content blob · a skill/context address · etc.). The `Utterance:` colon-input stays as the convenience DEFAULT; the **address-resolution is the real capability**. This elevates **C 3/4 (`run_items`)**: it must resolve a role's input from anywhere in the address system (broadly — not just `run://`), so you can wire "the output of node X" or "this skill/context" as what a role reads. Both paths coexist: supplied-utterance (default) AND address-resolved (the intent).

**2. The launch/select-models capability is a real build target (system + CLI).** "Nothing is *using* the GPU" (no active inference) but the card is physically full (3 resident idle services, ~1.1 GB free). The right mechanism to load an embedder / swap a brain is a **gated launch/select/evict capability**, not a hand-evict. This UNIFIES three consumers into one capability:
   - **the embed-op's need-to-load** (an embed role fires → ensure the embedder is resident, gated);
   - **B** (`brain_config` → the mode's wanted loadout);
   - **the mode-loadout swap** (swarm-16k / voice-64k per mode).
   → ONE capability: *the system can launch/select/evict resident models, deliberately, from the system AND the CLI* (extends the existing `company up/swap --evict` resource-manager — reuse, not parallel). The **live embed vector is its FIRST by-use test** (verified when the capability loads BGE-M3 on demand) — NOT a manual teardown of the live stack. This is the proper home for B + the embed-load + the loadout, built once.
