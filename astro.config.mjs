import sitemap from '@astrojs/sitemap';
import tailwind from '@tailwindcss/vite';
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  // Set your canonical site URL for correct canonical/OG tags
  site: 'https://petersalmon.dev',
  // Build directly into the GitHub Pages folder
  outDir: './docs',
  integrations: [sitemap()],
  vite: {
    plugins: [tailwind()],
  },
});
