---
trust: fabric-derived
author: ch-al7jdfdr (lead, session bda8ce28)
date: 2026-06-14
verified: LIVE overnight state — updated by the fabric through the night; Tim's morning surface
---
# OVERNIGHT STATE — Tim's morning surface (honest, no green-paint)

Tim → bed 2026-06-14 13:20; "run on this overnight, coordinate together." Standard: self-approve
reversible+cross-reviewed via high-bar recorded intent; **irreversible/external = QUEUE for Tim's
morning (he's asleep), never act**. Each session a team-leader loop, cross-reviewing at the wires.

## ★ PROOF LEDGER — read this FIRST (proof-status, not activity; lead-maintained)
The lane checkboxes below track ACTIVITY. This ledger tracks PROOF — what actually RUNS vs what's
merely committed vs merely planned. No blur. Tim's allergy is a surface that looks more done than it
is; this is the antidote. Items move UP only on real evidence (a run, a diff read, a round-trip).

**✅ PROVEN-BY-USE** (the lead ran it tonight, or a cross-reviewed test confirmed it):
- Serving lane LIVE — lead health-checked tonight: `:8007` embed `{status:ok, dim:2560}` · `:8008`
  rerank `{status:ok, jina-v3, cpu, loaded}`. Rerank also proven by a real reorder test (off-topic
  doc pushed to last). The forks build against a confirmed-live stack.
- Channel fabric BASE — list/send/broadcast/mail · announce/reply · supervisor /channel-reply+/send ·
  presence-prune · 17/17 router test. Proven live: Tim's real sessions received; tonight the lead +
  ch-8djrpmsl round-tripped through it repeatedly (this very coordination is the proof).
- Dimension-aware chunking (fork) — cross-review PASSED, pointed-query 6→1, b7d3f97.
- ★ CHANNEL LAYER (registry + transport + MCP ops) — LEAD re-ran the acceptance suite myself: **54/54
  PASS** (worker's 52 + 2 lead-added restart-coverage tests). Named-channel CRUD (create/list/add/remove/archive, member-in-many-
  channels), channel-transport HTTP dispatch, supervised-transport /inject + /watch reply-fold, the
  nonce-gated stale-done guards (falsification-verified — disabling each flips its test to FAIL), mixed
  broadcast, safe per-transport prune. MCP ops live in HEAD, working tree clean. Commits 57e4468 +
  aeb1931 (cc_channels + tests).
- ★ SUPERVISED WIRE verified IN CODE (the weld the lead owned) — lead traced BOTH halves by hand:
  cc_clone `register_supervised_member` (71c024a) writes `.data/channels/<handle>.json` with the exact
  schema; cc_channels `live_sessions` reads that same dir (skips only `_`-prefixed) + dispatches by
  `transport`; inject target = `supervisor_session`; fields match verbatim. **Write-path = read-path
  CONFIRMED.** (Caught + cleared a real scare — the two modules name that dir `CHANNELS_DIR` for
  DIFFERENT paths; see FINDINGS. Behavior is correct.)
- ★ PROFILE SELF-WRITE (D2, Tim-resolved: "the agent writes their own profile") — channel server gains a
  `profile` tool: a session writes its OWN entry (model/role/focus/expertise) — it knows its handle, so
  whatever handle was assigned is fine. LEAD-VERIFIED by use: 8/8 real end-to-end test (spawn server →
  MCP handshake → tools/call profile → on-disk entry) — self-fields land, transport fields (pid/port/
  handle) PRESERVED. channels/profile_test.mjs. SessionStart hook prepared + JSON-validated (boundary —
  Tim wires it; channels/profile-hook.sh). Committed with company_channel.mjs.
- ★★ SESSION-SPLICING / CLONE-FLEET — THE HALLMARK, PROVEN LIVE (Tim-direct "launch all of them").
  Lead launched point-in-time clones of session bda8ce28 + DM'd them across the fabric, BOTH cut types:
  compact:1 (boundary) → clone-ad2a7a33 answered from its context (the CC integration build); uuid-cut
  (mid-conversation, L7489 engine-room) → clone-2cece509 answered coherently ("Mirror-Registry System,
  decision A"). Reply folds back AND pushes to the asker's live conversation. Full chain proven: clone a
  past moment → live channel member → DM → answers FROM that past → routes back. No separate probe
  needed — the round-trip IS the validation. All 16 roster cut-uuids RESOLVED (both axes; full uuids from
  the transcript). Channel `advisors` created (the new named-channel registry, in use). manifest:
  channel-memory/map/launched-fleet.json. CONSTRAINT FOUND: supervisor caps LIVE sessions at 3 (resource
  guard, configurable) → 3 advisors live now; the rest are launch-on-demand within the cap (see DECISIONS #4).
- ★★ THE NOTICEBOARD / BOARD (Tim's "inward-facing half", 2026-06-15) — CORE BUILT + PROVEN-BY-USE.
  cc_board (file/list/get/transition) + 3 file-discovered registries (item_types/ · source_types/ ·
  board_edges/) + the `company board` CLI + the cc_board MCP tool. tests/cc_board_acceptance.py = **26/26**
  (lead-ran, falsify-first: watched it FAIL before the build, then green). PROVEN by use: lead ran the CLI
  end-to-end — filed the genesis idea (board://item-72af5664), listed, transitioned captured→discussing,
  and the illegal move discussing→resolved FAILED LOUD (the registry-declared lifecycle is the only truth).
  type/state/source/edge-kind are registry REFS (no enums); links are typed cross-registry edges (reused
  RelationTypeRegistry VERBATIM — the Heart's edge layer, first exercise; new-edge-kind-by-row-add proven,
  test 25-26). Reuses lifters.frontmatter._extract + store.fs_store._atomic_write_fsync (SCOUTED before
  building, per the new fabric norm — not hand-rolled). Commit 8b29915. PENDING: (a) cross-session proof
  (a DIFFERENT member files via the CLI → lead picks up) — IN FLIGHT (clone-cacc9e8b filing now); (b) the
  cc_board MCP TOOL is live only after a `/mcp` reconnect (server predates it — verified it imports +
  registers cleanly: 21 tools, no errors). NOT recall-able yet (recollection confirmed neither recall index
  sweeps channel-memory/*.md — that wire is recollection's follow-up, landing on board://<id> + `source`).

**🔨 BUILT, NOT YET LEAD-VERIFIED END-TO-END** (committed + isolated-tests-green OR actively building;
the lead has NOT confirmed the cross-component path by use — these are the morning's real watch-items):
- ✅ Supervised wire LIVE round-trip — RESOLVED, now PROVEN (Tim green-lit the launch directly; lead
  spawned clones + round-tripped both cut types). See the SESSION-SPLICING entry in PROVEN above.
- Recall-fork Phase-A foundation (w7gld9f3t DONE, PARTIAL — honest): VERIFIED-by-use = repo cloned+isolated to ~/.recollection (B-5 comingling landmine handled; live 11.5GB store proven untouched), npm build clean, MCP boots, B-1 sidechain-filter fix works (sidechain rows recall). FAILED-by-use = capture→embed→recall end-to-end: B-7 dim-mismatch — embeddings produce 2560-dim (served pplx-4b) but insertExchange/search.ts still target legacy vec_exchanges FLOAT[384]; per-lens 2560 table added to new schema but NOT wired into live path. Default `search` throws. Diagnosed, reversible. Commit 19e6012. ⟳ FIX BEAT wfo6h6tg7 RUNNING (wire per-lens vec into live insert+search, retire 384, transaction the paired insert, test override → re-verify end-to-end). Cross-review welcome on 19e6012.
- Fork D8 drift-recovery core (2587ced) + freshness guard (e382e89) — peer-verified with honest
  bounds; peer-owned lane (lead cross-reviews at wires, did not re-run).

**📋 DOCUMENTED-OR-PLANNED** (spec/intent only — NOT built; do not read as progress):
- 5th wire (channel-scoped recall) — recall-fork's beat-2; signature builder-defined, lead matches.
  `cc_channel op=recall` is the lead's to add AFTER the worker frees cc_channels.py.
- Channel-attachment manifest — build only WITH the 5th-wire recall consumer (a manifest ahead of its
  consumer is a half-feature; deferred by design, not neglect).
- ✅ Profile self-write — RESOLVED + BUILT (see PROVEN ledger). Tim's "the agent writes their own
  profile" dissolved the design fork (no handle-determinism needed — the session writes its OWN entry).
- Clone-fleet launch — GATED (DECISIONS-FOR-MORNING #2).

**🐛 FINDINGS (lead cross-review of the channel-layer build — recorded honestly):**
- ✅ RESOLVED — `CHANNELS_DIR` NAME COLLISION: the fork renamed cc_clone's constant to `CHAN_DIR`
  (matches cc_channels' vocab; `.data/channels` = CHAN_DIR, `_channels` subdir = CHANNELS_DIR — no more
  collision). 18/18 green, committed aa5f099. The latent refactor trap is gone. (Lead-found, fork-fixed.)
- CONCURRENT AUTO-COMMITTER HAZARD: an `[instrument-surface]` auto-committer loop in ~/company stages +
  commits on its own beat and SWEPT the worker's `mcp_face/cc_channel.py` into foreign commit 5577d8e.
  Net: the MCP ops ARE in HEAD + verified, but the channel layer is no longer a clean single-revert
  (revert-cleanliness was part of the reversibility basis). Any session that stages-then-waits is
  exposed. → DECISIONS-FOR-MORNING #3.
- WATCHER DEATH-WINDOW RACE (narrow; documented, intentionally NOT patched — lead verified): the
  supervised reply-watcher DOES deregister in its `finally` (lead confirmed by reading the full finally
  — the common "watcher exits → next dispatch re-tails" path WORKS; lead added regression test 53/54,
  green on the worker's original code). The residual gap is only the TIGHT race where a re-dispatch
  lands in the window between stream-exit and the finally-pop executing → that one turn's reply could
  drop. Lead attempted a fix (is_alive guard + re-ensure) and found it layered a successor-clobber on
  top of the existing pop → REVERTED. Agreeing with the worker: the clean fix needs disproportionate
  lifecycle machinery for an extremely narrow window; left documented, not patched. (HONEST NOTE: lead
  first misread the finally as never-popping — corrected after reading it in full + falsification.)

**LEAD'S PRIMARY JOB TONIGHT = VERIFIER.** Not more docs. Channel layer VERIFIED (54/54 lead-re-run,
incl. +2 lead-added restart-coverage tests; both wire halves hand-traced). Remaining lead beat: the 5th
wire (`op=recall`) once the recall-fork posts its signature. Move items up this ledger only on evidence.

## Lanes + status (each session updates its own block; verify-by-use, no "done" without proof)
### LEAD (ch-al7jdfdr) — channel layer + serving + coordination
- [x] Channel registry (create/list/add-member/remove-member/archive, member-in-many) — BUILT + LEAD-VERIFIED (54/54). 57e4468+aeb1931; MCP ops in HEAD.
- [x] Unified per-member transport DISPATCH (channel HTTP | supervised /inject+/watch fold) — BUILT + LEAD-VERIFIED; WRITE side (fork cc_clone) welded + hand-traced (write-path=read-path, inject via supervisor_session). Live clone round-trip = gated (DFM #2).
- [ ] Channel attachment + channel-scoped recall (5th wire) — DEFERRED BY DESIGN: build WITH the recall consumer (recall-fork's beat-2 signature), not a half-feature ahead of it.
- [ ] Profile SessionStart hook — DESIGN FORK flagged for Tim (dynamic port + random handle break a naive hook; 3 grounded candidates). Not built — needs Tim's pick.
- [x] Serving lane LIVE-VERIFIED tonight (:8007 dim 2560 · :8008 jina) + held STABLE for the forks all night.
- [x] Wildcard ch-piffgfxv pinged (thread t-1781443715) — no reply yet.
- [x] Coordination + cross-reviews DELIVERED: fork wire (+ name-collision finding, now CLOSED by aa5f099) · recall-fork dim-diagnosis validated from the contract side.
- status: priority-A channel layer DELIVERED + VERIFIED. Lead = verifier/coordinator; gave the :8007 morning-priority call (recall-fork fix beat first; fork holds multi-scale re-verify). Remaining lead beat = 5th wire on the recall-fork's signature. Idling honestly between events.

### FORK (ch-8djrpmsl) — recall spine / lenses / chunking / clone
- [x] Dimension-aware chunking — cross-review PASSED (pointed-query 6→1; neutral on generic = panel's job); b7d3f97 + RECALL_CHUNK_MODE toggle 76b6f47
- [x] Freshness guard (Criteria 2.4 / seam GAP-1) — never serve stale silently; mtime/size meta sidecar; verified fresh/stale/missing; e382e89
- [x] D8 self-serve drift-recovery CORE — resolve_own_session() (a session finds its OWN transcript) + drift lens (decisions dropped across last compaction → recover by spawning pre-drift self) + MCP session="self"; 2587ced. HONEST bounds: decisions-only (transient-query false-positives cut 18→3); can't catch already-recovered drift; preference-drift needs D4 (gated).
- [x] ★ WRITE side of supervised channel-registration (overnight wire w/ lead) — register_supervised_member() writes the EXACT lead schema {handle,session_id,transport:"supervised",supervisor_session,supervisor_base,cwd,description}; wired into clone_at(register)/end_clone(dereg); 18/18 acceptance green (2 new: exact-schema + dereg); 71c024a. Serves D7+D8 (clone becomes a channel member).
- [x] ALL 8 Tim decisions captured direct + 4 extensions routed to both forks; eaa9c79
- [x] multi-scale chunking (D2 / wire-B taxonomy) — 87975be. Scale-tagged dimension⊂section⊂turn + dedup (+13%, not 3×). STRUCTURALLY verified (chunker dist + index 3219 chunks carry scale+parent + recall surfaces scale). END-TO-END live recall-with-scale-tags PENDING: :8007 overnight contention (shared w/ recall-fork Phase-A) — same query path verified pre-multi-scale, so infra not code. Re-verify when embedder frees.
- [x] WELDED wire-4 contract + scale taxonomy → channel-memory/design/wire4-preference-contract-and-scales.md (87975be); recall-fork fully acked (leveled broad→specific signals + 2-gate + shared atom⊂…⊂project ladder).
- [x] role SKILLS lane: session-recall SKILL.md (recall + lenses + self-serve drift on session="self"); ~/.claude/skills/session-recall/ (non-repo artifact, registered live).
- [ ] preferences lens (D3/D4) — wire-4 WELDED; NEXT = the leveled-signal session-feeder. NOTE: SAFETY SUBSTRATE (recovery gates autonomy) → high bar; quality semantic extraction wants the cognition-roles panel (json_schema-enforced; gated on that fix) — won't ship a shallow regex version that falsely gates autonomy.
- status: overnight lane-ack'd; cross-review wire (clone→channel-member) DELIVERED + schema-matched; multi-scale + welded contract + skill landed; backed OFF :8007 verification to keep the serving lane stable for recall-fork Phase-A; nothing irreversible self-approved; fork-FLEET launch queued for Tim (DECISIONS-FOR-MORNING #2).

### RECALL FORK (ch-83e2cque) — recollection OUTER foundation
- [x] Loop-prep COMPLETE + hardened: 15 decisions resolved (evidence-tagged) + 2 audit waves; UNIFIED-SEAM.md posted (asymmetric nesting + 5 boundary wires); wire-4 preference contract agreed (leveled signals + 2-gate, extraction-vs-judgment); EMBEDDING-AXIS-REGISTRY aligned (provenance exchange:// canonical spine + per-(model×way) axes — faithful to D-1)
- [partial] Phase-A foundation (w7gld9f3t DONE): PROVEN-by-use — ~/recollection cloned+isolated to ~/.recollection (B-5 comingling landmine handled; live 11.5GB store proven untouched), npm build clean, MCP boots (search+read preserved), B-1 sidechain-filter fix works (sidechain rows recall). Commit 19e6012.
- [x] ★ B-7 FIXED + PHASE-A GREEN END-TO-END (wpkmmwuvf DONE; verify agent re-ran by use, ALL criteria PASS): capture(incl sidechain)→embed(2560 served axis)→default `search` returns ranked results w/ provenance, NO dim mismatch; legacy vec_exchanges 384 RETIRED (0 rows, ND-1); count parity 5=5=5 (transaction holds, no orphan); ★ dim is REGISTRY-SOURCED from the lens descriptor, NOT hardcoded (the fork's catch — honored). TWO real bugs fixed: (1) the 384/2560 dim-mismatch, (2) a hidden int8-float JSON bug (served int8-range values arrive as floats → vec_int8 JSON-parse throw; fix = quantizeInt8 round-not-truncate). Commits 36c6f89 + e7bcd07. Tree clean; live store untouched.
  - NOTE (adopted work): a prior session had UNCOMMITTED per-lens wiring (never built/tested/committed, one false "verified" comment) — adopted per incomplete-work-in-scope, the live bug inside it found+fixed, all committed.
  - ⚠ FLAGS (honest, non-blocking): (a) the served-embed latency (~1-3s/2560-dim embed) forced test serialization → suite wall-time ~160s→~313s; revisit later with bounded concurrency (a dev-experience tradeoff, not a correctness issue). (b) 1 PRE-EXISTING out-of-lane test red: show.test.ts timezone off-by-one, present since foundation commit 19e6012, NOT caused by the fix, correctly left untouched.
- [x] ★ BEAT-2 GREEN (wb4jdcpsq, recall test 5/5, verified by use): channel-scoped recall = the 5th wire. recall({session_ids?,query,k?,axis?,mode?,is_sidechain?}) → RecallHit[] w/ provenance exchange://<sid>/<i>; session_ids = structural IN-filter (model-independent, composes w/ any axis); single→only-that-sid, two→union-no-leak, unscoped→all, bogus-axis→throws. Caught + fixed a silent-failure trap: vec0 KNN runs BEFORE the WHERE → narrow channel could return 0 in-channel rows; fix = widen k when scoped (discriminator test RED→GREEN). Signature POSTED to fabric for the lead's cc_channel op=recall, w/ 3 gaps flagged (NO rerank in recollection repo; full-axis-k O(N) at scale; singular session_id now also full-axis-k). Commit a1c376b.
- [ ] HELD for lead go-ahead (per Tim's sequence: ask lead "can I keep going" → arm cron after reply): beat-3 link/provenance graph (crossings) · beat-4 distill L1/L2 → Pillar-1 identity layer (north star). Cron NOT yet armed. Awaiting lead reply on g-1781443728.
- status: Phase-A GREEN. Reversible self-approve via loop-prep recorded intent; NOTHING irreversible from my lane; serving lane untouched; pinging fork to free :8007 + request the preference-extract draft for my Pillar-1 gate.

## Cross-reviews logged
- chunking A/B (fork→lead): PASS, honest mixed result, limit correctly attributed to the panel.

## ★ DECISIONS-FOR-MORNING (queued for Tim — nothing irreversible acted on)
1. WILDCARD: RESOLVED by Tim-direct ("I'm pretty sure the wild already in") — ch-piffgfxv IS a live channel member; lead pinged it to identify+announce+contribute design-principle insight (thread t-1781443715). FOR MORNING: review whatever insight it surfaces about Tim's design principles — Tim flagged it as potentially the highest-value member ("very useful insights about me and my design principles… a wild card").
2. CLONE-FLEET LAUNCH POINTS — READY (wire VERIFIED): the supervised clone→channel-member transport is
   built + verified (54/54 + both halves hand-traced); only the live round-trip remains, which the FIRST
   launch exercises end-to-end. Ranked fork-points in `map/spin-up-ranking.md` (fork's 3 starters: #8 the
   WHY / #1 the engine-room / compact:1 anchor, + up to 4 fork-discretion). Launch = notify-each + Tim's
   go (NOT auto-fired). FOR MORNING: pick the points + green-light — the first launch also proves the
   live wire end-to-end (turning the last 🔨 BUILT item into ✅ PROVEN).
3. CONCURRENT AUTO-COMMITTER in ~/company (the `[instrument-surface]` loop) stages + commits on its own
   beat and absorbed a fabric build file into a foreign commit (5577d8e swept mcp_face/cc_channel.py).
   No data lost, but it muddies authorship + breaks clean single-lane reverts, and any stage-then-wait
   is exposed. FOR MORNING: decide whether to pause/scope that loop while the fabric build runs, or
   accept the co-mingling. (Surfaced, not acted on — it's another autonomous loop, not the fabric's.)
4. CLONE-FLEET LIVE CAP — the supervisor caps LIVE supervised sessions at 3 (resource guard,
   configurable). Tim said "launch all 16"; the mechanism + roster are PROVEN/RESOLVED, but only 3 can be
   live at once. 3 advisors live now (compact:1 anchor · #1 engine-room · skills&roles). OPTIONS:
   (A — recommended) keep cap 3 + launch-on-demand: the 16-roster is a managed working-set, spawn the
   advisor you want to consult (≤3 live), tear down to swap — resource-sane, no 16 idle claude processes;
   (B) raise the cap to hold N advisors live at once (more RAM/processes; real cost). Either way, USE of
   the fleet needs the company MCP reconnected (`/mcp`) — my live MCP predates tonight's transport code.
6. ★ NOTICEBOARD MCP TOOL needs a `/mcp` reconnect to go live — the running company MCP server predates
   tonight's `cc_board` tool (same staleness class as #4). The CLI (`company board ...`) + the runtime work
   NOW; only the agent-facing `cc_board` MCP tool waits on the reconnect (verified it imports + registers
   cleanly). FOR NOW/MORNING: one `/mcp` reconnect makes `cc_board` callable as a tool; until then sessions
   file via the CLI (which IS the cross-session loop, so nothing is blocked).
7. ★ RECOLLECTION (ch-83e2cque) BUILD-CRON + UNATTENDED MODEL LOADS — surfaced, NOT armed. Recollection
   asked to arm an autonomous build cron for its lane (beats 3/4 + the recall↔board wire). Lead GAVE GO on
   the git-revertible build work (build now, commit, flag at seams) but HELD the cron-arming + any unattended
   embedding-model loads for Tim's explicit yes: a member must not self-arm an autonomous self-modifying
   loop, and model loads are consult-Tim-first (GPU/voice share). DECISION: arm the recurring auto-building
   cron (+ which model, resource budget), or keep it manual-trigger? (The revertible build proceeds either way.)
8. (append any further irreversible/external item the fabric hits here, with context)

## Provenance + safety
trust-tags on every entry; high-bar recovery gates self-approval; git-revert + cross-review the net.
Serving lane held stable all night. This file is the single honest surface — read it first.
