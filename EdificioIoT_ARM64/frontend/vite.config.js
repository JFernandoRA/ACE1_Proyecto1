import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // permite abrir el dashboard desde otros equipos en la red local
    port: 5173,
  },
})
