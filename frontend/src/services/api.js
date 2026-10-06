const API_ENDPOINT = import.meta.env.VITE_CHAT_API_URL;

export async function fetchChatHistory(sessionId) {
    try {
        const response = await fetch(`${API_ENDPOINT}?session_id=${encodeURIComponent(sessionId)}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        // Map Bedrock history objects to match frontend state format ({ role, text })
        const chatHistory = (data.history || []).map(item => ({
            role: item.role,
            text: item.content?.[0]?.text || '' // Changed 'content' to 'text'
        }));
        
        return chatHistory;
    } catch (error) {
        console.error('Error fetching chat history:', error);
        throw error;
    }
}

export async function sendMessage(sessionId, message) {
    const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: sessionId,
            message: message
        })
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
}