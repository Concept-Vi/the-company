// WAVE-2 DESIGN DIRECTION · THE SHARED KIT (H2 — one language for the whole product).
//
// These are the REUSABLE building blocks the regions compose from, so the Company's interface reads as ONE
// language (the commander's bridge) rather than each region inventing its own look. The Inbox exemplar is
// built FROM this kit; wave-3 region passes (Palette/Grow/Activity) adopt the SAME primitives. Every block
// is token-only (the .kit-* classes in app.css resolve to design-system.css tokens) → design-lint clean, no
// off-token literal, no bespoke element. Recognition-by-sight: a region is recognised by the SHAPE + TINT
// these primitives give it, not by reading text.
//
// THE VOCABULARY:
//   <SectionHead>  — a panel/region heading in the Fraunces display voice (the calm-authority title).
//   <LaneHead>     — a grouped-lane header: a tint cue + a name + a count badge ("decision → build · 2").
//   <Badge>        — a small status pill (awaiting / done / held / neutral) — read the state by colour+shape.
//   <Surface>      — the card primitive: an elevated well with an optional accent spine + tint (the unit a
//                    list-as-navigable-form is built from — a row that is a CARD, not a bare <li>).
//   <EmptyState>   — the honest "nothing here" cue (fail-loud-friendly: states WHY, never a blank).
import type { ReactNode } from 'react'

type Tone = 'sig' | 'await' | 'fail' | 'wire' | 'dim'

// SECTION HEADING — the region/panel title in the display voice. `tag` = an optional uppercase kicker above
// it (the role label), `aside` = a right-aligned slot (a count, an action). One heading shape everywhere.
export function SectionHead({ children, tag, aside }: { children: ReactNode; tag?: string; aside?: ReactNode }) {
  return (
    <div className="kit-sechead">
      <div className="kit-sechead-main">
        {tag && <span className="kit-kicker">{tag}</span>}
        <h3 className="kit-sectitle">{children}</h3>
      </div>
      {aside && <div className="kit-sechead-aside">{aside}</div>}
    </div>
  )
}

// LANE HEADER — the header of a grouped lane (the band that names a triage group + counts it). The `tone`
// drives the left-edge tint + the count colour so the lane's MEANING reads by sight (build=wire-blue,
// awaiting=amber, held=dim, done=green). `onToggle` makes it a collapsible band; `open` draws the caret.
export function LaneHead({ children, count, tone = 'dim', onToggle, open }:
  { children: ReactNode; count?: number; tone?: Tone; onToggle?: () => void; open?: boolean }) {
  const Tag = onToggle ? 'button' : 'div'
  return (
    <Tag className={'kit-lanehead kit-tone-' + tone} onClick={onToggle} {...(onToggle ? { type: 'button' as const } : {})}>
      {onToggle && <span className="kit-caret">{open ? '⌄' : '⌃'}</span>}
      <span className="kit-lane-name">{children}</span>
      {count != null && <span className="kit-lane-count">{count}</span>}
    </Tag>
  )
}

// BADGE — a small state pill. The whole point is recognition: the operator sees AMBER and knows "awaiting",
// GREEN "done", BLUE "building", without reading the word.
export function Badge({ children, tone = 'dim' }: { children: ReactNode; tone?: Tone }) {
  return <span className={'kit-badge kit-tone-' + tone}>{children}</span>
}

// SURFACE — the card primitive. A row in a navigable list is a CARD (elevated well, optional accent spine),
// never a bare line. `tone` paints the left spine (the lifecycle/kind signal); `onClick` makes it actionable
// (hover lifts it); `interactive` without onClick still gives the affordance look. This is the unit the
// "list-as-navigable-form" pattern is built from — a list of these reads as a board, not a text dump.
export function Surface({ children, tone, onClick, className = '', title, interactive, dataUiRef }:
  { children: ReactNode; tone?: Tone; onClick?: () => void; className?: string; title?: string; interactive?: boolean; dataUiRef?: string }) {
  const cls = 'kit-surface' + (tone ? ' kit-tone-' + tone : '') +
    (onClick || interactive ? ' kit-surface-actionable' : '') + (className ? ' ' + className : '')
  // data-ui-ref must stay ON the addressed element (the resolveUiTarget keystone queries by it), so forward it.
  return <div className={cls} onClick={onClick} title={title} data-ui-ref={dataUiRef}>{children}</div>
}

// EMPTY STATE — the honest "nothing here" cue. Never a blank gap: it states the rest-state plainly.
export function EmptyState({ children }: { children: ReactNode }) {
  return <div className="kit-empty">{children}</div>
}
