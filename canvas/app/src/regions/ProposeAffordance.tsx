// B1 · propose-affordance — the OFFER-WITH-OPTIONS surface (the rich "shall I?", click #2 of the
// two-click consent model). A four-channel offer:
//
//   • PICK an option   — the RHM's offered action(s) as one-click choices (options[]; B1 carries one,
//                         the surface maps over it generically). Picking COMMITS through /api/act
//                         (approveProposal(opt)).
//   • STEER            — a direction channel (NOT binary): the operator types a refinement and it loops
//                         BACK to the RHM to re-offer (steerProposal → reuses sendChat → a refined offer
//                         returns as a new proposal). This is the "or tell me how to change it" path.
//   • DEFER            — an honest set-aside ("not now") that drops the live card WITHOUT acting.
//   • DISMISS          — reject: drop the card, the action never ran (no backend call).
//
// ──────────────────────────────────────────────────────────────────────────────────────────────────
// B2 · ON-SCREEN INTERACTIVE BUILD (the consequential verbs: build/panel/extend).
// When the backend marks an offer `interactive` (any offered option is a consequential verb — the
// registry-truth marker, NOT options.length), the consequential consent must be a GUIDED CONVERSATION
// WITH ALTERNATIVES, not a one-click commit and not a silent inbox-drop. So this region renders a
// designed OPTION-COMPARISON surface where:
//
//   • the alternatives sit SIDE BY SIDE (recognition-by-sight — the operator weighs them by shape, the
//     `summary` is the distinguishing content, not the verb which is often identical across panel/build
//     options), selectable;
//   • SELECTING a card is VISUAL ONLY — it fires NO /api/act (selection ≠ approval; this is the whole of
//     B2 vs B1). The operator can keep discussing/steering after selecting;
//   • an EXPLICIT, separate "approve & build" commit is the ONLY thing that runs the chosen option
//     (→ approveProposal(selected) → /api/act → the existing dispatch: build composes a pipeline; panel/
//     extend surface a CONFIRM draft for a SECOND operator approval). Nothing runs until that approve.
//   • the steer/chat channel stays live throughout (chat-until-approve).
//
// FORM (recognition-by-sight, kit-composed): tokens-only via the .rhm-afford-* / .afford-cmp-* classes;
// the kit's Surface/Badge tone vocabulary; the selected card carries the signal spine + a "selected"
// badge. On phone the comparison cards STACK (a column) rather than reflowing a too-narrow row.
import { useState, useEffect } from 'react'
import { useApp } from '../AppContext'
import { Surface, Badge } from '../components/kit'

export function ProposeAffordance() {
  const { proposal, chatBusy, approveProposal, steerProposal, deferProposal, setAsideProposal, dismissProposal } = useApp()
  const [steer, setSteer] = useState('')
  // B2 · select-then-approve: which alternative is currently SELECTED (visual only — no /api/act). null =
  // none chosen yet. Reset whenever a NEW proposal arrives (a steer returns a fresh offer; a stale index
  // must not leak across offers). Kept LOCAL to this region (useAppController only owns the proposal data).
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null)
  useEffect(() => { setSelectedIdx(null); setSteer('') }, [proposal])
  if (!proposal) return null
  // the offered choices: the backend's options[] when present, else synthesise the primary offer as the
  // single choice (back-compat with any proposal that predates options[]). Each reads as a click-to-approve.
  const options = (proposal.options && proposal.options.length)
    ? proposal.options
    : [{ verb: proposal.verb, address: proposal.address, args: proposal.args, label: proposal.verb, summary: null }]
  const multi = options.length > 1
  // B2 marker: the consequential interactive offer renders the comparison + select-then-approve surface.
  const interactive = !!proposal.interactive
  function submitSteer() {
    const t = steer.trim()
    if (!t) return
    setSteer('')
    steerProposal(t)
  }

  // ── B2 · the ON-SCREEN INTERACTIVE comparison surface (consequential verbs) ──────────────────────────
  if (interactive) {
    const sel = selectedIdx != null ? options[selectedIdx] : null
    return (
      // NB: NO data-ui-ref on the card or its controls — an ephemeral affordance, not an addressed locus.
      <div className="rhm-afford rhm-afford-cmp"
        title="the right-hand-man offers these options — choose one, discuss, then approve. nothing runs until you approve.">
        <div className="afford-head">
          <span className="ic">⚒</span>
          <span className="afford-label">{multi ? 'choose an approach — compare, discuss, then approve' : 'proposed build — review, discuss, then approve'}</span>
          <Badge tone="await">nothing runs yet</Badge>
        </div>

        {/* the alternatives, side by side (recognition-by-sight). Selecting is VISUAL ONLY — no /api/act.
            The `summary` is the distinguishing content (verb/address are often identical across options). */}
        <div className={'afford-cmp-grid' + (multi ? '' : ' afford-cmp-single')}>
          {options.map((o, i) => {
            const chosen = selectedIdx === i
            return (
              <Surface key={i} tone={chosen ? 'sig' : 'dim'}
                className={'afford-cmp-card' + (chosen ? ' afford-cmp-chosen' : '')}
                onClick={() => setSelectedIdx(chosen ? null : i)}
                title={chosen ? 'selected — approve below to build this (nothing has run)' : 'select this approach (does not run it — selecting is not approving)'}>
                <div className="afford-cmp-card-head">
                  <span className="afford-cmp-name">{o.label || o.verb}</span>
                  {chosen && <Badge tone="sig">selected</Badge>}
                </div>
                {o.summary && <div className="afford-cmp-summary">{o.summary}</div>}
                <div className="afford-cmp-meta">
                  <span className="afford-opt-verb">{o.verb}</span>
                  {o.address && <span className="afford-addr">{o.address}</span>}
                </div>
              </Surface>
            )
          })}
        </div>

        {/* the steer/chat channel — live throughout (chat-until-approve), refines the offer set. */}
        {proposal.direction !== false && (
          <div className="afford-steer">
            <input className="afford-steer-in" placeholder="…or discuss — e.g. combine these, a smaller one, the other node"
              value={steer} disabled={chatBusy}
              onChange={e => setSteer(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') submitSteer() }} />
            <button className="b" onClick={submitSteer} disabled={chatBusy || !steer.trim()} title="loop this back to the RHM to refine the options">discuss</button>
          </div>
        )}

        {/* the EXPLICIT approve commit — the ONLY control that runs anything. Disabled until an option is
            selected: selection ≠ approval, and approval is a deliberate separate act (the B2 invariant). */}
        <div className="afford-actions">
          <button className="b afford-approve" onClick={() => sel && approveProposal(sel)}
            disabled={chatBusy || !sel}
            title={sel ? 'approve & build the selected approach (this is the consent commit — it runs now)' : 'select an approach above first'}>
            {sel ? `approve & build${sel.verb !== 'build' ? ' (' + sel.verb + ')' : ''}` : 'select an approach to approve'}
          </button>
          {/* B3 · the configurable QUEUE arm — defer this LIVE build into the inbox as a real, revivable
              item; revisiting re-opens THIS card (options + discuss + approve). Nothing runs on defer. */}
          <button className="b ghost" onClick={() => deferProposal()} disabled={chatBusy} title="not now — queue this build to your inbox; revisit it any time to resume the conversation (nothing runs)">⏸ queue to inbox</button>
          <button className="b ghost" onClick={() => setAsideProposal()} disabled={chatBusy} title="set aside without queuing — drop the card; nothing runs, nothing kept">set aside</button>
          <button className="b ghost" onClick={() => dismissProposal()} disabled={chatBusy} title="reject — drop the offer; nothing runs">dismiss</button>
        </div>
      </div>
    )
  }

  // ── B1 · the OFFER-WITH-OPTIONS single/light surface (safe verbs — click an option to act) ───────────
  return (
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

      {/* STEER — the direction channel (not binary): refine the offer and loop it back to the RHM. */}
      {proposal.direction !== false && (
        <div className="afford-steer">
          <input className="afford-steer-in" placeholder="…or steer it — e.g. smaller scope, a draft first, the other node"
            value={steer} disabled={chatBusy}
            onChange={e => setSteer(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') submitSteer() }} />
          <button className="b" onClick={submitSteer} disabled={chatBusy || !steer.trim()} title="loop this steer back to the RHM to refine the offer">refine</button>
        </div>
      )}

      {/* the graded secondaries: B3 defer = QUEUE to the inbox (durable, revivable — revisiting re-opens this
          offer); set aside = the lighter no-op (drop, not kept); dismiss = reject (drop, no act). */}
      <div className="afford-actions">
        <button className="b ghost" onClick={() => deferProposal()} disabled={chatBusy} title="not now — queue this offer to your inbox; revisit it any time to resume (nothing runs)">⏸ queue to inbox</button>
        <button className="b ghost" onClick={() => setAsideProposal()} disabled={chatBusy} title="set aside without queuing — drop the card; nothing kept">set aside</button>
        <button className="b ghost" onClick={() => dismissProposal()} disabled={chatBusy} title="reject — drop the offer; nothing runs">dismiss</button>
      </div>
    </div>
  )
}
