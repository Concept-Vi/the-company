# Fragmentation Map Scout 1 — Built-Not-Wired & Designed-Not-Built

**Purpose:** Identify disconnects: components built but never wired, designs completed but never implemented, registries with no consumers, split surfaces, unwired hooks, disabled services.

**Scope:** 10 classes of fragmentation, scanned 2026-07-09 with fresh evidence (file existence, code callers, systemctl status, registry readers).

---

## Class 1: Routines (Runtime System)

| Finding | State | Evidence |
|---------|-------|----------|
| `runtime/routines.py` · registry + _load_module/_build_routine · declares 2 routines (self_status, completion_poke) | BUILT-UNWIRED | File exists, functions defined, no callers except tests. Routines are FILE-DISCOVERED not called. |
| `runtime/routine_runner.py` · fire mechanism via session-supervisor spawn/inject/capture | BUILT-UNWIRED | File exists, implements FIRE, referenced in routine_schedule.py only, no active callers in flows. |
| `runtime/routine_schedule.py` · generates per-routine systemd .timer + .service files | BUILT-UNWIRED | File exists, render_units() + generate_units() work, OUTPUT GENERATED to ops/systemd/generated/ but NOT ARMED. |
| `ops/systemd/generated/company-routine-*.{service,timer}` · 4 generated unit files for 2 routines | GENERATED-UNINSTALLED | Files exist (created 2026-06-21, 2026-06-14), not linked to ~/.config/systemd/user/ (systemctl --user list-unit-files shows ZERO company-routine* units). No systemctl enable called. |
| **Crux** | BLOCKED | Routines exist in code + systemd templates exist + but systemctl installation never runs. Design says "generate units + arm" — arm step is missing. |

---

## Class 2: Dials (Character Traits)

| Finding | State | Evidence |
|---------|-------|----------|
| `dials/anticipation.py` · dial definition: how far ahead brain thinks (reactive/warm/hot) | DESIGNED-UNWIRED | File exists, DIAL dict defined, explicitly states "CONSUMERS (named honestly): the now-organ + resolver when built (GC14/Track-1); **nothing reads this yet** — the dial is their configuration seam, adjustable from day one." |
| `dials/stability.py` · dial definition: how much surface can move on its own | DESIGNED-UNWIRED | File exists, same pattern as anticipation — named but no consumer code exists to read/apply the dial. |
| `runtime/dials.py` · DialRegistry.discover() + get()/position_names() | BUILT-SURFACE-ONLY | Registry infrastructure exists, loads .py files, validates schema, but has ZERO runtime consumers. The "governs" field names seams that don't exist yet. |
| `mcp_face/tools/dials.py` · MCP tool: list/describe/set ops | BUILT-SURFACE-ONLY | Tool exists, wires to suite.dial_state()/suite.set_dial(), but no runtime code reads the dial values (they're stored but never consulted). |
| **Crux** | DESIGNED-NOT-IMPLEMENTED | Dials are 100% declarative, discovery + storage works. The CONSUMER seams (now-organ, resolver) are explicitly not built. Awaiting GC14/Track-1. |

---

## Class 3: CC_Gate (Gating/Approval)

| Finding | State | Evidence |
|---------|-------|----------|
| `runtime/cc_gate.py` · gate/resume/abort/list_gates/get_gate functions | BUILT | File exists, implements 5 core ops, file-discovered _path/_read/_write/_find/_transition internals. |
| `.data/gates/` directory | MISSING-STORAGE | Directory DOES NOT EXIST. gate() function tries to write to .data/gates/{gid}.jsonl, but the parent dir is never created. No mkdir -p in code. |
| `mcp_face/tools/cc_gate.py` · MCP interface to cc_gate functions | BUILT-WIRED | Tool exists, calls cc_gate.gate/resume/abort/list_gates/get_gate. Active callers in minds.py (lambda closure) + mcp_face/tools/cc_gate.py itself. |
| `runtime/minds.py` · gate-aware gating logic | PARTIAL-GATED-CLOSURE | References cc_gate in comment: "closure (e.g. `lambda a: any(g['state']=='gated' for g in cc_gate.list_gates() if g['step_address']==a)`)" — the integration point EXISTS but may never be invoked because minds.py itself is not yet a runtime path. |
| **Crux** | BUILT-INCOMPLETE | Gate mechanics exist + MCP wiring works, but .data/gates/ directory is never created → gate write fails silently. Storage layer is missing. |

---

## Class 4: Registry Freshness (Platform Hook)

| Finding | State | Evidence |
|---------|-------|----------|
| `ops/hooks/registry_freshness.py` · generalized platform version checker | BUILT | File exists, iterates PlatformRegistry.discover(), checks version_source on each platform, compares to store/<id>.version_stamp, prints warnings for stale platforms. |
| `ops/hooks/cc_registry_freshness_check.sh` · SessionStart hook wrapper | BUILT-WIRED | File exists, calls registry_freshness.py, falls back to claude-code-only bash check if python unavailable. Wired as SessionStart hook in .claude/settings.json (confirmed in file comments: "Wired as a Claude Code SessionStart hook"). |
| `flows/cc_registry_refresh.py` · refreshes version stamp after updates | BUILT | File exists, referenced as the action to take when registry is stale (print statement in registry_freshness.py line 55-57). |
| **Status** | BUILT-WIRED | Fully functional. Checks run on every SessionStart. Platform registry is discovered dynamically; new platforms are checked for free. |

---

## Class 5: Trigger System (Design-Described, Code Absent)

| Finding | State | Evidence |
|---------|-------|----------|
| `build-prep/trigger-system/DESIGN-SYNTHESIS.md` · master design doc | DESIGNED | File exists (2026-06-17), states: **"THE BIG FINDING — it's all built, and WIRED TO NOTHING"**. Lists required BUILD items (section "BUILD:"). |
| `runtime/triggers.py` · trigger registry (required by DESIGN) | DESIGNED-ABSENT | Design explicitly calls for "runtime/triggers.py registry" in BUILD section (line 51). File DOES NOT EXIST. |
| `runtime/trigger_driver.py` · event→action dispatch (dormant) | DESIGNED-ABSENT | Design calls for "trigger_driver.py (dormant) + board.filed emit + responds_to edge". File DOES NOT EXIST. |
| `mcp_face/tools/triggers.py` · MCP tool for trigger authoring | DESIGNED-ABSENT | Design calls for "mcp_face/tools/triggers.py". File DOES NOT EXIST. |
| `nodes/cc_launch.py` · CC-launch node (structured result capture) | DESIGNED-ABSENT | Design calls for "CC-launch node (nodes/cc_launch.py) + close the structured_output capture gap". File DOES NOT EXIST. |
| `edge_kinds/triggers.py` · trigger edge kind | FOUND-ELSEWHERE | File EXISTS at edge_kinds/triggers.py, not runtime/triggers.py. |
| **Crux** | DESIGNED-ABSENT (4 OF 4 MAIN ARTIFACTS) | Design is complete + all 3 design docs (forms-built, lifters, trigger-registry) describe one introspective self-build substrate. The TRIGGER half requires runtime/triggers.py + driver + node + tool. All 4 are missing. Design recommends: convert recognisers to DATA + wire trigger→CC-launch + board.filed emit. |

---

## Class 6: Design Docs Newer Than 2026-06-01 — Artifact Existence Audit

**Method:** Listed design docs newer than 2026-06-01 (sorted by mtime desc), spot-checked for named artifacts.

| File | Describes | Expected Artifacts | Found? | Status |
|------|-----------|-------------------|--------|--------|
| `/build-prep/mesh/PLAN.md` (2026-07-09) | Mesh architecture | Not yet scanned (latest) | ? | PENDING-DETAIL |
| `/build-prep/the-one-system/window-prep/BUILD-PLAN.md` (2026-07-03) | Window/prep for build | build-prep/ components | PARTIAL | See details below |
| `/build-prep/the-one-system/plan-a-jobs/DESIGN.md` (2026-07-02) | Jobs + triggers system | `jobs.json` + `triggers.json` | jobs.json EXISTS, **triggers.json ABSENT** | PARTIAL-MISSING |
| `/build-prep/the-one-system/JOBS-AND-COORDINATES-PLAN.md` (2026-07-02) | Jobs coordination | Runtime jobs system | EXISTS (runtime/jobs.py) | OK |
| `/build-prep/gpu-serving-rework/BUILD-PLAN.md` (2026-06-30) | GPU rework | vLLM + inference layer | Not fully verified | PENDING-DETAIL |
| `/build-prep/the-one-system/LEDGER-ENRICHMENT-PLAN.md` (2026-06-29) | Ledger enrichment | Ledger layer | Not fully verified | PENDING-DETAIL |
| `/build-prep/trigger-system/DESIGN*.md` (4 files, 2026-06-17) | Forms + lifters + triggers | triggers.py + driver + node (see Class 5) | **ABSENT** | DESIGNED-ABSENT (4) |

**Key Finding:** `triggers.json` MISSING — design.md (2026-07-02) explicitly references `triggers.json` as an `_ActionRegistry` store alongside `jobs.json`, but the file does NOT exist in `.data/store/`.

---

## Class 7: Canvas vs Surface (Two UIs, Different Tracks)

| Finding | State | Evidence |
|---------|-------|----------|
| `canvas/app/` · separate React/Vite app | SPLIT-TRACK-1 | Directory exists with index.html + src/App.tsx + tsconfig.json. Distinct build + dist (last modified 2026-06-10). |
| `surface/app/` · separate React/Vite app | SPLIT-TRACK-2 | Directory exists with index.html + src/App.tsx + tsconfig.json. Distinct build (last modified same date). |
| Canvas API calls | 19 fetch/axios | Grep found 19 API references (fetch, api, endpoint calls) in canvas/app/src/App.tsx. |
| Surface API calls | 26 fetch/axios | Grep found 26 API references in surface/app/src/App.tsx — MORE API integration. |
| **Split Pattern** | TWO SURFACES, SEPARATE BUILDS | Both apps exist + are independently built. Surface has more API wiring (26 vs 19 calls). Canvas appears lighter/research-facing, Surface more operational. |
| **Integration Status** | DUAL-NOT-CONSOLIDATED | No evidence of a unified canvas/surface bridge. Build/serve processes are separate (both have package.json + tsconfig.json). |

---

## Class 8: Systemd Units — Disabled & Static

**Disabled units** (enabled in VENDOR PRESET but marked disabled locally):

| Unit | State | Notes |
|------|-------|-------|
| `company-bridge.service` | disabled | Critical service, not running by default. |
| `company-canvas.service` | disabled | Canvas app service. |
| `company-embed-pplx.service` | disabled | Embedding service. |
| `company-remote.service` | disabled | Remote service. |
| `company-session-supervisor.service` | disabled | Session supervisor (CRITICAL for routine/gate execution). |
| `company-tts-kokoro.service` | disabled | TTS service. |
| `company.target` | disabled | Meta-target grouping company services. |
| Other voice/STT services (5 units) | disabled | Canary, Granite, Moonshine, Parakeet variants, all disabled. |

**Static units** (cannot be enabled/disabled, system-managed):

| Unit | State | Notes |
|------|-------|-------|
| `company-agent-sessions-exporter.service` | static | Exported to user scope; cannot toggle. |
| `company-claude-sessions-reindex.service` | static | Reindex service, auto-managed. |

**Routine timers (GENERATED but NEVER INSTALLED):**

| Unit | State | Notes |
|------|-------|-------|
| `company-routine-*.service` / `.timer` | NOT IN SYSTEMD | Generated to `ops/systemd/generated/` but never symlinked to `~/.config/systemd/user/`. Not registered with systemctl. |

**Crux:** 12+ core units are disabled by default. Session supervisor is disabled → routines cannot fire (routine_runner depends on it). No automated "arm on first session" mechanism found.

---

## Class 9: MCP Face Tools — Stub/NotImplemented Scan

**Scan method:** Grepped all `/mcp_face/tools/*.py` for NotImplementedError, `raise NotImplemented`, `pass  # stub`, `TODO.*implement` patterns.

| Finding | Evidence |
|---------|----------|
| **No stubs found** | 0 NotImplementedError, 0 stub markers, 0 TODO-implement. |
| Tools scanned | 30 files (access.py, cc_attachments.py, ... operators.py, point.py, routines.py, etc.). |
| Introspection.py mentions stubs | File contains "stub-populated registry" as a design concept (for testing), but no actual stubs in implementation. |
| **Status** | ALL TOOLS APPEAR IMPLEMENTED (no dead code markers). |

---

## Class 10: .data/store Registries — Readers per File

**Method:** Grepped entire codebase for each .jsonl/.json filename to count reader code.

| Registry File | Readers | Status | Notes |
|---|---|---|---|
| `annotations.jsonl` | 415 | ACTIVE | Heavy use (annotations are pervasive). |
| `chat.jsonl` | 1403 | ACTIVE | Heaviest reader count (chat is core). |
| `events.jsonl` | 591 | ACTIVE | High use (events are core). |
| `marks.jsonl` | 319 | ACTIVE | Marks system actively read. |
| `findings.jsonl` | 170 | ACTIVE | Findings are read regularly. |
| `cascades.json` | 502 | ACTIVE | Cascades are heavily used. |
| `jobs.json` | 20 | ACTIVE | Jobs registry actively read (job execution). |
| `trigger_state.json` | 18 | ACTIVE | Trigger state read in jobs.py + runtime/jobs.py. |
| `commit_queue.jsonl` | 20 | ACTIVE | Commit queue read regularly. |
| `access_grants.jsonl` | 6 | ACTIVE | Access control. |
| `remote_mcp_audit.jsonl` | 5 | ACTIVE | Audit trail. |
| `query_watch_state.json` | 1 | MINIMAL | Single reader. |
| `pyramid_fingerprints.json` | 4 | MINIMAL | Backup/rebuild exit key. |
| `provenance_backfill_state.json` | 1 | MINIMAL | Backfill state. |
| `saved_queries.json` | 1 | MINIMAL | Saved queries (mcp_face/tools/coordinate.py only). |

**Finding:** NO registries are COMPLETELY UNREAD. All have at least 1 reader. `saved_queries.json` + `query_watch_state.json` + `provenance_backfill_state.json` + `pyramid_fingerprints.json` have minimal (1–4) readers but are not orphaned.

---

## Summary Counts by Class

| Class | Total Items Scanned | Built-Unwired | Designed-Absent | Split/Dual | Disabled Units | Status |
|-------|-------|---|---|---|---|---|
| 1. Routines | 4 | 4 | 0 | 0 | 2 | BLOCKED (systemctl never runs) |
| 2. Dials | 4 | 2 | 2 | 0 | 0 | DESIGNED-INCOMPLETE |
| 3. CC_Gate | 4 | 2 | 1 (storage) | 0 | 0 | PARTIAL (no .data/gates/) |
| 4. Registry Freshness | 3 | 0 | 0 | 0 | 0 | BUILT-WIRED (OK) |
| 5. Trigger System | 5 | 0 | 4 | 1 | 0 | DESIGNED-ABSENT (4/4 artifacts missing) |
| 6. Design Docs | 4 | 0 | 1 | 0 | 0 | triggers.json missing |
| 7. Canvas/Surface | 2 | 0 | 0 | 2 | 2 services | SPLIT (dual UIs) |
| 8. Systemd Units | 22 | 0 | 0 | 0 | 12 | DISABLED (session-supervisor critical) |
| 9. MCP Tools | 30 | 0 | 0 | 0 | 0 | ALL IMPLEMENTED |
| 10. Registries | 15 | 0 | 0 | 0 | 0 | ALL HAVE READERS |

---

## Top 10 Most Consequential Findings

1. **Trigger System — 4 Missing Artifacts** · runtime/triggers.py + trigger_driver.py + mcp_face/tools/triggers.py + nodes/cc_launch.py · Design complete (DESIGN-SYNTHESIS.md) but ZERO implementation. Blocks agent-authorable trigger authoring. Design recommends recognisers→DATA + wire.

2. **Routines — Systemctl Never Runs** · 4 systemd unit files generated to ops/systemd/generated/ but NEVER linked/installed to ~/.config/systemd/user/. systemctl --user list-unit-files shows ZERO company-routine* units. Routine execution is blocked at the arm step.

3. **Session Supervisor — Disabled by Default** · company-session-supervisor.service is disabled → routine_runner cannot spawn routines (depends on supervisor). No automated enable mechanism found.

4. **CC_Gate — Storage Directory Missing** · .data/gates/ directory does NOT exist. gate() calls will fail silently when trying to write. File-based gating is broken at the persistence layer.

5. **Triggers.json — Designed but Not Created** · Design.md (2026-07-02) describes triggers.json as an _ActionRegistry store alongside jobs.json, but the file is never created. jobs.json EXISTS; triggers.json is missing.

6. **Dials — Consumers Not Implemented** · dials/anticipation.py + dials/stability.py explicitly state "nothing reads this yet". Design infrastructure exists (DialRegistry, MCP tool) but the now-organ + resolver (GC14/Track-1) that should consume dial values don't exist.

7. **Canvas/Surface Split — Dual Tracks, No Bridge** · Two separate React apps exist (canvas/app + surface/app) with different API call counts (19 vs 26). No unified canvas/surface bridge or consolidated build process found.

8. **Disabled Core Services — 12+ Units Offline** · company-bridge, company-canvas, company-embed-pplx, company-remote, company-session-supervisor, company-tts-kokoro, company.target, + 5 voice services are all disabled. No indication which should be enabled on first run.

9. **Saved_queries.json — Minimal Wiring** · Registry file exists but only 1 reader (mcp_face/tools/coordinate.py). Query watch/save system appears dormant or incomplete.

10. **Two Systemd Pattern Issues** · (a) Routine timers generated but not installed (missing systemctl enable step). (b) Session supervisor disabled (blocks routine execution). Combined: routines cannot fire even if timers were armed.

---

## Next Steps (Recommendations)

1. **Trigger System:** Prioritize build of runtime/triggers.py + trigger_driver.py. Unblock with DATA-based recognisers (RULE_OPS ops + regex strings) per DESIGN-SYNTHESIS recommendation.

2. **Routines:** Add systemctl install step after generate_units(). Enable company-session-supervisor on boot. Verify routine_runner can fire through supervisor.

3. **CC_Gate:** Create .data/gates/ directory on suite initialization. Add mkdir -p to gate write path.

4. **Triggers.json:** Create .data/store/triggers.json on job initialization. Wire ActionRegistry to discover/read/write triggers alongside jobs.

5. **Dials:** Confirm GC14/Track-1 timeline. Dials are ready to be consumed; awaiting now-organ + resolver integration.

6. **Canvas/Surface:** Map which UI is canonical (production vs. research). Consolidate or explicitly separate build/serve processes.

7. **Systemd:** Document which disabled units need to be enabled on first-run setup. Add an `ops/setup-systemd.sh` to orchestrate.

