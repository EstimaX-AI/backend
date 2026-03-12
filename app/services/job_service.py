import uuid
from fastapi import HTTPException

from repositories.job_repository import JobRepository
from messaging.publisher import publish_to_queue
from db.models import JobStatus


class JobService:

    @staticmethod
    def create_job(user_id, pdf_url):

        job_id = uuid.uuid4()

        job = JobRepository.create_job(
            job_id,
            user_id,
            pdf_url
        )

        message = {
            "job_id": str(job_id),
            "user_id": str(user_id) if user_id else None,
            "pdf_url": pdf_url
        }

        publish_to_queue("ai_jobs", message)

        return job

    @staticmethod
    def get_job_result(job_id):
        job = JobRepository.get_job_by_id(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job.status == JobStatus.FAILED:
            return {
                "data": {
                    "job_id": str(job.job_id),
                    "status": job.status,
                },
                "message": "Job processing failed"
            }

        if job.status != JobStatus.COMPLETED:
            return {
                "data": {
                    "job_id": str(job.job_id),
                    "status": job.status,
                },
                "message": "Job is still being processed"
            }

        return {
            "data": {
                "user_id": str(job.user_id) if job.user_id else None,
                "job_id": str(job.job_id),
                "status": job.status,
                "result": job.result or {},
                "created_at": job.created_at.isoformat() if job.created_at else None,
            },
            "message": "Job completed successfully"
        }
