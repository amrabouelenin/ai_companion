# AI Companion Robot (With French Tutor Mode)

This project sets up an AI Companion Robot with multiple personality modes including a French Tutor mode. It uses a modular architecture with several integrated services.

## Features

| Feature                       | Description                                                                      |
| ----------------------------- | -------------------------------------------------------------------------------- |
| **Conversational AI**         | Talk naturally (like ChatGPT), understand context, emotions.                     |
| **Emotional Reactions**       | Use screen/LEDs/gestures to express happiness, confusion, boredom, etc.          |
| **Task Helper**               | Set reminders, timers, answer questions, play music/news, give daily motivation. |
| **Companion Modes**           | Toggle between modes like "Chill Buddy," "Motivator," "French Tutor," etc.       |
| **Personality Customization** | Let you pick voice, tone (funny, serious, gentle), or even name it.              |

## Prerequisites

- Docker and Docker Compose installed
- NVIDIA GPU with CUDA support (for optimal performance with Whisper STT)

## Services

- **Ollama**: Local LLM service for natural language understanding and generation
- **Open WebUI**: Web interface for chatting with Ollama models
- **Piper TTS**: Text-to-speech service for voice output
- **Whisper STT**: Speech-to-text service for voice input
- **Companion Orchestrator**: Central service that coordinates all components and manages different personality modes

## Setup Instructions

1. Build and start all services:
   ```bash
   docker compose up -d
   ```

2. Access interfaces:
   - Open WebUI (chat interface): http://localhost:3000
   - Companion Orchestrator API: http://localhost:8000

## Service Configuration

### Ollama

- **Port**: 11434
- **Models**: Uses the default Ollama models (llama3 recommended)
- **Resource Limits**: 8 CPUs, 16GB memory (adjust as needed)

### Piper TTS (Text-to-Speech)

- **Port**: 5000
- **Voices**: Includes English and French voices
- **API Endpoint**: http://localhost:5000/api/tts

### Whisper STT (Speech-to-Text)

- **Port**: 9000
- **Model**: Medium model for better accuracy
- **GPU**: Requires NVIDIA GPU with CUDA support
- **API Endpoint**: http://localhost:9000/asr

### Companion Orchestrator

- **Port**: 8000
- **Available Modes**: General Assistant, French Tutor, Motivational Coach, Chill Buddy
- **Environment Variables**:
  - `OLLAMA_API_URL`: Connection to Ollama API
  - `PIPER_TTS_URL`: Connection to TTS service
  - `WHISPER_STT_URL`: Connection to STT service
  - `DEFAULT_COMPANION_MODE`: Default mode on startup
  - `AVAILABLE_MODES`: List of available personality modes

## Personality Modes

- **General Assistant**: Default helpful mode for everyday tasks
- **French Tutor**: Specialized mode for learning French, provides translations and corrections
- **Motivational Coach**: Energetic mode with positive reinforcement and motivation
- **Chill Buddy**: Relaxed conversation partner for casual chats

## API Endpoints

### Companion Orchestrator API

#### `GET /health`
Health check endpoint to verify the service is running.

**Response:**
```json
{"status": "healthy"}
```

#### `GET /modes`
List all available personality modes.

**Response:**
```json
[
  {"name": "general", "description": "General helpful assistant", "active": true},
  {"name": "french_tutor", "description": "French language tutor", "active": false},
  ...
]
```

#### `POST /mode/{mode_name}`
Change the active personality mode.

**Parameters:**
- `mode_name` (path parameter): Name of the mode to activate

**Response:**
```json
{"message": "Mode set to french_tutor"}
```

#### `POST /chat`
Text-based conversation with the AI companion.

**Request Body:**
```json
{
  "text": "Hello, can you help me learn French?",
  "mode": "french_tutor",  // Optional, uses active mode if not specified
  "user_id": "default_user"  // Optional
}
```

**Response:**
```json
{
  "text": "Bonjour! Je serais ravi de vous aider à apprendre le français...",
  "audio_url": "/text-to-speech?text=Bonjour%21%20Je%20serais...",
  "emotion": "happy"
}
```

**Note:** The `audio_url` field is a reference path that should be handled by your client. For direct audio retrieval, use the `/text-to-speech` endpoint described below.

#### `POST /text-to-speech`
Convert text to speech audio. Returns binary audio data as a WAV file.

**Request Body:**
```json
{
  "text": "Hello there, this is a test of the TTS service.",
  "user_id": "default_user"  // Optional
}
```

**Response:** Binary WAV audio file

**Important:** This endpoint requires a POST request with a JSON body (TextInput model). It does not support GET requests with query parameters, despite the URL format provided in the chat response `audio_url` field.

#### `POST /voice`
Voice-based conversation with the AI companion (audio input).

**Request Body:**
```json
{
  "audio_data": "<binary audio data>",
  "mode": "french_tutor",  // Optional
  "user_id": "default_user"  // Optional
}
```

**Response:** Same as `/chat` endpoint

#### `WebSocket /ws/{user_id}`
Real-time conversation via WebSocket connection.

**Parameters:**
- `user_id` (path parameter): User identifier for the WebSocket connection

**Message Format:**
```json
// Text input message:
{"type": "text", "text": "Hello AI companion", "mode": "general"}

// Mode change message:
{"type": "mode", "mode": "french_tutor"}
```

## Stopping the Services

```bash
docker compose down
```
