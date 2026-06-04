// F0 (carved from App.tsx:1565–1579) · brain-authored DECLARATIVE panels + lazy ARBITRARY extensions.
// PRESERVE-LIST item 1: each panel + each extension is wrapped in a PanelErrorBoundary (a bad one degrades
// to a contained card, never a white-screen). Extensions are LAZY-loaded inside Suspense so even a
// module-scope throw is caught by the boundary.
import { lazy, Suspense } from 'react'
import { PanelErrorBoundary } from '../components/PanelErrorBoundary'
import { PanelView } from '../components/PanelView'
import { useApp } from '../AppContext'

// Self-coded extensions — brain-authored .tsx, build-gated before promotion. LAZY-loaded (not eager):
// React.lazy defers each module's evaluation to RENDER time, inside its PanelErrorBoundary.
const extensionLoaders = import.meta.glob('../extensions/*.tsx')   // path -> () => Promise<module> (lazy)
const extensions = Object.entries(extensionLoaders).map(([path, loader]) => ({
  name: (path.split('/').pop() || 'ext').replace('.tsx', ''),
  Comp: lazy(loader as () => Promise<{ default: any }>),
}))

export function OpPanels() {
  const { panels, fieldValue, setField } = useApp()
  return (
    <div className="hud op-panels">
      {panels.map(p => (
        <PanelErrorBoundary key={p.id} name={p.id}>
          <PanelView p={p} value={fieldValue} onSet={setField} />
        </PanelErrorBoundary>
      ))}
      {extensions.map(({ name, Comp }) => (
        <PanelErrorBoundary key={name} name={name}>
          <div className="op-panel op-ext">
            <div className="op-title">⌁ {name}</div>
            <Suspense fallback={<div className="muted">loading…</div>}><Comp /></Suspense>
          </div>
        </PanelErrorBoundary>
      ))}
    </div>
  )
}
