# Registry-Generation Chain — Implementation Guide (HOW)

> HOW to build each RG criterion. Reads on RESEARCH-SYNTHESIS (what exists) + COMPLETION-CRITERIA (the bar).
> The spine: the chain is a **declared cascade** over the cognition engine — almost all reuse. Two parallel
> loops build it (guided-review [M] + cognition [C]); they meet at the cascade (RG7) + the whole-by-use (RG10).

## Principles (why it's shaped this way)
- **The chain is DATA, not code.** Declare it as a saved cascade (`save_cascade`) so it's registry-is-truth,
  reconfigurable, re-runnable when mockups change — NOT a hand-written orchestration script. (no-hardcoding.)
- **Grounding is everything (no-fiction).** A registration is only as good as its context: element + parent
  dossier + mockup summary + corpus exemplars + feature inventory. A model with thin context invents
  capabilities — which corrupts the registry (the one truth). Over-provide context; mark un-built `proposed`.
- **The floor is sacred.** The swarm PROPOSES; Tim approves; only then write. Never let the chain auto-write
  `addresses.json` (operator-only floor — the consent model). git-revert is the second net.
- **Reuse, never parallel.** Extend `parse.py`, grow `addresses.json`, use `run_cascade`, surface via governance.
  Every parallel system doubles the truth surface — the exact thing the registry exists to prevent.

## Sequence of operations (the chain, end to end)
1. **EXTRACT** (parse.py pass, deterministic): mockups → candidate units (filter meaningful). → `candidates.json`.
2. **GROUND** (`run_role(screen_reader)` × mockups): → per-mockup summaries, keyed by file.
3. **MAP** (`run_items(register_element, candidates)`): each unit + its context → a proposed dossier @ run://.
4. **REDUCE** (`run_reduce`): cluster-dedup across mockups + nest/validate tree + merge howtos → reconciled set.
5. **CONFIRM** (`run_jury` + refcheck): accuracy + no-fiction gate; flag low-confidence. → confirmed set.
6. **PROPOSE** (governance surface): confirmed set → ONE batch `review` decision in the inbox.
7. **APPROVE** (Tim, operator-only): walks the batch → approve once → triggers write-back.
8. **WRITE-BACK** (merge + stamp + round-trip): addresses.json += entries · mockups += data-ui-ref · re-run parse.py.
9. **PROVE** (RG10): reload studio → click a once-dead element → it resolves to its new dossier.

## File paths with roles (NEW / MODIFY / REUSE / who)
- **MODIFY** `design/_system/parse.py` [M] — ADD a `--extract-candidates` pass emitting `candidates.json`
  (the units). KEEP the existing data-ui-ref parse. The "meaningful element" filter lives here (tag allowlist +
  has-text + not-pure-layout). REFERENCE the existing parse for the selector/path derivation.
- **NEW** `roles/register_element.py` [C] — the role (RG3). Mirror `roles/screen_reader.py`'s shape exactly.
  Reflect it in `roles/AGENTS.md` (the drift-home — fail-loud if not). input_addresses = the candidate fields;
  output_schema = the dossier. CONTEXT assembly is the role's prompt_template (element + parent + summary +
  exemplars + inventory).
- **NEW (data)** `design/_system/registry-generation.cascade.json` (or via `save_cascade`) [J] — the cascade spec:
  the 5 steps + the run:// wiring. Authored by [M], run by [C]'s engine.
- **NEW** `design/_system/registry_writeback.py` [M] — the merge (entries→addresses.json, dedup-safe, additive),
  the data-ui-ref stamp (into the mockup HTML at the recorded selector), the parse.py re-run. Fail-loud; provenance.
- **MODIFY** the review surface (`canvas/app/src/regions/Review.tsx` / a new `RegistryProposals` region) [M] —
  RG8's batch-review surface: render the proposed dossiers, the ONE approve, per-entry skip. On corpus tokens.
- **REUSE (do not modify):** `runtime/cognition.py` (run_items/run_reduce/run_role — [C] holds), `runtime/suite.py`
  (save_cascade/run_cascade — [C] holds), `roles/screen_reader.py`, `design/_system/{addresses.json,corpus-meta.json,
  refcheck.py}`, `runtime/governance.py` (surface/inbox), the Feature & Function Inventory.

## The register_element role — output schema + context (the make-or-break of A)
```
output_schema: { address: str (proposed ui://, nested under the parent),
                 represents: str (short, like the 82's "RUN-run"),
                 howto: { what: str, what_you_can_do: str, how_to_change: str },  # at-altitude, the 82's voice
                 capabilities: [str],  # from the real capability vocabulary, NOT invented
                 maps_to_feature: str | "proposed",  # the feature inventory id, or proposed-not-built
                 confidence: float }
```
Context (the prompt_template assembles): the element outerHTML+text+tag · the parent registered address + ITS
dossier (so the child nests + inherits framing) · the mockup summary (RG2) · 3-5 existing addresses.json entries
as few-shot (voice/shape) · the feature inventory (no-fiction). DON'T invent — if no feature maps, `proposed`.

## Do's and don'ts
- DO declare the chain as a cascade (RG7) — DON'T hand-orchestrate the 5 steps in a script (no-hardcoding).
- DO surface proposals to Tim (RG8) — DON'T auto-write addresses.json (operator-only floor; the consent model).
- DO ground register_element in the feature inventory — DON'T let it invent a capability (corrupts the one truth).
- DO cluster-dedup across mockups (RG5) — DON'T register ui://inbox twice because it appears in C1 and C5.
- DO extend parse.py (RG1) — DON'T write a second mockup parser.
- DO mark un-built elements `proposed` — DON'T register a mockup-only element as if it's a live built surface.
- DON'T block V-A on RG11 (the live-surface generalization) — scope it, ship the mockup chain first.

## The parallel-loop split (so cognition's loop bolsters, doesn't collide)
- **[M] guided-review loop builds:** RG1 (extract), RG8 (proposal surface), RG9 (write-back+round-trip), the
  cascade spec authoring (RG7 data), drives RG10 (whole-by-use). File-disjoint: design/_system/* (parse,
  writeback, cascade json) + canvas/app/src/* + addresses.json/mockups (the write-back, operator-gated).
- **[C] cognition loop builds:** RG3 (register_element role), RG6 (confirm jury/role), any engine gap RG4/RG5
  expose (run_items at this N, cluster tuning), the run:// wiring. File-disjoint: roles/* + cognition.py/suite.py.
- **[J] meet at:** RG7 (the cascade composition — I author the spec, their engine runs it) + RG10 (the whole
  by-use — a real run, approve, a dead element resolves) — the convergence-round seam.
- **Coordination:** the claims board (file-disjoint) + MESSAGES (announce the role lands, the cascade spec lands,
  the whole-run). The flag-tiers + gate-green-before-shared-commit apply. cognition's parallel loop and mine
  fire staggered; neither writes the other's files.

## Verify (by USE, the loop's law)
- RG1: run the extract → inspect candidates.json (count sane, fields present, noise filtered).
- RG3/RG4: fire register_element on real elements → dossiers grounded, no fiction (adversarial spot-check).
- RG5: feed known duplicates → collapsed; tree valid vs the grammar.
- RG6: fabricated capability → flagged; real → passes.
- RG7: run_cascade over a 2-mockup slice → full pipeline lands at run://.
- RG8: confirmed set → one inbox batch → approve fires write-back; reject writes nothing.
- RG9/RG10: approve → addresses.json grew + mockup stamped + reload + click the once-dead element → rich dossier.
  Chrome + design-critic for RG8/RG10 FORM; the *feel* of the batch review + the resolved answer = needs-tim.
