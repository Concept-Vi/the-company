# ④ THE CONTAINER — Completion Criteria

*(The verifiable definition of done, lane by lane. Every criterion is verified BY USE — a real call, a real query, a real render — never by code existing. Tim's sight-verify is the terminator; no loop declares itself done. FORM is half of done on any operator-facing surface. Per ③'s decision (B then A): lanes L1–L7 ARE phase B, the substrate-hardening; L8 is the window payoff, built once on proven ground.)*

**Sources of truth:** THE-CONTAINER.md v3 (the synthesis + laws) · organ-studies/*.md (the designs) · cvi_mine (immutable source-of-record for migrated data) · AGENTS.md (the constitution).
**Standing rules for every criterion:** fail-loud with breadcrumbs on every miss · every migration count reconciles source↔target with denominators · every curation writes excluded-with-reason · every weld step lists its reversal · schema-additive only · commits to main, verify-first, per-criterion.

## L1 · SPINE — first slice
- [x] C1.1 `0012_container.sql` applied idempotently twice in a row on a scratch DB with identical result (schema container: spaces, projects, scopes, resources, members).
- [x] C1.2 `resolve_address("project://the-fusion")` returns the container record + its containment edges, live, through the ONE resolver. An unknown project fails loud with the decided breadcrumb text.
- [x] C1.3 `territory_for("project://the-fusion")` composes the project leg (identity + relations + status), absent legs noted-absent, prose renders without raw addresses.
- [x] C1.4 All 4 ledger labels have container.projects rows; `ledger.entry.project_id` backfill = 100% (161,835 + 1,743 + 1,028 + 331 rows verified by count query, denominator printed).
- [x] C1.5 PROJECT_ROOTS is read from container.projects.root_path; `platforms` (the live defect) now opens files. The old dict is commented out with the breadcrumb, not deleted.
- [x] C1.6 **The back-write moment**: the campaign's decided record (①–④ DECIDED lists, the 7 studies' findings, the 11 laws) lands in the-fusion's scopes as addressed resources, provenance-stamped to their source docs; queryable via project://the-fusion/decisions/…
- [x] C1.7 create_project runs as one atomic circuit (space-if-needed → project → membership → keeper binding → ledger label reservation); a failed step rolls the whole circuit back; the result is provenance-stamped.

## L2 · IDENTITY
- [ ] C2.1 principal / principal_auth / membership / delegation tables live; the operator seed migration mints exactly ONE operator row (Tim; t.geldard@ primary login attached; v.i@ attached to the VI AGENT principal per Tim's correction) + the standing acts-for delegation Tim→vi.
- [ ] C2.2 The OPERATOR_USER_ID remap runs shadow-then-flip: the remote gate's decisions proven identical under the principal-table read before authority flips; the env-default read path commented out with breadcrumb.
- [ ] C2.3 The 15 cloud users land per the map: 1 operator + 1 vi-agent + curated humans; the 7 no-email users archived excluded-with-reason; the uuid rewrite map applied to every migrated created_by/owner/granted_by/tuple column (spot-verified on 10 sampled rows against cvi_mine).
- [ ] C2.4 `may(principal, verb, address)` / `access_of(address)` exists as ONE function answering both faces; the MCP face and a UI read return the same answer for 5 test principal×address pairs.
- [ ] C2.5 The 13 duplicate delegations collapse to one confirmed grant with 13 evidence entries; the L5 grant lands with its window; delegation ceiling actually bounds a live guard() call (demonstrated with a test principal denied above its ceiling).

## L3 · REGISTRY
- [ ] C3.1 types/ + cascades/ registries discovered; `create(kind='type', spec)` gates (a trivial data_schema is REFUSED with a teaching error), writes the file, commits, rediscoveres — proven by registering one new test type end-to-end and then deleting it (the fan-out retracts).
- [ ] C3.2 generate_all(type) fans out with per-cascade honesty {ok|error|skipped:reason}; the completeness ledger holds a generated_from↔generates edge pair per artifact; the drift test fails when an artifact is removed by hand.
- [ ] C3.3 The 9 sound cloud types land as type files and regenerate their artifacts (tool rows, board face, address template) — counts reconciled vs cvi_mine's cascade output where applicable.
- [ ] C3.4 The 7 hollow types carry the hollow-types investigation's dispositions (RECONSTRUCT with de-facto schemas / FUSE with mapping recorded / HOLD with the missing evidence named) — each disposition traceable to its evidence, surfaced to Tim, none silently imported.
- [ ] C3.5 Law 11 proven: a type declares states+transitions in its socket; an illegal transition on an instance is refused fail-loud; a resolver read varies by state (one demonstrated case).
- [ ] C3.6 Suite.type_info() serves the registry + fan-out state to both faces from one function.

## L4 · GRAPH + PATH
- [ ] C4.1 edge_kinds/ registry live (id/directed/inverse/face/endpoints/behavior); ledger.edge writes validate kind against it fail-loud; the 44 existing kinds registered with face tags; spelling collisions (part_of/part-of) normalized with count-verified rewrite.
- [ ] C4.2 Reverses composed at read: a query for imported_by returns the composed inverse of imports (verified on a known pair); NO reverse rows stored (the ~8 cloud reverse rows dropped on landing, their forward rows verified present).
- [ ] C4.3 The landing plan executed with reconciliation: graph_edges 54 → ~40 real edges (test rows quarantined, reverses dropped — each with excluded-with-reason); type_instance_edges 606 → ~190 knowledge + 95 lineage (belongs_to 319 verified derivable from fields before dropping); denominators printed.
- [ ] C4.4 path/path_step live; ONE cascade run auto-derives its path (steps = legs, via = graph edges, payloads = run:// addresses); path://<id>/<ordinal> resolves; path_replay materializes the walk.
- [ ] C4.5 The fusion campaign itself exists as a path:// record (kind=fusion) with the build's major steps as ordinals — the case study's sequence/ scope is THIS.
- [ ] C4.6 Paths embed under space='paths'; a similarity query between two known paths returns sane ordering.
- [ ] C4.7 The projection contract emits paths[] alongside clusters/edges/spine/ghosts; counts-including-zero.

## L5 · CIRCUIT
- [ ] C5.1 The mark-backing shadow: marks written through the ONE API land in both stores; reads proven identical over 100 sampled marks; authority flips; the file-only path commented out with breadcrumb.
- [ ] C5.2 Intent lifecycle = marks only: claim(lease) / heartbeat / suspend / terminal; compose_state derives pending/running/lapsed/terminal — a test intent with an expired lease composes to LAPSED with no reaper process running.
- [ ] C5.3 The historical pour: 107 intents / 31 proposals / 18 approvals / 14 delegations land as rows+synthesized marks; **the 73 zombies compose to lapsed on arrival**; the 1:1 approval join reproduces as the take-mark view; counts reconciled vs cvi_mine.
- [ ] C5.4 An approval take-mark is retractable before a claim references it, and refused after (both cases demonstrated).
- [ ] C5.5 A CONFIRM-class action from an agent principal raises + surfaces to the inbox; the operator's resolve (and only that) releases it; the executor's lane never writes the resolved field (write-path test).
- [ ] C5.6 Deadline behavior: a SURFACE-class proposal past its deadline proceeds-by-default with a recorded note; a CONFIRM-class one escalates (both demonstrated with short test deadlines).

## L6 · BOARD
- [ ] C6.1 scope and author land as addresses on the item shape; list(scope=project://…) filters; the derived authored_by index answers reverse lookups without O(n) scan (timed on the 690).
- [ ] C6.2 8 new item_type rows (observation, milestone, design, task, blocker, cognitive_guide, research, diagnostic) with states+transitions honoring the legacy open/resolved/closed.
- [ ] C6.3 The 319 posts land losslessly: uuid ids kept, long-tail content keys preserved (spot-verify the 35-key tail on 5 sampled posts vs cvi_mine), resolver-names → history entries, project_id → scope. The stale JSONB NOT migrated; one provenance note written.
- [ ] C6.4 The Postgres projection regenerates from the file store; deleting the projection and re-deriving reproduces identical counts.
- [ ] C6.5 item.filed / item.transitioned events emit on the channel layer; a subscribed test agent wakes on one.
- [ ] C6.6 A pin is a view-record edge: pinning an item on one board-view does not pin it on another (demonstrated).
- [ ] C6.7 The board is NOT the inbox: a board item does not appear in inbox_lanes; an explicit escalation does.

## L7 · KEEPER
- [ ] C7.1 The ladder slot-kind lives in resolver.py: longest-prefix-on-address resolution proven with a 3-rung test (universal → project → scope), walk-up on absence, fail-loud legible absent below.
- [ ] C7.2 The 4 cloud config rows land as rungs and resolve correctly at their depths; keeper capability flags GATE the governed verb whitelist (a keeper denied a verb its rung excludes — demonstrated).
- [ ] C7.3 The keeper cast fires for mode='keeper'; per-project rung specialization changes one role's framing without touching any file (write rung → different resolved prompt — demonstrated).
- [ ] C7.4 `keeper_answer("project://counterpart-design", question, token)` returns a real answer composed from live territory (the project's actual ledger data), the envelope returned enriched with a trail; the SAME function serves the MCP face and an HTTP face.
- [ ] C7.5 The persona record resolves into the keeper's prompt; a project-level persona rung overrides it; removal restores the global one.

## L8 · ③-A THE WINDOW (gated on L1–L7 green + Tim's go)
- [ ] C8.1 The full multi-axis window renders the substrate: containment clusters, typed edges, spine, ghosts, paths overlay, zoom (scale:* rungs), time, provenance-to-conversation — per the projection contract, on the chosen surface.
- [ ] C8.2 the-fusion and counterpart-design render as living projects: board, decisions, resources, keeper — the case study visible through the window it built.
- [ ] C8.3 Selection is an address-set shared with the Keeper: select nodes → ask → the answer is scoped to the selection (law 9 of the upgrade laws, demonstrated live).
- [ ] C8.4 FORM: built on the design system, design-critic pass, design-lint green, native desktop AND native mobile, honest denominators on every view.
- [ ] C8.5 Tim's sight-verify. **This criterion can only be marked by Tim.**

## Campaign-level (always-on)
- [ ] CA.1 Every lane's migration emits a reconciliation report (source count → landed count → excluded-with-reason count, sums matching) archived under the-fusion/ore/.
- [ ] CA.2 drift_radar + floor_walk sweep green before any lane is declared closed (no stranded work, no unmounted capability, no stale decision).
- [ ] CA.3 The fusion path:// record gains an ordinal per lane closure — the case study records itself as it goes.
- [ ] CA.4 Nothing in cvi_mine is deleted or mutated, ever — it remains the immutable source-of-record.
