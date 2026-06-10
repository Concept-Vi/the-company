---
type: design-capture
module: cognition-self-improvement
tags: [company, gap-pressure, sensing, registries, candidates, drops]
status: candidates — NOT built, awaiting a builder session
captured: 2026-06-10
relates-to: ["[[REGISTRY-FILLING-PATTERN]]", "[[SYSTEM-GAPS]]", "[[MCP-DESIGN-PRINCIPLE]]", "[[Company Build Hub]]"]
---

# Gap Pressure — the law, the evidence, and the build candidates

**Status: CANDIDATES.** Tim's directive (2026-06-10, verbatim intent): *"I want all, but I might want it all done as candidates — all the learnings and insights with it too — put in the main agents file so another session working in there can pick it up, see for themselves, and build and improve."* Nothing below is built unless marked otherwise. A builder session should verify every claim against the evidence pointers before standing on it.

**Naming is OPEN.** Candidate names Tim has seen but not yet chosen between: *gap pressure* · *misfit residue* · *the drop ledger* · *constrained operation is a sensor*. This doc uses "gap pressure" provisionally.

---

## The law (provisional statement)

> Every operation that runs constrained against a declared registry is also a **sensor for that registry**. Where reality (the corpus, the task, the agent) presses on a missing or wrong entry, the operation leaks — invalid values, insisted-on ids, repeated misuse — and if that leakage is **recorded instead of swallowed**, gaps surface as a free byproduct of normal work. Gaps are detected as **pressure, not absence**: you cannot query for what's missing, but a constrained system under real load leaks at exactly the missing places.

### The four preconditions (and the failure each prevents)
1. **Closed, declared vocabulary** (registry-is-truth). Without it there is no misfit to measure — an open-ended output would happily produce anything and nothing registers as wrong.
2. **Grounded operation** (grounded-chain law). Pressure must come from real content/tasks pressing on the registry, not a model theorizing about categories. Ungrounded = noise, not signal.
3. **Fail-loud, never coerce** (no-silent-failures). Silent coercion to the nearest valid value *eats the evidence*. The drops exist only because the system refuses to pretend.
4. **Residue recorded as data** (introspective-data law). Unrecorded pressure evaporates. Logged pressure accumulates into legibility.

Remove any one → the sensor dies. These are all existing Company laws; gap pressure is what they **compose into**, unplanned. That is the significant part: it is not a feature, it is a property — every constrained operation the Company ever runs is already a sensor, if the residue is kept.

### Known limits (define the range, don't diminish it)
- Detects what the **worker model can name** but the registry lacks. A gap outside the model's own knowledge will not leak this way.
- **Weak pressure needs accumulation** — one or two drops are indistinguishable from noise; the sensor sharpens with operating time and run-records.
- Signal quality marker: **variant clusters converging on one concept** (multiple surface forms of the same missing entry) separate "category trying to be born" from stray error.

---

## Evidence — three independent instances (the law was operating before it was named)

1. **The Atlas linker fan (2026-06-10, this discovery's trigger).** `atlas_linker` role (registered, live) fanned over 271 Claude Code documentation pages with an 8-domain closed vocabulary, prompt-level constrained. 135 out-of-vocabulary values dropped by the consumer-side filter; **115 of them were 6 spelling variants of one missing concept ("MCP Servers")** → a 9th domain note was approved and built. Gap-detection cost: zero — exhaust from a tagging fan that took ~36s of engine time across 13 MCP calls. Evidence: event log seqs ~4434–4437+ (`cognition.items` rollups); results at `/home/tim/.claude/jobs/bda8ce28/tmp/linker_results.jsonl`; drop stats in that job's fan-runner report. NOTE the consumer-side location of the filter — the engine itself never saw these drops; that's candidate C1's whole point.
2. **RG10's stubborn-floor entries (prior, this folder).** `gc9_gap_intake.py` harvests "the feature id the model INSISTED on through correction (the gap signal)" — the same phenomenon read from insistence-under-correction rather than enum drops. Deterministic intake → proposed inventory rows.
3. **SYSTEM-GAPS.md (standing, this folder).** The hand-maintained version: "first-use friction is the input, not a failure." Agents ledger MCP/engine needs as they hit them. Gap pressure is this ledger made automatic and engine-native.

Related production line: **[[REGISTRY-FILLING-PATTERN]] (GC2)** — the reusable pipeline for *growing* registries. Gap pressure supplies its **intake**: GC2 consumes what the sensor surfaces. They are two halves of one circuit.

---

## Intentional uses (the extensions catalog, captured from the discovery conversation)

- **Taxonomy bootstrapping**: face an unknown corpus with a deliberately tiny seed vocabulary; fan; harvest drop clusters; add the strongest; re-fire; repeat until drops go quiet. The corpus names itself by successive pressure release (loop-until-dry).
- **Drift monitoring**: re-run a standing fan when the source corpus refreshes; a NEW drop cluster = the world grew a category the map lacks.
- **Starvation (the inverse read)**: registry entries that nothing ever lands in = negative pressure = pruning candidates. One ledger, two signals.
- **Shadow-pass field sensing**: constrained decoding makes wrong shapes impossible — which also hides what the model *wanted* to add. Periodically run a small UNconstrained sample alongside; diff extra keys/values against the schema. The constrained-vs-free gap IS the measurement of what the schema suppresses.
- **Cross-model triangulation**: same fan, two workers; shared drops = real gaps, model-unique drops = idiosyncrasy (the jury pattern applied to sensing).
- **Canary categories**: seed a known-overlapping entry and watch pressure redistribute — calibrates sensitivity before trusting the gauge on unknowns.
- **MCP-face misuse as API pressure**: agents' unknown-tool/invented-param attempts are the sensor pointed at the tool surface — a repeatedly-attempted parameter is a parameter asking to exist. (This is how the grounded-chain law was found, by hand.)
- **Retrieval-side pressure**: log semantic searches with weak best-match distances → queries-with-no-good-answer clusters = content that wants to be written. Inverse: constantly-hit chunks = load-bearing knowledge worth deepening.
- **Operator corrections as drops**: Tim's interrupts/corrections cluster into standing-rule proposals through the same rollup shape.

---

## The candidates (C1–C7, in recommended build order)

Each stage is independently provable by use before the next stands on it. All 🔴 unbuilt as of 2026-06-10.

**C1 — Drops in the engine + inline in the result envelope.** A `vocabulary` constraint mode on output fields: the role declares allowed values (a registry list, not prompt prose); out-of-vocabulary values are neither errors nor coerced — **recorded as drops, returned flagged**. Soft enforcement is deliberate: hard constrained decoding on the value set would make invalid values impossible and kill the sensor. `run_role`/`run_items` envelopes carry `drops` inline (count + top values) so the calling agent SEES pressure in-band. Seams: `runtime/cognition.py` validation tail; `fabric/client.py` returns; the closed output-field-type registry gains the vocabulary mode. Verify-by-use: re-run the atlas fan via a vocabulary-declared role → drops appear in the envelope and the event log, matching the consumer-side counts from instance 1.
**C2 — Drops event kind + query face.** Drops land as their own event kind with conditions (role, model, source address, value, ts), queryable via a `drops` face or an extension of `runs` (the log-IS-the-index pattern `runs` already proves). Verify: query returns instance-1-shaped data after a C1 fan.
**C3 — `registry_load` projection (starvation gauge).** Read-time projection over the event log: every registry entry + its usage counts over a window. Zero-load entries surface as pruning candidates. No new store. Verify: roles fired today show counts; never-fired roles show zero.
**C4 — Rollup role + surfacing into the gate.** A `cluster_drops` role (or run_reduce composition) over a ledger slice → `{concept, variants, count, sample_addresses}`; clusters above threshold flow into the EXISTING surfacing path (inbox / list_surfaced) as registry-addition proposals. The system becomes one more proposer standing in line for the operator's accept. Saved as a cascade: ledger → cluster → surface. Refine-before-gating holds: the operator sees clustered proposals, never raw drops. Verify: feed instance-1 drops through it → it proposes "MCP" with its 6 variants.
**C5 — `op="sense"` (shadow-pass) on the role op-axis.** Third op value beside generate/embed: fire a sample unconstrained (json_object only), diff produced keys/values against the declared schema/vocabulary, deposit differences as drops. Verify: a sense-pass over atlas pages reports the extra fields/values the constraint suppresses.
**C6 — MCP-face misuse ledger.** Record agents' failed/unknown tool, param, and value attempts (the face already fail-louds with rich errors — add the recording) into the drops family. Verify: deliberate wrong calls appear; over time, clusters rank which missing affordances agents want most. Subsumes part of [[SYSTEM-GAPS]]'s manual role over time — the hand-ledger stays for needs the sensor can't see (narrative/design needs).
**C7 — Constitution + capabilities surfacing.** The law into `docs/concepts-and-principles.md` (with preconditions + failure-each-prevents); `capabilities()`/`cognition_info()` document "after a fan, read your drops" as the canonical next move — the correct action made the documented easiest path. Also: migrate `atlas_linker` onto the vocabulary mechanism (its allowed list currently lives in prompt prose + a consumer-side filter).

**Adjacent small candidate (same session's evidence): evidence-in-error for parse failures.** `fabric/client.py` complete(): on unparseable-JSON, the FabricError should carry len + head + tail of the raw content. The 2026-06-10 stale-process hunt took ~40 minutes because the error carried only the JSONDecodeError position; with raw bytes in the error it would have taken one look. (A stale-server-process incident is also documented in that hunt: a long-lived mcp_face process served pre-G24 code from memory while disk was current — symptom: pretty-printed unconstrained output + retry-burn; fix: restart the serving process. Worth a STATE.md gotcha when a builder lands here.)

## Open questions for the builder
- Threshold semantics for C4 (count? variant-diversity? both?) — instance 1 suggests variant-cluster convergence is the stronger signal than raw count.
- Should drops dedupe per-source-item or count every occurrence? (Instance 1 counted occurrences; 93 of one value across ~100 pages reads differently than 93 from one page.)
- Does the vocabulary mode belong on output_fields (per-role) or as a referenced registry list (shared across roles)? Lean: referenced registry list — that's what makes C3's load-counting and C4's proposals registry-shaped.
- Interaction with G24 schema-guided decoding: vocabulary values must stay OUT of the json_schema enum (or the sensor dies) — confirm the derivation in `fabric/client.py` doesn't tighten this accidentally.

## Update protocol
This is a living capture. A builder session that lands a candidate flips its 🔴, links the commit, and updates the root AGENTS.md pointer's status line. New instances of the law observed in operation get added to the evidence section — accumulation is the point.
