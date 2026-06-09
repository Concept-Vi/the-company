---
type: constitution
module: roles
aliases: ["roles — constitution"]
tags: [company, constitution, roles, cognition, role-registry]
governs: [C2.1, C2.2, C2.3, C2.4, C2.5]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[nodes — constitution]]", "[[fabric — constitution]]"]
status: living
---

# roles/ — module constitution

**Is:** the **file-discovered role registry** of the collective cognition (Concurrent Cognition G2). A
**role** is a named model-FUNCTION — a specific job done by a model that is not (necessarily) the
conversational brain. Roles were two hardcoded things before G2 (`suite.py`'s one-entry `ROLE_REGISTRY`
class dict + `cognition.py`'s inline `SPIKE_ROLES`); G2 promotes both into ONE registry: a `roles/` dir,
one self-registering `roles/<id>.py` per role — **exactly mirroring how node-types self-register**
(`nodes/` + `runtime/registry.py`). Adding a role = adding a file; it self-registers + is queryable; a
removed file un-registers on `rediscover`.

**Guarantees:** a role is **one self-contained declaration** — a module-level `ROLE` dict over the C2.1
superset schema `{id · label · description · prompt_template · output_schema · input_addresses · op · trigger
· model_binding · mode_scope · rules · render_hint · draws · verdict_rule · knobs · …}`. Every field
except `id` is OPTIONAL, and a role's **facet follows which fields are populated**:
`prompt_template`+`output_schema` ⇒ a **generate** role can **fire** (`run_role`/`run_swarm`); `op:embed`
⇒ an **embed** role fires the vector path (no prompt/schema needed — `complete_embeddings`, local
embedder only); `mode_scope` ⇒ it is in that mode's **cast**; `draws` ⇒ it is a **jury** (N varied draws
+ a pure verdict_rule). The **op-axis** (`op: generate|embed`, default `generate`) declares the role's
OPERATION as data — today's every role is `generate` (byte-identical). On drop-in it
self-registers (`RoleRegistry.discover` reads `roles/*.py`) and is queryable
(`cast_for_mode`/`fireable`/`juries`) — **with no change to the cognition driver, suite, or UI.**
Roles fire model calls through `fabric/` guards (a model runs only INSIDE a role — L2).

**The registry is the single source (C2.1):** `runtime/roles.py` `RoleRegistry` mirrors
`runtime/registry.py` `NodeRegistry` (`discover`/`rediscover`/`register`); `suite.py` builds
`ROLE_REGISTRY = {id: role.spec}` from it (so `resolve_role`/`roles()` read the SAME dict-view), and
`cognition.py` sources `SPIKE_ROLES` from it. No second role notion, no fork.

**The roles (the live set — the drift home; `tests/roles_acceptance.py` asserts each is reflected here):**
- **`judge`** — role #0, the finished-thought judge (the voice circuit's semantic endpoint). Config-only:
  declares NO `prompt_template`/`mode_scope`/`draws` → fires via `is_finished_thought`, not the swarm; in
  no cast; not a jury. Moved here from suite.py UNCHANGED IN BEHAVIOUR (C2.2 — byte-identical binding).
- The **`listening` cast (C2.3 — DECISIONS Batch 3 Q1, the first locked cast):**
  - **`focus`** — the selector: utterance → intent + which auxiliary roles to fire (gates the cast).
  - **`recall`** — memory: utterance (+memory) → a past-context snippet + whether it is relevant to inject.
  - **`ground`** — citable facts: live state → whether in scope + a grounding note (gates recall's inject).
  - **`connect`** — a link: topic+thread → a related thread/decision worth surfacing.
  - **`check`** — contradiction: a forming answer vs ground → does it contradict? (CHAINS after a part
    starts — its dependency is declared as DATA; the chaining executor is G3/G4).
  - **`voice`** — tone: persona+answer → the toned phrasing (the cognition role, not the TTS module).
- The **`walkthrough` cast (guided-review's enriched guided turn — on the C cast-beyond-listening seam, 56d42f4):**
  the 6 `listening` roles above ALSO declare `mode_scope ⊇ {walkthrough}` (the enrichment swarm fires during
  the guided review walk), plus:
  - **`screen_reader`** — the at-altitude screen-comprehension: reads the `MOCKUP UNDER REVIEW` block (the
    `mockup://` focus injection, cognition's A) → a plain-language "what this screen is + what you can do" for
    the non-developer operator. Walkthrough-cast only (the review faculty; not `listening`). `op:generate`.
- **`verify_jury`** — the canonical **jury** (C2.4): `draws:3` + a pure majority-vote `verdict_rule`. In no
  cast (fired explicitly via `run_jury`). **⚠ E4 caveat:** N draws on ONE model are correlated (variance,
  not independent error) — a correctness-jury that matters needs model diversity; the verdict_rule shape
  accepts a future 2nd-model/cloud tiebreak. v1 single-model, limit documented.
- **`reduce_synth`** — the demonstrative **reduce-role** (C 2/4): the `reduce-tree` THOUGHT_SHAPE's declared
  `join` role made real — `op:generate`, takes the N map-output notes (composed by `run_reduce` into one
  `"notes"` input via the C 1/4 input-axis) → ONE merged `{summary}`. In no cast (fired explicitly via
  `run_reduce(mode="role")`, the cross-unit synthesize join — `runtime/cognition.py:run_reduce`). The
  reduce DRIVER also offers `mode="rule"` (a pure L2 verdict over the N values, mirroring `run_jury`) and
  `mode="cluster"` (the embed-cluster "which of these are the same" discovery join, reusing
  `nodes/retrieve._cosine`).
- **`repo_digest`** — the demonstrative **DIRECT-CREATE fixture** (#58): authored LIVE by the agent via
  `create_role` (no operator approval — the authoring-apply reframe), it reads a supplied file's content
  → a 1-sentence `{digest, kind}` of what the file is + its role in the system. `op:generate`, in no
  cast (fired explicitly via `run_role`/`run_items`); the repo-processing test fixture (map a folder of
  files through it). Proof that authoring is the agent's: written + git-committed `[self-apply]` + live
  in `cognition_info` with NO surfaced item.
- **`register_element`** — the **Registry-Generation chain's MAP role** (RG3): reads ONE candidate mockup
  element + its grounded context (parent dossier · mockup summary · exemplars · the feature inventory) →
  a PROPOSED registry dossier (`{address, represents, howto, capabilities, maps_to_feature, grounding}`)
  in the 82 existing `ui://` entries' voice. The `grounding` field is a discrete TAG (`built|proposed|
  uncertain|defer`) — the NO-CONFIDENCE law (G16: tags+counts, never a fabricated float; the old
  `confidence:float` was empirically flat noise — all 0.85 — so it was migrated out to a state tag).
  `op:generate`, `mode_scope:{registration}` (the cast-beyond-listening seam fires it). Fired over N
  candidates by `run_items` (RG4). NO-FICTION is the make-or-break: capabilities ⊆ the closed vocabulary,
  `maps_to_feature` a real inventory id COPIED VERBATIM or the literal `proposed` (the model coins INB-*
  ids by analogy — the verbatim instruction + the deterministic floor catch it) — it PROPOSES, never
  writes (operator-only floor). Mirrors `screen_reader`.
- **`confirm_registration`** — the **Registry-Generation chain's CONFIRM gate, Layer 2** (RG6): the
  accuracy **jury** (`draws:3` + a pure `quorum_grounded` `verdict_rule`). Each draw sees the PROPOSED
  dossier AND the ELEMENT it claims to represent → judges ONE boolean `grounded` (is `represents` accurate
  + `howto` honest to the element?); the N draws → a deterministic strict-majority quorum. In no cast
  (fired explicitly via `run_jury`). **TWO-LAYER design:** the no-fiction GUARANTEE is the DETERMINISTIC
  floor `design/_system/refcheck.py::check_dossier` (Layer 1 — model-independent: catches fabricated
  capability/feature/code refs regardless of model strength); THIS jury is the SOFT accuracy judgment on
  top. `confirm_status()` (in this role's file) ANDs them via a declared `runtime/rules.py` RULE_OPS data-
  AST → `confirmed` ⟺ quorum AND refcheck.passed; else FLAGGED (variance-not-error → flag, never dropped).
  **⚠ E4 caveat** (shared with `verify_jury`): N draws on ONE 4B are correlated — variance, not
  independent error — so Layer 2 is SOFT; the verdict_rule shape accepts a future stronger-model/cloud
  tiebreak (C2.5 / `models_for_role`) as an ENHANCEMENT, never a requirement.
- **`verify_lens`** — the **verification jury's LENS role** (COMPOSITIONS ⑥): judges ONE change-under-test
  through ONE lens (the lens rides in the unit: correctness · floor · drift · matches-criterion ·
  registry-is-truth · adversarial-disprove) → `{lens, verdict: pass|fail|uncertain, evidence,
  breaking_case}`. NOT a draws-jury — its "jury" is the cross-LENS fan (N distinct lenses, one draw each
  via `run_items`); the adversarial-disprove lens defaults to fail/uncertain if it can construct a
  breaking case. In the `verification` cast only (a cast-beyond-listening context; listening untouched).
  The deterministic green-iff-all-pass verdict-TALLY is the `verdict-tally` `run_reduce(mode='rule')`
  reduce-rule (now built, mcp_face `_REDUCE_RULES`); the unit contract is `{lens, change, bar}`.
- **`develop_option`** — the **option-panel MAP role** (COMPOSITIONS ⑩): develops ONE approach to a
  decision through ONE biasing lens (the lens rides in the unit: mvp-first · risk-first · reuse-first ·
  framework-first · radical-recompose) → `{lens, approach, buys, costs, touches, risk}`. In the `panel`
  cast (cast-beyond-listening; listening untouched). Fanned over the lenses via `run_items` → a diverse
  option-space for Tim's A/B/C forks.
- **`score_options`** — the **option-panel REDUCE role** (⑩, mode=role): takes the N per-lens approaches
  → `{scored:[{lens,rank,why}], recommendation, grafts}` — RANKS each (ordinal, 1=strongest) + a
  recommendation that may graft runner-up strengths. `rank` is an int ordinal not a 0..1 score (G16
  no-confidence: tags+counts, no fake-precision float). Mirrors `reduce_synth`'s reduce-role shape.
- **`mine_exchange`** — the **transcript-miner MAP role** (COMPOSITIONS ③): reads ONE conversation
  exchange (Tim-message + my-response, riding in the unit) → a self-improvement extract `{decision,
  rationale, tim_correction, my_error, bug_fix, needs_tim, frustration, pattern_tag}` (7 optional + the
  required `pattern_tag`). In the `mining` cast (cast-beyond-listening; listening untouched). Fanned over
  exchanges via `run_items`; the cross-exchange embed-CLUSTER of pattern_tags into named failure-patterns
  (→ drafts `feedback-*.md` for review) is the follow-on (needs the embedder).
- **`judge_mining`** — the **transcript-miner CONFIRM role** (③, no-fiction gate): validates ONE
  `mine_exchange` extract against its RAW exchange → `{grounded:bool, unsupported:str}` (did the miner
  fabricate a decision/correction not in the exchange?). NO confidence float (G16 no-confidence: the
  boolean verdict + the named unsupported field ARE the evidence). A single-generate validator
  (mirrors `verify_lens`; E4 caveat — soft, model-binding accepts a stronger tiebreak). In `mining`.
- **`decompose_seed`** — the **spec-compiler's seed→groups role** (COMPOSITIONS ⑦, 1×1): a dense seed →
  `{groups:[{group_id, what, systems_touched}]}` (the loop-prep "group by system, not implementation-order"). In the `spec` cast.
- **`expand_criterion`** — the **spec-compiler's group→criterion MAP** (⑦): one group → a TWO-FACED criterion
  `{id, function, form, files_touched, reuse_or_netnew, preserves}` (FUNCTION + FORM both; reuse-claim is
  PROPOSED here, the authoritative no-fiction grounding deferred to `ground_criterion`). In `spec`.
- **`ground_criterion`** — the **spec-compiler's no-fiction reuse-check** (⑦ MAP): one criterion →
  `{criterion_id, grounded: reuse|net-new, cite (real file:symbol if reuse), note}`. Degrades cleanly
  without the corpus (names the believed file + states confidence); the corpus-grounded retrieve is the ① enhancement. In `spec`.
- **`triad_synth`** — the **spec-compiler's REDUCE role** (⑦, mode=role; mirrors `reduce_synth`, no cast):
  the N grounded criteria → `{completion_criteria, implementation_guide, research_synthesis}` (the loop-prep
  triad, house style). A DRAFT → me → Tim (never a build off an unconfirmed compiled spec).
- **`judge_drift`** — the **drift-radar CONFIRM role** (COMPOSITION ②): given a cluster of semantically-near
  repo files (from `run_reduce(mode='cluster')` over `space='repo'`), judges genuine `built-twice` / `overlap`
  vs legitimately `distinct` → `{verdict, shared, the_source, note}` — the false-positive guard so the drift
  map flags real unification targets, not every near-neighbour. Single-generate (mirrors `verify_lens`); NO
  confidence float (verdict token + cluster nearness carry the signal). In the `drift` cast. Judges, never
  fixes — a confirmed drift becomes a MARK for review.

**Where new things go:** a new role = a new file `roles/<id>.py` declaring its `ROLE` dict (its `id`
MUST equal the file name). Put it in a mode's cast by adding that mode to its `mode_scope`. Make it a
jury by declaring `draws:N` + a `verdict_rule`.

**To extend:** declare the `ROLE` dict, drop it in. That's the whole self-extending path. **Update THIS
file** (the drift home) when you add a role — `tests/roles_acceptance.py` fails loud if a discovered
role isn't reflected here (mirrors how `edge_kinds_acceptance` guards `EDGE_KINDS` against
`contracts/AGENTS.md`).

**Seam:** discovered by `runtime/roles.py:RoleRegistry`; consumed by `runtime/suite.py` (`resolve_role`/
`roles()`/`cast_for_mode`/`resolve_role_binding`) and the cognition driver `runtime/cognition.py`
(`run_role`/`run_swarm`/`run_jury`). C2.5 binding: `role.requires ⊆ provider.provides`
(`runtime/roles.py:model_satisfies`/`resolve_binding`) against `Suite.capability_providers()` — a thin
seam G8/L-model will populate with the full capability catalog (the downstream dep).

**Never:** hardcode a role in a class dict (the thing G2 retired) · fork a second registry pattern (mirror
`NodeRegistry`, reuse-don't-parallel) · run a model inside a *rule* (a model runs only inside a *role*; a
routing/verdict rule is a pure declared function — L2) · let a role emit `resolve`/`approve`/`dispatch`
(the `claude -p`/build-dispatch floor is lead-only) · ship a role without reflecting it in this drift home.

## Relates to
- **Discovered by** [[runtime — constitution]] (`runtime/roles.py`, mirroring `runtime/registry.py`) and
  **consumed by** the cognition driver + the Suite.
- **Uses** [[fabric — constitution]] — a role's model call passes through its guards (validate/retry).
- **Mirrors** [[nodes — constitution]] — the same self-registering, file-discovered, queryable shape.

## Read next
[[Company Map]] (the whole picture) · [[runtime — constitution]] (what fires these) · the triad at
`build-prep/concurrent-cognition/` (the G2 criteria + guide).
