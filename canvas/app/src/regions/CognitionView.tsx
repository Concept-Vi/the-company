// L-fe · the LIVE COGNITION VIEW (criterion L-fe; build-prep/concurrent-cognition/explore/E2-cognition-view-ux.md).
//
// WHAT THIS IS: the operator's window onto the system's OWN thinking — "the commander's bridge" (06 §D, E2 §B).
// It EXTENDS the canvas (it is one MORE region beside Activity/RhmChat; it removes/replaces nothing) and is
// driven ENTIRELY by the live `cognition.*` SSE lifecycle the L-fe-be backend emits (the controller's
// foldCognition + the openStream cognition.* branch). reflects-never-owns: this view issues NO writes — it
// only READS /api/cognition_info (the registry projection) + the folded live turn. registry-driven (rule 8):
// the River's tributaries come from the turn's `cast[]` and the projection's roles — NO hardcoded role list,
// so a new role registered engine-side appears here with zero FE code.
//
// THE THREE ALTITUDES (E2 §B — the up-translation, default → drill-down):
//   • Altitude 0 — THE PULSE (default, ambient): a small breathing iris/aperture beside the reply. It
//     DILATES with how much cognition the turn took (roles fired + chars injected — shape-not-count, never
//     N hard dots), and carries a LOUD notch if a role FAILED (fail-loud at altitude, rule 4). One glyph =
//     the character of the turn. Click it to descend.
//   • Altitude 1 — THE RIVER (one click): the turn as a converging flow — roles enter as tributaries on the
//     left, width = contribution (injected chars, the budget=attention shape), a DRY gap for a cast role that
//     never fired, a RED silted stub for a role that failed — all converging into the BRAIN node → the reply.
//     The river FILLS in event order as cognition.* arrive (motion = content, E2 §D).
//   • Altitude 2 — THE NODES (toggle): the literal role cards (label · model · status · contribution · ms),
//     reusing the inspector DOM card pattern (NOT a tldraw board — roles are events, not graph nodes).
//
// FORM = needs-tim (E2 §9, AGENTS rule 9): the iris aesthetics, the river beauty/legibility, the felt shape,
// on-device legibility are NOT self-certified here. Built on the design system tokens ONLY (no bespoke hex/px
// beyond layout geometry of the self-contained SVG); the implementer does NOT grade FORM.
import { useState } from 'react'
import { useApp } from '../AppContext'

// map a role's lifecycle status → its by-sight render token. The REGISTERED states (ran/failed) read their
// token FROM the projection's node_states (registry-is-truth, rule 3 — exactly how NodeShape reads
// NODE_STATES); the lifecycle-only states (latent/firing/injected) — which the backend has NOT yet
// registered as node_states (06 §F#4 named them net-new) — fall back to design-system tokens. So a state
// the backend later registers will paint from its registered token automatically.
function statusToken(status: string, nodeStates: any[]): string {
  const reg = (Array.isArray(nodeStates) ? nodeStates : []).find((s: any) => s.id === status)
  if (reg?.render?.token) return reg.render.token
  switch (status) {
    case 'failed': return '--fail'
    case 'injected': return '--acc'        // contributed to the reply — the worn, bright channel
    case 'ran': return '--ok'
    case 'firing': return '--await'        // model call in flight — the warming amber
    case 'latent': return '--tx-3'         // declared but not fired — the faint/dry trace
    default: return '--tx-3'
  }
}

export function CognitionView() {
  const { cognitionInfo, cognitionTurn } = useApp()
  const [altitude, setAltitude] = useState(0)   // 0 = Pulse (default) · 1 = River · 2 = Nodes
  const nodeStates: any[] = cognitionInfo?.node_states || []
  const roleMeta: Record<string, any> = cognitionInfo?.roles || {}
  const turn = cognitionTurn

  // ---- the turn's SHAPE (shape-not-count) — derived purely from the folded lifecycle ----
  const roles: any[] = turn ? Object.values(turn.roles || {}) : []
  const nFired = roles.filter(r => r.status !== 'latent').length
  const nFailed = roles.filter(r => r.status === 'failed').length
  const injectedChars = turn?.injected_chars || 0
  // dilation: 0..1 — how much cognition (roles that fired + injected volume). shape-not-count: this is a
  // CONTINUOUS quantity (an opening aperture), never a literal count of dots (E2 §A/§C).
  const dilation = turn ? Math.min(1, (nFired / 8) * 0.6 + Math.min(1, injectedChars / 1200) * 0.4) : 0
  const active = !!turn && !turn.done
  const calm = !turn || (turn.done && nFired === 0)

  // ---------------------------------------------------------------- Altitude 0 · THE PULSE (default)
  // the breathing iris: a ring whose inner aperture opens with `dilation`. brightens (--acc) while active,
  // calm (--cache, dim) when idle/already-knew, a LOUD red notch (--fail) when any role failed (rule 4).
  // shape-not-count: the operator reads depth-of-thought as OPENNESS, not by counting tributaries.
  const R = 13, cx = 16, cy = 16
  const aperture = 2 + dilation * 8                          // inner radius grows with cognition
  const ringToken = nFailed > 0 ? '--fail' : active ? '--acc' : calm ? '--cache' : '--acc-deep'
  function Pulse() {
    return (
      <button className={'cog-pulse' + (active ? ' active' : '') + (nFailed ? ' notched' : '')}
        title={turn
          ? `cognition · ${nFired} role${nFired === 1 ? '' : 's'} fired${injectedChars ? ` · ${injectedChars} chars fed the reply` : ''}${nFailed ? ` · ${nFailed} FAILED` : ''}${turn.done ? '' : ' · thinking…'} — click to open the river`
          : 'cognition — no staged turn yet (a substantive turn in a staging mode opens the river)'}
        onClick={() => setAltitude(1)} data-ui-ref="ui://cognition/pulse">
        <svg width={32} height={32} viewBox="0 0 32 32" aria-hidden>
          {/* the breathing ring — its colour is the turn's character */}
          <circle cx={cx} cy={cy} r={R} fill="none" stroke={`var(${ringToken})`} strokeWidth={2}
            style={{ opacity: active ? 0.95 : 0.6 }} className={active ? 'cog-ring-breathe' : ''} />
          {/* the aperture — opens with depth-of-thought (dilation). filled with the glow token. */}
          <circle cx={cx} cy={cy} r={aperture} fill={`var(${ringToken})`}
            style={{ opacity: 0.28 + dilation * 0.5, transition: 'r .4s ease, opacity .4s ease' }} />
          {/* the LOUD notch — a wound on the ring when a role failed (fail-loud at altitude, rule 4) */}
          {nFailed > 0 && <rect x={cx - 1.5} y={cy - R - 2} width={3} height={6} fill="var(--fail)" />}
        </svg>
      </button>
    )
  }

  // ---------------------------------------------------------------- Altitude 1 · THE RIVER
  // a self-contained SVG: tributaries (one per cast role) on the left converge into the BRAIN node on the
  // right, which empties toward the reply. We REUSE the Edges *pattern* (screen-space SVG, token strokes,
  // a bezier per channel) but NOT the graph-coupled `Edges` COMPONENT — roles are cognition EVENTS, not
  // api.graph() nodes (loadGraph would prune any invented role shape; inventing positions violates
  // reflects-never-owns). This is E2 §H fork#3's lean (River as an expand-in-place panel). See the report's
  // reuse/net-new note. width = contribution (injected chars); a latent role = a faint DRY trace; a failed
  // role = a RED silted stub that does NOT reach the brain.
  function River() {
    const cast: string[] = turn ? (turn.cast?.length ? turn.cast : roles.map(r => r.role)) : []
    const W = 320, H = Math.max(120, cast.length * 26 + 40), bx = W - 64, by = H / 2, gap = (H - 30) / Math.max(1, cast.length)
    const maxChars = Math.max(1, ...roles.map(r => r.chars || 0))
    return (
      <div className="cog-river" data-ui-ref={turn?.address || 'ui://cognition/river'}>
        <svg width="100%" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" className="cog-river-svg">
          {cast.map((rid, i) => {
            const r = (turn?.roles || {})[rid] || { status: 'latent', chars: 0 }
            const y = 20 + i * gap
            const tok = statusToken(r.status, nodeStates)
            const fired = r.status !== 'latent'
            const failed = r.status === 'failed'
            const contrib = r.chars || 0
            const width = fired ? 1.5 + (contrib / maxChars) * 6 : 1     // worn-channel width = contribution
            const opacity = failed ? 0.9 : fired ? 0.4 + (contrib / maxChars) * 0.55 : 0.2  // faint/dry if latent
            // a failed channel ends in a silted stub short of the brain; others reach it.
            const endX = failed ? bx - 70 : bx
            const mx = (40 + endX) / 2
            return (
              <g key={rid}>
                <path d={`M 8 ${y} C ${mx} ${y} ${mx} ${by} ${endX} ${by}`} fill="none"
                  stroke={`var(${tok})`} strokeWidth={width} strokeLinecap="round"
                  strokeDasharray={fired ? undefined : '3 4'}   // latent = a dotted dry trace
                  style={{ opacity, transition: 'stroke-width .4s ease, opacity .4s ease' }} />
                {failed && <circle cx={endX} cy={by} r={3} fill="var(--fail)" />}{/* the red silted stub */}
                <text x={6} y={y - 4} className="cog-trib-label" fill={`var(${fired ? tok : '--tx-3'})`}>
                  {roleMeta[rid]?.label || rid}{contrib ? ` · ${contrib}` : ''}{failed ? ' ✕' : ''}
                </text>
              </g>
            )
          })}
          {/* the BRAIN node — the one coherent voice all tributaries converge into (E2 §B.2) */}
          <circle cx={bx} cy={by} r={16} fill="var(--acc-glow)" stroke={`var(${active ? '--acc' : '--acc-deep'})`}
            strokeWidth={2} className={active ? 'cog-ring-breathe' : ''} />
          <text x={bx} y={by + 4} textAnchor="middle" className="cog-brain-label" fill="var(--acc)">brain</text>
          {/* brain → reply (a terminal cue toward the chat lane, NOT a shape-to-shape edge — 06 §D) */}
          <path d={`M ${bx + 16} ${by} L ${W - 4} ${by}`} stroke="var(--acc-dim)" strokeWidth={2}
            markerEnd="url(#cog-arrow)" />
          <defs><marker id="cog-arrow" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="var(--acc-dim)" /></marker></defs>
        </svg>
        <div className="cog-river-foot muted">
          {turn
            ? <>{nFired}/{cast.length} tributaries{injectedChars ? ` · ${injectedChars} chars into the reply` : ''}{turn.parts ? ` · ${turn.parts} parts` : ''}{turn.done ? ` · ${turn.total_ms}ms` : ' · flowing…'}{nFailed ? ` · ${nFailed} silted (failed)` : ''}</>
            : 'no staged turn yet — speak (or type) a substantive turn in a staging mode to fill the river'}
        </div>
      </div>
    )
  }

  // ---------------------------------------------------------------- Altitude 2 · THE NODES (role cards)
  // the literal swarm — one card per cast role, reusing the inspector DOM card pattern (.cog-node), NOT a
  // tldraw board. Each card: label · effective model · status (by-sight token) · contribution · ms · the
  // role's trigger (from the projection — why it's in the cast, E2 §E.2). registry-driven: a new role appears.
  function Nodes() {
    const cast: string[] = turn ? (turn.cast?.length ? turn.cast : roles.map(r => r.role)) : []
    return (
      <div className="cog-nodes">
        {cast.length === 0 && <div className="muted">no staged turn yet.</div>}
        {cast.map(rid => {
          const r = (turn?.roles || {})[rid] || { status: 'latent', chars: 0, ms: 0 }
          const meta = roleMeta[rid] || {}
          const tok = statusToken(r.status, nodeStates)
          const regLabel = (nodeStates.find((s: any) => s.id === r.status) || {}).label
          return (
            <div key={rid} className={'cog-node ' + r.status} data-ui-ref={`run://${turn?.turn_id}/${rid}`}>
              <div className="cog-node-bar">
                <span className="cog-dot" style={{ background: `var(${tok})`, boxShadow: `0 0 8px var(${tok})` }} />
                <span className="cog-node-title">{meta.label || rid}</span>
                <span className="cog-node-status muted">{regLabel ? regLabel.toLowerCase() : r.status}</span>
              </div>
              <div className="cog-node-meta muted">
                {r.model ? <span>{r.model}</span> : null}
                {r.chars ? <span> · {r.chars} chars fed</span> : null}
                {r.ms ? <span> · {r.ms}ms</span> : null}
                {r.status === 'failed' && r.error ? <span className="cog-err"> · ✕ {r.error}</span> : null}
              </div>
              {meta.trigger && <div className="cog-node-trigger muted" title="why this role is in the cast">{meta.trigger}</div>}
            </div>
          )
        })}
      </div>
    )
  }

  // ---------------------------------------------------------------- the region shell
  // Altitude 0 (Pulse) is the DEFAULT ambient form — a small glyph that never clutters. River/Nodes are the
  // deeper altitudes, shown only when the operator descends (click the pulse). The header carries the
  // altitude controls + a back-to-pulse. EXTEND not replace: this is additive chrome beside the chat lane.
  return (
    <div className="hud cog" data-ui-ref="ui://cognition" data-cog-altitude={altitude}>
      {altitude === 0 && (
        <div className="cog-pulse-wrap" title="cognition — the system's thinking for the last turn">
          <Pulse />
          <span className="cog-pulse-label muted">{active ? 'thinking…' : turn ? 'thought' : 'cognition'}</span>
        </div>
      )}
      {altitude > 0 && (
        <div className="cog-deep">
          <div className="cog-head">
            <span className="cog-title">cognition{turn ? ` · turn ${String(turn.turn_id).slice(-6)}` : ''}</span>
            <span className="cog-alts">
              <button className={'cog-alt' + (altitude === 1 ? ' on' : '')} onClick={() => setAltitude(1)} title="the river — the converging flow">river</button>
              <button className={'cog-alt' + (altitude === 2 ? ' on' : '')} onClick={() => setAltitude(2)} title="the nodes — the literal role cards">nodes</button>
              <button className="cog-alt close" onClick={() => setAltitude(0)} title="back to the pulse">▁</button>
            </span>
          </div>
          {altitude === 1 ? <River /> : <Nodes />}
        </div>
      )}
    </div>
  )
}
