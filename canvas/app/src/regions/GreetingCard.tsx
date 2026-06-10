// S2-FE (overnight) · THE GREETING — the system MEETS Tim when he arrives (morning bar #1).
// Presence is a CONSTRUCTION (Track-1): on arrival the surface assembles caught-up-in-one-glance
// from /api/greeting — the night's work as headlines (git ground truth), what waits on his gate,
// and any memory whose return-condition came true (rendered as what it is: the system remembering
// on its own). A persistent quiet pill ("● while you were away") lives by the toolbar; the card
// AUTO-OPENS when the away-gap exceeds AWAY_MS (localStorage last-visit marker) — meeting him in
// the morning without imposing during a working day.
// FORM: kit/corpus vocabulary only (.hud card, .kit-sechead spirit, .b buttons, token colors).
import { useEffect, useState } from 'react'

const VISIT_KEY = 'company-last-visit'
const AWAY_MS = 4 * 3600 * 1000                              // a real away (sleep/work), not a tab-switch
let bootedThisLoad = false                                   // StrictMode double-effect guard: the visit
                                                             // marker write is NOT idempotent (the second
                                                             // dev-mode run would see since=now → built 0)

type Greeting = {
  since: string | null
  built: string[]
  built_total: number
  waiting_on_you: { id: string, title: string }[]
  waiting_total: number
  now: { mode: string, dials: Record<string, string>, surfaced_pending: number }
  returned_memories: { memory: string, condition: string, fired_because: string, what_returns: string }[]
}

export function GreetingCard() {
  const [g, setG] = useState<Greeting | null>(null)
  const [open, setOpen] = useState(false)
  const [showAllBuilt, setShowAllBuilt] = useState(false)

  useEffect(() => {
    if (bootedThisLoad) return
    bootedThisLoad = true
    const last = Number(localStorage.getItem(VISIT_KEY) || 0)
    const away = Date.now() - last
    localStorage.setItem(VISIT_KEY, String(Date.now()))
    const since = last ? new Date(last).toISOString() : undefined
    fetch('/api/greeting' + (since ? `?since=${encodeURIComponent(since)}` : ''))
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (!data) return                                     // fail-loud is the pill staying absent; no fake card
        setG(data)
        if (away > AWAY_MS && (data.built_total > 0 || data.waiting_total > 0)) setOpen(true)
      })
      .catch(() => {})                                        // bridge down → no greeting; the rest of the shell stands
  }, [])

  if (!g) return null
  return (
    <>
      <button className="b ghost greeting-pill" data-ui-ref="ui://chrome/greeting"
        title="while you were away — what was built, what waits on you, what returned"
        onClick={() => setOpen(o => !o)}>● while you were away</button>
      {open && (
        <div className="hud greeting-card" data-ui-ref="ui://chrome/greeting-card">
          <div className="rhm-head">while you were away
            <span className="rhm-min" title="close" onClick={() => setOpen(false)}>✕</span>
          </div>
          <div className="greet-body">
            <div className="greet-line muted">
              {g.now.mode} mode · dials: {Object.entries(g.now.dials).map(([k, v]) => `${k}=${v}`).join(' · ')}
            </div>
            {g.returned_memories.length > 0 && (
              <div className="greet-sec greet-returned">
                <div className="greet-h">a memory returned on its own</div>
                {g.returned_memories.map((m, i) => (
                  <div key={i} className="greet-mem" title={m.fired_because}>
                    <div>{m.what_returns}</div>
                    <div className="muted">because: {m.condition}</div>
                  </div>
                ))}
              </div>
            )}
            <div className="greet-sec">
              <div className="greet-h">built ({g.built_total})</div>
              {(showAllBuilt ? g.built : g.built.slice(0, 6)).map((b, i) => (
                <div key={i} className="greet-item">· {b}</div>
              ))}
              {g.built.length > 6 && (
                <button className="b ghost" onClick={() => setShowAllBuilt(s => !s)}>
                  {showAllBuilt ? 'fewer' : `all ${g.built.length}`}</button>
              )}
            </div>
            <div className="greet-sec">
              <div className="greet-h">waiting on you ({g.waiting_total})</div>
              {g.waiting_on_you.slice(0, 6).map(w => (
                <div key={w.id} className="greet-item">· {w.title}</div>
              ))}
              {g.waiting_total > 6 && <div className="muted">…and {g.waiting_total - 6} more in the inbox</div>}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
