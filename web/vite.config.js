import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/Equity-Valuation-Map/',
  optimizeDeps: {
    include: ['prop-types']
  }
})