Backend API for FINKO AI assistant (website chat integration)

# Features

- FastAPI backend
- OpenAI integration
- Vector Store knowledge base (RAG)
- Multilingual (ru, uz_latn, uz_cyrl, en)
- Session memory
- SQLite logging
- Bearer token security
- Docker support

# Requirements

- Python 3.11+
- OpenAI API key
- OpenAI Vector Store

# Environment Setup

Create `.env` file:

```
OPENAI_API_KEY=your_real_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_VECTOR_STORE_ID=vs_xxxxx
API_AUTH_TOKEN=your_token
DATABASE_PATH=./data/finko.sqlite3
```

# Run locally

```
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open:
http://127.0.0.1:8000/docs

# Run with Docker

```
docker build -t finko-ai .
docker run -p 8000:8000 --env-file .env finko-ai
```

# API Endpoints

## Health check

GET /health

## Chat

POST /api/chat

## Feedback

POST /api/feedback

## Config

GET /api/config

# Example Request

```
curl -X POST "http://127.0.0.1:8000/api/chat" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_TOKEN" \
-d '{
  "message": "Какие услуги доступны через FINKO?",
  "session_id": "web_123",
  "language_hint": "ru"
}'
```

# Important Rules

- Do not commit `.env`
- Do not expose API keys
- All answers must be based on knowledge base
- FINKO does NOT issue loans directly
- Final decisions are made by partner institutions

# Deployment Options

- Docker (recommended)
- Railway
- VPS

# Author

R.P.A.