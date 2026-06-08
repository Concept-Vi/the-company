// G-4 · THE SELF-BUILD WIRE'S OPERATOR DOOR (the missing FE caller for the decision→implementation wire;
// REPO-KNOWLEDGE D1 — "/api/build-intent has no FE caller", the #1 UI gap). This is the door to "change the
// Company through the interface": point at a ui:// element → describe the change → it MINTS a build-intent
// (POST /api/intent-at, via ctrl.mintBuildIntent) that derives its scope from the pointed address and carries
// the X16 blast-radius computed at consent time → the operator SEES the reach (the existing BlastRadiusReach
// ripple, reused not reimplemented) → approves it + (optionally) widens the reach. The shape is the wire's
// door: POINT → ASK → SEE THE REACH → APPROVE.
//
// SAFE-BY-DEFAULT / NO FICTION: minting a build-intent is composing a PLAN, never a live self-modify. The
// wire is INERT-by-default — dispatch runs under permission-mode `plan` (read-only) unless the operator
// deliberately arms it (COMPANY_WIRE_PERMISSION=acceptEdits, a backend env-gate not exposed to the FE). The
// armed state is NOT served on any route, so the door states the safe default as honest STATIC copy ("mints a
// plan for approval; dispatch is inert/plan-mode by default") — it does NOT render a live armed light it
// cannot back with data. Approving here records the operator verdict (/api/resolve); the watcher
// (drive_dispatchable) decides dispatch, posture-gated + exactly-once + guarded-close, off this face.
//
// THE SIBLING OF AnnotateBar (App.tsx): both render ONLY when a ui:// element is indicated, both float over
// the canvas cell, both reuse the .rhm-indicating chip vocabulary (tokens only, design-lint clean). Where
// AnnotateBar attaches a COMMENT, this REQUESTS A CHANGE. The wire's signature colour is WIRE-BLUE (the kit
// `wire` tone = --kind-content), matching the Inbox "decision → build" lane, so a glance ties the door to
// where the minted intent lands. Composed FROM the kit (Surface/Badge) + the corpus tokens — recognition by
// shape+tint, not by reading.
import { useState } from 'react'
import { api } from '../api'
import { useApp } from '../AppContext'
import { Badge } from './kit'
import { BlastRadiusReach } from './BlastRadiusReach'
import { getUI_INFO } from '../registryStore'

export function WireRequest() {
  const { indicated, clickMode, mintBuildIntent, resolveUiTarget, inbox } = useApp()
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  // the minted build-intent's ID (resolved=None). We hold the ID, not the mint's RETURN: surface_intent_at
  // returns a FLAT summary ({id, intent, scope, address, stale, note}) — the X16 BLAST-RADIUS lives in the
  // PERSISTED item's `payload.blast_radius`, not the return dict. So the door resolves the FULL item from
  // the live inbox (reflects-never-owns: the runtime owns it, the surface reads it) — `mintBuildIntent`
  // poll()s before returning, so the item is in `inbox` by then. This is what makes the door show the reach
  // (the existing ripple reads `d.payload.blast_radius`), not a perpetual empty-reach.
  const [mintedId, setMintedId] = useState<string | null>(null)
  const [mintedFallback, setMintedFallback] = useState<any | null>(null)   // the flat return, if the inbox lags
  const [approved, setApproved] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  // the FULL persisted minted item (carries payload.blast_radius) — found in the live inbox by id; falls
  // back to the flat mint return (no reach) only until the inbox catches up.
  const minted = mintedId
    ? ((inbox?.live_escalations || []).find((d: any) => d.id === mintedId) || mintedFallback)
    : null

  // RENDER GATE: only for an indicated ui:// element whose bare-click face is 'annotate' — i.e. a DESIGN/UI
  // element (not a run:// live node, whose bare click OPERATES). This is exactly where "request a change to
  // this element" is the meaningful gesture. Mirrors AnnotateBar's gate (single-sourced clickMode), so the
  // two mode-affordances never both claim an element. Hidden otherwise → never clutters the canvas.
  if (!indicated || clickMode(indicated) !== 'annotate') return null

  const title = getUI_INFO()[indicated]?.title || indicated

  async function request() {
    const t = text.trim(); if (!t || busy) return
    setBusy(true); setErr(null)
    const r = await mintBuildIntent(t)   // POST /api/intent-at — mint-only, fail-loud (notice on error)
    setBusy(false)
    // hold the minted id → the door resolves the FULL persisted item (with the X16 reach) from the live
    // inbox. Keep the flat return as a fallback until the inbox snapshot catches up.
    if (r && !r.error && r.id) { setMintedId(r.id); setMintedFallback(r); setText('') }
    // a failure already surfaced a notice via mintBuildIntent; nothing minted, the door stays in ask-mode
  }

  // APPROVE the minted build-intent — the operator verdict (the ONLY writer of `resolved`, /api/resolve).
  // This does NOT itself dispatch: it records approve; the watcher (drive_dispatchable) selects + dispatches
  // under the posture gate, exactly-once, off this face. Safe-by-default: with the wire un-armed (plan mode,
  // the default), an approved intent is a PLAN awaiting arming — never a live self-modify. Fail-loud.
  async function approve() {
    if (!minted?.id || busy) return
    setBusy(true); setErr(null)
    try {
      const res = await api.resolve(minted.id, 'approve')
      if ((res as any)?.error) { setErr((res as any).error); return }
      setApproved(true)
    } catch (e: any) { setErr(String(e?.message || e)) }
    finally { setBusy(false) }
  }

  function dismiss() { setMintedId(null); setMintedFallback(null); setApproved(false); setErr(null) }

  return (
    // data-ui-ref is on the OUTER door so the registry resolves it; the onDocClick capture EXCLUDES this
    // subtree (useAppController) so clicking inside the door never re-indicates it (would overwrite the
    // operator's pointed target). The wire-blue tint (.kit-tone-wire) is the wire's signature.
    <div className="wire-door kit-tone-wire" data-ui-ref="ui://canvas/wire-request"
         title="request a change to the pointed element — mints a build-intent (a plan) for your approval">
      <div className="wire-door-head">
        <span className="ic">⚙</span>
        <span className="wire-door-title">request a change</span>
        <Badge tone="wire">{title.length > 30 ? title.slice(0, 29) + '…' : title}</Badge>
      </div>

      {/* ASK — describe the change to the pointed element. The mint derives the scope from this address and
          computes the reach; the operator describes WHAT, the system computes HOW-FAR. */}
      {!minted && (
        <>
          <textarea className="wire-door-input" value={text} rows={2}
            placeholder={'describe the change to ' + (title) + '…'}
            disabled={busy}
            onChange={e => setText(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) { e.preventDefault(); request() } }} />
          <div className="wire-door-foot">
            {/* the honest INERT-BY-DEFAULT cue — static copy, not a live armed light (the armed state is not
                served to the FE). States the safe default plainly (no fiction). */}
            <span className="wire-door-inert" title="the wire is inert by default: minting + approving compose a PLAN; dispatch runs under read-only `plan` permission unless deliberately armed (a backend env-gate)">
              ◌ plan-mode · mints a plan for approval (inert by default)
            </span>
            <button type="button" className="wire-door-mint" disabled={!text.trim() || busy}
              title="mint a build-intent at the pointed address (⌘/Ctrl+Enter) — surfaces for approval, does not dispatch"
              onClick={request}>
              {busy ? 'minting…' : '⚙ mint build-intent'}
            </button>
          </div>
        </>
      )}

      {/* SEE THE REACH → APPROVE — the moment it is minted, show the X16 blast-radius ripple (the operator
          SEES what the change could reach) + the reach-approval (BlastRadiusReach, reused), then the approve
          gesture. The intent also lives in the Inbox builds lane; this is the door's immediate continuation. */}
      {minted && (
        <div className="wire-door-minted">
          <div className="wire-door-minted-head">
            <Badge tone="wire">minted</Badge>
            <span className="muted">build-intent at {title} — review the reach</span>
          </div>
          {/* the reach the operator approves — reuses the existing ripple + reach-approval (X16). A minted
              intent with no resolvable code scope shows the honest empty-reach state (DENY-ALL). */}
          {minted.payload?.blast_radius
            ? <BlastRadiusReach d={minted} onNavigate={resolveUiTarget} />
            : <div className="wire-door-noreach muted" title="this address resolves to no related code — the change reaches only the pointed address (DENY-ALL)">
                no resolvable code at this address — the change reaches only the pointed address (deny-all)
              </div>}
          <div className="wire-door-foot">
            <span className="wire-door-inert">◌ approving records your verdict — dispatch stays plan-mode (inert) until armed</span>
            {approved
              ? <Badge tone="sig">✓ approved — awaiting dispatch</Badge>
              : <button type="button" className="wire-door-approve" disabled={busy}
                  title="approve this build-intent — records your verdict; the watcher dispatches it (plan-mode by default), off this face"
                  onClick={approve}>
                  {busy ? 'approving…' : '✓ approve build'}
                </button>}
            <button type="button" className="wire-door-dismiss" onClick={dismiss}
              title="clear this minted intent from the door (it remains in the Inbox builds lane)">clear</button>
          </div>
          {err && <div className="wire-door-err" title="the verdict failed — fail loud, nothing dispatched">✕ {err}</div>}
        </div>
      )}
    </div>
  )
}
