import type { SurfaceState } from '../App'
import { Wheel } from '../wheel/Wheel'
import { Separator } from '../wheel/Separator'
import { Grid } from '../wheel/Grid'
import { Nucleation } from '../wheel/Nucleation'

// The wheel region with its three honest states: loading (calm), error (fail-loud), data.
// Never a faked/placeholder resting view — real data or an explicit state (no-silent-failures).
export function WheelOrState({ s }: { s: SurfaceState }) {
  if (s.error) {
    return (
      <div className="wheel-region wheel-state">
        <div className="state-card">
          <span className="display state-title">couldn’t reach the instrument</span>
          <code className="state-detail">{s.error}</code>
        </div>
      </div>
    )
  }
  if (s.loading || !s.proj) {
    return (
      <div className="wheel-region wheel-state">
        <div className="breathing" aria-label="loading" />
      </div>
    )
  }
  // The VIEW chooses the coordinate system (the seed's two systems over one space): square = the dyadic
  // STRUCTURE grid; circle = MEANING (the polar wheel / its lenses). Both share the address spine + disclosure.
  if (s.view === 'square') {
    return (
      <Grid proj={s.proj} feel={s.feel} selectedSeq={s.selected?.seq} onPick={(p) => s.setSelected(p)} />
    )
  }
  // Within the circle, the lens chooses its FORM (registry-true): the two-gravity separator is a two-basin
  // view; type-nucleation is the type-gravity view (types = divisions, points close around them); else the wheel.
  if (s.proj.binding.radius_from === 'separator') {
    return (
      <Separator
        proj={s.proj}
        feel={s.feel}
        selectedSeq={s.selected?.seq}
        onPick={(p) => s.setSelected(p)}
        polesDriven={!!(s.poles.a && s.poles.b)}
        onClearPoles={s.clearPoles}
      />
    )
  }
  if (s.proj.binding.radius_from === 'nucleation') {
    return (
      <Nucleation
        proj={s.proj}
        feel={s.feel}
        selectedSeq={s.selected?.seq}
        onPick={(p) => s.setSelected(p)}
        nuc={s.nuc}
        setNuc={s.setNuc}
      />
    )
  }
  return (
    <Wheel
      proj={s.proj}
      feel={s.feel}
      selectedSeq={s.selected?.seq}
      onPick={(p) => s.setSelected(p)}
      showGrid={s.view === 'both'}
      rung={s.rung}
      setRung={s.setRung}
    />
  )
}

// A calm, near-textless hint for the empty detail surface (so a strata/rail never reads as a void).
export function SelectHint() {
  return (
    <div className="select-hint" aria-hidden>
      <svg viewBox="0 0 48 48" className="select-hint-glyph">
        <circle cx="24" cy="24" r="18" fill="none" stroke="var(--ink-faint)" strokeWidth="1" opacity="0.5" />
        <circle cx="24" cy="24" r="10" fill="none" stroke="var(--ink-faint)" strokeWidth="1" opacity="0.5" />
        <circle cx="24" cy="24" r="2.4" fill="var(--ink-faint)" />
      </svg>
      <span className="select-hint-text">a point holds its context</span>
    </div>
  )
}
