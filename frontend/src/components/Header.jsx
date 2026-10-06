import { useState, useEffect } from 'react';

export function Header({ sessionId, onSessionChange }) {
  // Local state tracks what the user types without triggering App-level updates
  const [localSessionId, setLocalSessionId] = useState(sessionId);

  // Keep local state in sync if parent sessionId changes externally
  useEffect(() => {
    setLocalSessionId(sessionId);
  }, [sessionId]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = localSessionId.trim();
    if (trimmed && trimmed !== sessionId) {
      onSessionChange(trimmed);
    }
  };

  return (
    <header className="header">
      <h2>Monitus Companion</h2>
      <form onSubmit={handleSubmit} className="session-control">
        <label htmlFor="session-input">Session ID: </label>
        <input 
          id="session-input"
          type="text" 
          value={localSessionId} 
          onChange={(e) => setLocalSessionId(e.target.value)}
          className="session-input"
        />
        <button 
          type="submit" 
          className="session-button"
          disabled={!localSessionId.trim() || localSessionId.trim() === sessionId}
        >
          Load
        </button>
      </form>
    </header>
  );
}