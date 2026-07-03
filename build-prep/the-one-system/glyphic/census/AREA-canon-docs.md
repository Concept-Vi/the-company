# AREA — Canon / Discipline Docs (census reader: UNIFICATION + LOCKSTEP DEBT)

> Reader lens: the canon/discipline docs of `claude-ds` + the seat's charter docs. Territory read
> FIRST-HAND this pass (every line): `README.md` (v2), `DESIGN-LANGUAGE.md`, `SKILL.md`,
> `analysis/HANDOFF.md`, `analysis/SYSTEM-GAPS.md`, plus `analysis/{GUIDE,REQUIREMENTS,AUDIT-INDEX,
> DIAGRAMS,AXIS-REFACTOR,SYNTHESIS-PLAN,mid-lod,SYSTEM-MAP-EDITOR-ADAPTER}.md` (classified), and the
> two charter docs `THE-GENERATIVE-LANGUAGE.md` + `REGROUNDING.md`. Grounding read first:
> feedback-glyphic-course-corrections, CRITERIA+AMENDMENTS A1-A5, ROADMAP, ADVISOR-AUDIT (I close its
> §4 items 1-2), READING-LEDGER, GUIDE/SYNTHESIS tails, FINDINGS-LOG Slices 83-84.
> Marks: **[O]** Observed (file:line, no execution) · **[I]** Inferred (labeled, unverified) ·
> **[V]** Verified (I ran/confirmed it). READ-ONLY on all sources; I wrote only this census file.

---

## §A — DOC-BY-DOC ACCOUNT

### A1 · `DESIGN-LANGUAGE.md` (14.8K) — the cross-cutting rules the system OBEYS
**[O]** Structure: a numbered list of "how we design" laws. §1 multi-surface · §2 responsive/computed ·
§3 motion ("nothing teleports") · §4 visual-first ("A relationship is shown as a diagram… not a
bulleted list"; "the diagram vocabulary (nodes, connectors, arrowheads, **edge kinds**) is tokenised…
a generative diagram component will emit that same markup from a small `{nodes, edges}` spec",
DESIGN-LANGUAGE.md:46-48) · §5 depth · §6 colour discipline (two saturated voices — gold + sage) ·
§7 theme · §8 density · §9 composition ("Layouts are content-as-data, never bespoke… `design =
f(content, axisPosition)`") · §10 resolve-don't-pop · §11 authorship · §12 exports · §13 one-home
anti-drift law · §14 AI-is-the-system (`CV_AI`) · §15 the Bridge (`CV_HOST`) · §16 narrative title-chain
· **§18 universal component** (slots/sockets/parts/conditions; "the Glyphic's ring + symbol"; "Spec:
`system/glyphic-system.html`") · **§17 Axes** ("**Colour · Space · Size · Motion · Texture · Depth ·
Fill · Form · Symbol**, with **Meaning** the contextual/loadable layer *over* them (`CV_MEANING`)").
**[O]** §17 and §18 are out of numeric order (17 after 18) — a pre-existing quirk, not my concern.
**[O] The load-bearing fact for the lockstep drafts:** the Glyphic/CV_MEANING model is present ONLY
inside §17 (Meaning as a contextual layer over the axes) and §18 (the universal component grammar).
There is **no section on the read-out / transglyphing, no section on edges-as-directional-verbs, and
no section on referent-words-as-profile-data.** The language engine (readGraph, the edge law, R1/R2)
is entirely absent from this doc. **[O]** §4 is the closest existing anchor for the read-out (it already
says relationships are *shown*, not listed, and mentions "edge kinds" tokenised), and §17/§18 are the
anchors for CV_MEANING/edges as registry citizens.

### A2 · `README.md` (26.6K, "v2") — the brand bible + the generative-layer overview
**[O]** Two layers: the top ("v2 — THE GENERATIVE LAYER") is authoritative when it conflicts with the
v1 body (README.md:27 "When they conflict, v2 wins"). The v1 body is product-UI ground truth (voice,
colours, iconography, shapes).
**[O] The entity/shape table** (README.md:9-16): `User Portal → Circle · Property Wizard → Hexagon ·
Virtual Hubs → Octagon · Vi → Diamond(line-fill)`. Line 16: "Use the right shape **consistently**…
The shape system is one of the most distinctive parts of the brand." This is a **ConceptV business /
brand-entity** mapping sampled from the real decks — NOT a glyphic-language referent claim.
**[O]** The Glyphic bullet (README.md:41): "`CV_MEANING` holds swappable meaning profiles (what a
form/colour-value/texture/depth means in a given context) — the lone exception being symbols, whose
meaning is intrinsic." This ALREADY encodes "meaning is contextual/loadable" — i.e. it already agrees
with Tim's "nothing has one fixed meaning" for facet meaning; what it does NOT yet say is that the
**referent WORDS (the read-out vocabulary) are also profile data** (R2), nor does it mention the
read-out / edge-law at all.
**[O]** The README's own pointer to the lockstep duty is implicit (it cites `DESIGN-LANGUAGE.md` as
"the rules" throughout); the CLAUDE.md files make the duty explicit (see A3).

### A3 · `CLAUDE.md` (root + design-folder) + `SKILL.md` — the discipline that MANDATES the lockstep
**[O]** `claude-ds/CLAUDE.md` §0: "Everything is defined once and referenced everywhere… find the one
home, edit there, reference from everywhere else. Never create a second place for a thing to live."
**[O] The lockstep duty, verbatim** (`claude-ds/CLAUDE.md` §4.3): "Keep `DESIGN-LANGUAGE.md` +
`README.md` v2 in lockstep when you add a *rule the system makes*." And `analysis/HANDOFF.md` §4e:
"**New rules/claims the system makes** → `DESIGN-LANGUAGE.md` and the root `README.md` v2 section, **in
lockstep** (don't let the docs codify a stale read — the v1 README already did that once)." R1 (the
edge law) and R2 (referent-words-are-data) are exactly "rules the system makes" → **the lockstep is
owed and was skipped** (ADVISOR-AUDIT §4 item 2 — my debt to close, drafted in §C).
**[O]** `SKILL.md` is the consumer skill entrypoint. It repeats the entity-shape system (SKILL.md:29-34,
same Circle/Hexagon/Octagon/Diamond mapping) and the colour-ramp/colour-role logic. It is a
consumer-facing surface; if the shape-semantics wording is reconciled it should stay coherent with the
README, but SKILL.md is NOT one of the two lockstep homes (§C leaves it as a follow-on).
**[O]** `design/CLAUDE.md` (the parent `design/` keeper charter) governs the `design/_system/*.py`
corpus machinery — a DIFFERENT scope (the token/address/gallery/refcheck apparatus), not the glyphic
canon. Classified: live canon for the parent folder, out of my drafting scope.

### A4 · `analysis/HANDOFF.md` (25.7K) — the "master briefing" (STALE — see §D/§ below)
**[O]** Presents itself as "your complete briefing… no other instruction." Repo map, mindset,
conventions, traps. **[O] Its "What's DONE vs NEXT" (§7)** stops at **Slice 3** (the generative core):
"Done: Slice 1 token recalibration · Slice 2 atom tokens · Slice 3 the generative core." "Next: Slice
4 — the component & template library… Slice 5 — motion + interactivity." **[O]** It has **zero mention**
of the Glyphic language engine, `readGraph`/transglyphing, `CV_MEANING`, `cv-edges`, the edge law, or
R1/R2. Its "first moves in a fresh session" (§9) send a new agent to "Pick up Slice 4." A fresh session
booting on HANDOFF alone would have NO idea the language engine (G0-G11, verified) exists — it is two
whole build eras stale. This is the single largest self-description drift in my territory (§D + §ii).

### A5 · `analysis/SYSTEM-GAPS.md` (19.5K) — the analysis-era raw findings log
**[O]** A running log of what the 12-source-folder analysis found that the system "doesn't have yet,"
by confidence tier (confirmed-across-N-folders vs seeded/provisional). It is an ANALYSIS artifact
(feeds SYNTHESIS-PLAN → the v2 token/core build), not a live spec. Triage in §D.
**[O] The ramp citation A4 depends on** is here: `#d6bf57 → #c09d5d → #b98664` at SYSTEM-GAPS.md:11
("Gold→bronze→tan ramp: primary `#d6bf57`… bronze `#c09d5d`… tan `#b98664`") and :92 (same values as
`pitch-deck` sampled). **[O]** Also SYSTEM-GAPS.md:146: "**Shape-coded sub-brands** — hexagon (engine)
vs diamond (assistant); shape is semantic." — a pre-existing statement bearing directly on the
octagon/referent tension (see §B-1): the corpus DOES treat shape as semantic for BRAND ENTITIES.

### A6 · The other `analysis/*.md` (classified — no reader owns these)
- **`DIAGRAMS.md`** (54 lines) — **LIVE CANON.** The diagram generator's type system; the graph solver
  (`DiagramSolver`) implements it. **[O]** DIAGRAMS.md:14 lists node shapes "octagon **(Vi-Hub)** ·
  hexagon **(Property-Wizard)**" — again the BRAND-ENTITY shape mapping, and `tint = a position on the
  gold→bronze→tan ramp`. Relevant to R1 (edges) + the octagon tension.
- **`AXIS-REFACTOR.md`** (152 lines) — **LIVE CANON.** The master scope for `CV_AXES` (the 9 axes +
  Meaning). Companion to DESIGN-LANGUAGE §17. The facet-as-axis-value model the glyphic facets resolve
  through. Load-bearing for how CV_MEANING sits over the axes.
- **`SYNTHESIS-PLAN.md`** (96 lines) — **HISTORICAL (build order for the v2 token/core build).** "Nothing
  here is built yet — this is the plan" (its own header). Superseded by FINDINGS-LOG for what actually
  landed; kept as the analysis→build bridge record.
- **`mid-lod.md`** (38 lines) — **HISTORICAL (source-folder analysis, 6th-7th folder).** "Verdict: fully
  confirms the model; no new grammar." Its one refinement (the chaos→order hub state-morph) is a diagram
  rule. Confirms the octagon/hex Vi-Hub badge as corpus DNA (mid-lod.md:6).
- **`SYSTEM-MAP-EDITOR-ADAPTER.md`** (77 lines) — **LIVE CANON (a distinct feature contract).** The
  System Map editor's disk-write adapter/operation-queue. Unrelated to the glyphic language; a separate
  editor surface. Live but out of glyphic scope.
- **`GUIDE.md`** (50 lines, analysis) — **HISTORICAL (method).** How to run a source-folder analysis;
  "the next work is *building*, not analysing" (HANDOFF §3). Method archive.
- **`REQUIREMENTS.md`** (76 lines) — **LIVE CANON (the living spec / north-star).** "rules that compute,
  not dedicated writes." Its north-star (generate never-seen components that still obey the DNA) is the
  same north-star the glyphic language extends. Live.
- **`AUDIT-INDEX.md`** (46 lines) — **LIVE CANON (the whole-system content-TYPE map + the 10
  reconciliation tensions).** Its governing rule (AUDIT-INDEX.md:6-7): "**the SOURCE material is
  authoritative for the DNA; v1 docs are authoritative for what was built**" — directly relevant to
  reconciling the octagon tension (§B-1).

### A7 · The charter docs (the seat's own, never first-hand read before this pass)
- **`THE-GENERATIVE-LANGUAGE.md`** (21.2K) — the seat's DOCTRINE. §1 is 18 top-level laws (each marked
  `[Tim]`/`[ratified]`/`[my read]`). **[O] §1.18 IS the edge law, as a governing physics law:**
  "Everything flows both ways. **Typed directional edges with equal-and-opposite, per type, level, scale**
  `[Tim]`. Whatever can be shown can be pointed at; whatever can be generated can be read back. A one-way
  surface is a violation on par with a hardcoded hex." (THE-GENERATIVE-LANGUAGE.md:119-121). §2 is the
  fusion map (counterpart `dna/` faces ↔ claude-ds homes ↔ Company organs). §3 realisations; §4 method;
  §5 open threads. See §E for what the ROADMAP misses from this.
- **`REGROUNDING.md`** (18.8K) — the re-boot manifest / map. **[O]** §0 = THE STANDARD (product-level =
  done, not tests-pass). §3 restates the octagon test ("can you hear the octagon?"). §6 item 2: placement
  "currently a crude ring; the `n/x`/zones/LOD system is unbuilt" (= R3). §9 = the full anatomy (every
  subsystem to integrate). See §E.

---

## §B — CONTRADICTIONS: canon docs vs plan-of-record (each with a proposed resolution)

### B-1 · ★ THE BIGGEST ONE — "octagon = Gateway" (the referent word) vs the ConceptV entity-shape system
**The apparent contradiction.** Tim's correction #2 (feedback-glyphic-course-corrections): "an octagon
does not mean gateway, an AI just wrote that there once… Fixed shape-tables (octagon=Gateway etc.) are
AI inventions, not canon — retire into fields. The 'octagon decision' was a false decision."
Amendment A1 / R2 removes `REFERENT_KIND = { octagon:'gateway'… }` (the read-out word) into profile
field data. **BUT** the canon docs assert a shape→entity table everywhere:
- README.md:13 `Virtual Hubs | Octagon`; README.md:16 "use the right shape consistently."
- SKILL.md:33 "Virtual Hubs → octagon"; DIAGRAMS.md:14 "octagon **(Vi-Hub)**"; mid-lod.md:6
  "octagon/hex Vi-Hub badge"; SYSTEM-GAPS.md:146 "shape is semantic."
- THE-GENERATIVE-LANGUAGE.md:136 (fusion map, shapes.json row): "shape=f(entityType), CARDINALITY:
  octagon once… CV_MEANING forms (circle=kind, square=specific, **octagon=gateway**…)".

**[I] Proposed resolution — TWO DISTINCT LAYERS, only one is the target of Tim's correction (I have not
run code to confirm the two are cleanly separated in `cv-meaning.js`; this is a doc-level reading):**
1. **The ConceptV brand-entity shape mapping** (Octagon = the Virtual Hubs *product entity*) is
   corpus-observed business DNA — sampled from real decks, confirmed across ≥7 folders. By AUDIT-INDEX's
   own rule ("the SOURCE material is authoritative for the DNA") this is **NOT an AI invention and is NOT
   what Tim retired.** It is a domain fact about ConceptV's brand, legitimately consistent.
2. **The glyphic-language REFERENT word** (`REFERENT_KIND.octagon = 'gateway'`) is the read-out noun the
   engine emitted for *any* octagon glyph regardless of context — a fixed lookup the author API couldn't
   reach. **THIS** is the "AI just wrote that once" invention Tim retired (R2 moved it to `form.kindWord`
   field data). The word 'gateway' has no ConceptV-brand basis; it was a generic default.
   The two are not the same claim: one says "the Virtual Hubs entity is drawn as an octagon" (brand);
   the other said "every octagon *means* the word gateway" (a baked read-out). The lockstep drafts (§C)
   and the reconciliation must be careful to retire ONLY #2 and PRESERVE #1 — the README entity table
   stays; the read-out word becomes field data with no single fixed meaning.
   **Plan-file action (tentative, §F):** the R2 slice + the lockstep entry must state this split
   explicitly so a future session does not "fix" the README entity table thinking it is the invented one.
   **[O] Note the charter itself blurs this** (THE-GENERATIVE-LANGUAGE.md:136 puts `octagon=gateway`
   INSIDE the CV_MEANING-forms cell of the fusion map, adjacent to `octagon once` cardinality) — the
   charter should be corrected to separate the brand-entity shape from the retired referent word.

### B-2 · The edge law is a top-level CHARTER LAW, but the ROADMAP treats it as a one-off fix (R1)
**[O]** THE-GENERATIVE-LANGUAGE.md:119-121 states the edge law (§1.18) as one of the 18 governing physics
laws that "hold everywhere, in every medium, at every scale" — two-way flow, equal-and-opposite, "a
one-way surface is a violation on par with a hardcoded hex." **[O]** DESIGN-LANGUAGE.md has NO law
corresponding to it. The ROADMAP's R1 lands it narrowly: relationship Types gain `directed`+`inverse`,
readGraph realises the inverse (FINDINGS Slice 83). **The mechanism is built; the LAW is not codified in
the discipline docs.** Contradiction: the charter says this is a universal law of the system; the canon
docs the system polices itself by (DESIGN-LANGUAGE/README) are silent on it.
**Proposed resolution:** close the lockstep (§C-1) — add the law to DESIGN-LANGUAGE.md as a first-class
numbered rule, and to README's v2 layer, so the discipline docs carry what the charter charges. This is
exactly the ADVISOR-AUDIT §4 item-2 debt.

### B-3 · HANDOFF.md says the build is at Slice 3; the plan-of-record + verifiers say G0-G11 are built
**[O]** HANDOFF §7 "Next: Slice 4" (component/template library) — no language engine. **[V-by-audit]**
The plan-of-record (CRITERIA STATUS RECONCILED 2026-07-03; ADVISOR-AUDIT §3 harness re-run;
READING-LEDGER) show the entire glyphic language engine (G0-G11, readGraph, parse, multi-target,
data-binding, the DiagramSolver glyphgraph render) built and harness-green, plus R1/R2 landed.
**Contradiction:** HANDOFF is the doc a fresh session is told to boot from ("START HERE"), and it is two
build eras behind. A next-gen session would re-derive or ignore the language engine.
**Proposed resolution (§F):** HANDOFF §7 (Done/Next) and §9 (first moves) get a corrective addendum
pointing at the language engine + the PHASE RECONCILE work + REGROUNDING.md as the true current entry.
Do NOT rewrite HANDOFF wholesale (it is accurate for the token/core era); ADD a "since this was written"
block at the top and correct §7/§9. (Home for the correction is FINDINGS-LOG for the record + a HANDOFF
addendum; both are self-description, not "rules the system makes," so they are NOT the DESIGN-LANGUAGE
lockstep — separate from §C.)

### B-4 · "Two saturated voices, never more" (DESIGN-LANGUAGE §6) vs the read-out's line-colour field
**[O]** DESIGN-LANGUAGE.md:58: "exactly **two saturated voices**, never more: gold + sage-green." **[O]**
The read-out's edge line-colour is a FIELD with red=blocked / green=approved / gold=active (CRITERIA
G2.2; FINDINGS Slice 80). **[I] Not a true contradiction** — §6 governs *brand chrome* saturation; edge
state-colours are a *status/data* layer (the same distinction §6 itself draws between the sage *voice*
and `--pig-success` the *state*, DESIGN-LANGUAGE.md:58). But a reader could read them as conflicting.
**Proposed resolution:** when §C-1's edge-law section lands, one clause should note that edge state-colour
is a data/status channel resolved from the meaning field, distinct from the two brand voices — closing
the ambiguity rather than leaving a future reader to trip on it.

### B-5 · DESIGN-LANGUAGE §4 promises a diagram from `{nodes, edges}`; the glyphgraph is that, unstated
**[O]** DESIGN-LANGUAGE.md:48: "a generative diagram component will emit that same markup from a small
`{nodes, edges}` spec." **[O]** The glyphgraph render (CRITERIA G5; the DiagramSolver `glyphgraph` case)
IS the realisation — a `CVGraph {nodes, edges}` rendered as full glyphics with edges carrying meaning
visually, read-out beneath. The canon promised it in future tense; it exists. **Not a contradiction, a
STALENESS:** §4 should be updated (in the §C lockstep pass) to point at the built glyphgraph + read-out
as the realisation, so the doc stops describing a shipped thing as future work.

---

## §C — THE LOCKSTEP DRAFTS (ready-to-paste text for DESIGN-LANGUAGE.md + README.md, in their voice)

> These are DRAFTS for the plan/build to apply, NOT edits I made. They close ADVISOR-AUDIT §4 items 1-2
> (the DESIGN-LANGUAGE/README lockstep skipped for R1 edge-law + R2 referent-words-as-data). Written in
> each doc's established voice/format. Section numbers proposed; the seat picks the final numbering. I
> mark where each belongs in the existing structure. **[I]** the exact wording is starter/live-tunable
> (A5); the LAW is fixed by Tim's corrections + the charter.

### C-1 · DESIGN-LANGUAGE.md — NEW RULE: the edge law (R1). Belongs as a new numbered section, adjacent to §4 (visual-first / diagrams) and §13 (one-home). Proposed §19.

```markdown
## 19. Relations are directional verbs with an equal-and-opposite — the edge law
A relationship in the system is not a label on a line; it is a **typed directional verb that declares
its inverse**. Every edge kind has a `directed` flag, and every directed kind declares its `inverse`
**once** (`contains ↔ contained by`, `has-face ↔ face-of`); the opposite telling is *composed at read*
from the one stored edge and the reader's focus — never stored twice. Symmetric relations (`equals`,
`and`, `navigates`, `mirrors`) declare `directed:false`. This makes the language two-way by
construction: **whatever can be shown can be pointed at, and whatever can be generated can be read
back** — a one-way surface is a drift on par with a hardcoded hex. The read-out (`readGraph`) realises
"A contains B" or "B is contained by A" from the same edge; the reverse parser stores the one canonical
edge from either saying. A *sentence* about a relation ("is the face of") lives in the read-out, never
as an edge type-id. Edge kinds live in ONE home (the meaning field `('edge', word)` + a `relationship`
Type carrying `{directed, inverse}` — the shape the Company's `relation_types` already use); geometry
(line-style, colour, routing, arrowheads) stays in the shape layer and is *look only*. An edge's
**line-colour is a data/status field** (red=blocked · green=approved · gold=active) resolved from the
meaning — a status channel, distinct from the two brand voices of §6. To add a relation: author the
field, register the Type with its inverse — it renders, reads both directions, and parses, with no code
edit. (Engine: `assets/icons/cv-meaning.js` read-out + `cv-edges.js`; Types: `app/registry/
relationships-seed.js`. Full law: `build-prep/the-one-system/glyphic/THE-GENERATIVE-LANGUAGE.md` §1.18.)
```

### C-2 · DESIGN-LANGUAGE.md — NEW RULE: nothing has one fixed meaning; the read-out words are profile data (R2). Belongs as a new numbered section adjacent to §17 (Axes / Meaning). Proposed §20.

```markdown
## 20. Nothing has one fixed meaning — the read-out vocabulary is profile data
Meaning in this system is a **field** (feeling + senses, contextual, combinatorial), never a single
baked sentence, and **every word the language speaks is authorable profile data — never a private
constant the author API cannot reach.** A fixed interpretation anywhere the author API can't touch is a
violation of the one-home law (§13) applied to meaning. The referent words the read-out uses — the noun
a form resolves to, the phrase an operator reads as, the determiner ladder ('a possible' / 'the' /
'this' / 'a') — are **field data on the meaning profile** (`form.kindWord`, `form.opWord`,
`fill`/`outline.determiner`), read by both `referent()` and the reverse `parse()`, so authoring a word
moves the read-out AND the parse together, live, with no code edit. This is why "an octagon does not
*mean* gateway": the glyph carries a meaning FIELD, not a fixed word — the read-out word is a
correctable profile value, tuned during use, not a definition. (This is distinct from ConceptV's
brand-entity **shape system** — Octagon = the Virtual Hubs product entity, etc. — which is observed
brand DNA, not a language referent; see README. The entity-shape mapping is a domain fact and stays;
the *read-out word* for a bare glyph is the field data described here.) Symbols remain the lone
intrinsic-meaning exception (their meaning is not profile-governed). Correction happens DURING
generation through the authoring API (`setField`/`setGloss`), never behind a build gate. (Engine:
`assets/icons/cv-meaning.js`; the authoring API `CV_MEANING.author`.)
```

### C-3 · README.md — v2 layer, edge law + read-out. Belongs as an addition to the Glyphic bullet block (README.md:41 area), OR a short new bullet after it. Proposed: extend the existing Glyphic bullet + add one read-out bullet.

```markdown
- **The read-out — the language speaks (`readGraph` / transglyphing)** (`assets/icons/cv-meaning.js`):
  a glyphgraph is a **sentence drawn**; the read-out turns any `CVGraph` into real language. A single
  glyph reads as a **referent** (a noun phrase, not a sentence); a relation reads as a clause whose mood
  follows the line (solid = "is", dashed = "could") and whose verb follows the relation type; branches
  coordinate ("A and B") and subordinate ("…, which …"); negation and conditionals read. **Relations are
  directional verbs with a declared equal-and-opposite** — the opposite telling is composed at read from
  ONE stored edge, so the language is two-way (`parse()` inverts the same grammar: text → glyphgraph).
  **Nothing has one fixed meaning:** the read-out's referent words (the noun a form reads as, the
  determiner ladder) are **authorable profile data**, not constants — an octagon carries a meaning
  field, not the baked word "gateway"; the word is tuned live through the author API. This is separate
  from the brand **entity-shape system** above (Octagon = Virtual Hubs, etc.), which is observed brand
  DNA that stays fixed. Rules: `DESIGN-LANGUAGE.md` §19 (the edge law) + §20 (meaning is a field).
```

**[I] Placement note for the applier:** in DESIGN-LANGUAGE.md the two new sections should carry forward
the doc's telegraphic, imperative voice (short declaratives, `--token`/`code` refs inline, "never"
absolutes) — the drafts above match it. In README.md the v2 section is a bulleted feature overview with
`(path)` refs and bold lead-ins — the draft bullet matches that shape. Neither draft renumbers existing
sections; §19/§20 append cleanly (the doc already has an out-of-order §17-after-§18, so append-at-end is
consistent with its history).

---

## §D — SYSTEM-GAPS TRIAGE (real vs since-closed, with evidence)

> SYSTEM-GAPS.md is an ANALYSIS-ERA log (feeds SYNTHESIS-PLAN → the v2 token/core build). Most entries
> were graduated into tokens/core during Slices 1-3. Triaged against HANDOFF §7 (done) + DESIGN-LANGUAGE
> + the README v2 bullets. **[O]** unless marked.

**SINCE-CLOSED (graduated into the built system):**
- **Near-white zoning ladder** (SYSTEM-GAPS.md:10, :87) → CLOSED. Slice 1 recalibrated `--zone-*`;
  `core/containers.css` computes zone-wash from nesting depth (HANDOFF §5, §4c; README.md:34).
- **Gold→bronze→tan ramp** (:11, :92) → CLOSED. `--ramp-1..4` shipped Slice 1 (README.md:43; HANDOFF
  §4b). *(This is the ramp A4 cites for the ordinal axis — the intent is real AND landed as tokens.)*
- **Grid / 12% margins / frame signature** (:12, :112) → CLOSED into `tokens/surfaces.css` +
  `core/containers.css` (`.cv-band` carries the ratio-invariant margins, HANDOFF §5).
- **Colour-role logic (ink/gold/bronze)** (:13, :167) → CLOSED into DESIGN-LANGUAGE §6 + HANDOFF §4b.
- **Texture (hatch + blueprint ghost)** (:65-66, :100-102, :128) → CLOSED into `tokens/texture.css`
  (HANDOFF repo map).
- **Depth / elevation / z-stack** (:123, :127) → CLOSED into `tokens/depth.css` + the `--z-*` scale
  (`tokens/layout.css`).
- **Containment hierarchy / zoning=depth / LOD-on-the-tree** (:40-55) → CLOSED — this became the
  generative core (Slice 3): the containment ladder + LOD pruning (HANDOFF §5; AXES.md is its home).
- **Atom set / archetype library / "slides ARE templates"** (:14, :36, :113) → PARTIALLY CLOSED — the 13
  archetypes are registered (`core/archetype-catalog.js`; README.md:36); atom rendering is a registry
  (`ContainmentTree.registerAtom`). Some catalogued atoms (hero-number, QR phygital card, geo-locator,
  device-channel strip) remain a **starter set** to grow (HANDOFF §8 flags this). → still-open, low risk.
- **Register / LOD / density axes** (:16-25, :33-38) → CLOSED as the axis-dials (README.md:33; the
  orthogonal-axes discipline, HANDOFF §4d).
- **Diagram state-morph (chaos→hub)** (:133; mid-lod.md) → CLOSED into the DiagramSolver `morph` type
  (HANDOFF §5 "morph… tweens via motion tokens").
- **Status traffic-light set (green/amber/red)** (:138) → CLOSED as status tokens + it recurs as the
  edge line-colour field in the read-out (CRITERIA G2.2). Reconciled by §B-4.

**STILL REAL (open, correctly not-yet-built):**
- **Motion-placement rules** ("animate only hero concept + immersive views; analytical slides still",
  :28, :175-178) → OPEN. HANDOFF §7 puts this in Slice 5 (motion + interactivity). Real.
- **The deck→app interactive bridge** (:51, :140-141, :178) → OPEN (Slice 5). The runtime-mutable tree =
  the embedded product UI. Real; overlaps the glyphic live-instrument work (REGROUNDING §6).
- **Some connective/narrative components** (glass panel, italic-bronze connective caption, trust strip,
  profile block, stat-callout, QR phygital card, :70-74, :124, :132) → OPEN as component-library work
  (Slice 4). Real but low risk — component build, not architecture.
- **Responsive fragility per-level collapse rules** (:187-188) → PARTIALLY OPEN (HANDOFF §8 flags the
  collapse rules as minimal — split→stack at 640px only). Real.

**[I] Net:** SYSTEM-GAPS is ~75% since-closed (the token/structure/DNA half — Slices 1-3) and ~25% still
real (the component-library + motion + interactive-bridge half — Slices 4-5, which overlap the glyphic
live-instrument / product-integration work in REGROUNDING §6). None of its open items CONTRADICT the
plan-of-record; they SIT UNDER the same product-integration bar. **The file is not stale-wrong, it is
stale-partial** — it should carry a header note that Slices 1-3 items are closed (pointing at
FINDINGS-LOG), so it stops reading as an all-open to-do. That header note is a §F candidate.

---

## §E — CHARTER GAPS THE ROADMAP MISSES

> Reading THE-GENERATIVE-LANGUAGE.md + REGROUNDING.md against the current ROADMAP. The charter charges
> the seat with more than the ROADMAP's PHASE-A/RECONCILE/REMAINING lists capture.

**E-1 · The edge law is a UNIVERSAL law, not a one-relation fix.** THE-GENERATIVE-LANGUAGE §1.18 says
two-way flow holds "per type, level, scale… a one-way surface is a violation on par with a hardcoded
hex." The ROADMAP's R1 satisfies it for *relationship edges*. **[I] The charter charges it wider:**
EVERY generated surface should be readable-back (the read-out) AND pointable-at (addressable). The
ROADMAP has no standing checkpoint for "is this new surface two-way?" — it lands the edge case and moves
on. **Gap:** a standing invariant (charter §1.10's `checker` classes — predicate/build/model) that
polices two-wayness across the build, not just at R1. Tentative §F item.

**E-2 · Bimodal records / "every citizen carries its verbal twin" (§2 molecules.json row, §1.10).** The
charter's fusion map (THE-GENERATIVE-LANGUAGE.md:134) says the fused system has BIMODAL records: "every
visual unit carries its verbal twin." The ROADMAP builds the read-out for glyphgraphs but does not carry
the charge that *every* citizen (a token, a Type, an axis value) should be able to say itself (§3
realisation-6 "THE ONE CITIZEN GRAMMAR (e) its VOICE — every citizen can say itself"). **Gap:** G8
self-describing (guides/pages per glyphic thing) is in scope, but the deeper charter claim — the
read-out generalises to the whole registry, not just glyphgraphs — is not a ROADMAP item.

**E-3 · Fields on the canvas (§3 realisation-5).** "The glyphgraph should carry FIELDS (warmth/ordinal/
density gradients) as orientation… Nobody has built this yet; the laws for it exist." The ROADMAP's R4
touches the ordinal axis (the `--ramp-*` tokens) but not the broader "fields as canvas orientation"
charge. **[I] Gap:** the ordinal ramp is one field; the charter wants warmth/density gradients as
first-class canvas orientation. Larger than R4.

**E-4 · The "80% — frames without furniture" diagnosis (§3 realisation-4 + §1.11 provision laws).** The
charter says the seat's own build is at 80%: "bare nodes on a void, no atmosphere/organisms, no zones,
timid type, no evidence density." REGROUNDING §6.6 echoes this (product polish + gallery integration:
"currently a bespoke test-harness page"). The ROADMAP's PHASE REMAINING has "the G5 FORM taste flags +
the writer FORM pass to Tim's eye" but does NOT carry the **provision** charge (organisms, atmosphere,
evidence density, zones on the canvas) as explicit build items. **[I] This is the charter's central
product-bar charge and the ROADMAP under-books it.** The biggest charter→roadmap gap.

**E-5 · Convergence = the per-FACE fusion map, not a scoped read+fuse.** THE-GENERATIVE-LANGUAGE §2 is a
detailed face-by-face correspondence (16 counterpart `dna/*.json` faces ↔ claude-ds homes ↔ Company
organs) with named keystone correspondences. The ROADMAP's PHASE CONVERGENCE is one line ("Identify
counterpart/design's unique parts and FUSE the best… A scoped read+fuse pass"). **[I] Gap:** the ROADMAP
flattens a mapped 16-face convergence into a vague pass — the charter already did the mapping the ROADMAP
treats as undone. The convergence phase should reference §2's face table as its worklist.

**E-6 · `sequence.json` — the narrative arc face claude-ds LACKS (§2, row 10).** The fusion map flags
"sequence.json (roles, envelopes, arcs, tiers, fusion, lexicon) | — (**missing in claude-ds!**)". A
glyphgraph telling has an ARC (charter). DESIGN-LANGUAGE §16 (narrative title-chain) is the nearest
existing home but is deck-specific. **[I] Gap:** the ROADMAP has no item for the narrative-arc face of
the read-out (a telling's sequencing), which the charter names as an absent organ.

**Charter-gap VERDICT (for the ≤5-line final message):** the ROADMAP faithfully lands the CRITERIA
amendments (R1-R5) but under-books THREE charter charges — (E-1) two-wayness as a *standing* invariant
not a one-off, (E-4) the "provision / frames-without-furniture" product bar as explicit build items, and
(E-5/E-6) the mapped 16-face convergence + the missing narrative-arc organ. The charter is ahead of the
ROADMAP; the ROADMAP should adopt §2's face-map as its convergence worklist and add a provision phase.

---

## §F — PROPOSED PLAN-FILE EDITS (tentative — for the lead/Tim to apply, not applied by me)

1. **CRITERIA.md — extend A1/A2 dispositions with the octagon SPLIT (§B-1).** Add to A1 (or a note on
   A2): the R2 read-out-word retirement must PRESERVE the ConceptV brand-entity shape mapping (Octagon =
   Virtual Hubs — observed brand DNA per AUDIT-INDEX's source-is-authoritative rule) and retire ONLY the
   generic referent word. State it so a future session cannot "fix" the README entity table.

2. **CRITERIA.md / ROADMAP R1+R2 — book the LOCKSTEP as a concrete verify item.** The lockstep drafts in
   §C are ready to paste into DESIGN-LANGUAGE.md (proposed §19 edge-law + §20 meaning-is-a-field) and
   README.md (the read-out bullet). Add "DONE when: DESIGN-LANGUAGE.md §19/§20 + the README read-out
   bullet exist and match R1/R2." This closes ADVISOR-AUDIT §4 item-2 explicitly, with a bar.

3. **FINDINGS-LOG.md — Slices 83/84 already exist (the ADVISOR-AUDIT §4 item-1 debt is CLOSED).** [O] I
   verified Slices 83 (R1) + 84 (R2) are at the top of `analysis/FINDINGS-LOG.md`. The audit's item-1
   ("no FINDINGS-LOG slice for R1/R2") is now satisfied. Both slices' "Open" lines already name the
   DESIGN-LANGUAGE/README lockstep as pending (Slice 84:28 "DESIGN-LANGUAGE/README lockstep entries
   pending (drafted by the census team)") — this report IS that draft. Update those Open lines to point
   at this file when the drafts land.

4. **HANDOFF.md — add a "SINCE SLICE 3" corrective addendum (§B-3).** Do not rewrite; prepend a short
   block: "This briefing is accurate for the token/core era (Slices 1-3). Since written, the Glyphic
   LANGUAGE ENGINE (G0-G11 — read-out/parse/multi-target/data-binding/glyphgraph render) was built +
   verified, and PHASE RECONCILE (R1 edge law, R2 referent-words-as-data) landed. Boot from
   `build-prep/the-one-system/glyphic/REGROUNDING.md` + CRITERIA.md for current state." Correct §7/§9.

5. **SYSTEM-GAPS.md — add a header note (§D).** "Slices 1-3 items (zoning/ramp/grid/texture/depth/
   containment/axes/status) are CLOSED — see analysis/FINDINGS-LOG. The still-open items are the
   component-library (Slice 4) + motion/interactive-bridge (Slice 5) tier, which overlap the glyphic
   product-integration work (REGROUNDING §6)." So it stops reading as an all-open to-do.

6. **ROADMAP.md — adopt the charter's charges (§E, tentative).** (a) PHASE CONVERGENCE: reference
   THE-GENERATIVE-LANGUAGE §2's 16-face fusion map as the convergence worklist, not a vague "scoped
   read+fuse." (b) Add the **provision / product-bar** charge (organisms, atmosphere, evidence density,
   zones on the canvas — the "80% frames-without-furniture" gap) as explicit items under PHASE REMAINING,
   since REGROUNDING §0/§6 make it THE standard. (c) Note two-wayness (edge law) as a STANDING invariant
   (checker class) across the build, not only R1. (d) Add the missing narrative-arc organ (sequence.json
   face) as a read-out item. Mark all tentative — these widen scope, so they walk through Tim.

7. **THE-GENERATIVE-LANGUAGE.md — correct the octagon blur (§B-1).** [O] §2's shapes.json row
   (line 136) folds `octagon=gateway` (the retired referent word) into the CV_MEANING-forms cell next to
   `octagon once` (brand cardinality). Separate them: the brand entity-shape (octagon = Virtual Hubs) is
   observed DNA; the read-out word is retired field-data. A one-line correction keeps the charter true.
   *(This edits a charter doc — flag to the lead before touching; charter docs are Tim-authored.)*

---

**Marks legend:** every claim above is [O] Observed (file:line) unless tagged [I] Inferred or [V]
Verified. The two-layer octagon reading (§B-1) and the charter-gap verdicts (§E) are the load-bearing
INFERENCES — flagged as such; they rest on doc-level reading, not code execution. READ-ONLY on all
sources; I wrote only this census file.
