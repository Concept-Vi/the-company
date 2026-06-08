// F0 (carved from App.tsx:1383–1430) · the selected-node inspector. data-ui-ref="inspector" preserved.
// The right rail (.panel) is now the layout's `panel` grid-area, holding Inspector + Inbox + Grow stacked
// in one scroll column. WAVE-4 COCKPIT-REGIONS — the FORM redesigned to the commander's-bridge language: a
// kit SectionHead (display voice) replaces the bare <h3>; the status + kind read as kit Badges (state by
// colour, the status tint still driven by the served registry token, rule 3); the freshness verdict is a
// Badge; the output is a kit <Surface> well; the act-on-output buttons live in a clear footer. PRESERVED
// (the bar): the generic registry-driven NodeConfigForm (the DESIGNED config surface — NOT reworked), every
// data-ui-ref (inspector · freshness · act · workshop · surface · build), the L10 freshness derivation +
// fail-loud "unknown — <reason>", the F3 status-by-served-token logic, U1 force via () => doRun([...]). Pure
// markup pass — no controller change, no new state. The .row/.k/.panel pre vocabulary is KEPT (shared, still
// rendered here + by Grow/NodeConfigForm).
import { PanelErrorBoundary } from '../components/PanelErrorBoundary'
import { NodeConfigForm } from '../components/NodeConfigForm'
import { SectionHead, Badge, Surface, EmptyState } from '../components/kit'
import { useApp } from '../AppContext'

export function Inspector() {
  const { selected, nodeStates, configTick, configByNode, setWorkshop, doRun, surfaceOutput, buildFromOutput, setNodeConfig, freshness, freshnessBusy } = useApp()
  // L10 · "stale at this address" (§21.7#10): the DERIVED half of cached/stale, shown ALONGSIDE the served
  // `cached` badge below. The verdict is a COSTED DERIVATION (recompile + input-hash + _memo_sig compare;
  // seams-engine Seam 8a), fetched on-demand for THIS selected node (controller.fetchFreshness →
  // GET /api/stale-at). Fail-loud (rule 4): an unevaluable node reads "unknown — <reason>", NEVER a silent
  // "fresh". Only render the badge for the node it was derived FOR (guard a stale verdict from a prior pick).
  const fr = freshness && selected && freshness.address === selected.address ? freshness : null
  const staleBadge = freshnessBusy
    ? <Badge tone="dim">checking…</Badge>
    : fr
      ? (fr.unknown || fr.stale == null
          ? <span title={fr.reason || 'freshness could not be derived'}>
              <Badge tone="dim">{fr.volatile ? 'always re-derived' : 'unknown'}</Badge></span>
          : fr.stale
            ? <span data-ui-ref="ui://inspector/freshness"
                title="the cached result at this address is out of date vs its current inputs — rerun to refresh">
                <Badge tone="await">stale ⚠</Badge></span>
            : <span data-ui-ref="ui://inspector/freshness"
                title="the cached result at this address matches its current inputs">
                <Badge tone="sig">fresh ✓</Badge></span>)
      : null
  // F3: drive the inspector status BY SIGHT from the served registry (capabilities().node_states), same source
  // as the canvas card — no parallel hardcoded ternary. `def.label` is the word; `def.render.token` colours the
  // badge (the ONE source of status colour, rule 3). FAILED surfaces its error string (fail-loud, rule 4);
  // STUCK keeps its legible reason. The status badge wears the served token as its tone colour.
  const def = selected ? nodeStates[selected.status] : undefined
  const word = def?.label ? def.label.toLowerCase() : selected?.status
  // the registry token (e.g. var(--ok)/var(--fail)) drives the badge colour directly — keep the served token
  // as the SINGLE source of status colour (rule 3), expressed on the kit badge shape.
  const statusStyle: any = def?.render?.token ? { color: `var(${def.render.token})`, borderColor: `var(${def.render.token})` } : {}
  return (
    <>
      {selected ? (
        <>
          <SectionHead tag="inspecting · selected node">{selected.nodeType}</SectionHead>
          {/* identity + state read by sight: the node-id, the kind, and the status all as badges/cues. */}
          <div className="ins-state">
            <Badge tone="dim">{selected.kind}</Badge>
            {/* the status badge: the served registry token colours it (rule 3). FAILED/STUCK surface their
                reason as the title (fail-loud); the cached state shows the ↺ re-served cue. */}
            <span className="ins-status-badge" style={statusStyle}
              title={selected.status === 'failed' ? (selected.error || 'the node raised an error')
                : selected.status === 'stuck' ? 'an input never resolved' : selected.status}>
              {selected.status === 'failed' ? '✕ failed'
                : selected.status === 'stuck' ? 'stuck'
                  : selected.status === 'cached' ? `${word} ↺`
                    : word}
            </span>
            {/* L10 · the DERIVED freshness verdict beside the served status. */}
            {staleBadge}
            {/* D4/D5: force this node past the memo cache, right from the inspector header. */}
            <button className="b ghost sm ins-force" data-ui-ref="ui://inspector/act" title="force re-run (bypass memo cache)"
              onClick={() => doRun([selected.nodeId])}>↻ force</button>
          </div>
          {/* the failed/stuck reason, surfaced in full (fail-loud) — not hidden behind a title alone. */}
          {(selected.status === 'failed' || selected.status === 'stuck') && (
            <div className="ins-fail-reason">{selected.status === 'failed'
              ? (selected.error || 'the node raised an error')
              : 'stuck — an input never resolved'}</div>
          )}
          <div className="ins-meta">
            <span className="k">node-id</span><span className="mono">{selected.nodeId}</span>
          </div>
          <div className="ins-meta"><span className="k">address</span></div>
          <div className="ins-addr mono">{selected.address}</div>
          {/* A2/A4: editable config — generic form from config_schema + live config, contained by a boundary.
              The NodeConfigForm is the DESIGNED generic surface; left untouched (preserve-list item 3). */}
          <div className="ins-section-label"><span className="k">config</span></div>
          {/* configTick in the key forces a fresh mount after a write so the form shows merged values */}
          <div key={selected.nodeId + ':' + configTick}>
            <PanelErrorBoundary name={selected.nodeType + ' config'}>
              <NodeConfigForm
                nodeType={selected.nodeType}
                config={configByNode.current[selected.nodeId] || {}}
                onSet={(key, value) => setNodeConfig(selected.nodeId, key, value)} />
            </PanelErrorBoundary>
          </div>
          <div className="ins-section-label"><span className="k">output</span></div>
          {/* the output is a kit Surface well — a card, not a bare <pre> dump (recognition-by-sight). */}
          <Surface tone={selected.output ? 'sig' : 'dim'} className="ins-output">
            <pre>{selected.output || '— not yet resolved —'}</pre>
          </Surface>
          {selected.output && (
            <div className="out-actions">
              <button className="b ghost" data-ui-ref="ui://inspector/workshop" onClick={() => setWorkshop(selected)}>open workshop ⤢</button>
              {/* F3: rerun from the output (force past the memo gate) — same ENG-force locus as the status force */}
              <button className="b ghost" data-ui-ref="ui://inspector/act" title="force re-run this node (bypass the memo cache)"
                onClick={() => doRun([selected.nodeId])}>↻ rerun</button>
              {/* F2: route this result to the decision surface (inbox/COA) */}
              <button className="b ghost" data-ui-ref="ui://inspector/surface" title="surface this output as a decision in the inbox"
                onClick={() => surfaceOutput(selected.nodeId)}>→ inbox</button>
              {/* F3: build a new node from this output — prefills + reuses the grow→propose→approve chain */}
              <button className="b ghost" data-ui-ref="ui://inspector/build" title="build a node from this output (edit + dispatch in grow)"
                onClick={() => buildFromOutput(selected.nodeId, selected.output)}>⊕ build from output</button>
            </div>
          )}
        </>
      ) : <EmptyState>select a node to inspect it — pan/zoom the canvas; zoom in for detail (semantic zoom).</EmptyState>}
    </>
  )
}
