import { defineConfig } from 'vite'
import path from 'path'

// Build into app/static/dist so Flask can serve the compiled assets
export default defineConfig({
  root: path.resolve(__dirname, 'frontend'),
  build: {
    outDir: path.resolve(__dirname, 'app', 'static', 'dist'),
    emptyOutDir: true,
    rollupOptions: {
      input: path.resolve(__dirname, 'frontend', 'main.js')
    }
  }
})
