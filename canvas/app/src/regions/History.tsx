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
//
// WAVE-? REGION-BATCH-2 (HEAD-ONLY pass, A1/H) — this is a CLASS-A region (like Activity): its `.ev`/`.hist`
// grouped-row body is ALREADY the designed, shared, token-coloured vocabulary (the same rows Activity /
// Versions / SelfChanges reuse) — Surface-ifying it would REGRESS cross-region coherence. So the conversion
// is the SAME light touch Activity took: only the HEAD is brought to the commander's-bridge language — a kit
// SectionHead in the display voice (the indicated address rides the kicker `tag`; the event count + busy
// state read as a kit Badge in the aside). This also FIXES a live drift: the old `.act-title` CSS rule was
// deleted in Activity's wave-4 pass but these three regions still rendered `.act-title`, so their titles had
// been unstyled (bare 12px mono) since then — the SectionHead restores the display voice. The `.ev`/`.hist`/
// `.ver` body + every grouped-row, every data-ui-ref, the collapse state are all PRESERVED untouched.
import { useState } from 'react'
import { relTime } from '../api'
import { SectionHead, Badge } from '../components/kit'
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
      {/* the HEAD — the commander's-bridge title in the display voice. The indicated address rides the kicker
          (the locus this trajectory is FOR); the event count reads as a Badge (sig when there's history, dim
          when empty) so the operator sees "how much happened here" by sight. */}
      <SectionHead tag={indicated}
        aside={historyBusy
          ? <Badge tone="dim">loading…</Badge>
          : <Badge tone={traj.length ? 'sig' : 'dim'}>{traj.length} event{traj.length === 1 ? '' : 's'} here</Badge>}>
        history
      </SectionHead>
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
