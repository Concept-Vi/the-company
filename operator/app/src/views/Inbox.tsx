// INBOX — the I1 NEEDS-ME INBOX: GET /api/needs-me (runtime/needs_me.py) rendered as a card
// stack, one card per registered `inbox_sources/*` row folded in (decisions · surfaced ·
// obligations · board_requests). Each card: a source Badge, title, why (plain meaning), and its
// declared verb buttons — POSTing to the card's own door (src/lib/api.ts:actOnCard) WITH the
// X-Operator-Session header (minted once on app boot, App.tsx). A verb's result surfaces via the
// U6 Toast (window.CV_TOAST) — success removes the card locally (optimistic — a fresh GET would
// confirm, but the fold is cheap enough to just re-fetch); failure toasts loud and the card stays
// (never a silent no-op). Empty inbox = the designed "nothing needs you · N running" state —
// N = the live inbox-source count (`sources.length`), never a blank screen.
// LIVE REFRESH (I2): tails GET /api/stream from the live edge (the SAME EventSource + Last-Event-ID
// pattern as Arrival — gapless auto-reconnect), same as views/Arrival.tsx. ANY event debounce-refetches
// needs-me (~2s) — not just the board/decision kinds the fold cares about, because the bus's real kind
// vocabulary doesn't line up 1:1 with the source names (e.g. a decision resolving lands as kind
// `op.run`/`op:"decision.decided"`, not `kind:"decision.decided"` — verified against
// runtime/decision_registry.py + runtime/bridge.py:1673). Debouncing on the general pulse is honest
// about that and still isn't polling: nothing fires without a real event landing on the bus.
import { useCallback, useEffect, useRef, useState } from 'react'
import { ApiError, actOnCard, fetchNeedsMe, fetchNow, type InboxCard, type InboxVerb, type NeedsMe } from '../lib/api'
import { ds } from '../ds'
import { stamp } from '../lib/address'
import type React from 'react'

declare global {
  interface Window {
    CV_TOAST?: { show: (opts: { tone?: string; title?: React.ReactNode; message?: React.ReactNode }) => number }
  }
}

function toast(opts: { tone?: string; title?: React.ReactNode; message?: React.ReactNode }) {
  window.CV_TOAST?.show(opts)
}

export default function Inbox() {
  const { Card, Badge, Button, List, ListRow, ToastHost } = ds()
  const [data, setData] = useState<NeedsMe | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState<string | null>(null) // "<source>:<id>:<verb>" while a POST is in flight
  const debounceRef = useRef<number | null>(null)

  const load = useCallback(() => {
    fetchNeedsMe()
      .then((d) => {
        setData(d)
        setError(null)
      })
      .catch((e: unknown) => setError(e instanceof ApiError ? e.message : String(e)))
  }, [])

  useEffect(() => {
    load()
  }, [load])

  // THE LIVE TAIL (I2) — same EventSource + Last-Event-ID pattern as Arrival's pulse: read the
  // live edge once (GET /api/now), then tail /api/stream from there. The browser's own gapless
  // reconnect (Last-Event-ID) means we never poll — a dropped connection resumes exactly where
  // it left off, driven entirely by the bridge pushing real events, never a timer.
  useEffect(() => {
    let es: EventSource | null = null
    let alive = true
    fetchNow()
      .then((now) => {
        if (!alive) return
        const edge = now.last_event?.seq ?? -1
        es = new EventSource(`/api/stream?since=${edge}`)
        es.onmessage = () => {
          // debounce ~2s: a burst of events (a board fold, a decision resolving) collapses to
          // one refetch, never a refetch-per-event and never a setInterval anywhere.
          if (debounceRef.current !== null) window.clearTimeout(debounceRef.current)
          debounceRef.current = window.setTimeout(() => {
            debounceRef.current = null
            load()
          }, 2000)
        }
        es.onerror = () => {} // browser auto-reconnects with Last-Event-ID (gapless)
      })
      .catch(() => {}) // the live tail is an enhancement — needs-me still works from the initial GET if /api/now fails
    return () => {
      alive = false
      es?.close()
      if (debounceRef.current !== null) window.clearTimeout(debounceRef.current)
    }
  }, [load])

  const onVerb = useCallback(
    async (card: InboxCard, verb: InboxVerb) => {
      const key = `${card.source}:${card.id}:${verb.id}`
      setBusy(key)
      try {
        await actOnCard(card, verb)
        toast({ tone: 'success', title: verb.label, message: `${card.title} — done.` })
        // optimistic remove (a stale card outliving its own verb would mislead); a fresh GET
        // re-syncs truth (a source-side no-op — e.g. obligations' "Comment" — will resurface it,
        // which is correct: that verb honestly does not resolve the obligation).
        setData((d) => (d ? { ...d, cards: d.cards.filter((c) => !(c.source === card.source && c.id === card.id)) } : d))
        load()
      } catch (e: unknown) {
        toast({ tone: 'error', title: `${verb.label} failed`, message: e instanceof ApiError ? e.message : String(e) })
      } finally {
        setBusy(null)
      }
    },
    [load],
  )

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
  if (!data) {
    return (
      <div className="state-block">
        <div className="title">Reaching the bridge…</div>
        <div className="body">GET /api/needs-me</div>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s-6)', padding: 'var(--s-6)', maxWidth: 'var(--frame-desktop, 100%)' }}>
      <ToastHost />

      {data.errors.length > 0 ? (
        <Card variant="outline" title="Some sources didn't answer" sub="fail-soft — the rest of your inbox is still real">
          <List divided>
            {data.errors.map((e, i) => (
              <ListRow key={i} primary={e.source} secondary={e.error} />
            ))}
          </List>
        </Card>
      ) : null}

      {data.cards.length === 0 ? (
        <div className="state-block">
          <div className="glyph" aria-hidden="true">
            ✓
          </div>
          <div className="title">Nothing needs you</div>
          <div className="body">{data.sources.length} source{data.sources.length === 1 ? '' : 's'} running</div>
        </div>
      ) : (
        data.cards.map((card) => (
          <Card
            key={`${card.source}:${card.id}`}
            {...stamp(`ui://operator/inbox/card/${card.id}`)}
            title={card.title}
            sub={card.created || undefined}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-3)', marginBottom: 'var(--s-3)', flexWrap: 'wrap' }}>
              <Badge tone="comm">{card.source}</Badge>
              <span>{card.why}</span>
            </div>
            <div style={{ display: 'flex', gap: 'var(--s-3)', flexWrap: 'wrap' }}>
              {card.verbs.map((verb) => {
                const key = `${card.source}:${card.id}:${verb.id}`
                return (
                  <Button
                    key={verb.id}
                    variant={verb.id === 'reject' ? 'secondary' : 'primary'}
                    disabled={busy === key}
                    onClick={() => onVerb(card, verb)}
                  >
                    {busy === key ? '…' : verb.label}
                  </Button>
                )
              })}
            </div>
          </Card>
        ))
      )}
    </div>
  )
}
