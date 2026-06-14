import { stamp } from '../lib/address'

// G11 — the multi-scale rung ladder. Step the meaning-field between UNITS (every item) and coarser THEMES
// (WARD cluster centroids). Shows only where a scale pyramid exists (proj.scale.rungs). Pure read (?rung=).
export function RungLadder({
  rungs,
  rung,
  setRung,
}: {
  rungs: number[]
  rung: number | null
  setRung: (r: number | null) => void
}) {
  if (!rungs.length) return null
  return (
    <div className="rungladder" {...stamp('ui://controls/rung')}>
      <span className="rung-glyph" aria-hidden>⊟</span>
      <button className={`rung-step ${rung == null ? 'rung-step--on' : ''}`} onClick={() => setRung(null)}>units</button>
      {[...rungs].sort((a, b) => b - a).map((r) => (
        <button key={r} className={`rung-step ${rung === r ? 'rung-step--on' : ''}`} onClick={() => setRung(r)}>{r}</button>
      ))}
    </div>
  )
}
