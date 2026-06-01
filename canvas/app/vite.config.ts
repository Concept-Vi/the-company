import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The rich canvas talks to the bridge (the UI face of the Suite) over /api.
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: { '/api': 'http://localhost:8770' },
  },
})
