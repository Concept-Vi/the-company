# ConceptV — Design Language

This is the *how we design*, not just *what colours we use*. It captures the cross-cutting rules every screen obeys, independent of the visual DNA still being ingested. Tokens live in `styles.css` and its imports; this doc is the intent behind them.

---

## 1. Multi-surface native — always

Every design exists on **three canonical surfaces at once**, and is never considered "done" until it reads correctly on all of them:

| Surface | Frame | Token |
|---|---|---|
| Desktop | 1440 × 900 | `--frame-desktop-*` |
| Mobile · portrait | 390 × 844 | `--frame-mobile-p-*` |
| Mobile · landscape | 844 × 390 | `--frame-mobile-l-*` |
| (Tablet, optional) | 834 × 1112 | `--frame-tablet-*` |

**Method — author once, present many.** Build a single responsive source using fluid sizing + container queries. The *MultiSurface harness* (component, built once the language settles) frames that source at each viewport simultaneously, so portrait and landscape mobile are always in view next to desktop. Where a layout must genuinely differ — a side rail becoming a bottom tab bar — branch explicitly on `[data-surface]`, never on guesswork. Everything else should adapt without a branch.

Touch targets are never smaller than `--touch-min` (44px). Mobile respects safe-area insets via `.surface-shell`.

## 2. Responsive & computed — nothing is sized by its content alone

The recurring bugs (text spilling out, pills stretching a row) are banned by construction:

- **Type is fluid** — use `--fs-*` clamps, never fixed px for content text.
- **Every flex child that holds text gets `.min0`** so it can shrink; pair with `.truncate` or `.line-clamp`.
- **Pill/chip rows use `.pill-group`** — they wrap as a set; individual pills truncate their label past `--pill-max` rather than stretching.
- **Grids use `.auto-grid`** — columns fit to available width, no media queries.
- **Long copy gets a `.measure`** cap so line length stays readable.

If something *can* overflow, it has an explicit truncation or wrap strategy. No exceptions.

## 3. Motion — nothing teleports

State and page changes are **choreographed, not refreshed**. Elements move on and off; they never flash in or snap away.

- **Enter** from off-frame/collapsed, decelerating (`--ease-entrance`, `--dur-enter`).
- **Exit** toward off-frame, accelerating and a touch faster (`--ease-exit`, `--dur-exit`).
- **Move** between layouts via the View Transitions API (preferred) or a FLIP helper — persistent elements travel to their new position (`.moves`, `--ease-emphasized`).
- Lists/grids arrive as a **stagger** wave (`.stagger`, `--i`).
- All motion is gated behind `prefers-reduced-motion` — content still appears, it just stops travelling.

## 4. Visual-first — minimal text on screen

Prefer **diagrams, interactive visuals, and custom components** over stacked lists of text. A relationship is shown as a diagram (`tokens/diagram.css`), not a bulleted list. A status is a chip, not a sentence. Words earn their place; when a thing can be *shown*, show it.

The diagram vocabulary (nodes, connectors, arrowheads, edge kinds) is tokenised so every diagram looks like one hand drew it — and a generative diagram component will emit that same markup from a small `{nodes, edges}` spec.

## 5. Depth & texture — lightly stacked sheets

Surfaces read as layered translucent sheets, not heavy boxes: a warm-tinted elevation ramp (`--elev-0`…`--elev-5`), a subtle grain tooth (`.grain`), and hairline borders. The selected/active element — and only that one — earns a gold `--glow-active`.

## 6. Colour discipline (carried from the surface-zone system)

Near-white tinted surfaces separate functional zones; **gold is reserved for Vi, active decisions, selected states, key emphasis, and primary actions** — never a default background. Differences between zones are felt more than seen. See the *Surface-Zone Registry* card.

There are exactly **two saturated voices**, never more: **gold** (`--accent-gold` → `--vi-*`) = active / decision / attention, and **sage-green** (`--accent-communication` → `--comm-*`) = *communication / relationship / positive value-flow / sustainability* (corpus-proven: the capital-raise p5 legend literally labels it "Communication"). Green is sparse and semantic — never structural (that voice is **bronze**, `--accent-bronze`) and never a decision (that is gold). It is a *voice*, distinct from `--pig-success` which is a *state* (passed/ready). The ground itself has a **clean↔warm knob** (`data-ground="clean|warm"` — white `#FFFFFF` ⟷ ivory `#FCFAF2`); both are the same `light` theme, and every `--zone-*`/`--comm-*` role recomputes against whichever ground is set, so nothing is re-picked by hand.

---

### Build order for the overhaul
1. **Foundation tokens** *(this layer — done)*: surfaces, sizing, motion, depth, diagram vocabulary, **theme modes, density, layout primitives + layering, loading/interaction states, attention/focus, icons, data-viz, imagery, spatial canvas, provenance, export surfaces + lifecycle**.
2. **Surface system**: repaint colour/texture values with the incoming DNA on top of this structure.
3. **Components**: real `.d.ts` + `.jsx` pairs — including the MultiSurface harness and the diagram generator.
4. **Specimens, cards & templates**: the visible documentation + starting points.

---

## 7. Theme modes — one ground, four worlds
Every wash mixes toward `--zone-ground`, so a theme is just flipping that ground + the ink ramp: **light** (default), **dim** (soft warm dark), **dark** (full warm dark — never cold grey), **contrast** (high-contrast light). Set `data-theme` on any wrapper. Gold discipline is preserved in every mode.

## 8. Density — one knob, three comforts
`data-density="compact | comfortable | spacious"` scales breathing room via `--density`. New components reach for the density-aware `--d-*` spacing tokens so a single attribute re-tunes a whole layout (dense desktop data vs. roomy mobile).

## 9. Composition — primitives, not bespoke layout
Build from `.stack` / `.cluster` / `.sidebar` / `.switcher` / `.grid-fit` / `.cover` / `.reel` / `.center` — responsive by construction, no per-component media queries. Overlays obey the `--z-*` layering scale; never hand-pick a z-index.

**Layouts are content-as-data, never bespoke.** A slide/page archetype is a *pure function* `content → CVNode tree` (a fixed Section/Zone/Cluster subtree), rendered by the block solver and recomputed by the dials — `design = f(content, axisPosition)`. Reach for `Slide`/`Archetypes` (`core/Slide.jsx`) and the typed-container ladder before hand-laying-out a frame; a new atom is a registered renderer (`ContainmentTree.registerAtom`), not a one-off element. The same content at a different LOD/surface/density must recompute, not be re-authored.

## 10. Resolve, don't pop
Loading uses `.skeleton` placeholders that shimmer and then swap to real content with an `.enter-*` class — content *resolves*. Empty/error/first-run are designed `.state-block`s, not bare text. Interaction states (`.interactive`, gold focus-visible ring) are consistent everywhere.

## 11. Authorship is always legible
`data-author="human | vi | suggested"` (and the `.by-*` badges) mark who made a thing — a trust signal across an agentic workspace. Vi output awaiting review carries the `.vi-authored` wash.

## 12. Everything is a surface — including exports
Screens are mobile-native; deliverables are export-native. Compose against `.page` frames (A4 / Letter / 16×9 slide) with a real `@media print` path. Mark maturity with lifecycle tags (`.lc-experimental / -stable / -deprecated`) so experiments are visibly quarantined.

## 13. One home per concept — change once, propagate everywhere (the anti-drift law)
The system is **four single-source registries**, all the same shape: **tokens** (`styles.css` + `tokens/*.css`), **types** (`window.CV_REGISTRY` + `core/archetype-catalog.js`), **the engine** (`core/` solvers on `cv-nodes.d.ts`), and **AI** (`window.CV_AI`, `app/ai/*`). Every value, type, archetype, generative move, model provider, and the brand voice has **exactly one home**; everything else holds a reference, never a copy. Change the home → it propagates to every consumer. Adding something = registering it in the right home, never forking a parallel copy. (Full wiring: `analysis/INTEGRATION.md`; how-to: `CLAUDE.md`.)

## 14. AI is part of the system, not bolted on
Everything Vi can do is the registry `CV_AI`: **providers** (model endpoints — swap in one place, loud-fail if absent), **behaviours** (instruction fragments composed into prompts — the **voice** is `voice.conceptv`, sourced once, never inlined), **skills** (named intents — the transform menu is a *projection* of them), **capabilities** (generative moves — `id == move`, the catalogue IS the dispatch; 43 across 14 families), and **context** (surface-keyed resolvers — `execute()` resolves "what screen Vi is on" automatically). `ai = f(capability, context, params)`, the mirror of `design = f(content, axis)`. Call models only through `CV_AI.execute(id)` / `CV_AI.complete(prompt)` / `CV_AI.resolveProvider(id)` — never a raw endpoint. The registry inspector projects the whole catalogue, so the interface and the AI read one source.

## 15. The Bridge — Vi can reach the repository (`CV_HOST`)
The fifth registry, same shape, answers "what can Vi DO to the repo it runs in, and what's available HERE?" `capability-available = f(environment, runtime)`. **Runtimes** are pluggable and resolved by capability: `review` (the sandbox floor — no disk, stages every change as real source for review; always available), `fsapi` (browser File System Access — real read/write when the app runs top-level / exported), `native` (`window.CV_HOST_NATIVE` — a local shell or MCP host giving read/write/list/exec/tools, auto-detected on export). A **serializer** (one home per change kind) turns any registry mutation — a token, a `CV_AI` entry, a Type, a card — into the *exact source* of the one file it belongs in, so Vi authors real diffs, not vague suggestions. `repo.*` / `ds.propose` / `ds.apply` are `CV_AI` capabilities, so "touch the repo" routes through the same `execute()` path. Every commit is **staged for review first**; a connected writer (or opt-in auto-apply) writes to disk. The honest boundary is kept loud, never silent: in the sandbox there is no disk write — the mode is labelled "Sandbox review" and changes wait for the agent or a human to commit. Add a way to reach the world (a Tauri shell, an MCP file tool) = register a runtime, not edit every caller. The Bridge canvas + the `CV_HOST — the Bridge` card are projections of `CV_HOST.describe()`.

## 16. Narrative architecture — the sequence is part of the design (the title chain)
A multi-page artifact is not a bag of slides; **the order is a designed object**, and the deepest decks
make the argument legible from the **title rail alone**. The corpus-proven rule (capital-raise, 30pp):
**slide titles chain into one running sentence**, each beginning with a *leading connective* — `But` /
`To` / `With` / `That` / `Which` / `By` / `And` / `Because` — so each title is a clause continuing the
prior, and the body of each slide merely *proves* its clause. Read end-to-end the titles parse as a
single paragraph: problem → thesis → mechanism → proof → moat → ask. Consequences for the system:
- A deck Type carries a `titleChain` intent (the connectives + clause order), not just a list of titles;
  the narrative arc (`problem→thesis→mechanism→proof→ask→appendix`) is a **reorderable, LOD-pruned
  sequence** of archetypes — the same content at lower LOD drops support clauses but keeps the spine.
- **Section breaks** are full-bleed photographic dividers (one word); **cover & closing are the live
  product surface** (panotour chrome) with a frosted overlay panel — the brand frame *is* the product.
- This is a single home: the connective voice + clause-chaining belongs in `CV_AI` (a `deck.titlechain`
  capability composing the house `voice.conceptv`), never re-typed per deck. The composer projects it.

## 18. Everything is a universal component — slots, sockets, declarations
Every thing on an interface — a Glyphic, a Button, a Card, a panel, a graph, a slide — is a **universal
component**: a Type in `window.CV_REGISTRY` that **declares its parts, value-slots and sockets**.
- **value-slot** — a parameter that takes a *value* from an axis (`{axis, groups?|values?, default}`)
  or an enum; the vocabulary resolves from the axis/contract, never copied.
- **socket** — an attachment point that takes a *typed thing* (another component) or an *event*
  (`kind:'event'`, e.g. onClick→open at an `address`), gated by `accepts`/`forbid` + conditions.
- **part** — a named sub-component with its own slots/sockets (the Glyphic's ring + symbol).
- **condition** — any slot/socket/declaration can carry conditions, evaluated by the one shared
  evaluator `window.CV_COND` (`"texture requires fill != none"`), so the rule is identical in
  validation and in the editor.
Acceptance is **declarative**: `CV_REGISTRY.candidatesForSocket(socket)` returns what fits, so a panel
that declares a glyphic-accepting socket shows the glyphic library with **no bespoke code**. The
interface is a projection of these declarations (`system/type-system.html` lists all 94 Types live).
New thing on screen = register a Type, never hand-wire a screen. (Spec: `system/glyphic-system.html`
§05b–§05e.)

## 17. Axes — every visual dimension is a typed system; tokens are its value-units
Every primary dimension of the language is a **first-class Axis** in `window.CV_AXES` (the sixth
registry, same shape): **Colour · Space · Size · Motion · Texture · Depth · Fill · Form · Symbol**,
with **Meaning** the contextual/loadable layer *over* them (`CV_MEANING`). An axis is a hierarchy of
typed values; **tokens ARE those value-units** — the Colour axis *is* the colour tokens, the Size axis
*is* the `--size-*` tokens — so an axis adds type/grouping/meaning around the token graph, it never
replaces it. **Everything visual resolves its value of an axis from that axis** (`CV_AXES.css(axis,
value)`); nothing hardcodes a value table (motion is not "glyphic motion" — it is the Motion axis, and
a Glyphic *subscribes* to it). A component declares each part-slot as a **subscription**
`{ axis, groups?|values?, default }`; an editor/foundry shows exactly `CV_AXES.candidates(sub)`. New
visual dimension = register an axis, not a per-consumer constant. (Spec: `system/glyphic-system.html`
§08; plan: `analysis/AXIS-REFACTOR.md`.)
