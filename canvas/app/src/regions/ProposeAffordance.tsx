// B1 · propose-affordance — the OFFER-WITH-OPTIONS surface (the rich "shall I?", click #2 of the
// two-click consent model). UPGRADED from a binary [approve · dismiss] card into a four-channel offer:
//
//   • PICK an option   — the RHM's offered action(s) as one-click choices (options[]; v1 carries one,
//                         the surface maps over it generically so it's ready when the backend emits
//                         several). Picking an option commits it through /api/act (approveProposal(opt)).
//   • STEER            — a direction channel (NOT binary): the operator types a refinement and it loops
//                         BACK to the RHM to re-offer (steerProposal → reuses sendChat → a refined offer
//                         returns as a new proposal). This is the "or tell me how to change it" path.
//   • DEFER            — an honest set-aside ("not now") that drops the live card WITHOUT acting and
//                         WITHOUT rejecting. (No durable queue yet — flagged gap; never pretends queued.)
//   • DISMISS          — reject: drop the card, the action never ran (no backend call).
//
// Nothing executes until the operator picks. The offered verb/address read LEGIBLY (the address in the
// monospace addr style so the operator sees exactly what would run, where).
//
// FORM (recognition-by-sight, kit-composed): built on the committed commander's-bridge language —
// tokens only (design-system.css via the .rhm-afford-* classes), the kit's Surface/Badge tone vocabulary
// for the option rows (a picked offer is a CARD with the signal spine, not a bare button), the steer
// input mirrors the .rhm-input chat-field pattern (so design-lint sees no bespoke element). The card
// header signals "awaiting your call" in amber; the option rows carry the signal-green action spine.
import { useState } from 'react'
import { useApp } from '../AppContext'
import { Surface, Badge } from '../components/kit'

export function ProposeAffordance() {
  const { proposal, chatBusy, approveProposal, steerProposal, deferProposal, dismissProposal } = useApp()
  const [steer, setSteer] = useState('')
  if (!proposal) return null
  // the offered choices: the backend's options[] when present, else synthesise the primary offer as the
  // single choice (back-compat with any proposal that predates options[]). Each reads as a click-to-approve.
  const options = (proposal.options && proposal.options.length)
    ? proposal.options
    : [{ verb: proposal.verb, address: proposal.address, args: proposal.args, label: proposal.verb }]
  const multi = options.length > 1
  function submitSteer() {
    const t = steer.trim()
    if (!t) return
    setSteer('')
    steerProposal(t)
  }
  return (
    // NB: NO data-ui-ref on the card or its controls — the card is an ephemeral affordance, not an
    // addressed locus (clicking it must not re-indicate/route it as a ui:// target).
    <div className="rhm-afford" title="the right-hand-man offers this — nothing runs until you choose, steer, or set it aside">
      <div className="afford-head">
        <span className="ic">⚑</span>
        <span className="afford-label">{multi ? 'choose an action — or steer' : 'proposed action — approve, steer, or set aside'}</span>
        <Badge tone="await">awaiting you</Badge>
      </div>

      {/* PICK — the offered action(s) as one-click choices. A single option reads as the approve choice;
          several read as a menu. Each is a kit Surface (signal spine) → recognised as an action by sight. */}
      <div className="afford-options">
        {options.map((o, i) => (
          <Surface key={i} tone="sig" onClick={() => !chatBusy && approveProposal(o)}
            title="run this — the consent commit (nothing ran until now)">
            <div className="afford-opt-row">
              <span className="afford-verb">{o.label || o.verb}</span>
              {o.verb !== (o.label || o.verb) && <span className="afford-opt-verb">{o.verb}</span>}
              {o.address && <span className="afford-addr">{o.address}</span>}
              <span className="afford-opt-go" aria-hidden>→</span>
            </div>
          </Surface>
        ))}
      </div>

      {/* STEER — the direction channel (not binary): refine the offer and loop it back to the RHM. Shown
          when the offer accepts direction (proposal.direction). Mirrors the chat .rhm-input field pattern. */}
      {proposal.direction !== false && (
        <div className="afford-steer">
          <input className="afford-steer-in" placeholder="…or steer it — e.g. smaller scope, a draft first, the other node"
            value={steer} disabled={chatBusy}
            onChange={e => setSteer(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') submitSteer() }} />
          <button className="b" onClick={submitSteer} disabled={chatBusy || !steer.trim()} title="loop this steer back to the RHM to refine the offer">refine</button>
        </div>
      )}

      {/* the graded secondaries: defer = not now (set aside, no act); dismiss = reject (drop, no act). */}
      <div className="afford-actions">
        <button className="b ghost" onClick={() => deferProposal()} disabled={chatBusy} title="not now — set the offer aside without acting (it isn’t queued)">defer</button>
        <button className="b ghost" onClick={() => dismissProposal()} disabled={chatBusy} title="reject — drop the offer; nothing runs">dismiss</button>
      </div>
    </div>
  )
}
