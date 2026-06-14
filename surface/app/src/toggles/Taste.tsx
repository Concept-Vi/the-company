import { useState } from 'react'
import type { MotionFeel } from '../tokens/motion'
import { stamp } from '../lib/address'

// SLICE-ONLY SCAFFOLD (S4): Tim resolves the §8 taste calls by FLIPPING and watching, not by speccing.
// type + pigment set :root data-attributes (paper.css re-tints/re-types live); motion flips spring<->eased.
const TYPES = [
  { id: 'source', label: 'Source' },
  { id: 'crimson', label: 'Crimson' },
  { id: 'lora', label: 'Lora' },
]
const PIGMENTS = [
  { id: 'muted', label: 'Muted' },
  { id: 'soft', label: 'Soft' },
  { id: 'present', label: 'Present' },
]

export function Taste({
  feel,
  setFeel,
  compact,
}: {
  feel: MotionFeel
  setFeel: (f: MotionFeel) => void
  compact?: boolean
}) {
  const [type, setType] = useState('source')
  const [pigment, setPigment] = useState('soft')

  function applyType(id: string) {
    setType(id)
    document.documentElement.setAttribute('data-type', id)
  }
  function applyPigment(id: string) {
    setPigment(id)
    document.documentElement.setAttribute('data-pigment', id)
  }

  return (
    <div className={`taste ${compact ? 'taste--compact' : ''}`} {...stamp('ui://controls/taste')}>
      <ToggleRow label="Aa" options={TYPES} value={type} onPick={applyType} />
      <ToggleRow label="◑" options={PIGMENTS} value={pigment} onPick={applyPigment} />
      <ToggleRow
        label="↝"
        options={[
          { id: 'spring', label: 'Spring' },
          { id: 'eased', label: 'Eased' },
        ]}
        value={feel}
        onPick={(id) => setFeel(id as MotionFeel)}
      />
    </div>
  )
}

function ToggleRow({
  label,
  options,
  value,
  onPick,
}: {
  label: string
  options: { id: string; label: string }[]
  value: string
  onPick: (id: string) => void
}) {
  return (
    <div className="toggle-row">
      <span className="toggle-glyph" aria-hidden>{label}</span>
      <div className="toggle-pills">
        {options.map((o) => (
          <button
            key={o.id}
            className={`pill ${value === o.id ? 'pill--on' : ''}`}
            onClick={() => onPick(o.id)}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  )
}
