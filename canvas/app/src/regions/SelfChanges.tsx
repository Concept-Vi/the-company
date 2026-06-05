// L5 · self-change locating (§21.7#5) · "what did the SYSTEM change HERE?" When the operator INDICATES a
// ui:// element, this region shows the self-modification audit log FILTERED to that element's code scope —
// the S3 address→code join (Suite.self_changes_at → GET /api/self-changes-at). Each row is a [self-apply]
// commit whose changed_files touched THIS element's scope; revert is per-row, reusing the EXISTING
// operator-only api.revert (the /api/revert gate — no new revert path, gate untouched).
// Reflects-never-owns: the runtime is authoritative; this region only reads + composes the existing revert.
//
// STALE TRICHOTOMY (rule 4 — fail loud, never a silent empty that lies "nothing changed here"):
//   • corpus stale          → a loud "corpus stale — regenerate design/_system" line (the join is stale,
//                             so the list cannot be trusted; the operator is told, never shown a false []).
//   • scope empty, not stale → "this element maps to no code" (the address has no code scope to locate against).
//   • scope resolves         → the filtered change rows (an empty set = a true "no self-changes here").
//
// FORM (rule 9 — FORM is half of done): NAVIGABLE, built on the design system. REUSES the existing event-row
// vocabulary (.ev / .ev-k / .ev-s / .ev-t — the same token-coloured rows the Activity feed + the L3 History
// region use) so it is coherent by construction. The thin .hist-* layout layer is the same one History uses;
// the revert affordance reuses the existing .b.ghost.sm button + the ↩ glyph the Grow region's revert uses.
// No hardcoded colours, no bespoke element — design-lint clean (design-token classes + var() tokens only).
//
// Renders ONLY when a ui:// element is indicated (else nothing — it never clutters the rail). data-ui-ref
// (quoted, per the lane rule) keeps it addressable on the surface itself.
import { relTime } from '../api'
import { useApp } from '../AppContext'

export function SelfChanges() {
  const { indicated, selfChanges, selfChangesBusy, revertSelfChangeAt } = useApp()
  if (!indicated || !indicated.startsWith('ui://')) return null   // only a ui:// locus has a code scope

  const stale = !!selfChanges?.stale
  const scope = selfChanges?.scope || []
  const changes = selfChanges?.changes || []
  const note = selfChanges?.note || ''

  return (
    <div className="hist" data-ui-ref="ui://workshop/self-changes">
      <div className="hist-head">
        <span className="act-title">what changed here</span>
        <span className="muted hist-addr" title={indicated}>{indicated}</span>
        <span className="muted">
          {selfChangesBusy
            ? 'loading…'
            : stale
              ? 'corpus stale'
              : `${changes.length} self-change${changes.length === 1 ? '' : 's'} here`}
        </span>
      </div>

      {/* fail-loud: a stale corpus is NEVER shown as "nothing here" — the operator is told to regenerate. */}
      {stale && !selfChangesBusy && (
        <div className="err">⚠ corpus join is stale — regenerate design/_system to locate self-changes here. {note}</div>
      )}

      {/* the address maps to no code scope (orphan / CSS-selector ref) — distinct from "no changes". */}
      {!stale && scope.length === 0 && !selfChangesBusy && (
        <div className="muted">this element maps to no code scope — nothing can be located here. {note}</div>
      )}

      {/* scope resolved, but the system hasn't changed anything touching it yet — a true empty. */}
      {!stale && scope.length > 0 && changes.length === 0 && !selfChangesBusy && (
        <div className="muted">the system hasn't changed anything at this element yet — its code scope is {scope.join(', ')}.</div>
      )}

      {!stale && changes.length > 0 && (
        <div className="ev-list hist-list">
          {changes.map((c: any, i: number) => (
            <div key={c.sha ?? i} className={'ev ev-' + (c.is_revert ? 'revert' : 'apply')}>
              <span className="ev-k">{c.is_revert ? 'revert' : 'self-apply'}</span>
              <span className="ev-s">{(c.subject || '').replace('[self-apply] ', '')}</span>
              <span className="ev-t" title={'touched here: ' + (c.matched_files || []).join(', ')}>
                {(c.matched_files || []).length} file{(c.matched_files || []).length === 1 ? '' : 's'}
              </span>
              <span className="ev-t">{relTime(c.ts)}</span>
              {/* revert FROM here — the EXISTING operator-only api.revert (the /api/revert gate). A revert
                  row is already an undo, so it offers no further revert (no "revert the revert"). */}
              {!c.is_revert && (
                <button className="b ghost sm" data-ui-ref="ui://workshop/self-changes"
                  onClick={() => revertSelfChangeAt(c.sha)} title="git revert this change — bounded, recoverable">
                  ↩ revert
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
