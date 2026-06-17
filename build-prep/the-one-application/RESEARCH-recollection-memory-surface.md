# RESEARCH — common company memory INTO the channels + how it resolves under the surface (recollection's domain, from all sides + BEYOND)

*Tim 2026-06-17 (research-first, all sides + beyond): the full V-surface needs the common company memory wired into the channels + resolving under the surface. This is recollection's research contribution to the lead's assembled synthesis — code-grounded (3 read-only explorer waves + ancestral recall), honest-state, with the BEYOND lens. Don't-build-yet; this feeds design. State labels: LIVE · BUILT-BUT-ORPHANED · DESIGNED-UNBUILT · SPEC-ONLY.*

## ★ THE HEADLINE (the one finding that reframes the build)
**The memory substrate is BUILT and FED; the missing piece is ONE universal memory leg.** Because `territory_for` (the universal address→context composer) is ALREADY folded into EVERY brain turn (`bridge.py:1697`, `_claude_stream` → `run_turn(context_block=ctx)`), adding ONE memory leg to it turns EVERY resolved address — every rendered/selected thing on the surface — into something that AUTO-GROUNDS in recall. The orphaned compute already exists (`recall_for_decision`). So "memory under the surface" is not a big build — it's wiring one orphan into one universal leg. It generalizes far past decisions: it's memory under the whole V-surface.

## 1. THE MEMORY SUBSTRATE — BUILT + FED (the shared corpus is real)
| Layer | What | State | file:line |
|---|---|---|---|
| The corpus spaces | history (2928) · repo (1289) · topics/worldview/principles (~324 ea) · common_knowledge (112) · operators (58) + scale-cluster vecs (~500) = ~5,862 vectors | LIVE + populated | projections/*.py · store/vector_index.py:64 |
| query_corpus (text→top-k) | embeds query → ranks a space; loud honest-empty | LIVE | runtime/suite.py:10836 |
| neighbours (recall-under-a-unit) | the constellation around a unit; each drillable | LIVE + proven | corpus_neighbours.py:31 · /api/cognition/neighbours bridge.py:1494 |
| rerank (precision) | jina-v3 cross-encoder, :8008 CPU/0-VRAM, opt-in | LIVE | corpus_rerank.py:55 |
| find_relations (inversion) | near∩¬far cross-space ("same principle, diff subject") | LIVE | suite.py:10854 |
| recall_for_decision (decision→bundle) | multi-space pool → rerank → neighbours; the RHM's grounding | **BUILT-BUT-ORPHANED** (imported by nothing; its docstring claims a route that doesn't exist) | runtime/decision_memory.py:28 |
| capture_corpus / ingest (write+embed) | the ONE write seam, both faces call it | LIVE | suite.py:10575 / :10474 |
- ★ HONEST GAP: conversation-memory lives in THREE parallel stores (the corpus `history` space via g23_mine · per-session recall-index sidecars · out-of-repo substrate.db) with three embed paths — "ONE shared memory" is NOT yet true for session memory; unifying them is real work.

## 2. INTO THE CHANNELS — the seam is ABSENT (the real gap)
- Two live channel systems: `cc_channels.py` (file-based, the working `fabric` channel) + `session_channels.py` (store-event, channels/gatherings). Both carry live traffic.
- ★ THE SEAM IS ONE-DIRECTIONAL + NARROW: grep across all channel code finds ZERO calls to corpus/recall/embed/capture. Channels neither READ memory nor WRITE their exchange into it. The only built memory-read is the RHM's path (decision_memory, orphaned). The designed connector = **"the 5th wire: channel-scoped recall"** (channel-memory/mega-prep/CHANNEL-LAYER-SEAM.md) — DESIGNED-UNBUILT.
- GATED ON #69 (three sub-gaps, all PARTIAL): (A) COMPANY_SESSION_ID injection so `session=self` works in one call (blocked: editing ~/.claude.json is auto-denied self-mod; patch proposed); (B) member-session discovery (handle→uuid; poll-only peers don't auto-announce — confirmed by my R10: live sessions aren't recall-able until backfilled); (C) live/continuous capture (the exporter is batch every 20min, not streaming).
- ANCESTRAL INTENT (recall, Tim verbatim): "sometimes I'd pull it in as a one-off, sometimes make it a group or a CHANNEL THAT DOES PERSIST" — channels-as-persistent-memory was the design vision; the persist-half is the unbuilt capture-channel-into-memory.

## 3. HOW IT RESOLVES UNDER THE SURFACE — the resolution-first mechanism (the build path)
- The ONE resolver: `resolve_address` (cognition.py:842), 17 schemes, the documented add-a-scheme seam at **cognition.py:1029** (`if sch is not None: raise` → add a dispatch branch, exactly as skill/board/clone/mind/vi-vision graduated). `exchange://`/`file://`/`project://` are ALREADY REGISTERED + reserved as recollection's lane (register-but-defer).
- `territory_for` (territory.py:42) composes legs (identity · corpus_record · context · relations · library) → `territory_prose` (territory.py:170, NEVER-raises) → **folded into every brain turn (bridge.py:1697)**.
- ★ THE TWO INSERTION POINTS for memory (both real, both small):
  - **(A) `recall://` scheme** at cognition.py:1029 (recollection's lane) — an address resolves to its recall bundle. OR graduate the reserved `exchange://`.
  - **(B) a MEMORY LEG** on territory_for at territory.py:167 (fork's lane; I supply the compute) — calls recall_for_decision; per-leg guarded (degrade-clean); rendered in territory_prose beside "Details." This is the universal one (every address, every turn).
- The decision-surface's `explanation_source` resolving THROUGH this = the resolution-first expression I already proposed (recall:// leg → territory_prose → RHM explains grounded).

## 4. ★ BEYOND (past what Tim specified — grounded extrapolation)
- **Universal auto-grounding:** the memory leg sits BELOW the scheme switch → it composes for run://·board://·code://·ui://·mind://… uniformly. Every rendered thing on the V-surface arrives with its prior-discussion + neighbours + provenance, citeable. "Explanation resolves through recall, never stored" becomes the DEFAULT, not a decision-only feature.
- **The channel exchange BECOMES memory:** a capture-source sweeping channels.jsonl/mail.jsonl into the corpus (session_channels.py:20 literally calls these "the rows a future heart ingests") → "what did the fabric work out about X?" recallable by meaning. Closes the persist-half of Tim's ancestral vision.
- **Proactive memory pushed INTO channels (G8):** the channel transport rail (push/inject/fan) ALREADY exists; recollection's G8 proactive-injection layer is the trigger — relevant prior context injected when a topic recurs (the inverse of pull-recall). The rail is built; the trigger is the unbuilt layer (UNIFIED-SEAM.md).
- **Operator-memory as a per-address leg:** operator_memory.py:7 already stores rows pointing at the exchange:// moments that taught them → the memory leg could auto-ground any address in WHAT'S KNOWN ABOUT TIM (the GC14 injection, designed-unbuilt), not just the corpus.
- **Structural memory (recollection's crossings):** when exchange://file://project:// graduate at the same cognition.py:1029 seam, the memory leg traverses the crossings graph (what-touched-this-file, containment) — memory-context becomes STRUCTURAL, not just semantic. (Ties to the lead's ONE-substrate-engine: crossings = typed edges = an instance of it.)

## 5. THE SMALLEST PATH (research → design input; recollection's piece)
recall_for_decision is BUILT (the compute). The build = (1) fork adds the memory leg to territory_for (I draft) OR I add the recall:// scheme (my lane) — either makes memory a RESOLVED leg under every address; (2) for channels: the channel-scoped-recall 5th wire + the capture-channel-into-corpus source (gated on #69 self-resolution). The universal composer + the every-turn fold already exist — this is wiring, not new architecture. NOTHING bespoke; all registry+resolution.

*Files: runtime/{decision_memory,corpus_neighbours,corpus_rerank,territory,cognition,suite,session_recall,session_channels,cc_channels,bridge}.py · projections/*.py · channel-memory/mega-prep/{CHANNEL-LAYER-SEAM,UNIFIED-SEAM}.md · channel-memory/noticeboard/item-501c4188.md (#69). 3 explorer waves + ancestral recall, this session.*
