import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// THE FRESH INSTRUMENT SURFACE — a sibling app to canvas/app, NEVER on top of it.
// Default port 5174 (canvas/app keeps 5173, the live PWA). Same bridge (:8770) over /api.
// Env-overridable so an isolated session can point at its own bridge without touching the live one.
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: Number(process.env.VITE_DEV_PORT) || 5174,
    // Reach the dev server over Tailscale HTTPS (tailnet-only; Tim's phone) — same allowance as canvas/app.
    allowedHosts: ['.tail777bc2.ts.net'],
    // /api = the Suite/bridge face (the SAME thick contract canvas/app uses — we are thin over it).
    proxy: {
      '/api': process.env.VITE_API_TARGET || 'http://localhost:8770',
    },
  },
})
