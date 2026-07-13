import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// THE OPERATOR APP — K1: ~/company/operator/app, served by the bridge at /app (B1).
// Tooling mirrors surface/app (the proven quarry: vite + React 18.3.1 — the DS pins 18.3.1).
// Port 5175 (canvas/app keeps 5173, surface/app keeps 5174). Same bridge (:8770) over /api.
//
// DS-SERVING DECISION (K0 §3, documented): the DS is NOT copied/symlinked into public/
// (a symlink under public/ would make vite COPY the whole DS into dist — a second home,
// the drift the DS constitution exists to prevent). Instead the BRIDGE serves the one
// DS home (design/claude-ds) at /ds/* (see runtime/bridge.py), and this dev server
// PROXIES /ds → the bridge — so dev and the built app reference the SAME /ds/* URLs,
// one home, zero copies. Consequence (honest): `npm run dev` needs the bridge up on
// :8770, exactly like /api already does.
export default defineConfig({
  plugins: [react()],
  // Served by the bridge under /app/ (B1) — assets resolve as /app/assets/*.
  base: '/app/',
  server: {
    host: '127.0.0.1',
    port: Number(process.env.VITE_DEV_PORT) || 5175,
    // No fs.allow reach into design/claude-ds (there was one, for the now-closed bundle-stale-chrome
    // tension — AGENTS.md — while AppShell/List/Toast were imported AS SOURCE). Every DS component now
    // comes through ds() → the compiled _ds_bundle.js, served same-origin over the /ds proxy below —
    // vite never needs to read the DS's source tree.
    proxy: {
      // /api = the Suite/bridge face (the same thick contract canvas/app + surface/app use).
      '/api': process.env.VITE_API_TARGET || 'http://127.0.0.1:8770',
      // /ds = the DS home served by the bridge (see the decision note above).
      '/ds': process.env.VITE_API_TARGET || 'http://127.0.0.1:8770',
      // DEV-ONLY compensation (verified by use, 2026-07-13): vite DEV prepends `base` (/app/) to
      // root-absolute URLs in index.html — the stylesheet link becomes /app/ds/styles.css and the
      // SPA fallback serves it as text/html (an unstyled page). `vite build` leaves the URL
      // UNCHANGED (dist/index.html keeps /ds/styles.css), so this asymmetry is dev's alone —
      // rewrite /app/ds/* back to the bridge's /ds/* here, and both paths hit the one DS home.
      '/app/ds': {
        target: process.env.VITE_API_TARGET || 'http://127.0.0.1:8770',
        rewrite: (p: string) => p.replace(/^\/app\/ds/, '/ds'),
      },
    },
  },
})
