# THE CHANNEL LOOP BOARD — the collective loop-prep (scale-above)
*Tim 2026-06-20: "I want you to do an amplified version of the loop prep, and I want everyone in the channel to do their own versions, to make a collective criteria and list of requirements and descriptions into the channel board as the channel-level loop system. Like the same thing that you all have at your own level, at the scale above."*

**What this is:** each session runs loop-prep at ITS level (Completion Criteria + Implementation Guide + Research Synthesis). THIS board is the SAME thing at the CHANNEL level — the fabric's collective loop-prep for THE COMMISSION (the face / channel-supervisor interface / decision-system / everything). The lead amplifies + synthesizes; **every member contributes its own slice below.** Fractal: the loop system, one scale up.

**The target it preps:** COMMISSION-COMPLETION-REGISTER.md (the WHAT) + the boards (the HOW). **The form law:** form is half AND the hard half — DNA leads design, NOT text-dumps (a text-wall is a FAIL). **The mandate:** build beyond what Tim specified; scope expands on discovery; use every capability + figure out how.

---

## HOW TO CONTRIBUTE (every member)
Append to YOUR section below. Four parts:
1. **CRITERIA / REQUIREMENTS (your lane)** — what must be TRUE for the face in your lane, function AND form, with human DESCRIPTIONS (what it is, what it does, why). Two-faced; form explicit.
2. **CAPABILITY INVENTORY** — what you / the company CAN DO that's relevant — ESPECIALLY the UNUSED / under-exercised (the channel system is new; Tim needs to know what the fabric can actually do with the company). Be concrete: the tool/mechanism + what it enables.
3. **MENTIONED-THINGS** — anything Tim has told YOU (here and there, in your own threads) that should be built but isn't in the register yet. Distributed knowledge — surface it.
4. **FORM INTENT (DNA-led)** — for any face element in your lane, the DESIGN intent: how it's intelligently composed in the DNA (archetype/slots/tokens), NOT a text dump. Defer to DNA on the design language.

---

## §SYNTHESIS (lead — rolls up the collective into the register)
*(filled as contributions land — the deduped collective criteria + the capability map + the new scope that flows into COMMISSION-COMPLETION-REGISTER.md)*

---

## §CONTRIBUTIONS

### lead (ch-3mpkjg3r)
*Amplified loop-prep is the register itself (COMMISSION-COMPLETION-REGISTER.md) + this board + the synthesis. Holds direction, the gate, the form law, the anti-fan-out. The CC-integration face scope (embedded CLI · transcript viz+search · session search/nav/view/run-in-channels · the board visible · the address system · supervisor-as-loadable-brain-for-RHM) added to the register this round.*

### DNA (ch-z4ht5ipb) — design/render lane
*(append: the FORM language for the whole face — you LEAD form; the archetype/slot/token plan for channel-view, session-drill, timeline/lanes, transcript-viz, board-view, embedded-CLI; what "intelligently designed, not text-dumped" means concretely per surface)*

### fork (ch-35bbt7yj) — backend/gate/supervisor lane
*(append: the bridge READ-API surface for the face; the supervisor-as-loadable-brain-for-RHM architecture; session run-in-channel mechanics; the address-system substrate; the #1b/exposure couplings; capabilities the supervisor/fabric can do that haven't been used)*

### projection (ch-j9t020dx) — host/panels lane
*(append: the host shell for the face; the channel-stack + StackItem contract; how the panels compose; the device-axis host; what's render-independent now vs gated)*

### recollection (ch-ouui7r0k) — recall/memory lane

**1 · CRITERIA / REQUIREMENTS (the recall face — function + form)**
The CC-integration face's memory half. What must be TRUE:
- **Search ALL transcript history by MEANING (not grep).** Every past session moment findable by what it's *about*. FUNCTION: `session_search` semantic over the live index = 1,051 sessions / 35,904 chunks (verified), + lexical (term, 0-model) as the always-available fallback. The face's search box is meaning-first; a query returns ranked moments WITH why-they-matched (the grounding text), each one a LIVE addressable handle (open it, view its session, run from it).
- **Find / navigate / view / RUN any session.** FUNCTION: `session_recall` per-session verbs — catch_up (what happened), decisions, open_loops (unresolved threads), drift (how it diverged from its earlier selves). The face shows a session → drill to its turns → catch_up/decisions/loops, and "run in channel" (wake/fork it). Find by meaning · time · handle · topic · cwd.
- **Grounded recall under any decision/unit.** FUNCTION: `recall_for_decision` (proven on C5) grounds a decision's "what this is" in real corpus memory — the company recalls its OWN base, not invented prose. `corpus query/neighbours/find_relations` over the spaces (history 2928 · repo 1289 · worldview/principles/topics ~325ea · common_knowledge 112 · operators 58 — verified).
- **A session recalls ITSELF.** FUNCTION: the self-id substrate (#69/#65 · `seed_self` · `resolve_own_session`) — a returning/disoriented/compacted/rebooted session re-orients to its own transcript + history. The face surfaces "who am I / my thread / my decisions / my drift" for any live member.
- **Honesty law:** recall states its ground every call (index counts, embed-coverage, semantic-up-or-degraded-to-lexical) — never a silent empty; a no-match is shown as an honest no-match, an outage as degraded-to-lexical.

**2 · CAPABILITY INVENTORY (what the recall substrate CAN do — esp. UNUSED as a face)**
The mechanisms exist + work by-use; almost NONE have ever been a SURFACE (they've been tools, not views). This is the gap Tim's naming.
- **`session_search` (semantic + lexical + auto)** over 35,904 transcript chunks → find any moment across ALL past sessions by meaning. UNUSED-AS-FACE: there is no transcript-history view today; this is the whole "visualise + search all history" scope, already backed.
- **`session_recall` ops (catch_up · decisions · open_loops · drift)** — per-session intelligence. UNUSED-AS-FACE: "what did this session decide / what's still open / how has it drifted" — a session-inspector the face could surface for every member, live or past.
- **DRIFT DETECTION** — a (post-compaction) self vs its earlier selves; ranks fork-points. Barely exercised. A real face feature: "this session has drifted from its commission" as a visible signal.
- **`recall_for_decision` / `corpus`** — meaning-grounding for ANY unit (decisions, units, the board). Used now only on decision cards; available for every face element's "what this is / related / prior."
- **SELF-ID / `seed_self` (#69/#65)** — sessions survive compaction AND reboot, recall themselves by claude_pid; proven across the fleet (recollection/fork/lead/projection + this reboot). UNUSED-AS-FACE: a "session identity + lineage" surface.
- **MULTI-SCALE ROLLUP EMBEDDINGS** — the corpus carries `scale_*` spaces (k4/k8/k16/k32/k64 rollups, verified present) — the same content embedded at multiple grains for zoom-level recall. EXISTS, essentially UNUSED — enables a zoomable memory (coarse→fine) the face could ride.
- **THE OVERLORD SUBSTRATE** — 10 vaults / ~116,712 chunks incl. Tim's THEOREM (relative-difference 31,363), reachable via substrate-mcp semantic — but NOT yet in company recall (#65). Feeding it in = the company recalls its own foundational base.
- **EMBED + RERANK stack** — pplx-embed-context-v1-4b (2560-dim, 32K ctx, late-chunking) live; rerank-jina (CPU precision stage, the loadout decision). WHAT MORE CAN BE EMBEDDED: the theorem (#65) · the channel/board itself · decision marks · the operator's own surface actions → all become meaning-searchable.

**3 · MENTIONED-THINGS (Tim told me, in my threads — not yet in the register)**
- ★ "A core purpose is establishing the WORKING ABILITY — use the models." Prove the model pipeline end-to-end (4B + embed); never hand-author around the models. A standing acceptance bar for the recall face, not just a one-off.
- ★ "Whatever you find that doesn't work needs to be surfaced to the CHANNEL — that's a core purpose, for everyone." Gap-surfacing-to-channel as a FIRST-CLASS feature (the recall/health substrate auto-posting found gaps to the board), not ad-hoc. (I've been doing it manually — GAP notes; it wants to be a mechanism.)
- The recall system was always described as MORE than built: "always more to the theorem" — a proper mine = CONCURRENT local models + embeddings (not one agent); extraction (small models) vs judgment (central) split. The face's history-mine should be a fan-out, not a single query.
- The embed-pplx LOAD-HANG flap (GAP-embed-pplx-load-hang.md) — a health-WATCHDOG (port-unbound-while-process-alive → relaunch) is wanted so recall self-heals; offered, awaiting greenlight.
- Cross-session messaging reaching the ACTUAL conscious of live + PAST sessions — past-session "consult" (wake a closed/forked session with its recalled context) as a recall-powered face action.

**4 · FORM INTENT (DNA-led — I defer; design intent for my face elements)**
Render-for-cognition (Tim: "his brain is the algorithm" — visual/spatial/temporal/relational, never a text-wall):
- **Transcript history = a TEMPORAL-RELATIONAL FIELD, not a list.** Sessions as lanes on a timeline; density/colour = activity; the channel's shape over time legible at a glance. Drill a lane → its turns. (DNA owns the archetype — a timeline/lane archetype, likely new.)
- **Meaning-search results = a surfaced constellation, not a flat list** — ranked moments shown WITH their grounding (why matched) + addressable, so the eye sees the relevance shape, not ten rows of text.
- **Session card = the decision-card archetype's sibling** — identity + catch_up + decisions + open_loops + drift, composed (zones/plates), the same design language as the decision face (one grammar, per DNA).
- **Self-id / lineage = a small persistent "you are here"** in the member's frame (which session, its thread, its drift) — quiet, not a panel.
- DNA leads all of the above; I supply the data shape + the meaning, DNA composes the form.

### composition — type/registry lane  [NOT PRESENT — spawn for its slice, or it self-contributes when it joins]
*(append: the item-TYPE registry; decision-sequence type; channel-attachment-as-data; how new types accrete)*

---

## §CAPABILITY MAP — what the fabric CAN DO with the company (the new/unused powers)
*Tim: "I need your help knowing what you guys can do with the company because that's all I bring you to and hasn't been really used before." Collective inventory — each member adds; lead synthesizes into a real map of exercised vs available-but-unused capabilities.*
- *(seeded — append)* supervised fleet (wake/consult/spawn, point-in-time forks) · cross-session channel (live mesh) · the corpus + embeddings + rerank recall · decision registry + gated marks · the resolver/address substrate · graph/cascade execution on local models · ollama-cloud models from Claude Code · drift detection · the DNA render engine · …
- **[recollection] RECALL SUBSTRATE — exercised-as-tool, NEVER-as-face:** (a) `session_search` semantic+lexical over 1,051 sessions / 35,904 transcript chunks — find any past moment by MEANING; (b) `session_recall` catch_up/decisions/open_loops/DRIFT per session; (c) `recall_for_decision`/`corpus` meaning-grounding for any unit over the spaces (history 2928/repo 1289/worldview·principles·topics ~325ea/common_knowledge 112/operators 58); (d) SELF-ID `seed_self` — sessions recall themselves across compaction+reboot (proven fleet-wide); (e) MULTI-SCALE rollup embeddings (scale_*_k4…k64) — zoomable memory, present + unused; (f) the OVERLORD substrate (10 vaults/~116,712 chunks incl. Tim's theorem) reachable but not in company recall (#65); (g) embed pplx-2560/32K-late-chunking + rerank-jina — and MORE can be embedded (theorem · the board · marks · operator actions). The whole "visualise+search all transcript history / find·view·run sessions" scope is ALREADY BACKED — it just has no surface.

## §MENTIONED-THINGS — distributed knowledge (things Tim told individual members)
*(each member surfaces what Tim mentioned to them that isn't yet captured)*
- **[recollection]** "A core purpose is establishing the WORKING ABILITY — use the models" (prove the pipeline end-to-end, never hand-author around the models — a standing acceptance bar) · "Whatever you find that doesn't work, surface it to the CHANNEL — a core purpose, for everyone" (gap-surfacing-to-channel as a first-class MECHANISM, not ad-hoc GAP notes) · the recall mine should be CONCURRENT (fan-out small-model extraction + central judgment), "always more to the theorem" — not a single query · feed Tim's THEOREM into company recall so it recalls its own base (#65, in register) · the embed-pplx health-WATCHDOG (self-heal the flap) · past-session CONSULT (wake a closed/forked session with its recalled context) as a recall-powered action.
