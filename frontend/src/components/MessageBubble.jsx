export function MessageBubble({ role, text, onTTS }) {
  const isUser = role === 'user';

  return (
    <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
      <div className="role-label">{isUser ? 'You' : 'Monitus'}</div>
      <p className="message-text">{text}</p>
      
      {!isUser && (
        <button onClick={() => onTTS(text)} className="tts-button" title="Listen to response">
          🔊 Listen
        </button>
      )}
    </div>
  );
}