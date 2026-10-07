// Read the active environment endpoint defined by vite.config.js
const API_URL = import.meta.env.VITE_CHAT_API_URL;

/**
 * Clean base URL to prevent double slashes or missing endpoint paths
 */
function getEndpointUrl() {
  if (!API_URL) {
    console.error('Chat API URL is undefined!');
  }
  return API_URL;
}

export async function fetchChatHistory(sessionId) {
  try {
    const endpoint = getEndpointUrl();
    const response = await fetch(`${endpoint}?session_id=${encodeURIComponent(sessionId)}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Support both 'history' and 'messages' keys safely
    const rawHistory = data.history || data.messages || [];

    // Map Bedrock history objects to match frontend state format ({ role, text })
    return rawHistory.map((item) => ({
      role: item.role,
      text: item.content?.[0]?.text || item.text || '',
    }));
  } catch (error) {
    console.error('Error fetching chat history:', error);
    // Return empty array on failure so UI unlocks instead of crashing
    return [];
  }
}

export async function sendMessage(sessionId, message) {
  const endpoint = getEndpointUrl();

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}