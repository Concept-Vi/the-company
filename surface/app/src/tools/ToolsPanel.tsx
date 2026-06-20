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
  | { phase: 'gated' } // a non-safe-posture tool: the SERVER enforces the gate (#1b); the UI doesn't fire a write unbuilt
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

  // RUN — the GENERIC invoke door (fork's /api/tools/invoke, now LIVE; replaces the transitional corpus-only path).
  // POST {name, args} → the envelope {ok, tool, posture, result | error}; the tool's own output rides under `result`.
  // The RESULT CONTENT render stays DNA's tool-card archetype (gap 4) — we HOLD the result + show a HUMAN run-status
  // (a count when it's a list), never raw JSON, never a bespoke content render (from-DNA law). POSTURE: the SERVER
  // enforces the gate fail-closed; the UI additionally won't FIRE a non-safe (mutating/consent) tool without the
  // operator-token gate (#1b, not built) → it shows an honest 'gated', never a silent write. Verified live: corpus
  // op=query → result.ranked real hits.
  const doRun = async () => {
    if (!tool) return
    if (tool.posture && tool.posture !== 'safe') {
      setRun({ phase: 'gated' }) // needs the operator-token gate (#1b) — don't fire a write from the UI unbuilt
      return
    }
    setRun({ phase: 'running' })
    try {
      const r = await fetch('/api/tools/invoke', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: tool.name, args: values }),
      })
      const data = await r.json().catch(() => null)
      // fail loud (human): a transport error, or the engine's honest {ok:false}/{error} (e.g. a genuinely broken tool).
      if (!r.ok || !data || data.ok === false || data.error) {
        setRun({ phase: 'error', message: 'That didn’t run just now — try again in a moment.' })
        return
      }
      // the tool's output rides under `result`; HOLD it for DNA's tool-card (gap 4). Count when it's a list
      // (ranked/hits/results/items); else count=-1 → an honest "it ran, the view is being designed".
      const out = (data.result ?? {}) as Record<string, unknown>
      const list =
        (Array.isArray(out.ranked) && (out.ranked as unknown[])) ||
        (Array.isArray(out.hits) && (out.hits as unknown[])) ||
        (Array.isArray(out.results) && (out.results as unknown[])) ||
        (Array.isArray(out.items) && (out.items as unknown[])) ||
        (Array.isArray(data.result) && (data.result as unknown[])) ||
        null
      setRun({ phase: 'done', count: list ? list.length : -1, hits: list || [out] })
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
                  {run.phase === 'done' && run.count < 0 && (
                    <p className="tools-result-status">
                      Done. The clear view of what came back is being designed — it’ll show right here next.
                    </p>
                  )}
                  {run.phase === 'gated' && (
                    <p className="tools-result-pending">
                      This one makes a change, so it needs your sign-off — that’s coming with the approval step.
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
