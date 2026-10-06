import { useState, useEffect } from 'react';
import { fetchChatHistory, sendMessage } from './services/api';
import { Header } from './components/Header';
import { ChatWindow } from './components/ChatWindow';
import { MessageInput } from './components/MessageInput';
import './App.css';

export default function App() {
  const [sessionId, setSessionId] = useState('test_dev_001');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    
    fetchChatHistory(sessionId).then(history => {
      if (isMounted) {
        setMessages(history);
        setLoading(false);
      }
    });

    return () => { isMounted = false; };
  }, [sessionId]);

  const handleSend = async (userText) => {
    setMessages(prev => [...prev, { role: 'user', text: userText }]);
    setLoading(true);

    try {
      const data = await sendMessage(sessionId, userText);
      setMessages(prev => [...prev, { role: 'assistant', text: data.message }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', text: `⚠️ Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleTTS = (text) => {
    if (!('speechSynthesis' in window)) return alert("TTS unavailable");
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(text));
  };

  return (
    <div className="app-container">
      <Header sessionId={sessionId} onSessionChange={setSessionId} />
      <ChatWindow messages={messages} loading={loading} onTTS={handleTTS} />
      <MessageInput onSend={handleSend} disabled={loading} />
    </div>
  );
}