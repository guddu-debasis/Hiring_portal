import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware  # <--- 1. Add this import
from app.core.database import engine, Base
from app.api.v1.endpoints import router

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Create tables in TiDB/MySQL
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hiring Automation System")

# --- 2. ADD CORS MIDDLEWARE HERE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows your Streamlit app to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    # Note: On Render, the port is handled by the $PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)