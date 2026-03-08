# Adhi Compliance — Backend

AI Compliance Platform built with FastAPI. Provides ingestion, RAG-based Q&A,
EU AI Act risk classification, compliance monitoring, bias auditing, model cards,
report generation, and real-time alert delivery.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                    FastAPI (uvicorn)                  │
│  Routes: ingest │ compliance │ bias │ reports │ auth  │
└──────────┬─────────────────────────┬─────────────────┘
           │ sync reads              │ dispatches tasks
    ┌──────▼──────┐          ┌───────▼──────────┐
    │  SQLite /   │          │  Celery Workers   │
    │  PostgreSQL │          │  (compliance_tasks│
    │  (SQLAlchemy│          │   tasks.py)       │
    │  + Alembic) │          └───────┬──────────┘
    └─────────────┘                  │
                             ┌───────▼──────────┐
                             │  Redis (broker +  │
                             │  result backend)  │
                             └──────────────────┘
```

**Key components:**

| Layer | Technology |
|---|---|
| Web framework | FastAPI + Uvicorn |
| Database ORM | SQLAlchemy 2 |
| Migrations | Alembic |
| Task queue | Celery 5 + Redis |
| LLM | Google Gemini (google-genai SDK) |
| Embeddings | sentence-transformers + FAISS |
| Logging | python-json-logger (JSON structured) |
| Alerts | Slack / Teams / Email webhooks |
| Containers | Docker + docker-compose |

---

## Local Development Setup

### Prerequisites

- Python 3.12+
- Redis (for Celery; optional for in-memory fallback)
- Node.js 20+ (for the frontend)

### 1. Clone & enter the backend directory

```bash
git clone <repo>
cd Adhi/backend
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example env file and fill in your secrets:

```bash
cp .env.example .env
```

Required variables:

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Gemini API key (required if `LLM_PROVIDER=gemini`) |
| `DATABASE_URL` | SQLAlchemy DB URL (default: `sqlite:///./data/metadata.db`) |
| `REDIS_URL` | Redis connection string (default: `redis://localhost:6379/0`) |
| `ALERT_SLACK_WEBHOOK` | Slack incoming webhook URL (optional) |
| `ALERT_TEAMS_WEBHOOK` | Microsoft Teams webhook URL (optional) |
| `ALERT_EMAIL_SMTP` | SMTP DSN e.g. `smtp://user:pass@host:587` (optional) |
| `COMPLIANCE_SCAN_INTERVAL_HOURS` | Hours between automated scans (default: 24) |
| `SARVAM_API_KEY` | Sarvam STT key (optional) |
| `HF_TOKEN` | HuggingFace token (optional) |
| `SUPABASE_URL` | Supabase project URL (optional) |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (optional) |
| `SENTRY_DSN` | Sentry DSN for error tracking (optional) |

### 4. Run database migrations

```bash
# First run — apply all migrations
alembic upgrade head

# After editing models — generate + apply new migration
alembic revision --autogenerate -m "describe your change"
alembic upgrade head

# Roll back one migration
alembic downgrade -1
```

### 5. Start the API server

```bash
uvicorn app.main:app --reload --port 8000
```

### 6. Start the Celery worker (separate terminal)

```bash
celery -A app.workers.celery_app:celery_app worker \
  --loglevel=info \
  --queues=cpu_tasks,compliance_tasks,gpu_tasks \
  --concurrency=2
```

### 7. Start Celery Beat (periodic scans, separate terminal)

```bash
celery -A app.workers.celery_app:celery_app beat \
  --loglevel=info \
  --scheduler celery.beat:PersistentScheduler
```

---

## Docker Setup (recommended for production)

```bash
# From the project root (Adhi/)
docker-compose up --build

# Apply migrations on first run
docker-compose exec backend alembic upgrade head
```

Services started by docker-compose:

| Service | Port | Description |
|---|---|---|
| `backend` | 8000 | FastAPI server (4 workers) |
| `frontend` | 3000 | Next.js UI |
| `redis` | 6379 | Celery broker |
| `celery-worker` | — | Task worker |
| `celery-beat` | — | Periodic scheduler |

---

## API Documentation

Once the server is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key endpoint groups

| Tag | Base path | Description |
|---|---|---|
| Ingestion | `/api/v1/ingest` | Upload files for RAG indexing |
| Query | `/api/v1/query` | RAG-based Q&A |
| Compliance Checks | `/api/v1/compliance-checks` | Run/list compliance assessments |
| AI Systems | `/api/v1/ai-systems` | Register and classify AI systems |
| Bias Audits | `/api/v1/bias-audits` | Upload datasets for fairness analysis |
| Monitoring | `/api/v1/monitoring` | Trigger scans, check deadlines, drift |
| Reports | `/api/v1/reports` | Generate HTML/CSV compliance reports |
| Model Cards | `/api/v1/model-cards` | Generate EU AI Act Article 13 cards |
| Background Tasks | `/api/v1/tasks/{id}/status` | Poll Celery task status |

---

## Background Task Pattern

Heavy operations are dispatched as Celery tasks and return a `task_id` immediately:

```http
POST /api/v1/compliance-checks?async=true
→ { "task_id": "abc-123" }

GET /api/v1/tasks/abc-123/status
→ { "status": "SUCCESS", "ready": true }

GET /api/v1/tasks/abc-123/result
→ { "result": { "check_id": "...", "status": "partial" } }
```

---

## Project Structure

```
backend/
├── alembic/                  # Database migrations
│   ├── env.py                # Migration environment (reads app.config)
│   └── versions/             # Generated migration scripts
├── app/
│   ├── api/                  # FastAPI route handlers
│   │   └── routes_tasks.py   # Background task status endpoints
│   ├── core/
│   │   └── logging.py        # JSON structured logging + request middleware
│   ├── llm/                  # Gemini answer generator
│   ├── middleware/            # Error handler, request logging
│   ├── retrieval/            # FAISS-based RAG retriever
│   ├── services/             # Business logic
│   │   ├── alert_service.py
│   │   ├── audit_service.py
│   │   ├── bias_auditor.py
│   │   ├── compliance_checker.py
│   │   ├── compliance_monitor.py  # alert triggers wired
│   │   ├── model_card_generator.py
│   │   └── report_generator.py
│   ├── store/
│   │   ├── models.py         # SQLAlchemy models (includes AuditLog)
│   │   └── metadata_store.py # DB engine, Base, SessionLocal
│   └── workers/
│       ├── celery_app.py     # Celery app + beat schedule
│       ├── compliance_tasks.py  # Compliance background tasks
│       └── tasks.py          # Ingestion tasks
├── Dockerfile
├── alembic.ini
└── requirements.txt
```
