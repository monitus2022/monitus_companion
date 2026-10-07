import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const API_ENDPOINTS = {
  prod: 'https://hi389sem08.execute-api.ap-northeast-1.amazonaws.com/chat',
  dev: 'https://f423y3o2y8.execute-api.ap-northeast-1.amazonaws.com/chat',
};

export default defineConfig(() => {
  // Cloudflare Pages exposes git branch as process.env.CF_PAGES_BRANCH
  const branch = process.env.CF_PAGES_BRANCH || 'local';
  
  // 'main' branch uses prod endpoint; all other branches (dev/previews) use dev endpoint
  const activeApiUrl = branch === 'main' 
    ? API_ENDPOINTS.prod 
    : API_ENDPOINTS.dev;

  console.log(`[Vite Build] Branch "${branch}" -> API Target: "${activeApiUrl}"`);

  return {
    plugins: [react()],
    define: {
      'import.meta.env.VITE_CHAT_API_URL': JSON.stringify(activeApiUrl),
    },
  };
});