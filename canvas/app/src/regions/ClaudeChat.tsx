// S1 (overnight) · THE BUILDER SIDE-PANEL — a real Claude Code session embedded in the surface.
// Tim points at an element (the shared `indicated` locus — I1, the same chip semantics as the RHM
// chat) and talks to the BUILDER: it investigates the actual repo with the pointed-at address's
// context riding in, streams its activity live (tool lines = "what it's doing"; text = its words),
// and remembers the conversation across turns (--resume on the backend). SAFE BY CONSTRUCTION:
// plan-mode default backend-side; a wanted change goes through the WireRequest door (point → ask →
// see-reach → approve) — this panel never mutates anything itself.
//
// DIVISION OF LABOR (Track-1 round 4): Viv (RhmChat) is the ENTITY — speaks about the system from
// live state. This panel is the CONTRACTOR — investigates + describes changes. Two chats, one
// surface, the same indicated locus.
//
// FORM: kit/corpus vocabulary only (.hud card, .msg/.who/.txt log shape, .rhm-indicating chip,
// .b buttons) — zero literal colors. Self-contained state (the session is panel-local; the
// controller's `indicated` is the only shared read) + per-panel error boundary at the mount.
import { useRef, useState } from 'react'
import { useApp } from '../AppContext'
import { useForagerSelection } from '../ForagerShape'

type PanelMsg = { role: 'user' | 'builder' | 'act', text: string }

// FORAGER D1 · the SELECTION-SET BLOCK — the sculpted context handed to the builder. Bounded by
// construction: per-item head ≤400ch (server already caps the head at 400), total cap 6KB; the header
// says CURRENT selection because --resume compounds blocks across turns (replace-semantics in wording —
// the Synthesis' handoff rule).
const SET_BLOCK_CAP = 6144

export function ClaudeChat() {
  const { indicated, indicate, mintBuildIntent } = useApp()
  const [msgs, setMsgs] = useState<PanelMsg[]>([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [min, setMin] = useState(true)            // starts minimized — present, never imposing
  // D1 · the armed context set (the composed block riding the NEXT turn; one-shot — cleared once it rides)
  const [ctxBlock, setCtxBlock] = useState<string | null>(null)
  // the live multi-select of forager circles, read straight off the editor (the one selection truth —
  // a hook, not a window global; ClaudeChat mounts below <Tldraw> so useEditor reaches the instance)
  const foragerSel = useForagerSelection()
  const sessionRef = useRef<string | null>(null)
  const logRef = useRef<HTMLDivElement | null>(null)

  const push = (m: PanelMsg) => {
    setMsgs(prev => [...prev, m])
    queueMicrotask(() => { const el = logRef.current; if (el) el.scrollTop = el.scrollHeight })
  }

  // D1 · GIVE TO BUILDER — compose the selection-set block from the CURRENT forager multi-select and
  // arm it for the next turn. Per-item line: `- {address} ({kind},{session}): {head≤400}`; total cap
  // 6KB (items beyond the cap are counted honestly, never silently dropped). The header's
  // replace-wording is load-bearing: --resume compounds earlier blocks into history, so the builder is
  // told THIS set supersedes any earlier one.
  const giveToBuilder = () => {
    const items = foragerSel
    if (!items.length) return
    let block = `[Operator's selected context — ${items.length} item${items.length === 1 ? '' : 's'} — ` +
      `this is the CURRENT selection; it REPLACES any earlier selection block in this conversation]\n`
    let included = 0
    for (const s of items) {
      const line = `- ${s.props.address} (${s.props.kind || '?'},${s.props.session || '?'}): ` +
        `${(s.props.content_head || '').slice(0, 400)}\n`
      if (block.length + line.length > SET_BLOCK_CAP) break
      block += line; included++
    }
    if (included < items.length) block += `… (+${items.length - included} more selected item${items.length - included === 1 ? '' : 's'} beyond the 6KB cap)\n`
    setCtxBlock(block)
    push({ role: 'act', text: `context set armed — ${included}${included < items.length ? '/' + items.length : ''} selected circle${items.length === 1 ? '' : 's'} ride the next turn (current selection replaces earlier)` })
  }

  const send = async () => {
    const prompt = input.trim()
    if (!prompt || busy) return
    setInput(''); setBusy(true)
    push({ role: 'user', text: prompt })
    try {
      const r = await fetch('/api/claude/turn', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt, session_id: sessionRef.current, address: indicated || undefined,
          // D1 · ADDITIVE field — the armed forager selection-set block (absent = today's body exactly)
          context_block: ctxBlock || undefined,
        }),
      })
      if (!r.ok || !r.body) { push({ role: 'act', text: `the builder door answered ${r.status} — fail-loud, nothing swallowed` }); return }
      if (ctxBlock) setCtxBlock(null)             // one-shot: it rode in; kept on failure above for a resend
      const reader = r.body.getReader()
      const dec = new TextDecoder()
      let buf = ''
      let sawDone = false                                   // fail-loud: a stream that ends without a
                                                            // terminal event must ANNOUNCE itself (the
                                                            // bridge-restart-mid-turn lesson, 2026-06-11)
      for (;;) {
        const { done, value } = await reader.read()
        if (done) break
        buf += dec.decode(value, { stream: true })
        const lines = buf.split('\n'); buf = lines.pop() || ''
        for (const line of lines) {
          if (!line.trim()) continue
          let ev: any
          try { ev = JSON.parse(line) } catch { continue }
          if (ev.type === 'init' && ev.session_id) sessionRef.current = ev.session_id
          else if (ev.type === 'tool') push({ role: 'act', text: `${ev.name}${ev.detail ? ' · ' + ev.detail : ''}` })
          else if (ev.type === 'text' && ev.text) push({ role: 'builder', text: ev.text })
          else if (ev.type === 'error') { sawDone = true; push({ role: 'act', text: `error: ${ev.error}` }) }
          else if (ev.type === 'done') { sawDone = true; if (ev.is_error) push({ role: 'act', text: `turn failed: ${ev.result}` }) }
        }
      }
      if (!sawDone) push({ role: 'act', text: 'the turn ended without completing (backend interrupted?) — ask again' })
    } catch (e: any) {
      push({ role: 'act', text: `stream broke: ${e?.message || e}` })
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className={'hud rhm claude-panel' + (min ? ' min' : '')} data-ui-ref="ui://chat/builder">
      <div className="rhm-head">
        builder <span className="muted">· claude code{sessionRef.current ? ' · session live' : ''}</span>
        <span className="rhm-min" data-ui-ref="ui://chat/builder-minimize"
          title={min ? 'expand the builder' : 'minimize the builder'}
          onClick={() => setMin(m => !m)}>{min ? '▢' : '▁'}</span>
      </div>
      <div className="rhm-log" ref={logRef}>
        {msgs.length === 0 && <div className="muted">
          the builder — a real Claude Code session inside the surface. point at anything, then ask:
          "what is this?" · "why does it work that way?" · "I want this changed". it investigates the
          actual system and answers plainly; changes go through your approval, always.
        </div>}
        {msgs.map((m, i) => (
          <div key={i} className={'msg ' + (m.role === 'user' ? 'user' : 'assistant')}>
            <span className="who">{m.role === 'user' ? 'you' : m.role === 'builder' ? 'cc' : '⚙'}</span>
            <span className={'txt' + (m.role === 'act' ? ' muted' : '')}>{m.text}</span>
          </div>
        ))}
        {busy && <div className="msg assistant"><span className="who">cc</span><span className="txt muted">working…</span></div>}
      </div>
      {indicated && (
        <div className="rhm-indicating" title="the builder receives this element's context with your message">
          <span className="ic">⌖</span>
          <span className="ind-addr">{indicated}</span>
          <button className="ind-clear" onClick={() => indicate(null)} title="stop indicating">✕</button>
        </div>
      )}
      {/* FORAGER D1 · the SET CHIP (.rhm-indicating vocabulary — the same chip language as the locus
         above). Live multi-select of forager circles → "give to builder" composes + arms the bounded
         selection-set block; the armed state shows until the next turn carries it (✕ disarms). */}
      {(foragerSel.length > 0 || ctxBlock) && (
        <div className="rhm-indicating forager-set"
          title="the sculpted context set — selected forager circles handed to the builder on your next message">
          <span className="ic">⬡</span>
          {foragerSel.length > 0
            ? <button className="ind-give" data-ui-ref="ui://chat/builder-give-set" onClick={giveToBuilder}
                title="compose the selected circles into the next turn's context block (current selection replaces earlier)">
                {foragerSel.length} selected → give to builder
              </button>
            : <span className="ind-addr">context set armed — rides your next message</span>}
          {ctxBlock && <button className="ind-clear" onClick={() => setCtxBlock(null)} title="disarm the context set">✕</button>}
        </div>
      )}
      {/* S1-handoff · BUILD THIS — the seam from conversation to consequence: the builder's LAST
         description becomes a build-intent AT the pointed address (reuses ctrl.mintBuildIntent →
         /api/intent-at → the wire's existing review/approve gate; plan-mode dispatch unless armed).
         The panel never mutates anything itself — this button is the ONLY exit, and it exits into
         Tim's gate. Enabled only when there's a pointed element AND a builder description to carry. */}
      {(() => {
        const lastCc = [...msgs].reverse().find(m => m.role === 'builder')?.text
        return (indicated && lastCc) ? (
          <div className="rhm-mem">
            <button className="b ghost" data-ui-ref="ui://chat/builder-build-this"
              title="turn the builder's last description into a build-intent at the pointed element (goes to your approval, never builds directly)"
              onClick={async () => {
                const r = await mintBuildIntent(`[described by the builder panel] ${lastCc}`)
                if (r) push({ role: 'act', text: 'build-intent minted — it is in your inbox for review/approve' })
              }}>⚒ build this</button>
          </div>
        ) : null
      })()}
      <div className="rhm-input">
        <input placeholder="ask the builder — point at something first if it's about a thing"
          data-ui-ref="ui://chat/builder-input" value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') send() }} />
        <button className="b" data-ui-ref="ui://chat/builder-send" onClick={send} disabled={busy}>{busy ? '…' : '→'}</button>
      </div>
    </div>
  )
}
