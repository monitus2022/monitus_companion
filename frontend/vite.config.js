// vite.config.js
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // Load environment variables from system environment (Cloudflare) and .env files
  const env = loadEnv(mode, process.cwd(), '');
  
  // Detect git branch from Cloudflare Pages runner (defaults to 'local' for dev server)
  const branch = process.env.CF_PAGES_BRANCH || 'local';
  const isProdBranch = branch === 'main';

  // Select target API URL
  const activeApiUrl = isProdBranch
    ? env.VITE_CHAT_API_URL_PROD
    : (env.VITE_CHAT_API_URL_DEV || env.VITE_CHAT_API_URL);

  // Print during Cloudflare build process for verification in build logs
  console.log(`[Vite Build] Branch: "${branch}" | Target API URL: "${activeApiUrl}"`);

  return {
    plugins: [react()],
    define: {
      'import.meta.env.VITE_CHAT_API_URL': JSON.stringify(activeApiUrl)
    }
  };
});