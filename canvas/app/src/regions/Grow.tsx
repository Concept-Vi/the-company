// F0 (carved from App.tsx:1532–1562) · the grow region — teach a new node + the surfaced-for-approval
// review (operator approves; the brain never self-applies) + live node-types + last self-change revert.
// PRESERVE-LIST: operator-only approval (approveApply goes through resolve+apply, operator-initiated).
import { api } from '../api'
import { useApp } from '../AppContext'

export function Grow() {
  const {
    gname, gspec, surf, drill, reason, growMsg, types, lastChange,
    setGname, setGspec, setDrill, setReason, setSurf, setGrowMsg, dispatch, approveApply, revertLast, poll,
  } = useApp()
  return (
    <>
      <h3 style={{ marginTop: 18 }}>grow · teach a new node</h3>
      <input placeholder="node name (e.g. wordcount)" value={gname} onChange={e => setGname(e.target.value)} />
      <input placeholder="what it should do" value={gspec} onChange={e => setGspec(e.target.value)} />
      <button className="b" onClick={dispatch}>dispatch build →</button>
      {surf?.error && <div className="err" style={{ marginTop: 8 }}>{surf.error}</div>}
      {surf && !surf.error && (
        <div className="surf">
          <div className="shd">⚠ surfaced for your approval · {surf.id}</div>
          {surf.coa
            ? <>
                <div className="coa">{surf.coa}</div>
                <button className="b ghost sm" onClick={() => setDrill(d => !d)}>{drill ? '⌃ hide raw draft' : '⌄ drill to the raw draft'}</button>
                {drill && <pre>{surf.code}</pre>}
              </>
            : <pre>{surf.code}</pre>}
          <input className="reason" placeholder="why? (captured into the trajectory)" value={reason}
            onChange={e => setReason(e.target.value)} />
          <button className="b" onClick={approveApply}>✓ approve &amp; apply</button>
          <button className="b ghost" onClick={() => { api.resolve(surf.id, 'reject', reason); setSurf(null); setReason(''); setGrowMsg('rejected — reason captured into the path.'); poll() }}>✕ reject</button>
        </div>
      )}
      {!surf && <div className="muted" style={{ marginTop: 8 }}>{growMsg}</div>}
      <div className="muted" style={{ marginTop: 12, borderTop: '1px solid var(--line)', paddingTop: 9 }}>
        live node-types ({types.length}): {types.map(t => <span key={t} className="tg">{t}</span>)}
      </div>
      {lastChange?.sha && (
        <div className="muted" style={{ marginTop: 8 }}>
          last self-change: <span className="sig">{(lastChange.subject || '').replace('[self-apply] ', '')}</span>
          <button className="b ghost sm" style={{ marginLeft: 8 }} onClick={revertLast} title="git revert — bounded, recoverable">⟲ revert</button>
        </div>
      )}
    </>
  )
}
