/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

// Only process.env is used here; declared to avoid adding @types/node as a dependency.
declare const process: { env: Record<string, string | undefined> };

// The logo lives in ../media/brand (shared with the media team), so Vite may read one level up.
// /api is proxied to the backend (default port 8787; set MEG_API_URL to change it).
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { port: 5173, fs: { allow: ['..'] }, proxy: { '/api': process.env.MEG_API_URL ?? 'http://127.0.0.1:8787' } },
  test: { environment: 'jsdom', include: ['src/**/*.test.{ts,tsx}'] },
});
