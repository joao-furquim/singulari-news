# Singulari News

An AI-powered newsletter platform with a content curator agent, automatic AI summaries, and a complete authentication system.

---

## About

Singulari News is a full-stack news aggregation platform built as a technical challenge. Articles are dropped as JSON files into a hotfolder watched by a Python curator agent. The agent classifies each article by keyword scoring, publishes it to a BullMQ queue, and a NestJS consumer generates an AI summary via Gemini before persisting to PostgreSQL. A React frontend polls for new articles every 30 seconds and shows a notification banner when new content arrives.

---

## Architecture

```
                          ┌────────────────────────────────────────────────────┐
                          │                  Browser / User                    │
                          └───────────────────────┬────────────────────────────┘
                                                  │ HTTP :80
                          ┌───────────────────────▼────────────────────────────┐
                          │           frontend  (nginx + React)                │
                          │           React 18 · MUI · Vite · TypeScript        │
                          └───────────────────────┬────────────────────────────┘
                                                  │ /api proxy → :8000
                          ┌───────────────────────▼────────────────────────────┐
                          │         backend  (FastAPI + Tortoise ORM)          │
                          │         JWT auth · REST API · :8000                │
                          └──────┬────────────────────────────┬───────────────┘
                                 │ SQL                         │ SQL
                    ┌────────────▼──────────┐      ┌──────────▼────────────────┐
                    │  db  (PostgreSQL 16)  │      │  (reads from db too)      │
                    └───────────────────────┘      │                           │
                                                   │   consumer  (NestJS)      │
                                                   │   BullMQ worker           │
                                                   │   Gemini summary API      │
                                                   └──────────┬────────────────┘
                                                              │ dequeue
                          ┌───────────────────────────────────▼───────────────┐
                          │            redis  (BullMQ broker + JWT cache)     │
                          └───────────────────────────────────▲───────────────┘
                                                              │ enqueue
                          ┌───────────────────────────────────┴───────────────┐
                          │           agent  (Python + APScheduler)           │
                          │  watches data/queue/ · classifies · publishes     │
                          └───────────────────────────────────────────────────┘
                                     ▲
                                     │ JSON files dropped here
                                 data/queue/
```

**Data flow:**

1. JSON files (single article or batch array) are dropped into `agent/data/queue/`
2. The **agent** runs every 5 minutes, picks up the file, classifies each article by keyword scoring (8 canonical categories), and publishes jobs to Redis via BullMQ
3. The **consumer** dequeues each job, calls Gemini to generate a 3-sentence summary, saves to PostgreSQL, and marks the job processed
4. The **backend** exposes a paginated `GET /news` endpoint with filters (period, categories, date range)
5. The **frontend** polls every 10 s (dev) / 30 s (prod) and shows a notification banner when new articles arrive

---

## Technical Decisions

### FastAPI over Django / Flask

FastAPI's native `async`/`await` support is a first-class citizen, which matches the I/O-heavy nature of the backend (DB queries, external API calls, file handling). Its automatic OpenAPI documentation (`/docs`) reduces manual work during development. Pydantic v2 integration gives free request/response validation with detailed 422 errors. Django would add ORM and admin overhead we don't need; Flask would require assembling the same async story from third-party packages.

### Tortoise ORM + Aerich over SQLAlchemy + Alembic

Tortoise ORM was designed for asyncio from the ground up, whereas SQLAlchemy's async story is a wrapper around the synchronous core. Aerich (Tortoise's migration tool) generates versioned migration files automatically from model diffs, matching the Alembic workflow without any additional glue code. The tradeoff is a smaller ecosystem — complex joins require more explicit prefetching — but for this read-heavy workload the ergonomics are worth it.

### BullMQ + Redis over RabbitMQ

BullMQ provides persistent, ordered job queues on top of Redis, which the application already uses for JWT caching. A single Redis instance handles both concerns in the demo environment. BullMQ's retry-with-backoff and job priority features cover the ingest pipeline requirements without deploying a separate broker. RabbitMQ would be the right upgrade path when multiple independent producers (scrapers, webhooks, RSS readers) need to fan-out to multiple consumers with different routing rules — see **Future Improvements**.

### PostgreSQL over MongoDB

Articles are structured data with well-defined schemas and relational constraints (category FK, user preferences join table, favorites many-to-many). PostgreSQL's full-text search and `JSONB` columns give an escape hatch for semi-structured metadata without sacrificing ACID guarantees. MongoDB's flexible schema would add operational complexity without a clear benefit for this data model.

### React + MUI over Next.js / Tailwind

The application is a purely client-side SPA with real-time polling — there are no SEO requirements that would justify SSR. MUI v5 provides a complete design system (dark theme, accessible components, date pickers) out of the box, allowing the UI to be built quickly without writing custom CSS. Tailwind would require a more hands-on design system; Next.js would add unnecessary build complexity for a single-page dashboard.

### Hotfolder agent over real-time scraping

Decoupling article ingestion from the backend makes the pipeline resilient to scraper failures and avoids rate-limit coupling between the curator and the API. Operators can drop any JSON payload (manual curation, RSS-to-JSON converters, webhook forwarders) into the queue folder without touching code. The agent's `process_inbox()` supports both single-article objects and batch arrays in the same file.

### Gemini over OpenAI

Gemini's free tier (`gemini-2.0-flash-lite`) is sufficient for generating 3-sentence article summaries in a demo environment, eliminating the need for paid API credits. The consumer's `generateSummaryWithFallback()` extracts the first two sentences of the article as a degraded fallback when the API is unavailable, ensuring the pipeline never blocks. OpenAI's GPT models would be a drop-in replacement by changing `AI_MODEL` in `.env`.

---

## Services

| Service      | Technology                    | Port  | Notes                            |
|--------------|-------------------------------|-------|----------------------------------|
| `frontend`   | React 18 · Vite · nginx       | 80    | Serves static build; proxies `/api` to backend |
| `backend`    | FastAPI · Tortoise ORM        | 8000  | REST API + JWT auth              |
| `db`         | PostgreSQL 16                 | 5432  | Primary data store               |
| `redis`      | Redis 7                       | 6379  | BullMQ broker + JWT cache        |
| `agent`      | Python 3.11 · APScheduler     | —     | Hotfolder curator; runs every 5 min |
| `consumer`   | NestJS · BullMQ               | —     | Dequeues jobs, generates summaries |
| `seed-demo`  | Python (profile: demo)        | —     | Creates demo users               |
| `seed-articles` | Python (profile: demo)    | —     | Populates `queue/` with 30 sample articles |

---

## Prerequisites

- **Docker** ≥ 24 and **Docker Compose** ≥ 2.20
- API keys for Gemini, Resend, and Cloudflare R2 (optional for local testing — the pipeline falls back gracefully when these are absent)

No local Python, Node, or database installation is required.

---

## How to Run

### 1. Clone the repository

```bash
git clone <repo-url>
cd singulari-news
```

### 2. Configure environment

```bash
cp .env.example .env
# Open .env and fill in your API keys (see External APIs section)
```

### 3. Start all services

```bash
docker compose up --build
```

Database migrations run automatically on backend startup via `aerich upgrade`.

### 4. Load demo data (optional)

```bash
# Create demo users (reviewer, editor, user1, user2)
docker compose --profile demo up seed-demo

# Populate the article queue with 30 sample articles across 8 categories
docker compose --profile demo up seed-articles
```

After running `seed-articles`, the agent will process the queue on its next scheduler tick (within 5 minutes) and the articles will appear in the frontend.

### 5. Access the application

| Service   | URL                         |
|-----------|-----------------------------|
| Frontend  | http://localhost             |
| Backend   | http://localhost:8000        |
| Swagger   | http://localhost:8000/docs   |
| Redoc     | http://localhost:8000/redoc  |

---

## Default Credentials

| Role     | Email                  | Password    | Notes                                |
|----------|------------------------|-------------|--------------------------------------|
| Root     | root@singulari.com     | Root@123    | Cannot be deleted or listed via API  |
| Admin    | admin@singulari.com    | Admin@123   | Full user and content management     |

---

## External APIs

| API              | Purpose                  | Env variable(s)                                      |
|------------------|--------------------------|------------------------------------------------------|
| Google Gemini    | AI article summaries     | `AI_API_KEY`, `AI_MODEL=gemini-2.0-flash-lite`       |
| Resend           | Transactional email      | `RESEND_API_KEY`, `EMAIL_FROM`                       |
| Cloudflare R2    | Avatar image storage     | `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `R2_PUBLIC_URL` |

Replace actual keys with `<CHAVE_DE_API>` in any shared `.env.example` file. Never commit real keys to version control.

---

## Running Tests

### Backend — unit tests

```bash
cd backend
poetry run pytest tests/ -v
```

### Backend — integration tests (SQLite in-memory, no Docker required)

```bash
cd backend
poetry run pytest tests/integration/ -v
```

### Frontend — component and hook tests

```bash
cd frontend
npm test
```

### All at once (from repo root)

```bash
make test-all
```

---

## Future Improvements

- **RabbitMQ** as the message broker to support multiple independent article producers (RSS scrapers, webhook receivers, email parsers) with topic-based routing to multiple consumer instances
- **WebSockets** to replace the 30-second polling loop with server-push notifications for new articles
- **Thumbnail generation** via an image AI API (DALL-E, Stable Diffusion) to create category-specific cover images for each article card
- **Internationalisation** with i18next (PT-BR / EN) — the `locale` field on the `User` model is already in place
- **Redis cache** for `GET /news` responses to reduce database load under high traffic (30-second TTL matching the polling interval)
- **Rate limiting** on public routes (`GET /news`, `POST /users`, `POST /login`) via a FastAPI middleware or an upstream API gateway
- **Full-text search** using PostgreSQL `tsvector` or Elasticsearch to enable keyword search across article titles and content
- **Email digest** — a weekly scheduled job (APScheduler) that sends each user a personalised newsletter based on their category preferences via Resend
