// F0 · the restructured shell.
//
// WHAT CHANGED (the carve): the former single 1659-line file with one ~1070-line Hud() mega-component is
// now a coherent set of files — api.ts (the client + pure helpers), registryStore.ts (the 6 module globals
// → one external store the tldraw shape can reach), NodeShape.tsx (the generic node shape + Edges +
// loadGraph), useAppController.ts (the state container — ALL the former Hud state + handlers + effects, in
// ONE hook, not 37 useState scattered), AppContext.ts (exposes the controller to the regions), and
// regions/*.tsx (Toolbar · Palette · Inspector · Inbox · Grow · OpPanels · Activity · RhmChat ·
// Walkthrough · Workshop). Plus components/*.tsx (PanelErrorBoundary · PanelView · NodeConfigForm ·
// BuildIntentCard).
//
// THE LAYOUT SHELL (F0 deliverable: "a real layout shell, NOT 7 fixed-px absolute islands"): the regions
// are placed into a top-level CSS GRID (`.app-shell`, areas top/rail/canvas/panel/foot from
// design/design-system.css's `.app` model). The grid is layered OVER the tldraw board; the `canvas`
// grid-cell is pointer-events:none so the board underneath stays fully interactive (pan/zoom/select/drag),
// while the chrome cells (top/rail/panel/foot) re-enable pointer-events. This replaces the absolute-px
// islands with one layout container. (F1 = full token adoption · F2 = responsive breakpoints + dock/collapse
// + removing fitGraph's duplicated px — F0 carves the structure those build on.)
//
// PRESERVED (the bar — see each region/controller file for the inline how): per-panel error boundaries ·
// reflects-never-owns · registry-driven config+ports · SSE mergeEvents seq-dedup · the resolveUiTarget/show
// keystone · wtBusyRef guards · semantic zoom · drag-to-wire · voice push-to-talk · demonstrate-first ·
// delete-confirm · the U1 canvas-RUN fix (() => doRun() + the always-clearing finally) · operator-only approval.
import { Tldraw, useEditor } from 'tldraw'
import { NodeShapeUtil, Edges } from './NodeShape'
import { useAppController } from './useAppController'
import { AppContext } from './AppContext'
import { PanelErrorBoundary } from './components/PanelErrorBoundary'
import { Toolbar } from './regions/Toolbar'
import { Palette } from './regions/Palette'
import { Inspector } from './regions/Inspector'
import { Inbox } from './regions/Inbox'
import { Grow } from './regions/Grow'
import { OpPanels } from './regions/OpPanels'
import { Activity } from './regions/Activity'
import { RhmChat } from './regions/RhmChat'
import { Walkthrough } from './regions/Walkthrough'
import { Workshop } from './regions/Workshop'

// Hud — the single component with useEditor. It builds the controller (the state container) ONCE and
// provides it to every region via AppContext, then lays the regions out in the grid shell. It is a child
// of <Tldraw>, so the controller's editor-bound handlers + the shape both share the one editor instance,
// and Edges paints in tldraw's own container (screen-space via pageToScreen) — exactly as before the carve.
function Hud() {
  const editor = useEditor()
  const ctrl = useAppController(editor)
  return (
    <AppContext.Provider value={ctrl}>
      {/* Edges paints over the whole viewport (pointer-events:none); kept outside the grid so it overlays
         the canvas in tldraw's container — the wire ↔ port screen-space math is unchanged. */}
      <Edges edges={ctrl.edges} />
      {/* The top-level layout shell — one grid container, not absolute-px islands. The `canvas` cell is
         transparent + pointer-events:none so the tldraw board underneath stays interactive. */}
      <div className="app-shell">
        <div className="as-top"><Toolbar /></div>
        <div className="as-rail"><Palette /></div>
        {/* the canvas cell is a passthrough — the tldraw board renders behind the shell; overlays that must
           sit over the canvas (walkthrough card, op-panels) live here, each re-enabling pointer-events. */}
        <div className="as-canvas">
          <PanelErrorBoundary name="walkthrough">
            <Walkthrough />
          </PanelErrorBoundary>
          <OpPanels />
          <Activity />
          <RhmChat />
        </div>
        {/* the right rail — Inspector + Inbox + Grow stacked in ONE scroll column (the .panel rail, as
           before). data-ui-ref="inspector" is on this scroll container (the resolveUiTarget keystone +
           the U7 scroll-into-view query it by that ref). */}
        <div className="as-panel hud panel" data-ui-ref="inspector">
          <Inspector />
          <Inbox />
          <Grow />
        </div>
      </div>
      {/* Workshop is a full-viewport modal (position:fixed) — outside the grid so it covers everything. */}
      <Workshop />
    </AppContext.Provider>
  )
}

export default function App() {
  return (
    <div style={{ position: 'fixed', inset: 0 }}>
      <Tldraw
        shapeUtils={[NodeShapeUtil]}
        persistenceKey="company-canvas-v2"
        components={{ StylePanel: null, ActionsMenu: null, QuickActions: null }}
      >
        <Hud />
      </Tldraw>
    </div>
  )
}
