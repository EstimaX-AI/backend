import uuid
from sqlalchemy.orm import Session
from db.models import Job, JobStatus
from repositories.base import BaseRepository


class JobRepository(BaseRepository):

    def create_job(self, project_name: str, original_image_path: str) -> Job:
        job = Job(
            id=uuid.uuid4(),
            project_name=project_name,
            original_image_path=original_image_path,
            status=JobStatus.PROCESSING,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_by_id(self, job_id: uuid.UUID) -> Job | None:
        return self.db.query(Job).filter(Job.id == job_id).first()

    def update_status(self, job: Job, status: JobStatus):
        job.status = status
        self.db.commit()
        self.db.refresh(job)
        return job

    def update_completion(self, job: Job):
        job.status = JobStatus.COMPLETED
        self.db.commit()
        self.db.refresh(job)
        return job