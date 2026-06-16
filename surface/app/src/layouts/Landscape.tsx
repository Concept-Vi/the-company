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
import { WheelOrState, SelectHint } from './shared'
import { stamp } from '../lib/address'

// MOBILE LANDSCAPE (844×390): wheel left (~70%), a composed right rail (~30%). The rail is balanced —
// lens chip + gear pinned top, the detail surface fills the body (a calm hint when nothing is selected),
// so it never reads as an empty panel with furniture on the floor (fix #3). Native to the wide-short frame.
export function Landscape({ s }: { s: SurfaceState }) {
  return (
    <div className="layout layout--landscape">
      <Notice message={s.notice} onDismiss={s.dismissNotice} />

      <section className="center center--left">
        <WheelOrState s={s} />
      </section>

      <aside className="rail" {...stamp('ui://strata/rail')}>
        <div className="rail-head">
          <div className="bar-left">
            {s.proj && <LensChip proj={s.proj} current={s.binding} onPick={s.setBinding} />}
            <SpaceChip proj={s.proj} space={s.space} setSpace={s.setSpace} />
            <LayerChip emb={s.emb} setEmb={s.setEmb} />
            <ResChip proj={s.proj} dim={s.dim} setDim={s.setDim} emb={s.emb} />
            <QuantChip proj={s.proj} quant={s.quant} setQuant={s.setQuant} />
          </div>
          <div className="bar-right">
            <LiveDot live={s.live} setLive={s.setLive} />
            <ViewToggle view={s.view} setView={s.setView} />
            <Settings feel={s.feel} setFeel={s.setFeel} />
          </div>
        </div>
        <CentreChip centre={s.centre} onReset={() => s.setCentre(null)} />
        <div className="rail-detail">
          {s.selected && !s.galleryOpen ? (
            <Disclosure point={s.selected} feel={s.feel} variant="rail" onDismiss={() => s.setSelected(null)} onFocus={s.focusCentre} onSetPole={s.setPole} binding={s.proj?.binding} centreLabel={s.centre?.label} />
          ) : (
            <SelectHint />
          )}
        </div>
        <Legend s={s} />
      </aside>
      <Scrubber at={s.at} setAt={s.setAt} corpusStart={s.corpusStart} now={s.now} />
      <Tether selectedSeq={s.selected?.seq} />
    </div>
  )
}
