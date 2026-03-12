from db.database import SessionLocal
from db.models import ProcessingJob, JobStatus


class JobRepository:

    @staticmethod
    def create_job(job_id, user_id, pdf_url):
        db = SessionLocal()

        job = ProcessingJob(
            job_id=job_id,
            user_id=user_id,
            status=JobStatus.QUEUED
        )

        db.add(job)
        db.commit()
        db.refresh(job)
        db.expunge(job)
        db.close()

        return job

    @staticmethod
    def get_job_by_id(job_id):
        db = SessionLocal()

        job = db.query(ProcessingJob).filter(ProcessingJob.job_id == job_id).first()

        if job:
            db.expunge(job)

        db.close()

        return job
