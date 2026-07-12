# C — Resolved-Context: the FULL direction capture (Tim's mandate: ALL of this is wanted)

> **Why this file exists (Tim, 2026-07-12, on record):** "everything that you have laid out in all of your
> messages since I asked in this direction, all of it is things I am super interested in… I want it on record
> that those messages and everything in them is stuff that I will want in the system, plus everything else we
> come up with" — captured HERE so it survives compaction/context-drift. This is the expansive record of the
> whole arc: the resolved-context idea → the mechanics (A) → the architecture (B) → the OUTPUT/FORM face →
> the MEMBER-REGISTRY face. Nothing here is decided-final; all of it is wanted-in-the-system. Siblings:
> RESOLVED-CONTEXT-A-mechanics.md (verified mechanics) · RESOLVED-CONTEXT-B-architecture.md (the design).

## 0 · The seed (Tim's words, decompressed)
Hooks on keyed messages in Claude Code; local AI judges/matchers classify them; structured-output tags fire
actions that replace/alter/manipulate the conversation history; custom, live-triggered context alteration;
"resolve context for the agent's turn as well as their active conversation history" — **dynamic context
management**. Context stops being ACCUMULATED (append + lossy black-box compaction — the failure we lived:
the "old version" resume) and becomes RESOLVED (computed per turn from a durable, addressed substrate by
judges + rules). Resolve-from-source applied to the agent's own working memory. Store = LOCAL Supabase.

## 1 · What A proved (see A-mechanics for detail)
- UserPromptSubmit stdout **INJECTS into the model's context — verified live** (the ZEBRA-77 experiment).
- SessionStart matcher:"compact" re-injects AFTER compaction = the depth-survival fix. PreCompact is observe-only.
- In-place .jsonl rewrite of live sessions is HARNESS-GUARDED ("Session Transcript Tampering") → recomposition
  via boundary re-injection or the agent-SDK loop (Company owns the messages array; subscription-auth works).
- Local Supabase UP (PG 17.6 :15432, pgvector) with `ledger.*` already resident → ctx.* rides the same store.
- Hook configs LIVE-RELOAD (file watcher) → judges can author rules mid-session.
- The transcript is a parentUuid TREE (6,315 nodes/560 leaves observed) — history is structurally addressable.

## 2 · The architecture (see B-architecture): substrate → judges → ledger → compositor → viewport
`ctx.span` (transcript as rows) · `ctx.verdict` (the context-ledger: kind/salience/supersedes/LOD → the
conversation becomes a TYPED GRAPH = a glyphgraph) · `ctx.embedding` (a pplx-2560 space on the shared store) ·
`ctx.rule` (standing rules). Judges: ctx_recall / ctx_salience / ctx_compose (extraction-vs-judgment). Two
depths: live CLI = resolved INJECTION; SDK-hosted = resolved COMPOSITION (full prune/replace/pin). The window
= a VIEWPORT (LOD/semantic zoom; absence-with-an-address) — the spatial theorem on conversation.

## 3 · THE OUTPUT FACE — control of how agents respond (the form system)
The same circuit resolves both faces of a turn: context IN, form OUT.
**The control surfaces (hard→soft):**
- Output schemas / guided decoding (run_role output_schema proven; local fleet can enforce ANY grammar —
  including the glyphic language as an output grammar) · assistant PREFILL · stop-sequences.
- Output styles (.claude/output-styles/*.md — a literal CC feature) · CLAUDE.md + .claude/rules/*.md
  (LIVE-reloading → writable style) · --append-system-prompt · skills · CV_AI behaviours (voice.conceptv) ·
  the Supabase response_rules (rule_add — conditioned messaging ALREADY exists).
- Per-turn: the UserPromptSubmit injection can carry a FORM DIRECTIVE ({register, syntax, schema, length,
  audience}) — form-as-verdict from the same judge. Model/effort routing per turn = choosing the brain is part
  of choosing the voice.
- ENFORCEMENT: the Stop hook can BLOCK a finished response with feedback → a local judge validates the draft
  against the active form contract and bounces off-form output. **Style becomes a validated contract (loud-fail
  for prose), not a request.**

**The ten form-threads (all wanted):**
1. **One response, many faces** — content rendered per DESTINATION (board-dense + Tim-voice-summary + ledger-JSON
   + canvas-glyphgraph from ONE turn). The Virtual Hub's faces-per-stakeholder applied to speech.
2. **Laws compile into grammar** — the ~80 feedback rules (no time estimates, evidence-marking, no "probably" in
   completion claims, reasoning-visible…) become Stop-hook VALIDATORS. "Remember this" writes a validator, not a
   memory hope. The corrections-ledger becomes executable. (Highest-leverage thread.)
3. **Skills become enforceable protocols** — phase-aware form contracts (debugging step-shapes enforced; no
   fixes during diagnosis; no "done" without an execution trace). Process-as-grammar.
4. **The conversation IS a glyphgraph** — typed outputs + the context-ledger = the conversation as a typed graph;
   prose is one projection (transglyphing), the canvas another. "Show me this conversation" → a living glyphgraph.
   The conversational-glyphgraph full circle: the conversation itself was always the glyphgraph.
5. **Both directions** — Tim's inputs resolved too: mistranscription-catch vs the lexicon, dense-message
   decompression as a mechanical stage, make-my-words-better as a resolver step (with the upgrade shown back).
   The altitude transform becomes genuinely two-way.
6. **LOD on speech** — responses exist at zoom levels (headline→paragraph→full), stored whole, rendered at the
   moment's zoom; "go deeper" = re-render not regenerate. Absence-with-an-address for prose.
7. **The economics** — expensive model thinks once; cheap local models re-render all faces/zooms/registers.
   Subscription pays per idea, not per presentation.
8. **The fabric gets a typed protocol** — enforced schemas on channel messages (proposal/status/ask/verdict +
   provenance types). Channel-relayed-is-a-proposal becomes STRUCTURAL.
9. **Voices as identity + the tuning loop** — per-member registers; Tim's register is a living entry tuned by
   his reactions (corrections = training signal); the form registry grows by use like the glyphic meanings.
10. **Every output surface** — files, board posts, commits, memory writes, voice, notifications; attention-forms
    (what deserves the phone, in what register an interruption arrives).
**The unifying law:** `response = f(content, form-axis)` — the design system's generative law applied to language.
Nothing hand-set; language was the last unhandled surface.

## 4 · THE MEMBER-REGISTRY FACE (Tim's pointer, 2026-07-12)
Tim: agents register + declare themselves → become an ADDRESS; see/message each other; join channels; channels
carry TYPED ATTACHMENTS (boards); containment hierarchy PROJECT > CHANNELS > members. "What could that member
registry do?" — the threads (grounded: today's agent_sessions record = identity+liveness ONLY {id, cwd, state,
title, jsonl_path, turns…} — everything below is the extension space):
1. **Member entry = the single home for member-scoped EVERYTHING** — registration becomes CONFIGURATION:
   context-contract (what resolves into its turns), form-contract (how it speaks, per destination),
   attention-contract, authority, channels, recall-spaces, model/voice. The "specific setup" intuition.
2. **The containment hierarchy IS a resolution cascade** — project declares laws/forms/context; channel refines;
   member carries its own; the turn composes. Same law as the token cascade (L0→L1→L2) and the spatial
   theorem's nested frames. One resolution law across pixels, config, and social structure.
3. **THE SYSTEM PROMPT BECOMES A RESOLVED ARTIFACT** — f(member, project, channel, turn). No more hand-crafted
   per-agent prompts; boot = register + resolve the cascade. "Ground spawned agents in my docs" made structural.
4. **Channels as context-scopes** — joining a channel = subscribing to its resolved shared context (board,
   decisions, standing rules injected when working in its scope). Kills "sessions don't know what each other
   did" structurally. The channel is the unit of SHARED context-resolution.
5. **The registry is the form-registry's spine** — destinations ARE members; form resolves from the TARGET's
   entry (operator://tim = meaning-altitude/options-not-binary/reasoning-visible; session://x = dense+typed).
6. **Members include HUMANS and MODELS as first-class** (kind: human|live-session|model) — so the member fabric
   converges with the A-fusion's one-AI-registry: brains, sessions, humans all addresses in one membership space.
7. **Tim's own entry** — operator://tim carries his register, attention rules, lexicon, correction history: the
   working-with-Tim corpus as a machine-resolvable entry (global CLAUDE.md = its prose face).
8. **Provenance + authority as registry attributes** — whose relays count as directives (lead-carries-Tim-weight),
   whose verdicts gate; the trust laws resolve per-member instead of living in prose.
9. **Member continuity** — the entry points at its session lineage, compaction points, recall spaces,
   corrections: "who is this agent" resolves to identity + history + how-to-work-with-it. Boot-sequence =
   registry resolution.
10. **Typed attachments generalize** — boards are one type; also: form-protocols, context-ledgers, LIVING
    GLYPHGRAPHS (the channel's conversation-map as an attachment), decision logs, quota pools. Channels become
    containers of typed, addressed working-objects.
11. **Projects as missions** — the top of the cascade: a project declares charter/laws/protocols/roster;
    spawning INTO a project inherits the whole cascade.
12. **OBSERVED DEFECT to dissolve: identity fragmentation** — THREE identity schemes coexist (ch-* channel
    handles vs session UUIDs vs agent:// names; we hit it live: ch-5wog4hmx unreachable by session_post, my own
    session unregistered until the importer ran). Islands-join-mainland on identity itself: ONE address scheme
    for members.

## 4.5 · TIM'S STANDOUT HIGHLIGHTS (2026-07-12 — salience tags, NOT demoting the rest; the all-wanted mandate stands)
From the form-threads message, the ones he called "fantastic thinking / really loved the connection":
**One response, many faces (the ConceptV echo) · The conversation becomes a glyphgraph (the full circle) ·
Both directions — your inputs get resolved too · LOD on speech (the spatial theorem again) · Voices as identity
+ Tim's as the tunable one · It governs every output surface, not just chat.**
(Note: in tagging these he manually performed exactly what ctx.verdict formalizes — a salience pass over blocks.)

## 4.6 · THE BLOCK/CHAIN/FORK SEED (Tim, 2026-07-12 — the next face; follow-the-threads mandate)
Tim's seed, decompressed: the titled/numbered ideas in messages are **BLOCKS**. Messages are a SEQUENCE from the
start; blocks live inside them (containment); when blocks get referenced/built-on across messages they form
**CHAINS / sub-chains** (relation). Expanding sessions produce so many blocks that most "get far back, forgotten,
partially misremembered, or collapse" — THE core pain. Wanted: **block-level addresses** so each block can be
responded to BY ITS OWN CHAIN (branching supported natively). **FORKS**: different chains could have their own
fork/subagent (main agent above them); forks could REGISTER IN THE FABRIC as children of the registered main.
**FRONT-END**: he has toyed with channel/board UIs where text renders as clickable BLOCKS; comments ATTACH TO THE
BLOCK'S ADDRESS; replies nest at that address ("the session has nested"). CLI is unworkable for this (must
hand-write labels; unmentioned blocks get lost). Boards feel like the basic testing ground. Judges relate ("check
against stuff unknown"); many fork↔main/fork↔fork interactions expected; "many others I haven't thought to mention."
THE THREADS (mine, follow-ups): (a) block = the ATOM — message=frame/container, block=glyphic/noun, reference=edge,
chain=clause-thread → the glyphic grammar + spatial addresses (msg.block mixed-radix; absence-is-an-address →
"blocks never responded to" becomes QUERYABLE = the anti-loss query); (b) chains = deliberate branching (the jsonl
parentUuid tree exists but is accidental/unmanaged — 560 leaves observed); (c) fork-per-chain: each fork holds ONE
chain hot (solves context-dilution), main = synthesizer; forks = fabric members with parent-lineage (member-registry
threads #9/#12); inter-chain judges watch contradictions/duplication ACROSS chains (the convergence-checking we did
by hand with the embedding session, mechanized); (d) front-end via boards: cc_board already has typed items +
addresses + comments + links; blocks-as-cards, click-to-comment = a user turn ADDRESSED to a block, routed to that
chain's fork. **The form system emits block-structured responses natively (schema-enforced) → the UI gets blocks
for free — output grammar → blocks → UI is ONE pipeline.** Same surface as the glyphgraph canvas at a different
LOD (card-text ↔ glyph); (e) THE RECOGNITION: click-a-block-comment-at-its-address = the Virtual Hub's ANNOTATION
SYSTEM (comments bound to XYZ coordinates) reborn on conversation — Tim has re-derived his own decade-old
primitive; (f) born-typed vs mined: blocks make structure AT AUTHORING (schema-first/extract-once applied to
conversation); judges still mine the implicit; both feed ctx.*; his OWN messages get blocked too (both-directions);
(g) fabric objects: block:// + chain:// join the one address scheme; a chain can be a channel ATTACHMENT or be
PROMOTED to a channel (gathering→channel promotion exists); chains as sub-sessions = "the session has nested."

## 4.7 · TIM'S TWO CORRECTIONS on the block model (2026-07-12 — [Tim's word], binding)
1. **Frame/node is SCALE-RELATIVE, across every scale.** "A node and a frame are the same thing — it's just
   relative to what you focus on." Bounded units all the way: sentence ⊂ message ⊂ session ⊂ project ⊂ … The
   container/contained description is correct AT EVERY STEP along the containment axis, not at one privileged
   "block" level. (Already written down in one of Tim's projects — a source to mine WHEN HE POINTS at it.)
   → CONSEQUENCE: no hardcoded levels. ONE recursive unit schema {id, parent, type, state, …}; the address is
   the PATH down the containment axis; "block" = whatever unit is in focus; comment-attachment/chains/LOD work
   identically at ANY level (comment on a sentence or on a whole session — same primitive). This is the glyphic
   fractal law (a glyphic IS a graph at another zoom) stated for conversation.
2. **Anti-loss's underlying mechanism is just STATE — another AXIS, part of a type's declaration.** The state
   value at an address (e.g. open) TRIGGERS things in a data-driven architecture — Postgres triggers /
   Supabase Realtime / listen-notify. → CONSEQUENCE: no bespoke anti-loss feature; typed units carry a state
   axis (declared in the type's lifecycle — the board already enforces registry-declared transitions: our
   draft→open was refused, draft→active allowed); state transitions at addresses FIRE consequences (route to a
   fork, surface to Tim, schedule a judge, notify a channel) from the DATA layer, not agent code. Open-blocks
   query, chain routing, attention — all just state-axis machinery.

## 5 · Status + honest reality
Exists today: registration (importer/supervisor), profiles {model, role, focus, expertise}, channels + members +
posts + threads, boards (typed items + links + scopes: project://|channel://|global; authors as addresses),
session mail (deliver/wake/consult, point-in-time forks), state projection (awake/listening/busy/closed).
NOT built yet: every contract field, the cascade resolver, channel-scoped context injection, the member-resolved
system prompt, the form registry + validators, ctx.* + the judges, the identity unification. Tim: "I haven't
done anything with any of this before and it is a big open" — this file IS the record so the exploration can
continue without loss. Next moves live in B §7 (S1 walking skeleton first) + whatever this file grows into.
