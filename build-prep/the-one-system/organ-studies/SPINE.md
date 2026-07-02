# ORGAN REBUILD STUDY — THE SPINE (the container hierarchy)

*(④ the-one-system · fusion session, 2026-07-02. Method: both sides worked out — IS / WORKS / REACHING — then the ONE rebuilt from the many. Evidence: cvi_mine (cloud mirror), _cloud-snapshot/db/schema.sql, /home/tim/company, recollection, counterpart/design substrate. Verbatim study by the SPINE investigator; verified refs at foot.)*

**DISCOVERY (Observed):** a fifth articulation already exists — `THE-CONTAINER.md` (v2, same day) is a fusion-session spec for exactly this weld. Verified independently; treated as prior art, not source of authority.

## (1) SIDE A — the cloud container hierarchy

### What it IS (Observed)
- **`spaces`** (schema.sql:38694): `space_type` CHECK personal|project, `space_key`, `space_path ltree`, `space_address text`, decorators/categories/tags, taxonomy, purpose, status, owner_user_id. CHECKs: personal spaces nameless, project spaces named. Comment: "Personal space = Vi's memory about user. Project spaces = actual work/collaboration." 55 rows: 14 unnamed personal, ~11 duplicate default-project, `space_path` NULL almost everywhere (one populated), `space_address` NULL everywhere, taxonomy {} everywhere.
- **`projects`** (38851): space_id FK, project_key, `project_path ltree NOT NULL`, project_type (design/meta/operations/research), keeper_agent, notice_board jsonb (legacy), entry_points (all []), parent_project_id (all NULL), project_address. 12 rows. Paths like `root.ps.conversation_intelligence.ci_processing`, `root.ps.bobs_cars.bobs_cars` (doubled leaf). project_address populated on ONE row (`project://block-composition`). keeper_agent inconsistent in kind: text keys on two rows, a raw uuid on one.
- **`project_scopes`** (39158): scope_key, scope_path ltree, scope_type (folder|registry), scope_address populated for two projects in TWO grammars (`ci-scope://…`, `project://…`), parent_scope_id all NULL, denormalized resource_count (stale). 86 rows.
- **`project_resources`** (39122): 483 rows. resource_type: document 209, note 67, pattern 61, comment 43, proposal 18, workflow 14 … discourse, not files. Carries resource_address, TWO ltree columns (resource_path AND address_tree, identical in samples), uri_refs[] AND ref_uris[] (both empty ×483), embedding vector(384) (NULL ×483), content_hash NULL, version/version_history, decorators heavily used ({@pattern,@verified,@v2-kernel}…), depth_level all 0, parent_resource_id.
- **`project_content`** (39083): 41 rows — a second, thinner content lane that never merged with resources.
- **`project_spaces` VIEW**: SELECT … FROM spaces WHERE space_type='project'.
- **members**: project_members polymorphic (user|agent + agent_key); space_members FKs auth.users only.

### How it WORKS (Observed)
- **create_project** (10158): one atomic circuit — space (path = parent||key) → owner space_member → project (project_path = space_path||key) → owner project_member → seed_space_tokens.
- **get_project_dashboard** (16647): composes project+space+stats+scopes+board+members+recent in one jsonb; emits `'project_address', 'project://'||key` **computed at read, ignoring the stored column** — the address is a convention, not a stored fact.
- **query_project_spaces** (20467): filter resources+content by space_key/decorator/type — decorators are the one richly-populated, actually-used query axis.

### REACHING (Observed structure → labeled Inference)
- Dormant address columns in 3+ grammars = wanted one addressed universe, had no SCHEMES contract/resolver — reaching for contracts/address.py.
- uri_refs/ref_uris 0/483 + embedding 0/483 = pointing/finding sockets for a body that didn't exist yet — reaching for the ledger.
- The ci_* twins ARE the design iteration (34929–35032): addresses/paths become NOT NULL, description NOT NULL, one clean scheme + path per level — the second draft tightened exactly the map's mandatoriness.
- parent_* + depth_level present at every level, used at none: recursive containment designed, unexercised.

## (2) SIDE B — the engine's project/address model

### What it IS (Observed)
- **ledger**: run.project text NOT NULL, entry.project text; entries carry path, node_type, parent(text)+depth, address = code://<project>/<path> (symbols ::<sym>). Counts: company 161,835 · counterpart-design 1,743 · platforms 1,028 · claude-ds 331. ledger.edge 720k+: calls 493,246, **contains 108,343**, imports 65,001, references 38,921, generated-by 1,403 …
- **contracts/address.py:145**: SCHEMES = (run,cas,blob,vec,ui,code,skill,context,guide,session,cap,board,clone,mind,exchange,file,project,vi-vision,decision,image,extraction). `project://` registered ~106–112 for recollection's containment lane — "register-but-defer".
- **PROJECT_ROOTS** (ops/ledger_interpret.py:31): hardcoded dict label→root. **Defect: `platforms` (1,028 entries) is absent** — the dormant proto-projects-table, already drifted.
- **ingest lineage** (mcp_face/tools/ingest.py:18-19,46): project/session/round required on every record, bare text, default "company".
- **territory_for** (runtime/territory.py:97, ~138): project:// noted "no content-resolver yet — identity degrade-clean (absent)".
- **Recollection** (recollection/src/db.ts:777-780): projectNodeId(project)='project://'+project; seeded relation types include contains/is_contained_by (project>session>exchange); stamped inverses, deterministic edge ids, idempotent.

### WORKS (Observed)
ledger_build walks a root (--root scans another repo into the SAME ledger), keys by rel-path, mints code://…::sym, derives parent/depth/contains — **containment derived by scan, never authored**. Interpret opens originals via PROJECT_ROOTS. Everything resolves through the ONE resolver or fails loud.

### REACHING (Inference from observed)
- project mandatory-but-bare = an FK with no table; label load-bearing (161k rows) before the entity existed.
- project:// claimed three times (SCHEMES, recollection, territory), deferred three times with the same honest note: no store owns the record yet.
- NORTH-STAR states it: "Multi-project is simple: each project is just an address at the project level."

### The FOURTH articulation (counterpart/design substrate) (Observed)
registry/address-registry.json: address=relpath, contains as prime parent-edge, equal-and-opposite referenced_by stored, derived-never-placed, registry-is-truth; "the substrate is the local instance of the COMPANY layer's address-resolution, per project (root dir = the project)" — the project IS the root, implicit.

## (3) COMMON CORE · UNION'S EDGES · IMPLIED-BUT-ABSENT

### Common core
1. **A project is an addressed container node with a stable text key** — both sides independently minted the identical form: cloud computes `'project://'||project_key`; engine returns `project://<name>`. Two AIs, no coordination, one grammar — the strongest evidence in this study.
2. **Containment is the prime axis**, encoded four ways for one relation: ltree (A) · parent+depth+contains edges (B, 108,343) · contains/is_contained_by (recollection) · contains parent-edge (design substrate). Scale ladder everywhere: space⊃project⊃scope⊃resource ≈ project⊃session⊃exchange ≈ project⊃dir⊃file⊃symbol.
3. **Typed content units live AT addresses under the container**, with typed cross-reference fields.
4. **The registry-is-truth impulse**: ci_* made address+path NOT NULL; B has SCHEMES + one resolver; the design repo derives its whole map.

### Union's edges
A only: the space level (ownership, personal-vs-project, members human+agent), scopes as named/curated sub-containers distinct from derived directory containment, keeper binding, decorators/taxonomy as query axes, the atomic create circuit, dashboard composition, resource versioning, per-space token/theming seeds.
B only: content at scale (164,937 entries vs 483), grammar below the file (::<symbol>), containment derived by scan, the provenance axis (generated-by → exchange:// — transcripts are ROOT), runs (the scan itself addressed+temporal), one resolver + fail-loud, territory composition, embeddings that exist (76k).
Design repo only: types-by-convention, derived wayfinder projection, project-as-root (no project row at all).

### Implied-but-absent
1. **A projects TABLE the ledger's bare labels FK into** — PROJECT_ROOTS is its fossil (already drifted); A's projects table is it without the ledger under it.
2. **A working project:// resolver** — A stored addresses nobody could resolve; B registered and deferred twice.
3. **The pointer join**: A's uri_refs (0/483) waited for B's ledger addresses; B's ledger had nothing authored-about pointing at it. The ABOUT and IS layers, built apart, each with an empty socket shaped like the other.
4. **One grammar across container levels**: A drifted into 4+ schemes; B had nothing between project://<name> and the file.
5. **Space/ownership on the engine side** (absent entirely) and **embedding/search on the container side** (the vector(384) that never got a pipeline).

## (4) THE REBUILT ONE — the single spine

### The ontology (answered)
- **Space** = the ownership/membership frame — who holds this and who may act. Not where content lives.
- **Project** = the unit-of-world — a top-level address (NORTH-STAR verbatim). The join of ALL lanes: ledger label, recollection scale node, container row, design-repo root.
- **Scope** = a named, AUTHORED sub-container (curated shelf: decisions/, patterns/). Explicitly distinct from DERIVED containment (directories/sessions): both are `contains` edges, differing by **provenance (authored vs derived)**, never by mechanism.
- **Resource** = an authored content unit (the ABOUT layer). **Ledger entry** = a derived content unit (the IS layer). Same law (addressed, typed, edged), two provenances.

### Structure (schema-additive, one source, fail-loud) — schema `container` beside `ledger`
```
container.spaces      (space_id, space_key UNIQUE, kind, owner, status, created_at, …)
container.projects    (project_id, space_id FK, project_key UNIQUE, project_type,
                       root_path,          -- absorbs PROJECT_ROOTS (nullable)
                       keeper_role,        -- a registered cognition ROLE id
                       status, phase, description, entry_points, created_at, …)
container.scopes      (scope_id, project_id FK, parent_scope_id FK, scope_key, scope_type, description, …)
container.resources   (resource_id, project_id FK, scope_id FK, resource_key, resource_type,
                       address TEXT NOT NULL UNIQUE,   -- the ci_* lesson: mandatory, one grammar
                       content jsonb, content_hash, version, version_history jsonb,
                       decorators text[], tags text[],
                       source_system, source_uuid,     -- transplant provenance
                       created_by, created_at, updated_at)
container.members     (project_id, member_type user|agent, principal, role, …)
```
Additive to the ledger: nullable `project_id uuid` FK on ledger.entry/run/coverage_findings; the bare text label stays.

### One address grammar
```
project://<project-key>                        the project node        (container.projects)
project://<project-key>/<scope-path>           an authored container   (container.scopes)
project://<project-key>/<scope-path>/<key>     an authored unit        (container.resources)
code://<project-key>/<path>[::<symbol>]        a derived unit          (ledger.entry/symbol)
exchange://<sid>/<i> · session://<sid> · file://…    provenance/containment lanes (recollection)
```
`<project-key>` is the ONE join across all lanes. Legacy schemes retire to an address_alias column. Parse declared once in contracts/address.py.

### ltree vs text (answered)
**Text canonical address = identity. ltree = a derived index, never identity.** A's disease was ltree-as-authored-identity (NULL/stale/doubled). B and the substrate prove the cure: containment derived, re-runnable. container.* may carry ONE ltree column regenerated from parent FKs by a fold (derive-never-place); the ledger keeps parent/depth/contains, also derived.

### Mechanics (one function → MCP + UI)
1. **Resolver — both claimants served with one dataset**: resolve_address("project://…") returns the record PLUS its containment edges (exactly what recollection registered the scheme for). Fail-loud with ①'s breadcrumb format.
2. **territory_for grows its project leg** (fills the declared absence at territory.py:138).
3. **PROJECT_ROOTS dies as code, lives as data** (container.projects.root_path) — mechanically fixes the platforms gap.
4. **The dashboard becomes territory**: get_project_dashboard's composition = the UI face of what territory_for serves the MCP face — write once, project twice.
5. **create_project stays one atomic circuit** (A's proven mechanic) + keeper-role binding + ledger label reservation; provenance-stamped, no silent success.

### Data landing
| Existing | Lands as |
|---|---|
| 4 ledger labels | 4 minted container.projects rows; backfill project_id — 100% coverage by construction |
| Cloud 12 projects | 9 migrate, 3 excluded-with-reason; source_uuid kept |
| 86 scopes / 483 resources / 41 project_content | migrate under their projects; project_content FOLDS INTO resources (parallel lane, same organ); addresses rewritten to the one grammar, old forms kept as aliases |
| Empty uri_refs | finally point at code://, exchange:// addresses; referenced_by composed at read |
| Dead embedding column | not migrated — resources embed through the ONE pipeline into ledger.embedding |
| Recollection's project:// nodes | keep minting; key now FK-checkable; resolver serves its lane |
| counterpart/design registry | unchanged — root binds to root_path; census can pour in as code://counterpart-design/... |
| Decorators | migrate verbatim — the one lane A actually used; a query axis on both faces |

### Genuinely NEW
The projects table as FK target of everything · authored-vs-derived as a provenance flag on one contains mechanism · keeper as a registered role resolved through territory · PROJECT_ROOTS as a projection of the registry.

## (5) EACH SIDE'S PARTIALITY
**A stopped because it was built before there was anything to contain** — sockets for a ledger that didn't exist; no SCHEMES/resolver so each session minted its own scheme; no derive step so every map decayed. Ontology right, physics wrong (placed, not derived).
**B stopped because its job was extraction, not ownership** — needed a partition label, not an entity; register-but-defer was the CORRECT discipline, and this rebuild pays exactly that debt. Physics right, ontology deferred until multi-project became real (per NORTH-STAR, it now is).
**Recollection**: the project is a scale node whose meaning is its containment edges. **Design substrate**: the project can be implicit (root=project) if its interior map is derived and true.

**Key refs:** schema.sql spaces:38694 projects:38851 project_resources:39122 project_scopes:39158 ci_*:34929–35032 create_project:10158 get_project_dashboard:16647 query_project_spaces:20467 · contracts/address.py:106-112,145 · ops/ledger_interpret.py:31 · ops/ledger_build.py docstring · mcp_face/tools/ingest.py:18-19,46 · runtime/territory.py:97,138 · recollection/src/db.ts:740-820 · registry/address-registry.json.
