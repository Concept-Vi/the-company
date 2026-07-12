# BLOCKS — the container universal component

> Companion to `analysis/AXES.md` (the generative model) and the Glyphic spec
> (`system/glyphic-system.html`). The Glyphic is the reference universal component
> for **marks**; the BLOCK is the same grammar applied to **containers**. Read this
> before touching `app/registry/block-type.js`, `tokens/material.css`, or
> `system/block-system.html` (the living spec).

## 1. What a block is

A **block is the tangible unit of a zone** — a bounded, addressable region of a page.
Everything a page shows lives inside one: glyphics, text, controls, media, *and other
blocks*. The whole page is itself a block (level `page`); a page is a **composition of
blocks and their rules**; and every block resolves through the ONE operation
(`CV_NODE.resolve` → the `block` solver), so the entire page is eventually made only
of resolutions.

A block is composed of exactly two **parts** plus its own whole-unit dials:

| Piece | What it is | Its slots (each a subscription to an axis) |
|---|---|---|
| **ground** part | the plane *behind* the surface — what translucent materials refract | `color` (color axis, neutral/brand), `texture` (none · grid · grain), `motion` (ambient drift) |
| **surface** part | the material sheet — what you see and what contains | `material` (**material axis**: glass · parchment · stone · none), `elevation` (depth axis), `tint` (color axis, semantic — the tonal whisper; gold reserved for Vi), `texture` (override) |
| whole unit | the block's own dials | `level` (the depth coordinate), `keyline` + `gap` (space axis), `flow` (flow axis), `density`, `contain` |

This mirrors the Glyphic exactly: ring/fill/symbol ⇢ ground/surface/content; every
slot's vocabulary is resolved live from its axis, never copied.

## 2. Coordinates in depth — the containment ladder

Blocks have **coordinates**: `{ level, path }`.

- **`level`** is the rung on the containment ladder — the zoning ladder made
  addressable: `page(0) → region(1) → panel(2) → card(3) → well(4)`, plus
  `overlay(5)` above the flow. The level **derives** the material depth-modifier
  (panel = base, card/well = inset, overlay = raised) — nesting depth is never
  styled by hand; it is *read off the coordinate*.
- **`path`** is the address from the page root through named sockets:
  `page/main/pipe[2]` — the same addressability glyphics have (`ring.fill`),
  assigned by `CV_BLOCK.walk()`, never hand-set. **Composition IS the coordinate
  system.**

## 3. The MATERIAL axis — glass is a value, not the system

The liquid-glass work (slices 104–114) built one material deeply. Blocks generalize
it: a surface's substance is a **material axis value**:

- `glass` — translucent; binds to `tokens/glass.css` (glass's home is untouched).
- `parchment` — opaque warm paper, fibre texture. Home: `tokens/material.css`.
- `stone` — opaque cool mineral, speckle, squarer corners, lower lift. Home: same.
- `none` — the zero: a block that is pure layout (the page block usually).

One consuming utility (`.material` + `--raised`/`--inset` modifiers) reads one set
of roles (`--mat-*`); each material is a `[data-material]` scope binding those roles
to its own tokens. All materials derive from `--zone-ground`/`--ink`, so all of them
recompute across light/dim/dark/contrast. **The ground behind the surface is
independently switchable** (`data-ground-texture`): the backdrop is the ground part's
business, not the material's.

## 4. Ordered sockets, and actions as sockets

Sockets carry an **`order`** — reading order, render order, address order:

`header(1) → body(2, multiple) → footer(3) → primary(4) → actions(5) → onActivate(6)`

The last three are **ACTION sockets**: they accept `action` and are filled by
address `"action:<id>"` from **CV_ACTIONS** — the verbs registry (already the
system's eighth registry). `CV_NODE` resolves the address through CV_ACTIONS the
same way it fills every other socket (one mechanic, different home), and
`CV_NODE.candidates` on an action socket lists the verb catalogue. `primary` is THE
verb of a block (one gold voice per block, max); `onActivate` is the event socket —
what the block *does* when activated.

## 5. The rules a block obeys (all pre-existing, now subscribed)

- **`.keyline`** — shared content inset (density-derived); siblings align by construction. **The keyline
  belongs to SURFACES**: a material-`none` block is pure layout and is transparent to the keyline (padding an
  invisible box double-insets its children and breaks cross-depth alignment); the page is the one exception
  (its keyline is the artifact margin). `chrome()` enforces this.
- **`.contain`** — clip to the rounded box; a block's content cannot cross its border.
- **`.flow`** — counted children arrange by the computed equation; overflow intent is
  the flow-axis value (wrap/reel/fixed). Text inside obeys the typed-text budgets
  (`tokens/text.css`).
- **Conditions** (CV_COND, on the Type): `tint requires material != none`,
  `reel requires level != page`, `primary requires level != page`.

## 6. The one operation

```js
// resolve the Type (structure) …
const ir = CV_NODE.resolve('block');
// … or get chrome for an instance spec (level+material+… → classes/attrs/style):
const c = CV_BLOCK.chrome({ level: 'card', material: 'parchment', tint: 'review' });
// → { tag, level, classes:['material','material--inset','contain','keyline'],
//     attrs:{ 'data-material':'parchment', 'data-glass-zone':'review' }, style:{} }
// assign coordinates over a whole page spec:
CV_BLOCK.walk(pageSpec, (node, coord) => { /* coord.path, coord.depth, coord.level */ });
```

The solver emits **only system utilities and tokens** — no literal ever leaves it.
`CV_NODE.render({kind:'block',…})` reaches it as the `block` kind solver; layout of
tree content stays with the existing engines (ContainmentTree / the flow equation) —
the block solver computes the **surface**, coordinates, and socket order.

## 7. Homes (nothing has two)

| Thing | Home |
|---|---|
| Block Type (grammar: parts/slots/sockets/conditions) | `app/registry/block-type.js` |
| Materials (parchment/stone + the `.material` consumer) | `tokens/material.css` |
| Glass material | `tokens/glass.css` (unchanged) |
| Material axis (typed view) | `axes/material/material-axis.js` |
| Flow axis (typed view) | `axes/flow/flow-axis.js` (mechanism: `tokens/layout.css` §FLOW) |
| Containment ladder (levels) | `LEVELS` in block-type.js, exposed as `CV_BLOCK.levels()` |
| Actions | `CV_ACTIONS` (`app/registry/actions.js`) — sockets hold addresses only |
| The graph layout engine (positions COMPUTED from relations) | `core/graph-layout.js` → `window.CV_GRAPH_LAYOUT.solve(graph)`. ONE home for both the DiagramSolver and the skin/board painter; types incl. `column` (hub + orbit + columns + fx/fy furniture) |
| Living spec + demo | `system/block-system.html` |
| Skins (the registry of worlds: glass · stone) | `tokens/skins.css` (bindings + states + threads) · `axes/skin/skin-axis.js` (the registry) · `system/skin-system.html` (living spec) · `analysis/SKINS.md` (decomposition + quality bar) |

## 8. Open / next

- Graduate the tonal-glass experiment's `[data-glass-zone]` tints into a proper
  `tint` home consumed by the surface part (today the experiment file holds them).
- Registry inspector: surface `CV_BLOCK.orderedSockets()` + the ladder in the
  Studio's block editor (TypeBuilder already handles layer `block`).
- Teach `ContainmentTree` to read `CV_BLOCK.chrome()` for its zone washes so the
  deck solver and the app chrome share the surface computation.
- More materials (velum? mesh?) = one `[data-material]` scope + one axis value —
  no consumer changes, by construction.
