// L6 · live-history / versions at an address (§21.7#6) · "a portal shows the CURRENT ref live; this is the
// TRAIL of values the address has HELD over time." When the operator SELECTS a node, this region shows that
// node's OUTPUT-address version history — every set_ref to it as a {cas, ts, preview} row, NEWEST-FIRST
// (GET /api/ref-versions → Suite.ref_versions → store.ref_history, the index appended on each set_ref). The
// CURRENT value (the live portal window) is marked; the prior versions' bytes survive (put_content is
// write-once) and each row previews its content. Reflects-never-owns: the runtime is authoritative; this
// region only reads.
//
// THE ADDRESS IT SHOWS (the load-bearing point — see useAppController.versionedAddress): versions accrue
// where a `set_ref` WROTE. A PORTAL never calls set_ref (RESOLVE='reference', the scheduler skips it), so a
// portal's OWN address has no history — the controller queries the address its config.ref POINTS AT. A
// compute node's own run:// `address` IS where its versions accrue. So this region shows the right trail for
// whichever node is selected; when nothing versioned is selected it renders nothing (never clutters).
//
// FORM (rule 9 — FORM is half of done): NAVIGABLE, not a raw list. Built on the design system — it REUSES the
// .ev event-row vocabulary (.ev / .ev-k / .ev-s / .ev-t, token-coloured per kind) and the thin .hist-*
// layout layer the L3 History + L5 SelfChanges regions use, so it is coherent with them by construction. The
// CURRENT version is badged (the .ev-run kind = the live signal token); prior versions read .ev-decision
// (the content token). No hardcoded colours, no bespoke element — design-lint clean (design-token classes +
// var() tokens only; the thin .ver-* layer is layout-only).
//
// Renders ONLY when a node with a versioned output address is selected (else nothing). data-ui-ref (quoted,
// per the lane rule) keeps it addressable on the surface itself.
import { relTime } from '../api'
import { SectionHead, Badge } from '../components/kit'
import { useApp } from '../AppContext'

// WAVE-? REGION-BATCH-2 (HEAD-ONLY pass, A1/H) — CLASS-A region: the `.ev`/`.ver` row body is the shared,
// designed, token-coloured vocabulary (current=ev-run signal, prior=ev-decision content) coherent with the
// L3 History + L5 SelfChanges + Activity regions — left untouched (Surface-ifying it would regress that). The
// conversion is HEAD-ONLY (the Activity pattern): a kit SectionHead in the display voice (the versioned
// address rides the kicker; the version count reads as a Badge). PRESERVED: the is_current "current"/"prior"
// kind badge, the abbreviated cas hash, newest-first ordering, the honest empty, every data-ui-ref.
export function Versions() {
  const { versions, versionsBusy } = useApp()
  if (!versions) return null                                    // nothing versioned selected — never clutters

  const addr = versions.address
  const rows = versions.versions || []                          // newest-first (backend orders it)

  return (
    <div className="hist ver" data-ui-ref="ui://inspector/versions">
      {/* the HEAD — display-voice title; the versioned address rides the kicker; the count of values this
          address has HELD reads as a Badge (the trail depth, by sight). */}
      <SectionHead tag={addr}
        aside={versionsBusy
          ? <Badge tone="dim">loading…</Badge>
          : <Badge tone={rows.length ? 'sig' : 'dim'}>{rows.length} version{rows.length === 1 ? '' : 's'} held</Badge>}>
        versions
      </SectionHead>

      {/* honest empty (rule 4): an address never written shows a true "no versions", never a silent blank. */}
      {rows.length === 0 && !versionsBusy && (
        <div className="muted">this address holds no versions yet — run the node (or its source) and each result becomes a version here.</div>
      )}

      {rows.length > 0 && (
        <div className="ev-list hist-list">
          {rows.map((v, i) => (
            // the CURRENT version reads as the live signal (ev-run token); prior versions read as content.
            <div key={v.cas ?? i} className={'ev ' + (v.is_current ? 'ev-run' : 'ev-decision') + ' ver-row'}>
              <span className="ev-k">{v.is_current ? 'current' : 'prior'}</span>
              <span className="ev-s" title={v.preview}>{v.preview}</span>
              {/* the content hash, abbreviated — the addressable identity of this version (fetchable by cas). */}
              <span className="ev-t ver-cas" title={v.cas}>{(v.cas || '').replace('cas://b2:', '').slice(0, 8)}</span>
              <span className="ev-t">{relTime(v.ts)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
