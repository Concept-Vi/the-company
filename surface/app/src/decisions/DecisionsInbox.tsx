import { useEffect } from 'react'
import { useDecisions, closeDecisionsList, loadDecisions } from './decisionsStore'

// THE DECISIONS LIST — the focused modal opened from the entry (DecisionsBar). Shows the pending decisions in HUMAN
// words (each one's name + the suggested option) → tap one → it opens through the SAME decision host the deep-link
// uses (we dispatch `decision:open`, GalleryMount renders it). ONE open-path, no parallel render logic. An App-root
// sibling (peer to the V / gallery / source panel), so it overlays cleanly on every form factor. Reads the shared
// store (one fetch shared with the entry); fail-loud on error (honest message + retry, never a silent empty).
//
// COPY is an AI-supplied DRAFT, deliberately plain (operator meaning, never machine words), marked for Tim's later
// steer — only FINAL copy ratification is gated on him; the mechanism + flow are built now.
export function DecisionsInbox() {
  const { pending, loading, error, open } = useDecisions()

  // close on Esc while open
  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeDecisionsList()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open])

  const pick = (address: string, id: string) => {
    closeDecisionsList()
    // open through the ONE decision host (same path as the URL deep-link) — no parallel render
    window.dispatchEvent(new CustomEvent('decision:open', { detail: { address, id } }))
  }

  return (
    <div className={`inbox-overlay ${open ? 'inbox-overlay--open' : ''}`} aria-hidden={!open}>
      <div className="inbox-scrim" onClick={closeDecisionsList} />
      <div className="inbox-panel" role="dialog" aria-label="Decisions waiting for you" aria-modal="true">
        <header className="inbox-head">
          <div className="inbox-head-text">
            <h2 className="inbox-title">Decisions waiting for you</h2>
            <p className="inbox-sub">The Company needs your call on these.</p>
          </div>
          <button className="inbox-close" onClick={closeDecisionsList} aria-label="close">
            ✕
          </button>
        </header>
        <div className="inbox-body">
          {error && (
            <p className="inbox-msg inbox-msg--error">
              {error}{' '}
              <button className="inbox-retry" onClick={loadDecisions}>
                Try again
              </button>
            </p>
          )}
          {!error && loading && pending.length === 0 && <p className="inbox-msg">Looking…</p>}
          {!error && !loading && pending.length === 0 && (
            <p className="inbox-msg">You’re all caught up — no decisions waiting.</p>
          )}
          {pending.length > 0 && (
            <ul className="inbox-list">
              {pending.map((d) => (
                <li key={d.id}>
                  <button className="inbox-row" onClick={() => pick(d.address, d.id)}>
                    <span className="inbox-row-main">
                      <span className="inbox-row-name">{d.name}</span>
                      {d.recommended_label && (
                        <span className="inbox-row-rec">Suggested: {d.recommended_label}</span>
                      )}
                    </span>
                    <span className="inbox-row-go" aria-hidden="true">
                      ›
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}
