import {
  Tldraw, Editor, ShapeUtil, HTMLContainer, Rectangle2d, T,
  createShapeId, useEditor, useValue, type TLBaseShape,
} from 'tldraw'
import { useState } from 'react'

// ---------------------------------------------------------------- api (proxied to the bridge)
const J = { 'Content-Type': 'application/json' }
const api = {
  graph: () => fetch('/api/graph').then(r => r.json()),
  types: () => fetch('/api/types').then(r => r.json()),
  run: () => fetch('/api/run', { method: 'POST' }).then(r => r.json()),
  propose: (name: string, spec: string) =>
    fetch('/api/propose', { method: 'POST', headers: J, body: JSON.stringify({ name, spec }) }).then(r => r.json()),
  resolve: (id: string, choice: string) =>
    fetch('/api/resolve', { method: 'POST', headers: J, body: JSON.stringify({ id, choice }) }).then(r => r.json()),
  apply: (id: string) =>
    fetch('/api/apply', { method: 'POST', headers: J, body: JSON.stringify({ id }) }).then(r => r.json()),
}

// ---------------------------------------------------------------- the node shape (one generic kind)
type NodeShape = TLBaseShape<'node', {
  w: number; h: number; nodeId: string; nodeType: string; kind: string
  status: string; output: string; address: string
}>

const shapeIdFor = (nodeId: string) => createShapeId('n-' + nodeId)

class NodeShapeUtil extends ShapeUtil<NodeShape> {
  static override type = 'node' as const
  static override props = {
    w: T.number, h: T.number, nodeId: T.string, nodeType: T.string, kind: T.string,
    status: T.string, output: T.string, address: T.string,
  }
  getDefaultProps(): NodeShape['props'] {
    return { w: 240, h: 130, nodeId: '', nodeType: '', kind: 'process', status: 'idle', output: '', address: '' }
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
    return (
      <HTMLContainer>
        <div className={'node-card ' + p.status}>
          <div className="node-bar">
            <span className="node-dot" />
            <span className="node-type">{p.nodeType}</span>
            <span className="node-kind">{p.kind}</span>
          </div>
          {expanded && (
            <div className="node-body">
              {hasOut
                ? <div className="node-out">{String(p.output)}</div>
                : <div className="node-out empty">no output — not yet resolved</div>}
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
        props: { status: n.status || 'idle', output: n.output == null ? '' : String(n.output) },
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

  // load once
  useState(() => {
    ;(async () => {
      const g = await loadGraph(editor); setEdges(g.edges || [])
      setTypes(await api.types())
    })()
    return null
  })

  const selected = useValue('sel', () => {
    const s = editor.getOnlySelectedShape()
    return s && s.type === 'node' ? (s as NodeShape).props : null
  }, [editor])

  async function doRun() {
    setRunning(true); setGrowMsg('resolving… presence of data at each address fires the next node')
    try { const st = await api.run(); await refresh(editor, st); setGrowMsg('run complete.') }
    finally { setRunning(false) }
  }
  async function dispatch() {
    if (!gname || !gspec) { setGrowMsg('enter a name + what it should do.'); return }
    setGrowMsg(`dispatching… the brain is writing the ${gname} node…`); setSurf(null)
    const r = await api.propose(gname, gspec)
    if (r.error) { setGrowMsg(''); setSurf({ error: r.error }) } else setSurf(r)
  }
  async function approveApply() {
    await api.resolve(surf.id, 'approve')
    const r = await api.apply(surf.id)
    if (r.error) { setSurf({ ...surf, error: r.error }) }
    else { setSurf(null); setGrowMsg(`✓ approved + applied → ${surf.name} is now a live node-type.`); setTypes(r.types) }
  }

  return (
    <>
      <Edges edges={edges} />
      <div className="hud toolbar">
        <span className="title">the&nbsp;<em>company</em></span>
        <button className="b" onClick={doRun} disabled={running}>{running ? 'running…' : '▶ run'}</button>
        <button className="b ghost" onClick={async () => { const g = await loadGraph(editor); setEdges(g.edges || []) }}>reload</button>
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

        <h3 style={{ marginTop: 18 }}>grow · teach a new node</h3>
        <input placeholder="node name (e.g. wordcount)" value={gname} onChange={e => setGname(e.target.value)} />
        <input placeholder="what it should do" value={gspec} onChange={e => setGspec(e.target.value)} />
        <button className="b" onClick={dispatch}>dispatch build →</button>
        {surf?.error && <div className="err" style={{ marginTop: 8 }}>{surf.error}</div>}
        {surf && !surf.error && (
          <div className="surf">
            <div className="shd">⚠ surfaced for your approval · {surf.id}</div>
            <pre>{surf.code}</pre>
            <button className="b" onClick={approveApply}>✓ approve &amp; apply</button>
            <button className="b ghost" onClick={() => { api.resolve(surf.id, 'reject'); setSurf(null); setGrowMsg('rejected.') }}>✕ reject</button>
          </div>
        )}
        {!surf && <div className="muted" style={{ marginTop: 8 }}>{growMsg}</div>}
        <div className="muted" style={{ marginTop: 12, borderTop: '1px solid var(--line)', paddingTop: 9 }}>
          live node-types ({types.length}): {types.map(t => <span key={t} className="tg">{t}</span>)}
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
        persistenceKey="company-canvas"
        components={{ StylePanel: null, ActionsMenu: null, QuickActions: null }}
      >
        <Hud />
      </Tldraw>
    </div>
  )
}
