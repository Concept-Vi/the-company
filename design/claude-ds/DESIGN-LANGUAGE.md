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

Touch targets are never smaller than `--touch-min` (44px). Mobile respects safe-area insets via `.surface-shell`. The mobile device chrome is a system component set in `tokens/device.css` — `.cv-device` (bezel) → `.cv-device__screen` (a flex column) holding `.cv-statusbar`, `.cv-appbar`, a `.cv-screen-scroll` body, and `.cv-tabbar`/`.cv-tab`, all sized from `--mobile-*`/`--safe-*`. Bars are flex-none siblings and the body scrolls *between* them, so a bar never floats over the frame or the content. Never hand-roll a phone frame, status bar, or tab bar — consume these.

## 2. Responsive & computed — nothing is sized by its content alone

The recurring bugs (text spilling out, pills stretching a row) are banned by construction:

- **Type is fluid** — use `--fs-*` clamps, never fixed px for content text.
- **Every flex child that holds text gets `.min0`** so it can shrink; pair with `.truncate` or `.line-clamp`.
- **Pill/chip rows use `.pill-group`** — they wrap as a set; individual pills truncate their label past `--pill-max` rather than stretching.
- **Grids use `.auto-grid`** — columns fit to available width, no media queries; set `--col-min` so cards never crush below a legible width instead of spilling their labels.
- **Groups of N siblings use the `.flow` axis** — declare the inputs (`--count`, `--item-min`, `--flow-gap` ← density) and the columns *compute*; declare overflow **intent** with `data-flow` (`wrap` rows · `reel` one sacred row with themed horizontal scroll · `fixed` for known-width surfaces only). Never hand-set a column count in fluid UI.
- **Long copy gets a `.measure`** cap so line length stays readable.
- **Depth is a coordinate, not a style** (`tokens/skins.css` §DEPTH LADDER): every material block carries
  `data-depth` — its level-axis rank from root (page 0 → region 1 → panel 2 → card 3 → well 4 → overlay 5),
  stamped by the block solver. Skins resolve the rank to physics: lift shadows scale with depth, a per-skin
  bevel models the slab edge, and `--skin-map-normal`/`--skin-map-roughness` resolve surface map addresses
  shared by CSS and the 3D well solver. Ghost/potential blocks are the OPPOSITE depth — carved into the
  surface (inset, no lift). A zone within a zone is a level; a level is depth; depth is physical.
- **Materials sample the world** (`tokens/material.css`): a skin's block texture is ONE image painted in
  world (viewport) coordinates — each block shows the patch under its own position, so no two blocks repeat,
  with zero per-instance configuration. The texture multiplies with the fill beneath it, so semantic colour
  tokens tint through the material. Textures tile at native resolution × `--world-zoom` (the camera dial) —
  never stretched, never `cover` for a tile. Inset zones may declare their own material via
  `--skin-mat-texture-inset`.
- **A glyphic node is not a container**: its diameter comes from the control rung (`--glyph-d`), it takes no
  keyline, and its symbol centers on the solver's anchor — the circle IS the glyph.
- **Text is typed with a length budget** (`tokens/text.css`): every label/title slot has a declared budget (`--len-micro/label/title/desc`), copy is *written to it* (the `copy.budgets` behaviour in the AI registry makes this a language rule), and layout reserves room for it. When a slot can legitimately be narrower than its budget, author a **designed short form** — `.alt-full`/`.alt-short` swapped by the nearest `.q` container — never clip. **Truncation is not design**: `.truncate`/`.line-clamp` are last resorts for uncontrolled user strings (filenames, pasted titles) only.
- **Surfaces contain and align by rule, not by coincidence** — a rounded surface holding flowing content gets `.contain` (clips to the radius, so no label crosses the border); sibling surfaces in a column get `.keyline` (the shared `--keyline` inset) so their content lines up on one vertical line by construction. These live in `tokens/layout.css` and compose with `.min0`/`.truncate` (which keep the *text* honest — `.contain`/`.keyline` keep the *surface* honest).
- **Containers are BLOCKS** (`analysis/BLOCKS.md`, `app/registry/block-type.js`): the container universal component — ground + material surface (**material axis**: glass · velum · parchment · stone · none, `tokens/material.css`; default **`skin`** = the active skin's surface) + a containment-depth coordinate (`page → region → panel → card → well`, which *derives* the depth-modifier) + ordered content sockets (order = reading order) + action sockets (verbs from CV_ACTIONS, filled by address). Pages are compositions of blocks; every surface resolves through `CV_BLOCK.chrome()` / the `block` solver in `CV_NODE` — never hand-assembled chrome. **Skins** (`tokens/skins.css` + the skin axis) re-bind the whole world — ground, surface, shadows, threads, state glow — so one spec resolves to the glass world or the stone (plaster + porcelain) world in full.

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
- **part** — a named sub-component with its own slots/sockets (the Glyphic's ring + **fill** + symbol).
  A facet that lives on a part (the glyphic's `fill`, on the `glyphic-fill` part-type) only reaches the
  projection if the parent **declares that part**: `flatValueSlots` walks `parts` and merges their slots, so
  `toInspector`/the AI tool-schema see one flat facet set. If a facet is missing from an editor, the cause
  is almost always a part the parent never declared — fix it by declaring the part, **never** by reading the
  axis directly in the consumer (that is a second home; the projection is the one source).
- **Per-part independence** — each part owns *every* axis (colour · texture · motion · …), cleanly separate,
  while the whole unit still scales/elevates/moves as one. The canonical glyphic form is a **part tree**
  (`CV_GLYPHIC.expandParts`): `whole` + `ring`/`fill`/`symbol`, each with its own values; the flat spec is
  the expand-time default (back-compat), `spec.parts.<part>.<axis>` overrides. The renderer is a **layered
  compositor** — `compose` stacks one `markSVG` layer per part, each with its own colour/texture/motion class
  (`markSVG` stays monolithic for other consumers; texture maps per medium — a *face* gets the pattern, a
  *line* gets a dash). The editor reads `toInspector().partGroups` (`CV_NODE.partSlots`, not collapsed) and
  shows a **section per part**; a per-part edit is `set-value({slot, value, part})` onto the same part tree
  the renderer reads, so edit and render can't drift. (Card: `system/glyphic-parts.html`.)
- **Forking & revert** — `update()`/`relate()` on a built-in **fork it into the user layer** (persisted), and
  `get()` returns the user override first. The only way back to canonical is **`CV_REGISTRY.revert(id)`**
  (= `remove()` of the user-owned layer); a pure built-in with no fork can't be removed. So a built-in
  customised or polluted at runtime is always recoverable — and tests must `revert` what they fork.
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

**An axis is self-describing and relational, not a flat list (Colour leads — `axes/color/color-axis.js`).**
Tokens are the *matter* (the literal, one home in the stylesheet); the axis is the *grammar* — it carries
what a token can't know about itself, in **two tiers** (a rule lives at the most general level it's true):
- **Families (groups) self-describe + relate**: `role` (what the family is for), `pairsOn` (the legible
  foreground family/value), `voice` (a saturated voice vs quiet structure), default `roles`. Families form a
  small relational graph, computed once, read everywhere.
- **Values override only when they differ**: `on` (this colour's legible ink), `roles`
  (`fill`/`line`/`text`), `themeInvariant` (holds across theme flips), `alias` (synonym of a canonical id).
- **One home for derived facts** via `CV_AXES`: `pairOn`/`pairCSS` (the single source for *"what ink sits on
  this colour"* — it dissolved the hardcoded `--on-gold`; the compositor's solid-fill ink reads it), `rolesOf`/
  `byRole`, `themeInvariant`, `canonical`/`isAlias`. A token home stays the single source of the *value*; the
  axis never copies a literal.
- **Same axis, different families per type** — a component declares which families its colour slot resolves
  (`groups:[…]`), the value-side twin of a socket's `accepts`: a glyphic *mark* subscribes to
  `brand·semantic·communication`; a *surface* subscribes to `zoning` (the tonal-zone washes, themselves axis
  values). The picker is just `candidates(slotRule)`. (Card: `system/colour-axis.html`.) **Audit note:** a
  role token must reference its primitive (`--fg-primary: var(--ink)`), never re-copy the hex — duplicate-hex
  clusters in `colors_and_type.css` are a reconciliation backlog, not the pattern.

## 19. The collapse — one node, and the @decorator vocabulary
The four registries stop *mirroring* each other and become **one substrate**. `window.CV_NODE`
(`core/cv-node.js`) is the weld (like `RenderType` welded type-system to engine): it references the
existing homes and copies nothing.
- **One unit** — `CV_NODE.lens(x)` projects a Type, an axis value (a token), or a glyphic spec into the
  *same* canonical node `{id,kind,layer,classification,axis,axisValue,valueSlots,sockets,parts,
  conditions,payload}`. A token is a leaf (`kind:'token'`); the rest interior. Unity is in the
  **mechanic, not in flattening type** — `kind` still carries the solver/behaviour, so a token and a
  deck are the same node but never interchangeable.
- **One relation** — a slot and a socket are one attachment point with `accepts`. `accepts` names an
  **axis** → a value-socket; a **classification** → a thing-socket. **`CV_REGISTRY.accepts` now handles
  both** (the fold), so there is one matcher.
- **One mechanic** — `CV_NODE.resolve(node, ctx)` fills sockets by **address** (by reference, never a
  copy), resolves parts, and **recurses, threading `ctx` downward** so a condition deep in the tree
  reads ancestor state (a ring's "texture requires fill != none" reads the glyphic's fill).
  `render(node)` dispatches to a **pluggable per-kind solver** (glyphic→`CV_GLYPHIC.compose`,
  token→axis `resolveCSS`, *→`__cvRenderType`); CV_NODE invents no renderer.

**Decorators** are the cross-cutting vocabulary (the **seventh registry**, `window.CV_DECORATORS`,
`app/registry/decorators.js`). Where `kind` is *what a thing IS*, a decorator is *what is ALSO true of
it, or what it can ALSO do*: `provenance · classification · tags · layer · axis · zero · token ·
optional · multiple · event · address · accepts · conditions · means · intrinsic · deprecated ·
experimental · generatable · editable`, plus the source `@dsCard` / `@template` annotations — **one
catalogue**. It is **retrospective**: each decorator's `derive(node)` *reads* the value from the node's
existing field, so the vocabulary lives here while the value stays in its single home (no second home).
Decorators **do things**: `find({decorator,value})` searches the whole system; a `condition` decorator
gates via `CV_COND`; a `generatable` decorator routes to a `CV_AI` capability; an `editable` decorator
names an inspector's fields; a socket may `requires`/`forbids` decorators and `CV_NODE.accepts` honours
it. New aspect = one entry — instantly searchable, and if it's a behaviour, instantly runnable. (Spec:
`system/glyphic-system.html` §09–§10; proof: `_qa/cv-node-test.html`, `_qa/decorators-test.html`.)

## 20. The Studio — one projection to UI and AI; one action layer
The system is editable both by **assembling** (click a library/inspector) and by **talking** (chat +
two-way voice) — and these are not two systems. The thesis: **`ui = project(node)` and
`tools = project(node)` are the same `project`.** A node declares itself (kind · value-slots · sockets ·
parts · decorators · conditions); **actions** declare what can be done to it; one projection emits both
the inspector you click and the function schema the AI calls.
- **`CV_VARS`** (`app/registry/vars.js`) — the ONE variable-resolution mechanism (`literal` ·
  `"{{ path }}"` · `{var,default}` · `{ref}` · `{op,args}`) resolved against a context. Used by actions'
  params, the shared context, projection, and conditions (`CV_COND` delegates its path-read here) — so a
  path means the same thing everywhere.
- **`CV_ACTIONS`** (`app/registry/actions.js`, the **eighth registry**) — every verb/tool/function: an
  `actionType`, variable-resolved `params`, a per-action **Skill** (its AI how/when), `targets`, a `run`.
  `applicable(node)` filters by classification; `invoke()` resolves args via `CV_VARS` then runs;
  generative verbs route to `CV_AI`.
- **`CV_PROJECT`** (`app/registry/project.js`) — `toInspector(node)` (UI) + `toToolSchema(node)` (AI
  function-calling) + `toContext(state)` (the shared context blob), all from one declaration.
  `coherent(node)` proves the UI action set === the AI tool set, so click and talk can't drift.
- **`CV_INSPECTOR`** (`app/registry/inspector.js`) — the ONE editing surface. `mount(el, {typeId?, node,
  audience?, captions?, onChange?, onAction?})` renders the WHOLE `CV_PROJECT.toInspector` output for ANY
  kind: value-slots, **sockets** (each with its live `CV_NODE.candidates`; event-sockets open an address),
  decorators, actions. The **preview rule is universal** — every slot option is previewed by rendering the
  node through `CV_NODE.render` with that one slot overridden (a recoloured glyph IS the colour preview),
  so there is no per-facet branching; size/motion read via the option's own axis, not a facet-name check.
  A `pick:{axis,current,base,onPick}` mode renders a single-axis value picker (the behaviours panel's
  "choose a target value"). Every edit goes through `CV_ACTIONS.invoke` (set-value/fill-socket/open) — the
  same verbs the AI calls. **Logic is unified here; the skin is the host's** (a consumer restyles the
  `.ci-*` classes / hides captions to match its look), so adopting it never loses a surface's look. Surfaces
  that still hand-roll an editor (the Studio's FACETS renderer, the behaviours panel) are consumers to
  migrate onto this — there must be no second home for "how to edit a node."
- **Providers, context, command** live in the existing `CV_AI` (`app/ai/ai-studio.js`): a **voice**
  provider and a **local-provider** pattern (bound via `CV_HOST` — `resolveProvider` already delegates
  unknown runtimes there, so you connect your own); a **studio context** resolver; and `studio.command`
  (instruction → one action call from the live tool schema). Voice is just a provider feeding the same
  loop.

**One action layer:** a dropdown change, an action button, a typed command, or a voice transcript all
become `CV_ACTIONS.invoke(action, args, ctx)`; the node mutates; the viewer re-projects. **Rule:** a
hardcode is a class to dissolve or a capability to build — applied this slice by dissolving the
`generatable` kind→capability map into a query over `CV_AI` (a capability declares `generates:[…]`).
(Concept + live proof: `system/glyphic-system.html` §11; working demo: `system/studio.html`; plan:
`analysis/STUDIO.md`; proof: `_qa/studio-test.html`.)

## 21. Root Unity — the self-building system; lookups are queries, not maps
The system is named **Root Unity** — **√(unit)**: every part is the same one unit, and the system is the
root from which each instance grows (mark: `assets/brand/root-unity-mark.js`). Two principles codified
this slice:
- **A lookup is a query over a single source, never a stored map.** `CV_QUERY` (`app/registry/query.js`)
  is the named pattern: `relations(node, {from, field})` computes a relationship by asking the registry
  that owns the fact. The `generatable` decorator was a `kind→capability` map; it is now
  `CV_QUERY.relation(node, {from:'ai', field:'generates'})` (the capability declares what it
  `generates`). **If you write `MAP[x]=y`, stop — find the registry that already knows y for x and query
  it.** Available as a `{query}` value-spec in `CV_VARS` too.
- **The system builds itself through its own verbs (meta-actions).** `CV_ACTIONS` carries the
  construction verbs — `define-kind · add-field · relate · define-rule · define-axis · define-decorator
  · define-trigger · define-action · define-macro` — each writing to the one home for what it defines.
  New layers, distinct parts, what-slots-into-what, and rules are all declared *through the interface*,
  not hand-coded.

**Events are rules, not intentional calls.** `CV_EVENTS` (`app/registry/events.js`, the **ninth
registry**) binds an event to an action: `{ on, when?, do, args }`. A process emits where it is
(`emit('ai.focus', {target})`) and a declared trigger reacts (`ai.focus → highlight`) — so what the AI
is attending to highlights automatically. Events compose actions + conditions + variables; no new
mechanism. Two more substrate ideas landed: **undo-as-inverse** (each mutating verb declares
`invert`; `CV_ACTIONS.inverse()` returns the opposite invocation — history for free) and
**macros-as-actions** (a recorded chain is itself a registered `actionType:'macro'` — a Skill that is
steps, not a prompt). (Spec: `system/glyphic-system.html` §12; demo: `system/studio.html`; proof:
`_qa/meta-test.html`.)

## 22. Generation from data — every collection-UI is a view (query + projector)
The derive-by-query principle (§21) generalises from *lookups* to *whole interfaces*. A **view** is a node
(`kind:'view'`) whose `spec` is a **query + a projector**; `CV_PROJECT.toCollection(view, ctx)` turns it
into a live list of rows. So a library, a palette, a menu, a gallery are **generated from the registries,
dynamically, with no per-surface code** — "the interface is a projection of the registries" made literal
and reactive. Register a Type / axis value / action / decorator and it appears in the relevant view
automatically (verified: defining a kind grows `view.library` with zero UI code). Seed views:
`view.palette-form|symbol|colour`, `view.library`, `view.actions`, `view.decorators`, and `view.views`
(a **view of views** — a view is itself a node, so generation-from-data goes all the way down). A view's
`onPick` wires each row back to an **action**, so a palette is *assemble-from-library*: click a row →
`CV_ACTIONS.invoke`, the same action layer as the inspector and the AI. Data flows in (registry → query →
rows), intent flows out (row → action → mutation → re-projection). Also this slice: **selection-as-node**
(a selection is a `kind:'selection'` node so actions apply to it uniformly), and another hardcode
dissolved — the Studio's chat interpreter now derives its vocabularies from the axes
(`CV_AXES.resolve(axis).ids()`) instead of mirroring them in lists. (Spec:
`system/glyphic-system.html` §13; demo: the Studio Library panel; proof: `_qa/views-test.html`.)

## 23. Interface craft — the Studio must use the system on itself (a living projection)
The Studio is **for a regular person**, not a developer, and it is a **perpetual work-in-progress
projection** — it will keep being upgraded as more of Root Unity becomes functional. Two standing rules:
- **The interface uses the system's own mechanics on itself.** Don't dump raw technical strings in a
  patchwork of paper cards. Use: **glyphics as the visual currency** (library items, thumbnails, status
  marks — render real glyphics via `CV_NODE.render`, not text pills); **tonal zoning** for surface
  hierarchy (rail/canvas/inspector at different zone depths, not all flat paper); **proportional panels**
  and an **8px rhythm** with even alignment; **iconography** (CV_ICONS) on actions/sections/tabs; **colour
  + subtlety** (gold reserved for the live/primary, gentle motion, hover states); and **human text, not
  machine text** — the canvas reads "an octagon holding a house, soft gold wash, still", with the raw
  spec/JSON kept to the technical panes.

### 23a. The audience axis — one projection, two surfaces (maker vs author)
The reason an interface dumps everything is it has no notion of *who a thing is for*. So **`audience`** is
now a first-class field across the registries (`CV_REGISTRY` / `CV_ACTIONS` / `CV_DECORATORS` normalize:
`audience: [...] | null`), and **`CV_PROJECT` filters by the active audience**. Values: **`maker`** (a
regular person), **`author`** (system-builder), **`dev`** (debug). `null` = everyone. The seeded
decorators default to `['author','dev']` (a maker never sees raw `provenance`/`classification`/`intrinsic`
chips); system verbs (`select`/`insert`/`open`/`highlight`) are `['author','dev']`; `set-value`/`generate`/
`remove` are for everyone. So the **Make** and **Build** views of the Studio are the *same projection at
two audiences* — Build reveals the meta-actions, decorators, the AI/Context panes and the JSON; Make hides
them by projection, not by hand. New rule: tag what a thing is *for*; never hand-hide. This is the
generalized capability the Studio instance demanded.
- **Text is live data, generated from where you are.** Extend generation-from-data to *copy*: titles,
  descriptions, helper microcopy and status all resolve from the current node/selection/context (via
  `CV_VARS` / a `describe(node)` humaniser), so the words update as the user moves — the interface
  narrates itself. Decorators, axes and actions carry human descriptions the UI surfaces (the registries
  should *describe* themselves; keep extending those descriptions).
- **Native responsive — mobile and landscape.** The shell must reflow to phone portrait and landscape,
  not just desktop. (Status: first attentive pass done in `system/studio.html`; flagged for continued
  upgrade — the interface is a projection and is expected to keep improving.) (Spec:
  `system/glyphic-system.html` §13; demo: `system/studio.html`.)


## 24. The material world — skins are physical laws, and layout is solved from ratios
The skin system (`tokens/skins.css` + the skin axis) renders the interface as a PHYSICAL WORLD, and
every quality of that world is a computed law with one home — never a per-element setting:

- **One light.** The key light is a single constant shared by the texture bake pass and the shadow
  chain (`--key-shadow-x`): every baked highlight and every cast shadow agree on direction by
  construction. A raised slab is LIGHTER than the ground it stands on (value follows elevation).
- **World-coordinate sampling.** Every material surface — recursively, wells included — samples the
  ONE texture at its own world offset (`--mat-tex-pos`, stamped by the solver after layout). Two
  blocks can never show the same grain phase. (`background-attachment: fixed` is banned: it silently
  dies under filter/transform.)
- **Asset span fields.** A texture's on-screen footprint is a field OF THE ASSET (its physical grain
  coverage — `--span-wall`, `--span-face` = wall × ratio), scaled by the one `--world-zoom` camera.
  Ground and slab grain share a single world scale and cannot drift.
- **Cross-depth tone law.** Depth is also a tone coordinate: each rank below its parent shifts one
  shade toward the skin's own shadow pigment (`--depth-tint`), so a well reads as the same world
  recessed — never a separate sticker.
- **The ratio-fit law** (`core/layout-fit.js`, one home for solver + its CSS): media boxes ARE their
  measured aspect ratio (`--asset-ar`, stamped from the asset — letterboxing is geometrically
  impossible); arrangement is SOLVED by comparing the ratios of everything in the container
  (portrait/square media sits beside the text stack in the 42% minor column — imagery outweighs
  words; wide media spans). Gaps and paddings derive from the control rung. "Fit the height, take
  the whole row" flat rules are banned.
- **The motion mandate (forward doctrine).** This mode is an animated realism machine: skin changes
  and block state changes MORPH (stone/glass behaving as liquid or coordinated sand — FLIP
  transitions on the solved layout), the camera zooms/slides across the infinite wall with Vi at its
  centre, and all of it stays a resolution cascade — one value change (`data-skin`) re-binds the
  entire world. Perfect the stone world first; other skins are then parameter tweaks, because the
  laws live in the shared homes.

(Homes: `tokens/skins.css`, `core/layout-fit.js`, `core/world-camera.js`, `core/render3d.js`;
demo: `system/skin-system.html`.)
