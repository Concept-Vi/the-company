# Chain Components — the actual mechanics (runs, concurrency, allocation, schemas, reduces)

> The component-level build spec for the 4B-swarm chains (`CHAIN-DESIGNS.md` is the what; this is the HOW).
> Every chain shares ONE anatomy (§1); the per-chain differences are just choices within it. §2 works four
> flagships end-to-end at full detail (one per reduce-pattern); §3 gives the rest as anatomy-deltas. Numbers
> are SEM-1's measured reality, not the rosy claim. The engine (`run_items`/`run_reduce` + the embed op) is
> cognition's; this spec is what coherence builds ON it + the reduces coherence owns.

---

## 1 · THE SHARED ANATOMY (every chain has these seven components)

### 1.1 The UNIT and its allocation
- **A unit = one file + its path/self-description** (SEM-2's canonical unit — the artifact bundled with its
  own yardstick). For symbol-level chains, a unit = one function/class. The `unit_selector` (an Action field)
  picks them: a glob (`runtime/**/*.py`), a file-list, or a registry slice. Default = the whole repo,
  gitignore-aware, minus binaries/lockfiles.
- **Allocation = the repo partitioned into units, one unit → one MAP call.** ~234 first-party files / 48K LOC
  (SEM-1). So a whole-repo map ≈ 234 calls.
- **The over-context sub-tier (chunk-and-compose).** The 4B context window is ~65K tokens; `suite.py` is
  ~180K (SEM-1). A unit that exceeds the window is split into symbol-or-section CHUNKS, each chunk is its own
  MAP call, and a tiny per-file mini-reduce composes the chunk-facts back into one file-fact. This is
  INTRA-file (not the cross-file reduce). Most files fit in one call; only the few giants chunk.

### 1.2 The MAP call (per unit)
- **Mechanism: `run_items(role, units)`** — cognition's axis-inversion: 1 role × N units (vs run_swarm's N
  roles × 1 ctx). Each invocation resolves the unit's `input_addresses` → the unit content into the role's
  context, fires the role on the 4B, writes the structured output to `run://<scan-id>/<unit>`.
- **The role IS the map declaration** (a declared file, e.g. `roles/connection_extract.py` — the
  finding-type-as-declared-role idea): `{op: "generate", model: <4b registry ref>, prompt: <extraction
  instruction>, input_addresses: [the unit], output_schema: <the fixed schema>, thinking: false}`.
- **STRUCTURED OUTPUT, never tools.** The map uses `json_schema` guided decoding (fabric/transport.py's
  response_format branch) — the 4B is CONSTRAINED to emit a schema-valid object; the client validates +
  retries on malformed (fabric/client.py). **No tool-calling** — tools = agency = the not-agent-by-default
  law; the map is pure dataflow extraction. (Tim's "structured output vs tools": always structured, for the
  map. Tools never appear in the map.)
- **Thinking OFF for extraction.** Extraction is not reasoning; thinking off + schema-constrain is fastest +
  most reliable (constrained decoding HELPS classification/extraction — "Let Me Speak Freely", SEM-3; and it
  removes the 2-in-6 malformed-under-thinking risk SEM-3 measured). Thinking is reserved for the stronger-model
  reduce, never the cheap map.
- **The prompt is bounded + identical across units** — "Extract <X> from this file as the schema. Do not
  judge, do not infer beyond the file; if absent, return empty." Same prompt every unit (that's what makes it
  a map, and what makes the output comparable in the reduce).

### 1.3 CONCURRENCY (the real numbers — SEM-1 measured)
- **~14 concurrent on real source files** (the live config caps `max_num_seqs:16`; files KV-bind above ~5K
  tokens, so effective ~8-14). Aggregate ~2,241 tok/s at concurrency 32 for tiny inputs; less for real files.
- **The fan = a semaphore-bounded pool of ~14 in-flight HTTP calls** to the resident 4B (one OpenAI-style
  endpoint). 234 units / 14 ≈ ~17 waves; a bounded-extraction call (small output, no thinking) ≈ ~1-3s →
  **whole repo ≈ 30-90s.** "A minute," honestly — not "seconds," but exhaustive (every file), which is the
  point: not sampling, total coverage.
- **Contention is sweep-vs-cognition-waves, not sweep-vs-chat** (SEM-1): both use the resident 4B's slot pool.
  Fix = a polite SECOND `SlotBudget` for scans (a raised `reserve_r`) so a scan yields to live cognition turns
  — the scan runs in the gaps, never evicts the resident brain. VRAM is a non-issue (the scan loads nothing —
  fires at the already-resident model).

### 1.4 The DIGEST (the fact-base — own/reflect)
- The map outputs accrete into a **digest**: `{unit → structured-fact}`, the reusable repo fact-base.
- **Content-hash keyed for INCREMENTAL re-derivation:** each fact carries its unit's `content_hash`; a re-scan
  re-maps a unit ONLY if its hash changed (mirrors the vector-index incremental pattern in `fs_store`). So the
  first scan is ~60s; a re-scan after editing 3 files is ~3 calls.
- **`cas://`-addressable, re-derived not owned** (own/reflect): the digest is a cache, never the truth; the
  truth is the code, re-mappable any time. Many reduces run over one digest; a followup needing no new
  extraction is a cheap re-reduce over the warm digest.

### 1.5 The REDUCE (the judgment — three kinds, never the 4B's)
- **EXACT** (code over the structured facts) — set-algebra/joins/diffs. Deterministic, re-derivable →
  **trustworthy, can gate.** (A, C-diff, E-join.)
- **EMBEDDING** (the embed op → cluster / nearest-neighbour over fact-vectors) → **candidate-only** (proximity
  proposes; a stronger model confirms). (D.)
- **STRONGER MODEL** (a Claude Code agent / a bigger model) — runs ONLY on the FEW candidates the exact pass
  flagged → cheap + the only systematic-error gate. Never the 4B judging itself; never a same-model jury
  (variance≠error, SEM-3). (B, C-adjudicate.)
- Mechanism: the reduce reads the digest back (via the run:// resolver / the fact-base) and is plain coherence
  code (`coherence_detect`/`coherence_actions`), EXCEPT the embedding reduce (calls the embed op) and the
  stronger-model reduce (one model call per candidate).

### 1.6 FINDING EMISSION (into the store I built)
- The reduce calls `append_finding({kind, address, state, evidence, source, owner})` per gap; structural-exact
  findings → `source:"structural"`; embedding/stronger-model → `source:"semantic"` (candidate). Catalogue/
  prior dispositions ride forward (`dispose_finding`); the burn-down reflects them; `company coherence` shows
  them. The chain is just a new SOURCE into the model that already exists.

### 1.7 CALIBRATION (D — before a chain gates)
- Each chain has captured-incident FIXTURES (`build-prep/coherence/eval-set/<chain>.json`) with stable ground
  truth; `calibrate(predictions, truth, config)` measures precision/recall per model-config; the chain ships
  to the panel / is allowed to gate only if its number clears the threshold. The N-config sweep (run the same
  chain under qwen-4b vs a bigger model vs different thinking-budgets) is the experiment axis — the harness
  ranks them, `save_calibration` pins the winner as the Action's default.

---

## 2 · FOUR FLAGSHIPS, END-TO-END (one per reduce-pattern)

### 2.1 · A1 — THE UNIVERSAL CONNECTION GRAPH  (EXACT reduce — the highest-leverage chain)
- **Units:** every code+config+doc file (~234). **Allocation:** one MAP call/file; the ~3 giants chunk.
- **MAP role** `roles/connection_extract.py`: op=generate, 4b, thinking off, json_schema:
  ```
  CONNECTION_SCHEMA = {
    "defines":         ["symbol"],        # functions/classes/routes/events/components this file DEFINES
    "calls":           ["symbol"],        # symbols it CALLS/uses
    "serves_routes":   ["/api/..."],      # HTTP routes it SERVES (bridge handlers)
    "consumes_routes": ["/api/..."],      # routes it CALLS (fetch/EventSource/requests)
    "emits_events":    ["event.kind"],    # SSE/event kinds it emits
    "listens_events":  ["event.kind"],    # event kinds it consumes
    "imports":         ["module"],
    "addresses":       ["ui://|code://|run://"]   # addresses referenced/defined
  }
  ```
  Prompt: "List exactly what this file defines, calls, serves, consumes, emits, listens-for, imports,
  addresses. Extract only what's literally present; empty arrays if none. Do not judge."
- **Run:** ~234 calls, ~14-wide, ~60s. Output digest: `{file → CONNECTION_SCHEMA}`.
- **REDUCE (exact, my code):**
  - build `provides = ⋃(defines ∪ serves_routes ∪ emits_events)` keyed by symbol/route/event → the files
    that provide it; `uses = ⋃(calls ∪ consumes_routes ∪ listens_events)`.
  - **orphan** = provided ∧ never used (minus declared entry-points: faces, mains, tests).
  - **dangling** = used ∧ never provided.
  - the Python↔TS route join: `serves_routes ∩ consumes_routes` across languages = a pure string-join (the
    boundary no off-the-shelf tool spans).
- **Emits:** `unwired-<kind>` findings (route/event/capability/component), `dangling-<kind>` findings. EXACT →
  gateable. **Subsumes + universalises** my AST reachability + capability-no-consumer (those are Python-route-
  only; this is every kind, every language).
- **Calibration:** fixtures = files with known provide/use facts (incl. the cross-language route cases).

### 2.2 · C1 — HALF-MIGRATION  (EXACT-flag → STRONGER-MODEL adjudicate)
- **Units:** data-handling files (selector: files that read/write the store / a record / a table). ~dozens.
- **MAP role** `roles/shape_extract.py`, json_schema:
  ```
  SHAPE_SCHEMA = {
    "record_shapes": [{"name": "...", "fields": ["..."], "lifecycle_states": ["pending|applied|..."]}],
    "storage_mechanism": "jsonl|annotation-store|supabase|in-memory|..."
  }
  ```
  Prompt: "Extract every record/data shape this file reads or writes: its name, fields, and any lifecycle/
  status states it moves through, plus the storage mechanism. Only what's present."
- **Run:** ~dozens of calls, one wave, ~seconds. Digest: `{file → SHAPE_SCHEMA}`.
- **REDUCE (two-stage):**
  1. EXACT: cluster record_shapes across files by field-overlap (Jaccard > 0.5); within a cluster, find PAIRS
     where two different `storage_mechanism`s handle ~the same record AND `lifecycle_states(new) ⊊
     lifecycle_states(old)` (the new mechanism DROPPED states) → **candidate pair** (this is the /status bug:
     jsonl had pending→applied→dismissed; the annotation store dropped them).
  2. STRONGER MODEL (only on the few candidate pairs): "is the dropped lifecycle a real defect, or an
     intentional retirement?" → confirm or dismiss. SEM-3 verified the 4B FLAGS this 5/5; the adjudication is
     the stronger model's (the 4B can't, and a jury can't — only model diversity).
- **Emits:** `half-migration` finding, `source:"semantic"`, candidate, with the dropped-states as evidence.
- **Calibration:** the /status incident as the TP fixture; clean migrations as TNs.

### 2.3 · D1 — BUILT-TWICE / CONCEPT-COHERENCE  (EMBEDDING reduce — needs the embed op)
- **Units:** every file. **MAP role** `roles/concept_extract.py`, json_schema:
  ```
  CONCEPT_SCHEMA = { "concepts": [{"name": "...", "refers_to": "one-sentence meaning",
                                   "kind": "data|capability|ui|protocol|config"}] }
  ```
  Prompt: "List the distinct concepts this file works with: each concept's name (as used here) and a
  one-sentence description of what it refers to. Only concepts actually present."
- **Run:** ~234 generate calls (~60s) → then the EMBED pass: embed each concept's `refers_to` (the embed op,
  cognition's — 32-wide, seconds). Digest: `{concept → {name, vector, file}}`.
- **REDUCE (embedding, candidate):**
  - cluster concept-vectors (cosine nearest-neighbour above a threshold, or simple agglomerative).
  - a cluster spanning DIVERGENT NAMES = one concept built twice (the mode-dial: `MODE_SPECS` and
    `THOUGHT_SHAPES` were two names for the mode declaration). a single NAME spanning divergent clusters = an
    overloaded term.
  - STRONGER MODEL confirms the top candidates ("are these two genuinely the same concept?").
- **Emits:** `concept-built-twice` finding, candidate. **This is the chain that catches the mode-dial-built-
  twice before the merge.** Calibration: the mode-dial incident as the TP fixture.

### 2.4 · F1 — `company onboard`  (PURE TRANSFORM — no judgment, the output IS the product)
- **Units:** every file. **MAP role** `roles/file_summary.py`, json_schema:
  ```
  SUMMARY_SCHEMA = { "purpose": "one line", "kind": "engine|surface|gate|node|test|doc|config|...",
                     "key_symbols": ["..."], "depends_on": ["module"], "owner_hint": "..." }
  ```
  Prompt: "Summarise this file: one-line purpose, its kind, its key symbols, what it depends on."
- **Run:** ~234 calls, ~60s. **REDUCE (assemble, no judgment):** group by directory/kind → a structured
  orientation map; cross-link via `depends_on`. No finding-emission — the OUTPUT is the map itself.
- **Product:** a fresh, TRUE orientation a starting session reads in ~a minute (the fix for "main drifted under
  me"). No calibration (nothing to be right/wrong about — it's a transform); quality is judged by use.
- **Same pattern → F2 auto-explain** (map: per open finding → a plain-language explanation; reduce: attach to
  the burn-down) and **F3 candidate-disposition** (map: per finding → propose {disposition, reason}; reduce:
  surface as candidates). Pure-transform, the 4B's output consumed directly.

---

## 3 · THE REST, AS ANATOMY-DELTAS (same seven components; only the noted fields differ)
- **A2 address-graph** — MAP schema = `{addresses_defined, addresses_referenced}`; REDUCE exact (defined∖
  referenced = orphan; referenced∖defined = dangling). Like A1, narrower.
- **B1 doc-drift** — MAP two roles: `claim_extract` (docs → `{claims:[{subject,asserts}]}`) + reuse A1's
  capability facts. REDUCE exact-flag (claim subject not in capabilities) → stronger-model adjudicate. Units =
  docs + docstrings (~700 markdown + source headers).
- **B2 self-description-truth** — MAP = extract MAP/STATE assertions; REDUCE vs the A1 digest.
- **C2 producer↔consumer schema** — MAP `{emits_schema, expects_schema}`; REDUCE exact mismatch.
- **D2 semantic-duplication** — MAP = none new (reuse A1 symbols); EMBED each function body; NN above threshold
  = duplicate-logic candidate.
- **E1 coverage** — MAP two roles: `test_exercises` (test → `{exercises:[capability]}`) + A1's provides;
  REDUCE exact join (provided ∖ exercised = uncovered).
- **G1 claim→symbol→exists** — MULTI-PASS: B1's claims → reduce picks referenced symbols → MAP2 `symbol_locate`
  → reduce checks existence. The reduce decides the second map (run_reduce's decide-next).
- **G2 the compiler** — a cheap MAP over the dir (`{kind, area}` per file) feeds the NL→Chain-config compiler
  so the plan is grounded in a real scan. Recursive (a chain that builds chains).

---

## 4 · THE BUILD SEAM (what's mine vs cognition's, concretely)
- **Cognition builds (the engine):** `run_items(role, units, concurrency)` (the 1×N fan + input-address
  resolution + the slot budget), the embed op, `run_reduce` (the read-back-via-resolver harness), model
  launch/select/evict.
- **Coherence builds (mine, on that engine):** each MAP role file (the extraction declaration + schema), each
  REDUCE function (the exact/embedding/stronger-model judgment), the finding-emission, the digest cache + its
  content-hash invalidation, the calibration fixtures + sweep, the Action declarations that save each chain,
  `build_coherence_info`/`company coherence` surfacing.
- **The handshake:** a chain = a declared role (map) + a declared Action (the chain config: which role, which
  units, which reduce, which model) + a reduce function (mine). `run_items` runs the map; my reduce runs on the
  output; `append_finding` lands it. The Action's per-step model is a registry ref (registry-is-truth) → the
  N-config experiment swaps it → the calibration ranks it → `save_calibration` pins the winner.
