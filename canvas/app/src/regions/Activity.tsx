// F0 (carved from App.tsx:1581–1596) · the activity region — now summary + the live event feed.
// WAVE-4 COCKPIT-REGIONS — the HEAD redesigned to the commander's-bridge language; the FEED deliberately
// LEFT on the shared .ev event-row vocabulary. Why the light touch: the .ev/.ev-k/.ev-s/.ev-t rows are NOT
// prototype-grade — they are the DESIGNED, token-coloured-per-kind vocabulary that History, Versions, and
// SelfChanges all REUSE (app.css §L3/L6). Surface-ifying the feed here would REGRESS that cross-region
// coherence. So the recognition-by-sight win is at the HEAD: a kit SectionHead in the display voice + the
// `now` state read as kit Badges (resolved-progress on the signal tone, awaiting on the amber tone) instead
// of a run-on muted line. The feed stays the shared instrument trace it shares with the addressed-history
// regions. PRESERVED: data-ui-ref="activity" · events keyed by e.seq · the .ev row vocabulary. Pure markup.
import { relTime } from '../api'
import { SectionHead, Badge } from '../components/kit'
import { useApp } from '../AppContext'

export function Activity() {
  const { now, events } = useApp()
  return (
    <div className="hud activity" data-ui-ref="activity">
      {/* the HEAD — the bridge's live-state read. The graph name is the kicker; the resolved-progress + the
          awaiting count read as Badges (by colour), so the operator sees the run-state at a glance. */}
      <SectionHead tag={now ? now.graph : 'activity'}
        aside={now
          ? <>
              <Badge tone="sig">{now.nodes_resolved}/{now.nodes_total} resolved</Badge>
              {now.surfaced_pending ? <Badge tone="await">{now.surfaced_pending} awaiting</Badge> : null}
            </>
          : null}>
        now
      </SectionHead>
      {/* the FEED — the captured trajectory, the shared .ev instrument-row vocabulary (token-coloured per
          kind), the SAME rows History/Versions/SelfChanges reuse. Left as-is by design (not prototype-grade). */}
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
