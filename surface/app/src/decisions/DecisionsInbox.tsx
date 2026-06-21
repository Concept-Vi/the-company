import { useEffect } from 'react'
import { useDecisions, closeDecisionsList, loadDecisions, type StackItem } from './decisionsStore'

// THE CHANNEL-STACK — the operator's work-queue: the focused modal opened from the entry (DecisionsBar). It shows
// what the Company's autonomous work has surfaced that only the operator can settle (criteria B2: "the channel-stack
// as the primary 'what needs you' view — the DecisionsInbox, generalized"). Each item is a TYPE; today the only
// landed type is a decision (`decision-sequence`), so the stack dispatches on `item.type` with ONE real case + a
// fail-loud default — that single switch is the seam A4 (composition's item-type registry) lands into; no renderer
// is built for a kind no real data exercises yet (fork's stack-feed lands the others). Tapping a decision opens it
// through the SAME decision host the deep-link uses (we dispatch `decision:open`; GalleryMount renders the card —
// that at-bar card is DNA's, untouched here). ONE open-path, no parallel render logic. An App-root sibling, so it
// overlays cleanly on every form factor. Reads the shared store; fail-loud on a list error (retry, never silent).
//
// COPY is an AI-supplied DRAFT, deliberately plain (operator meaning, never machine words — the operator never sees
// "channel" or "stack"), marked for Tim's later steer. Only FINAL copy ratification is gated on him; mechanism +
// flow are built now.
export function DecisionsInbox() {
  const { pending, loading, error, refreshError, open } = useDecisions()

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
    // open through the ONE decision host (same path as the URL deep-link) — no parallel render. fromInbox:true so
    // closing the card RETURNS to this stack (work-the-queue), not to the wheel.
    window.dispatchEvent(new CustomEvent('decision:open', { detail: { address, id, fromInbox: true } }))
  }

  return (
    <div className={`inbox-overlay ${open ? 'inbox-overlay--open' : ''}`} aria-hidden={!open}>
      <div className="inbox-scrim" onClick={closeDecisionsList} />
      <div className="inbox-panel" role="dialog" aria-label="What needs you" aria-modal="true">
        <header className="inbox-head">
          <div className="inbox-head-text">
            <h2 className="inbox-title">What needs you</h2>
            <p className="inbox-sub">The Company has carried these as far as it can on its own.</p>
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
            <p className="inbox-msg">You’re all caught up — nothing needs you right now.</p>
          )}
          {pending.length > 0 && (
            <ul className="inbox-list">
              {pending.map((item) => (
                <li key={item.id}>{renderStackItem(item, pick)}</li>
              ))}
            </ul>
          )}
          {/* a REFRESH failed but the list above is still valid (last-good): an honest, non-alarming note —
              NOT the red "couldn't load" banner (that would contradict the cards the operator can see). */}
          {refreshError && pending.length > 0 && (
            <p className="inbox-msg inbox-msg--quiet">
              Showing your last loaded list — couldn’t refresh just now.{' '}
              <button className="inbox-retry" onClick={loadDecisions}>
                Try again
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

// THE TYPED DISPATCH — one item-type case per render, with a fail-loud default (no-silent-failures: an unknown kind
// shows an HONEST "needs you / view not ready" row, never vanishes). This switch is the single seam A4 widens; no
// speculative renderer is built for a kind no real data exercises yet.
function renderStackItem(item: StackItem, pick: (address: string, id: string) => void) {
  switch (item.type) {
    case 'decision-sequence':
      return <DecisionRow item={item} onPick={pick} />
    default:
      // the A4 seam: a real item whose type/render isn't landed yet stays VISIBLE and honest (never silently dropped)
      return (
        <div className="inbox-row inbox-row--unready" role="note">
          <span className="inbox-row-main">
            <span className="inbox-row-name">{item.name || 'Something needs you'}</span>
            <span className="inbox-row-meaning">
              This needs you, but its view isn’t ready yet — it’s flagged here so it isn’t lost.
            </span>
          </span>
        </div>
      )
  }
}

// THE DECISION ITEM — a legible at-a-glance preview built from the item's REAL record fields: the short handle
// (name), the actual question (meaning), the suggestion, and the reversibility note (so the operator knows the
// stakes before opening). meaning/reversibility degrade soft (absent until enrichment resolves, or if the record
// won't load) → the row still reads as name + suggestion. Tapping opens the decision's card (DNA's, via the host).
function DecisionRow({ item, onPick }: { item: StackItem; onPick: (address: string, id: string) => void }) {
  return (
    <button className="inbox-row" onClick={() => onPick(item.address, item.id)}>
      <span className="inbox-row-main">
        <span className="inbox-row-name">{item.name}</span>
        {item.meaning && <span className="inbox-row-meaning">{item.meaning}</span>}
        {(item.recommended_label || item.reversibility) && (
          <span className="inbox-row-foot">
            {item.recommended_label && (
              <span className="inbox-row-rec">Suggested: {item.recommended_label}</span>
            )}
            {item.reversibility && <span className="inbox-row-revers">{item.reversibility}</span>}
          </span>
        )}
      </span>
      <span className="inbox-row-go" aria-hidden="true">
        ›
      </span>
    </button>
  )
}
