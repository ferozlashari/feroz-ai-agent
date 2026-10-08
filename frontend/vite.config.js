import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Frontend /api ki saari requests backend (port 8000) ko bhej deta hai
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
})
