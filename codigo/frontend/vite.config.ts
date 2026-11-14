import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const backend = 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // accesible desde tablets en la red local
    proxy: {
      '/api': backend,
      '/pictos': backend,
      '/ws': { target: backend, ws: true },
    },
  },
})
