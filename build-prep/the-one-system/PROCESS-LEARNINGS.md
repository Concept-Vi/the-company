# Process learnings — the extraction/audit/enrichment methodology (reflects into Company operations)

*Tim 2026-06-30: capture the PROCESS — the sequence, tools, setups, purposes, the patterns (like the dragnet use of local models against the deterministic layer + the loop) — not the technical bugs (those live in `4B-FINDINGS.md` / `COVERAGE-AUDIT-BUILD-SPEC.md`). This is the reusable methodology destined to be generalised/automated INTO the Company as a standing, re-runnable capability. Each pattern is named so it can be reached for again.*

---

## 0. The frame these all serve
The Company fragmented because agents acted on **partial knowledge**. The cure is one complete, true, living self-model (the ledger) — that Tim sees and steers by recognition, that the splinters fuse inside, and that the unified system grows from. Every pattern below exists to **build that self-model and keep it honest, cheaply and at scale**, so the breadth is machine-work and Tim's recognition is spent only where it's irreplaceable.

---

## 1. PATTERN — Two-layer extraction: deterministic floor + model interpretive layer
- **Deterministic first** (AST/parse): structural facts — symbols, imports, edges, counts. Exact, free, fast, no hallucination. This is the *trustworthy skeleton*.
- **Model layer over it** (the local 4B / cloud): the meaning the parser can't get — "what this file does", relationships, descriptions.
- **Why this order:** the deterministic layer is what you can *believe*; the model layer is *checked against* it. Never let the model invent structure the parser should own.
- **Purpose:** completeness you can trust + meaning you can't get mechanically, kept separate so each stays honest.

## 2. PATTERN — The DRAGNET: local models as concurrent OBJECTIVE VERIFIERS of the deterministic layer
The headline learning. A deterministic extractor **fails silently** — a missed symbol leaves no trace. So you point a **fleet of cheap local-model calls at the actual files** and ask a *bounded, objective* question: "here is the file and exactly what the extractor captured — what's MISSING / WRONG / uncovered?"
- **The model is an AUDITOR against ground truth, NOT an opinion-maker.** The file is the answer key. This is the line that makes it legitimate (vs. the rejected "let the model judge relationships" — see §6).
- **Run over EVERYTHING, never sample** — silent failures hide precisely where you didn't look. Completeness is the whole point.
- **Let the failure CLASSES emerge** — don't pre-name them. Open output (a `discrepancy_type` the model chooses) → aggregate → the classes fall out of the data. The contract is given as *intent*, treated as examples-not-closed, so the model can flag kinds the contract itself missed (audits the contract's own blind spots).
- **Small local model is RIGHT for this, not a compromise:** the task is clear, bounded, objective measurement at massive concurrency — exactly where small models are reliable and cheap. (Subjective judgement is the wrong job for them — §6.)

## 3. PATTERN — The convergence LOOP (find → trace to cause → fix the generator → re-run → confirm)
Not "find gaps and patch outputs." The loop:
1. Run the dragnet over all files → failure classes emerge.
2. **Trace each class to its CAUSE in the deterministic extractor code** (e.g. "module-level `NAME = {...}` counted but never persisted").
3. **Fix the GENERATOR**, not the generated rows.
4. **Re-run** (cheaply — only changed/affected files; carry forward the rest).
5. **Confirm** the expected now appears. Repeat until the map is true.
- **Purpose:** the ledger converges to truth by construction, and the *fix improves every future run*, not just today's rows. "Fix the generator, not the generated" is the governing rule for anything that gets re-run.

## 4. SETUP — Drive everything THROUGH the system (MCP tools + CLI), never bespoke
- Model calls → the cognition engine's **roles** (`run_role` / `run_items` / `run_draft`), not a urllib harness. You inherit: model-routing, **structured-output validation** (the role `output_schema` → guided JSON decode), **run provenance** (`run://<turn>/<role>`), and **reusability**.
- A driver script's only legitimate jobs are **assembling inputs** (from the ledger) and **persisting outputs** (to the ledger) — the data plumbing the per-call MCP surface can't loop by hand. The *model invocation itself* always goes through the engine.
- **Why:** bespoke = one-off, goes around the system, can't reflect into operations. In-system = reusable, governed, and becomes a standing capability. (This was a correction mid-build — it matters.)

## 5. SETUP — Match the tool's *mode* to the task
- **Measurement vs reasoning:** the audit is a *measurement* → run the model **no-think** (`thinking: False` on the role). Thinking-on is for genuine reasoning; for bounded extraction it's pure cost (and times out batch). Declare it on the ROLE so the batch path inherits it (don't rely on a per-call flag the batch tools may not expose).
- **Structured output is the contract:** define real typed fields (objects, enums, lists-of-objects) so findings are queryable by field — never jam structure into a string. The schema is enforced at the decoder.
- **Deterministic joins for deterministic work:** aggregating findings = a *rule* reduce (no model), not a model reduce. Only reach for a model where judgement is actually needed.
- **No-confidence (G16):** express strength as tags + counts (a `complete` pass-flag, a `discrepancy_type`, corroboration counts) — never a confidence float.

## 6. PRINCIPLE — Objective measurement, not mined opinion (the line that keeps the ledger trustworthy)
The dragnet works *because* its question is objective (file vs. extraction — verifiable). The moment a model is asked to *judge* (is A a "variant of" B? does this "supersede" that?), it's inventing opinions a small model can't be trusted for, and that no one asked for.
- **Discoverable (objective) → mine it.** **Declared/prescriptive (an act) → comes from the decision system / Tim's recognition, never mined.**
- **Relatedness → measure it** (embeddings: position in space = a fact), don't opine it. The machine finds candidates objectively; the human recognises the relationship.
- This is why the edge work split into *fact-edges* (observed in frontmatter, deterministic) vs. the deferred judgement edges — and why the proximity/embedding layer is the objective substitute for "which things are alike."

## 7. SETUP — Scale + reliability discipline (so it runs intuitively through the tools)
- **Run over everything, incremental + resumable + idempotent:** persist every N, skip done on restart, upsert. A long pass must survive interruption and re-run cheaply.
- **Concurrency = the model's real capacity** (the server's `max_num_seqs`), and the **system must follow the live loadout** — cached, loadout-derived state (gates, providers) must resolve at call-time or be invalidated on swap, never frozen at startup. (A whole class; the principle is what generalises.)
- **Lean DB/IO:** guard queries, don't stack heavy passes, never hash/scan the whole tree on top of a running sweep. (Two Docker wedges taught this.)
- **Fail loud, never silent-partial:** oversize/skip is RECORDED (a flagged finding), never a silent truncation that fakes completeness (the no-partial law).
- **Measure before scaling:** a single pathological config (a model 9× slow) invalidates every throughput assumption — verify the real rate on a small batch before committing the full pass.

## 8. THE DESTINY — generalise this into a standing Company operation
Once proven on this real case, the whole sequence becomes **composable / targeted / automated** in the Company: a re-runnable capability (target a project/path/file-type, re-extract + re-audit on drift, feed builds and new designs). The file-type → contract mapping becomes a **type registry** (extension matches a type, rules resolve into the prompt). The ledger + its projected surfaces (MCP tools, UI, company) stay the **constant map of the playing field** the unification is designed against. This document is the seed of that operation's design.

---

## The shape in one line
**Deterministic floor → dragnet the local models over it as objective verifiers (all of it, classes emergent) → trace classes to the generator → fix + cheap re-run → converge → generalise into a standing operation — all in-system, objective-only, tags-not-confidence, fail-loud.**
