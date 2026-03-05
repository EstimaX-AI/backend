# services/job_service.py

import uuid

from repositories.job_repository import JobRepository
from messaging.publisher import publish_to_queue


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
            "user_id": str(user_id),
            "pdf_url": pdf_url
        }

        publish_to_queue("ai_jobs", message)

        return job