import { defineConfig } from 'astro/config';
import alpine from '@astrojs/alpinejs';
import tailwind from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  // Set your canonical site URL for correct canonical/OG tags
  site: 'https://petersalmon.dev',
  // Build directly into the GitHub Pages folder
  outDir: './docs',
  integrations: [alpine()],
  vite: {
    plugins: [tailwind()],
  },
});
