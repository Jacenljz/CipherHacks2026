import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In dev, proxy API + WebSocket to the FastAPI backend so the frontend can use
// same-origin relative URLs (which also work when FastAPI serves the build).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/ws': { target: 'ws://127.0.0.1:8000', ws: true },
    },
  },
})
