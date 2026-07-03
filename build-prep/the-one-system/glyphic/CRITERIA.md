# Glyphic Language — Completion Criteria (the truth-table)

> What must be **true** before this is done — not a task list. Each item is checkable only by
> demonstration. See GUIDE.md for HOW, SYNTHESIS.md for what exists. Status: ☐ DESIGNED (intended,
> unbuilt) · ◐ BROKEN/PARTIAL (exists, wrong or incomplete) · ☑ VERIFIED (confirmed by use).
> **STATUS RECONCILED 2026-07-03** against a full verifier run (all 13 _demo harnesses executed —
> see READING-LEDGER.md) + Tim's corrections (see AMENDMENTS at the end — they are CRITERIA).

## Verification protocol (the loop runs exactly this — both bars or not done)
- **FUNCTION bar** — verified BY USE, never by reading code: run the headless harness
  (`_demo/verify_*.js` under node — extend it per group) AND, for any surface, the live page in
  chrome-devtools. A read-out item is green only when the **real engine produces the real sentence
  from a real graph**, and every **loud-fail case actually throws** (no fallback, no silent default).
- **FORM bar (design rubric)** — for every surface, verified BY SIGHT (chrome screenshot) + a
  **design-critic** pass: built on design-system tokens/components (no hardcoded hex/px, no bespoke
  one-offs) · no overlaps · responsive · consistent scale/type/spacing · a **navigable visual surface,
  not a text-wall** · empty/loading/error states · outcome demonstrable. "It rendered, console clean"
  is the FLOOR, not the bar.
- **The read-out oracle** — for any transglyphed sentence: *"can you hear the octagon?"* If it narrates
  the picture (shapes/fills/motion), it is BROKEN, not done.
- No item is green on FUNCTION alone. Engine-only items (G1–G4, G6) have no FORM face and say so.

## Priority order (dependency — foundations first)
**G0 one-mechanism+authoring → G1 lexicon → G2 facets → G3 data-model+schema+conformance →
G4 transglyphing(readGraph) → G5 render → G6 convergence → G7 product-face.** G0 is the architectural
spine (everything resolves through it, everything is authored through it); G7 is assessed continuously on
every surface from G5 on.

---

## G0 — The one mechanism: variable resolution + live dual-authoring  (engine + the spine)
- **G0.1** the meaning dictionary is **DATA** — a loadable profile that round-trips to JSON; the seed is
  profile data, not fixed literals the author API can't reach. Export → edit → load round-trips faithfully. ☑
- **G0.2** `CV_MEANING.author` API exists — `setField/removeField/setRelation/setGloss/setOperator` mutates
  the active profile AND persists; a malformed input (e.g. a field with no feeling) **throws** (loud). ☑
- **G0.3** resolution is ONE mechanism, three single-sources — meaning via `CV_MEANING.field`, value via the
  token graph (`var(--token)`/axes), identity via `resolve_address`; NO parallel language-resolver exists
  (verified by grep + by reading: the read-out pulls meaning only from CV_MEANING, never inline). ☑
- **G0.4** the SAME `author` API is reachable by BOTH the user (interface panel, G7) and the integrated AI
  (a Company authoring capability) — one API, two faces; the AI can read the language in-context AND configure
  it. (AI path may land in a later pass, but the API must be built to serve both from day one.) ☑ (ai-glyphic-language.js = the AI face; the user panel rides G7)
- **G0.5** authoring through the system actually develops the language: adding a field/relation via `author`
  immediately changes what `readGraph` produces — verified by use (author a new operator → it transglyphs). ☑ (proven: 'contradicts' authored at runtime; parse() reads authored words for free)

## G1 — Universal-operator lexicon  (engine; no FORM face)
- **G1.1** `=` `≠` `+` `→` `⊂` `?` `!` exist as relation/operator entries with **field** meanings
  (feeling + senses), not single words. `CV_MEANING.field('edge','equals')` etc. return a field. ☑ for `= ≠ + → ⊂` · **`?` `!` RE-SCOPED**: they are ILLOCUTIONARY (mood/force on a clause), not binary relations (relationships-seed documents this) — they enter as MOOD markers when built, never as edge Types
- **G1.2** Their glyphs resolve from `CV_ICONS` (the symbol single-source); an operator with no icon
  **throws** (no inline SVG fallback). ◐ UNVERIFIED — operators carry text symbols (=, ≠) not CV_ICONS glyph refs; verify or wire
- **G1.3** `≠`/`not` is usable as negation by the read-out (G4.4). ☑ (verify_g2_4 22/22)

## G2 — New facets in CV_MEANING  (engine; no FORM face)
- **G2.1** ring and symbol carry colour/motion **independently**; `describe` reflects ring-state on the
  *reference* and symbol-state on the *thing* (e.g. "the selected colour set" vs the thing unchanged). ◐ (glyphic-type parts exist w/ independent colour slots; the describe() ring-vs-thing reflection UNVERIFIED)
- **G2.2** an edge's **line colour** is a field (red=blocked, green=approved, gold=active) and combines
  with line-style in the relation read-out. ☑ (field + render both live — verify_g2, slice 80)
- **G2.3** **size** reads as comparison: two nodes of different size in a relation → "more than"; absolute
  large size → emphasis. ☑ (verify_g2 35/35 — size meaning-typed + read)
- **G2.4** **conditional** structure reads "if … then …" (via `CV_COND`); **negation** (`≠`) inserts
  "not/never". ☑ (verify_g2_4)
- **G2.5** every new facet value LOUD-FAILS on an unknown value (a present-but-unknown value throws). ☑ (proven across every harness)

## G3 — Glyphgraph data model + type graph + conformance  (engine; no FORM face)
- **G3.1** `CVGraph` carries, per node, a full glyphic-spec + optional `address` + x/y; per edge, a
  relation-type id + line facets + label — and existing `DiagramSolver` consumers still work unchanged
  (preserve: hub/network/pipeline/timeline/quadrant/tree/stack all still render). ◐ (glyphgraph in the union + edge facets declared [W0]; the node **`address`** field is NOT yet carried — the G6 seam)
- **G3.2** `relationship` Types are seeded (filling `kind.graph`'s `accepts:['relationship']`); each has
  source/target sockets with `accepts` node-classes. `CV_REGISTRY.query({family:'relationship'})` returns them. ☑ (relationships-seed.js — live-reconciled union; verify_g3 25/25)
- **G3.3** `validateGlyphgraph(graph)` checks every edge's source/target against the relation-type's sockets
  via `CV_REGISTRY.accepts` + edge `conditions` via `CV_COND`; a well-formed graph passes, an ill-formed one
  **throws** with the specific violation (the grammar rejecting ungrammatical input). ☑ (glyphgraph.js; collect-then-throw)
- **G3.4** no second edge registry / no second meaning store created — verified by grep (relationship Types
  live in the registry; meaning in CV_MEANING; geometry in CV_SHAPES). ◐ — held at seed-time, then VIOLATED 2026-07-03 by a `verbs` table added into cv-edges.js (inert, uncoupled) → disposition in AMENDMENT A2

## G4 — Transglyphing: readGraph (graph → sentence)  (engine; no FORM face) — THE PROOF
- **G4.1** a **single node** transglyphs to its **referent** (a noun phrase, e.g. "this colour set"), NOT a
  full sentence and NOT a facet recitation. ☑ (verify_readgraph — the referent voice)
- **G4.2** a **relation** (2 nodes + edge) transglyphs to a real sentence whose mood follows the line
  (solid="is", dashed="could") and whose verb follows the relation-type; it passes the octagon oracle. ☑ mechanism (wording = standing live-tune)
- **G4.3** a **branching graph** transglyphs with **coordination** ("A and B") and **subordination**
  ("…, which …"); a real multi-clause paragraph from one graph. ☑
- **G4.4** **embedding** (an edge whose object is a sub-graph) reads as a complement/relative clause;
  **negation** reads ("…was never sent"); **conditionals** read ("if…then…"). ☑ (verify_g2_4; lone-conditional front-hoist)
- **G4.5** `readGraph(graph, {target:'english'})` runs on a REAL graph end-to-end (single node → referent;
  relation/branch/chain → real sentences). ☑ DONE (mechanism). The WORDING is **seeded starter data, tuned
  LIVE through the system** — NOT a mid-build gate (Tim, 2026-06-30: "build it all the right way and it's all
  easily tuned through the system, including by the AI; far easier to tune live, generating in front of me,
  than to pause and hand-craft now"). So: seed sensible readings, keep building; tuning is a continuous/late
  LIVE activity via the authoring surface + live generation, not an approval checkpoint.
- **G4.6** every read-out path loud-fails on an unknown facet/value/relation (no silent default). ☑

## G5 — Render: the glyphgraph as a laid-out visual  (FUNCTION **and** FORM)
- **G5.1** glyphgraph render
  - FUNCTION — a `glyphgraph` layout case positions nodes (authored x/y + a layered/radial fallback) and
    `DiagramSolver` renders each node as a **full glyphic** (CV_GLYPHIC.render), with edges carrying their
    meaning **VISUALLY** — line-style (mood), colour (state), direction, the relation's glyph. The graph MUST
    READ WITHOUT TEXT LABELS — there is NO reliance on edge labels (Tim, 2026-06-30: "otherwise it's not the
    language"). Verified by sight on a real graph. ☑ (slice 80; chrome-verified)
  - **G5.1b** edge labels are **OPTIONAL, off by default** — a reveal on **select / hover / highlight** (or a
    dedicated mode), never drawn by default and never required for legibility. ☑ (title = 2-node readGraph clause; labels-mode chip = the MEANING)
  - FORM — design-system tokens only (no hardcoded hex/px); glyphs render correct at node size; edges read
    by their visual facets, no overlaps; reads as a **navigable graph, not a text-wall**; responsive. Design-critic pass. ◐ (FORM taste flags OPEN from slice 80: mixed routing · curved-edge arrowhead angle)
- **G5.2** line colour + the new line-types (right-angled / curved / free) render via `edgeSVG`
  - FUNCTION — each line-type + colour renders distinctly on a real edge. ☑ (positioned edgeSVG + routing facet)
  - FORM — token-pure, visually coherent with the mark system. ◐ (taste flags above)
- **G5.3** the page `system/language.html` shows a real laid-out glyphgraph WITH its transglyphed paragraph
  beneath, generated live
  - FUNCTION — sentence is computed from the rendered graph (not hardcoded); changing a facet changes it. ☑ (language.html live)
  - FORM — design rubric across the page; the graph is the focal navigable surface. ◐ (page exists; full FORM pass w/ Tim pending)

## G6 — Convergence: glyphgraph over real addresses  (engine; no FORM face) — after G4 rings true
- **G6.1** a glyphgraph node's `address` resolves via `resolve_address` to a real Company thing; the node
  renders + transglyphs from the resolved content (not a hand-typed label). ☐
- **G6.2** glyphgraph edges reuse `relation_types/` (a `glyphgraph_edges/` vocabulary only if a needed edge
  kind isn't a corpus relation); no duplicate edge mechanism. ☐
- **G6.3** (later) a `glyphgraph://<frame>/<id>` scheme resolves via a new `resolve_address` branch. ☐ (deferred)

## G7 — Product Face (standing, every surface from G5 on)
- **G7.1** every Glyphic surface (the page, the render, any future canvas) passes the **design rubric**
  under a design-critic: tokens/components not bespoke · no overlaps · responsive at stated widths ·
  consistent scale/type/spacing · navigable-not-text · empty/loading/error states. ☐
- **G7.2** sync: the engine pieces (cv-meaning, cv-glyphics, cv-edges, cv-shapes, the new relationships-seed,
  the DiagramSolver changes) are merged to the canonical DNA Studio (DesignSync, diff-first), so all
  perspectives co-building Glyphic stay in sync. ☑ (standing; DesignSync live)

## G8b — DATA-BOUND glyphics: the live status/communication layer (Tim, 2026-06-30)
**Mandate:** a glyphic's facets can be BOUND to live data (not only literal), so the language can *speak the
current truth about real things* — the system describing an actual project (e.g. a property sale) to Tim,
always current. Two modes: **unbound** (compose meaning freely) AND **bound** (a live window onto a data thing).
- **G8b.1** a facet value can be a BINDING = a reference into the data (an address / Supabase row+field, via the
  one resolver) + a MAPPING (data-value → facet-value, e.g. status:sold→colour green). ☑ (verify_g8b 32/32)
- **G8b.2** a bound glyphic RESOLVES LIVE — when the data changes, the glyphic's facets (and its read-out)
  change automatically; no redraw/rewrite. ☑ (resolveBindings is PURE — re-resolve = liveness)
- **G8b.3** generalises the EXISTING encoding grammar (CV_MEANING.encodings: data-field → visual channel with
  value→appearance maps) — same mechanism, any field → any facet → any glyphic. Do NOT build a parallel binder. ☑ (a binding IS an encoding set; ONE resolveSet)
- **G8b.4** a project = a glyphgraph of bound glyphics; transglyph → a spoken status update resolved from live
  data ("the Smith offer on 12 Oak St is accepted, finance pending"). ☐  (Assumes the Supabase/data backend.)

## G8 — Self-describing & dual-surface (everything built carries its context)  (Tim, 2026-06-30)
**Mandate:** *"if it's all in the system — the howtos, the page systems, the AI registries, the dual
surfaces — everything you build has its context attached, so everything is automatically modifiable,
explained, everything through the system."* So nothing is built mute: each Glyphic thing is registered
WITH its context.
- **G8.1** every Glyphic thing (the language registry, each facet/operator/relation family, the glyphgraph
  type, the authoring API) has a **howto/guide** attached (the dual AI+human narrative face) — discoverable
  through the system, not just in a code comment. ☐
- **G8.2** every Glyphic surface + key concept has a **page** (page-face) bound to its address, so it can be
  opened and read in context. ☐
- **G8.3** the authoring + read-out are registered in the **AI registry (`CV_AI`)** as capabilities, so the
  integrated AI can read the language in-context AND configure it — the same `CV_MEANING.author` (G0.4),
  exposed as an AI capability + a user panel (the DUAL surface). ◐ (AI face ☑ ai-glyphic-language.js; the USER PANEL ☐)
- **G8.4** "context attached" verified by use: from a Glyphic thing you can reach its howto, its page, and
  its authoring affordance through the system (not by reading source). ☐
- **NOTE (standing rule):** wide research/exploration precedes every build step; anything unfinished/related
  found in the system is ADDED to scope here (under-preparation costs more than it saves). Log additions in SYNTHESIS.

## In scope, sequenced last by dependency (NOT deferred — Tim: "there is no 'later', it's all part of now")
These are part of the COMPLETE thing, not optional extras; they're built last only because they depend on the
rest, and must be built whole (not half-started):
- **G9 · the reverse — `parse(text → glyphgraph)`** ☑ STARTER (verify_g9 9/9 — deterministic inversion of
  the forward grammar reading the same single sources at parse time; authored words parse for free; honest
  STARTER GAPS throw naming themselves: subordination · conditionals · embedded negation → those are the
  remaining G9 work; the writer's role-based extract pipeline is the richer sibling, not a replacement).
- **G10 · multi-target transglyphing** ☑ (verify_g10 30/30 — READGRAPH_TARGETS realiser registry; english
  byte-stable; triples structural [English cannot leak]; a `code` target = registered-when-built).
- **G11 · layout** ◐ BROKEN → REDO AS RELATIVE (Amendment A3). History: force-directed was REJECTED by
  measurement; STABLE-SLOT shipped verified 21/21 (x-axis, append-scope, honest boundaries, a LEFT-VS-CENTRED
  taste call flagged for Tim and never surfaced); then OVERWRITTEN 2026-07-03 by an absolute global freeze
  (fixed pixel pitches, frozen rows, ring retired, brick-wrap) that broke the harness (19/21) and violated
  the relative laws. The redo is specified in A3.
"Complete" = every group G0–G11 demonstrably true. Nothing here is dropped; it's the tail of the same build.


---

## AMENDMENTS (Tim, 2026-07-03 — these are CRITERIA, reconciled after the drift correction)

### A1 · The referent words are PROFILE DATA (a G0 completion — the engine violates its own G0.1)
`REFERENT_KIND` (octagon→'gateway', hex→'system', …), `REFERENT_OP` (triangle/diamond phrases) and the
DETERMINER ladder are module-private consts in cv-meaning.js (663-665, 1058-1063) — fixed literals the
author API cannot reach. ☐ Move them into the profile as FIELD DATA on form/fill/outline (the shape the
line fields' `phrase` already uses); `referent()` and `parse()` read them from the active profile (parse
already builds every OTHER inverse vocabulary live). DONE when: `author.setField('form','octagon', …,
{kindWord:'…'})` changes the read-out AND the parse, live, no code edit. **Nothing has one fixed meaning
— a fixed interpretation anywhere the author API can't reach is a violation** (Tim).

### A2 · THE EDGE LAW: valid typed edges are DIRECTIONAL VERBS with an EQUAL AND OPPOSITE (Tim)
The Company's relation_types records already carry `{directed, inverse}` — the law encoded. ☐ Relationship
Types gain `directed` + `inverse` (declared inverses, composed at read, never stored twice — the grammar-
level satisfaction). ☐ Every seeded edge kind is re-expressed as a directional verb-pair or re-dispositioned
(Tim-visible): 'face' (the page-face relation — has-face ↔ face-of?), 'documents' (June-flagged invented),
'higher-order', 'navigates', and the operators. "Is the face of" as a SENTENCE belongs to the read-out, not
to the type id. ☐ The 2026-07-03 `verbs` table in cv-edges.js (transport/gather/descend/orbit — inert,
uncoupled, a G3.4 violation) is DISPOSITIONED: verbs that survive enter as meaning FIELDS + relationship
Types with inverses through the author/registration doors; the table is removed. ☐ cv-edges' soft default
(absent kind → 'face') becomes loud. G6.2 (reuse relation_types/) is the convergence face of this law.

### A3 · PLACEMENT IS RELATIVE — total redo (Tim: "you applied an absolute rule to a relative system")
☐ Position = a RELATIVE address (span/angle within the parent frame), re-resolved on change — never fixed
pixel constants, never a global freeze, never f(live count). ☐ A change re-resolves INSIDE its boundary and
holds OUTSIDE it (every boundary is the root of its own cascade): a new sibling re-partitions its parent's
span — siblings inside shift proportionally (bounded by the change budget, angled, animated); nothing
outside the boundary moves. ☐ The SAME laws govern every relational mutation: addition, removal, an ORDER
change (before→after), retargeting, containment change. ☐ Major parts hold, locals adapt — "some things
must move; that's the point — it's generative." ☐ The 2026-07-03 absolute-freeze implementation
(DiagramSolver W2 edit + cv-address slotFor pixel projection) is redesigned to this; verify_g11 is
rewritten to assert THE LAWS (scoped movement + outside-boundary stillness), and the left-anchored vs
centred taste call FINALLY goes in front of Tim in the live render. Authored x/y (drag) stays the
per-node override.

### A4 · The 2026-07-03 drift reconciliation (undo/redo/generalise — each item dispositioned, none silent)
☐ The 12 minted 'language'-family symbols: single-sentence descriptions → MEANING FIELDS (feeling +
senses, combinatorial, authored via the API); the library caption demoted to depiction-for-search; glosses
stay. ☐ The ordinal axis: fixed stop-labels + fixed interpretation → ONE contextually-loaded meaning
(legitimate) resolved relative to the telling's extent; reconcile its token targets with the CORPUS-SAMPLED
ramp SYSTEM-GAPS already specifies (`#d6bf57→#c09d5d→#b98664` as a tokenised --ramp-*, distinct from the
flat accent) — the ramp intent pre-existed; point at ITS tokens when minted. ☐ cv-organisms.js /
cv-address.js / cv-arc.js (the ports): KEEP as machinery, re-verify their disposition as A3/the build
consumes them; the address algebra's span math serves A3 directly. ☐ assessment/SYNTHESIS.md's false
"not done" claims: corrected by this reconciliation (the verifier run is the truth; READING-LEDGER.md
holds the record).

### A5 · The read-out "gate" is CORRECTABILITY-BY-USE (standing, never a blocker)
G4.5 as written stands: wording = seeded starter data, tuned LIVE through the authoring surface while
generating in front of Tim. Never re-erect a wording checkpoint. The standing wording flags (slice 80's
sentence-coverage [since closed], the verb-ish mood-folding note in verify_readgraph, "This the AI"
determiner-vs-gloss collision) are LIVE-TUNE items, worked during use.
