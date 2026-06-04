// F0 (carved from App.tsx:1432–1530) · the inbox · chief-of-staff triage. data-ui-ref="inbox" +
// data-ui-ref="deferred-queue" preserved. The build-intent lane (BuildIntentCard, demonstrate-first),
// action-grouped lanes, the W7 deferred queue, and the collapsible resolved-for-you group are all carved
// verbatim. PRESERVE-LIST: per-panel error boundaries (each build-intent card), demonstrate-first review.
import { PanelErrorBoundary } from '../components/PanelErrorBoundary'
import { BuildIntentCard } from '../components/BuildIntentCard'
import { isBuildIntent } from '../api'
import { useApp } from '../AppContext'

export function Inbox() {
  const { inbox, session, wtBusy, events, types, showResolved, startWalk, openCoa, addNode, setShowResolved } = useApp()
  return (
    <div data-ui-ref="inbox">
      <h3 style={{ marginTop: 18 }}>inbox · chief-of-staff triage</h3>
      <div className="ibx-head">
        {/* U11: qualify the count so it is never mistaken for unresolved GRAPH NODES. */}
        <span className="sig" title="decisions/approvals escalated to you — not graph nodes">{inbox.counts?.escalations || 0} decision(s) awaiting you</span>
        <span className="muted"> · {inbox.counts?.resolved || 0} resolved-for-you</span>
        {/* B-frontend: the operator entry point for S1 — walk ALL live escalations through the organ. */}
        {(inbox.live_escalations || []).length > 0 && !session && (
          <button className="b sm" style={{ marginLeft: 'auto' }} disabled={wtBusy} title="walk all awaiting items through the review organ"
            onClick={() => startWalk((inbox.live_escalations || []).map((d: any) => d.id))}>{wtBusy ? 'starting…' : '▷ walk these'}</button>
        )}
      </div>
      {/* WIRE-UI: the decision→implementation wire's build-intents get their OWN lane, rendered as rich
         cards. They still live in `live_escalations` (code never writes `resolved`, only the `status` lane),
         so we split them out BEFORE the generic action-grouping below. */}
      {(() => {
        const esc: any[] = inbox.live_escalations || []
        const builds = esc.filter(isBuildIntent)
        if (!builds.length) return null
        return (
          <div className="ibx-lane ibx-builds">
            <div className="ibx-lane-head">decision → build <span className="muted">· {builds.length}</span></div>
            {builds.map((d: any) => (
              <PanelErrorBoundary key={d.id} name={'build-intent ' + d.id}>
                {/* DEMONSTRATE-FIRST: onDemonstrate places the built node-type on the canvas; liveTypes is
                   the registry truth that gates the "show me" affordance to a node-type that went live. */}
                <BuildIntentCard d={d} onOpen={openCoa} onDemonstrate={(t: string) => { void addNode(t) }} liveTypes={types} />
              </PanelErrorBoundary>
            ))}
          </div>
        )
      })()}
      {/* U12: group the REMAINING (non-build-intent) live escalations by ACTION into visual lanes. A
         `(test)` heuristic distinguishes test-pollution items so they're visible-but-separable. */}
      {(() => {
        const esc: any[] = (inbox.live_escalations || []).filter((d: any) => !isBuildIntent(d))
        const isTest = (d: any) => /test|fixture|pollut|sample|demo/i.test(((d.payload?.name || '') + ' ' + (d.id || '')))
        const lanes: Record<string, any[]> = {}
        esc.forEach(d => { const k = (isTest(d) ? 'test · ' : '') + (d.action || 'decision'); (lanes[k] = lanes[k] || []).push(d) })
        return Object.entries(lanes).map(([lane, items]) => (
          <div key={lane} className={'ibx-lane' + (/^test · /.test(lane) ? ' ibx-test' : '')}>
            <div className="ibx-lane-head">{lane} <span className="muted">· {items.length}</span></div>
            {items.map((d: any) => (
              <div key={d.id} className="ibx-item" onClick={() => openCoa(d.id)}>
                ⚠ {d.payload?.name || d.id} <span className="muted">— compile ↗</span>
              </div>
            ))}
          </div>
        ))
      })()}
      {(inbox.counts?.escalations || 0) === 0 && <div className="muted">nothing awaiting you.</div>}
      {/* WIRE-UI: the W7 DEFERRED QUEUE — when the dispatch loop hits its concurrency cap it emits a
         `decision.deferred` event (event-only; NO inbox item) per held build, so the operator SEES what was
         held rather than it silently disappearing (fail-loud). Read from the activity log, newest first,
         deduped by the resolve seq; clears once that seq dispatches. */}
      {(() => {
        const dispatchedSeqs = new Set(
          (events || []).filter((e: any) => e.kind === 'decision.dispatch').map((e: any) => e.derived_from))
        const seen = new Set<number>()
        const deferred = (events || [])
          .filter((e: any) => e.kind === 'decision.deferred')
          .filter((e: any) => !dispatchedSeqs.has(e.derived_from))   // already dispatched a later pass → not still deferred
          .filter((e: any) => { const s = e.derived_from; if (seen.has(s)) return false; seen.add(s); return true })
        if (!deferred.length) return null
        return (
          <div className="ibx-lane ibx-deferred" data-ui-ref="deferred-queue">
            <div className="ibx-lane-head">⏸ deferred (cap reached) <span className="muted">· {deferred.length}</span></div>
            {deferred.map((e: any) => (
              <div key={e.seq} className="ibx-item ibx-defer-item" onClick={() => e.surfaced && openCoa(e.surfaced)}
                title="held this pass because the dispatch concurrency cap was reached; a later pass will dispatch it">
                held · {e.surfaced || ('seq ' + e.derived_from)} <span className="muted">— cap {e.cap}, re-offered next pass</span>
              </div>
            ))}
          </div>
        )
      })()}
      {/* U12: resolved-for-you as its own collapsible group (audit lane — needn't be worked). */}
      {(inbox.resolved_for_you || []).length > 0 && (
        <div className="ibx-lane ibx-resolved">
          <div className="ibx-lane-head" style={{ cursor: 'pointer' }} onClick={() => setShowResolved(s => !s)}>
            {showResolved ? '⌄' : '⌃'} resolved-for-you <span className="muted">· {(inbox.resolved_for_you || []).length} (audit)</span>
          </div>
          {showResolved && (inbox.resolved_for_you || []).map((d: any) => (
            <div key={d.id} className="ibx-item ibx-done" onClick={() => openCoa(d.id)}>
              ✓ {d.action} · {d.payload?.name || d.id}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
