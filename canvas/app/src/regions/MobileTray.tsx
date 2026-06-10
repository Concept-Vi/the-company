// THE MOBILE TRAY (Tim's design, 2026-06-11): long-press points at things; the SELECTION raises this
// slim tray above the tabbar — chips of what's pointed + the VERBS. "Explain" is a verb, not a
// gesture (the resolution of the long-press conflict): point first, then ask what it is. "Change"
// is input + button ONLY (elegance by subtraction — the chips ARE the context, no narration).
// "Ask" hands the whole set to the builder sheet. The tray serves EVERY selection kind: chrome
// elements, canvas nodes (run://), forager circles (exchange://) — one selection model.
// FORM: kit/corpus vocabulary (.rhm-indicating chips, .b buttons); mobile-only by CSS.
import { useState } from 'react'
import { useApp } from '../AppContext'

export function MobileTray() {
  const { pointedSet, togglePointed, clearPointed, mintBuildIntent, setMobileTab } = useApp() as any
  const [verb, setVerb] = useState<null | 'explain' | 'change'>(null)
  const [explained, setExplained] = useState<{ addr: string, text: string }[]>([])
  const [changeText, setChangeText] = useState('')
  const [busy, setBusy] = useState(false)

  if (!pointedSet?.length) return null

  const explain = async () => {
    setVerb('explain'); setBusy(true); setExplained([])
    const out: { addr: string, text: string }[] = []
    for (const addr of pointedSet.slice(0, 6)) {
      try {
        const r = await fetch('/api/address-help?address=' + encodeURIComponent(addr)).then(x => x.json())
        const what = r?.what_this_is
        const t = (typeof what === 'string' ? what : what?.title || what?.represents || '') ||
                  (r?.how_to_use?.howto || '')
        out.push({ addr, text: String(t || 'no description recorded yet — that gap is itself a finding').slice(0, 220) })
      } catch { out.push({ addr, text: 'could not reach the registry (fail-loud)' }) }
    }
    setExplained(out); setBusy(false)
  }

  const ask = () => {
    // hand the set to the BUILDER sheet as its context block (replace-semantics; the panel listens)
    const block = `[Operator's pointed context — ${pointedSet.length} item${pointedSet.length === 1 ? '' : 's'} — CURRENT selection]\n` +
      pointedSet.map(a => `- ${a}`).join('\n')
    window.dispatchEvent(new CustomEvent('builder-context', { detail: { block } }))
    setMobileTab?.('builder')
  }

  const mint = async () => {
    const t = changeText.trim(); if (!t) return
    setBusy(true)
    const r = await mintBuildIntent(t)                     // mints at the last-pointed (the indicated locus)
    setBusy(false)
    if (r) { setChangeText(''); setVerb(null) }
  }

  return (
    <div className="mobile-tray" data-ui-ref="ui://tray">
      <div className="tray-chips">
        {pointedSet.map((a: string) => (
          <span key={a} className="rhm-indicating tray-chip" onClick={() => togglePointed(a)}
            title="tap to remove from the selection">
            <span className="ic">⌖</span><span className="ind-addr">{a.split('/').pop() || a}</span>
          </span>
        ))}
      </div>
      {verb === 'explain' && (
        <div className="tray-explain">
          {busy && <span className="muted">reading…</span>}
          {explained.map(e => <div key={e.addr} className="tray-exp-row"><b>{e.addr.split('/').pop()}</b> — {e.text}</div>)}
        </div>
      )}
      {verb === 'change' && (
        <div className="tray-change">
          <input value={changeText} placeholder="" autoFocus
            onChange={e => setChangeText(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') mint() }} />
          <button className="b" onClick={mint} disabled={busy || !changeText.trim()}>{busy ? '…' : '⚒'}</button>
        </div>
      )}
      <div className="tray-verbs">
        <button className="b ghost" onClick={() => verb === 'explain' ? setVerb(null) : explain()}>? explain</button>
        <button className="b ghost" onClick={ask}>💬 ask</button>
        <button className="b ghost" onClick={() => setVerb(v => v === 'change' ? null : 'change')}>⚒ change</button>
        <button className="b ghost" onClick={() => { clearPointed(); setVerb(null) }}>✕ clear</button>
      </div>
    </div>
  )
}
