# ④ THE CONTAINER — project_space fusion + the self-recording case study

*(Tim, 2026-07-02, via the fusion session. **v2** — revised after a three-critic gauntlet: adversarial refuter (facts verified against cvi_mine/ledger/engine, 14 defects), law-validator (verdict table vs AGENTS.md/NORTH-STAR/substrate laws, 8 amendments), completeness critic (13 gaps, 3 build-blocking). All folded below. Read NORTH-STAR.md first; ④ is the next movement: ① vector substrate, ② address surface, ③ the window, ④ the CONTAINER — who owns what, which project scopes what, members human+agent, the Keeper, the discourse layer.)*

## Plain-language: what it is (revised core)

The cloud "Concept-Vi" Supabase (snapshotted 2026-06-30; restored complete locally as **`cvi_mine`** — 466/466 tables, counts reconciled) contains a proven **project_space** system. ④ brings it home by one rule the reviews sharpened:

> **Transplant only the SPINE that has no local counterpart. Everything that overlaps an existing engine mechanism arrives as DATA into that mechanism — never as a second mechanism.**

- **SPINE (transplants — nothing like it exists locally):** spaces → projects → scopes → resources (+ project_content), space_members + project_members, keeper config, space-scoped token values, the generative type fan-out. New schema `container` beside `ledger`.
- **OVERLAPS (fuse as data into the engine's existing organ):**
  - cloud notice_board_posts (319) → **cc_board items** (`board://`, the engine's board — rule 3/one-source; cc_board's addressed-items+typed-edges shape is the stronger form);
  - cloud universal_types (16) + cascade_registry (10 handlers) → **registered types in the ONE registry** (the engine's registry philosophy is the home; the cloud's *generative fan-out* is absorbed as the registry's generate step — law 7 kept true by construction);
  - cloud intents/proposals/approvals/delegations → **the engine's decision://+marks+wire circuit** (approval = mark, per law 4; the container contributes the **space_id axis + the context tuple** to the existing circuit, not a second circuit). Migrated circuit rows arrive as decision records + marks (history preserved, provenance-stamped).

## Evidence base (numbers corrected per refuter)

- Container lived-in: 12 project rows, 86 scopes, **483 resources — predominantly discourse units** (document 209, note 67, pattern 61, comment 43, proposal 18, workflow 14, Q&A 16; plus a small non-discourse tail: scripts/folders/pointers ~6%). The container is the **about** layer; the ledger (`is` layer) stacks beneath — same distinction as the substrate's two halves, made same-law by the reverse index (below).
- Boards: 319 posts; **316/319** post types match registered universal_types (research=2, diagnostic=1 unregistered — the registry worked, with a small honest tail).
- Circuit: 107 intents (**73 zombie 'running'**) / 31 proposals / 18 approvals / 14 delegations. **33 intents + 22 proposals live in personal spaces** — curation must not orphan them (disposition below).
- Empty designed seams: uri_refs **0**/483, embedding **0**/483 — built before the ledger existed; ④ completes the sentence.
- Graphs, jobs not winners (each keeps its contextual job): containment → ltree (fold type_instance_edges' belongs_to=319/606 in); knowledge → **ledger.edge (720,461 as of 2026-07-02** — recount at build; the ledger is live and growing); lineage → **the 16 lineage rows** of graph_edges (branched_from 7, restarted_from 7, continues 2) are the `path://` ancestor; the other 38 rows (syncs_with 9, depends_on/depended_by 8, references, implements…) migrate as ordinary typed edges.
- Ledger side: `project` is bare text on **entry, run, coverage_findings** (not edge/embedding/symbol); 4 labels — company **161,835**, counterpart-design 1,743, platforms 1,028, claude-ds 331. ltree installed, 0 ltree columns.
- Engine side: `project://` and `code://` both registered-but-unresolvable in `resolve_address` (fail-loud raise). **`project://` has a PRIOR CLAIMANT** — registered for recollection's containment-graph lane (contracts/address.py:106–112). Reconciliation below.
- Sources: cvi_mine (the immutable reference; also the rollback source-of-record), the snapshot dir, the session memory corpus (`~/.claude/projects/-home-tim-repos-counterpart-design/memory/fusion-architecture-map.md`, `fusion-upgrade-laws.md`, `prototypes-are-the-spec.md`, `supabase-cloud-pull.md`), and the three review reports (this session's transcript).

## Identity (build-blocker resolved by decision)

- cvi_mine has 15 auth.users; the local stack has 4 test accounts; zero overlap. The container FKs outward ONLY to auth.users.
- **Resolution:** mint ONE canonical local Tim identity (the operator); build an explicit uuid rewrite map applied at migration (`created_by`/`owner_user_id`/`granted_by`/tuple `user_id` → Tim's local uuid where the cloud row was Tim's; the other 14 cloud users → curated-out-with-reason rows, their owned objects re-homed to the archive space below). Agent identities (keepers) are **project_members agent rows** (member_type='agent', agent_key) — NOTE (refuter #8): `space_members` is NOT polymorphic (FKs auth.users); only project_members carries agents. The case study binds Keepers at the **project** level accordingly; extending space membership to agents is a separate, additive, later proposal.

## Physical home + operational vehicle (build-blockers resolved)

- **Schema `container`** in the local Postgres beside `ledger` (public is occupied by the Face Pipeline/channel fabric — collision avoided by construction).
- **Vehicle, per engine conventions:** `0012_container.sql` (tracked, idempotent schema) + `ops/migrate_container_from_cvi.py` (curated transplant; idempotent upserts keyed on source uuid; resumable; emits a source↔target reconciliation report with denominators) + `tests/container_acceptance.py` (the gate). Every weld step lists its reversal; cvi_mine is the immutable rollback source; every curation writes an excluded-with-reason row (law 8).
- **Cross-table CHECK constraints become real FKs/triggers at rebuild** (found live: component_theme_specs' CHECKs query token_vocabulary — an integrity illusion that also broke pg_restore ordering).

## The weld (revised)

1. **`project://` — one scheme, both claimants served.** The container resolver provides BOTH faces: the container record (space/project/scope/resource, by key or ltree) AND the containment edges recollection's lane wanted — the same data, two projections. The registration comment in `contracts/address.py` is updated (registry-is-truth) as part of ④, coordinated on the board before the edit.
2. **`code://` — ② owns the seam; ④ consumes it.** ② is already cutting code-address resolution to the ledger. ④ does NOT edit that dispatcher independently; if ②'s general branch isn't landed when ④ needs it, ④ proposes the branch THROUGH the coordination file/board and ② reviews. (Refuter #13 resolved: ownership assigned.)
3. **Ledger binding, total backfill:** add nullable `project_id` FK columns (schema-additive) on `ledger.entry/run/coverage_findings`; **mint container project rows for ALL 4 ledger labels** (company, platforms, claude-ds minimally dressed; counterpart-design fully) so the backfill is 100%, not 1.1%.
4. **Pointers with their reverses (equal-and-opposite, declared per kind):** `project_resources.uri_refs` → ledger addresses, reverse `referenced_by` **composed at read** via the resolver (stored inverses only if profiling demands — the composed reverse IS legal under law 1). Sequence edges ship both names: precedes↔follows, depends_on↔depended_on_by, branched_from↔branched_to.
5. **Breadcrumbs (①'s decided format):** `project://` miss → "expected container.spaces/projects (:15432 container schema); previously cloud gctunhsuwpaxeatwlmuv spaces table (cvi_mine mirror); fix: ops/migrate_container_from_cvi.py --slice spine". `code://` miss → "expected ledger.entry/symbol for <project>/<path>; project not ingested — run ops/ledger_build.py --root <path> --project <label>".

## The case study (bootstrap de-circularized)

- **Phase 0 (before the container exists):** approvals ride the engine's EXISTING inbox/governance; the 10 laws land there as proposals; build decisions are recorded as the engine's decision:// records + marks from the first act.
- **First slice (verifiable alone):** `0012_container.sql` + the `project://` resolver + ONE row (`the-fusion`) + a live resolve round-trip. No data migration yet.
- **Back-write moment (right after first slice):** a one-shot ops back-write of the campaign's already-made decisions/findings (①②③④ DECIDED lists, the investigation findings) into `the-fusion`'s scopes, provenance-stamped to their source docs + this spec — the record is born complete, then new records flow live.
- One Space (Tim's) → projects: `counterpart-design` (subject; resources point at its 1,743 ledger addresses) + `the-fusion` (scopes: decisions/ ore/ sequence/ concepts/) + minimal rows for company/platforms/claude-ds (backfill targets).
- **The Keeper is a build item, not an assumption (refuter #14):** Keeper = a registered cognition ROLE per project; its context = territory composed over `project://<p>`; keeper_agent_config rows bind through the SAME context-resolution ladder as token_values (validator amendment 5: ONE resolution mechanism, two uses — keeper config and tokens are both instances of law 2).

## Migration dispositions (explicit; replaces "the 12")

| Organ | Cloud rows | Disposition |
|---|---|---|
| spaces | 55 | ~“Tim's space” + curated project spaces; 15 unnamed personal + duplicate default-projects → excluded-with-reason; ONE `cvi-archive` space minted to re-home orphans |
| projects | 12 | **9 migrate** (ci-processing, workshop-v2, vi-coder-config, dev-tracers, block-composition, project-system, universal-types, vi-chat, el-external-wizardry); bobs-cars + miro-integration + default-project → archive dispositions in cvi_mine (excluded-with-reason). the-fusion is minted new — **the 10th live project, first born at home** |
| resources / scopes / content | 483 / 86 / 41 | migrate with their surviving projects; provenance-stamped (source=cvi_mine + original uuid) |
| board posts | 319 | → cc_board items, typed from the registry (register `research`+`diagnostic` or mark unregistered-with-reason); provenance-stamped |
| intents/proposals/approvals/delegations | 107/31/18/14 | → decision records + marks in the engine circuit; the 33 intents + 22 proposals from personal spaces re-home to `cvi-archive` (nothing orphaned); 73 zombies marked `abandoned` with evidence; delegations re-keyed per identity map |
| universal_types + cascade_registry | 16 + 10 | → the ONE registry as registered types + the generate step (validator amendment 3: explicit federation, no second registry) |
| keeper configs / token values | 4 / 64 | rows migrate onto the one context-resolution ladder |
| graph_edges | 54 | 16 lineage rows → path:// ancestry (inert history until sessions resolve; provenance kept); 38 relation rows → typed edges with declared reverses |
| hosted_content | 62 | STAYS in cvi_mine for now — the surface story belongs to ③; condition-addressed: returns when ③'s direction lands |
| repo_knowledge_index | — | retired with honour (the ledger IS it) |

## The 10 laws (as proposals; two amended)

1. **State is composed, never hand-stored** — immutable rows are the source; composed state MAY be materialized as a DERIVED, re-runnable registry (never hand-edited): the registry is the fold. (Bridges registry-is-truth.)
2. Address + context = coordinate. 3. Every address accumulates faces. 4. **Propose→confirm for CONSEQUENTIAL acts** (scope: anything irreversible, contract-touching, operator-facing, or cross-session — routine in-scope build commits under rule 10 are not proposals); proposal = addressed record, approval = mark, execution = run:// trail; the circuit's own intents carry heartbeat/timeout → terminal states (zombie-proof by schema). 5. Self-scanning resident process. 6. `path://` first-class (ancestor: the 16 lineage rows). 7. ONE generative type registry (kept true by the fuse-as-data rule). 8. Honesty as trust layer. 9. Selection is an address-set. 10. Vocabulary as data.

## Verification (split per completeness #8)

- **④-core (surface-independent):** resolver round-trips for `project://the-fusion` + `code://company/...`; the Keeper ROLE answers a real question from composed territory; migration reconciliation report all-green with denominators; acceptance suite green; zombie terminal-states demonstrated; every curated exclusion carries its reason.
- **④-surface (gated on ③'s A/B/C):** the counterpart-design project rendered on the chosen surface, built on THAT surface's design system, desktop + mobile, design-critic + design-lint pass. FORM is half of done — ④-core alone is explicitly HALF.

## DECISIONS

- **(Tim, decided):** local home; organ+mine; one Space, two dressed projects; discourse-layer reading; laws as proposals; full charge.
- **(Folded by review, surfacing for Tim's awareness):** spine-transplant + fuse-overlaps-as-data (the anti-parallel rule); identity minting + archive space; 9-not-12 project migration; ② owns code://.
- **(OPEN — Tim):** ③'s A/B/C (④-surface waits on it; ④-core does not).

## Coordination

④ edits: NEW `container` schema, NEW ops/tests files, the `project://` branch + address.py comment (announced on the board first), additive ledger columns. ④ does NOT edit the code:// seam (②'s). Rule 10 obeyed: main, verify-first, no stranded branches. — the fusion session
