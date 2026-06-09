// THE STUDIO'S NAMED STRUCTURAL PRIMITIVES — the keystone of the Application-Structure Pack (layer ②).
//
// WHAT THIS FILE IS: the real, named component shells the Studio surface composes from, so Claude Design
// can DESIGN AGAINST NAMED PRIMITIVES (the pack's strongest lever after the design system). Each primitive
// declares its CONTRACT in its header — { binds: the data it shows · emits: the events/intents it raises ·
// token-slots: the CSS-variable styling interface its look reads from } — and is STRUCTURE-ONLY: layout
// that works, NO bespoke aesthetic, NO gold-look. Claude Design fills the token-slots; the structure stays.
//
// THE FIVE NAMED PARTS (the studio skeleton = [ Rail │ Stage │ RhmPanel ], Composer lives in RhmPanel,
// Card is the Rail's row):
//   <Card>      — one gallery item (a reviewable mockup), carrying its reviewed-surface ui:// address.
//   <Rail>      — the gallery: the corpus of Cards, grouped, registry-bound (G4).
//   <Stage>     — the device stage: the chosen mockup in a sandboxed iframe (phone/desktop), served same-origin.
//   <Composer>  — the addressed-feedback composer: comment-at-locus (→/api/annotate) + request-change (→/api/intent-at).
//   <RhmPanel>  — the right-hand-man organ at the locus (the real <RhmChat/>) + AddressHelp + the Composer.
//
// LAWS THIS FILE OBEYS (layer ⑤):
//   · click INDICATES + CONSENTS, never click=execute — a Card click INDICATES its locus (no run); the RHM
//     PROPOSES in chat; an action goes through see-and-approve (the I3 approve→/api/act path in RhmChat).
//   · reflects-never-owns — every part shows backend truth (corpus / annotations / address-help via api+SSE);
//     it never holds authoritative state. The locus is the one indicate() sink, not a parallel store.
//
// REUSE: composes the shared kit (Surface/SectionHead/Badge/EmptyState) inside these shells, and the REAL
// controller fns (indicate via setReviewMockup, sendChat, annotateLocus, mintBuildIntent, fetchAddressHelp).
// It does NOT reinvent the chat box (that was the standalone studio's sin) — the RhmPanel mounts <RhmChat/>.
import { useState, useEffect, useRef, type ReactNode } from 'react'
import { useApp } from '../AppContext'
import { Surface, SectionHead, Badge, EmptyState } from './kit'
import { RhmChat } from '../regions/RhmChat'

// ─────────────────────────────────────────────────────────────────────────────────────────────────────
// <Card> — ONE GALLERY ITEM (a reviewable mockup in the corpus).
//   binds:   { file, title, platform, group, address } — one corpus row (from /api/corpus, registry-truth).
//   emits:   onSelect(file, address) — INDICATES the reviewed-surface locus + loads the mockup in the Stage.
//            (click INDICATES, never executes — selecting a card points at it; nothing runs.)
//   token-slots (the styling interface Claude Design fills, read by .studio-card in app.css):
//            --studio-card-bg · --studio-card-border · --studio-card-active-accent · --studio-card-radius ·
//            --studio-card-pad · --studio-card-platform-tint.
// Composes the kit <Surface> (the elevated card primitive) + <Badge> (the platform pill) so it reads as the
// ONE product language. Carries `data-ui-ref={address}` so the document-level capture listener indicates it.
export function Card({ file, title, platform, group, address, active, onSelect }: {
  file: string; title: string; platform: string; group: string; address: string | null;
  active: boolean; onSelect: (file: string, address: string | null) => void
}) {
  void group   // bound for the contract (the Rail groups by it); not painted on the card itself
  // platform tone maps onto a kit Badge tone — STRUCTURAL mapping only (the colour is a token Claude Design owns).
  const tone = platform === 'mobile' ? 'await' : platform === 'tool' ? 'wire' : 'sig'
  return (
    <Surface
      tone={active ? 'wire' : undefined}
      onClick={() => onSelect(file, address)}
      className={'studio-card' + (active ? ' is-active' : '')}
      title={address ? file + ' · ' + address : file}
      dataUiRef={address || undefined}
    >
      <span className="studio-card-title">{title}</span>
      <span className="studio-card-meta">
        <Badge tone={tone}>{platform}</Badge>
        {/* the raw ui:// address is the SYSTEM's locus — kept as data-ui-ref + the title tooltip, NOT shown
           as a visible label. A non-developer reads the title + platform, never address syntax like
           "ui://canvas" (FORM: no dev jargon on the operator face, 2026-06-09). */}
      </span>
    </Surface>
  )
}

// ─────────────────────────────────────────────────────────────────────────────────────────────────────
// <Rail> — THE GALLERY (the corpus of Cards, grouped).
//   binds:   corpus[] (from /api/corpus — registry-is-truth, NOT a hardcoded list) + the active file.
//   emits:   onSelect(file, address) (delegated to each Card) · re-bind on mount.
//   token-slots: --studio-rail-bg · --studio-rail-w · --studio-rail-gap · --studio-group-label-color.
// Composes kit <SectionHead> (the rail heading) + grouped <Card>s. Fail-loud: a corpus error renders a
// visible <EmptyState> stating WHY (reflects-never-owns + rule 4), never a silently empty gallery.
export function Rail() {
  const { corpus, corpusErr, reviewMockup, setReviewMockup } = useApp()
  // group the registry rows into the rail's sections (the corpus carries `group` per item — one source).
  const groups: Record<string, typeof corpus> = {}
  for (const it of corpus) (groups[it.group] = groups[it.group] || []).push(it)
  return (
    <div className="studio-rail" data-ui-ref="ui://studio/rail">
      <SectionHead tag="review corpus">mockups</SectionHead>
      {corpusErr && <EmptyState>could not load the corpus — {corpusErr}</EmptyState>}
      {!corpusErr && corpus.length === 0 && <EmptyState>the corpus is empty — no reviewable mockups on disk.</EmptyState>}
      {Object.entries(groups).map(([g, items]) => (
        <div className="studio-group" key={g}>
          <div className="studio-group-label">{g}</div>
          {items.map(it => (
            <Card key={it.file} {...it} active={reviewMockup === it.file}
              onSelect={(f, a) => setReviewMockup(f, a)} />
          ))}
        </div>
      ))}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────────────────────────────
// <Stage> — THE DEVICE STAGE (the chosen mockup, sandboxed, phone/desktop).
//   binds:   reviewMockup (the open file) + reviewAddress (the locus it depicts) + a local device toggle.
//   emits:   nothing to the backend (a pure VIEW — reflects-never-owns). The device toggle is local presentation.
//   token-slots: --studio-stage-bg · --studio-stage-frame-shadow · --studio-stage-phone-w (390) ·
//                --studio-stage-desktop-w (1440) · --studio-stage-pad.
//   IN-MOCKUP ELEMENT DEIXIS (BUILT): clicking a control INSIDE a staged mockup indicates THAT element's
//   ui:// address (not just the whole reviewed surface). MECHANISM: the bridge serves the mockup with a tiny
//   sandboxed capture script (only on the studio `?studio=1` serving path) that, on a click inside the mockup,
//   finds the nearest element carrying a full-ui:// `data-ui-ref` and postMessages it to the parent window.
//   The Stage listens for that {type:'studio-deixis', address} message and calls setReviewMockup(currentFile,
//   address) — the SAME locus sink the gallery uses: it leaves the open file unchanged (no iframe remount, the
//   `key={reviewMockup}` is stable) and sets reviewAddress + indicate(address), so the Composer/RhmPanel/
//   AddressHelp all re-bind to the clicked element's locus. NO parallel store. FAIL-SOFT: a click on an element
//   with no ui:// data-ui-ref posts nothing → the locus stays at the whole-mockup address (today's behaviour).
//   GUARDS (load-bearing): only same-origin messages, only the studio-deixis envelope, only ui:// addresses —
//   so vite/devtools' own dev-time postMessages can never move the locus.
export function Stage({ titleFor }: { titleFor: (f: string | null) => string }) {
  const { corpus, reviewMockup, reviewAddress, setReviewMockup } = useApp()
  const [device, setDevice] = useState<'desktop' | 'phone'>('desktop')
  // non-stale read of the open file inside the click delegate — mirrors useAppController's indicatedRef
  // pattern, so the deixis re-indicate keeps the SAME file open and only swaps the address.
  const reviewMockupRef = useRef<string | null>(reviewMockup)
  reviewMockupRef.current = reviewMockup
  // the WHOLE-mockup (base) locus — the address the mockup represents (its corpus row). BOTH levels are
  // reachable (Tim 2026-06-09: "I may want to select the whole thing AND add comments — not either/or"):
  // clicking an addressed ELEMENT selects it; clicking the background (or the ⤢ whole-screen control) returns
  // to the whole mockup. A ref so the (per-load) click delegate reads it fresh.
  const baseAddr = corpus.find((c: any) => c.file === reviewMockup)?.address || null
  const baseAddrRef = useRef<string | null>(baseAddr)
  baseAddrRef.current = baseAddr
  useEffect(() => {
    function onMsg(e: MessageEvent) {
      if (e.origin !== location.origin) return                     // only our own served mockups (not vite/devtools)
      const d: any = e.data
      if (!d || d.type !== 'studio-deixis') return                 // only the deixis envelope
      const addr = typeof d.address === 'string' ? d.address : ''
      if (!addr.startsWith('ui://')) return                        // only a full ui:// address is a locus
      setReviewMockup(reviewMockupRef.current, addr)
    }
    window.addEventListener('message', onMsg)
    return () => window.removeEventListener('message', onMsg)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
  // ★ ELEMENT-LEVEL DEIXIS — wired from the PARENT on iframe load. The mockups never sent the studio-deixis
  // message (0/23 — so element selection NEVER worked, Tim's "I can only select the whole thing"). The frame
  // is same-origin (served from /mockups, sandbox allow-same-origin), so the parent attaches the click
  // delegate directly. BOTH levels: a click on an addressed element → that element's locus; a click on the
  // background → the WHOLE-mockup base (so you can always comment on the whole screen too).
  const frameRef = useRef<HTMLIFrameElement | null>(null)
  // attach the click delegate to the mockup doc ONCE (idempotent via a flag), so element-clicks select.
  function attachDeixis(doc: Document | null | undefined) {
    if (!doc || !doc.body || (doc as any).__deixisWired) return false
    ;(doc as any).__deixisWired = true
    doc.addEventListener('click', (ev: Event) => {
      const t = ev.target as Element | null
      const el = t?.closest?.('[data-ui-ref]') as Element | null
      const a = el?.getAttribute('data-ui-ref') || ''
      const next = a.startsWith('ui://') ? a : baseAddrRef.current   // element locus, else the whole mockup
      setReviewMockup(reviewMockupRef.current, next)
    }, true)
    return true
  }
  // ROBUST attach: onLoad alone is unreliable for a key-remounting iframe (it can fire before React binds the
  // handler, or the same-origin doc isn't ready yet). So ALSO poll briefly per open file until the doc is
  // ready + wired (idempotent). This is the fix for "element-select never worked" being load-timing-fragile.
  useEffect(() => {
    if (!reviewMockup) return
    let tries = 0
    const id = setInterval(() => {
      tries++
      const done = attachDeixis(frameRef.current?.contentDocument)
      if (done || tries > 20) clearInterval(id)   // ~20×120ms ≈ 2.4s budget
    }, 120)
    return () => clearInterval(id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reviewMockup])
  return (
    <div className="studio-stage" data-ui-ref="ui://studio/stage">
      <div className="studio-stage-head">
        <span className="studio-stage-title">
          {reviewMockup
            ? titleFor(reviewMockup)
            : <span className="muted">pick a mockup from the left to review</span>}
        </span>
        <span className="studio-stage-tools">
          {/* the locus indicator — the operator SEES what the RHM is grounded on (the vision: "I should see
             what it's grounded on"), but in PLAIN words, never raw address syntax: strip the "ui://" scheme
             and lead with "looking at:" (FORM: no dev jargon on the operator face, 2026-06-09). */}
          {reviewAddress && <Badge tone="wire">looking at: {reviewAddress.replace(/^ui:\/\//, '')}</Badge>}
          {/* WHOLE-SCREEN — always return to commenting on the whole mockup (both levels, not either/or). Shown
             when an ELEMENT is selected (reviewAddress drilled below the base); click to pop back to the whole. */}
          {baseAddr && reviewAddress && reviewAddress !== baseAddr && (
            <button type="button" className="studio-dev" data-ui-ref="ui://studio/stage/whole"
              title="comment on the whole screen (not just the selected element)"
              onClick={() => setReviewMockup(reviewMockup, baseAddr)}>⤢ whole screen</button>
          )}
          <button type="button" className={'studio-dev' + (device === 'desktop' ? ' on' : '')}
            data-ui-ref="ui://studio/stage/device-desktop" onClick={() => setDevice('desktop')}>desktop</button>
          <button type="button" className={'studio-dev' + (device === 'phone' ? ' on' : '')}
            data-ui-ref="ui://studio/stage/device-phone" onClick={() => setDevice('phone')}>phone</button>
        </span>
      </div>
      <div className={'studio-stage-body dev-' + device}>
        {reviewMockup
          ? <iframe key={reviewMockup} ref={frameRef} className="studio-frame" title={reviewMockup}
              onLoad={() => attachDeixis(frameRef.current?.contentDocument)}
              src={'/mockups/' + reviewMockup + '?studio=1'} sandbox="allow-scripts allow-same-origin" />
          : <EmptyState>no mockup open.</EmptyState>}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────────────────────────────
// <Composer> — THE ADDRESSED-FEEDBACK COMPOSER (the structured-comment-at-locus input).
//   binds:   the indicated locus (reviewAddress) + the comment THREAD at it (annotations — read back from
//            the SHARED store, GET /api/annotations, NOT the bespoke jsonl).
//   emits:   onComment(text)  → annotateLocus → POST /api/annotate  (the I6 attach-comment seam, SHARED store)
//            onRequest(text)  → mintBuildIntent → POST /api/intent-at (the L1-adjacent build-intent door —
//                               WIRED: surface_intent_at IS built; the address→intent leg is reachable today)
//   token-slots: --studio-composer-bg · --studio-composer-input-border · --studio-composer-thread-gap.
//   EXCLUSION (load-bearing): the Composer carries data-ui-ref="ui://studio/composer" and the Studio's
//   onDocClick guard skips clicks inside it — so clicking into the textarea does NOT re-indicate the
//   composer and overwrite the locus (the exact bug the chat-region + wire-door + help-panel exclusions
//   prevent). The Composer READS the locus, it never BECOMES it.
//   LAW: this is the ANNOTATE/REQUEST face (attach-a-comment / request-a-change). It NEVER executes — a
//   request mints a build-intent (resolved=None, plan-mode); dispatch is off this face (consent gate).
export function Composer() {
  const { reviewMockup, reviewAddress, annotations, annotationsBusy, annotateLocus, mintBuildIntent,
          mockupGenerate, generateBusy, generateResult } = useApp()
  const [text, setText] = useState('')
  const thread = annotations?.thread || []
  const hasLocus = !!(reviewAddress && reviewAddress.startsWith('ui://'))
  async function comment() { const t = text.trim(); if (!t) return; await annotateLocus(t); setText('') }
  async function request() { const t = text.trim(); if (!t) return; await mintBuildIntent(t); setText('') }
  // GENERATE FOLLOW-ON — gated on a MOCKUP being open (the whole file), NOT on hasLocus: generate refines
  // the file from its captured feedback; comment/request act at the ui:// locus. plan-mode is safe (proposes,
  // changes nothing). The engine PROPOSES — the surface SHOWS what it would change (generateResult below).
  const generated = generateResult && reviewMockup && generateResult.mockup_file === reviewMockup ? generateResult : null
  return (
    <div className="studio-composer" data-ui-ref="ui://studio/composer">
      <div className="studio-composer-locus">
        {hasLocus
          ? <>commenting on <b>this part of the screen</b></>  /* the raw ui:// locus is the machine address — kept as the binding, not shown; "this part" reads at the operator's altitude */
          : <span className="muted">pick a screen, then comment or ask for a change</span>}
      </div>
      {/* the THREAD read back from the SHARED annotation store (proves persist-to-shared-store, not jsonl) */}
      {hasLocus && (
        <div className="studio-composer-thread">
          {annotationsBusy && <span className="muted">loading comments…</span>}
          {!annotationsBusy && thread.length === 0 && <span className="muted">no comments here yet.</span>}
          {thread.map((a: any, i: number) => (
            <div className="studio-comment" key={a.ts || i}>
              <span className="studio-comment-src muted">{a.source || a.role || 'operator'}</span>
              <span className="studio-comment-text">{a.text}</span>
            </div>
          ))}
        </div>
      )}
      <textarea className="studio-composer-input" rows={2} value={text}
        placeholder={hasLocus ? 'comment on this surface, or describe a change…' : 'point at a surface first'}
        onChange={e => setText(e.target.value)} disabled={!hasLocus} />
      <div className="studio-composer-actions">
        <button type="button" className="studio-act" disabled={!hasLocus || !text.trim()} onClick={comment}
          title="attach this as a comment at the locus (shared annotation store)">💬 comment</button>
        <button type="button" className="studio-act" disabled={!hasLocus || !text.trim()} onClick={request}
          title="request a change here — mints a build-intent (plan-mode; you approve the reach later)">⚙ request a change</button>
        {/* GENERATE FOLLOW-ON — runs the committed generate-for-mockups engine on the OPEN mockup (plan-mode,
            safe). Gated on a mockup being open, NOT on the locus. The RHM PROPOSES; nothing is applied. */}
        <button type="button" className="studio-act" data-ui-ref="ui://studio/generate"
          disabled={!reviewMockup || generateBusy} onClick={() => mockupGenerate(reviewMockup)}
          title="generate (plan) — refine this mockup from its captured feedback; proposes the edit, changes nothing">
          {generateBusy ? '… generating' : '✨ generate'}</button>
      </div>
      {/* the PROPOSED result the engine returned — what it WOULD change (plan-mode: changed_files is [] = nothing applied). */}
      {generated && (
        <div className="studio-generate-result" data-ui-ref="ui://studio/generate/result">
          <div className="studio-generate-head muted">
            proposed edit for <b>{generated.mockup_file}</b> · mode {generated.mode} ·
            {' '}{Array.isArray(generated.changed_files) ? generated.changed_files.length : 0} file(s) would change
          </div>
          {generated.proposed_summary
            ? <div className="studio-generate-summary">{generated.proposed_summary}</div>
            : <span className="muted">the engine returned no summary text.</span>}
        </div>
      )}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────────────────────────────
// <RhmPanel> — THE RIGHT-HAND-MAN ORGAN AT THE LOCUS (the real one, not a feedback box).
//   binds:   the indicated locus (reviewAddress) + its address-help bundle (addressHelp, GET /api/address-help)
//            + the live chat organ (via <RhmChat/>, which the controller binds to the locus through
//            sendChat's focus.selected = [mockup://<file>, ui://<address>, …node-ids]).
//   emits:   (via RhmChat) sendChat → POST /api/chat with focus={selected:["ui://…"]} — the focus→locus→
//            context-at-address channel. The RHM PROPOSES; the I3 approve card fires /api/act on consent.
//   token-slots: --studio-rhm-bg · --studio-rhm-help-bg · --studio-rhm-lede-color.
//   This is the WHOLE POINT of the rebuild: the standalone studio's right panel was a static textarea
//   labelled "right-hand-man"; here it IS the same brain/persona/thread machinery the canvas uses, grounded
//   at the studio element's locus. address_help shows "what is this + what a change would touch" at the locus.
export function RhmPanel({ children }: { children?: ReactNode }) {
  const { reviewAddress, addressHelp, addressHelpBusy, sendChat, reviewMockup } = useApp()
  const hasLocus = !!(reviewAddress && reviewAddress.startsWith('ui://'))
  return (
    <div className="studio-rhm" data-ui-ref="ui://studio/rhm">
      <div className="studio-rhm-lede">
        You're reviewing a design surface — the right-hand-man reads it for you in plain language.
        {/* The lede no longer just TELLS the operator to ask — it gives a one-click primed question that
           FIRES the read for them (reuses sendChat, which carries the open mockup as focus → the
           screen_reader role narrates the screen at the operator's altitude). "Reads each screen FOR you." */}
        <button className="b studio-read-btn" data-ui-ref="ui://studio/rhm/read"
          disabled={!reviewMockup}
          style={{ display: 'block', marginTop: 8 }}
          title="the right-hand-man reads this screen and tells you what it is + what you can do"
          onClick={() => sendChat('What am I looking at here, and what can I do on this screen?')}>
          ◎ what am I looking at?
        </button>
      </div>
      {/* AddressHelp AT THE LOCUS — "what is this + what a change would touch" (the D1 composer). reflects-only. */}
      {hasLocus && (
        <div className="studio-rhm-help" data-ui-ref="ui://studio/rhm/help">
          {addressHelpBusy && <span className="muted">resolving the locus…</span>}
          {!addressHelpBusy && addressHelp && (
            <>
              <div className="studio-help-what"><b>this surface:</b> {addressHelp.what_this_is}</div>
              {addressHelp.how_to_change?.scope?.length > 0 && (
                <div className="studio-help-change muted">
                  a change here would touch {addressHelp.how_to_change.scope.length} file(s)
                </div>
              )}
            </>
          )}
        </div>
      )}
      {/* the REAL organ — same brain/persona/threads as the canvas, bound to the locus via focus.selected.
         studio: hide the canvas-oriented dev affordances (model name, twin record/debrief) for the non-dev reviewer. */}
      <RhmChat studio />
      {children}
    </div>
  )
}
