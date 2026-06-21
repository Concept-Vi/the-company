import { useEffect, useRef } from 'react'
import { useSessions, openSessions, closeSessions, selectSession } from './sessionDrillStore'
import './sessions.css'

// THE SESSION-DRILL SURFACE (FACE-1, the supervisor face) — the list of Claude-Code sessions the Company has run →
// drill into one → DNA's session-card organism rendered on its LIVE record + the recall lenses. An App-root SIBLING
// OVERLAY (the GalleryMount/DecisionsInbox/ToolsPanel pattern — host seam 1). The RENDER is DNA's: the session-card
// mounts via the drop-in (DNA.faceRecord.sessionRecord(row) → DNA.renderArchetype(session-card) → appendChild) — NO
// bespoke card render (from-DNA law); the host frames it + hosts the lenses. Data is LIVE (/api/sessions +
// /api/session-recall via sessionDrillStore). Opens on the `sessions:open` window event (the entry verb/chrome is
// DNA's design lane — a follow). Operator-law: human meaning only; the session id is never shown as the title.

type DNAGlobal = {
  faceRecord?: { sessionRecord?: (raw: unknown) => unknown }
  renderArchetype?: (archetype: unknown, record: unknown, opts: unknown) => HTMLElement
  _sessionCardArchetype?: unknown
}
const dna = () => (window as unknown as { DNA?: DNAGlobal }).DNA

export function SessionDrill() {
  const { sessions, loading, error, open, selected, lens } = useSessions()
  const cardRef = useRef<HTMLDivElement>(null)

  // open on `sessions:open`; Esc backs out of a drill, then closes (mirrors the other overlays).
  useEffect(() => {
    const onOpen = () => openSessions()
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'Escape' || !open) return
      if (selected) selectSession(null)
      else closeSessions()
    }
    window.addEventListener('sessions:open', onOpen)
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('sessions:open', onOpen)
      window.removeEventListener('keydown', onKey)
    }
  }, [open, selected])

  // MOUNT DNA's session-card on the drilled row (the dd96150 drop-in). Load the archetype once (cached on DNA),
  // adapt the raw row → the record, render through the ONE generic renderArchetype, append. Degrade-clean: DNA not
  // loaded / no archetype / adapter throws → an honest line (never a crash, never a bespoke card).
  useEffect(() => {
    const host = cardRef.current
    if (!host || !selected) return
    const row = sessions.find((s) => s.id === selected)
    if (!row) return
    let cancelled = false
    ;(async () => {
      const D = dna()
      if (!D?.renderArchetype || !D.faceRecord?.sessionRecord) {
        host.textContent = 'The session view isn’t ready yet.'
        return
      }
      if (!D._sessionCardArchetype) {
        try {
          const ly = await (await fetch('/dna/layouts.json')).json()
          D._sessionCardArchetype = ly.archetypes?.['session-card']
        } catch {
          /* local + reliable; a fetch fail degrades below */
        }
      }
      if (cancelled || cardRef.current !== host) return
      try {
        const rec = D.faceRecord.sessionRecord(row)
        const card = D.renderArchetype(D._sessionCardArchetype, rec, { composed: true })
        host.replaceChildren(card)
      } catch {
        host.textContent = 'Couldn’t draw this session just now.'
      }
    })()
    return () => {
      cancelled = true
    }
  }, [selected, sessions])

  const drilled = selected ? sessions.find((s) => s.id === selected) : null

  return (
    <div className={`sessions-overlay ${open ? 'sessions-overlay--open' : ''}`} aria-hidden={!open}>
      <div className="sessions-scrim" onClick={closeSessions} />
      <div className="sessions-panel" role="dialog" aria-label="Sessions" aria-modal="true">
        <header className="sessions-head">
          {selected ? (
            <button className="sessions-back" onClick={() => selectSession(null)} aria-label="back to the session list">
              ‹ All sessions
            </button>
          ) : (
            <div className="sessions-head-text">
              <h2 className="sessions-title">Sessions</h2>
              <p className="sessions-sub">Every session the Company has run — open one to see what it’s doing.</p>
            </div>
          )}
          <button className="sessions-close" onClick={closeSessions} aria-label="close">
            ✕
          </button>
        </header>

        <div className="sessions-body">
          {error && (
            <p className="sessions-msg sessions-msg--error">
              {error} <button className="sessions-retry" onClick={openSessions}>Try again</button>
            </p>
          )}

          {/* THE LIST */}
          {!selected && !error && (
            <>
              {loading && sessions.length === 0 && <p className="sessions-msg">Looking…</p>}
              {sessions.length > 0 && (
                <ul className="sessions-list">
                  {sessions.slice(0, 60).map((s) => (
                    <li key={s.id}>
                      <button className="sessions-row" onClick={() => selectSession(s.id)}>
                        <span className="sessions-row-name">{s.title || s.name || 'Session'}</span>
                        <span className="sessions-row-meta">
                          {s.state}
                          {s.cwd ? ' · ' + (s.cwd.split('/').filter(Boolean).slice(-1)[0] || s.cwd) : ''}
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </>
          )}

          {/* THE DRILL — DNA's session-card (mounted into cardRef) + the recall lenses */}
          {selected && (
            <div className="sessions-detail">
              <div className="sessions-card" ref={cardRef} />
              {lens?.loading && <p className="sessions-msg">Looking into it…</p>}
              {lens && !lens.loading && (lens.open_loops?.length || lens.catch_up?.length) ? (
                <div className="sessions-lens">
                  {lens.open_loops && lens.open_loops.length > 0 && (
                    <section className="sessions-lens-sec">
                      <h3 className="sessions-lens-h">Still open</h3>
                      <ul>{lens.open_loops.slice(0, 8).map((it, i) => <li key={i}>{it.text}</li>)}</ul>
                    </section>
                  )}
                  {lens.catch_up && lens.catch_up.length > 0 && (
                    <section className="sessions-lens-sec">
                      <h3 className="sessions-lens-h">Recently</h3>
                      <ul>{lens.catch_up.slice(0, 8).map((it, i) => <li key={i}>{it.text}</li>)}</ul>
                    </section>
                  )}
                </div>
              ) : lens && !lens.loading && drilled ? (
                <p className="sessions-msg sessions-msg--quiet">No recall lenses for this session yet.</p>
              ) : null}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
