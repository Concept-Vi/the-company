# AREA: surface/ — The Operator Surface (Instrument)

**Extractor:** Sonnet 4.6 subagent  
**Date:** 2026-06-21  
**Scope:** `/home/tim/company/surface/` — the full React+Vite operator instrument: authored src/, synced gallery JS/CSS, DNA JSON, config, scripts.

---

## 1. PURPOSE

The `surface/` area is the **operator-facing instrument** — the visual interface Tim (or any operator) uses to perceive and interact with the Company's living fabric. It is a React 18 + Vite (TypeScript) app at port **5174** that proxies `/api` to port 8770 (the bridge). It is NOT the canvas (5173) and NOT a developer tool — it is the singular instrument through which an operator navigates, explores, annotates, and directs the Company's self-growing corpus.

Core identity: **"Project: Instrument"** (index.html `<title>`). The operator surface never shows machine IDs, addresses, raw file paths, or code names to the operator — every surface translates ALL technical names → human meaning (operator-law).

---

## 2. MAJOR SUB-AREAS

### 2.1 Entry Points & Config
- `surface/app/index.html` — entry HTML; loads DNA gallery scripts as classic `<script>` tags (BEFORE the deferred React module)
- `surface/app/vite.config.ts` — port 5174, allowedHosts for Tailscale `.tail777bc2.ts.net`, `/api` proxy to `:8770`
- `surface/app/package.json` — name: "instrument-surface"; predev/prebuild: sync-gallery; deps: framer-motion ^12.4.0
- `surface/app/src/main.tsx` — mounts `<App />` in StrictMode; imports paper.css, surface.css, rhm.css

### 2.2 App Core
- `surface/app/src/App.tsx` (563 lines) — the orchestrator; defines all types, all state, all store wiring; the root render tree

### 2.3 Layouts (three form factors)
- `src/layouts/Desktop.tsx` — 1024+px; 3-col grid (264px left strata, 1fr center, 320px right strata)
- `src/layouts/Portrait.tsx` — tall/narrow; flex column; bottom sheet disclosure
- `src/layouts/Landscape.tsx` — wide-short; rail on right (30%); center (70%)
- `src/layouts/shared.tsx` — WheelOrState, SelectHint (shared across all three)

### 2.4 Faces (overlay modals / mounted surfaces)
- `src/gallery/GalleryMount.tsx` — DNA decision/gallery card host (always-in-DOM, visibility toggled)
- `src/sessions/SessionDrill.tsx` — session list → drill (FACE-1 depth)
- `src/channels/ChannelView.tsx` — fabric graph (FACE-1 breadth #1)
- `src/decisions/DecisionsInbox.tsx` — operator decision queue
- `src/decisions/DecisionsBar.tsx` — count chip (entry to inbox)
- `src/tools/ToolsBar.tsx` — fixed bottom-left pill; glyph ⛭
- `src/tools/ToolsPanel.tsx` — tool list → detail (SchemaForm + run)
- `src/rhm/RightHand.tsx` (753 lines) — the Right-Hand Man overlay; draggable V handle; 6 verbs fan layout

### 2.5 Source Panel
- `src/source/SourcePanel.tsx` — V's "open-source" verb result; fuller record behind a tapped dot

### 2.6 Wheel Views (the center)
- `src/wheel/Wheel.tsx` — semantic polar wheel (sectors, rings, edges, point cloud)
- `src/wheel/Grid.tsx` — structure/square view (dyadic nested grid)
- `src/wheel/Separator.tsx` — GROUP 9 two-gravity separator form (two basins: pole A/B)
- `src/wheel/Nucleation.tsx` — type-nucleation view (type system as angular divisions)
- `src/wheel/Tether.tsx` — rAF selection tether (SVG arc from selected dot to card)
- `src/wheel/Disclosure.tsx` — selected point detail card (variants: panel / sheet / rail)
- `src/wheel/useSize.ts` — ResizeObserver hook; shared by Wheel and Separator

### 2.7 Toggle Controls (chips and controls)
- `src/toggles/LensChip.tsx` — lens switcher dropdown (current lens + live count)
- `src/toggles/Lens.tsx` — pill-row lens switcher (compact form)
- `src/toggles/SpaceChip.tsx` — embedded item-space selector (from /api/layers)
- `src/toggles/LayerChip.tsx` — embedder layer selector (from /api/layers)
- `src/toggles/ResChip.tsx` — MRL resolution picker (dim=N from /api/layer-dims; powers of 2)
- `src/toggles/QuantChip.tsx` — representation picker (full float vs binary/coarse)
- `src/toggles/CentreChip.tsx` — active relative centre indicator + reset
- `src/toggles/LiveDot.tsx` — live/freeze toggle for the EventSource stream
- `src/toggles/Scrubber.tsx` — time scrubber (range [corpusStart, now]; G3)
- `src/toggles/RungLadder.tsx` — multi-scale rung ladder (units → themes; G11)
- `src/toggles/ViewToggle.tsx` — three view modes: both / circle / square
- `src/toggles/Legend.tsx` — always-present orientation card (title + 2-3 explanation lines)
- `src/toggles/Notice.tsx` — animated fail-loud notice (never a silent swallow)
- `src/toggles/Settings.tsx` — gear affordance → Taste panel
- `src/toggles/Taste.tsx` — typeface / pigment / motion taste scaffold (S4)
- `src/toggles/useChipMenu.ts` — shared chip menu state + viewport collision detection

### 2.8 Stores (subscribe pattern)
- `src/decisions/decisionsStore.ts` — decision queue; /api/decisions + /api/territory enrichment
- `src/sessions/sessionDrillStore.ts` — session list + lens ops; /api/sessions + /api/session-recall
- `src/channels/channelStore.ts` — fabric channels; /api/channels (GAP: ensureStarted empty)
- `src/tools/toolsStore.ts` — tools list; /api/tools with CORPUS_SEED fallback

### 2.9 Library (lib/)
- `src/lib/api.ts` — all types (ProjPoint, Projection, Territory, etc.) + fetch helpers
- `src/lib/address.ts` — ui:// address system; Locus store; installAddressCapture; installPointerBridge; resolveUiTarget
- `src/lib/pointables.ts` — CATALOG of 10 curated pointables; installPointables(); window.surfacePointables()
- `src/lib/resolveAllocation.ts` — MODAL_INVARIANT; POST /api/resolve → CSS modal geometry vars
- `src/lib/seed.ts` — geometry math: wheelGeom, placePolar, ringRadii, sectorHue, chordPath, wedgePath, gridCellCenter, dyadicLevels
- `src/lib/verifyMode.ts` — isVerifyMode() (URL ?verify param)

### 2.10 Tokens
- `src/tokens/paper.css` — Fresh Paper design language: ground/ink/pigment/elevation/type/spacing/radii; taste toggle [data-type]/[data-pigment]
- `src/tokens/motion.ts` — single motion system: SPRING_GENTLE, SPRING_SNAPPY, EASE_OUT, DUR; transition() function; fadeRise variants

### 2.11 CSS Sub-component files
- `src/surface.css` (691 lines) — all layout+component CSS; token-only (no literal hex/px)
- `src/rhm/rhm.css` — V handle, fan, aim caption, greeting, brain panel, note composer
- `src/sessions/sessions.css` — sessions overlay modal frame
- `src/channels/channels.css` — channels overlay modal frame (wider: 760px max-width; full-width centered graph)
- `src/source/source.css` — source panel; bottom-right anchored on wide, bottom sheet on narrow

### 2.12 Public Gallery (synced — DNA + fabric hooks, read-only copies)
- `public/gallery/surface.js` (512 lines) — DNA shared runtime: color math, warmth dial→surfaces, injectVars, DNA.esc; MUST load FIRST
- `public/gallery/organisms.js` (783 lines) — DNA organism generators: icon, iconStrip, mesh, hubNetwork, consequencesBox, cascade, detailStrip
- `public/gallery/unit-view.js` (453 lines) — DNA.renderUnit: normalised unit → phone-look screen DOM
- `public/gallery/archetype.js` (516 lines) — DNA.renderArchetype: THE ONE generic renderer; takes archetype (from layouts.json) + data record → screen element
- `public/gallery/face-adapters.js` (62 lines) — DNA.faceRecord.sessionRecord + DNA.faceRecord.channelGraph adapters
- `public/gallery/phone.css` — DNA look file (token-based — depends on dna-tokens.css)
- `public/gallery/dna-tokens.css` — GENERATED by sync-gallery from piece.css; ONLY :root token blocks (no dangerous globals)
- `public/gallery/fork-brain-core.js` (186 lines) — THE ONE brain-turn engine: /api/claude/turn NDJSON stream, per-address session continuity, /api/territory/write route-back; _stripMd; window.forkBrainCore
- `public/gallery/fork-v-brain.js` (96 lines) — every-page V/RHM brain mount; attach({panelEl, getAimAddress, getAimLabel}) → {ask, direct, aimChanged, destroy}
- `public/gallery/fork-gallery-brain-hooks.js` (111 lines) — per-unit gallery brain hooks; HOOK 1: gallery:rendered → bindBrain; HOOK 2: gallery:direction → route-back; HOOK 1b: decision:rendered → in-card Ask
- `public/gallery/wildcard-gallery-binder.js` (214 lines) — portable interaction binder; gallery:rendered → direction-targets keyed by ADDRESS; emits gallery:verb{verb:'annotate'} + legacy gallery:direction; decide() for decision_take

### 2.13 Public DNA (synced — from counterpart/design/dna/)
- `public/dna/layouts.json` — archetype definitions (renderArchetype fills from this)
- `public/dna/tokens.json` — colour/warmth token set; DNA.injectVars self-fetches this
- `public/dna/grammar.json` — space/bond/scale grammar; DNA.injectSpace self-fetches this

### 2.14 Scripts
- `scripts/sync-gallery.mjs` — predev/prebuild: copy DNA modules from counterpart/design repo + fabric hooks from build-prep/front-interface/; FAIL LOUD if any missing; extracts :root token blocks from piece.css → dna-tokens.css
- `scripts/prove-decision-harness.js` — browser-console harness; proveDecision(addr, {decide?}); tests 5 legs: resolve, host-open, in-card-ask, take-flips-state, rerender-refresh

---

## 3. PER-FILE INVENTORY

### App.tsx — The Orchestrator
**Role:** Single shared state + root render; drives all other components.

**Types defined:**
- `FormFactor`: `'desktop' | 'portrait' | 'landscape'`; classify() with useFormFactor() hook; body.dataset.ff
- `ViewMode`: `'both' | 'circle' | 'square'`
- `Centre`: `{ ref: string; label: string }`
- `NucParams`: `{ types_space: string; space: string; rung: number }`
- `SurfaceState`: ~30 fields — proj, error, loading, binding, emb, space, dim, quant, selected, galleryOpen, drillAddress, feel, view, nuc, centre, poles, live, at, corpusStart, now, rung, notice, dismissNotice

**Key behaviors:**
- `binding` persisted to `localStorage('projection.lens')`; validated against proj.bindings
- `setSpace` resets centre/selected/poles (cross-space contamination prevention)
- `live stream`: EventSource `/api/stream?since=lastSeqRef.current`; 2500ms throttle; pauses when `at` (time scrub) or `!live`
- `corpusStart`: one-shot EventSource `/api/stream?since=-1` to get earliest timestamp
- `projection:select` dispatch: fires on selected unit change; detail = `{address, source, record, seq, kind, space, kind_name, kind_meaning, summary}` or null
- `gallery:verb` handler: navigate → focusCentre; open-source → fetchTerritory + SourcePanel; drive/generate → Notice; annotate + is_decision_take → writeDirections via forkBrainCore.writeDirections or POST /api/territory/write (suppressed in verify mode)
- resolveAndApplyModal() called on mount + resize → /api/resolve → CSS vars

**Root render tree:**
```
<layout> + <GalleryMount> + <DecisionsInbox> + <SessionDrill> + <ChannelView> + <ToolsBar> + <ToolsPanel> + <RightHand> + <SourcePanel>
```

---

### GalleryMount.tsx — DNA Decision Card Host
**Role:** Always-in-DOM overlay; hosts DNA-rendered gallery/decision cards; never React-unmounted (keeps DNA's container refs stable).

**Events listened:**
- `gallery:rendered` — persists subtype/render_kind on refs; dispatches `decision:ready {address}`
- `decision:rendered` — opens gallery overlay; stores currentAddr/subtype/render_kind
- `gallery:rerender` — re-emits renderGallery with current refs
- `projection:select` — if no decisionMode, deselects wheel
- `keydown` Escape — dismiss
- `decision:open {address, id, fromInbox?}` — opens a specific decision card

**Events dispatched:**
- `decision:ready {address}` — after card renders

**API called:**
- DNA: window.DNA.renderGallery; polls #gallery-mount every 250ms up to 80 tries (~20s)

**Key mechanisms:**
- `decisionModeRef` — prevents wheel-deselect from killing a decision walk
- `fromInboxRef` — if true, dismiss() re-opens DecisionsInbox (work-the-queue)
- `openDecision()` — clears container, polls for DNA, renders via window.DNA.renderGallery
- Deep-link: reads `?decide=` from URL
- Module-level `bound` guard (StrictMode safe)

---

### RightHand.tsx — The Right-Hand Man
**Role:** Persistent draggable V handle (bottom-right); 6-verb fan layout; brain panel; note composer; guided tour; first-contact greeting.

**VERBS (6):**
- `navigate` — dispatches `gallery:verb{verb:'navigate'}`; live=true
- `open-source` — dispatches `gallery:verb{verb:'open-source'}`; live=true  
- `ask` — opens panelOpen (brain panel); live=true
- `annotate` — opens noteOpen (note composer); live=true
- `drive` — dispatches `gallery:verb{verb:'drive'}`; live=false (soon)
- `generate` — dispatches `gallery:verb{verb:'generate'}`; live=false (soon)

**Events listened:**
- `projection:select` — aim update (from wheel point selection)
- `projection:aim` — sector aim (from wheel sector click)
- `gallery:write-error` — note error

**Events dispatched (via gallery:verb):**
- `gallery:verb {verb: 'navigate' | 'open-source' | 'drive' | 'generate', aim_address, ...}`

**API called:**
- `/api/territory/write` — note save (POST via brain.direct or direct POST)
- `/api/claude/turn` — via forkVBrain.attach (brain panel)

**Key mechanisms:**
- `surfaceAimRef`: `ui://instrument/surface#binding=<id>` — the default aim
- `brain`: `window.forkVBrain.attach({panelEl, getAimAddress, getAimLabel, placeholder})`
- `saveNote()`: brain.direct({type:'comment', text}) → /api/territory/write; auto-close after 1100ms
- Drag: pointerCapture; persisted to `localStorage('rhm.handle.pos')`
- Greeting: one-time first-contact; `localStorage('rhm.greeted')`; "Show me around" starts guided tour
- Guided tour: runTourStep(0→2); STARTERS = ['What am I looking at?', 'What can I do here?', 'Where can I go from here?']
- aimAvailable=false: Note/Ask show honest "can't act on this kind yet" card
- Fan layout: cumulative y with dx lean (arc around corner angle)

**Stamps:**
`ui://rhm/handle`, `ui://rhm/brain`, `ui://rhm/note`, `ui://rhm/greet`

---

### Wheel.tsx — Semantic Polar Wheel
**Role:** The main visualization for semantic/activity lenses; polar coordinate point cloud with sectors, rings, edges.

**Events dispatched:**
- `projection:aim {address, label, meaning}` — on sector click (NOT projection:select)
- `projection:select {address, ...}` — on point click (via parent onPick callback → App.tsx)

**Key mechanisms:**
- SVG layers (back to front): grid, rings, coincidence spine, sector wedges, GROUP10 edges, strain spokes, centre dot, AnimatePresence point cloud, theme labels (≤12), hit layer, custom centre marker
- G10 readout: tapped sector name + in/out counts + finding (pure source/sink)
- G11: RungLadder when scale.rungs present; theme names shown when count ≤ 12
- `pointAddress(p)`: uses p.address if ui://, else mints `ui://canvas/seq-${p.seq}`
- uses `useSize` for measured container

---

### Disclosure.tsx — Selected Point Detail Card
**Role:** The "what is this thing" detail card for the selected point; three layout variants.

**Variants:** `'panel' | 'sheet' | 'rail'` (different entrance animations)

**API called:**
- `/api/context?address=<addr>` — contextAt(addr); shows up to 6 items

**Key mechanisms:**
- `placement()` — derives "why it's here" from binding.radius_from (semantic/separator/nucleation/address/default)
- `humanizeCtx(s)` — strips ui:// addresses, hash@path tails, bare abs paths, routine:name machine IDs — operator-law render boundary
- Footer: pole-set buttons (separator lens only), "⊙ centre here" focus button
- Always AnimatePresence — entrance/exit mirror
- `data-tether-card` attribute — enables the Tether SVG arc

---

### Tether.tsx — Selection Tether
**Role:** Pure-presentation rAF loop drawing a bowed SVG arc from selected dot to detail card. Zero React re-renders per frame.

**Mechanism:**
- Finds `[data-tether-point]` (set on selected dot in Wheel/Separator/Nucleation/Grid) and `[data-tether-card]` (set on Disclosure)
- Measures both in client coords; starts at dot's EDGE (≈ selected radius 7px), ends at card's nearest border point
- BOWS arc radially outward from the wheel center (avoids reading as a spoke); fallback: perpendicular to chord
- Only shows when dot-to-card distance > 18px
- `pointer-events: none` — never blocks a click

---

### Separator.tsx — Two-Gravity Separator Form
**Role:** GROUP 9 separator lens visualization; two basins (pole A/B); diverging balance bar.

**Props:** `proj, feel, selectedSeq, onPick, polesDriven?, onClearPoles?`

**Key mechanisms:**
- `place(p)`: basin coordinate based on p.pole ('a'=left, 'b'=right) × p.r × halfW
- Balance bar geometry: (la/tot)*barW left, (lb/tot)*barW right
- Pole labels: `polesDriven ? leaf(poleA.label) : poleA.label` — leaf = last path segment
- Fifth-gate verdict: `.sep-verdict--yes/--no` — "separates" / "does not separate"
- Stamp: `ui://instrument/separator`

---

### Nucleation.tsx — Type Nucleation View
**Role:** Type system as angular divisions; membership boundary; candidate new type blooms (✦).

**Props:** `proj, feel, selectedSeq, onPick, nuc, setNuc`

**Key mechanisms:**
- `clusterTheta`: mean θ per pile cluster (places born bloom at pile's TRUE angle)
- Three point readings: inside (fits type, angle-hue), pile/strain (candidate new type), tail (residue → corner)
- `cornerPlace(theta, fit, cx, cy, R, seed)`: deterministic hash-jitter corner placement for residue
- Birth dial: `birthMass = max(3, round(dial * pileClustered))` — client-side, no refetch
- Candidate blooms: dashed ochre ring (forming) vs filled green disc + ✦ (born)
- Pickers: items space / types space / rung — drive engine (registry-true)
- Stamps: `ui://instrument/nucleation`, `ui://instrument/type/<id>`, `ui://instrument/candidate/<k>`, `ui://instrument/residue`

---

### Grid.tsx — Structure/Square View
**Role:** Dyadic nested grid visualization for the `view='square'` mode.

**Key mechanisms:**
- Points placed by `gridCellCenter(cell.i, cell.j, 2^cell.d, cx, cy, R, seq)` with 4px clamp inside box
- Same AnimatePresence + hit-layer pattern as Wheel
- Dyadic nested boxes, circles, axes, coincidence points

---

### Stores (all use subscribe pattern)

**decisionsStore.ts:**
- `StackItem`: id, address, type, name, state, recommended_label, meaning, reversibility, subtype, owner
- `isTimFacing(d)`: `d.owner === 'tim'` — REGISTRY-TRUE filter; never hardcoded subtype-set
- `enrich()`: Promise.allSettled per item → /api/territory; merge-by-id (no seq-abort to avoid flickering)
- `ensureStarted()`: kicks loadDecisions() once + wires `gallery:rerender → loadDecisions()` at STORE level (avoids N reloads per event)
- `error` = cold-load failure; `refreshError` = refresh failed with existing list (soft flag, never contradicts visible cards)
- GAP: only 'decision-sequence' type is landed; A4 widens the type union via the seam already in the render

**sessionDrillStore.ts:**
- `LENS_ROUTE`: `/api/session-recall?session=<id>&op=<op>` — filled seam; goes live on checkpoint bounce
- `loadLens()`: concurrent fetch of catch_up + open_loops + directives with 4000ms timeout each
- Ops: 'catch_up', 'open_loops', 'directives'

**channelStore.ts:**
- GAP: `ensureStarted()` is EMPTY — channels NEVER auto-load; only loaded when `openChannels()` called. This means if nothing triggers openChannels(), channels never load even if a subscriber exists.
- Members shape: `/api/channels` serves `members` as an OBJECT `{<uuid>:{participation,added}}`; DNA's channelGraph expects ARRAY — normalized at ChannelView call site (flagged to DNA, code-grounded)

**toolsStore.ts:**
- `CORPUS_SEED`: hardcoded "prove-on-one" corpus tool; used when /api/tools fails; scaffold=true flag (honest)
- `applyFormMeta(d)`: maps fork's snake_case form_meta → ToolDescriptor; infers opField from matching enum keys
- `resolveEnumSources(tool)`: fetches each enumSource URL with 1500ms timeout; converts to enum; degrade-clean
- GAP 4: ToolsPanel holds result for DNA tool-card (pending); shows human count status, never raw JSON

---

### Library Files

**api.ts:**
- Types: `ProjPoint` (30+ fields), `Sector`, `Edge`, `BindingRef`, `Projection`, `ContextBundle`, `Territory`
- `ApiError` class; `getJSON<T>()` generic fetcher with typed error
- `fetchProjection(params)`, `fetchContext(address)`, `fetchTerritory(address)`, `fetchLayers()`, `fetchLayerDims()`

**address.ts:**
- `parseUiAddress()`, `isUiAddress()`, `stamp()` (returns data-ui-ref props for React)
- `Locus store`: `{ address, notice }` with subscribe/setLocus
- `indicate(addr)`: removes old `.ui-indicated`, adds new one
- `resolveUiTarget(addr, opts?)`: single sink; `transient=true` for V-pointing; `transient=false` for clicks (persists)
- `installAddressCapture()`: capture-phase click listener on document
- `installPointerBridge()`: listens to `ui:point` CustomEvent → resolveUiTarget with transient=true
- `clearNotice()`, `contextAt(addr)`

**pointables.ts:**
- `CATALOG`: 10 curated pointables — lens, space, layer, resolution, representation, view, centre, time, live, legend
- `installPointables()`: exposes `window.surfacePointables()` = curated (DOM-filtered) + auto-discovered [data-ui-ref][data-point-label]
- Tokens are OPAQUE (`auto-N`), never the ui:// address (operator-law)

**resolveAllocation.ts:**
- `MODAL_INVARIANT`: pad_top (clamp), pad_x (select by orient), frame_max_h (sub)
- `resolveAndApplyModal()`: POSTs to `/api/resolve`; sets `--res-modal-pad-top`, `--res-modal-pad-x`, `--res-modal-frame-max-h` on :root; degrade-clean on failure

**seed.ts:**
- `TAU`, `R_MIN=0.06`, `R_MAX=1.0`, `WHEEL_FRAC=0.46`
- `wheelGeom(w,h)`: cx=w/2, cy=h/2, R=min(w,h)*0.35
- `placePolar(theta,r,cx,cy,R)`: -90deg rotation (theta=0 at north)
- `ringRadii(rings,R)`, `sectorHue(i,n)`, `chordPath()`, `arrowHead()`, `wedgePath()`
- `gridCellCenter(i,j,m,cx,cy,R,jitterSeed)`: deterministic hash jitter
- `dyadicLevels(m)`: coarsest→finest with opacity weights

**verifyMode.ts:**
- `isVerifyMode()`: checks URL `?verify` param; returns false in non-browser env
- Used to suppress decision_take writes; shows persistent `.verify-banner`

---

### Toggle Controls

**LensChip.tsx:**
- Resting: short label (derived from registry label, never hardcoded) + live count
- Menu on demand: all binding labels; closes on pick
- Viewport collision detection via useChipMenu
- Stamps: `ui://controls/lens`, `ui://controls/lens/current`, `ui://controls/lens/<id>`

**SpaceChip.tsx:**
- Registry-true: reads spaces from /api/layers (Object.keys)
- Hidden for by_nucleation lens (which has its own nuc pickers)
- Hidden when `!proj.binding.space` (non-vector lenses have no space axis)
- Stamps: `ui://controls/space`

**LayerChip.tsx:**
- Hidden when only one layer (no choice)
- Reads from /api/layers → union across all spaces
- `DEFAULT = 'default'` (emb=null); a named layer → ?emb=<name>
- Stamps: `ui://controls/layer`

**ResChip.tsx:**
- MRL ladder: powers of 2 strictly below full dim, down to 64
- Registry-true: derived from `/api/layer-dims` for current space+emb
- Hidden when `!full || options.length <= 1`
- Stamps: `ui://controls/resolution`

**QuantChip.tsx:**
- Two options: full (float), binary ('coarse' label — honest: geometry not speed)
- Hidden when `!proj.binding.space` (non-vector lenses)
- HONEST PERF NOTE in source: binary is a coarser GEOMETRY, not a speed win — "Coarse" label, not "Quick"
- Stamps: `ui://controls/representation`

**CentreChip.tsx:**
- Absent when centre is null
- Whole chip resets centre → "show all ×"
- AnimatePresence enter/exit
- Stamps: `ui://controls/centre`

**LiveDot.tsx:**
- Pulsing dot when live; static when frozen
- Tap = toggle live/frozen
- Stamps: `ui://controls/live`

**Scrubber.tsx:**
- Range [corpusStart, now]; fraction-based (avoids epoch arithmetic per drag)
- Snap to live when f ≥ 0.999 → setAt(null)
- Stamps: `ui://controls/scrubber`

**RungLadder.tsx:**
- Shows only when `proj.scale.rungs` present
- `units` = rung=null; buttons for each rung (sorted desc)
- Stamps: `ui://controls/rung`

**ViewToggle.tsx:**
- Three modes: both (circle in square) / circle / square — inline SVGs for disambiguation
- Stamps: `ui://controls/view`, `ui://controls/view/both|circle|square`

**Legend.tsx:**
- Always present when proj loaded; collapsible (persisted to `localStorage('instrument.legend.collapsed')`)
- Smart bypass: static meta ONLY when not re-centred AND not time-scrubbed; else computed describe()
- Seven lens-aware cases in describe(): square, nucleation, separator, semantic-coarse, semantic-uncentred, semantic-centred, edges/default
- In Both+wheel lenses: adds "◆ on the axes · where grid & circle meet — the ratified spine"

**Notice.tsx:**
- AnimatePresence enter/exit (y: -12 → 0)
- role="status" for a11y
- `×` dismiss button

**Settings.tsx:**
- Single gear ⚙ → Taste panel (on demand, not permanently on surface)
- Viewport-anchored panel (not gear-anchored — prevents left overflow on phone)
- Uses Taste component inside

**Taste.tsx:**
- Three toggle rows: Aa (typeface: source/crimson/lora), ◑ (pigment: muted/soft/present), ↝ (motion: spring/eased)
- Applies via `document.documentElement.setAttribute('data-type', id)` etc.
- Stamps: `ui://controls/taste`

**useChipMenu.ts:**
- Shared state: open, menuClass, wrapRef, toggle, close
- Collision detection: `lenschip-menu--right` when chip.left + menuW > window.innerWidth - 8

---

### Gallery JS Modules

**surface.js (DNA shared runtime):**
- `DNA.color`: hex math (hexToRgb, rgbToHex, lerpHex, isHex, normHex)
- `DNA.surfaces(tokens, warmth, polarity)`: warmth dial → 4 page surfaces; polarity 'dark' → invertL
- `DNA.injectVars(target, tokens, warmth, polarity)`: writes full CSS var set onto a document root
- `DNA.api`: feedback/tokens/grammar persistence (:8090 API)
- `DNA.esc`: HTML escape
- CRITICAL: MUST load FIRST in index.html (does a hard `global.DNA = {…}` overwrite)

**organisms.js (DNA furniture):**
- `DNA.org.icon(name, size)`: 24-grid, stroke 1.5 icons (house/ledger/plan/chat/calendar/crane/scale/compass/chart/plug)
- `DNA.org.iconStrip(names, opts)`: icons on dashed rail
- `DNA.org.mesh(w, h, opts)`: ambient network (seeded, deterministic)
- `DNA.org.hubNetwork(opts)`: typed hub + spokes; opts: {nodes, hub:'octagon', weighted, organic, direction, w, h}
- `DNA.org.consequencesBox(title, stats, opts)`: controlled density panel
- `DNA.org.cascade(stages, opts)`: time spine
- `DNA.org.detailStrip(entries)`: tiny-entry texture run
- All return SVG/HTML STRING coloured with CSS vars

**unit-view.js (DNA.renderUnit):**
- Normalised unit → immersive phone-look screen DOM
- Input: `{super, title, prose, mark?, action?, meta?, neighbours?, stats?, sockets?, cardLines?}`
- Thin data reads as intentional immersive space (not a text-wall + void)
- Uses `DNA.org.hubNetwork` for the constellation field

**archetype.js (DNA.renderArchetype):**
- THE ONE generic renderer for ALL archetypes (decision cards, session cards, channel-view, etc.)
- `DNA.renderArchetype(archetype, record, opts)` → a screen element
- Slot resolution: `slot_map` (slot id → dotted path or 'resolve:<x>') or slot.id; pick() traverses dotted path
- Slot types: heading (question/anchor), label (what-kind/state), lead (explanation voice card), shape (opts.visualDevice)
- Self-contained VI_MARK SVG (no dependency on unit-view.js for the V glyph)
- Length-aware question rendering: L>180 → dc-q-lead (calm prose), L>90 → dc-q-md, else crisp hero
- "Why" line rendered ONLY when distinct from explanation (prevents verbatim repetition)

**face-adapters.js (DNA.faceRecord):**
- `DNA.faceRecord.sessionRecord(raw)`: raw /api/sessions row → session-card record shape
- `DNA.faceRecord.channelGraph(rawChannels)`: raw /api/channels array → {identity, nodes, edges, hub}
- Normalizes members object→array internally here (in addition to the host-side normalization in ChannelView)

**fork-brain-core.js (window.forkBrainCore):**
- `core.talk(replyEl, address, prompt, opts)`: POST /api/claude/turn; stream NDJSON {init|text|tool|done|error}; per-address session continuity (_sessions map)
- `_stripMd(t)`: strips markdown syntax at display layer (asterisks, code, headers, bullets)
- Pointables: reads `window.surfacePointables()` at send-time; sends {token,label} ONLY (no addresses); maps token→address for `ui:point` dispatch
- `core.writeDirections(batch, address, opts)`: POST /api/territory/write with batched directions
- Wait state: "Looking…" text + `.brain-loading` class toggle

**fork-v-brain.js (window.forkVBrain):**
- `forkVBrain.attach({panelEl, getAimAddress, getAimLabel?, placeholder?})` → `{ask, direct, aimChanged, destroy}`
- Builds `.v-brain` DOM inside panel (idempotent); aimEl/replyEl/inputEl/sendEl
- `ask(prompt)`: reads live aim address; per-aim session continuity via core._sessions
- `direct(item)`: routes direction back at current aim → core.writeDirections → /api/territory/write
- Aim label shown in panel ("Ask about: <label>"); never the raw address

**fork-gallery-brain-hooks.js:**
- HOOK 1: `gallery:rendered` → `bindBrain(rootEl, sourceAddr)`: adds "Ask about this" button; lazy panel creation on first click
- HOOK 1b: `decision:rendered` → in-card Ask for decision overlays
- HOOK 2: `gallery:direction` → group by element_id → core.writeDirections route-back

**wildcard-gallery-binder.js (window.galleryBinder):**
- REACTIONS vocab: `['good', 'wrong', 'explain', 'remember_this', 'do_this']`
- CONTENT_COMMENT_TYPES: `['note', 'direction', 'correction', 'question', 'praise', 'discuss']`
- `emitVerb(verb, aim_address, payload)` → `window.dispatchEvent(CustomEvent('gallery:verb', ...))`
- `emitDirection(item)` → gallery:verb{verb:'annotate'} + legacy gallery:direction transition alias
- `decide(addr, optionLabel)` → validates canonical form (decision://<frame>/<id>) → emits gallery:verb{verb:'annotate', payload:{mark_type:'decision_take', value, is_decision_take:true}}; FAILS LOUD on non-canonical address

---

## 4. EVENT WIRING MAP

### Events DISPATCHED by surface (window-level CustomEvents)

| Event | Dispatched by | Detail shape |
|-------|--------------|--------------|
| `projection:select` | App.tsx (on point pick) | `{address, source, record, seq, kind, space, kind_name, kind_meaning, summary}` or null |
| `projection:aim` | Wheel.tsx (sector click) | `{address, label, meaning}` |
| `decision:ready` | GalleryMount.tsx | `{address}` |
| `gallery:verb` | wildcard-gallery-binder.js, RightHand.tsx (navigate/open-source/drive/generate) | `{verb, aim_address, payload}` |
| `gallery:direction` | wildcard-gallery-binder.js (legacy alias) | item shape |
| `ui:point` | fork-brain-core.js (from brain token→address map) | — |

### Events LISTENED by surface components

| Event | Listened by | Action |
|-------|------------|--------|
| `gallery:rendered` | GalleryMount.tsx, fork-gallery-brain-hooks.js | cache subtype/render_kind; dispatch decision:ready; bind brain |
| `decision:rendered` | GalleryMount.tsx, fork-gallery-brain-hooks.js | open gallery overlay; in-card Ask |
| `gallery:rerender` | GalleryMount.tsx, decisionsStore.ts | re-render current card; reload decisions |
| `projection:select` | GalleryMount.tsx, RightHand.tsx | deselect wheel (if no decisionMode); update aim |
| `projection:aim` | RightHand.tsx | update aim (sector) |
| `decision:open {address, id, fromInbox?}` | GalleryMount.tsx | open specific decision card |
| `channels:open` | ChannelView.tsx | open channels overlay |
| `sessions:open` | SessionDrill.tsx | open sessions overlay |
| `gallery:write-error` | RightHand.tsx | show note error |
| `keydown` (Escape) | GalleryMount.tsx, SessionDrill.tsx, ChannelView.tsx, ToolsPanel.tsx | close overlay |
| `ui:point` | lib/address.ts (installPointerBridge) | resolveUiTarget with transient=true |

---

## 5. /API ENDPOINT MAP

| Endpoint | Called by | Purpose |
|----------|-----------|---------|
| `GET /api/stream?since=<seq>` | App.tsx | EventSource live projection updates (throttled 2500ms) |
| `GET /api/stream?since=-1` | App.tsx | One-shot corpusStart discovery |
| `POST /api/projection` | App.tsx (fetchProjection) | Fetch full projection data |
| `GET /api/context?address=<addr>` | Disclosure.tsx (contextAt) | Context items for selected point |
| `GET /api/territory?address=<addr>` | decisionsStore.ts (enrich), SourcePanel.tsx, prove-decision-harness.js | Territory record for a thing |
| `POST /api/territory/write` | App.tsx (writeDirections), RightHand.tsx (saveNote), fork-brain-core.js | Write directions/notes/decision takes |
| `GET /api/decisions` | decisionsStore.ts | Pending decision queue |
| `GET /api/sessions` | sessionDrillStore.ts | Session list |
| `GET /api/session-recall?session=<id>&op=<op>` | sessionDrillStore.ts | Session recall lenses (catch_up/open_loops/directives) |
| `GET /api/channels` | channelStore.ts | Fabric channels |
| `GET /api/tools` | toolsStore.ts | Tool definitions |
| `POST /api/tools/invoke {name, args}` | ToolsPanel.tsx | Execute a tool (gated: non-safe tools blocked) |
| `GET /api/layers` | LayerChip.tsx, SpaceChip.tsx | Embedder layers by space |
| `GET /api/layer-dims` | ResChip.tsx | Full vector dims per space/layer |
| `POST /api/resolve` | resolveAllocation.ts | Modal geometry invariant resolution |
| `POST /api/claude/turn` | fork-brain-core.js | NDJSON brain turn stream |
| `GET /dna/layouts.json` | GalleryMount.tsx, SessionDrill.tsx, ChannelView.tsx, archetype.js | Archetype definitions |
| `GET /dna/tokens.json` | surface.js (DNA.injectVars self-fetches) | DNA colour token set |
| `GET /dna/grammar.json` | surface.js (DNA.injectSpace self-fetches) | DNA space/bond/scale grammar |

---

## 6. PROPS/STATE MAP (SurfaceState)

```
SurfaceState {
  proj:           Projection | null       // full projection data from /api/projection
  error:          string | null           // fetch error (shown via Notice)
  loading:        boolean                 // initial load state
  binding:        string                  // active lens id (persisted to localStorage)
  emb:            string | null           // embedder layer (null=default BGE)
  space:          string | null           // item space override (null=binding default)
  dim:            number | null           // MRL dim truncation (null=full)
  quant:          string | null           // 'binary' | null (full float)
  selected:       number | null           // selected point seq number
  galleryOpen:    boolean                 // gallery overlay visible
  drillAddress:   string | null           // address of open decision
  feel:           MotionFeel              // 'spring' | 'eased'
  view:           ViewMode                // 'both' | 'circle' | 'square'
  nuc:            NucParams               // nucleation picker state
  centre:         Centre | null           // relative centre {ref, label}
  poles:          { a?: ...; b?: ... }   // separator poles
  live:           boolean                 // EventSource stream active
  at:             string | null           // time scrub ISO timestamp (null=now)
  corpusStart:    string | null           // earliest event timestamp
  now:            string | null           // latest event timestamp
  rung:           number | null           // semantic scale rung (null=units)
  notice:         string | null           // fail-loud notice message
  dismissNotice:  () => void             // clear notice
}
```

---

## 7. INDEX.HTML LOAD ORDER (CRITICAL)

```html
<!-- MUST LOAD IN THIS ORDER (each extends window.DNA from the previous) -->
<script src="/gallery/surface.js">        <!-- 1. FIRST: seeds window.DNA (hard overwrite) -->
<script src="/gallery/organisms.js">      <!-- 2. Extends DNA.org.* -->
<script src="/gallery/unit-view.js">      <!-- 3. DNA.renderUnit (after organisms) -->
<script src="/gallery/archetype.js">      <!-- 4. DNA.renderArchetype + DNA.renderGallery -->
<script src="/gallery/face-adapters.js">  <!-- 5. DNA.faceRecord.* -->
<script src="/gallery/fork-brain-core.js"><!-- 6. window.forkBrainCore (ONE engine) -->
<script src="/gallery/fork-v-brain.js">   <!-- 7. window.forkVBrain (rides core) -->
<script src="/gallery/wildcard-gallery-binder.js"> <!-- 8. window.galleryBinder -->
<script src="/gallery/fork-gallery-brain-hooks.js"><!-- 9. per-unit hooks (rides core) -->
<!-- THEN the deferred React module -->
<script type="module" src="/src/main.tsx" defer>
```

---

## 8. NOTABLE GAPS, SURPRISES, INCOMPLETE WORK

### GAPS (open seams)

1. **channelStore ensureStarted() is EMPTY** — `src/channels/channelStore.ts:81-84`. Channels never auto-load on first subscriber. Only loads when `openChannels()` is explicitly called. If the store is subscribed but the overlay never opened, channels are never fetched. The comment says "started" but there's no initial loadChannels() call. Compare with decisionsStore/sessionDrillStore which both call their load function in ensureStarted().

2. **GAP 4: ToolsPanel DNA tool-card result** — `src/tools/ToolsPanel.tsx`: The run result is held for DNA tool-card rendering (mentioned in source as "gap 4 — pending"); currently shows human count status only, never raw JSON. The DNA tool-card visual is not yet wired.

3. **gallery:direction legacy alias** — wildcard-gallery-binder.js emits both `gallery:verb{verb:'annotate'}` AND the legacy `gallery:direction`. The legacy alias has a TODO comment: "Drop this line once all dispatch is on gallery:verb."

4. **session-recall LENS_ROUTE seam** — `src/sessions/sessionDrillStore.ts`: `LENS_ROUTE` is defined and used but described as "goes live on checkpoint bounce." The endpoint exists as a filled seam; whether it's live depends on bridge state.

5. **fork-gallery-brain-hooks.js HOOK 2 (gallery:direction → route-back)** — described as "on-surface use-verification is projection's per THE BAR. No green-paint." The write path (POST /api/territory/write bridge route) is explicitly called a "PROPOSED diff" in fork-brain-core.js.

6. **drive/generate verbs** — RightHand.tsx verbs 5+6 are `live=false` ("soon"); they dispatch gallery:verb but the recipient path for these is unclear. In App.tsx, `gallery:verb` with verb='drive' or 'generate' shows a Notice rather than doing actual work.

7. **resolveAllocation.ts** — described as "committed-not-live"; the /api/resolve endpoint may not be fully wired.

8. **Taste typeface/pigment NOT persisted** — Taste.tsx sets `document.documentElement.setAttribute(...)` in memory but does NOT persist to localStorage. The motion feel (MotionFeel) IS passed as prop from App.tsx state (persisted by App), but type/pigment reset on reload.

9. **Members normalization in TWO places** — channelStore.ts comments "the host normalizes at the call site" AND face-adapters.js/channelGraph() normalizes internally. Double normalization; the channelStore comment flags it as flagged to DNA for a fix.

### SURPRISES (design decisions worth noting)

1. **GalleryMount is ALWAYS in DOM** — never React-unmounted; visibility toggled via CSS classes. This is a deliberate design to keep DNA's container refs stable. Standard React unmount/remount would destroy DNA's internal element refs.

2. **Subscribe store pattern throughout** — all stores (decisionsStore, sessionDrillStore, channelStore, toolsStore, Locus in address.ts) use the same module-level state + Set of subscribers + useX() hook pattern. NOT React Context, NOT Zustand. Lightweight and explicit.

3. **gallery:rerender wired at store level** — decisionsStore wires `window.addEventListener('gallery:rerender', () => loadDecisions())` ONCE at ensureStarted(), not per subscriber. This prevents N reloads when multiple components subscribe.

4. **enrich() merge-by-id (no seq-abort)** — Deliberate: in-flight enrichment applies regardless of which load triggered it. Old approach with hard seq-abort caused visible flicker (meaning vanished then reappeared after reopen).

5. **pointables tokens are OPAQUE** — window.surfacePointables() returns {token: 'auto-N', label, address}; only {token, label} sent to brain (never address). Token→address map kept client-side only. Operator-law.

6. **isVerifyMode() suppresses writes** — ?verify URL param prevents decision_take writes AND shows a persistent banner. Useful for demos/review.

7. **Two form factors do actual layout restructuring** — not just CSS media queries. Desktop/Portrait/Landscape are three DIFFERENT React component trees with different component arrangements (not the same tree with CSS hiding). The classify() function selects which to render.

8. **Tether uses rAF loop, not React** — zero React re-renders per frame; writes directly to SVG path.setAttribute via refs. This is explicitly the right approach for following animations.

9. **DNA's renderDecision is RETIRED** — archetype.js comment: "decision card draws through renderArchetype (renderDecision RETIRED) since the 2026-06-19 one-engine collapse." The host MUST carry archetype.js or decision:// renders empty.

10. **sync-gallery FAIL LOUD** — if ANY DNA source file is missing, the predev/prebuild script exits with code 1. No silent stale fallback. This blocks development if counterpart/design checkout is missing.

11. **Nucleation cornerPlace is deterministic** — uses `Math.sin(n * 12.9898 + 4.1) * 43758.5453` hash jitter (same formula as common shader noise). Stable across renders (same point always goes to same corner position).

12. **Binary quantization honest labeling** — QuantChip labels binary as "Coarse" not "Quick" or "Fast" — with source comment explaining binary is a coarser GEOMETRY not a speed win. The speed lever is ResChip (dim=).

---

## 9. CSS Z-INDEX STACK

```
20:  .scrubber (float)
30:  .disclosure (bottom sheet variant)
44:  .vhandle-scrim (RHM fan overlay veil)
45:  .vhandle (RHM handle + fan)
46:  .v-brain-panel, .v-greet, .v-note, .v-brain-tour (RHM panels)
50:  .sessions-overlay, .channels-overlay, .inbox-overlay, .tools-overlay
58:  .src-scrim (source panel scrim)
59:  .v-source (source panel card)
60:  .gallery-overlay (DNA decision card overlay)
```

---

## 10. CROSS-REFS TO OTHER AREAS

- `/home/tim/repos/counterpart/design/` — DNA's repo; sync-gallery sources surface.js, organisms.js, unit-view.js, archetype.js, face-adapters.js, phone.css, piece.css, dna/*.json from there. If DNA_REPO_DIR env var is unset, defaults to this path.
- `/home/tim/company/build-prep/front-interface/` — fabric hooks source: fork-brain-core.js, fork-v-brain.js, fork-gallery-brain-hooks.js, wildcard-gallery-binder.js. If FRONT_INTERFACE_DIR env var is unset, defaults to `../../../build-prep/front-interface` relative to scripts/.
- `bridge` at port 8770 — the `/api` proxy target; all surface API calls go here
- `canvas` at port 5173 — sister app (separate Vite app)
- `public/dna/layouts.json` — archetype definitions used by GalleryMount, SessionDrill, ChannelView, and the archetype.js renderer

---

*End of AREA-surface.md*
