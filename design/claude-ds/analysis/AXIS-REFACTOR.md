# AXIS REFACTOR — the universal axis systems (master scope)

> Written at the convergence point (Info/Tim's message, slice 59). This is the
> durable home for the plan so it is not lost across the long build. Update the
> STATUS column as each lands. Companion: `system/glyphic-system.html` §08.

## The principle (what we're building)

Every **primary axis** of the design language is its own **dedicated system** — a
hierarchical, typed registry of values — and **everything** built on this system
**resolves its value of that axis from that system**. No axis is owned by a
consumer. Motion is not "glyphic motion"; it is the **Motion axis**, with many
types/groups, and a Glyphic is just **one consumer** that **declares which motion
it subscribes to** in its part slots. Same for colour, space, size, form,
texture, depth, fill, symbol, meaning — and any axis we discover.

This generalises the Glyphic facet model: a facet WAS already "an axis value
resolved from a single source." We now make each source a **first-class Axis
system** with one shared shape, and make component slot declarations
**subscriptions** to an axis (+ a value subset), under conditions. The engine
resolves every visual value through an axis.

### Tokens ARE the value-units (Info, slice 60)
An axis does **not** replace or wrap "over" the token system — **the tokens are
the typed units of value on the axis**. The colour axis *is* the colour tokens
(typed/grouped); the size axis *is* the `--size-*` tokens; etc. A value's `token`
is its canonical identity; `resolveCSS()` returns `var(--token)`; the literal
stays in its stylesheet home. A component's slot declares a **token** (through an
axis value). Tokens are core to the whole model, not superseded by it.

### Anti-drift mandate (applied to axes)
One home per axis. Consumers hold references (subscriptions), never copies. No
hardcoded per-consumer value tables — the glyphic's local `.mo-*` set MUST become
a Motion-axis subscription. Loud fail on missing axis/value. The interface is a
projection of the axis registries.

## The shared Axis shape (CV_AXIS)

A generic factory so every axis has the SAME API (mirrors CV_REGISTRY / CV_AI /
CV_MEANING): `register/resolve/list/query/subscribe`, **hierarchy** (group →
subgroup → value, via `parent`/`group`), `values()`, `groups()`, `resolveCSS()`
(value → token/CSS), `default`, and `meta`. Each axis instance is registered in a
top-level **CV_AXES** registry so the set of axes is itself enumerable/typed.

A **subscription** (what a component slot declares): `{ axis, values?: [...] |
groups?: [...], default, conditions? }`. `candidates(subscription)` → the allowed
values; this is what an editor/foundry shows.

## The axes (initial set — extend as discovered)

| Axis | Home (planned) | Wraps / source | STATUS |
|---|---|---|---|
| **(foundation)** | `axes/axis-core.js` → `CV_AXIS`/`CV_AXES` | — | TODO |
| Motion | `axes/motion/` | NEW typed groups + keyframes (replaces cv-glyphic.css motion) | TODO |
| Colour | `axes/color/` | colour token graph (colors_and_type.css) | TODO |
| Space | `axes/space/` | spacing tokens | TODO |
| Size | `axes/size/` | icon/size tokens | TODO |
| Form | `axes/form/` | CV_SHAPES.geom (n-gon) | TODO |
| Texture | `axes/texture/` | tokens/texture.css | TODO |
| Depth | `axes/depth/` | tokens/depth.css (--elev-*) | TODO |
| Fill | `axes/fill/` | colour-token recipes | TODO |
| Symbol | `axes/symbol/` | CV_ICONS (intrinsic-meaning) | TODO |
| Meaning | reconcile `CV_MEANING` into axis pattern (contextual, loadable) | — | TODO |

> Symbol & Meaning are special: Symbol values carry **intrinsic** meaning;
> Meaning is the **contextual/loadable** layer (profiles). Keep that distinction.

## Build order (each step independently usable; commit + check between)

1. `axes/axis-core.js` — CV_AXIS factory + CV_AXES registry + subscription helpers.
2. **Motion axis** first (it's the live pain point): typed groups (ambient /
   attention / interactive / process …) → values → keyframes. Port the 8 glyphic
   motions in as values; delete the hardcoded ownership from cv-glyphics/glyphic.css.
3. Refactor **Glyphic** to a **subscriber**: its part slots declare
   `{axis:'motion', groups:[...]}`; compose() resolves via CV_AXIS.
4. Stand up the other axes wrapping existing single sources (no value duplication
   — they reference the token/source that already exists).
5. Update **slot declarations** (glyphic-type.js valueSlots → subscriptions) and
   the **Glyphic component** + explorer/spec consumers.
6. **Directory restructure** into `axes/` (+ keep compiler-required paths:
   styles.css closure, components/*.{jsx,d.ts}, @dsCard html). Move carefully;
   update every `<script src>`/`@import`. Validate after each move.
7. Reconcile consumers + app load order; check_design_system clean each time.
8. README + DESIGN-LANGUAGE + FINDINGS-LOG in lockstep.

## DO-NOT-LOSE — carried scope from before this refactor (still owed)

- **Foundry conversational UI** (propose → feedback → click → iterate → Save
  panel); capabilities `glyphic.generate`/`glyphic.save` + schema already built.
  Needs §7 value-vocab sign-off + live provider. (spec §6 step 6)
- **Consumer convergence**: brand_shapes / brand_vi / components_box_variants →
  onto CV_GLYPHIC.render (cosmetic; same single source one layer down).
- **§7 open questions** still awaiting Info/Tim: unit/facet naming, v1 facet set,
  Form-axis ends, meaning vocabularies, the value variable, taxonomy depth.
- Event-sockets / addresses / conditions on sockets — declared in spec §05c,
  registry `accepts()` seeded; full condition engine not yet built.
- Slot/socket **conditions** generally (e.g. "texture requires fill != none") are
  declared as strings; no evaluator yet.

## Autonomy note

Info/Tim will not comment until this is fully implemented; I add to scope anything
I find that needs merging into this foundation (else it becomes "a part of the
system that is not part of the system"). Use the questions tool only to BATCH
genuinely-blocking options; otherwise decide and proceed.

## STATUS LOG (newest first) — mirror key moves in FINDINGS-LOG.md
- **Universal grammar completion + total coverage** (slice 61). Condition evaluator
  `app/registry/conditions.js` → CV_COND (structured / string-DSL / predicate; used by
  accepts()/slotEnabled/subscription-validate — one rule everywhere). Event-sockets +
  addresses: socket schema gained kind('slot'|'event')/event/address/onPick + socketInfo().
  TOTAL COMPONENT COVERAGE: app/registry/components-type.js registers the 10 UI components
  (Button/Badge/Avatar/Card/Input/Switch/Tabs/Segmented/Stepper/Modal) as Types with
  classification + value-slots (axis subscriptions / enums) + content/event sockets; Glyphic
  already done = 11. kinds-type.js adds the composition-menu PANEL (with a glyphic-accepting
  socket — declarative acceptance demo: candidatesForSocket → 7 matches, no bespoke code) +
  graph/slide kind refs. Seed token/shape Types reconciled to axes (axis/axisValue fields).
  Projection card system/type-system.html (94 Types across 6 layers, live from CV_REGISTRY).
  Foundry UI system/glyphic-foundry.html (conversational propose→feedback→save, routes through
  CV_AI.execute(glyphic.generate/save) with graceful demo fallback; verified generate→render→
  save 126→127). check_design_system clean.
  - **H (consumer convergence) — resolved by analysis, not forced**: brand_shapes/brand_vi/
    components_box_variants render ENTITY VESSELS (shape+label / fillable image-slot) via
    CV_SHAPES.markSVG; CV_GLYPHIC.render delegates to that same single source. They are not
    glyphics (composition layer), so routing them through CV_GLYPHIC would be a category error.
    They already resolve from the one source — no change needed.
- **axes/ foundation + all 9 axes BUILT & verified** (slice 60). `axes/axis-core.js`
  → CV_AXIS factory + CV_AXES registry (register/resolve/list/query/subscribe,
  hierarchy, resolveCSS, candidates/validate for subscriptions). Axes: color ·
  space · size · motion · texture · depth · fill · form · symbol — all registered,
  resolve at runtime (verified: motion glow→mo-glow, color gold→var(--accent-gold),
  size md→var(--size-md)+40px, symbol 126 values, meaning bridge ok).
  - **Tokens ARE the value-units** (Info clarification): values carry `token` as
    canonical id; added `--size-*` element ramp to tokens/sizing.css (size axis is
    those tokens). color/space/size/depth axes are token-backed; form/symbol wrap
    their live value sources (CV_SHAPES/CV_ICONS); motion/texture/fill name values
    realised in CSS/markSVG.
  - **Motion de-owned from Glyphic**: keyframes moved to axes/motion/motion.css,
    value set to axes/motion/motion-axis.js; cv-glyphic.css now base-only;
    CV_GLYPHIC.motionClassFor() resolves via the Motion axis (legacy fallback).
  - **Slots → subscriptions**: glyphic-type.js valueSlots now `sub(axisId,
    {groups?/values?,default})` resolved live from CV_AXES (no copied vocab).
  - **Meaning reconciled**: CV_MEANING.facets ARE axis ids; added CV_MEANING.axis()
    bridge; symbols remain the intrinsic exception.
  - **Wiring**: app/index.html + spec + explorer load the axis layer in order
    (axis-core → value sources → axes → meaning → glyphics). check_design_system
    clean (499 tokens, Glyphic compiles, no issues).
  - **Directory**: new `axes/<name>/` tree is the home of the axis layer. Legacy
    value-source libs (cv-shapes/cv-icons/cv-glyphics/cv-meaning) stay in
    assets/icons/ (moving them breaks ~20 card refs for no single-source gain —
    they're already the one home; the axes reference them). Documented, not drift.
- (pending) scope captured; build starting at axis-core.
