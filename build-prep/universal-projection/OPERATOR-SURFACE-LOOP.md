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
