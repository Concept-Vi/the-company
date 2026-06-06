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
//
// AESTHETIC VARIANTS (variant?: 'A'|'B'|'C', default 'A') — the visual reach surface is Tim's design call,
// so this component offers THREE distinguishable aesthetic treatments behind ONE selector (NOT copied
// files — no versioning). The variant branches ONLY the SVG geometry + legend layout, through a single
// per-variant CONFIG object (VARIANTS). ALL logic/behaviour is shared (one render path): the tick/approve
// state machine, the optimistic done-set, the empty-ring filter, the total===0 empty state, the disabled-
// until-ticked control, the default-narrow note, and the ui:// nav guard are identical across variants —
// variants change LOOK only. Colour stays TOKEN-ONLY: each ring's colour lives in its `br-ring-*` class
// (the RINGS table), variants never re-specify colour; per-variant glow/emphasis is a CSS wrapper class
// (`br-variant-<key>`) using existing tokens. The "+N" density cap is VISUAL-ONLY (it caps nodes drawn ON
// the ripple); the legend always lists EVERY member as a tick-able chip, so the state machine spans the
// full member set regardless of variant.
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

// --- the variant CONFIG (geometry + layout ONLY; never colour). One render path reads cfg = VARIANTS[v].
export type ReachVariant = 'A' | 'B' | 'C'
type VariantCfg = {
  label: string                 // the selector label
  desc: string                  // a one-line description of the look (selector tooltip)
  innerR: number                // radius of the innermost ring band (svg units, viewBox 0..200)
  outerR: number                // radius of the outermost ring band
  centreR: number               // the pointed-centre node radius
  bandOffset: number            // how far the members sit out from the ring line (0..1 of band gap)
  nodeR: number                 // base member-node radius (idle)
  nodeRActive: number           // member-node radius when ticked / in-reach
  ringStroke: number            // the ring-outline stroke width
  ringOpacity: number           // the ring-outline opacity
  sizeByKind: boolean           // B: scale node radius by ring index (inner kinds read as "heavier")
  densityCap: number            // max member nodes DRAWN per ring on the svg (0 = no cap). Visual only —
                                // the legend always lists every member. Overflow → a "+N" chip on the ring.
  legend: 'below' | 'inline'    // legend placement: a block below the ripple, or inline ring labels on/near the svg
}
const VARIANTS: Record<ReachVariant, VariantCfg> = {
  // A · the current look — tight even rings, small uniform nodes, legend block below. The known-good baseline.
  A: { label: 'A', desc: 'tight even rings · small nodes · legend below (current)',
    innerR: 26, outerR: 92, centreR: 13, bandOffset: 0.6, nodeR: 3.5, nodeRActive: 5,
    ringStroke: 1, ringOpacity: 0.5, sizeByKind: false, densityCap: 0, legend: 'below' },
  // B · generous & legible — wider ring spacing, larger nodes sized by kind, inline ring labels riding the
  //     bands, and a +N overflow chip on dense rings (the legend still holds every member).
  B: { label: 'B', desc: 'generous spacing · nodes sized by kind · inline ring labels · +N density caps',
    innerR: 34, outerR: 96, centreR: 16, bandOffset: 0.5, nodeR: 4.5, nodeRActive: 6.5,
    ringStroke: 1.4, ringOpacity: 0.65, sizeByKind: true, densityCap: 8, legend: 'inline' },
  // C · dense constellation — rings pulled tight into a compact star-field, tiny glowing nodes, a subtle
  //     glow on the whole field (CSS wrapper, token-driven), legend below. Reads as one constellation.
  C: { label: 'C', desc: 'dense radial constellation · tiny glowing nodes · subtle glow',
    innerR: 22, outerR: 80, centreR: 11, bandOffset: 0.5, nodeR: 2.8, nodeRActive: 4.2,
    ringStroke: 0.8, ringOpacity: 0.4, sizeByKind: false, densityCap: 0, legend: 'below' },
}
const VARIANT_KEYS: ReachVariant[] = ['A', 'B', 'C']

export function BlastRadiusReach({ d, onNavigate, variant: variantProp = 'A' }:
  { d: any; onNavigate?: (address: string) => void; variant?: ReachVariant }) {
  const p = d.payload || {}
  const br = p.blast_radius || {}
  const already: string[] = p.reach_approved || []
  const [ticked, setTicked] = useState<Set<string>>(new Set())
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const [done, setDone] = useState<string[]>([])
  // the live aesthetic choice — a preview affordance, local lane state, defaults to the prop (A). Flipping
  // it re-renders the SAME real data through a different geometry/layout config. Not persisted (out of lane).
  const [variant, setVariant] = useState<ReachVariant>(variantProp)
  const cfg = VARIANTS[variant]

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

  // the per-ring radius (the band line each kind's members sit on). Shared formula; the variant config
  // (innerR/outerR/bandOffset) is the ONLY thing that changes the spacing between variants.
  function ringRadius(ri: number): number {
    const gap = (cfg.outerR - cfg.innerR) / Math.max(1, rings.length)
    return cfg.innerR + ri * gap + gap * cfg.bandOffset
  }
  // the member-node radius for ring index ri (B scales inner=heavier; A/C uniform). The active (ticked/in-
  // reach) radius is the variant's nodeRActive. Shared everywhere a node is drawn.
  function nodeRadius(ri: number, active: boolean): number {
    if (active) return cfg.nodeRActive
    if (!cfg.sizeByKind) return cfg.nodeR
    // sized by kind: innermost (more impactful) rings read larger. rings.length is small (≤4).
    const span = Math.max(1, rings.length - 1)
    return cfg.nodeR + (1 - ri / span) * (cfg.nodeRActive - cfg.nodeR) * 0.7
  }

  return (
    <div className={'br-reach br-variant-' + variant} data-needs-tim="x16-reach-surface">
      <div className="br-reach-head">
        reach <span className="muted">· {total} related{approvedAll.size ? ` · ${approvedAll.size} in reach` : ''}</span>
        {/* THE AESTHETIC VARIANT SELECTOR — a small on-design-system segmented control so the operator flips
            the ripple's LOOK live (real data re-renders) and chooses one. A preview affordance, not data:
            it carries no data-ui-ref (it addresses no feature, it tunes presentation), defaults to A, and
            does not persist (the choice is Tim's to make by sight, then declare). */}
        <div className="br-variant-pick" role="group" aria-label="ripple aesthetic variant (preview)"
          title="preview the ripple's look — flip A/B/C to choose an aesthetic (real data re-renders)">
          <span className="br-variant-tag muted">look</span>
          {VARIANT_KEYS.map(k => (
            <button key={k} type="button"
              className={'br-variant-btn' + (k === variant ? ' on' : '')}
              aria-pressed={k === variant}
              title={VARIANTS[k].desc}
              onClick={() => setVariant(k)}>{VARIANTS[k].label}</button>
          ))}
        </div>
      </div>
      {/* THE RIPPLE — rendered as ACTUAL concentric rings around the pointed centre, not a flex list. Each
          ring is a relationship KIND (innermost = the pointed address; outward = co-reference · would-break
          dependents · relies-on dependencies · semantic). A member sits ON its ring (distinguished by ring
          radius + kind colour-token + the legend), and the legend below maps each ring band to its members
          as tick-able chips (the ON-ring nodes and the legend chips share state). Default reach = the centre
          ONLY; ticking pulls a member INTO the reach (widens the scope). px geometry is lint-free; colour is
          token-only. Legible at 285px, scales up via the SVG viewBox. The GEOMETRY (radii/spacing/node-size/
          density-cap/labels) is driven by the per-variant config; behaviour is shared. */}
      <div className="br-ripplemap" role="img"
        aria-label={`blast radius ripple: ${total} related code members across ${rings.length} relationship rings`}>
        <svg className="br-rings-svg" viewBox="0 0 200 200" preserveAspectRatio="xMidYMid meet">
          {/* the concentric ring outlines — one per present kind, evenly spaced from the centre outward.
              stroke width + opacity are variant-config (token colour stays on the br-ring-* class). */}
          {rings.map((r, ri) => (
            <circle key={'c' + r.key} cx="100" cy="100" r={ringRadius(ri)}
              className={'br-ring-circle ' + r.cls}
              strokeWidth={cfg.ringStroke} style={{ opacity: cfg.ringOpacity }} />
          ))}
          {/* the pointed centre — the default reach, always in scope. Radius is variant-config. */}
          <circle cx="100" cy="100" r={cfg.centreR} className="br-centre-node" />
          {/* each member placed ON its ring by angle (distributed around the circle). The "+N" density cap
              (cfg.densityCap) limits how many nodes are DRAWN on a dense ring — VISUAL ONLY (the legend
              below still lists every member as a tick-able chip, so the tick/approve state machine spans
              the full set). The overflow is shown as a single "+N" chip on the ring's far edge. */}
          {rings.map((r, ri) => {
            const radius = ringRadius(ri)
            const cap = cfg.densityCap
            const drawn = cap > 0 && r.members.length > cap ? r.members.slice(0, cap) : r.members
            const overflow = r.members.length - drawn.length
            const slots = drawn.length + (overflow > 0 ? 1 : 0)   // reserve an angular slot for the +N chip
            const nodes = drawn.map((m, mi) => {
              const ang = (mi / slots) * Math.PI * 2 - Math.PI / 2
              const cx = 100 + radius * Math.cos(ang)
              const cy = 100 + radius * Math.sin(ang)
              const inReach = approvedAll.has(m)
              const on = ticked.has(m)
              return (
                <circle key={'m' + r.key + m} cx={cx} cy={cy} r={nodeRadius(ri, inReach || on)}
                  className={'br-node ' + r.cls + (inReach ? ' in-reach' : on ? ' ticked' : '')}
                  onClick={() => toggle(m)}>
                  <title>{m}{inReach ? ' · in reach' : on ? ' · ticked' : ' · click to tick (widen the reach)'}</title>
                </circle>
              )
            })
            // the +N overflow chip — a single mark standing for the capped-off members (all still listed +
            // tick-able in the legend). Placed in the reserved final angular slot on this ring.
            const overflowMark = overflow > 0 ? (() => {
              const ang = (drawn.length / slots) * Math.PI * 2 - Math.PI / 2
              const cx = 100 + radius * Math.cos(ang)
              const cy = 100 + radius * Math.sin(ang)
              return (
                <g key={'ov' + r.key} className={'br-overflow ' + r.cls}>
                  <circle cx={cx} cy={cy} r={cfg.nodeRActive + 1} className={'br-overflow-node ' + r.cls} />
                  <text x={cx} y={cy} className="br-overflow-text" textAnchor="middle" dominantBaseline="central">+{overflow}
                    <title>{overflow} more on this ring — all listed + tick-able in the legend below</title>
                  </text>
                </g>
              )
            })() : null
            // INLINE RING LABEL (variant B) — a short kind label riding the ring's top, so the picture
            // self-explains without dropping to the legend. The legend still carries the chips.
            const inlineLabel = cfg.legend === 'inline' ? (
              <text key={'rl' + r.key} x="100" y={100 - radius - 2} textAnchor="middle"
                className={'br-ring-label ' + r.cls}>{r.label.split(' (')[0]}
                <title>{r.hint}</title>
              </text>
            ) : null
            return <g key={'g' + r.key}>{nodes}{overflowMark}{inlineLabel}</g>
          })}
        </svg>
        <div className="br-centre-cap" title="the pointed address — the DEFAULT reach (always in scope)">
          pointed{scope.length ? ` · ${scope.length}` : ''}
        </div>
      </div>
      {/* THE LEGEND — each ring band named + its members as tick chips. The ring is the spatial picture; the
          legend is where the operator reads + ticks. The on-ring nodes and these chips share toggle state.
          The legend ALWAYS lists every member (even those capped off the ripple by the +N density cap), so
          the tick/approve state machine spans the full member set regardless of variant. */}
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
