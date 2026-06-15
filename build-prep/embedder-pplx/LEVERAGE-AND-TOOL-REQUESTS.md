# pplx-embed-context-v1-4B — MAXIMAL LEVERAGE + TOOL REQUESTS (the surface embedder)

**Decision (Tim, 2026-06-15):** "take the strongest, and leverage absolutely everything you can with it."
The Company's embedder becomes **`perplexity-ai/pplx-embed-context-v1-4b`**. Add it to a **loadout for this
surface**. Where a tool can't yet exploit a capability, the detailed request is written HERE (company MCP tools
AND the company CLI) to be added. Living doc — update in place.

This supersedes the old default ([[project-embedding-model-decision]] picked pplx-4b over Qwen3-8B for VRAM;
this goes further — pplx is now THE embedder, fully leveraged, replacing the legacy BGE-M3 corpus).

---

## 1. The model — verified facts (research.perplexity.ai + HF card + local measurement)

| Property | Value | Source |
|---|---|---|
| Family | `pplx-embed-v1` (dense) · **`pplx-embed-context-v1`** (context-aware) | Perplexity research, Feb 2026 |
| Base | **Qwen3 → bidirectional encoder via diffusion continued-pretraining** | research post |
| Dimensions | **2560** (4B) · MRL-truncatable | HF table + measured locally (2560) |
| Context | **32,768 tokens** | HF table |
| Quantization | native **INT8 (4×) / binary (32×)**, quantization-aware-trained | research post |
| Instruction prefix | **not required** (deliberate — no prompt-drift) | HF card |
| Pooling | mean | HF table |
| Quality | SOTA-class: MTEB-Multilingual-v2 ≈ Qwen3-Emb-4B, > gemini-embedding-001; **beats BGE-M3 head-to-head** (71.1 vs 61.8 Recall@10) | research post |
| Context bench | **ConTEB SOTA 81.96 nDCG@10** (> voyage-context-3 79.45) | research post |
| License | MIT | HF |
| **Local serving** | `:8007`, ~8.2 GB, `ops/serve_pplx_embed.py` (raw transformers + FastAPI; vLLM lacks the arch). **Exposes ONLY `/v1/embeddings`** (pooled, one-text→one-vector). dtype bfloat16. | services.json + serve script |

The legacy corpus is **BGE-M3 (1024-dim, `:8001`, currently DOWN)** — every existing space (repo/principles/
worldview/topics/history + pyramids) is BGE 1024. Switching to pplx means re-embedding (incomparable across
models) — see §4 migration.

---

## 2. THE CROWN UPGRADE — context-as-parent-context (Tim's insight, CONFIRMED)

Tim: *"I wonder if [context-relative-to-document] can work for technically non-document things… context of a
thing in the context of its parent thing… a perfect match for this instrument."* **Yes — and it is.**

**Mechanism (HF model card, `extract_chunks_from_concatenated`):** the context model embeds a GROUP of items by
(1) joining them with the SEP token into one sequence, (2) running **full bidirectional attention over the whole
sequence**, (3) mean-pooling each item's token span back out (split at SEP positions). The model has no concept
of "document" — **the "parent" is simply whatever items you choose to embed jointly.** Each item's vector is
therefore *informed by every sibling in the group* = "this thing, as it sits among its siblings, inside its parent."

**This generalizes to the Company's fractal structure — every parent→children relation:**
- a **registry → its rows** (operators among operators; projections among projections)
- a **type → its fields**
- a **space → its units**
- a **sector (the wheel division) → its points**
- an **address subtree → its child addresses** (the address spine IS a parent-child tree)
- a **cascade → its steps**, a **document → its lens-extracts**

**Why it's a perfect match for THIS instrument** (the instrument reads things *in their place*, not in isolation):
- **Nucleation** (where a registry under-covers its content): with context-embedding, a row's vector reflects how
  it differs from its siblings → "fits / piles / corners" become *context-true*, not isolated-text artifacts.
- **Strain** (structure↔meaning gap): meaning measured *with* the parent's context → the gap is the real
  translation-loss, not a chunking artifact.
- **find_relations** (cross-space set ops) over context-aware vectors → relations reflect role-in-context.
- **The coincidence spine / the whole seed**: "the real = a thing addressable in its parent frame" — the
  embedder now natively encodes exactly that.

**Constraint:** a parent's children must fit in 32K tokens *concatenated*. Registries (29 roles, 8 projections,
…) fit trivially. Large spaces (644-unit repo) need batching by parent-subgroup or a representative-context
window — a knob in the capture path (§3.2).

### 2a. EMPIRICAL FINDING (2026-06-15) — context is NOT a free win; the GROUPING is decisive
Proved it before migrating (the existing `:8007` `documents` endpoint, no server change). Embedded the 29 OPERATORS
two ways: PLAIN (each alone) vs CONTEXT (all 29 as one parent-group). Script: `$CLAUDE_JOB_DIR/tmp/context_proof.py`.
- **Context genuinely moves the vectors** — mean cos(plain, context) = 0.847 (repo_digest → 0.751). Late-chunking
  is real and generalizes to non-document things. ✓ (Tim's mechanism confirmed.)
- **BUT embedding a whole registry as one group HOMOGENIZES it** — operator-family separability *fell*: intra−inter
  cosine margin went 0.169 (plain) → **0.097 (context)**, Δ **−0.072**; only **5/29** roles tightened toward their
  family. Both intra (0.485→0.607) and inter (0.316→0.510) rose, but inter rose MORE → the shared "we're all
  operators" parent-context pulled everyone *together*, washing out the distinctions.
- **Why:** pplx-context is built for RETRIEVAL DISAMBIGUATION (a chunk found via its document's context — it is
  ConTEB SOTA at that). Our **nucleation/strain are DIFFERENTIATION readings** (how a thing differs *within* its
  type). Context that disambiguates-for-retrieval can *homogenize-for-differentiation*. Opposite goals.
- **Decision (refined):** the migration's safe, universal win is **PLAIN pplx** (2560-dim, already beats BGE-M3
  on quality — that's the real upgrade). **Context-aware embedding is SELECTIVE, not blanket:** only for a
  genuinely COHESIVE parent whose shared context *disambiguates* its members (e.g. a real document's lens-extracts,
  a thread's turns) AND only proven per-case. Do NOT context-embed a heterogeneous registry for nucleation —
  it degrades the very separability the lens needs. This saved the instrument from a plausible-but-wrong upgrade.

---

## 3. TOOL REQUESTS (detailed — to be added into the tools)

### 3.1 contextual endpoint — ✅ ALREADY EXISTS + VERIFIED (no build needed)
`ops/serve_pplx_embed.py` already exposes late-chunking: `POST /v1/embeddings` with an optional **`documents`**
field `[[c1, c2, …], …]` (a list of parent-groups, each a list of child texts) → calls the model's native
`.encode()` and returns one row per (document, chunk), tagged in `meta:{document,chunk}`. Plain `input` mode
(each string = a single-chunk doc) is the default. Verified 2026-06-15: a 29-child group returns 29×2560
context-aware vectors, and the context vectors differ from the plain ones (mean cos 0.847 — §2a). So the
mechanism is fully servable today. The OPEN question was never "can we serve it" but "does it HELP" — answered
in §2a (helps retrieval; homogenizes registry-differentiation). No serve-script change required.

### 3.2 capture / embed seam — context-aware embedding (`runtime/cognition.py`, `runtime/corpus.py`)
**SELECTIVE, not blanket** (see §2a — context homogenizes a registry and hurts nucleation/strain separability;
it helps only for a cohesive parent whose shared context disambiguates members, e.g. a real document's
lens-extracts). The migration default is PLAIN pplx. This context path is an OPT-IN for proven cohesive-parent
cases only. The serve endpoint already supports it (`:8007` `documents` field — §3.1 is DONE). When opting in:
`embed_corpus_to_spaces` / `capture_corpus` / `vector_index.build_index` currently embed each record's text
*independently* (plain `/v1/embeddings`). The context path would:
- A record may carry a **`context_parent`** key (an address / group id — e.g. the unit's parent address, its
  projection, or its registry). Records sharing a `context_parent` are **batched per-parent** and embedded via
  the contextual endpoint (§3.1) so each child's vector is context-informed.
- A **parent-resolver** (registry-true): derive the group key from the corpus record (parent address from the
  address spine; or the projection/registry it belongs to). No hardcoding — read the registry/address tree.
- A **fit/batch policy** for the 32K limit: if a parent's children exceed the window, split into
  context-batches (note the split — no silent truncation; fail-loud/Notice per [[feedback-no-silent-failures]]).
- Keep the plain (non-context) path as the default fallback (and for spaces where parent-context is meaningless).
- This is a NET extension of the existing one-source seam — NOT a parallel embed path (reuse build_index).

### 3.3 `fabric/config.py` + the company CLI — embedder selection + the surface loadout
- **Re-wire the default** once the migration (§4) runs: `DEFAULT_EMBED_MODEL=perplexity-ai/pplx-embed-context-v1-4b`,
  `DEFAULT_EMBED_URL=http://localhost:8007/v1`, `DEFAULT_EMBED_DIM=2560`. **Do NOT flip this before the corpus is
  re-embedded** — a mixed-dim space (BGE 1024 + pplx 2560 vectors) breaks find_relations/nucleation (fail-loud
  dim guard, but a corrupted space). The flip + re-embed must be atomic/staged.
- **`company embed`** (the CLI already has `bench embed`): point bench at pplx; add an embedder-SWAP verb (or
  reuse `company swap embed-pplx <model>`), and a **loadout** (§5) for the surface.
- **MRL knob:** allow a per-space target dim (truncate 2560 → 1024/512) for cheaper spaces — a CLI/config knob.

### 3.4 company MCP tools — expose context + grouping
- **`capture`**: add a `context_parent` (or `group_by`) param so an agent can capture N children under one parent
  with context-aware embedding in one call.
- **`find_relations` / nucleation**: nothing required to *work* at 2560-dim (registry-true; the pickers already
  read embedded stores) — but document that types/items must share the embedder (dim guard already enforces).
- **`models_for_role` / capability**: register pplx-context as the embedder capability (so role/embed binding
  resolves to it).

### 3.5 Leverage the remaining features (each a knob, not a rewrite)
- **32K context** — embed long units whole (drop the 8192-era truncation; many repo/doc units were being cut).
- **No instruction prefix** — remove any BGE-era instruction/prompt handling from the embed path (simpler, no drift).
- **INT8 / binary native quantization** — for LARGE spaces, store quantized (4×/32× smaller). A storage-mode knob
  per space (the engine compares via cosine on the quantized vectors — pplx is quantization-aware-trained).
- **MRL** — see §3.3 (truncatable dims).

---

## 4. THE MIGRATION (BGE → pplx, system-wide — careful, atomic/staged)
1. Ensure `embed-pplx` resident + healthy (`:8007`); register the loadout (§5).
2. Build the contextual serve endpoint (§3.1) so the migration can embed context-aware where it helps.
3. **Re-embed every existing space** with pplx (2560): repo, principles, worldview, topics, history — via the
   capture/embed seam pointed at pplx (context-aware per §3.2 where a parent exists). Incomparable across models,
   so this is all-or-nothing per space.
4. **Rebuild scale pyramids** for every re-embedded space (the pyramids are BGE-derived; stale after re-embed).
5. Flip `fabric.config` default → pplx (§3.3) AFTER 3–4, so new captures match.
6. **Verify**: dims = 2560 everywhere; `tests/projection_instrument_acceptance.py` + find_relations/nucleation/
   strain re-pass; the instrument lenses still read (curl + both viewports).
7. **Ship the keystone lens** on the pplx corpus: operators (types) vs content (items), both pplx → the
   `by_operator_nucleation` reading goes live (the keystone was PROVEN on pplx — see instrument-surface/STATUS.md).
- **GPU note:** pplx-4b ~8.2 GB. The loadout must fit it alongside the bridge (+ voice if co-resident) on the
  16 GB card. BGE (`:8001`, 2.5 GB) can be retired from the loadout once the corpus is off it.

---

## 5. THE SURFACE LOADOUT (registered 2026-06-15 — `ops/services.json` combos)
Added combo **`instrument`** = `[bridge, embed-pplx]` — the instrument surface's API + its embedder
(pplx-context-4b, the strongest, context-aware). `company up @instrument` brings the surface up on pplx.
(Per [[project-mode-loadout-registry]] the per-surface model loadout is a registry concern — this is that entry;
extend with voice/stt if the surface needs the right-hand-man co-resident.)

---

## 6. SEQUENCING (each a verifiable beat)
1. ✅ register the `instrument` loadout + write this spec (2026-06-15).
2. ✅ contextual endpoint already exists + context-vs-plain PROVEN (§2a): context homogenizes a registry →
   migration default is PLAIN pplx; context is selective-only. (2026-06-15)
3. **The migration (§4) — PLAIN pplx** (the real, safe quality win over BGE): point the embed path at pplx,
   re-embed every space (2560), rebuild pyramids, flip the default — staged, atomic per space, verify each.
   This is the next big beat; it's a shared-corpus operation → do it deliberately with per-step verification.
4. Ship the keystone lens + the L15 promote gesture on the pplx corpus (the keystone was PROVEN on plain pplx).
5. Leverage knobs (§3.5): 32K, MRL, quantized storage — as the corpus grows.
6. Context-aware capture (§3.2) — LATER + SELECTIVE: only for proven cohesive-parent retrieval cases, never blanket.
