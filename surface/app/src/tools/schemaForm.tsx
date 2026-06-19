import type { ToolDescriptor, JSONSchemaProp } from './toolsStore'

// THE OP-CONDITIONAL FORM ENGINE — a tool's JSON-Schema → a FRIENDLY form (operator-law: human labels, never the
// raw param name; no raw schema). GENERIC: it consumes any ToolDescriptor, so it serves all 66 tools off fork's
// /api/tools (gap 2) — corpus is just the prove-on-one that stress-tests it (15 params, op-conditional). The
// "op-conditional" part: when a tool declares an `opField` (a discriminator enum, e.g. corpus's `op`), the engine
// renders that selector FIRST and then shows ONLY the params relevant to the chosen op (descriptor.opParams) — so
// the operator sees "Your question" for a query, not the read/find params. No opParams → it shows all params
// (graceful fallback, so an un-enriched tool still renders). On DNA tokens only (paper.css) — no bespoke values.

// the human label + help for a param (descriptor.labels → schema title/description → the bare name as last resort).
function labelFor(tool: ToolDescriptor, name: string, prop: JSONSchemaProp): { label: string; help?: string } {
  const authored = tool.labels?.[name]
  if (authored) return authored
  return { label: prop.title || name, help: prop.description }
}

// which params to show for the current op (op-conditional) — else every param but the op selector itself.
function visibleParams(tool: ToolDescriptor, op: string | undefined): string[] {
  const all = Object.keys(tool.inputSchema.properties || {})
  const opField = tool.opField
  if (opField && op && tool.opParams && tool.opParams[op]) {
    // the op's own params (kept in the authored order), op selector excluded (it renders separately above)
    return tool.opParams[op].filter((p) => p !== opField && tool.inputSchema.properties[p])
  }
  return all.filter((p) => p !== opField)
}

const MULTILINE = /(^|_)(text|question|query|prompt|body|message|content)($|_)/i

function isRequired(tool: ToolDescriptor, name: string): boolean {
  return (tool.inputSchema.required || []).includes(name)
}

export function SchemaForm({
  tool,
  values,
  onChange,
}: {
  tool: ToolDescriptor
  values: Record<string, unknown>
  onChange: (name: string, value: unknown) => void
}) {
  const props = tool.inputSchema.properties || {}
  const opField = tool.opField
  const op = opField ? String(values[opField] ?? props[opField]?.default ?? props[opField]?.enum?.[0] ?? '') : undefined

  const renderField = (name: string) => {
    const prop = props[name]
    if (!prop) return null
    const { label, help } = labelFor(tool, name, prop)
    const required = isRequired(tool, name)
    const val = values[name] ?? prop.default ?? ''
    const id = `tf-${name}`
    let control
    if (Array.isArray(prop.enum)) {
      // a small enum → a friendly pill group (operator picks, doesn't type a code)
      control = (
        <div className="tf-pills" role="group" aria-labelledby={`${id}-l`}>
          {prop.enum.map((opt) => (
            <button
              key={opt}
              type="button"
              className={`tf-pill ${String(val) === opt ? 'tf-pill--on' : ''}`}
              aria-pressed={String(val) === opt}
              onClick={() => onChange(name, opt)}
            >
              {opt}
            </button>
          ))}
        </div>
      )
    } else if (prop.type === 'boolean') {
      control = (
        <button
          type="button"
          id={id}
          className={`tf-toggle ${val ? 'tf-toggle--on' : ''}`}
          role="switch"
          aria-checked={!!val}
          onClick={() => onChange(name, !val)}
        >
          <span className="tf-toggle-knob" aria-hidden="true" />
          <span className="tf-toggle-state">{val ? 'On' : 'Off'}</span>
        </button>
      )
    } else if (prop.type === 'integer' || prop.type === 'number') {
      control = (
        <input
          id={id}
          className="tf-input tf-input--num"
          type="number"
          value={val === '' ? '' : Number(val)}
          step={prop.type === 'integer' ? 1 : 'any'}
          onChange={(e) => onChange(name, e.target.value === '' ? '' : Number(e.target.value))}
        />
      )
    } else if (MULTILINE.test(name)) {
      control = (
        <textarea
          id={id}
          className="tf-input tf-textarea"
          rows={3}
          value={String(val)}
          onChange={(e) => onChange(name, e.target.value)}
        />
      )
    } else {
      control = (
        <input
          id={id}
          className="tf-input"
          type="text"
          value={String(val)}
          onChange={(e) => onChange(name, e.target.value)}
        />
      )
    }
    return (
      <div className="tf-field" key={name}>
        <label className="tf-label" id={`${id}-l`} htmlFor={id}>
          {label}
          {required && <span className="tf-req" aria-label="required"> ·</span>}
        </label>
        {help && <p className="tf-help">{help}</p>}
        {control}
      </div>
    )
  }

  return (
    <div className="tf-form">
      {/* the op selector first (friendly), if this tool is op-discriminated */}
      {opField && Array.isArray(props[opField]?.enum) && (
        <div className="tf-field tf-field--op">
          <label className="tf-label" id={`tf-${opField}-l`}>
            {labelFor(tool, opField, props[opField]).label}
          </label>
          {labelFor(tool, opField, props[opField]).help && (
            <p className="tf-help">{labelFor(tool, opField, props[opField]).help}</p>
          )}
          <div className="tf-pills" role="group" aria-labelledby={`tf-${opField}-l`}>
            {props[opField].enum!.map((opt) => (
              <button
                key={opt}
                type="button"
                className={`tf-pill ${op === opt ? 'tf-pill--on' : ''}`}
                aria-pressed={op === opt}
                onClick={() => onChange(opField, opt)}
              >
                {tool.opLabels?.[opt] || opt}
              </button>
            ))}
          </div>
        </div>
      )}
      {visibleParams(tool, op).map(renderField)}
    </div>
  )
}
