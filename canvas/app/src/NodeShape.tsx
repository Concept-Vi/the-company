// F0 (carved from App.tsx:357–575, 484–535) · the ONE generic node shape + the edges overlay + the
// graph→shapes loader. Pure extraction — no behavior change. The shape reads its draw-truth (ports/schema)
// from the registry store (getOINFO / the CONNECT/FORCE_RUN/DRAG_CONN handles), which is reachable from
// inside tldraw (it was the 6 module globals before the carve — now one external store).
import {
  Editor, ShapeUtil, HTMLContainer, Rectangle2d, T,
  createShapeId, useEditor, useValue, stopEventPropagation, type TLBaseShape,
} from 'tldraw'
import { api } from './api'
import { getOINFO, CONNECT, DRAG_CONN, setDragConn, FORCE_RUN } from './registryStore'

// ---------------------------------------------------------------- the node shape (one generic kind)
export type NodeShape = TLBaseShape<'node', {
  w: number; h: number; nodeId: string; nodeType: string; kind: string
  status: string; output: string; address: string; ref: string; layer: string
}>

export const shapeIdFor = (nodeId: string) => createShapeId('n-' + nodeId)

// Per-port vertical placement — shared by the nub render (CSS top) AND the Edges overlay (page-space
// y), so a wire lands exactly on its port. Ports are evenly spread across the card height (NODE_H).
export const NODE_H = 130
export function portTop(i: number, n: number) {
  return ((i + 1) / (n + 1)) * NODE_H
}

export class NodeShapeUtil extends ShapeUtil<NodeShape> {
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
    const ports = getOINFO()[p.nodeType]?.ports || { inputs: {}, outputs: {} }
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
            setDragConn({ from_node: p.nodeId, from_port: port })
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
            setDragConn(null)
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
export async function loadGraph(editor: Editor) {
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

export async function refresh(editor: Editor, state?: any) {
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
export function Edges({ edges }: { edges: { from: string; from_port?: string; to: string; to_port?: string }[] }) {
  const editor = useEditor()
  const lines = useValue('edges', () => {
    editor.getCamera()                                   // subscribe to camera + zoom changes
    const z = editor.getZoomLevel()
    // page-space y of a named port on a node (mirrors portTop in the shape so wire ↔ nub line up).
    const portY = (nodeType: string, side: 'inputs' | 'outputs', port?: string) => {
      const list = Object.keys(getOINFO()[nodeType]?.ports?.[side] || {})
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
          fill="none" style={{ stroke: 'var(--acc-dim)' }} strokeWidth={1.5} />
      })}
    </svg>
  )
}
