import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.database import engine, Base
from app.api.v1.endpoints import router


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")


if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hiring Automation System")


app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)