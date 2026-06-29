---
type: proposal
register: prescriptive
title: IDENTITY + USERS Fusion — the AI members are company identities; the humans are who is looking
subject: openwebui-company-fusion (identity layer)
posture: both sides incomplete + unreviewed; no source of truth; best parts fused INTO THE COMPANY; no duplicates
created: 2026-06-28
verification_basis: live company source (file:line, Observed) + OWUI map (owui-side-map.md §7) + live .data/channels regs (Observed) + area-A/D/E maps
relates-to: ["[[owui-side-map]]", "[[area-A-runtime-core]]", "[[area-D-channels-voice]]", "[[area-E-mcp-roles-skills]]"]
tags: [fusion, identity, users, principals, access-control, personas]
---

# IDENTITY + USERS Fusion

> **Reading note.** The headline insight is verified on disk, not assumed: the company **already** carries
> humans and AI sessions in **one registry** — `.data/channels/tim.json`, `.data/channels/operator.json`,
> and the `ch-*.json` agent sessions are siblings in the same channel-member directory. The fusion is not
> "bolt a user system onto an agent system." It is: **finish the identity kind that already half-exists**,
> and graft OWUI's *enforcement* discipline onto it — without importing OWUI's user table.

---

## 0. VERIFICATION DONE (trust nothing — what I actually confirmed live)

| Claim under test | Verdict | Evidence (Observed) |
|---|---|---|
| Company agent identity = handle/role/model/profile | **PARTLY TRUE — thinner than claimed** | `.data/channels/ch-cr4p7uxj.json` schema = `{handle, session_id, cwd, description, model, profile, pid, claude_pid, port, started, transport}`. The reg is a **liveness/transport** record. "role" is NOT a reg column — it lives inside the free-text `profile` blob. |
| `profile` carries model/role/focus/expertise | **TRUE but self-described + ungated** | Live regs: `ch-q8fhrkkd.json` profile keys `['model','role','focus','expertise']`, model `claude-opus-4-8[1m]`. Written by the agent itself via the `profile` MCP tool (area-D:16; company-channel server instructions). No validation, no authority — an agent declares its own identity. |
| Humans already in the same registry | **TRUE — this is the keystone** | `.data/channels/tim.json` (`handle:"tim"`, desc "operator surface"), `operator.json` (`handle:"operator"`, "the room operator (NL→ops)"). Humans/operator are channel members **of the same kind shape** as `ch-*` agent sessions. |
| Company has a "roles registry" | **TRUE but it is NOT identity** | `roles/*.py` (area-E, 34 files) = **cognition roles** (focus, recall, ground, judge, voice…). These are *model-execution units*, not principals/personas. **Naming collision only** — zero identity-role overlap. Verified: `runtime/roles.py` has no principal/viewer/permission/human concept. |
| Company has user/viewer/permission/AccessGrant tooling | **FALSE — absent** | No `mcp_face/tools/{user,viewer,auth,perm,grant,ident,princ}*.py`. The only access primitives are (a) the **operator token** (`bridge.py:564 _mint_operator_token`, `:572 _is_genuine_operator`, `:677 _tool_gate`) and (b) MCP **posture tiers** (`mcp_face/remote.py:69 TIER_OPERATOR`, `:74 _tool_posture` — operator vs non-operator "safe" subset, fail-closed). |
| Company has a real auth principal | **TRUE — `supabase_principal.py`** | `runtime/supabase_principal.py`: least-privilege RLS-scoped JWT (login→Bearer), "itself a client-registry row." This IS the company's native "authenticate-as-a-scoped-identity" mechanism, already used by `channel_boundary` + `vi_vision`. |
| OWUI `AccessGrant` shape | **TRUE — with one correction to the map** | **Verified live** `open_webui/models/access_grants.py:20-41`: `AccessGrant(resource_type, resource_id, principal_type, principal_id, permission, created_at)`, UNIQUE on (type,id,principal_type,principal_id,permission). **Correction:** `principal_type` is **`"user" or "group"` ONLY** (`:23` comment). The wildcard `*` is a value of **`principal_id`** (`:24` "user_id, group_id, or `*` (wildcard for public)") — NOT of `principal_type`. The map (owui-side-map §7) put `*` on the type; it is on the id. |
| OWUI identity stack (auth + enforcement) | **TRUE (mapped, not re-verified)** | owui-side-map.md §7/§4: `User(role pending/user/admin, oauth, scim)`, `Group(permissions)+GroupMember`, chained-base (`has_base_model_access`), SCIM/OAuth/LDAP/trusted-header. Grant *table* verified above; these auth adapters taken from the (well-cited) map. |

**Net correction to the brief's "Known":** the company does NOT have a rich agent-identity registry with role
+ permissions. It has a **thin liveness reg + a self-authored profile blob + a binary operator gate**. That
makes the fusion *more* additive, not less — there is little to dedup, much to build, and OWUI supplies the
exact missing organ (a typed principal + a grant table).

---

## 1. BEST PARTS

**From the Company:**
- **One membership registry for everything that participates** (`.data/channels/`, projected by
  `session_channels.fold_channels`, area-A §6). Humans and agents are already siblings. *This is the prize* —
  it dissolves the "users vs agents" split before it starts.
- **Self-described agent profile** (model/role/focus/expertise via the `profile` tool) — the AI member's
  *operating identity* (what brain, what it's doing now), naturally live and self-maintained.
- **Personas as character-identity** (`voice/personas.py`, verified full read): `brain` (system-persona),
  `voice_description`, `engine`, `voices{}`. This is the AI's **presented self** (Viv/Tess/Sable/Pip/Wren over
  one VOICE_BASE) — a layer OWUI has no equivalent of.
- **`supabase_principal`** — a real least-privilege authenticated identity primitive, RLS-scoped, registry-row
  shaped. The company's native answer to "who is authenticated and what may they touch."
- **Posture-tiered capability gating** (`remote.py` operator vs safe-subset; `bridge.py` operator token +
  `_tool_gate` fail-closed). A working, if binary, access spine.

**From OWUI (owui-side-map.md §7, §4):**
- **A typed principal + grant table**: `AccessGrant(resource_type, resource_id, principal_type, principal_id,
  permission)` — relational, queryable, the forward-truth model (vs legacy JSON). The single best harvest.
- **A clean `principal_type` axis** (live: `user | group`; `*`-public rides on `principal_id`). The type is a
  free Text column with a UNIQUE constraint spanning it — so it **extends by adding values**
  (`agent`, `persona`, `viewer`) with zero schema change. This is exactly the "open kind axis" the company
  wants; the harvest is the *table shape*, and the extension is additive rows, not a migration.
- **Chained-base enforcement** (`has_base_model_access`) — a derived/preset identity cannot escalate past
  what its base is allowed. A real invariant worth keeping.
- **Group + GroupMember** (relational) — scalable role/permission bundling.
- **Enterprise auth adapters** (SCIM 2.0, OAuth/OIDC, LDAP, trusted-header SSO) — the *only* way real outside
  humans log in at scale. The company has none of this; it is pure harvest, no overlap.

---

## 2. THE FUSED MODEL — two clean KINDS, one registry, one grant table

**Decision: NOT one undifferentiated identity table, and NOT two parallel systems.** One *registry* that holds
**two typed kinds of principal**, both addressable, both grantable. This is the company's own pattern
(typed registry rows that resolve), applied to identity — and it matches the live fact that `tim.json` and
`ch-*.json` already cohabit one directory.

```
                          PRINCIPAL  (the one identity kind, principal://<kind>/<id>)
                        ┌───────────────────────────┬───────────────────────────────┐
            kind = AGENT (an AI member)                      kind = VIEWER (a human looking)
  ┌──────────────────────────────────────┐        ┌────────────────────────────────────────┐
  • session principal  (ch-* reg: live)            • the operator / Tim  (today: tim.json)
  • persona principal  (Viv/Tess/… : presented)    • outside humans  (OWUI auth: SCIM/OAuth/LDAP)
  identity = profile{model,role,focus} + persona    identity = email/oauth/scim + group membership
  authenticates AS = supabase_principal (RLS)        authenticates AS = OWUI auth → session JWT
  └──────────────────────────────────────┘        └────────────────────────────────────────┘
                        └───────────────┬───────────────────────────┘
                                        ▼
                    AccessGrant rows  (harvested from OWUI table shape, type axis extended)
   (resource_type, resource_id, principal_type∈ viewer|agent|persona|group, principal_id[ or "*" public], permission)
                                        ▼
                    gates → fabric capabilities (MCP tools, models, channels, knowledge, voice)
```

**How they relate WITHOUT duplicating:**
- **AGENT = the AI members** (the company's own people). Their identity is the **session reg + self-described
  profile + persona**. They are *created by participating* (a session registers; a persona is a declared
  registry row). OWUI's User table is **never** used to represent an agent — that would be the duplicate. An
  agent that needs to *act on guarded resources* authenticates AS a `supabase_principal` (already the pattern).
- **VIEWER = who is looking** (humans). Their identity + login is **OWUI's identity stack** (the enterprise
  auth + SCIM/OAuth/LDAP) — harvested as the company's *human-authentication adapter*. The operator/Tim is the
  first viewer (today crudely the operator token; the fusion upgrades the operator token into a viewer
  principal so it is one model, not a special case).
- **The bridge between them is the channel registry** (already live): both kinds appear as channel members, so
  the "who is in this room / on this thread" question has ONE answer regardless of kind. `fold_channels` keeps
  projecting; it just gains a `principal_kind` discriminator (it half-has one: `tim.json` lacks `claude_pid`,
  agent regs have it).

**Should OWUI's permission/AccessGrant model gate access to fabric capabilities? — YES, and it is the unifier.**
The company already gates (operator token + posture tiers) but **binarily** (operator / not). That is the
half-built seam. The fusion replaces the binary gate with the **AccessGrant table as the single authority**:
- `resource_type` extends from OWUI's set (`knowledge|model|prompt|tool|note|channel|file`) to the company's
  capability surface (**`tool` already covers MCP tools; add `capability`, `role`(cognition), `voice`,
  `persona`, `flow`**).
- `_tool_gate` (`bridge.py:677`) and `_tool_posture` (`remote.py:74`) **stop being the policy and become
  enforcement points that READ the grant table.** Posture stays as the *fail-closed default* (unclassified →
  operator-only); grants are the *positive* authority on top. This is the "INTO the company" graft: OWUI's
  table feeds the company's existing gate, the company's binary tiers become the floor of a richer model.
- OWUI's **chained-base invariant** (a preset can't exceed its base, owui §4) is a *candidate* tool for the
  agent/persona/session relation — but **which is base is an OPEN QUESTION, not settled here** (see §4 S-6).
  Note the relational tension Tim will scrutinize: a **persona (Viv/Tess) is durable** — it outlives any
  session; a **session (`ch-*`, has a pid) is ephemeral** — it *wears* a persona for its lifetime. So the
  stable identity-of-record is plausibly the *persona*, with the session as the transient instance — meaning
  inheritance may run **persona → session**, the opposite of OWUI's preset→base direction, or be orthogonal
  (session = liveness, persona = character, principal = grant-holder; three relations, not one hierarchy).
  This is left explicitly open for Tim; the grant table works under any of them.

**One registry or two kinds?** → **One registry, two typed kinds, one grant table.** (Per the company's
"unions not bridges" + "both plus others" laws: it's not user-XOR-agent; it's one principal abstraction with a
`kind` axis, open to a third kind later — e.g. a service/integration principal, which `supabase_principal`
already foreshadows.)

---

## 3. COMPANY-INTERNAL DUPLICATION — found + resolutions

**D-1. Three places say "who an agent is," none authoritative.**
- (a) channel reg `model` column; (b) `profile.model/role/focus`; (c) the persona (`voice/personas.py`).
  These overlap on "model" and "role/character" with **no single truth** and free-text drift (live regs show
  `claude-opus-4-8`, `claude-opus-4-8 (1M)`, `claude-opus-4-8[1m]` — three spellings of one model).
  **Resolution:** the **AGENT principal row** is the single identity record. `profile` becomes a *projection
  of the live session onto that principal* (operating-state, not identity-of-record); persona becomes a
  *typed attribute/preset* of the principal (presented-self), not a separate parallel store. Model string is
  normalized through the existing model registry (area-A: model is a TIM-RULE registry pick, not a literal) —
  the three spellings collapse to one resolved id.

**D-2. "Role" means two unrelated things.**
- Cognition `roles/*.py` (focus/judge/voice — execution units) vs an identity "role" (admin/user, or
  persona-as-role). **Naming collision, verified, zero shared code.**
  **Resolution:** keep the names distinct in the model: cognition role = `role://` (unchanged); identity role
  = a **grant/group** on a principal (OWUI's `Group.permissions`), never called a "role" in the registry to
  avoid the collision. Document the collision in `AGENTS.md` so it never gets "unified" by mistake.

**D-3. `voice` role vs `voice` persona attribute vs `voice` engine.** Three `voice`-named things (cognition
role `roles/voice.py` = tone; persona `voice`/`voice_description`; TTS engine). Adjacent to identity because
persona carries voice. **Resolution:** not an identity dup — flag only. Persona's voice fields stay on the
persona principal-attribute; the cognition `voice` role and TTS engine are downstream consumers, not identity.

**D-4. Two access authorities (operator token vs MCP posture tiers).** `bridge.py` operator token and
`remote.py` posture tiers both answer "may this caller act," computed independently.
  **Resolution:** both become **enforcement points reading the one AccessGrant table** (see §2). The map note
  says `_tool_gate` *MIRRORS* `remote.py:_is_allowed` "EXACTLY" (bridge.py:3430) — so they are *already meant
  to agree*; making the grant table the shared source removes the hand-mirroring (a drift hazard) entirely.

---

## 4. BROKEN / HALF-BUILT SEAMS

- **S-1. Agent identity is self-asserted + ungated.** `profile` is whatever the agent writes; the public
  channel webhook on the OWUI side is unauthenticated (owui-side-map §2). In a fused world where an AGENT
  principal can hold *grants*, self-asserted identity is a privilege-escalation seam. **Needs:** the principal
  row (identity-of-record) is authority; `profile` self-writes only the *operating-state* fields, never the
  grant-bearing identity. (Marks-as-flag, not a blocker for v1 internal fabric.)
- **S-2. No human-auth organ exists in the company at all.** Only the operator token (one human, one secret).
  Everything OWUI §7 (SCIM/OAuth/LDAP/trusted-header) is **net-new harvest** — nothing to dedup, but nothing
  built. This is the largest build, not a tweak. Honest status: VIEWER-kind auth is **planned, not present**.
- **S-3. `tim.json` vs `operator.json` are two records for arguably one viewer.** `tim` (handle, port 8783,
  transport channel) and `operator` (supervised session as-05711b1b, "room operator"). One is the human's
  surface, one is the operator *agent* acting for him — i.e. they are **different kinds** (viewer vs agent),
  which validates the two-kind model, but today the distinction is implicit/undeclared. **Needs:** explicit
  `principal_kind` on the reg (the discriminator §2 names; `fold_channels` half-derives it from `claude_pid`
  presence — make it explicit, fail-loud).
- **S-4. OWUI's own identity layer is mid-migration** (owui-side-map §7: `AccessGrant` table ⟷ legacy JSON
  `access_control` coexist; same dual-store as chats). **Harvest the grant TABLE, drop the JSON-field twin** —
  do not inherit the duplication into the company (the map explicitly warns this, §10 weak-list #2).
- **S-5. `supabase_principal` ≠ a principal *registry*.** It is an auth *flow* (login→JWT), not the typed
  identity store §2 needs. The seam: the AccessGrant table + principal rows must live in the company's own
  registry/store (FsStore or Supabase), with `supabase_principal` as the *authenticator* for agent principals,
  OWUI-auth as the authenticator for viewer principals. They are complementary, not the same layer.
- **S-6. The persona ↔ session ↔ principal relation is UNRESOLVED (open question, not a built thing).**
  §2 raises but does not settle which is base: persona is durable, session is ephemeral, so OWUI's
  preset→base direction may be inverted (persona→session) or the three may be orthogonal relations. Whichever
  it is decides where the grant-cap (`has_base_model_access`, owui §4) attaches — and if grants ever attach to
  the ephemeral side without a cap on the durable side (or vice-versa), a persona/session becomes an
  escalation path. **This is the relation to settle WITH Tim before personas carry grants** (the relationships
  are the content). The grant table itself is direction-agnostic, so this does not block the schema.

---

## 5. NEXT-STEP OPTIONS (for Tim)

**A — Depth/Understanding.** I verified identity is *thinner* than the brief assumed (self-asserted profile,
binary gate, no human-auth, no grant table). Before building, trace the **operator-token → `_tool_gate` →
`remote.py` posture** path end-to-end with live values, so we know exactly where the AccessGrant read slots
in without breaking the current operator path. (Lowest risk; the gate is load-bearing and live.)

**B — Dealer's choice (map the principal schema).** Draft the concrete `Principal` + `AccessGrant` row schemas
as company registry rows (kind axis, the resource_type extension, the persona-as-preset attribute), and show
how `fold_channels` gains its `principal_kind` discriminator — a paper schema to react to before any code.

**C — Tentative artifact (graft point).** Build the smallest real graft: make `_tool_gate`/`_tool_posture`
**read a grant table** (seeded with one operator grant = today's behaviour exactly), proving the binary gate
becomes a grant-row floor with zero behaviour change — then the richer model is purely additive rows.

**Recommendation: B then C.** The schema is the cheap correctable surface (Tim reacts to meaning), and C is the
reversible engine-graft that needs no face — it can proceed under minimize-gating once the schema reads right.
A is only needed if C surfaces a surprise in the live gate.
