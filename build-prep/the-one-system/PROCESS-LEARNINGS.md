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

## 9. THE INHERENT PROBLEM WITH DETERMINISTIC PASSES — and the mitigation (the deepest one)
A deterministic extractor can only capture **what it was told to look for.** Its contract IS its blind spot: it is *constitutionally incapable* of reporting a kind of thing nobody wrote a rule for — and worse, it does so **silently** (a count with no identity, or simply nothing, looks identical to "nothing was there"). You cannot audit a deterministic pass with another deterministic pass — the second one shares the first's blind spots by construction. **A specific check only finds what you already suspect.**
- **The mitigation:** an *open* check that reads the actual artifact with no closed expectation — the model sees the file AND what was captured, and is asked for **discrepancies of any kind**, explicitly including *"things in the file of a kind the contract doesn't cover."* That's the move that lets the instrument **find the limits of its own contract**, not just adherence to it.
- **Why a model (not more rules):** only an open reader can surface the *unanticipated* class. The deterministic layer is precise but blind; the model layer is the eyes that see what the rules forgot. This is the real reason the two layers coexist — not "model adds meaning" but "model covers the deterministic layer's structural blindness."
- **Generalises:** any deterministic/rule-based pass in the Company (extractors, validators, linters, registries) carries this same blindness; the dragnet pattern is the general way to audit any of them against reality.

## 10. PROMPT DESIGN — what we learned writing the audit prompt
- **State the PURPOSE, not just a checklist.** "Capture every *symbol* — every named, identifiable definition the system could reference/link to (its anchors)" + the specific list as **examples, explicitly not closed.** A bare list makes the model police adherence; the purpose + open framing makes it reason about what *should* be an anchor — so it flags kinds the contract omitted. (Tim's point: the named items are *instances* of a category; name the category.)
- **Give the model the real contract, framed as INTENT, not as ground truth.** Show "what the extractor was *supposed* to capture" and say the intent was completeness — so it reports adherence-failures AND contract-weaknesses AND wrong captures, as distinct things. The contract is a subject of the audit, not its authority.
- **The author's own vague description is a brief, not a spec.** Tim isn't the developer; "whatever component/function/export/hook are instances of" → I supply the terminology (symbols/anchors) and apply it. Capturing intent-from-vague-direction is part of the method.
- **Be literal / anti-hallucination clamp:** "only report what is genuinely in the file." Pair an open question with a hard groundedness rule, or open-ness drifts into invention.

## 11. OUTPUT STRUCTURE — the evolution and why
- **Flat `list[str]` → rich typed objects.** First cut jammed each finding into a string. The lesson: **structure the output so it's queryable by the dimension you'll aggregate on.** Findings became objects with a discrete **`discrepancy_type` enum** (the four buckets: in-contract-not-extracted / in-file-not-in-contract / wrong / other) + `name`, `symbol_kind`, `location`, `detail`. Now the failure-class map is `group by discrepancy_type` — no string-parsing.
- **An explicit PASS flag (`complete: bool`), and "clean" = empty arrays, never null.** A clean file lands a *queryable* pass (`where complete` / `where not complete` = the worklist). Don't represent "no issues" as absence — represent it as an explicit, filterable state.
- **The discrepancy buckets ARE the discovery axis.** Making the model classify each finding into an open-then-aggregated category is *how the failure classes emerge from the data* rather than being pre-decided. The output shape is the analysis design.
- **The structured-output mechanism already existed** (rich field types: object/list[object]/enum, guided-decoded). Lesson: the limit I "found" was a stale tool *description*, not the capability — check the registry/source before believing a constraint, and fix the single source so it can't drift (derive the doc from the registry).

## 12. INPUT DESIGN — feed the audit fairly (a subtle false-positive source)
- **Consolidate the extraction you show the model; don't expose the extractor's internal field-split.** Early false positives came from showing `symbols` AND `declares` separately — the model "helpfully" reconciled the two internal fields instead of comparing *file vs. extraction*. Show ONE consolidated "captured" list. The audit's job is file-vs-reality, not internal-consistency.
- **Feed the extractor's own COUNTS alongside the captured items.** This let the audit say the precise thing: *"counts report n_constants=1, but the constant's identity was never persisted"* — distinguishing "detected-but-dropped" from "never seen." The metadata about the extraction is part of the evidence.
- **Inputs are file-type dependent** (the contract + what "complete" means vary by kind), but the *check* is generic/open across all kinds — so unknown classes still surface. Type-specific expectation, type-agnostic discovery.

## 13. THE EXPERIMENTAL METHOD ITSELF (how we worked, not just what we found)
- **Observe one before scaling many.** Every step: run a single call, read the *raw* response shape, before fanning out. Caught `content:None`, the reasoning cost, the field-split false positive, the cold-JIT effect — each on one example, cheaply.
- **A/B under identical conditions to isolate a cause.** The 9× slowness wasn't diagnosed from logs alone — it took swapping the model and running the *same* inputs. "Same everything but the one variable" is how you turn a suspicion into a root cause.
- **Warm vs cold is a real variable for these models.** The concurrency "anomaly" (slower-than-single-stream) was cold per-shape JIT, proven by re-running the same shape warm. Measure warm AND cold; don't trust a single cold number.
- **Distrust a number that violates the model** (Tim: "that does NOT seem right"). 30 tok/s for an 8-bit when the 4-bit does 2700 → don't accept it, find why. A result that contradicts a known baseline is a lead, not a fact.
- **Verify by real use at each stage** — the role works end-to-end (clean / gap / clean-JS), the batch inherits no-think, the gate actually lets 32 through (checked at the model, not assumed from config). "Config says 32" ≠ "32 in flight."

## 14. THE LEDGER PROCESS — what building a self-model taught (the reframe)
The meta-learning under all of this: **the ledger is not an artifact to FINISH; it is a living instrument to keep TRUE.** "Build the map" → "stand up the organ that keeps the map honest." This reframes everything downstream (query/visualise/embeddings/UI are its *senses*, not decorations).
- **Coverage ≠ truth.** The first build was "complete, provable by directory-diff" AND riddled with silent quality failures (truncation read as whole, constants counted-but-dropped, dumps read as substrate). Every file present, many wrong, nothing flagged. "We covered everything" is the easy half; "everything we covered is TRUE" is the hard, invisible half. A directory-diff proves completeness, not soundness.
- **The ledger reveals its gaps only when USED, never when inspected.** Nothing was found by looking at the map (it always looks internally consistent) — every gap surfaced from putting LOAD through it (querying, feeding the model, auditing). Prove-by-use applies to the map as hard as to code. The audit isn't a nice-to-have; it's the only thing that tells you if the map is real.
- **It is self-referential — that IS the point made concrete.** The audit's inputs are the ledger's own symbols; its outputs join back to `ledger.entry`. The map improves the map. The ledger-build is already running, at smallest scale, the recursive self-examination the whole Company is meant to do — it's the **first instance of the standing operation**, not a precursor to it.
- **Drift is the ground state, not an edge case.** Files renamed under us, the live fabric made thousands more, the loadout shifted beneath the engine. A self-model of a LIVING system is permanently catching up; "stale" is its default and reconciliation is a continuous duty. So carry-forward + drift-detection are **load-bearing architecture**, not features.
- **"What belongs" is a relational judgment the building forces.** Data-vs-substrate, the bundles — the boundary question is never about the file in isolation; it's relational (is this content present elsewhere? derived? a count or an identity?). `_ds_bundle.js` was excludable because its content lived BETTER elsewhere (83 modules interpreted individually). The map's boundaries are a relational discovery.
- **The sequence emerged from real dependencies; it wasn't designed.** truncation→exclusion→metadata→edges→audit→fix→re-run each revealed the next by hitting a wall (can't audit before honest extraction; can't safely reconcile drift before carry-forward; can't scale before the engine follows the loadout; can't query before persist; can't visualise before query). The dependency chain taught itself in order — trust "prove the real case, let requirements emerge" over an upfront plan that would've had the dependencies wrong.
- **Honest completeness is the ledger's only currency.** Everything trusts the ledger's claim about ITSELF. The "overhead" moments — recording "1 remaining = honest drift not a defect", stubbing excluded files WITH a reason, failing loud on oversize instead of silent-truncating — are the integrity. A self-model that lies about its own completeness is worse than none; it poisons every decision built on it. This can't be retrofitted.

## 15. WORKING-METHOD learnings (how the agent should operate — caught in this session)
Honest reflection on the agent's own patterns, kept because they recur and cost real time/resources:
- **Verify your OWN claims, not just the system's.** The throughput saga had three confident-but-wrong diagnoses in a row (stale `ps` → "stuck at 2"; "GPU-bound, use 6" → actually a pathological config; a "contending other session" that didn't exist). The same "deterministic passes fail silently, check against reality" discipline the methodology preaches must apply to the agent's own assertions. A single observation is a lead, not a fact — re-read before asserting, *especially* under momentum.
- **Don't confabulate from a fragment.** One offhand mention ("background upgrades in another session") got spun into a persistent, active, evidence-free narrative used to justify caution. Building a story-scaffold from a scrap and treating it as real is a distinct failure mode — name it, check it, drop it when unconfirmed.
- **The cheap shortcut that violates the stated principle is the one to distrust.** Repeatedly drifted to "sample then confirm" (the exact failure class) and to "run the deterministic count" (blind to the unknown) under progress-pressure. When a next-step feels efficient, check it against the frame just agreed — efficiency that breaks the principle is a regression.
- **Re-anchor to PURPOSE before proposing next steps.** Lost the "why" (the ledger's, the 4B's) when heads-down on mechanism, and proposed mechanically-sensible but purpose-blind moves. Surface the framing/why EARLY and explicitly so a wrong frame is caught before it becomes code — don't make the operator reverse-engineer the framing from work already done.
- **Check what EXISTS before assuming a gap.** Kept proposing to build things already built (rich output types, `active_brain` call-time resolution, the minds reset hook, `interpret_file`/`dragnet` roles). The Company has more in it than the build-instinct credits; look first.
- **Findings come from RUNNING, not planning.** Every real discovery (FP8 slowness, the gate cap, dropped constants, JS gaps, cold-JIT) emerged from doing it at scale, not analysis — vindicates "prove the real case first." Observe-one-before-many; A/B to isolate; distrust a number that violates a known baseline.

## The shape in one line
**Deterministic floor → dragnet the local models over it as objective verifiers (all of it, classes emergent) → trace classes to the generator → fix + cheap re-run → converge → generalise into a standing operation — all in-system, objective-only, tags-not-confidence, fail-loud. The ledger is not finished, it is kept true.**
