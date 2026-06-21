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

// THE THREE-QUESTION WALK (Phase 0's spine, Tim-approved): the RHM is the teacher that walks the operator
// through — but the brain's Ask panel starts BLANK, and a stranger doesn't know what to ask (the cold-stranger
// gap). So the panel offers the three questions as one-tap starters; tapping one asks the REAL brain about the
// CURRENT aim (it answers grounded on wherever the V is pointed — self-similar at every level). This is the
// proactive walk in its grounded seed form: the RHM offers the questions; the existing brain teaches the answer.
const STARTERS = ['What am I looking at?', 'What can I do here?', 'Where can I go from here?'] as const

type Pos = { x: number; y: number } | null
type Drag = { id: number; ox: number; oy: number; sx: number; sy: number; moved: boolean }
type Brain = { ask: (p?: string) => unknown; groundedAsk: (p?: string) => unknown; direct: (i: unknown) => Promise<unknown[]>; aimChanged: () => void; destroy: () => void }

const POS_KEY = 'rhm.handle.pos'
// FIRST-CONTACT GREETING — the RHM is "the always-present guide… the teacher that walks the operator through
// the surface" (commission 2026-06-17). The icon alone is MUTE: a cold stranger sees a gold V and can't know
// it's the right-hand-man, that it can teach them, or that "Ask" explains what they're looking at. So on first
// contact the V INTRODUCES itself once (gated by this flag), then never again. Copy is TENTATIVE draft (the AI
// supplies it; DNA owns the verbal face, Tim ratifies) — marked for steer, not final.
const GREETED_KEY = 'rhm.greeted'

export function RightHand({ binding }: { binding?: string }) {
  const [open, setOpen] = useState(false) // the verb fan
  const [moreOpen, setMoreOpen] = useState(false) // the not-yet-live ("soon") verbs, revealed on demand (composition-ratified: first contact = live only)
  const [greet, setGreet] = useState(false) // the one-time first-contact self-introduction
  const [aimedThing, setAimedThing] = useState(false) // false = the surface default (nothing picked) → the fan caption
  const [tourStep, setTourStep] = useState<number | null>(null) // the guided walk: 0/1/2 = stepping ①②③; null = not touring
  const [tourAnswering, setTourAnswering] = useState(false) // true while the current step's answer is still streaming
  const [panelOpen, setPanelOpen] = useState(false) // the brain (Ask) panel
  const [noteOpen, setNoteOpen] = useState(false) // the Note (annotate) composer
  const [noteText, setNoteText] = useState('')
  const [noteStatus, setNoteStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')
  const [aimLabel, setAimLabel] = useState('this part of the surface') // human aim label, mirrored for the Note head
  const [aimMeaning, setAimMeaning] = useState<string | null>(null) // the aim's one-line meaning (sectors carry it)
  const [aimAvailable, setAimAvailable] = useState(true) // false = a thing is aimed but unaddressable (activity event) → record-verbs honestly unavailable
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
  // the SURFACE-DEFAULT aim, carrying which projection VIEW is live as a fragment (`#binding=<id>`) — fork's
  // territory_prose grounds the brain on THAT view's registry meta (name/is/fills/why), so "what am I looking
  // at?" with nothing picked answers with the real on-screen view, not a thin generic placeholder. The format
  // (`#binding=<id>`) is the seam fork agreed to parse (thread t-1781769953). Held in a ref so the live
  // callbacks read the current view without re-binding listeners.
  const surfaceAimRef = useRef<string>(SURFACE_AIM)

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

  // each time the fan closes, collapse the "soon" reveal — so EVERY open starts at the clean live-only first
  // contact (composition's ratified call: the not-yet-built stays off the critical first impression).
  useEffect(() => {
    if (!open) setMoreOpen(false)
  }, [open])

  // closing the Ask panel ends any guided walk → reopening starts fresh (the normal starters), never mid-tour.
  useEffect(() => {
    if (!panelOpen) setTourStep(null)
  }, [panelOpen])

  // keep the surface-default aim carrying the LIVE view (which projection binding is up) so the brain grounds
  // "what am I looking at?" on the real on-screen view. When the V is currently AT the surface default (nothing
  // picked), update its live aim too, so the very next Ask grounds on the current view without a re-pick.
  useEffect(() => {
    const sa = `${SURFACE_AIM}#binding=${binding || 'raw'}`
    surfaceAimRef.current = sa
    if (!aimedThing) {
      aimRef.current = sa
      // refresh the HUMAN label to the LIVE view's name — territory_label now resolves the surface aim to the
      // active view ("What's happening" / "Meaning" / …, fork's grounding). So the brain panel reads "Ask about:
      // What's happening" + the Note head names the real view — consistent with the now-grounded answer (instead
      // of the generic "this part of the surface"). The fan caption stays "everything here" (it names the SCOPE).
      fetch(`/api/territory/label?address=${encodeURIComponent(sa)}`)
        .then((r) => (r.ok ? r.json() : null))
        .then((j: { label?: string } | null) => {
          if (j?.label) {
            labelRef.current = j.label
            setAimLabel(j.label)
          }
          try {
            brainRef.current?.aimChanged()
          } catch {
            /* not mounted */
          }
        })
        .catch(() => {
          try {
            brainRef.current?.aimChanged()
          } catch {
            /* best-effort */
          }
        })
    }
  }, [binding, aimedThing])

  // ── FIRST-CONTACT GREETING ──────────────────────────────────────────────────────────────────────────
  // On a brand-new operator (no greeted flag), the RHM introduces itself a beat after load — long enough that
  // the surface has settled so the bubble is noticed, not jarring. Shown ONCE; dismissed by "Got it", by Esc/
  // outside-press, or simply by the operator engaging the V (opening the fan = they found it → no need to tell).
  const dismissGreet = useCallback(() => {
    setGreet(false)
    try {
      localStorage.setItem(GREETED_KEY, '1')
    } catch {
      /* storage blocked — it just greets again next load; harmless */
    }
  }, [])
  useEffect(() => {
    let already = false
    try {
      already = localStorage.getItem(GREETED_KEY) === '1'
    } catch {
      /* storage blocked → treat as not-yet-greeted */
    }
    if (already) return
    const t = window.setTimeout(() => setGreet(true), 900)
    return () => clearTimeout(t)
  }, [])

  // PROACTIVE LEAD-IN — the RHM doesn't just OFFER the walk, it BEGINS it. "Show me around" (in the greeting)
  // retires the intro, opens the Ask panel, and asks the first of the three questions AT THE CURRENT AIM, so a
  // first-timer is immediately shown a grounded answer ("You're looking at…") without having to discover the
  // tap-V → tap-Ask → tap-a-question sequence. The remaining two questions wait as starters for them to continue.
  // This is the teacher starting to talk — the proactive seed of the walk. Uses the proven ask() path; fail-soft.
  // run ONE step of the guided walk: ask that question at the current aim + track when its answer finishes
  // streaming (so the "Next" control only appears once the operator has something to read). fail-soft.
  const runTourStep = useCallback((step: number) => {
    setTourStep(step)
    setTourAnswering(true)
    try {
      Promise.resolve(brainRef.current?.groundedAsk(STARTERS[step])).finally(() => setTourAnswering(false))
    } catch {
      setTourAnswering(false)
    }
  }, [])
  // "Show me around" — the RHM BEGINS the guided walk at ① (vs leaving the operator to find the next tap).
  const startTour = useCallback(() => {
    dismissGreet()
    setPanelOpen(true)
    runTourStep(0)
  }, [dismissGreet, runTourStep])
  // advance the walk to the next question, or finish (back to the normal panel) after the third.
  const tourNext = useCallback(() => {
    if (tourStep == null) return
    const next = tourStep + 1
    if (next >= STARTERS.length) setTourStep(null)
    else runTourStep(next)
  }, [tourStep, runTourStep])

  // ── FOLLOW THE OPERATOR'S AIM ───────────────────────────────────────────────────────────────────────
  // The V's aim re-points wherever the operator points: a wheel-POINT pick (projection:select) OR a SECTOR
  // tap (projection:aim — its own event, because projection:select opens a content face and a synthetic
  // sector address would fail-loud there). The label drives both the brain ("Ask about: …") and the Note
  // composer head — operator-law: MEANING, never the raw address. A caller may hand us the label (sectors do,
  // because territory_label has no kind-meta); otherwise we resolve it from the bridge. Default = the surface.
  const setAim = useCallback((address: string | null | undefined, label?: string | null, meaning?: string | null, available = true) => {
    // `available=false` = a THING is aimed but it has NO resolvable address (an activity event — ~28% of the
    // stream). The V must NOT silently retarget the surface (that wrote the operator's notes to the whole surface);
    // it aims at NOTHING writable and the record-verbs go honestly unavailable until the thing becomes addressable.
    aimRef.current = available ? (address || surfaceAimRef.current) : ''
    setAimAvailable(available)
    // is a SPECIFIC thing picked, or are we at the surface default (nothing pointed at)? The fan caption needs
    // this so it never says "this part of the surface" (jargon, and points at nothing) when the operator hasn't
    // picked anything — it says "everything here" + teaches the drill instead. (Compare the BASE, ignoring the
    // `#binding=<id>` fragment — any ui://instrument/surface[#…] is still the surface default.)
    setAimedThing(!(available && (!address || address.split('#')[0] === SURFACE_AIM)))
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
      const d = (e as CustomEvent).detail as { address?: string; source?: string; kind_name?: string | null; kind_meaning?: string | null } | null
      if (!d) {
        setAim(surfaceAimRef.current) // a genuine deselect → back to the surface (the live view; notable/askable)
        return
      }
      const addr = d.address || d.source
      if (addr) {
        setAim(addr) // an addressed thing → aim + resolve its rich label (unchanged)
        return
      }
      // a SELECTED but ADDRESSLESS thing (an activity event: create/run/op.run/agent_sessions/…). It has no
      // resolvable address, so the V can't open/note/re-centre it (the real fix = events becoming addressable,
      // routed to fork). Be HONEST: name the thing by its kind + mark it unavailable — NEVER the silent surface aim.
      setAim('', d.kind_name || 'this kind of thing', d.kind_meaning ?? null, false)
    }
    const onAim = (e: Event) => {
      const d = (e as CustomEvent).detail as { address?: string; label?: string | null; meaning?: string | null } | null
      setAim(d?.address || surfaceAimRef.current, d?.label ?? undefined, d?.meaning ?? null)
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
      if (greet) dismissGreet() // engaging the V = they found it; retire the one-time intro
    }
    // SYMMETRIC with onPointerDown's best-effort setPointerCapture: releasing is cleanup, and it THROWS
    // NotFoundError if nothing was captured (capture is best-effort → can silently fail; a pointercancel or
    // a synthetic pointer also leaves nothing to release). `?.` only guards the method being absent, not the
    // throw — so wrap it. (Caught by the cumulative regression smoke-test: an uncaught NotFoundError here.)
    try {
      e.currentTarget.releasePointerCapture?.(e.pointerId)
    } catch {
      /* nothing captured — release is best-effort cleanup, safe to skip */
    }
  }, [greet, dismissGreet])

  // cancel any pending "Noted ✓ → auto-close" so a re-edit or re-open never closes the live composer
  const clearCloseTimer = useCallback(() => {
    if (closeTimer.current != null) {
      clearTimeout(closeTimer.current)
      closeTimer.current = null
    }
  }, [])

  const onVerb = useCallback(
    (id: string) => {
      // a THING is aimed but it has no resolvable address (an activity event) → the V's own legs (Ask/Note) can't
      // act on it. Show the honest "can't act on this kind yet" card (the Note panel in unavailable mode), NEVER a
      // silent surface action (Note used to write the operator's comment to the whole surface). navigate/open-source
      // (gallery:verb → App) handle their own honest Notice. (Coming-soon = the real fix: events becoming addressable.)
      if ((id === 'ask' || id === 'annotate') && !aimAvailable) {
        clearCloseTimer()
        setOpen(false)
        setPanelOpen(false)
        setNoteStatus('idle')
        setNoteOpen(true)
        return
      }
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
    [clearCloseTimer, aimAvailable],
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

  // ── THE FAN LAYOUT — a thumb arc rising from the corner, leaning left as it climbs ("around the angle"). ──
  // FIRST CONTACT = the LIVE verbs only (each with its touch-visible description — composition's operator-
  // legibility law: descriptions VISIBLE ON TOUCH, never hover-only), capped by a "what's coming" toggle that
  // reveals the not-yet-live verbs (honestly SOON-labeled) — they're discoverable, never on the first impression
  // and never shown as working. Slots are taller for the 2-line live pills; the caption sits above the top item.
  // Pills are RIGHT-edge anchored (translate(-100%,…)); cumulative y so variable heights never overlap.
  const liveVerbs = VERBS.filter((v) => v.live)
  const soonVerbs = VERBS.filter((v) => !v.live)
  const fanSeq: Array<{ type: 'verb'; v: (typeof VERBS)[number] } | { type: 'toggle' }> = [
    ...liveVerbs.map((v) => ({ type: 'verb' as const, v })),
    { type: 'toggle' as const },
    ...(moreOpen ? soonVerbs.map((v) => ({ type: 'verb' as const, v })) : []),
  ]
  let _fanY = 40 // gap from the icon centre to the bottom of the first slot
  const fanItems = fanSeq.map((it) => {
    const tall = it.type === 'verb' && it.v.live // live pills carry a description → taller slot
    const slot = tall ? 58 : 40
    const center = _fanY + slot / 2
    _fanY += slot + 6 // a breath between slots
    return { it, dy: -center, dx: -(22 + Math.round((center - 28) * 0.24)) }
  })
  const _capCenter = _fanY + 28 // the aim caption sits above the top item
  const fanCap = { dy: -_capCenter, dx: -(22 + Math.round((_capCenter - 28) * 0.24)) }

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
        {/* THE THREE-QUESTION STARTERS — the proactive walk's seed. Rendered in projection's wrapper ABOVE fork's
            appended `.v-brain` (a stable React subtree React owns; fork's brain node trails it, untouched). Tapping
            a starter asks the REAL brain (forkVBrain.ask) about the current aim → it answers in the reply slot.
            A stranger no longer faces a blank "what do I ask?" — the RHM offers the three questions to walk. */}
        {tourStep != null ? (
          // GUIDED WALK — the RHM leads through ①②③ in sequence (vs leaving the starters for the operator to find).
          // The current question's answer streams in fork's reply below; "Next" appears once it's done, so they
          // read before advancing. This is the faithful "the teacher walks you through" (commission), operator-paced.
          <div className="v-brain-tour" role="group" aria-label="Guided walk">
            <div className="v-brain-tour-step">Step {tourStep + 1} of {STARTERS.length}</div>
            <div className="v-brain-tour-q">{STARTERS[tourStep]}</div>
            {!tourAnswering &&
              (tourStep < STARTERS.length - 1 ? (
                <button className="v-brain-tour-next" type="button" onClick={tourNext}>
                  Next — {STARTERS[tourStep + 1]} →
                </button>
              ) : (
                // the final step CLOSES the panel (the panel-close effect ends the tour) → the operator is handed
                // back to the surface to explore, matching what the button says (the fresh-eyes caught the old
                // version only swapping back to the starters — a broken promise between the label and the behaviour).
                <button className="v-brain-tour-next" type="button" onClick={() => setPanelOpen(false)}>
                  That’s the tour — I’ll explore →
                </button>
              ))}
          </div>
        ) : (
          // THE THREE-QUESTION STARTERS — the reactive seed (tap any one). Rendered in projection's wrapper ABOVE
          // fork's appended `.v-brain` (a stable React subtree; fork's brain node trails it, untouched). A stranger
          // never faces a blank "what do I ask?" — the RHM offers the three questions to walk on their own.
          <div className="v-brain-starters" role="group" aria-label="Questions to get started">
            <div className="v-brain-starters-cap">Not sure where to start? Ask me —</div>
            {STARTERS.map((q) => (
              <button
                key={q}
                className="v-brain-starter"
                type="button"
                onClick={() => {
                  try {
                    brainRef.current?.groundedAsk(q)
                  } catch {
                    /* brain not mounted — the starter is a no-op rather than a crash (fail-soft, like the panel) */
                  }
                }}
              >
                {q}
              </button>
            ))}
          </div>
        )}
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
          <div className="v-note-aim">{aimAvailable ? `Note about: ${aimLabel}` : aimLabel}</div>
          {aimMeaning && <div className="v-note-meaning">{aimMeaning}</div>}
          {aimAvailable ? (
            <>
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
            </>
          ) : (
            // HONEST UNAVAILABLE (no-silent-failure): a thing is aimed but it's an activity EVENT with no saved
            // record to note/open/ask-about yet. Say so plainly — never the old silent write to the whole surface.
            <p className="v-note-unavailable">
              This is something the Company <em>did</em> — an activity event, not a saved record. You can’t note or open
              it yet; that’s coming once these can be opened.
            </p>
          )}
        </div>
      )}

      {/* FIRST-CONTACT GREETING — the RHM introduces itself as the guide, once. A gentle non-modal bubble by the
          V (no scrim → the surface stays usable behind it); dismissed by "Got it" or by opening the V. Copy is a
          TENTATIVE draft for DNA/Tim to ratify (the AI supplies the words; the operator reacts to meaning). */}
      {greet && !open && !panelOpen && !noteOpen && (
        <div className="v-greet" role="status" {...stamp('ui://rhm/greet')}>
          <div className="v-greet-h">I’m your right-hand-man</div>
          <p className="v-greet-b">
            Your guide here — I can explain whatever you’re looking at, or act on anything you point at. New here?
            Let me show you around.
          </p>
          <div className="v-greet-actions">
            <button className="v-greet-dismiss" type="button" onClick={dismissGreet}>
              I’ll explore
            </button>
            <button className="v-greet-tour" type="button" onClick={startTour}>
              Show me around
            </button>
          </div>
        </div>
      )}

      <div ref={elRef} className="vhandle" data-open={open} data-greet={greet} style={style} {...stamp('ui://rhm/handle')}>
        {open && (
          <div className="vhandle-fan" role="menu" aria-label="Right-hand-man actions">
            {/* THE AIM CAPTION — names, in human terms, what the verbs will act on RIGHT NOW (the default aim is
                the whole surface until the operator points at a thing). Without it the fan is a menu with no
                object: a stranger can't tell "Note" notes the surface vs a picked thing. Non-interactive label;
                sits above the verb arc. */}
            {/* the aim caption rides ABOVE the top item; suppressed while "what's coming" is expanded (the taller
                fan would otherwise push it up into the page's own description text). It returns on collapse. */}
            {!moreOpen && (
              <div
                className="vhandle-aim"
                aria-hidden="true"
                style={{ transform: `translate(-100%, -50%) translate(${fanCap.dx}px, ${fanCap.dy}px)` }}
              >
                <span className="vhandle-aim-k">These act on</span>
                <span className="vhandle-aim-v">{aimedThing ? aimLabel : 'everything here'}</span>
                {!aimedThing && <span className="vhandle-aim-hint">tap a dot to focus on one thing</span>}
              </div>
            )}
            {fanItems.map(({ it, dx, dy }) => {
              const transform = `translate(-100%, -50%) translate(${dx}px, ${dy}px)`
              if (it.type === 'toggle') {
                // the honest reveal: "what's coming" shows the not-yet-live verbs (still SOON-labeled); never
                // hidden-forever, never shown as working. Keeps the first impression to the live, usable actions.
                return (
                  <button
                    key="__more"
                    className="vhandle-more"
                    type="button"
                    aria-expanded={moreOpen}
                    style={{ transform }}
                    onClick={() => setMoreOpen((o) => !o)}
                  >
                    {moreOpen ? 'Show less' : 'What’s coming'}
                  </button>
                )
              }
              const v = it.v
              if (v.live) {
                // a LIVE verb: the label + its description, BOTH visible on touch (the operator-legibility law —
                // the description must not hide on a hover/title the phone can't show).
                return (
                  <button
                    key={v.id}
                    className="vhandle-verb"
                    role="menuitem"
                    data-verb={v.id}
                    aria-label={`${v.label}. ${v.desc}`}
                    style={{ transform }}
                    onClick={() => onVerb(v.id)}
                  >
                    <span className="vhandle-verb-label">{v.label}</span>
                    <span className="vhandle-verb-desc">{v.desc}</span>
                  </button>
                )
              }
              // a NOT-YET-LIVE verb (only ever shown after "what's coming") — honestly soon-tagged + still tappable
              // to the "coming soon" Notice; never presented as working.
              return (
                <button
                  key={v.id}
                  className="vhandle-verb vhandle-verb--soon"
                  role="menuitem"
                  data-verb={v.id}
                  title={`${v.label} — ${v.desc} (coming soon)`}
                  aria-label={`${v.label}. ${v.desc}. Coming soon.`}
                  style={{ transform }}
                  onClick={() => onVerb(v.id)}
                >
                  {v.label}
                  <span className="vhandle-verb-soon">soon</span>
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
