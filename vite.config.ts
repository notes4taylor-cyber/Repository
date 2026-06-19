import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Use relative asset paths so the build works no matter what subpath it's
  // served from (e.g. GitHub Pages serves project sites at /<repo>/). Since
  // this is a single-page app with no client-side router, relative base is the
  // most robust choice and needs no repo-name hardcoding.
  base: './',
});
