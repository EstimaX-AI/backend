import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.jobs import router as jobs_router
from messaging.consumer import start_consumer
from db.database import engine
from db.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    thread = threading.Thread(target=start_consumer, daemon=True)
    thread.start()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(jobs_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
