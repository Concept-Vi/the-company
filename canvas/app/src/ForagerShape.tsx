// FORAGER v1 (S7-FE) · the SECOND shape vocabulary on the one canvas: corpus search hits as CIRCLES
// ('f-' ids, Circle2d) living BESIDE the graph's rectangular NodeShapes ('n-' ids) — visually distinct,
// never rearranging the graph. Mirrors NodeShape.tsx exactly (TLBaseShape + T.* validators + HTMLContainer
// + the zoom>0.5 semantic zoom), per the Context Forager Implementation Guide.
//
// THE COEXISTENCE RULE (A2, make-or-break): the graph loader's prune filters `shape.type === 'node'`
// (NodeShape.tsx loadGraph — verified in place, untouched), so it NEVER eats forager circles; the
// forager's own clear (clearForagerShapes below) filters `type === 'forager'`, so it never touches
// 'n-' shapes. Two loaders, two id prefixes, two type filters — each blind to the other's shapes.
//
// VIEW-SIDE ONLY (the don't): forager circles are session-local sculpting material — they never enter
// the backend graph store (run:// stays backend-truth). The drag write-back listener filters
// `to.type !== 'node'` (useAppController), so dragging a circle never fires /api/move. Native tldraw
// selection + Delete work on circles untouched (B1 — whittling is the stock delete, no confirm friction).
import {
  Editor, ShapeUtil, HTMLContainer, Circle2d, T,
  createShapeId, useEditor, useValue, type TLBaseShape,
} from 'tldraw'

// the circle's props — the guide's exact field set {w,h,address,label,kind,session,score,content_head}
// + `hits` (the re-hit counter that drives the dedupe pulse: a re-hit increments it, the inner div is
// keyed by it, so the land animation REPLAYS — prop-driven, no DOM poking). Adding a prop is why the
// persistenceKey bumped to company-canvas-v4 (the stale-snapshot lesson — App.tsx comment).
export type ForagerShape = TLBaseShape<'forager', {
  w: number; h: number; address: string; label: string; kind: string; session: string
  score: number; content_head: string; hits: number
}>

// the shape every hit becomes — one fixed diameter (the circle reads by SHAPE at distance, not size)
export const FORAGER_D = 128

// 'f-' id convention (the coexistence rule's other half): a STABLE id per corpus address, so dedupe is
// structural (same address → same shape id → update, never a duplicate). djb2 over the address — corpus
// addresses carry chars (://, #) that don't belong in an id, so we hash rather than embed.
function hashAddr(s: string): string {
  let h = 5381
  for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0
  return (h >>> 0).toString(36)
}
export const foragerIdFor = (address: string) => createShapeId('f-' + hashAddr(address))

// a recognizable label from the address tail (the FORM bar: circles read by sight at zoom) —
// scheme dropped, last two path segments, bounded.
export function foragerLabel(address: string): string {
  const tail = address.replace(/^[a-z0-9+.-]+:\/\//i, '')
  const segs = tail.split('/').filter(Boolean)
  return (segs.slice(-2).join('/') || tail).slice(0, 42)
}

export class ForagerShapeUtil extends ShapeUtil<ForagerShape> {
  static override type = 'forager' as const
  static override props = {
    w: T.number, h: T.number, address: T.string, label: T.string, kind: T.string,
    session: T.string, score: T.number, content_head: T.string, hits: T.number,
  }
  getDefaultProps(): ForagerShape['props'] {
    return { w: FORAGER_D, h: FORAGER_D, address: '', label: '', kind: '', session: '', score: 0, content_head: '', hits: 1 }
  }
  // Circle2d — the TRUE circular hit-area (research: exported by tldraw 3.15.6). The circle fills the
  // shape's w×h box (top-left geometry like every tldraw shape), so select/drag/delete land on the disc.
  // CHIP-HIDDEN (C1): a filtered-out circle rides opacity 0 (the TOP-LEVEL tldraw field — no shape-prop
  // churn, the v4 snapshot schema untouched); its geometry collapses to a point so an invisible circle
  // can't be click/box-selected into the D1 builder set unseen. Geometry recomputes on the record change
  // (records are immutable — an opacity update is a new record), so hide/reveal tracks live.
  getGeometry(shape: ForagerShape) {
    if (shape.opacity === 0) return new Circle2d({ radius: 0.5, isFilled: false })
    return new Circle2d({ radius: shape.props.w / 2, isFilled: true })
  }
  override canResize = () => false
  override hideRotateHandle = () => true

  component(shape: ForagerShape) {
    const editor = useEditor()
    const zoom = useValue('zoom', () => editor.getZoomLevel(), [editor])   // semantic zoom — NodeShape's exact pattern
    const p = shape.props
    const expanded = zoom > 0.5
    // CHIP-HIDDEN (C1): render nothing while filtered out (the container is already invisible at
    // opacity 0; skipping the body also makes the REVEAL replay the land gesture — the keyed remount).
    if (shape.opacity === 0) return <HTMLContainer />
    // A1 FORM · the score-tinted ring: cosine score → how much SIGNAL the ring carries. Token-DERIVED
    // (color-mix off --sig/--line — the established app.css pattern, e.g. the aurora/bi-outcome-bad),
    // never an invented literal. score may be absent (0) → the ring rests at the base line tint.
    const pct = Math.max(10, Math.min(100, Math.round((p.score || 0) * 100)))
    const ring = `color-mix(in srgb, var(--sig) ${pct}%, var(--line))`
    return (
      <HTMLContainer>
        {/* data-ui-ref = the corpus address (an EXPRESSION, not a quoted literal — same reasoning as
            NodeShape's run:// stamp: corpus addresses are live record addresses, not ui:// registry
            entries). It is what lets indicate(address) paint the .ui-indicated ring on THIS disc. */}
        {/* key={p.hits}: a RE-HIT (dedupe by address) increments hits → React remounts this div →
            the land/pulse animation replays. Announce without duplication (B2). */}
        <div key={p.hits} data-ui-ref={p.address} className="forager-circle land" style={{ borderColor: ring }}
          title={p.address}>
          {!expanded && <span className="fc-label">{p.label || p.address}</span>}
          {expanded && (
            <>
              {/* B3-light · the zoomed body IS the in-place River detail: what it is (kind), where it
                  came from (session), what it says (head) — the click adds indicate(address). */}
              <span className="fc-kind">{p.kind || 'record'}{p.session ? ' · ' + p.session : ''}</span>
              <span className="fc-label">{p.label || p.address}</span>
              {p.content_head && <span className="fc-head">{p.content_head}</span>}
            </>
          )}
        </div>
      </HTMLContainer>
    )
  }
  indicator(shape: ForagerShape) {
    return <circle cx={shape.props.w / 2} cy={shape.props.h / 2} r={shape.props.w / 2} />
  }
}

// ---------------------------------------------------------------- the forager loader (hits → circles)
// One hit row as /api/corpus-query serves it (bridge.py S7: address · score · kind · projection ·
// session · ts_source · head). head is ALREADY ≤400ch server-side.
export type ForagerHit = {
  address: string; score?: number | null; kind?: string | null
  projection?: string | null; session?: string | null; ts_source?: string | null; head?: string | null
}

// update-or-create with DEDUPE BY ADDRESS (B2: successive searches ADD; a re-hit PULSES, never dupes).
// New circles land near the VIEWPORT CENTER in a loose grid (deterministic per-address jitter keeps it
// organic, not a lattice); an existing circle is NEVER moved (the operator's sculpting layout is theirs —
// the don't: never rearrange). SLOT OCCUPANCY: each grid slot is checked against every circle already on
// the canvas (and this batch's own placements), so a SECOND search flows AROUND the first batch instead
// of stacking on the same center slots — successive searches ADD legibly (B2), and a slot the operator
// dragged a circle out of becomes placeable again. Mirrors loadGraph's update/create discipline, scoped
// to type==='forager'.
export function placeForagerHits(editor: Editor, hits: ForagerHit[]): { created: number; pulsed: number } {
  const existing = editor.getCurrentPageShapes().filter(s => s.type === 'forager') as ForagerShape[]
  const byAddr = new Map(existing.map(s => [s.props.address, s]))
  const taken = existing.map(s => ({ x: s.x, y: s.y }))     // occupied positions (live set + this batch below)
  const c = editor.getViewportPageBounds().center
  const COLS = 4, GX = 168, GY = 152
  let placed = 0, created = 0, pulsed = 0
  for (const h of hits) {
    if (!h?.address) continue
    const props = {
      w: FORAGER_D, h: FORAGER_D, address: h.address, label: foragerLabel(h.address),
      kind: h.kind || '', session: h.session || '', score: typeof h.score === 'number' ? h.score : 0,
      content_head: h.head || '',
    }
    const prev = byAddr.get(h.address)
    if (prev) {
      // RE-HIT: refresh the record fields + bump hits → the keyed inner div remounts → the pulse.
      editor.updateShape<ForagerShape>({
        id: prev.id, type: 'forager', props: { ...props, hits: (prev.props.hits || 1) + 1 },
      })
      pulsed++
      continue
    }
    const id = foragerIdFor(h.address)
    if (editor.getShape(id)) continue                       // hash-collision guard (different address, same id) — skip, never clobber
    const n = parseInt(hashAddr(h.address), 36)
    const jx = (n % 37) - 18, jy = ((n >> 3) % 33) - 16     // deterministic per-address jitter → the LOOSE grid
    // walk the grid (center outward, row-major) to the first UNOCCUPIED slot — bounded, never spins.
    let x = 0, y = 0, guard = 0
    do {
      const col = placed % COLS, row = Math.floor(placed / COLS)
      x = c.x - ((COLS - 1) * GX) / 2 + col * GX - FORAGER_D / 2 + jx
      y = c.y - GY + row * GY - FORAGER_D / 2 + jy
      placed++; guard++
    } while (guard < 400 && taken.some(t => Math.abs(t.x - x) < GX * 0.55 && Math.abs(t.y - y) < GY * 0.55))
    taken.push({ x, y })
    editor.createShape<ForagerShape>({ id, type: 'forager', x, y, props: { ...props, hits: 1 } })
    created++
  }
  return { created, pulsed }
}

// THE FORAGER'S CLEAR — the coexistence rule's second half: filters type === 'forager' ONLY, so it can
// never touch an 'n-' graph shape (A2). The mirror of loadGraph's prune filtering type === 'node'.
export function clearForagerShapes(editor: Editor): number {
  const ids = editor.getCurrentPageShapes().filter(s => s.type === 'forager').map(s => s.id)
  if (ids.length) editor.deleteShapes(ids)
  return ids.length
}

// ---------------------------------------------------------------- selection (the D1 handoff read)
// The hook ClaudeChat reads the selected circles through. The mission prefers a hook over window
// globals; we go one better than mirroring into registryStore — registryStore's own constitution says
// editor/graph state must NEVER get a second source of truth there, and tldraw's useValue IS the same
// subscribe/snapshot external-store pattern, read straight off the ONE truth (the editor's selection).
// Works in any component below <Tldraw> (ClaudeChat mounts inside Hud, which is inside <Tldraw>).
export function useForagerSelection(): ForagerShape[] {
  const editor = useEditor()
  return useValue('forager selection',
    () => editor.getSelectedShapes().filter(s => s.type === 'forager') as ForagerShape[], [editor])
}
