import {
  Tldraw, Editor, ShapeUtil, HTMLContainer, Rectangle2d, T,
  createShapeId, useEditor, useValue, stopEventPropagation, type TLBaseShape,
} from 'tldraw'
import { useState, useRef, useEffect, Component, lazy, Suspense } from 'react'

// Per-panel error boundary — a malformed/throwing panel definition renders a CONTAINED card,
// never white-screening the canvas (the operator's only control surface). Recovery is bridge-side.
class PanelErrorBoundary extends Component<{ name: string; children: any }, { err: boolean }> {
  constructor(p: any) { super(p); this.state = { err: false } }
  static getDerivedStateFromError() { return { err: true } }
  render() {
    return this.state.err
      ? <div className="op-panel op-err">⚠ panel “{this.props.name}” failed to render — revert it from the grow panel (↩).</div>
      : this.props.children
  }
}

// ---------------------------------------------------------------- api (proxied to the bridge)
const J = { 'Content-Type': 'application/json' }
const api = {
  graph: () => fetch('/api/graph').then(r => r.json()),
  types: () => fetch('/api/types').then(r => r.json()),
  // D4: run optionally FORCES a set of node ids past the memo gate (bypass cache). No body = normal run.
  run: (force?: string[]) =>
    fetch('/api/run', { method: 'POST', headers: J, body: JSON.stringify(force ? { force } : {}) }).then(r => r.json()),
  // A2: write a node's config (merge-not-replace, backend set_config). Returns fresh graph state.
  set: (node: string, config: any) =>
    fetch('/api/set', { method: 'POST', headers: J, body: JSON.stringify({ node, config }) }).then(r => r.json()),
  // B2: live model registry for a kind (chat|embed) — the source of truth, never a hardcoded list.
  models: (kind: string) => fetch('/api/models?kind=' + encodeURIComponent(kind)).then(r => r.json()),
  // C5: write a node's position back (sibling of config) after a drag — debounced, backend is truth.
  move: (node: string, x: number, y: number) =>
    fetch('/api/move', { method: 'POST', headers: J, body: JSON.stringify({ node, x, y }) }).then(r => r.json()),
  propose: (name: string, spec: string) =>
    fetch('/api/propose', { method: 'POST', headers: J, body: JSON.stringify({ name, spec }) }).then(r => r.json()),
  resolve: (id: string, choice: string, reason = '') =>
    fetch('/api/resolve', { method: 'POST', headers: J, body: JSON.stringify({ id, choice, reason }) }).then(r => r.json()),
  apply: (id: string) =>
    fetch('/api/apply', { method: 'POST', headers: J, body: JSON.stringify({ id }) }).then(r => r.json()),
  objectInfo: () => fetch('/api/object_info').then(r => r.json()),
  // registry-is-truth: WHAT EXISTS (node-types, models, modes, mode_directives, verbs, panels). The
  // presence-mode descriptions are read from capabilities().mode_directives — one backend source, no
  // parallel hardcoded copy on the surface.
  capabilities: () => fetch('/api/capabilities').then(r => r.json()),
  addNode: (type: string, config: any = {}) =>
    fetch('/api/node', { method: 'POST', headers: J, body: JSON.stringify({ type, config }) }).then(r => r.json()),
  connect: (e: any) =>
    fetch('/api/connect', { method: 'POST', headers: J, body: JSON.stringify(e) }).then(r => r.json()),
  del: (node: string) =>
    fetch('/api/delete-node', { method: 'POST', headers: J, body: JSON.stringify({ node }) }).then(r => r.json()),
  now: () => fetch('/api/now').then(r => r.json()),
  events: () => fetch('/api/events').then(r => r.json()),
  chat: (message: string, focus?: any) =>
    fetch('/api/chat', { method: 'POST', headers: J, body: JSON.stringify({ message, focus }) }).then(r => r.json()),
  chatHistory: () => fetch('/api/chat').then(r => r.json()),
  setMode: (mode: string) =>
    fetch('/api/mode', { method: 'POST', headers: J, body: JSON.stringify({ mode }) }).then(r => r.json()),
  rhmConfig: () => fetch('/api/rhm-config').then(r => r.json()),
  setRhmConfig: (updates: any) =>
    fetch('/api/rhm-config', { method: 'POST', headers: J, body: JSON.stringify(updates) }).then(r => r.json()),
  inbox: () => fetch('/api/inbox').then(r => r.json()),
  coa: (id: string) => fetch('/api/coa', { method: 'POST', headers: J, body: JSON.stringify({ id }) }).then(r => r.json()),
  // F2: route a node's RESULT to the decision surface — backend reads the output from live state
  // (client sends only the node id; canvas reflects-never-owns), surfaces it on the EXISTING inbox path.
  surfaceOutput: (node: string) =>
    fetch('/api/surface-output', { method: 'POST', headers: J, body: JSON.stringify({ node }) }).then(r => r.json()),
  react: () => fetch('/api/react', { method: 'POST' }).then(r => r.json()),
  lastChange: () => fetch('/api/last-change').then(r => r.json()),
  revert: (sha: string) => fetch('/api/revert', { method: 'POST', headers: J, body: JSON.stringify({ sha }) }).then(r => r.json()),
  panels: () => fetch('/api/panels').then(r => r.json()),
  voice: () => fetch('/api/voice').then(r => r.json()),
  stt: (blob: Blob) => fetch('/api/stt', { method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: blob }).then(r => r.json()),
  tts: (text: string) => fetch('/api/tts', { method: 'POST', headers: J, body: JSON.stringify({ text }) }).then(r => r.blob()),
  // C1: the UI-component registry (sibling of object_info) — the source of truth for what's addressable.
  uiInfo: () => fetch('/api/ui_info').then(r => r.json()),
  // B: the walkthrough/review session lifecycle. start makes its OWN session-graph (not graph-scoped);
  // current = the node at the cursor + its coa framing + its ui:// target; next opens the gate + advances.
  reviewStart: (item_ids: string[], mode = 'walkthrough') =>
    fetch('/api/review/start', { method: 'POST', headers: J, body: JSON.stringify({ item_ids, mode }) }).then(r => r.json()),
  reviewCurrent: (session: string) =>
    fetch('/api/review/current?session=' + encodeURIComponent(session)).then(r => r.json()),
  reviewNext: (session: string) =>
    fetch('/api/review/next', { method: 'POST', headers: J, body: JSON.stringify({ session }) }).then(r => r.json()),
  reviewStatus: (session: string) =>
    fetch('/api/review/status?session=' + encodeURIComponent(session)).then(r => r.json()),
  // D: the per-step verdict — operator-only. Session+position tag the verdict to its walk step (additive;
  // legacy id+choice+reason callers unchanged). Reflects-never-owns: the verdict goes THROUGH the gate.
  resolveStep: (id: string, choice: string, reason: string, session: string, position: number) =>
    fetch('/api/resolve', { method: 'POST', headers: J, body: JSON.stringify({ id, choice, reason, session, position }) }).then(r => r.json()),
}

const MODES = ['listening', 'text-only', 'background', 'focus', 'walkthrough', 'watch-and-react', 'decide-for-me', 'off']
// U11: the per-mode descriptions (so a newcomer can tell them apart in the dropdown). registry-is-truth:
// these come from capabilities().mode_directives (backend MODE_DIRECTIVES in runtime/suite.py is the ONE
// source) — read into Hud state at boot, NOT a parallel hardcoded copy. A mode missing from the snapshot
// renders an empty string (safe fallback), never a stale guess.

// ---------------------------------------------------------------- module-scoped shared registries
// The node SHAPE (rendered inside tldraw) cannot reach Hud-local React state, so the data it needs to
// draw ports must live at module scope. These are set ONCE on load (mirrors the `window.__editor` handle
// pattern already used for automation). They are READ truth from the backend, never canvas-owned.
let OINFO: any = {}                                   // type -> { ports:{inputs,outputs}, config_schema, kind }
let MODEL_OPTIONS: Record<string, string[]> = {}      // 'chat_models' | 'embed_models' -> live model id list
// C1: a drag from an output nub to an input nub COMMITS through this hook (Hud installs it). The shape
// only detects the gesture + endpoints; the CONNECTION round-trips /api/connect (backend type-checks,
// backend owns the edge) — the canvas reflects it, never owns it.
let CONNECT: (from_node: string, from_port: string, to_node: string, to_port: string) => void = () => {}
// the live drag-to-connect gesture, module-scope so the source-nub pointerdown and any target-nub
// pointerup share it across shape instances.
let DRAG_CONN: { from_node: string; from_port: string } | null = null
// D4: a per-node force-rerun affordance on the card bypasses the memo gate for just that node.
let FORCE_RUN: (node_id: string) => void = () => {}
// C1: the UI-component registry (from /api/ui_info) — READ truth, the source of what's addressable. The
// resolver validates ui:// targets against it (registry-is-truth: an unknown ref fails loud, never a
// silent no-op). Set ONCE on load (mirrors OINFO). ref -> {ref,kind,title,capabilities,domHandle,cameraRef}.
let UI_INFO: Record<string, any> = {}

// A2/B2: transform a node-type's config_schema ({key:{type,label,default,options_from?,options?,...}})
// into the flat field-defs PanelView renders. enum -> select; everything else -> input. options come from
// the LIVE registry (options_from) or an inline list — never hardcoded here.
function resolveOptions(f: any): string[] {
  if (f.options_from) return MODEL_OPTIONS[f.options_from] || []
  if (Array.isArray(f.options)) return f.options
  return []
}
function configSchemaToFields(schema: any): any[] {
  return Object.entries(schema || {}).map(([key, f]: [string, any]) => ({
    key,
    label: f.label || key,
    type: (f.type === 'enum' || f.options_from || Array.isArray(f.options)) ? 'select' : 'input',
    rawType: f.type,                                  // number|string|text|enum — drives value coercion
    options: resolveOptions(f),
    default: f.default,
  }))
}
// Coerce an edited form value back to its declared type before writing (the advisor's number/null trap):
// number fields must send a Number (not "0.7"); an emptied number preserves null rather than NaN.
function coerceConfigValue(field: any, raw: string): any {
  if (field.rawType === 'number') {
    if (raw === '' || raw == null) return null
    const n = Number(raw)
    return Number.isNaN(n) ? null : n
  }
  return raw
}

function relTime(iso?: string) {
  if (!iso) return ''
  const d = (Date.now() - new Date(iso).getTime()) / 1000
  if (d < 1) return 'now'
  if (d < 60) return `${Math.floor(d)}s`
  if (d < 3600) return `${Math.floor(d / 60)}m`
  return `${Math.floor(d / 3600)}h`
}

// Self-coded extensions — brain-authored .tsx, build-gated before promotion. LAZY-loaded (not eager):
// React.lazy defers each module's evaluation to RENDER time, inside its PanelErrorBoundary — so even a
// module-scope throw is caught and contained (a card), never white-screening the canvas (red-team B2).
const extensionLoaders = import.meta.glob('./extensions/*.tsx')   // path -> () => Promise<module> (lazy)
const extensions = Object.entries(extensionLoaders).map(([path, loader]) => ({
  name: (path.split('/').pop() || 'ext').replace('.tsx', ''),
  Comp: lazy(loader as () => Promise<{ default: any }>),
}))

// A brain-authored declarative panel, rendered generically. Render-prone work lives HERE (inside a
// component) so a malformed definition throws during PanelView's render and is caught by the
// PanelErrorBoundary wrapping it — never the parent Hud (which would white-screen the canvas).
function PanelView({ p, value, onSet }: { p: any; value: (f: any) => string; onSet: (f: any, v: string) => void }) {
  return (
    <div className="op-panel">
      <div className="op-title">{p.title}</div>
      {(p.fields || []).map((f: any) => (
        <div className="op-field" key={f.key}>
          <span className="op-label">{f.label || f.target}</span>
          {f.type === 'select'
            ? <select value={value(f)} onChange={e => onSet(f, e.target.value)}>
                {(f.options || []).map((o: string) => <option key={o} value={o}>{o}</option>)}
              </select>
            : <input defaultValue={value(f)} onBlur={e => onSet(f, e.target.value)} />}
        </div>
      ))}
      {(!p.fields || !p.fields.length) && <div className="muted">no fields</div>}
    </div>
  )
}

// WIRE-UI: a surfaced item is a BUILD-INTENT iff payload.intent === "build" (the wire's discriminator,
// runtime/suite.py is_build_intent). The wire surfaces FOUR shapes through this ONE flag — the initial
// intent, a launch/verify FAILURE re-queue, a SCOPE-OVERRUN re-queue, and (when the backend lane lands)
// the explicit surfaced-for-review — all distinguished by `status` + the presence of build_result / why /
// overrun, NOT a new field per shape. reflects-never-owns: we read these off the surfaced item the backend
// owns; we invent nothing.
function isBuildIntent(d: any): boolean {
  return !!d && (d.payload?.intent === 'build')
}
// WIRE-UI: map the backend's REAL status lane (governance.py REVIEW_STATUSES: inbox · presented ·
// responded · resolved · requeue · implemented) to an operator-legible build phase. There is NO
// `dispatched` status — dispatch sets `presented` (suite.py:1344) — so we read `presented` as
// "dispatched · running" (the autonomous `claude -p` build is in flight). Author-from-registry: every
// label here corresponds to a status the backend can actually emit.
function buildPhase(d: any): { label: string; cls: string } {
  const st = d.status || 'inbox'
  const r = d.payload?.build_result
  if (st === 'implemented') return { label: 'implemented ✓', cls: 'bi-done' }
  if (st === 'presented') return { label: 'dispatched · running…', cls: 'bi-running' }
  // a re-queued failure/overrun is distinguished by having RUN: a build_result, an overrun, or a
  // requeued_from back-reference. NOT by `why` — every build-intent carries a `why` from
  // surface_build_intent (suite.py:1251 `why or spec`), so keying on `why` would mislabel a fresh
  // awaiting intent as surfaced-back (caught in the by-use pass).
  if (r || d.payload?.overrun || d.payload?.requeued_from) return { label: 'surfaced back — needs you', cls: 'bi-back' }
  return { label: 'awaiting approval', cls: 'bi-inbox' }
}

// WIRE-UI · DEMONSTRATE-FIRST (operator steer): the operator is NOT a developer and will never read
// code — so a build's review must headline the WORKING OUTCOME, demonstrated, not a changed-files diff.
// deriveOutcome reads the build_result and produces (a) a plain-language "what you can now do" line and
// (b) — when the change is something we can drive the canvas to SHOW — a demonstrable node-type. A new
// node-type is the canonical demonstrable: a build whose changed files added a `nodes/<name>.py` makes a
// new node-type live, which we can place + run on the canvas so the operator JUDGES THE OUTCOME BY SEEING
// IT. When nothing is canvas-demonstrable we fall back to the plain-language summary (never a diff as the
// headline). reflects-never-owns: derived purely from the build_result the backend owns.
function deriveOutcome(d: any, liveTypes: string[]): { line: string; demoType: string | null } {
  const p = d.payload || {}
  const r = p.build_result
  const changed: string[] = (r?.changed_files) || []
  // a new node-type = a freshly-added nodes/<name>.py whose stem is now a LIVE registered type.
  const nodeFile = changed.find((f: string) => /(^|\/)nodes\/[^/]+\.py$/.test(f))
  const nodeType = nodeFile ? (nodeFile.split('/').pop() || '').replace('.py', '') : null
  const demoType = nodeType && liveTypes.includes(nodeType) ? nodeType : null
  if (demoType) return { line: `The “${demoType}” node is ready — place it on the canvas to see it work.`, demoType }
  // not canvas-demonstrable → a plain-language "what you can now do", taken from the build's own summary
  // (the brain's natural-language description of what it did), never the file list.
  if (r?.success && r?.summary) return { line: r.summary.split('\n')[0].slice(0, 240), demoType: null }
  if (r?.success) return { line: 'The build completed — review the outcome below.', demoType: null }
  return { line: '', demoType: null }
}

// WIRE-UI · DEMONSTRATE-FIRST: the build-intent review card. The HEADLINE is the working outcome in plain
// language + a "▷ show me" that drives the canvas to demonstrate the built thing actually doing its thing
// (a new node placed + runnable). The changed-files list is SECONDARY/for-the-record — collapsed behind a
// disclosure, never the headline (the operator judges the OUTCOME, not edits). Scope/class/phase frame it;
// a surfaced-back build shows its actionable WHY. Clicking the head compiles it via coa() (same as any
// inbox item). Pure presentation: every field is read from the surfaced item; PanelErrorBoundary-wrapped.
function BuildIntentCard({ d, onOpen, onDemonstrate, liveTypes }:
  { d: any; onOpen: (id: string) => void; onDemonstrate: (nodeType: string) => void; liveTypes: string[] }) {
  const [showRecord, setShowRecord] = useState(false)
  const p = d.payload || {}
  const phase = buildPhase(d)
  const result = p.build_result
  const changed: string[] = (result?.changed_files) || p.overrun || []
  const outcome = deriveOutcome(d, liveTypes)
  return (
    <div className={'bi-card ' + phase.cls} data-ui-ref={'build-intent'}>
      <div className="bi-head" onClick={() => onOpen(d.id)} title="compile this decision to a value-choice ↗">
        <span className="bi-tag">⚙ build-intent</span>
        <span className={'bi-phase ' + phase.cls}>{phase.label}</span>
      </div>
      <div className="bi-meta">
        <span className="bi-class" title="declared consequence class — its governance posture decides whether it auto-runs or surfaces">
          {p.consequence_class || 'decision_build'}</span>
        <span className="bi-scope" title="the declared scope — paths a verified build is allowed to touch (empty = deny-all)">
          scope: {(p.scope && p.scope.length) ? p.scope.join(', ') : '∅ (deny-all)'}</span>
      </div>
      {/* the INTENT (what was asked) — shown for an awaiting/running build (no terminal phase yet). */}
      {(phase.cls === 'bi-inbox' || phase.cls === 'bi-running') && (p.spec || p.why) && <div className="bi-spec">{p.spec || p.why}</div>}
      {/* DEMONSTRATE-FIRST · gated on the backend LIFECYCLE PHASE, NOT the subprocess exit code. Only a
          CLOSED build (status==='implemented' → bi-done) headlines the working outcome + offers the "show
          me" demonstration. This is the load-bearing discriminator: a build can have build_result.success
          ===true and STILL be surfaced-back (a scope-overrun ran + changed files = success true; a
          verify-fail-no-op = success true, no changes) — those are NOT done, must not wear the "done"
          headline, and must not offer a (bogus) demo. status===implemented is the backend's only
          closed-and-done signal (author-from-registry). */}
      {phase.cls === 'bi-done' && (
        <div className="bi-outcome">
          <div className="bi-outcome-head">✓ done — here is what you can now do</div>
          {outcome.line && <div className="bi-outcome-line">{outcome.line}</div>}
          {outcome.demoType && (
            <button className="b sm bi-demo" title={`place a ${outcome.demoType} node on the canvas and see it run`}
              onClick={() => onDemonstrate(outcome.demoType!)}>▷ show me “{outcome.demoType}” working</button>
          )}
        </div>
      )}
      {/* SURFACED BACK (bi-back: scope-overrun / verify-fail / crashed — with OR without a build_result):
          lead with the plain-language reason it needs the operator, never a diff, never a demo. Overrun-
          aware wording (an overrun build DID run but went out of bounds vs one that didn't complete). The
          `why` is the actionable reason and is ALWAYS present on a bi-back item (suite.py / resurface_crashed
          set it for fail/overrun/crash). */}
      {phase.cls === 'bi-back' && (
        <div className="bi-outcome bi-outcome-bad">
          <div className="bi-outcome-head bad">{p.overrun ? '⚠ the build went outside its declared scope — it needs you' : '✕ the build did not complete — it needs you'}</div>
          {p.why && <div className="bi-outcome-line">{p.why}</div>}
        </div>
      )}
      {/* SECONDARY / FOR-THE-RECORD: the changed-files list + raw summary, COLLAPSED by default. The
          operator never has to read edits to review; this is the audit trail, available on demand. */}
      {result && (changed.length > 0 || result.summary) && (
        <div className="bi-record">
          <div className="bi-record-toggle" onClick={() => setShowRecord(s => !s)}
            title="the technical record — changed files + the build's own log (for reference, not the review)">
            {showRecord ? '⌄' : '⌃'} for the record {p.overrun ? `· ⚠ ${changed.length} file(s) outside scope` : changed.length ? `· ${changed.length} file(s) changed` : ''}
          </div>
          {showRecord && (
            <>
              {changed.length > 0 && (
                <div className="bi-files">
                  {changed.map((f: string) => <div key={f} className={'bi-file' + (p.overrun ? ' over' : '')}>{f}</div>)}
                </div>
              )}
              {result.summary && <pre className="bi-summary">{result.summary}</pre>}
              {result.permission_mode && <div className="bi-perm" title="the claude -p permission mode this build ran under">ran under: {result.permission_mode}</div>}
            </>
          )}
        </div>
      )}
    </div>
  )
}

// A2/A4: the editable node inspector form. Generic for EVERY node-type — fields come from the type's
// config_schema (the single source); values from the node's live config. enum/options → a <select>
// (model dropdowns fill from the live registry via options_from); everything else → an <input>. An edit
// commits through api.set (merge), then the parent refreshes. Wrapped by PanelErrorBoundary at the call
// site so a malformed schema degrades to a contained card, never white-screening the control surface.
function NodeConfigForm({ nodeType, config, onSet }:
  { nodeType: string; config: any; onSet: (key: string, value: any) => void }) {
  const schema = OINFO[nodeType]?.config_schema || {}
  const fields = configSchemaToFields(schema)
  if (!fields.length) return <div className="muted">this node-type has no configurable fields.</div>
  return (
    <div className="cfg-form">
      {fields.map(f => {
        const cur = config && config[f.key] != null ? config[f.key] : f.default
        return (
          <div className="op-field" key={f.key}>
            <span className="op-label">{f.label}</span>
            {f.type === 'select'
              ? <select value={cur == null ? '' : String(cur)} onChange={e => onSet(f.key, coerceConfigValue(f, e.target.value))}>
                  {/* surface the current value even if it isn't in the live option list (fail-loud, no silent drop) */}
                  {cur != null && !f.options.includes(String(cur)) && <option value={String(cur)}>{String(cur)} (current)</option>}
                  {f.options.length === 0 && <option value="">(no registered options)</option>}
                  {f.options.map(o => <option key={o} value={o}>{o}</option>)}
                </select>
              : <input
                  type={f.rawType === 'number' ? 'number' : 'text'}
                  defaultValue={cur == null ? '' : String(cur)}
                  onBlur={e => onSet(f.key, coerceConfigValue(f, e.target.value))}
                  onKeyDown={e => { if (e.key === 'Enter') (e.target as HTMLInputElement).blur() }}
                />}
          </div>
        )
      })}
    </div>
  )
}

// ---------------------------------------------------------------- the node shape (one generic kind)
type NodeShape = TLBaseShape<'node', {
  w: number; h: number; nodeId: string; nodeType: string; kind: string
  status: string; output: string; address: string; ref: string; layer: string
}>

const shapeIdFor = (nodeId: string) => createShapeId('n-' + nodeId)

// Per-port vertical placement — shared by the nub render (CSS top) AND the Edges overlay (page-space
// y), so a wire lands exactly on its port. Ports are evenly spread across the card height (NODE_H).
const NODE_H = 130
function portTop(i: number, n: number) {
  return ((i + 1) / (n + 1)) * NODE_H
}

class NodeShapeUtil extends ShapeUtil<NodeShape> {
  static override type = 'node' as const
  static override props = {
    w: T.number, h: T.number, nodeId: T.string, nodeType: T.string, kind: T.string,
    status: T.string, output: T.string, address: T.string, ref: T.string, layer: T.string,
  }
  getDefaultProps(): NodeShape['props'] {
    return { w: 240, h: 130, nodeId: '', nodeType: '', kind: 'process', status: 'idle', output: '', address: '', ref: '', layer: 'authored' }
  }
  getGeometry(shape: NodeShape) {
    return new Rectangle2d({ width: shape.props.w, height: shape.props.h, isFilled: true })
  }
  override canResize = () => false
  override hideRotateHandle = () => true

  component(shape: NodeShape) {
    const editor = useEditor()
    const zoom = useValue('zoom', () => editor.getZoomLevel(), [editor])   // semantic zoom
    const p = shape.props
    const expanded = zoom > 0.5
    const hasOut = p.output != null && String(p.output) !== ''
    const isPortal = p.nodeType === 'portal'
    // C1: ports come from the registry (OINFO), so a new node-type gets nubs with zero per-type code.
    const ports = OINFO[p.nodeType]?.ports || { inputs: {}, outputs: {} }
    const inputs = Object.keys(ports.inputs || {})
    const outputs = Object.keys(ports.outputs || {})
    // D5: legible cached-vs-ran — a cache hit must SAY so (fail-loud against "nothing happened").
    // U2: a stuck node says so distinctly (not the neutral "idle/no output"); the reason is generic and
    // honest — the scheduler's "stuck" means an input address never resolved (no per-node error string).
    const statusLabel = p.status === 'ran' ? 'ran' : p.status === 'cached' ? 'cached ↺'
      : p.status === 'stuck' ? 'stuck — an input never resolved' : p.status
    const isStuck = p.status === 'stuck'

    // A nub. An OUTPUT nub starts a connect gesture: stopPropagation (so tldraw doesn't read it as a
    // node-drag/select) + setPointerCapture (so we keep the pointer through the drag). Because capture
    // redirects the pointer-up back to the SOURCE element, we resolve the drop target with
    // elementFromPoint and read its data-node/data-port — NOT the input nub's own onPointerUp (which
    // never fires under capture). Each input nub carries data-* so the source can find it. The wire
    // COMMITS through /api/connect — the backend type-checks and owns the edge; the canvas only reflects.
    const nub = (side: 'in' | 'out', port: string, i: number, n: number) => {
      const top = portTop(i, n)
      const common: any = { className: 'port-nub ' + side, style: { top },
        title: `${side === 'in' ? 'input' : 'output'} · ${port}`,
        children: <span className="port-label">{port}</span> }
      if (side === 'in') {
        // a drop target — identify it for elementFromPoint resolution
        return <div {...common} key={side + port} data-innode={p.nodeId} data-inport={port} />
      }
      return (
        <div {...common} key={side + port}
          onPointerDown={e => {
            stopEventPropagation(e)                              // tldraw-aware: don't let it read this as node-drag/select
            ;(e.currentTarget as HTMLElement).setPointerCapture?.(e.pointerId)
            DRAG_CONN = { from_node: p.nodeId, from_port: port }
          }}
          onPointerUp={e => {
            stopEventPropagation(e)
            ;(e.currentTarget as HTMLElement).releasePointerCapture?.(e.pointerId)
            if (DRAG_CONN) {
              // the input nub under the cursor at drop (capture redirected the up to the source)
              const el = document.elementFromPoint(e.clientX, e.clientY) as HTMLElement | null
              const hit = el?.closest('.port-nub.in') as HTMLElement | null
              const toNode = hit?.getAttribute('data-innode')
              const toPort = hit?.getAttribute('data-inport')
              if (toNode && toPort && toNode !== DRAG_CONN.from_node) {
                CONNECT(DRAG_CONN.from_node, DRAG_CONN.from_port, toNode, toPort)
              }
            }
            DRAG_CONN = null
          }}
        />
      )
    }
    return (
      <HTMLContainer>
        <div className={`node-card ${p.status} layer-${p.layer}` + (isPortal ? ' portal' : '')}>
          <div className="node-bar">
            <span className="node-dot" />
            <span className="node-type">{isPortal ? '⊕ portal' : p.nodeType}</span>
            <span className="node-kind">{p.layer === 'system' ? 'system' : p.kind}</span>
          </div>
          {isPortal && <div className="node-ref">live view → {p.ref}</div>}
          {expanded && (
            <div className="node-body">
              {/* U2: a stuck node is visibly FAILED with a reason — never the neutral "not yet resolved". */}
              {isStuck
                ? <div className="node-out stuck">⚠ stuck — an input address never resolved (wire its inputs, or run upstream first)</div>
                : hasOut
                  ? <div className="node-out">{String(p.output)}</div>
                  : <div className="node-out empty">{isPortal ? 'window onto an unresolved address' : 'no output — not yet resolved'}</div>}
            </div>
          )}
          {expanded && (
            <div className="node-addr">
              <span className="na-txt">{p.address}{p.status !== 'idle' ? ` · ${statusLabel}` : ''}</span>
              {/* D4: force re-run THIS node past the memo gate */}
              <span className="na-force" title="force re-run this node (bypass the memo cache)"
                onPointerDown={e => { stopEventPropagation(e); FORCE_RUN(p.nodeId) }}>↻</span>
            </div>
          )}
          {/* C1: port nubs — inputs left, outputs right, one per registered port (y-offset by index) */}
          {inputs.map((port, i) => nub('in', port, i, inputs.length))}
          {outputs.map((port, i) => nub('out', port, i, outputs.length))}
        </div>
      </HTMLContainer>
    )
  }
  indicator(shape: NodeShape) {
    return <rect width={shape.props.w} height={shape.props.h} rx={4} />
  }
}

// ---------------------------------------------------------------- load / refresh graph -> shapes
// C5-fe: update-or-create-or-PRUNE (mirrors refresh()). The backend `n.position` is the SINGLE source of
// truth for layout — so we never invent coordinates and never let tldraw's IndexedDB own the layout.
//  (a) existing shape  → update it INCLUDING position (from n.position)
//  (b) missing shape   → create it AT n.position (not 150+i*300)
//  (c) orphan shape    → PRUNE it (nodeId no longer in g.nodes) — so delete still works (no ghost shapes)
// All store writes here are PROGRAMMATIC; the drag-listener filters to source:'user', so these do NOT
// emit spurious /api/move calls (the write-back feedback-loop trap).
async function loadGraph(editor: Editor) {
  const g = await api.graph()
  const wasEmpty = editor.getCurrentPageShapes().filter(s => s.type === 'node').length === 0
  const live = new Set<string>()
  g.nodes.forEach((n: any, i: number) => {
    live.add(n.id)
    const id = shapeIdFor(n.id)
    const pos = n.position || { x: 150 + i * 300, y: 220 }   // fallback only if backend gave none
    const props = {
      w: 240, h: NODE_H, nodeId: n.id, nodeType: n.type, kind: n.kind || 'process',
      status: n.status || 'idle', output: n.output == null ? '' : String(n.output), address: n.address || '',
      ref: (n.config && n.config.ref) || '', layer: n.layer || 'authored',
    }
    if (editor.getShape(id)) {
      editor.updateShape<NodeShape>({ id, type: 'node', x: pos.x, y: pos.y, props })   // position from backend
    } else {
      editor.createShape<NodeShape>({ id, type: 'node', x: pos.x, y: pos.y, props })
    }
  })
  // (c) prune orphans — a shape whose backend node is gone (deleted). Without this, delete leaves a ghost.
  const orphans = editor.getCurrentPageShapes()
    .filter(s => s.type === 'node' && !live.has((s as NodeShape).props.nodeId))
    .map(s => s.id)
  if (orphans.length) editor.deleteShapes(orphans)
  // (c) fit only when the page started empty — never on every mutation (that wiped operator layout).
  if (wasEmpty && g.nodes.length) editor.zoomToFit({ animation: { duration: 200 } })
  return g
}

async function refresh(editor: Editor, state?: any) {
  const g = state || await api.graph()
  g.nodes.forEach((n: any) => {
    const id = shapeIdFor(n.id)
    if (editor.getShape(id)) {
      const pos = n.position
      editor.updateShape<NodeShape>({
        id, type: 'node',
        ...(pos ? { x: pos.x, y: pos.y } : {}),
        props: { status: n.status || 'idle', output: n.output == null ? '' : String(n.output), layer: n.layer || 'authored' },
      })
    }
  })
  return g
}

// ---------------------------------------------------------------- edges overlay (reactive, screen-space)
// C1: edges carry from_port/to_port (backend-owned). Each wire anchors on the EXACT port (y-offset by the
// port's index among its node's ports), not the shape mid — so it lands on the nub it represents.
function Edges({ edges }: { edges: { from: string; from_port?: string; to: string; to_port?: string }[] }) {
  const editor = useEditor()
  const lines = useValue('edges', () => {
    editor.getCamera()                                   // subscribe to camera + zoom changes
    const z = editor.getZoomLevel()
    // page-space y of a named port on a node (mirrors portTop in the shape so wire ↔ nub line up).
    const portY = (nodeType: string, side: 'inputs' | 'outputs', port?: string) => {
      const list = Object.keys(OINFO[nodeType]?.ports?.[side] || {})
      const i = port ? list.indexOf(port) : -1
      if (i < 0) return NODE_H / 2                        // fallback: shape mid
      return portTop(i, list.length)
    }
    return edges.map(e => {
      const aShape = editor.getShape(shapeIdFor(e.from)) as NodeShape | undefined
      const bShape = editor.getShape(shapeIdFor(e.to)) as NodeShape | undefined
      const a = editor.getShapePageBounds(shapeIdFor(e.from))
      const b = editor.getShapePageBounds(shapeIdFor(e.to))
      if (!a || !b || !aShape || !bShape) return null
      const aType = aShape.props.nodeType, bType = bShape.props.nodeType
      const ay = a.minY + portY(aType, 'outputs', e.from_port) * z   // page→screen scales by zoom
      const by = b.minY + portY(bType, 'inputs', e.to_port) * z
      const p1 = editor.pageToScreen({ x: a.maxX, y: ay })
      const p2 = editor.pageToScreen({ x: b.minX, y: by })
      return { x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y }
    }).filter(Boolean) as any[]
  }, [editor, edges])
  return (
    <svg style={{ position: 'absolute', inset: 0, pointerEvents: 'none', zIndex: 200, width: '100%', height: '100%' }}>
      {lines.map((l, i) => {
        const mx = (l.x1 + l.x2) / 2
        return <path key={i} d={`M ${l.x1} ${l.y1} C ${mx} ${l.y1} ${mx} ${l.y2} ${l.x2} ${l.y2}`}
          fill="none" stroke="#2f6b59" strokeWidth={1.5} />
      })}
    </svg>
  )
}

// ---------------------------------------------------------------- the HUD (toolbar · inspector · grow · workshop)
function Hud() {
  const editor = useEditor()
  const [edges, setEdges] = useState<{ from: string; from_port?: string; to: string; to_port?: string }[]>([])
  const [running, setRunning] = useState(false)
  // U4: a legible run-error surface. A real api.run()/refresh() rejection (network, a node that RAISED
  // and failed the whole run) sets this; the toolbar shows it with a retry, and it always clears `running`
  // (no dead-end latch, no uncaught rejection). null = no error.
  const [runError, setRunError] = useState<string | null>(null)
  // U2: the most-recent run's STUCK node ids. The scheduler reports "stuck" (an input address that never
  // resolved) ONLY on the emitted `run` event — the per-node /api/graph status is only ran|cached|idle and
  // would OVERWRITE any stuck paint on the next loadGraph. So we hold stuck here (from the run event /
  // run result) and re-apply it onto the shapes AFTER each loadGraph; a node clears the moment it next runs.
  const stuckNodes = useRef<Set<string>>(new Set())
  // U3: when a run is in flight, the wall-clock start (ms) so the toolbar can show elapsed during the
  // ~20-27s waits. The backend emits NO per-node progress signal (one `run` event AFTER the whole run
  // returns), so "which exact node is computing now" is not derivable in this lane — see report notes.
  const [runStartedAt, setRunStartedAt] = useState<number | null>(null)
  const [runElapsed, setRunElapsed] = useState(0)
  const [types, setTypes] = useState<string[]>([])
  const [gname, setGname] = useState('')
  const [gspec, setGspec] = useState('')
  const [surf, setSurf] = useState<any>(null)
  const [growMsg, setGrowMsg] = useState('the brain writes it · you approve · it goes live.')
  const [workshop, setWorkshop] = useState<any>(null)
  const [oinfo, setOinfo] = useState<any>({})
  // registry-is-truth: per-mode descriptions read from capabilities().mode_directives (backend is the one
  // source). Default {} → every lookup falls back to '' until the snapshot loads (safe, never a stale guess).
  const [modeDesc, setModeDesc] = useState<Record<string, string>>({})
  const [notice, setNotice] = useState('')
  const [gid, setGid] = useState('codebase')
  const [layerView, setLayerView] = useState(0)   // 0 all · 1 origin only · 2 system only
  const [now, setNow] = useState<any>(null)
  const [events, setEvents] = useState<any[]>([])
  const [chat, setChat] = useState<any[]>([])
  const [chatMsg, setChatMsg] = useState('')
  const [chatBusy, setChatBusy] = useState(false)
  const [cfg, setCfg] = useState<any>({ model: '', persona: '' })
  const [cfgOpen, setCfgOpen] = useState(false)
  // U12: the /api/inbox payload is { live_escalations:[…], resolved_for_you:[…], batched:{action:[ids]},
  // counts:{escalations,resolved} } (suite.inbox_lanes). `batched` is a SUBSET-grouping of live_escalations
  // (same items, grouped by action, only themes with >1) — NOT a third disjoint lane. We render the two
  // real lanes (live grouped by action as visual sub-groups; resolved-for-you as a collapsible group).
  const [inbox, setInbox] = useState<any>({ live_escalations: [], resolved_for_you: [], batched: {}, counts: { escalations: 0, resolved: 0 } })
  const [showResolved, setShowResolved] = useState(false)   // U12: resolved-for-you collapsed by default (it needn't be worked)
  const [drill, setDrill] = useState(false)
  const [reason, setReason] = useState('')
  const [lastChange, setLastChange] = useState<any>(null)
  const [panels, setPanels] = useState<any[]>([])
  const [recording, setRecording] = useState(false)
  const recorderRef = useRef<MediaRecorder | null>(null)
  // A2/A4: the selected node's live config (from /api/graph), keyed by nodeId — the inspector reads it
  // here, NOT off the tldraw shape props (which carry no config). Refreshed on every graph load.
  const configByNode = useRef<Record<string, any>>({})
  const [configTick, setConfigTick] = useState(0)   // bump to re-render the inspector form after a write
  // C5: per-node debounce timers for drag-end → /api/move (one write per settle, not per pointermove).
  const moveTimers = useRef<Record<string, any>>({})
  const streamSeq = useRef<number>(-1)              // G2: highest seq the client has seen (EventSource cursor)
  // B-frontend: the active review session — null when no walk is running. Holds the LIVE current step
  // ({session,cursor,total,item,framing,raw,ui_target,done}). The card renders from this; the SSE
  // review.advance event refreshes it; reflects-never-owns (the backend session is authoritative).
  const [session, setSession] = useState<any>(null)
  const sessionRef = useRef<any>(null)              // mirror for the openStream closure (set once, never re-bound)
  const [wtReason, setWtReason] = useState('')      // the step's reject/comment WHY (captured into the verdict)
  const [voiceOn, setVoiceOn] = useState(true)      // F3: voice|text toggle — voice-first, falls back to text
  const [wtSpoke, setWtSpoke] = useState('')        // last voice status line for the card (speaking/heard/fell back)
  const spokenFor = useRef<string>('')              // F1: which (session:cursor) we've already spoken — speak ONCE per step
  // CONCURRENCY GUARD: /api/review/next and /api/resolve framing take ~20s; an operator who clicks, sees
  // nothing, and clicks again would issue CONCURRENT requests that desync the backend cursor (Next) or
  // record two verdicts (respond). wtBusy DISABLES Next + every respond control while a request is in
  // flight (the visible/UX half). wtBusyRef is the LOAD-BEARING half: a rapid double-click can fire two
  // handlers before React commits the disabled re-render, so we gate on the ref synchronously at entry —
  // one click = one request, guaranteed. Cleared in `finally` so an error re-enables (never a dead end).
  const [wtBusy, setWtBusy] = useState(false)
  const wtBusyRef = useRef(false)
  sessionRef.current = session

  // Merge events by SEQ into the current list — an event already present (same seq) is never duplicated,
  // regardless of source (initial /api/events backlog · the SSE ?since= backlog · reconnect replay · a
  // poll() re-fetch). This makes `key={e.seq}` inherently unique and kills the "two children with the
  // same key" render-loop. Sorted ascending; capped at the last 200.
  function mergeEvents(setter: typeof setEvents, incoming: any[]) {
    setter(prev => {
      const bySeq = new Map<number, any>()
      for (const e of prev) if (e && e.seq != null) bySeq.set(e.seq, e)
      for (const e of incoming) if (e && e.seq != null) bySeq.set(e.seq, e)
      // newest-first (matches the backend's /api/events order + the activity-feed reading); keep newest 200
      return Array.from(bySeq.values()).sort((a, b) => b.seq - a.seq).slice(0, 200)
    })
  }
  async function poll() {
    // NOTE: poll() MERGES events (never replaces) so it can't reintroduce a seq the stream already showed.
    try { setNow(await api.now()); mergeEvents(setEvents, await api.events()); setInbox(await api.inbox()); setLastChange(await api.lastChange()); setPanels(await api.panels()) } catch { /* bridge transient */ }
  }
  async function openCoa(id: string) {
    setGrowMsg('compiling the decision into a value-choice…')
    const c = await api.coa(id)            // decision-compiler UP
    setSurf({ id: c.id, name: c.raw?.name, code: c.raw?.code, coa: c.framing }); setDrill(false)
  }

  // mirror the latest graph's per-node config into the ref the inspector reads (A2/A4). Only bump the
  // re-render tick when the config actually CHANGED — so an unrelated live event (move/run) during an
  // edit doesn't re-mount the form and drop an in-progress keystroke (the uncontrolled inputs settle on blur).
  function syncConfig(g: any) {
    const m: Record<string, any> = {}
    ;(g.nodes || []).forEach((n: any) => { m[n.id] = n.config || {} })
    const changed = JSON.stringify(m) !== JSON.stringify(configByNode.current)
    configByNode.current = m
    if (changed) setConfigTick(t => t + 1)
  }

  // load once, then go LIVE via the event stream (G2) — no 2.5s polling timer.
  useState(() => {
    ;(window as any).__editor = editor   // automation/debug handle
    // C1: install the connect hook — a nub-drag commits the wire through /api/connect (backend owns it).
    CONNECT = (fn, fp, tn, tp) => { void doConnect(fn, fp, tn, tp) }
    // D4: install the per-node force-rerun hook.
    FORCE_RUN = (nid) => { void doRun([nid]) }
    ;(async () => {
      // B2: live model lists FIRST (the source of truth) so config_schema dropdowns resolve immediately.
      try { MODEL_OPTIONS = { chat_models: await api.models('chat'), embed_models: await api.models('embed') } } catch { /* */ }
      OINFO = await api.objectInfo(); setOinfo(OINFO)      // C1: ports/schema reachable by the shape + Edges
      try { UI_INFO = await api.uiInfo() } catch { /* the registry is the source of truth for ui:// targets */ }   // C1: UI-component registry
      // registry-is-truth: pull the per-mode directives from capabilities() (backend MODE_DIRECTIVES is the
      // ONE source) so the presence dropdown shows backend truth, not a parallel hardcoded copy.
      try { const caps = await api.capabilities(); setModeDesc(caps?.mode_directives || {}) } catch { /* dropdown still lists modes; descriptions empty until reachable */ }
      const g = await loadGraph(editor); setEdges(g.edges || []); setGid(g.id); syncConfig(g)
      if ((g.nodes || []).length) setTimeout(fitGraph, 120)   // U6: chrome-aware fit on first load (defer so shapes are laid out)
      setTypes(await api.types())
      setChat(await api.chatHistory())
      setCfg(await api.rhmConfig())
      const evs = await api.events(); mergeEvents(setEvents, evs)
      streamSeq.current = evs.reduce((m: number, e: any) => Math.max(m, e.seq ?? -1), -1)  // cursor = last seen
      setNow(await api.now()); setInbox(await api.inbox()); setLastChange(await api.lastChange()); setPanels(await api.panels())
      // S7c (same-device resume): a persisted session id rehydrates the walk at the SAME cursor on reload /
      // SSE-drop. The backend session is server-authoritative; we just re-read present_current. (True
      // cross-device phone resume needs the backend to expose the active session id — a lane-Q surface.)
      try {
        const sid = localStorage.getItem('company-review-session')
        if (sid) {
          const s = await api.reviewCurrent(sid)
          if (s && !s.error) setSession(s)
          else localStorage.removeItem('company-review-session')   // stale/closed — don't resurface a dead walk
        }
      } catch { /* */ }
      openStream()                                        // G2: replaces setInterval(poll, 2500)
    })()
    // C5: drag-end write-back. The {source:'user'} filter narrows to operator gestures; the LOAD-BEARING
    // loop-breaker is the equality guard below (from.x/y === to.x/y → skip): loadGraph re-writing the
    // backend position to the SAME value produces no x/y delta, so no /api/move is emitted (do not remove
    // that guard trusting the source filter alone). Debounced per-shape: a drag is ONE /api/move, not many.
    const unlisten = editor.store.listen((entry) => {
      for (const rec of Object.values(entry.changes.updated)) {
        const [from, to]: any = rec as any
        if (!to || to.typeName !== 'shape' || to.type !== 'node') continue
        if (from && from.x === to.x && from.y === to.y) continue   // only POSITION changes write a move
        const nid = (to.props as any).nodeId; if (!nid) continue
        const x = to.x, y = to.y
        clearTimeout(moveTimers.current[nid])
        moveTimers.current[nid] = setTimeout(() => { void api.move(nid, x, y) }, 350)
      }
    }, { source: 'user', scope: 'document' })
    return unlisten
  })

  // G2: the live surface — one EventSource replaces the 2.5s poll. Each event is dispatched BY KIND to the
  // exact refresh the timer used to do blindly. Connect with ?since=<cursor> so we don't replay history.
  function openStream() {
    const since = streamSeq.current
    const es = new EventSource('/api/stream?since=' + since)
    es.onmessage = async (m) => {
      let ev: any; try { ev = JSON.parse(m.data) } catch { return }
      // Always merge the event into the log by SEQ (mergeEvents dedupes), so the log can NEVER hold two
      // children with the same key — even when the initial /api/events backlog, the SSE ?since= backlog,
      // a reconnect replay, and poll() re-fetches all overlap (this was the render-loop root cause).
      mergeEvents(setEvents, [ev])
      // The high-water gate gates DISPATCH (not the log): an event we've already acted on must not
      // re-trigger loadGraph/poll on a reconnect replay. Only genuinely-new seqs drive a refresh.
      if (ev.seq != null && ev.seq <= streamSeq.current) return
      if (ev.seq != null) streamSeq.current = ev.seq
      const k = ev.kind
      // structural changes → reload the graph (positions/edges/nodes/status)
      if (k === 'run' || k === 'create' || k === 'connect' || k === 'delete' || k === 'move') {
        // U2: a `run` event carries the scheduler's stuck/ran arrays directly — fold it in BEFORE the
        // repaint so the stuck overlay survives the loadGraph that follows (which only knows ran|cached|idle).
        if (k === 'run') applyStuckFromEvents([ev])
        const g = await loadGraph(editor); setEdges(g.edges || []); syncConfig(g)
        paintStuck()   // U2: re-apply stuck after loadGraph reset statuses to ran|cached|idle
        try { setNow(await api.now()) } catch { /* */ }
      } else if (k === 'mode' || k === 'config') {
        try { setNow(await api.now()); setCfg(await api.rhmConfig()) } catch { /* */ }
      } else if (k === 'ask' || k === 'reject' || k === 'resolve' || k === 'apply' || k === 'grow' || k === 'revert' || k.startsWith('decision.')) {
        // WIRE-UI: the decision→implementation wire emits `decision.*` events (intent · dispatch ·
        // implemented · verify · deferred · crashed · surfaced_for_review). NONE of them carry a
        // companion `ask` (unlike surface_review), so without this branch a surfaced build-intent, a
        // dispatch start, or an `implemented` close would fall into the final `else` (setNow only) and
        // the inbox/build-intent surface would go STALE until an unrelated event. startsWith('decision.')
        // (not an enumerated list) so the NEW `decision.surfaced_for_review` kind is handled the moment
        // the backend lane emits it — author-from-registry: we react to the kind family, invent nothing.
        // The deferred queue reads from the activity log (decision.deferred is event-only, no inbox item),
        // and the events already auto-merged at the top of onmessage — so this just refreshes the inbox+now.
        try { setInbox(await api.inbox()); setNow(await api.now()); setLastChange(await api.lastChange()); setPanels(await api.panels()) } catch { /* */ }
      } else if (k === 'chat' || k === 'react') {
        try { setChat(await api.chatHistory()) } catch { /* */ }
      } else if (k === 'review.advance' || k === 'review.start') {
        // B-frontend: the walk advanced server-side (this event used to fall into `else`). Refresh the card
        // from present_current IF it's OUR session — reflects-never-owns (the backend session is truth).
        if (ev.session && sessionRef.current && ev.session === sessionRef.current.session) {
          await refreshSession(ev.session)
        }
      } else {
        try { setNow(await api.now()) } catch { /* */ }
      }
    }
    es.onerror = () => { /* EventSource auto-reconnects; Last-Event-ID gives gapless resume */ }
  }

  async function reload() { const g = await loadGraph(editor); setEdges(g.edges || []); syncConfig(g); paintStuck(); await poll(); await maybeReact() }
  // U6: fit the graph but PAD for the fixed chrome so no node tucks under the palette/inspector/toolbar/
  // activity/rhm. zoomToBounds(bounds, {inset}) only insets SYMMETRICALLY — our panels are asymmetric — so
  // instead we EXPAND the content bounds by each panel's screen extent (converted to page units via zoom)
  // and fit THAT padded box. Pure view (owns no node data). Panel rects mirror app.css fixed positions.
  function fitGraph() {
    const shapes = editor.getCurrentPageShapes().filter(s => s.type === 'node')
    if (!shapes.length) { editor.zoomToFit({ animation: { duration: 300 } }); return }
    // union of all node page-bounds
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
    shapes.forEach(s => {
      const b = editor.getShapePageBounds(s.id); if (!b) return
      minX = Math.min(minX, b.minX); minY = Math.min(minY, b.minY)
      maxX = Math.max(maxX, b.maxX); maxY = Math.max(maxY, b.maxY)
    })
    if (!isFinite(minX)) { editor.zoomToFit({ animation: { duration: 300 } }); return }
    // panel screen extents (px) from app.css: palette ~158 + 12 left; inspector ~330 + 12 right; toolbar
    // ~56 top; activity/rhm ~240 bottom. Convert to page units at the CURRENT zoom (approximation that
    // keeps the chrome clear; the fit re-zooms, so a generous pad is the safe direction).
    const z = editor.getZoomLevel() || 1
    const padL = (158 + 24) / z, padR = (330 + 24) / z, padT = (56 + 16) / z, padB = (240 + 16) / z
    const bounds = { x: minX - padL, y: minY - padT, w: (maxX - minX) + padL + padR, h: (maxY - minY) + padT + padB }
    editor.zoomToBounds(bounds, { targetZoom: 1, animation: { duration: 300 } })
  }
  async function maybeReact() {   // watch-and-react: backend-gated, comments only in that mode
    try { const r = await api.react(); if (r.comment) setChat(await api.chatHistory()) } catch { /* */ }
  }
  // U5: a palette add seeds its position into the VISIBLE viewport (the operator is looking here) instead
  // of the backend default (0,0) — which sat UNDER the top-left palette/toolbar. This is operator-intent
  // placement (the canvas reporting where the operator placed it, exactly like the drag→/api/move write-
  // back), NOT an invented layout: the position rides to the backend, which stays the source of truth.
  // Then pan+flash to the returned node id so "here's your node" feedback is unmistakable.
  async function addNode(type: string) {
    setNotice('+ ' + type)
    // centre of the current viewport, nudged by a small per-add jitter so repeated adds don't stack exactly.
    const vp = editor.getViewportPageBounds()
    const jitter = ((editor.getCurrentPageShapes().filter(s => s.type === 'node').length) % 5) * 26
    const x = Math.round(vp.midX - 120 + jitter)   // 120 = half a node's width (w:240)
    const y = Math.round(vp.midY - NODE_H / 2 + jitter)
    const r = await fetch('/api/node', { method: 'POST', headers: J, body: JSON.stringify({ type, config: {}, position: { x, y } }) }).then(x => x.json())
    await reload()
    // pan+flash to the new node (pure view — owns no data). The shape exists after reload()'s loadGraph.
    const nid = r?.id
    if (nid) {
      const sid = shapeIdFor(nid)
      if (editor.getShape(sid)) {
        editor.select(sid)
        editor.zoomToSelection({ animation: { duration: 350 } })
        // a transient flash ring on the new card (additive; removed after the pulse — no layout reflow).
        setTimeout(() => {
          const el = document.querySelector(`[data-shape-id="${sid}"] .node-card`) as HTMLElement | null
          if (el) { el.classList.add('node-flash'); setTimeout(() => el.classList.remove('node-flash'), 1400) }
        }, 60)
      }
      setNotice(`+ ${type} · ${nid} (added in view)`)
    }
  }
  async function wireSelected() {
    const sel = (editor.getSelectedShapes().filter(s => s.type === 'node') as NodeShape[])
    if (sel.length !== 2) { setNotice('select exactly two nodes to wire (left → right)'); return }
    const [a, b] = [...sel].sort((p, q) => p.x - q.x)
    const outs = Object.keys(oinfo[a.props.nodeType]?.ports?.outputs || {})
    const ins = Object.keys(oinfo[b.props.nodeType]?.ports?.inputs || {})
    if (!outs.length || !ins.length) { setNotice('those node-types have no compatible ports'); return }
    const r = await api.connect({ from_node: a.props.nodeId, from_port: outs[0], to_node: b.props.nodeId, to_port: ins[0] })
    if (r.error) setNotice('✕ ' + r.error)
    else { setNotice(`wired ${a.props.nodeId}.${outs[0]} → ${b.props.nodeId}.${ins[0]}`); await reload() }
  }
  // C1: a drag from an output nub to an input nub. The backend TYPE-CHECKS the wire and OWNS the edge;
  // we just reflect the result (fail-loud on a type mismatch).
  async function doConnect(from_node: string, from_port: string, to_node: string, to_port: string) {
    const r = await api.connect({ from_node, from_port, to_node, to_port })
    if (r?.error) setNotice('✕ ' + r.error)
    else { setNotice(`wired ${from_node}.${from_port} → ${to_node}.${to_port}`); const g = await loadGraph(editor); setEdges(g.edges || []); syncConfig(g) }
  }
  // A2: write one config key on a node → /api/set (merge) → refresh so the inspector shows the merged
  // value and the changed memo signature is reflected (D3 rerun-on-change). Backend returns fresh state.
  async function setNodeConfig(nodeId: string, key: string, value: any) {
    setNotice(`set ${nodeId}.${key}`)
    const g = await api.set(nodeId, { [key]: value })
    if (g?.error) { setNotice('✕ ' + g.error); return }
    setEdges(g.edges || []); syncConfig(g); await refresh(editor, g)
  }
  // F2: route the selected node's OUTPUT to the decision surface (inbox/COA). Composes the existing
  // surfaced path — the backend reads the output from live state, surfaces it as a 'result' decision;
  // it then shows up in the inbox panel (live_escalations) and drills via the same coa() compiler.
  // poll() gives instant local feedback regardless of the SSE stream.
  async function surfaceOutput(nodeId: string) {
    setNotice('surfacing output of ' + nodeId + ' → inbox')
    const r = await api.surfaceOutput(nodeId)
    if (r?.error) { setNotice('✕ ' + r.error); return }
    setNotice(`→ inbox · ${r.name} (drill from the inbox to decide)`); await poll()
  }
  // F3: choose "build from this output" — prefill the GROW panel's spec with the node's output and
  // focus it, then let the EXISTING propose → surfaced → approve&apply chain run untouched (no new
  // propose path). The operator names it + edits the spec, then dispatches as usual.
  function buildFromOutput(nodeId: string, output: string) {
    setGname('')
    setGspec(output || '')
    setSurf(null)
    setGrowMsg(`build a node from ${nodeId}'s output — name it, refine the spec, then dispatch.`)
    setNotice('build-from-output → grow panel (edit + dispatch)')
  }
  async function deleteSelected() {
    const sel = (editor.getSelectedShapes().filter(s => s.type === 'node') as NodeShape[])
    if (!sel.length) { setNotice('select node(s) to delete'); return }
    // U10: guard the only real destructive path — a single click must not irreversibly delete. Confirm
    // first (names the nodes so the operator knows exactly what goes). A key-delete just reappears on the
    // next loadGraph since the backend is truth; THIS is the path that actually removes from the backend.
    const names = sel.map(s => s.props.nodeId).join(', ')
    if (!window.confirm(`Delete ${sel.length} node(s)?\n\n${names}\n\nThis removes them from the graph.`)) {
      setNotice('delete cancelled'); return
    }
    for (const s of sel) await api.del(s.props.nodeId)
    setNotice(`deleted ${sel.length} node(s)`); await reload()
  }
  async function sendChat(override?: string) {
    const m = (override ?? chatMsg).trim()
    if (!m || chatBusy) return
    setChatMsg(''); setChatBusy(true)
    setChat(c => [...c, { role: 'user', text: m }])
    try {
      // co-presence: the RHM sees what the operator has selected on the canvas right now
      const selected = (editor.getSelectedShapes().filter(s => s.type === 'node') as NodeShape[]).map(s => s.props.nodeId)
      const r = await api.chat(m, { selected }); setChat(r.history); await poll()
      if (now?.mode === 'listening' && r.reply) speakReply(r.reply).catch(() => { /* TTS hiccup is harmless here */ })   // voice out: speak the reply
      // the decision-compiler DOWN: an action the RHM took routes through the gate
      if (r.action?.did === 'run' || r.action?.did === 'build') { await reload() }
      if (r.action?.did === 'show') {           // attention-direction: move the operator's view (THE KEYSTONE)
        // C3/S2: route EVERY target through resolveUiTarget — node-ids drive the camera (the existing path),
        // ui://<kind>/<ref> strings (once lane X passes them through) drive the camera OR scroll+spotlight a
        // chrome panel. One sink for both forms; this is what makes `show` ui://-aware (not node-only).
        const targets: string[] = r.action.targets || []
        const canvasIds = targets.filter(t => !t.startsWith('ui://')).map((nid: string) => shapeIdFor(nid)).filter((id: any) => editor.getShape(id))
        if (canvasIds.length) { editor.select(...canvasIds); editor.zoomToSelection({ animation: { duration: 450 } }) }
        targets.forEach(t => { if (t.startsWith('ui://')) resolveUiTarget(t) })   // chrome/panel/canvas-by-address
      }
      if (r.action?.did === 'propose') {
        const all = await fetch('/api/surfaced').then(x => x.json())
        const d = all.find((x: any) => x.id === r.action.surfaced)
        if (d) setSurf({ id: d.id, name: d.payload.name, code: d.payload.code })   // → operator approves in GROW panel
      }
      if (r.action?.did === 'panel') {            // update the interface through the interface
        const all = await fetch('/api/surfaced').then(x => x.json())
        const d = all.find((x: any) => x.id === r.action.surfaced)
        if (d) setSurf({ id: d.id, name: d.payload.name, code: JSON.stringify(d.payload.panel, null, 2), isPanel: true })
      }
      if (r.action?.did === 'extend') {           // arbitrary code → build-gated on approve
        const all = await fetch('/api/surfaced').then(x => x.json())
        const d = all.find((x: any) => x.id === r.action.surfaced)
        if (d) setSurf({ id: d.id, name: d.payload.name, code: d.payload.code, isExt: true })
      }
    }
    catch { setChat(c => [...c, { role: 'assistant', text: '(could not reach the brain)' }]) }
    finally { setChatBusy(false) }
  }
  async function changeMode(m: string) { setNotice('presence → ' + m); await api.setMode(m); await poll() }
  async function applyCfg() {
    const c = await api.setRhmConfig({ model: cfg.model, persona: cfg.persona })
    setCfg(c); setCfgOpen(false); setNotice('RHM config → ' + (c.model || 'default')); await poll()
  }
  function cycleLayers() {
    const next = (layerView + 1) % 3
    setLayerView(next)
    const b = document.body.classList
    b.remove('layers-dim', 'layers-dim-authored')
    if (next === 1) { b.add('layers-dim'); setNotice('layers · origin only (system-derived dimmed)') }
    else if (next === 2) { b.add('layers-dim-authored'); setNotice('layers · system-derived only (origin dimmed)') }
    else setNotice('layers · all')
  }
  async function portalSelected() {
    const sel = (editor.getSelectedShapes().filter(s => s.type === 'node') as NodeShape[])
    if (sel.length !== 1) { setNotice('select one node to open a live portal onto it'); return }
    const src = sel[0]
    if (src.props.nodeType === 'portal') { setNotice('that is already a portal'); return }
    const ref = `run://${gid}/${src.props.nodeId}`
    await api.addNode('portal', { ref })
    setNotice(`portal → ${ref} (one artefact, live view)`); await reload()
  }

  // C2/C3 — THE KEYSTONE (frontend half): resolveUiTarget moves the operator's view to ANY addressable UI
  // thing. It is the SINGLE sink for both attention-direction entry points (the chat `show` action AND the
  // walkthrough card's per-step drive). It accepts two forms for backward-compat while lane X lands:
  //   • a bare node-id          → treat as ui://canvas/<id> (today's `show` targets are node-ids)
  //   • ui://<kind>/<ref>       → canvas → editor.select+zoomToSelection (the EXISTING show path, App.tsx);
  //                               chrome|field|panel|ext → querySelector('[data-ui-ref]')+scrollIntoView+
  //                               a transient .ui-spotlight ring (the net-new DOM-present path).
  // registry-is-truth: a ui:// ref is validated against UI_INFO (from /api/ui_info) — an UNKNOWN ref fails
  // loud with a notice, never a silent no-op. The verdict/edit never flows here — this only MOVES the view.
  function resolveUiTarget(target?: string): boolean {
    if (!target) return false
    // form 1: bare node-id (legacy show targets) → canvas camera, the existing path
    if (!target.startsWith('ui://')) return driveCanvas(target)
    const m = target.match(/^ui:\/\/([^/]+)\/(.+)$/)
    if (!m) { setNotice('✕ malformed ui:// target: ' + target); return false }
    const kind = m[1], ref = m[2]
    if (kind === 'canvas') {
      if (ref === '*') { editor.zoomToFit({ animation: { duration: 450 } }); setNotice('→ canvas'); return true }
      return driveCanvas(ref)
    }
    // chrome | field | panel | ext → a DOM target. Validate against the registry (fail loud if unknown).
    if (UI_INFO[ref] == null && Object.keys(UI_INFO).length) {
      setNotice('✕ no registered UI target for ' + ref + ' (registry is truth)'); return false
    }
    // openable (e.g. workshop) must be OPEN before we can scroll to it — honor the capability from the registry.
    if (UI_INFO[ref]?.capabilities?.openable && ref === 'workshop' && !workshop && selectedRef.current) {
      setWorkshop(selectedRef.current)   // open the workshop onto the current selection so the target exists in the DOM
    }
    // defer one frame so a just-opened region is mounted before we query for it (fail loud if still absent).
    setTimeout(() => {
      const el = document.querySelector('[data-ui-ref="' + ref + '"]') as HTMLElement | null
      if (!el) { setNotice('✕ UI target not in the DOM right now: ' + ref); return }
      el.scrollIntoView({ block: 'center', behavior: 'smooth' })
      el.classList.add('ui-spotlight')
      setNotice('→ ' + (UI_INFO[ref]?.title || ref))
      setTimeout(() => el.classList.remove('ui-spotlight'), 2400)   // transient ring — additive, no layout reflow
    }, 30)
    return true
  }
  // the canvas camera path — reused by both ui://canvas/<id> and a bare node-id. select+zoomToSelection is
  // the EXISTING show path (preserved). A node-id with no shape fails loud (we never point at nothing).
  function driveCanvas(nodeId: string): boolean {
    const id = shapeIdFor(nodeId)
    if (!editor.getShape(id)) { setNotice('✕ no node ' + nodeId + ' on the canvas'); return false }
    editor.select(id); editor.zoomToSelection({ animation: { duration: 450 } })
    setNotice('→ ' + nodeId); return true
  }
  // a ref the resolver can read the current selection from (for openable canvas-present), without a re-render dep.
  const selectedRef = useRef<NodeShape['props'] | null>(null)

  // B-frontend: start a walk over a set of review item ids (the inbox affordance — the operator-driven entry
  // point for S1; the RHM-offered walk, lane X, will call the same start path). Persists the session id in
  // localStorage so a page reload / SSE-drop resumes at the same cursor (S7c, same-device).
  async function startWalk(itemIds: string[]) {
    if (!itemIds.length) { setNotice('no review items to walk'); return }
    if (wtBusyRef.current) return                  // CONCURRENCY GUARD: start framing also takes ~20s while session is still null (button not yet hidden) — a 2nd click would start TWO sessions. Drop it.
    wtBusyRef.current = true; setWtBusy(true)
    setNotice('starting walk over ' + itemIds.length + ' item(s)…')
    try {
      const s = await api.reviewStart(itemIds, 'walkthrough')
      if (s?.error) { setNotice('✕ ' + s.error); return }
      try { localStorage.setItem('company-review-session', s.session) } catch { /* */ }
      setSession(s); setWtReason(''); setWtSpoke('')
    } catch (e: any) { setNotice('✕ could not start the walk: ' + (e?.message || e)) }
    finally { wtBusyRef.current = false; setWtBusy(false) }   // re-enable on success OR error
  }
  // refresh the card from the server-authoritative present_current (driven by the review.advance SSE event,
  // and on resume). reflects-never-owns: the backend session is truth; we re-read it, never invent the step.
  async function refreshSession(sid: string) {
    try {
      const s = await api.reviewCurrent(sid)
      if (s?.error) { setNotice('✕ session: ' + s.error); endWalk(); return }
      setSession(s); setWtReason('')
    } catch { /* bridge transient — the next event re-pulls */ }
  }
  function endWalk() {
    setSession(null); sessionRef.current = null; spokenFor.current = ''
    try { localStorage.removeItem('company-review-session') } catch { /* */ }
  }
  // D-frontend: respond to the current step — operator-only, tagged with the session id + cursor position.
  // approve/reject/comment/skip/decide. The verdict goes THROUGH /api/resolve (reflects-never-owns); a
  // reject/comment carries the WHY (training signal + actionable edit, E2). respond RECORDS; Next ADVANCES.
  async function respondStep(choice: string) {
    if (!session?.item) return
    if (wtBusyRef.current) return                  // CONCURRENCY GUARD: a request is already in flight — drop the extra click (one click = one verdict)
    wtBusyRef.current = true; setWtBusy(true)       // ref gates synchronously (pre-render); state disables the controls visibly
    const why = (choice === 'reject' || choice === 'comment') ? wtReason : ''
    setNotice('verdict: ' + choice + ' · ' + session.item)
    try {
      const r = await api.resolveStep(session.item, choice, why, session.session, session.cursor)
      if (r?.error || r?.ok === false) { setNotice('✕ ' + (r.error || 'resolve refused')); return }
      setSession((cur: any) => cur ? { ...cur, _responded: choice } : cur)   // mark the step responded (UI hint)
      await poll()   // refresh the inbox so the resolved item drops out of live_escalations
    } catch (e: any) { setNotice('✕ resolve failed: ' + (e?.message || e)) }
    finally { wtBusyRef.current = false; setWtBusy(false) }   // re-enable on success OR error — never a dead end
  }
  // B-frontend: Next — write the current step's go-gate (backend) → the scheduler fires it → the session
  // advances to the next unresolved step (or done). The review.advance SSE event ALSO refreshes the card;
  // we apply the returned step directly for instant feedback (idempotent with the event refresh).
  async function nextStep() {
    if (!session?.session) return
    if (wtBusyRef.current) return                  // CONCURRENCY GUARD: framing takes ~20s — a 2nd click would issue a CONCURRENT /api/review/next that desyncs the cursor. Drop it.
    wtBusyRef.current = true; setWtBusy(true)
    setNotice('next →')
    try {
      const s = await api.reviewNext(session.session)
      if (s?.error) { setNotice('✕ ' + s.error); return }
      if (s.done) { setSession({ ...session, ...s, done: true, item: null, framing: null }) }
      else { setSession(s); setWtReason('') }
    } catch (e: any) { setNotice('✕ next failed: ' + (e?.message || e)) }
    finally { wtBusyRef.current = false; setWtBusy(false) }   // re-enable on success OR error
  }

  // B+C — the per-step VIEW DRIVE: when the walk lands on a new step, MOVE the view to the thing the item
  // concerns. The target is the RAW item's ui_target (ui://chrome/toolbar, ui://canvas/*, …) — NOT the
  // top-level meta ui://review/<id> (that meta address isn't in the registry). Deps are the STEP only (not
  // voiceOn) so toggling voice mid-step does NOT re-zoom/re-spotlight a view the operator didn't ask to move.
  useEffect(() => {
    if (!session || session.done || !session.item) return
    const tgt = session.raw?.ui_target
    if (tgt) resolveUiTarget(tgt)   // registry-validated; fail-loud if unknown
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.session, session?.cursor, session?.item])

  // F — the per-step NARRATION: SPEAK the step's framing, voice-FIRST (not gated to listening mode; gated on
  // the voice|text toggle). Speak ONCE per (session:cursor) step (spokenFor guard) so a re-render/refresh
  // doesn't re-narrate; any voice failure falls back to text (F4 — never a dead end).
  useEffect(() => {
    if (!session || session.done || !session.item) return
    const stepKey = session.session + ':' + session.cursor
    if (spokenFor.current === stepKey) return
    spokenFor.current = stepKey
    const text = session.framing || (session.raw?.payload?.note) || ('Review item ' + session.item)
    if (voiceOn) {
      setWtSpoke('speaking…')
      speakReply(text)
        .then(() => setWtSpoke('🔊 spoke the framing'))
        .catch(() => setWtSpoke('voice unavailable — read it on screen'))   // F4: never a dead end
    } else setWtSpoke('text mode')
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.session, session?.cursor, session?.item, voiceOn])

  // U3: tick an elapsed counter while a run is in flight, so the operator sees progress during the
  // ~20-27s resolutions (not a frozen "running…"). Cleared when the run ends (runStartedAt → null).
  // Also toggle a body class so CSS can PULSE the not-yet-resolved node cards (best-effort per-node
  // progress: the backend emits no per-node signal, so we pulse all pending nodes rather than fake a
  // single "computing" node — see report notes; faking one would violate fail-loud honesty).
  useEffect(() => {
    if (runStartedAt == null) { document.body.classList.remove('canvas-running'); return }
    document.body.classList.add('canvas-running')
    const t = setInterval(() => setRunElapsed(Math.floor((Date.now() - runStartedAt) / 1000)), 250)
    return () => { clearInterval(t); document.body.classList.remove('canvas-running') }
  }, [runStartedAt])

  const selected = useValue('sel', () => {
    const s = editor.getOnlySelectedShape()
    return s && s.type === 'node' ? (s as NodeShape).props : null
  }, [editor])

  // U7: selecting a node must surface its inspector even if the operator has scrolled the right rail down
  // to the inbox/grow. The inspector is the top of the shared scroll column (.panel); on a new selection
  // we scroll it back into view so the "I selected something" feedback is never silently off-screen.
  useEffect(() => {
    if (!selected) return
    const insp = document.querySelector('[data-ui-ref="inspector"]') as HTMLElement | null
    if (insp) insp.scrollTo ? insp.scrollTo({ top: 0, behavior: 'smooth' }) : (insp.scrollTop = 0)
  }, [selected?.nodeId])
  selectedRef.current = selected

  // D4: run the graph; `force` (a node-id list) bypasses the memo gate for just those nodes. D5: the run
  // result reports ran/cached per node — refresh() writes those statuses onto the cards (legible rerun).
  async function doRun(force?: string[]) {
    setRunning(true); setRunError(null)
    setRunStartedAt(Date.now()); setRunElapsed(0)   // U3: start the elapsed clock for the in-flight run
    setGrowMsg(force ? `force re-running ${force.join(', ')} (past the memo cache)…`
                     : 'resolving… presence of data at each address fires the next node')
    try {
      const st = await api.run(force); await refresh(editor, st)
      const ran = (st.nodes || []).filter((n: any) => n.status === 'ran').length
      const cached = (st.nodes || []).filter((n: any) => n.status === 'cached').length
      // U2: the run RESULT (state) carries only ran|cached|idle — the STUCK list lives on the emitted
      // `run` event. Pull the freshest events and read the latest run event's stuck array, then re-apply
      // the stuck paint onto the shapes (loadGraph/refresh would otherwise leave them looking merely idle).
      try { const evs = await api.events(); applyStuckFromEvents(evs) } catch { /* the SSE run event also carries it */ }
      const stuckN = stuckNodes.current.size
      setGrowMsg(`run complete · ${ran} ran · ${cached} cached` + (stuckN ? ` · ${stuckN} stuck` : '') + '.')
      await poll(); await maybeReact()
    }
    catch (e: any) {
      // U4 (fail loud, no dead end): a REAL rejection — network down, or a node that RAISED and failed the
      // whole run (the scheduler has no per-node "errored" bucket; a raising node fails api.run() outright).
      // Surface it legibly with a retry; never an uncaught promise rejection, never a silent swallow.
      const msg = e?.message || String(e)
      setRunError(msg); setGrowMsg('✕ run failed — ' + msg); setNotice('✕ run failed: ' + msg)
    }
    finally { setRunning(false); setRunStartedAt(null) }   // ALWAYS clears running — the latch can never persist
  }
  // U2: read the latest `run` event's stuck/ran arrays and update stuckNodes, then repaint the shapes.
  // A node that just RAN is no longer stuck (clear it); a node reported stuck gets the stuck paint. The
  // run event shape is {kind:'run', ran:[...], cached:[...], stuck:[...]} (suite._emit meta). Idempotent.
  function applyStuckFromEvents(evs: any[]) {
    const runEv = (evs || []).filter((e: any) => e && e.kind === 'run').sort((a, b) => (b.seq ?? 0) - (a.seq ?? 0))[0]
    if (!runEv) return
    const stuck: string[] = Array.isArray(runEv.stuck) ? runEv.stuck : []
    const ran: string[] = Array.isArray(runEv.ran) ? runEv.ran : []
    const next = new Set(stuck)
    ran.forEach(id => next.delete(id))   // anything that ran this pass is, by definition, no longer stuck
    stuckNodes.current = next
    paintStuck()
  }
  // U2: write the stuck status onto the tldraw shapes (a client-only overlay status; the backend status
  // stays ran|cached|idle — reflects-never-owns: we don't invent a backend truth, we annotate from the
  // run event the backend DID emit). Re-applied after every loadGraph so a refresh can't erase it.
  function paintStuck() {
    editor.getCurrentPageShapes().forEach(s => {
      if (s.type !== 'node') return
      const nid = (s as NodeShape).props.nodeId
      const isStuck = stuckNodes.current.has(nid)
      const cur = (s as NodeShape).props.status
      if (isStuck && cur !== 'stuck') editor.updateShape<NodeShape>({ id: s.id, type: 'node', props: { status: 'stuck' } })
      else if (!isStuck && cur === 'stuck') editor.updateShape<NodeShape>({ id: s.id, type: 'node', props: { status: 'idle' } })
    })
  }
  async function dispatch() {
    if (!gname || !gspec) { setGrowMsg('enter a name + what it should do.'); return }
    setGrowMsg(`dispatching… the brain is writing the ${gname} node…`); setSurf(null)
    const r = await api.propose(gname, gspec)
    if (r.error) { setGrowMsg(''); setSurf({ error: r.error }) } else setSurf(r)
    await poll()
  }
  // voice out — speak text (local Kokoro via the bridge). Used by the RHM reply (listening mode) AND the
  // walkthrough per-step narration (F1, voice-first). Throws on failure so callers that need a fallback
  // (the walk, F4) can catch and degrade to text; the chat caller wraps it so a TTS hiccup is harmless.
  async function speakReply(text: string) {
    const blob = await api.tts(text)
    await new Audio(URL.createObjectURL(blob)).play()
  }
  // voice in — push-to-talk: record → STT → send as a chat turn (which then speaks its reply)
  async function recordToggle() {
    if (recording) { recorderRef.current?.stop(); return }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const rec = new MediaRecorder(stream)
      const chunks: BlobPart[] = []
      rec.ondataavailable = e => chunks.push(e.data)
      rec.onstop = async () => {
        stream.getTracks().forEach(t => t.stop()); setRecording(false); setNotice('transcribing…')
        try {
          const r = await api.stt(new Blob(chunks, { type: 'audio/webm' }))
          if (r.text) {
            setNotice('you said: ' + r.text)
            // F2: when a walk is active, the mic routes to the session RESPOND path (not sendChat). A simple
            // keyword map turns speech into a verdict (approve/reject/skip/comment/decide); anything else
            // becomes a comment carrying the transcript as the WHY (never a dead end — F4). Outside a walk,
            // it's a normal chat turn (which speaks its reply).
            if (sessionRef.current && !sessionRef.current.done) {
              const t = r.text.toLowerCase()
              const choice = /\bapprove|accept|yes|approved\b/.test(t) ? 'approve'
                : /\breject|decline|no\b/.test(t) ? 'reject'
                : /\bskip|pass|later\b/.test(t) ? 'skip'
                : /\bdecide|you decide|defer to you\b/.test(t) ? 'decide'
                : 'comment'
              if (choice === 'reject' || choice === 'comment') setWtReason(r.text)   // capture the spoken WHY
              setWtSpoke('🎙 heard: "' + r.text + '" → ' + choice)
              await respondStep(choice)
            } else await sendChat(r.text)
          }
          else setNotice('(no speech detected)')
        } catch (e: any) { setNotice('STT error — type instead: ' + (e?.message || e)) }   // F4: fall back to text
      }
      recorderRef.current = rec; rec.start(); setRecording(true); setNotice('listening… (click again to stop)')
    } catch { setNotice('mic unavailable — grant microphone permission') }
  }
  function fieldValue(f: any) {
    if (f.target === 'mode') return now?.mode || 'listening'
    if (f.target === 'model') return cfg?.model || ''
    if (f.target === 'persona') return cfg?.persona || ''
    return ''
  }
  async function setField(f: any, v: string) {
    if (f.target === 'mode') await changeMode(v)
    else { const c = await api.setRhmConfig({ [f.target]: v }); setCfg(c); setNotice(f.target + ' → ' + v) }
  }
  async function revertLast() {
    if (!lastChange?.sha) return
    setGrowMsg('rolling back the last self-change…')
    const r = await api.revert(lastChange.sha)
    setTypes(await api.types()); await reload()
    setGrowMsg('↩ reverted — the change is undone (git ' + (r.head || '').slice(0, 8) + '). bounded, recoverable.')
  }
  async function approveApply() {
    await api.resolve(surf.id, 'approve')
    const r = await api.apply(surf.id)
    if (r.error) { setSurf({ ...surf, error: r.error }) }
    else { setSurf(null); setGrowMsg(`✓ approved + applied → ${surf.name} is now a live node-type.`); setTypes(r.types); await poll() }
  }

  return (
    <>
      <Edges edges={edges} />
      {/* B-frontend: the WALKTHROUGH CARD — the visible review organ. Shown only while a session is active.
         Wrapped in PanelErrorBoundary so a bad item degrades to a contained card, never white-screens (LAW).
         Renders present_current's framed item; the per-step effect already drove the view to its ui:// target
         + spoke it. respond → /api/resolve (operator-only verdict); Next → /api/review/next; "N of M" progress. */}
      {session && (
        <PanelErrorBoundary name="walkthrough">
          <div className="hud walkthrough" data-ui-ref="walkthrough">
            <div className="wt-head">
              <span className="wt-title">walkthrough</span>
              <span className="wt-mode">
                <button className={voiceOn ? 'on' : ''} onClick={() => setVoiceOn(true)} title="voice-first: speak each step">🔊 voice</button>
                <button className={!voiceOn ? 'on' : ''} onClick={() => setVoiceOn(false)} title="text only">text</button>
              </span>
              <span className="wt-prog">{session.done ? 'complete' : `${(session.cursor ?? 0) + 1} of ${session.total}`}</span>
              <span className="close" style={{ cursor: 'pointer', color: 'var(--dim)' }} title="leave the walk (the session stays server-side)"
                onClick={endWalk}>✕</span>
            </div>
            {session.done ? (
              <div className="wt-done">✓ walk complete — {session.total} item(s) reviewed. Verdicts are recorded; the
                build loop reads them on its next fire (approved→done · new-ask→a new criterion · rejected→requeued · skipped→still pending).
                <div style={{ marginTop: 10 }}><button className="b ghost" onClick={endWalk}>close</button></div>
              </div>
            ) : (
              <>
                {/* S7b: framing is fail-safe — if the coa LLM errored the backend returns the raw payload; we
                   still show SOMETHING (the note / the item id), the walk never blocks. */}
                <div className="wt-frame">{session.framing || (session.raw?.payload?.note) || ('Review item: ' + session.item + ' (no framing returned — raw payload below)')}</div>
                {session.raw?.ui_target && <div className="wt-target">concerns: {session.raw.ui_target}
                  <button className="b ghost sm" style={{ marginLeft: 8 }} title="move the view to this thing again"
                    onClick={() => resolveUiTarget(session.raw.ui_target)}>↪ show again</button></div>}
                <input className="wt-reason" placeholder="why? (captured into the verdict — required for reject/comment)"
                  value={wtReason} onChange={e => setWtReason(e.target.value)} />
                {/* CONCURRENCY GUARD: every respond control is disabled while a request is in flight (wtBusy)
                   — one click = one verdict; the .wt-busy class dims them so the lock is visible during the ~20s wait. */}
                <div className={'wt-respond' + (wtBusy ? ' wt-busy' : '')}>
                  <button className="b verdict approve" disabled={wtBusy} onClick={() => respondStep('approve')} title="approve this item">✓ approve</button>
                  <button className="b ghost verdict reject" disabled={wtBusy} onClick={() => respondStep('reject')} title="reject (give a reason)">✕ reject</button>
                  <button className="b ghost verdict" disabled={wtBusy} onClick={() => respondStep('comment')} title="comment — capture a note, stays pending">✎ comment</button>
                  <button className="b ghost verdict" disabled={wtBusy} onClick={() => respondStep('skip')} title="skip — still needs you later">⤼ skip</button>
                  <button className="b ghost verdict" disabled={wtBusy} onClick={() => respondStep('decide')} title="let the system decide (deterministic, by consequence)">⚖ decide</button>
                </div>
                <div className="wt-foot">
                  {wtBusy
                    ? <span className="wt-resolved">⏳ working… (framing can take a moment)</span>
                    : session._responded
                      ? <span className="wt-resolved">✓ responded: {session._responded}</span>
                      : <span className="muted">respond, then advance</span>}
                  {/* Next disabled while a /api/review/next (or any respond) request is pending — a 2nd click
                     mid-flight would issue a concurrent next that desyncs the backend cursor. */}
                  <button className="b" style={{ marginLeft: 'auto' }} disabled={wtBusy} onClick={nextStep} title="advance to the next step">{wtBusy ? '…' : 'next →'}</button>
                  {wtSpoke && <span className="wt-spoke">{wtSpoke}</span>}
                </div>
              </>
            )}
          </div>
        </PanelErrorBoundary>
      )}
      <div className="hud toolbar" data-ui-ref="toolbar">
        <span className="title">the&nbsp;<em>company</em></span>
        {now && (
          <span className={'presence ' + (now.mode === 'off' ? 'off' : running || chatBusy ? 'busy' : now.surfaced_pending ? 'warn' : 'ok')}>
            <span className="pdot" />{running ? `running… ${runElapsed}s` : chatBusy ? 'thinking…' : now.presence}
          </span>
        )}
        {/* U4: a legible, recoverable run-error surface — shows the failure + a retry, right where RUN is.
           Clears on the next successful run (doRun sets runError=null at entry). */}
        {runError && !running && (
          <span className="run-err" title={runError}>
            ✕ run failed
            <button className="b sm" style={{ marginLeft: 6 }} onClick={() => doRun()} title="retry the run">↻ retry</button>
            <button className="b ghost sm" style={{ marginLeft: 4 }} onClick={() => setRunError(null)} title="dismiss">✕</button>
          </span>
        )}
        {now && (
          // U11: the dropdown's title shows the CURRENT mode's description; each option carries its own
          // description as a title so hovering an option (where the browser shows it) explains it too.
          <select className="mode-sel" value={now.mode || 'listening'} onChange={e => changeMode(e.target.value)}
            title={'presence dial · ' + (now.mode || 'listening') + ' — ' + (modeDesc[now.mode || 'listening'] || '')}>
            {MODES.map(m => <option key={m} value={m} title={modeDesc[m] || ''}>{m}</option>)}
          </select>
        )}
        {/* U11: an always-visible one-line description of the active mode (tooltips alone are not legible enough). */}
        {now && <span className="mode-desc" title={modeDesc[now.mode || 'listening'] || ''}>{modeDesc[now.mode || 'listening'] || ''}</span>}
        {/* U1 (load-bearing fix): wrap in an arrow so React's MouseEvent is NOT passed as `force`.
           Passing the event made `force.join(', ')` (doRun, line ~880) throw a synchronous TypeError
           BEFORE the try{, so `finally{ setRunning(false) }` never ran and api.run() never fired →
           button latched until reload. `() => doRun()` → force is undefined → the normal-run branch
           POSTs /api/run. The other callers (force-rerun) pass real string[] arrays and are unchanged. */}
        <button className="b" onClick={() => doRun()} disabled={running}>{running ? 'running…' : '▶ run'}</button>
        <button className="b ghost" onClick={wireSelected}>＋ wire</button>
        <button className="b ghost" onClick={portalSelected}>⊕ portal</button>
        <button className="b ghost" onClick={deleteSelected}>🗑 delete</button>
        <button className="b ghost" onClick={cycleLayers}>◐ layers: {['all', 'origin', 'system'][layerView]}</button>
        {/* U6: fit the graph with padding for the fixed panels so nothing tucks under the chrome */}
        <button className="b ghost" onClick={fitGraph} title="zoom to fit — padded so no node hides under the panels">⊡ fit</button>
        <button className="b ghost" onClick={reload}>reload</button>
        {notice && <span className="notice">{notice}</span>}
      </div>

      <div className="hud palette">
        <h3>palette</h3>
        <div className="muted" style={{ marginBottom: 8 }}>click to add · select 2 + “wire”</div>
        {Object.keys(oinfo).sort().map(t => (
          <div key={t} className="pchip" onClick={() => addNode(t)}>
            <span>+ {t}</span><span className="pk">{oinfo[t]?.kind || ''}</span>
          </div>
        ))}
      </div>

      <div className="hud panel" data-ui-ref="inspector">
        {selected ? (
          <>
            <h3>{selected.nodeType} · {selected.nodeId}</h3>
            <div className="row"><span className="k">kind</span><span>{selected.kind}</span></div>
            <div className="row">
              <span className="k">status</span>
              <span>
                {/* U2: stuck reads as a legible failure in the inspector too, not a bare word. */}
                {selected.status === 'cached' ? 'cached ↺'
                  : selected.status === 'stuck' ? <span className="err">stuck — an input never resolved</span>
                  : selected.status}
                {/* D4/D5: force this node past the memo cache, right from the inspector */}
                <button className="b ghost sm" style={{ marginLeft: 8 }} title="force re-run (bypass memo cache)"
                  onClick={() => doRun([selected.nodeId])}>↻ force</button>
              </span>
            </div>
            <div className="row"><span className="k">address</span></div>
            <div className="muted" style={{ wordBreak: 'break-all' }}>{selected.address}</div>
            {/* A2/A4: editable config — generic form from config_schema + live config, contained by a boundary */}
            <div className="row" style={{ marginTop: 8 }}><span className="k">config</span></div>
            {/* configTick in the key forces a fresh mount after a write so the form shows merged values */}
            <div key={selected.nodeId + ':' + configTick}>
              <PanelErrorBoundary name={selected.nodeType + ' config'}>
                <NodeConfigForm
                  nodeType={selected.nodeType}
                  config={configByNode.current[selected.nodeId] || {}}
                  onSet={(key, value) => setNodeConfig(selected.nodeId, key, value)} />
              </PanelErrorBoundary>
            </div>
            <div className="row" style={{ marginTop: 8 }}><span className="k">output</span></div>
            <pre>{selected.output || '— not yet resolved —'}</pre>
            {selected.output && (
              <div className="out-actions">
                <button className="b ghost" onClick={() => setWorkshop(selected)}>open workshop ⤢</button>
                {/* F3: rerun from the output (force past the memo gate) — composes the existing /api/run force verb */}
                <button className="b ghost" title="force re-run this node (bypass the memo cache)"
                  onClick={() => doRun([selected.nodeId])}>↻ rerun</button>
                {/* F2: route this result to the decision surface (inbox/COA) — the sanctioned operator path */}
                <button className="b ghost" title="surface this output as a decision in the inbox"
                  onClick={() => surfaceOutput(selected.nodeId)}>→ inbox</button>
                {/* F3: build a new node from this output — prefills + reuses the grow→propose→approve chain */}
                <button className="b ghost" title="build a node from this output (edit + dispatch in grow)"
                  onClick={() => buildFromOutput(selected.nodeId, selected.output)}>⊕ build from output</button>
              </div>
            )}
          </>
        ) : <div className="muted">select a node to inspect it. pan/zoom the canvas; zoom in for detail (semantic zoom).</div>}

        <div data-ui-ref="inbox">
          <h3 style={{ marginTop: 18 }}>inbox · chief-of-staff triage</h3>
          <div className="ibx-head">
            {/* U11: qualify the count so it is never mistaken for unresolved GRAPH NODES — these are
               decisions/approvals the chief-of-staff has escalated to you. */}
            <span className="sig" title="decisions/approvals escalated to you — not graph nodes">{inbox.counts?.escalations || 0} decision(s) awaiting you</span>
            <span className="muted"> · {inbox.counts?.resolved || 0} resolved-for-you</span>
            {/* B-frontend: the operator entry point for S1 — walk ALL live escalations through the organ.
               The RHM-offered walk (lane X) calls the same startWalk path; this makes S1 testable now. */}
            {(inbox.live_escalations || []).length > 0 && !session && (
              <button className="b sm" style={{ marginLeft: 'auto' }} disabled={wtBusy} title="walk all awaiting items through the review organ"
                onClick={() => startWalk((inbox.live_escalations || []).map((d: any) => d.id))}>{wtBusy ? 'starting…' : '▷ walk these'}</button>
            )}
          </div>
          {/* WIRE-UI: the decision→implementation wire's build-intents get their OWN lane, rendered as
             rich cards (scope · consequence_class · phase · the implemented result/diff) so the operator
             can SEE a build end to end — never a bare uuid (a build-intent payload has no `name`). They
             still live in `live_escalations` (code never writes `resolved`, only the `status` lane), so
             we split them out here BEFORE the generic action-grouping below. */}
          {(() => {
            const esc: any[] = inbox.live_escalations || []
            const builds = esc.filter(isBuildIntent)
            if (!builds.length) return null
            return (
              <div className="ibx-lane ibx-builds">
                <div className="ibx-lane-head">decision → build <span className="muted">· {builds.length}</span></div>
                {builds.map((d: any) => (
                  <PanelErrorBoundary key={d.id} name={'build-intent ' + d.id}>
                    {/* DEMONSTRATE-FIRST: onDemonstrate places the built node-type on the canvas (addNode
                       puts it in the viewport + flashes it = "see it present + runnable"); liveTypes is the
                       registry truth that gates the "show me" affordance to a node-type that actually went live. */}
                    <BuildIntentCard d={d} onOpen={openCoa} onDemonstrate={(t: string) => { void addNode(t) }} liveTypes={types} />
                  </PanelErrorBoundary>
                ))}
              </div>
            )
          })()}
          {/* U12: group the REMAINING (non-build-intent) live escalations by ACTION into visual lanes (so a
             large queue isn't one flat list). The grouping mirrors the backend's `batched` keying; here we
             group ALL of them (not only >1) so every item lands under a labelled lane. A `(test)` heuristic
             distinguishes test-pollution items so they're visible-but-separable, never silently mixed in. */}
          {(() => {
            const esc: any[] = (inbox.live_escalations || []).filter((d: any) => !isBuildIntent(d))
            const isTest = (d: any) => /test|fixture|pollut|sample|demo/i.test(((d.payload?.name || '') + ' ' + (d.id || '')))
            const lanes: Record<string, any[]> = {}
            esc.forEach(d => { const k = (isTest(d) ? 'test · ' : '') + (d.action || 'decision'); (lanes[k] = lanes[k] || []).push(d) })
            return Object.entries(lanes).map(([lane, items]) => (
              <div key={lane} className={'ibx-lane' + (/^test · /.test(lane) ? ' ibx-test' : '')}>
                <div className="ibx-lane-head">{lane} <span className="muted">· {items.length}</span></div>
                {items.map((d: any) => (
                  <div key={d.id} className="ibx-item" onClick={() => openCoa(d.id)}>
                    ⚠ {d.payload?.name || d.id} <span className="muted">— compile ↗</span>
                  </div>
                ))}
              </div>
            ))
          })()}
          {(inbox.counts?.escalations || 0) === 0 && <div className="muted">nothing awaiting you.</div>}
          {/* WIRE-UI: the W7 DEFERRED QUEUE — when the dispatch loop hits its concurrency cap it emits a
             `decision.deferred` event (event-only; NO inbox item) per held build, so the operator SEES what
             was held rather than it silently disappearing (fail-loud). We read it from the activity log,
             newest first, deduped by the resolve seq the deferral is keyed on (a later pass re-defers the
             same seq until it dispatches — we show the latest state, not every re-defer). A deferral clears
             from view once that seq dispatches (a decision.dispatch for the same derived_from supersedes it). */}
          {(() => {
            const dispatchedSeqs = new Set(
              (events || []).filter((e: any) => e.kind === 'decision.dispatch').map((e: any) => e.derived_from))
            const seen = new Set<number>()
            const deferred = (events || [])
              .filter((e: any) => e.kind === 'decision.deferred')
              .filter((e: any) => !dispatchedSeqs.has(e.derived_from))   // already dispatched a later pass → not still deferred
              .filter((e: any) => { const s = e.derived_from; if (seen.has(s)) return false; seen.add(s); return true })
            if (!deferred.length) return null
            return (
              <div className="ibx-lane ibx-deferred" data-ui-ref="deferred-queue">
                <div className="ibx-lane-head">⏸ deferred (cap reached) <span className="muted">· {deferred.length}</span></div>
                {deferred.map((e: any) => (
                  <div key={e.seq} className="ibx-item ibx-defer-item" onClick={() => e.surfaced && openCoa(e.surfaced)}
                    title="held this pass because the dispatch concurrency cap was reached; a later pass will dispatch it">
                    held · {e.surfaced || ('seq ' + e.derived_from)} <span className="muted">— cap {e.cap}, re-offered next pass</span>
                  </div>
                ))}
              </div>
            )
          })()}
          {/* U12: resolved-for-you as its own collapsible group (audit lane — needn't be worked). */}
          {(inbox.resolved_for_you || []).length > 0 && (
            <div className="ibx-lane ibx-resolved">
              <div className="ibx-lane-head" style={{ cursor: 'pointer' }} onClick={() => setShowResolved(s => !s)}>
                {showResolved ? '⌄' : '⌃'} resolved-for-you <span className="muted">· {(inbox.resolved_for_you || []).length} (audit)</span>
              </div>
              {showResolved && (inbox.resolved_for_you || []).map((d: any) => (
                <div key={d.id} className="ibx-item ibx-done" onClick={() => openCoa(d.id)}>
                  ✓ {d.action} · {d.payload?.name || d.id}
                </div>
              ))}
            </div>
          )}
        </div>

        <h3 style={{ marginTop: 18 }}>grow · teach a new node</h3>
        <input placeholder="node name (e.g. wordcount)" value={gname} onChange={e => setGname(e.target.value)} />
        <input placeholder="what it should do" value={gspec} onChange={e => setGspec(e.target.value)} />
        <button className="b" onClick={dispatch}>dispatch build →</button>
        {surf?.error && <div className="err" style={{ marginTop: 8 }}>{surf.error}</div>}
        {surf && !surf.error && (
          <div className="surf">
            <div className="shd">⚠ surfaced for your approval · {surf.id}</div>
            {surf.coa
              ? <>
                  <div className="coa">{surf.coa}</div>
                  <button className="b ghost sm" onClick={() => setDrill(d => !d)}>{drill ? '⌃ hide raw draft' : '⌄ drill to the raw draft'}</button>
                  {drill && <pre>{surf.code}</pre>}
                </>
              : <pre>{surf.code}</pre>}
            <input className="reason" placeholder="why? (captured into the trajectory)" value={reason}
              onChange={e => setReason(e.target.value)} />
            <button className="b" onClick={approveApply}>✓ approve &amp; apply</button>
            <button className="b ghost" onClick={() => { api.resolve(surf.id, 'reject', reason); setSurf(null); setReason(''); setGrowMsg('rejected — reason captured into the path.'); poll() }}>✕ reject</button>
          </div>
        )}
        {!surf && <div className="muted" style={{ marginTop: 8 }}>{growMsg}</div>}
        <div className="muted" style={{ marginTop: 12, borderTop: '1px solid var(--line)', paddingTop: 9 }}>
          live node-types ({types.length}): {types.map(t => <span key={t} className="tg">{t}</span>)}
        </div>
        {lastChange?.sha && (
          <div className="muted" style={{ marginTop: 8 }}>
            last self-change: <span className="sig">{(lastChange.subject || '').replace('[self-apply] ', '')}</span>
            <button className="b ghost sm" style={{ marginLeft: 8 }} onClick={revertLast} title="git revert — bounded, recoverable">⟲ revert</button>
          </div>
        )}
      </div>

      <div className="hud op-panels">
        {panels.map(p => (
          <PanelErrorBoundary key={p.id} name={p.id}>
            <PanelView p={p} value={fieldValue} onSet={setField} />
          </PanelErrorBoundary>
        ))}
        {extensions.map(({ name, Comp }) => (
          <PanelErrorBoundary key={name} name={name}>
            <div className="op-panel op-ext">
              <div className="op-title">⌁ {name}</div>
              <Suspense fallback={<div className="muted">loading…</div>}><Comp /></Suspense>
            </div>
          </PanelErrorBoundary>
        ))}
      </div>

      <div className="hud activity" data-ui-ref="activity">
        <div className="act-head">
          <span className="act-title">now</span>
          {now && <span className="muted">{now.graph} · {now.nodes_resolved}/{now.nodes_total} resolved{now.surfaced_pending ? ` · ${now.surfaced_pending} awaiting you` : ''}</span>}
        </div>
        <div className="ev-list">
          {events.length === 0 && <div className="muted">no activity yet — run something.</div>}
          {events.map((e, i) => (
            <div key={e.seq ?? i} className={'ev ev-' + e.kind}>
              <span className="ev-k">{e.kind}</span>
              <span className="ev-s">{e.summary}</span>
              <span className="ev-t">{relTime(e.ts)}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="hud rhm" data-ui-ref="chat">
        <div className="rhm-head">
          right-hand-man <span className="muted">· {cfg.model || 'default model'}</span>
          <span className="cfg-gear" title="configure model + persona" onClick={() => setCfgOpen(o => !o)}>⚙</span>
        </div>
        {cfgOpen && (
          <div className="rhm-cfg">
            <input placeholder="model (e.g. deepseek-v4-flash:cloud)" value={cfg.model || ''}
              onChange={e => setCfg({ ...cfg, model: e.target.value })} />
            <input placeholder="persona / voice (optional)" value={cfg.persona || ''}
              onChange={e => setCfg({ ...cfg, persona: e.target.value })} />
            <button className="b" onClick={applyCfg}>apply config</button>
          </div>
        )}
        <div className="rhm-log">
          {chat.length === 0 && <div className="muted">ask about the system — it answers from live state, and says so when it can't see something.</div>}
          {chat.map((t, i) => (
            <div key={i} className={'msg ' + t.role}>
              <span className="who">{t.role === 'user'
                ? <>you<span className="grade gold" title="gold — Tim's own words (trains the twin)">◆</span></>
                : <>vi<span className="grade working" title="working-grade — the twin's inference, not ground truth">◇</span></>}
              </span>
              <span className="txt">{t.text}</span>
            </div>
          ))}
          {chatBusy && <div className="msg assistant"><span className="who">vi</span><span className="txt muted">thinking…</span></div>}
        </div>
        <div className="rhm-input">
          <input placeholder="ask the company about itself…" value={chatMsg}
            onChange={e => setChatMsg(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') sendChat() }} />
          <button className={'b ghost mic' + (recording ? ' rec' : '')} onClick={recordToggle}
            title="push-to-talk (voice in; speaks back in listening mode)">{recording ? '■' : '🎙'}</button>
          <button className="b" onClick={() => sendChat()} disabled={chatBusy}>{chatBusy ? '…' : '→'}</button>
        </div>
      </div>

      {workshop && (
        <div className="workshop" data-ui-ref="workshop">
          <span className="close" onClick={() => setWorkshop(null)}>✕</span>
          <h2>{workshop.nodeType} · {workshop.nodeId}</h2>
          <div className="muted">{workshop.address}</div>
          <div className="full">{workshop.output}</div>
        </div>
      )}
    </>
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
