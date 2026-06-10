// FORAGER v1 (S7-FE) · THE SEARCH LANE — the top-center bar that turns a corpus query into circles on
// the canvas (A1), the vision bar: Tim sculpts a context set by recognition and hands it to the builder.
//
// THE FLOW: type a query + pick a space (the space list is REGISTRY-READ — /api/cognition_info `spaces`,
// the embeddable-projection subset; fallback history/repo, surfaced not silent) → EXPLICIT submit (the
// don't: never search on keystroke — embedder load) → GET /api/corpus-query?text&space&k=16 → hits land
// as ForagerShape circles near the viewport center in a loose grid (placeForagerHits: dedupe by address,
// re-hit pulses — B2). HONEST EMPTY: the backend's note (embedder down) is RENDERED loud; zero hits gets
// a "nothing returned" state (A3). Errors are loud (jr normalizes to {error} → the red note).
//
// C1 CHIPS: derived from the LOADED circles' REAL kind/session fields (registry-is-truth — no hardcoded
// vocab; a value appears as a chip the moment a hit carries it). FOCUS semantics (the mission's words:
// "clicking a chip hides non-matching circles"): a chip ON keeps its value and HIDES the rest — union
// within a facet, intersection across facets; no chips on = everything visible. Hide is TRUE hide
// (opacity 0 + collapsed hit-geometry + deselect) — never delete, and never a faint ghost the operator
// could still box-select into the D1 builder set without seeing it. CLEAR deletes type==='forager' ONLY
// (the coexistence rule, A2).
//
// B3-light: selecting a single circle INDICATES its address (useApp().indicate — the forager FEEDS the
// existing I1 locus machinery; it never clears another surface's indication — the chip's ✕ does that).
//
// FORM: kit/corpus tokens only — the bar wears the .rhm card anatomy (.hud .rhm: head/log/input — one
// language with the chat panels), starts MINIMIZED (present, never imposing), kit EmptyState for the
// honest-empty note. Hidden <699px (stated honestly as the mobile gap, like its claude-panel sibling).
import { useEffect, useState } from 'react'
import { useEditor, useValue } from 'tldraw'
import { useApp } from '../AppContext'
import { api } from '../api'
import { EmptyState } from '../components/kit'
import {
  placeForagerHits, clearForagerShapes, type ForagerShape,
} from '../ForagerShape'

type Note = { kind: 'err' | 'empty' | 'info'; text: string } | null

export function ForagerBar() {
  const editor = useEditor()
  const { indicate } = useApp()
  const [min, setMin] = useState(true)             // starts minimized — present, never imposing
  const [q, setQ] = useState('')
  const [space, setSpace] = useState('')
  const [spaces, setSpaces] = useState<string[]>([])
  const [note, setNote] = useState<Note>(null)
  const [busy, setBusy] = useState(false)
  // C1 · the FOCUSED chip set ('kind:x' / 'session:y' keys). Empty = no filter, everything visible.
  const [focused, setFocused] = useState<Set<string>>(new Set())

  // the SPACE LIST — registry-read from /api/cognition_info `spaces` (the embeddable-projection subset
  // the contract derives via projections.embeddable()). Fallback history/repo per the guide — SURFACED
  // as a note, never a silent degrade (no-silent-fallbacks law).
  useEffect(() => {
    let live = true
    api.cognitionInfo().then((r: any) => {
      if (!live) return
      const sp: string[] = Array.isArray(r?.spaces) ? r.spaces.filter((s: any) => typeof s === 'string') : []
      if (r?.error || sp.length === 0) {
        setSpaces(['history', 'repo'])
        setSpace(prev => prev || 'history')
        setNote({ kind: 'info', text: r?.error ? `spaces registry unavailable (${r.error}) — offering history/repo` : 'no embeddable spaces listed — offering history/repo' })
      } else {
        setSpaces(sp)
        setSpace(prev => prev || (sp.includes('history') ? 'history' : sp[0]))
      }
    })
    return () => { live = false }
  }, [])

  // the LIVE forager set (reactive read off the one truth — the editor store). Chips + the count derive
  // from THIS: the loaded circles' real kind/session fields, never a hardcoded vocabulary (C1).
  const shapes = useValue('forager shapes',
    () => editor.getCurrentPageShapes().filter(s => s.type === 'forager') as ForagerShape[], [editor])

  // B3-light · selecting exactly ONE circle indicates its address — the forager rides the EXISTING I1
  // locus machinery (the chip in the chats + the builder's address context). Deliberately NO
  // indicate(null) on deselect: the forager feeds the locus, it never clears another surface's.
  const onlySel = useValue('forager only-selected', () => {
    const s = editor.getOnlySelectedShape()
    return s && s.type === 'forager' ? (s as ForagerShape) : null
  }, [editor])
  useEffect(() => {
    if (onlySel) indicate(onlySel.props.address)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [onlySel?.id])

  // C1 · chips FILTER the visible set — clicking a chip HIDES the NON-MATCHING circles (the mission's
  // focus semantics), never deletes (the whittle stays the operator's delete gesture, B1). Visible =
  // (no kind-chips on OR kind matches one) AND (no session-chips on OR session matches one). Hide rides
  // the shape's TOP-LEVEL tldraw `opacity` (no shape-prop churn — the v4 snapshot schema is untouched):
  // opacity 0 = invisible, and ForagerShape.getGeometry collapses the hit-area at opacity 0 so a hidden
  // circle can't be click/box-selected into the D1 set unseen. Hidden circles are also DESELECTED for
  // the same reason. Applied imperatively over the live set so fresh hits respect a live filter.
  function applyFilters(focus: Set<string>) {
    const all = editor.getCurrentPageShapes().filter(s => s.type === 'forager') as ForagerShape[]
    if (!all.length) return
    const kinds = [...focus].filter(k => k.startsWith('kind:'))
    const sessions = [...focus].filter(k => k.startsWith('session:'))
    const hiddenIds = new Set<string>()
    editor.updateShapes(all.map(s => {
      const kindOk = kinds.length === 0 || kinds.includes('kind:' + s.props.kind)
      const sessOk = sessions.length === 0 || sessions.includes('session:' + s.props.session)
      const visible = kindOk && sessOk
      if (!visible) hiddenIds.add(s.id)
      return { id: s.id, type: 'forager' as const, opacity: visible ? 1 : 0 }
    }))
    const stillSelected = editor.getSelectedShapeIds().filter(id => hiddenIds.has(id))
    if (stillSelected.length) editor.deselect(...stillSelected)
  }
  function toggleChip(key: string) {
    const next = new Set<string>(focused)
    if (next.has(key)) next.delete(key); else next.add(key)
    setFocused(next); applyFilters(next)
  }

  async function search() {
    const text = q.trim()
    if (!text || busy) return                       // EXPLICIT submit only (the don't: no keystroke search)
    setBusy(true); setNote(null)
    try {
      const r = await api.corpusQuery(text, space || null, 16)
      if (r?.error) { setNote({ kind: 'err', text: '✕ ' + r.error }); return }   // loud, never swallowed
      const hits = Array.isArray(r?.hits) ? r.hits : []
      if (hits.length === 0) {
        // A3 · the HONEST EMPTY — the backend's note (embedder down) rendered as-is, or the plain
        // "nothing returned" state. Never an empty silence.
        setNote({ kind: 'empty', text: r?.note ? '⚠ ' + r.note : `nothing returned for “${text}” in ${space || 'the corpus'}` })
        return
      }
      const { created, pulsed } = placeForagerHits(editor, hits)
      applyFilters(focused)                         // a fresh circle respects any live chip filter
      setNote({
        kind: 'info',
        text: `${hits.length} hit${hits.length === 1 ? '' : 's'} — ${created} new circle${created === 1 ? '' : 's'}` +
          (pulsed ? ` · ${pulsed} re-hit pulsed` : '') + (r?.note ? ` · ⚠ ${r.note}` : ''),
      })
    } catch (e: any) {
      setNote({ kind: 'err', text: '✕ ' + (e?.message || e) })  // transport break — loud
    } finally { setBusy(false) }
  }

  // the chip rows — value→count over the live set (real index fields: kind, session)
  const counts = new Map<string, number>()
  for (const s of shapes) {
    if (s.props.kind) counts.set('kind:' + s.props.kind, (counts.get('kind:' + s.props.kind) || 0) + 1)
    if (s.props.session) counts.set('session:' + s.props.session, (counts.get('session:' + s.props.session) || 0) + 1)
  }
  const chips = [...counts.entries()].sort((a, b) => a[0].localeCompare(b[0]))

  return (
    <div className={'hud rhm forager-bar' + (min ? ' min' : '')} data-ui-ref="ui://forager">
      <div className="rhm-head">
        forager <span className="muted">· search the corpus → circles{shapes.length ? ` · ${shapes.length} on canvas` : ''}</span>
        <span className="rhm-min" data-ui-ref="ui://forager/minimize"
          title={min ? 'expand the forager' : 'minimize the forager'}
          onClick={() => setMin(m => !m)}>{min ? '▢' : '▁'}</span>
      </div>
      <div className="rhm-input">
        <input placeholder="search the corpus — hits land as circles" data-ui-ref="ui://forager/input"
          value={q} onChange={e => setQ(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') search() }} />
        <select value={space} onChange={e => setSpace(e.target.value)}
          title="the space to search — the registry's embeddable projections">
          {spaces.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <button className="b" data-ui-ref="ui://forager/search" onClick={search} disabled={busy}>{busy ? '…' : '→'}</button>
      </div>
      {note && (note.kind === 'empty'
        ? <EmptyState>{note.text}</EmptyState>
        : <div className={'forager-note' + (note.kind === 'err' ? ' err' : '')}>{note.text}</div>)}
      {chips.length > 0 && (
        <div className="forager-chips">
          {chips.map(([key, n]) => {
            const [facet, ...rest] = key.split(':')
            const val = rest.join(':')
            const on = focused.has(key)
            return (
              <button key={key} className={'forager-chip' + (on ? ' on' : '')}
                title={on ? `release ${facet} ${val} (show everything again)` : `focus ${facet} ${val} — hide the non-matching circles (filter, not delete)`}
                onClick={() => toggleChip(key)}>
                {facet === 'kind' ? '◆' : '↳'} {val}<span className="n">{n}</span>
              </button>
            )
          })}
          <button className="forager-chip fc-clear" data-ui-ref="ui://forager/clear"
            title="remove every forager circle (graph nodes untouched — the clear filters type==='forager' only)"
            onClick={() => { const n = clearForagerShapes(editor); setFocused(new Set()); setNote({ kind: 'info', text: `${n} circle${n === 1 ? '' : 's'} cleared — graph untouched` }) }}>
            ✕ clear circles
          </button>
        </div>
      )}
    </div>
  )
}
