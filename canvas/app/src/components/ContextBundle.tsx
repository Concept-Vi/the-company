// X5 · the SURFACED CONTEXT-BUNDLE view + X7 · the PIN affordance. Renders a build-intent's persisted
// `payload.context[]` — the NOTEBOOK the build will see at this locus: the bounded, deduped attached strata
// (comments/chats/history/versions) R2's _r2_gather + _r2_score_and_cap resolved AT MINT/APPROVE time
// (consent-time, X5 trust property — the SURFACED record == what the build's prompt composes; the build
// cannot resolve a different one later). Each item is {kind, address, ts, text, pinned}. The view is
// NAVIGABLE (click an item's address → resolveUiTarget drives the view to that locus, registry-validated,
// fail-loud) and each item carries the X7 pin control (api.pin → POST /api/pin, operator-only) so the
// operator can HOLD an item in the bounded R2 window (the dead `pinned` term's SET path).
//
// CONSENT-TIME NOTE: payload.context is a FROZEN snapshot persisted at mint (suite.py:3437). Suite.pin
// writes a pin overlay to the store for FUTURE gathers — it does NOT re-resolve this persisted bundle. So
// the pin state is reflected OPTIMISTICALLY here (mirror of BlastRadiusReach's `done` pattern); the held
// snapshot is unchanged. Pure presentation + the one operator action; built on the corpus design system
// (tokens only, no hardcoded colour). PanelErrorBoundary-wrapped at the call site. FORM = needs-tim.
import { useMemo, useState } from 'react'
import { api, relTime } from '../api'

// the strata kinds R2 gathers, each given a short legible glyph + label (the kind is read off the item,
// not invented — these are the {kind} values _r2_gather emits: annotation/comment, chat, history, version).
function kindFace(kind: string): { glyph: string; label: string } {
  const k = (kind || '').toLowerCase()
  if (k.includes('annot') || k.includes('comment')) return { glyph: '✎', label: 'comment' }
  if (k.includes('chat')) return { glyph: '❝', label: 'chat' }
  if (k.includes('version')) return { glyph: '⎘', label: 'version' }
  if (k.includes('hist')) return { glyph: '⟲', label: 'history' }
  if (k.includes('self') || k.includes('change')) return { glyph: '✱', label: 'change' }
  return { glyph: '•', label: k || 'item' }
}

export function ContextBundle({ d, onNavigate }: { d: any; onNavigate?: (address: string) => void }) {
  const p = d.payload || {}
  const items: any[] = Array.isArray(p.context) ? p.context : []
  // OPTIMISTIC pin overlay (keyed by item ts) — the consent-time snapshot is frozen, so we reflect the
  // pin/unpin act locally; the backend write affects FUTURE gathers, not this held bundle.
  const [pinOverlay, setPinOverlay] = useState<Record<string, boolean>>({})
  const [busyTs, setBusyTs] = useState<string | null>(null)
  const [err, setErr] = useState<string | null>(null)

  // the resolved bundle, NEWEST first (recency is R2's primary axis; the operator reads the freshest first).
  const sorted = useMemo(
    () => [...items].sort((a, b) => String(b.ts || '').localeCompare(String(a.ts || ''))),
    [items])
  const pinnedCount = sorted.filter(it => (pinOverlay[it.ts] ?? !!it.pinned)).length

  async function togglePin(it: any) {
    const ts = String(it.ts || '')
    const addr = String(it.address || '')
    if (!ts || !addr) {
      setErr('this item has no address/handle — cannot pin (fail loud, nothing changed)')   // fail loud
      return
    }
    const next = !(pinOverlay[ts] ?? !!it.pinned)
    setBusyTs(ts); setErr(null)
    try {
      const r = await api.pin(addr, ts, next)
      if ((r as any)?.error) { setErr((r as any).error); return }   // fail loud — no silent no-op
      setPinOverlay(o => ({ ...o, [ts]: next }))                    // optimistic — pin reflected locally
    } catch (e: any) {
      setErr(String(e?.message || e))
    } finally { setBusyTs(null) }
  }

  // EMPTY STATE: a locus with no attached strata mints an empty bundle — say so plainly, never an empty box.
  if (items.length === 0) {
    return (
      <div className="cb-bundle cb-empty" data-ui-ref="ui://inbox/context-bundle"
        title="the build will see no attached context at this locus — its notebook is empty">
        <div className="cb-head">context · what this build will see</div>
        <div className="cb-empty-note">no attached context at this locus — the build sees only the pointed address + its code relationships</div>
      </div>
    )
  }

  return (
    <div className="cb-bundle" data-ui-ref="ui://inbox/context-bundle" data-needs-tim="x5-context-bundle">
      <div className="cb-head">
        context <span className="muted">· what this build will see · {sorted.length} item(s){pinnedCount ? ` · ${pinnedCount} pinned` : ''}</span>
      </div>
      <div className="cb-list">
        {sorted.map((it, i) => {
          const ts = String(it.ts || '')
          const face = kindFace(it.kind)
          const isPinned = pinOverlay[ts] ?? !!it.pinned
          const busy = busyTs === ts
          return (
            <div key={ts || i} className={'cb-item' + (isPinned ? ' pinned' : '')}>
              <div className="cb-item-bar">
                <span className="cb-kind" title={'stratum: ' + face.label}>{face.glyph} {face.label}</span>
                {/* X7: the pin control — held in the bounded R2 window. Optimistic local reflect. The glyph
                    is a monospace-on-system mark (⊙ pinned / ○ unpinned), NOT a colour emoji, to sit on the
                    thin-glyph design language. data-ui-ref places the registered ui://inbox/context-pin. */}
                <button type="button" className={'cb-pin' + (isPinned ? ' on' : '')}
                  data-ui-ref="ui://inbox/context-pin"
                  disabled={busy}
                  title={isPinned ? 'pinned — held in the build’s context window; click to unpin'
                    : 'pin to HOLD this in the build’s bounded context window (survives the recency/proximity decay)'}
                  onClick={() => togglePin(it)}>
                  {busy ? '…' : isPinned ? '⊙ pinned' : '○ pin'}
                </button>
                <span className="cb-ts muted" title={ts}>{relTime(ts)}</span>
              </div>
              {/* NAVIGATION GUARD: resolveUiTarget's registry-validated + fail-loud path is for `ui://`
                  addresses ONLY. A context item's address can be `run://` (X6's ui://↔run:// bridge gathers
                  run://-keyed strata), which bypasses the ui:// gate into the camera path (mis-route). So
                  the address is only a live link when it is `ui://`; a non-ui:// address shows as a legible
                  static label (no wrong jump). */}
              {(() => {
                const navigable = typeof it.address === 'string' && it.address.startsWith('ui://')
                return (
                  <button type="button" className="cb-addr"
                    title={!it.address ? 'no address on this item'
                      : navigable ? ('go to ' + it.address)
                        : (it.address + ' (run:// locus — view-drive is a reserved design call)')}
                    disabled={!navigable}
                    onClick={() => navigable && onNavigate && onNavigate(it.address)}>
                    {it.address || '∅ no address'}
                  </button>
                )
              })()}
              {it.text && <div className="cb-text">{it.text}</div>}
            </div>
          )
        })}
      </div>
      {err && <div className="cb-err" title="the pin write failed — fail loud, nothing silently changed">✕ {err}</div>}
    </div>
  )
}
