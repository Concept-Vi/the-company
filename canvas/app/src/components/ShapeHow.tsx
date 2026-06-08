// F1 ALTITUDE · THE IN-SYSTEM FEEDBACK AFFORDANCE — "shape how it presents to me, it remembers."
//
// WHAT THIS IS (this lane, f1-fe-surface): the VISIBLE half of the presentation-pref LEARNING LOOP (committed
// backend e1700b4). It is the recognition-by-sight control where the operator, AT a locus, RESHAPES how the
// system presents that thing to him — "show me this terser / more detail / lead with the change". It is the
// SIBLING of the annotate bar (comment at an address) + the wire door (request a change at an address),
// pointed at a third intent: "how you're shown this". Same point→ask shape, reused.
//
// THE FLOW (closes by USE): a chip (or an arg + chip) → onShape(kind, arg, text) → ctrl.setPresentationPrefAt
// → POST /api/presentation-pref (Suite.set_presentation_pref — the recorder, OFF the verb whitelist: a pref
// is a CONTROL signal, not an action) → re-fetch the address-help bundle → the AddressHelp panel above
// RE-RENDERS adapted (the learned marker appears; lead_with:change hoists the mechanism). It PERSISTS (the
// store leaf reads disk, survives reload). The voice/typing INPUT ("show me this differently") rides the
// existing chat path (/api/chat, untouched per G-8); this is the deterministic affordance that records it.
//
// THE FOUR KINDS (the PRESENTATION_PREFS vocabulary, suite.py:3674):
//   • terser    — fewer words, the essentials only            (BARE — no arg)
//   • more      — expand, the fuller picture                   (BARE — no arg)
//   • lead_with — put <arg> first (e.g. "the change")          (ARG-TAKING — a non-empty arg required)
//   • shape     — present as <arg> (the form Tim recognises)   (ARG-TAKING — a non-empty arg required)
// REGISTRY-IS-TRUTH CAVEAT (rule 8): PRESENTATION_PREFS is NOT exposed via /api/capabilities yet, so these
// four are mirrored here from the backend vocabulary. The backend re-validates the kind/arg + 400s on a
// mismatch (fail-loud), so a drift surfaces as a notice, never a silent wrong write. Flagged as an
// identified_gap (G-F1FE-CAP: expose presentation_prefs in capabilities so this reads from the registry).
//
// FORM (rule 9): built on the SHARED KIT (Surface / Badge / EmptyState) + var() tokens — design-lint clean,
// the commander's-bridge language. The chips read by SHAPE+TINT (a row of pills, the active one lit sig). It
// lives in the right-rail .panel column, so it inherits the ≤699px bottom-sheet (the 'panel' tab) for free —
// reachable thumb-first on phone. Operator-initiated, so no auto-raise (G-57 is for PUSHED offers, N/A here).
import { useState } from 'react'
import { Surface, Badge, EmptyState } from './kit'

// The bare (no-arg) kinds — a single click records them.
const BARE = [
  { kind: 'terser', label: 'terser', hint: 'fewer words, the essentials only' },
  { kind: 'more', label: 'more detail', hint: 'expand — the fuller picture' },
] as const
// The arg-taking kinds — a click ARMS a small input (the arg) before recording.
const ARG = [
  { kind: 'lead_with', label: 'lead with…', hint: 'put something first (e.g. "the change")', placeholder: 'e.g. the change' },
  { kind: 'shape', label: 'show as…', hint: 'the form you recognise it by', placeholder: 'e.g. a checklist' },
] as const

type Pref = { kind: string; arg?: string } | null

export function ShapeHow({ current, busy, onShape }:
  { current: Pref; busy: boolean; onShape: (kind: string, arg?: string, text?: string) => void }) {
  // which arg-taking kind is ARMED (its input shown), and the typed arg.
  const [armed, setArmed] = useState<string | null>(null)
  const [arg, setArg] = useState('')

  function fireBare(kind: string, hint: string) {
    if (busy) return
    // `text` = the human phrasing kept for the thread (single-source with the directive the model consumes).
    onShape(kind, undefined, hint)
  }
  function fireArg(kind: string) {
    if (busy) return
    const a = arg.trim()
    if (!a) return                                   // the controller + backend fail-loud; the UI just no-ops the empty submit
    onShape(kind, a, `${kind === 'lead_with' ? 'lead with' : 'show as'} ${a}`)
    setArmed(null); setArg('')
  }

  const activeKind = current?.kind

  // NO data-ui-ref: this affordance READS the indicated locus (via the controller), it must never BECOME it.
  // The document-level click-capture listener (useAppController) indicates the nearest [data-ui-ref] ancestor;
  // a ref here would re-indicate to the affordance on every chip click — overwriting the pointed target BEFORE
  // onShape reads it (the exact failure the chat-region + wire-door exclusions guard against). Carrying a ref
  // would ALSO orphan it (ui://inspector/shape-how isn't registered in the corpus — ui_registry_acceptance
  // would fail; same class as G-55). So the affordance is unaddressed by design — flagged as an identified_gap
  // (register ui://inspector/shape-how in a corpus lane → then it can carry the ref + be guidable, like D2's
  // ui://inspector/help did). The panel's OWN locus (ui://inspector/help) still rides the indicated element.
  return (
    <div className="ahelp-shape">
      <div className="ahelp-shape-head">
        <span className="ahelp-shape-title">shape how you're shown this</span>
        {busy && <Badge tone="await">shaping…</Badge>}
      </div>
      <div className="ahelp-shape-chips">
        {BARE.map(c => (
          <button key={c.kind} type="button" disabled={busy} title={c.hint}
            className={'ahelp-chip' + (activeKind === c.kind ? ' ahelp-chip-on' : '')}
            onClick={() => fireBare(c.kind, c.hint)}>
            {c.label}{activeKind === c.kind && <span className="ahelp-chip-star"> ✦</span>}
          </button>
        ))}
        {ARG.map(c => (
          <button key={c.kind} type="button" disabled={busy} title={c.hint}
            className={'ahelp-chip' + (activeKind === c.kind ? ' ahelp-chip-on' : '') + (armed === c.kind ? ' ahelp-chip-armed' : '')}
            onClick={() => { setArmed(v => v === c.kind ? null : c.kind); setArg('') }}>
            {c.label}{activeKind === c.kind && <span className="ahelp-chip-star"> ✦</span>}
          </button>
        ))}
      </div>

      {/* the ARG input — shown only when an arg-taking chip is armed. Enter or the ✓ records it. */}
      {armed && (
        <div className="ahelp-shape-arg">
          <input className="ahelp-shape-input" autoFocus value={arg} disabled={busy}
            placeholder={ARG.find(c => c.kind === armed)?.placeholder || 'a value…'}
            onChange={e => setArg(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') fireArg(armed); if (e.key === 'Escape') { setArmed(null); setArg('') } }} />
          <button type="button" className="ahelp-shape-go" disabled={busy || !arg.trim()} onClick={() => fireArg(armed)} title="record this shaping">✓</button>
        </div>
      )}

      {!armed && !current && (
        <EmptyState>tell the system how to present this — it remembers, and shows it this way from now on.</EmptyState>
      )}
    </div>
  )
}
