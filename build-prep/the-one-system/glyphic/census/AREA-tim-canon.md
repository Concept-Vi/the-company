# AREA — TIM CANON (the pages where Tim's decisions are recorded)

> Census reader-teammate report. Territory: the four system/ pages + two analysis/ MDs that hold
> Tim's actual recorded decisions vs. AI presentation. READ-ONLY on sources; this is the only file
> I wrote. Marks: **Observed** (in the file, cited file:line) · **Inferred** (labelled) · **Verified**
> (I ran/traced it). The seat's root failure was replacing what Tim wrote with its own determinations;
> this report recovers what he wrote, first-hand, and names every place a seat disposition diverges.

---

## §A · PAGE-BY-PAGE ACCOUNT

### A1 · `system/glyphic-system.html` (75.2K, 660 lines) — THE Q&A / DECISION PAGE
**The single most important file in this whole territory.** It is the living spec Tim explicitly asked
for as a *markup surface* — the page carries his TWO verbatim messages in full (§1, §1b), the AI's
decomposition, the facet model, the codebase research, the build log (§6, with per-step `· BUILT`
markers), and the **Open Questions** (§7) that record what Tim has and hasn't decided.

- **Structure (Observed):** masthead → §00 orientation → §01 brief verbatim → §01b brief-addendum
  verbatim → §02 decomposition → §03 facet model (live specimens via `CV_GLYPHIC.render`) → §03b
  cumulative facet walk → §04 codebase research → §05/§05b–e universal-component grammar (slots/sockets/
  anatomy/declarations) → §06 the plan (8 steps, most `· BUILT`) → §07 open questions → §08 universal-axes.
- **Live or abandoned (Inferred, structural):** it renders live specimens (line 519 `GL = CV_GLYPHIC`;
  §3 facet table + §3b matrix injected from the real renderer). ADVISOR-AUDIT §4 verified it consumes
  ONLY `CV_GLYPHIC.render/compose` (line 519) — a specimen consumer, untouched by R1/R2 throw-paths. So:
  **live surface, and the canonical record of Tim's decisions.** Not abandoned.
- Its own status badges (line 147-149): "Foundations built · Naming 'Glyphic' · For Markup & direction."

### A2 · `analysis/LANGUAGE.md` (4.9K, 70 lines) — THE FOUNDING LANGUAGE SPEC (Tim-dated)
The founding spec of the *language* layer, explicitly dated and attributed **(Tim, 2026-06-29)** in its
header (line 6) and again at line 48 ("Tim's additions"). This is where the recorded **parts-of-speech
vocabulary** lives — the FORM / FILL+OUTLINE / COLOR / TEXTURE / EDGE word-tables (lines 33-49). It is a
descriptive-register founding doc, not AI-invented presentation. **This is the primary vocabulary source
for §C below.**

### A3 · `system/language.html` (13.8K, 199 lines) — LIVE LANGUAGE SURFACE
The live "marks that say themselves" page. Renders via the real engine (`cv-meaning` + `cv-glyphics`,
lines 78-79), computes every sentence live (`GL.describe`, `M.readGraph`), loud-fails on unknown values
(line 38, 99). Contains a real laid-out glyphgraph (a project graph, lines 143-156) with its read-out
computed live. **Live surface**, AI-authored presentation wrapping the real engine. It hardcodes
`kind:'face'` and `kind:'part-of'` in its demo graphs (lines 110-111, 152-154) — see §C/§D.

### A4 · `system/the-whole-thing.html` (37.1K, 451 lines) — AI-AUTHORED VISION WALK
Explicitly **"Written by the language seat after the full immersion walk … 2026-07-02"** (line 2). This
is AI presentation, not a Tim decision record. It attributes "Author of all principles: Tim Geldard"
(line 2, 314) and quotes Tim in two places (see §B), but the *page itself* — the seven zones, the fusion
map, the law matrix — is the seat's synthesis. **Live surface** (renders 5 live glyphgraphs via the real
DiagramSolver + readGraph, lines 435-447). Its demo graphs are the biggest concentration of the
`kind:'face' / 'projection-of' / 'mirrors' / 'part-of' / 'seeds' / 'resolves' / 'navigates'` edge kinds
(lines 364-420) — central to audit flag 1 (see §D).

### A5 · `system/system-map.html` (87.0K, 1031 lines) + `analysis/SYSTEM-MAP-ENCODING-GRAMMAR.md` (5.8K)
A **codebase-structure canvas** (a file-tree/dependency map of claude-ds itself), NOT a glyphic-language
surface. It consumes `CV_MEANING` in a *different* capacity than the language layer: through the
**encoding profile** `CV_MEANING.encodings('system-map')` (SYSTEM-MAP-ENCODING-GRAMMAR.md:5-8; baked into
`system-map.json` by `build-system-map.js`; loaded as `ENC = DATA.encoding`, system-map.html:333-342,
887). It also has its OWN separate edge-type registry (`EDGE_TYPES`, system-map.html:789-793) with three
verb-pairs: `contains/sits-inside`, `loads/loaded-by`, `resolves/resolves-into`. **Live surface** (a
working canvas app). See §D for how this second edge registry bears on the edge law.

---

## §B · THE TIM-DECISION REGISTER (verbatim quotes + file:line — THE HEART)

> Only material *attributable to Tim* is here. His two verbatim brief-messages are the deepest source;
> the dated LANGUAGE.md header + line-48 "Tim's additions" are the other first-hand records. Everything
> else on these pages is AI decomposition/presentation and is NOT in this register.

### B1 · The naming decision — "Glyphic" (DECIDED by Tim)
- glyphic-system.html:157 (Observed): *"You named the unit a **Glyphic**; the facet names are still
  provisional — rename freely; the structure is the part I'm asking you to react to."*
- glyphic-system.html:482 (Observed, §7, marked ✓ decided): *"**Naming — decided.** You named the unit a
  **Glyphic**; it's now the registry name (`CV_GLYPHIC`). Facet names (Form / Symbol / Fill / Colour /
  Texture / Motion / Size / Depth) are still open — rename any."*
- **Recovered decision:** Tim named it **Glyphic**. The eight FACET NAMES were left explicitly OPEN by
  Tim — "rename freely" / "still open."

### B2 · The Form axis — Tim's verbatim (the "n+1" polygon progression)
- glyphic-system.html:167 (Observed, Tim verbatim §1): *"The outer ring can be any polygon up to 8 from
  zero (the lack of outer ring) with a simple n + 1. In the centre, is the actual icon, the distinct
  symbol representing a distinct 'thing'."*
- **Recovered decision (Tim's own words):** the ring = polygon **0 (no ring) → 8**, "n+1"; the centre =
  the distinct symbol. NOTE: the "circle = ∞" upper end is the AI's proposal (glyphic-system.html:414,
  484 asks Tim to *confirm* `circle = ∞` — an OPEN QUESTION, not a Tim decision).

### B3 · The three independent regions (ring / symbol / fill), meaning multiplies — Tim verbatim
- glyphic-system.html:167 (Observed, Tim §1): *"All parts, outer ring, the internal icon, the space
  between them/fill/background, are independent of each other, and so the combinations multiply the
  meanings/possibilities."*
- glyphic-system.html:167 (Observed, Tim §1): *"Shapes and icons can have distinct meaning,
  generatively."* … *"what it represents is a variable, for compositional use."*
- **Recovered decision:** orthogonal facets whose meanings MULTIPLY; meaning is a *variable* per use —
  this is Tim's own seed of "meaning is a field / contextual," first-hand.

### B4 · Fill is part of the ring, not a third equal part — Tim's self-correction (verbatim)
- glyphic-system.html:178 (Observed, Tim §1b): *"I've been referring to the fill as a third and equal
  piece, but I'm now realising that I think it's actually a part of the outer ring … it has space inside
  it, and now that I think about it, it also has Space outside it technically … the actual glyphic itself
  is a perfect square in terms of its actual component/element."*
- **Recovered decision:** Tim RE-STRUCTURED the anatomy himself: element = a **perfect square**; the ring
  bounds an **inner space (fill)** and an **outer space**; fill is a sub-part of the ring, not a peer.

### B5 · Slots & sockets — Tim's coined vocabulary (verbatim, kept)
- glyphic-system.html:178 (Observed, Tim §1b): *"I called them slots and sockets because I don't know any
  of the industry terminology … the slots are the values that each thing can take … and sockets are what
  a glyphic can fill, like whatever other container types that glyphics can populate … a socket could be
  on a trigger event as well, like an on click action."*
- glyphic-system.html:311, 482-alike (Observed, AI honouring it): *"Your coinage is good and I'll keep
  it."*
- **Recovered decision:** Tim's OWN terms **slot** (a value a part accepts) and **socket** (a typed thing
  / event-trigger a component accepts) are canon, by his coinage. Kept.

### B6 · Everything is a universal component; one mechanism; type registries declare themselves — Tim verbatim
- glyphic-system.html:178 (Observed, Tim §1b): *"in any interaction or interface, everything on it and in
  it is a templated dynamic component thing … they are one thing, they are a universal component, but
  that's just one kind … they all have the same slot socket universal component Architecture but [are]
  distinct things … Everything is one of those, and they're all in registries, what I've been referring
  to as type registries … every type declares itself and it's parts."*
- glyphic-system.html:178 (Observed, Tim §1b): *"those declaration and rules are what renders and
  governance the interface, like there's no extra code for it … if I click on it … it can automatically
  show me the library of things that can fill it, without writing specific code for it."*
- **Recovered decision:** the universal-component grammar (Types declare parts/slots/sockets/conditions;
  the interface is a projection of the declarations, no bespoke per-screen code) is **Tim's own
  architecture**, stated verbatim — not an AI invention. This is the resolution-first / registry-is-truth
  law in Tim's own words.

### B7 · Build faithfulness as foundation-and-example — Tim verbatim
- glyphic-system.html:178 (Observed, Tim §1b): *"it is important to get the implementation and build of
  this to be the most faithful to the theory and purity of the manifestation to be its best, because
  everything else that we build for it will use what you are making now as both the foundation and the
  example."*
- **Recovered mandate:** the Glyphic build is the *reference implementation* of the whole grammar;
  faithfulness to the theory is a stated requirement, not a nicety.

### B8 · The AI mark-foundry (generate → options → feedback → save) — Tim verbatim
- glyphic-system.html:167 (Observed, Tim §1, sub-comment): *"I will want the AI system built into the
  icon system, so it can generate icons for me … see options, have a multi-step conversation, updating on
  screen and me giving feedback and clicking options it generates for me until I click a save button …
  include the tags and descriptions and allocating to categories … best to make through schemas or
  something."*
- **Recovered decision:** the conversational foundry (propose N → feedback → iterate → Save; schema-first)
  is Tim's spec. Status: capabilities built, UI pending (glyphic-system.html:443-444, gated by Tim on
  §7 sign-off + a live provider).

### B9 · The meaning/language layer — dated Tim record (LANGUAGE.md)
- LANGUAGE.md:6 (Observed, attributed): *"the meaning lives in the facets, never borrowed from another
  language. (Tim, 2026-06-29.)"*
- LANGUAGE.md:9-12 (Observed, "The one law"): *"**Meaning is a field, not a single thing.** … A thing
  that means one fixed thing is a lookup, not a language. And meaning is **combinatorial**."*
- **Recovered decision:** the foundational law Tim's 2026-07-03 correction #2 re-states ("nothing has one
  fixed meaning") was ALREADY WRITTEN HERE, dated 2026-06-29. The correction is not new doctrine — it is
  Tim insisting the code conform to what LANGUAGE.md already recorded.

### B10 · The line-routing additions — attributed to Tim (LANGUAGE.md)
- LANGUAGE.md:46-48 (Observed): *"line = the relation's mood (solid=is, dashed=could, dotted=tentative,
  lines=ongoing, **right-angled=routed, curved=organic, free=loose** — Tim's additions)."*
- **Recovered decision:** the routing mood-values (right-angled / curved / free) are **Tim's additions**,
  explicitly. (They are LINE facets — mood — not edge KINDS; see §D.)

### B11 · "Glyphic = address; edges are the verbs" — the language-at-two-heights record
- LANGUAGE.md:56-59 (Observed): *"Addresses are the **nouns**, edges the **verbs** … a glyphic are the
  **same language at two heights**."*
- **Recovered principle (dated Tim record):** the convergence principle (glyphic ≡ address; edge ≡
  relation_type) is recorded here — the ground under G6 and the edge law.

### B12 · Two Tim-quotes carried in the-whole-thing.html (channel-relayed; treat as PROPOSAL-grade)
- the-whole-thing.html:255 (Observed, quoted): *"my cognition is a projection of the same language of the
  universe; I am a composition and a coordinate."*
- the-whole-thing.html:2, 314 (Observed, attribution): *"Author of all principles: Tim Geldard."*
- **Caution (Inferred):** these are quotes *the seat placed on an AI-authored page*, not a decision
  surface Tim marked up. Per the `channel-relayed-is-proposal` rule, treat as the seat's rendering of
  Tim's words, not a first-hand mark-up. B1-B11 are the trustworthy first-hand register.

---

## §C · VOCABULARY COMPARISON — recorded words vs currently-seeded words (audit flag 3)

> The audit's flag 3 asks: does my territory contain PRIOR recorded wordings that R1/R2 should have used
> instead of freshly-invented starters? I compared the seeded words in cv-meaning.js (R2 lines 366-383,
> R1 lines 431-458 — read first-hand) against the recorded vocabularies in LANGUAGE.md and
> glyphic-system.html. **Headline: for the FORM referent words, the R2 seed MATCHES the recorded
> LANGUAGE.md vocabulary exactly — no mismatch. The one real divergence is a SECOND, older form-vocabulary
> in glyphic-system.html that neither matches nor was reconciled. For EDGE words, R1's inverses are
> genuinely new invention with no prior recorded wording to draw on.**

### C1 · FORM referent words — MATCH (LANGUAGE.md ↔ R2 seed)
| Form | LANGUAGE.md:33-35 (recorded, Tim-dated) | cv-meaning.js R2 seed (366-371) | Verdict |
|---|---|---|---|
| octagon | "a gateway" | kindWord `gateway` | **MATCH** |
| hex | "a system" | kindWord `system` | **MATCH** |
| pentagon | "a feature" | kindWord `feature` | **MATCH** |
| heptagon | "a special case" | kindWord `special type` | ~match (near-synonym) |
| triangle | "an operation on it" | opWord `action on` | ~match (near-synonym) |
| diamond | "interacting with it (deciding is one kind)" | opWord `use of` | ~match (narrows to "use") |
| circle | "the kind itself" | (determiner-driven; no kindWord) | consistent |
| square | "a specific one" | (determiner-driven) | consistent |

**Verified (structural):** R2 did NOT invent fresh FORM words — it lifted the LANGUAGE.md vocabulary
into profile data. So the A1/R2 move is *conformant to the recorded canon*, not a divergence. The word
'gateway' that Tim's correction #2 singled out ("an octagon does not mean gateway, an AI just wrote that
there once") traces to **LANGUAGE.md:35 (2026-06-29)** — i.e. it was recorded in a dated language spec,
though as a *seed dictionary that "grows in use"* (LANGUAGE.md:32), never as a fixed definition. R2's fix
(make it authorable field data, not a const) is exactly the right response to the correction.

### C2 · A SECOND form-vocabulary exists in glyphic-system.html — UNRECONCILED (the real mismatch)
glyphic-system.html carries a DIFFERENT set of form-type words, never reconciled against LANGUAGE.md's:
- glyphic-system.html:247 (Observed): the shape-types *"Entity/Action/Object/Decision/Feature/System/
  Specialised/Gateway"* (8 types, from `CV_SHAPES.shapeTypes`).
- glyphic-system.html:525 (Observed, §3 facet table): Form *"means: type-class — Entity / Action / System
  / Gateway …"*
- glyphic-system.html:485 (Observed, §7 OPEN QUESTION, **never answered by Tim**): *"**Meaning
  vocabularies.** The 8 shape-types are my proposal — do they match how you think about your entities, or
  should the type list change?"*

**The mismatch (Observed):** there are TWO recorded form vocabularies —
(a) LANGUAGE.md's read-out phrasing (gateway/system/feature/special-case/operation/interacting), and
(b) glyphic-system.html's *type-class* names (Entity/Action/Object/Decision/Feature/System/Specialised/
Gateway from CV_SHAPES). They overlap (Gateway, Feature, System) but are NOT the same list, and Tim was
asked which he wants (§7) and **never recorded an answer.** R2 seeded from (a). This is a genuine open
canon question the seat's plan does not flag. **Neither is "wrong"** — LANGUAGE.md's are *sentence words*,
glyphic-system.html's are *type-class labels* — but the relationship between the two is unrecorded, and
per correction #2 (nothing has one fixed meaning) both should be field-shaped, contextually-resolved, not
two frozen tables.

### C3 · FILL / OUTLINE (mode) words — MATCH with a small extension
| Value | LANGUAGE.md:37-39 | cv-meaning.js R2 seed (377-383) | Verdict |
|---|---|---|---|
| none | "held as a concept" | 'held as a concept', determiner `the` | **MATCH** |
| paper | "here, in context (+icon → present)" | 'here, in context', determiner `this` | **MATCH** |
| wash | "featured" | 'featured', determiner `this` | **MATCH** |
| dashed (outline) | "potential" | 'potential', determiner `a possible` | **MATCH** |
| solid | "full/set (flagged: needs a solid-colour fill value)" | 'full / set', determiner `the` (marked aspirational) | **MATCH + flag preserved** |

**Verified (structural):** the mode vocabulary was also lifted faithfully from LANGUAGE.md, including the
"solid needs a real fill value" flag (cv-meaning.js:381 comment mirrors LANGUAGE.md:39). No invention.

### C4 · EDGE words — R1's inverses ARE fresh invention (no prior recorded wording)
The recorded EDGE material is thin. LANGUAGE.md:46-48 records edge as *"the relation-carrier, not a
verb"* and names only **face / higher-order / navigates** as example relations (line 48), plus the LINE
moods and the routing values. It records NO inverse-wordings, and 'documents'/'part-of'/'projection-of'/
'mirrors' are NOT in LANGUAGE.md's edge list at all.

So R1's seeded inverse phrases — `faced by`, `documented by` / `a guide to`, `the container of`,
`grown from`, `projected as`, `framed by`, `the higher concept of`, `resolved into` (cv-meaning.js:432-458,
read first-hand) — are **genuinely new AI wording with no prior recorded wording to prefer instead.** This
is legitimate under G4.5/A5 (seed sensible starters, tune live) — my territory does NOT contain a "should
have used X instead." **The problem is not the words; it is (a) the KINDS they attach to (§D) and (b)
that most are NOUN-PHRASES, not the directional VERBS Tim's edge law requires** (correction #3). LANGUAGE.md:47
already frames edge as "the relation-carrier, NOT a 'verb'" — a tension with the verb-pair law that the
seat has not surfaced (matches audit flag 3's noun-phrase-vs-verb note).

---

## §D · FICTION / DRIFT between pages and engine (audit flags 1 & the fiction check)

### D1 · 'face' and 'documents' appear ONLY in AI-invented material, never in Tim-recorded material (answers audit flag 1 (c))
**Verified (grep + read):** the relation `kind:'face'` appears in my territory ONLY inside AI-authored
demo graphs — language.html:110-111, 154; the-whole-thing.html:364-367. It does NOT appear in Tim's two
verbatim messages (glyphic-system.html §1/§1b — the only "face" hits there are CSS/`.facet`/`surface`
tokens, Verified by grep). 'documents' appears in NEITHER Tim material NOR my territory's demo graphs at
all — it is purely a cv-edges.js kind (confirmed June-flagged-invented in the ledger). LANGUAGE.md:48
lists **face / higher-order / navigates** as the example relations, in a *descriptive, dated* doc — this
is the closest to a recorded home for 'face', and it frames 'face' as the design-faces/page-face concept,
NOT as a Tim-authored decision. **Conclusion supporting audit flag 1:** 'face' has a thin descriptive
recorded basis (LANGUAGE.md:48, cv-edges.js header = "the page is the visible face/projection of the
source"); 'documents' has none in my territory and is invented. R1 authoring a brand-new meaning field
for 'documents' ('a guide to' ↔ 'documented by', cv-meaning.js:433-434) reads as LEGITIMIZATION of the
June-flagged-invented relation — exactly the audit's flag-1 concern, and it contradicts correction #3
("'documents' as an edge kind = drift").

### D2 · The demo graphs speak MANY edge kinds the edge-law disposition hasn't cleared
the-whole-thing.html's five live graphs use: **face, projection-of, mirrors, part-of, seeds, resolves,
navigates** (Observed, lines 364-420). language.html uses **face, part-of** (110-154). These are all
currently rendering live. Under correction #3 + A2, each must be a directional verb with an equal-and-
opposite OR be re-dispositioned Tim-visible. R1 gave them inverses in the meaning profile (composed at
read), which satisfies the grammar — BUT the pages still hardcode the raw `kind:` strings, and the
"Tim-visible surfacing" of face/documents (A2's own requirement) has no vehicle. **This is live fiction-
risk only if a kind loses its meaning field** (then readGraph throws) — ADVISOR-AUDIT §4 verified no
current breakage, but these pages are the exact surfaces that would break, and no chrome pass is recorded
post-R1/R2. (Not my remit to run chrome; flagging for the loop.)

### D3 · language.html narrates a NOT-YET-BUILT feature (honest fiction flag)
language.html:55-61 (Observed) promises, in prose: *"(Next: the relation's **type** by sight — a small
relation-glyph at the line — so a dashed 'part-of' can't be mistaken for a dashed 'face'; today type is
read on hover / labels.)"* — this is an *honest* "Next:" label (not claimed as built), so it is NOT
fiction by the no-fiction rule, but it names a real GAP: **edge TYPE is not yet visually distinguishable
without hover/labels** — two dashed edges of different kinds look identical. This bears on G5.1's "reads
without text labels" claim (CRITERIA G5.1 ☑): the graph reads *mood/state/direction* without labels, but
NOT relation-TYPE. A latent tension with the ☑ on G5.1. Worth surfacing to the render lane.

### D4 · glyphic-system.html §6 build-log — a completeness claim to verify, not trust
glyphic-system.html §6 marks 7 of 8 plan steps `· BUILT` and the schemas `· BUILT` (lines 408-448). Per
the `critical-comparison / built-means-usable` rules these are *claims on a presentation page*, not
verification. ADVISOR-AUDIT independently re-ran the harnesses and found the engine genuinely far more
complete than the seat's own assessment claimed — so these BUILT markers are broadly *corroborated* by
the verifier run, NOT drift. I flag them only so the loop treats §6 as a claim-surface (it is authored
prose), not as the source of truth (the harnesses are).

### D5 · glyphic-system.html §7 open questions — Tim's UNANSWERED decisions (the live canon gaps)
§7 (lines 481-488, Observed) records SIX questions put to Tim, of which only Naming (✓) is answered:
1. v1 facet set (which facets ship first) — **unanswered**
2. Form-axis ends: confirm `0=no ring` and `circle=∞`; are 1-/2-side steps wanted? — **unanswered**
3. Meaning vocabularies: do the 8 shape-types match Tim's entities? — **unanswered** (the §C2 mismatch)
4. The value variable: what real value-sets (status / entity-type / lifecycle)? — **unanswered**
5. Taxonomy depth for symbols — **unanswered**
6. (§08 carried) per-axis cards, socket-conditions engine, foundry UI — **carried, not decided**
**These six are the recorded live canon-gaps.** The seat's plan (CRITERIA/ROADMAP) does not carry them
as an explicit Tim-decision queue. Correction #5 (correctability-by-use) says don't gate on them — but
they should be *surfaced* as the live-tune questions they are, not silently defaulted by the seat.

### D6 · system-map.html's second edge registry — a parallel to reconcile (bears on G3.4 / the edge law)
system-map.html:789-793 (Observed) defines its OWN `EDGE_TYPES` (contains/loads/resolves) with
bidirectional verb-pairs (`fwd`/`rev`), and its header comment (lines 785-788) states the law in Tim's
shape: *"An edge type IS a verb pair (forward describes from→to, reverse describes to→from) — never an
opaque name."* This is a SECOND edge-relationship registry, *outside* the glyphic meaning home — exactly
the class of thing G3.4 forbids ("no second edge registry"). **BUT:** it is a codebase-*structure* map
(files loading/resolving files), a different domain than the glyphic language's relations, and it already
independently encodes Tim's equal-and-opposite law. **Disposition question for the plan (§F):** is this a
drift to unify into the one edge home, or a legitimately-separate structural-map vocabulary? It is NOT in
the seat's edge-law scope (R1 touched only cv-edges/cv-meaning/relationships-seed). Flagging as
newly-surfaced (resolve-divergence-into-scope): at minimum it proves Tim's verb-pair law was ALREADY
independently discovered/recorded in this page's comment — corroborating that the law is Tim's, not an
A2 invention.

---

## §E · DISCONNECTED / ABANDONED PAGES
- **None are abandoned.** All four system/ pages render live: glyphic-system.html (specimen consumer),
  language.html (live engine), the-whole-thing.html (5 live graphs), system-map.html (live canvas).
  (Inferred from script wiring + ADVISOR-AUDIT §4's verified consume-trace of glyphic-system.html.)
- **Register-mismatch note (Observed):** glyphic-system.html and the-whole-thing.html are AUTHORED
  PRESENTATION pages (dense, for-Tim-markup and for-the-record respectively) — per
  `board-is-workspace-not-reading`, they are agent/record surfaces, not Tim's reading register. Their
  BUILT markers and law-claims are authored prose to be verified, never trusted as source (§D4).
- **The one true DECISION surface** is glyphic-system.html §1/§1b/§7 (Tim's verbatim + his open
  questions). LANGUAGE.md is the one true dated LANGUAGE-canon. Everything else is presentation over the
  engine.

---

## §F · PROPOSED PLAN-FILE EDITS (tentative — where a seat disposition meets recorded canon)

> Written provisionally with sources. These are proposals for the lead/loop, not applied edits.

1. **CRITERIA A1 / §C1 — ADD a note that the R2 FORM words are CONFORMANT to recorded canon, not
   invented.** A1 currently frames the referent words as consts to be freed. TRUE — but §C1 shows the
   *words themselves* (gateway/system/feature…) trace to the dated LANGUAGE.md:33-35 vocabulary, so R2's
   seed is a faithful lift, not a fresh invention. Proposed: add to A1/the READING-LEDGER R2 entry —
   "the seeded kindWords match LANGUAGE.md (Tim, 2026-06-29); A1 frees them to be *authorable*, it does
   not replace an invented word with a better one." (Prevents a future session 're-deciding' words that
   are already the recorded canon.)

2. **CRITERIA A2 / §C2 — SURFACE the two-form-vocabulary mismatch as the recorded open canon-question it
   is.** glyphic-system.html:485 records Tim being ASKED whether the 8 CV_SHAPES type-classes
   (Entity/Action/Object/Decision/Feature/System/Specialised/Gateway) match his entities — **and never
   answering.** The plan should carry this as a live-tune / Tim-visible question (correction #5), not let
   R2 silently canonise the LANGUAGE.md list while the CV_SHAPES list still lives in cv-shapes.js. Both
   must become field-shaped (correction #2), and their relationship recorded.

3. **CRITERIA A2 / §D1 — STRENGTHEN the 'documents' disposition against recorded canon.** Audit flag 1
   already flags that R1 gave 'documents' a new AI meaning field (legitimization). §D1 confirms
   'documents' appears in NO Tim material and NO territory demo graph — its only home is cv-edges.js, and
   LANGUAGE.md does not list it. Proposed: A2 should say plainly that 'documents' is *retired unless
   re-authored through the Tim-visible door* (per correction #3 "'documents' as an edge kind = drift"),
   and that R1's meaning-field for it is a STARTER pending that surfacing — not a settled citizen. The
   demo pages (the-whole-thing / language) do not use 'documents', so retiring the kind breaks nothing
   there (Observed).

4. **ROADMAP / §D2+D3 — ADD "chrome pass over the three live language pages after R1/R2" as an explicit
   line, and add the edge-TYPE-by-sight gap.** language.html:55-61 records the real gap (two dashed edges
   of different kinds are visually identical today), which sits in tension with G5.1's ☑ ("reads without
   text labels"). Proposed: a RECONCILE-phase line — verify the live pages render post-R1/R2 (the audit
   found no *static* breakage but no browser pass exists), AND treat "relation-type by sight" as open G5
   FORM work, not silently-covered by the G5.1 ☑.

5. **CRITERIA G3.4 / §D6 — NOTE system-map.html's second edge registry as a surfaced divergence to
   disposition.** It is a real second edge-relationship registry (system-map.html:789-793), currently
   outside the edge-law scope. Proposed: add to the edge-law disposition list a decision — unify into the
   one edge home (if the structural-map relations are the same language at another height, per
   LANGUAGE.md:56-59) OR record it as a legitimately-scoped structural vocabulary. It ALSO independently
   encodes Tim's verb-pair law (comment lines 785-788), which is *corroborating evidence* the edge law is
   Tim's, worth citing in A2.

6. **CRITERIA / §B9+B12 — CITE LANGUAGE.md (Tim, 2026-06-29) as the DATED first-hand home of "meaning is
   a field," and DOWNGRADE the-whole-thing.html Tim-quotes to proposal-grade.** Correction #2 is not new
   doctrine; it re-asserts LANGUAGE.md:9-12. Proposed: the amendments should cite LANGUAGE.md as the
   recorded canon they conform TO (strengthens the "original plans ARE the job" frame), and note that
   the-whole-thing.html's Tim-quotes are seat-placed (channel-relayed-is-proposal), so B1-B11 are the
   trustworthy register, not the vision-walk page.

---

## Marks legend applied
Observed = cited file:line, seen directly. Inferred = labelled, structural reasoning. Verified = I ran
the grep / traced the consume-path myself (D1 grep; C1/C3/C4 cross-read of cv-meaning.js R1/R2 seed
lines against LANGUAGE.md, first-hand). No source files were edited; this census file is the only write.
