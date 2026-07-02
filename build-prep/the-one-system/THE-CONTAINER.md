# ④ THE CONTAINER — project_space fusion + the self-recording case study

*(Tim, 2026-07-02, via the fusion session — the charge: "full research, design, plan and orchestration execution, to full polish production with the latent principles and design architecture of the chaotic bolted-together prototypes." Read NORTH-STAR.md first; this is the next movement of the same campaign. ① made the ledger the vector substrate, ② made it the address surface, ③ is the window — ④ gives the universe its CONTAINER: who owns what, which project scopes what, members human+agent, the Keeper, and the discourse layer. It fills the socket the engine already reserved: `project://` is registered-but-deferred in `contracts/address.py`.)*

## Plain-language: what it is

The cloud "Concept-Vi" Supabase (fully snapshotted to disk 2026-06-30, now restored locally as the **`cvi_mine`** reference DB on :15432) contains a proven **project_space** system: Space → Project → Scope → Resource, each level addressed (URI + ltree), with polymorphic **members (users AND agents)**, a per-project **Keeper** with 4-level config inheritance, space-scoped design tokens, a **generative type registry** (register a type → tools/board-face/UI/capabilities auto-generate), and the **Intent→Proposal→Approval→Execution** circuit carrying `(user_id, actor_id, space_id, correlation_id)`.

④ transplants that **organ** (not the 466-table flood) into the one system, defines `project://` AND `code://` in the one resolver (the three-way weld: container → ledger body → cognition join in one motion), and proves it end-to-end with a **case study that records itself**: the fusion runs as the first project born in the unified container.

## The evidence base (what was mined — 5 deep investigations, 2026-07-02)

- **The cloud container was genuinely LIVED IN**: 12 real projects = the prototypes organizing themselves (ci-processing, workshop-v2, vi-coder-config, dev-tracers, block-composition, project-system, universal-types, vi-chat, el-external-wizardry, bobs-cars…); 86 scopes; **483 resources whose types are DISCOURSE units** (document 209, note 67, pattern 61, comment, proposal, workflow, question/answer) — the container is the **about** layer; the ledger is the **is** layer. They stack; no collision.
- **319 board posts whose types match registered universal_types** — the generative registry demonstrably worked (16 types registered; all 10 cascade handlers enabled).
- **The circuit really ran**: 107 intents / 31 proposals / 18 approvals / 14 delegations — but **73 intents are zombie "running"** (dead sessions, nothing watching). Fail-loud discipline is not optional here.
- **The designed seams sat EMPTY**: `project_resources.uri_refs` = 0/483, `embedding` = 0/483 — the pointer columns were built before the ledger existed. ④ completes the sentence.
- **Three graphs drifted into three JOBS** — don't merge tables, name the jobs: containment → ltree paths (fold `type_instance_edges` `belongs_to`=319/606 into it); knowledge → `ledger.edge` (579k, the winner); lineage/paths → `graph_edges` (54 rows are session lineage: branched_from/restarted_from/continues — a `path://` prototype all along).
- Full detail: the session memory corpus (`~/.claude/projects/-home-tim-repos-counterpart-design/memory/fusion-*.md`) + the cloud snapshot (`/home/tim/repos/Supabase/supabase/_cloud-snapshot/`, verified restorable) + `cvi_mine`.

## What moves / what doesn't

- **Moves (the organ, rebuilt clean under this repo's laws, schema-additive):** the spine (spaces, projects, project_scopes, project_resources, project_content), membership (space_members, project_members — polymorphic user|agent), keeper_agent_config (4-level inheritance), notice_board_posts + types, token_values (system|user|space|thread cascade), the intent circuit (intents/proposals/approvals/delegations + context tuple), universal_types + cascade_registry (the generative registry), graph_edges (as the path/lineage layer). The proven RPC shape (`create_project` as ONE atomic circuit: space+owner-member+project+token-seed) re-expressed as shared functions.
- **Does NOT move (stays queryable in `cvi_mine`):** the ci_* lineage (1/1/7/1/2 rows — its design already absorbed; archive), the 4 fake federation arms of all_type_registries, visual_dev/vi_coder text-keyed project systems (later movements, condition-addressed), miro_* (parked), bobs-cars (demo tenant), `repo_knowledge_index` (**retired with honour — the ledger IS what it wanted to be**), the ~15 unnamed auto-personal spaces + duplicate default-project rows (curated out at transplant; migrated data is CURATED, never bulk-copied).
- **Data migration of the 12 projects + 483 resources + 319 posts**: YES — they are the records of the prototypes' own development (case-study-shaped already). The-fusion becomes project 13, the first born in the unified home.

## The three-way weld (the core build)

1. **`project://` gets its resolver** — resolves to the container record (space/project/scope/resource by ltree or key), per `contracts/address.py`'s reserved scheme.
2. **`code://` gets its resolver** — the ledger's own scheme, currently unresolvable by the runtime (the universe cannot read its own body). Resolves to `ledger.entry`/`ledger.symbol` records.
3. **`ledger.*.project` (bare text) binds to the container** — promoted to a real scoping key referencing the project row (schema-additive: add the FK column alongside, backfill, never break).
4. **`project_resources.uri_refs` finally points** — a repo-project's resources point at ledger addresses (pointed-at, never copied).

## The case study (the proof, self-recording from act one)

One Space (Tim's; Tim as owner-member, Keepers as agent-members) with two projects:
- **`counterpart-design`** — the subject repo (already in the ledger: 1,743 entries). Resources = pointers to ledger addresses; the surface and the Keeper resolve the same addresses; project_type uses the seeded-token types.
- **`the-fusion`** — the case study. Scopes: `decisions/` (immutable records, state composed from decision_take/update/retract marks) · `ore/` (mined capabilities as findings with gold_likelihood/built_twice/overlap marks) · `sequence/` (typed precedes/depends_on edges linking decisions→runs→findings — the AI's paths, replayable, the template for every future fusion) · `concepts/` (vocabulary as it's discovered). Its notice board receives the campaign's posts. The Keeper's context = territory over `project://the-fusion`.
- Every consequential build step flows through the propose→confirm circuit it is building. Backlog items land condition-addressed (explicit return-when), never parked silently.

## The 10 emergent laws (the latent architecture, land as PROPOSALS — Tim's yes fires each)

1. State is composed, never stored (rows immutable; meaning resolved at read).
2. Address + context = coordinate (every read is "resolve this address AT this coordinate" — extends the North Star's coordinate-space frame).
3. Every address accumulates faces (fact/interpretation/disposition/geometry/page; one resolver serves all).
4. Propose→confirm is the universal write law (proposal = addressed record, approval = mark, execution = run:// trail — structural provenance, the review layer this no-developer system never had).
5. The universe self-scans as a resident process (drift → auto-proposed marks).
6. `path://` first-class (ordered typed walks; replayable, embeddable, promotable — graph_edges' lineage rows are the ancestor).
7. One generative type registry (register a kind → scheme resolution, MCP verbs, board/panel face, embedding policy, edge kinds, keeper behaviours — universal_types+cascades are the working ancestor; how forecasts/theorems/documents arrive with zero new systems).
8. Honesty as the trust layer (denominators, excluded-with-reason, honest-empty on every view).
9. Selection is an address-set (what the operator sees/filters/selects = an addressed context record the Keeper resolves against; saveable ways-of-looking).
10. Vocabulary as data (names mined→proposed→confirmed→enforced; ends session naming drift; tmp_edgevocab is the ancestor).

## PROACTIVE IMPROVEMENTS to fold in (standing directive: Tim can't ask for what he can't see)

- **Zombie-proof the circuit**: intents get heartbeat/timeout → terminal states; migration marks the 73 zombies `abandoned` with evidence (honest history, never silent deletion).
- **RLS done properly** on the transplanted organ (the cloud had SELECT-only asymmetries, a WITH CHECK(true) hole, and `hosted_content` RLS disabled "temporarily" — fix at transplant, not inherited).
- **One function → two faces** for every container capability (create/query/dashboard/compose as shared functions projected to MCP + UI), per the North Star.
- **ltree everywhere it belongs**: the local ledger installed ltree but uses text paths — adopt the container's ltree discipline for container paths; evaluate (don't assume) whether ledger paths should follow.
- **Embedding discipline stays local**: the cloud's vector(384) single-dim is retired; the container's resources embed through the one multi-space store; absorb the cloud's *event-driven auto-embed trigger pattern* (queue/pg_net), not its geometry.
- **The two vector homes finish unifying** (FsStore → ledger.embedding read-path = movement ①; ④ builds on ①'s seam, never adds a third home).

## Verification (by use, never by claim)

- The resolver resolves `project://the-fusion` and `code://company/...` end-to-end; the Keeper answers a real question from its territory; the surface renders the counterpart-design project (real browser); every migrated count reconciles source↔target with denominators.
- **FORM is half of done** (rule 9): container surfaces built on the design system, design-critic + design-lint gates, native desktop AND mobile.
- Adversarial verify-jury on each criterion; drift_radar + floor_walk sweep before any "done"; **Tim's sight-verify is the terminator** — the loop never declares itself done.

## DECISIONS

- **(Tim, decided)**: fusion home = local Docker stack; organ + mine (not the flood); one Space, two projects; the discourse-layer reading of resources; the anatomy verdicts above; the 10 laws proceed as proposals; full charge given for research→design→plan→orchestration→execution→polish.
- **(OPEN — coordination)**: where ④ slots against ①→②→③ order (natural: ④ can start now — its schema work is additive and collision-free; its surface slice should land inside ③'s direction once Tim calls A/B/C; my lean matches the North Star's C→A: the-fusion project board + the counterpart-design project view ARE strong candidates for ③'s "narrow powerful slice").
- **(OPEN — Tim)**: ③'s A/B/C call itself.

## Coordination note (for the interface + cognition sessions)

④'s build surface: NEW schema (container tables) + NEW resolver branches (`project://`, `code://`) + additive columns on `ledger.*` — no collision with the wire/self-build stream or the ①② cutover seams; it CONSUMES ②'s canonical addresses and ①'s search function. I follow rule 10 (main, verify-first, no stranded branches) and will announce build starts on the board. — the fusion session
