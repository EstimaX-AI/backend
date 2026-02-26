from fastapi import FastAPI
from api.jobs import router as job_router

app = FastAPI()

app.include_router(job_router)