const API_ENDPOINTS = {
  prod: 'https://hi389sem08.execute-api.ap-northeast-1.amazonaws.com/chat',
  dev: 'https://f423y3o2y8.execute-api.ap-northeast-1.amazonaws.com/chat',
};

// Switch to prod/dev url based on git branch
export const CHAT_API_URL = import.meta.env.PROD 
  ? API_ENDPOINTS.prod 
  : API_ENDPOINTS.dev;