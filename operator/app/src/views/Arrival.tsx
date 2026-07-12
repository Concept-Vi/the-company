// ARRIVAL — the first (thin) view: GET /api/greeting rendered with DS components
// (Card / List / Badge), plus a LIVE PULSE line tailing GET /api/stream (SSE,
// Last-Event-ID reconnect — the pattern harvested from surface/app/src/App.tsx:451-508).
// Everything visible is REAL bridge data; errors surface as a loud notice, never a blank.
import { useEffect, useRef, useState } from 'react'
import { ApiError, fetchGreeting, fetchNow, type Greeting } from '../lib/api'
import { ds } from '../ds'
// U6 chrome components landed AFTER the last _ds_bundle.js compile — imported AS SOURCE
// from the one DS home until the bundle is recompiled (tension noted in AGENTS.md; the
// CSS still comes only from the one /ds/styles.css chain).
import type React from 'react'
import { List as ListDS, ListRow as ListRowDS } from '../../../../design/claude-ds/components/List.jsx'
// The DS's .d.ts inheritance (React.HTMLAttributes) doesn't resolve from outside the DS
// dir (no node_modules there), which erases `children` — loosen locally, runtime unchanged.
const List = ListDS as unknown as React.ComponentType<Record<string, unknown>>
const ListRow = ListRowDS as unknown as React.ComponentType<Record<string, unknown>>

type Pulse = { count: number; lastSeq: number; lastKind: string; lastTs: string }

export default function Arrival() {
  const { Card, Badge } = ds()
  const [greeting, setGreeting] = useState<Greeting | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [pulse, setPulse] = useState<Pulse>({ count: 0, lastSeq: -1, lastKind: '', lastTs: '' })
  const lastSeqRef = useRef(-1)

  // the digest — one fetch, fail-loud into the notice
  useEffect(() => {
    let alive = true
    fetchGreeting()
      .then((g) => {
        if (alive) setGreeting(g)
      })
      .catch((e: unknown) => {
        if (alive) setError(e instanceof ApiError ? e.message : String(e))
      })
    return () => {
      alive = false
    }
  }, [])

  // THE LIVE PULSE (surface/app/src/App.tsx:451-508 pattern): read the live edge from
  // /api/now once, then tail /api/stream from there. EventSource auto-reconnects gaplessly
  // (the bridge stamps `id:` per event → the browser resends Last-Event-ID). ?channel= on
  // the app URL narrows to channel-stamped events only (the bridge's server-side filter).
  useEffect(() => {
    let es: EventSource | null = null
    let alive = true
    const chan = new URLSearchParams(window.location.search).get('channel')
    fetchNow()
      .then((now) => {
        if (!alive) return
        const edge = now.last_event?.seq ?? -1
        lastSeqRef.current = edge
        const qs = `since=${edge}${chan ? `&channel=${encodeURIComponent(chan)}` : ''}`
        es = new EventSource(`/api/stream?${qs}`)
        es.onmessage = (e) => {
          let ev: { seq?: number; kind?: string; ts?: string }
          try {
            ev = JSON.parse(e.data)
          } catch {
            return
          }
          if (typeof ev.seq !== 'number' || ev.seq <= lastSeqRef.current) return
          lastSeqRef.current = ev.seq
          setPulse((p) => ({
            count: p.count + 1,
            lastSeq: ev.seq as number,
            lastKind: ev.kind || '(unkinded)',
            lastTs: ev.ts || '',
          }))
        }
        es.onerror = () => {} // browser auto-reconnects with Last-Event-ID (gapless)
      })
      .catch((e: unknown) => {
        if (alive) setError(e instanceof ApiError ? e.message : String(e))
      })
    return () => {
      alive = false
      es?.close()
    }
  }, [])

  if (error) {
    return (
      <div className="state-block" role="alert">
        <div className="glyph" aria-hidden="true">
          ⚠
        </div>
        <div className="title">The bridge did not answer</div>
        <div className="body">{error}</div>
      </div>
    )
  }
  if (!greeting) {
    return (
      <div className="state-block">
        <div className="title">Reaching the bridge…</div>
        <div className="body">GET /api/greeting</div>
      </div>
    )
  }

  const chan = new URLSearchParams(window.location.search).get('channel')
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-6)', padding: 'var(--s-6)', maxWidth: 'var(--frame-desktop, 100%)' }}>
      {/* the live pulse line */}
      <Card pad="sm">
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-4)', flexWrap: 'wrap' }}>
          <Badge tone={pulse.count > 0 ? 'success' : undefined} dot>
            live
          </Badge>
          <span>
            {pulse.count} event{pulse.count === 1 ? '' : 's'} since arrival
            {chan ? ` on channel “${chan}”` : ''}
          </span>
          {pulse.lastSeq >= 0 ? (
            <span>
              — last: {pulse.lastKind} (#{pulse.lastSeq}
              {pulse.lastTs ? `, ${pulse.lastTs.slice(11, 19)}` : ''})
            </span>
          ) : (
            <span>— watching the stream</span>
          )}
        </div>
      </Card>

      {/* built while away — git-ground-truth headlines */}
      <Card
        title="Built while you were away"
        sub={greeting.since ? `since ${greeting.since.slice(0, 16).replace('T', ' ')}` : 'since the beginning'}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-3)', marginBottom: 'var(--s-3)' }}>
          <Badge tone="gold">{greeting.built_total}</Badge>
          <span>commits landed</span>
        </div>
        {greeting.built.length ? (
          <List divided>
            {greeting.built.map((b, i) => (
              <ListRow key={i} primary={b} />
            ))}
          </List>
        ) : (
          <div className="state-block">
            <div className="title">Nothing landed yet</div>
            <div className="body">No commits since your last contact.</div>
          </div>
        )}
      </Card>

      {/* waiting on the operator's gate */}
      <Card title="Waiting on you" sub="the gate — newest first">
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-3)', marginBottom: 'var(--s-3)' }}>
          <Badge tone={greeting.waiting_total > 0 ? 'warning' : 'success'}>{greeting.waiting_total}</Badge>
          <span>{greeting.waiting_total > 0 ? 'items need your decision' : 'nothing waits on you'}</span>
        </div>
        {greeting.waiting_on_you.length ? (
          <List divided>
            {greeting.waiting_on_you.map((w) => (
              <ListRow key={w.id || w.title} primary={w.title} secondary={w.id || undefined} />
            ))}
          </List>
        ) : null}
      </Card>

      {/* the now signal */}
      <Card title="Now">
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-3)', flexWrap: 'wrap' }}>
          <Badge tone="comm" dot>
            {String(greeting.now.mode || 'unknown')}
          </Badge>
          {greeting.now.presence ? <span>{String(greeting.now.presence)}</span> : null}
          {Object.entries(greeting.now.dials || {}).map(([k, v]) => (
            <Badge key={k}>{`${k}: ${v}`}</Badge>
          ))}
          {typeof greeting.now.surfaced_pending === 'number' ? (
            <span>{greeting.now.surfaced_pending} surfaced pending</span>
          ) : null}
        </div>
      </Card>

      {/* returned memories — only when a condition has actually fired */}
      {greeting.returned_memories.length ? (
        <Card title="Returned memories" sub="a return-condition came true">
          <List divided>
            {greeting.returned_memories.map((m, i) => (
              <ListRow key={i} primary={m.what_returns || m.memory || ''} secondary={m.fired_because} />
            ))}
          </List>
        </Card>
      ) : null}
    </div>
  )
}
