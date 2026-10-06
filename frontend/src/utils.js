// Helper to strip Markdown formatting so TTS doesn't speak symbols
const cleanMarkdownForTTS = (text) => {
  return text
    .replace(/```[\s\S]*?```/g, '') // Strip code blocks
    .replace(/`([^`]+)`/g, '$1')     // Remove inline code ticks
    .replace(/[*_#~]/g, '')          // Strip formatting symbols (*, _, #, ~)
    .trim();
};

export { cleanMarkdownForTTS };