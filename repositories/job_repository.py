# repositories/job_repository.py

from db.database import SessionLocal
from db.models import Job, JobStatus


class JobRepository:

    @staticmethod
    def create_job(job_id, user_id, pdf_url):
        db = SessionLocal()

        job = Job(
            id=job_id,
            user_id=user_id,
            original_image_path=pdf_url,
            status=JobStatus.QUEUED
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        db.close()

        return job