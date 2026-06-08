// F0 (carved from App.tsx:1373–1381) · the node-type palette region — chips from the registry (OINFO).
// WAVE-4 COCKPIT-REGIONS — redesigned from prototype-grade (<h3> + bare .pchip list) into a
// recognition-by-sight rack composed from the SHARED KIT (components/kit.tsx, H2), following the Inbox
// exemplar. The palette now reads at a glance: a kit SectionHead in the display voice, then the node-types
// GROUPED BY KIND into kit lanes (process · content) so the operator sees WHAT KIND a node is by the lane it
// sits in + its spine tint — not by reading a `kind` word on every row. Each type is a kit <Surface> card
// (actionable, lifts on hover) with a kind-coloured monogram, the type name, and a "＋ add" cue. The kind
// drives the tint (the design-system kind language: process=mint, content=blue), so the rack is navigable.
// PRESERVED (the bar — function untouched): data-ui-ref="ui://rail/palette" · addNode(t) on click · the
// registry source (oinfo from /object_info). Pure markup pass — no new state, no controller change.
import { SectionHead, LaneHead, Surface, EmptyState } from '../components/kit'
import { useApp } from '../AppContext'

// the two LIVE node kinds (design-system.css guard: only process + content are live; present/model are
// forward-provision, never rendered as a kind). Tone maps kind → the kit lane/spine colour: process reads on
// the signal/mint tone (it ACTS), content on the wire/blue tone (it HOLDS data) — the same kind language the
// canvas node-cards wear, so the palette and the board read as one vocabulary.
const KIND_TONE: Record<string, 'sig' | 'wire' | 'dim'> = { process: 'sig', content: 'wire' }
const KIND_LABEL: Record<string, string> = { process: 'process · acts', content: 'content · holds' }

export function Palette() {
  const { oinfo, addNode } = useApp()
  const types = Object.keys(oinfo).sort()

  // group the registry's node-types by their declared kind so the rack reads by lane (recognition-by-sight).
  // an unexpected/forward kind falls into a neutral "other" lane (fail-soft, never dropped, never mislabelled).
  const byKind: Record<string, string[]> = {}
  types.forEach(t => { const k = oinfo[t]?.kind || 'other'; (byKind[k] = byKind[k] || []).push(t) })
  // a stable lane order: the live kinds first (process, content), then any others.
  const kinds = Object.keys(byKind).sort((a, b) => {
    const order = (k: string) => (k === 'process' ? 0 : k === 'content' ? 1 : 2)
    return order(a) - order(b) || a.localeCompare(b)
  })

  return (
    <div className="hud palette" data-ui-ref="ui://rail/palette">
      <SectionHead tag="build blocks">palette</SectionHead>
      <div className="pal-hint">click a block to drop it on the board · select 2 + “wire” to connect</div>
      {kinds.map(kind => {
        const tone = KIND_TONE[kind] || 'dim'
        return (
          <div key={kind} className="pal-lane">
            <LaneHead tone={tone} count={byKind[kind].length}>{KIND_LABEL[kind] || kind}</LaneHead>
            {byKind[kind].map(t => (
              // each node-type is an actionable kit Surface card: a kind monogram + the type name + the add
              // cue. The Surface spine carries the kind tone, so the card's colour IS its kind (read by sight).
              <Surface key={t} tone={tone} onClick={() => addNode(t)} className="pal-chip"
                title={'add a ' + t + ' node (' + kind + ')'}>
                <span className={'pal-mono pal-mono-' + (KIND_TONE[kind] || 'dim')}>{t.slice(0, 2).toUpperCase()}</span>
                <span className="pal-name">{t}</span>
                <span className="pal-add">＋ add</span>
              </Surface>
            ))}
          </div>
        )
      })}
      {types.length === 0 && <EmptyState>no node-types in the registry yet — the palette fills from /object_info.</EmptyState>}
    </div>
  )
}
