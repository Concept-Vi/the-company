import { useEffect } from 'react'
import type { Territory } from '../lib/api'
import './source.css'

// THE SOURCE SURFACE — the V's "Source" verb result. The operator picks a dot, points the V at it, taps
// Source → this reveals the FULLER record behind the dot: the comprehended content the wheel/inspector only
// showed a 140-char crumb of, plus its provenance. It lives HERE (an App-level sibling), NOT inside the V
// (rhm/) — the V is the swap-seam container DNA replaces; this durable render must survive that swap. It
// consumes the App-side `gallery:verb` dispatch exactly like the navigate re-centre does (composition's
// contract: open-source = reveal the aimed thing's source). Built on the Fresh Paper tokens — zero hardcoded
// colour. Operator-law: every word here is MEANING — no raw addresses, no code, no machine record keys.

// the human "what this is" + the fuller body the Source panel shows for the selected point.
export type SourceView = {
  addr: string // the resolvable record address we asked the territory of (for the staleness guard; NEVER shown)
  label: string // the kind's HUMAN name (rides on the point) — what the operator tapped
  meaning: string | null // the kind's one-line meaning
  content: string | null // the fuller comprehended prose (the drill-past-the-summary value); null = none resolved
  refs: number // board references INTO this thing (provenance) — rendered only when > 0
  loading: boolean
  error: string | null
}

// the upper bound on the fuller record we show — generous (this IS the drill-past-the-summary view, and the
// panel scrolls), but a rail so a pathological record can never become an unbounded wall. Honest ellipsis.
const SOURCE_MAX = 4000

// Pull the HUMAN content out of a resolved territory (operator-law: prose only — never a raw dict/code/address).
// The comprehended record resolves as {kind, lineage, model, output, …}; `output` is the legible part and is
// either a STRING (prose) or a LIST OF STRINGS (captured points — rendered as bullet lines). A plain-string
// identity is itself the content. Anything that resolves to no plain text (a list of dicts, a nested object)
// degrades to null → "no plain words" (NEVER a raw dump). corpus_content (the dereferenced cas content) wins
// over identity when present.
export function readTerritoryContent(t: Territory): string | null {
  const got = contentFrom(t.corpus_content ?? t.identity)
  if (!got) return null
  return got.length > SOURCE_MAX ? `${got.slice(0, SOURCE_MAX).replace(/\s+\S*$/, '')}…` : got
}

// recursive human-text extractor: string → itself; list → its string items as bullet lines (non-strings
// dropped); object → the first content-bearing field. Returns null when nothing plain-text is found.
function contentFrom(cand: unknown): string | null {
  if (typeof cand === 'string') return cand.trim() || null
  if (Array.isArray(cand)) {
    const lines = cand.filter((x): x is string => typeof x === 'string' && x.trim().length > 0).map((x) => `• ${x.trim()}`)
    return lines.length ? lines.join('\n') : null
  }
  if (cand && typeof cand === 'object') {
    for (const k of ['output', 'text', 'digest', 'summary', 'body', 'content']) {
      const got = contentFrom((cand as Record<string, unknown>)[k])
      if (got) return got
    }
  }
  return null
}

// The provenance count: how many recorded things reference this one (board edges-IN). 0 for most corpus
// points (they carry no authored board edges) → an honest "stands on its own", never a fabricated link.
export function territoryRefCount(t: Territory): number {
  const ei = t.relations?.edges_in
  return Array.isArray(ei) ? ei.length : 0
}

export function SourcePanel({ source, onClose }: { source: SourceView | null; onClose: () => void }) {
  // Escape closes; the scrim press closes too. (The V handle keeps its own listeners; this is its own surface.)
  useEffect(() => {
    if (!source) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [source, onClose])

  if (!source) return null
  return (
    <>
      <div className="src-scrim" onClick={onClose} />
      <aside className="v-source" role="dialog" aria-label="Source" aria-modal="false">
        <button className="v-source-close" type="button" aria-label="Close" onClick={onClose}>
          ×
        </button>
        <div className="v-source-tag">The full record</div>
        <h2 className="v-source-name">{source.label}</h2>
        {source.meaning && <p className="v-source-meaning">{source.meaning}</p>}

        {source.loading && (
          <p className="v-source-status" role="status">
            Looking…
          </p>
        )}
        {source.error && (
          <p className="v-source-status v-source-status--err" role="status">
            Couldn’t reach the source — try again.
          </p>
        )}
        {!source.loading && !source.error && (
          <>
            {source.content ? (
              <>
                {/* a heading so the content doesn't float — the operator was told "a note was saved"; this
                    names what they're now reading (fresh-eyes critic: the body needs a label to cohere). */}
                <div className="v-source-bodylabel">What’s in it</div>
                <div className="v-source-body">{source.content}</div>
              </>
            ) : (
              <p className="v-source-empty">The fuller record isn’t in plain words here — only the summary above.</p>
            )}
            {source.refs > 0 && (
              <p className="v-source-prov">
                Referenced by {source.refs} other {source.refs === 1 ? 'thing' : 'things'}.
              </p>
            )}
          </>
        )}
      </aside>
    </>
  )
}
