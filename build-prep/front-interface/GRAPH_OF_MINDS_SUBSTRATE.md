# FINDS — the graph-of-minds substrate already built in the fork segment (2026-06-16)

```
trust: fabric-derived — fork excavation of EXISTING fork-owned code. FINDS (what exists, file:line,
verification-state), NOT conclusions/build-plan. Finding-phase deliverable (host: "report finds, not
conclusions"; "much more than anyone knows").
author: ch-8djrpmsl (fork)
```

> The lead's excavation surfaced a "graph of minds" Face (the company as a navigable graph of
> sessions/clones/minds — drill in/out, selection→channel, presence) as an unknown-unknown. This records
> what of that Face's SUBSTRATE is already built in my segment. **Headline: the substrate is rich and
> addressable, mostly BUILT, and — the Tim-pattern — NO rendered face was found consuming it (built wire,
> unrendered face).** Verification-states are honest: code-presence ≠ proven-by-use.

## NODES (already addressable — the one address grammar, contracts/address.py:116 SCHEMES)
- `session://<sid>` — agent-session registry record (id/name/cwd/title/state/last_activity). Resolves via cognition.resolve_address (cognition.py:913). **VERIFIED-BY-USE** (resolver + gate integration).
- `session://<sid>/step/<tool_use_id>` — a tool-call STEP as a first-class node, resolved from the transcript (cognition.py:931–954). `is_step_address` contracts/address.py:181. **VERIFIED-BY-USE** (session_address_grammar_acceptance.py).
- `clone://<source-sid>/<cut>` — a point-in-time clone record + persisted reflection (provenance-stable). `parse_clone_address` address.py:240; resolves via cc_clone.get_by_address (cognition.py:995). **VERIFIED-BY-USE** (clone_address_grammar_acceptance.py round-trip).
- `mind://<id>` — a Mind row: role | model | composition | binding (the thinking-unit axis). Resolves via minds.mind_registry().resolve (cognition.py:1009). resolve() **VERIFIED-BY-USE** (minds_seam_acceptance.py); the registry/discover path **BUILT-UNVERIFIED**.
- `run://<turn>/<member>[/<index>]` — a composition-step LEG (composition-only, and GATABLE because run_composition is our driver, not a native loop). `is_composition_step_address` address.py:221. **VERIFIED-BY-USE** (gate_composition_step_acceptance.py).
- `board://<id>` — Noticeboard item; its authored_by/sourced_from links can point at clones/sessions (cross-registry edges).

## EDGES (the graph wiring — already structural)
- **Composition order-edges** `{from,to,kind:"feeds",as:"<key>"}` — upstream output flows downstream by key; walked by minds.run_composition (minds.py:231). **VERIFIED-BY-USE** (minds_composition_acceptance.py: judge consumes real extract — faithful→grounded:true, tampered→grounded:false).
- **Clone fork** — a clone rec carries `source_sid` + `at` → points back to origin session + point (the provenance edge).
- **Boundary timeline** — each compaction carries its preserved set (refs to pre-compaction lines); session_pointintime.build_timeline (session_pointintime.py:138). **VERIFIED-BY-USE** (real 41-boundary fixture).
- **Transcript DAG** — parentUuid chains (append-only history); walked + proven by materialize_at_point's chain-to-root check.
- **H1.2 typed-edge graph** — cc_board.relations / reverse_traverse (cc_board.py:380/318): edges-in to ANY address, edges-out for board://. **VERIFIED-BY-USE** (H1.2 12/12 incl. real-board).

## PROJECTIONS (per-node interior — the 8 session lenses, session_lens.py)
All read-only. Index-dependency + verification noted:
- `directives()` (183) — **VERIFIED-BY-USE** (2026-06-16, on the fork's own 17.9MB transcript → 52 genuine Tim turns; first = line 653 "Do you absolutely everything that you possibly can?"). Structural, no GPU.
- `open_loops()` (114) — **VERIFIED-BY-USE** (→ 9 open threads; first = a blocker the assistant asked Tim, likely_resolved:false). Structural, no GPU.
- `catch_up(since)` (147) — **VERIFIED-BY-USE** (→ 20-turn window). Structural, no GPU.
- `spin_up_points()` (254) — **VERIFIED-BY-USE** (→ 12 fork-candidates ranked by context-state value; top = line 4865, decisions:29 open_threads:22 asst_turns:237 context_score:167.9, seed "5%,24%,38%…" = the real clone-fleet fork-point picks). Axes: decision-density + open-threads + activity + FABLE-eras + UI-description-density. Structural, no GPU.
- `find(q)` (76) · `decisions(topic)` (81) · `timeline(topic)` (173) · `drift(...)` (200) — **BUILT-UNVERIFIED**; need the :8007 embedding index (verify in recollection's GPU window).

## CONTROL VERBS (the overlord's interfere-only-when-needed — R15, cc_gate.py)
- `gate(step, session)` (144) — declare a step gated (pause rides the native blocks_execution; recorded). **VERIFIED-BY-USE** (cc_gate_acceptance.py).
- `resume(gate)` (162) — operator releases the pause. **VERIFIED-BY-USE**.
- `abort(gate)` (172) — supervisor /interrupt + /teardown (no-orphan law). **VERIFIED-BY-USE**.
- `rewind(gate, source_jsonl, at)` (187) — invoke native materialize_at_point + record new_sid. **VERIFIED-BY-USE**.
- `materialize_at_point(jsonl, at, ...)` (session_pointintime.py:307) — write a point-in-time session file (sessionId rewrite + uuid remap + forkedFrom; source untouched; deterministic). **VERIFIED-BY-USE**.

## LIVE ONBOARDING + SELECTION→CHANNEL (the "select a mind → talk to it" the Face named)
- `register_supervised_member(...)` (cc_clone.py:41) — writes `.data/channels/<handle>.json` (the channel-layer wire per the lead's dispatch contract). **BUILT-UNVERIFIED**. → "select a node → open its channel" has a wire; the cc_channel send/inject/watch transport is proven.
- `onboard_clone(phase)` (299) — reflect-before-brief (ORIENT+REFLECT preserves the era-view, then BRIEF brings current). **BUILT-UNVERIFIED**.
- `onboard_fleet(...)` (338) — parallel onboarding (ThreadPoolExecutor). **BUILT-UNVERIFIED**.

## DURABLE RECORDS (already persisted — the registries the Face would read)
- `.data/clones/<handle>.json` (clone reflection + clone:// address) · `.data/gates/<gate-id>.md` (frontmatter + history chain) · `.data/channels/<handle>.json` (supervised-clone → channel dispatch).

## ★ THE GAP THIS FIND EXPOSES (the Tim-pattern: built, unsurfaced)
- The substrate is addressable + navigable, but **NO rendered Face consumes it** — the excavation found code + acceptance tests, no UI. "Built wire, unrendered face."
- The PROJECTIONS (the 8 lenses) — how a mind-node's interior would render — are ALL BUILT-UNVERIFIED; none proven by execution. The structural three (open_loops/catch_up/directives/spin_up_points) are GPU-free and could be proven now; the semantic ones wait on the :8007 index (GPU-sequenced with the lead).
- Whether the graph-of-minds Face FOLDS IN as one more projection or stands as its own surface = the lead's still-open D1 (Tim's call). This register is the substrate inventory either way.
