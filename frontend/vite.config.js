import { defineConfig } from 'vite'
import path from 'path'

// Vite config placed in frontend so `npm run build` picks it up when
// executed from the frontend directory. Output is written to
// app/static/dist so Flask can serve compiled assets.
export default defineConfig({
  root: path.resolve(__dirname, '.'),
  build: {
    outDir: path.resolve(__dirname, '..', 'app', 'static', 'dist'),
    emptyOutDir: true,
    rollupOptions: {
      input: path.resolve(__dirname, 'index.html'),
      output: {
        // Emit a deterministic CSS filename so Flask templates can reference it
        assetFileNames: (assetInfo) => {
          if (assetInfo && assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'styles.css'
          }
          return 'assets/[name]-[hash][extname]'
        }
      }
    }
  }
})
