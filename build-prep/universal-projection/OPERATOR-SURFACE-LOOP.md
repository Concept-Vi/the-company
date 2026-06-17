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

## THE PHASES (sequenced so the loop can't build on sand)

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
