// F0 (carved from App.tsx:1532–1562) · the grow region — teach a new node + the surfaced-for-approval
// review (operator approves; the brain never self-applies) + live node-types + last self-change revert.
// WAVE-4 COCKPIT-REGIONS — redesigned from prototype-grade (<h3> + dashed .surf block + inline-style live-
// types line) into the commander's-bridge language composed from the SHARED KIT (components/kit.tsx, H2): a
// kit SectionHead (display voice); the surfaced-for-approval review is now a kit <Surface> on the AWAIT tone
// (the operator sees "awaiting your verdict" by colour, the proposal reads as a card not a dashed scrap); the
// live node-types read as a kit lane of kind-toned chips (the registry truth, navigable, not a comma list);
// the last-self-change revert is a kit <Surface> footer (dim audit tone). PRESERVED (the bar): operator-only
// approval (approveApply goes through resolve+apply, operator-initiated — the brain never self-applies),
// every data-ui-ref (grow · grow/dispatch · grow/approve · grow/reject · workshop/self-changes), the reject
// path's resolve+capture-reason. Pure markup pass — no new state, no controller change.
import { api } from '../api'
import { SectionHead, LaneHead, Badge, Surface } from '../components/kit'
import { useApp } from '../AppContext'

export function Grow() {
  const {
    gname, gspec, surf, drill, reason, growMsg, types, lastChange,
    setGname, setGspec, setDrill, setReason, setSurf, setGrowMsg, dispatch, approveApply, revertLast, poll,
  } = useApp()
  return (
    <div data-ui-ref="ui://grow" className="grow">
      <SectionHead tag="teach a new node">grow</SectionHead>
      {/* the teach inputs — keep the shared .panel input vocabulary (still rendered here + by the inspector). */}
      <input placeholder="node name (e.g. wordcount)" value={gname} onChange={e => setGname(e.target.value)} />
      <input placeholder="what it should do" value={gspec} onChange={e => setGspec(e.target.value)} />
      <button className="b" data-ui-ref="ui://grow/dispatch" onClick={dispatch}>dispatch build →</button>

      {/* the build error, fail-loud as a kit Surface on the fail tone (read the failure by colour). */}
      {surf?.error && <Surface tone="fail" className="grow-err">{surf.error}</Surface>}

      {/* SURFACED FOR APPROVAL — the brain's proposal, awaiting the operator's verdict. A kit Surface on the
          AWAIT tone: the operator sees by colour that something needs a verdict, and the proposal reads as a
          card (the COA plain-language draft, optionally drilling to the raw code), with approve/reject. The
          approval is operator-initiated (resolve+apply) — the brain never self-applies (preserve-list). */}
      {surf && !surf.error && (
        <Surface tone="await" className="grow-surf" interactive>
          <div className="grow-surf-head">
            <Badge tone="await">awaiting your verdict</Badge>
            <span className="grow-surf-id mono">{surf.id}</span>
          </div>
          {surf.coa
            ? <>
                <div className="grow-coa">{surf.coa}</div>
                <button className="b ghost sm grow-drill" onClick={() => setDrill(d => !d)}>{drill ? '⌃ hide raw draft' : '⌄ drill to the raw draft'}</button>
                {drill && <pre>{surf.code}</pre>}
              </>
            : <pre>{surf.code}</pre>}
          <input className="grow-reason" placeholder="why? (captured into the trajectory)" value={reason}
            onChange={e => setReason(e.target.value)} />
          <div className="grow-verdicts">
            <button className="b" data-ui-ref="ui://grow/approve" onClick={approveApply}>✓ approve &amp; apply</button>
            <button className="b ghost" data-ui-ref="ui://grow/reject" onClick={() => { api.resolve(surf.id, 'reject', reason); setSurf(null); setReason(''); setGrowMsg('rejected — reason captured into the path.'); poll() }}>✕ reject</button>
          </div>
        </Surface>
      )}
      {!surf && growMsg && <div className="grow-msg muted">{growMsg}</div>}

      {/* the LIVE node-types — the registry truth, read as a kit lane of kind-toned chips (navigable, not a
          comma-separated run-on). The lane counts them; each chip is a Badge so the set reads at a glance. */}
      <div className="grow-types">
        <LaneHead tone="sig" count={types.length}>live node-types</LaneHead>
        <div className="grow-types-chips">
          {types.map(t => <Badge key={t} tone="dim">{t}</Badge>)}
        </div>
      </div>

      {/* the LAST self-change — the audit footer, a dim kit Surface with the bounded git-revert affordance. */}
      {lastChange?.sha && (
        <Surface tone="dim" className="grow-lastchange">
          <span className="grow-lc-label">last self-change</span>
          <span className="grow-lc-subj sig">{(lastChange.subject || '').replace('[self-apply] ', '')}</span>
          <button className="b ghost sm grow-revert" data-ui-ref="ui://workshop/self-changes" onClick={revertLast}
            title="git revert — bounded, recoverable">⟲ revert</button>
        </Surface>
      )}
    </div>
  )
}
