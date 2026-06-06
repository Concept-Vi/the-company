// F8 · the FLEET SURFACE — the live model layer made visible (model · kind · alive), addressed ui://models.
//
// WHY (fe-map §1 GAP): the system had NO fleet/crew surface — the live model registry (the fabric layer the
// brain authors from) was invisible on the canvas. F8 paints it as a navigable panel, NOT a text dump.
//
// SOURCE OF TRUTH (rule 8, author-from-registry): every row IS a model the live registry returned for that
// kind (api.models('chat') / api.models('embed') → /api/models → suite.models_at → fabric transport.list_models).
// Nothing here is hardcoded; the controller's `fleet` state is the registry response, refreshable live.
//
// WHAT "alive" HONESTLY MEANS: the registry exposes model NAMES per endpoint, NOT a per-model heartbeat
// (verified: suite.available_models / models_at return a list of name strings, no liveness field). So a model
// PRESENT in the live registry list IS the live fleet for its kind — that is the honest "alive" signal (it's
// registered + reachable at the endpoint right now). We do NOT fabricate a per-model up/down dot (that would
// be rule-8 confabulation + a silent fallback). The KIND-LEVEL liveness is real and shown: a kind whose
// registry fetch FAILED renders its error (fail-loud, rule 4), never a silently empty list.
//
// WAVE-? REGION-BATCH-2 (FULL conversion, A1/H) — CLASS-B region: redesigned from prototype-grade (bare
// .fleet-head/.fleet-row markup) into the commander's-bridge language composed from the SHARED KIT
// (components/kit.tsx, H2), following the Palette exemplar almost 1:1 (models-grouped-by-kind reads exactly
// like Palette's node-types-grouped-by-kind). A kit SectionHead (display voice) with the live fleet size as
// an aside Badge + the live-reprobe refresh; a kit LaneHead per kind (count chip); each model is a kit
// <Surface> card (non-clickable — a model has no per-model action) with a kind monogram (the same monogram
// language Palette uses) + the honest live-registry dot. A failed endpoint surfaces as a kit <Surface
// tone="fail"> (the same fail-loud card Grow uses), never a
// bespoke error block. The thin .fleet-* layer is LAYOUT-ONLY now (the dot, the monogram, the legend) — the
// look lives in .kit-* (kit is the sole authority). PRESERVED (the function half): the registry source of
// truth, the per-kind fail-loud error, the honest dot + legend (registry-membership, not a health probe),
// the live refresh, data-ui-ref="ui://models".
//
// SOURCE OF TRUTH (rule 8): every row IS a model the live registry returned; nothing here is hardcoded.
// ADDRESSABLE (S1): ui://models is registered in design/_system/addresses.json; this panel carries the
// matching data-ui-ref so the registered address resolves to a real DOM element.
import { SectionHead, LaneHead, Badge, Surface, EmptyState } from '../components/kit'
import { useApp } from '../AppContext'

// the kind language: chat/embed map to the kit lane + spine + monogram colour (the same tones the canvas
// node-cards + the Palette rack wear), so the fleet reads as one vocabulary with the rest of the deck.
const KIND_TONE: Record<string, 'sig' | 'wire' | 'dim'> = { chat: 'sig', embed: 'wire' }

// one kind's group — its lane header (count), the model rows it returned, and any fail-loud error.
function FleetKind({ kind, models, err }: { kind: string; models: string[]; err: string }) {
  const tone = KIND_TONE[kind] || 'dim'
  return (
    <div className="fleet-kind">
      <LaneHead tone={err ? 'fail' : tone} count={err ? undefined : models.length}>{kind}</LaneHead>
      {/* fail-loud (rule 4): a down/unconfigured endpoint surfaces its error as a kit fail-tone Surface
         (the SAME card Grow uses for its build error) — never a silently blank group. */}
      {err
        ? <Surface tone="fail" className="fleet-err">⚠ {err}</Surface>
        : models.length === 0
          ? <EmptyState>no models registered at the {kind} endpoint.</EmptyState>
          : models.map(name => (
              // each model is a kit Surface card: a kind monogram + the model name + the honest live dot. The
              // spine carries the kind tone, so the card's tint IS its kind (read by sight). NON-clickable by
              // design — a model has no per-model action, so no onClick/interactive (no false affordance).
              <Surface key={kind + ':' + name} tone={tone} className="fleet-row" title={name}>
                <span className={'fleet-mono fleet-mono-' + tone}>{name.slice(0, 2).toUpperCase()}</span>
                <span className="fleet-name">{name}</span>
                {/* the live-registry dot: a model in the list IS the live fleet (registry-is-truth). The
                   tooltip states the HONEST meaning so it is not misread as a per-model health probe (which
                   the registry does not expose): listed-now = live; a down model DROPS OUT of the list. */}
                <span className="fleet-dot" title="listed in the live registry — a down model drops out of this list" />
              </Surface>
            ))}
    </div>
  )
}

export function Fleet() {
  const { fleet, refreshFleet } = useApp()
  // total live models across kinds — the panel's at-a-glance fleet size (kinds with an error contribute 0).
  const total = (fleet.chatErr ? 0 : fleet.chat.length) + (fleet.embedErr ? 0 : fleet.embed.length)
  return (
    <div className="fleet" data-ui-ref={'ui://models'}>
      {/* the HEAD — display-voice title; the live fleet size reads as a Badge (sig); the live-reprobe refresh
         re-queries the registry without a restart (suite.models_at is uncached). */}
      <SectionHead tag="the live model layer"
        aside={<>
          {fleet.loaded
            ? <Badge tone="sig">{total} live</Badge>
            : <Badge tone="dim">loading…</Badge>}
          <button className="b ghost sm fleet-refresh"
            onClick={() => refreshFleet()} title="re-probe the live model registry">↻</button>
        </>}>
        fleet
      </SectionHead>
      <div className="fleet-body">
        <FleetKind kind="chat" models={fleet.chat} err={fleet.chatErr} />
        <FleetKind kind="embed" models={fleet.embed} err={fleet.embedErr} />
      </div>
      {/* visible legend (not just a tooltip): the dot's HONEST meaning, so 'alive' reads as registry
         membership — a coarse-but-real liveness signal — not a per-model health probe we don't have. */}
      <div className="fleet-legend"><span className="fleet-dot" /> listed in the live registry · a down model drops out</div>
    </div>
  )
}
