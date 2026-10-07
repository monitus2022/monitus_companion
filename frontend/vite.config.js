import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  // Cloudflare injects branch name into process.env.CF_PAGES_BRANCH
  const branch = process.env.CF_PAGES_BRANCH || 'local';
  const isProdBranch = branch === 'main';

  // Read explicitly from process.env or loadEnv
  const devUrl = process.env.VITE_CHAT_API_URL_DEV || env.VITE_CHAT_API_URL_DEV;
  const prodUrl = process.env.VITE_CHAT_API_URL_PROD || env.VITE_CHAT_API_URL_PROD;

  // Local development fallback (.env.local)
  const localUrl = env.VITE_CHAT_API_URL;

  const activeApiUrl = isProdBranch 
    ? prodUrl 
    : (devUrl || localUrl);

  if (!activeApiUrl) {
    console.warn(`\n⚠️ [Vite Build Warning] No API URL defined for branch "${branch}"!\n`);
  }

  console.log(`[Vite Build] Branch: "${branch}" | Target API URL: "${activeApiUrl}"`);

  return {
    plugins: [react()],
    define: {
      'import.meta.env.VITE_CHAT_API_URL': JSON.stringify(activeApiUrl)
    }
  };
});