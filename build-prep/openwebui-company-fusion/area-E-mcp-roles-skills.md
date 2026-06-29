---
type: map
register: descriptive
module: mcp_face, roles, skills
aliases: ["Area E — MCP Face + Roles + Skills"]
tags: [company, inventory, mcp-tools, roles-registry, skills-registry, agent-surface]
coverage: {files_read: 68, files_total: 68, last_read: "2026-06-28"}
relates-to: ["[[Company Map]]", "[[mcp_face — constitution]]", "[[roles — constitution]]", "[[skills — constitution]]"]
status: living
---

# Area E: MCP Face + Roles + Skills — COMPLETE INVENTORY

## STRUCTURE
Three interconnected registries forming the company's agent-facing API surface and internal cognition architecture:

1. **mcp_face/tools/** — 28 consolidated MCP tools (agent-facing); file-discovered via pkgutil
2. **roles/** — 34 role declarations; file-discovered via runtime/roles.py::RoleRegistry
3. **skills/** — 6 skill instructions; file-discovered via runtime/skills.py::SkillRegistry

---

## MCP TOOLS (28 total; mcp_face/tools/*.py)

### Core Cognition & Execution
- **corpus** (mcp_face/tools/corpus.py:22) — Ask the corpus; read the repo-exocortex records (query/list/find/read/neighbours/determine); semantic retrieve + dragnet extraction layer read; detail+limit params for token efficiency
- **create** (mcp_face/tools/create.py:~30) — Consolidated declarative-authoring (kinds: role, skill, context, projection, mark_type, generation_policy, relation_type, guide, ai_tic); direct-apply floor (no resolve/approve/dispatch); reflects in drift-home on success
- **runs** (mcp_face/tools/runs.py:~25) — Run INDEX (list/find); read the `op.run` event log; RUN addresses keyed by operation class; read-only
- **flows** (mcp_face/tools/flows.py:15) — Proven production-line chains (list/describe/run/propose); grounded multi-step compositions; proposes-only architecture; repo-authored, never launched in claude -p
- **rule** (mcp_face/tools/rule.py:~30) — Routing rules on roles (validate/dry_run/attach/detach); deterministic condition AST; surface proposals for operator, never self-apply
- **node** (mcp_face/tools/node.py:27) — Graph-node operations (create/delete/propose/apply); graph instances + node-type library; apply gated by operator approval; no self-approval privilege

### Session Fabric & Coordination
- **sessions** (mcp_face/tools/sessions.py:~60) — Session fabric agent face (op: list/inbox/watch/describe/search/timeline); READ only; session_post separate tool for WRITE (mailbox append); no spawn/resume/dispatch verbs here
- **channels** (mcp_face/tools/channels.py:35) — Cross-session fabric structure (op: list/describe/history/edges); channel_act separate for WRITE (create/gather/add/remove/status/post/mode/promote/disperse/archive); supervision-layer distinct
- **session_recall** (mcp_face/tools/session_recall.py) — Semantic recall + lenses over a session; first-class MCP; session history as queryable semantic space

### Channel/Company Collaboration Surface
- **cc_attachments** (mcp_face/tools/cc_attachments.py:25) — Bind targets to channels (op: attach/detach/list/manifest/types); registry of binding kinds (attachment_types/); bindings are file-discovered rows; manifest projects grouped bindings
- **cc_board** (mcp_face/tools/cc_board.py) — Noticeboard / board; agent-facing surface over runtime/cc_board.py
- **cc_channel** (mcp_face/tools/cc_channel.py) — Cross-session messaging into LIVE Claude Code sessions
- **cc_images** (mcp_face/tools/cc_images.py) — Image embedding + retrieval through the MCP; visual corpus face
- **cc_voice** (mcp_face/tools/cc_voice.py) — Give text VOICE; fabric's wire to TTS engine
- **cc_gate** (mcp_face/tools/cc_gate.py) — Per-step GATE / ABORT / REWIND; session control surface
- **cc_clone** (mcp_face/tools/cc_clone.py) — Point-in-time CLONE to fabric; snapshot sessions
- **cc_retire** (mcp_face/tools/cc_retire.py) — Retirement verb (member/channel retire); cleanup surface

### Data & State Access
- **introspection** (mcp_face/tools/introspection.py:48) — Capability registry tool (op: list/get/search/describe/snapshot); mirrors CapabilityRegistry singleton; read-only health view; fail-loud on unknown caps
- **marks** (mcp_face/tools/marks.py) — Marks READ (consolidated; op: by='target'|'type'|'findings'); read the marks store (claim/span targets) or legacy findings store; registry-gated by type
- **context** (mcp_face/tools/context.py) — Live context-window read + compact; manage session memory footprint
- **operator** (mcp_face/tools/operator.py) — Operator-memory tool; brain's persistent knowledge of Tim's preferences

### Decision Surface & Workflow
- **decisions** (mcp_face/tools/decisions.py) — DECISIONS-WAITING verb; operator's canonical waiting items; brain-facing source
- **verdict_panels** (mcp_face/tools/verdict_panels.py) — VERDICT-PANEL tool (GC7 on the face); multi-lens judgment surfaces
- **point** (mcp_face/tools/point.py) — RHM's POINT verb; emit door onto surface spotlight; brain to UI surface
- **dials** (mcp_face/tools/dials.py) — DIALS tool (Track-1 on face); configuration/tuning surface
- **routines** (mcp_face/tools/routines.py) — ROUTINES tool (Session Fabric S-R9.1); in-Company /fire arm (schedule/invoke recurring tasks)

### Graph & Workflow Data
- **instrument** (mcp_face/tools/instrument.py) — THE INSTRUMENT'S tool face; MCP door onto radial projection (graph instrumentation)
- **ingest** (mcp_face/tools/ingest.py) — INGEST tool; repo-exocortex first-class; capture source content into corpus
- **point** (mcp_face/tools/point.py) — RHM's POINT verb; emit onto surface spotlight

### KEY CHARACTERISTICS
- **ONE tool, one resource, ONE `op` selector** (MCP-DESIGN-PRINCIPLE); never flat tools
- **File-discovered** via pkgutil in mcp_face/server.py (add a file → auto-register, no server.py edit)
- **Export `OPS` constant** (CONTRACT-FORMAT §9.2); drift tests verify dispatcher matches OPS
- **Floor = NO resolve/approve/dispatch/claude -p verbs** (keeper rule across all tools)
- **CQRS: READ & WRITE split** (e.g., sessions/session_post; channels/channel_act; marks/mark)
- **Annotations** (readonly/destructive/idempotent hints via contracts.ToolAnnotations; remote.py:_tool_posture reads posture="safe" for non-operator tiers)

---

## ROLES (34 total; roles/*.py)

### Core Cognition Roles
- **`judge`** — (judge.py) Finished-thought judge; role #0; fires via is_finished_thought, NOT the swarm; no prompt_template/mode_scope/draws; config-only
- **`voice`** — (voice.py) Tone: persona+answer → toned phrasing; listening cast; cognition role, not TTS module
- **`recall`** — (recall.py) Memory: utterance (+memory) → past-context snippet + relevance flag; listening cast
- **`ground`** — (ground.py) Citable facts: live state → scope check + grounding note; listening cast; gates recall's inject
- **`connect`** — (connect.py) Link: topic+thread → related thread/decision worth surfacing; listening cast
- **`check`** — (check.py) Contradiction: forming answer vs ground → does it contradict?; listening cast; chains after parts start
- **`focus`** — (focus.py) Selector: utterance → intent + which auxiliary roles to fire; listening cast; gates cast
- **`screen_reader`** — (screen_reader.py) At-altitude screen-comprehension; reads MOCKUP UNDER REVIEW → plain-language "what is this + what can you do"; walkthrough-cast only; cognition role

### Composition & Analysis Roles
- **`develop_option`** — (develop_option.py:~60) Option-panel MAP role; one approach through one biasing lens (mvp-first / risk-first / reuse-first / framework-first / radical-recompose) → {lens, approach, buys, costs, touches, risk}; panel cast
- **`score_options`** — (score_options.py:~50) Option-panel REDUCE role; N per-lens approaches → {scored:[{lens,rank,why}], recommendation, grafts}; ranks ordinal (1=strongest), no fake-precision float; mirrors reduce_synth
- **`mine_exchange`** — (mine_exchange.py:~50) Transcript-miner MAP role; ONE conversation exchange → extract {decision, rationale, tim_correction, my_error, bug_fix, needs_tim, frustration, pattern_tag}; mining cast; fanned via run_items
- **`judge_mining`** — (judge_mining.py:~40) Transcript-miner CONFIRM role; validates mine_exchange extract → {grounded:bool, unsupported:str}; no confidence float (G16 law); mining cast
- **`judge_drift`** — (judge_drift.py:~60) Drift-radar CONFIRM role; cluster of semantically-near repo files → {verdict, shared, the_source, note} (built-twice / overlap vs distinct); single-generate; drift cast; no confidence float

### Specification & Compilation Roles
- **`decompose_seed`** — (decompose_seed.py:~50) Spec-compiler's seed→groups role; dense seed → {groups:[{group_id, what, systems_touched}]}; spec cast; loop-prep
- **`expand_criterion`** — (expand_criterion.py:~60) Spec-compiler's group→criterion MAP; one group → {id, function, form, files_touched, reuse_or_netnew, preserves} (TWO-FACED); spec cast
- **`ground_criterion`** — (ground_criterion.py:~50) Spec-compiler's no-fiction reuse-check; one criterion → {criterion_id, grounded: reuse|net-new, cite, note}; spec cast; degrades without corpus
- **`triad_synth`** — (triad_synth.py:~70) Spec-compiler's REDUCE role (mode=role); N grounded criteria → {completion_criteria, implementation_guide, research_synthesis}; draft only (operator-only apply); spec cast

### Registration & Verification Roles
- **`register_element`** — (register_element.py:~90) Registry-Generation chain's MAP role (RG3); ONE mockup element + context → PROPOSED registry dossier {address, represents, howto, capabilities, maps_to_feature, grounding}; grounding ∈ {built|proposed|uncertain|defer}; mode_scope:{registration}; NO-FICTION law (capabilities ⊆ closed vocab, maps_to_feature real id VERBATIM or "proposed"); proposes, never writes
- **`confirm_registration`** — (confirm_registration.py:~90) Registry-Generation chain's CONFIRM gate Layer 2; jury (draws:3, quorum_grounded verdict_rule); each draw → {grounded:bool}; AND with deterministic Layer-1 refcheck; in no cast; fired via run_jury; E4 caveat: single-model correlation (variance not independent error)
- **`verify_jury`** — (verify_jury.py:~70) Canonical jury (C2.4); draws:3 + pure majority-vote verdict_rule; in no cast; fired explicitly via run_jury; E4 caveat: N draws on ONE model = correlated (variance not independent error)
- **`verify_lens`** — (verify_lens.py:~80) Verification jury's LENS role (COMPOSITIONS ⑥); judges ONE change through ONE lens (correctness · floor · drift · matches-criterion · registry-is-truth · adversarial-disprove) → {lens, verdict: pass|fail|uncertain, evidence, breaking_case}; verification cast; NOT draws-jury (cross-LENS fan, one draw each); adversarial-disprove defaults fail/uncertain if breaking case found
- **`element_fit_lens`** — (element_fit_lens.py) Panel seat (GC7); judges whether registry dossier CLAIMS fit actual element — capabilities/feature match element's snippet; agent-authored
- **`voice_lens`** — (voice_lens.py) Panel seat (GC7); judges whether registry dossier reads at OPERATOR'S altitude — plain language, no HTML/code-speak, voice of existing entries; agent-authored

### Decision & Refinement Roles
- **`explain_role`** — (explain_role.py:~80) Decision EXPLAIN role (explain-wire's model leg, 2026-06-21); when Tim opens decision card → generates operator-facing explanation; composes recollection's grounding block+caveat + fork's explanation_policy_for(decision) + OWN prompt_slot (§5 per-subtype FRAMING, resolved by coordinate={subtype}); theorem-fork framing = NEVER-ASSERT law; op:generate; fired by projection's RHM at explain seam
- **`refine_decision`** — (refine_decision.py:~80) Decision REFINE role (L5 propose-side, 2026-06-22); given decision card's current content (card input) → RHM DECIDES whether sharper MEANING would help, PROPOSES if so; per card-refine-posture (authorize→tim); propose verb writes INERT decision_update mark (by=rhm) awaiting Tim's accept; content-only (never structural routing fields); DETERMINE role (thinking:True); kimi-bound (ollama-served, honoured); op:generate
- **`guide_author`** — (guide_author.py:~70) Guide-author's brain role (narrative-guide face, 2026-06-28); composes how-to guide for target, grounded ONLY in supplied sources; op:generate; model via registry (default_model None → cfg brain); in no mode_scope (fired explicitly); used by runtime/guide_author.py:model_composer

### Synthesis Roles
- **`reduce_synth`** — (reduce_synth.py:~60) Demonstrative reduce-role (C 2/4); reduce-tree THOUGHT_SHAPE's declared join role; N map-output notes → ONE merged {summary}; op:generate; in no cast (fired explicitly via run_reduce mode="role"); mirrors verdict-tally structure

### Extraction & Dragnet Roles
- **`dragnet_coarse`** — (dragnet_coarse.py) Dragnet family (unify-exercise 2026-06-26); stage-1 neutral coarse pass → {about, kind, touches}; output_schema FROZEN contracts.dragnet_schema.Coarse; carries non-authorable NEUTRAL_FRAGMENT; op:generate; PROTECTED (edit/delete refuse); guarded by dragnet-freeze block in roles_acceptance.py
- **`dragnet_fine`** — (dragnet_fine.py) Dragnet stage-2 fine deepening → {summary, entities, claims, relations, open_questions}; output_schema FROZEN; op:generate; PROTECTED
- **`dragnet_design`** — (dragnet_design.py) Dragnet visual-dna-only design-binding pass → {resolves_into, resolution}; output_schema FROZEN; op:generate; PROTECTED

### Direct-Create & Fixture Roles
- **`repo_digest`** — (repo_digest.py:~50) Demonstrative DIRECT-CREATE fixture (#58); authored LIVE by agent via create_role; supplied file → {digest, kind} (1-sentence digest of what file is + role in system); op:generate; in no cast (fired explicitly via run_role/run_items); self-apply with NO surfaced item
- **`embed`** — (embed.py) Embed operation role; op:embed (not generate); fires vector path (no prompt/schema needed); complete_embeddings, local embedder only

### Discovery & Interpretation Roles
- **`interpret_file`** — (interpret_file.py) Agent-authored role; discovery-system interpret phase; file's programmatically-extracted structural observations → interpretive observation
- **`atlas_linker`** — (atlas_linker.py) Agent-authored role; tags Claude Code documentation page + connects to Atlas domain notes; corpus enrichment fan (run_items)
- **`eval_classify`** — (eval_classify.py) Agent-authored role; labels short text as exactly one of {question|statement|command}; throwaway eval role

### KEY ROLE CHARACTERISTICS
- **File-discovered** via runtime/roles.py::RoleRegistry (add file roles/<id>.py → auto-registers, no registry edit)
- **Self-contained ROLE dict** at module level; id MUST equal file stem
- **Optional fields determine facet**: prompt_template+output_schema ⇒ generate role (can fire); op:embed ⇒ embed role; mode_scope ⇒ in cast; draws+verdict_rule ⇒ jury
- **BINDING TRAP** (2026-06-22): default_model lives TOP-LEVEL, NOT inside model_binding (silently unread if nested → falls to DEFAULT_BRAIN = -pro; caught by-use, verify resolve_role(id)['model'])
- **Resolved slots** (prompt_slot · schema_slot · thinking): resolve against turn coordinate (grain · viewer · mode · subtype · register); compute per-coordinate, not static
- **Casting** (mode_scope): listening cast = {focus, recall, ground, connect, check, voice} (first locked cast C2.3); walkthrough = above 6 PLUS screen_reader (guided-review enrichment); panel/spec/verification/registration/mining/drift = cast-beyond-listening contexts; no mode_scope = not in any cast (fired explicitly)
- **Juries** (draws + verdict_rule): verify_jury (3 draws, majority-vote); confirm_registration (3 draws, quorum_grounded); E4 caveat: N draws on ONE model = variance not independent error
- **Floor = NO automatic application** (operator-approval gated on propose roles); models run ONLY inside roles (L2 — fabric guards)

---

## SKILLS (6 total; skills/*.py)

### Core Instruction Skills
- **`summarize`** (summarize.py) — Seed skill; reusable instructions to faithfully condense supplied content (keep load-bearing detail + relationships, add nothing, no preamble); demonstrative first member; skill://summarize resolves to actual instructions a role reads as input
- **`extract_decisions`** — (extract_decisions.py) Demonstrative DIRECT-CREATE skill (#56 write-half · #58); authored LIVE by agent via create_skill; reusable instructions to list every DECISION in document (one per line: `<decision> - <rationale>`); skill://extract_decisions resolves; readable via list_skills_contexts; proof skill write-half is agent's: written + git-committed [self-apply] + live with NO surfaced item

### Composition Recipe Skills (AK3 — Cognition Engine Workflows)
- **`corpus_pipeline`** (corpus_pipeline.py) — 3-layer corpus pipeline recipe: capture (describe over N units → corpus records) → run_items (extract) → run_items (project) → engine/bridge capture+embed pass → run_reduce (cluster THEN synthesize) → findings_for; order + output→input wiring; flags two gaps: NO standalone embed MCP tool (LAYER-2 embed is engine pass), NO write-mark tool
- **`patterned_visibility`** (patterned_visibility.py) — Patterned-visibility loop recipe: run → look/compare (list_corpus · find_corpus · find_relations · findings_for · read_corpus_record · find_runs) → mark the pattern (create_projection, since no write-mark tool) → reveals next step → repeat; discovery is loop, not pre-scripted list
- **`inversion_query`** (inversion_query.py) — Inversion-query recipe: find_relations(item, near_space, far_space) returns near∩¬far cross-space set difference; when/how to use; includes inversion read to find MISSING; space ids from cognition_info().spaces; fails loud without persisted vector for item in both spaces
- **`map_reduce_composition`** (map_reduce_composition.py) — Map-vs-reduce composition recipe: when to run_items (1 role × N units, MAP) vs run_reduce (cross-unit JOIN: role|rule|cluster); how to chain them (MAP's addresses output feeds REDUCE's addresses input — load-bearing seam)

### KEY SKILL CHARACTERISTICS
- **File-discovered** via runtime/skills.py::SkillRegistry (add file skills/<id>.py → auto-registers)
- **Self-contained SKILL dict** at module level; id MUST equal file stem; required: id + content; optional: label, description
- **Addressable as skill://<id>** (C 3b address scheme); resolves via runtime/cognition.py::resolve_address
- **Content field** = resolvable value (instructions text a role reads); unknown id RAISES fail-loud (registry-is-truth, never fabricate)
- **Composition skills** = multi-step cognition workflow recipes (order + wiring); NOT executable code (role *can* read one as input, but primary use is as reader's composition playbook)
- **Floor** = declarative content describing how to compose READ / RUN / declarative-create tools; none instructs resolve/approve/dispatch or launches claude -p

---

## NOTABLE / SURPRISING

### Design Patterns & Laws
1. **MCP-DESIGN-PRINCIPLE** (core): ONE consolidated tool per resource with `op` selector; never flat tools; file-discovered via pkgutil (add file → auto-register, no server.py edit) — mirrors roles + skills discovery
2. **Registry-is-truth**: roles, skills, node-types, capabilities live as file-discovered rows; rediscovered per call; a new committed file appears without restart; no second source
3. **CQRS applied rigorously**: READ and WRITE tools split (sessions/session_post; channels/channel_act; marks + separate write tool; deliberate honoring of audit distinction)
4. **MCP-DESIGN-PRINCIPLE tradeoff**: god-tool forbidden (fold related reads only if keyed by SAME resource; separate keying → separate tools); runs deliberately NOT folded with get_state/get_results (different keys: run:// vs graph_id)
5. **Floor (recurring law, across tools)**: NO resolve/approve/dispatch/claude -p verbs (operator verbs gated separately); models run ONLY inside roles (L2, fabric guards); surfaces are proposals, never auto-applied on cold agents

### Binding & Model Resolution
6. **DEFAULT_MODEL binding trap** (2026-06-22, found live): default_model lives TOP-LEVEL on ROLE dict, NOT nested inside model_binding; nested bindings silently unread → fall to DEFAULT_BRAIN (-pro, TIM-RULE anti-pattern); explain_role + refine_decision both had this; verify by-use (resolve_role(id)['model']), not by reading file
7. **Resolved slots** (prompt_slot · schema_slot · thinking): compute per coordinate (grain · viewer · mode · subtype · register) at run-time, not static; thinking=None is NOT False (only explicit declaration routes think-control); unslotted roles are byte-identical to slot-free roles

### Casting & Mode Architecture
8. **Mode-driven role casting**: listening (6 members: focus, recall, ground, connect, check, voice) is FIRST locked cast (C2.3, DECISIONS Batch 3 Q1); walkthrough = listening 6 PLUS screen_reader (enrichment swarm fires during guided review); panel/spec/verification/registration/mining/drift = cast-beyond-listening contexts; no mode_scope = not in any cast (fired explicitly, not swarm-driven)
9. **Jury design caveat (E4)**: N draws on ONE model = variance, not independent error (model's systematic bias replicated N times); correctness-jury needing model diversity accepts future tiebreak via models_for_role (C2.5); current single-model limit documented

### No-Fiction Law (Deterministic Floor)
10. **register_element / confirm_registration**: TWO-LAYER no-fiction guarantee: Layer 1 = deterministic refcheck (design/_system/refcheck.py::check_dossier, model-independent, catches fabricated capability/feature/code refs); Layer 2 = soft accuracy jury (model-dependent); grounding field ∈ {built|proposed|uncertain|defer} (NO confidence float — G16 law); maps_to_feature must be REAL id COPIED VERBATIM or literal "proposed"; model coins INB-* ids by analogy — verbatim instruction + deterministic floor catch it
11. **Dragnet frozen output_schema & neutral fragment**: dragnet_coarse/fine/design output_schema FROZEN to contracts.dragnet_schema.{Coarse,Fine,Design} (D1 one-superset, imported never authored); coarse prompt carries non-authorable NEUTRAL_FRAGMENT verbatim (D3, neutral pass ≠ relevant pass); _build_role dragnet-family field-freeze door enforces both; PROTECTED (edit/delete refuse); rejects non-frozen schema, forbids schema_slot (grain is role-identity, requires neutral fragment)

### Unexpected Consolidations & Moves
12. **create (consolidated 8→1)**: replaces flat create_role / create_skill / create_context / create_projection / create_mark_type / create_generation_policy / create_relation_type / create_ai_tic; direct-apply floor (no resolve/approve/dispatch); reflects in drift-home (M4 self-teaching) on success
13. **corpus (consolidated read surface, query exposed)**: replaces flat list_corpus / find_corpus / read_corpus_record AND EXPOSES previously-unexposed query (ask-the-codebase semantic retrieve, G20); determine op reads dragnet extraction layer; detail+limit params for token efficiency; rerank (jina-v3 cross-encoder) opt-in with rerank_score + orig_rank + reranked order
14. **marks (split: READ/WRITE)**: consolidates three flat READS (marks_for / marks_by_type / findings_for) into ONE marks(by='target'|'type'|'findings'); write stays separate (mark tool, CQRS); by='type' carries registry GATE (fail-loud on typo'd mark_type, registry-is-truth)
15. **rule (expose detach, constrain attach)**: consolidates validate_rule / dry_run_rule / attach_rule AND EXPOSES previously direct-only detach (symmetric remove); validate/dry_run pure reads; attach/detach surface role_build proposals (operator-only floor)

### Corpus & Vector Architecture
16. **Corpus is engine's exocortex**: digests of sources stored (not raw files); every ingest pass + capture output → addressed records (run://, code://, extraction://); dragnet layer (extraction:// asset) = full-coverage claim extraction (source-traced, no-fiction by construction); determine op clusters REAL claims BY INDEX (theme-labels only, NEVER generates claim text); every claim carries FULL provenance (chunk_id + rel_path + anchor + rerank_score)
17. **Embedding spaces are scoped**: corpus(op=query, space='repo') = ask-codebase; spaces scoped to embeddable lenses; find_relations(item, near_space, far_space) = cross-space set difference (inversion-query recipe); cognition_info().spaces names available spaces; fails loud on unknown space or missing vector

### Agent-Authored Entries (Self-Apply)
18. **Direct-create roles/skills bypass operator approval**: repo_digest (create_role) + extract_decisions (create_skill) self-apply [self-apply] git-commit, live in cognition_info with NO surfaced item; proof that authoring is agent's (not operator-guarded); both are demonstrative fixtures of the write-half
19. **Agent-authored roles live in drift-home** (roles/AGENTS.md): interpret_file · atlas_linker · eval_classify · element_fit_lens · voice_lens; auto-reflected entries (/* created live by create face; one line per entry — keeps acceptance green; refine prose by integration */)

### Session & Coordination Fabric
20. **Session Fabric FLOOR law**: sessions/session_post + channels/channel_act ONLY append mail/events to store, never spawn/resume/dispatch; supervisor service alone acts on deliver/wake/consult intents; channel_post can NEVER wake/spawn (organ's routing law); verbs are ROUTING DECISIONS, not mechanisms (live registry state → path: supervised-live→deliver · closed→wake · otherwise→queue)
21. **Annotations (honest instance F10.1)**: sessions/channels first wired contracts.ToolAnnotations (readonly/destructive/idempotent) → SDK's ToolAnnotations hints; posture="safe" (remote.py:_tool_posture) exposes READ tools to authenticated non-operator tier; WRITE tools untagged (fail-closed, operator-only)

### Cast & Mode Boundaries
22. **Walkthrough cast enrichment**: listening's 6 roles (focus, recall, ground, connect, check, voice) ALSO declare mode_scope ⊇ {walkthrough}; enrichment swarm fires during guided review walk (same cast members, new context); screen_reader walkthrough-cast-only (not listening)
23. **Verification cast (COMPOSITIONS ⑥)**: verify_lens LENS role (6 lenses: correctness · floor · drift · matches-criterion · registry-is-truth · adversarial-disprove); NOT draws-jury (cross-lens fan, one draw each via run_items); adversarial-disprove lens defaults fail/uncertain if breaking case found; green-iff-all-pass deterministic tally via verdict-tally run_reduce(mode='rule')
24. **Panel cast (COMPOSITIONS ⑩)**: develop_option (MAP, 5 lenses) + score_options (REDUCE, mode=role); fanned over lenses; ranks ordinal (1=strongest), no fake-precision float (G16 law); may graft runner-up strengths into recommendation

### Specification Compiler Workflow
25. **Spec compiler pipeline**: decompose_seed (seed→groups) → expand_criterion (group→TWO-FACED criterion: function + form) → ground_criterion (no-fiction reuse-check, cite real file:symbol or degraded-graceful) → triad_synth (REDUCE, mode=role: N criteria → {completion_criteria, implementation_guide, research_synthesis}); loop-prep triple; triad is DRAFT only (operator-only apply)

### Reduced Clarity & Ambiguity Points
26. **Composition skills are NOT code**: corpus_pipeline, patterned_visibility, inversion_query, map_reduce_composition are declarative recipes (order + wiring); NOT executable; primary use = reader's composition playbook; roles CAN read them as input (via skill:// addressing), but that's secondary
27. **Retrieve + Rerank two-layer**: corpus(op=query) single-layer-pplx (default, fast); opt-in rerank (jina-v3 cross-encoder, :8008 served) re-orders by deeper relevance; MULTI-LAYER-CONSULT.md endorsed base before cross-layer fusion; FAIL-LOUD if hit's CAS digest text unresolvable (never blank-text rerank)
28. **Capability registry seam (lane-cap-wire)**: introspection tool reaches CapabilityRegistry via module-level singleton (introspection.registry.capability_registry()) or suite attribute (degraded fallback); RAISES TEACHING-loud if neither (not AttributeError), naming missing lane; fixture logic stub-populated; live binary discovery queued for lead-verify

---

## SUMMARY TABLE

| Category | Count | Pattern | Discovery | Floor |
|----------|-------|---------|-----------|-------|
| **MCP Tools** | 28 | ONE resource + `op` selector | pkgutil (mcp_face/server.py) | NO resolve/approve/dispatch/claude -p |
| **Roles** | 34 | File-discovered rows (roles/*.py) | RoleRegistry.discover | Models run ONLY inside roles; operator-gated apply |
| **Skills** | 6 | File-discovered rows (skills/*.py) | SkillRegistry.discover | Declarative instructions; address scheme skill:// |
| **Composition Skills** | 4 | Multi-step workflow recipes | skills/*.py (5 of 6 total) | Readers' playbooks (declarative wiring, not code) |

---

## RELATES TO
- [[Company Map]] (whole structure)
- [[mcp_face — constitution]] (tool design principles)
- [[roles — constitution]] (role registry details)
- [[skills — constitution]] (skill registry details)
- [[runtime — constitution]] (discovery + execution)
- [[contracts — constitution]] (address scheme, AGENTS.md)

---

## ABBREVIATIONS & REFERENCES
- **C2.x** = Concurrent Cognition G2 (role registry, mode/cast architecture, resolved slots, binding)
- **G16** = No-confidence law (tags+counts instead of fabricated float scores)
- **GC1-GC7** = Guide/Composition tiers (flows, verify lenses, panel seats, etc.)
- **AK3** = Cognition Engine (composition skills, multi-step workflows)
- **E4** = Jury correlation caveat (N draws on ONE model = variance, not independent)
- **M4** = Self-teaching response (drift-home reflection in create tool return)
- **MCP-DESIGN-PRINCIPLE** = mcp_face/AGENTS.md:§ (one tool per resource, file-discovered, no new tool per op)
- **CONTRACT-FORMAT §9.2** = Export OPS constant; drift tests verify dispatcher matches
- **registry-is-truth** = No hardcoding, no second sources; file-discovered rows are the single truth
- **Floor** = Governance law (NO auto-apply on cold agents, models gated in roles, operator verbs separated)
- **CQRS** = Command Query Responsibility Segregation (READ/WRITE tools split by audit)
- **mode_scope** = Which mode(s) a role participates in; determines cast membership
- **resolved slots** = Compute per coordinate (grain/viewer/mode/subtype/register) at run-time
- **NEUTRAL_FRAGMENT** = Non-authorable dragnet prompt text (neutral pass ≠ relevant pass)
- **no-fiction guarantee** = Two-layer: deterministic refcheck (Layer 1) + soft jury (Layer 2)

