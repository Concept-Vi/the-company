# DISCOVERY SYNTHESIS — supervisor · coordinator · engines · context-layering · UI seam (2026-07-09)

*The system-wide research campaign Tim mandated before any build ("anything short of system-wide checking
will cause a gap or splinter — that's just a fact"). Five parallel explorations, all file:line-grounded,
full reports preserved in the agents' outputs; this is the composite. Nothing here is canon — all of it
is AI-built residue examined by AI; claims carry their evidence class.*

## 1. THE ENGINE CENSUS — Tim asked: "trigger/rule/condition engines… finished or connected? basically 0?"
His intuition was RIGHT for the middle layers, WRONG (happily) for the newest, and missed one ACTIVE BREAK:

| # | Engine | Fires | Built? | Connected/armed? |
|---|---|---|---|---|
| 1 | **jobs.py trigger_tick** (schedule/change/condition, edge-detect) | deterministic handlers/cascades/roles/flows | FULLY | **LIVE — 5 armed jobs ticking ~60s** (verified in /proc + trigger_state) |
| 2 | **scheduler.py** (address-readiness dataflow; memo-gated) | graph nodes | FULLY (mature, "the heart") | LIVE via Suite.run |
| 3 | **rules.py G3 AST** (role-output routing; Tim: "the main mechanism all of this is aimed at") | inject/chain/address/surface/lane | FULLY, tested | LIVE on EVERY reply assembly — but only ONE declared rule in use |
| 4 | **mode_detection_rules.py** | mode candidates | FULLY | LIVE (deliberate reuse of #3's grammar — the GOOD pattern) |
| 5 | **hookify** (~/.claude, 15 behavioral rules) | warn/block on CC lifecycle | FULLY | **BROKEN-WHILE-CLAIMING-ARMED**: config_loader.py:210 uses a bare relative glob `('.claude', 'hookify.*.local.md')` — loads ONLY when cwd==~ . Reproduced: from /home/tim/company → matched []. Tim's 15 global rules (no-speculation, verify-before-done…) have NEVER fired in any project session. The Supabase repo's own 8 scoped rules DO fire. |
| 6 | **agent_mcp.response_rules** (Supabase substrate) | [response-rule] blocks on tool calls | FULLY | LIVE — measured fired_counts (2/2/17/0/3) |
| 7 | **agent_mcp.systems** (runnable state machines, SQL conditions) | held runs | FULLY | LIVE, on-demand (2 systems) |
| 8 | **routines** (+ routine_schedule systemd generator) | full `claude -p` sessions | runner+generator YES | **0 timers enabled** (2 generated, never armed — by stated law) |
| 9 | **dials** (condition-scoped overrides in rules-AST shape) | nothing | get/set YES; evaluation STUBBED (honest: overrides_evaluated=False) | zero consumers |
| 10 | **cc_gate** (observer on CC's native pause) | — | tested | never invoked (.data/gates absent) |
| 11 | flows / mark_types / cascades | — | manual-by-design (NOT reactive; confirmed intent) | n/a |
| 12 | drift_radar / orienteering_drift / coherence_detect | marks | built | pass-invoked only (a different genus: detection, not arm+fire) |
| 13 | bridge daemons (_freshness_loop, commit-drain, warm-cache) | reindex/drain | built | LIVE right now |
| 14 | **build-prep/trigger-system DESIGN** (runtime/triggers.py + trigger_driver + cc_launch) | CC sessions off board events | **0% built** (verified absent) | the THIRD trigger concept, design-only |

**THE DEDUP VERDICT (design-for-the-class):** three "event→fire" concepts exist at three resolutions:
jobs.py (live) · routines (built-not-armed) · trigger-system design (unbuilt). The spine is **jobs.py** —
its RUN_KINDS already says "graph/agent land later". Extending RUN_KINDS with an `agent`/`routine` kind
(fire a supervised Claude session as a job body, via the NOW-RUNNING supervisor) retires both others with
no new engine-shaped code. Naming collisions to clean: rule.py vs reduce_rule_names; three "freshness"es.

## 2. THE CONNECTION MAP — RHM · supervisor · concurrent cognition
- **RHM** = a role resolving to a model (rhm_config → resident vLLM), living in Suite.chat()/chat_parts().
- **Concurrent cognition IS wired into the RHM's turn**: chat_parts fires run_swarm concurrently
  (registry-derived SlotBudget, VramGate, CLOUD_FAN_SLOTS) and injects into Part 2. LIVE via
  /api/chat/stream + /api/voice/stream. **BUT only the old disposable canvas UI calls those** — the new
  surface app reaches only /api/brain/ask (separate, non-swarm, kimi-routed). The swarm is unreachable
  from the forward-facing UI.
- **Supervisor ↔ cognition: ZERO wire** either direction (both files grepped).
- **RHM ↔ supervisor: one read-only lens** — brain_router._fleet_answer sees the roster, may PROPOSE a
  wake, never fires one.
- **What Tim remembered being "connected" = ops/owui_room.py**: a real live wire, room → supervisor
  /bridge-session, spawning Claude sessions (incl. the 'operator' persona). It is a room↔spawner wire,
  NOT an RHM-brain wire (owui_room has zero refs to rhm_config/brain_router/cognition; the code's
  comments blur "operator"/"RHM" — different code objects).

## 3. SUPERVISOR STATE (this branch's work, done)
First-ever run 2026-07-09: healthy on :8771 (cap 3, plan-mode). PROVEN: spawn → inject → reply
("SUPERVISOR-PROOF-OK") → watch replay → teardown clean. Now a managed always-on service.
Full anatomy: /health /sessions /watch(ndjson replay+live) /spawn /inject /interrupt(untested-vs-real)
/teardown /bridge-session(consent-gated wider profile) /channel-reply /channel-send. Mailbox verbs
deliver/wake/consult (+at= time-travel); head-of-line blocking is a stated F1 simplification.
Spawned world: company-MCP only (never the node channel server — cc_channels has a synthetic-reply
workaround), plan default, CLAUDE.md/skills load per normal -p, prompt = first injected turn.
Knobs: COMPANY_FABRIC_CONCURRENCY/PERMISSION/TURN_TIMEOUT_S/INIT_WAIT_S/SPAWN_SETTLE_S,
COMPANY_BRIDGE_SESSION_PERMISSION, per-spawn model/effort/permission/provider=ollama(!).
Gotchas: INIT_WAIT dead weight (min() with 1.0s settle); resume-stderr overflow fixed via drain thread;
wake-cwd fallback chain can surface as opaque spawn failure.

## 4. THE COORDINATOR — machinery vs the unproven step
Conducted-mode channels are BUILT + unit-proven (80 checks): a post routes ONE context-laden intent to
the coordinator (you_are=coordinator + members + how_to_work_the_channel: session_post per member on the
same thread; inbox to read; report back to the asker). NEVER wakes the coordinator (queue if closed — a
deliberate law). THE UNPROVEN STEP (STATE.md's own 🟡): a coordinator ACTING on its intent has never run
live. Persona precedent: owui op_spawn_operator (prompt = first-turn persona + register_supervised_member
for channel addressability). Hard-won convergence lesson (ingest-session's FINDING-0): handles churn —
the coordinator must address by durable ids, never ch-XXXX.

## 5. TIM'S LAYERED-CONTEXT IDEA — grounded design verdict
*(idea: local models make layered versions of session history attached to RANGES; the live
coordinator/RHM resolves WHICH version per address by CONFIG; original never mutated; widen-at-will.)*

**Every load-bearing primitive already exists:**
- IMMUTABLE ORIGINALS: proven copy-only materializer (session_pointintime.materialize_at_point:
  atomic-temp writes, re-stat before/after, structural post-verify) — "the original never changes" is law.
- RANGE GRAMMAR, live end-to-end: `compact:N` / `uuid:` / `ts:` (parse_point → session_post at= →
  supervisor _at_launch). Ranges are stable coordinates over append-only files TODAY.
- MULTI-SCALE INDEX: session_recall's dimension⊂section⊂turn (per-message, dedup-aware).
- THE RESOLVER PATTERN: runtime/resolver.py's CONTAINMENT LADDER (deepest containing rung, walk up,
  fail-loud) = literally "resolve which address by configuration", already trusted elsewhere; plus the
  cognition role→model resolution as the architectural cousin.
- FRESHNESS DISCIPLINE: index_freshness (never serve stale silently) proven for one derived layer.
- RANGE-KEYED COPY CORPUS: ledger.exchange (session_id, line_start, line_end) — raw, not condensed.

**The build = exactly 3 new pieces (not a rebuild):**
(a) LAYER STORAGE keyed by session range — local-model condensations at multiple resolutions (the 4B/
    kimi produce them; a jobs-handler like redescribe_changed's shape; freshness-stamped);
(b) a RESOLVER CALL-SITE: {session, range, config} → which stored layer (a resolver.py instance/sibling);
(c) a WIDEN VERB usable in-session (today "widen" = spawn a whole live copy via wake/consult at=).

**CC-CLI levers (doc-cited):** SessionStart+compact-matcher hook = THE supported re-injection lever
(additionalContext ≤10k chars); UserPromptSubmit per-turn; /compact instructions (hints, lossy);
DISABLE_AUTO_COMPACT; PreCompact can BLOCK not rewrite; transcript-edit-then-resume UNDOCUMENTED but
mechanically plausible (copy + --session-id; uuid-chain risk — and materialize_at_point is the estate's
own working proof of the copy route). FULL programmatic control (pinned keys, sliding window,
clear_tool_uses, memory tool) = the Claude API/Agent-SDK path — the always-on stream would need to be
SDK-driven for total control. NAMING: 'layers' + 'point' are claimed words in this estate — new
vocabulary needed for session-range layers.

## 6. THE UI SEAM (don't splinter)
Active integration TODAY: claude-ds is absorbing DNA's runtime (furniture-port; "once DNA lands" =
in-progress), and the WINDOW prototype (.build-container/phase-b-served/instrument.html, :8786) is
mid-reconciliation + GATED (L8: L1-L7 green + Tim's sight-verify; round-5 rejected; round-6 binds all
141 hand-rolled CSS instances to claude-ds rule engines). **The safe landing for SessionsPanel + board
comments = surface/app (:5174)**: already proxies claude-ds same-origin (/design→:8775), already carries
comment/favour/reaction mark types (a4fe3e83) and SessionDrill/BoardView actively landing; canvas/app is
a different track; instrument.html is moving+gated ground. Bridge gaps for the panel: no CORS anywhere →
add /api/supervisor/* proxy routes on the bridge (+ gated POST spawn/inject following /api/tools/invoke's
posture-gate pattern); board comments = POST route onto runtime/cc_board.comment (author operator://tim)
or the ALREADY-LIVE /api/territory/write mark path (both exist server-side; board-native comments are
what agents naturally read back via cc_board op=thread).

## 7. WHAT GOES IN TOGETHER (the composite slate, per Tim: "at the same time")
1. Supervisor stays on (done) · coordinator spawned with persona + conducted convergence channel + the
   first live conducted exchange (the unproven step, run gently).
2. SessionsPanel + board-comments in surface/app + bridge proxy/comment routes.
3. Context-layering v1: the 3 new pieces on existing primitives (range-keyed layer store via a jobs
   handler on local models · resolver call-site · widen verb) — coordinator/RHM read the same resolver.
4. Engine consolidation onto the jobs spine (RUN_KINDS += agent/routine kind → retire the unbuilt
   trigger-system design + unarmed routine timers); fix hookify's cwd bug (Tim's own rules, dead in every
   project session); reach the swarm from the forward-facing surface (wire chat_parts or successor).
All of it recorded to the convergence board; PII law respected (private content → local models).
