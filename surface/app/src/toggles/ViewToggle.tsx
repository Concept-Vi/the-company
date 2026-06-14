import type { ViewMode } from '../App'
import { stamp } from '../lib/address'

// Three ways to read the seed's one space (Tim 2026-06-14): BOTH = the circle inscribed in the square (the
// heart — meaning + structure together), CIRCLE = isolate meaning, SQUARE = isolate structure. Glyphs are tiny
// inline SVGs so the "circle-in-square" relationship is unambiguous.
const MODES: { id: ViewMode; label: string; glyph: JSX.Element }[] = [
  {
    id: 'both',
    label: 'both — circle in square',
    glyph: (
      <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden>
        <rect x="2" y="2" width="12" height="12" fill="none" stroke="currentColor" strokeWidth="1.2" />
        <circle cx="8" cy="8" r="5.6" fill="none" stroke="currentColor" strokeWidth="1.2" />
      </svg>
    ),
  },
  {
    id: 'circle',
    label: 'circle — meaning',
    glyph: (
      <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden>
        <circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" strokeWidth="1.2" />
      </svg>
    ),
  },
  {
    id: 'square',
    label: 'square — structure',
    glyph: (
      <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden>
        <rect x="2" y="2" width="12" height="12" fill="none" stroke="currentColor" strokeWidth="1.2" />
      </svg>
    ),
  },
]

export function ViewToggle({ view, setView }: { view: ViewMode; setView: (v: ViewMode) => void }) {
  return (
    <div className="viewtoggle" {...stamp('ui://controls/view')}>
      {MODES.map((m) => (
        <button
          key={m.id}
          className={`viewtoggle-btn ${view === m.id ? 'viewtoggle-btn--on' : ''}`}
          {...stamp(`ui://controls/view/${m.id}`)}
          onClick={() => setView(m.id)}
          aria-label={m.label}
          title={m.label}
        >
          {m.glyph}
        </button>
      ))}
    </div>
  )
}
