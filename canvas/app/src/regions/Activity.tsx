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
            <span className="ev-s">{summaryText(e.summary)}</span>
            <span className="ev-t">{relTime(e.ts)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
