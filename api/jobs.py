from fastapi import APIRouter, UploadFile, File, Form
from services.job_service import JobService
import os

router = APIRouter()


@router.post("/jobs")
async def create_job(
    file: UploadFile = File(...),
    project_name: str = Form(...)
):

    # Save file locally (temporary)
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    result = JobService.process_job(
        project_name=project_name,
        original_image_path=file_path
    )

    return result