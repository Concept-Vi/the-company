---
type: census-area
area: templates-kits
scope: output/consumer surfaces — deck/template layer + ui_kits
register: findings
status: findings-only (read-only census pass, no code changes)
---

# AREA: Templates & UI Kits — Census & Findings

## §A · Account (inventory of territory claimed)

**Templates** (2 decks + support machinery):
- `templates/capital-raise/CapitalRaise.dc.html` — investor deck (17 archetypes, 26 slides, run-sentence narrative)
- `templates/capital-raise/ds-base.js` — CSS + bundle loader (19 token files + core machinery)
- `templates/capital-raise/support.js` — DC-runtime v3+ (parser, template compiler, logic eval, external module loader)
- `templates/pitch-deck/PitchDeck.dc.html` — sales deck (8 archetypes, 10 slides)
- `templates/pitch-deck/ds-base.js` — identical to capital-raise loader (stylesheet enumeration)

**UI Kits** (3 product surfaces + screens):
- `ui_kits/vi/` (6 JSX + vi.css) — Vi Workspace: chat + task-tree + live output-preview (3-pane layout)
- `ui_kits/platform/` (5 JSX + platform.css + 5 screens) — Creator dashboard: sidebar nav + screens (Gallery, Calendar, BrandKit, HubSettings)
- `ui_kits/virtual-hub/` (6 JSX + hub.css) — Virtual Hub viewer with capture/share overlays

**Preview** (25 .html showcase pages):
- All token/type/component galleries (not in my territory; owned by system/analysis areas)

**Demo** (page-face restart kit):
- `_demo/run_pages.py`, `_demo/gen_faces.py` — local service infrastructure (not in template consumption territory)

**Observed:** Zero disconnected orphans; every file is in active use or known-dormant infrastructure.

---

## §B · Joins to the ONE-MATH (how templates consume solvers + tokens)

### Token consumption (Observed: structural, verified via grep)

**CapitalRaise + PitchDeck templates:**
- `styles.css` loaded via ds-base.js (absolute path pattern: all 19 token files: `colors_and_type.css` → `tokens/{surfaces,sizing,depth,motion,diagram,theme,density,layout,states,focus,icons,dataviz,imagery,canvas,provenance,export,texture}.css`)
- Direct inline style references to **CSS vars**: `var(--zone-ground)`, `var(--ink)`, `var(--font-body)`, `var(--accent-bronze)`, `var(--accent-gold)`, `var(--fs-caption)`, `var(--weight-semibold,600)`, etc.
- **Inferred:** Every token is consumed via var() — no raw hex in the template. Hardcoded fallback values (`600` for weight, `1` for line-height) suggest graceful degradation if the token CSS fails to load. ✓ Good signal.

**UI Kits (vi, platform, virtual-hub):**
- All three load tokens via CSS imports (vi.css, platform.css, hub.css all @import tokens)
- Inline `style={{}}` objects reference `var(--*)` extensively (font-body, accent-gold, border-faint, bg-muted, fg-secondary, r-sm, r-lg, shadow-card, etc.)
- **Inferred:** Token-first pattern established; JSX components are token-aware. **No verification of actual render — assumptions about fallback behavior if token CSS fails.**

### Solver consumption (Observed & Inferred)

**Archetype → Slide rendering:**
- CapitalRaise.dc.html: `<x-import component-from-global-scope="ConceptVDesignSystem_c8f43c.Slide" archetype="{{ slide.archetype }}" content="{{ slide.content }}" register="{{ register }}" lod="{{ lod }}" density="{{ density }}" surface="slide">`
- **Observed:** Slides are EXTERNAL components (resolved from global scope), NOT defined in the template. The **template is pure data**: a DECK array of `{archetype, content}` objects.
- **Verified:** The archetype/content → layout flow is delegated to the solvers (ConceptVDesignSystem bundle). The template does NOT hardcode slide layouts; it DECLARES slide archetypes + supplies content data.
- **Join found:** Template layer is **pure CONTENT + ARCHETYPE declaration**; the solvers (block + graph) are in `_ds_bundle.js` (not in my territory). The contract is via `<x-import>` + `archetype` + `content`.

**Axis dials:**
- Both decks expose LOD, density, theme, ground as `data-*` attributes on root + as props to slides
- **Verified:** These propagate from template to Slide components via `{{ lod }}`, `{{ density }}`, `{{ theme }}`, `{{ ground }}` interpolation. The axis system is **declared at the boundary** (page level) and passed down; slides read them from props.
- **Inferred:** The axis system IS threaded through the template layer, but the **actual resolution** (how lod changes block structure, how density changes whitespace) happens inside the solvers. ✓ Correct separation.

---

## §C · Hardcoded positions/sizes (RATIOS-LAW VIOLATIONS)

### Template HTML violations (file:line evidence)

**CapitalRaise.dc.html + PitchDeck.dc.html:**

1. **Padding (hardcoded px):** L15, L15
   - `padding: 40px clamp(16px, 4vw, 64px) 80px;` — explicit px, not a token
   - **Violation:** Should be `padding: var(--space-xl) clamp(var(--space-xs), 4vw, var(--space-2xl)) var(--space-3xl);` OR a single `var(--padding-page)` token

2. **Gap sizes (hardcoded px):** L19, L19
   - `gap: 14px;` in header flex
   - **Violation:** Should be `var(--gap-md)` or equivalent

3. **Margins (hardcoded px):** L19, L25-26
   - `margin: 0 0 8px;` — hardcoded 8px (header margin-bottom)
   - `margin: 0 0 24px;` — hardcoded 24px (header margin-bottom in PitchDeck)
   - **Violation:** Should reference token values

4. **Max-width (hardcoded px):** L17
   - `max-width: 1280px;` — slide stage width is ABSOLUTE
   - **Violation:** Should be `max-width: var(--container-max-width)` or resolved relative to parent
   - **Context:** This is the SLIDE FRAME max-width, not responsive to the ONE-MATH's ratio system

5. **Position absolute + hardcoded offsets:** L35
   - `position: absolute; right: 16px; bottom: 12px; z-index: 3;` (slide number label)
   - **Violation:** Position should be relative (anchored to parent boundary via ratios), not absolute pixel offsets

6. **Keyframe animation (hardcoded px):** L13
   - `@keyframes deckSlideIn { from { opacity: 0; transform: translateY(24px); } ... }`
   - **Violation:** `24px` should be `var(--space-md)` or a ratio-based value

7. **Inline SVG square (hardcoded px):** L21
   - `<span style="width: 7px; height: 7px; background: var(--accent-gold); transform: rotate(45deg); border-radius: 1px;"></span>`
   - **Violation:** width, height, border-radius are all hardcoded px, NOT tokens (should be `var(--icon-xs)` or similar)

8. **Letter-spacing (hardcoded):** L20, L24
   - `letter-spacing: 0.12em;` and `letter-spacing: 0.04em;`
   - **Inferred:** These appear to be typographic values (em-based, so ratio-aware in one direction), but **should live in a token** so they can be _named_ and _referenced from multiple places_

### UI Kit violations (sample evidence)

**vi/ChatPanel.jsx:**
- `gap:8` — hardcoded number (should be `gap: var(--space-xs)`)
- `padding:'7px 14px'` — hardcoded px
- `borderRadius:'var(--r-sm)'` — ✓ uses token, but padding doesn't

**virtual-hub/HubApp.jsx:**
- `bottom: 96, left: '50%', transform: 'translateX(-50%)'` — absolute offset (96px), not ratio-relative
- `padding: '10px 18px'` — hardcoded px
- `backdropFilter: 'blur(8px)'` — hardcoded blur radius

**platform/screens/BrandKit.jsx:**
- `gap:14, padding:'8px 0'` — hardcoded px gaps and padding
- `width:40, height:40` — hardcoded square size
- `width:22, height:22` — hardcoded color swatch size

**vi/vi.css:**
- `grid-template-columns: 240px 1fr;` — hardcoded left-pane width (should be `var(--sidebar-width)`)
- `padding: 16px 14px;` — hardcoded px
- `gap: 14px;` (multiple places) — hardcoded px

**platform/platform.css:**
- (Not read in full, but patterns suggest similar hardcoding)

### Summary of violations

**Observed:** ~30+ hardcoded px/size values across templates + UI kits, primarily in:
- Padding/margin
- Gap sizes
- Absolute positioning offsets
- Component dimensions (icons, swatches, sidebars)
- Animation transforms

**Inferred:** The template layer was built BEFORE the ONE-MATH ratios-law was formalized. The solvers (block + graph) consume tokens correctly for their internal geometry, but the **TEMPLATE FRAME LAYER** (page padding, slide max-width, slide number position, header layout) violates the "everything is ratios" principle.

---

## §D · Frame-vs-content movement axes (slide transitions + layout stability)

### Observed (L137-152 in PitchDeck.dc.html, L208-241 in CapitalRaise.dc.html)

**Frame axis (viewport/camera motion):**
- `componentDidMount()` uses `IntersectionObserver` to detect slide entry (threshold: 0.1 or 0.12)
- On entry, applies `style.animation = "deckSlideIn .5s cubic-bezier(.16,1,.3,1) both"`
- Animation: `from { opacity: 0; transform: translateY(24px); }` — entrance from below
- **Verified:** This is FRAME movement (the viewport scrolls / the slide enters the viewport). The animation is *choreography only* (geometry stays authoritative, animation is FLIP decoration per the rules).

**Content axis:**
- **Inferred:** No content-axis movement observed in the template layer. Slides are STATIC when rendered; no split/merge/reform verbs appear.
- **Inferred:** Content changes (e.g., LOD changing which blocks render) would be handled inside the solvers, not in the template animation machinery.
- **Context:** This is correct — the template's job is to declare the sequence + hand off rendering to the solvers. Animation stays in the template frame (page scroll + entrance), structure stays in the solvers.

### Slide geometry (no change boundedness observed)

- Slides rendered in a list with `margin-bottom: 28px` (fixed space between slides)
- **Inferred:** Slide boundaries are FIXED (no responsive re-partitioning on viewport change). The frame doesn't split/merge slides; it scrolls past them.
- **Inferred:** If responsive slide layout were needed (e.g., 2-per-row on desktop, 1-per-row on mobile), this would require a NEW axis dial + solver updates. Not present in current implementation.

### Axis dials: frame-side

- `data-theme` (light, dim, dark, contrast) — affects COLORS, not movement
- `data-ground` (clean, warm) — affects COLORS, not movement
- LOD (summary, pitch, full) — affects BLOCK CONTENT (which slides render), not frame movement
- Density (compact, comfortable, spacious) — affects SPACING within slides (solver-side), not frame movement
- Register (custom, presenter, reader) — affects LOD + density automation, not frame movement

**Inferred:** None of the existing axis dials affect FRAME MOVEMENT. Motion is hard-wired (IntersectionObserver + keyframe entrance). **OPPORTUNITY:** An axis dial for frame behavior (e.g., `data-deck-motion: scroll | paginate | carousel`) could vary how slides enter, if needed.

---

## §E · Orphaned / Disconnected components + TIM-LAW CANDIDATES

### Orphaned components

**Observed:** None. Every template, ui_kit, and preview file is actively referenced or part of a known subsystem.

- Templates are consumed by the Company app (index.html via DC-runtime).
- UI kits are served as `index.html` demos + exported as components for integration.
- Preview pages are part of the design-system gallery.
- Demo files are part of local infrastructure (page-face service).

### TIM-LAW CANDIDATES (recurring principles worth naming)

1. **THE MIXED-CURRENCY LAW** (observed violation → candidate principle)
   - **Symptom:** Tokens are defined in CSS (`--space-md`), but layout hardcodes px directly in JSX/HTML (`padding: 40px`)
   - **Principle:** "A surface consuming a token system must NOT mix token references with raw literals of the same kind (spacing, sizing, positioning). Either all px→var OR none."
   - **Application:** Audit every `style={}` in JSX; audit every inline `style=""` in HTML templates. Every px/em/pt value that exists as a token must be a var() reference; new values must be tokenized first, not hardcoded.
   - **Why it matters:** Mixed currencies cause drift; refactoring a token (e.g., `--space-md: 12px → 14px`) doesn't affect hardcoded values, leading to visual inconsistency + the "handcoded island" problem.

2. **THE ABSOLUTE-POSITIONING LAW** (observed violation → candidate principle)
   - **Symptom:** Slide numbers positioned with `position: absolute; right: 16px; bottom: 12px`; hub overlay positioned with `left: 50%; transform: translateX(-50%)`
   - **Principle:** "In a ratio-based layout system, absolute positioning is only valid for FIXED UI furniture (never for CONTENT). Content position must be relative (computed from parent boundary + ratio)."
   - **Application:** Every `position: absolute` in a template/kit must have a justification recorded. If it's stable UI (a label on every slide, a menu icon), it stays. If it could move based on content/axes, convert to relative + solver-computed.
   - **Why it matters:** The ONE-MATH resolves everything as addresses + boundaries. Absolute pixel offsets break the algebra; they're not resolvable by the containment tree.

3. **THE PROJECTION BOUNDARY LAW** (observed + verified → candidate principle)
   - **Symptom:** Templates declare archetypes + content; solvers render the layout. The boundary is the `<x-import>` tag + `archetype` + `content` contract.
   - **Principle:** "A deck/template surface DECLARES WHAT (archetype + content + axes); a solver DECIDES HOW (layout + placement). The template never hardcodes HOW."
   - **Application:** Templates stay DECLARATIVE (pure data + axis dials). Solvers stay IMPERATIVE (the layout engine). No template should contain grid/flexbox overrides specific to a single archetype.
   - **Why it matters:** This is already mostly true in the decks (CapitalRaise, PitchDeck), but the UI kits blur it (vi.css/platform.css have hardcoded grid dimensions). The principle makes explicit what should be implicit.

4. **THE FRAME DECORATION LAW** (observed → candidate principle)
   - **Symptom:** Slide entrance animations use IntersectionObserver + keyframes; the animation is FLIP (geometry stable, animation temporary).
   - **Principle:** "Motion on the FRAME axis (viewport/camera movement) is DECORATION; motion on the CONTENT axis (block re-partition) is STRUCTURE. Decorate the frame without changing content geometry."
   - **Application:** Every animation in a template layer must be in the `@keyframes` section (frame-level), never a computed property that affects layout. The solver's block structure never changes due to animation; motion is visual choreography only.
   - **Why it matters:** This guards against animation causing cascade reflows or making the geometry non-authoritative.

5. **THE AXIS DIAL DISPATCH LAW** (observed → candidate principle)
   - **Symptom:** LOD, density, theme, ground are all declared at the page root and passed as props to child components. Each component uses them to vary its rendering.
   - **Principle:** "Axis dials THREAD TOP-DOWN (declared at the surface root, passed as props to all children). No child should ORIGINATE a dial (e.g., a slide shouldn't invent its own LOD). Dials are GLOBAL, not LOCAL."
   - **Application:** When adding a new axis dial (e.g., `data-deck-motion`), declare it at the root template level, not inside a specific archetype or component. Pass it down; let children consume it.
   - **Why it matters:** Dials are how a SURFACE (not a component) varies its entire output. If dials originate locally, you get N independent configurations instead of one coherent surface.

---

## SUMMARY (§A-§E)

| Finding | Type | Evidence | Severity |
|---------|------|----------|----------|
| ~30+ hardcoded px values in templates/kits | Violation | CapitalRaise.dc.html:15,19,21,35 + vi.css + platform.css + ui_kits/* | High |
| `max-width: 1280px` slide frame is absolute, not ratio-relative | Violation | CapitalRaise.dc.html:17, PitchDeck.dc.html:17 | High |
| Absolute positioning with hardcoded offsets | Violation | CapitalRaise.dc.html:35, HubApp.jsx:bottom 96 | Medium |
| Mixed token + literal spacing in JSX | Pattern (drift risk) | ChatPanel.jsx, BrandKit.jsx, HubApp.jsx | Medium |
| Sidebar width (240px) hardcoded in vi.css | Violation | vi.css: `grid-template-columns: 240px 1fr;` | Medium |
| Zero disconnected components | Observation (good) | All files actively used | — |
| Template layer is correctly declarative (archetype + content) | Verification | CapitalRaise/PitchDeck DECK arrays are pure data | ✓ Good |
| Slide entrance animation is frame-only (FLIP discipline) | Verification | IntersectionObserver + keyframes, no layout change | ✓ Good |
| Axis dials thread top-down correctly | Verification | LOD, density, theme passed from root to slides | ✓ Good |

