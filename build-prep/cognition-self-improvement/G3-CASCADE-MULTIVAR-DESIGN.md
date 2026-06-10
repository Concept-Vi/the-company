# G3 — Cascade Multi-Variable Design (the seams that let code-chains become data-chains)

**Status: TENTATIVE design — written 2026-06-10 from the lived evidence of the RG10 build. Not
reviewed by Tim; assumptions marked. This is the design-first half of G3; nothing here is built.**

## The question G3 answers

The flows registry (GC1) holds chains as *committed code* because today's cascades (declared
data-chains) cannot express what the registry-filling chain needs. The manual module
(`registry_generation_run.py`) supplies three seams by hand — those seams ARE the spec for what the
cascade engine lacks. Closing them collapses the two chain-kinds toward one: **declare the chain,
never code it** (the strongest form of registry-is-truth for processes — and the shape Tim's
GC13 lifecycle wants, where an accepted proposal *dispatches a declared chain*).

## The four seams (each named by the manual code that proves the need)

### S1 · Keyed per-unit context
The MAP step needs each unit to see ITS OWN group's ground (the mockup summary for the mockup that
unit came from). Today `run_items` has ONE shared ctx; the manual module threads `ground` per batch
by running one mockup at a time.
**Design:** a step field `unit_ctx: {ground: "run://<turn>/screen_reader/{mockup}"}` — `{field}`
substitutes from the unit dict (units become dicts with declared fields; the address template
resolves per unit). Engine: `run_items` gains an optional `per_unit_ctx` resolver. Additive — absent
field, today's path byte-identical.

### S2 · Resolve-once shared inputs
Exemplars + closed vocabularies are resolved ONCE and shared across all N fires (the
context-efficiency law). The manual module builds them in `_grounding_payload`.
**Design:** a cascade-level `shared:` block of named inputs resolved at cascade start into the shared
ctx. The resolver vocabulary is the open question — ASSUMPTION: reuse the address schemes
(`code://` file reads via the corpus, `run://` priors) rather than minting a `file://` scheme;
a `corpus-query:` form could cover "top-k exemplars" (rides G4 retrieve). Needs a decision.

### S3 · Judgment + check step kinds
The chain ends in run_jury/run_panel + deterministic gates (refcheck, prose_check) — none are
cascade step kinds.
**Design:** three additive step kinds:
- `jury` — fires `run_jury` (exists; role must declare draws + verdict_rule);
- `panel` — fires `run_panel` (exists; references the verdict_panels registry by id);
- `check` — a DETERMINISTIC gate by NAME. This needs a **checks registry** (`checks/<id>.py`, the
  refcheck/prose_check arc made declarable — the third instance of "the model raises, the floor
  decides" suggests the floor itself should be registry data). The check's verdict routes the unit
  (pass→continue, fail→flag), mirroring confirm_status's declared AND.
ASSUMPTION: the checks registry is the right unification (it also gives GC14's condition-clauses a
home pattern later). The floor law holds: checks are repo-authored, MCP-invoked, judge-only.

### S4 · Partition + resume stay OUT (the flows/cascades split survives)
The chain runs per-mockup with resume-safe state. Cascades should express ONE pure batch;
partitioning, retry budgets, and resume state remain the FLOW layer's job (flows wrap cascades).
This keeps cascades deterministic data and keeps statefulness where git-committed code already
handles it. DECISION, not assumption — reversing it would rebuild flows inside the cascade engine.

## What this unlocks, in order
S3-check is the highest-value single piece (every future chain wants declared floors); S1+S2
together make the registry chain declarable end-to-end; the full set lets `flows/registry_generation`
become a thin `run_cascade` call — and a future accepted-proposal (GC13) can carry its build recipe
as pure data.

## Build order (when greenlit)
1. checks/ registry + the `check` step kind (S3a — smallest, highest reuse)
2. `panel`/`jury` step kinds (S3b — executors exist)
3. S1 per-unit ctx (run_items extension, additive)
4. S2 shared block (after the resolver-vocabulary decision)
5. Re-express registry_generation as a saved cascade; the flow row becomes its wrapper (proof by use)
