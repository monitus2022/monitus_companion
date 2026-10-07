// vite.config.js
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // Load environment variables available at build time (including Cloudflare variables)
  const env = loadEnv(mode, process.cwd(), '');

  // Detect git branch from Cloudflare Pages runner
  const isProdBranch = process.env.CF_PAGES_BRANCH === 'main';

  // Fallback to local dev variable if running locally (`npm run dev`)
  const activeApiUrl = isProdBranch
    ? env.VITE_CHAT_API_URL_PROD
    : (env.VITE_CHAT_API_URL_DEV || env.VITE_CHAT_API_URL);

  return {
    plugins: [react()],
    define: {
      // Expose the selected URL to React components as import.meta.env.VITE_CHAT_API_URL
      'import.meta.env.VITE_CHAT_API_URL': JSON.stringify(activeApiUrl)
    }
  };
});