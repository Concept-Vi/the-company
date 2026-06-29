---
type: proposal
title: OpenWebUI ↔ Company — Master Fusion Proposal
register: prescriptive
status: draft-for-approval
posture: nothing-trusted · both-sides-incomplete · best-parts-into-the-centre · no-duplicates-inward-or-outward · no-horizon
date: 2026-06-28
grounds:
  - area-A..I (company maps) · owui-side-map.md · fusion-{channels,brain-tools,voice,conversations-sessions,knowledge-memory,identity-users,faces}.md
---

# OpenWebUI ↔ Company — Master Fusion Proposal

**What this is.** One integrated proposal for fusing OpenWebUI and the Company, synthesized from a full
by-area map of the company + a deep map of OpenWebUI + seven capability-level fusion drafts, every one
**verified live** (not trusted from the code's self-description). It is organized to be (a) approved by Tim
and (b) built from. It is a living spine, not a finished spec — both sides keep developing.

## 0. The one principle

There is **no source of truth** and nothing is complete on either side. So for every capability: take the
**best parts of each**, fuse them, and **build the fused thing INTO the company** (the centre that accrues).
OpenWebUI is both a **donor of parts** (its product-grade chrome, channels, RAG, auth, branching) and a
**face** onto the company substrate. **No duplicates** — and that law turns **inward**: the company's own
self-duplications get healed in the same pass. No fixed end-state is assumed (no horizon).

## 1. Fix-first foundations (live-broken; they block fusion NOW)

Verified broken this pass — these are not design choices, they are current breakage that any fusion sits on:

- **F1 — The voice mouth is DEAD.** kokoro (:4123) reports health-ok and "ready" but `POST /tts` never
  completes (onnxruntime GPU device-discovery hang on WSL2). It's the only always-on CPU mouth; GPU
  engines are down. **No voice turn can complete end-to-end right now.** Fix: pin kokoro to
  CPUExecutionProvider + put under systemd warm-on-boot. (fusion-voice §S-V1)
- **F2 — The STT shim is broken + mispinned.** `ops/stt_openai_shim.py` references an undefined `PROVIDER`
  (NameError, :58/:69); the running process is pinned to a DOWN `granite` ear. Neither reads the live
  loadout. Fix in the rewrite (see Voice). (fusion-voice §S-V2/V3)
- **F3 — The bridge wedges under load.** `:8770` hung mid-session (every route) while in-process chat
  answered in ~3s; a restart cleared it → **load-induced, not a logic bug**. Fix: per-request deadline +
  bounded worker pool (it's an unbounded-thread stdlib server). (fusion-brain-tools)
- **F4 — vLLM has no autostart + ~7-min cold start.** The RHM refuses to *act* whenever `:8000` is down.
  Fix: enable the unit on boot; accept/curtain the warmup. (keystone-prove session earlier)
- **F5 — The `-pro` anti-pattern is still live.** `DEFAULT_BRAIN = deepseek-v4-pro:cloud`
  (`fabric/config.py:21`) is the fallback at 6 call-sites — violates cognition-is-role-resolved. Fix: make
  the fallback role-resolved, not a pinned `-pro`. (fusion-brain-tools)

These are small, mostly mechanical, and reversible. Nothing voice- or act-related is real until F1–F4 hold.

## 2. The capability fusions

Each: **best parts (company / OWUI) → the fused thing → built into the company.** Condensed; detail in the
per-capability files.

### 2.1 Channels — *an OWUI channel IS a company channel*
- **Best — company:** a real transport/structure split already exists (`cc_channels` live transport +
  `session_channels` durable structure), richer routing (direct/conducted modes, gatherings), reactions-as-
  control proven. **Best — OWUI:** `@model` as a first-class streaming participant, threads, reactions, pins,
  members/roles/unread, Socket.IO realtime.
- **Fused:** one channel — `session_channels` row = durable truth, `cc_channels` = its live transport, the
  OWUI channel = a rendered face (not a second store). OWUI's `@model` generalizes to a **third member-kind**
  reached via the company brain/grounded pipeline (surfacing failures, *not* OWUI's swallowed errors). OWUI's
  threads/reactions/members/realtime get **built into `session_channels`** as first-class. The 🛑/⏸ reaction
  controls promote from my daemon into the channel primitive.
- **Heal (internal):** there are **two named-channel stores** (`cc_channels/_channels/*.json` vs
  `session_channels/channels.jsonl`) and **doubled MCP tools** (`cc_channel` mgmt vs `channel_act`). Fold the
  cc_channels named-store into session_channels (keep its live-messaging ops); make `cc_channel` =
  live-messaging only, `channels`/`channel_act` = all structure; **fold `ops/owui_room.py` into
  session_channels** as the OWUI-face adapter (it reinvented the roster).
- **Seam-as-work:** `channel_boundary` Realtime is *built but unwired* (no session_channels→boundary hook;
  not in services.json/systemd) — corrected from the map's "stubbed."

### 2.2 Brain + Tools — *the operator IS the RHM; tools via native MCP*
- **Best — company:** the RHM (brain_router + Suite.chat), loadout-selected model, governed verbs, the
  ~68-tool MCP fabric. **Best — OWUI:** manifold Pipe model-lists, native tool-calling, and a Tools surface
  that **natively speaks MCP**.
- **Fused:** expose the RHM as an **OWUI manifold Pipe** (one `operator` model + a registry-driven role/model
  manifold reading `rhm_config`/`services.json`) — retiring the standalone OpenAI-shim process. Expose the
  company tools to OWUI via its **native `type:'mcp'`** Tools, pointed at the company MCP gateway — so OWUI
  models can call the fabric without a parallel adapter.
- **Heal (internal):** three overlapping seams exist today (the `:4300` shim, `owui_room`'s operator-as-CC-
  session, the `:8772` MCP gateway) — collapse to the two clean ones above. Kill the `-pro` fallback (F5).
- **Seam-as-work:** `mcp_face/server.py` is **stdio-only**; whether OWUI's MCP client can reach the `:8772`
  HTTP gateway is **unverified** — must be confirmed before relying on native-MCP tools. Tool count is
  unreconciled (28 modules / ~66–80 ops) — flagged, not tidied.

### 2.3 Voice + Ears — *OWUI native voice, riding the company loadout*
- **Correction:** OWUI's voice-call UI is **compiled frontend** that can only call two stateless endpoints
  (`/v1/audio/speech`, `/v1/audio/transcriptions`). It **cannot** call the company's fused `/api/voice/turn`
  without forking — so the **shim approach is correct**, not a mistake. (Reverses my earlier worry.)
- **Best — company:** loadout-driven engine/ear/voice/persona selection, engine variety, the `speakable`
  layer, the one-circuit `/api/voice/turn` (for the company's own surfaces). **Best — OWUI:** streaming
  sentence-split TTS with caching + the in-chat voice-call UX.
- **Fused:** thin **both shims to adapters over the bridge's loadout-aware `/api/tts` + `/api/voice/stt`**, so
  switching ear/voice/persona in the company (one `set_rhm_config`) makes OWUI follow **by construction**
  (`rhm_config()` is the single source). Don't re-implement engine routing in the shim.
- **Heal/seam-as-work:** F1 (dead mouth), F2 (broken shim); ear co-residence/VRAM; cosyvoice build broken;
  ref-clip **exists** (map was wrong). whisper.cpp :2022 down.

### 2.4 Conversations + Sessions — *build the conversation store the company lacks*
- **Correction:** the company has **no conversation-content store at all** — sessions are metadata+pointer,
  events carry only summaries, recall reads the *foreign* Claude-Code `.jsonl` transcripts. So this isn't
  "two memories that disagree" — it's "one side has none."
- **Best — company:** the addressed store + fold pattern, single-writer discipline, recall. **Best — OWUI:**
  a branching message DAG (parent/children/current), regen/edit, chat-history UX.
- **Fused:** build a **new FsStore conversation leaf** (`.data/store/conversations/<cid>.jsonl`, append-only
  + read-time fold) that **donates OWUI's branching DAG shape**; the supervisor appends message events for
  agent conversations (single-writer preserved); OWUI's chat UI becomes a **view**; recall re-points at this
  one store. OWUI contributes *shape + UX*, not a database.
- **Heal (internal):** recollection split-brain is **two physical DBs** (12.5 GB/86k rows old-schema-with-
  embeddings vs 218 MB/8k rows new-schema-empty-vec) — migrate-then-retire (the new one is unembedded; naive
  deletion loses the only populated index). The existing `owui_fabric_bridge` syncs **channels only, never
  chats** — chats must NOT be bolted onto it.

### 2.5 Knowledge + Memory — *the corpus is the store; harvest OWUI's RAG plumbing*
- **Best — company:** projection lenses / embedding spaces, the corpus, the inversion-finder, a `lexical`
  mode (not cosine-only). **Best — OWUI:** a mature RAG factory (14 vector backends, **hybrid BM25 fusion +
  rerank**, agentic retrieval, a document-loader matrix, documents UI).
- **Fused (union, 3 legs):** (a) the company corpus is THE knowledge store; OWUI collections become
  projection/space *filters*, not a second table. (b) OWUI's genuine deltas — the **BM25 fusion stage**, the
  **document-loader matrix** (PDF/docx/OCR), agentic retrieval — get **built into the company**. (c) the
  corpus is exposed as MCP tools (already live) that OWUI's Tools call — OWUI as a *face*, dereferencing live.
- **Heal (internal):** several memory-flagged bugs are **stale/wrong** — `:8004` is a deliberate hot-swap
  pair (not a collision), the floor is already `-0.13`, freshness auto-reindex is **built but has zero
  callers** (scheduling is the residual). The episodic split is actually **3-way** (corpus / recollection
  sqlite-vec / interim Chroma) — name it, converge to one.

### 2.6 Identity + Users — *one principal registry, two kinds, OWUI AccessGrant as the authority*
- **Correction:** the company's agent-identity is **thinner** than assumed (channel reg = thin liveness; the
  agent's `role`/`model` live in a self-authored, ungated `profile` blob; company "roles" are *cognition*
  roles — a naming collision, not principals). There is **no** user/permission tooling — only a binary
  operator-token + MCP posture tiers. **Humans already cohabit the agent registry** (`tim.json`,
  `operator.json` sit beside the `ch-*` agents).
- **Best — company:** agent identities + personas. **Best — OWUI:** human users, groups, the **AccessGrant**
  model (chained-base enforcement), enterprise auth (SCIM/OAuth/LDAP).
- **Fused:** ONE principal registry, **two typed kinds** — **AGENT** (the AI members) and **VIEWER** (the
  humans, via OWUI auth) — bridged by the already-live channel registry, **gated by OWUI's AccessGrant as the
  single authority**; the company's binary gates become enforcement points that read grant rows (posture =
  fail-closed floor). This *finishes an identity kind that half-exists* rather than bolting on a system.
- **Open (for Tim):** persona is durable, session ephemeral — OWUI's preset→base direction may be inverted;
  flagged, not assumed.

### 2.7 Faces + Surfaces — *open options, no destination*
- **Verified:** canvas (`:5173`, tldraw renderer) and surface (`:5174`, DNA renderer) are **not in use**
  (nothing listens); they use **two distinct renderers** — a real convergence candidate, not "two faces of
  one spine." There are **three design lineages** (`design/` corpus, `claude-ds`, the DNA repo) — `claude-ds`
  ↔ DNA is the real duplication risk.
- **Constraint (plain):** OWUI's frontend is a **built bundle** — customizable without a fork only via
  `static/custom.css` + `static/loader.js` + `WEBUI_NAME`/banners/logo. Deeper layout needs a **fork**; the
  license caps **rebranding at scale** (>50 users/30 days), not forking itself.
- **Fused — five open options, no pick (no horizon):** (A) skin OWUI with company DNA tokens via custom.css
  [no fork]; (B) DOM-mount a company surface via loader.js [no fork]; (C) embed company UI via Action/Pipe/
  MCP inside OWUI chat [no fork]; (D) fork OWUI to host company surfaces [license-capped]; (E) keep separate
  faces on one shared backend. Non-exclusive. Direction is Tim's to recognize, not mine to fix.
- **Heal (internal):** characterize whether `claude-ds`'s axes/solvers and the DNA grammar are one model
  under two names (then converge); pick a renderer-convergence direction (canvas tldraw vs surface DNA).

## 3. The company-internal coherence ledger (healed in the same pass)

"No duplicates" inward. The fusion surfaces these company-side dupes/half-builds; each gets resolved as part
of the work (proposed, per Tim's instruction):

| # | Internal issue (verified) | Proposed resolution |
|---|---|---|
| I1 | Two named-channel stores (cc_channels `_channels/` vs session_channels `channels.jsonl`) | Fold cc_channels named-store into session_channels; keep cc_channels live-messaging |
| I2 | Doubled channel MCP tools (`cc_channel` vs `channels`/`channel_act`) | `cc_channel`=messaging, `channels`/`channel_act`=structure |
| I3 | `owui_room.py` reinvents the roster | Fold into session_channels as the OWUI-face adapter |
| I4 | Three brain↔OWUI seams (`:4300` shim, owui_room operator, `:8772` gateway) | Collapse to: RHM-as-Pipe + native-MCP tools |
| I5 | `-pro` anti-pattern still the live fallback (6 call-sites) | Role-resolve the fallback |
| I6 | Recollection split-brain (2 physical DBs, one unembedded) | Migrate-then-retire |
| I7 | 3-way episodic split (corpus / recollection / interim Chroma) | Converge to one substrate |
| I8 | Three design lineages; claude-ds↔DNA unlinked | Characterize-then-converge |
| I9 | Two surface renderers (tldraw vs DNA), neither in use | Pick a convergence direction |
| I10 | Stale map/memory claims (8004 "collision", floor 0.5, ref-clip-missing, channel_boundary "stubbed") | Correct the maps/memory |

## 4. Build sequence (reversible, foundations first)

1. **Foundations (F1–F5)** — dead mouth, broken STT shim, bridge load-guard, vLLM autostart, kill `-pro`.
   Small, mechanical; without them voice + acting are hollow.
2. **Brain + Tools seam** — RHM-as-Pipe + verify-then-wire native MCP tools. (Proves the operator acts by
   voice through OWUI's own model surface.)
3. **Voice** — thin shims to loadout-aware bridge endpoints (after F1/F2). Voice follows the loadout.
4. **Channels** — fold owui_room → session_channels; OWUI channel = company channel; build in @model/threads/
   reactions/realtime; resolve I1–I3.
5. **Conversations** — the new conversation store + OWUI chat as a view; resolve I6.
6. **Knowledge** — corpus-as-store + harvest OWUI RAG plumbing; resolve I7; correct stale bug-claims.
7. **Identity** — principal registry (agent/viewer) + AccessGrant authority.
8. **Faces** — Tim picks among the five options; then build toward it.

Each step verified by-use before the next; each a reversible commit; company-internal heals folded in as the
relevant capability is touched.

## 5. Honest status

- **Verified live this pass:** the broken foundations (F1–F4), the channel store/tool duplication, the
  no-conversation-store fact, the recollection 2-DB split, the stale bug-claims, the two renderers, OWUI 0.9.6
  stock + its fork-only frontend + license cap.
- **Assumed / map-sourced (not re-verified):** OWUI internals beyond what was probed; the exact OWUI MCP
  client transport-fit (named as the key verify-item for the tools seam).
- **Not trusted:** every "it works" / "this is the design" in either codebase. Where this proposal relies on a
  seam, that seam is named for live verification before build.
