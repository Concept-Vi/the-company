// BOOT ORDER (load-bearing): the DS bundle consumes React as a window global, and every
// component in this app calls ds() synchronously at render — so the DS door MUST be open
// before the first ReactDOM render. bootDS() sets window.React/ReactDOM (our pinned
// 18.3.1 — one React instance), loads /ds/_ds_bundle.js, and imports the sanctioned
// /ds/index.js door. A boot failure renders the DS's own .state-block loudly — the app
// never silently mounts unstyled or component-less (claude-ds CLAUDE.md §3).
import React from 'react'
import ReactDOM from 'react-dom/client'
import { bootDS } from './ds'
import { mintOperatorSession } from './lib/api'

async function main() {
  const rootEl = document.getElementById('root')
  if (!rootEl) throw new Error('[operator-app] #root missing from index.html')
  // #1b: mint the per-process operator-session token ALONGSIDE the DS boot (not blocking first
  // paint on it — enforcement is flag-gated off today, so a mint failure must not brick the app).
  // Loud in the console either way (no-silent-failures) — never swallowed into nothing.
  void mintOperatorSession().catch((e: unknown) =>
    console.warn('[operator-app] /api/operator-session mint failed — POSTs will carry no token:', e),
  )
  try {
    await bootDS()
  } catch (e) {
    rootEl.innerHTML = `
      <div class="state-block" role="alert">
        <div class="glyph" aria-hidden="true">⚠</div>
        <div class="title">The design system did not load</div>
        <div class="body">${String((e as Error).message || e).replace(/</g, '&lt;')}</div>
      </div>`
    throw e // fail loud in the console too — never a silent degraded shell
  }
  const { default: App } = await import('./App')
  ReactDOM.createRoot(rootEl).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  )
}

void main()
