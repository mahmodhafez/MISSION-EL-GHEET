/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

// The logo lives in ../media/brand (shared with the media team), so Vite may read one level up.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { port: 5173, fs: { allow: ['..'] } },
  test: { environment: 'jsdom', include: ['src/**/*.test.{ts,tsx}'] },
});
