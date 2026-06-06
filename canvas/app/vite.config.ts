import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The rich canvas talks to the bridge (the UI face of the Suite) over /api.
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    // Port + /api proxy target are env-overridable (default unchanged: 5173 → :8770) so an isolated
    // worktree session can run its OWN bridge (e.g. VITE_DEV_PORT=5174 VITE_API_TARGET=http://localhost:8771)
    // without touching the live services. Backward compatible — omit the envs and behaviour is identical.
    port: Number(process.env.VITE_DEV_PORT) || 5173,
    // Allow the device to reach the dev server over Tailscale HTTPS (tailnet-only; phone access).
    allowedHosts: ['.tail777bc2.ts.net'],
    proxy: { '/api': process.env.VITE_API_TARGET || 'http://localhost:8770' },
  },
})
