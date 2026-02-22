```
backend/
│
├── app/
│   ├── main.py                      # FastAPI entrypoint
│   │
│   ├── api/                         # Route layer
│   │   ├── routes.py
│   │   ├── jobs.py
│   │   ├── detections.py
│   │   ├── estimation.py
│   │   └── health.py
│   │
│   ├── core/                        # Core configs
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   └── exceptions.py
│   │
│   ├── db/                          # Database layer
│   │   ├── database.py
│   │   ├── models.py
│   │   └── migrations/
│   │
│   ├── schemas/                     # Pydantic schemas
│   │   ├── job.py
│   │   ├── detection.py
│   │   ├── estimation.py
│   │   └── common.py
│   │
│   ├── services/                    # Business logic
│   │   ├── job_service.py
│   │   ├── detection_service.py
│   │   ├── estimation_service.py
│   │   ├── storage_service.py
│   │   └── health_service.py
│   │
│   ├── messaging/                   # RabbitMQ integration
│   │   ├── connection.py
│   │   ├── publisher.py             # Publish job.created
│   │   ├── consumer.py              # Consume job.completed/failed
│   │   └── handlers.py              # Result message handlers
│   │
│   ├── repositories/                # DB abstraction layer
│   │   ├── job_repository.py
│   │   ├── detection_repository.py
│   │   └── base.py
│   │
│   └── utils/
│       ├── file_utils.py
│       └── validators.py
│
├── tests/
│   ├── test_jobs.py
│   ├── test_estimation.py
│   └── test_messaging.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── Makefile
└── .env.dev
```
# Blueprint AI Backend

## REST API Specification (Image Enabled) – v1.0

---

# 1. Overview

This document defines the REST API contract for the Blueprint AI Backend.

Responsibilities:

* Accept blueprint uploads
* Manage job lifecycle
* Communicate with AI via RabbitMQ
* Store image URLs (original + annotated)
* Expose detection and estimation data to frontend

Base URL:

```
/api/v1
```

All timestamps: ISO 8601 (UTC)
All IDs: UUID v4
All responses: application/json

---

# 2. Global Response Format

## Success

```json
{
  "data": {},
  "message": "Optional message"
}
```

## Error

```json
{
  "error": "ERROR_CODE",
  "message": "Human readable explanation",
  "details": {}
}
```

---

# 3. Job Lifecycle

```
PENDING → QUEUED → PROCESSING → COMPLETED
                           ↘ FAILED
```

---

# 4. Create Job

## Endpoint

```
POST /jobs
```

## Request

Content-Type: multipart/form-data

Field:

* file (PDF | PNG | JPG)

Optional metadata:

```json
{
  "project_name": "Residential Layout A",
  "confidence_threshold": 0.25
}
```

## Response (201)

```json
{
  "data": {
    "job_id": "uuid",
    "status": "PENDING",
    "original_image_url": "https://storage/original/uuid.png",
    "created_at": "2026-02-22T10:25:41Z"
  }
}
```

Backend Actions:

* Store original image in object storage
* Insert DB record
* Publish job message to RabbitMQ
* Update status → QUEUED

---

# 5. Get Job Status

## Endpoint

```
GET /jobs/{job_id}
```

## Processing Response

```json
{
  "data": {
    "job_id": "uuid",
    "status": "PROCESSING",
    "original_image_url": "https://storage/original/uuid.png",
    "progress": 55
  }
}
```

## Completed Response

```json
{
  "data": {
    "job_id": "uuid",
    "status": "COMPLETED",
    "original_image_url": "https://storage/original/uuid.png",
    "annotated_image_url": "https://storage/annotated/uuid.png",
    "image_size": {
      "width": 2480,
      "height": 3508
    },
    "symbol_counts": {
      "valve": 12,
      "pump": 4
    },
    "total_detections": 16,
    "completed_at": "2026-02-22T10:26:09Z"
  }
}
```

---

# 6. Get Detection Details

## Endpoint

```
GET /jobs/{job_id}/detections
```

## Response

```json
{
  "data": {
    "job_id": "uuid",
    "original_image_url": "https://storage/original/uuid.png",
    "annotated_image_url": "https://storage/annotated/uuid.png",
    "image_size": {
      "width": 2480,
      "height": 3508
    },
    "detections": [
      {
        "label": "valve",
        "confidence": 0.91,
        "bbox": {
          "x1": 100,
          "y1": 200,
          "x2": 180,
          "y2": 280
        }
      }
    ]
  }
}
```

Purpose:

* original_image_url → base render
* annotated_image_url → preview render
* detections → dynamic frontend drawing

---

# 7. Generate Estimation

## Endpoint

```
GET /jobs/{job_id}/estimation
```

## Response

```json
{
  "data": {
    "job_id": "uuid",
    "total_symbols": 16,
    "material_breakdown": [
      {
        "symbol": "valve",
        "count": 12,
        "unit_cost": 1500,
        "total_cost": 18000
      }
    ],
    "grand_total_cost": 38000
  }
}
```

---

# 8. Health Check

## Endpoint

```
GET /health
```

## Response

```json
{
  "data": {
    "status": "healthy",
    "services": {
      "database": "connected",
      "rabbitmq": "connected"
    }
  }
}
```

---

End of Backend REST API Specification
