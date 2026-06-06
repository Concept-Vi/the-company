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

  // NAVIGATION GUARD: a blast-radius member is a `code://` address (X9/X14 read code-edges.json, keyed by
  // code:// ids). resolveUiTarget's registry-validated + fail-loud path is for `ui://` strings ONLY — a
  // `code://` string skips the grammar/registry gate and falls to driveCanvas (the camera path), which
  // would mis-route to "no node on the canvas". WHERE a code:// member navigates TO (resolve the code locus
  // on the canvas / open the source) is a RESERVED Tim design call (the original note's 2nd clause). So we
  // only fire onNavigate for a `ui://` member; a non-ui:// member's label stays inert (no wrong jump),
  // pending the reserved design pass. ui:// members (if any surface) get the keystone's validated drive.
  function navigable(m: string): boolean { return typeof m === 'string' && m.startsWith('ui://') }

  // a short, legible leaf name for a long ui:///code:// member address (the chip shows the tail; the full
  // address is the title/tooltip). Keeps the ripple legible at the ~285px right-rail width.
  function leaf(m: string): string {
    const noState = m.split('/@')[0]
    const tail = noState.split('/').filter(Boolean).pop() || noState
    return tail.length > 18 ? tail.slice(0, 17) + '…' : tail
  }

  return (
    <div className="br-reach" data-needs-tim="x16-reach-surface">
      <div className="br-reach-head">
        reach <span className="muted">· {total} related{approvedAll.size ? ` · ${approvedAll.size} in reach` : ''}</span>
      </div>
      {/* THE RIPPLE — rendered as ACTUAL concentric rings around the pointed centre, not a flex list. Each
          ring is a relationship KIND (innermost = the pointed address; outward = co-reference · would-break
          dependents · relies-on dependencies · semantic). A member sits ON its ring (distinguished by ring
          radius + kind colour-token + the legend), and the legend below maps each ring band to its members
          as tick-able chips (the ON-ring nodes and the legend chips share state). Default reach = the centre
          ONLY; ticking pulls a member INTO the reach (widens the scope). px geometry is lint-free; colour is
          token-only. Legible at 285px, scales up via the SVG viewBox. */}
      <div className="br-ripplemap" role="img"
        aria-label={`blast radius ripple: ${total} related code members across ${rings.length} relationship rings`}>
        <svg className="br-rings-svg" viewBox="0 0 200 200" preserveAspectRatio="xMidYMid meet">
          {/* the concentric ring outlines — one per present kind, evenly spaced from the centre outward. */}
          {rings.map((r, ri) => {
            const radius = 26 + ri * ((92 - 26) / Math.max(1, rings.length)) + ((92 - 26) / Math.max(1, rings.length)) * 0.6
            return <circle key={'c' + r.key} cx="100" cy="100" r={radius}
              className={'br-ring-circle ' + r.cls} />
          })}
          {/* the pointed centre — the default reach, always in scope. */}
          <circle cx="100" cy="100" r="13" className="br-centre-node" />
          {/* each member placed ON its ring by angle (distributed around the circle). */}
          {rings.map((r, ri) => {
            const radius = 26 + ri * ((92 - 26) / Math.max(1, rings.length)) + ((92 - 26) / Math.max(1, rings.length)) * 0.6
            return r.members.map((m, mi) => {
              const ang = (mi / r.members.length) * Math.PI * 2 - Math.PI / 2
              const cx = 100 + radius * Math.cos(ang)
              const cy = 100 + radius * Math.sin(ang)
              const inReach = approvedAll.has(m)
              const on = ticked.has(m)
              return (
                <circle key={'m' + r.key + m} cx={cx} cy={cy} r={inReach ? 5 : on ? 5 : 3.5}
                  className={'br-node ' + r.cls + (inReach ? ' in-reach' : on ? ' ticked' : '')}
                  onClick={() => toggle(m)}>
                  <title>{m}{inReach ? ' · in reach' : on ? ' · ticked' : ' · click to tick (widen the reach)'}</title>
                </circle>
              )
            })
          })}
        </svg>
        <div className="br-centre-cap" title="the pointed address — the DEFAULT reach (always in scope)">
          pointed{scope.length ? ` · ${scope.length}` : ''}
        </div>
      </div>
      {/* THE LEGEND — each ring band named + its members as tick chips. The ring is the spatial picture; the
          legend is where the operator reads + ticks. The on-ring nodes and these chips share toggle state. */}
      <div className="br-legend">
        {rings.map(r => (
          <div key={r.key} className={'br-band ' + r.cls} title={r.hint}>
            <div className="br-band-label"><span className="br-band-swatch" /> {r.label} <span className="muted">· {r.members.length}</span></div>
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
                      disabled={!navigable(m)}
                      title={navigable(m) ? ('go to ' + m) : (m + ' (code locus — navigation is a reserved design call)')}
                      onClick={() => navigable(m) && onNavigate && onNavigate(m)}>{leaf(m)}</button>
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
