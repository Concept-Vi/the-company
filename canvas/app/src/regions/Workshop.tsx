// F0 (carved from App.tsx:1635–1642) · the workshop region — full-screen output viewer modal.
// data-ui-ref="workshop" preserved (the resolveUiTarget keystone opens it on demand for the `workshop` ref).
//
// WAVE-? REGION-BATCH-2 (FULL conversion, A1/H) — CLASS-B region: redesigned from prototype-grade (bare <h2>
// + <div className="full">) into the commander's-bridge language. There is no modal exemplar, so it ADOPTS
// the shared vocabulary: a kit SectionHead in the display voice (the node-type as title, the node-id as the
// kicker, the address as a dim Badge aside) + the full output read in a kit <Surface> well (sig tone — the
// resolved value). The STRUCTURAL chrome stays bespoke (it's layout, not look): .workshop's position:fixed/
// inset (the full-viewport modal) + the .close affordance. PRESERVED: data-ui-ref="workshop", the open/close
// (setWorkshop), the full output text.
import { SectionHead, Badge, Surface } from '../components/kit'
import { useApp } from '../AppContext'

export function Workshop() {
  const { workshop, setWorkshop } = useApp()
  if (!workshop) return null
  return (
    <div className="workshop" data-ui-ref="workshop">
      <span className="close" onClick={() => setWorkshop(null)} title="close">✕</span>
      {/* the HEAD — display-voice title (the node-type), the node-id as the kicker, the address as a dim Badge. */}
      <SectionHead tag={workshop.nodeId} aside={<Badge tone="dim">{workshop.address}</Badge>}>
        {workshop.nodeType}
      </SectionHead>
      {/* the full output — a kit Surface well (sig tone, the resolved value), in the display voice. */}
      <Surface tone="sig" className="ws-output"><div className="ws-full">{workshop.output}</div></Surface>
    </div>
  )
}
