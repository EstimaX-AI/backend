from fastapi import APIRouter, UploadFile, File
from services.storage_service import StorageService
from services.job_service import JobService
import uuid

router = APIRouter()
@router.post("/jobs")
async def create_job(file: UploadFile = File(...)):

    file_bytes = await file.read()

    filename = f"{uuid.uuid4()}.pdf"

    signed_url = StorageService.upload_pdf(file_bytes, filename)

    job = JobService.create_job(None, signed_url)

    return {
        "job_id": str(job.id),
        "pdf_url": signed_url,
        "status": job.status
    }