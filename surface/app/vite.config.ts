import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// THE FRESH INSTRUMENT SURFACE — a sibling app to canvas/app, NEVER on top of it.
// Default port 5174 (canvas/app keeps 5173, the live PWA). Same bridge (:8770) over /api.
// Env-overridable so an isolated session can point at its own bridge without touching the live one.
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: Number(process.env.VITE_DEV_PORT) || 5174,
    // Reach the dev server over Tailscale HTTPS (tailnet-only; Tim's phone) — same allowance as canvas/app.
    // 2026-06-22: bound 0.0.0.0 (tailnet-reachable, for Tim's phone) — Tim DIRECTLY authorized the network exposure.
    // allowedHosts: true so the phone reaches it by tailnet hostname OR IP (private tailnet — his devices only).
    allowedHosts: true,
    // /api = the Suite/bridge face (the SAME thick contract canvas/app uses — we are thin over it).
    // /design = the design-system static server (:8775) proxied SAME-ORIGIN, so a design-system page
    // (e.g. the glyphgraph generator) is served as its ONE source file yet can reach /api (the bridge
    // has no CORS — this proxy is the union's transport, A4 of the Glyphic AI fusion; never copy the page).
    proxy: {
      '/api': process.env.VITE_API_TARGET || 'http://localhost:8770',
      '/design': {
        target: process.env.VITE_DESIGN_TARGET || 'http://127.0.0.1:8775',
        rewrite: (p: string) => p.replace(/^\/design/, ''),
      },
    },
  },
})
