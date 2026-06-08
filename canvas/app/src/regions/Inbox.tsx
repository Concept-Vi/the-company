// F0 (carved from App.tsx:1432–1530) · the inbox · chief-of-staff triage.
// WAVE-2 DESIGN DIRECTION — the operator's MAIN surface, redesigned from prototype-grade (<h3>+bare lists)
// into a recognition-by-sight triage deck composed from the SHARED KIT (components/kit.tsx, H2). The
// triage now reads at a glance by SHAPE + TINT, not by reading: an AWAITING headline (amber count), the
// decision→build lane (wire-blue, rich cards), the action lanes (amber), the HELD/deferred lane (dim), and
// the resolved-for-you audit (green, collapsed). Every row is a kit <Surface> card with a lifecycle spine,
// not a bare line. This is the REFERENCE the other regions follow.
//
// PRESERVED (the bar — function untouched, only the FORM redesigned): data-ui-ref="inbox" +
// data-ui-ref="deferred-queue" + every ui:// address · the BuildIntentCard composition (demonstrate-first,
// blast-radius, context-bundle) · the W7 deferred-queue dedup logic · U11 escalation-not-node qualifier ·
// U12 action-grouping + test-pollution separation · L8 click-to-thing (resolveUiTarget) · per-build
// PanelErrorBoundary · operator-only verdicts via startWalk. NOT touched: the voice-FE lane.
import { PanelErrorBoundary } from '../components/PanelErrorBoundary'
import { BuildIntentCard } from '../components/BuildIntentCard'
import { SectionHead, LaneHead, Badge, Surface, EmptyState } from '../components/kit'
import { isBuildIntent } from '../api'
import { useApp } from '../AppContext'

export function Inbox() {
  const { inbox, session, wtBusy, events, types, showResolved, startWalk, openCoa, addNode, setShowResolved, resolveUiTarget, reviveOffer } = useApp()

  const escalations = inbox.counts?.escalations || 0
  const resolvedCount = inbox.counts?.resolved || 0
  const liveEsc: any[] = inbox.live_escalations || []
  const builds = liveEsc.filter(isBuildIntent)

  // B3 · the DEFERRED-OFFER lane (§6B QUEUE mode): live offers the operator queued for later. They are a
  // DISTINCT action class (`deferred_offer`) carrying the full revival state in payload.proposal, so split
  // them out BEFORE the generic action-grouping (like builds) — each renders as a RESUME card whose click
  // RE-OPENS the live interactive offer (reviveOffer → the ProposeAffordance card), NOT a dead queue line.
  // NB: this is a DIFFERENT lane from the W7 `deferred-queue` below (concurrency-HELD builds read from
  // events by seq) — own data-ui-ref, never folded into it.
  const deferredOffers = liveEsc.filter((d: any) => d.action === 'deferred_offer')

  // U12: the REMAINING (non-build, non-deferred-offer) escalations grouped by ACTION into visual lanes; a
  // `(test)` heuristic separates test-pollution so it's visible-but-distinct.
  const others = liveEsc.filter((d: any) => !isBuildIntent(d) && d.action !== 'deferred_offer')
  const isTest = (d: any) => /test|fixture|pollut|sample|demo/i.test(((d.payload?.name || '') + ' ' + (d.id || '')))
  const actionLanes: Record<string, any[]> = {}
  others.forEach(d => { const k = (isTest(d) ? 'test · ' : '') + (d.action || 'decision'); (actionLanes[k] = actionLanes[k] || []).push(d) })

  // W7: the DEFERRED queue — held builds (cap reached), read from the activity log, deduped by resolve seq,
  // cleared once that seq dispatches. Fail-loud: the operator SEES what was held, never silently dropped.
  const dispatchedSeqs = new Set((events || []).filter((e: any) => e.kind === 'decision.dispatch').map((e: any) => e.derived_from))
  const seen = new Set<number>()
  const deferred = (events || [])
    .filter((e: any) => e.kind === 'decision.deferred')
    .filter((e: any) => !dispatchedSeqs.has(e.derived_from))
    .filter((e: any) => { const s = e.derived_from; if (seen.has(s)) return false; seen.add(s); return true })

  const resolved: any[] = inbox.resolved_for_you || []

  return (
    <div data-ui-ref="inbox" className="ibx">
      {/* THE HEADLINE — the operator's standing question, in the display voice, with the awaiting count as an
         amber badge (read the load by sight). The "walk these" action sits in the aside slot. */}
      <SectionHead
        tag="chief of staff"
        aside={
          (inbox.live_escalations || []).length > 0 && !session
            ? <button className="b sm" data-ui-ref="ui://inbox/walk" disabled={wtBusy}
                title="walk all awaiting items through the review organ"
                onClick={() => startWalk((inbox.live_escalations || []).map((d: any) => d.id))}>
                {wtBusy ? 'starting…' : '▷ walk these'}
              </button>
            : null
        }>
        inbox
      </SectionHead>
      {/* U11: qualify the count so it is never mistaken for unresolved GRAPH NODES. */}
      <div className="ibx-stat" title="decisions/approvals escalated to you — not graph nodes">
        <Badge tone={escalations ? 'await' : 'dim'}>{escalations} awaiting you</Badge>
        <span className="muted"> · {resolvedCount} resolved-for-you</span>
      </div>

      {/* WIRE-UI: the decision→implementation wire's build-intents get their OWN lane (wire-blue), rendered as
         the rich BuildIntentCard (demonstrate-first). They live in live_escalations (code never writes
         `resolved`), so split BEFORE the generic action-grouping below. */}
      {builds.length > 0 && (
        <div className="ibx-lane" data-ui-ref="ui://inbox/build-review">
          <LaneHead tone="wire" count={builds.length}>decision → build</LaneHead>
          {builds.map((d: any) => (
            <PanelErrorBoundary key={d.id} name={'build-intent ' + d.id}>
              {/* DEMONSTRATE-FIRST: onDemonstrate places the built node-type on the canvas; liveTypes is the
                 registry truth gating the "show me" affordance to a node-type that went live. */}
              <BuildIntentCard d={d} onOpen={openCoa} onDemonstrate={(t: string) => { void addNode(t) }} liveTypes={types} onNavigate={resolveUiTarget} />
            </PanelErrorBoundary>
          ))}
        </div>
      )}

      {/* B3 · the DEFERRED-OFFER lane (wire-blue, like builds — these are live consent conversations the
         operator parked). Each card RESUMES the offer: clicking re-opens the interactive ProposeAffordance
         card (options + steer + approve) from where it was left. Nothing runs until that approve. */}
      {/* NB: NO data-ui-ref yet — `ui://inbox/deferred-offers` is not in design/_system/addresses.json
         (the corpus is owned by a file-disjoint lane; the orphan check ui_registry_acceptance forbids an
         unregistered data-ui-ref). Flagged for the corpus-registration batch (same class as the pending
         ui://settings/* · ui://inspector/help · ui://toolbar/guide). The lane works fully without it. */}
      {deferredOffers.length > 0 && (
        <div className="ibx-lane">
          <LaneHead tone="wire" count={deferredOffers.length}>⏸ parked offers — resume to decide</LaneHead>
          {deferredOffers.map((d: any) => {
            const opts = d.payload?.proposal?.options || []
            const isInteractive = !!d.payload?.proposal?.interactive
            return (
              <Surface key={d.id} tone="wire" className="ibx-defer-offer"
                onClick={() => reviveOffer(d.id)}
                title="reopen this offer — resume the conversation (discuss / steer / approve). nothing has run.">
                <span className="ibx-item-name">{isInteractive ? '⚒' : '⚑'} {d.payload?.name || d.id}</span>
                {d.payload?.note && <span className="muted ibx-defer-note">{d.payload.note}</span>}
                <span className="muted ibx-item-cta">
                  {opts.length > 1 ? `${opts.length} options · resume ↗` : 'resume ↗'}
                </span>
              </Surface>
            )
          })}
        </div>
      )}

      {/* U12: the action lanes — remaining escalations grouped by action; test-pollution dimmed but visible. */}
      {Object.entries(actionLanes).map(([lane, items]) => {
        const test = /^test · /.test(lane)
        return (
          <div key={lane} className={'ibx-lane' + (test ? ' ibx-test' : '')}>
            <LaneHead tone={test ? 'dim' : 'await'} count={items.length}>{lane}</LaneHead>
            {items.map((d: any) => (
              <Surface key={d.id} tone={test ? 'dim' : 'await'} onClick={() => openCoa(d.id)}
                className="ibx-item" dataUiRef="ui://inbox/coa">
                <span className="ibx-item-name">⚠ {d.payload?.name || d.id}</span>
                <span className="muted ibx-item-cta">compile ↗</span>
                {/* L8 (§21.7#9): a surfaced item carrying a ui:// target gets a click-to-thing link →
                   composes the PRESERVED resolveUiTarget keystone to navigate+spotlight it IN CONTEXT.
                   stopPropagation so it doesn't also fire the row's openCoa. No target → renders nothing. */}
                {d.payload?.ui_target && (
                  <button type="button" className="ibx-target-link" data-ui-ref="ui://inbox/target"
                    title={'go to ' + d.payload.ui_target}
                    onClick={(e) => { e.stopPropagation(); resolveUiTarget(d.payload.ui_target) }}>
                    ↳ go to thing
                  </button>
                )}
              </Surface>
            ))}
          </div>
        )
      })}

      {/* the rest-state — honest, never a blank gap. (deferredOffers ARE escalations, so the count guards it.) */}
      {escalations === 0 && builds.length === 0 && <EmptyState>nothing awaiting you — the deck is clear.</EmptyState>}

      {/* W7: the DEFERRED QUEUE — held builds (dim, fail-loud-visible, not awaiting a verdict yet). */}
      {deferred.length > 0 && (
        <div className="ibx-lane" data-ui-ref="deferred-queue">
          <LaneHead tone="dim" count={deferred.length}>⏸ held — cap reached</LaneHead>
          {deferred.map((e: any) => (
            <Surface key={e.seq} tone="dim" className="ibx-defer-item"
              onClick={() => e.surfaced && openCoa(e.surfaced)}
              title="held this pass because the dispatch concurrency cap was reached; a later pass will dispatch it">
              <span className="ibx-item-name">held · {e.surfaced || ('seq ' + e.derived_from)}</span>
              <span className="muted ibx-item-cta">cap {e.cap}, re-offered next pass</span>
            </Surface>
          ))}
        </div>
      )}

      {/* U12: resolved-for-you — its own collapsible audit lane (green, needn't be worked). */}
      {resolved.length > 0 && (
        <div className="ibx-lane">
          <LaneHead tone="sig" count={resolved.length} open={showResolved} onToggle={() => setShowResolved(s => !s)}>
            resolved-for-you · audit
          </LaneHead>
          {showResolved && resolved.map((d: any) => (
            <Surface key={d.id} tone="sig" onClick={() => openCoa(d.id)} className="ibx-done">
              <span className="ibx-item-name">✓ {d.action} · {d.payload?.name || d.id}</span>
            </Surface>
          ))}
        </div>
      )}
    </div>
  )
}
