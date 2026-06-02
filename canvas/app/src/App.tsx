import {
  Tldraw, Editor, ShapeUtil, HTMLContainer, Rectangle2d, T,
  createShapeId, useEditor, useValue, stopEventPropagation, type TLBaseShape,
} from 'tldraw'
import { useState, useRef, Component, lazy, Suspense } from 'react'

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
  react: () => fetch('/api/react', { method: 'POST' }).then(r => r.json()),
  lastChange: () => fetch('/api/last-change').then(r => r.json()),
  revert: (sha: string) => fetch('/api/revert', { method: 'POST', headers: J, body: JSON.stringify({ sha }) }).then(r => r.json()),
  panels: () => fetch('/api/panels').then(r => r.json()),
  voice: () => fetch('/api/voice').then(r => r.json()),
  stt: (blob: Blob) => fetch('/api/stt', { method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: blob }).then(r => r.json()),
  tts: (text: string) => fetch('/api/tts', { method: 'POST', headers: J, body: JSON.stringify({ text }) }).then(r => r.blob()),
}

const MODES = ['listening', 'text-only', 'background', 'focus', 'walkthrough', 'watch-and-react', 'decide-for-me', 'off']

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
    const statusLabel = p.status === 'ran' ? 'ran' : p.status === 'cached' ? 'cached ↺' : p.status

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
              {hasOut
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
  const [types, setTypes] = useState<string[]>([])
  const [gname, setGname] = useState('')
  const [gspec, setGspec] = useState('')
  const [surf, setSurf] = useState<any>(null)
  const [growMsg, setGrowMsg] = useState('the brain writes it · you approve · it goes live.')
  const [workshop, setWorkshop] = useState<any>(null)
  const [oinfo, setOinfo] = useState<any>({})
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
  const [inbox, setInbox] = useState<any>({ live_escalations: [], resolved_for_you: [], counts: { escalations: 0, resolved: 0 } })
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
      const g = await loadGraph(editor); setEdges(g.edges || []); setGid(g.id); syncConfig(g)
      setTypes(await api.types())
      setChat(await api.chatHistory())
      setCfg(await api.rhmConfig())
      const evs = await api.events(); mergeEvents(setEvents, evs)
      streamSeq.current = evs.reduce((m: number, e: any) => Math.max(m, e.seq ?? -1), -1)  // cursor = last seen
      setNow(await api.now()); setInbox(await api.inbox()); setLastChange(await api.lastChange()); setPanels(await api.panels())
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
        const g = await loadGraph(editor); setEdges(g.edges || []); syncConfig(g)
        try { setNow(await api.now()) } catch { /* */ }
      } else if (k === 'mode' || k === 'config') {
        try { setNow(await api.now()); setCfg(await api.rhmConfig()) } catch { /* */ }
      } else if (k === 'ask' || k === 'reject' || k === 'resolve' || k === 'apply' || k === 'grow' || k === 'revert') {
        try { setInbox(await api.inbox()); setNow(await api.now()); setLastChange(await api.lastChange()); setPanels(await api.panels()) } catch { /* */ }
      } else if (k === 'chat' || k === 'react') {
        try { setChat(await api.chatHistory()) } catch { /* */ }
      } else {
        try { setNow(await api.now()) } catch { /* */ }
      }
    }
    es.onerror = () => { /* EventSource auto-reconnects; Last-Event-ID gives gapless resume */ }
  }

  async function reload() { const g = await loadGraph(editor); setEdges(g.edges || []); syncConfig(g); await poll(); await maybeReact() }
  async function maybeReact() {   // watch-and-react: backend-gated, comments only in that mode
    try { const r = await api.react(); if (r.comment) setChat(await api.chatHistory()) } catch { /* */ }
  }
  async function addNode(type: string) { setNotice('+ ' + type); await api.addNode(type); await reload() }
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
  async function deleteSelected() {
    const sel = (editor.getSelectedShapes().filter(s => s.type === 'node') as NodeShape[])
    for (const s of sel) await api.del(s.props.nodeId)
    if (sel.length) { setNotice(`deleted ${sel.length} node(s)`); await reload() }
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
      if (now?.mode === 'listening' && r.reply) speakReply(r.reply)   // voice out: speak the reply
      // the decision-compiler DOWN: an action the RHM took routes through the gate
      if (r.action?.did === 'run' || r.action?.did === 'build') { await reload() }
      if (r.action?.did === 'show') {           // attention-direction: move the operator's view
        const ids = r.action.targets.map((nid: string) => shapeIdFor(nid)).filter((id: any) => editor.getShape(id))
        if (ids.length) { editor.select(...ids); editor.zoomToSelection({ animation: { duration: 450 } }) }
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

  const selected = useValue('sel', () => {
    const s = editor.getOnlySelectedShape()
    return s && s.type === 'node' ? (s as NodeShape).props : null
  }, [editor])

  // D4: run the graph; `force` (a node-id list) bypasses the memo gate for just those nodes. D5: the run
  // result reports ran/cached per node — refresh() writes those statuses onto the cards (legible rerun).
  async function doRun(force?: string[]) {
    setRunning(true)
    setGrowMsg(force ? `force re-running ${force.join(', ')} (past the memo cache)…`
                     : 'resolving… presence of data at each address fires the next node')
    try {
      const st = await api.run(force); await refresh(editor, st)
      const ran = (st.nodes || []).filter((n: any) => n.status === 'ran').length
      const cached = (st.nodes || []).filter((n: any) => n.status === 'cached').length
      setGrowMsg(`run complete · ${ran} ran · ${cached} cached.`); await poll(); await maybeReact()
    }
    finally { setRunning(false) }
  }
  async function dispatch() {
    if (!gname || !gspec) { setGrowMsg('enter a name + what it should do.'); return }
    setGrowMsg(`dispatching… the brain is writing the ${gname} node…`); setSurf(null)
    const r = await api.propose(gname, gspec)
    if (r.error) { setGrowMsg(''); setSurf({ error: r.error }) } else setSurf(r)
    await poll()
  }
  // voice out — speak the RHM's reply (local Kokoro via the bridge)
  async function speakReply(text: string) {
    try { const blob = await api.tts(text); new Audio(URL.createObjectURL(blob)).play() } catch { /* */ }
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
          if (r.text) { setNotice('you said: ' + r.text); await sendChat(r.text) }
          else setNotice('(no speech detected)')
        } catch (e: any) { setNotice('STT error: ' + (e?.message || e)) }
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
      <div className="hud toolbar">
        <span className="title">the&nbsp;<em>company</em></span>
        {now && (
          <span className={'presence ' + (now.mode === 'off' ? 'off' : running || chatBusy ? 'busy' : now.surfaced_pending ? 'warn' : 'ok')}>
            <span className="pdot" />{running ? 'running…' : chatBusy ? 'thinking…' : now.presence}
          </span>
        )}
        {now && (
          <select className="mode-sel" value={now.mode || 'listening'} onChange={e => changeMode(e.target.value)} title="presence dial — the RHM's mode">
            {MODES.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        )}
        <button className="b" onClick={doRun} disabled={running}>{running ? 'running…' : '▶ run'}</button>
        <button className="b ghost" onClick={wireSelected}>＋ wire</button>
        <button className="b ghost" onClick={portalSelected}>⊕ portal</button>
        <button className="b ghost" onClick={deleteSelected}>🗑 delete</button>
        <button className="b ghost" onClick={cycleLayers}>◐ layers: {['all', 'origin', 'system'][layerView]}</button>
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

      <div className="hud panel">
        {selected ? (
          <>
            <h3>{selected.nodeType} · {selected.nodeId}</h3>
            <div className="row"><span className="k">kind</span><span>{selected.kind}</span></div>
            <div className="row">
              <span className="k">status</span>
              <span>
                {selected.status === 'cached' ? 'cached ↺' : selected.status}
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
            {selected.output && <button className="b ghost" onClick={() => setWorkshop(selected)}>open workshop ⤢</button>}
          </>
        ) : <div className="muted">select a node to inspect it. pan/zoom the canvas; zoom in for detail (semantic zoom).</div>}

        <h3 style={{ marginTop: 18 }}>inbox · chief-of-staff triage</h3>
        <div className="ibx-head">
          <span className="sig">{inbox.counts?.escalations || 0} awaiting you</span>
          <span className="muted"> · {inbox.counts?.resolved || 0} resolved-for-you</span>
        </div>
        {(inbox.live_escalations || []).map((d: any) => (
          <div key={d.id} className="ibx-item" onClick={() => openCoa(d.id)}>
            ⚠ {d.action} · {d.payload?.name || d.id} <span className="muted">— compile ↗</span>
          </div>
        ))}
        {(inbox.counts?.escalations || 0) === 0 && <div className="muted">nothing awaiting you.</div>}

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

      <div className="hud activity">
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

      <div className="hud rhm">
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
        <div className="workshop">
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
