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

// the run state — an honest little machine (idle → running → done|wired-pending|error). NO raw output ever.
type RunState =
  | { phase: 'idle' }
  | { phase: 'running' }
  | { phase: 'done'; count: number; hits: unknown[] } // hits HELD for DNA's tool-card render (gap 4); we show a human status
  | { phase: 'pending' } // an op/tool whose invoke isn't wired transitionally yet (honest, not faked)
  | { phase: 'error'; message: string }

export function ToolsPanel() {
  const { tools, loading, error, scaffold, open, selected } = useTools()
  const [values, setValues] = useState<Record<string, unknown>>({})
  const [run, setRun] = useState<RunState>({ phase: 'idle' })

  const tool = selected ? tools.find((t) => t.name === selected) || null : null

  // the Run guard (operator-law: never fire an incomplete form). The current op's required params (op-conditional)
  // that are still blank → Run is disabled + a gentle human hint names the first one.
  const curOp = tool?.opField ? String(values[tool.opField] ?? '') : ''
  const requiredNow = tool
    ? [...(tool.opRequired?.[curOp] || []), ...(tool.inputSchema.required || [])].filter((n) => n !== tool.opField)
    : []
  const missing = requiredNow.filter((n) => {
    const v = values[n]
    return v === undefined || v === null || String(v).trim() === ''
  })
  const firstMissingLabel = missing.length ? tool?.labels?.[missing[0]]?.label || missing[0] : ''
  const canRun = missing.length === 0

  // when the picked tool changes, seed its form from defaults + clear any prior run state.
  useEffect(() => {
    if (tool) setValues(defaultsFor(tool))
    setRun({ phase: 'idle' })
  }, [selected]) // eslint-disable-line react-hooks/exhaustive-deps

  // RUN. Transitional invoke (lead-sanctioned: build the loop against the EXISTING endpoint now, swap onto fork's
  // generic /api/tools/invoke when it lands). The prove-on-one — corpus op=query — maps to /api/corpus-query (the
  // semantic door; resolved by-use: /api/cognition/corpus GET is records-list, NOT op=query). READ posture = no
  // gate. The RESULT CONTENT render stays DNA's tool-card archetype (gap 4) — we hold the hits + show a HUMAN
  // run-status (count), never raw JSON, never a bespoke content render (from-DNA law).
  const doRun = async () => {
    if (!tool) return
    const op = tool.opField ? String(values[tool.opField] ?? '') : ''
    if (tool.name !== 'corpus' || op !== 'query') {
      setRun({ phase: 'pending' }) // other ops/tools ride fork's generic invoke door (not wired transitionally)
      return
    }
    setRun({ phase: 'running' })
    try {
      const p = new URLSearchParams()
      p.set('text', String(values.text ?? ''))
      if (values.space) p.set('space', String(values.space))
      if (values.k) p.set('k', String(values.k))
      const r = await fetch(`/api/corpus-query?${p.toString()}`)
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      const data = await r.json()
      const hits: unknown[] = Array.isArray(data.hits) ? data.hits : []
      setRun({ phase: 'done', count: hits.length, hits })
    } catch {
      setRun({ phase: 'error', message: 'That didn’t run just now — try again in a moment.' })
    }
  }

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
                {!canRun && firstMissingLabel && (
                  <p className="tools-run-hint">Fill in “{firstMissingLabel}” to run.</p>
                )}
                <button
                  className="tools-run"
                  onClick={doRun}
                  disabled={run.phase === 'running' || !canRun}
                >
                  {run.phase === 'running' ? 'Looking…' : 'Run ›'}
                </button>
              </div>
              {/* the RESULT region — the stable container DNA.renderArchetype(toolCard, result) will write into
                  (gap 4). The invoke is REAL (op=query → /api/corpus-query); we show a HUMAN run-status (count) and
                  HOLD the hits for DNA's tool-card render — never raw JSON, never a bespoke content render. */}
              {run.phase !== 'idle' && (
                <div className="tools-result" aria-live="polite">
                  {run.phase === 'running' && <p className="tools-result-pending">Looking…</p>}
                  {run.phase === 'done' && run.count > 0 && (
                    <p className="tools-result-status">
                      Found {run.count} {run.count === 1 ? 'thing' : 'things'}. The clear view of each is being
                      designed — it’ll show right here next.
                    </p>
                  )}
                  {run.phase === 'done' && run.count === 0 && (
                    <p className="tools-result-status">
                      Nothing matched — try another question, or a different area to look in.
                    </p>
                  )}
                  {run.phase === 'pending' && (
                    <p className="tools-result-pending">
                      Running this one connects next — it’ll come through the same door once that’s wired in.
                    </p>
                  )}
                  {run.phase === 'error' && <p className="tools-result-error">{run.message}</p>}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
