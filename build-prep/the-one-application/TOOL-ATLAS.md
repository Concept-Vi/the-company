# THE COMPANY MCP TOOL ATLAS — the honest map of every tool

*Tim 2026-06-20: "needs one investigating the actual mcp tools, there's a lot of them." This is the dedicated deep pass over the ACTUAL ~66 company MCP tools — run with a CRITICAL-COMPARISON / default-to-skeptical mentality (findings kept coming back "it's right" when they weren't; this pass hunts what's WRONG). Every claim below is grounded — file:line, live-test result, or on-disk evidence — and tagged Observed / Inferred / Verified per Tim's evidence law.*

**This file DOUBLES as the FACE 3 (tool-face) human-meaning layer.** The `human_name` + `human_description` per tool ARE the embedded, pleasant descriptions the tool-face renders. The merge-ready block is the clearly-marked §MERGE section at the bottom.

**Counts (66 UNIQUE tools; the source investigation had 74 entries — 8 tools were investigated in two families each and are presented ONCE here, deduped):**
- **~40 REAL-and-working** — wired, fired on real data, behave as described.
- **~16 NEVER-WIRED / BROKEN / DEAD** — never fired in production, or return empty silently, or have no consumer.
- **~15 OVERCLAIMING** — they *work* but the docstring/commit/name lies (stale embedder, false-green routing, "verified by use" that wasn't, a safety floor that isn't wired). **This bucket is cross-cutting** — an overclaimer is often also in the "working" set (e.g. `corpus` works but its docstring names a dead embedder). It is the bucket Tim cares most about: *real vs aspirational.*

> CONVERGENCE (do not re-describe — these are the truth):
> - **COMMISSION-COMPLETION-REGISTER.md** — the WHAT-must-all-be-true; §CAPABILITIES ledger is where unused powers get stacked.
> - **TOOL-FACE-BUILD.md** — the build spec for the surface this atlas feeds (the `/api/tools` door, the `tool-card` archetype, the safety gate / `explicitly_denied` list).
> - **CHANNEL-LOOP-BOARD.md** — the collective loop-prep; "the engines are built and have no FACE" headline; the capability inventory this atlas is the tool-half of.

---

# ★ CRITICAL SUMMARY — what is REAL vs ASPIRATIONAL (clustered by ROOT CAUSE)

The broken/overclaiming tools are NOT 16 independent failures. They collapse into a **handful of root causes**. Fix the cause, fix the cluster.

## ROOT CAUSE 1 — the cwd-relative-discover bug (3 tools return EMPTY, SILENTLY)
**`dials`, `operator`, `panel`** all return `{...: []}` on the live MCP face while their registries are POPULATED on disk.
- **Mechanism (Verified, reproduced):** these tools call a `*Registry().discover()` whose default `dirs=` is a RELATIVE path (`('dials',)`, `('operator_memory',)`, `('verdict_panels',)`). The MCP server process cwd ≠ repo root → it discovers ZERO. Proven: from `/tmp` the same `discover()` returns `[]`; from repo root it returns the real rows (2 dials, 29 operator rows, 1 panel).
- **The fix already EXISTS and was never propagated:** the projection author discovered this for `bindings` and hardcoded an ABSOLUTE `os.path.join(ROOT,'bindings')` (documented why). That same one-line fix → these four tool faces.
- **★ THE SINGLE MOST DANGEROUS ONE: `operator`.** Its docstring instructs an agent "read op=rules FIRST" — Tim's 29 standing rules (record_expansively, no_silent_failures, verify_before_claiming…). On the MCP face it returns `[]`, so the agent proceeds **rule-blind**, behaving as if Tim has NO standing rules. And the empty is SILENT — which itself violates `no_silent_failures`, one of the very rows that fails to load.
- **NOT in this cluster (precision matters):** `flows` is sometimes lumped here — it is NOT cwd-dark. Family-4 VERIFIED all 8 flows discoverable. `flows` is "never-fired + browser-unreachable" (Root Cause 4), a different defect.

## ROOT CAUSE 2 — the reasoning-model budget gap (every `run_*` empties on cloud/reasoning models)
**`run_role`, `run_items`, `run_reduce`(mode=role), `run_draft`, `run_draft_items`, `run_cascade`** all default `max_tokens=256` (512 for run_reduce). A reasoning model fills the whole budget with thinking and returns EMPTY content → `FabricError 'empty content from model'`.
- **Verified by raw curl on the exact `client.complete` path:** `deepseek-v4-flash:cloud` @64 tokens → empty; @2000 → `{'kind':'animal'}` (works). The resident 4B brain works at low budget only because its reasoning is minimal — so "the default was tested, the models work" is the WRONG conclusion.
- **★ THE FALSE GREEN:** the 2026-06-20 routing fix makes cloud REACHABLE (routes a non-`/` model to `:11434`) but does NOT raise the budget → every cloud generate still empties at the default. "Concurrent cloud cognition works" is **unverified for any reasoning model.** Reachable ≠ produces content.
- The build ALREADY HIT this (empty `kind` strings in `run_draft_items`) and mislabelled it "small-model sensitivity" — same systemic gap, under-diagnosed.

## ROOT CAUSE 3 — the `mark` governance bypass (VERIFIED by execution — security)
**`mark`** lets ANY unprivileged agent write `decision_take`/`decision_retract` that flips a decision pending↔decided with NO operator attribution.
- **Verified (ran it):** `SUITE.mark('decision://global/...','decision_take', by='rogue-subagent')` returned a record with no raise, no attribution check; `decision_inbox` then read `state='decided', decided_by='rogue-subagent'`. A retract flipped it back. The ONLY gate is `mark_type ∈ registry` (a type-validity check, NOT an attribution check).
- **Root cause (not "the gate gates wrong"):** a GOVERNANCE-class event (deciding) is registered as an ordinary `mark_type`, so it rides the telemetry append-path while the system elsewhere treats deciding as operator-only. The two halves are incoherent.
- The bridge's defenses are HTTP-side ONLY: `/api/tools/invoke` DENIES `mark` (it's in `explicitly_denied`), `/api/territory/write` has a dry_run guard. The raw MCP `mark` tool bypasses all of them. The `#1b` operator-token seam is DESIGNED but NOT WIRED (the code itself flags this). `decision_retract`'s docstring claims it "inherits the gated floor" — the floor it claims does not yet exist.

## ROOT CAUSE 4 — the browser-unreachable chain-library (MCP-only, no `/api` route)
**`flows`, `run_cascade`, `save_cascade`, `list_cascades`, `routines`, `get_results`, `node(op=propose/apply)`** are MCP/agent-only — there is NO `/api` route, so the operator CANNOT run/save them from the surface.
- This is THE headline known gap. The on-canvas graph (build nodes, wire, run) IS browser-wired via `/api/*`; the chain-LIBRARY above it is not. `list_cascades` is touched by the bridge ONLY to draw a precedence *diagram* (the operator can SEE cascades as a picture but cannot RUN one).
- `node(propose/apply)` (the self-grow-a-step-type path) is likewise MCP-only.

## ROOT CAUSE 5 — built-twice (Tim's `built_twice` mark-type — name it)
**`cc_channel` vs `channel_act`** are TWO named-channel-with-membership registries on TWO different leaves (`cc_channels.py` → `_channels/<id>.json` vs `session_channels.py` → `agent_sessions/channels.jsonl`), each with its own create/add/remove/archive. The TRANSPORT halves genuinely differ (cc_channel = live-port injection; channel_act = durable fabric structure) — but the named-channel-REGISTRY half is a parallel re-implementation of one concept. Exactly Tim's concern: decide whether one subsumes the other.

## STANDALONE FLAGS (don't fit a cluster)
- **`models` is NOT an MCP tool** (misnomer in the task list). No `mcp__company__models` exists. The MCP path to the model list is `capabilities(section='models')`; inventory/swap is the `company` CLI + `/models` skill.
- **`list_by_type` was MISCLASSIFIED** as a decision/board/channel tool — it is the canvas node-type port-graph query. Catalogued in GRAPH/BUILD where it belongs.
- **`reduce_rule_names`** belongs to COGNITION (serves `run_reduce`), not decision/board/channel — catalogued in COGNITION.
- **`capability` (singular) is DATA-EMPTY.** The registry is binary-discovered (spawns the live `claude` binary, ~14s) and its population wiring is `🟡 lead-verify-queued` — never verified to populate. `describe()` returns `total=0` on an unwired Suite. Distinct from `capabilities` (plural, the Company's own what-exists map, which works).
- **Built-and-abandoned signatures:** `cc_voice` (fired exactly twice, in one minute, on commit day; nothing since), `cc_attachments` (zero bindings ever while ~10 channels run live), `cc_gate` (no `.data/gates/` dir exists — never fired; "verified by use" was unit-only), `edit_role`/`delete_role` (superseded by `create`; edit likely never fired as an edit).
- **The "decided" state shown by `decisions` is not proof the OPERATOR decided** — see Root Cause 3; any `mark()` caller can have set it.

## ONE RECONCILED CONTRADICTION (the skeptical pass found a self-contradiction)
**`run_cascade` / `save_cascade`:** the COGNITION investigation said "NEVER-used in production"; the GRAPH/FLOWS investigation found REAL run records (`.data/store/ref_history`, many `cascade-*` records dated Jun 9-10). **Reconciled truth:** cascades WERE run on real data during a dev/eval window (Jun 9-10) — NOT "never" — but never in steady production, AND browser-unreachable. Both passes were partly right; the evidence-backed claim (records found) wins on "ran," the production-loop claim wins on "not steady."

---

# THE PER-FAMILY CATALOG

*Each tool once, in its best-fit family. Cross-family tools carry an "also relevant to" pointer. Layers: **human name · human description** (Tim-facing, the FACE-3 copy) — **what it REALLY does** (Verified behaviour) — **concrete uses** — **ever-used** — **critical flags**.*

---

## FAMILY 1 — RECALL / MEMORY
*The corpus-discovery pillar + session-fabric recall + the marks detection layer. The Company's durable memory of itself.*

### `corpus` — Company memory
**Human:** Search and read the Company's durable memory. Ask a plain-English question and get the records nearest in meaning — or browse, filter, open one, or find related ones.
**Really does (Verified live):** five ops over one event log. `query` embeds your question (LIVE pplx `:8007`, 2560-dim) and ranks the pplx vector index — ran live, returned `runtime/corpus.py` 0.623, `mcp_face/tools/corpus.py` 0.545. `list`/`find` are read-time projections over the one log filtered to `corpus.record` (3220 on disk, dedup-on-read). `read` opens a record by address. `neighbours` returns the semantic field around a unit. `rerank=True` uses the live jina-v3 `:8008`.
**Concrete uses:** ask-the-codebase ("how does X work") rendering top `code://` files with scores; render a memory-record card; relational constellation panel around a unit.
**Ever-used:** WIRED + USED. Same Suite methods serve the FE bridge; one of only 3 tools in the remote MCP audit log (10 calls). Corpus is populated (3220 records, 3032 pplx vectors, 8 spaces).
**Flags:** ★ DOCSTRING STALE — docstring says "BGE-M3 @ :8001" but config resolves to LIVE pplx `:8007` (`:8001` is down). Code correct, prose lies. ★ DEFAULT-SPACE TRAP (Verified) — `query` with NO `space=` reads the unspaced pplx layer (0 vectors) → "index is EMPTY" every time; you MUST pass `space=`. Two embedding layers coexist (2830 bare/BGE dead-weight + 3032 pplx; query reads only pplx). `read` returns the capture DIGEST, not raw file text (docstring honest).

### `ingest` — Feed the memory
**Human:** Pour files (a folder or a list) into the Company memory so it can answer questions about them — the "load the codebase" feeder.
**Really does (Verified by reading the method):** walks roots (sorted, skips hidden/venv/binaries, `.py/.md/.ts/...`, 6000 chars/file), requires `roles/repo_digest` (RAISES if missing), content-hash incremental skip (a changed file re-ingests with no `force`), fans the digest role over files (the swarm), captures+embeds each digest keyed `code://<path>` into the space (default `repo`). Bounded `max_files=50/call`.
**Concrete uses:** point the FACE at a new dir → becomes queryable; re-ingest a changed file (hash detects it); bounded full-repo sweep via repeated calls.
**Ever-used:** WIRED + USED. 645 repo-space pplx vectors + 659 repo records ARE ingest's output.
**Flags:** RAISES if `repo_digest` missing (fail-loud, correct); capture fails loud if embedder down (`:8007` up, so works). Deletions out of scope (a removed file's record goes stale — flagged). GPU docstring "bge-m3 resident" is STALE (it's pplx `:8007`). No live re-run done (spends GPU + commits).

### `capture` — Capture to memory
**Human:** Process N things through one lens and SAVE each result as a durable, searchable memory record — the sink where at-scale AI output lives instead of being thrown away.
**Really does (Verified):** resolves a role, fans it over N units (the axis-inversion engine), persists per-unit records via the SHARED `Suite.capture_corpus` seam (the ONE write+embed path BOTH the MCP tool AND the bridge use — closed a real prior bug where the bridge wrote but never embedded). Enforces a LINEAGE GATE: `session/round/project` REQUIRED or RAISES. Writes records first, then embeds embeddable ones into their space.
**Concrete uses:** comprehend documents under a lens (populates worldview/principles spaces); persist a batch of analyses; a FACE "process these N things" button.
**Ever-used:** WIRED + USED. 3220 records across 8 projections; `flows/ts_backfill.py` calls it; the bridge route calls it.
**Flags:** lineage is a non-optional gate (cold agent must supply all three). ★ The embed-text derivation is FLAGGED needs-tim/unvalidated — it stringifies the whole structured output as the embeddable text; whether that's lens CONTENT vs JSON noise is unverified (embedding QUALITY for structured captures is unproven). `source_address` >200 chars or with newlines RAISES.

### `find_relations` — Inversion finder
**Human:** "Same principle, different subject." Given an item, returns things NEAR it in one space (shared principle) but NOT near it in another (different topic) — the cross-pollination discovery query.
**Really does (Verified live):** anchors on the item's OWN persisted per-space vectors (NO re-embed → no embedder dependency on the query side), runs kNN in both spaces, THRESHOLDS each to true neighbours (cosine ≥ `min_score` default 0.5 — the correctness pivot; without it "far" contains everything and the result is always empty), then `relations = near − far − {item}`. Ran live on `interpret_file.py` (near=principles, far=topics) → 8 real relations.
**Concrete uses:** discovery surface ("shares a principle with these but diverges in topic"); cross-pollination finder; relational FACE panel.
**Ever-used:** WIRED. Served by the FE bridge + the MCP tool; 162 items have both principles+topics vectors. Live test returned 8.
**Flags:** ★ DOCSTRING CONTRADICTION — the Suite docstring says "not on the MCP face / not in RHM_VERBS" but it IS the `find_relations` MCP tool (stale self-description). DATA-COVERAGE LIMIT — only works on items in BOTH named spaces; the usable principles↔topics anchor set is small (162). `min_score=0.5` is a HARDCODED default (flagged: should be registry-projected). Reads only the pplx layer.

### `mark` — Leave a mark / make a take
**Human:** Add a typed note onto something — a comment, reaction, favour, coherence finding, OR a decision take/retract. The single write verb behind the whole marks layer.
**Really does (Verified by execution):** `SUITE.mark(target, mark_type, **fields)` → `store.append_mark`. The ONLY gate is `mark_type ∈ registry` (11 registered types incl. `decision_take`/`decision_retract`). Append-only — a target accrues a mark THREAD.
**Concrete uses:** comment/reaction/favour on a corpus unit; record a coherence mark (ai_fingerprint/overlap); DECIDE a decision (write `decision_take(value=label)` on `decision://global/<id>`).
**Ever-used:** WIRED + USED. 74 marks on disk across 8 types (decision_take 28, comment 13, overlap 13…).
**Flags:** ★★ VERIFIED GOVERNANCE BYPASS — see Root Cause 3. Any unprivileged agent can flip a decision with no operator attribution; the bridge denies `mark` over HTTP but the raw MCP face does not; the `#1b` operator-token seam is designed-not-wired. ★ ROOT CAUSE — a governance event modelled as an ordinary mark_type. Requires the mark_type be a discovered registry file (author via `create(kind='mark_type')` first). *Cross-family: also the write side of the marks layer in DECISION/BOARD.*

### `marks` — Read marks / findings
**Human:** Read the typed marks on something — every mark on a target, every mark of a kind across targets, or the legacy coherence findings at an address. Read-only.
**Really does (Verified):** `by='target'` → `marks_for` (gold-likelihood profile composed on read, never stored). `by='type'` → `marks_by_type`, REGISTRY-GATED fail-loud (a typo'd type RAISES instead of silently `[]`). `by='findings'` → `store.findings_for` directly (no Suite wrapper — flagged seam).
**Concrete uses:** read a decision's take thread; cross-target denoise surface (`mark_type='ai_fingerprint'`); decision ledger (`decision_take` → 28 marks).
**Ever-used:** PARTIALLY. `target`/`type` live over 74 marks. ★ `by='findings'` returns `[]` for EVERYTHING — there is NO `findings.jsonl` on disk (its only writer, `coherence_detect.py`, has never run). Dead-data path.
**Flags:** `by='type'` gate is genuinely enforced (clean). `by='findings'` bypasses the Suite gate to the store (flagged architectural asymmetry). The danger is on the `mark` WRITE twin, not here.

### `inspect_address` — Inspect address
**Human:** Read any addressed content back — a past run's output, a content blob, a skill's instructions, a context blob. The canonical "open this pointer."
**Really does (Verified live):** `resolve_address(store, address, turn_id)` — the engine's ONE canonical read path. RAISES on an unresolvable/unknown address (never silent); RAISES on a bare name (a ctx key, not an address). Ran live on a real `run://` → returned the full record dict.
**Concrete uses:** open a corpus record's full payload; inspect a past role/cascade run output; resolve a `skill://`/`context://` blob.
**Ever-used:** WIRED + USED. The SAME read path `run_role/run_items/capture/cascades` use internally — load-bearing engine primitive.
**Flags:** Read-only, fail-loud, no model call. One of the CLEANEST tools — no defects found. The correct counter-example to the family's silent-empty bug (it RAISES instead of returning empty). *Cross-family: also in PROJECTION/RESOLVER.*

### `sessions` — Session fabric (read)
**Human:** Read the fabric of every Claude Code session this machine has run — the fleet roster, a session's mailbox, its compaction timeline, live events, and a meaning-search over transcripts. Pure read.
**Really does (Verified live):** six ops over Suite registry methods. `list` → 1120 registered sessions (fold_errors=0, real states incl. supervised-live). `describe` → row + mailbox. `inbox` → mail since a cursor (non-destructive). `timeline` → compaction boundaries (launchable points). `watch` → supervisor events (404 on disk). `search` → corpus hit ⨝ live registry row + a ready-to-run `session_post` command (auto/semantic/lexical). Carries real readonly ToolAnnotations.
**Concrete uses:** the fleet view (1120 sessions w/ state/title/cwd); catch-up handle from a meaning-search; pick a fork point from the timeline.
**Ever-used:** WIRED + USED. 1120 sessions, 404 supervisor events, `op='list'` verified live; supervised-live sessions present (active now).
**Flags:** `watch` honest-empty if supervisor down (it's UP `:8771`). `search` semantic needs `:8007` (up; declares `mode_used` if it falls back). Well-guarded, live data, honest empties — no defect.

### `session_post` — Session fabric (write)
**Human:** Send a message/intent to another Claude Code session — deliver into a live one, wake a closed one, or consult forked copies (optionally N in parallel, optionally at a past point-in-time). The fabric's one consequential write.
**Really does (Verified — consumer exists + has run):** the tool NEVER spawns a process — it validates, resolves the routing verb (auto→deliver if live, wake if closed, else queue), and APPENDS a durable intent to the mailbox. The actual deliver/wake/consult is performed by `session_supervisor.py` (108KB, live at `:8771`, responding NOW with /spawn /inject). It HAS acted: 404 `agent_sessions.*` events (60 spawned, 127 turn); 5 intents on disk came from this tool.
**Concrete uses:** coordinate with a peer session; ask N forked consultants without touching the original; revive + hand work to a closed session (incl. time-travel `at='compact:N'`).
**Ever-used:** WIRED + USED + CONSUMED. NOT the inert "writes mail nobody reads" case. (Much of the 27-row traffic is test/probe-flavoured; real production volume is modest, but the path is genuinely closed.)
**Flags:** the tool's SUCCESS (mail appended) is NOT delivery — it's an INTENT; completion = the consequence event appearing in `sessions(op='watch')` (docstring honest, agent must verify). Hard dependency on the supervisor being UP (it is). `from_session` is REQUIRED as the reply path (a bare label silently breaks reply routing). `copies>3` (env cap) refused loud (cap is flagged-hardcoded). No live post performed (would spawn real processes).

### `session_recall` — Recall (semantic + lenses)
**Human:** Recall what was said/decided/asked in a session by MEANING (not grep), and detect a long session's DRIFT from its earlier selves. Eight lenses: find, decisions, open_loops, catch_up, timeline, directives, spin_up_points, drift.
**Really does (Verified live):** resolves the session ('self' → this session's transcript), combines a STRUCTURAL scanner (who/when/tokens/boundaries) with a SEMANTIC index (embed `:8007`, rerank `:8008`, both live). `decisions` = query-expansion + max-cosine merge. `drift` = pre-vs-post-last-compaction semantic presence (<0.55 cosine = drifted). Ran `find` live → 3 hits with scores.
**Concrete uses:** "what did we decide about X?"; catch up after stepping away; detect post-compaction drift with a launchable recovery point.
**Ever-used:** WIRED + USED. The recall index is real + populated (`.data/recall-index/`, one is 80MB). Both services live. Exposed as a first-class skill too.
**Flags:** bridge-free (embeds/reranks via Company services; a lens raises `{ok:False}` if either down — honest). The resolution/drift/open_loops heuristics are explicitly HINTS not proof (cue-vocabulary, regex — false pos/neg). Index must be BUILT for a session first. `spin_up_points` hardcodes `FABLE_MODEL='claude-fable-5'`.

### `context` — Live context (read / compact)
**Human:** Drive the in-session /context and /compact commands headlessly on a live session — read its context-window usage, or trigger a compaction with an optional focus.
**Really does (Verified code + live consumer):** `op='read'` injects `/context` via HTTP to the supervisor and captures the usage breakdown; `op='compact'` injects `/compact` (+focus) and waits for the compact boundary. Capture is bulletproofed against /watch backlog via arrival-time filtering. Fails teaching-loud if the supervisor is unreachable.
**Concrete uses:** check a long session's context budget without entering it; headless compaction with focus before overflow; a FACE context gauge.
**Ever-used:** WIRED, consumer LIVE, but LIGHTLY USED. Supervisor up + has /inject; lead-verified per the module. Only works on a supervised-live session. No persistent on-disk artifact proves repeated use (unlike corpus/sessions). Real but situational.
**Flags:** HARD DEPENDENCY — needs (a) supervisor up AND (b) target supervised-live. `op='compact'` is CONSEQUENTIAL (irreversible context loss except the summary). "lead-verified" is the module's own assertion — NOT re-proven this pass (no live compact triggered; it mutates a real session). No usage ledger → production frequency unverifiable.

---

## FAMILY 2 — DECISION / BOARD / CHANNEL
*The operator's decision inbox + the company noticeboard + the cross-session channel fabric. (`mark`/`marks` are the write/read of the marks layer — catalogued in RECALL above; `list_by_type`/`reduce_rule_names` were misfiled into this family and are catalogued in their real families below.)*

### `decisions` — Decisions waiting for you
**Human:** The strategic decision-cards waiting for YOU to decide on — each by its human name + the recommended option; never an id or code. The canonical "decisions waiting" inbox the RHM brain answers from.
**Really does (Verified):** iterates the file-discovered DecisionRegistry, composes FAST mark-state per row (`compose_state` over `marks_for(decision://global/<id>)` — GPU-free, no embed), returns `{waiting, decisions:[{name, recommended}], already_decided}`. State RESOLVES from the latest `decision_take`/`decision_retract` mark, never stored. Shares the EXACT `decision_inbox()` call the FE inbox pill renders → brain and screen agree by construction. Operator-law honoured: only name + recommended leave; the id stays server-side.
**Concrete uses:** "what decisions are waiting for me?"; powers the decisions-waiting pill count; the RHM walks the operator through one open decision.
**Ever-used:** WIRED + used by two faces. Called by the bridge `/api/decisions` AND this tool. Created 2026-06-19 as "THE COHERENCE FIX" because the brain had no MCP verb for the canonical registry and was mis-reaching `list_surfaced`.
**Flags:** ★ READ side coherent + complete, but the WRITE side it implies is the UNGATED `mark` path (Root Cause 3) — a "decided" shown here is NOT proof the OPERATOR decided it. Returns ONLY name+recommended (by design no id) — an agent that must ACT on a specific decision can't get the address from this tool (resolve via `territory`/`decision://` separately).

### `cc_board` — Company noticeboard
**Human:** File / list / pick-up / move-along typed items ABOUT the Company itself — request, issue, tip, guide, idea — that agents (and Tim) raise and a channel works through a lifecycle.
**Really does (Verified):** `file` validates type/source/links against registries, writes a `board://<id>` markdown record. `list`/`get`/`transition` (moves along the type's DECLARED legal states; fail-loud on illegal). `types` → the registries. PROBED: item_types has 5 (request/issue/tip/guide/idea), source_types 1 (claude_code), board_edges 4. Works end-to-end (not a skeleton).
**Concrete uses:** an agent files a found bug; the lead lists open items to pick up; move an item along its lifecycle.
**Ever-used:** WIRED into the address system — `board://` is a real scheme the cognition resolver dispatches; `territory.py` relations leg calls `cc_board.relations`. Has a CLI face. Genuinely cross-wired.
**Flags:** source_types has only ONE entry (claude_code) — the multi-source breadth the docstring implies isn't populated. `file`/`transition` are WRITES — confirm the remote gate restricts cc_board to read ops remotely (the JSON `allowed:null` is ambiguous). No silent no-op (missing item RAISES BoardError, caught → `{ok:False}`).

### `cc_channel` — Message live Claude Code sessions
**Human:** Discover other LIVE Claude Code sessions and inject a message straight into their running conversation (reply pushed back, no polling); plus manage named Claude-Code channel groups.
**Really does (Verified):** `list` → live sessions (pings supervisor/ports). `send` → push to the target's port OR supervised /inject; opens a reply thread. `broadcast` → loops send over targets under one group thread. `mail` → the message/reply log. The NAMED-CHANNEL half (create/add/remove/archive) reads/writes `_channels/<id>.json`. The live-injection transport into hand-launched sessions.
**Concrete uses:** coordinate with a peer live session; discover who is alive; group broadcast to several live sessions.
**Ever-used:** WIRED — the transport behind the cross-session-fabric skill + the company-channel MCP server (the `<channel>` injection tags). Remote posture 'design', `allowed=['send']`. Actively used for the fabric mesh.
**Flags:** ★ BUILT-TWICE (Root Cause 5) — its named-channel-registry half duplicates `channel_act`'s on a different leaf. Send to a closed session impossible (live-only; fall back to `session_post` wake/consult). `broadcast` catches per-target errors and continues — partial delivery returns per-target `ok`; the caller MUST inspect `results[]`.

### `channel_act` — Act on the session fabric (write)
**Human:** The single WRITE verb for the cross-session fabric structure — create/grab channels and gatherings, work the roster, post a message, set coordination mode, run the lifecycle. CQRS twin of `channels`.
**Really does (Verified):** every action is a durable append on `agent_sessions/channels.jsonl` (`fold_channels` reconstructs state). `post` direct mode fans one mail-intent per member (live → `deliver`, rest → `queue`); conducted mode sends ONE intent to the coordinator. It NEVER wake/spawns — the supervisor service alone acts on deliver-class (the no-spawn FLOOR is genuinely upheld). `mode`/`promote`/`disperse`/`archive` are lifecycle.
**Concrete uses:** spin up a durable working channel; message a channel (fans to members or coordinator); promote a momentary gathering that proved durable.
**Ever-used:** Backed by `session_channels.py` (fully implemented). Writes deferred remotely (NOT exposed remotely, same posture as `mark`); live locally; drift-guarded by an acceptance test.
**Flags:** ★ BUILT-TWICE counterpart to `cc_channel` (Root Cause 5). When the agent-session registry fold is absent, membership ops fail teaching-loud (good) BUT `post` then marks every fan `queue` — a degraded mode where a "live" member silently never gets delivered. Writes-deferred remotely but fully live locally (same exposure asymmetry as `mark`).

### `channels` — Read the session fabric
**Human:** The pure-read view of the cross-session fabric — list channels & gatherings, describe one with member statuses, read a channel's exchange history, or see a session's connection history.
**Really does (Verified):** PURE READ. `list` → `fold_channels` with filters. `describe` → channel + `member_statuses` (composes DECLARED awake/listening with DERIVED busy/closed + a live supervisor probe; `status_source` reports which sources answered — a down supervisor is REPORTED, never hidden). `history` → posts + their mail. `edges` → a session's connection history + a ready-to-run follow-up handle. Empty results honest.
**Concrete uses:** see what channels exist; "what did they work out?" (history); see who a session has talked to (edges + follow-up handle).
**Ever-used:** WIRED + exposed remotely (posture 'safe', read). CQRS read-twin of `channel_act`.
**Flags:** No defects — genuinely read-only, honest-empty, surfaces a down supervisor rather than dropping it. One of the cleanest tools. `describe`'s live supervisor probe (default on) makes it non-trivial latency + supervisor-dependent despite being a "read" (`probe_supervisor=False` is the escape hatch).

### `inbox` — Chief-of-staff inbox (triaged)
**Human:** The operator's surfaced-action inbox, bucketed into lanes — live escalations needing you, items already resolved-for-you (audit), and batched themes to handle in one sitting.
**Really does (Verified):** reads `self.inbox.list()` (the SAME store `list_surfaced` reads), filters out test-origin items (reports the excluded count — nothing hidden), buckets `live_escalations` (resolved is None) / `resolved_for_you` / `batched` (>1 of an action). A RE-SHAPING of the surfaced-action inbox, NOT a separate data source.
**Concrete uses:** "what needs my attention?"; audit what was handled-for-you; see themes to batch.
**Ever-used:** WIRED — `inbox_lanes` over the same store `list_surfaced`/`resolve_surfaced`/`edit_role` write to.
**Flags:** ★ NAME COLLISION — THREE distinct "inbox" surfaces: `inbox()` (chief-of-staff lanes), `list_surfaced` (flat rows over the SAME store), `sessions(op='inbox')` (the cross-session mailbox). Plus `decisions` is a FOURTH "waiting for you" concept. `inbox()` + `list_surfaced` read identical data, shaped differently — a candidate consolidation. No params → can't drill (switch to `list_surfaced(sid=)`).

### `list_surfaced` — Surfaced-action / build-approval inbox
**Human:** The self-growth approval queue — items the system surfaced for you to resolve (a build/role/flow dispatch, a review). Each carries a default + a resolution. NOT the strategic "decisions waiting" set.
**Really does (Verified):** `self.inbox.list()` with shaping — `sid=` returns one item's full payload (fail-loud if unknown); `status=` filters by lane; `unresolved_only=True` → live escalations; default → concise rows newest-first. Same store as `inbox()`.
**Concrete uses:** drill one surfaced build/role item; see live escalations; browse the approval queue.
**Ever-used:** WIRED — items surfaced here by `edit_role`/`delete_role`/`node propose`/etc.; `resolve_surfaced` (operator-only, OFF the MCP face) resolves them.
**Flags:** ★ Overlaps `inbox()` (candidate consolidation). ★ Historically the SOURCE of the coherence bug `decisions` fixes — the brain reached here for "decisions waiting" and leaked s-coded ids; the docstring now carries a ★ NOT-the-decisions-inbox warning (corrective, but still confusable for a cold agent). `resolve` correctly NOT on this face (operator-only) — this gate IS sound (unlike `mark`'s).

---

## FAMILY 3 — COGNITION / MODELS
*The model-firing primitives (run one / fan many / join / pipeline) + the registry-inspection reads. **The whole `run_*` set shares Root Cause 2 (the budget gap).***

### `run_role` — Run one specialist
**Human:** Fire a single cognition role (a specialist with a prompt + a validated output shape) over one input, and save the result to read back or feed downstream. The 1-to-1 generator.
**Really does (Verified):** mints a turn_id, resolves address-valued inputs, fires `client.complete` (schema-constrained decode), persists to `run://<turn>/<role>`, emits one `op.run` record. The SAME fire path the swarm uses.
**Concrete uses:** fire 'focus'/'verify_lens' on one utterance → validated JSON; the single-fire block `run_reduce(mode=role)`/`run_cascade` call internally; fire one describe-role on one corpus unit.
**Ever-used:** ENGINE fn heavily wired (100+ refs). The MCP TOOL itself: exercised by tests; the build's own honesty note lists it among "never used the company MCP in production loops until today."
**Flags:** ★ BROKEN at default budget for reasoning models (Root Cause 2) — `max_tokens=256`; reasoning fills it, content empty → FabricError. PROVEN via curl. ★ The 2026-06-20 routing fix is a FALSE GREEN (cloud reachable but still empties at default). The resident 4B works at low budget only because its reasoning is minimal.

### `run_items` — Fan one specialist over many (MAP)
**Human:** Run ONE role across N inputs at once (the MAP of map-reduce). Each input becomes one run at an addressable slot. The workhorse of the concurrent mine.
**Really does (Verified):** real axis-inversion — fans the role over N units CONCURRENTLY through the same pool + VramGate + barrier as the swarm. Per-unit resilience: a processing failure goes to `.failed`, good units still return. Writes each output to `run://<turn>/<role>/<i>`.
**Concrete uses:** fan a describe-role over 39 corpus candidates; produce the N map-outputs `run_reduce` joins; classify/extract a batch.
**Ever-used:** ENGINE fn wired into `capture`, `run_draft_items`, tests. The build flagged "nothing calls run_items yet" — the primitive exists; no production LOOP points it at a real target.
**Flags:** Same budget gap (Root Cause 2 — each unit is a `run_role` fire @256). ★ Does NOT get the 2026-06-20 cloud-routing fix — pins the resident endpoint, so a cloud model passed here is MIS-ROUTED. The MAP can return many empty/failed units silently-into-`.failed` (the batch "succeeds" mostly-failed).

### `run_reduce` — Join many into one (REDUCE)
**Human:** Combine a set of map-outputs into one result — by a synthesis role, a deterministic rule (count/concat/first/tally), or by clustering near-duplicates. The JOIN half of map-reduce.
**Really does (Verified):** reads N addresses back (fail-loud on missing, stable order), then `mode='role'` (composes into one input, fires a reduce-role), `mode='rule'` (a PURE named callable — count/concat/first/verdict-tally/`tally-by:<field>`, single-source via `resolve_reduce_rule`), or `mode='cluster'` (embeds + greedy cosine groups). rule/cluster run NO model.
**Concrete uses:** `tally-by:label` over N classified candidates → histogram; `mode='role'` synthesize N notes; `mode='cluster'` = "which are the same."
**Ever-used:** Tests cover all modes. `mode='cluster'` flagged built-but-never-fired in a production loop.
**Flags:** `mode='role'` inherits the budget gap (default 512, still empties on heavy reasoning) AND pins the resident endpoint (no cloud routing). `mode='cluster'` silently needs the embedder resident.

### `run_draft` — Run a throwaway specialist (no registration)
**Human:** Fire a one-off specialist defined inline for a single job, without saving it to the registry — keeps the registry clean.
**Really does (Verified):** renders the inline spec, loads it from a TEMP module, discovers it via the SAME RoleRegistry, `rmtree`s the tempdir, then the IDENTICAL fire path as `run_role`. NEVER written to `roles/`, NEVER committed (git-verified byte-identical before/after).
**Concrete uses:** "classify this one thing once" without polluting the registry; a bounded one-off extract; prototype a role before committing it.
**Ever-used:** ★ NEVER used — ZERO tests, ZERO production callers. In-process build-time check only. (Build report: "all built, MCP-callable, no loop points them at a real target.")
**Flags:** No committed test (regression coverage absent). Inherits the budget gap. DOES get the routing fix (can reach `:11434`) but the budget gap negates it for reasoning models.

### `run_draft_items` — Fan a throwaway over many
**Human:** The MAP version of the throwaway specialist — run an inline, unregistered role across N inputs. The primitive for "classify these N candidates once."
**Really does (Verified):** tempdir render/load/discover/rmtree (no commit), then the SAME fan as `run_items`.
**Concrete uses:** "classify these 39 candidates once" without registry pollution; a one-shot batch extract; throwaway MAP feeding a reduce.
**Ever-used:** ★ NEVER used — ZERO tests, ZERO production callers. The build observed the empty-output symptom HERE first.
**Flags:** No committed test. ★ The build ALREADY HIT the budget gap here (empty `kind` strings at 64 tokens) and mislabelled it "small-model sensitivity" (Root Cause 2 under-diagnosed). Does NOT get the cloud-routing fix → cloud model mis-routed.

### `run_cascade` — Run a saved pipeline end-to-end
**Human:** Run a previously saved multi-step pipeline (a "cascade") from start to finish, threading each step's output into the next. The declarative cousin of flows (flows = code; cascades = data).
**Really does (Verified):** loads the saved decl (fail-loud if unknown), rides the EXISTING primitives (no 2nd engine), dispatches step kinds (retrieve/check/jury/panel/reduce/items/role), threads `run://` addresses with explicit cardinality, persists + indexes each step, injects a real corpus retrieve_fn.
**Concrete uses:** run a saved map→reduce→synth recipe in one call; `ask-the-codebase` (retrieve → reduce_synth); a 4-step decompose→expand→ground→synth pipeline.
**Ever-used:** ★ RECONCILED (the one cross-pass contradiction): cascades WERE run on real data Jun 9-10 (`.data/store/ref_history` holds many `cascade-*` records: develop_option, eval_classify, verify_lens…) — NOT "never." But during a dev/eval window, NOT steady production, AND browser-unreachable. 8 cascades saved.
**Flags:** ★ BROWSER-UNREACHABLE (Root Cause 4) — no `/api/cascade` route; the bridge calls `list_cascades` ONLY to draw a precedence DIAGRAM. ★ CLOUD-BLIND — pins the resident endpoint; a cloud per-step model fails loud downstream (the multi-endpoint router N2 is unbuilt; the 2026-06-20 fix is NOT mirrored here). Inherits the budget gap per step. similarity/detect step ops are savable but have NO runner branch → mis-dispatch to 'role'. STALE COMMENT: server.py still says the runner is "unbuilt" but the tool is defined + has live run records. *Cross-family: GRAPH/FLOWS.*

### `save_cascade` — Save a pipeline as a recipe
**Human:** Freeze a proven multi-step pipeline into a named, re-runnable recipe — validated through the one existing door and persisted so it survives a restart.
**Really does (Verified):** validates the decl through `coherence_actions.build_action` (the ONE validator, reused — name/steps/op/per-step model against the LIVE registry/roles/reduce_rules; fail-loud, never written on invalid), persists to `cascade_registry`, returns a derived `inputs_hint`/`input_schema`.
**Concrete uses:** persist a map→reduce recipe after proving it once; an agent saves a discovery pipeline; freeze a capture→cluster→tally chain.
**Ever-used:** 8 cascades persisted (so it HAS produced live rows). Tests cover it; the saved artifacts cluster on the Jun 9-10 dev window.
**Flags:** ★ BROWSER-UNREACHABLE (Root Cause 4 — same as run_cascade). Save accepts what run rejects: a cloud per-step model passes validation but run pins resident → un-runnable on cloud. DOCSTRING OVERCLAIM (inverted) — says retrieve/similarity/detect "have no engine primitive yet," but retrieve IS runnable (the runner has a full retrieve branch; `ask-the-codebase` uses it); the true unrunnable set is narrower (embed/similarity/detect). *Cross-family: GRAPH/FLOWS.*

### `list_cascades` — List the saved recipes
**Human:** List every saved cascade with its full recipe (steps, ops, models, output schema) PLUS a derived hint of what input it eats. The "what recipes can I run" index.
**Really does (Verified):** returns the full decl rows enriched with `inputs_hint`/`input_schema` from step 0 (symmetric with `save_cascade`). Read-only.
**Concrete uses:** discover runnable recipes + read their steps before `run_cascade`; pick the right one + shape inputs; `capabilities(section='chains')` aggregates flows + cascades.
**Ever-used:** Called in the bridge ONLY to build the cascade-precedence VISUALIZATION (the layers/fit view), NOT a run/list endpoint. The FE consumes cascades as a diagram only.
**Flags:** ★ BROWSER-UNREACHABLE (Root Cause 4). Rows mix eval/test cascades (eval-cascade-probe…) with real recipes — no curation flag to tell a pilot recipe from a dev probe.

### `run_graph` — Run a canvas (node graph)
*Catalogued in FAMILY 4 (GRAPH/BUILD) — it runs node-type graphs, not cognition roles. Cross-family pointer only.*

### `models_for_role` — Which models fit this specialist
**Human:** Show which models satisfy a role's declared requirements (or raw capability strings) — the model picker. Author from what exists; never invent a name.
**Really does (Verified):** `role='<id>'` looks up `spec.model_binding.requires`, OR pass `requires='chat,json'`. Returns model-ids whose `provides` ⊇ requirements + the live providers. Reuses the FE path. Read-only.
**Concrete uses:** pick a model that provides a role's capability before `run_role(model=)`; choose per-step models for `save_cascade`; find an embed-capable model for a cluster reduce.
**Ever-used:** Read-only projection; 20 refs (tests). Functional.
**Flags:** Reports capability MATCH but NOT whether the model PRODUCES content at a budget — a "fits" model can still empty-out (the budget gap is invisible here). The SAME seam `resolve_model` wraps — and `resolve_model` is never wired into firing, so this "which fits" answer never actually ROUTES a run (firing defaults to the resident brain).

### `cognition_info` — Inspect the cognition registries
**Human:** The one place to learn "what can I compose with" — roles, rules, projections/spaces, mark-types, contexts. Scoped: a concise overview, one section, or one role's full spec.
**Really does (Verified):** the SAME projection `/api/cognition_info` serves, from the live registries. `role='<id>'` adds the AUTHORABLE fields (prompt_template verbatim + output_fields as round-trippable registry type names) → inspect→copy→`create` round-trips.
**Concrete uses:** discover the role/projection/rule vocabulary before composing; read a role's output_fields to author a downstream consumer; list embeddable spaces for `find_relations`.
**Ever-used:** Heavily exercised (58 refs). Functional. (Verified live in a sibling pass: 29 roles loaded — and this works while dials/operator/panel are cwd-dark, because role_registry uses an absolute path.)
**Flags:** Read-only, no functional gap. It reports what EXISTS, not what WORKS — it lists roles/models that empty-out at the default budget (the inspector can't reveal the budget gap).

### `cognition_inputs` — What a specialist can read
**Human:** Show the addresses a role/rule can read from (the utterance, upstream run outputs, context variables, skills/contexts) plus which op/thinking/tools the bound model supports. The input-wiring picker.
**Really does (Verified):** projects the readable address vocabulary + the model-capability projection against the role's capability-resolved bound model (or an explicit `model=`, or the current brain).
**Concrete uses:** learn which `run://`/`context://`/`skill://` addresses a role may consume; check whether the bound model supports tools/thinking; discover the context variables a capture role can read.
**Ever-used:** 12 refs (tests). Read-only. Functional.
**Flags:** The capability projection is for the role's capability-resolved bound model — but since `resolve_model` is never wired into firing, the model it describes may NOT be the model a run actually uses (firing defaults to the resident brain). Described-model and fired-model can diverge.

### `capability` (singular) — What the Claude Code platform exposes
**Human:** Read the capability registry — the live external platform's flags, slash-commands, tools, MCP tools, settings, hooks, permissions, each by safety posture. NOTE singular — distinct from `capabilities`.
**Really does (Verified code, DATA-EMPTY):** a real op-dispatched tool over the CapabilityRegistry, which is BINARY-DISCOVERED (spawns the live `claude` binary, ~14s) and LAZY-populates IF the wiring is in place. But the wiring (`set_capability_registry`) is explicitly `🟡 lead-verify-queued` — never verified to populate. `describe()` returns `total=0` on an unwired Suite.
**Concrete uses:** "what flags/tools/hooks does this Claude Code expose, and which are safe vs gated"; the system reading its own host platform; a posture audit.
**Ever-used:** ★ NEVER verified live — wired + importable, but the population path is unproven; no test populates a real registry. Effectively empty.
**Flags:** ★ DATA-EMPTY (Standalone flag). Lazy-populate spawns the `claude` binary (~14s, depends on `COMPANY_CLAUDE_BIN`; a missing binary → `ok:False`, doesn't fabricate). Easy to confuse with `capabilities` (plural).

### `capabilities` (plural) — What the Company can do (the what-exists map)
**Human:** The source of truth for what EXISTS in the Company — models, node-types, RHM verbs, panels, api verbs, the runnable chains (flows + cascades), the feature inventory, operator memory. Author from these; never invent.
**Really does (Verified):** builds a real snapshot (node_types, live `available_models()`, modes, the full mode type-registry…) + scoped sections: 'chains' (flows + saved cascades), 'features' (the closed feature id-set), 'operator'. No-args = a concise size-hint map.
**Concrete uses:** orient on the whole system before composing (first call of a session); `section='models'` → the live list to pick from; `section='features'` → a real feature id.
**Ever-used:** The source-of-truth surface fed into authoring prompts + selects. Functional + central.
**Flags:** `section='models'` reports the LIVE fleet — but those models empty-out at the default budget (the map says they EXIST, not that they WORK as-budgeted; an agent authoring from this picks models that fail at run). 'chains' lists 8 cascades as runnable, but those were never run in steady production (cloud-blind + budget gaps) — the map overstates runnability.

### `models` — Model inventory (NOT an MCP tool)
**Human:** Lists/swaps the local model fleet (HF cache for vLLM + the Ollama store). This is the `company` CLI surface and the `/models` skill — there is NO `mcp__company__models` tool.
**Really does (Verified):** ★ NO MCP tool named `models` exists. The surfaces are `ops/cli/models.py` (inventory + swap), the `/models` skill, `/switch-model`. The MCP path to the model LIST is `capabilities(section='models')`.
**Ever-used:** As CLI/skill: yes. As an MCP tool: DOES NOT EXIST.
**Flags:** ★ MISNOMER in the task list (Standalone flag). Don't expect `mcp__company__models`. The list it surfaces includes cloud + large reasoning models that empty-out at the default cognition budget.

### `preview_turn` — Preview a full staged turn (no history written)
**Human:** Run a complete staged conversational turn (the cast of specialists fires, routing applies) and return the parts + lifecycle, WITHOUT appending anything to live chat history. The non-mutating dry-run of a turn.
**Really does (Verified):** `chat_parts` with `persist=False` — fires a REAL staged turn but does NOT append to history/training_signal/thread. If `mode` given it is set then RESTORED in a finally (a preview never leaves the dial moved). Defaults to the first live graph.
**Concrete uses:** preview how a turn would stage before committing; test a mode's cast/routing without polluting history; inspect the cognition lifecycle a turn produces.
**Ever-used:** Tests cover it (8 refs). Functional non-mutating turn.
**Flags:** Fires the resident swarm → inherits whatever budget the cast roles use (a reasoning-bound cast role could empty). "Non-mutating" is true for chat history, but cognition telemetry events DO fire and `run://` outputs ARE persisted — "preview" ≠ zero side-effects on the run/event store.

### `runs` — Discover past runs (the run index)
**Human:** List past run_role/run_items/run_reduce runs and their output addresses, newest-first — so an agent can feed a discovered output as an input or re-run it.
**Really does (Verified):** `list`/`find` — a read-time projection over the `op.run` event log keyed by `run://`, scoped to the closed ENGINE_RUN_OPS, `run_kind` validated fail-loud. Returns `{address, op, turn_id, role, duration_ms, seq, ts}`.
**Concrete uses:** find a past output's `run://` to feed into a new run; enumerate a mining pass's outputs to join; see WHY a run stopped (`finish_reason` rides the record).
**Ever-used:** The #54 run index; depends on `op.run` records (which exist). Functional read.
**Flags:** Only indexes runs that EMITTED an `op.run` record (the MCP-face runs) — internal cast/jury/cascade-step fires are deliberately NOT indexed (to avoid flooding) → NOT a complete record of every model call. Surfaces `finish_reason` — which CAN expose the budget gap (empty content with `finish_reason='length'`/`'stop'`) if an agent reads it, but nothing flags it automatically.

### `reduce_rule_names` — List the deterministic join-rules
**Human:** Inspect the named built-in reduce-rules `run_reduce(mode='rule')` accepts — the pure deterministic functions for joining N map-outputs into one.
**Really does (Verified):** returns `{names: sorted(REDUCE_RULES), parameterised: ['tally-by:<field>']}` — single-sourced from `cognition.REDUCE_RULES` (the G11 unification removed a drifted parallel list). Pure read.
**Concrete uses:** see which named rules `run_reduce(mode='rule')` accepts; discover the `tally-by:<field>` pattern; author a `save_cascade` reduce step from a real name.
**Ever-used:** Single-sourced; referenced by `run_reduce`, its docs, save_cascade docs, and the fail-loud error. Functional read.
**Flags:** No defects — genuinely single-sourced ("derive never hardcode" holds). (Was misfiled into DECISION/BOARD in the task list — it serves the REDUCE/cognition family.)

---

## FAMILY 4 — GRAPH / BUILD / FLOWS
*The on-canvas composition graph (build nodes, wire, run) — fully built AND browser-wired via `/api/*`. The chain-LIBRARY above it (flows, cascades, routines) is built+runnable but MCP-ONLY → browser-unreachable (Root Cause 4). `run_cascade`/`save_cascade`/`list_cascades` are catalogued in COGNITION (cross-family). All 16 node-types are real `run()` bodies, not stubs.*

### `node` — Add / remove a step (and propose new step-types)
**Human:** The unit-level editor for a composition graph — add a step of a chosen type, remove a step plus its wires, or (the self-build path) ask the brain to WRITE a brand-new step-TYPE that surfaces for the operator to approve.
**Really does (Verified):** `create` validates type against the registry, holds a per-graph lock (T1-RACE lost-update guard), seeds the node with its type's config defaults THEN merges caller config (caller wins), appends + emits a 'create' event. `delete` removes the node AND every wire touching it. `create`/`set_config` route through an AUTO guard (no approval). `propose`/`apply` carry a REAL floor: `propose` surfaces a `code_build` decision (default=reject); `apply` reads `is_approved(id)` FROM the substrate — the proposing agent CANNOT self-approve.
**Concrete uses:** lay down a chain's steps (`type='llm'` then `type='ask'`); grow a new step-type (`propose` → operator approves → `apply`); tear down a mis-wired step.
**Ever-used:** create/delete/set_config browser-wired (`/api/node` etc.); ~70 saved graphs on disk (mostly auto review-*.json). `propose`/`apply` (the self-build code-write path) are MCP-ONLY (Root Cause 4); no apply commit evidence found.
**Flags:** `propose`/`apply` not browser-reachable (no `/api` route). create config-merge seeds type defaults FIRST then caller-wins (a "blank" node carries type defaults). delete cascades to edges ("reversible compose" only in the sense the graph can be rebuilt). In the bridge `explicitly_denied` list (a mutation verb on the generic door).

### `connect` — Wire one step's output into the next
**Human:** Draw a directed wire from a source step's output port to a target step's input port. Type-checked: it refuses a wire whose port types don't match.
**Really does (Verified):** per-graph lock, looks up both nodes (KeyError if unknown), reads source-output-type + target-input-type, and if BOTH are concrete and unequal (neither 'Any') RAISES a typed mismatch — a real fail-loud check. Appends an Edge, emits a 'connect' event at the downstream node. The scheduler treats a node READY only when every declared input port is wired AND resolved — so connect is load-bearing for run readiness.
**Concrete uses:** thread an AI step's output into the next step's context input; programmatically wire a generated graph; build a fan/join shape.
**Ever-used:** ★ HEAVILY USED + LIVE — 173 'connect' events in the event log (latest Jun 19: "wired c.value → u.text"); 9+ graphs on disk. Browser-wired (`/api/connect`).
**Flags:** ★ MISCATEGORIZED in the task framing (grouped with "the role-create ones") — it is graph-node wiring, unrelated to roles. The type check only fires when BOTH ports are concrete — an 'Any' port (join/gate) bypasses it (a semantically-wrong wire into Any is silently accepted). In the bridge `explicitly_denied` list, but genuinely exercised (unlike the dormant family members).

### `set_config` — Change a step's settings
**Human:** Update the configuration of one step already on a graph (a prompt, a constant's value, a retrieve's k). A merge — updates the keys you pass, leaves the rest.
**Really does (Verified):** AUTO guard; per-graph lock; `n.config.update(config)` (a MERGE, not replace); KeyError if the node is absent. Updates config only — position/size is a separate method.
**Concrete uses:** set what an AI step does before running; tune a retrieve's k between runs; flip a gate's condition.
**Ever-used:** Browser-wired (`/api/set`); round-trips from the canvas.
**Flags:** In the bridge `explicitly_denied` "dangerous verbs" list (a mutation an external cold agent is denied unless authorized). It is a MERGE not a replace — you cannot REMOVE a config key, only overwrite/add.

### `run_graph` — Run the chain
**Human:** Execute a whole graph — fire every step whose inputs are ready, in order, reporting which steps ran vs were served from cache vs got stuck (an input never resolved). The "run the chain" button.
**Really does (Verified):** a REACTIVE RESOLVER — a node fires the instant its input addresses resolve; output persists to a `run://`; that resolves downstream. The memo gate makes "rerun only what changed" and "resume across process" the SAME content-hash mechanism. PER-NODE ERROR ISOLATION: one node raising does NOT abort — it lands in `failed{nid:err}`, the run completes, a distinct 'warning' event surfaces it. `branch=` writes to `run://...@branch` (timelines coexist).
**Concrete uses:** execute a just-built chain (see ran vs cached); cheap idempotent re-run (memo); a what-if on a branch.
**Ever-used:** Browser-wired (`/api/run`, with `force=` the MCP tool lacks); ~20 refs; core dataflow engine. Functional + exercised.
**Flags:** ★ The MCP `run_graph` return `{ran,cached,stuck}` OMITS the `failed{}` map — a node that ERRORED is invisible in the direct return; you MUST read `get_events`/`get_state` to see failures (a real gap between faces: `/api/run` returns full state with `failed`, the MCP tool does not). MCP exposes NO `force=` (can't bypass the memo gate via MCP; only the browser can — face asymmetry). 'stuck' = an input never resolved (looks like partial success — check stuck count, not just ran). *Distinct from the cognition `run_*` family — the budget gap doesn't apply unless a node fires a role.*

### `get_state` — See the chain's current state
**Human:** The full live picture of one graph — every step with its type, human kind, config, status (idle/ran/cached/stuck/failed/live), output address + hash, the actual output, position/size, and all the wires. What a canvas renders from.
**Really does (Verified):** derives per-node status (failed > stuck > ran > cached > idle) from the fresh run result OR, on reload, FROM THE STORE (a node whose output address resolves reports 'cached' not 'idle' — the D5 persisted-status fix; failed/stuck survive a reload by reading the last 'run' event). Carries the actual output + a per-node 'error'. A genuinely careful status engine.
**Concrete uses:** render the canvas (status colour + output per step); after a run, read each node's status+error to decide what to fix; inspect a portal/reference node's live state.
**Ever-used:** Browser-wired (`/api/graph`); the FE canvas renders from this. Heavily exercised.
**Flags:** No truncation — embeds the FULL output of every node inline; on a large graph `get_state` can be very large (no scoping/limit param). Status on reload is DERIVED ('cached' = "the output address still resolves," not "this node ran this session").

### `get_results` — Get just the outputs
**Human:** A stripped-down read: just `{step_id: output}` for every step, dropping status/wires/positions. The "give me the answers" view.
**Really does (Verified):** a THIN PROJECTION of `state()` — `{n['id']: n['output'] for n in state(graph)['nodes']}`. No own logic.
**Concrete uses:** grab the final step's answer after a run without parsing full state; pull all outputs to feed a downstream synthesis.
**Ever-used:** ★ MCP-ONLY (Root Cause 4) — no `/api/results` route; the browser uses `/api/graph` (full state). Agent-only convenience.
**Flags:** No own `/api` route (the FE never calls it). Same no-truncation concern. Returns output for ALL nodes incl. unrun ones (None = not-yet-run, NOT "empty answer").

### `get_events` — Recent activity log (whole system)
**Human:** The captured trajectory of recent actions across the system — create, connect, run, grow, approve, warning — newest first. The "what just happened" feed.
**Really does (Verified):** thin pass-through to `store.recent_events(limit)`. CRITICAL: GLOBAL (whole-system), NOT graph-scoped (unlike `now`). Where `run_graph`'s failed/warning events surface.
**Concrete uses:** show the operator the live activity feed; poll for a 'warning' (a node FAILED) that `run_graph`'s return hid; audit the create/connect/run sequence.
**Ever-used:** Browser-wired (`/api/events`); the FE activity feed reads it. Exercised live.
**Flags:** GLOBAL not graph-scoped — on a busy system dominated by whatever ran most recently anywhere (no `graph=` filter; `now()` is the per-graph one). The ONLY MCP surface where `run_graph` node FAILURES appear.

### `now` — This chain right now (the at-a-glance card)
**Human:** A live snapshot for ONE graph — total steps, how many resolved, how many approvals pending, a presence line ("ready · all resolved" / "awaiting your approval" / "empty"), the mode, the single most-recent event. The dashboard card.
**Really does (Verified):** derived LIVE from `state(graph)` + the surfaced inbox + the last event. Per-GRAPH (takes `graph=`), unlike global `get_events`.
**Concrete uses:** a one-line "where this chain stands" card; check everything resolved before declaring done; surface pending approvals tied to the canvas.
**Ever-used:** Browser-wired (`/api/now`); the greeting/now-view organ renders it.
**Flags:** `surfaced_pending` counts the WHOLE inbox (all unresolved surfaced items), NOT items scoped to THIS graph — "awaiting your approval" on `now(graphA)` may reflect an approval belonging to graphB. `mode='off'` overrides presence to 'off' (masks a real empty/ready state).

### `object_info` — The step-type catalogue
**Human:** The full library of step-TYPES you can place on a canvas — each type's input/output ports, render-set, config shape. The palette an agent reads before composing.
**Really does (Verified):** returns the node-type library (ports + render + config). Human-meaning lives in `nodes/_meta.py` — 16 real types: ask, codebase, constant, embed, gate, join, llm, model_of_tim, pair, portal, retrieve, rhm_mode, similarity, titlecase, uppercase, wordcount. SPOT-CHECKED llm/retrieve/gate — real PORTS + real `run()`, NOT stubs.
**Concrete uses:** populate the canvas palette; read ports before `connect()` so wires are type-valid; discover a type's config before `set_config`.
**Ever-used:** Browser-wired (`/api/object_info`). Exercised live.
**Flags:** Type-meaning is a side map flagged TENTATIVE/draft for Tim/DNA to ratify (un-seeded types fall back to a humanized id). 16 is a modest palette — several are toy (uppercase/titlecase/wordcount) inflating the count vs the substantive ones (llm/ask/retrieve/embed/gate/join/portal).

### `list_graphs` — List all chains
**Human:** List every graph (canvas) saved in the system by id. The "open a chain" index.
**Really does (Verified):** returns the ids of all saved graphs.
**Concrete uses:** show which chains exist to open; enumerate graphs for a batch op; find the DEMO 'codebase' graph.
**Ever-used:** Browser-wired (`/api/graphs`); ~70 graphs on disk.
**Flags:** Population dominated by auto-generated review-*.json (machine exhaust), not operator-built chains — "list of chains" is mostly exhaust; the real demo is the single 'codebase' graph. No metadata in the list (just ids — `get_state` each to learn what it is).

### `list_by_type` — Which node-types produce a port-type
**Human:** Type-graph query over the node-type library — given a port/output type, which node-types PRODUCE it. A composition-discovery read for wiring graphs.
**Really does (Verified):** `registry.produces(output_type)` — a pure read over the NodeRegistry type graph. The GRAPH/CANVAS layer.
**Concrete uses:** find which node-types can feed a port (`list_by_type('text')`); composition discovery before `connect()`.
**Ever-used:** WIRED — pure registry read, remote posture 'safe'.
**Flags:** ★ MISCLASSIFIED in the task list (Standalone flag) — was filed under DECISION/BOARD/CHANNEL (name-confusion with the family's many `list_*` tools); it belongs HERE. Name is ALSO shared by `substrate-mcp`'s `list_by_type` (a different tool — an agent searching by name could grab the wrong one).

### `flows` — Run a proven production-line
**Human:** The registry of committed, code-authored production lines (the registry-filler, the transcript miner, the pattern cluster) — each a designed, grounded multi-step chain you invoke by NAME in one call, instead of hand-rebuilding it from primitives (which empirically loses the grounding).
**Really does (Verified):** file-discovered registry (`flows/<id>.py` = a FLOW dict + a `run()`), rediscovered per call. `run()` validates params fail-loud. THE FLOOR is REAL + enforced at discovery: every flow MUST declare `proposes_only=True` or discovery REFUSES it (a flow may compute/write/surface but NEVER resolve/approve/dispatch/launch `claude -p`). 8 flows present, all declare proposes_only: cc_registry_refresh, drift_radar, floor_walk, pattern_cluster, registry_generation, repo_ingest, transcript_mine, ts_backfill.
**Concrete uses:** fire a proven registry-filling line in one call; a grounded mining step instead of recomposing `run_role`/`run_items` by hand; `propose` a new production line for approval.
**Ever-used:** ★ REGISTERED + RUNNABLE but MCP-ONLY (Root Cause 4 — no `/api/flows` route) AND NO execution evidence found for any of the 8 flows (no run records, no flow-run summaries). Built, discoverable, runnable — but no proof any flow has been fired. (NOTE: precisely — this is "never-fired + browser-unreachable," NOT cwd-dark; all 8 ARE discoverable.)
**Flags:** MCP-ONLY (operator can't run a flow from the FE). NO execution evidence — the "grounded chain" that motivates the whole registry may never have been invoked through this tool. `list` points to saved CASCADES when empty — but flows vs cascades are two separate chain registries (a confusion surface).

### `routines` — Schedule / fire a repeatable Claude-Code task
**Human:** Named, repeatable tasks the Company drives by spawning a REAL Claude Code session, injecting the routine's prompt, capturing the result, and tearing down. The local-driven equivalent of a cloud cron — `op=fire` actually launches a `claude -p` session.
**Really does (Verified):** file-discovered registry. `op=fire` → `routine_runner.fire()` POSTs `/spawn` to the supervisor (`:8771`) with `{cwd, prompt, permission_mode, name:'routine:<id>', source:'routine'}`; the supervisor spawns a REAL `claude -p`, watches `/watch` for done, captures result + session_id, POSTs `/teardown`. Returns a durable run record. FAIL LOUD if the supervisor is unreachable.
**Concrete uses:** run a recurring self-check by spawning a real session; show the operator the scheduled tasks; drive a repeatable maintenance task on a systemd `.timer` cadence.
**Ever-used:** ★ NEVER FIRED. Only 2 routine files exist (self_status, launch-surfaces). ZERO fire evidence in `.data/`. MCP-ONLY (no `/api/routine` route). The fire mechanism is built + unit-tested (spawn-body against a stub) but has no live execution history.
**Flags:** NEVER FIRED end-to-end (unproven against a live supervisor). ★ GOVERNANCE GAP — `routine_runner` says "Lead-only at fire time (it spawns a real claude session)" but there is NO in-code lead-only gate; `op=fire` just calls `fire()`. This collides with Tim's standing rule "build-workers/sub-agents must NEVER fire `claude -p`." Enforcement, if any, is by MCP-face exposure/deployment — UNENFORCED floor, a governance gap. The ONLY tool in this family that launches a real external process (categorically heavier than `run_graph`/`flows(run)`). **Wire operator-gated, not agent-callable.**

---

## FAMILY 5 — PROJECTION / RESOLVER
*The instrument (the projection wheel) + its dials, rules, panels, operator-memory, address inspection. **This family carries the cwd-bug cluster (Root Cause 1): `dials`, `operator`, `panel`.** `inspect_address`/`rule` are catalogued elsewhere (cross-family). The clean contrast: tools backed by a Suite-init absolute-path registry ESCAPE the bug; file-discover-relative tool faces FALL to it.*

### `project` — The Instrument (the projection wheel)
**Human:** The radial universal-projection — the agent's twin of the operator's on-screen wheel. Resolves a chosen LENS into points on a circle-in-square: angle = a category, radius = distance from a centre (time-ago, meaning-distance, or lean between two poles). The same engine the visual surface draws. Data = whatever the lens names: live activity, the corpus, node connections, cascade flows, type-nucleation.
**Really does (Verified live, raw + grouped + time + Group-10):** discovers 9 bindings from an ABSOLUTE bindings path (deliberately — so it ESCAPES the cwd bug), resolves the binding, dispatches by `radius_from` to semantic/separator/nucleation (GPU/embedder-touching) or the pure project() for the angle-by-registry case. raw/grouped/time/Group-10 are runtime-VERIFIED working (real sectors+points). The 3 meaning-field lenses (semantic/separator/nucleation) are CODE-TRACED ONLY — not fired (they hit `:8007`; consult-before-model-loads).
**Concrete uses:** read exactly what the operator sees on the wheel (grounded RHM walkthroughs); drive the radial view headlessly (switch lens, re-centre, scrub time, zoom); `binding=''` returns the 9 human-labelled lenses for the operator to pick.
**Ever-used:** used by 2 faces — `build_projection` is called by `/api/projection` AND this tool. `territory.py` reads the binding meta but does NOT call build_projection (the lens-union enrichment is a flagged fast-follow, not wired).
**Flags:** ★ THIN SLICE proven — the engine reads at least 4 MORE axes the tool never surfaces: `quant` (binary-quantization representation), `since` (the event-window floor), `graph` (which graph for the graph: lens), `dial` (the nucleation 20/80 BIRTH threshold — so MCP nucleation is stuck at default 0.2). The k/recursion slot is internal-only. ★ The 3 meaning lenses are CODE-TRACED ONLY, NOT verified — and given 4 sibling registries silently broke on THIS exact MCP face, "the meaning lenses work" is unearned + high-risk until fired. Data thinness: `agent_sessions.*` points carry empty address/summary and dump into the 'field' catch-all (no kind-group entry).

### `layers` — The Multi-Layer Model
**Human:** Self-description of the embedding "layers" — for each memory space, which embedder layers exist and their full vector dimension. The picker behind `project`'s emb (which layer) and dim (how fine the meaning-zoom can go).
**Really does (Verified live):** returns `{space:{layer:dim}}` — real data, EVERY space carries a pplx layer (2560-dim): common_knowledge, history, operators, principles, repo, topics, worldview. BGE 'default' is 1024 in most, 2560 in operators (pplx-native). Reads `store.layer_dims()` (the store self-scans — a newly-embedded layer appears with no code edit).
**Concrete uses:** prove the multi-layer claim before driving `project`'s emb='pplx'; bound `project`'s dim (must be ≤ the layer's full_dim); the layer/resolution-picker source.
**Ever-used:** used by `project` + 2 UI affordances; mirrors `/api/layers` + `/api/layer-dims`.
**Flags:** ★ FLIPS a prior suspicion — pplx is NOT aspirational; it is ubiquitous (all 7 spaces), so `project`'s emb='pplx' axis has a genuine target. One of the few FULLY substantiated claims. Escapes the cwd bug because it reads the store (not a file-discover registry).

### `dials` — Character Dials (adjustable traits)
**Human:** The entity's adjustable character knobs — how far ahead the brain thinks (anticipation), how much the surface may rearrange itself (stability). Tim turns knobs instead of making one-time decisions.
**Really does (BROKEN LIVE):** `dials(op='list')` returns `{"dials": []}` on the MCP face — EMPTY. But the registry has 2 rows on disk (anticipation, stability). ★ ROOT CAUSE 1 (reproduced): `DialRegistry().discover()` defaults to a RELATIVE `dirs=('dials',)`; the MCP process cwd ≠ root → 0. Proven: from `/tmp` → `[]`; from root → `['anticipation','stability']`. `set`/persist (→ system-graph dials node) works structurally.
**Concrete uses:** would let the resolver be tuned (warm/hot anticipation, museum/workshop/stage stability) without code; the operator's knobs surface. Today: dark on the MCP face.
**Ever-used:** ★ NEVER-used as a consumer seam AND broken-on-MCP. Even when loaded, BOTH dials have ZERO behavioural consumers — both rows' `governs` say verbatim "nothing reads this yet"; the only reader is `cognition_info` echoing dial VALUES; `dial_state` hardcodes `overrides_evaluated:False`.
**Flags:** ★ TIM'S FLAG CONFIRMED + EXPLAINED — dials returns empty, NOT because the registry is empty (2 rows) but the cwd bug. ★ SILENT FAILURE — a bare `{dials:[]}` with no error, violating `no_silent_failures` (itself an operator-memory row that can't load via this same bug). ZERO consumers even when loaded (aspirational config for organs that don't exist yet — named honestly in `governs`, to their credit).

### `operator` — Operator Memory (the system's confirmed rules for working with Tim)
**Human:** The system's memory of how to work with its operator — confirmed standing rules, each carrying Tim's verbatim words as evidence. The thing an agent should read before surfacing anything to Tim.
**Really does (BROKEN LIVE):** `operator(op='rules')` returns `{"rules": []}` on the MCP face. But `operator_memory/` has 29 confirmed rows on disk (record_expansively, no_deferral, no_silent_failures, confirm_before_writing, verify_before_claiming…). ★ SAME ROOT CAUSE 1 — relative-default discover; MCP cwd ≠ root → 0 rows (reproduced: `/tmp` → 0, root → 29). Read-only by design (rows arrive via mining-propose → Tim-confirm).
**Concrete uses:** the RHM should read these rules BEFORE composing anything Tim sees (the docstring instructs "read op=rules FIRST"); surface the confirmed working-rules with verbatim evidence. Today: an agent trusting this on the MCP face gets `[]` and behaves rule-blind.
**Ever-used:** ★ BROKEN-on-MCP (empty live). The registry IS populated (29 rows) + reachable from repo-root context; the failure is specific to this tool face's relative discover.
**Flags:** ★★ THE SINGLE MOST DANGEROUS instance of the cwd bug — an agent told to read Tim's standing rules first gets nothing + proceeds rule-blind. The 29 rows INCLUDE `no_silent_failures` + `verify_before_claiming` — rules that, if loaded, would forbid exactly the silent-empty behaviour the bug produces. Same one-line fix as dials/panel (absolute ROOT path; the projection author already did it for bindings + documented why — never propagated).

### `panel` — Verdict Panel (a diverse jury)
**Human:** Judge something through a panel of N different lens-roles — a perspective-diverse jury (grounding vs voice vs claims-fit), one fire each, a deterministic quorum. Catches different failure modes than repeated draws of one judge. Verdicts inform the operator's review; the panel never approves anything.
**Really does (PARTIALLY BROKEN LIVE):** `panel(op='list')` returns `{"panels": []}`. But `verdict_panels/` has `registration_confirm.py` (seats: confirm_registration, voice_lens, element_fit_lens; quorum 2-of-3). ★ SAME ROOT CAUSE 1 — relative-default discover → 0 from the MCP cwd. The seats ARE real roles (VERIFIED live via `cognition_info` — 29 roles loaded), so `op='run'` would resolve + execute IF the registry weren't empty; instead `op='run'` KeyErrors fail-loud (the operator can't run a panel they can't list). `run_panel` itself is intact.
**Concrete uses:** jury a proposed dossier / a generated answer through 3 distinct lenses before Tim's gate; surface a named diverse verdict with every dissent named. Today: list/describe lie (`[]`); run fails loud.
**Ever-used:** ★ BROKEN-on-MCP for list/describe (empty); run unreachable (can't discover the id). The single panel + its 3 seats exist; only the panel-registry discover is broken.
**Flags:** list/describe silently `[]` while run would KeyError — inconsistent failure modes for the same broken registry. Only ONE panel exists (the "diverse-juries" framing is real but the population is a single founding row). ★ ASYMMETRY — the SEATS load fine (role_registry = absolute path) but the PANEL that composes them does not — PROOF the bug is specifically file-discover-relative tool faces, not the role layer.

### `rule` — Routing Rules (when X → route to Y)
**Human:** Work with a role's declarative routing rules — the deterministic "when <condition> → route the resolved value to <destination>" that fires after a role resolves. Validate or dry-run a rule (pure reads), or attach/detach one (which only PROPOSES a change for the operator — never self-applies).
**Really does (WORKS — code-verified; role_registry confirmed live):** wraps existing Suite methods (no new engine). `validate`/`dry_run` are PURE (never route). `attach`/`detach` are a constrained `edit_role` that re-PROPOSES the role + SURFACES a `role_build` (propose-not-apply). Floor enforced at construction: `FORBIDDEN_DESTINATION_VERBS=('resolve','approve','dispatch')` — a rule literally CANNOT be built that routes to dispatch/claude-p. A PROTECTED role refuses attach/detach. Validates `role_id` against the LIVE role_registry — which ESCAPES the cwd bug (built at Suite init with an absolute path).
**Concrete uses:** design a routing rule (focus.which_roles → join the cast) + dry-run it before proposing; "with these inputs → this fires → routes to inject" preview; attach surfaces a role_build for approval.
**Ever-used:** WIRED to real Suite methods; role_registry populated (29 roles, many already carry rules). Could not find a non-test live MCP caller of the `rule` tool specifically (an authoring affordance exercised by tests).
**Flags:** ★ The dispatch-floor IS genuinely enforced (verified at Rule construction) — this one HOLDS, unlike the `mark` gate. ★ The ONE projection/resolver-family tool backed by a Suite-init absolute-path registry → NOT broken by the cwd bug (the clean contrast that pins the root cause). attach/detach correctly never self-apply (propose-only). The surfaced role_build is resolved by the SAME operator-approval path whose `#1b` token-mint is unwired — residual risk is the shared `#1b` gap, not the rule tool. *Cross-family: DECISION/BOARD.*

### `field_types` — Output Field Types
**Human:** The closed registry of field types a proposed role's structured output may declare — text, number, flag, list, enum, nested object, list-of-objects.
**Really does (WORKS — verified live, DOCSTRING UNDERCOUNTS):** docstring claims 6 scalar types; LIVE returns 11 — those 6 PLUS enum (Literal), object (nested field-set), list[object], list[dict], dict. Escapes the cwd bug (Suite-backed).
**Concrete uses:** pick a role's output-field types when authoring via `create(kind='role')` — incl. the nested object / list[object] shapes the docstring hides; the output-field-type picker; confirm a proposed schema uses only registered types.
**Ever-used:** used by the role-builder + `/api/cognition/field_types`. Live-verified.
**Flags:** ★ DOCSTRING OVERCLAIM (inverted) — it UNDER-describes (says 6, registry exposes 11 incl. enum/object/list[object]); an agent trusting the docstring would never use the nested-object capability that EXISTS. Works correctly; the defect is the stale docstring.

### `list_skills_contexts` — Skills & Contexts
**Human:** List the addressable skill:// (reusable instructions) and context:// (reusable text blobs) a role's input can be set to — the same registries `inspect_address` reads.
**Really does (WORKS — verified live):** returns 6 skills (corpus_pipeline, extract_decisions, inversion_query, map_reduce_composition, patterned_visibility, summarize) + 1 context (company_overview), each with id/label/description. Reads module-level cognition registries (NOT a relative file-discover at call time) → ESCAPES the cwd bug.
**Concrete uses:** discover the reusable recipes an agent can wire as a role input before composing; surface the skill/context library for the role-builder; feeds `inspect_address` (the listed ids are what it resolves).
**Ever-used:** used — read by `resolve_address` (run_role input resolution); this is their list door. Live-populated.
**Flags:** Works; modest population (6 skills, 1 context) — small but real, not a stub. Backed by cognition module registries → escapes the cwd bug (contrast with dials/operator/panel).

### `inspect_address` — Inspect Address
*Catalogued in FAMILY 1 (RECALL). Cross-family: also the resolver's read door. Works, fails loud — the correct counter-example to the family's silent-empty bug.*

### `point` — Point (spotlight an on-screen thing as you talk)
**Human:** The right-hand-man's pointing finger — as the brain explains a surface it spotlights the on-screen thing it just named, so the operator's eye goes where the words go. A pure presentation signal carrying no address (addresses stay client-side — operator-law).
**Really does (WORKS — verified live + traced end-to-end):** the tool returns `{ok, token}` (verified live, token='wheel'). The real signal is the tool-CALL: traced full circuit — point tool_use → `run_turn` emits `{type:'point', token}` → the FE maps the OPAQUE token → `ui://` from its LOCAL pointables catalog → dispatches `ui:point` → projection's ONE spotlight sink. No address ever touches the brain or server (operator-law airtight). Unknown/stale token degrades to a clean client-side no-op.
**Concrete uses:** during a walkthrough, point at the wheel/lens/sector the moment it's named; the brain's emit door onto the surface spotlight; rides projection's existing spotlight sink (reuse, not a parallel highlighter).
**Ever-used:** used end-to-end — the emit is wired in `run_turn` (the live chat-turn path), the consume in the FE + the pointables install; both halves verified in code.
**Flags:** The tool in isolation is a no-op echo (easy to mistake for a stub) — but the circuit it triggers is fully wired (the act IS the signal). Cosmetic/read floor (moves no state — correctly so). Not exercised through a real brain turn this pass (would need a live chat turn with a pointables catalog).

---

## FAMILY 6 — CLONE / GATE / SESSION-FABRIC + SELF-AUTHORING
*Past-self clones, the gate/abort/rewind control, voiced output, channel attachments, the self-change ledger, and the self-authoring tools (create / propose_role / edit_role / delete_role). `connect` was grouped here in the task but is graph-wiring — catalogued in FAMILY 4. The session_supervisor (`:8771`) is the backbone all the cc_* tools ride.*

### `cc_clone` — Run a Past Self in the Channel
**Human:** Bring back any Claude Code session EXACTLY AS IT WAS at a chosen past moment (a compaction boundary, a timestamp, a message UUID), launch it as a live background "clone," and talk to it. The clone wakes believing it is mid-conversation with Tim; you DM it, it answers from its un-drifted past-context, and "onboard" makes it a standing "era-advocate" that cross-checks current work against what Tim wanted then.
**Really does (Verified — 8 on-disk records, fired in production):** `clone` cuts the source transcript at `at` into a NEW jsonl (source byte-untouched, fail-loud if it changed), calls supervisor `/spawn` with resume=new_sid, registers the clone as a SUPERVISED channel-member. `msg` injects via `/inject`, folds the 'done' event back as the reply. `onboard` runs the reflect-before-brief message + persists the reflection + a `clone://` address. `prepare` materializes + returns the operator launch command but spawns NOTHING (the interactive path an agent is forbidden to auto-launch). `resolve` → the record.
**Concrete uses:** DM a past-era self ("what did Tim want built in your era that we dropped?"); spin up the peak-context fork point (pick via `session_recall op=spin_up_points`), onboard it, let it advise a current builder; boot an expensive past-era clone CHEAP on a company/ollama model.
**Ever-used:** ★ FIRED IN PRODUCTION (strongest end-to-end evidence in the family) — 8 records (Jun 15-18); 4 carry a persisted `reflection` field, proving the full spawn→inject→/watch→done→msg→onboard→persist chain ran live. HOWEVER all 8 are STALE NOW — the supervisor holds only ONE session (a closed probe); none of the clones' supervisor ids are present, so `list_clones(prune=True)` would delete every record next call.
**Flags:** ★ DOCSTRING OVERCLAIM — "VERIFIED-BY-USE: booted on kimi" but NO recorded clone ran kimi; both ollama records fell to deepseek-v4-flash (context > 256K). The kimi path is probe-only. Registry is presence=truth but UNRECONCILED (8 records, 0 live). The whole era-advocate value depends on the supervisor being up AND holding clones live — a supervisor restart silently evaporates the advocate fleet. INTERACTIVE channel-member clones (`prepare`) are NEVER agent-launchable (safety classifier blocks the auto-launch) — operator-only by design.

### `cc_gate` — Pause / Abort / Rewind a Step
**Human:** The operator's per-step stop/undo over a live agent action — register a GATE on a declared step, then ABORT (interrupt + tear down, no orphans) or REWIND (fork the transcript back to an earlier point).
**Really does (Verified — an OBSERVER/RECORDER, not an enforcer):** `gate` writes a gate record (state=gated) — it does NOT itself pause anything; the actual pause must ride claude's NATIVE `blocks_execution` (enforced inside claude's own CLI loop, which this module CANNOT touch — the documented HONEST LIMIT). `resume` just records a transition. `abort` is the only op with real teeth (supervisor /interrupt then /teardown). `rewind` calls `materialize_at_point` (the same fork transform cc_clone uses).
**Concrete uses:** register a gate on a risky step then abort if it looks wrong; rewind a session that went down a bad path; gate a `run_composition` leg (the ONE place a real enforceable pre-pause exists, because run_composition is the Company's own driver).
**Ever-used:** ★ NEVER FIRED IN PRODUCTION — there is NO `.data/gates/` directory; `op=gate` has never written a record. The only callers outside tests are a DOC reference + the bridge deny-list. The commit "R15 gate/rewind fires (verified by use)" is unit-only (tempdir gates_dir + stubbed supervisor).
**Flags:** ★ DOCSTRING/COMMIT OVERCLAIM — "verified by use" was unit-only, never a real claude gating on `blocks_execution`. `gate`/`resume` are RECORD-ONLY — they create the APPEARANCE of a pause control but enforce nothing (a user could "gate" believing it is paused when it is not). Only `abort`/`rewind` have real effects — the headline GATE verb is the weakest part. In the bridge `explicitly_denied` list; combined with zero on-disk records → effectively dormant.

### `cc_voice` — Give Text a Voice
**Human:** Render any text to a spoken WAV through whichever of the Company's resident TTS engines is running. The building block for voiced cross-session conversation (a clone or the RHM "speaking" on the channel). Playback is device-side — this only produces the file.
**Really does (Verified):** `engines` reads `ops/services.json`, lists every tts-* service + health-checks each. `speak` finds the first UP tts-* engine, POSTs `{text[, voice]}`, validates the response starts with `b'RIFF'` (else raises with the error snippet — no silent silence), saves a WAV. It SURFACES an existing engine; never starts one (fail-loud "run `company up @xsession`").
**Concrete uses:** speak the RHM's answer aloud; render a clone's channel reply to audio (hear past-selves); check which TTS engine is loaded.
**Ever-used:** ★ FIRED EXACTLY TWICE, on BUILD-DAY ONLY — `.data/voice/` holds two WAVs both stamped 2026-06-14 17:35 (within one minute, the day cc_voice was committed). No output since. Built-and-abandoned.
**Flags:** Built-and-abandoned signature (two outputs in one minute on commit day, nothing in the 6 days since) — the voiced-conversation use it was built for never materialized. Hard dependency on a tts-* engine being UP (a separate manual loadout). Device-side playback only — the tool returns a path; nothing in the family PLAYS it, so end-to-end "voiced channel conversation" is not wired (only the render half).

### `cc_attachments` — Attach Things to a Channel
**Human:** Bind targets — a session, a doc, a recall scope, a board item, or the cloning capability — to a cross-session channel, as an add/remove registry. Lets a channel's setup be parametrically composed. The channel's "manifest" is a live projection of these rows grouped by type.
**Really does (Verified):** `attach` validates `attachment_type` against the registry (fail-loud), validates the channel exists by READ-ONLY import (file-disjoint — never writes a channel record), enforces non-multi types, writes an id-keyed row. `detach` removes it. `manifest` is a COMPUTED projection (groups target → by type, not stored). target is stored verbatim/opaque, never parsed.
**Concrete uses:** attach a set of past-session clones + a recall scope to ground a fabric conversation; bind the 'cloning' capability to a channel (so it can spin up era-advocates); attach docs/board items so the manifest projects what a channel is "about."
**Ever-used:** ★ NEVER FIRED — `channel-memory/channel_attachments/` is EMPTY (no row ever written) despite ~10 live channels. 5 attachment types registered (board_items, cloning, docs, recall, sessions), nothing ever bound. Built + dormant.
**Flags:** Zero bindings in production while the channel fabric is actively used (~10 channels, a 4MB+ mail log) — the parametric-channel vision is unrealized (channels work WITHOUT attachments). A documented FOLLOW-UP is explicitly NOT done (promoting attachment_type to a first-class corpus-registry kind so create/cognition_info see it — deferred) → attachment types are invisible to the create()/cognition_info surface. `require_channel` can be flipped False → a row pointing at nothing (footgun).

### `self_change_log` — What Has the System Changed About Itself
**Human:** The audit ledger of the Company's own reversible self-modifications — every [self-apply] (a role/skill/projection it authored into itself), [self-build] (an accepted autonomous wire build), [checkpoint] (an operator restore point), newest-first, each with sha/subject/ts/touched-files/is-revert. The one place to audit + one-click-revert the system's edits to itself.
**Really does (Verified — READ-ONLY):** git-greps the repo for the tagged commits, parses sha/subject/ts/changed_files, marks `is_revert`. It does NOT write — the WRITES come from `create()`/`apply_role`/the wire (each git-commits with those tags); this tool reads their trail. `last_self_change` computes still-standing changes (skips reverts). REVERT itself is operator-only + OFF this face (in the bridge `explicitly_denied`).
**Concrete uses:** audit what the system has autonomously authored before trusting it + grab a sha for the operator-only revert; review [self-build] entries after a loop; pair with the address-keyed `self_changes_at` filter.
**Ever-used:** ★ FIRED / LIVE LEDGER — the git history is full of real tagged commits (many `[self-apply] create cognition role …(direct)`, projections, relation_types + 6 `Revert "[self-apply]…"`). A real, non-trivial ledger.
**Flags:** The NAME reads like a writer but is strictly READ-ONLY (the change-WRITING is done by create()/the wire). Revert is deliberately NOT on this face (operator-only) — the "one-click rollback" the docstring sells is only half here (audit + sha, but not revert through the agent surface). 6 reverts in the ledger indicate the autonomous self-creates are genuinely fallible (churn the ledger honestly surfaces). In the bridge `explicitly_denied` list.

### `create` — Author a New Registry Entry
**Human:** One declarative-authoring tool with a `kind` selector — create a brand-new role, skill, context, projection, mark_type, generation_policy, relation_type, or ai_tic and have it go LIVE immediately, no operator approval. The agent's own authoring power: the system grows new cognition pieces into itself directly, correctness-gated so a malformed entry is refused rather than written.
**Really does (Verified):** the `kind` enum DERIVES from the live Suite's `create_<kind>` methods (registry-is-truth). Each `create_<kind>` renders the source, GATES it by importing in a tempdir (a bad spec FAILS LOUD, never written — so a broken role can't brick `RoleRegistry.discover`), writes atomically, git-commits with a `(direct)` [self-apply] tag, auto-reflects the drift-home AGENTS.md in the SAME commit, rediscovers → live. This is the #58 DIRECT path (Tim's correction that propose→surface→approve was the AI's default, not his constraint). The BUILD-DISPATCH floor is preserved — it writes a data/registry file, NEVER launches `claude -p`.
**Concrete uses:** the system authors a new cognition role into itself live during a build (the bulk of the [self-apply] ledger); add a projection/relation_type to extend how the corpus is sliced/linked; create a skill/context the cognition layer discovers on next access.
**Ever-used:** ★ HEAVILY USED — the git ledger is DOMINATED by create's output (`[self-apply] create cognition role X (direct)` etc.). The live, dominant authoring path that SUPERSEDED propose_role/edit_role.
**Flags:** create is the path that made propose_role/edit_role/delete_role largely VESTIGIAL (the `(direct)` tag is THIS tool's signature). Direct + no approval means the system mutates its own cognition layer autonomously — the only guard is the tempdir CORRECTNESS gate (compiles/imports), NOT semantic correctness; a syntactically-valid-but-wrong role goes live + shows up later as a revert (the ledger has several). Node-type / executable-code creation is deliberately EXCLUDED (declarative DATA only; an agent expecting to author a graph node-type here is refused → `node(op=create)`).

### `propose_role` — Propose a New Role (for Approval)
**Human:** Author a NEW cognition role but SURFACE it for the operator to approve rather than applying it live — the surfacing path, kept alongside the direct `create(kind='role')`.
**Really does (Verified):** optionally brain-drafts a field-set from a natural-language `brief` (asks the operator via needs-> on an unregistered value, never invents), renders + GATES the role (tempdir import), then `inbox.surface('role_build', default='reject')` + a 'grow' event. It does NOT apply — the consequential half is `apply_role` (reads `resolved=='approve'` FROM the inbox; the proposing agent CANNOT self-approve) which is OFF the MCP face. Fail-loud if the id already exists (→ edit_role).
**Concrete uses:** when the operator specifically wants to review a new role before it goes live; brain-draft a role from plain English + surface the field-set; propose a role on sensitive ground where direct authoring isn't wanted.
**Ever-used:** ★ FIRED, THEN SUPERSEDED — real surfaced role_build items on disk (s90/s93/s103/s105/s106) with 'grow' events Jun 8-10 (authtest_role, sentiment_probe, eval_classify, voice_lens). This is the PRE-#58 era; from Jun 11+ the ledger is all `create()` `(direct)`. Effectively legacy.
**Flags:** SUPERSEDED by `create(kind='role')` (the #58 reframe). Surface-ONLY — no teeth by itself; nothing happens until `apply_role` (operator-gated, off-face). The consequential apply is unexercisable by the proposing agent by design — so propose_role's whole point (gated activation) depends on an operator who, per #58, usually isn't asked anymore.

### `edit_role` — Edit an Existing Role (for Approval)
**Human:** Re-author an existing cognition role by merging your changes onto its current spec and surfacing the replacement for the operator to approve. Protected roles (ones the runtime imports by name) are refused — flagged as needing a code-level migration, never silently risked.
**Really does (Verified):** fail-loud if unknown; if PROTECTED, REFUSES + returns a needs-tim question (editing a runtime-imported role could break import). Otherwise MERGES the partial spec onto the LIVE spec (the GC12 fix: a bare partial used to WIPE output_fields — it now projects output_schema back to authorable rows + overlays only non-None named fields), renders + gates, then `inbox.surface('role_build', {edit:True})`. SURFACES; never self-applies.
**Concrete uses:** change one field of an existing role (a prompt_template) + surface the merged replacement; refine output_fields while keeping the rest intact (the merge guarantees no schema-wipe); attempt to edit a core role + get the protected refusal.
**Ever-used:** ★ LIKELY NEVER-FIRED AS EDIT — no role_build item on disk carries the `{edit:True}` marker (s90-s106 are all NEW proposals); same supersession as propose_role. Available, correctness-solid, but unexercised.
**Flags:** SUPERSEDED + likely never fired as an edit. Surface-only. Carries a real well-designed merge (GC12 prevents schema-wipe) — but a guard that good for a path nobody uses is a strong build-then-abandon signal. PROTECTED_ROLES refusal is correct + important but means the most consequential edits (runtime-imported roles) are explicitly off-limits.

### `delete_role` — Request Removal of a Role (for Approval)
**Human:** Surface the removal of a cognition role for the operator to approve — propose-not-apply applies to deletes too. Protected roles are refused outright as a brick risk. Nothing is removed until the operator approves; the actual file removal happens off the agent face.
**Really does (Verified):** fail-loud if unknown; if PROTECTED, REFUSES. Otherwise ONLY `inbox.surface('role_delete', default='reject')` + a 'grow' event — removes NOTHING. The consequential removal is `apply_role_delete` (re-checks PROTECTED, os.remove, git-commits, rediscovers; runs only on the operator's approve) which is OFF the MCP face.
**Concrete uses:** request removal of an experimental/obsolete role + surface for confirm; clean up after a probe role without giving the agent direct delete power; attempt to delete a core role + get the protected refusal.
**Ever-used:** ★ FIRED ONCE — one real role_delete surface (s104, Jun 10, eval_p1probe). After that, supersession. Single historical use, now legacy.
**Flags:** Surface-only with the LEAST teeth of the role family (removes nothing). Superseded surfacing era. ★ ASYMMETRY — NO DIRECT delete counterpart exists in create()'s world, so deletion is STILL surface-only/operator-gated: the system can AUTHOR roles directly but cannot DELETE them directly. PROTECTED_ROLES means the roles most worth removing carefully cannot be deleted via this path at all.

---

# §MERGE — content for `mcp_face/tool_meta.json` (projection / DNA to wire)

*This block is the merge-ready human-meaning layer. **DO NOT auto-edit `tool_meta.json` from this file** — the task assigns the wiring to projection/DNA, and confirm-before-writing applies. Map to the EXISTING schema (`tool-meta-registry-v1`): `human_name`, `human_description`, `op_labels`, `op_params`, `param_labels`, `enum_sources`. Below I supply the two directly-mergeable fields for every tool (`human_name` + `human_description`, jargon-cleaned to match the existing `corpus` row's register), plus the `op_labels` KEYS (from each tool's ops) and the `op_params` SOURCE (from each tool's key_params).*

**Authoring-pass follow-up (NOT faked here):**
- `human_name` + `human_description` for all 66 → take VERBATIM from each tool's catalog entry above (the **Human:** line). They are written in the FACE-3 register already.
- `op_labels` → one friendly verb per op. Ops are listed per-tool in the catalog (e.g. corpus: query/list/find/read/neighbours → "Ask a question / Browse all / Filter to some / Open one / Find related" — already in tool_meta.json as the seed pattern).
- `op_params` → the ordered VISIBLE params per op (expert knobs hidden). Source = each tool's key_params in the catalog; the visible-vs-hidden split is a DNA call.
- `param_labels` → human label per param. **Needs a dedicated authoring pass** — do not fake; derive from the param's role in the catalog.
- `enum_sources` → param → live registry URL for dropdowns (registry-is-truth). Known seeds: `space → /api/layers` (proven by `layers`), `mark_type → <mark_type_registry url>`, `role → /api/cognition_info`, `model → /api/cognition/models_for_role`, `output_type → /api/object_info`, `kind (create) → derived from Suite create_* methods`. **Needs a pass to confirm each live URL.**

**Per-tool merge stubs (human_name · ops-for-op_labels · key_params-for-op_params). `human_description` = the catalog's Human: line.**

| tool | human_name | ops (→ op_labels keys) | key_params (→ op_params source) |
|---|---|---|---|
| corpus | Company memory | query·list·find·read·neighbours | op·text·space·address·k·rerank·detail·project·kind·projection·source_address |
| ingest | Feed the memory | (no ops) | roots·paths·project·space·max_files·force·session·round |
| capture | Capture to memory | (no ops) | role·units·project·session·round·projection·record_kind·max_tokens·temperature |
| find_relations | Inversion finder | (no ops) | item·near_space·far_space·k·min_score |
| mark | Leave a mark | (no ops) | target·mark_type·value·confidence·source_pass·evidence |
| marks | Read marks | target·type·findings | by·target·mark_type·address·detail·limit |
| inspect_address | Inspect address | (no ops) | address·turn_id |
| sessions | Session fabric (read) | list·inbox·watch·describe·search·timeline | op·session·q·state·cwd·since·thread·verb·mode·detail |
| session_post | Session fabric (write) | auto·deliver·wake·consult (verbs) | to·message·verb·from_session·copies·thread·at |
| session_recall | Recall (semantic) | find·decisions·open_loops·catch_up·timeline·directives·spin_up_points·drift | op·session·q·since·k |
| context | Live context | read·compact | op·session·focus |
| decisions | Decisions waiting for you | (zero-arg) | (none) |
| cc_board | Company noticeboard | file·list·get·transition·types | op·type·title·author_session·body·source·channel·thread·links·item·to_state·state |
| cc_channel | Message live sessions | list·send·broadcast·mail·create_channel·list_channels·add_member·remove_member·archive_channel | op·to·message·thread·topic·frm·channel·name·handle·purpose·coordinator |
| channel_act | Act on the fabric (write) | create·gather·add·remove·status·post·mode·promote·disperse·archive | action·channel·name·purpose·members·session·participation·message·from_session·thread·mode·coordinator·parent |
| channels | Read the fabric | list·describe·history·edges | op·channel·session·kind·status·q·since·limit·probe_supervisor |
| inbox | Chief-of-staff inbox | (zero-arg) | (none) |
| list_surfaced | Build-approval inbox | (no ops) | sid·status·unresolved_only·limit·detail |
| run_role | Run one specialist | generate·embed | role·utterance·op·model·inputs·max_tokens·ensure·policy |
| run_items | Fan over many (MAP) | (no ops) | role·items·max_tokens·temperature |
| run_reduce | Join into one (REDUCE) | role·rule·cluster | addresses·mode·role·reduce_rule·cluster_threshold·max_tokens |
| run_draft | Run a throwaway specialist | (no ops) | draft_role·utterance·model·inputs·max_tokens·policy |
| run_draft_items | Fan a throwaway (MAP) | (no ops) | draft_role·items·max_tokens·temperature |
| run_cascade | Run a saved pipeline | (no ops) | name·inputs·max_tokens |
| save_cascade | Save a recipe | (no ops) | decl |
| list_cascades | List the recipes | (no ops) | (none) |
| run_graph | Run the chain | (no ops) | graph·branch |
| get_state | See the chain's state | (no ops) | graph |
| get_results | Get just the outputs | (no ops) | graph |
| get_events | Recent activity (system) | (no ops) | limit |
| now | This chain right now | (no ops) | graph |
| object_info | The step-type catalogue | (no ops) | (none) |
| list_graphs | List all chains | (no ops) | (none) |
| list_by_type | Which types produce a port | (no ops) | output_type |
| node | Add/remove a step | create·delete·propose·apply | op·graph·type·config·node_id·name·spec·surfaced_id |
| connect | Wire two steps | (no ops) | graph·from_node·from_port·to_node·to_port |
| set_config | Change a step's settings | (no ops) | graph·node·config |
| flows | Run a production-line | list·describe·run·propose | op·flow·params·spec |
| routines | Schedule/fire a task | list·get·fire | op·id |
| models_for_role | Which models fit | (no ops) | role·requires |
| cognition_info | Inspect cognition registries | (no ops) | section·role·detail |
| cognition_inputs | What a specialist can read | (no ops) | role·model |
| capability | Platform capabilities | list·get·search·describe·snapshot | op·id·kind·name·query·posture·platform_id |
| capabilities | What the Company can do | (no ops) | section |
| preview_turn | Preview a staged turn | (no ops) | utterance·mode |
| runs | Discover past runs | list·find | op·role·run_kind·run_op·since·limit |
| reduce_rule_names | List the join-rules | (zero-arg) | (none) |
| project | The Instrument (wheel) | (no ops) | binding·space·emb·dim·rung·center·at·types_space·pole_a·pole_b·limit |
| layers | The Multi-Layer Model | (zero-arg) | (none) |
| dials | Character Dials | list·describe·set | op·dial·value·overrides |
| operator | Operator Memory | rules·describe·proposed | op·rule |
| panel | Verdict Panel | list·describe·run | op·panel·utterance·element |
| rule | Routing Rules | validate·dry_run·attach·detach | op·ast·destination·sample_resolved·role_id·rule·rule_id |
| field_types | Output Field Types | (zero-arg) | (none) |
| list_skills_contexts | Skills & Contexts | (zero-arg) | (none) |
| point | Point (spotlight) | (no ops) | token |
| cc_clone | Run a Past Self | clone·msg·onboard·list·end·prepare·resolve | source·at·clone·message·model·provider·fleet·phase·address |
| cc_gate | Pause/Abort/Rewind | gate·resume·abort·rewind·list·get | step_address·session·gate·source·at·state |
| cc_voice | Give Text a Voice | engines·speak | text·voice |
| cc_attachments | Attach to a Channel | attach·detach·list·manifest·types | channel·attachment_type·target·attachment·require_channel |
| self_change_log | System self-changes | (no ops) | limit |
| create | Author a registry entry | role·skill·context·projection·mark_type·generation_policy·relation_type·ai_tic (kinds) | kind·spec·model |
| propose_role | Propose a role (approval) | (no ops) | spec |
| edit_role | Edit a role (approval) | (no ops) | role_id·spec |
| delete_role | Remove a role (approval) | (no ops) | role_id |

*Note: `models` is intentionally ABSENT (not an MCP tool — see Standalone flags). 66 tools above.*

---

# CONVERGENCE (point, do not re-describe)
- **COMMISSION-COMPLETION-REGISTER.md** — the WHAT-must-all-be-true. This atlas feeds its §CAPABILITIES ledger (the never-used powers) + the FACE-3 (tool-face) row.
- **TOOL-FACE-BUILD.md** — the build spec for the surface this atlas's human layer renders into (the `/api/tools` door, the `tool-card` archetype, the safety gate). The `explicitly_denied` list there cross-walks the Root-Cause-3/4 flags here.
- **CHANNEL-LOOP-BOARD.md** — "the engines are built and have no FACE." This atlas is the tool-half of that capability inventory — the per-tool ever-used / never-wired verdict the loop needs.
