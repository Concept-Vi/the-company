// X16 · operator-approves-the-reach — the BLAST-RADIUS / REACH surface (a SENSIBLE DEFAULT, flagged
// needs-tim; the visual reach surface is a RESERVED Tim design call — this is a reasonable first form,
// NOT a finished/green one). Renders a build-intent's persisted blast_radius (X14) as a NAVIGABLE
// VISUAL RIPPLE (concentric rings by relationship kind — the ripple SEEN, not a text-wall) with the
// reach-approval control: the operator ticks named members to WIDEN the build's editable scope to their
// files. DEFAULT-NARROW: nothing ticked → no call → the scope stays the pointed address only (never
// silently expands). EXPANSION is the explicit tick + "approve the reach" act. Operator-only (the
// /api/approve-reach route is off the MCP face). Pure presentation + the one operator action; built on
// the corpus design system (tokens only, no hardcoded colour) under the existing ui://inbox/build-intent
// ref (no new data-ui-ref). PanelErrorBoundary-wrapped at the call site.
import { useMemo, useState } from 'react'
import { api } from '../api'

// the four relationship rings, INNERMOST (the pointed address) outward — the ripple's structure.
// Each ring is a KIND of blast-radius member, distinguished (the X14 return shape).
const RINGS: { key: string; label: string; hint: string; cls: string }[] = [
  { key: 'structural_dependents', label: 'would break (dependents)', cls: 'br-ring-dependents',
    hint: 'symbols that DEPEND ON this code — a rename here ripples into them (verify them)' },
  { key: 'structural_dependencies', label: 'relies on (dependencies)', cls: 'br-ring-dependencies',
    hint: 'symbols this code DEPENDS ON — respect them; an edit may need them' },
  { key: 'co_reference', label: 'shares this code', cls: 'br-ring-coref',
    hint: 'other addresses/features that touch the SAME code symbol' },
  { key: 'semantic_neighbours', label: 'conceptually near', cls: 'br-ring-semantic',
    hint: 'conceptually-related code with no direct code link (semantic)' },
]

export function BlastRadiusReach({ d, onNavigate }: { d: any; onNavigate?: (address: string) => void }) {
  const p = d.payload || {}
  const br = p.blast_radius || {}
  const already: string[] = p.reach_approved || []
  const [ticked, setTicked] = useState<Set<string>>(new Set())
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const [done, setDone] = useState<string[]>([])

  // the members per ring, from the persisted radius (consent-time — what the operator SAW).
  const rings = useMemo(() => RINGS.map(r => ({ ...r, members: (br[r.key] as string[]) || [] }))
    .filter(r => r.members.length > 0), [br])
  const total = rings.reduce((n, r) => n + r.members.length, 0)

  // the pointed-address ring is the build's declared scope (the narrow default) — the ripple's centre.
  const scope: string[] = p.scope || []

  // ALREADY-APPROVED set (persisted) ∪ this-session ticks — both render as "in the reach".
  const approvedAll = useMemo(() => new Set([...already, ...done]), [already, done])

  function toggle(m: string) {
    if (approvedAll.has(m)) return                 // already in the reach — not re-tickable
    setTicked(s => { const n = new Set(s); n.has(m) ? n.delete(m) : n.add(m); return n })
  }

  async function approve() {
    const members = [...ticked]
    if (members.length === 0) return
    setBusy(true); setErr(null)
    try {
      const r = await api.approveReach(d.id, members)
      if ((r as any)?.error) { setErr((r as any).error); return }
      setDone(x => [...x, ...members])             // optimistic — they are now in the reach
      setTicked(new Set())
    } catch (e: any) {
      setErr(String(e?.message || e))              // fail loud — never a silent no-op
    } finally { setBusy(false) }
  }

  // EMPTY-STATE: a build whose address resolves to no code (orphan) has an empty radius — nothing to
  // expand. Say so plainly (the DENY-ALL build reaches nothing); never an empty box.
  if (total === 0) {
    return (
      <div className="br-reach br-empty" title="this build's address resolves to no related code — its reach is the pointed address only">
        <div className="br-reach-head">reach</div>
        <div className="br-empty-note">no related code — the edit reaches only the pointed address{(br.note ? ' · ' + br.note : '')}</div>
      </div>
    )
  }

  return (
    <div className="br-reach" data-needs-tim="x16-reach-surface">
      <div className="br-reach-head">
        reach <span className="muted">· {total} related{approvedAll.size ? ` · ${approvedAll.size} in reach` : ''}</span>
      </div>
      {/* the RIPPLE — the pointed address at the centre, the relationship rings around it. The default
          reach is the centre ONLY; ticking a ring member pulls it INTO the reach (widens the scope). */}
      <div className="br-ripple">
        <div className="br-centre" title="the pointed address — the DEFAULT reach (always in scope)">
          <span className="br-centre-dot" />
          <span className="br-centre-label">pointed{scope.length ? ` · ${scope.length} file(s)` : ''}</span>
        </div>
        {rings.map(r => (
          <div key={r.key} className={'br-ring ' + r.cls} title={r.hint}>
            <div className="br-ring-label">{r.label} <span className="muted">· {r.members.length}</span></div>
            <div className="br-chips">
              {r.members.map(m => {
                const inReach = approvedAll.has(m)
                const on = ticked.has(m)
                return (
                  <span key={m} className={'br-chip' + (inReach ? ' in-reach' : on ? ' ticked' : '')}>
                    <button type="button" className="br-chip-tick"
                      disabled={inReach || busy}
                      title={inReach ? 'in the approved reach' : on ? 'click "approve reach" to widen the edit to this' : 'tick to widen the edit-scope to reach this'}
                      onClick={() => toggle(m)}>
                      {inReach ? '◉' : on ? '◉' : '○'}
                    </button>
                    <button type="button" className="br-chip-label"
                      title={'go to ' + m}
                      onClick={() => onNavigate && onNavigate(m)}>{m}</button>
                  </span>
                )
              })}
            </div>
          </div>
        ))}
      </div>
      {/* the REACH-APPROVAL act — explicit, operator-only, default-narrow (disabled until something is
          ticked). Approving widens the build's editable scope to the ticked members' files. */}
      <div className="br-reach-act">
        <button type="button" className="b sm br-approve" disabled={ticked.size === 0 || busy}
          title="widen this build's editable scope to reach the ticked related code (the operator authorizes how far the edit propagates)"
          onClick={approve}>
          {busy ? 'widening…' : ticked.size ? `approve reach · +${ticked.size}` : 'tick to widen the reach'}
        </button>
        <span className="br-default-note muted">default: the pointed address only</span>
      </div>
      {err && <div className="br-err" title="the reach approval failed — fail loud, nothing silently widened">✕ {err}</div>}
    </div>
  )
}
