from fastapi import APIRouter, UploadFile, File, Form
from app.services.storage_service import upload_pdf
from app.services.job_service import create_job_service
import uuid
from uuid import UUID

router = APIRouter()


@router.post("/jobs")
async def create_job(
    user_id: UUID | None = Form(None),
    file: UploadFile = File(...)
):

    file_bytes = await file.read()

    filename = f"{uuid.uuid4()}.pdf"

    signed_url = upload_pdf(file_bytes, filename)

    job = create_job_service(user_id, signed_url)

    return {
        "job_id": str(job.job_id),
        "user_id": str(user_id) if user_id is not None else None,
        "pdf_url": signed_url,
        "status": job.status.value
    }