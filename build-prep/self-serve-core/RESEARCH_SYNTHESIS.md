# Research Synthesis — "The Core, Self-Serve for Every Session" (scope C)

*loop-prep round 1. Grounded in 7 parallel read-only explorer scouts of /home/tim/company (+ ~/recollection), 2026-06-15. This is the EVIDENCE BASE: what EXISTS, the self-serve state, the gaps. The Completion Criteria + Implementation Guide build on this. Changes flow synthesis → criteria → guide, never reverse (synthesis is ground truth).*

## Verdict in one line
**~80% of the substrate already exists** — this is largely ASSEMBLY + a few real new pieces (the search HIERARCHY, the self-serve ONBOARDING/discoverability layer, a handful of self-serve GAP closures, MCP COHERENCE, and FRONTEND scope exposure on the existing design system). It is NOT a from-scratch build. The prime directive (loop-prep #2): do not spec parallel systems — extend what's here.

## The build, decomposed (Tim's 2026-06-15 directive)
A fresh/spawned session, across multiple projects (recollection · wildcard · an interface/core-ops session · future), should self-serve: create+consult its OWN era clones (in a common channel) · search/ask/analyze/scan its own history, other sessions in the same project, and across projects (a natural hierarchy reflected in storage) · set up channels + rules + guides + project-info · select+add attachments + add new attachment types · learn all of this from built-in guides/MCP/onboarding (prepared for fresh + spawned sessions) · all search scopes exposed to a front end.

---

## ROUND 1 FINDINGS (per subsystem)

### 1. Era clones — MOSTLY BUILT + MCP-exposed
- Lifecycle: `clone_at(source_jsonl, at)` (cc_clone.py:145) materializes @ point → supervisor `/spawn` → registers `.data/clones/<h>.json` + `.data/channels/<h>.json` (member). `prepare_at` (404) = operator-gated command (interactive clones never auto-spawn). Consult: `msg_clone` (211), `onboard_clone`/`onboard_fleet` (299/338, reflect-before-brief; reflection persisted to the record).
- MCP: `cc_clone(op=clone|msg|onboard|list|end|prepare|resolve)` (mcp_face/tools/cc_clone.py:35) — **NOT lead-gated in code**; any MCP session can call it. CLI read: `company clone get/list`.
- **GAPS:** (A) a SUPERVISED session can't discover its OWN transcript path to self-clone — `session_recall(session="self")` resolves it internally but doesn't RETURN `jsonl_path` (need an MCP op exposing own-source). (B) a clone's reflection is persisted to its record but NOT posted to a channel. (C) a clone registers as a DM-able supervised member but is NOT auto-added to a named/common channel.

### 2. Channels + rules/guides/project-info — channels BUILT; rules/project-info MISSING as data
- TWO systems: `cc_channels.py` (named groups, `.data/channels/_channels/<id>.json`, MCP `cc_channel`) + `session_channels.py` (cross-session fabric, append-only `agent_sessions/channels.jsonl` fold, MCP `channels`/`channel_act`). Self-serve create/members/purpose/mode = YES.
- Guides: exist as a board item type (`item_types/guide.py`) + attachable to a channel (`board_edges/attached_to.py` + `cc_attachments`).
- **GAPS:** RULES have NO representation (no field, no type, no attachment-type). PROJECT-INFO has no semantic field (docs-attachment is the closest workaround). Adding either = a new event kind + fold branch in session_channels.py, OR a new attachment_type / item_type row.

### 3. Session-history search — own + whole-corpus BUILT; the HIERARCHY is the gap
- Own session: `session_recall.recall(jsonl, query)` (session_recall.py:337) + 8 lenses (session_lens.py: find/decisions/open_loops/catch_up/timeline/directives/drift/spin_up_points). MCP `session_recall(session="self"|sid)`. Embeds :8007 pplx-4b, reranks :8008 jina, fail-loud + freshness.
- Whole corpus: `sessions(op="search")` → `session_search.py:339` over ~/corpora/claude-sessions → substrate.db (lexical) + chroma (semantic). **Scoping = `state` only; NO project/cwd/session-set filter.**
- recollection's recall: HAS `project` (exact-match) + `session_ids[]` + `sources[]` filters (search.ts:9 / recall.ts:119), exposed in ITS MCP.
- **GAP (the hierarchy):** rung (a) own ✓, (b) whole-corpus ✓, but (c) one-project and (d) session-set are LOSSY/manual in Company search (post-filter by cwd breaks k) — first-class scoping lives only in recollection. Need: project/session-set scope on Company's search.

### 4. Session storage + project hierarchy — the project FIELD exists; stamping + scoping are the gaps
- `agent_sessions/<sid>.json` FLAT dir; each record carries `project` (importer-derived from `~/.claude/projects/<project>/`, ops/agent_sessions_importer.py:215; materialized inherits it). `cwd` is the primary key; `project` is a denormalization.
- **GAPS:** (1) `Suite.list_agent_sessions()` has NO `project` param (cwd exact-match only) — project filter = O(1000) client-side scan. (2) the SUPERVISOR does NOT stamp `project` on live-spawned sessions (only `cwd`) — `agent_sessions.registered/spawned` events omit project → live sessions re-derive from cwd. (3) optional future: `agent_sessions/by-project/<project>/` layout (not urgent at ~1000 rows).
- The corpus IS already project-organized (`~/corpora/claude-sessions/<project>/`). **Tim's "storage reflects the hierarchy" intuition = mostly the project-field is there; the gap is stamping live sessions + a project scope param, NOT a storage rebuild.**

### 5. Attachments + types — attach is self-serve; add-NEW-TYPE is the gap
- `cc_attachments` (attach/detach/list/manifest/types) binds rows at `channel-memory/channel_attachments/<id>.md`; manifest is a read-time projection. `attachment_types/` registry (file-discovered): 5 types — sessions, docs, recall, board_items, cloning. Adding a type = drop `attachment_types/<id>.py` with `ATTACHMENT_TYPE={...}`.
- **GAPS:** add-a-TYPE is NOT self-serve — no MCP op (`cc_attachments` OPS lacks add_type), `reset_registry()` not MCP-exposed (file drop needs a server restart to go live), and attachment_type is NOT in `Suite._CORPUS_REGISTRIES` (suite.py:352) so generic `create(kind=...)`/`cognition_info` don't see it. No attachments CLI.

### 6. MCP surface — ~24 tools / ~86 ops, mostly exposed; bootstrap + coherence gaps
- One-tool-per-resource + `op` selector, auto-registered via pkgutil (`register(mcp, suite)`). Exposed: sessions/session_post, cc_clone, cc_gate, session_recall, channels/channel_act, cc_channel, cc_attachments, cc_board, cc_voice, create/rule/node/runs/corpus/ingest/flows, capability/marks/operator/routines/verdict_panels, context, project/layers, + server.py graph/cognition tools.
- **GAPS:** (1) session bootstrap is operator-manual (`--mcp-config channel.mcp.json` flag) — no MCP op to self-register into the fabric; announce/reply live on a SEPARATE `company-channel` server (split surface). (2) fresh-session onboarding missing (only CLONE onboarding). (3) `session_search` (whole-corpus) is NOT a clean standalone MCP tool with scoping. (4) supervisor state + service health are CLI-only (no MCP query). 

### 7. Onboarding + supervisor + frontend + design — rich substrate; the self-serve ENTRY is the gap
- Onboarding bits exist: `start_guide` (model-free ui:// tour), AddressHelp (3-leg what/how-to-use/how-to-change), GreetingCard (away-time catch-up), `capabilities()` (the "what can I do" source of truth), the clone Phase 0–4 protocol.
- Supervisor (`session_supervisor.py`, 127.0.0.1:8771): mailbox (deliver/wake/consult), spawn-flag registry (posture-derived), `/spawn /inject /watch /interrupt /teardown /bridge-session`. **The mailbox + at-point launch ARE the onboarding-delivery substrate** (can carry a Phase-1 ORIENT at spawn).
- Frontend: real design system (`design/_system/tokens.json` → `design/design-system.css`, `canvas/app/src/components/kit.tsx`, design-lint gate; GOLD-PRIMARY warm theme). Regions: Walkthrough, Fleet, AddressHelp, GreetingCard, ForagerBar (semantic search over spaces), ClaudeChat/RhmChat/Inbox/Activity/etc. API via bridge.py (/api/capabilities, /api/corpus-query, /api/greeting, /api/guide/start, /api/address-help).
- **GAPS:** no DEFAULT fresh-session onboarding flow (the pieces exist, no entry point orchestrates them); no session/project discovery MCP tool surfaced to the FE; the ForagerBar search has NO session/project/cross-project SCOPE PICKER (only space chips); no unified "welcome — your peers + capabilities + how-to" region.

---

## SYNTHESIZED BUILD SHAPE — the real new work (grouped; foundations first)

- **C1 · Search hierarchy (foundation) — FRESHNESS-not-scope (recollection's refinement, adopted 2026-06-15).** The boundary is FRESHNESS, not scope: recollection's recall ALREADY does all three scopes (own/project/cross-project) via its session_ids/project/sources filters over the backfilled corpus — do NOT parallel it. `session_recall` owns the LIVE EDGE (current session + un-backfilled tail, zero lag). A complete recall = **live-edge ⊕ deep-corpus UNIONED at the freshness seam** (one recall grammar, two freshness layers, the UNIFIED-SEAM: recollection OUTER ⊕ session_recall INNER). **Company (lead) builds:** the UNION/freshness-seam layer + the supervisor stamping `project` on live-spawned sessions (so the live edge is project-scopable) + the scoped MCP/frontend exposure. **recollection (its lane) builds:** the DELEGATION SURFACE — a filtered recall call-target (CLI/subprocess JSON preferred: symmetric to board/clone reads + reuses the session_search subprocess-bridge precedent ops/wire_substrate_claude_sessions.py; MCP recall op optional for direct agent use), landing when its backfill driver (w9wl941ro) greens. Storage already carries `project` — scoping, not a rebuild.
- **C2 · Self-serve onboarding/discoverability layer (foundation).** A fresh/spawned session self-orients: the supervisor mailbox delivers a Phase-1 ORIENT at spawn; a single onboarding answer composes `capabilities()` + live peers (`cc_channel list`) + era-clones (`cc_clone list`) + "learn the interface" (`start_guide`). Built-in guides (board `guide` items) carry the how-tos (set up scans/eras/channels/attachments/rules). Likely an `onboarding` MCP op/tool + supervisor delivery; guides as durable board items.
- **C3 · Self-serve gap closures.** Supervised own-source discovery (so a session self-clones); reflection→channel + clone→named-channel (clones discoverable in a common channel); channel RULES + PROJECT-INFO as first-class data (attachment_type or channel event); add-attachment-TYPE self-serve (MCP op + `reset_registry` exposure + promote attachment_type into `_CORPUS_REGISTRIES`).
- **C4 · MCP coherence.** Expose `session_search` (scoped) as a tool; supervisor/service health read; resolve the split `mcp_face` vs `company-channel` bootstrap so a fresh session has one door.
- **C5 · Frontend exposure (on the existing design system).** A session/project/cross-project SCOPE PICKER on ForagerBar; a unified onboarding/discovery region — built from `kit.tsx` + tokens (no bespoke), design-lint clean, navigable-not-text (FORM is half of done).

## Coordination (this build is FOR the fabric)
- The CONSUMERS are recollection · wildcard · the interface/core-ops session · future sessions — coordinate WITH them, not just build at them.
- recollection owns the cross-session/cross-project DATA layer: it is building a corpus BACKFILL DRIVER (its store had only 6 rows; the real ~13,270-conversation corpus was never backfilled). The full embed pass saturates shared :8007 for ~1–2 days (a deliberate kick it will flag) — the C1 cross-project search sits ON that backfilled corpus + Company's substrate.db/chroma. Sequence C1's cross-project rung against recollection's backfill.

## Open questions for round 2 / Tim
- ~~Cross-project search Company-vs-recollection?~~ **RESOLVED (recollection, 2026-06-15): freshness-not-scope.** recollection's recall owns ALL deep scopes; session_recall owns the live edge; UNION at the freshness seam. recollection builds the delegation surface; Company builds the union + supervisor project-stamp + exposure. (reuse-don't-parallel held — no 2nd cross-project engine.)
- Channel RULES: a new `attachment_type` (file-drop, reuses the registry) vs a channel event kind (first-class field)? (attachment_type is lighter + reuses the self-serve attach path.)
- Onboarding delivery: supervisor-mailbox ORIENT (automatic at spawn) vs a pull `onboarding` MCP op (session asks) — likely BOTH (push the orient, pull the detail).
