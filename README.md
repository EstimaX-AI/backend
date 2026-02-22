```
app/
├── api/                         # FastAPI route definitions
│   └── routes.py
│
├── db/                          # Database connection & models
│   ├── database.py
│   └── models.py
│
├── schemas/                     # Pydantic request/response schemas
│   ├── job.py
│   ├── detection.py
│   └── estimation.py
│
├── services/                    # Business logic & data access
│   ├── upload_job.py
│   ├── process_job.py
│   ├── get_job.py
│   ├── generate_estimation.py
│   └── healthcheck.py
│
├── tests/                       # Pytest test suite(later)
│   ├── conftest.py
│   └── test_routes.py
│
├── main.py                      # FastAPI application entrypoint
├── Dockerfile                   # Docker build instructions
├── Makefile                     # Task shortcuts (later)
├── requirements.txt             # Dependencies
└── .env.dev                     # Development environment variables
```
# Blueprint AI Estimation Backend

## API Contract Specification (v1.0)

---

# 1. Overview

This document defines the official request and response JSON contract for the Blueprint AI Estimation Backend. All clients (Web, Flutter, Admin tools) and the AI inference service must strictly adhere to this specification.

Base URL:

```
/api/v1
```

All timestamps are ISO 8601 (UTC).
All IDs are UUID v4.
All responses use JSON.

---

# 2. Global Response Standards

## 2.1 Success Response Structure

```json
{
  "data": {},
  "message": "Optional informational message"
}
```

## 2.2 Error Response Structure

```json
{
  "error": "ERROR_CODE",
  "message": "Human readable explanation",
  "details": {}
}
```

---

# 3. Create Blueprint Job

## Endpoint

```
POST /jobs
```

## Request

Content-Type: multipart/form-data

Field:

* file (PDF | PNG | JPG)

Optional JSON metadata:

```json
{
  "project_name": "Hospital Layout - Phase 1",
  "confidence_threshold": 0.25
}
```

## Success Response (201)

```json
{
  "data": {
    "job_id": "3f8a9f90-cc12-4b91-9f3d-3d4c9e1f0a12",
    "status": "PENDING",
    "file_name": "blueprint.pdf",
    "created_at": "2026-02-22T10:25:41Z"
  }
}
```

## Validation Error (400)

```json
{
  "error": "INVALID_FILE_TYPE",
  "message": "Only PDF, PNG, JPG files are allowed.",
  "details": {}
}
```

---

# 4. Trigger Job Processing

## Endpoint

```
POST /jobs/{job_id}/process
```

## Request

```json
{
  "confidence_threshold": 0.25,
  "model_version": "v1.2.0"
}
```

## Response

```json
{
  "data": {
    "job_id": "3f8a9f90-cc12-4b91-9f3d-3d4c9e1f0a12",
    "status": "PROCESSING",
    "started_at": "2026-02-22T10:26:01Z"
  },
  "message": "AI processing started"
}
```

---

# 5. AI Service Contract

## Backend → AI Service Request

```json
{
  "job_id": "3f8a9f90-cc12-4b91-9f3d-3d4c9e1f0a12",
  "file_url": "https://storage/blueprint.pdf",
  "confidence_threshold": 0.25
}
```

## AI → Backend Success Response

```json
{
  "model_version": "yolo_v8_symbol_2.1",
  "processing_time_ms": 4820,
  "image_width": 2480,
  "image_height": 3508,
  "detections": [
    {
      "label": "valve",
      "confidence": 0.91,
      "bbox": {
        "x1": 104,
        "y1": 233,
        "x2": 189,
        "y2": 305
      }
    }
  ]
}
```

## AI Failure Response

```json
{
  "error": "MODEL_INFERENCE_FAILED",
  "message": "Unable to process image",
  "details": {
    "reason": "CUDA out of memory"
  }
}
```

---

# 6. Get Job Status

## Endpoint

```
GET /jobs/{job_id}
```

## Processing Response

```json
{
  "data": {
    "job_id": "3f8a9f90-cc12-4b91-9f3d-3d4c9e1f0a12",
    "status": "PROCESSING",
    "progress": 65,
    "started_at": "2026-02-22T10:26:01Z"
  }
}
```

## Completed Response

```json
{
  "data": {
    "job_id": "3f8a9f90-cc12-4b91-9f3d-3d4c9e1f0a12",
    "status": "COMPLETED",
    "model_version": "yolo_v8_symbol_2.1",
    "processing_time_ms": 4820,
    "symbol_counts": {
      "valve": 12,
      "pump": 4,
      "junction": 6
    },
    "total_detections": 22,
    "created_at": "2026-02-22T10:25:41Z",
    "completed_at": "2026-02-22T10:26:09Z"
  }
}
```

## Failed Response

```json
{
  "error": "MODEL_TIMEOUT",
  "message": "AI service did not respond within timeout window",
  "details": {
    "job_id": "3f8a9f90-cc12-4b91-9f3d-3d4c9e1f0a12"
  }
}
```

---

# 7. Get Full Detection Details

## Endpoint

```
GET /jobs/{job_id}/detections
```

## Response

```json
{
  "data": {
    "job_id": "3f8a9f90-cc12-4b91-9f3d-3d4c9e1f0a12",
    "image_size": {
      "width": 2480,
      "height": 3508
    },
    "detections": [
      {
        "label": "valve",
        "confidence": 0.91,
        "bbox": {
          "x1": 104,
          "y1": 233,
          "x2": 189,
          "y2": 305
        }
      }
    ]
  }
}
```

---

# 8. Generate Estimation

## Endpoint

```
GET /jobs/{job_id}/estimation
```

## Response

```json
{
  "data": {
    "job_id": "3f8a9f90-cc12-4b91-9f3d-3d4c9e1f0a12",
    "estimation_summary": {
      "total_symbols": 22,
      "material_breakdown": [
        {
          "symbol": "valve",
          "count": 12,
          "unit_cost": 1500,
          "total_cost": 18000
        },
        {
          "symbol": "pump",
          "count": 4,
          "unit_cost": 5000,
          "total_cost": 20000
        }
      ],
      "grand_total_cost": 38000
    }
  }
}
```

---

# 9. Health Check

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
      "ai_service": "reachable"
    },
    "uptime_seconds": 15234
  }
}
```

---

# 10. Status Lifecycle

```
PENDING → PROCESSING → COMPLETED
                     ↘ FAILED
```

---

# 11. Validation Rules

* confidence_threshold: float (0.0 – 1.0)
* bbox coordinates: integer pixel values
* total_detections: non-negative integer
* unit_cost & total_cost: positive integers
* UUID: valid v4 format

---

End of Specification (v1.0)
