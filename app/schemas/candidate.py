from pydantic import BaseModel, EmailStr
from typing import List, Optional

class JobCreate(BaseModel):
    title: str
    description: str
    requirements: str

class JobResponse(JobCreate):
    id: int
    class Config:
        from_attributes = True

class CandidateResponse(BaseModel):
    id: int
    job_id: int
    full_name: str
    email: EmailStr
    score: float
    status: str = "Pending"
    job_title: Optional[str] = None  # <--- ADD THIS FIELD

    class Config:
        from_attributes = True