# AREA-24 — analysis/ docs remainder + root docs + adherence config

> Coverage agent for the conversational-glyphgraph research wave. **Lens (Tim): descriptive only,
> nothing canonical here is being changed — this REPORTS what the docs already decided/constrain.**
> Every doc fact is **Observed (file:line)**. Every bridge from a doc fact to the live-instrument
> pipeline is **Inferred** and marked. I read all assigned docs in full.
>
> Territory read in full: `analysis/{AUDIT-SLICE1,AUDIT-INDEX,GUIDE,PROGRESS,README,_TEMPLATE,
> capital-raise,deck1-2026,recent-pitches,pitch-deck,landing-mockups,vt-family}.md`; root
> `README.md`, `SKILL.md`; `_adherence.oxlintrc.json`.
>
> **The filter (per the task + advisor):** most of this corpus is *design-deck dialect* — zoning
> ladders, the gold ramp, type scale, the 13 slide archetypes, register/LOD axes. That is CONTEXT
> for the wave, not a CONSTRAINT on "talk → live glyphgraph." Below I map the handful of findings
> that actually constrain the live-instrument onto the anchor's RESOLVE pipeline
> (`type→form` · `state→fill/colour` · `relation→edge` · `noun→symbol` · `generate-on-miss`),
> and bucket the rest as deck-dialect context.

---

## §A · The load-bearing constraints — mapped onto the RESOLVE pipeline

The anchor's pipeline is LISTEN → EXTRACT → **RESOLVE** (form from type · fill/colour from state ·
symbol via icon-lookup · edges from relations) → GENERATE-ON-MISS → AUTO-PLACE → RENDER → NARRATE.
These corpus facts each pin down one RESOLVE stage. They are **already-decided brand canon** the
live layer must honour, not new ideas.

### A1 · `type → form` — the entity-shape system (the #1 finding)
**Observed.** The brand assigns a **canonical outer shape per platform entity**, and uses it
*consistently in every diagram*:
- README.md:9-16 (root) — the canonical table: **Circle = User Portal · Hexagon = Property Wizard ·
  Octagon = Virtual Hubs · Diamond (line-fill) = Vi (AI framework)** · Rounded-rect = generic/fallback.
- SKILL.md:29-34 — same four shapes restated as a designing rule ("**Each has a canonical shape —
  preserve it when referencing the entity in any visual**").
- README.md:155-165 (root, "The shape system… one of the most distinctive parts of the brand") +
  README.md:16 ("Use the right shape **consistently**").
- Reinforced as *used-consistently-across-every-diagram*: pitch-deck.md:167 ("Shape-coded sub-brands:
  hexagon vs diamond carry meaning… Shape is semantic"); capital-raise.md:78-79 ("Shape-coded
  entities **re-confirmed**: User Portal = circle, Property Wizard = hexagon, Virtual Tours =
  octagon, Vi/brand = V monogram. Used consistently across every diagram").
- AUDIT-INDEX.md:36 — **explicit KEEP decision**: "Shape system (circle/hex/octagon/diamond) — KEEP,
  it's right. README + source agree; this is genuine brand DNA. Reuse as diagram node shapes +
  entity badges."

→ **Inferred (the bridge):** the glyphic's **form facet** is not a free choice when the extract
layer names a known ConceptV entity — it is *resolved* (User Portal → circle, Property Wizard →
hexagon, …). The live `type→form` step must read this mapping from a single source, not re-decide
it per utterance. This is the strongest pre-existing constraint on RESOLVE: a conversation that says
"the property wizard" should land a hexagon glyphic, deterministically. *(I have not verified how/
whether `CV_GLYPHIC`/`CV_MEANING` encode the entity→shape map; that is another area's territory —
flagging that the **decided mapping** lives in these docs and must be the source.)*

### A2 · `state → fill / colour` — the status traffic-light (a real semantic colour set)
**Observed.** A warm-shifted status set exists, *separate from brand gold*, with one-word states:
- pitch-deck.md:162 — "A traffic-light STATUS system exists in the embedded product UI: **green =
  approved · amber = review/pending · red = declined**. This is a real semantic colour set, separate
  from brand gold… a likely cross-folder universal."
- README.md:114 (root) — "Status dots are colour-coded with one word: `Pending`, `Approved`,
  `Resolved`, `Rejected`." README.md:131 — "Status colours are warm-shifted — desaturated and tilted
  toward yellow." README.md:258-261 — status = **filled coloured dots, never icons-with-meaning**.
- AUDIT-INDEX.md:38 — reconciliation note: status dots (Pending/Approved/Resolved/Rejected,
  warm-shifted) match the traffic-light finding; "reconcile… status chips with the existing warm
  dots — extend, don't fork."

→ **Inferred (the bridge):** when the extract layer reads a *state* off a noun ("the buyer's gone
cold", "approved", "pending"), the glyphic's **fill/colour facet** resolves against this existing
state→colour vocabulary — warm-shifted green/amber/red plus the named states — **not** an invented
palette. The anchor's "fill/colour from state" stage has a pre-decided target set here.

### A3 · `relation → edge` — the connector / "2-way" language
**Observed.** A genuine connector vocabulary (not decoration) already encodes relationship semantics:
- pitch-deck.md:164 — "**Connector / '2-way' language:** a **plug icon** + **dashed bidirectional
  connectors** recur to encode translation/overlay/sync. A genuine connector vocabulary, not
  decoration." pitch-deck.md:69 — "Connector — thin line + arrowhead crossing the split divider;
  dashed connectors (with plug icon) between panels and in flow/timeline diagrams."
- capital-raise.md:80-82 — glyph-as-semantics edges: `→` flow, `▸` claim, `◄/►` pointer (point back
  at an adjacent visual), `⌃/⌄` expand, `+` join, `↻` recycle/morph, `$` value badge.
- recent-pitches.md:19 — "**Two bullet semantics:** `▶` gold triangle = plain list; **`→` gold arrow
  = 'flow / leads-to'**… **Bullet glyph carries meaning**."
- README.md:165-171 (root) — process-flow pattern: outlined gold cards joined by **dashed gold arrows
  with arrowheads**; pill cards sit *on* the connector to label the transition.

→ **Inferred (the bridge):** the glyphgraph's **edges** (the anchor's "edges from relations") have a
pre-existing visual grammar — solid arrowhead = directed flow, dashed bidirectional = sync/2-way,
`+` = join, plug = translate/overlay. The relation-extraction model's output should resolve onto
*these* edge kinds, not arbitrary lines.

### A4 · `noun → symbol` + GENERATE-ON-MISS — the icon library + its hard conventions
**Observed.** There is ONE canonical icon library and the conventions any *generated* icon must obey:
- README.md:221-264 (root) — "**The CV Icon Library — 99 vectorized line icons**"; `cv-icons.js`
  exposes `window.CV_ICONS.data`; nine named categories (people/files/communication/architecture/
  browser/actions/system/logic/platform). README.md:230 — **the hard shape contract**: "All icons
  share one design language: **24 × 24 viewBox, 1.5 px stroke, `currentColor`, rounded caps and
  joins, no fills**." README.md:264 — "To add a new icon… **Keep the conventions** (`viewBox="0 0
  24 24"`, 1.5 px feel, rounded caps, no fills, `currentColor`)."
- SKILL.md:42 — the sharp prohibition: "**Avoid**… and — critically — **replacing the bronze icon
  library with Lucide/Feather** in diagram contexts." SKILL.md:73-78 — which icon family for which
  context (bronze for ambient illustration, gold-circle for entity badges, ink/gold for UI chrome,
  coloured dots for status — DO NOT swap sidebar colour-emoji for SVGs).
- README.md:244-256 (root) — the **gold-circle entity badge** (icon inside a thin gold ring, used
  when the icon represents a *system entity*) + the **desaturated state-strength gradient** (fade an
  icon to show inactive/unconnected entities) — `<CvIcon … desaturated={0.5}/>`.
- AUDIT-INDEX.md:37 — **explicit KEEP**: "99-icon bronze library + gold-circle badge + desaturated
  state-gradient — KEEP, strong… Build the diagram generator ON this, don't replace it."

→ **Inferred (the bridge):** the anchor's GENERATE-ON-MISS step (foundry draws a new icon when a
noun has no close match) is **constrained by a real brand contract** — a live-drawn symbol that
isn't 24×24 / 1.5px / currentColor / rounded-caps / no-fills, or that drifts toward a Lucide/Feather
look, *breaks the brand*. This is a concrete acceptance test on the foundry's output, already
written down here. (It dovetails with the anchor's note that `glyphic.generate` validates against
`CV_GLYPHIC.schema.symbol`.) Also: the **gold-circle wrap** + **desaturated** are existing
state/role treatments the live layer can reuse for "entity vs chrome" and "active vs inactive."

### A5 · The glyphic's colour facet obeys colour-role logic
**Observed.** SKILL.md:39 — "**Colour-role logic: ink = content · gold = active/decision/selected
(never a default background) · bronze = the structural/quiet voice**… any semantic hue is an opt-in
layer on top. Warm-only — no cool greys." pitch-deck.md:188-194 (the *when*, not just the *what*):
gold "**Never body text**"; ramp position encodes loudness (gold→bronze→tan = loud→quiet/structural).
capital-raise.md:178-194 + below — **sage-green `#9fbc73` is communication/relationship-only**.

→ **Inferred:** when the resolve step picks a glyphic's **colour facet**, gold means active/decision
(never a default canvas), bronze means structural/quiet, green means communication — so the live
graph's colouring carries meaning consistent with the rest of the system, not decoration.

### A6 · An existing hand-built glyphgraph *precedent* the live layer generates dynamically
**Observed.** The corpus already contains hand-authored relational glyphgraphs the live instrument
would generate from talk instead of by hand:
- capital-raise.md:99 — "Relationship triad (V-circle ← Role ← Role, green `$` badge)" (p10
  value-flow); capital-raise.md:116 — "single-system hub (p5): … User Portal → **Property Wizard
  orbited by verb labels** (Upload·Configure·Update·Output) → Virtual Tours → product grid + mini
  legend (green=Communication, gold=File flow)."
- recent-pitches.md:14-15 — **"slides ARE templates (proof)"**: p-25 and p-49 are the *same layout,
  different data* — direct evidence the relational diagrams are "assembled from reusable templates
  with swappable content."
- README.md:35 (root) — confirms the engine already has a **graph solver** (`DiagramSolver`,
  network · hub · morph · pipeline · timeline · quadrant · tree · compare · stack · stepper) on the
  shared `cv-nodes.d.ts` node type.

→ **Inferred:** these are exactly the structures (entity nodes by shape + typed edges + state colour)
the conversational layer aims to *grow live*. The static decks show the **target output**; the
live-instrument is the same graph, authored by voice + AI in real time. This **confirms the anchor's
own anchor** (DiagramSolver / CVGraph at README.md:35) from the doc side — the relational vocabulary
the live layer feeds already exists and is exercised across the whole corpus.

---

## §B · The PRODUCT, the domain & the ethos (business context for corpus-mining)

This is **business-deck content**, included because the task asks what the docs reveal about the
product + Tim's domain/ethos — it bears on what nouns the extract layer will hit and what "field"
the source corpus is mining. **Architecture vs business note:** none of §B is an architecture
constraint; it is the *subject matter* the live instrument talks about.

### B1 · The company, the field, the ethos
**Observed (root README.md):**
- README.md:1-3 — "**ConceptV** — an Australian innovation-technology company building products on
  **Universal Mechanics, a proprietary theoretical model of how complex multi-stakeholder systems
  operate.** Universal Mechanics has been developed internally **over ten years**; ConceptV's
  competitive advantage is that the engine — and every product built on it — is literally
  constructed on the mathematics of operation." → This is the **cognitive-language / field-of-
  science** that the system memory frames as Tim's 10-year original field. The ethos: *everything is
  built on the mathematics of how multi-stakeholder systems operate* — which is the same relational-
  systems thinking the glyphic language encodes (meaning composed from relationships, not isolated
  parts).
- README.md:96-114 (root, CONTENT FUNDAMENTALS) — the **voice**: "calm, professional, slightly
  formal… a serious-but-friendly Australian technology firm explaining a precise system to a
  sophisticated stakeholder." Sentence-case everywhere; direct second-person; imperative actions; no
  exclamation/emoji in body; **"inline previews of consequences" is the brand's signature copy
  pattern** (README.md:104). SKILL.md:85 flags the website was offline so tone was inferred from
  product strings + decks.

### B2 · The product surfaces + the noun-space the extract layer will hit
**Observed:**
- README.md:5-16 + SKILL.md:27-34 — **three connected platform entities + an AI framework**: User
  Portal (circle), Property Wizard (hexagon), Virtual Hubs (octagon), Vi (diamond). Not a single
  product — a connected system.
- README.md:108-110 (root, **Vocabulary anchors**) — the actual domain nouns: "The platform is a
  **Virtual Hub**. Individual interactive spaces are **Hubs**. Per-stage variations… are **Linked
  Hubs**. Buyer-facing pages are **Landing Pages**. Annotated screenshots inside hubs are
  **Captures**. The pipeline is **Revit → Enscape → ConceptV**. The AI framework is **Vi**. Service
  tiers are **Stage 1 / Stage 2 / Stage 3 + Marketing Package**."
- README.md:18 (root) — observed URL pattern `https://conceptv.io/panotours/yourcompany/projectname`.
- The decks' subject matter (translated content-agnostic, but the real domain is property): the
  field is **property design/construction/sale coordination** — pitch-deck.md:88 arc (problem =
  multi-stakeholder coordination cost → solution = single connected system); capital-raise.md:142-153
  (the running-sentence title chain spells the whole investor argument).

→ **Inferred:** if the live instrument is demoed on "a property sale" (anchor §2's example), the
extract layer's noun-space *is this vocabulary* — Hub, Linked Hub, Capture, Landing Page, stakeholder
roles (designers/developers/sales agents/suppliers/contractors, README.md:11), the Revit→Enscape→
ConceptV pipeline. These are the nouns that should resolve to known entity-shapes (§A1) or trigger
GENERATE-ON-MISS (§A4).

---

## §C · What the build MUST NOT contradict (the laws & decided calls)

### C1 · The single-source / no-second-home / loud-fail law — machine-enforced in my territory
**Observed.** This is the GOVERNING LAW of the anchor (§5), and it is *codified + machine-enforced*
in files I was assigned:
- `claude-ds/CLAUDE.md` §0 (in my context) — "**Everything is defined once and referenced
  everywhere**… find the one home, edit there, reference from everywhere else. Never create a second
  place." §3 — "**No second home for any value**… **Loud fail, never silent** → throw, don't degrade…
  **The interface is a projection of the registries**, not a parallel structure."
- **`_adherence.oxlintrc.json`** (mine) — the compiled lint config that *enforces* it: rules
  `react/forbid-elements`, `no-restricted-imports` (a large `patterns` list forbidding cross-imports
  across `app/**`, `axes/**`, `core/**`, `components/**`, `assets/icons/**`, etc.), and
  `no-restricted-syntax`; one override for `**/index.js`. Its `x-omelette` block carries the
  **canonical inventories** the system is checked against: a `components` map (naming **Glyphic**,
  **DiagramSolver**, **ContainmentTree**, **CVType**, Button/Card/Input/Modal/Segmented/Badge/Avatar
  — each with a `replaces:[]` field), the full `tokens` list (`--accent-gold`, `--accent-bronze*`,
  `--accent-communication*`, `--ramp-*`, …), `tokenKinds` (token→{color|…}), and `fontFamilies`
  (`DM Sans`, `JetBrains Mono`, `Sora`).
  - **NOTE — compiled output, never hand-edit** (AUDIT-INDEX.md:23 lists it under "Compiler outputs…
    never hand-edit"; `claude-ds/CLAUDE.md` §5 trap repeats this). So `_adherence.oxlintrc.json` is a
    *regenerated artifact*, not a source to author.

→ **Inferred:** the live-instrument's RESOLVE must read form/colour/symbol/edge from the single
sources (CV_GLYPHIC / CV_MEANING / CV_AXES / CV_ICONS) — **a hardcoded provider, a per-type render
branch, or a copied lookup table would violate the law the lint config already polices.** The
adherence config naming **Glyphic** and **DiagramSolver** as first-class canonical components
confirms (doc-side) that the live layer extends *these*, not parallels.

### C2 · The analysis-method decisions (dated calls / golden rules)
**Observed:**
- GUIDE.md:8-13 — the **golden rules**: (1) "**Analysis before building**… Synthesis happens only
  after a rule is confirmed across **≥2 folders**." (2) **Content-agnostic** — record grammar not
  subject. (3) **Ratios, not pixels.** (4) **Subtlety is the signal** — sample real pixels, never
  eyeball.
- PROGRESS.md:5-19 + :32 — **the corpus is 12/12 folders analysed** ("The corpus is now fully
  analysed (12/12 folders)"); the analysis phase is closed/frozen and build sessions BUILD on the
  model. PROGRESS.md:34-37 — build s1–s4b done, incl. **(s4b) the UNIFICATION weld**: the type
  system+generator (`app/registry/*`) and the rule engine+solvers (`core/*`) "had ZERO references
  between them, with THREE parallel archetype lists" → welded via `core/RenderType.jsx` +
  single-source `core/archetype-catalog.js`.
- AUDIT-INDEX.md:7-8 — the **conflict-resolution rule**: "**the SOURCE material is authoritative for
  the DNA; v1 docs are authoritative for what was built.**"

### C3 · The colour decisions (do-not-overwrite calls)
**Observed:**
- AUDIT-SLICE1.md:7-9 — "**`--accent-gold: #E0C010` is the REAL logo gold** (sampled from the actual
  ConceptV logo PNG, 234k px). It is a brand ASSET, not a guess. **Do NOT overwrite/soften it.**" The
  decks' softer `#d6bf57` is the *applied* gold — a **ramp stop**, not a replacement → **keep
  `--accent-gold` = `#E0C010`; ADD `--ramp-*`**. Same for bronze (keep `#988058`, add lighter ramp).
  AUDIT-SLICE1.md:11-18 — the **de-hardcode backlog** (≈10 consumers hardcode `#E0C010`/`#988058` and
  must be pointed at `var(--accent-gold)`/ramp — a drift-risk list).
- capital-raise.md:178-194 + :190-194 — **sage-green graduated to `--accent-communication` (slice
  28)** on three independent semantic uses (the p5 legend literally *defines* green = "Communication";
  green `$` connectors; sustainability mark). Cross-folder green proved to be photographic foliage →
  **green stays the sparsest, strictly-semantic voice** (communication/relationship/sustainability
  only). This is a *decided* token + role-set, now in `x-omelette` (`--accent-communication*`, §C1).
- deck1-2026.md:82-83 — **canonical-master call**: "deck1-2026 is **2× resolution, named '2026',
  motion-ready** ⇒ the **living master**… When values conflict, **sample from deck1-2026**."

### C4 · KEEP-don't-churn decisions (genuine DNA, ratified)
**Observed (AUDIT-INDEX.md:36-43):** explicit KEEP calls — (#8) **shape system** circle/hex/octagon/
diamond; (#9) **99-icon bronze library + gold-circle badge + desaturated state-gradient** ("Build…
ON this, don't replace it"); (#10) **status dots** warm-shifted. Vigilance note (AUDIT-INDEX.md:43):
"Don't churn these" — also voice, sentence-case, URL-preview copy pattern, entity vocabulary.

### C5 · Font / website caveats (open flags)
**Observed:** README.md:139 + SKILL.md:84 — **fonts are substituted** (Sora display + DM Sans body +
JetBrains Mono); the product's real UI font is unknown ("⚠ Font substitution flagged"). README.md:62
+ SKILL.md:85 — **conceptv.com.au was offline** during the build, so the system was calibrated against
mockups + assets alone (colours pixel-sampled from the real logo PNG `#E0C010`). → The build must not
treat the substituted fonts or the inferred tone as confirmed truth.

---

## §D · The deck-dialect context bucket (NOT a live-instrument constraint)

Recorded so the wave knows it was *read and consciously set aside* — this is the design-corpus
analysis, which is context, not a constraint on "talk → live glyphgraph":
- **Tonal zoning ladder** (near-white ~1–3% warm/neutral undertone = *containment depth*, not
  category): pitch-deck.md:25-38; deck1-2026.md:32; recent-pitches.md:29; capital-raise.md:48-55;
  landing-mockups.md:15. Plus the **clean↔warm** white-vs-ivory sub-axis (capital-raise.md:165).
- **The gold→bronze→tan ramp** as the brand accent (`--ramp-1..4`): pitch-deck.md:50; deck1-2026.md:34;
  recent-pitches.md:30; SKILL.md:39. (Distinct from the dataviz/chart palette — capital-raise.md:70-73.)
- **The 13 slide archetypes** (cover · split · statement · compare · modes · triptych · metric-band ·
  checklist · timeline · profile · terms · gallery · closing) + stepper/diagram: pitch-deck.md:72-86;
  README.md:36 (root).
- **The orthogonal axis-dials** — surface (slide↔web↔print, proven complete: vt-family.md:26-27) ·
  **LOD** (4 rungs summary→high-detail, orthogonal to surface: deck1-2026.md:64-65) · density ·
  register/purpose (terse-presented vs verbose-leave-behind: deck1-2026.md:13-27) · theme.
- **The space↔time complexity trade-off** (density vs motion = two ways to pay one budget):
  deck1-2026.md:56-57. **Bullet = {claim, support}** content-model: deck1-2026.md:70-71.
- **Five new diagram sub-types** queued for DiagramSolver (orbital verb-ring, stacked/expandable
  pipeline node, 1-D spectrum axis, manifold/converging-summation, progressive-fidelity stepper):
  capital-raise.md:23-24, :172-175.
- **Modular type scale** (~1.25 + display jump), `text-wrap:balance` titles, hanging-indent bullets,
  number-formatting convention, the ABSENT-list guardrails (no pure black / hard shadows / gradients /
  emoji / drop-caps): pitch-deck.md:180-214.
- **Texture & depth** layer (blueprint ghost + diagonal gold hatch + the z-stack incl. frosted glass):
  pitch-deck.md:139-160. The **frosted-glass / product-surface bookends**: capital-raise.md:16-17.

→ Of these, the items most likely to *touch* the live layer downstream (Inferred): the **frosted-
glass** treatment (a candidate for the reactflow canvas chrome) and the **diagram sub-types** (new
relational shapes the live graph could emit) — but these are *opportunities*, not constraints. The
auto-place/RENDER stages otherwise inherit the engine's existing solver + containment model
(README.md:34-35) rather than the deck-page-layout grammar.

---

## §E · Notes on doc state (so the next agent isn't misled)
- **GUIDE.md / PROGRESS.md / README.md live under `analysis/`, not the repo root.** Root has only
  `README.md`, `SKILL.md`, `CLAUDE.md`, `DESIGN-LANGUAGE.md`, `_adherence.oxlintrc.json`,
  `_ds_manifest.json`. (The task brief implied root GUIDE/PROGRESS; they are `analysis/GUIDE.md` etc.)
- **`_TEMPLATE.md`** (analysis/) is just the blank 9-level analysis template — no decisions, no
  constraints; it is the form each folder-analysis was filled from.
- **`AUDIT-INDEX.md`** (adjacent to my AUDIT-SLICE1, not clearly in another area's lane — read on the
  advisor's prompt) carries the **reconciliation tensions + KEEP decisions** summarised in §C4; it is
  the highest-density "decided calls" doc in my territory after AUDIT-SLICE1.

---

## 3-line summary
1. The corpus already *decides* every RESOLVE-stage target the live glyphgraph needs: **entity→shape**
   (Circle/Hexagon/Octagon/Diamond — the #1 constraint, README.md:9-16, KEEP'd AUDIT-INDEX.md:36),
   **state→colour** (warm traffic-light, pitch-deck.md:162), **relation→edge** (plug/dashed-2-way/`+`
   connector grammar, pitch-deck.md:164), and a **noun→symbol** library with a hard generate-on-miss
   contract (24×24·1.5px·currentColor·no-fills·never-Lucide, README.md:230 / SKILL.md:42).
2. The build must not contradict the **single-source / loud-fail / projection law** — machine-enforced
   by `_adherence.oxlintrc.json` (compiled, never-edit), whose canonical inventory already names
   Glyphic + DiagramSolver — nor the decided colour calls (keep `#E0C010`; green=communication-only;
   sample from deck1-2026), the ≥2-folder synthesis rule (GUIDE.md:9), or the substituted-font /
   site-offline caveats (README.md:139, SKILL.md:85).
3. Business context (the noun-space the extract layer mines): ConceptV is built on **Universal
   Mechanics** — a 10-year proprietary model of multi-stakeholder system operation (README.md:3) — with
   a connected product family (User Portal / Property Wizard / Virtual Hubs / Vi) and a precise domain
   vocabulary (Hub · Linked Hub · Capture · Landing Page · Revit→Enscape→ConceptV, README.md:108-110).

Path: `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-24-analysis-docs-remainder.md`
