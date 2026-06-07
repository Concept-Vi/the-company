// F0 (carved from App.tsx:1581–1596) · the activity region — now summary + the live event feed.
// data-ui-ref="activity" preserved. Events render keyed by e.seq (mergeEvents guarantees uniqueness).
import { relTime } from '../api'
import { useApp } from '../AppContext'

// L-fe (defensive, rule 4 / the F5/F7 robustness pattern): an event's `summary` is USUALLY a string, but
// some kinds carry a STRUCTURED rollup — e.g. `cognition.wave` emits a dict summary (turn_id/n_roles/
// wall_s/finish_order/budget…). Rendering a non-string object directly as a React child THROWS ("Objects
// are not valid as a React child"), which the panel boundary would degrade to a card — but the feed must
// show EVERY event, never crash on one. So coerce any non-string summary to a legible one-line string here
// (the feed is a glance surface; the structured detail lives at its address). Never a silent drop.
function summaryText(s: any): string {
  if (s == null) return ''
  if (typeof s === 'string') return s
  if (typeof s === 'object') {
    // a compact one-liner for a structured rollup — name the turn + the headline counts when present.
    const t = s.turn_id ? String(s.turn_id).slice(-6) : ''
    const bits: string[] = []
    if (t) bits.push('turn ' + t)
    if (s.n_roles != null) bits.push(s.n_roles + ' roles')
    if (s.wall_s != null) bits.push(s.wall_s + 's')
    if (bits.length) return bits.join(' · ')
    try { return JSON.stringify(s) } catch { return String(s) }
  }
  return String(s)
}

export function Activity() {
  const { now, events } = useApp()
  return (
    <div className="hud activity" data-ui-ref="activity">
      <div className="act-head">
        <span className="act-title">now</span>
        {now && <span className="muted">{now.graph} · {now.nodes_resolved}/{now.nodes_total} resolved{now.surfaced_pending ? ` · ${now.surfaced_pending} awaiting you` : ''}</span>}
      </div>
      <div className="ev-list">
        {events.length === 0 && <div className="muted">no activity yet — run something.</div>}
        {events.map((e, i) => (
          <div key={e.seq ?? i} className={'ev ev-' + e.kind}>
            <span className="ev-k">{e.kind}</span>
            <span className="ev-s">{summaryText(e.summary)}</span>
            <span className="ev-t">{relTime(e.ts)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
