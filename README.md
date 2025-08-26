This is a YouTube video summarization Chrome extension that extracts key conclusions from stock-related videos. The system consists of:

- **Chrome Extension**: Frontend UI that extracts YouTube video metadata and communicates with the backend
- **FastAPI Backend**: Downloads audio, transcribes using OpenAI Whisper, and generates summaries using GPT models
