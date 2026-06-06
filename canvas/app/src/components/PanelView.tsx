// F0 (carved from App.tsx:166–186) · a brain-authored declarative panel, rendered generically. Render-
// prone work lives HERE (inside a component) so a malformed definition throws during PanelView's render
// and is caught by the PanelErrorBoundary wrapping it — never the parent shell (which would white-screen).
export function PanelView({ p, value, onSet }: { p: any; value: (f: any) => string; onSet: (f: any, v: string) => void }) {
  return (
    <div className="op-panel">
      <div className="op-title">{p.title}</div>
      {(p.fields || []).map((f: any) => (
        <div className="op-field" key={f.key}>
          <span className="op-label">{f.label || f.target}</span>
          {f.type === 'select'
            ? <select value={value(f)} onChange={e => onSet(f, e.target.value)}>
                {(f.options || []).map((o: string) => <option key={o} value={o}>{o}</option>)}
              </select>
            : <input defaultValue={value(f)} onBlur={e => onSet(f, e.target.value)} />}
        </div>
      ))}
      {(!p.fields || !p.fields.length) && <div className="muted">no fields</div>}
    </div>
  )
}
