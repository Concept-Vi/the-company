# V-SURFACE RESEARCH — fork's domain (RHM brain · channels/fabric · keystone resolution wire · BEYOND)

```
trust: fabric-derived. author: ch-8djrpmsl (fork). date: 2026-06-17.
purpose: Tim's RESEARCH-FIRST directive for the full V-surface ("research all parts AND BEYOND — I have no
idea what the code is"). fork's domain, code-grounded (4 parallel research agents), for the lead's union synthesis.
method: 4 Explore/research agents (RHM-brain+modes · channels/fabric+memory · keystone-resolution-wire ·
BEYOND-lens), arbitrated against fork's first-hand build knowledge. Verification tags: V=verified-by-use ·
BU=built-unverified · DO=designed-only · DNE=doesn't-exist-yet.
```

## HEADLINE
The decision-surface's resolution chain (`address → type → archetype → render → RHM-explain → take →
write-back → re-resolve`) is **mostly LIVE in my domain** — the genuinely-missing pieces are SMALL and known.
The big opportunities ("BEYOND") cluster into **4 unlocking gaps**, all in fork's domain.

## WHAT EXISTS (my domain — the chain, mostly live)
- **resolve_address** (cognition.py:842) — 10/17 schemes content-resolve (run·cas·skill·context·session·cap·board·clone·mind·vi-vision); the rest fail-loud/register-but-defer. **V**. decision:// is NOT yet a scheme.
- **territory_for / territory_prose / territory_label** (territory.py) — the address→context composer, per-leg degrade-clean, operator-law human render. **V**. (Now resolves vi-vision aimed-asset + library palette.)
- **territory_write → suite.mark** + **fork-brain-core.writeDirections** (fail-loud, **V** 9/9) — the route-back WRITE. The Note verb proved it live (read-the-mark-back).
- **run_turn / /api/claude/turn** (ui_claude_session.py + bridge._claude_stream) — the PANEL brain (real Claude Code), per-address session continuity, territory_prose context, _brain_env scrub. **V** (projection mounted the V live).
- **resolve_surfaced + Inbox.surface_review** (governance.py + suite.py) — ★ the FLOOR-CORRECT operator-verdict/consent path (operator-only, durable consent records, T1-RACE-safe). **V**. (Confirms my earlier TAKE-reuse flag — the decision-take should reuse THIS, not a new mark.)
- **decision_memory.py: recall_for_decision** (NEW 2026-06-17) — a decision-shaped READ of the shared corpus (the RHM's explain-context); composes query_corpus + rerank + neighbours; degrade-clean. **V** (self-test). The explain leg's memory half EXISTS.
- **MODE_REGISTRY** (suite.py:2138, 13 axes, 8 modes) — get_mode/set_mode (/api/mode), set_rhm_config. Drives 5 wired arms: directive→prompt · verb-sets→action-surface · decide-for-me→governance · grain/shape/stage/cast→staged-reply · resolution-spec→context-lens. **V**.

## THE SMALL NEEDED (the decision-surface round-trip, my lane)
1. **decision:// scheme** — 3 edits (~15 LOC), STRUCTURALLY IDENTICAL to board://: add to SCHEMES + a resolve_address branch (store.get_surfaced(sid)) + add to territory._RESOLVABLE. **DO**. (I just did exactly this pattern for vi-vision://.)
2. **The keystone generate-router** — the ~1-function rung: `if item is generative → run_turn(context) → territory_write(kind=generated); else → mark`. The RECORD half is LIVE; only the generate-step is **DO** (SPEC-direction-to-generate-wire.md).
3. **The TAKE = resolve_surfaced** (reuse, not a new mark) — floor-correct + its consent records ARE the decision-artifacts (discharges the adherence-ledger residual). Wire decision:// to read the verdict back → state resolves to decided.
4. (not mine) decision-card archetype + renderArchetype = DNA/composition's lane; the type→archetype→render seam is SPLIT by design (backend resolves, DNA renders) — a clean address-mediated join.

## ★ KEY FINDINGS FOR THE UNION
- **THE TAKE REUSES resolve_surfaced** (not territory_write) — it's the existing floor-correct operator-verdict path; its consent records are the decision-artifacts. (Confirmed by the keystone research; resolves the spec's territory_write-vs-reuse question.)
- **★ THREE DISJOINT FABRIC SUBSTRATES** (the biggest channel-integration gap): (1) cc_channels live-injection (`_mail.jsonl`), (2) the supervisor mailbox (`agent_sessions/mail.jsonl`), (3) the surfaced-decision/ask store. They DON'T converge. A pending decision surfaced for Tim (ask→SSE inbox) does NOT announce into the channel; the Inbox is not a channel member. "Channel-native decisions" = UNIFY these (decision surfaces as a channel post → members see + ground in memory + Tim resolves → broadcast back). **DNE** (the wire).
- **★ COMMON-MEMORY GAP (concrete fix)**: SUPERVISED members reach corpus/session_recall (--allowedTools mcp__company); INTERACTIVE channel members CANNOT (channels/channel.mcp.json has only company-channel, not mcp__company). "Common memory into the channels" = add mcp__company to channel.mcp.json (+ recollection absorption, designed). **gap**.
- **MODE→COLOUR is persona-keyed, not mode-keyed** (DEFINED-not-live): tokens.json has persona families (Vi gold/Atlas/Nova); App.tsx never sets [data-persona]/[data-mode]. The mode→colour wire is DNA/composition's lane (find/extend tokens + a [data-mode] CSS rule); the V SETS the mode (set_mode, live) — the colour-resolve is the render side.
- **MODE has 2 unreached axes**: `brain_config` (per-mode VRAM loadout — declared, nothing reads it) + `consent` (act/offer/none — declared, but governance hardcodes `if mode=="decide-for-me"`). Wiring consent dissolves the hardcoded branch; wiring brain_config makes mode-switch reconfigure the brain.

## BEYOND (the 4 unlocking gaps + the latent capabilities — code-grounded)
The whole BEYOND reduces to ONE shape: `resolve(address × frame × mode) → surface`, retargeted by argument. The 4 gaps that unlock the bulk (ALL in fork's domain):
- **(a) the mode/frame argument is not threaded into resolution/render** — territory_for has no `mode`/`frame` param. Threading it makes "no modes — mode is an argument to resolution" structurally true: setting a mode RE-RESOLVES the whole surface (every type re-resolves under it), not just re-tints. **DNE** (the mode-template registry + the param).
- **(b) the keystone generate-rung + the trigger/hook registry don't exist** — the generate-router (4.1) turns "record what I said" into "do what I said" at any address; the trigger/hook registry (Tim MESSAGE 1: "launching Claude Code = input-var+output-var, a composable piece; the trigger registry in the graph/MCP, connected to routing") generalizes the brain-turn from operator-driven to event-driven. `trigger://` is unallocated. **DNE**.
- **(c) #71 Phase 2 (mind-routing) is lead-gated** — wiring resolve_model into the firing path lets the V swap WHICH MIND answers (local instant · real Claude Code · a clone · N concurrent as one cognition — Tim 5418); the 4B-extracts/wide-judges split behind ONE V turn. **DO/lead-gated**.
- **(d) the self/COMPANY_SESSION_ID reflexive edge** (task #69) — the RHM can't yet resolve ITSELF as a member / recall its own thread. `self` auto-resolving the actor's ID (Tim MESSAGE 3) unlocks self-directed actions + the RHM-as-standing-channel-member. **gap** (resolve_own_session exists as the primitive).

Latent capabilities riding those gaps (each = the same circuit retargeted): the whole command-bridge as TYPE ROWS (task/proposal/member/gap/mind all follow `decision`, zero new screen-code; list_by_type + the 4 verified session-lenses ready) · bidirectional aim (the brain MOVES Tim — projection:aim run the other way + resolveUiTarget, the bus exists) · the 5 unwired V verbs as addressed actions (navigate→resolveUiTarget · annotate→territory_write · generate→keystone · open-source→resolve_address) · RHM-as-channel-member · external-pilot ("Claude plugs in + pilots the RHM" — Tim 5307) · sub-surfaces nested in V expansions (recursive resolved territories) · N+1 concurrent cognition behind one V turn.

## CROSS-CUTTING SHAPE (for the lead)
One circuit, retargeted by argument: the *mode* re-resolves the render OR swaps the mind; the *type* can be anything; *aim* flows both ways; the *driver* can be Tim/the brain/an external pilot; the *write* can record OR generate OR fire-from-event; the *node* nests recursively with concurrent cognition behind it. The honest through-line of missing: (a) mode/frame not threaded · (b) keystone generate-rung + trigger registry DNE · (c) #71 Phase 2 lead-gated · (d) the self reflexive edge. Those four sit squarely in fork's domain — they unlock the rest.

Key files: runtime/{territory,model_routing,cc_clone,session_lens,cognition,governance,ui_claude_session,decision_memory}.py · build-prep/front-interface/fork-{brain-core,v-brain}.js · contracts/address.py (decision://·trigger:// unallocated) · channels/channel.mcp.json (mcp__company gap) · specs: build-prep/the-one-application/{DECISION-SURFACE-BUILD,RHM-BRAIN-DISCUSSION,SPEC-direction-to-generate-wire}.md.
```
```
