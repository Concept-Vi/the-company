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
// FORM (rule 9): a navigable visual panel on the corpus design-system — reuses the right-rail .panel chrome
// (h3 / .row / .k) + the .act-* heading rhythm + corpus status tokens (--ok alive · --dim muted · --fail
// error). No off-token literals (design-lint --fail-on gates those). data-ui-ref carries the FULL registered
// corpus address "ui://models" in QUOTED form (the S1 orphan-scanner is blind to the backtick form).
//
// ADDRESSABLE (S1): ui://models is registered in the corpus address registry (design/_system/addresses.json
// → _load_corpus_element_addresses → UI_REGISTRY → /api/ui_info), region "models". This panel carries the
// matching data-ui-ref so the registered address resolves to a real DOM element.
import { useApp } from '../AppContext'

// one kind's group — its label, the model rows it returned, and any fail-loud error for that endpoint.
function FleetKind({ kind, models, err }: { kind: string; models: string[]; err: string }) {
  return (
    <div className="fleet-kind">
      <div className="fleet-kind-head">
        <span className="fleet-kind-name">{kind}</span>
        <span className="fleet-kind-count">{err ? '—' : models.length}</span>
      </div>
      {/* fail-loud (rule 4): a down/unconfigured endpoint surfaces its error here — never a blank group. */}
      {err
        ? <div className="fleet-err">⚠ {err}</div>
        : models.length === 0
          ? <div className="muted">no models registered at the {kind} endpoint</div>
          : (
            <div className="fleet-list">
              {models.map(name => (
                <div className="fleet-row" key={kind + ':' + name} title={name}>
                  {/* the live-registry dot: a model in the list IS the live fleet (registry-is-truth) —
                     coloured on the corpus --ok token. The tooltip states the HONEST meaning so the dot is
                     not misread as a per-model health probe (which the registry does not expose): green =
                     listed in the live registry now; a down model DROPS OUT of the list (or the kind errors). */}
                  <span className="fleet-dot" title="listed in the live registry — a down model drops out of this list" />
                  <span className="fleet-name">{name}</span>
                  <span className="fleet-kind-tag">{kind}</span>
                </div>
              ))}
            </div>
          )}
    </div>
  )
}

export function Fleet() {
  const { fleet, refreshFleet } = useApp()
  // total live models across kinds — the panel's at-a-glance fleet size (kinds with an error contribute 0).
  const total = (fleet.chatErr ? 0 : fleet.chat.length) + (fleet.embedErr ? 0 : fleet.embed.length)
  return (
    <div className="fleet" data-ui-ref={'ui://models'}>
      <div className="fleet-head">
        <h3 className="fleet-title">fleet</h3>
        <span className="muted">{fleet.loaded ? total + ' live · model · kind · alive' : 'loading…'}</span>
        {/* live refresh — re-probe the registry without a restart (suite.models_at is uncached). */}
        <button className="b ghost sm fleet-refresh"
          onClick={() => refreshFleet()} title="re-probe the live model registry">↻</button>
      </div>
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
