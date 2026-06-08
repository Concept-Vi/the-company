# FE Structure — Deep Read
*Produced 2026-06-08. READ-ONLY pass. BUILT/PARTIAL/DESIGNED labels are honest — verified against running code, not docs.*

---

## 0 · Region count correction

The inventory claimed 19 regions; an earlier draft of this file claimed 18 including CognitionView. The actual `ls canvas/app/src/regions/` shows **18 files**:

```
Activity.tsx  AddressHelp.tsx  Fleet.tsx  Grow.tsx  History.tsx  Inbox.tsx
Inspector.tsx  OpPanels.tsx  Palette.tsx  ProposeAffordance.tsx  Review.tsx
RhmChat.tsx  SelfChanges.tsx  Settings.tsx  Toolbar.tsx  Versions.tsx
Walkthrough.tsx  Workshop.tsx
```

**CognitionView.tsx does not exist** on disk and is not imported in App.tsx — references to it in the previous draft were wrong (marked BUILT; it is absent). **Review.tsx DOES exist** (the new design-studio workspace). ProposeAffordance is in regions/ but NOT independently mounted in App.tsx — it renders inside RhmChat. App.tsx imports 17 regions directly.

---

## 1 · Surface Skeleton — how regions compose into a surface

### The grid shell (`App.tsx` — BUILT)

The outer shell is `App()` which mounts `<Tldraw>` filling the entire viewport, then places `<Hud>` as a child so the controller has access to `useEditor()`. Hud builds the controller once and wraps everything in `AppContext.Provider`.

```
App()                                     ← export default, canvas/app/src/App.tsx:307
  └─ <div style="position:fixed;inset:0">
       └─ <Tldraw shapeUtils=[NodeShapeUtil] persistenceKey="company-canvas-v3">
            └─ <Hud>  (App.tsx:119)        ← useEditor() here; ctrl built once; context provided
                 ├─ <Edges edges={ctrl.edges} />         ← pointer-events:none SVG; outside grid; screen-space wires
                 └─ <AppContext.Provider value={ctrl}>
                      └─ <PanelErrorBoundary name="surface">   ← shell-level backstop (F5)
                           ├─ <div class="view-switch" data-ui-ref="ui://view-switch">
                           │    ← canvas / review toggle buttons (App.tsx:159-162)
                           ├─ {view === 'review' && (
                           │    <PanelErrorBoundary name="review"><Review /></PanelErrorBoundary>
                           │  )}                             ← REVIEW WORKSPACE covers canvas when active
                           ├─ <div class="app-shell" data-mtab={mobileTab}
                           │        style={view==='review' ? {display:'none'} : undefined}>
                           │    ├─ <div class="as-top">
                           │    │    └─ <Toolbar />
                           │    ├─ <div class="as-rail as-sheet">
                           │    │    └─ <Palette />
                           │    ├─ <div class="as-canvas">      ← pointer-events:none passthrough
                           │    │    ├─ <PanelErrorBoundary name="walkthrough"><Walkthrough /></PanelErrorBoundary>
                           │    │    ├─ <OpPanels />
                           │    │    ├─ <Activity />
                           │    │    ├─ <PanelErrorBoundary name="chat"><RhmChat /></PanelErrorBoundary>
                           │    │    ├─ <AnnotateBar />        ← local App.tsx component
                           │    │    ├─ <WireRequest />        ← from components/WireRequest.tsx
                           │    │    └─ <JourneyBar />         ← local App.tsx component
                           │    ├─ <div class="as-panel as-sheet hud panel" data-ui-ref="inspector">
                           │    │    ├─ <Inspector />
                           │    │    ├─ <PanelErrorBoundary name="address-help"><AddressHelp /></PanelErrorBoundary>
                           │    │    ├─ <PanelErrorBoundary name="history"><History /></PanelErrorBoundary>
                           │    │    ├─ <PanelErrorBoundary name="self-changes"><SelfChanges /></PanelErrorBoundary>
                           │    │    ├─ <PanelErrorBoundary name="versions"><Versions /></PanelErrorBoundary>
                           │    │    ├─ <Inbox />
                           │    │    ├─ <Grow />
                           │    │    └─ <PanelErrorBoundary name="fleet"><Fleet /></PanelErrorBoundary>
                           │    └─ <nav class="tabbar" data-ui-ref="ui://tabbar">   ← mobile-only (<699px)
                           ├─ <Workshop />                         ← full-viewport modal, position:fixed; outside grid
                           └─ <PanelErrorBoundary name="settings"><Settings /></PanelErrorBoundary>
```

### CSS grid areas (BUILT — verified against `canvas/app/src/app.css:1086-1105`)

The `.app-shell` is a 2-row × 3-col grid (`app.css:1086-1093`): `grid-template-columns:158px 1fr 330px`, `grid-template-rows:auto 1fr`, areas `"top top top" / "rail canvas panel"`. The shell itself is `pointer-events:none`; each chrome cell or its content re-enables.

| Class | Grid area | Pointer events (app.css line) | Description |
|---|---|---|---|
| `.as-top` | `top` (spans all 3 cols) | **none** on the cell (`:1094`); `.app-shell .toolbar` re-enables `auto` (`:1103`) | Toolbar strip |
| `.as-rail` | `rail` | `auto` (`:1095`) | Left palette column (158px) |
| `.as-canvas` | `canvas` | **none** (`:1096`, passthrough); overlays re-enable per-element | tldraw board lives behind |
| `.as-panel` | `panel` | `auto` (`:1097`) | Right inspector/inbox/grow scroll rail (330px) |
| `.tabbar` | **NOT a grid area** | `auto` (`:1205`) | Mobile tab bar — `position:fixed; bottom:0` (`:1205/1216`), `display:none` >699px (`:1216`), shown only at <699px. There is **no `foot` grid-area**; the tabbar is fixed-positioned, not grid-placed. |

`.as-sheet` is applied to `.as-rail` and `.as-panel` so at <699px they become bottom-sheets driven by `data-mtab` on `.app-shell`. Desktop layout is untouched.

**`data-mtab`** attribute on `.app-shell` drives which sheet is visible at mobile width. Values: `'canvas' | 'palette' | 'inbox' | 'rhm' | 'activity'`.

### Pointer-events layering (BUILT — App.tsx:147-290)

1. `<div style="position:fixed;inset:0">` — tldraw fills the screen.
2. `.app-shell` overlays the full screen as a grid container.
3. `.as-canvas` cell: `pointer-events:none` — clicks fall through to tldraw.
4. Chrome cells: `.as-rail` and `.as-panel` are `pointer-events:auto` (app.css:1095/1097) and intercept directly. `.as-top` is itself `pointer-events:none` (`:1094`); its toolbar CONTENT re-enables via `.app-shell .toolbar{pointer-events:auto}` (`:1103`). `.tabbar` is `pointer-events:auto` (`:1205`) but fixed-positioned, not a grid cell.
5. In-canvas overlays (Activity, RhmChat, AnnotateBar, WireRequest, JourneyBar): each re-enables pointer events on its own root element.
6. Edges (`<Edges />`): full-viewport `pointer-events:none` SVG, lives outside the grid in tldraw's container.
7. Full-viewport modals (Workshop, Settings): `position:fixed`, outside the grid, cover everything.
8. Review workspace: when `view === 'review'`, covers the canvas; `.app-shell` is `display:none`.

---

## 2 · The 18 Regions — What Each Is

### Imported + mounted in App.tsx (17 regions)

#### Grid-placed regions

| Region file | Grid cell | `data-ui-ref` | One-line contract | Status |
|---|---|---|---|---|
| `Toolbar.tsx` | `.as-top` | `"toolbar"` | Command strip: mode dial, run, wire, delete, layers, fit, reload, guide, settings, indicate-mode toggle. | BUILT |
| `Palette.tsx` | `.as-rail` | `"ui://rail/palette"` | Node-type rack grouped by kind (process/content) via OINFO registry. Click to `addNode(t)`. | BUILT |
| `Inspector.tsx` | `.as-panel` (top of scroll col) | `"inspector"` (on rail container, not root) | Selected-node: status badge (registry-token-driven), NodeConfigForm, output surface, act-on-output buttons, freshness. | BUILT |
| `AddressHelp.tsx` | `.as-panel` | `"ui://inspector/help"` | D2 altitude surface: what-this-is / how-to-use / how-to-change for the indicated `ui://` locus. Null render unless indicated. | BUILT |
| `History.tsx` | `.as-panel` | — (unregistered) | Addressed event history for the indicated element (`/api/address-history`). Null render unless indicated. | BUILT |
| `SelfChanges.tsx` | `.as-panel` | — (unregistered) | Self-change audit log filtered to indicated element's code scope (`/api/self-changes-at`). Per-row revert. Null render unless indicated. | BUILT |
| `Versions.tsx` | `.as-panel` | — (unregistered) | Prior versions of selected node's output address (`/api/ref-versions`). Null render unless versioned node selected. | BUILT |
| `Inbox.tsx` | `.as-panel` | `"inbox"` | Chief-of-staff triage: build-intents (wire-blue), deferred offers, action lanes, resolved-for-you. **The reference region (kit exemplar).** | BUILT |
| `Grow.tsx` | `.as-panel` | `"ui://grow"` | Teach a new node: name + spec inputs, dispatch, surfaced-for-approval review, live node-types rack, last-change revert. | BUILT |
| `Fleet.tsx` | `.as-panel` (bottom of scroll col) | `"ui://models"` | Live model registry grouped by kind (chat/embed). Registry-truth rows; fail-loud per kind; refresh affordance. | BUILT |

#### In-canvas overlay regions (mounted inside `.as-canvas`)

| Region file | Container | `data-ui-ref` | One-line contract | Status |
|---|---|---|---|---|
| `Walkthrough.tsx` | `.as-canvas` (PanelErrorBoundary) | `"walkthrough"` on root | Guided walk card: present_current item, Next/verdict controls, voice narration. Null render unless `session` is live. | BUILT |
| `OpPanels.tsx` | `.as-canvas` | — | Declarative runtime-defined operator panels from `/api/panels` + lazy-loaded brain-authored extensions from `extensions/*.tsx`. | BUILT |
| `Activity.tsx` | `.as-canvas` | `"activity"` | Ambient SSE event feed: now-state summary + live event log. Read-only. | BUILT |
| `RhmChat.tsx` | `.as-canvas` (PanelErrorBoundary) | `"chat"` on container | Chat surface: history, input, send, voice PTT, `ProposeAffordance` sub-region. | BUILT |

#### View-switch workspace (conditionally replaces canvas)

| Region file | Mount point | `data-ui-ref` | One-line contract | Status |
|---|---|---|---|---|
| `Review.tsx` | Outside `.app-shell` (PanelErrorBoundary) | via `"ui://view-switch"` toggle | Design-studio workspace: corpus gallery (Rail), device stage (Stage), annotate/compose, RhmPanel (real RhmChat organ at the locus). Covers canvas when `view === 'review'`. | **STRUCTURE-BUILT / LOOK-PENDING** — its own header (Review.tsx:548-551) declares it the "surface skeleton … the STRUCTURE the look plugs into. The deliberate aesthetic (the look) is Claude Design's; this is the socket." Wiring works; the look is explicitly deferred to Claude Design. |

#### Full-viewport modals (outside grid, `position:fixed`)

| Region file | Mount point | One-line contract | Status |
|---|---|---|---|
| `Workshop.tsx` | Sibling of `.app-shell` | Full-screen content viewer for a selected node's output. Opened by `setWorkshop(payload)`. | BUILT |
| `Settings.tsx` | Sibling of `.app-shell` (PanelErrorBoundary) | Consolidated config: modes, models, personas, RHM-config, voice, resource-fit. Single config home. | BUILT |

### Sub-region (in regions/ but NOT independently mounted in App.tsx)

| Region file | Rendered by | One-line contract | Status |
|---|---|---|---|
| `ProposeAffordance.tsx` | `RhmChat.tsx` | B1/B2 offer-with-options surface: pick option / steer / defer / approve. Two-click consent gate. | BUILT |

---

## 3 · Component Contracts

### `AppContext.ts` + `useApp()` (BUILT — `canvas/app/src/AppContext.ts`)

```ts
export const AppContext = createContext<AppController | null>(null)
export function useApp(): AppController { ... }  // throws if outside Provider
```

`AppController` is the inferred return type of `useAppController` (`ReturnType<typeof useAppController>`). Adding a field to the return object of `useAppController` automatically adds it to the type — no interface to maintain separately.

Regions call `const { field1, handler1, ... } = useApp()`. Zero prop-drilling.

---

### `useAppController.ts` state shape (BUILT — `canvas/app/src/useAppController.ts:2271`)

The controller return object (from the actual `return { ... }` at line 2271):

**State values:** `edges, running, runError, runStartedAt, runElapsed, types, gname, gspec, surf, growMsg, workshop, oinfo, nodeStates, modeDesc, notice, gid, layerView, now, events, chat, chatMsg, chatBusy, cfg, inbox, showResolved, drill, reason, lastChange, panels, recording, configTick, session, wtReason, voiceOn, personas`

**Settings state (A3/E2-FE):** `settingsOpen, settingsTab, roles, voicePaths, voiceStatus, modeRegistry, autodetect, compositionCfg, settingsBusy, settingsErr`

**Voice/model state (S1/S2/S3/S5/S6/V3/V4):** `personaVoiceStatus, recordingSession, threads, threadId, chatModelsX, engineKnobs, voiceInfo, fitReport`

**Nav/UI state:** `wtSpoke, wtBusy, selected, mobileTab, fleet, indicated, proposal, history, historyBusy, addressHelp, addressHelpBusy, addressHelpError, prefBusy, selfChanges, selfChangesBusy, freshness, freshnessBusy, versions, versionsBusy, journeyId, journeyReplaying`

**Review/studio state:** `reviewMockup, reviewAddress, corpus, corpusErr, annotations, annotationsBusy`

**Refs (for inspector):** `configByNode`

**Setters:** `setGname, setGspec, setSurf, setWorkshop, setNotice, setCfg, setChatMsg, setShowResolved, setDrill, setReason, setWtReason, setVoiceOn, setRunError, setGrowMsg, setMobileTab, setSettingsOpen, setSettingsTab`

**Handlers:** `poll, openCoa, reload, fitGraph, addNode, wireSelected, doConnect, setNodeConfig, surfaceOutput, buildFromOutput, deleteSelected, sendChat, changeMode, cycleLayers, portalSelected, resolveUiTarget, startWalk, startGuide, endWalk, respondStep, nextStep, dispatch, recordToggle, fieldValue, setField, revertLast, revertSelfChangeAt, approveApply, doRun, refreshFleet, indicate, clickMode, annotateLocus, mintBuildIntent, setPresentationPrefAt, approveProposal, dismissProposal, steerProposal, deferProposal, setAsideProposal, reviveOffer, toggleJourneyRecording, replayJourney, switchPersona, openSettings, loadSettingsData, setCfgSlot, micPressed, setVoiceInputMode, setVoiceEnabled, toggleRecordConversation, startDebriefSession, newConversation, openConversation, chooseModel, applyRhm, setBrainKnob, setModelCtx, refreshFit, startVoiceService, indicateMode, toggleIndicateMode, setReviewMockup, refreshCorpus, fetchAnnotations`

---

### `api.ts` seam (BUILT — `canvas/app/src/api.ts`)

The sole I/O boundary. All `fetch('/api/...')` calls are here. No region or component calls `fetch` directly.

**Error normalization (`jr`):** `async function jr(r: Response)` — checks `r.ok`; on non-2xx returns `{ error: msg }` (parsed from body's `{error}` field or fallback to HTTP status text). This is a RETURNED error, not a throw, so callers branch on `if (r.error)` rather than catching. `tts` and `voiceStream` intentionally bypass `jr` (they return Blob/raw Response).

**API surface (grouped):**

| Group | Methods | Notes |
|---|---|---|
| Graph | `graph()`, `types()`, `run(force?)`, `set(node, config)`, `move(node, x, y)`, `addNode(type, config)`, `connect(e)`, `del(node)`, `objectInfo()`, `capabilities()` | Core runtime operations |
| Chat/RHM | `chat(message, focus?)`, `chatHistory()`, `act(verb, address?, args?)`, `events()`, `now()` | Chat + click-emission |
| Wire/Intent | `propose(name, spec)`, `resolve(id, choice, reason)`, `approveReach(id, members, reason)`, `apply(id)`, `intentAt(address, text, ...)`, `buildIntent(spec, scope?, ...)`, `coa(id)`, `deferOffer(proposal, note)`, `reviveOffer(id)`, `surfaceOutput(node)`, `react()` | Decision→build wire |
| Mode | `setMode(mode)`, `rhmConfig()`, `setRhmConfig(updates)`, `inbox()` | Presence/config |
| Voice | `voice()`, `stt(blob)`, `tts(text)`, `personas()`, `voiceServices()`, `voiceSwitch(persona)`, `voiceStream(blob, persona, trial?)`, `voiceLog(event, data)`, `voiceEngineKnobs()`, `finishedThought(text)` | Full voice circuit |
| Models | `models(kind)`, `modelLoad(service)`, `modelConfig(service, key, value)`, `fit(services)`, `chatModelsDetailed()` | Model registry + resource |
| Conversations | `newConversation(title?)`, `listConversations()`, `loadConversation(threadId)`, `trialSessions()`, `startDebrief(sessionIds, hostPersona?)` | Thread management |
| Address | `uiInfo()`, `corpus()`, `annotations(address)`, `addressHistory(address)`, `selfChangesAt(address)`, `addressHelp(address)`, `upTranslate(kind, ref)`, `presentationPref(address)`, `setPresentationPref(address, pref, text?)` | Address-keyed reads |
| Freshness | `staleAt(address)`, `refVersions(address)` | Memo gate + version history |
| Walkthrough | `reviewStart(item_ids, mode)`, `reviewCurrent(session)`, `reviewNext(session)`, `reviewStatus(session)`, `walkthroughStart(item_ids?)`, `resolveStep(id, choice, reason, session, position)` | Walk session lifecycle |
| Journey | `journeyStart()`, `journeyStep(journey, address)`, `journeyStop(journey)`, `journeyReplay(journey)`, `journeys()` | Reverse journey recording |
| History/Self | `lastChange()`, `revert(sha)`, `panels()` | Self-change revert |

**Utility exports:** `MODES: string[]`, `resolveOptions(f)`, `configSchemaToFields(schema)`, `coerceConfigValue(field, raw)`, `relTime(iso?)`, `isBuildIntent(d)`, `buildPhase(d)`, `deriveOutcome(d, liveTypes)`.

---

### `registryStore.ts` (BUILT — `canvas/app/src/registryStore.ts`)

WHY IT EXISTS: NodeShape renders inside tldraw (below `<Tldraw>`), so it cannot reach a React context. The 6 former module-scope globals are replaced with one external store readable via `useSyncExternalStore`.

**State shape (`RegistryState`):**
- `OINFO`: `Record<string, any>` — type → `{ports:{inputs,outputs}, config_schema, kind}` from `/object_info`
- `MODEL_OPTIONS`: `Record<string, string[]>` — kind → model name list (B2 live registry)
- `UI_INFO`: `Record<string, any>` — ui_info registry from `/api/ui_info`
- `NODE_STATES`: `Record<string, NodeStateDef>` — stateId → `{id, label, means?, applies_to?, render?{token, icon, shape}}` from `capabilities().node_states`

**External store API:**
- `registryStore.subscribe(cb)` / `registryStore.getSnapshot()` / `registryStore.set(patch)` — React 18 external store interface
- Imperative reads for non-React call sites: `getOINFO()`, `getMODEL_OPTIONS()`, `getUI_INFO()`, `getNODE_STATES()`

**Module-scope refs (not in store — function handles):**
- `CONNECT` / `setConnect(fn)` — the controller installs the drag-to-wire commit handler
- `DRAG_CONN` / `setDragConn(v)` — transient drag gesture state shared across shape instances
- `FORCE_RUN` / `setForceRun(fn)` — the per-node force-rerun affordance

---

### `kit.tsx` primitives (BUILT — `canvas/app/src/components/kit.tsx`)

All five primitives are token-only. Classes resolve through `app.css → design-system.css → tokens.json`. No inline styles, no bespoke hex/px.

**Tone vocabulary** (`type Tone = 'sig' | 'await' | 'fail' | 'wire' | 'dim'`):
- `sig` = done/ok/resolved (mint green signal)
- `await` = needs operator action (amber)
- `fail` = error state (red)
- `wire` = building/proposed/in-flight (blue)
- `dim` = neutral/background/held

#### `SectionHead`
- **Props:** `children: ReactNode`, `tag?: string`, `aside?: ReactNode`
- **Emits:** nothing
- **CSS:** `.kit-sechead`, `.kit-kicker` (uppercase kicker), `.kit-sectitle` (Fraunces display voice)
- **Slot:** `aside` = right-aligned slot for counts, action buttons

#### `LaneHead`
- **Props:** `children`, `count?: number`, `tone?: Tone`, `onToggle?: () => void`, `open?: boolean`
- **Emits:** `onToggle()` when provided (renders as `<button>` with caret; `open` controls caret direction)
- **CSS:** `.kit-lanehead .kit-tone-{tone}` — tone drives left-edge tint + count colour

#### `Badge`
- **Props:** `children`, `tone?: Tone`
- **Emits:** nothing
- **CSS:** `.kit-badge .kit-tone-{tone}` — read state by colour, not text

#### `Surface`
- **Props:** `children`, `tone?: Tone`, `onClick?: () => void`, `className?: string`, `title?: string`, `interactive?: boolean`, `dataUiRef?: string`
- **Emits:** `onClick()` — the row/card interaction
- **CSS:** `.kit-surface [.kit-tone-{tone}] [.kit-surface-actionable]`
- **Load-bearing prop:** `dataUiRef` is forwarded as `data-ui-ref` on the DOM element. The `resolveUiTarget` keystone queries by `[data-ui-ref]`; if an addressed element is a `<Surface>`, it must use `dataUiRef`, not `data-ui-ref` directly in JSX.

#### `EmptyState`
- **Props:** `children`
- **CSS:** `.kit-empty` — honest rest-state; never a blank gap

---

### `PanelErrorBoundary` (BUILT — `canvas/app/src/components/PanelErrorBoundary.tsx`)

```ts
class PanelErrorBoundary extends Component<{ name: string; children: any }, { err: boolean }>
```

A React class component. On render error: `"⚠ panel "{name}" failed to render"`. The canvas stays live. Currently wraps: every in-canvas overlay that can throw, every right-rail region below Inspector, both full-viewport modals, plus a shell-level backstop (`name="surface"`).

---

### `StudioKit.tsx` — named studio primitives (STRUCTURE-BUILT / LOOK-PENDING — `canvas/app/src/components/StudioKit.tsx`)

The structural shells the `Review.tsx` region composes from. Five named parts:
- `<Card>` — one gallery item; carries `data-ui-ref` of its reviewed-surface address
- `<Rail>` — the corpus gallery of Cards, grouped, registry-bound from `/api/corpus`
- `<Stage>` — sandboxed iframe device stage (phone/desktop)
- `<Composer>` — addressed-feedback composer (annotate → `/api/annotate` + change → `/api/intent-at`)
- `<RhmPanel>` — mounts the real `<RhmChat />` organ at the locus + AddressHelp + Composer

These components declare their contract in their header (binds/emits/token-slots). They are **structure-only by design** (StudioKit.tsx:5-7): "layout that works, NO bespoke aesthetic, NO gold-look. Claude Design fills the token-slots; the structure stays." This is the one place in the FE explicitly built as an empty socket for Claude Design to fill — the wiring is BUILT, the look is the deliverable that's PENDING. Everything else in the FE (sections 1-4 above) is BUILT with the gold look already applied.

---

## 4 · FE Conventions — Where Things Go

These are confirmed BUILT in the code, not guessed from documentation.

### File locations

| Thing | Where it lives | Convention |
|---|---|---|
| All state + handlers + effects | `useAppController.ts` | The single hook. One place, not scattered. |
| Context exposure | `AppContext.ts` | `createContext` + `useApp()` hook. Regions never receive props — they call `useApp()`. |
| API calls | `api.ts` | All `fetch('/api/...')` calls live here. `jr` normalizes HTTP errors. No fetch in regions or controller. |
| Shape-reachable registry | `registryStore.ts` | External store (subscribe/getSnapshot/set). OINFO, MODEL_OPTIONS, UI_INFO, NODE_STATES. Used by NodeShape/Edges inside tldraw. |
| Carved presentational surfaces | `regions/*.tsx` | No domain state, no fetch calls. Read from `useApp()`, call controller handlers. |
| Shared kit primitives | `components/kit.tsx` | SectionHead, LaneHead, Badge, Surface, EmptyState. The five primitives. |
| Multi-region non-kit components | `components/*.tsx` | PanelErrorBoundary, NodeConfigForm, BuildIntentCard, BlastRadiusReach, ContextBundle, ShapeHow, WireRequest, PanelView, StudioKit |
| App-local components | `App.tsx` | AnnotateBar, JourneyBar — bridge global controller state and grid structure; live only in App.tsx |

### Patterns confirmed in code

**kit-first** (BUILT): Every region that was redesigned imports from `'../components/kit'`. Regions do not invent equivalent primitives.

**Tokens-only** (BUILT): kit.tsx is "token-only (the .kit-* classes in app.css resolve to design-system.css tokens)". The design-lint `python3 design/_system/check.py --target canvas/app/src --fail-on` gates the build on this (AGENTS.md rule 9).

**`data-ui-ref` addressing** (BUILT): Every meaningful interactive element carries `data-ui-ref="ui://<region>/<element>"`. Must be registered in `design/_system/addresses.json`. Unregistered addresses are flagged as orphans by `parse.py`. An unregistered address still works at runtime but is invisible to show-me / address-help / history.

**PanelErrorBoundary wrapping** (BUILT): Every region that could throw has a per-panel boundary. Shell-level backstop catches layout-level throws. A panel throw renders a contained card; the canvas stays live.

**Single useAppController + AppContext** (BUILT): `useAppController(editor)` called once in `Hud`. `<AppContext.Provider value={ctrl}>` wraps the shell. Zero prop-drilling.

**api.ts is the sole I/O boundary** (BUILT): No region or component calls `fetch`. The controller calls `api.*`. `jr` normalizes HTTP errors.

**reflects-never-owns** (BUILT): Canvas never holds authoritative state. `loadGraph` writes to the tldraw editor store from backend truth. SSE `openStream` dispatches per-kind refreshes. Backend is always the source.

**Registry-is-truth** (BUILT): Node types, models, modes, node states, UI info — all read from backend registries, never hardcoded in FE. `getMODEL_OPTIONS()` reads from the registryStore; `configSchemaToFields()` reads schema from OINFO.

---

## 5 · The `data-ui-ref` → `addresses.json` Registration Chain (BUILT)

The join between a live DOM element and the design corpus:

1. A meaningful element carries `data-ui-ref="ui://<region>/<element>"` in its JSX (directly or via `Surface dataUiRef` prop).
2. `design/_system/addresses.json` registers that address: `{ "capabilities": [...], "represents": "<feature-id>", "code": "<file:line>" }`.
3. `python3 design/_system/parse.py` reads all mockups + the registry → `element-map.json` (element ⇄ address ⇄ feature ⇄ code + orphan lists).
4. `indicate(addr)` in the controller uses `document.querySelector('[data-ui-ref="' + addr + '"]')` to find the element and paint `.ui-indicated`.
5. `resolveUiTarget(address)` (the show-me keystone) uses the same query to scroll and spotlight the element.
6. `getUI_INFO()` (from `/api/ui_info`) lets the controller resolve a `ui://` address to its title for notice text.

**Orphan rules:**
- Address in code but not in `addresses.json` → orphan (parse.py flags it). Works at runtime, invisible to show-me/history.
- Address in `addresses.json` but no mockup carries it → registered-but-unused (the backlog).
- Inbox.tsx line 96–99 documents an explicitly deferred registration for `ui://inbox/deferred-offers` — acceptable-short-term pattern.

---

## 6 · How to Add a New Region — The Concrete Recipe

*Derived from Inbox.tsx (the declared reference) + App.tsx grid placement + cross-checked against Palette, Fleet, Inspector, Review.*

### Step 1: Create `regions/MyRegion.tsx`

```tsx
// canvas/app/src/regions/MyRegion.tsx
import { SectionHead, LaneHead, Badge, Surface, EmptyState } from '../components/kit'
import { PanelErrorBoundary } from '../components/PanelErrorBoundary'  // if sub-components can throw
import { useApp } from '../AppContext'

export function MyRegion() {
  const { /* the fields and handlers you need from the controller */ } = useApp()
  return (
    <div data-ui-ref="ui://myregion" className="myrgn">
      <SectionHead tag="my-kicker">my region</SectionHead>
      {/* kit primitives compose the content */}
    </div>
  )
}
```

Rules:
- No `useState` or `useEffect` unless purely local UI state (open/close toggle, etc.). All domain state lives in `useAppController.ts`.
- No `fetch` calls. Data comes from `useApp()`. Mutations call controller handlers.
- No inline styles. No hardcoded hex/px. Token classes only (`.kit-*`, `.b`, `.muted`, `.mono`, etc. from `app.css` / `design-system.css`).
- Kit-first: compose from the five kit primitives.
- Root element carries `data-ui-ref="ui://myregion"`. Sub-elements carry `data-ui-ref="ui://myregion/element"`.

### Step 2: Mount in App.tsx

Import and place inside `AppContext.Provider` in `Hud`'s return:

```tsx
// App.tsx — import
import { MyRegion } from './regions/MyRegion'

// RIGHT RAIL — append to .as-panel scroll column (stacks below Fleet):
<div className="as-panel as-sheet hud panel" data-ui-ref="inspector">
  {/* ... existing regions ... */}
  <PanelErrorBoundary name="my-region">
    <MyRegion />
  </PanelErrorBoundary>
</div>

// IN-CANVAS OVERLAY — append inside .as-canvas:
<div className="as-canvas">
  {/* ... existing overlays ... */}
  <PanelErrorBoundary name="my-region">
    <MyRegion />
  </PanelErrorBoundary>
</div>

// FULL-VIEWPORT MODAL — outside .app-shell, sibling of Workshop:
<PanelErrorBoundary name="my-region">
  <MyRegion />  {/* uses position:fixed internally */}
</PanelErrorBoundary>
```

**PanelErrorBoundary is not optional.** Every region in the current codebase that could throw is wrapped. The shell-level boundary is the backstop; per-panel boundaries contain failures to a card, keeping the canvas alive.

### Step 3: Wire state into `useAppController.ts`

If the region needs state or handlers the controller doesn't yet expose:

```ts
// useAppController.ts — add inside the function body
const [myData, setMyData] = useState<any>(null)

async function myHandler() {
  const r = await api.someEndpoint()
  if (r.error) { setNotice('✕ ' + r.error); return }
  setMyData(r.result)
}

// add to the return object:
return { ...existingFields, myData, setMyData, myHandler }
```

`AppController` is `ReturnType<typeof useAppController>` — inferred from the return shape. Adding a field automatically makes it available to all regions via `useApp()`. No interface to update separately.

### Step 4: Register addresses in `design/_system/addresses.json`

For every `data-ui-ref="ui://myregion"` and `data-ui-ref="ui://myregion/element"`:

```json
{
  "ui://myregion": {
    "region": "myregion",
    "element": "root",
    "capabilities": ["pointable", "spotlit"],
    "represents": "<feature-id from design/register.json>",
    "code": "regions/MyRegion.tsx:NN",
    "howto": "What this element does in plain language."
  }
}
```

Then run: `python3 design/_system/parse.py` → refreshes `element-map.json`.

An unregistered `data-ui-ref` is flagged as an orphan. The region works at runtime without registration, but show-me / address-help / history won't resolve the element.

### Step 5: Run the design-lint gate

```bash
python3 design/_system/check.py --target canvas/app/src --fail-on
```

Scans source for off-token literals (hardcoded hex, bespoke elements); exits non-zero. A new region using tokens only passes clean. This is the FORM gate (AGENTS.md rule 9).

### Step 6 (if the region has a mockup): Register in `design/register.json` + gallery

Place the mockup HTML in `design/mockups/`, register the view in `register.json` under the appropriate journey, run `python3 design/_system/gallery.py`. The `index.html` gallery is GENERATED — never edit it.

---

## 7 · What a New Surface Must Never Do

Hard rules confirmed in code and constitutions:

- **No per-node-type frontend code** (`canvas/AGENTS.md`): NodeShape is one generic shape. New node types require zero FE edits. A surface that introduces a node-type-specific render path violates the contract.
- **No parallel config surface** (Settings consolidation, `useAppController.ts:190`): all config lives in Settings. A new region must not create its own config UI.
- **No fetch calls** (confirmed: no region imports `fetch` or calls `api.*` directly — only the controller does).
- **No authoritative state** (reflects-never-owns): a region cannot hold state the backend owns. It reads from `useApp()` and calls controller handlers.
- **No unregistered `data-ui-ref`** in the long run: an unregistered address is a corpus orphan — tolerated short-term (as in Inbox.tsx), must be registered before the address system degrades.
- **No off-token styles**: the design-lint gate enforces this at build time (AGENTS.md rule 9).
- **No parallel fetch/store outside api.ts**: the api module is the sole I/O boundary.

---

## 8 · Key Structural Facts for Claude Design

1. **The kit Tone vocabulary** (`'sig' | 'await' | 'fail' | 'wire' | 'dim'`) is the signal language. A new surface's tint choice communicates meaning: sig = done/ok (mint green), await = needs action (amber), fail = error (red), wire = building/proposed (blue), dim = neutral/background.

2. **The `ui://` address scheme** (`ui://<region>[/<element>][@state]`) is the coordinate system. Every meaningful element has one. Capabilities on the address (`pointable`, `spotlit`, `presentable`, `openable`, `driven`) determine what the system can do with it (show-me, address-help, history, indicate, animate).

3. **ProposeAffordance is NOT independently mounted** — it renders inside RhmChat. Claude Design must not plan a placement for it as a separate grid region.

4. **The right rail is a single scroll column** — Inspector, AddressHelp, History, SelfChanges, Versions, Inbox, Grow, Fleet are all stacked in one `.as-panel` scroll container. New rail surfaces append to that stack inside a PanelErrorBoundary.

5. **Full-viewport modals follow the Workshop/Settings pattern**: `position:fixed` outside the grid, opened/closed by controller state, cover everything. Currently two exist (Workshop, Settings).

6. **Mobile collapses the rails to bottom-sheets** via `.as-sheet` + `data-mtab`. A new right-rail region inherits this automatically. A new in-canvas overlay is `display:none` at <699px (App.tsx:181-183); its content must be reachable via rhm or inbox sheet on mobile.

7. **Review workspace is a view-level switch** (not a grid region): when `view === 'review'`, the `.app-shell` is `display:none` and `<Review />` covers the screen. It lives inside the same `AppContext.Provider` and uses the same controller. The tldraw board keeps running underneath either way.

8. **CognitionView.tsx does not exist** on disk as of this read (2026-06-08). Any build plan that references it is referencing an absent file. The region list is exactly the 18 files confirmed in `ls regions/`.

9. **StudioKit.tsx named primitives** (`Rail`, `Stage`, `Composer`, `Card`, `RhmPanel`) are the building blocks Claude Design designs against for the studio workspace — distinct from the general kit.tsx primitives (SectionHead/LaneHead/Badge/Surface/EmptyState).

10. **`AppController` is inferred, not declared** — `ReturnType<typeof useAppController>`. The return object at `useAppController.ts:2271` IS the type. Adding a field to the return adds it to the type automatically.

---

*Sources (direct reads in this session): `inv-B-fe-design.md`, `canvas/AGENTS.md`, `api.ts` (full), `registryStore.ts` (full), `components/kit.tsx` (full), `regions/Inbox.tsx` (full), `AppContext.ts` (full), `App.tsx` (lines 1–327), `useAppController.ts` (lines 1–150, 2271–2307), `components/PanelErrorBoundary.tsx` (full), region headers (first 30 lines each): Toolbar, Palette, Inspector, Grow, OpPanels, Activity, RhmChat, Walkthrough, Workshop, Settings, Fleet, SelfChanges, Versions, AddressHelp, ProposeAffordance, History, Review, StudioKit.tsx (first 30 lines).*

*Label definitions (honest about evidence depth):*
- *BUILT = the file is present, exports the component, and is mounted in App.tsx (or, for ProposeAffordance, mounted in its parent region). For the deeply-read files (api.ts, registryStore.ts, kit.tsx, Inbox.tsx, AppContext.ts, PanelErrorBoundary.tsx, App.tsx, useAppController.ts return shape) BUILT also means the structure was read in full. For the skim-only regions, BUILT rests on present + exported + mounted + a read of the file's header/signature — NOT on executing the code. This is structural Observation, not functional Verification.*
- *STRUCTURE-BUILT / LOOK-PENDING = the component's wiring and layout exist and are mounted, but the file's own header declares the aesthetic deliberately deferred to Claude Design (Review.tsx, StudioKit.tsx).*
- *PARTIAL = partially implemented (some paths work). DESIGNED = design exists, no code yet. Neither was needed for any region in this read.*
- *No claim here rests on pattern-matching. CognitionView's absence was confirmed empirically (`ls regions/` + no import in App.tsx). The grid-area table was confirmed by reading app.css:1086-1105 directly.*
