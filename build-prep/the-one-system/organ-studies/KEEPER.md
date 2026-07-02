# ORGAN REBUILD STUDY — THE KEEPER + ITS CONTEXT

*(④ the-one-system · fusion session, 2026-07-02. [O]=Observed, [I]=Inferred.)*

## 1. SIDE A — the cloud Keeper pattern

### IS [O]
- **A standing agent-member with a config cascade.** projects.keeper_agent (text: 'ci-keeper-agent', 'vi-coder-keeper', one raw uuid) names the tending AI per project; assistant_registry resolves to a runnable (langgraph_assistant_id, provider_config) — the keeper's BODY is an external LangGraph assistant.
- **Membership**: project_members rows member_type='agent', agent_key ∈ {ci-keeper-agent, @keeper}, role='keeper', permissions {read,write,admin} [O, queried]. ci_create_project (schema.sql:4370-4389) **auto-inserts the keeper member at project creation** — binding is part of the project's birth.
- **Config**: keeper_agent_config (37620) {space_id, project_id, scope_key, config_key, config_value jsonb, override_level}; comment: "Level 0 = global, 1 = space, 2 = project, 3 = scope" (37637). NOTE: no inherits_from column exists in either table's DDL [O] — inheritance is implicit in the resolver's level-descend. projects.agent_config exists but every live row is {} [O] — a reached-for slot never filled.
- **The 4 live rows** [O]: initialization_procedure L0 {steps: [load_project_context, index_resources_by_decorator, build_knowledge_map, check_active_issues, identify_priorities]} · navigation_capabilities L0 {search_resources, traverse_hierarchy, filter_by_decorator, cross_project_search} · creation_capabilities L0 {create_projects, create_resources, create_workflows, annotate_entities} · domain_expertise L2 {specializations: [pipeline_composition, langgraph_integration, schema_design, pattern_detection, embedding_strategies, mcp_tool_design]}.

### WORKS [O]
- **Resolver**: ci_resolve_keeper_config (6716-6733): match key at scope(3)/project(2)/space(1)/global(0), ORDER BY override_level DESC LIMIT 1 — most-specific-wins, walk-up inheritance. Absent → {_not_configured: true} (a legible absent).
- **Context composer**: resolve_keeper_context (21580-21684): identity{user, actor, space, correlation, source} · project{key,name,type,phase,status,purpose} · notice_board (counts + critical) · scopes · resources (counts) · graph (edge counts) · members · keeper (the assistant row). One monolithic SQL composition.
- **Context → prompt**: resolve_prompt_variables (21745+): keeper context + resolve_tokens, then walks prompt_variable_registry (priority-ordered, decorator-affinity-filtered, token-gated) rendering project_name, notice_board_summary (with embedded tool-hints), critical_items, active_frame, autonomy_level, response_style. The keeper's system prompt is ASSEMBLED from registry-declared variables resolved against composed context.
- **The accreting token**: compose_project_page (9216) reads user_id/view_mode, derives archetype, pulls display_constraints from context_modifiers (dimension=archetype), and **RETURNS context_token || {theme_id, space_id, view_mode, archetype}** (~9460) — the token flows through and comes back ENRICHED. compose_block (8930) reads user/space/device/spatial/theme per block. context_modifiers declares 9 TCS dimensions (36027): narrative_progression, audience_segment, mood_tone, purpose_intent, brand_identity, temporal, spatial, state, archetype.

### REACHING [I]
"Universal Keeper agent adapts to project context" — one universal agent, per-context behavior via data. But the adaptation surface is thin: config values are capability FLAGS, not executable behavior; only domain_expertise exercises the ladder above L0; the token accretes but nothing records WHO added WHAT; the keeper's mind is opaque (external assistant id + blob).

## 2. SIDE B — the engine's cognition role system

### IS [O]
- **Roles**: roles/<id>.py declared units, file-discovered (RoleRegistry mirrors NodeRegistry); facet follows populated fields (prompt+schema ⇒ fireable; mode_scope ⇒ in a cast; draws ⇒ jury). ~40 live.
- **Resolved slots**: prompt_slot/schema_slot/thinking are resolve_slot values — literal | {select, cases, default?} | {op,args} AST — resolved per turn against the COORDINATE (grain·viewer·mode·subtype·register) in run_role (cognition.py:441-479). Canonical: explain_role.py prompt_slot={select:"subtype", cases:{theorem-fork, authorize, trade-off, cross-lane}, default} — **one role, context-resolved framing**.
- **The one resolver**: resolver.py — resolve(invariant, coordinate) → concrete, PURE, fail-loud; continuous axes by relationship-AST, discrete by registry-lookup. "You never store a variant."
- **Casts**: cast_for_mode(mode) (roles.py:352) = every role whose mode_scope includes the mode; fired concurrently in the staged turn (activation.py:186). listening cast: focus/recall/ground/connect/check/voice.
- **Territory**: territory_for(address) composes identity (per-scheme via the ONE resolve_address) + corpus + context items/chats + typed-edge relations + library + memory — **every leg independently guarded, degrade-to-noted-absent, timeout-bounded**; territory_prose renders the [Operator context] block (never raises; meaning only, never raw addresses).
- **The third articulation** [O, queried]: vi_shared.vi_persona — the persona as a versioned row ("Editable by Vi via update_persona… Read into every prompt under ## Persona"); vi_shared.vi_self_model — a registry of the agent's self-surfaces (persona, capability-tree, gap-log, work-graph…), each declaring edit_tool/edit_surface/events. **Identity and self-knowledge as governed, versioned data.**

### WORKS [O]
One brain active at a time; a turn composes territory prose → the cast fires concurrently → slots resolve against the shared coordinate → sampling/thinking per model-family registry → answers; route-back writes close the loop. Registry-declared, fail-loud, provenance-stamped.

### REACHING [I]
The engine has the BEHAVIOR of a tending intelligence but **no tended thing**: no standing member bound to a project address, no per-project config, no inheritance depth (slots select on exact values — no walk-up), the composed territory used once and discarded (nothing accretes), and the persona/self-model articulation sits in a third place.

## 3. COMMON CORE · UNION'S EDGES · IMPLIED-BUT-ABSENT

### COMMON CORE
1. **The tending AI is universal; its behavior is data resolved by context** — "Universal Keeper adapts" ≡ "one role, context-resolved behavior". Same sentence, two dialects.
2. **Resolve-by-specificity, most-specific-wins** — ORDER BY override_level DESC LIMIT 1 ≡ {select, cases, default}. The same operation.
3. **Context is composed at an anchor into a structured object folded into the prompt** — resolve_keeper_context(project_key) ≡ territory_for(address) + prose.
4. **The agent joins the world through the same fabric as everything else** — agent member rows ≡ typed edges.
5. **The prompt is assembled from registry-declared variables resolved against context** — prompt_variable_registry ≡ prompt_slot + resolve_slot.

### UNION'S EDGES
A brings: the containment LADDER with walk-up inheritance (0→3) · the ACCRETING context_token (returned enriched at every stage) · member-row binding created with the project · the notice-board/status leg · priority-ordered token-gated prompt variables · the TCS 9-dimension context_modifiers.
B brings: ONE pure resolver (continuous + discrete axes, fail-loud) · casts + concurrency · per-leg guarded degrade + timeouts · operator-law prose · provenance stamping · **persona/self-model as governed, versioned, self-editable data** · file-discovered registries · capability-query model binding.

### IMPLIED-BUT-ABSENT
- **The ONE ladder mechanism** serving config AND slots AND tokens — A has depth without the resolver; B has the resolver without depth.
- **An address-anchored context object that both composes AND accretes** — A accretes a flat token with no legs/provenance; B composes rich legs that don't accrete.
- **The keeper as a composition** (member + cast + config + persona at one address) — A has member+config with an opaque mind; B has the mind without a binding.
- **Per-project cast/persona rungs** — A's domain_expertise L2 gestures; B's casts are global per mode.
- **Config values that EXECUTE** — A's flags never gate anything observable; B's verb whitelist (RHM_VERBS) is exactly the gate they should feed.

## 4. THE REBUILT ONE

### 4.1 What the tending AI IS
**Not a new primitive — the composition of four existing primitives anchored at one address (project://<key>):**

| Half | Primitive | Landed as |
|---|---|---|
| binding | a member edge: agent://keeper —member-of→ project://<key> (role=keeper), with equal-and-opposite referenced_by | one typed edge, written at project creation (A's move in B's fabric) |
| behavior | a cast: cast_for_mode('keeper') — roles declaring mode_scope ⊇ {keeper} | existing roles/<id>.py files; zero new registry |
| parametrization | config rungs: ladder invariants per config_key (the 4 live keys carry over verbatim) | registry rows keyed (address-prefix, config_key) → value; Supabase-resident per NORTH-STAR §4 |
| identity | a persona record: agent://keeper/persona — vi_persona's shape (versioned, governed edit), overridable per project by a deeper rung | an addressed, versioned row; the self-model registry IS Suite.capabilities() served as data |

**"A role? a cast? a standing member with config?" — a standing member whose mind is a cast whose parameters are rungs whose identity is a record. All four are addresses.**

### 4.2 ONE context-resolution ladder (the single mechanism)
Keeper config · role slots · token values become **one slot-kind added to runtime/resolver.py** (schema-additive, reuse-don't-parallel):
```
{"ladder": "address",                          # the containment axis
 "rungs": {"": v0,                             # universal   (A's level 0)
           "space://x": v1,                    # space       (1)
           "project://x/y": v2,                # project     (2)
           "project://x/y#scope": v3},         # scope       (3)
 "default"?: v}
```
Resolution = **longest-prefix match on the coordinate's address** (deepest rung wins; walk up on absence; no rung + no default → fail-loud legible absent + breadcrumb). ci_resolve_keeper_config's ORDER BY override_level DESC re-expressed as a pure resolver slot — **override_level was always containment depth in disguise; the address IS the level.** Then: keeper config resolves through resolve(); role slots unchanged (and MAY now use ladder slots → per-project prompt framing and per-project casts); token values (theme/archetype/autonomy/response_style) = ladder+select slots over the same coordinate.

### 4.3 territory × context_token = the CONTEXT ENVELOPE
```
envelope = {
  coordinate: { address: "project://<key>",            # the anchor
                user_id, audience, autonomy,           # WHO   (A's token)
                device, platform, spatial, temporal,   # WHERE/WHEN (A/TCS)
                mode, viewer, grain, subtype, register,# B's turn axes
                theme_id?, archetype?, view_mode? },   # accreted as stages resolve
  territory: { identity, relations, corpus, memory,    # B's legs (guarded, bounded)
               status },                               # NEW leg = A's board/scopes/resources/members summary
  trail: [ {stage, added, at} ]                        # NEW: who accreted what
}
```
- Only `coordinate` (small, serializable — A's discipline) + `trail` accrete. Territory is COMPOSED, never accreted — recomputed per address, cached per turn.
- Lives nowhere at rest — resolution-first/derive-never-place. What lands is the turn's run:// record carrying the final coordinate as provenance.
- Every stage receives the envelope, resolves via the ONE resolver against coordinate, reads territory legs, **returns the envelope enriched** — A's RETURN token||{…} made universal, with B's guarantees (dead leg = noted-absent; enrichment failure = a trail note, never a killed turn).

### 4.4 The join
Creating project://<key> writes exactly ONE member edge. Nothing else is copied: universal rungs, the keeper cast, the global persona are FOUND BY RESOLUTION. Specializing = writing one deeper rung row; removing restores inheritance. A's L0-inherits-everywhere achieved by B's never-store-a-variant law.

### 4.5 End-to-end: "the Keeper answers about its project"
1. ARRIVE: question + surface token → coordinate {address: project://<key>, user, device, platform, temporal, audience, view_mode, mode:'keeper'}.
2. COMPOSE: territory_for(project://<key>) — identity (the project record), relations (member edges), status (board counts + critical + scopes/resources — A's composition as a guarded leg), corpus + memory. Absent legs noted, never fatal.
3. PARAMETRIZE: resolve(config-invariants, coordinate) → initialization_procedure (which legs/steps) · navigation/creation_capabilities (**→ gates the governed verb whitelist — the flags finally execute**) · domain_expertise + persona (→ prompt framing).
4. FIRE: cast_for_mode('keeper') concurrently; slots resolve against the SAME coordinate; territory_prose = the [Operator context] block.
5. ANSWER + ACCRETE: envelope returns enriched; the turn lands as run:// with the coordinate as provenance; route-back marks/decisions target the same address.
6. FAIL-LOUD: missing rung → legible absent + breadcrumb; dead leg → noted-absent; never silent degrade.
One function `keeper_answer(address, question, token)` — the chat surface and the agent tool both call it (one function → two faces).

## 5. EACH SIDE'S PARTIALITY
**A is the skeleton without the mind** — knows where the keeper stands, how parameters inherit, that context must flow and grow; but the cognition is an opaque external assistant, config flags are inert, the ladder is per-key SQL, the composer is a monolith without degrade, only one row exercises depth, agent_config sits empty, accretion records what but never who/why.
**B is the mind without a home** — knows how one intelligence behaves differently per context, how context composes with grace under failure, how identity is governed data; but nothing tends anything: no binding, no per-project config, no containment inheritance, the composed context evaporates after one render, the persona lives disconnected.
**The third articulation (vi_persona/vi_self_model) is the fragment both lack**: the tending AI's SELF as an addressed, versioned, edit-governed record — which is why the rebuilt Keeper carries a persona record and a self-model registry as first-class halves.

**Key refs:** schema.sql:6716, 21580, 21745, 9216+~9460, 8930, 37620/37637, 4370-4389, 36027 · runtime/resolver.py · runtime/roles.py:352 · runtime/cognition.py:441-479 · runtime/territory.py · roles/explain_role.py · roles/AGENTS.md:36-44 · cvi_mine: keeper_agent_config (4), project_members agent rows, vi_shared.vi_persona/vi_self_model.
