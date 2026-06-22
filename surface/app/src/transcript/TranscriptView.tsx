import { useEffect, useRef } from 'react'
import { useTranscript, openTranscript, closeTranscript, searchTranscript, setTranscriptQuery } from './transcriptStore'
import './transcript.css'

// THE TRANSCRIPT-VIZ SURFACE (FACE-1 breadth) — the WHOLE corpus (35,904 chunks · 1,051 sessions) searched BY MEANING
// and shown as a CONSTELLATION: one star per session, brightness = relevance (cosine), size = hits, color = state.
// An App-root SIBLING OVERLAY (the ChannelView/BoardView/SessionDrill pattern — host seam 1). The RENDER is DNA's
// (transcriptRecord adapter + constellation organism + the 'transcript-viz' archetype, all shipped) — NO bespoke
// graph (from-DNA law); the host frames it FULL-WIDTH CENTERED (a graph body must NOT inherit the decision-card
// 2-col layout — same hazard channel-view hit). Data is LIVE (/api/transcript-search via transcriptStore). Opens on
// the `transcript:open` window event. QUERY-DRIVEN: opening shows a search prompt; a query loads + draws the result set.
//
// RENDER CONTRACT (grounded, archetype's own "about", verified live): transcriptRecord(searchResponse) →
// {identity, mode:'raw', nodes:[{label,weight,brightness,status,…}], query, degraded}; constellation(rec,{w,h}) → SVG;
// renderArchetype('transcript-viz', rec, {visualDevice:<SVG>}) → render_kind=graph → the body slot returns
// opts.visualDevice (archetype.js:48, the SAME contract channel-view uses). The adapter reads the WHOLE response
// envelope (q + mode_used + semantic.available), so the store passes the whole thing through.

type DNAGlobal = {
  faceRecord?: { transcriptRecord?: (api: unknown) => { nodes?: unknown[] } & Record<string, unknown> }
  org?: { constellation?: (data: unknown, o: unknown) => string }
  renderArchetype?: (archetype: unknown, record: unknown, opts: unknown) => HTMLElement
  _transcriptVizArchetype?: unknown
}
const dna = () => (window as unknown as { DNA?: DNAGlobal }).DNA

export function TranscriptView() {
  const { query, raw, loading, error, open } = useTranscript()
  const graphRef = useRef<HTMLDivElement>(null)
  const results = (raw?.results as unknown[] | undefined) ?? []
  const searched = raw != null // a search has run (vs. the opening prompt state)

  // open on `transcript:open`; Esc closes (mirrors the other overlays).
  useEffect(() => {
    const onOpen = () => openTranscript()
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && open) closeTranscript()
    }
    window.addEventListener('transcript:open', onOpen)
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('transcript:open', onOpen)
      window.removeEventListener('keydown', onKey)
    }
  }, [open])

  // MOUNT DNA's constellation when a search has results. Load the transcript-viz archetype once (cached on DNA), adapt
  // the FULL response → the graph record, render through the ONE generic renderArchetype with constellation as the
  // visual device, append. Degrade-clean: DNA not loaded / no archetype / adapter throws → an honest line. Empty
  // results are handled in the body (a quiet no-match line, NOT a blank graph). Re-runs whenever `raw` changes.
  useEffect(() => {
    const host = graphRef.current
    if (!host || !open || results.length === 0) return
    let cancelled = false
    ;(async () => {
      const D = dna()
      if (!D?.renderArchetype || !D.faceRecord?.transcriptRecord || !D.org?.constellation) {
        host.textContent = 'The history view isn’t ready yet.'
        return
      }
      if (!D._transcriptVizArchetype) {
        try {
          const ly = await (await fetch('/dna/layouts.json')).json()
          D._transcriptVizArchetype = ly.archetypes?.['transcript-viz']
        } catch {
          /* local + reliable; a fetch fail degrades below */
        }
      }
      if (cancelled || graphRef.current !== host) return
      try {
        const rec = D.faceRecord.transcriptRecord(raw) // the WHOLE envelope (q + mode_used + semantic + results)
        const device = D.org.constellation(rec, { w: 600, h: 440, label: rec.query })
        const el = D.renderArchetype(D._transcriptVizArchetype, rec, { visualDevice: device })
        host.replaceChildren(el)
      } catch {
        host.textContent = 'Couldn’t draw the constellation just now.'
      }
    })()
    return () => {
      cancelled = true
    }
  }, [open, raw, results.length])

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    searchTranscript(query)
  }

  return (
    <div className={`transcript-overlay ${open ? 'transcript-overlay--open' : ''}`} aria-hidden={!open}>
      <div className="transcript-scrim" onClick={closeTranscript} />
      <div className="transcript-panel" role="dialog" aria-label="History" aria-modal="true">
        <header className="transcript-head">
          <div>
            <h2 className="transcript-title">History</h2>
            <p className="transcript-sub">Search everything the Company has discussed — by meaning. Each star is a conversation.</p>
          </div>
          <button className="transcript-close" onClick={closeTranscript} aria-label="close">
            ✕
          </button>
        </header>
        <form className="transcript-search" onSubmit={submit}>
          <input
            className="transcript-input"
            type="search"
            value={query}
            onChange={(e) => setTranscriptQuery(e.target.value)}
            placeholder="What were we working on…"
            aria-label="Search the corpus by meaning"
            autoFocus
          />
          <button className="transcript-go" type="submit" disabled={loading || !query.trim()}>
            {loading ? 'Searching…' : 'Search'}
          </button>
        </form>
        <div className="transcript-body">
          {error && (
            <p className="transcript-msg transcript-msg--error">
              {error} <button className="transcript-retry" onClick={() => searchTranscript(query)}>Try again</button>
            </p>
          )}
          {!error && !searched && !loading && (
            <p className="transcript-msg transcript-msg--quiet">Type a query above to search the Company’s whole history.</p>
          )}
          {!error && loading && results.length === 0 && <p className="transcript-msg">Searching the corpus…</p>}
          {!error && searched && !loading && results.length === 0 && (
            <p className="transcript-msg transcript-msg--quiet">No conversations match “{String(raw?.q ?? query)}” — the corpus may simply not hold it.</p>
          )}
          {/* DNA's constellation mounts here (full-width centered) once a search has results */}
          {results.length > 0 && <div className="transcript-graph" ref={graphRef} />}
        </div>
      </div>
    </div>
  )
}
