import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export function MessageBubble({ role, text, onTTS }) {
  const isUser = role === 'user';

  return (
    <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
      <div className="role-label">{isUser ? 'You' : 'Monitus'}</div>
      
      {isUser ? (
        <p className="message-text">{text}</p>
      ) : (
        <div className="markdown-content">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {text}
          </ReactMarkdown>
        </div>
      )}
      
      {!isUser && (
        <button onClick={() => onTTS(text)} className="tts-button" title="Listen to response">
          🔊 Listen
        </button>
      )}
    </div>
  );
}