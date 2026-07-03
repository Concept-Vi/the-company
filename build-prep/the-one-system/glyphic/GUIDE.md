# Glyphic Language — Implementation Guide (the how)

> HOW to build each criteria item. Rests on SYNTHESIS.md (ground truth) → drives CRITERIA.md.
> Tense is exact: **IS** = exists now; **WILL BE** = to build. Governing model: a glyphgraph is a
> **meaning representation** (Conceptual-Graph / AMR style) — concepts + typed relations — NOT a
> process/flow diagram. Every layer LOUD-FAILS (no fallback, no silent default). One home per thing.

## North-star principles (why, not just what)
1. **Meaning is a field, not a single value** — `(facet,value) → {feeling, senses[], type}`. A
   lookup-to-one-string is not a language. Combinatorial: the *combination* means.
2. **The sentence is a projection (transglyphing), not the meaning** — meaning lives in the graph;
   English is one target. So storage = the graph + fields; the read-out is a separate, replaceable step.
   The test for a read-out: *"can you hear the octagon?"* — if the sentence betrays it came from a
   picture (narrates shapes: "holding/featured/at rest"), it is WRONG. It must read like a thing a
   person would say about the subject, shapes invisible.
3. **A single glyph is a NOUN PHRASE (a referent), not a sentence.** Only a relation (≥2 nodes + edge)
   is a sentence. Never emit a full sentence for a lone node.
4. **form ⟂ fill** — form = *what kind* (circle=the kind/category, square=a member/instance, triangle=
   an operation, diamond=interacting-with, octagon=gateway, hex=system…); fill = *mode of reference*
   (none=concept, present=this, dashed-outline=potential, full=set). Keep orthogonal — do NOT let form
   do definiteness.
5. **Don't invent meanings** — seed only what Tim confirmed or what is genuinely in the visual feeling.
   Glosses (icon→word) and uncertain readings get flagged, not guessed.
6. **Extend-by-registration, no parallels** — see SYNTHESIS "Do-NOT-duplicate".
7. **One mechanism — variable resolution.** A glyphic is ONE thing, ONE operation. It has no private
   engine: its **values** resolve from the token graph, its **identity** from the address system, its
   **meaning** from the meaning registry — all the *same shape of operation* (a reference resolved against
   a single source). The language is an INSTANCE of the system's universal variable-resolution primitive,
   not a parallel subsystem. (Tim: "kinda the same mechanism as everything else.") Never fork the resolver.
8b. **Two read-outs, never conflated (Tim, 2026-06-30).** There is a DESCRIPTION layer and a MEANING
   layer, and they are separate artifacts: **describe/inspect** narrates a glyph's *facets* ("a square,
   present, frosted, at rest") — a check of what a mark is *made of*, NOT the language. **transglyph/
   meaning** is the *referent + relation* reading ("this file could become a page") — the actual language.
   Never label the facet-narration "the language." The inspector is un-gated; the meaning read-out's
   WORDING is gated on Tim's ear (G4). Keep their names + capabilities distinct (glyphic.describe vs the
   reserved glyphic.transglyph).
8. **Live dual-authoring is the point.** The language is WRITTEN over time, live, by Tim AND the integrated
   AI with EQUAL tools, through conversation and/or the interface. So the dictionary is DATA (profiles /
   registry records), never hardcoded; the engine is fixed machinery, the language is the data it resolves;
   the language's application AND development operate THROUGH the system itself, not by editing engine code.

## G0 — The one mechanism: variable resolution + live dual-authoring  (the foundation everything rests on)
**Principle:** this is the architecture Tim mandated and cannot guide on — get it exactly. Three unifications:
- **Resolution is one operation, three single-sources.** `meaning = CV_MEANING.field(facet,value)` ·
  `value = var(--token)` (the token graph / axes) · `identity = resolve_address(addr)`. Same shape; do not
  build a special language resolver. A glyphic resolves all three uniformly.
- **The dictionary is DATA, live-authorable.** Meaning lives in a loadable PROFILE (CV_MEANING already
  round-trips profiles to JSON). The seed dictionary is data, not fixed literals. Build a thin authoring
  API — `CV_MEANING.author.{setField, removeField, setRelation, setGloss, setOperator}` — that mutates the
  active profile + persists (export/load), LOUD-FAIL on malformed input (a field with no feeling throws).
- **Equal tools for user AND AI.** Expose authoring two ways from the ONE API: an interface panel (a Glyphic
  authoring surface, G7) AND an AI path (a Company MCP capability / the existing config-dials mechanism) so
  the AI can read the language in-context AND configure it. Both call the same `CV_MEANING.author`.
**Why it de-risks the disaster:** because every reading is live-authorable data, a wrong reading is a value
corrected live (by ear, through conversation/interface) — never baked into code. The read-out GATE (G4.5)
becomes "the mechanism lets Tim tune readings live," not "get every meaning right first." Seriousness =
data-driven + loud-fail + one mechanism, not up-front omniscience.
**Files:** MODIFY `cv-meaning.js` — ensure the seed is profile DATA; add the `author` API (mutates active
profile, persists via export/load, loud-fail). LATER: the interface panel (G7) + the AI authoring capability
(Company side). REUSE the token graph + `resolve_address` as the other two resolution sources — do not fork.
**Do/Don't:** DON'T hardcode any meaning the author API can't reach. DON'T give the AI a different authoring
path than the user — one API, two faces. DON'T fork resolution — tokens/addresses/meaning are one mechanism.

## G1 — The lexicon: the universal-operator sign-class  (foundation)
**Principle:** universal symbols carry near-universal meaning, so they buy expressiveness cheaply (logic
+ maths for free). `=` is *is / equals*, `≠` *is not* (negation), `+` *and/combined*, `→` *becomes/leads
to*, `⊂`/`∈` *part of/inside*, `?` *a question*, `!` *matters/urgent*. They act as **edges (relations) or
operator-nodes**.
**Files:** MODIFY `assets/icons/cv-edges.js` — add operator edge-kinds (`equals`, `not`, `becomes`,
`part-of`, `and`) with their meaning-fields (phrase + senses). MODIFY `assets/icons/cv-meaning.js` — seed
their FIELDS in the active profile (type `relation`/`operator`). REUSE `CV_ICONS` for the glyphs if present;
if a symbol isn't in CV_ICONS, ADD it there (loud-fail otherwise) — do NOT inline SVG.
**Do/Don't:** DON'T make `=` mean only "equals" — it's a field (*is / equals / is the same as*). DON'T
hardcode operator SVGs in the language layer — they're symbols in the icon single-source.

## G2 — New facets in CV_MEANING  (foundation for semantics)
**Principle:** the parts Tim named are independent meaning-bearing dimensions. Each gets a FIELD dictionary
+ a `MEANING_TYPE`, loud-fail on unknown value.
**WILL BE built in `assets/icons/cv-meaning.js`:**
- **independent ring vs symbol** — the ring (frame/determiner) and symbol (the thing) carry colour/motion
  independently. Read-out: ring-state modifies the *reference* ("the selected …"), symbol-state the *thing*.
  REUSE `glyphic-type.js` parts as the structural home; CV_MEANING seeds each part's facet fields.
- **line colour** — an edge's colour = the relation's STATE (red=blocked, green=approved, gold=active).
  ADD `lineColor` to the edge facets + fields; combine with line-style (mood) in the read-out.
- **size-as-comparison** — bigger = more/primary; a size DIFFERENCE between two nodes = "more than".
  ADD a `size` reading (comparative when two nodes differ, emphatic when absolute).
- **conditionals** — a dashed sub-structure = antecedent; reuse `CV_COND` to evaluate/representation. A
  relation/region marked conditional reads "if … then …".
- **negation** — the `≠`/`not` operator on a relation flips it ("was never sent"). Read-out inserts "not/never".
**Do/Don't:** DON'T merge ring+symbol into one state. DON'T add a facet without a field + a loud-fail path.

## G3 — The glyphgraph data model + the type graph (schema) + conformance
**Principle:** reuse the existing `CVGraph` IR as the sentence-as-data; make the registry the type graph;
make `accepts` + `CV_COND` the well-formedness validator (loud-fail = ungrammatical).
**WILL BE:**
- **Data model** — EXTEND `core/cv-nodes.d.ts` `CVGraph`: a node carries a full **glyphic-spec** (form,
  symbol, fill, color, texture, motion, ring/symbol parts) + an optional **`address`** (its real identity)
  + `x/y`; an edge carries a **relation-type id** + line facets (line, lineColor, direction) + `label`.
  This is additive — existing CVGraph consumers (DiagramSolver) keep working.
- **Type graph** — SEED `relationship` Types into the registry (fill `kind.graph`'s empty `accepts:
  ['relationship']` placeholder). Each: `{kind:'relationship', classification:['relationship'], sockets:{
  source:{accepts:[…node classes]}, target:{accepts:[…]}}, conditions:[…]}`. Operators (=, ≠, part-of…)
  are relationship Types too. NEW file `app/registry/relationships-seed.js` (mirrors `types-seed.js`).
- **Conformance** — a `validateGlyphgraph(graph)` that, for each edge, resolves its relation-type and checks
  source/target node-types via `CV_REGISTRY.accepts` + edge `conditions` via `CV_COND`. Returns the list of
  violations; **throws** on a malformed graph (loud). NEW: a small `glyphgraph.js` (the data-model + validator
  helpers) in `assets/icons/` or `core/` — REUSE CV_REGISTRY/CV_COND, don't reimplement.
**Do/Don't:** DON'T create a second edge registry — relationship Types ARE the edges. DON'T silently drop a
bad edge — throw. DON'T position-encode meaning the renderer owns; the data model is meaning, layout is G5.

## G4 — Transglyphing: readGraph (graph → sentence)  (THE proof)
**Principle:** generalise the existing `describe`/`describeRelation`/(planned)`readChain` to an arbitrary
graph. transglyphing = traverse a glyphgraph from a chosen focus and realise it as a sentence (one target;
the function signature takes a `target`, English first).
**Sequence (graph → text):**
1. choose a **focus/root** (the subject — explicit, or the most-connected/leftmost node).
2. compute each node's **referent** (NOT a facet recitation): determiner from fill-mode, kind from form
   (circle=kind/square=instance/…), thing from symbol-gloss, brief modifiers from colour/texture/motion only
   when notable. (Single node → just this referent.)
3. walk edges from the focus: each edge → a clause `[subject-ref] [mood+relation verb] [object-ref]`; mood
   from line-style (solid="is", dashed="could"), verb from the relation-type, negation from `≠`.
4. **coordination** (sibling edges of same kind) → "A and B"; **subordination/embedding** (an edge whose
   object is itself a sub-graph) → a relative/complement clause (recursion); **conditionals** → "if … then …".
5. assemble; the result reads like natural speech (apply "can you hear the octagon?").
**Files:** MODIFY `cv-meaning.js` — add `CV_MEANING.referent(spec)`, `readGraph(graph, {target,focus})`,
generalise the relation read-out; keep `describe` for a single node = its referent (a noun phrase). REUSE
`composeRelation`'s `.read` per-edge.
**Do/Don't:** DON'T narrate shapes. DON'T emit a sentence for a lone node — emit its referent. DON'T borrow
English grammar as the *substrate* — English is only the projection. DO offer 2–3 candidate readings where
the field is ambiguous (a future `readGraph` option), since meaning is a field.

## G5 — Render: DiagramSolver extension (the FORM surface)
**Principle:** reuse the solver's positioning + SVG substrate; add (a) a `glyphgraph` layout case, (b)
render each node as a **full glyphic** (`CV_GLYPHIC.render`) not a shape-clip, (c) edges carry meaning
**visually** — line-style/colour/direction/relation-glyph — so the graph **reads with NO text labels**
(a labelled diagram isn't a language); **edge labels are OPTIONAL, off by default**, revealed only on
select/hover/highlight (or a labels-mode) — never a dependency, (d) line **colour** + the new line-types.
**Files:** MODIFY `core/DiagramSolver.jsx` — add `case 'glyphgraph'` in `layout()` (start with authored
`x/y` + a simple layered/radial fallback; reuse the quadrant path that already reads x/y); in node render,
call `CV_GLYPHIC.render(node.glyphicSpec)`; edge labels behind a select/hover reveal (NOT drawn by default).
MODIFY `cv-shapes.js:edgeSVG` for line colour + right-angled/curved/free paths. OPTIONAL: `core/Slide.jsx` +
`core/archetype-catalog.js` add a `glyphgraph` archetype to make it a selectable type.
**FORM bar (design rubric):** built on design tokens (no hardcoded hex/px) · glyphs render correctly at the
node size · edges legible, labels not overlapping · the graph reads as a **navigable visual surface, not a
text-wall** · responsive. Verified by sight + a design-critic pass, not by "it rendered".
**Do/Don't:** DON'T add an early-return subtype view (those bypass positioning) — add a `layout()` case.
DON'T pull an external layout lib without checking the no-script-CSP/bundle. DON'T leave edge labels unrendered.

## G6 — Convergence: glyphgraph over real addresses (the islands-join)
**Principle:** a glyphgraph node = a real **address**; an edge = a **relation_type**. Same language, two
altitudes. This makes a glyphgraph a *statement about real things*, not a toy.
**WILL BE (held until G1–G5 ring true):** node `address` resolves via `resolve_address`; edges reuse
`relation_types/` (only branch a `glyphgraph_edges/` vocabulary if needed); later, a `glyphgraph://<frame>/<id>`
scheme (a new `resolve_address` branch, mirroring `decision://`). Keep the design-system render reading the
same graph the Company stores.
**Do/Don't:** DON'T add the `glyphgraph://` scheme until the design-side rings true. DON'T duplicate
relation_types — reuse.

## G7 — Product Face (standing, across all surfaces)
The language page (`system/language.html`) + the glyphgraph render held to the **design rubric**: design-
system components + tokens (no bespoke values) · no overlaps · responsive · consistent scale/type/spacing ·
a navigable visual/spatial surface (a commander recognises by sight) · empty/loading/error states · outcome
demonstrable. A surface is green on FORM only when a **design-critic** (browser, screenshots) passes it.

## Held for later (explicitly out of v1)
- **Reverse parser** (text → glyphgraph / semantic parsing) — the dream direction; needs G1–G6 solid first.
- **Force-directed / DAG layout** — only if authored-position + layered layout proves insufficient.
- **Multi-target transglyphing** (graph → code / other notations) — the signature generalises; targets later.


---

## THE CORRECTED LAWS (2026-07-03 — HOW-guidance for the amendments; criteria live in CRITERIA.md)

**Meaning is a FIELD, everywhere.** Whenever tempted to write `X = 'one sentence'` or a fixed lookup
table, the right shape already exists: a CV_MEANING field (feeling + senses + relation + gloss),
authorable via CV_MEANING.author. Extend the language in ITS shape — never mint a private const the
author API can't reach. The referent internals (REFERENT_KIND/OP, determiners) migrate into the profile
exactly the way line fields already carry `phrase`.

**Edges: one home, verb-pairs.** The flow is: meaning field ('edge', word) + relationship Type (family:
'relationship', + directed/inverse) → the seed union picks it up → geometry stays in CV_SHAPES/cv-edges
(look only). To add a verb: author the field, register the Type WITH its inverse, done — it renders,
reads, parses. Inverses are DECLARED once and composed at read (readGraph realises "A contains B" or
"B is contained by A" from ONE stored edge + focus) — never stored twice.

**Placement: the address IS the position.** cv-address spans give every node a relative address in its
parent frame; layout = resolving that address into the current viewport. A mutation re-partitions ONE
parent span; resolution cascades only within that boundary. Movement = the address diff (bounded, angled,
animated). Order-of-relation changes are the SAME operation on the ordinal dimension of the span. Authored
drag = a per-node override field, still relative to the parent.

**The wording loop.** Wording ships as seeded profile data; correction happens DURING generation in front
of Tim through the author API (setGloss/setField live). Building the easy correction path IS the gate.
