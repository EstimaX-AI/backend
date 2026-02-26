import uuid
import time

from db.database import SessionLocal
from db.models import JobStatus
from repositories.job_repository import JobRepository
from repositories.detection_repository import DetectionRepository
from repositories.estimation_repository import EstimationRepository
from services.estimation_service import EstimationService


class JobService:

    @staticmethod
    def process_job(project_name: str, original_image_path: str):

        db = SessionLocal()

        try:
            job_repo = JobRepository(db)
            detection_repo = DetectionRepository(db)
            estimation_repo = EstimationRepository(db)

            # 1️⃣ Create job
            job = job_repo.create_job(
                project_name=project_name,
                original_image_path=original_image_path
            )

            # 2️⃣ Mock AI response (temporary)
            mock_detections = [
                {
                    "label": "valve",
                    "confidence": 0.91,
                    "bbox": {"x1": 100, "y1": 200, "x2": 180, "y2": 280}
                },
                {
                    "label": "pump",
                    "confidence": 0.95,
                    "bbox": {"x1": 300, "y1": 400, "x2": 380, "y2": 480}
                }
            ]

            # 3️⃣ Store detections
            detection_repo.bulk_create(job.id, mock_detections)

            # 4️⃣ Fetch detections from DB
            detections = detection_repo.get_by_job_id(job.id)

            # 5️⃣ Calculate estimation
            estimation_result = EstimationService.calculate(detections)

            # 6️⃣ Store estimation
            estimation_repo.create_estimation(
                job_id=job.id,
                total_symbols=estimation_result["total_symbols"],
                grand_total_cost=estimation_result["grand_total_cost"],
                items=estimation_result["material_breakdown"]
            )

            # 7️⃣ Update job status
            job_repo.update_status(job, JobStatus.COMPLETED)

            return {
                "job_id": str(job.id),
                "status": "COMPLETED",
                "estimation": estimation_result
            }

        finally:
            db.close()