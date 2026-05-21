# PulseWire

A modular backend automation platform centered around Telegram publishing. PulseWire aggregates news from trusted RSS sources, normalizes the data, optionally summarizes it using AI, and automatically publishes formatted posts to a Telegram channel.

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM & Migrations:** SQLAlchemy 2.0 (async) + Alembic
- **HTTP Client:** HTTPX & feedparser
- **Telegram:** python-telegram-bot
- **Scheduling:** APScheduler (AsyncIOScheduler)
- **AI Integration:** OpenAI API (optional)
- **Containerization:** Docker + Docker Compose

## Quick Start

1. **Clone and configure**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Run with Docker Compose**
   ```bash
   docker compose up --build
   ```

3. **Run locally (development)**
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

## Project Structure

```
pulsewire/
├── app/
│   ├── api/routes/       # FastAPI route handlers
│   ├── core/             # Config & logging
│   ├── database/models/  # SQLAlchemy models
│   ├── services/
│   │   ├── aggregators/  # RSS fetching
│   │   ├── processors/   # DB ingestion & pipeline orchestration
│   │   ├── summarizers/  # Optional OpenAI logic
│   │   ├── telegram/     # Publishing logic
│   │   └── scheduler/    # APScheduler setup
│   ├── schemas/          # Pydantic schemas
│   └── main.py           # Application entrypoint
├── tests/
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL async connection string |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram Bot API token |
| `TELEGRAM_CHANNEL_ID` | Yes | Target Telegram channel |
| `OPENAI_API_KEY` | No | OpenAI API key for summarization |
| `SCHEDULER_INTERVAL_HOURS` | No | Pipeline run interval (default: 2) |
| `LOG_LEVEL` | No | Logging level (default: INFO) |
