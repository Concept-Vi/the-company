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
import { useState, useEffect } from 'react'
import { Tldraw, useEditor } from 'tldraw'
import { NodeShapeUtil, Edges } from './NodeShape'
import { useAppController } from './useAppController'
import { AppContext, useApp } from './AppContext'
import { PanelErrorBoundary } from './components/PanelErrorBoundary'
import { Toolbar } from './regions/Toolbar'
import { Palette } from './regions/Palette'
import { Inspector } from './regions/Inspector'
import { AddressHelp } from './regions/AddressHelp'
import { History } from './regions/History'
import { Versions } from './regions/Versions'
import { SelfChanges } from './regions/SelfChanges'
import { Inbox } from './regions/Inbox'
import { Grow } from './regions/Grow'
import { OpPanels } from './regions/OpPanels'
import { Activity } from './regions/Activity'
import { RhmChat } from './regions/RhmChat'
import { Walkthrough } from './regions/Walkthrough'
import { Workshop } from './regions/Workshop'
import { Settings } from './regions/Settings'
import { Fleet } from './regions/Fleet'
import { CognitionView } from './regions/CognitionView'
import { WireRequest } from './components/WireRequest'
import { api } from './api'

// I5 · the ANNOTATE-FACE affordance. Renders ONLY when the operator has indicated a ui:// element whose
// bare-click face is 'annotate' (ctrl.clickMode === 'annotate' — the canonical route_click rule, single-
// sourced). A small comment box → ctrl.annotateLocus → POST /api/annotate (the I6 path). This is the
// click→comment that makes the criteria FUNCTION reachable on the surface. The OPERATE face is never
// blurred with it (operate rides a control's own onClick → /api/act + the I3 approve path). FORM: reuses
// the corpus .rhm-indicating chip vocabulary (tokens only — the amber annotate cue is the mode-signal,
// needs-tim). Hidden whenever nothing annotate-mode is indicated, so it never clutters the canvas.
function AnnotateBar() {
  const { indicated, clickMode, annotateLocus } = useApp()
  const [text, setText] = useState('')
  if (!indicated || clickMode(indicated) !== 'annotate') return null   // only for an annotate-mode locus
  async function submit() {
    const t = text.trim(); if (!t) return
    await annotateLocus(t); setText('')                                // annotateLocus is fail-loud (notice on error)
  }
  return (
    <div className="rhm-indicating annotate-bar" title="attach a comment to the indicated element">
      <span className="ic">💬</span>
      <input className="ind-addr ann-input" value={text} placeholder={'comment on ' + indicated + '…'}
             onChange={e => setText(e.target.value)}
             onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); submit() } }} />
      <button className="ind-clear" onClick={submit} title="attach comment" disabled={!text.trim()}>↵</button>
    </div>
  )
}

// L9 · reverse journey-recording (§21.7#2-reverse). The REVERSE of the forward resolveUiTarget made
// reachable on the surface: an explicit RECORD toggle captures the operator's ordered ui:// click-path as
// a DISTINCT journey-record (each indicated element appends a step — wired in ctrl.indicate), and recorded
// journeys are REPLAYED by stepping the view through their addresses via the PRESERVED resolveUiTarget
// (ctrl.replayJourney). DISTINCT from the review-session walk (Walkthrough/Inbox → startWalk, which walks
// item-ids) — this records NAVIGATION. FORM: built on the corpus .rhm-indicating chip vocabulary (tokens
// only, mirroring AnnotateBar) — no bespoke styling, no literals. The control itself is NOT a registered
// ui:// locus (it captures OTHER addresses; making it one would orphan the registry — deliberately bare).
function JourneyBar() {
  const { journeyId, journeyReplaying, toggleJourneyRecording, replayJourney } = useApp()
  const [journeys, setJourneys] = useState<any[]>([])
  // refresh the replayable list on mount, and whenever recording stops (journeyId → null finalizes one).
  useEffect(() => {
    let live = true
    api.journeys().then((r: any) => { if (live && Array.isArray(r)) setJourneys(r) }).catch(() => { /* surfaced via notice elsewhere */ })
    return () => { live = false }
  }, [journeyId])
  const recording = !!journeyId
  return (
    <div className="rhm-indicating journey-bar" title="record an ordered click-path through addresses, then replay it as a walkthrough">
      <span className="ic">{recording ? '●' : '◉'}</span>
      <button className="ind-clear" onClick={() => toggleJourneyRecording()}
              title={recording ? 'stop + finalize this journey' : 'start recording a click-path journey'}>
        {recording ? '■ stop journey' : '◉ record journey'}
      </button>
      {!recording && journeys.length > 0 && (
        <select className="ind-addr" disabled={journeyReplaying} defaultValue=""
                title="replay a recorded journey — steps the view through its addresses"
                onChange={e => { const v = e.target.value; if (v) { replayJourney(v); e.currentTarget.value = '' } }}>
          <option value="" disabled>{journeyReplaying ? 'replaying…' : '▶ replay…'}</option>
          {journeys.map((j: any) => (
            <option key={j.id} value={j.id}>{j.id} · {j.steps} step{j.steps === 1 ? '' : 's'}</option>
          ))}
        </select>
      )}
    </div>
  )
}

// Hud — the single component with useEditor. It builds the controller (the state container) ONCE and
// provides it to every region via AppContext, then lays the regions out in the grid shell. It is a child
// of <Tldraw>, so the controller's editor-bound handlers + the shape both share the one editor instance,
// and Edges paints in tldraw's own container (screen-space via pageToScreen) — exactly as before the carve.
function Hud() {
  const editor = useEditor()
  const ctrl = useAppController(editor)
  // F2 (responsive): mobileTab drives which sheet shows at <699px. The data-mtab attribute on the shell lets
  // the CSS reveal exactly one bottom-sheet (or none for 'canvas'). On desktop/tablet the tabbar + sheet
  // behaviour is display:none, so this attribute is inert above 699px — desktop layout is untouched.
  const { mobileTab, setMobileTab } = ctrl
  // G-57 · PHONE: a CONSEQUENTIAL offer (the B2 interactive proposal — build/panel/extend) lands in the RHM
  // chat, but on phone the chat is a bottom-sheet hidden unless the 'rhm' tab is raised — so a fresh
  // consequential offer could be MISSED. When `ctrl.proposal.interactive` flips true (the registry-truth flag
  // the comparison surface renders on), auto-raise the rhm sheet so the operator sees the choice. This is the
  // SHEET-LAYER hook only (setMobileTab — already on the controller, zero voice-function reach). INERT on
  // desktop: the tabbar/sheets are display:none >699px, so setMobileTab changes nothing visible there (the
  // chat is always-on in the canvas cell) — it only matters at phone width. Single-source: it sets the SAME
  // mobileTab the operator's taps drive, so a raised offer and a manual tab never both claim the bottom edge.
  useEffect(() => {
    if (ctrl.proposal?.interactive) setMobileTab('rhm')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ctrl.proposal?.interactive])
  return (
    <AppContext.Provider value={ctrl}>
      {/* Edges paints over the whole viewport (pointer-events:none); kept outside the grid so it overlays
         the canvas in tldraw's container — the wire ↔ port screen-space math is unchanged. */}
      <Edges edges={ctrl.edges} />
      {/* F5: the SHELL-LEVEL catch-all. fe-map §5 traced the white-screen to an UNWRAPPED Hud shell —
         `App()` wrapped only <Tldraw>, no top-level boundary, so any render-throw inside the chrome killed
         the operator's only control surface. This boundary is the backstop UNDER the per-panel ones: a throw
         a panel-boundary doesn't catch (e.g. layout-level) now renders a contained card over the LIVE canvas
         (the tldraw board behind the grid keeps running) instead of a blank document. The chat path itself no
         longer throws (api.ts jr + the sendChat guard), so this is defense-in-depth, not the primary fix. */}
    <PanelErrorBoundary name="surface">
      {/* The top-level layout shell — one grid container, not absolute-px islands. The `canvas` cell is
         transparent + pointer-events:none so the tldraw board underneath stays interactive.
         F2: data-mtab = the active mobile sheet; data-bp on the breakpoints does the column/row collapse. */}
      <div className="app-shell" data-mtab={mobileTab}>
        {/* F2: as-rail/as-panel get .as-sheet so that at <699px they become bottom-sheets the tabbar toggles
           (instead of fixed-px islands that overlap the canvas). Above 699px .as-sheet is inert. */}
        <div className="as-top"><Toolbar /></div>
        <div className="as-rail as-sheet"><Palette /></div>
        {/* the canvas cell is a passthrough — the tldraw board renders behind the shell; overlays that must
           sit over the canvas (walkthrough card, op-panels) live here, each re-enabling pointer-events.
           F2: at <699px these in-canvas overlays are display:none (they overlap each other at phone width —
           fe-map §4); their content reaches the operator via the rhm bottom-sheet + the inbox sheet instead. */}
        <div className="as-canvas">
          <PanelErrorBoundary name="walkthrough">
            <Walkthrough />
          </PanelErrorBoundary>
          <OpPanels />
          <Activity />
          {/* F5: the rhm-chat panel was the unprotected white-screen gap (fe-map §5) — the most-exercised
             surface had the LEAST protection. A per-panel boundary contains a chat render-throw to a card,
             keeping the toolbar/RUN/canvas alive (better FORM than blanking the whole shell). Extends the
             existing per-panel boundary discipline (PRESERVE-LIST item 1). */}
          <PanelErrorBoundary name="chat">
            <RhmChat />
          </PanelErrorBoundary>
          {/* L-fe · the LIVE COGNITION VIEW (the commander's bridge, E2/06). EXTEND not replace: it is one
             MORE in-canvas overlay beside the chat/activity (removes/replaces nothing). It sits at the chat
             lane edge so the PULSE (Altitude 0, default) breathes BESIDE the reply — the conversation's
             heartbeat of cognition — and the RIVER/NODES expand in place on click. Driven entirely by the
             live cognition.* SSE (reflects-never-owns) + the /api/cognition_info projection (registry-driven).
             Per-panel boundary (PRESERVE-LIST item 1): a cognition render-throw degrades to a contained card,
             never a white-screen. At <699px the in-canvas overlays are display:none (fe-map §4) — the pulse
             rides the chat sheet there (the chat is the operator's reply surface on mobile). */}
          <PanelErrorBoundary name="cognition">
            <CognitionView />
          </PanelErrorBoundary>
          {/* I5 · the ANNOTATE FACE made reachable on the surface. When the operator has indicated a
             ui:// element that a bare click ANNOTATES (clickMode==='annotate' — the canonical route_click
             rule), this bar lets them attach a comment at that locus → POST /api/annotate (the I6 path,
             via ctrl.annotateLocus). This is the click→comment that makes the criteria FUNCTION live; the
             OPERATE face stays separate (a control's own onClick → /api/act + the I3 approve path) — never
             blurred. FORM: built on the corpus .rhm-indicating chip vocabulary (tokens only, no literals);
             the amber [data-click-mode="annotate"] cue + this bar are the DEFAULT mode-signal (needs-tim). */}
          <AnnotateBar />
          {/* G-4 · THE SELF-BUILD WIRE'S OPERATOR DOOR. The missing FE caller for the decision→implementation
             wire (REPO-KNOWLEDGE D1): when the operator has indicated a ui:// element, this door lets them
             REQUEST A CHANGE to it → mints a build-intent (POST /api/intent-at, via ctrl.mintBuildIntent,
             carrying the derived scope + the X16 blast-radius) → shows the reach (the reused BlastRadiusReach
             ripple) → approve (/api/resolve). Point → ask → see-the-reach → approve. Sibling of AnnotateBar
             (same indicated-element surface area, the wire-blue signature). SAFE-BY-DEFAULT: mint + approve
             compose a PLAN; dispatch is inert/plan-mode unless deliberately armed (stated as honest static
             copy — the armed state is not served to the FE). The onDocClick capture excludes this subtree so
             clicking into it never overwrites the pointed target. */}
          <WireRequest />
          {/* L9 · reverse journey-recording (§21.7#2-reverse). The RECORD toggle + REPLAY picker: capture
             the operator's ordered ui:// click-path as a DISTINCT journey-record (steps appended in
             ctrl.indicate while recording), replay it by stepping the view through its addresses via the
             PRESERVED resolveUiTarget. Sits beside AnnotateBar (the indicated-element surface area). FORM:
             corpus .rhm-indicating chip vocabulary (tokens only). DISTINCT from the review-session walk. */}
          <JourneyBar />
        </div>
        {/* the right rail — Inspector + Inbox + Grow stacked in ONE scroll column (the .panel rail, as
           before). data-ui-ref="inspector" is on this scroll container (the resolveUiTarget keystone +
           the U7 scroll-into-view query it by that ref).
           F2: .as-sheet makes it a bottom-sheet (the 'inbox' tab) at <699px. */}
        <div className="as-panel as-sheet hud panel" data-ui-ref="inspector">
          <Inspector />
          {/* D2 · the COMPOSED address-help / altitude surface (REPO-KNOWLEDGE D2): when the operator INDICATES
             a ui:// element, "what can I do here?" leads the indicated-locus stack — the three legs of
             address_help (what-this-is · how-to-use · how-to-change) composed AT TIM'S ALTITUDE (plain-language
             howto leads; the mechanism — code/files/blast-radius — drills down on demand). EXPOSES the existing
             D1 composer (GET /api/address-help → Suite.address_help, NOT a parallel composer). Degrades cleanly
             per leg (G-53: many elements author no howto yet). Per-panel boundary (PRESERVE-LIST): a render-throw
             degrades to a contained card, never a white-screen. Renders nothing unless a ui:// locus is
             indicated, so it never clutters the rail; mounted BEFORE History because "what can I do here" is the
             primary indicated-locus question. */}
          <PanelErrorBoundary name="address-help">
            <AddressHelp />
          </PanelErrorBoundary>
          {/* L3 · addressed history (§21.7#1): when the operator INDICATES a ui:// element, its full
             addressed trajectory ("everything that happened here") shows here — navigable, grouped by kind
             (GET /api/address-history → Suite.address_view, the decision_view sid path untouched). Per-panel
             boundary (PRESERVE-LIST): a history render-throw degrades to a contained card, never a white-screen.
             Renders nothing unless a ui:// locus is indicated, so it never clutters the rail. */}
          <PanelErrorBoundary name="history">
            <History />
          </PanelErrorBoundary>
          {/* L5 · self-change locating (§21.7#5): when the operator INDICATES a ui:// element, "what did the
             SYSTEM change HERE?" shows beneath its history — the self-change audit log filtered to this
             element's code scope (GET /api/self-changes-at → Suite.self_changes_at), with a per-row revert
             that reuses the EXISTING operator-only /api/revert gate. Per-panel boundary (PRESERVE-LIST): a
             render-throw degrades to a contained card, never a white-screen. Renders nothing unless a ui://
             locus is indicated. */}
          <PanelErrorBoundary name="self-changes">
            <SelfChanges />
          </PanelErrorBoundary>
          {/* L6 · live-history / versions at an address (§21.7#6): when a node with a versioned OUTPUT
             address is SELECTED, the trail of values that address has HELD over time shows here — navigable,
             newest-first, the current version badged, each prior version fetchable by its surviving cas (GET
             /api/ref-versions → Suite.ref_versions → store.ref_history). A portal is a live window onto
             another address, so this surfaces the address its config.ref POINTS AT (where set_ref wrote the
             versions), not the portal's own. Per-panel boundary (PRESERVE-LIST): a render-throw degrades to a
             contained card, never a white-screen. Renders nothing unless a versioned node is selected. */}
          <PanelErrorBoundary name="versions">
            <Versions />
          </PanelErrorBoundary>
          <Inbox />
          <Grow />
          {/* F8: the fleet surface — the live model layer (model · kind · alive), addressed ui://models.
             Additive, stacked in the SAME right-rail scroll column as Inspector/Inbox/Grow so it inherits the
             responsive bottom-sheet behaviour at <699px. Per-panel boundary (PRESERVE-LIST item 1): a fleet
             render-throw degrades to a contained card, never a white-screen. */}
          <PanelErrorBoundary name="fleet">
            <Fleet />
          </PanelErrorBoundary>
        </div>
        {/* F2: the MOBILE NAV — a bottom tabbar (corpus .tabbar component) shown ONLY at <699px. It replaces
           the hidden rails: Canvas (board, no sheet) · Inbox (the inspector/inbox sheet) · RHM (chat sheet) ·
           Run. RUN here calls the SAME doRun() as the toolbar — U1 preserved (arrow-wrapped, no event passed),
           so the operator can always run at phone width (corpus tabbar names Run as the 4th tab). */}
        <nav className="tabbar" data-ui-ref="ui://tabbar">
          <a className={mobileTab === 'canvas' ? 'on' : ''} onClick={() => setMobileTab('canvas')}><span className="ic">▦</span>canvas</a>
          <a className={mobileTab === 'palette' ? 'on' : ''} onClick={() => setMobileTab('palette')}><span className="ic">＋</span>add</a>
          <a className={mobileTab === 'inbox' ? 'on' : ''} onClick={() => setMobileTab('inbox')}><span className="ic">▤</span>panel</a>
          <a className={mobileTab === 'rhm' ? 'on' : ''} onClick={() => setMobileTab('rhm')}><span className="ic">◈</span>rhm</a>
          {/* A2 (G-36): the ACTIVITY feed tab — the ambient trace gets a thumb-reachable home (its own
             bottom-sheet, the .rhm-template reveal). Sits between rhm and run. */}
          <a className={mobileTab === 'activity' ? 'on' : ''} onClick={() => setMobileTab('activity')}><span className="ic">≋</span>feed</a>
          <a onClick={() => ctrl.doRun()}><span className="ic">▶</span>run</a>
        </nav>
      </div>
      {/* Workshop is a full-viewport modal (position:fixed) — outside the grid so it covers everything. */}
      <Workshop />
      {/* A3 + E2-FE/GC3 · the CONSOLIDATED SETTINGS surface. A full-viewport modal (Workshop pattern — outside
         the grid, position:fixed) so it covers everything and works IDENTICALLY desktop + phone (no bottom-sheet
         competition). It is the ONE designed home for every config slot (modes/models/personas/RHM-config/voice),
         reading the SAME controller state the scattered RhmChat gear + Toolbar dial read (single source). Opened
         from the Toolbar gear (ctrl.openSettings). Per-panel boundary: a settings render-throw degrades to a
         contained card, never a white-screen — its own modal already covers the live canvas behind it. */}
      <PanelErrorBoundary name="settings">
        <Settings />
      </PanelErrorBoundary>
    </PanelErrorBoundary>
    </AppContext.Provider>
  )
}

export default function App() {
  return (
    <div style={{ position: 'fixed', inset: 0 }}>
      <Tldraw
        shapeUtils={[NodeShapeUtil]}
        // BUMP THIS whenever the NodeShape props schema changes — tldraw persists the store to
        // IndexedDB under this key and VALIDATES every record on load; a snapshot written by an older
        // schema (e.g. before `error` was added to the node props) fails with
        // `ValidationError: props.error: Expected string, got undefined` in TldrawEditorBeforeLoading,
        // which white-screens the canvas. Bumping the key makes tldraw ignore the stale snapshot and
        // rebuild from the backend (nodes/positions are backend-authoritative — reflects-never-owns —
        // so only the local camera resets). v2→v3: the interactive-surface merge added node.props.error.
        persistenceKey="company-canvas-v3"
        components={{ StylePanel: null, ActionsMenu: null, QuickActions: null }}
      >
        <Hud />
      </Tldraw>
    </div>
  )
}
