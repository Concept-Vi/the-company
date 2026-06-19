import { useEffect, useState } from 'react'
import { useTools, closeTools, selectTool, loadTools, type ToolDescriptor } from './toolsStore'
import { SchemaForm } from './schemaForm'

// THE TOOL FACE PANEL — the pilot palette (Tim 2026-06-19: "click a tool, click the options, enter inputs, receive
// responses; no developer UI, no raw anything"). A focused modal (App-root sibling, like DecisionsInbox): the tool
// LIST → pick one → its human description + a friendly op-conditional form → Run. ONE store, fail-loud, on DNA
// tokens. Copy is AI-draft (plain operator words), marked for Tim's steer.
//
// ★ SCOPE THIS FIRE (front half): the LIST + the DESCRIPTION + the FORM are live + verifiable. RUN + the RESULT
// render are explicit PENDING SEAMS — the run door (fork's /api/tools/invoke, gap 3, or the resolved existing
// endpoint) and the result render (DNA's tool-card archetype via DNA.renderArchetype, gap 4) are not landed, so
// Run shows an HONEST pending state in the result region (never a fake result, never raw JSON). The result region
// IS the stable container the renderArchetype seam will write into.

function humanName(t: ToolDescriptor): string {
  return t.title || t.name.replace(/[_-]+/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

// seed the form values from the schema defaults so the form opens ready-to-run (not empty).
function defaultsFor(t: ToolDescriptor): Record<string, unknown> {
  const out: Record<string, unknown> = {}
  for (const [name, prop] of Object.entries(t.inputSchema.properties || {})) {
    if (prop.default !== undefined) out[name] = prop.default
    else if (Array.isArray(prop.enum) && prop.enum.length) out[name] = prop.enum[0]
  }
  return out
}

export function ToolsPanel() {
  const { tools, loading, error, scaffold, open, selected } = useTools()
  const [values, setValues] = useState<Record<string, unknown>>({})
  const [ran, setRan] = useState(false)

  const tool = selected ? tools.find((t) => t.name === selected) || null : null

  // when the picked tool changes, seed its form from defaults + clear any prior run state.
  useEffect(() => {
    if (tool) setValues(defaultsFor(tool))
    setRan(false)
  }, [selected]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (selected) selectTool(null)
        else closeTools()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, selected])

  const onChange = (name: string, value: unknown) => setValues((v) => ({ ...v, [name]: value }))

  return (
    <div className={`tools-overlay ${open ? 'tools-overlay--open' : ''}`} aria-hidden={!open}>
      <div className="tools-scrim" onClick={closeTools} />
      <div className="tools-panel" role="dialog" aria-label="Tools" aria-modal="true">
        <header className="tools-head">
          {selected ? (
            <button className="tools-back" onClick={() => selectTool(null)} aria-label="back to the tool list">
              ‹ All tools
            </button>
          ) : (
            <div className="tools-head-text">
              <h2 className="tools-title">Tools</h2>
              <p className="tools-sub">Pick a tool, set it up in plain words, and run it.</p>
            </div>
          )}
          <button className="tools-close" onClick={closeTools} aria-label="close">
            ✕
          </button>
        </header>

        <div className="tools-body">
          {error && (
            <p className="tools-msg tools-msg--error">
              {error} <button className="tools-retry" onClick={loadTools}>Try again</button>
            </p>
          )}

          {/* ---- the LIST ---- */}
          {!selected && !error && (
            <>
              {loading && tools.length === 0 && <p className="tools-msg">Looking…</p>}
              {tools.length > 0 && (
                <ul className="tools-list">
                  {tools.map((t) => (
                    <li key={t.name}>
                      <button className="tools-row" onClick={() => selectTool(t.name)}>
                        <span className="tools-row-main">
                          <span className="tools-row-name">{humanName(t)}</span>
                          <span className="tools-row-desc">{t.description}</span>
                        </span>
                        <span className="tools-row-go" aria-hidden="true">›</span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
              {scaffold && (
                <p className="tools-note">More tools are being wired up — this is the first one, live.</p>
              )}
            </>
          )}

          {/* ---- the DETAIL: description + friendly op-conditional form + run ---- */}
          {tool && (
            <div className="tools-detail">
              <h3 className="tools-detail-name">{humanName(tool)}</h3>
              <p className="tools-detail-desc">{tool.description}</p>
              <SchemaForm tool={tool} values={values} onChange={onChange} />
              <div className="tools-run-row">
                <button className="tools-run" onClick={() => setRan(true)}>Run ›</button>
              </div>
              {/* the RESULT region — the stable container DNA.renderArchetype(toolCard, result) will write into
                  (gap 4). Until the run door + the tool-card land, an HONEST pending state (never a fake/raw result). */}
              {ran && (
                <div className="tools-result" aria-live="polite">
                  <p className="tools-result-pending">
                    Running connects next — the result will appear here, shown clearly (not raw),
                    once running and its result view are wired in.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
