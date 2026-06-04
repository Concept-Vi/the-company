// F0 (carved from App.tsx:320–355) · the editable node inspector form. PRESERVE-LIST item 3: generic for
// EVERY node-type — fields come from the type's config_schema (the single source, via the registry store);
// values from the node's live config. enum/options → a <select> (model dropdowns fill from the live
// registry via options_from); everything else → an <input>. An edit commits through api.set (merge), then
// the parent refreshes. Wrapped by PanelErrorBoundary at the call site so a malformed schema degrades to a
// contained card. A new node-type gets a form with ZERO per-type code.
import { configSchemaToFields, coerceConfigValue } from '../api'
import { getOINFO } from '../registryStore'

export function NodeConfigForm({ nodeType, config, onSet }:
  { nodeType: string; config: any; onSet: (key: string, value: any) => void }) {
  const schema = getOINFO()[nodeType]?.config_schema || {}
  const fields = configSchemaToFields(schema)
  if (!fields.length) return <div className="muted">this node-type has no configurable fields.</div>
  return (
    <div className="cfg-form">
      {fields.map(f => {
        const cur = config && config[f.key] != null ? config[f.key] : f.default
        return (
          <div className="op-field" key={f.key}>
            <span className="op-label">{f.label}</span>
            {f.type === 'select'
              ? <select value={cur == null ? '' : String(cur)} onChange={e => onSet(f.key, coerceConfigValue(f, e.target.value))}>
                  {/* surface the current value even if it isn't in the live option list (fail-loud, no silent drop) */}
                  {cur != null && !f.options.includes(String(cur)) && <option value={String(cur)}>{String(cur)} (current)</option>}
                  {f.options.length === 0 && <option value="">(no registered options)</option>}
                  {f.options.map(o => <option key={o} value={o}>{o}</option>)}
                </select>
              : <input
                  type={f.rawType === 'number' ? 'number' : 'text'}
                  defaultValue={cur == null ? '' : String(cur)}
                  onBlur={e => onSet(f.key, coerceConfigValue(f, e.target.value))}
                  onKeyDown={e => { if (e.key === 'Enter') (e.target as HTMLInputElement).blur() }}
                />}
          </div>
        )
      })}
    </div>
  )
}
