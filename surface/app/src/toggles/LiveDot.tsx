import { stamp } from '../lib/address'

// The live indicator + freeze toggle (the seed §4 / mandate L9). A softly pulsing dot = the present is moving
// (new events stream in and the projection refreshes); tap to FREEZE (pause the stream) and tap to resume.
export function LiveDot({ live, setLive }: { live: boolean; setLive: (v: boolean) => void }) {
  return (
    <button
      className={`livedot ${live ? 'livedot--on' : 'livedot--off'}`}
      {...stamp('ui://controls/live')}
      onClick={() => setLive(!live)}
      aria-label={live ? 'live — tap to freeze' : 'frozen — tap to resume'}
      title={live ? 'live — the present is moving (tap to freeze)' : 'frozen (tap to resume the live stream)'}
    >
      <span className="livedot-dot" aria-hidden />
    </button>
  )
}
