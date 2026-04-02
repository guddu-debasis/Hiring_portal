from fastapi import FastAPI
from app.core.database import engine, Base
from app.api.v1.endpoints import router
# Import the models to register them with SQLAlchemy Base
from app.models.candidate import JobPost, Candidate 

# This line creates the MySQL tables automatically if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hiring Automation System",
    description="AI-powered candidate screening and ranking system",
    version="1.0.0"
)

# Root route for a quick health check
@app.get("/")
def read_root():
    return {"message": "Welcome to the Hiring Automation API", "status": "Online"}

# Include Routers with the versioned prefix
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    # Using 'app.main:app' allows reload to work correctly from the root
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)