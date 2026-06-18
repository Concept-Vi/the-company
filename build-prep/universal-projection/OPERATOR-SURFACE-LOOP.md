# The Operator Surface + Right-Hand-Man — the Living Plan (the loop reads THIS)

**Originated by Tim Geldard (commission 2026-06-17); all derived work attributed to him.**
This is the **living spec** for the long build loop. The cron prompt carries ONLY the stable mode+laws and points
here. **The spec EVOLVES — update THIS doc, never the cron.** (That split is the fix for the last loop's stale-prompt
drift.) Engine criteria for the projection wheel itself live in `COMPLETION-CRITERIA.md`; the engine (G10/G9) is at
THE BAR and is NOT churned by this loop.

---

## THE MISSION

Significantly upgrade the surface so an **OPERATOR** (Tim's word — one who *uses and sees* an instrument, not a
"viewer") can both **use and understand** it, and integrate the Company's **right-hand-man (RHM)** into it as the
always-present guide. The RHM is the *teacher* that walks the operator through the surface. Tim intends the surface to
change significantly from its current state — **build for replacement, not permanence.**

---

## MODE + LAWS (stable — mirrored in the cron)

- **The operator never sees code / files / machine names.** Translate everything to human MEANING + CONTEXT; the AI
  SUPPLIES the words; the operator reacts to MEANING, never asked to validate technical words. ([[feedback-translate-everything-human-meaning]])
- **Meaning lives in the DATA, never in the instrument.** Self-describing fields on the registry; the instrument reads
  + renders, staying empty of meaning. Registry-is-truth (no hardcoded sectors/lenses/poles/labels).
- **DESIGN + CONFIRM before building.** Research (company MCP + the channel) and converge a design before building. Do
  NOT build on a not-yet-settled understanding (today's repeated lesson: "I don't know what I'm looking at"). Gate
  high-ambiguity content on design convergence.
- **Fit the design ethos** (DNA's system — `components/kit.tsx` + tokens; no bespoke values). **Build REPLACEABLE** —
  the V icon is a placeholder for the real V component; leave a clean swap seam (composition briefs the component).
- **Coordinate via the fabric** (decide WITH the members, then act): composition (`ch-2mnxl9j0`) = registries / assets /
  THE V COMPONENT / the legibility-type machinery; DNA (`ch-ovxwz8k8`) = the visual+verbal face; fork (`ch-8djrpmsl`) =
  the loadable brain; recollection (`ch-83e2cque`) = recall/index; lead (`ch-al7jdfdr`) = sequencing.
- autonomous-spawn-lead-only · no green-paint / half-done-as-done / time-estimates / versioning · embedder/loadout via
  the `company` CLI, fail loud · read-first on shared `ops/services.json`.

## THE BAR (all four + the root operator test)

(1) VERIFIED LIVE — curl + driven on the phone at **390×844 FIRST** AND 1440×900, never "code looks right";
(2) connects to ALL real data; (3) the OPERATOR can DRIVE it; (4) INTERACTIVE;
(5) **ROOT:** a person who knows NOTHING of the system can **use AND understand it** — verified by a fresh-eyes
non-technical critic + Tim on his phone.

---

## ⚡ SPRINT MODE — 2026-06-17 (Tim away; loop ~7min, overlapping fires fine)

Tim left for a while and called for a BIG IMPLEMENTATION SPRINT — "this is building a main part of the application."
So the loop is now IMPLEMENT-mode, not research-only. The reconciliation with "don't build on sand":
- **Build NOW** (low/medium-ambiguity): the V-overlay SHELL, the legibility-type mechanism (composition's vessel),
  the address-aim + brain-load integrations (WITH fork). Research only just enough to build the next SAFE piece.
- **Draft, don't stall** (operator-facing COPY — tutorial text, field names): the AI SUPPLIES a tentative draft
  (marked for Tim's later steer). Only FINAL ratification of copy is gated on Tim / OQ1–4.
- **Partners:** fork (`ch-8djrpmsl`) = build-together on address resolution + the loadable brain (split the integration).
  DNA = a point-in-time CLONE the lead is spinning (DNA herself is occupied) for the visual+verbal face.

## THE PHASES (sequenced so the loop can't build on sand — but in sprint mode they overlap)

### Phase 0 — THE OPERATOR JOURNEY  ·  ✅ APPROVED by Tim ("yeah OK", 2026-06-17)  ·  Part 1
The design ground everything else conforms to.

**The spine (the discovery):** every moment, at its own depth, answers the SAME three questions —
**① What am I looking at? · ② What can I do here? · ③ Where can I go from here?**
Pedagogy = never leave a moment with any of the three unanswered, in human terms. **Drill-down = the same three
questions one level deeper** (composition's "deeper coordinate on the same axes") — self-similar all the way down.

**The walk** (and the data each moment requires → how the journey names the fields):
- **0 · First contact (cold).** One breath: *what this whole thing is* + *what it's aimed at now* (meaning, not
  mechanism). → the instrument's one-line identity + the current **address**'s *what-this-is / what-fills-it*.
- **1 · Reading the whole.** What position means here — centre, near/far, the slices — for THIS aim + THIS lens.
  → the **lens**'s *what-position-means-here* (centre/angle/radius/poles → human).
- **2 · Something catches the eye.** "What's *that*?" — reward the wonder. → each **element**'s identity on inspection.
- **3 · The first reach (act).** Touch / hide labels / slide time; controls read AS controls; first act obvious, safe,
  reversible. → each **control**'s *what-this-does* + the operator-state that remembers what they touched.
- **4 · Going in (drill).** Re-aim at a thing's interior; re-orient with the same three questions at the new level.
  → the SAME meta on the deeper **address** (every level self-describes).
- **5 · Realising it re-aims.** It's not one view — point elsewhere, dial other lenses. "You are here; here's what else
  you can aim at + what each lens shows." → human names for every **destination** + every **lens** (what it reveals).
- **6 · Coming back (time + state).** It remembers where they were + shows what changed. → the operator's
  **journey/state** as itself addressable + self-describing.

**The legibility-type's facets (what the journey names — composition builds the vessel, the journey shapes the set):**
- **address/thing** → name · is · fills · why
- **lens** → what position means · what it reveals
- **element** → identity on inspection
- **control** → what it does
- **destination** → name · what's there
- **journey/state** → where you are · where you've been · what changed

Not one flat block — these *facets*, each attached to the kind of thing it describes, all answering ①②③ at whatever
depth the operator stands. Composition's "the field-set is itself a TYPE" → the journey designs that legibility-type.

### Phase 1 — RESEARCH (no building) → the three-doc prep
Explore-before-specify (the loop-prep law). Via company MCP (corpus, code search, capabilities) + the channel:
- The **address system** (the universal-projection resolver + the code:// contract; how addresses are formed/resolved).
- The **right-hand-man connection** (how the RHM connects — bridge, the AI session, the panel/chat surface).
- The **loadable brain** (fork's loadable-brain wire — `fork-gallery-brain-hooks.js`; how a brain is loaded/bound).
- Existing **overlay / floating-action / radial-menu / draggable** patterns in the design system (reuse, don't parallel).
- Composition's **V component** + the **V icon** image (asked: thread `t-1781683048`), + the **legibility-type skeleton**
  composition is drafting (thread `g-1781668099`).
Output: update `COMPLETION-CRITERIA.md`-style criteria + an implementation guide + a research synthesis for this build.

### Phase 2 — THE V OVERLAY SHELL (low-ambiguity — Tim was specific)
Safe to build once Phase 1 grounds the seams. The RHM's identity, on every page:
- The **V icon** (placeholder, from composition) in the **bottom-right corner**; an **overlay** over any surface.
- **Tap → expansion modes:** slots/options that **fan out around the corner angle** (a radial arc) — stays in the
  corner, thumb-reach, never takes the whole screen.
- **Draggable** anywhere (to read under it); persists position; **present on every page**.
- A **replaceable seam** so the real V component swaps in later (composition's brief defines the seam).
- Fit the design ethos; verify by use both viewports (390 first); fresh-eyes critic.

### Phase 3 — GATED on design convergence (high-ambiguity)
Do NOT build until the design (Phase 0 questions + composition's legibility-type) converges:
- **The built-in tutorial** — the V highlights + walks the operator through screen parts (what the surface is, how to
  use the instrument, what things are, where they go). This is Phase-0 pedagogy *delivered by the RHM*.
- **The legibility field-set** wired live (the instrument reads registry `meta` for whatever it's aimed at) — conforms
  to composition's legibility-type; blocked on the journey naming the field-set.
- **Multi-select comm/channel groups** through the RHM *(NEEDS TIM CONFIRM — see open questions)*.
- Connecting the **RHM connection** + **loadable brain** + **address system** into the surface behind the V.

### Phase 4 — THE DECISION SURFACE (the prove-on-one; lead-SEQUENCED 2026-06-18, thread g-1781731059)  ·  ACTIVE
Tim's "first composed product" — the keystone retargeted at decisions, resolution-first. Spec: `build-prep/the-one-application/DECISION-SURFACE-BUILD.md`. Build order (foundations first): **1 composition** (the 3 TYPES: decision/option/decision-card — the long pole, gates the rest) → **2 fork** (decision:// scheme + keystone wire + RHM brain) → **3 DNA** (decision-card archetype render, slide format) → **4 projection (HOST — us)** → **5 wildcard** (the TAKE: verbs→territory_write) → **6 recollection** (the common-memory recall leg).
**projection's piece (stream #4) — DESIGN-CONFIRMED (mostly ALREADY BUILT — the resolution-first payoff):**
- BUILT (reuse, zero net-new): `/api/territory` (scheme-agnostic resolve — PROBED on `decision://` → degrades clean, full resolution the moment fork registers the scheme); the HOST (instrument + V + GalleryMount); the gallery:verb dispatcher (the TAKE rides it).
- NEEDED (small; 3 seam Qs broadcast g-1781731457): (1) /api/cognition EXPLAIN-WIRE — fork: do I route your brain-turn-from-address, or do you provide it? (2) the universal-MEMORY route — recollection/fork: fold the recall into territory_for (then /api/territory carries it, zero net-new) or a recall:// scheme (projection adds a route)? (3) the decision-SLIDE host-mount — DNA: via window.DNA.renderGallery (existing host, zero net-new) or a new slide-sequence path (projection adds a container)?
- SMALLEST PATH: if (2) folds into territory_for + (3) reuses renderGallery, projection's ONLY net-new is (1) the explain-wire — possibly just routing fork's brain. **Build the residual the instant composition's types (#1) + the 3 answers land.**

---

## OPEN QUESTIONS (block freezing the field-set / Phase 3; nothing earlier)

- **OQ1 — the spine's fourth question?** Is ①②③ complete, or does the operator always carry a fourth ("what's this
  for / why should I care") that deserves its own standing? (Tim hasn't answered.)
- **OQ2 — missed branches?** Any operator path beyond first-contact / read / notice / act / drill / re-aim / return?
- **OQ3 — the cold-open first sentence.** What should the very first breath SAY? Sets the whole pedagogy; the most
  Tim's of all. (Cheapest highest-value item to grab live.)
- **OQ4 — "multi-select comm select groups"** — confirm meaning (read tentatively as "select multiple communication
  groups at once" through the RHM).

---

## STATUS LOG (update every fire, honestly — ✅/🟡/🔴)

- **2026-06-17 — loop armed.** Phase 0 ✅ approved (operator journey). V-icon asked of composition (`t-1781683048`).
  Legibility-type skeleton in progress with composition (`g-1781668099`). NEXT: Phase 1 research (address system / RHM
  connection / loadable brain / overlay patterns) — NOT building yet. OQ1–OQ4 open.
- **2026-06-17 — Phase 1 research started.** Fork (`ch-8djrpmsl`) engaged on **address resolution + the loadable-brain
  integration** (thread `t-1781684391`) — Tim's pointer (fork built the loadable-brain wire + knows the resolve path).
  Asked: address-resolution path + traps, how a brain loads/binds + carries across every page (RHM connection), what to
  reuse-not-parallel. Awaiting fork's reply; will fold into the research synthesis.
- **2026-06-17 — ⚡ SPRINT MODE on (Tim away).** Loop cadence → **~7min** (job `961a66ef`; was 2h). Fork now a BUILD
  PARTNER (split the integration; thread `t-1781684391`). Lead asked to spin a **DNA point-in-time clone** for the
  visual+verbal face (thread `t-1781684666`; Tim's model intent "a fable… system should change it to opus" — lead owns
  the mechanics).
- **2026-06-17 — ✅ Phase 2: the V-OVERLAY SHELL built + verified (commit `3ac24f3`).** The right-hand-man handle:
  company-gold V icon (composition's `vi-classic-gold.svg`, copied to `surface/app/src/rhm/v-icon.svg`), bottom-right,
  DRAGGABLE + position-persisted (localStorage), on EVERY page (mounted at App root). Tap → the **6-verb radial fan**
  (composition's V-corner-handle contract: navigate/ask/annotate/drive/open-source/generate → draft labels Go to/Ask/
  Note/Drive/Source/Make) with a soft paper **overlay scrim**. Files: `surface/app/src/rhm/{RightHand.tsx,rhm.css,
  v-icon.svg}` + mounted in `App.tsx` + css in `main.tsx`. VERIFIED BY USE at **1440 + 390** (fan legible, no overlap/
  clip, drag moves+persists exactly), `tsc` + design-lint clean (0 off-token literals), 0 console errors, a SEPARATE
  fresh-eyes design-critic returned **PASS** (both its flagged issues — chart-overlap legibility + arc-not-column —
  resolved by the scrim + left-lean). Built on `paper.css` tokens; the gold lives in the SVG, not CSS.
  **SWAP SEAM** (composition's contract): the real V organism later renders into THIS container; verbs emit a
  `rhm:verb` window event the integration phase consumes (meet-at-data, no cross-repo code import).
  **MINOR polish carried (non-blocking, critic):** (a) ease the arc to bow slightly (currently ~linear diagonal);
  (b) on-device check the lowest pill's margin vs the scrubber thumb-zone.
  **NEXT:** (1) INTEGRATION with fork — wire the verbs to the address system + loadable brain (awaiting fork's brief,
  thread `t-1781684391`); (2) the built-in TUTORIAL (Phase-0 pedagogy delivered by the RHM — gated on journey/copy);
  (3) the legibility meaning-layer (composition's legibility-type, thread `g-1781668099`). Verb ACTIONS are stubs
  (emit the seam event) until (1) — honestly a shell, not wired behaviour.
- **2026-06-17 — ✅ Phase 3: the RIGHT-HAND-MAN BRAIN wired into the V (commit `c93c6ef`).** Tapping "Ask" opens a
  paper talk panel where the operator talks to REAL Claude Code about the current AIM (fork's `forkVBrain.attach` —
  the V host owns the aim [getAimAddress/getAimLabel, follows `projection:select`, default `ui://instrument/surface`];
  fork owns turn/stream/write). Applied bridge diff 3 (`/api/territory/label` → human aim-label). Synced
  `fork-brain-core` + `fork-v-brain` into the host (core loads first). VERIFIED BY USE: a real Claude Code reply
  STREAMED into the V panel at 390; panel renders at 1440; `forkBrainCore`+`forkVBrain` loaded, `.v-brain` mounted;
  0 console errors; design-lint 0, tsc 0.
  ★ OPERATOR-LAW FIX (caught by-use): the brain LEAKED a raw address ("I'll investigate what `ui://instrument/surface`
  …") in its first reply → strengthened `PANEL_BRIEFING` (`ui_claude_session.py`) to forbid raw addresses/scheme://
  in replies + told it the address-context is FOR-IT, not to echo → re-verified: "a piece of his own interface", no
  leak. (Put it in the canonical operator-face prompt — covers V + gallery; flagged fork, thread `t-1781684391`.)
  - 🟡 **RESIDUAL (flagged to fork's context-tuning lane):** when the aim is THIN/unregistered the brain narrates the
    system's internal readout ("empty blast radius, a module error on the relations leg") — softer than an address
    leak but still semi-jargon. Fixes: a meaningful registered default-aim + briefing tuning to not narrate internals.
  - **TRAIL for the lead's union (absorb-not-fork):** touched `/api/territory/label` (new read route) + the brain
    wire (the `_claude_stream` briefing). Note for the substrate-unification to absorb.
  - **NEXT:** wire the OTHER verbs (navigate/note/drive/source/make → their backends), the built-in TUTORIAL (Phase-0
    pedagogy delivered BY the RHM), and the legibility meaning-layer (composition's `legibility.js` `resolveLegibility`,
    built + ready — the instrument reads registry `meta` for the aim + renders human meaning).
- **2026-06-17 — ✅ LEGIBILITY (first slice): the legend reads HUMAN meaning from the REGISTRY (commit `7d9b646`).**
  Tim's #1 complaint ("I don't know what I'm looking at") — the Kinds-view legend was hardcoded jargon in `Legend.tsx`
  ("11 sectors · angle = the kind of each event"). MOVED the meaning into the REGISTRY: seeded `bindings/raw.py`
  `meta:{name,is,fills,why}` (composition's SEED shape; TENTATIVE draft copy), passed it through `/api/projection`,
  typed in `api.ts`, rendered DECLARED-FIRST in `Legend.tsx` (fallback = the computed lines for un-seeded lenses). The
  Kinds view now reads: "What's happening · A live map of everything the Company is doing · Each dot is one thing that
  happened — a note saved, a job run, a message; its slice is what KIND it is; how far from the centre is how long
  ago…". VERIFIED BY USE 390 + 1440 (jargon gone, human, registry-sourced), design-lint 0, tsc 0, 0 console errors.
  The instrument stays EMPTY of meaning (reads `binding.meta`) — registry-is-truth, the architecture Tim ratified.
  - **Coordinated composition** (thread `g-1781668099`): I seeded `binding.meta` with their SEED field shape on the
    surface/registry side; their legibility-type validate/backfill machinery enforces/declares it; field-set stays
    journey-gated (OQ1–4).
  - **NEXT:** (a) seed the OTHER lenses' `meta` so every view is legible (connections / two-gravities / meaning / …);
    (b) the SECTOR names (the ~51 machine kind-ids → human) — the lexical layer, needs per-kind meaning + an endpoint;
    (c) a HIDE toggle for the legend (Tim: "be able to hide them"); (d) the remaining verbs (Go to/Note/Drive/Source/
    Make) + the built-in tutorial.
- **2026-06-17 — ✅ LEGIBILITY: the WHOLE lens system reads human (commit `9b5da09`).** Seeded `meta:{name,is,fills,why}`
  + humanized the jargon `label` across ALL 9 bindings (raw / by_node_type / by_separator / by_nucleation / semantic /
  by_cascade / by_lens / grouped / time-of-day). Fixes Tim's IMG_1925 dropdown complaint: "Connections — the node
  registry by its directional type-flow" → "Connections — how things flow into each other"; "Type-nucleation" → "New
  kinds forming"; "Lenses — angle by the projection registry" → "Ways of looking"; etc. Registry-true (meaning in the
  rows; the Legend renders declared-first). Composition CONFIRMED the shape (19:53 — meta on any row; their validate/
  backfill covers it; ONE legibility-type, MANY registries). TENTATIVE copy (Tim/DNA ratify; field-set journey-gated
  OQ1–4). VERIFIED BY USE 390: switched to Connections → the human legend renders + the dropdown is fully humanized
  (raw verified at 1440 earlier; shared Legend component). The instrument stays empty of meaning.
  - **NEXT:** (a) the ~51 SECTOR kind-ids → human — composition's answer: SAME legibility-type, OWN kinds-registry; seed
    kind rows with `meta` now (tentative), the set-diff finds misses → needs the kinds-registry + a per-kind meaning
    path + the wheel-label render; (b) the HIDE toggle for the legend (Tim's "be able to hide them"); (c) the remaining
    verbs (Go to/Note/Drive/Source/Make) + the built-in tutorial.
- **2026-06-17 — ✅ legend HIDE TOGGLE (commit `add09df`).** Tim's "I should be able to hide them if wanted" — the
  legend explanation now collapses (the TITLE stays for orientation; the preference persists, localStorage). Refactored
  Legend to compute the orientation once (meta-first → fallback) then wrap it in the collapse; paper-token toggle +
  focus-ring. VERIFIED BY USE 390: collapse hides the lines + keeps the title, flips Hide↔Show, persists across reload;
  tsc 0, design-lint 0 (1440 = shared Legend component).
  - **NEXT (sector kind-names — coordinating composition, thread `g-1781668099`):** asked WHERE the kinds-meaning
    registry should live (no existing kind→human registry found — only closed primitive tuples) so I seed on their
    validate/backfill machinery, not beside it. RENDER plan = TAP-A-SECTOR → human name + one-line meaning (reuse the
    existing sector-selection), NOT 51 labels at once (crowds at 390). Then: the remaining verbs (Go to/Note/Drive/
    Source/Make) + the built-in tutorial.
- **2026-06-17 — ✅ LEGIBILITY: SECTOR kind-names → human (commit `d704e27`).** Tim's "I don't know what a sector
  is" — the wheel's sectors were raw machine-ids. NEW kinds-registry `kinds/raw.py` (composition's specified home:
  mirror bindings/raw.py, ONE meta map `{kind:{name,is}}`); `projection.py` sets each sector's `label` = the kind's
  human name (declared-first via the registry) + `meaning`, humanize-id fallback for un-seeded; sectors now tappable
  in ALL views (was edges-only); the tap-a-sector readout shows the human name + one-line meaning. VERIFIED BY USE
  390: tap `corpus.record` → "A note saved · The system wrote something into its memory"; all 11 raw-view sectors
  read human. Registry-true, instrument empty of meaning. tsc 0, design-lint 0, 0 console errors. Coordinated
  composition (kinds/raw.py is their home; their validate/backfill set-diff covers un-seeded kinds).
  - **NEXT:** the remaining verbs (Go to/Note/Drive/Source/Make → their backends); the built-in TUTORIAL (Phase-0
    pedagogy by the RHM); seed more kinds + the OTHER registries' meta (node-types/lenses/…) as views surface them.
- **2026-06-17 — ✅ the 'NOTE' VERB wired (the first ROUTE-BACK from the V).** Tapping the V's **Note** opens a paper
  composer that writes the operator's comment AT THE CURRENT AIM — reusing fork's brain (`brain.direct({type:'comment'})`
  → `/api/territory/write` → `suite.mark`); NO parallel writer. The V now re-aims at a **tapped sector** via a new
  `projection:aim` window event (Wheel→RightHand) — deliberately NOT `projection:select` (that opens a content face;
  a synthetic `ui://instrument/sector/<id>` would fail-loud in GalleryMount). The event carries the sector's HUMAN
  name **and** one-line meaning, so the composer head reads "Note about: A session turn / A working session finished
  one back-and-forth." (operator-law: meaning, never the address). After Save → "Noted ✓" then the composer
  **auto-closes** (timer cleared on edit/reopen/close/unmount — no lingering empty box). Files (this fire):
  `surface/app/src/wheel/Wheel.tsx`, `surface/app/src/rhm/{RightHand.tsx,rhm.css}`.
  - **VERIFIED — round-trip, by use, BOTH viewports.** Pre-flight curl proved `comment` is a registered mark_type +
    `suite.mark` accepts a sector target. Then DRIVEN: 390 (tap `agent_sessions.turn` → V → Note → type → Save) and
    1440 (`corpus.record`) — each note **READ BACK** from `suite.marks_for(ui://instrument/sector/<id>)`
    (value = the typed text, source=`operator`), not a POST-200. Auto-close + clean reopen verified by use at 390.
    tsc 0, design-lint 0.
  - **HONEST coverage:** the happy path is use-verified at both viewports + store read-back. The **error path** (brain
    module unmounted, or a write failure → "Couldn't save") is **logic-traced only**, not driven — it surfaces loud
    (no silent no-op) but has not been exercised live. (Two test marks now sit at `sector/_probe` +
    `sector/agent_sessions.turn` + `sector/corpus.record` — harmless; nothing renders sector-notes yet; the store has
    no delete API.)
  - **FRESH-EYES CRITIC (separate agent, cold-drive 390):** returned NEEDS-WORK, but its headline ("context chain
    broken — header steals a toast string") was a **MISDIAGNOSIS** — it drove blind (checked SVG `title` attrs, never
    saw the `.conn-readout`) and pattern-matched the sector-identity readout as a save-toast. Proof it's wrong: the
    `agent_sessions.turn` test showed "A session turn" (no save-connotation) and read back at that address. REAL signal
    extracted + FIXED this fire: (a) composer ambiguity → added the **meaning line** under the name; (b) the
    no-auto-close dead-end → **auto-close**.
  - **ROUTED to the legibility beat (not deferral — wrong evaluator here):** several kind NAMES read as past-tense
    EVENTS rather than CATEGORIES ("A note saved" ≈ "a note was just saved"). Cross-cutting (touches every kind, copy
    is TENTATIVE pending Tim/DNA); **Tim's eyes on his phone are the real fresh-eyes test** per THE BAR. The legibility
    beat should revisit `kinds/raw.py` naming. Also flagged: verb labels **Drive/Source/Make read as jargon** to a
    non-technical operator (tentative; ratification gated on Tim/DNA + OQ3 tutorial).
  - **NEXT:** the remaining verbs (Go to/Drive/Source/Make → backends); the built-in TUTORIAL (gated OQ3); seed more
    kinds + other registries' meta as views surface them.
- **2026-06-17 — ✅ re-verified the V BRAIN survives fork's env-scrub + ✅ LEGIBILITY: the CONNECTIONS lens reads human.**
  TWO things this fire:
  - **(1) MANDATORY re-verify (fork touched my wire).** fork's commit `1c0aa25` made `ui_claude_session.run_turn`
    pass `env=_brain_env()` to the `claude -p` Popen (strips `SUPABASE_*`/`VI_VISION_*` from the brain subprocess,
    for the vi-vision merge). Drove 'Ask' on my live mount at 390: the full turn streamed GREEN — init→text→tool→
    final (~1.8k-char grounded reply; it ran a grounding TOOL mid-turn, so tool-use survived the scrub), POST
    /api/claude/turn 200, no error, operator-law held (said "the Instrument surface", never a raw address). No
    regression; reported to fork (thread `t-1781684391`).
  - **(2) the CONNECTIONS lens (binding=by_node_type) was illegible** — its sectors are NODE TYPES, not kinds, so
    they fell through to the humanize-only fallback: cryptic titlecased ids ("Llm", "Titlecase", "Rhm Mode",
    "Portal", "Gate"), `meaning: null` on all 16 (verified via curl). FIX, mirroring the accepted `kinds/raw.py`
    pattern (composition's "ONE legibility-type, MANY registries"): NEW `nodes/_meta.py` `NODE_TYPE_META`
    `{node:{name,is}}` for all 16 node types (grounded in each node module's own docstring, TENTATIVE for Tim/DNA);
    `nodes/__init__.py` makes the dir importable (discover() skips `_`-files, so neither is loaded as a node);
    `projection.py` now picks the meaning-registry by sector DOMAIN (`binding.angle_from`: kinds default, node-types
    for Connections) via `_SECTOR_META_BY_DOMAIN` + the `_kind_name/_kind_meaning(s, meta)` param. Files:
    `nodes/{__init__,_meta}.py`, `runtime/projection.py`.
  - **VERIFIED BY USE, BOTH viewports.** 390: switched lens → Connections, tapped `llm` → readout "An AI step /
    Calls an AI model to transform or generate text. / 1 out · 5 in". 1440: tapped `retrieve` → "Find the nearest /
    Searches a collection and returns the items closest in meaning to your query. / 2 out · 3 in". Kinds (raw) lens
    re-checked = no regression (6/6 still human). Bridge restarted to load the registry; curl-confirmed 16/16 seeded.
  - **FRESH-EYES copy critic (separate agent, TEXT not blind-drive — avoids last fire's readout-misread):** judged
    the 16 name/desc pairs as a non-technical reader; 12 CLEAR, 4 UNCLEAR. FIXED all 4 in `_meta.py`: dropped
    "source code"→"code"; "numeric fingerprint"→"a fingerprint of its meaning"; "order matters"→"keeping the order
    you gave them"; and the worst — "The V's mode"→"Right-hand-man mode" (the name assumed you know what "The V"
    is, and my own description already said "right-hand-man" — inconsistent). Re-verified post-fix via curl.
  - **HONEST:** node-type COPY is TENTATIVE (Tim/DNA ratify; some — model_of_tim/rhm_mode/portal/gate — are my
    grounded reads of dev docstrings, not Tim's words). HOME is a sibling meta-map; the declared-at-birth ideal
    (a `META` on each node module, read into NodeType like OUTPUT_SCHEMA) is composition's call — flagged to them.
  - **VERBS still blocked (not built this fire, deliberately):** Go to/Drive/Source/Make have no defined operator-
    semantics in the briefs (the briefs define the ADDRESS-MOVER roles — recollection.navigate / fork.resolve —
    not what each V verb MEANS), AND the dominant V-aim is a synthetic `ui://instrument/sector/<id>` that doesn't
    map to centre/resolve/source on a real data node (App's relative-centre needs an embeddable address). Building
    one now = guess OR a frequently-no-op verb. Asked fork (the navigate-mover question) + will ask composition for
    the verb contract. Chose the safe high-value legibility beat instead.
  - **NEXT:** get composition's verb-contract semantics → build the clearest verb; coordinate node-meta HOME with
    composition; seed the OTHER registry domains' meta (roles/mark_types/lenses) as their lenses surface; TUTORIAL gated OQ3.
- **2026-06-17 — ✅ LEGIBILITY: human kind-words ride on every POINT + the point-inspector's operator-law LEAKS fixed; ⚠ found the DEFAULT-PATH drill-in (DNA's gallery face) badly illegible → routed to DNA.**
  - **The verbs stayed blocked** (composition heads-down on the vi-vision creds merge; no verb-contract reply yet). Confirmed
    they're genuinely blocked/redundant: re-centre is ALREADY wired (Disclosure "⊙ centre here" + CentreChip), so a
    'Go to'=re-centre verb would duplicate; Make=generate is the lead-governed gated keystone (NOT brain-callable, per fork).
    So I did the safe high-value legibility beat instead.
  - **★ FRESH-EYES (the dot-drill, deferred twice — finally tapped):** on the DEFAULT path, tapping a real thing opens
    DNA's gallery FACE, and it's badly illegible: the annotation row renders as bare ICONS (★ ✓ ✕ ? ☆ → + a tofu glyph)
    shown TWICE with machine-name aria ("remember_this", "do_this"), and the panel literally titled **"What this is"
    contains NO words** — just more icons. That's the deepest "understand what I'm looking at" surface failing the ROOT
    bar. It's DNA's visual+verbal face (GalleryMount hosts window.DNA) — NOT my lane to rebuild → ROUTED to DNA with the
    evidence + the fix-data (below).
  - **ROOT-CAUSE FIX (my lane, registry-is-truth): every PROJECTION POINT now carries `kind_name` + `kind_meaning`**
    (read declared-first from the kind registry; humanized-id fallback). The machine `kind` stays the key; the human
    words ride ON the data so EVERY consumer (the inspector, the gallery face, a future tooltip) shows MEANING, never
    the id. This is exactly the data DNA's "What this is" needs. Files: `runtime/projection.py`, `surface/app/src/lib/api.ts`.
  - **POINT-INSPECTOR (Disclosure.tsx, my lane) operator-law LEAKS fixed:** it was showing the **raw machine kind-id**
    as the header (`point.kind`), a **raw ui:// address** in a `<code>` footer, and the machine sector-id in the "in"
    row. Now: header = `kind_name` (case preserved — removed the `text-transform:lowercase` that would mangle "An AI
    step"→"an ai step"); a new meaning line under it; the raw-address `<code>` REMOVED (the address still rides on
    `data-ui-ref` for the spine, just never shown); the "in" row shows the human kind name on the Kinds lens. Files:
    `surface/app/src/wheel/Disclosure.tsx`, `surface/app/src/surface.css`.
  - **VERIFIED BY USE, BOTH viewports:** 1440 (Disclosure panel) + 390 (sheet), drove an address-less point (seq-5997,
    the gallery face only suppresses Disclosure for addressed points) → header "A session turn", meaning "A working
    session finished one back-and-forth.", in: "A session turn", NO raw address. Curl: all 600 points carry kind_name
    + kind_meaning. tsc 0, design-lint 0. Bridge restarted for projection.py.
  - **HONEST / still leaking (NOT my lane — routed):** (a) DNA's gallery FACE (the main drill surface) — to DNA; (b) the
    HOWTO **context-item text** embeds a raw "ui://canvas" (it's CORPUS CONTENT from /api/context, not a UI label) —
    flag to fork/composition (context composition); (c) other-lens "in" rows still show the sector leaf (those lenses'
    sector-human-names aren't carried on the point yet — a later enrichment).
  - **NEXT:** DNA renders point.kind_name/kind_meaning + labels the gallery-face icons (routed); composition's verb
    contract → build a verb; carry sector-human-names on points for non-Kinds "in"; TUTORIAL gated OQ3.
- **2026-06-17 — ✅ the V's VERBS are now LIVE on composition's unified `gallery:verb` contract; ✅ `navigate` (Go to) =
  re-centre wired + verified; ✅ fixed a latent gallery-reopen bug.** The verb contract LANDED (composition ch-2mnxl9j0
  + wildcard ch-piffgfxv): canonical ids navigate/ask/annotate/drive/open-source/generate; ONE event `gallery:verb`
  `{verb, aim_address, payload}`; projection owns navigate/drive/open-source, ask→fork, annotate/generate→wildcard;
  verb-order GO-TO+SOURCE first, MAKE last (writable-aim-gated). Built:
  - **The V (RightHand) now emits the unified `gallery:verb` envelope** for navigate/drive/open-source/generate
    (replacing the bare `rhm:verb` stub); ask/annotate stay the V's own legs. The verb ids already match composition's
    canonical ids.
  - **projection-side DISPATCHER (App.tsx)** consumes `gallery:verb` and routes by verb — the durable, swap-independent
    consumer (survives DNA's incoming vee-dock V). **`navigate` (Go to) = RE-CENTRE the instrument on the aimed THING**
    (reuses the proven `focusCentre` — the seed §8 relative-centre). Aim-type-gated: a real-unit aim (a picked point,
    run://·code:// addr) re-centres; a synthetic sector/surface aim → a calm Notice ("Go to re-centres on a thing — tap
    a dot first"). drive/open-source/generate → honest "… is coming next." Notice (no silent no-op) — actions pending.
  - **★ BUG FIXED (latent, mine): the `projection:select` effect re-fired on EVERY re-projection** (it had `proj` in
    deps), re-announcing the same selection on each lens/centre/time/**live-pulse** re-fetch → DNA's drill re-rendered
    → the drill face **re-opened spuriously** (incl. right after a Go-to re-centre, and on every live pulse while a
    point was selected). Fixed: dispatch only when the selected UNIT changes (ref-guarded); space-change already clears
    selection so the detail stays current. Files: `surface/app/src/{rhm/RightHand.tsx,App.tsx}`.
  - **VERIFIED BY USE, BOTH viewports.** 390 + 1440: picked an addressed point (seq-5849 → run://…/voice.py) → dismiss
    drill → V → **Go to → the wheel re-projected around "voice.py"** (CentreChip "⊙ voice.py", radius flips to
    "distance: structural from voice.py"), and the drill face did NOT re-open (fix holds). Sector-aim Go-to → the
    honest Notice (390). Drive → "Drive is coming next." (1440). tsc 0 (no CSS this fire).
  - **★ ARCHITECTURAL OBSTACLE surfaced to composition/DNA:** point-aim verbs fight the interaction model — picking a
    thing opens DNA's gallery FACE which (a) sits ABOVE the V (z-order, V unreachable while open) and (b) is the only
    way to aim the V at a real point (address-less points aim at the surface). So a point-verb needs a pick→dismiss→V
    dance. The verbs want either a usable aim WITHOUT the face dominating, or to operate from within the face. Design
    call for composition (contract) + DNA (face).
  - **OPEN with composition (asked):** confirm `navigate`=re-centre (vs locate — the contract gave the EVENT, not the
    per-aim ACTION); specify drive/open-source actions for sector vs point aims; MAKE wiring is wildcard's gated keystone.
  - **NEXT:** composition's per-aim action spec → wire drive/open-source; resolve the gallery-intercept so point-verbs
    are one-tap; DNA's vee-dock swap (emits the same `gallery:verb`); TUTORIAL gated OQ3.
- **2026-06-17 — ✅ the V's "SOURCE" (open-source) VERB GOES LIVE — drill past the dot to the fuller record (commit `660fd40`).**
  composition CONFIRMED the per-aim spec (their 22:51 reply): open-source = REVEAL THE AIMED THING'S SOURCE — for a real
  point, its definition/record + provenance. The advisor caught a conservative drift (I'd argued myself out of this on a
  redundancy worry composition had already refuted): open-source's ACTION is NOT blocked — only its button-PLACEMENT is
  (composition escalating verb-bar-on-face to Tim). The App `gallery:verb` dispatcher consumes the verb regardless of
  who/where emits it, so the action survives whatever placement Tim picks. So I built it (a READ — safe for the away-sprint,
  no write-gate like generate, no socket like drive; the most-specified verb; serves the ROOT bar most). Built:
  - **NEW `GET /api/territory`** — the structured, scheme-agnostic SOURCE read; REUSES fork's `territory_for` (NOT rebuilt);
    sibling of `/api/territory/label` + `/write`. **This is the projection-HOST's named "/api/territory wiring" leg** the
    lead's seam map calls projection's lane. Hands the surface the structured dict — `territory_prose` is brain-framed
    ("[internal handle — never shown to operator]…") so the SURFACE does the human translation, not the resolver. Route-table
    acceptance green (8/8). Bridge restarted to load it.
  - **NEW `surface/app/src/source/{SourcePanel.tsx,source.css}`** — a DURABLE, swap-INDEPENDENT App-level surface (NOT inside
    the replaceable V `rhm/`): reads the comprehended record and shows it in PLAIN WORDS. `readTerritoryContent` handles
    `output`-as-prose AND `output`-as-LIST (→ bullet lines) — recursive; a STRUCTURED/unresolvable record degrades clean
    ("not in plain words here"), NEVER a raw dict/code/address dump (operator-law). Provenance line only when real board refs
    exist (0 for corpus points → honestly absent). Paper-tokened; design-lint 0/0.
  - **App.tsx dispatcher:** `open-source` → `fetchTerritory(selected)` → the panel; a synthetic sector/surface aim → a calm
    Notice (sector-DERIVATION source is the next beat), never a silent no-op. Opening Source clears the point selection so the
    redundant inspector doesn't double up behind it.
  - **VERIFIED BY USE, BOTH viewports (390 first, then 1440):** drove the real path (pick a corpus point → dismiss DNA's face →
    V → Source) → the 6 captured principles render (the inspector showed NOTHING — summary is empty for these points). Address-
    less point → the honest Notice. tsc 0.
    - **★ advisor caught a verify-the-wrong-way gap:** I first dismissed the face via Escape — but the PHONE has no Escape, the
      operator taps the close-✕ or the scrim. Re-verified at 390 the REAL mobile dismiss BOTH ways (tap `.gallery-dismiss` AND
      tap `.gallery-scrim`): `selected` persists through each (GalleryMount's dismiss only flips `galleryOpen`, never touches
      selection) → V → Source → panel WITH the record, NO "tap a dot first" Notice. The named-device bar holds for the real tap.
  - **★ FRESH-EYES critic (separate agent, screenshots):** strongest findings FIXED — (a) the bullets floated with no heading
    → added a "What's in it" body label so it coheres; (b) the tag "SOURCE" read as "source code" → reframed "The full record"
    (+ relayed the verb-LABEL rename signal "The full story"/"See the record" to composition, whose contract owns the draft
    label); (c) two same-titled cards read as broken → clearing selection on Source-open removes the duplicate inspector.
    FILTERED OUT (intentional): the bullet CONTENT being engineer-speak ("structured JSON output") — that's the REAL stored
    record; sanitizing it = fabrication and defeats "Source = the actual thing." Faithful display is correct.
  - **⚠ HONEST / flagged (not blocking):** the RELATIONS (provenance) leg in `territory_for` throws ModuleNotFoundError ONLY
    in the live bridge process (degrade-clean note; reproduces clean in a fresh interpreter AND on `import runtime.bridge`, so
    it's the threaded-request import state). edges_in=0 for corpus points regardless → Source's provenance line correctly shows
    nothing. → flagged to fork (ch-8djrpmsl) with evidence + asked them to (a) diagnose, (b) put the exception MESSAGE in the
    degrade-note. NOT claimed fixed (couldn't root-cause without instrumenting the live process).
  - **COORDINATION (via fabric):** composition (Source live + label signal + drive held on placement); fork (/api/territory +
    the relations-bug flag); lead (confirmed wildcard's HOST/TAKE conflation correction — projection=HOST, wildcard=TAKE; +
    RESOLUTION-FIRST absorbed); DNA (the DECISION-SURFACE-BUILD.md company-repo PATH they asked for + the meaning-fields +
    /api/territory reuse for their decision-card render).
  - **NEXT:** **sector-human-names on points** (the advisor-noted few-line ride-along, deferred to keep this beat clean — the
    Disclosure "in" row still shows a machine sector leaf on non-Kinds lenses; carry `_kind_name(sid,_sector_meta)` onto each
    point); DRIVE / open-source-on-SECTOR (sector-derivation source) once Tim's verb-PLACEMENT steer lands; DNA's decision-card
    render reuses /api/territory; TUTORIAL gated OQ3.
- **2026-06-18 — ✅ LEGIBILITY: the inspector "in" row reads HUMAN on every lens + ✅ ratified verb label "See the record"; ⚠ relations-bug ROOT-CAUSED (handed to fork) after a self-inflicted bridge outage I recovered (commit `acd5e81`).**
  - **✅ Beat A — SECTOR-HUMAN-NAMES (commit `acd5e81`):** every projection point now carries `sector_name` (the sector's human
    name via the lens's meta-registry). The Disclosure "in" row was `p.sector===p.kind && kind_name ? kind_name : leaf(p.sector)`
    — so on NON-Kinds lenses it showed the raw machine sector-id (operator-law leak). Now `p.sector_name || leaf(...)` → human on
    EVERY lens. **VERIFIED BY USE both viewports** on the Activity (grouped) lens: machine `sector="field"` → the "in" row reads
    "Field"; data-level on Ways-of-looking: `common_knowledge`→"Common Knowledge", `memory`→"Memory". Kinds lens unchanged
    (sector==kind). Files: projection.py (compute `_sector_meta` before the points loop), api.ts, Disclosure.tsx.
  - **✅ Beat A2 — ratified label (commit `acd5e81`):** composition ratified (thread t-1781703728) "Source"→**"See the record"**
    (verb id `open-source` + the gallery:verb envelope UNCHANGED — display-only; rejected "The full story" as it collides with
    the coming slide/story/sequence concept). Verified live in the V fan.
  - **⚠ Beat B — the relations-leg bug: ROOT-CAUSED, but NOT fixed by me (correctly).** Pulled fork's fb1c631 message:
    `No module named 'lifters.frontmatter'; 'lifters' is not a package`. ROOT = a **NAME SHADOW**: `runtime/lifters.py` (the
    lifter-registry module) shadows the top-level `lifters/` PACKAGE. The service runs `python runtime/bridge.py` → sys.path[0] =
    the script dir `runtime/`, so `from lifters.frontmatter` (cc_board.py:46) resolves `lifters` → `runtime/lifters.py` (a module)
    → "not a package". Fails PERSISTENTLY in the bridge process (not request-time pollution as first theorized) — which is why the
    leg is always dead + why `python -c` couldn't repro (cwd-root puts the package first). **★ I tried a fix (eager-import cc_board
    at bridge.py module-top to cache it) and it CRASH-LOOPED the bridge at startup** (line-27 hits the same shadow before serving).
    I REVERTED immediately; bridge recovered in ~6s (`/api/now` 200). The clean fix touches CORE (runtime/suite.py + tests + the
    shadow rename) — NOT projection's lane, and the bridge is too central to hack. → handed fork the definitive root cause + two
    fix options (A: rename `runtime/lifters.py`→`lifter_registry.py` [recommended]; B: repo-root-first on sys.path) + the
    don't-eager-import warning. Degrade-clean holds meanwhile (edges_in=0 for corpus points → Source's provenance correctly silent).
  - **★ LESSON (recorded):** verified-by-use means run-as-the-SERVICE-runs. My fresh-interpreter + `import runtime.bridge` checks
    BOTH passed and masked a startup crash that only appears under `python runtime/bridge.py` (script-dir on sys.path[0]). A
    code-path that imports clean in one launch mode can be fatal in another — test the actual ExecStart.
  - **★ FRESH-EYES critic (separate agent, inspector screenshot):** VALIDATED the change (did not flag "Field" as machine). Its
    real findings are OTHERS' lanes / intentional: (a) `routine:self_status` machine summary + `[how-to @ ui://canvas]` raw address
    = operator-law leaks in the inspector — event-summary content + the context-item leak already flagged (commit 7edca62), NOT my
    lane → re-flag to composition/fork; (b) the "0.99" raw value + terse "in" label — the `num` is INTENTIONAL (Disclosure's law:
    "plain words + the REAL value", Tim's design) → not a leak; the "in"-label clarity is a lens-aware refinement → NEXT.
  - **COORDINATION:** composition ratified the label; lead ACCEPTED the HOST/TAKE conflation fix (projection=HOST, wildcard=TAKE)
    and called /api/territory "the proof the resolution-first constraint is real in the build"; fork given the relations root-cause.
  - **NEXT:** the "in"-label clarity (lens-aware: "kind"/"family"/"lens" instead of bare "in"); re-flag the inspector summary+howto
    leaks; DRIVE / open-source-on-SECTOR once Tim's verb-PLACEMENT steer lands; DNA's decision-card reuses /api/territory; TUTORIAL gated OQ3.
- **2026-06-18 — ✅ the V fan tells the truth: LIVE verbs vs "SOON" (no green-paint) + draft verb descriptions (commit `ca2e08c`).**
  The fan answered ② "what can I do here?" DISHONESTLY — all six verbs looked alike, but Drive + Make only Notice "coming next"
  (drive waits on Tim's verb-PLACEMENT steer + a dialable aim — corpus points have no dial; Make is wildcard's gated keystone).
  A stranger tapping "Make" hit a dead-end = half-done-presented-as-done. Fixed:
  - **LIVE** (Go to / Ask / Note / See the record) render solid; **NOT-YET-WIRED** (Drive, Make) render MUTED (faint ink + a
    DASHED provisional border) + a readable **"SOON"** status chip; still tappable → the honest "… is coming next." Notice (no
    silent no-op). The `live` flag is a runtime fact the host knows → the chip drops automatically when each verb wires up.
  - **★ BUG caught by use:** muting via `opacity:0.5` read as opacity **1** live — the `vhandle-pop` animation holds opacity:1
    (fill `both`) and overrides a static opacity. Re-did the mute via colour/border (dashed + faint ink), which the animation
    doesn't touch. (Same class of "the animation wins" gotcha worth remembering.)
  - Each verb carries a DRAFT one-line description (operator-law plain words, TENTATIVE) on title/aria — desktop hover tooltip +
    screen-reader name. **VERIFIED BY USE both viewports** (390 first): 4 solid + 2 dashed-SOON; tapping Drive → the honest Notice.
    tsc 0, design-lint 0/0. Tim's radial thumb-fan preserved.
  - **★ FRESH-EYES critic (separate agent, phone screenshot):** validated the soon-marking (sets expectations), and flagged THREE
    things that are the REAL V component's PRESENTATION (composition's lane — I did NOT redesign the placeholder for them, per
    "V=placeholder, real V swaps in"): (a) the PHONE has no hover → my title/aria descriptions are invisible there → bare verbs
    ("Go to"/"See the record") read opaque on the priority device — the real V needs touch-visible descriptions; (b) live/soon
    interleave (Make top, Drive middle) — group live-first/soon-last (composition's contract order); (c) the fan floats over the
    busy wheel + the radial stagger is hard to scan. → flagged ALL THREE to composition + supplied my draft description copy for
    their verb table. HONEST GAP: a phone stranger still can't read what "Go to"/"See the record" DO pre-tap (labels = composition's
    ratified contract; touch-visible descriptions = the real V's design) — not green-paint (soon-state is honest), but a real
    ROOT-bar gap owned by composition.
  - **COORDINATION:** flagged composition (V-component presentation + draft desc copy).
  - **✅ RELATIONS-BUG LOOP CLOSED (this fire):** fork landed the rename `runtime/lifters.py → runtime/lifter_registry.py`
    (86cd7c4, killing the shadow). I VERIFIED IT LIVE the way that matters (`company restart bridge` + curl — NOT an import
    check): bridge starts clean (6s); `run://corpus/...` → legs.relations=TRUE, notes=[] (ModuleNotFoundError GONE), edges_in=0
    (correct); **`board://item-...` → edges_in=4, edges_out=1** (provenance populates end-to-end). So territory_for's relations
    leg is alive for EVERY consumer — the RHM's brain-turn context (bridge.py:1697) now carries typed-edge provenance, and the
    Source verb's "Referenced by N" line works (silent for corpus points = correct, real for board things). Confirmed to fork.
  - **NEXT:** the "in"-label clarity; re-flag the inspector summary+howto leaks;
    DRIVE / open-source-on-SECTOR once Tim's verb-PLACEMENT steer lands; DNA's decision-card reuses /api/territory; TUTORIAL gated OQ3.
- **2026-06-18 — ✅ V fan conformed to composition's RATIFIED order+copy (commit `7dce89c`) + ✅ operator-law: the inspector's context items never show a raw machine address (commit `0ae6064`).**
  - **✅ Beat A — V-fan order+copy (RATIFIED by composition, thread t-1781706789):** display order → live-first, read→write arc:
    **Go to · See the record · Ask · Note · Drive(soon) · Make(soon)** (4 live lead = thumb-reach; 2 soon trail together —
    resolves the fresh-eyes interleave). Descriptions → canonical wording ("Re-centre the view on this", "Open the full record
    behind this"). A fresh-eyes RE-CHECK confirmed the grouping reads at a glance (usable-vs-coming clear; boxed SOON = "later",
    not "broken"). Verified both viewports. composition RULED the touch-visible-descriptions + scrim + fan-header are the REAL V's
    presentation (their lane) → I kept the placeholder honest, did NOT redesign; flagged the additive findings (header, SOON
    wording, order-direction) for their backlog.
  - **✅ Beat B — context-item operator-law guard (commit `0ae6064`):** the inspector's context section showed
    `[how-to @ ui://canvas] WHAT: …` — a raw ui:// address in operator-facing text. Reframed CORRECTLY: the R2 text legitimately
    carries the address FOR THE BRAIN (suite.py composes it; fed to the RHM via territory_prose) → the fix is the RENDER boundary,
    not upstream (the brain wants it). New `humanizeCtx()` in Disclosure strips a composed `[label @ scheme://addr]` frame + any
    bare `scheme://…` token; the useful content stays ("WHAT: the canvas — the live board…"). VERIFIED BY USE both viewports:
    `hasAddr=false` at 390 + 1440. (This beat's verify was by-use — the address is provably gone; the fresh-eyes this fire was on
    the fan. Root-correct, not a band-aid: the surface translates for the operator, the text keeps the address for the brain.)
  - **✅ RELATIONS-BUG fully closed + acknowledged by fork** (last fire's live verify holds — territory_for's provenance leg alive
    for every consumer). fork flagged a LATENT PATTERN (noted, NOT biting): `roles/`·`skills/`·`mark_types/` have the same
    module-shadows-package shape as lifters did; harmless today (the bridge never `from roles.X`), but if any bridge-path code ever
    package-imports a registry-rows dir it'll hit the identical shadow → the fix is the same (rename the registry module).
  - **HONEST / still open (others' lanes):** the `routine:self_status` event SUMMARY in the inspector is machine-ish — but it's
    CAPTURE-side content (the routine's own output), not the render boundary; humanizing it = fabrication → flagged, not mine.
  - **NEXT:** the "in"-label clarity (needs the binding to DECLARE a division-noun — composition's registry, not an FE hardcode —
    flag it); DRIVE / open-source-on-SECTOR once Tim's verb-PLACEMENT steer lands; composition's real-V presentation (touch-visible
    descriptions); the decision-surface bridge-route once the lead sequences it; TUTORIAL gated OQ3.
- **2026-06-18 — ✅ operator-law: stripped ML jargon from the meaning-reading controls (Layer/Res/Quant chips) (commit `12d8cf6`) + signalled the lead projection is ready for decision-surface sequencing.**
  The three "how meaning is read" chips leaked raw ML terms to the operator (the clearest remaining operator-law violation in
  the chrome): LayerChip "the embedder layer — which embedding you look through"; ResChip "how many vector dims … (MRL zoom)";
  QuantChip "full float (cosine) or binary sign-bits (Hamming-geometry)". Translated the instrument-authored copy → human PURPOSE
  ("How it reads meaning" / "How finely it reads meaning" / "How meaning is compared"), TENTATIVE for Tim's steer. QuantChip values
  full·float→"Full", binary·Hamming→"Coarse".
  - **★ CAREFUL not to mistranslate (blast-radius × reversibility — a MISLEADING human label teaches wrong, worse than honest
    jargon):** the code's own measured note says binary is a coarser GEOMETRY, NOT a speed win (the resolution picker is the speed
    lever). So "Coarse", never "quick". The subtle/risky translations I did NOT guess (see flagged).
  - **VERIFIED BY USE both viewports** (Meaning lens): all three tooltips jargon-free (regex-checked: no embed/MRL/dims/float/
    cosine/Hamming/sign-bit/vector); QuantChip drives Full↔Coarse live (chip → "▦ coarse"). tsc 0, no CSS.
  - **★ FRESH-EYES critic (separate, phone):** confirmed my tooltip fix is DESKTOP/screen-reader only — on the phone (no hover)
    the chip VALUES stay opaque ("◫ default · ◎ full · ▦ coarse" + abstract glyphs = "mystery settings I'd be afraid to touch";
    the ◎ bullseye misreads as 'focus'). Its actionable fix = put the DIMENSION-NOUN on the label ("Detail: Full"/"Grouping:
    Coarse"). FILTERED: this is the SAME phone-no-hover pattern composition owns for the V verbs → flagged for ONE consistent
    phone-label treatment (NOT unilateral chrome churn: the chrome already wraps 2 lines at 390, and Tim's model-experimentation
    intent [[native model layer]] wants these accessible, so NOT expert-gated). Also flagged composition: registry human-NAMES for
    embedder layers (so "◫ default"/"pplx" read human) + the binding division-noun for the "in"-label — both registry-true, their lane.
  - **★ READINESS SIGNAL to lead:** projection's unblocked surface has CONVERGED (V placeholder, inspector, Source/relations, chip
    legibility). The remaining in-lane items are gated (drive=Tim's placement) or owned-elsewhere (real-V presentation, registry
    names). Signalled the lead I have capacity for the DECISION-SURFACE host/bridge-route the moment it's sequenced (HOST + /api/
    territory shipped + /api/cognition + recollection's "bridge route" memory leg) — rather than spin on polish.
  - **NEXT (mostly awaiting others):** decision-surface host/route (lead to sequence); DRIVE/source-on-sector (Tim's placement);
    composition's real-V touch-labels + registry human-names (layers, division-noun); TUTORIAL gated OQ3.
- **2026-06-18 — ✅ the LEAD SEQUENCED the decision-surface build (projection = stream #4, the HOST); I DESIGN-CONFIRMED projection's seam (no code beat this fire — honest: the foundation isn't there to build against yet).**
  The lead sequenced (thread g-1781731059): composition's 3 TYPES gate the rest (the long pole, starting now) → fork (scheme+keystone) →
  DNA (render) → **projection #4** → wildcard (take) → recollection (memory). The lead asked each stream to design-confirm its seam then
  build IN ORDER. So projection's correct move NOW = design-confirm (not a hollow build on not-yet-existing types — that would fail the
  real-data bar + jump the sequence).
  - **★ EVIDENCE-BACKED design-confirm:** PROBED `/api/territory` on a `decision://` address → degrades CLEAN (no crash; scheme
    unregistered → honest "no content-resolver yet" note; relations leg works). So projection's RESOLVE leg is decision-READY with ZERO
    net-new — the moment fork registers the decision:// scheme, /api/territory carries the full resolution. The resolution-first payoff:
    the same resolver/host serve the new type. projection's piece is NEARLY ZERO net-new (HOST + /api/territory already cover SHOW+RESOLVE).
  - **3 SEAM Qs broadcast (g-1781731457) to pin the small residual:** (1) fork — is the /api/cognition explain-wire me-routing-your-brain
    or you-provide-it? (2) recollection/fork — fold the recall into territory_for (→ /api/territory carries it, zero new route) or a
    recall:// scheme (→ projection routes it)? (3) DNA — decision-slide via renderGallery (existing host) or a new slide path (new mount)?
  - **HONEST — why no code commit this fire:** every projection net-new piece needs (a) composition's types (#1, gating), (b) a render
    consumer (DNA #3), or (c) a seam answer — building any now = hollow (no real data, nothing to drive) + out-of-order. The design-confirm
    IS the lead-requested productive step; I build the residual the instant the foundation + answers land. NOT spinning on polish, NOT
    hollow-building — waiting correctly on the sequenced foundation with my seam pinned.
  - **NEXT:** build projection's residual (explain-wire / memory-route / host-mount — whichever the seam answers leave) when composition's
    types + the 3 answers land; meanwhile the V/inspector/chip legibility is converged + the registry-name + Tim-placement items sit with their owners.
- **2026-06-18 — ✅ ALL 3 seam answers IN (projection's decision piece confirmed ~zero net-new); ✅ ran the FIRST task-scoped END-TO-END stranger test → found the #1 operator gap (DNA's drill-face), escalated. Honest: no projection code beat (the gap is DNA's RUNG-C; my data's shipped; the host's gated on types).**
  - **SEAM ANSWERS (thread g-1781731457) — all confirm projection ~ZERO net-new:** (1) explain-wire = REUSE fork's brain turn
    (/api/claude/turn / forkBrainCore.talk with the decision address — DNA's render calls it; projection adds nothing); (2) memory =
    FOLD recall into territory_for as a guarded leg (recollection drafts, fork applies) → /api/territory carries it FREE; (3) host-mount
    = REUSE GalleryMount + renderGallery (DNA resolves decision:// via my /api/territory, RUNG-C renders, mounts in the existing host,
    the slide-walk re-renders one container). I DECIDED the window-event = REUSE `gallery:rendered` (per lead's reuse steer) + owned a
    lifecycle note (decouple the decision-slide's close from wheel-deselect — I verify/harden that against DNA's REAL render, not a stub).
    So projection's decision residual is genuinely ~nil; I build/verify the instant composition's types + DNA's render land.
  - **★ TASK-SCOPED END-TO-END TEST (the advisor's reserve, warranted as the build-wait stretched — verify-by-use, not research):**
    drove the surface cold on a phone against a stranger's GOAL ("find what the company's been doing, understand one thing"), fresh-eyes
    judged the WHOLE journey (E1/E2/E3 screenshots). VERDICT: goal technically reachable, PRACTICALLY UNREACHABLE for a stranger:
    • E1 cold open — WORKS (the legend reads human; a stranger forms a plan: tap a dot).
    • ★ E2 tap-a-dot (the PRIMARY path) — BROKEN: DNA's gallery FACE; the panel titled "What this is" answers with GLYPHS (★✓✕?☆→),
      no words. ROOT-bar failure on the most common action. (The face I flagged ~5 fires ago — still unfixed.)
    • E3 V→"See the record" — WORKS (my legible Source) but "buried behind a mystery button most first-timers won't discover."
  - **★ THE FINDING (what the test was FOR — redirects the build):** the #1 operator gap is NOT my polished components — it's DNA's
    drill-FACE, and it's the SAME RUNG-C render gap the decision-surface needs (DNA's "build once, three payoffs"). So RUNG-C is doubly
    urgent: it fixes the #1 operator gap AND the decision-card. The data is READY (kind_name+kind_meaning on every point + /api/territory).
    projection's lane = ZERO net-new (data shipped; the face is DNA's render) → escalated the PRIORITY to lead+DNA (g-1781732544) + the
    naming-inconsistency (E2 thing-name vs E3 kind) to composition (one registry-declared legibility `name` both surfaces render).
  - **HONEST — no projection code commit this fire:** the #1 gap is DNA's render (not my lane); the decision host is gated on composition's
    types; the naming-name is composition's registry. Forcing a projection code change = hollow/wrong-lane. The test (verify-by-use) +
    the escalation IS the high-leverage work — it proved the next real beat is RUNG-C, not more projection polish. Sent Tim the journey.
  - **NEXT:** when RUNG-C lands (DNA), re-run the end-to-end stranger test to confirm the primary path now reads human; build projection's
    decision residual (likely just the gallery:rendered host + the lifecycle-decouple) the instant composition's types + DNA's render land.
- **2026-06-18 — ✅ CODE BEAT (unblocks the #1-gap fix): fed DNA's RUNG-C a meaning-SOURCE — kind_name/kind_meaning/summary now ride on the `projection:select` detail (commit `368e631`).**
  The lead sequenced RUNG-C (DNA's lane) as the leading edge + said "projection: hold, data's shipped." Before holding, I PROBED whether
  DNA's render-path actually RECEIVES the meaning — and found a real blocker in MY lane: it doesn't. Neither /api/territory nor
  /api/cognition/corpus carries kind_name/kind_meaning, and the projection:select detail (DNA's face open-trigger) carried only the machine
  `kind`. So "the data's shipped" was HALF-TRUE — the human meaning rode on the projection POINTS but never reached the face. RUNG-C
  literally couldn't render "What this is" in words without a meaning-source.
  - **FIX:** the `projection:select` detail now carries `kind_name` + `kind_meaning` + `summary` alongside the address/kind. DNA reads
    detail.kind_meaning (lead) + kind_name (heading) + summary → "What this is" in WORDS. No extra resolve, no new endpoint (the face already
    receives this event). Interim source (projection's kind-registry legibility); maps onto composition's canonical legibility name/is when
    that registry lands. VERIFIED BY USE: drove a real corpus-point pick → detail = {…, kind:'corpus.record', kind_name:'A note saved',
    kind_meaning:'The system wrote something into its memory.', summary}. Data-contract change (viewport-independent; no FORM/CSS — the
    operator-visible render is DNA's, fresh-eyes-judged when RUNG-C ships). tsc 0. Told DNA (thread t-1781733363).
  - **★ WHY THIS, not "hold":** the lead's "data's shipped" assessment missed that the meaning never reached DNA's render-path — a probe-by-
    use caught it. This is the opposite of filler-polish: it's the one piece of MY data-plumbing that genuinely gates the #1-operator-gap fix.
    Found by NOT taking "hold" at face value + verifying the actual seam.
  - **DECISION-SURFACE seams all settled:** Q1 explain = reuse fork's brain turn; Q2 memory = fold into territory_for (free); Q3 host = reuse
    GalleryMount + gallery:rendered (DNA confirmed the source-keyed lifecycle decouple — key on detail.source==='decision', deferred to the
    real render). projection's decision residual ~nil, gated on composition's types + DNA's render.
  - **NEXT:** DNA renders meaning-first off the new detail fields → re-run the end-to-end stranger test to confirm the primary path reads
    human; build the decision residual when types + render land; carry composition's canonical legibility name/is when its registry lands.
- **2026-06-18 — HOLD + ✅ verified meaning-source coverage complete + ★ NUDGED the critical path (RUNG-C shouldn't gate on Tim).**
  Probe-by-use: RUNG-C NOT landed yet (the face still shows glyphs, not the meaning-words — DNA building). Verified the meaning-source is
  COMPLETE: all 11 live kinds carry good kind_name+kind_meaning (not just the one I tested) → DNA's RUNG-C render has real meaning for every
  kind. projection's parts (host, /api/territory, the select-detail meaning-source, the window-event decision) are shipped + complete; the
  active build (RUNG-C) is DNA's.
  - **★ CRITICAL-PATH NUDGE (advisor-caught — the real action this fire):** DNA said it's "escalating to Tim NOW for the go" on RUNG-C, but
    the sprint is explicit — do NOT gate on Tim; git-revert is the safety. RUNG-C is reversible, the live #1-gap fix, AND the decision-surface
    gate; parking it on an absent "go" stalls the whole critical path. So I nudged DNA+lead (g-1781733996): RUNG-C is buildable NOW (revert
    covers the FORM), zero-cost status check. Keeping the critical path moving once my part's shipped = reactive coordination, not filler.
  - **WATCH (not a beat now):** `corpus.record` is >half the dots; my kind-meta renders "A note saved" — borderline for a comprehended
    role's-principles (name-vs-thing slippage). The per-instance name is composition's `name` lane; but when RUNG-C lands + I re-run the
    stranger test, if "A note saved" misreads the majority, tuning the kind-MEANING is mine.
  - **NEXT:** await DNA's RUNG-C (nudged) → re-run the end-to-end stranger test; build the decision residual when types+render land.
- **2026-06-18 — ★★ THE #1 OPERATOR GAP IS FIXED + VERIFIED LIVE. RUNG-C landed (the nudge worked); I synced it into the surface + re-ran the stranger test → the primary path reads HUMAN.**
  The nudge worked: the lead CONCURRED (RUNG-C builds now, no Tim-gate — "the exact over-gating Tim corrected"), and DNA SHIPPED the meaning-first
  "What this is" render (reads kind_name/kind_meaning/summary off the projection:select detail I ship, commit 368e631). My build-trigger fired:
  - **★ projection's host action (its lane): synced DNA's render into the surface.** My instrument serves window.DNA from a COPY at
    public/gallery/ (gitignored, regenerated by surface/app/scripts/sync-gallery.mjs predev/prebuild from DNA's counterpart/design/ui/). My
    dev server predated DNA's edit → the copy was stale (still glyphs). RAN the sync manually → pulled DNA's new unit-view.js (25231B) → reload.
  - **VERIFIED BY USE + FRESH-EYES re-test:** tap a dot → "What this is" now reads "A note saved" (title, retiring the jargon) + "The system
    wrote something into its memory." (meaning leads), glyphs after. Fresh-eyes verdict (same stranger goal): "the one thing that made this
    screen useless — no plain words — is GONE; the goal is reachable now; the #1 failure is RESOLVED, not partly." The E2 ROOT-bar failure my
    first end-to-end test found is CLOSED. BEFORE/AFTER sent to Tim.
  - **★ COMMIT-COORDINATION (raised to DNA+lead, g-1781734536):** public/gallery/ is GITIGNORED (regenerated every build from DNA's repo =
    registry-of-truth), so projection commits NOTHING here; DNA's render is in their WORKING TREE only → a clean/prod build would lose it.
    Per the sprint (commit + git-revert) I told DNA to COMMIT their source. (projection no code commit this fire — the synced copy regenerates;
    the meaning-source App.tsx was last fire's commit.)
  - **REMAINING (POLISH, relayed — none block the goal):** DNA — tuck the annotation glyph rows fully AFTER the words + fix a glyph row's "…"
    (reads like truncation); composition — the per-instance `name` + a content hint (the meaning's generic = the kind, the specific is behind
    "Open the source"). The corpus.record "A note saved" watch-item: fresh-eyes found it READS TRUE enough for orientation (not misleading) — no rename.
  - **NEXT:** the decision-card render (next RUNG, when composition's types land — same lyRender, projection's host + /api/territory + select-detail
    meaning-source all ready); then the lifecycle-decouple (source==='decision') when the real decision-slide exists.
- **2026-06-18 — ✅ #1-gap fix made DURABLE (DNA committed) + verified; HOLD on the next rung (decision-card, gated on composition's types).**
  Lead confirmed the milestone + made DNA's commit the durability gate. Checked: DNA committed RUNG-C (counterpart/design `ad8a043`), tree clean.
  Verified the surface sync reproduces it — re-ran sync-gallery.mjs from DNA's COMMITTED source → public/gallery/unit-view.js byte-IDENTICAL to
  the committed file → a fresh build/checkout regenerates the human-reading render (NOT stranded). So the #1-gap fix is durable end-to-end.
  Confirmed to lead (t-1781734850). Per my rule (unblocked beat → build / critical path stalled → nudge / neither → short hold): NEITHER —
  the next rung (decision-card) is composition's-types-gated, the lead's driving the long pole, and projection's pieces are all READY + verified.
  So I HOLD with everything staged; the types landing + fork registering decision:// triggers my piece (DNA's same lyRender renders the card
  through my host → I re-run the stranger test on a real pending decision). No projection blocker remains.
- **2026-06-18 — ✅ RE-AIM (③ "where can I go") stranger test → two projection-lane legibility fixes shipped: the legend tells the truth after Go-to (`515e9fe`) + the centre chip says what-it-is/how-to-exit (`3d4bac1`).**
  Held on the decision-card gate (composition's types, lead-driving) — so I ran the task-scoped stranger test on the UNTESTED axis ③ re-aim
  (Go to / re-centre), in projection's lane (not the known V-phone gap). It found two real gaps + confirmed one composition item:
  - **★ Beat A — the legend MISDESCRIBED the re-centred view (`515e9fe`):** after Go-to, radius_from flips to 'address'/'semantic' (radius =
    distance from the centred thing), but the Legend kept rendering the binding's static declared `meta.is` — the UN-centred default ("how far
    = how long ago, the centre is now"). So the legend actively lied about what the stranger was looking at. FIX: when a centre is set, use the
    centre-AWARE computed describe() (reads live radius_from + the centre), not the stale static meta. VERIFIED both viewports: re-centred →
    legend reads "radius · distance from voice.py"; un-centred → still the default meta. CentreChip + legend + inspector now all agree.
  - **★ Beat B — "I feel TRAPPED" (`3d4bac1`):** the fresh-eyes #1 follow-up — after re-centring, the only way back was a tiny unlabelled ×
    (the whole chip reset, but a stranger couldn't tell; tooltip was hover-only jargon "return to the root origin"). FIX: the chip now reads
    "⊙ Centred on <thing> · show all ×" (a "Centred on" state-prefix + a plain "show all" exit) + a plain tooltip/aria. VERIFIED both viewports:
    Go to → chip reads it; tapping → centre clears, legend back to default. The re-aim→undo loop is now stranger-legible. tsc 0, design-lint 0/0.
  - **FRESH-EYES (separate, phone): confirmed both fixes land** + flagged the remaining: (a) the centre LABEL is a FILENAME ("voice.py" + "1.00"
    + "structural" "reads as developer internals, breaks the live-map story") → the LABEL is composition's per-instance legibility `name` lane
    (projection renders the human name when present; corpus units carry none today → the leaf fallback) — flagged to composition (t-1781736317),
    same field-set RUNG-C proved; (b) "1.00"/"structural" in the inspector distance row are MINE → plain-word next; (c) no transition cue when the
    rings change meaning (legend now updates, but silent) — a secondary enhancement.
  - **NEXT (mine):** plain-word the inspector's "structural from X / 1.00" distance row; (composition) per-instance `name` closes the filename
    label; the decision-card render when composition's types land (all projection pieces staged + verified).
- **2026-06-18 — ✅ operator-law: the re-centred inspector distance row reads "filed · close by from X" not "structural … 1.00" (commit `d2d8d4c`).**
  Cleared my own queued NEXT (the re-aim test's mine-to-fix item). The decision-card is HARD-GATED: composition won't author the 3 types
  without Tim's EXPLICIT scope word (a 5-stream cascade on the flagship = principal-level confirm, not a routine GO; Tim away; the lead can
  only clear it WITH Tim's word). So I built the unblocked in-lane fix.
  - Traced the value (projection.py: address-centre r = tree_distance/max = normalized FILING-tree distance) → accurate plain words near/mid/far
    "in how it's filed" (NOT a mistranslation — filing-distance, mirroring the semantic row's close/mid/far). KEPT the real value in `num` (did
    NOT drop the number on one row only — respects Disclosure's "plain words + the REAL value" law + row consistency; the show-raw-nums-at-all
    question is a Disclosure-wide design call, not a piecemeal override). VERIFIED both viewports: "filed · close by from voice.py 0.20", no jargon.
  - **STATE:** the re-aim (③) journey axis is now fully stranger-legible end-to-end (legend-after-Go-to ✓, centre-chip-not-trapped ✓, distance-row
    plain ✓). The remaining re-aim item — the filename centre LABEL — is composition's per-instance `name` (gated with the types).
  - **NEXT:** decision-card render the instant composition's types land (Tim's scope-word clears it; all projection pieces staged); meanwhile the
    operator surface's three journey axes tested so far (understand-a-thing ①, controls ③-act, re-aim ③) all read human.
- **2026-06-18 — ✅ JOURNEY LEG 6 (coming back — time + state): the legend tells the time-truth in the past (commit `cfbda88`).**
  Decision-card still HARD-GATED on Tim's scope word (composition won't cross; lead can't clear without Tim; Tim away) → ran the stranger test
  on the next untested journey leg (6 — the time scrubber), projection's lane.
  - **FUNCTION verified first (no bug):** dragging back genuinely shows the past — `at=` filters future events (past view ts-range Jun7–Jun9 vs
    now Jun13–17; futureEventsInPastView=0; count 600→454). The mechanism is sound.
  - **★ THE GAP (legibility): nothing told the operator they were in the PAST.** Scrubbed to Jun 5, the legend still read "A live map … the
    centre is now" — actively claiming live/now while showing history (same misdescription class as the re-centred-legend bug). FIX (mirrors it):
    when s.at is set, bypass the static "live/now" meta → the computed describe() LEADS with "showing the company as of <human moment> — what had
    happened by then" + "radius · age (centre = that moment)". Human moment via toLocaleString (operator-law, never ISO).
  - **VERIFIED both viewports + FRESH-EYES:** live → "A live map …"; scrubbed → "showing the company as of Jun 9, 11:07 AM…" (no live/now claim);
    the "now" button returns to live. Fresh-eyes verdict: "the loop is complete and self-explaining — a stranger can time-travel back, knows
    they're in the past, and knows how to come home." Remaining = pure wording polish ("as of"→"rewound to"; "now"→"back to now") — captured, non-blocking.
  - **STATE:** FOUR journey axes now tested + stranger-legible — ① understand-a-thing, ③-act controls, ③ re-aim, ⑥ coming-back/time. Untested: 0
    (first-contact cold — likely strong, the legend reads well) + 2 (something-catches-the-eye, ≈ ①). The operator surface's core loop reads human.
  - **NEXT:** decision-card render when types land (staged); optional — the wording-polish pass + a leg-0/2 stranger test if the gate stays closed.
- **2026-06-18 — ✅ THE FULL COMPOSITE END-TO-END STRANGER JOURNEY — the four piecemeal fixes COHERE as ONE continuous, reversible experience (verification only; no code committed — correctly).**
  Decision-card still HARD-GATED (composition is the SOLE gate: won't author the 3 types without Tim's EXPLICIT scope word — a 5-stream cascade on the flagship = principal-level confirm; she put the scope-Q to Tim directly; Tim silent; the lead can relay-clear it the instant Tim says one line). Per the advisor: instead of testing the two remaining ISOLATED legs (0 cold, 2 catch-eye), ran the ONE composite run that subsumes them AND tests the untested part — the SEAMS between my four fixes (do they feel like one experience or four patches?). Drove all 6 moments live, in flow, at 390 then spot-checked the compound state at 1440.
  - **★ NEW THIS FIRE: RUNG-C is now LIVE on MY surface.** DNA's committed render (ad8a043) is synced into `public/gallery/` — so the composite run exercised the FIXED "What this is" for real: tap-a-dot → title **"A note saved"** + meaning **"The system wrote something into its memory."** — WORDS, the #1-gap fix rendering on the primary path through my host.
  - **THE COMPOSITE (all transitions cohered + reversed cleanly):** ① cold open reads human (legend: "A live map of everything the Company is doing… how far = how long ago, the centre is now"); the gold V is the catch-the-eye. → ② tap a dot → RUNG-C words (above). → ③ Go to (⊙ centre here) → ALL THREE re-aim fixes fire together: chip "⊙ Centred on <thing> · show all ×", legend "radius · distance from <thing>", inspector "filed · far from <thing> 0.97". → ④ rewind the time scrubber → COMPOUND STATE reads correctly: legend LEADS "showing the company as of Jun 8, 5:24 PM — what had happened by then" AND keeps "radius · distance from <thing>" (time-state + re-aim-state coexist coherently). → ⑤ "now" button → the as-of line cleanly removed, centre preserved. → ⑥ "show all ×" → full reset to the exact cold-open default (legend back to "how long ago", chip gone, scrubber live). **No stuck states, no stale descriptions — the legend/chip ALWAYS tell the truth about the actual state. The state machine (centre × time × selection) is sound.**
  - **VERIFIED BOTH VIEWPORTS.** 390: the full 6-moment drive (screenshots C1–C5). 1440: re-aim compound state (C6) — FORM adapts cleanly (chip→top bar, inspector→right rail, legend top-left, no overlap); findings identical (viewport-independent meaning-logic, as expected).
  - **HOLISTIC JUDGMENT on the small in-lane dings the composite surfaced (advisor: judge once, don't fix piecemeal):**
    - the naked value ("far from X · 0.97" / "long ago · 1.00") → **KEEP** — it's Disclosure's "plain words + the REAL value" law working, not a bug; the show-raw-nums-at-all question is a Disclosure-WIDE design call, not a solo-rushable piecemeal override.
    - the title "What's happening — the live activity" still says "live" while the body says "as of [past]" → small structural tension (the body clarifies; the title = the binding label). Captured, non-blocking.
    - the inspector's HOWTO context item leaks UI jargon ("the canvas — the live board the whole composition sits on… semantic zoom") → that's CORPUS CONTENT (real data), not my render to rewrite; humanizeCtx strips addresses, not data-jargon. Captured (it's a context-source flavour issue, possibly cross-lane), not a surface fix.
  - **★ ROUTED (cross-lane, with evidence):**
    - **DNA** — answered their EXPLICIT open question ("where do the glyph rows come from — V sockets or wildcard?"). Live-DOM evidence: it's DNA's OWN `div.annotation-strip` (`button.annotation-icon.favour-btn` ★ + `span.reaction-row` stamps ✓✕?☆→) attached to EVERY `.annotatable` node (`.ttl.annotatable` + the meaning line) INSIDE `.screen.uv` — NOT the V sockets, NOT wildcard. They render as prominent boxed buttons bracketing the meaning sentence (polish #1) and one reaction-row ends in "…" (polish #2). This unblocks DNA's polish pass (place glyphs AFTER the words).
    - **composition** — the centre LABEL is still the machine leaf (a `.py` filename, or a bare machine id like "judge_drift") AND the SAME thing reads "A note saved" in the sheet but "judge_drift" in the chip/legend (one-screen inconsistency). The advisor's clarity: do NOT solo-patch this with kind_name — a centre label must IDENTIFY the anchor ("distance from A note saved" names no specific point; every note is "A note saved"). That's exactly why composition reserved a per-INSTANCE `name`; she explicitly ruled the leaf "correct… today". Routed as a one-liner for HER call (interim generic floor vs hold for per-instance name); not re-decided solo.
  - **★ HONEST FLAGSHIP STATE:** this fire is journey VERIFICATION + cross-lane routing — **NOT decision-surface (flagship) progress.** The flagship is frozen on Tim's scope word; a run of green journey-checks must not read as the main build advancing. Phase 0 (the operator journey) is now verified end-to-end as ONE coherent experience; the flagship remains staged-and-waiting (all projection pieces ready + verified).
  - **NEXT (if the gate stays closed):** the untested DOING axis — the V's own legs **Ask** (brain panel) + **Note** (composer) end-to-end stranger test (the looking/navigating axes are now done); else the decision-card render the instant composition's types + fork's decision:// land.
- **2026-06-18 — ✅ DROVE the DOING axis (V's Ask + Note) as a stranger → shipped a real in-lane fix (the Note round-trip, commit `82a8eb3`) + found a serious Ask break (routed to fork with full diagnosis).**
  Flagship still HARD-GATED (composition = sole gate, awaiting Tim's scope word; no movement). Per the advisor: don't build onboarding signage (it pre-empts OQ3 + the RHM-as-guide architecture); instead drive the untested half of the journey — the V's own legs — and fix what surfaces. It surfaced real things on both legs.
  - **★ FIX SHIPPED (mine) — the NOTE round-trip was broken (write-only) → now closed.** Drove Note at 390: composer reads human ("Note about: this part of the surface" / "Leave a note about this…"), empty-guard works (Save disabled until text), Save → "Noted ✓" → auto-close. The note PERSISTED (suite.marks_for confirms). BUT `/api/territory` returned `notes: []` despite the mark existing → traced: `territory_for`'s `notes` field is a DIAGNOSTIC channel (leg-unresolved messages), NOT operator notes; the operator's comment/reaction/favour marks are read by a SEPARATE fn (`territory_directions_at` / suite.marks_for) that `/api/territory` never called. So a note was written but invisible — "See the record" could never show it back. FIX: `/api/territory` now folds in the operator's directions (operator-SAFE fields only — type/value/source/when; raw `target` address omitted, operator-law); `api.ts` types it; `SourcePanel` renders them under "The note you left here"; `App.tsx` populates them. VERIFIED BY USE BOTH viewports: wrote a note at a real thing (`…voice.py/principles`, "A note saved") → "See the record" → the note reads back in its own card, distinct from the system's "What's in it" content. Fresh-eyes critic PASS (note clearly theirs, no jargon/leaks, clean form) — its one nitpick ("Your note here" reads like a placeholder) FIXED → "The note you left here". tsc 0, design-lint 0/0. Files: `runtime/bridge.py`, `surface/app/src/lib/api.ts`, `surface/app/src/source/SourcePanel.tsx`, `surface/app/src/App.tsx`, `surface/app/src/source/source.css`.
  - **🔴 ROUTED TO FORK (Ask leg broken for a stranger — fork's brain lane; I traced the roots from the live `claude -p` command):** drove Ask cold ("What am I looking at? I've never seen this before"). The panel header reads human ("Ask about: this part of the surface", no leak) BUT the REPLY: *"Tim is pointing at a part of his interface — internal handle `ui://instrument/surface` — and asking what it is… Let me investigate the codebase."* Three real bugs: (1) **third-person voice about Tim** ("Tim is pointing… explain it to *him*") — root: `PANEL_BRIEFING` (ui_claude_session.py:42-53) refers to the operator as "he/him/Tim" throughout, so the model mirrors it; (2) **RAW ADDRESS LEAK** — "`ui://instrument/surface`" dumped into the reply despite the briefing forbidding it — root: `territory_prose` (territory.py:184) puts the raw address in the context block "for you, never shown" and the model parrots it; (3) **`--permission-mode plan` + thin surface-aim context → a slow codebase investigation that never streams a final answer** (two `claude -p` procs ran for minutes, no answer). Proposed to fork: rewrite the briefing to SECOND person + answer-from-provided-context-first; drop the raw address from the operator-context prose (the model can't echo what it isn't given). Fork's lane (brain UI + turn execution); the slow/hanging turn also blocks by-use verification of any briefing fix from my side.
  - **🟡 FOUND (addressless points degrade the V to the surface):** tapping a point with NO resolvable address (e.g. "A session went quiet" — agent_sessions; `address` & `source` both empty) dispatches `projection:select` detail=null → RightHand's `setAim` falls back to SURFACE_AIM → the V's Ask/Note/Source all silently aim at "this part of the surface", not the thing the operator tapped. So a note on such a thing lands on the surface, and Source rejects it (isThing=false). Points WITH an address aim correctly (verified). The fix is upstream: every point should carry SOME resolvable address (projection.py) — flagging to investigate next (mine), so the V's legs never silently mis-aim.
  - **NEXT:** investigate why some points lack a resolvable address (projection.py — so the V never silently mis-aims); the decision-card render the instant composition's types + fork's decision:// land (all projection pieces staged); fork to fix the Ask brain (routed).
