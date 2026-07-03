# AREA — the generator surface (glyphgraph-generator.html), read in full

> Territory: `design/claude-ds/system/glyphgraph-generator.html` (692 lines, 52,937 bytes) —
> READ IN FULL (Observed, every line). Seam files also read in full or targeted where the
> generator's own comments pointed at specific lines: `core/DiagramSolver.jsx` glyphgraph case
> (lines 63-127, Observed full), `core/cv-address.js` (92 lines, Observed full), the R1/R2-era
> `ai-glyphic-language.js` (`glyphic.assist`, lines 85-155, Observed), `~/company/roles/glyph_*.py`
> (existence + line-counts, Observed). No code edited; no commits made.

---

## §A · Account of the page (sections, functions, seams)

The page is a **single IIFE** (line 169-690) that boots DiagramSolver via a runtime Babel
transform of the raw `.jsx` source (169-184 — fetches `core/DiagramSolver.jsx` as text, strips
`export`, `new Function` + `Babel.transform`; this is the SAME pattern every DS-consuming system
page uses, not a generator-local hack).

**State (201-208):** one `graph = {type:'glyphgraph', nodes:[], edges:[]}` + a `selection` Set
(ids). `window.CV_GLYPHGRAPH_SESSION` (206-208) is the shared substrate: `{graph, selection,
get selected(), subscribers}` — the exact vertical ROADMAP's "PHASE A · A6 Collaborative AI"
item names as what a future AI capability reads. `glyphic.assist` (ai-glyphic-language.js:99-104)
already reads it — **this seam is live, not aspirational.**

**Render/read cycle — `redraw()` (218-242):** the ONE function that: calls `place()` (retired
no-op, see §C), applies the ordinal field if on, renders `DiagramSolver` via React, computes the
sentence, validates the graph, repaints tray+meaning+session. Called after every mutation
(add/remove/move/edit/teach). This is the generator's spine — everything else exists to mutate
`graph` then call `redraw()`.

**Canvas interaction (244-301), all direct-manipulation, wired once (`canvasWired` guard, 271):**
- `dblclick` (273-274) → insert a node at the pointer's fractional position, auto-select it.
- `pointerdown` on a node (276-286) → select (+shift multi-select) then drag; writes `nd.x/nd.y`
  live during drag (284), commits + `redraw()` on pointerup (285).
- `pointerdown` on empty space (287-297) → rubber-band rectangle, adds every node whose fractional
  position falls inside to `selection`.
- `Delete`/`Backspace` (300) → removes the selected nodes + any edge touching them.
- Coordinate math (245-259): `VB=320, MARG=30, SPAN=VB-2*MARG` — **must match DiagramSolver's
  glyphgraph layout constants** (the comment at 245 says so explicitly; this is a duplicated-
  constant risk, see §B). `xyToFrac(n)` (252-256) reads `n.x/n.y` (authored) else `n._pos`
  (solver-computed, written back by DiagramSolver — see §E) else center-fallback `{.5,.5}`.

**Tray + Meaning panel (303-388):** `paintTray()` renders each node as a real `GL.render()`
glyphic (not a placeholder box). `paintMeaning()` (317-371) is the **primary editing surface**:
single-select shows the node's `M.referent()` (the noun-phrase voice, not a facet dump — matches
GUIDE.md's "single glyph = noun phrase" law), its relations (each rendered via
`M.field('edge',kind).feeling`, i.e. it reads the verb from the SAME meaning field the language
engine reads, no local vocabulary), a state-swatch (`M.valuesFor('color')`), and a
`<details class="refine">` — explicitly SECONDARY per the page's own subtitle ("Form-level
refinement is secondary") — form/symbol/fill pickers. Multi-select (320-331) shows a group-state
setter + group-delete. This is the "meaning-first, form-second" flow the ROADMAP's DONE list
credits as built.

**Meaning-resolution + the Company pipeline (390-524, "A4"/"A5" comment blocks):**
- `detectBridge()` (398-407) probes `/api/corpus-query` same-origin; sets `bridgeLive`, flips the
  text-role binding to `'company'` via `AI.setRoleProvider` if reachable. **No fallback silently
  degrades meaning** — off-bridge, `resolveMeaning()` throws explicitly (409).
- `fireRole()` (420-425) → `AI.resolveProvider('company').runRole(role, utterance, extra)` →
  `POST /run_role` (traced into `app/services/company.js:95-99`, Observed).
- `resolveWord()` (435-448): known gloss/id first (free) → embedding top-k over `glyph_meaning`
  space → **the `glyph_compose` judge role** (never trust rank-1 — "the thin-margin law", 427-429)
  → auto-teaches via `glyphic.author-gloss` on a confident verdict, else returns `{ask: hits}`.
- `resolvePhrase()` (451-462): known edge vocabulary (`M.valuesFor('edge')`) first, else embedding
  search restricted to `glyph://field/edge/*` addresses, score-gated (>0.3).
- `composeViaCompany()` (466-489): the real NL→graph pipeline — **`glyph_extract` role** on the
  whole utterance → `resolveWord` per node → `resolvePhrase` per relation → one graph. Settles one
  unknown word at a time (475, "teach → re-write").
- `showSuggestions()` (493-524): the human-in-the-loop teach strip — symbol hits are click-to-teach
  (persists gloss, re-writes), field hits shown as "composition-level, not a noun" (513-515,
  correctly distinguishing G1.1's illocutionary/field material from nouns), a "make an icon" escape
  hatch into the foundry.

**Write entrypoint (526-568):** `write(text)` branches on `bridgeLive`: company pipeline
(`composeViaCompany`) with a `writeStarter` fallback on failure (544, toasts the fallback — not
silent); off-bridge, straight to `writeStarter` which calls `M.parse(text)` — **the SAME reverse
parser G9 verifies (9/9)**, not a parallel parser (confirmed: `M.parse` is the only parse call in
the file).

**AI teach/icon (576-636):** `ai-teach` = a manual prompt-based gloss teach via
`glyphic.author-gloss`. `makeIcon()` (598-636) = the foundry flow: `glyph_symbol_candidates` role
→ 4 rendered candidates (each temporarily registered into `ICN.data` to prove it renders as a real
glyphic before commit, 615) → click to `glyphic.save` + optional `glyphic.author-gloss` → a
feedback loop that re-fires with an accumulated brief (629-635, "regenerate until it looks right",
matching Tim's quoted mandate in the comment at 596).

**Collaborative assist (639-656, 676-684):** `applyOps()` interprets 5 op types
(`set_state|add_edge|remove|add_node|narrate`) — **exactly the 5 the `glyphic.assist` capability
validates atomically** before returning (ai-glyphic-language.js:126-133, cross-checked, Observed
match). The instruction box (676-684) fires `AI.execute('glyphic.assist', {params:{instruction}})`
and applies the returned ops through the identical mutation paths the mouse uses — **"two hands,
one graph" is real, not aspirational**: `applyOps`'s `add_edge`/`remove`/`set_state` write directly
to `graph.nodes`/`graph.edges`, the same arrays canvas interaction and `paintMeaning` mutate.

**The ordinal field (657-674, "W2"):** a toggle that stamps `nd._field = CV_ORDINAL.tokenFor(i,n)`
(insertion order → a token name) for the solver to paint as a halo. Comment (658) flags this as
provisional: "Order = insertion order (the arc's beat-order arrives when arcs drive composition)."

---

## §B · UNIFICATION findings — parallel paths that should consume the engine, or duplicate it

1. **THE BIG ONE: DiagramSolver's glyphgraph placement does NOT use `cv-address.js`, despite
   `cv-address.js` existing specifically to serve it.** `core/cv-address.js` (Observed, full file)
   is headed "the glyphgraph placement law rides on this: a node's slot = its span in its frame,
   FROZEN at insertion (stable-slot)" (line 15-16) and exports `span/encode/decode/lca/lcaAll/
   zones/slotFor` — a complete, generic, DOM-free span algebra with exactly the FROZEN-slot
   semantics R3 needs (`slotFor(index, capacity)` at line 83-88 grows capacity by doubling,
   **never moves existing slots** — this is close to A3's letter already). But
   `DiagramSolver.jsx`'s glyphgraph case (lines 63-127, Observed full) **never calls
   `CV_ADDRESS.*` at all** — it hand-rolls an equivalent row/slot system with hardcoded pixel
   constants: `LAY_SIZE=58`, `LAY_PITCH=LAY_SIZE*1.55`, `LAY_MARGIN=44`, `LAY_ROW_PITCH=116`,
   `PER_LINE=3`, `SUB_PITCH=40` (lines 92-95, 117-118) — literal numbers, not derived from
   `CV_ADDRESS.span`. This is the file the READING-LEDGER's own comment (line 74) already flags:
   "the address IS the CV_ADDRESS shape... the pixel mapping is this bounded viewbox's projection
   of it" — but that's aspirational prose in a comment; the code beneath it does not do that. It's
   a **second placement mechanism sitting right beside the one built to replace it.** R3 is not
   "build the relative address system" — the address ALGEBRA already exists (ported 2026-07-03 per
   cv-address.js's own header) and is UNCONSUMED. R3 is "wire DiagramSolver's glyphgraph case onto
   it and delete the hand-rolled row/slot/brick-wrap math."
2. **A duplicated geometric constant across two files.** The generator's own canvas math (line 245)
   declares `VB=320, MARG=30, SPAN=VB-2*MARG` with the comment "must match DiagramSolver's
   glyphgraph layout" — but DiagramSolver's actual viewbox constant is `VB` from its own module
   scope (not grep-visible in the 63-127 slice; the generator's copy is a **literal duplicate
   Tim's own law would flag**: "if you catch yourself copy-pasting a value... stop" (claude-ds
   CLAUDE.md §0)). A3's redo is the natural place to collapse this: if position becomes a
   `CV_ADDRESS`-resolved relative span, the generator's `xyToFrac`/`fracToXY`/`ggBox` conversions
   should resolve through the SAME function DiagramSolver uses to turn a span into a pixel rect,
   not maintain an independent copy of the viewbox math.
3. **No second meaning/parse engine.** Verified negative finding: every read-out call in the
   generator goes through `M.readGraph`/`M.referent`/`M.field`/`M.parse` — no inline vocabulary,
   no local word lists (the `[['file','file'],['folder','project']...]` block at 187 is glosses fed
   THROUGH `M.author.setGloss`, i.e. authoring into the one profile, not a parallel dictionary).
   This confirms G0.3 (one mechanism) holds on this surface specifically, which the plan files
   asserted but (per ADVISOR-AUDIT §6) had not been verified by reading this file until now.
4. **The AI pipeline (`composeViaCompany`/`resolveWord`/`applyOps`) is fully wired against roles
   that DO exist** — `~/company/roles/glyph_extract.py` (48 lines), `glyph_compose.py` (34),
   `glyph_assist.py` (51), `glyph_symbol_candidates.py` (46) all exist (Observed, non-stub line
   counts). This corrects an assumption I initially formed from the ROADMAP's "A5 · Extract/
   compose roles... the real NL→graph" being listed as still-open PHASE A work: **the client-side
   half is fully built and the server-side roles exist**; what's actually unverified is the
   live end-to-end fire (no chrome/browser pass of this page is recorded anywhere in READING-LEDGER
   or the ADVISOR-AUDIT, which flags exactly this gap at §6 item 4 — "the generator... before R3").
   This is a verification gap, not a build gap.
5. **Field-toggle's ordinal placement is independent of node placement**, which is correct
   separation (§A) but means R3 must also decide whether `_field`'s "insertion order" ramp should
   become an address-relative reading (e.g. position-in-parent-span) once position IS the address —
   currently they're two independent order concepts (`_slot`'s insertion-at-layout-time vs
   `_field`'s raw array-index) that happen to correlate today and would silently diverge under any
   reordering operation once R3 makes reordering a real, re-resolving operation (Criterion A3: "the
   SAME laws govern... an ORDER change"). Flagging for R3 design, not claiming a bug.

---

## §C · Disconnected / unused code

1. **`place()` is a clean, intentional no-op** (line 215: `function place(){}`), called once per
   `redraw()` (219) for no effect. The comment above it (210-214) documents exactly why: the W2
   retirement replaced ring-angle-by-live-count placement with DiagramSolver's frozen-address
   layout, and `place()` was left as a call-site stub rather than removed, presumably to avoid
   touching the `redraw()` call chain. **Verdict: clean retirement, not half-done** — it does
   nothing, calls nothing, and its own comment accurately describes its retirement. It IS dead
   code in the literal sense (a function that does nothing) but it is not a bug or drift; R3's
   redo should either delete the call entirely or repurpose the same call-site as the new
   "resolve this node's address" hook (the natural seam for R3 to land in, since it's already
   invoked at the top of every redraw).
2. No other unused functions found — every function defined in the file (list extracted via grep,
   28 top-level closures) has at least one call site traced. No orphaned event listeners, no
   commented-out code blocks, no leftover `console.log` debugging.
3. **Not disconnected, but worth flagging as a taste/consistency gap**: `ai-icon` button (637) and
   `makeIcon(null,null,null)` — the generic "make an icon" entrypoint with no word/context — versus
   the word-scoped `makeIcon(word, originalText)` called from `showSuggestions`. Both paths are
   live and reachable; not dead, just two entry shapes into one function (fine — this is the
   documented "generate-on-miss + manual" duality, not drift).

---

## §D · Corrections to plan/ledger/audit claims

1. **ADVISOR-AUDIT §6 ranked this file HIGH-risk-unread "before R3... the placement system's
   biggest consumer."** Confirmed accurate in one direction, overstated in another: it IS the
   biggest INTERACTIVE consumer (drag/pin/insert all write `nd.x/nd.y`), but DiagramSolver.jsx is
   the actual placement IMPLEMENTATION and cv-address.js is the unconsumed MECHANISM — the
   generator itself contains no placement math beyond the coordinate-frame conversions in §B
   finding 2. R3's real work is bounded to DiagramSolver.jsx + cv-address.js; the generator's
   obligation is narrower than "rewrite placement" — it is "keep every one of the 5 interaction
   affordances working against whatever DiagramSolver exposes as the position/override contract"
   (spelled out in §E below).
2. **ROADMAP's PHASE A "A5 · Extract/compose roles... the real NL→graph"** reads as an open item,
   but the generator-side consumer code for A5 is fully built (composeViaCompany, resolveWord,
   resolvePhrase, showSuggestions) AND the roles exist server-side. What's open is END-TO-END
   VERIFICATION (a live chrome pass with the bridge actually running), not implementation. Suggest
   ROADMAP's A5 line be split: "roles + consumer: BUILT (generator + roles/*.py exist) — VERIFY by
   use (chrome + live bridge)" vs treating it as unbuilt.
3. **READING-LEDGER's queue** (STILL TO READ, item 7) lists "system pages (glyphic-system,
   language, system-map+build-system-map)" but does not separately queue
   `glyphgraph-generator.html` — it's implicitly covered by "system pages" but given ADVISOR-AUDIT's
   explicit flag, it deserved its own line. Now closed by this census.
4. **No evidence found that the generator or its seams violate G3.4 (no second edge registry)** —
   `resolvePhrase` reads `M.valuesFor('edge')` (the one home), never a local edge-kind list.
5. **CRITERIA G5.1's "graph MUST READ WITHOUT TEXT LABELS"** — confirmed true on this surface: the
   generator never renders an edge label itself; the sentence comes from `M.readGraph`, and edge
   read-out inside `paintMeaning`'s relation list uses `M.field('edge',kind).feeling`, i.e. the
   MEANING word, never the raw kind id — consistent with G5.1b's "labels-mode chip = the relation's
   MEANING never the raw id" as verified elsewhere (READING-LEDGER Slice 80).

---

## §E · THE R3 CONSUMER CONTRACT — what the generator needs from placement

This is the deliverable the lead asked for: precisely what R3 (placement redo, CRITERIA Amendment
A3) must preserve so the generator's interaction model keeps working.

**The five affordances that touch position, and their exact current mechanism:**

1. **Authored override (drag, dblclick-insert)** — writes `nd.x` / `nd.y` directly, values in
   `[0,1]`, fractional coordinates within the frame (`DiagramSolver.jsx:108-109`:
   `pos[id] = {x: 30 + nd.x*(VB-60), y: 30 + nd.y*(VB-60)}`). **Contract**: R3 MUST keep `nd.x/nd.y`
   as the highest-priority, per-node override — CRITERIA A3 says this explicitly ("Authored x/y
   (drag) stays the per-node override"), and the generator's drag handler (`pointermove`, line
   283-284) writes these fields directly and expects DiagramSolver to honor them without
   recomputing anything else. **If R3 changes the override field's name or coordinate space
   (e.g. to a span/angle pair instead of a 0-1 fraction), the generator's drag math (`fracToXY`,
   `xyToFrac`, `authorFracOf`, lines 249-257) must be rewritten in lockstep** — these three
   functions are the ONLY place the generator converts between screen pixels and the graph's
   position representation. That's a narrow, well-isolated seam (13 lines total) — good news for
   R3's blast radius.
2. **Auto-placement for un-authored nodes** — currently `nd._slot = {row, slot}` (frozen at
   insertion, DiagramSolver.jsx:99-104), resolved to pixels each render via the row/brick-wrap math
   (107-123), then written back as `nd._pos` (124). **Contract**: the generator reads `nd._pos` as
   its fallback position source (`xyToFrac`, line 254: `if(n._pos) return {fx:n._pos.x/VB,
   fy:n._pos.y/VB}`) for hit-testing (`hitNode`) and selection-ring placement (`wireCanvas`,
   267). **`nd._pos` in absolute pixel units (0..VB) is the load-bearing field** — whatever R3
   does internally (relative span/angle addresses), it MUST continue to write a resolved
   `nd._pos:{x,y}` in the same pixel space DiagramSolver's viewbox uses, because the generator
   never resolves an address itself — it only ever reads the solver's already-resolved pixel
   output. This is actually a CLEAN seam for R3: the generator has NO knowledge of `_slot`'s
   internal shape (row/slot) at all — it only reads `_pos`. **R3 can change `_slot`'s shape freely
   (to a `CV_ADDRESS` path/span) as long as `_pos` keeps being written.**
3. **Node hit-testing during drag/click** (`hitNode`, line 258-259) uses a radius derived from
   `nodeSizePx()` (246: 44/50/58px by live count) compared against `xyToFrac` distances — this is
   independent of placement mechanism, no R3 impact.
4. **Selection-ring overlay** (`wireCanvas`, 264-270) re-derives each selected node's screen
   fraction via `xyToFrac` every render — same dependency as #2, no additional surface.
5. **Group/rubber-band selection** (287-297) reads `xyToFrac` for every node to test rectangle
   membership — same dependency, no additional surface.

**The animation seam Tim's law requires ("movement bounded, angled, animated" — CRITERIA A3):**
Currently there is NO animation on placement changes — `redraw()` does a synchronous React
re-render (221) with no transition; `DiagramSolver.jsx`'s own comment at line 377 says "with
frozen-address placement the diff is minimal by construction: only the changed node moves" but
this is a claim about which nodes move, not that movement animates. **If R3 adds bounded/angled/
animated re-resolution inside a boundary, that animation must live inside DiagramSolver's render
(CSS transition on the position style, or a requestAnimationFrame tween) — the generator's
`redraw()` is a blunt instrument (React re-render + `wireCanvas` re-wire) and has no tweening
capacity of its own.** This is new machinery R3 introduces, not something the generator currently
does and R3 must preserve.

**The invariant that most constrains R3's design:** the generator treats `nd._slot` as ** solver-
private** (never reads it) and `nd._pos`/`nd.x`/`nd.y` as the **public contract**. This is good
news: R3 can freely replace `_slot`'s content with a `CV_ADDRESS` path (`[[k,n],[k,n],...]`) or a
span object, entirely inside DiagramSolver.jsx, without touching a single line of the generator —
**as long as the two public fields (`nd._pos` for computed placement, `nd.x/nd.y` for the authored
override, both in the 0..VB / 0..1 conventions already established) keep their current shape and
priority order.** The order-change law (A3: "SAME laws for order-of-relation changes") has no
current generator analog to preserve — there is no reordering UI today — so R3 is free to design
that operation without a legacy contract to honor there.

**One open risk for R3 to resolve, not preserved by anything today:** the generator's own copy of
`VB=320, MARG=30` (line 245) will silently desync if R3 changes DiagramSolver's viewbox math
without updating this duplicate (§B finding 2). Recommend R3 either exposes DiagramSolver's
viewbox constants as a readable export (`window.__cvDiagramSolver.VIEWBOX` or similar) the
generator can read instead of hardcoding, or explicitly re-derives the generator's copy as part of
the R3 commit (falsify-first: verify drag/insert/hit-test still work post-R3, per the FUNCTION bar).

---

## §F · Proposed plan-file edits (tentative)

- **ROADMAP.md, R3 line**: append "(§E, census/AREA-generator-surface.md): the generator's
  position contract is narrow — `nd.x/nd.y` (authored override, priority) + `nd._pos` (solver-
  resolved fallback, both in pixel/fraction space matching DiagramSolver's viewbox) are the ONLY
  two fields the generator reads; `nd._slot`'s internal shape is solver-private and free to
  redesign onto CV_ADDRESS. Verify by use: drag, dblclick-insert, hit-test, rubber-band, and the
  selection-ring overlay all still work post-R3 (5 affordances, §E)."
- **ROADMAP.md, PHASE A / A5 line**: split into "consumer + roles: BUILT (generator's
  composeViaCompany/resolveWord/resolvePhrase + `~/company/roles/glyph_{extract,compose,assist,
  symbol_candidates}.py` all exist, non-stub)" vs "END-TO-END VERIFY: no recorded chrome pass of
  this page with a live bridge — closes ADVISOR-AUDIT §8 item 1's 'run one chrome pass over...
  the generator' directive."
- **ADVISOR-AUDIT §6 / READING-LEDGER**: mark `glyphgraph-generator.html` READ IN FULL (this
  census); the file is not a placement-math consumer beyond the 5-affordance contract in §E — the
  actual R3 blast radius is `DiagramSolver.jsx` (partial-read, per audit item 2, still needs full
  read) + `cv-address.js` (now read in full here, §B finding 1) + `verify_g11.js` (not read this
  pass — recommend the placement-lens reader or R3's own implementer read it next, since it is the
  test being rewritten, not a consumer).
- **New finding not yet in any plan file — recommend a line in ROADMAP's PHASE RECONCILE / R3**:
  "cv-address.js's `slotFor`/`span`/`lca` are UNCONSUMED by DiagramSolver today (§B finding 1) —
  R3 is a WIRING task (replace the hand-rolled row/slot/brick-wrap constants at
  DiagramSolver.jsx:92-123 with CV_ADDRESS calls) more than a from-scratch design task; the algebra
  Tim's laws require already exists and already has 13/13 passing coverage (verify_address.js,
  per READING-LEDGER) — it was ported in and never wired to its intended consumer."

---

**Evidence classification summary:** §A, §B(1-3,5), §C, §E are **Observed** (direct file reads,
line-cited). §B(4) corrected an **Inferred** assumption (from ROADMAP prose) against **Observed**
fact (the role files' existence and line counts) — flagged as a correction, not a new inference.
§D is comparative analysis against other agents' already-written documents (Observed quotes from
those files, compared to Observed code). No execution/browser verification was performed (out of
scope for a read-only census); §E explicitly notes the end-to-end chrome-pass gap rather than
claiming it closed.
