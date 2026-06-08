# The Corpus-Chain Primitive — the grounded artefact

> **What this is.** The synthesis of the corpus-chain research wave (anchor `CORPUS-CHAIN-ANCHOR.md` + six
> companions `findings/CC-*.md`), written after the full set landed. Third in the series after
> `COHERENCE-SUBSTRATE.md` (structural) and `SEMANTIC-LAYER.md` (semantic). Not a spec — the grounded basis,
> with the anchor's hopeful claims corrected by evidence (several from live probes). The final section joins
> all three rounds into one corrected picture, which is the point of the whole effort.
>
> **The one-line version, corrected:** the corpus-chain (compile → map → reduce) is a real, mostly-prior-art
> primitive whose **map half is already built (`run_swarm`)** but whose **reduce and compiler are net-new and
> are the real builds** — and it genuinely is the substrate under the research-wave and the coherence
> semantic-layer, but it **collapses the roadmap only *partially*: three rounds → one LLM-read engine + four
> orthogonal pieces that still stand on their own.**

---

## 1 · The corrected thesis (what the round changed about the anchor)

My anchor claimed three things the evidence sharpened or overturned — and the corrections *are* the finding:

1. **"It IS `run_swarm`" → `run_swarm` is the MAP half ONLY.** (CC-6 + CC-4, grep-confirmed, independently.)
   `run_swarm` is fan-out + barrier + resolve-each-individually — there is **no cross-unit reduce** in the
   code; `run_jury` is N-draws-of-one-role (not a join); the only join that exists is `run_role`'s two-input
   rule. So **the smart REDUCE — cross-unit join + decide-next + hierarchical staging — does not exist, and is
   the real, highest-leverage build.** Two companions reached this independently; it's the round's spine.
2. **"Collapses three roadmap items into one" → partial: one engine + FOUR orthogonal pieces.** (CC-5.)
   Building the primitive collapses the *LLM-read* faculties (research-wave, coherence-scan, onboard, repo-QA)
   into configs of one engine — but leaves standing: the **structural three-leg graph**, the **disposition
   store**, the **loop + safety**, and the **calibration harness**. "Three rounds → one engine + four
   orthogonal pieces," not "three become one."
3. **"The cost-shape is the elegant invariant" → it's a per-config property, not a primitive invariant.**
   (CC-5.) "Cheap map, small reduce-input" holds for coherence-scan/onboard; the **research-wave face inverts
   both halves** (strong workers *and* large companion reduce-inputs) — *this very wave lived that inversion*
   (CC-4 measured: six ~10K-token companions already overflow the local synth context).

Also corrected: the **coverage-certainty argument (§5) is corroborated, not novel** — it's *literally
DocETL's published motivation* (CC-6). And the **honest novelty is the composition**, not the mechanics
(LOTUS/DocETL/RAPTOR/DSPy/FrugalGPT are the prior art): *one resident local small-model swarm serving many
faces, its output held as a dispositioned substrate feeding a no-humans loop (push, not pull), local-first.*

## 2 · The three stages, grounded

### COMPILE — net-new, and the make-or-break has a structural twist
`runtime/compile.py` is a name-collision (graph→execution, not intent→config), so the **NL→config compiler is
net-new** (CC-2, CC-6). And CC-2's defining finding, the asymmetry the semantic round's make-or-break didn't
have:

> **The compiler has no model tier above it — the strong model IS the planner.** So SEM-3's keystone (a
> *stronger* model confirms) is **structurally unavailable**. Trust can't come from a better judge; it comes
> from a **hedge**: `Chain.validate()` (deterministic, before run) + **dry-run-one-unit** + human/agent
> inspect-approve (the existing `governance.py` posture gate) + an optional grounding pre-map.

The verdict is tiered (CC-2, with a live probe emitting real Chain instances):
- **T1 auto-safe** — saved chains; well-specified per-unit classification over a known dir (Verified clean).
- **T2 must-approve** — novel/ambiguous intent. The sharp catch: the dominant defect — a *schema-valid but
  **non-unit-local** map_prompt* (asking the cheap worker a question it can't answer from its one unit) — is
  **invisible in the plan**, so an approver reading the config would miss it. **Therefore dry-run-one-unit is
  mandatory, not optional** — you must run one unit and look, not just read the plan.
- **T3 do-NOT-auto-compile** — deep cross-unit reasoning where the map shape is itself the wrong primitive
  (the SEM-3 S3 analog).

The economics that make this safe (CC-2): **you save the *config*, not the intent** — so the un-correctable
compile risk is paid + gated *once* for the high-value saved faces, concentrating the residual risk in the
*cheap-to-redo novel-query* quadrant. External ceiling is real (text-to-SQL: 98.7% of NL2SQL errors are
"valid-but-wrong"; SOTA ~52% on BIRD) — so the tiering and the dry-run hedge are not over-caution.

### MAP — built, with the seam named four times
The fan-out engine is real: `run_swarm` + the `json_schema` transport + `SlotBudget` + `run://` per-worker
addressing (CC-1, CC-3). Corrections:
- **It's two invocation substrates, not three tiers** (CC-3): OpenAI-HTTP (local 4B + Ollama Cloud) which
  rides `run_swarm`, vs a **subprocess `claude -p`** for the strong tier — which **cannot ride `run_swarm`**.
  So the research-wave face (strong workers) and the coherence-scan face (cheap workers) fan through
  *different machinery*. Three unrelated governors: local VRAM/KV knee (8–14), Ollama Cloud plan-quota
  (1/3/10, corrected from "~6–10"), `CONCURRENCY_CAP=3` for subprocesses. **Picking the cloud tier is also a
  contention escape** (off the local card — solves the sweep-vs-cognition-waves problem for free).
- **THE ONE LOAD-BEARING SEAM, named independently by four companions** (SEM-1, CC-1, CC-3, CC-4): `run_role`
  hardcodes `ctx["utterance"]` → a unit-reading worker needs it generalized to read `role.input_addresses`.
  CC-1 frames it precisely as a **fan-out axis inversion** — `run_swarm` fans *N roles × 1 ctx*; the map needs
  *1 role × N units* — best landed as a small `run_items` refactor (subsuming cast + jury). Everything routes
  through this one seam.
- Plus a **chunk-and-compose sub-tier** (CC-3) for files over the 65K context (`suite.py` ≈ 180K tokens) —
  *intra-file*, not to be conflated with the reduce's cross-file join. Canonical unit (CC-3's position): **a
  file + its self-description** (artifact bundled with its own yardstick).

### REDUCE — the least-built part, the real net-new build
CC-4's headline, corroborated by CC-6: **the reduce is where the work is.** `reduce-tree` is declared-but-dead
(`suite.py:1474`, never read at runtime, no reduce role exists); the live "reduce" is a deterministic
injection rule, not synthesis; **the cross-unit JOIN has no mechanism at all.** Its four jobs (join /
adjudicate / compose / decide-next) and the two hard mechanics, worked:
- **Staging threshold is a compile-time computation** (`n_units × map_digest_size vs synth_context`) — a
  `{contradicts,note}` scan fits one reduce call for *thousands* of units; six research companions already
  overflow. Hierarchical reduce's real hazard isn't lost-in-the-middle, it's *preserving the JOIN* → clustering
  must be query-dependent (+ a structural-pairing pre-stage that sidesteps the tree — steal DocETL's `resolve`).
- **Followup-routing folds into the adjudicate gate** (CC-4): *no citable digest support ⇒ re-map* — so the
  "answer from warm digest, or re-map?" judgment stops being load-bearing (a wrong guess just triggers a cheap
  re-map, never a bad answer). Elegant fail-safe.
- **Decide-next is a declared driver rule over the reduce's `status`** — not an agentic controller (honoring
  the Company's not-agent-by-default law).

## 3 · The chain as a declared type + the one validator that makes it compose

The chain is **its own declared type**, not a saved node-graph — CC-1's discriminator: *the graph scheduler is
serial, the map is parallel ("two drivers, one substrate")*. The load-bearing reuse is **one
`build_chain(decl)` validator** (mirroring `_build_role`) that gates compiled / saved / hand-written instances
through *one door* — that single validator is what makes "the runner executes any valid instance" true. The
one genuine schema extension (CC-5): a declared **`reduce_inputs` side-input** (the structural graph for the
wired∧meaningless prize; the owned dispositions for onboard; the question for repo-QA). Common purposes are
**saved chains** (declared like roles/node-types — the third instance of the self-registering-file law); novel
queries **compile fresh**.

## 4 · The honest build list (built vs net-new), grounded

```
BUILT / REUSE (don't rebuild):
  · run_swarm + json_schema transport + SlotBudget + run:// addressing   = the MAP engine
  · the graph substrate (compile.py lowers a declared config to execution) = where chain-config rides
  · governance.py posture gate           = the compiler's inspect-approve
  · authoring.py (validate-in-temp + dry_run_role) = the dry-run-one-unit pattern, already exists
  · implement.py                          = the structured fail-loud round-trip
  · UPTRANSLATE_KINDS already has "finding" (suite.py:5854) = the RHM hook for repo-QA/onboard, WRITTEN

NET-NEW (the real builds, in leverage order):
  1. the smart REDUCE — cross-unit JOIN + adjudicate + compose + decide-next   ← highest-leverage, doesn't exist
  2. the ONE seam: run_role ctx→input_addresses (the run_items axis-inversion refactor) ← everything routes here
  3. the NL→config COMPILER + Chain.validate() + dry-run-one-unit              ← the make-or-break, hedge-gated
  4. the reduce/resolve node-types (steal DocETL's resolve as the pairing pre-stage)
  5. digest-as-first-class-artifact (cas://-addressed) + selective invalidation  ← ingest-once-query-many
  6. chunk-and-compose sub-tier for over-context files
  7. the synth-tier registry home (no resident-model catalog yet — the G8 gap)
  8. reduce/compile telemetry + the calibration harness (free labelled intent→Chain pairs from saved faces)
```

## 5 · The three rounds, joined — the corrected whole

```
                          THE COHERENCE MODEL  (typed · addressed · dispositioned findings)
                                        ▲                        ▲
        ┌───────────────────────────────┘                        └─────────────────────┐
   STRUCTURAL detectors  (round 1)                          the CORPUS-CHAIN  (round 3)
   AST · registry · call-graph                              compile → map → reduce, configurable, declared
   exact · auto-actable · FINDS candidates                  ── the SEMANTIC layer (round 2) IS a coherence-scan chain
        │                                                      ── the RESEARCH-WAVE IS a research chain (strong workers)
        │                                                      ── onboard / repo-QA are chains too
        └──────────▶ structural-WIRED ∧ semantic-MEANINGLESS ◀── the prize, still the join of structure × meaning
                                        │
              CORPUS-CHAIN map = run_swarm (BUILT) · reduce + compiler = NET-NEW (the real work)
                                        │
   the FOUR orthogonal pieces that DON'T collapse into the chain:
   structural three-leg graph · disposition store · loop+safety · calibration harness
```

The corrected unified statement: **round 3 (the corpus-chain) is the engine that the LLM-read faculties of
rounds 1–2 are configs of — but only the LLM-read part.** The map of that engine is built (`run_swarm`); the
reduce and the compiler are the net-new, highest-leverage work; everything routes through one seam
(`run_role`→`input_addresses`); and four pieces (the structural graph, the disposition store, the loop, the
calibration harness) remain genuinely separate builds. The disciplines hold across all three rounds:
**positive-only / candidate-only** (nothing acts on a cheap-model or compiler judgment unconfirmed),
**own/reflect** (re-derive detection + digests cheaply, own only dispositions), **the human/stronger-model at
the judgment points** (and the compiler's twist: where no stronger model exists, the hedge of
validate+dry-run+approve replaces it), and **a measured number per class** (Area 3's "3 of 82"; SEM-3's
harness; CC-2's intent→Chain calibration) as what turns trust from assertion into measurement.

## 6 · The decisions this puts to Tim + the cognition session

1. **Build order, reframed by the round:** the highest-leverage net-new build is **the reduce** (it doesn't
   exist and every face needs it), gated behind **the one seam** (`run_role`→`input_addresses`). The compiler
   is valuable but hedge-gated and can come after a few hand-written saved chains prove the runner. So: *seam →
   reduce → a saved chain or two → then the compiler.* Sequencing is yours.
2. **The cognition session co-owns this hardest of the three** — it *is* their `run_swarm`/`run_role`/
   `run_jury` engine; the one seam is the `run_items` axis-inversion in their code; the reduce is net-new in
   the shared `suite.py`/cognition territory. This is a genuine co-design, not a relay.
3. **The compiler trust model is the consequential design call** (the round-3 analog of round-1's standing-grant
   and round-2's confirm-cascade): T1 auto / T2 dry-run-then-approve / T3 never-auto, with `Chain.validate()` +
   dry-run-one-unit as the structural hedge for a planner that has no stronger model above it.
4. **The calibration harness recurs as the first-real-artefact across all three rounds** — measure
   per-class/per-intent precision on the system's own named incidents before trusting any auto-path.

## 7 · One paragraph for the cross-read

The corpus-chain is real and mostly prior art in its mechanics (LOTUS/DocETL/RAPTOR/DSPy) — its novelty is the
*composition*: one resident local swarm serving many declared faces, output held as a dispositioned substrate
that pushes into a no-humans loop. The round corrected my anchor with evidence: `run_swarm` is the **map half
only**, so the **cross-unit reduce is net-new and the real, highest-leverage build**; everything routes through
**one seam** (`run_role`'s hardcoded `ctx["utterance"]` → `input_addresses`, an axis-inversion refactor named by
four companions); the **compiler is net-new and structurally un-confirmable** (it's the top tier, so trust is a
hedge — validate + dry-run-one-unit + inspect-approve — tiered T1/T2/T3, with the dominant defect, a non-unit-
local prompt, *invisible in the plan* so dry-run is mandatory); the chain is **its own declared type gated by
one `build_chain()` validator**; and building the whole thing **collapses the LLM-read faculties of all three
rounds into configs of one engine, but leaves four orthogonal pieces standing** (the structural graph, the
disposition store, the loop, the calibration harness). Joined to the other two rounds it completes the picture:
structure finds, the chain's map adjudicates, its reduce joins, a stronger model (or the compiler's hedge)
confirms, the disagreement (wired ∧ meaningless) is the prize, and a per-class calibration number turns the
whole thing from assertion into measurement — the system watching its own wiring *and* meaning, on a cheap
local swarm under a strong synthesis, without a human holding it together.
