import { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';

export function ChatWindow({ messages, loading, onTTS }) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="chat-window">
      {messages.map((msg, index) => (
        <MessageBubble
          key={index}
          role={msg.role}
          text={msg.text}
          onTTS={onTTS}
        />
      ))}

      {loading && (
        <div className="message-bubble assistant loading">
          <span className="loading-text">Monitus is thinking...</span>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}