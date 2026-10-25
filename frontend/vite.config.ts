import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  // Usa la misma dirección visible para React y las cookies del backend en desarrollo.
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
