// RG8 · THE PROPOSAL-BATCH SURFACE — the operator's floor for the registry-generation chain.
//
// WHAT THIS IS (build-prep/registry-generation, RG8): the surface where the swarm's PROPOSED registry
// dossiers (the register_element output_schema — IMPLEMENTATION-GUIDE.md §"The register_element role")
// land for one operator review. The chain reads the mockups → maps → reduces → confirms → and surfaces
// the confirmed set HERE as ONE batch. Tim walks the proposed entries, skips the ones he doesn't want,
// and APPROVES ONCE (simple-consent) → the write-back (RG9) fires. Reject/close → nothing is written.
//
// WHY IT IS SHAPED THIS WAY (the laws this file obeys):
//   · OPERATOR-ONLY FLOOR (the consent model) — the chain PROPOSES; it NEVER auto-writes addresses.json.
//     This surface is that floor made visible: nothing is written until the operator clicks approve. There
//     is exactly ONE approve gate for the whole batch (RG8: "approve once"), and per-entry SKIP only — no
//     per-entry approve button (that would be a different, per-row consent model than RG8 specifies).
//   · NO-FICTION made VISIBLE — every dossier carries a `maps_to_feature` field that is either a real
//     feature-inventory id OR the literal "proposed" (an un-built, mockup-only element). The surface renders
//     that as a TAG ("proposed (not built)" vs the feature id) so the operator SEES which proposals are
//     grounded in a built feature and which are speculative — the no-fiction signal, not buried in JSON.
//   · NOT A JSON WALL (RG8 FORM) — each dossier reads in PLAIN language: represents + howto{what /
//     what_you_can_do / how_to_change} at the operator's altitude, grouped by their parent surface. The raw
//     ui:// address is the machine locus (kept as a title tooltip / data-ui-ref), never the headline a
//     non-developer reads.
//   · ONE LANGUAGE — composes the SHARED KIT (components/kit.tsx: Surface / SectionHead / LaneHead / Badge /
//     EmptyState) and the studio token-slots (--studio-* CSS variables), so it reads as the same product
//     surface as the Review studio. No bespoke element, no off-token literal colour (inline styles read from
//     the corpus token vars, mirroring how StudioKit's Stage uses var(--acc, …)).
//   · REFLECTS-NEVER-OWNS — the proposals are READ TRUTH from the backend (the confirmed set the cascade
//     produced); the only LOCAL state this surface holds is transient review state (which entries the
//     operator has skipped this session). The skip set is sent WITH the approve so the floor records intent.
//
// WIRING (the seams):
//   · useRegistryProposals() — a SELF-CONTAINED controller hook (kept in THIS file, file-disjoint from the
//     shared useAppController during the parallel build). It fetches the proposed batch from the follow-on
//     backend route GET /api/registry/proposals and exposes an approve handler POST /api/registry/approve.
//   · BACKEND ROUTES ARE A FOLLOW-ON (RG8/RG9 backend lane). Until they exist the GET resolves to an honest
//     EmptyState (no fabricated dossiers — no-fiction: a fixture must NEVER ship as the live source) and the
//     approve handler surfaces the route's response/error. This component is the FORM half; the route + the
//     write-back it triggers are RG9's backend lane (noted, not stubbed-as-real).
import { useState, useEffect, useCallback } from 'react'
import { Surface, SectionHead, LaneHead, Badge, EmptyState } from './kit'

// ─────────────────────────────────────────────────────────────────────────────────────────────────────
// THE DOSSIER SHAPE — register_element's output_schema (IMPLEMENTATION-GUIDE.md §47-55). This is the
// CONTRACT between the cognition chain (which produces it) and this surface (which renders it). Frozen by
// [C]'s RG3 role; rendered here. A registration is a PROPOSED ui:// address + the at-altitude dossier.
export type RegistryHowto = {
  what: string              // what this surface IS, in plain language
  what_you_can_do: string   // what the operator can do with it
  how_to_change: string     // what changing it would touch / mean
}
export type RegistryDossier = {
  address: string                       // the PROPOSED ui:// address (nested under the parent)
  represents: string                    // the short label (like the 82's "RUN-run")
  howto: RegistryHowto                  // the at-altitude trio (what / what_you_can_do / how_to_change)
  capabilities: string[]                // from the real capability vocabulary, NOT invented
  maps_to_feature: string               // a feature-inventory id OR the literal "proposed" (un-built)
  grounding: 'built' | 'proposed' | 'uncertain' | 'defer'  // the no-confidence TAG (the RG3 schema change:
                                        // the float was flat noise; the discrete state carries the signal)
  // OPTIONAL provenance/flags the confirm step (RG6) may attach — rendered if present, never required.
  parent_address?: string | null        // the registered ancestor it nests under (the grouping key)
  mockup_file?: string | null           // which mockup it was read from (a secondary group hint)
  flagged?: boolean                      // RG6 marked it for extra scrutiny (low-confidence / variance)
  flag_reason?: string | null           // why it was flagged (shown so the operator knows what to check)
}

// the batch envelope the GET returns. `batch_id` is the handle the approve posts back (so the floor
// resolves THIS batch). Fail-loud: an `error` field surfaces a backend problem rather than a blank surface.
export type ProposalBatch = {
  batch_id: string | null
  proposals: RegistryDossier[]
  error?: string | null
}

const J = { 'Content-Type': 'application/json' }

// ─────────────────────────────────────────────────────────────────────────────────────────────────────
// useRegistryProposals — the SELF-CONTAINED controller hook (file-disjoint from useAppController during the
// parallel build). It binds the surface to the backend's confirmed proposal batch + the approve floor.
//   reads:  GET  /api/registry/proposals  → ProposalBatch (the confirmed set the cascade produced)
//   emits:  POST /api/registry/approve     → { approve: true, batch_id, skip: [address…] } (the write-back trigger)
// reflects-never-owns: the proposals are backend truth; the hook holds only fetch/approve transient state.
export function useRegistryProposals() {
  const [batch, setBatch] = useState<ProposalBatch>({ batch_id: null, proposals: [] })
  const [loading, setLoading] = useState(false)
  const [approving, setApproving] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    setNotice(null)
    try {
      const r = await fetch('/api/registry/proposals')
      if (!r.ok) {
        // the route is a FOLLOW-ON (RG8/RG9 backend lane) — a 404 is the honest "not built yet" state, not
        // an error to alarm the operator. Any OTHER non-2xx is surfaced as a fail-loud notice.
        if (r.status === 404) { setBatch({ batch_id: null, proposals: [] }); return }
        let body: any = null
        try { body = await r.json() } catch { /* non-JSON error body */ }
        const msg = (body && body.error) ? body.error : `${r.status} ${r.statusText || 'request failed'}`
        setBatch({ batch_id: null, proposals: [], error: msg })
        return
      }
      const data: any = await r.json()
      // tolerate either {proposals:[…]} envelope or a bare array (the route's exact shape is a follow-on).
      const proposals: RegistryDossier[] = Array.isArray(data) ? data : (data?.proposals || [])
      setBatch({ batch_id: data?.batch_id ?? null, proposals, error: data?.error ?? null })
    } catch (e: any) {
      // network failure (fetch rejects) — fail loud, never a silent empty surface.
      setBatch({ batch_id: null, proposals: [], error: String(e?.message || e) })
    } finally {
      setLoading(false)
    }
  }, [])

  // the ONE batch approve (simple-consent). `skip` = the addresses the operator removed from this batch;
  // they are NOT written. The backend write-back (RG9) merges the KEPT entries into addresses.json + stamps
  // the mockups + re-runs parse.py. Reject/close fires NOTHING (no call = no write — the consent invariant).
  const approve = useCallback(async (skip: string[]) => {
    setApproving(true)
    setNotice(null)
    try {
      const r = await fetch('/api/registry/approve', {
        method: 'POST', headers: J,
        body: JSON.stringify({ approve: true, batch_id: batch.batch_id, skip }),
      })
      if (!r.ok) {
        let body: any = null
        try { body = await r.json() } catch { /* non-JSON */ }
        const msg = (body && body.error) ? body.error
          : r.status === 404 ? 'the approve route is not wired yet (RG9 backend follow-on).'
          : `${r.status} ${r.statusText || 'approve failed'}`
        setNotice('could not approve — ' + msg)
        return { ok: false, error: msg }
      }
      const data: any = await r.json().catch(() => ({}))
      const kept = batch.proposals.length - skip.length
      setNotice('✓ approved ' + kept + ' registration(s) — the registry grows + the elements get addressed.')
      await refresh()  // re-read: an approved batch should clear (the floor consumed it)
      return { ok: true, data }
    } catch (e: any) {
      const msg = String(e?.message || e)
      setNotice('could not approve — ' + msg)
      return { ok: false, error: msg }
    } finally {
      setApproving(false)
    }
  }, [batch.batch_id, batch.proposals.length, refresh])

  useEffect(() => { void refresh() }, [refresh])

  return { batch, loading, approving, notice, refresh, approve }
}

// ─────────────────────────────────────────────────────────────────────────────────────────────────────
// the proposed-vs-feature TAG — the no-fiction signal made visible. A real feature id → a "wire" (grounded)
// badge naming the feature; the literal "proposed" → an "await" (amber, needs-extra-scrutiny) "not built"
// badge. The operator reads, by sight, which proposals are grounded in a built feature.
function FeatureTag({ mapsToFeature }: { mapsToFeature: string }) {
  const proposed = !mapsToFeature || mapsToFeature === 'proposed'
  return proposed
    ? <Badge tone="await">proposed · not built</Badge>
    : <Badge tone="wire">maps to: {mapsToFeature}</Badge>
}

// the grounding pill — the no-confidence discrete state (built > proposed > uncertain > defer).
// 'uncertain' and a panel flag read as needs-extra-scrutiny; 'built' reads as grounded.
function GroundingTag({ grounding, flagged }: { grounding: RegistryDossier['grounding']; flagged?: boolean }) {
  const scrutiny = flagged || grounding === 'uncertain'
  const tone = scrutiny ? 'fail' : grounding === 'built' ? 'sig' : 'await'
  return <Badge tone={tone}>{scrutiny ? '⚑ ' : ''}{grounding}</Badge>
}

// ONE PROPOSED DOSSIER — rendered in PLAIN language (NOT raw JSON). represents is the headline; the howto
// trio reads at the operator's altitude; the tags carry the no-fiction + confidence signals; the raw ui://
// address is the machine locus (title tooltip + data-ui-ref), never the headline a non-developer reads.
function DossierCard({ d, skipped, onToggleSkip }: {
  d: RegistryDossier; skipped: boolean; onToggleSkip: () => void
}) {
  return (
    <Surface
      tone={skipped ? 'dim' : d.flagged || d.grounding === 'uncertain' ? 'fail' : 'wire'}
      className={'rgp-dossier' + (skipped ? ' is-skipped' : '')}
      title={d.address}
      dataUiRef={d.address}
    >
      <div className="rgp-dossier-head" style={{ display: 'flex', alignItems: 'baseline', gap: 8, flexWrap: 'wrap' }}>
        <span className="rgp-represents" style={{ fontWeight: 600 }}>{d.represents || '(unnamed surface)'}</span>
        <FeatureTag mapsToFeature={d.maps_to_feature} />
        <GroundingTag grounding={d.grounding} flagged={d.flagged} />
        {/* per-entry SKIP only (RG8: no per-entry approve — the approve is the ONE batch gate). Skipping
           removes this entry from what the batch will write; it stays visible (dimmed), reversible. */}
        <button
          type="button"
          className="rgp-skip b sm"
          style={{ marginLeft: 'auto' }}
          title={skipped ? 'keep this registration in the batch' : 'skip this one — it will NOT be written when you approve the batch'}
          onClick={onToggleSkip}
        >
          {skipped ? '↺ keep' : '✕ skip'}
        </button>
      </div>

      {/* the howto trio — the at-altitude plain-language read (the 82's voice), NOT a JSON dump. */}
      <dl className="rgp-howto" style={{ margin: '6px 0 0', display: 'grid', gap: 4 }}>
        {d.howto?.what && (
          <div className="rgp-howto-row">
            <dt className="muted" style={{ fontSize: '0.85em' }}>what this is</dt>
            <dd style={{ margin: 0 }}>{d.howto.what}</dd>
          </div>
        )}
        {d.howto?.what_you_can_do && (
          <div className="rgp-howto-row">
            <dt className="muted" style={{ fontSize: '0.85em' }}>what you can do</dt>
            <dd style={{ margin: 0 }}>{d.howto.what_you_can_do}</dd>
          </div>
        )}
        {d.howto?.how_to_change && (
          <div className="rgp-howto-row">
            <dt className="muted" style={{ fontSize: '0.85em' }}>how to change it</dt>
            <dd style={{ margin: 0 }}>{d.howto.how_to_change}</dd>
          </div>
        )}
      </dl>

      {/* capabilities — from the real vocabulary (not invented). Shown as small pills so they read by sight. */}
      {d.capabilities?.length > 0 && (
        <div className="rgp-caps" style={{ marginTop: 6, display: 'flex', gap: 4, flexWrap: 'wrap' }}>
          {d.capabilities.map((c, i) => (
            <span key={c + '·' + i} className="rgp-cap kit-badge kit-tone-dim">{c}</span>
          ))}
        </div>
      )}

      {/* RG6 flag detail — why this entry needs extra scrutiny (shown only when the confirm step flagged it). */}
      {d.flagged && d.flag_reason && (
        <div className="rgp-flag muted" style={{ marginTop: 6, fontSize: '0.85em' }}>
          ⚑ flagged for review: {d.flag_reason}
        </div>
      )}
    </Surface>
  )
}

// ─────────────────────────────────────────────────────────────────────────────────────────────────────
// THE REGION — the batch-review surface. Groups the proposed dossiers by their parent (ancestor) surface
// so the operator reviews a screen's proposed elements together (dossiers nest — the parent is the natural
// grouping; falls back to the mockup file, then to a single lane). ONE batch approve at the foot.
export function RegistryProposals({ controller }: { controller?: ReturnType<typeof useRegistryProposals> }) {
  // allow an injected controller (so a parent can host the hook) but default to the self-contained one.
  const own = useRegistryProposals()
  const { batch, loading, approving, notice, refresh, approve } = controller ?? own

  // transient review state: the addresses the operator has SKIPPED this session (not written on approve).
  const [skipped, setSkipped] = useState<Set<string>>(new Set())
  const toggleSkip = useCallback((addr: string) => {
    setSkipped(prev => {
      const next = new Set(prev)
      if (next.has(addr)) next.delete(addr); else next.add(addr)
      return next
    })
  }, [])

  const proposals = batch.proposals || []
  const keptCount = proposals.filter(p => !skipped.has(p.address)).length

  // GROUP by parent/ancestor address (dossiers nest); fall back to the mockup file; then a single lane.
  // (Grouping is the plain "review a screen's elements together" — not an engineered taxonomy.)
  const groups: { key: string; label: string; items: RegistryDossier[] }[] = []
  const index: Record<string, number> = {}
  for (const p of proposals) {
    const key = p.parent_address || p.mockup_file || 'ungrouped'
    if (index[key] == null) {
      index[key] = groups.length
      const label = p.parent_address
        ? p.parent_address.replace(/^ui:\/\//, '')   // strip the scheme — plain words on the operator face
        : p.mockup_file || 'other proposed surfaces'
      groups.push({ key, label, items: [] })
    }
    groups[index[key]].items.push(p)
  }

  async function onApprove() {
    // the ONE consent commit — only the KEPT entries are written; the skipped set is excluded.
    await approve(Array.from(skipped))
  }

  return (
    <div className="rgp" data-ui-ref="ui://registry/proposals">
      <SectionHead
        tag="registry · proposed for your review"
        aside={
          <button type="button" className="b sm" data-ui-ref="ui://registry/proposals/refresh"
            disabled={loading} title="re-read the proposed batch from the chain"
            onClick={() => { void refresh() }}>
            {loading ? '…' : '↻ refresh'}
          </button>
        }>
        new registry entries
      </SectionHead>

      {/* the standing read: how many proposals, how many will be written (kept), the no-fiction note. */}
      <div className="rgp-stat" style={{ display: 'flex', gap: 8, alignItems: 'center', margin: '4px 0 10px' }}>
        <Badge tone={proposals.length ? 'await' : 'dim'}>{proposals.length} proposed</Badge>
        {proposals.length > 0 && <span className="muted">· {keptCount} will be written · {skipped.size} skipped</span>}
      </div>

      {/* fail-loud surfaces — a backend error or the approve notice, never swallowed. */}
      {batch.error && <EmptyState>could not load the proposals — {batch.error}</EmptyState>}
      {notice && <div className="rgp-notice muted" style={{ margin: '0 0 8px' }} data-ui-ref="ui://registry/proposals/notice">{notice}</div>}

      {/* the honest rest-state: the chain hasn't surfaced a batch (or the route is a follow-on). NOT a blank. */}
      {!batch.error && !loading && proposals.length === 0 && (
        <EmptyState>
          no registry proposals awaiting you. when the registry-generation chain runs over the mockups and
          confirms a set, the proposed entries appear here for one approve.
        </EmptyState>
      )}

      {/* THE GROUPED PROPOSED DOSSIERS — each surface's proposed elements together. */}
      {groups.map((g) => (
        <div className="rgp-group" key={g.key}>
          <LaneHead tone="wire" count={g.items.length}>{g.label}</LaneHead>
          {g.items.map((d) => (
            <div className="rgp-dossier-wrap" key={d.address}>
              <DossierCard d={d} skipped={skipped.has(d.address)} onToggleSkip={() => toggleSkip(d.address)} />
            </div>
          ))}
        </div>
      ))}

      {/* THE ONE APPROVE GATE (RG8: approve once → the write-back fires; reject/close → nothing written).
         simple-consent: one button, the whole kept batch. Disabled when there is nothing to write. */}
      {proposals.length > 0 && (
        <div className="rgp-foot" data-ui-ref="ui://registry/proposals/approve-bar"
          style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 12, paddingTop: 10, borderTop: '1px solid var(--studio-card-border, rgba(255,255,255,0.08))' }}>
          <button
            type="button"
            className="b"
            data-ui-ref="ui://registry/proposals/approve"
            disabled={approving || keptCount === 0}
            title="approve this batch — the kept registrations are written to the registry + the elements get addressed. nothing runs until you click this."
            onClick={() => { void onApprove() }}
          >
            {approving ? '… writing' : `✓ approve ${keptCount} registration${keptCount === 1 ? '' : 's'}`}
          </button>
          <span className="muted" style={{ fontSize: '0.85em' }}>
            nothing is written until you approve · skipped entries are excluded.
          </span>
        </div>
      )}
    </div>
  )
}

export default RegistryProposals
