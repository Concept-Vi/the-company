import { useDecisions, openDecisionsList } from './decisionsStore'

// THE DECISIONS ENTRY — the in-surface call-to-action: "the Company is waiting on you for N decisions." Rendered
// IN-FLOW directly below each layout's header (portrait/desktop) or atop the rail (landscape), so it never fights
// the header chrome and is always correctly placed on every form factor. Shown only when decisions are pending;
// tapping it opens the list (the modal lives in DecisionsInbox, an App-root sibling). Copy is an AI-supplied DRAFT
// (plain operator words), marked for Tim's later steer.
export function DecisionsBar() {
  const { pending } = useDecisions()
  const count = pending.length
  if (count === 0) return null
  return (
    <div className="inbox-bar">
      <button
        className="inbox-entry"
        onClick={openDecisionsList}
        aria-label={`${count} ${count === 1 ? 'decision' : 'decisions'} waiting for you — open the list`}
      >
        <span className="inbox-entry-dot" aria-hidden="true" />
        <span className="inbox-entry-label">
          {count} {count === 1 ? 'decision' : 'decisions'} waiting
        </span>
      </button>
    </div>
  )
}
