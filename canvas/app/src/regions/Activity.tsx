// F0 (carved from App.tsx:1581–1596) · the activity region — now summary + the live event feed.
// data-ui-ref="activity" preserved. Events render keyed by e.seq (mergeEvents guarantees uniqueness).
import { relTime } from '../api'
import { useApp } from '../AppContext'

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
            <span className="ev-s">{e.summary}</span>
            <span className="ev-t">{relTime(e.ts)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
