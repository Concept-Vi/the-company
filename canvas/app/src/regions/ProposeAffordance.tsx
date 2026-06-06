// I3 · propose-affordance — the CONSENT card (click #2 of the two-click model).
//
// NET-NEW (seams-rhm Seam 2 REFUTE): the system used to be execute-then-render — a verb ran
// server-side and the FE rendered the OUTCOME (r.action.did). There was no "proposed action awaiting
// a click" affordance. This card IS that affordance: when the RHM PROPOSES an action (the backend
// emits a structured {verb, address, args} on the chat response WITHOUT executing it), this renders
// the verb + address LEGIBLY and gives the operator an APPROVE button. Approving fires /api/act (the
// I2 dispatch path — REUSE) so the action runs ONLY on approve; dismiss just drops it (reject does
// nothing). This is where CONSENT lands (criteria line 99/107).
//
// FORM: built on the corpus design system — reuses the .rhm-indicating chip vocabulary (tokens only,
// no hardcoded colors) extended into a card with two actions. The verb is the headline; the address
// is shown in the monospace addr style so the operator reads exactly what will run, where.
import { useApp } from '../AppContext'

export function ProposeAffordance() {
  const { proposal, chatBusy, approveProposal, dismissProposal } = useApp()
  if (!proposal) return null
  return (
    // NB: NO data-ui-ref on the card or its controls — the card is an ephemeral affordance, not an
    // addressed locus (clicking it must not re-indicate/route it as a ui:// target).
    <div className="rhm-afford" title="the right-hand-man proposes this — nothing runs until you approve">
      <div className="afford-head">
        <span className="ic">⚑</span>
        <span className="afford-label">proposed action — approve to run</span>
      </div>
      <div className="afford-body">
        <span className="afford-verb">{proposal.verb}</span>
        {proposal.address && <span className="afford-addr">{proposal.address}</span>}
      </div>
      <div className="afford-actions">
        <button className="b" onClick={() => approveProposal()} disabled={chatBusy}>approve</button>
        <button className="b ghost" onClick={() => dismissProposal()} disabled={chatBusy}>dismiss</button>
      </div>
    </div>
  )
}
