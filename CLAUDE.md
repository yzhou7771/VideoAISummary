# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a YouTube video summarization Chrome extension that extracts key conclusions from stock-related videos. The system consists of:

- **Chrome Extension**: Frontend UI that extracts YouTube video metadata and communicates with the backend
- **FastAPI Backend**: Downloads audio, transcribes using OpenAI Whisper, and generates summaries using GPT models

## Architecture

### High-Level Flow
1. User opens YouTube video page and clicks extension
2. Extension extracts video ID, title, and channel information
3. User clicks "Extract Conclusions" button
4. Backend downloads audio using yt-dlp
5. Audio is transcribed using OpenAI Whisper API
6. Transcript is summarized using GPT model to extract 3-5 key conclusions
7. Results are displayed in the extension popup

### Project Structure (As Designed)
```
yt-summary-extension/
├── extension/           # Chrome Extension (Manifest V3)
│   ├── manifest.json   # Extension configuration
│   ├── popup.html      # Main UI
│   ├── popup.js        # Frontend logic
│   ├── content.js      # YouTube page interaction
│   ├── styles.css      # UI styling
│   └── icons/          # Extension icons
└── server/             # FastAPI Backend
    ├── app.py          # Main server application
    ├── prompts.py      # LLM prompt templates
    ├── requirements.txt # Python dependencies
    └── .env.example    # Environment configuration template
```

## Development Commands

### Backend Development

**Setup Environment:**
```bash
cd server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Configuration:**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

**Run Server:**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1
```

**Development Mode (with auto-reload):**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Test API Endpoint:**
```bash
# Replace VIDEO_ID with actual YouTube video ID
curl "http://localhost:8000/api/summarize?video_id=VIDEO_ID&lang=zh"
```

### Chrome Extension Development

**Install Extension:**
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `extension/` directory

**Test Extension:**
1. Navigate to any YouTube video page
2. Click the extension icon in the Chrome toolbar
3. Set backend API URL to `http://localhost:8000`
4. Click "Extract Conclusions"

## Key Dependencies

### Backend (Python)
- `fastapi`: Web framework for the API server
- `uvicorn`: ASGI server for running FastAPI
- `yt-dlp`: YouTube video/audio downloader
- `openai`: OpenAI API client for Whisper transcription and GPT summarization
- `python-dotenv`: Environment variable management

### Frontend (Chrome Extension)
- Manifest V3 Chrome Extension APIs
- Native JavaScript (no frameworks)
- Chrome Storage API for user preferences
- Chrome Runtime API for message passing

## Configuration

### Environment Variables (.env)
- `OPENAI_API_KEY`: OpenAI API key for Whisper and GPT access
- `WHISPER_MODEL`: Whisper model to use (default: "whisper-1")
- `SUMMARY_MODEL`: GPT model for summarization (default: "gpt-4o-mini")
- `TMP_DIR`: Directory for temporary audio files (default: "./tmp")

### Extension Settings
- Backend API base URL (stored in Chrome sync storage)
- Output language preference (Chinese/English)

## API Endpoints

### GET /api/summarize
Processes a YouTube video and returns conclusions.

**Parameters:**
- `video_id` (required): YouTube video ID
- `lang` (optional): Output language ("zh" for Chinese, "en" for English, default: "zh")

**Response:**
```json
{
  "video_id": "string",
  "conclusions": ["conclusion1", "conclusion2", "..."],
  "summary": "overall_summary",
  "transcript_preview": "first_1200_chars_of_transcript..."
}
```

## Development Notes

- The project is designed for United States stock market video analysis
- Audio processing uses temporary directories that are cleaned up after each request
- The extension supports both desktop and mobile YouTube URLs
- Transcription handles mixed Chinese/English content automatically
- Summary prompts are optimized for financial/investment content
- Error handling includes cleanup of temporary files
- CORS is enabled for all origins in development

## Optimization Opportunities

- Implement chunked transcription for videos longer than 25-30 minutes
- Add local Whisper support to reduce API costs
- Implement progress tracking for long-running operations
- Add caching for previously processed videos
- Support batch processing of multiple videos