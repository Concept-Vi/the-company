// F0 (carved from App.tsx:1383–1430) · the selected-node inspector. data-ui-ref="inspector" preserved.
// The right rail (.panel) is now the layout's `panel` grid-area, holding Inspector + Inbox + Grow stacked
// in one scroll column — same DOM structure as before (the rail was one .panel div). PRESERVE-LIST item 3:
// the generic registry-driven config form (NodeConfigForm). U1: inspector force uses `() => doRun([...])`.
import { PanelErrorBoundary } from '../components/PanelErrorBoundary'
import { NodeConfigForm } from '../components/NodeConfigForm'
import { useApp } from '../AppContext'

export function Inspector() {
  const { selected, configTick, configByNode, setWorkshop, doRun, surfaceOutput, buildFromOutput, setNodeConfig } = useApp()
  return (
    <>
      {selected ? (
        <>
          <h3>{selected.nodeType} · {selected.nodeId}</h3>
          <div className="row"><span className="k">kind</span><span>{selected.kind}</span></div>
          <div className="row">
            <span className="k">status</span>
            <span>
              {/* U2: stuck reads as a legible failure in the inspector too, not a bare word. */}
              {selected.status === 'cached' ? 'cached ↺'
                : selected.status === 'stuck' ? <span className="err">stuck — an input never resolved</span>
                : selected.status}
              {/* D4/D5: force this node past the memo cache, right from the inspector */}
              <button className="b ghost sm" style={{ marginLeft: 8 }} title="force re-run (bypass memo cache)"
                onClick={() => doRun([selected.nodeId])}>↻ force</button>
            </span>
          </div>
          <div className="row"><span className="k">address</span></div>
          <div className="muted" style={{ wordBreak: 'break-all' }}>{selected.address}</div>
          {/* A2/A4: editable config — generic form from config_schema + live config, contained by a boundary */}
          <div className="row" style={{ marginTop: 8 }}><span className="k">config</span></div>
          {/* configTick in the key forces a fresh mount after a write so the form shows merged values */}
          <div key={selected.nodeId + ':' + configTick}>
            <PanelErrorBoundary name={selected.nodeType + ' config'}>
              <NodeConfigForm
                nodeType={selected.nodeType}
                config={configByNode.current[selected.nodeId] || {}}
                onSet={(key, value) => setNodeConfig(selected.nodeId, key, value)} />
            </PanelErrorBoundary>
          </div>
          <div className="row" style={{ marginTop: 8 }}><span className="k">output</span></div>
          <pre>{selected.output || '— not yet resolved —'}</pre>
          {selected.output && (
            <div className="out-actions">
              <button className="b ghost" onClick={() => setWorkshop(selected)}>open workshop ⤢</button>
              {/* F3: rerun from the output (force past the memo gate) */}
              <button className="b ghost" title="force re-run this node (bypass the memo cache)"
                onClick={() => doRun([selected.nodeId])}>↻ rerun</button>
              {/* F2: route this result to the decision surface (inbox/COA) */}
              <button className="b ghost" title="surface this output as a decision in the inbox"
                onClick={() => surfaceOutput(selected.nodeId)}>→ inbox</button>
              {/* F3: build a new node from this output — prefills + reuses the grow→propose→approve chain */}
              <button className="b ghost" title="build a node from this output (edit + dispatch in grow)"
                onClick={() => buildFromOutput(selected.nodeId, selected.output)}>⊕ build from output</button>
            </div>
          )}
        </>
      ) : <div className="muted">select a node to inspect it. pan/zoom the canvas; zoom in for detail (semantic zoom).</div>}
    </>
  )
}
