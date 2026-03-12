from app.db.database import SessionLocal
from app.db.models import ProcessingJob, JobStatus


def create_job(job_id, user_id=None):

    db = SessionLocal()

    job = ProcessingJob(
        job_id=job_id,
        user_id=user_id,
        status=JobStatus.QUEUED,
        result=None
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    db.close()

    return job