import {
  Tldraw, Editor, ShapeUtil, HTMLContainer, Rectangle2d, T,
  createShapeId, useEditor, useValue, type TLBaseShape,
} from 'tldraw'
import { useState, useRef, Component } from 'react'

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
  run: () => fetch('/api/run', { method: 'POST' }).then(r => r.json()),
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

function relTime(iso?: string) {
  if (!iso) return ''
  const d = (Date.now() - new Date(iso).getTime()) / 1000
  if (d < 1) return 'now'
  if (d < 60) return `${Math.floor(d)}s`
  if (d < 3600) return `${Math.floor(d / 60)}m`
  return `${Math.floor(d / 3600)}h`
}

// Self-coded extensions — brain-authored .tsx components, build-gated before promotion here,
// loaded additively. Each is wrapped in PanelErrorBoundary so a runtime throw is contained.
// New files appear via Vite HMR re-evaluating the glob. (Operator-only; git-reversible.)
const extensionMods = import.meta.glob('./extensions/*.tsx', { eager: true })

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

// ---------------------------------------------------------------- the node shape (one generic kind)
type NodeShape = TLBaseShape<'node', {
  w: number; h: number; nodeId: string; nodeType: string; kind: string
  status: string; output: string; address: string; ref: string; layer: string
}>

const shapeIdFor = (nodeId: string) => createShapeId('n-' + nodeId)

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
          {expanded && <div className="node-addr">{p.address}{p.status !== 'idle' ? ` · ${p.status}` : ''}</div>}
        </div>
      </HTMLContainer>
    )
  }
  indicator(shape: NodeShape) {
    return <rect width={shape.props.w} height={shape.props.h} rx={4} />
  }
}

// ---------------------------------------------------------------- load / refresh graph -> shapes
async function loadGraph(editor: Editor) {
  const g = await api.graph()
  const existing = editor.getCurrentPageShapes().filter(s => s.type === 'node')
  if (existing.length) editor.deleteShapes(existing.map(s => s.id))
  g.nodes.forEach((n: any, i: number) => {
    editor.createShape<NodeShape>({
      id: shapeIdFor(n.id), type: 'node', x: 150 + i * 300, y: 220,
      props: {
        w: 240, h: 130, nodeId: n.id, nodeType: n.type, kind: n.kind || 'process',
        status: n.status || 'idle', output: n.output == null ? '' : String(n.output), address: n.address || '',
        ref: (n.config && n.config.ref) || '', layer: n.layer || 'authored',
      },
    })
  })
  editor.zoomToFit({ animation: { duration: 200 } })
  return g
}

async function refresh(editor: Editor, state?: any) {
  const g = state || await api.graph()
  g.nodes.forEach((n: any) => {
    const id = shapeIdFor(n.id)
    if (editor.getShape(id)) {
      editor.updateShape<NodeShape>({
        id, type: 'node',
        props: { status: n.status || 'idle', output: n.output == null ? '' : String(n.output), layer: n.layer || 'authored' },
      })
    }
  })
  return g
}

// ---------------------------------------------------------------- edges overlay (reactive, screen-space)
function Edges({ edges }: { edges: { from: string; to: string }[] }) {
  const editor = useEditor()
  const lines = useValue('edges', () => {
    editor.getCamera()                                   // subscribe to camera changes
    return edges.map(e => {
      const a = editor.getShapePageBounds(shapeIdFor(e.from))
      const b = editor.getShapePageBounds(shapeIdFor(e.to))
      if (!a || !b) return null
      const p1 = editor.pageToScreen({ x: a.maxX, y: a.midY })
      const p2 = editor.pageToScreen({ x: b.minX, y: b.midY })
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
  const [edges, setEdges] = useState<{ from: string; to: string }[]>([])
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

  async function poll() {
    try { setNow(await api.now()); setEvents(await api.events()); setInbox(await api.inbox()); setLastChange(await api.lastChange()); setPanels(await api.panels()) } catch { /* bridge transient */ }
  }
  async function openCoa(id: string) {
    setGrowMsg('compiling the decision into a value-choice…')
    const c = await api.coa(id)            // decision-compiler UP
    setSurf({ id: c.id, name: c.raw?.name, code: c.raw?.code, coa: c.framing }); setDrill(false)
  }

  // load once + a heartbeat so the surfaces stay live (now-view · presence · event log)
  useState(() => {
    ;(window as any).__editor = editor   // automation/debug handle
    ;(async () => {
      const g = await loadGraph(editor); setEdges(g.edges || []); setGid(g.id)
      setTypes(await api.types())
      setOinfo(await api.objectInfo())
      setChat(await api.chatHistory())
      setCfg(await api.rhmConfig())
      await poll()
    })()
    setInterval(poll, 2500)              // single-mount app; heartbeat is the presence pulse
    return null
  })

  async function reload() { const g = await loadGraph(editor); setEdges(g.edges || []); await poll(); await maybeReact() }
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

  async function doRun() {
    setRunning(true); setGrowMsg('resolving… presence of data at each address fires the next node')
    try { const st = await api.run(); await refresh(editor, st); setGrowMsg('run complete.'); await poll(); await maybeReact() }
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
            <div className="row"><span className="k">status</span><span>{selected.status}</span></div>
            <div className="row"><span className="k">address</span></div>
            <div className="muted" style={{ wordBreak: 'break-all' }}>{selected.address}</div>
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
        {Object.entries(extensionMods).map(([path, mod]) => {
          const C = (mod as any).default
          const name = (path.split('/').pop() || 'ext').replace('.tsx', '')
          if (!C) return null
          return (
            <PanelErrorBoundary key={path} name={name}>
              <div className="op-panel op-ext"><div className="op-title">⌁ {name}</div><C /></div>
            </PanelErrorBoundary>
          )
        })}
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
