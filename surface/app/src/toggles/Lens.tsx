import type { BindingRef } from '../lib/api'
import { stamp } from '../lib/address'

// The lens switcher — registry-true (reads bindings[] from the response, NEVER a hardcoded list).
// A new binding file on disk => a new pill here with zero edit (the universal-instrument property, L12).
export function Lens({
  bindings,
  current,
  onPick,
  compact,
}: {
  bindings: BindingRef[]
  current: string
  onPick: (id: string) => void
  compact?: boolean
}) {
  return (
    <div className={`lens ${compact ? 'lens--compact' : ''}`} {...stamp('ui://controls/lens')}>
      {bindings.map((b) => (
        <button
          key={b.id}
          {...stamp(`ui://controls/lens/${encodeURIComponent(b.id)}`)}
          className={`pill ${current === b.id ? 'pill--on' : ''}`}
          onClick={() => onPick(b.id)}
          title={b.label}
        >
          {b.label}
        </button>
      ))}
    </div>
  )
}
