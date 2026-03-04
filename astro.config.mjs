// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://racksperu.vercel.app',
  output: 'static',
  vite: {
    plugins: [tailwindcss()]
  },
  integrations: [sitemap()]
});