import { type PointerEvent as RPE, useCallback, useEffect, useRef, useState } from 'react'
import { stamp } from '../lib/address'
import vIcon from './v-icon.svg'

// THE RIGHT-HAND-MAN (the 'V') — the RHM's persistent identity, on EVERY page (App mounts it once, a sibling to
// the layout + the gallery). Tim 2026-06-17: a draggable overlay in the bottom-right that fans its options out
// around the corner angle, in thumb reach, never taking over the screen; movable so you can read under it. AND
// the LOADABLE BRAIN: tapping "Ask" opens a panel where the operator TALKS to the right-hand-man (real Claude
// Code) about whatever the V is aimed at.
//
// SWAP SEAM (composition's V-corner-handle contract): the real V organism later renders into THIS container — we
// MEET AT THE DATA (no cross-repo code import). BRAIN SEAM (fork): forkVBrain.attach({panelEl, getAimAddress,
// getAimLabel}) — the V host (here) owns the AIM; fork owns the turn/stream/write at that aim. We meet at the aim.

// The six verbs the right-hand-man collects from the surface (composition's contract). `id` = the CONTRACT verb
// (machine, NEVER shown). `label`/`desc` = operator-facing DRAFT copy — TENTATIVE, for Tim/composition to ratify
// ("See the record" already ratified, thread t-1781703728). `live` = the action is WIRED on projection's side
// TODAY; a !live verb is in the contract but not yet operable — shown dimmed + "soon" so the operator is never
// misled into a dead-end (no green-paint / half-done-as-done). `drive` waits on Tim's verb-PLACEMENT steer + the
// dominant aim having a dial; `generate` (Make) is wildcard's gated keystone. The desc rides on title/aria-label
// (desktop hover tooltip + screen-reader); the soon-state is visible on every device.
// DISPLAY ORDER + descriptions RATIFIED by composition (the V-contract owner, thread t-1781706789): live-first,
// then a read→write arc — orient → understand → inquire → mark → adjust → create. The 4 live verbs lead (bottom
// of the fan = thumb-reach), the 2 soon verbs trail together (resolves the fresh-eyes "interleaved soon" finding).
const VERBS = [
  { id: 'navigate', label: 'Go to', desc: 'Re-centre the view on this', live: true },
  { id: 'open-source', label: 'See the record', desc: 'Open the full record behind this', live: true },
  { id: 'ask', label: 'Ask', desc: 'Ask the right-hand-man about this', live: true },
  { id: 'annotate', label: 'Note', desc: 'Leave a note here', live: true },
  { id: 'drive', label: 'Drive', desc: 'Adjust its settings', live: false },
  { id: 'generate', label: 'Make', desc: 'Create something from this', live: false },
] as const

// the V's default aim when the operator hasn't pointed it at anything — the surface itself (territory_label
// degrades this to a human noun; the brain composes whatever context it can). Never shown raw to the operator.
const SURFACE_AIM = 'ui://instrument/surface'

type Pos = { x: number; y: number } | null
type Drag = { id: number; ox: number; oy: number; sx: number; sy: number; moved: boolean }
type Brain = { ask: (p?: string) => unknown; direct: (i: unknown) => Promise<unknown[]>; aimChanged: () => void; destroy: () => void }

const POS_KEY = 'rhm.handle.pos'

export function RightHand() {
  const [open, setOpen] = useState(false) // the verb fan
  const [panelOpen, setPanelOpen] = useState(false) // the brain (Ask) panel
  const [noteOpen, setNoteOpen] = useState(false) // the Note (annotate) composer
  const [noteText, setNoteText] = useState('')
  const [noteStatus, setNoteStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')
  const [aimLabel, setAimLabel] = useState('this part of the surface') // human aim label, mirrored for the Note head
  const [aimMeaning, setAimMeaning] = useState<string | null>(null) // the aim's one-line meaning (sectors carry it)
  const [pos, setPos] = useState<Pos>(() => {
    try {
      const r = localStorage.getItem(POS_KEY)
      return r ? (JSON.parse(r) as Pos) : null
    } catch {
      return null
    }
  })
  const dragRef = useRef<Drag | null>(null)
  const elRef = useRef<HTMLDivElement>(null)
  const panelRef = useRef<HTMLDivElement>(null)
  const noteRef = useRef<HTMLDivElement>(null)
  const brainRef = useRef<Brain | null>(null)
  const closeTimer = useRef<number | null>(null) // pending "Noted ✓ → auto-close" timer (cleared on edit/close/unmount)
  const aimRef = useRef<string>(SURFACE_AIM) // the CURRENT aim address (read live by the brain)
  const labelRef = useRef<string>('this part of the surface') // the HUMAN aim label (never the raw address)

  // ── MOUNT THE BRAIN (fork's forkVBrain) into the panel, once ────────────────────────────────────────
  // The V host owns the aim (getAimAddress/getAimLabel); fork owns the turn/stream/write. Fail-soft if the
  // brain module isn't loaded (the panel still renders; talk just no-ops) — never crash the surface.
  useEffect(() => {
    const fv = (window as unknown as { forkVBrain?: { attach: (c: unknown) => Brain } }).forkVBrain
    if (!fv || !panelRef.current) return
    try {
      brainRef.current = fv.attach({
        panelEl: panelRef.current,
        getAimAddress: () => aimRef.current,
        getAimLabel: () => labelRef.current,
        placeholder: 'Ask about what you’re looking at…',
      })
    } catch {
      brainRef.current = null
    }
    return () => {
      try {
        brainRef.current?.destroy()
      } catch {
        /* already gone */
      }
      brainRef.current = null
    }
  }, [])

  // ── FOLLOW THE OPERATOR'S AIM ───────────────────────────────────────────────────────────────────────
  // The V's aim re-points wherever the operator points: a wheel-POINT pick (projection:select) OR a SECTOR
  // tap (projection:aim — its own event, because projection:select opens a content face and a synthetic
  // sector address would fail-loud there). The label drives both the brain ("Ask about: …") and the Note
  // composer head — operator-law: MEANING, never the raw address. A caller may hand us the label (sectors do,
  // because territory_label has no kind-meta); otherwise we resolve it from the bridge. Default = the surface.
  const setAim = useCallback((address: string | null | undefined, label?: string | null, meaning?: string | null) => {
    aimRef.current = address || SURFACE_AIM
    setAimMeaning(meaning ?? null) // sectors carry a one-line meaning; point-picks/surface clear it
    if (label) {
      labelRef.current = label
      setAimLabel(label)
      try {
        brainRef.current?.aimChanged()
      } catch {
        /* not mounted */
      }
      return
    }
    fetch(`/api/territory/label?address=${encodeURIComponent(aimRef.current)}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((j: { label?: string } | null) => {
        if (j?.label) {
          labelRef.current = j.label
          setAimLabel(j.label)
          try {
            brainRef.current?.aimChanged()
          } catch {
            /* not mounted */
          }
        }
      })
      .catch(() => {
        /* label is best-effort; the brain still talks/writes at the aim */
      })
  }, [])

  useEffect(() => {
    const onSelect = (e: Event) => {
      const d = (e as CustomEvent).detail as { address?: string; source?: string } | null
      setAim(d?.address || d?.source || SURFACE_AIM)
    }
    const onAim = (e: Event) => {
      const d = (e as CustomEvent).detail as { address?: string; label?: string | null; meaning?: string | null } | null
      setAim(d?.address || SURFACE_AIM, d?.label ?? undefined, d?.meaning ?? null)
    }
    window.addEventListener('projection:select', onSelect)
    window.addEventListener('projection:aim', onAim)
    return () => {
      window.removeEventListener('projection:select', onSelect)
      window.removeEventListener('projection:aim', onAim)
    }
  }, [setAim])

  const onPointerDown = useCallback((e: RPE<HTMLButtonElement>) => {
    const el = elRef.current
    if (!el) return
    const rect = el.getBoundingClientRect()
    dragRef.current = { id: e.pointerId, ox: e.clientX - rect.left, oy: e.clientY - rect.top, sx: e.clientX, sy: e.clientY, moved: false }
    try {
      e.currentTarget.setPointerCapture(e.pointerId)
    } catch {
      /* capture is best-effort — drag still tracks via the window-relative math */
    }
  }, [])

  const onPointerMove = useCallback((e: RPE<HTMLButtonElement>) => {
    const d = dragRef.current
    if (!d || d.id !== e.pointerId) return
    if (!d.moved && Math.hypot(e.clientX - d.sx, e.clientY - d.sy) > 4) d.moved = true
    if (!d.moved) return
    const el = elRef.current
    const size = el ? el.offsetWidth : 56
    const nx = Math.min(Math.max(0, e.clientX - d.ox), window.innerWidth - size)
    const ny = Math.min(Math.max(0, e.clientY - d.oy), window.innerHeight - size)
    setPos({ x: nx, y: ny })
    setOpen(false) // moving closes the fan
  }, [])

  const onPointerUp = useCallback((e: RPE<HTMLButtonElement>) => {
    const d = dragRef.current
    dragRef.current = null
    if (!d) return
    if (d.moved) {
      // persist the new resting place (it is always there → remember where the operator put it)
      setPos((p) => {
        if (p) {
          try {
            localStorage.setItem(POS_KEY, JSON.stringify(p))
          } catch {
            /* storage blocked — position still holds for the session */
          }
        }
        return p
      })
    } else {
      setOpen((o) => !o) // a tap (no drag) toggles the fan
    }
    e.currentTarget.releasePointerCapture?.(e.pointerId)
  }, [])

  // cancel any pending "Noted ✓ → auto-close" so a re-edit or re-open never closes the live composer
  const clearCloseTimer = useCallback(() => {
    if (closeTimer.current != null) {
      clearTimeout(closeTimer.current)
      closeTimer.current = null
    }
  }, [])

  const onVerb = useCallback(
    (id: string) => {
      if (id === 'ask') {
        // the WIRED verb: open the brain panel — talk to the right-hand-man about the current aim
        setOpen(false)
        setPanelOpen(true)
        return
      }
      if (id === 'annotate') {
        // the WIRED Note verb: open a composer → write a comment AT THE CURRENT AIM. The mark rides the
        // company's scheme-agnostic route-back (brain.direct → /api/territory/write → suite.mark), so a note
        // lands on whatever the V is pointed at (a tapped sector, else the surface). Reuse, no parallel POST.
        clearCloseTimer()
        setOpen(false)
        setNoteStatus('idle')
        setNoteOpen(true)
        return
      }
      // navigate/drive/open-source/generate → composition's UNIFIED `gallery:verb` envelope (the V-corner-handle
      // verb contract, verb-discriminated). ONE dispatch path: projection's surface handlers take
      // navigate/drive/open-source; wildcard's binder takes generate (the gated keystone). ask/annotate are the
      // V's own legs (handled above). The verb ids here are already composition's canonical ids. aim_address =
      // the V's live aim; payload is empty for these (the aim suffices, per the contract).
      window.dispatchEvent(
        new CustomEvent('gallery:verb', { detail: { verb: id, aim_address: aimRef.current, payload: {} } }),
      )
      setOpen(false)
    },
    [clearCloseTimer],
  )

  // SAVE A NOTE — route the comment back at the current aim via fork's brain.direct (writeDirections →
  // /api/territory/write → suite.mark). Success = every per-element result carries ok:true; anything else
  // (HTTP error → [null], network → [true]+gallery:write-error, brain not mounted) surfaces an error — no
  // silent no-op (no-silent-failures). Verified round-trip by curl before wiring (mark persists + reads back).
  const saveNote = useCallback(async () => {
    const text = noteText.trim()
    if (!text) return
    const brain = brainRef.current
    if (!brain) {
      setNoteStatus('error') // the brain module never mounted — fail loud, never pretend it saved
      return
    }
    setNoteStatus('saving')
    try {
      const r = await brain.direct({ type: 'comment', text })
      const ok = Array.isArray(r) && r.length > 0 && r.every((x) => !!x && (x as { ok?: boolean }).ok === true)
      if (ok) {
        setNoteStatus('saved')
        setNoteText('')
        // confirm, then close on its own — no lingering empty box + disabled Save (fresh-eyes dead-end).
        // the timer is cleared if the operator edits again or reopens (clearCloseTimer), so it can't close a live box.
        clearCloseTimer()
        closeTimer.current = window.setTimeout(() => {
          setNoteOpen(false)
          setNoteStatus('idle')
          closeTimer.current = null
        }, 1100)
      } else {
        setNoteStatus('error')
      }
    } catch {
      setNoteStatus('error')
    }
  }, [noteText, clearCloseTimer])

  // close the fan / panel / note composer on Escape or an outside press
  useEffect(() => {
    if (!open && !panelOpen && !noteOpen) return
    const closeAll = () => {
      clearCloseTimer()
      setOpen(false)
      setPanelOpen(false)
      setNoteOpen(false)
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeAll()
    }
    const onDown = (e: PointerEvent) => {
      const t = e.target as Node
      const inHandle = !!elRef.current?.contains(t)
      const inPanel = !!panelRef.current?.contains(t)
      const inNote = !!noteRef.current?.contains(t)
      if (!inHandle && !inPanel && !inNote) closeAll()
    }
    window.addEventListener('keydown', onKey)
    window.addEventListener('pointerdown', onDown, true)
    return () => {
      window.removeEventListener('keydown', onKey)
      window.removeEventListener('pointerdown', onDown, true)
    }
  }, [open, panelOpen, noteOpen, clearCloseTimer])

  // never leave a timer running past unmount (it would setState on a gone component)
  useEffect(() => () => clearCloseTimer(), [clearCloseTimer])

  // a route-back failure (network, or a non-2xx the brain core swallows) surfaces as a Note error — never a
  // silent success. Active only while the composer is open (it is the only writer here).
  useEffect(() => {
    if (!noteOpen) return
    const onErr = () => setNoteStatus('error')
    window.addEventListener('gallery:write-error', onErr)
    return () => window.removeEventListener('gallery:write-error', onErr)
  }, [noteOpen])

  const style = pos ? { left: `${pos.x}px`, top: `${pos.y}px`, right: 'auto', bottom: 'auto' } : undefined

  return (
    <>
      {/* a soft paper scrim so the open fan / brain panel / note composer reads as an overlay ABOVE the surface
          (legible over the chart), without a heavy modal takeover; a press anywhere on it closes them */}
      {(open || panelOpen || noteOpen) && (
        <div
          className="vhandle-scrim"
          onClick={() => {
            clearCloseTimer()
            setOpen(false)
            setPanelOpen(false)
            setNoteOpen(false)
          }}
        />
      )}

      {/* THE BRAIN PANEL — fork's forkVBrain renders `.v-brain` inside here; always in the DOM (so attach has a
          target), shown when panelOpen. The operator talks to the right-hand-man about the current aim. */}
      <div ref={panelRef} className="v-brain-panel" data-open={panelOpen} {...stamp('ui://rhm/brain')}>
        <button className="v-brain-close" type="button" aria-label="Close" onClick={() => setPanelOpen(false)}>
          ×
        </button>
      </div>

      {/* THE NOTE COMPOSER — the WIRED 'Note' verb. Leave a note ABOUT the current aim; it routes back through
          fork's brain.direct → /api/territory/write → suite.mark (the same engine the gallery uses, no parallel
          writer). The head names what it lands on in HUMAN terms (operator-law: meaning, never the address). */}
      {noteOpen && (
        <div ref={noteRef} className="v-note" data-status={noteStatus} {...stamp('ui://rhm/note')}>
          <button
            className="v-note-close"
            type="button"
            aria-label="Close"
            onClick={() => {
              clearCloseTimer()
              setNoteOpen(false)
            }}
          >
            ×
          </button>
          <div className="v-note-aim">Note about: {aimLabel}</div>
          {aimMeaning && <div className="v-note-meaning">{aimMeaning}</div>}
          <textarea
            className="v-note-input"
            rows={3}
            placeholder="Leave a note about this…"
            value={noteText}
            // biome-ignore lint/a11y/noAutofocus: a composer the operator just opened — focus is the intent
            autoFocus
            onChange={(e) => {
              setNoteText(e.target.value)
              clearCloseTimer() // typing again cancels a pending auto-close
              if (noteStatus !== 'idle') setNoteStatus('idle') // editing clears the last result
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                void saveNote() // Enter saves; Shift+Enter newlines
              }
            }}
          />
          <div className="v-note-foot">
            {noteStatus === 'saving' && <span className="v-note-msg" role="status">Saving…</span>}
            {noteStatus === 'saved' && <span className="v-note-msg" role="status">Noted ✓</span>}
            {noteStatus === 'error' && (
              <span className="v-note-msg v-note-msg--err" role="status">Couldn’t save — try again</span>
            )}
            <button
              className="v-note-save"
              type="button"
              disabled={noteStatus === 'saving' || !noteText.trim()}
              onClick={() => void saveNote()}
            >
              Save
            </button>
          </div>
        </div>
      )}

      <div ref={elRef} className="vhandle" data-open={open} style={style} {...stamp('ui://rhm/handle')}>
        {open && (
          <div className="vhandle-fan" role="menu" aria-label="Right-hand-man actions">
            {VERBS.map((v, i) => {
              // a thumb arc rising from the bottom-right corner: EVEN vertical spacing (no overlap), leaning
              // LEFT as it climbs (the "around the angle" curve). Pills RIGHT-edge anchored (translate(-100%,…)).
              const dy = -(44 + i * 38)
              const dx = -(28 + Math.round(104 * Math.sin((i / (VERBS.length - 1)) * (Math.PI / 2))))
              return (
                <button
                  key={v.id}
                  className={`vhandle-verb${v.live ? '' : ' vhandle-verb--soon'}`}
                  role="menuitem"
                  data-verb={v.id}
                  // the desc rides on title/aria-label — a desktop hover tooltip + the screen-reader name; the
                  // operator on touch reads the label + the visible "soon" state, and learns the live verbs by use.
                  title={v.live ? `${v.label} — ${v.desc}` : `${v.label} — ${v.desc} (coming soon)`}
                  aria-label={v.live ? `${v.label}. ${v.desc}` : `${v.label}. ${v.desc}. Coming soon.`}
                  style={{ transform: `translate(-100%, -50%) translate(${dx}px, ${dy}px)` }}
                  onClick={() => onVerb(v.id)}
                >
                  {v.label}
                  {!v.live && <span className="vhandle-verb-soon">soon</span>}
                </button>
              )
            })}
          </div>
        )}
        <button
          className="vhandle-icon"
          aria-label="Right-hand-man"
          aria-expanded={open}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
        >
          <img src={vIcon} alt="" draggable={false} />
        </button>
      </div>
    </>
  )
}
