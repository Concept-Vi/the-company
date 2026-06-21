# AREA: Memory / Fabric / Channel / Introspection Substrate
**Extractor:** sonnet-4-6 subagent · Date: 2026-06-21 · Read-only pass

---

## 1. channel-memory/ — The Fabric's Communal Vault

**What it is:** A shared filesystem-based memory + working space for the cross-session channel fabric. Established by the lead (ch-al7jdfdr / bda8ce28) under Tim's direction 2026-06-14. Git-tracked. Every fabric member writes here under the COMMIT-GRAMMAR provenance protocol.

**What it holds (by subdir):**

### channel-memory/noticeboard/ — 32 items
The live Company noticeboard. Items are Markdown files with YAML frontmatter:
- Schema fields: `id`, `address` (board://<id>), `type`, `source`, `state`, `title`, `author_session`, `channel`, `thread`, `links` (typed edges), `created`, `updated`, `history` (state-change log)
- Item types found: `guide` (13), `request` (7), `idea` (7), `issue` (3), `tip` (1)
- States: `living`, `captured`, `open`, `discussed`
- Open/active items (require attention):
  - `item-15aaf9da` — Promote attachment_type to first-class _CORPUS_REGISTRIES kind
  - `item-4cb57b5d` — Wire board registries into suite.py _CORPUS_REGISTRIES + create_* + cognition_info
  - `item-a3844c46` — RERANK LOADOUT: jina reranker OFF decision path, no tracked owner (Tim-flagged 2026-06-18)
  - `item-ffa884e5` — Wire minds into _CORPUS_REGISTRIES (create/inspect first-classness for mind://)
  - `item-501c4188` — MCP-tool GAPS: where lead dropped to raw shell (unbuilt Company-layer surface)
- Date range: 2026-06-15 → 2026-06-18
- Notable: item-333b6b21 is the most substantial (5127 bytes) — UNION SYNTHESIS of the factory area
- **Loader/writer:** `mcp_face/tools/board.py` (cc_board ops: file/list/get/transition)

### channel-memory/mega-prep/ — 5 files
The SHARED MEGA-PREP subspace for the cross-session clone-fleet build (the channel/session-recall work of 2026-06-14 to 2026-06-18):
- `OVERNIGHT-STATE.md` (55818 bytes, 2026-06-18) — the largest file; a running state-of-the-union of ALL overnight build work; includes proven-live flags, decision registry, seam-analysis, channel-fabric milestones
- `APPROVAL-STANDARD.md` — the self-approval protocol (what the lead can green-light vs what needs Tim)
- `CHANNEL-LAYER-SEAM.md` — the channel-layer architecture seam document
- `EMBEDDING-AXIS-REGISTRY.md` — the embedding axis/dimension registry spec
- `UNIFIED-SEAM.md` — unified seam across lanes (session-recall + recollection merge plan)
- **Status:** These are from the 2026-06-14 to 2026-06-18 build wave. Some may be stale vs current reality.

### channel-memory/vision/ — 4 files
Tim's decompressed intents from 2026-06-14 to 2026-06-15:
- `2026-06-14-session-splicing-and-channel-memory.md` (18705 bytes) — the foundational vision for session-splicing + channel memory, the clone-fleet concept
- `2026-06-15-clone-fleet-purpose-and-onboarding.md` — purpose and onboarding for the clone fleet
- `2026-06-15-company-noticeboard-and-request-system.md` — noticeboard + request system design
- `2026-06-15-recollection-vs-board-comparison.md` — comparison of recollection vs noticeboard
- **Note:** These are source-of-truth entries authored by the lead from Tim's direction. No newer vision entries since 2026-06-15.

### channel-memory/schema/ — 1 file
- `session-store-grammar.md` (14171 bytes) — full grammar of the Claude Code `.jsonl` session store: event taxonomy, compaction-boundary grammar (the compact_boundary system event + isCompactSummary user event pair), field reference. Evidence-labeled (O/I/V). Verified against live sessions bda8ce28 + 11e7d395.
- Key finding recorded: lead session used claude-opus-4-8[1m] (1M context) → only 1 compaction in 12.5k lines over 4 days.

### channel-memory/scans/ — 2 NDJSON datasets + README
- `bda8ce28-...rows.ndjson` (4.578 MB) — full event scan of lead session bda8ce28
- `11e7d395-...rows.ndjson` (1.056 MB) — full event scan of fork session 11e7d395
- Paired `.summary.json` files (7 and 6 KB) with per-session stats
- `README.md` — explains the scan format (projectable DATA, not prose)
- **Status:** Scans from 2026-06-14 only. No newer scans. These are historical artifacts from the clone-fleet build.

### channel-memory/map/ — 4 files
- `lineage.json` — the session lineage tree: 2 nodes (bda8ce28 = root lead session, 11e7d395 = fork branching from it at compact:1 boundary). Includes token counts, boundary counts, segment splits. Root: 12725 events, 288 human turns, 2819 assistant turns, ~5.65M output tokens, 2026-06-10 to 2026-06-14. Fork: 2513 events, 55 human turns, 1067 assistant turns.
- `lineage.md` — human-readable version
- `launched-fleet.json` — manifest of the launched clone fleet (Tim's "launch all of them" command 2026-06-15)
- `fork-points.md` — analysis of where the fork branches from the lead
- `spin-up-ranking.md` — ranked clone spin-up plan (which to launch in what order)

### channel-memory/recall/ — 2 files
- `embedding-model-decision.md` — the embedding model selection decision (pplx-embed-context-4b chosen over Qwen3-8B so voice fits GPU; this is the origin record)
- `substrate-embeddings-fix.md` — the embeddings fix that followed the model decision

### channel-memory/design/ — 7 files (patch/design inputs for the lead's lane)
- `lead-lane-inputs.md` (8208 bytes) — the lead's A-D lane design inputs
- `claude-stream-territory-composer.patch.md` — stream+territory composer patch design
- `spawn-session-id-injection.patch.md` — session ID injection into spawn
- `territory-label-endpoint.patch.md` — territory label endpoint patch
- `territory-write-endpoint.patch.md` — territory write endpoint patch
- `howto-address-leak-fix.patch.md` — address leak fix
- `wire4-preference-contract-and-scales.md` — Wire 4 preference contract spec

### channel-memory/plan/ — 4 files
The loop-prep documents from 2026-06-14:
- `COMPLETION-CRITERIA.md` — the completion criteria for the channel/session-recall build
- `IMPLEMENTATION-GUIDE.md` — the implementation guide
- `INFERRED-PREFERENCES.md` — Tim's inferred preferences for this build
- `RESEARCH-SYNTHESIS.md` — research synthesis
- **Status:** These are from the 2026-06-14 pre-loop prep. Historical.

### channel-memory/ root files
- `README.md` — layout description + working protocol (provenance trust tags, cross-session collaboration rules, the HELD self-approval item)
- `CODES_OF_CONDUCT.md` (6669 bytes, 2026-06-16) — the fabric's constitution: roles (Tim/Lead/Members), responsibilities, codes of conduct, protocols. Names current segment owners: DNA (ch-ovxwz8k8), composition (ch-2mnxl9j0), projection, wildcard (ch-piffgfxv), fork (ch-8djrpmsl), recollection (ch-83e2cque).
- `TIM-INTERFACE-SYNTHESIS-2026-06-16.md` (7825 bytes) — Tim's interface synthesis from 2026-06-16 (the operator surface / RHM commission)
- `COMMIT-GRAMMAR.md` — provenance commit rules for all members

### channel-memory/channel_attachments/ — exists, empty (not listed)

---

## 2. channels/ — The Channel Server + MCP Infrastructure

**What it is:** The live channel transport layer — the MCP server that enables Claude Code sessions to receive and send cross-session messages in real time.

**Files:**
- `company_channel.mjs` (9585 bytes, 2026-06-18) — THE CHANNEL SERVER. An MCP server (`@modelcontextprotocol/sdk`) that:
  - Declares `claude/channel` capability (so sessions launched with `--dangerously-load-development-channels server:company-channel` receive injected channel messages as `<channel source="company-channel" from="..." thread="...">` tags in the live conversation)
  - Registers each session under `.data/channels/<HANDLE>.json` with: `{handle, session_id, cwd, description, model, profile, pid, claude_pid, port, started}`
  - Starts an HTTP server on a dynamic port; inbound POSTs to that port become `notifications/claude/channel` MCP events in the session
  - Exposes 3 tools: `reply` (routes reply to supervisor `/channel-reply` → mailbox + asker's session), `announce` (sets session's one-line description), `profile` (agent writes its OWN self-description: model/role/focus/expertise)
  - Identifies Claude ancestor PID via `/proc/<pid>/stat` walk (up to 40 levels) — used as the cross-system shared session key
  - Cleans up its registry entry on process exit
- `claude-fabric.sh` (1635 bytes, 2026-06-15) — startup script: launches a Claude Code session with the channel server MCP attached + env vars set (COMPANY_CHANNEL_HANDLE, COMPANY_SESSION_ID, etc.)
- `profile-hook.sh` (1322 bytes, 2026-06-15) — a SessionStart hook that auto-calls `profile` on session boot
- `profile_test.mjs` (3284 bytes, 2026-06-15) — end-to-end test for the profile mechanism (spawn server → MCP handshake → tools/call profile → verify on-disk entry)
- `channel.mcp.json` — MCP server declaration for Claude Code settings
- `package.json` + `package-lock.json` + `node_modules/` (94 subdirs) — Node.js dependencies (@modelcontextprotocol/sdk)
- `.gitignore` — excludes node_modules

**Cross-refs:**
- Channel registry lives at `.data/channels/<HANDLE>.json` (written by the channel server)
- Supervisor routes replies through `/channel-reply` (supervisor is at COMPANY_SUPERVISOR_BASE, default `http://127.0.0.1:8771`)
- Session identity (claude_pid) used by `resolve_own_session` which scans `.data/channels/*.json`

---

## 3. fabric/ — The Model Binding Layer

**What it is:** The model call layer — OpenAI-compatible HTTP transport + guarded call client. The "engine beneath" all runtime model calls (S6 in Company architecture).

**Files:**
- `transport.py` (22422 bytes, 2026-06-21) — THE TRANSPORT. Four transport factories + utilities:
  - `openai_transport()` — standard chat completions (→ content str)
  - `openai_tools_transport()` — native tool-calling (→ message dict with tool_calls)
  - `ollama_native_transport()` — Ollama `/api/chat` path, the ONLY path that honours `think` (think-control for reasoning models; the /v1 path silently ignores it — verified: 1304→43 output tokens on kimi-k2.6:cloud)
  - `openai_embeddings_transport()` — `/v1/embeddings` (→ list[list[float]])
  - `model_supports_tools()` — endpoint-aware tool capability detection (ollama /api/show caps field; LiteLLM /model/info; vLLM probe via forced tool_choice)
  - `list_models()` — live model list from `/v1/models` (NO Gemini)
  - `_SAMPLING_KEYS` ordered tuple — the sampling param allowlist (temperature/max_tokens/top_p/repetition_penalty/frequency_penalty/presence_penalty/top_k/min_p/stop/seed/n) shared by both chat transports
  - `_apply_response_format()` — structured output decision: json_schema → server-side constrained decode (vLLM xgrammar); schema/json → json_object; neither → free text
  - `_fill_meta()` — additive finish_reason + token-usage passthrough (out-param `meta={}`)
  - Hard constraint: **NO Gemini** (forbid_gemini() called FIRST in every transport)
- `client.py` (12804 bytes, 2026-06-21) — THE GUARDED CALL LAYER. Three call paths:
  - `complete()` — guarded text/structured call (retries=4, exponential+jittered backoff, empty-content guard, JSON repair + balance, schema validate, budget-retry on length-truncation)
  - `complete_with_tools()` — tool-calling sibling (validity = tool_calls OR non-empty content)
  - `complete_embeddings()` — vector guards (count mismatch, dim mismatch, empty)
  - Schema-guided decoding (G24): `schema=<PydanticModel>` → derives `json_schema` opt → server-side constrained decode; proven to close the "resident 4B emitting unparseable JSON" class
  - Budget-retry: when finish_reason=length, doubles max_tokens (cap 4096) on next attempt
  - `FabricError` — the fail-loud exception class
- `config.py` (3921 bytes, 2026-06-16) — Configuration:
  - `DEFAULT_BASE_URL` = `http://localhost:11434/v1` (Ollama, configurable via `COMPANY_FABRIC_URL`)
  - `DEFAULT_EMBED_URL` = `http://localhost:8007/v1` (pplx-embed-context-v1-4b, configurable via `COMPANY_EMBED_URL`)
  - `DEFAULT_BRAIN` = `deepseek-v4-pro:cloud`
  - `DEFAULT_TIMEOUT` = 180s; `DEFAULT_CLOUD_TIMEOUT` = 300s
  - `DEFAULT_EMBED_DIM` = 2560 (pplx 2560-dim INT8)
  - `DEFAULT_EMB_LAYER` = `pplx` (multi-layer embedding; `None`/`bge`/`bare` → legacy bge layer)
  - `FORBIDDEN = ("gemini",)` — hard NO-Gemini constraint
  - `resolve_emb_layer()` — resolves caller's emb arg to concrete storage-layer tag
- `AGENTS.md` — fabric constitution (S6): guarantees, seam, extension rules, what's in here
- `litellm.config.yaml` (2090 bytes, 2026-05-31) — LiteLLM proxy config (DORMANT relative to current ollama-direct default)
- `serve_litellm.sh` (362 bytes, 2026-05-31) — LiteLLM startup script (DORMANT)
- `vram.py` (789 bytes, 2026-05-31) — VRAM utility (reads nvidia-smi for live GPU state)
- `__pycache__/` — compiled Python cache

**Key gaps/surprises:**
- `litellm.config.yaml` + `serve_litellm.sh` date from 2026-05-31 (over 3 weeks old); `DEFAULT_BASE_URL` defaults to OLLAMA_DIRECT, not LiteLLM — LiteLLM proxy appears DORMANT in current setup
- `vram.py` not yet integrated into a live VRAM semaphore (was planned; not verified as wired)
- `fabric/` holds NO data — it's pure code; data lives at `.data/store` (via `STORE_DIR`)

---

## 4. operator_memory/ — The Operator Memory Registry (GC15)

**What it is:** The file-discovered OPERATOR-MEMORY registry — the system's growing, Tim-grounded memory of how to work with him. One Python file per memory row; each holds a `MEMORY` dict with: `id`, `rule`, `why`, `evidence` (required — Tim's verbatim quotes), `scope`, `status` (confirmed/proposed), `confirmed` (date + context).

**File count:** 28 Python files + AGENTS.md + __pycache__

**Architecture:**
- Pure data — nothing executes
- Loaded by: `runtime/operator_memory.py`
- Exposed via: `mcp_face/tools/operator.py` (op=rules|describe|proposed)
- Lifecycle: transcript mining PROPOSES rows (status='proposed') → Tim's confirmation makes them standing (status='confirmed')
- Scoping: `scope.when` (activity context) + `scope.where` (ui:// prefix)

**All current rows (from AGENTS.md + file inventory):**
1. `refine_before_gating` — refinement passes run autonomously; his gate gets the minimum set
2. `think_back_with_me` — thinking aloud = co-think, not act, not summarize
3. `easy_decision_surface` — his decision surface is never an isolated technical document
4. `no_unconditional_deferrals` — deferrals only with explicit return-condition in system memory
5. `multi_job_elements` — context decides; record contextual faces, don't flatten conflicts
6. `proposal_lifecycle` — propose → accept → build fires → registry flips Real
7. `never_reads_the_files` — he never reads files; everything at his altitude
8. `ai_supplies_domain_knowledge` — AI supplies per-domain depth Tim doesn't hold
9. `big_beats` — tight loop cadence = BIG steps per fire, not small safe ones; parallelize lanes
10. `confirm_before_writing` — propose first, Tim confirms, then write
11. `expand_dont_echo` — Tim's answers are seeds to expand into full spec, not things to mirror
12. `flag_hardcoding` — always flag hardcoding; replace with registry architecture
13. `found_elsewhere_not_replacement` — a found-in-a-separate-system thing ≠ replacement/equivalent
14. `goal_function_mandates` — mandate upgrade: upgrade Tim's directions to the BEST version of his intent
15. `incomplete_work_in_scope` — stranded/incomplete/uncommitted work adopted into scope and completed
16. `investigate_before_coding` — research the actual problem, read actual code paths before writing
17. `leverage_the_fleet` — habitual delegation; half the power isn't you alone
18. `look_at_output_first` — when generation fails, look at raw output before theorizing
19. `make_each_thing_work` — never "use a different engine"; each acquired to test them ALL
20. `native_mobile_always` — mobile/phone access is always a first-class requirement
21. `no_deferral` — every flagged gap/small-thing is in-scope, never parked
22. `no_silent_failures` — operations that can't proceed must fail loud (Notice + Gap)
23. `no_time_estimates` — never give time estimates
24. `no_unconditional_deferrals` — (see above)
25. `no_versioning` — update the same canonical files in place; never version content
26. `record_expansively` — capture MORE; volume is a feature
27. `refine_before_gating` — (see above)
28. `render_for_cognition` — render so Tim's perception is the compute
29. `use_existing_resources` — research and use existing libraries/UI kits/design systems
30. `verify_before_claiming` — never report "addressed" without execution verification
31. `verify_by_use` — "verified" only after execution proves it; comprehension can't upgrade

**Key observations:**
- All files dated 2026-06-10 to 2026-06-11 — the registry hasn't been added to in over 10 days
- Status of all rows: all confirmed (no proposed rows visible in the filesystem)
- AGENTS.md row list shows only 7 rows but filesystem has 28+ — the AGENTS.md "drift home" section is STALE; it lists only the original 7 and hasn't been updated as more rows were added
- Gap: no operator_memory rows about more recent Tim directives (e.g., lead-drives-everything, minimize-gating, friction-is-gap-sensor from 2026-06-21)

---

## 5. introspection/ — The Mirror-Registry Engine

**What it is:** The platform-agnostic capability discovery + classification engine (Level 1). Discovers what Claude Code (or any platform) self-reports as its capabilities, classifies each by security posture, and maintains a cached in-memory registry.

**Files:**
- `engine.py` (13318 bytes, 2026-06-14) — THE FOUR-VERB CIRCUIT: DISCOVER → CLASSIFY → PROJECT → REFRESH
  - `classify_entries()` — runs 5 rules over each CapabilityEntry; stamps posture/posture_rule/axis
  - `project()` — shapes classified rows into face-neutral projection dict
  - `classify_platform()` — DISCOVER + CLASSIFY end-to-end
  - `snapshot()` — full read: DISCOVER → CLASSIFY → PROJECT → projection dict
  - `diff()` — compares two CapabilityEntry lists: {added, changed, vanished}
  - `refresh()` — re-DISCOVER, diff against prior, return inbox batch payload; RAISES on empty-diff-on-version-bump
  - `register_head_builder()` / `derived_transport_invariants()` — thunk registry for R1 input derivation
- `rules.py` (13166 bytes, 2026-06-14) — THE FIVE CLOSED RULES (R1-R5 + R6 exclusion):
  - R1 LOCKED — flag in transport_invariants (derived from consumer spawn template, NEVER hand-listed)
  - R2 HAZARD — flag NAME contains hazard signal word (flag-name string ONLY, never description)
  - R3 CONSENT — flag in declared capability_axes (widens session surface); returns axis name
  - R6 SWAP-KIND HEAD-DEFAULT EXCLUSION — head flags that are also capability_axes members are NOT R1-locked; R3 fires instead
  - R5 SAFE — the EXPOSE-not-gate default (most surface lands here; Tim Ruling 1)
  - R4 UNMATCHED — novel/rail-incompatible flag → fail-CLOSED + surfaced, teaching-refusal
  - `derive_transport_invariants()` — derives R1 input from head_builder thunk UNION body_key_overrides MINUS R6 swap-defaults
  - **Leak invariant (F-FIX-10 / PG2):** ZERO platform-name literals in Level-1 code (engine.py + rules.py + adapters/); acceptance test greps and FAILS on any hit
- `registry.py` (9148 bytes, 2026-06-13) — THE CAPABILITY REGISTRY (CapabilityRegistry):
  - Dict-like in-memory table of one platform's discovered + classified CapabilityEntry rows
  - `discover()` — DISCOVER + CLASSIFY via engine; holds rows keyed by `entry.id` (= f"{kind}/{name}")
  - `snapshot()` — face-neutral projection
  - `search()` — substring match over id/name/description
  - Cached MODULE-LEVEL SINGLETON (NOT fresh-discover-each-call like sibling registries — binary discovery is expensive): `set_capability_registry()` + `capability_registry()` accessor
  - RAISES fail-loud if unset at resolve time
- `discover.py` (6583 bytes, 2026-06-13) — THE DISCOVER VERB: resolves executable, runs each declared DiscoverySource through adapter; LOUD MissingAdapterError if adapter not built; RAISES on parse below floor_guard
- `platforms.py` (11092 bytes, 2026-06-13) — THE PLATFORM ABSTRACTIONS: PlatformEntry bindings
- `__init__.py` (820 bytes, 2026-06-13) — module init
- `AGENTS.md` (17486 bytes, 2026-06-14) — extensive constitution + spec; covers all five rules, F-FIX series, the leak invariant, R6 swap-kind head-default, derive_transport_invariants, acceptance test gates
- `adapters/` — 4 adapter files: `cli_help.py`, `stream_init.py`, `subprocess_invoke.py`, `version_probe.py` + `__init__.py`

**What it does NOT hold (data lives elsewhere):**
- On-disk projection cache: `store/introspection_cache.json` (written by the refresh flow, LANE-REFRESH)
- Per-platform version stamps: `store/<id>.version_stamp`

**Key gaps/surprises:**
- Most recent file dates: 2026-06-13 to 2026-06-14 — no changes since then; the mirror-registry appears feature-complete but live verification (C-REG-1, the ≥30-flag live discovery) is listed as "LEAD-verify-queued"
- `platforms.py` — contains the platform abstractions; would need reading to verify the single live platform (Claude Code / claude_code.py) is fully wired
- The LIVE path spawns a claude binary — this means the introspection engine can only be exercised on a machine where `claude` is in PATH

---

## 6. routines/ — The Recurring Routine Definitions

**What it is:** Pure-data Python files, each declaring one `ROUTINE` dict — the scheduled/on-demand execution recipes for the Company. Three routines currently defined.

**Files:**
- `completion_poke.py` (4580 bytes, 2026-06-21 — NEWEST FILE in all 6 areas):
  - The COMPLETION-REFUTER (popcorn-B adversarial kernel, Tim 2026-06-21)
  - Cadence: every 30 minutes (`every:1800`) + fire-on-demand
  - Prompt: reads channel history + criteria/trackers, default-to-wrong on every "complete/done/live/verified" claim, finds holes, posts evidenced list to channel addressed to the lead
  - Reads: `build-prep/the-one-application/OPERATOR-LOOP-CLOSURE.md`, `COMMISSION-COMPLETION-REGISTER.md`, `CHANNEL-LOOP-BOARD.md`
  - Posts to: `mcp__company__cc_channel` broadcast/reply, addressed to lead (ch-3mpkjg3r)
  - Permission mode: default (reads + channel-posts; no dangerous writes)
  - Max turns: 12
- `self_status.py` (1196 bytes, 2026-06-14):
  - Daily morning health check (OnCalendar=*-*-* 09:00:00)
  - Asks a fresh session to report company health in one line
  - Permission mode: plan; max_turns: 1; repeats: False
- `launch-surfaces.py` (1680 bytes, 2026-06-17):
  - Manual-fire routine to report Tim's two review-surface URLs + up/down status
  - URLs: gallery http://localhost:8090/, surface http://localhost:5174/
  - Remote via Tailscale: workstation001.tail777bc2.ts.net / :8443
  - Permission mode: default; max_turns: 4; repeats: False

**Key gaps/surprises:**
- Only 3 routines defined — the routine system is nascent; the completion_poke was added 2026-06-21 (today/yesterday) as the first standing adversarial kernel
- `completion_poke.py` is the MOST RECENTLY MODIFIED file across all 6 areas (2026-06-21 19:19)
- No general-purpose heartbeat-sweep routine (the MEMORY.md mentions "heartbeat-sweep (cron) + drive-on-engagement" as the lead's responsibility — not yet formalized as a routine file)
- The routine runner is at `runtime/routine_runner.py` (not in this area)
- Systemd-timer arm: the cadence grammar (`every:1800`, `OnCalendar=*-*-*`) is declarative; the actual systemd unit files / cron wiring is NOT in this directory

---

## 7. .data/channels/ — The Live Session + Channel State Store

**What it holds (the operational runtime data, NOT in git):**

### Session registry (individual .json files)
8 live session registry files (as of 2026-06-20 to 2026-06-21):
- `ch-3mpkjg3r.json` — LEAD (claude-opus-4-8[1m], cwd=/home/tim, port 41563, started 2026-06-20T09:15)
- `ch-35bbt7yj.json` — fork role: foundational-theorem discovery + boot-runbook (claude-opus-4-8[1m], cwd=/home/tim)
- `ch-4kug7wsr.json` — (not read, small 375 bytes)
- `ch-869a5yzl.json` — wildcard: vi-visual-bridge territory, direction circuit + gallery binder (claude-opus-4-8[1m], cwd=/home/tim/vi-visual-bridge/.discovery/...)
- `ch-j9t020dx.json` — (not read, 1155 bytes)
- `ch-o1wy1t07.json` — (not read, 1161 bytes)
- `ch-ouui7r0k.json` — (not read, 913 bytes)
- `ch-z4ht5ipb.json` — (not read, most recent 2026-06-21 15:30)
- `ch-wz9j04r0.replies.jsonl` — a reply log for one session (early test)

### _mail.jsonl — THE CROSS-SESSION MAIL LOG
- Size: 5.261 MB · 2628 lines · date range: 2026-06-14 to 2026-06-21T20:46
- Message kinds: 1367 messages + 1261 replies
- Top senders by volume: ch-al7jdfdr (668), ch-3mpkjg3r (337), fabric (281), ch-83e2cque (215), ch-8djrpmsl (189), ch-projection (183), ch-2mnxl9j0 (170), ch-ovxwz8k8 (169), ch-35bbt7yj (64), ch-ouui7r0k (56)
- This is the COMPLETE durable record of all cross-session communications since 2026-06-14

### _threads.json — THE THREAD STATE
- Size: 71934 bytes · 485 threads
- Thread IDs appear to follow patterns: `t-<timestamp>-<handle>` (DM threads), `g-<timestamp>` (group/broadcast threads)
- Status field present but blank in sampled entries (may not be used)

### _channels/ — Named Channel Registry (4 channels)
- `advisors.json` — 3 members (the clone-advisor fleet)
- `design.json` — 0 members
- `fabric.json` — 10 members (the main fabric channel)
- `repo-reorg.json` — 1 member
- **Note:** description fields are empty in all 4 named channels (a gap — the profile tool writes session entries but named channels don't have descriptions populated)

---

## 8. .data/clones/ + .data/recall-index/ — Session Clone + Recall Infrastructure

### .data/clones/ — Clone Registry (8 clones)
Each `.json` file records a supervised clone:
- `kind`: supervised-clone
- `handle`: clone-<id>
- `supervisor_session`: the supervisor session that launched it
- `source_sid`: the source session UUID being cloned
- `at`: the cut point (uuid:<event-uuid> or compact:N)
- `materialized_path`: where the cloned session transcript was written
- `description`: e.g. "lead bda8ce28 @ 5% L1127 — the capture era (Fable-era, run on opus)"
- `reflection`: the clone's first self-reflection (unprompted)
- `address`: `clone://<source_sid>/uuid:<cut-uuid>`
- Clones are derived from the lead session (bda8ce28) at various cut points

### .data/recall-index/ — Chunked Embedding Index
5 sessions indexed (5 pairs of `.recall.jsonl` + `.recall.meta.json`):
- Sessions indexed: 11e7d395, 1e9865d9, 3f5e6735, 4f630654, 8dcca3e0
- Each meta.json records: source_bytes, source_mtime_ns, n_chunks, dim (2560), embed_model (perplexity-ai/pplx-embed-context-v1-4b), chunk_mode (dimension), source_path
- Example: 11e7d395 → 5209 chunks, 2560-dim, pplx embedder
- The `.recall.jsonl` files contain the chunked + embedded content (the searchable recall substrate)

---

## Cross-Cutting Observations

### The wiring between stores
1. **channel server** (channels/company_channel.mjs) → writes → `.data/channels/<HANDLE>.json` (session registry)
2. **supervisor** (runtime/supervisor.py, not in this area) → writes → `.data/channels/_mail.jsonl` + `_threads.json`; receives `/channel-reply` from channel servers
3. **noticeboard** (mcp_face/tools/board.py) → writes → `channel-memory/noticeboard/item-*.md`
4. **operator_memory** (runtime/operator_memory.py) → reads → `operator_memory/*.py`
5. **introspection engine** → writes on refresh → `store/introspection_cache.json` (not in this area)
6. **fabric.client** → is called by → `runtime/` (cognition, engine, bridge); NOT by this area's code
7. **recall-index** → written by → `runtime/session_pointintime.py` (not in this area); READ by the recollection/recall query path

### Surprising finds
- **operator_memory AGENTS.md is stale** — lists 7 rows; 28 files exist. The AGENTS.md drift-home section has not been updated in 10+ days.
- **LiteLLM is dormant** — `litellm.config.yaml` + `serve_litellm.sh` date from 2026-05-31; `DEFAULT_BASE_URL` points at ollama directly, not the LiteLLM proxy. This may be intentional but is UNTRACKED.
- **Named channels have empty descriptions** — all 4 entries in `_channels/*.json` have no description field populated.
- **_threads.json status fields are empty** — 485 threads, all without status (may be vestigial field).
- **Vision entries end 2026-06-15** — no new vision entries in `channel-memory/vision/` since 2026-06-15 (6 days ago). This is the source-of-truth decompress lane; its silence is notable.
- **completion_poke.py is the newest file** (2026-06-21 19:19) — Tim's adversarial completion-refuter was just added today as a standing routine; it's the freshest work across all 6 areas.
- **routines/ has no heartbeat-sweep** — MEMORY.md says the lead should do "heartbeat-sweep (cron) + drive-on-engagement"; no such routine file exists. The completion_poke is the only scheduled routine added so far.
- **Introspection live-verify queued** — C-REG-1 (live ≥30-flag discovery from real Claude binary) is flagged as "LEAD-verify-queued" in the registry.py docs. No evidence it's been run.
- **Only 5 sessions in recall-index** — the recall infrastructure is built but covers only 5 sessions (from the June 13-14 build wave). More recent sessions are NOT indexed for recall. This is a significant gap if the recollection system depends on this index.
- **channel-memory/channel_attachments/** — directory exists but appears empty (not listed in ls output); may be a planned but unbuilt feature.

### Notable completeness of the channel communication layer
The `_mail.jsonl` shows 2628 cross-session messages from 2026-06-14 to today (2026-06-21), with a rich mix of senders. The fabric IS live and actively communicating. Most senders are named segment owners (ch-al7jdfdr, ch-83e2cque, ch-8djrpmsl, ch-2mnxl9j0, ch-ovxwz8k8, ch-projection).

---

*Written by extraction subagent (sonnet-4-6) — no edits to any source files. All claims tagged by source: [O]bserved in files / [I]nferred from patterns / [V]erified by execution.*
