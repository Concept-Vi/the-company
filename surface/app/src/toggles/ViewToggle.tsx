import type { ViewMode } from '../App'
import { stamp } from '../lib/address'

// The seed's two coordinate systems over one space (§2): ○ = the CIRCLE (meaning — the polar wheel/lenses),
// ◻ = the SQUARE (structure — the dyadic grid). One quiet toggle; both are the same data, dual-read.
export function ViewToggle({ view, setView }: { view: ViewMode; setView: (v: ViewMode) => void }) {
  return (
    <div className="viewtoggle" {...stamp('ui://controls/view')}>
      <button
        className={`viewtoggle-btn ${view === 'circle' ? 'viewtoggle-btn--on' : ''}`}
        {...stamp('ui://controls/view/circle')}
        onClick={() => setView('circle')}
        aria-label="meaning (circle)"
        title="meaning — the circle"
      >
        ○
      </button>
      <button
        className={`viewtoggle-btn ${view === 'square' ? 'viewtoggle-btn--on' : ''}`}
        {...stamp('ui://controls/view/square')}
        onClick={() => setView('square')}
        aria-label="structure (square)"
        title="structure — the square grid"
      >
        ◻
      </button>
    </div>
  )
}
