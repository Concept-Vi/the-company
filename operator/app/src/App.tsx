// THE CHROME — the DS AppShell (nav rail desktop / tab bar mobile, tokens/controls.css +
// tokens/device.css) framing the view set. Nav: Arrival · Inbox · Chat · Channels — Arrival
// (B2) and Inbox (I1, the needs-me registry fold) are real; Chat/Channels still render the
// honest .state-block empty state (K3 order).
// Header: title + the theme/density dials (U6 Segmented) — three-way data-theme +
// data-density setters on <html>; the DS axes do all the styling work from there.
import { useEffect, useState } from 'react'
import { ds } from './ds'
import Arrival from './views/Arrival'
import Inbox from './views/Inbox'
import NotBuilt from './views/NotBuilt'
import { installAddressCapture, installPointerBridge, stamp } from './lib/address'

const NAV = [
  { id: 'arrival', label: 'Arrival' },
  { id: 'inbox', label: 'Inbox' },
  { id: 'chat', label: 'Chat' },
  { id: 'channels', label: 'Channels' },
]

const THEMES = ['light', 'dim', 'dark'] // tokens/theme.css modes (three-way; contrast exists but is a later dial)
const DENSITIES = ['compact', 'comfortable', 'spacious'] // tokens/density.css knob

function setAxis(attr: 'data-theme' | 'data-density', value: string) {
  // ONE setter, on <html> — the DS's axis machinery (tokens/theme.css, tokens/density.css)
  // cascades everything else. No per-component styling ever happens here.
  document.documentElement.setAttribute(attr, value)
}

export default function App() {
  const { Card, Segmented, AppShell } = ds()
  const [active, setActive] = useState('arrival')
  const [theme, setTheme] = useState(document.documentElement.getAttribute('data-theme') || 'light')
  const [density, setDensity] = useState(document.documentElement.getAttribute('data-density') || 'comfortable')

  useEffect(() => {
    // the harvested address spine — clicks on data-ui-ref elements route to the one sink
    installAddressCapture()
    installPointerBridge()
    // AppShell (the bundle's compiled component) renders the nav rail/tab-bar buttons
    // internally — it has no per-item address prop (AGENTS.md's address-scheme note).
    // Stamp data-ui-ref onto the real DOM nodes it produced, once: NAV's order is 1:1
    // with both button lists and every button is React-keyed by `it.id`, so these nodes
    // never get recreated — one stamp at mount holds for the app's lifetime.
    const railItems = document.querySelectorAll('.cv-appshell__rail .cv-rail-item')
    const tabItems = document.querySelectorAll('.cv-appshell__tabbar .cv-tab')
    NAV.forEach((item, i) => {
      const addr = `ui://operator/nav/${item.id}`
      railItems[i]?.setAttribute('data-ui-ref', addr)
      tabItems[i]?.setAttribute('data-ui-ref', addr)
    })
  }, [])

  const header = (
    // flexWrap: at phone width the two dials wrap under the title instead of overlapping it
    // (found by LOOKING at the phone-width shot; .cv-appbar's min-height lets the bar grow).
    <div className="cv-appbar" style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-4)', flexWrap: 'wrap' }}>
      <span className="cv-appbar__title" style={{ flex: 1 }}>
        Operator
      </span>
      <Segmented
        {...stamp('ui://operator/dials/theme')}
        aria-label="Theme"
        options={THEMES}
        value={theme}
        onChange={(v: string) => {
          setTheme(v)
          setAxis('data-theme', v)
        }}
      />
      <Segmented
        {...stamp('ui://operator/dials/density')}
        aria-label="Density"
        options={DENSITIES}
        value={density}
        onChange={(v: string) => {
          setDensity(v)
          setAxis('data-density', v)
        }}
      />
    </div>
  )

  return (
    <AppShell nav={NAV} activeId={active} onNavigate={setActive} header={header}>
      {active === 'arrival' ? (
        <Arrival />
      ) : active === 'inbox' ? (
        <Inbox />
      ) : (
        <div style={{ padding: 'var(--s-6)' }}>
          <Card>
            <NotBuilt what={NAV.find((n) => n.id === active)?.label || active} />
          </Card>
        </div>
      )}
    </AppShell>
  )
}
