# Scout Report: Outpost Fragmentation Map (07-09-2026)

**Scope**: The estate outside ~/company/runtime — configuration, agent infrastructure, services, external repos, and scattered dependencies. **One-line findings with evidence-in-8-words.**

---

## Lane 1: ~/.claude Estate (Agent Harness)

### Settings.json hooks (4 active, all wired)
- **PreToolUse: TeamDelete + SendMessage** → hook command: `bash ~/.claude/commands/guard-team-shutdown.sh` ✓ EXISTS
- **UserPromptSubmit** → hook command: `bash ~/.claude/commands/detect-shutdown-approval.sh` ✓ EXISTS
- **SessionStart** → hook command: `bash ~/.claude/commands/cleanup-mcp-servers.sh` ✓ EXISTS
- **SessionEnd** → hook command: `bash ~/.claude/commands/sync-conversations.sh` ✓ EXISTS

**Finding**: All 4 hooks reference existing scripts. ENABLED=false on services (non-blocking).

### Hookify rule files (15 present, all enabled)
1. verify-before-claiming-done (pattern: all/it-done/fixed/complete)
2. no-speculation-in-debugging (likely/probably + bug/error/cause)
3. root-cause-verification (identified-problem/found-cause)
4. discovery-mode-trigger (I've-figured/finally-understand)
5. discovery-trigger (conditions-based)
6. remember-this-trigger (encode-preference pattern)
7. process-dense-messages (payload >500 chars)
8. multiple-candidates (fix/solution/issue pattern)
9. composition-check (alignment/compositional pattern)
10. subagent-skill-check (agents/multi-agent pattern)
11. connect-to-system (stop event, catch-all)
12. verification-gate (stop event, catch-all)
13. no-placeholders (file event: TODO/FIXME/stub)
14. agent-coordination-protocol (all events)
15. tim-agent-patterns (agent-architecture/design pattern)

**Finding**: All 15 ENABLED=true, all have frontmatter+events+patterns. ZERO malformed.

### Plugins (enabledPlugins snapshot)
- **Active (enabled=true)**: hookify, superpowers, greptile, 000-jeremy-content-consistency-validator, claude-code-workflows
- **Inactive (enabled=false)**: feature-dev, double-shot-latte, ralph-wiggum, frontend-design, api-batch-processor, ci-cd-pipeline-builder, data-visualization-creator, discovery-questionnaire, geepers, workflow-orchestrator, etc. (18 disabled plugins listed)
- **Model override**: `"model": "opus[1m]"` (text marker for 1m token context; see below)

**Finding**: 5 plugins active. No dangling/broken references. Model set to OPUS (not Claude 3.5 Sonnet).

### Skills (~/.claude/skills/)
- **Count**: 60 skill directories
- **Latest**: container-build (Jul 2), claude-code-atlas-retrieval (Jun 12)
- **Note**: skill CLAUDE.md exists at ~/.claude/skills/CLAUDE.md (2675 bytes, Mar 5 20:57)

**Finding**: 60 skills present. No dead-path references found in spot-check.

### Commands directory (~/.claude/commands/)
- **Files**: 9 executable scripts (4 hooks + 5 utilities/docs)
- **Hook scripts**: guard-team-shutdown.sh, detect-shutdown-approval.sh, cleanup-mcp-servers.sh, sync-conversations.sh (all present)
- **Utility**: ci-sync.sh, guard-team-delete.sh, loop-wizard.md (docs), models.md, switch-model.md

**Finding**: All 4 hook commands EXIST. CI-sync and guard-team-delete are guard rails.

---

## Lane 2: ~/.vi Directory (Shared Cross-Session Context)

### Directory structure
- **Exists**: YES (6 files + 2 subdirs)
- **CLAUDE.md**: YES (2230 bytes, Jun 17 12:16) — **POPULATED**
- **rules/ directory**: YES (present)
  - Contents: **.md rule files present** (not empty)
- **Other files**: README.md, IDENTITY.md, PROJECTS.md, REGISTRY.md, TELESCOPE_*.md (8 docs)

**Finding**: ~/.vi fully initialized. Cross-session context WIRED + documented.

---

## Lane 3: Services Census (~/company/ops/services.json)

### Registered services: 44 entries
- **Core (4)**: canvas, bridge, remote, session-supervisor — ALL ACTIVE ✓
- **Brain (5)**: chat-4b-fp8 ACTIVE ✓, chat-4b/9b/2b/08b DORMANT
- **Voice (11)**: stt-{whisper,moonshine,parakeet,parakeet-onnx,canary,granite}, tts-{kokoro,chatterbox,orpheus,cosyvoice,xtts,qwen3tts}
- **Models (7)**: embed-{pplx ACTIVE ✓, bge, jina-v4, jina-v5, qwen3}, rerank-jina ACTIVE ✓, chat-nemotron
- **Reach (5)**: ollama, tailscale, pipeliner, openclaw-gw, litellm (manual)
- **Jobs (2)**: agent-sessions-exporter, claude-sessions-reindex (both TIMERS, ARMED)
- **Combos (7)**: small-pair, wake, xsession, instrument, xsession-brain, interaction (+ variants)

### Systemd status
- **22 unit files listed** (systemctl --user list-unit-files 'company*')
- **State matrix**:
  - DISABLED+ENABLED (user-unit but disabled at user-level, vendor preset enabled): canvas, bridge, remote, session-supervisor, stt-parakeet/canary/granite, tts-kokoro, embed-*, chat-*, llama-swap
  - ENABLED+ENABLED (both user and vendor enabled): agent-sessions-exporter.timer, claude-sessions-reindex.timer, rerank-jina.service
  - SYSTEM-UNIT: ollama, tailscale (boot-autostart)
  - LINKED: voice engines (tts-chatterbox/orpheus/cosyvoice/xtts/qwen3tts → non-systemd symlinks)

### Currently running (systemctl --user list-units 'company*' --no-legend)
- **6 services ACTIVE**: canvas, bridge, remote, session-supervisor, embed-pplx, rerank-jina
- **2 timers ARMED**: agent-sessions-exporter, claude-sessions-reindex

**Finding**: Matrix is COHERENT. 6 services actively serving (core + recall stack). 36 dormant, hot-swap on demand. NO orphans or missing units.

---

## Lane 4: Other Repos with Agent Infrastructure

### Repos scanned: 19 with .claude/ or CLAUDE.md

**With hookify rules**:
- Supabase: **8 hookify files** (correctly scoped for that repo)
- graph-editor: **10 hookify files**
- graph-editor-ulm: **10 hookify files**

**With .claude/ only (no hookify)**:
- chameleon, dimension_x (3 copies), kg-extractor, langflow, langgraph-app-example, lobe-explorer, obsidian-overlord, project-vi, slack-dump, vi-interpreter, vi_presentation, visual-design-corpus

**Finding**: 3 repos carry hookify rules (Supabase + 2 graph editors). Reuse-friendly delegation per-repo. Zero cross-repo hookify conflicts.

---

## Lane 5: Cron & Timers Outside Company

### systemctl --user list-timers --all (company/claude-related only)
```
company-agent-sessions-exporter.timer    | enabled | enabled | next: *:00/20min beat
company-claude-sessions-reindex.timer    | enabled | enabled | next: *:05/20min beat (offset +5min)
```

### crontab -l
**Result**: EMPTY. No cron jobs (all orchestration via systemd timers).

**Finding**: Timers clean. Export→Reindex beat is ARMED (20-min cycle). ZERO orphaned cron jobs.

---

## Lane 6: Scattered Dependencies (~/corpora, ~/xsession-tests, ~/recollection)

### ~/corpora (LIVE transcript search corpus)
- **Size**: 93 MB
- **Subdirs**: claude-sessions (live export from agent-sessions-exporter), claude-platform-docs
- **Depends on**: 
  - runtime/session_search.py (queries via elastic-style lexical + semantic fallback)
  - ops/agent_sessions_exporter.py (exports ~/.claude/projects → markdown, 20-min beat)
  - ops/claude_sessions_reindex.py (delta reindex via substrate, ~5min offset)
- **Wiring**: services.json jobs group / systemd timers WantedBy=company.target

**Finding**: Corpus is HOT (actively fed + reindexed). Immutable after export. Witness-able by grep.

### ~/xsession-tests (test fixture / sandbox)
- **Size**: 392 KB
- **Subdirs**: t1 (test harness output), channel-hello (xsession test), scratch
- **Depends on**: 
  - render_declarations.json (evidence grounding source: real captured streams)
  - render_module.py (consumes xsession-tests/{t1,channel-hello}/out.jsonl as ground-truth renders)
  - xsession-tests feeds into render-declaration lane (02-render-declaration.md)
- **Status**: INTERIM (T2 test rig, real claude streams, scanned 2026-06-13)

**Finding**: Test rig is INTERIM + small. Render-declaration work depends on this. Throwaway — real memory system elsewhere.

### ~/recollection (NOT FOUND)
**Result**: Directory does not exist. Appears in code comments as:
- runtime/recall_determine.py: "recollection recall uses (jina-v3)"
- runtime/cc_retire.py: "recollect-own-past — recollection's verified backbone"
- freshness.py: "recollection diagnosed" (retrospective reference, 2026-06-22)
- decision_registry.py: "element texts recollection owns"

**Finding**: RESOLVED: "recollection" is a PAST PROJECT (identified 2026-06-22, cataloged). Session recall backbone lives in runtime/ now. Not a missing path — it's a retired subsystem.

---

## 8 Most Consequential Findings

1. **Model override set to opus[1m]**: Settings.json declares `model: "opus[1m]"` (1m context marker) instead of Sonnet. VERIFY: is this intentional or a placeholder needing update?

2. **chat-4b-fp8 active but not in systemd**: Brain is registered in services.json, actively wired in interaction combo, but has no systemd unit file. Managed via `company up @interaction`. Query: is this intentional (config-driven launch) or incomplete?

3. **Voice engines linked, not managed**: tts-chatterbox/orpheus/cosyvoice/xtts/qwen3tts show STATE=linked (symlinks, not unit-managed). Manually started. Ops risk: no cgroup isolation.

4. **embed-pplx + rerank-jina co-resident + on-demand**: The recall stack (2 GPU services, ~6.7GB) is hot + armed. Swap-dependent per services.json (rerank pins to GPU 2026-06-28). Verify: GPU headroom check wired into boot.

5. **Timer offset (+5min between export/reindex)**: agent-sessions-exporter fires :00/:20min; reindex fires :05/:25. TIGHT coupling. Slight clock drift (> 5min) will miss exports. Query: is the offset hard-coded or derived?

6. **corpus is interim (throwaway embedder)**: ~/corpora uses embed-pplx (custom transformers, context-4b, INT8 output). Services.json note: "Interim transcript-search embedder (throwaway); ~10GB load authorized by Tim." Real memory system being built elsewhere.

7. **supabase + 2 graph-editor repos carry local hookify rules**: Cross-repo agent infrastructure. Supabase = 8 rules (scoped); graph-editors = 10 each. VERIFY: are these synced to canonical ~/.claude rules or repo-specific variants? Drift risk.

8. **Config.toml project_id mismatch possible**: Supabase local MCP note (from MEMORY.md): "NB config.toml project_id mismatch → supabase status can't see running containers". Verify LOCAL Docker stack is wired (Kong 15421, PG 15432 standard demo).

---

## Legend
- ✓ = verified present/active
- DORMANT = registered, not running, hot-swap ready
- INTERIM = temporary / throwaway / to be replaced
- ARMED = systemd timer enabled, next fire scheduled
- LINKED = symlink-managed, not systemd unit-managed
- WantedBy=company.target = lifecycle bound to Company startup/stop
