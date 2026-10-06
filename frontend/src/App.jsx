import { useState, useEffect } from 'react';
import { fetchChatHistory, sendMessage } from './services/api';
import { Header } from './components/Header';
import { ChatWindow } from './components/ChatWindow';
import { MessageInput } from './components/MessageInput';
import './App.css';
import { cleanMarkdownForTTS } from './utils';

export default function App() {
  const [sessionId, setSessionId] = useState('test_dev_001');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedVoiceURI, setSelectedVoiceURI] = useState('');

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
  // Old TTS handler with default voice
  // const handleTTS = (text) => {
  //   if (!('speechSynthesis' in window)) return alert("TTS unavailable");
  //   window.speechSynthesis.cancel();
  //   window.speechSynthesis.speak(new SpeechSynthesisUtterance(text));
  // };

  const handleTTS = (text) => {
    if (!('speechSynthesis' in window)) return alert("TTS unavailable");

    window.speechSynthesis.cancel(); // Stop any active audio

    const cleanedText = cleanMarkdownForTTS(text);
    const utterance = new SpeechSynthesisUtterance(cleanedText);

    // Apply selected voice
    if (selectedVoiceURI) {
      const allVoices = window.speechSynthesis.getVoices();
      const matchedVoice = allVoices.find(v => v.voiceURI === selectedVoiceURI);
      if (matchedVoice) utterance.voice = matchedVoice;
    }

    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="app-container">
      <Header 
        sessionId={sessionId} 
        onSessionChange={setSessionId}
        selectedVoiceURI={selectedVoiceURI}
        onVoiceChange={setSelectedVoiceURI}
      />
      <ChatWindow messages={messages} loading={loading} onTTS={handleTTS} />
      <MessageInput onSend={handleSend} disabled={loading} />
    </div>
  );


}