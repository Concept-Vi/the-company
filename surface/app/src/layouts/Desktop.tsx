import type { SurfaceState } from '../App'
import { LensChip } from '../toggles/LensChip'
import { Settings } from '../toggles/Settings'
import { Notice } from '../toggles/Notice'
import { Disclosure } from '../wheel/Disclosure'
import { WheelOrState, SelectHint } from './shared'
import { stamp } from '../lib/address'

// DESKTOP (1440×900): instrument centered + ambient side strata. Chrome is two quiet corners (lens chip
// top-left, settings gear top-right); the wheel owns the whole field. No permanent control island (fix #2/#5).
export function Desktop({ s }: { s: SurfaceState }) {
  return (
    <div className="layout layout--desktop">
      <Notice message={s.notice} onDismiss={s.dismissNotice} />

      <header className="bar bar--top" {...stamp('ui://chrome/topbar')}>
        {s.proj && <LensChip proj={s.proj} current={s.binding} onPick={s.setBinding} />}
        <Settings feel={s.feel} setFeel={s.setFeel} />
      </header>

      <main className="stage">
        <aside className="strata strata--left" {...stamp('ui://strata/left')} />

        <section className="center">
          <WheelOrState s={s} />
        </section>

        <aside className="strata strata--right" {...stamp('ui://strata/right')}>
          {s.selected ? (
            <Disclosure point={s.selected} feel={s.feel} variant="panel" onDismiss={() => s.setSelected(null)} />
          ) : (
            <SelectHint />
          )}
        </aside>
      </main>
    </div>
  )
}
