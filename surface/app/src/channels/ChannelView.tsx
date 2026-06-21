import { useEffect, useRef } from 'react'
import { useChannels, openChannels, closeChannels } from './channelStore'
import './channels.css'

// THE CHANNEL-VIEW SURFACE (FACE-1 breadth #1) — the live fabric as a GRAPH: channels as weighted hub-spokes
// (the fabric octagon hub + a spoke per channel, posts→proximity, recency→warmth). An App-root SIBLING OVERLAY
// (the SessionDrill/GalleryMount/DecisionsInbox pattern — host seam 1). The RENDER is DNA's (channelGraph adapter
// + hubNetwork organism + the 'channel-view' archetype, shipped 35aa95c) — NO bespoke graph (from-DNA law); the
// host frames it FULL-WIDTH CENTERED (a graph body must NOT inherit the decision-card 2-col layout — DNA's note:
// the graph right-shifts/cuts under 2-col). Data is LIVE (/api/channels via channelStore). Opens on the
// `channels:open` window event (the entry verb/chrome is DNA's design lane — a follow, like SessionDrill).
//
// RENDER CONTRACT (grounded, archetype's own "about"): channelGraph(rawChannels) → {identity,nodes,edges,hub};
// hubNetwork(nodes) → SVG; renderArchetype('channel-view', record, {visualDevice: <SVG>}) → the shape slot
// returns opts.visualDevice (archetype.js:48). NORMALIZE members object→ids at the call site (channelGraph's
// edges loop assumes members is an array but /api/channels serves an object — flagged to DNA, code-grounded).

type DNAGlobal = {
  faceRecord?: { channelGraph?: (raw: unknown) => { nodes?: unknown[] } & Record<string, unknown> }
  org?: { hubNetwork?: (o: unknown) => string }
  renderArchetype?: (archetype: unknown, record: unknown, opts: unknown) => HTMLElement
  _channelViewArchetype?: unknown
}
const dna = () => (window as unknown as { DNA?: DNAGlobal }).DNA

export function ChannelView() {
  const { channels, loading, error, open } = useChannels()
  const graphRef = useRef<HTMLDivElement>(null)

  // open on `channels:open`; Esc closes (mirrors the other overlays).
  useEffect(() => {
    const onOpen = () => openChannels()
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && open) closeChannels()
    }
    window.addEventListener('channels:open', onOpen)
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('channels:open', onOpen)
      window.removeEventListener('keydown', onKey)
    }
  }, [open])

  // MOUNT DNA's fabric graph (the 35aa95c drop-in). Load the channel-view archetype once (cached on DNA), adapt the
  // raw rows → the graph record, render through the ONE generic renderArchetype with hubNetwork as the visual
  // device, append. Degrade-clean: DNA not loaded / no archetype / adapter throws → an honest line (never a crash).
  useEffect(() => {
    const host = graphRef.current
    if (!host || !open || channels.length === 0) return
    let cancelled = false
    ;(async () => {
      const D = dna()
      if (!D?.renderArchetype || !D.faceRecord?.channelGraph || !D.org?.hubNetwork) {
        host.textContent = 'The fabric view isn’t ready yet.'
        return
      }
      if (!D._channelViewArchetype) {
        try {
          const ly = await (await fetch('/dna/layouts.json')).json()
          D._channelViewArchetype = ly.archetypes?.['channel-view']
        } catch {
          /* local + reliable; a fetch fail degrades below */
        }
      }
      if (cancelled || graphRef.current !== host) return
      try {
        // normalize members object→ids (channelGraph's edges loop expects an array; /api/channels serves an object)
        const raw = channels.map((c) => ({ ...c, members: Object.keys(c.members || {}) }))
        const rec = D.faceRecord.channelGraph(raw)
        const device = D.org.hubNetwork({ nodes: rec.nodes, hub: 'octagon', weighted: true, organic: true, w: 600, h: 440 })
        const el = D.renderArchetype(D._channelViewArchetype, rec, { visualDevice: device })
        host.replaceChildren(el)
      } catch {
        host.textContent = 'Couldn’t draw the fabric just now.'
      }
    })()
    return () => {
      cancelled = true
    }
  }, [open, channels])

  return (
    <div className={`channels-overlay ${open ? 'channels-overlay--open' : ''}`} aria-hidden={!open}>
      <div className="channels-scrim" onClick={closeChannels} />
      <div className="channels-panel" role="dialog" aria-label="The fabric" aria-modal="true">
        <header className="channels-head">
          <div className="channels-head-text">
            <h2 className="channels-title">The fabric</h2>
            <p className="channels-sub">Every channel the Company is working through — as a living map.</p>
          </div>
          <button className="channels-close" onClick={closeChannels} aria-label="close">
            ✕
          </button>
        </header>
        <div className="channels-body">
          {error && (
            <p className="channels-msg channels-msg--error">
              {error} <button className="channels-retry" onClick={openChannels}>Try again</button>
            </p>
          )}
          {!error && loading && channels.length === 0 && <p className="channels-msg">Looking…</p>}
          {!error && !loading && channels.length === 0 && (
            <p className="channels-msg channels-msg--quiet">No channels in the fabric right now.</p>
          )}
          {/* DNA's fabric graph mounts here (full-width centered) */}
          {channels.length > 0 && <div className="channels-graph" ref={graphRef} />}
        </div>
      </div>
    </div>
  )
}
