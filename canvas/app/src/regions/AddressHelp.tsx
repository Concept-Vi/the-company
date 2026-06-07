// D2 · THE COMPOSED ADDRESS-HELP / ALTITUDE SURFACE — "what can I do here?" for an addressed element.
//
// WHAT THIS IS (REPO-KNOWLEDGE D2): when the operator INDICATES a ui:// element, this panel shows the THREE
// LEGS of address_help composed into ONE designed surface AT TIM'S ALTITUDE. It EXPOSES the existing D1
// composer (Suite.address_help, committed 89f60d9) via GET /api/address-help → ctrl.fetchAddressHelp — it is
// NOT a parallel FE composer (registry-is-truth, rule 3): the join of what-this-is / how-to-use / how-to-change
// is done backend-side; this region only READS the bundle and renders it.
//
// THE ALTITUDE MOVE (F1, the heart of this lane — feedback-altitude-transformation-layer):
//   • LEAD with the plain-language WHAT + HOW-TO-USE (Tim's level — recognition-by-sight, the authored howto
//     prose in the calm-authority display voice). The howto is rendered AS AUTHORED — we do NOT parse/split it
//     on WHAT:/WHAT YOU CAN DO: markers (the seeded addresses follow that shape; future ones won't — splitting
//     would invent structure not in the data).
//   • DEMOTE the mechanism (code symbols, file paths, blast-radius reach) to a DRILL-DOWN — a collapsible
//     "how to change it" section, CLOSED by default. The operator expands it on demand. The collapse IS the
//     altitude move: up-translate reality to his level; down-drill to the depths only when asked.
//
// DEGRADE-CLEAN PER LEG (rule 4 fail-loud-legible + G-53 — many elements author no howto yet). The five
// states, each rendered DISTINCTLY (never a blank, never a crash):
//   1. all-3 present (e.g. ui://toolbar/run) — full panel: WHAT + howto + drill-down change leg.
//   2. thin howto (e.g. ui://toolbar/portal) — what + change present; how-to-use → honest "no how-to authored
//      yet" cue (G-53), never blank.
//   3. no-code (e.g. ui://canvas/wire-request) — what present; how-to-change honestly empty using the leg
//      `note` ("maps to no code scope"); how-to-use absent.
//   4. well-formed-but-unregistered (what_this_is carries '(unregistered)') — render "this address isn't
//      registered yet", NOT the '(unregistered)' token as if it were a description.
//   5. malformed → backend 400 → ctrl.addressHelpError set → render the fail-loud error, never blank.
//
// FORM (rule 9 — FORM is half of done): built on the SHARED KIT (SectionHead / Badge / Surface / EmptyState)
// + design tokens (var() only) — design-lint clean, coherent with the commander's-bridge language. The
// drill-down reuses the SAME collapse idiom History uses (a caret-button head + a body). Responsive: it lives
// in the right-rail .panel scroll column, so it inherits the ≤699px bottom-sheet (the 'panel' tab) for free.
// Renders NOTHING unless a ui:// element is indicated, so it never clutters the rail.
//
// NOW ADDRESSED (G-55 closed): this panel carries `data-ui-ref="ui://inspector/help"` — a registered corpus
// address (design/_system/addresses.json: region inspector, represents WALK-uiresolve, code
// AddressHelp.tsx + suite.py:address_help, with an authored howto). So the help panel is itself a
// guidable/help-able element (show-me can spotlight the help surface, and address_help can describe itself).
// The ref is carried on EVERY render branch (fail / loading / composed) so the locus is addressable in any
// state. The panel still renders nothing unless a ui:// element is indicated.
//
// G-53 NOTE (honest, surfaced not papered): when an element authors no howto, the plain-language WHAT degrades
// to the corpus `represents` feature-id (e.g. "represents NODE-portal") — a terser machine label, not full
// prose. We render it honestly (labelled as the registry's identity for the element) and flag the gap in the
// lane report; we do NOT edit suite.py to enrich `represents` (that file is owned by another lane).
import { useState } from 'react'
import { SectionHead, Badge, Surface, EmptyState } from '../components/kit'
import { useApp } from '../AppContext'

// Strip the leading 'ui://' for a calmer kicker (the full address still rides the SectionHead tag context).
function shortAddr(a: string): string { return a.replace(/^ui:\/\//, '') }

// The how-to-change leg carries a represents-style what_this_is of the form "ui://x — represents FEAT-id".
// When the howto is ABSENT (G-53), this is the only WHAT we have — surface the feature-id part as the
// element's registry identity rather than echoing the raw address twice.
function representsLabel(what: string, address: string): string | null {
  const m = what.match(/—\s*represents\s+(.+)$/)
  return m ? m[1].trim() : (what && what !== address ? what : null)
}

export function AddressHelp() {
  const { indicated, addressHelp, addressHelpBusy, addressHelpError } = useApp()
  // the mechanism drill-down is CLOSED by default — altitude: the depths hide until asked.
  const [showMechanism, setShowMechanism] = useState(false)
  if (!indicated || !indicated.startsWith('ui://')) return null   // only a ui:// locus has composed help

  // STATE 5 · fail-loud: a malformed/unresolvable address. Never a blank — say what failed.
  if (addressHelpError) {
    return (
      <div className="ahelp" data-ui-ref="ui://inspector/help">
        <SectionHead tag={shortAddr(indicated)} aside={<Badge tone="fail">unresolved</Badge>}>help</SectionHead>
        <Surface tone="fail"><span className="ahelp-fail">✕ {addressHelpError}</span></Surface>
      </div>
    )
  }

  const h = addressHelp
  // before the first bundle lands (or between indications) — an honest loading cue, never a blank.
  if (!h || h.address !== indicated) {
    return (
      <div className="ahelp" data-ui-ref="ui://inspector/help">
        <SectionHead tag={shortAddr(indicated)} aside={<Badge tone="dim">{addressHelpBusy ? 'loading…' : '—'}</Badge>}>help</SectionHead>
        {!addressHelpBusy && <EmptyState>resolving what you can do here…</EmptyState>}
      </div>
    )
  }

  const legs = h.legs_present
  const registered = legs.what_this_is                      // false ⇒ well-formed-but-unregistered (STATE 4)
  const howto = h.how_to_use                                // null ⇒ no authored how-to (G-53, STATE 2)
  const change = h.how_to_change
  const ident = representsLabel(h.what_this_is, h.address)  // the represents feature-id (the WHAT when howto is thin)
  // how-many legs resolved — the at-a-glance completeness cue (read by sight).
  const present = [legs.what_this_is, legs.how_to_use, legs.how_to_change].filter(Boolean).length

  return (
    <div className="ahelp" data-ui-ref="ui://inspector/help">
      {/* HEAD — the commander's-bridge title in the display voice. The address rides the kicker (the locus this
          help is FOR); a Badge counts how many of the 3 legs resolved (sig when full, await when partial). */}
      <SectionHead tag={shortAddr(indicated)}
        aside={<Badge tone={present === 3 ? 'sig' : present === 0 ? 'fail' : 'await'}>{present}/3 known</Badge>}>
        what you can do here
      </SectionHead>

      {/* STATE 4 · well-formed but UNREGISTERED — say so plainly, don't show the '(unregistered)' token as a description. */}
      {!registered && (
        <EmptyState>
          this element (<code className="ahelp-addr">{shortAddr(indicated)}</code>) isn't registered in the
          interface map yet — so there's no authored help, identity, or change-scope for it. Register it in the
          corpus to give it a how-to.
        </EmptyState>
      )}

      {registered && (
        <>
          {/* LEG 1+2 · THE ALTITUDE LEAD — plain-language WHAT + HOW-TO-USE, in the display voice. This is Tim's
              level: prose, not symbols. */}
          {howto
            ? <div className="ahelp-howto">{howto}</div>
            : (
              // STATE 2 · G-53 — no authored howto. Honest cue + the registry identity (the represents feature-id)
              // as the only WHAT we have, labelled as such — never blank, never a fabricated help text.
              <div className="ahelp-thin">
                {ident && <div className="ahelp-ident"><span className="ahelp-ident-k">this is</span> {ident}</div>}
                <EmptyState>no how-to authored for this element yet — its identity is shown above. (A how-to can be added to the corpus to teach it.)</EmptyState>
              </div>
            )}

          {/* LEG 3 · HOW TO CHANGE IT — the MECHANISM, behind a DRILL-DOWN (closed by default = the altitude move).
              The depths (code symbols, files, blast-radius reach) surface only when the operator expands. */}
          <button className="ahelp-drill" type="button" onClick={() => setShowMechanism(v => !v)}
            title={showMechanism ? 'hide the mechanism' : 'show how to change it (code, files, what it touches)'}>
            <span className="ahelp-caret">{showMechanism ? '▾' : '▸'}</span>
            <span className="ahelp-drill-label">how to change it</span>
            <Badge tone={legs.how_to_change ? 'wire' : 'dim'}>
              {legs.how_to_change ? `${change.scope.length} file${change.scope.length === 1 ? '' : 's'}` : 'no code'}
            </Badge>
          </button>

          {showMechanism && (
            <div className="ahelp-mech">
              {/* STATE 3 · no-code address — honest empty using the leg note, never a fabricated scope. */}
              {!legs.how_to_change && (
                <EmptyState>{change.note || 'this element maps to no code scope — there is nothing here to change directly.'}</EmptyState>
              )}
              {legs.how_to_change && (
                <>
                  <div className="ahelp-mech-sub">the files this element powers (a change here edits these):</div>
                  <div className="ahelp-files">
                    {change.scope.map((f: string) => (
                      <Surface key={f} tone="wire" className="ahelp-file"><code>{f}</code></Surface>
                    ))}
                  </div>
                  {/* the blast-radius reach — "if you change this, here's what else it touches" (X9/X14). Rendered as
                      a compact reach summary (counts by kind) so it reads by sight, not as a raw edge dump. */}
                  <BlastReach radius={change.blast_radius} />
                  {change.note && <div className="ahelp-note">{change.note}</div>}
                </>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

// The blast-radius reach, summarised by KIND (recognition-by-sight, not a wall of symbol names). Each kind is a
// labelled count chip; a populated kind expands its members inline. Degrades clean: an empty/stale radius shows
// its own note (the embedder-down semantic ring degrade, G-12/G-34, surfaces here as an honest note + empty).
function BlastReach({ radius }: { radius: any }) {
  if (!radius || typeof radius !== 'object') return null
  const co = radius.co_reference || []
  const deps = radius.structural_dependents || []
  const reqs = radius.structural_dependencies || []
  const sem = radius.semantic_neighbours || []
  const total = co.length + deps.length + reqs.length + sem.length
  if (total === 0) {
    // honest empty reach — say so (and surface a stale/semantic note if the corpus join couldn't be read).
    const note = radius.structural_note || radius.semantic_note || radius.note
    return <div className="ahelp-reach"><div className="ahelp-mech-sub">reach</div>
      <EmptyState>{note || 'this change touches nothing else — no co-references, dependents, or related code.'}</EmptyState></div>
  }
  return (
    <div className="ahelp-reach">
      <div className="ahelp-mech-sub">what a change here reaches:</div>
      <ReachKind label="also touches the same code" tone="await" members={co} />
      <ReachKind label="depends on this (verify)" tone="fail" members={deps} />
      <ReachKind label="this relies on" tone="dim" members={reqs} />
      <ReachKind label="conceptually related" tone="wire" members={sem} />
      {radius.semantic_note && sem.length === 0 && (
        <div className="ahelp-note">{radius.semantic_note}</div>
      )}
    </div>
  )
}

function ReachKind({ label, tone, members }: { label: string; tone: any; members: string[] }) {
  const [open, setOpen] = useState(false)
  if (!members || members.length === 0) return null
  return (
    <div className="ahelp-reach-kind">
      <button className="ahelp-reach-head" type="button" onClick={() => setOpen(v => !v)}>
        <span className="ahelp-caret">{open ? '▾' : '▸'}</span>
        <span className="ahelp-reach-label">{label}</span>
        <Badge tone={tone}>{members.length}</Badge>
      </button>
      {open && (
        <div className="ahelp-reach-members">
          {members.map((m: string) => <code key={m} className="ahelp-reach-member">{m}</code>)}
        </div>
      )}
    </div>
  )
}
