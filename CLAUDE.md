# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Environment setup: copy and populate .env.dev with required variables
```

## Architecture

EstimaX-AI Backend is a FastAPI service for processing blueprint images/PDFs using AI. Users upload blueprints, which are stored in Supabase S3, queued via RabbitMQ for async AI processing (symbol detection + cost estimation), and results are returned via polling.

### Layers

```
api/          →  Route handlers (FastAPI endpoints)
services/     →  Business logic (job orchestration, S3 upload)
repositories/ →  Database access (SQLAlchemy queries)
db/           →  ORM models + session management
messaging/    →  RabbitMQ publisher
core/         →  Pydantic settings loaded from .env.dev
```

### Request Flow

`POST /jobs` → `job_service.py` uploads file to Supabase S3, creates DB record, publishes message to RabbitMQ → job status transitions `PENDING → QUEUED → PROCESSING → COMPLETED|FAILED`

### Key Patterns

- **Response envelope**: All API responses use `{"data": {}, "message": "..."}` for success and `{"error": "ERROR_CODE", "message": "...", "details": {}}` for errors.
- **Base URL**: All routes are prefixed with `/api/v1`.
- **IDs**: UUIDv4 for all entities; timestamps in ISO 8601 UTC.
- **Storage**: Supabase S3 via boto3; presigned URLs have 30-minute TTL.
- **Config**: `core/config.py` uses Pydantic BaseSettings — add new env vars there first.

### Required Environment Variables

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `MQ_URL` / `MQ_HOST` / `MQ_PORT` / `MQ_USER` / `MQ_PASSWORD` / `MQ_VHOST` | RabbitMQ connection |
| `SUPABASE_S3_ENDPOINT` / `SUPABASE_ACCESS_KEY` / `SUPABASE_SECRET_KEY` / `SUPABASE_BUCKET_NAME` | Supabase S3 storage |

### Data Models (`db/models.py`)

- **Job**: Tracks blueprint processing (status, S3 paths, dimensions, detection count)
- **Detection**: Detected symbols (label, confidence, bounding box coordinates)
- **Estimation** + **EstimationItem**: Cost breakdown per symbol type
- **MessageLog**: Audit trail of RabbitMQ messages
