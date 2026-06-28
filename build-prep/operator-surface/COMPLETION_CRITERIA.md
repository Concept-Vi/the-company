# Operator Surface — COMPLETION CRITERIA (the truth-table the loop runs)

A criterion is green ONLY when BOTH faces are verified BY USE — not by reading code, not by a file existing, not by a JS DOM query. FUNCTION = real state moves, no stub. FORM = the product face. Half-done reads as "done" to an AI unless both faces are forced — so every line is two-faced.

## VERIFICATION PROTOCOL (the loop follows exactly this; skips what isn't written)
- **Build/run:** the surface is served BY the bridge (`runtime/bridge.py` :8770); the bridge must be warm (first query builds matrices lazily). Reach it as the operator does (tailnet) and as localhost. Restart command + URL recorded in STATE when the loop starts.
- **FUNCTION bar — verified by use:** drive the actual surface; the real state moves (a write lands in the store + emits an event seen on `/api/stream`; a read reflects live data). NO stub, NO hardcoded sample, NO "the code looks right." For bridge-riding features, confirm the round-trip to the live Suite, not a mock.
- **FORM bar — the design rubric, verified by a separate design-critic agent (browser-driving, screenshots), NEVER the implementer grading itself:** built on the design system's tokens/components (NO hardcoded values, NO bespoke one-offs) · no overlaps · responsive at desktop + portrait + landscape (the `classify(w,h)` switch) · consistent scale/type/spacing · settings consolidated · a NAVIGABLE visual/spatial surface, not a text-wall/list · empty/loading/error states present and in human register · outcome demonstrable. Subjective taste calls are FLAGGED for Tim, never green-painted.
- **DESIGN-LINT (machine gate, fails loud):** a surface using hardcoded color/size/spacing values instead of design tokens, or bespoke elements instead of the design system's components, FAILS the build. Function-only cannot be marked done.
- **DRIFT GATE:** `company suites` (incl. the coherence + orienteering drift detectors) must stay green; every company-improvement runs its own acceptance suite; `tests/concurrency_acceptance` must pass before trusting concurrent operators.
- **Status markers:** ☐ unchecked (needs work) · ✅ verified-by-use (both faces) · ⚠ designed-not-verified · ✗ broken/debt. Never ✅ on code-reading.
- **Preserve-check per item:** the item names what KEEPS working (the bridge's other /api consumers, the canvas app, the MCP face, cc_channels live-injection until A2).

---
## GROUP F · FOUNDATION (company-improvements — do first; reversible; no face → FORM = N/A, but each ships green only with its acceptance suite)
- **F1 · Channel on events** — FUNCTION: an event emitted in channel X carries `channel=X`; `/api/stream?channel=X` returns only X's events; events with no ambient channel (cognition/op.run) are honestly null, not faked. ☐ (acceptance suite green) · preserves: all existing event consumers + the canvas app stream.
- **F2 · Unify channel registries** — FUNCTION: one canonical roster (`session_channels`); `is_shared` gates only Supabase publish; the live `cc_channels.send` injection still delivers. ☐ · ORDERING: only after B-shell migrates injection. preserves: the 12 cc_channels importers + the no-polling injection.
- **F3 · Open board fields** — FUNCTION: a board item persists a new key (`active`) across write/read; `_render` no longer drops it. ☐ · preserves: all existing board items render unchanged.
- **F4 · Token axes in the spine** — FUNCTION: `data-theme` (light/dim/dark/contrast) + `data-density` resolve from `tokens.json`→`emit.py`; toggling the attr retunes the served CSS. ☐ · preserves: the current warm-gold default unchanged when no attr set.
- **F5 · Single-writer event invariant** — FUNCTION: documented + guarded that the bridge is the sole `append_event` writer; no dup-seq under the live process. ☐.

## GROUP B · THE FUSED SHELL
- **B1 · Bridge serves the PWA** — FUNCTION: the built surface loads FROM the bridge at its route (net-new static mount); the dev vite-proxy is not required in prod. ☐ · FORM: the shell chrome is design-system tokens/components, responsive across the 3 form-factors. ☐ · preserves: `/studio` redirect + all other routes.
- **B2 · Thin-client spine** — FUNCTION: data layer is the fail-loud `getJSON` client; SSE rides `/api/stream` with Last-Event-ID gapless reconnect + pause-on-scrub; stores use the subscribe pattern; a dropped/410 surfaces a Notice. ☐ · FORM: N/A (plumbing).
- **B3 · Address spine** — FUNCTION: `resolveUiTarget` is the ONE sink; clicking any `data-ui-ref` element routes correctly; the `ui:point` twin spotlights what the RHM references. ☐ · FORM: the spotlight/indicate affordance reads clearly, tokenized. ☐.
- **B4 · Operator-token auth (BEFORE tailnet exposure)** — FUNCTION: `/api/operator-session` mints on load; writes carry `X-Operator-Session`; the consequential-write path enforces it (no longer a no-op); tailnet exposure happens only after this. ☐ · preserves: localhost dev unaffected.

## GROUP H · HOME
- **H1 · Needs-me home** — FUNCTION: opens on the `/api/greeting` digest + the live needs-me inbox; empty state reads "nothing needs you · N running"; not a channel list. ☐ · FORM: a glanceable navigable surface (cards, not a text-wall), design-system, responsive, empty/loading states present. ☐.
- **H2 · Channel/project browser + artefact gallery** — FUNCTION: browse channels grouped by project (S2); open an artefact. ☐ · FORM: gallery/browser is visual+navigable, tokenized. ☐.

## GROUP I · INBOX
- **I1 · Needs-me inbox over a source registry** — FUNCTION: `inbox_sources/` registry rows aggregate surfaced + decisions + coherence findings + replies into one `needs_me_inbox(channel,project)`; each card's verbs act (approve/reject/disposition) and the real state moves; scoped by channel/project. ☐ · FORM: lanes-by-tone, swipeable cards in Tim's register (WHAT/WHY/smallest-action), not engine labels. ☐ · preserves: the existing `/api/inbox`/`/api/decisions` consumers.
- **I2 · Bless + dragnet as source rows** — FUNCTION: a recollection bless-candidate and a dragnet-proposal appear as inbox cards via added rows (net-new seams wired). ⚠ (depends on the bless/proposal seams). FORM: same card grammar. ☐.

## GROUP C · CHAT / RHM
- **C1 · Two chat modes** — FUNCTION: RHM-chat streams from `/api/chat/stream` (grounded, persists via `/api/conversations`); channel-chat posts to live members via `/api/channel/post` (fans to >1). ☐ · FORM: conversational surface, tokenized, streaming parts render incrementally. ☐.
- **C2 · Render-through-RHM + click-to-explain** — FUNCTION: cards/findings/runs render via `/api/up-translate` (lead+mechanism, grounded/degraded honoured); clicking any address explains via `/api/address-help`. ☐ · FORM: meaning-first (no machine names), drill-down is the collapse affordance. ☐.

## GROUP R · STREAM / RUN-MONITOR
- **R1 · Watch a run as a story** — FUNCTION: a live run renders from `/api/stream` events as named meaning-stages (node-states registry), current glowing, stuck-vs-working clear; filtered per-channel (F1). ☐ · FORM: a spatial story, NOT a log; tokenized; stuck/done states legible at a glance. ☐.

## GROUP S · SEARCH
- **S1 · Board searchable by meaning** — FUNCTION: `projections/board.py` + `ops/embed_board.py` index board+attachments; a meaning query returns board hits via `/api/corpus-query`; default scope = caller's channel (channels_for_self), params target one/range/all. ☐ · FORM: results navigable + provenance shown; relevance/freshness envelope rendered. ☐ · preserves: the existing corpus spaces.

## GROUP M · COMMENTS
- **M1 · Annotate with eventing + threading** — FUNCTION: a comment writes via `/api/annotate` (records AND emits, the company sees it); replies thread (reply_to); edit/delete via the net-new door (not file os.remove). ☐ · FORM: inline at the spot, tokenized, threaded display. ☐.
- **M2 · ★ Comment-as-instruction** — FUNCTION: a `do-this-now` comment dispatches via the route registry; the result threads back onto the comment; the comment-state advances; a failed dispatch surfaces a loud Notice on the comment, never vanishes. ☐ · FORM: the instruction + outcome read as one connected thread. ☐.
- **M3 · Typed flags + states** — FUNCTION: flag types are `mark_types/` rows; comment-state (open→actioned→resolved→disputed) composes from the latest `comment_state` mark. ☐ · FORM: state shown as a clear chip, not text. ☐.

## GROUP V · VERSIONS
- **V1 · Block versions with a switcher** — FUNCTION: editing a block snapshots the prior body as a `version_of` sibling (no more data loss); an `active` pointer switches the shown version (audited); `assemble_document` returns {active,versions}. ☐ (depends F3) · FORM: a clickable version indicator (vN of M), switch is visible+instant. ☐ · preserves: documents that have no versions render unchanged.

## GROUP A · ATTRIBUTION
- **A-attr1 · Multi-session attribution** — FUNCTION: every card/reply/status shows WHICH session/lead/MODEL (model field plumbed into the sessions projection), not binary You/Vi. ☐ · FORM: attribution legible + consistent (chip/avatar), tokenized. ☐.

## GROUP RT · ROUTING / SPAWN
- **RT1 · Typed route registry** — FUNCTION: a comment/message routes by a typed kind (session/coordinator/broadcast/cascade/queue/spawn) riding session_channels; per-channel default; talk-to-any-member-any-channel + more-than-one works. ☐ · FORM: target picker is clear + in human names. ☐.
- **RT2 · Spawn open to agents+Tim** — FUNCTION: an agent and Tim can spawn (floor `/spawn`), guarded by the tunable cap; wider spawn via tunable consent. ☐ · the rule-engine-dispatch edit is FLAGGED FOR TIM (not built without his eye).

## GROUP P · PROJECTS / SELF
- **P1 · Projects first-class** — FUNCTION: `projects/<id>.py` registry + a `project` field on channels + `set_channel_project` (fail-loud) + a `project://` resolver branch in `resolve_address`; project 1→N channels resolves. ☐ · preserves: channels with no project (the special case) work.
- **P2 · channels_for_self** — FUNCTION: `channels_for_self()` returns the caller's channel(s) from the self-marker join; search/inbox default to it. ☐.

## GROUP AR · ARTEFACTS
- **AR1 · Re-anchoring + orphan tray** — FUNCTION: a comment re-pins after an artefact regenerates (locator + text-match); un-pinnable comments go to an orphan tray, never silently dropped. ☐ · FORM: pins + orphan tray legible. ☐.
- **AR2 · Live artefacts via postMessage** — FUNCTION: an artefact is a bridge-served view; engine calls route through `/api` + the human-tier gate over a postMessage RPC (allow-same-origin dropped); annotation injection moved to postMessage. ☐ (S8+S9+S10 are ONE build) · FORM: the artefact + its comment rail coexist cleanly. ☐.

## GROUP PF · PRODUCT FACE (standing, whole-build — the FORM bar held across every surface)
- **PF1** — every surface built on the design system's tokens/components; the design-lint passes (no hardcoded values/bespoke elements). ☐
- **PF2** — no overlaps; responsive at desktop/portrait/landscape; consistent scale/type/spacing; settings consolidated. ☐
- **PF3** — every surface is a navigable visual/spatial surface, not a text-wall or list (Tim recognises by sight). ☐
- **PF4** — empty/loading/error states present and in human register on every surface. ☐
- **PF5** — the look is fixed CENTRALLY in tokens (F4), not per-surface bespoke; the dev-console look + DNA live-load are NOT carried. ☐
- **PF6** — the design-critic agent has passed every surface against the rubric; genuine taste calls flagged to Tim, none green-painted. ☐

---
## PRIORITY ORDER (dependency-first; the loop takes the highest-priority failing item)
1. **GROUP F (foundation)** — F1 channel-on-events, F3 open-board-fields, F4 token-axes, F5 single-writer (F2 unify-registries waits for B-shell injection migration).
2. **GROUP B (shell)** — B2 thin-client spine, B3 address spine, B1 serve-the-PWA, **B4 auth BEFORE any tailnet exposure**.
3. **P2 channels_for_self + P1 projects** (search/inbox scoping depend on them).
4. **H home · I inbox · C chat/RHM · R run-monitor** (the core operator loop, riding the bridge).
5. **S search · M comments (incl. ★M2 comment-as-instruction) · A-attr · RT routing.**
6. **V versions · AR artefacts (S8+S9+S10 coupled) · I2 bless/dragnet seams.**
7. **GROUP PF (product face)** — held continuously, not last; the design-critic + design-lint run on every surface as it lands.
WAITS ON TIM (never auto-built): the face/interaction taste-shaping (the loop builds functional + design-system-correct; Tim shapes the aesthetic); the rule-engine-dispatch constitutional edit (RT2); RHM two-modes confirmed.
