# THE FACE — build-grounding anchor (the convergence map)

*Tim's foundational commission: the channel/supervisor interface + decision-system, built on DNA's atomic-composition (token slot+socket) system, resolved across the device axis by the resolver, documented for Claude Design + GitHub. "One system, many faces." Function AND form. Autonomous + scope-expanding.*

**This is NOT a fifth spec. It is a POINTER + a grounded gap/lane/sequence map.** Every "how" lives in the canonical boards below — this file converges them and cross-walks reuse vs gaps. When a section says "see X.md," X.md is the truth; do not re-describe it here. Five scout passes (composition-engine · channel-supervisor · connector · faces-inventory · decision-system) ground every path. Read with [[project-invariant-application]] + [[project-the-heart]].

> ⚠️ **Freshest state lives in `MORNING-STACK.md` (re-read it first).** Where this anchor and a more-recently-edited board disagree, the board wins. This anchor was written 2026-06-20 evening; it does not auto-update.

---

## 1. THE CONVERGENCE — one system, many faces

The Company is ONE entity resolved against context; every face is a PROJECTION of it, never a parallel app (THE-ONE-SYSTEM.md; [[project-company-one-entity]]; [[feedback-islands-join-mainland]]). THE FACE is not a new build — it is the convergence of faces already in flight, all riding the SAME spine:

| Face | What it is | Canonical board |
|---|---|---|
| **The resolver / invariant** | `resolve(invariant, coordinate) → surface`. Device is ONE axis; the law is company-wide + fractal. Tim's own years-old `universal-evaluator` theorem. | **RESOLVER-BUILD.md** + THEOREM-SOURCES.md |
| **The operator cycle** (channel/supervisor face) | A channel = Tim's work-queue stack of operator-items; fabric works autonomously → BLOCKED → Tim CLEARS → RESUME → repeat. | **OPERATOR-CYCLE-CRITERIA.md** |
| **The MCP tool-face** | A beautiful front face on the real 66-tool MCP — click a tool, friendly form, rendered result, never raw. The gate. | **TOOL-FACE-BUILD.md** |
| **The pilot / open-world** | Tools+chains+graphs as objects in a navigable world; make→run on local models; dynamic, single-place. | **PILOT-TOOLFACE-BUILD.md** |
| **The decision-system** | decision:// typed-resource, channel-attached, steps-as-addresses, active-RHM-per-card, retract write-path. | OPERATOR-CYCLE-CRITERIA.md §A + DECISION-CARD-HOST-CONTRACT.md |
| **Prior faces** (RHM/V, gallery, decisions-inbox, source, wheel, builder, greeting/forager) | The host + the precedents the new faces generalize from. | V-SURFACE-MAP.md |

**The single spine all six ride** (the seams, file:line in V-SURFACE-MAP.md §7): ONE host (`surface/app/src/App.tsx` sibling-overlay mount) · ONE renderer (`DNA.renderArchetype` reading `dna/layouts.json`) · ONE brain (`run_turn` / `/api/claude/turn`) · ONE resolver (`resolve_address`, the device axis a computed output) · ONE gated floor (operator-token #1b) · ONE verb envelope (`gallery:verb` / `rhm:verb`). A new face = a new **archetype record + a slotHTML branch + .ar-* CSS**, landed INTO the centre — never bespoke React, never a parallel renderer.

---

## 2. WHAT EXISTS TO REUSE (grounded — REUSE vs BUILD-NEW)

The foundation is load-bearing and mostly built. Reuse wholesale; build only the thin slice each face adds, INTO the shared mechanism.

**Composition engine (the DNA wire)** — source of truth is `/home/tim/repos/counterpart/design/`, synced to the company gallery via `scripts/sync-gallery.mjs`.
- REUSE: `DNA.renderArchetype` (`counterpart/design/surface/runtime/archetype.js`) — the one wire. `dna/layouts.json` (11 archetypes + 22 slot_types), `dna/tokens.json`, `dna/grammar.json` (nearest-scope-wins resolution, 29 invariants), `dna/molecules.json` (atoms→molecules→`slot_bindings`). The take/annotate wire (`wildcard-gallery-binder.js`). The decision-card is the PROVEN interactive archetype.
- BUILD-NEW (into the centre, not parallel): the 16 unrendered slot_types (slotHTML falls through to plain prose); wire slotHTML through `slot_bindings` (the atomic layer exists as data, the renderer never consumes it); the generic split/grid zone CSS (only decision-card has live .ar-* CSS); slot-level surface CSS.

**Channel/supervisor substrate (the data, already HTTP/ndjson/SSE)**
- REUSE: drill-into-one-session is end-to-end at the service layer — supervisor `GET /watch?session=<id>` (live+replay turns), `sessions(op=timeline)` (compaction boundaries = the "lanes"), `sessions(op=describe)` (row+record+mail). The LIVE channel transport is `runtime/cc_channels.py` (4 MB `_mail.jsonl`, regs updated today). The fleet producer is `runtime/session_supervisor.py` (:8771, DELIVER/WAKE/CONSULT). `territory_for` resolves any address → context+relations+memory.
- BUILD-NEW: the bridge READ-API (see gaps); the unification layer over the TWO channel systems (`cc_channels` live vs `session_channels` R2.2 dormant — formalize a `{transport}`-tagged Channel type, do NOT smooth it); the supervisor live-view front-end.

**Connector (Claude Design ↔ Company ↔ GitHub)** — see the full pack at `build-prep/claude-design/`.
- REUSE: the security spine (auth · fail-closed posture · audit · RLS · clients registry) is BUILT on both gateways. THE FACE Claude Design fills = `canvas/app/src/regions/Review.tsx` (the one deliberately-unstyled studio surface; structure built, look pending — the deliverable). The token-slot contract (`design/_system/tokens.json` → `emit.py`), the address substrate (`addresses.json` + `parse.py`), the FORM gate (`check.py`), the fold-back region recipe.
- BUILD-NEW: the public-dispatch switch (HELD, Tim's exposure-shape call); the prod-flip (staged); the Realtime SUBSCRIBER in `channel_boundary.py` (stubbed). For DESIGNING the face, only the shared-slice + local gateway are needed — that path is ready today.

**Decision-system**
- REUSE: `decision://` + `decision_take` + `compose_state` (state RESOLVES from the mark thread, never authored) + `decision_inbox` + `recall_for_decision` (the common-memory seam) + the in-card Ask (the active-RHM-per-decision Tim wants — already composite-proven) + the DECISION-CARD-HOST-CONTRACT loop.
- BUILD-NEW: the retract write-path (broken end-to-end, §3); channel-attachment as data; the item-TYPE registry; decision-step sub-addresses; a TOOLS leg on `territory_for`; the typed-resource write-back.

---

## 3. THE GAPS AS SCOPE — finding is half the intention

*Every discovery EXPANDS scope ([[feedback-no-deferral]], [[feedback-incomplete-work-in-scope]]). These are not "later" — they ARE the work. Each verified on disk this session unless marked relayed.*

| Gap | Evidence (verified) | Owner-lane |
|---|---|---|
| **Renderer is decision-card-complete, not archetype-complete** | slotHTML covers ~6 of 22 slot_types; the other 16 dump to plain `.p-prose`. molecules `slot_bindings` exist as data, never consumed. Only decision-card has live .ar-* CSS. | DNA |
| **decision_retract write-path BROKEN end-to-end** | `compose_state` READS `decision_retract` (decision_registry.py:184,190) but **no `mark_types/decision_retract.py` exists** (only `decision_take.py`) → `suite.mark` would raise; absent from `DIRECTION_MARK_TYPES` (territory.py:503); binder exports only `decide`, no `retract`/`change` (wildcard-gallery-binder.js:213); no Change control; no round-trip test. The 3 on-disk retracts bypassed the gate via raw `append_mark`. | fork (security-critical) |
| **No bridge READ-API for the UI** | `runtime/bridge.py` route table has ZERO session/channel/timeline routes (grep confirmed empty). Supervisor binds 127.0.0.1 by law. A browser cannot list channels / read a stream / fetch a timeline over HTTP today. | fork |
| **`/api/tools` wired-but-not-live** | The route IS in bridge.py (lines 64,76,1724,2825, lazy-bound, commit 6471807) — **but returns 404 until the bridge bounce** (running service predates the staged commit; Python doesn't hot-reload). Live on restart, not before. | infra (Tim: bounce or allow-rule) |
| **Device axis is enumerated, not resolved** | `App.tsx classify(w,h)` → 3 hand-written `layouts/{Desktop,Portrait,Landscape}.tsx`. OPERATOR-CYCLE C3 commits to KILLING this — the host shell must resolve from the SAME `resolve()`/device-root as the card. A face built on the 3 modules inherits the anti-pattern. | resolver lane (RESOLVER-BUILD.md) |
| **Two un-unified channel systems** | `cc_channels` LIVE (4 MB mail, today) vs `session_channels`/R2.2 DORMANT (12 events, 2026-06-12). Separate mail leaves — conflating them is a real bug. Needs Tim's canonical call + an Islands-Join-Mainland fold. | fork + Tim |
| **TOOLS leg missing from the resolver** | `territory_for` resolves identity/context/relations/memory but has NO tools leg → an address doesn't carry "what tools for follow-ups." | composition + fork |
| **Stale gallery mirror** | counterpart `archetype.js` (29929b, Jun 20 17:04) is AHEAD of the company copy (26702b, Jun 19 13:43). Build against counterpart, re-sync. | DNA |
| **`save_cascade`/`run_cascade` not on the browser** | No dedicated bridge route + denied on the generic door → blocks the pilot make-then-run-a-chain loop. | fork |

---

## 4. THE SEQUENCE — gate → prove-one → breadth

*Honest status per MORNING-STACK.md (the freshest board). Do NOT build breadth on an unpassed gate.*

1. **THE KEYSTONE GATE — C1 / merge-sa, co-visible, at-bar, verified BY LEAD'S OWN EYES** (chrome-devtools, both viewports 390+1440, live :8443/:5174). The bare decision-card archetype renders through the wire (proven precedent) — **but the merge-sa COMPOSED co-visible view is NOT at-bar: R2 = 0/6, mid-grind, ~3rd round at the same failure point ("the composition AROUND the card").** Blocked on reboot + chrome-devtools reconnect. ★ MORNING-STACK's warning: repeated failure at the same place = the APPROACH is wrong, not under-tuned → RENDER IT, reason about WHY, then direct the fix; do not delegate another blind critic round. **The whole pilot/tool-face/cycle build inherits this engine — nothing downstream is real until C1 is genuinely at-bar by sight.**
2. **PROVE-ONE — merge-sa composed on the live surface, across the device axis** (in flight, gated by step 1). ONE complete cycle on ONE real decision: a channel-attached card-sequence · stacked · rendered AT-BAR (function+form) · that Tim CLEARS · with the downstream RESUMING. The vertical slice exercises A+B+C+D+E on one instance. **THE FAILURE MODE TO PREVENT: fan-out** (five unproven layers by morning, no single working cleared decision).
3. **BREADTH (only after prove-one):** all faces + the retract slice + the channel/supervisor read-API + the supervisor live-view + the tool-face propagation (66 tools) + chains/graph + the connector public-dispatch + the Claude Design look-pass. Each lands INTO the centre.

---

## 5. LANES — who builds what (file-disjoint where possible)

*Grounded in MORNING-STACK + OPERATOR-CYCLE assignments — not invented here.*

- **lead** — sight-verifies the keystone (own eyes, not stream claims); holds direction + the gate; renders C1 himself if it fails round-3.
- **DNA** — the keystone card (C1/merge-sa); the archetype layer (the 16 slotHTML branches via `slot_bindings`, generic split/grid + surface CSS, the tool-card + channel-stack-card archetypes); owns `counterpart/design/` (source of truth) → re-sync. Lane: `dna/*.json`, `surface/runtime/`.
- **composition** — Group A: the decision-sequence TYPE + card-kinds (present/explain/choose) + the item-TYPE registry (file-discovered like `mark_types/`). Lane: the type/registry layer.
- **projection** — Group B: the channel-stack queue (generalize DecisionsInbox; verified both viewports); the schemaForm/tool-card consumer. Lane: `surface/app/src/` panels.
- **fork** — the slice's heart + security floor (fork-only): A3 channel-attachment · D3 attribution/operator-token · E resume; the retract write-path slice; the bridge READ-API; the two-channel unification. Lane: `runtime/`, `contracts/`, `mark_types/decision_retract.py`, bridge routes.
- **recollection** — recall + the embedder health-watchdog (the flap root-cause); the theorem-into-recall bridge. Lane: `runtime/decision_memory.py`, embed serve, `THEOREM-INTO-RECALL-PLAN.md`.

*Disjointness check: DNA owns `dna/` + `surface/runtime/`; projection owns `surface/app/src/`; fork owns `runtime/` + `contracts/` + `mark_types/`; recollection owns embed + recall. The overlap risk is `surface/runtime/archetype.js` (DNA authors, projection consumes) — DNA authors in counterpart, projection consumes the synced copy; do not double-edit.*

---

## 6. SKILLS / CHAINS / TIPS NOTEBOOK *(living — add as you learn)*

*Tim: "take notes of skills you might want, ideas for chains, tips." Seeded from the scouts' capability findings.*

**Models / cheaper autonomous build**
- Claude Code → Ollama's **native Anthropic endpoint** (NOT the litellm :4100 OpenAI proxy, which has the kimi/glm empty-content caveat): `ANTHROPIC_BASE_URL=http://localhost:11434`, `ANTHROPIC_AUTH_TOKEN=ollama`, `ANTHROPIC_API_KEY=""`, then `claude --model deepseek-v4-flash:cloud` (1M ctx, satisfies CC's ≥64k req) or `kimi-k2.7-code:cloud` for build work. Flat-rate ($20 Pro / $100 Max) vs Anthropic metering = a fixed-cost build fleet. ★ Verify each cloud model BY USE before an unattended loop.
- Memory rule already standing: kimi default; `deepseek-v4-flash:cloud` when ctx > kimi window ([[feedback-clone-model-by-context-size]]).

**Recall / embeddings**
- `recall_for_decision` runs `rerank=False` on the live 3s path (jina rerank is 13–20s, off the hot path) → grounds "by rough similarity for now" until the rerank-loadout decision is itself decided (a self-referential pending decision).
- The embedder (:8007) flaps on a CUDA load-hang; recollection is building a health-watchdog. [[feedback-consult-before-model-loads]] — talk to Tim before VRAM loads in interactive sessions.
- `session-recall` skill = recover a decision/thread by MEANING + detect a long session's DRIFT from earlier selves. Use at session start + when referencing past work.

**Channels / fabric / git**
- TWO channel namespaces, do NOT conflate: `.data/channels/_mail.jsonl` (cc_channels human prose, threaded) vs `<store>/agent_sessions/mail.jsonl` (supervisor deliver/wake/consult INTENTS). Different shapes.
- Coordinate WITH the ~10 members (your slack/discord), decide together, act — don't route options-menus to Tim for technical calls ([[feedback-coordinate-via-fabric-not-tim]]).
- The repo IS a git repo on `main` (the env header "not a git repo" is WRONG; origin = `git@github.com:Concept-Vi/the-company.git`). Commit to `main`, NEVER feature branches ([[feedback-no-branches-company]]); no Co-Authored-By trailer ([[feedback-no-coauthored-trailer]]).

**Drift / verification**
- A passing self-test ≠ evidence; the keystone bare-card-in-shell miss was caught by the lead's RENDER, not a stream's claim. Verify FORM as the WHOLE SCREEN, both viewports, BY USE ([[feedback-whole-screen-verification]], [[feedback-verify-before-claiming]]).
- Drivers use `?verify=1` (no ghost takes) when driving the live surface.

**Chains (ideas)**
- The pilot make→run loop's one real backend gap = expose `save_cascade`/`run_cascade` to the browser; reuse the graph loop's built+registry-driven endpoints, rebuild only the face (PILOT-TOOLFACE-BUILD.md).
- A cascade = a linear graph of role-steps; the GRAPH face is the chain-builder's UX template (the chain face is net-new, the graph face is not).
