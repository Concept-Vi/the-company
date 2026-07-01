# ConceptV Design System

A design system for **ConceptV** — an Australian innovation-technology company building products on **Universal Mechanics**, a proprietary theoretical model of how complex multi-stakeholder systems operate. Universal Mechanics has been developed internally over ten years; ConceptV's competitive advantage is that the engine — and every product built on it — is literally constructed on the mathematics of operation.

## Product surfaces in this system

ConceptV is *not* a single product. The brand expresses three connected platform entities plus an AI framework:

| Entity | Shape (canonical) | What it is |
| --- | --- | --- |
| **User Portal** | Circle | Login + role-aware home for every stakeholder type (designers, developers, sales agents, suppliers, contractors, …) |
| **Property Wizard** | Hexagon | The configuration engine — takes uploaded design files, configures Virtual Hubs |
| **Virtual Hubs** | Octagon | The buyer/viewer-facing panotour experience — the published output |
| **Vi** | Diamond (line-fill) | The internal AI framework that powers all three. The "V<sub style="color:#E0C010">i</sub>" wordmark is set with a gold subscript "i". |

Use the right shape **consistently** when you reference an entity in decks, marketing illustrations, or product UI. The shape system is one of the most distinctive parts of the brand.

> URL pattern observed in mockups: `https://conceptv.io/panotours/yourcompanyname/projectname`

---

## ⚡ v2 — THE GENERATIVE LAYER (read this first)

> 🟢 **Taking over the build with no prior context? Start at `analysis/HANDOFF.md`** — the complete
> seamless briefing (mission, mindset, repo map, conventions, traps, done/next). Then this section.

The original system (everything below this section) was a faithful but **narrow** read of the source: flat ivory, one gold, no texture, "the system feels still." Deep analysis of the full source corpus (12 folders — pitch decks, one-pagers, web mockups, product UI; see `analysis/`) showed the real DNA is richer on every axis. v2 keeps everything genuine below and adds the missing depth. **When they conflict, v2 wins.**

The whole system is now one idea:

> **One type system + one rule engine + two layout solvers** (block = flow/stacking, graph = relational), computed by a small set of orthogonal **axis-dials** over a fixed **invariant DNA core**. `design = f(content, axisPosition)`.

- **Axis-dials** (orthogonal, compose freely): **surface** (desktop · mobile P/L · slide · print · web), **LOD** (summary → pitch → full), **density**, **theme**, **tint/gold intensity**. Set a point in this space → the concrete design is *computed*. → `analysis/AXES.md`.
- **Containment ladder** (the structural spine): `Band → Section → Zone → Cluster → Atom` — typed, composable containers, each with a role, spacing rhythm, collapse rule, and a **wash keyed to nesting depth**. The near-white zoning is *containment depth made visible* (~2% undertone per level), not a semantic colour map — which is why it's "universal and almost imperceptible." → `core/containers.css`.
- **Two solvers** on a shared node type (`core/cv-nodes.d.ts`): the **block solver** (`ContainmentTree`) lays a content tree out by nesting + flow with LOD pruning; the **graph solver** (`DiagramSolver`) computes diagram positions from relationships (network · hub · morph · pipeline · timeline · quadrant · tree · compare · stack · **stepper**). Both compiled into `_ds_bundle.js`, read via `window.ConceptVDesignSystem_c8f43c`.
- **Archetype layer** (`core/Slide.jsx`): a slide archetype is a **pure function `content → CVNode tree`** — "slides ARE templates" (fixed Section/Zone/Cluster subtree + content-as-data). `<Slide archetype content lod surface density/>` builds the chosen subtree and runs it through the solvers, so the same content at a different LOD/density/theme is *recomputed*. The 13 corpus archetypes (cover · split · statement · compare · modes · triptych · metric-band · checklist · timeline · profile · terms · gallery · closing) + `stepper`/`diagram` are registered in `Archetypes`. Atom rendering is an extensible registry (`ContainmentTree.registerAtom`) — a new atom is data, not a code branch.
- **Templates** (`templates/<slug>/`): reusable starting points a consumer copies, written as Design Components (`dc_write`). `templates/pitch-deck/PitchDeck.dc.html` is the ConceptV investor arc as content-as-data, with the **axis-dials (LOD · density · theme) exposed as live tweaks** that recompute the whole deck.
- **The weld** (`core/RenderType.jsx`, `core/archetype-catalog.js`): the design system is being unified from two halves that were built in isolation — the **type system + generator** (`app/registry/*`: the `CV_REGISTRY` 7-layer model + the `proposeType` Vi generator) and the **rule engine + solvers** (`core/*`). `RenderType` is the bridge: it resolves any `CV_REGISTRY` Type + data into the solver IR (`typeToNode`) and renders it through the one engine under the axis-dials. The archetype catalogue is single-sourced in `core/archetype-catalog.js`, read by both the bundle and the app, so there is one list, not three. The full map + staged plan: **`analysis/UNIFICATION.md`**.
- **Universal AXES** (`axes/axis-core.js` → `window.CV_AXES`, `axes/<name>/*`): every primary visual dimension — **Colour · Space · Size · Motion · Texture · Depth · Fill · Form · Symbol** (+ **Meaning** as the contextual layer over them) — is its own typed, hierarchical Axis system in the same `register/resolve/list/query/subscribe` shape as the other registries. **Tokens are the value-units of an axis** (the Colour axis *is* the colour tokens; the Size axis *is* the `--size-*` tokens) — the axis adds type/grouping, never replaces the token graph. Everything visual resolves its value via `CV_AXES.css(axis, value)`; a component's part-slot is a **subscription** `{axis, groups?|values?, default}` and an editor shows `CV_AXES.candidates(sub)`. No consumer hardcodes a value table (motion is the Motion axis; a Glyphic merely subscribes). Plan: `analysis/AXIS-REFACTOR.md`; rules: `DESIGN-LANGUAGE.md` §17.
- **Universal component grammar** (`app/registry/types-core.js`, `conditions.js`, `components-type.js`, `kinds-type.js`): everything on an interface is a **Type** in `window.CV_REGISTRY` declaring **parts · value-slots · sockets · conditions**. Value-slots subscribe to an axis (`{axis, groups?, default}`) or an enum; sockets accept a typed thing or an **event** (`kind:'event'`, onClick→open at an `address`); the shared evaluator `window.CV_COND` gates any condition (one rule in validation + editor). Acceptance is declarative — `candidatesForSocket(socket)` returns what fits, so a panel with a glyphic-accepting socket shows the library with no bespoke code. **Total coverage**: the Glyphic + all 10 UI components + the composition-menu panel + graph/slide kinds + the block/surface/doc library = 94 Types, all in one registry. The **Glyphic Foundry** (`system/glyphic-foundry.html`) generates new symbols into the library via `CV_AI.execute`. Projections: `system/type-system.html` (all Types) · `system/glyphic-system.html` (the model). Rules: `DESIGN-LANGUAGE.md` §18.
- **The Glyphic — the universal component** (`assets/icons/cv-glyphics.js` → `CV_GLYPHIC`, `assets/icons/cv-meaning.js` → `CV_MEANING`, `components/Glyphic.{jsx,d.ts}`, `app/registry/glyphic-type.js`): the icon system, generalised into the brand's compositional **mark** and the **reference universal component**. A Glyphic is a perfect-square element of independent, meaning-bearing **facets** (outer-ring form · symbol · fill · colour · texture · motion · size · depth), composed generatively by one renderer and resolved from single sources. It is registered both as a real **component** and as a **Type** in `CV_REGISTRY` that declares its **parts** (ring · symbol), **slots** (the values each part takes, from the live facet vocabularies) and **sockets** (the typed attachment points it exposes / fills) — the parts/slots/sockets/declarations grammar every other component kind will share, so the interface is a projection of declarations (`accepts()/candidatesForSocket()`), not bespoke code. **Meaning is contextual and loadable**: `CV_MEANING` holds swappable meaning profiles (what a form/colour-value/texture/depth means in a given context) — the lone exception being symbols, whose meaning is intrinsic. The AI glyphic-foundry capabilities (`app/ai/ai-glyphic.js`: `glyphic.generate` · `glyphic.save`) write schema-valid symbols into the library. Full living spec + the verbatim briefs + decomposition: **`system/glyphic-system.html`** (Design-System tab → “Glyphic System”).
- **Component layer** (`tokens/controls.css` → the `Button` / `Card` / `Input` / `Badge` / `Tabs` / `Segmented` / `Switch` / `Avatar` primitives in `components/`): the bread-and-butter controls — buttons (gold action · dark panotour · gold-outline pill · ghost · soft · sage comm), cards (cream / surface / outline / gold / raised), fields (gold-focus inputs, textarea, select, search), badges, stat pills, chips, tags, tables, dividers, plus **tabs** (gold-underline active, the dashboard tab bar), the **segmented audience toggle**, **switches** (gold-on), **avatars**, **tooltips**. Token-pure and theme-aware (every value resolves to a role token incl. `--on-gold` for fixed-gold surfaces, so the same class works on light/dim/dark/clean grounds), grounded in the source's real control vocabulary. The React primitives are thin wrappers over the `cv-*` classes; see the **Component Library** card.
- **Token layers** (`styles.css` → `colors_and_type.css` + `tokens/*.css`): the gold is now a **ramp** (`--ramp-1..4`, gold→bronze→tan) not one swatch; texture (hatch + blueprint ghost), elevation, motion ("nothing teleports"), density, theme, fluid type, and the **typed frame ratios** (ratio = a type; w/h derived by `calc`) all live here as registered tokens.

Canonical docs: **`DESIGN-LANGUAGE.md`** (the rules), **`analysis/AXES.md`** (the model), **`analysis/UNIFICATION.md`** (welding the type system to the engine), **`analysis/DIAGRAMS.md`** (the 10 diagram types), **`analysis/INTEGRATION.md`** (how new things connect without drift), **`analysis/SYNTHESIS-PLAN.md`** (the build order).

---

## Sources used to build this system

| Source | Stored at | Notes |
| --- | --- | --- |
| Real ConceptV wordmark + V mark (light, white, yellow) | `assets/logos/` | Provided in inspo2 — the authoritative logo assets. |
| Customer brand-kit screen | `assets/reference/dashboard_brandkit.jpg` | The customer's brand kit form. |
| Gallery / Calendar / Landing-Page editor / Virtual-Hub Settings | `assets/reference/dashboard_*.jpg` | Core dashboard product surfaces. |
| Comment-capture popup | `assets/reference/comment_popup.png` | Annotation/status flow inside hubs. |
| Bronze line-icon library (~80 glyphs) | `assets/icons/icon-library-bronze.jpg` | The canonical illustration icon set. Reference this sheet by name when designing diagrams. |
| Gold circle-icon family | `assets/icons/icon-library-gold-circles.jpg` | Entity-badge icons used in architecture diagrams. |
| Architecture & process diagrams | `assets/illustrations/` | Staged delivery, platform overview, stakeholders, Vi framework, account-creation flow, …  |
| `inspo/Deck 1 Presentation.pdf` | `inspo/` | 16-page pitch deck (image-only PDF). |

The conceptv.com.au website was offline during exploration, so this system has been calibrated against the mockups + provided assets alone. Colours were sampled pixel-accurate from the real logo PNG: `#E0C010`.

---

## Index — manifest of the root folder

```
.
├── README.md                  ← you are here
├── SKILL.md                   ← agent skill entrypoint
├── DESIGN-LANGUAGE.md         ← v2 — the cross-cutting design rules
├── styles.css                 ← v2 — single entry point: imports tokens + core
├── colors_and_type.css        ← the source-of-truth colour/type/zone tokens
├── tokens/                    ← v2 — surfaces, sizing, motion, depth, texture, theme, density, diagram, controls (component layer), …
├── components/                ← v2 — the UI primitives: Button · Card · Input · Badge · Tabs · Segmented · Switch · Avatar · Modal · Stepper · Glyphic (the universal compositional mark) — token-pure wrappers over tokens/controls.css + CV_GLYPHIC
├── system/                    ← v2 — living specs (markable in the DS tab): system/glyphic-system.html = the Glyphic / universal-component model
├── core/                      ← v2 — the generative core: containers.css + block & graph solvers + Slide (archetypes)
├── templates/                 ← v2 — reusable starting points (DCs): templates/pitch-deck/ = the investor arc
├── analysis/                  ← v2 — the full source-corpus analysis + the model (AXES, DIAGRAMS, …)
├── assets/
│   ├── logos/                 ← real ConceptV wordmark + V marks (PNG)
│   ├── icons/                 ← 99-icon library: cv-icons.js, CvIcon.jsx, svg/, index.html explorer
│   ├── illustrations/         ← architecture diagrams, process flows, Vi framework
│   └── reference/             ← raw screenshots of the source product
├── preview/                   ← Design-System-tab cards (~30)
├── ui_kits/
│   ├── platform/              ← creator-side dashboard (Gallery, Calendar, Brand Kit, Hub Settings)
│   └── virtual-hub/           ← viewer-side panotour experience (menu, info, floorplan, capture)
└── inspo/                     ← original source materials, unmodified
```

---

## CONTENT FUNDAMENTALS

ConceptV's voice is **calm, professional, and slightly formal** — the tone of a serious-but-friendly Australian technology firm explaining a precise system to a sophisticated stakeholder.

### Voice characteristics

- **Sentence case for everything, including button labels and screen titles.** Observed throughout: "Brand Kit", "Landing Page", "Page Settings", "Top Tasks & Reminders". No ALL-CAPS or shouty marketing voice. (One exception: in-frame system labels like `MENU` and `CLOSE` on the viewer's overlay are uppercase — a deliberate utility shift.)
- **Direct second-person ("you"), not first-person plural.** Example: "You can upload variations of your logo, or logos of collaborators." Never "We let you…" or "Users can…".
- **Imperative for actions.** Buttons and action chips are verbs: *Select, Filter, Sort, Search, Clear Filters, Create New, Upload, Manage, Preview, Publish, Deactivate*.
- **Compact helper copy under inputs, never floating tooltips.** Under "Hub Name" the helper line is `URL preview: https://conceptv.io/panotours/yourname/projectname` with the variables in gold. **Inline previews of consequences** is the brand's signature copy pattern.
- **No exclamation marks. No emoji in body copy.** (Sidebar nav uses colour-emoji as icons — see *Iconography* — but never inside body copy or buttons.)
- **Sparing inline gold accent for emphasis.** Only for: dynamic URL fragments, the active label inside a help line, link text. Never for arbitrary emphasis.

### Vocabulary anchors

The platform is called a **Virtual Hub**. Individual interactive spaces are **Hubs**. Per-stage variations (entry, apartment A, apartment B) are **Linked Hubs**. The buyer-facing pages are **Landing Pages**. Annotated screenshots inside hubs are **Captures**. The pipeline is **Revit → Enscape → ConceptV**. The AI framework is **Vi**. Service tiers are **Stage 1 / Stage 2 / Stage 3 + Marketing Package** (see `assets/illustrations/staged_delivery.png`).

### Numeric / system labels

Status dots are colour-coded with one word: `Pending`, `Approved`, `Resolved`, `Rejected`. Dates use slashes: `15/05/24`. Notification counts sit on a small red badge (no plus, no "9+"). Percentage stats in marketing materials use a **large gold number** with a soft-gold panel background and a single descriptive line beneath (see `assets/illustrations/stats_panels.png`).

---

## VISUAL FOUNDATIONS

ConceptV's visual language is **warm-paper-with-gold-ink**: an ivory canvas, near-black text with warmth, a saturated mustard-gold for everything that earns attention, and a deeper bronze used almost exclusively for line-drawn illustrations.

### Colours (sampled pixel-accurate from the real logo)

- **Gold accent — `#E0C010`** (sampled from the V-mark PNG, 234 036 pixels). Used for: primary buttons, active-state borders, link emphasis, screen titles, dashed empty-state outlines, status dots.
- **Bronze — `#988058`** (sampled from illustration figures). Used for: line-drawn illustrations, screen titles ("Brand Kit", "Gallery"), and the architectural icon set. Almost never UI chrome.
- **Ink — `#1F1A12`**. Near-black with a warm undertone.
- **Canvas — `#FBF7EC`**. Slightly-warm ivory page background.
- **Sunken — `#E8E2CC`**. Image-card placeholders, dropzone interiors, "no upload yet" panels.
- **Soft gold panel — `#FBF4C8` → `#FDFAEB`**. The background for grouped form sections.

No purple, no teal, no cool-grey neutral. Status colours are warm-shifted — desaturated and tilted toward yellow.

### Type

- **Display & screen titles — Sora, 600/700, tight tracking.** Substituted from a near-system custom sans observed in mockups.
- **Body & UI — DM Sans, 400/500.**
- **Mono — JetBrains Mono.** URLs, IDs, code samples.

> ⚠ **Font substitution flagged.** Real product font is unknown — please share `.woff2`/`.ttf` files for an exact match.

### Spacing & layout

- 8 px base grid. Spacing scale `4 / 8 / 12 / 16 / 20 / 24 / 32 / 48 / 64 / 80 / 96`.
- Dashboard layouts use a fixed-left **~280 px sidebar**, then 32–48 px gutters before content begins. Generous breathing room.
- **Section panels rather than card-on-card.** Form groups sit on a tinted soft-gold wash (`--accent-gold-50`) with no outer border, panel title above. Reach for this before an outlined card.
- **Cards**: white fill, no border, soft warm shadow, 12 px radius.
- **Image / video placeholder tiles**: `--bg-sunken` fill, no border, 4 px radius.

### Backgrounds & imagery

- Page backgrounds are **flat ivory**. *(v2: product-UI chrome stays flat; decks/marketing/presentation surfaces carry the low-opacity texture layer — hatch + blueprint ghost — and the depth-keyed zone washes. See `tokens/texture.css`, `core/containers.css`.)*
- Hero imagery is photographic, full-bleed, **warm-toned architectural** — beige stone, soft sun, light timber, marble. See `assets/illustrations/staged_delivery.png` for the canonical interior-render mood.
- Illustrations are **always** the bronze-line style at ~1.5 px stroke weight, rounded caps, no fills. Never coloured-in.

### The shape system (one of the most distinctive parts of the brand)

When the design references a platform entity, **use its canonical shape**:

- **Circle** — User Portal (login + account)
- **Hexagon** — Property Wizard (config engine)
- **Octagon** — Virtual Hubs (output)
- **Diamond with line-fill** — Vi (AI framework). Set the wordmark as "V<sub style="color:#E0C010">i</sub>" — capital V in ink, lowercase "i" in gold and slightly subscripted.
- **Rounded rect (12 px)** — generic entity / fallback

Architecture diagrams sit on a flat canvas, with the shaped entities joined by thin gold lines and dashed gold arrows. Categories of entity (Stakeholders, Files, …) are listed inside outlined gold rectangles. Use-case grids tile small reference screenshots in white cards with bronze borders.

### Process flow pattern

- Outlined gold cards joined by **dashed gold arrows with arrowheads**.
- Smaller pill cards sit *on* the connector (e.g. "1 – 2 Weeks", "Revision") to label the transition.
- Stage titles are display 700 in bronze; descriptions are body 11–13 px in fg-secondary.
- Cream-tinted variant (`--accent-gold-50`) for emphasis on alternating stages.

### Corner radii

- Small chips / checkboxes: **4–6 px**
- Buttons & inputs: **8 px**
- Cards & panels: **12 px**
- Modal / popup containers: **16 px**
- Pill shapes: full-round — only for status dots and the floating Chats button

### Borders

- Default cards have **no border** — separated by shadow + background contrast.
- Active-state borders are **dashed gold** — used for sidebar "favourited options" slots, upload-empty states, the active sidebar item.
- Form inputs are solid `1.5 px gold` — they read as "ready for input" by default. Focus state intensifies the border.

### Shadows / elevation

- Cards: very soft warm shadow, no offset hardness.
- Floating popups (Chats, comment popup): a slightly stronger drop.
- No inner shadows. No coloured glow shadows.

### Hover, press, motion

- Buttons: gold buttons darken ~10% on hover, ~20% on press.
- Sidebar items: white card appears on hover (matching the active state minus the dashed border).
- No scale transforms on press. No bounce. No entry animations on page load. The system feels still. *(v2: the product UI stays calm, but the system now has a full motion language — "nothing teleports": elements enter/exit by moving, state changes are choreographed, the network→hub morph tweens. Calm ≠ static. See `tokens/motion.css`, `DESIGN-LANGUAGE.md`.)*
- Transitions are 200 ms, `cubic-bezier(.2, .8, .2, 1)`.

### Transparency & blur

- Only the dark in-hub overlays (`MENU` / `CLOSE` toolbar) use `rgba(31,26,18,.92)` + 12 px backdrop-blur over the photo. The dashboard is opaque.

### Fixed elements

- Left navigation rail (fixed, ~280 px).
- Top-right notification + avatar cluster, scoped to the content column.
- Floating **Chats** pill, bottom-right of every dashboard surface.

---

## ICONOGRAPHY

ConceptV uses **three distinct icon families** for different purposes. Recognising which to reach for is essential.

### 1. Sidebar navigation — colour emoji as icons

The platform's main left-rail uses full-colour emoji glyphs in front of each label: 🗂 Projects · ⌨ Dashboard Updates · 🌐 Landing Pages · 📁 Files · 📷 Gallery · 🎨 Brand Kit · 📅 Calendar · 📄 Templates · 🛒 Pricing & Ordering · 🔌 View All · 💬 FAQs · 📘 Tutorials. **Preserve this convention** on platform-side surfaces.

### 2. The CV Icon Library — 99 vectorized line icons

The brand owns a **single canonical icon library** at `assets/icons/`:

- **`cv-icons.js`** — JS module that exposes `window.CV_ICONS.data` (a `{name: pathBody}` map of all 99 icons) plus `CV_ICONS.svg(name, opts)` and `CV_ICONS.markup(name, opts)` helpers for vanilla use.
- **`CvIcon.jsx`** — React component. Renders any icon with tone (`bronze | gold | ink | muted | cream`), size, and optional gold-circle entity-badge wrapping (`circle`, `circle filled`, `desaturated`).
- **`svg/`** — one individual `.svg` file per icon. Use as `<img src="assets/icons/svg/house.svg"/>` or via `<use>` for static contexts.
- **`index.html`** — searchable, filterable explorer. Click any icon to copy its name.

All icons share one design language: **24 × 24 viewBox, 1.5 px stroke, `currentColor`, rounded caps and joins, no fills** (unless intentional). They tile in nine categories:

| Category | Glyphs | Examples |
| --- | --- | --- |
| People & roles | 8 | person, people, handshake, team, user-network |
| Files & docs | 13 | file, files-stack, file-upload, brochure, clipboard, folder-gear |
| Communication | 9 | chat, chat-tree, megaphone, megaphone-link, bell, share, link, email |
| Architecture | 13 | house, house-multi, building-tall, crane, floorplan, blueprint, vr-headset, drone, 3d-cube, m² |
| Browser & dashboard | 11 | browser-house, browser-chart, monitor-house, dashboard, video-player, image-stack |
| Actions | 12 | plus, minus, check, close, edit, eye, eye-off, search, filter, sort, swap, refresh |
| System & status | 14 | gear, cloud-upload, database, dollar-circle, info-circle, lightbulb, location-pin, pin-route, calendar, color-swatches, sun-moon |
| Logic & flow | 10 | network, decision-tree, hierarchy, atom, globe, pie-chart, path-flow, check-square, no-symbol |
| Platform-specific | 9 | play, pause, lock, unlock, star, tag, workstation, connector, shop-cart |

### 3. The gold-circle entity badge — the same icons, wrapped

The brand's signature diagram treatment: any icon inside a thin gold ring. Use it whenever the icon represents an entity in a system architecture (User Portal, Hub, Stakeholder, etc.) — not for plain UI chrome.

```jsx
<CvIcon name="house" />                         // plain, 24px, bronze
<CvIcon name="house" tone="gold" size={32} />   // gold, larger
<CvIcon name="house" circle />                  // outline gold ring
<CvIcon name="house" circle filled />           // filled gold, ink glyph (active entity)
<CvIcon name="house" desaturated={0.5} />       // 50% strength (inactive state)
```

The desaturated variant is the canonical **state-strength gradient** for diagrams — fade an icon to show inactive / unconnected entities while keeping the active ones at 100%.

### 4. Status / decoration

Status uses **filled coloured dots** (8–10 px circles), never icons-with-meaning. Notification bell has a red circular numeric badge — no `+9`.

### Extending the library

To add a new icon: open `assets/icons/cv-icons.js` and append an entry to `CV_ICONS.data`. Keep the conventions (`viewBox="0 0 24 24"`, 1.5 px feel, rounded caps, no fills, `currentColor`). Re-run the SVG-generation script if you need individual files. The explorer at `assets/icons/index.html` will pick the new icon up automatically.

---

## UI Kits

| Kit | Path | What it covers |
| --- | --- | --- |
| **Platform dashboard** | `ui_kits/platform/` | Creator-side surfaces: sidebar (with real wordmark), Gallery, Calendar, Brand Kit, Virtual Hub Settings. |
| **Virtual Hub viewer** | `ui_kits/virtual-hub/` | Buyer-side panotour experience: hub frame, MENU/CLOSE toolbar, Info / Share / Floorplan panels, comment-capture popup. |
| **Vi (AI workspace)** | `ui_kits/vi/` | Three-pane workspace for the Vi AI framework: chat + live task-tree + brochure preview. Interactive brochure-builder demo. |

Each kit's `index.html` mounts the full surface composed; individual `*.jsx` components are designed to be lifted and reused.
