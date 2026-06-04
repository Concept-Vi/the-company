// F0 (carved from App.tsx:239–318) · WIRE-UI · DEMONSTRATE-FIRST: the build-intent review card. The
// HEADLINE is the working outcome in plain language + a "▷ show me" that drives the canvas to demonstrate
// the built thing actually doing its thing (a new node placed + runnable). The changed-files list is
// SECONDARY/for-the-record — collapsed behind a disclosure, never the headline (the operator judges the
// OUTCOME, not edits). Scope/class/phase frame it; a surfaced-back build shows its actionable WHY. Clicking
// the head compiles it via coa() (same as any inbox item). Pure presentation: every field is read from the
// surfaced item; PanelErrorBoundary-wrapped at the call site. PRESERVE-LIST: demonstrate-first review.
import { useState } from 'react'
import { buildPhase, deriveOutcome } from '../api'

export function BuildIntentCard({ d, onOpen, onDemonstrate, liveTypes }:
  { d: any; onOpen: (id: string) => void; onDemonstrate: (nodeType: string) => void; liveTypes: string[] }) {
  const [showRecord, setShowRecord] = useState(false)
  const p = d.payload || {}
  const phase = buildPhase(d)
  const result = p.build_result
  const changed: string[] = (result?.changed_files) || p.overrun || []
  const outcome = deriveOutcome(d, liveTypes)
  return (
    <div className={'bi-card ' + phase.cls} data-ui-ref="ui://inbox/build-intent">
      <div className="bi-head" onClick={() => onOpen(d.id)} title="compile this decision to a value-choice ↗">
        <span className="bi-tag">⚙ build-intent</span>
        <span className={'bi-phase ' + phase.cls}>{phase.label}</span>
      </div>
      <div className="bi-meta">
        <span className="bi-class" title="declared consequence class — its governance posture decides whether it auto-runs or surfaces">
          {p.consequence_class || 'decision_build'}</span>
        <span className="bi-scope" title="the declared scope — paths a verified build is allowed to touch (empty = deny-all)">
          scope: {(p.scope && p.scope.length) ? p.scope.join(', ') : '∅ (deny-all)'}</span>
      </div>
      {/* the INTENT (what was asked) — shown for an awaiting/running build (no terminal phase yet). */}
      {(phase.cls === 'bi-inbox' || phase.cls === 'bi-running') && (p.spec || p.why) && <div className="bi-spec">{p.spec || p.why}</div>}
      {/* DEMONSTRATE-FIRST · gated on the backend LIFECYCLE PHASE, NOT the subprocess exit code. Only a
          CLOSED build (status==='implemented' → bi-done) headlines the working outcome + offers the "show
          me" demonstration. A build can have build_result.success===true and STILL be surfaced-back (a
          scope-overrun ran + changed files; a verify-fail-no-op) — those are NOT done. status===implemented
          is the backend's only closed-and-done signal (author-from-registry). */}
      {phase.cls === 'bi-done' && (
        <div className="bi-outcome">
          <div className="bi-outcome-head">✓ done — here is what you can now do</div>
          {outcome.line && <div className="bi-outcome-line">{outcome.line}</div>}
          {outcome.demoType && (
            <button className="b sm bi-demo" title={`place a ${outcome.demoType} node on the canvas and see it run`}
              onClick={() => onDemonstrate(outcome.demoType!)}>▷ show me “{outcome.demoType}” working</button>
          )}
        </div>
      )}
      {/* SURFACED BACK (bi-back: scope-overrun / verify-fail / crashed): lead with the plain-language
          reason it needs the operator, never a diff, never a demo. The `why` is the actionable reason and
          is ALWAYS present on a bi-back item (suite.py / resurface_crashed set it for fail/overrun/crash). */}
      {phase.cls === 'bi-back' && (
        <div className="bi-outcome bi-outcome-bad">
          <div className="bi-outcome-head bad">{p.overrun ? '⚠ the build went outside its declared scope — it needs you' : '✕ the build did not complete — it needs you'}</div>
          {p.why && <div className="bi-outcome-line">{p.why}</div>}
        </div>
      )}
      {/* SECONDARY / FOR-THE-RECORD: the changed-files list + raw summary, COLLAPSED by default. The
          operator never has to read edits to review; this is the audit trail, available on demand. */}
      {result && (changed.length > 0 || result.summary) && (
        <div className="bi-record">
          <div className="bi-record-toggle" onClick={() => setShowRecord(s => !s)}
            title="the technical record — changed files + the build's own log (for reference, not the review)">
            {showRecord ? '⌄' : '⌃'} for the record {p.overrun ? `· ⚠ ${changed.length} file(s) outside scope` : changed.length ? `· ${changed.length} file(s) changed` : ''}
          </div>
          {showRecord && (
            <>
              {changed.length > 0 && (
                <div className="bi-files">
                  {changed.map((f: string) => <div key={f} className={'bi-file' + (p.overrun ? ' over' : '')}>{f}</div>)}
                </div>
              )}
              {result.summary && <pre className="bi-summary">{result.summary}</pre>}
              {result.permission_mode && <div className="bi-perm" title="the claude -p permission mode this build ran under">ran under: {result.permission_mode}</div>}
            </>
          )}
        </div>
      )}
    </div>
  )
}
