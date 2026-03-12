from fastapi import FastAPI
from api.jobs import router as jobs_router

app = FastAPI()

app.include_router(jobs_router)