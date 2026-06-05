// L3 · addressed history/audit (§21.7#1) · "clicking an element shows everything that happened AT ITS
// ADDRESS." When the operator INDICATES a ui:// element, this region shows that locus's full trajectory —
// the GET /api/address-history read (Suite.address_view, the addressed analogue of decision_view, the sid
// path untouched). Reflects-never-owns: the runtime is authoritative; this region only reads.
//
// FORM (rule 9 — FORM is half of done): the history is NAVIGABLE, not a raw log-dump. The events are
// GROUPED BY KIND (annotation · chat · run · resolve · …) into collapsible sections — the operator scans
// the SHAPE of what happened here (how many comments, when it last ran, what was resolved) and drills into
// a group, rather than reading a flat wall. Built on the design system: it REUSES the existing .ev event-row
// vocabulary (.ev / .ev-k / .ev-s / .ev-t — the same rows the Activity feed uses, already token-coloured
// per kind) so it is coherent with the live event feed by construction. No hardcoded colours, no bespoke
// element — design-lint clean (only design-token classes + a thin .hist-* layout layer using var() tokens).
//
// Renders ONLY when a ui:// element is indicated (else nothing — it never clutters the rail). data-ui-ref
// keeps it addressable on the surface itself (quoted, per the lane rule).
import { useState } from 'react'
import { relTime } from '../api'
import { useApp } from '../AppContext'

export function History() {
  const { indicated, history, historyBusy } = useApp()
  // local collapse state — which kind-groups are OPEN. Default: all open (the operator sees the whole shape
  // at a glance, then collapses the noisy ones). Keyed by kind so it survives re-fetches at the same locus.
  const [closed, setClosed] = useState<Record<string, boolean>>({})
  if (!indicated || !indicated.startsWith('ui://')) return null   // only a ui:// locus has an addressed view

  const traj = history?.trajectory || []
  // GROUP BY KIND, preserving chronological order within each group (the backend already sorts by seq).
  const groups: Record<string, any[]> = {}
  const order: string[] = []
  for (const e of traj) {
    const k = e.kind || 'event'
    if (!(k in groups)) { groups[k] = []; order.push(k) }
    groups[k].push(e)
  }
  // most-active kinds first — the navigable surface leads with where the most happened here.
  order.sort((a, b) => groups[b].length - groups[a].length)

  return (
    <div className="hist" data-ui-ref="ui://inspector/history">
      <div className="hist-head">
        <span className="act-title">history</span>
        <span className="muted hist-addr" title={indicated}>{indicated}</span>
        <span className="muted">{historyBusy ? 'loading…' : `${traj.length} event${traj.length === 1 ? '' : 's'} here`}</span>
      </div>
      {traj.length === 0 && !historyBusy && (
        <div className="muted">nothing has happened at this element yet — comment on it, or operate it, and it shows here.</div>
      )}
      <div className="hist-groups">
        {order.map(kind => {
          const evs = groups[kind]
          const isClosed = !!closed[kind]
          return (
            <div key={kind} className="hist-group">
              <button className="hist-group-head" onClick={() => setClosed(c => ({ ...c, [kind]: !c[kind] }))}
                title={isClosed ? 'expand' : 'collapse'}>
                <span className="hist-caret">{isClosed ? '▸' : '▾'}</span>
                <span className="ev-k">{kind}</span>
                <span className="hist-count">{evs.length}</span>
                {/* the newest event's time as the group's at-a-glance recency cue */}
                <span className="ev-t">{relTime(evs[evs.length - 1]?.ts)}</span>
              </button>
              {!isClosed && (
                <div className="ev-list hist-list">
                  {evs.map((e, i) => (
                    <div key={e.seq ?? i} className={'ev ev-' + e.kind}>
                      <span className="ev-s">{e.summary}</span>
                      <span className="ev-t">{relTime(e.ts)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
