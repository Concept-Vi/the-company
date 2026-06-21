import { useEffect, useRef } from 'react'
import { useBoard, openBoard, closeBoard } from './boardStore'
import './board.css'

// THE BOARD-VIEW SURFACE (FACE-1 breadth surface #2) — the fabric Noticeboard as GROUPED sections (by type, or
// state): each group a header (name + count) over its item rows. An App-root SIBLING OVERLAY (the ChannelView/
// SessionDrill/GalleryMount pattern — host seam 1). The RENDER is DNA's (boardRecord adapter + boardGroups organism
// + the 'board-view' archetype, render_kind=zones) — NO bespoke list (from-DNA law); the host frames it +
// SCROLLS it (a board runs long → a scrollable list body, NOT centered like the channel graph). Data is LIVE
// (/api/board via boardStore). Opens on the `board:open` window event (the entry verb/chrome is DNA's design lane).
//
// RENDER CONTRACT (grounded, the archetype's own "about"): boardRecord(rows,{groupBy}) → {identity,groups,total};
// DNA.org.boardGroups({groups}) → the grouped-sections HTML; renderArchetype('board-view', record, {visualDevice:
// <html>}) → the body shape slot returns opts.visualDevice (archetype.js). slot_map: where→address (kicker),
// name→title (title). Mirrors channel-view exactly (graph→groups is the only swap).

type DNAGlobal = {
  faceRecord?: { boardRecord?: (rows: unknown, opts?: unknown) => { groups?: unknown[] } & Record<string, unknown> }
  org?: { boardGroups?: (o: unknown) => string }
  renderArchetype?: (archetype: unknown, record: unknown, opts: unknown) => HTMLElement
  _boardViewArchetype?: unknown
}
const dna = () => (window as unknown as { DNA?: DNAGlobal }).DNA

export function BoardView() {
  const { rows, loading, error, open } = useBoard()
  const bodyRef = useRef<HTMLDivElement>(null)

  // open on `board:open`; Esc closes (mirrors the other overlays).
  useEffect(() => {
    const onOpen = () => openBoard()
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && open) closeBoard()
    }
    window.addEventListener('board:open', onOpen)
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('board:open', onOpen)
      window.removeEventListener('keydown', onKey)
    }
  }, [open])

  // MOUNT DNA's board-groups. Load the board-view archetype once (cached on DNA), adapt the raw rows → the grouped
  // record, render through the ONE generic renderArchetype with boardGroups as the visual device, append. Degrade-
  // clean: DNA not loaded / no archetype / adapter throws → an honest line (never a crash).
  useEffect(() => {
    const host = bodyRef.current
    if (!host || !open || rows.length === 0) return
    let cancelled = false
    ;(async () => {
      const D = dna()
      if (!D?.renderArchetype || !D.faceRecord?.boardRecord || !D.org?.boardGroups) {
        host.textContent = 'The board view isn’t ready yet.'
        return
      }
      if (!D._boardViewArchetype) {
        try {
          const ly = await (await fetch('/dna/layouts.json')).json()
          D._boardViewArchetype = ly.archetypes?.['board-view']
        } catch {
          /* local + reliable; a fetch fail degrades below */
        }
      }
      if (cancelled || bodyRef.current !== host) return
      try {
        const rec = D.faceRecord.boardRecord(rows, {}) // groupBy defaults to 'type'
        const device = D.org.boardGroups({ groups: rec.groups, w: 720 })
        const el = D.renderArchetype(D._boardViewArchetype, rec, { visualDevice: device })
        host.replaceChildren(el)
      } catch {
        host.textContent = 'Couldn’t draw the board just now.'
      }
    })()
    return () => {
      cancelled = true
    }
  }, [open, rows])

  return (
    <div className={`board-overlay ${open ? 'board-overlay--open' : ''}`} aria-hidden={!open}>
      <div className="board-scrim" onClick={closeBoard} />
      <div className="board-panel" role="dialog" aria-label="The board" aria-modal="true">
        <header className="board-head">
          <div className="board-head-text">
            <h2 className="board-title">The board</h2>
            <p className="board-sub">Everything the Company has noted — grouped by kind.</p>
          </div>
          <button className="board-close" onClick={closeBoard} aria-label="close">
            ✕
          </button>
        </header>
        <div className="board-body">
          {error && (
            <p className="board-msg board-msg--error">
              {error} <button className="board-retry" onClick={openBoard}>Try again</button>
            </p>
          )}
          {!error && loading && rows.length === 0 && <p className="board-msg">Looking…</p>}
          {!error && !loading && rows.length === 0 && (
            <p className="board-msg board-msg--quiet">Nothing on the board right now.</p>
          )}
          {/* DNA's grouped board mounts here (full-width, scrolls) */}
          {rows.length > 0 && <div className="board-groups" ref={bodyRef} />}
        </div>
      </div>
    </div>
  )
}
