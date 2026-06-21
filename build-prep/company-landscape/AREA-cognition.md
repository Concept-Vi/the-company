---
type: landscape-dragnet
area: cognition — roles / minds / generation_policies / lifters / ai_tics
date: 2026-06-21
status: exhaustive read-only sweep
---

# AREA-cognition — Exhaustive Landscape Dragnet

Coverage: `roles/` (30 source files), `minds/` (4 source files), `generation_policies/` (6 source files), `lifters/` (3 source files), `ai_tics/` (7 source files). Total 50 source files + 5 AGENTS.md constitutions.

---

## 1. ROLES/ — complete inventory

### Constitution (`roles/AGENTS.md`)
- **What it is:** The file-discovered role registry of Concurrent Cognition (G2). One self-registering `roles/<id>.py` per role — mirrors `nodes/` self-registration pattern.
- **Schema:** `ROLE` dict with fields: `id` · `label` · `description` · `prompt_template` · `output_schema` · `input_addresses` · `op` · `trigger` · `model_binding` · `mode_scope` · `rules` · `render_hint` · `draws` · `verdict_rule` · `knobs` · `prompt_slot` (coordinate-resolved framing). All fields except `id` optional.
- **Facets:** `generate` (default op, fires model) | `embed` (fires vector path, no prompt needed) | jury (adds `draws:N` + `verdict_rule`).
- **Discovery:** `runtime/roles.py:RoleRegistry.discover()` reads `roles/*.py` — consumed by `runtime/suite.py` + `runtime/cognition.py`.
- **Seam:** `tests/roles_acceptance.py` asserts every discovered role is reflected in the constitution. Adding a file = adding a role, zero code change.

### Role Inventory (all 30 source files)

#### Core / Legacy
| id | op | mode_scope | is_jury | description |
|----|-----|-----------|---------|-------------|
| `judge` | generate | none (config-only, no prompt_template) | no | Role #0. Voice circuit's finished-thought endpoint. Fired by `is_finished_thought` / POST /api/voice/finished-thought. Has `recommended_model: cyankiwi/Qwen3.5-4B-AWQ-4bit` (measured 463ms vs cloud 2113ms). `requires:["chat","fast","no-think"]`. `knobs:{max_tokens:2048,temperature:0}`. **DUAL BINDING ISSUE**: flat top-level fields (legacy `resolve_role` read) AND `model_binding` dict coexist — flagged for G8 unification. |
| `embed` | embed | none | no | Demonstrative op-axis embed role. Embeds `ctx["utterance"]` via local embedder only. No prompt_template. `requires:["embed"]`. Returns `{vector,dim,model}`. Fail-loud on missing/dim-mismatch embedder. |

#### Listening Cast (C2.3 — the locked cast, DECISIONS Batch 3 Q1)
| id | op | mode_scope | is_jury | description |
|----|-----|-----------|---------|-------------|
| `focus` | generate | listening, walkthrough | no | The SELECTOR. Utterance → `{intent, which_roles:[...]}`. Fires first every turn; gates the rest of the cast. `requires:["chat","json","fast"]` — extraction role, wants the no-think 4B fast path. CAPABILITY TIER #71 declared. |
| `recall` | generate | listening, walkthrough | no | The MEMORY. Utterance + memory → `{snippet, relevant:bool}`. Fires when `focus.which_roles` includes "recall". Injection rule: `recall.relevant AND ground.in_scope` → inject into later part. |
| `ground` | generate | listening, walkthrough | no | GROUNDING. Live state → `{in_scope:bool, note}`. Fires when `focus.which_roles` includes "ground". `in_scope` co-gates recall injection. |
| `connect` | generate | listening, walkthrough | no | LINK finder. Topic + thread → `{link, worth_surfacing:bool}`. Fires when `focus.which_roles` includes "connect". |
| `check` | generate | listening, walkthrough | no | CONTRADICTION sentinel. Forming answer vs ground → `{contradicts:bool, note}`. CHAINS AFTER part-1 starts (dependency declared as data: `"run://<turn>/part-1"` + `"ground"`). Chaining executor is G3/G4 — **NOT YET BUILT** (role declares it, the staged-chainer is downstream). |
| `voice` | generate | listening, walkthrough | no | TONE shaper. Persona + answer → `{toned, tone}`. Fires when `focus.which_roles` includes "voice". Distinct from the TTS voice/ module. |

#### Walkthrough Cast (cast-beyond-listening seam, 56d42f4)
| id | op | mode_scope | is_jury | description |
|----|-----|-----------|---------|-------------|
| `screen_reader` | generate | walkthrough only | no | Screen/mockup comprehension for non-developer operator. Reads `MOCKUP UNDER REVIEW` block (mockup:// focus, cognition's A) from live-state. → `{screen_present:bool, what_this_is, what_you_can_do}`. Walkthrough-cast faculty (not listening). |

#### Explain-wire (2026-06-21, NEW)
| id | op | mode_scope | is_jury | description |
|----|-----|-----------|---------|-------------|
| `explain_role` | generate | none (fired explicitly) | no | **DECISION EXPLAIN role** — when Tim opens a decision card. Composes THREE halves: recollection's `block`+`caveat` (input_addresses), fork's `explanation_policy_for(decision)` (policy=), and own `prompt_slot` (per-subtype framing resolved by `coordinate={subtype}`). Has 4 subtypes in `_FRAMING`: `theorem-fork` (NEVER-ASSERT law), `authorize` (security/risk), `trade-off` (neutral axes), `cross-lane` (technical recommendation). Default fallback for unknown subtype. `prompt_slot` REPLACES `prompt_template` wholesale when coordinate is set. |

#### Jury roles (demonstrative)
| id | op | mode_scope | is_jury | draws | verdict_rule | description |
|----|-----|-----------|---------|-------|-------------|-------------|
| `verify_jury` | generate | none | yes | 3 | `majority_vote` | Canonical jury (C2.4). N varied draws of boolean `{holds,reason}` → deterministic majority vote. E4 caveat: correlated draws on one model. Slot-in point for model-diversity tiebreak. |
| `confirm_registration` | generate | none | yes | 3 | `quorum_grounded` | RG6 accuracy gate. TWO-LAYER: Layer1=deterministic refcheck (`design/_system/refcheck.py:check_dossier` — vocabulary/feature/code fabrication check); Layer2=soft jury quorum. `confirm_status()` ANDs them via `CONFIRM_RULE_AST` (declared RULE_OPS data-AST). E4 caveat applies. imports `refcheck.py` via `_SYS_DIR` path insertion. |

#### Reduce roles (demonstrative)
| id | op | mode_scope | input_addresses | description |
|----|-----|-----------|----------------|-------------|
| `reduce_synth` | generate | none | `("notes",)` | Demonstrative reduce-role (C2/4). N map-output notes → `{summary}`. `requires:["chat","json","reasoning"]` — CAPABILITY TIER: wants a reasoner not the 4B. |
| `score_options` | generate | none | `("notes",)` | Option-panel REDUCE (COMPOSITIONS ⑩). N develop_option approaches → `{scored:[{lens,rank,why}], recommendation, grafts}`. `rank` is ordinal int not float (G16 no-confidence). |
| `triad_synth` | generate | none | `("notes",)` | Spec-compiler REDUCE (COMPOSITIONS ⑦, step 3). N grounded criteria → `{completion_criteria, implementation_guide, research_synthesis}` (three markdown docs). Needs generous `max_tokens` — 512 truncates three docs → fail-loud JSON parse failure. |

#### Registry-Generation chain (cast: registration)
| id | op | mode_scope | is_jury | description |
|----|-----|-----------|---------|-------------|
| `register_element` | generate | registration | no | RG3 MAP. Candidate element (snippet/text/tag + parent dossier + exemplars + inventory) → proposed registry dossier `{address,represents,howto:{what,what_you_can_do,how_to_change},capabilities,maps_to_feature,grounding}`. NO-FICTION: capabilities ⊆ closed vocabulary (5 caps); `maps_to_feature` verbatim from inventory or "proposed". Defers if selector already registered. DEFER rule: sets `grounding:"defer"`. `grounding` is discrete tag (G16, not float — old float was empirically flat noise at 0.85). G3·S1 RESOLVED: `run://<turn>/screen_reader/{mockup}` replaced by bare `"ground"` in input_addresses, materialized per-unit via `run_items` unit_ctx. |
| `confirm_registration` | generate | none | yes | (see jury table above) |

#### Spec-compiler (cast: spec, COMPOSITIONS ⑦)
| id | op | mode_scope | description |
|----|-----|-----------|-------------|
| `decompose_seed` | generate | spec | Step 2a. Dense seed → `{groups:[{group_id,what,systems_touched}]}`. Groups by SYSTEM boundary not implementation order. 1×1 role (not fanned). Advisory: drafts groups, never builds. |
| `expand_criterion` | generate | spec | Step 2b MAP. One group → TWO-FACED criterion `{id,function,form,files_touched,reuse_or_netnew,preserves}`. BOTH faces mandatory (form="n/a" only for pure-backend). Reuse-claim is PRELIMINARY — deferred to `ground_criterion`. |
| `ground_criterion` | generate | spec | Step 2c MAP. One criterion → `{criterion_id, grounded:"reuse"|"net-new", cite, note}`. NO-FICTION make-or-break: NEVER invent a reuse cite. `corpus_slice` optional (degrades cleanly without embedder). NOT a draws-jury. |
| `triad_synth` | generate | none | Step 3 REDUCE (see reduce table above) |

#### Verification jury (cast: verification, COMPOSITIONS ⑥)
| id | op | mode_scope | description |
|----|-----|-----------|-------------|
| `verify_lens` | generate | verification | MAP. One lens + change + bar → `{lens, verdict:"pass"|"fail"|"uncertain", evidence, breaking_case}`. Six LENSES: correctness · floor · drift · matches-criterion · registry-is-truth · adversarial-disprove. NOT a draws-jury (cross-lens fan, not same-role draws). Verdict tally (green-iff-all-pass) is downstream `_REDUCE_RULES` reduce-rule. |

#### Option panel (cast: panel, COMPOSITIONS ⑩)
| id | op | mode_scope | description |
|----|-----|-----------|-------------|
| `develop_option` | generate | panel | MAP. One lens + question + constraints → `{lens,approach,buys,costs,touches,risk}`. Five LENSES: mvp-first · risk-first · reuse-first · framework-first · radical-recompose. Advisory: never picks the fork. |
| `score_options` | generate | none | REDUCE (see reduce table above) |

#### Transcript miner (cast: mining, COMPOSITIONS ③)
| id | op | mode_scope | description |
|----|-----|-----------|-------------|
| `mine_exchange` | generate | mining | MAP. Exchange `{tim_message,my_response}` → `{decision,rationale,tim_correction,my_error,bug_fix,needs_tim,frustration,pattern_tag}`. NO-FICTION: most fields default to "". Follow-on: embed-cluster of pattern_tags needs bge-m3 embedder window — FLAGGED, NOT BUILT. |
| `judge_mining` | generate | mining | CONFIRM. One `{extract,raw_exchange}` unit → `{grounded:bool,unsupported}`. Bias toward FAIL (false negative = passing fabrication). NOT a draws-jury. E4 caveat. |

#### Drift radar (cast: drift, COMPOSITION ②)
| id | op | mode_scope | description |
|----|-----|-----------|-------------|
| `judge_drift` | generate | drift | CONFIRM gate. Cluster of near repo files → `{verdict:"built-twice"|"overlap"|"distinct", shared, the_source, note}`. Conservative: only flag real drift, not every near-neighbour. NO confidence float. Judges, never fixes — a confirmed drift becomes a MARK. |

#### Atlas / Agent-authored roles (via create_role #58 direct-create)
| id | op | mode_scope | description |
|----|-----|-----------|-------------|
| `repo_digest` | generate | none | Demonstrative direct-create fixture (#58). File content → `{digest:str, kind:"code"|"doc"|"config"|"test"|"data"}`. Authored live by agent, no operator approval. |
| `atlas_linker` | generate | none | Claude Code Atlas corpus enrichment fan. Doc page → `{tags:[3-7 kebab], atlas_notes:[0-3 domain titles], summary}`. Eight domain titles fixed set. |
| `eval_classify` | generate | none | Throwaway eval role. Text → `{label:"question"|"statement"|"command"}`. |
| `interpret_file` | generate | none | Discovery-system interpret phase. Structural observations → `{notable:[],uncertainties:[],architectural_role}`. NEVER restates raw structural facts. |
| `element_fit_lens` | generate | registration | Panel seat (GC7). Does dossier's CLAIMS fit actual element? `{grounded:bool,reason}`. MOCKUP-EPISTEMICS calibration: static HTML cannot prove dynamic behaviour — judge against KIND and depicted purpose, never dissent for staticness. |
| `voice_lens` | generate | registration | Panel seat (GC7). Does dossier read at operator's altitude? Scoped to `howto.what` + `howto.what_you_can_do` ONLY. DOMAIN VOCABULARY IS NOT JARGON (activity feed, node, diff, inbox etc. are operator language). |

### Mode → Cast mapping (synthesized)
| mode | cast members |
|------|-------------|
| `listening` | focus · recall · ground · connect · check · voice |
| `walkthrough` | focus · recall · ground · connect · check · voice · screen_reader |
| `registration` | register_element · element_fit_lens · voice_lens |
| `verification` | verify_lens |
| `mining` | mine_exchange · judge_mining |
| `spec` | decompose_seed · expand_criterion · ground_criterion |
| `panel` | develop_option |
| `drift` | judge_drift |
| none / explicit | judge · embed · verify_jury · confirm_registration · reduce_synth · score_options · triad_synth · repo_digest · atlas_linker · eval_classify · interpret_file · explain_role · judge_drift |

### GAPS / SURPRISES in roles/

1. **`check` chainer NOT built** — `check.py` declares dependency on `run://<turn>/part-1` + `ground` output; the staged-part chaining executor (G3/G4) that fires it after part-1 emits is flagged downstream but not present. Role declares the contract, enforcement is absent.

2. **`reduce_synth` capability tier mismatch** — declares `requires:["chat","json","reasoning"]` routing to a reasoner (chat-nemotron). The resident 4B provides `[chat,json,tools,fast,no-think]` but NOT reasoning → routes to a different model. This is intentional (extraction-vs-judgment) but Phase 2 wiring is needed.

3. **`judge` DUAL BINDING** — legacy flat top-level fields (`default_model`, `recommended_model`, `env_model`, etc.) coexist with the G2 `model_binding` dict. They mirror each other and can drift. Flagged for G8 unification.

4. **`mine_exchange` follow-on incomplete** — cross-exchange `pattern_tag` embed-cluster reduce needs bge-m3 embedder window; explicitly flagged in code as NOT BUILT. Composition ③ is half-done.

5. **`triad_synth` max_tokens gotcha** — must receive generous `max_tokens` from caller (512 default truncates three full markdown docs → fail-loud JSON parse). This is a caller contract, not self-enforcing.

6. **`confirm_registration` sys.path manipulation** — inserts `~/company/design/_system` at sys.path[0] to import `refcheck.py`. Brittle: path is hardcoded (`os.path.expanduser("~/company")`). Works on Tim's machine but fragile across environments.

7. **`explain_role` is very new (2026-06-21)** — the explain-wire's model leg. The `prompt_slot` + `coordinate` coordinate-resolved framing mechanism is the newest mechanism in the whole roles layer. Wiring from the RHM/projection's explain seam is the upstream dependency.

8. **`element_fit_lens` and `voice_lens`** have no `label` field in their ROLE dict (authored via direct-create; the drift home's agent-authored section has them but not the files themselves). The constitution's auto-reflected section is one-line prose, not the full structured entry.

9. **`eval_classify`** is explicitly a "throwaway eval role" — no label, authored only for test purposes. May be dead weight in production.

10. **`embed` role** — the sole `op:embed` role in the registry. The local-only embedder constraint is a hard rule (no cloud escapes). Its `can_fire` relies on `op=="embed"` path in `runtime/roles.py:102`.

---

## 2. MINDS/ — complete inventory

### Constitution
No separate `minds/AGENTS.md` found — constitution is absent (GAP, see below). Four source files.

### Mind types
A **mind** is a named reference pattern — not a new execution mechanism, but a registry row that binds an identity to an existing role or composition. Three `kind` values observed:

| kind | meaning | example |
|------|---------|---------|
| `role` | binds a mind-name to a specific role | `extractor` → `mine_exchange`; `judge` → `judge_mining` |
| `composition` | a named ordered composition of member-minds | `pair` = extractor → judge |
| `binding` | binds a mode string to a composition | `bind_compose_test`: mode `compose-test` → `pair` |

### Full mind inventory

| id | kind | binds/member | description |
|----|------|-------------|-------------|
| `extractor` | role | `mine_exchange` | Fast fact-extractor leg (the N in N+1). The EXTRACT half of extraction-vs-judgment. |
| `judge` | role | `judge_mining` | The +1 judging leg. Consumes extractor's `run://` output (the JUDGE half). |
| `pair` | composition | [extractor → judge] | The N+1 first unit. Feeds edge: extractor output → judge as `"extract"`, original source as `"raw_exchange"`. The `source_as:"raw_exchange"` threading prevents the flat-fan bug (judge gets the real extract, not the raw utterance). |
| `bind_compose_test` | binding | mode `compose-test` → `pair` | Mode→composition binding as registry DATA, not a suite.py mode-field. |

### GAPS / SURPRISES in minds/

1. **NO AGENTS.md constitution** — the minds/ module has no module constitution. Every other module has one. This is a clear gap; the registry mechanism, schema, and live-set are undocumented in the standard drift-home format.

2. **Only 4 source files** — 3 role-minds + 1 binding. The description says "13 minds" but the actual source file count is 4. The discrepancy suggests either the brief was counting something else, or minds/ is sparse by design (it's newer than the other modules). No pycache evidence of additional minds beyond what's present.

3. **`pair` composition feeds-edge** — the `order` field carries a `feeds` edge with `as:"extract"` and `source_as:"raw_exchange"`. This is the mechanism that prevents the flat-fan bug. `run_composition` must walk the edge. The executor (`run_composition`) is referenced but not in scope of this dragnet area.

4. **`bind_compose_test` mode** — the `compose-test` mode has no corresponding role-cast in the mode-cast map above. It binds to `pair` composition, which is the N+1 unit. This feels like a test/dev fixture, not a production mode.

---

## 3. GENERATION_POLICIES/ — complete inventory

### Constitution (`generation_policies/AGENTS.md`)
- **What it is:** File-discovered GENERATION-POLICY registry (NEWMOD · O2 · P1). Declared per-content generation regime — not static code knobs.
- **Schema:** `GENERATION_POLICY` dict: `id` (MUST equal file stem) · `rep_penalty_ladder` (NON-EMPTY ascending list of floats, required) · `diff_against_source` (bool, required) · `json_schema` (bool, optional) · `temperature` (float, optional) · `budget` (optional) · `desc` (optional).
- **Why it exists:** The degenerate repetition loop pathology (~20% real files, grammar-constrained long arrays at temp0 → freq_penalty is WRONG, rep_penalty LADDER is the cure). Tim-decision lean: rep_penalty can silently under-capture LEGITIMATE enumeration → `diff_against_source` check.
- **Seam:** `runtime/generation_policies.py:GenerationPolicyRegistry` → `policy_for(id)` / `next_rep_penalty()` / `as_records()`. The wiring into `run_role`'s gen-robustness is flagged as a SEPARATE coordinated pass — **ladder-into-run_role MAY NOT BE WIRED YET**.

### Full policy inventory

| id | rep_penalty_ladder | diff_against_source | json_schema | temperature | desc |
|----|------------------|-------------------|------------|------------|------|
| `capture_default` | [1.1, 1.2] | True | True | 0.0 | Corpus-capture regime (enumerative, grammar-constrained, greedy). THE proof-of-concept. |
| `prose_default` | [1.1] | False | False | 0.3 | Free-prose regime (reduce/consult). Single-rung; not the loop surface. |
| `policy.risk-grounding` | [1.1] | False | False | 0.0 | Authorize-subtype explanations. Greedy for security precision. (2026-06-21) |
| `policy.technical-recommendation` | [1.1] | False | False | 0.1 | Cross-lane-subtype explanations. Near-greedy for technical prose. (2026-06-21) |
| `policy.theorem-grounding` | [1.1] | False | False | 0.0 | Theorem-fork-subtype explanations. Greedy — precision on Tim's math. (2026-06-21) |
| `policy.trade-off-neutral` | [1.1] | False | False | 0.2 | Trade-off-subtype explanations. Small warmth for readable neutral prose. (2026-06-21) |

### GAPS / SURPRISES in generation_policies/

1. **Explain-policy batch authored 2026-06-21** — four new policies (`policy.*`) were authored the same day as `explain_role`. They "meet at the contract" (each matches a decision_subtype's `explanation_policy` id). This is the newest batch in the system.

2. **`policy.*` naming convention** — the `id` uses a dot (`.`) separator, unlike the underscore-separated `capture_default`/`prose_default`. This is not a problem (file stem matches id) but is a divergence from the snake_case convention of other registries.

3. **Ladder wiring into run_role** — the constitution flags "the WIRING — incl. `run_role` reading the ladder — is a SEPARATE coordinated pass, NOT built in this lane." The policies exist; whether `run_role` actually uses the `rep_penalty_ladder` is an open question. The acceptance test asserts the registry, not the integration.

4. **`acc_tmp_policy.cpython-314.pyc`** in pycache — indicates a provisional/temp policy file was loaded at some point during a `cpython-314` interpreter run (Python 3.14 alpha). The source file is gone but the compiled artifact remains. Not a gap, but evidence of test activity.

5. **`budget` field declared in schema but unused** — all 6 policies omit `budget`. The schema allows it for future per-policy token-budget control; it is not wired.

---

## 4. LIFTERS/ — complete inventory

### Constitution (`lifters/AGENTS.md`)
- **What it is:** File-discovered LIFTER registry (NEWMOD · P1 · K2). A lifter is a deterministic EXTRACTOR — produces `produced_by:"code"` projections without a model call.
- **Schema:** `LIFTER` dict: `id` (MUST equal file stem) · `extract` (callable `(text, *, meta=None) -> value`) · `produces` (optional) · `desc` (optional).
- **Seam:** `runtime/lifters.py:LifterRegistry` → `for_projection(pid)` (K2 routing) · `as_records()` (cognition_info). A `create_lifter` agent-authoring face is flagged as a seam — **NOT YET BUILT**.

### Full lifter inventory

| id | produces | description |
|----|---------|-------------|
| `frontmatter` | dict | Extracts leading `---`-fenced YAML block. Uses PyYAML if available, falls back to minimal line parser (fail-soft to {}). Deterministic. |
| `links` | list[str] | Extracts outbound links (`[[wikilinks]]` + `[md](targets)`). Deduplicated, order-preserving. Deterministic. |
| `blocks` | list[dict] | Extracts heading-block structure (`{level, heading}` per `#`-heading). Deterministic. |

### GAPS / SURPRISES in lifters/

1. **Only 3 lifters** — the constitution covers the baseline structural extractions. No semantic lifters. The `acc_tmp_lift.cpython-314.pyc` suggests a provisional lifter was tested but not committed.

2. **`create_lifter` is a seam** — executable-code lifter authoring is gated (like node-types). The flag in the constitution is explicit: the `_build_lifter` gate + `Suite.create_lifter` method are NOT built.

3. **`frontmatter` uses PyYAML gracefully** — fail-soft to a minimal line-parser if `yaml` not importable. This is a dependency softness: structural fidelity depends on whether `pyyaml` is installed.

4. **No `produces` field set** — all three lifters omit the `produces` field (it is optional per schema). The `for_projection(pid)` routing therefore relies purely on `id` matching a projection's `produced_by:"code"` signal.

---

## 5. AI_TICS/ — complete inventory

### Constitution (`ai_tics/AGENTS.md`)
- **What it is:** File-discovered AI-TIC registry (NEWMOD · M4 · P1). An AI-tic is a catalogued generic-AI fingerprint (a machine-generated tell). The fingerprint pass (M4) matches coined-vocab projections against this registry → `ai-fingerprint` marks (direction: `subtract` — denoising = surfacing, the inversion).
- **Schema:** `AI_TIC` dict: `id` (MUST equal file stem) · `markers` (NON-EMPTY list of strings, required) · `label` (optional) · `desc` (optional).
- **Seam:** `runtime/ai_tics.py:AiTicRegistry` → `all_markers()` (flat cue set) · `as_records()` (cognition_info + fingerprint pass). A `create_ai_tic` agent-authoring face is flagged as a seam — **NOT YET BUILT**. The fingerprint mark-pass wiring is also flagged as a SEPARATE coordinated pass.

### Full AI-tic inventory

| id | label | markers | desc |
|----|-------|---------|------|
| `framework_imposition` | framework-imposition | "best practice", "industry standard", "framework", "design pattern", "according to the standard" | Imposing generic framework/terminology over native shape (Tim rejects standard frameworks) |
| `versioning` | versioning | "v2", "v3", "round 2", "round-2", "-final", "_final", "version 2", "(copy)", "revised" | v2/round-N/dated copies instead of canonical in-place (named Tim frustration: no-versioning) |
| `false_finality` | false-finality | "it's fixed", "all done", "fully working", "complete and ready", "production-ready", "now works perfectly" | Declaring done/fixed/complete without proof (named Tim frustration: verify-before-claiming) |
| `silent_fallback` | silent-fallback | "falls back to", "as a fallback", "if that fails, use", "just use a different", "silently", "best-effort" | Routing around a problem / swallowing an error (named Tim frustration: no-silent-failures, make-each-thing-work) |
| `agent_arch` | agent-arch | "the agent decides", "autonomous agent", "agent loop", "tool-calling agent", "the agent will then", "agentic workflow" | Defaulting to agent-architecture where the work is content/dataflow (named Tim distinction: not-agent-architecture-by-default) |
| `closure_form` | closure-form | "in conclusion", "to summarize", "in summary", "to wrap up", "final thoughts", "that's everything" | Closure-form writing (summarized/finished, expansion-ratio<1) that kills institutional memory (named Tim frustration: open-future-writing) |
| `mvp` | MVP | "MVP", "minimum viable", "for now we can", "prioritize by impact", "phase 1 only", "good enough for now", "nice to have" | MVP/impact-prioritization/scope-cutting (named Tim frustration: no-MVP, all-or-nothing) |

### GAPS / SURPRISES in ai_tics/

1. **Fingerprint pass (M4) is NOT wired** — the constitution explicitly flags: "the WIRING — incl. the fingerprint mark-pass reading the catalogue — is a SEPARATE coordinated pass, NOT built in this lane." The tics exist as a catalogue; the pass that detects them in live content and appends `ai-fingerprint` marks is not built.

2. **`create_ai_tic` is a seam** — no agent-facing authoring path. New tics require a new file.

3. **7 tics all seed from Tim's NAMED frustrations** — the catalogue is explicitly personal (Tim's CLAUDE.md rules materialized as subtract-direction marks). This is by design but the set is small (7 entries).

4. **`acc_tmp_tic.cpython-314.pyc`** — same pattern as generation_policies: provisional tic tested under Python 3.14 alpha, source gone. Not a gap.

5. **Markers are exact-string** — the fingerprint pass matches on exact marker strings in content. No fuzzy/semantic matching at the tic level. This is intentional (deterministic, not model-dependent) but means minor phrasing variations escape detection.

---

## 6. Cross-cutting observations

### Architecture patterns (consistent across all 5 modules)
- **File-discovered registry** — every module uses the same self-registering `<module>/<id>.py` pattern. `id` MUST equal file stem. Drop a file = add a registry entry; remove = un-registers on `rediscover`. Five independent registries all following the same shape.
- **`AGENTS.md` as drift home** — every module (except `minds/` — GAP) has a constitution that is the authoritative list. Acceptance tests (`tests/<module>_acceptance.py`) assert the file matches the discovered set.
- **No model inside a rule (L2)** — all verdict/route/inject rules are declared as pure data-ASTs or callable functions over already-resolved outputs. The model runs only inside a role's draw.
- **Floor invariant (C9.2)** — `roles/*`, `ai_tics/*`, `lifters/*`, `generation_policies/*` are in the COG_SOURCES scan that enforces the floor: no `resolve`/`approve`/`dispatch` tokens. Roles emit no `claude -p`.
- **No confidence floats (G16)** — the "no-confidence law" is consistently applied. `register_element` migrated from `confidence:float` (empirically flat at 0.85) to a discrete `grounding` tag. `verify_lens` uses `"pass"|"fail"|"uncertain"`. `judge_drift` uses a closed three-way verdict. `score_options` uses ordinal `rank:int` not a 0..1 score. `judge_mining` uses `grounded:bool` + named `unsupported`.

### Seam inventory (what is declared but not yet built / wired)
| seam | location | status |
|------|---------|--------|
| `check` chaining executor (G3/G4) | `roles/check.py` | NOT BUILT — staged-part chainer deferred |
| `run_role` rep_penalty ladder wiring | `generation_policies/AGENTS.md` | SEPARATE PASS — policies exist, wiring status unclear |
| Fingerprint mark-pass (M4) | `ai_tics/AGENTS.md` | NOT BUILT — catalogue exists, pass deferred |
| `mine_exchange` pattern_tag embed-cluster | `roles/mine_exchange.py` | NOT BUILT — needs bge-m3 embedder window |
| `create_lifter` agent-authoring face | `lifters/AGENTS.md` | SEAM — flagged, not built |
| `create_ai_tic` agent-authoring face | `ai_tics/AGENTS.md` | SEAM — flagged, not built |
| `create_generation_policy` agent-authoring | `generation_policies/AGENTS.md` | SEAM — flagged, not built |
| `minds/` module constitution | `minds/` (absent) | GAP — no AGENTS.md |
| `judge` dual-binding unification (G8) | `roles/judge.py` | FLAGGED for G8 — legacy flat fields + model_binding both present |
| Verdict-tally reduce-rule for `verify_lens` | `mcp_face._REDUCE_RULES` | next-beat follow-on — `verify_lens` usable now but tally not wired |
| `explain_role` wiring from RHM/projection | projection's explain seam | open seam — the explain-wire's call-site is upstream dep |

### Coordinate system (roles that use `coordinate=` / `prompt_slot`)
Only `explain_role` uses the `prompt_slot` + `coordinate={subtype}` mechanism. This is the newest mechanism in the layer (2026-06-21). It resolves the prompt WHOLESALE at run-time based on the decision subtype — no `{}` placeholders, the system prompt is replaced entirely. This pattern is novel; no other role uses it yet.

### Capability tiers (model_binding declared)
Three distinct tiers observed across `model_binding.requires`:
- `["chat","json"]` — the standard swarm (4B resident), used by most roles
- `["chat","json","fast"]` — fast extract/select (focus — the no-think 4B hot path)
- `["chat","fast","no-think"]` — the judge's voice-circuit hot path
- `["chat","json","reasoning"]` — the reduce_synth synthesizer (needs a reasoner, not the 4B)
- `["embed"]` — the embed role (local embedder only)

Phase 2 wiring (`resolve_model` routing on these capabilities into the actual firing path) is declared but not yet live — currently falls through to `RESIDENT_MODEL` kwarg.

---

## 7. File counts vs brief numbers

| area | brief says | actual source files |
|------|-----------|-------------------|
| roles/ | 97 | 30 .py files (inc. 6 agent-authored) |
| minds/ | 13 | 4 .py files |
| generation_policies/ | 16 | 6 .py files |
| lifters/ | 11 | 3 .py files |
| ai_tics/ | 23 | 7 .py files |

The brief numbers (97/13/16/11/23) count all files including `__pycache__/*.pyc` compiled artifacts. The meaningful source-file counts are much smaller. The compiled artifacts include `cpython-312` and `cpython-314` variants (two Python versions have exercised this code).
