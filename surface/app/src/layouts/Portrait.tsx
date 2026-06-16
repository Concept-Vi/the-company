import type { SurfaceState } from '../App'
import { LensChip } from '../toggles/LensChip'
import { SpaceChip } from '../toggles/SpaceChip'
import { LayerChip } from '../toggles/LayerChip'
import { ResChip } from '../toggles/ResChip'
import { QuantChip } from '../toggles/QuantChip'
import { Settings } from '../toggles/Settings'
import { ViewToggle } from '../toggles/ViewToggle'
import { LiveDot } from '../toggles/LiveDot'
import { CentreChip } from '../toggles/CentreChip'
import { Legend } from '../toggles/Legend'
import { Scrubber } from '../toggles/Scrubber'
import { Notice } from '../toggles/Notice'
import { Disclosure } from '../wheel/Disclosure'
import { Tether } from '../wheel/Tether'
import { WheelOrState } from './shared'
import { stamp } from '../lib/address'

// MOBILE PORTRAIT (390×844): the wheel OWNS the frame; chrome is one thin top row (lens chip + gear);
// detail arrives as a bottom sheet on demand. Native to the tall frame — not a shrunk desktop. Word budget 2–4.
export function Portrait({ s }: { s: SurfaceState }) {
  return (
    <div className="layout layout--portrait">
      <Notice message={s.notice} onDismiss={s.dismissNotice} />

      <header className="bar bar--top portrait-top" {...stamp('ui://chrome/topbar')}>
        <div className="bar-left">
          {s.proj && <LensChip proj={s.proj} current={s.binding} onPick={s.setBinding} />}
          <SpaceChip proj={s.proj} space={s.space} setSpace={s.setSpace} />
          <LayerChip emb={s.emb} setEmb={s.setEmb} />
          <ResChip proj={s.proj} dim={s.dim} setDim={s.setDim} emb={s.emb} />
          <QuantChip proj={s.proj} quant={s.quant} setQuant={s.setQuant} />
        </div>
        <div className="bar-right">
          <CentreChip centre={s.centre} onReset={() => s.setCentre(null)} />
          <LiveDot live={s.live} setLive={s.setLive} />
          <ViewToggle view={s.view} setView={s.setView} />
          <Settings feel={s.feel} setFeel={s.setFeel} />
        </div>
      </header>

      {/* legend + wheel CENTRE as one group in the full vertical region (not just the post-legend slice), so the
         plate sits optically centred — no top-heavy band. (design-critic: portrait circle pushed low.) */}
      <div className="portrait-stage">
        <Legend s={s} />
        <section className="center center--full">
          <WheelOrState s={s} />
        </section>
      </div>

      <Scrubber at={s.at} setAt={s.setAt} corpusStart={s.corpusStart} now={s.now} />

      {/* detail as a bottom sheet (nonmodal, draggable handle) — nothing permanent at rest */}
      {!s.galleryOpen && <Disclosure point={s.selected} feel={s.feel} variant="sheet" onDismiss={() => s.setSelected(null)} onFocus={s.focusCentre} onSetPole={s.setPole} binding={s.proj?.binding} centreLabel={s.centre?.label} />}
      <Tether selectedSeq={s.selected?.seq} />
    </div>
  )
}
