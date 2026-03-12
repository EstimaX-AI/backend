import uuid

from app.repositories.job_repository import create_job
from app.messaging.publisher import publish_to_queue


def create_job_service(user_id, pdf_url):

    job_id = uuid.uuid4()

    # Store job in DB
    job = create_job(
        job_id=job_id,
        user_id=user_id
    )

    
    message = {
        "job_id": str(job_id),
        "user_id": str(user_id) if user_id else None,
        "pdf_url": pdf_url
    }

    

    publish_to_queue("ai_jobs", message)

    return job