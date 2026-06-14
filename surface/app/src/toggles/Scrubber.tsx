import { stamp } from '../lib/address'

// G3 — THE TIME SCRUBBER. Slide the temporal centre into the past; the instrument projects only what existed
// by then (ts ≤ at). Range = [corpusStart, now]; the far right (now) is the live present. Pure read (?at=).
function fmt(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch {
    return iso
  }
}

export function Scrubber({
  at,
  setAt,
  corpusStart,
  now,
}: {
  at: string | null
  setAt: (t: string | null) => void
  corpusStart: string | null
  now: string | null
}) {
  if (!corpusStart || !now) return null
  const startMs = Date.parse(corpusStart)
  const nowMs = Date.parse(now)
  if (!(nowMs > startMs)) return null
  const curMs = at ? Date.parse(at) : nowMs
  const frac = Math.max(0, Math.min(1, (curMs - startMs) / (nowMs - startMs)))
  const onChange = (f: number) => {
    if (f >= 0.999) setAt(null) // snapped to the live present
    else setAt(new Date(startMs + f * (nowMs - startMs)).toISOString())
  }
  return (
    <div className={`scrubber ${at ? 'scrubber--past' : ''}`} {...stamp('ui://controls/scrubber')}>
      <span className="scrubber-glyph" aria-hidden>⏱</span>
      <input
        className="scrubber-range"
        type="range"
        name="scrubber"
        min={0}
        max={1}
        step={0.001}
        value={frac}
        onChange={(e) => onChange(Number(e.target.value))}
        aria-label="time scrubber"
      />
      <span className="scrubber-label">{at ? fmt(at) : 'now · live'}</span>
      {at && (
        <button className="scrubber-now" onClick={() => setAt(null)} title="return to the live present">now</button>
      )}
    </div>
  )
}
