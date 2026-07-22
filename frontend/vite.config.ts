// Concept by MrHan (08974747477)
/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

// Dev proxy sends /api to the local backend so the SPA and API share an origin.
// In production the frontend Nginx container performs the equivalent proxy.
// No production hostname is hardcoded.
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false, // no production sourcemaps (Phase 2C.1 decision)
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    css: false,
    restoreMocks: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      exclude: ['src/api/generated/**', '**/*.test.{ts,tsx}', 'src/test/**'],
    },
  },
});
