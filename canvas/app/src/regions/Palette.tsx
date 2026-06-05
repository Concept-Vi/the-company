// F0 (carved from App.tsx:1373–1381) · the node-type palette region — chips from the registry (OINFO).
import { useApp } from '../AppContext'

export function Palette() {
  const { oinfo, addNode } = useApp()
  return (
    <div className="hud palette" data-ui-ref="ui://rail/palette">
      <h3>palette</h3>
      <div className="muted" style={{ marginBottom: 8 }}>click to add · select 2 + “wire”</div>
      {Object.keys(oinfo).sort().map(t => (
        <div key={t} className="pchip" onClick={() => addNode(t)}>
          <span>+ {t}</span><span className="pk">{oinfo[t]?.kind || ''}</span>
        </div>
      ))}
    </div>
  )
}
