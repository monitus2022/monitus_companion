import { useState, useEffect } from 'react';

export function Header({ sessionId, onSessionChange, selectedVoiceURI, onVoiceChange }) {
  const [localSessionId, setLocalSessionId] = useState(sessionId);
  const [voices, setVoices] = useState([]);

  useEffect(() => {
    setLocalSessionId(sessionId);
  }, [sessionId]);

  // Load and listen for system voices
  useEffect(() => {
    const loadVoices = () => {
      if (!('speechSynthesis' in window)) return;
      const availableVoices = window.speechSynthesis.getVoices();
      
      // Filter for English voices (or remove .filter to show all languages)
      const englishVoices = availableVoices.filter(v => v.lang.startsWith('en'));
      setVoices(englishVoices.length ? englishVoices : availableVoices);

      // Set default voice if none selected
      if (!selectedVoiceURI && englishVoices.length > 0) {
        onVoiceChange(englishVoices[0].voiceURI);
      }
    };

    loadVoices();

    // Chrome/Edge load voices asynchronously
    if ('speechSynthesis' in window) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }
  }, [selectedVoiceURI, onVoiceChange]);

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
      
      <div className="header-controls">
        {/* Voice Selector Dropdown */}
        {voices.length > 0 && (
          <select 
            value={selectedVoiceURI} 
            onChange={(e) => onVoiceChange(e.target.value)}
            className="voice-select"
            title="Select TTS Voice"
          >
            {voices.map((v) => (
              <option key={v.voiceURI} value={v.voiceURI}>
                {v.name} ({v.lang})
              </option>
            ))}
          </select>
        )}

        {/* Session ID Form */}
        <form onSubmit={handleSubmit} className="session-control">
          <input 
            id="session-input"
            type="text" 
            value={localSessionId} 
            onChange={(e) => setLocalSessionId(e.target.value)}
            className="session-input"
            placeholder="Session ID"
          />
          <button 
            type="submit" 
            className="session-button"
            disabled={!localSessionId.trim() || localSessionId.trim() === sessionId}
          >
            Load
          </button>
        </form>
      </div>
    </header>
  );
}