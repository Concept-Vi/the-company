// THE CHROME — the DS AppShell (nav rail desktop / tab bar mobile, tokens/controls.css +
// tokens/device.css) framing the view set. Nav: Arrival · Inbox · Chat · Channels — Arrival
// (B2) and Inbox (I1, the needs-me registry fold) are real; Chat/Channels still render the
// honest .state-block empty state (K3 order).
// Header: title + the theme/density dials (U6 Segmented) — three-way data-theme +
// data-density setters on <html>; the DS axes do all the styling work from there.
import { useEffect, useState } from 'react'
import { ds } from './ds'
// U6 chrome landed after the last bundle compile — source import from the one DS home
// (see AGENTS.md for the bundle-stale tension; CSS still rides only /ds/styles.css).
import type React from 'react'
import { AppShell as AppShellDS } from '../../../design/claude-ds/components/AppShell.jsx'
// The DS ships real .d.ts files beside these sources, but their `React.HTMLAttributes`
// inheritance doesn't resolve from OUTSIDE the DS dir (no node_modules there), which
// erases `children` from the prop type. Loosen locally — runtime shape is unchanged.
const AppShell = AppShellDS as unknown as React.ComponentType<Record<string, unknown>>
import Arrival from './views/Arrival'
import Inbox from './views/Inbox'
import NotBuilt from './views/NotBuilt'
import { installAddressCapture, installPointerBridge } from './lib/address'

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
  const { Card, Segmented } = ds()
  const [active, setActive] = useState('arrival')
  const [theme, setTheme] = useState(document.documentElement.getAttribute('data-theme') || 'light')
  const [density, setDensity] = useState(document.documentElement.getAttribute('data-density') || 'comfortable')

  useEffect(() => {
    // the harvested address spine — clicks on data-ui-ref elements route to the one sink
    installAddressCapture()
    installPointerBridge()
  }, [])

  const header = (
    // flexWrap: at phone width the two dials wrap under the title instead of overlapping it
    // (found by LOOKING at the phone-width shot; .cv-appbar's min-height lets the bar grow).
    <div className="cv-appbar" style={{ display: 'flex', alignItems: 'center', gap: 'var(--s-4)', flexWrap: 'wrap' }}>
      <span className="cv-appbar__title" style={{ flex: 1 }}>
        Operator
      </span>
      <Segmented
        aria-label="Theme"
        options={THEMES}
        value={theme}
        onChange={(v: string) => {
          setTheme(v)
          setAxis('data-theme', v)
        }}
      />
      <Segmented
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
