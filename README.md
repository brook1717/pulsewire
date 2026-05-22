# PulseWire — Production-Grade Backend News Automation Platform

> Automated RSS-to-Telegram content pipeline with database-first integrity, optional AI summarization, and zero-downtime scheduling.

**Created by [Biruk Kasahun](https://birukkasahun.com)**

---

## Architectural Positioning

PulseWire is a portfolio/demonstration project **engineered entirely to a production-ready standard**. Every design decision reflects real-world backend architecture principles:

- **Database-first deduplication** — article uniqueness is enforced at the PostgreSQL constraint level, eliminating race conditions and in-memory drift.
- **Graceful third-party API isolation** — the OpenAI summarization layer is strictly optional; failures are caught, logged, and bypassed without halting the pipeline.
- **Strict async pipeline sequencing** — the system uses asynchronous Python end-to-end (FastAPI, SQLAlchemy 2.0 async, HTTPX) while deliberately avoiding premature complexity like Celery or distributed task queues.

---

## Core Features

- **RSS Data Normalization** — fetches from predefined feeds, extracts and standardizes title, source, URL, category, and timestamps.
- **DB-Enforced Constraint Filtering** — duplicate articles are rejected via UNIQUE constraints with graceful `IntegrityError` handling.
- **Resilient Optional AI Summarization** — generates sub-100-word Telegram-ready summaries via OpenAI; falls back to raw descriptions on any failure.
- **Automated Telegram Publishing** — formats and posts articles to a configured channel using MarkdownV2.
- **Interval Scheduling** — APScheduler triggers the pipeline on a configurable cadence (default: every 2 hours).
- **Audit Logging** — every pipeline event (fetch, process, publish) is recorded in a `BotLog` table for observability.
- **Operational Endpoints** — `GET /logs` for audit trail, `POST /trigger` for manual execution (API-key protected).

---

## System Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌───────────────────┐
│  RSS Feeds  │────▶│  Aggregator      │────▶│  PostgreSQL       │
│  (external) │     │  (httpx + parser) │     │  (deduplication)  │
└─────────────┘     └──────────────────┘     └────────┬──────────┘
                                                      │
                                                      ▼
                                             ┌────────────────────┐
                                             │  OpenAI Client     │
                                             │  (optional summary)│
                                             └────────┬───────────┘
                                                      │
                                                      ▼
                                             ┌────────────────────┐
                                             │  Telegram Channel  │
                                             │  (MarkdownV2 post) │
                                             └────────────────────┘

Orchestration: APScheduler (AsyncIOScheduler) ─── interval trigger ──▶ run_pipeline()
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL 16 |
| ORM & Migrations | SQLAlchemy 2.0 (async) + Alembic |
| HTTP Client | HTTPX + feedparser |
| Telegram | python-telegram-bot |
| Scheduling | APScheduler (AsyncIOScheduler) |
| AI (optional) | OpenAI API |
| Containerization | Docker + Docker Compose |

---

## Setup & Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/brook1717/pulsewire.git
cd pulsewire
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | `postgresql+asyncpg://user:pass@host:5432/db` |
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from @BotFather |
| `TELEGRAM_CHANNEL_ID` | Yes | Target channel (e.g. `@yourchannel`) |
| `API_KEY` | Yes | Static key for `POST /trigger` endpoint |
| `OPENAI_API_KEY` | No | Enables AI summarization when set |
| `SCHEDULER_INTERVAL_HOURS` | No | Pipeline cadence in hours (default: 2) |
| `LOG_LEVEL` | No | `DEBUG`, `INFO`, `WARNING` (default: INFO) |

### 3. Launch the full stack

```bash
docker compose up --build
```

This single command starts:
- **PostgreSQL 16** with health-checked readiness
- **FastAPI application** with scheduler, API endpoints, and pipeline

### 4. Run database migrations

```bash
docker compose exec app alembic upgrade head
```

### 5. Verify

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | None | Liveness check |
| `GET` | `/logs` | None | 50 most recent pipeline audit logs |
| `POST` | `/trigger` | `X-API-Key` header | Manually execute the pipeline |

---

## Project Structure

```
pulsewire/
├── app/
│   ├── api/routes/          # Operational endpoints (logs, trigger)
│   ├── core/                # Settings (Pydantic) & structured logging
│   ├── database/models/     # Article, BotLog (SQLAlchemy 2.0)
│   ├── services/
│   │   ├── aggregators/     # Async RSS fetching & normalization
│   │   ├── processors/      # Ingestion, deduplication, pipeline orchestration
│   │   ├── summarizers/     # Optional OpenAI integration
│   │   ├── telegram/        # MarkdownV2 publishing
│   │   └── scheduler/       # APScheduler lifecycle
│   ├── schemas/             # Pydantic validation models
│   └── main.py              # FastAPI app & lifespan management
├── alembic/                 # Async database migrations
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Production Next Steps

- **Celery + Redis** — migrate to distributed task execution for multi-tenant feed isolation and retry semantics.
- **Prometheus + Grafana** — instrument pipeline latency, publish success rate, and queue depth metrics.
- **Centralized Logging** — ship structured JSON logs to ELK/Loki for cross-service correlation.
- **Rate Limiting** — add per-channel publish throttling to respect Telegram API limits at scale.
- **Feed Management API** — expose CRUD endpoints for dynamic RSS feed configuration without redeployment.
- **Webhook Delivery** — extend output beyond Telegram to Slack, Discord, or custom webhook targets.
- **CI/CD Pipeline** — GitHub Actions for automated testing, linting, and container registry pushes.

---

## License

This project is part of the professional portfolio of **Biruk Kasahun**.  
For inquiries: [birukkasahun.com](https://birukkasahun.com)
