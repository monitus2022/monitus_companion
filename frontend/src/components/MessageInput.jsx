import { useState } from 'react';

export function MessageInput({ onSend, disabled }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSend(input.trim());
    setInput('');
  };

  return (
    <form onSubmit={handleSubmit} className="input-form">
      <input
        type="text"
        placeholder="Type your message..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={disabled}
        className="text-input"
      />
      <button type="submit" disabled={disabled || !input.trim()} className="send-button">
        Send
      </button>
    </form>
  );
}