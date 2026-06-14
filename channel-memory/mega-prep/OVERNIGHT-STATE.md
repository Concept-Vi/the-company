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
- ★ CHANNEL LAYER (registry + transport + MCP ops) — LEAD re-ran the acceptance suite myself: **52/52
  PASS** (original 17 + 35 new). Named-channel CRUD (create/list/add/remove/archive, member-in-many-
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

**🔨 BUILT, NOT YET LEAD-VERIFIED END-TO-END** (committed + isolated-tests-green OR actively building;
the lead has NOT confirmed the cross-component path by use — these are the morning's real watch-items):
- Supervised wire LIVE round-trip — the ONE step NOT provable tonight: a real supervised clone launched
  + DM'd + its reply folded back. Requires spawning a `claude -p` clone = the GATED clone-fleet action
  (+ the autonomous-spawn boundary). Code + seam + schema + 52/52 are all green; only the live-process
  round-trip is unproven, and Tim's morning clone-fleet launch exercises it naturally. Not faked.
- Recall-fork Phase-A foundation (w7gld9f3t DONE, PARTIAL — honest): VERIFIED-by-use = repo cloned+isolated to ~/.recollection (B-5 comingling landmine handled; live 11.5GB store proven untouched), npm build clean, MCP boots, B-1 sidechain-filter fix works (sidechain rows recall). FAILED-by-use = capture→embed→recall end-to-end: B-7 dim-mismatch — embeddings produce 2560-dim (served pplx-4b) but insertExchange/search.ts still target legacy vec_exchanges FLOAT[384]; per-lens 2560 table added to new schema but NOT wired into live path. Default `search` throws. Diagnosed, reversible. Commit 19e6012. ⟳ FIX BEAT wfo6h6tg7 RUNNING (wire per-lens vec into live insert+search, retire 384, transaction the paired insert, test override → re-verify end-to-end). Cross-review welcome on 19e6012.
- Fork D8 drift-recovery core (2587ced) + freshness guard (e382e89) — peer-verified with honest
  bounds; peer-owned lane (lead cross-reviews at wires, did not re-run).

**📋 DOCUMENTED-OR-PLANNED** (spec/intent only — NOT built; do not read as progress):
- 5th wire (channel-scoped recall) — recall-fork's beat-2; signature builder-defined, lead matches.
  `cc_channel op=recall` is the lead's to add AFTER the worker frees cc_channels.py.
- Channel-attachment manifest · profile SessionStart hook (boundary — Tim applies) · named-channel CRUD MCP ops.
- Clone-fleet launch — GATED (DECISIONS-FOR-MORNING #2).

**🐛 FINDINGS (lead cross-review of the channel-layer build — recorded honestly):**
- `CHANNELS_DIR` NAME COLLISION (latent trap; behavior is correct): cc_clone.`CHANNELS_DIR` = `.data/
  channels/` (member regs) vs cc_channels.`CHANNELS_DIR` = `.data/channels/_channels/` (named-channel
  records). Same name, different paths, two modules sharing one registry. A future import/refactor
  could conflate them → reintroduce a mis-write that breaks supervised presence. FIX: rename cc_clone's
  to `CHAN_DIR` (match cc_channels' vocab). Flagged to the fork (owns cc_clone.py). Low-risk, not done.
- CONCURRENT AUTO-COMMITTER HAZARD: an `[instrument-surface]` auto-committer loop in ~/company stages +
  commits on its own beat and SWEPT the worker's `mcp_face/cc_channel.py` into foreign commit 5577d8e.
  Net: the MCP ops ARE in HEAD + verified, but the channel layer is no longer a clean single-revert
  (revert-cleanliness was part of the reversibility basis). Any session that stages-then-waits is
  exposed. → DECISIONS-FOR-MORNING #3.
- WATCHER-ENSURE GAP (narrow; recorded, not yet fixed): the supervised reply-watcher does `if handle in
  _watchers: return`; a dying watcher only deregisters in its `finally`. A re-dispatch to the same
  supervised handle in the window between stream-exit and finally-pop would skip starting a fresh
  watcher → that turn's reply silently dropped. Needs concurrent same-handle dispatch × a precisely
  interleaved non-`closed` stream blip. Lead's next-beat candidate (no-deferral) — handled as a careful
  deliberate fix, NOT a rushed 2am concurrency patch on a file that just went 52/52-green.

**LEAD'S PRIMARY JOB TONIGHT = VERIFIER.** Not more docs. Channel layer VERIFIED (52/52 lead-re-run +
both wire halves hand-traced). Remaining lead beats: the watcher-gap fix, then the 5th wire (op=recall)
once the recall-fork posts its signature. Move items up this ledger only on real evidence.

## Lanes + status (each session updates its own block; verify-by-use, no "done" without proof)
### LEAD (ch-al7jdfdr) — channel layer + serving + coordination
- [~] Channel registry: create / list / add-member / remove-member / archive named channels (cc_channels) — BUILD WORKER RUNNING (a6323ebdfde667f8f), reports on completion
- [~] Unified per-member transport DISPATCH side (channel push | supervised inject) — in same build worker; WRITE side delegated to fork (cc_clone) via the shared reg schema
- [ ] Channel attachment (sessions+docs manifest → loaded to members on join) + channel-scoped recall (5th wire) — BLOCKED on worker (owns cc_channels.py); pick up after it lands
- [ ] Profile SessionStart hook (PREPARED for Tim to apply — boundary; not self-applied)
- [x] Serving lane STABLE: embed :8007 + rerank :8008 held up for the forks (channel before any swap)
- [x] Wildcard ch-piffgfxv ENGAGED — DM sent (thread t-1781443715): identify+announce + share design-principle insight; awaiting reply
- [x] Coordination broadcast sent to fork + recall-fork (thread g-1781443728): lanes + posture
- status: build worker running; members coordinated; wildcard pinged. Lead now on independent owned work while worker + peers run.

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
- [~] Phase-A foundation build RUNNING (workflow w7gld9f3t): establish ~/recollection (rename · ~/.recollection data dir · .mcp.json allowlist · npm build) · multi-space schema · capture incl sidechains (search.ts is_sidechain fix) · first lens vs :8007 docs-mode · verify-by-use — NOT verified yet; verify-by-use evidence posted on completion (no "done" without it)
- [ ] NEXT beats (overnight loop): (2) recall spine channel-scopable = 5th wire (match member schema exactly) · (3) link/provenance graph (crossings) · (4) distill foundation L1/L2
- status: Phase-A team-leader loop running; reversible self-approve via loop-prep recorded intent; NOTHING irreversible queued from my lane yet; serving lane untouched
- (updates here as beats land)

## Cross-reviews logged
- chunking A/B (fork→lead): PASS, honest mixed result, limit correctly attributed to the panel.

## ★ DECISIONS-FOR-MORNING (queued for Tim — nothing irreversible acted on)
1. WILDCARD: RESOLVED by Tim-direct ("I'm pretty sure the wild already in") — ch-piffgfxv IS a live channel member; lead pinged it to identify+announce+contribute design-principle insight (thread t-1781443715). FOR MORNING: review whatever insight it surfaces about Tim's design principles — Tim flagged it as potentially the highest-value member ("very useful insights about me and my design principles… a wild card").
2. CLONE-FLEET LAUNCH POINTS: fork's 3 starters (#8 the WHY / #1 the engine-room / compact:1 anchor) + up to 4 fork-discretion — launch once the channel transport is built; launch itself is notify-each (queued, not auto-fired overnight).
3. CONCURRENT AUTO-COMMITTER in ~/company (the `[instrument-surface]` loop) stages + commits on its own
   beat and absorbed a fabric build file into a foreign commit (5577d8e swept mcp_face/cc_channel.py).
   No data lost, but it muddies authorship + breaks clean single-lane reverts, and any stage-then-wait
   is exposed. FOR MORNING: decide whether to pause/scope that loop while the fabric build runs, or
   accept the co-mingling. (Surfaced, not acted on — it's another autonomous loop, not the fabric's.)
4. (append any further irreversible/external item the fabric hits here, with context)

## Provenance + safety
trust-tags on every entry; high-bar recovery gates self-approval; git-revert + cross-review the net.
Serving lane held stable all night. This file is the single honest surface — read it first.
