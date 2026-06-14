import type { SurfaceState } from '../App'
import { LensChip } from '../toggles/LensChip'
import { Settings } from '../toggles/Settings'
import { ViewToggle } from '../toggles/ViewToggle'
import { LiveDot } from '../toggles/LiveDot'
import { CentreChip } from '../toggles/CentreChip'
import { Legend } from '../toggles/Legend'
import { Notice } from '../toggles/Notice'
import { Disclosure } from '../wheel/Disclosure'
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
          {s.proj && <LensChip proj={s.proj} current={s.binding} onPick={s.setBinding} />}
          <div className="bar-right">
            <LiveDot live={s.live} setLive={s.setLive} />
            <ViewToggle view={s.view} setView={s.setView} />
            <Settings feel={s.feel} setFeel={s.setFeel} />
          </div>
        </div>
        <CentreChip centre={s.centre} onReset={() => s.setCentre(null)} />
        <div className="rail-detail">
          {s.selected ? (
            <Disclosure point={s.selected} feel={s.feel} variant="rail" onDismiss={() => s.setSelected(null)} onFocus={s.focusCentre} binding={s.proj?.binding} centreLabel={s.centre?.label} />
          ) : (
            <SelectHint />
          )}
        </div>
        <Legend s={s} />
      </aside>
    </div>
  )
}
