# ORGAN REBUILD STUDY — MEMBERSHIP + TENANCY
*(④ the-one-system · fusion session, 2026-07-02. Who exists, who belongs, who may see/do what — THREE partial articulations. Observed/Inferred tagged.)*

## 1 · EACH SIDE

### SIDE A — the cloud container (cvi_mine)
**IS** (Observed): **15 auth.users** — the only outward identity FK. Named: t.geldard@conceptv.com.au (554e223d…), v.i@conceptv.com.au (ebe5f9c7…), vi@system.local (reserved uuid …0001), grant@gapdevelopment, phil.geldard, scott.geldard, nick.godfrey — plus **7 users with no email** (test debris). · **55 spaces**: 15 personal (one per user, unnamed), 14 "Default Project", 10 Vi:* mode spaces owned by the Vi principal, + named work projects. Comment: "Personal space = Vi's memory about user. Project spaces = actual work/collaboration" (38724). · **42 space_members**: principal_id **FK auth.users (NOT polymorphic)**, role + scopes[] + role_definition_id + granted_by/revoked_at. **All 42 rows role=owner**, scopes {read,write,execute,admin,approve} (two Local Dev rows add dev.trace_code, dev.modify_structure). · **14 project_members**: **polymorphic** — member_type user|agent, user_id XOR agent_key, role, permissions, member_context/activity_summary. · **11 role_definitions**: system owner/editor/viewer/guest + TEMPLATES with a fine scope grammar — write:leads, execute:send_quote, approve:financing_proposals (dealership set), Project Lead/Contributor/Reviewer. parent_role_id inheritance + scope_constraints. · **14 delegations**: every user → grantee_actor_id='vi:global' (**bare text, no FK**), space=NULL (global), scopes {read,write,create:intent,create:proposal}, max_autonomy L0–L5, validity window, UNIQUE(user,grantee,space). 13 at L3; ebe5f9c7 alone at **L5** (+create:agent_workflow, deploy:langgraph, manage:user_agents). · **user_policy** (36430): per-user max_autonomy, delivery prefs, quiet hours, budget limits, capability allow/deny. · **The minting circuit** — create_user_environment() trigger (~10500): new auth user → personal space + default project space + vi:global L3 delegation + user_policy; **phone ending 615 → L4** (matches remote.py's "Tim (…615)"). The Vi entity (…0001) gets a personal space only — "Vi IS the autonomous system."
**WORKS** (Observed): RLS membership-derived, deny-by-default — spaces_unified_access (creator OR owner OR unrevoked member OR active project_member), space_members_visibility (own rows), delegations_user_visibility, project_members_visibility (own OR co-member via SECURITY DEFINER user_is_project_member()). check_delegation(user, actor, space, scopes[]): space-specific-over-global (ORDER BY space_id NULLS LAST), window, scope-superset (@>).
**REACHING** [I]: full multi-user multi-tenant collaboration where WHAT AN AI MAY DO FOR A USER is a first-class, windowed, autonomy-graded record; roles-as-data for arbitrary businesses (the dealership templates).
**Not verified**: any live caller of check_delegation/user_policy; and check_project_access **always allows when auth.uid() IS NULL** ("Service role… always allow") — an explicit service-layer bypass.

### SIDE B — the engine (/home/tim/company)
**IS** (Observed): **runtime/principals.py** — ONE principal registry as a RESOLVER VIEW over channel reg files (.data/channels/<handle>.json). Kind axis **AGENT | VIEWER** (+ honest `ambiguous`), open ("a third kind… additive later"). Resolution: explicit principal_kind wins → agent signals (claude_pid, ch-/ga- handle, supervised) → viewer signal → **ambiguous, never silently bucketed**. operator.json (a supervised session acting FOR Tim) deliberately flagged ambiguous. Maps channel MEMBER_KINDS so identity-kind and room-membership-kind are one vocabulary at two granularities. · **runtime/grants.py** — OWUI-shaped rows (resource_type, resource_id, principal_type, principal_id, permission) in append-only jsonl; principal_type ∈ viewer|agent|group, the law: the type axis **"EXTENDS BY ADDING VALUES… zero migration"**; `*` is a principal_ID, never a type. **Seeded to reproduce exactly today's remote decision; consulted IN SHADOW only.** · **runtime/governance.py** — action-class postures on reversibility·cost·externality: AUTO/SURFACE/CONFIRM, LOCKED={source_data, external, frozen_contract} never graduates, **unknown class → CONFIRM** (fail-closed). Inbox: resolve() operator-only, OFF the MCP face; a separate status lane never touches resolved. · **mcp_face/remote.py** — Bearer-only; JWT verified; **sub == OPERATOR_USER_ID (env default ebe5f9c7…, "Tim (…615)") → ALL tools; any other valid user → posture=='safe' subset; unclassified → operator-only fail-closed**. "No connector-scope claim is required or consulted — identity IS the gate" (260, 292-294). **Mandatory audit**: every call (incl. DENY) rows into connector_audit via service-role REST; **audit-write failure ⇒ the call is refused**. Grant-shadow divergence logged loud (147-163, 468-473).
**WORKS** (Observed): tools/list + tools/call derive from the live registry filtered by tier; dispatch inherits the stdio face's teaching errors.
**REACHING** (stated in docstrings): flip authority to the grant table once the shadow is trusted; a third principal kind; grants derived rather than seeded.

### SIDE C — the LOCAL live public schema (the two-party design store)
**IS** (Observed, live): **clients** — one row claude-design: oauth_client_id, mcp_url, **per-tool contract** in allowed_tools ({scope, allowed sub-verbs, remote_posture} — observed postures `safe` and `design` only), scopes ['company:design:read','company:design:write'], approval_mode='operator-gate', channels=['design','design-pipeline'], bind_aud=false (staged). · **custom_access_token_hook** — OAuth tokens matching the registered client get claims stamped FROM the clients row at mint time (registry-is-truth): app_metadata {role: design_client, client_id, scope}; everything else passes untouched. · **Resolvers**: client_id() (JWT → active clients row), is_design_client(), is_company_boundary(), channel_granted(chan) — **two-sided consent**: the client lists the channel AND the channel has shared=true. · **RLS two-party boundary** (17 policies): boundary policies (full via is_company_boundary()) paired with client policies bound to row identity (from_session=client_id() on posts, submitted_by=client_id() on submissions, channel_granted on rooms). · **connector_audit** (18 rows): B's mandatory-audit landing table. · **4 local auth.users** — a deliberate claim TEST MATRIX (full stamp / boundary role / scope-only / plain).
**WORKS/REACHING**: proves an external AI vendor can be a CONTRACTED principal — identity minted from a registry row, capabilities enumerated per-tool with sub-verb allowlists, everything audited, shared surface requiring consent from both parties. Reaching: N clients, richer postures, bind_aud.

## 2 · COMMON CORE · UNION'S EDGES · IMPLIED-BUT-ABSENT

### Common core
1. **Registry-is-truth identity**: a credential resolves against a registry row — never a hand-list (remote.py deleted its exposure file; the hook reads the clients row; A's trigger provisions from the users table).
2. **A KIND axis on principals**: user|agent (A) · viewer|agent|group extends-by-values (B) · design_client vs company_boundary (C). Same axis, three vocabularies.
3. **Membership as a typed, revocable, consented edge to a container**: space/project_members (A), grant rows (B), client↔channel with shared=true (C — the only TWO-SIDED one).
4. **Fail-closed everywhere**: RLS deny-by-default (A,C); unclassified → operator-only, unknown class → CONFIRM (B).
5. **One distinguished operator whose identity IS the boundary** and who is the only resolver of gated decisions: sub==OPERATOR (B); operator-gate (C); phone-615 → L4 (A); Inbox.resolve operator-only off the MCP face (B).
6. **Mandatory audit at the boundary** (B fail-loud → C's table; A's audit triggers).
7. **AI autonomy is granted, graded, and bounded** — delegations L0–L5 + user_policy (A); AUTO/SURFACE/CONFIRM/LOCKED (B); per-tool posture + operator-gate (C). **Three graduations of the same dial.**

### Union's edges
A only: container hierarchy · personal-vs-project semantics · roles-as-data with inheritance + templates · delegation windows + space-precedence · user_policy (quiet hours, budgets, allow/deny) · auto-provisioning trigger · membership-derived RLS.
B only: principal resolution **with evidence and honest ambiguity** · the **shadow-migration method** (seed-to-current → prove-equal → flip authority) · posture axes + LOCKED forever-confirm · the surfaced-decision inbox as THE approval channel · audit-failure-refuses-the-call.
C only: **external AI client as a contracted first-class principal** · claim minting at token time from the registry · two-party RLS · two-sided channel consent · per-tool **sub-verb** allowlists · the claim test matrix.

### Implied-but-absent
1. **Agents as durable principals.** A's grantee is the string 'vi:global'; agent_key is text; B's agents live in ephemeral session files; C's client isn't a member of any space. Cloud user vi@system.local (…0001) and actor string 'vi:global' are THE SAME ENTITY, never joined. No table where an agent has an id, a kind, and edges the way a user does.
2. **One scope grammar.** A: read/write/execute/admin/approve + write:leads; C: company:design:write; B: permission='use'. Three grammars, no parser, no registry.
3. **The delegation→enforcement wire.** A stores delegations and defines check_delegation; B enforces confirms — **neither reads the other**. L0–L5 and AUTO/SURFACE/CONFIRM are the same idea, unbraided.
4. **One operator record.** Tim is minted three ways: env-var (B), phone-615 trigger (A), boundary claim (C). No single "this is the operator" row.
5. **Effective-access as a queryable function** — nothing answers "who can see/do X at address Y" as one call.

## 3 · THE REBUILT ONE

### 3.1 The one principal model
```
principal(principal_id uuid, kind text, handle text, display text, status, metadata, created_at)
kind ∈ {operator, human, agent, client}   -- OPEN vocabulary (extends by adding values)
```
operator — exactly one active row: Tim. · human — outside people. · agent — Vi ('vi:global' ≡ vi@system.local …0001, finally ONE row), ci-keeper-agent, @keeper, durable identities for live sessions (B's file resolver stays as the live-session transport registry; durable identity is the row). · client — external AI vendors (claude-design's contract fields live on/beside its row). **The standard party/actor pattern brought proactively: identity ≠ authentication.**
```
principal_auth(principal_id, auth_user_id FK auth.users)   -- authentication is an EDGE TO identity
```
Humans/clients have one or more auth users; most agents none. Fixes A's partiality (space_members FK auth.users can't hold agents) WITHOUT breaking it — additive.

### 3.2 Containers + membership — one edge type at every level
Containers are ADDRESSES: company → space → project → channel.
```
membership(principal_id → principal, container_kind, container_address,
           role, scopes text[], role_definition_id, granted_by → principal, granted_at, revoked_at)
```
space_members, project_members, clients.channels are all instances of this ONE edge. **Two-sided consent kept from C**: access = membership row exists AND the container admits that principal kind (shared=true generalized to a container-side admits[]). role_definitions kept as-is (A's is the richest) — roles are DATA, the single source RLS and the gateway both read.

### 3.3 The layered authorization stack
| # | Layer | Question | Mechanism | Where |
|---|---|---|---|---|
| L0 | Authentication | Token valid? | Supabase JWT / Bearer (B) | GoTrue + gateway |
| L1 | Claim minting | What does the token carry? | the hook stamps kind/principal/scopes FROM the registry (C) | token hook |
| L2 | Principal resolution | Who/what kind? | principal table + B's evidence-based resolver; honest-ambiguous | gateway/RPC |
| L3 | Tenancy floor (RLS) | May it see this ROW? | membership-derived policies (A) + kind policies (C) — unbypassable | Postgres RLS |
| L4 | Capability | May it USE this verb on this resource? | grant rows **derived** from membership × role_definitions × client contracts (derive-never-place), C's sub-verb allowlists as resource-qualified rows | gateway |
| L5 | Conduct/autonomy | HOW may it act right now? | posture (AUTO/SURFACE/CONFIRM/LOCKED) **intersected with the delegation** (ceiling = stricter of class posture and delegation max_autonomy + window + scope-superset — A's semantics finally enforced). CONFIRM resolves ONLY through the operator inbox (B+C one mechanism) | runtime guard |
| L6 | Audit | Recorded? | mandatory connector_audit insert; failure refuses the call | gateway |
**The scope grammar** (the missing unifier): one registered grammar <domain>:<resource>:<verb> — A's five verbs are the verb set; write:leads and company:design:write both parse into it; grants and delegation scopes store the normalized form. The grammar is a registry, not convention.

### 3.4 Tim's identity + the 15→map
**Observed**: the engine's operator is ebe5f9c7… = v.i@conceptv.com.au — the L5 account, owner of the real work projects, the "615" super-user. t.geldard@ = 554e223d… owns Local Dev/Obsidian/EL. **[I], flag for Tim: both are Tim — a working account and a person account.**
**Rebuilt**: ONE principal(kind=operator) row, minted by a SEED MIGRATION (registry-authored, never an env default); both auth users attach via principal_auth. OPERATOR_USER_ID becomes a READ of that row — one minting story replacing three. The boundary service identity becomes an AGENT principal acting for the operator — the operator.json ambiguity resolved by making "acts-for" a delegation edge instead of a classification puzzle.
**The 15 cloud + 4 local**: 2 → the operator principal (pending Tim's confirm) · vi@system.local → the vi:global agent principal (one row at last) · grant/phil/scott/nick → human principals (curate real vs family-test) · **7 no-email users → test debris, archived, not migrated** · the 4 local users stay a claim-matrix TEST FIXTURE, never principals.

### 3.5 Delegation as first-class
```
delegation(delegator → principal, grantee → principal,   -- FK now, not text
           container address|NULL, scopes[], max_autonomy L0..L5, valid_from/to, status)
```
A's table nearly right; the rebuild resolves grantee to a principal FK and — the actual gap — **wires it into L5**: the same guard that gates Tim's confirms reads the delegation to bound what Vi may auto-do for a user in a space this week. A's precedence + window semantics kept verbatim.

### 3.6 The personal space
Lands as **a container, not a permission construct**: one space(type=personal) per human principal, auto-provisioned at principal creation (A's trigger kept), membership = {the human as owner} ∪ {agents holding an active delegation from that human}. Contents = the AI's model-of-the-user: user_policy, preferences, memory. Work never lives there. Multi-user then costs nothing new: one principal + auto personal space + membership edges — the same circuit, for all four principal kinds.

### 3.7 Migration method + the genuinely new
Schema-additive: principal/principal_auth/membership/scope-grammar are NEW; space_members/project_members/clients/delegations stay, are **mirrored into the new model, run as a proven-equal shadow, then authority flips and the old read path is commented out** — B's grant-shadow method IS the migration method; NORTH-STAR's comment-out-with-breadcrumbs is the retirement rule.
**Genuinely new**: the effective-access resolver as ONE shared function — access_of(address) / may(principal, verb, address) — projected to both MCP and UI, so the permission the UI displays and the permission the gate enforces can never diverge.

## 4 · EACH SIDE'S PARTIALITY
**A** modeled the SOCIETY but never enforced it and can't hold its own AI: richest containers/roles/delegations, but principals are auth.users only (agents are bare strings), check_delegation has no evidenced caller, check_project_access waves service-role through, 42/42 members are owner — a multi-tenant model living a single-tenant life. Knows WHO BELONGS; gates nothing an agent does.
**B** built the LIVE GATE and the right laws (fail-closed, honest ambiguity, extend-by-values, shadow-then-flip, audit-or-refuse) but is flat: binary tier, no containers, no scopes consulted, principals in ephemeral files, grants seeded not derived. Knows HOW TO CHECK; almost nothing structured to check against.
**C** is the only side where an external AI is a contracted, minted, audited principal with two-sided consent — but a two-party miniature: one client, no humans-as-members, no containers above channels.
**A: who belongs · B: how it's checked · C: how an outsider is contracted in.** The rebuilt organ is the braid.

**Key refs:** runtime/principals.py · runtime/grants.py · runtime/governance.py · mcp_face/remote.py (67-163, 460-509) · schema.sql (create_user_environment ~10500; check_delegation ~3965; spaces comment 38724; delegations 36419; user_policy 36430) · live rows via cvi_mine + local postgres · AGENTS.md · NORTH-STAR.md.
