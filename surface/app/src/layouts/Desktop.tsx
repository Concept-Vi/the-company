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

// DESKTOP (1440×900): instrument centered + ambient side strata. Chrome is two quiet corners (lens chip
// top-left, settings gear top-right); the wheel owns the whole field. No permanent control island (fix #2/#5).
export function Desktop({ s }: { s: SurfaceState }) {
  return (
    <div className="layout layout--desktop">
      <Notice message={s.notice} onDismiss={s.dismissNotice} />

      <header className="bar bar--top" {...stamp('ui://chrome/topbar')}>
        <div className="bar-left">
          {s.proj && <LensChip proj={s.proj} current={s.binding} onPick={s.setBinding} />}
          <SpaceChip proj={s.proj} space={s.space} setSpace={s.setSpace} />
          <LayerChip emb={s.emb} setEmb={s.setEmb} />
          <ResChip proj={s.proj} dim={s.dim} setDim={s.setDim} emb={s.emb} />
          <QuantChip proj={s.proj} quant={s.quant} setQuant={s.setQuant} />
          <CentreChip centre={s.centre} onReset={() => s.setCentre(null)} />
        </div>
        <div className="bar-right">
          <LiveDot live={s.live} setLive={s.setLive} />
          <ViewToggle view={s.view} setView={s.setView} />
          <Settings feel={s.feel} setFeel={s.setFeel} />
        </div>
      </header>

      <main className="stage">
        <aside className="strata strata--left" {...stamp('ui://strata/left')}>
          <Legend s={s} />
        </aside>

        <section className="center">
          <WheelOrState s={s} />
        </section>

        <aside className="strata strata--right" {...stamp('ui://strata/right')}>
          {s.selected && !s.galleryOpen ? (
            <Disclosure point={s.selected} feel={s.feel} variant="panel" onDismiss={() => s.setSelected(null)} onFocus={s.focusCentre} onSetPole={s.setPole} binding={s.proj?.binding} centreLabel={s.centre?.label} />
          ) : (
            <SelectHint />
          )}
        </aside>
      </main>
      <Scrubber at={s.at} setAt={s.setAt} corpusStart={s.corpusStart} now={s.now} />
      <Tether selectedSeq={s.selected?.seq} />
    </div>
  )
}
