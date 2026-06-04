// F0 (carved from App.tsx:1635–1642) · the workshop region — full-screen output viewer modal.
// data-ui-ref="workshop" preserved (the resolveUiTarget keystone opens it on demand for the `workshop` ref).
import { useApp } from '../AppContext'

export function Workshop() {
  const { workshop, setWorkshop } = useApp()
  if (!workshop) return null
  return (
    <div className="workshop" data-ui-ref="workshop">
      <span className="close" onClick={() => setWorkshop(null)}>✕</span>
      <h2>{workshop.nodeType} · {workshop.nodeId}</h2>
      <div className="muted">{workshop.address}</div>
      <div className="full">{workshop.output}</div>
    </div>
  )
}
